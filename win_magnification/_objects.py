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
from win_magnification import tools
from win_magnification import types

LM = typing.TypeVar('LM', bound=typing.Tuple)


class MatrixWrapper(tools.Matrix, _utils.WrappedField[LM], typing.Generic[LM]):
    """
    Observable matrix wrapper
    """
    _SIZE = 4

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[LM]] = None,
    ):
        tools.Matrix.__init__(self)
        self._resize(self._SIZE)
        _utils.WrappedField.__init__(self, datasource)
        self._inner_observables.add('_value')
        self._subscribe_initial()

    @property
    def _raw(self) -> LM:
        return self._value

    @_raw.setter
    def _raw(self, value: LM):
        self._value = value


class Vector2(_utils.WrappedField[typing.Tuple[float, float]]):
    """
    Pair of horizontal and vertical components
    """
    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[typing.Tuple[float, float]]] = None,
    ):
        self.x: float = 0.0
        """
        | Horizontal component
        | |Accessors: Get Set Delete|
        """
        self.y: float = 0.0
        """
        | Vertical component
        | |Accessors: Get Set Delete|
        """
        super().__init__(datasource)

    @property
    def same(self) -> typing.Optional[float]:
        """
        | Get/set same value from/to (x, y)
        | Or None if values differs
        | |Accessors: Get Set|
        """
        with self.batch():
            return _utils.ensure_same(
                self.x,
                self.y,
            )

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
    Magnifier window scale (horizontal, vertical)

    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.DEFAULT_TRANSFORM_PAIR[0]


