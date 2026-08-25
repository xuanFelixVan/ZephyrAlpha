# [BLUEPRINT] MOD-PLAN-000 | (plan_engine package init)
# [MODULE] zephyr.plan_engine
# [DOMAIN] D_TRADING
# [TTL] permanent
# [A_module] module_id=MOD-UNK-plan_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from typing import Final

from zephyr.plan_engine import (
    auction_hit_recorder,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-015）
    batch_boundary_runner,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-012）
    boundary_revision_engine,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-006）
    brier_calibration,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-010）
    closing_session_decision,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-003）
    daily_trade_plan,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-011）
    evidence_chain_decision,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-SIG-076，GAP-F-42）
    llm_premarket_analysis,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-007）
    overnight_boundary_reviser,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-004）
    premarket_constraint_loader,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-002）
    # NOTE(2026-08-25, W-P1-19): scaffold 注册器类级 eager import 非法插入
    # import 块内（`from zephyr.plan_engine.premarket_workflow import
    # PremarketWorkflow`，语法错误级），已归一为模块名条目按字母序入列
    # （#ARCH-242 同型复发）。
    premarket_workflow,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-021）
    scenario_attribution_stats,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-009）
    scenario_plan_recorder,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-008）
    scenario_planner,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-005）
    # NOTE(2026-08-25, W-P1-19): scaffold 注册器将类级 eager import 非法插入
    # 本 import 块内（`from zephyr.plan_engine.scenario_playbook import ScenarioPlaybook`
    # 插在括号中造成语法错误），已归一为模块名条目按字母序入列（#ARCH-242 同型复发）。
    scenario_playbook,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-019）
    scenario_probability_model,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-017）
    sit_out_list,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-014）
    tomorrow_boundary_planner,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-001）
    # NOTE(2026-08-25, W-P1-19): scaffold 注册器类级 eager import 非法插入
    # import 块内（`from zephyr.plan_engine.track_fusion import TrackFusion`，
    # 语法错误级），已归一为模块名条目按字母序入列（#ARCH-242 同型复发）。
    track_fusion,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-020）
    trading_debate,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-013）
    trading_analyst_agents,  # noqa: F401  # ORPHAN-MODULE: 引用登记（MOD-PLAN-013 扩展，GAP-F-44）
)

__all__: Final = [
    "tomorrow_boundary_planner",
    "premarket_constraint_loader",
    "premarket_workflow",
    "closing_session_decision",
    "overnight_boundary_reviser",
    "scenario_planner",
    "scenario_playbook",
    "boundary_revision_engine",
    "llm_premarket_analysis",
    "scenario_plan_recorder",
    "scenario_attribution_stats",
    "brier_calibration",
    "daily_trade_plan",
    "batch_boundary_runner",
    "trading_debate",
    "trading_analyst_agents",
    "evidence_chain_decision",
    "sit_out_list",
    "auction_hit_recorder",
    "scenario_probability_model",
    "track_fusion",
]
