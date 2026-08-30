# [BLUEPRINT] MOD-EXE-BIZ-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §3.2/§4-S0.3/§4-S1.3
# [MODULE] zephyr.autonomy_core.agents.business_agent_entry
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pyyaml ; zephyr.autonomy_core.agents._run_store ; zephyr.autonomy_core.agents._g04_ops_check（§4-S1.3 薄委派，懒加载）
# [CONSUMERS] tests/autonomy/test_execution_layer_agent_entries.py ; tests/autonomy/test_business_g04_ops_check.py ; 人手动触发（CLI）
# [STARTUP] manual
# [MATURITY] testing
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
#   desc: 样例①：注册状态查询（读 factor/strategy registry 状态汇总，端到端落盘）.；源码 L166-L207
#   inputs: ticket runtime_dir repo_root
#   outputs: dict[str, Any]
# - id: A2
#   name_zh: ② draft_factor_candidate_evaluation
#   name_en: draft_factor_candidate_evaluation
#   intro: 样例②：因子候选评估工单（读候选条目出评估建议文本，仅建议）.
#   desc: 样例②：因子候选评估工单（读候选条目出评估建议文本，仅建议）.；源码 L210-L242
#   inputs: ticket runtime_dir repo_root
#   outputs: dict[str, Any]
# - id: A3
#   name_zh: ③ run_g04_strategy_ops_check
#   name_en: run_g04_strategy_ops_check
#   intro: S1.3 G04 三策略运营核对工单（20号文打板/多因子/事件驱动；
#   desc: S1.3 G04 三策略运营核对工单（20号文打板/多因子/事件驱动；薄委派 _g04_ops_check）.；源码 L265-L269
#   inputs: ticket
#   outputs: dict[str, Any]
# - id: A4
#   name_zh: ④ main
#   name_en: main
#   intro: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].
#   desc: CLI 手动触发入口：--ticket <工单 JSON 路径> [--runtime-dir DIR].；源码 L272-L289
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
from collections import Counter
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.autonomy_core.agents._run_store import AgentRunStore

ROLE: Final[str] = "business"
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
_REGISTRIES: Final[dict[str, tuple[str, str, str]]] = {
    "factor": ("docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", "factors", "factor_id"),
    "strategy": (
        "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml",
        "strategies",
        "strategy_id",
    ),
}
ADVICE_ONLY_DISCLAIMER: Final[str] = "仅建议：本产出为运营辅助建议，不构成任何交易指令，落地需人审。"

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


def _load_entries(path: Path, key: str) -> list[dict[str, Any]] | None:
    """读注册表条目列表（不可读/解析失败返回 None，由调用方标 evidence_missing）."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    entries = data.get(key) if isinstance(data, dict) else None
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else None


def query_registration_status(
    ticket: dict[str, Any],
    *,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """样例①：注册状态查询（读 factor/strategy registry 状态汇总，端到端落盘）."""
    ticket_id = str(ticket.get("ticket_id") or "").strip() or "biz-status"
    root = Path(repo_root) if repo_root else _REPO_ROOT
    store = AgentRunStore(ROLE, runtime_dir=runtime_dir, repo_root=root)
    store.begin(ticket_id, ticket)

    registries: dict[str, Any] = {}
    for name, (rel, key, id_field) in _REGISTRIES.items():
        entries = _load_entries(root / rel, key)
        if entries is None:
            registries[name] = {"status": "evidence_missing", "registry": rel}
            continue
        wanted = str(ticket.get(id_field) or "")
        hit = next((e for e in entries if str(e.get(id_field)) == wanted), None) if wanted else None
        registries[name] = {
            "registry": rel,
            "total_entries": len(entries),
            "status_counts": dict(Counter(str(e.get("status") or "unknown") for e in entries)),
            "queried_id": wanted or None,
            "entry": hit,
            "entry_found": (hit is not None) if wanted else None,
        }
    report = {
        "kind": "registration_status",
        "advice_only": True,
        "disclaimer": ADVICE_ONLY_DISCLAIMER,
        "registries": registries,
    }
    store.write_output("registration_status.json", report, ticket_id)
    missing = any(r.get("status") == "evidence_missing" for r in registries.values())
    store.finish(
        ticket_id,
        "evidence_missing" if missing else "completed",
        {k: v.get("total_entries") for k, v in registries.items()},
    )
    return report


def draft_factor_candidate_evaluation(
    ticket: dict[str, Any],
    *,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """样例②：因子候选评估工单（读候选条目出评估建议文本，仅建议）."""
    ticket_id = str(ticket.get("ticket_id") or "").strip() or "biz-candidate-eval"
    root = Path(repo_root) if repo_root else _REPO_ROOT
    store = AgentRunStore(ROLE, runtime_dir=runtime_dir, repo_root=root)
    store.begin(ticket_id, ticket)

    rel, key, _ = _REGISTRIES["factor"]
    entries = _load_entries(root / rel, key) or []
    wanted = [str(x) for x in ticket.get("factor_ids") or []]
    pool = [e for e in entries if str(e.get("status")) == "candidate"]
    if wanted:
        pool = [e for e in pool if str(e.get("factor_id")) in wanted]
    limit = int(ticket.get("limit") or 3)
    suggestions = [_candidate_advice(e) for e in pool[:limit]]
    status = "completed" if entries else "evidence_missing"
    report = {
        "kind": "factor_candidate_eval",
        "advice_only": True,
        "disclaimer": ADVICE_ONLY_DISCLAIMER,
        "status": status,
        "registry": rel,
        "candidate_pool_size": len(pool),
        "candidates": suggestions,
    }
    store.write_output("factor_candidate_eval.json", report, ticket_id)
    store.finish(ticket_id, status, {"evaluated": len(suggestions), "pool": len(pool)})
    return report


def _candidate_advice(entry: dict[str, Any]) -> dict[str, Any]:
    """按注册表已登记字段拼装评估建议（零新业务逻辑：只复述缺口，不下结论）."""
    gaps: list[str] = []
    if not str(entry.get("evidence") or "").strip():
        gaps.append("回测证据为空，建议先排期 PIT 合规回测再评估 IC/IR")
    if str(entry.get("algorithm_status") or "") == "pending_backtest":
        gaps.append("algorithm_status=pending_backtest，尚未量化回测")
    if not str(entry.get("code_path") or "").strip():
        gaps.append("code_path 未落地（设计态），建议登记代码锚点后再进候选评审")
    if not gaps:
        gaps.append("登记字段齐备，建议进人工候选评审（回测口径复核）")
    return {
        "factor_id": entry.get("factor_id"),
        "name": entry.get("name"),
        "factor_class": entry.get("factor_class"),
        "suggestion_zh": "；".join(gaps) + "。（仅建议，人审定夺）",
        "human_gated": True,
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
