# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar

    W = TypeVar("W")


def main(maincls: type[W]) -> type[W]:
    mainwid = maincls()

    print("main(...):", mainwid)

    return maincls
