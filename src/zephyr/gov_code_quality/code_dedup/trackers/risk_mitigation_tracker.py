# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.trackers.risk_mitigation_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/risk/test_risk_mitigation_tracker.py
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
风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: risk_mitigation_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① RiskMitigationTracker
#   name_en: RiskMitigationTracker
#   intro: class RiskMitigationTracker 源码 L65-L101
#   desc: 公共方法（定义序）: track, mark_fixed, get_stale, summary；源码 L65-L101
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RiskMitigationTracker
#   downstream: tests/risk/test_risk_mitigation_tracker.py
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
class MitigationEntry:
    clone_id: str
    first_seen: str
    last_seen: str
    scan_count: int
    severity: str
    status: str = "UNFIXED"


@dataclass
class RiskMitigationTracker:
    entries: dict[str, MitigationEntry] = field(default_factory=dict)
    stale_threshold: int = 10

    def track(self, clone_id: str, severity: str) -> MitigationEntry:
        now = datetime.now(UTC).isoformat()
        if clone_id in self.entries:
            entry = self.entries[clone_id]
            entry.last_seen = now
            entry.scan_count += 1
            if entry.scan_count >= self.stale_threshold and entry.status == "UNFIXED":
                entry.status = "STALE"
            return entry

        entry = MitigationEntry(clone_id=clone_id, first_seen=now, last_seen=now, scan_count=1, severity=severity)
        self.entries[clone_id] = entry
        return entry

    def mark_fixed(self, clone_id: str) -> None:
        if clone_id in self.entries:
            self.entries[clone_id].status = "FIXED"

    def get_stale(self) -> list[MitigationEntry]:
        return [e for e in self.entries.values() if e.status == "STALE"]

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        unfixed = sum(1 for e in self.entries.values() if e.status == "UNFIXED")
        stale = sum(1 for e in self.entries.values() if e.status == "STALE")
        fixed = sum(1 for e in self.entries.values() if e.status == "FIXED")
        return {
            "total": total,
            "unfixed": unfixed,
            "stale": stale,
            "fixed": fixed,
            "stale_threshold": self.stale_threshold,
        }
