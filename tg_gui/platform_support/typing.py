# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

"""
This modules provies a minimal version of the cpython `typing` module.
The included typing objects *only* guarantee source compatiblity.
- `TYPE_CHECKING`
- `TypeVar("...", ...)`
- `Generic[...]`
- `Protocol[...]`
- `Self`
Import other typing objects inside an `if TYPE_CHECKING` statement, example:
```
from typing import TYPE_CHECKING, TypeVar, Self

T = TypeVar("T")
S = TypeVar("S", bound="Callable[[Awaitable[T]], T]") # requires ""

if TYPE_CHECKING: # always true at "type-time"
    from typing import Literal, Callable, Awaitable # etc
```
"""

## turn off type checking  for this modules
# type: ignore

locals()["TYPE_CHECKING"] = False

# here, const is just used a function that returns the called value
from micropython import const as runtime_checkable


def TypeVar(__name, *_, **__):
    return None  # TODO: consider returning __name


class _GenericBase:
    def __class_getitem__(cls, *_, **__):
        return cls


Generic = _GenericBase
Protocol = _GenericBase
Self = None

del _GenericBase
