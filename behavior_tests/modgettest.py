# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

_counter: int = 0


def __getattr__(name: str) -> int:
    global _counter
    ret = _counter
    _counter += 1
    return ret
