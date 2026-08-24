# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.limit_up_pool_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare SDK（ak.stock_zt_pool_em 东财涨停股池，延迟 import）; zephyr.data.table_registry（表名真源，调用期惰性解析）
# [CONSUMERS] （GAP-F-13 板块梯队明细 11 列后端数据腿；tasks.yaml 接线待 DDL 建表后排期）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 匿名访问；源字段全量保留（封板资金/首封/末封/炸板次数/连板/涨停统计/行业）；派生口径：seal_ratio=封板资金/流通市值（除零/缺失→None）、sealed_seconds=末封→15:00 收盘秒数（脏时间→None）；非法代码跳过不炸；源异常→空列表容错（对齐 _collect_limit_rows 口径）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-13 行
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采集/解析异常→log warning+空列表不抛；table=None 且 market_limit_up_pool 品类未注册→RuntimeError（fail-closed，报告标注 DDL 待执行）；trade_date 格式非法→ValueError（调用方契约违例）
# [TESTS] tests/zephyr/data/test_limit_up_pool_collector.py
# [A_module] module_id=MOD-DAT-limit_up_pool_ingest | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-DAT-limit_up_pool_ingest — 涨停池明细采集器（GAP-F-13）。

既有 limit_up_down 表只有 7 列（trade_date/symbol/name/close/pct_change/amount/
limit_type），而采集源 akshare stock_zt_pool_em（东财涨停股池）本身返回封板资金/
首次封板时间/最后封板时间/炸板次数/连板数/涨停统计/所属行业——源有字段没存。

裁定（2026-08-23 SECTOR 会话）：**不动既有 limit_up_down 表**（生产表 DDL 变更需
Owner 窗口），新建 c1_market.limit_up_pool 明细表承接全量字段。本模块=采集器+
解析层先行；DDL 建表（apply_schema.py）+ business_data_categories.yaml 品类登记
+ tasks.yaml 接线三件为 Owner 窗口待办（见 .runtime/construction_20260823/
reports/SECTOR_report.md §GAP-F-13）。

DDL 草稿（待统筹 CTR 评审后 apply_schema 执行）::

    CREATE TABLE IF NOT EXISTS c1_market.limit_up_pool
    (
        trade_date        Date,
        symbol            String,
        name              String,
        close             Decimal(18, 4),
        pct_change        Decimal(18, 4),
        amount            Decimal(18, 2),
        turnover_rate     Decimal(18, 4),
        float_market_cap  Decimal(20, 2),
        total_market_cap  Decimal(20, 2),
        seal_amount       Nullable(Decimal(20, 2)),
        seal_ratio        Nullable(Decimal(18, 6)),
        first_seal_time   Nullable(String),
        last_seal_time    Nullable(String),
        sealed_seconds    Nullable(Int32),
        open_board_count  Nullable(Int32),
        consec_limit      Nullable(Int32),
        limit_stat        String,
        industry          LowCardinality(String),
        data_source       LowCardinality(String) DEFAULT 'akshare',
        ingest_ts         DateTime64(3, 'UTC') DEFAULT now(),
        exchange          LowCardinality(String) MATERIALIZED <同 limit_up_down 前缀推导式>,
        symbol_canonical  String MATERIALIZED <同 limit_up_down universal 推导式>
    )
    ENGINE = ReplacingMergeTree
    PARTITION BY toYYYYMM(trade_date)
    ORDER BY trade_date, symbol

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: akshare stock_zt_pool_em 东财涨停股池（单日全量）
#   fields: 代码/名称/涨跌幅/最新价/成交额/流通市值/总市值/换手率/封板资金/首次封板时间/最后封板时间/炸板次数/涨停统计/连板数/所属行业
# 层: 特征
# - id: F1
#   name_zh: 封单比派生
#   formula: seal_ratio = 封板资金/流通市值（>0 才出，否则 None）
# - id: F2
#   name_zh: 封住时间派生
#   formula: sealed_seconds = 15:00:00 − 最后封板时间（秒；脏时间 None）
# 层: 算法
# - id: A1
#   name_zh: 解析层（纯函数）
#   desc: parse_zt_pool_rows 行映射+时间规整+派生+非法代码跳过
# - id: A2
#   name_zh: 采集与落库
#   desc: fetch（延迟 import akshare，异常→空列表）→ collect 参数化 INSERT（table 惰性经 table_registry 解析）
# 层: 输出
# - id: O1
#   name_zh: LimitUpPoolEntry 行集 / INSERT 行数
#   intro: 19 列 INSERT_COLUMNS 对齐 DDL 草稿列序；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> F1
# A1 --> F2
# A1,F1,F2 --> A2
# A2 --> O1
"""

from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Final, Iterable, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "CATEGORY_ID",
    "INSERT_COLUMNS",
    "LimitUpPoolEntry",
    "collect_limit_up_pool",
    "fetch_limit_up_pool",
    "parse_zt_pool_rows",
    "to_csv",
]

#: 品类真源 category_id（business_data_categories.yaml 登记=Owner 窗口待办）
CATEGORY_ID: Final = "market_limit_up_pool"

#: INSERT 列序（对齐模块 docstring DDL 草稿；exchange/symbol_canonical 为 MATERIALIZED 派生列不入列）
INSERT_COLUMNS: Final = (
    "trade_date",
    "symbol",
    "name",
    "close",
    "pct_change",
    "amount",
    "turnover_rate",
    "float_market_cap",
    "total_market_cap",
    "seal_amount",
    "seal_ratio",
    "first_seal_time",
    "last_seal_time",
    "sealed_seconds",
    "open_board_count",
    "consec_limit",
    "limit_stat",
    "industry",
    "data_source",
)

_MARKET_CLOSE_SECONDS: Final = 15 * 3600  # 15:00:00 A 股收盘
_HHMMSS_RE: Final = re.compile(r"^(\d{2}):(\d{2}):(\d{2})$")


@dataclass(frozen=True, slots=True)
class LimitUpPoolEntry:
    """涨停池明细行（stock_zt_pool_em 源字段全量 + 封单比/封住秒数派生）。"""

    trade_date: str  # YYYY-MM-DD
    symbol: str  # 6 位裸码（exchange/symbol_canonical 由 DDL MATERIALIZED 派生）
    name: str
    close: float | None
    pct_change: float | None
    amount: float | None
    turnover_rate: float | None  # 换手率 %
    float_market_cap: float | None  # 流通市值（元）
    total_market_cap: float | None  # 总市值（元）
    seal_amount: float | None  # 封板资金（元）
    seal_ratio: float | None  # 封单比 = 封板资金/流通市值
    first_seal_time: str | None  # 首次封板 HH:MM:SS
    last_seal_time: str | None  # 最后封板 HH:MM:SS
    sealed_seconds: int | None  # 封住时间 = 末封→15:00 秒数
    open_board_count: int | None  # 炸板次数（开板次数）
    consec_limit: int | None  # 连板数
    limit_stat: str  # 涨停统计（源原始口径，如 "3/2"）
    industry: str  # 所属行业
    data_source: str = "akshare"


def _safe_float(v: Any) -> float | None:
    """宽松浮点解析（None/NaN/空串/非法 → None）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f != f:  # NaN
        return None
    return f


