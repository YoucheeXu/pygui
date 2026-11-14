import tkinter as tk
from tkinter.font import Font
from typing import cast

from pyutilities_simple.logit import po

from pygui_simple.tkwin.calendarctrl import CalendarDialog
from pygui_simple.tkwin.tkcontrols import (
    ButtonCtrl,
    CheckbuttonCtrl,
    ComboboxCtrl,
    EntryCtrl,
    FrameCtrl,
    LabelCtrl,
    LabelFrameCtrl,
    NotebookCtrl,
    RadiobuttonCtrl,
    ScrollableFrameCtrl,
    ScrolledTextCtrl,
    SlideSwitchCtrl,
)
from pygui_simple.tkwin.tkwin import tkWin


class App(tkWin):
    def __init__(self):
        super().__init__("", "")

        # configure window
        self.title("test_win")
        self.center_window(1100, 580)

        # configure grid layout (4x4)
        _ = self.win.grid_columnconfigure(1, weight=1)
        _ = self.win.grid_columnconfigure((2, 3), weight=0)
        _ = self.win.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        # self.sidebar_frame: FrameCtrl = FrameCtrl(self, width=140, corner_radius=0)
        self.sidebar_frame: FrameCtrl = FrameCtrl(self, width=140)
        sidebar_frame = cast(tk.Widget, self.sidebar_frame.control)
        sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        _ = sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label: LabelCtrl = LabelCtrl(self.sidebar_frame, "CustomTkinter", font=Font(size=20, weight="bold"))
        # self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.logo_label.assemble({"layout":"grid", "grid":"{'row':0, 'column': 0, 'padx':20, 'pady':(20,10)}"})
        self.sidebar_button_1: ButtonCtrl = ButtonCtrl(self.sidebar_frame, command=self.sidebar_button_event)
        # self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_1.assemble({"layout":"grid", "grid":"{'row':1, 'column': 0, 'padx':20, 'pady':10}"})
        self.sidebar_button_2: ButtonCtrl = ButtonCtrl(self.sidebar_frame, text="b2", command=self.sidebar_button_event)
        # self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.assemble({"layout":"grid", "grid":"{'row':2, 'column': 0, 'padx':20, 'pady':10}"})
        self.sidebar_button_3: ButtonCtrl = ButtonCtrl(self.sidebar_frame, command=self.sidebar_button_event)
        # self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_3.assemble({"layout":"grid", "grid":"{'row':3, 'column': 0, 'padx':20, 'pady':10}"})
        self.appearance_mode_label: LabelCtrl = LabelCtrl(self.sidebar_frame, "Appearance Mode:", anchor="w")
        # self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_label.assemble({"layout":"grid", "grid":"{'row':5, 'column': 0, 'padx':20, 'pady':(10,0)}"})
        # self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
        #                                                                command=self.change_appearance_mode_event)
        # self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label: LabelCtrl = LabelCtrl(self.sidebar_frame, "UI Scaling:", anchor="w")
        # self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_label.assemble({"layout":"grid", "grid":"{'row':7, 'column': 0, 'padx':20, 'pady':(10,0)}"})
        # self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
        #                                                        command=self.change_scaling_event)
        # self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry: EntryCtrl = EntryCtrl(self, "Entry")
        # self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.entry.assemble({"layout":"grid", "grid":"{'row':3, 'column': 1, 'columnspan':2, 'padx':20, 'pady':(20,20), 'sticky':'nsew'}"})

        # self.main_button_1 = ButtonCtrl(self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1: ButtonCtrl = ButtonCtrl(self)
        # self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.main_button_1.assemble({"layout":"grid", "grid":"{'row':3, 'column': 3, 'padx':(20,20), 'pady':(20,20), 'sticky':'nsew'}"})

        # create textbox
        self.textbox: ScrolledTextCtrl = ScrolledTextCtrl(self, width=250)
        # self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.textbox.assemble({"layout":"grid", "grid":"{'row':0, 'column': 1, 'padx':(20,0), 'pady':(20,0), 'sticky':'nsew'}"})

        # create tabview
        self.tabview: NotebookCtrl = NotebookCtrl(self, width=250)
        # self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.assemble({"layout":"grid", "grid":"{'row':0, 'column': 2, 'padx':(20,0), 'pady':(20,0), 'sticky':'nsew'}"})
        self.tabview.add("Tabview")
        self.tabview.add("Tab 2")
        self.tabview.add("Tab 3")
        _ = cast(tk.Widget, self.tabview.tab("Tabview").control).grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        _ = cast(tk.Widget, self.tabview.tab("Tab 2").control).grid_columnconfigure(0, weight=1)

        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("CTkTabview"), dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.combobox_1: ComboboxCtrl = ComboboxCtrl(self.tabview.tab("Tabview"),
                                                    values=["Value 1", "Value 2", "Value Long....."])
        # self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.combobox_1.assemble({"layout":"grid", "grid":"{'row':1, 'column':0, 'padx':20, 'pady':(10,10)}"})
        self.string_input_button: ButtonCtrl = ButtonCtrl(self.tabview.tab("Tabview"), text="Open InputDialog",
                                                           command=self.open_input_dialog_event)
        # self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.string_input_button.assemble({"layout":"grid", "grid":"{'row':2, 'column':0, 'padx':20, 'pady':(10,10)}"})
        self.label_tab_2: LabelCtrl = LabelCtrl(self.tabview.tab("Tab 2"), "Label on Tab 2")
        # self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        self.label_tab_2.assemble({"layout":"grid", "grid":"{'row':0, 'column':0, 'padx':20, 'pady':20}"})
        self.label_frame: LabelFrameCtrl = LabelFrameCtrl(self.tabview.tab("Tab 3"), "hello", width=20)
        self.label_frame.assemble({"layout":"grid", "grid":"{'row':0, 'column':0, 'padx':20, 'pady':20}"})
        self.string_input_button.assemble({"layout":"grid", "grid":"{'row':2, 'column':0, 'padx':20, 'pady':(10,10)}"})
        self.label_tab_3: LabelCtrl = LabelCtrl(self.label_frame, "Label on Tab 3")
        # self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        self.label_tab_3.assemble({"layout":"grid", "grid":"{'row':0, 'column':0, 'padx':20, 'pady':20}"})

        # create radiobutton frame
        self.radiobutton_frame: FrameCtrl = FrameCtrl(self)
        # self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radiobutton_frame.assemble({"layout":"grid", "grid":"{'row':0, 'column':3, 'padx':(20,20), 'pady':(20,0), 'sticky':'nsew'}"})
        self.radio_var: tk.IntVar = tk.IntVar(value=0)
        self.label_radio_group: LabelCtrl = LabelCtrl(self.radiobutton_frame, text="CTkRadioButton Group:")
        # self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        self.label_radio_group.assemble({"layout":"grid", "grid":"{'row':0, 'column':2, 'columnspan':1, 'padx':10, 'pady':10, 'sticky':''}"})
        self.radio_button_1: RadiobuttonCtrl = RadiobuttonCtrl(self.radiobutton_frame, variable=self.radio_var, value=0)
        # self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_1.assemble({"layout":"grid", "grid":"{'row':1, 'column':2, 'padx':10, 'pady':20, 'sticky':'n'}"})
        self.radio_button_2: RadiobuttonCtrl = RadiobuttonCtrl(self.radiobutton_frame, variable=self.radio_var, value=1)
        # self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2.assemble({"layout":"grid", "grid":"{'row':2, 'column':2, 'padx':10, 'pady':20, 'sticky':'n'}"})
        self.radio_button_3: RadiobuttonCtrl = RadiobuttonCtrl(self.radiobutton_frame, variable=self.radio_var, value=2)
        # self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_3.assemble({"layout":"grid", "grid":"{'row':3, 'column':2, 'padx':10, 'pady':20, 'sticky':'n'}"})

        # create slider and progressbar frame
        # self.slider_progressbar_frame: FrameCtrl = FrameCtrl(self, fg_color="transparent")
        self.slider_progressbar_frame: FrameCtrl = FrameCtrl(self)
        # self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.assemble({"layout":"grid", "grid":"{'row':1, 'column':1, 'padx':(20, 0), 'pady':(20, 0), 'sticky':'nsew'}"})
        slider_progressbar_frame_ctrl = cast(tk.Widget, self.slider_progressbar_frame.control)
        _ = slider_progressbar_frame_ctrl.grid_columnconfigure(0, weight=1)
        _ = slider_progressbar_frame_ctrl.grid_rowconfigure(4, weight=1)
        # self.seg_button_1 = customtkinter.CTkSegmentedButton(self.slider_progressbar_frame)
        # self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        # self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        # self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        # self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        # self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        # self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        # self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        # create scrollable frame
        # self.scrollable_frame: ScrollableFrameCtrl  = ScrollableFrameCtrl(self, "CTkScrollableFrame")
        self.scrollable_frame: ScrollableFrameCtrl = ScrollableFrameCtrl(self)
        # self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.assemble({"layout":"grid", "grid":"{'row':1, 'column':2, 'padx':(20, 0), 'pady':(20, 0), 'sticky':'nsew'}"})
        _ = cast(tk.Widget,  self.scrollable_frame.control).grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches: list[SlideSwitchCtrl] = []
        for i in range(100):
            # switch = SlideSwitchCtrl(self.scrollable_frame, text=f"CTkSwitch {i}")
            switch = SlideSwitchCtrl(self.scrollable_frame, width=40, height=20)
            # switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            switch.assemble({"layout":"grid", "grid":f"{{'row':{i}, 'column':0, 'padx':10, 'pady':(0, 20)}}"})
            self.scrollable_frame_switches.append(switch)

        # create checkbox and switch frame
        self.checkbox_slider_frame: FrameCtrl = FrameCtrl(self)
        # self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.checkbox_slider_frame.assemble({"layout":"grid", "grid":"{'row':1, 'column':3, 'padx':(20, 20), 'pady':(20, 0), 'sticky':'nsew'}"})
        self.checkbox_1: CheckbuttonCtrl = CheckbuttonCtrl(self.checkbox_slider_frame)
        # self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_1.assemble({"layout":"grid", "grid":"{'row':1, 'column':0, 'padx':(20, 0), 'pady':20, 'sticky':'n'}"})
        self.checkbox_2: CheckbuttonCtrl = CheckbuttonCtrl(self.checkbox_slider_frame)
        # self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_2.assemble({"layout":"grid", "grid":"{'row':2, 'column':0, 'padx':(20, 0), 'pady':20, 'sticky':'n'}"})
        self.checkbox_3: CheckbuttonCtrl = CheckbuttonCtrl(self.checkbox_slider_frame)
        # self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")
        self.checkbox_3.assemble({"layout":"grid", "grid":"{'row':3, 'column':0, 'padx':(20, 0), 'pady':20, 'sticky':'n'}"})

        # set default values
        self.sidebar_button_3.configure(state="disabled", text="Disabled Button")
        self.checkbox_3.configure(state="disabled")
        self.checkbox_1.select()
        self.scrollable_frame_switches[0].on()
        self.scrollable_frame_switches[4].on()
        self.radio_button_3.configure(state="disabled")
        # self.appearance_mode_optionemenu.set("System")
        # self.scaling_optionemenu.set("100%")
        # self.optionmenu_1.set("CTkOptionmenu")
        self.combobox_1.set_val("ComboBox")
        # self.slider_1.configure(command=self.progressbar_2.set)
        # self.slider_2.configure(command=self.progressbar_3.set)
        # self.progressbar_1.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        self.textbox.insert("0.0", "Textbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        # self.seg_button_1.configure(values=["SegmentedButton", "Value 2", "Value 3"])
        # self.seg_button_1.set("Value 2")

    def open_input_dialog_event(self):
        # dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        # print("CTkInputDialog:", dialog.get_input())
        dialog  = CalendarDialog(self)
        po(f"CalendarDialog: {dialog.get_datestr()}")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        # customtkinter.set_appearance_mode(new_appearance_mode)
        pass

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        # customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

if __name__ == "__main__":
    app = App()
    app.go()
