import ctypes
import functools
import weakref
from queue import Queue
import threading
from abc import ABCMeta, abstractmethod, ABC
from typing import Callable, Optional

import timer  # type: ignore
import win32api  # type: ignore
import win32con  # type: ignore
import win32gui  # type: ignore

import win_magnification as mag
from constants import Rectangle


def make_partial_screen(hwnd, rectangle: Rectangle):
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        win32con.WS_EX_TOPMOST |
        win32con.WS_EX_LAYERED
    )
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_STYLE,
        win32con.WS_SIZEBOX |
        win32con.WS_SYSMENU |
        win32con.WS_CLIPCHILDREN |
        win32con.WS_CAPTION |
        win32con.WS_MAXIMIZEBOX
    )
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        *rectangle,
        win32con.SWP_SHOWWINDOW |
        win32con.SWP_NOZORDER |
        win32con.SWP_NOACTIVATE
    )


def get_fullscreen_size() -> Rectangle:
    # Calculate the span of the display area.
    max_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    max_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    return 0, 0, max_x, max_y
    # Alternative
    # return win32gui.GetClientRect(win32gui.GetDesktopWindow())


# noinspection SpellCheckingInspection
def make_fullscreen(hwnd, rectangle: Rectangle):
    # The window must be styled as layered for proper rendering.
    # It is styled as transparent so that it does not capture mouse clicks.
    # For draw on top of TaskManager/System menus we need to use win10 zBand
    # Most relevant is ZBID_UIACCESS, read blog below to know more
    # https://blog.adeltax.com/window-z-order-in-windows-10/
    win32gui.SetWindowLong(
        hwnd, win32con.GWL_EXSTYLE,
        win32con.WS_EX_TOPMOST |
        win32con.WS_EX_LAYERED |
        win32con.WS_EX_TOOLWINDOW |
        win32con.WS_EX_TRANSPARENT
    )

    win32gui.SetWindowLong(
        hwnd, win32con.GWL_STYLE,
        win32con.WS_CHILD
    )

    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        *rectangle,
        win32con.SWP_SHOWWINDOW |
        win32con.SWP_NOZORDER |
        win32con.SWP_NOACTIVATE
    )


WinEventHandler = Callable[['AbstractWindow'], None]


class AbstractWindow(metaclass=ABCMeta):
    window_class: int = 0
    window_class_name = "Py_MyAbstractWindowClass"
    windows: weakref.WeakValueDictionary[int, 'AbstractWindow'] = weakref.WeakValueDictionary()
    events: dict[int, Callable[[int, int, int, int], None]] = dict()
    # noinspection SpellCheckingInspection
    hinst = win32api.GetModuleHandle()

    def __init__(self):
        self._thread: Optional[int] = None
        self._window_started_event = threading.Event()
        self._command = Queue()
        self._result = Queue()
        self.hwnd: Optional[int] = None
        self.position = (0, 0)
        self.size = (400, 400)
        # noinspection PyTypeChecker
        self.rectangle: Rectangle = (*self.position, *self.size)
        self._fullscreen_rectangle: Rectangle = (0, 0, 200, 200)
        self._fullscreen_mode = False

    @property
    def rectangle(self) -> Rectangle:
        # noinspection PyTypeChecker
        return *self.position, *self.size  # type: ignore

    @rectangle.setter
    def rectangle(self, value):
        self.position = value[:2]
        self.size = value[2:]

    @abstractmethod
    def _create_window(self):
        pass

    def create_window(self):
        if self.is_alive:
            raise RuntimeError("Magnification window is already running")
        self._thread = win32api.GetCurrentThreadId()
        # Note: Without Dpi setting magnifier image quality is low and creepy
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        self._register_window_class()
        self._create_window()
        self.__class__.windows[self.hwnd] = self
        self._fullscreen_rectangle = get_fullscreen_size()
        if self._fullscreen_mode:
            make_fullscreen(self.hwnd, self._fullscreen_rectangle)
        else:
            make_partial_screen(self.hwnd, self.rectangle)
        self._window_started_event.set()

    @classmethod
    def _register_window_class(cls):
        if cls.window_class:
            return
        cls.window_class = win32gui.GetClassLong(win32gui.FindWindow(cls.window_class_name, None), win32con.GCW_ATOM)
        if cls.window_class:
            return
        window_class = win32gui.WNDCLASS()
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        # noinspection SpellCheckingInspection
        window_class.lpfnWndProc = cls.events
        window_class.hInstance = cls.hinst
        window_class.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
        # noinspection SpellCheckingInspection
        window_class.lpszClassName = cls.window_class_name
        cls.window_class = win32gui.RegisterClass(window_class)

    @property
    def is_alive(self):
        return self._window_started_event.is_set()

    def _close(self):
        # Implements close logic
        if not self.is_alive:
            raise RuntimeError("Window not started yet")
        self._window_started_event.clear()
        del self.__class__.windows[self.hwnd]
        self.hwnd = None
        win32api.PostQuitMessage(0)

    def _run_event(self, event: int):
        win32gui.PostMessage(
            self.hwnd, event, 0, 0
        )

    @property
    def current_rectangle(self):
        if self._fullscreen_mode:
            return self._fullscreen_rectangle
        return self.rectangle


