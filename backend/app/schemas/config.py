from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PortMode(str, Enum):
    ACCESS = "access"
    TRUNK = "trunk"
    QINQ = "qinq"
    DISABLED = "disabled"


class PortAdvanced(BaseModel):
    description: Optional[str] = None
    speed: Optional[str] = Field(None, description="Port speed configuration, e.g. auto, 1G")
    duplex: Optional[str] = Field(None, description="Duplex mode, e.g. auto, full, half")
    storm_control: Optional[str] = Field(None, description="Storm control profile name or numeric value")
    comment: Optional[str] = None


class PortConfig(BaseModel):
    name: str
    mode: PortMode
    access_vlan: Optional[int] = Field(None, ge=1, le=4094)
    trunk_vlans: Optional[str] = Field(
        None,
        description="Comma separated VLAN list or ranges (e.g. 10,20,100-110)",
    )
    qinq_outer: Optional[int] = Field(None, ge=1, le=4094)
    qinq_inner: Optional[int] = Field(None, ge=1, le=4094)
    advanced: PortAdvanced = Field(default_factory=PortAdvanced)

    @validator("access_vlan")
    def require_vlan_for_access(cls, value: Optional[int], values: dict) -> Optional[int]:
        if values.get("mode") == PortMode.ACCESS and value is None:
            raise ValueError("Access ports require an access_vlan value")
        return value

    @validator("trunk_vlans")
    def require_trunk_vlans(cls, value: Optional[str], values: dict) -> Optional[str]:
        if values.get("mode") == PortMode.TRUNK and not value:
            raise ValueError("Trunk ports require at least one VLAN in trunk_vlans")
        return value

    @validator("qinq_outer", "qinq_inner")
    def require_qinq_values(cls, value: Optional[int], values: dict, field):
        if values.get("mode") == PortMode.QINQ and value is None:
            raise ValueError(f"QinQ ports require value for {field.name}")
        return value


class ConfigMetadata(BaseModel):
    model_id: str
    model_name: str
    firmware: Optional[str] = None
    author: Optional[str] = None


class ConfigRequest(BaseModel):
    metadata: ConfigMetadata
    ports: List[PortConfig]
    profiles: Optional[List[str]] = Field(default_factory=list)


class ConfigPreview(BaseModel):
    cli: str
    config_json: dict
    config_cfg: str
    validation: "ValidationResult"


class Profile(BaseModel):
    name: str
    encrypted_password: Optional[str] = None
    metadata: ConfigMetadata
    ports: List[PortConfig]


class ValidationMessage(BaseModel):
    level: str
    code: str
    message: str
    port: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool
    messages: List[ValidationMessage] = Field(default_factory=list)


class ConvertRequest(BaseModel):
    source_model: str
    target_model: str
    ports: List[PortConfig]


class DiffRequest(BaseModel):
    left: dict
    right: dict


class AuditEntry(BaseModel):
    timestamp: str
    action: str
    details: dict


ConfigPreview.update_forward_refs()
