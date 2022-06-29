"""
Main module

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
from dataclasses import dataclass, field
from functools import partial

import _utils
import _wrapper
from _wrapper import *
import typing

from utils import PropertiesObserver


@_utils.require_single_thread()  # type: ignore
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    _utils.thread_holder.lock.acquire()
    _wrapper.initialize()
    _utils.thread_holder.hold_current_thread()


@_utils.require_single_thread()  # type: ignore
def finalize() -> None:
    """
    Destroys the magnifier run-time objects.
    """
    if not _utils.thread_holder.has_content:
        raise RuntimeError("Magnification API has not been initialized yet!")
    _wrapper.finalize()
    _utils.thread_holder.release_thread()


def set_transform_advanced(hwnd: int, matrix: TransformationMatrix) -> None:
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param matrix: A 3x3 matrix of the magnification transformation
    """
    _wrapper.set_transform(hwnd, matrix)


def set_transform(hwnd: int, scale: typing.Union[float, tuple[float, float]]):  # type: ignore
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param scale: Magnification factor, or it's separate x, y components
    """
    scale_x, scale_y = scale if isinstance(scale, tuple) else (scale, scale)
    set_transform_advanced(hwnd, get_transform_matrix(scale_x, scale_y))


reset_fullscreen_color_effect = partial(set_fullscreen_color_effect, effect=DEFAULT_COLOR_EFFECT)
reset_fullscreen_transform = partial(set_fullscreen_transform, *DEFAULT_FULLSCREEN_TRANSFORM)
reset_transform = partial(set_transform_advanced, matrix=DEFAULT_TRANSFORM)
reset_color_effect = partial(set_color_effect, effect=DEFAULT_COLOR_EFFECT)


# Object-Oriented Interface
class WinMagnificationAPI:
    def __init__(self):
        self.__disposed = False
        self.__fullscreen = FullscreenController()
        self.__window = CustomWindowController()
        initialize()

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
class Offset(ObservableWrapper[tuple[int, int]]):
    x: int
    y: int

    def __post_init__(self):
        super().__init__()

    @property
    def same(self) -> int:
        return self.x

    @same.setter
    def same(self, value: int):
        self.raw = value, value

    @property
    def raw(self) -> tuple[int, int]:
        return self.x, self.y

    @raw.setter
    def raw(self, value: tuple[int, int]):
        with self.batch():
            self.x, self.y = value

    @classmethod
    def wrap(cls, value: tuple[int, int]) -> 'Offset':
        return cls(*value)


@dataclass
class Rectangle(ObservableWrapper[RectangleRaw]):
    left: int
    top: int
    right: int
    bottom: int

    def __post_init__(self):
        super().__init__()

    @property
    def start(self):
        return self.left, self.top

    @start.setter
    def start(self, value: tuple[int, int]):
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
    def end(self, value: tuple[int, int]):
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

    @property
    def raw(self) -> RectangleRaw:
        return self.left, self.top, self.right, self.bottom

    @raw.setter
    def raw(self, value: RectangleRaw):
        with self.batch():
            self.left, self.top, self.right, self.bottom = value

    @classmethod
    def wrap(cls, value: RectangleRaw) -> 'Rectangle':
        return cls(*value)


@dataclass
class FullscreenTransform(ObservableWrapper[FullscreenTransformRaw]):
    scale: float
    offset: Offset

    def __post_init__(self):
        super().__init__()

    @property
    def raw(self) -> FullscreenTransformRaw:
        return self.scale, self.offset.raw

    @classmethod
    def wrap(cls, value: FullscreenTransformRaw) -> 'FullscreenTransform':
        return cls(value[0], Offset.wrap(value[1]))


@dataclass
class InputTransform(ObservableWrapper[InputTransformRaw]):
    enabled: bool
    source: Rectangle
    destination: Rectangle

    def __post_init__(self):
        super().__init__()

    @property
    def raw(self) -> InputTransformRaw:
        return self.enabled, self.source.raw, self.destination.raw

    @classmethod
    def wrap(cls, value: InputTransformRaw) -> 'InputTransform':
        return cls(value[0], Rectangle.wrap(value[1]), Rectangle.wrap(value[2]))


@dataclass
class WindowTransform(ObservableWrapper[TransformationMatrix]):
    x: float
    y: float
    __x_pos = pos_for_matrix(TransformationMatrixSize, 0, 0)
    __y_pos = pos_for_matrix(TransformationMatrixSize, 1, 1)
    _matrix: list[float] = None  # type: ignore

    def __post_init__(self):
        super().__init__()
        self._matrix = list(get_transform_matrix(self.x, self.y))

    @property
    def pair(self) -> tuple[float, float]:
        return self.x, self.y

    @pair.setter
    def pair(self, value: tuple[float, float]):
        with self.batch():
            self.x, self.y = value

    @property
    def same(self) -> float:
        return self.x

    @same.setter
    def same(self, value: float):
        self.pair = value, value

    @property
    def raw(self) -> TransformationMatrix:
        self._matrix[self.__x_pos] = self.x
        self._matrix[self.__y_pos] = self.y
        # noinspection PyTypeChecker
        return tuple(self._matrix)  # type: ignore

    @raw.setter
    def raw(self, value: TransformationMatrix):
        self._matrix = list(value)
        self.pair = value[self.__x_pos], value[self.__y_pos]

    @classmethod
    def wrap(cls, value: TransformationMatrix) -> 'WindowTransform':
        result = cls(0, 0)
        result.raw = value
        return result


class FullscreenController:
    def __init__(self):
        self._cursor_visible = True
        self._transform = CompositeWrappedField[FullscreenTransformRaw, FullscreenTransform](
            FullscreenTransform,
            get_fullscreen_transform,
            lambda value: set_fullscreen_transform(*value),
            DEFAULT_FULLSCREEN_TRANSFORM,
        )
        self._color_effect = CompositeField(
            get_fullscreen_color_effect,
            set_fullscreen_color_effect,
            DEFAULT_COLOR_EFFECT,
        )
        self._input_transform_transform = CompositeWrappedField[InputTransformRaw, InputTransform](
            InputTransform,
            get_input_transform,
            lambda value: set_input_transform(*value),
            DEFAULT_INPUT_TRANSFORM,
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
        self._scale = CompositeWrappedField[TransformationMatrix, WindowTransform](
            WindowTransform,
            lambda: get_transform(self.hwnd),
            lambda result: set_transform_advanced(
                self.hwnd,
                result
            ),
            DEFAULT_TRANSFORM,
        )
        self._color_effect = CompositeField(
            lambda: get_color_effect(self.hwnd),
            lambda value: set_color_effect(self.hwnd, value),
            DEFAULT_COLOR_EFFECT,
        )
        self._source = CompositeWrappedField(
            Rectangle,
            lambda: get_source(self.hwnd),
            lambda value: set_source(self.hwnd, value),
            DEFAULT_SOURCE,
        )
        self._filters = CompositeField(
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
