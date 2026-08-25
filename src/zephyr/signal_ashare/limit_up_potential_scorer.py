# [BLUEPRINT] MOD-SIG-102 | docs/03_modules/_domain_signal/limit_up_potential_scorer/blueprint.md
# [MODULE] zephyr.signal_ashare.limit_up_potential_scorer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；连板梯队/封单/龙虎榜/情绪等分证据鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：打板买入侧装配层、涨停板生态页评分卡；上游分生产方 MOD-SIG-097 梯队/封板时间、MOD-SIG-057 龙虎榜溢价、MOD-SIG-025 情绪分）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 七分封闭集（连板高度/封单强度/板块动量/筹码集中度/龙虎榜/量能配合/市场情绪）；IC 验证门 IC>0.03 且 ICIR>0.5 才配权；IC 加权 w_i=IC_i/ΣIC_j（Σ=1，出局归 0）；全分出局回退经验权重（Σ=1）且 sufficient=False；样本不足该分出局不阻断；综合分∈[0,100]；分档 A/B/C/D 封闭集；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01380 行 + 候选注册表 CAND-TESTB-017
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol/空分列表/未知分名/重复分名/分越界[0,1]/非有限样本/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_limit_up_potential_scorer.py
# [A_module] module_id=MOD-SIG-102 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""IC加权多因子涨停板潜力评分模型（MOD-SIG-102，B10-01380，模块33）。

场内对账：limit_up_classifier（MOD-ML-CLS1）=ML 分类器骨架（骨架态禁真训练）、
strength_ic_weight_calibrator=短线强度 6 维子分 IC 校准（维度族不同）、
bma_signal_weighter（MOD-L02-001）=信号级 BMA 动态权重（因子域，粒度不同）、
lhb_premium_analyzer（MOD-SIG-057）/limit_up_ecosystem_leadership（MOD-SIG-097）
=龙虎榜/梯队单分生产方；**涨停潜力七分 IC 验证后 IC 加权整合评分无实现**
（深挖批 min_build_spec 明示缺口），本模块落地。

七分封闭集（注册表 problem 既定）：
连板高度 ladder_height / 封单强度 seal_strength / 板块动量 sector_momentum /
筹码集中度 chip_concentration / 龙虎榜 lhb_premium / 量能配合 volume_confirmation /
市场情绪 market_sentiment。

算法（qlib IC 加权主流做法的纯函数核落地）：

1. **IC 验证**：每分注入历史样本（分值, 前瞻收益）PIT 对，Spearman 秩相关
   （平均秩处理并列，零 numpy/scipy）；滚动分块（默认 5 块）逐块 IC →
   ICIR=mean/pstdev（零方差且均值>0 → 999.0 视为极稳定，文档化 MVP 初拍）。
2. **配权**：IC>ic_gate（0.03）且 ICIR>icir_gate（0.5）→ 有效；
   w_i=IC_i/Σ_{有效} IC_j（Σ=1）；无效分权重归 0。
3. **回退**：全分出局（含全样本不足）→ 经验权重按在场分重归一，
   fallback_used=True 且 sufficient=False（显式降级不静默）。
4. **评分**：composite=Σ w_i×current_score_i×100（current_score 上游归一
   [0,1] 注入）；分档 ≥70 A / ≥50 B / ≥30 C / 其余 D（封闭集）。

不做什么：不生产任何单分（上游注入）、不做 ML 训练、不直连 DB、不荐股。

依据: AUD-DRAFT-001 深挖批 B10-01380（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-102
Version: 0.1.0

# [ALGO_FLOW]
# 输入: symbol + tuple[FactorEvidence]（分名/当前标准化分/(分值,前瞻收益)样本对）
# 特征: Spearman RankIC + 分块 IC 序列（ICIR）+ 当前分
# 算法: 校验 → 逐分 IC/ICIR → 门控配权（全出局→经验回退）→ 加权合成×100 → 分档
# 输出: LimitUpPotentialReport（综合分/分档/逐分评估/回退标记/充分标记/notes）
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "EMPIRICAL_WEIGHTS",
    "LIMIT_UP_FACTOR_NAMES",
    "FactorEvidence",
    "FactorEvaluation",
    "LimitUpPotentialConfig",
    "LimitUpPotentialReport",
    "LimitUpPotentialScorer",
]

#: 七分封闭集（候选注册表 CAND-TESTB-017 problem 既定口径）
LIMIT_UP_FACTOR_NAMES: Final[tuple[str, ...]] = (
    "ladder_height",  # 连板高度（MOD-SIG-097 梯队语义注入）
    "seal_strength",  # 封单强度
    "sector_momentum",  # 板块动量
    "chip_concentration",  # 筹码集中度
    "lhb_premium",  # 龙虎榜（MOD-SIG-057 语义注入）
    "volume_confirmation",  # 量能配合
    "market_sentiment",  # 市场情绪（MOD-SIG-025 语义注入）
)

