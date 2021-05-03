from __future__ import annotations

import contextlib
import re
from typing import Any, Callable

import pytest


@contextlib.contextmanager
def xerr(conditions: list[tuple[bool, Exception]]):
    "Like `pytest.raises`, for multiple possible errors"
    check = [e for c, e in conditions if c]
    try:
        yield
    except Exception as e:
        e_str = str(e)
        for match in check:
            if isinstance(e, type(match)) and re.search(str(match), e_str):
                return
        raise
    else:
        if check:
            pytest.fail(
                "DID NOT RAISE ANY OF:\n" + "\n".join(f"* {e!r}" for e in check)
            )


def fails(f: Callable[[], Any]) -> bool:
    "Whether a function raises any error or not"
    try:
        f()
    except Exception:
        return True
    return False


@contextlib.contextmanager
def ignore(*errs: Exception):
    "Suppress any of the given error-patterns"
    try:
        yield
    except Exception as e:
        e_str = str(e)
        for match in errs:
            if isinstance(e, type(match)) and re.search(str(match), e_str):
                return
        raise
