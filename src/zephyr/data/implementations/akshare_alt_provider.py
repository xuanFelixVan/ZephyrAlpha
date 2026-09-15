#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §alt-data
# [MODULE] zephyr.data.implementations.akshare_alt_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.table_registry; stdlib
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] 另类数据免注册直连源（akshare）；表名必经 TableRegistry 派生（#ARCH-CH-024）；
#              禁裸 os.getenv；接口返回空/异常时 yield error FetchResult 不抛出（与 hog_* 同约定）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] akshare 接口异常->yield FetchResult(error=...)（上层计失败不中断其他任务）；
#                  TableRegistry 查不到 category_id->KeyError fail-closed
# [TESTS] tests/zephyr/data/test_alt_sources.py
# [TTL] permanent
"""AkshareAltProvider — 另类数据第 1 批免注册直连源（千股千评 + 航运运价）。

背景（docs/_working/2026-09-12-alt-data-handoff.md §8-1，另类数据施工第 1 批）：
    为什么独立成模块而不开进 akshare_provider：
    - akshare_provider.py 为他在会（研报批）claim 在途文件，另类批独立成件零冲突；
    - 另类源与行情主链路生命周期解耦（接口漂移风险独立演进，alt_source_health_manager 监控）。

能力（capability -> 表）：
    alt_stock_comment   千股千评全表日快照 -> c1_market.alt_stock_comment
                        （东财数据中心综合评价；关注指数=股吧关注度代理——akshare 无股吧
                          发帖量直连接口（2026-09-12 实测枚举确认），人气榜通道
                          stock_hot_rank 已在跑，本能力补全市场级关注度面）
    alt_shipping_index  航运运价指数长表   -> c1_market.alt_shipping_index
                        （BDI 1988 起含日涨跌幅 + BCI/BSI/BHMI/HRCI/BCTI/BDTI 约 2006 起；
                          BDI 双源重叠以 macro_shipping_bdi 为准，免重）

PIT 三公理：快照/指数即所得，无前视；trade_date 取接口自带日期列（千股千评"交易日"
常为 T-1），不信运行日。
"""

from __future__ import annotations

import datetime
import json
import logging
import re
import time

import pandas as pd
import urllib.parse
import urllib.request
from typing import Iterator

from zephyr.data.policy_registry import SourcePolicy
from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.data.table_registry import get_registry
from zephyr.shared.security.secrets import get_secret_or_default

log = logging.getLogger(__name__)

# 表名从 business_data_categories.yaml 真源派生（#ARCH-CH-024，禁硬编码）
_TBL_ALT_STOCK_COMMENT = get_registry().table("market_alt_stock_comment")
_TBL_ALT_SHIPPING_INDEX = get_registry().table("market_alt_shipping_index")

# 千股千评表列（顺序与 DDL INSERT_COLUMNS 一致）
_ALT_COMMENT_COLUMNS = [
    "trade_date",
    "symbol",
    "name",
    "org_participation",
    "composite_score",
    "rank_change",
    "current_rank",
    "attention_index",
    "main_cost",
]

# 运价长表列
_ALT_SHIPPING_COLUMNS = ["trade_date", "index_code", "index_name", "value", "change_pct", "source"]

# 台风路径表列（顺序与 DDL INSERT_COLUMNS 一致）
_ALT_TYPHOON_COLUMNS = [
    "keyid", "tcidx", "tcno", "cname", "ename", "tclevel",
    "issue_ts", "forecast_ts", "interval_hours",
    "longitude", "latitude", "airpressure", "wind", "gust", "movespeed", "movedir",
    "radius6", "radius7", "radius8", "radius10", "issuer", "crt_time", "crt_date", "source",
]
_SZ_TYPHOON_URL = "https://opendata.sz.gov.cn/api/1049994100/1/service.xhtml"
_SZ_TYPHOON_PAGE_SIZE = 10000  # 平台单页上限
_SZ_TYPHOON_MAX_PAGES = 60     # 全量约 13 页，60 页为防御性天花板

# ---- 深圳开放数据平台批量源（spec 驱动，2026-09-14） ----
# 统计月报族 7+12 系列 -> alt_sz_stat_monthly（2026-09-14 深夜扩容：新 12 系列绑新钥匙
# SZ_OPEN_DATA_APPKEY_NEW=0ecc2b46，系列元组第三位 None=用主钥匙；数据接口页订阅绑定在
# 新钥匙应用名下——同接口主钥匙 10001 而新钥匙 200 实证）
_SZ_STAT_SERIES: tuple[tuple[str, str], ...] = (
    ("stat_gdp", "29200_03302370"),
    ("stat_price", "29200_03302383"),
    ("stat_fiscal", "29200_03302382"),
    ("stat_transport", "29200_03302377"),
    ("stat_trade", "29200_03302379"),
    ("stat_quick", "29200_03302369"),
    ("stat_fixinv", "29200_03302375"),
)
_SZ_STAT_SERIES_BATCH2: tuple[tuple[str, str], ...] = (
    ("stat_industry", "29200_03302373"),
    ("stat_industry_eff", "29200_03302374"),
    ("stat_construction", "29200_03302376"),
    ("stat_domestic_trade", "29200_03302378"),
    ("stat_fdi", "29200_03302380"),
    ("stat_tourism", "29200_03302381"),
    ("stat_private", "29200_03302384"),
    ("stat_district", "29200_03302385"),
    ("stat_emerging", "29200_03302386"),
    ("stat_annual_main", "29200_03302387"),
    ("stat_district_gdp", "29200_03302388"),
)
# 异构两件（字段形不兼容 stat 解析器）：统计分析（文章型 XH/BT/NY/ZW）与
# 企业登记发展（年表 NF+分类企业数）走独立 cap + 独立表
_SZ_STAT_SERIES_ALL = _SZ_STAT_SERIES + _SZ_STAT_SERIES_BATCH2
# 口岸流量 3+4 系列 -> alt_sz_port_monthly（批3：出入境人员/车辆/机场旅客/客船，新钥匙通道）
_SZ_PORT_SERIES: tuple[tuple[str, str], ...] = (
    ("port_teu", "29200_51400003"),
    ("port_goods", "29200_51400004"),
    ("port_air", "29200_51400006"),
    ("port_pax", "29200_51400001"),
    ("port_vehicles", "29200_51400002"),
    ("port_airpax", "29200_51400005"),
    ("port_ferry", "29200_51400020"),
)
_SZ_PORT_BATCH2_SIDS = {"29200_51400001", "29200_51400002", "29200_51400005", "29200_51400020"}
# 楼市日度 2 系列 -> alt_sz_house_daily
_SZ_HOUSE_SERIES: tuple[tuple[str, str], ...] = (
    ("house_new", "29200_01903510"),
    ("house_second", "29200_01903513"),
)
# 单一源
_SZ_SINGLE_APIS: dict[str, str] = {
    "alt_sz_weather_warning": "589826359/1/service.xhtml",
    "alt_sz_marine_forecast": "1464350655/1/service.xhtml",
    "alt_sz_visibility": "1580458478/1/service.xhtml",
    "alt_sz_air_quality_daily": "1920606096/1/service.xhtml",
    "alt_sz_air_quality_region": "29200_01003608/1/service.xhtml",
    "alt_sz_reservoir_level": "1952552493/1/service.xhtml",
    "alt_sz_reservoir_station": "1392394662/1/service.xhtml",
    "alt_sz_reservoir_rain_day": "29200_01403151/1/service.xhtml",
    "alt_sz_reservoir_rain_month": "29200_01403149/1/service.xhtml",
    "alt_sz_house_area": "29200_01903511/1/service.xhtml",
    "alt_sz_house_listing": "29200_01903509/1/service.xhtml",
    "alt_sz_house_presale": "29200_01903508/1/service.xhtml",
    "alt_sz_port_passengers": "29200_51400001/1/service.xhtml",
    "alt_sz_port_vehicles": "29200_51400002/1/service.xhtml",
    "alt_sz_port_air_pax": "29200_51400005/1/service.xhtml",
    "alt_sz_port_ferry": "29200_51400020/1/service.xhtml",
    "alt_sz_market_subject": "1485642496/1/service.xhtml",
    "alt_sz_stat_analysis": "29200_03302372/1/service.xhtml",
    "alt_sz_enterprise_year": "29200_03302396/1/service.xhtml",
    "alt_sz_reservoir_level": "1952552493/1/service.xhtml",
    "alt_sz_env_meteor": "675294854/1/service.xhtml",
    "alt_sz_climate_hist": "1287807159/1/service.xhtml",
    "alt_sz_ground_obs": "120238293/1/service.xhtml",
    "alt_typhoon_landfall_history": "29200_00903514/1/service.xhtml",
    "alt_typhoon_names": "29200_00903513/1/service.xhtml",
}
# 需要新钥匙（SZ_OPEN_DATA_APPKEY_NEW）的通道：2026-09-14 接口页订阅绑定在新钥匙应用名下
_SZ_NEW_KEY_CAPS = frozenset({
    "alt_sz_air_quality_daily", "alt_sz_air_quality_region", "alt_sz_reservoir_station",
    "alt_sz_reservoir_rain_day", "alt_sz_reservoir_rain_month",
    "alt_sz_house_area", "alt_sz_house_listing", "alt_sz_house_presale",
    "alt_sz_market_subject", "alt_sz_stat_analysis", "alt_sz_enterprise_year",
    "alt_sz_stat_monthly_batch2",
})
# 批3 系列级钥匙路由：口岸 4 新系列绑新钥匙应用（主钥匙 10001 实证）
_SZ_PORT_BATCH2_SIDS = {"29200_51400001", "29200_51400002", "29200_51400005", "29200_51400020"}
# batch2 系列级钥匙路由（新批订阅绑在新钥匙 0ecc2b46 应用名下，主钥匙 10001 实证）
_SZ_STAT_BATCH2_SIDS = {sid for _, sid in _SZ_STAT_SERIES_BATCH2}
_SZ_OPEN_BASE = "https://opendata.sz.gov.cn/api/"
_SZ_OPEN_PAGE_SIZE = 10000
_SZ_VISIBILITY_FULL_PAGE_LIMIT = 400  # 能见度全量模式页数天花板（400 万行）；超限=报批专项
_SZ_RES_LEVEL_TAIL_PAGES = 10  # 水位尾部页游标窗口（10 万行 ≈ 一周余量；日增实测 1-2 页）

