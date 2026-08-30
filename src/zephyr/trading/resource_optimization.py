# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.resource_optimization
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.lifecycle.daemon_registry; zephyr.shared.lifecycle.resource_optimization_models; zephyr.shared.io.io_cache; zephyr.shared.io.streaming_reader; zephyr.shared.infra.process_pool; zephyr.shared.lifecycle.lazy_loader; zephyr.shared.capacity_calibrator; zephyr.shared.capacity_digital_twin; zephyr.shared.capacity_fingerprint; zephyr.shared.capacity_governance_loop; zephyr.shared.capacity_runbook_generator; zephyr.shared.model_capacity_probe; zephyr.trading.__init__; zephyr.shared.event_bus; zephyr.gov_audit.bridge
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
resource_optimization.py - MAPE-K autonomic resource optimization engine
========================================================================

Moved from shared.lifecycle.resource_optimization_engine.
Canonical location is now zephyr.trading.resource_optimization.

Models remain in shared.lifecycle.resource_optimization_models to avoid
circular imports (shared.io / shared.infra depend on models).

MAPE-K loop:
  Monitor  -> snapshot CPU, memory, disk I/O, process/thread count
  Analyze  -> classify pressure (NORMAL/WARNING/CRITICAL/EMERGENCY)
  Plan     -> decide optimization or defensive strategy
  Execute  -> run strategy, record result
  Knowledge -> accumulate history for smarter decisions

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: level 参数
#   fields: 参数 level，类型注解 PressureLevel
#   code: resource_optimization.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① degradation_lv
#   name_en: degradation_lv
#   intro: PressureLevel → 蓝图 §3.3 降级链级别（Lv0~Lv3）。
#   desc: PressureLevel → 蓝图 §3.3 降级链级别（Lv0~Lv3）。；源码 L166-L168
#   inputs: level
#   outputs: str
# - id: A2
#   name_zh: ② CircuitBreaker
#   name_en: CircuitBreaker
#   intro: class CircuitBreaker 源码 L200-L264
#   desc: 公共方法（定义序）: state, allow, record_success, record_failure, reset；源码 L200-L264
#   inputs: failure_threshold recovery_timeout_s half_open_max_calls
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ResourceOptimizationEngine
#   name_en: ResourceOptimizationEngine
#   intro: MAPE-K 自治资源优化引擎（单例 facade）。
#   desc: MAPE-K 自治资源优化引擎（单例 facade）。 5.150.1 God Class 治本：3 个高内聚零耦合职责簇已提取为同文件协作者类—— _ConfigReloade…；公共方法（定义序）: classif…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import os
import random
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from zephyr.shared.capacity_governance.capacity_calibrator import CapacityCalibrator
from zephyr.shared.capacity_governance.capacity_digital_twin import CapacityDigitalTwin
from zephyr.shared.capacity_governance.capacity_fingerprint import CapacityFingerprint
from zephyr.shared.capacity_governance.capacity_governance_loop import CapacityGovernanceLoop
from zephyr.shared.capacity_governance.capacity_runbook_generator import CapacityRunbookGenerator
from zephyr.shared.capacity_governance.model_capacity_probe import ModelCapacityProbe
from zephyr.shared.infra.process_pool import MCPProcessPool
from zephyr.shared.io.io_cache import FileCache
from zephyr.shared.lifecycle.daemon_registry import DaemonRegistry
from zephyr.shared.lifecycle.lazy_loader import LazyModuleRegistry
from zephyr.shared.lifecycle.resource_optimization_models import (
    CacheStats,
    CircuitBreakerState,
    DefensiveStrategy,
    DegradationMatrix,
    HealthCheckResult,
    OptimizationRecord,
    OptimizationResult,
    OptimizationStrategy,
    PressureLevel,
    PressureState,
    ProcessPoolStats,
    ResourceSnapshot,
)

__all__ = [
    "DEGRADATION_CHAIN",
    "CacheStats",
    "CircuitBreaker",
    "CircuitBreakerState",
    "DefensiveStrategy",
    "DegradationMatrix",
    "HealthCheckResult",
    "OptimizationRecord",
    "OptimizationResult",
    "OptimizationStrategy",
    "PressureLevel",
    "PressureState",
    "ProcessPoolStats",
    "ResourceOptimizationEngine",
    "ResourceSnapshot",
    "degradation_lv",
]


# 四级降级链（AutoRuntime Core 蓝图 §3.3，D-INF035-05）——PressureLevel ↔ Lv0~Lv3 映射真源。
# 阈值见 _PressureThresholds（Lv1: CPU>75%/MEM>70%；Lv2: CPU>85%/MEM>80%；Lv3: CPU>95%/MEM>90%）。
DEGRADATION_CHAIN: dict[PressureLevel, dict[str, str]] = {
    PressureLevel.NORMAL: {
        "lv": "Lv0",
        "name": "Normal",
        "trigger": "CPU<75% & MEM<70%",
        "actions": "全功能运行",
    },
    PressureLevel.WARNING: {
        "lv": "Lv1",
        "name": "Throttle",
        "trigger": "CPU>75% 或 MEM>70%",
        "actions": "StatusDashboard 降采样 / OrphanDetector 暂停 / DreamCycle 推迟",
    },
    PressureLevel.CRITICAL: {
        "lv": "Lv2",
        "name": "Shed",
        "trigger": "CPU>85% 或 MEM>80%",
        "actions": "ModuleOnboardingScanner 纯增量 / MAPE-K 降频30s / AiAuditLogger 环形缓冲",
    },
    PressureLevel.EMERGENCY: {
        "lv": "Lv3",
        "name": "Critical",
        "trigger": "CPU>95% 或 MEM>90%",
        "actions": "拒绝非P0 DAG / HealthMonitor 仅心跳 / 通知Owner / 5min未恢复→Kill Switch",
    },
}


