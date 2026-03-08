![PyPI - Version](https://img.shields.io/pypi/v/forkache)

# forkache

A simple cache invalidation library for Python that automatically clears cached values when your process forks.

## Problem

When using `os.fork()` in Python, cached values initialized in the parent process persist in the child process. This can lead to subtle bugs where the child process uses stale cached data that doesn't reflect the current state.

For example:

```python
from functools import cache

@cache
def get_pid():
    return os.getpid()

get_pid()  # Returns parent PID, caches it

pid = os.fork()
if pid == 0:
    # Child process
    get_pid()  # Returns cached parent PID, not the child's PID!
```

## Solution

**forkache** provides a decorator that automatically clears cache entries after a fork occurs, ensuring your child process starts with a clean cache.

```python
from functools import cache
from forkache import fork_cache_clear

@fork_cache_clear()
@cache
def get_pid():
    return os.getpid()

get_pid()  # Returns parent PID, caches it

pid = os.fork()
if pid == 0:
    # Child process
    get_pid()  # Clears cache after fork, returns correct child PID
```

## Installation

```bash
pip install forkache
```

## Usage

### Basic Usage

Use the `@fork_cache_clear()` decorator on your cached functions:

```python
from functools import cache
from forkache import fork_cache_clear

@fork_cache_clear()
@cache
def expensive_operation():
    return compute_something()
```

### Supported Caching Libraries

The decorator works with any caching library that implements a standard cache clearing method:

#### functools
```python
from functools import cache
from forkache import fork_cache_clear

@fork_cache_clear()
@cache
def my_function(x):
    return x * 2
```

#### cachetools
```python
from cachetools import cached, LRUCache
from forkache import fork_cache_clear

@fork_cache_clear()
@cached(cache=LRUCache(maxsize=32))
def my_function(x):
    return x * 2
```

#### Custom Cache Methods

By default, `fork_cache_clear()` looks for cache clearing methods in this order:
- `cache_clear` (functools standard)
- `clear` (common convention)
- `delete_memoized` (memoization libraries)

If your caching library uses a different method name, specify it explicitly:

```python
@fork_cache_clear(clear_cache_function_name="invalidate")
@my_custom_cache_decorator
def my_function(x):
    return x * 2
```

## Requirements

- Python 3.13+
- No external dependencies

## License

MIT
