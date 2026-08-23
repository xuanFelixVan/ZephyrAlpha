# [BLUEPRINT] MOD-SIG-066 | 待统筹登记（缺口总账 GAP-F-06 + 45号作战手册 §4 W1）
# [MODULE] zephyr.signal_ashare.war_pool_generator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.mainline_probability（MOD-SIG-064 复用）; zephyr.signal_ashare.mainline_candidates（MOD-SIG-061 复用）; zephyr.signal_ashare.sector_leader（MOD-SIG-062 复用）
# [CONSUMERS] 作战室 W1 今日作战池条（2~3 票，池外不碰）; zephyr.plan_engine.sit_out_list（MOD-PLAN-014 池外规则真源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 交集纪律：主线候选板块龙头（结构腿）×个股催化剂（催化腿）交集才入池，池外不碰；空交集→空池+注解不强行出池；主线概率缺维（None）按中性 50 参与合成不拉低；出池 ≤ pool_target（默认 3）；无主线混沌/064 降级→空池；观测层消费不接交易；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-06 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 催化剂 strength 越界/config 非法/trade_date 非法→ValueError（fail-closed）；催化剂 provider 异常→空催化腿降级 notes 留痕不抛
# [TESTS] tests/signal_ashare/test_war_pool_generator.py
# [A_module] module_id=MOD-SIG-066 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""WarPoolGenerator — 作战池生成器 (MOD-SIG-066)

缺口总账 GAP-F-06 落码：作战室 W1"今日作战池 2~3 票"（45号 §4 W1：刻意小的
作战池，"催化剂×结构"交集票，池外不碰——注意力也是风险预算）。

两腿交集（机构五件套②契约）：
    - 结构腿：主线候选板块（MOD-SIG-064 主线概率榜 / MOD-SIG-061 候选榜适配器）
      的龙头（MOD-SIG-062 leader；config.include_backbones 可放中军补位）；
    - 催化腿：个股催化剂（业绩预告/新闻事件/政策等，catalyst_provider 注入——
      新闻页预期差标签/事件日历实例接线点，未接线→空催化腿→空池不强行出票）。

合成评分（静态权重 MVP，初拍待实盘标定）：
    pool_score = w_role×role_score(0-100, MOD-SIG-062 五维合成)
               + w_mainline×(mainline_pct 或中性 50)
               + w_catalyst×(catalyst_strength×100，多催化剂取 max 全量留痕)

不做什么：不出方向/点位（观测层）/不强行出池（交集空=空池）/催化剂数据
         源采集不在本模块（provider 注入位）。

依据: 缺口总账 GAP-F-06；45_warroom_playbook §3.3②/§4 W1
SSoT: depgraph MOD-SIG-066（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 主线板块清单（064 概率榜或 061 候选榜适配器产出）
#   fields: (sector_code, sector_name, mainline_pct|None)
# - id: I2
#   name: 龙头分组（MOD-SIG-062 SectorRoleGroup）
#   fields: sector_code/leader/backbones（StockRoleEntry: symbol/role/score/consec_limit）
# - id: I3
#   name: 个股催化剂（catalyst_provider 注入）
#   fields: symbol/catalyst_type/strength/source/name
# 层: 算法
# - id: A1
#   name_zh: 结构×催化交集
#   desc: 主线板块龙头（可放中军）∩ 催化剂标的（strength≥min 门控）
# - id: A2
#   name_zh: 三维加权合成排序
#   desc: pool_score=0.5×角色分+0.3×主线分(缺维中性50)+0.2×催化剂分；降序取 pool_target
# 层: 输出
# - id: O1
#   name_zh: WarPoolResult
#   intro: date/entries(symbol/sector/role/三维分/催化剂链/reasons)/no_pool_flag/degraded/annotations/notes
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> A1
# I3 --> A1
# A1,I1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final

from zephyr.signal_ashare.mainline_candidates import MainlineCandidatesResult
from zephyr.signal_ashare.mainline_probability import (
    MainlineProbabilityResult,
    compute_mainline_probability,
)
from zephyr.signal_ashare.sector_leader import (
    SectorLeaderBoard,
    SectorRoleGroup,
    identify_sector_leaders,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "CatalystRecord",
    "WarPoolConfig",
    "WarPoolEntry",
    "WarPoolResult",
    "generate_war_pool",
    "sectors_from_candidates",
    "sectors_from_probability",
    "select_war_pool",
]

