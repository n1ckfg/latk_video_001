import sys
import os
from pathlib import Path
import pymeshlab as ml
import numpy as np
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image

def xyFromLoc(loc, width):
    x = loc % width
    y = (loc - x) / width
    return x, y

def remap(value, min1, max1, min2, max2):
    return np.interp(value,[min1, max1],[min2, max2])

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

def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] # get all args after "--"

    inputPath = argv[0] 
    outputPath = argv[1] 
   
    maxIntVal = 255 * 255 * 255

    seqMinX = 0
    seqMaxX = 0
    seqMinY = 0
    seqMaxY = 0
    seqMinZ = 0
    seqMaxZ = 0
    localDims = []
    localNorms = []

    # 1. First pass, to resample and get dimensions for normalizing coordinates
    urls = []
    counter = 0

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

        newSampleNum = 256 * 256 #mesh.vertex_number()
        if (mesh.edge_number() == 0 and mesh.face_number() == 0):
            ms.poisson_disk_sampling(samplenum=newSampleNum, subsample=True)
        else:
            ms.poisson_disk_sampling(samplenum=newSampleNum, subsample=False)
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

        print("Resampled frame " + str(counter+1))
        counter += 1
    
    for localDim in localDims:
        normMinX = remap(localDim[0], seqMinX, seqMaxX, 0, 1)
        normMaxX = remap(localDim[1], seqMinX, seqMaxX, 0, 1)
        normMinY = remap(localDim[2], seqMinY, seqMaxY, 0, 1)
        normMaxY = remap(localDim[3], seqMinY, seqMaxY, 0, 1)
        normMinZ = remap(localDim[4], seqMinZ, seqMaxZ, 0, 1)
        normMaxZ = remap(localDim[5], seqMinZ, seqMaxZ, 0, 1)

        normVals = (normMinX, normMaxX, normMinY, normMaxY, normMinZ, normMaxZ)
        localNorms.append(normVals)

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

        imgRgb = Image.new("RGB", (512, 512))
        imgRgbPixels = imgRgb.load()

        for i, vertexColor in enumerate(vertexColors):
            color = (int(vertexColor[0] * 255), int(vertexColor[1] * 255), int(vertexColor[2] * 255))

            ix, iy = xyFromLoc(i, 512)
            imgRgbPixels[ix, iy] = color

        vertexPositions = ms.current_mesh().vertex_matrix()

        imgX = Image.new("RGB", (512, 512))
        imgXPixels = imgX.load()
        imgY = Image.new("RGB", (512, 512))
        imgYPixels = imgY.load()
        imgZ = Image.new("RGB", (512, 512))
        imgZPixels = imgZ.load()

        for vert in vertexPositions:
            x = remap(vert[0], localDims[0], localDims[1], normVals[0], normVals[1])
            y = remap(vert[1], localDims[2], localDims[3], normVals[2], normVals[3])
            z = remap(vert[2], localDims[4], localDims[5], normVals[4], normVals[5])

            ix, iy = xyFromLoc(i, 512)
            imgXPixels[ix, iy] = int(maxIntVal * x)
            imgYPixels[ix, iy] = int(maxIntVal * y)
            imgZPixels[ix, iy] = int(maxIntVal * z)

        imgFinal = Image.new("RGB", (1024, 1024))
        imgFinal.paste(imgRgb, (0, 0))
        imgFinal.paste(imgX, (512, 0))
        imgFinal.paste(imgY, (512, 512))
        imgFinal.paste(imgZ, (0, 512))
        imgFinal.convert("RGB").save(outputPath + "/output" + str(i) + ".png")

        print("Finished frame " + str(counter+1))
        counter += 1

    #os.system("ffmpeg -i " + outputPath + "/output%d.png -c:v libx264 -pix_fmt yuv420p -r 30 output.mp4")

main()
