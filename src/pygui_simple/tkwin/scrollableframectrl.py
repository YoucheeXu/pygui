from __future__ import annotations

import platform
import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast, override
from weakref import WeakSet

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


class ScrollableFrameCtrl(tkControl):
    """ 智能滚动容器
    """
    def __init__(self, parent: Widget, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        width = cast(int, kwargs.get("width", 0))
        height = cast(int, kwargs.get("height", 0))

        self._outter_frame: tk.Frame = tk.Frame(master, **kwargs)

        self._scroll_bound: WeakSet[tk.Widget | tk.Toplevel] = WeakSet()

        # 配置网格布局权重，确保框架能扩展
        _ = self._outter_frame.grid_rowconfigure(0, weight=1)
        _ = self._outter_frame.grid_columnconfigure(0, weight=1)

        self._os_type: str = platform.system()
        self._update_after_id: str | None = None

        # 创建画布
        self._canvas: tk.Canvas = tk.Canvas(self._outter_frame, width=width, height=height,
            highlightthickness=0, highlightbackground="#ccc", takefocus=True)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        # 垂直滚动条
        self._vscrollbar: ttk.Scrollbar = ttk.Scrollbar(self._outter_frame, orient="vertical",
            command=self._canvas.yview)
        self._vscrollbar.grid(row=0, column=1, sticky="ns")
        self._vscrollbar.grid_remove()  # 默认隐藏
        _ = self._canvas.configure(yscrollcommand=self._vscrollbar.set)

        # 水平滚动条
        self._hscrollbar: ttk.Scrollbar = ttk.Scrollbar(self._outter_frame, orient="horizontal",
            command=self._canvas.xview)
        _ = self._hscrollbar.grid(row=1, column=0, sticky="ew")
        self._hscrollbar.grid_remove()  # 默认隐藏
        _ = self._canvas.configure(xscrollcommand=self._hscrollbar.set)

        # Create a frame inside the canvas which will be scrolled with it
        self._inner_frame: tk.Frame = tk.Frame(self._canvas)
        super().__init__(self._inner_frame)

        # self._outter_frame.bindtags((self._outter_frame, self._canvas, "Frame", "all"))
        # 调整bindtags，确保事件先传给自身，再传给画布
        # self._inner_frame.bindtags((self._inner_frame, self._canvas, "Frame", "all"))

        self._interior_id: int = self._canvas.create_window((0, 0),
            window=self._inner_frame, anchor="nw")

        # 绑定事件处理
        _ = self._inner_frame.bind('<Configure>', self._on_configure_inner)
        _ = self._canvas.bind('<Configure>', self._on_configure_canvas)
        _ = self._inner_frame.bind("<Map>", self._on_map_inner)

        # 鼠标滚轮支持
        self._bind_scroll_events(self._canvas)
        self._bind_scroll_events(self._inner_frame)
        # self._bind_scroll_events(self._outter_frame)

        # 初始更新
        self._outter_frame.update_idletasks()
        self._on_configure_inner(None)

    def _bind_scroll_events(self, widget: tk.Widget):
        """ 为单个控件绑定所有必要的滚动事件"""
        if self._os_type == "Linux":
            vevents = ["<Button-4>",            # 上滚
                "<Button-5>"]                   # 下滚
            hevents = ["<Shift-Button-4>",      # 左滚
                "<Shift-Button-5>"]             # 右滚
        else:
            vevents = ["<MouseWheel>"]          # 垂直滚动
            hevents = ["<Shift-MouseWheel>"]    # 水平滚动
            if self._os_type == "Darwin":
                hevents.append("<Command-MouseWheel>")

        # 为控件绑定滚动事件处理函数
        for event in vevents:
            _ = widget.bind(event, self._on_vmousewheel)
        for event in hevents:
            _ = widget.bind(event, self._on_hmousewheel)

    def update_layout(self) -> None:
        """ 公共方法：更新布局和滚动区域"""
        self._on_configure_inner(None)

    def _on_map_inner(self, event: tk.Event[tk.Frame]) -> None:
        """ 当内部控件被映射时强制更新布局"""
        self._outter_frame.update_idletasks()
        self._on_configure_inner(event)

    def _on_configure_inner(self, event: tk.Event[tk.Frame] | None):
        """ 内容变化时更新滚动区域"""

        self._outter_frame.update_idletasks()

        # Update the scrollbars to match the size of the inner frame
        width = self._inner_frame.winfo_reqwidth()
        height = self._inner_frame.winfo_reqheight()
        _ = self._canvas.config(scrollregion=(0, 0, width, height))

        # if self._inner_frame.winfo_reqwidth() != self._canvas.winfo_width():
            # Update the canvas's width to fit the inner frame
            # _ = self._canvas.config(width=self._inner_frame.winfo_reqwidth())

        # 垂直滚动条显示逻辑
        canvas_height = self._canvas.winfo_height()
        if height > canvas_height + 5:
            _ = self._vscrollbar.grid()
        else:
            self._vscrollbar.grid_remove()

        # 水平滚动条显示逻辑
        canvas_width = self._canvas.winfo_width()
        if width > canvas_width + 5:
            _ = self._hscrollbar.grid()
        else:
            self._hscrollbar.grid_remove()

        # 为所有子控件绑定滚动事件
        for widget in self._inner_frame.winfo_children():
            if widget not in self._scroll_bound:
                self._bind_scroll_events(cast(tk.Widget, widget))
                self._scroll_bound.add(widget)

    def _on_configure_canvas(self, event: tk.Event[tk.Canvas]):
        """ 画布大小变化时调整"""
        if self._inner_frame.winfo_reqwidth() != self._canvas.winfo_width():
            # Update the inner frame's width to fill the canvas
            _ = self._canvas.itemconfigure(self._interior_id, width=self._canvas.winfo_width())
            # _ = self._canvas.itemconfig(self._interior_id, width=event.width)
        if self._update_after_id is not None:
            self._outter_frame.after_cancel(self._update_after_id)

        self._update_after_id = self._outter_frame.after(30, self._on_configure_inner, None)

    def _on_vmousewheel(self, event: tk.Event[tk.Misc]):
        """ 垂直滚动处理"""
        if not self._vscrollbar.winfo_viewable():
            return None
        # po("_on_vmousewheel")
        # if not self._vscrollbar.winfo_ismapped():
            # return "break"
        # delta = event.delta
        # pv(delta)
        # scroll_units = -1 if delta > 0 else 1
        delta = event.delta if hasattr(event, 'delta') else -1 if event.num == 4 else 1
        scroll_units = -int(delta / 120)
        self._canvas.focus_set()
        self._canvas.yview_scroll(scroll_units, "units")
        # 阻止事件传播到其他组件
        return "break"

    def _on_hmousewheel(self, event: tk.Event[tk.Misc]):
        """ 水平滚动处理"""
        if not self._hscrollbar.winfo_viewable():
            return None
        # po("_on_hmousewheel")
        # self.update_layout()

        # if not self._hscrollbar.winfo_ismapped():
            # return "break"

        _ = event.widget.focus_set()

        delta = event.delta if hasattr(event, 'delta') else -1 if event.num == 4 else 1
        scroll_units = -int(delta / 120)
        _ = self._canvas.xview_scroll(scroll_units, "units")
        # 阻止事件传播到其他组件
        return "break"

    @override
    def assemble(self, attr_dict: dict[str, str], prefix: str = ""):
        ctrl = self._control
        self._control = self._outter_frame  # pyright: ignore[reportUnannotatedClassAttribute]
        super().assemble(attr_dict, prefix)
        self._control = ctrl

    @override
    def destroy(self):
        # po(f"ScrollableFrame {self._idself} destroy")
        self._inner_frame.destroy()
        self._vscrollbar.destroy()
        self._hscrollbar.destroy()
        self._canvas.destroy()
        super().destroy()


@WidgetRegistry.register("ScrollableFrame")
class tkScrollableFrameCtrl(ScrollableFrameCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        super().__init__(parent, **options)
