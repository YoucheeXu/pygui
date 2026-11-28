import datetime
import tkinter as tk
from tkinter import messagebox

from pygui_simple.winbasic import Container
from pyutilities_simple.logit import pv

from src.database.time_database_type import reminder2str, time2str
from src.roundcheckbutton import RoundCheckbutton
from src.todo.todo_type import COLORS, FONT_CONFIG, SWIPE_CONFIG, Todo


class TodoItem:
    def __init__(
        self, parent: tk.Frame, todo: Todo, owner: Container, *,
            width: int = 390, show_divider: bool = True) -> None:
        self._parent: tk.Frame = parent
        self._owner: Container = owner
        self._show_divider: bool = show_divider

        self._todo: Todo = todo

        self._reminder_str: str = ""
        self._expired: bool = False

        # Core UI containers
        self._wrapper: tk.Frame = tk.Frame(
            parent, bg=COLORS["background"], height=SWIPE_CONFIG["placeholder_height"], width=width
        )
        self._wrapper.pack(fill="x", pady=0)
        # self._wrapper.todo_id = todo_dict["tid"]

        self._content_frame: tk.Frame = tk.Frame(
            self._wrapper, bg=COLORS["background"], height=SWIPE_CONFIG["placeholder_height"], width=width
        )
        self._content_frame.place(x=0, y=0, relwidth=1.0)

        # State variables
        self._is_delete_btn_visible: bool = False

        self._last_nearest_index: int = -1

        self._edit_mode: bool = False
        self._edit_entry: tk.Entry | None = None
        self._editing: bool = False

        # Create UI components
        self._create_left_area()
        self._create_right_buttons()
        self._create_delete_button()
        self._create_divider()
        self._bind_events()

        self._expired = self._is_reminder_expired(self._todo)
        self._reminder_str = self._get_reminder_str(self._todo)
        self._update_text_display(self._reminder_str, self._expired)

    @property
    def todo(self):
        return self._todo

    @todo.setter
    def todo(self, val: Todo):
        self._todo = val
        pv(self._todo)

    def _create_left_area(self) -> None:
        self._left_area: tk.Frame = tk.Frame(
            self._content_frame, bg=COLORS["background"], height=SWIPE_CONFIG["placeholder_height"]
        )
        self._left_area.pack(side="left", fill="both", expand=True)
        _ = self._left_area.pack_propagate(False)

        self._checkbox: RoundCheckbutton = RoundCheckbutton(
            self._left_area, callback=self._on_toggle_completed
        )

        self._text_container: tk.Frame = tk.Frame(self._left_area, bg=COLORS["background"])
        self._text_container.pack(side="left", fill="both", expand=True)

    def _create_right_buttons(self) -> None:
        self._btn_container: tk.Frame = tk.Frame(
            self._content_frame, bg=COLORS["background"], width=80, height=SWIPE_CONFIG["placeholder_height"]
        )
        self._btn_container.pack(side="right", padx=5, pady=0, fill="y")
        _ = self._btn_container.pack_propagate(False)

        # More options button
        self._more_btn: tk.Button = tk.Button(
            self._btn_container, text="⋮", font=("Arial", 14, "bold"), bg=COLORS["background"],
            fg=COLORS["accent"], borderwidth=0, relief="flat", width=2, height=2)
        _ = self._more_btn.configure(command=lambda: self._on_open_detail(self._more_btn.winfo_rootx(),
            self._more_btn.winfo_rooty()))
        # self._more_btn.pack(side="top", padx=2, pady=5)
        self._more_btn.pack_forget()

        # Edit-mode delete button
        self._edit_delete_btn: tk.Button = tk.Button(
            self._btn_container, text="Delete", font=FONT_CONFIG["small"], bg=COLORS["background"],
            fg=COLORS["danger"], borderwidth=0, width=4, command=self.delete
        )
        if self._edit_mode:
            self._edit_delete_btn.pack(side="top", padx=2, pady=2)
        else:
            self._edit_delete_btn.pack_forget()

    def _create_delete_button(self) -> None:
        self._delete_btn: tk.Button = tk.Button(
            self._wrapper, text="Delete", font=FONT_CONFIG["small"], bg=COLORS["danger"],
            fg="white", borderwidth=0, command=self.delete, width=10, state="disabled"
        )
        self._delete_btn.place(
            x=400, y=0, width=SWIPE_CONFIG["delete_btn_width"], height=SWIPE_CONFIG["placeholder_height"]
        )

    def _create_divider(self) -> None:
        if self._show_divider:
            self._divider: tk.Frame = tk.Frame(
                self._wrapper, bg=COLORS["border"], height=1, width=400 - 30
            )
            self._divider.place(x=30, y=SWIPE_CONFIG["placeholder_height"]-1)

    def _bind_events(self) -> None:
        # Text edit event
        _ = self._text_container.bind("<Button-1>", self._on_text_click)

    def _on_text_click(self, _: tk.Event) -> str:
        if self._editing:
            return "break"

        self._switch_to_edit_mode()
        return "break"

    def _switch_to_edit_mode(self) -> None:
        if self._editing:
            return

        # Clear text container
        for widget in self._text_container.winfo_children():
            widget.destroy()

        self._editing = True

        _ = self._owner.process_message("StartEdit", tid=self._todo["tid"])

        # Create edit entry
        original_width: int = int((400 - 100) / 8)
        new_width: int = int(original_width * (2/3))

        self._edit_entry = tk.Entry(
            self._text_container, font=(FONT_CONFIG["body"][0], FONT_CONFIG["body"][1], "bold"),
            bg="white", fg=COLORS["primary_text"], relief="solid", bd=1,
            highlightthickness=1, highlightcolor=COLORS["accent"], width=new_width
        )
        self._edit_entry.pack(side="left", fill="x", expand=False, padx=5, pady=10)
        self._edit_entry.insert(0, self._todo["data"]["name"])
        self._edit_entry.select_range(0, tk.END)
        self._edit_entry.focus_force()

        self._more_btn.pack(side="top", padx=2, pady=5)

        # Bind save/cancel
        _ = self._edit_entry.bind("<Return>", lambda e: self.save_edit())
        _ = self._edit_entry.bind("<FocusOut>", lambda e: self.save_edit())
        _ = self._edit_entry.bind("<Escape>", lambda e: self.cancel_edit())

    def save_edit(self) -> None:
        if not self._edit_entry:
            return

        self._editing = False

        self._more_btn.pack_forget()

        new_text: str = self._edit_entry.get().strip()
        if not new_text:
            new_text = "Unnamed todo"

        # Update data
        self._todo["data"]["name"] = new_text
        # self._app.save_todos()

        # Refresh display
        # self._update_text_display()
        self._update_text_display(self._reminder_str, self._expired)
        # self._owner.update_stats()

        _ = self._owner.process_message("SaveEdit", tid=self._todo["tid"])

    def cancel_edit(self) -> None:
        self._editing = False

        self._more_btn.pack_forget()

        # self._update_text_display()
        self._update_text_display(self._reminder_str, self._expired)

        _ = self._owner.process_message("CancelEdit", tid=self._todo["tid"])

    def _is_reminder_expired(self, todo: Todo) -> bool:
        tududata = todo["data"]
        if tududata["reminder_id"] <= 0:
            return False

        reminder_info = tududata["reminder_infos"][todo["reminder_idx"]]
        reminder_time = reminder_info["clock_time"]
        reminder_dtime = datetime.datetime.combine(todo["day"], reminder_time)

        return reminder_dtime < datetime.datetime.now()

    def _update_text_display(self, reminder_str: str, is_expired: bool = False, is_completed: bool = False):
        # Clear text container
        for widget in self._text_container.winfo_children():
            widget.destroy()

        # Text styling
        text_color = COLORS["secondary_text"] \
            if is_completed else COLORS["primary_text"]
        strike: str = "overstrike" if is_completed else "normal"

        # Main text frame
        text_frame: tk.Frame = tk.Frame(self._text_container, bg=COLORS["background"])
        text_frame.pack(side="left", fill="both", expand=True, padx=5, pady=2)

        # title
        name_label: tk.Label = tk.Label(
            text_frame, text=self._todo["data"]["name"],
            font=(FONT_CONFIG["body"][0], FONT_CONFIG["body"][1], "bold", strike),
            bg=COLORS["background"], fg=text_color, anchor="w", wraplength=280, justify="left"
        )
        name_label.pack(side="top", fill="x", anchor="w")

        # Note text
        note_label: tk.Label = tk.Label(
            text_frame, text=self._todo.get("note", ""),
            font=(FONT_CONFIG["small"][0], FONT_CONFIG["small"][1], strike),
            bg=COLORS["background"], fg=COLORS["secondary_text"], anchor="w", wraplength=280, justify="left"
        )
        if self._todo.get("note", "").strip():
            note_label.pack(side="top", fill="x", anchor="w", pady=(0, 1))
        else:
            note_label.pack_forget()

        reminder_color: str = COLORS["danger"] if is_expired else COLORS["secondary_text"]

        reminder_label: tk.Label = tk.Label(
            text_frame, text=reminder_str,
            font=(FONT_CONFIG["small"][0], FONT_CONFIG["small"][1], strike),
            bg=COLORS["background"], fg=reminder_color, anchor="w", wraplength=280, justify="left"
        )
        reminder_label.pack(side="top", fill="x", anchor="w")

        # Bind edit events
        for widget in [text_frame, name_label, note_label, reminder_label]:
            _ = widget.bind("<Button-1>", self._on_text_click)
            _ = widget.bind("<B1-Motion>", lambda e: "break")

    def _get_reminder_str(self, todo: Todo):
        if todo["data"]["reminder_id"] !=0 :
            reminder_info = todo["data"]["reminder_infos"][todo["reminder_idx"]]
            reminder_time = reminder_info["clock_time"]
            clock_str= time2str(reminder_time)
            cyc_str, _ = reminder2str(todo["data"]["reminder"])
            reminder_str = f"Remind: {clock_str} 🔁 {cyc_str[:-5]}"
        else:
            reminder_str = "No reminder"
        return reminder_str

    def _on_toggle_completed(self) -> None:
        # if self._owner._editing_todo_id == self._todo_dict["tid"]:
        #     self.cancel_edit()
        self.cancel_edit()

        reminder_idx = self._todo["reminder_idx"]
        tududata = self._todo["data"]
        tududata["reminder_infos"][reminder_idx]["completed"] = True

        self._update_text_display(self._reminder_str, self._expired, True)

        # Notify to owner
        _ = self._owner.process_message("CompleteTodo", todo=self._todo)

        # if self._todo["reminder_idx"] == -1:
        #     # _ = self._owner.process_message("CompleteTodo", todo=self._todo)
        #     pass
        # else:
        #     self._expired = self._is_reminder_expired(self._todo)
        #     self._reminder_str = self._get_reminder_str(self._todo)
        #     self._update_text_display(self._reminder_str, self._expired)

    def delete(self) -> None:
        # Confirm deletion in edit mode
        if self._edit_mode and not messagebox.askyesno("Confirmation", "Are you sure to delete this todo?"):
            return

        # Notify to owner
        # self._owner.delete_todo_by_id(self._todo_dict["tid"])

    def _on_open_detail(self, x: int, y: int) -> None:
        if self._editing:
            self.cancel_edit()
        _ = self._owner.process_message("OpenEditTodoDlg", mousepos=[x,y], todo=self._todo)
        # pv(self._todo_dict)

    def update_edit_mode(self) -> None:
        if self._edit_mode:
            self._edit_delete_btn.pack(side="top", padx=2, pady=2)
        else:
            self._edit_delete_btn.pack_forget()

    # TODO
    def tick(self) -> None:
        # calc status
        pass
        # self._checkbox.set_checked(updated_data["status"] == StatusEnum.COMPLETED)
        # self._update_text_display()
