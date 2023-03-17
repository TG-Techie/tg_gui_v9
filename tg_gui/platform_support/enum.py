# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

import sys
import gc

if sys.implementation.name not in {"circuitpython", "micropython"}:
    from typing import Any, Self


class Enum:
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        assert (
            cls is not Enum
        ), "subclass Enum to create enum instances, tried to init directly"
        return object.__new__(cls)

    def __init__(self, name: str, value: Any, from_auto: bool = False) -> None:
        self._name: str = name
        self._from_auto = from_auto
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self._name}: {repr(self.value)}{' (auto)' if self._from_auto else ''}>"

    def __init_subclass__(cls) -> None:

        # increment so auto numbers are all greater than the value in the class body
        # this is not standards complicant but should do the trick
        int_values: tuple[int, ...] = tuple(
            filter(lambda o: isinstance(o, int), cls.__dict__.values())  # type: ignore
        )
        auto_number: int = max(int_values) if len(int_values) else 0

        for name, attr in cls.__dict__.items():
            from_auto = False
            if isinstance(attr, auto):
                from_auto = True
                auto_number += 1
                attr = auto_number

            setattr(cls, name, cls(name, attr, from_auto=from_auto))

        # for now, disable creating more variants
        if "__init__" not in cls.__dict__:
            setattr(cls, "__init__", None)

        # cleanup the now referenceless auto() instances
        if int_values:
            gc.collect()

    def __eq__(self, other: Self) -> bool:
        return self.value == other.value


class auto:
    _next_stamp = 1

    value: None | int

    def __init__(self) -> None:
        self.value = None
        self._stamp = self._next_stamp
        auto._next_stamp += 1

    def __repr__(self):
        return f"auto({self.value})"