# 能力 -> 通用拉取器路由（方法名仍按 _fetch_{cap} 约定在类尾 setattr 生成）
_SZ_OPEN_CAPS = frozenset({
    "alt_sz_stat_monthly", "alt_sz_port_monthly", "alt_sz_house_daily",
    "alt_sz_weather_warning", "alt_sz_marine_forecast", "alt_sz_visibility",
    "alt_sz_air_quality_daily", "alt_sz_air_quality_region",
    "alt_sz_reservoir_level", "alt_sz_reservoir_station",
    "alt_sz_reservoir_rain_day", "alt_sz_reservoir_rain_month",
    "alt_sz_house_area", "alt_sz_house_listing", "alt_sz_house_presale",
    "alt_sz_port_passengers", "alt_sz_port_vehicles", "alt_sz_port_air_pax", "alt_sz_port_ferry",
    "alt_sz_market_subject", "alt_sz_stat_analysis", "alt_sz_enterprise_year",
    "alt_sz_env_meteor", "alt_sz_climate_hist", "alt_sz_ground_obs",
    "alt_typhoon_landfall_history", "alt_typhoon_names",
})

_ALT_SZ_STAT_COLUMNS = ["series_code", "report_ym", "report_date", "zbmc", "dw", "xh", "val_month", "val_cum", "yoy_cum", "raw"]
_ALT_SZ_PORT_COLUMNS = ["series_code", "month_str", "month", "value", "release_time"]
_ALT_SZ_HOUSE_COLUMNS = ["series_code", "src_id", "tj_date", "zone", "report_catalog", "house_usage", "ks_num", "ks_area", "cj_num", "cj_area"]
_ALT_SZ_WARNING_COLUMNS = ["recid", "keyid", "tnumber", "signal_type", "signal_level", "issue_state", "district", "issue_content", "issue_ts", "crt_time", "crt_date", "underwriter", "autosent_flag", "autosent_count", "trace_flag", "trace_count", "sync_rownum"]
_ALT_SZ_VISIBILITY_COLUMNS = ["obtid", "obtname", "ddatetime", "ddate", "v", "v10m", "minv", "minvtime"]
_ALT_SZ_AIR_DAILY_COLUMNS = ["xh", "monitor_name", "monitor_time", "aqi", "level", "level_class", "level_color", "primary_pollutant", "health_note"]
_ALT_SZ_AIR_REGION_COLUMNS = ["id", "district_code", "district_name", "monitor_time", "aqi", "pm25", "pm10", "so2", "no2", "co", "o3", "grade", "primary_pollutant", "second_pollutant", "update_ts"]
_ALT_SZ_RES_STATION_COLUMNS = ["stcd", "stnm", "sttp"]
_ALT_SZ_RES_RAIN_DAY_COLUMNS = ["sjid", "date", "reservoir", "daily_rain"]
_ALT_SZ_RES_RAIN_MONTH_COLUMNS = ["sjid", "month", "reservoir", "avg_rain"]
_ALT_SZ_HOUSE_AREA_COLUMNS = ["id", "stat_date", "zone", "area_type", "cj_num", "cj_area"]
_ALT_SZ_HOUSE_LISTING_COLUMNS = ["xh", "house_name", "zone", "location", "usage", "usage2", "built_area", "publish_date", "organ", "verify_code", "full_serial"]
_ALT_SZ_HOUSE_PRESALE_COLUMNS = ["xh", "zone", "project", "buildings", "purpose", "presale_area", "house_suites", "issued_date", "pass_date", "issue_organ", "organ_name", "site_address", "parcel_code", "contract_no", "project_id", "house_id", "ad_years"]
_ALT_SZ_MARKET_SUBJECT_COLUMNS = ["year", "nzi_ent", "nzi_cap", "wzi_ent", "wzi_cap", "wzi_invest", "gsh_ent", "gsh_cap", "sy_ent", "nmzy_hz", "nmzy_cz"]
_ALT_SZ_STAT_ANALYSIS_COLUMNS = ["xh", "ny", "title", "body"]
_ALT_SZ_ENTERPRISE_YEAR_COLUMNS = ["year", "total", "wzi", "domestic", "private", "individual", "others1", "others2", "ext1", "ext2", "ext3", "ext4", "ext5", "ext6"]
_ALT_SZ_RES_LEVEL_COLUMNS = ["id", "stcd", "tm", "tdate", "rz"]
_ALT_SZ_ENV_METEOR_COLUMNS = ["id", "datetime", "area", "type", "wr_level", "wr_index", "evaluate", "c_level", "continue_time", "kq_rank", "zyfomite"]
_ALT_SZ_CLIMATE_HIST_COLUMNS = ["ddatetime", "ddate", "pressure", "rain", "temp", "humidity", "wind_speed", "wind_dir_deg", "wind_dir"]
_ALT_SZ_GROUND_OBS_COLUMNS = ["ddatetime", "ddate", "pressure", "rain", "wind_dir_deg", "temp", "humidity", "visibility", "wind_speed", "crt_time", "crt_date"]
_ALT_SZ_MARINE_COLUMNS = ["recid", "area_name", "ddatetime", "forecast_time", "is_next_day", "weather_status", "weather_pic", "wind_direct", "wind_speed", "wind_gust", "wind_gust_direct", "temp_max", "temp_min", "humidity", "humidity_max", "rain", "rain_min", "visibility", "visibility_min", "wave_level", "wave_height", "liusu", "qiya", "zwx", "yujing", "write_time"]
_ALT_LANDFALL_COLUMNS = ["id", "year", "tcno", "tc_en_name", "tc_cn_name", "land_no", "land_lev", "land_prov", "cyclone_num", "land_sum", "memo"]
_ALT_TYNAMES_COLUMNS = ["keyid", "name", "name_chn", "country", "start_time", "end_time", "name_meanings"]
_TBL_ALT_SZ_STAT = get_registry().table("market_alt_sz_stat_monthly")
_TBL_ALT_SZ_PORT = get_registry().table("market_alt_sz_port_monthly")
_TBL_ALT_SZ_HOUSE = get_registry().table("market_alt_sz_house_daily")
_TBL_ALT_SZ_WARNING = get_registry().table("market_alt_sz_weather_warning")
_TBL_ALT_SZ_MARINE = get_registry().table("market_alt_sz_marine_forecast")
_TBL_ALT_SZ_VISIBILITY = get_registry().table("market_alt_sz_visibility")
_TBL_ALT_SZ_AIR_DAILY = get_registry().table("market_alt_sz_air_quality_daily")
_TBL_ALT_SZ_AIR_REGION = get_registry().table("market_alt_sz_air_quality_region")
_TBL_ALT_SZ_RES_STATION = get_registry().table("market_alt_sz_reservoir_station")
_TBL_ALT_SZ_RES_RAIN_DAY = get_registry().table("market_alt_sz_reservoir_rain_day")
_TBL_ALT_SZ_RES_RAIN_MONTH = get_registry().table("market_alt_sz_reservoir_rain_month")
_TBL_ALT_SZ_HOUSE_AREA = get_registry().table("market_alt_sz_house_area")
_TBL_ALT_SZ_HOUSE_LISTING = get_registry().table("market_alt_sz_house_listing")
_TBL_ALT_SZ_HOUSE_PRESALE = get_registry().table("market_alt_sz_house_presale")
_TBL_ALT_SZ_MARKET_SUBJECT = get_registry().table("market_alt_sz_market_subject")
_TBL_ALT_SZ_STAT_ANALYSIS = get_registry().table("market_alt_sz_stat_analysis")
_TBL_ALT_SZ_ENTERPRISE_YEAR = get_registry().table("market_alt_sz_enterprise_year")
_TBL_ALT_SZ_RES_LEVEL = get_registry().table("market_alt_sz_reservoir_level")
_TBL_ALT_SZ_ENV_METEOR = get_registry().table("market_alt_sz_env_meteor")
_TBL_ALT_SZ_CLIMATE_HIST = get_registry().table("market_alt_sz_climate_hist")
_TBL_ALT_SZ_GROUND_OBS = get_registry().table("market_alt_sz_ground_obs")
_TBL_ALT_LANDFALL = get_registry().table("market_typhoon_landfall_history")
_TBL_ALT_TYNAMES = get_registry().table("market_typhoon_names")
_TBL_ALT_TYPHOON = get_registry().table("market_alt_typhoon_track")

# 统计月报列名兼容映射（各系列列名不一，取首个非空）
_STAT_MONTH_KEYS = ("BENYUE", "BNBJD", "BY")
_STAT_CUM_KEYS = ("BYZLJ", "BNBJDZLJ", "CZBYZLJ_JRSNTYYE")
_STAT_YOY_KEYS = ("LJTB", "CZLJTB_JRTBZC", "BYZLJPJ")

