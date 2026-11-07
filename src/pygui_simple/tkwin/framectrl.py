import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast, override

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


class FrameCtrl(tkControl):
    def __init__(self, idself: str, parent: Widget, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        columnconfigure = cast(str, kwargs.pop("columnconfigure", ""))

        ctrl = tk.Frame(master, **kwargs)
        tkControl.__init__(self, "", master, idself, ctrl)

        if columnconfigure:
            lst = columnconfigure.strip('()').split(',')
            colcfgs = tuple(int(x) for x in lst)
            for i, wgh in enumerate(colcfgs):
                _ = ctrl.columnconfigure(i, weight=wgh)

    @override
    def destroy(self):
        # po(f"FrameCtrl {self._idself} destroy")
        super().destroy()

# TODO: not finished
@WidgetRegistry.register("Frame")
@WidgetRegistry.register("Tab")
class tkFrameCtrl(FrameCtrl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        super().__init__(idself, parent, **options)

    @override
    def destroy(self):
        # po(f"FrameCtrl {self._idself} destroy")
        super().destroy()
