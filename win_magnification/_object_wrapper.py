from __future__ import annotations

from win_magnification import _object_utils as _utils
from win_magnification._functional_wrapper import *  # type: ignore
from win_magnification._wrapper import *
from win_magnification.const import *
from win_magnification.types import *


class Vector2(_utils.CompositeWrappedField[typing.Tuple[float, float]]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[typing.Tuple[float, float]]] = None,
        default: typing.Optional[typing.Tuple[float, float]] = None
    ):
        self.x: float = 0
        self.y: float = 0
        super().__init__(datasource, default)

    @property
    def same(self) -> float:
        return self.x

    @same.setter
    def same(self, value: float):
        with self.batch():
            self._raw = value, value

    @property
    def _raw(self):
        return self.x, self.y

    @_raw.setter
    def _raw(self, value):
        self.x, self.y = value


class Offset(_utils.CompositeWrappedField[typing.Tuple[int, int]]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[typing.Tuple[int, int]]] = None,
        default: typing.Optional[typing.Tuple[int, int]] = None
    ):
        self.x: int = 0
        self.y: int = 0
        super().__init__(datasource, default)

    @property
    def same(self) -> int:
        return self.x

    @same.setter
    def same(self, value: int):
        with self.batch():
            self._raw = value, value

    @property
    def _raw(self):
        return self.x, self.y

    @_raw.setter
    def _raw(self, value):
        self.x, self.y = value


class Rectangle(_utils.CompositeWrappedField[RectangleRaw]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[RectangleRaw]] = None,
        default: typing.Optional[RectangleRaw] = None
    ):
        self.left: int = 0
        self.top: int = 0
        self.right: int = 0
        self.bottom: int = 0
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return self.left, self.top, self.right, self.bottom

    @_raw.setter
    def _raw(self, value):
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
        with self.batch():
            self._raw = value, value, value, value


class FullscreenTransform(_utils.CompositeWrappedField[FullscreenTransformRaw]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[FullscreenTransformRaw]] = None,
        default: typing.Optional[FullscreenTransformRaw] = None
    ):
        self.scale: float = 0.0
        self.offset = Offset(default=DEFAULT_FULLSCREEN_TRANSFORM[1])
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return self.scale, self.offset.raw

    @_raw.setter
    def _raw(self, value):
        self.scale, self.offset.raw = value


class InputTransform(_utils.CompositeWrappedField[InputTransformRaw]):
    def __init__(
            self,
            datasource: typing.Optional[_utils.DataSource[InputTransformRaw]] = None,
            default: typing.Optional[InputTransformRaw] = None
    ):
        self.enabled: bool = False
        self.source = Rectangle(default=ZERO_RECT)
        self.destination = Rectangle(default=ZERO_RECT)
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return self.enabled, self.source.raw, self.destination.raw

    @_raw.setter
    def _raw(self, value):
        self.enabled, self.source.raw, self.destination.raw = value


class WindowTransform(_utils.CompositeWrappedField[TransformationMatrix]):
    __x_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 0, 0)
    __y_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 1, 1)
    __x_offset_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 0, 2)
    __y_offset_pos = tools.pos_for_matrix(TRANSFORMATION_MATRIX_SIZE, 1, 2)

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[TransformationMatrix]] = None,
        default: typing.Optional[TransformationMatrix] = None
    ):
        self.scale = Vector2(default=(
            DEFAULT_TRANSFORM[self.__x_pos],
            DEFAULT_TRANSFORM[self.__y_pos],
        ))
        self.offset = Vector2(default=(
            DEFAULT_TRANSFORM[self.__x_offset_pos],
            DEFAULT_TRANSFORM[self.__y_offset_pos],
        ))
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return tools.get_transform_matrix(*self.scale.raw, *self.offset.raw)

    @_raw.setter
    def _raw(self, value):
        self.scale.raw = value[self.__x_pos], value[self.__y_pos]
        self.offset.raw = -value[self.__x_offset_pos], -value[self.__y_offset_pos]


class FullscreenController:
    def __init__(self):
        self._cursor_visible = True
        self._transform = FullscreenTransform(
            _utils.DataSource.dynamic(
                get_fullscreen_transform,
                lambda value: set_fullscreen_transform(*value),
            ),
            DEFAULT_FULLSCREEN_TRANSFORM
        )
        self._color_effect = _utils.CompositeField(
            _utils.DataSource.dynamic(
                get_fullscreen_color_effect,
                set_fullscreen_color_effect,
            ),
            DEFAULT_COLOR_EFFECT,
        )
        self._input_transform_transform = InputTransform(
            _utils.DataSource.dynamic(
                get_input_transform,
                lambda value: set_input_transform(*value),
            ),
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
        self._transform = WindowTransform(
            _utils.DataSource.dynamic(
                lambda: get_transform(self.hwnd),
                lambda result: set_transform_advanced(
                    self.hwnd,
                    result
                ),
            ),
            DEFAULT_TRANSFORM,
        )
        self._color_effect = _utils.CompositeField(
            _utils.DataSource.dynamic(
                lambda: get_color_effect(self.hwnd),
                lambda value: set_color_effect(self.hwnd, value),
            ),
            DEFAULT_COLOR_EFFECT,
        )
        self._source = Rectangle(
            _utils.DataSource.dynamic(
                lambda: get_source(self.hwnd),
                lambda value: set_source(self.hwnd, value),
            ),
            DEFAULT_SOURCE,
        )
        self._filters = _utils.CompositeField(
            _utils.DataSource.dynamic(
                lambda: get_filters(self.hwnd)[1],
                lambda value: set_filters(self.hwnd, *value),
            ),
            DEFAULT_FILTERS_LIST,
        )

    @property
    def transform(self):
        return self._transform

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
