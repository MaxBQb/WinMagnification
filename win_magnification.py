"""
Main module

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
import contextlib
from dataclasses import dataclass
from functools import partial

import _utils
import _wrapper
from _wrapper import *
import typing


@_utils.require_single_thread()
def safe_initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    _utils.thread_holder.lock.acquire()
    _wrapper.initialize()
    _utils.thread_holder.hold_current_thread()


@_utils.require_single_thread()
def safe_finalize() -> None:
    """
    Destroys the magnifier run-time objects.
    """
    if not _utils.thread_holder.has_content:
        raise RuntimeError("Magnification API has not been initialized yet!")
    _wrapper.finalize()
    _utils.thread_holder.release_thread()


def set_window_transform_simple(hwnd: int, scale: typing.Union[float, tuple[float, float]]):
    scale_x, scale_y = scale if isinstance(scale, tuple) else (scale, scale)
    matrix = [
        [scale_x, 0, 0],
        [0, scale_y, 0],
        [0, 0, 1],
    ]
    set_window_transform_advanced(hwnd, matrix)


initialize = safe_initialize
finalize = safe_finalize
set_window_transform_advanced = set_window_transform
set_window_transform = set_window_transform_simple  # type: ignore
reset_fullscreen_color_effect = partial(set_fullscreen_color_effect, effect=DEFAULT_COLOR_EFFECT)
reset_fullscreen_transform = partial(set_fullscreen_transform, *DEFAULT_FULLSCREEN_TRANSFORM)


@contextlib.contextmanager
def require_components():
    try:
        initialize()
        yield
    finally:
        finalize()


# Object-Oriented Interface
class WinMagnificationAPI:
    def __init__(self):
        initialize()
        self.__disposed = False
        self.__fullscreen = FullscreenController()

    @property
    def fullscreen(self):
        return self.__fullscreen

    def dispose(self):
        """
        You may use this method for cleanup,
        but python's GC can do that for you
        """
        if self.__disposed:
            return
        self.__disposed = True
        finalize()

    def __del__(self):
        self.dispose()


@dataclass
class Offset:
    x: int
    y: int

    @classmethod
    def same(cls, value: int):
        return cls(value, value)

    @property
    def raw(self):
        return self.x, self.y


@dataclass
class FullscreenTransform:
    """
    Fullscreen transformation representation
    Note: to change properties use `with` block:

    with api.fullscreen.transform as transform:
        transform.offset.x += 1
    """

    scale: float
    offset: Offset

    @property
    def default_scale(self):
        return DEFAULT_FULLSCREEN_TRANSFORM[0]

    @property
    def default_offset(self):
        return Offset(DEFAULT_FULLSCREEN_TRANSFORM[1][0], DEFAULT_FULLSCREEN_TRANSFORM[1][1])

    def reset_scale(self):
        self.scale = self.default_scale

    def reset_offset(self):
        self.offset = self.default_offset

    @property
    def raw(self) -> FullscreenTransformRaw:
        return self.scale, self.offset.raw

    @classmethod
    def fromRaw(cls, value: FullscreenTransformRaw):
        return cls(value[0], Offset(*value[1]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            set_fullscreen_transform(*self.raw)


class FullscreenController:
    @property
    def transform(self):
        """
        Note: to change properties use `with` block:

        with api.fullscreen.transform as transform:
            transform.offset.x += 1
        """
        return FullscreenTransform.fromRaw(
            get_fullscreen_transform()
        )

    @transform.setter
    def transform(self, value: FullscreenTransform):
        set_fullscreen_transform(*value.raw)

    @property
    def default_transform(self):
        return FullscreenTransform.fromRaw(DEFAULT_FULLSCREEN_TRANSFORM)

    @staticmethod
    def reset_transform():
        reset_fullscreen_transform()

    @property
    def color_effect(self):
        return get_fullscreen_color_effect()

    @color_effect.setter
    def color_effect(self, value: ColorMatrix):
        set_fullscreen_color_effect(value)

    @property
    def default_color_effect(self):
        return DEFAULT_COLOR_EFFECT

    @staticmethod
    def reset_color_effect():
        reset_fullscreen_color_effect()
