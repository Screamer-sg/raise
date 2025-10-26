from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from ..schemas.config import (
    AuditEntry,
    ConfigPreview,
    ConfigRequest,
    PortConfig,
    PortMode,
    Profile,
)
from .validator import ConfigValidator
from ..utils.crypto import CryptoService
from ..utils.models import ModelCatalog
from ..utils.audit import AuditTrail
from ..utils.diff import diff_configs


@dataclass
class GeneratedConfig:
    cli: str
    config_json: dict
    config_cfg: str


class ConfiguratorService:
    def __init__(
        self,
        models_path: Path,
        storage_path: Path,
        crypto_service: CryptoService,
        audit_trail: AuditTrail,
    ) -> None:
        self.catalog = ModelCatalog(models_path)
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.crypto_service = crypto_service
        self.validator = ConfigValidator(self.catalog)
        self.audit_trail = audit_trail
        self.profile_path = storage_path / "profiles"
        self.profile_path.mkdir(parents=True, exist_ok=True)

    def list_models(self) -> List[dict]:
        return self.catalog.list_models()

    def get_model(self, model_id: str) -> dict:
        return self.catalog.get_model(model_id)

    # generation logic
    def generate(self, request: ConfigRequest) -> ConfigPreview:
        validation = self.validator.validate(request)
        cli = self._build_cli(request.ports)
        cfg = self._build_cfg(request)
        config_json = json.loads(json.dumps(cfg))  # deep copy

        preview = ConfigPreview(
            cli=cli,
            config_json=config_json,
            config_cfg=self._format_cfg(cfg),
            validation=validation,
        )

        self.audit_trail.write(
            AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action="generate",
                details={"model": request.metadata.model_id, "valid": validation.is_valid},
            )
        )
        return preview

    def convert(self, source_model: str, target_model: str, ports: Iterable[PortConfig]) -> List[PortConfig]:
        source = self.catalog.get_model(source_model)
        target = self.catalog.get_model(target_model)
        target_ports = [p["name"] for p in target["ports"]]

        converted: List[PortConfig] = []
        for idx, port in enumerate(ports):
            try:
                target_name = target_ports[idx]
            except IndexError:
                break
            updated_data = port.dict()
            updated_data["name"] = target_name
            converted.append(PortConfig.from_dict(updated_data))

        self.audit_trail.write(
            AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action="convert",
                details={"source": source_model, "target": target_model, "count": len(converted)},
            )
        )
        return converted

    def save_profile(self, profile: Profile) -> Profile:
        if profile.encrypted_password and not profile.encrypted_password.startswith("enc::"):
            profile.encrypted_password = self.crypto_service.encrypt(profile.encrypted_password)

        path = self.profile_path / f"{profile.name}.json"
        path.write_text(json.dumps(profile.dict(), indent=2), encoding="utf-8")

        self.audit_trail.write(
            AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action="save_profile",
                details={"profile": profile.name},
            )
        )
        return profile

    def list_profiles(self) -> List[str]:
        return sorted(p.stem for p in self.profile_path.glob("*.json"))

    def load_profile(self, name: str) -> Profile:
        path = self.profile_path / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(name)
        data = json.loads(path.read_text(encoding="utf-8"))
        return Profile.from_dict(data)

    def backup_profiles(self) -> Dict[str, dict]:
        return {
            p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in self.profile_path.glob("*.json")
        }

    def restore_profiles(self, payload: Dict[str, dict]) -> None:
        for name, data in payload.items():
            path = self.profile_path / f"{name}.json"
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.audit_trail.write(
            AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action="restore_profiles",
                details={"profiles": list(payload)},
            )
        )

    def diff(self, left: dict, right: dict) -> str:
        return diff_configs(left, right)

    def _build_cli(self, ports: Iterable[PortConfig]) -> str:
        lines: List[str] = []
        for port in ports:
            lines.extend(self._port_to_cli(port))
        return "\n".join(lines)

    def _build_cfg(self, request: ConfigRequest) -> dict:
        return {
            "metadata": request.metadata.dict(),
            "ports": [self._port_to_dict(port) for port in request.ports],
            "profiles": request.profiles,
        }

    def _format_cfg(self, cfg: dict) -> str:
        lines = ["configuration", f" model {cfg['metadata']['model_id']}"]
        for port in cfg["ports"]:
            lines.append(f" interface {port['name']}")
            lines.append(f"  mode {port['mode']}")
            if port["mode"] == PortMode.ACCESS.value and port.get("access_vlan"):
                lines.append(f"  access vlan {port['access_vlan']}")
            if port["mode"] == PortMode.TRUNK.value and port.get("trunk_vlans"):
                lines.append(f"  trunk allow {port['trunk_vlans']}")
            if port["mode"] == PortMode.QINQ.value:
                lines.append(f"  qinq outer {port.get('qinq_outer', '')}")
                lines.append(f"  qinq inner {port.get('qinq_inner', '')}")
            adv = port.get("advanced", {})
            if adv.get("description"):
                lines.append(f"  description {adv['description']}")
            if adv.get("speed"):
                lines.append(f"  speed {adv['speed']}")
            if adv.get("duplex"):
                lines.append(f"  duplex {adv['duplex']}")
            if adv.get("storm_control"):
                lines.append(f"  storm-control {adv['storm_control']}")
            if adv.get("comment"):
                lines.append(f"  comment {adv['comment']}")
            lines.append(" exit")
        lines.append("end")
        return "\n".join(lines)

    def _port_to_cli(self, port: PortConfig) -> List[str]:
        lines = [f"interface {port.name}", f" switchport mode {port.mode.value}"]
        if port.mode == PortMode.ACCESS and port.access_vlan:
            lines.append(f" switchport access vlan {port.access_vlan}")
        if port.mode == PortMode.TRUNK and port.trunk_vlans:
            lines.append(f" switchport trunk allowed vlan {port.trunk_vlans}")
        if port.mode == PortMode.QINQ and port.qinq_outer and port.qinq_inner:
            lines.append(f" switchport qinq outer {port.qinq_outer}")
            lines.append(f" switchport qinq inner {port.qinq_inner}")
        if port.advanced.description:
            lines.append(f" description {port.advanced.description}")
        if port.advanced.speed:
            lines.append(f" speed {port.advanced.speed}")
        if port.advanced.duplex:
            lines.append(f" duplex {port.advanced.duplex}")
        if port.advanced.storm_control:
            lines.append(f" storm-control {port.advanced.storm_control}")
        if port.advanced.comment:
            lines.append(f" ! {port.advanced.comment}")
        lines.append(" exit")
        return lines

    def _port_to_dict(self, port: PortConfig) -> dict:
        data = port.dict()
        data["mode"] = port.mode.value
        return data


__all__ = ["ConfiguratorService", "GeneratedConfig"]