def _safe_int(v: Any) -> int | None:
    """宽松整型解析（浮点截断取整；非法 → None）。"""
    f = _safe_float(v)
    return int(f) if f is not None else None


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _norm_hhmmss(v: Any) -> str | None:
    """封板时间规整：int 92500 / str '143000' / '09:30:00' → 'HH:MM:SS'；脏值 → None。"""
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        m = _HHMMSS_RE.match(s)
        if m:
            hh, mm, ss = int(m[1]), int(m[2]), int(m[3])
        else:
            digits = re.sub(r"\D", "", s)
            if not digits:
                return None
            digits = digits.zfill(6)[-6:]
            hh, mm, ss = int(digits[:2]), int(digits[2:4]), int(digits[4:6])
    else:
        f = _safe_int(v)
        if f is None:
            return None
        digits = str(f).zfill(6)[-6:]
        hh, mm, ss = int(digits[:2]), int(digits[2:4]), int(digits[4:6])
    if hh > 23 or mm > 59 or ss > 59:
        return None
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def _sealed_seconds(last_seal: str | None) -> int | None:
    """封住时间 = 末封 → 15:00 收盘秒数；末封缺失/超收盘 → None。"""
    if last_seal is None:
        return None
    hh, mm, ss = (int(p) for p in last_seal.split(":"))
    sec = hh * 3600 + mm * 60 + ss
    if sec > _MARKET_CLOSE_SECONDS:
        return None
    return _MARKET_CLOSE_SECONDS - sec


def parse_zt_pool_rows(
    rows: Iterable[Mapping[str, Any]],
    trade_date: str | date | datetime,
) -> list[LimitUpPoolEntry]:
    """解析层（纯函数不触网不触库）：stock_zt_pool_em 行映射 + 封单比/封住秒数派生。

    Args:
        rows: 映射行迭代（DataFrame.iterrows() 的 row 具 .get，兼容 Mapping）。
        trade_date: 数据日（str 须 YYYY-MM-DD，非法抛 ValueError fail-closed）。

    Returns:
        LimitUpPoolEntry 列表；非法代码（空/非 6 位数字）跳过。
    """
    d = _normalize_date(trade_date)
    iso_date = d.isoformat()
    out: list[LimitUpPoolEntry] = []
    for row in rows:
        raw = str(row.get("代码") or "").strip()
        sym = raw.zfill(6)
        if not (raw and len(sym) == 6 and sym.isdigit()):
            continue
        seal_amount = _safe_float(row.get("封板资金"))
        float_mcap = _safe_float(row.get("流通市值"))
        seal_ratio: float | None = None
        if seal_amount is not None and float_mcap is not None and float_mcap > 0:
            seal_ratio = seal_amount / float_mcap
        first_seal = _norm_hhmmss(row.get("首次封板时间"))
        last_seal = _norm_hhmmss(row.get("最后封板时间"))
        out.append(
            LimitUpPoolEntry(
                trade_date=iso_date,
                symbol=sym,
                name=str(row.get("名称") or ""),
                close=_safe_float(row.get("最新价")),
                pct_change=_safe_float(row.get("涨跌幅")),
                amount=_safe_float(row.get("成交额")),
                turnover_rate=_safe_float(row.get("换手率")),
                float_market_cap=float_mcap,
                total_market_cap=_safe_float(row.get("总市值")),
                seal_amount=seal_amount,
                seal_ratio=seal_ratio,
                first_seal_time=first_seal,
                last_seal_time=last_seal,
                sealed_seconds=_sealed_seconds(last_seal),
                open_board_count=_safe_int(row.get("炸板次数")),
                consec_limit=_safe_int(row.get("连板数")),
                limit_stat=str(row.get("涨停统计") or ""),
                industry=str(row.get("所属行业") or ""),
            )
        )
    return out


