# [BLUEPRINT] MOD-EXE-BIZ-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S1.3
# [MODULE] zephyr.autonomy_core.agents._g04_ops_check
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pyyaml ; zephyr.autonomy_core.agents._run_store ; zephyr.autonomy_core.agents.business_agent_entry（ADVICE_ONLY_DISCLAIMER 沿用）
# [CONSUMERS] zephyr.autonomy_core.agents.business_agent_entry（懒加载薄委派）; tests/autonomy/test_business_g04_ops_check.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 注册表/catalogs 一律只读（不写不改）；组件在位性=只读文件存在性检查（20号文 §2.7 设施盘点清单+2026-08-21 sleeve 落码回填）；产出仅建议语义（ADVICE_ONLY_DISCLAIMER 沿用），100% human_gated 落盘；不写注册表本体
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4-S1.3 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 注册表不可读→对应策略 registry.status=evidence_missing 且总报告 status=evidence_missing，不抛
# [TESTS] tests/autonomy/test_business_g04_ops_check.py
# [A_module] module_id=MOD-EXE-BIZ-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""S1.3 业务 Agent U7 深化：G04 三策略运营核对件（14号文 §4-S1.3）.

对 20号文首批三策略（打板 daban / 多因子 multifactor / 事件驱动 event_driven）做
因子-策略-组合状态核对，产出缺口清单（仅建议语义）：
  ①注册表侧：strategy_registry 该策略类条目状态分布 + code_path/evidence 缺口；
    factor_registry 关联因子（belongs_to_strategies 指向本策略条目者）的
    evidence/algorithm_status 状态；
  ②组件在位性：G04_COMPONENTS 清单（20号文 §2.7 设施盘点锚定）只读存在性检查；
  ③产出 g04_strategy_ops_check.json 核对报告（差异/缺口清单，仅建议，人审定夺）。
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.autonomy_core.agents._run_store import AgentRunStore
from zephyr.autonomy_core.agents.business_agent_entry import ADVICE_ONLY_DISCLAIMER

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
BLUEPRINT_REF: Final[str] = "20_first_batch_strategies.md §2.2-2.4/§2.7"
G04_STRATEGY_CLASSES: Final[tuple[str, ...]] = ("daban", "multifactor", "event_driven")
G04_STRATEGY_NAMES: Final[dict[str, str]] = {
    "daban": "打板", "multifactor": "多因子", "event_driven": "事件驱动",
}
_CATALOGS: Final[dict[str, tuple[str, str]]] = {
    "strategy": ("docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml", "strategies"),
    "factor": ("docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", "factors"),
}

# 组件在位性清单（锚定 20号文 §2.7 设施盘点 + 2026-08-21 三 sleeve 策略类落码回填）
G04_COMPONENTS: Final[dict[str, tuple[str, ...]]] = {
    "daban": (
        "src/zephyr/signal_ashare/short_term_stock_selector.py",
        "src/zephyr/signal_ashare/institutional_behavior_analyzer.py",
        "src/zephyr/signal_ashare/youzi_relay_emotion_engine.py",
        "src/zephyr/signal_ashare/quant_short_term_strength_engine.py",
        "src/zephyr/signal_ashare/dual_engine_fusion_decision_engine.py",
        "src/zephyr/pf_core/strategies/daban_sleeve_strategy.py",
    ),
    "multifactor": (
        "src/zephyr/factor/factor_factory.py",
        "src/zephyr/factor/alpha_signal_pipeline.py",
        "src/zephyr/factor/momentum_factor.py",
        "src/zephyr/factor/value_factor.py",
        "src/zephyr/factor/analysis/ic_ir_calc.py",
        "src/zephyr/factor/analysis/multifactor_synthesis.py",
        "src/zephyr/factor/analysis/factor_optimization.py",
        "src/zephyr/factor/governance/engine.py",
        "src/zephyr/pf_core/strategies/multifactor_sleeve_strategy.py",
    ),
    "event_driven": (
        "src/zephyr/signal_ashare/intraday_buy_sell_point_analyzer.py",
        "src/zephyr/signal_ashare/event_driven_screener.py",
        "src/zephyr/data/news_collector.py",
        "src/zephyr/pf_core/strategies/event_driven_sleeve_strategy.py",
    ),
}


