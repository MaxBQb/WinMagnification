"""
| Internal module
| Only use of :class:`WinMagnificationAPI` allowed
"""
from __future__ import annotations

import typing
from win_magnification import _object_utils as _utils
from win_magnification import _wrapper
from win_magnification import _functional_wrapper as _wrapper2
from win_magnification import const
from win_magnification import types


class Vector2(_utils.CompositeWrappedField[typing.Tuple[float, float]]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[typing.Tuple[float, float]]] = None,
        default: typing.Optional[typing.Tuple[float, float]] = None
    ):
        self.x: float = 0.0
        self.y: float = 0.0
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


class Rectangle(_utils.CompositeWrappedField[types.RectangleRaw]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.RectangleRaw]] = None,
        default: typing.Optional[types.RectangleRaw] = None
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


class FullscreenTransform(_utils.CompositeWrappedField[types.FullscreenTransformRaw]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.FullscreenTransformRaw]] = None,
        default: typing.Optional[types.FullscreenTransformRaw] = None
    ):
        self.scale: float = 0.0
        self.offset = Offset(default=const.DEFAULT_FULLSCREEN_TRANSFORM[1])
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return self.scale, self.offset.raw

    @_raw.setter
    def _raw(self, value):
        self.scale, self.offset.raw = value


class InputTransform(_utils.CompositeWrappedField[types.InputTransformRaw]):
    def __init__(
            self,
            datasource: typing.Optional[_utils.DataSource[types.InputTransformRaw]] = None,
            default: typing.Optional[types.InputTransformRaw] = None
    ):
        self.enabled: bool = False
        self.source = Rectangle(default=const.ZERO_RECT)
        self.destination = Rectangle(default=const.ZERO_RECT)
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return self.enabled, self.source.raw, self.destination.raw

    @_raw.setter
    def _raw(self, value):
        self.enabled, self.source.raw, self.destination.raw = value


class WindowTransform(_utils.CompositeWrappedField[types.TransformationMatrix]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.TransformationMatrix]] = None,
        default: typing.Optional[types.TransformationMatrix] = None
    ):
        self.scale = Vector2(default=const.DEFAULT_TRANSFORM_PAIR[0])
        self.offset = Vector2(default=const.DEFAULT_TRANSFORM_PAIR[1])
        super().__init__(datasource, default)

    @property
    def _raw(self):
        return const.tools.get_transform_matrix(*self.scale.raw, *self.offset.raw)

    @_raw.setter
    def _raw(self, value):
        self.pair = _wrapper2.to_simple_transform(value)

    @property
    def pair(self) -> types.SimpleTransformation:
        with self.batch():
            return self.scale.raw, self.offset.raw

    @pair.setter
    def pair(self, value: types.SimpleTransformation):
        with self.batch():
            self.scale.raw, self.offset.raw = value


class FullscreenController:
    def __init__(self):
        self._cursor_visible = True
        self._transform = FullscreenTransform(
            _utils.DataSource.dynamic(
                _wrapper.get_fullscreen_transform,
                lambda value: _wrapper.set_fullscreen_transform(*value),
            ),
            const.DEFAULT_FULLSCREEN_TRANSFORM
        )
        self._color_effect = _utils.CompositeField(
            _utils.DataSource.dynamic(
                _wrapper.get_fullscreen_color_effect,
                _wrapper.set_fullscreen_color_effect,
            ),
            const.DEFAULT_COLOR_EFFECT,
        )
        self._input_transform_transform = InputTransform(
            _utils.DataSource.dynamic(
                _wrapper.get_input_transform,
                lambda value: _wrapper.set_input_transform(*value),
            ),
            const.DEFAULT_INPUT_TRANSFORM
        )

    @property
    def transform(self) -> FullscreenTransform:
        return self._transform

    @property
    def color_effect(self):
        return self._color_effect

    @property
    def input_transform(self) -> InputTransform:
        return self._input_transform_transform

    @property
    def cursor_visible(self) -> bool:
        """
        | Cursor show/hidden state
        | Doesn't reflect actual value, shows last used value instead
        """
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, value: bool):
        self._cursor_visible = value
        _wrapper.set_cursor_visibility(value)


class CustomWindowController:
    def __init__(self):
        self.hwnd = 0
        self._transform = WindowTransform(
            _utils.DataSource.dynamic(
                lambda: _wrapper2.get_transform_advanced(self.hwnd),
                lambda result: _wrapper2.set_transform_advanced(
                    self.hwnd,
                    result
                ),
            ),
            const.DEFAULT_TRANSFORM,
        )
        self._color_effect = _utils.CompositeField(
            _utils.DataSource.dynamic(
                lambda: _wrapper.get_color_effect(self.hwnd),
                lambda value: _wrapper.set_color_effect(self.hwnd, value),
            ),
            const.DEFAULT_COLOR_EFFECT,
        )
        self._source = Rectangle(
            _utils.DataSource.dynamic(
                lambda: _wrapper.get_source(self.hwnd),
                lambda value: _wrapper.set_source(self.hwnd, value),
            ),
            const.DEFAULT_SOURCE,
        )
        self._filters = _utils.CompositeField(
            _utils.DataSource.dynamic(
                lambda: _wrapper.get_filters(self.hwnd)[1],
                lambda value: _wrapper.set_filters(self.hwnd, *value),
            ),
            const.DEFAULT_FILTERS_LIST,
        )

    @property
    def transform(self) -> WindowTransform:
        return self._transform

    @property
    def color_effect(self):
        return self._color_effect

    @property
    def source(self) -> Rectangle:
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
        _wrapper2.initialize()

    @property
    def fullscreen(self) -> FullscreenController:
        """Gives access to fullscreen functions of Magnification API"""
        return self.__fullscreen

    @property
    def window(self) -> CustomWindowController:
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
        _wrapper2.finalize()

    def __del__(self):
        """
        Calls :meth:`.WinMagnificationAPI.dispose` on object distraction
        """
        self.dispose()
