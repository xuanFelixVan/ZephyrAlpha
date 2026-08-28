# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.onchain_provider
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.provider_base, zephyr.shared.security.secrets
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] planned
# [INVARIANTS] 只读不交互（不签名不上链）；无付费 key 时走 mock 序列（is_mock=1）；返回 FetchResult 不写 CH
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-004
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HTTP 5xx->retry；4xx->RuntimeError；API 异常->FetchResult(error=...)
# [TESTS] tests/zephyr/data/test_onchain_provider.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""链上数据 Provider 骨架（CAND-CRYPTO-004，94号 §5：链上数据接入）。

数字货币特有另类数据源（A股无对应物），只读不交互：
- Glassnode 免费端点：交易所净流入（exchange netflow）、活跃地址（active addresses）
- CryptoQuant 免费端点：稳定币流动（stablecoin flows，交易所稳定币储备/净流）

付费 API 密钥注入接口（trigger: paid_api_key_configured）：
- get_service_secret("GLASSNODE_API_KEY", "glassnode", required=False)
- get_service_secret("CRYPTOQUANT_API_KEY", "cryptoquant", required=False)
密钥未配置时使用确定性 mock 序列（is_mock=1）保证管道可跑通；
密钥配置后自动切换真实 HTTP 端点（is_mock=0），无需改代码。
"""

from __future__ import annotations

import datetime
import hashlib
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

# Glassnode API v1（免费 tier：日频核心指标，需注册 key；无 key 时 mock）
_GLASSNODE_BASE = "https://api.glassnode.com/v1/metrics"
_GLASSNODE_NETFLOW_URL = f"{_GLASSNODE_BASE}/distribution/exchange_net_position_change"
_GLASSNODE_ACTIVE_ADDR_URL = f"{_GLASSNODE_BASE}/addresses/active_count"

# CryptoQuant 免费端点（稳定币交易所净流；无 key 时 mock）
_CRYPTOQUANT_BASE = "https://api.cryptoquant.com/v1"
_CRYPTOQUANT_STABLECOIN_URL = f"{_CRYPTOQUANT_BASE}/erc20/exchange-flows/netflow"

# 链上指标列名（与 alt_data 管道对齐）
_ONCHAIN_COLUMNS: Final = [
    "metric",
    "asset",
    "trade_date",
    "value",
    "source",
    "is_mock",
]

# capability → (source, endpoint, 默认资产)
_CAPABILITY_ROUTES: Final[dict[str, tuple[str, str, str]]] = {
    "exchange_netflow": ("glassnode", _GLASSNODE_NETFLOW_URL, "BTC"),
    "active_addresses": ("glassnode", _GLASSNODE_ACTIVE_ADDR_URL, "BTC"),
    "stablecoin_flows": ("cryptoquant", _CRYPTOQUANT_STABLECOIN_URL, "USDT"),
}

# capability → API key（服务名, 环境变量名）
_CAPABILITY_KEYS: Final[dict[str, tuple[str, str]]] = {
    "exchange_netflow": ("glassnode", "GLASSNODE_API_KEY"),
    "active_addresses": ("glassnode", "GLASSNODE_API_KEY"),
    "stablecoin_flows": ("cryptoquant", "CRYPTOQUANT_API_KEY"),
}


@dataclass
class _LiveFetchRequest:
    """真实端点拉取请求参数包（§5.150 Long Parameter List 规避）。"""

    url: str
    api_key: str
    asset: str
    start: datetime.date
    end: datetime.date
    capability: str
    source: str


class OnchainProvider(IngestProviderBase):
    """链上数据 Provider（Glassnode/CryptoQuant 免费端点骨架）。

    无付费 key 时输出确定性 mock 序列（is_mock=1），
    配置 key 后切换真实端点（is_mock=0）。shared 线程安全模型。
    """

    source_name: str = "onchain"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="onchain",
        display_name="链上数据(Glassnode/CryptoQuant)",
        auth_type="api_key_optional",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=10,
        capabilities=[
            CapabilityContract(
                "exchange_netflow",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="onchain",
            ),
            CapabilityContract(
                "active_addresses",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="onchain",
            ),
            CapabilityContract(
                "stablecoin_flows",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="onchain",
            ),
        ],
        known_issues=[
            "免费 tier 限频紧（Glassnode 日频核心指标）",
            "无付费 key 时输出 mock 序列（is_mock=1）",
            "付费指标（MVRV/SOPR）待 paid_api_key_configured 后扩展",
        ],
    )

    def __init__(self):
        super().__init__()
        self._api_keys: dict[str, str] = {}  # service -> api_key

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：注入付费 API 密钥（可选），未配置则 mock 模式。"""
        for service, key_name in {("glassnode", "GLASSNODE_API_KEY"), ("cryptoquant", "CRYPTOQUANT_API_KEY")}:
            key = get_service_secret(key_name, service, required=False)
            if key:
                self._api_keys[service] = key
                self._log.info("%s API Key 已配置（真实端点模式）", service)
            else:
                self._log.info("%s API Key 未配置（mock 序列模式）", service)
        self._connected = True
        self._log.info("Onchain 已连接（%d/2 源为真实端点）", len(self._api_keys))

    def health_check(self) -> bool:
        """探活：有 key 的源 ping 真实端点；无 key 的源 mock 模式恒可用。"""
        ok = True
        for service, (url, asset) in {
            "glassnode": (_GLASSNODE_ACTIVE_ADDR_URL, "BTC"),
            "cryptoquant": (_CRYPTOQUANT_STABLECOIN_URL, "USDT"),
        }.items():
            if service not in self._api_keys:
                continue  # mock 模式无需探活
            try:
                params = {"api_key": self._api_keys[service], "a": asset, "i": "24h", "limit": 1}
                resp = self._http_get(url, timeout=10, params=params)
                resp.json()
            except Exception as e:  # noqa: BLE001 — 探活失败不阻断
                self._log.warning("%s 探活失败: %s", service, e)
                ok = False
        return ok

    def disconnect(self) -> None:
        """断开连接：无状态 REST，清空已注入密钥并标记断开。"""
        self._api_keys.clear()
        self._connected = False
        self._log.info("Onchain 已断开（API Key 缓存已清空）")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """按 capability 路由到 Glassnode/CryptoQuant 端点（或 mock 序列）。"""
        if not self._connected:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="onchain 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability", "")
        supported = capability == "exchange_netflow" or capability == "active_addresses" or capability == "stablecoin_flows"
        if not supported:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )
            return

        symbols = payload.symbols or []
        if not symbols:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"{capability} 必须显式传 symbols（如 BTC/ETH 或 USDT/USDC）",
            )
            return

        if capability == "exchange_netflow":
            yield from self._fetch_exchange_netflow(payload, policy)
        elif capability == "active_addresses":
            yield from self._fetch_active_addresses(payload, policy)
        else:
            yield from self._fetch_stablecoin_flows(payload, policy)

    # ---- capability 拉取入口（CAP-CONSISTENCY：每 capability 一个 _fetch_<cap> 方法） ----

    def _fetch_exchange_netflow(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """Glassnode 交易所净流入（币进出交易所=潜在卖压信号）。"""
        yield from self._fetch_metric(payload, policy, "exchange_netflow")

    def _fetch_active_addresses(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """Glassnode 活跃地址数（链上活跃度）。"""
        yield from self._fetch_metric(payload, policy, "active_addresses")

    def _fetch_stablecoin_flows(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """CryptoQuant 稳定币交易所净流（干火药购买力）。"""
        yield from self._fetch_metric(payload, policy, "stablecoin_flows")

    # ---- 指标拉取 ----

    def _fetch_metric(self, payload: FetchPayload, policy: "SourcePolicy", capability: str) -> Iterator[FetchResult]:
        """逐资产拉取链上指标日频序列；无 key 时生成确定性 mock 序列。"""
        source, url, _default_asset = _CAPABILITY_ROUTES[capability]
        key_service, key_name = _CAPABILITY_KEYS[capability]
        api_key = self._api_keys.get(key_service, "")

        start = payload.start or datetime.date.today() - datetime.timedelta(days=90)
        end = payload.end or datetime.date.today()

        for asset in payload.symbols or []:
            t0 = now_utc()
            if api_key:
                request = _LiveFetchRequest(
                    url=url,
                    api_key=api_key,
                    asset=asset,
                    start=start,
                    end=end,
                    capability=capability,
                    source=source,
                )
                rows, error = self._fetch_live(request, policy)
            else:
                rows, error = self._mock_series(capability, asset, start, end, source), None

            last_key = max((r[2] for r in rows), default="")
            yield FetchResult(
                table=payload.table,
                columns=_ONCHAIN_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=(now_utc() - t0).total_seconds(),
                error=error,
            )

    def _fetch_live(
        self,
        request: _LiveFetchRequest,
        policy: "SourcePolicy",
    ) -> tuple[list[tuple], str | None]:
        """真实端点拉取（付费 key 已配置）。返回 (rows, error)。"""
        params = {
            "api_key": request.api_key,
            "a": request.asset,
            "i": "24h",
            "s": int(datetime.datetime.combine(request.start, datetime.time.min).timestamp()),
            "u": int(datetime.datetime.combine(request.end, datetime.time.max).timestamp()),
        }
        try:
            resp = self._call_with_policy(self._http_get, policy, request.url, timeout=30, params=params)
            data = resp.json()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return [], f"{request.source} API 请求失败: {e}"

        if not isinstance(data, list):
            return [], f"{request.source} API 响应格式异常: {str(data)[:120]}"

        rows = []
        for point in data:
            ts = int(point.get("t", 0))
            trade_date = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date()
            rows.append((
                request.capability,
                request.asset,
                trade_date.isoformat(),
                float(point.get("v", 0.0)),
                request.source,
                0,
            ))
        return rows, None

    def _mock_series(
        self,
        capability: str,
        asset: str,
        start: datetime.date,
        end: datetime.date,
        source: str,
    ) -> list[tuple]:
        """确定性 mock 日频序列（无付费 key 时保证管道可跑通）。

        值由 (capability, asset, date) 哈希派生，同输入恒同输出——
        测试可重复，下游管道可联调，is_mock=1 显式标记非真实数据。
        """
        rows = []
        day = start
        while day <= end:
            digest = hashlib.sha256(f"{capability}|{asset}|{day.isoformat()}".encode("utf-8")).hexdigest()
            value = int(digest[:12], 16) / float(0xFFFFFFFFFFFF) * 1000.0 - 500.0
            rows.append((
                capability,
                asset,
                day.isoformat(),
                round(value, 6),
                source,
                1,
            ))
            day += datetime.timedelta(days=1)
        return rows
