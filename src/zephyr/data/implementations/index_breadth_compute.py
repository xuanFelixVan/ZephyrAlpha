# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.index_breadth_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider (capability=kline_index_breadth 路由)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 供应商侧真进料：从 c1_market.kline_daily 全市场日线自算涨跌家数回填 c1_market.kline_index
#   真表；只补 advance_count=0 AND decline_count=0 的零值位（真源优先，官方存量永不改写）；
#   整行读-改-写（ReplacingMergeTree 无部分列更新能力，非破坏性修复唯一路径）；
#   禁 DROP/ALTER/DELETE（RULE-DATA-OPS）；宇宙口径由 INDEX_UNIVERSE 注册表裁定，
#   每个 entry 必须有探针对拍证据（corr_ratio≥0.98 且 mag_ratio∈[0.9,1.1]）方可入表
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 读取/计算失败→返回 FetchResult(error=...) 不抛异常；
#   覆盖度防御触发/无聚合行→该日不写（fail-visible：跳过清单计数告警，禁静默零值）
# [TESTS] tests/data/implementations/test_index_breadth_compute.py
# [A_module] module_id=MOD-DATA-IDXBREADTH | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""指数涨跌家数（市场广度）供应商侧真进料 Provider（车道 G 治本，2026-09-16）。

断点事实（实证）：c1_market.kline_index 的 advance_count/decline_count 自 2026-07-03
起全表停更（bdpan 手工归档源 2026-07-02 16:24 断供；miniqmt/akshare 两 live 源均无
涨跌家数字段——表 INSERT_COLUMNS 不含该二列 = 结构性进料口缺失）。下游 F4 ad_ratio
恒 0 两个月，HMM F4/RiskSignal #7/T3 情绪/S2 breadth_thrust 四消费端同时失效。

第一性原理：涨跌家数是**成分股价格的函数**，不是独立外部事实。任何指数发布商给的
adv/dec 都只是其成分口径的一次聚合。故真进料不必依赖任何外部接口——从成分宇宙
自身日线聚合即得同源数字：

    ret_i(t) = close_i(t)×adj_i(t) / (close_i(t-1)×adj_i(t-1)) − 1   （后复权）
    其符号与交易所"收盘价 vs 除权参考价"比较同序（除权日复权因子同步跳变，
    复权收益自然消化除权，故与交易所涨跌判定一致）
    advance = countIf(ret > 0)，decline = countIf(ret < 0)

专业实践依据：券商/公募的市场宽度（breadth / A-D line / stock @ 52-week high 类）
指标一律由行情库成分自算（TBQA、Wind 宽度、iFind 宽度皆如此），无外购日度涨跌家数
接口——自算口径是本领域的默认做法，且零外部依赖、可无限回补、可审计。

选型证据（.runtime/tmp/laneG_probe_universe.py，真值=bdpan 时代官方存量
2019-01-01~2026-07-02，逐标的对拍；corr=涨跌比相关，mag=自算/官方 家数量级比）：

    000001 上证指数   SH      corr 0.9998 mag 0.981 mean|Δadv| 19.0
    000002 上证A指    SH      corr 0.9999 mag 1.001 mean|Δadv|  3.4
    000688 科创50     KC      corr 1.0000 mag 0.999 mean|Δadv|  0.7  (291 天)
    399001 深证成指   SZ      corr 0.9999 mag 0.987 mean|Δadv| 16.2
    399004 深证100R   SZ      corr 0.9999 mag 0.987 mean|Δadv| 16.2
    399006 创业板指   CY      corr 1.0000 mag 1.000 mean|Δadv|  1.7
    399102 创业板综   CY      corr 1.0000 mag 1.000 mean|Δadv|  1.7
    399106 深证综指   SZ      corr 0.9999 mag 0.987 mean|Δadv| 16.2
    399107 深证A指    SZ      corr 1.0000 mag 1.001 mean|Δadv|  4.2
    899050 北证50     BJ      corr 0.9999 mag 0.998 mean|Δadv|  0.5  (866 天)

    落选：000905 中证500（最优 SH mag 4.088=成分 500 只 vs 全沪市家数，口径不可由
    宇宙聚合复现）、000985 中证全指（官方存量无宽度）、399100 新指数（名称即占位，
    口径无据）。成分权重表 index_constituent 未用于自算——注册表内标的经验证据已
    达 corr≥0.9999，引入成分依赖只增故障面（等权计数不需权重）。

