# [BLUEPRINT] MOD-DATENG-005 | docs/03_modules/_domain_data_eng/gpu_resource_manager/blueprint.md
# [MODULE] zephyr.data_eng.gpu_resource_manager
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] 无（裁决核心纯内存；nvml_probe/clock/telemetry/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（盘中推理/盘后训练调度挂时段表 / 显存水位接 gpu_monitor 探针 / 降级标记接推理运行时）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配额注册表闭合(未注册kind禁止acquire); 时段表规则不重叠(首匹配确定性); OOM裁决确定性(probe.used+request>total*oom_watermark→降级CPU+告警); 分配/释放配对(release未知id拒绝); 裁决全量入telemetry; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_eng/gpu_resource_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GpuResourceError(占位 ZA-DE-UNREGISTERED-GPU-RESOURCE)——非法总量/非法配额/未注册kind/重复workload/非法请求量/未知release/时段规则重叠/probe缺失时抛
# [TESTS] tests/data_eng/test_gpu_resource_manager.py
# [A_module] module_id=MOD-DATENG-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



GpuResourceManager — GPU 资源管理器（MOD-DATENG-005）。

B5-07239（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-008，B5 R-100）：
CUDA 显存分区与预算（训练/推理配额注册表）+ 时段优先调度（盘中推理优
先/盘后训练，注入时段表）+ 显存水位监控（注入 nvml_probe 回调）+ OOM
防护裁决（超限降级 CPU 标记 + 告警），指标入 telemetry 回调。

边界声明（蓝图 §0）：gpu_monitor（D_TRADING）为 NVML 采集件——本件不采
集，只对注入 probe 的采样做配额/时段/OOM 裁决；降级只是标记
（degraded_to_cpu=True），不执行进程/设备切换（OS 副作用零）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: total_memory_mb 参数
#   fields: 参数 total_memory_mb（无注解）
#   code: gpu_resource_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: gpu_resource_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: nvml_probe 参数
#   fields: 参数 nvml_probe（无注解）
#   code: gpu_resource_manager.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: telemetry_sink 参数
#   fields: 参数 telemetry_sink（无注解）
#   code: gpu_resource_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① GpuResourceManager
#   name_en: GpuResourceManager
#   intro: GPU 资源裁决件（配额 + 时段优先 + 水位监控 + OOM 降级）。
#   desc: GPU 资源裁决件（配额 + 时段优先 + 水位监控 + OOM 降级）。；公共方法（定义序）: register_quota, set_schedule, acquire, release, check_waterm…
#   inputs: total_memory_mb clock nvml_probe telemetry_sink alert_sink oom_waterm…
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: GpuResourceManager
#   downstream: 运行时装配批（盘中推理/盘后训练调度挂时段表 / 显存水位接 gpu_monitor 探针 / 降级标记接推理运行时）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "AllocationVerdict",
    "GpuResourceError",
    "GpuResourceManager",
    "GpuSample",
    "TimeWindowRule",
    "WorkloadKind",
]


class GpuResourceError(Exception):
    """GPU 资源裁决输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DE-UNREGISTERED-GPU-RESOURCE。
    """


class WorkloadKind(str, Enum):
    """GPU 负载类型（词表闭合）。"""

    TRAINING = "training"
    INFERENCE = "inference"


@dataclass(frozen=True)
class TimeWindowRule:
    """时段优先规则：[start_minute, end_minute) 日内分钟窗口内 preferred 优先。"""

    start_minute: int
    end_minute: int
    preferred: WorkloadKind


@dataclass(frozen=True)
class GpuSample:
    """NVML 显存采样（注入 probe 的返回载荷）。"""

    used_mb: int
    total_mb: int


@dataclass(frozen=True)
class AllocationVerdict:
    """显存分配裁决（on_gpu=False 即降级 CPU 标记）。"""

    workload_id: str
    kind: WorkloadKind
    requested_mb: int
    granted_mb: int
    on_gpu: bool
    degraded_to_cpu: bool
    reason: str


@dataclass
class _Allocation:
    kind: WorkloadKind
    granted_mb: int


