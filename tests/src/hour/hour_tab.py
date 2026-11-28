#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import datetime
import re
import xml.etree.ElementTree as et
from typing import cast, override

from pygui_simple.tkwin.dialogctrl import DialogCtrl
from pygui_simple.tkwin.tkcontrols import (
    ComboboxCtrl,
    FrameCtrl,
    ImageButtonCtrl,
    ImagePanelCtrl,
    LabelCtrl,
)
from pygui_simple.winbasic import Container, Widget, WinBasic, on_message
from pyutilities_simple.logit import pe, po, pv

from src.action_sys import ActTyp
from src.database.time_database import TimeDatabase
from src.database.time_database_type import (
    DayType,
    IconTuple,
    ReminderDataDict,
    TimeUnit,
    clockstr2reminder,
    default_plan_data,
    reminder2str,
    schedulestr2reminder,
)
from src.hour.dialog_detail import HourDetailDlg
from src.hour.dialog_edit import EditHourDlg
from src.hour.dialog_record import RecordHourDlg
from src.schedule import Schedule


class HourTab(Container):
    """ _summary_

    Attributes:
        _gui (_type_): _description_
        _schedule (_type_): _description_
        _images_dict (_type_): _description_
        _selclock_dlg (_type_): _description_
        _selschedule_dlg (_type_): _description_
        _hoursdb (_type_): _description_
    """
    def __init__(self, owner: WinBasic, schedule: Schedule):
        """ _summary_

        Args:
            owner (tkWin): _description_
        """
        super().__init__()
        self._app: WinBasic = owner
        self._app.filter_message(self.process_message)
        self._schedule: Schedule = schedule
        self._images_dict: dict[int, dict[int, str]] = {
            0: {0: "resources\\items\\CircleFlagsUsBetsyRoss.png", 1: "resources\\items\\FlatUiNews.png", 
                2: "resources\\items\\gift.png", 3: "resources\\items\\VaadinAlarm.png"},
            1: {0: "resources\\items\\Course\\cpp.png", 1: "resources\\items\\Course\\MPC.png",
                2: "resources\\items\\Course\\Vehicle Engineering.png", 3: "resources\\items\\Course\\PMSM.png",
                4: "resources\\items\\Course\\Handwrite.png", 5: "resources\\items\\Course\\股票.png",
                6: "resources\\items\\Course\\管理.png", 7: "resources\\items\\Course\\绘画.png",
                8: "resources\\items\\Course\\机器视觉.png", 9: "resources\\items\\Course\\Calligraphy.png",
                10: "resources\\items\\Course\\语文.png", 11: "resources\\items\\Course\\自动化.png"},
            2: {0: "resources\\items\\Exercise\\锻炼.png", 1: "resources\\items\\Exercise\\俯卧撑.png",
                2: "resources\\items\\Exercise\\跑步.png", 3: "resources\\items\\Exercise\\平板支撑.png",
                4: "resources\\items\\Exercise\\足球.png"},
            3: {0: "resources\\items\\Language\\German.png", 1: "resources\\items\\Language\\Korean.png",
                2: "resources\\items\\Language\\Japanese.png", 3: "resources\\items\\Language\\English.png",
                4: "resources\\items\\Language\\Oral.png", 5: "resources\\items\\Language\\Listen.png",
                6: "resources\\items\\Language\\Read.png", 7: "resources\\items\\Language\\Write.png"},
            4: {0: "resources\\items\\Test\\CET-4.png", 1: "resources\\items\\Test\\CET-6.png",
                2: "resources\\items\\Test\\CFA.png", 3: "resources\\items\\Test\\CPA.png",
                4: "resources\\items\\Test\\GRE.png", 5: "resources\\items\\Test\\IELTS.png",
                6: "resources\\items\\Test\\TOEFL.png"}
        }

        self._selclock_dlg: DialogCtrl = cast(DialogCtrl, self.get_control("dlgSelClock"))
        self._selclock_dlg.register_eventhandler("confirm", self._selclockdlg_confirm)
        self._selclock_dlg.register_eventhandler("beforego", self._selclockdlg_beforego)
        self._selclock_dlg.register_eventhandler("cancel", self._selclockdlg_cancel)

        self._clkstr: str = ""
        self._old_clkstr: str = ""

        self._selschedule_dlg: DialogCtrl = cast(DialogCtrl, self.get_control("dlgSelSchedule"))
        self._selschedule_dlg.register_eventhandler("confirm", self._selscheduledlg_confirm)
        self._selschedule_dlg.register_eventhandler("beforego", self._selscheduledlg_beforego)
        self._selschedule_dlg.register_eventhandler("cancel", self._selscheduledlg_cancel)

        self._schedulestr: str = ""
        self._old_schedulestr: str = ""

        self._hoursdb: TimeDatabase = TimeDatabase()

        self._recordlg_cfg: et.Element = self._app.read_customctrlcfg("resources\\RecordHourDlg.xml")
        self._detaildlg_cfg: et.Element = self._app.read_customctrlcfg("resources\\HourDetailDlg.xml")
        self._editdlg_cfg: et.Element = self._app.read_customctrlcfg("resources\\EditHourDlg.xml")

    def _open(self, dbpath: str):
        """ _summary_
        Args:
            dbpath (type): _description_
        """
        return self._hoursdb.open(dbpath)

    def new_hours(self, dbpath: str):
        """ _summary_
        Args:
            dbpath (type): _description_
        """
        _ = self._open(dbpath)

    def open_hours(self, dbpath: str):
        """ _summary_
        Args:
            dbpath (type): _description_
        """
        _ = self._open(dbpath)
        plans = self._hoursdb.read_plans()
        for pid, plandata in plans.items():
            name = plandata["name"]
            iid = cast(IconTuple, plandata["iid"])
            self.create_hourctrl(pid,
                name, iid,
                plandata["reminders"], plandata["sums"], plandata['fid'])
            for eid, reminderdata in plandata["reminders"].items():
                if clock_time := reminderdata["clk_time"]:
                    self._schedule.add_event(eid, name, clock_time, reminderdata["every"], reminderdata["unit"],
                        reminderdata["custom"],
                        reminderdata["cycbgn_dtime"], reminderdata["cycend_dtime"],
                        ActTyp.LOCK_SCREEN)

    def update_hourctrl_attrib(self, uid: int, attrib: str, val: str | int, eid: int = 0):
        """ _summary_

        Args:
            uid (int): _description_
            attrib (str): _description_
            val (str | float): _description_

        Raises:
            KeyError: _description_
        """
        match attrib:
            case "name":
                ctrl_item1 = cast(LabelCtrl, self.get_control(f"lblItem{uid}"))
                _ = ctrl_item1.configure(text=val, anchor='w')
            case "image":
                ctrl_item2 = cast(ImageButtonCtrl, self.get_control(f"btnItem{uid}"))
                ctrl_item2.change_image(cast(str, val))
            case "clock":   # lblClock{hid}_{eid}
                if val in ["", "选择定时提醒"]:
                    return
                ctrl_item3 = cast(LabelCtrl, self.get_control(f"lblClock{uid}_{eid}"))
                ctrl_item3.set_text(cast(str, val))
            case "sum":
                ctrl_item4 = cast(LabelCtrl, self.get_control(f"lblSumHour{uid}"))
                _ = ctrl_item4.configure(text=f"{float(val)/60:.1f}\nhours")
            case _:
                raise KeyError(f"Unkonw arrtrib: {attrib}")

    def get_hourctrl_attrib(self, uid: int, attrib: str, eid: int = 0) -> str:
        """ _summary_

        Args:
            uid (int): _description_
            attrib (str): _description_

        Returns:
            str: _description_
        """
        val: str = ""
        match attrib:
            case "name":
                ctrl_item1 = cast(LabelCtrl, self.get_control(f"lblItem{uid}"))
                val = cast(str, ctrl_item1['text'])
            # case "image":
                # ctrl_item2 = cast(ImageButtonCtrl, self.get_control(f"btnItem{id_}")
                # raise NotImplementedError("")
            case "clock":
                ctrl_item3 = cast(LabelCtrl, self.get_control(f"lblClock{uid}_{eid}"))
                val = ctrl_item3.get_text()
            case "sum":
                ctrl_item4 = cast(LabelCtrl, self.get_control(f"lblSumHour{uid}"))
                val = cast(str, ctrl_item4['text'])
            case _:
                val = ""
        return val

    def delete_hourctrl(self, father: int, iid: int):
        """ _summary_

        Args:
            father (int): _description_
            iid (int): _description_
        """
        self._app.delete_control(f"frmItem{iid}")
        self._app.delete_control(f"btnItem{iid}")
        self._app.delete_control(f"lblItem{iid}")
        self._app.delete_control(f"pnlClock{iid}")
        plan = self._hoursdb.get_plandata(iid)
        for eid in plan["reminders"]:
            self._app.delete_control(f"lblClock{iid}_{eid}")
        self._app.delete_control(f"lblSumHour{iid}")
        self._app.delete_control(f"frmClock{iid}")
        if father == -1:
            self._app.delete_control(f"frmGroup{iid}")

    def add_clock_ctrl(self, hid: int, eid: int, reminder: ReminderDataDict):
        clk_str, _ = reminder2str(reminder)

        level = 4

        pnl_clock = cast(ImagePanelCtrl, self._app.get_control(f"pnlClock{hid}"))
        if not pnl_clock.visible:
            pnl_clock.show()

        frm_clock = cast(FrameCtrl, self._app.get_control(f"frmClock{hid}"))

        lblclock_xml = self._app.create_xml("Label", {"id": f"lblClock{hid}_{eid}",
            "text": clk_str, "clickable": "true",
            "options":"{'justify':'center'}"})
        _, lbl_clock = self._app.create_control(frm_clock, lblclock_xml, level)
        self._app.assemble_control(lbl_clock, {"layout":"pack",
            "pack":"{'side':'left'}"}, f"{'  '*level}")

    def create_hourctrl(self, hid: int, item: str, iid: IconTuple,
            reminders: dict[int, ReminderDataDict], sums: int, fid: int = -1):
        """ _summary_

        Args:
            hid (int): _description_
            item (str): _description_
            iid (IconTuple): _description_
            clock (str): _description_
            sums (int): _description_, in minutes
            fid (int, optional): _description_. Defaults to -1.
        """
        imagepath = self._get_imagepath(iid.grpidx, iid.eleidx)

        frmain = cast(Widget, self.get_control("frmHourMain"))
        is_subitem = (fid != -1)
        if is_subitem:
            frmgroup = cast(Widget, self.get_control(f"frmGroup{fid}"))
            item_padx1 = 15
            item_padx2 = 5
        else:
            xml = self._app.create_xml("Frame", {"id":f"frmGroup{hid}"})
                 # "options":"{'borderwidth':1,'relief':'ridge'}"})
            _, frmgroup = self._app.create_control(frmain, xml, 2)
            item_padx1 = 0
            item_padx2 = 5

        level = 3
        frmitem_xml = self._app.create_xml("Frame", {"id": f"frmItem{hid}"})
        _, frm_item = self._app.create_control(frmgroup, frmitem_xml, level)

        level = 4

        radio = 0.8 if is_subitem else 1.0

        btnitem_xml = self._app.create_xml("ImageButton", {"id": f"btnItem{hid}",
            "image": imagepath,
            "options": f"{{'height': {int(60 * radio)}, 'width': {int(60 * radio)}}}"}, frmitem_xml)
        _, btn_item = self._app.create_control(frm_item, btnitem_xml, level)
        self._app.assemble_control(btn_item, {"layout":"grid",
            "grid":"{'row':0,'column':0,'rowspan':2}"}, '  '*level)

        lblitem_xml = self._app.create_xml("Label", {"text": item,
            "id": f"lblItem{hid}", "options": "{'width':48}"}, frmitem_xml)
        _, lbl_item = self._app.create_control(frm_item, lblitem_xml, level)
        self._app.assemble_control(lbl_item, {"layout":"grid",
            "grid":"{'row':0,'column':1,'sticky':'w'}"},
            f"{'  '*level}")

        frmclock_xml = self._app.create_xml("Frame", {"id": f"frmClock{hid}"}, frmitem_xml)
        _, frm_clock = self._app.create_control(frm_item, frmclock_xml, level)
        self._app.assemble_control(frm_clock, {"layout":"grid",
            "grid": "{'row':1,'column':1,'sticky':'w'}"}, f"{'  '*level}")

        pnlclock_xml = self._app.create_xml("ImagePanel", {"id": f"pnlClock{hid}",
            "image": "resources\\VaadinAlarm.png",
             "options": "{'height':20, 'width':20}"}, frmclock_xml)
        _, pnl_clock = self._app.create_control(frm_clock, pnlclock_xml, level)
        self._app.assemble_control(pnl_clock, {"layout":"pack",
            "pack":"{'side':'left'}"}, f"{'  '*level}")

        i = 0
        for eid, data in reminders.items():
            clk_str, _ = reminder2str(data)
            if clk_str:
                lblclock_xml = self._app.create_xml("Label", {"id": f"lblClock{hid}_{eid}",
                    "text": clk_str, "clickable": "true",
                    "options":"{'justify':'center'}"}, frmclock_xml)
                _, lbl_clock = self._app.create_control(frm_clock, lblclock_xml, level)
                self._app.assemble_control(lbl_clock, {"layout":"pack",
                    "pack":"{'side':'left'}"}, f"{'  '*level}")
                i += 1

        if i <= 0:
            cast(ImagePanelCtrl, pnl_clock).hide()

        lblsum_xml = self._app.create_xml("Label", {"id": f"lblSumHour{hid}",
            "text": f"{sums/60:.1f}\nhours", "clickable": "true",
            "options":"{'justify':'center'}"}, frmitem_xml)
        _, lbl_sum = self._app.create_control(frm_item, lblsum_xml, level)
        self._app.assemble_control(lbl_sum, {"layout":"grid",
            "grid":"{'row':0,'column':2,'rowspan':2,'sticky':'w'}"}, f"{'  '*level}")

        self._app.assemble_control(frm_item, {"layout": "pack",
            "pack": f"{{'side':'top','pady':1,'padx':({item_padx1},{item_padx2})}}"},
            f"{'  '*(level-1)}")

        if not is_subitem:
            if hid == 1:
                pady1 = 10
            else:
                pady1 = 5
            self._app.assemble_control(frmgroup, {"layout": "pack",
                "pack":f"{{'side':'top','pady':({pady1},5),'fill':'x'}}"}, f"{'  '*(2-1)}")

    def _get_imagepath(self, group: int, index: int):
        """ _summary_

        Args:
            group (int): _description_
            index (int): _description_

        Returns:
            _type_: _description_
        """
        return self._images_dict[group].get(index, "CircleFlagsUsBetsyRoss.png")

    def get_control(self, idctrl: str) -> object:
        """ _summary_

        Args:
            idctrl (str): _description_

        Returns:
            object: _description_
        """
        return self._app.get_control(idctrl)

    def show_selclockdlg(self, owner: Container | None = None,
            x: int = 0, y: int = 0, **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
            kwargs (type): _description_
        """
        self._selclock_dlg.do_show(owner, (x, y), **kwargs)
        return self._clkstr

    def _selclockdlg_beforego(self, **kwargs: object):
        po(f"_selclockdlg_beforego: {kwargs}")
        clkstr = cast(str, kwargs['clkstr'])
        self._old_clkstr = clkstr
        clkstr_list = clkstr.split()
        cmb_selday = cast(ComboboxCtrl, self._selclock_dlg.get_control("cmbSelDay"))
        cmb_selday.set_val(clkstr_list[0])
        time_list = clkstr_list[1].split(":")
        cmb_selhour = cast(ComboboxCtrl, self._selclock_dlg.get_control("cmbSelHour"))
        cmb_selhour.set_val(time_list[0])
        cmb_selminute = cast(ComboboxCtrl, self._selclock_dlg.get_control("cmbSelMinute"))
        cmb_selminute.set_val(time_list[1])

    def _selclockdlg_cancel(self, **_: object):
        self._clkstr = self._old_clkstr

    def _selclockdlg_confirm(self, **kwargs: object) -> tuple[bool, str]:
        """ _summary_
        Args:
            kwargs (type): _description_
        """
        po(f"_selclockdlg_confirm: {kwargs}")
        # owner = cast(Container, self._selclock_dlg.owner)
        cmb_selday = cast(ComboboxCtrl, self._selclock_dlg.get_control("cmbSelDay"))
        sel_day = cmb_selday.get_val()
        cmb_selhour = cast(ComboboxCtrl, self._selclock_dlg.get_control("cmbSelHour"))
        sel_hour = cmb_selhour.get_val()
        cmb_selminute = cast(ComboboxCtrl, self._selclock_dlg.get_control("cmbSelMinute"))
        sel_minute = cmb_selminute.get_val()
        hour = int(sel_hour)
        minute = int(sel_minute)
        clk_str = f"{sel_day} {hour:02}:{minute:02}"
        self._clkstr = clk_str
        pv(self._clkstr)
        return True, ""

    def show_selscheduledlg(self, owner: Container | None = None, x: int = 0, y: int = 0, **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
        """
        self._selschedule_dlg.do_show(owner, (x, y), **kwargs)
        return self._schedulestr

    def _str2duration(self, duration_str: str):
        PATTERN = re.compile(
            r"""
            ^               # Start of string (ensure we match the entire duration string)
            (?:(\d+)h)?     # Optional hours group: (\d+) = 1+ digits, h = literal "h" (non-capturing group for optional)
            \s*             # Optional whitespace (handles "1h 30m" or "1h30m")
            (?:(\d+)m)?     # Optional minutes group: (\d+) = 1+ digits, m = literal "m" (non-capturing group for optional)
            $               # End of string (avoid partial matches like "1h30mxyz")
            """,
            re.VERBOSE | re.IGNORECASE  # VERBOSE = readable regex; IGNORECASE = match H/M or h/m
        )

        match = PATTERN.match(duration_str.strip())
        if not match:
            raise ValueError(f"Invalid duration string: '{duration_str}' (expected format like 15m, 1h30m, 3h)")

        # Extract groups: group 1 = hours, group 2 = minutes (default to 0 if None)
        hours_str = match.group(1)
        minutes_str = match.group(2)

        # Convert to integers (0 if missing)
        hours = int(hours_str) if hours_str else 0
        minutes = int(minutes_str) if minutes_str else 0
        return hours * 60 + minutes

    def _selscheduledlg_beforego(self, **kwargs: object):
        po(f"_selscheduledlg_beforego: {kwargs}")
        schedule_str = cast(str, kwargs['schedulestr'])
        self._old_schedulestr = schedule_str

        cmb_selunit = cast(ComboboxCtrl, self._selschedule_dlg.get_control("cmbSelUnit"))
        cmb_selval = cast(ComboboxCtrl, self._selschedule_dlg.get_control("cmbSelVal"))

        schedule = schedulestr2reminder(schedule_str)

        unit = schedule["unit"]
        if unit == TimeUnit.DAY:
            unit_str = "Everyday"
        elif unit == TimeUnit.WEEK:
            unit_str =  "Everyweek"
        else:
            pv(schedule)
            unit_str = ""
            # raise ValueError(f"don't supoort schedule: {unit!s}")
 
        cmb_selunit.set_val(unit_str)

        val = schedule["duration"]
        h, m = divmod(int(val), 60)
        pv(h, m)
        h_str = f"{h}h" if h else ""
        m_str = f"{m}m" if m else ""
        val_str = f"{h_str}{m_str}"
        pv(val_str)
        cmb_selval.set_val(val_str)

    def _selscheduledlg_cancel(self, **_: object):
        self._schedulestr = self._old_schedulestr

    def _selscheduledlg_confirm(self, **kwargs: object) -> tuple[bool, str]:
        """ _summary_
        Args:
            kwargs (type): _description_
        """
        po(f"_selscheduledlg_confirm: {kwargs}")
        cmb_selval = cast(ComboboxCtrl, self._selschedule_dlg.get_control("cmbSelVal"))
        duration_str = cmb_selval.get_val()
        if duration_str == "不计划":
            self._schedulestr = ""
        else:
            cmb_selunit = cast(ComboboxCtrl, self._selschedule_dlg.get_control("cmbSelUnit"))
            unit_str = cmb_selunit.get_val()

            self._schedulestr = f"{unit_str} {duration_str}"

        return True, ""

    def show_recordhourdlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
            kwargs (type): _description_
        """
        # dlg_id = "dlgRecordHour"
        # dlg_cfg = self._gui.get_customctrlcfg(dlg_id)
        dlg = RecordHourDlg(self, self._recordlg_cfg, self._app)
        dlg.do_show(owner, (x, y), **kwargs)

    def show_hourdetaildlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
            kwargs (type): _description_
        """
        # dlg_id = "dlgHourDetail"
        # dlg_cfg = self._gui.get_customctrlcfg(dlg_id)
        dlg = HourDetailDlg(self._app, self._detaildlg_cfg)
        dlg.do_show(owner, (x, y), **kwargs)

    def show_edithourdlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
            kwargs (type): _description_
        """
        # dlg_id = "dlgEditHour"
        # dlg_cfg = self._gui.get_customctrlcfg(dlg_id)
        dlg = EditHourDlg(self._app, self._editdlg_cfg)
        dlg.do_show(owner, (x, y), **kwargs)

    def modify_clock(self, hid: int, eid: int, clk_time: datetime.time, custom: DayType):
        cycbgn_dtime = datetime.datetime.now()
        reminder = self._hoursdb.modify_reminder(hid, eid,
            clk_time=clk_time,
            every=1,
            unit=TimeUnit.WEEK,
            custom=custom,
            cycbgn_dtime=cycbgn_dtime,
            cycend_dtime=None,
        )
        clk_str, _ = reminder2str(reminder)
        self.update_hourctrl_attrib(hid, "clock", clk_str, eid)

        self._schedule.modify_event(eid, clk_time, cycbgn_dtime, custom=reminder["custom"])

    @on_message("showSelClockDlg")  # come from `EditHourDlg` or <-`HourDetailDlg`<-`EditHourDlg`
    def on_show_selclock_dlg(self, **kwargs: object): # come from `EditHourDlg` or <-`HourDetailDlg`<-`EditHourDlg`
        owner = cast(Container, kwargs["owner"])
        x, y = cast(tuple[int, int], kwargs["pos"])
        options = cast(dict[str, object], kwargs["options"])
        return self.show_selclockdlg(owner, x, y, **options)

    @on_message("ShowSelScheduleDlg") # come from `EditHourDlg` or <-`HourDetailDlg`<-`EditHourDlg`
    def on_show_selschedule_dlg(self, **kwargs: object): # come from `EditHourDlg` or <-`HourDetailDlg`<-`EditHourDlg`
        owner = cast(Container, kwargs["owner"])
        x, y = cast(tuple[int, int], kwargs["pos"])
        options = cast(dict[str, object], kwargs["options"])
        return self.show_selscheduledlg(owner, x, y, **options)

    @on_message("RecordHour")  # come from `RecordHourDlg`
    def on_record(self, **kwargs: object):  # come from `RecordHourDlg`
        hid = cast(int, kwargs["id"])
        strt_dtime = cast(datetime.datetime, kwargs["strt_dtime"])
        duration = cast(int, kwargs["duration"])
        name = self._hoursdb.get_plandata(hid)["name"]
        _ = self._hoursdb.add_record(pid=hid, name=name,
            bgn_dtime=strt_dtime, duration=duration)

        return True

    @on_message("ChangeSum")   # come from RecordHourDlg or HourDetailDlg <- RecordHourDlg
    def on_change_sum(self, **kwargs: object):   # come from RecordHourDlg or HourDetailDlg <- RecordHourDlg
        hid = cast(int, kwargs["id"])
        sum_minutes= cast(int, kwargs["sum"])
        self.update_hourctrl_attrib(hid, "sum", sum_minutes)
        _ = self._hoursdb.modify_plan(hid, sums=sum_minutes)

        return True

    @on_message("changeItemImage") # come from <-`HourDetailDlg`<-`EditHourDlg`
    def on_change_item_image(self, **kwargs: object): # come from <-`HourDetailDlg`<-`EditHourDlg`
        hid = cast(int, kwargs["id"])
        grp = cast(int, kwargs["group"])
        idx = cast(int, kwargs["index"])
        imagepath = self._get_imagepath(grp, idx)
        self.update_hourctrl_attrib(hid, "image", imagepath)
        icon = IconTuple(grp, idx)
        _ = self._hoursdb.modify_plan(hid, iid=icon)

        return True

    @on_message("NewClock") # come from `EditHourDlg`
    def on_new_clock(self, **kwargs: object):
        hid = cast(int, kwargs["hid"])
        name = cast(str, kwargs["name"])
        reminder = cast(ReminderDataDict, kwargs["reminder"])
        eid = self._hoursdb.add_reminder(hid, **reminder)
        if clk_time := reminder['clk_time']:
            self._schedule.add_event(eid, name, clk_time, reminder['every'],
                reminder['unit'], reminder['custom'],
                reminder['cycbgn_dtime'], reminder['cycend_dtime']
            )
            self.add_clock_ctrl(hid, eid, reminder)

        return True

    @on_message("ModifyClock") # come from `EditHourDlg`
    def on_modify_clock(self, **kwargs: object):
        hid = cast(int, kwargs["id"])
        eid = cast(int, kwargs["eid"])
        clk_time = cast(datetime.time, kwargs["clk_time"])
        custom = cast(DayType, kwargs["custom"])
        self.modify_clock(hid, eid, clk_time, custom)

        return True

    @on_message("DelClock") # come from `EditHourDlg`
    def on_del_clock(self, **kwargs: object):
        hid = cast(int, kwargs["hid"])
        eid = cast(int, kwargs["eid"])
        # reminder = cast(ReminderDataDict, kwargs["reminder"])
        self._hoursdb.del_reminder(hid, eid)
        self._schedule.del_event(eid)

        pnl_clock = cast(ImagePanelCtrl, self._app.get_control(f"pnlClock{hid}"))
        self._app.delete_control(f"lblClock{hid}_{eid}")

        hour_detail = self._hoursdb.get_plandata(hid)
        num_clock = 0
        for reminder in hour_detail["reminders"].values():
            if reminder["clk_time"]:
                num_clock += 1
        if num_clock == 0:
            pnl_clock.hide()

        return True

    @on_message("NewSchedule") # come from <-`HourDetailDlg`<-`EditHourDlg`<-`SelScheduleDlg`
    def on_new_schedule(self, **kwargs: object):
        hid = cast(int, kwargs["id"])
        reminder = cast(ReminderDataDict, kwargs["reminder"])
        _ = self._hoursdb.add_reminder(hid, **reminder)
        pe(kwargs)

        return True

    @on_message("ModifySchedule")  # come from <-`HourDetailDlg`<-`EditHourDlg`<-`SelScheduleDlg`
    def on_modify_schedule(self, **kwargs: object):
        hid: int = cast(int, kwargs["id"])
        eid = cast(int, kwargs["eid"])
        reminder = cast(ReminderDataDict, kwargs["reminder"])
        _ = self._hoursdb.modify_reminder(hid, eid,
            every=reminder["every"],
            unit=reminder["unit"],
            custom=reminder["custom"],
            duration=reminder["duration"],
            cycbgn_dtime=datetime.datetime.now(),
        )

        return True

    @on_message("DelSchedule")  # come from <-`HourDetailDlg`<-`EditHourDlg`<-`SelScheduleDlg`
    def on_del_schedule(self, **kwargs: object):
        hid = cast(int, kwargs["id"])
        eid = cast(int, kwargs["eid"])
        self._hoursdb.del_reminder(hid, eid)

        return True

    @on_message("deleteItem")
    def on_del_item(self, **kwargs: object):  # come from <-`HourDetailDlg`<-`EditHourDlg`
        hid = cast(int, kwargs["id"])
        detail = self._hoursdb.get_plandata(hid)

        children = self._hoursdb.get_children(hid)
        if len(children) > 0:
            return False, f"Couldn't delete {detail['name']} wtih children"

        self._app.delete_control(f"frmItem{hid}")
        self._app.delete_control(f"btnItem{hid}")
        self._app.delete_control(f"lblItem{hid}")
        self._app.delete_control(f"btnClock{hid}")
        self._app.delete_control(f"lblSum{hid}")
        fid = detail["fid"]
        if fid == -1:
            self._app.delete_control(f"frmGroup{hid}")

        self._hoursdb.del_plan(hid)

        return True, f"Success to delete {detail['name']}"

    @on_message("btnNewHour")
    def on_open_new_hour(self, **kwargs: object):
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        self.show_edithourdlg(self, x+20, y+20, fid=-1, id=0, db=self._hoursdb)
        return True

    @on_message("NewHour")
    def on_new_hour(self, **kwargs: object): # come from `EditHourDlg` or <-`HourDetailDlg`<-`EditHourDlg`
        name =cast(str, kwargs["name"])
        fid = cast(int, kwargs["fid"])
        iid = cast(IconTuple, kwargs["iid"])
        reminders = cast(dict[int, ReminderDataDict], kwargs["reminders"])

        plandata = default_plan_data()
        plandata["fid"] = fid
        plandata["iid"] = iid
        plandata["name"] = name
        hid = self._hoursdb.add_plan(**plandata)
        self.create_hourctrl(hid, name, iid, reminders, 0, fid)

        return True

    @on_message("getImagePath") # come from `HourDetailDlg`
    def on_get_image_path(self, **kwargs: object):
        group = cast(int, kwargs["group"])
        index = cast(int, kwargs["index"])
        return self._get_imagepath(group, index)

    @on_message("getImagesDict")   # come from `EditHourDlg`
    def on_get_images_dict(self, **_: object):
        return self._images_dict

    @on_message("DeleteFatherCtrl")    # come from `TimeDatabase`
    def on_delete_fatherctrl(self, **kwargs: object):
        fid = cast(int, kwargs["id"])
 
        children =self._hoursdb.get_children(fid)
        for sid in children:
            self.delete_hourctrl(fid, sid)
        self.delete_hourctrl(-1, fid)

        return True

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        if idmsg.startswith("btnItem"):
            hid = int(idmsg[7:])
            x, y = cast(tuple[int, int], kwargs["mousepos"])
            self.show_hourdetaildlg(self, x+20, y+20, id=hid, db=self._hoursdb)
        elif idmsg.startswith("lblSumHour"):
            hid = int(idmsg[10:])
            detail = self._hoursdb.get_plandata(hid)
            x, y = cast(tuple[int, int], kwargs["mousepos"])
            self.show_recordhourdlg(self, x+20, y+20, id=hid, detail=detail)
        elif idmsg.startswith("lblClock"):  # lblClock{hid}_{eid}
            msglist = idmsg.split("_")
            len_eid = len(msglist[1])
            hid = int(idmsg[8: -(len_eid + 1)])
            eid = int(idmsg[-len_eid: ])
            x, y = cast(tuple[int, int], kwargs["mousepos"])
            lbl_clock = cast(LabelCtrl, self._app.get_control(idmsg))
            oldclkstr = lbl_clock.get_text()
            kwargs.update({"clkstr": oldclkstr})
            clkstr = self.show_selclockdlg(self, x+20, y+20, id=hid, eid=eid, **kwargs)
            reminder = clockstr2reminder(clkstr)
            clk_time = reminder["clk_time"]
            assert clk_time is not None
            if clkstr != oldclkstr:
                self.modify_clock(hid, eid, clk_time, cast(DayType, reminder["custom"]))
        else:
            return super().process_message(idmsg, **kwargs)
        return True

    @override
    def destroy(self, **kwargs: object):
        """ _summary_
        """
        _ = self._hoursdb.close()
