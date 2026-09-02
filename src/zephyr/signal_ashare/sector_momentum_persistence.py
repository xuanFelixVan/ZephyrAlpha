# [BLUEPRINT] MOD-SIG-098 | docs/03_modules/_domain_signal/sector_momentum_persistence/blueprint.md
# [MODULE] zephyr.signal_ashare.sector_momentum_persistence
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；板块收益/资金流/梯队/指数序列鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：主线持续性页签、买入侧持续性门槛装配层；上游名单 MOD-SIG-061 mainline_candidates）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 五维持续分缺维按可用权重重归一（不留 0 拉低，同 MOD-SIG-064 缺维先例）；MPS=正收益日占比∈[0,1]；资金子分对齐 MOD-SIG-064 F3 口径（0.6×正流入占比+0.4×尾部连正/3）；梯队 CV=σ/μ（μ=0 降级）；共振=Pearson ρ（零方差降级）；恢复速度查表（1d→1.0/未收复→0.1）；广度二态 mainline≥0.6/speculative≤0.3 封闭集；PIT（全部窗口数据≤当日）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01367 行 + 候选注册表 CAND-TESTB-013
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 序列不等长/短于 min_window/非有限值/负梯队高度/空板块列表/配置越界（权重和≠1） → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_sector_momentum_persistence.py
# [A_module] module_id=MOD-SIG-098 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""动量层级与板块持续性模型（MOD-SIG-098，B10-01367）。

场内对账：mainline_probability（MOD-SIG-064）= 主线概率四因子评分（管"谁是主线"）；
**动量广度判定/梯队层级稳定性 CV/Momentum Persistence Score/分歧恢复速度/
板块-指数共振度无实现**（深挖批 min_build_spec 明示缺口），本模块落地
（管"主线能持续多久"，与 064 上下游候选关系、语义正交）。

两件套：

- **单板块五维持续分**：MPS（窗口正收益日占比，≥0.7 持续标记）+ 资金流持续性
  （MOD-SIG-064 F3 同口径：0.6×正流入日占比+0.4×min(尾部连正天数/3,1)）
  + 梯队层级稳定性（日最高连板 CV 查表：≤0.3→1.0/≤0.5→0.7/≤0.8→0.4/>0.8→0.1）
  + 板块-指数共振度（Pearson ρ）+ 分歧恢复速度（最近分歧日≤−2% 后累计收益收复
  天数查表：1d→1.0/2d→0.8/3d→0.6/4-5d→0.4/>5d 或未收复→0.1）；缺维按可用权重
  重归一，composite=Σw·s/Σw(可用)×100。
- **市场动量广度**：窗口复利动量>0 板块占比；≥0.6→mainline（主线生态），
  ≤0.3→speculative（投机生态），其间→balanced。

依据: AUD-DRAFT-001 深挖批 B10-01367（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-098
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 板块窗（日收益/主力净流入/日最高连板/当日梯队分布）+ 指数日收益 / 板块列表
# 特征: 正收益日占比 + 正流入占比与尾连 + 梯队 CV + Pearson ρ + 分歧收复天数 + 窗动量符号
# 算法: 五维子分（查表/比率）→ 缺维重归一加权合成；广度占比 → 二态判定
# 输出: SectorPersistenceScore（五子分+composite+persistent 标记）+ MarketBreadthRegime
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "MarketBreadthRegime",
    "MomentumPersistenceConfig",
    "SectorMomentumInput",
    "SectorMomentumPersistence",
    "SectorPersistenceScore",
]

_WEIGHT_SUM_TOL: Final = 1e-9


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class SectorMomentumInput:
    """板块窗口输入（鸭子类型；序列等长，尾部=最新交易日）。"""

    sector_code: str
    daily_returns: tuple[float, ...]
    fund_net_inflows: tuple[float, ...]
    ladder_top_heights: tuple[int, ...]
    ladder_distribution: dict[int, int]


