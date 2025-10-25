from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ..schemas.config import AuditEntry


class AuditTrail:
    def __init__(self, audit_path: Path) -> None:
        self.audit_path = audit_path
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, entry: AuditEntry) -> None:
        records = self._read_all()
        records.append(entry.dict())
        self.audit_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def _read_all(self) -> list:
        if not self.audit_path.exists():
            return []
        return json.loads(self.audit_path.read_text(encoding="utf-8"))

    def entries(self) -> Iterable[AuditEntry]:
        for item in self._read_all():
            yield AuditEntry.parse_obj(item)


__all__ = ["AuditTrail"]
