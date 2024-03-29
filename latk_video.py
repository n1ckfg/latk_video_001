import sys
import os
from pathlib import Path
import pymeshlab as ml
import numpy as np
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import PIL.ImageFilter as ImageFilter
import colorsys
from sklearn.cluster import KMeans
import math
import latk
import time

class Cluster(object):
    def __init__(self):
        self.points = []
        self.colors = []
        self.indices = []
        self.centroid = (0.0,0.0,0.0)

def clamp(n, min_n, max_n):
    return max(min(max_n, n), min_n)

def zeroPadding(val, maxVal):
    return str(val).zfill(len(str(maxVal)))

def xyFromLoc(loc, width):
    x = loc % width
    y = (loc - x) / width
    return int(clamp(x, 0, width-1)), int(clamp(y, 0, width-1))

def fract(x):
    return x - np.floor(x)

def mix(x, y, a):
    return x * (1.0 - a) + y * a 

def remap(value, min1, max1, min2, max2, useNp=True):
    if (useNp == False):
        range1 = max1 - min1
        range2 = max2 - min2
        valueScaled = float(value - min1) / float(range1)
        return min2 + (valueScaled * range2)
    else:
        return np.interp(value, [min1, max1], [min2, max2])

def lerp(a, b, f): 
    return (a * (1.0 - f)) + (b * f)

def lerp3d(a, b, f):
    x = (a[0] * (1.0 - f)) + (b[0] * f)   
    y = (a[1] * (1.0 - f)) + (b[1] * f)   
    z = (a[2] * (1.0 - f)) + (b[2] * f)   
    return (x, y, z)

def drawLine(drawReps, p1, p2):
    returns = []

    for i in range(0, drawReps):
        val = float(i) / float(drawReps) 
        p3 = lerp3d(p1, p2, val)      
        returns.append(p3)

    return returns

def changeExtension(_url, _newExt, _append=None):
    returns = ""
    returnsPathArray = _url.split(".")
    for i in range(0, len(returnsPathArray)-1):
        returns += returnsPathArray[i]
    if (_append != None):
        returns += _append
    returns += _newExt

    print ("New url: " + returns)
    return returns

def hueToRgb(hue): # float
    h = hue * 6.0 - 2.0
    r = abs(h - 1.0) - 1.0
    g = 2.0 - abs(h)
    b = 2.0 - abs(h - 2.0)
    return (r, g, b)

def rgbToHue(rgb): # vec3
    minc = min(min(rgb[0], rgb[1]), rgb[2])
    maxc = max(max(rgb[0], rgb[1]), rgb[2])
    div = 1.0 / (6.0 * max(maxc - minc, 1.0e-5))
    r = (rgb[1] - rgb[2]) * div
    g = 1.0 / 3.0 + (rgb[2] - rgb[0]) * div
    b = 2.0 / 3.0 + (rgb[0] - rgb[1]) * div
    d = mix(r, mix(g, b, rgb[1] < rgb[2]), rgb[0] < max(rgb[1], rgb[2]))
    return fract(d + 1.0)

def colorFloatToColorInt(rgb):
    return (int(rgb[0] * 255.0), int(rgb[1] * 255.0), int(rgb[2] * 255.0))

def colorIntToColorFloat(rgb):
    return (float(rgb[0] / 255.0), float(rgb[1] / 255.0), float(rgb[2] / 255.0))

def encoder(depth):
    result = hueToRgb(depth)
    return colorFloatToColorInt(result)

def encodePoint(col, pos, seqMin=0.0, seqMax=1.0):
    color = (int(col[0] * 255.0), int(col[1] * 255.0), int(col[2] * 255.0))

    x = remap(pos[0], seqMin, seqMax, 0.0, 1.0)
    y = remap(pos[1], seqMin, seqMax, 0.0, 1.0)
    z = remap(pos[2], seqMin, seqMax, 0.0, 1.0)

    xResult = encoder(x)
    yResult = encoder(y)
    zResult = encoder(z)

    return color, (xResult, yResult, zResult)

