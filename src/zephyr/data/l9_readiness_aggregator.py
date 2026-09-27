# [BLUEPRINT] MOD-DATA-L9AGG | docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md | §四最小件
# [MODULE] zephyr.data.l9_readiness_aggregator
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader/ch_writer（读写通道，测试可注入）; zephyr.data.table_registry（表名派生禁硬编码）;
#   zephyr.governance.depgraph_schema（PG 只读，fail-open）; time_utils.now_utc（禁 datetime.now——RULE-SCHEMA-TZ）;
#   config/trading_decision_map.yaml（pit_effective_from 真源）; pipeline_events.resolve_pf_alloc_trade_date（业务日真源，懒加载）
# [CONSUMERS] TDM-E-L9-AGG（module_ref 锚——本件即"知识供给汇聚"实件）; TDM-E-L9-AGG→TDM-E-FLOW 供给健康读数边
#   （下游 pf_alloc/建仓流消费=二期）; strategy_pipeline.pipeline_events（task_completed 唤醒挂接）; 晨报供给健康段（读表）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯读取聚合层（源线数据已在 CH/PG，禁在汇聚点采集——f34 册边界）; fail-open：探测失败≠读数为零，
#   禁静默绿（reconcile 同款，error 行出声）; 声明式 skip/suspended（B/C 渠道未接、V2 定案挂起、读数面未登记
#   留因不计红，禁硬凑绿——f31/f33 册）; 事件触发禁 cron/Timer/sleep（宪法 §9.3，daily_kline 系 SUCCESS 唤醒，
#   同日 60min 节流 DB 侧时钟比较）; DateTime64(3)+显式时区、ingest_ts 由 DB now64(3) 生成、写侧零墙钟
#   （RULE-SCHEMA-TZ）; 表名经 TableRegistry 派生禁硬编码; SQL 常量 _SQL_* 前缀（NO-BARE-SQL）; 图谱侧口径与
#   reconcile_chain_refs.py 同判据，禁另立第三套（f34 册 §五）
# [MODIFY-GUARD] 读数口径/分档阈值变更须同步 f34 册六向台账；图谱侧判据变更须与 reconcile_chain_refs.py 同批（双文件口径锁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 钩子永不反噬调度器（全捕获转 error 出声）; CH/PG 探测失败转 error 行留因继续; 业务日不可解析=data_insufficient
# [TESTS] tests/data/test_l9_readiness_aggregator.py
# [A_module] module_id=MOD-DATA-L9AGG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-data-l9agg-l9-readiness-aggregator-20260926
"""L9 知识供给汇聚就绪度聚合器——TDM-E-L9-AGG 的实件（f34 册 P0 断链"知识汇聚点"最小件）。

真源：docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md §四（最小实件化路径，
"读数原料已散装在岗——聚合器只做拼装，零新采集"）+ TDM-E-L9-AGG 节点 algo_note
（"本节点只承载结构与指向，不存实时数据"——实件化目标不是数据湖，而是就绪度读数生产者）。

定位：29 源线（A01-A16/B01-B10/C01-C03）+5 图谱（G1-G5）+3 状态快照（V1-V3）的汇聚读数点。
事件触发（调度器 task_completed 唤醒，daily_kline 系 SUCCESS=行情到位）→ 纯读取四源
（①源线 CH 新鲜度 ②图谱 PG/registry 对账读数 ③状态快照 CH 读数 ④TDM pit_effective_from 真源）
→ 逐源线单行读数（绿/黄/红/挂起/跳过 + 时戳 + 行数）→ 写 c1_market.l9_readiness_daily
（ReplacingMergeTree latest-wins 同日刷新幂等）→ T 日聚合读数喂次日数据就绪度
（TDM-E-L9-AGG→TDM-E-FLOW 边 pit_proof；latency_budget=T-1 08:00）。

分档纪律（f34 册堵点④）：
  A 档 16 线计健康分（CH 读数面在产）；B/C 档 13 线单列 suspended 挂起不计红（渠道未接，
  与"挂起不入批"登记语义对齐，禁为凑数建假源）；读数面未登记的（A11 EIA）skip 留因不硬凑；
  V2 定案挂起（纪要 §8.3 不代建）suspended；G5 挂零 red 如实（WP-0.5 治本未落地，f32 册）。

fail-open 三条：探测失败=error 行留因（绝不静默记绿/零）；CH 写失败出声返回 error 摘要；
全源不可达时汇总行必为非绿。消费侧（pf_alloc 就绪度检查）=二期接线，先落数后接线。

用法：
  python -m zephyr.data.l9_readiness_aggregator                # 唤醒过滤+节流+读数+写 CH
  python -m zephyr.data.l9_readiness_aggregator --dry-run      # 只拼装打 stdout，零写
  python -m zephyr.data.l9_readiness_aggregator --force        # 绕过 60min 节流强制刷新

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/data/l9_readiness_aggregator.yaml
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date as _date
from datetime import timedelta
from typing import Any, Final, Protocol
from zoneinfo import ZoneInfo

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = ["aggregate", "maybe_emit_l9_readiness", "run_aggregate"]

MODULE_ID: Final = "MOD-DATA-L9AGG"

_TDM_YAML: Final = REPO_ROOT / "config" / "trading_decision_map.yaml"
_CHAIN_REGISTRY: Final = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "chain_registry.yaml"
)

_SH_TZ: Final = ZoneInfo("Asia/Shanghai")

#: 判定链同款自然唤醒点（daily_kline 系 SUCCESS=行情到位，宪法 §9.3 事件触发禁轮询）。
#: 夜批后续层（nightly_financial/整批巡检）落定的数据由下次唤醒的 60min 节流刷新兜底，
#: 读数逐行携带实测 max 时戳——滞后可见不遮蔽（fail-open 语义）。
_WAKE_TASK_KEYS: Final = ("daily_kline", "kline_daily", "kline_index")

#: 同业务日最小刷新间隔（分钟）：DB 侧 ingest_ts 比较，防同一晚 ~15 个 daily_kline 系任务
#: 完成事件各自触发一次全量拼装。表不存在/查询失败=不节流直走（建表前可见 FAIL）。
_THROTTLE_MINUTES: Final = 60

#: CH 新鲜度扫描窗（天）：有界扫描防 tick_data 亿级行全表扫（分区裁剪友好）。
_FRESH_WINDOW_DAYS: Final = 7


#: A 档读数面（f30 册 §三逐线对号入座；表名经 TableRegistry 派生禁硬编码 db.table；
#: max_lag_days 按 TDM 边 frequency 分档：daily/realtime/intraday=3，weekly/BDI=5，
#: FRED 混频=7，互动问答=7，季度财务公告日=100，adhoc 披露=20）。
@dataclass(frozen=True)
class _LineSpec:
    """一条 CH 读数面探测参数（NO-LONG-PARAM-LIST：参数组走数据类不进签名）。"""

    line: str
    tier: str
    category_id: str
    col: str
    max_lag: int
    note: str


_A_LINES_CH: Final = (
    _LineSpec("A01", "A", "market_kline_daily", "trade_date", 3, "日线/分钟行情（daily）"),
    _LineSpec("A02", "A", "market_tick", "trade_date", 3, "Tick 分笔（realtime；历史断档 PIT 已登记）"),
    _LineSpec("A03", "A", "market_sector_state", "trade_date", 3, "板块/概念指数（f30 实测口径=sector_state）"),
    _LineSpec("A04", "A", "market_daily_valuation", "trade_date", 3, "估值（daily）"),
    _LineSpec("A05", "A", "fund_income_statement", "announce_date", 100, "财务（quarterly，公告日 PIT）"),
    _LineSpec("A06", "A", "market_money_flow", "trade_date", 3, "资金流（daily）"),
    _LineSpec("A07", "A", "market_alt_stock_comment", "trade_date", 3, "千股千评（daily 快照）"),
    _LineSpec("A08", "A", "market_alt_shipping_index", "trade_date", 5, "航运 BDI（daily，发布滞后 T-1）"),
    _LineSpec("A09", "A", "market_news_sentiment_window", "window_date", 3, "财经快讯情绪（realtime 夜间窗）"),
    _LineSpec("A10", "A", "market_macro_data", "report_date", 7, "国际宏观 FRED（daily/weekly 混频）"),
    _LineSpec("A12", "A", "market_weather_data", "record_date", 3, "天气（realtime 观测）"),
    _LineSpec("A13", "A", "fund_shareholder_count", "end_date", 20, "股东户数（adhoc 披露日锚定）"),
    _LineSpec("A14", "A", "fund_irm_interactive_qa", "question_date", 7, "互动易问答（intraday）"),
    _LineSpec("A15", "A", "crypto_kline_daily", "trade_date", 3, "加密永续（realtime 快照）"),
)
#: A11 EIA 周度族无 CH 品类锚（DS 引用式）——声明式 skip 留因，登记读数面后即接（禁硬凑）。
_A_SKIP: Final = (("A11", "读数面未登记：EIA 周度族无 CH 品类锚（DS 引用式，f30 A11）"),)

#: B/C 档 13 线：渠道未接，suspended 挂起不计红（f31 册：登记诚实，禁为凑数建假源）。
_B_LINES: Final = (
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
)
_C_LINES: Final = ("C01", "C02", "C03")

# ── SQL 常量（NO-BARE-SQL gate：_SQL_* 前缀定义行；{table} 经 TableRegistry 派生填充）──

#: CH 新鲜度探测：max(日期列) + 近窗行数（有界扫描，分区裁剪友好）。
_SQL_FRESHNESS = "SELECT max({col}), countIf({col} >= toDate('{since}')) FROM {table}"

#: 节流探测：同业务日近 N 分钟内是否已有入库（DB 侧时钟比较，零墙钟）。
_SQL_THROTTLE = (
    "SELECT countIf(ingest_ts >= now64(3) - INTERVAL {minutes} MINUTE) FROM {table} WHERE trade_date = '{day}'"
)

#: V1 大盘快照读数（judgment 台账，f33 册：asof_ts 判定时刻）。
_SQL_V1_JUDGMENT = "SELECT max(asof_ts), countIf(asof_ts >= toDateTime64('{since}', 3, 'UTC')) FROM {table}"

#: 状态快照读数（sector_state，f33 册 V3 在产证据面）。
_SQL_V3_SECTOR = "SELECT max(trade_date), countIf(trade_date >= toDate('{since}')) FROM {table}"

#: 读数落库写侧模板（NO-BARE-SQL：_SQL_* 前缀常量；列序=schema.INSERT_COLUMNS 单点真源）。
_SQL_INSERT_READINGS = "INSERT INTO {table} {cols} FORMAT TSV"

# PG 侧（图谱五谱，f32 册行数口径；depgraph PG，只读）——
_SQL_PG_IG_CHAIN = "SELECT count(*) FROM ig_chain"
_SQL_PG_IG_FACT_CKG = "SELECT count(*) FROM ig_fact WHERE source = 'ckg_2021'"
# ig_equity_edge 退役第一步（successor=entity_graph）：G3 切换新真源 edge_holding（entity_graph 六表，
# DDL 真源=apply_entity_graph_ddl.py；现行集口径=valid_to IS NULL，与 chainmap_equity_graph.py 同判据），
# 旧表 DROP 待 Owner 终准。
_SQL_PG_EDGE_HOLDING = "SELECT count(*) FROM edge_holding WHERE valid_to IS NULL"
_SQL_PG_STOCK_CONCEPT = "SELECT count(*) FROM stock_concept"
_SQL_PG_IO_EDGE = "SELECT count(*) FROM ig_io_edge"
#: G5 挂零复测（f32 册：from_sector_code 与 ig_node 两套 id 体系，挂上=治本落地）。
_SQL_PG_IO_HUNG = (
    "SELECT count(*) FROM ig_io_edge e WHERE EXISTS(SELECT 1 FROM ig_node n WHERE n.node_id = e.from_sector_code)"
)

#: 图谱谱位 → (PG SQL, 依据注记)。G5 特判挂零；G3=五谱唯一 TDM 有码节点（equity_penetration）。
_G_PG: Final = (
    ("G1", _SQL_PG_IG_CHAIN, "产业链（ig_chain，DDL 真源=apply_industry_graph_ddl）"),
    ("G2", _SQL_PG_IG_FACT_CKG, "CKG 事实层（静态快照 as_of=2021-10-26，PIT 诚实）"),
    # G3 已切新真源：股权穿透=edge_holding（entity_graph 六表，MOD-ENTITY-GRAPH）；
    # ig_equity_edge 退役第一步，旧表 DROP 待 Owner 终准。
    ("G3", _SQL_PG_EDGE_HOLDING, "股权穿透（edge_holding，entity_graph 六表，MOD-ENTITY-GRAPH）"),
    ("G4", _SQL_PG_STOCK_CONCEPT, "概念题材（stock_concept，THS 导出）"),
)


#: 读数面 category_id → 全限定表名解析（TableRegistry 派生，禁硬编码；查不到=KeyError fail-closed
#: 由调用方转 error 行，不静默）。
def _resolve_table(category_id: str) -> str:
    from zephyr.data.table_registry import get_registry

    return get_registry().table(category_id)


def _sh_now_str() -> str:
    """读数产出时刻（事件时戳）：now_utc 转上海时区毫秒串（生成侧零 datetime.now）。"""
    return now_utc().astimezone(_SH_TZ).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _default_reader(sql: str, timeout: int = 60) -> str:
    from zephyr.data import ch_reader

    return ch_reader.query(sql, timeout=timeout)


def _default_writer(table: str, columns: str, tsv: str) -> bool:
    from zephyr.data.ch_writer import write_tsv

    return bool(write_tsv(table, columns, tsv.encode("utf-8")))


def _default_pg_query(sql: str) -> list[tuple] | None:
    """PG 只读通道；fail-open 返回 None（探测失败≠读数为零，由调用方转 error 行）。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                return list(cur.fetchall())
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001 — PG fail-open（reconcile 同款）
        log.warning("PG 探测失败（fail-open 转 error 行）: %s", exc)
        return None


