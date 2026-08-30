# [BLUEPRINT] MOD-REGIME-014 | docs/03_modules/_domain_regime/style_regime_model/blueprint.md
# [MODULE] zephyr.regime.style_regime_model
# [DOMAIN] D_REGIME
# [DEPENDENCIES] 无（风格序列/规则分档/防抖纯内存；hmm_runner 与参数映射全注入）
# [CONSUMERS] 运行时装配批（风格参数档查找 / MOD-SIG-130 三维矩阵风格轴复用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 风格序列=大小盘收益差+价值成长收益差(等长非空有限); 风格态词表闭合(大盘价值|大盘成长|小盘价值|小盘成长); hmm_runner 未注入降级规则分档(差值正负+幅度阈值，带内未决); HMM 输出标签须词表内且等长; 切换确认=连续N期同向防抖(未决期不破旧态); 参数映射4态必填全; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_regime/style_regime_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StyleRegimeError(占位 ZA-REGIME-UNREGISTERED-STYLE-REGIME)——收益序列非法/幅度阈值或确认期数非法/HMM输出非法/参数映射缺态/全期未决无法确认时抛
# [TESTS] tests/regime/test_style_regime_model.py
# [A_module] module_id=MOD-REGIME-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
StyleRegimeModel — 市场风格体制识别模型（MOD-REGIME-014）。

B10-01447（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-CYCLE-006，A1 模块32）：
**大小盘/价值成长收益差风格序列构建** + **HMM 风格态识别**（注入
hmm_runner；hmmlearn 未装时不引依赖，降级**规则分档**：差值正负 + 幅度
阈值）+ **风格→策略参数映射表**（按风格态输出参数档）+ **风格切换确认**
（连续 N 期同向防抖，未决期不触发切换）。

查重分工（蓝图 §0）：core/regime_detector=HMM 4 态大盘体制概率（本件=
截面风格相对强弱，不产出大盘概率）；regime_cycle_analyzer=体制周期节律
（零交集）；本件风格态/SizeAxis 供 strategy_matrix_3d（MOD-SIG-130）作
风格轴复用。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: state 参数
#   fields: 参数 state，类型注解 StyleState
#   code: style_regime_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① size_axis_of
#   name_en: size_axis_of
#   intro: 风格态 → 大小盘 2 轴映射（确定性）。
#   desc: 风格态 → 大小盘 2 轴映射（确定性）。；源码 L111-L117
#   inputs: state
#   outputs: SizeAxis
# - id: A2
#   name_zh: ② StyleRegimeModel
#   name_en: StyleRegimeModel
#   intro: 市场风格体制识别（HMM 注入 / 规则降级 + 防抖确认，纯内存确定性）。
#   desc: 市场风格体制识别（HMM 注入 / 规则降级 + 防抖确认，纯内存确定性）。；公共方法（定义序）: build_spread_series, identify_raw, confirm, params_for, ana…
#   inputs: param_map hmm_runner magnitude_threshold confirm_periods
#   outputs: 返回值
#   （注：A2 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: SizeAxis
#   name_en: SizeAxis
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（风格参数档查找 / MOD-SIG-130 三维矩阵风格轴复用）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "SizeAxis",
    "StyleParams",
    "StyleReading",
    "StyleRegimeError",
    "StyleRegimeModel",
    "StyleState",
    "size_axis_of",
]


class StyleRegimeError(Exception):
    """风格体制输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-REGIME-UNREGISTERED-STYLE-REGIME。
    """


class StyleState(str, Enum):
    """风格态 4 档（词表闭合：大小盘 × 价值成长）。"""

    LARGE_VALUE = "large_value"  # 大盘价值
    LARGE_GROWTH = "large_growth"  # 大盘成长
    SMALL_VALUE = "small_value"  # 小盘价值
    SMALL_GROWTH = "small_growth"  # 小盘成长


class SizeAxis(str, Enum):
    """大小盘风格 2 轴（三维策略矩阵风格轴复用）。"""

    LARGE = "large"
    SMALL = "small"


def size_axis_of(state: StyleState) -> SizeAxis:
    """风格态 → 大小盘 2 轴映射（确定性）。"""
    if not isinstance(state, StyleState):
        raise StyleRegimeError(f"未知风格态: {state!r}")
    if state in (StyleState.LARGE_VALUE, StyleState.LARGE_GROWTH):
        return SizeAxis.LARGE
    return SizeAxis.SMALL


