# [BLUEPRINT] MOD-SIG-129 | docs/03_modules/_domain_signal/volume_regime_adaptive/blueprint.md
# [MODULE] zephyr.signal_ashare.volume_regime_adaptive
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（量能分类/查找表纯内存；策略参数与历史量序列全注入）
# [CONSUMERS] 运行时装配批（量能×体制策略参数查找 / MOD-SIG-130 三维矩阵轴复用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 量比=vol/MA20(MA20>0); 量能三态词表闭合(缩量<0.7|平量[0.7,1.3]|放量>1.3，边界归平量); 分位=100×历史≤当前量占比(注入历史); 极端分位护栏(≤5%或≥95%触发仓位减半effective); 策略矩阵3×3=9格构造期必填全; 格值仓位∈[0,1]方向词表闭合(long|flat|short); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/volume_regime_adaptive/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] VolumeRegimeError(占位 ZA-SIG-UNREGISTERED-VOLUME-REGIME)——量/均量非有限或越界/历史序列空或含非法值/阈值配置非法/矩阵缺格或多格/格值非法/未知体制或量能态类型时抛
# [TESTS] tests/signal_ashare/test_volume_regime_adaptive.py
# [A_module] module_id=MOD-SIG-129 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""VolumeRegimeAdaptive — 量能体制自适应策略（MOD-SIG-129）。

B10-01445（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-045，A1 模块23）：
**量能三态**（vol/MA20：缩量 <0.7 / 平量 0.7-1.3 / 放量 >1.3，极端分位
≤5% 或 ≥95% 标记）+ **量能×体制 3×3 策略矩阵查找表**（趋势/均值回归/
混沌 × 三态，参数由回测填参注入）+ **查找表查询接口** + **极端分位护栏**
（极端量下仓位减半生效，原格值保留可查）。

查重分工（蓝图 §0）：sector_volume_anomaly=板块成交额五档偏离标签（观测
层，本件=单标的三态+策略参数查找）；intraday_volume_orderflow=日内量能
结构/订单流（本件=日频 vol/MA20 体制适配）；strategy_matrix_3d（MOD-SIG-
130）=本件三态与体制轴的三维扩展消费方，轴枚举在此定义供其复用。
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AdaptiveDecision",
    "DIRECTIONS",
    "MarketRegime",
    "StrategyParams",
    "VolumeRegimeAdaptive",
    "VolumeRegimeError",
    "VolumeSignal",
    "VolumeState",
]

#: 选股方向词表（闭合）
DIRECTIONS: Final[frozenset[str]] = frozenset({"long", "flat", "short"})


class VolumeRegimeError(Exception):
    """量能体制输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-VOLUME-REGIME。
    """


class VolumeState(str, Enum):
    """量能三态（词表闭合）。"""

    SHRINK = "shrink"  # 缩量：量比 < 缩量阈值
    FLAT = "flat"      # 平量：量比 ∈ [缩量阈值, 放量阈值]
    SPIKE = "spike"    # 放量：量比 > 放量阈值


class MarketRegime(str, Enum):
    """市场体制三态（词表闭合，三维矩阵体制轴复用）。"""

    TREND = "trend"                          # 趋势
    MEAN_REVERSION = "mean_reversion"        # 均值回归
    CHOPPY = "choppy"                        # 混沌


@dataclass(frozen=True)
class VolumeSignal:
    """量能分类结果（frozen）。

    percentile=None 表示未注入历史序列（无分位语义）；is_extreme 仅在
    percentile 注入且越出极端护栏阈值时为 True。
    """

    ratio: float
    state: VolumeState
    percentile: float | None
    is_extreme: bool


@dataclass(frozen=True)
class StrategyParams:
    """策略矩阵格值（仓位/方向，frozen）。"""

    position_pct: float
    direction: str
    note: str = ""

    def __post_init__(self) -> None:
        if not math.isfinite(self.position_pct) or not 0.0 <= self.position_pct <= 1.0:
            raise VolumeRegimeError(f"格值仓位越界: {self.position_pct!r}（须 ∈[0,1]）")
        if self.direction not in DIRECTIONS:
            raise VolumeRegimeError(f"格值方向非法: {self.direction!r}（词表闭合 long|flat|short）")


@dataclass(frozen=True)
class AdaptiveDecision:
    """自适应查询结果：原始格值 + 护栏后生效参数（frozen）。"""

    signal: VolumeSignal
    params: StrategyParams
    effective_params: StrategyParams
    guarded: bool


