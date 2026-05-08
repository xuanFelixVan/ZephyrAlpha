"""SSoT注册器 — 提取函数自动注册到 shared API清单."""

from __future__ import annotations

import yaml
from datetime import datetime, timezone
from pathlib import Path


class SSOTRegistrar:
    """共享函数 SSoT 注册器."""

    def __init__(self, manifest_path: str | Path | None = None) -> None:
        if manifest_path is None:
            manifest_path = Path("data/cache/shared_api_manifest.yaml")
        self._manifest_path = Path(manifest_path)

    def register(
        self,
        function_name: str,
        module: str,
        signature: str = "",
        caller_count: int = 0,
    ) -> dict:
        """注册提取函数到 shared 清单."""
        entry = {
            "function": function_name,
            "module": module,
            "signature": signature,
            "caller_count": caller_count,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_manifest(entry)
        return entry

    def _append_manifest(self, entry: dict) -> None:
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        existing: dict = {"version": "1.0.0", "functions": []}
        if self._manifest_path.exists():
            try:
                existing = yaml.safe_load(self._manifest_path.read_text(encoding="utf-8")) or existing
            except yaml.YAMLError:
                pass
        existing.setdefault("functions", []).append(entry)
        existing["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._manifest_path.write_text(
            yaml.dump(existing, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
