from functools import partial

from . import _utils, _wrapper
from .defaults import *


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


def set_transform_advanced(hwnd: int, matrix: TransformationMatrix) -> None:
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param matrix: A 3x3 matrix of the magnification transformation
    """
    _wrapper.set_transform(hwnd, matrix)


def set_transform(hwnd: int, scale: typing.Union[float, tuple[float, float]]):  # type: ignore
    """
    Sets the transformation matrix for a magnifier control.

    :param hwnd: The handle of the magnification window.
    :param scale: Magnification factor, or it's separate x, y components
    """
    scale_x, scale_y = scale if isinstance(scale, tuple) else (scale, scale)
    set_transform_advanced(hwnd, get_transform_matrix(scale_x, scale_y))


reset_fullscreen_color_effect = partial(_wrapper.set_fullscreen_color_effect, effect=DEFAULT_COLOR_EFFECT)
reset_fullscreen_transform = partial(_wrapper.set_fullscreen_transform, *DEFAULT_FULLSCREEN_TRANSFORM)
reset_transform = partial(set_transform_advanced, matrix=DEFAULT_TRANSFORM)
reset_color_effect = partial(_wrapper.set_color_effect, effect=DEFAULT_COLOR_EFFECT)
