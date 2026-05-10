#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from __future__ import annotations
import calendar
import datetime
from typing import override, cast
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

from pygui.winbasic import Dialog
from pygui.tkcontrol import tkControl


class CalendarCtrl(tkControl):
    """ A tkinter-based interactive calendar control for date selection.

    This widget implements a monthly calendar UI with date picking, month/year navigation,
    and custom selection styling. It integrates with a parent Dialog component to handle
    date selection events. Built on ttk and tkinter for native GUI rendering.

    Attributes:
        _master: Parent tkinter widget container for the control
        _owner: Parent Dialog instance for event message processing
        _date: First day of the currently displayed calendar month
        _selection: Tuple of (day text, tree item ID, column) for selected date; None if unselected
        _contain_frame: Main ttk Frame holding all calendar sub-widgets
        _cal: Text/Locale calendar generator for formatting month data
        _canvas: Canvas widget for rendering date selection highlight
        _canvas_text: Text item ID on the selection canvas
        _font: Default font for calendar text rendering
        _calendar: ttk Treeview widget displaying the monthly calendar grid
        _cmb_year: ttk Combobox for year selection
        _cmb_month: ttk Combobox for month selection
        _items: List of Treeview item IDs for calendar week rows
    """
    def __init__(self, parent: tk.Misc, owner: Dialog, idself: str, **kwargs: object):
        """ Initialize the calendar control widget.

        Args:
            parent: Parent tkinter widget to host the calendar
            owner: Dialog instance that owns this control and handles events
            idself: Unique control ID for event messaging with the owner
            **kwargs: Optional configuration parameters
                fwday: First day of the week (0 = Monday, default: 0)
        """
        ctrl = ttk.Frame(parent)
        super().__init__(parent, "", idself, ctrl)

        self._master: tk.Misc = parent
        self._owner: Dialog = owner

        # first day of week, default to Monday)
        fwday = cast(int, kwargs.get("fwday", 0))
        locale = None

        # Initialize with current year/month (first day of the month)
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        self._date: datetime.date = datetime.datetime(year, month, 1)

        # No date selected by default
        self._selection: tuple[str, str, str] | None = None

        self._contain_frame: ttk.Frame = ctrl
        self._cal: calendar.TextCalendar | calendar.LocaleTextCalendar = \
            self.__get_calendar(locale, fwday)

        # Initialize UI components
        self.__setup_styles()        # Create custom ttk widget styles
        self.__place_widgets()       # Layout all sub-widgets
        self.__config_calendar()     # Configure calendar columns and headers
        self._canvas_text: int = 0
        self._font: tkFont.Font = tkFont.Font()

        # Selection style colors
        sel_bg = '#ecffc4'
        sel_fg = '#05640e'        
        self._canvas: tk.Canvas = self.__setup_selection(sel_bg, sel_fg)

        # Create 6 empty rows for calendar weeks
        self._items: list[str] = [self._calendar.insert('', 'end', values=[]) for _ in range(6)]
        # Populate and render the calendar
        self._update()
        print(f"first day of week: {self._cal.firstweekday}")

    def __get_calendar(self, locale: tuple[str | None, str | None] | None = None,
            fwday: int = 0):
        """ Create and return a configured calendar formatter.

        Args:
            locale: Locale tuple for localized calendar; None for default text calendar
            fwday: First day of the week (0 = Monday)

        Returns:
            TextCalendar or LocaleTextCalendar: Configured calendar formatting instance
        """
        if locale is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale)

    @override
    def __setitem__(self, item: str, value: object):
        """ Override item assignment for widget attributes.

        Args:
            item: Attribute name to modify
            value: New value for the attribute

        Raises:
            AttributeError: If attempting to write to read-only 'year'/'month' attributes
        """
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            _ = self._canvas.itemconfigure(self._canvas_text, item=value)
        else:
            self._contain_frame.__setitem__(item, value)

    @override
    def __getitem__(self, item: str):
        """ Override item access for widget attributes.

        Args:
            item: Attribute name to retrieve

        Returns:
            Value of the requested attribute
        """
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas_text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    def __setup_styles(self):
        """ Define custom ttk styles for calendar navigation arrow buttons."""
        style = ttk.Style(self._master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(self):
        """ Layout and position all UI widgets in the control frame."""
        # Register input validation callback for year combobox
        input_judgment_num = self._master.register(self.input_judgment)

        # Header frame (navigation + year/month selectors)
        title_frame = ttk.Frame(self._contain_frame)
        gframe = ttk.Frame(self._contain_frame)
        title_frame.pack(in_=self._contain_frame, side='top', pady=5, anchor='center')
        gframe.pack(in_=self._contain_frame, fill=tk.X, pady=5)

        # Previous/Next month buttons
        lbtn = ttk.Button(title_frame, style='L.TButton', command=self._prev_month)
        lbtn.grid(in_=title_frame, column=0, row=0, padx=12)
        rbtn = ttk.Button(title_frame, style='R.TButton', command=self._next_month)
        rbtn.grid(in_=title_frame, column=5, row=0, padx=12)

        # Year combobox (last 10 years)
        self._cmb_year: ttk.Combobox = ttk.Combobox(title_frame, width=5,
            values=[str(year) for year in range(datetime.datetime.now().year,
                datetime.datetime.now().year-11, -1)],
            validate='key', validatecommand=(input_judgment_num, '%P'))
        _ = self._cmb_year.current(0)
        self._cmb_year.grid(in_=title_frame, column=1, row=0)
        _ = self._cmb_year.bind('<KeyPress>', lambda event: self._update(event, True))
        _ = self._cmb_year.bind("<<ComboboxSelected>>", self._update)
        tk.Label(title_frame, text = '年', justify = 'left').grid(in_=title_frame, column=2, row=0, padx=(0,5))

        # Month combobox (1-12)
        self._cmb_month: ttk.Combobox = ttk.Combobox(title_frame, width=3,
            values=['%02d' % month for month in range(1,13)], state='readonly')
        _ = self._cmb_month.current(datetime.datetime.now().month - 1)
        self._cmb_month.grid(in_=title_frame, column=3, row=0)
        _ = self._cmb_month.bind("<<ComboboxSelected>>", self._update)
        tk.Label(title_frame, text='月', justify='left').grid(in_=title_frame, column=4, row=0)

        # Main calendar grid widget
        self._calendar: ttk.Treeview = ttk.Treeview(gframe, show='', selectmode='none', height=7)
        self._calendar.pack(expand=1, fill='both', side='bottom', padx=5)

    def _generate_week_cols(self, fwd: int):
        """ Generate ordered weekday column labels (Chinese) based on the first week day.

        Base order: 一 (Mon) → 日 (Sun); rotated to match the first week day.

        Args:
            fwd: First day of the week (0-6, 0 = Monday)

        Returns:
            list[str]: Rotated list of Chinese weekday labels

        Raises:
            ValueError: If fwd is outside the valid 0-6 range
        """
        BASE_WEEK = ['一','二','三','四','五','六','日']

        # Validate input (only accept valid Chinese weekdays)
        if fwd < 0 or fwd > 6:
            raise ValueError("Invalid first day! Must be: 0~6")

        # Rotate the list: put first day at index 0
        cols = BASE_WEEK[fwd:] + BASE_WEEK[:fwd]
        return cols

    def __config_calendar(self):
        """ Configure the calendar Treeview: columns, headers, and column widths."""
        cols = self._generate_week_cols(self._cal.firstweekday)
        self._calendar['columns'] = cols
        _ = self._calendar.tag_configure('header', background='grey90')
        _ = self._calendar.insert('', 'end', values=cols, tags='header')

        # Set uniform column width based on the longest weekday label
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            _ = self._calendar.column(col, width=maxwidth, minwidth=maxwidth,
            anchor='center')

    def __setup_selection(self, sel_bg: str, sel_fg: str):
        """ Initialize the selection canvas and click event bindings.

        Args:
            sel_bg: Background color for selected date highlight
            sel_fg: Text color for selected date

        Returns:
            tk.Canvas: Configured selection canvas widget
        """
        def __canvas_forget(_: tk.Event[tk.Canvas] | tk.Event[ttk.Treeview]):
            canvas.place_forget()
            self._selection = None

        canvas = tk.Canvas(self._calendar, background=sel_bg,
            borderwidth=0, highlightthickness=0)
        self._canvas_text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')

        # Bind events to clear selection
        _ = canvas.bind('<Button-1>', __canvas_forget)
        _ = self._calendar.bind('<Configure>', __canvas_forget)
        _ = self._calendar.bind('<Button-1>', self._clicked)
        return canvas

    def _build_calendar(self):
        """ Populate the Treeview with day values for the current month/year."""
        year, month = self._date.year, self._date.month
        cal = self._cal.monthdayscalendar(year, month)

        # Fill each week row with day numbers (empty string for days outside the month)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_select(self, text: str, bbox: tuple[int, int, int, int]):
        """ Render the date selection highlight on the calendar grid.

        Args:
            text: Day number to display in the selection
            bbox: Bounding box (x, y, width, height) for the selection area
        """
        x, y, width, height = bbox
        textw = self._font.measure(text)
        canvas = self._canvas

        # Resize canvas and center text
        _ = canvas.configure(width=width, height=height)
        canvas.coords(self._canvas_text, (width - textw)/2, height / 2 - 1)
        _ = canvas.itemconfigure(self._canvas_text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)

    def _clicked(self, evt: tk.Event[ttk.Treeview] | None = None,
            item: str | None = None, column: str | None = None, widget: ttk.Treeview | None = None):
        """ Handle mouse click events to select a date on the calendar.

        Triggers selection highlight and sends a 'select_date' event to the owner dialog.

        Args:
            evt: Tkinter click event; None for programmatic calls
            item: Treeview row ID (optional, for programmatic selection)
            column: Treeview column ID (optional, for programmatic selection)
            widget: Target Treeview widget (optional)
        """
        # Resolve click target from event if not provided
        if evt and not item:
            x, y, widget = evt.x, evt.y, evt.widget
            item = widget.identify_row(y)
            column = widget.identify_column(x)

        # Ignore clicks on non-day areas
        if not column or item not in self._items:
            return
        assert(widget is not None)

        item_values = widget.item(item)['values']
        if not len(item_values):
            return

        text = item_values[int(column[1]) - 1]
        if not text: 
            return

        # Delay selection if calendar is not yet rendered
        bbox = widget.bbox(item, column)
        if not bbox:
            _ = self._master.after(20, lambda: self._clicked(None, item, column, widget))
            return

        # Update selection and trigger event
        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_select(text, bbox)

        year, month = self._date.year, self._date.month
        date = datetime.date(year, month, int(self._selection[0]))
        _ = self._owner.process_message(self._idself, event="select_date", val=date)

    def _prev_month(self):
        """ Navigate to the previous month and refresh the calendar."""
        self._canvas.place_forget()
        self._selection = None

        # Calculate first day of the previous month
        self._date = self._date - datetime.timedelta(days=1)
        self._date = datetime.datetime(self._date.year, self._date.month, 1)

        # Update comboboxes and refresh UI
        self._cmb_year.set(self._date.year)
        self._cmb_month.set(self._date.month)
        self._update()

    def _next_month(self):
        """ Navigate to the next month and refresh the calendar."""
        self._canvas.place_forget()
        self._selection = None

         # Calculate first day of the next month
        year, month = self._date.year, self._date.month
        self._date = self._date + datetime.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = datetime.datetime(self._date.year, self._date.month, 1)

        # Update comboboxes and refresh UI
        self._cmb_year.set(self._date.year)
        self._cmb_month.set(self._date.month)
        self._update()

    def _update(self, event: tk.Event[ttk.Combobox] | None = None, key: bool = False):
        """ Refresh the calendar UI when year/month selections change.

        Args:
            event: Tkinter combobox change event (optional)
            key: Flag for key press events; only refresh on Enter key
        """
        # Skip refresh for non-Enter key presses
        if key and event and event.keysym != 'Return':
            return

        # Validate year input
        year = int(self._cmb_year.get())
        month = int(self._cmb_month.get())
        if year == 0 or year > 9999:
            return

        # Reset selection and rebuild calendar
        self._canvas.place_forget()
        self._date = datetime.datetime(year, month, 1)
        self._build_calendar()

        # Auto-select today's date if viewing current month
        if year == datetime.datetime.now().year and month == datetime.datetime.now().month:
            day = datetime.datetime.now().day
            for _item, day_list in enumerate(self._cal.monthdayscalendar(year, month)):
                if day in day_list:
                    item = 'I00' + str(_item + 2)
                    column = '#' + str(day_list.index(day)+1)
                    _ = self._master.after(100, lambda :self._clicked(item=item, column=column,
                        widget=self._calendar))

    def get_date(self):
        """ Get the currently selected date as a datetime object.

        Returns:
            datetime.date | None: Selected date; None if no selection
        """
        if not self._selection:
            return None
        year, month = self._date.year, self._date.month
        return datetime.date(year, month, int(self._selection[0]))

    def get_datestr(self):
        """ Get the currently selected date as an ISO format string.

        Returns:
            str | None: Date string (YYYY-MM-DD); None if no selection
        """
        if not self._selection:
            return None
        year, month = self._date.year, self._date.month
        return str(datetime.date(year, month, int(self._selection[0])))

    def input_judgment(self, content: str):
        """ Validate input for the year combobox (only digits/empty allowed).

        Args:
            content: Input string from the year combobox

        Returns:
            bool: True if input is valid, False otherwise
        """
        if content.isdigit() or content == "":
            return True
        else:
            return False

    def cancel_select(self):
        """ Clear the current date selection and hide the highlight."""
        self._selection = None
        self._canvas.place_forget()


class CalendarDialog(Dialog):
    """ A modal, borderless pop-up dialog for date selection.

    This class creates a top-level tkinter window containing a CalendarCtrl widget
    and confirm/cancel buttons. It acts as a standalone date picker with modal
    behavior (blocks input to other windows until closed) and custom positioning.

    Attributes:
        _top: Borderless Toplevel window for the dialog UI
        _calendar_ctrl: Embedded CalendarCtrl widget for date selection
        _hh: Stored height of the dialog window
    """
    def __init__(self, point: tuple[int, int] | None = None):
        """ Initialize and render the date selection dialog.

        Creates a borderless, topmost modal dialog with a calendar control and
        action buttons. Positions the window at the given coordinates or center
        of the screen if no position is provided.

        Args:
            point: Optional (x, y) screen coordinates for the dialog window;
                defaults to screen center if None
        """
        super().__init__("", 0, 0)

        # Initialize hidden top-level window
        self._top: tk.Toplevel = tk.Toplevel()
        self._top.withdraw()

        # Main container frame
        frame = ttk.Frame(self._top)

        # Embed calendar control and set layout
        self._calendar_ctrl: CalendarCtrl = CalendarCtrl(frame, self, "")
        self._calendar_ctrl.control.pack(expand = 1, fill = 'both')

        # Bottom action bar with confirm/cancel buttons
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(in_=frame, side='bottom', pady=5)

        # Confirm button (save selection and close)
        ttk.Button(bottom_frame, text="确 定", width=6,
            command=lambda: self._exit(True)).grid(row=0, column=0, sticky='ns', padx=20)
        ttk.Button(bottom_frame, text="取 消", width=6, command=self._exit). \
            grid(row=0, column=1, sticky='ne', padx=20)

        # tk.Frame(frame, bg='#565656').\
        #     place(x=0, y=0, relx=0, rely=0, relwidth=1, relheigh=2/200)
        # tk.Frame(frame, bg='#565656'). \
        #     place(x=0, y=0, relx=0, rely=198/200, relwidth=1, relheigh=2/200)
        # tk.Frame(frame, bg='#565656'). \
        #     place(x=0, y=0, relx=0, rely=0, relwidth=2/200, relheigh=1)
        # tk.Frame(frame, bg='#565656'). \
        #     place(x=0, y=0, relx=198/200, rely=0, relwidth=2/200, relheigh=1)

        # Layout main frame
        frame.pack(expand = 1, fill = 'both')

        # Remove window title bar/borders
        self._top.overrideredirect(True)
        self._top.update_idletasks()

        # Calculate window dimensions and position
        width, height = self._top.winfo_reqwidth(), self._top.winfo_reqheight()
        self._hh: int = height
        # Set position: custom point or screen center
        if point:
            x, y = point[0], point[1]
        else:
            x, y = (self._top.winfo_screenwidth() - width)/2, \
                (self._top.winfo_screenheight() - height)/2

        # Apply window geometry (size + position)
        self._top.geometry(f"{width}x{height}+{x}+{y}")
        # _ = self._master.after(300, self._main_judge)

        # Disable window resizing
        _ = self._top.resizable(width=tk.FALSE, height=tk.FALSE)
        # self._top.transient(self._parent)
        # Bind window close event
        self._top.protocol("WM_DELETE_WINDOW", self.destroy)

        # Configure modal behavior: topmost, grab focus, block input
        self._top.attributes('-topmost', True)
        self._top.grab_set()        # ensure all input goes to our window
        # Show window and wait for user interaction
        self._top.deiconify()
        self._top.focus_set()
        self._top.wait_window()

    def _main_judge(self):
        """ Check if the dialog window retains focus; close if focus is lost.

        Recursively monitors window focus state and closes the dialog if it loses
        focus to another window/element. Includes exception handling for stability.
        """
        try:
            if self._top.focus_displayof() is None \
                or 'toplevel' not in str(self._top.focus_displayof()):
                self._exit()
            else:
                _ = self._top.after(10, self._main_judge)
        except:
            _ = self._top.after(10, self._main_judge)

    def get_datestr(self):
        """ Retrieve the currently selected date as an ISO-format string.

        Returns:
            str | None: Date string (YYYY-MM-DD) if a date is selected,
                None if no selection exists
        """
        return self._calendar_ctrl.get_datestr()

    def _exit(self, confirm: bool = False):
        """ Close the dialog and release modal input control.

        Cancels the date selection if closing via cancel/close; preserves the
        selection if confirmed. Releases window grab and destroys the dialog.

        Args:
            confirm: If True, keep the selected date; if False, clear selection
        """
        if not confirm:
            self._calendar_ctrl.cancel_select()
        # Release modal focus and close window
        self._top.grab_release()
        self._top.destroy()

    @override
    def destroy(self, **kwargs: object):
        """ Override base Dialog destroy method with empty implementation.

        Prevents default destruction logic from interfering with custom
        dialog closing behavior defined in _exit().
        """
        pass


if __name__ == "__main__":
    class CalendarCtrl_test():
        def __init__(self):

            self.root: tk.Tk = tk.Tk()

            # 设置tk窗口在屏幕中心显示
            sw = self.root.winfo_screenwidth()    # 得到屏幕宽度
            sh = self.root.winfo_screenheight()    # 得到屏幕高度
            ww = 200    # 设置窗口 宽度
            wh = 60    # 设置窗口 高度

            x = (sw - ww) / 2
            y = (sh - wh) / 2
            self.root.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

            self.Frame_row1: tk.Frame = tk.Frame(self.root)
            self.Frame_row1.pack()

            self.var_test: tk.StringVar = tk.StringVar()
            self.Entry_test: tk.Entry = tk.Entry(self.Frame_row1, width=10,
                textvariable=self.var_test, font="宋体, 12",
                                         justify='center', )
            self.Entry_test.grid(row=0, column=0, padx=5, pady=5)

            self.Button_test: tk.Button = tk.Button(self.Frame_row1, width=2,
                text='*', font="宋体, 12",
                justify='center',
                command=lambda: self.get_date(self.Entry_test.winfo_rootx(),
                                    self.Entry_test.winfo_rooty() + 20))
            self.Button_test.grid(row=0, column=1, padx=5, pady=5)

            self.root.mainloop()

        def get_date(self, x: int, y: int):    # x, y位Entry的坐标位置
            # 接收弹窗的数据
            res = self.ask_date(x, y)
            if res is None:
                return
            self.var_test.set(res)

        def ask_date(self, x: int, y: int):
            calendar = CalendarDialog((x, y))
            return calendar.get_datestr()

    app = CalendarCtrl_test()
