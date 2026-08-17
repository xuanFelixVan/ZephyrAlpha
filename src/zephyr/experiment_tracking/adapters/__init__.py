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
M3: regime_adapter / feature_adapter / backtest_adapter / full_chain_adapter
"""
from __future__ import annotations

from typing import Final

__all__: Final = ["c1_adapter"]
