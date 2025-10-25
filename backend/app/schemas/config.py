from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PortMode(str, Enum):
    ACCESS = "access"
    TRUNK = "trunk"
    QINQ = "qinq"
    DISABLED = "disabled"

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.value


@dataclass
class PortAdvanced:
    description: Optional[str] = None
    speed: Optional[str] = None
    duplex: Optional[str] = None
    storm_control: Optional[str] = None
    comment: Optional[str] = None

    def dict(self) -> Dict[str, Optional[str]]:
        return {
            "description": self.description,
            "speed": self.speed,
            "duplex": self.duplex,
            "storm_control": self.storm_control,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Optional[str]]] = None) -> "PortAdvanced":
        data = data or {}
        return cls(
            description=data.get("description"),
            speed=data.get("speed"),
            duplex=data.get("duplex"),
            storm_control=data.get("storm_control"),
            comment=data.get("comment"),
        )


@dataclass
class PortConfig:
    name: str
    mode: PortMode
    access_vlan: Optional[int] = None
    trunk_vlans: Optional[str] = None
    qinq_outer: Optional[int] = None
    qinq_inner: Optional[int] = None
    advanced: PortAdvanced = field(default_factory=PortAdvanced)

    def dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "mode": self.mode.value,
            "access_vlan": self.access_vlan,
            "trunk_vlans": self.trunk_vlans,
            "qinq_outer": self.qinq_outer,
            "qinq_inner": self.qinq_inner,
            "advanced": self.advanced.dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "PortConfig":
        mode = data.get("mode")
        if isinstance(mode, PortMode):
            port_mode = mode
        else:
            port_mode = PortMode(str(mode))
        advanced = PortAdvanced.from_dict(data.get("advanced"))
        return cls(
            name=str(data.get("name")),
            mode=port_mode,
            access_vlan=_maybe_int(data.get("access_vlan")),
            trunk_vlans=_maybe_str(data.get("trunk_vlans")),
            qinq_outer=_maybe_int(data.get("qinq_outer")),
            qinq_inner=_maybe_int(data.get("qinq_inner")),
            advanced=advanced,
        )


@dataclass
class ConfigMetadata:
    model_id: str
    model_name: str
    firmware: Optional[str] = None
    author: Optional[str] = None

    def dict(self) -> Dict[str, Optional[str]]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "firmware": self.firmware,
            "author": self.author,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ConfigMetadata":
        return cls(
            model_id=str(data.get("model_id")),
            model_name=str(data.get("model_name")),
            firmware=_maybe_str(data.get("firmware")),
            author=_maybe_str(data.get("author")),
        )


@dataclass
class ConfigRequest:
    metadata: ConfigMetadata
    ports: List[PortConfig]
    profiles: List[str] = field(default_factory=list)

    def dict(self) -> Dict[str, object]:
        return {
            "metadata": self.metadata.dict(),
            "ports": [port.dict() for port in self.ports],
            "profiles": list(self.profiles),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ConfigRequest":
        metadata = ConfigMetadata.from_dict(data["metadata"])
        ports = [PortConfig.from_dict(port) for port in data.get("ports", [])]
        profiles = [str(p) for p in data.get("profiles", [])]
        return cls(metadata=metadata, ports=ports, profiles=profiles)


@dataclass
class Profile:
    name: str
    metadata: ConfigMetadata
    ports: List[PortConfig]
    encrypted_password: Optional[str] = None

    def dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "metadata": self.metadata.dict(),
            "ports": [port.dict() for port in self.ports],
            "encrypted_password": self.encrypted_password,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Profile":
        return cls(
            name=str(data.get("name")),
            metadata=ConfigMetadata.from_dict(data["metadata"]),
            ports=[PortConfig.from_dict(port) for port in data.get("ports", [])],
            encrypted_password=_maybe_str(data.get("encrypted_password")),
        )


@dataclass
class ValidationMessage:
    level: str
    code: str
    message: str
    port: Optional[str] = None

    def dict(self) -> Dict[str, Optional[str]]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "port": self.port,
        }


@dataclass
class ValidationResult:
    is_valid: bool
    messages: List[ValidationMessage] = field(default_factory=list)

    def dict(self) -> Dict[str, object]:
        return {
            "is_valid": self.is_valid,
            "messages": [message.dict() for message in self.messages],
        }


@dataclass
class ConfigPreview:
    cli: str
    config_json: Dict[str, object]
    config_cfg: str
    validation: ValidationResult

    def dict(self) -> Dict[str, object]:
        return {
            "cli": self.cli,
            "config_json": self.config_json,
            "config_cfg": self.config_cfg,
            "validation": self.validation.dict(),
        }


@dataclass
class ConvertRequest:
    source_model: str
    target_model: str
    ports: List[PortConfig]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "ConvertRequest":
        return cls(
            source_model=str(data.get("source_model")),
            target_model=str(data.get("target_model")),
            ports=[PortConfig.from_dict(port) for port in data.get("ports", [])],
        )


@dataclass
class DiffRequest:
    left: Dict[str, object]
    right: Dict[str, object]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "DiffRequest":
        return cls(left=dict(data.get("left", {})), right=dict(data.get("right", {})))


@dataclass
class AuditEntry:
    timestamp: str
    action: str
    details: Dict[str, object]

    def dict(self) -> Dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "details": dict(self.details),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "AuditEntry":
        return cls(
            timestamp=str(data.get("timestamp")),
            action=str(data.get("action")),
            details=dict(data.get("details", {})),
        )


def _maybe_int(value: object) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None


def _maybe_str(value: object) -> Optional[str]:
    if value is None:
        return None
    return str(value)


__all__ = [
    "PortMode",
    "PortAdvanced",
    "PortConfig",
    "ConfigMetadata",
    "ConfigRequest",
    "ConfigPreview",
    "Profile",
    "ValidationMessage",
    "ValidationResult",
    "ConvertRequest",
    "DiffRequest",
    "AuditEntry",
]
