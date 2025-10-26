"""Utilities to export configuration profiles to various formats."""

from __future__ import annotations

import json
from typing import Any, Dict


def to_cli(config: Dict[str, Any]) -> str:
    lines = [f"configure terminal", f"hostname {config.get('hostname', 'switch')}"]
    management = config.get("management", {})
    if management:
        ip = management.get("ip")
        mask = management.get("mask")
        gateway = management.get("gateway")
        if ip and mask:
            lines.append(f"interface vlan 1")
            lines.append(f" ip address {ip} {mask}")
            lines.append(" exit")
        if gateway:
            lines.append(f"ip default-gateway {gateway}")

    for port in config.get("ports", []):
        port_id = port.get("id")
        if not port_id:
            continue
        lines.append(f"interface {port_id}")
        mode = port.get("mode", "access")
        if mode == "access":
            vlan = next(iter(port.get("vlans", [])), None)
            if vlan is not None:
                lines.append(f" switchport access vlan {vlan}")
        elif mode == "trunk":
            vlan_list = ",".join(str(vlan) for vlan in port.get("vlans", []))
            if vlan_list:
                lines.append(f" switchport trunk allowed vlan {vlan_list}")
        description = port.get("description")
        if description:
            lines.append(f" description {description}")
        lines.append(" exit")

    lines.append("end")
    return "\n".join(lines) + "\n"


def to_cfg(config: Dict[str, Any]) -> str:
    lines = ["# Raisecom configuration", f"hostname={config.get('hostname', 'switch')}"]
    management = config.get("management", {})
    for key in ("ip", "mask", "gateway"):
        if key in management:
            lines.append(f"management_{key}={management[key]}")
    for index, port in enumerate(config.get("ports", []), start=1):
        prefix = f"port{index}"
        for field in ("id", "mode", "vlans", "description"):
            value = port.get(field)
            if value is not None:
                if isinstance(value, list):
                    value = ",".join(str(item) for item in value)
                lines.append(f"{prefix}_{field}={value}")
    return "\n".join(lines) + "\n"


def to_json(config: Dict[str, Any]) -> str:
    return json.dumps(config, indent=2, ensure_ascii=False) + "\n"


EXPORTERS = {
    "cli": to_cli,
    "cfg": to_cfg,
    "json": to_json,
}


def export_config(config: Dict[str, Any], fmt: str) -> str:
    if fmt not in EXPORTERS:
        raise ValueError(f"Unsupported export format '{fmt}'")
    return EXPORTERS[fmt](config)


__all__ = ["export_config", "EXPORTERS", "to_cli", "to_cfg", "to_json"]

