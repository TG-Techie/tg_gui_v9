# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

import sys

from enum import Enum, auto

from typing import TYPE_CHECKING

if sys.implementation.name not in {"circuitpython", "micropython"}:
    from typing import Literal, LiteralString, TypeVar, overload


S = TypeVar("S", bound="LiteralString")


class _FlagPrompt:
    def __getattr__(self, name: S) -> S:
        return name


__ = flag = _FlagPrompt()


if sys.implementation.name in {"circuitpython", "micropython"}:
    from cpython_compat import enum

    sys.modules["enum"] = enum


class InitKind(Enum):
    noinit = auto()
    required = auto()
    default = auto()
    default_factory = auto()