#: 经验权重（MVP 初拍待回验标定，Σ=1；全分 IC 出局时按在场分重归一回退）
EMPIRICAL_WEIGHTS: Final[dict[str, float]] = {
    "ladder_height": 0.20,
    "seal_strength": 0.15,
    "sector_momentum": 0.15,
    "chip_concentration": 0.10,
    "lhb_premium": 0.15,
    "volume_confirmation": 0.15,
    "market_sentiment": 0.10,
}

#: ICIR 零方差且均值>0 的极稳定替代值（文档化 MVP 初拍）
_STABLE_ICIR: Final = 999.0


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class LimitUpPotentialConfig:
    """门/窗/分档配置（构造即校验，fail-closed）。"""

    ic_gate: float = 0.03
    icir_gate: float = 0.5
    min_samples: int = 30
    ic_chunks: int = 5
    grade_a_threshold: float = 70.0
    grade_b_threshold: float = 50.0
    grade_c_threshold: float = 30.0

    def __post_init__(self) -> None:
        if self.ic_gate < 0.0:
            msg = f"ic_gate 须≥0，实得 {self.ic_gate}"
            raise ValueError(msg)
        if self.icir_gate < 0.0:
            msg = f"icir_gate 须≥0，实得 {self.icir_gate}"
            raise ValueError(msg)
        if self.min_samples < 6:
            msg = f"min_samples 须≥6，实得 {self.min_samples}"
            raise ValueError(msg)
        if self.ic_chunks < 2:
            msg = f"ic_chunks 须≥2，实得 {self.ic_chunks}"
            raise ValueError(msg)
        if not (
            self.grade_a_threshold
            >= self.grade_b_threshold
            >= self.grade_c_threshold
            >= 0.0
        ):
            msg = (
                "分档门槛须单调不增且≥0："
                f"A={self.grade_a_threshold}/B={self.grade_b_threshold}/C={self.grade_c_threshold}"
            )
            raise ValueError(msg)
        if self.grade_a_threshold > 100.0:
            msg = f"grade_a_threshold 须≤100，实得 {self.grade_a_threshold}"
            raise ValueError(msg)


