# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations
from typing import TYPE_CHECKING, Self

from .core.widget import Widget, Body


class Group(Widget):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

    body = Body[Self](lambda self: self)

    def foo(self):
        x = self.body()
        print(x)
