# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

# look below for the exported functions

from sys import implementation as _implementation


# --- [ runtime setup ] ---

# if on circuitpython or micropython, patch the runtime to be closer to cpython
# including: minimal typing, enum.Enum, and __future__.annotations support
if _implementation.name in {"circuitpython", "micropython"}:
    from sys import modules
    from . import enum
    from . import typing

    from .typing import cleanup_typing_artifacts, typing_standin

    modules.pop(enum.__name__)
    modules.pop(typing.__name__)

    enum.__name__ = "enum"
    typing.__name__ = "typing"

    modules["enum"] = enum
    modules["typing"] = typing

    del enum, typing

    # micropython does not have import __future__ support
    try:
        import __future__
    except:  # micropython
        from . import future

        modules.pop(future.__name__)
        modules["__future__"] = future
        future.__name__ = "__future__"

        del future

    del modules
else:
    cleanup_typing_artifacts = lambda *_, **__: set()  # type: ignore
    typing_standin = object


# import typing info to type the functions this module exports (see exports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Self, Literal, Any


# --- [ exports ] ---

# values for checking runtime support, all of these *must* return True on cpython or
# during type-checking

random_base_uid: int
runtime_typing: "Callable[[], Literal[True]]"
supports_warnings: "Callable[[], Literal[True]]"
cleanup_typing_artifacts: "Callable[[dict[str, object]], set[str]]"
typing_standin: type[object]

if TYPE_CHECKING:
    __all__: tuple[str, ...] = (
        "random_base_uid",
        "runtime_typing",
        "supports_warnings",
        "typing_standin",
        "cleanup_typing_artifacts",
    )

# --- [ implementing the exported objects ] ---
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
            return not (_implementation.name == "circuitpython" or _implementation.name == "micropython")  # type: ignore

    runtime_typing = _RuntimeCheck("runtime_typing")
    supports_warnings = _RuntimeCheck("supports_warnings")

    del _RuntimeCheck.__init__, _RuntimeCheck
else:
    runtime_typing = supports_warnings = lambda: not (  # type: ignore
        _implementation.name == "circuitpython" or _implementation.name == "micropython"
    )


# here we use try/except since desktop circuitpython/microython aren't always differentiated well
try:  # circuitpython and cpython
    from random import randint

    random_base_uid = randint(0, 15)
    del randint
except:  # micropython
    from urandom import getrandbits  # type: ignore

    random_base_uid = getrandbits(4)
    del getrandbits
finally:
    pass
