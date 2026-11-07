import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("Style")
class StyleCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, object] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text")

        assert text is not None
        ctrl = ttk.Style()
        _ = ctrl.configure(text, **options)
        super().__init__(idself, master, text, ctrl)
