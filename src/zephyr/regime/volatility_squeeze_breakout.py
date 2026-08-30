# [BLUEPRINT] MOD-REGIME-013 | docs/03_modules/_domain_regime/volatility_squeeze_breakout/blueprint.md
# [MODULE] zephyr.regime.volatility_squeeze_breakout
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy
# [CONSUMERS] 运行时装配批（regime 特征链 / overlay_signals_builder overlay_dims 契约供数）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 强压缩=RV_5d/RV_20d<0.5且布林带宽分位<10%双腿联合（单腿不出）; 突破方向概率仅压缩窗口内有语义（非压缩期中性0.5不干预）; 确认=RV扩张>1.5且放量>1.5x且同向连续>=3日; 样本不足/数据缺失降级不抛错（对齐MOD-REGIME-011）; 配置非法/输入契约违反 Fail-Closed; overlay_dims score∈[0,100]/flag∈{0,1}/无信号=0
# [MODIFY-GUARD] tests/regime/test_volatility_squeeze_breakout.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SqueezeConfigError(未登记错误码-申请中)
# [TESTS] tests/regime/test_volatility_squeeze_breakout.py
# [A_module] module_id=MOD-REGIME-013 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
模块51 波动率压缩与突破模型（MOD-REGIME-013）。

真源：construction_backlog_dig.tsv B10-01387（A1 交易决策架构 §3 模块51，
裁定=做 P1）+ CAND-CYCLE-005。

与 MOD-REGIME-011 分工（查重铁律④细读 TSV 裁定=扩展施工）：alerter 只出
rv_ratio<0.8 压缩**早标记**且其 docstring 明示"<0.5 强压缩归模块51 联动"，
突破方向判定与维持确认无任何既有件。本模块三件套：
  ① 强压缩双腿联合标记——rv_ratio=RV_5d/RV_20d（年化，口径复用 alerter）<0.5
     **且** 布林带宽（20 窗 2σ，(upper−lower)/mid）历史分位 <10%；单腿命中只出
     分项不出联合标记；
  ② 突破方向概率——价格位置（close 在近 20 日区间归一位置）与量能方向
     （近 20 日上涨日成交量占比）等权混合 → p_up∈[0,1]；仅压缩窗口内有语义，
     非压缩期置中性 0.5 不干预；
  ③ 3 日维持确认——RV 扩张（rv_ratio>1.5，即 RV_5d>1.5×RV_20d）且放量
     （5 日均量/20 日均量>1.5）且同向连续 >=3 日 → confirmed，方向取窗口
     价格位移符号。

降级哲学（对齐 MOD-REGIME-011）：样本不足/非有限数据 → 全维度=0 + degraded
不抛错；仅配置非法/输入契约违反（量价长度不齐）Fail-Closed。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: volatility_squeeze_breakout.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SqueezeBreakoutSignal
#   name_en: SqueezeBreakoutSignal
#   intro: 压缩突破信号（降级时全维度=0，对齐 overlay 契约哲学）。
#   desc: 压缩突破信号（降级时全维度=0，对齐 overlay 契约哲学）。 Attributes: rv_ratio: RV_5d/RV_20d 年化波动比（长窗零波动为 inf） bb…；公共方法（定义序）: overlay…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② VolatilitySqueezeBreakout
#   name_en: VolatilitySqueezeBreakout
#   intro: 模块51 波动率压缩与突破判定器（纯函数，降级不抛错）。
#   desc: 模块51 波动率压缩与突破判定器（纯函数，降级不抛错）。；公共方法（定义序）: config, assess；源码 L205-L350
#   inputs: config
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: SqueezeBreakoutSignal, VolatilitySqueezeBreakout
#   downstream: 运行时装配批（regime 特征链 / overlay_signals_builder overlay_dims 契约供数）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

import numpy as np

__all__: Final = [
    "SqueezeBreakoutSignal",
    "SqueezeConfig",
    "SqueezeConfigError",
    "VolatilitySqueezeBreakout",
]

_log = logging.getLogger(__name__)

_ANNUALIZATION: Final[int] = 252  # A股交易日年化因子（对齐 MOD-REGIME-011/alerter）


