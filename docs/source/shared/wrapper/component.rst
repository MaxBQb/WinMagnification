.. dropdown:: Parameter wrapper
   :color: warning
   :animate: fade-in-slide-down
   :icon: container

   This is wrapper for argument of :abbr:`complex (Have many parameters)` :mod:`winapi <win_magnification>` function, so
   at the time this property accessed the real value is already retrieved.
   Any changes made for this property, or its inner properties are immediately update real value.
   To apply changes at once you may use :meth:`.WrappedField.batch`.
   Also you may use :attr:`.raw` which is equivalent of change all inner fields at once

   .. note::
      .. include:: ../shared/wrapper/common.rst