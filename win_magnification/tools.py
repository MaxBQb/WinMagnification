"""
| Additional tools available for programmer
| Author: MaxBQb
"""
from __future__ import annotations

import functools
import itertools
import math
import typing

from win_magnification import types


def get_matrix_side(elements_count: int, dimension_count=2):
    """
    | Gets size of square matrix side
    | Example: linear matrix 9x9:
    | **elements_count** = 81
    | **dimension_count** = 2

    :param elements_count: Total count of elements in matrix
    :param dimension_count: Array = 1, matrix = 2, cube = 3, etc.
    :return: Matrix rows/columns count
    """
    return int(math.pow(elements_count, 1.0/dimension_count))


def pos_for_matrix(array_len: int, *coords: int) -> int:
    """
    | Get index of element in linear structure,
      defined by it's coordinates.
    | Example:
    >>> array = (
    ...   0, 0, 0,
    ...   0, 1, 2,
    ...   0, 0, 0,
    ... )
    >>> array[pos_for_matrix(len(array), 1, 2)]
    2

    :param array_len: Size fo linear structure
    :param coords: Element coordinates
    :return: Index in array
    """
    row_len = get_matrix_side(array_len, len(coords))
    return sum(
        row_len ** i * pos for (i, pos) in enumerate(reversed(coords), 0)
    )


def get_extraction_pattern(matrix_size: int, *positions: typing.Iterable[int]):
    """
    | Generates sequence of linear positions from matrix coords
    | Example:

    >>> list(get_extraction_pattern(9, (1, 1), (2, 2), (1, 2)))
    [4, 8, 5]

    :param matrix_size: Amount of elements in matrix
    :param positions: Sequence of coords
    :return: Sequence of linear coords
    """
    return (
        pos_for_matrix(matrix_size, *position) for position in positions
    )


def extract_from_matrix(matrix: tuple, *linear_positions: int):
    """
    | Get values from **matrix** at **positions** specified
    | Example:

    >>> array = (
    ...   0, 0, 0,
    ...   0, 1, 2,
    ...   0, 3, 0,
    ... )
    >>> pattern = get_extraction_pattern(len(array), (2, 1), (1, 1), (1, 2))
    >>> extract_from_matrix(array, *pattern)
    (3, 1, 2)

    :param matrix: Linear matrix
    :param linear_positions: Indexes in **matrix**
    :return: Values from **positions** specified
    """
    return tuple(
        matrix[position] for position in linear_positions
    )


def matrix_to_str(matrix: tuple):
    """
    | Converts matrix to pretty string format
    | Example:
    >>> matrix_to_str((2,))
    '2'
    >>> print(matrix_to_str((1,2,-3.9,4)))
     1    2
    -3.9  4

    :param matrix: Array which sqrt(size) is natural number
    """
    row_len = get_matrix_side(len(matrix))
    matrix = tuple(map(str, matrix))
    negative_column = [False]*row_len
    column_width = [1]*row_len

    for i in range(row_len):
        for j, element in enumerate(matrix[i * row_len:(1 + i) * row_len]):
            if element.startswith('-'):
                negative_column[j] = True

            if len(element) > column_width[j]:
                column_width[j] = len(element)

    for i in range(row_len):
        # Exclude '-' from width calculation
        if negative_column[i]:
            column_width[i] -= 1

    return '\n'.join(
        (' '.join((
            (' ' if not (j == 0 and not negative_column[j]) and not element.startswith('-')
             else '') + element.ljust(column_width[j], ' ')
            for j, element in enumerate(matrix[i * row_len:(1 + i) * row_len])
        ))).rstrip() for i in range(row_len)
    )


def print_matrix(matrix: tuple):
    """
    | Prints matrix in pretty format
    | Example:
    >>> print_matrix((2,))
    2
    >>> print_matrix((1,2,-3.9,4))
     1    2
    -3.9  4

    :param matrix: Array which sqrt(size) is natural number
    """
    print(matrix_to_str(matrix))