def _resolve_trade_date() -> str:
    """共用业务日真源（禁墙钟猜日）：pipeline_events.resolve_pf_alloc_trade_date。"""
    from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

    return resolve_pf_alloc_trade_date()


def _pit_effective_from() -> str:
    """知识层 PIT 生效日：TDM 本体 effective_from 真源读取（D118/D122），禁硬编码。"""
    dm = yaml.safe_load(_TDM_YAML.read_text(encoding="utf-8"))
    raw = str(dm.get("effective_from") or "").strip()
    if not raw:
        raise RuntimeError(f"TDM 缺 effective_from（{_TDM_YAML.name} 顶部真源轴）")
    return raw[:10]


def _clean(detail: str) -> str:
    """TSV 值消毒：detail 禁含制表/换行（FORMAT TSV 裸值无转义）。"""
    return detail.replace("\t", " ").replace("\r", " ").replace("\n", " ")[:480]


def _lag_days(day: str, max_val: str) -> int | None:
    """max(日期列) 距业务日日数；空值/不可解析=None（NULL/空表语义）。"""
    raw = (max_val or "").strip()
    if not raw or raw == "\\N":
        return None
    try:
        return (_date.fromisoformat(day) - _date.fromisoformat(raw[:10])).days
    except ValueError:
        return None


