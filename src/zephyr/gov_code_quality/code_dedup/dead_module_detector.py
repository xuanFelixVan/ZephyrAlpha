# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.dead_module_detector
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/drift/test_dead_module_detector.py
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
死共享模块检测器 — shared/子模块无人使用 -> DEAD.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dead_module_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① DeadModuleDetector
#   name_en: DeadModuleDetector
#   intro: 死模块检测.
#   desc: 死模块检测.；公共方法（定义序）: detect；源码 L52-L76
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DeadModuleDetector
#   downstream: tests/governance/drift/test_dead_module_detector.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import UTC, datetime
from pathlib import Path


class DeadModuleDetector:
    """死模块检测."""

    _DEAD_THRESHOLD_DAYS: int = 60

    def detect(self, shared_dir: str | Path, last_access: dict[str, str]) -> list[dict]:
        """检测30天+无人使用的shared模块."""
        sdir = Path(shared_dir)
        dead: list[dict] = []
        now = datetime.now(UTC)

        for py_file in sdir.rglob("*.py"):
            key = str(py_file)
            last = last_access.get(key, "")
            if not last:
                dead.append({"module": key, "reason": "从未被引用"})
                continue
            try:
                dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                if (now - dt.replace(tzinfo=UTC)).days >= self._DEAD_THRESHOLD_DAYS:
                    dead.append({"module": key, "reason": f"超过{self._DEAD_THRESHOLD_DAYS}天未引用"})
            except ValueError:
                pass

        return dead
