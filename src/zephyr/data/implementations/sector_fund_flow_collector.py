# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.sector_fund_flow_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare SDK（ak.stock_fund_flow_industry / ak.stock_fund_flow_concept 同花顺即时资金流，延迟 import）; zephyr.data.table_registry（表名真源，调用期惰性解析）
# [CONSUMERS] （GAP-F-16 逆势榜资金卡注入位数据源；tasks.yaml 接线待 DDL 建表后排期）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 匿名访问；源字段全量保留（行业指数/涨跌幅/流入/流出/净额/公司家数/领涨股）；金额为同花顺源原始口径（亿元，当日累计）；空名/数值全空行跳过不炸；单类型源异常→该类型空列表容错（对齐 _collect_limit_rows 口径）；冻结 dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-16 行
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采集/解析异常→log warning+空列表不抛；table=None 且 market_sector_fund_flow 品类未注册→RuntimeError（fail-closed，报告标注 DDL 待执行）；sector_type 非 industry/concept→ValueError（调用方契约违例）
# [TESTS] tests/zephyr/data/test_sector_fund_flow_collector.py
# [A_module] module_id=MOD-DAT-sector_fund_flow_ingest | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-DAT-sector_fund_flow_ingest — 板块级资金流快照采集器（D3 / GAP-F-16）。

背景（源调查 2026-08-24，akshare 1.18.75 实测）：
    板块级**分钟**资金流 akshare 直接接口不存在——东财板块资金流历史走
    push2his fflow/daykline（klt=101 日级），其分钟端点 fflow/kline 对板块
    secid=90.BKxxxx 返回 rc=102 空数据（个股分钟资金流同端点亦被反爬断连）；
    且东财 push2/push2his 端点自本机持续 RemoteDisconnected（与 tasks.yaml
    2026-08-14 东财反爬留痕同源）。可用源=**同花顺即时资金流快照**
    （ak.stock_fund_flow_industry / stock_fund_flow_concept，symbol="即时"）：
    当日累计流入/流出/净额，90 行业+387 概念，实测 3/3 成功 ~0.2s/次。

分钟粒度实现路径：盘中定时轮询快照（净额为当日累计值），相邻快照差分即
分钟区间净流入；消费方（逆势榜卡2 段内主力净流入）= 段末累计 − 段前累计。
轮询排期（1min 对齐 kline_sector_intraday 粒度）属 tasks.yaml/scheduler 接线，
DDL 建表后排期（Owner 窗口待办）。

裁定（对齐 2026-08-23 SECTOR 会话 limit_up_pool 先例）：**不直建表**。
本模块=采集器+解析层+CSV 中间层先行；DDL 建表（apply_schema.py）+
business_data_categories.yaml 品类登记 + tasks.yaml 接线三件为 Owner 窗口
待办（见 .runtime/construction_20260823/reports/D3FUND_report.md）。

DDL 草稿（待统筹 CTR 评审后 apply_schema 执行）::

    CREATE TABLE IF NOT EXISTS c1_market.sector_fund_flow
    (
        trade_date        Date,
        timestamp         DateTime,
        sector_type       LowCardinality(String),   -- industry/concept
        sector_name       String,                   -- 同花顺板块名（JOIN sector_meta 键）
        sector_index      Nullable(Decimal(18, 4)),
        pct_change        Nullable(Decimal(18, 4)),
        inflow_amount     Nullable(Decimal(20, 4)), -- 流入资金（亿元，当日累计，THS 原始口径）
        outflow_amount    Nullable(Decimal(20, 4)), -- 流出资金（亿元，当日累计）
        net_amount        Nullable(Decimal(20, 4)), -- 净额（亿元，当日累计；差分=区间净流入）
        company_count     Nullable(UInt32),
        lead_stock        String,
        lead_pct_change   Nullable(Decimal(18, 4)),
        data_source       LowCardinality(String) DEFAULT 'ths',
        ingest_ts         DateTime64(3, 'UTC') DEFAULT now()
    )
    ENGINE = ReplacingMergeTree
    PARTITION BY toYYYYMM(trade_date)
    ORDER BY (sector_type, sector_name, timestamp)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: akshare stock_fund_flow_industry(symbol="即时") 同花顺行业资金流快照（90 行）
