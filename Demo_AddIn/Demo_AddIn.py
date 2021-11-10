#------------------------------------
# Demo_AddIn.py
# Authors: Kareem Omar and Jared Carl
# ECE1896 Senior Design
#------------------------------------

# import libraries
import adsk.core, adsk.fusion, adsk.cam, traceback, math
import sys, time, json
import threading

# set python.analysis.extraPaths to ../Libraries in .vscode settings
sys.path.append('..//Libraries')
import serial
import serial.tools.list_ports
from Reciever import Reciever
from CustomizationGUI import CustomizationGUI

# reciever initialization
reciever = Reciever(timing=0)

# global variable initialization
app = None
ui = adsk.core.UserInterface.cast(None)
handlers = []
stopFlag = None
updateCameraEventID = 'UpdateCameraEventID'
updateCameraEvent = None
tbPanel = None
sensitivity_object = None
settingsOpen = False

# The class for handling sensitivity of the hardware input
class SensitivityObject:

    def __init__(self):
        self.orbitSensitivity = 1       # degrees per trackball degree
        self.panSensitivity = .0075     # inches per trackball degree
        self.zoomSensitivity = .00125   # inches per trackball degree
    
    def update(self, neworbit, newpan, newzoom):
        self.orbitSensitivity = neworbit
        self.panSensitivity = newpan
        self.zoomSensitivity = newzoom
    
    def getOrbitSensitivity(self):
        return self.orbitSensitivity

    def getOrbitMultiplier(self):
        #return 750 * self.orbitSensitivity
        return 75 * self.orbitSensitivity
    
    def getPanSensitivity(self):
        return self.panSensitivity
    
    def getPanMultiplier(self):
        # return 25 * .0247 * self.panSensitivity # for breadboard setup
        return .0247 * self.panSensitivity
    
    def getZoomSensitivity(self):
        return self.zoomSensitivity

    def getZoomMultiplier(self):
        return self.zoomSensitivity
        # return 20 * self.zoomSensitivity # for breadboard setup


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
                pan(adsk.core.Application.get(), x, y)
            elif mode == 2:
                # execute Zoom
                zoom(adsk.core.Application.get(), x, y)
            else:
                # error, default to Orbit
                orbit(adsk.core.Application.get(), adsk.core.Application.get().activeViewport, adsk.core.Application.get().userInterface, x, y, z)

        except:
            if ui:
                ui.messageBox('Failed in notify:\n{}'.format(traceback.format_exc()))


# The class for the new thread.
class WorkerThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        reciever.fetch_data()   # throw out first fetch
        while True:
            mode, x, y, z = reciever.fetch_data()
            if abs(x) <= 25:
                x = 0
            if abs(y) <= 25:
                y = 0
            if abs(z) <= 25:
                z = 0

            if  x != 0 or y != 0 or z != 0:
                print('reciever:', mode, x, y, z)
                args = {'mode': mode,'x': x, 'y': y, 'z': z}
                app.fireCustomEvent(updateCameraEventID, json.dumps(args))

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
                time.sleep(1)

# Execute run
#   Inputs:
#       context
#   Outputs:
#       N/A
def run(context):
    global ui
    global app

    try:
        # create and initialize the application, viewport, and camera objects
        app = adsk.core.Application.get()

        # create and initialize the message ui
        ui = app.userInterface
        ui.messageBox('3D Mouse Demo\nAdd-In Enabled')

        # initialize sensitivity object
        global sensitivity_object
        sensitivity_object = SensitivityObject()

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('3DMouseButtonID', 
                                                   '3D Mouse Settings', 
                                                   'Sensitivity Customization for 3D Mouse')
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
            ui.messageBox('Failed in Run:\n{}'.format(traceback.format_exc()))

# Execute stop
#   Inputs:
#       context
#   Outputs:
#       N/A
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


