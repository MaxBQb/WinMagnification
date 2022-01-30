"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://searchcode.com/codesearch/view/66549806/
"""
import contextlib
import threading
from ctypes import *
from ctypes.wintypes import *
from functools import partial, wraps
from typing import Callable

_DLL = WinDLL('magnification.dll')
_current_thread = None


# C Constants (feel free to use)
WC_MAGNIFIER = "Magnifier"
MS_SHOWMAGNIFIEDCURSOR = 1
MS_CLIPAROUNDCURSOR = 2
MS_INVERTCOLORS = 4
MW_FILTERMODE_INCLUDE = 0
MW_FILTERMODE_EXCLUDE = 1


# C Types
_MAGCOLOREFFECT = (c_float * 5) * 5
_PMAGCOLOREFFECT = POINTER(_MAGCOLOREFFECT)


# C Function structure
_DLL.MagInitialize.restype = BOOL

_DLL.MagUninitialize.restype = BOOL

_DLL.MagGetFullscreenColorEffect.restype = BOOL
_DLL.MagGetFullscreenColorEffect.argtypes = (_PMAGCOLOREFFECT,)

_DLL.MagSetFullscreenColorEffect.restype = BOOL
_DLL.MagSetFullscreenColorEffect.argtypes = (_PMAGCOLOREFFECT,)


_DLL.MagSetFullscreenTransform.restype = BOOL
_DLL.MagSetFullscreenTransform.argtypes = (c_float, c_int, c_int)

_DLL.MagGetFullscreenTransform.restype = BOOL
_DLL.MagGetFullscreenTransform.argtypes = (POINTER(c_float), POINTER(c_int), POINTER(c_int))


# Type hints
ColorMatrix = list[
    list[float, float, float, float, float],
    list[float, float, float, float, float],
    list[float, float, float, float, float],
    list[float, float, float, float, float],
    list[float, float, float, float, float],
]
"""
Red
Green
Blue
Alpha
Translation (affine transformation)

Matrix 5x5 affect color like so:
r*=x   g+=x*r b+=x*r a+=x*r 0
r+=x*g g*=x   b+=x*g a+=x*g 0
r+=x*b g+=x*b b*=x   a+=x*b 0
r+=x*a g+=x*a b+=x*a a*=x   0
r+=x   g+=x   b+=x   a+=x   1

