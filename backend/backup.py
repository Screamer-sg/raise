"""Daily backup scheduling for configuration profiles."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class BackupScheduler:
    """Periodically capture a snapshot of the configuration file."""

    def __init__(self, source_file: str, backup_dir: str, *, interval: timedelta | None = None) -> None:
        self._source = Path(source_file)
        self._backup_dir = Path(backup_dir)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._interval = interval or timedelta(days=1)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="BackupScheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop.wait(self._interval.total_seconds()):
            self.perform_backup()

    def perform_backup(self) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        target = self._backup_dir / f"profiles-{timestamp}.json"
        if not self._source.exists():
            target.write_text("[]\n", encoding="utf-8")
            return target
        data = json.loads(self._source.read_text(encoding="utf-8"))
        target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return target

    def run_now(self) -> Path:
        return self.perform_backup()


__all__ = ["BackupScheduler"]

