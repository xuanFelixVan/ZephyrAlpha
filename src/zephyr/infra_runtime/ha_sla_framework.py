# [BLUEPRINT] MOD-INF-076 | docs/03_modules/_domain_infrastructure_runtime/ha_sla_framework/blueprint.md
# [MODULE] zephyr.infra_runtime.ha_sla_framework
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（纯内存编排；时钟/restart/升级回调全注入）
# [CONSUMERS] 运行时装配批（单机进程 SLA 登记/健康探针编排/自动重启编排）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SLA/探针名唯一; target_pct∈(0,100]; window/interval/timeout>0; 探针异常按不健康计; elapsed>timeout 判超时 unhealthy; 连续失败≥threshold 触发注入 restart(回调异常不阻断); 冷却期内抑制重启并留痕; SLA 统计窗口 [now-window,now] 无样本 Fail-Closed; 严格单机不做集群; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/ha_sla_framework/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] HaSlaError(占位 ZA-INF-UNREGISTERED-HA-SLA)——空名/重复注册/非法阈值/未知SLA或探针/SLA无绑定探针/窗口无样本时抛
# [TESTS] tests/infra_runtime/test_ha_sla_framework.py
# [A_module] module_id=MOD-INF-076 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
HaSlaFramework — 高性能高可用保障框架（MOD-INF-076）。

B10-02366（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-009，A9运维架构）：
SLA 注册表（register_sla）+ 健康探针编排（register_probe 周期/超时/降级）
+ 进程级自动重启编排（复用 A9 NSSM/Supervisor 语义，注入 restart 回调，
健康失败 N 次触发 + 冷却期）+ SLA 违约判定与升级链路（注入升级回调）。
严格单机范围，不做集群。

纯内存确定性：时钟注入（探针耗时=时钟差，假时钟可模拟耗时/超时）；
restart/升级回调异常不阻断编排，仅留痕。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: ha_sla_framework.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: escalation_sink 参数
#   fields: 参数 escalation_sink（无注解）
#   code: ha_sla_framework.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HaSlaFramework
#   name_en: HaSlaFramework
#   intro: 单机 HA/SLA 框架（SLA 注册表 + 探针编排 + 自动重启编排）。
#   desc: 单机 HA/SLA 框架（SLA 注册表 + 探针编排 + 自动重启编排）。；公共方法（定义序）: register_sla, register_probe, bind_restart, run_probe, due_…
#   inputs: clock escalation_sink
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: HaSlaFramework
#   downstream: 运行时装配批（单机进程 SLA 登记/健康探针编排/自动重启编排）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "HaSlaError",
    "HaSlaFramework",
    "ProbeResult",
    "RestartEvent",
    "SlaReport",
    "SlaTarget",
]


class HaSlaError(Exception):
    """HA/SLA 编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-HA-SLA。
    """


@dataclass(frozen=True)
class SlaTarget:
    """SLA 目标声明（frozen）。"""

    name: str
    target_pct: float
    window: float


@dataclass(frozen=True)
class ProbeResult:
    """单次探针执行结果（frozen）。"""

    probe: str
    ok: bool
    elapsed: float
    at: float
    timed_out: bool


@dataclass(frozen=True)
class RestartEvent:
    """自动重启事件（invoked=False 为冷却期抑制留痕，frozen）。"""

    probe: str
    at: float
    consecutive_failures: int
    invoked: bool
    detail: str


@dataclass(frozen=True)
class SlaReport:
    """SLA 窗口评估报告（frozen）。"""

    name: str
    target_pct: float
    actual_pct: float
    window: float
    total: int
    healthy: int
    breached: bool
    evaluated_at: float


@dataclass(frozen=True)
class _ProbeSpec:
    probe: Callable[[], bool]
    interval: float
    timeout: float


@dataclass(frozen=True)
class _RestartBinding:
    restart: Callable[[str], None]
    failure_threshold: int
    cooldown: float


