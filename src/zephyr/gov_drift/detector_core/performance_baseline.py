# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.performance_baseline
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name，类型注解 str
#   code: performance_baseline.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: segments 参数
#   fields: 参数 segments，类型注解 dict[str, int]
#   code: performance_baseline.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_segment
#   name_en: get_segment
#   intro: get_segment(name) 源码 L96-L100
#   desc: 源码 L96-L100
#   inputs: name
#   outputs: LatencySegment | None
# - id: A2
#   name_zh: ② validate_e2e
#   name_en: validate_e2e
#   intro: validate_e2e(segments) 源码 L103-L111
#   desc: 源码 L103-L111
#   inputs: segments
#   outputs: tuple[bool, str]
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: LatencySegment | None
#   name_en: LatencySegment | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# - id: O2
#   name_zh: tuple[bool, str]
#   name_en: tuple[bool, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class LatencySegment:
    name: str
    max_ms: int
    description: str


PERFORMANCE_BASELINE: Final[list[LatencySegment]] = [
    LatencySegment(name="market_to_signal", max_ms=200, description="行情->信号"),
    LatencySegment(name="signal_to_risk", max_ms=10, description="信号->风控"),
    LatencySegment(name="risk_to_order", max_ms=50, description="风控->订单"),
]

E2E_MAX_MS: Final[int] = 500
E2E_BUDGET_BREAKDOWN: Final[dict[str, int]] = {
    "market_to_signal": 200,
    "signal_to_risk": 10,
    "risk_to_order": 50,
    "network_overhead": 100,
    "remaining_slack": 140,
}


def get_segment(name: str) -> LatencySegment | None:
    for seg in PERFORMANCE_BASELINE:
        if seg.name == name:
            return seg
    return None


def validate_e2e(segments: dict[str, int]) -> tuple[bool, str]:
    total = sum(segments.values())
    if total > E2E_MAX_MS:
        return False, f"E2E {total}ms > {E2E_MAX_MS}ms"
    for name, val in segments.items():
        seg = get_segment(name)
        if seg and val > seg.max_ms:
            return False, f"{name}: {val}ms > {seg.max_ms}ms"
    return True, f"E2E {total}ms ≤ {E2E_MAX_MS}ms — PASS"
