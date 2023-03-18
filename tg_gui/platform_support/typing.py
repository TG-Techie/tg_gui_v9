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
from micropython import const as runtime_checkable  # type: ignore

dataclass_transform = lambda *_, **__: (lambda o: o)  # type: ignore


def TypeVar(__name: str, *_: object, **__: object) -> object:
    return TypeVar  # type: ignore


class _GenericBase:
    def __class_getitem__(cls, *_: object, **__: object) -> type["_GenericBase"]:
        return cls


Generic = _GenericBase
Protocol = _GenericBase
Self = _GenericBase

typing_standin = _GenericBase


def cleanup_typing_artifacts(
    scope: dict[str, object], debug: bool = False
) -> frozenset[str]:
    """
    This is designed to be called at the end of a module. Doing so on circuitpython
    removes typing artifacts left inorder to conserve memory. [provided enough objects
    were imported that the scope's dictionary would shrink enough to trigger a resize,
    naturally ;-)]

    :param scope: the scope to clean up, generally `locals()`.
    :returns: a set of the keys that were removed.
    """

    excluded_values = globals().values()

    to_remove = frozenset(
        k
        for k, v in scope.items()
        if v in excluded_values and k not in ("TYPE_CHECKING", "Self")
    )

    if debug and __debug__:
        print(
            f"cleaning typing data from the {scope.get('__name__', '??')} module, "
            + f"initial size = {len(scope)},"
            + f" final size = {len(scope) - len(to_remove)},"
            + f" reduction = {(len(to_remove) / len(scope))*100}%"
        )

    for k in to_remove:
        del scope[k]

    return to_remove
