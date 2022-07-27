"""
| Type hints
Author: MaxBQb |
`Microsoft Docs <https://docs.microsoft.com/en-us/windows/win32/api/_magapi/>`_ |
`Header <https://pastebin.com/Lh82NjjM>`_
"""
import typing


ColorMatrix: 'typing.TypeAlias' = typing.Tuple[
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

TransformationMatrix: 'typing.TypeAlias' = typing.Tuple[
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

.. tip::
   it's not mentioned in `docs <https://docs.microsoft.com/en-us/windows/win32/api/magnification/ns-magnification-magtransform>`_, but I noticed this:

   === === ===
    X   Y   T
   === === ===
    N  0.0 -X
   0.0  N  -Y
   0.0 0.0 1.0
   === === ===

   | **X** Offset from left to right |right|
   | **Y** Offset from up to down |down|
   | Where (0, 0) is |up-left| upper-left corner of magnifier window
"""

SimpleTransform: 'typing.TypeAlias' = typing.Tuple[
    typing.Tuple[float, float],
    typing.Tuple[float, float],
]
"""
| Tuple of (**scale**, **offset**)
| **scale**: (x, y)
| **offset**: (x, y)

.. hint::
   **Offset** starts from |up-left| upper-left corner of magnification window
"""

FullscreenTransform: 'typing.TypeAlias' = typing.Tuple[float, typing.Tuple[int, int]]
"""
| Tuple of **magnification factor** and **offset** for the full-screen magnifier:
| **magnification factor** = 1.0 |=> screen content is not being magnified.
| 1.0 < **magnification factor** <= 4096.0 |=> scale factor for magnification.
| **magnification factor** < 1.0 is **not valid**.
| The **offset** is relative to the |up-left| upper-left corner of the primary monitor, in unmagnified coordinates.
| -262144 <= offset(x, y) <= 262144.
"""

Rectangle: 'typing.TypeAlias' = typing.Tuple[int, int, int, int]
"""
Tuple of ints: (|left| **left**, |up| **top**, |right| **right**, |down| **bottom**)
"""

InputTransform: 'typing.TypeAlias' = typing.Tuple[bool, Rectangle, Rectangle]
"""
| Tuple of **is_enabled**, **source** and **destination**:
- **is_enabled**: True if input translation is enabled.
- **source**: The source rectangle, in unmagnified screen coordinates,
  that defines the area of the screen that is magnified.
- **destination**: The destination rectangle, in screen coordinates,
  that defines the area of the screen where the magnified screen content is displayed.
| Pen and touch input in this rectangle is mapped to the source rectangle.
"""
