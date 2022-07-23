"""
| Color effects (color transformation matrices)
| Inspired by:
- windows color filters
- `negative screen color matrices <https://zerowidthjoiner.net/negativescreen>`_
- `css filters <https://webplatform.github.io/docs/css/functions/sepia/>`_
| `More about color transformations <https://docs.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-using-a-color-matrix-to-transform-a-single-color-use>`_
| Author: MaxBQb
"""
from __future__ import annotations

from win_magnification import const
from win_magnification import tools
from win_magnification import types


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    const.COLOR_INVERSION_EFFECT,
))
def inversion(value=1.0) -> types.ColorMatrix:
    """
    | Invert colors (black -> white, white -> black)
    | Uses :func:`.get_transition`

    :param value: Power of effect applied
    :return: Color inversion effect matrix
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    const.COLOR_GRAYSCALE_EFFECT,
))
def grayscale(value=1.0) -> types.ColorMatrix:
    """
    | All colors become shades of gray
    | Uses :func:`.get_transition`

    :param value: Power of effect applied
    :return: Color grayscale effect matrix
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    const.COLOR_SEPIA_EFFECT,
))
def sepia(value=1.0) -> types.ColorMatrix:
    """
    | All colors become shades of brown
    | Uses :func:`.get_transition`

    :param value: Power of effect applied
    :return: Color sepia effect matrix
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    (1.2, 0.0, 0.0, 0.0, -0.2,
     0.0, 1.2, 0.0, 0.0, -0.2,
     0.0, 0.0, 1.2, 0.0, -0.2,
     0.0, 0.0, 0.0, 1.0, 0.0,
     0.0, 0.0, 0.0, 0.0, 1.0,),
))
def contrast(value=1.0) -> types.ColorMatrix:
    """
    | Make colors more bright and contrast
    | Uses :func:`.get_transition`
    | Example:

    >>> tools.print_matrix(contrast())
    1.2  0.0  0.0  0.0 -0.2
    0.0  1.2  0.0  0.0 -0.2
    0.0  0.0  1.2  0.0 -0.2
    0.0  0.0  0.0  1.0  0.0
    0.0  0.0  0.0  0.0  1.0

    :param value: Power of effect applied
    :return: Color sepia effect matrix
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    (127.0, 127.0, 127.0, 0.0, 0.0,
     127.0, 127.0, 127.0, 0.0, 0.0,
     127.0, 127.0, 127.0, 0.0, 0.0,
     0.0, 0.0, 0.0, 1.0, 0.0,
     -180.0, -180.0, -180.0, 0.0, 1.0,)
))
def binary(value=1) -> types.ColorMatrix:
    """
    | Only white and black colors stay
    | Uses :func:`.get_transition`
    | Example:

    >>> tools.print_matrix(binary())
     127.0  127.0  127.0  0.0  0.0
     127.0  127.0  127.0  0.0  0.0
     127.0  127.0  127.0  0.0  0.0
     0.0    0.0    0.0    1.0  0.0
    -180.0 -180.0 -180.0  0.0  1.0

    :param value: Power of effect applied, normally uses -1, 0, 1,
        on low values (like 0.001) act like :func:`.get_transition` value
    :return: Color binary effect matrix
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    const.COLOR_BLIND_DEUTERANOPIA_EFFECT,
))
def blindness_deuteranopia(value=1.0) -> types.ColorMatrix:
    """
    | Simulates color blindness: Deuteranomaly (green-weak)
    | Uses :func:`.get_transition`

    :param value: Power of effect applied
    :return: Color effect matrix adjusted for deuteranopia
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    const.COLOR_BLIND_PROTANOPIA_EFFECT,
))
def blindness_protanopia(value=1.0) -> types.ColorMatrix:
    """
    | Simulates color blindness: Protanomaly (red-weak)
    | Uses :func:`.get_transition`

    :param value: Power of effect applied
    :return: Color effect matrix adjusted for protanopia
    """


@tools.replace(tools.get_transition(
    const.COLOR_NO_EFFECT,
    const.COLOR_BLIND_TRITANOPIA_EFFECT,
))
def blindness_tritanopia(value=1.0) -> types.ColorMatrix:
    """
    | Simulates color blindness: Tritanomaly (blue-yellow weak)
    | Uses :func:`.get_transition`

    :param value: Power of effect applied
    :return: Color effect matrix adjusted for tritanopia
    """
