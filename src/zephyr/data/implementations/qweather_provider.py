# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.qweather_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (和风天气 API devapi.qweather.com)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] QWEATHER_API_KEY 必填（免费注册）；写入 c1_market.weather_data；免费版无历史API——必须每日积累
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；网络失败->yield error 不抛出
# [TESTS] tests/zephyr/data/test_providers.py::TestQWeatherProvider
# [A_module] module_id=MOD-DAT-qweather_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QWeatherProvider 实现（MOD-L00-004 §4.3 数据源集成器）。

#ARCH-REALTIME-ACCUM（2026-08-04）：和风天气数据接入——时间敏感型积累。

封装和风天气（QWeather）免费版 API，继承 IngestProviderBase，
提供实时天气 + 7天预报拉取能力。

数据源：
- 和风天气: https://{QWEATHER_API_HOST}/v7（免费，需注册 API key + 专属 API Host）
- 2026 年起公共地址 devapi.qweather.com 已弃用，必须用控制台分配的专属 API Host
- 免费版 1000 次/天，40 城市 × 2 种数据 = 80 次/天，远低于限制

支持的能力（capability，通过 payload.extra["capability"] 路由）：
- qweather_now: 实时天气（40 个主要城市，每日快照）
- qweather_forecast: 7 天预报（40 个主要城市，每日快照）
- qweather_full: 实时 + 预报全量获取

⚠️ 时间敏感型数据：和风天气免费版无历史数据 API，今天不记录就永远缺。
   必须每日执行积累，写入 c1_market.weather_data 表。

