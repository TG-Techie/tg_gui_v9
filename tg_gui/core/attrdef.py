# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations

# allow type-checking time import of Widget for typing purposes
# pyright: reportImportCycles=false


from .shared import (
    uid as uid,
    UID,
    Maybe,
    Missing,
    isnotmissing,
    ismissing,
)


from typing import TYPE_CHECKING, Generic, TypeVar, Self

from enum import Enum, auto


T = TypeVar("T")

if TYPE_CHECKING:
    from typing import TypeGuard, Any, Literal, overload, Callable

    from .widget import Widget


class InitKind(Enum):
    required = auto()
    default = auto()
    default_factory = auto()


def isattrdef(o: Any | AttrDef[Any]) -> TypeGuard[AttrDef[Any]]:
    return isinstance(o, AttrDef)


class AttrDef(Generic[T]):
    uid: UID
    name: str
    owning_type: type[Widget]
    _in_init: bool = False
    _default: Maybe[T] = Missing
    _default_factory: Maybe[Callable[[], T]] = Missing
    _private_id: str

    @property
    def init_kind(self) -> InitKind:
        if isnotmissing(self._default):
            return InitKind.default
        elif isnotmissing(self._default_factory):
            return InitKind.default_factory
        else:
            return InitKind.required

    @property
    def in_init(self) -> bool:
        return self._in_init

    def __set_name__(self, owner: type[Widget], name: str) -> None:
        self.name = name
        self.owning_type = owner
        self._private_id = f":{self.name}"

    def __get__(self, inst: Widget, iscls: type[Widget] | None) -> T:
        return getattr(inst, self._private_id)

    def __set__(self, inst: Widget, value: T) -> None:
        setattr(inst, self._private_id, value)

    def init(self, inst: Widget, value: Maybe[T] = Missing) -> None:
        if ismissing(value):
            if self.init_kind == InitKind.required:
                raise TypeError(
                    f"{inst.__class__.__name__}(...) missing required argument "
                    + repr(self.name)
                )
            elif self.init_kind == InitKind.default:
                assert isnotmissing(self._default)
                value = self._default
            else:
                assert self.init_kind == InitKind.default_factory
                assert isnotmissing(self._default_factory)
                value = self._default_factory()
        assert isnotmissing(value)
        self.__set__(inst, value)

    if TYPE_CHECKING:
        # FUTURE: add __new__ overloads to specialize State into SequenceState and MappingState as needed

        @overload
        def __new__(
            cls,
            default: T,
            *,
            init: Literal[False] = False,
        ) -> Self:
            ...

        @overload
        def __new__(
            cls,
            *,
            default_factory: Callable[[], T],
            init: Literal[False] = False,
        ) -> Self:
            ...

        @overload
        def __new__(
            cls,
            *,
            required: Literal[True],
            init: Literal[True] = True,
        ) -> Any:
            ...

        @overload
        def __new__(
            cls,
            default: T,
            *,
            init: Literal[True],
        ) -> T:
            ...

        @overload
        def __new__(
            cls,
            *,
            default_factory: Callable[[], T],
            init: Literal[True],
        ) -> T:
            ...

        def __new__(
            cls,
            default: Maybe[T] = Missing,
            *,
            default_factory: Maybe[Callable[[], T]] = Missing,
            required: Maybe[Literal[True]] = Missing,
            init: Maybe[bool] = Missing,
        ) -> Any:
            ...

    else:

        def __init__(
            self,
            default: Maybe[T] = Missing,
            *,
            default_factory: Maybe[Callable[[], T]] = Missing,
            required: Maybe[Literal[True]] = Missing,
            init: Maybe[bool] = Missing,
        ) -> None:
            if isnotmissing(required):
                assert ismissing(default)
                assert ismissing(default_factory)
                assert init is not False
                init = True

                self._init_kind = InitKind.required
            elif isnotmissing(default):
                assert ismissing(required)
                assert ismissing(default_factory)

                self._default = default
            if isnotmissing(default_factory):
                assert ismissing(required)
                assert ismissing(default)

                self._default_factory = default_factory

            if init is True:
                self._in_init = True

            self.uid = uid()