def win_event(message: int):
    def _wrapper(fun: WinEventHandler):
        # noinspection PyUnusedLocal
        def on_event(hwnd: int, message_: int, wparam: int, lparam: int):
            self = AbstractWindow.windows.get(hwnd, None)
            if self:
                return fun(self)

        @functools.wraps(fun)
        def run_event(self: AbstractWindow = None):
            if self:
                win32gui.PostMessage(
                    self.hwnd, message, 0, 0,
                )

        AbstractWindow.events[message] = on_event
        return run_event
    return _wrapper


class BasicWindow(AbstractWindow, ABC):
    @win_event(win32con.WM_CLOSE)
    def close(self):
        win32gui.DestroyWindow(self.hwnd)

    @win_event(win32con.WM_DESTROY)
    def _on_destroy(self):
        self._close()

    def wait_window_start(self, timeout=None):
        self._window_started_event.wait(timeout)

    @property
    def fullscreen_mode(self):
        return self._fullscreen_mode

    @fullscreen_mode.setter
    def fullscreen_mode(self, value):
        self._fullscreen_mode = value
        if self.is_alive:
            if value:
                self._fullscreen_rectangle = get_fullscreen_size()
                self._execute(make_fullscreen, self.hwnd, self._fullscreen_rectangle)
            else:
                self._execute(make_partial_screen, self.hwnd, self.rectangle)

    def _execute(self, command: Callable, *args, **kwargs):
        if self._thread == win32api.GetCurrentThreadId():
            return command(*args, **kwargs)
        else:
            element = (command, args, kwargs)
            self._command.put(element)
            self._on_command_get()
            return self._result.get()

    @win_event(win32con.WM_USER)
    def _on_command_get(self):
        command, args, kwargs = self._command.get()
        result = command(*args, **kwargs)
        self._result.put(result)


class MagnifierWindow(BasicWindow):
    window_class_name = "Py_CustomMagnifierWindowHost"

    def __init__(self):
        super().__init__()
        self.magnifier_hwnd = None

    def _create_window(self):
        self._create_host_window()
        self._create_magnifier_window()
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        self._on_move()

    def _create_magnifier_window(self):
        # noinspection SpellCheckingInspection
        self.magnifier_hwnd = win32gui.CreateWindow(
            mag.WC_MAGNIFIER,
            "Custom Magnifier Window",
            win32con.WS_CHILD |
            # mag.MS_SHOWMAGNIFIEDCURSOR |
            win32con.WS_VISIBLE,
            *win32gui.GetClientRect(self.hwnd),
            self.hwnd, 0,
            self.hinst,
            None
        )

    def _create_host_window(self):
        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_TOPMOST |
            win32con.WS_EX_LAYERED |
            win32con.WS_EX_TRANSPARENT,
            self.window_class_name,
            "Custom Magnifier Host Window",
            win32con.WS_CLIPCHILDREN |
            win32con.WS_CAPTION,
            0, 0, 0, 0,
            0, 0,
            self.hinst,
            None
        )
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)

    def _close(self):
        super()._close()
        self.magnifier_hwnd = None

    @win_event(win32con.WM_SIZE)
    def _on_resize(self):
        if not self.fullscreen_mode:
            self.size = win32gui.GetClientRect(self.hwnd)[2:]
        win32gui.SetWindowPos(self.magnifier_hwnd, 0, *win32gui.GetClientRect(self.hwnd), 0)

    @win_event(win32con.WM_MOVE)
    def _on_move(self):
        if self.fullscreen_mode:
            return
        self.position = list(win32gui.GetWindowRect(self.hwnd)[:2])
        self.position[0] += 2*win32api.GetSystemMetrics(win32con.SM_CXFRAME)
        self.position[1] += 2*win32api.GetSystemMetrics(win32con.SM_CYFRAME)
        self.position[1] += win32api.GetSystemMetrics(win32con.SM_CYCAPTION)

    @win_event(win32con.WM_PAINT)
    def _draw(self):
        if not self.is_alive:
            return

        mag.set_window_source(self.magnifier_hwnd, self.current_rectangle)

        if self.hwnd is None:
            return
        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOACTIVATE |
            win32con.SWP_NOMOVE |
            win32con.SWP_NOSIZE
        )


def run_magnifier_window(window: MagnifierWindow) -> threading.Thread:
    @mag.require_components()
    def inner():
        win32gui.InitCommonControls()
        window.create_window()
        win32gui.PumpMessages()

    thread = threading.Thread(target=inner)
    thread.start()
    window.wait_window_start()
    return thread
