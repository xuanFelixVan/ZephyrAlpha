# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.eia_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (EIA API v2 api.eia.gov)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] EIA_API_KEY 必填（免费注册）；写入 c1_market.macro_data 与 akshare/FRED 共表
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；网络失败->yield error 不抛出
# [TESTS] tests/zephyr/data/test_providers.py::TestEiaProvider
# [A_module] module_id=MOD-DAT-eia_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
EiaProvider 实现（MOD-L00-004 §4.3 数据源集成器）。

#ARCH-EDB-EXPAND（2026-08-04）：EIA 能源数据接入。

封装 EIA（美国能源信息署）API v2，继承 IngestProviderBase，
提供石油/天然气库存、产量、价格等能源指标拉取能力。

数据源：
- EIA API v2: https://api.eia.gov/v2/（免费，需注册 API key）

支持的能力（capability，通过 payload.extra["capability"] 路由）：
- eia_petroleum: 石油数据（原油/汽油/馏分油库存、WTI/Brent现货价格）
- eia_naturalgas: 天然气数据（天然气库存）
- eia_full: 全量获取所有 EIA 指标（用于回填）

与 akshare/FRED macro_data 共表（c1_market.macro_data），通过 indicator_name
前缀区分：
- akshare 指标: GDP / CPI / PMI ...
- FRED 指标: FRED_GDP / FRED_CPI ...
- 世界银行指标: WB_GDP / WB_POP ...
- EIA 指标: EIA_CRUDE_INVENTORY / EIA_WTI_SPOT / EIA_BRENT_SPOT ...

设计要点：
- EIA_API_KEY 从环境变量读取（必填，免费注册 https://www.eia.gov/opendata/register.php）
- EIA API v2 是 RESTful，每个序列通过 path + facets 参数查询
- 每个序列作为一批，yield 一个 FetchResult，异常不抛出
- 海外站点，国内访问可能需 VPN；支持 HTTPS_PROXY 环境变量代理

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: eia_provider.py
# 层: 算法
# - id: A1
#   name_zh: ① EiaProvider
#   name_en: EiaProvider
#   intro: EIA 能源数据 Provider。
#   desc: EIA 能源数据 Provider。 免费数据源，需注册 API key（https://www.eia.gov/opendata/register.php）。 线程安全模型：s…；公共方法（定义序）: connect…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EiaProvider
#   downstream: zephyr.data.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
# 与 akshare/FRED macro_data 共表，通过 indicator_name 前缀区分数据源
_TBL_MACRO_DATA = get_registry().table("market_macro_data")

# macro_data 表列顺序（与 akshare/FRED 一致）
# data_source 显式提供 "eia"（表 DEFAULT 'akshare' 仅适用于 akshare_provider）
_MACRO_COLUMNS: Final = ["report_date", "indicator_name", "indicator_value", "unit", "frequency", "data_source"]

# EIA API v2 基址
_EIA_API_URL = "https://api.eia.gov/v2"

# HTTP 请求超时（秒）——海外站点设宽松些
_EIA_TIMEOUT = 30