# Execute orbit
#   Inputs:
#       app, viewport, ui, x, y, z
#   Outputs:
#       N/A
# The shell of the orbit algorithm
def orbit(app, viewport, ui, x, y, z):
    try:
        # set up debugging of screen coordinates
        #filePath = 'C:\\Users\\mcqkn\\Documents\\Fall_2021\\ECE1896\\Autodesk Output Files'
        #fileName = '\\Orbit_debug.txt'
        #output = open(filePath + fileName, 'w')
        #output.write("This is the Orbit debugging file:\n\n")

        # initialize the camera, target, and eye variables
        camera = viewport.camera
        target = camera.target
        eye = camera.eye

        # initialize and create screen vectors
        uV, eV, sV = screenVectors(ui, camera)

        # find the distance between the Target and the Eye
        r = distanceET(viewport, ui)

        # set the relative factor for the thetas
        global sensitivity_object
        orbit_multiplier = sensitivity_object.getOrbitMultiplier()

        # read in the hardware input (debugging use only)
        #Lx, Ly, Lz = hardwareInput_debug(ui)

        # translate the hardware input to a relative change to an angle
        Tx = x / 8192 * orbit_multiplier
        Ty = y / 8192 * orbit_multiplier
        Tz = z / 8192 * orbit_multiplier

        # run initial debug
        #output = initial_debug(ui, output, uV, sV, eV, eye, Tx, Ty, Tz, target, r)

        # if the hardware reads a change in z
        # do not modify eyeVector
        if(Tz != 0):
            # create the new upVector with the old sideVector
            uV = newVector(ui, uV, sV, Tz)
            uV.normalize()

            # re-assign the sideVector in accordance with the new upVector
            sV = uV.crossProduct(eV)
            sV.normalize()

            # debug notes
            #output = function_debug(ui, output, uV, sV, eV, eye, 'New upVector:')

        # if the hardware reads a change in x
        # do not modify upVector
        if(Tx != 0):
            # create the new sideVector with the old eyeVector
            sV = newVector(ui, sV, eV, Tx)
            sV.normalize()

            # re-assign the eyeVector in accordance with the new sideVector
            eV = sV.crossProduct(uV)
            eV.normalize()

            # re-assign the eye in accordance with the new eyeVector
            # find the end of the eyeVector, multiply that point by the radius, and move it in line with the target point
            eye = eV.asPoint()
            eye = adsk.core.Point3D.create(eye.x * r + target.x, eye.y * r + target.y, eye.z * r + target.z)

            # debug notes
            #output = function_debug(ui, output, uV, sV, eV, eye, 'New sideVector:')

        # if the hardware reads a change in y
        # do not modify sideVector
        if(Ty != 0):
            # create the new eyeVector with the old upVector
            eV = newVector(ui, eV, uV, Ty)
            eV.normalize()

            # re-assign the upVector in accordance with the new eyeVector
            uV = eV.crossProduct(sV)
            uV.normalize()

            # re-assign the eye in accordance with the new eyeVector
            # find the end of the eyeVector, multiply that point by the radius, and move it in line with the target point
            eye = eV.asPoint()
            eye = adsk.core.Point3D.create(eye.x * r + target.x, eye.y * r + target.y, eye.z * r + target.z)

            # debug notes
            #output = function_debug(ui, output, uV, sV, eV, eye, 'New eyeVector:')

        # re-assign changed Fusion360 variables to their camera parameters
        camera.eye = eye
        camera.upVector = uV
        camera.isSmoothTransition = False
        viewport.camera = camera

        # make the changes in Fusion 360
        adsk.doEvents()
        viewport.refresh()

        # close debug file
        #output.close()

    except:
        if ui:
            ui.messageBox('Failed in rotate:\n{}'.format(traceback.format_exc()))