class HaSlaFramework:
    """单机 HA/SLA 框架（SLA 注册表 + 探针编排 + 自动重启编排）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], float] | None = None,
        escalation_sink: Callable[[SlaReport], None] | None = None,
    ) -> None:
        self._clock = clock or time.monotonic
        self._escalation_sink = escalation_sink
        self._slas: dict[str, SlaTarget] = {}
        self._probes: dict[str, _ProbeSpec] = {}
        self._restart_bindings: dict[str, _RestartBinding] = {}
        self._history: dict[str, list[ProbeResult]] = {}
        self._last_run_at: dict[str, float] = {}
        self._consecutive_failures: dict[str, int] = {}
        self._last_restart_at: dict[str, float] = {}
        self._restart_events: dict[str, list[RestartEvent]] = {}

    # ── 注册 ─────────────────────────────────────────────────────────────

    def register_sla(self, name: str, target_pct: float, window: float) -> SlaTarget:
        """登记 SLA 目标（名称唯一；0 < target_pct ≤ 100；window > 0）。"""
        if not name:
            raise HaSlaError("SLA 名为空")
        if name in self._slas:
            raise HaSlaError(f"SLA 重复注册: {name!r}")
        if not isinstance(target_pct, (int, float)) or not 0 < target_pct <= 100:
            raise HaSlaError(f"target_pct 非法: {target_pct!r}（须 ∈ (0,100]）")
        if not isinstance(window, (int, float)) or window <= 0:
            raise HaSlaError(f"window 非法: {window!r}（须 > 0）")
        sla = SlaTarget(name=name, target_pct=float(target_pct), window=float(window))
        self._slas[name] = sla
        return sla

    def register_probe(
        self,
        name: str,
        probe: Callable[[], bool],
        interval: float,
        timeout: float,
    ) -> None:
        """登记健康探针（名称唯一；interval/timeout > 0）。"""
        if not name:
            raise HaSlaError("探针名为空")
        if name in self._probes:
            raise HaSlaError(f"探针重复注册: {name!r}")
        if not callable(probe):
            raise HaSlaError(f"probe 不可调用: {probe!r}")
        if not isinstance(interval, (int, float)) or interval <= 0:
            raise HaSlaError(f"interval 非法: {interval!r}（须 > 0）")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise HaSlaError(f"timeout 非法: {timeout!r}（须 > 0）")
        self._probes[name] = _ProbeSpec(probe=probe, interval=float(interval), timeout=float(timeout))
        self._history[name] = []
        self._consecutive_failures[name] = 0
        self._restart_events[name] = []

    def bind_restart(
        self,
        probe_name: str,
        restart: Callable[[str], None],
        failure_threshold: int,
        cooldown: float,
    ) -> None:
        """绑定自动重启编排（连续失败 threshold 次触发；冷却期内抑制）。"""
        if probe_name not in self._probes:
            raise HaSlaError(f"未知探针: {probe_name!r}")
        if not callable(restart):
            raise HaSlaError(f"restart 不可调用: {restart!r}")
        if not isinstance(failure_threshold, int) or failure_threshold <= 0:
            raise HaSlaError(f"failure_threshold 非法: {failure_threshold!r}（须为正整数）")
        if not isinstance(cooldown, (int, float)) or cooldown < 0:
            raise HaSlaError(f"cooldown 非法: {cooldown!r}（须 ≥ 0）")
        self._restart_bindings[probe_name] = _RestartBinding(
            restart=restart, failure_threshold=failure_threshold, cooldown=float(cooldown)
        )

    # ── 探针编排 ──────────────────────────────────────────────────────────

    def run_probe(self, name: str) -> ProbeResult:
        """执行一次探针：异常/超时按不健康计；驱动自动重启编排。"""
        spec = self._probes.get(name)
        if spec is None:
            raise HaSlaError(f"未知探针: {name!r}")
        started = self._clock()
        ok = False
        try:
            ok = bool(spec.probe())
        except Exception:  # noqa: BLE001 — 探针异常按不健康计不抛
            _log.exception("探针执行异常: %s", name)
        finished = self._clock()
        elapsed = finished - started
        timed_out = elapsed > spec.timeout
        if timed_out:
            ok = False
        result = ProbeResult(probe=name, ok=ok, elapsed=elapsed, at=finished, timed_out=timed_out)
        self._history[name].append(result)
        self._last_run_at[name] = finished
        self._after_probe(name, ok, finished)
        return result

    def _after_probe(self, name: str, ok: bool, now: float) -> None:
        if ok:
            self._consecutive_failures[name] = 0
            return
        self._consecutive_failures[name] += 1
        binding = self._restart_bindings.get(name)
        if binding is None:
            return
        failures = self._consecutive_failures[name]
        if failures < binding.failure_threshold:
            return
        last_restart = self._last_restart_at.get(name)
        if last_restart is not None and now - last_restart < binding.cooldown:
            self._restart_events[name].append(
                RestartEvent(
                    probe=name,
                    at=now,
                    consecutive_failures=failures,
                    invoked=False,
                    detail=f"冷却期内抑制（距上次重启 {now - last_restart:.6f}s < {binding.cooldown}s）",
                )
            )
            return
        detail = "重启回调已调用"
        try:
            binding.restart(name)
        except Exception:  # noqa: BLE001 — 重启回调异常不阻断编排
            _log.exception("restart 回调异常: %s", name)
            detail = "restart 回调异常（已留痕）"
        self._last_restart_at[name] = now
        self._consecutive_failures[name] = 0
        self._restart_events[name].append(
            RestartEvent(probe=name, at=now, consecutive_failures=failures, invoked=True, detail=detail)
        )

    def due_probes(self) -> tuple[str, ...]:
        """到期探针（从未运行或距上次 ≥ interval；确定性排序）。"""
        now = self._clock()
        due = [
            name
            for name, spec in self._probes.items()
            if name not in self._last_run_at or now - self._last_run_at[name] >= spec.interval
        ]
        return tuple(sorted(due))

    # ── SLA 评估 ──────────────────────────────────────────────────────────

    def sla_report(self, name: str) -> SlaReport:
        """SLA 窗口评估（[now-window, now]；无样本 Fail-Closed）。"""
        sla = self._slas.get(name)
        if sla is None:
            raise HaSlaError(f"未知 SLA: {name!r}")
        if name not in self._probes:
            raise HaSlaError(f"SLA {name!r} 无同名绑定探针（无法取样）")
        now = self._clock()
        samples = [r for r in self._history[name] if now - sla.window <= r.at <= now]
        if not samples:
            raise HaSlaError(f"SLA {name!r} 窗口内无样本（window={sla.window}s）")
        healthy = sum(1 for r in samples if r.ok)
        total = len(samples)
        actual = healthy / total * 100.0
        return SlaReport(
            name=name,
            target_pct=sla.target_pct,
            actual_pct=actual,
            window=sla.window,
            total=total,
            healthy=healthy,
            breached=actual < sla.target_pct,
            evaluated_at=now,
        )

    def evaluate_sla(self, name: str) -> SlaReport:
        """SLA 违约判定 + 升级链路（违约且注入升级回调 → 通报，不阻断）。"""
        report = self.sla_report(name)
        if report.breached and self._escalation_sink is not None:
            try:
                self._escalation_sink(report)
            except Exception:  # noqa: BLE001 — 升级回调不阻断（蓝图 §1）
                _log.exception("escalation_sink 升级失败: %s", name)
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    def probe_history(self, name: str) -> tuple[ProbeResult, ...]:
        """探针历史（按执行先后，确定性）。"""
        if name not in self._probes:
            raise HaSlaError(f"未知探针: {name!r}")
        return tuple(self._history[name])

    def restart_events(self, name: str) -> tuple[RestartEvent, ...]:
        """重启事件留痕（含冷却期抑制记录，按发生先后）。"""
        if name not in self._probes:
            raise HaSlaError(f"未知探针: {name!r}")
        return tuple(self._restart_events[name])
