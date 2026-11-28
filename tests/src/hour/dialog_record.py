import datetime
import xml.etree.ElementTree as et
from typing import cast, override

from pygui_simple.tkwin.dialogctrl import DialogCtrl
from pygui_simple.tkwin.scrollpickerctrl import (
    DateScrollPickerDialog,
    TimeScrollPickerDialog,
)
from pygui_simple.tkwin.tkcontrols import (
    LabelCtrl,
)
from pygui_simple.winbasic import Container, Widget, WinBasic, on_message

from src.database.time_database_type import (
    PlanDataDict,
    time2str,
)


class RecordHourDlg(DialogCtrl):
    """ _summary_

    """
    def __init__(self, parent: Widget, dlg_cfg: et.Element, owner: WinBasic):
        """ _summary_

        Args:
            app (tkWin): _description_
            dlg_cfg (et.Element): _description_
        """
        self._app: WinBasic = owner
        attr_dict: dict[str, str] = dlg_cfg.attrib
        # super().__init__(app, dlg_cfg)
        super().__init__(parent, attr_dict.get("text", ""), int(attr_dict["Width"]), int(attr_dict["Height"]))

        self._subctrlcfg_list: list[et.Element] = list(dlg_cfg)

    @property
    @override
    def path(self) -> str:
        return self._app.path

    @override
    def _construct_children(self) -> None:
        for sub_ctrl in self._subctrlcfg_list:
            _ = self.create_controls(self._main_frame, sub_ctrl, 1)
        return super()._construct_children()

    @override
    def _beforego(self, **kwargs: object):
        detail = cast(PlanDataDict, kwargs["detail"])

        lbl_item = cast(LabelCtrl, self.get_control("lblItemRecordHour"))
        lbl_item.set_text(detail["name"])

        today = datetime.date.today()
        lbl_day = cast(LabelCtrl, self.get_control("lblSelDayRecordHour"))
        lbl_day.set_text(str(today))

        clock_time = None
        reminders = detail["reminders"]
        if reminders:
            # TODO: get now's nearby reminder
            reminder = next(iter(reminders.values()))
            clock_time  = reminder['clk_time']
            schedule_val = reminder["duration"]
        else:
            schedule_val = 15
        if clock_time is None:
            clock_time = datetime.datetime.now().time()

        lbl_strtime = cast(LabelCtrl, self.get_control("lblSelStrtRecordHour"))
        clock_val = time2str(clock_time)
        lbl_strtime.set_text(clock_val)

        lbl_lastime = cast(LabelCtrl, self.get_control("lblSelLastRecordHour"))
        lbl_lastime.set_text(f"{schedule_val}m")

    @on_message("lblSelDayRecordHour")
    def on_select_day(self, **kwargs: object):
        """ _summary_
        """
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        scrollpicker = DateScrollPickerDialog(self, (x, y+20),
            "选择日期")
        date = scrollpicker.get_datestr()
        lbl_day = cast(LabelCtrl, self.get_control("lblSelDayRecordHour"))
        lbl_day.set_text(date)
 
        return True

    @on_message("lblSelStrtRecordHour")
    def on_select_strtime(self, **kwargs: object):
        """ _summary_
        """
        lbl_strtime = cast(LabelCtrl, self.get_control("lblSelStrtRecordHour"))
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        scrollpicker = TimeScrollPickerDialog(self, (x, y+20),
            stp=5, title="选择时间", initial=lbl_strtime.get_text())
        strt_time = scrollpicker.get_timestr()
        lbl_strtime = cast(LabelCtrl, self.get_control("lblSelStrtRecordHour"))
        lbl_strtime.set_text(strt_time)

        return True

    def _schedule_txt2clk(self, txt: str):
        """ _summary_

        Args:
            txt (str): _description_

        Returns:
            _type_: _description_
        """
        if not txt:
            return "00:00"
        clk = txt.replace("h", ":").replace("m", "")
        if ":" not in clk:
            # clk = "00:" + clk
            h, m = divmod(int(clk), 60)
            clk = f"{h: 02d}:{m: 02d}"
        return clk

    @on_message("lblSelLastRecordHour")
    def on_select_lastime(self, **kwargs: object):
        """ _summary_
        """
        lbl_lastime = cast(LabelCtrl, self.get_control("lblSelLastRecordHour"))
        lastime = self._schedule_txt2clk(lbl_lastime.get_text())
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        scrollpicker = TimeScrollPickerDialog(self, (x, y+20),
            stp=5, title="持续时间", initial=lastime)
        lastime = scrollpicker.get_timestr()
        lastime_list = lastime.split(":")
        hour = int(lastime_list[0])
        minute = int(lastime_list[1])
        lastime = str(hour * 60 + minute) + "m"

        lbl_lastime = cast(LabelCtrl, self.get_control("lblSelLastRecordHour"))
        lbl_lastime.set_text(lastime)

        return True

    @override
    def _confirm(self, **kwargs: object):
        hid = cast(int, kwargs["id"])
        detail = cast(PlanDataDict, kwargs["detail"])
        owner = cast(Container, self.owner)

        lbl_day = cast(LabelCtrl, self.get_control("lblSelDayRecordHour"))
        day = lbl_day.get_text()

        lbl_strtime = cast(LabelCtrl, self.get_control("lblSelStrtRecordHour"))
        strt_time = lbl_strtime.get_text()

        strt_dtime = datetime.datetime.strptime(f"{day} {strt_time}", "%Y-%m-%d %H:%M")

        lbl_lastime = cast(LabelCtrl, self.get_control("lblSelLastRecordHour"))
        last_time = lbl_lastime.get_text()
        duration = int(last_time[:-1])

        _ = owner.process_message("RecordHour", id=hid,
            strt_dtime=strt_dtime, duration=duration)
        # detail = self._get_hourdetail(db, hid)
        sum_minutes = detail["sums"] + duration

        _ = owner.process_message("ChangeSum", id=hid, sum=sum_minutes)

        self.destroy(confirm=True, **kwargs)

    @override
    def _cancel(self, **kwargs: object):
        self.destroy(confirm=False, **kwargs)
