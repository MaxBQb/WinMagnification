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

You may use old-Style function names:
```py
import win_magnification.old
```

Or you may use more pythonic function names:
```py
import win_magnification
```

You can even use Object-Oriented wrapper:
```py
import win_magnification as mag

api = mag.WinMagnificationAPI()
```

# Known alternatives
[Pymagnification](https://pypi.org/project/pymagnification/)

I can't actually use this lib, I don't know why, it just do nothing and imports nothing.
Also it don't support fullscreen* functions

# Known issues
Working from different threads is pain, and I'm trying to solve/restrict this somehow

# [PyWin32](https://pypi.org/project/pywin32/) Integration?
This package uses ctypes only, so no pywin32 required.
But, well, you can use pywin32 for creating magnifier windows and so on (see example)
