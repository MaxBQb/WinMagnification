"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
from ctypes import *
from ctypes.wintypes import *
from typing import Optional
from defaults import *
import _utils

_DLL = WinDLL('magnification.dll')

# C Types
# noinspection SpellCheckingInspection
_MAGCOLOREFFECT = (c_float * ColorMatrixSize)
# noinspection SpellCheckingInspection
_PMAGCOLOREFFECT = POINTER(_MAGCOLOREFFECT)

# noinspection SpellCheckingInspection
_MAGTRANSFORM = (c_float * TransformationMatrixSize)
# noinspection SpellCheckingInspection
_PMAGTRANSFORM = POINTER(_MAGTRANSFORM)


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
    return _DLL.MagSetFullscreenColorEffect(_utils.to_c_array(effect))


@_utils.require_single_thread()
def get_fullscreen_color_effect() -> ColorMatrix:
    """
    Retrieves the color transformation matrix associated with the full-screen magnifier.

    :return: The color transformation matrix, or the identity matrix if no color effect has been set.
    """
    result = _utils.to_c_array((0,) * ColorMatrixSize)
    _utils.handle_win_last_error(_DLL.MagGetFullscreenColorEffect(result))
    return _utils.to_py_array(result)


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
def get_fullscreen_transform() -> FullscreenTransformRaw:
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


@_utils.raise_win_errors
def set_color_effect(hwnd: int, effect: Optional[ColorMatrix]) -> None:
    """
    Sets the color transformation matrix for a magnifier control.

    :param hwnd: The magnification window.
    :param effect: The color transformation matrix, or None to remove the current color effect, if any.
    """
    return _DLL.MagSetColorEffect(
        hwnd,
        _utils.to_c_array(effect)
        if effect is not None
        else None
    )


def get_color_effect(hwnd: int) -> ColorMatrix:
    """
    Gets the color transformation matrix for a magnifier control.

    :param hwnd: The magnification window.
    :return: The color transformation matrix, or None if no color effect has been set.
    """
    result = _utils.to_c_array((0,) * ColorMatrixSize)
    _utils.handle_win_last_error(_DLL.MagGetColorEffect(hwnd, result))
    return _utils.to_py_array(result)


@_utils.raise_win_errors
def set_transform(hwnd: int, matrix: TransformationMatrix) -> None:
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param matrix: A 3x3 matrix of the magnification transformation
    """
    return _DLL.MagSetWindowTransform(hwnd, _utils.to_c_array(matrix))


def get_transform(hwnd: int) -> TransformationMatrix:
    """
    Use to get the magnification transformation matrix on the window provided by the window handle

    :param hwnd: The handle of the magnification window.
    :return: A 3x3 matrix of the magnification transformation.
    """
    result = _utils.to_c_array((0,) * TransformationMatrixSize)
    _utils.handle_win_last_error(_DLL.MagGetWindowTransform(hwnd, result))
    return _utils.to_py_array(result)


@_utils.raise_win_errors
def set_source(hwnd: int, rectangle: Rectangle) -> None:
    """
    Sets the source rectangle for the magnification window.

    :param hwnd: The handle of the magnification window.
    :param rectangle: Magnification rectangle (left, top, right, bottom)
    """
    return _DLL.MagSetWindowSource(hwnd, RECT(*rectangle))


def get_source(hwnd: int) -> Rectangle:
    """
    Gets the rectangle of the area that is being magnified.

    :param hwnd: The window handle.
    :return: Magnification rectangle (left, top, right, bottom)
    """
    result = pointer(RECT(0, 0, 0, 0))
    _utils.handle_win_last_error(_DLL.MagGetWindowSource(hwnd, result))
    return _utils.to_py_rectangle(result.contents)


@_utils.raise_win_errors
def set_filters(root_hwnd: int, *hwnds: int, exclude=True) -> None:
    """
    Sets the list of windows to be magnified or the list of windows to be excluded from magnification.

    :param root_hwnd: The handle of the magnification window.
    :param exclude: The magnification filter mode. It can be one of the following values:
        False = INCLUDE (This value is not supported on Windows 7 or newer).
        True = EXCLUDE (Magnifier acts as windows from list aren't exist at all)
    :param hwnds: List of window handles.
    """
    return _DLL.MagSetWindowFilterList(
        root_hwnd,
        MW_FILTERMODE_EXCLUDE if exclude else MW_FILTERMODE_INCLUDE,
        len(hwnds),
        _utils.to_c_array(hwnds, HWND)
    )


def get_filters(hwnd: int) -> tuple[bool, tuple[int]]:
    """
    Retrieves the list of windows that are magnified or excluded from magnification.

    :param hwnd: The magnification window.
    :return: The filter mode and the list of window handles.
    """
    exclude = pointer(DWORD())
    count = _DLL.MagGetWindowFilterList(hwnd, exclude, 0, None)
    if count == -1:
        raise RuntimeError(f"Invalid hwnd: {hwnd}")
    elif count == 0:
        return (
            exclude.contents.value == MW_FILTERMODE_EXCLUDE,
            tuple()
        )
    result = (HWND * count)(*((0,) * count))
    _DLL.MagGetWindowFilterList(hwnd, exclude, count, result)
    return (
        exclude.contents.value == MW_FILTERMODE_EXCLUDE,
        _utils.to_py_array(result, int)
    )


# C-Function original names and signatures
MagInitialize = initialize
_DLL.MagInitialize.restype = BOOL

# noinspection SpellCheckingInspection
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

MagSetColorEffect = set_color_effect
_DLL.MagSetColorEffect.restype = BOOL
_DLL.MagSetColorEffect.argtypes = (HWND, _PMAGCOLOREFFECT,)

MagGetColorEffect = get_color_effect
_DLL.MagGetColorEffect.restype = BOOL
_DLL.MagGetColorEffect.argtypes = (HWND, _PMAGCOLOREFFECT,)

MagSetWindowTransform = set_transform
_DLL.MagSetWindowTransform.restype = BOOL
_DLL.MagSetWindowTransform.argtypes = (HWND, _PMAGTRANSFORM,)

MagGetWindowTransform = get_transform
_DLL.MagGetWindowTransform.restype = BOOL
_DLL.MagGetWindowTransform.argtypes = (HWND, _PMAGTRANSFORM,)

MagSetWindowSource = set_source
_DLL.MagSetWindowSource.restype = BOOL
_DLL.MagSetWindowSource.argtypes = (HWND, RECT)

MagGetWindowSource = get_source
_DLL.MagGetWindowSource.restype = BOOL
_DLL.MagGetWindowSource.argtypes = (HWND, POINTER(RECT))

MagSetWindowFilterList = set_filters
_DLL.MagSetWindowFilterList.restype = BOOL
_DLL.MagSetWindowFilterList.argtypes = (HWND, DWORD, c_int, POINTER(HWND))

MagGetWindowFilterList = get_filters
_DLL.MagGetWindowFilterList.restype = BOOL
_DLL.MagGetWindowFilterList.argtypes = (HWND, POINTER(DWORD), c_int, POINTER(HWND))
