"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://searchcode.com/codesearch/view/66549806/
"""
from ctypes import *
from ctypes.wintypes import *
from typing import Optional

_DLL = WinDLL('magnification.dll')


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
def _get_empty_matrix(size: int):
    return [[0]*size for _ in range(size)]


def _to_py_matrix(c_matrix: Array[Array]):
    return list(map(list, c_matrix))


def _to_с_matrix(matrix: list[list], content_type=c_float):
    return (content_type*len(matrix)*len(matrix))(*[
        (content_type*len(row))(*row) for row in matrix
    ])


# Functions
def initialize() -> bool:
    """
    Creates and initializes the magnifier run-time objects.

    :return: True if successful.
    """
    return _DLL.MagInitialize()


def uninitialize() -> bool:
    """
    Destroys the magnifier run-time objects.

    :return: True if successful.
    """
    return _DLL.MagUninitialize()


def set_fullscreen_color_effect(effect: ColorMatrix):
    """
    Changes the color transformation matrix associated with the full-screen magnifier.

    :param effect: The new color transformation matrix.
    This parameter must not be None.
    :return: True if successful.
    """
    return _DLL.MagSetFullscreenColorEffect(_to_с_matrix(effect))


def get_fullscreen_color_effect() -> Optional[ColorMatrix]:
    """
    Retrieves the color transformation matrix associated with the full-screen magnifier.

    :return: The color transformation matrix, or the identity matrix if no color effect has been set.
    """
    result = _to_с_matrix(_get_empty_matrix(5))
    if _DLL.MagGetFullscreenColorEffect(result):
        return _to_py_matrix(result)


# Compatability with original function names
MagInitialize = initialize
MagUninitialize = uninitialize
MagSetFullscreenColorEffect = set_fullscreen_color_effect
MagGetFullscreenColorEffect = get_fullscreen_color_effect
