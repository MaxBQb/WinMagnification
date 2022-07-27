"""
| Wraps ctypes.windll.magnification
Author: MaxBQb |
`Microsoft Docs <https://docs.microsoft.com/en-us/windows/win32/api/_magapi/>`_ |
`Header <https://pastebin.com/Lh82NjjM>`_
"""
from __future__ import annotations

import ctypes
import sys
import typing
from ctypes import wintypes

from win_magnification import _utils
from win_magnification import const
from win_magnification import types

if sys.platform == 'win32':
    _DLL = ctypes.WinDLL('magnification.dll')
else:
    _DLL = None
    print("Magnification API exists only for Windows!")

# C Types
# noinspection SpellCheckingInspection
_MAGCOLOREFFECT = (ctypes.c_float * const.COLOR_MATRIX_SIZE)
# noinspection SpellCheckingInspection
_PMAGCOLOREFFECT = ctypes.POINTER(_MAGCOLOREFFECT)

# noinspection SpellCheckingInspection
_MAGTRANSFORM = (ctypes.c_float * const.TRANSFORMATION_MATRIX_SIZE)
# noinspection SpellCheckingInspection
_PMAGTRANSFORM = ctypes.POINTER(_MAGTRANSFORM)


# Functions
@_utils.raise_win_errors
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.

    :raises OSError: On fail
    """
    return _DLL.MagInitialize()


@_utils.raise_win_errors
def finalize() -> None:
    """
    Destroys the magnifier run-time objects.

    :raises OSError: On fail
    """
    return _DLL.MagUninitialize()


@_utils.require_single_thread()
@_utils.raise_win_errors
def set_fullscreen_color_effect(effect: types.ColorMatrix) -> None:
    """
    Changes the color transformation matrix associated with the full-screen magnifier.

    :param effect: The new color transformation matrix.
    :type effect: :data:`.ColorMatrix`
    :raises OSError: On fail
    :raises RuntimeError: |single thread|
    """
    return _DLL.MagSetFullscreenColorEffect(_utils.to_c_array(effect))


@_utils.require_single_thread()
def get_fullscreen_color_effect() -> types.ColorMatrix:
    """
    Retrieves the color transformation matrix associated with the full-screen magnifier.

    :return: The color transformation matrix, or the identity matrix (:data:`.COLOR_NO_EFFECT`)
        if no color effect has been set.
    :rtype: :data:`.ColorMatrix`
    :raises OSError: On fail
    :raises RuntimeError: |single thread|
    """
    result = _utils.to_c_array((0,) * const.COLOR_MATRIX_SIZE)
    _utils.handle_win_last_error(_DLL.MagGetFullscreenColorEffect(result))
    return _utils.to_py_array(result)


@_utils.require_single_thread()
@_utils.raise_win_errors
def set_fullscreen_transform(scale: float, offset: typing.Tuple[int, int]) -> None:
    """
    Changes the magnification settings for the full-screen magnifier.

    :param scale: The new magnification factor for the full-screen magnifier.
        1.0 <= scale <= 4096.0. If this value is 1.0, the screen content is not magnified and no offsets are applied.
    :param offset:
        The offset is relative to the |up-left| upper-left corner of the primary monitor, in unmagnified coordinates.
        -262144 <= (x, y) <= 262144.
    :raises OSError: On fail
    :raises RuntimeError: |single thread|
    """
    return _DLL.MagSetFullscreenTransform(scale, *offset)


@_utils.require_single_thread()
def get_fullscreen_transform() -> types.FullscreenTransform:
    """
    Retrieves the magnification settings for the full-screen magnifier.

    :return: Tuple of current **magnification factor** and **offset**
    :rtype: :data:`.FullscreenTransformRaw`
    :raises OSError: On fail
    :raises RuntimeError: |single thread|
    """
    scale = ctypes.pointer(ctypes.c_float())
    offset_x = ctypes.pointer(ctypes.c_int())
    offset_y = ctypes.pointer(ctypes.c_int())

    _utils.handle_win_last_error(_DLL.MagGetFullscreenTransform(scale, offset_x, offset_y))
    return (
        scale.contents.value, (
            offset_x.contents.value,
            offset_y.contents.value,
        )
    )


@_utils.raise_win_errors
def set_color_effect(hwnd: int, effect: typing.Optional[types.ColorMatrix]) -> None:
    """
    Sets the color transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param effect: The color transformation matrix, or None to remove the current color effect, if any.
    :type effect: :data:`.ColorMatrix`
    :raises OSError: On fail
    """
    return _DLL.MagSetColorEffect(
        hwnd,
        _utils.to_c_array(effect)
        if effect is not None
        else None
    )


def get_color_effect(hwnd: int) -> types.ColorMatrix:
    """
    Gets the color transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :return: Current color transformation matrix.
    :rtype: :data:`.ColorMatrix`
    :raises OSError: On fail
    """
    result = _utils.to_c_array((0,) * const.COLOR_MATRIX_SIZE)
    _utils.handle_win_last_error(_DLL.MagGetColorEffect(hwnd, result))
    if result is None:
        return const.DEFAULT_COLOR_EFFECT
    return _utils.to_py_array(result)


@_utils.raise_win_errors
def set_transform(hwnd: int, matrix: types.TransformationMatrix) -> None:
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param matrix: A 3x3 matrix of the magnification transformation
    :type matrix: :data:`.TransformationMatrix`
    :raises OSError: On fail
    """
    return _DLL.MagSetWindowTransform(hwnd, _utils.to_c_array(matrix))


