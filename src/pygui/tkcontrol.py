# !/usr/bin/python3
# -*- coding: UTF-8 -*-
from typing import cast
from typing import Any, override
import tkinter as tk

from pygui.winbasic import Control


class tkControl(Control):
    def __init__(self, parent: tk.Misc, title: str, idself: str, tkctrl: tk.Widget):
        super().__init__(title, idself)
        self._parent: tk.Misc = parent
        self._tkctrl: tk.Widget = tkctrl
        self._assemble_type: str = ""
        self._layout_info: tk._PackInfo | tk._PlaceInfo | None = None
        # self._hidden: bool = True

    @property
    def control(self):
        return self._tkctrl

    @property
    def visible(self):
        return self._tkctrl.winfo_viewable()

    @override
    def configure(self, **kwargs: Any):
        self._tkctrl.configure(**kwargs)

    @override
    def __getitem__(self, item: str):
        # return getattr(self._tkctrl, item)
        return self._tkctrl[item]

    @override
    def __setitem__(self, item: str, value):
        self._tkctrl.__setitem__(item, value)

    @override
    def disable(self, is_disbl: bool = True):
        if is_disbl:
            self._tkctrl.configure(state="disabled")
        else:
            self._tkctrl.configure(state="normal")

    def _get_layout_method(self, widget: tk.Widget):
        """判断控件使用的布局方式（pack/grid/place）"""
        # 检查是否使用了 place
        try:
            if widget.tk.call("place", "info", widget):
                return "place"
        except tk.TclError as _:
            # print(f"{self._idself}._get_layout_method.place: {e}")
            pass
        try:
            # 检查是否使用了 pack
            if widget.tk.call("pack", "info", widget):
                return "pack"
        except tk.TclError as _:
            # print(f"{self._idself}._get_layout_method.pack: {e}")
            pass
        try:
            # 检查是否使用了 grid
            if widget.tk.call("grid", "info", widget):
                return "grid"
        except tk.TclError as _:
            # print(f"{self._idself}._get_layout_method.grid: {e}")
            pass

        raise ValueError("未使用任何布局管理器")

    @override
    def hide(self, is_hide: bool = True):
        if not self._assemble_type:
            self._assemble_type = self._get_layout_method(self._tkctrl)
        match self._assemble_type:
            case "grid":
                if is_hide:
                    self._tkctrl.grid_remove()
                else:
                    self._tkctrl.grid()
            case "pack":
                if is_hide:
                    # if not self._hidden:
                    try:
                        self._layout_info = self._tkctrl.pack_info()
                        self._tkctrl.pack_forget()
                    except Exception as _:
                        # print(f"{self._idself}.hide.pack: {e}")
                        pass
                else:
                    # if self._hidden:
                    assert self._layout_info is not None
                    self._tkctrl.pack(**self._layout_info)
            case "place":
                if is_hide:
                    try:
                        self._layout_info = self._tkctrl.place_info()
                        self._tkctrl.place_forget()
                    except Exception as _:
                        # print(f"{self._idself}.hide.place: {e}")
                        pass
                else:
                    assert self._layout_info is not None
                    self._tkctrl.place(**self._layout_info)
            case _:
                raise ValueError(f"unkown layout: {self._assemble_type}")
        # self._hidden = is_hide

    @override
    def destroy(self):
        self._tkctrl.destroy()
