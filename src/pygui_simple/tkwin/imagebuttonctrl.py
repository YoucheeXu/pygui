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


@WidgetRegistry.register("ImageButton")
class ImageButtonCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        master = cast(tk.Misc, parent.control)
        text = attr_dict.get("text", "")
        width = cast(int, options.get("width", 0))
        height = cast(int, options.get("height", 0))

        ctrl = tk.Button(master, **options)
        tooltip = attr_dict.get("tooltip", "")
        super().__init__(idself, master, text, ctrl, tooltip)
        # self._res_path: str = owner.res_path
        self._app_path: str = owner.path
        self._ww: int = width
        self._image: ImageTk.PhotoImage
        self._hh: int = height if height else width if width else 0

        image = attr_dict.get("image")
        assert image is not None
        imagefile = os.path.join(self._app_path, image)
        eimg = self._read_image(imagefile, self._ww, self._hh)
        # if eimg is None:
            # raise RuntimeError(f"fail to read image: {imagefile}")

        def cmd():
            _ = owner.process_message(idself,
                mousepos=(ctrl.winfo_rootx(), ctrl.winfo_rooty()))

        if text:
            _ = ctrl.configure(text=text, image=eimg, command=cmd, compound=tk.LEFT,
                relief=tk.FLAT, **options)
                # **options)
        else:
            _ = ctrl.configure(image=eimg, command=cmd, relief=tk.FLAT, **options)
        self._image = eimg

    def _read_image(self, imagepath: str, w: int, h: int):
        # image = cv2.imread(imagepath, cv2.IMREAD_UNCHANGED)
        img_raw = Image.open(fp=imagepath).convert("RGBA")
        if w:
            # image = cv2.resize(image, (w, h), interpolation=cv2.INTER_CUBIC)
            img_raw = img_raw.resize(size=(w, h))
        return ImageTk.PhotoImage(image=img_raw)

    # TODO: wait to test
    def change_image(self, imagefile: str, w: int = 0, h: int = 0):
        imagefile = os.path.join(self._app_path, imagefile)
        if not w:
            w, h = self._ww, self._hh
        photo = self._read_image(imagefile, w, h)
        # if photo is not None:
        btn = cast(tk.Button, super().control)
        _ = btn.configure(image=photo)
        # btn.image = photo
        self._image = photo
