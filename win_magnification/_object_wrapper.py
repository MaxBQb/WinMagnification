from __future__ import annotations

import dataclasses

from win_magnification import _object_utils as _utils
from win_magnification._functional_wrapper import *  # type: ignore
from win_magnification._wrapper import *
from win_magnification.const import *
from win_magnification.types import *


class Offset(_utils.CompositeWrappedField[typing.Tuple[int, int]]):
    def _define_observable(self):
        self.x: int = 0
        self.y: int = 0

    @property
    def same(self) -> int:
        return self.x

    @same.setter
    def same(self, value: int):
        self.raw = value, value

    @property
    def _local_raw(self):
        return self.x, self.y

    @_local_raw.setter
    def _local_raw(self, value):
        self.x, self.y = value


class Rectangle(_utils.CompositeWrappedField[RectangleRaw]):
    def _define_observable(self):
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0

    @property
    def _local_raw(self):
        return self.left, self.top, self.right, self.bottom

    @_local_raw.setter
    def _local_raw(self, value):
        self.left, self.top, self.right, self.bottom = value

    @property
    def start(self):
        return self.left, self.top

    @start.setter
    def start(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.left, self.top = value

    @property
    def start_same(self):
        return self.left

    @start_same.setter
    def start_same(self, value: int):
        self.start = value, value

    @property
    def end(self):
        return self.right, self.bottom

    @end.setter
    def end(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.right, self.bottom = value

    @property
    def end_same(self):
        return self.right

    @end_same.setter
    def end_same(self, value: int):
        self.end = value, value

    @property
    def same(self) -> int:
        return self.left

    @same.setter
    def same(self, value: int):
        self.raw = value, value, value, value


class FullscreenTransform(_utils.CompositeWrappedField[FullscreenTransformRaw]):
    def _define_observable(self):
        self.scale: float = 0.0
        self.offset = Offset(default=DEFAULT_FULLSCREEN_TRANSFORM[1])

    @property
    def _local_raw(self):
        return self.scale, self.offset.raw

    @_local_raw.setter
    def _local_raw(self, value):
        self.scale, self.offset.raw = value


class InputTransform(_utils.CompositeWrappedField[InputTransformRaw]):
    def _define_observable(self):
        self.enabled: bool = False
        self.source = Rectangle(default=ZERO_RECT)
        self.destination = Rectangle(default=ZERO_RECT)

    @property
    def _local_raw(self):
        return self.enabled, self.source.raw, self.destination.raw

    @_local_raw.setter
    def _local_raw(self, value):
        self.enabled, self.source.raw, self.destination.raw = value


class WindowTransform(_utils.CompositeWrappedField[TransformationMatrix]):
    __x_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 0, 0)
    __y_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 1, 1)

    def _define_observable(self):
        self.x: float = 0.0
        self.y: float = 0.0

    def __post_init__(self):
        super().__init__()
        self._matrix = list(tools.get_transform_matrix(self.x, self.y))

    @property
    def pair(self) -> typing.Tuple[float, float]:
        return self.x, self.y

    @pair.setter
    def pair(self, value: typing.Tuple[float, float]):
        with self.batch():
            self.x, self.y = value

    @property
    def same(self) -> float:
        return self.x

    @same.setter
    def same(self, value: float):
        self.pair = value, value

    @property
    def _local_raw(self):
        return tools.get_transform_matrix(self.x, self.y)

    @_local_raw.setter
    def _local_raw(self, value):
        self.pair = value[self.__x_pos], value[self.__y_pos]


class FullscreenController:
    def __init__(self):
        self._cursor_visible = True
        self._transform = FullscreenTransform(
            get_fullscreen_transform,
            lambda value: set_fullscreen_transform(*value),
            DEFAULT_FULLSCREEN_TRANSFORM
        )
        self._color_effect = _utils.CompositeField(
            get_fullscreen_color_effect,
            set_fullscreen_color_effect,
            DEFAULT_COLOR_EFFECT,
        )
        self._input_transform_transform = InputTransform(
            get_input_transform,
            lambda value: set_input_transform(*value),
            DEFAULT_INPUT_TRANSFORM
        )

    @property
    def transform(self):
        return self._transform

    @property
    def color_effect(self):
        return self._color_effect

    @property
    def input_transform(self):
        return self._input_transform_transform

    @property
    def cursor_visible(self):
        """Doesn't reflect actual value, shows last used value instead"""
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, value: bool):
        self._cursor_visible = value
        set_cursor_visibility(value)


class CustomWindowController:
    def __init__(self):
        self.hwnd = 0
        self._scale = WindowTransform(
            lambda: get_transform(self.hwnd),
            lambda result: set_transform_advanced(
                self.hwnd,
                result
            ),
            DEFAULT_TRANSFORM,
        )
        self._color_effect = _utils.CompositeField(
            lambda: get_color_effect(self.hwnd),
            lambda value: set_color_effect(self.hwnd, value),
            DEFAULT_COLOR_EFFECT,
        )
        self._source = Rectangle(
            lambda: get_source(self.hwnd),
            lambda value: set_source(self.hwnd, value),
            DEFAULT_SOURCE,
        )
        self._filters = _utils.CompositeField(
            lambda: get_filters(self.hwnd)[1],
            lambda value: set_filters(self.hwnd, *value),
            DEFAULT_FILTERS_LIST,
        )

    @property
    def scale(self):
        return self._scale

    @property
    def color_effect(self):
        return self._color_effect

    @property
    def source(self):
        return self._source

    @property
    def filters(self):
        return self._filters


class WinMagnificationAPI:
    """
    Object-Oriented wrapper for Magnification API

    .. automethod:: __del__
    """

    def __init__(self):
        self.__disposed = False
        self.__fullscreen = FullscreenController()
        self.__window = CustomWindowController()
        initialize()

    @property
    def fullscreen(self):
        """Gives access to fullscreen functions of Magnification API"""
        return self.__fullscreen

    @property
    def window(self):
        """Gives access to window (custom magnifier controller) functions of Magnification API"""
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
        """
        Calls :meth:`.WinMagnificationAPI.dispose` on object distraction
        """
        self.dispose()