@dataclass(frozen=True)
class MomentumPersistenceConfig:
    """阈值与权重配置（构造即校验，fail-closed）。"""

    min_window: int = 10
    mps_persistent_threshold: float = 0.7
    fund_sustain_days: int = 3
    ladder_cv_stable: float = 0.3
    resonance_threshold: float = 0.6
    divergence_threshold: float = -0.02
    breadth_mainline: float = 0.6
    breadth_speculative: float = 0.3
    weight_mps: float = 0.30
    weight_fund: float = 0.25
    weight_ladder: float = 0.20
    weight_resonance: float = 0.15
    weight_recovery: float = 0.10

    def __post_init__(self) -> None:
        if self.min_window < 5:
            msg = f"min_window 须≥5，实得 {self.min_window}"
            raise ValueError(msg)
        if not (0.0 < self.mps_persistent_threshold < 1.0):
            msg = f"mps_persistent_threshold 须∈(0,1)，实得 {self.mps_persistent_threshold}"
            raise ValueError(msg)
        if self.fund_sustain_days < 1:
            msg = f"fund_sustain_days 须≥1，实得 {self.fund_sustain_days}"
            raise ValueError(msg)
        if not (0.0 < self.ladder_cv_stable < 1.0):
            msg = f"ladder_cv_stable 须∈(0,1)，实得 {self.ladder_cv_stable}"
            raise ValueError(msg)
        if not (0.0 < self.resonance_threshold < 1.0):
            msg = f"resonance_threshold 须∈(0,1)，实得 {self.resonance_threshold}"
            raise ValueError(msg)
        if not (-1.0 < self.divergence_threshold < 0.0):
            msg = f"divergence_threshold 须∈(-1,0)，实得 {self.divergence_threshold}"
            raise ValueError(msg)
        if not (0.0 < self.breadth_speculative < self.breadth_mainline < 1.0):
            msg = f"广度阈值须 0<speculative<mainline<1，实得 {self.breadth_speculative}/{self.breadth_mainline}"
            raise ValueError(msg)
        weights = self.weights()
        for name, w in weights.items():
            if w < 0.0:
                msg = f"权重 {name} 须≥0，实得 {w}"
                raise ValueError(msg)
        if abs(sum(weights.values()) - 1.0) > _WEIGHT_SUM_TOL:
            msg = f"权重和须=1，实得 {sum(weights.values())}"
            raise ValueError(msg)

    def weights(self) -> dict[str, float]:
        return {
            "mps": self.weight_mps,
            "fund": self.weight_fund,
            "ladder": self.weight_ladder,
            "resonance": self.weight_resonance,
            "recovery": self.weight_recovery,
        }


@dataclass(frozen=True)
class SectorPersistenceScore:
    """单板块持续分输出。"""

    sector_code: str
    mps: float
    mps_persistent: bool
    fund_score: float
    fund_streak_days: int
    ladder_cv: float | None
    ladder_stability_score: float | None
    resonance: float | None
    recovery_days: int | None
    recovery_score: float | None
    composite_score: float | None
    degraded: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketBreadthRegime:
    """市场动量广度二态输出。"""

    sector_count: int
    positive_count: int
    breadth: float
    regime: str
    mainline_flag: bool
    speculative_flag: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------