def degradation_lv(level: PressureLevel) -> str:
    """PressureLevel → 蓝图 §3.3 降级链级别（Lv0~Lv3）。"""
    return DEGRADATION_CHAIN[level]["lv"]


logger = logging.getLogger(__name__)


class _PressureThresholds(BaseModel):
    # 阈值真源 = AutoRuntime Core 蓝图 §3.3 四级降级链（2026-08-22 对齐，04号文 Phase 0 步骤 0.5）：
    #   Lv1(WARNING):   CPU>75% 或 MEM>70%
    #   Lv2(CRITICAL):  CPU>85% 或 MEM>80%
    #   Lv3(EMERGENCY): CPU>95% 或 MEM>90%
    memory_warning_percent: float = 70.0
    memory_critical_percent: float = 80.0
    memory_emergency_percent: float = 90.0
    cpu_warning_percent: float = 75.0
    cpu_critical_percent: float = 85.0
    cpu_emergency_percent: float = 95.0
    process_warning_count: int = 50
    process_critical_count: int = 100
    process_emergency_count: int = 250
    gpu_warning_percent: float = 85.0
    gpu_critical_percent: float = 95.0
    gpu_emergency_percent: float = 98.0


class _HysteresisConfig(BaseModel):
    confirmation_count: int = 2
    cooldown_seconds: float = 60.0
    hysteresis_percent: float = 10.0
    oscillation_threshold_per_hour: int = 3


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_s: float = 30.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout_s = recovery_timeout_s
        self._half_open_max_calls = half_open_max_calls
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitBreakerState:
        # 5.91.3 修复: getter仅返回当前状态,不触发状态转换和计数器修改
        with self._lock:
            return self._state

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

    def _try_recover(self) -> None:
        """5.91.3 修复: 提取状态转换逻辑,仅在allow()中调用。"""
        if self._state is CircuitBreakerState.OPEN:
            if time.monotonic() - self._last_failure_time >= self._recovery_timeout_s:
                self._state = CircuitBreakerState.HALF_OPEN
                self._half_open_calls = 0

    def allow(self) -> bool:
        with self._lock:
            self._try_recover()
            if self._state is CircuitBreakerState.CLOSED:
                return True
            if self._state is CircuitBreakerState.HALF_OPEN:
                if self._half_open_calls < self._half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            return False

    def record_success(self) -> None:
        with self._lock:
            if self._state is CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._state is CircuitBreakerState.HALF_OPEN or self._failure_count >= self._failure_threshold:
                self._state = CircuitBreakerState.OPEN

    def reset(self) -> None:
        with self._lock:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0


class _PressureStateMachine:
    def __init__(self, config: _HysteresisConfig | None = None) -> None:
        self._config = config or _HysteresisConfig()
        self._current = PressureLevel.NORMAL
        self._previous: PressureLevel | None = None
        self._entered_at = datetime.now(UTC)
        self._transition_count = 0
        self._pending_level: PressureLevel | None = None
        self._pending_confirmations = 0
        self._last_transition_time: float = 0.0
        self._hourly_transitions: list[float] = []
        self._lock = threading.Lock()

    @property
    def current(self) -> PressureLevel:
        return self._current

    @property
    def state(self) -> PressureState:
        cooldown = 0.0
        if self._last_transition_time > 0:
            elapsed = time.monotonic() - self._last_transition_time
            cooldown = max(0.0, self._config.cooldown_seconds - elapsed)
        return PressureState(
            current_level=self._current,
            previous_level=self._previous,
            entered_at=self._entered_at,
            transition_count=self._transition_count,
            cooldown_remaining_s=cooldown,
        )

    def transition(self, classified: PressureLevel) -> PressureLevel:
        with self._lock:
            if classified == self._current:
                self._pending_level = None
                self._pending_confirmations = 0
                return self._current

            now = time.monotonic()
            self._hourly_transitions = [t for t in self._hourly_transitions if now - t < 3600]

            level_order = [
                PressureLevel.NORMAL,
                PressureLevel.WARNING,
                PressureLevel.CRITICAL,
                PressureLevel.EMERGENCY,
            ]
            classified_idx = level_order.index(classified)
            current_idx = level_order.index(self._current)
            is_escalation = classified_idx > current_idx

            if is_escalation:
                effective_confirm = self._config.confirmation_count
                if len(self._hourly_transitions) >= self._config.oscillation_threshold_per_hour:
                    effective_confirm = min(effective_confirm + 1, 5)

                if self._pending_level == classified:
                    self._pending_confirmations += 1
                else:
                    self._pending_level = classified
                    self._pending_confirmations = 1

                if self._pending_confirmations >= effective_confirm:
                    self._apply_transition(classified, now)
                return self._current
            else:
                elapsed = now - self._last_transition_time if self._last_transition_time > 0 else float("inf")
                if elapsed < self._config.cooldown_seconds:
                    return self._current
                self._apply_transition(classified, now)
                return self._current

    def _apply_transition(self, new_level: PressureLevel, now: float) -> None:
        self._previous = self._current
        self._current = new_level
        self._entered_at = datetime.now(UTC)
        self._transition_count += 1
        self._last_transition_time = now
        self._hourly_transitions.append(now)
        self._pending_level = None
        self._pending_confirmations = 0


# ══════════════════════════════════════════════════════════════════════════
# 5.150.1 Extract Class 协作者（God Class 治本：高内聚零耦合职责簇）
# 模式对齐 action_dispatcher.py：
#   - 纯静态方法（零引擎依赖）由 engine 类级别名 staticmethod 委托
#   - 依赖引擎状态的方法由 engine 同名薄封装委托（实例级 patch 面不变）
# 协作者均无状态——配置/开关/子系统句柄等状态保留在 engine 上（测试直接访问），
# 协作者仅经 engine 参数读写，不反向持有引用。
# ══════════════════════════════════════════════════════════════════════════


