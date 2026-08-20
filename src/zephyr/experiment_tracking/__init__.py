# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.config ; zephyr.experiment_tracking.experiment_tracker ; zephyr.experiment_tracking.models
# [CONSUMERS] zephyr.backtest.regime_validation.c1_runner ; zephyr.frontend.dashboard.components.experiment_history ; AI/人查询
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单一 FallbackBackend JSON；enable_tracking=False→NullBackend；tracking失败只记stderr不抛
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 调用失败→stderr warning 不抛（不崩业务）
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""

L_INFRA_TELEMETRY — 实验跟踪包（单一 JSON FallbackBackend，MLflow 已退役）。

统一实验跟踪入口：所有"零件"（C1 / regime_detector / 特征管道 / 回测引擎 / 全链路）的运行
记录到本地 JSON（logs/experiment_tracking_fallback/），人和 AI 都能通过 query 接口
或 Panel「实验历史」Tab 查询、对比、追溯。

命名说明: 包名 ``experiment_tracking``（非 ``observability``）——项目里 observability 是横切
概念（infrastructure/shared/security 各有 observability 子域），实验跟踪独占顶层 observability
会语义混淆，故本包取名 experiment_tracking。
详见 11_regime_backtest_validation_plan §2.3 命名冲突发现 + §9 决策 A。

公共 API:
    ExperimentTracker / get_tracker / reset_tracker — 跟踪器（单例工厂）
    RunContext — run 上下文管理器（with 语法）
    ExperimentTrackingConfig / load_config — 配置（环境变量覆盖）
    RunSummary / RunDetail — 数据模型（统一 JSON 源）

依据: 11_regime_backtest_validation_plan §3 ② + 51_panel_experiment_history_mlflow_retirement.md
Version: 0.2.0（MLflow 退役，单一 JSON 后端）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 实验跟踪使用方导入请求 模块导入
#   fields: 跟踪器/配置/数据模型符号访问（ExperimentTracker/get_tracker/RunContext/load_config/RunSummary 等）
#   code: zephyr.experiment_tracking L41-48
# 层: 算法
# - id: A1
#   name_zh: ① 公共 API 汇聚重导出
#   name_en: __init__ re-export
#   intro: 把 config/tracker/models 三个子模块的公共符号汇成统一入口
#   desc: from config/experiment_tracker/models 导入 8 个符号并列入 __all__，调用方只认包名不认子模块
#   inputs: I1
#   outputs: 统一公共 API 符号表
#   invariant: 单一 FallbackBackend JSON；enable_tracking=False→NullBackend；tracking 失败只记 stderr 不抛
# 层: 输出
# - id: O1
#   name_zh: 统一实验跟踪入口
#   name_en: experiment_tracking public API
#   intro: 所有零件（C1/regime_detector/特征管道/回测引擎）记录运行到本地 JSON(logs/experiment_tracking_fallback/) 的统一入口
#   invariant: 降级不崩业务（ERROR_CONTRACT: 失败仅 stderr warning）
#   downstream: zephyr.backtest.regime_validation.c1_runner；zephyr.frontend.dashboard.components.experiment_history；AI/人查询（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
