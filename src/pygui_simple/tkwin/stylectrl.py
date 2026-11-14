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
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        master = cast(tk.Misc, parent.control)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, object] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text = attr_dict.get("text")

        assert text is not None
        ctrl = ttk.Style(master)
        _ = ctrl.configure(text, **options)
        super().__init__(ctrl)
