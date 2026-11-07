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


class ButtonCtrl(tkControl):
    def __init__(self, idself: str, text: str, parent: Widget, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        tooltip = cast(str, kwargs.pop("tooltip", ""))

        ctrl = ttk.Button(master, text=text, **kwargs)
        super().__init__(idself, master, text, ctrl, tooltip)

@WidgetRegistry.register("Button")
class tkButtonCtrl(ButtonCtrl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text = attr_dict.get("text")
        assert text is not None

        tooltip = attr_dict.get("tooltip", "")
        super().__init__(idself, text, parent, tooltip=tooltip)
        self._owner: WinBasic = owner
        _ = super().configure(command=self._btn_clicked, **options)

    def _btn_clicked(self):
        btn = cast(ttk.Button, self._tkctrl)
        _ = self._owner.process_message(self._idself,
            mousepos=(btn.winfo_rootx(), btn.winfo_rooty()))
