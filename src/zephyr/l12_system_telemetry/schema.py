"""SchemaSubsystem — Schema 版本管理与兼容性校验（MOD-INF-015 §5.1 · schema）.

加载 config/metrics_schema.yaml，提供 get_version / check_compatibility 等 API。
"""

from __future__ import annotations

from pathlib import Path

import yaml


class SchemaSubsystem:
    _CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "metrics_schema.yaml"
    _VERSION = "0.9.0"

    def __init__(self, module_id: str = "", test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._schema: dict = self._load_schema() if self._CONFIG_PATH.exists() else {}

    def _load_schema(self) -> dict:
        try:
            return yaml.safe_load(self._CONFIG_PATH.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}

    def get_version(self) -> str:
        return self._VERSION

    def check_compatibility(self, target_version: str) -> bool:
        parts = self._VERSION.split(".")
        tgt_parts = target_version.split(".")
        try:
            if parts[0] != tgt_parts[0]:
                return False
            if int(parts[1]) >= int(tgt_parts[1]):
                return True
            return False
        except (IndexError, ValueError):
            return False

    def get_namespaces(self) -> list[str]:
        return list(self._schema.get("namespaces", {}).keys())

    def validate_metric_name(self, name: str) -> bool:
        if not self._schema:
            return True
        for ns in self._schema.get("namespaces", {}).values():
            for field in ns.get("fields", []):
                if field.get("name") == name:
                    return True
        return False
