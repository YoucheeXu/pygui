import datetime
import tkinter as tk
from tkinter import messagebox
from typing import TypedDict, cast, override

from pygui_simple.winbasic import Widget, WinBasic
from pyutilities_simple.logit import po

from src.database.time_database_type import (
    DayType,
    ReminderDataDict,
    StatusEnum,
    TimeUnit,
    default_plan_data,
)
from src.pagectrl import PageCtrl
from src.todo.todo_item import TodoItem
from src.todo.todo_type import (
    COLORS,
    FONT_CONFIG,
    SWIPE_CONFIG,
    Todo,
    TodoData,
    TodosDict,
)


class ProjectPage(PageCtrl):
    def __init__(self, parent: Widget, owner: WinBasic, title: str) -> None:
        super().__init__(parent, title, owner)

    @override
    def _go_back(self, event: tk.Event) -> None:
        """ Navigate back to the main TodoTab frame.

        Triggers the main app's frame switching method to display TodoTab.
        """
        assert self._owner is not None
        _ = self._owner.process_message("ShowMainPage")