# macro_china_freight_index 列 -> (index_code, index_name)；
# BDI 不在本表（双源重叠以 macro_shipping_bdi 为准，历史更长且带涨跌幅）
_FREIGHT_INDEX_MAP: tuple[tuple[str, str, str], ...] = (
    ("波罗的海好望角型船运价指数BCI", "BCI", "波罗的海好望角型船运价指数"),
    ("灵便型船综合运价指数BHMI", "BHMI", "灵便型船综合运价指数"),
    ("波罗的海超级大灵便型船BSI指数", "BSI", "波罗的海超级大灵便型船指数"),
    ("HRCI国际集装箱租船指数", "HRCI", "国际集装箱租船指数"),
    ("油轮运价指数成品油运价指数BCTI", "BCTI", "成品油运价指数"),
    ("油轮运价指数原油运价指数BDTI", "BDTI", "原油运价指数"),
)

# 情绪面板通用列（与 sentiment_panel 表 INSERT_COLUMNS 对齐）
_CB_PANEL_COLUMNS = ("metric", "trade_date", "value", "value_classification", "source", "extra")

# 口岸月度 4 系列(51400001/2/5/20)与水库水位表(1952552493)已验证可调但未接线
# （DDL/解析器/任务缺），下批补——勿在此加入半接线 cap（2026-09-14）
_AKSHARE_ALT_CAPABILITIES = frozenset({
    "alt_stock_comment", "alt_shipping_index", "alt_typhoon_track",
    "alt_sz_stat_monthly", "alt_sz_port_monthly", "alt_sz_house_daily",
    "alt_sz_weather_warning", "alt_sz_marine_forecast", "alt_sz_visibility",
    "alt_sz_air_quality_daily", "alt_sz_air_quality_region",
    "alt_sz_reservoir_station",
    "alt_sz_reservoir_rain_day", "alt_sz_reservoir_rain_month",
    "alt_sz_house_area", "alt_sz_house_listing", "alt_sz_house_presale",
    "alt_sz_market_subject", "alt_sz_stat_analysis", "alt_sz_enterprise_year",
    "alt_sz_reservoir_level", "alt_sz_env_meteor", "alt_sz_climate_hist", "alt_sz_ground_obs",
    "alt_typhoon_landfall_history", "alt_typhoon_names", "cb_premium_median"})



def _tsv_safe(v) -> str:
    """TSV 值中和：Tab/CR/LF 替换为空格（String 列防污染）。"""
    return str(v or "").replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _num_or_safe(v):
    """数值优先（浮点可解析则返回 float），否则 TSV 安全字符串。"""
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return _tsv_safe(v)

def _norm_date(v) -> str | None:
    """规范化 akshare 日期为 'YYYY-MM-DD' 字符串（兼容 Timestamp/str/NaT）。"""
    if v is None:
        return None
    s = str(v)
    if s in ("NaT", "nan", "None", "", "nat"):
        return None
    return s[:10]


def _to_float(v) -> float | None:
    """安全转 float；NaN 防穿透返回 None（Nullable 列语义）。"""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f != f:  # NaN
        return None
    return f


def _to_int(v) -> int | None:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


