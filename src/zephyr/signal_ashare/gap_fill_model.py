# [BLUEPRINT] MOD-SIG-092 | docs/03_modules/_domain_signal/gap_fill_model/blueprint.md
# [MODULE] zephyr.signal_ashare.gap_fill_model
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas（ATR14 由 D_FACTOR 注入，本模块不 import 指标实现）
# [CONSUMERS] （候选：精筛/买入侧信号装配层、T0 日内套利 MOD-SIG-090 缺口情景）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 缺口分级四档封闭集（Tiny/Small/Medium/Large）；分级阈值严格递增；回补概率∈[0,1]；部分回补分布每档归一（∑=1）；MAE 止损参考方向=缺口 fade 方向逆向；frozen dataclass asdict JSON 可序列化；纯统计查表不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01359 行 + 候选注册表 CAND-TESTB-007
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法方向/负缺口/非正价格/非正 ATR/缺列/概率越界/分布不归一/阈值非递增 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_gap_fill_model.py
# [A_module] module_id=MOD-SIG-092 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""缺口回补概率模型（MOD-SIG-092，B10-01359）。

场内无 gap_fill 实现（深挖对账：grep 仅命中 governance gap_analyzer 等无关项），
本模块按缺口统计查表法纯统计落地，无重库依赖：

    Gap Size = (Open − Close_prev) / ATR_14  （ATR 标准化，波动率自适应）

- **四档分级**：Tiny<0.3x / Small<0.6x / Medium<1.2x / Large≥1.2x（封闭集，边界归上档）。
- **回补概率查表**：默认 Tiny=77.8% / Large=8.2%（trading literature 口径），
  Small/Medium 默认线性内插，全部可配置（GapFillConfig）。
- **部分回补分布**：25/50/75/100% 四档概率（每档归一），期望回补比例派生。
- **回补时间分布**：expected_fill_bars 每档默认 1/2/5/20 根，可配置。
- **MAE 止损参考**：缺口 fade 交易的逆向不利 excursion 参考价
  （up 缺口止损在 open 上方 mae_frac×|gap|，down 缺口镜像）。

ATR14 由 D_FACTOR 注入（与 MOD-RK atr_stop_engine "ATR14 注入" 先例一致），
本模块不 import 指标实现、不直连 DB、不荐股。

依据: AUD-DRAFT-001 深挖批 B10-01359（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-092
Version: 0.1.0

# [ALGO_FLOW]
# 输入: OHLC DataFrame + ATR14 序列（D_FACTOR 注入）/ 单缺口标量组
# 特征: 标准化缺口 |Open−Close_prev|/ATR14 + 方向 + 当日 high/low 回补标记
# 算法: 分级（阈值封闭集）→ 查表（回补概率/部分回补分布/时间分布/MAE 系数）
# 输出: GapFillForecast（grade/fill_probability/partial_fill_distribution/
#       expected_fill_fraction/expected_fill_bars/mae_stop_price）+ detect 事件表
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Final

import pandas as pd

logger = logging.getLogger(__name__)

__all__: Final = [
    "GapDirection",
    "GapFillConfig",
    "GapFillForecast",
    "GapFillProbabilityModel",
    "GapGrade",
    "GapFillModel",  # scaffold 注册别名（__init__ export 契约）
]

_FILL_LEVELS: Final = (0.25, 0.5, 0.75, 1.0)
_OHLC_COLUMNS: Final = ("open", "high", "low", "close")
_DIST_TOLERANCE: Final = 1e-6


class GapGrade(str, Enum):
    """缺口标准化分级（封闭集，|gap|/ATR14）。"""

    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class GapDirection(str, Enum):
    """缺口方向（open 相对 prev_close）。"""

    UP = "up"
    DOWN = "down"


def _default_fill_probability() -> dict[str, float]:
    # trading literature 口径：Tiny=77.8% / Large=8.2%，中间档线性内插（可配置）
    return {
        GapGrade.TINY.value: 0.778,
        GapGrade.SMALL.value: 0.55,
        GapGrade.MEDIUM.value: 0.30,
        GapGrade.LARGE.value: 0.082,
    }


def _default_partial_fill_distribution() -> dict[str, dict[float, float]]:
    # 每档 25/50/75/100% 部分回补概率（归一）；小缺口倾向全回补，大缺口倾向浅回补
    return {
        GapGrade.TINY.value: {0.25: 0.05, 0.5: 0.10, 0.75: 0.15, 1.0: 0.70},
        GapGrade.SMALL.value: {0.25: 0.10, 0.5: 0.20, 0.75: 0.25, 1.0: 0.45},
        GapGrade.MEDIUM.value: {0.25: 0.20, 0.5: 0.30, 0.75: 0.30, 1.0: 0.20},
        GapGrade.LARGE.value: {0.25: 0.40, 0.5: 0.30, 0.75: 0.20, 1.0: 0.10},
    }


