# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

import time as _time
from ..platform_support import supports_warnings as _supports_warnings


def __getattr__(name: str):
    if name == "sleep":
        msg = "When using tg_gui, use the tg_gui supplied sleep function. `from tg_gui import sleep`"
        if _supports_warnings():
            raise Warning(msg)
        else:
            print("WARNING: When using tg_gui, use the tg_gui supplied sleep function.")
    return getattr(_time, name)
