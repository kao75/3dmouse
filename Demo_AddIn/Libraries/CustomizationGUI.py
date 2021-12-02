from tkinter import *
from tkinter import ttk
import tkinter as tk
import time


class SensitivityObject:
    def __init__(self):
        self.orbitSensitivity = 1  # degrees per trackball degree
        self.panSensitivity = .0075  # inches per trackball degree
        self.zoomSensitivity = .00125  # inches per trackball degree
        self.dirX = 1
        self.dirY = -1
        self.dirZ = 1

    def update(self, neworbit, newpan, newzoom, newdirX, newdirY, newdirZ):
        self.orbitSensitivity = neworbit
        self.panSensitivity = newpan
        self.zoomSensitivity = newzoom
        self.dirX = newdirX
        self.dirY = newdirY
        self.dirZ = newdirZ

    def getOrbitSensitivity(self):
        return self.orbitSensitivity

    def getOrbitMultiplier(self):
        return 75 * self.orbitSensitivity

    def getPanSensitivity(self):
        return self.panSensitivity

    def getPanMultiplier(self):
        return .0247 * self.panSensitivity

    def getZoomSensitivity(self):
        return self.zoomSensitivity

    def getZoomMultiplier(self):
        return self.zoomSensitivity

    def getDirections(self):
        return {'x': self.dirX, 'y': self.dirY, 'z': self.dirZ}


class CustomizationGUI:
    def __init__(self, sensitivity_object):
        self.root = Tk()
        self.root.title("3D Mouse Settings")
        self.closed = False
        self.sensitivity_object = sensitivity_object

        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Button(mainframe, text="Cancel", command=self.root.destroy).grid(column=1, row=6, sticky=W)
        ttk.Button(mainframe, text="Apply", command=self.apply).grid(column=5, row=6, sticky=W)

        directions = self.sensitivity_object.getDirections()

        self.invertedX = tk.BooleanVar()
        if directions['x'] == 1:
            self.invertedX.set(False)
        else:
            self.invertedX.set(True)
        Checkbutton(mainframe, text="Invert X", variable=self.invertedX).grid(column=5, row=1, sticky='W')

        self.invertedY = tk.BooleanVar()
        if directions['y'] == 1:
            self.invertedY.set(False)
        else:
            self.invertedY.set(True)
        Checkbutton(mainframe, text="Invert Y", variable=self.invertedY).grid(column=5, row=2, sticky='W')

        self.invertedZ = tk.BooleanVar()
        if directions['z'] == 1:
            self.invertedZ.set(False)
        else:
            self.invertedZ.set(True)
        Checkbutton(mainframe, text="Invert Z", variable=self.invertedZ).grid(column=5, row=3, sticky='W')

        self.orbit_sensitivity = tk.DoubleVar()
        self.orbit_sensitivity.set(self.sensitivity_object.getOrbitSensitivity())
        ttk.Label(mainframe, text="Orbit Sensitivity:").grid(column=1, row=1, sticky=E)
        orbit_slider = ttk.Scale(
            mainframe,
            from_=.25,
            to=3,
            orient='horizontal',
            command=self.orbit_slider_changed,
            variable=self.orbit_sensitivity
        ).grid(
            column=3,
            row=1,
            sticky='e'
        )
        self.orbit_value_label = ttk.Label(
            mainframe,
            text=self.get_current_orbit()
        )
        self.orbit_value_label.grid(
            row=1,
            column=4,
            sticky='n'
        )

        self.pan_sensitivity = tk.DoubleVar()
        self.pan_sensitivity.set(self.sensitivity_object.getPanSensitivity())
        ttk.Label(mainframe, text="Pan Sensitivity:").grid(column=1, row=2, sticky=E)
        pan_slider = ttk.Scale(
            mainframe,
            from_=.0025,
            to=.3,
            orient='horizontal',
            command=self.pan_slider_changed,
            variable=self.pan_sensitivity
        ).grid(
            column=3,
            row=2,
            sticky='e'
        )
        self.pan_value_label = ttk.Label(
            mainframe,
            text=self.get_current_pan()
        )
        self.pan_value_label.grid(
            row=2,
            column=4,
            sticky='n'
        )

        self.zoom_sensitivity = tk.DoubleVar()
        self.zoom_sensitivity.set(self.sensitivity_object.getZoomSensitivity())
        ttk.Label(mainframe, text="Zoom Sensitivity:").grid(column=1, row=3, sticky=E)
        zoom_slider = ttk.Scale(
            mainframe,
            from_=.001,
            to=.35,
            orient='horizontal',
            command=self.zoom_slider_changed,
            variable=self.zoom_sensitivity
        ).grid(
            column=3,
            row=3,
            sticky='e'
        )
        self.zoom_value_label = ttk.Label(
            mainframe,
            text=self.get_current_zoom()
        )
        self.zoom_value_label.grid(
            row=3,
            column=4,
            sticky='n'
        )

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.root.mainloop()

    def on_closing(self):
        self.closed = True

    def is_running(self):
        return not self.closed

    def get_sensitivities(self):
        return self.orbit_sensitivity.get(), self.pan_sensitivity.get(), self.zoom_sensitivity.get()

    def apply(self):
        newdirX = 1
        newdirY = 1
        newdirZ = 1
        if self.invertedX.get() == True:
            newdirX = -1
        if self.invertedY.get() == True:
            newdirY = -1
        if self.invertedZ.get() == True:
            newdirZ = -1
        self.sensitivity_object.update(self.orbit_sensitivity.get(), self.pan_sensitivity.get(), self.zoom_sensitivity.get(), newdirX, newdirY, newdirZ)

    def get_current_orbit(self):
        return '{: .4f} degrees per trackball degree'.format(self.orbit_sensitivity.get())

    def orbit_slider_changed(self, event):
        self.orbit_value_label.configure(text=self.get_current_orbit())

    def get_current_pan(self):
        return '{: .4f} inches per trackball degree'.format(self.pan_sensitivity.get())

    def pan_slider_changed(self, event):
        self.pan_value_label.configure(text=self.get_current_pan())

    def get_current_zoom(self):
        return '{: .4f} inches per trackball degree'.format(self.zoom_sensitivity.get())

    def zoom_slider_changed(self, event):
        self.zoom_value_label.configure(text=self.get_current_zoom())


def main():
    so = SensitivityObject()
    gui = CustomizationGUI(so)
    print(so.dirX)
    print(so.dirY)
    print(so.dirZ)
    time.sleep(4)


if __name__ == '__main__':
    main()


