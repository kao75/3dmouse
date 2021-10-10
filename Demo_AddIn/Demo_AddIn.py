import adsk.core, adsk.fusion, adsk.cam, traceback, math
import sys, time, json
import threading

# set python.analysis.extraPaths to ../Libraries in .vscode settings
sys.path.append('C://Users//omara//PycharmProjects//3dmouse//Libraries')
import serial
import serial.tools.list_ports
from Reciever import Reciever

import pyautogui

reciever = Reciever(timing=0)

app = None
ui = adsk.core.UserInterface.cast(None)
handlers = []
stopFlag = None
myCustomEvent = 'MyCustomEventId'
customEvent = None


# The event handler that responds to the custom event being fired.
class ThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Make sure a command isn't running before changes are made.
            if ui.activeCommand != 'SelectCommand':
                ui.commandDefinitions.itemById('SelectCommand').execute()

            eventArgs = json.loads(args.additionalInfo)
            mode = int(eventArgs['mode'])
            x = int(eventArgs['x'])
            y = int(eventArgs['y'])
            z = int(eventArgs['z'])

            if mode == 0:
                # execute Orbit
                orbit(adsk.core.Application.get(), adsk.core.Application.get().activeViewport, adsk.core.Application.get().userInterface, x, y, z)
            elif mode == 1:
                # execute Pan
                pan(adsk.core.Application.get(), adsk.core.Application.get().activeViewport, adsk.core.Application.get().userInterface, x, y, z)
            elif mode == 2:
                # execute Zoom
                zoom(adsk.core.Application.get(), adsk.core.Application.get().activeViewport, adsk.core.Application.get().userInterface, x, y, z)
            else:
                # error, default to Orbit
                orbit(adsk.core.Application.get(), adsk.core.Application.get().activeViewport, adsk.core.Application.get().userInterface, x, y, z)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# The class for the new thread.
class MyThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        last_move = -1
        while True:
            mode, x, y, z = reciever.fetch_data()
            if mode == 0:
                mode_s = 'ORBIT'
            elif mode == 1:
                mode_s = 'PAN'
            elif mode == 2:
                mode_s = 'ZOOM'
            print(mode_s + ' | ' + ' x ' + str(x) + '\ty ' + str(y) + '\tz ' + str(z))
            if last_move > 8:  # if its been 8 iterations since last move, disable pan
                pyautogui.mouseUp(button='middle')
                last_move = -1
            if abs(x) < 10:
                x = 0
            if abs(y) < 10:
                y = 0
            if abs(z) < 10:
                z = 0

            if x != 0 or y != 0 or z != 0:
                mx_current, my_current = pyautogui.position()
                mx_new = mx_current + int(x / 2.5)
                my_new = my_current + int(y / 2.5)
                if last_move == -1:
                    pyautogui.mouseDown(button='middle')
                last_move = 0
                pyautogui.moveTo(x=mx_new, y=my_new)
            elif last_move != -1:
                last_move = last_move + 1

        # lastUpdated = 0
        # lastMode = 0
        # x_acc = 0
        # y_acc = 0
        # z_acc = 0
        # while True:
        #     mode, x, y, z = reciever.fetch_data()
        #     print(mode, x, y, z)
        #     if abs(x) > 9:
        #         x_acc = x_acc + x
        #     if abs(y) > 9:
        #         y_acc = y_acc + y
        #     if abs(z) > 9:
        #         z_acc = z_acc + z

        #     if abs(x_acc) > 30 or abs(y_acc) > 30 or abs(z_acc) > 30 or lastUpdated > 25 or lastMode != mode:
        #         args = {'mode': lastMode,'x': x_acc, 'y': y_acc, 'z': z_acc}
        #         app.fireCustomEvent(myCustomEvent, json.dumps(args))
        #         lastMode = mode
        #         x_acc = 0
        #         y_acc = 0
        #         z_acc = 0
        #         lastUpdated = 0

        #     lastUpdated = lastUpdated + 1


