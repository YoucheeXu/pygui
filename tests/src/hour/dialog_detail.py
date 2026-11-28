import datetime
import math
import tkinter as tk
import xml.etree.ElementTree as et
from typing import cast, override

from matplotlib import backend_bases
from matplotlib.colors import to_hex
from matplotlib.container import BarContainer
from matplotlib.patches import Rectangle
from pygui_simple.tkwin.dialogctrl import tkDialogCtrl
from pygui_simple.tkwin.matplotctrl import LineData, MatPlotCtrl
from pygui_simple.tkwin.tkcontrols import (
    CanvasCtrl,
    FrameCtrl,
    ImageButtonCtrl,
    LabelCtrl,
)
from pygui_simple.winbasic import Container, Widget, WinBasic, on_message
from pyutilities_simple.logit import pe, po, pv

from src.database.time_database import TimeDatabase
from src.database.time_database_type import (
    DayType,
    IconTuple,
    PlanDataDict,
    ReminderDataDict,
    TimeUnit,
    default_plan_data,
    default_reminder_data,
    reminder2str,
)
from src.hour.dialog_edit import EditHourDlg
from src.hour.dialog_record import RecordHourDlg
from src.hour.hour_type import HourTuple


class HourDetailDlg(tkDialogCtrl):
    """ _summary_

    Attributes:
        _last_cid (int): the previous old child index
        _children (_type_): _description_
    """
    def __init__(self, app: WinBasic, dlg_cfg: et.Element):
        """ _summary_

        Args:
            app (WinBasic): _description_
            dlg_cfg (et.Element): _description_
        """
        super().__init__(app, dlg_cfg, app)
        self._last_cid: int = 0
        self._children: dict[int, HourTuple] = {}

        self._hid: int = 0
        self._detail: PlanDataDict = default_plan_data()
        self._db: TimeDatabase | None = None
        self._firstday: datetime.date = datetime.date(2025,12,25)

        self._recordlg_cfg: et.Element = app.read_customctrlcfg("resources\\RecordHourDlg.xml")
        self._editdlg_cfg: et.Element = app.read_customctrlcfg("resources\\EditHourDlg.xml")

    def _update_hourdetailctrl(self, attrib: str, val: str | float):
        """ _summary_

        Args:
            attrib (str): _description_
            val (str | float): _description_

        Raises:
            KeyError: _description_
        """
        match attrib:
            case "name":
                lbl_item = cast(LabelCtrl, self.get_control("lblInfoHourDetail"))
                text_list = lbl_item.get_text().split("\n")
                text_list[0] = str(val)
                lbl_item.set_text(f"{text_list[0]}\n{text_list[1]}")
            case "StartDate":
                lbl_item = cast(LabelCtrl, self.get_control("lblInfoHourDetail"))
                text_list = lbl_item.get_text().split("\n")
                if val:
                    text_list[1] = str(val)
                else:
                    text_list[1] = "从未开始"
                lbl_item.set_text(f"{text_list[0]}\n{text_list[1]}")
            case "sum":
                lbl_sum = cast(LabelCtrl, self.get_control("lblSumHourDetail"))
                lbl_sum.set_text(f"{val}\nhours")
            case "TotalDays":
                lbl_item = cast(LabelCtrl, self.get_control("lblWholeHourDetail"))
                lbl_item.set_text(f"{val}\n坚持天数")
            case "HoursEveryWeek":
                lbl_item = cast(LabelCtrl, self.get_control("lblAvrgHourDetail"))
                lbl_item.set_text(f"{val}h\n平均每周")
            case "HoursLast7Days":
                lbl_item = cast(LabelCtrl, self.get_control("lblRecentHourDetail"))
                lbl_item.set_text(f"{val}h\n最近七天")
            case "RestHours2Milestone":
                lbl_item = cast(LabelCtrl, self.get_control("lblRestHourDetail"))
                lbl_item.set_text(f"{val}\n距离里程碑")
            case _:
                raise KeyError(f"Unkonw arrtrib: {attrib}")

    def _get_hourdetail(self, db: TimeDatabase, hid: int):
        """ _summary_

        Args:
            hid (int): _description_

        Returns:
            _type_: _description_
        """
        plandata = db.get_plandata(hid)
        return plandata

    def _get_minutes_byday(self, hid: int, day: datetime.date):
        assert self._db is not None
        records = self._db.get_records(day, hid)
        total_minutes = 0
        for record in records.values():
            total_minutes += record['duration']
        return total_minutes

    def _plot_weekview(self, hid: int, detail: PlanDataDict, db: TimeDatabase,
            firstday: datetime.date):
        name_labels: list[str] = []
        actual_data: list[list[float]] = []
        bar_list: list[BarContainer] = []
        color_list: list[str] = []
        aim_data: list[list[float]] = []
        icon_path_list: list[str] = []

        children = db.get_children(hid)
        week_day = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        target_ydata: list[float] = [0] * 7

        if len(detail["reminders"]) == 0:
            return

        reminder = default_reminder_data()
        for rmd in detail["reminders"].values():
            if rmd["clk_time"] is None:
                reminder = rmd
                break

        unit = 1
        match reminder['unit']:
            case TimeUnit.DAY:
                unit = 1
            case TimeUnit.WEEK:
                unit = 7
            case TimeUnit.MONTH:
                unit = 30
            case _:
                unit = 360

        total_minutes = reminder['duration']
        per_minutes = total_minutes / unit

        custom = reminder['custom']
        if isinstance(custom, DayType):
            match custom:
                case DayType.WORKDAY:
                    target_ydata = [per_minutes, per_minutes, per_minutes, \
                        per_minutes, per_minutes, 0, 0]
                case DayType.WEEKEND:
                    target_ydata = [0, 0, 0, 0, 0, per_minutes, per_minutes]
                case _:
                    target_ydata = [per_minutes, per_minutes, per_minutes, \
                        per_minutes, per_minutes, per_minutes, per_minutes]
        else:
            target_ydata = [per_minutes, per_minutes, per_minutes, \
                per_minutes, per_minutes, per_minutes, per_minutes]

        xdata: list[int] = []
        father_ydata: list[float] = []
        children_ydata: dict[int, list[float]] = {}
        labels: list[str] = []
        for i in range(7):
            day = firstday + datetime.timedelta(days=i)
            weekday = day.weekday()
            labels.append(f"{week_day[weekday]}\n{day.day}")
            xdata.append(i)
            minutes = self._get_minutes_byday(hid, day)
            father_ydata.append(minutes)
            po(f"minutes of day {day} is {minutes}")
            for cid in children:
                minutes = self._get_minutes_byday(cid, day)
                if children_ydata.get(cid) is None:
                    children_ydata[cid] = [minutes]
                else:
                    children_ydata[cid].append(minutes)

        name_labels.append(detail["name"])
        actual_data.append(father_ydata)
        aim_data.append(target_ydata)
        icon = cast(IconTuple, detail["iid"])
        imagepath = self._get_imagepath(icon.grpidx, icon.eleidx)
        icon_path_list.append(imagepath)
        for cid, child in children.items():
            name_labels.append(child.data["name"])
            actual_data.append(children_ydata[cid])
            aim_data.append([45, 45, 45, 45, 45, 45, 45])
            icon = cast(IconTuple, child.data["iid"])
            imagepath = self._get_imagepath(icon.grpidx, icon.eleidx)
            icon_path_list.append(imagepath)

        # draw bar
        plt_weekview = cast(MatPlotCtrl, self.get_control("pltEveryDayHour"))
        plt_weekview.clear_canvas()        
        plt_weekview.xdata = xdata
        father_yline = LineData(father_ydata,
            {"tick_label":labels,"width":0.4,"facecolor":"green"}, "bar")
        _ = plt_weekview.add_line(father_yline)
        bar = cast(BarContainer, father_yline.line)
        bar_list.append(bar)
        color_list.append(to_hex(bar.patches[0].get_facecolor()))

        bottom_ydata = father_ydata.copy()
        for child_ydata in children_ydata.values():
            child_yline = LineData(child_ydata, {"width":0.4,"bottom":bottom_ydata}, "bar")
            _ = plt_weekview.add_line(child_yline)
            bar = cast(BarContainer, child_yline.line)
            bar_list.append(bar)
            color_list.append(to_hex(bar.patches[0].get_facecolor()))
            for i in range(7):
                bottom_ydata[i] += child_ydata[i]
        limit_yline = LineData(target_ydata, {"linestyle":"dotted","color":"red"})
        _ = plt_weekview.add_line(limit_yline)
        plt_weekview.draw()

        # Hover tip
        patch_map: dict[Rectangle, tuple[str, float]] = {}
        for idx, bar_container in enumerate(bar_list):
            item_name = name_labels[idx]
            item_y_list = actual_data[idx]
            # Bind each single bar patch with its subject name and daily value
            for patch, val in zip(bar_container.patches, item_y_list):
                patch_map[patch] = (item_name, val)

        fig_canvas = plt_weekview.canvas

        tooltip = plt_weekview.add_tooltip(0,0,"",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
            visible=False)
        def on_mouse_move(e: backend_bases.Event):
            e = cast(backend_bases.MouseEvent, e)
            if e.inaxes != plt_weekview.ax:
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
        plt_weekview.event_callback('motion_notify_event', on_mouse_move)

        # detail bar
        chart_total_w = 346
        progress_canvas = cast(CanvasCtrl, self.get_control("cvsDetailEveryDayHour"))
        _ = cast(tk.Canvas, progress_canvas.control).config(width=chart_total_w,background='white')

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
            icon_bottom = base_y + NAME_TEXT_HEIGHT + BAR_HEIGHT + 3
            icon_h = icon_bottom - icon_top
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
            _ = progress_canvas.create_text(
                bar_start_x, name_y_center, text=lab, anchor="w", font=("Microsoft YaHei", 10, "bold")
            )

            # Draw total consumed time text on same horizontal level as subject name
            right_text_x = bar_start_x + BAR_TOTAL_LENGTH + 12
            _ = progress_canvas.create_text(
                right_text_x, name_y_center, text=f"{sum_act}min", anchor="w", font=("Microsoft YaHei", 9)
            )

            # Draw gray background base bar + colored progress fill bar
            _ = progress_canvas.create_rectangle(
                bar_start_x, bar_top, bar_start_x + BAR_TOTAL_LENGTH, bar_bottom, fill=GRAY_BG_COLOR, outline="#888888"
            )
            _ = progress_canvas.create_rectangle(
                bar_start_x, bar_top, bar_start_x + fill_len, bar_bottom, fill=col, outline="black"
            )

            # Draw completion rate text aligned vertically with progress bar center
            _ = progress_canvas.create_text(
                right_text_x, bar_center_y, text=f"{ratio:.0%}", anchor="w", font=("Microsoft YaHei", 9)
            )

    def _get_hours_7days_ago(self, hid: int):
        assert self._db is not None
        today = datetime.datetime.now().date()
        seven_days_ago = today + datetime.timedelta(days=-7)
        records = self._db.get_records(seven_days_ago, hid, today)
        total_minutes = 0
        for record in records.values():
            total_minutes += record["duration"]
        return total_minutes / 60.0

    # TODO:
    def _get_hours_milestone(self, _: int):
        return "∞"

    @override
    def _beforego(self, **kwargs: object):
        po(f"_hourdetaildlg_beforego: {kwargs}")
        self._hid = cast(int, kwargs["id"])
        self._db = cast(TimeDatabase, kwargs["db"])

        self._detail = self._get_hourdetail(self._db, self._hid)

        lbl_father = cast(LabelCtrl, self.get_control("lblFatherItemDetail"))
        fid = self._detail["fid"]
        if fid != -1:
            detail_father = self._get_hourdetail(self._db, fid)
            name_father = detail_father["name"]
            pv(name_father)
            lbl_father['text'] = name_father
        else:
            lbl_father.hide()

        icon = cast(IconTuple, self._detail["iid"])
        imagepath = self._get_imagepath(icon.grpidx, icon.eleidx)
        img_item = cast(ImageButtonCtrl, self.get_control("btnImageHourDetail"))
        img_item.change_image(imagepath)

        # TODO: children?
        firstday = datetime.datetime.fromisoformat("2025-01-01T16:34:00")
        end_date = firstday.date()
        today = datetime.datetime.now().date()
        total_days = 0
        strt_date = today
        records = self._db.get_records(firstday, self._hid, today)
        for record in records.values():
            bgn_dtime = cast(datetime.datetime, record['bgn_dtime'])
            if bgn_dtime.date() != firstday.date():
                total_days += 1
            strt_date = min(strt_date, bgn_dtime.date())
            end_date = max(end_date, bgn_dtime.date())

        lbl_item = cast(LabelCtrl, self.get_control("lblInfoHourDetail"))
        lbl_item.set_text(f"{self._detail["name"]}\n从{strt_date}开始")
        self._update_hourdetailctrl("sum", f"{self._detail["sums"]/ 60:.1f}")
        self._update_hourdetailctrl("TotalDays", total_days)

        total_weeks = math.ceil(((end_date - strt_date).days + 1)/7)
        hours_everyweek = self._detail["sums"] / total_weeks /60
        self._update_hourdetailctrl("HoursEveryWeek", f"{hours_everyweek:.1f}")
        hours_7days_ago = self._get_hours_7days_ago(self._hid)
        self._update_hourdetailctrl("HoursLast7Days", f"{hours_7days_ago:.1f}")
        hours2milestone = self._get_hours_milestone(self._hid)
        self._update_hourdetailctrl("RestHours2Milestone", hours2milestone)

        clk_str = ""
        schedule_str = ""
        for reminder in self._detail["reminders"].values():
            if reminder["clk_time"]:
                clkstr, _ = reminder2str(reminder)
                clk_str = clk_str + "\t" + clkstr
            else:
                pv(reminder)
                _, schedule_str = reminder2str(reminder)
                pv(schedule_str)

        lbl_selclock = cast(LabelCtrl, self.get_control("lblSelClockItemDetail"))
        lbl_selclock['text'] = clk_str
        lbl_selschedule = cast(LabelCtrl, self.get_control("lblSelScheduleItemDetail"))
        lbl_selschedule['text'] = schedule_str

        parent = cast(FrameCtrl, self.get_control("frmSubItmes"))
        children = self._db.get_children(self._hid)
        idx = 0
        for cid, child in children.items():
            icon = cast(IconTuple, child.data["iid"])
            self._children[idx] = HourTuple(hid=cid, name=child.data["name"],
                iid=icon, fid=child.data["fid"],
                reminders=child.data["reminders"], sums=child.data["sums"])
            self._create_childctrl(parent, idx, child.data["name"],
                icon, f"{child.data["sums"] / 60: .1f}")
            idx += 1
        self._last_cid = len(self._children) - 1
        lbl_totalsubitems = cast(LabelCtrl, self.get_control("lblTotalChildren"))
        lbl_totalsubitems["text"] = f"共{idx}个子项目"

        self._firstday = today + datetime.timedelta(days=-today.weekday())
        self._plot_weekview(self._hid, self._detail, self._db, self._firstday)

        """
        thismonth = today.month
        for i in range(6):
            month = thismonth - i
            hours = self._db.get_hoursbymonth(self._iid, month)
            po(f"hours of month {month} is {hours}")

        thisyear = today.year
        for i in range(6):
            year = thisyear - i
            hours = self._db.get_hoursbyyear(self._iid, year)
            po(f"hours of year {year} is {hours}")
        """

    @override
    def _cancel(self, **kwargs: object):
        po(f"_hourdetaildlg_cancel: {kwargs}")
        for idx in self._children:
            self._delete_childctrl(idx)
        self._children.clear()
        self.destroy(confirm=False, **kwargs)

    @override
    def _confirm(self, **kwargs: object):
        po(f"_hourdetaildlg_confirm: {kwargs}")
        owner = cast(Container, self.owner)
        for idx, child in self._children.items():
            if idx > self._last_cid:
                name =      child.name
                iid =       child.iid
                reminders = child.reminders
                fid = cast(int, kwargs["id"])
                _ = owner.process_message("NewHour",
                    name=name, fid=fid, iid=iid, reminders=reminders)
            self._delete_childctrl(idx)
        self._children.clear()

        self.destroy(confirm=True, **kwargs)

    def _get_imagepath(self, group: int, index: int):
        """ _summary_

        Args:
            group (int): _description_
            index (int): _description_

        Returns:
            _type_: _description_
        """
        owner = cast(Container, self._owner)
        imagepath = cast(str, owner.process_message("getImagePath", group=group, index=index))
        return imagepath

    def show_recordhourdlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
        """
        # dlg_id = "dlgRecordHour"
        # dlg_cfg = self._app.get_customctrlcfg(dlg_id)
        recordhour_dlg = RecordHourDlg(self, self._recordlg_cfg, self._app)
        recordhour_dlg.do_show(owner, (x, y), **kwargs)

    def _show_edithourdlg(self, owner: Container | None = None, x: int = 0, y: int = 0,
            **kwargs: object):
        """ _summary_
        Args:
            owner (type): _description_
            x (type): _description_
            y (type): _description_
        """
        # dlg_id = "dlgEditHour"
        # dlg_cfg = self._app.get_customctrlcfg(dlg_id)
        dlg = EditHourDlg(self._app, self._editdlg_cfg)
        dlg.do_show(owner, (x, y), **kwargs)

    def _create_childctrl(self, parent: Widget, uid: int, sub_item: str,
            iid: IconTuple, sums: str):
        """ _summary_

        Args:
            parent (Widget): _description_
            uid (int): _description_
            sub_item (str): _description_
            iid (tuple[int, int]): _description_
            sums (str): _description_
        """
        imagepath = self._get_imagepath(iid.grpidx, iid.eleidx)

        level = 2
        frm_child_xml = self.create_xml("Frame", {"id": f"frmSub{uid}"})
        _, frm_child = self.create_control(parent, frm_child_xml, level)

        level = 3

        pnlitem_xml = self.create_xml("ImagePanel", {"id": f"pnlChild{uid}",
            "image": imagepath, 
            "options": "{'height':20, 'width':20}"}, frm_child_xml)
        _, pnl_item = self.create_control(frm_child, pnlitem_xml, level)
        self.assemble_control(pnl_item, {"layout":"pack",
            "pack":"{'side':'left','anchor':'w'}"}, '  '*level)

        lblitem_xml = self.create_xml("Label", {"id": f"lblChild{uid}", 
            "text": sub_item, "options": "{'width':40}"}, frm_child_xml)
        _, lbl_subitem = self.create_control(frm_child, lblitem_xml, level)
        self.assemble_control(lbl_subitem, {"layout":"pack",
            "pack":"{'side':'left','anchor':'w'}"}, f"{'  '*level}")

        lblsum_xml = self.create_xml("Label", {"text": f"{sums}h",
            "id": f"lblSubSum{uid}"}, frm_child_xml)
        _, lbl_sum = self.create_control(frm_child, lblsum_xml, level)
        self.assemble_control(lbl_sum, {"layout":"pack",
            "pack":"{'side':'left','anchor':'e'}"}, f"{'  '*level}")

        self.assemble_control(frm_child, {"layout": "grid",
            "grid": f"{{'row':{uid},'column':0,'pady':4}}"}, f"{'  '*(level-1)}")

    def _delete_childctrl(self, sid: int):
        """ _summary_

        Args:
            sid (int): _description_
        """
        self.delete_control(f"frmSub{sid}")
        self.delete_control(f"pnlChild{sid}")
        self.delete_control(f"lblChild{sid}")
        self.delete_control(f"lblSubSum{sid}")

    @on_message("btnImageHourDetail")
    def on_edit_hour(self, **kwargs: object):
        hid = cast(int, kwargs["id"])
        db = cast(TimeDatabase, kwargs["db"])
        detail = self._get_hourdetail(db, hid)
        fid = detail["fid"]
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        self._show_edithourdlg(self, x+20, y+20,
            fid=fid, id=hid, db=db)
        return True

    @on_message("changeItemImage") # come from `EditHourDlg`
    def on_change_image_path(self, **kwargs: object):
        owner = cast(Container, self.owner)
        hid = cast(int, kwargs["id"])
        grp = cast(int, kwargs["group"])
        idx = cast(int, kwargs["index"])
        imagebutton = cast(ImageButtonCtrl, self.get_control("btnImageHourDetail"))
        imagepath = self._get_imagepath(grp, idx)
        imagebutton.change_image(imagepath)
        return owner.process_message("changeItemImage",
            id=hid, group=grp, index=idx)

    @on_message("SumClock") # come from `EditHourDlg`
    def on_sum_clock(self, **kwargs: object):
        lbl_selclock = cast(LabelCtrl,
			self.get_control("lblSelClockItemDetail"))
        clock_str = cast(str, kwargs["clock_str"])
        lbl_selclock.set_text(clock_str)
        return True

    @on_message("NewSchedule") # come from `EditHourDlg`
    def on_new_schedule(self, **kwargs: object):
        owner = cast(Container, self.owner)
        reminder = cast(ReminderDataDict, kwargs["reminder"])
        _, schedule_str = reminder2str(reminder) 
        lbl_selschedule = cast(LabelCtrl,
            self.get_control("lblSelScheduleItemDetail"))
        lbl_selschedule.set_text(schedule_str)
        return owner.process_message("NewSchedule", **kwargs)

    @on_message("ModifySchedule")  # come from `EditHourDlg`
    def on_modify_schedule(self, **kwargs: object):
        owner = cast(Container, self.owner)
        reminder = cast(ReminderDataDict, kwargs["reminder"])
        _, schedule_str = reminder2str(reminder) 
        lbl_selschedule = cast(LabelCtrl,
            self.get_control("lblSelScheduleItemDetail"))
        lbl_selschedule.set_text(schedule_str)
        return owner.process_message("ModifySchedule", **kwargs)

    @on_message("DelSchedule") # come from `EditHourDlg`
    def on_del_schedule(self, **kwargs: object):
        owner = cast(Container, self.owner)
        lbl_selschedule = cast(LabelCtrl,
            self.get_control("lblSelScheduleItemDetail"))
        lbl_selschedule.set_text("")
        return owner.process_message("DelSchedule", **kwargs)

    @on_message("btnAddChild")
    def on_add_child(self, **kwargs: object):
        db = cast(TimeDatabase, kwargs["db"])
        hid = cast(int, kwargs["id"])
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        self._show_edithourdlg(self, x+20, y+20,
            fid=hid, id=0, db=db)
        return True

    @on_message("CreateChild")  # come from `EditHourDlg`
    def on_create_child(self, **kwargs: object):
        parent = cast(FrameCtrl, self.get_control("frmSubItmes"))
        cid = len(self._children)
        name = cast(str, kwargs["name"])
        iid = cast(IconTuple, kwargs["iid"])
        self._create_childctrl(parent, cid, name, iid, "0.0")

        reminders = cast(dict[int, ReminderDataDict],  kwargs["reminders"])
        fid = cast(int, kwargs["fid"])
        self._children[cid] = HourTuple(0, name, iid, fid,
            reminders, 0)
        lbl_totalsubitems = cast(LabelCtrl, self.get_control("lblTotalChildren"))
        lbl_totalsubitems["text"] = f"共{len(self._children)}个子项目"
        return True

    @on_message("btnRecordHourDetail")
    def on_record(self, **kwargs: object):
        fid = self._detail["fid"]
        x, y = cast(tuple[int, int], kwargs["mousepos"])
        self.show_recordhourdlg(self, x+20, y+20,
            fid=fid, id=self._hid, detail=self._detail)
        return True

    @on_message("ChangeSum")   # come from `RecordHourDlg`
    def on_change_sum(self, **kwargs: object):
        owner = cast(Container, self.owner)
        hid = cast(int, kwargs["id"])        
        sum_minutes= cast(float, kwargs["sum"])
        lbl_sum = cast(LabelCtrl, self.get_control("lblSumHourDetail"))
        lbl_sum.set_text(f"{float(sum_minutes)/60:.1f}\nhours")
        # self._update_hour(hid, "sum", sum_minutes)
        # _ = owner.process_message("updateHour", id=hid, attrib="sum", val=sum_minutes)
        _ = owner.process_message("ChangeSum", id=hid, sum=sum_minutes)
        return True

    @on_message("btnPrevDayHour")
    def on_prev_day(self, **kwargs: object):
        db = cast(TimeDatabase, kwargs["db"])
        self._firstday -= datetime.timedelta(days=1)
        self._plot_weekview(self._hid, self._detail, db, self._firstday)
        return True

    @on_message("btnPrevWeekHour")
    def on_prev_week(self, **kwargs: object):
        db = cast(TimeDatabase, kwargs["db"])
        self._firstday -= datetime.timedelta(days=7)
        self._plot_weekview(self._hid, self._detail, db, self._firstday)
        return True

    @on_message("btnNextDayHour")
    def on_next_day(self, **kwargs: object):
        db = cast(TimeDatabase, kwargs["db"])
        self._firstday += datetime.timedelta(days=1)
        self._plot_weekview(self._hid, self._detail, db, self._firstday)
        return True

    @on_message("btnNextWeekHour")
    def on_next_week(self, **kwargs: object):
        db = cast(TimeDatabase, kwargs["db"])
        self._firstday += datetime.timedelta(days=7)
        self._plot_weekview(self._hid, self._detail, db, self._firstday)
        return True

    @on_message("deleteItem")  # come from `EditHourDlg`
    def on_del_hour(self, **kwargs: object):
        owner = cast(Container, self.owner)
        hid = cast(int, kwargs["id"])
        _ = owner.process_message("deleteItem", id=hid)
        self.destroy()
        return True
