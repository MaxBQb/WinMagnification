"""
Defaults and constants

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""

from . import tools
from . import types

# C Constants (feel free to use)
WC_MAGNIFIER = "Magnifier"  # Class registered only after initialize() call
# noinspection SpellCheckingInspection
MS_SHOWMAGNIFIEDCURSOR = 1
# noinspection SpellCheckingInspection
MS_CLIPAROUNDCURSOR = 2
# noinspection SpellCheckingInspection
MS_INVERTCOLORS = 4
# noinspection SpellCheckingInspection
MW_FILTERMODE_EXCLUDE = 0
# noinspection SpellCheckingInspection
MW_FILTERMODE_INCLUDE = 1

COLOR_MATRIX_SIZE: int = 5 ** 2
TRANSFORMATION_MATRIX_SIZE: int = 3 ** 2

# Color matrix
COLOR_NO_EFFECT: types.ColorMatrix = (
    1.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)

COLOR_INVERSION_EFFECT: types.ColorMatrix = (
    -1.0, 0.0, 0.0, 0.0, 0.0,
    0.0, -1.0, 0.0, 0.0, 0.0,
    0.0, 0.0, -1.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    1.0, 1.0, 1.0, 0.0, 1.0
)

COLOR_GRAYSCALE_EFFECT: types.ColorMatrix = (
    0.3, 0.3, 0.3, 0.0, 0.0,
    0.6, 0.6, 0.6, 0.0, 0.0,
    0.1, 0.1, 0.1, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)

COLOR_INVERTED_GRAYSCALE_EFFECT: types.ColorMatrix = tools.combine_matrices(
    COLOR_GRAYSCALE_EFFECT,
    COLOR_INVERSION_EFFECT,
)

COLOR_SEPIA_EFFECT: types.ColorMatrix = (
    0.393, 0.349, 0.272, 0.0, 0.0,
    0.769, 0.686, 0.534, 0.0, 0.0,
    0.189, 0.168, 0.131, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)

COLOR_BLIND_DEUTERANOPIA_EFFECT: types.ColorMatrix = (
    0.8, 0.258, 0.0, 0.0, 0.0,
    0.2, 0.742, 0.142, 0.0, 0.0,
    0.0, 0.0, 0.858, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""Color blindness: Deuteranomaly (green-weak)"""

COLOR_BLIND_PROTANOPIA_EFFECT: types.ColorMatrix = (
    0.817, 0.333, 0.0, 0.0, 0.0,
    0.183, 0.667, 0.125, 0.0, 0.0,
    0.0, 0.0, 0.875, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""Color blindness: Protanomaly (red-weak)"""

COLOR_BLIND_TRITANOPIA_EFFECT = (
    0.967, 0.0, 0.0, 0.0, 0.0,
    0.033, 0.733, 0.183, 0.0, 0.0,
    0.0, 0.267, 0.817, 0.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 1.0
)
"""Color blindness: Tritanomaly (blue-yellow weak)"""

# Transformation matrix
NO_TRANSFORM: types.TransformationMatrix = (
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0,
)

# Rect
ZERO_RECT: types.RectangleRaw = (0,) * 4

# Defaults
DEFAULT_COLOR_EFFECT: types.ColorMatrix = COLOR_NO_EFFECT
DEFAULT_TRANSFORM: types.TransformationMatrix = NO_TRANSFORM
DEFAULT_FULLSCREEN_TRANSFORM: types.FullscreenTransformRaw = (1.0, (0, 0))
DEFAULT_INPUT_TRANSFORM: types.InputTransformRaw = (False, ZERO_RECT, ZERO_RECT)
DEFAULT_SOURCE: types.RectangleRaw = ZERO_RECT
DEFAULT_FILTERS_LIST: tuple = tuple()
