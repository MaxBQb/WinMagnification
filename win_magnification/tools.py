"""
Additional tools available for programmer

Author: MaxBQb
"""
import math
import win_magnification.types as mag_types


def pos_for_matrix(array_len: int, *coords: int) -> int:
    row_len = int(math.log(array_len, len(coords)))
    return sum(
        row_len ** i * pos for (i, pos) in enumerate(reversed(coords), 0)
    )


def get_transform_matrix(x=1.0, y=1.0) -> mag_types.TransformationMatrix:
    return (
        x, 0.0, 0.0,
        0.0, y, 0.0,
        0.0, 0.0, 1.0,
    )


def get_color_matrix(
        mul_red=1.0, mul_green=1.0, mul_blue=1.0, mul_alpha=1.0,
        add_red=0.0, add_green=0.0, add_blue=0.0, add_alpha=0.0,
) -> mag_types.ColorMatrix:
    return (
        mul_red, 0.0, 0.0, 0.0, 0.0,
        0.0, mul_green, 0.0, 0.0, 0.0,
        0.0, 0.0, mul_blue, 0.0, 0.0,
        0.0, 0.0, 0.0, mul_alpha, 0.0,
        add_red, add_green, add_blue, add_alpha, 1.0,
    )


def get_color_matrix_inversion(value=1.0):
    value2 = value * 2 - 1.0
    return get_color_matrix(
        mul_red=-value2,
        mul_green=-value2,
        mul_blue=-value2,
        add_red=value,
        add_green=value,
        add_blue=value,
    )