def _grade(lag: int | None, max_lag: int) -> str:
    """滞后分档：≤阈值=green；≤2×阈值=yellow；更旧/空=red（断供必须可见）。"""
    if lag is None:
        return "red"
    if lag <= max_lag:
        return "green"
    if lag <= max_lag * 2:
        return "yellow"
    return "red"


def _probe_ch_line(
    spec: _LineSpec,
    day: str,
    since: str,
    reader: Callable[..., str],
    sql: str,
) -> dict[str, Any]:
    """单条 CH 读数面探测：freshness+近窗行数 → 绿/黄/红 + error 行留因（fail-open）。"""
    table = _resolve_table(spec.category_id)
    try:
        out = (reader(sql.format(col=spec.col, since=since, table=table)) or "").strip()
        parts = out.split("\t")
        max_val = parts[0] if parts and parts[0] else "\\N"
        rows = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else 0
    except Exception as exc:  # noqa: BLE001 — 探测失败≠读数为零，留因出声
        return _row(day, spec.line, spec.tier, "error", -1, -1, f"探测失败 {type(exc).__name__}: {exc}"[:200])
    lag = _lag_days(day, max_val)
    status = _grade(lag, spec.max_lag)
    # 近窗零行黄帽只作用于高频线（max_lag<30）：季频/年频线公告稀疏是常态，
    # 健康判据全权交给频率感知的滞后分档（禁季频线被窗口零行误压黄）
    if rows == 0 and spec.max_lag < 30 and lag is not None and lag > _FRESH_WINDOW_DAYS:
        status = "yellow" if status == "green" else status  # 近窗零行但历史在=陈旧可见
    if rows == 0 and lag is None:
        status = "red"  # 空表=断供，禁静默绿
    return _row(
        day,
        spec.line,
        spec.tier,
        status,
        lag if lag is not None else -1,
        rows,
        f"{spec.note}；max({spec.col})={max_val[:10]}；表={table}",
    )


