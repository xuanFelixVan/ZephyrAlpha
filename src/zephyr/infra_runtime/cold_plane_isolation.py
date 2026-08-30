# [BLUEPRINT] MOD-INF-079 | docs/03_modules/_domain_infrastructure_runtime/cold_plane_isolation/blueprint.md
# [MODULE] zephyr.infra_runtime.cold_plane_isolation
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（隔离核心纯内存；clock/is_trading_hours/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（Cold 平面配额声明校验 / 通道白名单门禁 / 盘中产出盘后激活）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配额闭合校验(核⊆16-19/内存≤20GB/IO BelowNormal/iFind≤5QPS); Cold→Warm 仅 config:* 前缀 30s 轮询通道; Cold→Hot 直连拒绝+告警(Fail-Closed); iFind 令牌桶超限拒绝; 盘中产出入待激活队列盘后应用(pending→applied); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/cold_plane_isolation/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ColdPlaneError(占位 ZA-INF-UNREGISTERED-COLD-PLANE)——配额越界/通道白名单外/Cold→Hot直连/QPS超限/空artifact_id/盘中激活时抛
# [TESTS] tests/infra_runtime/test_cold_plane_isolation.py
# [A_module] module_id=MOD-INF-079 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ColdPlaneIsolator — Cold 平面（>1s）隔离器（MOD-INF-079）。

B14-04550（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-012，A9 运维架构
§平面隔离）：Cold 平面资源配额声明与校验（核 16-19 / 内存 ≤20GB / IO
BelowNormal / iFind ≤5QPS 令牌桶，时钟注入），Cold→Warm 仅经 `config:*` 前
缀 30s 轮询**通道白名单**，Cold→Hot **禁直连**（越界调用拒绝 + 告警回调，
Fail-Closed），盘中产出入**待激活队列**盘后应用（pending→applied 状态机，
注入 is_trading_hours 判定）。

查重分工（蓝图 §0）：resource_scheduler=三平面资源隔离统一裁决（本件只做
Cold 平面侧声明校验与通道门禁，不重复 cgroup 级隔离）；latency_budget_
allocator=延迟预算分解（零交集）；runtime_plane_tag=平面标签契约（本件复用
其平面语义，不重建标签体系）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: cold_plane_isolation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: is_trading_hours 参数
#   fields: 参数 is_trading_hours（无注解）
#   code: cold_plane_isolation.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: cold_plane_isolation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ColdPlaneIsolator
#   name_en: ColdPlaneIsolator
#   intro: Cold 平面隔离件（配额校验 + 通道门禁 + iFind 令牌桶 + 待激活队列）。
#   desc: Cold 平面隔离件（配额校验 + 通道门禁 + iFind 令牌桶 + 待激活队列）。；公共方法（定义序）: declare_quota, open_channel, is_open, acquire_ifind,…
#   inputs: clock is_trading_hours alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: ColdPlaneIsolator
#   downstream: 运行时装配批（Cold 平面配额声明校验 / 通道白名单门禁 / 盘中产出盘后激活）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ALLOWED_CORES",
    "CHANNEL_POLL_INTERVAL_S",
    "CHANNEL_PREFIX",
    "ColdPlaneError",
    "ColdPlaneIsolator",
    "ColdPlaneViolation",
    "IFIND_MAX_QPS",
    "MAX_MEMORY_GB",
    "PendingActivation",
    "PendingStatus",
    "Plane",
    "ResourceQuota",
    "REQUIRED_IO_PRIORITY",
]

#: 配额常量：Cold 平面可用核组（核 16-19）
ALLOWED_CORES: Final[frozenset[int]] = frozenset({16, 17, 18, 19})
#: 配额常量：内存上限（GB）
MAX_MEMORY_GB: Final[int] = 20
#: 配额常量：IO 优先级必须为 BelowNormal
REQUIRED_IO_PRIORITY: Final[str] = "below_normal"
#: 配额常量：iFind 拉取 QPS 上限（令牌桶容量与速率）
IFIND_MAX_QPS: Final[float] = 5.0
#: 通道白名单：Cold→Warm 仅允许 config:* 前缀
CHANNEL_PREFIX: Final[str] = "config:"
#: 通道白名单：Cold→Warm 轮询间隔（秒）
CHANNEL_POLL_INTERVAL_S: Final[float] = 30.0


