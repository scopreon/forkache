import subprocess
import sys


def test_functools_cache_fork():
    program = """
import os
from functools import cache
from forkache import fork_cache_clear

@fork_cache_clear()
@cache
def get_pid():
    return os.getpid()

get_pid()

pid = os.fork()

if pid == 0:
    assert get_pid() == os.getpid()
    os._exit(0)
else:
    _, status = os.waitpid(pid, 0)
    assert os.WEXITSTATUS(status) == 0
"""
    res = subprocess.Popen([sys.executable, "-c", program])
    res.wait()
    assert res.returncode == 0


def test_cachetools_cache_fork():
    program = """
import os
from cachetools import cached, LRUCache
from forkache import fork_cache_clear

@fork_cache_clear()
@cached(cache=LRUCache(maxsize=32))
def get_pid():
    return os.getpid()

get_pid()

pid = os.fork()

if pid == 0:
    assert get_pid() == os.getpid()
    os._exit(0)
else:
    _, status = os.waitpid(pid, 0)
    assert os.WEXITSTATUS(status) == 0
"""
    res = subprocess.Popen([sys.executable, "-c", program])
    res.wait()
    assert res.returncode == 0