# 引擎
# ------------------------------------------------------------------
class SectorMomentumPersistence:
    """板块动量持续性度量引擎（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: MomentumPersistenceConfig | None = None) -> None:
        self._config = config if config is not None else MomentumPersistenceConfig()

    @property
    def config(self) -> MomentumPersistenceConfig:
        return self._config

    # ── 输入校验 ──────────────────────────────────────────────────
    def _validate_sector(self, sector: SectorMomentumInput, index_returns: Sequence[float]) -> None:
        cfg = self._config
        n = len(sector.daily_returns)
        if not (len(sector.fund_net_inflows) == len(sector.ladder_top_heights) == n):
            msg = "板块序列不等长（returns/inflows/ladder_top_heights）"
            raise ValueError(msg)
        if len(index_returns) != n:
            msg = f"指数收益与板块窗不等长: {len(index_returns)} vs {n}"
            raise ValueError(msg)
        if n < cfg.min_window:
            msg = f"窗口 {n}<{cfg.min_window}"
            raise ValueError(msg)
        series = (*sector.daily_returns, *sector.fund_net_inflows, *index_returns)
        if not all(math.isfinite(v) for v in series):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if any(h < 0 for h in sector.ladder_top_heights):
            msg = "梯队高度含负值"
            raise ValueError(msg)

    # ── 单板块五维持续分 ───────────────────────────────────────────
    def score_sector(self, sector: SectorMomentumInput, index_returns: Sequence[float]) -> SectorPersistenceScore:
        cfg = self._config
        self._validate_sector(sector, index_returns)
        notes: list[str] = []
        rets = list(sector.daily_returns)
        n = len(rets)

        # ① MPS = 正收益日占比
        mps = sum(1 for r in rets if r > 0.0) / n
        mps_persistent = mps >= cfg.mps_persistent_threshold

        # ② 资金流持续性（MOD-SIG-064 F3 同口径）
        inflows = list(sector.fund_net_inflows)
        pos_ratio = sum(1 for v in inflows if v > 0.0) / n
        streak = 0
        for v in reversed(inflows):
            if v > 0.0:
                streak += 1
            else:
                break
        fund_score = 0.6 * pos_ratio + 0.4 * min(streak / cfg.fund_sustain_days, 1.0)

        # ③ 梯队层级稳定性 CV 查表（μ=0 → 降级）
        heights = list(sector.ladder_top_heights)
        mean_h = statistics.fmean(heights)
        ladder_cv: float | None = None
        ladder_score: float | None = None
        if mean_h > 0.0:
            ladder_cv = statistics.pstdev(heights) / mean_h
            if ladder_cv <= cfg.ladder_cv_stable:
                ladder_score = 1.0
            elif ladder_cv <= 0.5:
                ladder_score = 0.7
            elif ladder_cv <= 0.8:
                ladder_score = 0.4
            else:
                ladder_score = 0.1
        else:
            notes.append("窗口零涨停（梯队均值=0），梯队稳定性腿降级")

        # ④ 板块-指数共振度 Pearson ρ（零方差 → 降级）
        idx = [float(v) for v in index_returns]
        resonance: float | None = None
        sd_s = statistics.pstdev(rets)
        sd_i = statistics.pstdev(idx)
        if sd_s > 0.0 and sd_i > 0.0:
            mean_s = statistics.fmean(rets)
            mean_i = statistics.fmean(idx)
            cov = statistics.fmean([(a - mean_s) * (b - mean_i) for a, b in zip(rets, idx)])
            resonance = cov / (sd_s * sd_i)
        else:
            notes.append("板块或指数收益零方差，共振度腿降级")

        # ⑤ 分歧恢复速度（最近分歧日收复天数查表）
        recovery_days: int | None = None
        recovery_score: float | None = None
        div_idx = max((i for i, r in enumerate(rets) if r <= cfg.divergence_threshold), default=None)
        if div_idx is not None:
            cum = 0.0
            for j in range(div_idx + 1, n):
                cum += rets[j]
                if cum >= -rets[div_idx]:
                    recovery_days = j - div_idx
                    break
            if recovery_days is not None:
                if recovery_days <= 1:
                    recovery_score = 1.0
                elif recovery_days <= 2:
                    recovery_score = 0.8
                elif recovery_days <= 3:
                    recovery_score = 0.6
                elif recovery_days <= 5:
                    recovery_score = 0.4
                else:
                    recovery_score = 0.1
            else:
                recovery_score = 0.1  # 分歧未收复
        else:
            notes.append("窗口无分歧日，恢复速度腿降级")

        # 合成（缺维重归一）
        weights = cfg.weights()
        legs: dict[str, float | None] = {
            "mps": mps,
            "fund": fund_score,
            "ladder": ladder_score,
            "resonance": resonance,
            "recovery": recovery_score,
        }
        avail = {k: v for k, v in legs.items() if v is not None}
        composite: float | None = None
        degraded = False
        if avail:
            w_sum = sum(weights[k] for k in avail)
            composite = sum(weights[k] * v for k, v in avail.items()) / w_sum * 100.0
        else:
            degraded = True
            notes.append("五维全缺，不出伪分")

        return SectorPersistenceScore(
            sector_code=sector.sector_code,
            mps=mps,
            mps_persistent=mps_persistent,
            fund_score=fund_score,
            fund_streak_days=streak,
            ladder_cv=ladder_cv,
            ladder_stability_score=ladder_score,
            resonance=resonance,
            recovery_days=recovery_days,
            recovery_score=recovery_score,
            composite_score=composite,
            degraded=degraded,
            notes=tuple(notes),
        )

    # ── 市场动量广度二态 ───────────────────────────────────────────
    def market_breadth(self, sectors: Sequence[SectorMomentumInput]) -> MarketBreadthRegime:
        cfg = self._config
        if not sectors:
            msg = "空板块列表"
            raise ValueError(msg)
        positive = 0
        for s in sectors:
            if not s.daily_returns:
                msg = f"板块 {s.sector_code} 空收益序列"
                raise ValueError(msg)
            if not all(math.isfinite(v) for v in s.daily_returns):
                msg = f"板块 {s.sector_code} 收益含非有限值"
                raise ValueError(msg)
            momentum = math.prod(1.0 + r for r in s.daily_returns) - 1.0
            if momentum > 0.0:
                positive += 1
        breadth = positive / len(sectors)
        if breadth >= cfg.breadth_mainline:
            regime = "mainline"
        elif breadth <= cfg.breadth_speculative:
            regime = "speculative"
        else:
            regime = "balanced"
        return MarketBreadthRegime(
            sector_count=len(sectors),
            positive_count=positive,
            breadth=breadth,
            regime=regime,
            mainline_flag=regime == "mainline",
            speculative_flag=regime == "speculative",
        )
