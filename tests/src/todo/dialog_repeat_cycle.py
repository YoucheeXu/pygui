from __future__ import annotations

import tkinter as tk
import xml.etree.ElementTree as et
from functools import partial
from tkinter import ttk
from typing import cast, override

from pygui_simple.tkwin.dialogctrl import DialogCtrl, tkDialogCtrl
from pygui_simple.tkwin.tkcontrols import (
    FrameCtrl,
    LabelCtrl,
    ScrollPickerCtrl,
)
from pygui_simple.winbasic import Widget, WinBasic, on_message

from src.database.time_database_type import TimeUnit


class RepeatCycleDlg(tkDialogCtrl):
    def __init__(self, parent: Widget, dlg_cfg: et.Element, owner: WinBasic):
        super().__init__(parent, dlg_cfg, owner)

        # Weekday list
        self.weekdays: list[str] = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        self.selected_weekdays: set[int] = {0}  # Default: select Monday
        self.checkmark_labels: list[ttk.Label] = []  # Store references for dynamic updates

        # Date grid (1-31)
        self.date_labels: dict [int, ttk.Label] = {}  # Store references to date labels for updates
        self.selected_dates: set[int] = set()  # 存储所有选中的日期，支持多选
        self.selected_dates.add(19)  # 默认选中19号（与截图一致）

    def _configure_styles(self):
        """ Configure iOS-inspired ttk styles for the interface"""
        style = ttk.Style()
        # style.theme_use("default")

        # Card container style (white background, no border)
        # style.configure(
        #     "Card.TFrame",
        #     background="white",
        #     relief=tk.FLAT,
        #     borderwidth=0
        # )

        style.configure(
            "CardLabel.TLabel",
            background="white",
            font=("Helvetica", 16)  # Fallback cross-platform font
        )

        style.configure(
            "WeekdayLabel.TLabel",
            background="white",
            font=("Helvetica", 16)
        )
        style.configure(
            "CheckmarkLabel.TLabel",
            background="white",
            font=("Helvetica", 16),
            foreground="#007aff"
        )

        # Date number styles
        style.configure(
            "DateNormal.TLabel",
            background="white",
            foreground="black",
            font=("Helvetica", 18),
            anchor=tk.CENTER
        )
        style.configure(
            "DateSelected.TLabel",
            background="#007aff",
            foreground="white",
            font=("Helvetica", 18),
            anchor=tk.CENTER
        )

    def _create_weekday_selection_card(self, parent: FrameCtrl):
        """ Create multi-select weekday toggle card"""
        # weekday_card = ttk.Frame(parent.control, style="Card.TFrame", padding=(16, 12, 16, 12))
        # weekday_card.pack(fill=tk.X, padx=16, pady=8)
        weekday_card = cast(tk.Widget, parent.control)
        # _ = weekday_card.grid_columnconfigure(0, weight=1)

        for i, day in enumerate(self.weekdays):
            # Clickable row frame
            row = ttk.Frame(weekday_card, style="Card.TFrame", cursor="hand2")
            row.pack(fill=tk.X, pady=4)

            # Weekday label (left-aligned)
            day_label = ttk.Label(row, text=day, style="WeekdayLabel.TLabel")
            day_label.pack(side=tk.LEFT)

            # Checkmark (right-aligned, only visible when selected)
            checkmark_text = "✓" if i in self.selected_weekdays else ""
            checkmark_label = ttk.Label(row, text=checkmark_text, style="CheckmarkLabel.TLabel")
            checkmark_label.pack(side=tk.RIGHT)
            self.checkmark_labels.append(checkmark_label)

            # Bind click events to all elements in the row
            toggle_callback = partial(self._toggle_weekday, i)
            _ = row.bind("<Button-1>", toggle_callback)
            _ = day_label.bind("<Button-1>", toggle_callback)
            _ = checkmark_label.bind("<Button-1>", toggle_callback)

            # Add divider line (except after last row)
            if i < len(self.weekdays) - 1:
                ttk.Separator(weekday_card, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

    def _toggle_weekday(self, idx: int, _: tk.Event[tk.Widget] | None = None):
        """ Toggle selected state of a weekday when clicked"""
        if idx in self.selected_weekdays:
            # Deselect the weekday
            self.selected_weekdays.remove(idx)
            __ = self.checkmark_labels[idx].config(text="")
        else:
            # Select the weekday
            self.selected_weekdays.add(idx)
            __ = self.checkmark_labels[idx].config(text="✓")

    def _create_date_selection_card(self, parent: FrameCtrl):
        """ Create multi-select date selection card with grid view"""
        date_card = ttk.Frame(cast(tk.Widget, parent.control), style="Card.TFrame", padding=(16, 12, 16, 12))
        date_card.pack(fill=tk.X, padx=16, pady=8)
        # date_card = parent.control

        # "日期" option with checkmark (selected)
        date_option_frame = ttk.Frame(date_card, style="Card.TFrame")
        date_option_frame.pack(fill=tk.X, pady=4)
        ttk.Label(date_option_frame, text="日期", style="CardLabel.TLabel").pack(side=tk.LEFT)
        ttk.Label(date_option_frame, text="✓", style="CheckmarkLabel.TLabel").pack(side=tk.RIGHT)

        # Divider line
        ttk.Separator(date_card, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # "在..." option (placeholder for future use)
        ttk.Label(date_card, text="在...", style="CardLabel.TLabel").pack(anchor=tk.W, pady=4)

        # Divider line before date grid
        ttk.Separator(date_card, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # Create grid frame for dates
        date_grid_frame = ttk.Frame(date_card, style="Card.TFrame")
        date_grid_frame.pack(fill=tk.X, pady=4)

        # Populate dates 1-31 in a 7-column grid
        for day in range(1, 32):
            row = (day - 1) // 7
            col = (day - 1) % 7

            # 根据初始选中状态设置样式
            if day in self.selected_dates:
                label = ttk.Label(
                    date_grid_frame,
                    text=str(day),
                    style="DateSelected.TLabel",
                    width=4,
                    padding=(0, 12),
                    cursor="hand2"  # 保持可点击状态，支持取消选择
                )
            else:
                label = ttk.Label(
                    date_grid_frame,
                    text=str(day),
                    style="DateNormal.TLabel",
                    width=4,
                    padding=(0, 12),
                    cursor="hand2"
                )

            label.grid(row=row, column=col, sticky="nsew")
            self.date_labels[day] = label

            # 绑定点击事件，支持切换选中状态
            _ = label.bind("<Button-1>", lambda e, d=day: self._toggle_date_selection(d))

        # Configure grid weights to make cells equal width
        for col in range(7):
            _ = date_grid_frame.grid_columnconfigure(col, weight=1)

    def _toggle_date_selection(self, day: int):
        """ Toggle selected state of a date (supports multi-select)"""
        label = self.date_labels[day]

        if day in self.selected_dates:
            # 取消选中：从集合中移除，切换为普通样式
            self.selected_dates.remove(day)
            _ = label.config(style="DateNormal.TLabel")
        else:
            # 选中日期：添加到集合中，切换为高亮样式
            self.selected_dates.add(day)
            _ = label.config(style="DateSelected.TLabel")

    @override
    def _beforego(self, **kwargs: object):
        spr_ctrl = cast(ScrollPickerCtrl[int], self.get_control("sprEveryRepeatCycle"))
        spr_ctrl.hide()
        spr_ctrl = cast(ScrollPickerCtrl[str], self.get_control("sprFrqRepeatCycle"))
        spr_ctrl.hide()

        # Configure custom styles
        self._configure_styles()

        cycle_info = cast(str, kwargs["cycle_info"])
        lbl = cast(LabelCtrl, self.get_control(idctrl="lblInfoRepeatCycle"))
        lbl.set_text(cycle_info)

        frm_week = cast(FrameCtrl, self.get_control("frmWeekCustomRepeatCycle"))
        self._create_weekday_selection_card(frm_week)
        frm_week.hide()

        frm_month = cast(FrameCtrl, self.get_control("frmMonthCustomRepeatCycle"))
        self._create_date_selection_card(frm_month)
        frm_month.hide()

    @on_message("lblSelEveryRepeatCycle")
    def on_show_hide_repeatcycle(self, **_: object):
        spr_ctrl = cast(ScrollPickerCtrl[int], self.get_control("sprEveryRepeatCycle"))
        spr_ctrl.hide(spr_ctrl.visible)

    @on_message("sprEveryRepeatCycle")
    def on_moidfy_repeatcycle(self, **kwargs: object):
        val = cast(int, kwargs["val"])
        lbl_every = cast(LabelCtrl, self.get_control("lblSelEveryRepeatCycle"))
        lbl_every.set_text(str(val))
        lbl_info = cast(LabelCtrl, self.get_control(idctrl="lblInfoRepeatCycle"))
        if val == 0:
            lbl_info.set_text("Never")
        else:
            lbl_frq = cast(LabelCtrl, self.get_control("lblSelFrqRepeatCycle"))
            frq = lbl_frq.get_text()

            lbl_info.set_text(f"Every {val} {frq}")

        return True

    @on_message("lblSelFrqRepeatCycle")
    def on_show_hide_frqcylce(self, **_: object):
        spr_ctrl = cast(ScrollPickerCtrl[str], self.get_control("sprFrqRepeatCycle"))
        spr_ctrl.hide(spr_ctrl.visible)

        return True

    @on_message("sprFrqRepeatCycle")
    def on_moidfy_frqcycle(self, **kwargs: object):
        val = cast(str, kwargs["val"])
        lbl_every = cast(LabelCtrl, self.get_control("lblSelFrqRepeatCycle"))
        lbl_every.set_text(val)
        
        frm_week = cast(FrameCtrl, self.get_control("frmWeekCustomRepeatCycle"))
        frm_month = cast(FrameCtrl, self.get_control("frmMonthCustomRepeatCycle"))
        if val == "Week":
            frm_month.hide()
            frm_week.show()
        elif val == "Month":
            frm_week.hide()
            frm_month.show()
        else:
            frm_week.hide()
            frm_month.hide()

        return True

    @override
    def _confirm(self, **kwargs: object):
        # po(f"{self._idself} confirm")
        lbl_info = cast(LabelCtrl, self.get_control(idctrl="lblInfoRepeatCycle"))
        cycle_info = lbl_info.get_text()
        lbl_every = cast(LabelCtrl, self.get_control("lblSelEveryRepeatCycle"))
        every = int(lbl_every.get_text())
        lbl_frq = cast(LabelCtrl, self.get_control("lblSelFrqRepeatCycle"))
        frq = TimeUnit[lbl_frq.get_text().upper()]

        assert self._owner is not None
        _ = self._owner.process_message("ModifyCycle", cycle_info=cycle_info, every=every, frq=frq)

        self.destroy(confirm=True, **kwargs)
  
    @override
    def _cancel(self, **kwargs: object):
        # po(f"{self._idself} cancel")

        self.destroy(confirm=False, **kwargs)
