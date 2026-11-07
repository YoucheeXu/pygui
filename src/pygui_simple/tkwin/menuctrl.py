import tkinter as tk
import xml.etree.ElementTree as et
from ast import literal_eval
from typing import Any, cast

from pygui_simple.tkwin.tkcontrol import tkControl
from pygui_simple.winbasic import (
    Widget,
    WidgetRegistry,
    WinBasic,
)


@WidgetRegistry.register("Menu")
class MenuCtrl(tkControl):
    def __init__(self, idself: str, ctrl_cfg: et.Element, parent: Widget, owner: WinBasic):
        attr_dict = ctrl_cfg.attrib
        master = cast(tk.Misc, parent.control)
        kwargs: dict[str, Any] = {}
        if "kwargs" in attr_dict:
            kwargs = eval(attr_dict["options"])

        menubar = tk.Menu(master, **kwargs)
        super().__init__("", master, idself, menubar)

        def get_cmd(cmd_name: str, **kwargs: object):
            return lambda: owner.process_message(cmd_name, **kwargs)

        def get_cmd_e(cmd_name: str, **kwargs: object):
            return lambda event: owner.process_message(cmd_name, **kwargs)

        win = cast(tk.Tk, owner.control)

        for menuitemcfg in list(ctrl_cfg):
            attr_dict = menuitemcfg.attrib
            label = attr_dict["Header"]
            owner.debug_print(f"  Menu: {label}")
            menu = tk.Menu(menubar, tearoff=False)

            if "options" in attr_dict:
                options = literal_eval(attr_dict["options"])
            else:
                options = {}

            for submenucfg in list(menuitemcfg):
                tag = submenucfg.tag
                subattr_dict = submenucfg.attrib
                if tag == "Separator":
                    menu.add_separator()
                    owner.debug_print(f"    subMenu: {submenucfg.tag}")
                    continue
                if "options" in subattr_dict:
                    sub_options = literal_eval(subattr_dict["options"])
                else:
                    sub_options = {}
                sub_label = subattr_dict["Command"]
                if "id" in subattr_dict:
                    idmenu = subattr_dict["id"]
                else:
                    idmenu = str(sub_label.replace(" ", "").replace("...", ""))
                owner.debug_print(f"    subMenu: {tag} -> {sub_label}")
                if tag == "Checkbutton":
                    var_name = subattr_dict["variable"]
                    self.__dict__[f"_{var_name}"] = tk.BooleanVar()
                    var = self.__dict__[f"_{var_name}"]
                    # var.set(True)
                    # msg = "Changed"
                    # ext_msg = var.get()
                    # cmd = get_cmd(cmd_name, msg, ext_msg)
                    kwargs = {"event": "Changed", "val": var.get()}
                    cmd = get_cmd(idmenu, **kwargs)
                    menu.add_checkbutton(
                        label=sub_label, command=cmd, variable=var, **sub_options
                    )
                elif tag == "MenuItem":
                    # msg = "Clicked"
                    # ext_msg = ""
                    kwargs = {"event": "Clicked"}
                    # cmd = get_cmd(cmd_name, msg, ext_msg)
                    cmd = get_cmd(idmenu, **kwargs)
                    menu.add_command(label=sub_label, command=cmd, **sub_options)
                else:
                    raise ValueError(f"    Unknown Menu: {tag} -> {sub_label}")

                if "accelerator" in sub_options:
                    shortcut_lst = cast(str, sub_options["accelerator"]).split("+")
                    shortcut = (
                        "<"
                        + shortcut_lst[0].replace("Ctrl", "Control").strip()
                        + "-"
                        + shortcut_lst[1].lower().strip()
                        + ">"
                    )
                    # pv(shortcut)
                    # cmd = get_cmd_e(cmd_name, msg, ext_msg)
                    cmd = get_cmd_e(idmenu, **kwargs)
                    _ = win.bind_all(shortcut, cmd)
            menubar.add_cascade(label=label, menu=menu, **options)
        _ = win.config(menu=menubar)
