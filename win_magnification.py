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
class Offset(PropertiesObserver):
    x: int
    y: int

    def __post_init__(self):
        super().__init__()

    @property
    def same(self) -> int:
        return self.x

    @same.setter
    def same(self, value: int):
        self.pair = value, value

    @property
    def pair(self):
        return self.x, self.y

    @pair.setter
    def pair(self, value: tuple[int, int]):
        with self.batch():
            self.x, self.y = value


@dataclass
class FullscreenTransform(PropertiesObserver):
    scale: float
    offset: Offset

    def __post_init__(self):
        super().__init__()

    def reset_scale(self):
        self.scale = DEFAULT_FULLSCREEN_TRANSFORM[0]

    def reset_offset(self):
        self.offset = Offset(*DEFAULT_FULLSCREEN_TRANSFORM[1])

    @property
    def raw(self) -> FullscreenTransformRaw:
        return self.scale, self.offset.pair

    @raw.setter
    def raw(self, value: FullscreenTransformRaw):
        with self.batch():
            self.scale, self.offset.pair = value

    @classmethod
    def from_raw(cls, value: FullscreenTransformRaw):
        return cls(value[0], Offset(*value[1]))


@dataclass
class InputTransform(PropertiesObserver):
    enabled: bool
    source: Rectangle
    destination: Rectangle

    def __post_init__(self):
        super().__init__()

    @property
    def raw(self) -> InputTransformRaw:
        return self.enabled, self.source, self.destination

    @raw.setter
    def raw(self, value: InputTransformRaw):
        with self.batch():
            self.enabled, self.source, self.destination = value


@dataclass
class WindowTransform(PropertiesObserver):
    x: float
    y: float
    __x_pos = pos_for_matrix(TransformationMatrixSize, 0, 0)
    __y_pos = pos_for_matrix(TransformationMatrixSize, 1, 1)
    _matrix = None

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
    def matrix(self) -> TransformationMatrix:
        self._matrix[self.__x_pos] = self.x
        self._matrix[self.__y_pos] = self.y
        # noinspection PyTypeChecker
        return tuple(self._matrix)  # type: ignore

    @matrix.setter
    def matrix(self, value: TransformationMatrix):
        self._matrix = list(value)
        self.pair = value[self.__x_pos], value[self.__y_pos]

    @classmethod
    def from_matrix(cls, value: TransformationMatrix):
        result = cls(0, 0)
        result.matrix = value
        return result


class FullscreenController:
    @property
    def transform(self):
        result = FullscreenTransform.from_raw(
            get_fullscreen_transform()
        )
        result.subscribe(lambda: set_fullscreen_transform(*result.raw))
        return result

    @property
    def default_transform(self):
        return FullscreenTransform.from_raw(DEFAULT_FULLSCREEN_TRANSFORM)

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

    @property
    def input_transform(self):
        result = InputTransform(*get_input_transform())
        result.subscribe(lambda: set_input_transform(*result.raw))
        return result

    @staticmethod
    def set_cursor_visibility(show_cursor: bool):
        set_cursor_visibility(show_cursor)


class CustomWindowController:
    def __init__(self):
        self.hwnd = 0

    @property
    def scale(self):
        result = WindowTransform.from_matrix(
            get_transform(self.hwnd)
        )
        result.subscribe(lambda: set_transform_advanced(
            self.hwnd,
            result.matrix
        ))
        return result

    @property
    def default_scale(self):
        return WindowTransform.from_matrix(DEFAULT_TRANSFORM)

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
