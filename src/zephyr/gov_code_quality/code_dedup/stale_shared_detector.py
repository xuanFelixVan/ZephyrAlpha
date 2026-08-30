# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.stale_shared_detector
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/drift/test_stale_shared_detector.py
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
过时共享函数检测器 — 无caller × 30天 -> STALE标记.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: stale_shared_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① StaleSharedDetector
#   name_en: StaleSharedDetector
#   intro: 过时共享函数检测.
#   desc: 过时共享函数检测.；公共方法（定义序）: detect；源码 L51-L78
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: StaleSharedDetector
#   downstream: tests/governance/drift/test_stale_shared_detector.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import UTC, datetime


class StaleSharedDetector:
    """过时共享函数检测."""

    _STALE_AGE_DAYS: int = 30

    def detect(self, functions_with_callers: list[dict]) -> list[str]:
        """无caller × 30天未使用 -> STALE."""
        now = datetime.now(UTC)
        stale: list[str] = []

        for func_info in functions_with_callers:
            if func_info.get("caller_count", 0) > 0:
                continue

            last_used = func_info.get("last_used_at", "")
            if not last_used:
                stale.append(func_info["name"])
                continue

            try:
                used_date = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
            except ValueError:
                continue

            if (now - used_date.replace(tzinfo=UTC)).days >= self._STALE_AGE_DAYS:
                stale.append(func_info["name"])

        return stale
