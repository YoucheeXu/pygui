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


class ComboboxCtrl(tkControl):
    def __init__(self, idself: str, parent: Widget, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        default = cast(int, kwargs.pop("default", "0"))
        tooltip = cast(str, kwargs.pop("tooltip", ""))
        self._var: tk.StringVar = tk.StringVar()

        ctrl = ttk.Combobox(master, textvariable=self._var, **kwargs)
        _ = ctrl.current(default)
        super().__init__(idself, master, "", ctrl, tooltip)

    def get_val(self) -> str:
        return self._var.get()

    def set_val(self, val: str):
        self._var.set(val)

    def select(self, idx: int):
        ctrl = cast(ttk.Combobox, self._tkctrl)
        return ctrl.current(idx)


@WidgetRegistry.register("Combobox")
class tkComboboxCtrl(ComboboxCtrl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        super().__init__(idself, parent, **options)
        _ = cast(tk.Misc, self.control).bind(
            "<<ComboboxSelected>>",
            lambda event: owner.process_message(
                idself, event="Selected", val=self._var.get()
            ),
        )