class TransformOffset(Vector2):
    """
    Magnifier window target offset (x |down|, y |right|)
    from |up-left| upper-left corner of magnifier screen

    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.DEFAULT_TRANSFORM_PAIR[1]


class FullscreenOffsetWrapper(_utils.WrappedField[typing.Tuple[int, int]]):
    """
    | Fullscreen magnification target offset
    | Relative to the |up-left| upper-left corner of the primary monitor

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
        | Starts from |up-left| upper-left corner
        | |Accessors: Get Set Delete|
        """
        self.y: int = 0
        """
        | Vertical |down| offset component
        | Starts from |up-left| upper-left corner
        | |Accessors: Get Set Delete|
        """
        super().__init__(datasource)

    @property
    def same(self) -> typing.Optional[int]:
        """
        | Get/set same value from/to (x, y)
        | Or None if values differs
        | |Accessors: Get Set|
        """
        with self.batch():
            return _utils.ensure_same(
                self.x,
                self.y,
            )

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
    Pair of two points (start |up-left|, end |down-right|)

    .. include:: ../shared/wrapper/component.rst
    """
    _DEFAULT_RAW = const.ZERO_RECT

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.Rectangle]] = None,
    ):
        self.left: int = 0
        """
        | |left| x-component of start point |up-left|
        | |Accessors: Get Set Delete|
        """
        self.top: int = 0
        """
        | |up| y-component of start point |up-left|
        | |Accessors: Get Set Delete|
        """
        self.right: int = 0
        """
        | |right| x-component of end point |down-right|
        | |Accessors: Get Set Delete|
        """
        self.bottom: int = 0
        """
        | |down| y-component of end point |down-right|
        | |Accessors: Get Set Delete|
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
        | |Accessors: Get Set|
        """
        return self.left, self.top

    @start.setter
    def start(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.left, self.top = value

    @property
    def start_same(self) -> typing.Optional[int]:
        """
        | Get/set same value from/to (left, top)
        | Or None if values differs
        | |Accessors: Get Set|
        """
        with self.batch():
            return _utils.ensure_same(
                self.left,
                self.top,
            )

    @start_same.setter
    def start_same(self, value: int):
        self.start = value, value

    @property
    def end(self) -> typing.Tuple[int, int]:
        """
        | Get/set value from/to (right, bottom)
        | |Accessors: Get Set|
        """
        return self.right, self.bottom

    @end.setter
    def end(self, value: typing.Tuple[int, int]):
        with self.batch():
            self.right, self.bottom = value

    @property
    def end_same(self) -> typing.Optional[int]:
        """
        | Get/set same value from/to (right, bottom)
        | Or None if values differs
        | |Accessors: Get Set|
        """
        with self.batch():
            return _utils.ensure_same(
                self.right,
                self.bottom,
            )

    @end_same.setter
    def end_same(self, value: int):
        self.end = value, value

    @property
    def same(self) -> typing.Optional[int]:
        """
        | Get/set same value from/to (left, top, right, bottom)
        | Or None if values differs
        | |Accessors: Get Set|
        """
        with self.batch():
            return _utils.ensure_same(
                self.left,
                self.top,
                self.right,
                self.bottom,
            )

    @same.setter
    def same(self, value: int):
        with self.batch():
            self._raw = value, value, value, value


class SourceRectangleWrapper(RectangleWrapper):
    """
    Source area, to get origin pixels from

    .. include:: ../shared/wrapper/head.rst
    """
    _DEFAULT_RAW = const.DEFAULT_SOURCE


class ColorMatrixWrapper(MatrixWrapper['types.ColorMatrix']):
    """
    Use to apply color transformations

    .. include:: ../shared/wrapper/common.rst
    """
    _SIZE = const.COLOR_MATRIX_SIZE
    _DEFAULT_RAW = const.DEFAULT_COLOR_EFFECT

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[LM]] = None,
    ):
        super().__init__(datasource)
        self._transition: typing.Optional[tools.Transition] = None
        self._transition_power = 0.0

    @property
    def transition_power(self) -> float:
        """
        | Applies color effect transition
        | Use :meth:`make_transition` or :meth:`from_transition` to setup
          and apply transition from **start** to **end** with scale of **value**
          then you can change **value** with this method:
        | **value** = 0 |=> **start**
        | **value** = 1 |=> **end**
        | 0 <= **value** <= 1 |=> **start** moved towards **end**
        | **value** > 1 |=> **start** moved towards **end** out of **end** bound
        | **value** < 0 |=> **end** moved towards **start** out of **start** bound
        | |Accessors: Get Set|
        """
        return self._transition_power

    @transition_power.setter
    def transition_power(self, value: typing.Union[float, int]):
        value = float(value)
        self._transition_power = value
        if self._transition:
            self.linear = self._transition(value)

    @property
    def transition(self) -> typing.Optional[tools.Transition]:
        """
        | Current :data:`.Transition` or None if not set yet
        | |Accessors: Get|
        """
        return self._transition

    def make_transition(
        self,
        end: tools.Matrix.Any,
        start: typing.Optional[tools.Matrix.Any] = None,
        initial_power: typing.Optional[typing.Union[float, int]] = None,
    ):
        """
        | Setup and apply transition from **start** to **end**
          with scale of **initial_power**:
        | **initial_power** = 0 |=> **start**
        | **initial_power** = 1 |=> **end**
        | 0 <= **initial_power** <= 1 |=> **start** moved towards **end**
        | **initial_power** > 1 |=> **start** moved towards **end** out of **end** bound
        | **initial_power** < 0 |=> **end** moved towards **start** out of **start** bound

        :param start: :abbr:`Initial state (transit from)` (default: current color effect)
        :param end: :abbr:`Final state (transit to)`
        :param initial_power: Float scale of transition
            normally stays between :abbr:`0 (start)` and :abbr:`1 (end)` to get transition effect
            (default: last value used or 0)
        :raises TypeError: If params conversion fails
        """
        if start is None:
            start = self
        else:
            start = self.from_any(start)
            if start is None:
                raise TypeError('Unable to convert `start` value to matrix')
        end = self.from_any(end)
        if end is None:
            raise TypeError('Unable to convert `end` value to matrix')

        self.from_transition(tools.get_transition(
            start.linear,
            end.linear,
        ), initial_power)

    def from_transition(
        self,
        transition: tools.Transition,
        initial_power: typing.Optional[typing.Union[float, int]] = None,
    ):
        """
        Setup and apply transition from existing one

        :param transition: one of :mod:`.effects` or copy of :attr:`last used one <transition>`
        :param initial_power: Float start scale of transition
            normally stays between :abbr:`0 (start)` and :abbr:`1 (end)` to get transition effect
            (default: last value used or 0)
        """
        if initial_power is None:
            initial_power = self.transition_power
        self._transition = transition
        self.transition_power = initial_power


class FiltersListWrapper(_utils.WrappedField[tuple]):
    """
    Window filtration list

    .. include:: ../shared/wrapper/common.rst
    """
    _DEFAULT_RAW = const.DEFAULT_FILTERS_LIST


