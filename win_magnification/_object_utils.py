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
        self._batching_changes = 0
        self._subscribe_initial()

    def _subscribe_initial(self):
        for name, value in vars(self).items():
            if self.__is_property_observed(name):
                self.__subscribe_property(name, value)

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
        if not self._batching_changes:
            self._has_changes = False
        self._batching_changes += 1
        try:
            yield self
        finally:
            self._batching_changes -= 1
            if not self._batching_changes and self._has_changes:
                self._on_change()


_T = typing.TypeVar('_T')


class CompositeField(typing.Generic[_T]):
    def __init__(
            self,
            source: typing.Callable[[], _T],
            setter: typing.Callable[[_T], None],
            default: _T,
    ):
        self._source = source
        self._setter = setter
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
        return self._source()

    @raw.setter
    def raw(self, value: _T):
        self._setter(value)

    @raw.deleter
    def raw(self):
        self.raw = self._default

    def reset(self):
        del self.raw


_C = typing.TypeVar('_C', bound='CompositeWrappedField')


class CompositeWrappedField(CompositeField[_T], PropertiesObserver, typing.Generic[_T]):
    def __init__(
            self,
            source: typing.Optional[typing.Callable[[], _T]] = None,
            setter: typing.Optional[typing.Callable[[_T], None]] = None,
            default: typing.Optional[_T] = None
    ):

        def set_value(x: _T):
            self._local_raw = x

        CompositeField.__init__(
            self,
            source or (lambda: self._local_raw),
            setter or set_value,
            default
        )
        PropertiesObserver.__init__(self)
        self._is_cached = False
        self._raw: typing.Optional[_T] = None
        if default is not None:
            self._default_wrapped: _C = self.__class__(
                source=lambda: default,
                setter=lambda x: None,
                default=None,
            )

            def set_raw():
                with self._ignore_all_changes():
                    self._setter(self._local_raw)

            self.subscribe(set_raw)
        else:
            self._default_wrapped = None
        temp = set(dir(self))
        with self._ignore_all_changes():
            self._define_observable()
        self._source_dependent = set(dir(self)).difference(temp)
        self._subscribe_initial()

    def __getattribute__(self, item):
        if item not in {
            '_source_dependent',
            '_all_changes_ignored',
        } and not getattr(self, '_all_changes_ignored', False) \
                and item in getattr(self, '_source_dependent', {}):
            self._read_all()
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in getattr(self, '_source_dependent', {}):
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

    def _define_observable(self):
        pass

    @property
    @abc.abstractmethod
    def _local_raw(self) -> _T:
        pass

    @_local_raw.setter
    @abc.abstractmethod
    def _local_raw(self, value: _T):
        pass

    def _read_all(self):
        if not self._cache_used:
            with self._ignore_all_changes():
                self._local_raw = self.raw

    @property
    def _cache_used(self):
        return self._is_cached and self._batching_changes != 0

    @property
    def raw(self) -> _T:
        if not self._cache_used:
            self._is_cached = self._batching_changes != 0
            self._raw = self._source()
        return self._raw  # type: ignore

    @raw.setter
    def raw(self, value: _T):
        self._setter(value)
        self._is_cached = False

    @raw.deleter
    def raw(self):
        self.raw = self._default

    @property
    def default(self: _C) -> _C:  # type: ignore
        return self._default_wrapped if self._default_wrapped else self
