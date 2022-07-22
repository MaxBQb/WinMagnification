"""
| Internal module
| Only use of :class:`WinMagnificationAPI` allowed
"""
from __future__ import annotations

import typing

from win_magnification import _functional_wrapper as _wrapper2
from win_magnification import _object_utils as _utils
from win_magnification import _wrapper
from win_magnification import const
from win_magnification import types


class Vector2(_utils.WrappedField[typing.Tuple[float, float]]):
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[typing.Tuple[float, float]]] = None,
    ):
        self.x: float = 0.0
        """
        | Horizontal component
        | |accessors: get set delete|
        """
        self.y: float = 0.0
        """
        | Vertical component
        | |accessors: get set delete|
        """
        super().__init__(datasource)

    @property
    def same(self) -> float:
        """
        | Get/set same value from/to (x, y)
        | |accessors: get set|
        """
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


class TransformScale(Vector2):
    """
    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.DEFAULT_TRANSFORM_PAIR[0]


class TransformOffset(Vector2):
    """
    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.DEFAULT_TRANSFORM_PAIR[1]


class FullscreenOffsetWrapper(_utils.WrappedField[typing.Tuple[int, int]]):
    """
    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.DEFAULT_FULLSCREEN_TRANSFORM[1]

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[typing.Tuple[int, int]]] = None,
    ):
        self.x: int = 0
        """
        | Horizontal |right| offset component
        | Starts from |upleft| upper-left corner
        | |accessors: get set delete|
        """
        self.y: int = 0
        """
        | Vertical |down| offset component
        | Starts from |upleft| upper-left corner
        | |accessors: get set delete|
        """
        super().__init__(datasource)

    @property
    def same(self) -> int:
        """
        | Get/set same value from/to (x, y)
        | |accessors: get set|
        """
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


class RectangleWrapper(_utils.WrappedField['types.Rectangle']):
    """
    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.ZERO_RECT

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.Rectangle]] = None,
    ):
        self.left: int = 0
        """
        | |left| x-component of start point |upleft|
        | |accessors: get set delete|
        """
        self.top: int = 0
        """
        | |up| y-component of start point |upleft|
        | |accessors: get set delete|
        """
        self.right: int = 0
        """
        | |right| x-component of end point |downright|
        | |accessors: get set delete|
        """
        self.bottom: int = 0
        """
        | |down| y-component of end point |downright|
        | |accessors: get set delete|
        """
        super().__init__(datasource)

    @property
    def _raw(self):
        return self.left, self.top, self.right, self.bottom

    @_raw.setter
    def _raw(self, value):
        self.left, self.top, self.right, self.bottom = value

    @property
    def start(self) -> typing.Tuple[int, int]:
        """
        | Get/set value from/to (left, top)
        | |accessors: get set|
        """
        return self.left, self.top

    @start.setter
    def start(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.left, self.top = value

    @property
    def start_same(self) -> int:
        """
        | Get/set same value from/to (left, top)
        | |accessors: get set|
        """
        return self.left

    @start_same.setter
    def start_same(self, value: int):
        self.start = value, value

    @property
    def end(self) -> typing.Tuple[int, int]:
        """
        | Get/set value from/to (right, bottom)
        | |accessors: get set|
        """
        return self.right, self.bottom

    @end.setter
    def end(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.right, self.bottom = value

    @property
    def end_same(self) -> int:
        """
        | Get/set same value from/to (right, bottom)
        | |accessors: get set|
        """
        return self.right

    @end_same.setter
    def end_same(self, value: int):
        self.end = value, value

    @property
    def same(self) -> int:
        """
        | Get/set same value from/to (left, top, right, bottom)
        | |accessors: get set|
        """
        return self.left

    @same.setter
    def same(self, value: int):
        with self.batch():
            self._raw = value, value, value, value


class SourceRectangleWrapper(RectangleWrapper):
    """
    .. include:: ../shared/wrapper/head.rst
    """
    _DEFAULT_RAW = const.DEFAULT_SOURCE


class ColorMatrixWrapper(_utils.WrappedField['types.ColorMatrix']):
    """.. include:: ../shared/wrapper/common.rst"""
    _DEFAULT_RAW = const.DEFAULT_COLOR_EFFECT


class FiltersListWrapper(_utils.WrappedField[tuple]):
    """.. include:: ../shared/wrapper/common.rst"""
    _DEFAULT_RAW = const.DEFAULT_FILTERS_LIST


class FullscreenTransformWrapper(_utils.WrappedField['types.FullscreenTransform']):
    """
    .. include:: ../shared/wrapper/head.rst
    """
    _DEFAULT_RAW = const.DEFAULT_FULLSCREEN_TRANSFORM

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.FullscreenTransform]] = None,
    ):
        self.scale: float = 0.0
        """
        | Fullscreen magnification factor
        | |accessors: get set delete| 
        """
        self.offset: FullscreenOffsetWrapper = FullscreenOffsetWrapper()
        """
        | Fullscreen magnification target offset
        | Relative to the |upleft| upper-left corner of the primary monitor
        | |accessors: get set delete|
        """
        super().__init__(datasource)

    @property
    def _raw(self):
        return self.scale, self.offset.raw

    @_raw.setter
    def _raw(self, value):
        self.scale, self.offset.raw = value


