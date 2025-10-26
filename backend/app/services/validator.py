from __future__ import annotations

from collections import Counter
from typing import Iterable, List

from ..schemas.config import ConfigRequest, PortConfig, PortMode, ValidationMessage, ValidationResult
from ..utils.models import ModelCatalog


class ConfigValidator:
    def __init__(self, catalog: ModelCatalog) -> None:
        self.catalog = catalog

    def validate(self, request: ConfigRequest) -> ValidationResult:
        messages: List[ValidationMessage] = []
        model = self.catalog.get_model(request.metadata.model_id)
        port_names = {port["name"] for port in model["ports"]}

        messages.extend(self._validate_port_names(request.ports, port_names))
        messages.extend(self._validate_vlan_ranges(request.ports))
        messages.extend(self._validate_qinq(request.ports))

        return ValidationResult(is_valid=not any(m.level == "error" for m in messages), messages=messages)

    def _validate_port_names(self, ports: Iterable[PortConfig], allowed_names: set[str]) -> List[ValidationMessage]:
        messages: List[ValidationMessage] = []
        seen = Counter()
        for port in ports:
            seen[port.name] += 1
            if port.name not in allowed_names:
                messages.append(
                    ValidationMessage(
                        level="error",
                        code="port.invalid",
                        message=f"Port {port.name} is not available on the selected model",
                        port=port.name,
                    )
                )
        for port_name, count in seen.items():
            if count > 1:
                messages.append(
                    ValidationMessage(
                        level="error",
                        code="port.duplicate",
                        message=f"Port {port_name} is configured more than once",
                        port=port_name,
                    )
                )
        return messages

    def _validate_vlan_ranges(self, ports: Iterable[PortConfig]) -> List[ValidationMessage]:
        messages: List[ValidationMessage] = []
        for port in ports:
            if port.mode == PortMode.TRUNK and port.trunk_vlans:
                for segment in port.trunk_vlans.split(","):
                    segment = segment.strip()
                    if not segment:
                        continue
                    if "-" in segment:
                        start, _, end = segment.partition("-")
                        if not (start.isdigit() and end.isdigit() and 1 <= int(start) <= int(end) <= 4094):
                            messages.append(
                                ValidationMessage(
                                    level="error",
                                    code="vlan.range",
                                    message=f"Invalid VLAN range '{segment}' on {port.name}",
                                    port=port.name,
                                )
                            )
                    elif not segment.isdigit() or not 1 <= int(segment) <= 4094:
                        messages.append(
                            ValidationMessage(
                                level="error",
                                code="vlan.value",
                                message=f"Invalid VLAN '{segment}' on {port.name}",
                                port=port.name,
                            )
                        )
        return messages

    def _validate_qinq(self, ports: Iterable[PortConfig]) -> List[ValidationMessage]:
        messages: List[ValidationMessage] = []
        for port in ports:
            if port.mode == PortMode.QINQ:
                if port.qinq_outer == port.qinq_inner:
                    messages.append(
                        ValidationMessage(
                            level="warning",
                            code="qinq.same",
                            message=f"Outer and inner VLANs are identical on {port.name}",
                            port=port.name,
                        )
                    )
                for value in (port.qinq_outer, port.qinq_inner):
                    if value is None or not 1 <= value <= 4094:
                        messages.append(
                            ValidationMessage(
                                level="error",
                                code="qinq.invalid",
                                message=f"QinQ VLAN {value} out of range on {port.name}",
                                port=port.name,
                            )
                        )
        return messages