class ColdPlaneError(Exception):
    """Cold 平面隔离输入/越界调用非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-COLD-PLANE。
    """


class Plane(str, Enum):
    """运行时平面（Cold >1s / Warm <1s / Hot <10ms）。"""

    COLD = "cold"
    WARM = "warm"
    HOT = "hot"


class PendingStatus(str, Enum):
    """待激活队列状态机。"""

    PENDING = "pending"
    APPLIED = "applied"


@dataclass(frozen=True)
class ResourceQuota:
    """Cold 平面资源配额声明（frozen）。"""

    cores: tuple[int, ...]
    memory_gb: float
    io_priority: str
    ifind_qps: float


@dataclass(frozen=True)
class ColdPlaneViolation:
    """Cold 平面越界调用（告警载荷）。"""

    source: Plane
    target: Plane
    channel: str
    reason: str
    raised_at: datetime.datetime


@dataclass(frozen=True)
class PendingActivation:
    """盘中产出待激活条目（状态机 pending→applied）。"""

    artifact_id: str
    payload: dict
    status: PendingStatus
    produced_at: datetime.datetime
    applied_at: datetime.datetime | None = None


class ColdPlaneIsolator:
    """Cold 平面隔离件（配额校验 + 通道门禁 + iFind 令牌桶 + 待激活队列）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        is_trading_hours: Callable[[], bool] | None = None,
        alert_sink: Callable[[ColdPlaneViolation], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._is_trading_hours = is_trading_hours or (lambda: False)
        self._alert_sink = alert_sink
        self._channels: dict[str, tuple[Plane, Plane, float]] = {}
        self._pending: dict[str, PendingActivation] = {}
        self._tokens = float(IFIND_MAX_QPS)
        self._qps = float(IFIND_MAX_QPS)
        self._last_refill: datetime.datetime | None = None

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, source: Plane, target: Plane, channel: str, reason: str) -> None:
        violation = ColdPlaneViolation(
            source=source,
            target=target,
            channel=channel,
            reason=reason,
            raised_at=self._clock(),
        )
        _log.warning("Cold 平面越界: %s -> %s (%s)", source.value, target.value, reason)
        if self._alert_sink is not None:
            try:
                self._alert_sink(violation)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _refill(self, now: datetime.datetime) -> None:
        if self._last_refill is None:
            self._last_refill = now
            return
        elapsed = max((now - self._last_refill).total_seconds(), 0.0)
        self._tokens = min(self._qps, self._tokens + elapsed * self._qps)
        self._last_refill = now

    # ── 配额声明校验 ──────────────────────────────────────────────────────

    def declare_quota(self, quota: ResourceQuota) -> ResourceQuota:
        """配额声明校验：核⊆16-19 / 内存≤20GB / IO BelowNormal / iFind≤5QPS。"""
        if not isinstance(quota, ResourceQuota):
            raise ColdPlaneError(f"非法配额对象: {type(quota)!r}")
        if not quota.cores:
            raise ColdPlaneError("核组声明为空")
        bad = [c for c in quota.cores if c not in ALLOWED_CORES]
        if bad:
            raise ColdPlaneError(f"核组越界: {bad!r}（Cold 平面仅允许核 16-19）")
        if not (0 < quota.memory_gb <= MAX_MEMORY_GB):
            raise ColdPlaneError(f"内存配额越界: {quota.memory_gb}GB（合法区间 (0, {MAX_MEMORY_GB}]）")
        if quota.io_priority != REQUIRED_IO_PRIORITY:
            raise ColdPlaneError(f"IO 优先级非法: {quota.io_priority!r}（Cold 平面须为 below_normal）")
        if not (0 < quota.ifind_qps <= IFIND_MAX_QPS):
            raise ColdPlaneError(f"iFind QPS 越界: {quota.ifind_qps}（合法区间 (0, {IFIND_MAX_QPS}]）")
        # 声明驱动令牌桶：取声明 QPS（≤5）重建桶，满桶起始
        self._qps = float(quota.ifind_qps)
        self._tokens = self._qps
        self._last_refill = None
        return quota

    # ── 通道白名单 ────────────────────────────────────────────────────────

    def open_channel(
        self,
        channel: str,
        source: Plane,
        target: Plane,
        *,
        poll_interval_s: float = CHANNEL_POLL_INTERVAL_S,
    ) -> None:
        """通道开闸：Cold→Hot 直连拒绝+告警；Cold→Warm 仅 config:* 30s 轮询。"""
        if not channel:
            raise ColdPlaneError("channel 为空")
        if not isinstance(source, Plane) or not isinstance(target, Plane):
            raise ColdPlaneError(f"非法平面: {source!r} -> {target!r}")
        if channel in self._channels:
            raise ColdPlaneError(f"channel 重复: {channel!r}")
        if source is Plane.COLD and target is Plane.HOT:
            reason = f"Cold→Hot 直连拒绝: 通道 {channel!r} 越界（Fail-Closed）"
            self._alert(source, target, channel, reason)
            raise ColdPlaneError(reason)
        if source is Plane.COLD and target is Plane.WARM:
            if not channel.startswith(CHANNEL_PREFIX):
                reason = f"Cold→Warm 白名单外通道拒绝: {channel!r}（仅允许 {CHANNEL_PREFIX}* 前缀）"
                self._alert(source, target, channel, reason)
                raise ColdPlaneError(reason)
            if poll_interval_s != CHANNEL_POLL_INTERVAL_S:
                raise ColdPlaneError(f"Cold→Warm 轮询间隔非法: {poll_interval_s}s（须为 {CHANNEL_POLL_INTERVAL_S}s）")
        self._channels[channel] = (source, target, float(poll_interval_s))

    def is_open(self, channel: str) -> bool:
        """通道是否已开闸。"""
        return channel in self._channels

    # ── iFind 令牌桶 ──────────────────────────────────────────────────────

    def acquire_ifind(self) -> None:
        """iFind 拉取令牌（声明 QPS 令牌桶，注入时钟 refill；超限拒绝）。"""
        now = self._clock()
        self._refill(now)
        if self._tokens < 1.0:
            raise ColdPlaneError(f"iFind QPS 超限: 令牌耗尽（上限 {self._qps} QPS，Fail-Closed）")
        self._tokens -= 1.0

    # ── 盘中产出待激活队列 ────────────────────────────────────────────────

    def submit_artifact(self, artifact_id: str, payload: dict) -> None:
        """盘中产出登记为 pending（artifact_id 非空唯一），盘后统一激活。"""
        if not artifact_id:
            raise ColdPlaneError("artifact_id 为空")
        if artifact_id in self._pending:
            raise ColdPlaneError(f"artifact_id 重复: {artifact_id!r}")
        self._pending[artifact_id] = PendingActivation(
            artifact_id=artifact_id,
            payload=dict(payload),
            status=PendingStatus.PENDING,
            produced_at=self._clock(),
        )

    def apply_pending(self) -> list[PendingActivation]:
        """盘后应用：非交易时段方允许；按 (produced_at,artifact_id) 确定性激活。"""
        if self._is_trading_hours():
            raise ColdPlaneError("交易时段禁止激活 Cold 平面产出（Fail-Closed）")
        now = self._clock()
        applied: list[PendingActivation] = []
        for artifact_id in sorted(
            self._pending,
            key=lambda aid: (self._pending[aid].produced_at, aid),
        ):
            entry = self._pending[artifact_id]
            if entry.status is PendingStatus.PENDING:
                entry = PendingActivation(
                    artifact_id=entry.artifact_id,
                    payload=entry.payload,
                    status=PendingStatus.APPLIED,
                    produced_at=entry.produced_at,
                    applied_at=now,
                )
                self._pending[artifact_id] = entry
            applied.append(entry)
        return applied

    def pending_activations(self, status: PendingStatus | None = None) -> list[PendingActivation]:
        """待激活队列视图（按 (produced_at,artifact_id) 确定性排序）。"""
        entries = sorted(self._pending.values(), key=lambda e: (e.produced_at, e.artifact_id))
        if status is not None:
            if not isinstance(status, PendingStatus):
                raise ColdPlaneError(f"非法状态: {status!r}")
            entries = [e for e in entries if e.status is status]
        return entries
