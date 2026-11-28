import datetime
from typing import TypedDict

from src.database.time_database_type import ReminderDataDict, StatusEnum

# --------------------------
# Type Definitions & Config
# --------------------------
COLORS: dict[str, str] = {
    "background": "#F5F5F7",      # iOS light mode background
    "card": "#F5F5F7",            # Same as overall background
    "primary_text": "#1D1D1F",    # Primary text color
    "secondary_text": "#86868B",  # Secondary text color
    "accent": "#007AFF",          # iOS theme blue
    "success": "#34C759",         # Completed state green
    "border": "#E6E6E8",          # Divider color (light gray)
    "danger": "#FF3B30",          # Delete red
    "danger_bg": "#FFEEEE",       # Swipe-to-delete background color
    "placeholder": "#C7C7CC",     # Placeholder text color
    "drag_placeholder": "#EFEFF4",# Drag placeholder background color
    "drag_active": "#E8F4FF",     # Dragging item background color
    "drag_border": "#007AFF",     # Dragging border color
    "group_title": "#636366"      # Group title text color
}

FONT_CONFIG: dict[str, tuple[str, int, str]] = {
    "title": ("Microsoft YaHei", 20, "bold"),
    "subtitle": ("Microsoft YaHei", 16, "normal"),
    "body": ("Microsoft YaHei", 14, "normal"),
    "small": ("Microsoft YaHei", 12, "normal"),
    "group_title": ("Microsoft YaHei", 14, "bold")
}

SWIPE_CONFIG: dict[str, int] = {
    "delete_threshold": -80,      # Left swipe delete threshold (pixels)
    "max_swipe_distance": -80,    # Maximum left swipe distance (pixels)
    "delete_btn_width": 80,       # Delete button width (pixels)
    "animation_duration": 100,    # Rebound animation duration (milliseconds)
    "show_btn_threshold": -20,    # Threshold to show delete button (pixels)
    "drag_threshold": 10,         # Minimum distance to trigger drag sorting (pixels)
    "placeholder_height": 80      # Tudu item height (pixels)
}

REPEAT_OPTIONS: list[str] = [
    "No repeat", "Every day", "Every week", "Every month", "Every year"
]

class ReminderInfo(TypedDict):
    clock_time: datetime.time
    completed: bool

class TodoData(TypedDict):
    name: str
    note: str
    tags: list[str]
    fid: int
    status: StatusEnum
    reminder_id: int
    reminder: ReminderDataDict
    reminder_infos: list[ReminderInfo]

type TodosDict = dict[int, TodoData]

class Todo(TypedDict):
    tid: int
    data: TodoData
    day: datetime.date
    reminder_idx: int
