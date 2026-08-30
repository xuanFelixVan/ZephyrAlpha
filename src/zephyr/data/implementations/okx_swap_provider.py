# [BLUEPRINT] MOD-MKT-DATA | docs/03_modules/_domain_mkt_data/vendor_base/blueprint.md
# [MODULE] zephyr.data.implementations.okx_swap_provider
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.provider_base
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] planned
# [INVARIANTS] 公开端点无需签名；资金费率历史分页幂等（同区间重复拉取=同数据）；返回 FetchResult 不写 CH
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §4.4 CAND-CRYPTO-003
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HTTP 5xx->retry；4xx->RuntimeError；API code!=0->FetchResult(error=...)
# [TESTS] tests/zephyr/data/test_okx_swap_provider.py
# [A_module] module_id=MOD-MKT-DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
OKX 永续合约数据 Provider（CAND-CRYPTO-003，94号 §4.4 Phase 2 数据集）。

公开 REST 端点（无需签名）采集永续合约四类专属数据：
- 资金费率历史：GET /api/v5/public/funding-rate-history（分页 before=毫秒时间戳，100 条/页）
- 持仓量 OI：GET /api/v5/public/open-interest?instType=SWAP（当前快照，轮询积累）
- 标记价格：GET /api/v5/public/mark-price?instType=SWAP（当前快照）
- 基差：标记价格(SWAP) - 现货指数价（GET /api/v5/market/index-tickers），计算衍生

限频：20 req/2s（OKX V5 公开端点限制），provider_base._rate_limit_sleep 自动限流。
爆仓数据（liquidation）OKX 仅 WS 推送无历史回填，不在本 provider 范围（registry 风险提示项）。

instId 约定：永续合约为 BTC-USDT-SWAP 形式；现货指数价对应 BTC-USDT。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: okx_swap_provider.py
# 层: 算法
# - id: A1
#   name_zh: ① OkxSwapProvider
#   name_en: OkxSwapProvider
#   intro: OKX 永续合约数据 Provider（CAND-CRYPTO-003）。
#   desc: OKX 永续合约数据 Provider（CAND-CRYPTO-003）。 公开 REST 端点（无需签名），shared 线程安全模型。 已知问题：OI/标记价格/基差为当前快…；公共方法（定义序）: connect…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: OkxSwapProvider
#   downstream: zephyr.data.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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

if TYPE_CHECKING:
    from zephyr.data.policy_registry import SourcePolicy

# OKX V5 公开端点（永续合约数据族）
_BASE_URL = "https://www.okx.com"
_FUNDING_RATE_URL = f"{_BASE_URL}/api/v5/public/funding-rate"
_FUNDING_RATE_HISTORY_URL = f"{_BASE_URL}/api/v5/public/funding-rate-history"
_OPEN_INTEREST_URL = f"{_BASE_URL}/api/v5/public/open-interest"
_MARK_PRICE_URL = f"{_BASE_URL}/api/v5/public/mark-price"
_INDEX_TICKERS_URL = f"{_BASE_URL}/api/v5/market/index-tickers"

# 资金费率历史列名
_FUNDING_RATE_COLUMNS = [
    "symbol",
    "funding_time",
    "funding_rate",
    "realized_rate",
    "method",
]

# 持仓量 OI 列名
_OPEN_INTEREST_COLUMNS = [
    "symbol",
    "ts",
    "oi",
    "oi_ccy",
    "oi_usd",
]

# 标记价格列名
_MARK_PRICE_COLUMNS = [
    "symbol",
    "ts",
    "mark_px",
]

# 基差列名（mark_px - index_px 衍生）
_BASIS_COLUMNS = [
    "symbol",
    "ts",
    "mark_px",
    "index_px",
    "basis",
    "basis_pct",
]


def _ms_to_iso(ts_ms: int) -> str:
    """毫秒时间戳 → UTC ISO 字符串。"""
    return datetime.datetime.fromtimestamp(ts_ms / 1000, tz=datetime.timezone.utc).isoformat()


