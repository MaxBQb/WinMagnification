"""
Main module

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
import contextlib
from functools import partial

import _utils
import _wrapper
from _wrapper import *


@_utils.require_single_thread()
def safe_initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    if _utils.thread_holder.has_content:
        raise RuntimeError("Magnification API already initialized!")
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


initialize = safe_initialize
finalize = safe_finalize
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
        self.__fullscreen_transform = _FullscreenTransform()

    @property
    def fullscreen_color_effect(self):
        return get_fullscreen_color_effect()

    @fullscreen_color_effect.setter
    def fullscreen_color_effect(self, value: ColorMatrix):
        set_fullscreen_color_effect(value)

    @fullscreen_color_effect.deleter
    def fullscreen_color_effect(self):
        reset_fullscreen_color_effect()

    @property
    def fullscreen_transform(self):
        return self.__fullscreen_transform

    def __del__(self):
        finalize()


class _FullscreenTransform:
    def __init__(self):
        self.__offset = _FullscreenTransform._Offset(self)

    def _change(self,
                scale: float = None,
                x: int = None,
                y: int = None):
        _scale, (_x, _y) = self.raw
        self.raw = (
            _utils.get_alternative(scale, _scale),
            (_utils.get_alternative(x, _x),
             _utils.get_alternative(y, _y))
        )

    @property
    def scale(self) -> float:
        scale, _ = self.raw
        return scale

    @scale.setter
    def scale(self, value: float):
        self._change(scale=value)

    @scale.deleter
    def scale(self):
        scale, _ = DEFAULT_FULLSCREEN_TRANSFORM
        self._change(scale=scale)

    @property
    def offset(self) -> '_FullscreenTransform._Offset':
        return self.__offset

    @property
    def raw(self) -> tuple[float, tuple[int, int]]:
        return get_fullscreen_transform()

    @raw.setter
    def raw(self, value: tuple[float, tuple[int, int]]):
        set_fullscreen_transform(*value)

    @raw.deleter
    def raw(self):
        reset_fullscreen_transform()

    class _Offset:
        def __init__(self, outer: '_FullscreenTransform'):
            self.__outer = outer

        @property
        def x(self) -> int:
            x, _ = self.raw
            return x

        @x.setter
        def x(self, value: int):
            self.__outer._change(x=value)

        @x.deleter
        def x(self):
            _, (x, _) = DEFAULT_FULLSCREEN_TRANSFORM
            self.__outer._change(x=x)

        @property
        def y(self) -> int:
            _, y = self.raw
            return y

        @y.setter
        def y(self, value: int):
            self.__outer._change(y=value)

        @y.deleter
        def y(self):
            _, (_, y) = DEFAULT_FULLSCREEN_TRANSFORM
            self.__outer._change(y=y)

        @property
        def raw(self) -> tuple[int, int]:
            _, offset = self.__outer.raw
            return offset

        @raw.setter
        def raw(self, value: tuple[int, int]):
            x, y = value
            self.__outer._change(x=x, y=y)

        @raw.deleter
        def raw(self):
            _, (x, y) = DEFAULT_FULLSCREEN_TRANSFORM
            self.__outer._change(x=x, y=y)
