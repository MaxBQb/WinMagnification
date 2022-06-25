"""
Additional tools used primary in wrapper

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
import contextlib
import threading
from ctypes import *
from functools import wraps
from typing import Callable, ParamSpec, Optional

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


def get_empty_matrix(size: int):
    return [[0] * size for _ in range(size)]


def to_py_matrix(c_matrix: Array[Array]):
    return list(map(list, c_matrix))


def to_c_matrix(matrix: list[list], content_type=c_float):
    return (content_type * len(matrix) * len(matrix))(*[
        (content_type * len(row))(*row) for row in matrix
    ])


def get_alternative(value, default):
    return default if value is None else value


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
