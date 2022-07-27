"""
| Default values and constants
Author: MaxBQb |
`Microsoft Docs <https://docs.microsoft.com/en-us/windows/win32/api/_magapi/>`_ |
`Header <https://pastebin.com/Lh82NjjM>`_
"""
from win_magnification import tools
from win_magnification import types

# C Constants (feel free to use)
WC_MAGNIFIER = "Magnifier"
"""
Window Class of Magnifier

.. warning::
   Class registered only after :func:`.initialize` call
"""
# noinspection SpellCheckingInspection
MS_SHOWMAGNIFIEDCURSOR = 1
"""
`Magnifier Window Style <https://docs.microsoft.com/en-us/windows/win32/winauto/magapi/magapi-magnifier-styles>`_:
Displays the magnified system cursor along with the magnified screen content.
"""
# noinspection SpellCheckingInspection
MS_CLIPAROUNDCURSOR = 2
"""
`Magnifier Window Style <https://docs.microsoft.com/en-us/windows/win32/winauto/magapi/magapi-magnifier-styles>`_:
Clips the area of the magnifier window that surrounds the system cursor.
This style enables the user to see screen content that is behind the magnifier window.
"""
# noinspection SpellCheckingInspection
MS_INVERTCOLORS = 4
"""
`Magnifier Window Style <https://docs.microsoft.com/en-us/windows/win32/winauto/magapi/magapi-magnifier-styles>`_:
Displays the magnified screen content using inverted colors.
"""
# noinspection SpellCheckingInspection
MW_FILTERMODE_EXCLUDE = 0
"""
Exclude the windows from magnification.

:meta private:
"""

# noinspection SpellCheckingInspection
MW_FILTERMODE_INCLUDE = 1
"""
Magnify the windows.

.. attention::
   This value is not supported on Windows 7 or newer.

:meta private:
"""

COLOR_MATRIX_SIZE: int = 5 ** 2
TRANSFORMATION_MATRIX_SIZE: int = 3 ** 2