def fetch_limit_up_pool(
    trade_date: str | date | datetime,
    ak: Any | None = None,
) -> list[LimitUpPoolEntry]:
    """采集层：单日 stock_zt_pool_em 拉取 + 解析（延迟 import akshare 不触模块级代理补丁）。

    源接口异常/空帧 → log warning + 空列表（对齐 _collect_limit_rows 容错口径）。
    """
    d = _normalize_date(trade_date)
    if ak is None:
        import akshare as ak_mod

        ak = ak_mod
    try:
        df = ak.stock_zt_pool_em(date=d.strftime("%Y%m%d"))
    except Exception as e:  # noqa: BLE001 — 源失败容错不抛
        logger.warning("stock_zt_pool_em(%s) 失败: %s", d.isoformat(), e)
        return []
    if df is None or len(df) == 0:
        return []
    # DataFrame 行 → Mapping 迭代（解析层纯函数入口）
    return parse_zt_pool_rows((r for _, r in df.iterrows()), d)


def _resolve_table(table: str | None) -> str:
    """表名解析：显式注入优先；None 经 table_registry 真源解析（未注册 → RuntimeError fail-closed）。"""
    if table:
        return table
    try:
        from zephyr.data.table_registry import get_registry

        return get_registry().table(CATEGORY_ID)
    except KeyError as e:
        raise RuntimeError(
            f"品类 {CATEGORY_ID} 未在 business_data_categories.yaml 注册"
            "（limit_up_pool DDL 建表+品类登记为 Owner 窗口待办，见 SECTOR 报告）"
        ) from e


def collect_limit_up_pool(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
    ak: Any | None = None,
    table: str | None = None,
) -> int:
    """采集+落库一日涨停池明细。

    Args:
        trade_date: 数据日。
        ch_client: clickhouse-driver 鸭子类型；None 时延迟取 ch_writer.get_client。
        ak: akshare 模块（测试注入假数据源位）；None 延迟 import。
        table: 目标表全限定名（测试/编排注入位）；None 经 table_registry 解析。

    Returns:
        落库行数（源空/失败 → 0 不建 INSERT）。

    Raises:
        RuntimeError: table=None 且品类未注册（DDL 待执行待办，fail-closed）。
        ValueError: trade_date 格式非法（调用方契约违例）。
    """
    full_table = _resolve_table(table)
    if ch_client is None:
        from zephyr.data.ch_writer import get_client

        ch_client = get_client()
    entries = fetch_limit_up_pool(trade_date, ak=ak)
    if not entries:
        return 0
    cols = ", ".join(INSERT_COLUMNS)
    rows = [tuple(getattr(e, c) for c in INSERT_COLUMNS) for e in entries]
    ch_client.execute(f"INSERT INTO {full_table} ({cols}) VALUES", rows)
    return len(rows)


def to_csv(
    entries: Iterable[LimitUpPoolEntry],
    path: str | Path,
    append: bool = False,
) -> str:
    """CSV 中间层（DDL 建表前的落地通道；幂等追加，header 不重复）。

    对齐 D3FUND 批模式（sector_fund_flow_collector.to_csv）：limit_up_pool 表
    DDL 待 Owner 窗口期间，涨停池明细（封板资金/首封/炸板次数）经本通道落地。

    Args:
        entries: 涨停池明细行迭代。
        path: 目标 CSV 路径（父目录自动创建）。
        append: True 追加（已有文件不重复写 header）；False 覆盖。

    Returns:
        写入的文件路径；entries 空 → 空串不建文件。
    """
    rows = list(entries)
    if not rows:
        return ""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    write_header = not (append and p.exists())
    with p.open("a" if append else "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(INSERT_COLUMNS))
        if write_header:
            writer.writeheader()
        for e in rows:
            writer.writerow({c: getattr(e, c) for c in INSERT_COLUMNS})
    return str(p)