class SqueezeConfigError(ValueError):
    """压缩突破配置非法或输入契约违反（Fail-Closed；未登记错误码-申请中）。"""


@dataclass(frozen=True)
class SqueezeConfig:
    """压缩突破配置（阈值为 TSV/CAND 最小施工形态真源，待实盘标定）。

    Attributes:
        rv_short_window: RV 短窗（默认 5 日）
        rv_long_window: RV 长窗基线（默认 20 日）
        strong_compression_threshold: 强压缩 RV 比上限（默认 0.5，模块51 真源；
            区别于 alerter 早标记 0.8）
        bb_window: 布林带窗（默认 20）
        bb_num_std: 布林带标准差倍数（默认 2.0）
        bb_percentile_threshold: 带宽历史分位上限（默认 0.10=10%）
        direction_window: 方向概率窗口（默认 20 日）
        sustain_days: 维持确认日数（默认 3）
        confirm_rv_expansion: 确认 RV 扩张下限（默认 1.5，RV_5d>1.5×RV_20d）
        confirm_volume_expansion: 确认放量下限（默认 1.5，5日均量>1.5×20日均量）
        min_history: 最小样本数（默认 60；须 >= rv_long_window + bb_window）
    """

    rv_short_window: int = 5
    rv_long_window: int = 20
    strong_compression_threshold: float = 0.5
    bb_window: int = 20
    bb_num_std: float = 2.0
    bb_percentile_threshold: float = 0.10
    direction_window: int = 20
    sustain_days: int = 3
    confirm_rv_expansion: float = 1.5
    confirm_volume_expansion: float = 1.5
    min_history: int = 60

    def __post_init__(self) -> None:
        if self.rv_short_window < 2:
            raise SqueezeConfigError(f"rv_short_window 须 >=2: {self.rv_short_window}")
        if self.rv_long_window <= self.rv_short_window:
            raise SqueezeConfigError(
                f"rv_long_window({self.rv_long_window}) 须 > rv_short_window({self.rv_short_window})"
            )
        if not 0.0 < self.strong_compression_threshold < 1.0:
            raise SqueezeConfigError(f"strong_compression_threshold 须 ∈(0,1): {self.strong_compression_threshold}")
        if self.bb_window < 2:
            raise SqueezeConfigError(f"bb_window 须 >=2: {self.bb_window}")
        if self.bb_num_std <= 0.0:
            raise SqueezeConfigError(f"bb_num_std 须 >0: {self.bb_num_std}")
        if not 0.0 < self.bb_percentile_threshold < 1.0:
            raise SqueezeConfigError(f"bb_percentile_threshold 须 ∈(0,1): {self.bb_percentile_threshold}")
        if self.direction_window < 2:
            raise SqueezeConfigError(f"direction_window 须 >=2: {self.direction_window}")
        if self.sustain_days < 1:
            raise SqueezeConfigError(f"sustain_days 须 >=1: {self.sustain_days}")
        if not self.confirm_rv_expansion > 1.0:
            raise SqueezeConfigError(f"confirm_rv_expansion 须 >1: {self.confirm_rv_expansion}")
        if not self.confirm_volume_expansion > 1.0:
            raise SqueezeConfigError(f"confirm_volume_expansion 须 >1: {self.confirm_volume_expansion}")
        if self.min_history < self.rv_long_window + self.bb_window:
            raise SqueezeConfigError(
                f"min_history({self.min_history}) 须 >= rv_long_window+bb_window"
                f"({self.rv_long_window + self.bb_window})"
            )


