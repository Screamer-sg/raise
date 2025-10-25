from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class ModelCatalog:
    def __init__(self, models_path: Path) -> None:
        self.models_path = models_path
        self._cache: Dict[str, dict] = {}

    def list_models(self) -> List[dict]:
        return [self.get_model(path.stem) for path in sorted(self.models_path.glob("*.json"))]

    def get_model(self, model_id: str) -> dict:
        if model_id not in self._cache:
            path = self.models_path / f"{model_id}.json"
            if not path.exists():
                raise KeyError(f"Model {model_id} not found")
            self._cache[model_id] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[model_id]


__all__ = ["ModelCatalog"]
