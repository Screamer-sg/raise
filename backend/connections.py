"""Connectivity helpers for Telnet and serial links."""

from __future__ import annotations

import telnetlib
from contextlib import closing
from dataclasses import dataclass
from typing import Iterable, List, Optional

import serial


@dataclass
class CommandResult:
    command: str
    response: str


class ConnectionError(RuntimeError):
    """Raised when a device connection could not be established."""


def run_telnet_session(host: str, port: int, commands: Iterable[str], *,
                       username: Optional[str] = None, password: Optional[str] = None,
                       timeout: int = 5) -> List[CommandResult]:
    """Run a simple Telnet session and collect responses."""

    try:
        with closing(telnetlib.Telnet(host, port, timeout=timeout)) as client:
            if username:
                client.read_until(b"login:", timeout=timeout)
                client.write(username.encode("utf-8") + b"\n")
            if password:
                client.read_until(b"Password:", timeout=timeout)
                client.write(password.encode("utf-8") + b"\n")

            results: List[CommandResult] = []
            for command in commands:
                client.write(command.encode("utf-8") + b"\n")
                output = client.read_until(b"#", timeout=timeout)
                results.append(CommandResult(command=command, response=output.decode("utf-8", errors="ignore")))
            return results
    except OSError as exc:  # pragma: no cover - network operations are environment dependent
        raise ConnectionError(str(exc)) from exc


def run_serial_session(port: str, commands: Iterable[str], *, baudrate: int = 9600,
                       timeout: int = 5) -> List[CommandResult]:
    """Run commands over a serial interface."""

    try:
        with serial.Serial(port, baudrate=baudrate, timeout=timeout) as device:
            results: List[CommandResult] = []
            for command in commands:
                device.write(command.encode("utf-8") + b"\r\n")
                device.flush()
                response = device.read_until(b"#")
                results.append(CommandResult(command=command, response=response.decode("utf-8", errors="ignore")))
            return results
    except serial.SerialException as exc:  # pragma: no cover - depends on serial availability
        raise ConnectionError(str(exc)) from exc


__all__ = ["run_telnet_session", "run_serial_session", "ConnectionError", "CommandResult"]

