from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


class HTTPException(Exception):
    """Minimal HTTP-style exception used by the simplified FastAPI shim."""

    def __init__(self, status_code: int, detail: Any) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass
class _Route:
    path: str
    methods: Tuple[str, ...]
    endpoint: Callable[..., Any]

    def match(self, method: str, path: str) -> Optional[Dict[str, str]]:
        if method not in self.methods:
            return None
        pattern_parts = _split_path(self.path)
        request_parts = _split_path(path)
        if len(pattern_parts) != len(request_parts):
            return None
        params: Dict[str, str] = {}
        for pattern, value in zip(pattern_parts, request_parts):
            if pattern.startswith("{") and pattern.endswith("}"):
                params[pattern[1:-1]] = value
            elif pattern != value:
                return None
        return params


def _split_path(path: str) -> List[str]:
    stripped = path.strip("/")
    if not stripped:
        return []
    return stripped.split("/")


class FastAPI:
    """Tiny subset of FastAPI sufficient for the unit tests."""

    def __init__(self, title: str = "", version: str = "") -> None:
        self.title = title
        self.version = version
        self._routes: List[_Route] = []
        self._middleware: List[Tuple[type, Dict[str, Any]]] = []

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Iterable[str],
    ) -> None:
        normalized_methods = tuple(method.upper() for method in methods)
        self._routes.append(_Route(path, normalized_methods, endpoint))

    def get(self, path: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, ["GET"])
            return func

        return decorator

    def post(self, path: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, ["POST"])
            return func

        return decorator

    def add_middleware(self, middleware_class: type, **options: Any) -> None:
        self._middleware.append((middleware_class, options))

    def resolve(self, method: str, path: str) -> Tuple[Optional[Callable[..., Any]], Dict[str, str]]:
        method = method.upper()
        for route in self._routes:
            params = route.match(method, path)
            if params is not None:
                return route.endpoint, params
        return None, {}


__all__ = ["FastAPI", "HTTPException"]
