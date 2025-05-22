from tkinter import *
import efficiencies
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import numpy as np


class Application(Tk):

    c = 3e8

    def __init__(
            self,
            screenName: str | None = None,
            baseName: str | None = None,
            className: str = "Tk",
            useTk: bool = True,
            sync: bool = False,
            use: str | None = None,
    ):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.protocol('WM_DELETE_WINDOW', self.__quit)  # Necessary when embedding matplotlib in tkinter
        self.title("FZP Calculator")

        self.radii = list()

        self.grid_rowconfigure((0,1), weight=1)
        self.grid_columnconfigure((0,1), weight=1)
        self.inputs_frame = Frame(self)
        self.inputs_frame.grid(row=0, column=0, pady=10, padx=10)
        self.lens_frame = Frame(self)
        self.lens_frame.grid(row=0, column=1, pady=10, padx=10)
        self.efficiency_frame = Frame(self)
        self.efficiency_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

        # Populating the input frame
        Label(self.inputs_frame, text="Lens' diameter:", font=("Arial", 10)).grid(row=0, column=0, sticky=SW)
        Label(self.inputs_frame, text="Feed's HPBW:", font=("Arial", 10)).grid(row=1, column=0, sticky=NW)
        Label(self.inputs_frame, text="Frequency:", font=("Arial", 10)).grid(row=2, column=0, sticky=NW)
        self.diameter = StringVar(self, value="1")
        self.feed_hpbw = StringVar(self, value="60")
        self.frequency = StringVar(self, value="10000000000")
        Entry(self.inputs_frame, width=15, textvariable=self.diameter, font=("Arial", 10)).grid(row=0, column=1, sticky=S)
        Entry(self.inputs_frame, width=15, textvariable=self.feed_hpbw, font=("Arial", 10)).grid(row=1, column=1, sticky=N)
        Entry(self.inputs_frame, width=15, textvariable=self.frequency, font=("Arial", 10)).grid(row=2, column=1, sticky=N)
        Label(self.inputs_frame, text="m", font=("Arial", 10)).grid(row=0, column=2, sticky=SW)
        Label(self.inputs_frame, text="º", font=("Arial", 10)).grid(row=1, column=2, sticky=NW)
        Label(self.inputs_frame, text="Hz", font=("Arial", 10)).grid(row=2, column=2, sticky=NW)
        self.warning_label = Label(self.inputs_frame, font=("Arial", 10), fg="red")
        self.warning_label.grid(row=4, column=0, columnspan=3, pady=10)
        Button(self.inputs_frame, text="Calculate Radii", font=("Arial", 12), width=15, height=3, 
               command=self.__get_input).grid(row=5, column=0, columnspan=3, pady=20)

        # Populating the lens frame
        self.lens_figure = Figure(figsize=(4, 3), dpi=100)
        self.lens_plot = self.lens_figure.add_subplot()
        self.lens_plot.set_aspect("equal")
        self.lens_canvas = FigureCanvasTkAgg(self.lens_figure, master=self.lens_frame)
        self.lens_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

        # Populating the efficiency frame
        self.eff_figure = Figure(figsize=(10, 2.5), dpi=100)
        self.eff_plot = self.eff_figure.add_subplot()
        self.eff_canvas = FigureCanvasTkAgg(self.eff_figure, master=self.efficiency_frame)
        self.eff_canvas.get_tk_widget().grid(row=0, column=0, pady=10)
        self.focal_lenght = DoubleVar(self)
        self.eff_scale = Scale(self.efficiency_frame, orient=HORIZONTAL, variable=self.focal_lenght, resolution=0.01, from_=0.01, to=10)
        self.eff_scale.grid(row=1, column=0, sticky=EW)

    def open(self):
        self.mainloop()

    def __get_input(self):
        try:
            d = float(self.diameter.get())
            hpbw = float(self.feed_hpbw.get())
            f = float(self.frequency.get())
            if d <= 0 or hpbw <= 0 or hpbw >= 360:
                raise(ValueError)
            n = efficiencies.get_patern(hpbw)
            self.focal_lenght.set(0.5*d)
            self.eff_scale.configure(to=d*10)
            self.__draw_lens(d, f)  # Draw lens radii
            self.__draw_efficiency(d, n)  # Draw efficiency plot
        except ValueError:
            self.warning_label.configure(text="Invalid parameters")

    def __draw_lens(self, d: float, f: float):
        if f > 0:
            self.radii.clear()
            m = 1
            while True:
                aux1 = m * self.c / f
                aux2 = float(self.focal_lenght.get()) + (m * self.c / f / 4)
                r = math.sqrt(aux1*aux2)
                if r > d/2:
                    break
                self.radii.append(r)
                m += 1
            self.lens_plot.clear()
            for i in range(len(self.radii)-1):
                inner_radius = self.radii[i]
                outer_radius = self.radii[i+1]
                # Only fill even-numbered zones (alternating gray and blank)
                if i % 2 == 0:
                    ring = patches.Wedge(center=(0, 0), r=outer_radius, theta1=0, theta2=360,
                                         width=outer_radius - inner_radius, facecolor='gray', edgecolor='black')
                    self.lens_plot.add_patch(ring)
            # Set plot limits
            self.lens_plot.set_xlim(-d/2, d/2)
            self.lens_plot.set_ylim(-d/2, d/2)
            self.lens_canvas.draw()
        else:
            raise(ValueError)

    def __draw_efficiency(self, d: float, n:int):
        eff = np.zeros(int(d*1000)-1)
        fl = np.zeros(int(d*1000)-1)
        for i in range(0, int(d*1000)-1):
            fl[i] = (i + 1) * 0.01
            eff[i] =  efficiencies.illumination_numerical(n, d, fl[i]) * efficiencies.spillover(n, d, fl[i]) * efficiencies.phase(2) * efficiencies.blockage(self.radii, d)
        self.eff_plot.clear()
        self.eff_plot.plot(fl, eff)
        self.eff_canvas.draw()

    def __quit(self):
        """Forces the mainloop to exit"""
        self.quit()
        self.destroy()




if __name__ == "__main__":
    app = Application()
    app.open()