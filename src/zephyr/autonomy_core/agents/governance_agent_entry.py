# [BLUEPRINT] MOD-EXE-GOV-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.1/§4-S0.2
# [MODULE] zephyr.autonomy_core.agents.governance_agent_entry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.autonomy_boundary_gate ; zephyr.autonomy_core.agents._run_store
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py ; 人手动触发（CLI）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯组装薄入口（零新业务逻辑：gate 判定复用 MOD-AU-001）；产出 100% 落盘 .runtime/agent_runs/governance/ 且标 human_gated；不修改规则本体（规则修订走治理流程 human_gated）
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 S0.2 验收口径
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 单个 target 判定异常不中断整单（fail-closed 语义由 MOD-AU-001 保证）；工单缺字段→ValueError（入口输入校验）
# [TESTS] tests/autonomy/test_execution_layer_agent_entries.py
# [A_module] module_id=MOD-EXE-GOV-001 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""治理 Agent 薄入口（14号文 §3.1 gate 检查/规则执行，§4 S0.2 手动形态）.

输入：gate 检查工单（落盘 JSON：ticket_id + targets 路径列表）。
处理：逐 target 组装调用既有 AutonomyBoundaryGate（MOD-AU-001，GOV-AI-001 注册表
三分类判定），聚合 gate verdict。
输出：gate_verdicts.json + run.json + audit.jsonl 落盘（.runtime/agent_runs/governance/）。
不做：不修改规则本身；不做自治运行时（人手动触发，61号文 §4.1 边界内）。

手动触发：python -m zephyr.autonomy_core.agents.governance_agent_entry --ticket <path>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Final

from zephyr.autonomy_core.agents._run_store import AgentRunStore
from zephyr.autonomy_core.autonomy_boundary_gate import (
    AutonomyBoundaryGate,
    GateDecision,
)

ROLE: Final[str] = "governance"

# 职责边界声明（Agent Card 子集，14号文 §3.1：capabilities/autonomyBoundaries/healthCheck）
AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "gate_check",
            "name": "gate 检查工单执行",
            "inputs": "落盘工单 JSON（ticket_id/targets/session_id）",
            "outputs": "gate verdict 汇总 + 审计落盘",
            "autonomyLevel": "L0_manual",
        }
    ],
    "autonomyBoundaries": {
        "ai_modifiable": [],
        "human_gated": ["gate verdict 处置与人审工单消化"],
        "immutable": ["规则本体（修订走治理流程）"],
    },
    "healthCheck": {"heartbeat": "manual_trigger_only"},
}


def run_gate_check_ticket(
    ticket: dict[str, Any],
    *,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    gate: AutonomyBoundaryGate | None = None,
) -> dict[str, Any]:
    """执行一张 gate 检查工单（端到端：输入工单→gate verdict→审计落盘）.

    Args:
        ticket: {"ticket_id": str, "targets": [路径...], "session_id"/"note" 可选}.
        runtime_dir: 落盘根（默认仓根 .runtime/）.
        repo_root: 仓根（默认自动解析；测试注入）.
        gate: 可注入的判定门（默认新建 AutonomyBoundaryGate，复用 GOV-AI-001 真表）.

    Returns:
        落盘的 verdict 汇总 dict（含 overall：passed/escalated/blocked）.
    """
    ticket_id = str(ticket.get("ticket_id") or "").strip()
    targets = ticket.get("targets")
    if not ticket_id or not isinstance(targets, list) or not targets:
        raise ValueError("gate 检查工单缺 ticket_id 或 targets 为空")
    session_id = str(ticket.get("session_id") or "")

    store = AgentRunStore(ROLE, runtime_dir=runtime_dir, repo_root=repo_root)
    store.begin(ticket_id, ticket)
    own_gate = gate is None
    gate = gate or AutonomyBoundaryGate(runtime_dir=runtime_dir, repo_root=repo_root)
    try:
        verdicts: list[dict[str, Any]] = [
            gate.check_write_permission(
                f"{ticket_id}-{index:02d}", str(target), {"session_id": session_id}
            ).to_dict()
            for index, target in enumerate(targets)
        ]
    finally:
        if own_gate:
            gate.close()  # 自建 gate 的审计句柄由本入口负责关闭；注入 gate 归调用方

    counts: dict[str, int] = {d.value: 0 for d in GateDecision}
    for item in verdicts:
        counts[item["decision"]] += 1
    overall = (
        "blocked"
        if counts[GateDecision.BLOCK.value]
        else ("escalated" if counts[GateDecision.ESCALATE.value] else "passed")
    )
    report = {
        "overall": overall,
        "decision_counts": counts,
        "verdicts": verdicts,
        "note": str(ticket.get("note") or ""),
    }
    store.write_output("gate_verdicts.json", report, ticket_id)
    store.finish(ticket_id, overall, {"targets": len(targets), **counts})
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR]."""
    parser = argparse.ArgumentParser(description="治理 Agent 薄入口：gate 检查工单手动触发")
    parser.add_argument("--ticket", required=True, help="gate 检查工单 JSON 路径")
    parser.add_argument("--runtime-dir", default=None, help="落盘根（默认仓根 .runtime/）")
    args = parser.parse_args(argv)
    ticket = json.loads(Path(args.ticket).read_text(encoding="utf-8"))
    report = run_gate_check_ticket(ticket, runtime_dir=args.runtime_dir)
    print(json.dumps({"overall": report["overall"], **report["decision_counts"]}, ensure_ascii=False))
    return 0


__all__ = ["AGENT_CARD", "ROLE", "main", "run_gate_check_ticket"]


if __name__ == "__main__":
    raise SystemExit(main())
