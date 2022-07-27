"""
| Internal module
"""

from __future__ import annotations

import contextlib
import inspect
import threading
import typing

_PropertiesObserverType = typing.TypeVar('_PropertiesObserverType', bound='PropertiesObserver')


class PropertiesObserver:
    """
    | Usage example:
    >>> class MyPropertiesObserver(PropertiesObserver):
    ...     def __init__(self):
    ...         self.property1 = 10
    ...         self.property2 = 10
    ...         super().__init__()
    ...
    >>> property_observer = MyPropertiesObserver()
    >>> property_observer.subscribe(lambda *_: print('update'))
    >>> with property_observer.batch() as value:
    ...     value.property1 += 1  # or property_observer.property1 += 1
    ...     value.property2 -= 1  # or property_observer.property2 -= 1
    update
    >>> property_observer.property1 += 1; property_observer.property2 -= 1
    update
    update
    """

    def __init__(self):
        self._ignored_changes = set()
        self._all_changes_ignored = False
        self._inner_observables = set()
        self._is_property = False
        self._observers = set()
        self._locks: typing.Dict[str, threading.RLock] = dict()
        self._has_changes = False
        self._batching_changes = False
        self._subscribe_initial()

    def _subscribe_initial(self):
        for name, value in self._properties_observed.items():
            self.__subscribe_property(name, value)

    @property
    def _properties_observed(self):
        return {
            key: value for key, value in vars(self).items() if self.__is_property_observed(key)
        }

    def __is_property_observed(self, name: str):
        if self._all_changes_ignored or name in self._ignored_changes:
            return False

        if not (name in self._inner_observables or
                not name.startswith('_')):
            return False

        prop = getattr(type(self), name, None)
        return not prop or not inspect.isdatadescriptor(prop)

    @contextlib.contextmanager
    def _ignore_changes(self, *names: str):
        for name in names:
            self._ignored_changes.add(name)
        try:
            yield
        finally:
            for name in names:
                self._ignored_changes.remove(name)

    @contextlib.contextmanager
    def _ignore_all_changes(self):
        if self._all_changes_ignored:
            yield
            return
        self._all_changes_ignored = True
        try:
            yield
        finally:
            self._all_changes_ignored = False

    def __setattr__(self, name: str, value):
        notify = hasattr(self, "_observers") and \
                 self.__is_property_observed(name)
        if notify:
            self._locks.setdefault(name, threading.RLock())
            self._locks[name].acquire()
        super().__setattr__(name, value)
        if notify:
            with self._ignore_changes(name):
                self._on_property_changed(name, value)
            self._locks[name].release()

    def __subscribe_property(self, prop_name, value):
        if not isinstance(value, PropertiesObserver):
            return
        if self._is_property:
            return
        else:
            self._is_property = True
        value.subscribe(lambda: self._on_property_changed(prop_name, value))

    def _on_change(self):
        for on_change in self._observers:
            on_change()

    def subscribe(self, on_change: typing.Callable):
        """
        | The **on_change** functions will be called when
          a class property changes *(mostly for internal use)*
        | See example :class:`above <PropertiesObserver>`

        :param on_change: Function to call
        """
        self._observers.add(on_change)

    def _on_property_changed(self, name: str, value):
        self.__subscribe_property(name, value)
        if not self._batching_changes:
            if not self._all_changes_ignored:
                self._on_change()
        else:
            self._has_changes = True

    @contextlib.contextmanager
    def batch(self: _PropertiesObserverType):
        """
        | Use this *contextmanager* to apply changes at once
        | See example :class:`above <PropertiesObserver>`
        """
        if self._batching_changes:
            yield self
            return
        self._has_changes = False
        self._batching_changes = True
        try:
            yield self
        finally:
            self._batching_changes = False
            if self._has_changes:
                self._on_change()


T = typing.TypeVar('T')
TSource = typing.Callable[[], T]
TSetter = typing.Callable[[T], None]


