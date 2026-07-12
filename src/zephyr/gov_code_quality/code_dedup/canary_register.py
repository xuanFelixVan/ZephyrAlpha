# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.canary_register
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/canary/test_canary_register.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_canary_register | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""金丝雀注册表维护器 — 注册/过期/腐败检测."""

from datetime import UTC, datetime
from pathlib import Path

import yaml


class CanaryRegister:
    """金丝雀函数注册表."""

    def __init__(self, registry_path: str | Path | None = None) -> None:
        if registry_path is None:
            registry_path = Path("data/cache/canary_register.yaml")
        self._path = Path(registry_path)
        self._canaries: list[dict] = []
        self._load()

    def register(self, function_name: str, module: str, stage: str = "active") -> None:
        self._canaries.append(
            {
                "function": function_name,
                "module": module,
                "stage": stage,
                "registered_at": datetime.now(UTC).isoformat(),
                "last_verified": "",
            }
        )
        self._save()

    def check_staleness(self, max_age_days: int = 90) -> list[dict]:
        stale = []
        now = datetime.now(UTC)
        for c in self._canaries:
            if not c["last_verified"]:
                stale.append(c)
                continue
            try:
                dt = datetime.fromisoformat(c["last_verified"].replace("Z", "+00:00"))
                if (now - dt.replace(tzinfo=UTC)).days > max_age_days:
                    c["stage"] = "stale"
                    stale.append(c)
            except ValueError:
                pass
        return stale

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = yaml.safe_load(self._path.read_text(encoding="utf-8")) or {}
                self._canaries = data.get("canaries", [])
            except yaml.YAMLError:
                pass

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            yaml.dump({"canaries": self._canaries, "updated_at": datetime.now(UTC).isoformat()}, allow_unicode=True),
            encoding="utf-8",
        )
