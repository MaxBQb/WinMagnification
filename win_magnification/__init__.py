"""
| WinMagnification Package: Python wrapper for Magnification API
Author: MaxBQb |
`Microsoft Docs <https://docs.microsoft.com/en-us/windows/win32/api/_magapi/>`_ |
`Header <https://pastebin.com/Lh82NjjM>`_
"""
from win_magnification._objects import WinMagnificationAPI
from win_magnification._functional_wrapper import *
from win_magnification._wrapper import (
    get_fullscreen_color_effect, set_fullscreen_color_effect,
    set_fullscreen_transform, get_fullscreen_transform,
    get_color_effect, set_color_effect,
    set_source, get_source,
    set_filters, get_filters,
    get_input_transform, set_input_transform,
    set_cursor_visibility
)
from win_magnification import const
from win_magnification import effects
from win_magnification import tools
