# !/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import ctypes
import platform
import sys
import tkinter as tk
import tkinter.messagebox as tkMessageBox
from functools import partial
from typing import cast, override

from pygui_simple.tkwin.tkwm import tkWM
from pygui_simple.winbasic import Window

IS_WINDOWS = platform.system() == "Windows" # sys.platform.startswith("win")

class tkWin(Window):
    def __init__(self, cur_path: str, xmlfile: str):
        super().__init__(cur_path, xmlfile)

        # Windows提前启用DPI感知
        if IS_WINDOWS:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)

        # self._win: tk.Tk = tk.Tk()
        self._root: tkWM[tk.Tk] = tkWM[tk.Tk](tk.Tk())
        self._win: tk.Tk = cast(tk.Tk, self._root.control)
        self.control = self._win  # pyright: ignore[reportUnannotatedClassAttribute]

        """
        if IS_WINDOWS:
            try:  # >= win 8.1
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except:  # win 8.0 or less
                ctypes.windll.user32.SetProcessDPIAware()
            # ctypes.windll.shcore.SetProcessDpiAwareness(1)
            scale_fact = cast(float, ctypes.windll.shcore.GetScaleFactorForDevice(0))
            pv(scale_fact)
            self._win.tk.call("tk", "scaling", scale_fact / 90)
        """
        self._scale_factor: float = self._get_scale_factor()
        self._win.tk.call("tk", "scaling", self._scale_factor)

        exit_window = partial(self.exit)
        self._win.protocol("WM_DELETE_WINDOW", exit_window)
        # 注册（绑定）窗口变动事件
        _ = self._win.bind('<Configure>', self._on_winresize)
        _ = self._win.bind_all("<KeyPress>", self._on_keypress)
        # _ = self._win.bind_all("<MouseWheel>", self._on_mousewheel)
        # self._win.bind("<Motion>", self._motion)
        # self._win.bind("<Button-1>", self._mouseclicked)
        # self._win.columnconfigure(0, weight=1)
        # self._win.rowconfigure(0, weight=1)

        # self._mousex: int = 0
        # self._mousey: int = 0

        if xmlfile:
            self.title(self._title)
            self.create_window()

    def _get_scale_factor(self):
        """ 获取系统缩放比例(默认1.0)"""
        if IS_WINDOWS:
            # Windows：通过系统API获取缩放比例
            user32 = ctypes.windll.user32
            dpi = cast(float, user32.GetDpiForWindow(user32.GetForegroundWindow()))
            return dpi / 96.0  # 96 DPI为默认缩放（100%）
        elif sys.platform == "darwin":
            # macOS：通过Tk内置方法获取
            return cast(float, self._win.tk.call("tk", "scaling"))
        else:
            # Linux：假设使用1.0或通过xdpyinfo获取（简化处理）
            return 1.0

    @property
    @override
    def win(self):
        return self._win

    @override
    def title(self, val: str):
        super().title(val)
        self._win.title(self._title)

    @override
    def create_window(self):
        if self._ww and self._hh:
            self.center_window(self._ww, self._hh)

        for frm in list(self._wincfg):
            # _ = self.create_controls(self._win, frm)
            _ = self.create_controls(self._root, frm)

    @override
    def movie_window(self, x: int, y: int, w: int, h: int):
        _ = self._win.geometry(f"{w}x{h}+{x}+{y}")
        return super().movie_window(x, y, w, h)

    @override
    def center_window(self, width: int, height: int):
        """ 设置窗口居中和宽高

        Args:
            width (int): 窗口宽度
            hight (int): 窗口高度

        Returns:
            None
        """
        # 获取屏幕宽度和高度
        sw = self._win.winfo_screenwidth()
        sh = self._win.winfo_screenheight()

        # 计算中心坐标
        cen_x = int((sw - width) / 2)
        cen_y = int((sh - height) / 2)

        # 设置窗口大小并居中
        self.movie_window(cen_x, cen_y, width, height)

    def show_info(self, title: str = "", message: str = ""):
        _ = tkMessageBox.showinfo(title, message)

    def show_warn(self, title: str = "", message: str = ""):
        _ = tkMessageBox.showwarning(title, message)

    @override
    def show_err(self, title: str = "", message: str = ""):
        _ = tkMessageBox.showerror(title, message)

    def ask_yesno(self, title: str = "", message: str = ""):
        return tkMessageBox.askyesno(title, message)

    @override
    def go(self):
        self.register_eventhandler("Exit", self.exit)
        self.register_eventhandler("Quit", self.exit)

        super().back(False)

        # self._x = self._win.winfo_rootx()
        # self._y = self._win.winfo_rooty()

        self._win.focus_force()
        # self._win.focus_set()

        self._win.mainloop()

    def _on_winresize(self, event: tk.Event[tk.Misc] | None):
        """ listen events of window resizing.
        """
        if event is not None:
            if self._ww != self._win.winfo_width() or self._hh != self._win.winfo_height():
                if self._ww != self._win.winfo_width():
                    self._ww = self._win.winfo_width()
                if self._hh != self._win.winfo_height():
                    self._hh = self._win.winfo_height()
                _ = self.process_message("WindowResize", w=self._ww, h=self._hh)

    def _on_keypress(self, event: tk.Event[tk.Misc]):
        """
            event.state
            0x0001 	Shift.          0x0004 	Control.
            0x0002 	Caps Lock.      0x0010 	Num Lock.
            0x0008 	Left-hand Alt.  0x0080 	Right-hand Alt.
            0x0100 	Mouse button 1. 0x0200 	Mouse button 2.
            0x0400 	Mouse button 3
        """
        state= cast(int, event.state)
        # pv(state)
        ctrl = (state & 0x0004) >> 2
        shift = state & 0x0001
        # alt = state & 0x0008 | state & 0x0080
        _ = self.process_message("KeyPress", key=event.keysym, ctrl=ctrl, shift=shift)

    def exit(self, **_: object):
        res = tkMessageBox.askquestion(
            "Exit Application", "Do you really want to exit?"
        )
        if res == "yes":
            super().destroy()
            self._win.destroy()
