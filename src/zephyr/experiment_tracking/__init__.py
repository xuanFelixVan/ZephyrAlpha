# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.config ; zephyr.experiment_tracking.experiment_tracker ; zephyr.experiment_tracking.models
# [CONSUMERS] zephyr.backtest.regime_validation.c1_runner ; zephyr.frontend.dashboard.components.experiment_history ; AI/人查询
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] lazy import mlflow；未装→FallbackBackend(同接口)；enable_tracking=False→NullBackend；tracking失败只记stderr不抛
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 调用失败→stderr warning 不抛（不崩业务）
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪包（MLflow 薄包装 + 降级）。

统一实验跟踪入口：所有"零件"（C1 / regime_detector / 特征管道 / 回测引擎 / 全链路）的运行
记录到本地 MLflow（SQLite），人和 AI 都能通过 query 接口或 ``mlflow ui`` 查询、对比、追溯。

命名说明: 包名 ``experiment_tracking``（非 ``observability``）——项目里 observability 是横切
概念（infrastructure/shared/security 各有 observability 子域），实验跟踪独占顶层 observability
会语义混淆。MLflow 本质即 experiment tracking，故本包取名 experiment_tracking。
详见 discussion_002 §2.3 命名冲突发现 + §9 决策 A。

公共 API:
    ExperimentTracker / get_tracker / reset_tracker — 跟踪器（单例工厂）
    RunContext — run 上下文管理器（with 语法）
    ExperimentTrackingConfig / load_config — 配置（环境变量覆盖）
    RunSummary / RunDetail — 数据模型（屏蔽 MLflow vs 降级差异）

依据: discussion_002 §3 ② + backtest_observability_mlflow_plan.md M1
Version: 0.1.0
"""
from __future__ import annotations

from typing import Final

from zephyr.experiment_tracking.config import ExperimentTrackingConfig, load_config
from zephyr.experiment_tracking.experiment_tracker import (
    ExperimentTracker,
    RunContext,
    get_tracker,
    reset_tracker,
)
from zephyr.experiment_tracking.models import RunDetail, RunSummary

__all__: Final = [
    "ExperimentTracker",
    "ExperimentTrackingConfig",
    "RunContext",
    "RunDetail",
    "RunSummary",
    "get_tracker",
    "load_config",
    "reset_tracker",
]
