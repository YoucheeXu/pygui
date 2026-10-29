#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import abc
import os
import xml.etree.ElementTree as et
from collections import OrderedDict
from typing import Literal, Protocol, TypeVar, cast, override


# EventHanlder: TypeAlias = Callable[[tuple[Any, ...], dict[str, Any]], Any]
# EventHanlder: TypeAlias = Callable[[dict[str, Any]], Any]
# EventHanlder: TypeAlias = Callable[[Mapping[str, Any]], Any]
class EventHanlder(Protocol):
    def __call__(self, **kwargs: object) -> object: ...


# EventsHanlder: TypeAlias = Callable[[str, dict[str, Any]], Any]
# EventsHanlder: TypeAlias = Callable[[str, Mapping[str, Any]], Any]
class EventsHanlder(Protocol):
    def __call__(self, idmsg: str, **kwargs: object) -> object: ...


class Widget:
    def __init__(self, idself: str, ctrl_cfg: et.Element | None = None, parent: Widget | None = None,
            owner: WinBasic | None = None, level: int = 0):
        self._idself: str = idself
        self._control: object = None
        self._level: int = level

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, ctrl: object):
        self._control = ctrl

W = TypeVar("W", bound=Widget)

class WidgetRegistry:
    _widgets: dict[str, type[Widget]] = {}

    def __init__(self):
        pass

    @classmethod
    def register(cls, tag: str):
        """装饰器用法：@WidgetRegistry.register('MyTag')"""
        def deco(widget_cls: type[W]):
            cls._widgets[tag] = widget_cls
            return widget_cls
        return deco

    @classmethod
    def get(cls, tag: str):
        if tag not in cls._widgets:
            return None
        return cls._widgets[tag]

    @classmethod
    def known_tags(cls):
        return list(cls._widgets.keys())

class Control(Widget, metaclass=abc.ABCMeta):
    def __init__(self, title: str, idself: str, level: int):
        super().__init__(idself, level=level)
        self._title: str = title
        self._backed: bool = True

    @property
    def title(self):
        return self._title

    @property
    def backed(self):
        return self._backed

    def back(self, bset: bool = True):
        self._backed = bset

    @abc.abstractmethod
    def configure(self, **kwargs: object):
        pass

    @abc.abstractmethod
    def __getitem__(self, item: str) -> object:
        pass

    @abc.abstractmethod
    def __setitem__(self, item: str, value: object):
        pass

    @abc.abstractmethod
    def hide(self, is_hide: bool = True):
        pass

    def show(self):
        self.hide(False)

    @abc.abstractmethod
    def disable(self, is_disbl: bool = True):
        pass

    def enable(self):
        self.disable(False)

    @abc.abstractmethod
    def assemble(self, attr_dict: dict[str, str], prefix: str = ""):
        pass

    @abc.abstractmethod
    def destroy(self):
        pass


class Container(Widget, metaclass=abc.ABCMeta):
    def __init__(self, owner: Container | None = None):
        super().__init__("")
        self._eventhandler_dict: dict[str, list[EventHanlder]] = {}
        self._msgs_hanlders: list[tuple[int, list[str], EventsHanlder]] = []
        self._owner: Container | None = owner

        self._backed: bool = True

        self._idctrl_dict: OrderedDict[str, Widget] = OrderedDict()

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, val: Container):
        self._owner = val  

    def back(self, bset: bool = True):
        for idctrl, ctrl in self._idctrl_dict.items():
            try:
                ctrl = cast(Control, ctrl).back(bset)
            except AttributeError as _:
                # po(f"{idctrl} doesn't support back")
                print(f"{idctrl} doesn't support back")
        self._backed = bset

    def register_eventhandler(self, idmsg: str, handler: EventHanlder):
        """_summary_

        Args:
            idmsg (str): _description_
            handler (EventHanlder): _description_
        """
        handlerlist = self._eventhandler_dict.get(idmsg)
        if handlerlist is not None:
            self._eventhandler_dict[idmsg].append(handler)
        else:
            self._eventhandler_dict[idmsg] = [handler]

    def filter_message(self, hanlder: EventsHanlder,
            typ: Literal[-1, 0, 1] = 0, msglst: list[str] | None = None):
        """filter message to deal with

        Args:
            hanlder (): hanlder to deal message
            typ ():
                1: filter all message in msglst
                0: all message
                -1: filter any message except in msglst
            msglst(): message list
        """
        if msglst is not None:
            self._msgs_hanlders.append((typ, msglst, hanlder))
        else:
            self._msgs_hanlders.append((typ, [], hanlder))
        # pv(self._msgs_hanlders)

    def process_message(self, idmsg: str, **kwargs: object) -> object:
        for typ, msglst, hander in self._msgs_hanlders:
            if typ == 0:
                ret = hander(idmsg, **kwargs)
                if ret is not None:
                    return ret
            elif typ == 1:
                if idmsg in msglst:
                    ret = hander(idmsg, **kwargs)
                    if ret is not None:
                        return ret
            elif typ == -1:
                if idmsg not in msglst:
                    ret = hander(idmsg, **kwargs)
                    if ret is not None:
                        return ret

        funcs = self._eventhandler_dict.get(idmsg, None)
        if funcs is not None:
            ret = None
            for func in funcs:
                ret = func(**kwargs)
            return ret

        if self._owner is not None:
            return self._owner.process_message(idmsg, **kwargs)
        print(f"Container: undeal msg of {idmsg} with {kwargs}")
        return None

    @abc.abstractmethod
    def destroy(self, **kwargs: object):
        pass

