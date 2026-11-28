import tkinter as tk
from abc import ABCMeta
from typing import override

from pygui_simple.winbasic import Widget, WinBasic

from src.pagectrl import PageCtrl
from src.todo.todo_item import TodoItem
from src.todo.todo_type import TodosDict


class BaseTodoPage(PageCtrl, metaclass=ABCMeta):
    """ Base class for all Todo pages (shared UI structure).

    This class provides a reusable UI template for all four todo pages, including
    a title bar with a back button to TodoTab and a content frame for page-specific
    widgets. All concrete pages inherit from this class.

    Args:
        parent: Parent widget (root window or container frame)
        controller: Main application instance for frame navigation
        page_title: Display title for the page's title bar
    """
    def __init__(self, parent: Widget, owner: WinBasic, title: str, width: int = 390, **kwargs: object) -> None:
        super().__init__(parent, title, owner, width=width, **kwargs)

        self._width: int = width

        self._todo_items: dict[int, TodoItem] = {}
        self._todos_data: TodosDict = {}

    @override
    def _go_back(self, event: tk.Event) -> None:
        """ Navigate back to the main TodoTab frame.

        Triggers the main app's frame switching method to display TodoTab.
        """
        assert self._owner is not None
        _ = self._owner.process_message("ShowMainPage")

    @property
    def todos(self):
        return self._todos_data

    @todos.setter
    def todos(self, val: TodosDict):
        self._todos_data = val
        # pv(self._todos_data)

    @override
    def show(self):
        self.refresh()
        super().show()
