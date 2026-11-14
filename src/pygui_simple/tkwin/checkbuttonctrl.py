import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


class CheckbuttonCtrl(tkControl):
    def __init__(self, parent: Widget, text: str = "Checkbutton", **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        tooltip = cast(str, kwargs.pop("tooltip", ""))
        vartext = cast(str, kwargs.pop("var", ""))
        if not vartext:
            vartext = text.replace(" ", "").replace(".", "_").replace("\n", "_")
        select = cast(bool, kwargs.pop("select", False))
        self._vartext: str = "_" + vartext
        var = tk.IntVar(value=0)
        setattr(self, self._vartext, var)
        self._variable: tk.IntVar = var

        self._ctrl: tk.Checkbutton = tk.Checkbutton(master, text=text,
            variable=self._variable, **kwargs)
        super().__init__(self._ctrl, tooltip)

        if select:
            self._ctrl.select()

    @property
    def vartext(self):
        return self._vartext

    @property
    def variable(self):
        return self._variable

    def select(self):
        self._ctrl.select()

    def get_val(self) -> int:
        return self._variable.get()

@WidgetRegistry.register("Checkbutton")
class tkCheckbuttonCtrl(CheckbuttonCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text = attr_dict.get("text")
        assert text is not None

        super().__init__(parent, text=text, **options)

        _ = super().variable.trace_add("write",
            lambda u0, u1, u2: owner.process_message(self.vartext, event="Changed",
                val=self.get_val()))
