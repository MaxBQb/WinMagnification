from __future__ import annotations

import typing

from win_magnification import _utils, _wrapper
from win_magnification import const
from win_magnification import tools
from win_magnification import types


@_utils.require_single_thread()  # type: ignore
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.

    :raises OSError: On fail
    :raises RuntimeError: |single thread|
    """
    _utils.thread_holder.lock.acquire()
    _wrapper.initialize()
    _utils.thread_holder.hold_current_thread()


@_utils.require_single_thread()  # type: ignore
def finalize() -> None:
    """
    Destroys the magnifier run-time objects.

    :raises OSError: On fail
    :raises RuntimeError: If :func:`initialize` never called
    :raises RuntimeError: |single thread|
    """
    if not _utils.thread_holder.has_content:
        raise RuntimeError("Magnification API has not been initialized yet!")
    _wrapper.finalize()
    _utils.thread_holder.release_thread()


def set_transform_advanced(hwnd: int, matrix: types.TransformationMatrix) -> None:
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param matrix: A 3x3 matrix of the magnification transformation
    :type matrix: :data:`.TransformationMatrix`
    :raises OSError: On fail
    """
    _wrapper.set_transform(hwnd, matrix)


def get_transform_advanced(hwnd: int) -> types.TransformationMatrix:
    """
    Use to get the magnification transformation matrix on the window provided by the window handle

    :param hwnd: The handle of the magnification window.
    :return: A 3x3 matrix of the magnification transformation.
    :rtype: :data:`.TransformationMatrix`
    :raises OSError: On fail
    """
    return _wrapper.get_transform(hwnd)


def set_transform(
    hwnd: int,
    scale: typing.Union[float, typing.Tuple[float, float]],
    offset: typing.Union[float, typing.Tuple[float, float]] = 0.0,
):  # type: ignore
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param scale: Magnification factor, or it's separate x, y components
    :param offset: Magnifier offset from |up-left| left upper corner
    :raises OSError: On fail
    """
    set_transform_advanced(hwnd, tools.get_transform_matrix(
        *(scale if isinstance(scale, tuple) else (scale, scale)),
        *(offset if isinstance(offset, tuple) else (offset, offset))
    ))


def to_simple_transform(matrix: types.TransformationMatrix) -> types.SimpleTransform:
    """
    Get (scale, offset) tuple from **matrix**

    >>> to_simple_transform(tools.get_transform_matrix(1.0, 2.0, 3.0, 4.0))
    ((1.0, 2.0), (3.0, 4.0))

    :param matrix: Raw transform matrix
    :return: (scale, offset)
    :raises OSError: On fail
    """
    scale_x, scale_y, offset_x, offset_y = tools.extract_from_matrix(
        matrix, *const.DEFAULT_TRANSFORM_EXTRACTION_PATTERN
    )
    if offset_y != 0.0:
        offset_y = -offset_y
    if offset_x != 0.0:
        offset_x = -offset_x
    return (
        (scale_x, scale_y),
        (offset_x, offset_y)
    )


def get_transform(hwnd: int) -> types.SimpleTransform:
    """
    Use to get the magnification transformation (**scale**, **offset**) on the window provided by the window handle
    **Offset** counts from |up-left| left-upper corner of magnification window

    :param hwnd: The handle of the magnification window.
    :return: Tuple of **scale** (x, y) and **offset** (x, y)
    :raises OSError: On fail
    """
    return to_simple_transform(get_transform_advanced(hwnd))


def reset_fullscreen_color_effect():
    """
    Resets the color transformation matrix associated with the full-screen magnifier.

    :raises OSError: On fail
    """
    _wrapper.set_fullscreen_color_effect(const.DEFAULT_COLOR_EFFECT)


def reset_fullscreen_transform():
    """
    Resets the magnification settings for the full-screen magnifier.

    :raises OSError: On fail
    """
    _wrapper.set_fullscreen_transform(*const.DEFAULT_FULLSCREEN_TRANSFORM)


def reset_transform(hwnd: int):
    """
    Resets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :raises OSError: On fail
    """
    set_transform_advanced(hwnd, const.DEFAULT_TRANSFORM)


def reset_color_effect(hwnd: int):
    """
    Resets the color transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :raises OSError: On fail
    """
    _wrapper.set_color_effect(hwnd, const.DEFAULT_COLOR_EFFECT)
