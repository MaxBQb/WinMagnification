"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://searchcode.com/codesearch/view/66549806/
"""
import threading
from ctypes import *
from ctypes.wintypes import *

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


# Internal functions
def _raise_win_errors(win_function):
    def wrapper(*args, **kwargs):
        if not win_function(*args, **kwargs):
            raise WinError()
    return wrapper


def _reload_on_thread_changed(win_function):
    def wrapper(*args, **kwargs):
        global _current_thread
        current_thread = threading.current_thread().name
        if current_thread != _current_thread:
            _current_thread = current_thread
            uninitialize()
            initialize()
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


# Functions
@_raise_win_errors
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    return _DLL.MagInitialize()


@_raise_win_errors
def uninitialize() -> None:
    """
    Destroys the magnifier run-time objects.
    """
    return _DLL.MagUninitialize()


@_reload_on_thread_changed
@_raise_win_errors
def set_fullscreen_color_effect(effect: ColorMatrix) -> None:
    """
    Changes the color transformation matrix associated with the full-screen magnifier.

    :param effect: The new color transformation matrix.
    This parameter must not be None.
    """
    return _DLL.MagSetFullscreenColorEffect(_to_c_matrix(effect))


@_reload_on_thread_changed
def get_fullscreen_color_effect() -> ColorMatrix:
    """
    Retrieves the color transformation matrix associated with the full-screen magnifier.

    :return: The color transformation matrix, or the identity matrix if no color effect has been set.
    """
    result = _to_c_matrix(_get_empty_matrix(5))
    _raise_win_errors(_DLL.MagGetFullscreenColorEffect(result))
    return _to_py_matrix(result)


@_reload_on_thread_changed
@_raise_win_errors
def set_fullscreen_transform(magnification_level: float, offset: tuple[int, int]):
    """
    Changes the magnification settings for the full-screen magnifier.

    :param magnification_level: The new magnification factor for the full-screen magnifier.
    1.0 <= magnification_level <= 4096.0. If this value is 1.0, the screen content is not magnified and no offsets are applied.
    :param offset:
    The offset is relative to the upper-left corner of the primary monitor, in unmagnified coordinates.
    -262144 <= (x, y) <= 262144.
    """
    return _DLL.MagSetFullscreenTransform(magnification_level, *offset)


@_reload_on_thread_changed
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
    magnification_level = pointer(c_float())
    offset_x = pointer(c_int())
    offset_y = pointer(c_int())
    _raise_win_errors(_DLL.MagGetFullscreenTransform(magnification_level, offset_x, offset_y))
    return (
        magnification_level.contents.value, (
            offset_x.contents.value,
            offset_y.contents.value,
        )
    )


# Compatability with original function names
MagInitialize = initialize
MagUninitialize = uninitialize
MagSetFullscreenColorEffect = set_fullscreen_color_effect
MagGetFullscreenColorEffect = get_fullscreen_color_effect
MagSetFullscreenTransform = set_fullscreen_transform
MagGetFullscreenTransform = get_fullscreen_transform


# Object-Oriented Interface
class WinMagnificationAPI:
    @property
    def fullscreen_color_effect(self):
        return get_fullscreen_color_effect()

    @fullscreen_color_effect.setter
    def fullscreen_color_effect(self, value: ColorMatrix):
        set_fullscreen_color_effect(value)

    @property
    def fullscreen_transform(self):
        return get_fullscreen_transform()

    @fullscreen_transform.setter
    def fullscreen_transform(self, value: tuple[float, tuple[int, int]]):
        set_fullscreen_transform(*value)

    def __del__(self):
        uninitialize()
