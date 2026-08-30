# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.trackers.consequence_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/delegation/test_consequence_tracker.py
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
后果追踪——记录每次修复操作对依赖方的影响.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: consequence_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① ConsequenceTracker
#   name_en: ConsequenceTracker
#   intro: class ConsequenceTracker 源码 L65-L98
#   desc: 公共方法（定义序）: record, rollback_last, summary；源码 L65-L98
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ConsequenceTracker
#   downstream: tests/governance/delegation/test_consequence_tracker.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Consequence:
    fix_id: str
    target_file: str
    impacted_files: list[str]
    timestamp: str
    rollback_available: bool = True
    status: str = "APPLIED"


@dataclass
class ConsequenceTracker:
    history: list[Consequence] = field(default_factory=list)
    rollback_stack: list[Consequence] = field(default_factory=list)

    def record(self, fix_id: str, target_file: str, impacted_files: list[str]) -> Consequence:
        c = Consequence(
            fix_id=fix_id,
            target_file=target_file,
            impacted_files=impacted_files,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self.history.append(c)
        self.rollback_stack.append(c)
        return c

    def rollback_last(self) -> dict[str, Any]:
        if not self.rollback_stack:
            return {"rolled_back": False, "reason": "stack_empty"}

        last = self.rollback_stack.pop()
        last.status = "ROLLED_BACK"
        return {
            "rolled_back": True,
            "fix_id": last.fix_id,
            "target_file": last.target_file,
            "impacted_files": last.impacted_files,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "total_fixes": len(self.history),
            "rollback_count": sum(1 for c in self.history if c.status == "ROLLED_BACK"),
            "pending_rollback": len(self.rollback_stack),
        }
