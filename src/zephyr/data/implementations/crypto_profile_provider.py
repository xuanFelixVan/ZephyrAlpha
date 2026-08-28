# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.crypto_profile_provider
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.provider_base, zephyr.shared.security.secrets
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] planned
# [INVARIANTS] 只读不交互；统一输出 7 列 (symbol,name,launch_date,circulating_supply,total_supply,website,explorer)；返回 FetchResult 不写 CH
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HTTP 5xx->retry；4xx->RuntimeError；API 异常->FetchResult(error=...)
# [TESTS] tests/zephyr/data/test_crypto_profile_provider.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""币圈档案 Provider（发行/流通/链上信息，CoinGecko/CoinMarketCap 免费 API）。

采集币种档案，覆盖两类信息：
- 基本信息：发行时间（launch_date）/流通量（circulating_supply）/总量（total_supply）/
  官网（website）/白皮书（whitepaper，解析进 CoinProfile 供下游使用）
- 链上信息：合约地址（contract_address，用于构造代币级浏览器链接）/
  区块链浏览器链接（explorer）

统一行格式（7 列，与任务约定一致）：
    (symbol, name, launch_date, circulating_supply, total_supply, website, explorer)

数据源：
- CoinGecko 免费 API（默认，无需 key）：/coins/list 做 symbol→id 映射（进程内缓存），
  /coins/{id} 取 genesis_date / market_data / links / contract_address。
- CoinMarketCap 免费 tier（需注册 key）：/v1/cryptocurrency/info 取官网/白皮书/浏览器/
  合约/date_added，/v1/cryptocurrency/quotes/latest 取流通量/总量。
  key 经 get_service_secret("CMC_API_KEY", "coinmarketcap", required=False) 注入；
  未配置时选 coinmarketcap 源直接报错行，CoinGecko 源不受影响。

代币级浏览器链接：命中 _PLATFORM_EXPLORERS 的平台且有 contract_address 时，
explorer 构造为 {平台浏览器}/token/{contract}（如 USDT→etherscan.io/token/0xdAC17...）；
否则回退 links.blockchain_site 首个非空链接。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Iterator

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.shared.security.secrets import get_service_secret
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    from zephyr.data.policy_registry import SourcePolicy

# CoinGecko 免费 API（无需 key；公开 tier 限频约 10-30 次/分钟）
_COINGECKO_BASE: Final = "https://api.coingecko.com/api/v3"
_COINGECKO_LIST_URL: Final = f"{_COINGECKO_BASE}/coins/list"
_COINGECKO_PING_URL: Final = f"{_COINGECKO_BASE}/ping"

# CoinMarketCap 免费 tier（需 CMC_API_KEY；333 次/日）
_CMC_BASE: Final = "https://pro-api.coinmarketcap.com/v1/cryptocurrency"
_CMC_INFO_URL: Final = f"{_CMC_BASE}/info"
_CMC_QUOTES_URL: Final = f"{_CMC_BASE}/quotes/latest"

# 统一档案列名（任务约定输出格式）
_PROFILE_COLUMNS: Final = [
    "symbol",
    "name",
    "launch_date",
    "circulating_supply",
    "total_supply",
    "website",
    "explorer",
]

_SUPPORTED_SOURCES: Final = ("coingecko", "coinmarketcap")

# CoinGecko asset_platform_id → 平台浏览器 base（用于构造代币级链接）
_PLATFORM_EXPLORERS: Final[dict[str, str]] = {
    "ethereum": "https://etherscan.io",
    "binance-smart-chain": "https://bscscan.com",
    "polygon-pos": "https://polygonscan.com",
    "arbitrum-one": "https://arbiscan.io",
    "optimistic-ethereum": "https://optimistic.etherscan.io",
    "avalanche": "https://snowtrace.io",
    "solana": "https://solscan.io",
    "tron": "https://tronscan.org",
    "base": "https://basescan.org",
}


def _first_non_empty(value: object) -> str:
    """取首个非空字符串；list 逐元素找，str 直取，其余/空返回 ""。"""
    if isinstance(value, list):
        for item in value:
            if item:
                return str(item)
        return ""
    return str(value) if value else ""


def _to_float(value: object) -> float:
    """宽松数值转换，None/非法值归 0.0。"""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


@dataclass
class CoinProfile:
    """币种档案（解析中间态；统一行格式经 to_row() 输出）。

    whitepaper/contract_address 属"支持采集"字段（白皮书、合约地址），
    不进入 7 列统一行——contract_address 已折入 explorer 代币级链接，
    whitepaper 留档供下游（如档案落库扩展列）使用。
    """

    symbol: str
    name: str = ""
    launch_date: str = ""
    circulating_supply: float = 0.0
    total_supply: float = 0.0
    website: str = ""
    whitepaper: str = ""
    contract_address: str = ""
    explorer: str = ""
    source: str = ""

    def to_row(self) -> tuple:
        """统一行格式：(symbol, name, launch_date, circulating_supply, total_supply, website, explorer)。"""
        return (
            self.symbol,
            self.name,
            self.launch_date,
            self.circulating_supply,
            self.total_supply,
            self.website,
            self.explorer,
        )


