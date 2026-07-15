# [BLUEPRINT] MOD-L00-001 | docs/02_enterprise_architecture/05_dataflow_architecture/data_inventory.md
# [MODULE] scripts.governance.d5_architecture.generators.generate_data_inventory
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS] 人工查看data_inventory.md
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读ClickHouse元数据;输出到05_dataflow_architecture/
# [MODIFY-GUARD] 修改需通过维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse不可用→exit 1;无业务表→exit 2
# [TESTS]
# [TTL] permanent
"""G-inventory: 扫描 ClickHouse 生成业务数据清单 MD

真源链：
  ClickHouse 业务数据库（实时扫描，真源）
    → 本生成器查询 system.tables/system.parts 元数据
    → data_inventory.md（自动派生产物，禁止手工编辑）

输出结构（精简版，人类可读）：
  1. 总览（业务表总数/非空表数/数据总行数）
  2. 按数据库分节（c1_market / c3_fundamental 等）
  3. 每节一个表格：表名 | 中文名 | 起始时间 | 截止时间 | 标的数 | 总行数
  4. 字段说明

查询优化：用 system.tables/system.parts 元数据（秒级），不扫描实际数据。
         count(DISTINCT symbol) 只对小表（<1000万行）查，大表跳过。

用法
----
    python scripts/governance/d5_architecture/generators/generate_data_inventory.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# ch_reader 在 src/zephyr/data/ 下
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

__manifest__ = """
args: []
description: 'G-inventory: 扫描 ClickHouse 生成业务数据清单 MD'
dimensions:
- D5
priority: P2
timeout_seconds: 120
warn_only: false
"""

OUTPUT_PATH = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture" / "data_inventory.md"
)

REQUIREMENTS_PATH = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture" / "data_acquisition_requirements.yaml"
)

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_TABLES = "SELECT database, name, total_rows FROM system.tables WHERE database IN ('{db_list}') ORDER BY database, name"
_SQL_PARTS_DATES_BATCH = "SELECT database, table, min(min_date) as min_d, max(max_date) as max_d FROM system.parts WHERE active = 1 AND database IN ('{db_list}') GROUP BY database, table"
_SQL_COLUMNS_BATCH = "SELECT database, table, name FROM system.columns WHERE database IN ('{db_list}')"
_SQL_COLUMNS_SINGLE = "SELECT name FROM system.columns WHERE database='{db}' AND table='{table}'"
_SQL_DATE_RANGE = "SELECT min({date_col}), max({date_col}) FROM {db}.{table}"
_SQL_SYMBOL_UNIQ = "SELECT uniq({symbol_col}) FROM {table_name}"
_SQL_TABLE_ROWS = "SELECT total_rows FROM system.tables WHERE database='{db}' AND name='{table}'"
_SQL_PARTS_DATES_SINGLE = "SELECT min(min_date), max(max_date) FROM system.parts WHERE database='{db}' AND table='{table}' AND active=1"

# 业务数据库列表
_BUSINESS_DBS = ("c1_market", "c2_factor", "c3_fundamental", "c4_reference")

# 日期列优先级（从高到低）
_DATE_COL_PRIORITY = (
    "trade_date", "announce_date", "end_date", "report_period",
    "cal_date", "date", "datetime",
)

# 标的列优先级（从高到低）
_SYMBOL_COL_PRIORITY = (
    "symbol", "ts_code", "stock_code", "news_id", "code",
    "etf_code", "sector_code", "index_code", "board_code",
    "indicator_name", "con_code", "stock_id",
)

# ============================================================
# 10层数据分层体系（真源：data_retention_contract.yaml §2）
# ============================================================
_LAYER_INFO: dict[str, dict] = {
    "L1":  {"name": "Tick执行层",       "category": "信号", "freq": "3秒",       "desc": "逐笔成交/指数快照/集合竞价，用于做T回测和滑点建模"},
    "L2":  {"name": "分钟时机层",       "category": "信号", "freq": "1-60min",   "desc": "分钟K线，用于日内入场时机和动量信号"},
    "L3":  {"name": "日K趋势层",        "category": "信号", "freq": "日/周/月",   "desc": "日K线/复权因子/估值/指数K线，用于择时、趋势、选股"},
    "L4":  {"name": "资金面层",         "category": "信号", "freq": "日",        "desc": "融资融券/大宗交易/龙虎榜/资金流向，用于主力资金动向分析"},
    "L5":  {"name": "基本面层",         "category": "信号", "freq": "季度",      "desc": "财务三表/财务指标/分红配股/股权质押/股东数据"},
    "L6":  {"name": "新闻事件层",       "category": "信号", "freq": "实时",      "desc": "新闻/证券公告/分析师预测/解禁计划，用于事件驱动和情绪分析"},
    "L7":  {"name": "产业链关联层",     "category": "工具", "freq": "季度/年",    "desc": "产业链全景图/行业分类/板块指数，用于上下游传导分析"},
    "L8":  {"name": "衍生品跨市场层",   "category": "信号", "freq": "日",        "desc": "期货/期权/港股/美股，用于跨市场套利、对冲和波动率分析"},
    "L9":  {"name": "宏观层",           "category": "信号", "freq": "月/季",      "desc": "CPI/PMI/M2/社融/LPR等宏观经济指标，用于大类资产配置"},
    "L10": {"name": "静态元数据层",     "category": "基础", "freq": "月/年",      "desc": "标的列表/交易日历/指数成分，所有层的基础设施"},
}

# 表名 → 层的推断规则（按优先级从高到低匹配，基于 data_retention_contract.yaml 真源）
_LAYER_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("L1",  ("tick", "l2_tick", "auction", "realtime", "index_quote")),
    ("L2",  ("1min", "5min", "15min", "30min", "60min")),
    ("L3",  ("kline_daily", "kline_weekly", "kline_monthly", "adj_factor", "daily_valuation", "kline_index", "kline_sector")),
    ("L4",  ("margin", "block_trade", "dragon_tiger", "money_flow", "hk_connect", "limit_up_down", "stock_indicator")),
    ("L5",  ("balance_sheet", "income_statement", "cashflow", "financial_indicator", "main_business",
             "earnings_forecast", "express_report", "audit_opinion", "dividend", "rights_issue",
             "equity_pledge", "shareholder", "share_change", "repurchase")),
    ("L6",  ("news", "share_unlock", "analyst_forecast", "disclosure")),
    # L7 只匹配关联关系/行业分类/板块K线，不匹配列表/元数据（那些归 L10）
    ("L7",  ("industry_class", "sector_constituent", "concept_board_constituent", "sector_kline")),
    ("L8",  ("futures", "option", "convertible_bond", "kline_cb", "hk_kline", "kline_hk",
             "us_daily", "kline_us", "us_index", "kline_futures")),
    ("L9",  ("macro_data", "edb_data")),
    # L10 匹配所有列表/元数据/日历类表
    ("L10", ("stock_list", "trade_calendar", "index_constituent", "index_list", "index_weight",
             "etf_list", "etf_benchmark", "etf_nav", "lof_list", "convertible_bond_list",
             "hk_stock_list", "hk_trade_calendar", "st_stock_list",
             "sector_list", "sector_meta", "market_index_meta",
             "concept_board", "concept_sector")),
]


def _infer_layer(table_name: str) -> str:
    """根据表名推断数据层。未匹配的表默认归 L10。"""
    t = table_name.lower()
    for layer, keywords in _LAYER_RULES:
        for kw in keywords:
            if kw in t:
                return layer
    return "L10"

# 表中文名映射
_TABLE_ZH: dict[str, str] = {
    # c1_market
    "_pepb_staging": "PE/PB暂存表",
    "adj_factor": "复权因子",
    "analyst_forecast": "分析师预测",
    "auction_snapshot": "集合竞价快照",
    "block_trade": "大宗交易",
    "convertible_bond_iv": "可转债隐含波动率",
    "convertible_bond_list": "可转债列表",
    "daily_kline": "A股日K线（原始）",
    "daily_valuation": "每日估值",
    "dragon_tiger": "龙虎榜",
    "etf_benchmark": "ETF基准",
    "etf_kline_15min": "ETF15分钟K线",
    "etf_kline_1min": "ETF1分钟K线",
    "etf_kline_30min": "ETF30分钟K线",
    "etf_kline_5min": "ETF5分钟K线",
    "etf_kline_60min": "ETF60分钟K线",
    "etf_list": "ETF列表",
    "futures_kline": "期货K线",
    "futures_position": "期货持仓",
    "futures_term_structure": "期货期限结构",
    "hk_daily_kline": "港股日K线",
    "hk_stock_list": "港股股票列表",
    "hk_trade_calendar": "港股交易日历",
    "index_constituent": "指数成分股",
    "index_kline": "指数日K线",
    "index_list": "指数列表",
    "index_quote": "指数报价",
    "industry_class": "行业分类",
    "kline_15min": "A股15分钟K线",
    "kline_1min": "A股1分钟K线",
    "kline_30min": "A股30分钟K线",
    "kline_5min": "A股5分钟K线",
    "kline_60min": "A股60分钟K线",
    "kline_daily": "A股日K线（前复权）",
    "kline_daily_hfq": "A股日K线（后复权）",
    "kline_daily_none": "A股日K线（不复权）",
    "kline_monthly": "A股月K线（前复权）",
    "kline_monthly_hfq": "A股月K线（后复权）",
    "kline_monthly_none": "A股月K线（不复权）",
    "kline_weekly": "A股周K线（前复权）",
    "kline_weekly_hfq": "A股周K线（后复权）",
    "kline_weekly_none": "A股周K线（不复权）",
    "lof_kline_15min": "LOF15分钟K线",
    "lof_kline_1min": "LOF1分钟K线",
    "lof_kline_30min": "LOF30分钟K线",
    "lof_kline_5min": "LOF5分钟K线",
    "lof_kline_60min": "LOF60分钟K线",
    "lof_list": "LOF列表",
    "macro_data": "宏观经济数据",
    "margin_trading": "融资融券",
    "money_flow": "资金流向",
    "option_iv_surface": "期权波动率曲面",
    "sector_kline": "板块指数K线",
    "stock_list": "A股股票列表",
    "tdx_market_index": "通达信板块指数",
    "tdx_sector_info": "通达信板块信息",
    "tick_data": "Tick数据（实时）",
    "tick_history": "Tick数据（历史）",
    "trade_calendar": "交易日历",
    "us_daily_kline": "美股日K线",
    "us_index": "美股指数",
    # c1_market 新增表
    "auction_book": "集合竞价簿",
    "block_trade_detail": "大宗交易明细",
    "concept_board": "概念板块",
    "concept_board_constituent": "概念板块成分股",
    "concept_sector": "概念板块列表",
    "edb_data": "EDB宏观数据",
    "etf_nav": "ETF净值",
    "futures_kline_qmt": "期货K线（QMT）",
    "hk_connect_flow": "沪深港通资金",
    "hk_kline": "港股K线",
    "index_weight": "指数权重",
    "kline_cb": "可转债K线",
    "kline_futures": "期货K线",
    "kline_hk_daily": "港股日K线",
    "kline_index": "指数K线",
    "kline_sector": "板块K线",
    "kline_us_daily": "美股日K线",
    "limit_up_down": "涨跌停",
    "market_index_meta": "市场指数元数据",
    "option_greeks": "期权Greeks",
    "option_kline": "期权K线",
    "realtime_snapshot": "实时快照",
    "sector_list": "板块列表",
    "sector_meta": "板块元数据",
    "st_stock_list": "ST股票列表",
    "stock_indicator": "股票指标",
    "kline_etf_15min": "ETF15分钟K线",
    "kline_etf_1min": "ETF1分钟K线",
    "kline_etf_30min": "ETF30分钟K线",
    "kline_etf_5min": "ETF5分钟K线",
    "kline_etf_60min": "ETF60分钟K线",
    "kline_lof_15min": "LOF15分钟K线",
    "kline_lof_1min": "LOF1分钟K线",
    "kline_lof_30min": "LOF30分钟K线",
    "kline_lof_5min": "LOF5分钟K线",
    "kline_lof_60min": "LOF60分钟K线",
    "l2_tick": "Level2 Tick数据",
    # c3_fundamental
    "audit_opinion": "审计意见",
    "balance_sheet": "资产负债表",
    "cashflow_statement": "现金流量表",
    "disclosure_plan": "财报披露计划",
    "dividend": "分红数据",
    "earnings_forecast": "业绩预告",
    "equity_pledge": "股权质押",
    "equity_pledge_detail": "股权质押明细",
    "equity_pledge_summary": "股权质押汇总",
    "express_report": "业绩快报",
    "financial_indicator": "财务指标",
    "income_statement": "利润表",
    "industry_class_ifind": "iFind行业分类",
    "main_business": "主营业务构成",
    "news_data": "新闻数据（爬虫）",
    "news_news_info": "新闻信息（tushare）",
    "news_security": "新闻-股票关联",
    "restricted_shares": "限售解禁",
    "rights_issue": "配股/分红方案",
    "sector_constituent": "板块成分股",
    "share_unlock": "限售解禁",
    "shareholder": "股东数据",
    "shareholder_count": "股东户数",
    "top10_circulating_shareholders": "十大流通股东",
    "top10_shareholders": "十大股东",
    # c3_fundamental 新增表
    "industry_class_suppl": "行业分类补充",
    "repurchase": "回购",
    "share_change": "股本变动",
}


# ============================================================
# ch_reader 查询辅助
# ============================================================
def _query_rows(sql: str) -> list[list]:
    """执行 CH 查询，返回 list[list]。兼容 ch_reader.query 的多种返回格式。

    使用 ch_reader（自动注入 FINAL），失败时返回空列表。
    """
    from zephyr.data import ch_reader
    try:
        result = ch_reader.query(sql)
    except Exception as e:
        print(f"CH query 失败: {e}", file=sys.stderr)
        return []

    # 字符串返回：TSV 格式，按 \n 分行，\t 分列
    if isinstance(result, str):
        lines = [ln for ln in result.strip().split("\n") if ln]
        return [ln.split("\t") for ln in lines]

    # list/tuple 返回
    if isinstance(result, (list, tuple)):
        rows = []
        for item in result:
            if isinstance(item, (list, tuple)):
                rows.append(list(item))
            else:
                rows.append([item])
        return rows

    # 其他类型
    return [[result]]


def _query_single(sql: str) -> str:
    """执行 CH 查询，返回第一行第一列的字符串值。"""
    rows = _query_rows(sql)
    if rows and rows[0]:
        return str(rows[0][0]) if rows[0][0] is not None else ""
    return ""


def _parse_int(s) -> int:
    """安全解析整数值。"""
    if s is None:
        return 0
    s = str(s).strip().replace(",", "")
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


# ============================================================
# 表扫描
# ============================================================
def _get_all_tables_batch() -> list[dict]:
    """一次性查询所有业务库的所有表基本信息（表名/库/行数）+ 从 system.parts 获取日期范围。

    用两条 SQL 批量获取，避免逐表查询导致 WSL 连接频繁断开。
    """
    db_list = "','".join(_BUSINESS_DBS)

    # 查询1：表名 + 行数
    rows = _query_rows(_SQL_TABLES.format(db_list=db_list))
    if not rows:
        return []

    # 查询2：日期范围（从 system.parts 聚合）
    date_rows = _query_rows(_SQL_PARTS_DATES_BATCH.format(db_list=db_list))
    date_map: dict[str, tuple[str, str]] = {}
    for r in date_rows:
        if len(r) >= 4:
            key = f"{r[0]}.{r[1]}"
            min_d = r[2] if r[2] else ""
            max_d = r[3] if r[3] else ""
            date_map[key] = (min_d, max_d)

    result = []
    for r in rows:
        if len(r) >= 3:
            key = f"{r[0]}.{r[1]}"
            min_d, max_d = date_map.get(key, ("", ""))
            result.append({
                "db": r[0],
                "table": r[1],
                "total_rows": _parse_int(r[2]),
                "min_date": min_d,
                "max_date": max_d,
            })
    return result


def _get_all_columns_batch() -> dict[str, set[str]]:
    """一次性查询所有业务表的所有列名。返回 {db.table: {col1, col2, ...}}。"""
    db_list = "','".join(_BUSINESS_DBS)
    rows = _query_rows(_SQL_COLUMNS_BATCH.format(db_list=db_list))
    result: dict[str, set[str]] = {}
    for r in rows:
        if len(r) >= 3:
            key = f"{r[0]}.{r[1]}"
            result.setdefault(key, set()).add(r[2])
    return result


def _get_table_columns(db: str, table: str) -> set[str]:
    """获取表的所有列名。"""
    rows = _query_rows(
        _SQL_COLUMNS_SINGLE.format(db=db, table=table)
    )
    return {r[0] for r in rows if r and r[0]}


def _detect_column(columns: set[str], priority: tuple) -> str | None:
    """按优先级检测表中的列，返回第一个存在的列名。"""
    for col in priority:
        if col in columns:
            return col
    return None


def _query_date_range(db: str, table: str, date_col: str) -> tuple[str, str]:
    """从数据表的日期列查询 min/max 日期。返回 (min_date, max_date)。"""
    rows = _query_rows(
        _SQL_DATE_RANGE.format(date_col=date_col, db=db, table=table)
    )
    if rows and rows[0]:
        min_d = str(rows[0][0]) if rows[0][0] else ""
        max_d = str(rows[0][1]) if len(rows[0]) > 1 and rows[0][1] else ""
        # 1970-01-01 是 Date 纪元默认值，无意义
        if min_d == "1970-01-01":
            min_d = ""
        if max_d == "1970-01-01":
            max_d = ""
        return (min_d, max_d)
    return ("", "")


def _query_symbol_count(db: str, table: str, symbol_col: str) -> int:
    """用 uniq() 近似函数查标的数（秒级，不受表大小限制）。"""
    val = _query_single(
        _SQL_SYMBOL_UNIQ.format(symbol_col=symbol_col, table_name=f"{db}.{table}")
    )
    return _parse_int(val)


def _scan_table(db: str, table: str) -> dict:
    """扫描单张表，返回统计信息 dict。

    优化：用 system 元数据表查 count/date（秒级），只对小表查 count(DISTINCT symbol)。
    """
    full_table = f"{db}.{table}"

    # 1. 从 system.tables 元数据获取行数（秒级）
    total_rows = _parse_int(
        _query_single(
            _SQL_TABLE_ROWS.format(db=db, table=table)
        )
    )

    # 2. 从 system.parts 元数据获取日期范围（秒级）
    min_date = ""
    max_date = ""
    parts = _query_rows(
        _SQL_PARTS_DATES_SINGLE.format(db=db, table=table)
    )
    if parts and parts[0]:
        vals = parts[0]
        if len(vals) > 0 and vals[0]:
            min_date = str(vals[0])
        if len(vals) > 1 and vals[1]:
            max_date = str(vals[1])

    # 3. 用 uniq() 近似函数查标的数（秒级，不受表大小限制）
    symbol_count = ""
    if total_rows > 0:
        columns = _get_table_columns(db, table)
        symbol_col = _detect_column(columns, _SYMBOL_COL_PRIORITY)
        if symbol_col:
            symbol_count = _query_single(
                _SQL_SYMBOL_UNIQ.format(symbol_col=symbol_col, table_name=full_table)
            )

    # 1970-01-01 是 Date 纪元默认值，无意义，清空
    if min_date == "1970-01-01":
        min_date = ""
    if max_date == "1970-01-01":
        max_date = ""

    # 空表清空所有统计
    if total_rows == 0:
        min_date = ""
        max_date = ""
        symbol_count = ""

    return {
        "table": table,
        "full_table": full_table,
        "db": db,
        "zh": _TABLE_ZH.get(table, table),
        "layer": _infer_layer(table),
        "min_date": min_date,
        "max_date": max_date,
        "symbol_count": symbol_count,
        "total_rows": total_rows,
    }


# ============================================================
# MD 生成
# ============================================================
def _fmt_rows(n: int) -> str:
    """行数格式化（万/亿为单位）。"""
    if n == 0:
        return "0"
    if n < 10000:
        return str(n)
    if n < 100_000_000:
        return f"{n / 10000:.1f}万"
    return f"{n / 100_000_000:.2f}亿"


def _fmt_num(s: str) -> str:
    """数字字符串加千分位。空值返回 —。"""
    if not s:
        return "—"
    try:
        n = int(s)
        return f"{n:,}"
    except (ValueError, TypeError):
        return s


def _load_requirements() -> dict[str, dict]:
    """从 YAML 加载数据获取需求清单（P0-P3）。

    返回 {table_name: {priority, need, availability}}。
    YAML 不存在时返回空 dict（生成器降级为无需求列）。
    """
    if not REQUIREMENTS_PATH.exists():
        print(f"[WARN] 需求清单不存在: {REQUIREMENTS_PATH}", file=sys.stderr)
        return {}
    try:
        data = yaml.safe_load(REQUIREMENTS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] 需求清单加载失败: {e}", file=sys.stderr)
        return {}
    return data.get("requirements", {})


def _gen_header(today: date, all_tables: list[dict]) -> list[str]:
    """生成 frontmatter + 头部说明 + 层级总览表。"""
    total_tables = len(all_tables)
    non_empty = sum(1 for t in all_tables if t["total_rows"] > 0)
    total_rows = sum(t["total_rows"] for t in all_tables)

    # 按层统计
    layer_counts: dict[str, int] = {}
    layer_rows: dict[str, int] = {}
    for t in all_tables:
        layer_counts[t["layer"]] = layer_counts.get(t["layer"], 0) + 1
        layer_rows[t["layer"]] = layer_rows.get(t["layer"], 0) + t["total_rows"]

    lines = [
        "---",
        "doc_type: architecture_view",
        "title: 业务数据清单 / Data Inventory",
        'version: "3.0"',
        "status: active",
        f"date: {today.isoformat()}",
        "owner: auto-generator",
        "ttl: permanent",
        "---",
        "",
        "# 业务数据清单 / Data Inventory",
        "",
        "> **这个文档是给人看的**：按10层数据分层体系展示 ClickHouse 每张业务表「存了什么、从什么时候到什么时候、多少标的、多少行」。",
        "> **真源是 ClickHouse 实时扫描**，本文档是自动生成的派生产物，**禁止手工编辑**。",
        f"> **生成器**：`scripts/governance/d5_architecture/generators/generate_data_inventory.py`（可随时运行刷新）。",
        f"> **10层分层体系真源**：`docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml` §2。",
        f"> **需求补充真源**：`docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_requirements.yaml`（P0-P3优先级+可获取性）。",
        "",
        "---",
        "",
        "## 总览",
        "",
        f"- 业务表总数：**{total_tables}**",
        f"- 非空表数：**{non_empty}**",
        f"- 数据总行数：**{_fmt_rows(total_rows)}**",
        "",
        "### 10层数据分布",
        "",
        "| 层 | 名称 | 类别 | 频率 | 表数 | 总行数 | 说明 |",
        "|---|------|------|------|------|--------|------|",
    ]

    for layer_id in sorted(_LAYER_INFO.keys(), key=lambda x: int(x[1:])):
        info = _LAYER_INFO[layer_id]
        cnt = layer_counts.get(layer_id, 0)
        rows = _fmt_rows(layer_rows.get(layer_id, 0))
        lines.append(
            f"| {layer_id} | {info['name']} | {info['category']} | {info['freq']} | {cnt} | {rows} | {info['desc']} |"
        )

    lines.extend(["", "---", ""])
    return lines


def _gen_layer_section(layer_id: str, tables: list[dict], requirements: dict) -> list[str]:
    """生成单个数据层的表格章节（含需求补充列）。"""
    info = _LAYER_INFO[layer_id]
    lines = [
        f"## {layer_id} {info['name']}（{info['category']} / {info['freq']}）",
        "",
        f"> {info['desc']}",
        "",
        f"共 **{len(tables)}** 张表。",
        "",
        "| 表名 | 中文名 | 库 | 起始时间 | 截止时间 | 标的数 | 总行数 | 需补充 | 可获取性 |",
        "|------|--------|----|----------|----------|--------|--------|--------|---------|",
    ]
    for t in tables:
        min_d = t["min_date"] or "—"
        max_d = t["max_date"] or "—"
        sym = _fmt_num(t["symbol_count"]) if t["symbol_count"] else "—"
        rows = _fmt_num(str(t["total_rows"]))
        req = requirements.get(t["table"])
        if req:
            need = f"{req['priority']}: {req['need']}"
            avail = req.get("availability", "—")
        else:
            need = "—"
            avail = "—"
        lines.append(
            f"| `{t['table']}` | {t['zh']} | {t['db']} | {min_d} | {max_d} | {sym} | {rows} | {need} | {avail} |"
        )
    lines.append("")
    return lines


def _gen_footer() -> list[str]:
    """生成字段说明。"""
    return [
        "---",
        "",
        "## 字段说明",
        "",
        "- **表名**：ClickHouse 中的表名（不含库名前缀）。",
        "- **中文名**：表中文名映射字典，不在字典中的表显示表名本身。",
        "- **起始时间 / 截止时间**：从 `system.parts` 元数据获取的 `min_date` / `max_date`（秒级查询，不扫描实际数据）。",
        "  空表或无日期分区的表显示 —。",
        "- **标的数**：自动检测标的字段（优先级：symbol > ts_code > stock_code > news_id > code > etf_code > sector_code > ...）的 `uniq()` 近似值（秒级查询）。",
        "  无标的字段的表（如交易日历、资金渠道汇总）显示 —。",
        "- **总行数**：从 `system.tables` 元数据获取的 `total_rows`（秒级查询，不扫描实际数据）。",
        "- **需补充**：数据获取缺口（仅空表登记），来自 `data_acquisition_requirements.yaml`。",
        "  已有数据的表显示 —。仅行数为 0 的空表才登记需求。",
        "- **可获取性**：数据获取方式验证状态，来自 `data_acquisition_requirements.yaml`。",
    ]


# ============================================================
# 主入口
# ============================================================
def main() -> int:
    """主入口：批量扫描 ClickHouse → 按10层分组生成 data_inventory.md。"""
    today = date.today()

    # 1. 批量获取所有表基本信息（单条 SQL，避免连接频繁断开）
    print("批量查询所有业务表基本信息...", file=sys.stderr)
    batch_tables = _get_all_tables_batch()
    if not batch_tables:
        print("[ERROR] 无法连接 ClickHouse 或未找到业务表", file=sys.stderr)
        return 1
    print(f"  获取到 {len(batch_tables)} 张表", file=sys.stderr)

    # 2. 批量获取所有列名
    print("批量查询所有表列名...", file=sys.stderr)
    batch_columns = _get_all_columns_batch()
    print(f"  获取到 {len(batch_columns)} 张表的列信息", file=sys.stderr)

    # 3. 组装表信息
    all_tables: list[dict] = []
    for t in batch_tables:
        db = t["db"]
        table = t["table"]
        full_table = f"{db}.{table}"
        columns = batch_columns.get(full_table, set())

        # 检测日期列和标的列
        date_col = _detect_column(columns, _DATE_COL_PRIORITY)
        symbol_col = _detect_column(columns, _SYMBOL_COL_PRIORITY)

        # 如果 system.tables 没有 min/max_date，尝试从 system.parts 获取
        min_date = t["min_date"]
        max_date = t["max_date"]
        if (not min_date or not max_date) and date_col and t["total_rows"] > 0:
            d_min, d_max = _query_date_range(db, table, date_col)
            if d_min:
                min_date = d_min
            if d_max:
                max_date = d_max

        # 标的数（只对非空表且检测到标的列的查）
        symbol_count = 0
        if symbol_col and t["total_rows"] > 0:
            symbol_count = _query_symbol_count(db, table, symbol_col)

        all_tables.append({
            "table": table,
            "full_table": full_table,
            "db": db,
            "zh": _TABLE_ZH.get(table, table),
            "layer": _infer_layer(table),
            "min_date": min_date,
            "max_date": max_date,
            "symbol_count": symbol_count,
            "total_rows": t["total_rows"],
        })

    # 4. 按数据层分组
    layer_tables: dict[str, list[dict]] = {}
    for t in all_tables:
        layer_tables.setdefault(t["layer"], []).append(t)

    # 5. 加载数据获取需求清单
    print("加载数据获取需求清单...", file=sys.stderr)
    requirements = _load_requirements()
    print(f"  加载到 {len(requirements)} 个表的需求信息", file=sys.stderr)

    # 6. 生成 MD（按 L1-L10 顺序输出）
    lines: list[str] = []
    lines.extend(_gen_header(today, all_tables))

    for layer_id in sorted(_LAYER_INFO.keys(), key=lambda x: int(x[1:])):
        tables_in_layer = layer_tables.get(layer_id, [])
        if tables_in_layer:
            tables_in_layer.sort(key=lambda x: x["table"])
            lines.extend(_gen_layer_section(layer_id, tables_in_layer, requirements))
            lines.append("---")
            lines.append("")

    lines.extend(_gen_footer())

    # 6. 写入文件
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    total_tables = len(all_tables)
    total_rows = sum(t["total_rows"] for t in all_tables)
    print(
        f"✅ 生成完成：{total_tables} 张表，"
        f"数据总行数 {_fmt_rows(total_rows)}，"
        f"输出到 {OUTPUT_PATH}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
