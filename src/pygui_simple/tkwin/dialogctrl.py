import tkinter as tk
import xml.etree.ElementTree as et
from functools import partial
from typing import cast, override

from pygui_simple.tkwin.buttonctrl import ButtonCtrl
from pygui_simple.tkwin.framectrl import FrameCtrl
from pygui_simple.tkwin.scrollableframectrl import ScrollableFrameCtrl
from pygui_simple.tkwin.tkwm import tkWM
from pygui_simple.winbasic import (
    Container,
    Dialog,
    EventHanlder,
    Widget,
    WidgetRegistry,
    WinBasic,
)


# TODO: auto height
class DialogCtrl(Dialog):
    def __init__(self, parent: Widget, title: str, width: int, height: int):
        super().__init__(title, width, height)

        self._master: tk.Tk | tk.Toplevel = cast(tk.Tk, parent.control)

        self._top: tkWM[tk.Toplevel] | None = None
        self._alive: bool = False
        self._extral_msg: dict[str, object] = {}

    @override
    def title(self, val: str):
        super().title(val)
        self._topctrl.title(self._title)

    @property
    def alive(self):
        return self._alive

    @override
    def movie_window(self, x: int, y: int, w: int, h: int):
        super().movie_window(x, y, w, h)
        self._topctrl.geometry(f'{self._ww}x{self._hh}+{self._xx}+{self._yy}')

    def do_show(self, owner: Container | None = None, x: int = 0, y: int = 0, **kwargs: object):
        self._alive = True
        if owner is not None:
            self._owner = owner  # pyright: ignore[reportUnannotatedClassAttribute]

        # Initialize hidden top-level window
        self._top = tkWM[tk.Toplevel](tk.Toplevel(self._master))
        self._topctrl: tk.Toplevel = cast(tk.Toplevel, self._top.control)
        self._topctrl.withdraw()

        # x, y, _, _ = self._app.get_winsize()
        # if owner is not None:
            # self._xx = x
            # self._yy = y
        # else:
            # self._xx = self._parent.winfo_rootx() + x
            # self._yy = self._parent.winfo_rooty() + y

        if owner is None:
            x += self._master.winfo_rootx()
            y += self._master.winfo_rooty()

        # Main container frame
        self._main_frame: ScrollableFrameCtrl = ScrollableFrameCtrl(self._top,
            width=self._ww-30, height=self._hh-160)
        self._idctrl_dict["frmMain"] = self._main_frame

        self._construct_children()

        _ = self._main_frame.assemble({"layout": "pack",
            "pack": "{'side':'top','fill':'both','expand':True,'padx':5,'pady':5}"})

        # Bottom action bar with confirm/cancel buttons
        bottom_frame = FrameCtrl(self._top, height=50)
        self._idctrl_dict["frmBot"] = bottom_frame

        # Confirm button (save selection and close)
        confirm = partial(self._confirm, **kwargs)
        confirm_button = ButtonCtrl(bottom_frame, "Confirm", width=20,
            command=confirm)
        self._idctrl_dict["btnConfirm"] = confirm_button
        confirm_button.assemble({"layout":"pack",
            "pack":"{'side':'right','fill':'both','expand':True,'padx':5,'pady':5}"}, f"{'  '*1}")

        cancel = partial(self._cancel, **kwargs)
        cancel_button = ButtonCtrl(bottom_frame, "Cancel", width=20,
            command=cancel)
        self._idctrl_dict["btnCancel"] = cancel_button
        cancel_button.assemble({"layout":"pack",
            "pack":"{'side':'right','fill':'both','expand':True,'padx':5,'pady':5}"}, f"{'  '*1}")

        bottom_frame.assemble({"layout": "pack",
            "pack": "{'side':'bottom','fill':'x','padx':5,'pady':5}"})

        self._extral_msg = kwargs
        self._beforego(**kwargs)

        # if not self._ww:
        #     self._topctrl.update_idletasks()
        #     # Calculate window dimensions and position
        #     w, h = self._topctrl.winfo_reqwidth(), self._topctrl.winfo_reqheight()
        #     print(w)
        #     print(h)
        # else:
        #     w, h = self._ww, self._hh
        # self.movie_window(x, y, w, h)
        self.movie_window(x, y, self._ww, self._hh)
        self._topctrl.title(self._title)
        # _ = self._master.after(300, self._main_judge)

        # Disable the window's resizing capability
        _ = self._topctrl.resizable(width=tk.FALSE, height=tk.FALSE)
        # self._top.wait_visibility() # can't grab until window appears, so we wait
        self._topctrl.transient(self._master)   # dialog window is related to main
        self._topctrl.protocol("WM_DELETE_WINDOW", self._cancel) # intercept close button

        # if self._owner is not None:
        #     self._owner.back()
        super().back(False)

        # Keep this window always on top of other windows
        _ = self._topctrl.wm_attributes("-topmost", True)  # pyright: ignore[reportUnknownMemberType]
        self._topctrl.grab_set()        # ensure all input goes to our window
        # Show window and wait for user interaction
        self._topctrl.wm_deiconify()
        # self._parent.wait_window(self._top)
        self._topctrl.wait_window()

    def _construct_children(self):
        pass

    def _main_judge(self):
        """ Check if the dialog window retains focus; close if focus is lost.

        Recursively monitors window focus state and closes the dialog if it loses
        focus to another window/element. Includes exception handling for stability.
        """
        try:
            if self._topctrl.focus_displayof() is None \
                or 'toplevel' not in str(self._topctrl.focus_displayof()):
                self.destroy()
            else:
                _ = self._topctrl.after(10, self._main_judge)
        except tk.TclError:
            _ = self._topctrl.after(10, self._main_judge)

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        if self._alive:
            kwargs.update(self._extral_msg)
            return super().process_message(idmsg, **kwargs)
        return None

    @override
    def destroy(self, **kwargs: object):
        """ Override base Dialog destroy method with empty implementation.
        """
        # po(f"Dialog {self._idself} destroy with {kwargs}")
        if self._top:
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

            self._topctrl.grab_release()
            super().back()
            for idctrl in list(self._idctrl_dict):
                self.delete_control(idctrl)
            # po("subctrl have been deleted!")
            self._idctrl_dict.clear()
            # print(self._idctrl_dict.keys())
            self._topctrl.destroy()
            self._top = None
        self._alive = False
        # if self._owner is not None:
        #     self._owner.back(False)
        super().destroy()

@WidgetRegistry.register("Dialog")
class tkDialogCtrl(DialogCtrl):
    def __init__(self, parent: Widget, dlg_cfg: et.Element, owner: WinBasic):
        self._app: WinBasic = owner

        attr_dict = dlg_cfg.attrib
        super().__init__(parent, attr_dict.get("text", ""), int(attr_dict["Width"]), int(attr_dict["Height"]))

        self._subctrlcfg_list: list[et.Element] = list(dlg_cfg)

    @property
    @override
    def path(self):
        return self._app.path

    @override
    def _construct_children(self):
        for sub_ctrl in self._subctrlcfg_list:
            _ = self.create_controls(self._main_frame, sub_ctrl, 1)
        return super()._construct_children()
