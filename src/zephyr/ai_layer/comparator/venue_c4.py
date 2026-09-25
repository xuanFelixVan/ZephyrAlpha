# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.venue_c4
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator (import_ruler/ruler_available/VenueUnavailable);
#                zephyr.backtest.regime_validation.c4_deflated_sharpe_runner (DSR 批量考尺，SSOT 引用不复制);
#                zephyr.strategy_pipeline.screen_source (fetch_bothwin 台账真源)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (claim_exam 注册表项)
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 薄封装零复制考尺逻辑（D-L4-01：只转调既有件，DSR/双窗判据 SSOT 在考尺模块）；
#              调不到考尺=fail-closed 拒考（VenueUnavailable，DESIGN C4 验收标准）；
#              考场边界自守：verdict 只是证据，不构成任何策略上线/转正动作（DESIGN §2.1 边界声明）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.1（算法选型行=制式真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 考尺 import 失败→VenueUnavailable；未知 op→ValueError；payload 缺键→KeyError
#                  （调用方=executor 预检后传入，键契约见 run() docstring）
# [TESTS] tests/ai_layer/comparator/test_venues.py（available 正反/import 注入 fail-closed/
#         dsr_batch+bothwin 转调/未知 op 拒绝/四适配器制式一致性）
# [TTL] permanent
"""venue_c4 — 算法/策略考场适配器：C4 双窗锦标赛制式的薄封装（D-L4-02）。

制式（DESIGN §2.1，全部转调既有件，本件零考尺逻辑）::

    IS 冻结窗初赛（2020-01-01..2023-12-31，84 件规模已验证）
    → OOS 窗复赛（双窗齐才 emit）
    → DSR 批内折减（c4_deflated_sharpe_runner = DSR SSOT）
    → BHY FDR 多重校正（常量层 fdr_q；BHY 计算复用 factor.analysis.bhy_fdr，由 too_good 查③消费）
    → bothwin 终裁（IS>0 ∧ 各 OOS 段>0 ∧ decay<0.5，台账=screen_source.fetch_bothwin）

锦标赛截断（N≥5 取前 K）在 executor.shortlist_top_k（纯函数），不在本件。
"""

from __future__ import annotations

import functools

from typing import Any, Final, Mapping

from zephyr.ai_layer.comparator import import_ruler, make_available_probe, ruler_available

__all__: Final = ["RULER_MODULES", "VENUE_ID", "available", "criteria", "run"]

VENUE_ID: Final = "venue_c4"
RULER_MODULES: Final = (
    "zephyr.backtest.regime_validation.c4_deflated_sharpe_runner",
    "zephyr.strategy_pipeline.screen_source",
)
IS_FROZEN_WINDOW: Final = "2020-01-01..2023-12-31"   # DESIGN §1③ 现行冻结窗（制式描述，非考尺逻辑）


# FUNCTION-DUP 治本（2026-09-24 st-ailayer-final-20260924）：available 与兄弟考场同体，partial 绑定唯一实现 ruler_available
available = make_available_probe(RULER_MODULES, globals())


def criteria() -> dict[str, Any]:
    """考尺判据快照（预注册时冻进 experiment 卡）：制式描述+考尺模块指纹。"""
    return {
        "venue": VENUE_ID,
        "is_frozen_window": IS_FROZEN_WINDOW,
        "tournament_rounds": 2,
        "ruler_modules": list(RULER_MODULES),
        "bothwin_rule": "IS>0 and each OOS segment>0 and decay<bothwin_decay_max(policy)",
    }


def run(payload: Mapping[str, Any]) -> dict[str, Any]:
    """转调考尺（op 分派，零逻辑复制）。

    ops::

        dsr_batch  {returns_by_variant: {名: 收益序列}, num_trials?: int}
                   → c4_deflated_sharpe_runner.run_deflated_sharpe_batch
        bothwin    {} → screen_source.fetch_bothwin()（现行冠军=台账 bothwin 现役集）
    """
    op = str(payload.get("op") or "")
    if op == "dsr_batch":
        runner = import_ruler(RULER_MODULES[0])
        report = runner.run_deflated_sharpe_batch(
            payload["returns_by_variant"], num_trials=payload.get("num_trials")
        )
        return {"venue": VENUE_ID, "op": op, "passed": bool(getattr(report, "passed", False)),
                "report": report}
    if op == "bothwin":
        screen = import_ruler(RULER_MODULES[1])
        return {"venue": VENUE_ID, "op": op, "rows": screen.fetch_bothwin()}
    raise ValueError(f"venue_c4 unknown_op:{op}")
