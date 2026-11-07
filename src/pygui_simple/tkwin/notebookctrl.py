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


@WidgetRegistry.register("Notebook")
class NotebookCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        subctrlcfg_list=list(ctrl_cfg)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        self.handles_child_creation = True  # pyright: ignore[reportUnannotatedClassAttribute]
        master = cast(tk.Misc, parent.control)

        ctrl = ttk.Notebook(master, **options)
        tkControl.__init__(self, "", master, idself, ctrl)
        # app.debug_print()
        self._app: WinBasic = owner
        self._idself: str = idself
        self._idctrl_list: list[str] = []
        for subctrl_cfg in list(subctrlcfg_list):
            id_, sub_ctrl = self._app.create_control(self,
                subctrl_cfg, self.level + 1)
            self._idctrl_list.append(id_)
            # app.debug_print(f"tabCtrl: {subctrl_cfg.tag}")
            subctrl = cast(tk.Widget, sub_ctrl.control)
            ctrl.add(subctrl, text=subctrl_cfg.attrib["text"])
            for item in list(subctrl_cfg):
                idctrl_list = self._app.create_controls(sub_ctrl, item,
                    self.level + 2, owner)
                self._idctrl_list.extend(idctrl_list)

    @override
    def destroy(self):
        # po(f"NotebookCtrl {self._idself} destroy")
        for idctrl in self._idctrl_list:
            self._app.delete_control(idctrl)
        self._idctrl_list.clear()
        super().destroy()
