import importlib
from typing import TYPE_CHECKING, cast

from pygui_simple.winbasic import Control

_LAZY = {
    "ButtonCtrl": ".buttonctrl",
    "CalendarCtrl": ".calendarctrl",
    "CanvasCtrl": ".canvasctrl",
    "CheckbuttonCtrl": ".checkbuttonctrl",
    "ComboboxCtrl": ".comboboxctrl",
    "EntryCtrl":  ".entryctrl",
    "FrameCtrl":  ".framectrl",
    "ImageButtonCtrl": ".imagebuttonctrl",
    "ImagePanelCtrl": ".imagepanelctrl",
    "LabelCtrl":  ".labelctrl",
    "LabelFrameCtrl":  ".labelframectrl",
    "ListboxCtrl":  ".listboxctrl",
    "MenuCtrl":  ".menuctrl",
    "NotebookCtrl":  ".notebookctrl",
    "PicsListviewCtrl":  ".picslistviewctrl",
    "RadiobuttonCtrl":  ".radiobuttonctrl",
    "RadioButtonGroupCtrl":  ".radiobuttongroupctrl",
    "ScrollableFrameCtrl":  ".scrollableframectrl",
    "ScrollbarCtrl":  ".scrollbarctrl",
    "ScrolledTextCtrl":  ".scrolledtextctrl",
    "ScrollPickerCtrl":  ".scrollpickerctrl",
    "SlideSwitchCtrl":  ".slideswitchctrl",
    "SpinboxCtrl":  ".spinboxctrl",
    "StatusBarCtrl":  ".statusbarctrl",
    "StyleCtrl":  ".stylectrl",
    "TimeScrollPickerCtrl":  ".scrollpickerctrl",
    "ToolbarCtrl":  ".toolbarctrl",
}

if TYPE_CHECKING:
    from .buttonctrl import ButtonCtrl
    from .calendarctrl import CalendarCtrl
    from .canvasctrl import CanvasCtrl
    from .checkbuttonctrl import CheckbuttonCtrl
    from .comboboxctrl import ComboboxCtrl
    from .entryctrl import EntryCtrl
    from .framectrl import FrameCtrl
    from .imagebuttonctrl import ImageButtonCtrl
    from .imagepanelctrl import ImagePanelCtrl
    from .labelctrl import LabelCtrl
    from .labelframectrl import LabelFrameCtrl
    from .listboxctrl import ListboxCtrl
    from .menuctrl import MenuCtrl
    from .notebookctrl import NotebookCtrl
    from .picslistviewctrl import PicsListviewCtrl
    from .radiobuttonctrl import RadiobuttonCtrl
    from .radiobuttongroupctrl import RadioButtonGroupCtrl
    from .scrollableframectrl import ScrollableFrameCtrl
    from .scrollbarctrl import ScrollbarCtrl
    from .scrolledtextctrl import ScrolledTextCtrl
    from .scrollpickerctrl import ScrollPickerCtrl, TimeScrollPickerCtrl
    from .slideswitchctrl import SlideSwitchCtrl
    from .spinboxctrl import SpinboxCtrl
    from .statusbarctrl import StatusBarCtrl
    from .stylectrl import StyleCtrl
    from .toolbarctrl import ToolbarCtrl

    __all__ = [
        "ButtonCtrl",
        "CalendarCtrl",
        "CanvasCtrl",
        "CheckbuttonCtrl",
        "ComboboxCtrl",
        "EntryCtrl",
        "FrameCtrl",
        "ImageButtonCtrl",
        "ImagePanelCtrl",
        "LabelCtrl",
        "LabelFrameCtrl",
        "ListboxCtrl",
        "MenuCtrl",
        "NotebookCtrl",
        "PicsListviewCtrl",
        "RadioButtonGroupCtrl",
        "RadiobuttonCtrl",
        "ScrollPickerCtrl",
        "ScrollableFrameCtrl",
        "ScrollbarCtrl",
        "ScrolledTextCtrl",
        "SlideSwitchCtrl",
        "SpinboxCtrl",
        "StatusBarCtrl",
        "StyleCtrl",
        "TimeScrollPickerCtrl",
        "ToolbarCtrl",
    ]

def __getattr__(name: str):
    submodule = _LAZY.get(name)
    if submodule is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(submodule, __package__)
    value = cast(type[Control], getattr(module, name))
    globals()[name] = value   # 缓存,之后再访问不会重复 import
    return value

def __dir__():
    return sorted(set(globals()) | set(_LAZY))