class FullscreenTransformWrapper(_utils.WrappedField['types.FullscreenTransform']):
    """
    Scale/offset fullscreen magnifier transformations

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
        | |Accessors: Get Set Delete| 
        """
        self.offset: FullscreenOffsetWrapper = FullscreenOffsetWrapper()
        """
        | Fullscreen magnification target offset
        | Relative to the |up-left| upper-left corner of the primary monitor
        | |Accessors: Get Set Delete|
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
    Input transformation for pen and touch input

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
        | |Accessors: Get Set Delete|
        """
        self.source: RectangleWrapper = RectangleWrapper()
        """
        | The source rectangle, in unmagnified screen coordinates,
          that defines the area of the screen that is magnified
        | |Accessors: Get Set Delete|
        """
        self.destination: RectangleWrapper = RectangleWrapper()
        """
        | The destination rectangle, in screen coordinates,
          that defines the area of the screen where the magnified
          screen content is displayed.
        | |Accessors: Get Set Delete|
        """
        super().__init__(datasource)

    @property
    def _raw(self):
        return self.enabled, self.source.raw, self.destination.raw

    @_raw.setter
    def _raw(self, value):
        self.enabled, self.source.raw, self.destination.raw = value


class TransformationMatrixWrapper(_utils.WrappedField['types.TransformationMatrix']):
    """
    Scale/offset magnifier transformations

    .. include:: ../shared/wrapper/head.rst
    """
    _DEFAULT_RAW = const.DEFAULT_TRANSFORM

    def __init__(
        self,
        datasource: typing.Optional[_utils.DataSource[types.TransformationMatrix]] = None,
    ):
        self.scale: TransformScale = TransformScale()
        """
        | Magnifier window scale
        | |Accessors: Get Set Delete| 
        """
        self.offset: TransformOffset = TransformOffset()
        """
        | Magnifier window target offset
        | Relative to the |up-left| upper-left corner of window
        | |Accessors: Get Set Delete|
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
        | |Accessors: Get Set|
        """
        with self.batch():
            return self.scale.raw, self.offset.raw

    @pair.setter
    def pair(self, value: types.SimpleTransform):
        with self.batch():
            self.scale.raw, self.offset.raw = value


class FullscreenController:
    """
    Gives access to fullscreen functions of Magnification API
    """
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
        | |Accessors: Get|
        """
        return self._transform

    @property
    def color_effect(self) -> ColorMatrixWrapper:
        """
        | Color transformations
        | |Accessors: Get|
        """
        return self._color_effect

    @property
    def input_transform(self) -> InputTransformWrapper:
        """
        | Input transformation for pen and touch input
        | |Accessors: Get|
        """
        return self._input_transform_transform

    @property
    def cursor_visible(self) -> bool:
        """
        | Cursor shown/hidden state

        .. note::
           Doesn't reflect actual value, shows last used value instead

        | |Accessors: Get Set|
        """
        return self._cursor_visible

    @cursor_visible.setter
    def cursor_visible(self, value: bool):
        self._cursor_visible = value
        _wrapper.set_cursor_visibility(value)


class CustomWindowController:
    """
    Gives access to window (custom magnifier controller)
    functions of Magnification API
    """
    def __init__(self):
        self.hwnd: int = 0
        """
        | Magnification window handle
        | |Accessors: Get Set|
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
        | |Accessors: Get|
        """
        return self._transform

    @property
    def color_effect(self) -> ColorMatrixWrapper:
        """
        | Color transformations
        | |Accessors: Get|
        """
        return self._color_effect

    @property
    def source(self) -> SourceRectangleWrapper:
        """
        | Source area, to get origin pixels from
        | |Accessors: Get|
        """
        return self._source

    @property
    def filters(self) -> FiltersListWrapper:
        """
        | Window filtration list
        | |Accessors: Get|
        """
        return self._filters


class WinMagnificationAPI:
    """
    | :mod:`Object-Oriented wrapper <win_magnification._objects>` for Magnification API
    | Also manages :func:`.initialize` and :func:`.finalize` calls

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
        | |Accessors: Get|
        """
        return self.__fullscreen

    @property
    def window(self) -> CustomWindowController:
        """
        | Gives access to window (custom magnifier controller)
          functions of Magnification API
        | |Accessors: Get|
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
        Calls :meth:`.dispose` on object distraction
        """
        self.dispose()
