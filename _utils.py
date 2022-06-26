"""
Additional tools used primary in wrapper

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
import contextlib
import threading
from ctypes import *
from ctypes.wintypes import RECT
from functools import wraps
from typing import Callable, ParamSpec

from constants import Rectangle

P = ParamSpec("P")

_current_thread = None


def handle_win_last_error(function_result: bool):
    if not function_result:
        raise WinError()


def raise_win_errors(win_function: Callable[P, bool]) -> Callable[P, None]:
    @wraps(win_function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        handle_win_last_error(win_function(*args, **kwargs))
    return wrapper


@contextlib.contextmanager
def require_single_thread():
    thread_holder.require_thread_match()
    yield


def to_py_array(c_matrix: Array, content_type=float):
    return tuple(map(content_type, c_matrix))


def to_c_array(matrix: tuple, content_type=c_float):
    return (content_type * len(matrix))(*matrix)


def to_py_rectangle(rectangle: RECT) -> Rectangle:
    # noinspection PyTypeChecker
    return (
        rectangle.left,
        rectangle.top,
        rectangle.right,
        rectangle.bottom
    )


class ThreadHolder:
    def __init__(self):
        self.__thread_identifier = None
        self.lock = threading.Lock()
    
    @property    
    def has_content(self):
        return self.__thread_identifier is not None
    
    @property
    def _current_thread(self):
        return threading.current_thread().ident
    
    @property
    def is_current_thread_match(self):
        return self.__thread_identifier == self._current_thread

    def require_thread_match(self):
        if not self.is_current_thread_match and self.has_content:
            raise RuntimeError("Magnification API must be accessed from a single thread!")

    def hold_current_thread(self):
        self.require_thread_match()
        self.__thread_identifier = self._current_thread

    def release_thread(self):
        self.require_thread_match()
        self.__thread_identifier = None
        self.lock.release()


thread_holder = ThreadHolder()
