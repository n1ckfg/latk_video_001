import sys
import os
from pathlib import Path
import pymeshlab as ml
import numpy as np
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import colorsys
import kmeans

class PointData(object):
    def __init__(self, _pos, _col):
        self.pos = _pos
        self.col = _col

def xyFromLoc(loc, width):
    x = loc % width
    y = (loc - x) / width
    return x, y

def fract(x):
    return x - np.floor(x)

def mix(x, y, a):
    return x * (1.0 - a) + y * a 

def remap(value, min1, max1, min2, max2):
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

def rgbToHsv(rgb): # vec3
    minc = min(min(rgb[0], rgb[1]), rgb[2])
    maxc = max(max(rgb[0], rgb[1]), rgb[2])
    div = 1.0 / (6.0 * max(maxc - minc, 1.0e-5))
    r = (rgb[1] - rgb[2]) * div
    g = 1.0 / 3.0 + (rgb[2] - rgb[0]) * div
    b = 2.0 / 3.0 + (rgb[0] - rgb[1]) * div
    d = mix(r, mix(g, b, rgb[1] < rgb[2]), rgb[0] < max(rgb[1], rgb[2]))
    d2 = fract(d + 1.0)
    return (d2, d2, d2)

def colorFloatToColorInt(rgb):
    return (int(rgb[0] * 255.0), int(rgb[1] * 255.0), int(rgb[2] * 255.0))

def colorIntToColorFloat(rgb):
    return (float(rgb[0] / 255.0), float(rgb[1] / 255.0), float(rgb[2] / 255.0))


def encoder(depth):
    result = hueToRgb(depth)
    test = rgbToHsv(result)
    #print(str(depth) + ", " + str(test) + ", " + str(abs(depth - test)))
    #if (abs(depth - test) > 1.0):
        #return 0
    #else:
    return colorFloatToColorInt(result)

def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] # get all args after "--"

    inputPath = argv[0] 
    outputPath = argv[1] 
   
    seqMinX = 0
    seqMaxX = 0
    seqMinY = 0
    seqMaxY = 0
    seqMinZ = 0
    seqMaxZ = 0
    localDims = []
    localNorms = []

    dim = 1024
    hdim = int(dim / 2)

    # 1. First pass, to resample and get dimensions for normalizing coordinates
    urls = []
    counter = 0

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
    	col = imgTest2Pixels[x, y]
    	imgTest2Pixels[x, y] = colorFloatToColorInt(rgbToHsv(colorIntToColorFloat(col)))
    imgTest2.save("test/test2.png")

    for fileName in os.listdir(inputPath):
        fileName = fileName.lower()
        if fileName.endswith("obj") or fileName.endswith("ply"): 
            url = os.path.abspath(os.path.join(inputPath, fileName))
            urls.append(url)
    urls.sort()

    for i in range(0, len(urls)):  
        print("\nLoading meshes " + str(i+1) + " / " + str(len(urls)))

        minX = 0
        maxX = 0
        minY = 0
        maxY = 0
        minZ = 0
        maxZ = 0

        ms = ml.MeshSet()
        ms.load_new_mesh(urls[i])
        mesh = ms.current_mesh()

        newSampleNum = hdim * hdim #mesh.vertex_number()
        if (mesh.edge_number() == 0 and mesh.face_number() == 0):
            ms.poisson_disk_sampling(samplenum=newSampleNum, subsample=True) # exactnumflag=True 
        else:
            ms.poisson_disk_sampling(samplenum=newSampleNum, subsample=False) # exactnumflag=True
        ms.vertex_attribute_transfer(sourcemesh=0, targetmesh=1)
        ms.save_current_mesh(changeExtension(urls[i], ".ply", "_resampled"), save_vertex_color=True)
        
        vertexPositions = ms.current_mesh().vertex_matrix()

        for vert in vertexPositions:
            x = vert[0]
            y = vert[1]
            z = vert[2]
            if (x < minX):
                minX = x
            if (x > maxX):
                maxX = x
            if (y < minY):
                minY = y
            if (y > maxY):
                maxY = y
            if (z < minZ):
                minZ = z
            if (z > maxZ):
                maxZ = z

        localDim = (minX, maxX, minY, maxY, minZ, maxZ)
        localDims.append(localDim)

        if (minX < seqMinX):
            seqMinX = minX
        if (maxX > seqMaxX):
            seqMaxX = maxX
        if (minY < seqMinY):
            seqMinY = minY
        if (maxY > seqMaxY):
            seqMaxY = maxY
        if (minZ < seqMinZ):
            seqMinZ = minZ
        if (maxZ > seqMaxZ):
            seqMaxZ = maxZ

        print("Resampled frame " + str(counter+1))
        counter += 1
    
    for localDim in localDims:
        normMinX = remap(localDim[0], seqMinX, seqMaxX, 0, 1)
        normMaxX = remap(localDim[1], seqMinX, seqMaxX, 0, 1)
        normMinY = remap(localDim[2], seqMinY, seqMaxY, 0, 1)
        normMaxY = remap(localDim[3], seqMinY, seqMaxY, 0, 1)
        normMinZ = remap(localDim[4], seqMinZ, seqMaxZ, 0, 1)
        normMaxZ = remap(localDim[5], seqMinZ, seqMaxZ, 0, 1)

        localNorm = (normMinX, normMaxX, normMinY, normMaxY, normMinZ, normMaxZ)
        localNorms.append(localNorm)

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

        imgRgb = Image.new("RGB", (hdim, hdim))
        imgRgbPixels = imgRgb.load()
        imgX = Image.new("RGB", (hdim, hdim))
        imgXPixels = imgX.load()
        imgY = Image.new("RGB", (hdim, hdim))
        imgYPixels = imgY.load()
        imgZ = Image.new("RGB", (hdim, hdim))
        imgZPixels = imgZ.load()

        for j, point in enumerate(points):
            color = (int(point.col[0] * 255.0), int(point.col[1] * 255.0), int(point.col[2] * 255.0))

            x = remap(point.pos[0], localDims[i][0], localDims[i][1], localNorms[i][0], localNorms[i][1])
            y = remap(point.pos[1], localDims[i][2], localDims[i][3], localNorms[i][2], localNorms[i][3])
            z = remap(point.pos[2], localDims[i][4], localDims[i][5], localNorms[i][4], localNorms[i][5])

            xResult = encoder(x)
            yResult = encoder(y)
            zResult = encoder(z)

            if (xResult != 0 and yResult != 0 and zResult != 0):
                jx, jy = xyFromLoc(j, hdim)
                imgRgbPixels[jx, jy] = color
                imgXPixels[jx, jy] = xResult
                imgYPixels[jx, jy] = yResult
                imgZPixels[jx, jy] = zResult

        imgFinal = Image.new("RGB", (dim, dim))
        imgFinal.paste(imgRgb, (0, 0))

        imgFinal.paste(imgX, (hdim, 0))

        imgFinal.paste(imgY, (hdim, hdim))
        
        imgFinal.paste(imgZ, (0, hdim))
        
        imgFinal.save(outputPath + "/output" + str(i) + ".png")

        print("Finished frame " + str(counter+1))
        counter += 1


    # https://trac.ffmpeg.org/wiki/Encode/H.264
    # ffmpeg -y -i output%d.png -c:v libx264 -pix_fmt yuv420p -crf 5 -preset slow -r 30 output.mp4
    #os.system("ffmpeg -y -i " + outputPath + "/output%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 5 -r 30 output/output.mp4")

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

main()
