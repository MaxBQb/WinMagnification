# WinMagnification
Python wrapper for [Windows Magnification API](https://docs.microsoft.com/en-us/windows/win32/api/_magapi/)

Covered functions:
+ MagInitialize
+ MagUninitialize
+ MagGetFullscreenColorEffect
+ MagSetFullscreenColorEffect
+ MagSetFullscreenTransform
+ MagGetFullscreenTransform
+ MagSetColorEffect
+ MagGetColorEffect
+ MagSetWindowTransform
+ MagGetWindowTransform
+ MagSetWindowSource
+ MagGetWindowSource
+ MagSetWindowFilterList
+ MagGetWindowFilterList
+ MagGetInputTransform
+ MagSetInputTransform
+ MagShowSystemCursor

You may use old-style function names:
```py
import win_magnification as mag
import win_magnification.old as old_mag

old_mag.MagInitialize()
old_mag.MagSetFullscreenColorEffect(mag.const.COLOR_INVERSION_EFFECT)
old_mag.MagSetFullscreenColorEffect(mag.const.DEFAULT_COLOR_EFFECT)
old_mag.MagUninitialize()
```

Or you may use more pythonic function names:
```py
import win_magnification as mag

mag.initialize()
mag.set_fullscreen_color_effect(mag.const.COLOR_INVERSION_EFFECT)
mag.reset_fullscreen_color_effect()
mag.finalize()
```

Or... you can even use Object-Oriented wrapper:
```py
import win_magnification as mag

api = mag.WinMagnificationAPI()
api.fullscreen.color_effect.raw = mag.const.COLOR_INVERSION_EFFECT
api.fullscreen.color_effect.reset()
```

# Restrictions
There are 3.5 groups of functions:

- Fullscreen (nothing required, call and chill) have limited functional, but simple:
  + get/set_fullscreen_color_effect
  + get/set_fullscreen_transform
  + **get_input_transform**
- Window (requires window creation as shown in [example](https://github.com/MaxBQb/WinMagnification/blob/master/example/windows_utils.py)),
more powerful, but requires such things like custom window creation (hello from [pywin32](https://pypi.org/project/pywin32/)),
[UiAccess](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/user-account-control-allow-uiaccess-applications-to-prompt-for-elevation-without-using-the-secure-desktop) (Hard to obtain) if you need your magnifier [above everything](https://blog.adeltax.com/window-z-order-in-windows-10/), but you can simulate all fullscreen functions too:
  + get/set_color_effect
  + get/set_transform
  + get/set_source
  + get/set_filters (supports exclusion only, looks like excluded windows never exist for magnifier)
- [UiAccess](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/user-account-control-allow-uiaccess-applications-to-prompt-for-elevation-without-using-the-secure-desktop) required:
  + **set_input_transform**
- Other:
  + initialize
  + finalize
  + set_cursor_visibility (cursor stay hidden until active)

# Known alternatives
[Pymagnification](https://pypi.org/project/pymagnification/)

I can't actually use this lib, I don't know why, it just does nothing and imports nothing.
Also, it doesn't support fullscreen* functions

# Known issues
Working from different threads is pain, and I'm trying to solve/restrict this somehow

# [PyWin32](https://pypi.org/project/pywin32/) Integration?
This package uses ctypes only, so no pywin32 required.
But, well, you can use pywin32 for creating magnifier windows and so on (see [example](https://github.com/MaxBQb/WinMagnification/blob/master/example/windows_utils.py))