#   fields: 行业/行业指数/行业-涨跌幅/流入资金/流出资金/净额/公司家数/领涨股/领涨股-涨跌幅/当前价
# - id: I2
#   name: akshare stock_fund_flow_concept(symbol="即时") 同花顺概念资金流快照（387 行，同构）
# 层: 算法
# - id: A1
#   name_zh: 解析层（纯函数）
#   desc: parse_ths_fund_flow_rows 行映射+宽松数值解析+空名/全空行跳过
# - id: A2
#   name_zh: 采集与落库/落盘
#   desc: fetch（延迟 import akshare，单类型异常→该类型空）→ collect 参数化 INSERT（table 惰性经 table_registry 解析）/ to_csv 中间层
# 层: 输出
# - id: O1
#   name_zh: SectorFundFlowEntry 行集 / INSERT 行数 / CSV 路径
#   intro: 13 列 INSERT_COLUMNS 对齐 DDL 草稿列序；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Final, Iterable, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "CATEGORY_ID",
    "INSERT_COLUMNS",
    "SECTOR_TYPES",
    "SectorFundFlowEntry",
    "collect_sector_fund_flow",
    "fetch_sector_fund_flow",
    "parse_ths_fund_flow_rows",
    "to_csv",
]

#: 品类真源 category_id（business_data_categories.yaml 登记=Owner 窗口待办）
CATEGORY_ID: Final = "market_sector_fund_flow"

#: 支持的板块类型 → akshare 接口名
SECTOR_TYPES: Final = {"industry": "stock_fund_flow_industry", "concept": "stock_fund_flow_concept"}

#: INSERT 列序（对齐模块 docstring DDL 草稿；ingest_ts 为 DEFAULT 列不入列）
INSERT_COLUMNS: Final = (
    "trade_date",
    "timestamp",
    "sector_type",
    "sector_name",
    "sector_index",
    "pct_change",
    "inflow_amount",
    "outflow_amount",
    "net_amount",
    "company_count",
    "lead_stock",
    "lead_pct_change",
    "data_source",
)


@dataclass(frozen=True, slots=True)
class SectorFundFlowEntry:
    """板块资金流快照行（THS 即时帧全量字段；金额=亿元，当日累计口径）。"""

    trade_date: str  # YYYY-MM-DD（由 timestamp 派生）
    timestamp: str  # YYYY-MM-DD HH:MM:SS（快照采集时刻=轮询时刻）
    sector_type: str  # industry/concept
    sector_name: str  # 同花顺板块名（消费方经 sector_meta JOIN 映射 881xxx）
    sector_index: float | None  # 行业指数
    pct_change: float | None  # 行业涨跌幅 %
    inflow_amount: float | None  # 流入资金（亿元，当日累计）
    outflow_amount: float | None  # 流出资金（亿元，当日累计）
    net_amount: float | None  # 净额（亿元，当日累计；相邻快照差分=区间净流入）
    company_count: int | None  # 公司家数
    lead_stock: str  # 领涨股
    lead_pct_change: float | None  # 领涨股涨跌幅 %
    data_source: str = "ths"


def _safe_float(v: Any) -> float | None:
    """宽松浮点解析（None/NaN/空串/'--'/非法 → None）。"""
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


def _normalize_ts(ts: str | date | datetime) -> datetime:
    """归一化快照时刻（str 须 'YYYY-MM-DD HH:MM[:SS]' 或 'YYYY-MM-DD'，非法抛 ValueError）。"""
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, date):
        return datetime(ts.year, ts.month, ts.day)
    s = str(ts).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"ts 非真实时间（须 YYYY-MM-DD[ HH:MM[:SS]]）: {ts!r}")


