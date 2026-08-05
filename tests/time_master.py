#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys

from src.hour_tab import HourTab
from src.schedule import Schedule
from src.todo_tab import TodoTab

from pygui_simple.tkwin import tkWin


class TimeMasterApp:
    def __init__(self, curpath: str, xmlfile: str):
        """_summary_

        Args:
            curpath (str): _description_
            xmlfile (str): _description_
        """
        super().__init__()
        self._app_path: str = curpath

        self._gui: tkWin = tkWin(self._app_path, xmlfile)
        self._gui.filter_message(self.process_message)

        bell_path = os.path.join(self._app_path, "resources", "bell.mp3")
        wather_mp3 = os.path.join(self._app_path, "resources", "water-drop-close-sonorous.mp3")
        self._schedule: Schedule = Schedule(bell_path, wather_mp3)
    
        self._tab_hour: HourTab = HourTab(self._gui, self._schedule)
        self._tab_todo: TodoTab = TodoTab(self._gui, self._schedule)

    def open(self):
        hours_db_path = os.path.join(self._app_path, "data", "hours.db")
        if not os.path.isfile(hours_db_path):
            self._tab_hour.new_hours(hours_db_path)
        else:
            self._tab_hour.open_hours(hours_db_path)

        todo_db_path = os.path.join(self._app_path, "data", "todos.db")
        if not os.path.isfile(todo_db_path):
            self._tab_todo.new_todos(todo_db_path)
        else:
            self._tab_todo.open_todos(todo_db_path)

        self._schedule.event_to_agenda()

    def process_message(self, idmsg: str, **kwargs: object):
        match idmsg:
            case "NewUser":
                print(kwargs)
            case _:
                return None
        return True

    def run(self):
        self._gui.go()

    def destroy(self, **kwargs: object):
        """ _summary_
        """
        self._tab_hour.destroy(**kwargs)
        print("App exit!")

def main():
    file_path = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        file_path = os.path.dirname(os.path.abspath(sys.executable))
    proj_path = os.path.abspath(os.path.join(file_path, "."))
    xml_file = os.path.join(proj_path, "resources", "time_master.xml")
    print(f"xml_file = {xml_file}")
    app = TimeMasterApp(proj_path, xml_file)
    app.open()
    app.run()
    app.destroy()

if __name__ == "__main__":
    main()
