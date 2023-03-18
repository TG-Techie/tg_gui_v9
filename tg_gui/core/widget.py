# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations
from ..platform_support import typing_standin, cleanup_typing_artifacts

from .shared import UID, uid, by_uid, runtime_typing, Missing, ismissing

from .attrdef import InitKind, isattrdef

# pyright: reportImportCycles=false

from typing import TYPE_CHECKING, TypeVar, Generic, Self, Protocol, dataclass_transform

if TYPE_CHECKING or runtime_typing():
    from typing import (
        TYPE_CHECKING,
        Any,
        ClassVar,
        Callable,
    )

    from .shared import Maybe

    from abc import abstractproperty

    __all__ = ("Widget", "Body")


T = TypeVar("T")
Ws = TypeVar("Ws", bound="Widget")
Wco = TypeVar("Wco", bound="Widget", contravariant=True)


if TYPE_CHECKING:
    # here we use an _AttrSpec protocol so subclasses of AttrDef can be used (like State)
    # without having to modify the Widget base class.
    # ALL uses
    class _AttrDefAndSubclasses(Protocol):
        uid: UID
        name: str

        @abstractproperty
        def init_kind(self) -> InitKind:
            ...

        @abstractproperty
        def in_init(self) -> bool:
            ...

        def init(self, inst: Widget, value: Maybe[Any]):
            ...

        # def init(self, inst: Widget, value: Any = Missing):
        #     ...

    _BodyCallable = Callable[[Wco], "Widget"]
else:
    _AttrDefAndSubclasses = typing_standin


class _BodyDef(Generic[Wco]):
    """
    sugar used to have type-safe inferred declaration of lambdas for the body method of
    Widget classes.
    ```
    body = Body[Self](lambda self: text...)
    ```
    """

    @classmethod
    def __call__(cls, method: Callable[[Wco], Ws]) -> Callable[[Wco], Ws]:
        return method

    def __getitem__(self, type: type[Ws]) -> _BodyDef[Ws]:
        assert self is Body, "Body should be a singleton"
        return Body


Body: _BodyDef[Any] = _BodyDef()
_BodyDef.__new__ = NotImplemented
del _BodyDef


@dataclass_transform(
    eq_default=False,
    order_default=False,
    kw_only_default=False,
    field_specifiers=(_AttrDefAndSubclasses,),
)
class Widget:
    uid: UID

    # body: ClassVar[Callable[[W], Ws]] = None  # type: ignore
    if not TYPE_CHECKING:
        body = None

    _arg_specs_: ClassVar[tuple[_AttrDefAndSubclasses, ...]] = ()
    _attr_specs_: ClassVar[dict[str, _AttrDefAndSubclasses]] = {}

    # def __matmul__(self, transform: Callable[[Self], Self]) -> Self:
    #     pass

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.uid = uid()
        self.state_modified = True
        specs = self._arg_specs_

        assert Missing not in kwargs.values()

        # input sanitization
        if __debug__:
            if len(args) > len(specs):
                raise TypeError(
                    f"{self.__class__.__name__}(...) takes up to {len(specs)} positional "
                    + f"arguments ({len(args)} given)"
                )
            elif len(kwargs) > (len(specs) - len(args)):
                raise TypeError(
                    f"{self.__class__.__name__}(...) called with {len(kwargs)} keyword "
                    + f"arguments, takes up to {len(specs)} total arguments"
                )

        # future: integrate the two below loops
        n_args = len(args)
        missing_args: set[str] = set()
        for index, spec in enumerate(specs):
            spec_name = spec.name

            # passed as positional, if so exit early
            if index < n_args:
                if spec_name in kwargs:
                    raise TypeError(f"got multiple values for argument '{spec_name}'")
                spec.init(self, args[index])
                continue

            # else passed as kwarg

            arg = kwargs.pop(spec_name, Missing)

            if ismissing(arg) and spec.init_kind == InitKind.required:
                missing_args.add(spec_name)
            else:
                spec.init(self, arg)

        # cleanup and checking
        if missing_args:
            raise TypeError(
                f"{self.__class__.__name__}(...) missing "
                + f"argument(s) {', '.join(missing_args)}"
            )

        if kwargs:
            raise TypeError(
                f"{self.__class__.__name__}(...) got unexpected "
                + f"keyword argument(s) {', '.join(kwargs.values())}"
            )

        return

    def __init_subclass__(cls: type[Widget]) -> None:
        # --- body attr ---
        # for typing ease, the user can define the body propery using
        # `body = Body[Self](lambda: ...)` syntax

        # assert "body" in cls.__dict__, "body must be defined"
        assert (
            getattr(cls, "body", None) is not None
        ), "body must be defined in the class declaration or a parent class"

        # --- attributes and arguemnts ---
        # climb the base classes and determine arg order

        attr_specs: dict[str, _AttrDefAndSubclasses] = {}
        new_specs: dict[str, _AttrDefAndSubclasses] = {
            name: spec for name, spec in cls.__dict__.items() if isattrdef(spec)
        }

        for basecls in reversed(cls.__bases__):
            if not issubclass(basecls, Widget):
                continue
            attr_specs.update(basecls._attr_specs_)
        else:
            attr_specs.update(new_specs)

        setattr(cls, "_attr_specs_", dict(attr_specs))

        # the argument order, according to @dataclass_transform conventions, preserves
        # previous optional(/default) arguments and adds new ones on the end in order of
        # declaration where re-declared attributes do not change the argument order
        prev_args = {spec.name for spec in cls._arg_specs_}
        new_args = [
            spec
            for spec in attr_specs.values()
            if spec.in_init and spec.name not in prev_args
        ]
        new_args.sort(key=by_uid)
        setattr(cls, "_arg_specs_", cls._arg_specs_ + tuple(new_args))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} widget uid {self.uid}>"

    if __debug__:

        def __new__(cls, *_: Any, **__: Any) -> Self:
            assert (
                cls is not Widget
            ), "cannot create an instance of the Widget baseclass class, use a subclass"
            return object.__new__(cls)


cleanup_typing_artifacts(locals())