def _row(day: str, line: str, tier: str, status: str, lag: int, rows: int, detail: str) -> dict[str, Any]:
    return {
        "trade_date": day,
        "source_line": line,
        "tier": tier,
        "status": status,
        "freshness_lag_days": int(lag),
        "rows_in_window": int(rows),
        "detail": _clean(detail),
    }


def _chain_refs_reading(day: str) -> dict[str, Any]:
    """图谱对账读数（G-REFS）：与 reconcile_chain_refs.py 同判据（covered=registry covered 位，
    断链=引用不在册；只报不清，未吸收=遗漏探测器读数）。broke>0=red；未吸收>0=yellow。"""
    try:
        dm = yaml.safe_load(_TDM_YAML.read_text(encoding="utf-8"))
        reg = yaml.safe_load(_CHAIN_REGISTRY.read_text(encoding="utf-8"))
        known = {c["chain_id"] for c in reg.get("chains", []) if c.get("chain_id")}
        refs: dict[str, list[str]] = {}
        broken = 0
        for n in dm.get("nodes", []):
            for cid in n.get("chain_refs") or []:
                refs.setdefault(n["node_id"], []).append(cid)
                if cid not in known:
                    broken += 1
        covered = {c["chain_id"] for c in reg.get("chains", []) if c.get("covered")}
        referenced = {cid for lst in refs.values() for cid in lst}
        uncovered = len(covered - referenced)
        status = "red" if broken else ("yellow" if uncovered else "green")
        return _row(
            day,
            "G-REFS",
            "G-REFS",
            status,
            -1,
            len(referenced),
            f"chain_refs 双向对账（reconcile 同口径）：引用{len(referenced)}/断链{broken}"
            f"/覆盖{len(covered)}/未吸收{uncovered}（只报不清）",
        )
    except Exception as exc:  # noqa: BLE001 — fail-open 留因
        return _row(day, "G-REFS", "G-REFS", "error", -1, -1, f"对账读数失败 {type(exc).__name__}: {exc}"[:200])


