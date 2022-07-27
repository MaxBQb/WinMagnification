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
    return int(math.pow(elements_count, 1.0 / dimension_count))


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


def extract_from_matrix(matrix: Matrix.Linear, *linear_positions: int):
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


def matrix_to_str(matrix: Matrix.Linear):
    """
    | Converts matrix to pretty string format
    | Example:
    >>> matrix_to_str((2.0,))
    '2.0'
    >>> print(matrix_to_str((1.0,2.0,-3.9,4.0)))
     1.0  2.0
    -3.9  4.0

    :param matrix: Array which sqrt(size) is natural number
    """
    row_len = get_matrix_side(len(matrix))
    matrix = tuple(str(round(element, 4)) for element in matrix)
    negative_column = [False] * row_len
    column_width = [1] * row_len

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


def print_matrix(matrix: Matrix.Linear):
    """
    | Prints matrix in pretty format
    | Example:
    >>> print_matrix((2.0,))
    2.0
    >>> print_matrix((1.0,2.0,-3.9,4.0))
     1.0  2.0
    -3.9  4.0

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
    :param offset_x: Horizontal |right| offset from |up-left| left upper corner of window
    :param offset_y: Vertical |down| offset from |up-left| left upper corner of window
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


def get_filled_matrix(value=0.0, size=0) -> Matrix.Linear:
    return (value,) * size


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


Transition: 'typing.TypeAlias' = typing.Callable[[typing.Union[float, int]], 'Matrix.Linear']
"""
Function with predefined transition matrix
makes predefined start moved towards predefined end, 
with scale of value, which normally stays between 0 (start) and 1 (end)
to get transition effect
"""


def get_transition(start: Matrix.Linear, end: Matrix.Linear) -> 'Transition':
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
    (0.0, 0.0, 0.0)
    >>> move(1)
    (10.0, 10.0, 10.0)
    >>> move(0.4)
    (4.0, 4.0, 4.0)
    >>> move(-0.4)
    (-4.0, -4.0, -4.0)
    >>> move(-1.4)
    (-14.0, -14.0, -14.0)

    :param start: :abbr:`Initial state (transit from)`
    :param end: :abbr:`Final state (transit to)`
    :return: Transition function from **start** to **end** matrix
    """
    diff = tuple(
        end[i] - start[i] for i in range(len(start))
    )

    def transit(value: typing.Union[float, int] = 1.0) -> Matrix.Linear:
        """
        Make tuple start moved towards tuple end
        with scale of value

        :param value: Float scale of transition
            normally stays between :abbr:`0 (start)` and :abbr:`1 (end)` to get transition effect
        :return: Start matrix moved towards end matrix with value scale
        """
        value = float(value)
        return tuple(
            start[i] + diff[i] * value for i in range(len(start))
        )

    return transit


