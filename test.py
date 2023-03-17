# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from tg_gui.prelude import *

# print("", dir())

from tg_gui import Text, Group
from tg_gui import text


class Build(Widget):
    foo: int = State(required=True)
    bar: int = State(default=3, init=True)

    @Body
    def body(self):
        return self


class BuildTwo(Build):
    foo: int = State(default=5, init=True)


class Main(Widget):
    items = State(default_factory=list[str])

    Body[Self](lambda self: Group())


main(Main)

# import sys
# print(*(m for m in sys.modules.keys() if m.startswith("tg")), sep="\n")
