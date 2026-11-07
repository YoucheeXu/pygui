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


class RadiobuttonCtrl(tkControl):
    def __init__(self, idself: str, text: str, parent: Widget, variable: tk.IntVar, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        self._variable: tk.IntVar = variable
        tooltip = cast(str, kwargs.pop("tooltip", ""))

        ctrl = ttk.Radiobutton(master, text=text, variable=variable, **kwargs)
        super().__init__(idself, master, text, ctrl, tooltip)

    def get_val(self) -> int:
        # return self.__dict__[self._vartext].get()
        return self._variable.get()


@WidgetRegistry.register("Radiobutton")
class tkRadiobuttonCtrl(RadiobuttonCtrl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text = attr_dict.get("text")
        assert text is not None
        if "var" in attr_dict:
            vartext = "_" + attr_dict["var"]
        else:
            vartext = "_var" + attr_dict["text"].replace(" ", "") \
                .replace(".", "_").replace("\n", "_")
        value = int(attr_dict["value"])

        if vartext not in owner.__dict__:
            owner.__dict__[vartext] = tk.IntVar()

        super().__init__(idself, text, parent, owner.__dict__[vartext], **options)

        variable = cast(tk.IntVar, owner.__dict__[vartext])
        _ = cast(ttk.Radiobutton, super().control).configure(
			value=value,
            command=lambda: owner.process_message(vartext, event="Changed", val=variable.get()))
