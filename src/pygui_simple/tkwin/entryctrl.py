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


@WidgetRegistry.register("Entry")
class EntryCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):

        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)

        ctrl = ttk.Entry(master)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__("", master, idself, ctrl, tooltip)
        self._var: tk.StringVar = tk.StringVar()
        _= ctrl.configure(textvariable=self._var, **options)
        text = attr_dict.get("text")
        if text is not None:
            self.set_text(text)

    def get_text(self) -> str:
        return self._var.get()

    def set_text(self, val: str):
        self._var.set(val)
