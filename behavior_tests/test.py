# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from tg_gui.core.widget import *


class Text(Widget):
    label: str = State(required=True, init=True)
    font: str = State(default="menlo", init=True)

    body = Body[Self](lambda self: self)


class SubclassedText(Text):
    foo: int = State(default=1, init=True)
    font: str = State(default="comic sans", init=True)


SubclassedText()


class DoubleSubclassedText(SubclassedText):
    bar: None = State(default=None, init=True)


DoubleSubclassedText()

Text()
SubclassedText()
DoubleSubclassedText()


from dataclasses import dataclass


@dataclass
class DT:
    label: str = State(required=True, init=True)
    font: str = State(default="menlo", init=True)


@dataclass
class SubclassedDT(DT):
    foo: int = State(default=1, init=True)
    font: str = State(default="comic sans", init=True)


SubclassedDT()


@dataclass
class DoubleSubclassedDT(SubclassedDT):
    bar: None = State(default=None, init=True)


DoubleSubclassedDT()

DT()
SubclassedDT()
DoubleSubclassedDT()
