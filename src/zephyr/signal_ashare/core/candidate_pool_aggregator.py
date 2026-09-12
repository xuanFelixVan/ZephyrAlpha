# [BLUEPRINT] MOD-SIG-142 | docs/03_modules/_domain_signal/sentiment_cycle/blueprint.md | §
# [R21 备注] 原"待统筹登记（R21 模块 id 格式冲突未解）"按 gate 合规化为数字制 MOD-SIG-142；
# 落图统筹移交 TDM 增长轨的决议不变，spec=docs/_working/2026-09-11-l308-aggregator-construction.md。
# [MODULE] zephyr.signal_ashare.core.candidate_pool_aggregator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数核零 IO；三来源候选与否决裁决由调用方注入——零 import 上游三件，鸭型镜像对齐 C13 SimilarDayScenario.from_inference 先例）
# [CONSUMERS] TDM-E-L3-08（候选池输出，落图待 TDM 增长轨接线，wiring-news-ig-001 先例）；TDM-E-L3-09（Tier 槽位回填对接 pool_tier_maintenance，待接线）；TDM-E-L4（买卖点层，顺位前段未否决段消费）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核零 IO（三来源候选与否决裁决由调用方注入，对齐 C13 intraday_tomorrow_forecast 纯函数核范式）; 三来源=双池合流候选+策略链候选+否决后清单标记; 否决只标记不剔除（一票否决裁决在上游 negative_veto MOD-SIG-137，本件留痕不重复裁决——否决标记不占容量、不参与顺位、沉底留痕不丢）; 同 symbol 多来源命中按顺位最优去重（tie-break 链=rank_score 降→source_rank 升(None=+inf)→sleeve 定义序→symbol 字典序，全链确定无平票）; 同束同 symbol 完全重复 (symbol,sleeve) 对=fail-closed（上游契约违反/同源束劈参数注入防线）、跨束同 symbol 异 sleeve=合法合流去重（双池合流常态）; 最终排序=未否决在前按顺位分降序、vetoed 沉底留痕（喂 L4 只取未否决顺位前段）; 容量 10-20（真源=节点 algo_note）：上限截断按顺位分保留（默认 20），不足下限不硬凑（fail-open notes 透出），vetoed 不占容量、截断项只进 truncated_out 不进 entries; 空候选来源→空池（fail-open）但否决留痕照常透出（vetoed_symbols 不丢）; 非法输入（rank_score 非有限/未知 sleeve/空 symbol/source_rank 负/束内完全重复/容量配置越界/空 as_of/空否决原因）→ fail-closed; 不持上游对象（零 import 鸭型镜像）；Tier 槽位仅预留不判定（分层归 TDM-E-L3-09 pool_tier_maintenance，tier_slot 由调用方回填）; 同输入必同输出（frozen+纯函数）; sleeve 定义序仅 tie-break 用无优先级语义（algo_note：带各自 sleeve 标签与顺位分，排序只认顺位分）
# [MODIFY-GUARD] 地图节点 TDM-E-L3-08（落图归 TDM 增长轨接线，本件不自行落图——wiring-news-ig-001 先例）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] rank_score 非有限/未知 sleeve/空 symbol/source_rank 为负/完全重复 (symbol,sleeve) 对/容量配置越界(1≤min_size≤max_size)/空 as_of/空否决原因 → CandidatePoolInputError（fail-closed）；空候选来源 → 空池（fail-open，否决留痕照常透出）
# [TESTS] tests/signal_ashare/test_candidate_pool_aggregator.py
# [TTL] permanent
"""CandidatePoolAggregator — L3 候选池输出汇总器（TDM-E-L3-08，aggregation 结构位）。

节点语义（TDM-E-L3-08 algo_note 逐条对码）：
    汇总输出：双池合流+策略链候选+顺位排序+否决后清单=最终候选池（10-20 只），
    带各自 sleeve 标签与顺位分，喂 L4 买卖点层。

三来源（任务真源逐条对码）：
    1. dual_pool_candidates   双池合流候选（短线池 fine_scoring_engine / 波段池
       quant_short_term_strength_engine 产出，每条自带 sleeve 标签）
    2. strategy_chain_candidates   策略链候选（打板/多因子/事件驱动三 sleeve 链
       产出，TDM-E-L3-07-1/2/3 feed 边）
    3. veto_marks   否决后清单标记（negative_veto MOD-SIG-137 否决裁决留痕注入——
       本件只标记不剔除：一票否决裁决在上游，本件留痕不重复裁决；否决标记不占
       容量、不参与顺位、沉底留痕不丢）

聚合管线：三来源合并 → 同 symbol 去重（保留顺位最优）→ 顺位排序 →
容量截断（10-20，按顺位分保留）→ 最终候选池（带 sleeve 标签/顺位分/否决标记/
Tier 槽位），喂 TDM-E-L4 买卖点层与 TDM-E-L3-09 Tier 分层（pool_tier_maintenance）。

晨审 st-tdm-review-20260911 §7.1 裁定：constraint_solver/exposure_manager 锚定
**驳回（语义不对位）**——两者都是"候选池定稿之后"的组合层，不承载"双池合流+
顺位+否决清单汇总"的候选池输出语义；节点为 aggregation 结构位，汇总件归属另立
（Owner 2026-09-11 批准立项本件）。落图归 TDM 增长轨接线（wiring-news-ig-001
先例：交付包落码+tests，规格卡移交增长轨统筹落图，本件不自行落图）。

MOD id 待统筹登记（R21 模块 id 格式冲突未解，按接线先例 wiring-news-ig-001
移交 TDM 增长轨统筹登记，落图建议见 docs/_working/2026-09-11-l308-aggregator-construction.md）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterable

__all__: Final = [
    "CandidatePoolConfig",
    "CandidatePoolInputError",
    "FinalCandidatePool",
    "FinalPoolEntry",
    "PoolCandidateInput",
    "SLEEVE_ORDER",
    "SleeveKind",
    "VetoMark",
    "aggregate_candidate_pool",
]


class SleeveKind(str, Enum):
    """sleeve 标签（来源枚举；仅 tie-break 确定序用，无优先级语义——排序只认顺位分）。"""

    SHORT_TERM = "short_term"  # 短线池（fine_scoring_engine 产出）
    SWING = "swing"  # 波段池（quant_short_term_strength_engine 产出）
    DABAN = "daban"  # 打板链（daban_sleeve_strategy 产出，TDM-E-L3-07-1）
    MULTIFACTOR = "multifactor"  # 多因子链（multifactor_sleeve_strategy 产出，TDM-E-L3-07-2）
    EVENT_DRIVEN = "event_driven"  # 事件驱动链（event_driven_sleeve_strategy 产出，TDM-E-L3-07-3）


#: sleeve 定义序（仅 tie-break 确定序，无优先级语义——algo_note：带各自 sleeve 标签
#: 与顺位分，排序只认顺位分）
SLEEVE_ORDER: Final[tuple[SleeveKind, ...]] = (
    SleeveKind.SHORT_TERM,
    SleeveKind.SWING,
    SleeveKind.DABAN,
    SleeveKind.MULTIFACTOR,
    SleeveKind.EVENT_DRIVEN,
)
_SLEEVE_VALUES: Final[frozenset[str]] = frozenset(s.value for s in SLEEVE_ORDER)
_SLEEVE_INDEX: Final[dict[str, int]] = {s.value: i for i, s in enumerate(SLEEVE_ORDER)}

#: 容量真源（TDM-E-L3-08 algo_note：最终候选池 10-20 只）
DEFAULT_MIN_SIZE: Final = 10
DEFAULT_MAX_SIZE: Final = 20


class CandidatePoolInputError(ValueError):
    """输入非法（fail-closed）：分数非有限/sleeve 未知/空 symbol/完全重复对/配置越界/空 as_of。"""


@dataclass(frozen=True)
class CandidatePoolConfig:
    """容量配置（真源=TDM-E-L3-08 algo_note：最终候选池 10-20 只）。"""

    min_size: int = DEFAULT_MIN_SIZE
    max_size: int = DEFAULT_MAX_SIZE

    def __post_init__(self) -> None:
        if not (1 <= self.min_size <= self.max_size):
            raise CandidatePoolInputError(
                f"容量配置越界（须 1 ≤ min_size ≤ max_size）: "
                f"min_size={self.min_size}, max_size={self.max_size}"
            )


@dataclass(frozen=True)
class PoolCandidateInput:
    """单条候选镜像（frozen；上游三件输出的鸭型镜像，零 import 上游对象）。

    rank_score=上游顺位分（任意有限标量，越高越优——上游分数体系不一，z_score/
    0-100 分/权重均可，调用方负责口径统一）；source_rank=上游内部名次（可选，
    tie-break 用，0/1 起名次皆可，仅相对序参与比较）。
    """

    symbol: str
    sleeve: str
    rank_score: float
    source_rank: int | None = None

    def __post_init__(self) -> None:
        if not self.symbol or not self.symbol.strip():
            raise CandidatePoolInputError("symbol 为空")
        if self.sleeve not in _SLEEVE_VALUES:
            raise CandidatePoolInputError(
                f"{self.symbol} sleeve 未知: {self.sleeve!r}（合法值: {sorted(_SLEEVE_VALUES)}）"
            )
        if not math.isfinite(self.rank_score):
            raise CandidatePoolInputError(f"{self.symbol} rank_score 非有限: {self.rank_score!r}")
        if self.source_rank is not None and self.source_rank < 0:
            raise CandidatePoolInputError(f"{self.symbol} source_rank 为负: {self.source_rank}")

    @classmethod
    def from_mirror(
        cls,
        obj,
        sleeve: str | SleeveKind,
        *,
        score_attr: str = "rank_score",
        rank_attr: str | None = "source_rank",
        symbol_attr: str = "symbol",
    ) -> PoolCandidateInput:
        """鸭型镜像转换（零 import；对齐 C13 SimilarDayScenario.from_inference 先例）。"""
        rank_val = getattr(obj, rank_attr) if rank_attr else None
        return cls(
            symbol=str(getattr(obj, symbol_attr)),
            sleeve=sleeve.value if isinstance(sleeve, SleeveKind) else str(sleeve),
            rank_score=float(getattr(obj, score_attr)),
            source_rank=int(rank_val) if rank_val is not None else None,
        )

    @classmethod
    def from_fine_scored_entry(cls, obj, sleeve: str | SleeveKind) -> PoolCandidateInput:
        """fine_scoring_engine.ScoredEntry 姿态镜像（symbol/z_score/rank，零 import）。"""
        return cls(
            symbol=str(obj.symbol),
            sleeve=sleeve.value if isinstance(sleeve, SleeveKind) else str(sleeve),
            rank_score=float(obj.z_score),
            source_rank=int(obj.rank),
        )


@dataclass(frozen=True)
class VetoMark:
    """否决后清单标记（frozen；negative_veto 否决裁决留痕注入——只标记不剔除）。

    reasons=全部命中原因（可审计，对齐 negative_veto reasons 全量披露不变量）。
    """

    symbol: str
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.symbol or not self.symbol.strip():
            raise CandidatePoolInputError("否决标记 symbol 为空")
        if not self.reasons:
            raise CandidatePoolInputError(f"{self.symbol} 否决原因为空（无原因标记不可审计）")

    @classmethod
    def from_veto_verdict(cls, obj, symbol: str) -> VetoMark | None:
        """negative_veto.NegativeVetoVerdict 姿态转换（vetoed=False → None，零 import）。

        verdict 本体不带 symbol，由调用方补传（与裁决时遍历的候选一一对应）；
        reasons 鸭型对齐 NegativeVetoVerdict.reasons（全量披露命中原因不变量）。
        """
        if not obj.vetoed:
            return None
        return cls(symbol=symbol, reasons=tuple(str(r) for r in obj.reasons))


@dataclass(frozen=True)
class FinalPoolEntry:
    """最终候选池单条目（frozen；喂 TDM-E-L4 买卖点层 / TDM-E-L3-09 Tier 回填）。

    sleeves=全部命中 sleeve 标签（多来源合流时按定义序去重合并）；best_sleeve=
    顺位最优来源的 sleeve（主标签）；rank_score=去重保留的顺位最优分；
    tier_slot=Tier 槽位（本件置 None 仅预留——分层归 TDM-E-L3-09
    pool_tier_maintenance，由调用方回填槽位）。
    """

    symbol: str
    sleeves: tuple[str, ...]
    best_sleeve: str
    rank_score: float
    source_rank: int | None
    vetoed: bool
    veto_reasons: tuple[str, ...]
    tier_slot: int | None = None

    def to_dict(self) -> dict:
        """全基本类型字典（JSON 可序列化）。"""
        return {
            "symbol": self.symbol,
            "sleeves": list(self.sleeves),
            "best_sleeve": self.best_sleeve,
            "rank_score": self.rank_score,
            "source_rank": self.source_rank,
            "vetoed": self.vetoed,
            "veto_reasons": list(self.veto_reasons),
            "tier_slot": self.tier_slot,
        }


@dataclass(frozen=True)
class FinalCandidatePool:
    """最终候选池（frozen；喂 TDM-E-L4 买卖点层 / TDM-E-L3-09 Tier 回填）。

    entries=最终候选池（未否决在前按顺位分降序，vetoed 沉底留痕——喂 L4 只取
    未否决顺位前段；截断出池项不在此列，见 truncated_out）；capacity=容量上限
    生效值；actual_size=未否决保留数；truncated_out=上限截断出池名单（按顺位，
    审计——可喂 L3-09 Tier3 雷达池）；vetoed_symbols=否决标记清单（含候选束外
    纯留痕）。
    """

    as_of: str
    entries: tuple[FinalPoolEntry, ...]
    capacity: int
    actual_size: int
    truncated_out: tuple[str, ...]
    vetoed_symbols: tuple[str, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict:
        """全基本类型字典（JSON 可序列化）。"""
        return {
            "as_of": self.as_of,
            "entries": [e.to_dict() for e in self.entries],
            "capacity": self.capacity,
            "actual_size": self.actual_size,
            "truncated_out": list(self.truncated_out),
            "vetoed_symbols": list(self.vetoed_symbols),
            "notes": list(self.notes),
        }


def _priority_key(cand: PoolCandidateInput) -> tuple:
    """顺位最优比较键（越小越优；tie-break 链全确定无平票）。

    rank_score 降 → source_rank 升(None=+inf) → sleeve 定义序 → symbol 字典序。
    """
    sr = float(cand.source_rank) if cand.source_rank is not None else math.inf
    return (-cand.rank_score, sr, _SLEEVE_INDEX[cand.sleeve], cand.symbol)


def _final_sort_key(entry: FinalPoolEntry) -> tuple:
    """最终排序键：未否决在前按顺位分降序，vetoed 沉底留痕（内部同确定序）。"""
    sr = float(entry.source_rank) if entry.source_rank is not None else math.inf
    return (
        1 if entry.vetoed else 0,
        -entry.rank_score,
        sr,
        _SLEEVE_INDEX[entry.best_sleeve],
        entry.symbol,
    )


def _collect_and_dedupe(
    dual_pool_candidates: Iterable[PoolCandidateInput],
    strategy_chain_candidates: Iterable[PoolCandidateInput],
) -> tuple[dict[str, PoolCandidateInput], dict[str, list[str]]]:
    """收集与去重：完全重复 (symbol,sleeve) 对=fail-closed；跨束同 symbol 异 sleeve=按顺位最优保留。"""
    seen_pairs: set[tuple[str, str]] = set()
    best_by_symbol: dict[str, PoolCandidateInput] = {}
    sleeves_by_symbol: dict[str, list[str]] = {}
    for bundle in (dual_pool_candidates, strategy_chain_candidates):
        for cand in bundle:
            pair = (cand.symbol, cand.sleeve)
            if pair in seen_pairs:
                raise CandidatePoolInputError(
                    f"完全重复 (symbol,sleeve) 对: {pair}（上游契约违反或同源束劈参数注入）"
                )
            seen_pairs.add(pair)
            if cand.symbol in best_by_symbol:
                sleeves_by_symbol[cand.symbol].append(cand.sleeve)
                if _priority_key(cand) < _priority_key(best_by_symbol[cand.symbol]):
                    best_by_symbol[cand.symbol] = cand
            else:
                best_by_symbol[cand.symbol] = cand
                sleeves_by_symbol[cand.symbol] = [cand.sleeve]
    return best_by_symbol, sleeves_by_symbol


def _merge_veto_marks(veto_marks: Iterable[VetoMark]) -> dict[str, list[str]]:
    """否决后清单标记：重复 symbol → reasons 合并去重保序（否决记录天然可叠加）。"""
    veto_reasons: dict[str, list[str]] = {}
    for mark in veto_marks:
        existing = veto_reasons.get(mark.symbol)
        if existing is None:
            veto_reasons[mark.symbol] = list(mark.reasons)
        else:
            for r in mark.reasons:
                if r not in existing:
                    existing.append(r)
    return veto_reasons


def _build_entries(
    best_by_symbol: dict[str, PoolCandidateInput],
    sleeves_by_symbol: dict[str, list[str]],
    veto_reasons: dict[str, list[str]],
) -> list[FinalPoolEntry]:
    """组装条目：sleeves 按定义序合并去重；否决只标记不剔除。"""
    entries: list[FinalPoolEntry] = []
    for symbol in best_by_symbol:
        cand = best_by_symbol[symbol]
        mark_reasons = veto_reasons.get(symbol)
        sleeves = tuple(s.value for s in SLEEVE_ORDER if s.value in sleeves_by_symbol[symbol])
        entries.append(
            FinalPoolEntry(
                symbol=symbol,
                sleeves=sleeves,
                best_sleeve=cand.sleeve,
                rank_score=cand.rank_score,
                source_rank=cand.source_rank,
                vetoed=mark_reasons is not None,
                veto_reasons=tuple(mark_reasons) if mark_reasons is not None else (),
                tier_slot=None,
            )
        )
    return entries


def aggregate_candidate_pool(
    dual_pool_candidates: Iterable[PoolCandidateInput],
    strategy_chain_candidates: Iterable[PoolCandidateInput],
    veto_marks: Iterable[VetoMark],
    as_of: str,
    config: CandidatePoolConfig | None = None,
) -> FinalCandidatePool:
    """聚合主入口：三来源合并 → 同 symbol 去重（保留顺位最优）→ 顺位排序 → 容量截断。

    Args:
        dual_pool_candidates: 双池合流候选（短线池/波段池产出，每条自带 sleeve 标签）。
        strategy_chain_candidates: 策略链候选（打板/多因子/事件链产出，TDM-E-L3-07-1/2/3 feed 边）。
        veto_marks: 否决后清单标记（negative_veto 否决裁决留痕注入——只标记不剔除）。
        as_of: 交易日标签（审计透传，本件无墙钟）。
        config: 容量配置（None=默认 10-20，真源=TDM-E-L3-08 algo_note）。

    Returns:
        FinalCandidatePool（frozen；entries=未否决在前按顺位分降序+vetoed 沉底留痕）。

    Raises:
        CandidatePoolInputError: 输入非法（fail-closed）；空候选来源返回空池（fail-open）。
    """
    if not as_of or not as_of.strip():
        raise CandidatePoolInputError("as_of 为空（审计字段必须留痕）")
    cfg = config or CandidatePoolConfig()

    best_by_symbol, sleeves_by_symbol = _collect_and_dedupe(dual_pool_candidates, strategy_chain_candidates)
    veto_reasons = _merge_veto_marks(veto_marks)

    if not best_by_symbol:
        # 空候选来源 → 空池（fail-open），否决留痕照常透出（不丢）
        notes = ["候选来源全空 → 空池（fail-open）"]
        if veto_reasons:
            notes.append(f"否决留痕 {len(veto_reasons)} 条（无候选可标记，仅透出清单）")
        return FinalCandidatePool(
            as_of=as_of,
            entries=(),
            capacity=cfg.max_size,
            actual_size=0,
            truncated_out=(),
            vetoed_symbols=tuple(sorted(veto_reasons)),
            notes=tuple(notes),
        )

    entries = _build_entries(best_by_symbol, sleeves_by_symbol, veto_reasons)

    # ── 最终排序：未否决在前按顺位分降序，vetoed 沉底留痕 ──
    entries.sort(key=_final_sort_key)

    # ── 容量截断：上限截断按顺位分保留；vetoed 不占容量；不足下限不硬凑 ──
    notes: list[str] = []
    qualified = [e for e in entries if not e.vetoed]
    truncated_out: list[str] = []
    if len(qualified) > cfg.max_size:
        truncated_out = [e.symbol for e in qualified[cfg.max_size:]]
        kept = qualified[: cfg.max_size]
        notes.append(
            f"容量截断：未否决 {len(qualified)} 只 > 上限 {cfg.max_size}，"
            f"按顺位分保留前 {cfg.max_size} 只"
        )
    else:
        kept = qualified
        if len(qualified) < cfg.min_size:
            notes.append(f"未否决候选 {len(qualified)} 只 < 下限 {cfg.min_size}，不硬凑（fail-open）")
    if veto_reasons:
        notes.append(f"否决标记 {len(veto_reasons)} 条（不占容量、沉底留痕）")
    if truncated_out:
        notes.append(f"截断出池 {len(truncated_out)} 只（可喂 L3-09 Tier3 雷达池）")

    # 最终池 = 保留段 + vetoed 沉底留痕段（截断项不入池，只进 truncated_out）
    final_entries = tuple(list(kept) + [e for e in entries if e.vetoed])
    return FinalCandidatePool(
        as_of=as_of,
        entries=final_entries,
        capacity=cfg.max_size,
        actual_size=len(kept),
        truncated_out=tuple(truncated_out),
        vetoed_symbols=tuple(sorted(veto_reasons)),
        notes=tuple(notes),
    )


