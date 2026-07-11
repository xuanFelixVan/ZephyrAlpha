# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.ssot_registrar
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/rule_enforcement/test_ssot_registrar.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_dedup/test_ssot_registrar.py
# [A_module] module_id=MOD-UNK_ssot_registrar | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SSoT注册器 — 提取函数自动注册到 shared API清单."""

from datetime import UTC, datetime
from pathlib import Path

import yaml


class SSOTRegistrar:
    """共享函数 SSoT 注册器."""

    def __init__(self, manifest_path: str | Path | None = None) -> None:
        if manifest_path is None:
            manifest_path = Path("data/cache/shared_apimanifest.yaml")
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
            "registered_at": datetime.now(UTC).isoformat(),
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
        existing["updated_at"] = datetime.now(UTC).isoformat()
        self._manifest_path.write_text(
            yaml.dump(existing, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
