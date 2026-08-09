# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.config
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.experiment_tracking.experiment_tracker ; zephyr.experiment_tracking.query
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配置不可变(frozen)；环境变量覆盖默认值；enable_tracking=False 时全局 no-op
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无（纯配置）
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪配置（MLflow tracking_uri / 降级目录 / 全局开关）。

从环境变量读取覆盖，ExperimentTrackingConfig 为不可变 dataclass。
enable_tracking=False（ZEPHYR_EXPERIMENT_TRACKING=0）时 get_tracker() 返回 NullTracker（no-op）。

环境变量:
  ZEPHYR_EXPERIMENT_TRACKING=0  → enable_tracking=False（全局关闭，NullBackend）
  ZEPHYR_TRACKING_URI=...       → tracking_uri（默认本地 SQLite）

依据: 11_regime_backtest_validation_plan §3 ② 薄包装层设计 + backtest_observability_mlflow_plan.md M1
Version: 0.1.0
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentTrackingConfig:
    """实验跟踪配置——不可变。

    环境变量覆盖（优先级高于默认值）:
      ZEPHYR_EXPERIMENT_TRACKING=0  → enable_tracking=False（全局关闭，NullBackend）
      ZEPHYR_TRACKING_URI=...       → tracking_uri（默认本地 SQLite）
    """
    tracking_uri: str = "sqlite:///logs/mlflow.db"
    experiment_prefix: str = "zephyr-"           # experiment 名前缀（component → zephyr-{component}）
    fallback_dir: Path = Path("logs/experiment_tracking_fallback")
    enable_tracking: bool = True                  # 全局开关
    artifact_logging: bool = True                 # 是否落净值曲线 CSV（大数据量可关）


def load_config() -> ExperimentTrackingConfig:
    """从环境变量加载配置（覆盖默认值）。"""
    enable = os.environ.get("ZEPHYR_EXPERIMENT_TRACKING", "1") != "0"
    uri = os.environ.get("ZEPHYR_TRACKING_URI", "sqlite:///logs/mlflow.db")
    return ExperimentTrackingConfig(
        tracking_uri=uri,
        enable_tracking=enable,
    )
