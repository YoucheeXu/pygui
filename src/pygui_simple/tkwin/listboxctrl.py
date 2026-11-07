import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("Listbox")
class ListboxCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)

        ctrl = tk.Listbox(master, **options)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(idself, master, "", ctrl, tooltip)

    def insert(self, index: str | int, *elements: str | float):
        ctrl = cast(tk.Listbox, self._tkctrl)
        ctrl.insert(index, *elements)
        # self.scroll_to_bottom_if_needed()

    def scroll_to_bottom_if_needed(self):
        ctrl  = cast(tk.Listbox, self._tkctrl)
        # 获取滚动条位置
        scrollbar_position = ctrl.yview()[1]
        # 检查滚动条是否在最底部
        if scrollbar_position != 1.0:
            # 在最底部时，执行自动滚动
            ctrl.see(tk.END)
