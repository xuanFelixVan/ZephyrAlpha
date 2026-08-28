# [BLUEPRINT] MOD-MKT-DATA | docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md
# [MODULE] zephyr.data.implementations.okx_provider
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.provider_base, zephyr.shared.security.secrets
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] planned
# [INVARIANTS] 公开端点无需签名；REST 补数幂等（同区间重复拉取=同数据）；返回 FetchResult 不写 CH
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-002
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HTTP 5xx->retry；4xx->RuntimeError；API code!=0->FetchResult(error=...)
# [TESTS] tests/zephyr/data/test_okx_provider.py
# [A_module] module_id=MOD-MKT-DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""OKX 交易所行情 Provider（CAND-CRYPTO-002，94号 Q1 裁定：OKX 备/数据互备源）。

公开 REST 端点拉取 BTC/ETH 现货 K 线数据，接入现有 WAL→CH 落库管道。
- 近期 3 个月：GET /api/v5/market/candles
- 历史完整：GET /api/v5/market/history-candles（主流币种）
- 公开端点无需 API 密钥（行情数据公开）；私有端点（交易/账户）需签名（Phase 2）
- 限频：20 req/2s（OKX V5 公开端点限制），provider_base._rate_limit_sleep 自动限流

响应格式：{code: "0", data: [[ts_ms, open, high, low, close, vol, volCcy, volCcyQuote, confirm], ...]}
时间倒序（最新在前），分页用 after/before 毫秒时间戳。
"""

from __future__ import annotations

import datetime
import time
from typing import TYPE_CHECKING, Iterator

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.shared.security.secrets import get_secret_or_default

if TYPE_CHECKING:
    from zephyr.data.policy_registry import SourcePolicy

# OKX V5 公开端点
_BASE_URL = "https://www.okx.com"
_CANDLES_URL = f"{_BASE_URL}/api/v5/market/candles"
_HISTORY_CANDLES_URL = f"{_BASE_URL}/api/v5/market/history-candles"

# bar 映射：内部周期名 → OKX bar 参数
_BAR_MAP: dict[str, str] = {
    "1d": "1D",
    "4h": "4H",
    "1h": "1H",
}

# K 线列名（与 CH kline 表对齐，crypto 版）
_KLINE_COLUMNS = [
    "symbol",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "bar",
    "confirm",
]


class OkxProvider(IngestProviderBase):
    """OKX 交易所行情 Provider。

    公开 REST 端点（无需签名），shared 线程安全模型。
    已知问题：公开端点限频 20req/2s；历史 K 线仅主流币种。
    """

    source_name: str = "okx"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="okx",
        display_name="OKX 交易所",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=10,  # 20req/2s = 10/s 保守取 10
        capabilities=[
            CapabilityContract(
                "kline_crypto",
                supports_symbols_null=False,  # 必须显式传 symbols（BTC-USDT/ETH-USDT）
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="spot",
            ),
        ],
        known_issues=["公开端点限频 20req/2s", "历史 K 线仅主流币种", "近期 3 个月与历史接口分离"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：验证 API 密钥可用性（公开端点可选，私有端点必需）。"""
        api_key = get_secret_or_default("OKX_API_KEY", "")
        if api_key:
            self._log.info("OKX API Key 已配置（私有端点可用）")
        else:
            self._log.info("OKX API Key 未配置（仅公开行情端点可用）")
        self._connected = True
        self._log.info("OKX 已连接（公开 REST 端点）")

    def health_check(self) -> bool:
        """探活：请求 BTC-USDT 最新 1 根日 K。"""
        try:
            resp = self._http_get(
                _CANDLES_URL,
                timeout=10,
                params={"instId": "BTC-USDT", "bar": "1D", "limit": "1"},
            )
            data = resp.json()
            return data.get("code") == "0" and len(data.get("data", [])) > 0
        except Exception as e:  # noqa: BLE001 — 探活失败不阻断
            self._log.warning("OKX 探活失败: %s", e)
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 REST，直接标记断开。"""
        self._connected = False
        self._log.info("OKX 已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """按 capability 路由到具体获取方法。"""
        if not self._connected:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="okx 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "kline_crypto":
            yield from self._fetch_kline_crypto(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- K 线拉取 ----

    def _fetch_kline_crypto(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """拉取数字货币 K 线（公开端点，分页全覆盖）。

        近期 3 个月走 /candles，更早走 /history-candles。
        时间倒序返回，分页用 before=最早时间戳-1 向前翻页。
        """
        symbols = payload.symbols or []
        if not symbols:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="kline_crypto 必须显式传 symbols（如 BTC-USDT/ETH-USDT）",
            )
            return

        bar = (payload.extra or {}).get("bar", "1d")
        okx_bar = _BAR_MAP.get(bar, "1D")
        start = payload.start or datetime.date.today() - datetime.timedelta(days=365)
        end = payload.end or datetime.date.today()

        # 转毫秒时间戳
        end_ts_ms = int(datetime.datetime.combine(end, datetime.time.max).timestamp() * 1000)
        start_ts_ms = int(datetime.datetime.combine(start, datetime.time.min).timestamp() * 1000)

        # 3 个月分界（OKX /candles 只支持近 3 个月）
        three_months_ago_ms = int((datetime.datetime.now() - datetime.timedelta(days=90)).timestamp() * 1000)

        for symbol in symbols:
            all_rows: list[tuple] = []
            current_before = end_ts_ms

            while current_before > start_ts_ms:
                t0 = time.time()
                # 选择端点：近期用 /candles，历史用 /history-candles
                if current_before > three_months_ago_ms and start_ts_ms < three_months_ago_ms:
                    # 跨期：先拉历史段
                    url = _HISTORY_CANDLES_URL
                elif current_before > three_months_ago_ms:
                    url = _CANDLES_URL
                else:
                    url = _HISTORY_CANDLES_URL

                try:
                    resp = self._call_with_policy(
                        self._http_get,
                        policy,
                        url,
                        timeout=30,
                        params={
                            "instId": symbol,
                            "bar": okx_bar,
                            "before": str(current_before),
                            "limit": "300",
                        },
                    )
                    data = resp.json()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    yield FetchResult(
                        table=payload.table,
                        columns=_KLINE_COLUMNS,
                        rows=all_rows,
                        last_key=str(current_before),
                        elapsed_sec=time.time() - t0,
                        error=f"OKX API 请求失败: {e}",
                    )
                    return

                if data.get("code") != "0":
                    yield FetchResult(
                        table=payload.table,
                        columns=_KLINE_COLUMNS,
                        rows=all_rows,
                        last_key=str(current_before),
                        elapsed_sec=time.time() - t0,
                        error=f"OKX API 错误: {data.get('msg', 'unknown')}",
                    )
                    return

                candles = data.get("data", [])
                if not candles:
                    break  # 无更多数据

                for c in candles:
                    ts_ms = int(c[0])
                    trade_date = datetime.datetime.fromtimestamp(ts_ms / 1000, tz=datetime.timezone.utc).date()
                    all_rows.append((
                        symbol,
                        trade_date.isoformat(),
                        float(c[1]),  # open
                        float(c[2]),  # high
                        float(c[3]),  # low
                        float(c[4]),  # close
                        float(c[5]),  # volume
                        float(c[6]) if len(c) > 6 else 0.0,  # volCcy (amount)
                        okx_bar,
                        int(c[8]) if len(c) > 8 else 0,  # confirm
                    ))

                # 分页：最早一根的时间戳 - 1ms
                earliest_ts = int(candles[-1][0])
                if earliest_ts <= start_ts_ms:
                    break
                current_before = earliest_ts - 1

            elapsed = time.time() - t0
            # last_key=最大 trade_date（断点续传键），r[1]=trade_date ISO 字符串
            last_key = max(r[1] for r in all_rows) if all_rows else ""
            yield FetchResult(
                table=payload.table,
                columns=_KLINE_COLUMNS,
                rows=all_rows,
                last_key=last_key,
                elapsed_sec=elapsed,
            )
