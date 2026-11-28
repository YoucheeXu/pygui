import tkinter as tk
from collections.abc import Callable

from src.todo.todo_type import COLORS


class RoundCheckbutton:
    def __init__(self, parent: tk.Frame, callback: Callable[[], None] | None = None, is_checked: bool = False) -> None:
        self._parent: tk.Frame = parent
        self._callback: Callable[[], None] | None = callback
        self._checked: bool = is_checked

        self._canvas: tk.Canvas = tk.Canvas(
            parent, width=20, height=20, bg=COLORS["background"], highlightthickness=0
        )
        self._canvas.pack(side="left", padx=(5, 10), pady=5)
        self._draw_checkbox()

        _ = self._canvas.bind("<Button-1>", self.on_click)
        _ = self._canvas.bind("<B1-Motion>", lambda e: "break")

    def _draw_checkbox(self) -> None:
        self._canvas.delete("all")
        if self._checked:
            _ = self._canvas.create_oval(2, 2, 18, 18, fill=COLORS["accent"], outline="")
            _ = self._canvas.create_polygon(5, 10, 8, 13, 15, 6, fill="white", outline="")
        else:
            _ = self._canvas.create_oval(2, 2, 18, 18, fill="", outline=COLORS["secondary_text"], width=1)

    def on_click(self, _: tk.Event) -> str:
        self._checked = not self._checked
        self._draw_checkbox()
        if self._callback:
            self._callback()
        return "break"

    def select(self, checked: bool) -> None:
        self._checked = checked
        self._draw_checkbox()

    def deselect(self):
        self.select(False)
