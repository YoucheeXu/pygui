#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
    uv pip install e .
    uv run .\tests\test_tkwin.py
"""
from __future__ import annotations
from functools import partial
import os
import sys
import random
import datetime
import uuid
import xml.etree.ElementTree as et
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from typing import override, cast

from matplotlib import backend_bases
from matplotlib.colors import to_hex
from matplotlib.container import BarContainer
from matplotlib.patches import Rectangle

from pygui_simple.winbasic import Widget, Container, Dialog, WinBasic
from pygui_simple.tkmatplot import LineData, MatPlotCtrl
from pygui_simple.tkcontrol import tkControl
from pygui_simple.tkwin import LabelCtrl, EntryCtrl, ButtonCtrl, CheckButtonCtrl
from pygui_simple.tkwin import ListboxCtrl, LabelFrameCtrl, ScrollableFrameCtrl
from pygui_simple.tkwin import PicsListviewCtrl, FrameCtrl, DialogCtrl, tkWin
from pygui_simple.tkwin import CanvasCtrl
from pygui_simple.tkslideswitch import SlideSwitchCtrl
from pygui_simple.tkcalendar import CalendarCtrl, CalendarDialog
from pygui_simple.tkscrollpicker import ScrollPickerCtrl, TimeScrollPickerCtrl, TimeScrollPickerDialog


class RepeatCycleDlg(DialogCtrl):
    def __init__(self, app: WinBasic, dlg_cfg: et.Element):
        super().__init__(app, dlg_cfg)

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
        weekday_card = parent.control
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
        date_card = ttk.Frame(parent.control, style="Card.TFrame", padding=(16, 12, 16, 12))
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

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        # kwargs.update(self._extral_msg)
        if self.alive:
            match idmsg:
                case "lblSelEveryRepeatCycle":
                    spr_ctrl = cast(ScrollPickerCtrl[int], self.get_control("sprEveryRepeatCycle"))
                    spr_ctrl.hide(spr_ctrl.visible)
                case "sprEveryRepeatCycle":
                    val = cast(int, kwargs["val"])
                    lbl_ctrl = cast(LabelCtrl, self.get_control("lblSelEveryRepeatCycle"))
                    lbl_ctrl.set_text(str(val))
                case "lblSelFrqRepeatCycle":
                    spr_ctrl = cast(ScrollPickerCtrl[str], self.get_control("sprFrqRepeatCycle"))
                    spr_ctrl.hide(spr_ctrl.visible)
                case "sprFrqRepeatCycle":
                    val = cast(str, kwargs["val"])
                    lbl_ctrl = cast(LabelCtrl, self.get_control("lblSelFrqRepeatCycle"))
                    lbl_ctrl.set_text(val)
                    
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
                case _:
                    print(f"undeal with idMsg of RepeatCyclekDlg: {idmsg} with {kwargs}")
                    return super().process_message(idmsg, **kwargs)
            return True
        return super().process_message(idmsg, **kwargs)                    

    @override
    def _confirm(self, **kwargs: object):
        # po(f"{self._idself} confirm")
        return True, ""

    @override
    def _cancel(self, **kwargs: object):
        # po(f"{self._idself} cancel")
        return True, ""

class TodoDetailDlg(DialogCtrl):
    def __init__(self, app: tkWin, dlg_cfg: et.Element):
        super().__init__(app, dlg_cfg)

    @override
    def _beforego(self, **kwargs: object):

        sls_date = cast(SlideSwitchCtrl, self.get_control("slsDateEditTodo"))
        sls_date.set_state(True)
        calendar = cast(CalendarCtrl, self.get_control("cadDateEditTodo"))
        calendar.hide()

        sls_time = cast(SlideSwitchCtrl, self.get_control("slsTimeEditTodo"))
        sls_time.set_state(True)
        time_scrollerpicker_ctrl = cast(TimeScrollPickerCtrl, self.get_control("tspTimeEditTodo"))
        time_scrollerpicker_ctrl.hide()

        calendar = cast(CalendarCtrl, self.get_control("cadEndEditTodo"))
        calendar.hide()

    @override
    def _confirm(self, **kwargs: object):
        # po(f"{self._idself} confirm")
        return True, ""

    @override
    def _cancel(self, **kwargs: object):
        # po(f"{self._idself} cancel")
        return True, ""

    def show_repeatcycledlg(self, owner: Dialog | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        dlg_id = "dlgRepeatCycle"
        dlg_cfg = self._app.get_customctrlcfg(dlg_id)
        dlg = RepeatCycleDlg(self._app, dlg_cfg)
        # self._gui.register_customctrl(dlg_id, recordhour_dlg)
        dlg.do_show(owner, x+20, y+20, **kwargs)

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        # kwargs.update(self._extral_msg)
        if self.alive:
            match idmsg:
                case "lblSelDateEditTodo":
                    lbl = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
                    calendar = cast(CalendarCtrl, self.get_control("cadDateEditTodo"))
                    if lbl.get_text():
                        calendar.hide(calendar.visible)
                        # slideswitch = cast(SlideSwitchCtrl, self.get_control("slsDateEditTodo"))
                        # slideswitch.set_state(calendar.visible)
                case "slsDateEditTodo":
                    val = cast(bool, kwargs['val'])
                    calendar = cast(CalendarCtrl, self.get_control("cadDateEditTodo"))
                    if not val:
                        calendar.cancel_select()
                        lbl = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
                        lbl.set_text("")
                    calendar.hide(not val)
                case "cadDateEditTodo":
                    lbl = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
                    date = cast(datetime.date, kwargs['val'])
                    # date_text = f"{date.year}年{date.month:02d}月{date.day:02d}日"
                    date_text = date.strftime("%B %d, %Y\t%A")
                    # print(f"select date: {date_text}")
                    lbl.set_text(date_text)
                case "lblSelTimeEditTodo":
                    lbl = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
                    time_scrollerpicker_ctrl = cast(TimeScrollPickerCtrl, self.get_control("tspTimeEditTodo"))
                    if lbl.get_text():
                        time_scrollerpicker_ctrl.hide(time_scrollerpicker_ctrl.visible)
                        # slideswitch = cast(SlideSwitchCtrl, self.get_control("slsDateEditTodo"))
                        # slideswitch.set_state(calendar.visible)
                case "slsTimeEditTodo":
                    val = cast(bool, kwargs['val'])
                    time_scrollerpicker_ctrl = cast(TimeScrollPickerCtrl, self.get_control("tspTimeEditTodo"))
                    if not val:
                        lbl = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
                        lbl.set_text("")
                    time_scrollerpicker_ctrl.hide(not val)
                case "tspTimeEditTodo":
                    lbl = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
                    time = cast(datetime.time, kwargs['val'])
                    # date_text = f"{date.year}年{date.month:02d}月{date.day:02d}日"
                    time_text = time.strftime("%H:%M")
                    # print(f"select date: {date_text}")
                    lbl.set_text(time_text)
                case "lblSelCycleEditTodo":
                    lbl = cast(LabelCtrl, self.get_control(idctrl="lblSelCycleEditTodo"))
                    cycle_info = lbl.get_text()
                    x, y = cast(tuple[int, int], kwargs["mousepos"])
                    return self.show_repeatcycledlg(self, x+20, y+20, cycle_info=cycle_info)
                case "lblSelEndEditTodo":
                    calendar = cast(CalendarCtrl, self.get_control("cadEndEditTodo"))
                    calendar.hide(calendar.visible)
                case "cadEndEditTodo":
                    date = cast(datetime.date, kwargs["val"])
                    lbl_ctrl = cast(LabelCtrl, self.get_control("lblSelEndEditTodo"))
                    lbl_ctrl.set_text(date.strftime("%Y-%m-%d"))
                case _:
                    print(f"undeal with idMsg of TodoDetailDlg: {idmsg} with {kwargs}")
                    return super().process_message(idmsg, **kwargs)
            return True
        return super().process_message(idmsg, **kwargs)


class EditHourDlg(DialogCtrl):
    """_summary_

    """
    def __init__(self, app: tkWin, dlg_cfg: et.Element):
        """_summary_

        Args:
            app (tkWin): _description_
            dlg_cfg (et.Element): _description_
        """
        super().__init__(app, dlg_cfg)
        self._hid: int = 0
        # self._reminders_dict: dict[int, ReminderDataDict] = {}

    def _add_clockctrl(self, cid: int, clkstr: str):
        del_image = "del.png"

        frm_clock = cast(Widget, self.get_control("frmClockEditHour"))

        level = 1

        btndel_xml = self.create_xml("ImageButton", {"id": f"btnDelClock{cid}EditHour",
            "image": del_image,
            "options": "{'height': 20, 'width': 20, 'bg':'white'}"})
        _, btn_del = self.create_control(frm_clock, btndel_xml, level)
        self.assemble_control(btn_del, {"layout":"grid",
            "grid":f"{{'row':{cid+1},'column':0,'sticky':'w'}}"}
        )

        lblclock_xml = self.create_xml("Label", {"text": clkstr,
            "id": f"lblClock{cid}EditHour", "options": "{'style':'BW.TLabel'}"})
        # pv(lbl_item_xml)
        _, lbl_clock = self.create_control(frm_clock, lblclock_xml, level)
        self.assemble_control(lbl_clock, {"layout":"grid",
            "grid":f"{{'row':{cid+1},'column':1,'sticky':'w'}}"}
        )

    @override
    def _beforego(self, **kwargs: object):
        # po(f"_edithourdlg_beforego: {kwargs}")
        # fid = cast(int, kwargs["fid"])
        fid = -1
        # self._old_fid = fid
        # hid = cast(int, kwargs["id"])
        hid = 3
        # db = cast(TimeDatabase, kwargs["db"])
        # owner = cast(Dialog, self.owner)

        if fid != -1:
            lbl_father = cast(LabelCtrl, self.get_control("lblSelFatherEditHour"))
            # detail_father = self._get_hourdetail(db, fid)
            # name_father = detail_father["name"]
            # pv(name_father)
            # lbl_father['text'] = name_father
            lbl_father['text'] = ""

        lbl_selclock = cast(LabelCtrl, self.get_control("lblSelClockEditHour"))
        sls_clock = cast(SlideSwitchCtrl, self.get_control("slsClockEditHour"))

        if hid == 0:
            self.set_title("New Item")

            lbl_selclock.show()
            sls_clock.hide()

            btn_delhour = cast(ButtonCtrl, self.get_control("btnDelItemEditHour"))
            btn_delhour.hide()
            grp, idx = 0, 0
        else:
            self.set_title("Edit Item")
            # detail = self._get_hourdetail(db, hid)
            # pv(detail)

            ent_name = cast(EntryCtrl, self.get_control("txtItemEditHour"))
            # ent_name.set_val(detail["name"])
            ent_name.set_val("English")
            ent_name.disable()

            # eid = list(detail["reminders"].k eys())[0]
            # reminder = detail["reminders"][eid]
            # self._eid = eid
            # self._reminders_dict[eid] = reminder
            # clkstr, schdulestr = reminder2str(reminder)
            clkstr = "Everyday 13:40"
            schdulestr = "Everyday 15m"

            lbl_clock = cast(LabelCtrl, self.get_control("lblClockEditHour"))
            # self._old_clock = lbl_selclock['text']
            # pv(clkstr)
            if clkstr:
                lbl_clock['text'] = "提醒已开启"
                lbl_selclock.hide()
                sls_clock.show()
                sls_clock.set_state(True)
                self._add_clockctrl(0, clkstr)
            else:
                lbl_clock['text'] = "定时提醒"
                lbl_selclock['text'] = "选择定时提醒"
                lbl_selclock.show()
                sls_clock.hide()
            lbl_selschedule = cast(LabelCtrl, self.get_control("lblSelScheduleEditHour"))
            # self._old_schedule = lbl_selschedule['text']
            lbl_selschedule['text'] = schdulestr if schdulestr else "选择时间投入计划"

            # icon = detail["iid"] if detail["iid"] is not None else IconTuple(0, 0)
            # self._old_iid = icon
            # grp, idx = tuple(icon)
            grp = 0
            idx =0

        # images_dict = cast(dict[int, dict[int, str]], owner.process_message("GetImagesDict"))
        # list_itemimage = cast(PicsListviewCtrl, self.get_control("lstImageEditHour"))
        # list_itemimage.add_imagegroup("一般", list(images_dict[0].values()))
        # list_itemimage.add_imagegroup("课程", list(images_dict[1].values()))
        # list_itemimage.add_imagegroup("锻炼", list(images_dict[2].values()))
        # list_itemimage.add_imagegroup("语言", list(images_dict[3].values()))
        # list_itemimage.add_imagegroup("考试", list(images_dict[4].values()))

        # list_itemimage.select(grp, idx)

    @override
    def _confirm(self, **kwargs: object):
        return True, ""

    def _del_reminder(self, cid: int):
        # eid = list(self._reminders_dict.keys())[cid]
        # del self._reminders_dict[eid]
        eid = cid

        lbl_clock = cast(LabelCtrl, self.get_control("lblClockEditHour"))
        lbl_clock['text'] = "定时提醒"
        lbl_selclock = cast(LabelCtrl, self.get_control("lblSelClockEditHour"))
        lbl_selclock['text'] = "选择定时提醒"
        lbl_selclock.show()
        sls_clock = cast(SlideSwitchCtrl, self.get_control("slsClockEditHour"))
        sls_clock.hide()

        self.delete_control(f"btnDel{cid}EditHour")
        self.delete_control(f"lblClock{cid}EditHour")

        assert self._owner is not None
        _ = self._owner.process_message("DelReminder", hid=self._hid, eid=eid)

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        if self.alive:
            kwargs.update(self._extral_msg)
            owner = cast(Dialog, self.owner)
            if idmsg.startswith("btnDelClock"):
                cid = int(idmsg[10:11])
                self._del_reminder(cid)
                return True
            match idmsg:
                case "lblSelClockEditHour":
                    # pv(kwargs)
                    x, y = cast(tuple[int, int], kwargs["mousepos"])
                    return owner.process_message("showSelClockDlg", owner=self,
                        pos=(x+20,y+20), options=kwargs)
                case "changeClock": # come from `SelClockDlg`
                    lbl_selclock = cast(LabelCtrl, self.get_control("lblSelClockEditHour"))
                    # clk_time = cast(datetime.time | None, kwargs["clk_time"])
                    # if clk_time is None:
                    #     lbl_selclock['text'] = ""
                    # else:
                    #     custom = cast(DayType, kwargs["custom"])
                    #     reminder = default_reminder_data()
                    #     reminder["clk_time"] = clk_time
                    #     reminder["custom"] = custom
                    #     reminder["unit"] = TimeUnit.WEEK
                    #     reminder["every"] = 1
                    #     clk_str, _ = reminder2str(reminder)
                    clk_str = cast(str, kwargs["clk_str"])
                    lbl_selclock['text'] = clk_str
                case "lblSelScheduleEditHour":
                    # pv(kwargs)
                    x, y = cast(tuple[int, int], kwargs["mousepos"])
                    return owner.process_message("showSelScheduleDlg", owner=self,
                        pos=(x+20,y+20), options=kwargs)
                case "changeSchedule":  # come from `SelScheduleDlg`
                    # schedule_str = cast(str, kwargs["schedule_str"])
                    # lbl_selschedule = cast(LabelCtrl, self.get_control("lblSelScheduleEditHour"))
                    # lbl_selschedule['text'] = schedule_str
                    # every = cast(int, kwargs["every"])
                    # unit = cast(TimeUnit, kwargs["unit"])
                    # duration = cast(int, kwargs['duration'])
                    # reminder = self._reminders_dict[self._eid]
                    # reminder["every"] = every
                    # reminder["unit"] = unit
                    # reminder["duration"] = duration
                    pass
                case "btnDelItemEditHour":
                    self.destroy()
                    return owner.process_message("deleteItem", id=self._hid)
                case _:
                    return super().process_message(idmsg, **kwargs)
            return True
        return super().process_message(idmsg, **kwargs)


class ExampleApp(Container):
    def __init__(self, cur_path: str, xmlfile: str):
        super().__init__()
        self._app_path: str = cur_path

        self._i: int = 0
        self._idx_left_vertical: int = 0
        self._idx_left_horizontal: int = 0
        self._idx_right_vertical: int = 0
        self._idx_right_horizontal: int = 0

        self._gui: tkWin = tkWin(self._app_path, xmlfile)
        self._gui.filter_message(self._process_message)
        self._gui.set_title("Hello tkinter")

        self._hourdetail_dlg: DialogCtrl = cast(DialogCtrl, self._gui.get_control("dlgHourDetail"))
        self._hourdetail_dlg.filter_message(self._hourdetaildlg_processmessage)
        self._hourdetail_dlg.register_eventhandler("confirm", self._hourdetaildlg_confirm)

    def _create_label(self, parent: tkControl, lid: str, rowid: int, txt: str):
        lbl_xml = self._gui.create_xml("Label", {"text": txt, "id": lid})
        _, lbl_ctrl = self._gui.create_control(parent, lbl_xml, 0, self)
        self._gui.assemble_control(lbl_ctrl, {"layout":"grid",
            "grid":f"{{'row':{rowid},'column':0,'sticky':'w'}}"})

    def _show_hourdetaildlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        kwargs.update({"name": "English Read"})
        self._hourdetail_dlg.do_show(owner, x+20, y+20, **kwargs)

    def _hourdetaildlg_beforego(self, **kwargs: object):
        # po(f"_hourdetaildlg_beforego: {kwargs}")

        lbl_item = cast(LabelCtrl, self._gui.get_control("lblInfoHourDetail"))
        lbl_item.set_text(cast(str, kwargs["name"]))

        # prepare data
        week_day = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        limit_ydata: list[float] = [0] * 7

        per_minutes = 60
        limit_ydata = [per_minutes, per_minutes, per_minutes, \
            per_minutes, per_minutes, per_minutes, per_minutes]

        xdata: list[int] = []
        father_ydata: list[float] = []
        children_ydata: dict[int, list[float]] = {}
        labels: list[str] = []
        today = datetime.datetime.today().date()
        monday = today + datetime.timedelta(days=-today.weekday())
        for i in range(7):
            day = monday + datetime.timedelta(days=i)
            weekday = day.weekday()
            labels.append(f"{week_day[weekday]}\n{day.day}")
            xdata.append(i)
            # minutes = random.randint(0, 15)
            # father_ydata.append(minutes)
            # limit_ydata.append(1.0)
            # po(f"minutes of {day} is {minutes}")
            # for sid in range(3):
            #     minutes = random.randint(0, 15)
            #     if children_ydata.get(sid) is None:
            #         children_ydata[sid] = [minutes]
            #     else:
            #         children_ydata[sid].append(minutes)

        father_ydata = [15, 15, 15, 15, 0, 0, 0]
        father_ydata_aim: list[float] = [15, 15, 15, 15, 15, 15, 15]
        children_ydata[0] = [0, 45, 45, 0, 0, 0, 0]
        children_ydata[1] = [0, 0, 0, 45, 0, 0, 0]
        children_ydata[2] = [0, 0, 0, 0, 0, 45, 45]
        children_ydata[3] = [0, 0, 0, 0, 0, 0, 0]
        children_ydata_aim: list[float] = [45, 45, 45, 45, 45, 45, 45]

        name_labels: list[str] = ["English", "Read", "Listen", "Oral", "write"]

        actual_data: list[list[float]] = []
        actual_data.append(father_ydata)

        aim_data: list[list[float]] = [father_ydata_aim, children_ydata_aim, children_ydata_aim, children_ydata_aim]

        # draw bar
        plt_everyday = cast(MatPlotCtrl, self._gui.get_control("pltEveryDayHour"))
        bar_list: list[BarContainer] = []
        color_list: list[str] = []
        plt_everyday.xdata = xdata

        father_yline = LineData(father_ydata,
            {"tick_label":labels,"width":0.4,"facecolor":"green"}, "bar")
            # {"width":0.4,"facecolor":"green"}, "bar")
        _ = plt_everyday.add_line(father_yline)
        bar = cast(BarContainer, father_yline.line)
        bar_list.append(bar)
        color_list.append(to_hex(bar.patches[0].get_facecolor()))

        bottom_ydata = father_ydata.copy()
        for _, child_ydata in children_ydata.items():
            actual_data.append(child_ydata)
            child_yline = LineData(child_ydata, {"width":0.4,"bottom":bottom_ydata}, "bar")
            _ = plt_everyday.add_line(child_yline)
            bar = cast(BarContainer, child_yline.line)
            bar_list.append(bar)
            color_list.append(to_hex(bar.patches[0].get_facecolor()))
            for i in range(7):
                bottom_ydata[i] += child_ydata[i]
        limit_yline = LineData(limit_ydata, {"linestyle":"dotted","color":"red"})
        _ = plt_everyday.add_line(limit_yline)
        plt_everyday.draw()

        # Hover tip
        patch_map: dict[Rectangle, tuple[str, float]] = {}
        for idx, bar_container in enumerate(bar_list):
            item_name = name_labels[idx]
            item_y_list = actual_data[idx]
            # Bind each single bar patch with its subject name and daily value
            for patch, val in zip(bar_container.patches, item_y_list):
                patch_map[patch] = (item_name, val)

        fig_canvas = plt_everyday.canvas

        tooltip = plt_everyday.add_tooltip(0,0,"", bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8), visible=False)
        def on_mouse_move(e: backend_bases.Event):
            e = cast(backend_bases.MouseEvent, e)
            if e.inaxes != plt_everyday.ax:
                tooltip.set_visible(False)
                fig_canvas.draw()
                return
            hover_patch = None
            for patch in patch_map:
                if patch.contains(e)[0]:
                    hover_patch = patch
                    break
            if hover_patch is not None:
                name, cur_val = patch_map[hover_patch]
                # 格式：第一行项目名，第二行时间
                tip_content = f"{name}\n{cur_val}min"
                tooltip.set_text(tip_content)
                tooltip.set_position((e.xdata if e.xdata else 0, e.ydata if e.ydata else 0))
                tooltip.set_visible(True)
            else:
                tooltip.set_visible(False)
            fig_canvas.draw()
        plt_everyday.event_callback('motion_notify_event', on_mouse_move)

        # progress bar
        # File path list for each subject's independent icon image
        icon_path_list: list[str] = [
			"items\\Language\\English.png",
			"items\\Language\\Listen.png",
			"items\\Language\\Read.png",
			"items\\Language\\Oral.png",
			"items\\Language\\Write.png",
        ]
        main_frame = cast(FrameCtrl, self._gui.get_control("tabEveryDayHour"))
        # chart_total_w = main_frame.control.winfo_width()
        chart_total_w = 340        
        # Bottom Tk canvas for dynamic auto-wrap progress bar panel
        # progress_canvas: tk.Canvas = tk.Canvas(main_frame.control, height=320, bg="white", width=chart_total_w)
        # progress_canvas.grid(row=3, column=0, columnspan=3)
        # progress_canvas = cast(tk.Canvas, self._gui.get_control("cvsDetailEveryDayHour"))
        progress_canvas = cast(CanvasCtrl, self._gui.get_control("cvsDetailEveryDayHour"))
        _ = cast(tk.Canvas, progress_canvas.control).config(width=chart_total_w)

        # Fixed layout constants for progress item styling
        ICON_WIDTH: int = 32
        BAR_TOTAL_LENGTH: int = 70
        BAR_HEIGHT: int = 11  # Progress bar height set to half of original size
        ITEM_FIXED_WIDTH: int = BAR_TOTAL_LENGTH + ICON_WIDTH + 50
        ROW_GAP: int = 40
        COL_GAP: int = 20
        NAME_TEXT_HEIGHT: int = 18
        GRAY_BG_COLOR: str = "#cccccc"

        # Calculate max items per single row, auto wrap to new line when over width limit
        per_row_max: int = int(chart_total_w / ITEM_FIXED_WIDTH)
        per_row_max = max(1, per_row_max)

        all_items = list(zip(name_labels, color_list, actual_data, aim_data, icon_path_list))

        for col_idx, (lab, col, act_list, aim_list, icon_path) in enumerate(all_items):
            cur_row = col_idx // per_row_max
            cur_col = col_idx % per_row_max

            # Calculate left margin for horizontal even distribution in one row
            row_total_used_width = per_row_max * ITEM_FIXED_WIDTH + (per_row_max - 1) * COL_GAP
            row_left_margin = (chart_total_w - row_total_used_width) / 2 if per_row_max > 1 else 15
            base_x = row_left_margin + cur_col * (ITEM_FIXED_WIDTH + COL_GAP)
            base_y = 15 + cur_row * ROW_GAP

            sum_act = sum(act_list)
            sum_aim = sum(aim_list)
            ratio: float = sum_act / sum_aim if sum_aim != 0 else 0.0
            fill_len: float = BAR_TOTAL_LENGTH * ratio

            # Calculate vertical bound of left side full-height subject icon (covers name + progress bar area)
            icon_top = base_y
            icon_bottom = base_y + NAME_TEXT_HEIGHT + BAR_HEIGHT + 6
            icon_h = int(icon_bottom - icon_top)
            icon_center_x = base_x + ICON_WIDTH / 2
            icon_center_y = (icon_top + icon_bottom) / 2

            # Draw tall left sidebar icon (covers both name area and progress bar vertically)
            icon_top = base_y
            icon_bottom = base_y + NAME_TEXT_HEIGHT + BAR_HEIGHT + 6
            _ = progress_canvas.create_image(
                icon_center_x, icon_center_y,
                file_path=icon_path,
                target_w=ICON_WIDTH,
                target_h=icon_h,
                fallback_fill=col,
                anchor="center"
            )

            bar_start_x = base_x + ICON_WIDTH + 12
            name_y_center = base_y + NAME_TEXT_HEIGHT / 2
            right_text_x = bar_start_x + BAR_TOTAL_LENGTH + 12
            bar_top = base_y + NAME_TEXT_HEIGHT + 4
            bar_bottom = bar_top + BAR_HEIGHT
            bar_center_y = (bar_top + bar_bottom) / 2

            # Draw subject name above progress bar, left aligned
            name_y_center = base_y + NAME_TEXT_HEIGHT / 2
            _ = progress_canvas.create_text(
                bar_start_x, name_y_center, text=lab, anchor="w", font=("Microsoft YaHei", 10, "bold")
            )

            # Draw total consumed time text on same horizontal level as subject name
            right_text_x = bar_start_x + BAR_TOTAL_LENGTH + 12
            _ = progress_canvas.create_text(
                right_text_x, name_y_center, text=f"{sum_act}min", anchor="w", font=("Microsoft YaHei", 9)
            )

            # Draw gray background base bar + colored progress fill bar
            bar_top = base_y + NAME_TEXT_HEIGHT + 4
            bar_bottom = bar_top + BAR_HEIGHT
            _ = progress_canvas.create_rectangle(
                bar_start_x, bar_top, bar_start_x + BAR_TOTAL_LENGTH, bar_bottom, fill=GRAY_BG_COLOR, outline="#888888"
            )
            _ = progress_canvas.create_rectangle(
                bar_start_x, bar_top, bar_start_x + fill_len, bar_bottom, fill=col, outline="black"
            )

            # Draw completion rate text aligned vertically with progress bar center
            bar_center_y = (bar_top + bar_bottom) / 2
            _ = progress_canvas.create_text(
                right_text_x, bar_center_y, text=f"{ratio:.0%}", anchor="w", font=("Microsoft YaHei", 9)
            )

    def _hourdetaildlg_confirm(self, **kwargs: object) -> tuple[bool, str]:
        # po(f"_hourdetaildlg_confirm: {kwargs}")
        return True, ""

    def _hourdetaildlg_cancel(self, **kwargs: object) -> tuple[bool, str]:
        # po(f"_hourdetaildlg_cancel: {kwargs}")
        return True, ""

    def _hourdetaildlg_processmessage(self, idmsg: str, **kwargs: object):
        if self._hourdetail_dlg.alive:
            match idmsg:
                case "beforego":
                    self._hourdetaildlg_beforego(**kwargs)
                case "btnRecordHourDetail":
                    x, y = cast(tuple[int, int], kwargs["mousepos"])
                    calendar_dlg = CalendarDialog((x + 20, y + 40))
                    date = calendar_dlg.get_datestr()
                    if date:
                        print(f"hour detail dialog: select date {date}")
                case "lblSelClockItemDetail":
                    x, y = cast(tuple[int, int], kwargs["mousepos"])
                    time_scrollpicker_dlg = TimeScrollPickerDialog((x + 20, y + 40))
                    time = time_scrollpicker_dlg.get_time()
                    print(f"hour detail dialog: select time {time}")
                    timestr = time_scrollpicker_dlg.get_timestr()
                    lbl_selclock = cast(LabelCtrl, self._gui.get_control("lblSelClockItemDetail"))
                    lbl_selclock.set_text(timestr)
                case "cancel":
                    return self._hourdetaildlg_cancel(**kwargs)
                case _:
                    print(f"HourDetailDlg: undeal msg of {idmsg} with {kwargs}")
            return True
        return None

    def _show_tododetaildlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        dlg_id = "dlgTodoDetail"
        dlg_cfg = self._gui.get_customctrlcfg(dlg_id)
        dlg = TodoDetailDlg(self._gui, dlg_cfg)
        # self._gui.register_customctrl(dlg_id, recordhour_dlg)
        dlg.do_show(owner, x+20, y+20, **kwargs)

    def _show_edithourdlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        dlg_id = "dlgEditHour"
        dlg_cfg = self._gui.get_customctrlcfg(dlg_id)
        dlg = EditHourDlg(self._gui, dlg_cfg)
        # self._gui.register_customctrl(dlg_id, recordhour_dlg)
        dlg.do_show(owner, x+20, y+20, **kwargs)

    def _process_message(self, idmsg: str, **kwargs: object):
        match idmsg:
            case "meuShowInfoBox":
                self._gui.show_info('Python Message Info Box', '通知：程序运行正常！')
            case "WarnBox":
                self._gui.show_warn('Python Message Warning Box', '警告：程序出现错误，请检查！')
            case "ErrorBox":
                self._gui.show_err('Python Message Error Box', '错误：程序出现严重错误，请退出！')
            case "ChoiceBox":
                answer = self._gui.ask_yesno("Python Message Dual Choice Box", "你喜欢这篇文章吗？\n您的选择是：")
                if answer:
                    self._gui.show_info('显示选择结果', '您选择了“是”，谢谢参与！')
                else:
                    self._gui.show_info('显示选择结果', '您选择了“否”，谢谢参与！')
            case "varRadSel":
                values = ["富强民主", "文明和谐", "自由平等", "公正法治", "爱国敬业", "诚信友善"]
                monty2 = cast(LabelFrameCtrl, self._gui.get_control("控件示范区2"))
                idx = cast(int, kwargs["val"])
                monty2.configure(text=values[idx])
            case "varChkEna":
                check_btn = cast(CheckButtonCtrl, self._gui.get_control("遵从内心"))
                if cast(int, kwargs["val"]) == 1:
                    check_btn.disable()
                else:
                    check_btn.enable()
            case "varChkUne":
                # check_btn = cast(CheckButtonCtrl, self.get_control("屈于现实"))
                # if int(kwargs["val"]) == 1:
                    # check_btn.disable()
                # else:
                    # check_btn.enable()
                pass
            case "点击之后_按钮失效":
                btn = cast(ButtonCtrl, self._gui.get_control("点击之后_按钮失效"))
                name = cast(EntryCtrl, self._gui.get_control("name"))
                btn.configure(text='Hello\n ' + name.get_val())
                # self.disable_control(btn)
                btn.disable()
            case "blankSpin":
                spin = cast(tk.Spinbox, self._gui.get_control("blankSpin"))
                value = spin.get()
                scr = cast(scrolledtext.ScrolledText, self._gui.get_control("scrolledtext"))
                scr.insert(tk.INSERT, value + '\n')
            case "bookSpin":
                spin = cast(tk.Spinbox, self._gui.get_control("bookSpin"))
                value = spin.get()
                scr = cast(scrolledtext.ScrolledText, self._gui.get_control("scrolledtext"))
                scr.insert(tk.INSERT, value + '\n')
            case "btnHaa":
                ctrl = cast(ListboxCtrl, self._gui.get_control("lstHaa"))
                self._i += 1
                ctrl.insert("end", f"第{self._i:02}项")
            case "btnLeftVAdd":
                ctrl = cast(ScrollableFrameCtrl, self._gui.get_control("frmLeftContentArea"))
                self._idx_left_vertical += 1
                num_row = self._idx_left_vertical
                id_lbl = f"lblLeftV{num_row}"
                self._create_label(ctrl, id_lbl, num_row, f"垂直内容{num_row}")
            case "btnLeftVSub":
                id_lbl = f"lblLeftV{self._idx_left_vertical}"
                self._gui.delete_control(id_lbl)
                self._idx_left_vertical -= 1
            case "btnLeftHAdd":
                ctrl = cast(ScrollableFrameCtrl, self._gui.get_control("frmLeftContentArea"))
                self._idx_left_horizontal += 1
                num_row = self._idx_left_horizontal
                id_lbl = f"lblLeftH{num_row}"
                self._create_label(ctrl, id_lbl, num_row, f"{'水平内容'*num_row}")
            case "btnLeftHSub":
                id_lbl = f"lblLeftH{self._idx_left_horizontal}"
                self._gui.delete_control(id_lbl)
                self._idx_left_horizontal -= 1
            case "btnRightVAdd":
                ctrl = cast(ScrollableFrameCtrl, self._gui.get_control("frmRightContentArea"))
                self._idx_right_vertical += 1
                num_row = self._idx_right_vertical
                id_lbl = f"lblRightV{num_row}"
                self._create_label(ctrl, id_lbl, num_row, f"垂直内容{num_row}")
            case "btnRightVSub":
                id_lbl = f"lblRightV{self._idx_right_vertical}"
                self._gui.delete_control(id_lbl)
                self._idx_right_vertical -= 1
            case "btnRightHAdd":
                ctrl = cast(ScrollableFrameCtrl, self._gui.get_control("frmRightContentArea"))
                self._idx_right_horizontal += 1
                num_row = self._idx_right_horizontal
                id_lbl = f"lblRightH{num_row}"
                self._create_label(ctrl, id_lbl, num_row, f"{'水平内容'*num_row}")
            case "btnRightHSub":
                id_lbl = f"lblRightH{self._idx_right_horizontal}"
                self._gui.delete_control(id_lbl)
                self._idx_right_horizontal -= 1
            case "About":
                pass
            case "ShowHourdetailDialog":
                # x, y = cast(tuple[int, int], kwargs["mousepos"])
                x, y = self._gui.pos
                self._show_hourdetaildlg(self, x+20, y+20, **kwargs)
            case "ShowEditHourDialog":
                # x, y = cast(tuple[int, int], kwargs["mousepos"])
                x, y = self._gui.pos
                self._show_edithourdlg(self, x+20, y+20, **kwargs)
            case "ShowTododetailDialog":
                x, y = self._gui.pos
                self._show_tododetaildlg(self, x+20, y+20, **kwargs)
            case _:
                # print(f"unkonwn message: {idmsg}")
                return super().process_message(idmsg, **kwargs)
        return True

    def go(self):
        self._gui.go()

    @override
    def destroy(self, **kwargs: object):
        pass


def test_gui():

    filepath = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        filepath = os.path.dirname(os.path.abspath(sys.executable))
    winsample_xml = os.path.join(filepath, "resources", "windowSample.xml")
    eapp = ExampleApp(filepath, winsample_xml)
    eapp.go()

if __name__ == "__main__":
    test_gui()
