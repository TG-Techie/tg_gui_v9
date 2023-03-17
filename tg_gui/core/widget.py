# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations

from .shared import UID, uid, by_uid, runtime_typing, Missing, ismissing

from .state import InitKind, isstatedef

# pyright: reportImportCycles=false

from typing import TYPE_CHECKING, TypeVar, Generic, Self

if TYPE_CHECKING or runtime_typing():
    from typing import (
        TYPE_CHECKING,
        dataclass_transform,
        Protocol,
        Any,
        ClassVar,
        Callable,
    )

    from .shared import Maybe

    from abc import abstractproperty

    __all__ = ("Widget", "Body")

else:
    ABC = object
    Protocol = object
    abstractproperty = property
    abstractmethod = lambda fn: fn
    dataclass_transform = lambda *_, **__: (lambda o: o)  # type: ignore


T = TypeVar("T")
W = TypeVar("W", bound="Widget", contravariant=True)
Ws = TypeVar("Ws", bound="Widget")

if TYPE_CHECKING:

    class _AttrSpec(Protocol):
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

    _BodyCallable = Callable[[W], "Widget"]
else:
    _AttrSpec = object


class _BodyDef(Generic[W]):
    """
    sugar used to have type-safe inferred declaration of lambdas for the body method of
    Widget classes.
    ```
    body = Body[Self](lambda self: text...)
    - OR -
    Body[Self](lambda self: text...)
    ```
    """

    _methods_by_module: dict[str, _BodyCallable[W]] = {}

    @classmethod
    def __call__(cls, method: Callable[[W], Ws]) -> Callable[[W], Ws]:
        # caches the methods in this object, only one class per module can use this syntax as a time

        owning_modname: str = method.__globals__["__name__"]

        # check if there is alreay a method being constructed in a specific module,
        # if not set the entry for the module
        was_already_set = method is not cls._methods_by_module.setdefault(
            owning_modname, method
        )
        if was_already_set:
            raise ValueError(
                f"a Widget class is already being constructed in module {repr(owning_modname)}"
            )

        return method

    def __getitem__(self, type: type[Ws]) -> _BodyDef[Ws]:
        assert self is Body
        return Body

    @classmethod
    def widget_get_body_method(cls, widcls: type[W]) -> _BodyCallable[W] | None:
        return cls._methods_by_module.pop(widcls.__module__, None)


Body: _BodyDef[Any] = _BodyDef()
del _BodyDef


@dataclass_transform(
    eq_default=False,
    order_default=False,
    kw_only_default=False,
    field_specifiers=(_AttrSpec,),
)
class Widget:
    uid: UID

    state_modified: bool  # TODO: evaluate if this is how state updating will happend
    # body: ClassVar[Callable[[W], Ws]] = None  # type: ignore
    if not TYPE_CHECKING:
        body = None

    _arg_specs_: ClassVar[tuple[_AttrSpec, ...]] = ()
    _attr_specs_: ClassVar[dict[str, _AttrSpec]] = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.uid = uid()
        self.state_modified = True
        specs = self._arg_specs_

        assert Missing not in kwargs.values()

        # input sanitization
        if __debug__ and len(args) > len(specs):
            raise TypeError(
                f"{self.__class__.__name__}(...) takes up to {len(specs)} positional "
                + f"arguments ({len(args)} given)"
            )
        if __debug__ and len(kwargs) > (len(specs) - len(args)):
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
        # `body[Self](lambda: ...)` syntax
        bodyattr = Body.widget_get_body_method(cls)

        if (
            "body" not in cls.__dict__ and getattr(cls, "body") is None
        ):  # pyright: reportUnnecessaryComparison=false
            assert bodyattr is not None, (
                f"{cls} missing definition for the body method, use "
                + "`body[Self](lambda self: ...)` syntax"
            )
            setattr(cls, "body", bodyattr)
        else:
            assert (  # None = not defined in the body
                bodyattr is None or bodyattr is getattr(cls, "body")
            ), (f"conflicting definitions for {cls}")

        # --- attributes and arguemnts ---
        # climb the base classes and determine arg order

        attr_specs: dict[str, _AttrSpec] = {}
        new_specs: dict[str, _AttrSpec] = {
            name: spec for name, spec in cls.__dict__.items() if isstatedef(spec)
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
            ), "cannot create an instance of the Widget class, use a subclass"
            return object.__new__(cls)
