"""
Constants and type hints

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""


# C Constants (feel free to use)
WC_MAGNIFIER = "Magnifier"
MS_SHOWMAGNIFIEDCURSOR = 1
MS_CLIPAROUNDCURSOR = 2
MS_INVERTCOLORS = 4
MW_FILTERMODE_INCLUDE = 0
MW_FILTERMODE_EXCLUDE = 1


# Type hints
ColorMatrix = list[
    list[float, float, float, float, float],
    list[float, float, float, float, float],
    list[float, float, float, float, float],
    list[float, float, float, float, float],
    list[float, float, float, float, float],
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


# Color matrix
IDENTITY_MATRIX: ColorMatrix = [
     [1, 0, 0, 0, 0],
     [0, 1, 0, 0, 0],
     [0, 0, 1, 0, 0],
     [0, 0, 0, 1, 0],
     [0, 0, 0, 0, 1],
]
NO_EFFECT = IDENTITY_MATRIX

COLOR_INVERSION_EFFECT: ColorMatrix = [
     [-1, 0, 0, 0, 0],
     [0, -1, 0, 0, 0],
     [0, 0, -1, 0, 0],
     [0, 0, 0, 1, 0],
     [1, 1, 1, 0, 1],
]


# Defaults
DEFAULT_COLOR_EFFECT = NO_EFFECT
DEFAULT_FULLSCREEN_TRANSFORM = (1.0, (0, 0))
