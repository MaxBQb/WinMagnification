.. dropdown:: Function wrapper
   :color: success
   :animate: fade-in-slide-down
   :icon: package

   This is wrapper for :abbr:`complex (Have many parameters)` :mod:`winapi <win_magnification>` function, so
   each time inner property accessed it will retrieve real values
   by calling this function, which can be used to change some
   parameters independently of others, to get/set a couple of values at once
   use :meth:`.WrappedField.batch`, also you may use :attr:`.raw`, it works just like
   direct winapi function call.

   .. note::
      .. include:: ../shared/wrapper/common.rst
