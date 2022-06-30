import typing

from . import _utils, _wrapper
from . import const
from . import types
from . import tools


@_utils.require_single_thread()  # type: ignore
def initialize() -> None:
    """
    Creates and initializes the magnifier run-time objects.
    """
    _utils.thread_holder.lock.acquire()
    _wrapper.initialize()
    _utils.thread_holder.hold_current_thread()


@_utils.require_single_thread()  # type: ignore
def finalize() -> None:
    """
    Destroys the magnifier run-time objects.
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
    """
    _wrapper.set_transform(hwnd, matrix)


def set_transform(hwnd: int, scale: typing.Union[float, typing.Tuple[float, float]]):  # type: ignore
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param scale: Magnification factor, or it's separate x, y components
    """
    scale_x, scale_y = scale if isinstance(scale, tuple) else (scale, scale)
    set_transform_advanced(hwnd, tools.get_transform_matrix(scale_x, scale_y))


def reset_fullscreen_color_effect():
    """
    Resets the color transformation matrix associated with the full-screen magnifier.
    """
    _wrapper.set_fullscreen_color_effect(const.DEFAULT_COLOR_EFFECT)


def reset_fullscreen_transform():
    """
    Resets the magnification settings for the full-screen magnifier.
    """
    _wrapper.set_fullscreen_transform(*const.DEFAULT_FULLSCREEN_TRANSFORM)


def reset_transform(hwnd: int):
    """
    Resets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    """
    set_transform_advanced(hwnd, const.DEFAULT_TRANSFORM)


def reset_color_effect(hwnd: int):
    """
    Resets the color transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    """
    _wrapper.set_color_effect(hwnd, const.DEFAULT_COLOR_EFFECT)