@dataclass(frozen=True)
class SqueezeBreakoutSignal:
    """压缩突破信号（降级时全维度=0，对齐 overlay 契约哲学）。

    Attributes:
        rv_ratio: RV_5d/RV_20d 年化波动比（长窗零波动为 inf）
        bb_width_percentile: 当前布林带宽历史分位 ∈[0,1]
        strong_rv_leg: RV 强压缩腿（rv_ratio<0.5）
        bb_squeeze_leg: 带宽分位腿（分位<10%）
        squeeze_flag: 双腿联合压缩标记（单腿不出）
        p_up: 突破向上概率（仅压缩窗口内有语义；非压缩期中性 0.5）
        p_down: 突破向下概率 = 1 − p_up
        vol_ratio: 5 日均量/20 日均量
        sustain_hits: 尾部同向连续日数
        confirmed: 3 日维持确认标记
        confirm_direction: 确认方向（"up"/"down"/None）
        degraded: 降级标记（样本不足等，全维度=0）
        degrade_reason: 降级原因（未降级为 None）
    """

    rv_ratio: float
    bb_width_percentile: float
    strong_rv_leg: int
    bb_squeeze_leg: int
    squeeze_flag: int
    p_up: float
    p_down: float
    vol_ratio: float
    sustain_hits: int
    confirmed: int
    confirm_direction: str | None
    degraded: bool
    degrade_reason: str | None = field(default=None)

    def overlay_dims(self) -> dict[str, float]:
        """overlay_signals_builder 消费契约：score∈[0,100]/flag∈{0,1}/无信号=0。"""
        if self.degraded:
            return {"vol_squeeze": 0, "breakout_dir_score": 0.0, "breakout_confirmed": 0}
        return {
            "vol_squeeze": int(self.squeeze_flag),
            "breakout_dir_score": float(self.p_up * 100.0) if self.squeeze_flag else 0.0,
            "breakout_confirmed": int(self.confirmed),
        }