class DataSource(typing.Generic[T]):
    """
    Wraps interaction with outer world data sources
    """

    def __init__(self):
        self.use_cache: bool = False
        """
        | Save last value or get fresh one each time?
        | |Accessors: Get Set|
        """
        self._has_cache = False
        self._cache: T = None

    def source(self) -> T:
        """Overridable method of getting fresh data"""

    def setter(self, value: T) -> None:
        """Overridable method of updating data"""

    @property
    def has_cache(self) -> bool:
        """
        | True if last value saved, and it should be used instead of getting fresh one
        | |Accessors: Get|
        """
        return self._has_cache and self.use_cache

    @property
    def data(self) -> T:
        """
        | Value from datasource
        | When :attr:`.use_cache` enabled stores and reuses the last value retrieved
        | |Accessors: Get Set|
        """
        if self.use_cache:
            if not self._has_cache:
                self._cache = self.source()
                self._has_cache = True
            return self._cache
        return self.source()

    @data.setter
    def data(self, value: T):
        self._has_cache = False
        self.setter(value)

    @classmethod
    def dynamic(cls: typing.Type[WrappedFieldType], source: TSource, setter: TSetter) -> WrappedFieldType:
        """
        Creates :class:`DataSource` with source/setter specified

        :param source: New method of getting fresh data
        :param setter: New method of updating data
        :return: New DataSource
        """
        result = cls()
        result.source = source
        result.setter = setter
        return result

    @classmethod
    def const(cls: typing.Type[WrappedFieldType], value: T) -> WrappedFieldType:
        """
        Creates :class:`DataSource` which constantly returns
        the same value, that can't be changed

        :param value: Const to retrieve
        :return: New DataSource
        """
        return cls.dynamic(
            lambda: value,
            lambda: None,
        )


WrappedFieldType = typing.TypeVar('WrappedFieldType', bound='WrappedField')  #: Any child of :class:`WrappedField`


class WrappedField(PropertiesObserver, typing.Generic[T]):
    """
    | Allows to get/set/get default/reset value of field wrapped
    | Mostly used to allow selective changes of complex fields
    """
    _DEFAULT_RAW: T
    _DEFAULT: WrappedFieldType  # type: ignore

    def __init__(
            self,
            datasource: typing.Optional[DataSource[T]] = None
    ):
        self._source_dependent = set()

        def set_value(x: T):
            with self.batch():
                self._raw = x

        def get_value() -> T:
            with self._ignore_all_changes():
                return self._raw

        self._datasource = datasource or DataSource.dynamic(
            get_value,
            set_value,
        )
        super().__init__()

        def set_raw():
            with self._ignore_all_changes():
                self.raw = self._raw

        self.subscribe(set_raw)

    def _subscribe_initial(self):
        super()._subscribe_initial()
        self._source_dependent = set(self._properties_observed)

    def __getattribute__(self, item):
        if item != '_source_dependent' and \
                item != '_all_changes_ignored' and \
                hasattr(self, '_source_dependent') and \
                not getattr(self, '_all_changes_ignored', True) and \
                item in getattr(self, '_source_dependent'):
            self._read_all()
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if hasattr(self, '_source_dependent') and \
                key in getattr(self, '_source_dependent'):
            if not self._all_changes_ignored:
                self._read_all()
            if isinstance(value, WrappedField):
                try:
                    field: WrappedField = getattr(self, key)
                    field.raw = value.raw
                    return
                except AttributeError:
                    pass
        super().__setattr__(key, value)

    def __delattr__(self, item):
        if item in self._source_dependent:
            setattr(self, item, getattr(self.default, item))
        else:
            return super().__delattr__(item)

    @property
    def _raw(self) -> T:
        return None  # type: ignore

    @_raw.setter
    def _raw(self, value: T):
        pass

    def _read_all(self):
        if not self._datasource.has_cache:
            with self._ignore_all_changes():
                self._raw = self.raw

    @contextlib.contextmanager
    def batch(self: WrappedFieldType):
        """
        | Use this *contextmanager* to read/write fields at one shot
        | See example in :class:`parent <PropertiesObserver>`
        """
        if self._batching_changes:
            yield self
            return
        with super().batch():
            self._datasource.use_cache = True
            try:
                yield self
            finally:
                self._datasource.use_cache = False

    @property
    def default(self: WrappedFieldType) -> WrappedFieldType:
        """
        | Default value of wrapped field
        | |Accessors: Get|
        """
        if not hasattr(self, '_DEFAULT'):
            self.__class__._DEFAULT = self.__class__(
                DataSource.const(self._DEFAULT_RAW)
            )
        return self._DEFAULT

    def __eq__(self, other):
        if isinstance(other, WrappedField):
            return self.raw == other.raw
        return super().__eq__(other)

    @property
    def raw(self) -> T:
        """
        | Raw value with no wrappers used
        | |Accessors: Get Set Delete|
        | **Deleter**: resets value with :attr:`.default`
        """
        return self._datasource.data

    @raw.setter
    def raw(self, value: T):
        self._datasource.data = value

    @raw.deleter
    def raw(self):
        self.raw = self._DEFAULT_RAW

    def reset(self):
        """Resets value of wrapped field to :attr:`.default`"""
        del self.raw


def ensure_same(*values: T) -> typing.Optional[T]:
    pattern = values[0]
    if all(value == pattern for value in values):
        return pattern
    return None
