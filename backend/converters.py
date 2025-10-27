"""Model conversion helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

import json


@dataclass
class ModelTemplate:
    name: str
    ports: Iterable[Dict[str, Any]]
    features: Iterable[str]
    default_vlan: int

    @classmethod
    def from_dict(cls, name: str, payload: Dict[str, Any]) -> "ModelTemplate":
        return cls(
            name=name,
            ports=payload.get("ports", []),
            features=payload.get("features", []),
            default_vlan=payload.get("default_vlan", 1),
        )


class ModelConverter:
    """Convert configuration payloads between switch models using templates."""

    def __init__(self, template_path: str) -> None:
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Model template file {template_path} not found")
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        self._templates = {
            name: ModelTemplate.from_dict(name, definition)
            for name, definition in payload.get("models", {}).items()
        }
        self._field_map = payload.get("field_mappings", {})

    @property
    def models(self) -> Dict[str, ModelTemplate]:
        return self._templates

    def convert(self, config: Dict[str, Any], target_model: str) -> Dict[str, Any]:
        template = self._templates.get(target_model)
        if template is None:
            raise ValueError(f"Unknown model '{target_model}'")

        converted = {"model": target_model, "ports": [], "features": list(template.features)}

        for field, mapping in self._field_map.items():
            value = self._extract_field(config, mapping)
            if value is not None:
                converted[field] = value

        src_ports = config.get("ports", [])
        template_ports = list(template.ports)
        for idx, port_template in enumerate(template_ports):
            base = dict(port_template)
            if idx < len(src_ports):
                src_port = src_ports[idx]
                base.update({
                    "mode": src_port.get("mode", base.get("type", "access")),
                    "vlans": src_port.get("vlans", [template.default_vlan]),
                    "description": src_port.get("description", "")
                })
            else:
                base.update({"mode": base.get("type", "access"), "vlans": [template.default_vlan], "description": ""})
            converted["ports"].append(base)

        converted.setdefault("hostname", config.get("hostname", f"{target_model.lower()}-switch"))
        converted.setdefault("location", config.get("location", ""))
        converted.setdefault("backups", config.get("backups", []))
        return converted

    def _extract_field(self, payload: Dict[str, Any], dotted_path: str) -> Any:
        parts = dotted_path.split(".")
        value: Any = payload
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value


__all__ = ["ModelConverter", "ModelTemplate"]