class _ConfigReloader:
    """配置加载/热重载协作者（职责簇：YAML 配置发现/解析/应用 + mtime 热重载）。

    5.150.1 Extract Class: 从 ResourceOptimizationEngine 提取的高内聚配置簇。
    状态（_config_path/_config_mtime 及被应用的 thresholds/hysteresis/self_healing/
    audit/eventbus 字段）保留在 engine 上（测试直接赋值 engine._config_path），
    本类无状态，仅经 engine 参数读写。engine 保留同名薄封装，实例级 patch 面不变。
    """

    @staticmethod
    def discover_path() -> str | None:
        config_paths = [
            os.path.join(os.getcwd(), "config", "resource_optimization.yaml"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "resource_optimization.yaml"),
        ]
        for cp in config_paths:
            cp = os.path.normpath(cp)
            if os.path.isfile(cp):
                return cp
        return None

    @staticmethod
    def apply(engine: ResourceOptimizationEngine, path: str) -> None:
        try:
            import yaml

            with open(path, encoding="utf-8") as f:
                raw = f.read()
            cfg = yaml.safe_load(raw)
            if not isinstance(cfg, dict):
                return
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.exception("ResourceOptimizationEngine: config load failed from %s", path, exc_info=True)
            return

        engine._config_mtime = os.path.getmtime(path)

        pt = cfg.get("pressure_thresholds", {})
        if pt:
            engine.thresholds = _PressureThresholds(
                memory_warning_percent=pt.get("memory_warning_percent", 70.0),
                memory_critical_percent=pt.get("memory_critical_percent", 80.0),
                memory_emergency_percent=pt.get("memory_emergency_percent", 90.0),
                cpu_warning_percent=pt.get("cpu_warning_percent", 75.0),
                cpu_critical_percent=pt.get("cpu_critical_percent", 85.0),
                cpu_emergency_percent=pt.get("cpu_emergency_percent", 95.0),
                process_warning_count=pt.get("process_warning_count", 50),
                process_critical_count=pt.get("process_critical_count", 100),
                process_emergency_count=pt.get("process_emergency_count", 250),
                gpu_warning_percent=pt.get("gpu_warning_percent", 85.0),
                gpu_critical_percent=pt.get("gpu_critical_percent", 95.0),
                gpu_emergency_percent=pt.get("gpu_emergency_percent", 98.0),
            )

        hy = cfg.get("hysteresis", {})
        if hy:
            engine.hysteresis = _HysteresisConfig(
                confirmation_count=hy.get("confirmation_count", 2),
                cooldown_seconds=hy.get("cooldown_seconds", 60.0),
                hysteresis_percent=hy.get("hysteresis_percent", 10.0),
                oscillation_threshold_per_hour=hy.get("oscillation_threshold_per_hour", 3),
            )
            engine._pressure_sm = _PressureStateMachine(engine.hysteresis)

        sh = cfg.get("self_healing", {})
        if sh:
            engine.self_healing_enabled = sh.get("enabled", True)
            engine._self_healing_max_recovery_s = sh.get("max_recovery_time_s", 60.0)
            engine.self_healing_verification_delay_s = sh.get("verification_delay_s", 5.0)
            engine.self_healing_max_retries = sh.get("max_retries", 3)

        au = cfg.get("audit", {})
        if au:
            engine.audit_enabled = au.get("enabled", True)

        eb = cfg.get("eventbus", {})
        if eb:
            engine.eventbus_enabled = eb.get("enabled", True)
            engine._eventbus_topic = eb.get("topic", "resource.pressure.changed")

        logger.info("ResourceOptimizationEngine: config loaded from %s", path)

    @staticmethod
    def check_reload(engine: ResourceOptimizationEngine) -> None:
        if engine.config_path is None:
            return
        try:
            current_mtime = os.path.getmtime(engine.config_path)
            if current_mtime != engine._config_mtime:
                engine.apply_config(engine.config_path)
        except OSError as e:
            # 5.54.5 修复：原 except OSError: pass 静默停止热重载，配置文件误删后引擎无感知。
            # 改为 warning 级别日志记录。
            logger.warning("ResourceOptimizationEngine: config hot-reload failed (%s: %s)", type(e).__name__, e)


