from typing import Any


def remove_whitespaces(v: Any):
    if isinstance(v, str):
        return v.strip()