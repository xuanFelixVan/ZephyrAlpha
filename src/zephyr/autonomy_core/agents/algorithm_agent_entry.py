# [BLUEPRINT] MOD-EXE-ALGO-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.3/§4-S0.4/§4-S1.1
# [MODULE] zephyr.autonomy_core.agents.algorithm_agent_entry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.agents._run_store ; zephyr.experiment_tracking.query ; zephyr.trading.gpu_monitor ; zephyr.autonomy_core.agents._s11_wiring（§4-S1.1 可选接线，懒加载）
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_execution_layer_s11_wiring.py ; 人手动触发（CLI）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 实验登记先于执行（无 pending 登记片段不进入执行步，steps 顺序留痕）；单卡显存占用 >=90% 拒启动算法任务（约束二硬上限）；Phase 0 不新起训练/评估进程，执行步只读既有实验记录；不写注册表本体（REG-EXP-001 登记交统筹）；S1.1 注入缝（cascade_router/module_mapper）默认 None 零行为变化
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 S0.4/S1.1 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 显存采集不可用→守卫降级为 not_available 放行并如实留痕；实验记录缺失→status=evidence_missing 不抛；S1.1 模块映射载荷非法→status=error 裁决留痕不抛
# [TESTS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_execution_layer_s11_wiring.py
# [A_module] module_id=MOD-EXE-ALGO-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
算法 Agent 薄入口（14号文 §3.3 信号/模型/训练实验，§4 S0.4 手动形态）.

输入：算法实验工单（落盘 JSON：ticket_id/experiment_type/target_id/run_id/component）。
处理纪律（步骤顺序即验收口径，run.json steps 留痕）：
  ①实验登记先于执行——先落 experiment_registration.pending.json 待登记片段
    （REG-EXP-001 注册表本体不写，交统筹登记）；
  ②显存守卫——复用 zephyr.trading.gpu_monitor.collect_gpu_stats（nvidia-smi 口径），
    memory_used/memory_total >= 0.90 → 拒启动（status=refused_vram）；
  ③执行步只读——经 experiment_tracking.query.get_run 读既有实验记录出评估报告，
    Phase 0 不新起训练/评估进程（手动形态，14号文 §3.3 依赖降级说明）。
S1.1 可选接线（默认 None 零行为变化）：cascade_router→11号文模型选择裁决
（model_routing.decision.json）；experiment_type=module_generation 且注入
module_mapper→13号文四选一裁决留痕（module_mapping.spec.json）。

手动触发：python -m zephyr.autonomy_core.agents.algorithm_agent_entry --ticket <path>

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ticket 参数
#   fields: 参数 ticket，类型注解 dict[str, Any]
#   code: algorithm_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: runtime_dir 参数
#   fields: 参数 runtime_dir（无注解）
#   code: algorithm_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: algorithm_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: gpu_stats_provider 参数
#   fields: 参数 gpu_stats_provider（无注解）
#   code: algorithm_agent_entry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_algorithm_experiment_ticket
#   name_en: run_algorithm_experiment_ticket
#   intro: 执行一张算法实验工单（登记先于执行 + 显存守卫 + 只读评估，端到端落盘）.
#   desc: 执行一张算法实验工单（登记先于执行 + 显存守卫 + 只读评估，端到端落盘）. Args: ticket: {"ticket_id", "experiment_type", "t…；源码 L146-L231
#   inputs: ticket runtime_dir repo_root gpu_stats_provider tracking_config casca…
#   outputs: dict[str, Any]
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].
#   desc: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].；源码 L234-L243
#   inputs: argv
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_exec…
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_exec…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.autonomy_core.agents._run_store import AgentRunStore
from zephyr.experiment_tracking.config import ExperimentTrackingConfig
from zephyr.experiment_tracking.query import get_run

ROLE: Final[str] = "algorithm"
VRAM_HARD_LIMIT: Final[float] = 0.90  # 约束二：单卡 RTX 3090 显存 <90% 硬上限

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "algorithm_experiment",
            "name": "算法实验工单（登记→显存守卫→只读评估）",
            "inputs": "落盘实验工单 JSON",
            "outputs": "待登记片段 + 显存守卫结论 + 评估报告（落盘）",
            "autonomyLevel": "L0_manual",
        }
    ],
    "autonomyBoundaries": {
        "ai_modifiable": [],
        "human_gated": ["实验登记本体（交统筹）", "评估结论采纳"],
        "immutable": ["全自动策略搜索（30号文 §5 暂缓）", "GPU 多卡/集群抽象（约束二）"],
    },
    "healthCheck": {"heartbeat": "manual_trigger_only"},
}


def _default_gpu_stats() -> dict[str, Any]:
    from zephyr.trading.gpu_monitor import collect_gpu_stats

    return collect_gpu_stats()


def _check_vram(stats: dict[str, Any]) -> dict[str, Any]:
    """显存守卫：available 且占用 >= 硬上限 → refuse；采集不可用→降级放行留痕."""
    if not stats.get("available"):
        return {"guard": "not_available", "refused": False, "stats": stats}
    total = float(stats.get("memory_total_gb") or 0.0)
    used = float(stats.get("memory_used_gb") or 0.0)
    ratio = (used / total) if total > 0 else 0.0
    refused = ratio >= VRAM_HARD_LIMIT
    return {
        "guard": "refused_vram" if refused else "passed",
        "refused": refused,
        "memory_ratio": round(ratio, 4),
        "hard_limit": VRAM_HARD_LIMIT,
        "stats": stats,
    }


