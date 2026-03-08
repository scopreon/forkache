"""Cache invalidation utilities for forked processes.

This module provides decorators to automatically clear cached values when a
process forks, preventing child processes from inheriting stale cache entries.
"""

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


class CacheTypeError(TypeError):
    """Raised when a cache clearing method is not found or not callable."""


def fork_cache_clear(
    clear_cache_function_name: str | None = None,
) -> Callable[[CachedFunction[P, T]], CachedFunction[P, T]]:
    """Decorator to automatically clear cache after a process fork.

    Registers a fork handler that clears the cache in child processes,
    preventing them from inheriting stale cached values from the parent.

    Args:
        clear_cache_function_name: Optional name of the cache clearing method.
            If not provided, defaults to checking for 'cache_clear', 'clear',
            or 'delete_memoized' methods in order.

    Returns:
        A decorator function that wraps cached functions.

    Raises:
        CacheTypeError: If the cache clearing method is not found or
            not callable.

    Example:
        >>> from functools import cache
        >>> @fork_cache_clear()
        ... @cache
        ... def my_function(x):
        ...     return x * 2
    """

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
                    f"A cache clearing function in {CACHE_CLEAR_METHODS} "
                    f"was not found as an attribute of "
                    f"{cached_function.__qualname__}"
                )

        os.register_at_fork(after_in_child=clear_cache_function)
        return cached_function

    return _wraps
