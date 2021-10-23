from tkinter import *
from tkinter import ttk
import tkinter as tk
import time


class SensitivityObject:
    def __init__(self):
        self.orbitSensitivity = 70
        self.panSensitivity = .0075  # inches per degree
        self.zoomSensitivity = 70

    def update(self, neworbit, newpan, newzoom):
        self.orbitSensitivity = neworbit
        self.panSensitivity = newpan
        self.zoomSensitivity = newzoom
        print('\n\nINSIDE OF UPDATE\n\n')

    def getOrbitSensitivity(self):
        return self.orbitSensitivity

    def getPanSensitivity(self):
        return self.panSensitivity

    def getZoomSensitivity(self):
        return self.zoomSensitivity


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

        ttk.Button(mainframe, text="Apply", command=self.apply).grid(column=8, row=6, sticky=W)

        self.orbit_sensitivity = tk.DoubleVar()
        self.orbit_sensitivity.set(self.sensitivity_object.getOrbitSensitivity)
        ttk.Label(mainframe, text="Orbit Sensitivity:").grid(column=1, row=1, sticky=E)
        orbit_slider = ttk.Scale(
            mainframe,
            from_=50,
            to=300,
            orient='horizontal',
            command=self.orbit_slider_changed,
            variable=self.orbit_sensitivity
        ).grid(
            column=3,
            row=1,
            sticky='we'
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
        self.pan_sensitivity.set(self.sensitivity_object.getPanSensitivity)
        ttk.Label(mainframe, text="Pan Sensitivity:").grid(column=1, row=2, sticky=E)
        pan_slider = ttk.Scale(
            mainframe,
            from_=.0025,
            to=.015,
            orient='horizontal',
            command=self.pan_slider_changed,
            variable=self.pan_sensitivity
        ).grid(
            column=3,
            row=2,
            sticky='we'
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
        self.zoom_sensitivity.set(self.sensitivity_object.getZoomSensitivity)
        ttk.Label(mainframe, text="Zoom Sensitivity:").grid(column=1, row=3, sticky=E)
        zoom_slider = ttk.Scale(
            mainframe,
            from_=.01,
            to=.3,
            orient='horizontal',
            command=self.zoom_slider_changed,
            variable=self.zoom_sensitivity
        ).grid(
            column=3,
            row=3,
            sticky='we'
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

        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.root.bind("<FocusOut>", sensitivity_object(self.orbit_sensitivity.get(), self.pan_sensitivity.get(), self.zoom_sensitivity.get()))
        # self.root.bind("<Return>", sensitivity_object(self.orbit_sensitivity.get(), self.pan_sensitivity.get(), self.zoom_sensitivity.get()))
        self.root.mainloop()

    def on_closing(self):
        self.closed = True

    def is_running(self):
        return not self.closed

    def get_sensitivities(self):
        return self.orbit_sensitivity.get(), self.pan_sensitivity.get(), self.zoom_sensitivity.get()

    def apply(self):
        self.sensitivity_object.update(self.orbit_sensitivity.get(), self.pan_sensitivity.get(), self.zoom_sensitivity.get())

    def get_current_orbit(self):
        return '{: .2f} mm per rotation'.format(self.orbit_sensitivity.get())

    def orbit_slider_changed(self, event):
        self.orbit_value_label.configure(text=self.get_current_orbit())

    def get_current_pan(self):
        return '{: .4f} inches per degree'.format(self.pan_sensitivity.get())

    def pan_slider_changed(self, event):
        self.pan_value_label.configure(text=self.get_current_pan())

    def get_current_zoom(self):
        return '{: .2f} mm per rotation'.format(self.zoom_sensitivity.get())

    def zoom_slider_changed(self, event):
        self.zoom_value_label.configure(text=self.get_current_zoom())


def main():
    ts = SensitivityObject()
    gui = CustomizationGUI(ts.updatevalues)
    print('1')
    time.sleep(4)
    print(ts.displayvalues())


if __name__ == '__main__':
    main()


