# [BLUEPRINT] MOD-SIG-152 | docs/_working/decision_map_campaign/links/L04_stock_wire/SKEL.md §3（M-41/D22 落地）+ L04-C02（LK-04 通电侧带）
# [MODULE] zephyr.signal_ashare.core.candidate_pool_snapshot
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.core.candidate_pool_aggregator（纯函数聚合核复用，零改）; zephyr.data.ch_writer（lazy，落表正门）; zephyr.data.provider_base（FetchResult，lazy）
# [CONSUMERS] zephyr.strategy_pipeline.daily_gate_snapshot（**生产触发方**：collect_gate_snapshot L3 environment_switch 采集点侧带 _collect_candidate_pool，盘后日循环逐交易日驱动 run_pool_batch_for_day，落表经 ch_writer 正门）；TDM-E-L4 买卖/P2-02 做T调度/P1 体检/BM-BUY-03/整装回测（PIT 真读消费面，载体解锁后逐批接线，现均未接）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数核零时钟零 IO（pool_to_rows/run_daily_batch 不取 now()/time.time()，ingest_ts 由 DDL DEFAULT now() 承载 RULE-SCHEMA-TZ，elapsed_sec 恒 0.0——daban_load_producer 同款）；真源唯一：表结构以 schemas/categories/market/market_stock_candidate_pool.py DDL 为唯一真源，POOL_INSERT_COLUMNS 与其 INSERT_COLUMNS 严格同序 16 列；否决只标记不剔除（裁决在上游 negative_veto MOD-SIG-137，本件留痕不重复裁决，vetoed 行沉底照写）；rank_score 原值透传禁二次归一（上游分数体系不一，口径统一归调用方）；不可产字段显式缺省（tier_slot/conduction_adj/缺省成分=None/空 dict 留痕，禁拍 1.0/0 冒充真值）；空池日=零行 fail-visible warning 非静默（daban 先例同款：空≠0 假信号）；三来源候选注入制（零 import 上游三件，鸭型镜像经 PoolCandidateInput/VetoMark，注册制 PoolBundleSource 供后续 sleeve 接线，无注册源=空池如实缺省）；CH 全程 ch_writer 正门（禁裸 SQL/裸 connect）；环境开关只作快照元留痕（来源标尺），链启停过滤归注入源（L3-06 裁决在上游）
# [MODIFY-GUARD] 地图节点 TDM-E-L3-08 持久化腿（落图归 TDM 增长轨接线，本件不自行落图）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] day 非 ISO 日期/池对象缺 as_of -> ValueError（fail-closed）；聚合输入非法 -> CandidatePoolInputError（透传聚合器契约）；空池 -> 零行 FetchResult + logger.warning（fail-visible 非静默）；persist 落表经 ch_writer.write_result（error 非 None 返回 False，不抛）；run_pool_batch_for_day 永不外抛（任何异常折 status=absent 留痕——侧带不炸门快照）
# [TESTS] tests/signal_ashare/test_candidate_pool_snapshot.py
# [A_module] module_id=MOD-SIG-152 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] candidate-pool-snapshot-l04c01-20260925
"""CandidatePoolSnapshot — 当日候选池快照日批生产者（L04-C01，M-41/D22 载体落地产物）。

背景（L04 作业簿 W2③/W7② 实证）：
    TDM-E-L3 十五节点主链（漏斗→否决→聚合→Tier）码件全在，但产出"纯内存/回测
    内存话，无持久化"——最终候选池（10-20 只，带 sleeve 标签+顺位分+否决标记）只在
    回测内存里活一瞬，L4 买卖/P2-02 做T调度/P1 体检/BM-BUY-03/整装回测全部吃不到
    真值全史（D22 池成员持久化欠账，外审 M-41）。本模块是该载体的**批产生产者**：
    逐交易日把聚合器 FinalCandidatePool 物化为 c1_market.stock_candidate_pool 快照行
    （trade_date×stage×symbol 一行/池内标的），落表经 ch_writer 正门。

链路与边界（daban_load_producer 先例全款复刻，零新调度器）：
    事件触发：盘后日循环 daily_gate_snapshot.collect_gate_snapshot 的 L3
    environment_switch 采集点侧带（L04-C02 最小侵入：五层门快照契约不变，pool 为
    附加键不进 absent_layers 降级矩阵）→ run_pool_batch_for_day(day) →
    aggregate_candidate_pool（聚合器纯函数复用，零改）→ pool_to_rows → persist。
    生成器零时钟：纯函数路径无 now()/time.time()；ingest_ts 由 DDL DEFAULT 承载。
    三来源注入制：dual_pool/strategy_chain/veto_marks 经 PoolCandidateInput/VetoMark
    鸭型镜像注入（聚合器同款零 import 契约）；后续 sleeve 生产者接线走
    register_pool_bundle_source 注册制（本件不替上游拍候选，无源=空池如实缺省）。

字段口径（细节见 DDL 文件头）：
    sleeve=best_sleeve 主标签｜sleeves=合流全集 JSON｜rank_score 原值透传｜
    pool_rank=最终顺位 1-based（未否决在前按顺位分降序、vetoed 沉底）｜
    vetoed+veto_reasons=否决留痕｜tier_slot/conduction_adj=预留显式缺省｜
    score_components=评分明细 JSON｜snapshot_meta=快照元 JSON（容量/截断/否决清单/
    环境开关六段×四开关/成交额代理——单表回放自足）。

PIT 消费契约：决策日 T 只读 max(trade_date) < T 分区（shift(1) 防未来函数；
    池成员与顺位收盘后才知）。ReplacingMergeTree (trade_date, stage, symbol)
    同键重放幂等——同日重跑/升版重推导安全。

SSoT: docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/SKEL.md §3 L04-C01/C02
     + schemas/categories/market/market_stock_candidate_pool.py（表结构唯一真源）
     + ulib3b_demand_gap_ledger.md:47（D22）/ trading_decision_map.yaml L3-08/09

# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/candidate_pool_snapshot.yaml
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Final, Mapping, Protocol, Sequence, runtime_checkable

from zephyr.signal_ashare.core.candidate_pool_aggregator import (
    FinalCandidatePool,
    PoolCandidateInput,
    VetoMark,
    aggregate_candidate_pool,
)

if TYPE_CHECKING:
    from zephyr.data.provider_base import FetchResult

_logger = logging.getLogger(__name__)

#: 读回通道协议（测试注入 fake reader；None=DatabaseService reader 角色，禁裸 connect）
Reader = Callable[[str], Any]

#: 目标表（表结构真源 = schemas/categories/market/market_stock_candidate_pool.py）
_TARGET_TABLE: Final = "c1_market.stock_candidate_pool"
CATEGORY_ID: Final = "market_stock_candidate_pool"
#: 语义化版本（口径变更必升版：列语义/顺位口径/否决口径变更均须 bump）
POOL_VERSION: Final = "v1"
_DATA_SOURCE: Final = "candidate_pool_aggregator"
#: 快照时点（盘后日批=收盘定稿；pre_open/intraday_vN 预留，真源=DDL stage 列注）
DEFAULT_STAGE: Final = "close_final"

#: INSERT 列序——与 DDL INSERT_COLUMNS 严格同序 16 列（不含 exchange/symbol_canonical
#: MATERIALIZED 与 DEFAULT ingest_ts；ch_writer.write_result 自动过滤 MATERIALIZED）。
POOL_INSERT_COLUMNS: Final = (
    "trade_date",
    "stage",
    "symbol",
    "sleeve",
    "sleeves",
    "rank_score",
    "source_rank",
    "pool_rank",
    "vetoed",
    "veto_reasons",
    "tier_slot",
    "conduction_adj",
    "score_components",
    "snapshot_meta",
    "version",
    "data_source",
)


# ---------------------------------------------------------------------------
# 纯函数层（零时钟、零 IO）——池 → 快照行
# ---------------------------------------------------------------------------


def _compact_json(value: object) -> str:
    """确定性紧凑 JSON（sort_keys+ensure_ascii=False；同输入必同串，重放幂等前提）。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _iso_day_or_raise(day: str) -> str:
    """校验并归一业务日为 ISO 'YYYY-MM-DD'（非法 ValueError fail-closed；零墙钟）。"""
    if isinstance(day, datetime.datetime):
        return day.date().isoformat()
    if isinstance(day, datetime.date):
        return day.isoformat()
    try:
        return datetime.date.fromisoformat(str(day)[:10]).isoformat()
    except ValueError as exc:
        raise ValueError(f"业务日非法（须 ISO YYYY-MM-DD）: {day!r}") from exc