More info: https://docs.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-using-a-color-matrix-to-transform-a-single-color-use
"""


# Color matrix
IDENTITY_MATRIX: ColorMatrix = [
     [1, 0, 0, 0, 0],
     [0, 1, 0, 0, 0],
     [0, 0, 1, 0, 0],
     [0, 0, 0, 1, 0],
     [0, 0, 0, 0, 1],
]
NO_EFFECT = IDENTITY_MATRIX

COLOR_INVERSION_EFFECT: ColorMatrix = [
     [-1, 0, 0, 0, 0],
     [0, -1, 0, 0, 0],
     [0, 0, -1, 0, 0],
     [0, 0, 0, 1, 0],
     [1, 1, 1, 0, 1],
]


# Defaults
DEFAULT_COLOR_EFFECT = NO_EFFECT
DEFAULT_FULLSCREEN_TRANSFORM = (1.0, (0, 0))


# Internal functions
def _raise_win_errors(win_function: Callable[..., bool]):
    @wraps(win_function)
    def wrapper(*args, **kwargs):
        if not win_function(*args, **kwargs):
            raise WinError()
    return wrapper


def _require_single_thread(win_function: Callable):
    @wraps(win_function)
    def wrapper(*args, **kwargs):
        if threading.current_thread().ident != _current_thread:
            raise RuntimeError("Magnification API must be accessed from a single thread!")
        return win_function(*args, **kwargs)
    return wrapper


def _get_empty_matrix(size: int):
    return [[0]*size for _ in range(size)]


def _to_py_matrix(c_matrix: Array[Array]):
    return list(map(list, c_matrix))


def _to_c_matrix(matrix: list[list], content_type=c_float):
    return (content_type*len(matrix)*len(matrix))(*[
        (content_type*len(row))(*row) for row in matrix
    ])


def _get_alternative(value, default):
    return default if value is None else value


# Functions
@_raise_win_errors
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    return _DLL.MagInitialize()


def safe_initialize():
    global _current_thread
    current_thread = threading.current_thread().ident
    if current_thread == _current_thread:
        raise RuntimeError("Magnification API already initialized!")
    if _current_thread is not None:
        raise RuntimeError("Magnification API must be accessed from a single thread!")
    initialize()
    _current_thread = current_thread


@_raise_win_errors
def uninitialize() -> None:
    """
    Destroys the magnifier run-time objects.
    """
    return _DLL.MagUninitialize()


def safe_uninitialize():
    global _current_thread
    current_thread = threading.current_thread().ident
    if _current_thread is None:
        raise RuntimeError("Magnification API has not been initialized yet!")
    if current_thread != _current_thread:
        raise RuntimeError("Magnification API must be accessed from a single thread!")
    uninitialize()
    _current_thread = None


@_require_single_thread
@_raise_win_errors
def set_fullscreen_color_effect(effect: ColorMatrix) -> None:
    """
    Changes the color transformation matrix associated with the full-screen magnifier.

    :param effect: The new color transformation matrix.
    This parameter must not be None.
    """
    return _DLL.MagSetFullscreenColorEffect(_to_c_matrix(effect))


@_require_single_thread
def get_fullscreen_color_effect() -> ColorMatrix:
    """
    Retrieves the color transformation matrix associated with the full-screen magnifier.

    :return: The color transformation matrix, or the identity matrix if no color effect has been set.
    """
    result = _to_c_matrix(_get_empty_matrix(5))
    _raise_win_errors(_DLL.MagGetFullscreenColorEffect(result))
    return _to_py_matrix(result)


@_require_single_thread
@_raise_win_errors
def set_fullscreen_transform(scale: float, offset: tuple[int, int]) -> None:
    """
    Changes the magnification settings for the full-screen magnifier.

    :param scale: The new magnification factor for the full-screen magnifier.
    1.0 <= scale <= 4096.0. If this value is 1.0, the screen content is not magnified and no offsets are applied.
    :param offset:
    The offset is relative to the upper-left corner of the primary monitor, in unmagnified coordinates.
    -262144 <= (x, y) <= 262144.
    """
    return _DLL.MagSetFullscreenTransform(scale, *offset)


@_require_single_thread
def get_fullscreen_transform() -> tuple[float, tuple[int, int]]:
    """
    Retrieves the magnification settings for the full-screen magnifier.

    :return: Current magnification factor and offset (x, y)
    The current magnification factor for the full-screen magnifier:
        - 1.0 = screen content is not being magnified.
        - > 1.0 = scale factor for magnification.
        - < 1.0 is not valid.
    The offset is relative to the upper-left corner of the primary monitor, in unmagnified coordinates.
    """
    scale = pointer(c_float())
    offset_x = pointer(c_int())
    offset_y = pointer(c_int())
    _raise_win_errors(_DLL.MagGetFullscreenTransform(scale, offset_x, offset_y))
    return (
        scale.contents.value, (
            offset_x.contents.value,
            offset_y.contents.value,
        )
    )


# Extra functions
reset_fullscreen_color_effect = partial(set_fullscreen_color_effect, effect=DEFAULT_COLOR_EFFECT)
reset_fullscreen_transform = partial(set_fullscreen_transform, *DEFAULT_FULLSCREEN_TRANSFORM)


@contextlib.contextmanager
def require_components():
    try:
        safe_initialize()
        yield
    finally:
        safe_uninitialize()


# Compatability with original function names
MagInitialize = initialize
MagUninitialize = uninitialize
MagSetFullscreenColorEffect = set_fullscreen_color_effect
MagGetFullscreenColorEffect = get_fullscreen_color_effect
MagSetFullscreenTransform = set_fullscreen_transform
MagGetFullscreenTransform = get_fullscreen_transform


# Object-Oriented Interface
class WinMagnificationAPI:
    def __init__(self):
        safe_initialize()
        self.__fullscreen_transform = FullscreenTransform()

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
        safe_uninitialize()


class FullscreenTransform:
    def __init__(self):
        self.__offset = FullscreenTransform._Offset(self)

    def _change(self,
                scale: float = None,
                x: int = None,
                y: int = None):
        _scale, (_x, _y) = self.raw
        self.raw = (
            _get_alternative(scale, _scale),
            (_get_alternative(x, _x),
             _get_alternative(y, _y))
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
    def offset(self) -> 'FullscreenTransform._Offset':
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
        def __init__(self, outer: 'FullscreenTransform'):
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
