# [BLUEPRINT] MOD-INF-085 | docs/03_modules/_domain_infrastructure_operations/wal_checkpoint_monitor/blueprint.md
# [MODULE] zephyr.infra_ops.wal_checkpoint_monitor
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 无（协议核心纯内存；metrics_probe/checkpoint_runner/telemetry_sink/alert_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（SQLite WAL 库绑定 probe / checkpoint 执行器 / telemetry 指标路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阈值 0≤warn<critical; 采集非法(负值/缺probe)Fail-Closed; WARN→PASSIVE/CRITICAL→TRUNCATE 策略裁决确定性; checkpoint 执行仅经注入回调不直连 DB; telemetry 逐指标回调; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/wal_checkpoint_monitor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] WalMonitorError(占位 ZA-INF-UNREGISTERED-WAL-MONITOR)——阈值非法/probe缺失/采集值非法/runner缺失或执行失败时抛
# [TESTS] tests/infra_ops/test_wal_checkpoint_monitor.py
# [A_module] module_id=MOD-INF-085 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""WalCheckpointMonitor — SQLite WAL 检查点监控器（MOD-INF-085）。

B13-04268（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-003，A3数据
架构）：SQLite WAL 运行态监控——wal 文件大小 / checkpoint 耗时 / 写入速率
三指标采集（注入 metrics_probe 回调，不直连 DB），阈值预警分级
（OK/WARN/CRITICAL），自动 checkpoint 策略裁决（达 WARN 阈→PASSIVE，达
CRITICAL 阈→TRUNCATE；执行经注入 checkpoint_runner 回调，未注入
Fail-Closed），并挂 telemetry 指标回调供仪表盘消费。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AlertLevel",
    "CheckpointMode",
    "WalMetrics",
    "WalMonitorError",
    "WalCheckpointMonitor",
]


class WalMonitorError(Exception):
    """WAL 监控输入/执行非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-WAL-MONITOR。
    """


class AlertLevel(str, Enum):
    """预警分级（词表闭合）。"""

    OK = "ok"
    WARN = "warn"
    CRITICAL = "critical"


class CheckpointMode(str, Enum):
    """SQLite checkpoint 模式。"""

    PASSIVE = "PASSIVE"
    FULL = "FULL"
    TRUNCATE = "TRUNCATE"


@dataclass(frozen=True)
class WalMetrics:
    """WAL 采集快照（frozen）。"""

    wal_bytes: int
    checkpoint_ms: float
    write_rate: float
    collected_at: datetime.datetime


class WalCheckpointMonitor:
    """WAL 监控件（采集 + 分级 + 策略裁决 + telemetry）。"""

    def __init__(
        self,
        *,
        warn_threshold_bytes: int,
        critical_threshold_bytes: int,
        metrics_probe: Callable[[], WalMetrics] | None = None,
        checkpoint_runner: Callable[[CheckpointMode], bool] | None = None,
        telemetry_sink: Callable[[str, float], None] | None = None,
        alert_sink: Callable[[AlertLevel, WalMetrics], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if warn_threshold_bytes < 0 or critical_threshold_bytes < 0:
            raise WalMonitorError("阈值不可为负")
        if warn_threshold_bytes >= critical_threshold_bytes:
            raise WalMonitorError(
                f"阈值非法: warn({warn_threshold_bytes}) 须严格小于 critical({critical_threshold_bytes})"
            )
        self._warn = warn_threshold_bytes
        self._critical = critical_threshold_bytes
        self._probe = metrics_probe
        self._runner = checkpoint_runner
        self._telemetry = telemetry_sink
        self._alert_sink = alert_sink
        self._clock = clock or datetime.datetime.now
        self._last: WalMetrics | None = None

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _emit_telemetry(self, m: WalMetrics) -> None:
        if self._telemetry is None:
            return
        try:
            self._telemetry("wal_bytes", float(m.wal_bytes))
            self._telemetry("wal_checkpoint_ms", float(m.checkpoint_ms))
            self._telemetry("wal_write_rate", float(m.write_rate))
        except Exception:  # noqa: BLE001 — 指标回调不阻断监控主路
            _log.exception("telemetry_sink 回调失败")

    def _alert(self, level: AlertLevel, m: WalMetrics) -> None:
        _log.warning("WAL 预警: %s wal_bytes=%d", level.value, m.wal_bytes)
        if self._alert_sink is not None:
            try:
                self._alert_sink(level, m)
            except Exception:  # noqa: BLE001 — 告警不阻断
                _log.exception("alert_sink 告警失败")

    # ── 采集 ─────────────────────────────────────────────────────────────

    def collect(self) -> WalMetrics:
        """采集一次：probe 未注入/采集值非法 → Fail-Closed。"""
        if self._probe is None:
            raise WalMonitorError("metrics_probe 未注入（禁止直连 DB 采集）")
        m = self._probe()
        if not isinstance(m, WalMetrics):
            raise WalMonitorError(f"probe 返回值非法: {type(m)!r}（须为 WalMetrics）")
        if m.wal_bytes < 0 or m.checkpoint_ms < 0 or m.write_rate < 0:
            raise WalMonitorError(
                f"采集值非法（负值）: wal_bytes={m.wal_bytes} "
                f"checkpoint_ms={m.checkpoint_ms} write_rate={m.write_rate}"
            )
        self._last = m
        self._emit_telemetry(m)
        return m

    # ── 分级与策略裁决 ────────────────────────────────────────────────────

    def assess(self, metrics: WalMetrics) -> AlertLevel:
        """阈值分级：≥critical→CRITICAL；≥warn→WARN；否则 OK。"""
        if metrics.wal_bytes >= self._critical:
            return AlertLevel.CRITICAL
        if metrics.wal_bytes >= self._warn:
            return AlertLevel.WARN
        return AlertLevel.OK

    def decide_checkpoint(self, metrics: WalMetrics) -> CheckpointMode | None:
        """策略裁决：WARN→PASSIVE；CRITICAL→TRUNCATE；OK→不触发。"""
        level = self.assess(metrics)
        if level is AlertLevel.CRITICAL:
            return CheckpointMode.TRUNCATE
        if level is AlertLevel.WARN:
            return CheckpointMode.PASSIVE
        return None

    # ── 巡检主路 ─────────────────────────────────────────────────────────

    def tick(self) -> AlertLevel:
        """采集→分级→按裁决执行 checkpoint（经注入 runner）→ 告警留痕。"""
        m = self.collect()
        level = self.assess(m)
        mode = self.decide_checkpoint(m)
        if mode is None:
            return level
        self._alert(level, m)
        if self._runner is None:
            raise WalMonitorError(
                f"checkpoint_runner 未注入（{level.value} 级须执行 {mode.value}，禁止旁路）"
            )
        try:
            ok = bool(self._runner(mode))
        except Exception as exc:  # noqa: BLE001 — 执行异常按失败处理
            _log.exception("checkpoint_runner 执行异常: %s", mode.value)
            raise WalMonitorError(f"checkpoint 执行异常: {mode.value}") from exc
        if not ok:
            raise WalMonitorError(f"checkpoint 执行失败（NACK）: {mode.value}")
        return level

    # ── 查询 ─────────────────────────────────────────────────────────────

    @property
    def last_metrics(self) -> WalMetrics | None:
        """最近一次采集快照（未采集为 None）。"""
        return self._last
