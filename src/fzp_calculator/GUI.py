from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import numpy as np
from importlib import resources

import fzp_calculator.efficiencies as efficiencies

class Application(Tk):

    c = 3e8
    units = {"Hz": 1,
             "kHz": 1e3,
             "MHz": 1e6,
             "GHz": 1e9}

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
        self.resizable(False, False)
        icon_path = resources.files("fzp_calculator.resources").joinpath("icon.png")
        self.icon = PhotoImage(file=icon_path)
        self.iconphoto(False, self.icon)

        self.radii = list()

        self.grid_rowconfigure((0,1), weight=1)
        self.grid_columnconfigure((0,1,2), weight=1)
        self.inputs_frame = Frame(self)
        self.inputs_frame.grid(row=0, column=0, pady=10, padx=10)
        self.radii_frame = Frame(self)
        self.radii_frame.grid(row=0, column=1, pady=10, padx=10, sticky=NE)
        self.lens_frame = Frame(self)
        self.lens_frame.grid(row=0, column=2, pady=10, padx=10, sticky=E)
        self.efficiency_frame = Frame(self)
        self.efficiency_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10)

        # Populating the input frame
        self.parameters_frame = LabelFrame(self.inputs_frame, text="Parameters")
        self.parameters_frame.grid(row=0, column=0, columnspan=3)
        auxframe = Frame(self.parameters_frame)
        auxframe.grid(row=0, column=0, pady=10, padx=10)
        Label(auxframe, text="Lens' diameter:", font=("Arial", 12)).grid(row=0, column=0, sticky=SW, padx=5, pady=5)
        Label(auxframe, text="Feed's HPBW:", font=("Arial", 12)).grid(row=1, column=0, sticky=NW, padx=5, pady=5)
        Label(auxframe, text="Frequency:", font=("Arial", 12)).grid(row=2, column=0, sticky=NW, padx=5, pady=5)
        self.diameter = StringVar(self, value="1")
        self.feed_hpbw = StringVar(self, value="60")
        self.frequency = StringVar(self, value="10")
        Entry(auxframe, width=15, textvariable=self.diameter, font=("Arial", 12)).grid(row=0, column=1, sticky=S, padx=5, pady=5)
        Entry(auxframe, width=15, textvariable=self.feed_hpbw, font=("Arial", 12)).grid(row=1, column=1, sticky=N, padx=5, pady=5)
        Entry(auxframe, width=15, textvariable=self.frequency, font=("Arial", 12)).grid(row=2, column=1, sticky=N, padx=5, pady=5)
        Label(auxframe, text="m", font=("Arial", 12)).grid(row=0, column=2, sticky=SW, padx=5, pady=5)
        Label(auxframe, text="º", font=("Arial", 12)).grid(row=1, column=2, sticky=NW, padx=5, pady=5)
        self.unit = StringVar(self, value = tuple(self.units.keys())[3])
        ttk.Spinbox(auxframe, font=("Arial", 12), values=tuple(self.units.keys()), textvariable=self.unit, 
                    state="readonly", width=4).grid(row=2, column=2, sticky=NW, padx=5, pady=5)
        self.input_button = Button(auxframe, text="Read parameters", font=("Arial", 12), width=15, height=2, 
                                   command=self.__get_input)
        self.input_button.grid(row=3, column=0, pady=20, columnspan=3)
        self.warning_label = Label(self.inputs_frame, font=("Arial", 10), fg="red")
        self.warning_label.grid(row=1, column=0, columnspan=3, pady=10)
        Label(self.inputs_frame, text="Focal length:", font=("Arial", 12)).grid(row=2, column=0, sticky=W, pady=(50, 10))
        Label(self.inputs_frame, text="Estimated efficiency:", font=("Arial", 12)).grid(row=3, column=0, sticky=W)
        self.focal_lenght_label = Label(self.inputs_frame, font=("Arial", 12))
        self.focal_lenght_label.grid(row=2, column=1, pady=(50, 10), sticky=E)
        Label(self.inputs_frame, text="m", font=("Arial", 12)).grid(row=2, column=2, pady=(50, 10))
        self.eff = StringVar(self) 
        self.eff_label = Label(self.inputs_frame, textvariable=self.eff, font=("Arial", 12))
        self.eff_label.grid(row=3, column=1, sticky=E)
        Label(self.inputs_frame, text="%", font=("Arial", 12)).grid(row=3, column=2)

        # Populating the radii frame
        self.choices = StringVar()
        self.radii_list = Listbox(self.radii_frame, height=15, font=("Arial", 10), listvariable=self.choices)
        self.radii_list.grid(row=0, column=0, sticky=NE, pady=20)

        # Populating the lens frame
        self.lens_figure = Figure(figsize=(4, 4), dpi=100)
        self.lens_figure.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.15)
        self.lens_plot = self.lens_figure.add_subplot()
        self.lens_plot.set_aspect("equal")
        self.lens_canvas = FigureCanvasTkAgg(self.lens_figure, master=self.lens_frame)
        self.lens_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
        self.lens_canvas.get_tk_widget().configure(highlightthickness=2, highlightbackground="black")

        # Populating the efficiency frame
        self.eff_figure = Figure(figsize=(10, 2.5), dpi=100)
        self.eff_figure.subplots_adjust(left=0.075, right=0.98, top=0.9, bottom=0.2)
        self.eff_plot = self.eff_figure.add_subplot()
        self.eff_plot.set_xlabel("Focal length [m]")
        self.eff_plot.set_ylabel("aperture efficiency")
        self.eff_canvas = FigureCanvasTkAgg(self.eff_figure, master=self.efficiency_frame)
        self.eff_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
        self.eff_canvas.get_tk_widget().configure(highlightthickness=2, highlightbackground="black")
        self.focal_lenght = DoubleVar(self)
        self.focal_lenght_label.configure(textvariable=self.focal_lenght)
        self.eff_scale = Scale(self.efficiency_frame, orient=HORIZONTAL, variable=self.focal_lenght, resolution=0.01, from_=0.01, to=10, 
                               command=self.__get_input, state=DISABLED)
        self.eff_scale.grid(row=1, column=0, sticky=EW, padx=20)

    def open(self):
        self.mainloop()

    def __get_input(self, event = None):
        try:
            d = float(self.diameter.get())
            hpbw = float(self.feed_hpbw.get())
            f = float(self.frequency.get()) * self.units[self.unit.get()]
            if d <= 0 or hpbw <= 0 or hpbw >= 360:
                raise(ValueError)
            n = efficiencies.get_patern(hpbw)
            if event is None:
                self.focal_lenght.set(0.5*d)
                self.eff_scale.configure(to=d*5)
            self.__draw_lens(d, f)  # Draw lens radii
            self.__draw_efficiency(d, n, f)  # Draw efficiency plot
            fl = float(self.focal_lenght.get())
            eff = efficiencies.illumination_numerical(n, d, fl) * efficiencies.spillover(n, d, fl) * efficiencies.phase(2) * efficiencies.blockage(fl, d, f)
            self.eff.set(f"{100*eff:.4f}")
            self.eff_scale.configure(state=NORMAL)
        except ValueError:
            self.warning_label.configure(text="Invalid parameters")

    def __draw_lens(self, d: float, f: float):
        if f > 0:
            self.radii.clear()
            radii_display = list()
            m = 1
            while True:
                aux1 = m * self.c / f
                aux2 = float(self.focal_lenght.get()) + (m * self.c / f / 4)
                r = math.sqrt(aux1*aux2)
                if r > d/2:
                    break
                self.radii.append(r)
                radii_display.append(f"r({m}) = {r:.3f} m")
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
            self.lens_plot.add_patch(plt.Circle((0, 0), d/2, color="b", fill=False, linewidth=2))
            # Set plot limits
            self.lens_plot.set_xlim(-d/2 * 1.01, d/2 * 1.01)
            self.lens_plot.set_ylim(-d/2 * 1.01, d/2 * 1.01)
            self.lens_canvas.draw()
            self.choices.set(radii_display)
        else:
            raise(ValueError)

    def __draw_efficiency(self, d: float, n:int, f:float):
        eff = np.zeros(int(d*1000)-1)
        fl = np.zeros(int(d*1000)-1)
        for i in range(0, int(d*1000)-1):
            fl[i] = (i + 1) * 0.01
            eff[i] =  efficiencies.illumination_numerical(n, d, fl[i]) * efficiencies.spillover(n, d, fl[i]) * efficiencies.phase(2) * efficiencies.blockage(fl[i], d, f)
        self.eff_plot.clear()
        self.eff_plot.set_xlabel("Focal length [m]")
        self.eff_plot.set_ylabel("aperture efficiency")
        self.eff_plot.plot(fl, eff)
        self.eff_plot.set_xlim([0, 5*d])
        self.eff_plot.set_ylim([0, np.max(eff)*1.1])
        self.eff_plot.plot(np.array([float(self.focal_lenght.get()), float(self.focal_lenght.get())]), np.array([0, np.max(eff)*1.1]), "red")
        self.eff_canvas.draw()

    def __quit(self):
        """Forces the mainloop to exit"""
        self.quit()
        self.destroy()


if __name__ == "__main__":
    app = Application()
    app.open()