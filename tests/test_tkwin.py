#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
    uv pip install e .
    uv run .\tests\test_tkwin.py
"""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import scrolledtext
from typing import cast, override

from pygui_simple.tkcontrol import tkControl
from pygui_simple.tkwin import (
    ButtonCtrl,
    CheckButtonCtrl,
    EntryCtrl,
    LabelFrameCtrl,
    ListboxCtrl,
    ScrollableFrameCtrl,
    tkWin,
)
from pygui_simple.winbasic import Container


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

    def _create_label(self, parent: tkControl, lid: str, rowid: int, txt: str):
        lbl_xml = self._gui.create_xml("Label", {"text": txt, "id": lid})
        _, lbl_ctrl = self._gui.create_control(parent, lbl_xml, 0, self)
        self._gui.assemble_control(lbl_ctrl, {"layout":"grid",
            "grid":f"{{'row':{rowid},'column':0,'sticky':'w'}}"})

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
                btn.configure(text='Hello\n ' + name.get_text())
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