def build_snapshot_meta(
    pool: FinalCandidatePool,
    *,
    market_state: str | None = None,
    turnover_yi: float | None = None,
    switches: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """快照元 dict（单表回放自足：容量/截断/否决清单/聚合注记/环境开关来源标尺）。

    Args:
        pool: 聚合器产物（capacity/actual_size/truncated_out/vetoed_symbols/notes 透传）。
        market_state: 六段状态名（L3-06 查表轴回显；None=当日未评）。
        turnover_yi: 两市成交额亿元代理（None=代理缺席，诚实留痕不编 0）。
        switches: environment_switches.to_dict()（六段×四开关；None=未评/缺席）。
    """
    env: dict[str, Any] = {
        "market_state": market_state,
        "turnover_yi": turnover_yi,
        "switches": dict(switches) if switches is not None else None,
    }
    return {
        "capacity": pool.capacity,
        "actual_size": pool.actual_size,
        "truncated_out": list(pool.truncated_out),
        "vetoed_symbols": list(pool.vetoed_symbols),
        "notes": list(pool.notes),
        "env": env,
    }


@dataclass(frozen=True)
class PoolSnapshotParams:
    """快照产线参数束（pool_to_rows/run_daily_batch/run_pool_batch_for_day 共用）。

    §5.150 长参数列表治本：8 个产线旋钮收编单一参数对象（None=显式缺省，
    禁拍 1.0/0 冒充中性——与各字段 INVARIANTS 同口径）。
    """

    stage: str = DEFAULT_STAGE
    conduction_adj: float | None = None
    score_components_by_symbol: Mapping[str, Mapping[str, Any]] | None = None
    market_state: str | None = None
    turnover_yi: float | None = None
    switches: Mapping[str, Any] | None = None
    version: str = POOL_VERSION
    data_source: str = _DATA_SOURCE


def pool_to_rows(pool: FinalCandidatePool, params: PoolSnapshotParams | None = None) -> list[dict[str, Any]]:
    """FinalCandidatePool → 快照行 dict 列表（键=POOL_INSERT_COLUMNS；纯函数零时钟零 IO）。

    行序=pool.entries 聚合器最终序（未否决在前按顺位分降序、vetoed 沉底留痕），
    pool_rank=1-based 位置（重放 L4"只取未否决顺位前段"消费的依据）。
    score_components_by_symbol={symbol: 评分明细 dict}（调用方注入位；缺=空 dict 留痕）。
    conduction_adj 透传（W0 两字段接线后回填；None=显式缺省禁拍 1.0 冒充中性）。
    """
    p = params or PoolSnapshotParams()
    stage = p.stage
    conduction_adj = p.conduction_adj
    score_components_by_symbol = p.score_components_by_symbol
    market_state = p.market_state
    turnover_yi = p.turnover_yi
    switches = p.switches
    version = p.version
    data_source = p.data_source
    day = _iso_day_or_raise(pool.as_of)
    if not stage or not str(stage).strip():
        raise ValueError("stage 为空（快照时点必须留痕）")
    meta_json = _compact_json(
        build_snapshot_meta(pool, market_state=market_state, turnover_yi=turnover_yi, switches=switches)
    )
    components = score_components_by_symbol or {}
    rows: list[dict[str, Any]] = []
    for pos, entry in enumerate(pool.entries, start=1):
        rows.append(
            {
                "trade_date": day,
                "stage": str(stage),
                "symbol": str(entry.symbol),
                "sleeve": str(entry.best_sleeve),
                "sleeves": _compact_json(list(entry.sleeves)),
                "rank_score": float(entry.rank_score),
                "source_rank": None if entry.source_rank is None else int(entry.source_rank),
                "pool_rank": pos,
                "vetoed": 1 if entry.vetoed else 0,
                "veto_reasons": _compact_json(list(entry.veto_reasons)),
                "tier_slot": None if entry.tier_slot is None else int(entry.tier_slot),
                "conduction_adj": None if conduction_adj is None else float(conduction_adj),
                "score_components": _compact_json(components.get(entry.symbol, {})),
                "snapshot_meta": meta_json,
                "version": str(version),
                "data_source": str(data_source),
            }
        )
    return rows


def pool_rows_to_tuples(rows: Sequence[Mapping[str, Any]]) -> list[tuple]:
    """快照行 dict → 与 POOL_INSERT_COLUMNS 同序的 tuple 列表（供 FetchResult.rows）。"""
    return [tuple(row.get(col) for col in POOL_INSERT_COLUMNS) for row in rows]


# ---------------------------------------------------------------------------
# 三来源注入制（零 import 上游三件；后续 sleeve 生产者经注册制接线）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PoolBundles:
    """单日三来源候选束（聚合器三入参的打包形态 + 来源注记）。"""

    dual_pool_candidates: tuple[PoolCandidateInput, ...] = ()
    strategy_chain_candidates: tuple[PoolCandidateInput, ...] = ()
    veto_marks: tuple[VetoMark, ...] = ()
    notes: tuple[str, ...] = field(default=())


@runtime_checkable
class PoolBundleSource(Protocol):
    """候选来源协议（生产=注册制来源，测试=fake 注入 run_pool_batch_for_day）。"""

    def fetch_bundles(self, day: str) -> PoolBundles: ...


_BUNDLE_SOURCES: list[PoolBundleSource] = []


def register_pool_bundle_source(source: PoolBundleSource) -> None:
    """注册候选来源（幂等：同对象重复注册忽略）。后续 sleeve 接线唯一入口。"""
    if not callable(getattr(source, "fetch_bundles", None)):
        kind = type(source).__qualname__
        raise TypeError(f"候选来源须实现 fetch_bundles(day)->PoolBundles: 收到 {kind}")
    if any(existing is source for existing in _BUNDLE_SOURCES):
        return
    _BUNDLE_SOURCES.append(source)


def registered_bundle_sources() -> tuple[PoolBundleSource, ...]:
    """已注册来源只读视图（测试隔离 save/restore 用）。"""
    return tuple(_BUNDLE_SOURCES)


def clear_bundle_sources() -> None:
    """清空注册表（测试隔离专用；生产路径不调用）。"""
    _BUNDLE_SOURCES.clear()


def collect_bundles(day: str) -> PoolBundles:
    """逐注册来源采集三来源候选束并合并（确定序=注册序）。

    无注册源 → 空 PoolBundles + 注记（如实缺省非静默：三来源 sleeve 生产者
    未接线是 L04-C02 全链串接的既知现状，本件不替上游拍候选）。
    单来源异常不炸整批：该来源折空束+注记留痕（fail-open，对齐门快照缺席语义）。
    """
    sources = registered_bundle_sources()
    if not sources:
        return PoolBundles(
            notes=(
                "无已注册候选来源（dual_pool/strategy_chain/veto 三来源生产者未接线，"
                "L04-C02 全链串接另案）→ 空池如实缺省",
            )
        )
    duals: list[PoolCandidateInput] = []
    chains: list[PoolCandidateInput] = []
    vetoes: list[VetoMark] = []
    notes: list[str] = []
    for src in sources:
        name = type(src).__name__
        try:
            bundles = src.fetch_bundles(day)
        except Exception as exc:  # noqa: BLE001 — 单来源异常折空束留痕（不炸整批）
            notes.append(f"来源 {name} 采集异常折空束: {type(exc).__name__}")
            continue
        duals.extend(bundles.dual_pool_candidates)
        chains.extend(bundles.strategy_chain_candidates)
        vetoes.extend(bundles.veto_marks)
        notes.append(
            f"来源 {name}: dual={len(bundles.dual_pool_candidates)} "
            f"chain={len(bundles.strategy_chain_candidates)} "
            f"veto={len(bundles.veto_marks)}"
        )
        notes.extend(bundles.notes)
    return PoolBundles(
        dual_pool_candidates=tuple(duals),
        strategy_chain_candidates=tuple(chains),
        veto_marks=tuple(vetoes),
        notes=tuple(notes),
    )


# ---------------------------------------------------------------------------
# 批产编排（生产者入口——由 daily_gate_snapshot L3 采集点侧带触发；本模块零时钟）
# ---------------------------------------------------------------------------


def run_daily_batch(pool: FinalCandidatePool, params: PoolSnapshotParams | None = None) -> FetchResult:
    """当日池 → stock_candidate_pool 快照 FetchResult（不触发写、不调时钟）。

    空池日（entries 全空）→ 零行 FetchResult + WARNING（fail-visible：空≠0 假信号，
    daban 先例同款；当日无候选/来源未接线均落此分支，非静默）。
    """
    from zephyr.data.provider_base import FetchResult

    p = params or PoolSnapshotParams()
    stage = p.stage
    day = _iso_day_or_raise(pool.as_of)
    rows = pool_to_rows(pool, params=p)
    tuples = pool_rows_to_tuples(rows)
    if not tuples:
        _logger.warning(
            "candidate_pool: %s stage=%s 空池（无候选或来源未接线）——零行快照，非静默",
            day,
            stage,
        )
    else:
        _logger.info(
            "candidate_pool: %s stage=%s 产 %d 快照行（actual_size=%d vetoed=%d truncated=%d）",
            day,
            stage,
            len(tuples),
            pool.actual_size,
            len(pool.vetoed_symbols),
            len(pool.truncated_out),
        )
    return FetchResult(
        table=_TARGET_TABLE,
        columns=list(POOL_INSERT_COLUMNS),
        rows=tuples,
        last_key=f"{day}|{stage}",
        elapsed_sec=0.0,
        rows_fetched=len(tuples),
    )


def _default_writer(result: FetchResult) -> bool:
    """落表正门（ch_writer.write_result：列过滤/MATERIALIZED 排除/本地落盘兜底内建）。"""
    from zephyr.data import ch_writer

    return ch_writer.write_result(result)


def persist(result: FetchResult, *, timeout: int = 600, writer: Callable[[FetchResult], bool] | None = None) -> bool:
    """快照 FetchResult → ClickHouse（生产落表入口；只读验证/测试经 writer 注入隔离）。"""
    ok = bool((writer or _default_writer)(result))
    if not ok:
        _logger.warning("candidate_pool: persist 失败 table=%s rows=%d", result.table, len(result.rows))
    return ok


def run_pool_batch_for_day(
    day: str,
    params: PoolSnapshotParams | None = None,
    *,
    bundle_source: PoolBundleSource | None = None,
    writer: Callable[[FetchResult], bool] | None = None,
) -> dict[str, Any]:
    """LK-04 通电入口：单日候选池采集→聚合→快照落表（永不外抛，侧带不炸门快照）。

    Args:
        day: 业务日 YYYY-MM-DD（fail-closed 校验；禁墙钟猜日）。
        market_state/turnover_yi/switches: L3 environment_switch 采集点已有产物透传
            （来源标尺留痕进 snapshot_meta；本件不重算不断言——只采不断言同款纪律）。
        conduction_adj: 传导调节分乘数注入位（W0 接线后回填；None=显式缺省）。
        bundle_source: 候选来源注入位（None=注册制 collect_bundles；测试注 fake 零全局态）。
        writer: 落表注入位（None=ch_writer 正门；测试注 fake 断言零生产写入）。

    Returns:
        {"status": "ok"|"empty", "trade_date", "stage", "pool_size", "actual_size",
         "vetoed", "rows", "persisted", "version", "notes"}（JSON 可序列化）。
        params: 产线参数束（stage/conduction_adj/market_state/turnover_yi/switches 等 8 旋钮）。
        status=empty：空池零行未落表（fail-visible 已在生产者侧 warning）。
    """
    try:
        p = params or PoolSnapshotParams()
        stage = p.stage
        d = _iso_day_or_raise(day)
        bundles = bundle_source.fetch_bundles(d) if bundle_source is not None else collect_bundles(d)
        pool = aggregate_candidate_pool(
            bundles.dual_pool_candidates,
            bundles.strategy_chain_candidates,
            bundles.veto_marks,
            as_of=d,
        )
        result = run_daily_batch(pool, params=p)
        if not result.rows:
            return {
                "status": "empty",
                "trade_date": d,
                "stage": stage,
                "pool_size": len(pool.entries),
                "actual_size": pool.actual_size,
                "vetoed": len(pool.vetoed_symbols),
                "vetoed_symbols": list(pool.vetoed_symbols),
                "rows": 0,
                "persisted": False,
                "version": POOL_VERSION,
                "notes": list(bundles.notes) + list(pool.notes),
            }
        persisted = persist(result, writer=writer)
        return {
            "status": "ok",
            "trade_date": d,
            "stage": stage,
            "pool_size": len(pool.entries),
            "actual_size": pool.actual_size,
            "vetoed": len(pool.vetoed_symbols),
            "vetoed_symbols": list(pool.vetoed_symbols),
            "rows": len(result.rows),
            "persisted": persisted,
            "version": POOL_VERSION,
            "notes": list(bundles.notes) + list(pool.notes),
        }
    except Exception as exc:  # noqa: BLE001 — 侧带 fail-open：缺席折结构留痕，不炸门快照
        _logger.warning("candidate_pool: %s 日批异常折 absent（fail-open）: %s", day, exc)
        return {"status": "absent", "error": type(exc).__name__, "trade_date": str(day)}


# ---------------------------------------------------------------------------
# PIT 读回（C01 验收"回放任一历史日可取当日池快照"；只读，禁裸 connect 走 resolve_reader）
# ---------------------------------------------------------------------------

_JSON_COLUMNS: Final = ("sleeves", "veto_reasons", "score_components", "snapshot_meta")
_STAGE_ALLOWED: Final = frozenset({"close_final", "pre_open"} | {f"intraday_v{n}" for n in range(1, 13)})
#: 读回 SQL 模板（§5.160.2 SQL 集中化；day/stage 经 fail-closed 校验后才可代入）
# 注意：SQL 字面量行带 noqa: bare-sql——bare_sql_gate 豁免抽取器（_extract_sql_constant_lines）
# 只认 ast.Assign（AnnAssign+Final 命名不豁免），而 MUTABLE-CONST-WITHOUT-FINAL 又强制 Final，
# 两 gate 夹缝处按 gate 处方走行级 noqa 豁免（SQL 已集中化为本模块 _SQL_* 常量真源，非裸散落）。
_SQL_POOL_LOAD_EXACT: Final = (
    "SELECT {cols} FROM {table} WHERE trade_date = '{day}' AND stage = '{stage}' ORDER BY pool_rank ASC"  # noqa: bare-sql  SQL 集中化模板常量（AnnAssign 豁免盲区，非裸散落）
)
_SQL_POOL_LOAD_PIT: Final = (
    "SELECT {cols} FROM {table} "  # noqa: bare-sql  SQL 集中化模板常量（AnnAssign 豁免盲区，非裸散落）
    "WHERE trade_date = (SELECT max(trade_date) FROM {table} WHERE trade_date < '{day}') "  # noqa: bare-sql  同上集中化模板常量（PIT 取决策日前最近一日）
    "AND stage = '{stage}' ORDER BY pool_rank ASC"
)
_SQL_POOL_LOAD_COLS: Final = ", ".join(POOL_INSERT_COLUMNS)


def load_pool_snapshot(
    day: str,
    *,
    mode: str = "exact",
    stage: str = DEFAULT_STAGE,
    reader: Reader | None = None,
) -> dict[str, Any]:
    """池快照读回 API（只读；fail-visible 缺席语义与供料端对齐）。

    Args:
        day: 业务日 YYYY-MM-DD（fail-closed ISO 校验）。
        mode: "exact"=回放当日快照（C01 验收口径）；"pit"=决策日 T 读
            max(trade_date) < T 最近分区（shift(1) 防未来函数，daban 先例同款）。
        stage: 快照时点（close_final 盘后定稿；封闭集校验防注入）。
        reader: 注入式只读通道（None=DatabaseService reader 角色）。

    Returns:
        {"status": "ok", "trade_date", "stage", "pool": [行 dict...]}；
        行键=POOL_INSERT_COLUMNS（JSON 四列反序列化，解析失败保原串留痕不炸）。
        status="absent"：exact 无当日行 / pit 无更早分区（如实缺席，禁编空池）。
    """
    from zephyr.pf_alloc.allocation_inputs import resolve_reader

    d = _iso_day_or_raise(day)
    if stage not in _STAGE_ALLOWED:
        raise ValueError(f"stage 非法（封闭集，真源=DDL stage 列注）: {stage!r}")
    template = {
        "pit": _SQL_POOL_LOAD_PIT,
        "exact": _SQL_POOL_LOAD_EXACT,
    }.get(mode)
    if template is None:
        raise ValueError(f"mode 非法（exact|pit）: {mode!r}")
    sql = template.format(cols=_SQL_POOL_LOAD_COLS, table=_TARGET_TABLE, day=d, stage=stage)
    try:
        rows = list(resolve_reader(reader)(sql))
    except Exception as exc:  # noqa: BLE001 — 读通道故障=快照不可得（fail-visible 不伪装空池）
        _logger.warning("candidate_pool: %s 读回异常折 absent（mode=%s）: %s", d, mode, exc)
        return {"status": "absent", "error": type(exc).__name__, "trade_date": d, "stage": stage}
    if not rows:
        return {"status": "absent", "error": "no_pool_row", "trade_date": d, "stage": stage}
    pool: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(zip(POOL_INSERT_COLUMNS, raw, strict=True))
        for col in _JSON_COLUMNS:
            value = row.get(col)
            if isinstance(value, str):
                try:
                    row[col] = json.loads(value)
                except (TypeError, ValueError):
                    pass  # 解析失败保原串留痕（不炸读回）
        pool.append(row)
    return {"status": "ok", "trade_date": str(pool[0]["trade_date"]), "stage": stage, "pool": pool}


__all__: Final = [
    "CATEGORY_ID",
    "DEFAULT_STAGE",
    "POOL_INSERT_COLUMNS",
    "POOL_VERSION",
    "PoolBundleSource",
    "PoolBundles",
    "build_snapshot_meta",
    "clear_bundle_sources",
    "collect_bundles",
    "load_pool_snapshot",
    "persist",
    "pool_rows_to_tuples",
    "pool_to_rows",
    "register_pool_bundle_source",
    "registered_bundle_sources",
    "run_daily_batch",
    "run_pool_batch_for_day",
]
