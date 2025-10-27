"""Utilities for persisting and manipulating switch configuration profiles."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ConfigProfile:
    """Representation of a configuration profile stored on disk."""

    id: str
    name: str
    model: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "model": self.model, "data": self.data}


class ConfigManager:
    """Handle CRUD operations for configuration profiles backed by JSON files."""

    def __init__(self, storage_path: str) -> None:
        self._path = Path(storage_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]\n", encoding="utf-8")
        self._lock = threading.Lock()

    def _load(self) -> List[ConfigProfile]:
        with self._path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        return [ConfigProfile(**item) for item in raw]

    def _save(self, profiles: List[ConfigProfile]) -> None:
        serialised = [profile.to_dict() for profile in profiles]
        with self._path.open("w", encoding="utf-8") as fh:
            json.dump(serialised, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    def list_profiles(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [profile.to_dict() for profile in self._load()]

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for profile in self._load():
                if profile.id == profile_id:
                    return profile.to_dict()
        return None

    def create_profile(self, name: str, model: str, data: Dict[str, Any]) -> Dict[str, Any]:
        profile = ConfigProfile(id=str(uuid.uuid4()), name=name, model=model, data=data)
        with self._lock:
            profiles = self._load()
            profiles.append(profile)
            self._save(profiles)
        return profile.to_dict()

    def update_profile(self, profile_id: str, *, name: Optional[str] = None, model: Optional[str] = None,
                        data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        with self._lock:
            profiles = self._load()
            for idx, profile in enumerate(profiles):
                if profile.id == profile_id:
                    if name is not None:
                        profile.name = name
                    if model is not None:
                        profile.model = model
                    if data is not None:
                        profile.data = data
                    profiles[idx] = profile
                    self._save(profiles)
                    return profile.to_dict()
        return None

    def delete_profile(self, profile_id: str) -> bool:
        with self._lock:
            profiles = self._load()
            filtered = [profile for profile in profiles if profile.id != profile_id]
            if len(filtered) == len(profiles):
                return False
            self._save(filtered)
        return True

    def upsert_from_dict(self, profile_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing profile if the ID matches, otherwise create a new record."""

        profile_id = profile_dict.get("id")
        name = profile_dict.get("name", "Imported profile")
        model = profile_dict.get("model", "unknown")
        data = profile_dict.get("data", {})

        if profile_id:
            updated = self.update_profile(profile_id, name=name, model=model, data=data)
            if updated is not None:
                return updated
        return self.create_profile(name, model, data)


__all__ = ["ConfigManager", "ConfigProfile"]

