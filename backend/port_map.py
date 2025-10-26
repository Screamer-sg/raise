"""Utilities to build a coloured port map representation."""

from __future__ import annotations

from typing import Any, Dict, List


MODE_COLOURS = {
    "uplink": "#2d8cf0",
    "trunk": "#f0a202",
    "access": "#3bb273",
    "disabled": "#888888",
}


def build_port_map(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    ports = []
    for port in config.get("ports", []):
        mode = port.get("mode", "access")
        ports.append(
            {
                "id": port.get("id", ""),
                "mode": mode,
                "colour": MODE_COLOURS.get(mode, MODE_COLOURS["access"]),
                "vlans": port.get("vlans", []),
                "description": port.get("description", ""),
            }
        )
    return ports


__all__ = ["build_port_map", "MODE_COLOURS"]

