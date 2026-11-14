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
    def __init__(self, parent: Widget, text: str, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        tooltip = cast(str, kwargs.pop("tooltip", ""))

        ctrl = ttk.Label(master, text=text, **kwargs)
        super().__init__(ctrl, tooltip)

    def get_text(self):
        lblctrl = cast(ttk.Label, self._tkctrl)
        return cast(str, lblctrl["text"])

    def set_text(self, val: str):
        lblctrl = cast(ttk.Label, self._tkctrl)
        lblctrl["text"] = val

@WidgetRegistry.register("Label")
class tkLabelCtrl(LabelCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        clickable = "clickable" in attr_dict
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text: str | None = attr_dict.get("text")
        assert text is not None

        super().__init__(parent, text, **options)

        if "id" in attr_dict:
            self._idctrl: str = attr_dict["id"]
        elif text:
            self._idctrl = text.replace(" ", "").replace(".", "_").replace("\n", "_")
        else:
            raise RuntimeError("No id")

        if clickable:
            _= cast(tk.Misc, self.control).bind("<Button-1>",
                lambda e: owner.process_message(self._idctrl,
                    mousepos=e.widget.winfo_pointerxy()))
