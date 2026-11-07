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


@WidgetRegistry.register("Combobox")
class ComboboxCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        default = int(attr_dict.get("default", "0"))

        ctrl = ttk.Combobox(master)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__("", master, idself, ctrl, tooltip)
        self._var: tk.StringVar = tk.StringVar()
        _ = ctrl.configure(textvariable=self._var, **options)
        _ = ctrl.current(default)
        _ = ctrl.bind(
            "<<ComboboxSelected>>",
            lambda event: owner.process_message(
                idself, event="Selected", val=self._var.get()
            ),
        )

    def get_val(self) -> str:
        return self._var.get()

    def set_val(self, val: str):
        self._var.set(val)

    def select(self, idx: int):
        ctrl = cast(ttk.Combobox, self._tkctrl)
        return ctrl.current(idx)
