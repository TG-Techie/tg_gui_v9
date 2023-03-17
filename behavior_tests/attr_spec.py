# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

from __future__ import annotations

from shared import uid, Missing, isnotmissing

from typing import (
    TYPE_CHECKING,
    TypeVar,
    runtime_checkable,
    dataclass_transform,
    Protocol,
)

if TYPE_CHECKING:
    from .shared import UID, Maybe

    from typing import (
        Any,
        overload,
        TypeVar,
        ClassVar,
        Callable,
        Literal,
    )

    AnyCallable = Callable[..., Any]
else:
    AnyCallable = object

A = TypeVar("A", bound="AttrSpecified")
T = TypeVar("T")
S = TypeVar("S")

if TYPE_CHECKING:
    _TypeID = str if __debug__ else int


def _class_id_hash(t: type) -> _TypeID:
    explicit = f"({t.__module__}:{t.__qualname__}>)"
    return explicit if __debug__ else hash(explicit)


def _type_id_from_frozen_types(types: tuple[type, ...]) -> _TypeID:
    assert (
        tuple(sorted(types, key=_class_id_hash)) == types
    ), "for the purpose of class IDs, 'frozen types' must tuples of types sorted by _class_id_hash"
    if __debug__:
        return f"({''.join(map(str, map(_class_id_hash, types)))})"
    else:
        return hash(types)


@runtime_checkable
class Spec(Protocol):

    uid: UID
    param_name: str
    owning_type: type[AttrSpecified]

    def init_self(
        self,
    ) -> None:
        self.uid = uid()

    def on_get_attr(self, inst: Any, stored: Maybe[T]) -> T:
        if isnotmissing(stored):
            return stored
        else:
            raise AttributeError(f"{inst} missing attribute {self.param_name}")

    def on_set_attr(self, inst: Any, old_value: Maybe[T], new_value: T) -> T:
        return new_value

    # type-hinting tricks
    if TYPE_CHECKING:
        """
        add type-checking alias to make assigning attrs in the widget body type-safe
        ex:
        ```
        class SomeWidget(...):
            # with this
            myvar = SomeSpec(default=5 ,types={int, None})
            # without this
            myvar: None | int = SomeSpec(default=5) # type: ignore
        ```
        """

        def __new__(
            cls,
            init: Literal[False],
        ) -> Any:
            ...

    else:

        def __init__(self, *args, **kwargs) -> None:
            self.init_self(*args, **kwargs)

    def __get__(self, inst: T, _: type[T] | None = None) -> Any:

        assert hasattr(
            self, "param_name"
        ), f"{self} spec, of type {self.__class__}, used before initialized"

        return self.on_get_attr(inst, getattr(inst, ":" + self.param_name, Missing))

    def __set__(self, inst: Any, value: Any) -> Any:
        assert hasattr(
            self, "param_name"
        ), f"{self} spec, of type {self.__class__}, used before initialized"

        setattr(
            inst,
            self.on_set_attr(
                inst, getattr(inst, ":" + self.param_name, Missing), value
            ),
            ":" + self.param_name,
        )

    def __set_name__(self, owner: type[AttrSpecified], name: str) -> None:
        if not hasattr(self, self.param_name):
            self.param_name = name
            self.owning_type = owner
        else:
            raise RuntimeError(
                f"{self}.__set_name__(...) already "
                + "set to {repr(name)}, cannot set to {repr(name)}"
            )