class GpuResourceManager:
    """GPU 资源裁决件（配额 + 时段优先 + 水位监控 + OOM 降级）。"""

    def __init__(
        self,
        *,
        total_memory_mb: int,
        clock: Callable[[], datetime.datetime] | None = None,
        nvml_probe: Callable[[], GpuSample] | None = None,
        telemetry_sink: Callable[[object], None] | None = None,
        alert_sink: Callable[[str], None] | None = None,
        oom_watermark: float = 0.9,
    ) -> None:
        if total_memory_mb <= 0:
            raise GpuResourceError(f"total_memory_mb 非法: {total_memory_mb}")
        if not 0.0 < oom_watermark <= 1.0:
            raise GpuResourceError(f"oom_watermark 非法: {oom_watermark}")
        self._total_mb = total_memory_mb
        self._clock = clock or datetime.datetime.now
        self._probe = nvml_probe
        self._telemetry = telemetry_sink
        self._alert_sink = alert_sink
        self._oom_watermark = oom_watermark
        self._quotas: dict[WorkloadKind, int] = {}
        self._rules: tuple[TimeWindowRule, ...] = ()
        self._allocations: dict[str, _Allocation] = {}

    # ── 配额与时段表注册 ──────────────────────────────────────────────────

    def register_quota(self, kind: WorkloadKind, budget_mb: int) -> None:
        """显存分区预算：kind ∈ 词表，budget ∈ (0, total]。"""
        if not isinstance(kind, WorkloadKind):
            raise GpuResourceError(f"非法负载类型: {kind!r}")
        if budget_mb <= 0 or budget_mb > self._total_mb:
            raise GpuResourceError(f"budget_mb 非法: {budget_mb}")
        self._quotas[kind] = budget_mb

    def set_schedule(self, rules: Iterable[TimeWindowRule]) -> None:
        """时段优先表：日内分钟窗口不重叠（重叠 Fail-Closed）。"""
        items = sorted(rules, key=lambda r: (r.start_minute, r.end_minute))
        prev_end = -1
        for rule in items:
            if not 0 <= rule.start_minute < rule.end_minute <= 1440:
                raise GpuResourceError(f"时段窗口非法: [{rule.start_minute}, {rule.end_minute})")
            if not isinstance(rule.preferred, WorkloadKind):
                raise GpuResourceError(f"非法优先类型: {rule.preferred!r}")
            if rule.start_minute < prev_end:
                raise GpuResourceError(f"时段规则重叠: [{rule.start_minute}, {rule.end_minute}) 与前一规则相交")
            prev_end = rule.end_minute
        self._rules = tuple(items)

    # ── 分配裁决 ──────────────────────────────────────────────────────────

    def acquire(self, workload_id: str, kind: WorkloadKind, request_mb: int) -> AllocationVerdict:
        """分配裁决：时段优先 → 配额预算 → OOM 水位，任一不通过即降级 CPU。"""
        if not workload_id:
            raise GpuResourceError("workload_id 为空")
        if workload_id in self._allocations:
            raise GpuResourceError(f"workload 重复分配: {workload_id!r}")
        if kind not in self._quotas:
            raise GpuResourceError(f"未注册配额: {kind!r}（配额注册表闭合）")
        if request_mb <= 0:
            raise GpuResourceError(f"request_mb 非法: {request_mb}")

        verdict = self._judge(workload_id, kind, request_mb)
        if verdict.on_gpu:
            self._allocations[workload_id] = _Allocation(kind=kind, granted_mb=request_mb)
        else:
            self._alert(f"GPU分配降级CPU: {workload_id} kind={kind.value} reason={verdict.reason}")
        self._emit_telemetry(verdict)
        return verdict

    def _judge(self, workload_id: str, kind: WorkloadKind, request_mb: int) -> AllocationVerdict:
        # ① 时段优先：当前时刻落在优先他类的窗口 → 非优先类降级
        now = self._clock()
        minute = now.hour * 60 + now.minute
        for rule in self._rules:
            if rule.start_minute <= minute < rule.end_minute and rule.preferred is not kind:
                return self._verdict(
                    workload_id,
                    kind,
                    request_mb,
                    0,
                    False,
                    f"TIME_WINDOW_PRIORITY({minute}min 窗口优先 {rule.preferred.value})",
                )
        # ② 配额预算：本类已批 + 请求 > 预算 → 降级
        used_by_kind = sum(a.granted_mb for a in self._allocations.values() if a.kind is kind)
        budget = self._quotas[kind]
        if used_by_kind + request_mb > budget:
            return self._verdict(
                workload_id,
                kind,
                request_mb,
                0,
                False,
                f"QUOTA_EXCEEDED({used_by_kind}+{request_mb}>{budget}MB)",
            )
        # ③ OOM 水位：probe 当前占用 + 请求 > total*watermark → 降级
        if self._probe is not None:
            sample = self._probe()
            if sample.used_mb + request_mb > self._total_mb * self._oom_watermark:
                return self._verdict(
                    workload_id,
                    kind,
                    request_mb,
                    0,
                    False,
                    f"OOM_GUARD({sample.used_mb}+{request_mb}>{self._total_mb * self._oom_watermark:.0f}MB)",
                )
        return self._verdict(workload_id, kind, request_mb, request_mb, True, "GRANTED")

    @staticmethod
    def _verdict(
        workload_id: str,
        kind: WorkloadKind,
        requested_mb: int,
        granted_mb: int,
        on_gpu: bool,
        reason: str,
    ) -> AllocationVerdict:
        return AllocationVerdict(
            workload_id=workload_id,
            kind=kind,
            requested_mb=requested_mb,
            granted_mb=granted_mb,
            on_gpu=on_gpu,
            degraded_to_cpu=not on_gpu,
            reason=reason,
        )

    # ── 释放 ──────────────────────────────────────────────────────────────

    def release(self, workload_id: str) -> None:
        """释放分配（未知 id → Fail-Closed）。"""
        alloc = self._allocations.pop(workload_id, None)
        if alloc is None:
            raise GpuResourceError(f"未知 workload: {workload_id!r}（分配/释放须配对）")
        _log.info("GPU分配释放: %s kind=%s %dMB", workload_id, alloc.kind.value, alloc.granted_mb)

    # ── 水位监控 ──────────────────────────────────────────────────────────

    def check_watermark(self) -> GpuSample:
        """显存水位监控：probe 采样 → 超 OOM 水位告警；样本入 telemetry。"""
        if self._probe is None:
            raise GpuResourceError("nvml_probe 未注入（水位监控强制注入探针）")
        sample = self._probe()
        if sample.used_mb < 0 or sample.total_mb <= 0:
            raise GpuResourceError(f"probe 采样非法: {sample!r}")
        self._emit_telemetry(sample)
        if sample.used_mb >= sample.total_mb * self._oom_watermark:
            self._alert(f"显存水位告警: {sample.used_mb}/{sample.total_mb}MB >= watermark {self._oom_watermark}")
        return sample

    # ── 状态快照 ──────────────────────────────────────────────────────────

    def status(self) -> dict[str, object]:
        """运行状态快照（确定性）。"""
        return {
            "total_memory_mb": self._total_mb,
            "quotas_mb": {k.value: v for k, v in sorted(self._quotas.items())},
            "used_by_kind_mb": {
                k.value: sum(a.granted_mb for a in self._allocations.values() if a.kind is k)
                for k in sorted(self._quotas)
            },
            "allocations": len(self._allocations),
            "schedule_rules": len(self._rules),
        }

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, message: str) -> None:
        _log.warning("GPU资源告警: %s", message)
        if self._alert_sink is not None:
            try:
                self._alert_sink(message)
            except Exception:  # noqa: BLE001 — 告警不阻断
                _log.exception("alert_sink 告警失败")

    def _emit_telemetry(self, payload: object) -> None:
        if self._telemetry is not None:
            try:
                self._telemetry(payload)
            except Exception:  # noqa: BLE001 — telemetry 不阻断裁决
                _log.exception("telemetry_sink 回调失败")
