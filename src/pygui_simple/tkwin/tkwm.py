import tkinter as tk
from typing import TypeVar

from pygui_simple.winbasic import Widget

T = TypeVar("T", bound=tk.Tk | tk.Toplevel)
class tkWM[T](Widget):
    def __init__(self, wm: T):
        super().__init__()
        self._tkwm: T = wm
        self.control = self._tkwm  # pyright: ignore[reportUnannotatedClassAttribute]