def run(context):
    global ui
    global app

    try:
        # create and initialize the application, viewport, and camera objects
        app = adsk.core.Application.get()
        viewport = app.activeViewport

        # initialize the camera smooth trnsition parameter to True
        viewport.camera.isSmoothTransition = True

        # create and initialize the message ui
        ui = app.userInterface
        ui.messageBox('3D Mouse Demo\nAdd-In Enabled')

        print(upVectorOrientation(viewport.camera, ui))

        # Register the custom event and connect the handler.
        global customEvent
        try:
            app.unregisterCustomEvent(myCustomEvent)
        except:
            pass
        customEvent = app.registerCustomEvent(myCustomEvent)
        onThreadEvent = ThreadEventHandler()
        customEvent.add(onThreadEvent)
        handlers.append(onThreadEvent)

        # Create a new thread for the other processing.
        global stopFlag
        stopFlag = threading.Event()
        myThread = MyThread(stopFlag)
        myThread.start()

    except:
        if ui:
            ui.messageBox('Run script Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        reciever.close()
        if handlers.count:
            customEvent.remove(handlers[0])
        stopFlag.set()
        app.unregisterCustomEvent(myCustomEvent)
        ui.messageBox('3D Mouse Demo\nAdd-In Stopped')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Execute Orbit
#   Inputs:
#       app, viewport, ui, Lx, Ly, Lz
#   Outputs:
#       N/A
#   Assume hardware sends operation mode input as Orbit.
#   Only changes the direction once, will add hardware input and output with
#   the addition of that software.
def orbit(app, viewport, ui, Lx, Ly, Lz):
    # ui.messageBox('ORBIT | x:' + str(Lx) + ', y:' + str(Ly) + ', z:' + str(Lz))
    try:
        print('ORBIT')
    except:
        if ui:
            ui.messageBox('Failed in orbit:\n{}'.format(traceback.format_exc()))


# Debug
def debug(ui, uVx0, uVy0, uVz0, uVx1, uVy1, uVz1):
    try:
        filePath = 'C:\\Users\\mcqkn\\Documents\\Fall_2021\\ECE1896\\Autodesk Output Files'
        fileName = '\\IO_Debug.txt'

        output = open(filePath + fileName, 'w')
        output.write("Debugging notes for IO in Algorithms.py\n\n")

        output.write('uVx0 = ' + str(uVx0) + '\n')
        output.write('uVy0 = ' + str(uVy0) + '\n')
        output.write('uVz0 = ' + str(uVz0) + '\n\n')

        output.write('uVx1 = ' + str(uVx1) + '\n')
        output.write('uVy1 = ' + str(uVy1) + '\n')
        output.write('uVz1 = ' + str(uVz1) + '\n')

    except:
        if ui:
            ui.messageBox('Failed in Debug:\n{}'.format(traceback.format_exc()))


# Execute upVectorOrientation
#   Inputs:
#       camera, ui
#   Outputs:
#       uVx0, uVy0, uVz0
#   Read the current orientation of the upVector from Fusion 360
def upVectorOrientation(camera, ui):
    try:
        return camera.upVector.x, camera.upVector.y, camera.upVector.z

    except:
        if ui:
            ui.messageBox('Failed in upVectorOrientation:\n{}'.format(traceback.format_exc()))


# Execute hardwareInput
#   Inputs:
#       ui
#   Outputs:
#       Lx, Ly, Lz, mode
#   Read in change in direction and mode inputs from hardware.
#   For testing purposes, just input three integers as the change in arc
#   length on the cue ball, and keep the mode of operation at 0 for orbit.
def hardwareInput(ui):
    try:
        Lx = 1  # arc length relative to the x direction
        Ly = 1  # arc length relative to the y direction
        Lz = 1  # arc length relative to the z direction
        mode = 0  # mode of operation

        # return the read in directional values
        return Lx, Ly, Lz, mode

    except:
        if ui:
            ui.messageBox('Failed in input:\n{}'.format(traceback.format_exc()))


# Execute Orbit's Mathematical Algorithm
#   Inputs:
#       ui, Lx0, Ly0, Lz0, uVx0, uVy0, uVz0
#   Outputs:
#       uVx1, uVy1, uVz1
# Run through the Orbit algorithm described in the Conceptual Design Document.
# Not optimized for memory
def orbitAlgorithm(ui, Lx, Ly, Lz, uVx0, uVy0, uVz0):
    try:
        filePath = 'C:\\Users\\mcqkn\\Documents\\Fall_2021\\ECE1896\\Autodesk Output Files'
        fileName = '\\Algorithm_Debug.txt'

        output = open(filePath + fileName, 'w')
        output.write("Debugging notes for orbitAlgorithm in Algorithms.py\n\n")

        pi = math.pi  # initialize pi locally
        Rc = 3  # radius of the cue ball in ***some units***
        piRc = pi * Rc

        # calculate thetas
        Tx = (180 * Lx) / piRc  # change in angle relative to x in the Lx arc length
        Ty = (180 * Ly) / piRc  # change in angle relative to y in the Ly arc length
        Tz = (180 * Lz) / piRc  # change in angle relative to z in the Lz arc length

        # print thetas
        output.write('Tx = ' + str(Tx) + '\n')
        output.write('Ty = ' + str(Ty) + '\n')
        output.write('Tz = ' + str(Tz) + '\n')

        # calculate trig functions in advance to save computation time
        cosTz = math.cos(math.radians(Tz))
        sinTz = math.sin(math.radians(Tz))
        cosTy = math.cos(math.radians(Ty))
        sinTy = math.sin(math.radians(Ty))
        cosTx = math.cos(math.radians(Tx))
        sinTx = math.sin(math.radians(Tx))

        # calculate vector rotations around each axis
        # z-axis
        XzP = uVx0 * cosTz - uVy0 * sinTz
        YzP = uVx0 * sinTz + uVy0 * cosTz
        ZzP = uVz0

        # y-axis
        XyP = uVx0 * cosTy + uVz0 * sinTy
        YyP = uVy0
        ZyP = uVz0 * cosTy - uVx0 * sinTy

        # x-axis
        XxP = uVx0
        YxP = uVy0 * cosTx - uVz0 * sinTx
        ZxP = uVy0 * sinTx + uVz0 * cosTx

        # combine the final upVector calculations from each vector rotation
        uVx1 = XzP + XyP + XzP
        uVy1 = YzP + YyP + YxP
        uVz1 = ZzP + ZyP + ZxP

        # return the final upVector indeces
        return uVx1, uVy1, uVz1

    except:
        if ui:
            ui.messageBox('Failed in algorithm:\n{}'.format(traceback.format_exc()))


# Execute Pan
#   Inputs:
#       ui
#   Outputs:
#       N/A
# Placeholder function for now
def pan(app, viewport, ui, x, y, z):
    try:
        print('PAN')

        cam = app.activeViewport.camera

        current_eye = cam.eye.asArray()
        current_target = cam.target.asArray()

        new_eye = adsk.core.Point3D.create(current_eye[0] + x / 200.0, current_eye[1] + y / 200.0,
                                           current_eye[2] + z / 200.0)
        new_target = adsk.core.Point3D.create(current_target[0] + x / 200.0, current_target[1] + y / 200.0,
                                              current_target[2] + z / 200.0)

        cam.eye = new_eye
        cam.target = new_target
        app.activeViewport.camera = cam

        adsk.doEvents()
        app.activeViewport.refresh()

    except:
        if ui:
            ui.messageBox('Failed in Pan:\n{}'.format(traceback.format_exec()))


# Execute Zoom
#   Inputs:
#       ui
#   Outputs:
#       N/A
# Plceholder function for now
def zoom(app, viewport, ui, x, y, z):
    try:
        print('ZOOM')
    except:
        if ui:
            ui.messageBox('Failed in Zoom:\n{}'.format(traceback.format_exec()))