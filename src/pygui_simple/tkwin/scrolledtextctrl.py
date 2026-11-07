import tkinter as tk
import xml.etree.ElementTree as et
from _tkinter import Tcl_Obj
from tkinter import scrolledtext
from typing import cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("ScrolledText")
class ScrolledTextCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        master = cast(tk.Misc, parent.control)
        options: dict[str, object] = {}
        if "options" in attr_dict:
            options = cast(dict[str, object], eval(attr_dict["options"]))

        ctrl = scrolledtext.ScrolledText(master, **options)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(idself, master, "", ctrl, tooltip)

    def insert(self, index: str| float | Tcl_Obj | tk.Widget, chars: str, *args: str | list[str] | tuple[str,...]):
        cast(scrolledtext.ScrolledText, self._control).insert(index, chars, *args)
