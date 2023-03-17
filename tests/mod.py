# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from attr_spec import AttrSpecified, ParamSpec


class Foo(AttrSpecified):
    a: str = ParamSpec(default="")


class Bar(Foo):
    b: int = ParamSpec(default=0)
