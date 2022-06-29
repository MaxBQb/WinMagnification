"""
Defaults for transformation and color effects

Author: MaxBQb
"""
from constants import *
from utils import *

# Color matrix
NO_EFFECT: ColorMatrix = get_color_matrix()
COLOR_INVERSION_EFFECT = get_color_matrix_inversion()

# Transformation matrix
NO_TRANSFORM = get_transform_matrix()

# Rect
ZERO_RECT: RectangleRaw = (0,)*4

# Defaults
DEFAULT_COLOR_EFFECT: ColorMatrix = NO_EFFECT
DEFAULT_TRANSFORM: TransformationMatrix = NO_TRANSFORM
DEFAULT_FULLSCREEN_TRANSFORM: FullscreenTransformRaw = (1.0, (0, 0))
DEFAULT_INPUT_TRANSFORM: InputTransformRaw = (False, ZERO_RECT, ZERO_RECT)
DEFAULT_SOURCE: RectangleRaw = ZERO_RECT
DEFAULT_FILTERS_LIST: tuple = tuple()
