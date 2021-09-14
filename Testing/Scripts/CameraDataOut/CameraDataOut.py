#Author-Dylan Butler
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

def main():
    app = adsk.core.Application.get()

    viewport = app.activeViewport
    camera = viewport.camera

    eye = camera.eye
    type = camera.cameraType
    perspectiveAngle = camera.perspectiveAngle
    target = camera.target
    upVector = camera.upVector
    viewExtents = camera.viewExtents

    filePath = 'D://OneDrive - University of Pittsburgh//Fall 2021//Ece 1896//Project//3D Mouse Project//Software//Fusion//Testing'
    fileName = '//TestOutput.txt'

    output = open(filePath + fileName, 'w')
    output.write("This is a test\n\n")

    output.write("eye - x: " + str(eye.x) + "\n")
    output.write("eye - y: " + str(eye.y) + "\n")
    output.write("eye - z: " + str(eye.z) + "\n\n")

    output.write("target - x: " + str(target.x) + "\n")
    output.write("target - y: " + str(target.y) + "\n")
    output.write("target - z: " + str(target.z) + "\n\n")

    output.write("upVector - x: " + str(upVector.x) + "\n")
    output.write("upVector - y: " + str(upVector.y) + "\n")
    output.write("upVector - z: " + str(upVector.z) + "\n\n")

    output.write("viewExtents: " + str(viewExtents) + "\n\n")

    output.write("perspective angle: " + str(perspectiveAngle) + "\n\n")

    output.close()

    
main() 