import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast, override

from pygui_simple.tkwin.radiobuttonctrl import RadiobuttonCtrl
from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("RadioButtonGroup")
class RadioButtonGroupCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text")
        assert text is not None

        ctrl = ttk.LabelFrame(master)
        super().__init__(idself, master, text, ctrl)
        # self._idself: str = idself
        # self._var_val: tk.IntVar = tk.IntVar()
        self._vartext: str = "_var" + text.replace(" ", "_")
        self._app: WinBasic = owner
        self._owner: WinBasic = owner
        # pv(options)
        _ = self.configure(text=text, **options)
        # self._radbutton_lst: list[ttk.Radiobutton] = []
        self._radbutton_lst: list[RadiobuttonCtrl] = []
        _ = self._create_subctrls(ctrl_cfg)

    def get_val(self) -> int:
        # return self._var_val.get()
        return cast(tk.IntVar, self._app.__dict__[self._vartext]).get()

    def set_val(self, val: int):
        # self._var_val.set(val)
        cast(tk.IntVar, self._app.__dict__[self._vartext]).set(val)

    def _create_subctrls(self, subctrls: et.Element):
        for subctrl_cfg in subctrls:
            radbtn_attr_dict = subctrl_cfg.attrib
            value = int(radbtn_attr_dict["value"])
            text: str = radbtn_attr_dict["text"]
            sub_ctrl = self._add_radiobutton(value, text)
            # self._app.debug_print(f"{'  '*(level + 1)}Control: Radiobutton, text: {text}", end="")
            self._app.assemble_control(sub_ctrl, radbtn_attr_dict)

    def _add_radiobutton(self, val: int, txt: str, **opt_dict: object):
        ctrl_cfg = self._app.create_xml("Radiobutton", {"text": f"{txt}",
            "vartext": self._vartext,
            "value": f"{val}"})
        radbutton = RadiobuttonCtrl("", ctrl_cfg, self, self._owner)
        radbutton.level = self.level+1
        radbutton.configure(**opt_dict)
        self._radbutton_lst.append(radbutton)
        return radbutton

    @override
    def destroy(self):
        # po(f"RadiobuttonGroupCtrl {self._idself} destroy")
        for radbutton in self._radbutton_lst:
            # self._debug_print(f"going to del {id_ctrl}")
            radbutton.destroy()
        self._radbutton_lst.clear()
        super().destroy()
