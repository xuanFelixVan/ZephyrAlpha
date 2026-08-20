# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.experiment_tracker
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.config ; zephyr.experiment_tracking.fallback_tracker
# [CONSUMERS] zephyr.experiment_tracking.adapters.c1_adapter ; zephyr.experiment_tracking.query
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单一 FallbackBackend JSON；enable_tracking=False→NullBackend；tracking失败只记stderr不抛
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 调用失败→stderr warning 不抛（不崩业务）；RunContext 内业务异常正常传播
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪器主类（单一 JSON FallbackBackend，MLflow 已退役）。

Zephyr 语义 → 存储映射:
  component (零件类型) → 子目录名 (logs/experiment_tracking_fallback/{component}/)
  一次运行            → {run_id}/run_meta.json（params/metrics/tags/status/artifacts）
  指标               → metrics (baseline_/experiment_ 前缀)
  配置               → params
  产物               → artifacts (nav CSV / report MD / ...，写 run 目录)
  语义标签           → tags

后端机制:
  - enable_tracking=True  → FallbackBackend（写 logs/experiment_tracking_fallback/{component}/{run_id}/run_meta.json）
  - enable_tracking=False（ZEPHYR_EXPERIMENT_TRACKING=0）→ _NullBackend（no-op）
  - 所有 log 调用包 try/except，失败只记 stderr 不抛——业务回测不受 tracking 失败影响

依据: 11_regime_backtest_validation_plan §3 ② + 51_panel_experiment_history_mlflow_retirement.md 工作流 A
SSoT: depgraph MOD-OBS-001
Version: 0.2.0（MLflow 退役，单一 JSON 后端）
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Optional

from zephyr.experiment_tracking.config import ExperimentTrackingConfig, load_config
from zephyr.experiment_tracking.fallback_tracker import FallbackBackend

_logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# RunContext — run 上下文管理器
# ──────────────────────────────────────────────────────────────────────────────


class RunContext:
    """单次 run 的上下文管理器。

    用法:
        with tracker.start_run("c1-validation", tags={...}) as run:
            run.log_params({...})
            run.log_metrics({...})
            run.log_artifact_bytes(csv_bytes, "nav_curve.csv")

    __exit__ 语义:
      - 正常退出 → end_run("FINISHED")
      - 异常退出 → end_run("FAILED")，但**不吞异常**（return False → 异常正常传播）
      - log_xxx 内部失败已 try/except 兜住，不会触发异常退出
    """

    def __init__(self, backend: Any, run_id: str, component: str, run_name: str) -> None:
        self._backend = backend
        self.run_id = run_id
        self._component = component
        self.run_name = run_name

    def __enter__(self) -> "RunContext":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        status = "FAILED" if exc_type is not None else "FINISHED"
        try:
            self._backend.end_run(status)
        except Exception as e:  # noqa: BLE001 — tracking 收尾失败不阻断
            print(f"[zephyr.experiment_tracking] end_run 失败(忽略): {e}", file=sys.stderr)
        return False  # 不吞异常

    def log_params(self, params: dict[str, Any]) -> None:
        try:
            self._backend.log_params(params)
        except Exception as e:  # noqa: BLE001 — tracking 失败不崩业务
            print(f"[zephyr.experiment_tracking] log_params 失败(忽略): {e}", file=sys.stderr)

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        try:
            self._backend.log_metrics(metrics, step)
        except Exception as e:  # noqa: BLE001
            print(f"[zephyr.experiment_tracking] log_metrics 失败(忽略): {e}", file=sys.stderr)

    def log_artifact(self, local_path: str | Path, artifact_path: str | None = None) -> None:
        try:
            self._backend.log_artifact(str(local_path), artifact_path)
        except Exception as e:  # noqa: BLE001
            print(f"[zephyr.experiment_tracking] log_artifact 失败(忽略): {e}", file=sys.stderr)

    def log_artifact_bytes(self, data: bytes, filename: str, artifact_path: str | None = None) -> None:
        try:
            self._backend.log_artifact_bytes(data, filename, artifact_path)
        except Exception as e:  # noqa: BLE001
            print(f"[zephyr.experiment_tracking] log_artifact_bytes 失败(忽略): {e}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────────────────────
# Backend 抽象 —— FallbackBackend / NullBackend 共同接口
# ──────────────────────────────────────────────────────────────────────────────


class _NullBackend:
    """enable_tracking=False 时的 no-op backend（所有方法空实现）。"""

    def start_run(self, component: str, run_name: str | None, tags: dict | None) -> str:
        return "null-run"

    def log_params(self, params: dict[str, Any]) -> None:
        pass

    def log_metrics(self, metrics: dict[str, float], step: int | None) -> None:
        pass

    def log_artifact(self, local_path: str, artifact_path: str | None) -> None:
        pass

    def log_artifact_bytes(self, data: bytes, filename: str, artifact_path: str | None) -> None:
        pass

    def end_run(self, status: str) -> None:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# ExperimentTracker 主类
# ──────────────────────────────────────────────────────────────────────────────


class ExperimentTracker:
    """统一实验跟踪入口（单一 JSON 后端）。

    自动选择 backend:
      - enable_tracking=False → _NullBackend
      - 否则                 → FallbackBackend（JSON）
    """

    def __init__(self, config: ExperimentTrackingConfig | None = None) -> None:
        self._config = config or load_config()
        self._backend = self._make_backend()

    def _make_backend(self) -> Any:
        if not self._config.enable_tracking:
            return _NullBackend()
        return FallbackBackend(self._config.fallback_dir)

    @property
    def available(self) -> bool:
        """跟踪是否启用（False = 关闭模式 NullBackend）。"""
        return self._config.enable_tracking

    @property
    def config(self) -> ExperimentTrackingConfig:
        return self._config

    def start_run(
        self,
        component: str,
        run_name: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> RunContext:
        """开启一个 run。component 映射到 experiment 名（zephyr-{component}）。"""
        run_id = self._backend.start_run(component, run_name, tags)
        return RunContext(self._backend, run_id, component, run_name or component)


# ──────────────────────────────────────────────────────────────────────────────
# 单例工厂
# ──────────────────────────────────────────────────────────────────────────────

_tracker_singleton: ExperimentTracker | None = None


def get_tracker() -> ExperimentTracker:
    """获取全局 tracker 单例（首次调用按 config 初始化）。"""
    global _tracker_singleton
    if _tracker_singleton is None:
        _tracker_singleton = ExperimentTracker()
    return _tracker_singleton


def reset_tracker() -> None:
    """重置单例（测试用：改环境变量后重新初始化）。"""
    global _tracker_singleton
    _tracker_singleton = None
