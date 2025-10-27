"""Flask entry-point for the Raisecom Configurator backend."""

from __future__ import annotations

import atexit
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from .backup import BackupScheduler
from .config_manager import ConfigManager
from .connections import ConnectionError, run_serial_session, run_telnet_session
from .converters import ModelConverter
from .exporters import export_config
from .importers import import_csv
from .port_map import build_port_map
from .validators import ConfigValidator

ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = ROOT / "storage"
BACKUP_DIR = STORAGE_DIR / "backups"
PROFILES_FILE = STORAGE_DIR / "profiles.json"
MODELS_FILE = STORAGE_DIR / "models.json"

app = Flask(
    __name__,
    static_folder=str(ROOT / "frontend"),
    static_url_path="",
)

config_manager = ConfigManager(str(PROFILES_FILE))
model_converter = ModelConverter(str(MODELS_FILE))
validator = ConfigValidator()
backup_scheduler = BackupScheduler(str(PROFILES_FILE), str(BACKUP_DIR))
backup_scheduler.start()
atexit.register(backup_scheduler.stop)


@app.route("/")
def index() -> Any:
    return app.send_static_file("index.html")


@app.get("/api/configs")
def list_configs() -> Any:
    return jsonify({"profiles": config_manager.list_profiles()})


@app.post("/api/configs")
def create_config() -> Any:
    payload = request.get_json(force=True)
    name = payload.get("name", "New profile")
    model = payload.get("model", "unknown")
    data = payload.get("data", {})
    profile = config_manager.create_profile(name, model, data)
    return jsonify(profile), 201


@app.get("/api/configs/<profile_id>")
def get_config(profile_id: str) -> Any:
    profile = config_manager.get_profile(profile_id)
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(profile)


@app.put("/api/configs/<profile_id>")
def update_config(profile_id: str) -> Any:
    payload = request.get_json(force=True)
    profile = config_manager.update_profile(
        profile_id,
        name=payload.get("name"),
        model=payload.get("model"),
        data=payload.get("data"),
    )
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(profile)


@app.delete("/api/configs/<profile_id>")
def delete_config(profile_id: str) -> Any:
    deleted = config_manager.delete_profile(profile_id)
    if not deleted:
        return jsonify({"error": "Profile not found"}), 404
    return "", 204


@app.post("/api/import/csv")
def import_config_csv() -> Any:
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400
    csv_file = request.files["file"]
    try:
        payloads = import_csv(csv_file.read())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    profiles = [config_manager.upsert_from_dict({"name": data["name"], "model": data.get("model", "unknown"), "data": data}) for data in payloads]
    return jsonify({"profiles": profiles})


@app.post("/api/convert")
def convert_config() -> Any:
    payload = request.get_json(force=True)
    config = payload.get("config", {})
    target_model = payload.get("target_model")
    if not target_model:
        return jsonify({"error": "target_model is required"}), 400
    try:
        converted = model_converter.convert(config, target_model)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(converted)


@app.post("/api/validate")
def validate_config() -> Any:
    payload = request.get_json(force=True)
    result = validator.validate(payload)
    return jsonify(result)


@app.get("/api/configs/<profile_id>/export")
def export_profile(profile_id: str) -> Any:
    fmt = request.args.get("format", "cli")
    profile = config_manager.get_profile(profile_id)
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    try:
        content = export_config(profile.get("data", {}), fmt)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"format": fmt, "content": content})


@app.get("/api/configs/<profile_id>/ports")
def get_port_map(profile_id: str) -> Any:
    profile = config_manager.get_profile(profile_id)
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    port_map = build_port_map(profile.get("data", {}))
    return jsonify({"ports": port_map})


@app.post("/api/connections/telnet")
def telnet_connect() -> Any:
    payload = request.get_json(force=True)
    try:
        results = run_telnet_session(
            payload["host"],
            int(payload.get("port", 23)),
            payload.get("commands", []),
            username=payload.get("username"),
            password=payload.get("password"),
            timeout=int(payload.get("timeout", 5)),
        )
    except (KeyError, TypeError):
        return jsonify({"error": "host and commands are required"}), 400
    except ConnectionError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"results": [result.__dict__ for result in results]})


@app.post("/api/connections/serial")
def serial_connect() -> Any:
    payload = request.get_json(force=True)
    try:
        results = run_serial_session(
            payload["port"],
            payload.get("commands", []),
            baudrate=int(payload.get("baudrate", 9600)),
            timeout=int(payload.get("timeout", 5)),
        )
    except (KeyError, TypeError):
        return jsonify({"error": "port and commands are required"}), 400
    except ConnectionError as exc:
        return jsonify({"error": str(exc)}), 502
    return jsonify({"results": [result.__dict__ for result in results]})


@app.post("/api/backups/run")
def run_backup() -> Any:
    path = backup_scheduler.run_now()
    return jsonify({"backup": str(path.relative_to(ROOT))})


@app.get("/api/backups")
def list_backups() -> Any:
    backups = [str(path.relative_to(ROOT)) for path in sorted(BACKUP_DIR.glob("profiles-*.json"))]
    return jsonify({"backups": backups})


@app.get("/static/<path:filename>")
def serve_static(filename: str) -> Any:
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

