from __future__ import annotations

import base64
import os


class CryptoService:
    """Tiny reversible encoder used to protect stored profile secrets."""

    def __init__(self, secret: str | None = None) -> None:
        self._secret = (secret or os.environ.get("RAISECOM_SECRET", "raisecom-secret")).encode(
            "utf-8"
        )

    def encrypt(self, plaintext: str) -> str:
        payload = plaintext.encode("utf-8") + b"::" + self._secret
        token = base64.urlsafe_b64encode(payload).decode("utf-8")
        return f"enc::{token}"

    def decrypt(self, token: str) -> str:
        raw = token[5:] if token.startswith("enc::") else token
        data = base64.urlsafe_b64decode(raw.encode("utf-8"))
        value, _, secret = data.partition(b"::")
        if secret != self._secret:
            raise ValueError("Token secret mismatch")
        return value.decode("utf-8")


__all__ = ["CryptoService"]
