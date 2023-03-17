# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

import sys as _sys
from time import sleep
from . import time


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    __all__ = ("sleep",)

# patch in a version of the time module that warns to use tg_gui.sleep
_sys.modules.pop(time.__name__)
_sys.modules["time"] = time
time.__name__ = "time"

del _sys
