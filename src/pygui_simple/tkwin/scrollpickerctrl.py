#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import calendar
import datetime
import tkinter as tk
import xml.etree.ElementTree as et
from collections.abc import Callable
from typing import Any, TypeVar, cast, override

from pygui_simple.tkwin.dialogctrl import DialogCtrl
from pygui_simple.tkwin.labelctrl import LabelCtrl
from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import Widget, WidgetRegistry, WinBasic

T = TypeVar("T", bound=int | str)

class ScrollPicker[T](tk.Frame):
    def __init__(self, master: tk.Tk | tk.Frame,
            val_list: list[T],
            initial: T | None = None,
            on_select: Callable[[T], None] | None = None,
            **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._master: tk.Tk | tk.Frame = master

        self._val_list: list[T] = val_list
        self._on_select: Callable[[T], None] | None = on_select
        if initial:
            self._selected_data: T = initial
            try:
                self._index: int = self._val_list.index(initial)
            except ValueError:
                self._index = 0
        else:
            self._selected_data = val_list[0]
            self._index = 0

        self._background: str = cast(str, kwargs.get('background', 'white'))

        # Create UI components
        self._create_widgets()
        # Bind mouse events
        self._bind_mouse_scroll()
        # Initialize preview content
        self._update_previews()

        self._data_up2: tk.Label
        self._data_up1: tk.Label
        self._data_label: tk.Label
        self._data_down1: tk.Label
        self._data_down2: tk.Label

    @property
    def data(self):
        return self._selected_data

    def _create_widgets(self) -> None:
        # Configure grid weights for a cleaner layout
        for i in range(5):  # row
            _ = self.grid_rowconfigure(i, weight=1)
        for i in range(1):  # column
            _ = self.grid_columnconfigure(i, weight=1)

        # Top Preview (+2)
        self._data_up2 = tk.Label(self, font=("SimHei", 10), fg="#888888", width=6,
            bg=self._background,
            anchor="center")
        self._data_up2.grid(row=0, column=0)

        # Top Preview (+1)
        self._data_up1 = tk.Label(self, font=("SimHei", 12), fg="#555555", width=6,
            bg=self._background,
            anchor="center")
        self._data_up1.grid(row=1, column=0)

        # Current selected value
        self._data_label = tk.Label(
            self,
            text=str(self._selected_data),
            font=("SimHei", 16, "bold"),
            relief="solid",
            width=8,
            height=2,
            anchor="center",
            bg=self._background
        )
        self._data_label.grid(row=2, column=0, padx=10)

        # Bottom Preview (-1)
        self._data_down1 = tk.Label(self, font=("SimHei", 12), fg="#555555", width=6,
            bg=self._background,
            anchor="center")
        self._data_down1.grid(row=3, column=0)

        # Bottom Preview (-2)
        self._data_down2 = tk.Label(self, font=("SimHei", 10), fg="#888888", width=6,
            bg=self._background,
            anchor="center")
        self._data_down2.grid(row=4, column=0)

    def _bind_mouse_scroll(self) -> None:
        """ Bind mouse wheel events"""

        scrollable_data_widgets = [self._data_label, self._data_up1, self._data_up2,
            self._data_down1, self._data_down2]
        for widget in scrollable_data_widgets:
            _ = widget.bind("<MouseWheel>", self._on_data_scroll)
            _ = widget.bind("<Button-4>", self._on_data_scroll)
            _ = widget.bind("<Button-5>", self._on_data_scroll)

        # Hover effect
        _ = self._data_label.bind("<Enter>", self._on_enter)
        _ = self._data_label.bind("<Leave>", self._on_leave)

    def _on_enter(self, event: tk.Event[tk.Label]) -> None:
        """ Change style when the mouse enters"""
        if hasattr(event.widget, 'config'):
            _ = event.widget.config(bg="#e0f0ff")

    def _on_leave(self, event: tk.Event[tk.Label]) -> None:
        """ Restore style when the mouse leaves"""
        if hasattr(event.widget, 'config'):
            _ = event.widget.config(bg="white")

    def _update_previews(self) -> None:
        self._data_label["text"] = self._selected_data

        """ Update top and bottom preview content"""
        # Top Preview (+1 and +2, capped by upper limit)
        up1 = self._get_data(self._index + 1)
        up2 = self._get_data(self._index + 2)

        # Bottom Preview (-1 & -2, capped by lower limit)
        down1 = self._get_data(self._index - 1)
        down2 = self._get_data(self._index - 2)

        _ = self._data_up2.config(text=str(up2))
        _ = self._data_up1.config(text=str(up1))
        _ = self._data_down1.config(text=str(down1))
        _ = self._data_down2.config(text=str(down2))

    def _on_data_scroll(self, event: tk.Event) -> None:
        """ Handle scrolling"""
        if event.delta > 0 or getattr(event, 'num', 0) == 4:  # Increase on scroll up
            self._selected_data = self._get_data(self._index + 1, True)
        else:  # Decrease on scroll down
            self._selected_data = self._get_data(self._index - 1, True)

        _ = self._data_label.config(text=str(self._selected_data))

        self._update_previews()

        if self._on_select is not None:
            self._on_select(self._selected_data)

    def _get_data(self, index: int, update_index: int = False):
        val_len  = len(self._val_list)
        if index >= val_len:
            index -= val_len
        elif index < 0:
            index += val_len
        if update_index:
            self._index = index
        return self._val_list[index]

    def update_data(self, data: T):
        self._selected_data = data
        print(f"data = {data}")
        self._index = self._val_list.index(self._selected_data)
        self._update_previews()

    def update_val_list(self, val_list: list[T]):
        self._val_list = val_list
        self._update_previews()

class ScrollPickerCtrl[T](tkControl):
    def __init__(self, parent: Widget,
            width: int, height: int,
            val_list: list[T], *,
            initial: T | None = None,
            background: str = "white",
            callback: Callable[[T], None] | None = None):
        master: tk.Misc = cast(tk.Misc, parent.control)

        self._frame: tk.Frame = tk.Frame(master,
            background=background,
            width=width, height=height)
        super().__init__(self._frame)

        self._scrollpicker: ScrollPicker[T] = ScrollPicker[T](self._frame, val_list,
            initial, self.on_val_change,
            background=background
        )

        self._selected_val: T = initial if initial else val_list[0]

        # Create UI components
        self._create_widgets()

        self._callback: Callable[[T], None] | None = callback

    @property
    def scrollpicker(self):
        return self._scrollpicker

    def _create_widgets(self) -> None:
        _ = self._frame.grid_rowconfigure(0, weight=1)
        _ = self._frame.grid_columnconfigure(0, weight=1)

        self._scrollpicker.grid(row=0, column=1)

    def on_val_change(self, val: T):
        self._selected_val = val
        if self._callback:
            self._callback(val)

    def get_val(self):
        """ Get currently selected value"""
        return self._selected_val

class DateScrollPickerDialog(DialogCtrl):
    def __init__(self, parent: WinBasic, point: tuple[int, int] | None = None,
            title: str = "", initial: str = ""):
        self._title: str = title if title else "Date picker"
        
        super().__init__(parent, title, 300, 190)

        # Initial date setting
        if not initial:
            today = datetime.datetime.now().date()
            self._selected_year: int = today.year
            self._selected_month: int = today.month
            self._selected_day: int = today.day
        else:
            today_list = initial.split("-")
            self._selected_year = int(today_list[0])
            self._selected_month = int(today_list[1])
            self._selected_day = int(today_list[2])

        self._result_var: tk.StringVar = tk.StringVar()

        if point:
            x, y = point
        else:
            x, y = 0, 0
        self.do_show(parent, x, y)

    @override
    def _construct_children(self):
        year_list = list(range(1970, 2101))
        self._year_scrollpicker: ScrollPickerCtrl[int] = ScrollPickerCtrl[int](self._main_frame, 0, 0,
            year_list, initial=self._selected_year,
            callback=self._on_year_change)
        self._idctrl_dict["scpYear"] = self._year_scrollpicker

        month_list  = list(range(1, 13))
        self._month_scrollpicker: ScrollPickerCtrl[int] = ScrollPickerCtrl[int](self._main_frame, 0, 0,
            month_list, initial=self._selected_month,
            callback=self._on_month_change)
        self._idctrl_dict["scpMonth"] = self._month_scrollpicker

        day_list = list(range(1, 32))
        self._day_scrollpicker: ScrollPickerCtrl[int] = ScrollPickerCtrl[int](self._main_frame, 0, 0,
            day_list, initial=self._selected_day,
            callback=self._on_day_change)
        self._idctrl_dict["scpDay"] = self._day_scrollpicker

        # for i in range(3):  # row
        #     _ = cast(tk.Widget, self._main_frame.control).grid_rowconfigure(i, weight=1)
        # for i in range(3):  # column
        #     _ = cast(tk.Widget, self._main_frame.control).grid_columnconfigure(i, weight=1)

        cast(tk.Widget, self._year_scrollpicker.control).grid(row=0, column=0)
        cast(tk.Widget, self._month_scrollpicker.control).grid(row=0, column=1)
        cast(tk.Widget, self._day_scrollpicker.control).grid(row=0, column=2)

        self._result_var.set(f"Current selection: {self._selected_year}-{self._selected_month:02d}-{self._selected_day:02d}")
        result_label = LabelCtrl(self._main_frame, "", textvariable=self._result_var, font=("SimHei", 12))
        cast(tk.Widget, result_label.control).grid(row=3, column=0, columnspan=3, pady=5)
        self._idctrl_dict["lblDateResull"] = result_label
        return super()._construct_children()

    def _on_year_change(self, year: int):
        self._selected_year = year
        self._adjust_day_range()
        self._update_result_preview()

    def _on_month_change(self, month: int):
        self._selected_month = month
        self._adjust_day_range()
        self._update_result_preview()

    def _on_day_change(self, day: int):
        self._selected_day = day
        self._update_result_preview()

    def _get_max_day(self) -> int:
        """ Get maximum days of the selected month"""
        return calendar.monthrange(self._selected_year, self._selected_month)[1]

    def _adjust_day_range(self):
        """ Adjust date to fit selected year and month"""
        max_day = self._get_max_day()
        if self._selected_day > max_day:
            self._selected_day = max_day
            self._day_scrollpicker.scrollpicker.update_data(self._selected_day)
        day_list = list(range(1, max_day))
        self._day_scrollpicker.scrollpicker.update_val_list(day_list)

    def _update_result_preview(self):
        """ Update result preview"""
        formatted_date: str = f"{self._selected_year}-{self._selected_month:02d}-{self._selected_day:02d}"
        self._result_var.set(f"Current selection: {formatted_date}")

    @override
    def _confirm(self, **kwargs: object):
        """ Record the finally selected date"""
        formatted_date: str = f"{self._selected_year}-{self._selected_month:02d}-{self._selected_day:02d}"
        self._result_var.set(f"Selected: {formatted_date}")
        self.destroy()

    def get_datestr(self) -> str:
        """ Get currently selected date string"""
        return f"{self._selected_year}-{self._selected_month:02d}-{self._selected_day:02d}"

class TimeScrollPickerCtrl(tkControl):
    def __init__(self, parent: Widget,
            width: int, height: int, *,
            stp: int = 0,
            background: str = "white",
            title: str = "", initial: str = "",
            callback: Callable[[datetime.time], None] | None = None):
        master = cast(tk.Misc, parent.control)
        self._stp: int = stp

        self._selected_hour: int = 0
        self._selected_minute: int = 0

        self._frame: tk.Frame = tk.Frame(master,
            background=background,
            width=width, height=height)
        super().__init__(self._frame)

        # self.set_initial(initial)
        if not initial:
            now: datetime.datetime = datetime.datetime.now()
            self._selected_hour = now.hour
            self._selected_minute = now.minute
        else:
            now_list = initial.split(":")
            self._selected_hour = int(now_list[0])
            self._selected_minute = int(now_list[1])

        stp_hour, stp_minute = divmod(stp, 60)

        print(f"step: {stp_hour} {stp_minute}")

        if stp_hour:
            hour_list = list(range(0, 24, stp_hour))
            self._selected_hour = (self._selected_hour // stp_hour) * stp_hour
        else:
            hour_list = list(range(24))
        print(f"hour_list :{hour_list}")
        self._hour_scrollpicker: ScrollPicker[int] = ScrollPicker[int](self._frame,
            hour_list, self._selected_hour,
            self._on_hour_change,
            background=background
        )

        if stp_minute:
            minute_list = list(range(0, 60, stp_minute))
            self._selected_minute = (self._selected_minute // stp_minute) * stp_minute
        else:
            minute_list = list(range(60))
        print(f"minute_list :{minute_list}")
        self._minute_scrollpicker: ScrollPicker[int] = ScrollPicker(self._frame,
            minute_list, self._selected_minute,
            self._on_minute_change,
            background=background
        )

        self._result_var: tk.StringVar = tk.StringVar()

        # Create UI components
        self._create_widgets()

        self._callback: Callable[[datetime.time], None] | None = callback

    def _create_widgets(self) -> None:
        # Configure grid weights for better layout
        for i in range(1):  # row
            _ = self._frame.grid_rowconfigure(i, weight=1)
        for i in range(2):  # column
            _ = self._frame.grid_columnconfigure(i, weight=1)

        self._hour_scrollpicker.grid(row=0, column=1)
        self._minute_scrollpicker.grid(row=0, column=2)

        self._result_var = tk.StringVar()
        self._result_var.set(f"Current selection: {self._selected_hour:02d}:{self._selected_minute:02d}")

    def _on_hour_change(self, hour: int):
        self._selected_hour = hour
        self._update_result_preview()
        time = datetime.time(self._selected_hour, self._selected_minute)
        self.on_time_change(time)

    def _on_minute_change(self, minute: int):
        self._selected_minute = minute
        self._update_result_preview()
        time = datetime.time(self._selected_hour, self._selected_minute)
        self.on_time_change(time)

    def on_time_change(self, time: datetime.time):
        if self._callback:
            self._callback(time)

    def _update_result_preview(self) -> None:
        """ Update result preview"""
        formatted_time: str = f"{self._selected_hour:02d}:{self._selected_minute:02d}"
        self._result_var.set(f"Selected: {formatted_time}")

    def set_initial(self, initial: str = ""):
        if not initial:
            now: datetime.datetime = datetime.datetime.now()
            self._selected_hour = now.hour
            self._selected_minute = now.minute
        else:
            now_list = initial.split(":")
            self._selected_hour = int(now_list[0])
            self._selected_minute = int(now_list[1])
        stp_hour, stp_minute = divmod(self._stp, 60)
        if stp_hour:
            self._selected_hour = (self._selected_hour // stp_hour) * stp_hour
        if stp_minute:
            self._selected_minute = (self._selected_minute // stp_minute) * stp_minute
        self._hour_scrollpicker.update_data(self._selected_hour)
        self._minute_scrollpicker.update_data(self._selected_minute)

    def get_time(self):
        """ Get currently selected time"""
        return datetime.time(self._selected_hour, self._selected_minute)

    def get_timestr(self) -> str:
        """ Get currently selected time string"""
        return f"{self._selected_hour:02d}:{self._selected_minute:02d}"

class TimeScrollPickerDialog(DialogCtrl):
    def __init__(self, parent: WinBasic, point: tuple[int, int] | None = None, *, stp: int = 0,
            title: str = "", initial: str = ""):
        title = title if title else "Time Picker"
        self._stp: int = stp
        super().__init__(parent, title, 250, 190)

        # Initial time setting
        if not initial:
            now: datetime.datetime = datetime.datetime.now()
            self._selected_hour: int = now.hour
            self._selected_minute: int = now.minute
        else:
            now_list = initial.split(":")
            self._selected_hour = int(now_list[0])
            self._selected_minute = int(now_list[1])

        self._result_var: tk.StringVar = tk.StringVar()
        self._result_var.set(f"Current selection: {self._selected_hour:02d}:{self._selected_minute:02d}")

        if point:
            x, y = point
        else:
            x, y = 0, 0
        self.do_show(parent, x, y)

    @override
    def _construct_children(self):
        self._time_scrollpicker: TimeScrollPickerCtrl = TimeScrollPickerCtrl(
            self._main_frame,
            100, 50,
            stp=self._stp,
            initial=f"{self._selected_hour}:{self._selected_minute}"
        )
        cast(tk.Widget, self._time_scrollpicker.control).pack(pady=5)
        self._idctrl_dict["tspTimePicker"] = self._time_scrollpicker

        # result_label = ttk.Label(self._frame, textvariable=self._result_var, font=("SimHei", 12))
        result_label = LabelCtrl(self._main_frame, "", textvariable=self._result_var, font=("SimHei", 12))
        cast(tk.Widget, result_label.control).pack(pady=(5,0))
        self._idctrl_dict["tspTimePicker"] = result_label

        return super()._construct_children()

    def get_time(self):
        """ Get currently selected time"""
        return self._time_scrollpicker.get_time()

    def get_timestr(self) -> str:
        """ Get currently selected time string"""
        return self._time_scrollpicker.get_timestr()

    def _exit(self):
        assert self._top is not None
        topctrl = cast(tk.Toplevel, self._top.control)
        topctrl.grab_release()
        topctrl.destroy()

@WidgetRegistry.register("ScrollPicker")
class tkScrollPickerCtrl(tkControl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        typ = __builtins__.get(attr_dict["type"], int)
        initial = attr_dict.get("initial", None)
        bg = attr_dict.get("background", "white")
        if 'value_list' in options:
            val_list = [typ(v) for v in options["value_list"]]
        else:
            start = cast(int, options["start"])
            end = cast(int, options['end'])
            val_list = list(range(start, end+1))
        ctrl = ScrollPickerCtrl[typ](parent,
            int(attr_dict["width"]), int(attr_dict["height"]), val_list, initial=initial, background=bg,
            callback=self.on_val_change)

        super().__init__(cast(tk.Widget, ctrl.control))

        if "id" in attr_dict:
            self._idctrl: str = attr_dict["id"]
        else:
            raise RuntimeError("No id")

        self._owner: WinBasic = owner

    def on_val_change(self, val: object):
        _ = self._owner.process_message(self._idctrl, event="SelectValue", val=val)

@WidgetRegistry.register("TimeScrollPicker")
class tkTimeScrollPickerCtrl(TimeScrollPickerCtrl):
    def __init__(self, parent: Widget, ctrl_cfg: et.Element, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        options: dict[str, Any] = {}
        if "options" in attr_dict:
            options = eval(attr_dict["options"])

        super().__init__(parent, **options)

        self._owner: WinBasic = owner
        if "id" in attr_dict:
            self._idctrl: str = attr_dict["id"]
        else:
            raise RuntimeError("No id")

    @override
    def on_time_change(self, time: datetime.time):
        _ = self._owner.process_message(self._idctrl, event="SelectTime", val=time)
        return super().on_time_change(time)
