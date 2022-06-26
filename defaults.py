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

# Defaults
DEFAULT_COLOR_EFFECT = NO_EFFECT
DEFAULT_TRANSFORM = NO_TRANSFORM
DEFAULT_FULLSCREEN_TRANSFORM: FullscreenTransformRaw = (1.0, (0, 0))
