import tkinter as tk
import xml.etree.ElementTree as et
from idlelib.statusbar import MultiStatusBar
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("StatusBar")
class StatusBarCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        master = cast(tk.Misc, parent.control)
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        ctrl = MultiStatusBar(master, **options)
        super().__init__(idself, master, "", ctrl)

    def set_label(self, name: str, text: str = '', side: str = 'left', width: int = 0):
        cast(MultiStatusBar, self.control).set_label(name, text, side, width)
