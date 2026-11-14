import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("Spinbox")
class SpinboxCtrl(tkControl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        master = cast(tk.Misc, parent.control)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        if "id" in attr_dict:
            idctrl: str = attr_dict["id"]
        elif text := attr_dict.get("text", ""):
            idctrl = text.replace(" ", "").replace(".", "_").replace("\n", "_")
        else:
            raise RuntimeError("No id")

        ctrl = tk.Spinbox(master,
            command=lambda: owner.process_message(idctrl, event="Changed"),
            **options)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(ctrl, tooltip)

    def get(self):
        return cast(tk.Spinbox, self._control).get()
