"""
| Additional tools used primary in wrapper
| Author: MaxBQb
"""
from __future__ import annotations

import contextlib
import ctypes
import ctypes.wintypes
import functools
import threading
import typing

from win_magnification.types import Rectangle

P = [typing.Any]
if typing.TYPE_CHECKING:
    P = typing.ParamSpec("P")  # type: ignore

_current_thread = None


def handle_win_last_error(function_result: bool):
    if not function_result:
        raise ctypes.WinError()


def raise_win_errors(win_function: typing.Callable[P, bool]) -> typing.Callable[P, None]:  # type: ignore
    @functools.wraps(win_function)
    def wrapper(*args: 'P.args', **kwargs: 'P.kwargs') -> None:  # type: ignore
        handle_win_last_error(win_function(*args, **kwargs))
    return wrapper


@contextlib.contextmanager
def require_single_thread():
    thread_holder.require_thread_match()
    yield


def to_py_array(c_matrix: ctypes.Array, content_type=float):
    return tuple(map(content_type, c_matrix))


def to_c_array(matrix: tuple, content_type=ctypes.c_float):
    return (content_type * len(matrix))(*matrix)


def to_py_rectangle(rectangle: ctypes.wintypes.RECT) -> Rectangle:
    # noinspection PyTypeChecker
    return (  # type: ignore
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
