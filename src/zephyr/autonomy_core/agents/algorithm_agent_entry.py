# [BLUEPRINT] MOD-EXE-ALGO-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.3/§4-S0.4/§4-S1.1
# [MODULE] zephyr.autonomy_core.agents.algorithm_agent_entry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.agents._algorithm_experiment（B16 拆出实现件，run_algorithm_experiment_ticket/ROLE/VRAM_HARD_LIMIT 经此再导出）; zephyr.autonomy_core.agents._s11_wiring（§4-S1.1 可选接线，懒加载，经实现件）
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_execution_layer_s11_wiring.py ; 人手动触发（CLI）
# [STARTUP] manual
# [MATURITY] production
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

B16 治本拆分（长城审计 §6#18，2026-09-05）：实验工单实现（登记先于执行/显存守卫/
只读评估/S1.1 可选接线）拆至 _algorithm_experiment（本文件再导出，公共 API 与 CLI
行为不变），薄入口守 <200 行。

输入：算法实验工单（落盘 JSON：ticket_id/experiment_type/target_id/run_id/component）。
处理纪律（步骤顺序即验收口径，run.json steps 留痕，实现见 _algorithm_experiment）：
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

# [ALGO_FLOW] external: docs/03_modules/_domain_autonomy_core/algo_flow/agents/algorithm_agent_entry.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Final

from zephyr.autonomy_core.agents._algorithm_experiment import (
    ROLE,
    VRAM_HARD_LIMIT,
    run_algorithm_experiment_ticket,
)

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
