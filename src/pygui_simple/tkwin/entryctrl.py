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


class EntryCtrl(tkControl):
    def __init__(self, parent: Widget, placeholder: str, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        self._var: tk.StringVar = tk.StringVar()
        tooltip = cast(str, kwargs.pop("tooltip", ""))
        if placeholder:
            self.set_text(placeholder)

        ctrl = ttk.Entry(master, textvariable=self._var, **kwargs)
        super().__init__(ctrl, tooltip)
        _= ctrl.configure()

    def get_text(self) -> str:
        return self._var.get()

    def set_text(self, val: str):
        self._var.set(val)


@WidgetRegistry.register("Entry")
class tkEntryCtrl(EntryCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):

        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text = attr_dict.get("text", "")
        tooltip = attr_dict.get("tooltip", "")

        super().__init__(parent, text, tooltip=tooltip, **options)
