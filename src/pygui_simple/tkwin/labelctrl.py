import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("Label")
class LabelCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        clickable = "clickable" in attr_dict
        master = cast(tk.Misc, parent.control)
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text: str | None = attr_dict.get("text")
        assert text is not None

        ctrl = ttk.Label(master, text=text, **options)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(idself, master, text, ctrl, tooltip)
        if clickable:
            _= ctrl.bind("<Button-1>",
                lambda e: owner.process_message(idself,
                    mousepos=e.widget.winfo_pointerxy()))

    def get_text(self):
        lblctrl = cast(ttk.Label, self._tkctrl)
        return cast(str, lblctrl["text"])

    def set_text(self, val: str):
        lblctrl = cast(ttk.Label, self._tkctrl)
        lblctrl["text"] = val
