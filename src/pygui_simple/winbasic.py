#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations

import abc
import os
import xml.etree.ElementTree as et
from collections import OrderedDict
from collections.abc import Callable, ItemsView
from typing import ClassVar, Literal, Protocol, TypeVar, cast, override

from pyutilities_simple.logit import po


class Widget:
    #: If True, this control creates its own child controls.
    #: The parent window / container skips automatic child creation during setup.
    _handles_child_creation: bool = False

    def __init__(self, parent: Widget | None = None, ctrl_cfg: et.Element | None = None,
            owner: WinBasic | None = None):
        self._control: object = None
        self._level: int = -1

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, ctrl: object):
        self._control = ctrl

    @property
    def handles_child_creation(self):
        return self._handles_child_creation

    @handles_child_creation.setter
    def handles_child_creation(self, val: bool):
        self._handles_child_creation = val

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, val: int):
        self._level = val

W = TypeVar("W", bound=Widget)

class WidgetRegistry:
    """ A global static registry for Widget subclasses.
    Provides decorator API to register widget classes by string tag,
    and lookup API to retrieve widget classes by tag at runtime.
    """

    # Class-level storage: tag string -> Widget subclass type
    # ClassVar means this dict belongs to the WidgetRegistry class, not instances.
    _widgets: ClassVar[dict[str, type[Widget]]] = {}

    def __init__(self):
        # Instance creation is allowed, but we do not store state on instances.
        # All data lives on the class itself via classmethods.
        pass

    @classmethod
    def register(cls, tag: str):
        """ Decorator factory. Accept a tag name and return a decorator.
        Usage: @WidgetRegistry.register("my_widget_tag")

        Args:
            tag: Unique string identifier for this widget type.
        Returns:
            A decorator that accepts a Widget subclass and registers it.
        """
        def deco(widget_cls: type[W]):
            # Bind the widget class to the given tag in the registry dict
            cls._widgets[tag] = widget_cls
            # Return the original widget class unchanged (decorator identity wrap)
            return widget_cls
        return deco

    @classmethod
    def get(cls, tag: str):
        """ Look up a widget class by tag.

        Args:
            tag: The tag string used during registration.
        Returns:
            Widget subclass if found; None if the tag does not exist.
        """
        if tag not in cls._widgets:
            return None
        return cls._widgets[tag]

    @classmethod
    def known_tags(cls):
        """ Return a list of all registered widget tag names.
        Useful for inspection, debug UI, or enumeration.
        """
        return list(cls._widgets.keys())