class OkxSwapProvider(IngestProviderBase):
    """OKX 永续合约数据 Provider（CAND-CRYPTO-003）。

    公开 REST 端点（无需签名），shared 线程安全模型。
    已知问题：OI/标记价格/基差为当前快照（无历史回填接口），需轮询积累；
    爆仓数据仅 WS 推送，不在本 provider 范围。
    """

    source_name: str = "okx_swap"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="okx_swap",
        display_name="OKX 永续合约",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=10,  # 20req/2s = 10/s 保守取 10
        capabilities=[
            CapabilityContract(
                "funding_rate_history",
                supports_symbols_null=False,  # 必须显式传 symbols（BTC-USDT-SWAP）
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="swap",
            ),
            CapabilityContract(
                "open_interest",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,  # 当前快照
                expected_market="crypto",
                expected_variety="swap",
            ),
            CapabilityContract(
                "mark_price",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,  # 当前快照
                expected_market="crypto",
                expected_variety="swap",
            ),
            CapabilityContract(
                "basis",
                supports_symbols_null=False,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,  # 当前快照（mark_px - index_px 衍生）
                expected_market="crypto",
                expected_variety="swap",
            ),
        ],
        known_issues=[
            "公开端点限频 20req/2s",
            "OI/标记价格/基差仅当前快照，需轮询积累",
            "爆仓数据仅 WS 推送无历史回填（不在本 provider 范围）",
        ],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：公开端点无需密钥，直接标记连接。"""
        self._connected = True
        self._log.info("OKX Swap 已连接（公开 REST 端点，无需签名）")

    def health_check(self) -> bool:
        """探活：请求 BTC-USDT-SWAP 当前资金费率。"""
        try:
            resp = self._http_get(
                _FUNDING_RATE_URL,
                timeout=10,
                params={"instId": "BTC-USDT-SWAP"},
            )
            data = resp.json()
            return data.get("code") == "0" and len(data.get("data", [])) > 0
        except Exception as e:  # noqa: BLE001 — 探活失败不阻断
            self._log.warning("OKX Swap 探活失败: %s", e)
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 REST，直接标记断开。"""
        self._connected = False
        self._log.info("OKX Swap 已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 capability 路由到具体获取方法。"""
        if not self._connected:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="okx_swap 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "funding_rate_history":
            yield from self._fetch_funding_rate_history(payload, policy)
        elif capability == "open_interest":
            yield from self._fetch_open_interest(payload, policy)
        elif capability == "mark_price":
            yield from self._fetch_mark_price(payload, policy)
        elif capability == "basis":
            yield from self._fetch_basis(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 公共校验 ----

    def _require_symbols(self, payload: FetchPayload, capability: str) -> list[str] | None:
        """校验 symbols 显式传入，未传返回 None。"""
        symbols = payload.symbols or []
        if not symbols:
            return None
        return symbols

    def _symbols_error_result(self, payload: FetchPayload, capability: str) -> FetchResult:
        return FetchResult(
            table=payload.table,
            columns=[],
            rows=[],
            last_key="",
            elapsed_sec=0.0,
            error=f"{capability} 必须显式传 symbols（如 BTC-USDT-SWAP）",
        )

    # ---- 资金费率历史 ----

    def _fetch_funding_rate_history(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """拉取资金费率历史（公开端点，分页全覆盖）。

        /api/v5/public/funding-rate-history 时间倒序返回（最新在前），
        分页用 before=最早 fundingTime-1 向前翻页，100 条/页。
        """
        symbols = self._require_symbols(payload, "funding_rate_history")
        if symbols is None:
            yield self._symbols_error_result(payload, "funding_rate_history")
            return

        start = payload.start or datetime.date.today() - datetime.timedelta(days=90)
        end = payload.end or datetime.date.today()
        end_ts_ms = int(datetime.datetime.combine(end, datetime.time.max).timestamp() * 1000)
        start_ts_ms = int(datetime.datetime.combine(start, datetime.time.min).timestamp() * 1000)

        for symbol in symbols:
            all_rows: list[tuple] = []
            current_before = end_ts_ms

            while current_before > start_ts_ms:
                t0 = time.time()
                try:
                    resp = self._call_with_policy(
                        self._http_get,
                        policy,
                        _FUNDING_RATE_HISTORY_URL,
                        timeout=30,
                        params={
                            "instId": symbol,
                            "before": str(current_before),
                            "limit": "100",
                        },
                    )
                    data = resp.json()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    yield FetchResult(
                        table=payload.table,
                        columns=_FUNDING_RATE_COLUMNS,
                        rows=all_rows,
                        last_key=str(current_before),
                        elapsed_sec=time.time() - t0,
                        error=f"OKX API 请求失败: {e}",
                    )
                    return

                if data.get("code") != "0":
                    yield FetchResult(
                        table=payload.table,
                        columns=_FUNDING_RATE_COLUMNS,
                        rows=all_rows,
                        last_key=str(current_before),
                        elapsed_sec=time.time() - t0,
                        error=f"OKX API 错误: {data.get('msg', 'unknown')}",
                    )
                    return

                records = data.get("data", [])
                if not records:
                    break  # 无更多数据

                for rec in records:
                    ts_ms = int(rec["fundingTime"])
                    if ts_ms < start_ts_ms or ts_ms > end_ts_ms:
                        continue
                    all_rows.append(
                        (
                            symbol,
                            _ms_to_iso(ts_ms),
                            float(rec["fundingRate"]),
                            float(rec.get("realizedRate") or rec["fundingRate"]),
                            rec.get("method", ""),
                        )
                    )

                # 分页：最早一条的 fundingTime - 1ms
                earliest_ts = min(int(rec["fundingTime"]) for rec in records)
                if earliest_ts <= start_ts_ms:
                    break
                current_before = earliest_ts - 1

            elapsed = time.time() - t0
            # last_key=最大 funding_time ISO（断点续传键）
            last_key = max(r[1] for r in all_rows) if all_rows else ""
            yield FetchResult(
                table=payload.table,
                columns=_FUNDING_RATE_COLUMNS,
                rows=all_rows,
                last_key=last_key,
                elapsed_sec=elapsed,
            )

    # ---- 持仓量 OI（当前快照） ----

    def _fetch_open_interest(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """拉取持仓量 OI 当前快照（/api/v5/public/open-interest?instType=SWAP）。"""
        symbols = self._require_symbols(payload, "open_interest")
        if symbols is None:
            yield self._symbols_error_result(payload, "open_interest")
            return

        for symbol in symbols:
            t0 = time.time()
            try:
                resp = self._call_with_policy(
                    self._http_get,
                    policy,
                    _OPEN_INTEREST_URL,
                    timeout=30,
                    params={"instType": "SWAP", "instId": symbol},
                )
                data = resp.json()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                yield FetchResult(
                    table=payload.table,
                    columns=_OPEN_INTEREST_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=f"OKX API 请求失败: {e}",
                )
                return

            if data.get("code") != "0":
                yield FetchResult(
                    table=payload.table,
                    columns=_OPEN_INTEREST_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=f"OKX API 错误: {data.get('msg', 'unknown')}",
                )
                return

            rows: list[tuple] = []
            for rec in data.get("data", []):
                ts_ms = int(rec["ts"])
                rows.append(
                    (
                        symbol,
                        _ms_to_iso(ts_ms),
                        float(rec["oi"]),
                        float(rec.get("oiCcy") or 0.0),
                        float(rec.get("oiUsd") or 0.0),
                    )
                )

            last_key = max(r[1] for r in rows) if rows else ""
            yield FetchResult(
                table=payload.table,
                columns=_OPEN_INTEREST_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.time() - t0,
            )

    # ---- 标记价格（当前快照） ----

    def _fetch_mark_price(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """拉取标记价格当前快照（/api/v5/public/mark-price?instType=SWAP）。"""
        symbols = self._require_symbols(payload, "mark_price")
        if symbols is None:
            yield self._symbols_error_result(payload, "mark_price")
            return

        for symbol in symbols:
            t0 = time.time()
            try:
                resp = self._call_with_policy(
                    self._http_get,
                    policy,
                    _MARK_PRICE_URL,
                    timeout=30,
                    params={"instType": "SWAP", "instId": symbol},
                )
                data = resp.json()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                yield FetchResult(
                    table=payload.table,
                    columns=_MARK_PRICE_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=f"OKX API 请求失败: {e}",
                )
                return

            if data.get("code") != "0":
                yield FetchResult(
                    table=payload.table,
                    columns=_MARK_PRICE_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=f"OKX API 错误: {data.get('msg', 'unknown')}",
                )
                return

            rows: list[tuple] = []
            for rec in data.get("data", []):
                ts_ms = int(rec["ts"])
                rows.append(
                    (
                        symbol,
                        _ms_to_iso(ts_ms),
                        float(rec["markPx"]),
                    )
                )

            last_key = max(r[1] for r in rows) if rows else ""
            yield FetchResult(
                table=payload.table,
                columns=_MARK_PRICE_COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.time() - t0,
            )

    # ---- 基差（标记价格 - 现货指数价，衍生计算） ----

    @staticmethod
    def _spot_index_inst_id(swap_symbol: str) -> str:
        """永续合约 instId → 现货指数 instId（BTC-USDT-SWAP → BTC-USDT）。"""
        if swap_symbol.endswith("-SWAP"):
            return swap_symbol[: -len("-SWAP")]
        return swap_symbol

    def _fetch_basis(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """拉取基差（SWAP 标记价格 - 现货指数价，两公开端点衍生计算）。"""
        symbols = self._require_symbols(payload, "basis")
        if symbols is None:
            yield self._symbols_error_result(payload, "basis")
            return

        for symbol in symbols:
            t0 = time.time()
            try:
                # 1) SWAP 标记价格
                mark_resp = self._call_with_policy(
                    self._http_get,
                    policy,
                    _MARK_PRICE_URL,
                    timeout=30,
                    params={"instType": "SWAP", "instId": symbol},
                )
                mark_data = mark_resp.json()
                # 2) 现货指数价
                index_resp = self._call_with_policy(
                    self._http_get,
                    policy,
                    _INDEX_TICKERS_URL,
                    timeout=30,
                    params={"instId": self._spot_index_inst_id(symbol)},
                )
                index_data = index_resp.json()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                yield FetchResult(
                    table=payload.table,
                    columns=_BASIS_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error=f"OKX API 请求失败: {e}",
                )
                return

            for payload_data, label in ((mark_data, "mark-price"), (index_data, "index-tickers")):
                if payload_data.get("code") != "0":
                    yield FetchResult(
                        table=payload.table,
                        columns=_BASIS_COLUMNS,
                        rows=[],
                        last_key="",
                        elapsed_sec=time.time() - t0,
                        error=f"OKX API 错误({label}): {payload_data.get('msg', 'unknown')}",
                    )
                    return

            mark_records = mark_data.get("data", [])
            index_records = index_data.get("data", [])
            if not mark_records or not index_records:
                yield FetchResult(
                    table=payload.table,
                    columns=_BASIS_COLUMNS,
                    rows=[],
                    last_key="",
                    elapsed_sec=time.time() - t0,
                    error="OKX API 返回空数据（mark-price 或 index-tickers）",
                )
                return

            mark_px = float(mark_records[0]["markPx"])
            index_px = float(index_records[0]["idxPx"])
            ts_ms = int(mark_records[0]["ts"])
            basis = mark_px - index_px
            basis_pct = basis / index_px if index_px else 0.0

            row = (
                symbol,
                _ms_to_iso(ts_ms),
                mark_px,
                index_px,
                basis,
                basis_pct,
            )
            yield FetchResult(
                table=payload.table,
                columns=_BASIS_COLUMNS,
                rows=[row],
                last_key=row[1],
                elapsed_sec=time.time() - t0,
            )
