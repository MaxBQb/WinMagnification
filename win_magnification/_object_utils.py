from __future__ import annotations

import abc
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
    ...     value.property1 += 1
    ...     value.property2 -= 1
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
        self._observers.add(on_change)

    def _on_property_changed(self, name: str, value):
        self.__subscribe_property(name, value)
        if not self._batching_changes:
            self._on_change()
        else:
            self._has_changes = True

    @contextlib.contextmanager
    def batch(self: _PropertiesObserverType):
        """
        | Use to apply changes at once
        | See example above (:class:`PropertiesObserver`)
        """
        if self._batching_changes:
            yield
            return
        self._has_changes = False
        self._batching_changes = True
        try:
            yield self
        finally:
            self._batching_changes = False
            if self._has_changes:
                self._on_change()


_T = typing.TypeVar('_T')


class DataSource(typing.Generic[_T]):
    def __init__(self):
        self.use_cache = False
        self._has_cache = False
        self._cache: _T = None

    def source(self) -> _T:
        pass

    def setter(self, value: _T) -> None:
        pass

    @property
    def has_cache(self):
        return self._has_cache and self.use_cache

    @property
    def data(self):
        if self.use_cache:
            if not self._has_cache:
                self._cache = self.source()
                self._has_cache = True
            return self._cache
        return self.source()

    @data.setter
    def data(self, value):
        self._has_cache = False
        self.setter(value)

    @classmethod
    def dynamic(
            cls,
            source: typing.Callable[[], _T],
            setter: typing.Callable[[_T], None],
    ):
        result = cls()
        result.source = source
        result.setter = setter
        return result

    @classmethod
    def static(
            cls,
            value: _T,
    ):
        _state = [value]

        def setter(x: _T):
            _state[0] = x

        result = cls.dynamic(
            lambda: _state[0],
            setter,
        )
        return result

    @classmethod
    def const(
            cls,
            value: _T,
    ):
        return cls.dynamic(
            lambda: value,
            lambda: None,
        )


class CompositeField(typing.Generic[_T]):
    def __init__(
            self,
            datasource: DataSource[_T],
            default: _T,
    ):
        self._datasource = datasource
        self._default = default

    def __eq__(self, other):
        if isinstance(other, CompositeField):
            return self.raw == other.raw
        return super().__eq__(other)

    @property
    def default(self) -> _T:
        return self._default

    @property
    def raw(self) -> _T:
        return self._datasource.data

    @raw.setter
    def raw(self, value: _T):
        self._datasource.data = value

    @raw.deleter
    def raw(self):
        self.raw = self._default

    def reset(self):
        del self.raw


_C = typing.TypeVar('_C', bound='CompositeWrappedField')


class CompositeWrappedField(CompositeField[_T], PropertiesObserver, typing.Generic[_T]):
    def __init__(
            self,
            datasource: typing.Optional[DataSource[_T]] = None,
            default: typing.Optional[_T] = None
    ):

        def set_value(x: _T):
            self._raw = x

        CompositeField.__init__(
            self,
            datasource or DataSource.dynamic(
                lambda: self._raw,
                set_value,
            ),
            default
        )
        PropertiesObserver.__init__(self)
        if default is not None:
            self._default_wrapped: _C = self.__class__(
                DataSource.const(default),
                default=None,
            )

            def set_raw():
                with self._ignore_all_changes():
                    self.raw = self._raw

            self.subscribe(set_raw)
        else:
            self._default_wrapped = None
        self._subscribe_initial()
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
            if isinstance(value, CompositeWrappedField):
                try:
                    field: CompositeWrappedField = getattr(self, key)
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
    @abc.abstractmethod
    def _raw(self) -> _T:
        pass

    @_raw.setter
    @abc.abstractmethod
    def _raw(self, value: _T):
        pass

    def _read_all(self):
        if not self._datasource.has_cache:
            with self._ignore_all_changes():
                self._raw = self.raw

    @contextlib.contextmanager
    def batch(self: _C):
        if self._batching_changes:
            yield
            return
        self._datasource.use_cache = True
        try:
            with super().batch():
                yield self
        finally:
            self._datasource.use_cache = False

    @property
    def default(self: _C) -> _C:  # type: ignore
        return self._default_wrapped if self._default_wrapped else self