def get_transform(hwnd: int) -> types.TransformationMatrix:
    """
    Use to get the magnification transformation matrix on the window provided by the window handle

    :param hwnd: The handle of the magnification window.
    :return: A 3x3 matrix of the magnification transformation.
    :rtype: :data:`.TransformationMatrix`
    :raises OSError: On fail
    """
    result = _utils.to_c_array((0,) * const.TRANSFORMATION_MATRIX_SIZE)
    _utils.handle_win_last_error(_DLL.MagGetWindowTransform(hwnd, result))
    if result is None:
        return const.DEFAULT_TRANSFORM
    return _utils.to_py_array(result)


@_utils.raise_win_errors
def set_source(hwnd: int, rectangle: types.Rectangle) -> None:
    """
    Sets the source rectangle for the magnification window.

    :param hwnd: The handle of the magnification window.
    :param rectangle: Magnification rectangle
    :type rectangle: :data:`.RectangleRaw`
    :raises OSError: On fail
    """
    return _DLL.MagSetWindowSource(hwnd, wintypes.RECT(*rectangle))


def get_source(hwnd: int) -> types.Rectangle:
    """
    Gets the rectangle of the area that is being magnified.

    :param hwnd: The handle of the magnification window.
    :return: Magnification rectangle
    :rtype: :data:`.RectangleRaw`
    :raises OSError: On fail
    """
    result = ctypes.pointer(wintypes.RECT(0, 0, 0, 0))
    _utils.handle_win_last_error(_DLL.MagGetWindowSource(hwnd, result))
    return _utils.to_py_rectangle(result.contents)


@_utils.raise_win_errors
def set_filters(root_hwnd: int, *hwnds: int, exclude=True) -> None:
    """
    | Sets the list of windows to be magnified or the list of windows to be excluded from magnification.
    | The magnification filter mode can be one of the following values:
    | **exclude** = False |=> INCLUDE (This value is not supported on Windows 7 or newer).
    | **exclude** = True |=> EXCLUDE (Magnifier acts as windows from list aren't exist at all)

    :param root_hwnd: The handle of the magnification window.
    :param exclude: The magnification filter mode.
    :param hwnds: List of window handles.
    :raises OSError: On fail
    """
    return _DLL.MagSetWindowFilterList(
        root_hwnd,
        const.MW_FILTERMODE_EXCLUDE if exclude else const.MW_FILTERMODE_INCLUDE,
        len(hwnds),
        _utils.to_c_array(hwnds, wintypes.HWND)
    )


def get_filters(hwnd: int) -> typing.Tuple[bool, typing.Tuple[int]]:
    """
    Retrieves the list of windows that are magnified or excluded from magnification.

    :param hwnd: The handle of the magnification window.
    :return: The filter mode and the list of window handles.
    :raises OSError: On fail
    :raises RuntimeError: On invalid hwnd used
    """
    exclude = ctypes.pointer(wintypes.DWORD())
    count = _DLL.MagGetWindowFilterList(hwnd, exclude, 0, None)
    if count == -1:
        raise RuntimeError(f"Invalid hwnd: {hwnd}")
    elif count == 0:
        return (  # type: ignore
            exclude.contents.value == const.MW_FILTERMODE_EXCLUDE,
            tuple()
        )
    result = (wintypes.HWND * count)(*((0,) * count))
    _DLL.MagGetWindowFilterList(hwnd, exclude, count, result)
    return (
        exclude.contents.value == const.MW_FILTERMODE_EXCLUDE,
        _utils.to_py_array(result, int)
    )


@_utils.raise_win_errors
def set_input_transform(is_enabled: bool, source: types.Rectangle, destination: types.Rectangle) -> None:
    """
    | Sets the current active input transformation for pen and touch input,
      represented as a source rectangle and a destination rectangle.
    | Requires the calling process to have `UIAccess <https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/user-account-control-only-elevate-uiaccess-applications-that-are-installed-in-secure-locations>`_ privileges.

    :param is_enabled: True to enable input transformation, or False to disable it.
    :param source: The new source rectangle, in unmagnified screen coordinates,
        that defines the area of the screen to magnify.
        This parameter is ignored if **is_enabled** is False.
    :type source: :data:`.RectangleRaw`
    :param destination: The new destination rectangle, in unmagnified screen coordinates,
        that defines the area of the screen where the magnified screen content is displayed.
        Pen and touch input in this rectangle is mapped to the source rectangle.
        This parameter is ignored if **is_enabled** is False.
    :type destination: :data:`.RectangleRaw`
    :raises OSError: On fail
    """
    return _DLL.MagSetInputTransform(
        is_enabled,
        ctypes.pointer(wintypes.RECT(*source)),
        ctypes.pointer(wintypes.RECT(*destination))
    )