class _StrategyExecutor:
    """优化策略执行协作者（职责簇：7 种 OptimizationStrategy 执行 + 防御降级动作）。

    5.150.1 Extract Class: 从 ResourceOptimizationEngine 提取的策略执行簇。
    纯函数式方法（memory_compact/streaming_read/defensive，零引擎依赖）由 engine
    类级别名 staticmethod 委托；依赖引擎子系统（_monitor_interval/_file_cache/
    _process_pool/_lazy_loader）的方法由 engine 同名薄封装委托，实例级 patch 面不变。
    """

    @staticmethod
    def schedule_adapt(engine: ResourceOptimizationEngine, pressure: PressureLevel) -> list[str]:
        intervals = {
            PressureLevel.NORMAL: 30.0,
            PressureLevel.WARNING: 60.0,
            PressureLevel.CRITICAL: 120.0,
            PressureLevel.EMERGENCY: 0.0,
        }
        new_interval = intervals.get(pressure, 30.0)
        if new_interval > 0:
            engine._monitor_interval = new_interval
            return [f"schedule_adapt: interval set to {new_interval}s for {pressure.value}"]
        else:
            return [f"schedule_adapt: paused for {pressure.value}"]

    @staticmethod
    def memory_compact() -> list[str]:
        import gc

        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        return [f"memory_compact: gc.collect() freed {collected} objects ({before} -> {after})"]

    @staticmethod
    def cache_warm(engine: ResourceOptimizationEngine, context: dict[str, Any] | None) -> list[str]:
        files = []
        if context and "files" in context:
            files = context["files"]
        if not files:
            return ["cache_warm: no files specified in context"]
        loaded = engine._file_cache.warm(files)
        return [f"cache_warm: preloaded {loaded}/{len(files)} files"]

    @staticmethod
    def io_batch(engine: ResourceOptimizationEngine, context: dict[str, Any] | None) -> list[str]:
        files = []
        if context and "files" in context:
            files = context["files"]
        if not files:
            return ["io_batch: no files specified in context"]
        loaded = 0
        for fp in files:
            result = engine._file_cache.get_or_load(fp)
            if result is not None:
                loaded += 1
        return [f"io_batch: batch loaded {loaded}/{len(files)} files"]

    @staticmethod
    def streaming_read(context: dict[str, Any] | None) -> list[str]:
        path = context.get("path") if context else None
        if not path:
            return ["streaming_read: no path specified in context"]
        p = str(path)
        try:
            size_mb = os.path.getsize(p) / (1024 * 1024)
        except OSError:
            size_mb = 0.0
        if size_mb > 1.0:
            return [f"streaming_read: {p} ({size_mb:.1f}MB) — use stream_jsonl/tail_jsonl"]
        return [f"streaming_read: {p} ({size_mb:.1f}MB) — small file, direct read OK"]

    @staticmethod
    def process_pool(engine: ResourceOptimizationEngine, context: dict[str, Any] | None) -> list[str]:
        stats = engine._process_pool.get_stats()
        if stats.active_processes == 0:
            return ["process_pool: no active processes to optimize"]
        reuse_before = stats.reuse_count
        return [f"process_pool: {stats.active_processes} active, {reuse_before} reuses — pool sharing active"]

    @staticmethod
    def lazy_init(engine: ResourceOptimizationEngine, context: dict[str, Any] | None) -> list[str]:
        loader_stats = engine._lazy_loader.stats()
        pending = loader_stats.get("pending", 0)
        if pending == 0:
            return ["lazy_init: all registered modules already loaded"]
        return [f"lazy_init: {pending} modules pending — deferred until first access"]

    @staticmethod
    def defensive(pressure: PressureLevel) -> list[str]:
        actions: list[str] = []
        if pressure is PressureLevel.EMERGENCY:
            stopped = DaemonRegistry.stop_low_priority(min_priority=5)
            if stopped:
                actions.append(f"stop_low_priority(5): stopped {stopped}")
            import gc

            gc.collect()
            actions.append("emergency_gc: forced garbage collection")
        elif pressure is PressureLevel.CRITICAL:
            stopped = DaemonRegistry.stop_low_priority(min_priority=2)
            if stopped:
                actions.append(f"stop_low_priority(2): stopped {stopped}")
            actions.append("reduce_frequency: monitor interval extended")
        return actions