def _default_mae_fraction() -> dict[str, float]:
    # fade 交易的逆向不利 excursion 系数（×|gap|）：大缺口 fade 需更宽止损
    return {
        GapGrade.TINY.value: 0.5,
        GapGrade.SMALL.value: 0.75,
        GapGrade.MEDIUM.value: 1.0,
        GapGrade.LARGE.value: 1.5,
    }


def _default_expected_fill_bars() -> dict[str, int]:
    return {
        GapGrade.TINY.value: 1,
        GapGrade.SMALL.value: 2,
        GapGrade.MEDIUM.value: 5,
        GapGrade.LARGE.value: 20,
    }


@dataclass(frozen=True)
class GapFillConfig:
    """查表配置（全部可覆盖；构造即校验，fail-closed）。"""

    tiny_max: float = 0.3
    small_max: float = 0.6
    medium_max: float = 1.2
    fill_probability: dict[str, float] = field(default_factory=_default_fill_probability)
    partial_fill_distribution: dict[str, dict[float, float]] = field(default_factory=_default_partial_fill_distribution)
    mae_fraction: dict[str, float] = field(default_factory=_default_mae_fraction)
    expected_fill_bars: dict[str, int] = field(default_factory=_default_expected_fill_bars)

    def __post_init__(self) -> None:
        if not (0.0 < self.tiny_max < self.small_max < self.medium_max):
            msg = (
                f"分级阈值须严格递增且为正: tiny_max={self.tiny_max} "
                f"small_max={self.small_max} medium_max={self.medium_max}"
            )
            raise ValueError(msg)
        grades = {g.value for g in GapGrade}
        for name, table, check in (
            ("fill_probability", self.fill_probability, lambda v: 0.0 <= v <= 1.0),
            ("mae_fraction", self.mae_fraction, lambda v: v > 0.0),
            ("expected_fill_bars", self.expected_fill_bars, lambda v: v >= 1),
        ):
            if set(table) != grades:
                msg = f"{name} 键集须为四档封闭集，实得 {sorted(table)}"
                raise ValueError(msg)
            for grade, value in table.items():
                if not check(value):
                    msg = f"{name}[{grade}]={value} 越界"
                    raise ValueError(msg)
        if set(self.partial_fill_distribution) != grades:
            msg = "partial_fill_distribution 键集须为四档封闭集"
            raise ValueError(msg)
        for grade, dist in self.partial_fill_distribution.items():
            if set(dist) != set(_FILL_LEVELS):
                msg = f"partial_fill_distribution[{grade}] 档位须为 {_FILL_LEVELS}"
                raise ValueError(msg)
            if any(p < 0.0 for p in dist.values()):
                msg = f"partial_fill_distribution[{grade}] 含负概率"
                raise ValueError(msg)
            total = sum(dist.values())
            if abs(total - 1.0) > _DIST_TOLERANCE:
                msg = f"partial_fill_distribution[{grade}] 未归一（∑={total}）"
                raise ValueError(msg)