class InputTransformWrapper(_utils.WrappedField['types.InputTransform']):
    """
    .. include:: ../shared/wrapper/head.rst
    """
    _DEFAULT_RAW = const.DEFAULT_INPUT_TRANSFORM

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.InputTransform]] = None,
    ):
        self.enabled: bool = False
        """
        | Is input translation enabled
        | |accessors: get set delete|
        """
        self.source: RectangleWrapper = RectangleWrapper()
        """
        | The source rectangle, in unmagnified screen coordinates,
          that defines the area of the screen that is magnified
        | |accessors: get set delete|
        """
        self.destination: RectangleWrapper = RectangleWrapper()
        """
        | The destination rectangle, in screen coordinates,
          that defines the area of the screen where the magnified
          screen content is displayed.
        | |accessors: get set delete|
        """
        super().__init__(datasource)

    @property
    def _raw(self):
        return self.enabled, self.source.raw, self.destination.raw

    @_raw.setter
    def _raw(self, value):
        self.enabled, self.source.raw, self.destination.raw = value


class TransformationMatrixWrapper(_utils.WrappedField['types.TransformationMatrix']):
    """.. include:: ../shared/wrapper/head.rst"""
    _DEFAULT_RAW = const.DEFAULT_TRANSFORM

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.TransformationMatrix]] = None,
    ):
        self.scale: TransformScale = TransformScale()
        """
        | Magnifier window scale
        | |accessors: get set delete| 
        """
        self.offset: TransformOffset = TransformOffset()
        """
        | Magnifier window target offset
        | Relative to the |upleft| upper-left corner of window
        | |accessors: get set delete|
        """
        super().__init__(datasource)

    @property
    def _raw(self):
        return const.tools.get_transform_matrix(*self.scale.raw, *self.offset.raw)

    @_raw.setter
    def _raw(self, value):
        self.pair = _wrapper2.to_simple_transform(value)

    @property
    def pair(self) -> types.SimpleTransform:
        """
        | Tuple of (offset, scale), both of which are tuples of (x, y)
        | |accessors: get set|
        """
        with self.batch():
            return self.scale.raw, self.offset.raw

    @pair.setter
    def pair(self, value: types.SimpleTransform):
        with self.batch():
            self.scale.raw, self.offset.raw = value


class FullscreenController:
    def __init__(self):
        self._cursor_visible = True
        self._transform = FullscreenTransformWrapper(
            _utils.DataSource.dynamic(
                _wrapper.get_fullscreen_transform,
                lambda value: _wrapper.set_fullscreen_transform(*value),
            ),
        )
        self._color_effect = ColorMatrixWrapper(
            _utils.DataSource.dynamic(
                _wrapper.get_fullscreen_color_effect,
                _wrapper.set_fullscreen_color_effect,
            )
        )
        self._input_transform_transform = InputTransformWrapper(
            _utils.DataSource.dynamic(
                _wrapper.get_input_transform,
                lambda value: _wrapper.set_input_transform(*value),
            )
        )

    @property
    def transform(self) -> FullscreenTransformWrapper:
        """
        | Scale/offset fullscreen magnifier transformations
        | |accessors: get|
        """
        return self._transform

    @property
    def color_effect(self) -> ColorMatrixWrapper:
        """
        | Color transformations
        | |accessors: get|
        """
        return self._color_effect

    @property
    def input_transform(self) -> InputTransformWrapper:
        """
        | Input transformation for pen and touch input
        | |accessors: get|
        """
        return self._input_transform_transform

    @property
    def cursor_visible(self) -> bool:
        """
        | Cursor shown/hidden state
        .. note::
           Doesn't reflect actual value, shows last used value instead
        | |accessors: get set|
        """
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, value: bool):
        self._cursor_visible = value
        _wrapper.set_cursor_visibility(value)


class CustomWindowController:
    def __init__(self):
        self.hwnd: int = 0
        """
        | Magnification window handle
        | |accessors: get set|
        """
        self._transform = TransformationMatrixWrapper(
            _utils.DataSource.dynamic(
                lambda: _wrapper2.get_transform_advanced(self.hwnd),
                lambda result: _wrapper2.set_transform_advanced(
                    self.hwnd,
                    result
                )
            )
        )
        self._color_effect = ColorMatrixWrapper(
            _utils.DataSource.dynamic(
                lambda: _wrapper.get_color_effect(self.hwnd),
                lambda value: _wrapper.set_color_effect(self.hwnd, value),
            )
        )
        self._source = SourceRectangleWrapper(
            _utils.DataSource.dynamic(
                lambda: _wrapper.get_source(self.hwnd),
                lambda value: _wrapper.set_source(self.hwnd, value),
            )
        )
        self._filters = FiltersListWrapper(
            _utils.DataSource.dynamic(
                lambda: _wrapper.get_filters(self.hwnd)[1],
                lambda value: _wrapper.set_filters(self.hwnd, *value),
            )
        )

    @property
    def transform(self) -> TransformationMatrixWrapper:
        """
        | Scale/offset magnifier transformations
        | |accessors: get|
        """
        return self._transform

    @property
    def color_effect(self) -> ColorMatrixWrapper:
        """
        | Color transformations
        | |accessors: get|
        """
        return self._color_effect

    @property
    def source(self) -> SourceRectangleWrapper:
        """
        | Source area, to get origin pixels from
        | |accessors: get|
        """
        return self._source

    @property
    def filters(self) -> FiltersListWrapper:
        """
        | Window filtration list
        | |accessors: get|
        """
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
        """
        | Gives access to fullscreen functions of Magnification API
        | |accessors: get|
        """
        return self.__fullscreen

    @property
    def window(self) -> CustomWindowController:
        """
        | Gives access to window (custom magnifier controller)
          functions of Magnification API
        | |accessors: get|
        """
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
