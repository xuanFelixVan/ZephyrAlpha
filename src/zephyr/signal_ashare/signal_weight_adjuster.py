# [BLUEPRINT] MOD-SIG-131 | docs/03_modules/_domain_signal/signal_weight_adjuster/blueprint.md
# [MODULE] zephyr.signal_ashare.signal_weight_adjuster
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；时钟/审计回调/告警回调全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 滚动窗口三指标(IC/胜率/回撤)→加权得分∈[0,1]→目标权重∈[min,max]；单次调整限幅(默认±20%相对现行权重)；每次变更版本递增+审计回调；回滚按版本恢复并生成新版本；漂移=目标与现行相对偏差>阈值即告警；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/signal_weight_adjuster/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SignalWeightError(占位 ZA-SIG-UNREGISTERED-SIGNAL-WEIGHT)——未注册信号/重复注册/空signal_id/指标越界/无指标样本/未知版本/非法配置时抛
# [TESTS] tests/signal_ashare/test_signal_weight_adjuster.py
# [A_module] module_id=MOD-SIG-131 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
SignalWeightAdjuster — 信号权重调节器（MOD-SIG-131）。

B11-02593（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-054，A7 技能
signal-weight-adjust）：滚动 IC/胜率/回撤三指标加权得分→目标权重
+ 单次调整限幅（默认 ±20% 相对现行权重）+ 权重变更审计回调
+ 按版本回滚 + 漂移告警（目标与现行相对偏差 > 阈值）。

查重分工：multi_strategy_capital_allocator=资金分配（本件=信号层权重
调节，不分配资金）；strength_ic_weight_calibrator=IC 权重校准（本件=
三指标滚动调节+版本回滚+漂移告警，零交集）。

纯内存/DI设计；外部副作用（OS调用/网络/进程控制）全部经注入回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: signal_weight_adjuster.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: signal_weight_adjuster.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: signal_weight_adjuster.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: signal_weight_adjuster.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SignalWeightAdjuster
#   name_en: SignalWeightAdjuster
#   intro: 信号权重调节器（三指标得分→目标权重+限幅+审计+回滚+漂移告警）。
#   desc: 信号权重调节器（三指标得分→目标权重+限幅+审计+回滚+漂移告警）。；公共方法（定义序）: register_signal, record_metrics, rolling_metrics, score, target…
#   inputs: config clock audit_sink alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: SignalWeightAdjuster
#   downstream: 运行时装配批（统一注入点装配）
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
import math
from dataclasses import dataclass
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "MetricSample",
    "RollingMetrics",
    "SignalWeightAdjuster",
    "SignalWeightConfig",
    "SignalWeightError",
    "WeightChangeRecord",
    "WeightDriftAlert",
]


class SignalWeightError(Exception):
    """信号权重调节协议输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-SIGNAL-WEIGHT。
    """


