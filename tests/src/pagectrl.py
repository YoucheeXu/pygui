#!/usr/bin/python3
import tkinter as tk
import xml.etree.ElementTree as et
from ast import literal_eval
from tkinter import ttk
from typing import cast, override

from pygui_simple.tkwin.framectrl import FrameCtrl
from pygui_simple.tkwin.scrollableframectrl import ScrollableFrameCtrl
from pygui_simple.winbasic import Widget, WinBasic


class PageCtrl(WinBasic):
    def __init__(self, parent: Widget, title: str, owner: WinBasic, *, width: int = 0, **kwargs: object):
        self._main_frame: FrameCtrl = FrameCtrl(parent, width=width)
        self._ctrl: tk.Widget = cast(tk.Widget, self._main_frame.control)

        super().__init__(owner.path)

        self._title: str = title
        self._owner = owner  # pyright: ignore[reportUnannotatedClassAttribute]
        self._alive: bool = False

        # -------------------------- Grid Layout (Key to Fill Remaining Space) -------------------------
        # Row 0: Fixed nav/title bar (weight=0)
        # Row 1: Content frame fills ALL remaining space (weight=1)
        # Column 0: Full width fill (weight=1)
        _ = self._ctrl.grid_rowconfigure(0, weight=0)
        _ = self._ctrl.grid_rowconfigure(1, weight=1)
        _ = self._ctrl.grid_columnconfigure(0, weight=1)

        # -------------------------- Title Bar (Consistent for All Pages, Fixed Height) -------------------------
        # Create title bar frame with background color
        nav_bar = tk.Frame(self._ctrl, 
            # bg="#2c3e50",
            height=50)
        # Place title bar in row 0, full width
        nav_bar.grid(row=0, column=0, sticky="nsew", padx=2)
        _ = nav_bar.pack_propagate(False)  # Fix height

        # Back Button (returns to TodoTab)
        back_btn = ttk.Label(
            nav_bar,
            text="<<"
        )
        back_btn.pack(side=tk.LEFT, padx=10, pady=8)
        _ = back_btn.bind("<Button-1>", self._go_back)

        # Page Title Label
        title_label = tk.Label(
            nav_bar,
            text=self._title,
            # fg=COLORS["accent"],
            # bg="white",
            font=("Arial", 14, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=120)

        # Edit button
        # self._edit_btn: ttk.Label = ttk.Label(
        #     nav_bar, text="Edit", font=FONT_CONFIG["small"],
        #     # bg="white",
        #     # fg=COLORS["accent"],
        #     borderwidth=0,
        #     # command=self._toggle_edit_mode
        # )
        # self._edit_btn.place(relx=0.9, rely=0.5, anchor="center")
        # _ = self._edit_btn.bind("<Button-1>", self._toggle_edit_mode)

        # -------------------------- Page Content Frame (FILLS ALL REMAINING SPACE) -----------
        self._content_frame: FrameCtrl = FrameCtrl(self._main_frame, bg="#ecf0f1")
        self._scrollable_frame: ScrollableFrameCtrl = ScrollableFrameCtrl(self._content_frame, width=width)
        # self._scrollable_frame: FrameCtrl = FrameCtrl(self._main_frame, width=380, height=800)
        _ = self._scrollable_frame._inner_frame.config(bg="#F5F5F7")
        _ = cast(tk.Frame, self._scrollable_frame.control).config(bg="#F5F5F7")
        self._scrollable_frame._outter_frame.pack(fill="both", expand=True, padx=0, pady=0)
        cast(tk.Widget, self._content_frame.control).grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        _ = self._scrollable_frame._canvas.bind("<Button-1>", self._on_global_click)

        self._construct_children()

    def _go_back(self, event: tk.Event):
        pass

    def _on_global_click(self, event: tk.Event):
        pass

    def _construct_children(self):
        pass

    def refresh(self):
        pass

    def show(self):
        self._alive = True
        self.refresh()
        cast(tk.Frame, self._main_frame.control).tkraise()

    def hide(self):
        self._alive = False

    def assemble(self, attr_dict: dict[str, str], prefix: str = ""):
        if "layout" in attr_dict:
            if attr_dict["layout"] == "pack":
                self._ctrl.pack(**(literal_eval(attr_dict["pack"])))
            elif attr_dict["layout"] == "grid":
                self._ctrl.grid(**(literal_eval(attr_dict["grid"])))
            elif attr_dict["layout"] == "place":
                self._ctrl.place(**(literal_eval(attr_dict["place"])))
            else:
                # self.debug_print(f"{prefix}, unknown layout of {attr_dict['layout']}")
                return
        else:
            # self._debug_print(f"{attr_dict['text']}: no assemble")
            return

        if "childOpt" in attr_dict:
            for child in self._ctrl.winfo_children():
                cast(tk.Widget, child).grid_configure(**(literal_eval(attr_dict["childOpt"])))

        # self.debug_print(f"{prefix}, layout: {attr_dict['layout']}")

    def refresh_content(self):
        canvas = self._scrollable_frame._canvas
        _ = canvas.configure(scrollregion=canvas.bbox("all"))

    @override
    def destroy(self, **kwargs: object):
        return super().destroy(**kwargs)

class tkPageCtrl(PageCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        title = attr_dict["title"]
        width = cast(int, attr_dict.get("Width", 0))
        height = cast(int, attr_dict.get("Height", 0))

        self._subctrlcfg_list: list[et.Element] = list(ctrl_cfg)

        super().__init__(parent, title, owner, width=width, height=height)

        self._id: str = attr_dict.get("id", "")

    @property
    def id(self):
        return self._id

    @override
    def _construct_children(self):
        for sub_ctrl in self._subctrlcfg_list:
            _ = self.create_controls(self._scrollable_frame, sub_ctrl, 1)
        return super()._construct_children()
