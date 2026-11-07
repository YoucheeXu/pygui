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


@WidgetRegistry.register("Toolbar")
class ToolbarCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        master = cast(tk.Misc, parent.control)
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        subctrls = list(ctrl_cfg)

        ctrl = ttk.Frame(master, **options)
        super().__init__(idself, master, "", ctrl)
        self._app_path: str = owner.path
        self._app: WinBasic = owner
        self._idctrl_list: list[str] = []
        for subctrl in subctrls:
            idctrl_list = self._app.create_controls(self, subctrl, self._level + 1)
            self._idctrl_list.extend(idctrl_list)

    @override
    def destroy(self):
        for idctrl in self._idctrl_list:
            self._app.delete_control(idctrl)
        self._idctrl_list.clear()
        super().destroy()
