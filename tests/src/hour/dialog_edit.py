import tkinter as tk
import xml.etree.ElementTree as et
from typing import cast, override
from uuid import uuid4

from pygui_simple.tkwin.dialogctrl import tkDialogCtrl
from pygui_simple.tkwin.tkcontrols import (
    ButtonCtrl,
    EntryCtrl,
    FrameCtrl,
    LabelCtrl,
    PicsListviewCtrl,
    SlideSwitchCtrl,
)
from pygui_simple.winbasic import Container, WinBasic, on_message
from pyutilities_simple.logit import pe, po, pv

from src.database.time_database import TimeDatabase
from src.database.time_database_type import (
    IconTuple,
    ReminderDataDict,
    clockstr2reminder,
    default_reminder_data,
    reminder2str,
    schedulestr2reminder,
)
from src.hour.hour_type import Reminder, ReminderStatusEnum


class EditHourDlg(tkDialogCtrl):
    """ _summary_

    """
    def __init__(self, app: WinBasic, dlg_cfg: et.Element):
        """ _summary_

        Args:
            app (tkWin): _description_
            dlg_cfg (et.Element): _description_
        """
        super().__init__(app, dlg_cfg, app)
        self._old_fid: int = -1
        self._old_iid: IconTuple = IconTuple(0, 0)
        self._hid: int = 0
        self._reminders: list[Reminder] = []
        self._num_valid_reminders: int = 0
        self._schedule: Reminder = {
            "eid": -1,
            "data": default_reminder_data(),
            "status": ReminderStatusEnum.HOLD
        }
        self._frm_moreclock: FrameCtrl | None  = None

    def _add_clockctrl(self, eid: int, clkstr: str, isnew: bool = True):
        cid = len(self._reminders)
        if eid:
            image_act = "resources\\del.png"
            idbtn_act = f"btnDelClock{cid}EditHour"
            id_lblinfo = f"lblClock{cid}EditHour"
            id_frmitem = f"frmClock{cid}EditHour"
            self._num_valid_reminders += 1
        else:
            image_act =  "resources\\add.png"
            idbtn_act = "btnMoreClockEditHour"
            id_lblinfo = "lblMoreClockEditHour"
            id_frmitem = "frmMoreClockEditHour"

        frm_clock = self.get_control("frmClockEditHour")

        frmitem_xml = self.create_xml("Frame", {"id": id_frmitem,
            "options": "{'bg':'white','columnconfigure':'(0,0,1)'}"}
        )
        _, frm_item = self.create_control(frm_clock, frmitem_xml, 1)

        if not eid:
            self._frm_moreclock = cast(FrameCtrl, frm_item)

        btnact_xml = self.create_xml("ImageButton", {"id": idbtn_act,
            "image": image_act,
            "options": "{'height': 20, 'width': 20, 'bg':'white'}"}, frmitem_xml)
        _, btn_act = self.create_control(frm_item, btnact_xml, 2)
        self.assemble_control(btn_act, {"layout":"grid",
            "grid":"{'row':0,'column':0,'sticky':'w'}"}, ' '*2
        )

        lblinfo_xml = self.create_xml("Label", {"id": id_lblinfo,
            "text": clkstr, "clickable": "true",
            "options": "{'style':'BW.TLabel'}"}, frmitem_xml)
        _, lbl_info = self.create_control(frm_item, lblinfo_xml, 2)
        self.assemble_control(lbl_info, {"layout":"grid",
            "grid":"{'row':0,'column':1,'sticky':'w'}"}, ' '*2
        )

        self.assemble_control(frm_item, {"layout":"grid",
            "grid":f"{{'row':{cid+1},'column':0,'columnspan':3,'sticky':'w'}}"}, ' '
        )

        if eid:
            data = clockstr2reminder(clkstr)
            reminder: Reminder = {
                "eid": eid,
                "data": data,
                "status": ReminderStatusEnum.NEW if isnew else ReminderStatusEnum.HOLD
            }
            self._reminders.append(reminder)

    @override
    def _beforego(self, **kwargs: object):
        po(f"_edithourdlg_beforego: {kwargs}")
        fid = cast(int, kwargs["fid"])
        self._old_fid = fid
        hid = cast(int, kwargs["id"])
        self._hid = hid
        db = cast(TimeDatabase, kwargs["db"])
        owner = cast(Container, self.owner)

        if fid != -1:
            lbl_father = cast(LabelCtrl, self.get_control("lblSelFatherEditHour"))
            detail_father = self._get_hourdetail(db, fid)
            name_father = detail_father["name"]
            pv(name_father)
            lbl_father['text'] = name_father

        lbl_addclock = cast(LabelCtrl, self.get_control("lblAddClockEditHour"))
        sls_clock = cast(SlideSwitchCtrl, self.get_control("slsClockEditHour"))

        if hid == 0:
            self.title("New Item")
            btn_delhour = cast(ButtonCtrl, self.get_control("btnDelItemEditHour"))
            btn_delhour.hide()
            lbl_addclock.show()
            sls_clock.hide()
            grp, idx = 0, 0
        else:
            self.title("Edit Item")
            detail = self._get_hourdetail(db, hid)
            pv(detail)

            ent_name = cast(EntryCtrl, self.get_control("txtItemEditHour"))
            ent_name.set_text(detail["name"])
            ent_name.disable()

            lbl_clock = cast(LabelCtrl, self.get_control("lblClockEditHour"))
            schedule_str = ""
            i = 0
            for eid, reminderdata in detail["reminders"].items():
                if reminderdata["clk_time"]:
                    clk_str, _ = reminder2str(reminderdata)
                    lbl_clock['text'] = "提醒已开启"
                    lbl_addclock.hide()
                    self._add_clockctrl(eid, clk_str, False)
                    i += 1
                else:
                    _, schedule_str = reminder2str(reminderdata)
                    self._schedule["eid"] = eid
                    self._schedule["data"] = reminderdata

            if i <= 0:
                lbl_clock['text'] = "定时提醒"
                lbl_addclock['text'] = "点击添加"
                lbl_addclock.show()
                sls_clock.hide()
            else:
                sls_clock.set_state(True)
                sls_clock.show()
                self._add_clockctrl(0, "点击添加更多提醒时间")

            lbl_selschedule = cast(LabelCtrl, self.get_control("lblSelScheduleEditHour"))
            lbl_selschedule['text'] = schedule_str if schedule_str else "选择时间投入计划"

            icon = detail["iid"] if detail["iid"] is not None else IconTuple(0, 0)
            self._old_iid = icon
            grp, idx = tuple(icon)

        images_dict = cast(dict[int, dict[int, str]], owner.process_message("getImagesDict"))
        list_itemimage = cast(PicsListviewCtrl, self.get_control("lstImageEditHour"))
        list_itemimage.add_imagegroup("一般", list(images_dict[0].values()))
        list_itemimage.add_imagegroup("课程", list(images_dict[1].values()))
        list_itemimage.add_imagegroup("锻炼", list(images_dict[2].values()))
        list_itemimage.add_imagegroup("语言", list(images_dict[3].values()))
        list_itemimage.add_imagegroup("考试", list(images_dict[4].values()))

        list_itemimage.select(grp, idx)

    @override
    def _confirm(self, **kwargs: object):
        po(f"_edithourdlg_confirm: {kwargs}")
        owner = cast(Container, self.owner)
        fid = cast(int, kwargs["fid"])
        hid = cast(int, kwargs["id"])

        reminders: dict[int, ReminderDataDict] = {}
        for reminder in self._reminders:
            reminders[reminder["eid"]] = reminder["data"]

        ent_name = cast(EntryCtrl, self.get_control("txtItemEditHour"))
        name = ent_name.get_text()

        if not name:
            ent_name.set_text("name shouldn't not be empty")
            return

        if hid != 0:    # edit item
            sum_clock_str = ""
            for reminder in self._reminders:
                eid = reminder["eid"]
                data = reminder["data"]
                status = reminder["status"]
                clk_time = data["clk_time"]
                custom = data["custom"]
                clk_str, _ = reminder2str(data)

                if status == ReminderStatusEnum.NEW:
                    _ = owner.process_message("NewClock", hid=hid, name=name, reminder=data)
                    sum_clock_str += " " + clk_str
                elif status == ReminderStatusEnum.MODIFY:
                    _ = owner.process_message("ModifyClock", id=hid, eid=eid,
                    clk_time=clk_time, custom=custom, clk_str=clk_str)
                    sum_clock_str += " " + clk_str
                elif status == ReminderStatusEnum.DELETE:
                    _ = owner.process_message("DelClock", hid=hid, eid=eid, reminder=data)
                else:
                    sum_clock_str += " " + clk_str

            _ = owner.process_message("SumClock", clock_str=sum_clock_str)

            if self._schedule["status"] == ReminderStatusEnum.MODIFY:
                _ = owner.process_message("ModifySchedule", hid=hid, eid=self._schedule["eid"], reminder=self._schedule["data"])
            elif self._schedule["status"] == ReminderStatusEnum.NEW:
                _ = owner.process_message("NewSchedule", hid=hid, reminder=self._schedule["data"])
            elif self._schedule["status"] == ReminderStatusEnum.DELETE:
                _ = owner.process_message("DelSchedule", hid=hid, eid=self._schedule["eid"])

            lst_itemimage = cast(PicsListviewCtrl,
                self.get_control("lstImageEditHour"))
            grp, idx = lst_itemimage.get_selected()
            if IconTuple(grp, idx) != self._old_iid:
                _ = owner.process_message("changeItemImage",
                    id=hid, group=grp, index=idx)
        else:   # New item
            lst_itemimage = cast(PicsListviewCtrl,
                self.get_control("lstImageEditHour"))
            iid = lst_itemimage.get_selected()
            icon = IconTuple(*iid)
            if fid == -1:
                _ = owner.process_message("NewHour",
                    name=name, fid=fid, iid=icon,
                    reminders=reminders)
            else:
                _ = owner.process_message("CreateChild", name=name, iid=icon,
                    fid=fid, reminders=reminders)

        self.destroy(confirm=True, **kwargs)

    @override
    def _cancel(self, **kwargs: object):
        self.destroy(confirm=False, **kwargs)

    def _get_hourdetail(self, db: TimeDatabase, hid: int):
        """ _summary_

        Args:
            hid (int): _description_

        Returns:
            _type_: _description_
        """
        plandata = db.get_plandata(hid)
        return plandata

    def _del_clock(self, cid: int):
        self._num_valid_reminders -= 1

        if not self._num_valid_reminders:
            lbl_clock = cast(LabelCtrl, self.get_control("lblClockEditHour"))
            lbl_clock['text'] = "定时提醒"
            lbl_addclock = cast(LabelCtrl, self.get_control("lblAddClockEditHour"))
            lbl_addclock['text'] = "点击添加"
            lbl_addclock.show()
            sls_clock = cast(SlideSwitchCtrl, self.get_control("slsClockEditHour"))
            sls_clock.hide()

            self.delete_control("btnMoreClockEditHour")
            self.delete_control("lblMoreClockEditHour")
            self.delete_control("frmMoreClockEditHour")

        self.delete_control(f"btnDelClock{cid}EditHour")
        self.delete_control(f"lblClock{cid}EditHour")
        self.delete_control(f"frmClock{cid}EditHour")

        self._frm_moreclock = None

        if self._hid == 0:
            del self._reminders[cid]
        else:
            self._reminders[cid]["data"]["clk_time"] = None
            self._reminders[cid]["status"] = ReminderStatusEnum.DELETE

        if self._frm_moreclock:
            self._frm_moreclock.control.grid_configure(row=len(self._reminders)+1)

    @on_message("lblAddClockEditHour")
    def on_add_clock(self, **_: object):
        lbl_addclock = cast(LabelCtrl, self.get_control("lblAddClockEditHour"))
        lbl_addclock.hide()
        sls_clock = cast(SlideSwitchCtrl, self.get_control("slsClockEditHour"))
        sls_clock.show()
        sls_clock.set_state(True)
        eid = uuid4().int
        clkstr = "Everyday 14:00"
        self._add_clockctrl(eid, clkstr, True)
        if not self._frm_moreclock:
            self._add_clockctrl(0, "点击添加更多提醒时间")
        return True

    @on_message("btnMoreClockEditHour", "lblMoreClockEditHour")
    def on_more_clock(self, **_: object):
        eid = uuid4().int
        clkstr = "Everyday 14:00"
        self._add_clockctrl(eid, clkstr, True)
        if self._frm_moreclock:
            cast(tk.Widget, self._frm_moreclock.control).grid_configure(row=len(self._reminders)+1)
        return True

    @on_message("lblSelScheduleEditHour")
    def on_edit_schedule(self, **kwargs: object):
        kwargs.update(self._extral_msg)
        owner = cast(Container, self.owner)
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        lbl_selschedule = cast(LabelCtrl, self.get_control("lblSelScheduleEditHour"))
        old_schedulestr = lbl_selschedule.get_text()
        schedule_str = old_schedulestr
        if old_schedulestr == "选择时间投入计划":
            schedule_str = "Workday 15m"
        kwargs.update({"schedulestr": schedule_str})
        schedule_str = cast(str, owner.process_message("ShowSelScheduleDlg", owner=self,
            pos=(x+20,y+20), options=kwargs))
        pv(schedule_str)
        pv(old_schedulestr)
        if schedule_str != old_schedulestr:
            lbl_selschedule.set_text(schedule_str)
            if schedule_str:
                reminder = schedulestr2reminder(schedule_str)
                pv(reminder)
                self._schedule["data"] = reminder
                if old_schedulestr == "选择时间投入计划":
                    self._schedule["status"] = ReminderStatusEnum.NEW
                else:
                    self._schedule["status"] = ReminderStatusEnum.MODIFY
            else:
                self._schedule["data"] = default_reminder_data()
                self._schedule["status"] = ReminderStatusEnum.DELETE
        return True

    @on_message("btnDelItemEditHour")
    def on_del_hour(self, **_: object):
        owner = cast(Container, self.owner)
        iid = cast(int, owner.process_message("getId"))
        self.destroy()
        return owner.process_message("deleteItem", id=iid)

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        owner = cast(Container, self.owner)
        if idmsg.startswith("btnDelClock"):
            cid = int(idmsg[11:12])
            self._del_clock(cid)
        elif idmsg.startswith("lblClock"):
            cid = int(idmsg[8: -8])
            lbl_clk = cast(LabelCtrl, self.get_control(idmsg))
            oldclkstr = cast(str, lbl_clk['text'])
            x, y = cast(tuple[int, int], kwargs["mousepos"])
            kwargs.update({"clkstr": oldclkstr})
            clkstr = cast(str, owner.process_message("showSelClockDlg", owner=self,
                pos=(x+20,y+20), options=kwargs))
            if clkstr != oldclkstr:
                lbl_clk['text'] = clkstr
                reminder = clockstr2reminder(clkstr)
                self._reminders[cid]["data"] = reminder
                if self._reminders[cid]["status"] != ReminderStatusEnum.NEW:
                    self._reminders[cid]["status"] = ReminderStatusEnum.MODIFY
        else:
            return super().process_message(idmsg, **kwargs)
        return True
