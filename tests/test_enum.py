# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

import sys

if sys.implementation.name in {"circuitpython", "micropython"}:
    from cpython_compat import enum

    sys.modules["enum"] = enum


from enum import Enum, auto


class MissingType(Enum):
    Missing = auto()


Missing = MissingType.Missing

print(Missing)