@dataclass(frozen=True)
class StyleParams:
    """风格→策略参数档（frozen）。"""

    position_pct: float
    focus: str
    rebalance_days: int

    def __post_init__(self) -> None:
        if not math.isfinite(self.position_pct) or not 0.0 <= self.position_pct <= 1.0:
            raise StyleRegimeError(f"参数档仓位越界: {self.position_pct!r}（须 ∈[0,1]）")
        if not self.focus:
            raise StyleRegimeError("参数档 focus 为空")
        if not isinstance(self.rebalance_days, int) or isinstance(self.rebalance_days, bool) or self.rebalance_days < 1:
            raise StyleRegimeError(f"参数档调仓周期非法: {self.rebalance_days!r}（须 ≥1 整数）")


@dataclass(frozen=True)
class StyleReading:
    """风格识别结果（frozen）。

    raw_states 元素为 None 表示该期未决（规则降级下双差值之一落在幅度
    阈值带内）；confirmed_states 为防抖确认序列（与输入等长，前导未决
    期回填首个确认态）。
    """

    size_spread: tuple[float, ...]
    value_spread: tuple[float, ...]
    raw_states: tuple[StyleState | None, ...]
    confirmed_states: tuple[StyleState, ...]
    current: StyleState
    params: StyleParams
    used_hmm: bool