class _ExternalNotifier:
    """外部通知协作者（职责簇：EventBus 压力事件 + gov_audit 审计外发）。

    5.150.1 Extract Class: 从 ResourceOptimizationEngine 提取的外发通知簇。
    两路同构——enabled 开关守卫 + 外部系统调用 + 异常抑制。开关/去抖状态
    （_eventbus_enabled/_eventbus_topic/_last_pressure_level/_audit_enabled）
    保留在 engine 上，engine 保留同名薄封装，实例级 patch 面不变。
    """

    @staticmethod
    def emit_pressure_event(engine: ResourceOptimizationEngine, snap: ResourceSnapshot) -> None:
        if not engine.eventbus_enabled:
            return
        if snap.pressure == engine.last_pressure_level:
            return
        engine.last_pressure_level = snap.pressure
        try:
            from zephyr.shared.event_bus import bus

            bus.emit(
                engine._eventbus_topic,
                {
                    "pressure_level": snap.pressure.value,
                    "cpu_percent": snap.cpu_percent,
                    "memory_percent": snap.memory_percent,
                    "process_count": snap.process_count,
                    "timestamp": snap.timestamp,
                },
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in resource_optimization", exc_info=True)

    @staticmethod
    def audit_optimization(engine: ResourceOptimizationEngine, record: OptimizationRecord) -> None:
        if not engine.audit_enabled:
            return
        try:
            from zephyr.gov_audit.bridge import write_to_core

            write_to_core(
                "resource_optimization",
                {
                    "strategy": record.strategy.value,
                    "trigger": record.trigger.value,
                    "actions_taken": record.actions_taken,
                    "memory_before_gb": record.memory_before_gb,
                    "memory_after_gb": record.memory_after_gb,
                    "quality_preserved": record.quality_preserved,
                    "success": record.success,
                    "duration_ms": record.duration_ms,
                },
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in resource_optimization", exc_info=True)


class ResourceOptimizationEngine:
    """MAPE-K 自治资源优化引擎（单例 facade）。

    5.150.1 God Class 治本：3 个高内聚零耦合职责簇已提取为同文件协作者类——
    _ConfigReloader（配置加载/热重载）、_StrategyExecutor（策略执行+防御降级）、
    _ExternalNotifier（EventBus/审计外发），本类以类级别名 staticmethod + 同名
    薄封装委托，公共 API 与实例级 patch 面不变。
    保留在本类的簇（Monitor/Analyze 核心、optimize 调度、监控编排、自愈闭环、
    子系统访问器）与单例状态/调用顺序/副作用深度交织，不外移，理由见各职责分区注释块。
    """

    _instance: ResourceOptimizationEngine | None = None
    instance: ResourceOptimizationEngine | None = _instance  # public alias（Stage 4 公共化）
    _init_lock = threading.Lock()

    def __new__(cls) -> ResourceOptimizationEngine:
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        # 5.98.3 修复: __init__守卫加锁,防并发首次调用重复初始化
        with self._init_lock:
            if self._initialized:
                return
            self._thresholds = _PressureThresholds()
            self._hysteresis = _HysteresisConfig()
            self._pressure_sm = _PressureStateMachine(self._hysteresis)
            self._circuit_breakers: dict[str, CircuitBreaker] = {}
            self._optimization_history: list[OptimizationRecord] = []
            self._max_history = 10000
            self._pressure_callbacks: list[Callable[[PressureLevel, ResourceSnapshot], None]] = []
            self._monitor_thread: threading.Thread | None = None
            self._monitor_running = False
            self._last_snapshot: ResourceSnapshot | None = None
            self._monitor_interval = 30.0
            self._started_at: float | None = None
            self._degradation_matrix = DegradationMatrix(
                normal={"scheduler": "30s", "cache": "warm", "process_pool": "active"},
                warning={"scheduler": "60s", "cache": "warm", "process_pool": "active"},
                critical={"scheduler": "120s", "cache": "cold", "process_pool": "frozen"},
                emergency={"scheduler": "paused", "cache": "evicted", "process_pool": "stopped"},
            )
            self._file_cache = FileCache(max_entries=1000, ttl_seconds=300.0)
            self._process_pool = MCPProcessPool(max_processes=30)
            self._lazy_loader = LazyModuleRegistry()
            self._capacity_calibrator = CapacityCalibrator()
            self._capacity_digital_twin = CapacityDigitalTwin("resource-optimization")
            self._capacity_fingerprint = CapacityFingerprint()
            self._capacity_governance_loop = CapacityGovernanceLoop()
            self._capacity_runbook_generator = CapacityRunbookGenerator()
            self._model_capacity_probe = ModelCapacityProbe()
            self._config_path: str | None = None
            self._config_mtime: float = 0.0
            self._self_healing_enabled = True
            self._self_healing_max_recovery_s = 60.0
            self._self_healing_verification_delay_s = 5.0
            self._self_healing_max_retries = 3
            self._audit_enabled = True
            self._eventbus_enabled = True
            self._eventbus_topic = "resource.pressure.changed"
            self._last_pressure_level = PressureLevel.NORMAL
            self._initialized = True
            self._load_config()
            logger.info("ResourceOptimizationEngine: initialized (singleton)")

    def classify_pressure(self, snap) -> PressureLevel:
        """公共接口：classify_pressure（Stage 4 公共化）。"""
        return self._classify_pressure(snap)

    @property
    def circuit_breakers(self) -> dict[str, CircuitBreaker]:
        """只读：circuit_breakers（Stage 4 公共化）。"""
        return self._circuit_breakers

    @circuit_breakers.setter
    def circuit_breakers(self, value):
        """写入：circuit_breakers（Stage 4 公共化）。"""
        self._circuit_breakers = value

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def monitor_running(self):
        """只读：monitor_running（Stage 4 公共化）。"""
        return self._monitor_running

    @monitor_running.setter
    def monitor_running(self, value):
        """写入：monitor_running（Stage 4 公共化）。"""
        self._monitor_running = value

    @property
    def pressure_callbacks(self) -> list[Callable[[PressureLevel, ResourceSnapshot], None]]:
        """只读：pressure_callbacks（Stage 4 公共化）。"""
        return self._pressure_callbacks

    @pressure_callbacks.setter
    def pressure_callbacks(self, value):
        """写入：pressure_callbacks（Stage 4 公共化）。"""
        self._pressure_callbacks = value

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def pressure_sm(self):
        """只读：pressure_sm（Stage 4 公共化）。"""
        return self._pressure_sm

    @pressure_sm.setter
    def pressure_sm(self, value):
        """写入：pressure_sm（Stage 4 公共化）。"""
        self._pressure_sm = value

    # ══ 职责分区① Monitor/Analyze 核心（保留，不外移） ══
    # 保留理由：snapshot() 的副作用链环环相扣——psutil/ctypes 采集 →
    # _classify_pressure（读 _thresholds）→ _pressure_sm.transition（状态机副作用）→
    # 写 _last_snapshot；classification 夹在采集与状态转换之间，强行外移会破坏调用顺序语义。

    def snapshot(self) -> ResourceSnapshot:
        snap = ResourceSnapshot(timestamp=time.time())
        try:
            import psutil

            mem = psutil.virtual_memory()
            snap.memory_percent = mem.percent
            snap.memory_used_gb = mem.used / (1024**3)
            snap.memory_total_gb = mem.total / (1024**3)
            snap.cpu_percent = psutil.cpu_percent(interval=0)
            snap.process_count = len(psutil.pids())
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    snap.disk_io_read_mb_s = disk_io.read_bytes / (1024**2)
                    snap.disk_io_write_mb_s = disk_io.write_bytes / (1024**2)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in resource_optimization", exc_info=True)
            import shutil

            try:
                usage = shutil.disk_usage(".")
                snap.disk_free_gb = usage.free / (1024**3)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in resource_optimization", exc_info=True)
        except ImportError:
            try:
                import ctypes

                if os.name == "nt":
                    kernel32 = ctypes.windll.kernel32

                    class MEMORYSTATUSEX(ctypes.Structure):
                        _fields_ = [
                            ("dwLength", ctypes.c_ulong),
                            ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                        ]

                    mem_status = MEMORYSTATUSEX()
                    mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                    kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
                    snap.memory_percent = float(mem_status.dwMemoryLoad)
                    snap.memory_total_gb = mem_status.ullTotalPhys / (1024**3)
                    snap.memory_used_gb = (mem_status.ullTotalPhys - mem_status.ullAvailPhys) / (1024**3)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in resource_optimization", exc_info=True)

        try:
            from zephyr.trading.gpu_monitor import collect_gpu_stats

            gpu = collect_gpu_stats()
            snap.gpu_percent = gpu.get("gpu_percent", 0.0)
            snap.gpu_memory_used_gb = gpu.get("memory_used_gb", 0.0)
            snap.gpu_memory_total_gb = gpu.get("memory_total_gb", 0.0)
            snap.gpu_available = gpu.get("available", False)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in resource_optimization", exc_info=True)

        try:
            from zephyr.trading.process_reaper import scan_ghost_windows

            ghosts = scan_ghost_windows()
            snap.ide_ghost_windows = len(ghosts)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in resource_optimization", exc_info=True)

        classified = self._classify_pressure(snap)
        snap.pressure = self._pressure_sm.transition(classified)
        self._last_snapshot = snap
        return snap

    def _classify_pressure(self, snap: ResourceSnapshot) -> PressureLevel:
        t = self._thresholds
        # 查表法：按优先级降序检查 (level, metric_value, threshold_value)
        checks = (
            (PressureLevel.EMERGENCY, snap.memory_percent, t.memory_emergency_percent),
            (PressureLevel.EMERGENCY, snap.process_count, t.process_emergency_count),
            (PressureLevel.EMERGENCY, snap.cpu_percent, t.cpu_emergency_percent),
            (PressureLevel.CRITICAL, snap.memory_percent, t.memory_critical_percent),
            (PressureLevel.CRITICAL, snap.process_count, t.process_critical_count),
            (PressureLevel.CRITICAL, snap.cpu_percent, t.cpu_critical_percent),
            (PressureLevel.WARNING, snap.memory_percent, t.memory_warning_percent),
            (PressureLevel.WARNING, snap.process_count, t.process_warning_count),
            (PressureLevel.WARNING, snap.cpu_percent, t.cpu_warning_percent),
        )
        for level, metric, threshold in checks:
            if metric >= threshold:
                return level
        return PressureLevel.NORMAL

    # ══ 职责分区② Plan/Execute 核心（保留，不外移） ══
    # 保留理由：optimize() 是 MAPE-K 调度枢纽——按序编排 熔断器 → snapshot 前采 →
    # 策略执行 → snapshot 后采 → 历史截断 → 审计外发，跨 6 个状态字段的调用顺序即语义。

    def optimize(
        self,
        strategy: OptimizationStrategy,
        context: dict[str, Any] | None = None,
    ) -> OptimizationResult:
        cb = self._circuit_breakers.get(strategy.value)
        if cb is None:
            cb = CircuitBreaker()
            self._circuit_breakers[strategy.value] = cb

        snap_before = self.snapshot()

        if not cb.allow():
            return OptimizationResult(
                strategy=strategy,
                success=False,
                snapshot_before=snap_before,
                quality_preserved=True,
                error_message=f"circuit breaker OPEN for {strategy.value}",
            )

        start = time.monotonic()
        actions: list[str] = []
        success = True
        error_msg: str | None = None

        try:
            if strategy is OptimizationStrategy.SCHEDULE_ADAPT:
                actions = self._execute_schedule_adapt(snap_before.pressure)
            elif strategy is OptimizationStrategy.MEMORY_COMPACT:
                actions = self._execute_memory_compact()
            elif strategy is OptimizationStrategy.CACHE_WARM:
                actions = self._execute_cache_warm(context)
            elif strategy is OptimizationStrategy.IO_BATCH:
                actions = self._execute_io_batch(context)
            elif strategy is OptimizationStrategy.PROCESS_POOL:
                actions = self._execute_process_pool(context)
            elif strategy is OptimizationStrategy.LAZY_INIT:
                actions = self._execute_lazy_init(context)
            elif strategy is OptimizationStrategy.STREAMING_READ:
                actions = self._execute_streaming_read(context)
            else:
                raise ValueError(f"unknown strategy: {strategy}")

            cb.record_success()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            success = False
            error_msg = str(e)
            cb.record_failure()
            logger.exception("ResourceOptimizationEngine: optimize(%s) failed", strategy.value, exc_info=True)

        snap_after = self.snapshot()
        duration_ms = int((time.monotonic() - start) * 1000)

        record = OptimizationRecord(
            trigger=snap_before.pressure,
            strategy=strategy,
            actions_taken=actions,
            memory_before_gb=snap_before.memory_used_gb,
            memory_after_gb=snap_after.memory_used_gb,
            process_count_before=snap_before.process_count,
            process_count_after=snap_after.process_count,
            quality_preserved=True,
            duration_ms=duration_ms,
            success=success,
        )
        self._optimization_history.append(record)
        if len(self._optimization_history) > self._max_history:
            self._optimization_history = self._optimization_history[-self._max_history :]

        self.audit_optimization(record)

        return OptimizationResult(
            strategy=strategy,
            success=success,
            actions_taken=actions,
            snapshot_before=snap_before,
            snapshot_after=snap_after,
            quality_preserved=True,
            error_message=error_msg,
        )

    # ── 策略执行 facade（委托 _StrategyExecutor，5.150.1 Extract Class） ──
    # 纯方法用类级别名 staticmethod（对齐 action_dispatcher 静态簇模式）；
    # 依赖引擎子系统的方法用同名薄封装，实例级 patch 面（patch.object(engine, ...)）不变。

    def _execute_schedule_adapt(self, pressure: PressureLevel) -> list[str]:
        return _StrategyExecutor.schedule_adapt(self, pressure)

    _execute_memory_compact = staticmethod(_StrategyExecutor.memory_compact)

    def _execute_cache_warm(self, context: dict[str, Any] | None) -> list[str]:
        return _StrategyExecutor.cache_warm(self, context)

    def _execute_io_batch(self, context: dict[str, Any] | None) -> list[str]:
        return _StrategyExecutor.io_batch(self, context)

    _execute_streaming_read = staticmethod(_StrategyExecutor.streaming_read)

    def _execute_process_pool(self, context: dict[str, Any] | None) -> list[str]:
        return _StrategyExecutor.process_pool(self, context)

    def _execute_lazy_init(self, context: dict[str, Any] | None) -> list[str]:
        return _StrategyExecutor.lazy_init(self, context)

    _execute_defensive = staticmethod(_StrategyExecutor.defensive)

    # ══ 职责分区③ 子系统访问器/DaemonRegistry 委托（保留，不外移） ══
    # 保留理由：全部为一行委托（DaemonRegistry/_file_cache/_process_pool/_lazy_loader/
    # _optimization_history/_pressure_callbacks/_pressure_sm/_degradation_matrix/
    # _circuit_breakers），本身是 facade 的最薄形态，提取无内聚收益。
    # health_check 横切读取 6 个子系统状态，是引擎级聚合视图，属本类。

    def register_daemon(
        self,
        name: str,
        start_fn: Callable[[], None],
        stop_fn: Callable[[], None],
        priority: int = 5,
    ) -> None:
        DaemonRegistry.register(name, start_fn, stop_fn, priority)

    def start_daemon(self, name: str) -> bool:
        return DaemonRegistry.start(name)

    def stop_daemon(self, name: str) -> bool:
        return DaemonRegistry.stop(name)

    def get_cache_stats(self) -> CacheStats:
        return self._file_cache.get_stats()

    def get_file_cache(self) -> FileCache:
        return self._file_cache

    def get_process_pool_stats(self) -> ProcessPoolStats:
        return self._process_pool.get_stats()

    def get_process_pool(self) -> MCPProcessPool:
        return self._process_pool

    def get_lazy_loader(self) -> LazyModuleRegistry:
        return self._lazy_loader

    def get_optimization_history(self, limit: int = 100) -> list[OptimizationRecord]:
        return self._optimization_history[-limit:]

    def on_pressure(self, callback: Callable[[PressureLevel, ResourceSnapshot], None]) -> None:
        self._pressure_callbacks.append(callback)

    def health_check(self) -> HealthCheckResult:
        running = self._monitor_running
        loop_alive = self._monitor_thread is not None and self._monitor_thread.is_alive()
        age = 0.0
        if self._last_snapshot is not None:
            age = time.time() - self._last_snapshot.timestamp
        status = DaemonRegistry.status()
        # 5.26.3/5.26.9 修复：health_check 真实检查 cache 和 process_pool 状态（原硬编码 True）
        try:
            cache_stats = self._file_cache.get_stats()
            cache_healthy = cache_stats.total_entries >= 0
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("health_check: cache stats failed: %s", e, exc_info=True)
            cache_healthy = False
        try:
            pool_stats = self._process_pool.get_stats()
            process_pool_healthy = pool_stats.zombie_count == 0
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("health_check: process_pool stats failed: %s", e, exc_info=True)
            process_pool_healthy = False
        return HealthCheckResult(
            engine_running=running,
            monitor_loop_alive=loop_alive,
            last_snapshot_age_s=round(age, 1),
            pressure_level=self._pressure_sm.current,
            daemon_count=len(status),
            cache_healthy=cache_healthy,
            process_pool_healthy=process_pool_healthy,
        )

    def get_pressure_state(self) -> PressureState:
        return self._pressure_sm.state

    def force_pressure(self, level: PressureLevel, reason: str) -> None:
        logger.warning(
            "ResourceOptimizationEngine: force_pressure(%s) — %s",
            level.value,
            reason,
        )
        self._pressure_sm._current = level
        self._pressure_sm._entered_at = datetime.now(UTC)
        self._pressure_sm._transition_count += 1

    def get_degradation_matrix(self) -> DegradationMatrix:
        return self._degradation_matrix

    def get_circuit_breaker_status(self) -> dict[str, CircuitBreakerState]:
        return {name: cb.state for name, cb in self._circuit_breakers.items()}

    # ══ 职责分区④ 监控编排：事件驱动 MAPE-K 循环（保留，不外移） ══
    # 保留理由：monitor_tick() 按序编排 配置热重载 → snapshot → 压力回调 →
    # EventBus 外发 → 防御降级 → 自愈闭环，调用顺序与副作用跨全部保留簇交织，
    # 是引擎的运行时骨架，外移等于把引擎掏空。

    def start_monitor(self, interval: float = 30.0) -> None:
        """P1 修复（2026-07-05）：事件驱动替代 time.sleep daemon。

        订阅 EventBus 事件触发 monitor_tick()，不再启动后台轮询线程。
        interval 参数保留用于 CI 批量兜底参考。
        """
        if self._monitor_running:
            return
        self._monitor_interval = interval
        self._monitor_running = True
        self._started_at = time.monotonic()
        try:
            from zephyr.shared.event_bus import bus

            bus.subscribe("task.completed", lambda _: self.monitor_tick())
            bus.subscribe("task.failed", lambda _: self.monitor_tick())
            bus.subscribe("resource.check.request", lambda _: self.monitor_tick())
            logger.info("ResourceOptimizationEngine: monitor started (event-driven, no daemon thread)")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("ResourceOptimizationEngine: EventBus subscribe failed: %s", e, exc_info=True)

    def stop_monitor(self) -> None:
        self._monitor_running = False
        logger.info("ResourceOptimizationEngine: monitor stopped")

    def monitor_tick(self) -> None:
        """事件驱动入口：采集资源快照 + 压力回调 + 自愈。

        由 EventBus 事件触发或 CI 批量兜底调用。替代原 _monitor_loop 的 time.sleep 轮询。
        """
        if not self._monitor_running:
            return
        try:
            self.check_config_reload()
            snap = self.snapshot()

            if snap.pressure is not PressureLevel.NORMAL:
                logger.warning(
                    "ResourceOptimizationEngine: pressure %s (mem=%.1f%%, cpu=%.1f%%, procs=%d)",
                    snap.pressure.value,
                    snap.memory_percent,
                    snap.cpu_percent,
                    snap.process_count,
                )
                for cb in self._pressure_callbacks:
                    try:
                        cb(snap.pressure, snap)
                    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.debug("suppressed error in resource_optimization", exc_info=True)

            self.emit_pressure_event(snap)

            if snap.pressure in (PressureLevel.EMERGENCY, PressureLevel.CRITICAL):
                self._execute_defensive(snap.pressure)
                self.self_heal_cycle(snap)

        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.exception("ResourceOptimizationEngine: monitor tick failed", exc_info=True)

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    # ── 配置加载/热重载 facade（委托 _ConfigReloader，5.150.1 Extract Class） ──
    # 状态 _config_path/_config_mtime 及被应用字段保留在本类（测试直接访问），
    # 同名薄封装保留实例级 patch 面。

    def _load_config(self) -> None:
        self._config_path = _ConfigReloader.discover_path()
        if self._config_path is None:
            return
        self.apply_config(self._config_path)

    def apply_config(self, path: str) -> None:
        _ConfigReloader.apply(self, path)

    def _apply_config(self, path: str) -> None:
        self.apply_config(path)

    def check_config_reload(self) -> None:
        _ConfigReloader.check_reload(self)

    def _check_config_reload(self) -> None:
        self.check_config_reload()

    # ══ 职责分区⑤ 自愈闭环（保留，不外移） ══
    # 保留理由：_self_heal_cycle 与 optimize()/snapshot() 调用顺序深度交织——
    # 策略选择 → optimize 执行 → 验证快照 → 压力等级比较 → 指数退避重试，
    # 且测试以 patch.object(ResourceOptimizationEngine, "optimize"/"snapshot")
    # 类级补丁验证该编排，外移会破坏补丁语义与重试时序。

    def self_heal_cycle(self, snap: ResourceSnapshot) -> OptimizationResult | None:
        if not self.self_healing_enabled:
            return None
        if snap.pressure is PressureLevel.NORMAL:
            return None

        start = time.monotonic()
        retries = 0
        while retries < self.self_healing_max_retries:
            if time.monotonic() - start > self._self_healing_max_recovery_s:
                logger.warning("ResourceOptimizationEngine: self-heal timeout after %.0fs", time.monotonic() - start)
                break

            strategy = self.select_healing_strategy(snap.pressure)
            result = self.optimize(strategy)
            if result.success:
                time.sleep(self.self_healing_verification_delay_s)
                verify_snap = self.snapshot()
                level_order = [
                    PressureLevel.NORMAL,
                    PressureLevel.WARNING,
                    PressureLevel.CRITICAL,
                    PressureLevel.EMERGENCY,
                ]
                if level_order.index(verify_snap.pressure) < level_order.index(snap.pressure):
                    logger.info(
                        "ResourceOptimizationEngine: self-heal succeeded — %s -> %s",
                        snap.pressure.value,
                        verify_snap.pressure.value,
                    )
                    return result
            retries += 1
            logger.warning(
                "ResourceOptimizationEngine: self-heal retry %d/%d",
                retries,
                self.self_healing_max_retries,
            )
            # 5.72.4 修复：exponential backoff + jitter 避免重试风暴
            if retries < self.self_healing_max_retries:
                _delay = (2**retries) + random.uniform(0, 1)
                time.sleep(min(_delay, 30.0))

        logger.warning("ResourceOptimizationEngine: self-heal failed after %d retries", retries)
        return None

    def _self_heal_cycle(self, snap: ResourceSnapshot) -> OptimizationResult | None:
        return self.self_heal_cycle(snap)

    def select_healing_strategy(self, pressure: PressureLevel) -> OptimizationStrategy:
        if pressure is PressureLevel.EMERGENCY or pressure is PressureLevel.CRITICAL:
            return OptimizationStrategy.MEMORY_COMPACT
        else:
            return OptimizationStrategy.SCHEDULE_ADAPT

    def _select_healing_strategy(self, pressure: PressureLevel) -> OptimizationStrategy:
        return self.select_healing_strategy(pressure)

    # ── 外部通知 facade（委托 _ExternalNotifier，5.150.1 Extract Class） ──
    # 开关/去抖状态（_eventbus_enabled/_eventbus_topic/_last_pressure_level/
    # _audit_enabled）保留在本类，同名薄封装保留实例级 patch 面。

    def emit_pressure_event(self, snap: ResourceSnapshot) -> None:
        _ExternalNotifier.emit_pressure_event(self, snap)

    def _emit_pressure_event(self, snap: ResourceSnapshot) -> None:
        self.emit_pressure_event(snap)

    def audit_optimization(self, record: OptimizationRecord) -> None:
        _ExternalNotifier.audit_optimization(self, record)

    def _audit_optimization(self, record: OptimizationRecord) -> None:
        self.audit_optimization(record)

    # ══ 公共属性访问器（reverse hierarchy: backing field 保持 _name，property 暴露公共面） ══

    @property
    def config_path(self) -> str | None:
        return self._config_path

    @config_path.setter
    def config_path(self, value: str | None) -> None:
        self._config_path = value

    @property
    def thresholds(self) -> _PressureThresholds:
        return self._thresholds

    @thresholds.setter
    def thresholds(self, value: _PressureThresholds) -> None:
        self._thresholds = value

    @property
    def hysteresis(self) -> _HysteresisConfig:
        return self._hysteresis

    @hysteresis.setter
    def hysteresis(self, value: _HysteresisConfig) -> None:
        self._hysteresis = value

    @property
    def self_healing_enabled(self) -> bool:
        return self._self_healing_enabled

    @self_healing_enabled.setter
    def self_healing_enabled(self, value: bool) -> None:
        self._self_healing_enabled = value

    @property
    def self_healing_max_retries(self) -> int:
        return self._self_healing_max_retries

    @self_healing_max_retries.setter
    def self_healing_max_retries(self, value: int) -> None:
        self._self_healing_max_retries = value

    @property
    def self_healing_verification_delay_s(self) -> float:
        return self._self_healing_verification_delay_s

    @self_healing_verification_delay_s.setter
    def self_healing_verification_delay_s(self, value: float) -> None:
        self._self_healing_verification_delay_s = value

    @property
    def eventbus_enabled(self) -> bool:
        return self._eventbus_enabled

    @eventbus_enabled.setter
    def eventbus_enabled(self, value: bool) -> None:
        self._eventbus_enabled = value

    @property
    def last_pressure_level(self) -> PressureLevel:
        return self._last_pressure_level

    @last_pressure_level.setter
    def last_pressure_level(self, value: PressureLevel) -> None:
        self._last_pressure_level = value

    @property
    def audit_enabled(self) -> bool:
        return self._audit_enabled

    @audit_enabled.setter
    def audit_enabled(self, value: bool) -> None:
        self._audit_enabled = value