class ParamSpec(Spec):

    kw_only: bool
    is_required: bool
    default_value: Maybe[Any] = Missing
    default_factory: Maybe[Callable[[], Any]] = Missing

    @property
    def in_init(self) -> Literal[True]:
        return True

    def on_init(self, passed: Maybe[T]) -> Maybe[T]:
        if self.is_required:
            if isnotmissing(passed):
                return passed
            else:
                raise TypeError(f"missing required argument {self.param_name}")
        elif isnotmissing(self.default_value):
            return self.default_value
        elif isnotmissing(self.default_factory):
            return self.default_factory()
        else:
            raise RuntimeError(
                "invalid internal state for spec object, "
                + f"param_name={repr(getattr(self, 'param_name', '<not found>'))}, "
                + f"owning_type={repr(getattr(self, 'owning_type', '<not found>'))}"
            )

    if TYPE_CHECKING:

        @overload
        def __new__(
            cls,
            *,
            default: T,
            required: Literal[False] = False,
            kw_only: Literal[True] = True,
            init: Literal[True] = True,
        ) -> T:
            ...

        @overload
        def __new__(
            cls,
            *,
            default_factory: Callable[[], T],
            required: Literal[False] = False,
            kw_only: Literal[True] = True,
            init: Literal[True] = True,
        ) -> T:
            ...

        @overload
        def __new__(
            cls,
            *,
            required: Literal[True],
            kw_only: bool = True,
            init: Literal[True] = True,
        ) -> Any:
            ...

        def __new__(
            cls,
            *,
            required: Maybe[bool] = Missing,
            default: Maybe[T] = Missing,
            default_factory: Maybe[Callable[[], T]] = Missing,
            kw_only: Maybe[bool] = Missing,
            init: Literal[True] = True,
        ) -> T:
            ...

    def init_self(
        self,
        kw_only: bool = True,
        init: Literal[True] = True,
    ) -> None:
        self.kw_only = kw_only
        super().init_self()


@dataclass_transform(
    eq_default=False,
    order_default=False,
    # kw_only_default=True,
    field_specifiers=(Spec,),
)
class AttrSpecified:

    _pos_arg_specs_: ClassVar[tuple[Spec, ...]]
    _kw_arg_specs_: ClassVar[dict[str, Spec]]

    def __init_subclass__(cls) -> None:
        """
        pre-processes the declarations in a class's  body prior to it's execution.
        """

        # extract all the newly declared specs
        specs: dict[str, Spec] = {
            n: s for n, s in cls.__dict__.items() if isinstance(s, Spec)
        }

        # pull out the init specs into the two kinds
        pos_args: list[Spec] = []
        pos_arg_names: set[str] = set()
        kwargs: dict[str, Spec] = {}

        for name, spec in specs.items():
            if not isinstance(spec, ParamSpec):
                continue

            # add based on kind
            if spec.kw_only:
                kwargs[name] = spec
            else:
                pos_args.append(spec)
                pos_arg_names.add(name)

        # order based on declaration order
        pos_args.sort(
            key=lambda a: a.uid,
        )

        # compile the args and kwargs, newer specs will override older ones.
        for base in cls.__bases__:
            if not issubclass(base, AttrSpecified):
                continue
            pos_args += [
                spec
                for spec in base._pos_arg_specs_  # pyright: ignore[reportPrivateUsage]
                if spec.param_name not in pos_arg_names
            ]
            pos_arg_names = set(s.param_name for s in pos_args)
            assert len(pos_args) == len(pos_arg_names)

            kwargs.update(
                {
                    n: s
                    for n, s in base._kw_arg_specs_.items()  # pyright: ignore[reportPrivateUsage]
                    if n not in kwargs
                }
            )

        # make sure to update the object
        cls._pos_arg_specs_ = tuple(pos_args)  # pyright: ignore[reportPrivateUsage]
        cls._kw_arg_specs_ = kwargs  # pyright: ignore[reportPrivateUsage]

        # return cls

    def __init__(self, *args: Any, **kwargs: Any):
        assert (
            "_pos_arg_specs_" in self.__class__.__dict__
            and "_kw_arg_specs_" in self.__class__.__dict__
        ), "Widget class not decorated, add @widget"

        if len(args) != len(self._pos_arg_specs_):
            raise TypeError(
                f"{self.__class__.__name__} expects {len(self._pos_arg_specs_)} "
                + f"positional arguments, got {len(args)}"
            )

        kw_arg_specs = self._kw_arg_specs_
        if any((extra_kw := kw) not in kwargs for kw in kw_arg_specs):
            raise TypeError(
                f"{self.__class__.__name__}: unexpect keyword argument '{extra_kw}'"
            )

        raise NotImplemented