_T_contra = TypeVar("_T_contra", contravariant=True)
class SupportsWrite(Protocol[_T_contra]):
    def write(self, s: _T_contra, /) -> object: ...

class WinBasic(Container, metaclass=abc.ABCMeta):
    def __init__(self, app_path: str = "", xmlfile: str = ""):
        title = ""
        w, h = 0, 0
        if xmlfile:
            element_tree = et.parse(xmlfile)
            self._wincfg: et.Element[str] = element_tree.getroot()
            win_attr = self._wincfg.attrib
            title = win_attr["Title"]
            if "Width" in win_attr:
                w, h = int(win_attr["Width"]), int(win_attr["Height"])
        super().__init__()

        self._app_path: str = app_path
        self._is_debug: bool = False

        self._customctrlcfg_dict: dict[str, et.Element] = {}

        self._xx: int = 0
        self._yy: int = 0
        self._ww: int = w
        self._hh: int = h
        self._title: str = title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, val: str):
        self._title = val

    @property
    def path(self):
        return self._app_path

    @property
    def pos(self):
        return self._xx, self._yy

    @property
    def size(self):
        return self._ww, self._hh

    def create_xml(self, tag: str, attr_dict: dict[str, str], root: et.Element | None = None) -> et.Element:
        if root is not None:
            item_xml = et.SubElement(root, tag)
        else:
            item_xml = et.Element(tag)
        item_xml.attrib = attr_dict.copy()
        return item_xml

    def create_control(self, parent: Widget, ctrl_cfg: et.Element,
            level: int = 0, owner: WinBasic | None = None) -> tuple[str, Widget]:
        if owner is None:
            owner = self
        tag = ctrl_cfg.tag
        attr_dict = ctrl_cfg.attrib
        text: str | None = attr_dict.get("text")
        idctrl: str = ""
        if "id" in attr_dict:
            idctrl = attr_dict["id"]
        elif text is not None:
            idctrl = text.replace(" ", "").replace(".", "_").replace("\n", "_")
        else:
            raise RuntimeError("No id")
        self.debug_print(f"{'  '*level}{tag}, id: {idctrl}, text: {text}", end="")

        if idctrl in self._idctrl_dict:
            raise KeyError(f"{idctrl} already exists")

        if widget_cls := WidgetRegistry.get(tag):
            ctrl = widget_cls(idctrl, ctrl_cfg, parent, owner, level)
        else:
            raise KeyError(f"{tag}: unknown Control")

        self._idctrl_dict[idctrl] = ctrl

        return idctrl, ctrl

    def assemble_control(self, ctrl: Widget, attr_dict: dict[str, str], prefix: str = ""):
        if isinstance(ctrl, Control):
            ctrl.assemble(attr_dict, prefix)

    def create_controls(self, parent: Widget, ctrl_cfg: et.Element,
            level: int = 0, owner: WinBasic | None = None) -> OrderedDict[str, Widget]:
        idctrl_dict: OrderedDict[str, Widget] = OrderedDict()
        tag = ctrl_cfg.tag
        if tag == "CustomDialog":   # TODO
            attr_dict = ctrl_cfg.attrib
            idctrl = attr_dict["id"]
            self._customctrlcfg_dict[idctrl] = ctrl_cfg
            return idctrl_dict
        idctrl, ctrl = self.create_control(parent, ctrl_cfg, level, owner)
        idctrl_dict[idctrl] = ctrl
        # TODO
        if tag in ["Menu", "Notebook", "RadiobuttonGroup",
            "Statusbar", "Toolbar", "Dialog"]:
            pass
        else:
            for subctrl_cfg in list(ctrl_cfg):
                subidctrl_dict = self.create_controls(ctrl, subctrl_cfg, level + 1, owner)
                idctrl_dict.update(subidctrl_dict)
        self.assemble_control(ctrl, ctrl_cfg.attrib, f"{'  '*level}")
        return idctrl_dict

    def delete_control(self, idctrl: str):
        ctrl = cast(Control, self._idctrl_dict[idctrl])
        try:
            ctrl.destroy()
        except AttributeError:
            print(f"WinBasic warnning: {idctrl} doesn't have destroy")            
        # del self._idctrl_dict[idctrl]

    def get_control(self, idctrl: str):
        return self._idctrl_dict[idctrl]

    def read_customctrlcfg(self, cfg: str):
        cfgfile = os.path.join(self._app_path, cfg)
        element_tree = et.parse(cfgfile)
        ctrl_cfg: et.Element[str] = element_tree.getroot()
        ctrl_attr = ctrl_cfg.attrib
        idctrl = ctrl_attr["id"]
        self._customctrlcfg_dict[idctrl] = ctrl_cfg

    def get_customctrlcfg(self, idctrl: str):
        return self._customctrlcfg_dict[idctrl]

    @override
    def destroy(self, **kwargs: object):
        # pv(self._idctrl_dict.keys())
        for idctrl in reversed(list(self._idctrl_dict.keys())):
            if idctrl in self._idctrl_dict:
                # po(f"Going to delete {idctrl}")
                self.delete_control(idctrl)
        self._idctrl_dict.clear()

        super().destroy(**kwargs)

    def debug_print(self, *values: object,
        sep: str | None = " ",
        end: str | None = "\n",
        file: SupportsWrite[str] | None = None,
        flush: Literal[False] = False):
        if self._is_debug:
            print(*values, sep, end, file, flush)

