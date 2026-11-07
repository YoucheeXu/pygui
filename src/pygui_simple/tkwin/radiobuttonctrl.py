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


@WidgetRegistry.register("Radiobutton")
class RadiobuttonCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text")
        assert text is not None
        if "var" in attr_dict:
            vartext = "_" + attr_dict["var"]
        else:
            vartext = "_var" + attr_dict["text"].replace(" ", "") \
                .replace(".", "_").replace("\n", "_")
        value = int(attr_dict["value"])

        ctrl = ttk.Radiobutton(master)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__("", master, idself, ctrl, tooltip)
        # self._app: GuiBasic = app
        self._owner: WinBasic = owner
        self._vartext: str = vartext
        if self._vartext not in self._owner.__dict__:
            self._owner.__dict__[self._vartext] = tk.IntVar()
        variable = cast(tk.IntVar, self._owner.__dict__[self._vartext])
        _ = ctrl.configure(text=text,
            variable=variable, value=value,
            command=lambda: owner.process_message(vartext, event="Changed", val=variable.get()),
            **options)

    def get_val(self) -> int:
        # return self.__dict__[self._vartext].get()
        return cast(tk.IntVar, self._owner.__dict__[self._vartext]).get()