def run_algorithm_experiment_ticket(
    ticket: dict[str, Any],
    *,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    gpu_stats_provider: Callable[[], dict[str, Any]] | None = None,
    tracking_config: ExperimentTrackingConfig | None = None,
    cascade_router: Any | None = None,
    module_mapper: Any | None = None,
) -> dict[str, Any]:
    """执行一张算法实验工单（登记先于执行 + 显存守卫 + 只读评估，端到端落盘）.

    Args:
        ticket: {"ticket_id", "experiment_type", "target_id", "run_id", "component"?}.
        gpu_stats_provider: 可注入显存采集（默认 nvidia-smi 口径 collect_gpu_stats）.
        tracking_config: 可注入实验跟踪配置（默认 load_config；测试注入 fallback_dir）.
        cascade_router/module_mapper: S1.1 可选注入 11号文 cascade/13号文 ModuleMapper（默认 None 不接）.

    Returns:
        运行报告 dict（status：completed/refused_vram/evidence_missing）.
    """
    ticket_id = str(ticket.get("ticket_id") or "").strip()
    if not ticket_id:
        raise ValueError("算法实验工单缺 ticket_id")
    store = AgentRunStore(ROLE, runtime_dir=runtime_dir, repo_root=repo_root)
    store.begin(ticket_id, ticket)
    steps: list[str] = []

    # ① 实验登记先于执行：落待登记片段（注册表本体交统筹）
    registration = {
        "kind": "experiment_registration_pending",
        "status": "pending_registration",
        "experiment_type": str(ticket.get("experiment_type") or "model_evaluation"),
        "target_id": str(ticket.get("target_id") or ""),
        "run_id": str(ticket.get("run_id") or ""),
        "params_summary": ticket.get("params") or {},
        "note": "待登记凭证：REG-EXP-001 注册表本体由统筹登记；未登记不进入执行步",
    }
    store.write_output("experiment_registration.pending.json", registration, ticket_id)
    steps.append("registered")

    # S1.1 可选接线（默认 None 零行为变化）：cascade 模型选择 / ModuleMapper 模块裁决
    extras: dict[str, Any] = {}
    if cascade_router is not None:
        from zephyr.autonomy_core.agents import _s11_wiring

        extras["model_routing"] = _s11_wiring.route_experiment_model(ticket, cascade_router)
        store.write_output("model_routing.decision.json", extras["model_routing"], ticket_id)
        steps.append("model_routed" if extras["model_routing"]["status"] == "routed" else "model_route_skipped")
    if module_mapper is not None and str(ticket.get("experiment_type") or "") == "module_generation":
        from zephyr.autonomy_core.agents import _s11_wiring

        extras["module_mapping"] = _s11_wiring.map_module_generation(ticket, module_mapper)
        store.write_output("module_mapping.spec.json", extras["module_mapping"], ticket_id)
        steps.append("module_mapped" if extras["module_mapping"]["status"] == "mapped" else "module_map_error")

    # ② 显存守卫：<90% 硬上限，超阈值拒启动
    guard = _check_vram((gpu_stats_provider or _default_gpu_stats)())
    store.write_output("vram_guard.json", guard, ticket_id)
    steps.append(guard["guard"])
    if guard["refused"]:
        store.finish(ticket_id, "refused_vram", {"steps": steps})
        return {"status": "refused_vram", "steps": steps, "guard": guard, **extras}

    # ③ 执行步（Phase 0 只读形态）：读既有实验记录出评估报告
    run_id = str(ticket.get("run_id") or "")
    component = str(ticket.get("component") or "") or None
    detail = get_run(run_id, component=component, config=tracking_config) if run_id else None
    if detail is None:
        store.finish(ticket_id, "evidence_missing", {"steps": steps, "run_id": run_id})
        return {"status": "evidence_missing", "steps": steps, "run_id": run_id, **extras}
    evaluation = {
        "kind": "model_evaluation_report",
        "run_id": detail.run_id,
        "component": detail.component,
        "run_status": detail.status,
        "passed": detail.passed,
        "metrics": detail.metrics,
        "tags": detail.tags,
        "reproducible": bool(detail.artifact_paths),
        "note": "Phase 0 手动形态：本报告为既有实验记录的只读汇总，可复现性以 artifact 落盘为准",
    }
    store.write_output("evaluation_report.json", evaluation, ticket_id)
    steps.append("evaluated")
    store.finish(ticket_id, "completed", {"steps": steps, "run_id": run_id})
    return {"status": "completed", "steps": steps, "evaluation": evaluation, **extras}


def main(argv: list[str] | None = None) -> int:
    """CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR]."""
    parser = argparse.ArgumentParser(description="算法 Agent 薄入口：实验工单手动触发")
    parser.add_argument("--ticket", required=True, help="算法实验工单 JSON 路径")
    parser.add_argument("--runtime-dir", default=None, help="落盘根（默认仓根 .runtime/）")
    args = parser.parse_args(argv)
    ticket = json.loads(Path(args.ticket).read_text(encoding="utf-8"))
    report = run_algorithm_experiment_ticket(ticket, runtime_dir=args.runtime_dir)
    print(json.dumps({"status": report["status"], "steps": report["steps"]}, ensure_ascii=False))
    return 0


__all__ = [
    "AGENT_CARD",
    "ROLE",
    "VRAM_HARD_LIMIT",
    "main",
    "run_algorithm_experiment_ticket",
]


if __name__ == "__main__":
    raise SystemExit(main())
