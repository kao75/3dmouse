import adsk.core, adsk.fusion, adsk.cam, traceback, math
import sys, time, json
import threading

# set python.analysis.extraPaths to ../Libraries in .vscode settings
sys.path.append('C://Users//omara//PycharmProjects//3dmouse//Libraries')
import serial
import serial.tools.list_ports
from Reciever import Reciever
from CustomizationGUI import CustomizationGUI

reciever = Reciever(timing=0)

app = None
ui = adsk.core.UserInterface.cast(None)
handlers = []
stopFlag = None
updateCameraEventID = 'UpdateCameraEventID'
updateCameraEvent = None
tbPanel = None
settingsOpen = False


class SensitivityObject():

    def __init__(self):
        self.orbitSensitivity = 70
        self.panSensitivity = .0075 # inches per degree
        self.zoomSensitivity = 70
    
    def update(self, neworbit, newpan, newzoom):
        self.orbitSensitivity = neworbit
        self.panSensitivity = newpan
        self.zoomSensitivity = newzoom
        print('\n\nINSIDE OF UPDATE\n\n')
    
    def getOrbitSensitivity(self):
        return self.orbitSensitivity

    def getOrbitMultiplier(self):
        return self.getOrbitSensitivity
    
    def getPanSensitivity(self):
        return self.panSensitivity
    
    def getPanMultiplier(self):
        return 25 * .0247 * self.panSensitivity
        # return .0247 * self.panSensitivity
    
    def getZoomSensitivity(self):
        return self.zoomSensitivity

    def getZoomMultiplier(self):
        return self.zoomSensitivity


sensitivity_object = SensitivityObject()


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

            if mode == 10:
                # execute Orbit
                orbit(adsk.core.Application.get(), adsk.core.Application.get().activeViewport, adsk.core.Application.get().userInterface, x, y, z)
            elif mode == 0 or mode == 1:
                # execute Pan
                pan(adsk.core.Application.get(), x, y, z)
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
class WorkerThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while True:
            mode, x, y, z = reciever.fetch_data()
            if abs(x) < 25:
                x = 0
            if abs(y) < 25:
                y = 0
            if abs(z) < 25:
                z = 0

            print(mode, x, y, z)
            if  x != 0 or y != 0 or z != 0:
                args = {'mode': mode,'x': x, 'y': y, 'z': z}
                app.fireCustomEvent(updateCameraEventID, json.dumps(args))
            time.sleep(.01)

# The class for the gui settings thread.
class SettingsThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        global sensitivity_object, settingsOpen
        while True:
            if settingsOpen:
                gui = CustomizationGUI(sensitivity_object)
                settingsOpen = False
            else:
                time.sleep(.75)


def run(context):
    global ui
    global app

    try:
        # create and initialize the application, viewport, and camera objects
        app = adsk.core.Application.get()

        # create and initialize the message ui
        ui = app.userInterface
        ui.messageBox('3D Mouse Demo\nAdd-In Enabled')

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('3DMouseButtonID', 
                                                   '3D Mouse Settings', 
                                                   'Settings for 3D Mouse')
        # Connect to the command created event.
        mouseSettingsCommandCreated = MouseSettingsCommandCreatedEventHandler()
        buttonSample.commandCreated.add(mouseSettingsCommandCreated)
        handlers.append(mouseSettingsCommandCreated)
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSample)


        # Register the custom event and connect the handler.
        global updateCameraEvent
        try:
            app.unregisterCustomEvent(updateCameraEventID)
        except:
            pass
        updateCameraEvent = app.registerCustomEvent(updateCameraEventID)
        onThreadEvent = ThreadEventHandler()
        updateCameraEvent.add(onThreadEvent)
        handlers.append(onThreadEvent)

        # Create a new thread for the other processing.
        global stopFlag
        stopFlag = threading.Event()
        workerThread = WorkerThread(stopFlag)
        workerThread.start()

        # Create thread for Settings GUI
        settingsThread = SettingsThread(stopFlag)
        settingsThread.start()

    except:
        if ui:
            ui.messageBox('Run script Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        reciever.close()

        if handlers.count:
            updateCameraEvent.remove(handlers[1])
        stopFlag.set()
        app.unregisterCustomEvent(updateCameraEventID)

        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        mouseButton = addinsPanel.controls.itemById('3DMouseButtonID')       
        if mouseButton:
            mouseButton.deleteMe()
        cmdDef = ui.commandDefinitions.itemById('3DMouseButtonID')
        if cmdDef:
            cmdDef.deleteMe()
        
        ui.messageBox('3D Mouse Demo\nAdd-In Stopped')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the commandCreated event.
class MouseSettingsCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command

        # Connect to the execute event.
        onExecute = MouseSettingsCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


# Event handler for the execute event.
class MouseSettingsCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        global settingsOpen
        settingsOpen = True



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
#       app
#   Outputs:
#       N/A
# Placeholder function for now
def pan(app, x, y, z):
    try:
        print('PAN')

        cam = app.activeViewport.camera

        current_eye = cam.eye
        current_target = cam.target

        upVector = cam.upVector
        eye_target_vector = current_target.vectorTo(current_eye)
        sideVector = eye_target_vector.crossProduct(upVector)
        sideVector.normalize()

        # print('up:', upVector.x, upVector.y, upVector.z)
        # print('side:', sideVector.x, sideVector.y, sideVector.z)

        global sensitivity_object
        pan_multiplier = sensitivity_object.getPanMultiplier()
        xChange = ((abs(upVector.x / 1.0) * y) + ((sideVector.x / 1.0) * x)) * pan_multiplier
        yChange = ((abs(upVector.y / 1.0) * y) + ((sideVector.y / 1.0) * x)) * pan_multiplier
        zChange = ((abs(upVector.z / 1.0) * y) + ((sideVector.z / 1.0) * x)) * pan_multiplier

        # .0081 inches/degree = change/5000 = change*.0002
        # .0247 * sens

        new_eye = adsk.core.Point3D.create(current_eye.x + xChange, current_eye.y + yChange, current_eye.z + zChange)
        new_target = adsk.core.Point3D.create(current_target.x + xChange, current_target.y + yChange, current_target.z + zChange)

        current_eye = new_eye
        current_target = new_target

        cam.eye = new_eye
        cam.target = new_target

        cam.isSmoothTransition = False

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