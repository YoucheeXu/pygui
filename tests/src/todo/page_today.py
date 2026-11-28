import datetime
import tkinter as tk
from tkinter import messagebox
from typing import TypedDict, cast, override

from pygui_simple.winbasic import Widget, WinBasic, on_message
from pyutilities_simple.logit import po

from src.database.time_database_type import (
    DayType,
    ReminderDataDict,
    StatusEnum,
    TimeUnit,
    default_plan_data,
)
from src.todo.page_base import BaseTodoPage
from src.todo.todo_item import TodoItem
from src.todo.todo_type import (
    COLORS,
    FONT_CONFIG,
    SWIPE_CONFIG,
    Todo,
    TodoData,
    TodosDict,
)


class TimeGroup(TypedDict):
    name: str
    start: datetime.time
    end: datetime.time

TIME_GROUPS: dict[str, TimeGroup] = {
    "morning": {"name": "Morning", "start": datetime.time(6, 0), "end": datetime.time(12, 0)},
    "afternoon": {"name": "Afternoon", "start": datetime.time(12, 0), "end": datetime.time(18, 0)},
    "evening": {"name": "Evening", "start": datetime.time(18, 0), "end": datetime.time(6, 0)},
    # "no_reminder": {"name": "No reminder", "start": None, "end": None}
}

class ReminderGroups(TypedDict):
    morning: ReminderDataDict
    afternoon: ReminderDataDict
    evening: ReminderDataDict