#: 主线概率缺维时的中性参与分（不拉低不出伪分，与 064 缺维重归一同哲学）
_NEUTRAL_MAINLINE_PCT: Final = 50.0


@dataclass(frozen=True, slots=True)
class CatalystRecord:
    """个股催化剂记录（催化腿输入，provider 注入——新闻/事件/业绩等数据源接线点）。

    Attributes:
        symbol: 个股代码（canonical，如 600001.SH）
        catalyst_type: 催化剂类型（EARNINGS/NEWS/POLICY/...，自由字符串留痕）
        strength: 催化强度 ∈ [0,1]（多催化剂取 max 参与合成，全量留痕）
        source: 数据源标识（如 news_symbol_linker/event_calendar，留痕可回查）
        name: 催化剂一句话描述（中文可审计）
    """

    symbol: str
    catalyst_type: str
    strength: float
    source: str = "unknown"
    name: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError(f"symbol 非法（须非空字符串）: {self.symbol!r}")
        if not (0.0 <= float(self.strength) <= 1.0):
            raise ValueError(f"strength 非法（须 ∈ [0,1]）: {self.strength!r}")
        if not isinstance(self.catalyst_type, str) or not self.catalyst_type.strip():
            raise ValueError(f"catalyst_type 非法（须非空字符串）: {self.catalyst_type!r}")


@dataclass(frozen=True, slots=True)
class WarPoolConfig:
    """作战池配置（静态权重 MVP 初拍值，待实盘标定）。

    Attributes:
        pool_target: 出池上限（45号 W1：2~3 票，默认 3）
        pool_min: 作战池规模下限（不足留痕 notes，不强行补票）
        include_backbones: 中军补位开关（默认 False=只龙头）
        min_catalyst_strength: 催化剂强度门控（低于视为无催化）
        w_role / w_mainline / w_catalyst: 三维合成权重
    """

    pool_target: int = 3
    pool_min: int = 2
    include_backbones: bool = False
    min_catalyst_strength: float = 0.0
    w_role: float = 0.5
    w_mainline: float = 0.3
    w_catalyst: float = 0.2

    def __post_init__(self) -> None:
        if self.pool_target <= 0:
            raise ValueError(f"pool_target 必须为正: {self.pool_target}")
        if self.pool_min < 0 or self.pool_min > self.pool_target:
            raise ValueError(f"pool_min 非法（须 ∈ [0, pool_target]）: {self.pool_min}")
        if not (0.0 <= float(self.min_catalyst_strength) <= 1.0):
            raise ValueError(f"min_catalyst_strength 非法（须 ∈ [0,1]）: {self.min_catalyst_strength!r}")
        for name in ("w_role", "w_mainline", "w_catalyst"):
            v = float(getattr(self, name))
            if v < 0:
                raise ValueError(f"{name} 非法（须非负）: {v!r}")
        if self.w_role + self.w_mainline + self.w_catalyst <= 0:
            raise ValueError("合成权重和必须为正")


@dataclass(frozen=True, slots=True)
class WarPoolEntry:
    """作战池条目（一票一行，理由链可审计）。"""

    symbol: str
    sector_code: str
    sector_name: str
    role: str  # leader / backbone
    mainline_pct: float | None  # 主线概率（064；None=缺维按中性 50 合成）
    role_score: float  # MOD-SIG-062 五维合成评分 0-100
    catalyst_strength: float  # 催化剂强度（多催化剂取 max）
    catalysts: list[str] = field(default_factory=list)  # 催化剂留痕（type:source:name）
    pool_score: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class WarPoolResult:
    """作战池输出契约（T 日盘后/T+1 盘前计算，观测层消费，不接交易）。"""

    date: str  # 数据日 YYYY-MM-DD
    entries: list[WarPoolEntry] = field(default_factory=list)
    no_pool_flag: bool = False  # 空交集/无主线/降级 → True（池外不碰日）
    degraded: bool = False  # 064 候选榜降级 → True（结果不可用于决策）
    annotations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return asdict(self)