def parse_ths_fund_flow_rows(
    rows: Iterable[Mapping[str, Any]],
    sector_type: str,
    ts: str | date | datetime,
) -> list[SectorFundFlowEntry]:
    """解析层（纯函数不触网不触库）：THS 即时资金流帧行映射。

    Args:
        rows: 映射行迭代（DataFrame.iterrows() 的 row 具 .get，兼容 Mapping）。
        sector_type: industry/concept（其余抛 ValueError fail-closed）。
        ts: 快照时刻（date/datetime/str；非法抛 ValueError）。

    Returns:
        SectorFundFlowEntry 列表；空板块名/流入流出净额全空行跳过。
    """
    if sector_type not in SECTOR_TYPES:
        raise ValueError(f"sector_type 须为 {sorted(SECTOR_TYPES)}: {sector_type!r}")
    snap = _normalize_ts(ts)
    ts_str = snap.strftime("%Y-%m-%d %H:%M:%S")
    iso_date = snap.date().isoformat()
    out: list[SectorFundFlowEntry] = []
    for row in rows:
        name = str(row.get("行业") or "").strip()
        if not name:
            continue
        inflow = _safe_float(row.get("流入资金"))
        outflow = _safe_float(row.get("流出资金"))
        net = _safe_float(row.get("净额"))
        if inflow is None and outflow is None and net is None:
            continue  # 资金流三值全空 → 无效行
        out.append(
            SectorFundFlowEntry(
                trade_date=iso_date,
                timestamp=ts_str,
                sector_type=sector_type,
                sector_name=name,
                sector_index=_safe_float(row.get("行业指数")),
                pct_change=_safe_float(row.get("行业-涨跌幅")),
                inflow_amount=inflow,
                outflow_amount=outflow,
                net_amount=net,
                company_count=_safe_int(row.get("公司家数")),
                lead_stock=str(row.get("领涨股") or ""),
                lead_pct_change=_safe_float(row.get("领涨股-涨跌幅")),
            )
        )
    return out


def _fetch_one_type(ak: Any, sector_type: str, ts: datetime) -> list[SectorFundFlowEntry]:
    """单类型拉取+解析；源异常/空帧 → log warning + 空列表（容错口径对齐 limit_up_pool）。"""
    func_name = SECTOR_TYPES[sector_type]
    try:
        df = getattr(ak, func_name)(symbol="即时")
    except Exception as e:  # noqa: BLE001 — 源失败容错不抛
        logger.warning("%s(即时) 失败: %s", func_name, e)
        return []
    if df is None or len(df) == 0:
        return []
    return parse_ths_fund_flow_rows((r for _, r in df.iterrows()), sector_type, ts)


def fetch_sector_fund_flow(
    ts: str | date | datetime | None = None,
    ak: Any | None = None,
) -> list[SectorFundFlowEntry]:
    """采集层：行业+概念双类型即时快照拉取（延迟 import akshare 不触模块级代理补丁）。

    Args:
        ts: 快照时刻注入位（测试/编排）；None 取当前本地时间。
        ak: akshare 模块（测试注入假数据源位）；None 延迟 import。

    Returns:
        SectorFundFlowEntry 列表（industry 在前 concept 在后）；单类型失败仅该类型缺。
    """
    snap = _normalize_ts(ts) if ts is not None else datetime.now()  # 本地交易时段口径（北京时间，naive）
    if ak is None:
        import akshare as ak_mod

        ak = ak_mod
    out: list[SectorFundFlowEntry] = []
    for sector_type in SECTOR_TYPES:
        out.extend(_fetch_one_type(ak, sector_type, snap))
    return out


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
            "（sector_fund_flow DDL 建表+品类登记为 Owner 窗口待办，见 D3FUND 报告）"
        ) from e


def collect_sector_fund_flow(
    ts: str | date | datetime | None = None,
    ch_client: Any | None = None,
    ak: Any | None = None,
    table: str | None = None,
) -> int:
    """采集+落库一次板块资金流快照（行业+概念）。

    Args:
        ts: 快照时刻注入位；None 取当前时间。
        ch_client: clickhouse-driver 鸭子类型；None 时延迟取 ch_writer.get_client。
        ak: akshare 模块（测试注入假数据源位）；None 延迟 import。
        table: 目标表全限定名（测试/编排注入位）；None 经 table_registry 解析。

    Returns:
        落库行数（源空/失败 → 0 不建 INSERT）。

    Raises:
        RuntimeError: table=None 且品类未注册（DDL 待执行待办，fail-closed）。
        ValueError: ts 格式非法（调用方契约违例）。
    """
    full_table = _resolve_table(table)
    if ch_client is None:
        from zephyr.data.ch_writer import get_client

        ch_client = get_client()
    entries = fetch_sector_fund_flow(ts=ts, ak=ak)
    if not entries:
        return 0
    cols = ", ".join(INSERT_COLUMNS)
    rows = [tuple(getattr(e, c) for c in INSERT_COLUMNS) for e in entries]
    ch_client.execute(f"INSERT INTO {full_table} ({cols}) VALUES", rows)
    return len(rows)


def to_csv(
    entries: Iterable[SectorFundFlowEntry],
    path: str | Path,
    append: bool = False,
) -> str:
    """CSV 中间层（DDL 建表前的落地通道；幂等追加，header 不重复）。

    Args:
        entries: 快照行迭代。
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
