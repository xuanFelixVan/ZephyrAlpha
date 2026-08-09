# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.experiment_tracker
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] mlflow(optional) ; zephyr.experiment_tracking.config ; zephyr.experiment_tracking.fallback_tracker
# [CONSUMERS] zephyr.experiment_tracking.adapters.c1_adapter ; zephyr.experiment_tracking.query
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] lazy import mlflow；未装→FallbackBackend(同接口)；enable_tracking=False→NullBackend；tracking失败只记stderr不抛
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 调用失败→stderr warning 不抛（不崩业务）；RunContext 内业务异常正常传播
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪器主类（MLflow 薄包装 + lazy import + 降级）。

Zephyr 语义 → MLflow 映射:
  component (零件类型) → experiment 名 (zephyr-{component})
  一次运行            → run (run_name={component}_{mode}_{timestamp})
  指标               → metrics (baseline_/experiment_ 前缀)
  配置               → params
  产物               → artifacts (nav CSV / report MD / ...)
  语义标签           → tags

降级机制:
  - mlflow 未装 → FallbackBackend（写 logs/experiment_tracking_fallback/{component}/{run_id}/run_meta.json）
  - enable_tracking=False（ZEPHYR_EXPERIMENT_TRACKING=0）→ _NullBackend（no-op）
  - 所有 log 调用包 try/except，失败只记 stderr 不抛——业务回测不受 tracking 失败影响

