#Author-Jared Carl
#Description-Implementation for algorithms for all three modes of operation for the 3D Mouse

from _typeshed import ReadableBuffer
import adsk.core, adsk.fusion, adsk.cam, traceback, math

def run(context):
    ui = None
    try:
        # create and initialize the application, viewportm and camera objects
        app = adsk.core.Application.get()
        viewport = app.activeViewport
        camera = viewport.camera

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
#       app, viewport, camera, ui
#   Outputs:
#       N/A
#   Assume hardware sends operation mode input as Orbit.
#   Only changes the direction once, will add hardware input and output with 
#   the addition of that software.
def orbit(app, viewport, camera, ui, Lx, Ly, Lz):
    try:
        # find the current orientation of the upVector
        uVx0, uVy0, uVz0 = upVectorOrientation(camera, ui)

        # execute the algorithm
        uVx1, uVy1, uVz1 = orbitAlgorithm(ui, Lx, Ly, Lz, uVx0, uVy0, uVz0)

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
#       Lx, Ly, Lz
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
# Run through the Orbit algorithm described in the Conceptual Design Document
def orbitAlgorithm(ui, Lx, Ly, Lz, uVx0, uVy0, uVz0):
    try:
        pi = math.pi    # initialize pi locally
        Rc = 3          # radius of the cue ball in ***some units***

        Tx = (180 * Lx) / (pi * Rc) # change in angle relative to x in the Lx arc length
        Ty = (180 * Ly) / (pi * Rc) # change in angle relative to y in the Ly arc length
        Tz = (180 * Lz) / (pi * Rc) # change in angle relative to z in the Lz arc length

    except:
        if ui:
            ui.messageBox('Failed in algorithm:\n{}'.format(traceback.format_exc()))

# Execute Pan
# Placeholder function for now
def pan(ui):
    try:
        ui.messageBox('Somehow wound up in Pan')
    except:
        if ui:
            ui.messageBox('Failed in Pan:\n{}'.format(traceback.format_exec()))

# Execute Zoom
# Plceholder function for now
def zoom(ui):
    try:
        ui.messageBox('Somehow wound up in Zoom')
    except:
        if ui:
            ui.messageBox('Failed in Zoom:\n{}'.format(traceback.format_exec()))