def aggregate(
    day: str,
    pit_effective_from: str,
    *,
    reader: Callable[..., str] | None = None,
    pg_query: Callable[[str], list[tuple] | None] | None = None,
    produced_at: str | None = None,
) -> list[dict[str, Any]]:
    """纯读取拼装：四源读数 → 逐源线行列表（零采集；CH/PG/registry 全注入可测）。

    Args:
        day: 业务日（'YYYY-MM-DD'，调用方已按共用真源校验）。
        pit_effective_from: 知识层 PIT 生效日（TDM effective_from 真源值）。
        reader: CH 只读通道（TSV）；None=模块级 _default_reader（调用时解析=测试注入点，
            禁改成 import 时绑定——judgment_ledger 行为保真同款约束）。
        pg_query: PG 只读通道（fail-open 返回 None）；None=模块级 _default_pg_query。
        produced_at: 产出时刻串（缺省=now_utc 转上海时区；测试注入）。

    Returns:
        行 dict 列表（键=INSERT_COLUMNS 顺序，不含 ingest_ts）。
    """
    reader = reader or _default_reader
    pg_query = pg_query or _default_pg_query
    produced = produced_at or _sh_now_str()
    since = (_date.fromisoformat(day) - timedelta(days=_FRESH_WINDOW_DAYS)).isoformat()
    rows: list[dict[str, Any]] = []

    # ① A 档源线（CH 新鲜度；A16=PG 投入产出静态面；A11=声明式 skip）
    for spec in _A_LINES_CH:
        rows.append(_probe_ch_line(spec, day, since, reader, _SQL_FRESHNESS))
    for line, reason in _A_SKIP:
        rows.append(_row(day, line, "A", "skip", -1, -1, reason))
    rows.append(
        _pg_line(
            day,
            "A16",
            "A",
            _SQL_PG_IO_EDGE,
            "投入产出（ig_io_edge，2020 版 153 部门静态面；消费挂零归 G5）",
            pg_query,
            static=True,
        )
    )

    # ② B/C 档：声明式挂起（零探测零采集；f31 册"挂起不入批"）
    for line in _B_LINES:
        rows.append(
            _row(day, line, "B", "suspended", -1, -1, "渠道未接，挂起不入批（f31 册；接入=另立战役 Owner 门位）")
        )
    for line in _C_LINES:
        rows.append(_row(day, line, "C", "suspended", -1, -1, "无渠道，挂起不入批（f31 册；禁为凑数建假源）"))

    # ③ 图谱五谱（PG fail-open）+ 对账读数
    for line, sql, note in _G_PG:
        rows.append(_pg_line(day, line, "G", sql, note, pg_query))
    rows.append(_probe_g5(day, pg_query))
    rows.append(_chain_refs_reading(day))

    # ④ 状态变量快照（f33 册：V1 大盘台账/V3 板块在产/V2 定案挂起）
    rows.append(_probe_v1(day, since, reader))
    rows.append(
        _row(
            day,
            "V2",
            "V",
            "suspended",
            -1,
            -1,
            "情绪聚合器定案挂起（纪要§8.3 不代建，f33 册）；底座 emotion_index_builder+sentiment_panel 在库",
        )
    )
    rows.append(_probe_v3(day, since, reader))

    # ⑤ 汇总行（suspended/skip 不计红；error 禁静默绿）
    rows.append(_summary_row(day, rows, produced))

    # 逐行补 PIT 生效日与产出时刻（汇总行同制）
    for r in rows:
        r["pit_effective_from"] = pit_effective_from
        r["produced_at"] = produced
    return rows


