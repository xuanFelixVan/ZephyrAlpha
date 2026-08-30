# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.speed_tester
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.policy_registry; zephyr.data.ch_writer
# [CONSUMERS] zephyr.data.cli
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读测速不写业务表；结果写入 c0_meta.fetch_perf；小样本测试
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测速异常->返回error字段不抛出；Provider连接失败->api_status=blocked
# [TESTS] tests/zephyr/data/test_speed_tester.py
# [A_module] module_id=MOD-GOV-speed_tester | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



数据源测速器（MOD-L00-004 §8.5）。

对每个数据能力×每个可用数据源做小样本测速，记录 rows/sec、symbols/sec、错误率，
用于主用/备用源选型和数据源健康监控。

用法：
    from zephyr.data.speed_tester import run_speed_tests
    results = run_speed_tests()  # 全量测速
    results = run_speed_tests(source_filter="miniqmt")  # 只测 miniqmt
    results = run_speed_tests(cap_filter="daily_valuation")  # 只测 daily_valuation

CLI:
    integrator speed-test [--source <src>] [--capability <cap>]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cfg 参数
#   fields: 参数 cfg，类型注解 SpeedTestConfig
#   code: speed_tester.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: source_filter 参数
#   fields: 参数 source_filter，类型注解 str | None
#   code: speed_tester.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: cap_filter 参数
#   fields: 参数 cap_filter，类型注解 str | None
#   code: speed_tester.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: results 参数
#   fields: 参数 results，类型注解 list[dict]
#   code: speed_tester.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① speed_test_one
#   name_en: speed_test_one
#   intro: 测试一个 (source, capability) 组合的下载速度。
#   desc: 测试一个 (source, capability) 组合的下载速度。 Args: cfg: 测速配置（封装所有参数） Returns: dict: 测速结果；源码 L523-L568
#   inputs: cfg
#   outputs: dict
# - id: A2
#   name_zh: ② run_speed_tests
#   name_en: run_speed_tests
#   intro: 批量执行测速。
#   desc: 批量执行测速。 Args: source_filter: 只测某数据源（None=全部） cap_filter: 只测某能力（None=全部） Returns: list[dic…；源码 L572-L642
#   inputs: source_filter cap_filter
#   outputs: list[dict]
# - id: A3
#   name_zh: ③ save_to_clickhouse
#   name_en: save_to_clickhouse
#   intro: 把测速结果写入 c0_meta.fetch_perf 表。
#   desc: 把测速结果写入 c0_meta.fetch_perf 表。；源码 L646-L683
#   inputs: results
#   outputs: bool
# - id: A4
#   name_zh: ④ print_report
#   name_en: print_report
#   intro: 打印测速对比报告。
#   desc: 打印测速对比报告。；源码 L687-L734
#   inputs: results
#   outputs: 返回值
#   （注：A4 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict
#   name_en: dict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.cli
# - id: O2
#   name_zh: list[dict]
#   name_en: list[dict]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.cli
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
# A4 --> O1
"""

from __future__ import annotations

import datetime
import logging
import time
from dataclasses import dataclass
from typing import Optional

from zephyr.data.provider_base import FetchPayload, FetchResult
from zephyr.data.table_registry import get_registry
from zephyr.shared.foundation.constants import DEFAULT_RSSHUB_URL

log = logging.getLogger(__name__)

# ============== 样本配置 ==============
SAMPLE_SYMBOLS = ["000001.SZ", "000002.SZ", "600000.SH", "600519.SH", "000858.SZ"]
SAMPLE_START = datetime.date(2026, 6, 30)
SAMPLE_END = datetime.date(2026, 7, 9)

# ============== Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）==============
_TBL_ADJ_FACTOR = get_registry().table("market_adj_factor")
_TBL_BALANCE_SHEET = get_registry().table("fund_balance_sheet")
_TBL_BLOCK_TRADE = get_registry().table("market_block_trade")
_TBL_CASHFLOW_STATEMENT = get_registry().table("fund_cashflow_statement")
_TBL_DAILY_VALUATION = get_registry().table("market_daily_valuation")
_TBL_DRAGON_TIGER = get_registry().table("market_dragon_tiger")
_TBL_FETCH_PERF = get_registry().table("meta_fetch_perf")
_TBL_FINANCIAL_INDICATOR = get_registry().table("fund_financial_indicator")
_TBL_HK_CONNECT_FLOW = get_registry().table("market_hk_connect_flow")
_TBL_INCOME_STATEMENT = get_registry().table("fund_income_statement")
_TBL_INDEX_CONSTITUENT = get_registry().table("market_index_constituent")
_TBL_INDUSTRY_CLASS = get_registry().table("market_industry_class")
_TBL_KLINE_15MIN = get_registry().table("market_kline_15min")
_TBL_KLINE_1MIN = get_registry().table("market_kline_1min")
_TBL_KLINE_30MIN = get_registry().table("market_kline_30min")
_TBL_KLINE_5MIN = get_registry().table("market_kline_5min")
_TBL_KLINE_60MIN = get_registry().table("market_kline_60min")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
_TBL_KLINE_DAILY_HFQ = get_registry().table("market_kline_daily_hfq")
_TBL_KLINE_ETF_15MIN = get_registry().table("market_etf_kline_15min")
_TBL_KLINE_ETF_1MIN = get_registry().table("market_etf_kline_1min")
_TBL_KLINE_ETF_30MIN = get_registry().table("market_etf_kline_30min")
_TBL_KLINE_ETF_5MIN = get_registry().table("market_etf_kline_5min")
_TBL_KLINE_ETF_60MIN = get_registry().table("market_etf_kline_60min")
_TBL_KLINE_FUTURES = get_registry().table("market_futures_kline")
_TBL_KLINE_INDEX = get_registry().table("market_index_kline")
_TBL_KLINE_LOF_15MIN = get_registry().table("market_lof_kline_15min")
_TBL_KLINE_LOF_1MIN = get_registry().table("market_lof_kline_1min")
_TBL_KLINE_LOF_30MIN = get_registry().table("market_lof_kline_30min")
_TBL_KLINE_LOF_5MIN = get_registry().table("market_lof_kline_5min")
_TBL_KLINE_LOF_60MIN = get_registry().table("market_lof_kline_60min")
_TBL_KLINE_MONTHLY = get_registry().table("market_kline_monthly")
_TBL_KLINE_MONTHLY_HFQ = get_registry().table("market_kline_monthly_hfq")
_TBL_KLINE_SECTOR = get_registry().table("market_sector_kline")
_TBL_KLINE_US_DAILY = get_registry().table("market_us_kline_daily")
_TBL_KLINE_WEEKLY = get_registry().table("market_kline_weekly")
_TBL_KLINE_WEEKLY_HFQ = get_registry().table("market_kline_weekly_hfq")
_TBL_MACRO_DATA = get_registry().table("market_macro_data")
_TBL_MAIN_BUSINESS = get_registry().table("fund_main_business")
_TBL_MARGIN_TRADING = get_registry().table("market_margin_trading")
_TBL_MONEY_FLOW = get_registry().table("market_money_flow")
_TBL_NEWS_DATA = get_registry().table("fund_news_data")
_TBL_RESTRICTED_SHARES = get_registry().table("fund_restricted_shares")
_TBL_TRADE_CALENDAR = get_registry().table("market_trade_calendar")
_TBL_US_INDEX = get_registry().table("market_us_index")

# ============== 测速矩阵 ==============
# (source, capability, target_table, extra, symbols_override, start_override, end_override)
# start_override/end_override 为 None 时用 SAMPLE_START/SAMPLE_END
# 财务报表是季度数据，10天窗口内 0 行，需用 1 年范围
_YEAR_AGO = datetime.date(2025, 7, 10)
TEST_MATRIX: list[tuple[str, str, str, dict, list | None, datetime.date | None, datetime.date | None]] = [
    # kline_daily 两源对比
    ("miniqmt", "kline_daily", _TBL_KLINE_DAILY, {"capability": "kline_daily"}, None, None, None),
    (
        "baostock",
        "kline_daily",
        _TBL_KLINE_DAILY,
        {"capability": "kline_daily"},
        ["sh.600000", "sz.000001", "sz.000002"],
        None,
        None,
    ),
    # daily_valuation
    ("akshare", "daily_valuation", _TBL_DAILY_VALUATION, {"capability": "daily_valuation"}, None, None, None),
    # kline_index
    (
        "miniqmt",
        "kline_index",
        _TBL_KLINE_INDEX,
        {"capability": "kline_index"},
        ["000300.SH", "000905.SH", "000001.SH"],
        None,
        None,
    ),
    # index_constituent 两源对比
    ("miniqmt", "index_constituent", _TBL_INDEX_CONSTITUENT, {"capability": "index_constituent"}, None, None, None),
    ("baostock", "index_constituent", _TBL_INDEX_CONSTITUENT, {"capability": "index_constituent"}, None, None, None),
    # money_flow: tushare 主源
    ("tushare", "money_flow", _TBL_MONEY_FLOW, {"capability": "money_flow"}, None, None, None),
    # adj_factor: miniQMT 唯一（事件驱动，改用 1 年范围重测）
    (
        "miniqmt",
        "adj_factor",
        _TBL_ADJ_FACTOR,
        {"capability": "adj_factor"},
        ["000001.SZ", "600000.SH"],
        _YEAR_AGO,
        None,
    ),
    # AKShare 快源
    ("akshare", "margin_trading", _TBL_MARGIN_TRADING, {"capability": "margin_trading"}, None, None, None),
    ("akshare", "block_trade", _TBL_BLOCK_TRADE, {"capability": "block_trade"}, None, None, None),
    ("akshare", "dragon_tiger", _TBL_DRAGON_TIGER, {"capability": "dragon_tiger"}, None, None, None),
    ("akshare", "macro_data", _TBL_MACRO_DATA, {"capability": "macro_data"}, None, None, None),
    # 财务报表（季度数据，用 1 年范围）
    (
        "miniqmt",
        "balance_sheet",
        _TBL_BALANCE_SHEET,
        {"capability": "balance_sheet"},
        ["000001.SZ", "600000.SH"],
        _YEAR_AGO,
        None,
    ),
    (
        "miniqmt",
        "income_statement",
        _TBL_INCOME_STATEMENT,
        {"capability": "income_statement"},
        ["000001.SZ", "600000.SH"],
        _YEAR_AGO,
        None,
    ),
    (
        "miniqmt",
        "cashflow_statement",
        _TBL_CASHFLOW_STATEMENT,
        {"capability": "cashflow_statement"},
        ["000001.SZ", "600000.SH"],
        _YEAR_AGO,
        None,
    ),
    (
        "miniqmt",
        "financial_indicator",
        _TBL_FINANCIAL_INDICATOR,
        {"capability": "financial_indicator"},
        ["000001.SZ", "600000.SH"],
        _YEAR_AGO,
        None,
    ),
    (
        "miniqmt",
        "main_business",
        _TBL_MAIN_BUSINESS,
        {"capability": "main_business"},
        ["000001.SZ", "600000.SH"],
        _YEAR_AGO,
        None,
    ),
    # trade_calendar
    ("baostock", "trade_calendar", _TBL_TRADE_CALENDAR, {"capability": "trade_calendar"}, None, None, None),
    # 复权日K
    ("miniqmt", "kline_daily_hfq", _TBL_KLINE_DAILY_HFQ, {"capability": "kline_daily_hfq"}, None, None, None),
    # 周/月K（日K聚合）
    (
        "miniqmt",
        "kline_weekly",
        _TBL_KLINE_WEEKLY,
        {"capability": "kline_weekly"},
        ["000001.SZ", "600000.SH"],
        None,
        None,
    ),
    (
        "miniqmt",
        "kline_monthly",
        _TBL_KLINE_MONTHLY,
        {"capability": "kline_monthly"},
        ["000001.SZ", "600000.SH"],
        None,
        None,
    ),
    # 分钟K线（数据量大，用 1 只样本）
    ("miniqmt", "kline_1min", _TBL_KLINE_1MIN, {"capability": "kline_1min"}, ["000001.SZ"], None, None),
    ("miniqmt", "kline_5min", _TBL_KLINE_5MIN, {"capability": "kline_5min"}, ["000001.SZ"], None, None),
    ("miniqmt", "kline_15min", _TBL_KLINE_15MIN, {"capability": "kline_15min"}, ["000001.SZ"], None, None),
    ("miniqmt", "kline_30min", _TBL_KLINE_30MIN, {"capability": "kline_30min"}, ["000001.SZ"], None, None),
    ("miniqmt", "kline_60min", _TBL_KLINE_60MIN, {"capability": "kline_60min"}, ["000001.SZ"], None, None),
    # ===== 4 个未验证源（P2）=====
    # tickflow 美股数据
    (
        "tickflow",
        "kline_us_daily",
        _TBL_KLINE_US_DAILY,
        {"capability": "kline_us_daily"},
        ["SPY.US", "AAPL.US"],
        None,
        None,
    ),
    ("tickflow", "us_index", _TBL_US_INDEX, {"capability": "us_index"}, None, None, None),
    # tushare 新闻数据（统一写入 news_data，需 TUSHARE_TOKEN）
    ("tushare", "news_data", _TBL_NEWS_DATA, {"capability": "news_data"}, None, None, None),
    # rss 财经新闻（symbols_override 传 RSS feed URL，非股票代码）
    (
        "rss",
        "news_data",
        _TBL_NEWS_DATA,
        {"capability": "news_data"},
        [
            "https://36kr.com/feed",
            f"{DEFAULT_RSSHUB_URL}/wallstreetcn/news",
            f"{DEFAULT_RSSHUB_URL}/yicai/news",
            f"{DEFAULT_RSSHUB_URL}/caixin/latest",
        ],
        None,
        None,
    ),
    # akshare 研报/北向资金/期货
    (
        "akshare",
        "research_report",
        _TBL_NEWS_DATA,
        {"capability": "research_report"},
        ["000001.SZ", "600000.SH"],
        None,
        None,
    ),
    ("akshare", "hk_connect_flow", _TBL_HK_CONNECT_FLOW, {"capability": "hk_connect_flow"}, None, None, None),
    ("akshare", "kline_futures", _TBL_KLINE_FUTURES, {"capability": "kline_futures"}, None, None, None),
    # tdx 通达信板块数据
    ("tdx", "kline_sector", _TBL_KLINE_SECTOR, {"capability": "kline_sector"}, ["sh.000001"], None, None),
    # tushare 申万行业分类
    ("tushare", "industry_class", _TBL_INDUSTRY_CLASS, {"capability": "industry_class"}, None, None, None),
    # ===== 新增能力测速（2026-07-11）=====
    # ETF 分钟K线（数据量大，用 1 只样本）
    ("miniqmt", "kline_etf_1min", _TBL_KLINE_ETF_1MIN, {"capability": "kline_etf_1min"}, ["510050.SH"], None, None),
    ("miniqmt", "kline_etf_5min", _TBL_KLINE_ETF_5MIN, {"capability": "kline_etf_5min"}, ["510050.SH"], None, None),
    ("miniqmt", "kline_etf_15min", _TBL_KLINE_ETF_15MIN, {"capability": "kline_etf_15min"}, ["510050.SH"], None, None),
    ("miniqmt", "kline_etf_30min", _TBL_KLINE_ETF_30MIN, {"capability": "kline_etf_30min"}, ["510050.SH"], None, None),
    ("miniqmt", "kline_etf_60min", _TBL_KLINE_ETF_60MIN, {"capability": "kline_etf_60min"}, ["510050.SH"], None, None),
    # LOF 分钟K线（数据量大，用 1 只样本）
    ("miniqmt", "kline_lof_1min", _TBL_KLINE_LOF_1MIN, {"capability": "kline_lof_1min"}, ["161725.SZ"], None, None),
    ("miniqmt", "kline_lof_5min", _TBL_KLINE_LOF_5MIN, {"capability": "kline_lof_5min"}, ["161725.SZ"], None, None),
    ("miniqmt", "kline_lof_15min", _TBL_KLINE_LOF_15MIN, {"capability": "kline_lof_15min"}, ["161725.SZ"], None, None),
    ("miniqmt", "kline_lof_30min", _TBL_KLINE_LOF_30MIN, {"capability": "kline_lof_30min"}, ["161725.SZ"], None, None),
    ("miniqmt", "kline_lof_60min", _TBL_KLINE_LOF_60MIN, {"capability": "kline_lof_60min"}, ["161725.SZ"], None, None),
    # 后复权周/月K线（日K聚合）
    (
        "miniqmt",
        "kline_weekly_hfq",
        _TBL_KLINE_WEEKLY_HFQ,
        {"capability": "kline_weekly_hfq"},
        ["000001.SZ", "600000.SH"],
        None,
        None,
    ),
    (
        "miniqmt",
        "kline_monthly_hfq",
        _TBL_KLINE_MONTHLY_HFQ,
        {"capability": "kline_monthly_hfq"},
        ["000001.SZ", "600000.SH"],
        None,
        None,
    ),
    # 限售股明细
    (
        "akshare",
        "restricted_shares",
        _TBL_RESTRICTED_SHARES,
        {"capability": "restricted_shares"},
        ["000001.SZ", "600000.SH"],
        None,
        None,
    ),
]


# ============== Provider 工厂 ==============
def _make_provider(source: str):
    """按 source 名称实例化 Provider。"""
    if source == "miniqmt":
        from zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider

        return MiniQmtIngestProvider()
    elif source == "akshare":
        from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

        return AkshareIngestProvider()
    elif source == "baostock":
        from zephyr.data.implementations.baostock_provider import BaostockProvider

        return BaostockProvider()
    elif source == "tickflow":
        from zephyr.data.implementations.tickflow_provider import TickFlowProvider

        return TickFlowProvider()
    elif source == "tushare":
        from zephyr.data.implementations.tushare_provider import TushareProvider

        return TushareProvider()
    elif source == "rss":
        from zephyr.data.implementations.rss_provider import RSSProvider

        return RSSProvider()
    elif source == "tdx":
        from zephyr.data.implementations.tdx_provider import TDXProvider

        return TDXProvider()
    elif source == "cls":
        from zephyr.data.implementations.cls_provider import ClsProvider

        return ClsProvider()
    elif source == "eastmoney_news":
        from zephyr.data.implementations.eastmoney_news_provider import EastmoneyNewsProvider

        return EastmoneyNewsProvider()
    else:
        raise ValueError("不支持的数据源类型")


def _get_policy(source: str):
    """获取数据源策略。"""
    from zephyr.data.policy_registry import get_registry

    return get_registry().get_policy(source)


# ============== 单项测速 ==============


@dataclass
class SpeedTestConfig:
    """测速配置参数（封装 speed_test_one 的参数）。"""

    source: str
    capability: str
    target_table: str
    extra: dict
    symbols_override: list | None = None
    sample_symbols: list | None = None
    sample_start: datetime.date | None = None
    sample_end: datetime.date | None = None


def _init_result(cfg: SpeedTestConfig, symbols: list) -> dict:
    """初始化测速结果 dict。"""
    return {
        "source": cfg.source,
        "capability": cfg.capability,
        "target_table": cfg.target_table,
        "symbols_count": len(symbols),
        "rows_fetched": 0,
        "elapsed_sec": 0.0,
        "rows_per_sec": 0.0,
        "symbols_per_sec": 0.0,
        "error_count": 0,
        "error_rate": 0.0,
        "rate_limited": 0,
        "api_status": "ok",
        "known_issues": "",
        "notes": "",
        "error_detail": "",
    }


def _try_connect(source: str, result: dict, t0: float) -> object | None:
    """尝试实例化并连接 Provider。失败时更新 result 并返回 None。"""
    try:
        provider = _make_provider(source)
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        result["elapsed_sec"] = time.time() - t0
        result["api_status"] = "broken"
        result["error_detail"] = "Provider 实例化失败"
        result["known_issues"] = str(e)[:200]
        return None

    try:
        provider.connect()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        result["elapsed_sec"] = time.time() - t0
        result["api_status"] = "blocked"
        result["error_detail"] = "连接失败"
        result["known_issues"] = str(e)[:200]
        return None
    return provider


def _fetch_batches(provider, payload, policy, result: dict) -> tuple[int, int, str]:
    """拉取数据并统计，返回 (total_rows, error_count, first_error)。"""
    total_rows = 0
    error_count = 0
    first_error = ""
    try:
        for fr in provider.fetch(payload, policy):
            if fr.error:
                error_count += 1
                if not first_error:
                    first_error = fr.error[:200]
                if "配额" in fr.error or "-4318" in fr.error or "-4309" in fr.error:
                    result["api_status"] = "rate_limited"
                    result["rate_limited"] = 1
                    break
                continue
            total_rows += fr.rows_fetched
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        error_count += 1
        first_error = str(e)[:200]
        if "Timeout" in str(e) or "Connection" in str(e):
            result["api_status"] = "blocked"
        else:
            result["api_status"] = "broken"
    return total_rows, error_count, first_error


def speed_test_one(cfg: SpeedTestConfig) -> dict:
    """测试一个 (source, capability) 组合的下载速度。

    Args:
        cfg: 测速配置（封装所有参数）

    Returns:
        dict: 测速结果
    """
    symbols = cfg.symbols_override or (cfg.sample_symbols or SAMPLE_SYMBOLS)
    start = cfg.sample_start or SAMPLE_START
    end = cfg.sample_end or SAMPLE_END

    payload = FetchPayload(
        table=cfg.target_table,
        symbols=symbols,
        start=start,
        end=end,
        incremental=False,
        extra=cfg.extra,
    )
    policy = _get_policy(cfg.source)
    result = _init_result(cfg, symbols)

    t0 = time.time()
    provider = _try_connect(cfg.source, result, t0)
    if provider is None:
        return result

    total_rows, error_count, first_error = _fetch_batches(provider, payload, policy, result)
    elapsed = time.time() - t0
    try:
        provider.disconnect()
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass

    result["rows_fetched"] = total_rows
    result["elapsed_sec"] = round(elapsed, 2)
    result["error_count"] = error_count
    if elapsed > 0:
        result["rows_per_sec"] = round(total_rows / elapsed, 2)
        result["symbols_per_sec"] = round(len(symbols) / elapsed, 4)
    if first_error:
        result["error_detail"] = first_error
        result["known_issues"] = first_error[:200]
    return result


# ============== 批量测速 ==============
def run_speed_tests(
    source_filter: str | None = None,
    cap_filter: str | None = None,
) -> list[dict]:
    """批量执行测速。

    Args:
        source_filter: 只测某数据源（None=全部）
        cap_filter: 只测某能力（None=全部）

    Returns:
        list[dict]: 测速结果列表
    """
    tests = TEST_MATRIX
    if source_filter:
        tests = [t for t in tests if t[0] == source_filter]
    if cap_filter:
        tests = [t for t in tests if t[1] == cap_filter]

    print(f"共 {len(tests)} 项测速任务")
    results = []
    for entry in tests:
        # 兼容 5 元素（旧）和 7 元素（新）元组
        source, capability, table, extra, sym_override = entry[:5]
        start_override = entry[5] if len(entry) > 5 else None
        end_override = entry[6] if len(entry) > 6 else None
        print(f"\n{'=' * 60}")
        print(f"  测速: {source} / {capability}")
        print(f"{'=' * 60}")
        try:
            cfg = SpeedTestConfig(
                source=source,
                capability=capability,
                target_table=table,
                extra=extra,
                symbols_override=sym_override,
                sample_start=start_override,
                sample_end=end_override,
            )
            r = speed_test_one(cfg)
            results.append(r)
            print(
                f"  rows={r['rows_fetched']} time={r['elapsed_sec']}s "
                f"rows/s={r['rows_per_sec']} sym/s={r['symbols_per_sec']} "
                f"status={r['api_status']}"
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            print(f"  [FATAL] {e}")
            results.append(
                {
                    "source": source,
                    "capability": capability,
                    "target_table": table,
                    "symbols_count": 0,
                    "rows_fetched": 0,
                    "elapsed_sec": 0.0,
                    "rows_per_sec": 0.0,
                    "symbols_per_sec": 0.0,
                    "error_count": 1,
                    "error_rate": 1.0,
                    "rate_limited": 0,
                    "api_status": "broken",
                    "known_issues": str(e)[:200],
                    "notes": "",
                    "error_detail": str(e)[:200],
                }
            )

    print_report(results)
    save_to_clickhouse(results)
    return results


# ============== 结果存储 ==============
def save_to_clickhouse(results: list[dict]) -> bool:
    """把测速结果写入 c0_meta.fetch_perf 表。"""
    try:
        from zephyr.data import ch_writer
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.warning(f"无法导入 ch_writer，跳过 CH 写入: {e}")
        return False

    columns_str = (
        "(source, capability, target_table, test_date, rows_fetched, "
        "elapsed_sec, rows_per_sec, symbols_per_sec, error_count, error_rate, "
        "rate_limited, api_status, known_issues, notes)"
    )
    tsv_lines = []
    test_date = datetime.date.today().isoformat()
    for r in results:
        row = (
            r["source"],
            r["capability"],
            r["target_table"],
            test_date,
            str(r["rows_fetched"]),
            str(r["elapsed_sec"]),
            str(r["rows_per_sec"]),
            str(r["symbols_per_sec"]),
            str(r["error_count"]),
            str(r["error_rate"]),
            str(r["rate_limited"]),
            r["api_status"],
            r["known_issues"][:200],
            f"小样本测速({r['symbols_count']}只)",
        )
        tsv_lines.append("\t".join(ch_writer.tsv_escape(v) for v in row))

    tsv_bytes = ("\n".join(tsv_lines) + "\n").encode("utf-8")
    ok = ch_writer.write_tsv(_TBL_FETCH_PERF, columns_str, tsv_bytes)
    print(f"\n写入 {_TBL_FETCH_PERF}: {len(results)} 条 {'成功' if ok else '失败'}")
    return ok


# ============== 报告输出 ==============
def print_report(results: list[dict]) -> None:
    """打印测速对比报告。"""
    print("\n" + "=" * 110)
    print("  全量数据源测速报告")
    print("=" * 110)
    print(f"\n样本: {len(SAMPLE_SYMBOLS)} 只股票, 日期 {SAMPLE_START} ~ {SAMPLE_END}\n")

    header = f"{'source':<10} {'capability':<22} {'rows':>8} {'time(s)':>8} {'rows/s':>10} {'sym/s':>8} {'status':<14} {'issues'}"
    print(header)
    print("-" * 110)
    for r in results:
        issues = r["known_issues"][:40] if r["known_issues"] else ""
        print(
            f"{r['source']:<10} {r['capability']:<22} {r['rows_fetched']:>8} "
            f"{r['elapsed_sec']:>8.2f} {r['rows_per_sec']:>10.2f} "
            f"{r['symbols_per_sec']:>8.4f} {r['api_status']:<14} {issues}"
        )

    # 按能力分组推荐
    print("\n" + "=" * 110)
    print("  主用/备用源推荐")
    print("=" * 110)
    by_cap: dict[str, list[dict]] = {}
    for r in results:
        by_cap.setdefault(r["capability"], []).append(r)

    for cap, items in by_cap.items():
        valid = [i for i in items if i["api_status"] in ("ok", "rate_limited")]
        valid.sort(key=lambda x: x["rows_per_sec"], reverse=True)
        print(f"\n  {cap}:")
        if not valid:
            print("    无可用源（全部 broken/blocked）")
            for i in items:
                print(f"    - {i['source']}: {i['api_status']} ({i['known_issues'][:50]})")
            continue
        primary = valid[0]
        secondary = valid[1] if len(valid) > 1 else None
        print(
            f"    主用: {primary['source']:<10} rows/s={primary['rows_per_sec']:.2f} "
            f"sym/s={primary['symbols_per_sec']:.4f} status={primary['api_status']}"
        )
        if secondary:
            print(
                f"    备用: {secondary['source']:<10} rows/s={secondary['rows_per_sec']:.2f} "
                f"sym/s={secondary['symbols_per_sec']:.4f} status={secondary['api_status']}"
            )
        else:
            print("    备用: 无（单源）")
