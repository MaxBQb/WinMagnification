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
NO_EFFECT: types.ColorMatrix = tools.get_color_matrix()
COLOR_INVERSION_EFFECT = tools.get_color_matrix_inversion()

# Transformation matrix
NO_TRANSFORM = tools.get_transform_matrix()

# Rect
ZERO_RECT: types.RectangleRaw = (0,) * 4

# Defaults
DEFAULT_COLOR_EFFECT: types.ColorMatrix = NO_EFFECT
DEFAULT_TRANSFORM: types.TransformationMatrix = NO_TRANSFORM
DEFAULT_FULLSCREEN_TRANSFORM: types.FullscreenTransformRaw = (1.0, (0, 0))
DEFAULT_INPUT_TRANSFORM: types.InputTransformRaw = (False, ZERO_RECT, ZERO_RECT)
DEFAULT_SOURCE: types.RectangleRaw = ZERO_RECT
DEFAULT_FILTERS_LIST: tuple = tuple()