def get_input_transform() -> types.InputTransform:
    """
    Retrieves the current input transformation for pen and touch input,
    represented as a source rectangle and a destination rectangle.

    :return: Tuple of **is_enabled**, **source** and **destination**
    :rtype: :data:`.InputTransformRaw`
    :raises OSError: On fail
    """
    is_enabled = ctypes.pointer(wintypes.BOOL())
    source = ctypes.pointer(wintypes.RECT())
    destination = ctypes.pointer(wintypes.RECT())

    _utils.handle_win_last_error(_DLL.MagGetInputTransform(is_enabled, source, destination))
    return (
        bool(is_enabled.contents.value),
        _utils.to_py_rectangle(source.contents),
        _utils.to_py_rectangle(destination.contents),
    )


@_utils.raise_win_errors
def set_cursor_visibility(show_cursor: bool):
    """
    Shows or hides the system cursor.

    .. note::
       Invisibility applies until cursor moves

    :param show_cursor: True to show the system cursor,
        or False to hide it.
    :raises OSError: On fail
    """
    return _DLL.MagShowSystemCursor(show_cursor)


# C-Function original names and signatures
if sys.platform == 'win32':
    _DLL.MagInitialize.restype = wintypes.BOOL
    _DLL.MagUninitialize.restype = wintypes.BOOL

    _DLL.MagGetFullscreenColorEffect.restype = wintypes.BOOL
    _DLL.MagGetFullscreenColorEffect.argtypes = (_PMAGCOLOREFFECT,)

    _DLL.MagSetFullscreenColorEffect.restype = wintypes.BOOL
    _DLL.MagSetFullscreenColorEffect.argtypes = (_PMAGCOLOREFFECT,)

    _DLL.MagSetFullscreenTransform.restype = wintypes.BOOL
    _DLL.MagSetFullscreenTransform.argtypes = (ctypes.c_float, ctypes.c_int,
                                               ctypes.c_int)

    _DLL.MagGetFullscreenTransform.restype = wintypes.BOOL
    _DLL.MagGetFullscreenTransform.argtypes = (ctypes.POINTER(ctypes.c_float),
                                               ctypes.POINTER(ctypes.c_int),
                                               ctypes.POINTER(ctypes.c_int))

    _DLL.MagSetColorEffect.restype = wintypes.BOOL
    _DLL.MagSetColorEffect.argtypes = (wintypes.HWND, _PMAGCOLOREFFECT,)

    _DLL.MagGetColorEffect.restype = wintypes.BOOL
    _DLL.MagGetColorEffect.argtypes = (wintypes.HWND, _PMAGCOLOREFFECT,)

    _DLL.MagSetWindowTransform.restype = wintypes.BOOL
    _DLL.MagSetWindowTransform.argtypes = (wintypes.HWND, _PMAGTRANSFORM,)

    _DLL.MagGetWindowTransform.restype = wintypes.BOOL
    _DLL.MagGetWindowTransform.argtypes = (wintypes.HWND, _PMAGTRANSFORM,)

    _DLL.MagSetWindowSource.restype = wintypes.BOOL
    _DLL.MagSetWindowSource.argtypes = (wintypes.HWND, wintypes.RECT)

    _DLL.MagGetWindowSource.restype = wintypes.BOOL
    _DLL.MagGetWindowSource.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.RECT))

    _DLL.MagSetWindowFilterList.restype = wintypes.BOOL
    _DLL.MagSetWindowFilterList.argtypes = (wintypes.HWND, wintypes.DWORD,
                                            ctypes.c_int, ctypes.POINTER(wintypes.HWND))

    _DLL.MagGetWindowFilterList.restype = wintypes.BOOL
    _DLL.MagGetWindowFilterList.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD),
                                            ctypes.c_int, ctypes.POINTER(wintypes.HWND))

    _DLL.MagGetInputTransform.restype = wintypes.BOOL
    _DLL.MagGetInputTransform.argtypes = (ctypes.POINTER(wintypes.BOOL),
                                          ctypes.POINTER(wintypes.RECT),
                                          ctypes.POINTER(wintypes.RECT))

    _DLL.MagSetInputTransform.restype = wintypes.BOOL
    _DLL.MagSetInputTransform.argtypes = (wintypes.BOOL,
                                          ctypes.POINTER(wintypes.RECT),
                                          ctypes.POINTER(wintypes.RECT))

    _DLL.MagShowSystemCursor.restype = wintypes.BOOL
    _DLL.MagShowSystemCursor.argtypes = (wintypes.BOOL,)