# ------------------------------------------------------------------
# 适配器（064/061 → 统一主线板块清单）
# ------------------------------------------------------------------


def sectors_from_probability(result: MainlineProbabilityResult) -> list[tuple[str, str, float | None]]:
    """MOD-SIG-064 主线概率榜 → [(sector_code, sector_name, mainline_pct)]。"""
    return [(it.sector_code, it.sector_name, it.probability_pct) for it in result.items]


def sectors_from_candidates(result: MainlineCandidatesResult) -> list[tuple[str, str, float | None]]:
    """MOD-SIG-061 候选榜 → [(sector_code, sector_name, None)]（无概率维，中性合成）。"""
    return [(c.sector_code, c.sector_name, None) for c in result.candidates]


# ------------------------------------------------------------------
# 纯函数核心（不触库，可单测）
# ------------------------------------------------------------------


def select_war_pool(
    sectors: list[tuple[str, str, float | None]],
    groups: dict[str, SectorRoleGroup],
    catalysts: list[CatalystRecord],
    *,
    config: WarPoolConfig | None = None,
    trade_date: str = "",
) -> WarPoolResult:
    """作战池挑选核（纯函数）：结构腿 × 催化腿交集 → 三维合成 Top pool_target。

    Args:
        sectors: 主线板块清单 [(sector_code, sector_name, mainline_pct|None)]。
        groups: 板块龙头分组 {sector_code: SectorRoleGroup}（MOD-SIG-062 产出）。
        catalysts: 个股催化剂清单（provider 装配产出；空 → 空池）。
        config: 配置（None 用默认静态权重 MVP）。
        trade_date: 数据日（留痕）。

    Returns:
        WarPoolResult；空交集 → no_pool_flag=True + 注解（不强行出池）。
    """
    cfg = config or WarPoolConfig()
    date_str = trade_date or datetime.date.today().isoformat()
    notes: list[str] = []
    annotations: list[str] = []

    if not sectors:
        annotations.append("主线板块清单空（无主线混沌/候选榜空），作战池空（不强行出池）")
        return WarPoolResult(date=date_str, no_pool_flag=True, annotations=annotations, notes=notes)

    # 催化腿：strength 门控 + 按 symbol 分组（多催化剂取 max，全量留痕）
    cat_by_symbol: dict[str, list[CatalystRecord]] = {}
    for c in catalysts:
        if c.strength >= cfg.min_catalyst_strength:
            cat_by_symbol.setdefault(c.symbol, []).append(c)
    if not cat_by_symbol:
        annotations.append("催化剂腿为空（provider 未接线/当日无催化剂），交集空 → 作战池空（池外不碰）")
        notes.append("催化剂数据源待接线（news_symbol_linker/event_calendar 实例），当前空催化腿降级")
        return WarPoolResult(date=date_str, no_pool_flag=True, annotations=annotations, notes=notes)

    # 结构腿：主线板块龙头（可放中军）× 催化腿交集
    entries: list[WarPoolEntry] = []
    for sector_code, sector_name, pct in sectors:
        group = groups.get(sector_code)
        if group is None:
            notes.append(f"板块 {sector_code} 无龙头分组（梯队榜缺该板块），跳过")
            continue
        role_entries = []
        if group.leader is not None:
            role_entries.append(group.leader)
        if cfg.include_backbones:
            role_entries.extend(group.backbones)
        for re_ in role_entries:
            cats = cat_by_symbol.get(re_.symbol)
            if not cats:
                continue  # 无催化剂 → 交集外
            cat_strength = max(c.strength for c in cats)
            mainline_component = pct if pct is not None else _NEUTRAL_MAINLINE_PCT
            pool_score = round(
                cfg.w_role * re_.score + cfg.w_mainline * mainline_component + cfg.w_catalyst * cat_strength * 100.0,
                4,
            )
            entries.append(
                WarPoolEntry(
                    symbol=re_.symbol,
                    sector_code=sector_code,
                    sector_name=sector_name,
                    role=re_.role,
                    mainline_pct=pct,
                    role_score=re_.score,
                    catalyst_strength=cat_strength,
                    catalysts=[f"{c.catalyst_type}:{c.source}:{c.name}".rstrip(":") for c in cats],
                    pool_score=pool_score,
                    reasons=[
                        f"主线板块={sector_name}（概率{ pct if pct is not None else '缺维中性' }）",
                        f"结构={re_.role}（评分{re_.score:.1f}，连板{re_.consec_limit}）",
                        f"催化剂×{len(cats)}（强度{cat_strength:.2f}）",
                    ],
                )
            )

    if not entries:
        annotations.append("主线龙头与催化剂交集为空，作战池空（池外不碰，不强行出池）")
        return WarPoolResult(date=date_str, no_pool_flag=True, annotations=annotations, notes=notes)

    entries.sort(key=lambda e: (e.pool_score, e.symbol), reverse=True)
    entries = entries[: cfg.pool_target]
    if len(entries) < cfg.pool_min:
        notes.append(f"作战池仅 {len(entries)} 票，不足 pool_min={cfg.pool_min} 下限（交集稀薄，留痕不补票）")
    annotations.append(f"今日作战池 {len(entries)} 票已出（主线×催化交集，池外不碰）")
    return WarPoolResult(date=date_str, entries=entries, annotations=annotations, notes=notes)


