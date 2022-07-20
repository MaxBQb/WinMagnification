"""
Functions with winapi-style names
"""
import win_magnification as mag

MagInitialize = mag.initialize
# noinspection SpellCheckingInspection
MagUninitialize = mag.finalize
MagGetFullscreenColorEffect = mag.get_fullscreen_color_effect
MagSetFullscreenColorEffect = mag.set_fullscreen_color_effect
MagSetFullscreenTransform = mag.set_fullscreen_transform
MagGetFullscreenTransform = mag.get_fullscreen_transform
MagSetColorEffect = mag.set_color_effect
MagGetColorEffect = mag.get_color_effect
MagSetWindowTransform = mag.set_transform_advanced
MagGetWindowTransform = mag.get_transform_advanced
MagSetWindowSource = mag.set_source
MagGetWindowSource = mag.get_source
MagSetWindowFilterList = mag.set_filters
MagGetWindowFilterList = mag.get_filters
MagGetInputTransform = mag.get_input_transform
MagSetInputTransform = mag.set_input_transform
MagShowSystemCursor = mag.set_cursor_visibility
