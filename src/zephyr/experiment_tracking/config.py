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
"""L_INFRA_TELEMETRY — 实验跟踪配置（fallback 目录 / 全局开关）。

从环境变量读取覆盖，ExperimentTrackingConfig 为不可变 dataclass。
enable_tracking=False（ZEPHYR_EXPERIMENT_TRACKING=0）时 get_tracker() 返回 NullTracker（no-op）。

环境变量:
  ZEPHYR_EXPERIMENT_TRACKING=0  → enable_tracking=False（全局关闭，NullBackend）

路径锚定: fallback_dir 默认锚 MAIN_REPO_ROOT（观测数据锚主仓防 worktree 分裂，
SSoT=zephyr.shared.io.paths §MAIN_REPO_ROOT 裁定），禁止 CWD 相对路径。

依据: 11_regime_backtest_validation_plan §3 ② 薄包装层设计 + 51_panel_experiment_history_mlflow_retirement.md 工作流 A3
Version: 0.2.1（fallback_dir 绝对路径锚定治本）
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from zephyr.shared.io.paths import MAIN_REPO_ROOT


@dataclass(frozen=True)
class ExperimentTrackingConfig:
    """实验跟踪配置——不可变。

    环境变量覆盖（优先级高于默认值）:
      ZEPHYR_EXPERIMENT_TRACKING=0  → enable_tracking=False（全局关闭，NullBackend）
    """
    fallback_dir: Path = MAIN_REPO_ROOT / "logs" / "experiment_tracking_fallback"
    enable_tracking: bool = True                  # 全局开关
    artifact_logging: bool = True                 # 是否落净值曲线 CSV（大数据量可关）


def load_config() -> ExperimentTrackingConfig:
    """从环境变量加载配置（覆盖默认值）。"""
    enable = os.environ.get("ZEPHYR_EXPERIMENT_TRACKING", "1") != "0"
    return ExperimentTrackingConfig(enable_tracking=enable)
