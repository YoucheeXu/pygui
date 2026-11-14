import os
import tkinter as tk
import xml.etree.ElementTree as et
from typing import Any, Literal, cast

from PIL import Image, ImageTk

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)

_FontDescription = str | tuple[str, int] | tuple[str, int, str]

@WidgetRegistry.register("Canvas")
class CanvasCtrl(tkControl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        master = cast(tk.Misc, parent.control)
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        self._app_path: str = owner.path
        self._img_cache: list[ImageTk.PhotoImage | None] = []

        ctrl = tk.Canvas(master, **options)
        super().__init__(ctrl)

    def create_text(
        self,
        x: float,
        y: float,
        /,
        *,
        activefill: str = "",
        activestipple: str = "",
        anchor: Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw', 's', 'se'] = "center",
        angle: float | str = 0,
        disabledfill: str = "",
        disabledstipple: str = "",
        fill: str = "black",
        font: _FontDescription = "",
        justify: Literal['left', 'center', 'right'] = "center",
        offset: float | str = "n",
        state: Literal['normal', 'hidden', 'disabled'] = "normal",
        stipple: str = "",
        tags: str | list[str] | tuple[str, ...] = "",
        text: float | str = "",
        width: float | str = 0
    ) -> int:
        """ Typed wrapper for tk.Canvas.create_text with positional-only x/y and keyword-only remaining args.

        Args:
            x: Horizontal coordinate for text anchor point, positional-only parameter.
            y: Vertical coordinate for text anchor point, positional-only parameter.
            activefill: Fill color when item is in active state.
            activestipple: Stipple pattern for active fill color.
            anchor: Anchor position aligning text to (x,y) coordinate.
            angle: Rotation angle of text; None uses Tk internal default.
            disabledfill: Fill color when item is disabled.
            disabledstipple: Stipple pattern for disabled fill color.
            fill: Normal text foreground color, default set to black for visibility.
            font: Tk font definition (string or font tuple format), None uses default system font.
            justify: Multi-line text alignment mode.
            offset: Text drawing offset value, None uses default.
            state: Display state of text item(normal/hidden/disabled).
            stipple: Stipple pattern applied to text fill.
            tags: Tag label or tag list bound to this canvas item.
            text: Content string or numeric value to render as text.
            width: Max wrap width for multi-line text, None disables auto line wrap.

        Returns:
            int: Unique integer canvas item ID returned by native Tk canvas.
        """
        canvas = cast(tk.Canvas, self._tkctrl)
        item_id = canvas.create_text(
            x, y,
            activefill=activefill,
            activestipple=activestipple,
            anchor=anchor,
            angle=angle,
            disabledfill=disabledfill,
            disabledstipple=disabledstipple,
            fill=fill,
            font=font,
            justify=justify,
            offset=offset,
            state=state,
            stipple=stipple,
            tags=tags,
            text=text,
            width=width
        )
        return item_id

    def create_rectangle(self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        /,
        *,
        fill: str = "",
        outline: str = "",
        width: float | str = 1,
        dash: str | int | list[int] | tuple[int, ...] = None,
        stipple: str = "",
        activefill: str = "",
        activeoutline: str = "",
        activedash: str | int | list[int] | tuple[int, ...] = None,
        disabledfill: str = "",
        disabledoutline: str = "",
        state: Literal['normal', 'hidden', 'disabled'] = "normal",
        tags: str | list[str] | tuple[str, ...] = ""
    ) -> int:
        canvas = cast(tk.Canvas, self._tkctrl)
        item_id = canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=fill,
            outline=outline,
            width=width,
            dash=dash,
            stipple=stipple,
            activefill=activefill,
            activeoutline=activeoutline,
            activedash=activedash,
            disabledfill=disabledfill,
            disabledoutline=disabledoutline,
            state=state,
            tags=tags
        )
        return item_id

    def create_image(
            self,
            x: float,
            y: float,
            /,
            *,
            file_path: str,
            target_w: int,
            target_h: int,
            anchor: Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw', 's', 'se'] = "center",
            fallback_fill: str = "#cccccc",
            tags: str | list[str] | tuple[str, ...] | None = None
        ) -> int:
            """Load local image file, auto resize then draw on canvas; auto fallback to colored rectangle on load failure.
            All loaded PhotoImage cached inside instance list to avoid Python GC destroy image resource.

            Args:
                x: Anchor X coordinate for image placement, positional-only param.
                y: Anchor Y coordinate for image placement, positional-only param.
                file_path: Relative/absolute local path of target image file(png/jpg supported).
                target_w: Fixed pixel width to resize source image.
                target_h: Fixed pixel height to resize source image.
                anchor: Align rule of image against input (x,y) coordinate.
                fallback_fill: Fill color for substitute rectangle when image file missing/corrupted.
                tags: Tag labels bind to generated canvas image item.

            Returns:
                int: Canvas item ID of either loaded image or fallback substitute rectangle.
            """
            canvas = cast(tk.Canvas, self._tkctrl)
            # Open source image and convert to RGBA to support transparent alpha channel
            image_path = os.path.join(self._app_path, file_path)
            raw_img = Image.open(image_path).convert("RGBA")
            # High quality down/up scale via LANCZOS resample algorithm
            resized_img = raw_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            photo_obj = ImageTk.PhotoImage(resized_img)
            # Persist image reference into internal cache to prevent garbage collection
            self._img_cache.append(photo_obj)
            item_id = canvas.create_image(x, y, image=photo_obj, anchor=anchor, tags=tags)
            return item_id