class VolumeRegimeAdaptive:
    """量能三态分类 + 量能×体制 3×3 策略矩阵查找（纯内存确定性）。"""

    def __init__(
        self,
        *,
        strategy_matrix: Mapping[tuple[MarketRegime, VolumeState], StrategyParams],
        shrink_threshold: float = 0.7,
        spike_threshold: float = 1.3,
        extreme_low_pct: float = 5.0,
        extreme_high_pct: float = 95.0,
    ) -> None:
        if not math.isfinite(shrink_threshold) or not math.isfinite(spike_threshold):
            raise VolumeRegimeError("量能阈值须为有限数")
        if not 0.0 < shrink_threshold < spike_threshold:
            raise VolumeRegimeError(
                f"阈值配置非法: shrink={shrink_threshold!r} spike={spike_threshold!r}（须 0<缩量<放量）"
            )
        if not (0.0 <= extreme_low_pct < extreme_high_pct <= 100.0):
            raise VolumeRegimeError(
                f"极端分位护栏非法: low={extreme_low_pct!r} high={extreme_high_pct!r}（须 0≤low<high≤100）"
            )
        expected = {(r, s) for r in MarketRegime for s in VolumeState}
        for key in strategy_matrix.keys():
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or not isinstance(key[0], MarketRegime)
                or not isinstance(key[1], VolumeState)
            ):
                raise VolumeRegimeError(f"策略矩阵键非法: {key!r}（须 (MarketRegime, VolumeState)）")
        given = set(strategy_matrix.keys())
        missing = expected - given
        extra = given - expected
        if missing:
            raise VolumeRegimeError(f"策略矩阵缺格: {sorted(str(k) for k in missing)}")
        if extra:
            raise VolumeRegimeError(f"策略矩阵多格（键须为 (MarketRegime, VolumeState)）: {sorted(str(k) for k in extra)}")
        for key, cell in strategy_matrix.items():
            if not isinstance(cell, StrategyParams):
                raise VolumeRegimeError(f"格值类型非法: {key!r} -> {type(cell).__name__}")
        self._matrix: dict[tuple[MarketRegime, VolumeState], StrategyParams] = dict(strategy_matrix)
        self._shrink = shrink_threshold
        self._spike = spike_threshold
        self._extreme_low = extreme_low_pct
        self._extreme_high = extreme_high_pct

    # ── 量能分类 ─────────────────────────────────────────────────────────

    @staticmethod
    def _check_volume(value: float, name: str) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise VolumeRegimeError(f"{name} 须为有限数值: {value!r}")
        if value < 0.0:
            raise VolumeRegimeError(f"{name} 不得为负: {value!r}")

    def classify(
        self,
        volume: float,
        ma20_volume: float,
        volume_history: Sequence[float] | None = None,
    ) -> VolumeSignal:
        """量比三态分类 + 可选极端分位标记（边界归平量）。"""
        self._check_volume(volume, "volume")
        self._check_volume(ma20_volume, "ma20_volume")
        if ma20_volume <= 0.0:
            raise VolumeRegimeError(f"ma20_volume 须 >0: {ma20_volume!r}")
        ratio = volume / ma20_volume
        if ratio < self._shrink:
            state = VolumeState.SHRINK
        elif ratio > self._spike:
            state = VolumeState.SPIKE
        else:
            state = VolumeState.FLAT

        percentile: float | None = None
        is_extreme = False
        if volume_history is not None:
            history = tuple(volume_history)
            if not history:
                raise VolumeRegimeError("volume_history 为空（无分位语义）")
            for h in history:
                self._check_volume(h, "volume_history 元素")
            below = sum(1 for h in history if h <= volume)
            percentile = 100.0 * below / len(history)
            is_extreme = percentile <= self._extreme_low or percentile >= self._extreme_high
        return VolumeSignal(ratio=ratio, state=state, percentile=percentile, is_extreme=is_extreme)

    # ── 查找表查询 ────────────────────────────────────────────────────────

    def query(self, regime: MarketRegime, state: VolumeState) -> StrategyParams:
        """（体制 × 量能态）→ 策略参数格值（类型非法 Fail-Closed）。"""
        if not isinstance(regime, MarketRegime):
            raise VolumeRegimeError(f"未知体制: {regime!r}")
        if not isinstance(state, VolumeState):
            raise VolumeRegimeError(f"未知量能态: {state!r}")
        return self._matrix[(regime, state)]

    def adapt(
        self,
        regime: MarketRegime,
        volume: float,
        ma20_volume: float,
        volume_history: Sequence[float] | None = None,
    ) -> AdaptiveDecision:
        """分类 + 查询一体：极端分位触发护栏（仓位减半生效，原格值保留）。"""
        signal = self.classify(volume, ma20_volume, volume_history)
        params = self.query(regime, signal.state)
        guarded = signal.is_extreme
        effective = params
        if guarded:
            effective = StrategyParams(
                position_pct=params.position_pct / 2.0,
                direction=params.direction,
                note=(params.note + " | 极端分位护栏：仓位减半").strip(" |"),
            )
            _log.warning(
                "极端量能分位护栏触发: regime=%s state=%s percentile=%.1f 仓位 %.2f→%.2f",
                regime.value, signal.state.value, signal.percentile or 0.0,
                params.position_pct, effective.position_pct,
            )
        _log.debug(
            "量能自适应: regime=%s ratio=%.3f state=%s extreme=%s",
            regime.value, signal.ratio, signal.state.value, guarded,
        )
        return AdaptiveDecision(signal=signal, params=params, effective_params=effective, guarded=guarded)