def get_transform_matrix(x=1.0, y=1.0, offset_x=0.0, offset_y=0.0) -> types.TransformationMatrix:
    """
    | Creates screen transformation matrix
    | Example:
    >>> print_matrix(get_transform_matrix(2.0, 8.0))
    2.0  0.0  0.0
    0.0  8.0  0.0
    0.0  0.0  1.0
    >>> print_matrix(get_transform_matrix(3.0, 4.0, 5.0, 6.0))
    3.0  0.0 -5.0
    0.0  4.0 -6.0
    0.0  0.0  1.0

    :param x: Horizontal magnification
    :param y: Vertical magnification
    :param offset_x: Horizontal |right| offset from |upleft| left upper corner of window
    :param offset_y: Vertical |down| offset from |upleft| left upper corner of window
    :return: Screen transformation matrix
    """
    if offset_y != 0.0:
        offset_y = -offset_y
    if offset_x != 0.0:
        offset_x = -offset_x
    return (
        x,   0.0, offset_x,
        0.0, y,   offset_y,
        0.0, 0.0, 1.0,
    )


def get_simple_color_matrix(
    mul_red=1.0, mul_green=1.0, mul_blue=1.0, mul_alpha=1.0,
    add_red=0.0, add_green=0.0, add_blue=0.0, add_alpha=0.0,
) -> types.ColorMatrix:
    """
    | Creates simple color transformation matrix
    | Example:
    >>> print_matrix(get_simple_color_matrix(
    ...     1.1, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0
    ... ))
    1.1  0.0  0.0  0.0  0.0
    0.0  2.0  0.0  0.0  0.0
    0.0  0.0  3.0  0.0  0.0
    0.0  0.0  0.0  4.0  0.0
    5.0  6.0  7.0  8.0  1.0

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
        mul_red, 0.0,       0.0,      0.0,       0.0,
        0.0,     mul_green, 0.0,      0.0,       0.0,
        0.0,     0.0,       mul_blue, 0.0,       0.0,
        0.0,     0.0,       0.0,      mul_alpha, 0.0,
        add_red, add_green, add_blue, add_alpha, 1.0,
    )


def get_transition(start: typing.Tuple, end: typing.Tuple):
    """
    | Make function which returns **start** moved towards **end**
    | with scale of **value** (param of that function):
    | **value** = 0 |=> **start**
    | **value** = 1 |=> **end**
    | 0 <= **value** <= 1 |=> **start** moved towards **end**
    | **value** > 1 |=> **start** moved towards **end** out of **end** bound
    | **value** < 0 |=> **end** moved towards **start** out of **start** bound
    | Example:
    >>> move = get_transition((0, 0, 0), (10, 10, 10))
    >>> move(0)
    (0, 0, 0)
    >>> move(1)
    (10, 10, 10)
    >>> move(0.4)
    (4.0, 4.0, 4.0)
    >>> move(-0.4)
    (-4.0, -4.0, -4.0)
    >>> move(-1.4)
    (-14.0, -14.0, -14.0)

    :param start: Initial state (transit from)
    :param end: Final state (transit to)
    :return: Transition function from **start** to **end** matrix
    """
    diff = tuple(
        end[i] - start[i] for i in range(len(start))
    )

    def transit(value=1.0):
        """
        Make tuple start moved towards tuple end
        with scale of value

        :param value: Float scale of transition
        normally stays between 0 (start) and 1 (end) to get transition effect
        :return: Start matrix moved towards end matrix with value scale
        """
        return tuple(
            start[i] + diff[i] * value for i in range(len(start))
        )
    return transit


def combine_matrices(first: typing.Tuple, second: typing.Tuple):
    """
    | Multiplies matrices, can be used to combine color transformations
    | Example:
    >>> A = (1, 2, 3, 4)
    >>> B = (5, 6, 7, 8)
    >>> combine_matrices(A, B)
    (19, 22, 43, 50)
    >>> combine_matrices(A, (1,))
    Traceback (most recent call last):
    ...
    ValueError: Matrices must be the same size!

    :param first: Matrix A
    :param second: Matrix B
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


def replace(func: typing.Callable) -> typing.Callable:
    """
    | Decorator, replaces one function with another (**func**)
    | Example:
    >>> def call():
    ...     print("call")
    ...
    >>> @replace(call)
    ... def talk():
    ...     '''talk docs'''
    ...     print("talk")
    >>> talk()
    call
    >>> talk.__doc__
    'talk docs'

    :param func: Function which will replace any other
    :return: Wrapper, that acts like **func**
    """
    def wrapper(inner_func: typing.Callable) -> typing.Callable:
        return functools.wraps(inner_func)(func)
    return wrapper
