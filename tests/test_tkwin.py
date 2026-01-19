import os
import sys
import random
import datetime
import xml.etree.ElementTree as et
import tkinter as tk
from tkinter import scrolledtext
from typing import override, cast

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

from src.pygui.winbasic import Dialog
from src.pygui.matplot import LineData, MatPlotCtrl
from src.pygui.tkcontrol import tkControl
from src.pygui.tkwin import LabelCtrl, EntryCtrl, ButtonCtrl, CheckButtonCtrl
from src.pygui.tkwin import ListboxCtrl, LabelFrameCtrl, ScrollableFrameCtrl
from src.pygui.tkwin import DialogCtrl, tkWin
"""
    uv run pytest --cov=src.pygui.tkwin .\tests\test_tkwin.py -v
"""

def test_gui():

    class TodoDetailDlg(DialogCtrl):
        def __init__(self, app: tkWin, dlg_cfg: et.Element):
            super().__init__(app, dlg_cfg)

        @override
        def _beforego(self, **kwargs: object):
            # po(f"{self._idself} beforego")
            pass

        @override
        def _confirm(self, **kwargs: object):
            # po(f"{self._idself} confirm")
            return True, ""

        @override
        def _cancel(self, **kwargs: object):
            # po(f"{self._idself} cancel")
            return True, ""

        @override
        def process_message(self, idmsg: str, **kwargs: object):
            kwargs.update(self._extral_msg)
            if self.alive:
                match idmsg:
                    case _:
                        return super().process_message(idmsg, **kwargs)
            return super().process_message(idmsg, **kwargs)

    class ExampleApp(tkWin):
        def __init__(self, cur_path: str, xmlfile: str):
            super().__init__(cur_path, xmlfile)
            self._i: int = 0
            self._idx_left_vertical: int = 0
            self._idx_left_horizontal: int = 0
            self._idx_right_vertical: int = 0
            self._idx_right_horizontal: int = 0

            self._hourdetail_dlg: DialogCtrl = cast(DialogCtrl, self.get_control("dlgHourDetail"))
            self._hourdetail_dlg.filter_message(self._hourdetaildlg_processmessage)
            self._hourdetail_dlg.register_eventhandler("confirm", self._hourdetaildlg_confirm)

        def _create_label(self, parent: tkControl, lid: str, rowid: int, txt: str):
            lbl_xml = self.create_xml("Label", {"text": txt, "id": lid})
            _, lbl_ctrl = self.create_control(parent, lbl_xml)
            self.assemble_control(lbl_ctrl, {"layout":"grid",
                "grid":f"{{'row':{rowid},'column':0,'sticky':'w'}}"})

        def show_hourdetaildlg(self, owner: Dialog | None = None, x: int = 0, y: int = 0,
                **kwargs: object):
            kwargs.update({"name": "English Read"})
            self._hourdetail_dlg.do_show(owner, x+20, y+20, **kwargs)

        def _hourdetaildlg_beforego(self, **kwargs: object):
            # po(f"_hourdetaildlg_beforego: {kwargs}")

            lbl_item = cast(LabelCtrl, self.get_control("lblInfoHourDetail"))
            lbl_item.set_text(cast(str, kwargs["name"]))

            week_day = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

            limit_ydata: list[float] = [0] * 7

            per_minutes = 60
            limit_ydata = [per_minutes, per_minutes, per_minutes, \
                per_minutes, per_minutes, per_minutes, per_minutes]

            plt_everyday = cast(MatPlotCtrl, self.get_control("pltEveryDayHour"))
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
                minutes = random.randint(0, 15)
                father_ydata.append(minutes)
                # limit_ydata.append(1.0)
                # po(f"minutes of {day} is {minutes}")
                for sid in range(3):
                    minutes = random.randint(0, 15)
                    if children_ydata.get(sid) is None:
                        children_ydata[sid] = [minutes]
                    else:
                        children_ydata[sid].append(minutes)
            plt_everyday.xdata = xdata
            father_yline = LineData(father_ydata,
                {"tick_label":labels,"width":0.4,"facecolor":"green"}, "bar")
                # {"width":0.4,"facecolor":"green"}, "bar")
            _ = plt_everyday.add_line(father_yline)
            bottom = father_ydata
            for sid, child_ydata in children_ydata.items():
                child_yline = LineData(child_ydata, {"width":0.4,"bottom":bottom}, "bar")
                bottom = child_ydata
                _ = plt_everyday.add_line(child_yline)
            limit_yline = LineData(limit_ydata, {"linestyle":"dotted","color":"red"})
            _ = plt_everyday.add_line(limit_yline)
            plt_everyday.draw()

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
                    case "cancel":
                        return self._hourdetaildlg_cancel(**kwargs)
                    case _:
                        return None
                return True
            return None

        def show_tododetaildlg(self, owner: Dialog | None = None, x: int = 0, y: int = 0,
                **kwargs: object):
            dlg_id = "dlgTodoDetail"
            dlg_cfg = self.get_customctrlcfg(dlg_id)
            dlg = TodoDetailDlg(self, dlg_cfg)
            # self._gui.register_customctrl(dlg_id, recordhour_dlg)
            dlg.do_show(owner, x+20, y+20, **kwargs)

        @override
        def process_message(self, idmsg: str, **kwargs: object):
            match idmsg:
                case "meuShowInfoBox":
                    self.show_info('Python Message Info Box', '通知：程序运行正常！')
                case "WarnBox":
                    self.show_warn('Python Message Warning Box', '警告：程序出现错误，请检查！')
                case "ErrorBox":
                    self.show_err('Python Message Error Box', '错误：程序出现严重错误，请退出！')
                case "ChoiceBox":
                    answer = self.ask_yesno("Python Message Dual Choice Box", "你喜欢这篇文章吗？\n您的选择是：")
                    if answer:
                        self.show_info('显示选择结果', '您选择了“是”，谢谢参与！')
                    else:
                        self.show_info('显示选择结果', '您选择了“否”，谢谢参与！')
                case "varRadSel":
                    values = ["富强民主", "文明和谐", "自由平等", "公正法治", "爱国敬业", "诚信友善"]
                    monty2 = cast(LabelFrameCtrl, self.get_control("控件示范区2"))
                    idx = cast(int, kwargs["val"])
                    monty2.configure(text=values[idx])
                case "varChkEna":
                    check_btn = cast(CheckButtonCtrl, self.get_control("遵从内心"))
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
                    btn = cast(ButtonCtrl, self.get_control("点击之后_按钮失效"))
                    name = cast(EntryCtrl, self.get_control("name"))
                    btn.configure(text='Hello\n ' + name.get_val())
                    # self.disable_control(btn)
                    btn.disable()
                case "blankSpin":
                    spin = cast(tk.Spinbox, self.get_control("blankSpin"))
                    value = spin.get()
                    scr = cast(scrolledtext.ScrolledText, self.get_control("scrolledtext"))
                    scr.insert(tk.INSERT, value + '\n')
                case "bookSpin":
                    spin = cast(tk.Spinbox, self.get_control("bookSpin"))
                    value = spin.get()
                    scr = cast(scrolledtext.ScrolledText, self.get_control("scrolledtext"))
                    scr.insert(tk.INSERT, value + '\n')
                case "btnHaa":
                    ctrl = cast(ListboxCtrl, self.get_control("lstHaa"))
                    self._i += 1
                    ctrl.insert("end", f"第{self._i:02}项")
                case "btnLeftVAdd":
                    ctrl = cast(ScrollableFrameCtrl, self.get_control("frmLeftContentArea"))
                    self._idx_left_vertical += 1
                    num_row = self._idx_left_vertical
                    id_lbl = f"lblLeftV{num_row}"
                    self._create_label(ctrl, id_lbl, num_row, f"垂直内容{num_row}")
                case "btnLeftVSub":
                    id_lbl = f"lblLeftV{self._idx_left_vertical}"
                    self.delete_control(id_lbl)
                    self._idx_left_vertical -= 1
                case "btnLeftHAdd":
                    ctrl = cast(ScrollableFrameCtrl, self.get_control("frmLeftContentArea"))
                    self._idx_left_horizontal += 1
                    num_row = self._idx_left_horizontal
                    id_lbl = f"lblLeftH{num_row}"
                    self._create_label(ctrl, id_lbl, num_row, f"{'水平内容'*num_row}")
                case "btnLeftHSub":
                    id_lbl = f"lblLeftH{self._idx_left_horizontal}"
                    self.delete_control(id_lbl)
                    self._idx_left_horizontal -= 1
                case "btnRightVAdd":
                    ctrl = cast(ScrollableFrameCtrl, self.get_control("frmRightContentArea"))
                    self._idx_right_vertical += 1
                    num_row = self._idx_right_vertical
                    id_lbl = f"lblRightV{num_row}"
                    self._create_label(ctrl, id_lbl, num_row, f"垂直内容{num_row}")
                case "btnRightVSub":
                    id_lbl = f"lblRightV{self._idx_right_vertical}"
                    self.delete_control(id_lbl)
                    self._idx_right_vertical -= 1
                case "btnRightHAdd":
                    ctrl = cast(ScrollableFrameCtrl, self.get_control("frmRightContentArea"))
                    self._idx_right_horizontal += 1
                    num_row = self._idx_right_horizontal
                    id_lbl = f"lblRightH{num_row}"
                    self._create_label(ctrl, id_lbl, num_row, f"{'水平内容'*num_row}")
                case "btnRightHSub":
                    id_lbl = f"lblRightH{self._idx_right_horizontal}"
                    self.delete_control(id_lbl)
                    self._idx_right_horizontal -= 1
                case "About":
                    pass
                case "ShowHourdetailDialog":
                    # x, y = cast(tuple[int, int], kwargs["mousepos"])
                    x, y = self._xx, self._yy
                    self.show_hourdetaildlg(self, x+20, y+20, **kwargs)
                case "ShowTododetailDialog":
                    x, y = self._xx, self._yy
                    self.show_tododetaildlg(self, x+20, y+20, **kwargs)
                case _:
                    return super().process_message(idmsg, **kwargs)
            return True

    filepath = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        filepath = os.path.dirname(os.path.abspath(sys.executable))
    winsample_xml = os.path.join(filepath, "resources", "windowSample.xml")
    eapp = ExampleApp(filepath, winsample_xml)
    eapp.go()


if __name__ == "__main__":
    test_gui()
