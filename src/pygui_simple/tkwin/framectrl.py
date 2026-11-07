import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast, override

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


# TODO: not finished
@WidgetRegistry.register("Frame")
@WidgetRegistry.register("Tab")
class FrameCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        if columnconfigure := options.get("columnconfigure"):
            del options["columnconfigure"]

        ctrl = tk.Frame(master, **options)
        tkControl.__init__(self, "", master, idself, ctrl)

        if columnconfigure:
            lst = cast(str, columnconfigure).strip('()').split(',')
            colcfgs = tuple(int(x) for x in lst)
            for i, wgh in enumerate(colcfgs):
                _ = ctrl.columnconfigure(i, weight=wgh)

    @override
    def destroy(self):
        # po(f"FrameCtrl {self._idself} destroy")
        super().destroy()