残差解释（为何不是逐位相等）：官方"平盘/停牌"判定与新股上市首日计入规则与本口径
微差；深证综指官方数略大于深市 A 股自算数（mag 0.987）——深证综指含深市 B 股等
非 A_share 品种，kline_daily 未纳。均值绝对偏差 ≤16/2897 家 = 0.6%，涨跌比偏差
0.0022，对 F4 ad_ratio（截面 z-score 消费）无实质影响。

写入语义（RULE-DATA-OPS 非破坏性）：
  kline_index 是 ReplacingMergeTree(ingest_ts)，无部分列更新能力 → 唯一非破坏性修复
  是整行读-改-写：读 FINAL 现值（name/OHLC/volume/amount/quality_flag 原样保留，
  TSV 字符串回写零精度损失），仅替换 advance_count/decline_count，不写 ingest_ts
  （DEFAULT now() 令新行成为版本赢家）。永不 DELETE、永不 ALTER。
  真源优先：仅当现值 advance_count=0 AND decline_count=0（=无信号）才填，bdpan 时代
  官方存量一行不动。
  溯源：回填行 data_source 改标 internal_breadth（消费端零 data_source 过滤已 grep
  证实），使"该数字来自内生聚合"可查、可回滚、可被告警线区分。

自愈窗口：日频任务的修复窗不取 scheduler 的月初 start，而取
`max(FLOOR_DATE, min(payload.start, payload.end - repair_lookback_days))`——
上游 kline_index 日频重灌（同一 trade_date 新版本行 adv=0 且 ingest_ts 更新）会在
lookback 窗内被本任务再次填回，跨月断档亦可自愈（深度历史修复经 extra.
repair_lookback_days 显式放大）。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/index_breadth_compute.yaml
"""

from __future__ import annotations

import datetime
import logging
import time
from typing import Final, Iterator

from zephyr.data.provider_base import (
    FetchPayload,
    FetchResult,
    IngestProviderBase,
)
from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# 注册表真名（#ARCH-CH-024 TABLE-NAME-REGISTRY 门合规，禁硬编码表名）
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")

# 回补地板：2019-01-01（实测 kline_daily 2018 及以前深市仅 ~141 只/日，宇宙覆盖
# 严重不足；2019-01-02 起才全量 3771+ 只——同 index_eqw_compute 基期裁定）
FLOOR_DATE: Final = datetime.date(2019, 1, 1)

# 日常修复窗（日历天）：覆盖 4 个月断档自愈；首跑即覆盖 2026-07-03 起的本次缺口
REPAIR_LOOKBACK_DAYS: Final = 120

# 热身窗（日历天）：保证窗首日的每只股票在窗内已有前收（长假 10 交易日 + 安全边际）
WARMUP_DAYS: Final = 45

# 回填行数据源标记（溯源：内生聚合，非外部发布值）
DATA_SOURCE_MARKER: Final = "internal_breadth"

# 宇宙口径（计数谓词 SQL 片段，基于 kline_daily 的 MATERIALIZED exchange + 6 位代码前缀）
# 前缀集合实测（2026-09-15）：SH={600,601,603,605,688,689} SZ={000,001,002,003,300,301,302}
# BJ={810,899,920}；无 B 股混入 market_type='A_share'。
UNIVERSE_PREDICATES: Final[dict[str, str]] = {
    "ALL_A": "1=1",
    "SZ": "exch = 'SZ'",
    "SH": "exch = 'SH'",
    "BJ": "exch = 'BJ'",
    "CY": "p3 IN ('300', '301', '302')",
    "KC": "p3 IN ('688', '689')",
}

# 指数标的 → 宇宙口径注册表（选型证据见模块 docstring；新标的须先过对拍双闸再登记）
INDEX_UNIVERSE: Final[dict[str, str]] = {
    "000001": "SH",  # 上证指数
    "000002": "SH",  # 上证A指
    "000688": "KC",  # 科创50（发布值为科创板板块宽度，实测 corr 1.0）
    "399001": "SZ",  # 深证成指
    "399004": "SZ",  # 深证100R
    "399006": "CY",  # 创业板指
    "399102": "CY",  # 创业板综
    "399106": "SZ",  # 深证综指（F4 ad_ratio 主消费标的）
    "399107": "SZ",  # 深证A指
    "899050": "BJ",  # 北证50
}

# 分宇宙覆盖度防御阈值（管道异常日判据：n 低于此值视为 kline_daily 断档，该日不写
# ——防"半宇宙"家数冒充官方全宇宙；实测 2026-09-15 宇宙规模 SZ 2897/SH 2308/
# BJ 1155/CY 1405/KC 616，阈值取各自早期上市规模的 1/3 以下安全边际）
MIN_COVERAGE: Final[dict[str, int]] = {
    "ALL_A": 1000,
    "SZ": 600,
    "SH": 600,
    "BJ": 40,
    "CY": 250,
    "KC": 20,
}

# 整行读-改-写列（kline_index 全部可插列；刻意不含 ingest_ts→DEFAULT now() 使新行胜出；
# 不含 MATERIALIZED exchange/symbol_canonical→CH 禁插 Code 44）
WRITE_COLUMNS: Final = [
    "trade_date",
    "symbol",
    "name",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "advance_count",
    "decline_count",
    "data_source",
    "quality_flag",
]

# SQL 模板常量（NO-BARE-SQL gate：_SQL_* 前缀定义行）
# 宇宙聚合：窗口 lag 取组内前一复权收盘 → ret → 按宇宙 countIf；组首行 ret=inf 由
# isFinite 滤除（等价"无前收不计"：新股首日/停牌跨段自然剔除，复牌跳空计入）。
# 注：本机 CH 无 lagIn 简写、neighbor 已 deprecated（index_eqw_compute 实测 2026-09-04）。
_SQL_UNIVERSE_AGG: Final = (
    "SELECT trade_date, {cols} "
    "FROM ("
    "  SELECT trade_date, ret, substring(sym6, 1, 3) AS p3, exch FROM ("
    "    SELECT trade_date, "
    "           replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', '') AS sym6, "
    "           exchange AS exch, "
    "           adj_close / lag(adj_close, 1) OVER (PARTITION BY symbol ORDER BY trade_date) - 1 AS ret "
    "    FROM ("
    f"      SELECT trade_date, symbol, exchange, "
    "             toFloat64(close) * toFloat64(ifNull(adj_factor, 1)) AS adj_close "
    f"      FROM {_TBL_KLINE_DAILY} "
    "      WHERE market_type = 'A_share' "
    "      AND trade_date >= toDate('{warm_start}') AND trade_date <= toDate('{end}')"
    "    )"
    "  ) "
    "  WHERE isFinite(ret) AND isNotNull(ret)"
    ") "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "GROUP BY trade_date ORDER BY trade_date FORMAT TSV"
)

# 现值为零宽度的行（=待修位）；FINAL 去重后才是版本赢家
_SQL_ZERO_BREADTH_ROWS: Final = (
    "SELECT {cols} FROM {table} FINAL "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "AND advance_count = 0 AND decline_count = 0 AND symbol IN ({symbols}) "
    "ORDER BY trade_date, symbol FORMAT TSV"
)

_SYMBOL_RE: Final = "0123456789"


def resolve_window(
    start: datetime.date,
    end: datetime.date,
    lookback_days: int = REPAIR_LOOKBACK_DAYS,
) -> tuple[datetime.date, datetime.date]:
    """修复窗裁定：取 payload.start 与 lookback 起点的较早者，地板 FLOOR_DATE 兜底。

    日频任务即使 scheduler 传月初 start，也会被 lookback 拉早 → 跨月断档自愈。
    """
    floor = max(FLOOR_DATE, min(start, end - datetime.timedelta(days=int(lookback_days))))
    return (floor, end)


def build_agg_columns(universes: list[str]) -> str:
    """宇宙计数列片段（adv_/dec_/n_ 三列一组，顺序与 _parse_agg_tsv 列名严格对应）。"""
    unknown = [u for u in universes if u not in UNIVERSE_PREDICATES]
    if unknown:
        raise ValueError(f"未注册宇宙口径: {unknown}（请补 UNIVERSE_PREDICATES）")
    return ", ".join(
        f"""countIf(ret > 0 AND {p}) AS adv_{u}, """
        f"""countIf(ret < 0 AND {p}) AS dec_{u}, countIf({p}) AS n_{u}"""
        for u, p in ((u, UNIVERSE_PREDICATES[u]) for u in universes)
    )


def agg_column_names(universes: list[str]) -> list[str]:
    """聚合结果列名（trade_date + 每宇宙 adv/dec/n）——与 build_agg_columns 同序。"""
    names = ["trade_date"]
    for u in universes:
        names += [f"adv_{u}", f"dec_{u}", f"n_{u}"]
    return names


def clean_symbols(symbols: list[str]) -> list[str]:
    """标的白名单净化（仅 6 位数字，防 SQL 字面量注入；保持入参顺序去重）。"""
    out: list[str] = []
    for s in symbols:
        code = str(s).strip()
        if len(code) == 6 and all(c in _SYMBOL_RE for c in code) and code not in out:
            out.append(code)
    return out


def parse_tsv(tsv: str, names: list[str]) -> list[dict[str, str]]:
    """TSV（无表头，ch_reader 已剥名称行）→ 列名字典列表；全列按字符串保留零精度损失。"""
    rows: list[dict[str, str]] = []
    for line in (tsv or "").strip().split("\n"):
        if not line:
            continue
        vals = line.split("\t")
        if len(vals) < len(names):
            log.warning("TSV 列数不足（%d<%d）跳过: %s", len(vals), len(names), line[:80])
            continue
        rows.append(dict(zip(names, vals[: len(names)])))
    return rows


def parse_agg(tsv: str, universes: list[str]) -> dict[tuple[str, str], dict[str, int]]:
    """聚合 TSV → {(trade_date, universe): {adv, dec, n}}。"""
    out: dict[tuple[str, str], dict[str, int]] = {}
    for row in parse_tsv(tsv, agg_column_names(universes)):
        d = row["trade_date"]
        for u in universes:
            try:
                out[(d, u)] = {
                    "adv": int(row[f"adv_{u}"]),
                    "dec": int(row[f"dec_{u}"]),
                    "n": int(row[f"n_{u}"]),
                }
            except (KeyError, ValueError) as e:  # noqa: BLE001 — 单格异常不毁整表
                log.warning("聚合行解析失败 %s/%s: %s", d, u, e)
    return out


def build_fill_rows(
    zero_rows: list[dict[str, str]],
    agg: dict[tuple[str, str], dict[str, int]],
    index_universe: dict[str, str] | None = None,
    min_coverage: dict[str, int] | None = None,
) -> tuple[list[tuple], list[dict]]:
    """零宽度现值行 + 宇宙聚合 → (待写整行元组, 跳过清单)。

    纯函数（不触 CH）——真源优先由调用方保证：zero_rows 只含 adv=0&dec=0 的行。
    跳过而非猜测：无聚合行（当日宇宙无日线）/覆盖度防御触发/自算宽度同为 0。
    """
    reg = index_universe if index_universe is not None else INDEX_UNIVERSE
    cov = min_coverage if min_coverage is not None else MIN_COVERAGE
    rows: list[tuple] = []
    skipped: list[dict] = []
    for r in zero_rows:
        d, sym = r["trade_date"], r["symbol"]
        uni = reg.get(sym)
        if uni is None:
            skipped.append({"trade_date": d, "symbol": sym, "reason": "标的未注册宇宙口径"})
            continue
        rec = agg.get((d, uni))
        if rec is None:
            skipped.append({"trade_date": d, "symbol": sym, "reason": f"无 {uni} 聚合行"})
            continue
        if rec["n"] < cov[uni]:
            skipped.append(
                {"trade_date": d, "symbol": sym, "reason": f"覆盖度防御 n={rec['n']}<{cov[uni]}"}
            )
            continue
        if rec["adv"] <= 0 and rec["dec"] <= 0:
            skipped.append({"trade_date": d, "symbol": sym, "reason": "自算涨跌同为 0"})
            continue
        rows.append(
            (
                r["trade_date"],
                r["symbol"],
                r["name"],
                r["open"],
                r["high"],
                r["low"],
                r["close"],
                r["volume"],
                r["amount"],
                str(rec["adv"]),
                str(rec["dec"]),
                DATA_SOURCE_MARKER,
                r["quality_flag"],
            )
        )
    return rows, skipped


class IndexBreadthComputeProvider(IngestProviderBase):
    """指数涨跌家数内生聚合进料 Provider（回填 kline_index 真表零宽度位）。

    用法（由 scheduler 自动调用，source=internal, capability=kline_index_breadth）：
        provider = IndexBreadthComputeProvider()
        provider.connect()
        for result in provider.fetch(payload, policy):
            # result.rows = kline_index 整行（原值保留 + adv/dec 填齐）
        provider.disconnect()
    """

    source_name = "internal"

    def connect(self) -> None:
        self._connected = True
        self._log.info("IndexBreadthComputeProvider 已就绪（本地聚合，无需外部连接）")

    def disconnect(self) -> None:
        self._connected = False

    def health_check(self) -> bool:
        from zephyr.data import ch_reader

        try:
            return ch_reader.count(_TBL_KLINE_DAILY, limit=1) >= 0
        except Exception as e:  # noqa: BLE001
            self._log.warning("健康检查失败: %s", e)
            return False

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """自算宇宙宽度→回填 kline_index 零宽度位→返回整行 FetchResult。"""
        start_time = time.monotonic()
        extra = payload.extra if isinstance(payload.extra, dict) else {}
        symbols = clean_symbols(list(payload.symbols) if payload.symbols else list(INDEX_UNIVERSE))
        lookback = int(extra.get("repair_lookback_days", REPAIR_LOOKBACK_DAYS))
        w_start, w_end = resolve_window(payload.start, payload.end, lookback)
        universes = sorted({INDEX_UNIVERSE[s] for s in symbols if s in INDEX_UNIVERSE})

        try:
            agg = self._load_agg(w_start, w_end, universes)
            zero_rows = self._load_zero_rows(symbols, w_start, w_end)
            rows, skipped = build_fill_rows(zero_rows, agg)
        except Exception as e:  # noqa: BLE001 — [ERROR_CONTRACT] 失败不抛
            log.error("广度进料失败 [%s~%s]: %s", w_start, w_end, e)
            yield FetchResult(
                table=payload.table,
                columns=list(WRITE_COLUMNS),
                rows=[],
                last_key=payload.end.isoformat(),
                elapsed_sec=time.monotonic() - start_time,
                error=str(e),
            )
            return

        log.info(
            "广度进料 %s~%s：目标 %d 标的/%d 宇宙，零宽度待修 %d 行 → 回填 %d 行，跳过 %d 行",
            w_start,
            w_end,
            len(symbols),
            len(universes),
            len(zero_rows),
            len(rows),
            len(skipped),
        )
        if skipped:
            # fail-visible：跳过=该日仍无宽度（消费端将落补位/告警线会点名），禁静默
            for it in skipped[:20]:
                log.warning("广度回填跳过 %s %s: %s", it["trade_date"], it["symbol"], it["reason"])
            if len(skipped) > 20:
                log.warning("广度回填跳过其余 %d 行（同因合并）", len(skipped) - 20)
        if not rows:
            log.warning(
                "广度进料 0 行回填（窗口 %s~%s 无零宽度待修行）——若上游断供未修则告警线应已点名",
                w_start,
                w_end,
            )

        yield FetchResult(
            table=payload.table,
            columns=list(WRITE_COLUMNS),
            rows=rows,
            last_key=payload.end.isoformat(),
            elapsed_sec=time.monotonic() - start_time,
            rows_fetched=len(rows),
            error=None,
        )

    # ── CH 读写 ──────────────────────────────────────────────────────────

    def _load_agg(
        self, start: datetime.date, end: datetime.date, universes: list[str]
    ) -> dict[tuple[str, str], dict[str, int]]:
        """CH 端宇宙聚合（TSV → {(date, universe): {adv,dec,n}}）。"""
        from zephyr.data import ch_reader

        if not universes:
            raise ValueError("无可用宇宙口径（注册表与标的交集为空）")
        warm_start = (start - datetime.timedelta(days=WARMUP_DAYS)).isoformat()
        sql = _SQL_UNIVERSE_AGG.format(
            cols=build_agg_columns(universes),
            warm_start=warm_start,
            start=start.isoformat(),
            end=end.isoformat(),
        )
        agg = parse_agg(ch_reader.query(sql), universes)
        if not agg:
            raise ValueError(f"{_TBL_KLINE_DAILY} 宇宙聚合空（{start}~{end}）——数据管道异常")
        return agg

    def _load_zero_rows(
        self, symbols: list[str], start: datetime.date, end: datetime.date
    ) -> list[dict[str, str]]:
        """读 kline_index FINAL 中宽度双零的整行（=待修位；官方有值行永不入列）。"""
        from zephyr.data import ch_reader

        if not symbols:
            return []
        sql = _SQL_ZERO_BREADTH_ROWS.format(
            cols=", ".join(WRITE_COLUMNS),
            table=_TBL_KLINE_INDEX,
            start=start.isoformat(),
            end=end.isoformat(),
            symbols=", ".join(f"'{s}'" for s in clean_symbols(symbols)),
        )
        return parse_tsv(ch_reader.query(sql), WRITE_COLUMNS)
