# !/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import ctypes
import platform
import sys
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import xml.etree.ElementTree as et
from functools import partial
from typing import TypeVar, cast, override

from pygui_simple.winbasic import (
    Container,
    Dialog,
    EventHanlder,
    Widget,
    WidgetRegistry,
    WinBasic,
    Window,
)

IS_WINDOWS = platform.system() == "Windows" # sys.platform.startswith("win")

T = TypeVar("T", bound=tk.Tk | tk.Toplevel)
class tkWM[T](Widget):
    def __init__(self, wm: T):
        super().__init__("")
        self._tkwm: T = wm
        self.control = self._tkwm  # pyright: ignore[reportUnannotatedClassAttribute]

# TODO: auto scrollable or not
@WidgetRegistry.register("Dialog")
class DialogCtrl(Dialog):
    def __init__(self, idself: str, dlg_cfg: et.Element, parent: Widget, owner: WinBasic):
        app = owner

        attr_dict = dlg_cfg.attrib
        super().__init__(attr_dict.get("text", ""), int(attr_dict["Width"]), int(attr_dict["Height"]), app)

        self._parent: tk.Tk | tk.Toplevel = cast(tk.Tk, app.control)

        self._top: tkWM[tk.Toplevel] | None = None
        self._alive: bool = False
        self._idself: str = attr_dict["id"]
        self._subctrlcfg_list: list[et.Element] = list(dlg_cfg)
        self._idctrl_list: list[str] = []
        self._extral_msg: dict[str, object] = {}

        self._title: str
        self._xx: int
        self._yy: int

    def set_title(self, val: str):
        self._title = val
        if self._top is not None:
            topctrl = cast(tk.Toplevel, self._top.control)
            topctrl.title(self._title)

    @property
    def alive(self):
        return self._alive

    def do_show(self, owner: Container | None = None, x: int = 0, y: int = 0, **kwargs: object):
        # po(f"show Dialog {self._idself}: {kwargs}")
        # self.deiconify()
        self._alive = True
        if owner is not None:
            self._owner = owner  # pyright: ignore[reportUnannotatedClassAttribute]

        self._top = tkWM[tk.Toplevel](tk.Toplevel(self._parent))
        topctrl = cast(tk.Toplevel, self._top.control)

        # x, y, _, _ = self._app.get_winsize()
        if owner is not None:
            self._xx = x
            self._yy = y
        else:
            self._xx = self._parent.winfo_rootx() + x
            self._yy = self._parent.winfo_rooty() + y
        # pv(self.pos)

        topctrl.geometry(f'{self._ww}x{self._hh}+{self._xx}+{self._yy}')

        # self.withdraw()
        iddlg = self._idself

        frmdlg_xml = self.create_xml("Top", {})

        id_frmain = f"frmMain{iddlg}"
        frmain_xml = self.create_xml("ScrollableFrame", {"id": id_frmain,
            "Width": f"{self._ww-30}", "Height": f"{self._hh-160}"}, frmdlg_xml)
        _, frmmain_ctrl = self.create_control(self._top,
            frmain_xml, 0)
        self._idctrl_dict[id_frmain] = frmmain_ctrl

        for sub_ctrl in self._subctrlcfg_list:
            _ = self.create_controls(frmmain_ctrl, sub_ctrl, 1)

        _ = self.assemble_control(frmmain_ctrl, {"layout": "pack",
            "pack": "{'side':'top','fill':'both','expand':True,'padx':5,'pady':5}"})

        frmbot_xml = self.create_xml("Frame", {"id": f"frmBot{iddlg}"}, frmdlg_xml)
        _, frmbot_ctrl = self.create_control(self._top,
            frmbot_xml, 0)

        btnConfirm_xml = self.create_xml("Button", {"id": f"btnConfirm{iddlg}",
            "text": "Confirm", "options": "{'width':20}"}, frmbot_xml)
        id_btnconfirm, btnConfirm_ctrl = self.create_control(frmbot_ctrl,
            btnConfirm_xml, 1)

        _ = self.assemble_control(btnConfirm_ctrl, {"layout":"pack",
            "pack":"{'side':'right','fill':'both','expand':True,'padx':5,'pady':5}"}, f"{'  '*1}")

        bntcancel_xml = self.create_xml("Button", {"id": f"btnCancel{iddlg}",
            "text": "Cancel", "options": "{'width':20}"}, frmbot_xml)
        id_btncancel, btncancel_ctrl = self.create_control(frmbot_ctrl,
            bntcancel_xml, 1)

        _ = self.assemble_control(btncancel_ctrl, {"layout":"pack",
            "pack":"{'side':'right','fill':'both','expand':True,'padx':5,'pady':5}"}, f"{'  '*1}")

        _ = self.assemble_control(frmbot_ctrl, {"layout": "pack",
            "pack": "{'side':'bottom','fill':'x','expand':True,'padx':5,'pady':5}"})

        self._extral_msg = kwargs
        _ = self.process_message("beforego", **kwargs)

        topctrl.title(self._title)

        # Disable the window's resizing capability
        _ = topctrl.resizable(width=tk.FALSE, height=tk.FALSE)
        # self._top.wait_visibility() # can't grab until window appears, so we wait
        topctrl.transient(self._parent)   # dialog window is related to main
        topctrl.protocol("WM_DELETE_WINDOW", self.destroy) # intercept close button

        # WinBasic.register_eventhandler(self, id_btncancel, self._do_cancel)
        self.register_eventhandler(id_btncancel, self._do_cancel)
        # WinBasic.register_eventhandler(self, id_btnconfirm, self._do_confirm)
        self.register_eventhandler(id_btnconfirm, self._do_confirm)

        # if self._owner is not None:
        #     self._owner.back()
        super().back(False)

        # 设置achieved_value，使该窗口始终处于其他窗口的上层
        _ = topctrl.wm_attributes("-topmost", True)  # pyright: ignore[reportUnknownMemberType]
        topctrl.grab_set()        # ensure all input goes to our window
        topctrl.wm_deiconify()
        # self._parent.wait_window(self._top)
        topctrl.wait_window()
        # pv(self._id_list)

    def _do_cancel(self, **kwargs: object):
        # po(f"Dialog {self._idself} _do_cancel")
        self.destroy(confirm=False, **kwargs)

    def _do_confirm(self, **kwargs: object):
        # po(f"Dialog {self._idself} _do_confirm")
        self.destroy(confirm=True, **kwargs)

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        kwargs.update(self._extral_msg)
        return super().process_message(idmsg, **kwargs)

    @override
    def destroy(self, **kwargs: object):
        # po(f"Dialog {self._idself} destroy")
        # pv(kwargs)
        confirm = cast(bool, kwargs.get("confirm", False))
        if self._top:
            topctrl = cast(tk.Toplevel, self._top.control)
            if confirm:
                ret, msg = cast(tuple[bool, str],
                    super().process_message("confirm", **kwargs))
                if not ret:
                    # self._app.show_err(self._title, msg)
                    print(f"{self._title}: {msg}")
                    return
            else:
                _ = self.process_message("cancel", **kwargs)

            if before_close := cast(EventHanlder | None, getattr(
                        self, "_before_close"
                    , None)):  # get before_close from child
                ret, msg = cast(tuple[bool, str], before_close(**kwargs))
                if not ret:
                    # self._app.show_err(self._title, msg)
                    print(f"{self._title}: {msg}")
                    return
            else:
                print(f"Warnning: {self._title} has no before_close")

            topctrl.grab_release()
            super().back()
            for idctrl in list(self._idctrl_dict.keys()):
                self.delete_control(idctrl)
            # po("subctrl have been deleted!")
            self._idctrl_dict.clear()
            topctrl.destroy()
            self._top = None
        self._alive = False
        # if self._owner is not None:
        #     self._owner.back(False)
        super().destroy()

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

        self._title: str

        self.set_title(self._title)
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

    def _center_window(self, width: int, hight: int):
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
        cen_y = int((sh - hight) / 2)

        self._xx: int = cen_x
        self._yy: int = cen_y

        # 设置窗口大小并居中
        self._win.geometry(f"{width}x{hight}+{cen_x}+{cen_y}")

    def set_title(self, val: str):
        self._title = val
        self._win.title(self._title)

    @override
    def create_window(self):
        if self._ww and self._hh:
            self._center_window(self._ww, self._hh)

        for frm in list(self._wincfg):
            # _ = self.create_controls(self._win, frm)
            _ = self.create_controls(self._root, frm)

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
