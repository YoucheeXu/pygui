import os
import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, cast

from PIL import Image, ImageTk

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("ImagePanel")
class ImagePanelCtrl(tkControl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        master = cast(tk.Misc, parent.control)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        ctrl = tk.Label(master)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(ctrl, tooltip)
        self._image: ImageTk.PhotoImage | None = None
        if image := attr_dict.get("image", ""):
            width = cast(int, options.get("width", 0))
            height = cast(int, options.get("height", 0))
            # imagefile = os.path.join(owner.res_path, image)
            imagefile = os.path.join(owner.path, image)
            image = self._read_image(imagefile, width, height)
            _ = ctrl.configure(text="", image=image, anchor=tk.CENTER, **options)
            self._image = image
        else:
            _ = ctrl.configure(text="", anchor=tk.CENTER, **options)

    def _read_image(self, imagepath: str, w: int, h: int):
        img_raw  = Image.open(imagepath).convert("RGBA")
        if w:
            # pv(w)
            # pv(h)
            img_raw = img_raw.resize((w, h))
        return ImageTk.PhotoImage(img_raw)

    def display_image(self, image: ImageTk.PhotoImage):
        _ = cast(tk.Label, super().control).configure(image=image)
        self._image = image
