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


@WidgetRegistry.register("Button")
class ButtonCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text")
        assert text is not None

        ctrl = ttk.Button(master, text=text, **options)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(idself, master, text, ctrl, tooltip)
        self._owner: WinBasic = owner
        _ = ctrl.configure(command=self._btn_clicked, **options)

    def _btn_clicked(self):
        btn = cast(ttk.Button, self._tkctrl)
        _ = self._owner.process_message(self._idself,
            mousepos=(btn.winfo_rootx(), btn.winfo_rooty()))
