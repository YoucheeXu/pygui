import os
import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast, override

from pygui_simple.tkwin.imagepanelctrl import ImagePanelCtrl
from pygui_simple.tkwin.labelframectrl import LabelFrameCtrl
from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


# TODO: Tip
@WidgetRegistry.register("PicsListview")
class PicsListviewCtrl(tkControl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        master = cast(tk.Misc, parent.control)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        ctrl = ttk.Frame(master, **options)
        super().__init__(ctrl)
        self._image_group: list[LabelFrameCtrl] = []
        self._imagepanel_llist: list[list[ImagePanelCtrl]] = []
        self._owner: WinBasic = owner
        self._num_column: int = int(attr_dict["num_column"])
        self._pic_size: int = int(attr_dict["pic_size"])
        self._app_path: str = owner.path
        self._grp_seld: int = 0
        self._idx_seld: int = 0
        self._idx_lstseld: list[int] = [0, 0]
        self._spacing: int = int(self._pic_size/10)
        self._groupidx: int = 0

        if "id" in attr_dict:
            self._idctrl: str = attr_dict["id"]
        else:
            raise RuntimeError("No id")

    def add_imagegroup(self, title: str, imagefile_list: list[str]):
        # frame = ttk.LabelFrame(self._tkctrl, text=title)
        frame_cfg = self._owner.create_xml("LabelFrame", {"text": f"btnItem{title}"})
        frame = LabelFrameCtrl(self, frame_cfg, self._owner)
        frame.level = self.level+1
        imagepanel_list: list[ImagePanelCtrl] = []
        for i, imagefile in enumerate(imagefile_list):
            imagefile = os.path.join(self._app_path, imagefile)
            ctrl_cfg = self._owner.create_xml("ImagePanel", 
                {"image": imagefile, 
                "options": f"{{'height': {self._pic_size}, 'width': {self._pic_size}}}"})
            image_panel = ImagePanelCtrl(frame, ctrl_cfg, self._owner)
            image_panel.level = self.level+2
            image_panel_ctrl = cast(tk.Widget, image_panel.control)
            image_panel_ctrl.grid(row=i // self._num_column, column=i % self._num_column,
                padx=self._spacing, pady=self._spacing)
            _= image_panel_ctrl.bind("<Button-1>",
                lambda e, grp=self._groupidx, idx=i: self.select(grp, idx))
            imagepanel_list.append(image_panel)
        self._imagepanel_llist.append(imagepanel_list)
        cast(tk.Widget, frame.control).pack()
        self._image_group.append(frame)
        self._groupidx += 1

    def select(self, grp:int, idx: int):
        self._idx_lstseld = [self._grp_seld, self._idx_seld]
        self._grp_seld = grp
        self._idx_seld = idx

        old_imagepanle = self._imagepanel_llist[self._idx_lstseld[0]][self._idx_lstseld[1]]
        _ = old_imagepanle.configure(highlightthickness=0)
        imagepanel = self._imagepanel_llist[self._grp_seld][self._idx_seld]
        _ = imagepanel.configure(highlightbackground="blue", highlightthickness=2)
        _ = self._owner.process_message(self._idctrl, event="clicked",
            group=self._grp_seld, index=self._idx_seld)

    def get_selected(self) -> tuple[int, int]:
        return self._grp_seld, self._idx_seld

    @override
    def destroy(self):
        # po(f"PicsListviewCtrl {self._idself} destroy")
        for group in self._imagepanel_llist:
            for image in group:
                image.destroy()
        self._imagepanel_llist.clear()
        for frm in self._image_group:
            frm.destroy()
        self._image_group.clear()
        self._tkctrl.destroy()
        self._grp_seld = 0
        self._idx_seld = 0
        super().destroy()
