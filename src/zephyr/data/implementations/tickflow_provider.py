# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tickflow_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] tickflow SDK (tf.klines.get)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 免费无key；60次/分钟限流；美股日/周/月K线；用ETF替代真实美股指数
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestTickFlowProvider
# [A_module] module_id=MOD-L00-004-tickflow_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TickFlow 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 tickflow SDK，继承 DataSourceBase。
- 免费无 key
- 60 次/分钟限流（必须 _call_with_policy 包裹以触发 RPM 限流）
- 美股日/周/月/季/年 K 线
- 用 SPY.US/DIA.US/QQQ.US ETF 替代真实美股指数
- 当前能力：us_daily_kline（美股日K线）/ us_index（美股指数，ETF替代）

关键设计：
- connect() 仅验证 SDK 可导入
- fetch() 调用 tf.klines.get，标的格式 "AAPL.US"
"""
from __future__ import annotations

import datetime
import logging
import time
from typing import Iterator

from ..provider_base import (
    DataSourceBase,
    DataSourceMeta,
    FetchPayload,
    FetchResult,
)
from ..policy_registry import SourcePolicy

log = logging.getLogger(__name__)


# 默认美股标的清单（ETF 替代指数 + 科技龙头）
_DEFAULT_US_SYMBOLS = [
    "SPY.US",   # S&P 500 ETF（替代标普500指数）
    "DIA.US",   # 道琼斯 ETF（替代道琼斯指数）
    "QQQ.US",   # 纳斯达克 ETF（替代纳斯达克指数）
    "AAPL.US",  # 苹果
    "MSFT.US",  # 微软
    "TSLA.US",  # 特斯拉
    "NVDA.US",  # 英伟达
    "GOOG.US",  # 谷歌
    "AMZN.US",  # 亚马逊
    "META.US",  # Meta
    "NFLX.US",  # 奈飞
]

# 美股指数 ETF 映射（us_index capability 用）
_US_INDEX_ETF = {
    "SPX": "SPY.US",    # 标普500 -> SPY ETF
    "DJI": "DIA.US",    # 道琼斯 -> DIA ETF
    "IXIC": "QQQ.US",   # 纳斯达克 -> QQQ ETF
}


class TickFlowProvider(DataSourceBase):
    """TickFlow 免费美股数据源 Provider。

    匿名访问、shared 线程安全模型。
    已知问题：60 次/分钟限流。
    """

    source_name: str = "tickflow"
    meta: DataSourceMeta = DataSourceMeta(
        name="tickflow",
        display_name="TickFlow 美股",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=60,
        capabilities=["us_daily_kline", "us_index"],
        known_issues=["60次/分钟限流", "ETF替代真实指数"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：验证 tickflow 可导入。"""
        import tickflow  # noqa: F401
        self._connected = True
        self._log.info("TickFlow 已连接（匿名访问）")

    def health_check(self) -> bool:
        """探活：尝试 import tickflow。"""
        try:
            import tickflow  # noqa: F401
            return True
        except ImportError as e:
            self._log.warning(f"TickFlow 探活失败（tickflow 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：重置状态。"""
        self._connected = False
        self._log.info("TickFlow 已断开")

    # ---- 拉取入口 ----

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        cap = (payload.extra or {}).get("capability")
        if cap == "us_daily_kline":
            yield from self._fetch_us_daily_kline(payload, policy)
        elif cap == "us_index":
            yield from self._fetch_us_index(payload, policy)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {cap}",
            )

    # ---- 美股日K线 ----

    def _fetch_us_daily_kline(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取美股日K线（tf.klines.get）。

        每个标的作为一批 yield FetchResult。
        """
        import tickflow as tf

        table = payload.table or "c1_market.us_daily_kline"
        columns = ["trade_date", "code", "open", "high", "low", "close", "volume"]
        symbols = payload.symbols or _DEFAULT_US_SYMBOLS
        start = (payload.start or datetime.date.today() - datetime.timedelta(days=365))
        end = payload.end or datetime.date.today()
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")

        for symbol in symbols:
            t0 = time.time()
            try:
                df = self._call_with_policy(
                    tf.klines.get,
                    policy,
                    symbol=symbol,
                    freq="D",
                    start_date=start_str,
                    end_date=end_str,
                )
                rows: list[tuple] = []
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        rows.append((
                            str(row.get("date", "")),
                            symbol,
                            float(row.get("open", 0) or 0),
                            float(row.get("high", 0) or 0),
                            float(row.get("low", 0) or 0),
                            float(row.get("close", 0) or 0),
                            int(row.get("volume", 0) or 0),
                        ))
                self._log.info(f"美股K线 {symbol}: {len(rows)} 行")
                if rows:
                    yield FetchResult(
                        table=table, columns=columns, rows=rows,
                        last_key=end.isoformat(), elapsed_sec=time.time() - t0,
                    )
            except Exception as e:
                self._log.warning(f"美股K线 {symbol} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.time() - t0, error=str(e),
                )

    # ---- 美股指数（ETF替代）----

    def _fetch_us_index(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取美股指数（用 ETF 替代真实指数）。

        SPX->SPY, DJI->DIA, IXIC->QQQ。
        """
        import tickflow as tf

        table = payload.table or "c1_market.us_index"
        columns = ["trade_date", "index_code", "etf_code", "open", "high", "low", "close", "volume"]
        start = (payload.start or datetime.date.today() - datetime.timedelta(days=365))
        end = payload.end or datetime.date.today()
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")

        for index_code, etf_symbol in _US_INDEX_ETF.items():
            t0 = time.time()
            try:
                df = self._call_with_policy(
                    tf.klines.get,
                    policy,
                    symbol=etf_symbol,
                    freq="D",
                    start_date=start_str,
                    end_date=end_str,
                )
                rows: list[tuple] = []
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        rows.append((
                            str(row.get("date", "")),
                            index_code,
                            etf_symbol,
                            float(row.get("open", 0) or 0),
                            float(row.get("high", 0) or 0),
                            float(row.get("low", 0) or 0),
                            float(row.get("close", 0) or 0),
                            int(row.get("volume", 0) or 0),
                        ))
                self._log.info(f"美股指数 {index_code}->{etf_symbol}: {len(rows)} 行")
                if rows:
                    yield FetchResult(
                        table=table, columns=columns, rows=rows,
                        last_key=end.isoformat(), elapsed_sec=time.time() - t0,
                    )
            except Exception as e:
                self._log.warning(f"美股指数 {index_code} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.time() - t0, error=str(e),
                )
