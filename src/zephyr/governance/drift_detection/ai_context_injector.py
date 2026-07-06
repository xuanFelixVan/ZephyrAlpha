# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.ai_context_injector
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_infrastructure.py; tests/ai/test_ai_context_injector.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注入内容不可覆盖用户指令
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_ai_context_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AI Context Injector — 施工前预检D-023-16 · §6.8。





module_id: MOD-INF-023


三级注入策略：minimal(<100token)/standard(<300token)/full(<1000token)


注入点：session_manager派发task时 + MCP discover_applicable_gates


对标 blueprint.md §6.8。"""

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
