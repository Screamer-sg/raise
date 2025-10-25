from __future__ import annotations

import base64
import os
from cryptography.fernet import Fernet, InvalidToken


class CryptoService:
    """Simple encryption helper to protect sensitive fields in profiles."""

    def __init__(self, secret: str | None = None) -> None:
        self.key = self._derive_key(secret)
        self.fernet = Fernet(self.key)

    def _derive_key(self, secret: str | None) -> bytes:
        if secret:
            data = secret.encode("utf-8")
        else:
            data = os.environ.get("RAISECOM_SECRET", "raisecom-secret").encode("utf-8")
        # Fernet requires 32 url-safe base64 encoded bytes
        return base64.urlsafe_b64encode(data.ljust(32, b"0")[:32])

    def encrypt(self, plaintext: str) -> str:
        token = self.fernet.encrypt(plaintext.encode("utf-8"))
        return f"enc::{token.decode('utf-8')}"

    def decrypt(self, token: str) -> str:
        if token.startswith("enc::"):
            token = token[5:]
        try:
            return self.fernet.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Invalid encrypted token") from exc


__all__ = ["CryptoService"]
