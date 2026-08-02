#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
import os

from pygui_simple.tkwin import tkWin

from src.hour_tab import HourTab


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
    
        self._tab_hour: HourTab = HourTab(self._gui)

    def open(self):
        hours_db_path = os.path.join(self._app_path, "data", "hours.db")
        if not os.path.isfile(hours_db_path):
            self._tab_hour.new_hours(hours_db_path)
        else:
            self._tab_hour.open_hours(hours_db_path)

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
    app.run()
    app.destroy()

if __name__ == "__main__":
    main()
