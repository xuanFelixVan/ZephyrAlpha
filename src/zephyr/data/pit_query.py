# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.pit_query
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry（zephyr.data.calendar 仅 TYPE_CHECKING 类型注解）
# [CONSUMERS] zephyr.backtest.core.data_handler; zephyr.backtest.core.pit_manager
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT三公理对齐(as_of_join/embargo/survivorship); announce_date<=query_time; LIMIT 1 BY取查询时点可见最新版本; 仅查白名单财务表
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非白名单表->PITQueryError; CH查询失败->返回空字符串(同ch_reader); 表无period_col->跳过LIMIT 1 BY
# [TESTS] tests/data/test_pit_query.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


财报 Point-In-Time (PIT) 查询能力（#ARCH-CH-021 P0-5）。

背景：c3 财务报表使用 ReplacingMergeTree 覆盖式更新，存在前视偏差风险——
同一 report_period 可能有原始公告 + 修正公告多个版本。本模块按 announce_date
建立 point-in-time 查询能力，与 backtest 域 pit_manager.py 三公理对齐。

对齐关系（数据层 ↔ 回测层）：
  - as_of()         ↔ pit_manager.as_of_join()       版本对齐：取查询时点可见最新版本
  - embargo 选项    ↔ pit_manager.apply_embargo()     泄漏防护：announce_date 截止回退
  - survivorship_universe() ↔ pit_manager.check_survivorship_bias()  幸存者偏差：PIT 标的池

底层依赖：财务表 ORDER BY (symbol, report_period, announce_date) 保留全部版本
（ReplacingMergeTree 按 sort key 去重，announce_date 不同则不合并），故
LIMIT 1 BY symbol, report_period（ORDER BY announce_date DESC）可取查询时点
已公告的最新版本——这正是 AS OF JOIN 语义。

SSoT: docs/03_modules/_domain_data/data_source_integrator_blueprint.md
      docs/03_modules/_domain_backtest/blueprint.md §5.1 PIT铁律

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: query_time 参数
#   fields: 参数 query_time，类型注解 datetime | date | str
#   code: pit_query.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: pit_query.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: symbols 参数
#   fields: 参数 symbols，类型注解 Iterable[str]
#   code: pit_query.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: embargo_days 参数
#   fields: 参数 embargo_days，类型注解 int
#   code: pit_query.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① fmt_query_time
#   name_en: fmt_query_time
#   intro: 将查询时点格式化为 'YYYY-MM-DD' 字符串（toDate() 入参）。
#   desc: 将查询时点格式化为 'YYYY-MM-DD' 字符串（toDate() 入参）。Stage 4 公共化。；源码 L233-L235
#   inputs: query_time
#   outputs: str
# - id: A2
#   name_zh: ② escape_symbol
#   name_en: escape_symbol
#   intro: 转义标的代码中的单引号，防 SQL 注入。
#   desc: 转义标的代码中的单引号，防 SQL 注入。Stage 4 公共化。；源码 L245-L247
#   inputs: symbol
#   outputs: str
# - id: A3
#   name_zh: ③ format_symbols
#   name_en: format_symbols
#   intro: 将标的列表格式化为 SQL IN 子句内容。
#   desc: 将标的列表格式化为 SQL IN 子句内容。Stage 4 公共化。；源码 L255-L257
#   inputs: symbols
#   outputs: str
# - id: A4
#   name_zh: ④ embargo_clause
#   name_en: embargo_clause
#   intro: 构建 announce_date 截止回退子句。
#   desc: 构建 announce_date 截止回退子句。Stage 4 公共化。；源码 L268-L270
#   inputs: embargo_days
#   outputs: str
# - id: A5
#   name_zh: ⑤ limit_by_clause
#   name_en: limit_by_clause
#   intro: 构建 LIMIT 1 BY 子句。
#   desc: 构建 LIMIT 1 BY 子句。Stage 4 公共化。；源码 L280-L282
#   inputs: period_col
#   outputs: str
# - id: A6
#   name_zh: ⑥ resolve_table
#   name_en: resolve_table
#   intro: 解析逻辑表名为全限定表名。
#   desc: 解析逻辑表名为全限定表名。Stage 4 公共化。；源码 L296-L298
#   inputs: table
#   outputs: tuple[str, str | None]
# - id: A7
#   name_zh: ⑦ tsv_to_records
#   name_en: tsv_to_records
#   intro: 将 ch_reader 返回的 TSV 字符串解析为记录列表。
#   desc: 将 ch_reader 返回的 TSV 字符串解析为记录列表。 Args: tsv: TSV 格式字符串（每行一条记录，制表符分隔） columns: 列名列表；None 时用整…；源码 L325-L347
#   inputs: tsv columns
#   outputs: list[dict]
# - id: A8
#   name_zh: ⑧ tsv_to_dataframe
#   name_en: tsv_to_dataframe
#   intro: 将 TSV 字符串转为 pandas DataFrame（供 pit_manager 消费）。
#   desc: 将 TSV 字符串转为 pandas DataFrame（供 pit_manager 消费）。 pandas 为惰性导入——避免数据层硬依赖 pandas（仅 backtest…；源码 L350-L360
#   inputs: tsv columns
#   outputs: 返回值
# - id: A9
#   name_zh: ⑨ FinancialPITQuery
#   name_en: FinancialPITQuery
#   intro: 财报 Point-In-Time 查询器（ P0-5）。
#   desc: 财报 Point-In-Time 查询器（ P0-5）。 落实 PIT 三公理（对齐 backtest.core.pit_manager.PITManager）： 1. 版本对齐…；公共方法（定义序）: as_of,…
#   inputs: config calendar
#   outputs: 返回值
#   （注：A9 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.backtest.core.data_handler; zephyr.backtest.core.pit_manager
# - id: O2
#   name_zh: tuple[str, str | None]
#   name_en: tuple[str, str | None]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.backtest.core.data_handler; zephyr.backtest.core.pit_manager
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Iterable

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry

if TYPE_CHECKING:  # 仅类型注解（CAND-CRYPTO-001 日历注入，零运行时依赖增量）
    from zephyr.data.calendar.base import MarketCalendar

log = logging.getLogger(__name__)

__all__ = [
    "PITQueryConfig",
    "PITQueryError",
    "FinancialPITQuery",
    "FINANCIAL_PIT_TABLES",
    "tsv_to_records",
    "tsv_to_dataframe",
]

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_AS_OF = (
    "SELECT {columns} FROM {tbl}{final} "
    "WHERE {symbol_clause} AND announce_date <= toDate('{qt}'){embargo} "
    "ORDER BY announce_date DESC{limit_by}"
)
_SQL_LATEST = (
    "SELECT {columns} FROM {tbl}{final} "
    "WHERE symbol = '{sym}' AND announce_date <= toDate('{qt}'){embargo} "
    "ORDER BY {period_col} DESC, announce_date DESC LIMIT 1"
)
_SQL_SURVIVORSHIP = (
    "SELECT symbol FROM {tbl}{final} "
    "WHERE (valid_from IS NULL OR valid_from <= toDate('{qt}')) "
    "AND (valid_to IS NULL OR valid_to = toDate('1900-01-01') OR valid_to > toDate('{qt}'))"
)

# 财务报表 PIT 表注册表：logical_name -> (category_id, period_col)
# period_col=None 表示该表无报告期列（如 repurchase 每次 announce 即独立事件，不做版本去重）
_FINANCIAL_PIT_TABLES: dict[str, tuple[str, str | None]] = {
    "balance_sheet": ("fund_balance_sheet", "report_period"),
    "income_statement": ("fund_income_statement", "report_period"),
    "cashflow_statement": ("fund_cashflow_statement", "report_period"),
    "financial_indicator": ("fund_financial_indicator", "report_period"),
    "express_report": ("fund_express_report", "report_period"),
    "audit_opinion": ("fund_audit_opinion", "report_period"),
    "earnings_forecast": ("fund_earnings_forecast", "report_period"),
    "dividend": ("fund_dividend", "dividend_year"),
    "repurchase": ("fund_repurchase", None),
}

# 解析为全限定表名（真源：business_data_categories.yaml via table_registry）
FINANCIAL_PIT_TABLES: dict[str, str] = {
    name: get_registry().table(cat_id) for name, (cat_id, _period) in _FINANCIAL_PIT_TABLES.items()
}

# 幸存者偏差标的池表
_TBL_STOCK_LIST = get_registry().table("market_stock_list")


class PITQueryError(Exception):
    """PIT 查询违规或参数错误（如非白名单表）。"""

    error_code = "ZA-DATA-PIT-001"


