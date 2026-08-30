# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.ai_context_injector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_infrastructure.py ; tests/ai/test_ai_context_injector.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注入内容不可覆盖用户指令
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AI Context Injector — 施工前预检D-023-16 · §6.8。


三级注入策略：minimal(<100token)/standard(<300token)/full(<1000token)


注入点：session_manager派发task时 + MCP discover_applicable_gates


对标 blueprint.md §6.8。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: module_id 参数
#   fields: 参数 module_id，类型注解 str
#   code: ai_context_injector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: active_events 参数
#   fields: 参数 active_events，类型注解 list[dict[str, object]]
#   code: ai_context_injector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: limit 参数
#   fields: 参数 limit，类型注解 int
#   code: ai_context_injector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: snapshot 参数
#   fields: 参数 snapshot，类型注解 HealthSnapshot
#   code: ai_context_injector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_health_snapshot
#   name_en: build_health_snapshot
#   intro: build_health_snapshot(module_id, active_events) 源码 L162-L175
#   desc: 源码 L162-L175
#   inputs: module_id active_events
#   outputs: HealthSnapshot
# - id: A2
#   name_zh: ② build_top_drifts
#   name_en: build_top_drifts
#   intro: build_top_drifts(active_events, limit) 源码 L178-L201
#   desc: 源码 L178-L201
#   inputs: active_events limit
#   outputs: list[TopDriftItem]
# - id: A3
#   name_zh: ③ inject_minimal
#   name_en: inject_minimal
#   intro: inject_minimal(snapshot) 源码 L204-L229
#   desc: 源码 L204-L229
#   inputs: snapshot
#   outputs: InjectedContext
# - id: A4
#   name_zh: ④ inject_standard
#   name_en: inject_standard
#   intro: inject_standard(snapshot, top_drifts) 源码 L232-L251
#   desc: 源码 L232-L251
#   inputs: snapshot top_drifts
#   outputs: InjectedContext
# - id: A5
#   name_zh: ⑤ inject_full
#   name_en: inject_full
#   intro: inject_full(snapshot, all_events) 源码 L254-L295
#   desc: 源码 L254-L295
#   inputs: snapshot all_events
#   outputs: InjectedContext
#   （注：A5 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: HealthSnapshot
#   name_en: HealthSnapshot
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/ai/test_ai_context_injector.py
# - id: O2
#   name_zh: list[TopDriftItem]
#   name_en: list[TopDriftItem]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_infrastructure.py ; tests/ai/test_ai_context_injector.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class InjectionLevel(str, Enum):
    MINIMAL = "minimal"

    STANDARD = "standard"

    FULL = "full"


@dataclass
class HealthSnapshot:
    module_id: str

    active_drift_count: int

    budget_remaining: dict[str, int]

    state_distribution: dict[str, int]

    snapshot_time: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TopDriftItem:
    event_id: str

    detector_id: str

    severity: str

    roi_score: float

    description: str


@dataclass
class InjectedContext:
    level: InjectionLevel

    token_estimate: int

    content: str

    injection_time: datetime = field(default_factory=lambda: datetime.now(UTC))


def build_health_snapshot(module_id: str, active_events: list[dict[str, object]]) -> HealthSnapshot:
    state_dist: dict[str, int] = {}

    for evt in active_events:
        state = str(evt.get("state", "UNKNOWN"))

        state_dist[state] = state_dist.get(state, 0) + 1

    return HealthSnapshot(
        module_id=module_id,
        active_drift_count=len(active_events),
        budget_remaining={"P0": 3, "P1": 8, "P2": 15},
        state_distribution=state_dist,
    )


def build_top_drifts(
    active_events: list[dict[str, object]],
    limit: int = 3,
) -> list[TopDriftItem]:
    scored: list[TopDriftItem] = []

    for evt in active_events:
        # 5.106.3 修复: evt.get("roi_score", 0.0) 仅在 key 缺失时返回 default,
        # key 存在但值为 None 时 float(None) 抛 TypeError。改为 `or 0.0` 兼容 None。
        roi = float(evt.get("roi_score") or 0.0)

        scored.append(
            TopDriftItem(
                event_id=str(evt.get("event_id", "")),
                detector_id=str(evt.get("detector_id", "")),
                severity=str(evt.get("severity", "INFO")),
                roi_score=roi,
                description=str(evt.get("description", ""))[:120],
            )
        )

    scored.sort(key=lambda x: x.roi_score, reverse=True)

    return scored[:limit]


def inject_minimal(snapshot: HealthSnapshot) -> InjectedContext:
    lines: list[str] = []

    lines.append(f"[DRIFT] MOD-INF-023 active_drifts={snapshot.active_drift_count}")

    lines.append(
        f"budget: P0={snapshot.budget_remaining.get('P0', 3)}/"
        f"P1={snapshot.budget_remaining.get('P1', 8)}/"
        f"P2={snapshot.budget_remaining.get('P2', 15)}"
    )

    states = snapshot.state_distribution

    lines.append(
        f"states: DETECTED={states.get('DETECTED', 0)} "
        f"TRIAGED={states.get('TRIAGED', 0)} "
        f"RESOLVING={states.get('RESOLVING', 0)}"
    )

    content = "\n".join(lines)

    return InjectedContext(
        level=InjectionLevel.MINIMAL,
        token_estimate=len(content.split()),
        content=content,
    )


def inject_standard(
    snapshot: HealthSnapshot,
    top_drifts: list[TopDriftItem],
) -> InjectedContext:
    lines: list[str] = [inject_minimal(snapshot).content, ""]

    lines.append("Top active drifts by ROI:")

    for i, td in enumerate(top_drifts, 1):
        lines.append(f"  {i}. [{td.severity}] {td.detector_id}: {td.description} (ROI={td.roi_score:.1f})")

    lines.append(f"\nTotal drifts awaiting attention: {snapshot.active_drift_count}")

    content = "\n".join(lines)

    return InjectedContext(
        level=InjectionLevel.STANDARD,
        token_estimate=len(content.split()),
        content=content,
    )


def inject_full(
    snapshot: HealthSnapshot,
    all_events: list[dict[str, object]],
) -> InjectedContext:
    lines: list[str] = [inject_minimal(snapshot).content, ""]

    lines.append("=== FULL DRIFT INVENTORY ===")

    lines.append(f"Total events: {len(all_events)}")

    lines.append("")

    severity_order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}

    all_events_sorted = sorted(
        all_events,
        key=lambda e: (
            severity_order.get(str(e.get("severity", "INFO")), 99),
            # 5.106.4 修复: e.get("roi_score", 0.0) 在值为 None 时 float(None) 抛 TypeError,改为 `or 0.0`
            -float(e.get("roi_score") or 0.0),
        ),
    )

    for evt in all_events_sorted:
        lines.append(
            f"[{evt.get('severity', '?')}] {evt.get('detector_id', '?')} | {evt.get('description', '?')[:100]}"
        )

        if evt.get("auto_fixable"):
            lines.append(f"  => auto_fixable: {evt.get('fix_description', 'N/A')[:80]}")

    lines.append("")

    lines.append(f"State breakdown: {snapshot.state_distribution}")

    content = "\n".join(lines)

    return InjectedContext(
        level=InjectionLevel.FULL,
        token_estimate=len(content.split()),
        content=content,
    )


_INJECTOR_MAP: dict[InjectionLevel, str] = {
    InjectionLevel.MINIMAL: "inject_minimal",
    InjectionLevel.STANDARD: "inject_standard",
    InjectionLevel.FULL: "inject_full",
}
