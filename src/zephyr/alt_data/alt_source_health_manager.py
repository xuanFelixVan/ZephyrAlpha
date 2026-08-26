# [BLUEPRINT] MOD-ALT-011 | docs/03_modules/_domain_alt_data/alt_source_health_manager/blueprint.md
# [MODULE] zephyr.alt_data.alt_source_health_manager
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] 无（协议核心纯内存；时钟/告警回调全注入）
# [CONSUMERS] 运行时装配批（另类数据连接器族健康面上报 / failover 切换决策输入 / 质量事件接 alert 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 评分核心纯内存无IO；成功率/新鲜度/延迟三分量权重和恒=1.0；健康分恒∈[0,1]；降级阶梯 NORMAL→DOWNWEIGHTED→FAILOVER→DISABLED 单次评估至多降一级；恢复仅经半开试探（HALF_OPEN 连续成功达标回 NORMAL，失败回退原态）；状态迁移必告警留痕；滑动窗口定长淘汰最旧样本；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/alt_source_health_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AltSourceHealthError(占位 ZA-ALT-UNREGISTERED-SOURCE-HEALTH)——权重和非法/阈值乱序/窗口非正/未知source/空source_id/负延迟/未来数据/空窗口评分/非法状态探测或评估时抛
# [TESTS] tests/alt_data/test_alt_source_health_manager.py
# [A_module] module_id=MOD-ALT-011 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AltSourceHealthManager — 另类数据源健康度管理器（MOD-ALT-011）。

B14-04617（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-TESTA-019，A9
D-ALT-DATA-31）：另类数据源健康度——成功率/新鲜度/延迟**滑动窗口评分**
（三分量权重可配，权重和恒 1.0）+ 自动**降级阶梯**状态机（正常→降权→
切源→标记停用，单次评估至多降一级）+ **恢复探测**（半开试探：连续成功
达标回正常，失败回退原态）+ 质量事件接**告警回调**。

