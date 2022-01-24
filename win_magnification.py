"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://searchcode.com/codesearch/view/66549806/
"""
from ctypes import *
from ctypes.wintypes import *

_DLL = WinDLL('magnification.dll')


# C Constants (feel free to use)
WC_MAGNIFIER = "Magnifier"
MS_SHOWMAGNIFIEDCURSOR = 1
MS_CLIPAROUNDCURSOR = 2
MS_INVERTCOLORS = 4
MW_FILTERMODE_INCLUDE = 0
MW_FILTERMODE_EXCLUDE = 1


# C Function structure
_DLL.MagInitialize.restype = BOOL

_DLL.MagUninitialize.restype = BOOL


# Functions
def initialize() -> bool:
    """
    Creates and initializes the magnifier run-time objects.

    :return: True if successful.
    """
    return _DLL.MagInitialize()


def uninitialize() -> bool:
    """
    Destroys the magnifier run-time objects.

    :return: True if successful.
    """
    return _DLL.MagUninitialize()


# Compatability with original function names
MagInitialize = initialize
MagUninitialize = uninitialize
