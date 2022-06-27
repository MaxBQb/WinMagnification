"""
Constants and type hints

Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""


# C Constants (feel free to use)
WC_MAGNIFIER = "Magnifier"  # Class registered only after initialize() call
MS_SHOWMAGNIFIEDCURSOR = 1
MS_CLIPAROUNDCURSOR = 2
MS_INVERTCOLORS = 4
MW_FILTERMODE_EXCLUDE = 0
MW_FILTERMODE_INCLUDE = 1


# Type hints
ColorMatrix = tuple[
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
ColorMatrixSize: int = 5**2

TransformationMatrix = tuple[
    float, float, float,
    float, float, float,
    float, float, float,
]
TransformationMatrixSize: int = 3**2


FullscreenTransformRaw = tuple[float, tuple[int, int]]
Rectangle = tuple[int, int, int, int]
"""
Tuple of ints: (left, top, right, bottom)
"""
