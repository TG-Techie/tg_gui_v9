# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations

from ..platform_support import runtime_typing

from enum import Enum

from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING or runtime_typing():
    from typing import (
        Literal,
        LiteralString,
        TypeGuard,
        TypeVar,
        Any,
        NewType,
    )
    from abc import abstractproperty

    T = TypeVar("T")

    __all__ = (
        "UID",
        "uid",
        "by_uid",
        "ismissing",
        "isnotmissing",
        "MissingType",
        "Missing",
        "Maybe",
        "runtime_typing",
    )

else:
    abstractproperty = property


class _Identifiable(Protocol):
    @abstractproperty
    def uid(self) -> "UID":
        ...


if TYPE_CHECKING or runtime_typing():
    UID = NewType("UID", int)
else:
    UID = int

from random import randint as _randint

__next_uid = UID(_randint(0, 10))


def uid() -> UID:
    """
    returns a unique number that can be used to identify / differentiate objects. UIDs
    are  guaranteed to be sequential but not continuos
    """
    global __next_uid
    new_uid: UID = __next_uid
    __next_uid += UID(1)
    return new_uid


def by_uid(o: _Identifiable) -> UID:
    return o.uid


class MissingType(Enum):
    Missing = None

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> LiteralString:
        return "Missing"


def isnotmissing(__obj: T | MissingType) -> TypeGuard[T]:
    return __obj is not Missing


def ismissing(__obj: Any) -> TypeGuard[MissingType]:
    return __obj is Missing


Missing = MissingType.Missing

if TYPE_CHECKING:
    Maybe = T | MissingType
else:
    Maybe = object
