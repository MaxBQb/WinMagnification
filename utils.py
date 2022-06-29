"""
Additional tools available for programmer

Author: MaxBQb
"""
import abc
import contextlib
import math
import threading
import typing

import constants


def pos_for_matrix(array_len: int, *coords: int) -> int:
    row_len = int(math.log(array_len, len(coords)))
    return sum(
        row_len ** i * pos for (i, pos) in enumerate(reversed(coords), 0)
    )


def get_transform_matrix(x=1.0, y=1.0) -> constants.TransformationMatrix:
    return (
        x, 0.0, 0.0,
        0.0, y, 0.0,
        0.0, 0.0, 1.0,
    )


def get_color_matrix(
        mul_red=1.0, mul_green=1.0, mul_blue=1.0, mul_alpha=1.0,
        add_red=0.0, add_green=0.0, add_blue=0.0, add_alpha=0.0,
) -> constants.ColorMatrix:
    return (
        mul_red, 0.0, 0.0, 0.0, 0.0,
        0.0, mul_green, 0.0, 0.0, 0.0,
        0.0, 0.0, mul_blue, 0.0, 0.0,
        0.0, 0.0, 0.0, mul_alpha, 0.0,
        add_red, add_green, add_blue, add_alpha, 1.0,
    )


def get_color_matrix_inversion(value=1.0):
    value2 = value * 2 - 1.0
    return get_color_matrix(
        mul_red=-value2,
        mul_green=-value2,
        mul_blue=-value2,
        add_red=value,
        add_green=value,
        add_blue=value,
    )


PropertiesObserverType = typing.TypeVar('PropertiesObserverType', bound='PropertiesObserver')


class PropertiesObserver:
    def __init__(self):
        self._ignored_changes = set()
        self._is_property = False
        self._observers = set()
        self._locks: dict[str, threading.RLock] = dict()
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
    def batch(self: PropertiesObserverType):
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


T = typing.TypeVar('T')
FieldWrapperType = typing.TypeVar('FieldWrapperType', bound='FieldWrapper')


class FieldWrapper(typing.Generic[T], metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def wrap(cls: typing.Type[FieldWrapperType], value: T) -> FieldWrapperType:
        pass

    @property
    @abc.abstractmethod
    def raw(self) -> T:
        pass


class ObservableWrapper(PropertiesObserver, FieldWrapper[T], abc.ABC):
    pass


class CompositeField(typing.Generic[T]):
    def __init__(
        self,
        source: typing.Callable[[], T],
        setter: typing.Callable[[T], None],
        default: T,
    ):
        self._source = source
        self._setter = setter
        self._default = default

    @property
    def default(self) -> T:
        return self._default

    @property
    def raw(self) -> T:
        return self._source()

    @raw.setter
    def raw(self, value: T):
        self._setter(value)

    @raw.deleter
    def raw(self):
        self.raw = self._default

    def reset(self):
        del self.raw


E = typing.TypeVar('E', bound=ObservableWrapper)


class CompositeWrappedField(CompositeField[T], typing.Generic[T, E]):
    def __init__(
        self,
        wrapper: typing.Type[E],
        source: typing.Callable[[], T],
        setter: typing.Callable[[T], None],
        default: T,
    ):
        super().__init__(source, setter, default)
        self._wrapper: typing.Callable[[T], E] = wrapper.wrap
        self._default_wrapped = self._wrapper(default)

    @property
    def default(self) -> E:  # type: ignore
        return self._default_wrapped

    @property
    def value(self) -> E:
        value = self._wrapper(self._source())
        value.subscribe(lambda: self._setter(value.raw))
        return value

    @value.deleter
    def value(self):
        del self.raw
