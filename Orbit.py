#Author - Jared Carl
#Description - Orbit implementation that linearly runs one full rotation

import adsk.core, adsk.fusion, adsk.cam, traceback, math

# NOTES:
# in order to abstract as much as possible, the only user (hardware) input needed is
#   in the "hardwareInput" function at the bottom of the file.
#
# to disable the debugging file, comment out these lines:
#   47-50, 69, 83, 102, 121, 133
#
# to enable the debugging file, make sure the file location in line 48 is legit and 
# uses "\\" to separate nested folders

# Execute run
# automatically runs at program initialization
def run(context):
    ui = None
    try:
        # create and initialize the application, viewport, and camera objects
        app = adsk.core.Application.get()
        viewport = app.activeViewport
        
        # initialize the camera smooth trnsition parameter to True
        viewport.camera.isSmoothTransition = True

        # initialize the camera
        camera = viewport.camera

        # create and initialize the message ui
        ui  = app.userInterface

        # initialize and create screen vectors
        uV, eV, sV = screenVectors(ui, camera)

        # execute orbit
        orbit(ui, viewport, uV, eV, sV)       

    except:
        if ui:
            ui.messageBox('Failed in run:\n{}'.format(traceback.format_exc()))

# Execute orbit
#   Inputs:
#       ui, viewport, uV, eV, sV
#   Outputs:
#       N/A
# The shell of the orbit algorithm
def orbit(ui, viewport, uV, eV, sV):
    try:
        # set up debugging of screen coordinates
        filePath = 'C:\\Users\\mcqkn\\Documents\\Fall_2021\\ECE1896\\Autodesk Output Files'
        fileName = '\\Orbit_debug.txt'
        output = open(filePath + fileName, 'w')
        output.write("This is the Orbit debugging file:\n\n")

        # initialize the camera, target, and eye variables
        camera = viewport.camera
        target = camera.target
        eye = camera.eye

        # find the distance between the Target and the Eye
        r = distanceET(viewport, ui)

        # read in the hardware input
        Lx, Ly, Lz, f, mode = hardwareInput(ui)

        # translate the hardware input to a relative change to an angle
        Tx = Lx / 8192 * f
        Ty = Ly / 8192 * f
        Tz = Lz / 8192 * f

        # run initial debug
        output = initial_debug(ui, output, uV, sV, eV, eye, Tx, Ty, Tz, target, r)

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
            output = function_debug(ui, output, uV, sV, eV, eye, 'New upVector:')

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
            output = function_debug(ui, output, uV, sV, eV, eye, 'New sideVector:')

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
            output = function_debug(ui, output, uV, sV, eV, eye, 'New eyeVector:')

        # re-assign changed Fusion360 variables to their camera parameters
        camera.eye = eye
        camera.upVector = uV
        viewport.camera = camera

        # make the changes in Fusion 360
        adsk.doEvents()
        viewport.refresh()

        # close debug file
        output.close()

    except:
        if ui:
            ui.messageBox('Failed in rotate:\n{}'.format(traceback.format_exc()))

# Execute newVector
#   Inputs:
#       ui, uV, sV, T
#   Outputs:
#       [Vector3D]
# create a new Vector from the angle generated from the hardware
def newVector(ui, Va, Vb, T):
    try:
        # create the components of the new Vector3D
        # if the angle is positive, use the positive projection of the horizontal Vector
        # if the angle is negative, use the negative projection of the horizontal Vector
        if(T > 0):
            mag_a = (math.pow((math.pow((Va.x), 2) + math.pow((Va.y), 2) + math.pow((Va.z), 2)), .5) / math.pow((math.pow((Vb.x), 2) + math.pow((Vb.y), 2) + math.pow((Vb.z), 2)), .5)) * math.cos(math.radians(90 - abs(T)))
            mag_b = math.cos(math.radians(90 - abs(T)))
        else:
            mag_a = -(math.pow((math.pow((Va.x), 2) + math.pow((Va.y), 2) + math.pow((Va.z), 2)), .5) / math.pow((math.pow((Vb.x), 2) + math.pow((Vb.y), 2) + math.pow((Vb.z), 2)), .5)) * math.cos(math.radians(90 - abs(T)))
            mag_b = math.cos(math.radians(90 - abs(T)))

        # create the vector components of the new Vector3D in terms of Va and Vb
        a = adsk.core.Vector3D.create(mag_a * Vb.x, mag_a * Vb.y, mag_a * Vb.z)
        b = adsk.core.Vector3D.create(mag_b * Va.x, mag_b * Va.y, mag_b * Va.z)

        # return the new vector
        return adsk.core.Vector3D.create(a.x + b.x, a.y + b.y, a.z + b.z)

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
        uV = adsk.core.Vector3D.create(-0.4081498184182195, 0.8164965730110046, -0.4083467545927849)
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
#       app, viewport
#   Outputs:
#       Rf
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
#
#   Outputs:
#
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
def hardwareInput(ui):
    try:
        # input from x rotary [-8192, 8192]
        Lx = 0

        # input from y rotary [-8192, 8192]
        Ly = 0

        # input from z rotary [-8192, 8192]
        Lz = 0

        # set the relative factor for the thetas
        f = 90

        # set the Operation Mode to 0 for Orbit
        # not used in this program, just passed through for later reference
        mode = 0

        # return the inputted values
        return Lx, Ly, Lz, f, mode

    except:
        if ui:
            ui.messageBox('Failed in hardwareInput:\n{}'.format(traceback.format_exc()))