def _pg_line(
    day: str,
    line: str,
    tier: str,
    sql: str,
    note: str,
    pg_query: Callable[[str], list[tuple] | None],
    static: bool = False,
) -> dict[str, Any]:
    """PG 计数读数（图谱/投入产出静态面）：count>0=green（静态面无新鲜度语义），0=red。"""
    res = pg_query(sql)
    if res is None:
        return _row(day, line, tier, "error", -1, -1, "PG 不可达（fail-open 留因，探测失败≠读数为零）")
    n = int(res[0][0]) if res and res[0] else 0
    suffix = "；static 口径无新鲜度轴" if static else ""
    return _row(day, line, tier, "green" if n > 0 else "red", -1, n, f"{note}；count={n}{suffix}")


def _probe_g5(day: str, pg_query: Callable[[str], list[tuple] | None]) -> dict[str, Any]:
    """G5 投入产出：挂零复测（f32 册——挂上节点数=0 则 red 如实，WP-0.5 治本未落地）。"""
    total = pg_query(_SQL_PG_IO_EDGE)
    hung = pg_query(_SQL_PG_IO_HUNG)
    if total is None or hung is None:
        return _row(day, "G5", "G", "error", -1, -1, "PG 不可达（fail-open 留因）")
    n_total = int(total[0][0]) if total and total[0] else 0
    n_hung = int(hung[0][0]) if hung and hung[0] else 0
    status = "green" if n_hung > 0 else "red"
    return _row(
        day,
        "G5",
        "G",
        status,
        -1,
        n_hung,
        f"投入产出传导边挂载：{n_hung}/{n_total}（挂零=部门码↔ig_node 两套 id 未治本，WP-0.5）",
    )


def _probe_v1(day: str, since: str, reader: Callable[..., str]) -> dict[str, Any]:
    """V1 大盘快照（judgment 台账）：通道在产量稀疏=黄帽（f33 册 20/4/9 行口径）。"""
    table = _resolve_table("judgment_intraday_market_state")
    try:
        out = (reader(_SQL_V1_JUDGMENT.format(table=table, since=since)) or "").strip()
        parts = out.split("\t")
        max_val = parts[0] if parts and parts[0] else "\\N"
        rows_7d = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else 0
    except Exception as exc:  # noqa: BLE001 — fail-open 留因
        return _row(day, "V1", "V", "error", -1, -1, f"探测失败 {type(exc).__name__}: {exc}"[:200])
    lag = _lag_days(day, max_val)
    status = _grade(lag, 3)
    detail = f"大盘 RegimeSnapshot 台账（judgment_intraday_market_state）；max(asof_ts)={max_val[:19]}"
    if rows_7d < 10 and status == "green":
        status = "yellow"  # 产量稀疏黄帽：通道在但非每日满产（f33 判读），禁稀疏表 read 满绿
        detail += "；近窗行稀疏（f33 黄：产量核对归 F37 车道）"
    return _row(day, "V1", "V", status, lag if lag is not None else -1, rows_7d, detail)