# Execute newVector
#   Inputs:
#       ui, Va, Vb, T
#   Outputs:
#       [Vector3D]
# create a new Vector from the angle generated from the hardware
def newVector(ui, Va, Vb, T):
    try:
        # create the components of the new Vector3D
        # if the angle is positive, use the positive projection of the horizontal Vector
        # if the angle is negative, use the negative projection of the horizontal Vector
        if (T > 0):
            mag_a = math.sin(math.radians(abs(T)))
            mag_b = math.cos(math.radians(abs(T)))
        else:
            mag_a = -math.sin(math.radians(abs(T)))
            mag_b = math.cos(math.radians(abs(T)))

        # return the new vector
        return adsk.core.Vector3D.create(mag_a * Vb.x + mag_b * Va.x, mag_a * Vb.y + mag_b * Va.y,
                                         mag_a * Vb.z + mag_b * Va.z)

    except:
        if ui:
            ui.messageBox('Failed in newUpVector:\n{}'.format(traceback.format_exc()))

# Execute screenVectors
#   Inputs:
#       ui, camera
#   Outputs:
#       uV, eV, sV
# Initialize the screen coordinate system used for vector rotations
def screenVectors(ui, camera):
    try:
        # assign local camera variables
        eye = camera.eye
        target = camera.target

        # initialize upVector
        # since Fusion360 incorrectly initializes the upVector, hardcode in the correct dimensions
        # uV = adsk.core.Vector3D.create(-0.4081498184182195, 0.8164965730110046, -0.4083467545927849)
        angle = target.asVector().angleTo(eye.asVector())
        if angle == 0.563626890972626:
            uV = adsk.core.Vector3D.create(-0.4081498184182195, 0.8164965730110046, -0.4083467545927849)
        else:
            uV = camera.upVector
        uV.normalize()

        # create eyeVector
        eV = target.vectorTo(eye)
        eV.normalize()

        # create sideVector
        sV = uV.crossProduct(eV)
        sV.normalize()

        return uV, eV, sV

    except:
        if ui:
            ui.messageBox('Failed in screenVectors:\n{}'.format(traceback.format_exc()))


# Execute distanceET
#   Inputs:
#       viewport, ui
#   Outputs:
#       [double]
# Find the distance between the camera eye and target
def distanceET(viewport, ui):
    try:
        # distance formula between the camera target and eye
        return pow(pow(viewport.camera.eye.x - viewport.camera.target.x, 2) + pow(viewport.camera.eye.y - viewport.camera.target.y, 2) + pow(viewport.camera.eye.z - viewport.camera.target.z, 2), .5)

    except:
        if ui:
            ui.messageBox('Failed in distanceET:\n{}'.format(traceback.format_exc()))


# Execute function_debug
#   Inputs:
#       ui, output, uV, sV, eV, E, title
#   Outputs:
#       output
# Write variables to an output file to help debugging
def function_debug(ui, output, uV, sV, eV, E, title):
    try:
        # write the title of this event to output
        output.write("---------------------------------\n")
        output.write(title + "\n\n")

        # write the upVector to output
        output.write("upVector.x = " + str(uV.x) + "\n")
        output.write("upVector.y = " + str(uV.y) + "\n")
        output.write("upVector.z = " + str(uV.z) + "\n\n")

        # write the sideVector to output
        output.write("sideVector.x = " + str(sV.x) + "\n")
        output.write("sideVector.y = " + str(sV.y) + "\n")
        output.write("sideVector.z = " + str(sV.z) + "\n\n")

        # write the eyeVector to output
        output.write("eyeVector.x = " + str(eV.x) + "\n")
        output.write("eyeVector.y = " + str(eV.y) + "\n")
        output.write("eyeVector.z = " + str(eV.z) + "\n\n")

        # write the eye to output
        output.write("Eye.x = " + str(E.x) + "\n")
        output.write("Eye.y = " + str(E.y) + "\n")
        output.write("Eye.z = " + str(E.z) + "\n\n")

        return output
    except: 
        if ui:
            ui.messageBox('Failed in function_debug:\n{}'.format(traceback.format_exc()))

