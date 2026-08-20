# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.fred_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (FRED API stlouisfed.org; World Bank API api.worldbank.org)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] FRED_API_KEY 可选（无 key 限额120/min）；写入 c1_market.macro_data 与 akshare 共表
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；网络失败->yield error 不抛出
# [TESTS] tests/zephyr/data/test_providers.py::TestFredProvider
# [A_module] module_id=MOD-DAT-fred_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

FredProvider 实现（MOD-L00-004 §4.3 数据源集成器）。

#ARCH-EDB-EXPAND（2026-08-04）：FRED + 世界银行免费宏观数据接入。

封装 FRED（美联储经济数据库）与 World Bank（世界银行）免费 API，继承
IngestProviderBase，提供国际宏观指标拉取能力，补充国内数据源（akshare/tushare）
覆盖不到的国际对比数据。

数据源：
- FRED: https://api.stlouisfed.org/fred/series/observations（免费，API key 可选）
- World Bank: https://api.worldbank.org/v2/country/all/indicator/{code}（免费，无需 key）

支持的能力（capability，通过 payload.extra["capability"] 路由）：
- macro_fred: FRED 宏观序列（美国GDP/CPI/失业率/联邦基金利率/国债收益率/美联储资产负债表/
  美元汇率/中国CPI/GDP 等），写入 c1_market.macro_data
- macro_worldbank: 世界银行国际宏观指标（各国GDP/人口/进出口/利率/CPI/工业/电力/FDI 等），
  写入 c1_market.macro_data

与 akshare macro_data 共表（c1_market.macro_data），通过 indicator_name 前缀区分：
- akshare 指标: GDP / CPI / PMI / Shibor / LPR ...
- FRED 指标: FRED_GDP / FRED_CPI / FRED_FEDFUNDS ...
- 世界银行指标: WB_GDP / WB_POP / WB_EXPORT ...