def combine_matrices(first: Matrix.Linear, second: Matrix.Linear):
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
    :raises ValueError: On matrices sizes mismatch
    """
    if len(first) != len(second):
        raise ValueError("Matrices must be the same size!")
    row_len = get_matrix_side(len(first))
    return tuple(itertools.chain(*([sum(
        a * b for a, b in zip(
            first[i * row_len:(1 + i) * row_len],
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


class Matrix:
    """
    :abbr:`Matrix (from linear algebra)` wrapper

    .. automethod:: __str__
    .. automethod:: __matmul__
    .. automethod:: __mul__
    .. automethod:: __add__
    .. automethod:: __sub__
    .. automethod:: __neg__

    """

    Linear: 'typing.TypeAlias' = typing.Tuple[float, ...]
    """
    :abbr:`Matrix (linear algebra term)` represented as flat tuple of floats
    """

    Square: 'typing.TypeAlias' = typing.Tuple[typing.Tuple[float, ...], ...]
    """
    :abbr:`Matrix (linear algebra term)` represented as tuple of tuples of floats
    """

    LinearLike: 'typing.TypeAlias' = typing.Collection[typing.Union[float, int]]
    """
    :abbr:`Matrix (linear algebra term)` represented as collection of numbers
    """

    SquareLike: 'typing.TypeAlias' = typing.Collection[typing.Collection[typing.Union[float, int]]]
    """
    :abbr:`Matrix (linear algebra term)` represented as collection of collections of numbers
    """

    Any: 'typing.TypeAlias' = typing.Union[
        LinearLike,
        SquareLike,
        'Matrix',
    ]
    """
    Any :abbr:`matrix (linear algebra term)`: :attr:`SquareLike`, :attr:`LinearLike` or :class:`Matrix` itself 
    """

    _ACCURACY = 8+1
    '''All elements round precision'''

    def __init__(self):
        self._value: 'Matrix.Linear' = tuple()
        self._size = 0
        self._side_size = 0

    def _resize(self, value: int):
        self._size = value
        side = get_matrix_side(self._size)
        self._side_size = side
        side **= 2
        if side != value:
            raise ValueError("Matrix size must have natural square root!\n"
                             f"Expect at least {side}, got {value}")
        self._value = get_filled_matrix()

    @property
    def linear(self) -> Linear:
        """
        | Get/set linear matrix from/to raw value
        | Example:

        >>> matrix = Matrix.from_linear((1,2,3,4))
        >>> matrix.linear = [4, 5, 6.9, 7]
        >>> matrix.linear
        (4.0, 5.0, 6.9, 7.0)
        >>> matrix.linear = [0]*5
        Traceback (most recent call last):
        ...
        ValueError: Linear matrix size mismatch
        Expected 4, got 5

        | |Accessors: Get Set|

        :raises ValueError: On size of new linear matrix musmatch the old one
        """
        return self._value

    @linear.setter
    def linear(self, value: LinearLike) -> None:
        if len(value) != self._size:
            raise ValueError(f"Linear matrix size mismatch\n"
                             f"Expected {self._size}, got {len(value)}")
        accuracy = self._ACCURACY
        self._value = tuple(
            round(float(element), accuracy) for element in value
        )

    @property
    def square(self) -> Square:
        """
        | Get/set :abbr:`square matrix (array of arrays)` from/to raw value
        | Example:

        >>> matrix = Matrix.from_linear((1,2,3,4))
        >>> matrix.square = [
        ...     [4, 5],
        ...     [6.9, 7]
        ... ]
        >>> matrix.linear
        (4.0, 5.0, 6.9, 7.0)
        >>> matrix.square
        ((4.0, 5.0), (6.9, 7.0))
        >>> matrix.square = [0]*4
        Traceback (most recent call last):
        ...
        TypeError: 'int' object is not iterable

        | |Accessors: Get Set|
        """
        value = self._value
        size = self._side_size
        return tuple(
            value[i * size:(i + 1) * size] for i in range(size)
        )

    @square.setter
    def square(self, value: SquareLike):
        self.linear = tuple(itertools.chain(*value))

    def __str__(self):
        """
        | Converts matrix to string
        | Example:

        >>> print(Matrix.from_linear((1.0,2.0,3.0,4.0)))
        1.0  2.0
        3.0  4.0
        """
        return matrix_to_str(self._value)

    def __matmul__(self, other: typing.Union[Any, int, float]):
        """
        | Multipies matrices
        | Example:

        >>> print(Matrix.from_linear((1,2,3,4)) * Matrix.from_linear((5,6,7,8)))
        19.0  22.0
        43.0  50.0
        >>> Matrix.from_linear((1.0,2.0,3.0,4.0)) @ "hello world"
        Traceback (most recent call last):
        ...
        TypeError: Can't multiply matrix and 'str'

        :raises TypeError: When unable to convert operand
        """
        matrix = self.from_any(other)
        if matrix is None:
            raise TypeError(f"Can't multiply matrix and {type(other).__name__!r}")
        return Matrix.from_linear(combine_matrices(self.linear, matrix.linear))

    def __mul__(self, other: typing.Union[Any, int, float]):
        """
        | Multiply matrix and number/:meth:`matrix <__matmul__>`
        | Example:

        >>> print(Matrix.from_linear((1.0,2.0,3.0,4.0)) * 1)
        1.0  2.0
        3.0  4.0
        >>> test_matrix = Matrix.from_linear((1.0,2.0,3.0,4.0))
        >>> test_matrix *= -2
        >>> print(test_matrix)
        -2.0 -4.0
        -6.0 -8.0
        >>> print(-Matrix.from_linear((1.0,2.0,3.0,4.0)) * 2)
        -2.0 -4.0
        -6.0 -8.0
        >>> print(Matrix.from_linear((1.0,2.0,3.0,4.0)) * Matrix.from_linear((5.0,6.0,7.0,8.0)))
        19.0  22.0
        43.0  50.0
        """
        if isinstance(other, (int, float)):
            origin_matrix = self._value
            return Matrix.from_linear(tuple(
                element * other for element in origin_matrix
            ))
        return self @ other

    def __add__(self, other: typing.Union[Any, int, float]):
        """
        | Add matrix/number to matrix
        | Example:

        >>> print(Matrix.from_linear((1.0,2.0,3.0,4.0)) + Matrix.from_linear((4.1,3.2,2.3,1.4)))
        5.1  5.2
        5.3  5.4
        >>> print(Matrix.from_linear((1.0,2.0,3.0,4.0)) + 4)
        5.0  6.0
        7.0  8.0
        >>> Matrix.from_linear((1.0,2.0,3.0,4.0)) + "hello world"
        Traceback (most recent call last):
        ...
        TypeError: Can't add 'str' to matrix

        :raises TypeError: When unable to convert operand
        """
        if isinstance(other, (int, float)):
            other = get_filled_matrix(float(other), self._size)
        matrix = self.from_any(other)
        if matrix is None:
            raise TypeError(f"Can't add {type(other).__name__!r} to matrix")
        matrix_a, matrix_b = self.linear, matrix.linear
        return Matrix.from_linear(tuple(
            matrix_a[i] + matrix_b[i] for i in range(len(matrix_b))
        ))

    def __sub__(self, other: typing.Union[Any, int, float]):
        """
        | Subtract matrix/number from matrix
        | Example:

        >>> print(Matrix.from_linear((1.1,2.2,3.3,4.4)) - Matrix.from_linear((1.0,2.0,3.0,4.0)))
        0.1  0.2
        0.3  0.4
        >>> print(Matrix.from_linear((1.0,2.0,3.0,4.0)) - 1)
        0.0  1.0
        2.0  3.0
        >>> Matrix.from_linear((1.0,2.0,3.0,4.0)) - "hello world"
        Traceback (most recent call last):
        ...
        TypeError: Can't subtract 'str' from matrix

        :raises TypeError: When unable to convert operand
        """
        if isinstance(other, (int, float)):
            other = get_filled_matrix(float(other), self._size)
        matrix = self.from_any(other)
        if matrix is None:
            raise TypeError(f"Can't subtract {type(other).__name__!r} from matrix")
        matrix_a, matrix_b = self.linear, matrix.linear
        return Matrix.from_linear(tuple(
            matrix_a[i] - matrix_b[i] for i in range(len(matrix_b))
        ))

    def __neg__(self):
        """
        | :meth:`Multiply <__mul__>` matrix with -1
        | Example:

        >>> print(-Matrix.from_linear((1.0,2.0,3.0,4.0)))
        -1.0 -2.0
        -3.0 -4.0
        """
        return self * -1

    @classmethod
    def from_any(cls, value: Any) -> typing.Optional[Matrix]:
        """
        | Convert :abbr:`Linear (flat tuple)`/:abbr:`Square (tuple of tuples)` matrix
          to :class:`Matrix`
        | Example:

        >>> Matrix.from_any((1,2,3.5))

        >>> print(Matrix.from_any((1,2,3.5,4)))
        1.0  2.0
        3.5  4.0
        >>> Matrix.from_any(((1,2),(3,)))

        >>> print(Matrix.from_any(((1,2),(3,4))))
        1.0  2.0
        3.0  4.0
        >>> print(Matrix.from_any(Matrix.from_any(((1,2),(3,4)))))
        1.0  2.0
        3.0  4.0

        :param value: Source of raw data
        :type value: :attr:`Matrix.Any`
        :return: Filled matrix, or None on conversion fails
        """
        if isinstance(value, Matrix):
            return value
        matrix = cls.from_square(value)
        if matrix is None:
            matrix = cls.from_linear(value)
        return matrix

    @classmethod
    def from_linear(cls, value: LinearLike) -> typing.Optional[Matrix]:
        """
        | Convert :abbr:`Linear (flat tuple)` matrix to :class:`Matrix`
        | Example:

        >>> print(Matrix.from_linear((1,2,3.5,4)))
        1.0  2.0
        3.5  4.0
        >>> Matrix.from_linear(((1,2),(3,4)))

        >>> Matrix.from_linear((1, 2))


        :param value: Source of raw data
        :return: Filled matrix, or None on conversion fails
        """

        try:
            size = len(value)
            matrix = cls()
            matrix._resize(size)
            matrix.linear = value
        except (TypeError, ValueError):
            return None
        return matrix

    @classmethod
    def from_square(cls, value: SquareLike) -> typing.Optional[Matrix]:
        """
        | Convert :abbr:`Square (tuple of tuples)` matrix
          to :class:`Matrix`
        | Example:

        >>> print(Matrix.from_square(((1,2),(3,4))))
        1.0  2.0
        3.0  4.0

        >>> Matrix.from_square(((1,2),(3,)))


        :param value: Source of raw data
        :return: Filled matrix, or None on conversion fails
        """

        try:
            size = len(value)
            matrix = cls()
            matrix._resize(size ** 2)
            matrix.square = value
        except (TypeError, ValueError):
            return None
        return matrix