def _load_entries(path: Path, key: str) -> list[dict[str, Any]] | None:
    """只读加载注册表条目（不可读/解析失败返回 None，由调用方标 evidence_missing）."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    entries = data.get(key) if isinstance(data, dict) else None
    return [e for e in entries if isinstance(e, dict)] if isinstance(entries, list) else None


def _check_components(strategy_class: str, root: Path) -> dict[str, Any]:
    """组件在位性：20号文 §2.7 清单只读存在性检查（不读内容、不写）."""
    expected = list(G04_COMPONENTS[strategy_class])
    in_place = [rel for rel in expected if (root / rel).is_file()]
    missing = [rel for rel in expected if not (root / rel).is_file()]
    return {"expected": len(expected), "in_place": in_place, "missing": missing}


def _check_strategy(
    strategy_class: str,
    strategies: list[dict[str, Any]] | None,
    factors: list[dict[str, Any]] | None,
    root: Path,
) -> dict[str, Any]:
    """单策略核对：注册表条目状态 + 关联因子 evidence 状态 + 组件在位性 + 缺口."""
    gaps: list[str] = []
    components = _check_components(strategy_class, root)
    if components["missing"]:
        gaps.append(f"{strategy_class}: 组件缺位（{BLUEPRINT_REF} 清单）: {components['missing']}")

    if strategies is None:
        gaps.append(f"{strategy_class}: 策略注册表不可读（evidence_missing）")
        registry: dict[str, Any] = {"status": "evidence_missing"}
        entry_ids: list[str] = []
    else:
        entries = [e for e in strategies if str(e.get("strategy_class") or "") == strategy_class]
        entry_ids = [str(e.get("strategy_id")) for e in entries]
        no_code = [sid for sid, e in zip(entry_ids, entries) if not str(e.get("code_path") or "").strip()]
        no_evidence = [sid for sid, e in zip(entry_ids, entries) if not str(e.get("evidence") or "").strip()]
        registry = {
            "status": "ok",
            "entry_count": len(entries),
            "status_counts": dict(Counter(str(e.get("status") or "unknown") for e in entries)),
            "entry_ids": entry_ids,
            "entries_without_code_path": no_code,
            "entries_without_evidence": no_evidence,
        }
        if not entries:
            gaps.append(f"{strategy_class}: strategy_registry 无该策略类条目（20号文首批三策略之一未登记）")
        if no_code:
            gaps.append(f"{strategy_class}: {len(no_code)} 条策略 code_path 为空（设计态未落码锚点）: {no_code}")
        if no_evidence:
            gaps.append(f"{strategy_class}: {len(no_evidence)} 条策略 evidence 为空（未回测）: {no_evidence}")

    if factors is None:
        gaps.append(f"{strategy_class}: 因子注册表不可读（evidence_missing）")
        linked = {"count": 0, "factor_ids": [], "evidence_missing": [], "pending_backtest": []}
    else:
        linked_entries = [f for f in factors
                          if {str(s) for s in (f.get("belongs_to_strategies") or [])} & set(entry_ids)]
        linked_ids = [str(f.get("factor_id")) for f in linked_entries]
        f_no_evidence = [fid for fid, f in zip(linked_ids, linked_entries)
                         if not str(f.get("evidence") or "").strip()]
        f_pending = [fid for fid, f in zip(linked_ids, linked_entries)
                     if str(f.get("algorithm_status") or "") == "pending_backtest"]
        linked = {"count": len(linked_ids), "factor_ids": linked_ids,
                  "evidence_missing": f_no_evidence, "pending_backtest": f_pending}
        if not linked_ids:
            gaps.append(f"{strategy_class}: factor_registry 无关联因子挂接"
                        "（belongs_to_strategies 未指向本策略条目）")
        if f_no_evidence:
            gaps.append(f"{strategy_class}: 关联因子未回测（evidence 为空）: {f_no_evidence}")
        if f_pending:
            gaps.append(f"{strategy_class}: 关联因子待回测（algorithm_status=pending_backtest）: {f_pending}")

    return {"strategy_class": strategy_class, "name_zh": G04_STRATEGY_NAMES[strategy_class],
            "registry": registry, "linked_factors": linked, "components": components,
            "gaps": gaps}


def run_g04_strategy_ops_check(
    ticket: dict[str, Any],
    *,
    role: str,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    catalogs: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """执行一张 G04 三策略运营核对工单（端到端落盘，仅建议语义）.

    Args:
        ticket: {"ticket_id", "kind"="g04_strategy_ops_check", ...}.
        catalogs: 可选注册表夹具注入（{"strategies": [...], "factors": [...]}；
                  None=只读加载仓内真源 catalogs YAML）.

    Returns:
        核对报告 dict（status：completed/evidence_missing；gaps 缺口清单）.
    """
    ticket_id = str(ticket.get("ticket_id") or "").strip() or "g04-ops-check"
    root = Path(repo_root) if repo_root else _REPO_ROOT
    store = AgentRunStore(role, runtime_dir=runtime_dir, repo_root=root)
    store.begin(ticket_id, ticket)

    if catalogs is None:
        strategies = _load_entries(root / _CATALOGS["strategy"][0], _CATALOGS["strategy"][1])
        factors = _load_entries(root / _CATALOGS["factor"][0], _CATALOGS["factor"][1])
    else:
        strategies = catalogs.get("strategies")
        factors = catalogs.get("factors")

    per_strategy = {cls: _check_strategy(cls, strategies, factors, root)
                    for cls in G04_STRATEGY_CLASSES}
    gaps = [gap for cls in G04_STRATEGY_CLASSES for gap in per_strategy[cls]["gaps"]]
    status = "evidence_missing" if (strategies is None or factors is None) else "completed"
    report = {
        "kind": "g04_strategy_ops_check",
        "advice_only": True,
        "disclaimer": ADVICE_ONLY_DISCLAIMER,
        "blueprint_ref": BLUEPRINT_REF,
        "status": status,
        "strategies": per_strategy,
        "gaps": gaps,
        "gap_count": len(gaps),
        "note": "缺口清单仅建议语义：人审决定是否立整改工单，本报告不触发任何自动动作",
    }
    store.write_output("g04_strategy_ops_check.json", report, ticket_id)
    store.finish(ticket_id, status, {"gaps": len(gaps)})
    return report


__all__ = ["BLUEPRINT_REF", "G04_COMPONENTS", "G04_STRATEGY_CLASSES", "run_g04_strategy_ops_check"]
