import dataclasses

from . import _object_utils as _utils
from ._wrapper import *
from ._functional_wrapper import *  # type: ignore
from .const import *
from . import tools
from .types import *


@dataclasses.dataclass
class Offset(_utils.ObservableWrapper[typing.Tuple[int, int]]):
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
    def raw(self) -> typing.Tuple[int, int]:
        return self.x, self.y

    @raw.setter
    def raw(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.x, self.y = value

    @classmethod
    def wrap(cls, value: typing.Tuple[int, int]) -> 'Offset':
        return cls(*value)


@dataclasses.dataclass
class Rectangle(_utils.ObservableWrapper[RectangleRaw]):
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


@dataclasses.dataclass
class FullscreenTransform(_utils.ObservableWrapper[FullscreenTransformRaw]):
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


@dataclasses.dataclass
class InputTransform(_utils.ObservableWrapper[InputTransformRaw]):
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


@dataclasses.dataclass
class WindowTransform(_utils.ObservableWrapper[TransformationMatrix]):
    x: float
    y: float
    __x_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 0, 0)
    __y_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 1, 1)
    _matrix: typing.List[float] = None  # type: ignore

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
        self._transform = _utils.CompositeWrappedField[FullscreenTransformRaw, FullscreenTransform](
            FullscreenTransform,
            get_fullscreen_transform,
            lambda value: set_fullscreen_transform(*value),
            DEFAULT_FULLSCREEN_TRANSFORM,
        )
        self._color_effect = _utils.CompositeField(
            get_fullscreen_color_effect,
            set_fullscreen_color_effect,
            DEFAULT_COLOR_EFFECT,
        )
        self._input_transform_transform = _utils.CompositeWrappedField[InputTransformRaw, InputTransform](
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
        self._scale = _utils.CompositeWrappedField[TransformationMatrix, WindowTransform](
            WindowTransform,
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
        self._source = _utils.CompositeWrappedField(
            Rectangle,
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
