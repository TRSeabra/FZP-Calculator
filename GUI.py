from tkinter import *
import efficiencies
import matplotlib


class Application(Tk):
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
        self.inputs_frame = Frame(self)
        self.inputs_frame.grid(row=0, column=0)
        self.lens_frame = Frame(self)
        self.lens_frame.grid(row=0, column=1)
        self.efficiency_frame = Frame(self)
        self.efficiency_frame.grid(row=1, column=0, columnspan=2)

        # Populating the input frame
        Label(self.inputs_frame, text="Lens' diameter:", font=("Arial", 10)).grid(row=0, column=0, sticky=SW)
        Label(self.inputs_frame, text="Feed's HPBW:", font=("Arial", 10)).grid(row=1, column=0, sticky=NW)
        self.diameter = StringVar(self)
        self.feed_hpbw = StringVar(self)
        Entry(self.inputs_frame, width=10, textvariable=self.diameter, font=("Arial", 10)).grid(row=0, column=1, sticky=S)
        Entry(self.inputs_frame, width=10, textvariable=self.feed_hpbw, font=("Arial", 10)).grid(row=0, column=1, sticky=N)


    def open(self):
        pass


if __name__ == "__main__":
    app = Application()
    app.open()