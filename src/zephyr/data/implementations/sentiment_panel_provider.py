# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.sentiment_panel_provider
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.provider_base, zephyr.shared.security.secrets
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] skeleton
# [INVARIANTS] 免费公开端点限频保守；返回 FetchResult 不写 CH；骨架能力（ETF/USDT溢价）显式 error 标注不进决策硬链
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-010
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HTTP 5xx->retry；4xx->FetchResult(error=...)；骨架能力->FetchResult(error="骨架...")
# [TESTS] tests/zephyr/data/test_sentiment_panel_provider.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
币圈宏观情绪面板 Provider（CAND-CRYPTO-010，94号 §5 + §9 Q6 裁定）。

轻量日频采集四个宏观情绪指标，定位=市场级风险节流输入（regime 分工：非 alpha 择时）：
- 恐惧贪婪指数（Fear & Greed Index）：alternative.me 免费 API（无需 key）
  GET https://api.alternative.me/fng/?limit=N —— 六因子加权 0-100
- BTC 占比（BTC Dominance）：CoinMarketCap 免费 API（需 CMC_API_KEY，free basic tier）
  GET /v1/global-metrics/quotes/latest —— data.btc_dominance
- ETF 流量（现货 ETF 净流入流出）：公开数据骨架（Farside/SoSoValue 类源待接入）
- USDT 场外溢价（亚洲资金入场指标）：公开数据骨架（C2C 场外公开报价源待接入）

统一行格式：(metric, trade_date, value, value_classification, source, extra)。
骨架能力（ETF/USDT 溢价）返回 error 标注"骨架"，失败降级可见、不进决策硬链。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: sentiment_panel_provider.py
# 层: 算法
# - id: A1
#   name_zh: ① SentimentPanelProvider
#   name_en: SentimentPanelProvider
#   intro: 币圈宏观情绪面板 Provider。
#   desc: 币圈宏观情绪面板 Provider。 免费公开端点（alternative.me 无需 key；CMC 需免费 key），shared 线程安全模型。 已知问题：免费源稳定性（限…；公共方法（定义序）: connect…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SentimentPanelProvider
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
from zephyr.shared.security.secrets import get_secret_or_default

if TYPE_CHECKING:
    from zephyr.data.policy_registry import SourcePolicy

# alternative.me 恐惧贪婪指数（免费，无需 key）
_FNG_URL = "https://api.alternative.me/fng/"

# CoinMarketCap 全球指标（免费 basic tier，需 API key）
_CMC_GLOBAL_URL = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"

# 统一列名（宏观情绪面板，metric 区分指标）
_SENTIMENT_COLUMNS = [
    "metric",
    "trade_date",
    "value",
    "value_classification",
    "source",
    "extra",
]

# 骨架能力标识（数据源待接入，晋升时落地）
_SKELETON_NOTES = {
    "crypto_etf_flow": "ETF 流量数据源骨架——公开源（Farside/SoSoValue 类）待接入，CAND-CRYPTO-010 晋升时落地",
    "crypto_usdt_premium": "USDT 场外溢价数据源骨架——C2C 场外公开报价源待接入，CAND-CRYPTO-010 晋升时落地",
}


