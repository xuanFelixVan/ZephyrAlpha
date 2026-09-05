# [BLUEPRINT] MOD-EXE-BIZ-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.2/§4-S0.3/§4-S1.3
# [MODULE] zephyr.autonomy_core.agents.business_agent_entry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.agents._registration_status（B16 拆出实现件，ROLE/ADVICE_ONLY_DISCLAIMER/两样例函数经此再导出） ; zephyr.autonomy_core.agents._g04_ops_check（§4-S1.3 薄委派，懒加载）
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_business_g04_ops_check.py ; 人手动触发（CLI）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯组装薄入口（注册表只读，真源=62号文 18 业务注册表）；产出 100% 落盘且标"仅建议"+human_gated；零交易执行路径——本模块不 import 任何下单/执行域包（zephyr.ex_core/ex_sor/trading），测试断言此不变量；S1.3 g04_strategy_ops_check=20号文三策略注册表+组件在位核对（仅建议语义）
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4 S0.3/S1.3 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 注册表不可读/条目不存在→产出件如实标 status=evidence_missing，不抛
# [TESTS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_business_g04_ops_check.py
# [A_module] module_id=MOD-EXE-BIZ-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
业务 Agent 薄入口（14号文 §3.2 因子/策略/组合运营，§4 S0.3 手动形态 + S1.3 G04 核对）.

B16 治本拆分（长城审计 §6#18，2026-09-05）：注册状态查询/因子候选评估实现拆至
_registration_status（本文件再导出，公共 API 与 CLI 行为不变），薄入口守 <200 行。

kind=registration_status（默认）：factor/strategy registry 状态汇总+单条目登记状态；
kind=factor_candidate_eval：status=candidate 候选条目评估建议文本；
kind=g04_strategy_ops_check（S1.3）：20号文首批三策略（打板/多因子/事件驱动）
注册表+组件在位核对（薄委派 _g04_ops_check）。产出物一律"仅建议"（advice_only=
true），不做自动交易决策/下单（交易决策属交易决策侧，§5-3）。
手动触发：python -m zephyr.autonomy_core.agents.business_agent_entry --ticket <path>

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ticket 参数
#   fields: 参数 ticket，类型注解 dict[str, Any]
#   code: business_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: runtime_dir 参数
#   fields: 参数 runtime_dir（无注解）
#   code: business_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: repo_root 参数
#   fields: 参数 repo_root（无注解）
#   code: business_agent_entry.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: argv 参数
#   fields: 参数 argv，类型注解 list[str] | None
#   code: business_agent_entry.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① query_registration_status
#   name_en: query_registration_status
#   intro: 样例①：注册状态查询（读 factor/strategy registry 状态汇总，端到端落盘）.
#   desc: 样例①：注册状态查询（读 factor/strategy registry 状态汇总，端到端落盘）.；源码 _registration_status.py（B16 拆出）
#   inputs: ticket runtime_dir repo_root
#   outputs: dict[str, Any]
# - id: A2
#   name_zh: ② draft_factor_candidate_evaluation
#   name_en: draft_factor_candidate_evaluation
#   intro: 样例②：因子候选评估工单（读候选条目出评估建议文本，仅建议）.
#   desc: 样例②：因子候选评估工单（读候选条目出评估建议文本，仅建议）.；源码 _registration_status.py（B16 拆出）
#   inputs: ticket runtime_dir repo_root
#   outputs: dict[str, Any]
# - id: A3
#   name_zh: ③ run_g04_strategy_ops_check
#   name_en: run_g04_strategy_ops_check
#   intro: S1.3 G04 三策略运营核对工单（20号文打板/多因子/事件驱动；
#   desc: S1.3 G04 三策略运营核对工单（20号文打板/多因子/事件驱动；薄委派 _g04_ops_check）.；源码 L150-L154
#   inputs: ticket
#   outputs: dict[str, Any]
# - id: A4
#   name_zh: ④ main
#   name_en: main
#   intro: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].
#   desc: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].；源码 L156-L173
#   inputs: argv
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_busi…
# - id: O2
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_busi…
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
# A4 --> O1
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Final

from zephyr.autonomy_core.agents._registration_status import (
    ADVICE_ONLY_DISCLAIMER,
    ROLE,
    draft_factor_candidate_evaluation,
    query_registration_status,
)

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "registration_status_query",
            "name": "因子/策略注册状态查询",
            "inputs": "注册表真源（只读）",
            "outputs": "注册状态报告（落盘）",
            "autonomyLevel": "L0_manual",
        },
        {
            "id": "factor_candidate_eval",
            "name": "因子候选评估工单起草",
            "inputs": "候选条目（status=candidate）",
            "outputs": "评估建议工单（仅建议）",
            "autonomyLevel": "L0_manual",
        },
        {
            "id": "g04_strategy_ops_check",
            "name": "S1.3 G04 三策略运营核对",
            "inputs": "注册表+组件在位（只读）",
            "outputs": "核对报告（仅建议）",
            "autonomyLevel": "L0_manual",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": [],
        "human_gated": ["全部产出（仅建议，人审后方可施工）"],
        "immutable": ["交易决策/下单（属交易决策侧）", "注册表本体"],
    },
    "healthCheck": {"heartbeat": "manual_trigger_only"},
}


def run_g04_strategy_ops_check(ticket: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """S1.3 G04 三策略运营核对工单（20号文打板/多因子/事件驱动；薄委派 _g04_ops_check）."""
    from zephyr.autonomy_core.agents import _g04_ops_check

    return _g04_ops_check.run_g04_strategy_ops_check(ticket, role=ROLE, **kwargs)


def main(argv: list[str] | None = None) -> int:
    """CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR]."""
    parser = argparse.ArgumentParser(description="业务 Agent 薄入口：注册查询/候选评估手动触发")
    parser.add_argument("--ticket", required=True, help="业务工单 JSON 路径")
    parser.add_argument("--runtime-dir", default=None, help="落盘根（默认仓根 .runtime/）")
    args = parser.parse_args(argv)
    ticket = json.loads(Path(args.ticket).read_text(encoding="utf-8"))
    handlers = {
        "registration_status": query_registration_status,
        "factor_candidate_eval": draft_factor_candidate_evaluation,
        "g04_strategy_ops_check": run_g04_strategy_ops_check,
    }
    handler = handlers.get(str(ticket.get("kind") or "registration_status"))
    if handler is None:
        raise ValueError(f"未知业务工单 kind: {ticket.get('kind')!r}")
    report = handler(ticket, runtime_dir=args.runtime_dir)
    print(json.dumps({"kind": report["kind"], "advice_only": report["advice_only"]}, ensure_ascii=False))
    return 0


__all__ = [
    "ADVICE_ONLY_DISCLAIMER",
    "AGENT_CARD",
    "ROLE",
    "draft_factor_candidate_evaluation",
    "main",
    "query_registration_status",
    "run_g04_strategy_ops_check",
]


if __name__ == "__main__":
    raise SystemExit(main())
