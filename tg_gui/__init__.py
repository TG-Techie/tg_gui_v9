# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

# intentionally excluding `from __future__ import annotations`

# --- cpython compat ---
# in on circuitpython, importing this first will patch the runtime to closer to cpython compatible, as needed
from . import platform_support as _

from .platform_support import runtime_typing as _runtime_typing
import sys as _sys

# --- versioning and (runtime) linting ---
# patch in a version of time that warns about time.sleep
from . import _async_prep as _


# --- typing ---
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any

# ----------------------------------


__module_exports: dict[str, str | tuple[None, "Any"]] = {
    # unimported = "<the module name>"
    # imported = (<the object to return>,) # in a tuple
    "Text": "text",
    "Group": "group",
    "sleep": "_async_prep",
}

if TYPE_CHECKING or _runtime_typing():
    __all__ = ()
    from .group import Group
    from .text import Text


def __getattr__(name: str) -> "Any":
    try:
        pack = __module_exports[name]
    except KeyError as err:
        args = err.args
        raise AttributeError(*args)

    if isinstance(pack, tuple):  # than it has already been imported
        _, obj = pack
        return obj
    else:  # import it and then cache it
        # obj = getattr(__import__(f"{__name__}.{pack}"), name)
        obj = None
        if TYPE_CHECKING:
            obj: Any = None

        # a rule of thumb check that builtins have not been messed with
        assert "builtin" not in _sys.modules

        # due to incompatibility issues this is the best balance between the options
        exec(f"from .{pack} import {name}")

        __module_exports[name] = (None, locals()[name])
        return obj