class Control(Widget, metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self._backed: bool = True

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

# EventHanlder: TypeAlias = Callable[[tuple[Any, ...], dict[str, Any]], Any]
# EventHanlder: TypeAlias = Callable[[dict[str, Any]], Any]
# EventHanlder: TypeAlias = Callable[[Mapping[str, Any]], Any]
class EventHanlder(Protocol):
    def __call__(self, **kwargs: object) -> object: ...

# EventsHanlder: TypeAlias = Callable[[str, dict[str, Any]], Any]
# EventsHanlder: TypeAlias = Callable[[str, Mapping[str, Any]], Any]
class EventsHanlder(Protocol):
    def __call__(self, idmsg: str, **kwargs: object) -> object: ...

F = TypeVar("F", bound=Callable[..., object])

def on_message(*msg_ids: str) -> Callable[[F], F]:
    """ Decorator factory: accept one or multiple message id strings, return a decorator.
    The returned decorator attaches the message id tuple as an attribute to the target function.

    Args:
        msg_ids: Variable-length positional arguments of string message identifiers.
    Returns:
        A decorator that takes a function and returns the same function with extra metadata.
    """
    def decorator(func: F) -> F:
        """ Attach the tuple of message ids to the function object as attribute _message_ids.

        Args:
            func (F): _description_

        Returns:
            F: _description_
        """
        func._message_ids = tuple(msg_ids)  # pyright: ignore[reportFunctionMemberAccess]
        # setattr(func, "_message_ids", tuple(msg_ids))
        return func
    return decorator

class Container(Widget, metaclass=abc.ABCMeta):
    # Class-level registry: maps message-id string -> list of handler method names
    # ClassVar: this attribute lives on the class, not on instances
    # We initialize with an empty dict as a placeholder; __init_subclass__ will replace it for each subclass
    _handlers: ClassVar[dict[str, list[str]]] = {}
    def __init__(self, owner: Container | None = None):
        super().__init__()
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

    def __init_subclass__(cls, **kwargs: object):
        """ Special class method: automatically invoked once when a subclass of Container is defined.
        This builds and merges the message handler registry for the new subclass.

        Args:
            **kwargs: Extra keyword arguments passed down from subclass definition.
        """
        super().__init_subclass__(**kwargs)
        # Local temporary registry being built for this subclass
        handlers: dict[str, list[str]] = {}
        # default: str | None = None

        # Step 1: Inherit handlers from all parent classes.
        # reversed(cls.__mro__[1:]): traverse MRO (method resolution order), skip cls itself.
        # Reversed order ensures closer parent classes override / append after distant ancestors.
        for base in reversed(cls.__mro__[1:]):
            # Read parent's _handlers dict; fall back to empty dict if attribute does not exist
            for mid, names in cast(dict[str, list[str]], getattr(base, "_handlers", {}).items()):
                # Get or create the handler list bucket for this message-id (mid)
                bucket = handlers.setdefault(mid, [])
                for n in names:
                    if n not in bucket:
                        bucket.append(n)
            # base_default = getattr(base, "_default_handler", None)
            # if base_default:
            #     default = base_default

        # Step 2: Scan methods defined directly on this subclass,
        # collect methods marked by the @on_message decorator (which adds _message_ids).
        for name, attr in cast(ItemsView[str, object], vars(cls).items()):
            ids: tuple[str, ...] | None = getattr(attr, "_message_ids", None)
            if ids:
                # dict.fromkeys removes duplicate message ids declared on the same method
                for mid in dict.fromkeys(ids):
                    bucket = handlers.setdefault(mid, [])
                    if name not in bucket:
                        bucket.append(name)
            # if getattr(attr, "_is_default", False):
            #     default = name

        # Assign the merged registry to the subclass's _handlers
        cls._handlers = handlers
        # cls._default_handler = default

    def register_eventhandler(self, idmsg: str, handler: EventHanlder):
        """ _summary_

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
        """ filter message to deal with

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
            elif typ == -1 and idmsg not in msglst:
                ret = hander(idmsg, **kwargs)
                if ret is not None:
                    return ret

        funcs = self._eventhandler_dict.get(idmsg, None)
        if funcs is not None:
            ret = None
            for func in funcs:
                ret = func(**kwargs)
            return ret

        names = self._handlers.get(idmsg)
        if names:
            result: object = None
            for name in names:
                handler = cast(EventHanlder, getattr(self, name))
                # result = handler(idmsg, **kwargs)
                result = handler(**kwargs)
            return result  # 多播时返回最后一个处理函数的结果

        # if self._default_handler is not None:
        #     handler = getattr(self, self._default_handler)
        #     return handler(idmsg, **kwargs)

        if self._owner is not None:
            return self._owner.process_message(idmsg, **kwargs)
        po(f"Container: undeal msg of {idmsg} with {kwargs}")
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

    def movie_window(self, x: int, y: int, w: int, h: int):
        self._xx = x
        self._yy = y
        self._ww = w
        self._hh = h

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
            ctrl = widget_cls(parent, ctrl_cfg, owner)
            ctrl.level = level
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
        if tag == "CustomDialog":   # TODO: wait to delete
            attr_dict = ctrl_cfg.attrib
            idctrl = attr_dict["id"]
            self._customctrlcfg_dict[idctrl] = ctrl_cfg
            return idctrl_dict
        idctrl, ctrl = self.create_control(parent, ctrl_cfg, level, owner)
        idctrl_dict[idctrl] = ctrl

        if ctrl.handles_child_creation:
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
            del self._idctrl_dict[idctrl]
        except AttributeError:
            print(f"WinBasic warnning: {idctrl} doesn't have destroy")            
        # del self._idctrl_dict[idctrl]

    def get_control(self, idctrl: str):
        return self._idctrl_dict[idctrl]

    def read_customctrlcfg(self, cfgpath: str):
        cfgfile = os.path.join(self._app_path, cfgpath)
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
    def center_window(self, width: int, height: int):
        pass

    @abc.abstractmethod
    def show_err(self, title: str = "", message: str = ""):
        pass

    @abc.abstractmethod
    def go(self):
        pass


class Dialog(WinBasic, metaclass=abc.ABCMeta):
    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        self.handles_child_creation = True  # pyright: ignore[reportUnannotatedClassAttribute]

        self._xx: int = 0
        self._yy: int = 0
        self._ww: int = width
        self._hh: int = height
        self._title: str = title

    @property
    def backed(self):
        return self._backed

    def _beforego(self, **kwargs: object):
        _ = self.process_message("beforego", **kwargs)

    def _confirm(self, **kwargs: object):
        _ = self.process_message("confirm", **kwargs)
        return self.destroy(confirm=True, **kwargs)

    def _cancel(self, **kwargs: object):
        _ = self.process_message("cancel", **kwargs)
        return self.destroy(confirm=False, **kwargs)
