import os
from typing import ParamSpec, TypeAlias, TypeVar, Callable

P = ParamSpec("P")
T = TypeVar("T")

CachedFunction: TypeAlias = Callable[P, T]


CACHE_CLEAR_METHODS = (
    "cache_clear",
    "clear",
    "delete_memoized",
)


class CacheTypeError(TypeError): ...


def fork_cache_clear(
    clear_cache_function_name: str | None = None,
) -> Callable[[CachedFunction[P, T]], CachedFunction[P, T]]:
    def _wraps(cached_function: CachedFunction[P, T]) -> CachedFunction[P, T]:
        clear_cache_function = None
        if clear_cache_function_name is not None:
            clear_cache_function = getattr(
                cached_function, clear_cache_function_name, None
            )
            if not callable(clear_cache_function):
                raise CacheTypeError(
                    "The cache clearing function "
                    f"`{clear_cache_function_name}` was not found as "
                    f"an attribute of {cached_function.__qualname__}"
                )
        else:
            for method in CACHE_CLEAR_METHODS:
                clear_cache_function = getattr(cached_function, method, None)
                if callable(clear_cache_function):
                    break
            if not callable(clear_cache_function):
                raise CacheTypeError(
                    f"A cache clearing function in {CACHE_CLEAR_METHODS} was"
                    f"not as an attribute of {cached_function.__qualname__}"
                )

        os.register_at_fork(after_in_child=clear_cache_function)
        return cached_function

    return _wraps
