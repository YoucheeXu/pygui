#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import datetime
import tkinter as tk
import xml.etree.ElementTree as et
from typing import cast, override

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import Container, WinBasic, on_message

from src.action_sys import ActTyp
from src.database.time_database import TimeDatabase
from src.database.time_database_type import (
    PlanDataDict,
    ReminderDataDict,
    StatusEnum,
)
from src.pagectrl import PageCtrl
from src.schedule import Schedule
from src.todo.dialog_edit import EditTodoDialog
from src.todo.page_project import ProjectPage
from src.todo.page_today import TodayTodoPage
from src.todo.todo_type import (
    ReminderInfo,
    Todo,
    TodoData,
    TodosDict,
)


class TodoTab(Container):
    """_summary_

    Attributes:
        _gui (_type_): _description_
        _schedule (_type_): _description_
        _todo_db (_type_): _description_
    """
    def __init__(self, owner: WinBasic, schedule: Schedule) -> None:
        """_summary_

        Args:
            owner (_type_): _description_
            schedule (_type_): _description_
        """
        super().__init__()

        self._app: WinBasic = owner
        self._app.filter_message(self.process_message)
        self._schedule: Schedule = schedule

        self._todos_db: TimeDatabase = TimeDatabase()
        self._todos: TodosDict = {}
        self._eids: list[int] = []

        self._active_page_name: str | None = None

        self._pages: dict[str, PageCtrl] = {}
        # self._pages_frame: dict[str, tk.Frame] = {}

        tudu_tab = self._app.get_control("tabTodo")
        # self._pages["TodayTodo"] = TodayTodoPage(tudu_tab, self._app, "Today")
        self._today_page: TodayTodoPage = TodayTodoPage(tudu_tab, self._app, "Today")
        self._pages["TodayTodo"] = self._today_page
        self._pages["Project"] = ProjectPage(tudu_tab, self._app, "Project")

        parent = cast(tk.Frame, cast(tkControl, self._app.get_control("tabTodo")).control)
        for page in self._pages.values():
            # page.frame.grid(row=0, column=0, sticky="nsew")
            page.assemble({"layout": "grid",
                        "grid": "{'row':0, 'column':0, 'sticky':'nsew'}"})
        _ = parent.grid_rowconfigure(0, weight=1)
        _ = parent.grid_columnconfigure(0, weight=1)

        self._main_pages_frame: tk.Frame = cast(tk.Frame, cast(tkControl, self._app.get_control("frmMainTodo")).control)

        frame = cast(tk.Frame, cast(tkControl, self._app.get_control("frmTodayTodo")).control)
        _ = frame.bind("<Button-1>", lambda e: self._show_page("TodayTodo"))

        self._editdlg_cfg: et.Element = self._app.read_customctrlcfg("resources\\EditTodoDlg.xml")

    def _open(self, db_path: str):
        """_summary_
        Args:
            db_path (type): _description_
        """
        _ =  self._todos_db.open(db_path)

    def new_todos(self, db_path: str):
        """_summary_
        Args:
            db_path (type): _description_
        """
        _ = self._open(db_path)

    def open_todos(self, db_path: str):
        """_summary_
        Args:
            db_path (type): _description_
        """
        _ = self._open(db_path)

        plans = self._todos_db.read_plans()
        for tid, plandata in plans.items():
            eids = list(plandata["reminders"].keys())
            if len(eids) > 0:
                eid = eids[0]
                reminderdata = plandata["reminders"][eid]
                if clock_time := reminderdata["clk_time"]:
                    self._schedule.add_event(eid, plandata["name"], clock_time, reminderdata["every"],
                        reminderdata["unit"], reminderdata["custom"],
                        reminderdata["cycbgn_dtime"], reminderdata["cycend_dtime"],
                        ActTyp.DRIPPING_WATER)
                tudu: TodoData = {
                    "name": plandata["name"],
                    "note": plandata["note"],
                    "tags": plandata["tags"],
                    "fid": plandata["fid"],
                    "status": plandata["status"],
                    "reminder_id": eid,
                    "reminder": reminderdata,
                    "reminder_infos": []
                }
                self._todos[tid] = tudu

        self._show_page("TodayTodo")

    def _get_todos_by_day(self, day: datetime.date):
        tudus: TodosDict = {}

        for tid, todo in self._todos.items():
            eid = todo["reminder_id"] 
            if eid == 0:
                reminderdata = todo["reminder"]
                assert reminderdata is not None
                cycbgn_dtime = reminderdata["cycbgn_dtime"]
                assert cycbgn_dtime is not None
                if cycbgn_dtime.date() == day:
                    tudus[tid] = todo
            else:
                day_agenda = self._schedule.agendas_on_date(day)
                if eid in day_agenda:
                    tudus[tid] = todo
                    agendas = day_agenda[eid]
                    for agenda in agendas:
                        reminderinfo: ReminderInfo = {
                            "clock_time": agenda.clock,
                            "completed": False
                        }
                        tudus[tid]["reminder_infos"].append(reminderinfo)

        return tudus

    def open_todo_detail_dlg(self, x: int, y: int, **kwargs: object) -> None:
        # dlg_id = "dlgEditTodo"
        # dlg_cfg = self._app.get_customctrlcfg(dlg_id)
        editodo_dlg = EditTodoDialog(self._app, self._editdlg_cfg, self._app)
        editodo_dlg.do_show(self, (x, y), **kwargs)

    def _show_page(self, page_name: str):
        for name, page in self._pages.items():
            if name == page_name:
                self._active_page_name = name
                self._update_page()
                page.show()
            else:
                page.hide()

    def _update_page(self):
        assert self._active_page_name is not None
        page_name = self._active_page_name

        if page_name == "TodayTodo":
            today_todos: TodosDict = {}
            now = datetime.datetime.now()
            for tid, tododata in self._todos.items():
                cycbgn_dtime = tododata["reminder"]["cycbgn_dtime"]
                cycend_dtime = tododata["reminder"]["cycend_dtime"]
                assert cycbgn_dtime is not None
                if tododata["status"] == StatusEnum.ONGOING and cycbgn_dtime <= now:
                    if cycend_dtime is None or cycend_dtime >= now:
                        today_todos[tid] = tododata

            tudus = self._get_todos_by_day(now.date())
            today_todos |= tudus
            self._today_page.todos = today_todos

    @on_message("ShowPage")
    def on_show_page(self, **kwargs: object):
        page_name = cast(str, kwargs["page"])
        self._show_page(page_name)

        return True

    @on_message("ShowMainPage")
    def on_show_mainpage(self, **_: object):
        self._main_pages_frame.tkraise()
        self._active_page_name = None

        return True

    @on_message("lblTitleToday", "lblNumberToday")
    def on_show_todaypage(self, **_: object):
        self._show_page("TodayTodo")

        return True

    @on_message("lblTitleProject", "lblNumberProject")
    def on_show_projectpage(self, **_: object):
        self._show_page("Project")

        return True

    @on_message("OpenEditTodoDlg")
    def on_show_editdlg(self, **kwargs: object):
        # tudu_dict = cast(TodoDict, kwargs['todo_dict'])
        x, y = cast(tuple[int, int], kwargs['mousepos'])
        self.open_todo_detail_dlg(x, y, **kwargs)

        return True

    @on_message("NewTodo")
    def on_new_todo(self, **kwargs: object):
        plandata = cast(PlanDataDict, kwargs["plandata"])
        reminderdata: ReminderDataDict = cast(ReminderDataDict, kwargs["reminderdata"])
        tid = self._todos_db.add_plan(**plandata)
        _ = self._todos_db.add_reminder(tid, 0, **reminderdata)
        tudu = cast(TodoData, kwargs['tododata'])
        self._todos[tid] = tudu
        return tid

    @on_message("ModifyTodo")
    def on_modify_todo(self, **kwargs: object):
        tudu = cast(Todo, kwargs["todo"])

        tududata = tudu["data"]
        # plandata: PlanDataDict = {
        #     "name": tududata["name"],
        #     "note": tududata["note"],
        #     "tags": tududata["tags"],
        #     "iid": None,
        #     "fid": tududata["fid"],
        #     "reminders": {},
        #     "action": ActTyp.NOACTION,
        #     "status": tududata["status"],
        #     "location": None,
        #     "sums": 0
        # }

        tid = tudu["tid"]
        # _ = self._todos_db.modify_plan(tid, **plandata)
        if eid := tududata["reminder_id"]:
            reminderdata = tududata["reminder"]
            if self._todos[tid]["reminder_id"]:
                _ = self._todos_db.del_reminder(tid, 0)
                _ = self._todos_db.add_reminder(tid, eid, **reminderdata)
            else:
                _ = self._todos_db.modify_reminder(tid, eid, **reminderdata)
            clock_time = reminderdata["clk_time"]
            assert clock_time is not None
            cycbgn_dtime = reminderdata["cycbgn_dtime"]
            assert cycbgn_dtime is not None
            if eid in self._schedule.events:
                _ = self._schedule.modify_event(eid, clock_time, cycbgn_dtime, tududata["name"], 
                    reminderdata["every"], reminderdata["unit"], reminderdata["custom"], reminderdata["cycend_dtime"])
            else:
                self._schedule.add_event(eid, tududata["name"], clock_time, reminderdata["every"],
                reminderdata["unit"], reminderdata["custom"],
                cycbgn_dtime, reminderdata["cycend_dtime"],
                ActTyp.DRIPPING_WATER)

        self._todos[tid] = tudu["data"]
        self._update_page()

        if self._active_page_name:
            self._pages[self._active_page_name].refresh()

        return True

    @override
    def destroy(self, **kwargs: object):
        """ _summary_
        """
        for page in self._pages.values():
            page.destroy(**kwargs)
        self._pages.clear()
        super().destroy(**kwargs)