设计要点：
- QWEATHER_API_KEY 从环境变量读取（必填，免费注册 https://dev.qweather.com）
- QWEATHER_API_HOST 从环境变量读取（必填，控制台-设置中查看专属 API Host）
- 认证方式：X-QW-Api-Key 请求头（2026 年起公共 key 查询参数已弃用）
- 40 个主要城市（直辖市+省会+重点城市），用经纬度作为 location 参数
- 国内服务，不需要 VPN
- 每个城市实时天气 1 行 + 7 天预报 7 行 = 8 行/城市/天
"""

from __future__ import annotations

import datetime
import logging
import os
import time
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
_TBL_WEATHER_DATA = get_registry().table("market_weather_data")

# weather_data 表列顺序（与 ClickHouse DDL 对齐）
_WEATHER_COLUMNS: Final = [
    "record_date",
    "location_id",
    "location_name",
    "forecast_type",
    "forecast_date",
    "temp",
    "temp_max",
    "temp_min",
    "feels_like",
    "text",
    "icon_code",
    "humidity",
    "precip",
    "pressure",
    "visibility",
    "wind_dir",
    "wind_scale",
    "wind_speed",
    "cloud",
    "dew_point",
]

# 和风天气 API 基址前缀（host 从环境变量读取，2026 年起公共地址已弃用）
_QWEATHER_API_PATH = "/v7"

# HTTP 请求超时（秒）
_QWEATHER_TIMEOUT = 15

# 每次请求间隔（秒）——礼貌限流，避免短时间大量请求
_QWEATHER_REQUEST_INTERVAL = 0.1


# ============== 主要城市列表（直辖市+省会+重点城市） ==============
# 格式: (城市名, 经度, 纬度)
# 用经纬度作为 location 参数（和风天气 v7 API 支持 "经度,纬度" 格式）
_QWEATHER_CITIES: Final = [
    # ---- 直辖市 ----
    ("北京", 116.41, 39.92),
    ("上海", 121.47, 31.23),
    ("天津", 117.20, 39.13),
    ("重庆", 106.55, 29.56),
    # ---- 华南 ----
    ("广州", 113.23, 23.16),
    ("深圳", 114.07, 22.62),
    ("海口", 110.32, 20.04),
    ("南宁", 108.37, 22.82),
    ("珠海", 113.58, 22.27),
    ("厦门", 118.09, 24.48),
    # ---- 华东 ----
    ("杭州", 120.16, 30.27),
    ("南京", 118.78, 32.07),
    ("合肥", 117.28, 31.86),
    ("福州", 119.30, 26.08),
    ("济南", 117.00, 36.65),
    ("宁波", 121.55, 29.87),
    ("苏州", 120.62, 31.32),
    ("无锡", 120.30, 31.57),
    ("温州", 120.70, 27.99),
    ("青岛", 120.38, 36.07),
    # ---- 华中 ----
    ("武汉", 114.31, 30.59),
    ("长沙", 112.93, 28.23),
    ("郑州", 113.62, 34.75),
    ("南昌", 115.86, 28.68),
    # ---- 华北 ----
    ("石家庄", 114.50, 38.05),
    ("太原", 112.55, 37.87),
    ("呼和浩特", 111.75, 40.84),
    # ---- 东北 ----
    ("沈阳", 123.43, 41.80),
    ("大连", 121.62, 38.91),
    ("哈尔滨", 126.64, 45.75),
    ("长春", 125.32, 43.82),
    # ---- 西南 ----
    ("成都", 104.07, 30.67),
    ("昆明", 102.83, 24.88),
    ("贵阳", 106.63, 26.65),
    ("拉萨", 91.13, 29.65),
    # ---- 西北 ----
    ("西安", 108.93, 34.27),
    ("兰州", 103.83, 36.06),
    ("银川", 106.27, 38.47),
    ("西宁", 101.78, 36.62),
    ("乌鲁木齐", 87.62, 43.79),
]


def _safe_float(v) -> float | None:
    """安全转 float，失败返回 None。"""
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


class QWeatherProvider(IngestProviderBase):
    """和风天气 Provider。

    免费数据源，需注册 API key（https://dev.qweather.com）。
    线程安全模型：shared（无状态 HTTP 调用）。
    国内服务，不需要 VPN。
    """

    source_name: str = "qweather"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="qweather",
        display_name="和风天气",
        auth_type="api_key_required",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=1000,
        capabilities=[
            CapabilityContract("qweather_now", supports_symbols_null=True),
            CapabilityContract("qweather_forecast", supports_symbols_null=True),
            CapabilityContract("qweather_full", supports_symbols_null=True),
        ],
        known_issues=[
            "QWEATHER_API_KEY必填（免费注册）",
            "QWEATHER_API_HOST必填（控制台-设置中查看专属API Host）",
            "免费版无历史数据API——必须每日积累，错过无法回填",
            "免费版1000次/天限制",
            "2026年起公共地址devapi.qweather.com已弃用",
        ],
    )

    def __init__(self):
        super().__init__()
        self._qweather_key: str | None = None
        self._api_host: str | None = None
        # 代理配置：国内服务，通常不需要代理
        self._proxies: dict | None = None
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
        if proxy:
            self._proxies = {"https": proxy, "http": proxy}

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：读取 QWEATHER_API_KEY + QWEATHER_API_HOST（均必填）。"""
        self._qweather_key = get_secret_or_default("QWEATHER_API_KEY")
        self._api_host = get_secret_or_default("QWEATHER_API_HOST")
        if self._qweather_key and self._api_host:
            log.info("和风天气已配置 API key + API Host (%s)", self._api_host)
        else:
            if not self._qweather_key:
                log.warning("和风天气未配置 API key（免费注册 https://dev.qweather.com）")
            if not self._api_host:
                log.warning(
                    "和风天气未配置 API Host（控制台-设置 中查看专属 API Host，格式如 abc1234xyz.def.qweatherapi.com）"
                )
        self._connected = True

    def health_check(self) -> bool:
        """探活：验证 QWEATHER_API_KEY + QWEATHER_API_HOST 配置 + 网络可达。

        和风天气 API v7 强制要求 key + 专属 API Host。
        无 key 或无 host 时返回 False——scheduler 会跳过本源。
        """
        if not self._connected:
            return False
        if not self._qweather_key:
            log.warning("和风天气探活失败：未配置 QWEATHER_API_KEY（免费注册 https://dev.qweather.com）")
            return False
        if not self._api_host:
            log.warning("和风天气探活失败：未配置 QWEATHER_API_HOST（控制台-设置 中查看专属 API Host）")
            return False
        try:
            # 用北京实时天气验证 key 有效性 + 网络连通
            url = f"https://{self._api_host}{_QWEATHER_API_PATH}/weather/now"
            headers = {"X-QW-Api-Key": self._qweather_key}
            resp = requests.get(
                url,
                params={"location": "116.41,39.92"},
                headers=headers,
                timeout=10,
                proxies=self._proxies,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "200":
                    return True
                log.warning(f"和风天气探活失败（API code={data.get('code')}）")
                return False
            log.warning(f"和风天气探活失败（HTTP {resp.status_code}）")
            return False
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning(f"和风天气探活失败（网络不可达）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 HTTP，无需操作。"""
        self._connected = False
        log.info("和风天气已断开")

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
                error="qweather 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "qweather_now":
            yield from self._fetch_now(payload, policy)
        elif capability == "qweather_forecast":
            yield from self._fetch_forecast(payload, policy)
        elif capability == "qweather_full":
            yield from self._fetch_now(payload, policy)
            yield from self._fetch_forecast(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 实时天气 ----

    def _fetch_now(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取 40 个城市的实时天气，每城市一行。"""
        if not self._qweather_key or not self._api_host:
            yield FetchResult(
                table=_TBL_WEATHER_DATA,
                columns=_WEATHER_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="QWEATHER_API_KEY 或 QWEATHER_API_HOST 未配置",
            )
            return

        today = datetime.date.today()
        iso_today = today.isoformat()
        rows: list[tuple] = []
        t0 = now_utc()

        for city_name, lon, lat in _QWEATHER_CITIES:
            location = f"{lon},{lat}"
            try:
                data = self._call_api("/weather/now", location, policy)
                now_data = data.get("now", {})
                rows.append(
                    (
                        iso_today,
                        location,
                        city_name,
                        "now",
                        iso_today,
                        _safe_float(now_data.get("temp")),
                        None,  # temp_max — 实时天气无最高温
                        None,  # temp_min — 实时天气无最低温
                        _safe_float(now_data.get("feelsLike")),
                        now_data.get("text", ""),
                        now_data.get("icon", ""),
                        _safe_float(now_data.get("humidity")),
                        _safe_float(now_data.get("precip")),
                        _safe_float(now_data.get("pressure")),
                        _safe_float(now_data.get("vis")),
                        now_data.get("windDir", ""),
                        now_data.get("windScale", ""),
                        _safe_float(now_data.get("windSpeed")),
                        now_data.get("cloud", ""),
                        _safe_float(now_data.get("dew")),
                    )
                )
                self._log.info("和风天气 now %s: %s°C %s", city_name, now_data.get("temp"), now_data.get("text"))
            except Exception as e:  # noqa: BLE001 — 5.135治标
                self._log.warning(f"和风天气 now {city_name} 获取失败: {e}")
            time.sleep(_QWEATHER_REQUEST_INTERVAL)

        yield FetchResult(
            table=_TBL_WEATHER_DATA,
            columns=_WEATHER_COLUMNS,
            rows=rows,
            last_key=iso_today,
            elapsed_sec=seconds_since(t0),
        )

    # ---- 7天预报 ----

    def _fetch_forecast(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取 40 个城市的 7 天预报，每城市每天一行。"""
        if not self._qweather_key or not self._api_host:
            yield FetchResult(
                table=_TBL_WEATHER_DATA,
                columns=_WEATHER_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="QWEATHER_API_KEY 或 QWEATHER_API_HOST 未配置",
            )
            return

        today = datetime.date.today()
        iso_today = today.isoformat()
        rows: list[tuple] = []
        t0 = now_utc()

        for city_name, lon, lat in _QWEATHER_CITIES:
            location = f"{lon},{lat}"
            try:
                data = self._call_api("/weather/7d", location, policy)
                daily_list = data.get("daily", [])
                for d in daily_list:
                    fx_date = d.get("fxDate", "")
                    if not fx_date:
                        continue
                    rows.append(
                        (
                            iso_today,
                            location,
                            city_name,
                            "forecast",
                            fx_date,
                            None,  # temp — 预报用 temp_max/temp_min
                            _safe_float(d.get("tempMax")),
                            _safe_float(d.get("tempMin")),
                            None,  # feels_like — 预报无体感温度
                            d.get("textDay", ""),
                            d.get("iconDay", ""),
                            _safe_float(d.get("humidity")),
                            _safe_float(d.get("precip")),
                            _safe_float(d.get("pressure")),
                            _safe_float(d.get("vis")),
                            d.get("windDirDay", ""),
                            d.get("windScaleDay", ""),
                            _safe_float(d.get("windSpeedDay")),
                            d.get("cloud", ""),
                            _safe_float(d.get("dew")),
                        )
                    )
                self._log.info("和风天气 7d %s: %d 天预报", city_name, len(daily_list))
            except Exception as e:  # noqa: BLE001 — 5.135治标
                self._log.warning(f"和风天气 7d {city_name} 获取失败: {e}")
            time.sleep(_QWEATHER_REQUEST_INTERVAL)

        yield FetchResult(
            table=_TBL_WEATHER_DATA,
            columns=_WEATHER_COLUMNS,
            rows=rows,
            last_key=iso_today,
            elapsed_sec=seconds_since(t0),
        )

    # ---- API 调用 ----

    def _call_api(
        self,
        endpoint: str,
        location: str,
        policy: SourcePolicy,
    ) -> dict:
        """调用和风天气 API，返回 JSON 响应的 dict。

        认证方式：X-QW-Api-Key 请求头（2026 年起公共 key 查询参数已弃用）。
        API Host 从 QWEATHER_API_HOST 环境变量读取（专属 API Host）。

        和风天气 API 返回 HTTP 200 + JSON code 字段：
        - code=200: 成功
        - 其他: API 错误（401=鉴权失败, 402=超配额, 404=找不到位置...）

        Raises:
            RuntimeError: API 返回非 200 code
        """
        url = f"https://{self._api_host}{_QWEATHER_API_PATH}{endpoint}"
        headers = {"X-QW-Api-Key": self._qweather_key}
        params = {"location": location}

        resp = self._call_with_policy(
            requests.get,
            policy,
            url,
            params=params,
            headers=headers,
            timeout=_QWEATHER_TIMEOUT,
            proxies=self._proxies,
        )
        data = resp.json()
        code = data.get("code")
        if code != "200":
            raise RuntimeError(f"和风天气 API 错误: code={code}, endpoint={endpoint}, location={location}")  # noqa: MSG-EXPOSURE — endpoint=和风公开 API 路径段、location=城市名，均非凭据
        return data
