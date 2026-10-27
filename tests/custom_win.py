import tkinter as tk
from collections.abc import Callable
from tkinter import Tk
from typing import Any, TypeVar
from xml.etree import ElementTree as ET


# ============================================================
# 2. 自定义控件基类
# ============================================================
class CustomWidget:
    """ 所有可注册控件的基类。
    子类只需实现 _build()，把最终 widget 赋给 self.widget。
    """

    def __init__(self, parent: "CustomWidget", **kwargs):
        self.parent: CustomWidget = parent
        self.options = kwargs
        self.widget = None
        self._build()

    def _build(self):
        raise NotImplementedError


W = TypeVar("W", bound="CustomWidget")

# ============================================================
# 1. 控件注册表
# ============================================================
class WidgetRegistry:
    _widgets: dict[str, type] = {}

    @classmethod
    def register(cls, tag: str):
        """装饰器用法：@WidgetRegistry.register('MyTag')"""
        def deco(widget_cls):
            cls._widgets[tag] = widget_cls
            return widget_cls
        return deco

    @classmethod
    def get(cls, tag: str) -> type:
        if tag not in cls._widgets:
            raise KeyError(
                f"未注册的控件 tag: '{tag}'。" +
                f"请先用 @WidgetRegistry.register('{tag}') 注册。"
            )
        return cls._widgets[tag]

    @classmethod
    def known_tags(cls):
        return list(cls._widgets.keys())



# ============================================================
# 3. 内置控件（一样通过注册表注册）
# ============================================================
@WidgetRegistry.register("Label")
class Label(CustomWidget):
    def _build(self):
        self.widget = tk.Label(self.parent, **self.options)
        self.widget.pack(anchor="w", padx=4, pady=2)


@WidgetRegistry.register("Button")
class Button(CustomWidget):
    def _build(self):
        self.widget = tk.Button(self.parent, **self.options)
        self.widget.pack(anchor="w", padx=4, pady=2)


@WidgetRegistry.register("Frame")
class Frame(CustomWidget):
    def _build(self):
        self.widget = tk.Frame(self.parent, **self.options)
        self.widget.pack(fill="x", padx=4, pady=2)


# ============================================================
# 4. 用户自定义控件 —— 关键点：只要加一行装饰器
# ============================================================
@WidgetRegistry.register("StarRating")
class StarRating(CustomWidget):
    """ 一个自定义控件：星级评分
    支持的 XML 属性: value(int), max(int), color(str), font(str)
    """

    def _build(self):
        self.value = int(self.options.pop("value", 0))
        self.max_stars = int(self.options.pop("max", 5))
        color = self.options.pop("color", "gold")
        font = self.options.pop("font", "Arial 16")

        self.frame = tk.Frame(self.parent, **self.options)
        self.frame.pack(anchor="w", padx=4, pady=2)

        self.star_labels = []
        for i in range(self.max_stars):
            lbl = tk.Label(
                self.frame, text="★", font=font,
                fg=color if i < self.value else "lightgray",
            )
            lbl.pack(side="left")
            self.star_labels.append(lbl)

        self.widget = self.frame

    # 可选：暴露给外部代码使用的方法
    def set_value(self, v: int):
        self.value = v
        for i, lbl in enumerate(self.star_labels):
            lbl.config(fg="gold" if i < v else "lightgray")


@WidgetRegistry.register("Card")
class Card(CustomWidget):
    """另一个自定义控件：标题卡片"""
    def _build(self):
        title = self.options.pop("title", "")
        bg = self.options.pop("bg", "#eef")
        self.frame = tk.Frame(self.parent, bg=bg, bd=1, relief="solid")
        self.frame.pack(fill="x", padx=4, pady=4)
        tk.Label(self.frame, text=title, bg=bg,
                 font=("Arial", 12, "bold")).pack(anchor="w", padx=6, pady=4)
        self.widget = self.frame


# ============================================================
# 5. 窗口类：读 XML → 查表 → 递归构建
# ============================================================
class XMLWindow:
    def __init__(self, xml_source: str):
        self.root: Tk = tk.Tk()
        self._instances: list[CustomWidget] = []          # 保存所有控件实例，方便后续访问
        self._load(xml_source)

    # ---------- 加载 ----------
    def _load(self, xml_source: str):
        if xml_source.lstrip().startswith("<"):
            root_elem = ET.fromstring(xml_source)
        else:
            root_elem = ET.parse(xml_source).getroot()

        # 顶层窗口自身属性
        for k, v in root_elem.attrib.items():
            self._apply_window_attr(k, self._convert(v))

        # 递归构建子控件
        for child in root_elem:
            self._build_widget(child, self.root)

    def _apply_window_attr(self, key: str, value):
        if key == "title":
            self.root.title(str(value))
        elif key == "width" or key == "height":
            w = value if key == "width" else self.root.winfo_width()
            h = value if key == "height" else self.root.winfo_height()
            self.root.geometry(f"{w}x{h}")
        # 其他属性自行扩展

    # ---------- 核心：根据 tag 实例化 ----------
    def _build_widget(self, elem: ET.Element, parent_widget: CustomWidget):
        try:
            widget_cls = WidgetRegistry.get(elem.tag)
        except KeyError as e:
            raise RuntimeError(f"XML 中 <{elem.tag}> 未注册") from e

        # 属性转换为 Python 类型
        kwargs = {k: self._convert(v) for k, v in elem.attrib.items()}

        # 实例化控件（这就是"通过 tag 调用自定义控件类"）
        instance = widget_cls(parent_widget, **kwargs)
        self._instances.append(instance)

        # 递归构建子控件，父级是 instance.widget
        if instance.widget is not None:
            for sub in elem:
                self._build_widget(sub, instance.widget)
        return instance

    # ---------- 属性类型自动推断 ----------
    @staticmethod
    def _convert(s: str) -> Any:
        v = s.strip()
        low = v.lower()
        if low in ("true", "yes"):   return True
        if low in ("false", "no"):   return False
        if low == "none":            return None
        try:    return int(v)
        except ValueError: pass
        try:    return float(v)
        except ValueError: pass
        return v

    def run(self):
        self.root.mainloop()


# ============================================================
# 6. 使用
# ============================================================
if __name__ == "__main__":
    xml_config = """
    <Window title="XML 驱动的窗口" width="480" height="320">
        <Label text="欢迎使用 XML 构建 UI" font="Arial 14" />
        <Card title="用户评分">
            <StarRating value="3" max="5" color="gold" />
        </Card>
        <Card title="操作">
            <Button text="确定" />
            <Button text="取消" />
        </Card>
    </Window>
    """

    win = XMLWindow(xml_config)
    win.run()