# ============== EIA 关键序列（精选高价值，免费可得） ==============
# 格式: (display_name, api_path, facet_value, indicator_name, unit, frequency)
# api_path 是 v2 路由路径（如 petroleum/stoc/wstk/data/）
# facet_value 是 series 标识（用于 facets[series][] 参数）
# indicator_name 统一加 EIA_ 前缀，避免与其他数据源冲突
_EIA_SERIES: Final = [
    # ---- 石油库存（周度，EIA Weekly Petroleum Status Report）----
    # 数据源: petroleum/sum/sndw/ — Weekly Summary, Supply & Disposition
    # 单位: Thousand Barrels（千桶）；series 编码 W*=Weekly + 类别 + US + 1=不含SPR
    # 修复(2026-08-05): 原 stoc/wstk + WSTURO 等编码返回 0 条，实测正确路由为 sum/sndw + WCESTUS1 等
    ("原油库存", "petroleum/sum/sndw/data/", "WCESTUS1", "EIA_CRUDE_INVENTORY", "千桶", "weekly"),
    ("汽油库存", "petroleum/sum/sndw/data/", "WGTSTUS1", "EIA_GASOLINE_INVENTORY", "千桶", "weekly"),
    ("馏分油库存", "petroleum/sum/sndw/data/", "WDISTUS1", "EIA_DISTILLATE_INVENTORY", "千桶", "weekly"),
    ("丙烷库存", "petroleum/sum/sndw/data/", "WPRSTUS1", "EIA_PROPANE_INVENTORY", "千桶", "weekly"),
    # ---- 石油现货价格（日度）----
    # 数据源: petroleum/pri/spt/ — Petroleum Spot Prices
    ("WTI现货价格", "petroleum/pri/spt/data/", "RWTC", "EIA_WTI_SPOT", "美元/桶", "daily"),
    ("Brent现货价格", "petroleum/pri/spt/data/", "RBRTE", "EIA_BRENT_SPOT", "美元/桶", "daily"),
    # ---- 天然气库存（月度）----
    # 数据源: natural-gas/stor/sum/ — Natural Gas Storage Summary
    # 修复(2026-08-05): 原 WNGST+weekly 编码不存在(返回0)，正确为 N5020US2+monthly
    # N5020US2 = U.S. Total Natural Gas in Underground Storage (Working Gas)
    ("天然气库存", "natural-gas/stor/sum/data/", "N5020US2", "EIA_NATGAS_INVENTORY", "MMcf", "monthly"),
]


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