class SentimentPanelProvider(IngestProviderBase):
    """币圈宏观情绪面板 Provider。

    免费公开端点（alternative.me 无需 key；CMC 需免费 key），shared 线程安全模型。
    已知问题：免费源稳定性（限频/来源变更）——日频采集+失败降级标注即可。
    """

    source_name: str = "crypto_sentiment_panel"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="crypto_sentiment_panel",
        display_name="币圈宏观情绪面板",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=5,  # 免费源保守限频
        capabilities=[
            CapabilityContract(
                "crypto_fear_greed_index",
                supports_symbols_null=True,  # 宏观指标无需 symbols
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="sentiment",
            ),
            CapabilityContract(
                "crypto_btc_dominance",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,  # 最新快照
                expected_market="crypto",
                expected_variety="sentiment",
            ),
            CapabilityContract(
                "crypto_etf_flow",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="sentiment",
            ),
            CapabilityContract(
                "crypto_usdt_premium",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=True,
                expected_market="crypto",
                expected_variety="sentiment",
            ),
        ],
        known_issues=[
            "免费源稳定性（alternative.me 限频/CMC 月度配额）——日频采集+失败降级标注",
            "crypto_etf_flow / crypto_usdt_premium 为骨架能力（数据源待接入）",
        ],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：验证可选 CMC API key 可用性（alternative.me 无需 key）。"""
        cmc_key = get_secret_or_default("CMC_API_KEY", "")
        if cmc_key:
            self._log.info("CMC_API_KEY 已配置（BTC 占比可用）")
        else:
            self._log.info("CMC_API_KEY 未配置（BTC 占比不可用，其余指标不受影响）")
        self._connected = True
        self._log.info("币圈宏观情绪面板已连接（免费公开端点）")

    def health_check(self) -> bool:
        """探活：请求 alternative.me 最新 1 条恐惧贪婪指数。"""
        try:
            resp = self._http_get(_FNG_URL, timeout=10, params={"limit": "1", "format": "json"})
            data = resp.json()
            return len(data.get("data", [])) > 0
        except Exception as e:  # noqa: BLE001 — 探活失败不阻断
            self._log.warning("宏观情绪面板探活失败: %s", e)
            return False

    def disconnect(self) -> None:
        """断开连接：无状态 REST，直接标记断开。"""
        self._connected = False
        self._log.info("币圈宏观情绪面板已断开")

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
                error="crypto_sentiment_panel 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability")
        if capability == "crypto_fear_greed_index":
            yield from self._fetch_fear_greed(payload, policy)
        elif capability == "crypto_btc_dominance":
            yield from self._fetch_btc_dominance(payload, policy)
        elif capability in _SKELETON_NOTES:
            yield from self._fetch_skeleton(payload, capability)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 恐惧贪婪指数（alternative.me） ----

    def _fetch_fear_greed(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """拉取恐惧贪婪指数历史（alternative.me，limit 条数=天数，时间倒序）。"""
        t0 = time.time()
        end = payload.end or datetime.date.today()
        start = payload.start or end - datetime.timedelta(days=30)
        limit = max((end - start).days + 1, 1)

        try:
            resp = self._call_with_policy(
                self._http_get,
                policy,
                _FNG_URL,
                timeout=30,
                params={"limit": str(limit), "format": "json"},
            )
            data = resp.json()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=payload.table,
                columns=_SENTIMENT_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.time() - t0,
                error=f"alternative.me API 请求失败: {e}",
            )
            return

        rows: list[tuple] = []
        for entry in data.get("data", []):
            ts = int(entry["timestamp"])
            d = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date()
            if not (start <= d <= end):
                continue
            rows.append(
                (
                    "fear_greed_index",
                    d.isoformat(),
                    float(entry["value"]),
                    entry.get("value_classification", ""),
                    "alternative.me",
                    "",
                )
            )

        last_key = max(r[1] for r in rows) if rows else ""
        yield FetchResult(
            table=payload.table,
            columns=_SENTIMENT_COLUMNS,
            rows=rows,
            last_key=last_key,
            elapsed_sec=time.time() - t0,
        )

    # ---- BTC 占比（CoinMarketCap） ----

    def _fetch_btc_dominance(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """拉取 BTC 占比最新快照（CMC global-metrics，免费 basic tier 需 key）。"""
        t0 = time.time()
        api_key = get_secret_or_default("CMC_API_KEY", "")
        if not api_key:
            yield FetchResult(
                table=payload.table,
                columns=_SENTIMENT_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.time() - t0,
                error="CMC_API_KEY 未配置（BTC 占比需 CoinMarketCap 免费 API key）",
            )
            return

        try:
            resp = self._call_with_policy(
                self._http_get,
                policy,
                _CMC_GLOBAL_URL,
                timeout=30,
                headers={"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"},
            )
            data = resp.json()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            yield FetchResult(
                table=payload.table,
                columns=_SENTIMENT_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.time() - t0,
                error=f"CMC API 请求失败: {e}",
            )
            return

        status = data.get("status", {})
        if status.get("error_code"):
            yield FetchResult(
                table=payload.table,
                columns=_SENTIMENT_COLUMNS,
                rows=[],
                last_key="",
                elapsed_sec=time.time() - t0,
                error=f"CMC API 错误: {status.get('error_message', 'unknown')}",
            )
            return

        global_data = data.get("data", {})
        today = datetime.date.today().isoformat()
        rows = [
            (
                "btc_dominance",
                today,
                float(global_data["btc_dominance"]),
                "",
                "coinmarketcap",
                "",
            )
        ]
        yield FetchResult(
            table=payload.table,
            columns=_SENTIMENT_COLUMNS,
            rows=rows,
            last_key=today,
            elapsed_sec=time.time() - t0,
        )

    # ---- 骨架能力（ETF 流量 / USDT 场外溢价） ----

    def _fetch_skeleton(self, payload: FetchPayload, capability: str) -> Iterator[FetchResult]:
        """骨架能力：接口与行格式就位，数据源待接入（晋升时落地）。"""
        yield FetchResult(
            table=payload.table,
            columns=_SENTIMENT_COLUMNS,
            rows=[],
            last_key="",
            elapsed_sec=0.0,
            error=_SKELETON_NOTES[capability],
        )
