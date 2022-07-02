"""
Color effects inspired by:
- windows color effects
- https://zerowidthjoiner.net/negativescreen
- css filters
- https://webplatform.github.io/docs/css/functions/sepia/

Author: MaxBQb
"""

import win_magnification as mag


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    mag.const.COLOR_INVERSION_EFFECT,
))
def inversion(value=1.0) -> mag.types.ColorMatrix:
    """
    Invert colors (black -> white, white -> black)
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color inversion effect matrix
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    mag.const.COLOR_GRAYSCALE_EFFECT,
))
def grayscale(value=1.0) -> mag.types.ColorMatrix:
    """
    All colors become shades of gray
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color grayscale effect matrix
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    mag.const.COLOR_SEPIA_EFFECT,
))
def sepia(value=1.0) -> mag.types.ColorMatrix:
    """
    Applies sepia effect
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color sepia effect matrix
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    (1.2, 0.0, 0.0, 0.0, -0.2,
     0.0, 1.2, 0.0, 0.0, -0.2,
     0.0, 0.0, 1.2, 0.0, -0.2,
     0.0, 0.0, 0.0, 1.0, 0.0,
     0.0, 0.0, 0.0, 0.0, 1.0,),
))
def contrast(value=1.0) -> mag.types.ColorMatrix:
    """
    Make colors more bright and contrast
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color sepia effect matrix
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    (127.0, 127.0, 127.0, 0.0, 0.0,
     127.0, 127.0, 127.0, 0.0, 0.0,
     127.0, 127.0, 127.0, 0.0, 0.0,
     0.0, 0.0, 0.0, 1.0, 0.0,
     -180.0, -180.0, -180.0, 0.0, 1.0,)
))
def binary(value=1) -> mag.types.ColorMatrix:
    """
    Only white and black colors stay
    :param value: int -1..1 type of effect applied
    -1 = binary inversion
    0 = no effect applied
    1 = binary color
    :return: Color binary effect matrix
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    mag.const.COLOR_BLIND_DEUTERANOPIA_EFFECT,
))
def blindness_deuteranopia(value=1.0) -> mag.types.ColorMatrix:
    """
    Simulates color blindness: Deuteranomaly (green-weak)
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color effect matrix adjusted for deuteranopia
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    mag.const.COLOR_BLIND_PROTANOPIA_EFFECT,
))
def blindness_protanopia(value=1.0) -> mag.types.ColorMatrix:
    """
    Simulates color blindness: Protanomaly (red-weak)
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color effect matrix adjusted for protanopia
    """


@mag.tools.replace(mag.tools.get_transition(
    mag.const.COLOR_NO_EFFECT,
    mag.const.COLOR_BLIND_TRITANOPIA_EFFECT,
))
def blindness_tritanopia(value=1.0) -> mag.types.ColorMatrix:
    """
    Simulates color blindness: Tritanomaly (blue-yellow weak)
    :param value: float 0..1 power of effect applied
    0 when no effect applied
    1 when effect fully applied
    :return: Color effect matrix adjusted for tritanopia
    """
