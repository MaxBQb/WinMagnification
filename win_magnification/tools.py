"""
Additional tools available for programmer

Author: MaxBQb
"""
import itertools
import math
import typing

from . import types


def get_matrix_side(elements_count: int, dimension_count=2):
    return int(math.pow(elements_count, 1.0/dimension_count))


def pos_for_matrix(array_len: int, *coords: int) -> int:
    row_len = get_matrix_side(array_len, len(coords))
    return sum(
        row_len ** i * pos for (i, pos) in enumerate(reversed(coords), 0)
    )


def print_matrix(matrix: typing.Tuple):
    row_len = get_matrix_side(len(matrix))
    for i in range(row_len):
        print(*(
            str(element).rjust(4, ' ')
            for element in matrix[i*row_len:(1+i)*row_len]
        ))


def get_transform_matrix(x=1.0, y=1.0) -> types.TransformationMatrix:
    return (
        x, 0.0, 0.0,
        0.0, y, 0.0,
        0.0, 0.0, 1.0,
    )


def get_simple_color_matrix(
    mul_red=1.0, mul_green=1.0, mul_blue=1.0, mul_alpha=1.0,
    add_red=0.0, add_green=0.0, add_blue=0.0, add_alpha=0.0,
) -> types.ColorMatrix:
    """
    Creates simple color transformation matrix
    :param mul_red: Red color multiplier
    :param mul_green: Green color multiplier
    :param mul_blue: Blue color multiplier
    :param mul_alpha: Colors transparency multiplier
    :param add_red: Red color addendum
    :param add_green: Green color addendum
    :param add_blue: Blue color addendum
    :param add_alpha: Colors transparency addendum
    :return: Color transformation matrix
    """
    return (
        mul_red, 0.0, 0.0, 0.0, 0.0,
        0.0, mul_green, 0.0, 0.0, 0.0,
        0.0, 0.0, mul_blue, 0.0, 0.0,
        0.0, 0.0, 0.0, mul_alpha, 0.0,
        add_red, add_green, add_blue, add_alpha, 1.0,
    )


def get_transition(start: typing.Tuple, end: typing.Tuple):
    """
    :param start: initial state (transit from)
    :param end: final state (transit to)
    :return: transition function from start to end matrix
    """
    diff = tuple(
        end[i] - start[i] for i in range(len(start))
    )

    def transit(value=1.0):
        """
        :param value: scale of transition
        normally stays between 0 and 1 to get transition effect
        :return: start matrix moved towards end matrix with value scale
        """
        return tuple(
            start[i] + diff[i] * value for i in range(len(start))
        )
    return transit


def combine_matrices(first: typing.Tuple, second: typing.Tuple):
    """
    Multiplies matrices, can be used to combine color transformations
    :param first: matrix A
    :param second: matrix B
    :return: A*B
    """
    if len(first) != len(second):
        raise ValueError("Matrices must be the same size!")
    row_len = get_matrix_side(len(first))
    return tuple(itertools.chain(*([sum(
        a*b for a, b in zip(
            first[i*row_len:(1+i)*row_len],
            second[j::row_len]
        )) for j in range(row_len)
        ] for i in range(row_len)
    )))


def replace(fun):
    def wrapper(_):
        return fun
    return wrapper
