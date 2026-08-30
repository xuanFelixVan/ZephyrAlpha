# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_freshness
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Freshness Decay
Author: factory-agent
Version: 0.3.0

720h linear decay model

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_freshness.py
# 层: 算法
# - id: A1
#   name_zh: ① FreshnessDecayModel
#   name_en: FreshnessDecayModel
#   intro: class FreshnessDecayModel 源码 L60-L113
#   desc: 公共方法（定义序）: save, load, compute, current_state, boost；源码 L60-L113
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FreshnessDecayModel
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_HISTORY = Path(__file__).resolve().parent / "_freshness.json"


class FreshnessDecayModel:
    HOURS_TO_ZERO = 720

    def save(self, data):
        """公共接口：save（Stage 4 公共化）。"""
        return self._save(data)

    def load(self) -> dict:
        """公共接口：load（Stage 4 公共化）。"""
        return self._load()

    WARNING_THRESHOLD = 30.0
    CRITICAL_THRESHOLD = 10.0

    @classmethod
    def compute(cls, validated_at: str) -> float:
        try:
            t = datetime.fromisoformat(validated_at)
            elapsed = (datetime.now(UTC) - t).total_seconds() / 3600
            return max(0.0, 100.0 - (elapsed / cls.HOURS_TO_ZERO) * 100.0)
        except (ValueError, TypeError):
            return 0.0

    def current_state(self, skill_id: str) -> dict[str, Any]:
        data = self._load()
        entry = data.get(skill_id)
        if entry:
            score = self.compute(entry.get("last_validated", ""))
            return {
                "skill_id": skill_id,
                "freshness_score": round(score, 1),
                "last_validated": entry["last_validated"],
                "registered": True,
            }
        return {"skill_id": skill_id, "freshness_score": 50.0, "registered": False}

    def boost(self, skill_id: str, amount: float = 50.0):
        data = self._load()
        data[skill_id] = {"last_validated": datetime.now(UTC).isoformat(), "boost": amount}
        self._save(data)

    def _load(self) -> dict:
        if _HISTORY.exists():
            try:
                return json.loads(_HISTORY.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        return {}

    def _save(self, data: dict):
        try:
            _HISTORY.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