def _validate_ratio(name: str, value: float, lo: float, hi: float) -> float:
    """校验指标为有限实数且落在 [lo, hi] 区间，越界 Fail-Closed。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SignalWeightError(f"{name} 非数值: {value!r}")
    v = float(value)
    if math.isnan(v) or math.isinf(v):
        raise SignalWeightError(f"{name} 非有限值: {value!r}")
    if not lo <= v <= hi:
        raise SignalWeightError(f"{name} 越界: {value!r}（须∈[{lo},{hi}]）")
    return v


@dataclass(frozen=True)
class SignalWeightConfig:
    """调节器配置（窗口/得分系数/权重上下限/限幅/漂移阈值）。"""

    window: int = 20
    ic_coef: float = 0.4
    win_coef: float = 0.4
    dd_coef: float = 0.2
    min_weight: float = 0.0
    max_weight: float = 1.0
    adjust_cap: float = 0.2
    drift_threshold: float = 0.15

    def __post_init__(self) -> None:
        if isinstance(self.window, bool) or not isinstance(self.window, int) or self.window < 1:
            raise SignalWeightError(f"window 非法: {self.window!r}（须为正整数）")
        for name in ("ic_coef", "win_coef", "dd_coef"):
            _validate_ratio(name, getattr(self, name), 0.0, 1.0e9)
        if self.ic_coef + self.win_coef + self.dd_coef <= 0.0:
            raise SignalWeightError("得分系数之和须为正")
        _validate_ratio("min_weight", self.min_weight, 0.0, 1.0e9)
        _validate_ratio("max_weight", self.max_weight, 0.0, 1.0e9)
        if not self.min_weight < self.max_weight:
            raise SignalWeightError("min_weight 须小于 max_weight")
        _validate_ratio("adjust_cap", self.adjust_cap, 1.0e-12, 1.0)
        _validate_ratio("drift_threshold", self.drift_threshold, 1.0e-12, 1.0e9)


@dataclass(frozen=True)
class MetricSample:
    """单次滚动指标样本（IC/胜率/回撤三要素）。"""

    ic: float
    win_rate: float
    drawdown: float

    def __post_init__(self) -> None:
        _validate_ratio("ic", self.ic, -1.0, 1.0)
        _validate_ratio("win_rate", self.win_rate, 0.0, 1.0)
        _validate_ratio("drawdown", self.drawdown, 0.0, 1.0)


@dataclass(frozen=True)
class RollingMetrics:
    """滚动窗口聚合指标（均值IC/均值胜率/最大回撤）。"""

    mean_ic: float
    mean_win_rate: float
    max_drawdown: float
    samples: int


@dataclass(frozen=True)
class WeightChangeRecord:
    """权重变更审计记录（每次 adjust/rollback 产出）。"""

    signal_id: str
    old_weight: float
    new_weight: float
    target_weight: float
    version: int
    reason: str
    capped: bool
    changed_at: datetime.datetime


@dataclass(frozen=True)
class WeightDriftAlert:
    """漂移告警（目标与现行相对偏差>阈值）。"""

    signal_id: str
    current_weight: float
    target_weight: float
    deviation: float
    threshold: float
    at: datetime.datetime


class SignalWeightAdjuster:
    """信号权重调节器（三指标得分→目标权重+限幅+审计+回滚+漂移告警）。"""

    def __init__(
        self,
        *,
        config: SignalWeightConfig | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[WeightChangeRecord], None] | None = None,
        alert_sink: Callable[[WeightDriftAlert], None] | None = None,
    ) -> None:
        self._cfg = config or SignalWeightConfig()
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._alert_sink = alert_sink
        # signal_id -> {weight, version, samples[list[MetricSample]], history[list[(version, weight)]]}
        self._signals: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # 注册与指标录入
    # ------------------------------------------------------------------
    def register_signal(self, signal_id: str, initial_weight: float) -> None:
        """注册信号并设定初始权重（版本=1）。"""
        if not signal_id or not str(signal_id).strip():
            raise SignalWeightError(f"signal_id 为空: {signal_id!r}")
        if signal_id in self._signals:
            raise SignalWeightError(f"信号已注册: {signal_id!r}")
        w = _validate_ratio("initial_weight", initial_weight, 1.0e-12, 1.0e9)
        self._signals[signal_id] = {
            "weight": w,
            "version": 1,
            "samples": [],
            "history": [(1, w)],
        }
        _log.info("信号注册: %s 初始权重=%.6f", signal_id, w)

    def record_metrics(
        self,
        signal_id: str,
        *,
        ic: float,
        win_rate: float,
        drawdown: float,
    ) -> MetricSample:
        """录入一次滚动指标样本（窗口超出即裁最旧）。"""
        state = self._require(signal_id)
        sample = MetricSample(ic=ic, win_rate=win_rate, drawdown=drawdown)
        samples: list[MetricSample] = state["samples"]
        samples.append(sample)
        del samples[: max(0, len(samples) - self._cfg.window)]
        return sample

    # ------------------------------------------------------------------
    # 得分与目标权重
    # ------------------------------------------------------------------
    def rolling_metrics(self, signal_id: str) -> RollingMetrics:
        """滚动窗口聚合（均值IC/均值胜率/最大回撤）。"""
        state = self._require(signal_id)
        samples: list[MetricSample] = state["samples"]
        if not samples:
            raise SignalWeightError(f"信号无指标样本: {signal_id!r}")
        n = len(samples)
        return RollingMetrics(
            mean_ic=sum(s.ic for s in samples) / n,
            mean_win_rate=sum(s.win_rate for s in samples) / n,
            max_drawdown=max(s.drawdown for s in samples),
            samples=n,
        )

    def score(self, signal_id: str) -> float:
        """三指标加权得分∈[0,1]（IC 线性映射 (-1,1)→(0,1)，回撤反向计分）。"""
        m = self.rolling_metrics(signal_id)
        cfg = self._cfg
        ic_scaled = (m.mean_ic + 1.0) / 2.0
        total = cfg.ic_coef + cfg.win_coef + cfg.dd_coef
        raw = (cfg.ic_coef * ic_scaled + cfg.win_coef * m.mean_win_rate + cfg.dd_coef * (1.0 - m.max_drawdown)) / total
        return min(1.0, max(0.0, raw))

    def target_weight(self, signal_id: str) -> float:
        """目标权重 = min_weight + (max_weight - min_weight) × 得分。"""
        cfg = self._cfg
        return cfg.min_weight + (cfg.max_weight - cfg.min_weight) * self.score(signal_id)

    # ------------------------------------------------------------------
    # 调整 / 回滚 / 漂移
    # ------------------------------------------------------------------
    def adjust(self, signal_id: str, *, reason: str = "") -> WeightChangeRecord:
        """按目标权重调整：单次限幅 adjust_cap×现行权重，版本递增+审计。"""
        state = self._require(signal_id)
        target = self.target_weight(signal_id)
        current = state["weight"]
        delta = target - current
        cap = self._cfg.adjust_cap * current
        applied = min(cap, max(-cap, delta))
        new_weight = max(0.0, current + applied)
        record = self._commit(
            signal_id,
            new_weight=new_weight,
            target=target,
            reason=reason or "adjust",
            capped=applied != delta,
        )
        _log.info(
            "权重调整: %s %.6f→%.6f（目标=%.6f 限幅=%s）",
            signal_id,
            current,
            new_weight,
            target,
            record.capped,
        )
        return record

    def rollback(self, signal_id: str, version: int, *, reason: str = "rollback") -> WeightChangeRecord:
        """按版本回滚：恢复该版本权重并生成新版本（审计留痕）。"""
        state = self._require(signal_id)
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise SignalWeightError(f"回滚版本非法: {version!r}")
        history: list[tuple[int, float]] = state["history"]
        matched = [w for v, w in history if v == version]
        if not matched:
            raise SignalWeightError(f"未知版本: {signal_id!r} v{version!r}")
        record = self._commit(
            signal_id,
            new_weight=matched[0],
            target=matched[0],
            reason=reason,
            capped=False,
        )
        _log.info("权重回滚: %s → v%d（权重=%.6f）", signal_id, version, matched[0])
        return record

    def check_drift(self, signal_id: str | None = None) -> tuple[WeightDriftAlert, ...]:
        """漂移检测：目标与现行相对偏差>阈值即产出告警（无样本信号跳过）。"""
        ids = [signal_id] if signal_id is not None else sorted(self._signals)
        alerts: list[WeightDriftAlert] = []
        for sid in ids:
            state = self._require(sid)
            if not state["samples"]:
                continue
            target = self.target_weight(sid)
            current = state["weight"]
            deviation = abs(target - current) / current
            if deviation > self._cfg.drift_threshold:
                alert = WeightDriftAlert(
                    signal_id=sid,
                    current_weight=current,
                    target_weight=target,
                    deviation=deviation,
                    threshold=self._cfg.drift_threshold,
                    at=self._clock(),
                )
                alerts.append(alert)
                if self._alert_sink is not None:
                    self._alert_sink(alert)
                _log.warning(
                    "权重漂移告警: %s 现行=%.6f 目标=%.6f 偏差=%.4f>%.4f",
                    sid,
                    current,
                    target,
                    deviation,
                    self._cfg.drift_threshold,
                )
        return tuple(alerts)

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    def current_weight(self, signal_id: str) -> float:
        """现行权重。"""
        return self._require(signal_id)["weight"]

    def version_of(self, signal_id: str) -> int:
        """现行版本号。"""
        return self._require(signal_id)["version"]

    def history(self, signal_id: str) -> tuple[tuple[int, float], ...]:
        """版本历史（(版本, 权重) 升序）。"""
        return tuple(self._require(signal_id)["history"])

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------
    def _require(self, signal_id: str) -> dict:
        if signal_id not in self._signals:
            raise SignalWeightError(f"信号未注册: {signal_id!r}")
        return self._signals[signal_id]

    def _commit(
        self,
        signal_id: str,
        *,
        new_weight: float,
        target: float,
        reason: str,
        capped: bool,
    ) -> WeightChangeRecord:
        state = self._signals[signal_id]
        old_weight = state["weight"]
        state["version"] += 1
        state["weight"] = new_weight
        state["history"].append((state["version"], new_weight))
        record = WeightChangeRecord(
            signal_id=signal_id,
            old_weight=old_weight,
            new_weight=new_weight,
            target_weight=target,
            version=state["version"],
            reason=reason,
            capped=capped,
            changed_at=self._clock(),
        )
        if self._audit_sink is not None:
            self._audit_sink(record)
        return record
