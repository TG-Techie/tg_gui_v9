# Copyright (C) 2023 Jonah 'Jay' Yolles-Murphy (@TG-Techie)
# this file is licensed under the MIT License, see the project root.

# class Spec(Generic[T]):

#     param_name: str
#     is_required: bool
#     types: tuple[type[T], ...]

#     if TYPE_CHECKING:

#         @overload
#         def __new__(
#             cls: type[Self],
#             *,
#             required: Literal[True],
#             types: set[type[T]] | frozenset[type[T]],
#         ) -> T:
#             ...

#         @overload
#         def __new__(
#             cls: type[Self],
#             *,
#             default: T,
#             required: Literal[False] = False,
#         ) -> T:
#             ...

#         @overload
#         def __new__(
#             cls: type[Self],
#             *,
#             default: T,
#             required: Literal[False] = False,
#             types: set[type[T]] | frozenset[type[T]],
#         ) -> T:
#             ...

#     def __new__(
#         cls: type[Self],
#         *,
#         default: _Omittable[T] = _Missing,
#         required: _Omittable[Literal[True, False]] = _Missing,
#         types: _Omittable[set[type[T]] | frozenset[type[T]]] = _Missing,
#     ) -> T:  # DefaultSpec | RequiredParam:

#         # allow normal instantiation of subclasses of Spec
#         if cls is not Spec:
#             return object.__new__(cls)  # pyright: ignore[reportGeneralTypeIssues]

#         if isnotmissing(default):
#             _typed_assert(
#                 required is False or required is _Missing,
#                 TypeError("required arguments cannot have deafult values"),
#             )
#             if types is _Missing:

#                 types = {type(default)}
#             return RequiredSpec(types=types)  # pyright: ignore[reportGeneralTypeIssues]
#         else:
#             _typed_assert(
#                 isnotmissing(types),
#                 TypeError("required arguments must have a types={{..., }} argument"),
#             )
#             return DefaultSpec(types=types)  # pyright: ignore[reportGeneralTypeIssues]
