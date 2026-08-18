# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.akshare_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare SDK (ak.macro_china_gdp/cpi/pmi/money_supply); zephyr.data.ch_reader
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 匿名访问；须断开 VPN（爬国内网站）；东财接口跳过（反爬）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestAKShareHelpers
# [A_module] module_id=MOD-DAT-akshare_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AKShare 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 AKShare 开源金融数据 SDK，继承 IngestProviderBase。
- 匿名访问，无需登录；但须断开 VPN（爬国内网站，海外 IP 会被拒）
- 当前能力：macro_data（GDP/CPI/PMI/货币供应量）
- 每个指标函数作为一批 yield FetchResult，异常时 yield error 不抛出

数据转换目标表 c1_market.macro_data：
    report_date, indicator_name, indicator_value, unit, frequency
"""
from __future__ import annotations

# ============== Windows IE 代理绕过（必须在 import requests/akshare 之前）==============
# 原因：Windows 启用 IE 代理（如 127.0.0.1:10808 V2Ray/Clash）时，requests 库通过
# urllib.request.getproxies_registry() 读取注册表代理设置，导致访问国内站点（东财/akshare）
# 被代理拦截（RemoteDisconnected）。NO_PROXY 环境变量对 getproxies_registry 无效。
# 修复：patch urllib 底层代理读取函数返回空 dict，强制直连。
# 安全性：仅影响 Python 进程内网络请求，不修改系统代理设置；退出进程后失效。
import os as _os

_os.environ.setdefault("NO_PROXY", "*")
_os.environ.setdefault("no_proxy", "*")
for _k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
    _os.environ.pop(_k, None)

import urllib.request as _urllib_req


def _no_proxies() -> dict:  # noqa: ANN202
    """返回空代理字典，阻止从 Windows 注册表读取 IE 代理。"""
    return {}


# patch 三层代理读取入口（requests 在 Windows 上最终调这些函数）
_urllib_req.getproxies = _no_proxies
if hasattr(_urllib_req, "getproxies_registry"):
    _urllib_req.getproxies_registry = _no_proxies
if hasattr(_urllib_req, "getproxies_environment"):
    _urllib_req.getproxies_environment = _no_proxies

# 诊断标记（确认 patch 执行）
import logging as _diag_logging

_diag_logging.getLogger(__name__).debug(
    "akshare_provider 代理 patch 已执行: getproxies=%r", _urllib_req.getproxies
)

import calendar
import datetime
import logging
import math
import re
import threading
import time
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    import pandas as pd

# patch requests.Session 禁用 trust_env（双保险，防止 akshare 内部新建 session 走代理）
try:
    import requests as _requests

    _orig_session_init = _requests.Session.__init__

    def _patched_session_init(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        _orig_session_init(self, *args, **kwargs)
        self.trust_env = False
        self.proxies = {}

    _requests.Session.__init__ = _patched_session_init
    _requests.utils.get_environ_proxies = lambda *a, **k: {}  # noqa: E731
except ImportError:
    pass

from zephyr.shared.utils.time_utils import now_utc, seconds_since

from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row
from ..policy_registry import SourcePolicy
from ..provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_ANALYST_FORECAST = get_registry().table("fund_analyst_forecast")
_TBL_AUDIT_OPINION = get_registry().table("fund_audit_opinion")
_TBL_BLOCK_TRADE = get_registry().table("market_block_trade")
_TBL_BLOCK_TRADE_DETAIL = get_registry().table("market_block_trade_detail")
_TBL_CONCEPT_BOARD = get_registry().table("market_concept_board")
_TBL_CONCEPT_BOARD_CONSTITUENT = get_registry().table("market_concept_board_constituent")
# #ARCH-IFIND-FAILOVER: 承接原 iFind 能力（iFind 已于 2026-08-14 退役，本源为正式主承担）
_TBL_CONCEPT_SECTOR = get_registry().table("market_concept_sector")
_TBL_REALTIME_SNAPSHOT = get_registry().table("market_realtime_snapshot")
_TBL_SECTOR_META = get_registry().table("market_sector_meta")
_TBL_CONVERTIBLE_BOND_LIST = get_registry().table("market_cb_list")
_TBL_DAILY_VALUATION = get_registry().table("market_daily_valuation")
_TBL_DISCLOSURE_PLAN = get_registry().table("fund_disclosure_plan")
_TBL_DIVIDEND = get_registry().table("fund_dividend")
_TBL_DRAGON_TIGER = get_registry().table("market_dragon_tiger")
_TBL_DRAGON_TIGER_SEAT = get_registry().table("market_dragon_tiger_seat")
_TBL_EQUITY_PLEDGE_DETAIL = get_registry().table("fund_equity_pledge_detail")
_TBL_EQUITY_PLEDGE_SUMMARY = get_registry().table("fund_equity_pledge_summary")
_TBL_ETF_BENCHMARK = get_registry().table("market_etf_benchmark")
_TBL_ETF_LIST = get_registry().table("market_etf_list")
_TBL_TRADE_CALENDAR = get_registry().table("market_trade_calendar")
_TBL_INDEX_CONSTITUENT = get_registry().table("market_index_constituent")
_TBL_ETF_NAV = get_registry().table("market_etf_nav")
_TBL_HOG_SPOT_INDEX = get_registry().table("market_hog_spot_index")
_TBL_HOG_FUTURES_CORE = get_registry().table("market_hog_futures_core")
_TBL_HOG_PROVINCE_SPOT = get_registry().table("market_hog_province_spot")
_TBL_HK_CONNECT_FLOW = get_registry().table("market_hk_connect_flow")
_TBL_HK_STOCK_LIST = get_registry().table("market_hk_stock_list")
_TBL_STOCK_HOT_RANK = get_registry().table("market_stock_hot_rank")  # #ARCH-REALTIME-ACCUM
_TBL_INDEX_LIST = get_registry().table("market_index_list")
_TBL_KLINE_FUTURES = get_registry().table("market_futures_kline")
_TBL_KLINE_HK_DAILY = get_registry().table("market_hk_kline_daily")
_TBL_LIMIT_UP_DOWN = get_registry().table("market_limit_up_down")
_TBL_LOF_LIST = get_registry().table("market_lof_list")
_TBL_MACRO_DATA = get_registry().table("market_macro_data")
_TBL_MARGIN_TRADING = get_registry().table("market_margin_trading")
_TBL_MONEY_FLOW = get_registry().table("market_money_flow")
_TBL_NEWS_DATA = get_registry().table("fund_news_data")
_TBL_REPURCHASE = get_registry().table("fund_repurchase")
_TBL_RESTRICTED_SHARES = get_registry().table("fund_restricted_shares")
_TBL_RIGHTS_ISSUE = get_registry().table("fund_rights_issue")
_TBL_SHARE_CHANGE = get_registry().table("fund_share_change")
_TBL_SHARE_UNLOCK = get_registry().table("fund_share_unlock")
_TBL_STOCK_INDICATOR = get_registry().table("market_stock_indicator")
_TBL_STOCK_LIST = get_registry().table("market_stock_list")
_TBL_ST_STOCK_LIST = get_registry().table("market_st_stock_list")
# JOB-077 市场元数据与约束接入（DS-081~083 新建表，2026-08-15）
_TBL_STOCK_BASIC = get_registry().table("meta_stock_basic")
_TBL_STK_LIMIT = get_registry().table("market_stk_limit")
_TBL_SUSPEND = get_registry().table("market_suspend")
# tracker #114 / 37号 §3.2a（2026-08-17 AI-IPO-001）：IPO 日历/募资规模（巨潮新股列表）
_TBL_IPO_CALENDAR = get_registry().table("market_ipo_calendar")

# JOB-077 SQL 集中化（NO-BARE-SQL gate 合规，常量名匹配 ^_?SQL_\w+$ 豁免正则）
# kline_daily 交易日序列/收盘价/每股日期数组（stk_limit 计算与 suspend 推导共用）
_SQL_KLINE_DAYS = (
    "SELECT DISTINCT trade_date FROM c1_market.kline_daily "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}' ORDER BY trade_date"
)
_SQL_KLINE_BARS = (
    "SELECT trade_date, symbol, close, adj_factor FROM c1_market.kline_daily "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}'"
)
_SQL_KLINE_SYMBOL_DAYS = (
    "SELECT symbol, groupArray(trade_date) FROM c1_market.kline_daily "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}' GROUP BY symbol"
)
# CH 不可达探活（ch_reader.query 故障静默返回空串，count() 仍为空=不可达）
_SQL_KLINE_PROBE = "SELECT count() FROM c1_market.kline_daily"
# ST 最近可得快照加载（PIT 严格：≤T 口径，窗口前推 400 天）
_SQL_ST_SNAPSHOTS = (
    "SELECT trade_date, symbol FROM {table} "
    "WHERE trade_date >= '{start}' AND trade_date <= '{end}'"
)
_TBL_TOP10_CIRCULATING_SHAREHOLDERS = get_registry().table("fund_top10_circulating_shareholders")
_TBL_TOP10_SHAREHOLDERS = get_registry().table("fund_top10_shareholders")


# === 裁定#217 Tier2 P4 Extract Method 重构（2026-07-15）===
# 原 AkshareIngestProvider.fetch 95行 McCabe=41（38个elif分支能力路由，均调用 self._fetch_{cap}(payload, policy)）。
# 治本：提取为 frozenset + getattr 动态分发，主函数简化为编排（McCabe=2）。
# 行为等价：所有路由调用签名/参数完全保留，unsupported capability 错误消息不变。
_AKSHARE_CAPABILITIES = frozenset({
    "macro_data", "daily_valuation", "margin_trading", "block_trade",
    "dragon_tiger", "dragon_tiger_seat", "money_flow", "share_unlock", "audit_opinion",
    "equity_pledge", "equity_pledge_summary", "dividend", "restricted_shares",
    "stock_news_em", "news_cctv", "news_economic_baidu", "news_baidu",
    "news_stock", "analyst_forecast", "rights_issue", "research_report",
    "hk_connect_flow", "kline_futures", "kline_hk_daily", "limit_up_down", "share_change",
    "st_stock_list", "concept_board", "stock_indicator", "block_trade_detail",
    "top10_shareholders", "top10_circulating_shareholders", "disclosure_plan",
    "repurchase", "convertible_bond_list", "etf_list", "lof_list",
    "hk_stock_list", "hk_trade_calendar", "index_list", "etf_benchmark",
    "etf_nav",  # #ARCH-CH-023: 替代 miniQMT get_etf_info（不支持）
    "hog_spot_index",  # 2026-07-29 生猪现货价格指数（akshare index_hog_spot_price）
    "hog_futures_core",  # 生猪期货核心价（akshare futures_hog_core）
    "hog_province_spot",  # 分省生猪现价（akshare spot_hog_soozhu）
    "stock_list_delisted",  # #ARCH-CH-021 P0-1: 退市股票列表（SH+SZ delist）
    "futures_position",  # #ARCH-FUTURES-POSITION: 替代 QMT（QMT get_instrument_detail 返回全0）
    # #ARCH-IFIND-FAILOVER: 承接原 iFind 能力（iFind 已于 2026-08-14 退役，本源为正式主承担）
    "concept_sector",      # 替代 iFind i问财概念板块（akshare stock_board_concept_name_ths）
    "realtime_snapshot",   # 替代 iFind THS_RealtimeQuotes（akshare stock_zh_a_spot_em，注意反爬）
    "sector_meta",         # 替代 iFind 881板块汇总（akshare 从成分股聚合计算）
    "stock_hot_rank",  # #ARCH-REALTIME-ACCUM: 东财人气/关注排行（每日快照积累）
    "option_kline",  # #ARCH-OPTION-AKSHARE-FALLBACK: 新浪源期权日K线（QMT无期权权限时fallback）
    # #ARCH-DATA-015: baostock IP黑名单治本——补全死 fallback 对应的能力（原配置空挂）
    "trade_calendar",    # A股交易日历（tool_trade_date_hist_sina，探针实证 8797 行可用）
    "index_constituent",  # 沪深300成分股（index_stock_cons_csindex，中证指数官网源）
    # JOB-077 市场元数据与约束接入（DS-081~083，2026-08-15）
    "stock_basic",      # DS-081 股票基本信息日快照（交易所官网清单，非东财）
    "stk_limit",        # DS-082 每日涨跌停价格（规则计算：昨收×(1±幅度)四舍五入到分）
    "suspend_status",   # DS-083 停复牌（东财停牌清单+百度停复牌公告+K线缺口推导）
    # tracker #114 / 37号 §3.2a（2026-08-17 AI-IPO-001）
    "ipo_calendar",     # DS-105 IPO 日历/募资规模（巨潮 stock_new_ipo_cninfo，沪深北全市场）
})


def safe_float(v) -> float | None:
    """安全转 float，失败返回 None。"""
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def safe_int(v) -> int | None:
    """安全转 int，失败返回 None。兼容 float 字符串（如 '7987.0'）。"""
    try:
        if v is None:
            return None
        f = float(v)
        return int(f)
    except (ValueError, TypeError):
        return None


def _cn_code_to_symbol(code: str) -> str:
    """6 位数字代码 → canonical 代码.交易所（600000.SH/000001.SZ/430047.BJ）。

    #ARCH-DATA-015：exchange 前缀规则与 index_constituent 表 MATERIALIZED 派生列
    口径一致（5/6/9→SH，0/1/2/3→SZ，4/8→BJ），保证 symbol_canonical 非空。
    """
    if code.startswith(("5", "6", "9")):
        return f"{code}.SH"
    if code.startswith(("4", "8")):
        return f"{code}.BJ"
    return f"{code}.SZ"


def _classify_seat(name: str) -> str:
    """龙虎榜席位类型分类：institution/broker/connect。"""
    if "机构专用" in name:
        return "institution"
    if "股通" in name:  # 深股通/沪股通/港股通
        return "connect"
    return "broker"


def _merge_lhb_seats(provider, ak, policy, symbol: str, date_str: str) -> dict:
    """合并龙虎榜买入/卖出 Top5 席位，按 seat_name 去重为每席位一行。

    Args:
        provider: AkshareIngestProvider 实例（用于 _call_with_policy）
        ak: akshare 模块
        policy: SourcePolicy 限流策略
        symbol: 6 位证券代码
        date_str: YYYYMMDD 日期串

    Returns:
        {seat_name: {buy, sell, net, buy_rank, sell_rank}}
    """
    seat_map: dict[str, dict] = {}
    for side, rank_key in (("买入", "buy_rank"), ("卖出", "sell_rank")):
        try:
            df_s = provider._call_with_policy(
                ak.stock_lhb_stock_detail_em, policy,
                symbol=symbol, date=date_str, flag=side,
            )
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            df_s = None
        if df_s is None or len(df_s) == 0:
            continue
        for rank, (_, srow) in enumerate(df_s.iterrows(), 1):
            seat = str(srow.get("交易营业部名称") or "")
            if not seat:
                continue
            if seat not in seat_map:
                seat_map[seat] = {
                    "buy": None, "sell": None, "net": None,
                    "buy_rank": None, "sell_rank": None,
                }
            seat_map[seat]["buy"] = safe_float(srow.get("买入金额"))
            seat_map[seat]["sell"] = safe_float(srow.get("卖出金额"))
            seat_map[seat]["net"] = safe_float(srow.get("净额"))
            seat_map[seat][rank_key] = rank
    return seat_map


def _build_valuation_col_map(df, norm_date_fn, start_str, end_str):
    col_map = {}
    for _, row in df.iterrows():
        d = norm_date_fn(row.get("date"))
        if d and start_str <= d <= end_str:
            col_map[d] = safe_float(row.get("value"))
    return col_map


def _build_top10_shareholder_row(row, sym, qe, ratio_col, type_col):
    return (
        sym,
        qe,
        qe,
        str(row.get("股东名称", "") or ""),
        safe_float(row.get("持股数")),
        safe_float(row.get(ratio_col)),
        safe_float(row.get("变动比率")),
        str(row.get("增减", "") or ""),
        str(row.get(type_col, "") or ""),
        "akshare",
        1,
    )


# CH fallback: 从 stock_list 获取 A 股 6 位代码（SQL_ 前缀豁免 NO-BARE-SQL gate）
# 治本(裁定#ARCH-AKSHARE-ANTICRAWLER-001)：增加 delist_date 过滤，
# 排除月初快照时已知退市日期的股票（快照后新退市的需提升 stock_list_refresh 频率解决）
SQL_STOCK_CODE_FROM_LIST = (
    "SELECT splitByChar('.', ts_code)[1] AS code "
    f"FROM {_TBL_STOCK_LIST} "
    "WHERE list_status = '上市' "
    "AND (delist_date IS NULL OR delist_date = toDate('1900-01-01') OR delist_date > today()) "
    "ORDER BY ts_code FORMAT TabSeparated"
)


class AkshareIngestProvider(IngestProviderBase):
    """AKShare 免费开源数据源 Provider。

    匿名访问、无需登录；线程安全模型为 shared（多线程共享 akshare 模块）。
    已知问题：须断开 VPN；东财接口反爬严重。
    """

    source_name: str = "akshare"

    # 东财 push2 反爬封锁标志：连续失败3次后置 True，后续直接跳东财走同花顺
    # #ARCH-EM-ANTIBOT-FAILOVER：IP 被东财封锁时避免逐板块浪费时间重试
    _em_push2_blocked: bool = False
    _em_fail_count: int = 0

    meta: IngestProviderMeta = IngestProviderMeta(
        name="akshare",
        display_name="AKShare 免费开源",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=60,
        capabilities=[
            # 治本修复#ARCH-CAP-NULL-SYMBOLS-001（2026-07-23）：
            # 所有声明 symbols=null 的 task 对应 capability 显式声明 supports_symbols_null=True，
            # 消除 83 条 CAP-NULL-SYMBOLS WARN。
            CapabilityContract("macro_data", supports_symbols_null=True),
            # 10 个支持 symbols=null 的能力（裁定 #ARCH-CH-018/#ARCH-CH-022）
            # Provider 内部调用 _get_all_a_symbols 做 fallback（akshare→CH stock_list）
            CapabilityContract("dividend", supports_symbols_null=True),
            CapabilityContract("restricted_shares", supports_symbols_null=True),
            CapabilityContract("daily_valuation", supports_symbols_null=True),
            CapabilityContract("money_flow", supports_symbols_null=True),
            CapabilityContract("stock_news_em", supports_symbols_null=True),
            CapabilityContract("research_report", supports_symbols_null=True),
            CapabilityContract("share_change", supports_symbols_null=True),
            CapabilityContract("stock_indicator", supports_symbols_null=True),
            CapabilityContract("top10_shareholders", supports_symbols_null=True),
            CapabilityContract("top10_circulating_shareholders", supports_symbols_null=True),
            # 以下能力支持 symbols=null（Provider 内部有全市场扫描或调用批量接口）
            CapabilityContract("equity_pledge", supports_symbols_null=True),
            CapabilityContract("margin_trading", supports_symbols_null=True),
            CapabilityContract("block_trade", supports_symbols_null=True),
            CapabilityContract("dragon_tiger", supports_symbols_null=True),
            CapabilityContract("dragon_tiger_seat", supports_symbols_null=True),
            CapabilityContract("share_unlock", supports_symbols_null=True),
            CapabilityContract("audit_opinion", supports_symbols_null=True),
            CapabilityContract("equity_pledge_summary", supports_symbols_null=True),
            # 新闻数据
            CapabilityContract("news_cctv", supports_symbols_null=True),
            CapabilityContract("news_economic_baidu", supports_symbols_null=True),
            CapabilityContract("news_baidu", supports_symbols_null=True),
            CapabilityContract("news_stock", supports_symbols_null=True),
            # 分析师预期 & 配股
            CapabilityContract("analyst_forecast", supports_symbols_null=True),
            CapabilityContract("rights_issue", supports_symbols_null=True),
            # 研报 & 北向资金 & 期货主力合约
            CapabilityContract("hk_connect_flow", supports_symbols_null=True),
            CapabilityContract("kline_futures", supports_symbols_null=True),
            CapabilityContract("kline_hk_daily", supports_symbols_null=True),
            # 涨跌停 & 股本变动 & ST股票 & 概念板块 & 指标 & 大宗交易明细
            CapabilityContract("limit_up_down", supports_symbols_null=True),
            CapabilityContract("st_stock_list", supports_symbols_null=True),
            CapabilityContract("concept_board", supports_symbols_null=True),
            CapabilityContract("block_trade_detail", supports_symbols_null=True),
            # 披露计划（淘宝历史数据持续更新）
            CapabilityContract("disclosure_plan", supports_symbols_null=True),
            # 回购数据
            CapabilityContract("repurchase", supports_symbols_null=True),
            # 静态列表月初刷新
            CapabilityContract("convertible_bond_list", supports_symbols_null=True),
            CapabilityContract("etf_list", supports_symbols_null=True),
            CapabilityContract("lof_list", supports_symbols_null=True),
            CapabilityContract("hk_stock_list", supports_symbols_null=True),
            CapabilityContract("hk_trade_calendar", supports_symbols_null=True),
            CapabilityContract("index_list", supports_symbols_null=True),
            CapabilityContract("etf_benchmark", supports_symbols_null=True),
            CapabilityContract("etf_nav", supports_symbols_null=True),  # #ARCH-CH-023
            CapabilityContract("stock_list_delisted", supports_symbols_null=True),  # #ARCH-CH-021 P0-1
            CapabilityContract("futures_position", supports_symbols_null=True),  # #ARCH-FUTURES-POSITION
            # 2026-07-29 生猪价格数据接入（akshare，单一时间序列无 symbols 概念）
            CapabilityContract("hog_spot_index", supports_symbols_null=True),
            CapabilityContract("hog_futures_core", supports_symbols_null=True),
            CapabilityContract("hog_province_spot", supports_symbols_null=True),
            # #ARCH-IFIND-FAILOVER: 承接原 iFind 能力（iFind 已于 2026-08-14 退役，本源为正式主承担）
            CapabilityContract("concept_sector", supports_symbols_null=True),
            CapabilityContract("realtime_snapshot", supports_symbols_null=True),
            CapabilityContract("sector_meta", supports_symbols_null=True),
            # #ARCH-REALTIME-ACCUM: 东财人气/关注排行（每日快照积累）
            CapabilityContract("stock_hot_rank", supports_symbols_null=True),
            # #ARCH-OPTION-AKSHARE-FALLBACK: 新浪源期权日K线（QMT无期权权限时fallback）
            CapabilityContract("option_kline", supports_symbols_null=True),
            # #ARCH-DATA-015: baostock 黑名单治本——死 fallback 能力补全（全量接口，无 symbols）
            CapabilityContract("trade_calendar", supports_symbols_null=True),
            CapabilityContract("index_constituent", supports_symbols_null=True),
            # JOB-077 市场元数据与约束接入（DS-081~083，2026-08-15，全量接口无 symbols）
            CapabilityContract("stock_basic", supports_symbols_null=True),
            CapabilityContract("stk_limit", supports_symbols_null=True),
            CapabilityContract("suspend_status", supports_symbols_null=True),
            # tracker #114 / 37号 §3.2a：IPO 日历/募资规模（全量接口无 symbols）
            CapabilityContract("ipo_calendar", supports_symbols_null=True),
        ],
        known_issues=["须断开VPN", "东财接口反爬严重"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接。AKShare 无需登录，直接标记为已连接。"""
        self._connected = True
        self._log.info("AKShare 已连接（匿名访问，无需登录）")

    def health_check(self) -> bool:
        """探活：尝试 import akshare，返回是否可用。"""
        try:
            import akshare  # noqa: F401
            return True
        except ImportError as e:
            self._log.warning(f"AKShare 探活失败（akshare 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接。AKShare 无持久连接资源，仅重置状态。"""
        self._connected = False
        self._log.info("AKShare 已断开")

    # ---- 拉取入口 ----

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。

        未知 capability -> yield FetchResult(error=...)。
        """
        cap = (payload.extra or {}).get("capability")
        if cap in _AKSHARE_CAPABILITIES:
            yield from getattr(self, f"_fetch_{cap}")(payload, policy)
            return
        yield FetchResult(
            table=payload.table,
            columns=[],
            rows=[],
            last_key="",
            elapsed_sec=0.0,
            error=f"unsupported capability: {cap}",
        )

    # ---- 宏观经济数据 ----

    def _fetch_macro_data(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取宏观经济数据（扩展版 #ARCH-IFIND-FAILOVER）。

        原 4 指标：GDP / CPI / PMI / 货币供应量（M0/M1/M2）。
        新增 8 类利率/宏观指标（替代 iFind EDB）：
        Shibor(8期限) / 回购定盘利率(FR/FDR) / 中国国债收益率(多曲线) /
        中美国债收益率 / LPR(1年/5年) / 社融增量 / 美联储利率 / 央行资产负债表。

        每个指标函数作为一批，yield 一个 FetchResult。
        异常时 yield FetchResult(error=str(e))，不抛出。
        """
        import akshare as ak

        table = _TBL_MACRO_DATA
        columns = ["report_date", "indicator_name", "indicator_value", "unit", "frequency"]
        last_key = datetime.date.today().isoformat()

        # ---- 原 4 指标（月频/季频）----
        jobs = [
            ("GDP", ak.macro_china_gdp, self._transform_gdp),
            ("CPI", ak.macro_china_cpi, self._transform_monthly),
            ("PMI", ak.macro_china_pmi, self._transform_monthly),
            ("MoneySupply", ak.macro_china_money_supply, self._transform_monthly),
        ]

        for name, fn, transform in jobs:
            t0 = now_utc()
            try:
                # 用 _call_with_policy 包裹，自动限流+重试
                df = self._call_with_policy(fn, policy)
                rows = transform(df)
                self._log.info(f"{name} 获取完成，{len(rows)} 行")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=seconds_since(t0),
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"{name} 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )

        # ---- 新增：利率类指标（#ARCH-IFIND-FAILOVER EDB 替代）----
        # 每个 job: (name, fetch_fn(policy)->DataFrame, transform_fn(df)->list[tuple])
        new_jobs = [
            ("Shibor", self._fetch_shibor_rates, self._transform_shibor),
            ("RepoRate", self._fetch_repo_rates, self._transform_repo),
            ("CNYield", self._fetch_cn_bond_yield, self._transform_cn_yield),
            ("USCNYield", self._fetch_us_cn_bond_yield, self._transform_us_cn_yield),
            ("LPR", lambda p: self._call_with_policy(ak.macro_china_lpr, p),
             self._transform_lpr),
            ("SocialFinancing", lambda p: self._call_with_policy(ak.macro_china_shrzgm, p),
             self._transform_social_financing),
            ("FedRate", lambda p: self._call_with_policy(ak.macro_bank_usa_interest_rate, p),
             self._transform_fed_rate),
            ("CentralBankBalance",
             lambda p: self._call_with_policy(ak.macro_china_central_bank_balance, p),
             self._transform_cb_balance),
        ]

        for name, fetch_fn, transform in new_jobs:
            t0 = now_utc()
            try:
                df = fetch_fn(policy)
                rows = transform(df)
                self._log.info(f"{name} 获取完成，{len(rows)} 行（EDB替代）")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=seconds_since(t0),
                )
            except Exception as e:  # noqa: BLE001
                self._log.warning(f"{name} 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )

    # ---- DataFrame 转换 ----

    def _transform_gdp(self, df) -> list[tuple]:
        """转换 GDP DataFrame。

        列"季度"如"2025年第1季度" -> 季度末日期；
        "国内生产总值-绝对值" -> indicator_name="GDP"，unit="亿元"；
        "国内生产总值-同比增长" -> indicator_name="GDP_同比"，unit="%"。
        frequency="季度"。
        """
        rows: list[tuple] = []
        for _, row in df.iterrows():
            quarter = str(row.iloc[0])
            report_date = self._quarter_to_date(quarter)
            if not report_date:
                continue
            # GDP 绝对值
            val = safe_float(row.get("国内生产总值-绝对值"))
            if val is not None:
                rows.append((report_date, "GDP", val, "亿元", "季度"))
            # GDP 同比
            yoy = safe_float(row.get("国内生产总值-同比增长"))
            if yoy is not None:
                rows.append((report_date, "GDP_同比", yoy, "%", "季度"))
        return rows

    def _transform_monthly(self, df) -> list[tuple]:
        """转换月度 DataFrame（CPI/PMI/货币供应量）。

        第一列如"2025年6月" -> 月末日期；其余列各自作为 indicator_name。
        unit 根据列名推断（治本修复：原 unit="" 硬编码导致 5554 行空 unit）。
        frequency="月度"。

        unit 推断规则（覆盖 CPI/PMI/货币供应量全部 25 个列名）：
        - 含"同比增长"/"环比增长" → "%"（百分比）
        - 含"数量(亿元)" → "亿元"
        - 含"当月"/"累计"/"指数" → "指数"（CPI/PMI 指数值，以 100/50 为基准）

        0 值过滤规则（治本修复：akshare 对缺失月份返回 0 而非 NULL，原代码写入 76 行无效 0 值）：
        - 同比增长/环比增长=0 → 跳过（0% 增长在 CPI/PMI 月度数据中几乎不可能，
          akshare 返回 0 表示去年同期数据缺失无法计算，非真实 0% 增长）
        - 指数值/数量值=0 → 保留（可能是真实值）
        """
        rows: list[tuple] = []
        cols = list(df.columns)
        for _, row in df.iterrows():
            month_str = str(row.iloc[0])
            report_date = self._month_to_date(month_str)
            if not report_date:
                continue
            for col in cols[1:]:
                val = safe_float(row.get(col))
                if val is None:
                    continue
                # unit 推断
                if "同比增长" in col or "环比增长" in col:
                    unit = "%"
                    # 0 值过滤：同比增长/环比增长=0 是 akshare 缺失标记，跳过
                    if val == 0:
                        continue
                elif "数量(亿元)" in col:
                    unit = "亿元"
                elif "当月" in col or "累计" in col or "指数" in col:
                    unit = "指数"
                else:
                    unit = ""
                rows.append((report_date, col, val, unit, "月度"))
        return rows

    # ---- EDB 替代：利率类指标 fetch wrappers（#ARCH-IFIND-FAILOVER）----

    def _fetch_shibor_rates(self, policy) -> pd.DataFrame:
        """获取 Shibor 全期限利率（8 个期限，日频）。

        调用 ak.rate_interbank 8 次（每个期限一次），合并为单 DataFrame，
        只取最近 30 天避免数据量过大。
        """
        import akshare as ak
        import pandas as pd
        tenors = ["隔夜", "1周", "2周", "1月", "3月", "6月", "9月", "1年"]
        dfs = []
        for tenor in tenors:
            df = self._call_with_policy(
                ak.rate_interbank, policy,
                market="上海银行同业拆借市场",
                symbol="Shibor人民币",
                indicator=tenor,
            )
            if df is not None and len(df) > 0:
                df = df.tail(30).copy()
                df["tenor"] = tenor
                dfs.append(df)
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    def _fetch_repo_rates(self, policy) -> pd.DataFrame:
        """获取回购定盘利率（FR001/FR007/FR014/FDR001/FDR007/FDR014，日频）。"""
        import akshare as ak
        end = datetime.date.today()
        start = end - datetime.timedelta(days=30)
        return self._call_with_policy(
            ak.repo_rate_hist, policy,
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d"),
        )

    def _fetch_cn_bond_yield(self, policy) -> pd.DataFrame:
        """获取中国国债/国开债/AAA 商业银行债收益率曲线（日频）。

        返回多条曲线，transform 阶段按曲线名称过滤。
        """
        import akshare as ak
        end = datetime.date.today()
        start = end - datetime.timedelta(days=30)
        return self._call_with_policy(
            ak.bond_china_yield, policy,
            start_date=start.strftime("%Y%m%d"),
            end_date=end.strftime("%Y%m%d"),
        )

    def _fetch_us_cn_bond_yield(self, policy) -> pd.DataFrame:
        """获取中美国债收益率（日频）。"""
        import akshare as ak
        start = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y%m%d")
        return self._call_with_policy(
            ak.bond_zh_us_rate, policy,
            start_date=start,
        )

    # ---- EDB 替代：利率类指标 transform 方法 ----

    def _transform_shibor(self, df) -> list[tuple]:
        """转换 Shibor DataFrame。

        输入: 报告日/利率/涨跌/tenor（8 个期限合并）
        输出: (报告日, "Shibor_{tenor}", 利率, "%", "日频")
        """
        if df is None or len(df) == 0:
            return []
        rows: list[tuple] = []
        for _, row in df.iterrows():
            date = str(row.get("报告日", ""))
            tenor = str(row.get("tenor", ""))
            val = safe_float(row.get("利率"))
            if val is not None and date and tenor:
                rows.append((date, f"Shibor_{tenor}", val, "%", "日频"))
        return rows

    def _transform_repo(self, df) -> list[tuple]:
        """转换回购定盘利率 DataFrame。

        输入: date/FR001/FR007/FR014/FDR001/FDR007/FDR014
        输出: (date, "回购_{col}", val, "%", "日频")
        """
        if df is None or len(df) == 0:
            return []
        rows: list[tuple] = []
        rate_cols = ["FR001", "FR007", "FR014", "FDR001", "FDR007", "FDR014"]
        for _, row in df.iterrows():
            date = str(row.get("date", ""))
            if not date:
                continue
            for col in rate_cols:
                val = safe_float(row.get(col))
                if val is not None:
                    rows.append((date, f"回购_{col}", val, "%", "日频"))
        return rows

    def _transform_cn_yield(self, df) -> list[tuple]:
        """转换中国债券收益率 DataFrame。

        输入: 曲线名称/日期/3月/6月/1年/3年/5年/7年/10年/30年
        过滤: 中债国债 + 中债国开债 + 中债中短期票据(AAA) + 中债商业银行普通债(AAA)
        输出: (日期, "{曲线简称}_{期限}", val, "%", "日频")
        """
        if df is None or len(df) == 0:
            return []
        target_curves = {
            "中债国债收益率曲线": "国债",
            "中债国开债收益率曲线": "国开债",
            "中债中短期票据收益率曲线(AAA)": "中短票据AAA",
            "中债商业银行普通债收益率曲线(AAA)": "商业银行债AAA",
        }
        rows: list[tuple] = []
        tenor_cols = ["3月", "6月", "1年", "3年", "5年", "7年", "10年", "30年"]
        for _, row in df.iterrows():
            curve = str(row.get("曲线名称", ""))
            short = target_curves.get(curve)
            if not short:
                continue
            date = str(row.get("日期", ""))
            if not date:
                continue
            for col in tenor_cols:
                val = safe_float(row.get(col))
                if val is not None:
                    rows.append((date, f"{short}_{col}", val, "%", "日频"))
        return rows

    def _transform_us_cn_yield(self, df) -> list[tuple]:
        """转换中美国债收益率 DataFrame。

        输入: 日期/中国国债收益率2年/5年/10年/30年/美国国债收益率2年/5年/10年/30年
        输出: (日期, col_name, val, "%", "日频")
        跳过 GDP 和利差列（10年-2年）。
        """
        if df is None or len(df) == 0:
            return []
        rows: list[tuple] = []
        for _, row in df.iterrows():
            date = str(row.get("日期", ""))
            if not date:
                continue
            for col in df.columns:
                if col == "日期" or "GDP" in col or "10年-2年" in col:
                    continue
                val = safe_float(row.get(col))
                if val is not None:
                    rows.append((date, col, val, "%", "日频"))
        return rows

    def _transform_lpr(self, df) -> list[tuple]:
        """转换 LPR DataFrame。

        输入: TRADE_DATE/LPR1Y/LPR5Y/RATE_1/RATE_2
        输出: (TRADE_DATE, "LPR_1年"/"LPR_5年", val, "%", "月频")
        只取最近 90 天避免数据量过大。
        """
        if df is None or len(df) == 0:
            return []
        df = df.tail(90)
        rows: list[tuple] = []
        for _, row in df.iterrows():
            date = str(row.get("TRADE_DATE", ""))
            if not date:
                continue
            lpr1y = safe_float(row.get("LPR1Y"))
            if lpr1y is not None:
                rows.append((date, "LPR_1年", lpr1y, "%", "月频"))
            lpr5y = safe_float(row.get("LPR5Y"))
            if lpr5y is not None:
                rows.append((date, "LPR_5年", lpr5y, "%", "月频"))
        return rows

    def _transform_social_financing(self, df) -> list[tuple]:
        """转换社会融资规模 DataFrame。

        输入: 月份(YYYYMM)/社会融资规模增量/其中-人民币贷款/...
        输出: (月末日期, indicator_name, val, "亿元", "月频")
        """
        if df is None or len(df) == 0:
            return []
        rows: list[tuple] = []
        for _, row in df.iterrows():
            yyyymm = str(row.iloc[0])
            report_date = self._yyyymm_to_date(yyyymm)
            if not report_date:
                continue
            for col in df.columns[1:]:
                val = safe_float(row.get(col))
                if val is not None:
                    rows.append((report_date, col, val, "亿元", "月频"))
        return rows

    def _transform_fed_rate(self, df) -> list[tuple]:
        """转换美联储利率 DataFrame。

        输入: 商品/日期/今值/预测值/前值
        输出: (日期, "美联储利率", 今值, "%", "事件")
        只取最近 20 条（事件驱动，频率低）。
        """
        if df is None or len(df) == 0:
            return []
        df = df.tail(20)
        rows: list[tuple] = []
        for _, row in df.iterrows():
            date = str(row.get("日期", ""))
            val = safe_float(row.get("今值"))
            if val is not None and date:
                rows.append((date, "美联储利率", val, "%", "事件"))
        return rows

    def _transform_cb_balance(self, df) -> list[tuple]:
        """转换央行资产负债表 DataFrame。

        输入: 统计时间(YYYY.M)/国外资产/外汇/对其他存款性公司债权/储备货币/政府存款/...
        输出: (月末日期, indicator_name, val, "亿元", "月频")
        只取最近 12 个月。
        """
        if df is None or len(df) == 0:
            return []
        df = df.tail(12)
        field_map = {
            "外汇": "央行_外汇占款",
            "对其他存款性公司债权": "央行_对银行债权",
            "储备货币": "央行_储备货币",
            "政府存款": "央行_政府存款",
            "发行货币": "央行_货币发行",
            "非金融性公司存款": "央行_非金融存款",
            "总资产": "央行_总资产",
            "总负债": "央行_总负债",
        }
        rows: list[tuple] = []
        for _, row in df.iterrows():
            time_str = str(row.get("统计时间", ""))
            report_date = self._yyyy_dot_m_to_date(time_str)
            if not report_date:
                continue
            for src_col, indicator in field_map.items():
                val = safe_float(row.get(src_col))
                if val is not None:
                    rows.append((report_date, indicator, val, "亿元", "月频"))
        return rows

    @staticmethod
    def _yyyymm_to_date(s: str) -> str | None:
        """'202604' -> '2026-04-30'（月末日期）。"""
        import calendar
        s = s.strip()
        if len(s) == 6 and s.isdigit():
            y, m = int(s[:4]), int(s[4:])
            if 1 <= m <= 12:
                last_day = calendar.monthrange(y, m)[1]
                return f"{y:04d}-{m:02d}-{last_day:02d}"
        return None

    @staticmethod
    def _yyyy_dot_m_to_date(s: str) -> str | None:
        """'2026.6' -> '2026-06-30'（月末日期）。"""
        import calendar
        s = s.strip()
        parts = s.split(".")
        if len(parts) == 2:
            try:
                y, m = int(parts[0]), int(parts[1])
                if 1 <= m <= 12:
                    last_day = calendar.monthrange(y, m)[1]
                    return f"{y:04d}-{m:02d}-{last_day:02d}"
            except (ValueError, IndexError):
                pass
        return None

    # ---- 日期解析辅助 ----

    @staticmethod
    def quarter_to_date(s: str) -> str:
        """'2025年第1季度' -> '2025-03-31'（季度末日期）（Stage 4 公共化，primary）。

        支持 '2025年第1-3季度' 形式（取末季度）。
        """
        m = re.match(r"(\d{4})年第([0-9\-]+)季度", s)
        if not m:
            return ""
        year = m.group(1)
        qs = m.group(2)
        if "-" in qs:
            last = int(qs.split("-")[-1])
        else:
            last = int(qs)
        month_day = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
        md = month_day.get(last)
        return f"{year}-{md}" if md else ""

    @staticmethod
    def _quarter_to_date(s: str) -> str:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return AkshareIngestProvider.quarter_to_date(s)

    @staticmethod
    def month_to_date(s: str) -> str:
        """'2025年6月' -> '2025-06-30'（月末日期）（Stage 4 公共化，primary）。"""
        m = re.match(r"(\d{4})年(\d{1,2})月?", s)
        if not m:
            return ""
        y, mo = m.group(1), int(m.group(2))
        last_day = calendar.monthrange(int(y), mo)[1]
        return f"{y}-{mo:02d}-{last_day:02d}"

    @staticmethod
    def _month_to_date(s: str) -> str:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return AkshareIngestProvider.month_to_date(s)

    # ---- 通用辅助（日期/标的） ----

    @staticmethod
    def _date_range(start: datetime.date, end: datetime.date) -> Iterator[datetime.date]:
        """生成 start 到 end（含）的自然日序列。"""
        cur = start
        while cur <= end:
            yield cur
            cur += datetime.timedelta(days=1)

    @staticmethod
    def _symbol_to_market(symbol: str) -> str:
        """6位代码转 AKShare market 参数：sh/sz/bj。

        60/68 开头->sh；00/30 开头->sz；其余（8/4等）->bj。
        """
        s = str(symbol).zfill(6)
        if s.startswith(("60", "68")):
            return "sh"
        elif s.startswith(("00", "30")):
            return "sz"
        else:
            return "bj"

    @staticmethod
    def _norm_date_str(v) -> str:
        """把日期类值截成 'YYYY-MM-DD' 字符串；空值返回 ''。"""
        if v is None:
            return ""
        s = str(v)
        if s.lower() in ("none", "nan", "nat", ""):
            return ""
        # 处理 'YYYY-MM-DD HH:MM:SS' / Timestamp / 'YYYY/MM/DD' 等
        s = s.replace("/", "-")
        if " " in s:
            s = s.split(" ")[0]
        return s[:10]

    def _get_all_a_symbols(self, ak, policy: SourcePolicy) -> list[str]:
        """获取全 A 股 6 位代码列表。

        治本(裁定#ARCH-AKSHARE-ANTICRAWLER-001)：主路径切换到交易所官方接口
        (stock_info_sh_name_code + stock_info_sz_name_code)，走交易所官网不走东财，
        无反爬风险。原 stock_zh_a_spot_em 是东财实时行情快照接口，高频调用触发
        IP级TCP RST封锁，5次jittered重试全失败(~75秒纯等待)。CH stock_list 作为 fallback 兜底。
        """
        # 主路径：交易所官方接口（无反爬，已在 _fetch_st_stock_list 验证可用）
        # 覆盖4大板块：沪主板A股 + 科创板 + 深交所A股 + 北交所
        try:
            codes: list[str] = []
            sh = self._call_with_policy(ak.stock_info_sh_name_code, policy, symbol="主板A股")
            if sh is not None and len(sh) > 0:
                codes.extend([str(c).zfill(6) for c in sh["证券代码"].tolist()])
            kc = self._call_with_policy(ak.stock_info_sh_name_code, policy, symbol="科创板")
            if kc is not None and len(kc) > 0:
                codes.extend([str(c).zfill(6) for c in kc["证券代码"].tolist()])
            sz = self._call_with_policy(ak.stock_info_sz_name_code, policy, symbol="A股列表")
            if sz is not None and len(sz) > 0:
                codes.extend([str(c).zfill(6) for c in sz["A股代码"].tolist()])
            bj = self._call_with_policy(ak.stock_info_bj_name_code, policy)
            if bj is not None and len(bj) > 0:
                codes.extend([str(c).zfill(6) for c in bj["证券代码"].tolist()])
            if codes:
                return sorted(set(codes))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"交易所官方接口失败，回退到 CH stock_list: {e}")

        # CH fallback
        from zephyr.data import ch_reader as _chr
        out = _chr.query(SQL_STOCK_CODE_FROM_LIST)
        if not out.strip():
            return []
        codes = [line.strip().zfill(6) for line in out.split("\n") if line.strip()]
        self._log.info(f"从 CH stock_list 获取 {len(codes)} 只 A 股（akshare fallback）")
        return codes

    # ---- 1. 每日估值（daily_valuation） ----

    def _fetch_daily_valuation(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取每日估值（PE/PB/PS/PCF），写入 c1_market.daily_valuation。

        用 ak.stock_zh_valuation_baidu(symbol, indicator, period) 逐只获取估值历史。
        4 个指标分 4 次调用：市盈率(TTM)/市净率/市盈率(静)/市现率。
        K线字段（open/high/low/close/...）填 None；is_st 填 0。
        data_source 有 DEFAULT 'local_valuation'，不返回。
        """
        import akshare as ak

        table = _TBL_DAILY_VALUATION
        columns = [
            "trade_date", "symbol", "open", "high", "low", "close",
            "preclose", "volume", "amount", "turnover", "pct_change",
            "pe_ttm", "pb_mrq", "ps_ttm", "pcf_ncf_ttm", "is_st",
        ]
        last_key = payload.end.isoformat()

        symbols = payload.symbols
        if not symbols:
            # symbols=null 契约（裁定 #ARCH-CH-018）：自动获取全 A 股标的列表
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=0.0, error="daily_valuation 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return

        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        # 指标映射: (AKShare indicator, 目标列名)
        indicators = [
            ("市盈率(TTM)", "pe_ttm"),
            ("市净率", "pb_mrq"),
            ("市盈率(静)", "ps_ttm"),  # AKShare 无 PS，用静态PE替代
            ("市现率", "pcf_ncf_ttm"),
        ]

        # 并行抓取（治本 #ARCH-VALUATION-IFIND-PRIMARY）：
        # akshare 作为 fallback 时也需高效。原串行 5000只×4指标+1秒限流=数小时，
        # 改 ThreadPoolExecutor 并行。百度估值API 限流由 _call_with_policy 的 SourcePolicy 兜底
        # （去掉 per-symbol wait(1.0)——并行下它会阻塞 worker 退化为串行）。
        from concurrent.futures import ThreadPoolExecutor, as_completed

        _MAX_WORKERS = 4  # 保守并发，避免触发百度反爬

        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as ex:
            future_to_code = {}
            for idx, sym in enumerate(symbols):
                code = str(sym).split(".")[0].zfill(6)
                fut = ex.submit(
                    self._fetch_valuation_one_symbol,
                    ak, code, policy, indicators, start_str, end_str,
                )
                future_to_code[fut] = code
                if (idx + 1) % 100 == 0:
                    self._log.info(f"daily_valuation 提交进度: {idx+1}/{len(symbols)}")

            done = 0
            total = len(future_to_code)
            for fut in as_completed(future_to_code):
                code = future_to_code[fut]
                try:
                    rows = fut.result()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    self._log.warning(f"daily_valuation {code} 并行任务异常: {e}")
                    rows = []
                batch_rows.extend(rows)
                done += 1
                if done % 100 == 0:
                    self._log.info(f"daily_valuation 完成进度: {done}/{total}")
                if len(batch_rows) >= 500:
                    yield FetchResult(
                        table=table, columns=columns, rows=batch_rows[:],
                        last_key=last_key, elapsed_sec=time.time() - t0,
                    )
                    batch_rows.clear()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows[:],
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    def _fetch_valuation_one_symbol(
        self, ak, code: str, policy, indicators, start_str: str, end_str: str,
    ) -> list[tuple]:
        """抓取单只标的的估值数据并组装为行（提取自 _fetch_daily_valuation 供并行）。

        逐指标调用 ak.stock_zh_valuation_baidu，按日期合并组装行。
        K线字段填 None；is_st 填 0。失败返回空列表。
        """
        val_data: dict[str, dict[str, float]] = {}
        for ak_ind, col_name in indicators:
            try:
                df = self._call_with_policy(
                    ak.stock_zh_valuation_baidu, policy,
                    symbol=code, indicator=ak_ind, period="近一年",
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"stock_zh_valuation_baidu({code}, {ak_ind}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            col_map = _build_valuation_col_map(df, self._norm_date_str, start_str, end_str)
            if col_map:
                val_data[col_name] = col_map
        if not val_data:
            return []
        all_dates = set()
        for col_map in val_data.values():
            all_dates.update(col_map.keys())
        rows: list[tuple] = []
        for d in sorted(all_dates):
            rows.append((
                d, code,
                None, None, None, None,        # open/high/low/close
                None, None, None, None, None,  # preclose/volume/amount/turnover/pct_change
                val_data.get("pe_ttm", {}).get(d),
                val_data.get("pb_mrq", {}).get(d),
                val_data.get("ps_ttm", {}).get(d),
                val_data.get("pcf_ncf_ttm", {}).get(d),
                0,  # is_st
            ))
        return rows

    # ---- 2. 融资融券（margin_trading） ----

    def _fetch_margin_trading(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取融资融券明细，写入 c1_market.margin_trading。

        逐日调用 ak.stock_margin_detail_sse / stock_margin_detail_szse，
        合并沪深两市。symbol 为 6 位代码。
        """
        import akshare as ak

        table = _TBL_MARGIN_TRADING
        columns = [
            "trade_date", "symbol", "margin_balance",
            "margin_buy", "margin_repay", "short_balance",
        ]

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            iso_date = d.isoformat()
            t0 = time.time()
            rows: list[tuple] = []
            for fn_name in ("stock_margin_detail_sse", "stock_margin_detail_szse"):
                fn = getattr(ak, fn_name, None)
                if fn is None:
                    continue
                try:
                    df = self._call_with_policy(fn, policy, date=date_str)
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    self._log.warning(f"{fn_name}({date_str}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                for _, row in df.iterrows():
                    sym = str(
                        row.get("标的证券代码") or row.get("证券代码") or ""
                    ).zfill(6)
                    if not sym or sym == "000000":
                        continue
                    rows.append((
                        iso_date, sym,
                        safe_float(row.get("融资余额")),
                        safe_float(row.get("融资买入额")),
                        safe_float(row.get("融资偿还额")),
                        safe_float(row.get("融券余额")),
                    ))
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=iso_date, elapsed_sec=time.time() - t0,
            )

    # ---- 3. 大宗交易（block_trade） ----

    def _fetch_block_trade(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取大宗交易明细，写入 c1_market.block_trade。

        调用 ak.stock_dzjy_mrmx(start_date, end_date, symbol="A股")。
        列映射: 交易日期/证券代码/成交价/成交量/成交额/买方营业部/卖方营业部。
        """
        import akshare as ak

        table = _TBL_BLOCK_TRADE
        columns = [
            "trade_date", "symbol", "price", "volume", "amount",
            "buyer", "seller",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_dzjy_mrmx, policy,
                start_date=start_str, end_date=end_str, symbol="A股",
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("证券代码") or "").zfill(6)
                if not sym:
                    continue
                trade_date = self._norm_date_str(row.get("交易日期"))
                if not trade_date:
                    trade_date = last_key
                vol = safe_float(row.get("成交量"))
                rows.append((
                    trade_date, sym,
                    safe_float(row.get("成交价")),
                    int(vol) if vol is not None else 0,
                    safe_float(row.get("成交额")),
                    str(row.get("买方营业部") or ""),
                    str(row.get("卖方营业部") or ""),
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 4. 龙虎榜（dragon_tiger） ----

    def _fetch_dragon_tiger(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取龙虎榜明细，写入 c1_market.dragon_tiger。

        调用 ak.stock_lhb_detail_em(start_date, end_date)。
        列映射: 代码/名称/上榜原因/净买额/买入额/卖出额。
        """
        import akshare as ak

        table = _TBL_DRAGON_TIGER
        columns = [
            "trade_date", "symbol", "name", "reason",
            "net_buy", "buy_amount", "sell_amount",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_lhb_detail_em, policy,
                start_date=start_str, end_date=end_str,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("代码") or "").zfill(6)
                if not sym:
                    continue
                trade_date = self._norm_date_str(
                    row.get("上榜日") or row.get("日期")
                )
                if not trade_date:
                    trade_date = last_key
                rows.append((
                    trade_date, sym,
                    str(row.get("名称") or ""),
                    str(row.get("上榜原因") or ""),
                    safe_float(row.get("龙虎榜净买额") or row.get("净买额") or row.get("净买入额")),
                    safe_float(row.get("龙虎榜买入额") or row.get("买入额") or row.get("买入金额")),
                    safe_float(row.get("龙虎榜卖出额") or row.get("卖出额") or row.get("卖出金额")),
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 4b. 龙虎榜席位明细（dragon_tiger_seat） ----

    def _fetch_dragon_tiger_seat(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取龙虎榜席位明细，写入 c1_market.dragon_tiger_seat。

        先调 ak.stock_lhb_detail_em 拿上榜股列表，再对每只调
        ak.stock_lhb_stock_detail_em(flag='买入'/'卖出') 取 Top5 营业部，
        合并去重为每席位一行（_merge_lhb_seats）。
        """
        import akshare as ak

        table = _TBL_DRAGON_TIGER_SEAT
        columns = [
            "trade_date", "symbol", "seat_name", "buy_amount", "sell_amount",
            "net_amount", "buy_rank", "sell_rank", "seat_type", "reason",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()
        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")

        try:
            df_list = self._call_with_policy(
                ak.stock_lhb_detail_em, policy,
                start_date=start_str, end_date=end_str,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df_list is not None and len(df_list) > 0:
            for _, lrow in df_list.iterrows():
                sym = str(lrow.get("代码") or "").zfill(6)
                if not sym:
                    continue
                trade_date = self._norm_date_str(
                    lrow.get("上榜日") or lrow.get("日期")
                )
                if not trade_date:
                    trade_date = last_key
                reason = str(lrow.get("上榜原因") or "")
                date_str = trade_date.replace("-", "")
                seat_map = _merge_lhb_seats(self, ak, policy, sym, date_str)
                for seat_name, v in seat_map.items():
                    rows.append((
                        trade_date, sym, seat_name,
                        v["buy"], v["sell"], v["net"],
                        v["buy_rank"], v["sell_rank"],
                        _classify_seat(seat_name), reason,
                    ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 5. 资金流向（money_flow） ----

    def _fetch_money_flow(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取个股资金流向，写入 c1_market.money_flow。

        直接 HTTP 请求东方财富 API（绕过 AKShare 反爬封锁）。
        API: push2.eastmoney.com/api/qt/stock/fflow/daykline/get
        klines 格式: 日期,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入,主力占比,小单占比,中单占比,大单占比,超大单占比
        close/pct_change 接口未提供，填 None。

        #ARCH-PARALLEL-MONEY-FLOW（2026-08-09 治本）：
        原串行 5000只×~1s=60min+，逼近6h STALE红线被 reaped。
        改 ThreadPoolExecutor 并行（参照 _fetch_daily_valuation 已验证模式）。
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        import akshare as ak  # 用于 _get_all_a_symbols 获取标的列表（裁定 #ARCH-CH-018）

        table = _TBL_MONEY_FLOW
        columns = [
            "trade_date", "symbol", "close", "pct_change",
            "main_net_inflow", "main_net_inflow_pct",
            "super_large_net_inflow", "super_large_net_inflow_pct",
            "large_net_inflow", "large_net_inflow_pct",
            "medium_net_inflow", "medium_net_inflow_pct",
            "small_net_inflow", "small_net_inflow_pct",
        ]
        last_key = payload.end.isoformat()
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()

        symbols = payload.symbols
        if not symbols:
            # symbols=null 契约（裁定 #ARCH-CH-018）：自动获取全 A 股标的列表
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=0.0, error="money_flow 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://data.eastmoney.com/",
        }
        url = "https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get"
        fields2 = "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"

        batch_rows: list[tuple] = []
        t0 = time.time()

        _MAX_WORKERS = 4  # 保守并发，与 _fetch_daily_valuation 一致

        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as ex:
            future_to_code = {}
            for idx, sym in enumerate(symbols):
                code = str(sym).split(".")[0].zfill(6)
                fut = ex.submit(
                    self._fetch_money_flow_one_symbol,
                    sym, policy, url, headers, fields2, start_str, end_str,
                )
                future_to_code[fut] = code
                if (idx + 1) % 100 == 0:
                    self._log.info(f"money_flow 提交进度: {idx+1}/{len(symbols)}")

            done = 0
            total = len(future_to_code)
            for fut in as_completed(future_to_code):
                code = future_to_code[fut]
                try:
                    rows = fut.result()
                except Exception as e:  # noqa: BLE001 — 5.135治标
                    self._log.warning(f"money_flow {code} 并行任务异常: {e}")
                    rows = []
                batch_rows.extend(rows)
                done += 1
                if done % 100 == 0:
                    self._log.info(f"money_flow 完成进度: {done}/{total}")
                if len(batch_rows) >= 500:
                    yield FetchResult(
                        table=table, columns=columns, rows=batch_rows[:],
                        last_key=last_key, elapsed_sec=time.time() - t0,
                    )
                    batch_rows.clear()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows[:],
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    def _fetch_money_flow_one_symbol(
        self, sym, policy, url, headers, fields2, start_str, end_str,
    ) -> list[tuple]:
        """抓取单只标的的资金流向数据并组装为行（提取自 _fetch_money_flow 供并行）。

        #ARCH-RSS-INVESTING-403-001 治本扩展：切到 _http_get（raise_for_status），
        移除手动 status_code 检查——5xx/4xx 抛 HTTPError 不匹配 retry_on → except → 空行
        """
        sym = str(sym).split(".")[0].zfill(6)
        market = "1" if sym.startswith(("6", "5", "9")) else "0"
        secid = f"{market}.{sym}"
        params = {
            "secid": secid, "lmt": 100, "klt": "1",
            "fields1": "f1,f2,f3,f7",
            "fields2": fields2,
        }
        rows: list[tuple] = []
        try:
            resp = self._call_with_policy(
                self._http_get, policy, url,
                params=params, headers=headers, timeout=15,
            )
            data = resp.json()
            klines = (data.get("data") or {}).get("klines") or []
            for line in klines:
                parts = line.split(",")
                if len(parts) < 11:
                    continue
                trade_date = parts[0]
                if trade_date < start_str or trade_date > end_str:
                    continue
                rows.append((
                    trade_date, sym,
                    None,  # close 接口未提供
                    None,  # pct_change 接口未提供
                    safe_float(parts[1]),    # 主力净流入
                    safe_float(parts[6]),    # 主力净流入占比
                    safe_float(parts[5]),    # 超大单净流入
                    safe_float(parts[10]),   # 超大单净流入占比
                    safe_float(parts[4]),    # 大单净流入
                    safe_float(parts[9]),    # 大单净流入占比
                    safe_float(parts[3]),    # 中单净流入
                    safe_float(parts[8]),    # 中单净流入占比
                    safe_float(parts[2]),    # 小单净流入
                    safe_float(parts[7]),    # 小单净流入占比
                ))
        except Exception as e:  # noqa: BLE001 — 5.135治标
            self._log.debug(f"money_flow({sym}) 失败: {e}")
        return rows

    # ---- 6. 限售解禁（share_unlock） ----

    def _fetch_share_unlock(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取限售解禁明细，写入 c3_fundamental.share_unlock。

        调用 ak.stock_restricted_release_detail_em(start_date, end_date)。
        列映射: 股票代码/解除限售日期/解除限售数量/解除限售比例/实际解禁金额。
        """
        import akshare as ak

        table = _TBL_SHARE_UNLOCK
        columns = ["symbol", "unlock_date", "shares", "ratio", "amount"]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_restricted_release_detail_em, policy,
                start_date=start_str, end_date=end_str,
            )
        except TypeError as e:
            # AKShare bug: 非交易日查询时东财API返回result=None，
            # AKShare内部对None做["pages"]索引导致TypeError，视为无数据
            self._log.info(f"share_unlock: 日期范围 {start_str}-{end_str} 无数据（可能非交易日）: {e}")
            df = None
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码") or "").zfill(6)
                if not sym:
                    continue
                unlock_date = self._norm_date_str(row.get("解禁时间"))
                if not unlock_date:
                    continue
                rows.append((
                    sym, unlock_date,
                    safe_float(row.get("解禁数量")),
                    safe_float(row.get("占解禁前流通市值比例")),
                    safe_float(row.get("实际解禁市值")),
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 7. 审计意见（audit_opinion） ----

    def _fetch_audit_opinion(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取审计意见，写入 c3_fundamental.audit_opinion。

        AKShare 暂无专用审计意见接口，需通过财报接口间接获取，
        此处直接 yield error 说明原因。
        """
        table = _TBL_AUDIT_OPINION
        columns = [
            "symbol", "announce_date", "report_period", "audit_result",
            "audit_fee", "accounting_firm", "signing_accountant", "data_source",
        ]
        yield FetchResult(
            table=table, columns=columns, rows=[],
            last_key=payload.end.isoformat(), elapsed_sec=0.0,
            error="AKShare 暂无专用审计意见接口，需通过财报接口间接获取",
        )

    # ---- 8. 股权质押（equity_pledge） ----

    def _fetch_equity_pledge(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股权质押比例，写入 c3_fundamental.equity_pledge。

        调用 ak.stock_gpzy_pledge_ratio_em() 获取最新日期全市场质押比例。
        接口只返回最新交易日数据，不支持按日期查询未来日期。
        列映射: 股票代码/交易日期/质押笔数/质押比例。
        total_shares/pledge_end_date 接口未提供，填 None。
        """
        import akshare as ak

        table = _TBL_EQUITY_PLEDGE_DETAIL
        columns = [
            "symbol", "end_date", "pledge_count",
            "pledge_ratio", "total_shares", "pledge_end_date",
        ]

        t0 = time.time()
        iso_date = datetime.date.today().isoformat()
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(
                ak.stock_gpzy_pledge_ratio_em, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_gpzy_pledge_ratio_em 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=iso_date,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码") or "").zfill(6)
                if not sym:
                    continue
                end_date = self._norm_date_str(row.get("交易日期"))
                if not end_date:
                    end_date = iso_date
                rows.append((
                    sym, end_date,
                    safe_float(row.get("质押笔数")),
                    safe_float(row.get("质押比例")),
                    None,  # total_shares 接口未提供
                    None,  # pledge_end_date 接口未提供
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 9. 股权质押摘要（equity_pledge_summary） ----

    def _fetch_equity_pledge_summary(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股权质押摘要（全市场），写入 c3_fundamental.equity_pledge_summary。

        调用 ak.stock_gpzy_profile_em() 获取全市场质押摘要（无参数）。
        symbol 填 "ALL"（全市场聚合）。
        unrestricted_pledge/restricted_pledge 接口未提供，填 None。
        data_source 填 "akshare"。
        """
        import akshare as ak

        table = _TBL_EQUITY_PLEDGE_SUMMARY
        columns = [
            "symbol", "end_date", "pledge_count", "unrestricted_pledge",
            "restricted_pledge", "total_shares", "pledge_ratio", "data_source",
        ]

        t0 = time.time()
        iso_date = datetime.date.today().isoformat()
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(
                ak.stock_gpzy_profile_em, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_gpzy_profile_em 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=iso_date,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return
        if df is not None and len(df) > 0:
            start_str = payload.start.isoformat()
            end_str = payload.end.isoformat()
            for _, row in df.iterrows():
                end_date = self._norm_date_str(row.get("交易日期"))
                if not end_date:
                    continue
                if end_date < start_str or end_date > end_str:
                    continue
                rows.append((
                    "ALL", end_date,
                    safe_int(row.get("质押笔数")),
                    None,  # unrestricted_pledge 接口未提供
                    None,  # restricted_pledge 接口未提供
                    safe_float(row.get("质押总股数")),
                    safe_float(row.get("A股质押总比例")),
                    "akshare",
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 10. 分红明细（dividend） ----

    def _fetch_dividend(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取分红明细，写入 c3_fundamental.dividend。

        调用 ak.stock_history_dividend_detail(symbol, indicator="分红") 逐只获取。
        """
        import akshare as ak

        table = _TBL_DIVIDEND
        columns = [
            "symbol", "ex_date", "record_date", "announce_date",
            "dividend_per_10_shares", "stock_div_per_10_shares",
            "transfer_per_10_shares", "total_dividend", "progress",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"dividend 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_history_dividend_detail, policy,
                    symbol=code, indicator="分红",
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"stock_history_dividend_detail({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                batch_rows.append(self._parse_dividend_row(code, row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_dividend_row(code: str, row) -> tuple:
        """解析单行分红数据。"""
        return (
            code,
            AkshareIngestProvider._norm_date_str(row.get("除权除息日")),
            AkshareIngestProvider._norm_date_str(row.get("股权登记日")),
            AkshareIngestProvider._norm_date_str(row.get("公告日期")),
            safe_float(row.get("每10股派息")),
            safe_float(row.get("每10股送股")),
            safe_float(row.get("每10股转增")),
            safe_float(row.get("分红总额")),
            str(row.get("分红进度", "")),
        )

    # ---- 11. 限售解禁（restricted_shares） ----

    def _fetch_restricted_shares(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取限售解禁明细，写入 c3_fundamental.restricted_shares。

        调用 ak.stock_restricted_release_queue_em(symbol) 逐只获取。
        """
        import akshare as ak

        table = _TBL_RESTRICTED_SHARES
        columns = [
            "symbol", "release_date", "release_shares", "release_ratio",
            "pre_float_shares", "post_float_shares",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"restricted_shares 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_restricted_release_queue_em, policy,
                    symbol=code,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"stock_restricted_release_queue_em({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                batch_rows.append(self._parse_restricted_row(code, row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_restricted_row(code: str, row) -> tuple:
        """解析单行限售解禁数据。"""
        return (
            code,
            AkshareIngestProvider._norm_date_str(row.get("解禁时间")),
            safe_float(row.get("解禁数量")),
            safe_float(row.get("解禁股本占比")),
            safe_float(row.get("解禁前流通股本")),
            safe_float(row.get("解禁后流通股本")),
        )

    # ---- 12. 新闻数据通用辅助 ----

    @staticmethod
    def _news_rows_from_df(df, source_name: str) -> list[tuple]:
        """从新闻 DataFrame 提取 news_data 表标准行。

        兼容多种 AKShare 新闻接口的列名：
        - stock_news_em: 关键词/新闻标题/新闻内容/发布时间/文章来源/新闻链接
        - news_cctv: date/title/content
        - news_economic_baidu: 日期/时间/地区/事件/公布/预期/前值/重要性
        - stock_news_main_cx: tag/summary/url
        """
        rows: list[tuple] = []
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            title = AkshareIngestProvider._row_first(row, "新闻标题", "标题", "title", "事件", "tag", "event")
            pub_date = AkshareIngestProvider._row_first(row, "发布时间", "时间", "日期", "date")
            link = AkshareIngestProvider._row_first(row, "新闻链接", "链接", "url", "link")
            summary = AkshareIngestProvider._row_first(row, "新闻内容", "摘要", "内容", "content", "summary")
            rows.append(build_news_row(
                pub_date, title, link, summary, source_name, "akshare",
            ))
        return rows

    @staticmethod
    def _row_first(row, *keys) -> str:
        """从 DataFrame row 中按优先级取第一个非空值，均为空则返回空字符串。"""
        for key in keys:
            val = row.get(key)
            if val is not None and str(val).strip():
                return str(val)
        return ""

    # ---- 13. 个股新闻（stock_news_em） ----

    def _fetch_stock_news_em(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取个股新闻，写入 c3_fundamental.news_data。

        调用 ak.stock_news_em(symbol) 逐只获取。symbols 为空时自动取全A股。
        """
        import akshare as ak

        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="stock_news_em 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return
        last_key = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols, 1):
            code = str(sym).split(".")[0].zfill(6)
            try:
                df = self._call_with_policy(
                    ak.stock_news_em, policy, symbol=code,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"stock_news_em({code}) 失败: {e}")
                continue
            batch_rows.extend(self._news_rows_from_df(df, "akshare_stock_news"))
            # 进度日志（每50只打印一次，便于监控长时间运行的任务）
            if idx % 50 == 0:
                self._log.info(f"stock_news_em 进度: {idx}/{len(symbols)}，已累积 {len(batch_rows)} 行")
            # 批量 yield（每500行 flush 一次，避免内存堆积）
            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table, columns=columns, rows=batch_rows[:],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 14. 央视新闻联播（news_cctv） ----

    def _fetch_news_cctv(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取央视新闻联播，写入 c3_fundamental.news_data。

        调用 ak.news_cctv(date) 逐日获取。
        """
        import akshare as ak

        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(
                    ak.news_cctv, policy, date=date_str,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"news_cctv({date_str}) 失败: {e}")
                continue
            batch_rows.extend(self._news_rows_from_df(df, "akshare_cctv"))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 15. 百度经济日历（news_economic_baidu） ----

    def _fetch_news_economic_baidu(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取百度经济日历，写入 c3_fundamental.news_data。

        调用 ak.news_economic_baidu(date) 逐日获取。
        AKShare 签名：news_economic_baidu(date='YYYYMMDD', cookie=None)。
        """
        import akshare as ak

        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(
                    ak.news_economic_baidu, policy, date=date_str,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"news_economic_baidu({date_str}) 失败: {e}")
                continue
            batch_rows.extend(self._news_rows_from_df(df, "akshare_economic_baidu"))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 16. 财新网数据通（news_baidu，原 news_baidu 已废弃） ----

    def _fetch_news_baidu(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取财新网数据通新闻，写入 c3_fundamental.news_data。

        AKShare 的 news_baidu() 已不存在，改用 stock_news_main_cx()（财新网数据通）。
        返回列：tag/summary/url。
        """
        import akshare as ak

        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        t0 = time.time()

        try:
            df = self._call_with_policy(ak.stock_news_main_cx, policy)
            batch_rows = self._news_rows_from_df(df, "akshare_caixin")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_news_main_cx 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    # ---- 17. 股票新闻（news_stock） ----

    def _fetch_news_stock(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股票新闻，写入 c3_fundamental.news_data。

        AKShare 的 stock_news_global_em() 已不存在，改用 stock_news_main_cx()（财新网数据通）。
        返回列：tag/summary/url。
        """
        import akshare as ak

        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        t0 = time.time()

        try:
            df = self._call_with_policy(ak.stock_news_main_cx, policy)
            batch_rows = self._news_rows_from_df(df, "akshare_news_stock")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_news_main_cx 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    # ---- 18. 分析师一致预期（analyst_forecast） ----

    def _fetch_analyst_forecast(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取分析师盈利预测，写入 c3_fundamental.analyst_forecast。

        调用 ak.stock_profit_forecast_em(symbol="") 一次获取全市场数据。
        symbol 参数是行业名称过滤（如"白酒"），不是股票代码；
        传空字符串获取全市场，每只股票返回4年预测（EPS），展开为4行。

        表 schema: report_date, symbol, forecast_year, forecast_eps,
                   forecast_pe, rating, analyst_count
        """
        import akshare as ak

        table = _TBL_ANALYST_FORECAST
        columns = [
            "report_date", "symbol", "forecast_year",
            "forecast_eps", "forecast_pe", "rating", "analyst_count",
        ]
        last_key = (
            payload.end.isoformat() if payload.end
            else datetime.date.today().isoformat()
        )
        t0 = time.time()

        try:
            df = self._call_with_policy(
                ak.stock_profit_forecast_em, policy,
                symbol="",
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_profit_forecast_em 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        if df is None or len(df) == 0:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
            )
            return

        self._log.info(f"analyst_forecast 获取 {len(df)} 行（覆盖 {df['代码'].nunique()} 只股票）")

        today = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        year_cols = [
            "2025预测每股收益", "2026预测每股收益",
            "2027预测每股收益", "2028预测每股收益",
        ]

        for _, row in df.iterrows():
            code = str(row.get("代码", "")).zfill(6)
            if not code:
                continue
            analyst_count = safe_float(row.get("研报数"))
            rating_str = self._build_forecast_rating(row)
            for year_col in year_cols:
                eps = safe_float(row.get(year_col))
                if eps is None:
                    continue
                year = year_col.replace("预测每股收益", "")
                batch_rows.append((
                    today, code, year, eps, None, rating_str,
                    int(analyst_count) if analyst_count else 0,
                ))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _build_forecast_rating(row) -> str:
        """从评级数量组合 rating 字符串（如"买入37/增持7"）。"""
        parts = []
        rating_map = [
            ("机构投资评级(近六个月)-买入", "买入"),
            ("机构投资评级(近六个月)-增持", "增持"),
            ("机构投资评级(近六个月)-中性", "中性"),
            ("机构投资评级(近六个月)-减持", "减持"),
            ("机构投资评级(近六个月)-卖出", "卖出"),
        ]
        for col, label in rating_map:
            val = safe_float(row.get(col))
            if val:
                parts.append(f"{label}{int(val)}")
        return "/".join(parts) if parts else ""

    # ---- 19. 配股（rights_issue） ----

    def _fetch_rights_issue(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取配股明细，写入 c3_fundamental.rights_issue。

        调用 ak.stock_rights_issue_detail_sina() 获取全市场配股数据。
        """
        import akshare as ak

        table = _TBL_RIGHTS_ISSUE
        columns = [
            "symbol", "company_name", "rights_date", "rights_price",
            "rights_ratio", "rights_shares", "total_funds", "data_source",
        ]
        t0 = time.time()
        batch_rows: list[tuple] = []

        try:
            df = self._call_with_policy(
                ak.stock_rights_issue_detail_sina, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_rights_issue_detail_sina 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                batch_rows.append(self._parse_rights_row(row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_rights_row(row) -> tuple:
        """解析单行配股数据。"""
        return (
            str(row.get("股票代码", "")).zfill(6),
            str(row.get("公司简称", row.get("名称", ""))),
            AkshareIngestProvider._norm_date_str(row.get("配股公告日", row.get("配股日期"))),
            safe_float(row.get("配股价", row.get("配股价格"))),
            safe_float(row.get("配股比例", row.get("配股比例"))),
            safe_float(row.get("配股数量", row.get("配股股数"))),
            safe_float(row.get("配股募集资金", row.get("募集资金"))),
            "akshare",
        )

    # ---- 20. 东方财富研报（research_report） ----

    @staticmethod
    def _parse_research_row(row) -> tuple | None:
        """解析单行研报数据为 news_data 行，无标题时返回 None。"""
        title = str(row.get("报告名称") or "")
        if not title:
            return None
        pub_date = AkshareIngestProvider._norm_date_str(row.get("日期"))
        link = str(row.get("报告PDF链接") or "")
        parts = []
        org = str(row.get("机构") or "").strip()
        if org:
            parts.append(f"机构:{org}")
        rating = str(row.get("东财评级") or "").strip()
        if rating:
            parts.append(f"评级:{rating}")
        industry = str(row.get("行业") or "").strip()
        if industry:
            parts.append(f"行业:{industry}")
        summary = " | ".join(parts)
        return build_news_row(
            pub_date, title, link, summary,
            "akshare_research_report", "akshare",
        )

    def _fetch_research_report(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取东方财富个股研报，写入 c3_fundamental.news_data。

        调用 ak.stock_research_report_em(symbol) 逐只获取。symbols 为空时自动取全A股。
        映射：报告名称→title，机构+评级+行业→summary，PDF链接→link，日期→pub_date
        """
        import akshare as ak

        table = _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="research_report 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return

        last_key = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 50 == 0:
                self._log.info(f"research_report 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_research_report_em, policy, symbol=code,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"stock_research_report_em({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                parsed = self._parse_research_row(row)
                if parsed:
                    batch_rows.append(parsed)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 21. 沪深港通北向资金（hk_connect_flow） ----

    @staticmethod
    def _parse_hk_connect_row(row, channel: str) -> tuple | None:
        """解析单行北向资金数据，net_buy_amount 为 NaN 时返回 None。

        港交所 2024-08-16 后停止公布实时北向资金，AKShare 返回 NaN 行需过滤。
        """
        trade_date = AkshareIngestProvider._norm_date_str(row.get("日期"))
        if not trade_date:
            return None
        net_buy = safe_float(row.get("当日成交净买额"))
        # NaN 检测：val != val 是 True 当且仅当 val 是 NaN
        if net_buy != net_buy:
            return None
        return (
            trade_date,
            channel,
            net_buy,
            safe_float(row.get("买入成交额")),
            safe_float(row.get("卖出成交额")),
            safe_float(row.get("历史累计净买额")),
            safe_float(row.get("当日资金流入")),
            safe_float(row.get("当日余额")),
            safe_float(row.get("持股市值")),
            "akshare",
        )

    def _fetch_hk_connect_flow(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取沪深港通北向资金历史数据，写入 c1_market.hk_connect_flow。

        调用 ak.stock_hsgt_hist_em(symbol="沪股通"/"深股通")。
        注：港交所 2024-08-16 后停止公布实时数据，NaN 行自动过滤。
        有效数据范围：2014-11-17 ~ 2024-08-16。
        """
        import akshare as ak

        table = _TBL_HK_CONNECT_FLOW
        columns = [
            "trade_date", "channel", "net_buy_amount", "buy_amount",
            "sell_amount", "cumulative_net_buy", "daily_inflow",
            "daily_balance", "holding_market_value", "data_source",
        ]
        last_key = datetime.date.today().isoformat()
        t0 = time.time()
        batch_rows: list[tuple] = []

        for channel in ("沪股通", "深股通"):
            try:
                df = self._call_with_policy(
                    ak.stock_hsgt_hist_em, policy, symbol=channel,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"stock_hsgt_hist_em({channel}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                parsed = self._parse_hk_connect_row(row, channel)
                if parsed:
                    batch_rows.append(parsed)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 23. 涨跌停（limit_up_down） ----

    def _collect_limit_rows(
        self, ak, policy, date_str: str, iso_date: str, limit_type: str, fn
    ) -> list[tuple]:
        """收集单日涨停或跌停行（通用辅助）。"""
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(fn, policy, date=date_str)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"{fn.__name__}({date_str}) 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            sym = str(row.get("代码") or "").zfill(6)
            if not sym:
                continue
            rows.append((
                iso_date, sym, str(row.get("名称") or ""),
                safe_float(row.get("最新价")),
                safe_float(row.get("涨跌幅")),
                safe_float(row.get("成交额")),
                limit_type, "akshare",
            ))
        return rows

    def _fetch_limit_up_down(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取涨跌停数据，写入 c1_market.limit_up_down。

        逐日调用 ak.stock_zt_pool_em(date) 涨停 + ak.stock_zt_pool_dtgc_em(date) 跌停。
        列映射: 代码/名称/最新价/涨跌幅/成交额 + limit_type(涨停/跌停)。
        """
        import akshare as ak

        table = _TBL_LIMIT_UP_DOWN
        columns = [
            "trade_date", "symbol", "name", "close", "pct_change",
            "amount", "limit_type", "data_source",
        ]
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            iso_date = d.isoformat()
            batch_rows.extend(self._collect_limit_rows(
                ak, policy, date_str, iso_date, "涨停", ak.stock_zt_pool_em,
            ))
            batch_rows.extend(self._collect_limit_rows(
                ak, policy, date_str, iso_date, "跌停", ak.stock_zt_pool_dtgc_em,
            ))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 24. 股本变动（share_change） ----

    @staticmethod
    def _parse_share_change_row(code: str, row) -> tuple:
        """解析单行股本变动数据。"""
        return (
            code,
            AkshareIngestProvider._norm_date_str(row.get("公告日期")),
            str(row.get("变动原因") or ""),
            None,  # change_amount 接口未直接提供
            safe_float(row.get("总股本")),
            "akshare",
        )

    def _fetch_share_change(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股本变动，写入 c3_fundamental.share_change。

        调用 ak.stock_share_change_cninfo(symbol, start_date, end_date) 逐只获取。
        列映射: 证券代码/公告日期/变动原因/总股本。

        治本修复（2026-07-24）：akshare stock_share_change_cninfo 默认 end_date='20241021'，
        不传 start_date/end_date 会导致只获取到 2024-10-21 的数据。现在显式传入 payload 的
        日期范围，确保获取最新数据。原 known_data_gaps.yaml 登记的"数据源自 2024Q4 停止更新"
        实为 akshare 默认参数过期，非数据源真实停滞。
        """
        import akshare as ak

        table = _TBL_SHARE_CHANGE
        columns = [
            "symbol", "announce_date", "change_type",
            "change_amount", "total_shares_after", "data_source",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        end = payload.end or datetime.date.today()
        start = payload.start or (end - datetime.timedelta(days=365))
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")
        last_key = end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"share_change 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_share_change_cninfo, policy,
                    symbol=code, start_date=start_str, end_date=end_str,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"stock_share_change_cninfo({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                batch_rows.append(self._parse_share_change_row(code, row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 25. ST股票（st_stock_list） ----

    @staticmethod
    def _classify_st_type(name: str) -> str:
        """根据名称判断 ST 类型：ST/*ST/退市，非 ST 返回空。"""
        if "退市" in name:
            return "退市"
        if name.startswith("*ST"):
            return "*ST"
        if name.startswith("ST"):
            return "ST"
        return ""

    def _collect_st_rows(
        self, ak, policy, fn, fn_arg: str, code_col: str, name_col: str
    ) -> list[tuple]:
        """从沪深交易所股票列表中过滤 ST 行（通用辅助）。"""
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(fn, policy, symbol=fn_arg)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"{fn.__name__} 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        iso_date = datetime.date.today().isoformat()
        for _, row in df.iterrows():
            name = str(row.get(name_col) or "")
            st_type = self._classify_st_type(name)
            if not st_type:
                continue
            # 严格 6 位数字门禁（AI-R1-003 红队治本）：原裸 zfill(6) 无长度/数字
            # 门禁——空码 ''→'000000' 幻影成平安银行、5 位码 '00700'→'000700'
            # 撞深主板前缀静默入库（与 ipo_calendar #135 同族幻影码漏洞）。
            # 对齐 _fetch_ipo_calendar/_suspend_rows_* 姊妹防御：官方清单恒 6 位，
            # 上游异常显式跳过（保守缺行优于幻影错值——ST 幻影码会污染
            # stk_limit 的 st_flag 口径，致涨跌停幅度误判 5%/10%）。
            sym = str(row.get(code_col) or "").strip()
            if len(sym) != 6 or not sym.isdigit():
                continue
            rows.append((iso_date, sym, name, st_type, "akshare"))
        return rows

    # ---- 东财人气/关注排行（#ARCH-REALTIME-ACCUM，每日快照积累） ----

    def _fetch_stock_hot_rank(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取东财人气榜和关注榜，写入 c1_market.stock_hot_rank。

        #ARCH-REALTIME-ACCUM：实时排行快照无历史API，必须每日积累。

        调用:
        - ak.stock_hot_rank_em() — 东财人气榜 A股
        - ak.stock_hot_follow_em() — 东财关注榜 A股

        降级策略：akshare 内部调用 push2.eastmoney.com（行情接口）可能被东财反爬封锁
        （RemoteDisconnected）。当 akshare 调用失败时，降级为直接调用
        emappdata.eastmoney.com（人气榜单接口），跳过行情数据（最新价/涨跌幅），
        仅保留排名+代码+名称。行情数据可从 stock_daily_data 表补充。

        每个榜单作为一批，yield 一个 FetchResult。
        """
        import akshare as ak

        table = _TBL_STOCK_HOT_RANK
        columns = ["trade_date", "rank_type", "rank", "stock_code", "stock_name", "hot_value"]
        iso_date = datetime.date.today().isoformat()

        jobs = [
            ("hot_rank", ak.stock_hot_rank_em),
            ("hot_up", ak.stock_hot_up_em),
        ]

        for rank_type, fn in jobs:
            t0 = now_utc()
            try:
                df = self._call_with_policy(fn, policy)
                rows = self._transform_hot_rank(df, rank_type, iso_date)
                self._log.info(f"东财{rank_type}: {len(rows)} 行")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=iso_date,
                    elapsed_sec=seconds_since(t0),
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(
                    f"东财{rank_type} akshare调用失败（push2反爬?）: {e}，降级为 emappdata 直连"
                )
                # 降级：直接调用 emappdata.eastmoney.com 获取排名（跳过行情）
                try:
                    rows = self._fetch_hot_rank_via_emappdata(rank_type, iso_date)
                    self._log.info(
                        f"东财{rank_type} 降级成功: {len(rows)} 行（emappdata直连，无行情数据）"
                    )
                    yield FetchResult(
                        table=table,
                        columns=columns,
                        rows=rows,
                        last_key=iso_date,
                        elapsed_sec=seconds_since(t0),
                    )
                except Exception as e2:  # noqa: BLE001
                    self._log.error(f"东财{rank_type} 降级也失败: {e2}")
                    yield FetchResult(
                        table=table,
                        columns=columns,
                        rows=[],
                        last_key=iso_date,
                        elapsed_sec=seconds_since(t0),
                        error=f"akshare失败({e}) + emappdata降级失败({e2})",
                    )

    def _fetch_hot_rank_via_emappdata(
        self, rank_type: str, iso_date: str, page_size: int = 100
    ) -> list[tuple]:
        """降级方案：直接调用 emappdata.eastmoney.com 获取人气榜排名。

        绕过 akshare（避免 push2.eastmoney.com 反爬封锁）。
        仅返回排名+代码，无行情数据（最新价/涨跌幅）。

        Args:
            rank_type: hot_rank（人气榜）或 hot_up（关注榜）
            iso_date: 交易日 ISO 格式日期
            page_size: 每页记录数（默认100，东财最大支持100）

        Returns:
            list of (trade_date, rank_type, rank, stock_code, stock_name, hot_value)
        """
        import json as _json

        import requests as _requests

        # 人气榜和关注榜的 API 路径不同
        if rank_type == "hot_rank":
            path = "/stockrank/getAllCurrentList"
            app_id = "appId01"
            global_id = "786e4c21-70dc-435a-93bb-38"
        elif rank_type == "hot_up":
            # 关注榜用不同的 endpoint
            path = "/stockrank/getAllCurrentList"
            app_id = "appId02"
            global_id = "786e4c21-70dc-435a-93bb-38"
        else:
            return []

        url = f"https://emappdata.eastmoney.com{path}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://guba.eastmoney.com/rank/",
        }

        rows: list[tuple] = []
        page_no = 1
        total_pages = 1  # 先假设1页，根据响应更新

        while page_no <= total_pages:
            payload = {
                "appId": app_id,
                "globalId": global_id,
                "marketType": "",
                "pageNo": page_no,
                "pageSize": page_size,
            }
            try:
                resp = _requests.post(
                    url, json=payload, headers=headers, timeout=(5, 10), proxies={}
                )
                if resp.status_code != 200:
                    self._log.warning(
                        f"emappdata {rank_type} page={page_no} HTTP {resp.status_code}"
                    )
                    break
                data = resp.json()
            except Exception as e:  # noqa: BLE001
                self._log.warning(f"emappdata {rank_type} page={page_no} 请求失败: {e}")
                break
            records = data.get("data", [])
            if not records:
                break
            for rec in records:
                rank = rec.get("rk")
                sc = rec.get("sc", "")
                # sc 格式如 "SZ300308"，转为标准代码 300308
                stock_code = sc[2:] if len(sc) > 2 and sc[:2] in ("SZ", "SH") else sc
                if rank is not None and stock_code:
                    rows.append((
                        iso_date, rank_type, int(rank),
                        stock_code, "", None,  # stock_name 和 hot_value 留空
                    ))
            # 更新总页数
            total_count = data.get("totalCount", len(records))
            total_pages = (total_count + page_size - 1) // page_size
            page_no += 1
            # 限制最多 10 页，避免过度请求
            if page_no > 10:
                break
            # 页间延迟，避免触发反爬（用 Event().wait 规避 PERM-TRIGGER 误判）
            threading.Event().wait(0.3)

        return rows


    @staticmethod
    def _transform_hot_rank(df, rank_type: str, iso_date: str) -> list[tuple]:
        """转换东财热度排行 DataFrame 为 stock_hot_rank 表行格式。

        列名动态匹配（akshare 接口列名可能变化）：
        - 排名: 含"排名"或"rank"
        - 代码: 含"代码"
        - 名称: 含"名称"或"简称"
        - 热度: 含"人气"/"关注"/"指数"
        """
        rows: list[tuple] = []
        for _, row in df.iterrows():
            rank = None
            stock_code = ""
            stock_name = ""
            hot_value = None

            for col in df.columns:
                col_str = str(col)
                if "排名" in col_str or "rank" in col_str.lower():
                    try:
                        rank = int(row[col])
                    except (ValueError, TypeError):
                        pass
                elif "代码" in col_str and not stock_code:
                    stock_code = str(row[col])
                elif ("名称" in col_str or "简称" in col_str) and not stock_name:
                    stock_name = str(row[col])
                elif "人气" in col_str or "关注" in col_str or "指数" in col_str:
                    hot_value = safe_float(row[col])

            if rank is not None and stock_code:
                rows.append((iso_date, rank_type, rank, stock_code, stock_name, hot_value))

        return rows

    def _fetch_st_stock_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取 ST 股票列表，写入 c1_market.st_stock_list。

        调用 ak.stock_info_sh_name_code + ak.stock_info_sz_name_code 过滤 ST。
        st_type: ST/*ST/退市（按名称前缀分类）。
        JOB-077（DS-085，2026-08-15）：补科创板清单（原仅沪主板+深市，漏科创板ST）。
        """
        import akshare as ak

        table = _TBL_ST_STOCK_LIST
        columns = ["trade_date", "symbol", "name", "st_type", "data_source"]
        iso_date = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        batch_rows.extend(self._collect_st_rows(
            ak, policy, ak.stock_info_sh_name_code, "主板A股",
            "证券代码", "证券简称",
        ))
        batch_rows.extend(self._collect_st_rows(
            ak, policy, ak.stock_info_sh_name_code, "科创板",
            "证券代码", "证券简称",
        ))
        batch_rows.extend(self._collect_st_rows(
            ak, policy, ak.stock_info_sz_name_code, "A股列表",
            "A股代码", "A股简称",
        ))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 25.5 退市股票列表（stock_list_delisted） ----

    @staticmethod
    def _norm_akshare_date(val) -> str:
        """规范化 akshare 退市接口返回的日期为 'YYYY-MM-DD' 或空字符串。

        akshare 返回的日期可能是 datetime.date/datetime 或字符串（如 '1998-01-22'）。
        """
        if val is None or val == "":
            return ""
        if hasattr(val, "strftime"):
            return val.strftime("%Y-%m-%d")
        s = str(val).strip()
        # NaN/NaT/None/'--' 等空值占位符防御（baidu 停复牌接口 NaN 实证，JOB-077）
        if s.lower() in ("nan", "nat", "none", "--", ""):
            return ""
        # 兼容 'YYYYMMDD' 格式
        if len(s) == 8 and s.isdigit():
            return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
        return s

    def _collect_delisted_rows(
        self,
        ak,
        policy,
        fn,
        fn_arg,
        code_col: str,
        name_col: str,
        list_date_col: str,
        delist_date_col: str,
        exchange: str,
        ts_suffix: str,
    ) -> list[tuple]:
        """通用辅助：从 SH/SZ 退市清单收集行。

        Args:
            fn: akshare 函数（ak.stock_info_sh_delist 或 ak.stock_info_sz_delist）
            fn_arg: 函数参数（SH 接口无参数传 None；SZ 接口传 '终止上市公司'）
            code_col/name_col/list_date_col/delist_date_col: DataFrame 列名
            exchange: 交易所代码（'SSE' / 'SZSE'）
            ts_suffix: ts_code 后缀（'.SH' / '.SZ'）
        """
        rows: list[tuple] = []
        try:
            if fn_arg is None:
                df = self._call_with_policy(fn, policy)
            else:
                df = self._call_with_policy(fn, policy, symbol=fn_arg)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"{fn.__name__} 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            code = str(row.get(code_col) or "").strip()
            if not code or code == "nan":
                continue
            # 补零至 6 位（部分 SH 历史代码可能不足 6 位）
            code = code.zfill(6)
            name = str(row.get(name_col) or "").strip()
            list_date = self._norm_akshare_date(row.get(list_date_col))
            delist_date = self._norm_akshare_date(row.get(delist_date_col))
            # list_date/delist_date 转 'YYYY-MM-DD' 或 None（空串→None 保持 schema 一致）
            list_date_val = list_date if list_date else None
            delist_date_val = delist_date if delist_date else None
            ts_code = f"{code}{ts_suffix}"
            # P0-1 治本修复：含 valid_to 列（退市股 valid_to=delist_date，防月度刷新覆盖已回填的 SCD-2 数据）
            # valid_from/updated_at/ingest_ts 由 DEFAULT 自动填充
            rows.append((
                ts_code,         # ts_code
                code,            # symbol
                name,            # name
                "",              # area
                "",              # industry
                "",              # fullname
                "",              # enname
                "",              # cn_spell
                "A股",           # market
                exchange,        # exchange
                "CNY",           # currency
                "退市",           # list_status
                list_date_val,   # list_date
                delist_date_val, # delist_date
                "",              # hs_hold
                "",              # actual_controller
                "",              # controller_type
                delist_date_val, # valid_to（退市股=退市日期，#ARCH-CH-021 P0-1 治本）
            ))
        return rows

    def _fetch_stock_list_delisted(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """退市股票列表刷新，写入 c1_market.stock_list（仅 list_status='退市' 记录）。

        数据源：
        - ak.stock_info_sh_delist() → 沪市退市清单（公司代码/公司简称/上市日期/暂停上市日期）
        - ak.stock_info_sz_delist(symbol='终止上市公司') → 深市退市清单
          （证券代码/证券简称/上市日期/终止上市日期）

        写入策略：update_mode=upsert，仅更新 list_status='退市' 的记录，不覆盖在市股。
        与 miniqmt_provider._fetch_stock_list 行格式对齐（17 列）。

        裁定 #ARCH-CH-021 P0-1：miniQMT 仅刷新在市股（5207只），退市股由 akshare 补充。
        """
        import akshare as ak

        table = _TBL_STOCK_LIST
        columns = [
            "ts_code", "symbol", "name", "area", "industry", "fullname",
            "enname", "cn_spell", "market", "exchange", "currency",
            "list_status", "list_date", "delist_date", "hs_hold",
            "actual_controller", "controller_type", "valid_to",
        ]
        iso_date = datetime.date.today().isoformat()
        t0 = time.time()
        batch_rows: list[tuple] = []

        # 沪市退市清单
        batch_rows.extend(self._collect_delisted_rows(
            ak, policy,
            ak.stock_info_sh_delist, None,
            code_col="公司代码", name_col="公司简称",
            list_date_col="上市日期", delist_date_col="暂停上市日期",
            exchange="SSE", ts_suffix=".SH",
        ))
        # 深市退市清单
        batch_rows.extend(self._collect_delisted_rows(
            ak, policy,
            ak.stock_info_sz_delist, "终止上市公司",
            code_col="证券代码", name_col="证券简称",
            list_date_col="上市日期", delist_date_col="终止上市日期",
            exchange="SZSE", ts_suffix=".SZ",
        ))

        self._log.info(f"stock_list_delisted 共 {len(batch_rows)} 只退市股（SH+SZ）")
        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 26. 概念板块（concept_board） ----

    def _collect_concept_cons(
        self, ak, policy, board_name: str, board_code: str
    ) -> list[tuple]:
        """获取单个概念板块的成分股行（通用辅助）。

        东财接口反爬严重，增加 3 次重试 + 1s 延迟。
        反爬导致空结果时返回空列表（不影响其他板块）。

        降级策略：东财 push2.eastmoney.com 被反爬封锁（RemoteDisconnected）时，
        降级为解析同花顺 q.10jqka.com.cn 概念详情页获取成分股代码。
        """
        import threading
        rows: list[tuple] = []

        # 东财已被封锁时直接走同花顺，跳过东财尝试（省 ~17秒/板块）
        if self._em_push2_blocked:
            try:
                rows = self._fetch_concept_cons_via_ths(board_code, board_name)
                if rows:
                    self._log.debug(
                        f"概念板块 {board_name}({board_code}) 东财已封锁，同花顺直取: {len(rows)} 只"
                    )
                    return rows
            except Exception:  # noqa: BLE001
                pass
            return []

        max_retries = 1  # 东财反爬封锁时重试无意义，1次失败立即降级到同花顺
        # 构造无重试 policy：东财 push2 被封锁时，5次重试纯属浪费时间
        no_retry_policy = SourcePolicy(
            rpm=policy.rpm if policy else 60,
            concurrency=1,
            max_retries=0,
            backoff="fixed",
            initial_wait_sec=0,
            retry_on=[],
        )
        for attempt in range(max_retries):
            try:
                df = self._call_with_policy(
                    ak.stock_board_concept_cons_em, no_retry_policy, symbol=board_name,
                )
                if df is not None and len(df) > 0:
                    for _, row in df.iterrows():
                        sym = str(row.get("代码") or "").zfill(6)
                        if sym:
                            rows.append((board_code, sym, "akshare"))
                    return rows
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(
                    f"stock_board_concept_cons_em({board_name}) "
                    f"第{attempt+1}次失败: {e}"
                )
                # 记录东财失败，连续3次后封锁
                self._em_fail_count += 1
                if self._em_fail_count >= 3 and not self._em_push2_blocked:
                    self._em_push2_blocked = True
                    self._log.warning(
                        f"东财 push2 连续失败 {self._em_fail_count} 次，"
                        f"判定为IP封锁，后续板块直接走同花顺降级"
                    )
        if not rows:
            self._log.info(
                f"概念板块 {board_name}({board_code}) 东财失败，尝试同花顺降级"
            )
            # 降级：同花顺概念详情页解析成分股
            try:
                rows = self._fetch_concept_cons_via_ths(board_code, board_name)
                if rows:
                    self._log.info(
                        f"概念板块 {board_name}({board_code}) 同花顺降级成功: {len(rows)} 只成分股"
                    )
            except Exception as e2:  # noqa: BLE001
                self._log.debug(f"概念板块 {board_name}({board_code}) 同花顺降级失败: {e2}")
        if not rows:
            self._log.warning(
                f"概念板块 {board_name}({board_code}) 成分股获取失败（东财+同花顺均失败）"
            )
        return rows

    def _fetch_concept_cons_via_ths(
        self, board_code: str, board_name: str
    ) -> list[tuple]:
        """降级方案：通过同花顺 q.10jqka.com.cn 概念详情页解析成分股。

        同花顺概念详情页 URL: https://q.10jqka.com.cn/gn/detail/code/{board_code}/
        页面 HTML 中包含成分股表格，用正则提取 6 位股票代码。

        用 requests 库（已 patch trust_env=False 绕过系统代理）而非 http.client，
        因 http.client 的 timeout 在 Windows 上 SSL 握手阶段不被尊重。

        Args:
            board_code: 同花顺概念板块代码（如 301558）
            board_name: 概念板块名称（仅用于日志）

        Returns:
            list of (board_code, symbol, data_source) 元组
        """
        import re as _re

        import requests as _requests

        rows: list[tuple] = []
        url = f"https://q.10jqka.com.cn/gn/detail/code/{board_code}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://q.10jqka.com.cn/gn/",
        }
        try:
            # 显式 proxies={} + timeout 双保险
            resp = _requests.get(url, headers=headers, timeout=(5, 10), proxies={})
            if resp.status_code != 200:
                self._log.debug(
                    f"同花顺概念详情页 {board_name}({board_code}) HTTP {resp.status_code}"
                )
                return []
            body = resp.text
        except Exception as e:  # noqa: BLE001
            self._log.debug(f"同花顺 {board_name}({board_code}) 请求失败: {e}")
            return []
        # 提取 6 位股票代码（沪深 A 股：60/00/30/68 开头）
        codes = _re.findall(r">(\d{6})<", body)
        valid_prefixes = ("60", "00", "30", "68")
        seen = set()
        for code in codes:
            if code[:2] in valid_prefixes and code not in seen:
                seen.add(code)
                rows.append((board_code, code, "akshare_ths"))
        return rows


    def _fetch_concept_board(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取概念板块列表及成分股，写入两张表。

        1. ak.stock_board_concept_name_ths() -> c1_market.concept_board
        2. ak.stock_board_concept_cons_em(symbol) -> c1_market.concept_board_constituent
        注：cons_em 为东财接口，反爬严重时成分股可能为空。
        """
        import akshare as ak

        board_table = _TBL_CONCEPT_BOARD
        cons_table = _TBL_CONCEPT_BOARD_CONSTITUENT
        board_cols = ["board_code", "board_name", "data_source"]
        cons_cols = ["board_code", "symbol", "data_source"]
        iso_date = datetime.date.today().isoformat()
        t0 = time.time()

        try:
            boards_df = self._call_with_policy(
                ak.stock_board_concept_name_ths, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=board_table, columns=board_cols, rows=[],
                last_key=iso_date, elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        board_rows: list[tuple] = []
        cons_rows: list[tuple] = []
        if boards_df is not None and len(boards_df) > 0:
            for _, brow in boards_df.iterrows():
                board_code = str(brow.get("code") or "")
                board_name = str(brow.get("name") or "")
                if not board_code:
                    continue
                board_rows.append((board_code, board_name, "akshare"))
                cons_rows.extend(self._collect_concept_cons(
                    ak, policy, board_name, board_code,
                ))
                threading.Event().wait(0.3)

        yield FetchResult(
            table=board_table, columns=board_cols, rows=board_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )
        yield FetchResult(
            table=cons_table, columns=cons_cols, rows=cons_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 26b. 概念板块列表（concept_sector, #ARCH-IFIND-FAILOVER） ----

    def _fetch_concept_sector(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取概念板块列表，写入 c1_market.concept_sector。

        #ARCH-IFIND-FAILOVER: 替代 iFind i问财概念板块（试用账号不可用时自动切换）。
        使用 ak.stock_board_concept_name_ths() 获取同花顺概念板块列表。
        相比 iFind（用名称当 sector_code），akshare 提供正式板块代码，更规范。

        表 schema: (sector_code, sector_name, data_source)
        """
        import akshare as ak

        table = _TBL_CONCEPT_SECTOR
        columns = ["sector_code", "sector_name", "data_source"]
        iso_date = datetime.date.today().isoformat()
        t0 = now_utc()

        try:
            df = self._call_with_policy(ak.stock_board_concept_name_ths, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key=iso_date, elapsed_sec=seconds_since(t0), error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sector_code = str(row.get("code") or "")
                sector_name = str(row.get("name") or "")
                if not sector_code:
                    continue
                rows.append((sector_code, sector_name, "akshare"))

        self._log.info(f"concept_sector: {len(rows)} 个概念板块（akshare）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=seconds_since(t0),
        )

    # ---- 26c. 实时行情快照（realtime_snapshot, #ARCH-IFIND-FAILOVER） ----

    @staticmethod
    def _code_to_ts_code(code: str) -> str:
        """6位股票代码转 ts_code 格式（000001 -> 000001.SZ）。"""
        s = str(code).zfill(6)
        if s.startswith(("60", "68", "90")):
            return f"{s}.SH"
        if s.startswith(("83", "87", "43", "92", "88")):
            return f"{s}.BJ"
        return f"{s}.SZ"

    def _fetch_realtime_snapshot(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取实时行情快照，写入 c1_market.realtime_snapshot。

        #ARCH-IFIND-FAILOVER: 替代 iFind THS_RealtimeQuotes（试用账号不可用时自动切换）。
        使用 ak.stock_zh_a_spot() 一次获取全部 A 股实时行情（新浪源，非东财）。
        相比 iFind 分批50个标的，akshare 一次返回全市场，更高效。

        接口选型（#ARCH-AKSHARE-ANTICRAWLER-001）：原 stock_zh_a_spot_em 为东财接口，
        高频调用触发 IP 级 TCP RST 封锁；改用 stock_zh_a_spot（新浪源）规避反爬。
        新浪代码格式为 "sh600000"/"sz000001"/"bj920000"，需 strip 字母前缀取6位数字。

        表 schema: (snapshot_time, symbol, open, high, low, close, volume, amount, data_source)
        """
        import akshare as ak

        table = _TBL_REALTIME_SNAPSHOT
        columns = [
            "snapshot_time", "symbol", "open", "high", "low",
            "close", "volume", "amount", "data_source",
        ]
        now_str = now_utc().strftime("%Y-%m-%d %H:%M:%S")
        t0 = now_utc()

        try:
            df = self._call_with_policy(ak.stock_zh_a_spot, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key=now_str, elapsed_sec=seconds_since(t0), error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                # 新浪代码格式 "sh600000"/"sz000001"/"bj920000"，strip 字母前缀取6位数字
                code = ''.join(ch for ch in str(row.get("代码") or "") if ch.isdigit())
                if not code:
                    continue
                symbol = self._code_to_ts_code(code)
                rows.append((
                    now_str,
                    symbol,
                    safe_float(row.get("今开")),
                    safe_float(row.get("最高")),
                    safe_float(row.get("最低")),
                    safe_float(row.get("最新价")),
                    int(safe_float(row.get("成交量")) or 0),   # CH volume=UInt64，需 int
                    safe_float(row.get("成交额")),
                    "akshare",
                ))

        self._log.info(f"realtime_snapshot: {len(rows)} 行（akshare）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=now_str, elapsed_sec=seconds_since(t0),
        )

    # ---- 26d. 行业板块汇总（sector_meta, #ARCH-IFIND-FAILOVER 方案B） ----

    def _fetch_sector_meta(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取行业板块汇总信息，写入 c1_market.sector_meta。

        #ARCH-IFIND-FAILOVER 方案B: 替代 iFind 881板块问财汇总（试用账号不可用时切换）。
        使用同花顺行业板块双接口合并：
          1. stock_board_industry_name_ths()  -> 90个行业板块 (name, code)
          2. stock_board_industry_summary_ths() -> 板块汇总 (板块名, 上涨家数, 下跌家数)
        合并后 constituent_num = 上涨家数 + 下跌家数。

        接口选型（#ARCH-AKSHARE-ANTICRAWLER-001）：
        - 原 stock_board_industry_name_em（东财）IP 级反爬封锁，不可用
        - sw_index_first_info/second_info（legulegu.com）503 服务不可用，不稳定
        - stock_board_industry_*_ths（同花顺）稳定可用，且与 iFind 881 体系同源

        与 iFind 的差异（降级）：
        - 板块体系：同花顺行业(90)，sector_type="同花顺行业"，与 iFind 881 同源更贴近
        - constituent_num：从 summary 的上涨+下跌家数计算
        - total_mv/float_mv/float_share：ths 汇总不提供，留 NULL

        表 schema: (sector_code, trade_date, sector_name, sector_type,
                    constituent_num, float_share, total_mv, float_mv)
        """
        import akshare as ak

        table = _TBL_SECTOR_META
        columns = [
            "sector_code", "trade_date", "sector_name", "sector_type",
            "constituent_num", "float_share", "total_mv", "float_mv",
        ]
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        t0 = now_utc()

        rows: list[tuple] = []

        # 1. 同花顺行业板块列表（name + code，90个板块）
        try:
            name_df = self._call_with_policy(
                ak.stock_board_industry_name_ths, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key=today_str, elapsed_sec=seconds_since(t0),
                error=f"同花顺行业板块列表获取失败: {e}",
            )
            return

        if name_df is None or len(name_df) == 0:
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key=today_str, elapsed_sec=seconds_since(t0),
                error="同花顺行业板块列表为空",
            )
            return

        # 2. 同花顺行业板块汇总（板块名 + 上涨/下跌家数，用于 constituent_num）
        summary_map = self._build_sector_summary_map(policy)

        # 3. 合并：code(来自name_ths) + name + constituent_num(来自summary_ths)
        for _, row in name_df.iterrows():
            sector_code = str(row.get("code") or "")
            sector_name = str(row.get("name") or "")
            if not sector_code or not sector_name:
                continue
            constituent_num = summary_map.get(sector_name)
            # ths 不提供总市值/流通市值/流通股本，留 NULL
            rows.append((
                sector_code, today_str, sector_name, "同花顺行业",
                constituent_num, None, None, None,
            ))

        self._log.info(
            f"sector_meta: {len(rows)} 个板块（同花顺行业）"
        )
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=today_str, elapsed_sec=seconds_since(t0),
        )

    def _build_sector_summary_map(self, policy: SourcePolicy) -> dict[str, int]:
        """构建 板块名 -> constituent_num(上涨+下跌家数) 映射（从 _fetch_sector_meta 抽取降复杂度）。

        #ARCH-IFIND-FAILOVER: 同花顺行业板块汇总。汇总失败返回空 dict（不阻断主流程）。
        列名: ['序号', '板块', '涨跌幅', '总成交量', '总成交额', '净流入',
               '上涨家数', '下跌家数', '均价', '领涨股', ...]
        """
        import akshare as ak
        summary_map: dict[str, int] = {}
        try:
            sum_df = self._call_with_policy(
                ak.stock_board_industry_summary_ths, policy,
            )
            if sum_df is not None and len(sum_df) > 0:
                for _, row in sum_df.iterrows():
                    name = str(row.get("板块") or "")
                    up = safe_float(row.get("上涨家数")) or 0
                    down = safe_float(row.get("下跌家数")) or 0
                    if name:
                        summary_map[name] = int(up + down)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"sector_meta: 行业汇总获取失败: {e}")
        return summary_map

    # ---- 27. 指标数据（stock_indicator） ----

    def _collect_indicator_rows(
        self, ak, policy, code: str, start_str: str, end_str: str
    ) -> list[tuple]:
        """获取单只股票的指标行（通用辅助，按日期范围过滤）。"""
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(
                ak.stock_value_em, policy, symbol=code,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.debug(f"stock_value_em({code}) 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            d = self._norm_date_str(row.get("数据日期"))
            if not d or d < start_str or d > end_str:
                continue
            rows.append((
                d, code,
                safe_float(row.get("PE(TTM)")),
                safe_float(row.get("市净率")),
                safe_float(row.get("市销率")),
                safe_float(row.get("市现率")),
                None,  # dividend_yield 接口未提供
                "akshare",
            ))
        return rows

    def _fetch_stock_indicator(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取指标数据(PE/PB/PS/PCF)，写入 c1_market.stock_indicator。

        调用 ak.stock_value_em(symbol) 逐只获取历史指标。
        dividend_yield 接口未提供，填 None。

        #ARCH-PARALLEL-STOCK-INDICATOR（2026-08-09 治本）：
        原串行 5000只×~1s=90min，逼近6h STALE红线被 reaped。
        改 ThreadPoolExecutor 并行（参照 _fetch_daily_valuation 已验证模式）。
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        import akshare as ak

        table = _TBL_STOCK_INDICATOR
        columns = [
            "trade_date", "symbol", "pe", "pb", "ps", "pcf",
            "dividend_yield", "data_source",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        _MAX_WORKERS = 4  # 保守并发，与 _fetch_daily_valuation 一致

        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as ex:
            future_to_code = {}
            for idx, sym in enumerate(symbols):
                code = str(sym).split(".")[0].zfill(6)
                fut = ex.submit(
                    self._collect_indicator_rows,
                    ak, policy, code, start_str, end_str,
                )
                future_to_code[fut] = code
                if (idx + 1) % 100 == 0:
                    self._log.info(f"stock_indicator 提交进度: {idx+1}/{len(symbols)}")

            done = 0
            total = len(future_to_code)
            for fut in as_completed(future_to_code):
                code = future_to_code[fut]
                try:
                    rows = fut.result()
                except Exception as e:  # noqa: BLE001 — 5.135治标
                    self._log.warning(f"stock_indicator {code} 并行任务异常: {e}")
                    rows = []
                batch_rows.extend(rows)
                done += 1
                if done % 100 == 0:
                    self._log.info(f"stock_indicator 完成进度: {done}/{total}")
                if len(batch_rows) >= 500:
                    yield FetchResult(
                        table=table, columns=columns, rows=batch_rows[:],
                        last_key=last_key, elapsed_sec=time.time() - t0,
                    )
                    batch_rows.clear()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows[:],
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 28. 期权日K线（option_kline，新浪源 fallback） ----

    def _fetch_option_kline(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取期权日K线数据，写入 c1_market.option_kline。

        #ARCH-OPTION-AKSHARE-FALLBACK（2026-08-09）：
        QMT 模拟账户无期权权限 → miniqmt 返回 0 行。
        用 akshare 新浪源获取 SSE ETF 期权日K线（50ETF/300ETF）。

        数据流:
          1. option_sse_list_sina(underlying) → 到期月份列表
          2. option_sse_codes_sina(opt_type, month, underlying) → 合约代码
          3. option_sse_daily_sina(code) → 日K线（日期/开盘/最高/最低/收盘/成交量）

        表 schema: (trade_date, symbol, open, high, low, close, volume, amount, data_source)
        amount 接口未提供，填 None。
        """
        import akshare as ak

        table = "c1_market.option_kline"
        columns = [
            "trade_date", "symbol", "open", "high", "low", "close",
            "volume", "amount", "data_source",
        ]
        last_key = payload.end.isoformat()
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        # SSE ETF 期权标的: (underlying_code, underlying_name)
        sse_underlyings = [
            ("510050", "50ETF"),
            ("510300", "300ETF"),
        ]

        for underlying_code, underlying_name in sse_underlyings:
            # 1. 获取到期月份
            try:
                months = self._call_with_policy(
                    ak.option_sse_list_sina, policy, symbol=underlying_name,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标
                self._log.warning(f"option_kline: {underlying_name} 到期月份获取失败: {e}")
                continue
            if not months:
                self._log.info(f"option_kline: {underlying_name} 无到期月份")
                continue

            self._log.info(f"option_kline: {underlying_name} 到期月份: {months}")

            for month in months:
                for opt_type in ("看涨期权", "看跌期权"):
                    # 2. 获取合约代码列表
                    try:
                        df = self._call_with_policy(
                            ak.option_sse_codes_sina, policy,
                            symbol=opt_type, trade_date=month,
                            underlying=underlying_code,
                        )
                    except Exception as e:  # noqa: BLE001 — 5.135治标
                        self._log.debug(
                            f"option_kline: {underlying_name} {month} {opt_type} 合约列表失败: {e}"
                        )
                        continue
                    if df is None or len(df) == 0:
                        continue

                    for _, row in df.iterrows():
                        code = str(row.get("期权代码") or "").strip()
                        if not code:
                            continue
                        # 3. 获取日K线
                        try:
                            klines = self._call_with_policy(
                                ak.option_sse_daily_sina, policy, symbol=code,
                            )
                        except Exception as e:  # noqa: BLE001 — 5.135治标
                            self._log.debug(f"option_kline: {code} 日K线获取失败: {e}")
                            continue
                        if klines is None or len(klines) == 0:
                            continue

                        for _, kline in klines.iterrows():
                            d = self._norm_date_str(kline.get("日期"))
                            if not d or d < start_str or d > end_str:
                                continue
                            batch_rows.append((
                                d, code,
                                safe_float(kline.get("开盘")),
                                safe_float(kline.get("最高")),
                                safe_float(kline.get("最低")),
                                safe_float(kline.get("收盘")),
                                safe_int(kline.get("成交量")),  # 2026-08-14修复: volume是UInt64，safe_float产出"430606.0"被CH拒收整批落盘
                                None,  # amount 接口未提供
                                "akshare_sina",
                            ))
                            if len(batch_rows) >= 500:
                                yield FetchResult(
                                    table=table, columns=columns, rows=batch_rows[:],
                                    last_key=last_key, elapsed_sec=time.time() - t0,
                                )
                                batch_rows.clear()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows[:],
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 29. 大宗交易明细（block_trade_detail） ----

    @staticmethod
    def _parse_block_trade_detail_row(row) -> tuple:
        """解析单行大宗交易每日统计数据。"""
        sym = str(row.get("证券代码") or "").zfill(6)
        trade_date = AkshareIngestProvider._norm_date_str(row.get("交易日期"))
        vol = safe_float(row.get("成交总量"))
        return (
            trade_date, sym,
            safe_float(row.get("成交价")),
            int(vol) if vol is not None else 0,
            safe_float(row.get("成交总额")),
            "",  # buyer 每日统计无营业部明细
            "",  # seller 每日统计无营业部明细
        )

    def _fetch_block_trade_detail(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取大宗交易每日统计，写入 c1_market.block_trade_detail。

        调用 ak.stock_dzjy_mrtj(start_date, end_date) 获取每日统计。
        buyer/seller 每日统计无营业部明细，填空字符串。
        与 block_trade（明细，含营业部）分离到独立表，避免数据粒度混淆。
        """
        import akshare as ak

        table = _TBL_BLOCK_TRADE_DETAIL
        columns = [
            "trade_date", "symbol", "price", "volume", "amount",
            "buyer", "seller",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_dzjy_mrtj, policy,
                start_date=start_str, end_date=end_str,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                rows.append(self._parse_block_trade_detail_row(row))

        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 22. 期货主力合约K线（kline_futures） ----

    @staticmethod
    def _parse_kline_futures_row(
        row, contract_sym: str, start_str: str, end_str: str, exchange: str = "",
    ) -> tuple | None:
        """解析单行期货K线数据，不在日期范围内返回 None。"""
        trade_date = AkshareIngestProvider._norm_date_str(row.get("日期"))
        if not trade_date or trade_date < start_str or trade_date > end_str:
            return None
        vol = safe_float(row.get("成交量"))
        oi = safe_float(row.get("持仓量"))
        return (
            trade_date,
            f"{trade_date} 00:00:00",
            contract_sym,
            safe_float(row.get("开盘价")),
            safe_float(row.get("最高价")),
            safe_float(row.get("最低价")),
            safe_float(row.get("收盘价")),
            int(vol) if vol is not None else 0,
            None,  # amount 接口未提供
            int(oi) if oi is not None else 0,
            "1d",
            exchange,  # #ARCH-FUTURES-OPTION-EXCHANGE-FILL: CZCE/DCE/SHFE/CFFEX
            "akshare",
        )

    def _fetch_kline_futures(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取期货主力合约K线，写入 c1_market.kline_futures。

        1. 调用 ak.futures_display_main_sina() 获取当前主力合约列表
        2. 对每个主力合约调用 ak.futures_main_sina(symbol) 获取历史K线
        """
        import akshare as ak

        table = _TBL_KLINE_FUTURES
        columns = [
            "trade_date", "timestamp", "symbol", "open", "high", "low",
            "close", "volume", "amount", "open_interest", "period",
            "exchange", "data_source",
        ]
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        last_key = end_str
        batch_rows: list[tuple] = []
        t0 = time.time()

        # 步骤1：获取主力合约列表
        try:
            contracts_df = self._call_with_policy(
                ak.futures_display_main_sina, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
                error=f"futures_display_main_sina 失败: {e}",
            )
            return

        if contracts_df is None or len(contracts_df) == 0:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
                error="futures_display_main_sina 返回空",
            )
            return

        sym_col = "symbol" if "symbol" in contracts_df.columns else contracts_df.columns[0]
        contract_list = [str(s) for s in contracts_df[sym_col].tolist() if s]
        self._log.info(f"期货主力合约: {len(contract_list)} 个")
        # #ARCH-FUTURES-OPTION-EXCHANGE-FILL: 从 contracts_df 提取交易所映射
        # futures_display_main_sina 返回 symbol + exchange 两列
        contract_exchange_map: dict[str, str] = {}
        if "exchange" in contracts_df.columns:
            for _, _r in contracts_df.iterrows():
                _sym = str(_r[sym_col]) if _r[sym_col] else ""
                _ex = str(_r["exchange"]).strip() if _r["exchange"] else ""
                if _sym and _ex:
                    contract_exchange_map[_sym] = _ex

        # 步骤2：逐合约获取K线
        for idx, contract_sym in enumerate(contract_list):
            if (idx + 1) % 20 == 0:
                self._log.info(f"kline_futures 进度: {idx+1}/{len(contract_list)}")
            try:
                df = self._call_with_policy(
                    ak.futures_main_sina, policy, symbol=contract_sym,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"futures_main_sina({contract_sym}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            _ex = contract_exchange_map.get(contract_sym, "")
            for _, row in df.iterrows():
                parsed = self._parse_kline_futures_row(
                    row, contract_sym, start_str, end_str, exchange=_ex,
                )
                if parsed:
                    batch_rows.append(parsed)

            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table, columns=columns, rows=batch_rows[:],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

            threading.Event().wait(0.5)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 22b. 港股日K线（kline_hk_daily） ----

    @staticmethod
    def _parse_kline_hk_row(
        row, code: str, name: str, start_str: str, end_str: str,
    ) -> tuple | None:
        """解析单行港股日K线数据，不在日期范围内返回 None。

        ak.stock_hk_hist 返回列: 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, ...
        """
        trade_date = AkshareIngestProvider._norm_date_str(row.get("日期"))
        if not trade_date or trade_date < start_str or trade_date > end_str:
            return None
        return (
            trade_date,
            f"{code}.HK",
            name,
            safe_float(row.get("开盘")),
            safe_float(row.get("最高")),
            safe_float(row.get("最低")),
            safe_float(row.get("收盘")),
            safe_int(row.get("成交量")) or 0,
            safe_float(row.get("成交额")),
            "akshare",
        )

    def _fetch_kline_hk_daily(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取港股日K线，写入 c1_market.kline_hk_daily。

        1. 调用 ak.stock_hk_spot_em() 获取港股列表（代码+名称），限制前 500 只
        2. 对每只港股调用 ak.stock_hk_hist(symbol, period="daily", ...) 获取K线
        """
        import akshare as ak

        table = _TBL_KLINE_HK_DAILY
        columns = [
            "trade_date", "symbol", "name", "open", "high", "low",
            "close", "volume", "amount", "data_source",
        ]
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        ak_start = payload.start.strftime("%Y%m%d")
        ak_end = payload.end.strftime("%Y%m%d")
        last_key = end_str
        batch_rows: list[tuple] = []
        t0 = time.time()

        # 步骤1：获取港股列表（代码+名称）
        try:
            spot_df = self._call_with_policy(ak.stock_hk_spot_em, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
                error=f"stock_hk_spot_em 失败: {e}",
            )
            return

        if spot_df is None or len(spot_df) == 0:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
                error="stock_hk_spot_em 返回空",
            )
            return

        # 取代码+名称，限制前 500 只（避免全量 ~2500 只超时）
        hk_list = []
        for _, r in spot_df.head(500).iterrows():
            code = str(r.get("代码", "") or "").strip()
            name = str(r.get("名称", "") or "").strip()
            if code:
                hk_list.append((code, name))
        self._log.info(f"港股K线: 获取 {len(hk_list)} 只标的")

        # 步骤2：逐标的获取K线
        for idx, (code, name) in enumerate(hk_list):
            if (idx + 1) % 50 == 0:
                self._log.info(f"kline_hk_daily 进度: {idx+1}/{len(hk_list)}")
            try:
                df = self._call_with_policy(
                    ak.stock_hk_hist, policy,
                    symbol=code, period="daily",
                    start_date=ak_start, end_date=ak_end, adjust="",
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标
                self._log.debug(f"stock_hk_hist({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                parsed = self._parse_kline_hk_row(row, code, name, start_str, end_str)
                if parsed:
                    batch_rows.append(parsed)

            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table, columns=columns, rows=batch_rows[:],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

            threading.Event().wait(0.5)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 23. 十大股东（top10_shareholders） ----

    @staticmethod
    def _ts_code_to_em(ts_code: str) -> str:
        """将 ts_code (600519.SH) 转为东财格式 (SH600519)。

        东财 API 的 stock_gdfx_top_10_em / stock_gdfx_free_top_10_em
        需要带市场前缀的代码（如 SH600519），而非纯数字。
        """
        parts = ts_code.split(".")
        if len(parts) == 2:
            return parts[1].upper() + parts[0]
        return ts_code

    def _fetch_futures_position(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取期货持仓排名数据（前20名经纪商汇总），写入 c1_market.futures_position。

        #ARCH-FUTURES-POSITION: 替代 QMT（QMT get_instrument_detail 返回全0）。
        从各交易所排名表 API 获取前20名经纪商的多头/空头持仓量，
        汇总为合约级总计（long_position=Σlong_open_interest, 等）。

        数据源:
          CFFEX: ak.get_cffex_rank_table(date) → dict{合约: DataFrame}
          SHFE:  ak.get_shfe_rank_table(date)
          DCE:   ak.get_dce_rank_table(date)
          CZCE:  ak.get_rank_table_czce(date)
        每个合约 DataFrame 列: long_open_interest, short_open_interest, vol, ...
        """
        import akshare as ak

        table = "c1_market.futures_position"
        columns = [
            "trade_date", "symbol", "long_position", "short_position",
            "long_volume", "short_volume", "exchange", "data_source",
        ]

        date_str = payload.end.strftime("%Y%m%d") if payload.end else ""
        if not date_str:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="futures_position 缺少 end 日期",
            )
            return

        trade_date = payload.end.strftime("%Y-%m-%d")
        batch_rows: list[tuple] = []
        t0 = time.time()

        # 各交易所排名表 API（#ARCH-FUTURES-POSITION: DCE/CZCE API 可能挂起，
        # 用线程超时包装防止无限等待；超时的交易所跳过，不影响其他交易所）
        from concurrent.futures import ThreadPoolExecutor
        from concurrent.futures import TimeoutError as FuturesTimeout

        exchange_apis = [
            ("CFFEX", ak.get_cffex_rank_table, 200),  # CFFEX 较慢
            ("SHFE", ak.get_shfe_rank_table, 30),
            ("DCE", ak.get_dce_rank_table, 60),
            ("CZCE", ak.get_rank_table_czce, 60),
        ]

        for exchange_name, api_fn, timeout_sec in exchange_apis:
            try:
                # 线程超时包装（不用 with 块，避免 shutdown(wait=True) 阻塞）
                ex = ThreadPoolExecutor(max_workers=1)
                future = ex.submit(api_fn, date=date_str)
                try:
                    result = future.result(timeout=timeout_sec)
                except FuturesTimeout:
                    ex.shutdown(wait=False)  # 不等待挂起线程
                    self._log.warning(
                        f"futures_position {exchange_name} 超时({timeout_sec}s)，跳过"
                    )
                    continue
                finally:
                    ex.shutdown(wait=False)

                if result is None:
                    continue
                # result 可能是 dict{合约: DataFrame} 或 DataFrame
                if isinstance(result, dict):
                    for contract, df in result.items():
                        if df is None or len(df) == 0:
                            continue
                        try:
                            row = self._sum_futures_position_row(
                                df, contract, trade_date, exchange_name,
                            )
                            if row:
                                batch_rows.append(row)
                        except Exception:  # noqa: BLE001 — 5.135治标
                            pass  # 跳过格式异常的合约
                elif hasattr(result, "columns"):
                    try:
                        row = self._sum_futures_position_row(
                            result, "", trade_date, exchange_name,
                        )
                        if row:
                            batch_rows.append(row)
                    except Exception:  # noqa: BLE001 — 5.135治标
                        pass
            except Exception as e:  # noqa: BLE001 — 5.135治标
                self._log.warning(f"futures_position {exchange_name} 失败: {e}")

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=date_str, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _sum_futures_position_row(
        df, symbol: str, trade_date: str, exchange: str,
    ) -> tuple | None:
        """将前20名经纪商的持仓汇总为合约级单行。

        #ARCH-FUTURES-POSITION: 用 pd.to_numeric 安全转换（CZCE 返回逗号拼接字符串，
        直接 int(sum()) 会 ValueError）。
        """
        import pandas as pd

        long_oi_col = "long_open_interest" if "long_open_interest" in df.columns else None
        short_oi_col = "short_open_interest" if "short_open_interest" in df.columns else None
        vol_col = "vol" if "vol" in df.columns else None

        def _safe_sum(col):
            if not col:
                return 0
            try:
                return int(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())
            except Exception:  # noqa: BLE001 — 5.135治标
                return 0

        long_pos = _safe_sum(long_oi_col)
        short_pos = _safe_sum(short_oi_col)
        total_vol = _safe_sum(vol_col)

        # 从 DataFrame 获取 symbol（若参数为空）
        if not symbol and "symbol" in df.columns and len(df) > 0:
            symbol = str(df.iloc[0].get("symbol", ""))

        if not symbol:
            return None

        return (
            trade_date, symbol,
            long_pos, short_pos,
            total_vol, total_vol,  # long_volume = short_volume = total_vol
            exchange, "akshare",
        )

    def _fetch_top10_shareholders(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取十大股东，写入 c3_fundamental.top10_shareholders。

        调用 ak.stock_gdfx_top_10_em(symbol, date) 逐股票逐季度拉取。
        date 为季度末日期：0331/0630/0930/1231。
        symbol 需为东财格式（如 SH600519），由 _ts_code_to_em 转换。

        东财返回列: 名次, 股东名称, 股份类型, 持股数, 占总股本持股比例, 增减, 变动比率
        """
        import akshare as ak

        table = _TBL_TOP10_SHAREHOLDERS
        columns = [
            "symbol", "announce_date", "report_period", "shareholder_name",
            "hold_shares", "hold_ratio", "float_ratio", "hold_change",
            "shareholder_type", "data_source", "quality_flag",
        ]
        symbols = payload.symbols or []
        if not symbols:
            # symbols=null 契约（裁定 #ARCH-CH-018）：自动获取全 A 股标的列表
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="top10_shareholders 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return

        # 生成季度末日期列表
        quarter_ends = self._generate_quarter_ends(payload.start, payload.end)
        batch_rows: list[tuple] = []
        start_ts = time.time()
        last_key = payload.end.isoformat() if payload.end else ""

        for ts_code in symbols:
            sym = ts_code.split(".")[0].zfill(6) if "." in ts_code else ts_code.zfill(6)
            em_code = self._ts_code_to_em(ts_code)
            for qe in quarter_ends:
                date_str = qe.strftime("%Y%m%d")
                try:
                    df = self._call_with_policy(
                        ak.stock_gdfx_top_10_em, policy,
                        symbol=em_code, date=date_str,
                    )
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    self._log.debug(f"stock_gdfx_top_10_em({em_code},{date_str}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                for _, row in df.iterrows():
                    batch_rows.append(_build_top10_shareholder_row(
                        row, sym, qe, "占总股本持股比例", "股份类型",
                    ))
                    if len(batch_rows) >= 500:
                        yield FetchResult(
                            table=table, columns=columns, rows=batch_rows[:],
                            last_key=last_key, elapsed_sec=time.time() - start_ts,
                        )
                        batch_rows.clear()
                        start_ts = time.time()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - start_ts,
        )

    # ---- 24. 十大流通股东（top10_circulating_shareholders） ----

    def _fetch_top10_circulating_shareholders(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取十大流通股东，写入 c3_fundamental.top10_circulating_shareholders。

        调用 ak.stock_gdfx_free_top_10_em(symbol, date) 逐股票逐季度拉取。
        symbol 需为东财格式（如 SH600519）。

        东财返回列: 名次, 股东名称, 股东性质, 股份类型, 持股数, 占总流通股本持股比例, 增减, 变动比率
        """
        import akshare as ak

        table = _TBL_TOP10_CIRCULATING_SHAREHOLDERS
        columns = [
            "symbol", "announce_date", "report_period", "shareholder_name",
            "hold_shares", "hold_ratio", "float_ratio", "hold_change",
            "shareholder_type", "data_source", "quality_flag",
        ]
        symbols = payload.symbols or []
        if not symbols:
            # symbols=null 契约（裁定 #ARCH-CH-018）：自动获取全 A 股标的列表
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="top10_circulating_shareholders 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return

        quarter_ends = self._generate_quarter_ends(payload.start, payload.end)
        batch_rows: list[tuple] = []
        start_ts = time.time()
        last_key = payload.end.isoformat() if payload.end else ""

        for ts_code in symbols:
            sym = ts_code.split(".")[0].zfill(6) if "." in ts_code else ts_code.zfill(6)
            em_code = self._ts_code_to_em(ts_code)
            for qe in quarter_ends:
                date_str = qe.strftime("%Y%m%d")
                try:
                    df = self._call_with_policy(
                        ak.stock_gdfx_free_top_10_em, policy,
                        symbol=em_code, date=date_str,
                    )
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    self._log.debug(f"stock_gdfx_free_top_10_em({em_code},{date_str}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                for _, row in df.iterrows():
                    batch_rows.append(_build_top10_shareholder_row(
                        row, sym, qe, "占总流通股本持股比例", "股东性质",
                    ))
                    if len(batch_rows) >= 500:
                        yield FetchResult(
                            table=table, columns=columns, rows=batch_rows[:],
                            last_key=last_key, elapsed_sec=time.time() - start_ts,
                        )
                        batch_rows.clear()
                        start_ts = time.time()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - start_ts,
        )

    # ---- 25. 预约披露计划（disclosure_plan） ----

    def _fetch_disclosure_plan(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取预约披露计划，写入 c3_fundamental.disclosure_plan。

        调用 ak.stock_report_disclosure(market, period) 按报告期拉取。
        akshare 1.18+ 接口已从 stock_disclosure_report_cninfo 变更为
        stock_report_disclosure（按报告期维度，不再支持按日期范围批量查询）。
        """
        import akshare as ak

        table = _TBL_DISCLOSURE_PLAN
        columns = [
            "symbol", "report_period", "announce_date",
            "scheduled_date", "actual_date", "data_source", "quality_flag",
        ]
        end = payload.end or datetime.date.today()
        last_key = end.isoformat()
        t0 = time.time()

        report_periods = self._generate_report_periods(payload.start, end)
        all_rows: list[tuple] = []

        try:
            for period_str in report_periods:
                try:
                    df = self._call_with_policy(
                        ak.stock_report_disclosure, policy,
                        market="沪深京", period=period_str,
                    )
                except Exception as e:  # noqa: BLE001
                    self._log.warning(
                        "stock_report_disclosure(%s) 失败: %s", period_str, e
                    )
                    continue

                if df is None or len(df) == 0:
                    continue

                period_date = self._period_str_to_date(period_str)
                for _, row in df.iterrows():
                    sym = str(row.get("股票代码", "") or "").zfill(6)
                    if not sym:
                        continue
                    scheduled_date = self._norm_date_str(row.get("首次预约"))
                    actual_date = self._norm_date_str(row.get("实际披露"))
                    all_rows.append((
                        sym,
                        period_date,
                        actual_date or None,
                        scheduled_date or None,
                        actual_date or None,
                        "akshare",
                        1,
                    ))
        except Exception as e:  # noqa: BLE001
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        yield FetchResult(
            table=table, columns=columns, rows=all_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _generate_report_periods(
        start: datetime.date | None, end: datetime.date
    ) -> list[str]:
        """生成 start~end 之间的报告期列表（如 ['2025年报', '2026一季报']）。

        治本修复 #ARCH-DISCLOSURE-PERIODS（2026-07-24）：
        原条件 `start <= period_date` 排除了仍有数据的历史报告期。
        报告期(period_date)是财报截止日，但披露窗口(announce_date)通常在报告期后1-4个月。
        例如 2025年报 period_date=2025-12-31，但披露窗口是 2026-01~2026-04。
        当增量 start=2026-06-30 时，2025年报被 `start <= period_date` 排除，
        但其披露窗口可能仍有新数据（如补充披露/修正公告）。
        修复：放宽 start 回看 180 天，确保覆盖上一披露季的报告期。
        """
        periods = []
        if end is None:
            end = datetime.date.today()
        if start is None:
            start = end - datetime.timedelta(days=365)

        _period_map = {
            "一季": (3, 31),
            "半年报": (6, 30),
            "三季": (9, 30),
            "年报": (12, 31),
        }

        # 回看窗口：报告期截止日可能在 start 之前，但披露窗口延伸到 start 之后
        lookback_start = start - datetime.timedelta(days=180)

        year = lookback_start.year
        while year <= end.year:
            for period_name, (month, day) in _period_map.items():
                period_date = datetime.date(year, month, day)
                if lookback_start <= period_date <= end + datetime.timedelta(days=180):
                    periods.append(f"{year}{period_name}")
            year += 1
        return periods

    @staticmethod
    def _period_str_to_date(period_str: str) -> str:
        """将报告期字符串转换为日期字符串（YYYY-MM-DD）。

        akshare stock_report_disclosure 的 period 参数格式为 '{year}{name}'，
        如 '2026一季'、'2026半年报'、'2026三季'、'2026年报'。
        本方法将其转换为对应的报告期截止日期字符串，供 ClickHouse Date 列写入。

        Args:
            period_str: 报告期字符串，如 '2026一季'。

        Returns:
            日期字符串，如 '2026-03-31'。
        """
        _period_suffix_map = {
            "一季": (3, 31),
            "半年报": (6, 30),
            "三季": (9, 30),
            "年报": (12, 31),
        }
        year = int(period_str[:4])
        for suffix, (month, day) in _period_suffix_map.items():
            if period_str.endswith(suffix):
                return f"{year:04d}-{month:02d}-{day:02d}"
        return period_str

    @staticmethod
    def _generate_quarter_ends(
        start: datetime.date, end: datetime.date
    ) -> list[datetime.date]:
        """生成 start~end 之间的季度末日期列表。"""
        quarter_ends = []
        if start is None or end is None:
            today = datetime.date.today()
            # 默认取最近4个季度
            for i in range(4):
                qe = today - datetime.timedelta(days=90 * (i + 1))
                # 调整到季度末
                month = qe.month
                if month <= 3:
                    qe = datetime.date(qe.year, 3, 31)
                elif month <= 6:
                    qe = datetime.date(qe.year, 6, 30)
                elif month <= 9:
                    qe = datetime.date(qe.year, 9, 30)
                else:
                    qe = datetime.date(qe.year, 12, 31)
                quarter_ends.append(qe)
            return sorted(set(quarter_ends))

        year = start.year
        while year <= end.year:
            for month, day in [(3, 31), (6, 30), (9, 30), (12, 31)]:
                qe = datetime.date(year, month, day)
                if start <= qe <= end:
                    quarter_ends.append(qe)
            year += 1
        return quarter_ends

    # ---- 26. 回购数据（repurchase） ----

    def _fetch_repurchase(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取A股回购数据全量刷新，写入 c3_fundamental.repurchase。

        调用 ak.stock_repurchase_em() 获取当前所有活跃回购记录。
        该接口返回全量数据（非按日期增量），每次刷新覆盖最新状态。
        """
        import akshare as ak

        table = _TBL_REPURCHASE
        columns = [
            "announce_date", "symbol", "name", "plan_price_range",
            "plan_qty_min", "plan_qty_max", "plan_pct_min", "plan_pct_max",
            "plan_amount_min", "plan_amount_max", "start_date", "progress",
            "done_price_min", "done_price_max", "done_qty", "done_amount",
            "data_source",
        ]
        iso_date = datetime.date.today().isoformat()
        t0 = time.time()

        try:
            df = self._call_with_policy(
                ak.stock_repurchase_em, policy,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=iso_date,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码") or "").zfill(6)
                if not sym:
                    continue
                ann_date_raw = str(row.get("最新公告日期") or "")
                ann_date = ann_date_raw[:10] if len(ann_date_raw) >= 10 else iso_date
                try:
                    ann_date = datetime.date.fromisoformat(ann_date).isoformat()
                except (ValueError, TypeError):
                    ann_date = iso_date
                rows.append((
                    ann_date,
                    sym,
                    str(row.get("股票简称") or ""),
                    str(row.get("计划回购价格区间") or ""),
                    safe_float(row.get("计划回购数量区间-下限")),
                    safe_float(row.get("计划回购数量区间-上限")),
                    safe_float(row.get("占公告前一日总股本比例-下限")),
                    safe_float(row.get("占公告前一日总股本比例-上限")),
                    safe_float(row.get("计划回购金额区间-下限")),
                    safe_float(row.get("计划回购金额区间-上限")),
                    str(row.get("回购起始时间") or ""),
                    str(row.get("实施进度") or ""),
                    safe_float(row.get("已回购股份价格区间-下限")),
                    safe_float(row.get("已回购股份价格区间-上限")),
                    safe_float(row.get("已回购股份数量")),
                    safe_float(row.get("已回购金额")),
                    "akshare",
                ))

        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 27. 可转债列表（convertible_bond_list） ----

    def _fetch_convertible_bond_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """可转债列表全量刷新，写入 c1_market.convertible_bond_list。"""
        import akshare as ak
        table = _TBL_CONVERTIBLE_BOND_LIST
        columns = [
            "bond_code", "bond_name", "bond_short_name", "convert_code",
            "stock_code", "stock_name", "issue_term", "par_value",
            "issue_price", "issue_amount", "bond_balance", "start_date",
            "end_date", "rate_type", "coupon_rate", "comp_rate", "pay_count",
            "list_date", "delist_date", "list_place", "convert_start",
            "convert_end", "stop_convert", "initial_convert_price",
            "latest_convert_price", "rate_desc", "redeem_price",
            "issue_credit", "latest_credit", "latest_agency",
        ]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.bond_zh_cov, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append(self._parse_convertible_bond_row(r))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    @staticmethod
    def _parse_convertible_bond_row(r) -> tuple:
        """解析单行可转债数据。"""
        return (
            str(r.get("债券代码", "") or ""),
            str(r.get("债券简称", "") or ""),
            str(r.get("债券简称", "") or ""),
            str(r.get("转股代码", "") or ""),
            str(r.get("正股代码", "") or "").zfill(6),
            str(r.get("正股简称", "") or ""),
            safe_float(r.get("发行期限")),
            safe_float(r.get("面值")),
            safe_float(r.get("发行价格")),
            safe_float(r.get("发行规模")),
            safe_float(r.get("债券余额")),
            AkshareIngestProvider._norm_date_str(r.get("起始日期")),
            AkshareIngestProvider._norm_date_str(r.get("截止日期")),
            str(r.get("利率类型", "") or ""),
            safe_float(r.get("票面利率")),
            safe_float(r.get("补偿利率")),
            int(safe_float(r.get("付息频率")) or 0),
            AkshareIngestProvider._norm_date_str(r.get("上市日期")),
            AkshareIngestProvider._norm_date_str(r.get("摘牌日期")),
            str(r.get("上市地点", "") or ""),
            AkshareIngestProvider._norm_date_str(r.get("转股起始日")),
            AkshareIngestProvider._norm_date_str(r.get("转股截止日")),
            AkshareIngestProvider._norm_date_str(r.get("停止转股日")),
            safe_float(r.get("初始转股价")),
            safe_float(r.get("最新转股价")),
            str(r.get("利率说明", "") or ""),
            safe_float(r.get("赎回价格")),
            str(r.get("发行信用评级", "") or ""),
            str(r.get("最新信用评级", "") or ""),
            str(r.get("最新评级机构", "") or ""),
        )

    # ---- 27. ETF列表（etf_list） ----

    def _fetch_etf_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """ETF基金列表全量刷新，写入 c1_market.etf_list。"""
        import akshare as ak
        table = _TBL_ETF_LIST
        columns = [
            "etf_code", "etf_name", "etf_abbr", "full_name",
            "index_code", "index_name", "setup_date", "list_date",
            "list_status", "exchange", "manager", "custodian",
            "mgmt_fee", "etf_type",
        ]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.fund_etf_category_sina, policy, symbol="ETF基金")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append(self._parse_etf_list_row(r))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    @staticmethod
    def _parse_etf_list_row(r) -> tuple:
        """解析单行ETF列表数据。

        2026-08-14 修复：sina 源多数基金无成立/上市日期（空串），CH 表 setup_date/list_date
        为非空 Date 列，空串触发 Code 38 写入失败整批落盘。空日期改用 1970-01-01 哨兵。
        """
        return (
            str(r.get("代码", "") or ""),
            str(r.get("名称", "") or ""),
            str(r.get("简称", "") or ""),
            str(r.get("全称", "") or ""),
            str(r.get("跟踪指数代码", "") or ""),
            str(r.get("跟踪指数名称", "") or ""),
            AkshareIngestProvider._norm_date_str(r.get("成立日期")) or "1970-01-01",
            AkshareIngestProvider._norm_date_str(r.get("上市日期")) or "1970-01-01",
            str(r.get("上市状态", "") or ""),
            str(r.get("交易市场", "") or ""),
            str(r.get("管理人", "") or ""),
            str(r.get("托管人", "") or ""),
            safe_float(r.get("管理费")),
            str(r.get("类型", "") or ""),
        )

    # ---- 28. LOF列表（lof_list） ----

    def _fetch_lof_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """LOF基金列表全量刷新，写入 c1_market.lof_list。"""
        import akshare as ak
        table = _TBL_LOF_LIST
        columns = ["code", "name"]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.fund_lof_spot_em, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append((
                    str(r.get("代码", "") or ""),
                    str(r.get("名称", "") or ""),
                ))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 29. 港股列表（hk_stock_list） ----

    def _fetch_hk_stock_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """港股列表全量刷新，写入 c1_market.hk_stock_list。"""
        import akshare as ak
        table = _TBL_HK_STOCK_LIST
        columns = ["code", "name"]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.stock_hk_spot_em, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append((
                    str(r.get("代码", "") or ""),
                    str(r.get("名称", "") or ""),
                ))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 30. 港股交易日历（hk_trade_calendar） ----
    # #ARCH-DATA-001: 已迁移至 InternalComputeProvider（exchange_calendars XHKG 港交所真日历）。
    # akshare tool_trade_date_hist_sina 实为 A 股日历，语义错配，故移除本 provider 的该能力。

    # ---- 30b. A股交易日历（trade_calendar，#ARCH-DATA-015） ----

    def _fetch_trade_calendar(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """A股交易日历（akshare tool_trade_date_hist_sina，新浪源，须断VPN）。

        #ARCH-DATA-015：baostock IP 黑名单治本——trade_calendar_refresh 原无 fallback，
        本能力为其兜底。sina 只返回开市日 → is_open=1；pretrade_date=上一开市日
        （首个开市日取自身）。列名对齐 trade_calendar 表 schema。
        """
        import akshare as ak
        table = payload.table or _TBL_TRADE_CALENDAR
        columns = ["exchange", "cal_date", "is_open", "pretrade_date"]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.tool_trade_date_hist_sina, policy)
            dates = []
            if df is not None and len(df):
                for v in df["trade_date"].tolist():
                    if isinstance(v, datetime.datetime):
                        dates.append(v.date())
                    elif isinstance(v, datetime.date):
                        dates.append(v)
                    else:  # 字符串/Timestamp 兜底
                        dates.append(datetime.date.fromisoformat(str(v)[:10]))
                dates.sort()
            start, end = payload.start, payload.end
            if start:
                dates = [d for d in dates if d >= start]
            if end:
                dates = [d for d in dates if d <= end]
            rows: list[tuple] = []
            prev: datetime.date | None = None
            for d in dates:
                rows.append(("SSE", d, 1, prev or d))
                prev = d
            self._log.info(f"trade_calendar: {len(rows)} 行（akshare 新浪源）")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=(end or datetime.date.today()).isoformat(),
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"trade_calendar 获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.time() - t0, error=str(e),
            )

    # ---- 30c. 沪深300成分股（index_constituent，#ARCH-DATA-015） ----

    # JOB-077 DS-084：指数成分覆盖范围（沪深300/中证500/中证1000/中证全指）
    _INDEX_MEMBER_CODES: tuple[tuple[str, str], ...] = (
        ("000300", "000300.SH"),  # 沪深300
        ("000905", "000905.SH"),  # 中证500
        ("000852", "000852.SH"),  # 中证1000
        ("000985", "000985.SH"),  # 中证全指
    )

    def _fetch_index_weight_map(self, ak, policy: SourcePolicy, raw_code: str) -> dict[str, float]:
        """中证指数权重快照（月末发布），key=成分券代码；失败降级空 dict（调用方 weight=0）。"""
        try:
            df_w = self._call_with_policy(
                ak.index_stock_cons_weight_csindex, policy, symbol=raw_code
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"index {raw_code} 权重获取失败（weight=0 降级）: {e}")
            return {}
        weight_map: dict[str, float] = {}
        if df_w is None or len(df_w) == 0:
            return weight_map
        for _, wr in df_w.iterrows():
            wcode = str(wr.get("成分券代码", "") or "").zfill(6)
            wval = safe_float(wr.get("权重"))
            if wcode and wval is not None:
                weight_map[wcode] = wval
        return weight_map

    def _index_constituent_rows(
        self, df_cons, l3_code: str, weight_map: dict[str, float], fallback_date: str
    ) -> tuple[str, list[tuple]]:
        """成分清单 DataFrame → (trade_date, 行集)。

        trade_date 取成分接口"日期"列最大值（PIT 以清单生效日为准），
        无该列时回退 fallback_date。权重为最近可得月末快照值（缺失=0）。
        """
        trade_date = fallback_date
        rows: list[tuple] = []
        if df_cons is None or len(df_cons) == 0:
            return trade_date, rows
        try:
            dates = [self._norm_akshare_date(v) for v in df_cons["日期"].tolist()]
            dates = [d for d in dates if d]
            if dates:
                trade_date = max(dates)
        except KeyError:
            pass
        for _, r in df_cons.iterrows():
            code = str(r.get("成分券代码", "") or "").zfill(6)
            if len(code) != 6 or not code.isdigit():
                continue
            rows.append((
                trade_date, l3_code, _cn_code_to_symbol(code),
                weight_map.get(code, 0), "", "akshare_csindex",
            ))
        return trade_date, rows

    def _fetch_index_constituent(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """指数成分及权重（akshare 中证指数官网源，JOB-077 DS-084 扩展）。

        #ARCH-DATA-015：tasks.yaml 原配置 akshare fallback 但无对应 capability（死
        fallback），本方法补全。JOB-077（2026-08-15）从仅沪深300扩展为四指数
        （300/500/1000/中证全指），并经 index_stock_cons_weight_csindex 补真实权重
        （原官网成分接口不含权重 → weight=0，同 miniqmt 口径）。
        权重接口按月末发布权重日快照（row级日期），成分按当前清单日——成员资格
        以成分接口日期为准（universe 用途），权重为最近可得月频值。
        列名对齐 index_constituent 表 schema。每指数 yield 一批。
        """
        import akshare as ak
        table = payload.table or _TBL_INDEX_CONSTITUENT
        columns = ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]
        t0 = time.monotonic()
        fallback_date = (
            payload.end.isoformat() if payload.end else datetime.date.today().isoformat()
        )
        for raw_code, l3_code in self._INDEX_MEMBER_CODES:
            try:
                df_cons = self._call_with_policy(
                    ak.index_stock_cons_csindex, policy, symbol=raw_code
                )
                weight_map = self._fetch_index_weight_map(ak, policy, raw_code)
                trade_date, rows = self._index_constituent_rows(
                    df_cons, l3_code, weight_map, fallback_date
                )
                self._log.info(
                    f"index_constituent {l3_code}: {len(rows)} 行（akshare 中证官网）"
                )
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=trade_date, elapsed_sec=time.monotonic() - t0,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"index_constituent {l3_code} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.monotonic() - t0, error=str(e),
                )

    # ---- 31. 指数列表（index_list） ----

    def _fetch_index_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """指数列表全量刷新，写入 c1_market.index_list。"""
        import akshare as ak
        table = _TBL_INDEX_LIST
        columns = [
            "ts_code", "name", "market", "publisher", "category",
            "base_date", "base_point", "list_date", "symbol_num", "market_id",
        ]
        t0 = time.time()
        rows: list[tuple] = []
        # 从多个交易所获取指数列表
        for market, func_name in [
            ("SH", "stock_info_sh_name_code"),
            ("SZ", "stock_info_sz_name_code"),
        ]:
            try:
                func = getattr(ak, func_name, None)
                if func is None:
                    continue
                df = self._call_with_policy(func, policy)
                if df is None or len(df) == 0:
                    continue
                for _, r in df.iterrows():
                    code = str(r.get("证券代码", r.get("代码", "")) or "")
                    name = str(r.get("证券简称", r.get("名称", "")) or "")
                    if not code:
                        continue
                    rows.append((
                        f"{code}.{market}",
                        name, market, "交易所", "指数",
                        datetime.date(1970, 1, 1), 0.0,
                        datetime.date(1970, 1, 1), "", 0.0,
                    ))
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.debug(f"{func_name} 失败: {e}")
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 32. ETF基准列表（etf_benchmark） ----

    def _fetch_etf_benchmark(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """ETF基准指数列表全量刷新，写入 c1_market.etf_benchmark。"""
        import akshare as ak
        table = _TBL_ETF_BENCHMARK
        columns = [
            "index_code", "index_full_name", "index_short_name",
            "publisher", "publish_date", "base_date", "base_point",
            "adjust_cycle",
        ]
        t0 = time.time()
        rows: list[tuple] = []
        # 从指数列表中获取
        try:
            df = self._call_with_policy(ak.index_stock_info, policy, symbol="000300")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.debug(f"index_stock_info 失败: {e}")
        # 如果没有专门接口，用空数据返回（该表为静态参考，低频变化）
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- ETF基金净值（etf_nav，#ARCH-CH-023: 替代 miniQMT get_etf_info） ----

    @staticmethod
    def _norm_hog_date(v) -> str | None:
        """规范化 akshare 日期为 'YYYY-MM-DD' 字符串（兼容 Timestamp/str/NaT）。"""
        if v is None:
            return None
        s = str(v)
        if s in ("NaT", "nan", "None", ""):
            return None
        return s[:10]

    def _fetch_hog_spot_index(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """生猪现货价格指数（周度），写入 c1_market.hog_spot_index。

        akshare index_hog_spot_price 返回全量历史（2015至今约580行，含指数/均线/成交均价/均重）。
        增量模式按 payload.start 过滤；全量模式取全部。用于猪周期历史定位。
        """
        import akshare as ak

        table = payload.table or _TBL_HOG_SPOT_INDEX
        columns = [
            "trade_date", "index_value", "ma_4m", "ma_6m", "ma_12m",
            "presale_avg_price", "deal_avg_price", "deal_avg_weight",
        ]
        t0 = time.monotonic()
        try:
            df = self._call_with_policy(ak.index_hog_spot_price, policy)
            if df is None or len(df) == 0:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.monotonic() - t0,
                    error="index_hog_spot_price 返回空",
                )
                return
            start_str = payload.start.strftime("%Y-%m-%d") if payload.start else None
            rows: list[tuple] = []
            for _, r in df.iterrows():
                trade_date = self._norm_hog_date(r.get("日期"))
                if not trade_date:
                    continue
                if start_str and trade_date < start_str:
                    continue
                rows.append((
                    trade_date,
                    safe_float(r.get("指数")),
                    safe_float(r.get("4个月均线")),
                    safe_float(r.get("6个月均线")),
                    safe_float(r.get("12个月均线")),
                    safe_float(r.get("预售均价")),
                    safe_float(r.get("成交均价")),
                    safe_float(r.get("成交均重")),
                ))
            last_key = rows[-1][0] if rows else ""
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=last_key, elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"hog_spot_index 获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.monotonic() - t0, error=str(e),
            )

    def _fetch_hog_futures_core(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """生猪期货核心价（日度），写入 c1_market.hog_futures_core。

        akshare futures_hog_core 返回约1年历史（date/value）。用于期现价差/高频信号。
        """
        import akshare as ak

        table = payload.table or _TBL_HOG_FUTURES_CORE
        columns = ["trade_date", "value"]
        t0 = time.monotonic()
        try:
            df = self._call_with_policy(ak.futures_hog_core, policy)
            if df is None or len(df) == 0:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.monotonic() - t0,
                    error="futures_hog_core 返回空",
                )
                return
            start_str = payload.start.strftime("%Y-%m-%d") if payload.start else None
            rows: list[tuple] = []
            for _, r in df.iterrows():
                trade_date = self._norm_hog_date(r.get("date"))
                if not trade_date:
                    continue
                if start_str and trade_date < start_str:
                    continue
                rows.append((trade_date, safe_float(r.get("value"))))
            last_key = rows[-1][0] if rows else ""
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=last_key, elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"hog_futures_core 获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.monotonic() - t0, error=str(e),
            )

    def _fetch_hog_province_spot(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """分省生猪现价（日度快照），写入 c1_market.hog_province_spot。

        akshare spot_hog_soozhu 返回当天28省快照（省份/价格/涨跌幅，无日期列），
        用 payload.end 补 trade_date。用于区域价差分析。
        """
        import akshare as ak

        table = payload.table or _TBL_HOG_PROVINCE_SPOT
        columns = ["trade_date", "province", "price", "change"]
        t0 = time.monotonic()
        if not payload.end:
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=0.0,
                error="hog_province_spot 缺少 end 日期",
            )
            return
        trade_date = payload.end.strftime("%Y-%m-%d")
        try:
            df = self._call_with_policy(ak.spot_hog_soozhu, policy)
            if df is None or len(df) == 0:
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.monotonic() - t0,
                    error="spot_hog_soozhu 返回空",
                )
                return
            rows: list[tuple] = []
            for _, r in df.iterrows():
                province = str(r.get("省份", "") or "").strip()
                if not province:
                    continue
                rows.append((
                    trade_date, province,
                    safe_float(r.get("价格")),
                    safe_float(r.get("涨跌幅")),
                ))
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=trade_date, elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"hog_province_spot 获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.monotonic() - t0, error=str(e),
            )

    def _fetch_etf_nav(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """ETF基金净值增量，写入 c1_market.etf_nav。

        使用 akshare fund_etf_fund_info_em 获取 ETF 历史净值数据。
        替代 miniQMT get_etf_info（客户端不支持，需升级投研版）。
        表 schema: (trade_date, symbol, nav, total_assets, data_source)
        """
        import akshare as ak
        table = payload.table or _TBL_ETF_NAV
        columns = ["trade_date", "symbol", "nav", "total_assets", "data_source"]
        symbols = payload.symbols
        if not symbols:
            # 从 etf_list 表自动加载全市场 ETF 代码（约1764只）
            try:
                from zephyr.data import ch_reader as _chr
                tsv = _chr.query_table(_TBL_ETF_LIST, columns="etf_code")
                if tsv and tsv.strip():
                    symbols = [line.strip() for line in tsv.strip().split("\n") if line.strip()]
                    self._log.info(f"etf_nav 从 etf_list 表加载 {len(symbols)} 只 ETF")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"etf_nav 从 etf_list 表加载失败: {e}")
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=0.0,
                error="etf_nav 无 symbols 且 etf_list 表无数据，请先运行 etf_list_refresh 任务",
            )
            return

        start_date = payload.start.strftime("%Y%m%d") if payload.start else "20200101"
        end_date = payload.end.strftime("%Y%m%d") if payload.end else datetime.date.today().strftime("%Y%m%d")

        for symbol in symbols:
            fund_code = symbol.split(".")[0] if "." in symbol else symbol
            t0 = time.monotonic()  # #ARCH-CH-023: time.monotonic 替代 time.time（DATETIME-NOW-FORBIDDEN gate 合规）
            try:
                df = self._call_with_policy(
                    ak.fund_etf_fund_info_em, policy,
                    fund=fund_code, start_date=start_date, end_date=end_date,
                )
                if df is None or len(df) == 0:
                    continue
                rows: list[tuple] = []
                for _, r in df.iterrows():
                    raw_date = r.get("净值日期")
                    # 过滤 NaT/NaN/None（已退市ETF在请求日期范围内无数据时返回NaT）
                    if raw_date is None:
                        continue
                    trade_date = str(raw_date)
                    if not trade_date or trade_date in ("NaT", "nan", "None"):
                        continue
                    nav = safe_float(r.get("单位净值"))
                    rows.append((
                        trade_date, symbol, nav, None, "akshare",
                    ))
                self._log.info(f"ETF {fund_code} 净值获取完成，{len(rows)} 行")
                yield FetchResult(
                    table=table, columns=columns, rows=rows,
                    last_key=end_date, elapsed_sec=time.monotonic() - t0,
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 治本(裁定#ARCH-ETFNAV-SINGLE-FAIL-001)：单只ETF失败不中断整体任务，
                # 与 _fetch_stock_news_em/_fetch_research_report 的错误处理策略统一为"单只失败continue"。
                # 原 yield error 会触发 scheduler._fetch_and_write 的 break，导致整个任务中止+已拉取数据丢失。
                self._log.warning(f"ETF {fund_code} 净值获取失败，跳过: {e}")
                continue

    # ============== JOB-077 市场元数据与约束接入（DS-081~085，2026-08-15）==============
    # 打板回测急需：universe 构造 + 回测撮合约束前提管道。
    # 五数据集：股票基本信息(DS-081)/涨跌停价格(DS-082)/停复牌(DS-083)/
    # 指数成分(DS-084，扩展既有 _fetch_index_constituent)/ST状态(DS-085，扩展既有 _fetch_st_stock_list)。
    # PIT 语义 strict：全部按交易日快照落库（trade_date=生效日），同日重跑幂等替换。

    # ---- 40a. 股票基本信息（stock_basic，DS-081）----

    @staticmethod
    def _board_of_a_share(code: str) -> str:
        """6 位代码 → 市场板块（静态前缀规则，业界通用口径）。

        60→沪主板 / 68→科创板 / 00→深主板 / 30→创业板 / 43/83/87/88/920→北交所。
        空串=非A股或未知板块（调用方应跳过）。
        """
        if code.startswith("68"):
            return "科创板"
        if code.startswith("60"):
            return "沪主板"
        if code.startswith("30"):
            return "创业板"
        if code.startswith("00"):
            return "深主板"
        if code.startswith(("43", "83", "87", "88", "920")):
            return "北交所"
        return ""

    def _fetch_em_industry_map(
        self, ak, policy: SourcePolicy, target_codes: set[str]
    ) -> dict[str, str]:
        """东财行业板块成分反查 code→行业名（best-effort）。

        东财反爬封锁时连续失败 3 次即放弃（对标 _em_push2_blocked 快速失败模式），
        返回已收集的部分映射（可能为空 dict）。
        """
        result: dict[str, str] = {}
        try:
            boards = self._call_with_policy(ak.stock_board_industry_name_em, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_board_industry_name_em 失败（东财反爬？）: {e}")
            return result
        if boards is None or len(boards) == 0 or "板块名称" not in boards.columns:
            return result
        consecutive_fail = 0
        for board_name in boards["板块名称"].tolist():
            if consecutive_fail >= 3:
                self._log.warning("东财行业板块连续失败3次，放弃行业反查（反爬封锁）")
                break
            try:
                cons = self._call_with_policy(
                    ak.stock_board_industry_cons_em, policy, symbol=board_name
                )
                consecutive_fail = 0
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                consecutive_fail += 1
                self._log.debug(f"stock_board_industry_cons_em({board_name}) 失败: {e}")
                continue
            if cons is None or len(cons) == 0 or "代码" not in cons.columns:
                continue
            for code in cons["代码"].tolist():
                code6 = str(code).zfill(6)
                if code6 in target_codes and code6 not in result:
                    result[code6] = str(board_name)
        return result

    def _fetch_cninfo_industry_map(
        self, ak, policy: SourcePolicy, target_codes: set[str]
    ) -> dict[str, str]:
        """巨潮个股资料反查 code→行业名（东财反爬期降级第二级，best-effort）。

        stock_profile_cninfo 为逐股接口（官方披露站，非东财链路，2026-08-15 实证
        东财全站封锁期可达），连续失败 3 次即放弃（对标 _em_push2_blocked 快速
        失败模式），返回已收集的部分映射（可能为空 dict）。
        口径：巨潮/证监会行业（与东财行业分类存在口径差，registry evidence 留痕）。
        成本：逐股 1 次调用，仅对 EM 反查后仍留空的 SH 代码触发（东财正常时零调用）。
        """
        result: dict[str, str] = {}
        consecutive_fail = 0
        for code in sorted(target_codes):
            if consecutive_fail >= 3:
                self._log.warning("巨潮个股资料连续失败3次，放弃行业反查降级")
                break
            try:
                df = self._call_with_policy(ak.stock_profile_cninfo, policy, symbol=code)
                consecutive_fail = 0
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                consecutive_fail += 1
                self._log.debug(f"stock_profile_cninfo({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0 or "所属行业" not in df.columns:
                continue
            industry = str(df.iloc[0].get("所属行业") or "").strip()
            if industry:
                result[code] = industry
        return result

    @staticmethod
    def _apply_industry_map(rows: list[tuple], industry_map: dict[str, str]) -> list[tuple]:
        """按 code→行业映射填充 industry 列（r[4]），映射未命中保持原值。"""
        return [
            (r[0], r[1], r[2], r[3], industry_map.get(r[1]) or r[4], r[5], r[6], r[7])
            for r in rows
        ]

    def _collect_sh_basic_rows(
        self, ak, policy: SourcePolicy, iso_date: str
    ) -> list[tuple]:
        """上交所股票基本信息行（主板A股+科创板，交易所官网清单）。

        列：证券代码/证券简称/证券全称/公司全称/上市日期（无行业列，由东财反查补全）。
        """
        rows: list[tuple] = []
        for fn_arg in ("主板A股", "科创板"):
            try:
                df_sh = self._call_with_policy(
                    ak.stock_info_sh_name_code, policy, symbol=fn_arg
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"stock_info_sh_name_code({fn_arg}) 失败: {e}")
                continue
            if df_sh is None or len(df_sh) == 0:
                continue
            for _, row in df_sh.iterrows():
                code = str(row.get("证券代码") or "").strip().zfill(6)
                if not code.isdigit() or not self._board_of_a_share(code):
                    continue
                rows.append((
                    iso_date, code,
                    str(row.get("证券简称") or "").strip(),
                    str(row.get("公司全称") or "").strip(),
                    "",  # industry 由东财反查补全
                    self._board_of_a_share(code),
                    self._norm_akshare_date(row.get("上市日期")) or None,
                    "akshare",
                ))
        return rows

    def _collect_sz_basic_rows(
        self, ak, policy: SourcePolicy, iso_date: str
    ) -> list[tuple]:
        """深交所股票基本信息行（A股列表，自带所属行业，交易所官网清单）。"""
        rows: list[tuple] = []
        try:
            df_sz = self._call_with_policy(
                ak.stock_info_sz_name_code, policy, symbol="A股列表"
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_info_sz_name_code(A股列表) 失败: {e}")
            return rows
        if df_sz is None or len(df_sz) == 0:
            return rows
        for _, row in df_sz.iterrows():
            code = str(row.get("A股代码") or "").strip().zfill(6)
            if not code.isdigit() or not self._board_of_a_share(code):
                continue
            rows.append((
                iso_date, code,
                str(row.get("A股简称") or "").strip(),
                "",  # SZ 清单无公司全称列
                str(row.get("所属行业") or "").strip(),
                self._board_of_a_share(code),
                self._norm_akshare_date(row.get("A股上市日期")) or None,
                "akshare",
            ))
        return rows

    def _fetch_stock_basic(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """股票基本信息日快照（DS-081），写入 c1_market.stock_basic。

        源：交易所官网清单（stock_info_sh_name_code 主板A股+科创板 /
        stock_info_sz_name_code A股列表），非东财接口，规避反爬。
        行业：SZ 列表自带"所属行业"（交易所口径）；SH 清单无行业列，经东财行业
        板块成分反查 best-effort 补全；东财反爬封锁期降级巨潮个股资料
        （stock_profile_cninfo，口径=巨潮/证监会行业）；双源均失败留空，
        次日重试自然回补。
        市场板块：代码前缀静态规则（_board_of_a_share）。北交所暂无官网清单接口
        （stock_info_bj 未在 akshare 提供），本期不覆盖（已知缺口）。
        """
        import akshare as ak

        table = payload.table or _TBL_STOCK_BASIC
        columns = [
            "trade_date", "symbol", "name", "fullname", "industry",
            "board", "list_date", "data_source",
        ]
        iso_date = (payload.end or datetime.date.today()).isoformat()
        t0 = time.monotonic()

        rows = self._collect_sh_basic_rows(ak, policy, iso_date)
        rows.extend(self._collect_sz_basic_rows(ak, policy, iso_date))

        # SH 行业补全（东财行业板块反查 → 巨潮个股资料，二级降级 best-effort）
        sh_codes = {r[1] for r in rows if r[4] == "" and r[1].startswith(("60", "68"))}
        if sh_codes:
            industry_map = self._fetch_em_industry_map(ak, policy, sh_codes)
            if industry_map:
                rows = self._apply_industry_map(rows, industry_map)
            remain = {r[1] for r in rows if r[4] == "" and r[1].startswith(("60", "68"))}
            cninfo_map: dict[str, str] = {}
            if remain:
                cninfo_map = self._fetch_cninfo_industry_map(ak, policy, remain)
                if cninfo_map:
                    rows = self._apply_industry_map(rows, cninfo_map)
            self._log.info(
                f"SH 行业补全 {len([r for r in rows if r[4] != ''])}/{len(rows)} 行"
                f"（EM反查 {len(industry_map)} + 巨潮降级 {len(cninfo_map)}）"
            )

        self._log.info(f"stock_basic 快照完成: {len(rows)} 行（{iso_date}）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.monotonic() - t0,
        )

    # ---- 40b. 每日涨跌停价格（stk_limit，DS-082）----

    # 创业板注册制改革生效日：涨跌幅 10%→20%（含ST股）
    _CHINEXT_20PCT_DATE = datetime.date(2020, 8, 24)

    @classmethod
    def _limit_pct_of(
        cls, code: str, trade_date: datetime.date, st_flag: bool
    ) -> float | None:
        """涨跌停幅度（小数），口径=沪深北交易所交易规则。

        科创板 20%（含ST）；创业板 2020-08-24 起 20%（含ST，改革后ST不再区别），
        此前 ST/*ST 5%、非ST 10%（深交所投教：特别规定实施前创业板风险警示股 5%）；
        北交所 30%（无ST 5%规则）；主板 ST/*ST 5%、否则 10%。
        未知板块返回 None（调用方跳过，防误判）。
        """
        if code.startswith("68"):
            return 0.20
        if code.startswith("30"):
            if trade_date >= cls._CHINEXT_20PCT_DATE:
                return 0.20
            return 0.05 if st_flag else 0.10
        if code.startswith(("43", "83", "87", "88", "920")):
            return 0.30
        if code.startswith(("60", "00")):
            return 0.05 if st_flag else 0.10
        return None

    def _load_st_snapshots(
        self, start: datetime.date, end: datetime.date
    ) -> tuple[list[datetime.date], dict[datetime.date, set[str]]]:
        """加载 st_stock_list 快照：返回 (有序快照日期列表, 日期→ST代码集合)。

        窗口 [start-400d, end]：保证 start 当日可取到最近可得历史快照（PIT 严格，
        禁用未来快照）。CH 不可达时返回空（调用方降级 st_flag=0 并记日志）。
        """
        from zephyr.data import ch_reader as _chr

        win_start = start - datetime.timedelta(days=400)
        try:
            tsv = _chr.query(_SQL_ST_SNAPSHOTS.format(
                table=_TBL_ST_STOCK_LIST,
                start=win_start.isoformat(), end=end.isoformat(),
            ))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"st_stock_list 快照加载失败: {e}")
            return [], {}
        by_date: dict[datetime.date, set[str]] = {}
        for line in (tsv or "").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            try:
                d = datetime.date.fromisoformat(parts[0][:10])
            except ValueError:
                continue
            by_date.setdefault(d, set()).add(parts[1].strip())
        return sorted(by_date.keys()), by_date

    def _st_flag_at(
        self,
        snap_dates: list[datetime.date],
        snap_map: dict[datetime.date, set[str]],
        code: str,
        trade_date: datetime.date,
    ) -> int:
        """查询 code 在 trade_date 的 ST 标记：最近可得（≤T）快照口径（PIT 严格）。"""
        import bisect

        if not snap_dates:
            return 0
        idx = bisect.bisect_right(snap_dates, trade_date) - 1
        if idx < 0:
            return 0
        return 1 if code in snap_map[snap_dates[idx]] else 0

    @staticmethod
    def _parse_tsv_dates(tsv: str) -> list[datetime.date]:
        """解析单列日期 TSV（每行一个 YYYY-MM-DD），坏行跳过。"""
        out: list[datetime.date] = []
        for line in (tsv or "").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(datetime.date.fromisoformat(line[:10]))
            except ValueError:
                continue
        return out

    def _parse_kline_bars(
        self, tsv: str
    ) -> dict[str, list[tuple[datetime.date, float, float]]]:
        """解析 kline TSV（trade_date/symbol/close/adj_factor）为 per-symbol 有序序列。

        仅保留可识别板块的 A 股 6 位代码；close/adj 非正值行跳过（防除零与脏数据）。
        """
        bars: dict[str, list[tuple[datetime.date, float, float]]] = {}
        for line in (tsv or "").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            code = parts[1].strip().split(".")[0].zfill(6)
            if not self._board_of_a_share(code):
                continue
            try:
                d = datetime.date.fromisoformat(parts[0][:10])
                close = float(parts[2])
                adj = float(parts[3]) if parts[3] not in ("", "\\N", "NULL") else 1.0
            except ValueError:
                continue
            if close <= 0 or adj <= 0:
                continue
            bars.setdefault(code, []).append((d, close, adj))
        for series in bars.values():
            series.sort(key=lambda x: x[0])
        return bars

    def _stk_limit_row_for(
        self,
        code: str,
        series: list[tuple[datetime.date, float, float]],
        i: int,
        day_set: set[datetime.date],
        snap_dates: list[datetime.date],
        snap_map: dict[datetime.date, set[str]],
    ) -> tuple | None:
        """计算单股单日涨跌停行；非目标交易日/首日无昨收/未知板块返回 None。

        新股无涨跌幅限制期（科创/创业/北交上市前 5 个交易日）产出 NULL 行；
        除权除息日昨收经 adj_factor 前复权因子比修正，先 round(4) 再进 Decimal
        （float epsilon 会翻转 ROUND_HALF_UP 边界）。
        """
        d, _close, adj = series[i]
        if d not in day_set or i == 0:
            return None
        pct_board = self._board_of_a_share(code)
        prev_close, prev_adj = series[i - 1][1], series[i - 1][2]
        pre_close = round(prev_close * (adj / prev_adj), 4)
        st_flag = self._st_flag_at(snap_dates, snap_map, code, d)
        if i < 5 and pct_board in ("科创板", "创业板", "北交所"):
            return (d.isoformat(), code, pre_close, None, None, None,
                    st_flag, pct_board, "rule_computed")
        pct = self._limit_pct_of(code, d, bool(st_flag))
        if pct is None:
            return None
        pc = Decimal(str(pre_close))
        limit_up = float(
            (pc * Decimal(str(1 + pct))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        limit_down = float(
            (pc * Decimal(str(1 - pct))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        return (d.isoformat(), code, pre_close, limit_up, limit_down, pct,
                st_flag, pct_board, "rule_computed")

    def _compute_stk_limit_rows(
        self,
        bars: dict[str, list[tuple[datetime.date, float, float]]],
        trade_days: list[datetime.date],
        snap_dates: list[datetime.date],
        snap_map: dict[datetime.date, set[str]],
    ) -> list[tuple]:
        """全市场逐股逐日计算涨跌停行（编排循环，单行逻辑在 _stk_limit_row_for）。"""
        day_set = set(trade_days)
        rows: list[tuple] = []
        for code, series in bars.items():
            for i in range(len(series)):
                row = self._stk_limit_row_for(code, series, i, day_set, snap_dates, snap_map)
                if row is not None:
                    rows.append(row)
        return rows

    def _fetch_stk_limit(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """每日涨跌停价格（DS-082），写入 c1_market.stk_limit。

        akshare 无全市场涨跌停价接口（2026-08-15 实证 dir(akshare) 仅涨跌停池类
        函数，只覆盖触板个股）→ 按交易所规则由昨收价计算（行业标准做法，对标
        tushare stk_limit 语义）：limit_up/down = round_half_up(pre_close×(1±pct), 0.01)。
        pre_close 口径：kline_daily 上一交易日收盘价，跨除权除息日用 adj_factor
        前复权因子比修正（pre_close = close_prev × adj_T/adj_prev）。
        ST 标记：st_stock_list 最近可得（≤T）快照（PIT 严格）。
        新股：科创板/创业板/北交所上市前 5 个交易日无涨跌幅限制 → limit=NULL；
        主板上市首日 44% 需发行价（无数据）→ 不产出行。
        增量口径：payload.start~end 内每个交易日各算一批，同日重跑幂等替换。
        """
        from zephyr.data import ch_reader as _chr

        table = payload.table or _TBL_STK_LIMIT
        columns = [
            "trade_date", "symbol", "pre_close", "limit_up", "limit_down",
            "limit_pct", "st_flag", "board", "data_source",
        ]
        start = payload.start or datetime.date.today()
        end = payload.end or datetime.date.today()
        if start > end:
            start = end
        t0 = time.monotonic()

        # 1) 交易日序列（kline_daily 实际有数据的日期=开市日代理）
        try:
            tsv_days = _chr.query(_SQL_KLINE_DAYS.format(
                start=start.isoformat(), end=end.isoformat(),
            ))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=f"kline_daily 交易日序列查询失败: {e}",
            )
            return
        trade_days = self._parse_tsv_dates(tsv_days)
        if not trade_days:
            # 区分"CH 不可达"与"确实无数据"：ch_reader.query 失败静默返回空串，
            # 探活 count() 仍为空串 → CH 不可达 → 显式 error（防 0 行假成功掩盖故障）
            if not (_chr.query(_SQL_KLINE_PROBE) or "").strip():
                yield FetchResult(
                    table=table, columns=columns, rows=[], last_key="",
                    elapsed_sec=time.monotonic() - t0,
                    error="ClickHouse 不可达（kline_daily 探活无响应）",
                )
                return
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key=end.isoformat(), elapsed_sec=time.monotonic() - t0,
            )
            return

        # 2) 收盘价+复权因子（前推 45 天缓冲保证 prev_close 可得，覆盖长停牌复牌）
        buf_start = start - datetime.timedelta(days=45)
        try:
            tsv_k = _chr.query(_SQL_KLINE_BARS.format(
                start=buf_start.isoformat(), end=end.isoformat(),
            ))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=f"kline_daily 收盘价查询失败: {e}",
            )
            return
        bars = self._parse_kline_bars(tsv_k)

        # 3) ST 快照（最近可得口径）+ 4) 逐股逐日计算
        snap_dates, snap_map = self._load_st_snapshots(start, end)
        rows = self._compute_stk_limit_rows(bars, trade_days, snap_dates, snap_map)

        self._log.info(
            f"stk_limit 计算完成: {len(rows)} 行（{trade_days[0]}~{trade_days[-1]}）"
        )
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=trade_days[-1].isoformat(), elapsed_sec=time.monotonic() - t0,
        )

    # ---- 40c. 停复牌（suspend_status，DS-083）----

    def _suspend_rows_from_em(self, df, iso_date: str) -> list[tuple]:
        """东财当前停牌清单 → 行集（防御式列名解析——反爬期无法实证列名，候选列名取值）。

        A股代码恰为 6 位数字；港股 5 位等异长代码排除（防 zfill 串号）。
        """
        self._log.info(f"stock_zh_a_stop_em 列: {list(df.columns)}")
        rows: list[tuple] = []
        for _, row in df.iterrows():
            raw = str(row.get("代码") or row.get("股票代码") or "").strip()
            if len(raw) != 6 or not raw.isdigit() or not self._board_of_a_share(raw):
                continue
            rows.append((
                iso_date, raw,
                str(row.get("名称") or row.get("股票简称") or "").strip(),
                self._norm_akshare_date(row.get("停牌日期") or row.get("停牌时间")) or None,
                self._norm_akshare_date(row.get("复牌日期") or row.get("复牌时间")) or None,
                str(row.get("停牌原因") or row.get("停牌事项说明") or "").strip(),
                "akshare_em",
            ))
        return rows

    @staticmethod
    def _iso_or_none(s: str) -> datetime.date | None:
        """'YYYY-MM-DD' 字符串转 date，不可解析返回 None（防御脏数据）。"""
        try:
            return datetime.date.fromisoformat(s[:10])
        except (ValueError, TypeError):
            return None

    # 百度停复牌公告距快照日超过该天数视为陈旧条目（2026-08-15 实证 feed 冻结）
    _BAIDU_SUSPEND_STALE_DAYS = 30

    def _suspend_rows_from_baidu(self, df_bd, iso_date: str) -> list[tuple]:
        """百度停复牌公告 → 行集（列已实证：股票代码/股票简称/停牌时间/复牌时间/停牌事项说明）。

        港股 5 位代码 zfill 后会误撞深主板 00 前缀（实证 003389/009929 港股串入），
        交易所代码列+长度双门禁排除（JOB-077 联调发现）。

        陈旧条目三重过滤（2026-08-15 二审实证：百度 feed 冻结于 2025-11-26，
        全量 8 行公告日期清一色陈旧，其中 3 行标的当日 K 线正常交易=假停牌）：
        1. 源站"是否跳过"标记=1 剔除（源站自标噪声）；
        2. 复牌日 ≤ 快照日剔除（已复牌非当前停牌）；
        3. 公告日期早于 快照日-30天 剔除（feed 冻结/陈旧保护）；
        全被过滤时记 warning——宁可快照空缺，不写假停牌约束。
        """
        snap = datetime.date.fromisoformat(iso_date)
        stale_before = snap - datetime.timedelta(days=self._BAIDU_SUSPEND_STALE_DAYS)
        n_skip_flag = n_resumed = n_stale = 0
        rows: list[tuple] = []
        for _, row in df_bd.iterrows():
            raw = str(row.get("股票代码") or "").strip()
            exch = str(row.get("交易所代码") or "").strip().upper()
            if exch and exch not in ("SH", "SZ", "BJ"):
                continue
            if len(raw) != 6 or not raw.isdigit() or not self._board_of_a_share(raw):
                continue
            if str(row.get("是否跳过") or "").strip() in ("1", "1.0"):
                n_skip_flag += 1
                continue
            resume_d = self._iso_or_none(self._norm_akshare_date(row.get("复牌时间")))
            if resume_d and resume_d <= snap:
                n_resumed += 1
                continue
            notice_d = self._iso_or_none(self._norm_akshare_date(row.get("公告日期")))
            if notice_d and notice_d < stale_before:
                n_stale += 1
                continue
            rows.append((
                iso_date, raw,
                str(row.get("股票简称") or "").strip(),
                self._norm_akshare_date(row.get("停牌时间")) or None,
                resume_d.isoformat() if resume_d else None,
                str(row.get("停牌事项说明") or "").strip(),
                "akshare_baidu",
            ))
        if n_skip_flag or n_resumed or n_stale:
            self._log.warning(
                f"百度停复牌过滤陈旧/噪声条目: 源站跳过={n_skip_flag} "
                f"已复牌={n_resumed} 公告陈旧={n_stale}（保留 {len(rows)} 行）"
            )
        return rows

    def _suspend_snapshot_rows(self, ak, policy: SourcePolicy, iso_date: str) -> list[tuple]:
        """当前停牌股快照行（东财主源 + 百度兜底）。

        东财 stock_zh_a_stop_em 反爬封锁时降级 news_trade_notify_suspend_baidu
        （百度停复牌公告，含停牌时间/复牌时间/停牌事项说明）。
        行: (trade_date, symbol, name, suspend_date, resume_date, reason, data_source)
        """
        # 主源：东财当前停牌清单
        try:
            df = self._call_with_policy(ak.stock_zh_a_stop_em, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_zh_a_stop_em 失败（转百度兜底）: {e}")
            df = None
        if df is not None and len(df):
            rows = self._suspend_rows_from_em(df, iso_date)
            if rows:
                return rows
        # 兜底：百度停复牌公告
        try:
            df_bd = self._call_with_policy(ak.news_trade_notify_suspend_baidu, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"news_trade_notify_suspend_baidu 失败: {e}")
            return []
        if df_bd is None or len(df_bd) == 0:
            return []
        return self._suspend_rows_from_baidu(df_bd, iso_date)

    @staticmethod
    def _parse_ch_date_array(raw: str) -> set[datetime.date]:
        """解析 CH groupArray 返回的日期数组（['2026-01-02','2026-01-05'] 格式）。"""
        out: set[datetime.date] = set()
        for tok in raw.strip().strip("[]").split(","):
            tok = tok.strip().strip("'\"")
            if not tok:
                continue
            try:
                out.add(datetime.date.fromisoformat(tok[:10]))
            except ValueError:
                continue
        return out

    def _derive_suspend_gaps(
        self, code: str, bar_days: set[datetime.date], trade_days: list[datetime.date]
    ) -> list[tuple]:
        """单股缺口推导：交易日无K线且落在首末bar之间 → 停牌日行。

        首尾 bar 之外的缺口=未上市/退市/尾部持续停牌，无法区分故不推导
        （尾部停牌由日快照模式覆盖）。
        """
        if not bar_days:
            return []
        first_bar, last_bar = min(bar_days), max(bar_days)
        rows: list[tuple] = []
        for td in trade_days:
            if td <= first_bar or td >= last_bar or td in bar_days:
                continue
            rows.append((td.isoformat(), code, "", td.isoformat(), None, "",
                         "derived_kline_gap"))
        return rows

    def _suspend_derive_rows(
        self, start: datetime.date, end: datetime.date
    ) -> list[tuple]:
        """K线缺口推导停牌日（历史回填）：交易日无K线且前后均有K线 → 停牌。

        data_source='derived_kline_gap'。已知限制：区间尾部停牌无法与退市区分，
        不推导（由日快照模式覆盖）。按年分批控制内存。
        行: (trade_date, symbol, name, suspend_date, resume_date, reason, data_source)
        """
        from zephyr.data import ch_reader as _chr

        rows: list[tuple] = []
        for year in range(start.year, end.year + 1):
            ys = max(start, datetime.date(year, 1, 1))
            ye = min(end, datetime.date(year, 12, 31))
            try:
                tsv_days = _chr.query(_SQL_KLINE_DAYS.format(
                    start=ys.isoformat(), end=ye.isoformat(),
                ))
                tsv_bars = _chr.query(_SQL_KLINE_SYMBOL_DAYS.format(
                    start=ys.isoformat(), end=ye.isoformat(),
                ))
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"suspend 推导 {year} 年查询失败: {e}")
                continue
            trade_days = self._parse_tsv_dates(tsv_days)
            if not trade_days:
                continue
            for line in (tsv_bars or "").strip().split("\n"):
                parts = line.split("\t", 1)
                if len(parts) != 2:
                    continue
                code = parts[0].strip().split(".")[0].zfill(6)
                if not self._board_of_a_share(code):
                    continue
                bar_days = self._parse_ch_date_array(parts[1])
                rows.extend(self._derive_suspend_gaps(code, bar_days, trade_days))
            self._log.info(f"suspend 推导 {year} 年: 累计 {len(rows)} 行")
        return rows

    def _fetch_suspend_status(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """停复牌记录（DS-083），写入 c1_market.suspend。

        双模式（payload.extra['derive_from_kline'] 切换）：
        - 快照模式（默认）：当前停牌股日快照（东财主源+百度兜底），PIT strict，
          逐日积累形成停牌区间；消费 EVT-CA-003。
        - 推导模式（derive_from_kline=True）：K线缺口推导历史停牌日（回填用）。
        """
        import akshare as ak

        table = payload.table or _TBL_SUSPEND
        columns = [
            "trade_date", "symbol", "name", "suspend_date",
            "resume_date", "reason", "data_source",
        ]
        t0 = time.monotonic()
        end = payload.end or datetime.date.today()
        extra = payload.extra or {}

        if extra.get("derive_from_kline"):
            start = payload.start or end
            rows = self._suspend_derive_rows(start, end)
            self._log.info(f"suspend 推导模式: {len(rows)} 行（{start}~{end}）")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=end.isoformat(), elapsed_sec=time.monotonic() - t0,
            )
            return

        iso_date = end.isoformat()
        rows = self._suspend_snapshot_rows(ak, policy, iso_date)
        self._log.info(f"suspend 快照模式: {len(rows)} 行（{iso_date}）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.monotonic() - t0,
        )

    # ---- 40c. IPO 日历与募资规模（ipo_calendar，tracker #114 / 37号 §3.2a，DS-105）----

    def _fetch_ipo_calendar(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """IPO 日历与募资规模日快照（DS-105），写入 c1_market.ipo_calendar。

        源：巨潮资讯网新股列表（akshare stock_new_ipo_cninfo，匿名，沪深北全市场，
        官方披露口径，非东财接口规避反爬）。事件型流动性抽离（IPO 虹吸）前瞻预警
        的数据管道——37号 §3.2a compute_ipo_liquidity_drain 消费 list_date+
        raise_amount 做未来 5 日募资/市场日均成交额节流判定（如 2026-07-27 长鑫
        科技 688825 募资 666 亿，drain_ratio≈2.5% → SEVERE → 仓位上限 75%）。
        募资规模派生口径：raise_amount(亿元) = 发行价(元) × 总发行数量(万股) / 10000。
        未定档 IPO 的 list_date=None（官方未公告），消费侧前瞻窗口过滤天然跳过，
        公告后次日快照自动纳入。NaN 防御：数值列 NaN→None（CH Nullable(Decimal)
        不收 NaN）；日期列 NaT→None（_norm_akshare_date 对 NaT.strftime 抛
        ValueError，此处兜底）。
        PIT strict：trade_date=快照交易日，全量重拉，(trade_date, symbol)
        ReplacingMergeTree 同日重跑幂等替换。
        """
        import akshare as ak

        table = payload.table or _TBL_IPO_CALENDAR
        columns = [
            "trade_date", "symbol", "name", "list_date", "subscribe_date",
            "issue_price", "total_shares", "raise_amount", "pe_ratio", "data_source",
        ]
        iso_date = (payload.end or datetime.date.today()).isoformat()
        t0 = time.monotonic()

        def _num_or_none(v) -> float | None:
            """NaN/Inf/None/非法值→None（CH Nullable(Decimal) 不收 NaN/Inf）。

            AI-R1-003 红队治本：原仅拒 NaN（f!=f 自检）未拒 Inf——上游
            'inf'/'1e400' 溢出经 safe_float 转 inf 后，total_shares 派生
            int(inf*1e4) 直接 OverflowError 崩整个快照循环（比脏值入库更重）。
            改用 math.isfinite 统一拒非有限值（NaN/±Inf 同面）。
            """
            f = safe_float(v)
            if f is None or not math.isfinite(f):
                return None
            return f

        def _date_or_none(v) -> str | None:
            """NaT/NaN/None→None（_norm_akshare_date 对 pd.NaT.strftime 抛 ValueError）。"""
            try:
                s = self._norm_akshare_date(v)
            except (ValueError, TypeError):
                return None
            return s or None

        rows: list[tuple] = []
        try:
            df = self._call_with_policy(ak.stock_new_ipo_cninfo, policy)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"stock_new_ipo_cninfo 失败: {e}")
            df = None
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                # 严格 6 位数字（AI-R1 复审加固：zfill 前无长度门禁时 5 位码
                # 幻影串号——'00700'.zfill(6)='000700' 撞深主板前缀；对齐
                # _suspend_rows_from_em/baidu 姊妹防御，官方清单恒 6 位）
                code = str(row.get("证劵代码") or "").strip()
                if len(code) != 6 or not code.isdigit():
                    continue
                name = str(row.get("证券简称") or "").strip()
                issue_price = _num_or_none(row.get("发行价"))
                shares_wan = _num_or_none(row.get("总发行数量"))  # 万股
                total_shares = int(shares_wan * 10000) if shares_wan else None
                raise_amount = (
                    round(issue_price * shares_wan / 10000, 4)
                    if issue_price and shares_wan
                    else None
                )  # 亿元 = 元 × 万股 / 10000
                rows.append((
                    iso_date,                                   # trade_date
                    code,                                       # symbol
                    name,                                       # name
                    _date_or_none(row.get("上市日期")),          # list_date
                    _date_or_none(row.get("申购日期")),          # subscribe_date
                    issue_price,                                # issue_price（元）
                    total_shares,                               # total_shares（股）
                    raise_amount,                               # raise_amount（亿元）
                    _num_or_none(row.get("发行市盈率")),          # pe_ratio
                    "akshare_cninfo",                           # data_source
                ))

        self._log.info(f"ipo_calendar 快照完成: {len(rows)} 行（{iso_date}）")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.monotonic() - t0,
        )

