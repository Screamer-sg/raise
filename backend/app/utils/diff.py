from __future__ import annotations

import json
from difflib import unified_diff
from typing import Any


def diff_configs(left: dict, right: dict) -> str:
    left_dump = json.dumps(left, indent=2, sort_keys=True).splitlines()
    right_dump = json.dumps(right, indent=2, sort_keys=True).splitlines()
    diff = unified_diff(left_dump, right_dump, fromfile="left", tofile="right", lineterm="")
    return "\n".join(diff)


__all__ = ["diff_configs"]