@dataclass(frozen=True)
class PITQueryConfig:
    """PIT 查询配置（frozen，对齐 pit_manager.PITConfig）。

    Attributes:
        embargo_days: 公告截止回退交易日数（防修正公告泄漏，默认 0 即不回退）；
            对齐 pit_manager.PITConfig.embargo_days 语义——在数据层将 announce_date
            截止时点前推 embargo_days 个自然日，避免使用临近查询时点的新公告。
    """

    embargo_days: int = 0


def fmt_query_time(query_time: datetime | date | str) -> str:
    """将查询时点格式化为 'YYYY-MM-DD' 字符串（toDate() 入参）。Stage 4 公共化。"""
    return _fmt_query_time(query_time)


def _fmt_query_time(query_time: datetime | date | str) -> str:
    """将查询时点格式化为 'YYYY-MM-DD' 字符串（toDate() 入参）。"""
    if isinstance(query_time, str):
        return query_time[:10]
    return query_time.strftime("%Y-%m-%d")


def escape_symbol(symbol: str) -> str:
    """转义标的代码中的单引号，防 SQL 注入。Stage 4 公共化。"""
    return _escape_symbol(symbol)


def _escape_symbol(symbol: str) -> str:
    """转义标的代码中的单引号，防 SQL 注入。"""
    return str(symbol).replace("'", "\\'")


def format_symbols(symbols: Iterable[str]) -> str:
    """将标的列表格式化为 SQL IN 子句内容。Stage 4 公共化。"""
    return _format_symbols(symbols)


def _format_symbols(symbols: Iterable[str]) -> str:
    """将标的列表格式化为 SQL IN 子句内容（'a','b','c'）。"""
    escaped = [_escape_symbol(s) for s in symbols if s]
    if not escaped:
        raise PITQueryError("symbols 不能为空")
    return ",".join(f"'{s}'" for s in escaped)


def embargo_clause(embargo_days: int) -> str:
    """构建 announce_date 截止回退子句。Stage 4 公共化。"""
    return _embargo_clause(embargo_days)


def _embargo_clause(embargo_days: int) -> str:
    """构建 announce_date 截止回退子句。"""
    if embargo_days and embargo_days > 0:
        return f" - INTERVAL {embargo_days} DAY"
    return ""


def limit_by_clause(period_col: str | None) -> str:
    """构建 LIMIT 1 BY 子句。Stage 4 公共化。"""
    return _limit_by_clause(period_col)


def _limit_by_clause(period_col: str | None) -> str:
    """构建 LIMIT 1 BY 子句。

    有 period_col 时按 (symbol, period_col) 取最新版本；
    无 period_col 时（repurchase）不做版本去重，返回全部已公告行。
    """
    if period_col is None:
        return ""
    return f" LIMIT 1 BY symbol, {period_col}"


def resolve_table(table: str) -> tuple[str, str | None]:
    """解析逻辑表名为全限定表名。Stage 4 公共化。"""
    return _resolve_table(table)


def _resolve_table(table: str) -> tuple[str, str | None]:
    """解析逻辑表名为全限定表名，返回 (qualified_table, period_col)。

    Args:
        table: 逻辑表名（如 'balance_sheet'）或全限定表名

    Returns:
        (全限定表名, period_col)；period_col=None 表示无报告期列

    Raises:
        PITQueryError: 表不在 PIT 白名单中
    """
    if table in FINANCIAL_PIT_TABLES:
        return FINANCIAL_PIT_TABLES[table], _FINANCIAL_PIT_TABLES[table][1]
    # 允许传入全限定表名（反向查找）
    for logical, qualified in FINANCIAL_PIT_TABLES.items():
        if qualified == table:
            return qualified, _FINANCIAL_PIT_TABLES[logical][1]
    raise PITQueryError(
        f"表 '{table}' 不在财报 PIT 白名单中（允许: {sorted(FINANCIAL_PIT_TABLES)}) "
        "—— PIT 查询仅限已登记的财务报表表，防止越权查询"
    )


def tsv_to_records(tsv: str, columns: list[str] | None = None) -> list[dict]:
    """将 ch_reader 返回的 TSV 字符串解析为记录列表。

    Args:
        tsv: TSV 格式字符串（每行一条记录，制表符分隔）
        columns: 列名列表；None 时用整数索引

    Returns:
        记录列表（每条为 dict 或按列名映射的 dict）
    """
    if not tsv or not tsv.strip():
        return []
    records: list[dict] = []
    for line in tsv.strip().split("\n"):
        line = line.rstrip("\r")
        if not line:
            continue
        values = line.split("\t")
        if columns:
            records.append(dict(zip(columns, values, strict=False)))
        else:
            records.append({f"col_{i}": v for i, v in enumerate(values)})
    return records