class EiaProvider(IngestProviderBase):
    """EIA 能源数据 Provider。

    免费数据源，需注册 API key（https://www.eia.gov/opendata/register.php）。
    线程安全模型：shared（无状态 HTTP 调用）。
    """

    source_name: str = "eia"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="eia",
        display_name="EIA 能源数据",
        auth_type="api_key_required",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=500,
        capabilities=[
            CapabilityContract("eia_petroleum", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("eia_naturalgas", supports_symbols_null=True, requires_date_range=True),
            CapabilityContract("eia_full", supports_symbols_null=True, requires_date_range=True),
        ],
        known_issues=["EIA_API_KEY必填（免费注册）", "海外站点国内访问可能需VPN"],
    )

    def __init__(self):
        super().__init__()
        self._eia_key: str | None = None
        # 代理配置：海外站点，若环境变量设了 HTTPS_PROXY 则启用（VPN 场景）；
        # 2026-08-14 增强：env 未设时探测本地代理端口 10808（同 fred_provider）
        self._proxies: dict | None = None
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or _detect_local_proxy()
        if proxy:
            self._proxies = {"https": proxy, "http": proxy}

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：读取 EIA_API_KEY（必填），验证网络可达。

        EIA API v2 自 2022 起强制要求 api_key（免费注册）。
        key 从环境变量 EIA_API_KEY 读取。
        """
        self._eia_key = get_secret_or_default("EIA_API_KEY")
        if self._eia_key:
            log.info("EIA 已配置 API key")
        else:
            log.warning("EIA 未配置 API key（免费注册 https://www.eia.gov/opendata/register.php）")
        self._connected = True

    def health_check(self) -> bool:
        """探活：验证 EIA API key 配置 + 网络可达。

        EIA API v2 强制要求 api_key。无 key 时返回 False——
        scheduler 会跳过本源。
        """
        if not self._connected:
            return False
        if not self._eia_key:
            log.warning("EIA 探活失败：未配置 EIA_API_KEY（免费注册 https://www.eia.gov/opendata/register.php）")
            return False
        try:
            # 用一个轻量路由验证 key 有效性 + 网络连通
            # petroleum/pri/spt/ 路由的元数据查询（不拉数据，只验证 key）
            url = f"{_EIA_API_URL}/petroleum/pri/spt/"
            params = {"api_key": self._eia_key}
            resp = requests.get(url, params=params, timeout=10, proxies=self._proxies)
            if resp.status_code == 200:
                return True
            log.warning(f"EIA 探活失败（status={resp.status_code}）: {resp.text[:100]}")
            return False
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning(f"EIA 探活失败（网络不可达，可能需 VPN）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 HTTP，无需操作。"""
        self._connected = False
        log.info("EIA 已断开")

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
                error="eia 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "eia_petroleum":
            yield from self._fetch_eia_data(payload, policy, filter_type="petroleum")
        elif capability == "eia_naturalgas":
            yield from self._fetch_eia_data(payload, policy, filter_type="naturalgas")
        elif capability == "eia_full":
            yield from self._fetch_eia_data(payload, policy, filter_type="all")
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- EIA 数据获取 ----

    def _fetch_eia_data(
        self,
        payload: FetchPayload,
        policy: SourcePolicy,
        filter_type: str = "all",
    ) -> Iterator[FetchResult]:
        """获取 EIA 能源数据，每序列一批 yield。

        遍历 _EIA_SERIES 配置表，根据 filter_type 过滤（petroleum/naturalgas/all），
        逐个调用 EIA API v2 获取观察值序列，转换为 macro_data 表格式。
        无 EIA_API_KEY 时 yield 单条 error。
        """
        if not self._eia_key:
            yield FetchResult(
                table=_TBL_MACRO_DATA,
                columns=_MACRO_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="EIA_API_KEY 未配置（免费注册: https://www.eia.gov/opendata/register.php）",
            )
            return

        start = payload.start or datetime.date.today() - datetime.timedelta(days=365 * 5)
        end = payload.end or datetime.date.today()

        for display_name, api_path, facet_value, indicator_name, unit, freq in _EIA_SERIES:
            # 按 filter_type 过滤
            if filter_type == "petroleum" and "natural-gas" in api_path:
                continue
            if filter_type == "naturalgas" and "natural-gas" not in api_path:
                continue

            t0 = now_utc()
            try:
                rows = self._fetch_eia_series(
                    api_path,
                    facet_value,
                    indicator_name,
                    unit,
                    freq,
                    start,
                    end,
                    policy,
                )
                self._log.info(
                    "EIA %s(%s): %d 行",
                    display_name,
                    facet_value,
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
                self._log.warning(f"EIA {facet_value}({display_name}) 获取失败: {e}")
                yield FetchResult(
                    table=_TBL_MACRO_DATA,
                    columns=_MACRO_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=seconds_since(t0),
                    error=str(e),
                )

    def _fetch_eia_series(
        self,
        api_path: str,
        facet_value: str,
        indicator_name: str,
        unit: str,
        freq: str,
        start: datetime.date,
        end: datetime.date,
        policy: SourcePolicy,
    ) -> list[tuple]:
        """获取单个 EIA 序列并转换为 macro_data 行格式。

        EIA API v2: /v2/{api_path}?api_key=...&frequency=...&data[0]=value
                    &facets[series][]={facet_value}&start=...&end=...
        返回 JSON: {"response": {"data": [{"period": "2024-01-05", "value": "431.5", ...}]}}
        value 为 None 或空表示缺失值，跳过。
        value 自 v2.1.6 起为字符串格式，需 float() 转换。
        """
        url = f"{_EIA_API_URL}/{api_path}"
        params = {
            "api_key": self._eia_key,
            "frequency": freq,
            "data[0]": "value",
            "facets[series][]": facet_value,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "length": 5000,  # EIA API v2 单次最多 5000 行
        }

        resp = self._call_with_policy(
            requests.get,
            policy,
            url,
            params=params,
            timeout=_EIA_TIMEOUT,
            proxies=self._proxies,
        )
        data = resp.json()

        # EIA v2 响应结构: {"response": {"data": [...]}}
        records = data.get("response", {}).get("data", [])

        rows: list[tuple] = []
        for record in records:
            value_raw = record.get("value")
            if value_raw is None or value_raw == "":
                continue  # EIA 缺失值标记
            try:
                value = float(value_raw)
            except (ValueError, TypeError):
                continue
            report_date = str(record.get("period", ""))
            if not report_date:
                continue
            # EIA period 格式因 frequency 而异：
            #   daily/weekly → "YYYY-MM-DD"（10 字符，直接用）
            #   monthly      → "YYYY-MM"（7 字符，补 "-01"）
            #   annual       → "YYYY"（4 字符，补 "-01-01"）
            if len(report_date) == 7:
                report_date = report_date + "-01"
            elif len(report_date) == 4:
                report_date = report_date + "-01-01"
            rows.append((report_date, indicator_name, value, unit, freq, "eia"))

        return rows