class AkshareAltProvider(IngestProviderBase):
    """另类数据免注册直连源 provider（akshare 直连，无需密钥）。"""

    _connected: bool = False

    meta: IngestProviderMeta = IngestProviderMeta(
        name="akshare_alt",
        display_name="AKShare 另类数据源（千股千评/航运运价）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=60,
        capabilities=[
            # 快照幂等：无 symbols 概念（全市场表），不支持增量（接口无历史通道）
            CapabilityContract(
                "alt_stock_comment",
                supports_symbols_null=True,
                supports_incremental=False,
                supports_full_refresh=False,
                requires_date_range=False,
                expected_market="a_share",
                expected_variety="stock",
            ),
            CapabilityContract(
                "alt_shipping_index",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="macro",
                expected_variety="index",
            ),
            # 台风路径：深圳开放数据平台 API（appKey 走 secrets 通道，非 anonymous）
            CapabilityContract(
                "alt_typhoon_track",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
            ),
            # 深圳开放数据批量源（2026-09-14）：spec 驱动通用拉取器
            CapabilityContract("alt_sz_stat_monthly", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_port_monthly", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_house_daily", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_sz_weather_warning", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_sz_marine_forecast", supports_symbols_null=True, requires_date_range=True),
            # 能见度探测：服务 1580458478 无过滤参数，provider 内二分定位起始页做增量
            CapabilityContract("alt_sz_visibility", supports_symbols_null=True, requires_date_range=True),
            # 批 2（2026-09-14 深夜，新钥匙通道 SZ_OPEN_DATA_APPKEY_NEW）
            CapabilityContract("alt_sz_air_quality_daily", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_sz_air_quality_region", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_sz_reservoir_station", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_reservoir_rain_day", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_reservoir_rain_month", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_house_area", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_sz_house_listing", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_house_presale", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_market_subject", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_stat_analysis", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_enterprise_year", supports_symbols_null=True, supports_incremental=False),
            # 批3（2026-09-14 深夜）：水位大表二分增量/环境气象/气候历史/地面观测
            CapabilityContract("alt_sz_reservoir_level", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_sz_env_meteor", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_climate_hist", supports_symbols_null=True, supports_incremental=False),
            CapabilityContract("alt_sz_ground_obs", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("alt_typhoon_landfall_history", supports_symbols_null=True,
                               supports_incremental=False, requires_date_range=False),
            CapabilityContract("alt_typhoon_names", supports_symbols_null=True,
                               supports_incremental=False, requires_date_range=False),
            CapabilityContract("cb_premium_median", supports_symbols_null=True,
                               supports_incremental=True, requires_date_range=True),
        ],
        known_issues=[
            "千股千评接口仅返回当日快照，无历史回补通道（每日累积模式）",
            "akshare 上游网页改版风险 -> alt_source_health_manager 探针兜底",
            "台风/深圳源接口要求 appKey 已订阅（errorCode 10001=未订阅），依赖 Owner 账号订阅状态",
        ],
    )

    # ---- 探活/连接/断开（与 akshare 主 provider 同约定） ----

    def connect(self) -> bool:
        """无持久连接资源：akshare 可导入即连立（lazy import 在 fetch 时发生）。"""
        self._connected = self.health_check()
        return self._connected

    def health_check(self) -> bool:
        try:
            import akshare  # noqa: F401

            return True
        except ImportError as e:
            self._log.warning(f"akshare_alt 探活失败（akshare 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """无持久连接资源，仅重置状态。"""

    # ---- 拉取入口 ----

    def _fetch_cb_premium_median(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """转债转股溢价率中位数（集思录 bond_cb_jsl 全市场）→ c1_market.sentiment_panel。

        metric='cb_conversion_premium_median'；F25 风险偏好温度计数据源。
        cookie 经 get_secret_or_default('CB_JSL_COOKIE')（.env 可选登记；匿名可取部分数据，
        覆盖不足时 F25 信号自然 warmup）。
        """
        import akshare as ak

        t0 = time.monotonic()
        table = payload.table or get_registry().table("market_sentiment_panel")
        try:
            cookie = get_secret_or_default("CB_JSL_COOKIE") or None
            df = self._call_with_policy(ak.bond_cb_jsl, policy, cookie) if cookie else self._call_with_policy(ak.bond_cb_jsl, policy)
            if df is None or len(df) == 0:
                yield FetchResult(
                    table=table, columns=list(_CB_PANEL_COLUMNS), rows=[], last_key="",
                    elapsed_sec=time.monotonic() - t0, error="bond_cb_jsl 返回空",
                )
                return
            prem = df["转股溢价率"].astype(str).str.rstrip("%")
            prem = pd.to_numeric(prem, errors="coerce").dropna()
            if prem.empty:
                yield FetchResult(
                    table=table, columns=list(_CB_PANEL_COLUMNS), rows=[], last_key="",
                    elapsed_sec=time.monotonic() - t0, error="转股溢价率列解析为空",
                )
                return
            d = (payload.end or datetime.date.today()).strftime("%Y-%m-%d")
            median = round(float(prem.median()), 4)
            row = (
                "cb_conversion_premium_median", d, median,
                "overheat" if median > 50 else ("freezing" if median < 10 else "normal"),
                "akshare_alt.bond_cb_jsl", f"coverage={len(prem)}",
            )
            yield FetchResult(
                table=table, columns=list(_CB_PANEL_COLUMNS), rows=[row], last_key=d,
                elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"cb_premium_median 获取失败: {e}")
            yield FetchResult(
                table=table, columns=list(_CB_PANEL_COLUMNS), rows=[], last_key="",
                elapsed_sec=time.monotonic() - t0, error=str(e),
            )

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由；未知能力 yield error。"""
        cap = (payload.extra or {}).get("capability")
        if cap in _AKSHARE_ALT_CAPABILITIES:
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

    # ---- 千股千评全表日快照 ----

    def _fetch_alt_stock_comment(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """千股千评全表日快照，写入 c1_market.alt_stock_comment。

        akshare stock_comment_em 返回当日全市场约 5200 行（关注指数/综合得分/机构参与度/
        排名及变动）。trade_date 以接口自带"交易日"列为准（PIT 锚，常为 T-1），
        缺失时回退 payload.end；ReplacingMergeTree 按 (trade_date, symbol) 幂等。
        """
        import akshare as ak

        table = payload.table or _TBL_ALT_STOCK_COMMENT
        t0 = time.monotonic()
        try:
            df = self._call_with_policy(ak.stock_comment_em, policy)
            if df is None or len(df) == 0:
                yield FetchResult(
                    table=table,
                    columns=_ALT_COMMENT_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.monotonic() - t0,
                    error="stock_comment_em 返回空",
                )
                return
            fallback_date = payload.end.strftime("%Y-%m-%d") if payload.end else None
            rows: list[tuple] = []
            trade_dates: list[str] = []
            for _, r in df.iterrows():
                symbol = str(r.get("代码", "") or "").strip()
                if not symbol:
                    continue
                trade_date = _norm_date(r.get("交易日")) or fallback_date
                if not trade_date:
                    continue
                trade_dates.append(trade_date)
                rows.append(
                    (
                        trade_date,
                        symbol,
                        str(r.get("名称", "") or "").strip(),
                        _to_float(r.get("机构参与度")),
                        _to_float(r.get("综合得分")),
                        _to_float(r.get("上升")),
                        _to_int(r.get("目前排名")),
                        _to_float(r.get("关注指数")),
                        _to_float(r.get("主力成本")),
                    )
                )
            last_key = max(trade_dates) if trade_dates else ""
            yield FetchResult(
                table=table,
                columns=_ALT_COMMENT_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"alt_stock_comment 获取失败: {e}")
            yield FetchResult(
                table=table,
                columns=_ALT_COMMENT_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=str(e),
            )

    # ---- 航运运价指数长表 ----

    @staticmethod
    def _shipping_start_guard(payload: FetchPayload) -> str | None:
        return payload.start.strftime("%Y-%m-%d") if payload.start else None

    def _fetch_alt_shipping_index(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """航运运价指数长表，写入 c1_market.alt_shipping_index。

        双源合流（增量按 payload.start 过滤；全量取全部）：
        - ak.macro_shipping_bdi：BDI 1988-10 起，含日涨跌幅
        - ak.macro_china_freight_index：BCI/BSI/BHMI/HRCI/BCTI/BDTI 约 2006 起（BDI 列弃用免重）
        """
        import akshare as ak

        table = payload.table or _TBL_ALT_SHIPPING_INDEX
        t0 = time.monotonic()
        # 全量模式（incremental=False）忽略 start：scheduler 对全量任务也传 start=月初
        # （_compute_start_date 无 None 路径），若照单过滤则"全量刷新"名不副实；
        # 真全量周度重拉约 1.45 万行，ReplacingMergeTree 同键替换幂等，代价可忽略
        start_str = self._shipping_start_guard(payload) if payload.incremental else None
        rows: list[tuple] = []
        try:
            # 源1：BDI（金十源，1988 起）
            df = self._call_with_policy(ak.macro_shipping_bdi, policy)
            if df is not None and len(df) > 0:
                for _, r in df.iterrows():
                    trade_date = _norm_date(r.get("日期"))
                    value = _to_float(r.get("最新值"))
                    if not trade_date or value is None:
                        continue
                    if start_str and trade_date < start_str:
                        continue
                    rows.append(
                        (
                            trade_date,
                            "BDI",
                            "波罗的海综合运价指数",
                            value,
                            _to_float(r.get("涨跌幅")),
                            "macro_shipping_bdi",
                        )
                    )
            else:
                self._log.warning("macro_shipping_bdi 返回空（BDI 断供？）")

            # 源2：六指数（约 2006 起；BDI 列弃用免重）
            df2 = self._call_with_policy(ak.macro_china_freight_index, policy)
            if df2 is not None and len(df2) > 0:
                for _, r in df2.iterrows():
                    trade_date = _norm_date(r.get("截止日期"))
                    if not trade_date:
                        continue
                    if start_str and trade_date < start_str:
                        continue
                    for col, code, name in _FREIGHT_INDEX_MAP:
                        value = _to_float(r.get(col))
                        if value is None:
                            continue
                        rows.append((trade_date, code, name, value, None, "macro_china_freight_index"))
            else:
                self._log.warning("macro_china_freight_index 返回空（六指数断供？）")

            rows.sort(key=lambda t: (t[1], t[0]))
            last_key = max((t[0] for t in rows), default="")
            yield FetchResult(
                table=table,
                columns=_ALT_SHIPPING_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.monotonic() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"alt_shipping_index 获取失败: {e}")
            yield FetchResult(
                table=table,
                columns=_ALT_SHIPPING_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.monotonic() - t0,
                error=str(e),
            )

    # ---- 台风路径（深圳开放数据平台 API，appKey 通道） ----

    @staticmethod
    def _unwrap_sz_api(payload_obj):
        """平台成功响应包裹层防御式解包。

        订阅生效前无法取得成功样例，兼容常见形态：裸 list / {result|data|rows|
        list|content|records: [...]} / 一层嵌套 dict 后再挂上述键。解析失败返回
        空列表（上层按 0 行处理，不伪装成功）。
        """
        cur = payload_obj
        for _ in range(2):
            if isinstance(cur, list):
                return cur
            if isinstance(cur, dict):
                for key in ("result", "data", "rows", "list", "content", "records"):
                    v = cur.get(key)
                    if isinstance(v, list):
                        return v
                    if isinstance(v, dict):
                        cur = v
                        break
                else:
                    return []
        return []

    def _sz_api_get(self, url: str, params: dict):
        """单次 GET 请求深圳开放数据平台数据接口（供 _call_with_policy 重试包裹）。"""
        import requests

        resp = requests.get(url, params=params, timeout=60,
                            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                   "AppleWebKit/537.36 zephyr-alt-provider"})
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _typhoon_row(raw: dict) -> tuple | None:
        """单行 dict -> 列序元组；缺 keyid 返回 None（跳过）。"""
        keyid = _to_int(raw.get("KEYID"))
        if keyid is None:
            return None
        crt_time = str(raw.get("CRTTIME") or "")
        return (
            keyid,
            _to_int(raw.get("TCIDX")) or 0,
            str(raw.get("TCNO") or ""),
            str(raw.get("CNAME") or ""),
            str(raw.get("ENAME") or ""),
            str(raw.get("TCLEVEL") or ""),
            str(raw.get("ISSUEDATE") or ""),
            str(raw.get("FORECASTDATE") or ""),
            _to_int(raw.get("INTERVALTIME")) or 0,
            _to_float(raw.get("LONGITUDE")) or 0.0,
            _to_float(raw.get("LATITUDE")) or 0.0,
            _to_float(raw.get("AIRPRESSURE")) or 0.0,
            _to_float(raw.get("WIND")) or 0.0,
            _to_float(raw.get("GUST")) or 0.0,
            _to_float(raw.get("MOVESPEED")) or 0.0,
            str(raw.get("MOVEDIR") or ""),
            _to_float(raw.get("SIXRADII")) or 0.0,
            _to_float(raw.get("SEVENRADII")) or 0.0,
            _to_float(raw.get("EIGHTRADII")) or 0.0,
            _to_float(raw.get("TENRADII")) or 0.0,
            str(raw.get("ISSUETYPE") or ""),
            crt_time,
            crt_time[:10] or "1970-01-01",
            "sz_api_1049994100",
        )

    def _fetch_alt_typhoon_track(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """台风路径结构化数据，写入 c1_market.alt_typhoon_track。

        深圳开放数据平台 API（appKey 经 get_service_secret 读取，禁裸 getenv）。
        增量按 crt_date（平台入库日期）过滤：startDate=last_key；全量不带日期翻页。
        KEYID 平台全局唯一，ReplacingMergeTree 幂等重放。
        """
        table = payload.table or _TBL_ALT_TYPHOON
        t0 = time.monotonic()
        try:
            app_key = get_secret_or_default("SZ_OPEN_DATA_APPKEY")
        except Exception as e:  # noqa: BLE001 — 密钥缺失即断供
            yield FetchResult(table=table, columns=_ALT_TYPHOON_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error=f"appKey 缺失: {e}")
            return
        if not app_key:
            yield FetchResult(table=table, columns=_ALT_TYPHOON_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error="SZ_OPEN_DATA_APPKEY 为空")
            return

        base_params = {"appKey": app_key, "rows": _SZ_TYPHOON_PAGE_SIZE}
        if payload.incremental and payload.start:
            base_params["startDate"] = payload.start.strftime("%Y%m%d")
        rows_out: list[tuple] = []
        seen_first: int | None = None
        try:
            for page in range(1, _SZ_TYPHOON_MAX_PAGES + 1):
                resp = self._call_with_policy(
                    self._sz_api_get, policy, _SZ_TYPHOON_URL, {**base_params, "page": page}
                )
                if isinstance(resp, dict) and resp.get("errorCode"):
                    yield FetchResult(table=table, columns=_ALT_TYPHOON_COLUMNS, rows=[],
                                      last_key="", elapsed_sec=time.monotonic() - t0,
                                      error=f"平台错误 {resp.get('errorCode')}: {resp.get('message')}")
                    return
                batch = self._unwrap_sz_api(resp)
                if not batch:
                    break
                for raw in batch:
                    row = self._typhoon_row(raw)
                    if row is not None:
                        rows_out.append(row)
                # 服务端忽略分页的防御：首页首条重复即止（防死循环刷同一批）
                first_keyid = _to_int(batch[0].get("KEYID")) if isinstance(batch[0], dict) else None
                if page > 1 and first_keyid is not None and first_keyid == seen_first:
                    break
                seen_first = first_keyid
                if len(batch) < _SZ_TYPHOON_PAGE_SIZE:
                    break
                time.sleep(0.5)
            rows_out.sort(key=lambda t: t[0])
            last_key = max((t[21][:10] for t in rows_out if t[21]), default="")
            yield FetchResult(table=table, columns=_ALT_TYPHOON_COLUMNS, rows=rows_out,
                              last_key=last_key, elapsed_sec=time.monotonic() - t0)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"alt_typhoon_track 获取失败: {e}")
            yield FetchResult(table=table, columns=_ALT_TYPHOON_COLUMNS, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error=str(e))

    # ---- 深圳开放数据平台批量源（spec 驱动，2026-09-14） ----

    def _sz_open_fetch_rows(self, policy: SourcePolicy, api_ctx: str,
                            extra: dict | None = None, max_pages: int = 40,
                            app_key: str | None = None) -> list[dict]:
        """通用分页拉取（appKey/限频/重试统一；忽略分页防御同台风通道）。

        app_key=None 时用主钥匙 SZ_OPEN_DATA_APPKEY；批 2 系列绑新钥匙
        SZ_OPEN_DATA_APPKEY_NEW（0ecc2b46 应用），由调用方显式传入。
        """
        if not app_key:
            app_key = get_secret_or_default("SZ_OPEN_DATA_APPKEY")
        if not app_key:
            raise ValueError("SZ_OPEN_DATA_APPKEY 为空（.env 缺失或未配置）")
        if "/service.xhtml" not in api_ctx:
            api_ctx = api_ctx + "/1/service.xhtml"
        url = _SZ_OPEN_BASE + api_ctx
        base = {"appKey": app_key, "rows": _SZ_OPEN_PAGE_SIZE}
        if extra:
            base.update(extra)
        all_rows: list[dict] = []
        seen_first = None
        for page in range(1, max_pages + 1):
            resp = self._call_with_policy(self._sz_api_get, policy, url, {**base, "page": page})
            if isinstance(resp, dict) and resp.get("errorCode"):
                raise ValueError(f"平台错误 {resp.get('errorCode')}: {resp.get('message')}")
            batch = self._unwrap_sz_api(resp)
            if not batch:
                break
            all_rows.extend(batch)
            if isinstance(batch[0], dict):
                first = _to_int(batch[0].get("KEYID")) or _to_int(batch[0].get("RECID")) or _to_int(batch[0].get("ID"))
            else:
                first = None
            if page > 1 and first is not None and first == seen_first:
                break
            seen_first = first
            if len(batch) < _SZ_OPEN_PAGE_SIZE:
                break
            time.sleep(0.4)
        return all_rows

    def _sz_get_total(self, policy: SourcePolicy, api_ctx: str) -> int | None:
        """首页小页探测取平台 total（失败返回 None，上层退化为全量翻页）。"""
        app_key = get_secret_or_default("SZ_OPEN_DATA_APPKEY")
        if not app_key:
            return None
        if "/service.xhtml" not in api_ctx:
            api_ctx = api_ctx + "/1/service.xhtml"
        url = _SZ_OPEN_BASE + api_ctx
        try:
            resp = self._call_with_policy(self._sz_api_get, policy, url,
                                          {"appKey": app_key, "page": 1, "rows": 1})
            if isinstance(resp, dict) and not resp.get("errorCode"):
                return _to_int(resp.get("total"))
        except Exception:  # noqa: BLE001 — 探测失败不致命
            pass
        return None

    def _sz_open_fetch_rows_from(self, policy: SourcePolicy, api_ctx: str, start_page: int = 1,
                                 last_page_cap: int | None = None,
                                 extra: dict | None = None) -> list[dict]:
        """从指定起始页翻到尾的变体（无过滤大表专用；忽略分页防御同主通道）。

        last_page_cap=None：翻到批次不足页即止（增量定位后场景，尾部是终点）；
        last_page_cap=N：最多翻到 N 页（全量模式末页封顶，防历史偶发扩表翻车）。
        """
        app_key = get_secret_or_default("SZ_OPEN_DATA_APPKEY")
        if not app_key:
            raise ValueError("SZ_OPEN_DATA_APPKEY 为空（.env 缺失或未配置）")
        if "/service.xhtml" not in api_ctx:
            api_ctx = api_ctx + "/1/service.xhtml"
        url = _SZ_OPEN_BASE + api_ctx
        base = {"appKey": app_key, "rows": _SZ_OPEN_PAGE_SIZE}
        if extra:
            base.update(extra)
        all_rows: list[dict] = []
        seen_first_dd = None
        page = max(1, start_page)
        while page <= (last_page_cap if last_page_cap else page + 1):
            resp = self._call_with_policy(self._sz_api_get, policy, url, {**base, "page": page})
            if isinstance(resp, dict) and resp.get("errorCode"):
                raise ValueError(f"平台错误 {resp.get('errorCode')}: {resp.get('message')}")
            batch = self._unwrap_sz_api(resp)
            if not batch:
                break
            all_rows.extend(batch)
            first_dd = str(batch[0].get("DDATETIME") or "") if isinstance(batch[0], dict) else ""
            if page > start_page and first_dd and first_dd == seen_first_dd:
                break  # 服务端忽略分页防御：跨页首行重复即止
            seen_first_dd = first_dd
            if len(batch) < _SZ_OPEN_PAGE_SIZE:
                break  # 不满页 = 已到尾（升序全序的尾部终点）
            time.sleep(0.4)
            page += 1
        return all_rows

    def _sz_find_start_page(self, policy: SourcePolicy, api_ctx: str, total: int,
                            target_date: str) -> int | None:
        """无过滤参数大表的增量起始页二分定位（升序 DDATETIME 全序）。

        返回首个 DDATETIME >= target_date 的页号；全表早于目标日返回 None
        （上层从尾页开始拉，靠幂等去重）；异常返回 None（退化为全量翻页）。
        """
        app_key = get_secret_or_default("SZ_OPEN_DATA_APPKEY")
        if not app_key:
            return None
        if "/service.xhtml" not in api_ctx:
            api_ctx = api_ctx + "/1/service.xhtml"
        url = _SZ_OPEN_BASE + api_ctx
        last_page = max(1, (total + _SZ_OPEN_PAGE_SIZE - 1) // _SZ_OPEN_PAGE_SIZE)

        def page_first_ddatetime(page: int) -> str | None:
            try:
                resp = self._call_with_policy(self._sz_api_get, policy, url,
                                              {"appKey": app_key, "page": page, "rows": _SZ_OPEN_PAGE_SIZE})
                if isinstance(resp, dict) and resp.get("errorCode"):
                    return None
                batch = self._unwrap_sz_api(resp)
                if not batch or not isinstance(batch[0], dict):
                    return None
                return str(batch[0].get("DDATETIME") or "")
            except Exception:  # noqa: BLE001 — 探测失败退化为全量
                return None

        lo, hi = 1, last_page
        # 边界快速退出：首页已 >= 目标（全量翻页）；尾页 < 目标（无新数据）
        first = page_first_ddatetime(1)
        if first is None:
            return None
        if first >= target_date:
            return 1
        last = page_first_ddatetime(last_page)
        if last is not None and last < target_date:
            return last_page  # 无新数据：从尾页起拉（0 行新增，幂等去重兜底）
        # 二分：找最小页使首行 DDATETIME >= target_date
        while lo < hi:
            mid = (lo + hi) // 2
            v = page_first_ddatetime(mid)
            if v is None:
                return None
            if v >= target_date:
                hi = mid
            else:
                lo = mid + 1
            time.sleep(0.3)
        return lo

    @staticmethod
    def _stat_row(series: str, raw: dict) -> tuple | None:
        """统计月报行 -> 长表元组；ZBMC 缺失跳过。"""
        ym = str(raw.get("NY") or "")
        zbmc = str(raw.get("ZBMC") or "").strip()
        if not ym or not zbmc:
            return None
        val_month = val_cum = yoy = None
        for k in _STAT_MONTH_KEYS:
            v = _to_float(raw.get(k))
            if v is not None:
                val_month = v
                break
        for k in _STAT_CUM_KEYS:
            v = _to_float(raw.get(k))
            if v is not None:
                val_cum = v
                break
        for k in _STAT_YOY_KEYS:
            v = _to_float(raw.get(k))
            if v is not None:
                yoy = v
                break
        report_date = f"{ym[:4]}-{ym[4:6]}-01" if len(ym) >= 6 else "1970-01-01"
        return (series, ym, report_date, zbmc, str(raw.get("DW") or ""),
                _to_int(raw.get("XH")) or 0, val_month, val_cum, yoy,
                json.dumps(raw, ensure_ascii=False))

    @staticmethod
    def _port_row(series: str, raw: dict) -> tuple | None:
        m = re.match(r"(\d{4})年(\d{1,2})月", str(raw.get("MONTH") or ""))
        if not m:
            # 客船进出港族无 MONTH 字段（TJSJ=统计月，GXSJ=更新时间）
            m2 = re.match(r"(\d{4})年(\d{1,2})月", str(raw.get("TJSJ") or ""))
            if not m2:
                return None
            month = f"{m2.group(1)}-{int(m2.group(2)):02d}-01"
            val = _to_float(raw.get("KCJCG"))
            if val is None:
                return None
            return (series, str(raw.get("TJSJ") or ""), month, val,
                    str(raw.get("GXSJ") or ""))
        month = f"{m.group(1)}-{int(m.group(2)):02d}-01"
        if series == "port_teu":
            val = _to_float(raw.get("TEU"))
        elif series == "port_goods":
            val = _to_float(raw.get("GOODS_QUANTITY"))
        elif series == "port_air":
            val = _to_float(raw.get("AIR_GOODS_QUANTITY"))
        elif series == "port_pax":
            val = _to_float(raw.get("CUSTOMS_NUMBER"))
        elif series == "port_vehicles":
            val = _to_float(raw.get("CAR_NUMBER"))
        elif series == "port_airpax":
            val = _to_float(raw.get("AIRPORT_CUSTOMS_NUMBER"))
        else:
            return None
        if val is None:
            return None
        return (series, str(raw.get("MONTH") or ""), month, val, str(raw.get("RELEASE_TIME") or ""))

    @staticmethod
    def _house_row(series: str, raw: dict) -> tuple | None:
        src_id = str(raw.get("ID") or "")
        tj = _norm_date(raw.get("TJ_DATE"))
        if not src_id or not tj:
            return None
        return (series, src_id, tj, str(raw.get("ZONE") or ""),
                str(raw.get("REPORTCATALOG") or ""), str(raw.get("HOUSE_USAGE2") or ""),
                _to_int(raw.get("KS_NUM")),
                _to_float(raw.get("KS_AREA")),
                _to_float(raw.get("CJ_NUM")) or 0.0,
                _to_float(raw.get("CJ_AREA")) or 0.0)

    @staticmethod
    def _warning_row(raw: dict) -> tuple | None:
        recid = _to_int(raw.get("RECID"))
        if recid is None:
            return None
        crt_time = str(raw.get("CRTTIME") or "")
        return (recid, _to_int(raw.get("KEYID")) or 0, _to_int(raw.get("TNUMBER")) or 0,
                str(raw.get("SIGNALTYPE") or ""), str(raw.get("SIGNALLEVEL") or ""),
                str(raw.get("ISSUESTATE") or ""), str(raw.get("DISTRICT") or ""),
                str(raw.get("ISSUECONTENT") or ""), str(raw.get("ISSUETIME") or ""),
                crt_time, crt_time[:10] or "1970-01-01",
                str(raw.get("UNDERWRITER") or ""), _to_int(raw.get("AUTOSENTFLAG")) or 0,
                _to_int(raw.get("AUTOSENTCOUNT")) or 0, _to_int(raw.get("TRACEFLAG")) or 0,
                _to_int(raw.get("TRACOUNT")) or 0, str(raw.get("SYNC_ROWNUM") or ""))

    @staticmethod
    def _visibility_row(raw: dict) -> tuple | None:
        """能见度行 -> 列序元组；缺 OBTID/DDATETIME 跳过。ddate 派生日期分区键。"""
        obtid = str(raw.get("OBTID") or "")
        ddatetime = str(raw.get("DDATETIME") or "")
        if not obtid or not ddatetime:
            return None
        return (obtid, str(raw.get("OBTNAME") or ""), ddatetime, ddatetime[:10] or "1970-01-01",
                _to_float(raw.get("V")), _to_float(raw.get("V10M")),
                _to_float(raw.get("MINV")), _to_int(raw.get("MINVTIME")))

    @staticmethod
    def _marine_row(raw: dict) -> tuple | None:
        recid = _to_int(raw.get("RECID"))
        if recid is None:
            return None
        wt = str(raw.get("WRITETIME") or "")
        return (recid, str(raw.get("AREANAME") or ""), str(raw.get("DDATETIME") or ""),
                str(raw.get("FORECASTTIME") or ""), _to_int(raw.get("ISNEXTDAY")) or 0,
                str(raw.get("WEATHERSTATUS") or ""), str(raw.get("WEATHERPIC") or ""),
                str(raw.get("WINDDIRECT") or ""), _to_float(raw.get("WINDSPEED")) or 0.0,
                _to_float(raw.get("WINDGUST")) or 0.0, str(raw.get("WINDGUSTDIRECT") or ""),
                _to_float(raw.get("MAXTEMPERATURE")) or 0.0, _to_float(raw.get("MINTEMPERATURE")) or 0.0,
                _to_float(raw.get("HUMIDITY")) or 0.0, _to_float(raw.get("MAXHUMIDITY")) or 0.0,
                _to_float(raw.get("RAIN")) or 0.0, _to_float(raw.get("MINRAIN")) or 0.0,
                _to_float(raw.get("VISI")) or 0.0, _to_float(raw.get("MINIVISI")) or 0.0,
                str(raw.get("WAVELEVEL") or ""), _to_float(raw.get("WAVEHEIGHT")) or 0.0,
                _to_float(raw.get("LIUSU")) or 0.0, _to_float(raw.get("QIYA")) or 0.0,
                _to_float(raw.get("ZWX")) or 0.0, str(raw.get("YUJING") or ""), wt)

    @staticmethod
    def _air_daily_row(raw: dict) -> tuple | None:
        xh = str(raw.get("XH") or "")
        if not xh:
            return None
        return (xh, str(raw.get("JCDWMC") or ""), str(raw.get("JCSJ") or ""),
                _to_int(raw.get("AQI")), str(raw.get("ZSLB") or ""),
                str(raw.get("ZSJB") or ""), str(raw.get("YSJB") or ""),
                str(raw.get("SYWRW") or ""), str(raw.get("JKYXZK") or ""))

    @staticmethod
    def _air_region_row(raw: dict) -> tuple | None:
        rid = str(raw.get("ID") or "")
        if not rid:
            return None
        return (rid, str(raw.get("CDBM") or ""), str(raw.get("CDMC") or ""),
                str(raw.get("JCSJ") or ""), _to_float(raw.get("AQI")),
                _to_float(raw.get("PM25")), _to_float(raw.get("PM10")),
                _to_float(raw.get("SO2")), _to_float(raw.get("NO2")),
                _to_float(raw.get("CO")), _to_float(raw.get("O3")),
                str(raw.get("KQDJ") or ""), str(raw.get("SYWRW") or ""),
                str(raw.get("CBWRW") or ""), str(raw.get("UPDATETIME") or ""))

    @staticmethod
    def _res_station_row(raw: dict) -> tuple | None:
        stcd = str(raw.get("STCD") or "")
        if not stcd:
            return None
        return (stcd, str(raw.get("STNM") or ""), str(raw.get("STTP") or ""))

    @staticmethod
    def _res_rain_day_row(raw: dict) -> tuple | None:
        sjid = _to_int(raw.get("SJID"))
        if sjid is None:
            return None
        return (sjid, str(raw.get("SJ") or ""), str(raw.get("SKMC") or ""),
                _to_float(raw.get("RJYL")))

    @staticmethod
    def _res_rain_month_row(raw: dict) -> tuple | None:
        sjid = _to_int(raw.get("SJID"))
        if sjid is None:
            return None
        return (sjid, str(raw.get("YF") or ""), str(raw.get("SKMC") or ""),
                _to_float(raw.get("PJJYL")))

    @staticmethod
    def _house_area_row(raw: dict) -> tuple | None:
        rid = str(raw.get("ID") or "")
        if not rid:
            return None
        return (rid, _norm_date(raw.get("TJ_DATE")) or "1970-01-01",
                str(raw.get("ZONE") or ""), str(raw.get("AREA_TYPE") or ""),
                _to_float(raw.get("CJ_NUM")) or 0.0, _to_float(raw.get("CJ_AREA")))

    @staticmethod
    def _house_listing_row(raw: dict) -> tuple | None:
        xh = str(raw.get("XH") or "")
        if not xh:
            return None
        return (xh, str(raw.get("HOUSE_NAME") or ""), str(raw.get("ZONE") or ""),
                str(raw.get("LU_LOCATION") or ""), str(raw.get("HOUSE_USAGE") or ""),
                str(raw.get("HOUSE_USAGE2") or ""), _to_float(raw.get("BUILT_IN_AREA")),
                str(raw.get("PUBLISH_DATE") or ""), str(raw.get("ORGAN_NAME") or ""),
                str(raw.get("VERIFY_CODE") or ""), str(raw.get("FULL_SERIAL_NO") or ""))

    @staticmethod
    def _house_presale_row(raw: dict) -> tuple | None:
        xh = str(raw.get("XH") or "")
        if not xh:
            return None
        return (xh, str(raw.get("ZONE") or ""), str(raw.get("PROJECTNAME") or ""),
                str(raw.get("BUILDINGNAMES") or ""), str(raw.get("PURPOSE") or ""),
                _to_float(raw.get("PRESELLAREA")), _to_int(raw.get("HOUSESUITES")),
                str(raw.get("ISSUEDDATE") or ""), str(raw.get("PASSDATE") or ""),
                str(raw.get("ISSUEORGAN") or ""), str(raw.get("ORGAN_NAME") or ""),
                str(raw.get("SITEADDRESS") or ""), str(raw.get("PARCEL_CODE") or ""),
                str(raw.get("FULL_CONTRACT_NO") or ""), str(raw.get("STRPREPROJECTID") or ""),
                str(raw.get("HOUSEID") or ""), str(raw.get("ADYEARS") or ""))

    @staticmethod
    def _market_subject_row(raw: dict | None) -> tuple | None:
        if not isinstance(raw, dict):
            return None
        year = _to_int(raw.get("ND"))
        if year is None:
            return None
        return (year, _to_int(raw.get("NZQYDQYHS")), _to_float(raw.get("NZQYDZCZB")),
                _to_int(raw.get("WSTZQYDQYHS")), _to_float(raw.get("WSTZQYDZCZB")),
                _to_float(raw.get("WSTZQYDTZZE")), _to_int(raw.get("GTGSHDHS")),
                _to_float(raw.get("GTGSHDZJSE")), _to_int(raw.get("SYQYDQYHS")),
                _to_int(raw.get("NMZYHZSDHS")), _to_float(raw.get("NMZYHZSDCZZE")))

    @staticmethod
    def _stat_analysis_row(raw: dict | None) -> tuple | None:
        if not isinstance(raw, dict):
            return None  # 平台 data 数组混入 null 元素（2026-09-14 实测）
        xh = str(raw.get("XH") or "")
        if not xh:
            return None
        return (xh, str(raw.get("NY") or ""), str(raw.get("BT") or ""),
                str(raw.get("ZW") or ""))

    @staticmethod
    def _enterprise_year_row(raw: dict | None) -> tuple | None:
        if not isinstance(raw, dict):
            return None
        year = _to_int(raw.get("NF"))
        if year is None:
            return None
        return (year, _to_int(raw.get("QYZS")), _to_int(raw.get("WZQY")),
                _to_int(raw.get("DSCY")), _to_int(raw.get("SYQY")),
                _to_int(raw.get("NZQY")), _to_int(raw.get("DYCY")), _to_int(raw.get("DECY")),
                _to_int(raw.get("WY10002999")) if _to_int(raw.get("WY10002999")) is not None else None,
                _to_int(raw.get("WY30004999")) if _to_int(raw.get("WY30004999")) is not None else None,
                _to_int(raw.get("WY50009999")) if _to_int(raw.get("WY50009999")) is not None else None,
                _to_int(raw.get("WY100499")) if _to_int(raw.get("WY100499")) is not None else None,
                _to_int(raw.get("WY500999")) if _to_int(raw.get("WY500999")) is not None else None,
                _to_int(raw.get("YYYS1")) if _to_int(raw.get("YYYS1")) is not None else None)

    @staticmethod
    def _res_level_row(raw: dict | None) -> tuple | None:
        """水库水位行（服务 1952552493，主钥匙，7630 万行，无过滤参数）。"""
        if not isinstance(raw, dict):
            return None
        rid = str(raw.get("ID") or "")
        tm = str(raw.get("TM") or "")
        if not rid or not tm:
            return None
        return (rid, str(raw.get("STCD") or ""), tm, tm[:10] or "1970-01-01",
                _to_float(raw.get("RZ")))

    @staticmethod
    def _env_meteor_row(raw: dict | None) -> tuple | None:
        """环境气象预报行（服务 675294854，环境气象等级/污染扩散评价）。"""
        if not isinstance(raw, dict):
            return None
        rid = str(raw.get("ID") or "")
        if not rid:
            return None
        return (rid, str(raw.get("DATETIME") or ""), str(raw.get("AREA") or ""),
                str(raw.get("TYPE") or ""), str(raw.get("WRLEVEL") or ""),
                str(raw.get("WRINDEX") or ""), str(raw.get("EVALUATE") or ""),
                str(raw.get("CLEVEL") or ""), str(raw.get("CONTINUETIME") or ""),
                str(raw.get("KQRANK") or ""), str(raw.get("ZYFOMITE") or ""))

    @staticmethod
    def _climate_hist_row(raw: dict | None) -> tuple | None:
        """气候历史行（服务 1287807159，1953 起基本站逐时观测）。

        三坑全踩（2026-09-15 实弹）：
        1. 源 String 列内嵌 Tab/换行污染 TSV 分隔 -> 值经 _num_or_safe 中和；
        2. DDATETIME 混合格式：新数据 '1952-07-01 02:00:00'，老数据
           '20041231220000'（14 位 YYYYMMDDHHMMSS）-> 统一归一化 ISO；
        3. DDL 9 列（含 ddate 派生列），早期版本漏传致 8/9 列错位。
        """
        if not isinstance(raw, dict):
            return None
        ts_raw = str(raw.get("DDATETIME") or "").strip()
        if not ts_raw:
            return None
        digits = re.sub(r"\D", "", ts_raw)
        if len(digits) >= 14:  # YYYYMMDDHHMMSS
            ts = (f"{digits[0:4]}-{digits[4:6]}-{digits[6:8]} "
                  f"{digits[8:10]}:{digits[10:12]}:{digits[12:14]}")
        elif len(digits) == 8:  # YYYYMMDD
            ts = f"{digits[0:4]}-{digits[4:6]}-{digits[6:8]} 00:00:00"
        elif "-" in ts_raw:
            ts = ts_raw if len(ts_raw) > 10 else ts_raw + " 00:00:00"
        else:
            return None  # 未知格式丢弃（幂等键必须可归一）
        ddate = ts[:10]
        if len(ddate) != 10 or ddate[4] != "-" or ddate[7] != "-":
            return None
        vals = [raw.get(k) for k in ("P", "R", "T", "U", "V", "WDDD", "WDDF")]
        return (ts, ddate, *[_num_or_safe(v) for v in vals])

    @staticmethod
    def _ground_obs_row(raw: dict | None) -> tuple | None:
        """地面观测实况行（服务 120238293，2017 起逐时观测）。"""
        if not isinstance(raw, dict):
            return None
        ts = str(raw.get("DDATETIME") or "")
        if not ts:
            return None
        crt = str(raw.get("CRTTIME") or "")
        # DDL 11 列：ddatetime, ddate, pressure, rain, wind_dir_deg, temp, humidity,
        # visibility, wind_speed, crt_time, crt_date（ddate 曾漏传致 10/11 列错位）
        return (ts, ts[:10] or "1970-01-01",
                _to_float(raw.get("P")), _to_float(raw.get("R")),
                _to_float(raw.get("FX")), _to_float(raw.get("T")),
                _to_float(raw.get("U")), _to_float(raw.get("V")),
                _to_float(raw.get("FS")), crt, crt[:10] or "1970-01-01")

    @staticmethod
    def _landfall_row(raw: dict) -> tuple | None:
        rid = _to_int(raw.get("ID"))
        if rid is None:
            return None
        return (rid, _to_int(raw.get("YEAR")) or 0, _to_int(raw.get("TCNO")) or 0,
                str(raw.get("TCENAME") or ""), str(raw.get("TCCNAME") or ""),
                _to_int(raw.get("LANDNO")) or 0, str(raw.get("LANDLEV") or ""),
                str(raw.get("LANDPROV") or ""), str(raw.get("CYCLONENUM") or ""),
                _to_int(raw.get("LANDSUM")) or 0, str(raw.get("MEMO") or ""))

    @staticmethod
    def _tynames_row(raw: dict) -> tuple | None:
        keyid = _to_int(raw.get("KEYID"))
        if keyid is None:
            return None
        return (keyid, str(raw.get("NAME") or ""), str(raw.get("NAMECHN") or ""),
                str(raw.get("COUNTRY") or ""), str(raw.get("STARTTIME") or ""),
                str(raw.get("ENDTIME") or ""), str(raw.get("NAMEMEANINGS") or ""))

    def _fetch_sz_open_data(self, payload: FetchPayload, policy: SourcePolicy, cap: str) -> Iterator[FetchResult]:
        """深圳开放数据批量源通用拉取（spec 路由，小表全量幂等重拉，大表 startDate 增量）。"""
        t0 = time.monotonic()
        tbl_map = {
            "alt_sz_stat_monthly": (_TBL_ALT_SZ_STAT, _ALT_SZ_STAT_COLUMNS),
            "alt_sz_port_monthly": (_TBL_ALT_SZ_PORT, _ALT_SZ_PORT_COLUMNS),
            "alt_sz_house_daily": (_TBL_ALT_SZ_HOUSE, _ALT_SZ_HOUSE_COLUMNS),
            "alt_sz_weather_warning": (_TBL_ALT_SZ_WARNING, _ALT_SZ_WARNING_COLUMNS),
            "alt_sz_marine_forecast": (_TBL_ALT_SZ_MARINE, _ALT_SZ_MARINE_COLUMNS),
            "alt_sz_visibility": (_TBL_ALT_SZ_VISIBILITY, _ALT_SZ_VISIBILITY_COLUMNS),
            "alt_sz_air_quality_daily": (_TBL_ALT_SZ_AIR_DAILY, _ALT_SZ_AIR_DAILY_COLUMNS),
            "alt_sz_air_quality_region": (_TBL_ALT_SZ_AIR_REGION, _ALT_SZ_AIR_REGION_COLUMNS),
            "alt_sz_reservoir_station": (_TBL_ALT_SZ_RES_STATION, _ALT_SZ_RES_STATION_COLUMNS),
            "alt_sz_reservoir_rain_day": (_TBL_ALT_SZ_RES_RAIN_DAY, _ALT_SZ_RES_RAIN_DAY_COLUMNS),
            "alt_sz_reservoir_rain_month": (_TBL_ALT_SZ_RES_RAIN_MONTH, _ALT_SZ_RES_RAIN_MONTH_COLUMNS),
            "alt_sz_house_area": (_TBL_ALT_SZ_HOUSE_AREA, _ALT_SZ_HOUSE_AREA_COLUMNS),
            "alt_sz_house_listing": (_TBL_ALT_SZ_HOUSE_LISTING, _ALT_SZ_HOUSE_LISTING_COLUMNS),
            "alt_sz_house_presale": (_TBL_ALT_SZ_HOUSE_PRESALE, _ALT_SZ_HOUSE_PRESALE_COLUMNS),
            "alt_sz_market_subject": (_TBL_ALT_SZ_MARKET_SUBJECT, _ALT_SZ_MARKET_SUBJECT_COLUMNS),
            "alt_sz_stat_analysis": (_TBL_ALT_SZ_STAT_ANALYSIS, _ALT_SZ_STAT_ANALYSIS_COLUMNS),
            "alt_sz_enterprise_year": (_TBL_ALT_SZ_ENTERPRISE_YEAR, _ALT_SZ_ENTERPRISE_YEAR_COLUMNS),
            "alt_sz_reservoir_level": (_TBL_ALT_SZ_RES_LEVEL, _ALT_SZ_RES_LEVEL_COLUMNS),
            "alt_sz_env_meteor": (_TBL_ALT_SZ_ENV_METEOR, _ALT_SZ_ENV_METEOR_COLUMNS),
            "alt_sz_climate_hist": (_TBL_ALT_SZ_CLIMATE_HIST, _ALT_SZ_CLIMATE_HIST_COLUMNS),
            "alt_sz_ground_obs": (_TBL_ALT_SZ_GROUND_OBS, _ALT_SZ_GROUND_OBS_COLUMNS),
            "alt_typhoon_landfall_history": (_TBL_ALT_LANDFALL, _ALT_LANDFALL_COLUMNS),
            "alt_typhoon_names": (_TBL_ALT_TYNAMES, _ALT_TYNAMES_COLUMNS),
        }
        table, columns = tbl_map[cap]
        try:
            rows_out: list[tuple] = []
            extra = None
            if cap in ("alt_sz_weather_warning", "alt_sz_marine_forecast", "alt_sz_house_daily") \
                    and payload.incremental and payload.start:
                extra = {"startDate": payload.start.strftime("%Y%m%d")}
            if cap == "alt_sz_stat_monthly":
                key_new = get_secret_or_default("SZ_OPEN_DATA_APPKEY_NEW")
                for series, ctx in _SZ_STAT_SERIES_ALL:
                    # 批 2 系列绑新钥匙应用（主钥匙 10001 实证）；新钥匙未配置则报可见错误
                    key = key_new if (ctx in _SZ_STAT_BATCH2_SIDS) else None
                    if ctx in _SZ_STAT_BATCH2_SIDS and not key:
                        raise ValueError("stat batch2 需 SZ_OPEN_DATA_APPKEY_NEW（.env 未配置）")
                    for r in self._sz_open_fetch_rows(policy, ctx, extra, app_key=key):
                        t = self._stat_row(series, r)
                        if t:
                            rows_out.append(t)
            elif cap == "alt_sz_port_monthly":
                key_new = get_secret_or_default("SZ_OPEN_DATA_APPKEY_NEW")
                for series, ctx in _SZ_PORT_SERIES:
                    key = key_new if ctx in _SZ_PORT_BATCH2_SIDS else None
                    if ctx in _SZ_PORT_BATCH2_SIDS and not key:
                        raise ValueError("port batch2 系列需 SZ_OPEN_DATA_APPKEY_NEW")
                    for r in self._sz_open_fetch_rows(policy, ctx, extra, app_key=key):
                        t = self._port_row(series, r)
                        if t:
                            rows_out.append(t)
            elif cap == "alt_sz_house_daily":
                for series, ctx in _SZ_HOUSE_SERIES:
                    for r in self._sz_open_fetch_rows(policy, ctx, extra):
                        t = self._house_row(series, r)
                        if t:
                            rows_out.append(t)
            elif cap == "alt_sz_visibility":
                # 服务 1580458478 无任何过滤参数（startDate/endDate 被忽略，实测 total 恒定）：
                # 全表升序分页 2457 页。增量 = 二分定位首个 ddate >= start 的页后翻到尾；
                # 探测失败 fail-visible（拒绝盲扫 400 万行）；定位页边界越窗行按日期剔除。
                # 全量模式：总行数超限即拒绝（回补纪律入码，全史报批后专项执行）。
                vis_ctx = _SZ_SINGLE_APIS[cap]
                if payload.incremental and payload.start:
                    total = self._sz_get_total(policy, vis_ctx)
                    if not total:
                        raise ValueError("能见度增量探测失败：total 不可得（平台退化），拒绝盲扫")
                    sp = self._sz_find_start_page(policy, vis_ctx, total, payload.start.strftime("%Y-%m-%d"))
                    if sp is None:
                        raise ValueError("能见度增量二分定位失败（平台退化），拒绝盲扫")
                    start_iso = payload.start.strftime("%Y-%m-%d")
                    batch_raw = self._sz_open_fetch_rows_from(policy, vis_ctx, sp, last_page_cap=None)
                    for r in batch_raw:
                        t = self._visibility_row(r)
                        if t and t[3] >= start_iso:
                            rows_out.append(t)
                else:
                    total = self._sz_get_total(policy, vis_ctx)
                    if total and total > _SZ_VISIBILITY_FULL_PAGE_LIMIT * _SZ_OPEN_PAGE_SIZE:
                        raise ValueError(
                            f"能见度全量回补 {total} 行超限（首刷纪律：近窗增量/全史单独报批）；"
                            "增量窗口走 incremental 任务，全史回补需 Owner 报批后专项执行")
                    batch_raw = self._sz_open_fetch_rows_from(
                        policy, vis_ctx, 1,
                        last_page_cap=_SZ_VISIBILITY_FULL_PAGE_LIMIT if total else None)
                    for r in batch_raw:
                        t = self._visibility_row(r)
                        if t:
                            rows_out.append(t)
            elif cap == "alt_sz_reservoir_level":
                # 服务 1952552493 无过滤参数且 TM 非全表单调序（按内部 ID 序存放，页内倒序/跨页乱段，
                # 2026-09-16 全史回补实证）："startDate 过滤"与"升序二分定位"两假设均不成立。
                # 增量改为尾部页游标：新行追加在页空间尾部（实测日增约 1-2 页），每次从尾页-N
                # 拉到真尾；total 即游标，无需持久状态，ReplacingMergeTree(stcd,id) 幂等去重。
                # 全量模式拒绝（7630 万行全史已由 2026-09-16 专项完成，回补器留盘 scripts/data/）。
                lvl_ctx = _SZ_SINGLE_APIS[cap]
                key_lvl = get_secret_or_default("SZ_OPEN_DATA_APPKEY_NEW") if cap in _SZ_NEW_KEY_CAPS else None
                if cap in _SZ_NEW_KEY_CAPS and not key_lvl:
                    raise ValueError(f"{cap} 需 SZ_OPEN_DATA_APPKEY_NEW（.env 未配置）")
                if payload.incremental and payload.start:
                    total = self._sz_get_total(policy, lvl_ctx)
                    if not total:
                        raise ValueError("水位增量探测失败：total 不可得（平台退化），拒绝盲扫")
                    last_page = (total + _SZ_OPEN_PAGE_SIZE - 1) // _SZ_OPEN_PAGE_SIZE
                    start_page = max(1, last_page - _SZ_RES_LEVEL_TAIL_PAGES + 1)
                    batch_raw = self._sz_open_fetch_rows_from(policy, lvl_ctx, start_page)
                    for r in batch_raw:
                        t = self._res_level_row(r)
                        if t:
                            rows_out.append(t)
                else:
                    raise ValueError(
                        "水位全量回补超限（首刷纪律：7630 万行全史已由 2026-09-16 专项完成，"
                        "拒绝盲扫防内存墙）；增量走 daily_event 任务尾部页游标")
            else:
                parser = {"alt_sz_weather_warning": self._warning_row,
                          "alt_sz_marine_forecast": self._marine_row,
                          "alt_sz_visibility": self._visibility_row,
                          "alt_sz_air_quality_daily": self._air_daily_row,
                          "alt_sz_air_quality_region": self._air_region_row,
                          "alt_sz_reservoir_station": self._res_station_row,
                          "alt_sz_reservoir_rain_day": self._res_rain_day_row,
                          "alt_sz_reservoir_rain_month": self._res_rain_month_row,
                          "alt_sz_house_area": self._house_area_row,
                          "alt_sz_house_listing": self._house_listing_row,
                          "alt_sz_house_presale": self._house_presale_row,
                          "alt_sz_market_subject": self._market_subject_row,
                          "alt_sz_stat_analysis": self._stat_analysis_row,
                          "alt_sz_enterprise_year": self._enterprise_year_row,
                          "alt_sz_reservoir_level": self._res_level_row,
                          "alt_sz_env_meteor": self._env_meteor_row,
                          "alt_sz_climate_hist": self._climate_hist_row,
                          "alt_sz_ground_obs": self._ground_obs_row,
                          "alt_typhoon_landfall_history": self._landfall_row,
                          "alt_typhoon_names": self._tynames_row}[cap]
                key = get_secret_or_default("SZ_OPEN_DATA_APPKEY_NEW") if cap in _SZ_NEW_KEY_CAPS else None
                if cap in _SZ_NEW_KEY_CAPS and not key:
                    raise ValueError(f"{cap} 需 SZ_OPEN_DATA_APPKEY_NEW（.env 未配置）")
                # 单资源通道页上限 100（100 万行）：ground_obs 等大单资源曾顶到 40 页上限被静默截尾
                for r in self._sz_open_fetch_rows(policy, _SZ_SINGLE_APIS[cap], extra,
                                                  max_pages=100, app_key=key):
                    t = parser(r)
                    if t:
                        rows_out.append(t)
            # 排序按首列幂等键（各解析器保证首列非 None）：全元组比较会在数值列
            # None/float 混排时 TypeError（climate_hist 缺测行实证 2026-09-16）
            rows_out.sort(key=lambda t: t[0])
            last_key = ""
            if rows_out:
                # 末行≠最大日期——last_key 必须显式取日期列最大值
                if cap == "alt_sz_weather_warning":
                    last_key = max(t[10] for t in rows_out)
                elif cap == "alt_sz_house_daily":
                    last_key = max(t[2] for t in rows_out)
                elif cap == "alt_sz_marine_forecast":
                    wt = [t[25][:10] for t in rows_out if t[25]]
                    last_key = max(wt) if wt else ""
                elif cap == "alt_sz_visibility":
                    dts = [t[2][:10] for t in rows_out if t[2]]
                    last_key = max(dts) if dts else ""
                elif cap == "alt_sz_air_quality_daily":
                    dts = [t[2][:10] for t in rows_out if t[2]]
                    last_key = max(dts) if dts else ""
                elif cap == "alt_sz_air_quality_region":
                    dts = [t[3][:10] for t in rows_out if t[3]]
                    last_key = max(dts) if dts else ""
                elif cap == "alt_sz_house_area":
                    last_key = max(t[1] for t in rows_out) if rows_out else ""
                elif cap == "alt_sz_reservoir_level":
                    dts = [t[2][:10] for t in rows_out if t[2]]
                    last_key = max(dts) if dts else ""
                elif cap == "alt_sz_env_meteor":
                    dts = [t[1][:10] for t in rows_out if t[1]]
                    last_key = max(dts) if dts else ""
                elif cap == "alt_sz_climate_hist":
                    dts = [t[0][:10] for t in rows_out if t[0]]
                    last_key = max(dts) if dts else ""
                elif cap == "alt_sz_ground_obs":
                    dts = [t[10] for t in rows_out if t[10]]
                    last_key = max(dts) if dts else ""
            yield FetchResult(table=table, columns=columns, rows=rows_out,
                              last_key=last_key, elapsed_sec=time.monotonic() - t0)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"{cap} 获取失败: {e}")
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.monotonic() - t0, error=str(e))


def _make_sz_fetcher(cap: str):
    def _fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        yield from self._fetch_sz_open_data(payload, policy, cap)
    return _fetch


for _cap in _SZ_OPEN_CAPS:
    setattr(AkshareAltProvider, f"_fetch_{_cap}", _make_sz_fetcher(_cap))
