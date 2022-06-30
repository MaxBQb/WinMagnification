"""
Author: MaxBQb
Docs: https://docs.microsoft.com/en-us/windows/win32/api/_magapi/
Header: https://pastebin.com/Lh82NjjM
"""
from ._wrapper import (
    get_fullscreen_color_effect, set_fullscreen_color_effect,
    set_fullscreen_transform, get_fullscreen_transform,
    get_color_effect, set_color_effect,
    get_transform, set_source, get_source,
    set_filters, get_filters,
    get_input_transform, set_input_transform,
    set_cursor_visibility
)
from ._functional_wrapper import *
from . import const
from . import tools
from ._object_wrapper import WinMagnificationAPI