# ------------------------------------------------------------------
# 装配层（064/062 现算或注入 + 催化剂 provider）
# ------------------------------------------------------------------


def generate_war_pool(
    trade_date: str | datetime.date | None = None,
    ch_client: Any | None = None,
    probability_result: MainlineProbabilityResult | None = None,
    leader_board: SectorLeaderBoard | None = None,
    catalyst_provider: Callable[[str], list[CatalystRecord]] | None = None,
    config: WarPoolConfig | None = None,
) -> WarPoolResult:
    """主入口：主线候选（064/062 产出）× 个股催化剂交集 → 2~3 票作战池。

    Args:
        trade_date: 数据日；None 时由 064 候选榜取最新数据日（PIT 口径）。
        ch_client: clickhouse-driver 鸭子类型（064/062 现算时透传）；注入结果时无用。
        probability_result: 预计算 064 概率榜（注入位）；None 现算。
        leader_board: 预计算 062 龙头榜（注入位）；None 现算。
        catalyst_provider: 催化剂数据源注入位 callable(trade_date)->list[CatalystRecord]；
            None → 空催化腿（数据源未接线，空池留痕）。
        config: 配置（None 用默认）。

    Returns:
        WarPoolResult；064 degraded/no_mainline → 空池 degraded/注解透传。
    """
    prob = probability_result or compute_mainline_probability(trade_date, ch_client=ch_client)
    date_str = prob.date
    if prob.degraded:
        return WarPoolResult(
            date=date_str,
            no_pool_flag=True,
            degraded=True,
            annotations=["主线概率榜降级，作战池不出票"],
            notes=list(prob.notes),
        )
    if prob.no_mainline_flag or not prob.items:
        return WarPoolResult(
            date=date_str,
            no_pool_flag=True,
            annotations=["无主线混沌/概率榜空，作战池空（池外不碰日）"],
            notes=list(prob.notes),
        )

    board = leader_board or identify_sector_leaders(date_str, ch_client=ch_client)
    groups: dict[str, SectorRoleGroup] = {g.sector_code: g for g in board.sectors}
    notes: list[str] = []
    if board.degraded:
        notes.append(f"龙头榜降级（结构腿缺位风险）: {'; '.join(board.notes)}")

    catalysts: list[CatalystRecord] = []
    if catalyst_provider is not None:
        try:
            catalysts = list(catalyst_provider(date_str))
        except Exception as e:  # noqa: BLE001 — 催化剂源异常独立降级不炸
            notes.append(f"催化剂 provider 异常，空催化腿降级: {e!r}")
            catalysts = []

    result = select_war_pool(
        sectors_from_probability(prob),
        groups,
        catalysts,
        config=config,
        trade_date=date_str,
    )
    if notes:
        result = WarPoolResult(
            date=result.date,
            entries=result.entries,
            no_pool_flag=result.no_pool_flag,
            degraded=result.degraded,
            annotations=result.annotations,
            notes=[*result.notes, *notes],
        )
    return result
