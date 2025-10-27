"""Validation helpers for configuration payloads."""

from __future__ import annotations

from typing import Any, Dict, List


class ValidationIssue:
    """A single validation issue."""

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message

    def to_dict(self) -> Dict[str, str]:
        return {"path": self.path, "message": self.message}


class ConfigValidator:
    """Validate configuration payloads to catch common issues."""

    REQUIRED_TOP_LEVEL = ("hostname", "model", "ports")

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[ValidationIssue] = []
        for field in self.REQUIRED_TOP_LEVEL:
            if field not in payload:
                issues.append(ValidationIssue(field, "Field is required"))

        if isinstance(payload.get("ports"), list):
            for index, port in enumerate(payload.get("ports", [])):
                path = f"ports[{index}]"
                if "id" not in port:
                    issues.append(ValidationIssue(f"{path}.id", "Port ID is required"))
                mode = port.get("mode")
                if mode not in {"access", "trunk", "uplink"}:
                    issues.append(ValidationIssue(f"{path}.mode", "Mode must be access, trunk or uplink"))
                vlans = port.get("vlans", [])
                if not isinstance(vlans, list) or not all(isinstance(vlan, int) for vlan in vlans):
                    issues.append(ValidationIssue(f"{path}.vlans", "VLANs must be a list of integers"))
        else:
            issues.append(ValidationIssue("ports", "Ports must be a list"))

        mgmt = payload.get("management", {})
        if isinstance(mgmt, dict):
            for key in ("ip", "mask", "gateway"):
                if key not in mgmt:
                    issues.append(ValidationIssue(f"management.{key}", "Management field is required"))
        else:
            issues.append(ValidationIssue("management", "Management section must be an object"))

        return {"valid": len(issues) == 0, "issues": [issue.to_dict() for issue in issues]}


__all__ = ["ConfigValidator", "ValidationIssue"]