# FIXME: Drag-and-drop sorting is not working properly. 
class TodayTodoPage(BaseTodoPage):
    def __init__(self, parent: Widget, owner: WinBasic, title: str):
        super().__init__(parent, owner, title)

        self._editing_todo_id: int | None = None

        self._placeholder_text: str = "Add new todo..."

        # Load data
        # self._todos = self.load_todos()

        self._original_todo_id: int | None = None
        self._current_offset_y: int = 0
        self._drag_placeholder: tk.Frame | None = None

        self._wrapper: tk.Frame # TODO

        # setup_stats_bar:
        # stats_frame = tk.Frame(self.content_frame, bg=COLORS["background"], height=40)
        # stats_frame.pack(fill="x", padx=20, pady=10)

        # self._stats_label: tk.Label = tk.Label(
        #     stats_frame, text=self.get_stats_text(), font=FONT_CONFIG["small"],
        #     bg=COLORS["background"], fg=COLORS["secondary_text"]
        # )
        # self._stats_label.pack(anchor="w")

        self._todo_container: tk.Frame = cast(tk.Frame, self._scrollable_frame.control)

        # setup_add_todo
        add_frame = tk.Frame(cast(tk.Widget, self._content_frame.control), bg=COLORS["background"], height=60)
        add_frame.pack(fill="x", padx=15, pady=10)

        # Input field
        self._todo_entry: tk.Entry = tk.Entry(
            add_frame, font=FONT_CONFIG["body"], bg=COLORS["card"], fg=COLORS["primary_text"],
            insertbackground=COLORS["accent"], relief="flat", bd=0, highlightthickness=0
        )
        self._todo_entry.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self._setup_entry_placeholder(self._todo_entry, self._placeholder_text)
        _ = self._todo_entry.bind("<Return>", self._on_add_todo)

        # Add button
        add_btn = tk.Button(
            add_frame, text="Add", font=FONT_CONFIG["small"],
            bg=COLORS["accent"], fg="white", borderwidth=0, relief="flat",
            command=self._on_add_todo, width=8
        )
        add_btn.pack(side="right", padx=5, pady=5)

    def on_window_resize(self, _: tk.Event) -> None:
        # if event.widget == self._parent:
        # if event.widget == self._gui.win:
            # self.render_todo_list()
        pass

    def _find_next_reminder(self, tododata: TodoData):
        last_fnshd_idx = -1
        for idx, reminder_info in enumerate(tododata['reminder_infos']):
            if reminder_info["completed"]:
                last_fnshd_idx = idx

        if last_fnshd_idx == -1:
            reminder_idx = 0
        else:
            reminder_idx = last_fnshd_idx + 1

        return reminder_idx

    def get_todo_time_group(self, reminder_time: datetime.time):
        if TIME_GROUPS["morning"]["start"] <= reminder_time < TIME_GROUPS["morning"]["end"]:
            return "morning"
        elif TIME_GROUPS["afternoon"]["start"] <= reminder_time < TIME_GROUPS["afternoon"]["end"]:
            return "afternoon"
        else:
            return "evening"

    def group_todos_by_time(self):
        grouped_todos: dict[str, list[Todo]] = {
            "morning": [], "afternoon": [], "evening": [], "no_reminder": []
        }

        # Sort by creation time (newest first)
        # sorted_todos = sorted(self._todos, key=lambda x: x["created_at"], reverse=True)
        sorted_todos = self._todos_data

        today =  datetime.date.today()
        for tid, tododata in sorted_todos.items():
            group_key = "no_reminder"
            if tododata["reminder_id"] !=0:
                for reminder_info in tododata["reminder_infos"]:
                    if not reminder_info["completed"]:
                        group_key = self.get_todo_time_group(reminder_info["clock_time"])
                        break
            reminder_idx = self._find_next_reminder(tododata)
            tudu: Todo = {
                "tid": tid,
                "data": tododata,
                "day": today,
                "reminder_idx": reminder_idx
            }
            grouped_todos[group_key].append(tudu)

        return grouped_todos

    def get_stats_text(self) -> str:
        total = len(self._todos_data)
        completed = sum(1 for todo in self._todos_data.values() if todo["status"] == StatusEnum.COMPLETED)

        return f"Completed {completed} / Total {total}"

    def create_group_title(self, group_key: str) -> tk.Frame:
        # group_info = TIME_GROUPS.get(group_key,
            # {"name": "No reminder", "start": None, "end": None})
        if group_key in TIME_GROUPS:
            title = TIME_GROUPS[group_key]["name"]
        else:
            title = "No reminder"

        title_frame = tk.Frame(self._todo_container, bg=COLORS["background"], height=30, width=400)
        title_frame.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(
            title_frame, text=title, font=FONT_CONFIG["group_title"],
            bg=COLORS["background"], fg=COLORS["group_title"]
        ).pack(anchor="w", padx=5)

        return title_frame

    def render_todo_list(self) -> None:
        if not self._todo_container:
            return

        # Clear existing items
        for widget in self._todo_container.winfo_children():
            widget.destroy()
        self._todo_items.clear()

        # Cancel active edits
        # self._editing_todo_id = None
        # self._current_edit_entry = None

        # Group todos
        grouped_todos = self.group_todos_by_time()
        group_order = ["morning", "afternoon", "evening", "no_reminder"]
        # group_order = list(TIME_GROUPS.keys())

        # Check if empty
        has_any_todo = any(len(v) > 0 for v in grouped_todos.values())
        if not has_any_todo:
            empty_label = tk.Label(
                self._todo_container, text="No todos yet! Add one below.",
                font=FONT_CONFIG["body"], bg=COLORS["background"], fg=COLORS["secondary_text"]
            )
            empty_label.pack(pady=50)
            return

        # Render groups
        for group_key in group_order:
            tudus_in_group = grouped_todos[group_key]
            if not tudus_in_group:
                continue

            # Group title
            _ = self.create_group_title(group_key)

            for idx, todo in enumerate(tudus_in_group):
                show_divider = (idx < len(tudus_in_group) - 1)
                tudu_item = TodoItem(self._todo_container, todo, self, width=self._width, show_divider=show_divider)
                self._todo_items[todo["tid"]] = tudu_item

        # Update scroll region
        self._todo_container.update_idletasks()

    @override
    def refresh(self):
        self._todo_items.clear()
        self.render_todo_list()
        # self.update_stats()

    def _on_add_todo(self, event: tk.Event | None = None) -> None:
        if not self._todo_entry:
            return

        text = self._todo_entry.get().strip()
        if text == self._placeholder_text or not text:
            _ = messagebox.showwarning("Warning", "Please enter todo content!")
            return

        # Create new todo
        plandata = default_plan_data()
        plandata['name'] = text
        # eid = uuid.uuid4().int
        eid = 0
        now = datetime.datetime.now()
        reminderdata: ReminderDataDict = {
            "clk_time": None,
            "bgn_time": None,  # Default
            "duration": 0,
            "every": 0,
            "unit": TimeUnit.WEEK,
            "custom": DayType.EVERYDAY,
            "cycbgn_dtime": now,  # Default
            "cycend_dtime": None   # Default
        }
        plandata["reminders"][eid] = reminderdata

        new_todo: TodoData = {
            "name": plandata['name'],
            "note": plandata['note'],
            "tags": plandata['tags'],
            "fid": plandata['fid'],
            "status": plandata["status"],
            "reminder_id": 0,
            "reminder": reminderdata,
            "reminder_infos": []
        }

        assert self._owner is not None
        tid = cast(int, self._owner.process_message("NewTodo", tododata=new_todo, plandata=plandata, reminderdata=reminderdata))

        self._todos_data[tid] = new_todo

        self.render_todo_list()
        # self.update_stats()

        # Reset input
        self._todo_entry.delete(0, tk.END)
        self._todo_entry.insert(0, self._placeholder_text)
        _ = self._todo_entry.config(fg=COLORS["placeholder"])

    def delete_todo_by_id(self, todo_id: int) -> None:
        # Remove from list
        del self._todos_data[todo_id]

        # Save and refresh
        # self.save_todos()
        self.render_todo_list()
        # self.update_stats()

    # TODO:
    def tick(self) -> None:
        # Update todo in list
        for tudu_item in self._todo_items.values():
            tudu_item.tick()

    @override
    def _on_global_click(self, event: tk.Event):
        self._todo_entry.delete(0, tk.END)
        self._todo_entry.insert(0, self._placeholder_text)
        _ = self._todo_entry.config(fg=COLORS["placeholder"])

        cast(tk.Widget, self._scrollable_frame.control).focus()

        if not self._editing_todo_id:
            return

        # Check if click is outside edit field
        # widget = event.widget
        # if widget == self._current_edit_entry or widget in self._current_edit_entry.winfo_children():
        #     return

        self._todo_items[self._editing_todo_id].save_edit()

    # def update_stats(self) -> None:
    #     if self._stats_label:
    #         _ = self._stats_label.config(text=self.get_stats_text())

    def _setup_entry_placeholder(self, entry: tk.Entry, placeholder: str) -> None:
        def on_focus_in(event: tk.Event) -> None:
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                _ = entry.config(fg=COLORS["primary_text"])

        def on_focus_out(event: tk.Event) -> None:
            if not entry.get().strip():
                entry.insert(0, placeholder)
                _ = entry.config(fg=COLORS["placeholder"])

        # Initialize placeholder
        entry.insert(0, placeholder)
        _ = entry.config(fg=COLORS["placeholder"])
        _ = entry.bind("<FocusIn>", on_focus_in)
        _ = entry.bind("<FocusOut>", on_focus_out)

    def _create_drag_placeholder(self, reference_item: tk.Frame) -> None:
        if self._drag_placeholder:
            self._drag_placeholder.destroy()

        # tudu_items: list[tk.Frame] = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        tudu_items = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        ref_index: int = tudu_items.index(reference_item) if reference_item in tudu_items else 0

        self._drag_placeholder = tk.Frame(
            self._todo_container, bg=COLORS["drag_placeholder"],
            height=SWIPE_CONFIG["placeholder_height"], width=400
        )
        if ref_index < len(tudu_items):
            self._drag_placeholder.pack(fill="x", pady=0, before=tudu_items[ref_index])

    def _move_drag_placeholder(self, target_index: int) -> None:
        if not self._drag_placeholder:
            return

        # tudu_items: list[tk.Frame] = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        tudu_items = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        if 0 <= target_index < len(tudu_items):
            self._drag_placeholder.pack_forget()
            self._drag_placeholder.pack(fill="x", pady=0, before=tudu_items[target_index])

    def _handle_drag_sort(self, dy: int) -> None:
        self._current_offset_y = dy
        self._wrapper.place(y=self._wrapper.winfo_y() + dy)

        # Find nearest todo item
        # tudu_items: list[tk.Frame] = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        tudu_items = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        current_y: int = self._wrapper.winfo_y() + SWIPE_CONFIG["placeholder_height"] // 2

        nearest_index: int = -1
        min_distance: float = float("inf")

        for idx, item in enumerate(tudu_items):
            if item == self._wrapper:
                continue
            item_y: int = item.winfo_y() + SWIPE_CONFIG["placeholder_height"] // 2
            distance: float = abs(item_y - current_y)

            if distance < min_distance:
                min_distance = distance
                nearest_index = idx

        if nearest_index != -1 and nearest_index != self._last_nearest_index:
            self._move_drag_placeholder(nearest_index)
            self._last_nearest_index: int = nearest_index

    def _finalize_drag_sort(self) -> None:
        """ Complete drag sorting and update todo order"""
        if not self._drag_placeholder or not self._original_todo_id:
            return

        # Get current order of todo items
        # tudu_items: list[tk.Frame] = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        tudu_items = [w for w in self._todo_container.winfo_children() if hasattr(w, "todo_id")]
        placeholder_index: int = tudu_items.index(self._drag_placeholder) if self._drag_placeholder in tudu_items else -1

        if placeholder_index == -1:
            return

        # Find original todo
        # original_todo = next((t for t in self._todos_data if t["iid"] == self._original_todo_id), None)
        # if not original_todo:
        #     return

        # Remove original todo from list
        # self._todos_data = [t for t in self._todos_data if t["iid"] != self._original_todo_id]

        # Insert at new position
        # self._todos_data.insert(placeholder_index, original_todo)

        # Save and re-render
        # self.save_todos()
        self.render_todo_list()

    @on_message("StartEdit")
    def on_start_edit(self, **kwargs: object):
        self._editing_todo_id = cast(int, kwargs["tid"])
        po(f"start edit tid = {self._editing_todo_id}")

        return True

    @on_message("SaveEdit")
    def on_save_edit(self, **kwargs: object):
        tid = cast(int, kwargs["tid"])
        self._editing_todo_id = None
        po(f"save edit tid = {tid}")

        return True

    @on_message("CancelEdit")
    def on_cancel_edit(self, **kwargs: object):
        tid = cast(int, kwargs["tid"])
        self._editing_todo_id = None
        po(f"cancel edit tid = {tid}")

        return True

    # @on_message("ModifyTodo")
    # def on_(self, **kwargs: object):
    #     tudu = cast(TodoDict, kwargs["todo_dict"])
    #     self.modify_todo(tudu["tid"], tudu)
    #     assert self._owner is not None
    #     _ = self._owner.process_message("ModifyTodo", todo_dict=tudu)

    #     return True

    @on_message("CompleteTodo")
    def on_complete_todo(self, **kwargs: object):
        tudu = cast(Todo, kwargs["todo"])
        assert self._owner is not None
        tododata = tudu["data"]
        now = datetime.datetime.now()
        reminder_idx = tudu["reminder_idx"]
        reminder_info = tododata["reminder_infos"][reminder_idx]

        # Mark complete
        tid = tudu["tid"]
        self._todos_data[tid]["reminder_infos"][reminder_idx]["completed"] = True

        # Notify owner
        clock_time = reminder_info["clock_time"]
        reminder_dtime = datetime.datetime.combine(tudu["day"], clock_time)
        duration = int(reminder_dtime.timestamp())
        _ = self._owner.process_message("RecordTodo", id=tudu["tid"],
            strt_dtime=now, duration=duration)

        # Next reminder
        reminder_idx = -1
        now = datetime.datetime.now()
        reminder_infos = tododata["reminder_infos"]
        for idx in range(tudu["reminder_idx"] + 1, len(reminder_infos)):
            if not reminder_infos[idx]["completed"]:
                clock_time = reminder_infos[idx]["clock_time"]
                reminder_dtime = datetime.datetime.combine(tudu["day"], clock_time)
                if reminder_dtime >= now:
                    reminder_idx = idx
                    break

        if reminder_idx == -1:
            del self._todos_data[tid]

        self.refresh()

        return True
