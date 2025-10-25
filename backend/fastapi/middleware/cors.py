from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List


@dataclass
class CORSMiddleware:
    """No-op middleware placeholder used by the FastAPI shim."""

    allow_origins: Iterable[str]
    allow_credentials: bool
    allow_methods: Iterable[str]
    allow_headers: Iterable[str]

    def __init__(
        self,
        allow_origins: Iterable[str],
        allow_credentials: bool,
        allow_methods: Iterable[str],
        allow_headers: Iterable[str],
        **_: Any,
    ) -> None:
        self.allow_origins = list(allow_origins)
        self.allow_credentials = allow_credentials
        self.allow_methods = list(allow_methods)
        self.allow_headers = list(allow_headers)


__all__: List[str] = ["CORSMiddleware"]