def _probe_v3(day: str, since: str, reader: Callable[..., str]) -> dict[str, Any]:
    """V3 板块快照（sector_state，f33 册：42.6 万行在产=实为绿）。"""
    return _probe_ch_line(
        _LineSpec("V3", "V", "market_sector_state", "trade_date", 3, "板块五成分状态（sector_state_pipeline 在产）"),
        day,
        since,
        reader,
        _SQL_V3_SECTOR,
    )


def _summary_row(day: str, rows: list[dict[str, Any]], produced: str) -> dict[str, Any]:
    """AGG 汇总行：健康分只计 A/G/G-REFS/V 三态行；suspended/skip 单列；error 非绿（禁静默绿）。"""
    counted = [r for r in rows if r["tier"] in ("A", "G", "G-REFS", "V")]
    n_red = sum(1 for r in counted if r["status"] == "red")
    n_yellow = sum(1 for r in counted if r["status"] == "yellow")
    n_error = sum(1 for r in counted if r["status"] == "error")
    n_green = sum(1 for r in counted if r["status"] == "green")
    n_susp = sum(1 for r in rows if r["status"] == "suspended")
    n_skip = sum(1 for r in rows if r["status"] == "skip")
    if n_red:
        status = "red"
    elif n_error or n_yellow:
        status = "yellow"
    else:
        status = "green"
    detail = (
        f"A/G/V 计健面：{n_green}绿/{n_yellow}黄/{n_red}红/{n_error}错；"
        f"挂起 {n_susp}（B/C 渠道未接+V2 定案）；跳过 {n_skip}（读数面未登记）；"
        f"产出 {produced}"
    )
    return _row(day, "AGG", "AGG", status, -1, len(rows), detail)


class _L9SchemaProto(Protocol):
    """l9 就绪度表 schema 模块结构契约（INSERT_COLUMNS/TABLE_NAME 供写侧与节流探测）。"""

    TABLE_NAME: str
    INSERT_COLUMNS: str


def _insert_columns(schema: _L9SchemaProto) -> list[str]:
    """写侧声明列解析：INSERT_COLUMNS 是多行串（含换行缩进），先归一空白再切分。"""
    flat = " ".join(str(schema.INSERT_COLUMNS).split())
    return [c.strip() for c in flat.strip("()").split(",") if c.strip()]


def rows_to_tsv(rows: list[dict[str, Any]], columns: list[str]) -> str:
    """行列表 → TSV 串（INSERT ... FORMAT TSV 载荷；列序=INSERT_COLUMNS）。"""
    lines = []
    for r in rows:
        lines.append("\t".join(str(r[c]) for c in columns))
    return "\n".join(lines) + "\n"


def _resolve_day(day: str | None) -> str:
    """业务日解析+校验（未校验日期禁入 SQL，alloc_budget_daily 同约定）。"""
    biz_day = day or _resolve_trade_date()
    _date.fromisoformat(biz_day)  # 非法格式 ValueError 上抛=调用方转 data_insufficient
    return biz_day


def _throttled(schema: _L9SchemaProto, biz_day: str, reader: Callable[..., str]) -> bool:
    """同业务日 60min 节流探测：DB 侧 ingest_ts 时钟比较（零墙钟）；探测失败=不节流直走。"""
    try:
        raw = (
            reader(_SQL_THROTTLE.format(minutes=_THROTTLE_MINUTES, table=schema.TABLE_NAME, day=biz_day)) or ""
        ).strip()
        return raw.isdigit() and int(raw) > 0
    except Exception as exc:  # noqa: BLE001 — 节流探测失败不节流直走（表缺失在下步可见）
        log.warning("节流探测失败（不节流直走）: %s", exc)
        return False