# Execute initial_debug
#   Inputs:
#       ui, output, uV, sV, eV, E, Tx, Ty, Tz, t, r
#   Outputs:
#       output
# Write variables to an output file before any computations are made
def initial_debug(ui, output, uV, sV, eV, E, Tx, Ty, Tz, t, r):
    try:
        output.write("Initialized Variables:\n")

        # write the hardware inputted thetas to output
        output.write("Tx = " + str(Tx) + "\n")
        output.write("Ty = " + str(Ty) + "\n")
        output.write("Tz = " + str(Tz) + "\n\n")

        # write the camera target to output
        output.write("target.x = " + str(t.x) + "\n")
        output.write("target.y = " + str(t.y) + "\n")
        output.write("target.z = " + str(t.z) + "\n\n")

        # write the camera eye to output
        output.write("eye.x = " + str(E.x) + "\n")
        output.write("eye.y = " + str(E.y) + "\n")
        output.write("eye.z = " + str(E.z) + "\n\n")

        # write the radius to output
        output.write("radius = " + str(r) + "\n\n")

        # write the upVector to output
        output.write("upVector.x = " + str(uV.x) + "\n")
        output.write("upVector.y = " + str(uV.y) + "\n")
        output.write("upVector.z = " + str(uV.z) + "\n\n")

        # write the sideVector to output
        output.write("sideVector.x = " + str(sV.x) + "\n")
        output.write("sideVector.y = " + str(sV.y) + "\n")
        output.write("sideVector.z = " + str(sV.z) + "\n\n")

        # write the eyeVector to output
        output.write("eyeVector.x = " + str(eV.x) + "\n")
        output.write("eyeVector.y = " + str(eV.y) + "\n")
        output.write("eyeVector.z = " + str(eV.z) + "\n\n")

        return output

    except:
        if ui:
            ui.messageBox('Failed in initial_debug:\n{}'.format(traceback.format_exc()))

# Execute hardwareInput
#   Inputs:
#       ui
#   Outputs:
#       Lx, Ly, Lz, mode
#   Read in change in direction and mode inputs from hardware.
#   For testing purposes, just input three integers as the change in
#   direction inputs, and keep mode at 0 for orbit
def hardwareInput_debug(ui):
    try:
        # input from x rotary [-8192, 8192]
        Lx = 0

        # input from y rotary [-8192, 8192]
        Ly = 0

        # input from z rotary [-8192, 8192]
        Lz = 0

        # return the inputted values
        return Lx, Ly, Lz

    except:
        if ui:
            ui.messageBox('Failed in hardwareInput:\n{}'.format(traceback.format_exc()))

# Execute Pan
#   Inputs:
#       app, x, y
#   Outputs:
#       N/A
# the pan algorithm
def pan(app, x, y):
    try:
        cam = app.activeViewport.camera

        current_eye = cam.eye
        current_target = cam.target

        upVector = cam.upVector
        eye_target_vector = current_target.vectorTo(current_eye)
        sideVector = eye_target_vector.crossProduct(upVector)
        sideVector.normalize()

        global sensitivity_object
        pan_multiplier = sensitivity_object.getPanMultiplier()
        xChange = ((abs(upVector.x / 1.0) * y) + ((sideVector.x / 1.0) * x)) * pan_multiplier
        yChange = ((abs(upVector.y / 1.0) * y) + ((sideVector.y / 1.0) * x)) * pan_multiplier
        zChange = ((abs(upVector.z / 1.0) * y) + ((sideVector.z / 1.0) * x)) * pan_multiplier

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
#       app, x, y
#   Outputs:
#       N/A
# The zoom algorithm
def zoom(app, x, y):
    try:

        cam = app.activeViewport.camera

        global sensitivity_object
        zoom_multiplier = sensitivity_object.getZoomMultiplier()
        current_viewExtents = cam.viewExtents
        log_multiplier = abs(math.log(current_viewExtents, 20))
        new_viewExtents = ((x+y)*log_multiplier*zoom_multiplier) + current_viewExtents
        if new_viewExtents < .15:
            new_viewExtents = .15
        cam.viewExtents = new_viewExtents

        cam.isSmoothTransition = False
        cam.isFitView = False

        app.activeViewport.camera = cam
        adsk.doEvents()
        app.activeViewport.refresh()
    except:
        if ui:
            ui.messageBox('Failed in Zoom:\n{}'.format(traceback.format_exec()))
