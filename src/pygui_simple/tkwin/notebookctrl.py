import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast, override

from pygui_simple.tkwin.framectrl import FrameCtrl
from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


class NotebookCtrl(tkControl):
    def __init__(self, parent: Widget, **kwargs: Any):
        master = cast(tk.Misc, parent.control)

        self._ctrl: ttk.Notebook = ttk.Notebook(master, **kwargs)
        super().__init__(self._ctrl)

        self._tab_dict: dict[str, FrameCtrl] = {}

    def add(self, name: str, **kwargs: Any):
        child = FrameCtrl(self)
        self._tab_dict[name] = child
        childctrl = cast(tk.Widget, child.control)
        cast(ttk.Notebook, self.control).add(childctrl, text=name, **kwargs)

    def tab(self, name: str):
        return self._tab_dict[name]

    @override
    def destroy(self):
        for tab in self._tab_dict.values():
            tab.destroy()
        return super().destroy()

@WidgetRegistry.register("Notebook")
class tkNotebookCtrl(NotebookCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        subctrlcfg_list=list(ctrl_cfg)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        self.handles_child_creation = True  # pyright: ignore[reportUnannotatedClassAttribute]

        super().__init__(parent, **options)
        # app.debug_print()
        self._app: WinBasic = owner
        self._idctrl_list: list[str] = []
        for subctrl_cfg in list(subctrlcfg_list):
            id_, sub_ctrl = self._app.create_control(self,
                subctrl_cfg, self.level + 1)
            self._idctrl_list.append(id_)
            # app.debug_print(f"tabCtrl: {subctrl_cfg.tag}")
            subctrl = cast(tk.Widget, sub_ctrl.control)
            cast(ttk.Notebook, self.control).add(subctrl, text=subctrl_cfg.attrib["text"])
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