def run_aggregate(
    day: str | None = None,
    *,
    force: bool = False,
    dry_run: bool = False,
    reader: Callable[..., str] | None = None,
    writer: Callable[[str, str, str], bool] | None = None,
    pg_query: Callable[[str], list[tuple] | None] | None = None,
) -> dict[str, Any]:
    """拼装→（节流闸）→写 CH；返回动作摘要（emitted/throttled/dry_run/error）。

    节流闸：同业务日 {_THROTTLE_MINUTES} 分钟内已有入库→throttled 零写（force 直过）。
    表不存在→error 出声提示先跑 apply_l9_readiness_ddl.py --apply（FAIL-VISIBLE）。
    reader/writer/pg_query None=模块级缺省通道（调用时解析=测试注入点）。
    """
    from schemas.categories import l9_readiness_daily as schema

    reader = reader or _default_reader
    writer = writer or _default_writer
    pg_query = pg_query or _default_pg_query
    out: dict[str, Any] = {"module": MODULE_ID, "action": "error"}
    try:
        biz_day = _resolve_day(day)
    except Exception as exc:  # noqa: BLE001 — 业务日不可解析=不发读数，但必须出声
        out["error"] = f"业务日不可解析（禁墙钟猜日）: {type(exc).__name__}: {exc}"[:200]
        return out
    out["trade_date"] = biz_day
    if not force and not dry_run and _throttled(schema, biz_day, reader):
        out["action"] = "throttled"
        return out
    try:
        pit = _pit_effective_from()
        rows = aggregate(biz_day, pit, reader=reader, pg_query=pg_query)
    except Exception as exc:  # noqa: BLE001 — 拼装失败出声（fail-open，绝不静默零读数）
        out["error"] = f"拼装失败 {type(exc).__name__}: {exc}"[:300]
        return out
    columns = _insert_columns(schema)
    out["rows"] = len(rows)
    out["summary"] = rows[-1]["status"] if rows else "none"
    if dry_run:
        out["action"] = "dry_run"
        out["tsv"] = rows_to_tsv(rows, columns)
        return out
    sql = _SQL_INSERT_READINGS.format(table=schema.TABLE_NAME, cols=schema.INSERT_COLUMNS)
    if not writer(schema.TABLE_NAME, str(schema.INSERT_COLUMNS), rows_to_tsv(rows, columns)):
        out["error"] = "CH 写入未确认（write_tsv=False）——读数未落地，禁记成功"
        return out
    out["action"] = "emitted"
    return out


def maybe_emit_l9_readiness(task_id: object = None, success: bool = True, **_kwargs) -> dict[str, Any]:
    """调度器 task_completed 唤醒钩子（唯一自动产出者；宪法 §9.3 事件触发禁轮询）。

    契约（judgment 链同款五态）：非唤醒点/任务失败→零副作用 skipped_wake_point；
    节流窗内→skipped_throttled；业务日不可解析→data_insufficient 出声；
    任何异常→error 出声**绝不反噬唤醒链**（本钩子挂在调度器 SUCCESS 事件上，抛出=拖死采集链）。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in _WAKE_TASK_KEYS):
        return {"action": "skipped_wake_point"}
    try:
        res = run_aggregate()
        action = res.get("action", "error")
        if action == "error":
            log.warning("[L9-AGG] 就绪度读数未落地: %s", res.get("error", ""))
            return {"action": "error", "reason": res.get("error", "")}
        if action == "throttled":
            return {"action": "skipped_throttled"}
        log.info("[L9-AGG] 就绪度读数已产出: %s", {k: v for k, v in res.items() if k != "tsv"})
        return {"action": "emitted", **{k: v for k, v in res.items() if k not in ("tsv", "rows")}}
    except Exception as exc:  # noqa: BLE001 — 钩子永不反噬调度器，失败必须出声
        log.warning("[L9-AGG] 唤醒钩子异常（不影响后续链）: %s", exc, exc_info=True)
        return {"action": "error", "reason": f"{type(exc).__name__}: {exc}"[:200]}


def main() -> int:
    ap = argparse.ArgumentParser(description="L9 知识供给汇聚就绪度聚合器（TDM-E-L9-AGG 实件）")
    ap.add_argument("--trade-date", default=None, help="业务日 YYYY-MM-DD（缺省=共用业务日真源）")
    ap.add_argument("--force", action="store_true", help="绕过同日 60min 节流强制刷新")
    ap.add_argument("--dry-run", action="store_true", help="只拼装打 stdout，零写（FAIL-VISIBLE 取证面）")
    args = ap.parse_args()
    res = run_aggregate(day=args.trade_date, force=args.force, dry_run=args.dry_run)
    if res.get("action") == "dry_run":
        print(res["tsv"], end="")
        print(f"== DRY-RUN：{res['rows']} 行，汇总态={res['summary']}（零写）==")
        return 0
    if res.get("action") == "error":
        print(f"FAIL: {res.get('error')}")
        return 3
    print(
        f"OK action={res['action']} trade_date={res.get('trade_date')} rows={res.get('rows')} summary={res.get('summary')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
