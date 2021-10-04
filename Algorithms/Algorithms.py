#Author-Jared Carl
#Description-Implementation for algorithms for all three modes of operation for the 3D Mouse

from _typeshed import ReadableBuffer
import adsk.core, adsk.fusion, adsk.cam, traceback, math

def run(context):
    ui = None
    try:
        # create and initialize the application, viewport, and camera objects
        app = adsk.core.Application.get()
        viewport = app.activeViewport

        # initialize the camera smooth trnsition parameter to True
        viewport.camera.isSmoothTransition = True

        # create and initialize the message ui
        ui  = app.userInterface
        ui.messageBox('Script Executed!')

        # read in the arc lengths from the hardware
        Lx, Ly, Lz, mode = hardwareInput(ui)

        if mode == 0:
            # execute Orbit
            orbit(app, viewport, ui, Lx, Ly, Lz)
        elif mode == 1:
            # execute Pan
            pan(ui)
        elif mode == 2:
            # execute Zoom
            zoom(ui)
        else:
            # error, default to Orbit
            orbit(app, viewport, ui, Lx, Ly, Lz)

    except:
        if ui:
            ui.messageBox('Run script Failed:\n{}'.format(traceback.format_exc()))

# Execute Orbit
#   Inputs:
#       app, viewport, ui, Lx, Ly, Lz
#   Outputs:
#       N/A
#   Assume hardware sends operation mode input as Orbit.
#   Only changes the direction once, will add hardware input and output with 
#   the addition of that software.
def orbit(app, viewport, ui, Lx, Ly, Lz):
    try:
        # find the current orientation of the upVector
        uVx0, uVy0, uVz0 = upVectorOrientation(viewport.camera, ui)

        # execute the algorithm
        uVx1, uVy1, uVz1 = orbitAlgorithm(ui, Lx, Ly, Lz, uVx0, uVy0, uVz0)

        # set the new upVector
        viewport.camera.upVector = adsk.core.Vector3D.create(uVx1, uVy1, uVz1)

        # make the changes in Fusion 360
        adsk.doEvents()
        viewport.refresh()

    except:
        if ui:
            ui.messageBox('Failed in orbit:\n{}'.format(traceback.format_exc()))

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
        Lx = 1          # arc length relative to the x direction
        Ly = 1          # arc length relative to the y direction
        Lz = 1          # arc length relative to the z direction
        mode = 0        # mode of operation

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
        pi = math.pi    # initialize pi locally
        Rc = 3          # radius of the cue ball in ***some units***

        # calculate thetas
        Tx = (180 * Lx) / (pi * Rc)   # change in angle relative to x in the Lx arc length
        Ty = (180 * Ly) / (pi * Rc)   # change in angle relative to y in the Ly arc length
        Tz = (180 * Lz) / (pi * Rc)   # change in angle relative to z in the Lz arc length

        # calculate vector rotations around each axis
        # z-axis
        XzP = uVx0 * math.cos(math.radians(Tz)) - uVy0 * math.sin(math.radians(Tz))
        YzP = uVx0 * math.sin(math.radians(Tz)) + uVy0 * math.cos(math.radians(Tz))
        ZzP = uVz0
        
        # y-axis
        XyP = uVx0 * math.cos(math.radians(Ty)) + uVz0 * math.sin(math.radians(Ty))
        YyP = uVy0
        ZyP = uVz0 * math.sin(math.radians(Ty)) - uVx0 * math.cos(math.radians(Ty))

        # x-axis
        XxP = uVx0
        YxP = uVy0 * math.cos(math.radians(Tx)) - uVz0 * math.sin(math.radians(Tx))
        ZxP = uVy0 * math.sin(math.radians(Tx)) + uVz0 * math.cos(math.radians(Tx))

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
def pan(ui):
    try:
        ui.messageBox('Somehow wound up in Pan')
    except:
        if ui:
            ui.messageBox('Failed in Pan:\n{}'.format(traceback.format_exec()))

# Execute Zoom
#   Inputs:
#       ui
#   Outputs:
#       N/A
# Plceholder function for now
def zoom(ui):
    try:
        ui.messageBox('Somehow wound up in Zoom')
    except:
        if ui:
            ui.messageBox('Failed in Zoom:\n{}'.format(traceback.format_exec()))