import tkinter as tk

from pygui_simple.tkwin.tkcontrols import (
    ButtonCtrl,
    CheckbuttonCtrl,
    ComboboxCtrl,
    EntryCtrl,
    FrameCtrl,
    LabelCtrl,
    RadiobuttonCtrl,
    ScrolledTextCtrl,
    SlideSwitchCtrl,
)
from pygui_simple.tkwin.tkwin import tkWin


def test_gui():
    gui = tkWin("", "")
    gui.title("test_win")
    gui.center_window(400, 580)

    frame_1 = FrameCtrl("frmMain", gui)
    frame_1.assemble({"layout":"pack",
                "pack":"{'pady':20, 'padx':60, 'fill':'both', 'expand':1}"})

    label_1 = LabelCtrl("lblHello", "hello", frame_1, justify="left")
    label_1.assemble({"layout":"pack",
                "pack":"{'pady':10, 'padx':10}"})

    # progressbar_1 = customtkinter.CTkProgressBar(master=frame_1)
    # progressbar_1.pack(pady=10, padx=10)

    def button1_callback():
        txt = entry_1.get_text()
        print(f"btn1 clicked: {txt}")
        label_1.set_text(txt)

    button_1 = ButtonCtrl("btn1","OK", frame_1, command=button1_callback)
    button_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})

    # slider_1 = customtkinter.CTkSlider(master=frame_1, command=slider_callback, from_=0, to=1)
    # slider_1.pack(pady=10, padx=10)
    # slider_1.set(0.5)

    entry_1 = EntryCtrl("ent1", "CTkEntry", frame_1)
    entry_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})

    # optionmenu_1 = customtkinter.CTkOptionMenu(frame_1, values=["Option 1", "Option 2", "Option 42 long long long..."])
    # optionmenu_1.pack(pady=10, padx=10)
    # optionmenu_1.set("CTkOptionMenu")

    combobox_1 = ComboboxCtrl("", frame_1, values=["Option 1", "Option 2", "Option 42 long long long..."])
    combobox_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})
    # combobox_1.set("CTkComboBox")
    _ = combobox_1.select(0)

    checkbox_1 = CheckbuttonCtrl("", "check", frame_1,)
    checkbox_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})

    radiobutton_var = tk.IntVar(value=1)

    radiobutton_1 = RadiobuttonCtrl("", "radio", frame_1, variable=radiobutton_var, value=1)
    radiobutton_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})

    radiobutton_2 = RadiobuttonCtrl("", "radio2", frame_1, variable=radiobutton_var, value=2)
    radiobutton_2.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})

    switch_1 = SlideSwitchCtrl("sld1", frame_1)
    # switch_1.pack(pady=10, padx=10)
    switch_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})

    text_1 = ScrolledTextCtrl("text_", frame_1, width=200, height=70)
    # text_1.pack(pady=10, padx=10)
    text_1.assemble({"layout":"pack", "pack":"{'pady':10, 'padx':10}"})
    text_1.insert("0.0", "CTkTextbox\n\n\n\n")

    # segmented_button_1 = customtkinter.CTkSegmentedButton(master=frame_1, values=["CTkSegmentedButton", "Value 2"])
    # segmented_button_1.pack(pady=10, padx=10)

    # tabview_1 = customtkinter.CTkTabview(master=frame_1, width=300)
    # tabview_1.pack(pady=10, padx=10)
    # tabview_1.add("CTkTabview")
    # tabview_1.add("Tab 2")

    # frame_1.assemble({"layout":"pack",
    #             "pack":"{'pady':20, 'padx':60, 'fill':'both', 'expand':1}"})

    gui.go()

if __name__ == "__main__":
    test_gui()