@dataclass(frozen=True)
class GapFillForecast:
    """单缺口回补预测输出。"""

    direction: str
    grade: str
    gap_size_atr: float
    prev_close: float
    open_price: float
    fill_probability: float
    partial_fill_distribution: dict[float, float]
    expected_fill_fraction: float
    expected_fill_bars: int
    mae_stop_price: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GapFillProbabilityModel:
    """缺口回补概率查表模型（纯统计，无状态）。"""

    def __init__(self, config: GapFillConfig | None = None) -> None:
        self._config = config if config is not None else GapFillConfig()

    @property
    def config(self) -> GapFillConfig:
        return self._config

    def classify(self, gap_size_atr: float) -> GapGrade:
        """按 |gap|/ATR14 标准化幅度分级（边界归上档）。"""
        size = float(gap_size_atr)
        if size < 0.0:
            msg = f"gap_size_atr 须取绝对值（非负），实得 {size}"
            raise ValueError(msg)
        cfg = self._config
        if size < cfg.tiny_max:
            return GapGrade.TINY
        if size < cfg.small_max:
            return GapGrade.SMALL
        if size < cfg.medium_max:
            return GapGrade.MEDIUM
        return GapGrade.LARGE

    def forecast(
        self,
        *,
        direction: str,
        gap_size_atr: float,
        prev_close: float,
        open_price: float,
    ) -> GapFillForecast:
        """单缺口查表预测：回补概率 + 部分回补分布 + 时间分布 + MAE 止损参考。"""
        if direction not in (GapDirection.UP.value, GapDirection.DOWN.value):
            msg = f"非法缺口方向: {direction!r}（须为 'up'/'down'）"
            raise ValueError(msg)
        size = float(gap_size_atr)
        if size < 0.0:
            msg = f"gap_size_atr 须非负，实得 {size}"
            raise ValueError(msg)
        if prev_close <= 0.0:
            msg = f"prev_close 须为正，实得 {prev_close}"
            raise ValueError(msg)
        if open_price <= 0.0:
            msg = f"open_price 须为正，实得 {open_price}"
            raise ValueError(msg)

        grade = self.classify(size)
        cfg = self._config
        dist = dict(cfg.partial_fill_distribution[grade.value])
        expected_fraction = sum(level * prob for level, prob in dist.items())
        gap_price = abs(open_price - prev_close)
        mae_distance = cfg.mae_fraction[grade.value] * gap_price
        # fade 方向逆向：up 缺口 fade=做空，止损在 open 上方；down 缺口镜像
        sign = 1.0 if direction == GapDirection.UP.value else -1.0
        mae_stop_price = open_price + sign * mae_distance
        return GapFillForecast(
            direction=direction,
            grade=grade.value,
            gap_size_atr=size,
            prev_close=float(prev_close),
            open_price=float(open_price),
            fill_probability=cfg.fill_probability[grade.value],
            partial_fill_distribution=dist,
            expected_fill_fraction=expected_fraction,
            expected_fill_bars=cfg.expected_fill_bars[grade.value],
            mae_stop_price=mae_stop_price,
        )

    def detect(
        self,
        ohlc: pd.DataFrame,
        atr14: pd.Series,
        *,
        min_gap_atr: float = 0.1,
    ) -> pd.DataFrame:
        """从 OHLC + ATR14 序列识别缺口事件（PIT：仅用 prev_close，无未来信息）。

        Parameters
        ----------
        ohlc : DataFrame[open, high, low, close]（缺列 fail-closed）。
        atr14 : ATR14 序列（与 ohlc 等长对齐，全正值）。
        min_gap_atr : 最小缺口幅度（标准化），低于视为无缺口。

        Returns
        -------
        DataFrame[index, direction, gap_size_atr, grade, prev_close, open,
                  filled_same_day]；无缺口 → 空表。
        """
        missing = [c for c in _OHLC_COLUMNS if c not in ohlc.columns]
        if missing:
            msg = f"ohlc 缺列: {missing}（须含 {list(_OHLC_COLUMNS)}）"
            raise ValueError(msg)
        if len(ohlc) != len(atr14):
            msg = f"atr14 与 ohlc 不等长: {len(atr14)} vs {len(ohlc)}"
            raise ValueError(msg)
        if (atr14 <= 0).any():
            msg = "atr14 含非正值（ATR 须为正）"
            raise ValueError(msg)
        if min_gap_atr < 0.0:
            msg = f"min_gap_atr 须非负，实得 {min_gap_atr}"
            raise ValueError(msg)

        prev_close = ohlc["close"].shift(1)
        gap = (ohlc["open"] - prev_close) / atr14
        events: list[dict[str, Any]] = []
        for i in range(1, len(ohlc)):
            size = gap.iloc[i]
            if pd.isna(size) or abs(size) < min_gap_atr:
                continue
            direction = GapDirection.UP.value if size > 0 else GapDirection.DOWN.value
            pc = float(prev_close.iloc[i])
            if direction == GapDirection.UP.value:
                filled = bool(ohlc["low"].iloc[i] <= pc)
            else:
                filled = bool(ohlc["high"].iloc[i] >= pc)
            events.append(
                {
                    "index": ohlc.index[i],
                    "direction": direction,
                    "gap_size_atr": abs(float(size)),
                    "grade": self.classify(abs(float(size))).value,
                    "prev_close": pc,
                    "open": float(ohlc["open"].iloc[i]),
                    "filled_same_day": filled,
                }
            )
        return pd.DataFrame(events)


# scaffold 注册别名（__init__.py export 契约，类名以 min_build_spec 为准）
GapFillModel = GapFillProbabilityModel