class StyleRegimeModel:
    """市场风格体制识别（HMM 注入 / 规则降级 + 防抖确认，纯内存确定性）。"""

    def __init__(
        self,
        *,
        param_map: Mapping[StyleState, StyleParams],
        hmm_runner: Callable[[tuple[float, ...], tuple[float, ...]], Sequence[str]] | None = None,
        magnitude_threshold: float = 0.005,
        confirm_periods: int = 3,
    ) -> None:
        if not math.isfinite(magnitude_threshold) or magnitude_threshold < 0.0:
            raise StyleRegimeError(f"幅度阈值非法: {magnitude_threshold!r}（须 ≥0 有限）")
        if not isinstance(confirm_periods, int) or isinstance(confirm_periods, bool) or confirm_periods < 1:
            raise StyleRegimeError(f"确认期数非法: {confirm_periods!r}（须 ≥1 整数）")
        missing = [s for s in StyleState if s not in param_map]
        if missing:
            raise StyleRegimeError(f"参数映射缺态: {[s.value for s in missing]}（4 态必填全）")
        for key, params in param_map.items():
            if not isinstance(key, StyleState):
                raise StyleRegimeError(f"参数映射键类型非法: {key!r}")
            if not isinstance(params, StyleParams):
                raise StyleRegimeError(f"参数映射值类型非法: {key!r} -> {type(params).__name__}")
        self._param_map: dict[StyleState, StyleParams] = dict(param_map)
        self._hmm_runner = hmm_runner
        self._magnitude = magnitude_threshold
        self._confirm_periods = confirm_periods

    # ── 风格序列构建 ─────────────────────────────────────────────────────

    @staticmethod
    def build_spread_series(
        lead_returns: Sequence[float],
        lag_returns: Sequence[float],
    ) -> tuple[float, ...]:
        """收益差风格序列：lead − lag 逐期差（等长/非空/有限，Fail-Closed）。"""
        lead = tuple(lead_returns)
        lag = tuple(lag_returns)
        if not lead:
            raise StyleRegimeError("收益序列为空")
        if len(lead) != len(lag):
            raise StyleRegimeError(f"收益序列不等长: {len(lead)} vs {len(lag)}")
        for value in lead + lag:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise StyleRegimeError(f"收益序列含非法值: {value!r}")
        return tuple(a - b for a, b in zip(lead, lag, strict=False))

    # ── 风格态识别（HMM 注入 / 规则降级） ──────────────────────────────────

    def _rule_bucket(self, size_spread: float, value_spread: float) -> StyleState | None:
        """规则分档：差值正负 + 幅度阈值；任一轴落带内 → 未决 None。"""
        if abs(size_spread) <= self._magnitude or abs(value_spread) <= self._magnitude:
            return None
        if size_spread > 0:
            return StyleState.LARGE_VALUE if value_spread > 0 else StyleState.LARGE_GROWTH
        return StyleState.SMALL_VALUE if value_spread > 0 else StyleState.SMALL_GROWTH

    def identify_raw(
        self,
        size_spread: Sequence[float],
        value_spread: Sequence[float],
    ) -> tuple[tuple[StyleState | None, ...], bool]:
        """逐期原始风格态：HMM 注入优先，未注入降级规则分档。

        返回 (原始态序列, 是否走 HMM)；HMM 输出标签非法/不等长 Fail-Closed。
        """
        size = tuple(size_spread)
        value = tuple(value_spread)
        if not size:
            raise StyleRegimeError("风格差值序列为空")
        if len(size) != len(value):
            raise StyleRegimeError(f"风格差值序列不等长: {len(size)} vs {len(value)}")
        for v in size + value:
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
                raise StyleRegimeError(f"风格差值序列含非法值: {v!r}")

        if self._hmm_runner is not None:
            labels = tuple(self._hmm_runner(size, value))
            if len(labels) != len(size):
                raise StyleRegimeError(f"hmm_runner 输出不等长: {len(labels)} vs {len(size)}")
            states: list[StyleState | None] = []
            for label in labels:
                try:
                    states.append(StyleState(label))
                except ValueError:
                    raise StyleRegimeError(f"hmm_runner 输出词表外标签: {label!r}") from None
            _log.debug("HMM 风格态识别: %d 期", len(states))
            return tuple(states), True

        raw = tuple(self._rule_bucket(s, v) for s, v in zip(size, value, strict=False))
        _log.debug("规则降级风格分档: %d 期（未决 %d 期）", len(raw), sum(1 for r in raw if r is None))
        return raw, False

    # ── 切换确认（连续 N 期同向防抖） ──────────────────────────────────────

    def confirm(self, raw_states: Sequence[StyleState | None]) -> tuple[StyleState, ...]:
        """防抖确认：新态须连续 N 期同向才切换；未决期不破旧态。

        前导未决期回填首个确认态（确定性）；全期未决 → Fail-Closed。
        """
        raw = tuple(raw_states)
        if not raw:
            raise StyleRegimeError("原始风格态序列为空")
        for r in raw:
            if r is not None and not isinstance(r, StyleState):
                raise StyleRegimeError(f"原始风格态非法: {r!r}")
        n = self._confirm_periods
        confirmed: list[StyleState | None] = []
        current: StyleState | None = None
        candidate: StyleState | None = None
        streak = 0
        for r in raw:
            if r is None:
                candidate = None  # 未决期中断候选连击，但不破旧态
                streak = 0
            elif current is None:
                current = r
            elif r == current:
                candidate = None
                streak = 0
            else:
                streak = streak + 1 if r == candidate else 1
                candidate = r
                if streak >= n:
                    _log.info("风格切换确认: %s → %s（连续 %d 期）", current.value, r.value, streak)
                    current = r
                    candidate = None
                    streak = 0
            confirmed.append(current)
        if current is None:
            raise StyleRegimeError("全期未决（规则分档全落阈值带内），无法确认风格态")
        # 前导未决期回填首个确认态（确定性）
        first = next(x for x in confirmed if x is not None)
        return tuple(x if x is not None else first for x in confirmed)

    # ── 参数映射查询 ───────────────────────────────────────────────────────

    def params_for(self, state: StyleState) -> StyleParams:
        """风格态 → 策略参数档（未知态 Fail-Closed）。"""
        if not isinstance(state, StyleState):
            raise StyleRegimeError(f"未知风格态: {state!r}")
        params = self._param_map.get(state)
        if params is None:
            raise StyleRegimeError(f"参数映射缺态: {state.value!r}")
        return params

    # ── 一体识别 ──────────────────────────────────────────────────────────

    def analyze(
        self,
        large_returns: Sequence[float],
        small_returns: Sequence[float],
        value_returns: Sequence[float],
        growth_returns: Sequence[float],
    ) -> StyleReading:
        """四组收益 → 风格序列 → 原始态 → 防抖确认 → 当前态参数档。"""
        size_spread = self.build_spread_series(large_returns, small_returns)
        value_spread = self.build_spread_series(value_returns, growth_returns)
        if len(size_spread) != len(value_spread):
            raise StyleRegimeError(f"大小盘与价值成长序列不等长: {len(size_spread)} vs {len(value_spread)}")
        raw, used_hmm = self.identify_raw(size_spread, value_spread)
        confirmed = self.confirm(raw)
        current = confirmed[-1]
        return StyleReading(
            size_spread=size_spread,
            value_spread=value_spread,
            raw_states=raw,
            confirmed_states=confirmed,
            current=current,
            params=self.params_for(current),
            used_hmm=used_hmm,
        )
