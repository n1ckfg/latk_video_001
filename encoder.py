import sys
import os
from pathlib import Path
import pymeshlab as ml
import numpy as np
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import colorsys

class PointData(object):
    def __init__(self, _pos, _col):
        self.pos = _pos
        self.col = _col

def clamp(n, min_n, max_n):
    return max(min(max_n, n), min_n)

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

def encoder(depth, debug=False):
    result = hueToRgb(depth)
    if (debug == True):
        test = rgbToHue(result)
        #print(str(depth) + ", " + str(test) + ", " + str(abs(depth - test)))
        if (abs(depth - test) > 0.01):
            return 0
    return colorFloatToColorInt(result)

def main(debug=False):
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] # get all args after "--"

    inputPath = argv[0] 
    outputPath = argv[1] 
   
    seqMin = 0.0
    seqMax = 0.0

    dim = 1024
    hdim = int(dim / 2)
    tileDim = int(dim / 8) # 16
    isMesh = False

    # 1. First pass, to resample and get dimensions for normalizing coordinates
    urls = []
    counter = 0

    if (debug == True):
        imgTest1 = Image.open("test/orig.png")
        imgTest1Pixels = imgTest1.load()
        for i in range(0, imgTest1.width * imgTest1.height):
            x, y = xyFromLoc(i, imgTest1.width)
            col = imgTest1Pixels[x, y]
            imgTest1Pixels[x, y] = encoder(float(col[0]) / 255.0)
        imgTest1.save("test/test1.png")
        
        imgTest2 = Image.open("test/test1.png")
        imgTest2Pixels = imgTest2.load()
        for i in range(0, imgTest2.width * imgTest2.height):
            x, y = xyFromLoc(i, imgTest2.width)
            d = rgbToHue(colorIntToColorFloat(imgTest2Pixels[x, y]))
            imgTest2Pixels[x, y] = colorFloatToColorInt((d, d, d))
        imgTest2.save("test/test2.png")
        print ("Wrote test images.")
    
    for fileName in os.listdir(inputPath):
        fileName = fileName.lower()
        if fileName.endswith("obj") or fileName.endswith("ply"): 
            url = os.path.abspath(os.path.join(inputPath, fileName))
            urls.append(url)
    urls.sort()

    for i in range(0, len(urls)):  
        print("\nLoading meshes " + str(i+1) + " / " + str(len(urls)))

        ms = ml.MeshSet()
        ms.load_new_mesh(urls[i])
        mesh = ms.current_mesh()

        newSampleNum = tileDim * tileDim #mesh.vertex_number()

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
        
        ms.generate_simplified_point_cloud(samplenum=newSampleNum) # exactnumflag=True
        
        ms.transfer_attributes_per_vertex(sourcemesh=0, targetmesh=1)
        
        ms.save_current_mesh(changeExtension(urls[i], ".ply", "_resampled"), save_vertex_color=True)
        
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

    for i in range(0, len(urls)):  
        print("\nLoading meshes " + str(i+1) + " / " + str(len(urls)))

        ms = ml.MeshSet()
        ms.load_new_mesh(urls[i])
        mesh = ms.current_mesh()
       
        vertexColors = ms.current_mesh().vertex_color_matrix()
        vertexPositions = ms.current_mesh().vertex_matrix()
        points = []
        for j in range(0, len(vertexPositions)):
            pos = vertexPositions[j]
            col = vertexColors[j]
            if (len(pos) == 3 and len(col) == 4):
                points.append(PointData(pos, col))

        imgRgb = Image.new("RGB", (tileDim, tileDim))
        imgRgbPixels = imgRgb.load()
        imgX = Image.new("RGB", (tileDim, tileDim))
        imgXPixels = imgX.load()
        imgY = Image.new("RGB", (tileDim, tileDim))
        imgYPixels = imgY.load()
        imgZ = Image.new("RGB", (tileDim, tileDim))
        imgZPixels = imgZ.load()

        for j, point in enumerate(points):
            color = (int(point.col[0] * 255.0), int(point.col[1] * 255.0), int(point.col[2] * 255.0))

            x = remap(point.pos[0], seqMin, seqMax, 0.0, 1.0)
            y = remap(point.pos[1], seqMin, seqMax, 0.0, 1.0)
            z = remap(point.pos[2], seqMin, seqMax, 0.0, 1.0)

            xResult = encoder(x)
            yResult = encoder(y)
            zResult = encoder(z)

            if (xResult != 0 and yResult != 0 and zResult != 0):
                jx, jy = xyFromLoc(j, tileDim)
                imgRgbPixels[jx, jy] = color
                imgXPixels[jx, jy] = xResult
                imgYPixels[jx, jy] = yResult
                imgZPixels[jx, jy] = zResult

        imgFinal = Image.new("RGB", (dim, dim))

        imgRgb = imgRgb.resize((hdim, hdim), 0)
        imgX = imgX.resize((hdim, hdim), 0)
        imgY = imgY.resize((hdim, hdim), 0)
        imgZ = imgZ.resize((hdim, hdim), 0)

        imgFinal.paste(imgRgb, (0, 0))
        imgFinal.paste(imgX, (hdim, 0))
        imgFinal.paste(imgY, (hdim, hdim))      
        imgFinal.paste(imgZ, (0, hdim))
        
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
    os.system("ffmpeg -y -i " + outputPath + "/output%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 17 -r 30 " + outputPath + "/output.mp4")

main()