class Window(WinBasic, metaclass=abc.ABCMeta):

    @property
    def win(self) -> object:
        pass

    @abc.abstractmethod
    def create_window(self):
        pass

    @abc.abstractmethod
    def show_err(self, title: str = "", message: str = ""):
        pass

    @abc.abstractmethod
    def go(self):
        pass


class Dialog(WinBasic, metaclass=abc.ABCMeta):
    def __init__(self, title: str, width: int, height: int, app: WinBasic):
        super().__init__()
        self._app: WinBasic = app

        self._xx: int = 0
        self._yy: int = 0
        self._ww: int = width
        self._hh: int = height
        self._title: str = title

    @property
    @override
    def path(self):
        return self._app.path

    @property
    def backed(self):
        return self._backed

    def _beforego(self, **kwargs: object):
        _ = super().process_message("beforego", **kwargs)

    @override
    def assemble_control(self, ctrl: Widget, attr_dict: dict[str, str], prefix: str = ""):
        return self._app.assemble_control(ctrl, attr_dict, prefix)

    def _confirm(self, **kwargs: object) -> tuple[bool, str]:
        return cast(tuple[bool, str], super().process_message("confirm", **kwargs))

    def _cancel(self, **kwargs: object) -> tuple[bool, str]:
        return cast(tuple[bool, str], super().process_message("cancel", **kwargs))

    @override
    def process_message(self, idmsg: str, **kwargs: object):
        match idmsg:
            case "beforego":
                self._beforego(**kwargs)
            case "confirm":
                return self._confirm(**kwargs)
            case "cancel":
                return self._cancel(**kwargs)
            case _:
                return super().process_message(idmsg, **kwargs)
        return True
