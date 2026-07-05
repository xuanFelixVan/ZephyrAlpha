# [A_module] module_id=MOD-INF_schema | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.schema
# [INVARIANTS] semantic versioning for schema compatibility; major version mismatch = incompatible; fail-safe on missing config
# [MODIFY-GUARD] facade.py; alerts.py; config/metrics_schema.yaml
# [CONSUMERS] zephyr.security.access_control
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] yaml.YAMLError; OSError; ValueError
# [TESTS] tests/system-telemetry/test_schema.py
# [TTL] permanent
"""SchemaSubsystem — Schema 版本管理与兼容性校验（MOD-INF-015 §5.1 · schema）.

加载 config/metrics_schema.yaml，提供 get_version / check_compatibility / get_namespaces / validate_metric_name API。
"""

from __future__ import annotations

from pathlib import Path

import yaml
from zephyr.shared.io.paths import REPO_ROOT


class SchemaSubsystem:
    _CONFIG_PATH = REPO_ROOT / "config" / "metrics_schema.yaml"
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
            if parts[0] == "0":
                return parts[1] == tgt_parts[1]
            return int(parts[1]) >= int(tgt_parts[1])
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

    def register_schema(self, schema_name: str, version: str) -> None:
        if "registered_schemas" not in self._schema:
            self._schema["registered_schemas"] = {}
        self._schema["registered_schemas"][schema_name] = version


__all__ = [
    "SchemaSubsystem",
    "check_compatibility",
    "get_namespaces",
    "get_version",
    "parts",
    "register_schema",
    "tgt_parts",
    "validate_metric_name",
]
