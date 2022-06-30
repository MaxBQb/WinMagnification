"""
Type hints

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
import typing

ColorMatrix = typing.Tuple[
    float, float, float, float, float,
    float, float, float, float, float,
    float, float, float, float, float,
    float, float, float, float, float,
    float, float, float, float, float,
]
"""
Red
Green
Blue
Alpha
Translation (affine transformation)

Matrix 5x5 affect color like so:
r*=x   g+=x*r b+=x*r a+=x*r 0
r+=x*g g*=x   b+=x*g a+=x*g 0
r+=x*b g+=x*b b*=x   a+=x*b 0
r+=x*a g+=x*a b+=x*a a*=x   0
r+=x   g+=x   b+=x   a+=x   1

More info: https://docs.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-using-a-color-matrix-to-transform-a-single-color-use
"""

TransformationMatrix = typing.Tuple[
    float, float, float,
    float, float, float,
    float, float, float,
]

FullscreenTransformRaw = typing.Tuple[float, typing.Tuple[int, int]]
RectangleRaw = typing.Tuple[int, int, int, int]
"""
Tuple of ints: (left, top, right, bottom)
"""

InputTransformRaw = typing.Tuple[bool, RectangleRaw, RectangleRaw]
