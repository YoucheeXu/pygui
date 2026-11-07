import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast, override

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


# TODO: not finished
@WidgetRegistry.register("LabelFrame")
class LabelFrameCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text")
        assert text is not None

        ctrl = ttk.LabelFrame(master, text=text, **options)
        tkControl.__init__(self, idself, master, text, ctrl)

    @override
    def destroy(self):
        # po(f"LabelFrameCtrl {self._idself} destroy")
        super().destroy()
