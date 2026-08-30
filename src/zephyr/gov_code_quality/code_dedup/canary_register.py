# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.canary_register
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/canary/test_canary_register.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
金丝雀注册表维护器 — 注册/过期/腐败检测.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry_path 参数
#   fields: 参数 registry_path（无注解）
#   code: canary_register.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CanaryRegister
#   name_en: CanaryRegister
#   intro: 金丝雀函数注册表.
#   desc: 金丝雀函数注册表.；公共方法（定义序）: canaries, register, check_staleness；源码 L54-L116
#   inputs: registry_path
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CanaryRegister
#   downstream: tests/canary/test_canary_register.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def canaries(self) -> list[dict]:
        """只读：canaries（Stage 4 公共化）。"""
        return self._canaries

    @canaries.setter
    def canaries(self, value):
        """写入：canaries（Stage 4 公共化）。"""
        self._canaries = value

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
