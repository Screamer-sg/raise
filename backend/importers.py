"""Import helpers for CSV payloads."""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import Any, Dict, List


EXPECTED_COLUMNS = {"name", "model", "hostname", "port", "mode", "vlans", "description"}


def import_csv(content: bytes) -> List[Dict[str, Any]]:
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    missing = EXPECTED_COLUMNS.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    grouped: Dict[str, Dict[str, Any]] = {}
    ports: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for row in reader:
        name = row.get("name") or "Imported"
        model = row.get("model") or "unknown"
        hostname = row.get("hostname") or name.lower().replace(" ", "-")
        key = f"{name}:{model}:{hostname}"
        grouped.setdefault(key, {"name": name, "model": model, "hostname": hostname, "ports": []})

        vlan_list = []
        vlan_field = (row.get("vlans") or "").strip()
        if vlan_field:
            for vlan in vlan_field.split(","):
                vlan = vlan.strip()
                if vlan.isdigit():
                    vlan_list.append(int(vlan))

        ports[key].append(
            {
                "id": row.get("port", ""),
                "mode": row.get("mode", "access"),
                "vlans": vlan_list,
                "description": row.get("description", ""),
            }
        )

    payloads: List[Dict[str, Any]] = []
    for key, meta in grouped.items():
        payload = dict(meta)
        payload["ports"] = ports[key]
        payloads.append(payload)
    return payloads


__all__ = ["import_csv", "EXPECTED_COLUMNS"]

