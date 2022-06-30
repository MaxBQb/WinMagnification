import abc
import contextlib
import threading
import typing

_PropertiesObserverType = typing.TypeVar('_PropertiesObserverType', bound='PropertiesObserver')


class PropertiesObserver:
    def __init__(self):
        self._ignored_changes = set()
        self._is_property = False
        self._observers = set()
        self._locks: typing.Dict[str, threading.RLock] = dict()
        self._batching_changes = 0
        self._subscribe_initial()

    def _subscribe_initial(self):
        for name, value in vars(self).items():
            if self.__is_property_observed(name):
                self.__subscribe_property(name, value)

    def __is_property_observed(self, name: str):
        return (
                not name.startswith('_') and
                name not in self._ignored_changes and
                vars(self).get(name)
        )

    @contextlib.contextmanager
    def _ignore_changes(self, name: str):
        self._ignored_changes.add(name)
        try:
            yield
        finally:
            self._ignored_changes.remove(name)

    def __setattr__(self, name: str, value):
        notify = hasattr(self, "_ignored_changes") and \
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

    @contextlib.contextmanager
    def batch(self: _PropertiesObserverType):
        """
        Use to apply changes at once

        with property_observer.batch() as value:
            value.property1 += 1
            value.property2 -= 1
        """
        self._batching_changes += 1
        try:
            yield self
        finally:
            self._batching_changes -= 1
        if not self._batching_changes:
            self._on_change()


_T = typing.TypeVar('_T')
_FieldWrapperType = typing.TypeVar('_FieldWrapperType', bound='FieldWrapper')


class FieldWrapper(typing.Generic[_T], metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def wrap(cls: typing.Type[_FieldWrapperType], value: _T) -> _FieldWrapperType:
        pass

    @property
    @abc.abstractmethod
    def raw(self) -> _T:
        pass


class ObservableWrapper(PropertiesObserver, FieldWrapper[_T], abc.ABC):
    pass


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


_E = typing.TypeVar('_E', bound=ObservableWrapper)


class CompositeWrappedField(CompositeField[_T], typing.Generic[_T, _E]):
    def __init__(
        self,
        wrapper: typing.Type[_E],
        source: typing.Callable[[], _T],
        setter: typing.Callable[[_T], None],
        default: _T,
    ):
        super().__init__(source, setter, default)
        self._wrapper: typing.Callable[[_T], _E] = wrapper.wrap
        self._default_wrapped = self._wrapper(default)

    @property
    def default(self) -> _E:  # type: ignore
        return self._default_wrapped

    @property
    def value(self) -> _E:
        value = self._wrapper(self._source())
        value.subscribe(lambda: self._setter(value.raw))
        return value

    @value.deleter
    def value(self):
        del self.raw
