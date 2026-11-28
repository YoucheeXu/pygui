import datetime
import uuid
import xml.etree.ElementTree as et
from copy import deepcopy
from typing import cast, override

from pygui_simple.tkwin.dialogctrl import tkDialogCtrl
from pygui_simple.tkwin.tkcontrols import (
    CalendarCtrl,
    EntryCtrl,
    LabelCtrl,
    SlideSwitchCtrl,
    TimeScrollPickerCtrl,
)
from pygui_simple.winbasic import Widget, WinBasic, on_message

from src.database.time_database_type import TimeUnit, date2str, str2time, time2str
from src.todo.dialog_repeat_cycle import RepeatCycleDlg
from src.todo.todo_type import Todo


class EditTodoDialog(tkDialogCtrl):
    """_summary_

    Attributes:
        _variable_ (_type_): _description_
    """
    def __init__(self, parent: Widget, dlg_cfg: et.Element, app: WinBasic):
        """_summary_

        Args:
            app (tkWin): _description_
            dlg_cfg (et.Element): _description_
        """
        self._todo: Todo | None = None
        self._todo_old: Todo | None = None
        super().__init__(parent, dlg_cfg, app)

        self._repeatcycledlg_cfg: et.Element = app.read_customctrlcfg("resources\\RepeatCycleDlg.xml")

    @override
    def _beforego(self, **kwargs: object):
        self._todo = cast(Todo, kwargs["todo"])
        self._todo_old = deepcopy(self._todo)

        tududata = self._todo["data"]
        entry_name = cast(EntryCtrl, self.get_control("txtNameEditTodo"))
        entry_name.set_text(tududata["name"])
        entry_note = cast(EntryCtrl, self.get_control("txtNoteEditTodo"))
        entry_note.set_text(tududata["note"])

        if tududata["reminder_id"] > 0:
            reminder_info = tududata["reminder_infos"][self._todo["reminder_idx"]]

            reminder_date = self._todo["day"]
            lbl_date = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
            lbl_date.set_text(date2str(reminder_date))
            sls_date = cast(SlideSwitchCtrl, self.get_control("slsDateEditTodo"))
            sls_date.set_state(True, False)

            reminder_time = reminder_info["clock_time"]
            lbl_time = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
            lbl_time.set_text(time2str(reminder_time))
            sls_time = cast(SlideSwitchCtrl, self.get_control("slsTimeEditTodo"))
            sls_time.set_state(True, False)

        calendar = cast(CalendarCtrl, self.get_control("cadDateEditTodo"))
        calendar.cancel_select()
        calendar.hide()
        time_scrollerpicker_ctrl = cast(TimeScrollPickerCtrl, self.get_control("tspTimeEditTodo"))
        time_scrollerpicker_ctrl.hide()

        # frm = cast(FrameCtrl, self.get_control(idctrl="frmEndEditTodo"))
        # frm.hide()

    @override
    def _confirm(self, **kwargs: object):
        assert self._todo is not None
        assert self._todo_old is not None

        tududata = self._todo["data"]
        entry_name = cast(EntryCtrl, self._app.get_control("txtNameEditTodo"))
        tududata["name"] = entry_name.get_text()
        entry_note = cast(EntryCtrl, self._app.get_control("txtNoteEditTodo"))
        tududata["note"] = entry_note.get_text()

        # date: datetime.date | None = None
        # lbl_date = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
        # date_str = lbl_date.get_text()
        # if date_str:
        #     date = datetime.datetime.strptime(date_str, "%B %d, %Y\t%A").date()

        # pv(date)

        # time: datetime.time | None = None
        # lbl_time = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
        # time_str = lbl_time.get_text()
        # if time_str:
        #     time = datetime.datetime.strptime(time_str, "%H:%M").time()

        # pv(time)

        # if date or time:
        #     if self._todo_dict["reminder_id"] <= 0:
        #         self._todo_dict["reminder_id"] = uuid.uuid4().int
        #     reminder = self._todo_dict["reminder"]
        #     assert reminder is not None
        #     reminder["clk_time"] = time
        #     date = date if date else datetime.datetime.now().date()
        #     time = time if time else datetime.time(0, 0)
        #     reminder["cycbgn_dtime"] = datetime.datetime.combine(date, time)

        # pv(self._todo_dict["reminder"])

        # TODO: compare self._todo_dict with self._todo_old


        if tududata["reminder"]["every"] !=0 and tududata["reminder_id"] == 0:
            tududata["reminder_id"] = uuid.uuid4().int

        assert self._owner is not None
        _ = self._owner.process_message("ModifyTodo", todo=self._todo)
        # pv(self._owner)

        self.destroy(confirm=True, **kwargs)


    @on_message("lblSelDateEditTodo")
    def on_switch_select_date(self, **_: object):
        lbl_date = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
        calendar = cast(CalendarCtrl, self.get_control("cadDateEditTodo"))
        if lbl_date.get_text():
            calendar.hide(calendar.visible)
            # slideswitch = cast(SlideSwitchCtrl, self.get_control("slsDateEditTodo"))
            # slideswitch.set_state(calendar.visible)

        return True

    @on_message("slsDateEditTodo")
    def on_switch_date(self, **kwargs: object):
        val = cast(bool, kwargs['val'])
        calendar = cast(CalendarCtrl, self.get_control("cadDateEditTodo"))
        if not val:
            calendar.cancel_select()
            lbl = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
            lbl.set_text("")
        calendar.hide(not val)

        return True

    @on_message("cadDateEditTodo")
    def on_select_date(self, **kwargs: object):
        lbl_date = cast(LabelCtrl, self.get_control("lblSelDateEditTodo"))
        date = cast(datetime.date, kwargs['val'])
        # date_text = f"{date.year}年{date.month:02d}月{date.day:02d}日"
        # date_text = date.strftime("%B %d, %Y\t%A")
        date_text = date2str(date)
        lbl_date.set_text(date_text)

        return True

    @on_message("lblSelTimeEditTodo")
    def on_switch_select_time(self, **_: object):
        lbl_time = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
        time_scrollerpicker_ctrl = cast(TimeScrollPickerCtrl, self.get_control("tspTimeEditTodo"))
        if lbl_time.get_text():
            time_scrollerpicker_ctrl.hide(time_scrollerpicker_ctrl.visible)
            # slideswitch = cast(SlideSwitchCtrl, self.get_control("slsDateEditTodo"))
            # slideswitch.set_state(calendar.visible)

        return True

    @on_message("slsTimeEditTodo")
    def on_switch_time(self, **kwargs: object):
        val = cast(bool, kwargs['val'])
        time_scrollerpicker_ctrl = cast(TimeScrollPickerCtrl, self.get_control("tspTimeEditTodo"))
        if not val:
            lbl_time = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
            lbl_time.set_text("")
        time_scrollerpicker_ctrl.hide(not val)

        return True

    @on_message("tspTimeEditTodo")
    def on_select_time(self, **kwargs: object):
        assert self._todo is not None
        lbl_time = cast(LabelCtrl, self.get_control("lblSelTimeEditTodo"))
        time = cast(datetime.time, kwargs['val'])
        # time_text = time.strftime("%H:%M")
        time_text = time2str(time)
        lbl_time.set_text(time_text)

        reminder = self._todo["data"]["reminder"]
        assert reminder is not None
        # reminder["clk_time"] = datetime.datetime.strptime(lbl_time.get_text(), "%H:%M").time()
        reminder["clk_time"] = str2time(lbl_time.get_text())

        return True

    @on_message("lblSelCycleEditTodo")
    def on_select_cycle(self, **kwargs: object):
        lbl = cast(LabelCtrl, self.get_control(idctrl="lblSelCycleEditTodo"))
        cycle_info = lbl.get_text()
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        # dlg_id = "dlgRepeatCycle"
        # dlg_cfg = self._app.get_customctrlcfg(dlg_id)
        dlg = RepeatCycleDlg(self, self._repeatcycledlg_cfg, self)
        dlg.do_show(self, (x+20, y+20), cycle_info=cycle_info)

        return True

    @on_message("ModifyCycle")
    def on_modify_cycle(self, **kwargs: object):
        assert self._todo is not None
        cycle_info = cast(str, kwargs["cycle_info"])
        lbl = cast(LabelCtrl, self.get_control(idctrl="lblSelCycleEditTodo"))
        lbl.set_text(cycle_info)

        reminder = self._todo["data"]["reminder"]
        assert reminder is not None
        reminder["every"] = cast(int, kwargs["every"])
        reminder["unit"] = cast(TimeUnit, kwargs["frq"])

        return True