def tsv_to_dataframe(tsv: str, columns: list[str] | None = None):
    """将 TSV 字符串转为 pandas DataFrame（供 pit_manager 消费）。

    pandas 为惰性导入——避免数据层硬依赖 pandas（仅 backtest 层需要）。
    """
    import pandas as pd  # 惰性导入

    records = tsv_to_records(tsv, columns)
    if not records:
        return pd.DataFrame(columns=columns or [])
    return pd.DataFrame(records)


class FinancialPITQuery:
    """财报 Point-In-Time 查询器（#ARCH-CH-021 P0-5）。

    落实 PIT 三公理（对齐 backtest.core.pit_manager.PITManager）：
      1. 版本对齐 (as_of)        — 取查询时点已公告的最新版本（LIMIT 1 BY）
      2. 泄漏防护 (embargo 选项) — announce_date 截止回退 embargo_days
      3. 幸存者偏差 (survivorship_universe) — PIT 标的池（含未来退市股）

    Usage:
        pit = FinancialPITQuery(PITQueryConfig(embargo_days=3))
        # AS OF JOIN: 平安银行 2026-06-01 可见的全部资产负债表报告期
        tsv = pit.as_of('balance_sheet', '000001.SZ', '2026-06-01')
        # 幸存者偏差标的池：2026-06-01 仍在市（含未来退市）的全部标的
        symbols = pit.survivorship_universe('2026-06-01')
    """

    def __init__(
        self,
        config: PITQueryConfig | None = None,
        calendar: MarketCalendar | None = None,
    ) -> None:
        self.config = config if config is not None else PITQueryConfig()
        # 市场日历注入（CAND-CRYPTO-001）：None=embargo 自然日口径（现状，逐字节不变）；
        # 注入后 embargo_days 按真交易日历回退（换算为自然日 INTERVAL，SQL 模板不动）
        self._calendar = calendar

    # ------------------------------------------------------------------
    # embargo 子句（公理2：泄漏防护）
    # ------------------------------------------------------------------
    def _embargo_sql(self, query_time: datetime | date | str) -> str:
        """构建 embargo 子句。calendar 未注入=自然日 INTERVAL（现状）；注入=真历回退换算。

        真历语义对齐 pit_manager._embargo_cutoff_by_calendar：锚定 <=query_time 最近
        交易日，前推 embargo_days 个交易日的日期为 cutoff；换算 k=(qt-cutoff).days
        走同一 `_ - INTERVAL k DAY` 模板，SQL 形状不变。日历窗口=embargo_days*3+15
        自然日（覆盖最长春节假期）；窗口内交易日不足时回窗口首日-1天（同 pit_manager
        日历不足口径）；窗口全空（不可能，防御）回退自然日口径。
        """
        if self._calendar is None or self.config.embargo_days <= 0:
            return _embargo_clause(self.config.embargo_days)
        qt_date = date.fromisoformat(_fmt_query_time(query_time))
        window = self.config.embargo_days * 3 + 15
        days = self._calendar.trading_days_in_range(qt_date - timedelta(days=window), qt_date)
        if not days:
            return _embargo_clause(self.config.embargo_days)
        idx = len(days) - 1 - self.config.embargo_days
        cutoff = days[idx] if idx >= 0 else days[0] - timedelta(days=1)
        return _embargo_clause((qt_date - cutoff).days)

    # ------------------------------------------------------------------
    # AS OF JOIN（公理1：版本对齐）
    # ------------------------------------------------------------------
    def as_of(
        self,
        table: str,
        symbol: str,
        query_time: datetime | date | str,
        columns: str = "*",
    ) -> str:
        """AS OF JOIN：返回单标的在查询时点可见的全部报告期最新版本。

        落实公理1（版本对齐）：对每个 report_period，取 announce_date <= query_time
        的最新版本，禁用后续修正公告（消除前视偏差）。

        Args:
            table: 逻辑表名（如 'balance_sheet'）
            symbol: 标的代码（如 '000001.SZ'）
            query_time: 查询时点（含），仅返回此时点已公告的数据
            columns: 查询列，默认 '*'

        Returns:
            TSV 格式字符串（每行一条记录，按 announce_date 降序）
        """
        sql = self._build_as_of_sql(table, [symbol], query_time, columns, single=True)
        return ch_reader.query(sql)

    def as_of_panel(
        self,
        table: str,
        symbols: Iterable[str],
        query_time: datetime | date | str,
        columns: str = "*",
    ) -> str:
        """AS OF JOIN 面板版：多标的同时查询时点可见的最新版本。

        Args:
            table: 逻辑表名
            symbols: 标的代码列表
            query_time: 查询时点（含）
            columns: 查询列，默认 '*'

        Returns:
            TSV 格式字符串
        """
        sym_list = list(symbols)
        sql = self._build_as_of_sql(table, sym_list, query_time, columns, single=False)
        return ch_reader.query(sql)

    def as_of_latest(
        self,
        table: str,
        symbol: str,
        query_time: datetime | date | str,
        columns: str = "*",
    ) -> str:
        """AS OF JOIN 最新一期：返回单标的在查询时点可见的最新报告期数据。

        适用于"只需最新财报快照"的场景（如因子计算取最新报告）。
        使用表的 period_col（report_period / dividend_year）排序取最新一期。

        Args:
            table: 逻辑表名（须含报告期列）
            symbol: 标的代码
            query_time: 查询时点（含）
            columns: 查询列，默认 '*'

        Returns:
            TSV 格式字符串（单行）

        Raises:
            PITQueryError: 表无报告期列（如 repurchase）
        """
        qualified, period_col = _resolve_table(table)
        if period_col is None:
            raise PITQueryError(f"表 '{table}' 无报告期列，as_of_latest 不适用")
        qt = _fmt_query_time(query_time)
        sym = _escape_symbol(symbol)
        embargo = self._embargo_sql(query_time)
        sql = _SQL_LATEST.format(
            columns=columns,
            tbl=qualified,
            final="",
            sym=sym,
            qt=qt,
            embargo=embargo,
            period_col=period_col,
        )
        return ch_reader.query(sql)

    # ------------------------------------------------------------------
    # 幸存者偏差标的池（公理3）
    # ------------------------------------------------------------------
    def survivorship_universe(self, query_time: datetime | date | str) -> list[str]:
        """PIT 标的池：返回查询时点仍在市（含未来退市）的全部标的。

        落实公理3（幸存者偏差）：通过 stock_list 的 SCD-2 列（valid_from/valid_to）
        时点过滤，包含查询时点之后退市但当时仍在市的标的，消除"用当前在市股
        回测历史"的幸存者偏差。

        判定逻辑：
          - valid_from <= query_time（已上市）
          - valid_to IS NULL 或 valid_to > query_time（尚未退市）
          （valid_to = '1900-01-01' 视为无退市日期，等同 NULL）

        Args:
            query_time: 查询时点（含）

        Returns:
            标的代码列表
        """
        qt = _fmt_query_time(query_time)
        sql = _SQL_SURVIVORSHIP.format(tbl=_TBL_STOCK_LIST, final="", qt=qt)
        tsv = ch_reader.query(sql)
        if not tsv or not tsv.strip():
            return []
        return [line.strip() for line in tsv.strip().split("\n") if line.strip()]

    # ------------------------------------------------------------------
    # SQL 构建（纯函数，便于单测）
    # ------------------------------------------------------------------
    def build_as_of_sql(
        self,
        table: str,
        symbols: list[str],
        query_time: datetime | date | str,
        columns: str,
        single: bool,
    ) -> str:
        """构建 AS OF JOIN SQL。Stage 4 公共化。"""
        return self._build_as_of_sql(table, symbols, query_time, columns, single)

    def _build_as_of_sql(
        self,
        table: str,
        symbols: list[str],
        query_time: datetime | date | str,
        columns: str,
        single: bool,
    ) -> str:
        """构建 AS OF JOIN SQL（公理1+公理2：版本对齐+embargo）。

        single=True 用 symbol = '...'，single=False 用 symbol IN (...)。
        ch_reader.query() 自动注入 FINAL（ReplacingMergeTree 去重）。
        """
        qualified, period_col = _resolve_table(table)
        qt = _fmt_query_time(query_time)
        embargo = self._embargo_sql(query_time)
        if single:
            symbol_clause = f"symbol = '{_escape_symbol(symbols[0])}'"
        else:
            symbol_clause = f"symbol IN ({_format_symbols(symbols)})"
        limit_by = _limit_by_clause(period_col)
        return _SQL_AS_OF.format(
            columns=columns,
            tbl=qualified,
            final="",
            symbol_clause=symbol_clause,
            qt=qt,
            embargo=embargo,
            limit_by=limit_by,
        )