设计要点：
- FRED_API_KEY 从环境变量读取（可选，无 key 也能用，有限额）
- requests 直连 API，不依赖 pandas_datareader（避免版本兼容问题）
- 海外站点，国内访问可能需 VPN；支持 HTTPS_PROXY 环境变量代理
- 每个序列/指标作为一批，yield 一个 FetchResult，异常不抛出

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 拉取负载 FetchPayload
#   fields: extra["capability"]路由键(macro_fred/macro_worldbank) + start/end日期范围 + table
#   code: fetch(payload, policy) (fred_provider.py L259)
# - id: I2
#   name: 数据源策略 SourcePolicy
#   fields: 限流/重试策略（_call_with_policy 包装 requests.get）
#   code: policy_registry.SourcePolicy (fred_provider.py L59)
# - id: I3
#   name: FRED 宏观序列配置表
#   fields: 22条序列（display_name, series_id, indicator_name带FRED_前缀, unit, frequency）
#   code: _FRED_SERIES (fred_provider.py L93)
# - id: I4
#   name: 世界银行指标配置表
#   fields: 12条指标（display_name, indicator_code, indicator_name带WB_前缀, unit, frequency=annual）
#   code: _WORLD_BANK_INDICATORS (fred_provider.py L129)
# - id: I5
#   name: FRED_API_KEY 环境变量（可选）
#   fields: 免费API key，无key限额120/min；HTTPS_PROXY代理可选
#   code: get_secret_or_default("FRED_API_KEY") (fred_provider.py L190)
# 层: 算法
# - id: A1
#   name_zh: ① capability 路由分发
#   name_en: FredProvider.fetch
#   intro: 按 payload.extra["capability"] 分发到 FRED 或世界银行拉取，未连接/未知capability yield error
#   desc: macro_fred→_fetch_fred_data；macro_worldbank→_fetch_worldbank_data；其他→yield FetchResult(error)（L259-285）
#   inputs: I1
#   outputs: Iterator[FetchResult]
# - id: A2
#   name_zh: ② FRED 序列批量拉取
#   name_en: _fetch_fred_data
#   intro: 遍历22条FRED序列逐条拉取，每序列yield一批，单序列异常不阻断后续
#   desc: start默认5年前/end默认今天；无API key→yield单条error即返；每序列try/except独立（L289-343）
#   inputs: I1 I3 I5
#   outputs: 每序列一批 FetchResult
# - id: A3
#   name_zh: ③ FRED 单序列获取与行转换
#   name_en: _fetch_fred_series
#   intro: 调FRED observations API拿JSON，跳过缺失值"."，转成macro_data表行
#   desc: params带series_id/起止日期/api_key；observations逐条float解析，value="."跳过；行=(report_date, indicator_name, value, unit, freq, "fred")（L345-392）
#   inputs: I2
#   outputs: list[tuple]（macro_data行）
# - id: A4
#   name_zh: ④ 世界银行指标批量拉取
#   name_en: _fetch_worldbank_data
#   intro: 遍历12个WB指标逐指标拉取，固定用10年日期范围对冲WB数据1-2年滞后
#   desc: date_range=近10年起止年；每指标try/except独立yield一批（L396-444）
#   inputs: I4
#   outputs: 每指标一批 FetchResult
# - id: A5
#   name_zh: ⑤ WB 单指标获取与区域聚合过滤
#   name_en: _fetch_wb_indicator / _get_wb_real_country_iso3
#   intro: 拉全部国家指标值，过滤AFE/EMU等区域聚合，indicator_name编码iso3国别
#   desc: 年份转"YYYY-01-01"；iso3空或非真实国家（region.id="NA"集合）跳过；full_indicator=WB_xxx/ISO3；data_source="worldbank"（L446-566）
#   inputs: I2
#   outputs: list[tuple]（macro_data行）
#   invariant: 区域聚合记录必须过滤，国家列表获取失败fail-open不过滤
# 层: 输出
# - id: O1
#   name_zh: 宏观数据批次流 FetchResult 迭代器
#   name_en: Iterator[FetchResult]
#   intro: 每序列/指标一批行，写c1_market.macro_data表与akshare共表，靠FRED_/WB_前缀区分来源
#   invariant: 写入c1_market.macro_data共表；列序=report_date/indicator_name/indicator_value/unit/frequency/data_source
#   downstream: zephyr.data.scheduler
# - id: O2
#   name_zh: 错误批次 FetchResult(error)
#   name_en: FetchResult error
#   intro: 网络/解析异常不抛出，yield带error的空批次由调度器记录
#   downstream: zephyr.data.scheduler（记录失败）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A4
# I1 --> A2
# I3 --> A2
# I5 --> A2
# A2 --> A3
# I2 --> A3
# I4 --> A4
# A4 --> A5
# I2 --> A5
# A3 --> O1
# A5 --> O1
# A2 --> O2
# A4 --> O2
# A1 --> O2
"""

from __future__ import annotations

import datetime
import logging
import os
from typing import Final, Iterator

import requests

from zephyr.shared.security.secrets import get_secret_or_default
from zephyr.shared.utils.time_utils import now_utc, seconds_since

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
# 与 akshare_provider macro_data 共表，通过 indicator_name 前缀区分数据源
_TBL_MACRO_DATA = get_registry().table("market_macro_data")

# macro_data 表列顺序（与 akshare _fetch_macro_data 一致）
# data_source 显式提供 "fred"/"worldbank"（表 DEFAULT 'akshare' 仅适用于 akshare_provider）
_MACRO_COLUMNS: Final = ["report_date", "indicator_name", "indicator_value", "unit", "frequency", "data_source"]

# FRED API 基址
_FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
# 世界银行 API 基址
_WB_API_URL = "https://api.worldbank.org/v2"

# HTTP 请求超时（秒）——海外站点设宽松些
# FRED 响应较快（30s 够），世界银行 API 响应较慢（需 60s）
_FRED_TIMEOUT = 30
_WB_TIMEOUT = 60


# ============== FRED 关键序列（精选高价值，免费可得） ==============
# 格式: display_name -> (series_id, indicator_name, unit, frequency)
# indicator_name 统一加 FRED_ 前缀，避免与 akshare 指标冲突
_FRED_SERIES: Final = [
    # ---- 美国核心宏观 ----
    ("美国GDP", "GDP", "FRED_GDP_US", "十亿美元", "quarterly"),
    ("美国CPI", "CPIAUCSL", "FRED_CPI_US", "指数(1982-84=100)", "monthly"),
    ("美国核心CPI", "CPILFESL", "FRED_CORE_CPI_US", "指数(1982-84=100)", "monthly"),
    ("美国失业率", "UNRATE", "FRED_UNRATE_US", "百分比", "monthly"),
    ("美国非农就业", "PAYEMS", "FRED_PAYEMS_US", "千人", "monthly"),
    ("美国联邦基金利率", "FEDFUNDS", "FRED_FEDFUNDS_US", "百分比", "monthly"),
    # ---- 美国国债收益率曲线 ----
    ("美国2年期国债收益率", "DGS2", "FRED_DGS2_US", "百分比", "daily"),
    ("美国10年期国债收益率", "DGS10", "FRED_DGS10_US", "百分比", "daily"),
    ("美国30年期国债收益率", "DGS30", "FRED_DGS30_US", "百分比", "daily"),
    ("美国10年期通胀保值", "T10YIE", "FRED_T10YIE_US", "百分比", "daily"),
    ("美国10年-2年期利差", "T10Y2Y", "FRED_T10Y2Y_US", "百分比", "daily"),
    # ---- 美国货币与央行 ----
    ("美国M2货币供应", "WM2NS", "FRED_M2_US", "十亿美元", "monthly"),
    ("美联储资产负债表", "WALCL", "FRED_WALCL_US", "百万美元", "weekly"),
    ("美国联邦债务", "GFDEBTN", "FRED_DEBT_US", "百万美元", "quarterly"),
    # ---- 汇率 ----
    ("美元兑人民币汇率", "DEXCHUS", "FRED_USDCNY", "人民币/美元", "daily"),
    ("美元指数", "DTWEXBGS", "FRED_DXY", "指数", "daily"),
    ("欧元兑美元汇率", "DEXUSEU", "FRED_EURUSD", "欧元/美元", "daily"),
    # ---- 中国（FRED 收录的中国序列） ----
    ("中国CPI", "CHNCPIALLMINMEI", "FRED_CPI_CN", "指数(2010=100)", "monthly"),
    ("中国GDP(美元)", "MKTGDPCNA646NWDB", "FRED_GDP_CN_USD", "十亿美元", "annual"),
    # ---- 大宗商品 ----
    ("原油WTI现货", "POILWTIUSDM", "FRED_WTI", "美元/桶", "monthly"),
    ("黄金伦敦现货", "GOLDAMGBD228NLBM", "FRED_GOLD", "美元/盎司", "monthly"),
    # ---- 恐慌指数 ----
    ("VIX波动率指数", "VIXCLS", "FRED_VIX", "指数", "daily"),
]


# ============== 世界银行关键指标（国际宏观对比） ==============
# 格式: display_name -> (indicator_code, indicator_name, unit, frequency)
# indicator_name 统一加 WB_ 前缀
_WORLD_BANK_INDICATORS: Final = [
    ("GDP现价美元", "NY.GDP.MKTP.CD", "WB_GDP_USD", "美元", "annual"),
    ("人均GDP", "NY.GDP.PCAP.CD", "WB_GDP_PER_CAPITA", "美元", "annual"),
    ("总人口", "SP.POP.TOTL", "WB_POP", "人", "annual"),
    ("商品出口", "TX.VAL.MRCH.CD.WT", "WB_EXPORT", "美元", "annual"),
    ("商品进口", "TM.VAL.MRCH.CD.WT", "WB_IMPORT", "美元", "annual"),
    ("实际利率", "FR.INR.RINR", "WB_REAL_RATE", "百分比", "annual"),
    ("CPI通胀率", "FP.CPI.TOTL.ZG", "WB_CPI_INFLATION", "百分比", "annual"),
    ("工业增加值占比", "NV.IND.MANF.ZS", "WB_INDUST_RATIO", "百分比", "annual"),
    ("电力消费", "EG.USE.ELEC.KH", "WB_ELEC", "千瓦时", "annual"),
    ("贸易占GDP比", "NE.TRD.GNFS.ZS", "WB_TRADE_RATIO", "百分比", "annual"),
    ("FDI净流入", "BX.KLT.DINV.CD.WD", "WB_FDI", "美元", "annual"),
    ("外汇储备", "FI.RES.TOTL.CD", "WB_FX_RESERVE", "美元", "annual"),
]

# 世界银行主要经济体 country code（全量 too 多，精选主要经济体）
_WB_COUNTRIES = "all"  # all=所有国家；也可指定 "CN;US;JP;DE;IN;GB;FR;BR;RU;KR"


def _detect_local_proxy(port: int = 10808, timeout: float = 1.0) -> str | None:
    """探测本地代理端口（v2rayN 10808 HTTP/SOCKS5 双协议）。

    VPN 开启时端口在监听，返回 http 代理 URL；关闭时 1s 内返回 None。
    与 rss_provider._is_vpn_ready 同一探测模式（2026-08-14 对齐）。
    """
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port))
        return f"http://127.0.0.1:{port}"
    except OSError:
        return None
    finally:
        s.close()


class FredProvider(IngestProviderBase):
    """FRED + 世界银行 宏观数据 Provider。

    免费数据源，无需强制认证（FRED key 可选）。
    线程安全模型：shared（无状态 HTTP 调用）。
    """

    source_name: str = "fred"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="fred",
        display_name="FRED/世界银行 宏观数据",
        auth_type="api_key_optional",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=120,
        capabilities=[
            CapabilityContract("macro_fred", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("macro_worldbank", supports_symbols_null=True, requires_date_range=True),
        ],
        known_issues=["FRED无key限额120/min", "世界银行数据有1-2年滞后", "海外站点国内访问可能需VPN"],
    )

    def __init__(self):
        super().__init__()
        self._fred_key: str | None = None
        # 代理配置：海外站点，若环境变量设了 HTTPS_PROXY 则启用（VPN 场景）；
        # 2026-08-14 增强：env 未设时探测本地代理端口 10808（v2rayN HTTP/SOCKS5 双协议端口），
        # 在监听则自动走代理——此前 env 未设导致直连 api.stlouisfed.org 超时/JSON 解析失败（x75/3天）
        self._proxies: dict | None = None
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or _detect_local_proxy()
        if proxy:
            self._proxies = {"https": proxy, "http": proxy}
        # 世界银行真实国家 iso3 代码缓存（首次调用时从 country API 加载）
        # 用于过滤区域聚合（AFE/AFW/ARB/CEB/EMU 等，region.id="NA"）
        self._wb_country_iso3: set[str] | None = None

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：读取 FRED_API_KEY（可选），验证网络可达。

        FRED key 可选——无 key 也能调用（限额 120/min），有 key 提高到 120/min
        且支持更多序列。key 从环境变量 FRED_API_KEY 读取。
        """
        self._fred_key = get_secret_or_default("FRED_API_KEY")
        if self._fred_key:
            log.info("FRED 已配置 API key（限额提升）")
        else:
            log.info("FRED 未配置 API key（使用免费限额 120/min）")
        self._connected = True

    def health_check(self) -> bool:
        """探活：验证 FRED API key 配置 + 网络可达。

        FRED API 自 2015 起强制要求 api_key（免费注册）。
        无 key 时降级为验证世界银行 API 可达性——世界银行无需 key，
        无 FRED key 时仍可拉取世界银行数据（macro_worldbank capability）。
        """
        if not self._connected:
            return False
        if not self._fred_key:
            log.warning(
                "FRED_API_KEY 未配置——FRED 数据将跳过"
                "（免费注册 https://fred.stlouisfed.org/docs/api/api_key.html），"
                "世界银行数据仍可正常拉取"
            )
            # 无 FRED key 时，验证世界银行 API 可达性
            try:
                resp = requests.get(
                    f"{_WB_API_URL}/country/all/indicator/NY.GDP.MKTP.CD",
                    params={"format": "json", "per_page": 1},
                    timeout=15,
                    proxies=self._proxies,
                )
                if resp.status_code == 200:
                    log.info("FRED_API_KEY 未配置，世界银行 API 可达——macro_worldbank 可用")
                    return True
                log.warning(f"世界银行探活失败（status={resp.status_code}）")
                return False
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning(f"世界银行探活失败（网络不可达，可能需 VPN）: {e}")
                return False
        try:
            # 用一个轻量序列验证 key 有效性 + 网络连通
            params = {
                "series_id": "FEDFUNDS",
                "observation_start": datetime.date.today().isoformat(),
                "observation_end": datetime.date.today().isoformat(),
                "file_type": "json",
                "api_key": self._fred_key,
            }
            resp = requests.get(
                _FRED_API_URL,
                params=params,
                timeout=10,
                proxies=self._proxies,
            )
            # 200=成功，400=key无效或参数错误，403=key无效
            if resp.status_code == 200:
                return True
            log.warning(f"FRED 探活失败（status={resp.status_code}）: {resp.text[:100]}")
            return False
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning(f"FRED 探活失败（网络不可达，可能需 VPN）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 HTTP，无需操作。"""
        self._connected = False
        log.info("FRED/世界银行 已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        if not self._connected:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="fred 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "macro_fred":
            yield from self._fetch_fred_data(payload, policy)
        elif capability == "macro_worldbank":
            yield from self._fetch_worldbank_data(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- FRED 宏观数据 ----

    def _fetch_fred_data(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取 FRED 宏观序列，每序列一批 yield。

        遍历 _FRED_SERIES 配置表，逐个调用 FRED API 获取观察值序列，
        转换为 macro_data 表格式（report_date, indicator_name, value, unit, frequency）。
        无 FRED_API_KEY 时 yield 单条 error（FRED API 强制要求 key）。
        """
        if not self._fred_key:
            yield FetchResult(
                table=_TBL_MACRO_DATA,
                columns=_MACRO_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="FRED_API_KEY 未配置（免费注册: https://fred.stlouisfed.org/docs/api/api_key.html）",
            )
            return
        start = payload.start or datetime.date.today() - datetime.timedelta(days=365 * 5)
        end = payload.end or datetime.date.today()

        for display_name, series_id, indicator_name, unit, freq in _FRED_SERIES:
            t0 = now_utc()
            try:
                rows = self._fetch_fred_series(
                    series_id,
                    indicator_name,
                    unit,
                    freq,
                    start,
                    end,
                    policy,
                )
                self._log.info(
                    "FRED %s(%s): %d 行",
                    display_name,
                    series_id,
                    len(rows),
                )
                yield FetchResult(
                    table=_TBL_MACRO_DATA,
                    columns=_MACRO_COLUMNS,
                    rows=rows,
                    last_key=end.isoformat(),
                    elapsed_sec=seconds_since(t0),
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"FRED {series_id}({display_name}) 获取失败: {e}")
                yield FetchResult(
                    table=_TBL_MACRO_DATA,
                    columns=_MACRO_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )

    def _fetch_fred_series(
        self,
        series_id: str,
        indicator_name: str,
        unit: str,
        freq: str,
        start: datetime.date,
        end: datetime.date,
        policy: SourcePolicy,
    ) -> list[tuple]:
        """获取单个 FRED 序列并转换为 macro_data 行格式。

        FRED API: /fred/series/observations?series_id=...&observation_start=...&observation_end=...
        返回 JSON: {"observations": [{"date": "2026-01-01", "value": "123.4"}, ...]}
        value 为 "." 表示缺失值，跳过。
        """
        params = {
            "series_id": series_id,
            "observation_start": start.isoformat(),
            "observation_end": end.isoformat(),
            "file_type": "json",
        }
        if self._fred_key:
            params["api_key"] = self._fred_key

        resp = self._call_with_policy(
            requests.get,
            policy,
            _FRED_API_URL,
            params=params,
            timeout=_FRED_TIMEOUT,
            proxies=self._proxies,
        )
        data = resp.json()
        observations = data.get("observations", [])

        rows: list[tuple] = []
        for obs in observations:
            value_str = str(obs.get("value", "."))
            if value_str == ".":
                continue  # FRED 缺失值标记
            try:
                value = float(value_str)
            except ValueError:
                continue
            report_date = str(obs.get("date", ""))
            rows.append((report_date, indicator_name, value, unit, freq, "fred"))
        return rows

    # ---- 世界银行宏观数据 ----

    def _fetch_worldbank_data(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取世界银行宏观指标，每指标一批 yield。

        遍历 _WORLD_BANK_INDICATORS 配置表，逐个调用 World Bank API 获取
        所有国家的指标值，转换为 macro_data 表格式。
        indicator_name 中编码 country code（如 WB_GDP_USD/CN）以便区分国家。
        """
        # 世界银行数据是年度数据且有 1-2 年滞后，scheduler 传递的日级日期范围
        # （如 start=2026-08-01 end=2026-08-04）会导致 date_range="2026:2026"
        # 而最新数据可能尚未发布。始终使用 10 年范围确保获取历史数据。
        today = datetime.date.today()
        start_year = (today - datetime.timedelta(days=365 * 10)).year
        end_year = today.year
        date_range = f"{start_year}:{end_year}"

        for display_name, indicator_code, indicator_name, unit, freq in _WORLD_BANK_INDICATORS:
            t0 = now_utc()
            try:
                rows = self._fetch_wb_indicator(
                    indicator_code,
                    indicator_name,
                    unit,
                    freq,
                    date_range,
                    policy,
                )
                self._log.info(
                    "WorldBank %s(%s): %d 行",
                    display_name,
                    indicator_code,
                    len(rows),
                )
                yield FetchResult(
                    table=_TBL_MACRO_DATA,
                    columns=_MACRO_COLUMNS,
                    rows=rows,
                    last_key=str(end_year),
                    elapsed_sec=seconds_since(t0),
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"WorldBank {indicator_code}({display_name}) 获取失败: {e}")
                yield FetchResult(
                    table=_TBL_MACRO_DATA,
                    columns=_MACRO_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )

    def _get_wb_real_country_iso3(self) -> set[str]:
        """获取世界银行真实国家的 iso3 代码集合（缓存）。

        世界银行 country/all 返回含区域聚合（AFE/AFW/ARB/CEB/EMU 等），其
        region.id 为 "NA"（Not Applicable）。真实国家的 region.id 非空（如 EAS/ECS）。
        本方法调用 country API 获取所有 region.id != "NA" 的国家 iso3 代码，
        缓存后供 _fetch_wb_indicator 过滤区域聚合使用。

        API: /v2/country?format=json&per_page=400
        返回: [{id, iso2, iso3, name, region:{id, value}, ...}, ...]
        region.id="NA" → 区域聚合，跳过；否则 → 真实国家，收 iso3。

        失败时返回空集合（fail-open，不过滤——优于阻断数据获取）。
        """
        if self._wb_country_iso3 is not None:
            return self._wb_country_iso3

        url = f"{_WB_API_URL}/country"
        params = {"format": "json", "per_page": 400}
        try:
            resp = requests.get(url, params=params, timeout=_WB_TIMEOUT, proxies=self._proxies)
            data = resp.json()
            if not isinstance(data, list) or len(data) < 2:
                self._wb_country_iso3 = set()
                return self._wb_country_iso3
            countries = data[1] or []
            real_codes: set[str] = set()
            for c in countries:
                region = c.get("region", {})
                region_id = str(region.get("id", "") or "")
                if region_id and region_id != "NA":
                    iso3 = str(c.get("iso3", "") or c.get("id", "") or "")
                    if iso3:
                        real_codes.add(iso3)
            self._wb_country_iso3 = real_codes
            self._log.info("WorldBank 国家列表加载: %d 个真实国家（已过滤区域聚合）", len(real_codes))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"WorldBank 国家列表获取失败，跳过区域聚合过滤: {e}")
            self._wb_country_iso3 = set()
        return self._wb_country_iso3

    def _fetch_wb_indicator(
        self,
        indicator_code: str,
        indicator_name: str,
        unit: str,
        freq: str,
        date_range: str,
        policy: SourcePolicy,
    ) -> list[tuple]:
        """获取单个世界银行指标（所有国家），转换为 macro_data 行格式。

        World Bank API: /v2/country/all/indicator/{code}?date=2015:2026&format=json&per_page=10000
        返回 JSON: [metadata, [{country:{id,value}, date:"2023", value:17.96, ...}, ...]]
        value 为 None 表示缺失，跳过。
        """
        url = f"{_WB_API_URL}/country/{_WB_COUNTRIES}/indicator/{indicator_code}"
        params = {
            "date": date_range,
            "format": "json",
            "per_page": 10000,
        }
        resp = self._call_with_policy(
            requests.get,
            policy,
            url,
            params=params,
            timeout=_WB_TIMEOUT,
            proxies=self._proxies,
        )
        data = resp.json()
        # 世界银行返回 [metadata, records] 两元素数组
        if not isinstance(data, list) or len(data) < 2:
            return []
        records = data[1] or []

        # 获取真实国家 iso3 代码集合（缓存），用于过滤区域聚合
        # #ARCH-EDB-EXPAND 数据质量优化：countryiso3code 非空但不在真实国家列表中的
        # 也是区域聚合（如 AFE/AFW/ARB/CEB/EMU 等3位代码），需二次过滤
        real_country_codes = self._get_wb_real_country_iso3()

        rows: list[tuple] = []
        skipped_aggregate = 0
        for rec in records:
            value = rec.get("value")
            if value is None:
                continue
            try:
                value_float = float(value)
            except (ValueError, TypeError):
                continue
            # 世界银行 date 字段：年度数据返回年份字符串（如 "2024"），
            # macro_data 表 report_date 列是 Date 类型，需要 "YYYY-MM-DD" 格式。
            # 将年份转为 "YYYY-01-01"；已是完整日期的保持不变。
            raw_date = str(rec.get("date", ""))
            if len(raw_date) == 4 and raw_date.isdigit():
                report_date = f"{raw_date}-01-01"
            else:
                report_date = raw_date
            # 用 countryiso3code 过滤区域聚合（#ARCH-EDB-EXPAND 数据质量优化）：
            # 世界银行 country/all 返回含区域聚合（AFE/AFW/ARB/CEB/EMU 等），
            # 其 countryiso3code 可能为空或非标准3位代码。
            # 两层过滤：①空 iso3 直接跳过；②iso3 不在真实国家集合中跳过
            iso3 = str(rec.get("countryiso3code", "") or "")
            if not iso3:
                skipped_aggregate += 1
                continue  # 无 iso3 代码，区域聚合
            if real_country_codes and iso3 not in real_country_codes:
                skipped_aggregate += 1
                continue  # iso3 非真实国家（区域聚合如 AFE/EMU），跳过
            # indicator_name 编码 country：WB_GDP_USD/CHN，便于按国家筛选
            full_indicator = f"{indicator_name}/{iso3}"
            rows.append((report_date, full_indicator, value_float, unit, freq, "worldbank"))
        if skipped_aggregate:
            self._log.info(
                "WorldBank %s: 过滤 %d 条区域聚合记录，保留 %d 条国家记录",
                indicator_code,
                skipped_aggregate,
                len(rows),
            )
        return rows
