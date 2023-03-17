# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from sys import implementation

# if on circuitpython or micropython, patch the runtime to be closer to cpython
# including: minimal typing, enum.Enum, and __future__.annotations support
if implementation.name in {"circuitpython", "micropython"}:
    from sys import modules
    from . import enum, typing

    modules.pop(enum.__name__)
    modules.pop(typing.__name__)

    enum.__name__ = "enum"
    typing.__name__ = "typing"

    modules["enum"] = enum
    modules["typing"] = typing

    del enum, typing

    # micropython does not have import __future__ support
    if implementation.name == "micropython":
        from . import future

        modules.pop(future.__name__)
        modules["__future__"] = future
        future.__name__ = "__future__"

        del future

    del modules


# import typing info to type the functions this module exports (see exports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Self, Literal, Any


# --- [ start exports ] ---

# values for checking runtime support, all of these *must* return True on cpython or
# during type-checking

runtime_typing: "Callable[[], Literal[True]]"
supports_warnings: "Callable[[], Literal[True]]"
# --- end exports ---

if __debug__:

    class _RuntimeCheck:
        """
        For debug, raise an Exception when runtime_typing(), or similar, is used and
        without being called.
        """

        def __init__(self, name: str) -> None:
            self._name = name

        def __bool__(self: "Self") -> bool:
            raise RuntimeError(f"`{self._name}(...)` must be called")

        def __call__(self, *__args: "Any", **__kwargs: "Any") -> "Literal[True]":
            return not (implementation.name == "circuitpython" or implementation.name == "micropython")  # type: ignore

    runtime_typing = _RuntimeCheck("runtime_typing")
    supports_warnings = _RuntimeCheck("supports_warnings")

    del _RuntimeCheck.__init__, _RuntimeCheck
else:
    runtime_typing = lambda: not (implementation.name == "circuitpython" or implementation.name == "micropython")  # type: ignore
    supports_warnings = runtime_typing
