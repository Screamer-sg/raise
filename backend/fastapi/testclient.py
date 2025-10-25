from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from . import FastAPI, HTTPException


@dataclass
class _Response:
    status_code: int
    _json: Any

    def json(self) -> Any:
        return self._json


def _serialise(obj: Any) -> Any:
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return {key: _serialise(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialise(value) for value in obj]
    return obj


class TestClient:
    """Very small subset of FastAPI's TestClient used in unit tests."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> _Response:
        return self._request("POST", path, json)

    def get(self, path: str) -> _Response:
        return self._request("GET", path, None)

    def _request(self, method: str, path: str, json: Optional[Dict[str, Any]]) -> _Response:
        endpoint, params = self.app.resolve(method, path)
        if endpoint is None:
            return _Response(404, {"detail": "Not Found"})

        kwargs: Dict[str, Any] = params.copy()
        if json is not None:
            signature = inspect.signature(endpoint)
            for name, parameter in signature.parameters.items():
                if name in kwargs:
                    continue
                annotation: Type[Any] | str = parameter.annotation
                if isinstance(annotation, str):
                    annotation = endpoint.__globals__.get(annotation, annotation)
                if hasattr(annotation, "from_dict"):
                    kwargs[name] = annotation.from_dict(json)
                else:
                    kwargs[name] = json
                break

        try:
            result = endpoint(**kwargs)
        except HTTPException as exc:  # pragma: no cover - simple error path
            return _Response(exc.status_code, {"detail": exc.detail})

        return _Response(200, _serialise(result))


__all__ = ["TestClient"]
