import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("Checkbutton")
class CheckbuttonCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text")
        assert text is not None
        if "var" in attr_dict:
            vartext = attr_dict["var"]
        else:
            vartext = attr_dict["text"].replace(" ", "").replace(".", "_").replace("\n", "_")
        select = "select" in attr_dict

        ctrl = tk.Checkbutton(master)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__("", master, idself, ctrl, tooltip)
        self._vartext: str = "_" + vartext
        self.__dict__[self._vartext] = tk.IntVar()
        variable = cast(tk.IntVar, self.__dict__[self._vartext])
        _ = ctrl.configure(text=text,
            variable=variable, **options)
        _ = variable.trace_add("write",
            lambda u0, u1, u2: owner.process_message(vartext, event="Changed",
                val=variable.get()))

        if select:
            ctrl.select()

    def get_val(self) -> int:
        return cast(tk.IntVar, self.__dict__[self._vartext]).get()
