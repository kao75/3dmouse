#Author-Dylan Butler
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, time, struct
import sys
sys.path.append('D:\\OneDrive - University of Pittsburgh\\Fall 2021\\Ece 1896\\Project\\3D Mouse Project\\Software\\Fusion\\Testing\\Libraries')
import serial

arduino = serial.Serial(port='COM4', baudrate=115200, timeout=2)
time.sleep(2)

def main():

    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        viewport = app.activeViewport
        camera = viewport.camera

        eye = camera.eye
        type = camera.cameraType
        perspectiveAngle = camera.perspectiveAngle
        target = camera.target
        upVector = camera.upVector
        viewExtents = camera.viewExtents

        arduinoData = write_read(eye.z)
        ui.messageBox(str(arduinoData))

        camera.isSmoothTransition = True
        camera.eye = adsk.core.Point3D.create(eye.x, eye.y, eye.z + arduinoData)
        #camera.eye = adsk.core.Point3D.create(eye.x, eye.y, eye.z)
        camera.target = target
        camera.upVector = upVector

        #Need this to update view
        viewport.camera = camera
        viewport.refresh() #Forces refresh, not always neccessary

        #ui.messageBox('Should be updated')


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def write_read(x):
    filePath = 'D://OneDrive - University of Pittsburgh//Fall 2021//Ece 1896//Project//3D Mouse Project//Software//Fusion//Testing'
    fileName = '//DataToBeSent.txt'
    output = open(filePath + fileName, 'w')

    output.write("eye.z read: " + str(x) + '\n')

    data = arduino.read_until(bytes('\n', 'utf-8'), 4)
    strData = str(struct.unpack('>f', data))
    disallowed_chars = "(,)"
    for char in disallowed_chars:
        strData = strData.replace(char, "")
    floatData = float(strData)

    output.write("eye.z updated: ")
    output.write(strData)
    output.write('\n')

    output.close()
    arduino.close()
    return floatData

main() 