class VolatilitySqueezeBreakout:
    """模块51 波动率压缩与突破判定器（纯函数，降级不抛错）。"""

    def __init__(self, config: SqueezeConfig | None = None) -> None:
        self._config = config or SqueezeConfig()

    @property
    def config(self) -> SqueezeConfig:
        return self._config

    def assess(self, closes: np.ndarray, volumes: np.ndarray) -> SqueezeBreakoutSignal:
        """评估日频量价序列，产出压缩突破信号。

        Args:
            closes: 日收盘价序列（须为正；与 volumes 等长——输入契约，违反 Fail-Closed）。
            volumes: 日成交量序列（非负；与 closes 等长）。
        """
        cfg = self._config
        c = np.asarray(closes, dtype=float).ravel()
        v = np.asarray(volumes, dtype=float).ravel()
        if len(c) != len(v):
            raise SqueezeConfigError(f"收盘价与成交量长度不一致: {len(c)} != {len(v)}（输入契约违反）")
        # 非有限/非法值成对过滤（量价同天剔除，保持对齐）
        mask = np.isfinite(c) & np.isfinite(v) & (c > 0) & (v >= 0)
        c, v = c[mask], v[mask]
        n = len(c) - 1  # 收益序列长度
        if n < cfg.min_history:
            return self._degraded(f"样本不足: {n} < min_history={cfg.min_history}")

        r = c[1:] / c[:-1] - 1.0  # 简单收益序列（长度 n）
        vr = v[1:]  # 与收益对齐（首日无前收剔除）

        # ── ① RV 强压缩腿（年化口径复用 MOD-REGIME-011） ──
        rv_short = float(np.std(r[-cfg.rv_short_window :], ddof=1)) * np.sqrt(_ANNUALIZATION)
        rv_long = float(np.std(r[-cfg.rv_long_window :], ddof=1)) * np.sqrt(_ANNUALIZATION)
        rv_ratio = rv_short / rv_long if rv_long > 0 else float("inf")
        strong_rv_leg = 1 if rv_ratio < cfg.strong_compression_threshold else 0

        # ── ① 布林带宽分位腿 ──
        widths = self._bb_width_series(c)
        current_width = float(widths[-1])
        percentile = float(np.mean(widths <= current_width))
        bb_squeeze_leg = 1 if percentile < cfg.bb_percentile_threshold else 0

        squeeze_flag = strong_rv_leg & bb_squeeze_leg

        # ── ② 突破方向概率（仅压缩窗口内有语义，非压缩期中性 0.5 不干预） ──
        if squeeze_flag:
            p_up = self._direction_probability(c, r, vr)
        else:
            p_up = 0.5
        p_down = 1.0 - p_up

        # ── ③ 3 日维持确认（RV 扩张 + 放量 + 同向连续） ──
        vol_ratio = self._volume_ratio(vr)
        sustain_hits = self._consecutive_same_sign_tail(c, r)
        confirmed = 0
        confirm_direction: str | None = None
        if (
            np.isfinite(rv_ratio)
            and rv_ratio > cfg.confirm_rv_expansion
            and vol_ratio > cfg.confirm_volume_expansion
            and sustain_hits >= cfg.sustain_days
        ):
            confirmed = 1
            move = float(c[-1] - c[-cfg.sustain_days - 1])
            confirm_direction = "up" if move > 0 else ("down" if move < 0 else None)

        return SqueezeBreakoutSignal(
            rv_ratio=rv_ratio,
            bb_width_percentile=percentile,
            strong_rv_leg=strong_rv_leg,
            bb_squeeze_leg=bb_squeeze_leg,
            squeeze_flag=squeeze_flag,
            p_up=p_up,
            p_down=p_down,
            vol_ratio=vol_ratio,
            sustain_hits=sustain_hits,
            confirmed=confirmed,
            confirm_direction=confirm_direction,
            degraded=False,
        )

    def _degraded(self, reason: str) -> SqueezeBreakoutSignal:
        return SqueezeBreakoutSignal(
            rv_ratio=0.0,
            bb_width_percentile=0.0,
            strong_rv_leg=0,
            bb_squeeze_leg=0,
            squeeze_flag=0,
            p_up=0.5,
            p_down=0.5,
            vol_ratio=0.0,
            sustain_hits=0,
            confirmed=0,
            confirm_direction=None,
            degraded=True,
            degrade_reason=reason,
        )

    def _bb_width_series(self, c: np.ndarray) -> np.ndarray:
        """布林带宽序列：(upper−lower)/mid = 2×num_std×σ(总体)/MA（逐窗）。"""
        cfg = self._config
        widths: list[float] = []
        for i in range(cfg.bb_window - 1, len(c)):
            window = c[i - cfg.bb_window + 1 : i + 1]
            ma = float(np.mean(window))
            if ma <= 0:
                continue
            sd = float(np.std(window, ddof=0))  # 布林惯例总体标准差
            widths.append(2.0 * cfg.bb_num_std * sd / ma)
        return np.asarray(widths, dtype=float)

    def _direction_probability(self, c: np.ndarray, r: np.ndarray, vr: np.ndarray) -> float:
        """价格位置 × 量能方向等权混合 → p_up∈[0,1]（初拟待实盘标定）。"""
        cfg = self._config
        window_c = c[-cfg.direction_window :]
        lo, hi = float(np.min(window_c)), float(np.max(window_c))
        price_pos = (float(c[-1]) - lo) / (hi - lo) if hi > lo else 0.5
        r_w = r[-cfg.direction_window :]
        v_w = vr[-cfg.direction_window :]
        total_vol = float(np.sum(v_w))
        up_vol = float(np.sum(v_w[r_w > 0]))
        vol_dir = up_vol / total_vol if total_vol > 0 else 0.5
        return float(np.clip(0.5 * price_pos + 0.5 * vol_dir, 0.0, 1.0))

    def _volume_ratio(self, vr: np.ndarray) -> float:
        """5 日均量/20 日均量（20 日均量为 0 → inf 交阈值判定）。"""
        cfg = self._config
        vol_short = float(np.mean(vr[-cfg.rv_short_window :]))
        vol_long = float(np.mean(vr[-cfg.rv_long_window :]))
        return vol_short / vol_long if vol_long > 0 else float("inf")

    def _consecutive_same_sign_tail(self, c: np.ndarray, r: np.ndarray) -> int:
        """尾部与 sustain 窗口价格位移同向的连续日数（0 收益中断）。"""
        cfg = self._config
        move = float(c[-1] - c[-cfg.sustain_days - 1])
        if move == 0.0:
            return 0
        move_sign = 1.0 if move > 0 else -1.0
        hits = 0
        for t in range(len(r) - 1, -1, -1):
            if r[t] == 0.0 or np.sign(r[t]) != move_sign:
                break
            hits += 1
        return hits
