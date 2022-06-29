# WinMagnification
Python wrapper for Windows Magnification API

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
