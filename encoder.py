import sys
import os
from pathlib import Path
import pymeshlab as ml
import numpy as np

def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] # get all args after "--"

    inputPath = argv[0] 
    outputPath = argv[1] 

    counter = 0

    urls = []

    for fileName in os.listdir(inputPath):
        if fileName.endswith(inputExt): 
            url = os.path.abspath(os.path.join(inputPath, fileName))
            urls.append(url)
    urls.sort()

    for i in range(0, len(urls)):  
        print("\nLoading meshes " + str(i+1) + " / " + str(len(urls)))

        ms = ml.MeshSet()
        ms.load_new_mesh(urls[i])
        mesh = ms.current_mesh()

        newSampleNum = 256 * 256 #mesh.vertex_number()
        if (mesh.edge_number() == 0 and mesh.face_number() == 0):
            ms.poisson_disk_sampling(samplenum=newSampleNum, subsample=True)
        else:
            ms.poisson_disk_sampling(samplenum=newSampleNum, subsample=False)
        ms.vertex_attribute_transfer(sourcemesh=0, targetmesh=1)
        #ms.save_current_mesh("input.ply", save_vertex_color=True)
        
        vertexPositions = ms.current_mesh().vertex_matrix()
        vertexColors = ms.current_mesh().vertex_color_matrix()

        for vertexColor in vertexColors:
            color = (vertexColor[0], vertexColor[1], vertexColor[2], 1.0)
            color = (color[0] * color[0], color[1] * color[1], color[2] * color[2], 1.0)
            la.layers[0].frames[counter].strokes[strokeCounter].points[pointCounter].vertex_color = color
            pointCounter += 1
            if (pointCounter > len(la.layers[0].frames[counter].strokes[strokeCounter].points)-1):
                pointCounter = 0
                strokeCounter += 1 

        print("Finished frame " + str(counter+1))
        counter += 1
    
    os.system("ffmpeg -i " + outputPath + "/output%d.png -c:v libx264 -pix_fmt yuv420p -r 30 output.mp4")

main()
