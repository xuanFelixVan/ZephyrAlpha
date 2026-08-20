# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.adapters
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker
# [CONSUMERS] zephyr.backtest.regime_validation.c1_runner ; (后续 regime/feature/backtest/full_chain)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 各 adapter 把领域对象→实验跟踪语义（params/metrics/artifacts/tags）；核心 tracker 零件无关
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 失败只记 stderr 不抛（不崩业务）
# [TESTS] tests/experiment_tracking/test_c1_adapter.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 各零件领域对象 → 实验跟踪语义适配器包（单一 JSON 后端，MLflow 已退役）。

M1: c1_adapter（C1ComparisonResult → tracking）
M4（50 号 §3 ⑥ 五零件接入）: regime_adapter（regime_detector 检测）/
    feature_adapter（regime_feature_builder 特征矩阵）/
    vectorized_adapter（vectorized_engine 回测）/
    strategy_runner_adapter（StrategyRunner 全链路）/
    c2c3_adapter（C2/C3 验证器）
全链路 lineage：各 adapter 的 lineage 参数把上游零件 run_id 写入 tags
（lineage_regime_run_id / lineage_feature_run_id / lineage_c1_run_id ...），
供 query/Panel 按 run 串联 regime→feature→backtest→C1 链。
"""
from __future__ import annotations

from typing import Final

__all__: Final = [
    "c1_adapter",
    "c2c3_adapter",
    "feature_adapter",
    "regime_adapter",
    "strategy_runner_adapter",
    "vectorized_adapter",
]
