from __future__ import annotations

from pathlib import Path
from typing import Dict, List

try:  # pragma: no cover - exercised indirectly via imports
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ModuleNotFoundError:  # pragma: no cover
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware

from .schemas.config import (
    ConfigPreview,
    ConfigRequest,
    ConvertRequest,
    DiffRequest,
    Profile,
    ValidationResult,
)
from .services.configurator import ConfiguratorService
from .utils.audit import AuditTrail
from .utils.crypto import CryptoService


def get_service(base_path: Path | None = None) -> ConfiguratorService:
    if base_path is None:
        base_path = Path(__file__).resolve().parents[2]
    models_path = base_path / "data" / "models"
    storage_path = base_path / "storage"
    crypto = CryptoService()
    audit = AuditTrail(storage_path / "audit" / "audit.json")
    return ConfiguratorService(models_path, storage_path, crypto, audit)


def create_app(base_path: Path | None = None) -> FastAPI:
    app = FastAPI(title="Raisecom Configurator", version="6.2")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    service = get_service(base_path)

    @app.get("/models")
    def list_models() -> List[dict]:
        return service.list_models()

    @app.get("/models/{model_id}")
    def get_model(model_id: str) -> dict:
        try:
            return service.get_model(model_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/config/preview", response_model=ConfigPreview)
    def preview(request: ConfigRequest) -> ConfigPreview:
        return service.generate(request)

    @app.post("/config/validate", response_model=ValidationResult)
    def validate(request: ConfigRequest) -> ValidationResult:
        return service.validator.validate(request)

    @app.post("/config/convert")
    def convert(request: ConvertRequest) -> List[dict]:
        ports = service.convert(request.source_model, request.target_model, request.ports)
        return [port.dict() for port in ports]

    @app.post("/profiles", response_model=Profile)
    def create_profile(profile: Profile) -> Profile:
        return service.save_profile(profile)

    @app.get("/profiles", response_model=List[str])
    def list_profiles() -> List[str]:
        return service.list_profiles()

    @app.get("/profiles/{name}", response_model=Profile)
    def load_profile(name: str) -> Profile:
        try:
            return service.load_profile(name)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/profiles/backup")
    def backup_profiles() -> Dict[str, dict]:
        return service.backup_profiles()

    @app.post("/profiles/restore")
    def restore_profiles(payload: Dict[str, dict]) -> Dict[str, List[str]]:
        service.restore_profiles(payload)
        return {"restored": list(payload)}

    @app.post("/config/diff")
    def diff(request: DiffRequest) -> Dict[str, str]:
        return {"diff": service.diff(request.left, request.right)}

    @app.get("/audit")
    def audit_log() -> List[dict]:
        return [entry.dict() for entry in service.audit_trail.entries()]

    return app


app = create_app()