依据: 11_regime_backtest_validation_plan §3 ② + backtest_observability_mlflow_plan.md M1
SSoT: depgraph MOD-OBS-001
Version: 0.1.0
"""
from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from zephyr.experiment_tracking.config import ExperimentTrackingConfig, load_config
from zephyr.experiment_tracking.fallback_tracker import FallbackBackend

_logger = logging.getLogger(__name__)

# lazy import mlflow
try:  # pragma: no cover — 依赖是否安装决定分支
    import mlflow  # type: ignore[import-untyped]
    _MLFLOW_AVAILABLE = True
except ImportError:
    mlflow = None  # type: ignore[assignment]
    _MLFLOW_AVAILABLE = False

_warned_fallback = False  # 降级 warning 只输出一次


def _warn_once(msg: str) -> None:
    """降级 warning 只输出一次（避免刷屏）。"""
    global _warned_fallback
    if not _warned_fallback:
        print(f"[zephyr.experiment_tracking] WARNING: {msg}", file=sys.stderr)
        _logger.warning(msg)
        _warned_fallback = True


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

    def log_metrics(self, metrics: dict[str, float], step: Optional[int] = None) -> None:
        try:
            self._backend.log_metrics(metrics, step)
        except Exception as e:  # noqa: BLE001
            print(f"[zephyr.experiment_tracking] log_metrics 失败(忽略): {e}", file=sys.stderr)

    def log_artifact(self, local_path: str | Path, artifact_path: Optional[str] = None) -> None:
        try:
            self._backend.log_artifact(str(local_path), artifact_path)
        except Exception as e:  # noqa: BLE001
            print(f"[zephyr.experiment_tracking] log_artifact 失败(忽略): {e}", file=sys.stderr)

    def log_artifact_bytes(self, data: bytes, filename: str, artifact_path: Optional[str] = None) -> None:
        try:
            self._backend.log_artifact_bytes(data, filename, artifact_path)
        except Exception as e:  # noqa: BLE001
            print(f"[zephyr.experiment_tracking] log_artifact_bytes 失败(忽略): {e}", file=sys.stderr)


# ──────────────────────────────────────────────────────────────────────────────
# Backend 抽象 —— MLflowBackend / FallbackBackend / NullBackend 共同接口
# ──────────────────────────────────────────────────────────────────────────────


class _MLflowBackend:
    """mlflow 可用时的 backend（操作 mlflow active run）。"""

    def __init__(self, tracking_uri: str, experiment_prefix: str) -> None:
        mlflow.set_tracking_uri(tracking_uri)  # type: ignore[union-attr]
        self._prefix = experiment_prefix

    def _ensure_experiment(self, exp_name: str) -> None:
        """确保 experiment 存在，显式指定 artifact_location。

        规避部分 mlflow 版本在 Windows 下默认生成 'file:D:/...' 畸形 URI（缺 '//')，
        导致 list_artifacts / mlflow ui 取不到产物。显式用 Path.as_uri() 生成
        合法 'file:///' 形式。
        """
        exp = mlflow.get_experiment_by_name(exp_name)  # type: ignore[union-attr]
        if exp is not None:
            return
        artifact_root = (Path("mlruns").resolve() / exp_name).as_uri()
        mlflow.create_experiment(exp_name, artifact_location=artifact_root)  # type: ignore[union-attr]

    def start_run(self, component: str, run_name: Optional[str], tags: Optional[dict]) -> str:
        exp_name = f"{self._prefix}{component}"
        self._ensure_experiment(exp_name)
        mlflow.set_experiment(exp_name)  # type: ignore[union-attr]
        run = mlflow.start_run(run_name=run_name or f"{component}_{datetime.now():%Y%m%d_%H%M%S}",  # type: ignore[union-attr]
                               tags=tags or {})
        return run.info.run_id

    def log_params(self, params: dict[str, Any]) -> None:
        for k, v in params.items():
            mlflow.log_param(k, v)  # type: ignore[union-attr]

    def log_metrics(self, metrics: dict[str, float], step: Optional[int]) -> None:
        for k, v in metrics.items():
            mlflow.log_metric(k, float(v), step=step)  # type: ignore[union-attr]

    def log_artifact(self, local_path: str, artifact_path: Optional[str]) -> None:
        mlflow.log_artifact(local_path, artifact_path=artifact_path)  # type: ignore[union-attr]

    def log_artifact_bytes(self, data: bytes, filename: str, artifact_path: Optional[str]) -> None:
        import tempfile, os
        tmp = Path(tempfile.mkdtemp()) / filename
        tmp.write_bytes(data)
        try:
            mlflow.log_artifact(str(tmp), artifact_path=artifact_path)  # type: ignore[union-attr]
        finally:
            try:
                os.remove(tmp)
                os.rmdir(tmp.parent)
            except OSError:
                pass

    def end_run(self, status: str) -> None:
        mlflow.end_run(status=status)  # type: ignore[union-attr]


class _NullBackend:
    """enable_tracking=False 时的 no-op backend（所有方法空实现）。"""

    def start_run(self, component: str, run_name: Optional[str], tags: Optional[dict]) -> str:
        return "null-run"

    def log_params(self, params: dict[str, Any]) -> None: pass
    def log_metrics(self, metrics: dict[str, float], step: Optional[int]) -> None: pass
    def log_artifact(self, local_path: str, artifact_path: Optional[str]) -> None: pass
    def log_artifact_bytes(self, data: bytes, filename: str, artifact_path: Optional[str]) -> None: pass
    def end_run(self, status: str) -> None: pass


# ──────────────────────────────────────────────────────────────────────────────
# ExperimentTracker 主类
# ──────────────────────────────────────────────────────────────────────────────


class ExperimentTracker:
    """MLflow 薄包装——统一实验跟踪入口。

    自动选择 backend:
      - enable_tracking=False → _NullBackend
      - mlflow 可用           → _MLflowBackend
      - mlflow 未装           → FallbackBackend（JSON 降级）
    """

    def __init__(self, config: Optional[ExperimentTrackingConfig] = None) -> None:
        self._config = config or load_config()
        self._backend = self._make_backend()

    def _make_backend(self) -> Any:
        if not self._config.enable_tracking:
            return _NullBackend()
        if _MLFLOW_AVAILABLE:
            try:
                return _MLflowBackend(self._config.tracking_uri, self._config.experiment_prefix)
            except Exception as e:  # noqa: BLE001 — mlflow 初始化失败降级
                _warn_once(f"mlflow 初始化失败({e})，降级到 JSON fallback")
                return FallbackBackend(self._config.fallback_dir)
        _warn_once(
            "mlflow 未安装，实验跟踪降级到本地 JSON（logs/experiment_tracking_fallback/）。"
            "安装以启用完整 UI: pip install -e '.[observability]'"
        )
        return FallbackBackend(self._config.fallback_dir)

    @property
    def available(self) -> bool:
        """mlflow 是否可用（False = 降级或关闭模式）。"""
        return _MLFLOW_AVAILABLE and self._config.enable_tracking

    @property
    def config(self) -> ExperimentTrackingConfig:
        return self._config

    def start_run(
        self,
        component: str,
        run_name: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> RunContext:
        """开启一个 run。component 映射到 experiment 名（zephyr-{component}）。"""
        run_id = self._backend.start_run(component, run_name, tags)
        return RunContext(self._backend, run_id, component, run_name or component)


# ──────────────────────────────────────────────────────────────────────────────
# 单例工厂
# ──────────────────────────────────────────────────────────────────────────────

_tracker_singleton: Optional[ExperimentTracker] = None


def get_tracker() -> ExperimentTracker:
    """获取全局 tracker 单例（首次调用按 config 初始化）。"""
    global _tracker_singleton
    if _tracker_singleton is None:
        _tracker_singleton = ExperimentTracker()
    return _tracker_singleton


def reset_tracker() -> None:
    """重置单例（测试用：改环境变量后重新初始化）。"""
    global _tracker_singleton, _warned_fallback
    _tracker_singleton = None
    _warned_fallback = False
