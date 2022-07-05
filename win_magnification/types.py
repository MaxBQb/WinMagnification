"""
| Type hints
Author: MaxBQb |
`Microsoft Docs <https://docs.microsoft.com/en-us/windows/win32/api/_magapi/>`_ |
`Header <https://pastebin.com/Lh82NjjM>`_
"""
import typing

ColorMatrix: typing.TypeAlias = typing.Tuple[
    float, float, float, float, float,
    float, float, float, float, float,
    float, float, float, float, float,
    float, float, float, float, float,
    float, float, float, float, float,
]
"""
| Matrix 5x5 affect color like so:

======== ======== ======== ======== =
Red      Green    Blue     Alpha    T
======== ======== ======== ======== =
r *= x   g += x*r b += x*r a += x*r 0
r += x*g g *= x   b += x*g a += x*g 0
r += x*b g += x*b b *= x   a += x*b 0
r += x*a g += x*a b += x*a a *= x   0
r += x   g += x   b += x   a += x   1
======== ======== ======== ======== =

| **T** is Affine transformation
| `Read more <https://docs.microsoft.com/en-us/windows/win32/gdiplus/-gdiplus-using-a-color-matrix-to-transform-a-single-color-use>`_
"""

TransformationMatrix: typing.TypeAlias = typing.Tuple[
    float, float, float,
    float, float, float,
    float, float, float,
]
"""
| Describes a transformation matrix that a magnifier control uses to magnify screen content.
| The transformation matrix is

=== === ===
 X   Y   T
=== === ===
 N  0.0 0.0
0.0  N  0.0
0.0 0.0 1.0
=== === ===

| **T** is Affine transformation
| **N** is the magnification factor.
"""

FullscreenTransformRaw: typing.TypeAlias = typing.Tuple[float, typing.Tuple[int, int]]
"""
| Tuple of **magnification factor** and **offset** for the full-screen magnifier:
| **magnification factor** = 1.0 |=> screen content is not being magnified.
| 1.0 < **magnification factor** <= 4096.0 |=> scale factor for magnification.
| **magnification factor** < 1.0 is **not valid**.
| The **offset** is relative to the upper-left corner of the primary monitor, in unmagnified coordinates.
| -262144 <= offset(x, y) <= 262144.
"""

RectangleRaw: typing.TypeAlias = typing.Tuple[int, int, int, int]
"""
Tuple of ints: (**left**, **top**, **right**, **bottom**)
"""

InputTransformRaw: typing.TypeAlias = typing.Tuple[bool, RectangleRaw, RectangleRaw]
"""
| Tuple of **is_enabled**, **source** and **destination**:
- **is_enabled**: True if input translation is enabled.
- **source**: The source rectangle, in unmagnified screen coordinates,
  that defines the area of the screen that is magnified.
- **destination**: The destination rectangle, in screen coordinates,
  that defines the area of the screen where the magnified screen content is displayed.
| Pen and touch input in this rectangle is mapped to the source rectangle.
"""