def latk_video_main(outputPath, dim=1024, tilePixelSize=8, tileSubdiv=16, framerate=12):
    #argv = sys.argv
    #argv = argv[argv.index("--") + 1:] # get all args after "--"

    # * * * * * * * * * * * * *
    #inputPath = argv[0] 
    #outputPath = argv[1] 
    #dim = int(argv[2]) # 1024
    #tilePixelSize = int(argv[3]) # 16
    #tileSubdiv = int(argv[4]) # 16
    #framerate = argv[5] # 30
    # * * * * * * * * * * * * *
    obj = ss()
    obj_type = obj.type.lower()

    tileDim = int(dim / tilePixelSize) 
    newSampleNum = tileDim * tileDim #mesh.vertex_number()
    latkSampleNum = newSampleNum * 2
    seqMin = 0.0
    seqMax = 0.0
    isMesh = False
    useNewResampleMethod = False
    halfDim = int(dim / 2)
    kmeansDim = int(tileDim / tileSubdiv)
    numClusters = int(tileSubdiv * tileSubdiv)

    # 1. First pass, to resample and get dimensions for normalizing coordinates
    urls = []
    counter = 0
   
    for fileName in os.listdir(inputPath):
        fileName = fileName.lower()
        if fileName.endswith("obj") or fileName.endswith("ply") or fileName.endswith("latk"): 
            url = os.path.abspath(os.path.join(inputPath, fileName))
            urls.append(url)
    urls.sort()

    numLatks = 0
    currentLatk = 0

    for i, url in enumerate(urls):  
        if (obj_type == "gpencil"):
            print("\nGenerating meshes from latk " + str(currentLatk+1) + " / " + str(numLatks))
            currentLatk += 1
            # https://pymeshlab.readthedocs.io/en/0.1.9/tutorials/import_mesh_from_arrays.html
            # https://numpy.org/doc/stable/reference/generated/numpy.asarray.html

            la = latk.Latk(url)
            la.normalize()

            longestFrameCount = 0
            counter = 0
            
            for layer in la.layers:
                if len(layer.frames) > longestFrameCount:
                    longestFrameCount = len(layer.frames)
            print ("Longest layer frame count: " + str(longestFrameCount))

            for j in range(0, longestFrameCount):
                allPoints = []
                allColors = []
                    
                for layer in la.layers:
                    index = j
                    if (index > len(layer.frames) - 1):
                        index = j % len(layer.frames) - 1

                    frame = layer.frames[index]

                    for stroke in frame.strokes:
                        if (len(stroke.points) > 1):
                            point = (stroke.points[0].co[0], stroke.points[0].co[2], stroke.points[0].co[1])
                            allPoints.append(point)
                            
                            color = (stroke.color[0], stroke.color[1], stroke.color[2], 1.0)
                            allColors.append(color)
                            
                            for i in range(1, len(stroke.points)):
                                point = (stroke.points[i].co[0], stroke.points[i].co[2], stroke.points[i].co[1])
                                allPoints.append(point)
                                allColors.append(color)
                                
                                p1 = stroke.points[i].co
                                p2 = stroke.points[i-1].co
                                newPoints = drawLine(tileDim, p1, p2)
                                for newPoint in newPoints:
                                    allPoints.append((newPoint[0], newPoint[2], newPoint[1]))
                                    allColors.append(color)

                verts = np.asarray(allPoints)
                colors = np.asarray(allColors)
                
                ms = ml.MeshSet()
                newMesh = ml.Mesh(verts, v_color_matrix=colors)
                ms.add_mesh(newMesh, "latk" + str(currentLatk))
                mesh = ms.current_mesh()

                if (useNewResampleMethod == True):
                    ms.generate_simplified_point_cloud(samplenum=latkSampleNum) # exactnumflag=True
                    ms.transfer_attributes_per_vertex(sourcemesh=0, targetmesh=1)
                else:
                    if (newSampleNum >= mesh.vertex_number()):
                        if (isMesh == False):
                            ms.generate_surface_reconstruction_ball_pivoting()
                        ms.generate_sampling_poisson_disk(samplenum=latkSampleNum, subsample=False)
                        ms.transfer_attributes_per_vertex(sourcemesh=0, targetmesh=1)
                    else:
                        ms.generate_sampling_poisson_disk(samplenum=latkSampleNum, subsample=True)

                ms.save_current_mesh(changeExtension(url, ".ply", "_" + zeroPadding(counter, longestFrameCount) + "_resampled"), save_vertex_color=True)
                
                vertexPositions = ms.current_mesh().vertex_matrix()

                for vert in vertexPositions:
                    x = vert[0]
                    y = vert[1]
                    z = vert[2]
                    if (x < seqMin):
                        seqMin = x
                    if (x > seqMax):
                        seqMax = x
                    if (y < seqMin):
                        seqMin = y
                    if (y > seqMax):
                        seqMax = y
                    if (z < seqMin):
                        seqMin = z
                    if (z > seqMax):
                        seqMax = z

                print("Resampled Latk frame " + str(counter+1))
                counter += 1
        elif (obj_type == "mesh"):
            print("\nLoading meshes " + str(i+1) + " / " + str(len(urls)))
            ms = ml.MeshSet()
            ms.load_new_mesh(url)
            mesh = ms.current_mesh()

            if (mesh.edge_number() != 0 or mesh.face_number() != 0):
                numUvs = 0
                
                try:
                    numUvs = len(ms.current_mesh().vertex_tex_coord_matrix())
                    if (numUvs > 0):
                        print("Found " + str(numUvs) + " vertex texture coordinates.")
                except:
                    print("Found " + str(numUvs) + " vertex texture coordinates.")

                if (numUvs == 0):
                    try:
                        numUvs = len(ms.current_mesh().wedge_tex_coord_matrix())
                        if (numUvs > 0):
                            print("Found " + str(numUvs) + " wedge texture coordinates.")
                    except:
                        print("Found " + str(numUvs) + " wedge texture coordinates.")

                if (numUvs > 0):
                    ms.transfer_texture_to_color_per_vertex(sourcemesh=0, targetmesh=0)

            if (mesh.edge_number() == 0 and mesh.face_number() == 0):
                isMesh = False # It's a point cloud             
            else:
                isMesh = True # It's a mesh            
            
            if (useNewResampleMethod == True):
                ms.generate_simplified_point_cloud(samplenum=newSampleNum) # exactnumflag=True
                ms.transfer_attributes_per_vertex(sourcemesh=0, targetmesh=1)
            else:
                if (newSampleNum >= mesh.vertex_number()):
                    if (isMesh == False):
                        ms.generate_surface_reconstruction_ball_pivoting()
                    ms.generate_sampling_poisson_disk(samplenum=newSampleNum, subsample=False)
                    ms.transfer_attributes_per_vertex(sourcemesh=0, targetmesh=1)
                else:
                    ms.generate_sampling_poisson_disk(samplenum=newSampleNum, subsample=True)
            
            ms.save_current_mesh(changeExtension(url, ".ply", "_resampled"), save_vertex_color=True)
            
            vertexPositions = ms.current_mesh().vertex_matrix()

            for vert in vertexPositions:
                x = vert[0]
                y = vert[1]
                z = vert[2]
                if (x < seqMin):
                    seqMin = x
                if (x > seqMax):
                    seqMax = x
                if (y < seqMin):
                    seqMin = y
                if (y > seqMax):
                    seqMax = y
                if (z < seqMin):
                    seqMin = z
                if (z > seqMax):
                    seqMax = z

            print("Resampled frame " + str(counter+1))
            counter += 1
    
    # 2. Second pass, to convert the resampled point clouds to images
    urls = []
    counter = 0

    for fileName in os.listdir(inputPath):
        fileName = fileName.lower()
        if fileName.endswith("_resampled.ply"): 
            url = os.path.abspath(os.path.join(inputPath, fileName))
            urls.append(url)
    urls.sort()

    for i, url in enumerate(urls):  
        print("\nLoading meshes " + str(i+1) + " / " + str(len(urls)))

        ms = ml.MeshSet()
        ms.load_new_mesh(url)
        mesh = ms.current_mesh()
       
        vertexColors = ms.current_mesh().vertex_color_matrix()
        vertexPositions = ms.current_mesh().vertex_matrix()
        clusters = []

        imgRgb = Image.new("RGB", (tileDim, tileDim))
        imgRgbPixels = imgRgb.load()
        imgX = Image.new("RGB", (tileDim, tileDim))
        imgXPixels = imgX.load()
        imgY = Image.new("RGB", (tileDim, tileDim))
        imgYPixels = imgY.load()
        imgZ = Image.new("RGB", (tileDim, tileDim))
        imgZPixels = imgZ.load()

        if (numClusters < 2): # no kmeans sort    
            for j in range(0, len(vertexPositions)):
                col, pos = encodePoint(vertexColors[j], vertexPositions[j], seqMin, seqMax)
                jx, jy = xyFromLoc(j, tileDim)
                imgRgbPixels[jx, jy] = col
                imgXPixels[jx, jy] = pos[0]
                imgYPixels[jx, jy] = pos[1]
                imgZPixels[jx, jy] = pos[2]
        else:
            # https://scikit-learn.org/stable/modules/clustering.html
            # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
            kmeans = KMeans(n_clusters=numClusters, n_init=10, algorithm="lloyd") # "lloyd", "elkan"
            kmeans.fit(vertexPositions)
            #kmeans.fit(vertexColors) # sort by color
           
            for j in range(0, numClusters):
                clusters.append(Cluster())

            for j, label in enumerate(kmeans.labels_):
                clusters[label].points.append(vertexPositions[j])
                clusters[label].colors.append(vertexColors[j])
                clusters[label].indices.append(j)

            for j, centroid in enumerate(kmeans.cluster_centers_):
                clusters[j].centroid = centroid

            # https://stackoverflow.com/questions/17555218/python-how-to-sort-a-list-of-lists-by-the-fourth-element-in-each-list
            clusters.sort(key=lambda x: x.centroid.all())

            # https://discourse.processing.org/t/linear-array-of-values-to-grid/14206/3
            stride = math.sqrt(len(clusters))
            for j, cluster in enumerate(clusters):
                jx = math.floor(j % stride)
                jy = math.floor(j / stride)
                
                for k in range(0, len(cluster.points)):
                    col, pos = encodePoint(cluster.colors[k], cluster.points[k], seqMin, seqMax)
                    kx, ky = xyFromLoc(k, kmeansDim)
                    kx += (jx * kmeansDim)
                    ky += (jy * kmeansDim)
                    imgRgbPixels[kx, ky] = col
                    imgXPixels[kx, ky] = pos[0]
                    imgYPixels[kx, ky] = pos[1]
                    imgZPixels[kx, ky] = pos[2]

        imgFinal = Image.new("RGB", (dim, dim))

        imgRgb = imgRgb.resize((halfDim, halfDim), 0)
        imgX = imgX.resize((halfDim, halfDim), 0)
        imgY = imgY.resize((halfDim, halfDim), 0)
        imgZ = imgZ.resize((halfDim, halfDim), 0)

        # https://www.tutorialspoint.com/python_pillow/python_pillow_blur_an_image.htm
        '''
        blurVal = 1
        imgRgb = imgRgb.filter(ImageFilter.BoxBlur(blurVal))
        imgX = imgX.filter(ImageFilter.BoxBlur(blurVal))
        imgY = imgY.filter(ImageFilter.BoxBlur(blurVal))
        imgZ = imgZ.filter(ImageFilter.BoxBlur(blurVal))
        '''

        imgFinal.paste(imgRgb, (0, 0))
        imgFinal.paste(imgX, (halfDim, 0))
        imgFinal.paste(imgY, (halfDim, halfDim))      
        imgFinal.paste(imgZ, (0, halfDim))
        
        imgFinal.save(outputPath + "/output" + str(i) + ".png")

        print("Finished frame " + str(counter+1))
        counter += 1


    # https://trac.ffmpeg.org/wiki/Encode/H.264

    '''
    # If you want more control over mp4 encoding
    VIDEO_BITRATE="5M"
    VIDEO_BITRATE_MAX="5M"
    VIDEO_BITRATE_MIN="5M"
    AUDIO_BITRATE="320k"

    ENCODE_SPEED="slow"
    PROFILE="high"
    LEVEL="5.2"

    cmd = "ffmpeg -y -i " + outputPath + "/output%d.png -vcodec libx264 -pix_fmt yuv420p -preset:v " + ENCODE_SPEED + " -b:v " + VIDEO_BITRATE + " -maxrate " + VIDEO_BITRATE_MAX + " -minrate " + VIDEO_BITRATE_MIN + " -profile:v " + PROFILE + " -level " + LEVEL + " -acodec aac -strict -2 -b:a " + AUDIO_BITRATE + " -r 30 " + outputPath + "/output.mp4"
    print(cmd)

    os.system(cmd)
    '''

    # ffmpeg -y -i output%d.png -c:v libx264 -pix_fmt yuv420p -crf 17 -preset slow -r 30 output.mp4

    #filterString = "-filter:v scale=in_color_matrix=auto:in_range=auto:out_color_matrix=bt709:out_range=tv"
    #os.system("ffmpeg -y -i " + outputPath + "/output%d.png " + filterString + " -c:v libx264 -pix_fmt yuv420p -preset slow -crf 17 -r " + str(framerate) + " " + outputPath + "/output_" + str(int(time.time())) + ".mp4")
    os.system("ffmpeg -y -i " + outputPath + "/output%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 17 -r " + str(framerate) + " " + outputPath + "/output_" + str(int(time.time())) + ".mp4")

