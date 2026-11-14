import tkinter as tk
import xml.etree.ElementTree as et
from tkinter import ttk
from typing import Any, cast, override

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


class LabelFrameCtrl(tkControl):
    def __init__(self, parent: Widget, text: str, **kwargs: Any):
        master = cast(tk.Misc, parent.control)
        assert text is not None

        ctrl = ttk.Labelframe(master, text=text, **kwargs)
        super().__init__(ctrl)

    @override
    def destroy(self):
        super().destroy()

@WidgetRegistry.register("LabelFrame")
class tkLabelFrameCtrl(LabelFrameCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])
        text = attr_dict.get("text")
        assert text is not None

        super().__init__(parent, text, **options)