@dataclass(frozen=True)
class FactorEvidence:
    """单分证据：当前标准化分 + 历史 PIT 样本（分值, 前瞻收益）。"""

    name: str
    current_score: float  # ∈[0,1]，上游归一注入
    samples: tuple[tuple[float, float], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.name not in LIMIT_UP_FACTOR_NAMES:
            msg = f"未知分名（七分封闭集外）: {self.name!r}"
            raise ValueError(msg)
        if not 0.0 <= self.current_score <= 1.0:
            msg = f"current_score 须∈[0,1]: {self.current_score}"
            raise ValueError(msg)
        for pair in self.samples:
            if len(pair) != 2 or not all(math.isfinite(v) for v in pair):
                msg = f"样本须为有限值二元对: {pair!r}"
                raise ValueError(msg)


@dataclass(frozen=True)
class FactorEvaluation:
    """单分评估（IC/ICIR/有效性/权重/当前分）。"""

    name: str
    ic: float
    icir: float
    effective: bool
    weight: float
    current_score: float
    sample_count: int
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LimitUpPotentialReport:
    """涨停潜力评分报告。"""

    symbol: str
    composite_score: float  # ∈[0,100]
    grade: str  # A/B/C/D 封闭集
    evaluations: tuple[FactorEvaluation, ...]
    fallback_used: bool
    sufficient: bool  # ≥1 有效分
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------
# Spearman 秩相关（平均秩处理并列，纯标准库）
# ------------------------------------------------------------------
def _average_ranks(values: Sequence[float]) -> list[float]:
    """平均秩（1..n，并列取均值）。"""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _spearman(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Spearman 秩相关；任一侧零方差（秩全同）→ None（不可验证）。"""
    n = len(xs)
    if n < 3:
        return None
    rx = _average_ranks(xs)
    ry = _average_ranks(ys)
    mx = statistics.fmean(rx)
    my = statistics.fmean(ry)
    sxx = sum((r - mx) ** 2 for r in rx)
    syy = sum((r - my) ** 2 for r in ry)
    if sxx == 0.0 or syy == 0.0:
        return None
    sxy = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    return sxy / math.sqrt(sxx * syy)


def _chunked(seq: Sequence[tuple[float, float]], chunks: int) -> list[Sequence[tuple[float, float]]]:
    """连续等分分块（余数前块多一）。"""
    n = len(seq)
    base, rem = divmod(n, chunks)
    out: list[Sequence[tuple[float, float]]] = []
    start = 0
    for c in range(chunks):
        size = base + (1 if c < rem else 0)
        if size > 0:
            out.append(seq[start : start + size])
        start += size
    return out


# ------------------------------------------------------------------
# 评分器
# ------------------------------------------------------------------
class LimitUpPotentialScorer:
    """涨停潜力七分 IC 加权评分器（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: LimitUpPotentialConfig | None = None) -> None:
        self._config = config if config is not None else LimitUpPotentialConfig()

    @property
    def config(self) -> LimitUpPotentialConfig:
        return self._config

    # ── 单分 IC/ICIR ─────────────────────────────────────────────
    def _evaluate_factor(self, ev: FactorEvidence) -> FactorEvaluation:
        cfg = self._config
        n = len(ev.samples)
        if n < cfg.min_samples:
            return FactorEvaluation(
                name=ev.name,
                ic=0.0,
                icir=0.0,
                effective=False,
                weight=0.0,
                current_score=ev.current_score,
                sample_count=n,
                notes=(f"样本不足 {n}<{cfg.min_samples}，该分出局",),
            )
        xs = [p[0] for p in ev.samples]
        ys = [p[1] for p in ev.samples]
        ic = _spearman(xs, ys)
        notes: list[str] = []
        if ic is None:
            return FactorEvaluation(
                name=ev.name,
                ic=0.0,
                icir=0.0,
                effective=False,
                weight=0.0,
                current_score=ev.current_score,
                sample_count=n,
                notes=("分值或收益零方差，IC 不可验证，该分出局",),
            )
        chunk_ics: list[float] = []
        for chunk in _chunked(ev.samples, cfg.ic_chunks):
            c_ic = _spearman([p[0] for p in chunk], [p[1] for p in chunk])
            if c_ic is not None:
                chunk_ics.append(c_ic)
        if len(chunk_ics) >= 2:
            mean_ic = statistics.fmean(chunk_ics)
            sd = statistics.pstdev(chunk_ics)
            if sd == 0.0:
                icir = _STABLE_ICIR if mean_ic > 0.0 else 0.0
                if mean_ic > 0.0:
                    notes.append("分块 IC 零方差，ICIR 按极稳定 999.0 计")
            else:
                icir = mean_ic / sd
        else:
            icir = 0.0
            notes.append("有效分块<2，ICIR 按 0 计")
        effective = ic > cfg.ic_gate and icir > cfg.icir_gate
        return FactorEvaluation(
            name=ev.name,
            ic=ic,
            icir=icir,
            effective=effective,
            weight=0.0,
            current_score=ev.current_score,
            sample_count=n,
            notes=tuple(notes),
        )

    # ── 主入口 ───────────────────────────────────────────────────
    def evaluate(
        self, symbol: str, factors: Sequence[FactorEvidence]
    ) -> LimitUpPotentialReport:
        if not symbol:
            msg = "symbol 不能为空"
            raise ValueError(msg)
        if not factors:
            msg = "分证据列表不能为空"
            raise ValueError(msg)
        names = [f.name for f in factors]
        if len(set(names)) != len(names):
            msg = f"分名重复: {sorted(n for n in names if names.count(n) > 1)}"
            raise ValueError(msg)

        cfg = self._config
        evals = [self._evaluate_factor(f) for f in factors]
        effective = [e for e in evals if e.effective]
        notes: list[str] = []

        weights: dict[str, float] = {e.name: 0.0 for e in evals}
        fallback_used = False
        if effective:
            ic_sum = sum(e.ic for e in effective)
            for e in effective:
                weights[e.name] = e.ic / ic_sum
        else:
            fallback_used = True
            emp_sum = sum(EMPIRICAL_WEIGHTS[e.name] for e in evals)
            for e in evals:
                weights[e.name] = EMPIRICAL_WEIGHTS[e.name] / emp_sum
            notes.append("全分 IC 验证出局，回退经验权重（显式降级）")

        evals = [
            FactorEvaluation(
                name=e.name,
                ic=e.ic,
                icir=e.icir,
                effective=e.effective,
                weight=weights[e.name],
                current_score=e.current_score,
                sample_count=e.sample_count,
                notes=e.notes,
            )
            for e in evals
        ]
        composite = sum(e.weight * e.current_score for e in evals) * 100.0
        if composite >= cfg.grade_a_threshold:
            grade = "A"
        elif composite >= cfg.grade_b_threshold:
            grade = "B"
        elif composite >= cfg.grade_c_threshold:
            grade = "C"
        else:
            grade = "D"
        return LimitUpPotentialReport(
            symbol=symbol,
            composite_score=composite,
            grade=grade,
            evaluations=tuple(evals),
            fallback_used=fallback_used,
            sufficient=bool(effective),
            notes=tuple(notes),
        )