查重分工（蓝图 §0）：market_data/failover/manager=行情主备源切换执行器
（本件=另类数据源健康度判定面，不执行切换，仅输出状态与告警）；本件不做
采集（采集在 alt_data_connector 族），仅消费样本做评分与阶梯裁决。
"""

from __future__ import annotations

import datetime
import logging
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "AltSourceHealthError",
    "AltSourceHealthManager",
    "HealthAlert",
    "HealthReport",
    "HealthState",
]

#: 降级阶梯序号（0 最优，3 最差；HALF_OPEN 为恢复试探过渡态不入阶梯）
_LADDER_RANK: Final[dict["HealthState", int]] = {}

_WEIGHT_KEYS: Final = ("success", "freshness", "latency")


class AltSourceHealthError(Exception):
    """健康度管理输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ALT-UNREGISTERED-SOURCE-HEALTH。
    """


class HealthState(str, Enum):
    """数据源健康状态机（降级阶梯 + 半开试探）。"""

    NORMAL = "normal"                # 正常
    DOWNWEIGHTED = "downweighted"    # 降权
    FAILOVER = "failover"            # 切源
    DISABLED = "disabled"            # 停用
    HALF_OPEN = "half_open"          # 半开试探（恢复过渡态）


_LADDER_RANK.update({
    HealthState.NORMAL: 0,
    HealthState.DOWNWEIGHTED: 1,
    HealthState.FAILOVER: 2,
    HealthState.DISABLED: 3,
})


@dataclass(frozen=True)
class HealthReport:
    """单次健康评估报告（frozen）。"""

    source_id: str
    state: HealthState
    score: float
    success_rate: float
    freshness: float
    latency_score: float
    evaluated_at: datetime.datetime


@dataclass(frozen=True)
class HealthAlert:
    """状态迁移告警载荷（frozen）。"""

    source_id: str
    from_state: HealthState
    to_state: HealthState
    score: float
    reason: str
    raised_at: datetime.datetime


class AltSourceHealthManager:
    """另类数据源健康度管理器（滑动窗口评分 + 降级阶梯 + 半开恢复）。"""

    def __init__(
        self,
        *,
        source_ids: Sequence[str],
        weights: Mapping[str, float] | None = None,
        window_size: int = 20,
        downweight_threshold: float = 0.8,
        failover_threshold: float = 0.5,
        disable_threshold: float = 0.2,
        max_staleness_seconds: float = 3600.0,
        max_latency_seconds: float = 10.0,
        probe_successes_needed: int = 2,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[HealthAlert], None] | None = None,
    ) -> None:
        if not source_ids:
            raise AltSourceHealthError("source_ids 为空（无健康度管理对象）")
        seen: set[str] = set()
        for sid in source_ids:
            if not sid or not sid.strip():
                raise AltSourceHealthError("source_id 空白")
            if sid in seen:
                raise AltSourceHealthError(f"source_id 重复: {sid!r}")
            seen.add(sid)

        w = dict(weights) if weights is not None else {
            "success": 0.5,
            "freshness": 0.3,
            "latency": 0.2,
        }
        if set(w) != set(_WEIGHT_KEYS):
            raise AltSourceHealthError(f"权重键须为 {_WEIGHT_KEYS}: {sorted(w)!r}")
        for key, val in w.items():
            if not 0.0 <= val <= 1.0:
                raise AltSourceHealthError(f"权重越界: {key}={val!r}（须∈[0,1]）")
        if abs(sum(w.values()) - 1.0) > 1e-9:
            raise AltSourceHealthError(f"权重和须=1.0: {sum(w.values())!r}")

        if window_size <= 0:
            raise AltSourceHealthError(f"window_size 非正: {window_size!r}")
        if not 0.0 < disable_threshold < failover_threshold < downweight_threshold < 1.0:
            raise AltSourceHealthError(
                "阈值须满足 0<disable<failover<downweight<1: "
                f"{disable_threshold!r}/{failover_threshold!r}/{downweight_threshold!r}"
            )
        if max_staleness_seconds <= 0:
            raise AltSourceHealthError(f"max_staleness_seconds 非正: {max_staleness_seconds!r}")
        if max_latency_seconds <= 0:
            raise AltSourceHealthError(f"max_latency_seconds 非正: {max_latency_seconds!r}")
        if probe_successes_needed <= 0:
            raise AltSourceHealthError(f"probe_successes_needed 非正: {probe_successes_needed!r}")

        self._weights = w
        self._window_size = window_size
        self._downweight_threshold = downweight_threshold
        self._failover_threshold = failover_threshold
        self._disable_threshold = disable_threshold
        self._max_staleness = max_staleness_seconds
        self._max_latency = max_latency_seconds
        self._probe_needed = probe_successes_needed
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink

        self._states: dict[str, HealthState] = {sid: HealthState.NORMAL for sid in seen}
        self._windows: dict[str, deque] = {sid: deque(maxlen=window_size) for sid in seen}
        self._last_score: dict[str, float] = {sid: 1.0 for sid in seen}
        self._probe_origin: dict[str, HealthState] = {}
        self._probe_streak: dict[str, int] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _known(self, source_id: str) -> None:
        if source_id not in self._states:
            raise AltSourceHealthError(f"未知数据源: {source_id!r}（未登记）")

    def _alert(self, source_id: str, from_state: HealthState, to_state: HealthState, reason: str) -> None:
        alert = HealthAlert(
            source_id=source_id,
            from_state=from_state,
            to_state=to_state,
            score=self._last_score[source_id],
            reason=reason,
            raised_at=self._clock(),
        )
        _log.warning("数据源健康状态迁移: %s %s -> %s (%s)", source_id, from_state.value, to_state.value, reason)
        if self._alert_sink is not None:
            try:
                self._alert_sink(alert)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _score(self, source_id: str) -> tuple[float, float, float, float]:
        """滑动窗口三分量评分（空窗口 Fail-Closed）。"""
        window = self._windows[source_id]
        if not window:
            raise AltSourceHealthError(f"数据源 {source_id!r} 无样本（空窗口不可评分）")
        now = self._clock()
        success_rate = sum(1 for ok, _, _ in window if ok) / len(window)
        newest_data_ts = max(data_ts for _, _, data_ts in window)
        age = (now - newest_data_ts).total_seconds()
        freshness = max(0.0, 1.0 - age / self._max_staleness)
        avg_latency = sum(lat for _, lat, _ in window) / len(window)
        latency_score = max(0.0, 1.0 - avg_latency / self._max_latency)
        score = (
            self._weights["success"] * success_rate
            + self._weights["freshness"] * freshness
            + self._weights["latency"] * latency_score
        )
        score = min(1.0, max(0.0, score))
        return score, success_rate, freshness, latency_score

    def _target_rank(self, score: float) -> int:
        if score >= self._downweight_threshold:
            return _LADDER_RANK[HealthState.NORMAL]
        if score >= self._failover_threshold:
            return _LADDER_RANK[HealthState.DOWNWEIGHTED]
        if score >= self._disable_threshold:
            return _LADDER_RANK[HealthState.FAILOVER]
        return _LADDER_RANK[HealthState.DISABLED]

    # ── 样本登记 ──────────────────────────────────────────────────────────

    def record_sample(
        self,
        source_id: str,
        *,
        success: bool,
        latency_seconds: float,
        data_ts: datetime.datetime,
    ) -> None:
        """登记一次采集样本（成功率/延迟/数据时间戳三要素入滑动窗口）。"""
        self._known(source_id)
        if latency_seconds < 0:
            raise AltSourceHealthError(f"latency_seconds 为负: {latency_seconds!r}")
        if data_ts > self._clock():
            raise AltSourceHealthError(f"data_ts 晚于当前时钟（未来数据）: {data_ts!r}")
        self._windows[source_id].append((bool(success), float(latency_seconds), data_ts))

    # ── 评估（降级阶梯） ───────────────────────────────────────────────────

    def evaluate(self, source_id: str) -> HealthReport:
        """评估：滑动窗口评分 → 降级阶梯（单次至多降一级；恢复仅经探测）。"""
        self._known(source_id)
        state = self._states[source_id]
        if state is HealthState.HALF_OPEN:
            raise AltSourceHealthError(f"数据源 {source_id!r} 半开试探中，禁止评估")
        score, success_rate, freshness, latency_score = self._score(source_id)
        self._last_score[source_id] = score

        target = self._target_rank(score)
        current = _LADDER_RANK[state]
        if target > current:
            new_rank = current + 1  # 阶梯：单次评估至多降一级
            new_state = next(s for s, r in _LADDER_RANK.items() if r == new_rank)
            reason = f"健康分 {score:.4f} 触发降级: {state.value} -> {new_state.value}"
            self._states[source_id] = new_state
            self._alert(source_id, state, new_state, reason)
            state = new_state
        return HealthReport(
            source_id=source_id,
            state=state,
            score=score,
            success_rate=success_rate,
            freshness=freshness,
            latency_score=latency_score,
            evaluated_at=self._clock(),
        )

    # ── 恢复探测（半开试探） ────────────────────────────────────────────────

    def probe(self, source_id: str, *, success: bool) -> HealthState:
        """半开试探：非 NORMAL 态可发起；连续成功达标回 NORMAL，失败回退原态。"""
        self._known(source_id)
        state = self._states[source_id]
        if state is HealthState.NORMAL:
            raise AltSourceHealthError(f"数据源 {source_id!r} 处于 NORMAL，无需恢复探测")

        if state is not HealthState.HALF_OPEN:
            self._probe_origin[source_id] = state
            self._probe_streak[source_id] = 0
            self._states[source_id] = HealthState.HALF_OPEN
            self._alert(source_id, state, HealthState.HALF_OPEN, "发起半开恢复试探")

        if success:
            self._probe_streak[source_id] += 1
            if self._probe_streak[source_id] >= self._probe_needed:
                origin = self._probe_origin.pop(source_id)
                self._probe_streak.pop(source_id)
                self._states[source_id] = HealthState.NORMAL
                self._alert(
                    source_id, HealthState.HALF_OPEN, HealthState.NORMAL,
                    f"半开试探连续 {self._probe_needed} 次成功（原态 {origin.value}），恢复健康",
                )
        else:
            origin = self._probe_origin.pop(source_id)
            self._probe_streak.pop(source_id)
            self._states[source_id] = origin
            self._alert(source_id, HealthState.HALF_OPEN, origin, "半开试探失败，回退原态")
        return self._states[source_id]

    # ── 查询 ─────────────────────────────────────────────────────────────

    def state_of(self, source_id: str) -> HealthState:
        """当前状态查询（未知数据源 → Fail-Closed）。"""
        self._known(source_id)
        return self._states[source_id]

    def health_of(self, source_id: str) -> HealthReport:
        """当前窗口评分快照（不触发状态迁移；空窗口 → Fail-Closed）。"""
        self._known(source_id)
        state = self._states[source_id]
        score, success_rate, freshness, latency_score = self._score(source_id)
        return HealthReport(
            source_id=source_id,
            state=state,
            score=score,
            success_rate=success_rate,
            freshness=freshness,
            latency_score=latency_score,
            evaluated_at=self._clock(),
        )

    def score_of(self, source_id: str) -> float:
        """当前窗口健康分（空窗口 → Fail-Closed）。"""
        return self.health_of(source_id).score

    def sources(self) -> tuple[str, ...]:
        """已登记数据源清单（确定性排序）。"""
        return tuple(sorted(self._states))