# Color matrix
COLOR_NO_EFFECT = (
    1.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""
Color transformation matrix which does nothing with colors

===  ===  ===  ===  ===
1.0  0.0  0.0  0.0  0.0
0.0  1.0  0.0  0.0  0.0
0.0  0.0  1.0  0.0  0.0
0.0  0.0  0.0  1.0  0.0
0.0  0.0  0.0  0.0  1.0
===  ===  ===  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_INVERSION_EFFECT = (
    -1.0, 0.0, 0.0, 0.0, 0.0,
    0.0, -1.0, 0.0, 0.0, 0.0,
    0.0, 0.0, -1.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    1.0, 1.0, 1.0, 0.0, 1.0
)
"""
| Color transformation matrix which inverts colors 
| Black -> White
| White -> Black
| And so on...

==== ==== ====  ===  ===
-1.0  0.0  0.0  0.0  0.0
 0.0 -1.0  0.0  0.0  0.0
 0.0  0.0 -1.0  0.0  0.0
 0.0  0.0  0.0  1.0  0.0
 1.0  1.0  1.0  0.0  1.0
==== ==== ====  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_GRAYSCALE_EFFECT = (
    0.3, 0.3, 0.3, 0.0, 0.0,
    0.6, 0.6, 0.6, 0.0, 0.0,
    0.1, 0.1, 0.1, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""
Color transformation matrix which convert colors into shades of gray

===  ===  ===  ===  ===
0.3  0.3  0.3  0.0  0.0
0.6  0.6  0.6  0.0  0.0
0.1  0.1  0.1  0.0  0.0
0.0  0.0  0.0  1.0  0.0
0.0  0.0  0.0  0.0  1.0
===  ===  ===  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_INVERTED_GRAYSCALE_EFFECT = tools.combine_matrices(
    COLOR_GRAYSCALE_EFFECT,
    COLOR_INVERSION_EFFECT,
)
"""
Color transformation matrix which convert inverted colors into shades of gray

==== ==== ====  ===  ===
-0.3 -0.3 -0.3  0.0  0.0
-0.6 -0.6 -0.6  0.0  0.0
-0.1 -0.1 -0.1  0.0  0.0
 0.0  0.0  0.0  1.0  0.0
 1.0  1.0  1.0  0.0  1.0
==== ==== ====  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_SEPIA_EFFECT = (
    0.393, 0.349, 0.272, 0.0, 0.0,
    0.769, 0.686, 0.534, 0.0, 0.0,
    0.189, 0.168, 0.131, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""
Color transformation matrix which convert colors into shades of brown

=====  =====  =====  ===  ===
0.393  0.349  0.272  0.0  0.0
0.769  0.686  0.534  0.0  0.0
0.189  0.168  0.131  0.0  0.0
0.0    0.0    0.0    1.0  0.0
0.0    0.0    0.0    0.0  1.0
=====  =====  =====  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_BLIND_DEUTERANOPIA_EFFECT = (
    0.8, 0.258, 0.0, 0.0, 0.0,
    0.2, 0.742, 0.142, 0.0, 0.0,
    0.0, 0.0, 0.858, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""
Color blindness: Deuteranomaly (green-weak)

===  =====  =====  ===  ===
0.8  0.258  0.0    0.0  0.0
0.2  0.742  0.142  0.0  0.0
0.0  0.0    0.858  0.0  0.0
0.0  0.0    0.0    1.0  0.0
0.0  0.0    0.0    0.0  1.0
===  =====  =====  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_BLIND_PROTANOPIA_EFFECT = (
    0.817, 0.333, 0.0, 0.0, 0.0,
    0.183, 0.667, 0.125, 0.0, 0.0,
    0.0, 0.0, 0.875, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""
Color blindness: Protanomaly (red-weak)

=====  =====  =====  ===  ===
0.817  0.333  0.0    0.0  0.0
0.183  0.667  0.125  0.0  0.0
0.0    0.0    0.875  0.0  0.0
0.0    0.0    0.0    1.0  0.0
0.0    0.0    0.0    0.0  1.0
=====  =====  =====  ===  ===

:type: :data:`.ColorMatrix`
"""

COLOR_BLIND_TRITANOPIA_EFFECT = (
    0.967, 0.0, 0.0, 0.0, 0.0,
    0.033, 0.733, 0.183, 0.0, 0.0,
    0.0, 0.267, 0.817, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""
Color blindness: Tritanomaly (blue-yellow weak)

=====  =====  =====  ===  ===
0.967  0.0    0.0    0.0  0.0
0.033  0.733  0.183  0.0  0.0
0.0    0.267  0.817  0.0  0.0
0.0    0.0    0.0    1.0  0.0
0.0    0.0    0.0    0.0  1.0
=====  =====  =====  ===  ===

:type: :data:`.ColorMatrix`
"""

# Rect
ZERO_RECT = (0,) * 4
"""
Rectangle of zeros

:type: :data:`.RectangleRaw`
"""

# Defaults
DEFAULT_COLOR_EFFECT = COLOR_NO_EFFECT
"""
Default color transformation matrix which does nothing with colors

===  ===  ===  ===  ===
1.0  0.0  0.0  0.0  0.0
0.0  1.0  0.0  0.0  0.0
0.0  0.0  1.0  0.0  0.0
0.0  0.0  0.0  1.0  0.0
0.0  0.0  0.0  0.0  1.0
===  ===  ===  ===  ===

:type: :data:`.ColorMatrix`
"""
DEFAULT_TRANSFORM = (
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0,
)
"""
Default transformation matrix which does nothing with magnification factor

===  ===  ===
1.0  0.0  0.0
0.0  1.0  0.0
0.0  0.0  1.0
===  ===  ===

:type: :data:`.TransformationMatrix`
"""

DEFAULT_TRANSFORM_EXTRACTION_PATTERN = tuple(tools.get_extraction_pattern(
    TRANSFORMATION_MATRIX_SIZE,
    (0, 0),
    (1, 1),
    (0, 2),
    (1, 2)
))
"""
Default transformation matrix extraction pattern
Allows to extract (scale_x, scale_y, offset_x, offset_y)
"""

_DEFAULT_TRANSFORM_PAIR = tools.extract_from_matrix(
    DEFAULT_TRANSFORM,
    *DEFAULT_TRANSFORM_EXTRACTION_PATTERN,
)
DEFAULT_TRANSFORM_PAIR: types.SimpleTransform \
    = _DEFAULT_TRANSFORM_PAIR[:2], _DEFAULT_TRANSFORM_PAIR[2:]
"""
Default transformation which does nothing with magnification factor
tuple of (scale, offset)

:type: :data:`.SimpleTransformation`
"""
del _DEFAULT_TRANSFORM_PAIR

DEFAULT_FULLSCREEN_TRANSFORM = (1.0, (0, 0))
"""
Default fullscreen transformation which does nothing with magnification factor

:type: :data:`.FullscreenTransformRaw`
"""
DEFAULT_INPUT_TRANSFORM = (False, ZERO_RECT, ZERO_RECT)
"""
Default input transformation which does nothing with magnification factor

:type: :data:`.InputTransformRaw`
"""
DEFAULT_SOURCE = ZERO_RECT
"""
Default rectangle of zeros

:type: :data:`.RectangleRaw`
"""

DEFAULT_FILTERS_LIST: tuple = tuple()
"""
Default empty list of filters for magnifier to **exclude**/include 
"""