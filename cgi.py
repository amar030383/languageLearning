"""Minimal shim for the stdlib `cgi.parse_header` used by some libraries.

This project-local module is used as a fallback on Python versions where the
`cgi` stdlib module has been removed. It implements a small subset of the
`parse_header` behavior required by `httpx._models` (parse content-type and
extract params like charset).

This is intentionally small and self-contained.
"""
from typing import Tuple, Dict


def parse_header(value: str) -> Tuple[str, Dict[str, str]]:
    """Parse a header like 'text/html; charset=utf-8' into (main, params).

    Returns a tuple (main_value, params_dict). Values and keys are stripped
    and keys are lower-cased. Quoted parameter values will have surrounding
    quotes removed.
    """
    if not value:
        return "", {}

    parts = [p.strip() for p in value.split(";")]
    main = parts[0]
    params: Dict[str, str] = {}

    for p in parts[1:]:
        if not p:
            continue
        if "=" in p:
            k, v = p.split("=", 1)
            k = k.strip().lower()
            v = v.strip()
            if len(v) >= 2 and ((v[0] == v[-1]) and v[0] in "'\""):
                v = v[1:-1]
            params[k] = v
        else:
            # Parameter without value — treat as flag with empty string
            params[p.lower()] = ""

    return main, params


__all__ = ["parse_header"]
