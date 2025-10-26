from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.config import ConfigMetadata, ConfigRequest, PortConfig, PortMode


def build_request() -> ConfigRequest:
    ports = [
        PortConfig(name="GE1/0/1", mode=PortMode.ACCESS, access_vlan=10),
        PortConfig(name="GE1/0/2", mode=PortMode.TRUNK, trunk_vlans="10,20,30-40"),
        PortConfig(name="GE1/0/3", mode=PortMode.QINQ, qinq_outer=3000, qinq_inner=3010),
    ]
    metadata = ConfigMetadata(model_id="rcs-sw24", model_name="Raisecom RCS-SW24")
    return ConfigRequest(metadata=metadata, ports=ports)


def test_preview_generation(tmp_path: Path, monkeypatch) -> None:
    base_path = tmp_path
    (base_path / "data" / "models").mkdir(parents=True)
    (base_path / "storage" / "profiles").mkdir(parents=True)
    (base_path / "storage" / "audit").mkdir(parents=True)

    model = Path(__file__).resolve().parents[2] / "data" / "models" / "rcs-sw24.json"
    (base_path / "data" / "models" / "rcs-sw24.json").write_text(model.read_text(), encoding="utf-8")

    app = create_app(base_path)
    client = TestClient(app)

    response = client.post("/config/preview", json=build_request().dict())
    assert response.status_code == 200
    payload = response.json()
    assert "cli" in payload
    assert "config_json" in payload
    assert payload["validation"]["is_valid"] is True