class CryptoProfileProvider(IngestProviderBase):
    """币圈档案 Provider（CoinGecko 免费 API 默认源 / CoinMarketCap 免费 tier 备选源）。

    shared 线程安全模型；CoinGecko symbol→id 映射进程内缓存（/coins/list 只拉一次）。
    """

    source_name: str = "crypto_profile"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="crypto_profile",
        display_name="币圈档案(CoinGecko/CoinMarketCap)",
        auth_type="api_key_optional",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=10,
        capabilities=[
            CapabilityContract(
                "coin_profile",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,
                expected_market="crypto",
                expected_variety="profile",
            ),
        ],
        known_issues=[
            "CoinGecko 公开 tier 限频紧（约 10-30 次/分钟，超限 429）",
            "CoinMarketCap 免费 tier 需注册 key（333 次/日），未配置时该源不可用",
            "CoinMarketCap date_added 为收录日而非严格发行日（免费字段最接近值）",
        ],
    )

    def __init__(self):
        super().__init__()
        self._cmc_api_key: str = ""
        self._gecko_id_map: dict[str, str] = {}  # symbol(lower) -> coingecko id 缓存

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：注入 CoinMarketCap key（可选）；CoinGecko 免费源无需 key。"""
        key = get_service_secret("CMC_API_KEY", "coinmarketcap", required=False)
        if key:
            self._cmc_api_key = key
            self._log.info("CoinMarketCap API Key 已配置（coinmarketcap 源可用）")
        else:
            self._log.info("CoinMarketCap API Key 未配置（仅 coingecko 源可用）")
        self._connected = True
        self._log.info("CryptoProfile 已连接")

    def health_check(self) -> bool:
        """探活：ping CoinGecko 免费端点（默认源可用即视为健康）。"""
        try:
            resp = self._http_get(_COINGECKO_PING_URL, timeout=10)
            resp.json()
            return True
        except Exception as e:  # noqa: BLE001 — 探活失败不阻断
            self._log.warning("coingecko 探活失败: %s", e)
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 REST，清空 key 与 id 缓存并标记断开。"""
        self._cmc_api_key = ""
        self._gecko_id_map.clear()
        self._connected = False
        self._log.info("CryptoProfile 已断开（key/缓存已清空）")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """按 capability 拉取币种档案（默认 coin_profile）。"""
        if not self._connected:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="crypto_profile 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability", "coin_profile")
        if capability != "coin_profile":
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )
            return

        if not payload.symbols:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="coin_profile 必须显式传 symbols（如 BTC/ETH）",
            )
            return

        yield from self._fetch_coin_profile(payload, policy)

    # ---- capability 拉取入口（CAP-CONSISTENCY：每 capability 一个 _fetch_<cap> 方法） ----

    def _fetch_coin_profile(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """逐币种拉取档案，每币一个 FetchResult（一行 7 列统一格式）。"""
        source = ((payload.extra or {}).get("source") or "coingecko").lower()
        if source not in _SUPPORTED_SOURCES:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported source: {source}（可选 {list(_SUPPORTED_SOURCES)}）",
            )
            return

        for symbol in payload.symbols or []:
            t0 = now_utc()
            if source == "coinmarketcap":
                profile, error = self._fetch_cmc_profile(symbol, policy)
            else:
                profile, error = self._fetch_gecko_profile(symbol, policy)
            rows = [profile.to_row()] if profile else []
            yield FetchResult(
                table=payload.table,
                columns=_PROFILE_COLUMNS,
                rows=rows,
                last_key=symbol,
                elapsed_sec=(now_utc() - t0).total_seconds(),
                error=error,
            )

    # ---- CoinGecko 免费源 ----

    def _resolve_gecko_id(self, symbol: str, policy: "SourcePolicy") -> tuple[str, str | None]:
        """symbol→coingecko id 映射（/coins/list 进程内缓存）。返回 (coin_id, error)。"""
        if not self._gecko_id_map:
            try:
                resp = self._call_with_policy(self._http_get, policy, _COINGECKO_LIST_URL, timeout=30)
                data = resp.json()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                return "", f"coingecko API 请求失败: {e}"
            if not isinstance(data, list):
                return "", f"coingecko API 响应格式异常: {str(data)[:120]}"
            for item in data:
                if isinstance(item, dict):
                    self._gecko_id_map.setdefault(
                        str(item.get("symbol", "")).lower(), str(item.get("id", ""))
                    )
        return self._gecko_id_map.get(symbol.lower(), ""), None

    def _fetch_gecko_profile(self, symbol: str, policy: "SourcePolicy") -> tuple[CoinProfile | None, str | None]:
        """CoinGecko /coins/{id} → CoinProfile。返回 (profile, error)。"""
        coin_id, error = self._resolve_gecko_id(symbol, policy)
        if error:
            return None, error
        if not coin_id:
            return None, f"coingecko 未找到 symbol: {symbol}"

        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false",
        }
        try:
            resp = self._call_with_policy(
                self._http_get, policy, f"{_COINGECKO_BASE}/coins/{coin_id}", timeout=30, params=params
            )
            data = resp.json()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return None, f"coingecko API 请求失败: {e}"
        if not isinstance(data, dict) or "id" not in data:
            return None, f"coingecko API 响应格式异常: {str(data)[:120]}"
        return self._parse_gecko_profile(symbol, data), None

    def _parse_gecko_profile(self, symbol: str, data: dict) -> CoinProfile:
        """解析 CoinGecko 币种详情：基本信息（genesis_date/供应量/官网/白皮书）+ 链上信息（合约/浏览器）。"""
        links = data.get("links") or {}
        market_data = data.get("market_data") or {}
        contract = str(data.get("contract_address") or "")
        platform = str(data.get("asset_platform_id") or "")
        explorer = _first_non_empty(links.get("blockchain_site"))
        platform_base = _PLATFORM_EXPLORERS.get(platform)
        if contract and platform_base:
            explorer = f"{platform_base}/token/{contract}"
        return CoinProfile(
            symbol=symbol.upper(),
            name=str(data.get("name") or ""),
            launch_date=str(data.get("genesis_date") or ""),
            circulating_supply=_to_float(market_data.get("circulating_supply")),
            total_supply=_to_float(market_data.get("total_supply")),
            website=_first_non_empty(links.get("homepage")),
            whitepaper=str(links.get("whitepaper") or ""),
            contract_address=contract,
            explorer=explorer,
            source="coingecko",
        )

    # ---- CoinMarketCap 免费 tier 源 ----

    def _fetch_cmc_profile(self, symbol: str, policy: "SourcePolicy") -> tuple[CoinProfile | None, str | None]:
        """CoinMarketCap /info + /quotes/latest → CoinProfile。返回 (profile, error)。"""
        if not self._cmc_api_key:
            return None, "coinmarketcap 源需要 CMC_API_KEY（connect 时注入，未配置）"
        headers = {"X-CMC_PRO_API_KEY": self._cmc_api_key}
        try:
            info_resp = self._call_with_policy(
                self._http_get, policy, _CMC_INFO_URL, timeout=30, headers=headers, params={"symbol": symbol}
            )
            info = info_resp.json()
            quote_resp = self._call_with_policy(
                self._http_get, policy, _CMC_QUOTES_URL, timeout=30, headers=headers, params={"symbol": symbol}
            )
            quotes = quote_resp.json()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return None, f"coinmarketcap API 请求失败: {e}"
        return self._parse_cmc_profile(symbol, info, quotes)

    def _parse_cmc_profile(
        self, symbol: str, info: dict, quotes: dict
    ) -> tuple[CoinProfile | None, str | None]:
        """解析 CoinMarketCap 响应：info（官网/白皮书/浏览器/合约/date_added）+ quotes（供应量）。"""
        info_data = (info or {}).get("data") or {}
        quote_data = (quotes or {}).get("data") or {}
        meta = info_data.get(symbol.upper()) or info_data.get(symbol) or {}
        if isinstance(meta, list):  # 同名多币时 CMC 返回 list，取首个
            meta = meta[0] if meta else {}
        quote = quote_data.get(symbol.upper()) or quote_data.get(symbol) or {}
        if isinstance(quote, list):
            quote = quote[0] if quote else {}
        if not meta and not quote:
            return None, f"coinmarketcap 未找到 symbol: {symbol}"

        urls = meta.get("urls") or {}
        ca = meta.get("contract_address")
        contract = ""
        if isinstance(ca, list) and ca:
            first = ca[0]
            contract = str(first.get("contract_address") or "") if isinstance(first, dict) else str(first)
        elif isinstance(ca, str):
            contract = ca

        launch = str(meta.get("date_added") or "")
        if "T" in launch:  # "2013-04-28T00:00:00.000Z" → "2013-04-28"
            launch = launch.split("T", 1)[0]

        return CoinProfile(
            symbol=symbol.upper(),
            name=str(meta.get("name") or quote.get("name") or ""),
            launch_date=launch,
            circulating_supply=_to_float(quote.get("circulating_supply")),
            total_supply=_to_float(quote.get("total_supply")),
            website=_first_non_empty(urls.get("website")),
            whitepaper=_first_non_empty(urls.get("whitepaper")),
            contract_address=contract,
            explorer=_first_non_empty(urls.get("explorer")),
            source="coinmarketcap",
        ), None
