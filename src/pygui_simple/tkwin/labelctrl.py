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


class LabelCtrl(tkControl):
    def __init__(self, idself: str, text: str, parent: Widget, **kwargs: Any):
        tooltip = cast(str, kwargs.pop("tooltip", ""))
        master = cast(tk.Misc, parent.control)

        ctrl = ttk.Label(master, text=text, **kwargs)
        super().__init__(idself, master, text, ctrl, tooltip)

    def get_text(self):
        lblctrl = cast(ttk.Label, self._tkctrl)
        return cast(str, lblctrl["text"])

    def set_text(self, val: str):
        lblctrl = cast(ttk.Label, self._tkctrl)
        lblctrl["text"] = val

@WidgetRegistry.register("Label")
class tkLabelCtrl(LabelCtrl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        clickable = "clickable" in attr_dict
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text: str | None = attr_dict.get("text")
        assert text is not None

        super().__init__(idself, text, parent, **options)
        if clickable:
            _= cast(tk.Misc, self.control).bind("<Button-1>",
                lambda e: owner.process_message(idself,
                    mousepos=e.widget.winfo_pointerxy()))
