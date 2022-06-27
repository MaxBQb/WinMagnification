"""
Main module

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
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


def set_transform_simple(hwnd: int, scale: typing.Union[float, tuple[float, float]]):
    scale_x, scale_y = scale if isinstance(scale, tuple) else (scale, scale)
    set_transform_advanced(hwnd, get_transform_matrix(scale_x, scale_y))


initialize = safe_initialize
finalize = safe_finalize
set_transform_advanced = set_transform
set_transform = set_transform_simple  # type: ignore
reset_fullscreen_color_effect = partial(set_fullscreen_color_effect, effect=DEFAULT_COLOR_EFFECT)
reset_fullscreen_transform = partial(set_fullscreen_transform, *DEFAULT_FULLSCREEN_TRANSFORM)
reset_transform = partial(set_transform_advanced, matrix=DEFAULT_TRANSFORM)
reset_color_effect = partial(set_color_effect, effect=DEFAULT_COLOR_EFFECT)


# Object-Oriented Interface
class WinMagnificationAPI:
    def __init__(self):
        initialize()
        self.__disposed = False
        self.__fullscreen = FullscreenController()
        self.__window = CustomWindowController()

    @property
    def fullscreen(self):
        return self.__fullscreen

    @property
    def window(self):
        return self.__window

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


@dataclass
class WindowTransform:
    x: float
    y: float
    __x_pos = pos_for_matrix(TransformationMatrixSize, 0, 0)
    __y_pos = pos_for_matrix(TransformationMatrixSize, 1, 1)

    def __post_init__(self):
        self._raw = list(get_transform_matrix(self.x, self.y))

    @property
    def raw(self):
        self._raw[self.__x_pos] = self.x
        self._raw[self.__y_pos] = self.y
        return tuple(self._raw)

    @property
    def pair(self):
        return self.x, self.y

    @classmethod
    def fromRaw(cls, value: TransformationMatrix):
        result = cls(value[cls.__x_pos], value[cls.__y_pos])
        cls._raw = list(value)
        return result

    @classmethod
    def same(cls, value: float):
        return cls(value, value)

    @classmethod
    def convert(cls, value: typing.Union[
        int, float, tuple[
            typing.Union[int, float],
            typing.Union[int, float]
        ], TransformationMatrix
    ]):
        if isinstance(value, (int, float)):
            value = value, value
        if isinstance(value, tuple) and len(value) == 2:
            return cls(float(value[0]), float(value[1]))
        # noinspection PyTypeChecker
        return cls.fromRaw(value)  # type: ignore


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

    def transformFrom(self, value: typing.Union[
        FullscreenTransform, FullscreenTransformRaw
    ]):
        if not isinstance(value, FullscreenTransform):
            value = FullscreenTransform.fromRaw(value)  # type: ignore
        self.transform = value

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


class CustomWindowController:
    def __init__(self):
        self.hwnd = 0

    @property
    def scale(self):
        """
        Note: properties changes don't reflect on actual window scale,
        use scale setter to apply changes
        """
        return WindowTransform.fromRaw(
            get_transform(self.hwnd)
        )

    @scale.setter
    def scale(self, value: WindowTransform):
        set_transform_advanced(self.hwnd, value.raw)

    def scaleFrom(self, value: typing.Union[
        int, float, tuple[
            typing.Union[int, float],
            typing.Union[int, float]
        ], TransformationMatrix, WindowTransform
    ]):
        if not isinstance(value, WindowTransform):
            value = WindowTransform.convert(value)
        self.scale = value

    @property
    def default_scale(self):
        return WindowTransform.fromRaw(DEFAULT_TRANSFORM)

    def reset_scale(self):
        reset_transform(self.hwnd)

    @property
    def color_effect(self):
        return get_color_effect(self.hwnd)

    @color_effect.setter
    def color_effect(self, value: ColorMatrix):
        set_color_effect(self.hwnd, value)

    @property
    def default_color_effect(self):
        return DEFAULT_COLOR_EFFECT

    def reset_color_effect(self):
        reset_color_effect(self.hwnd)

    @property
    def source(self):
        return get_source(self.hwnd)

    @source.setter
    def source(self, value: Rectangle):
        set_source(self.hwnd, value)

    @property
    def filters(self):
        _, filters = get_filters(self.hwnd)
        return filters

    @filters.setter
    def filters(self, value: tuple):
        set_filters(self.hwnd, *value)
