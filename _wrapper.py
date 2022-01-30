"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://searchcode.com/codesearch/view/66549806/
"""
from ctypes import *
from ctypes.wintypes import *

import _utils
from constants import *

_DLL = WinDLL('magnification.dll')


# C Types
_MAGCOLOREFFECT = (c_float * 5) * 5
_PMAGCOLOREFFECT = POINTER(_MAGCOLOREFFECT)


# Functions
@_utils.raise_win_errors
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    return _DLL.MagInitialize()


@_utils.raise_win_errors
def finalize() -> None:
    """
    Destroys the magnifier run-time objects.
    """
    return _DLL.MagUninitialize()


@_utils.require_single_thread()
@_utils.raise_win_errors
def set_fullscreen_color_effect(effect: ColorMatrix) -> None:
    """
    Changes the color transformation matrix associated with the full-screen magnifier.

    :param effect: The new color transformation matrix.
    This parameter must not be None.
    """
    return _DLL.MagSetFullscreenColorEffect(_utils.to_c_matrix(effect))


@_utils.require_single_thread()
def get_fullscreen_color_effect() -> ColorMatrix:
    """
    Retrieves the color transformation matrix associated with the full-screen magnifier.

    :return: The color transformation matrix, or the identity matrix if no color effect has been set.
    """
    result = _utils.to_c_matrix(_utils.get_empty_matrix(5))
    _utils.handle_win_last_error(_DLL.MagGetFullscreenColorEffect(result))
    return _utils.to_py_matrix(result)


@_utils.require_single_thread()
@_utils.raise_win_errors
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


@_utils.require_single_thread()
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

    _utils.handle_win_last_error(_DLL.MagGetFullscreenTransform(scale, offset_x, offset_y))
    return (
        scale.contents.value, (
            offset_x.contents.value,
            offset_y.contents.value,
        )
    )


# C-Function original names and signatures
MagInitialize = initialize
_DLL.MagInitialize.restype = BOOL

MagUninitialize = finalize
_DLL.MagUninitialize.restype = BOOL

MagGetFullscreenColorEffect = get_fullscreen_color_effect
_DLL.MagGetFullscreenColorEffect.restype = BOOL
_DLL.MagGetFullscreenColorEffect.argtypes = (_PMAGCOLOREFFECT,)

MagSetFullscreenColorEffect = set_fullscreen_color_effect
_DLL.MagSetFullscreenColorEffect.restype = BOOL
_DLL.MagSetFullscreenColorEffect.argtypes = (_PMAGCOLOREFFECT,)

MagSetFullscreenTransform = set_fullscreen_transform
_DLL.MagSetFullscreenTransform.restype = BOOL
_DLL.MagSetFullscreenTransform.argtypes = (c_float, c_int, c_int)

MagGetFullscreenTransform = get_fullscreen_transform
_DLL.MagGetFullscreenTransform.restype = BOOL
_DLL.MagGetFullscreenTransform.argtypes = (POINTER(c_float), POINTER(c_int), POINTER(c_int))
