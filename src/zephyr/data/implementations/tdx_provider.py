# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.tdx_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] mootdx SDK (Quotes.factory/index_bars/get_stock_list_in_sector)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] bestip自动选最快服务器；单线程串行；板块K线+成分股；无板块分笔Tick
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestTDXProvider
# [A_module] module_id=MOD-L00-004-tdx_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""通达信数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 mootdx SDK，继承 DataSourceBase。
- bestip 自动选最快服务器
- 单线程串行
- 板块指数 K 线 + 成分股列表
- **无板块分笔 Tick**（仅 K 线和成分股）
- 当前能力：industry_class（板块分类）

关键设计：
- connect() 用 Quotes.factory(market='std') 创建客户端，bestip 自动选择
- fetch() 调用 client.index_bars / client.get_stock_list_in_sector
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


class TDXProvider(DataSourceBase):
    """通达信数据源 Provider。

    bestip 自动选服务器、single_thread 线程安全模型。
    已知问题：单线程；无板块分笔 Tick。
    """

    source_name: str = "tdx"
    meta: DataSourceMeta = DataSourceMeta(
        name="tdx",
        display_name="通达信",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="single_thread",
        rate_limit_default=0,
        capabilities=["industry_class", "sector_kline"],
        known_issues=["单线程串行", "无板块分笔Tick", "需bestip选最快服务器"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：用 mootdx Quotes.factory 创建客户端。"""
        from mootdx.quotes import Quotes
        # bestip 自动选最快服务器
        self._client = Quotes.factory(market="std")
        self._connected = True
        self._log.info("通达信已连接（bestip 自动选择）")

    def health_check(self) -> bool:
        """探活：验证 client 可用。"""
        try:
            from mootdx.quotes import Quotes  # noqa: F401
            return self._connected and self._client is not None
        except ImportError as e:
            self._log.warning(f"通达信探活失败（mootdx 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：关闭 client。"""
        if self._client is not None:
            try:
                close = getattr(self._client, "close", None)
                if close:
                    close()
            except Exception as e:
                self._log.warning(f"通达信关闭异常: {e}")
        self._client = None
        self._connected = False
        self._log.info("通达信已断开")

    # ---- 拉取入口 ----

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        if not self._connected or self._client is None:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0, error="tdx 未连接",
            )
            return

        cap = (payload.extra or {}).get("capability")
        if cap == "industry_class":
            yield from self._fetch_industry_class(payload, policy)
        elif cap == "sector_kline":
            yield from self._fetch_sector_kline(payload, policy)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {cap}",
            )

    # ---- 板块分类 ----

    def _fetch_industry_class(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取板块分类列表（client.block）。

        mootdx block() 返回 DataFrame: [blockname, block_type, code_index, code]。
        """
        table = payload.table or "c3_fundamental.industry_class"
        columns = ["sector_code", "sector_name", "stock_code", "stock_name"]
        t0 = time.time()
        try:
            df = self._call_with_policy(self._client.block, policy)
            rows: list[tuple] = []
            if df is not None and not df.empty:
                # 列提取替代 iterrows（38万行性能）
                blocknames = df["blockname"].astype(str).tolist()
                codes = df["code"].astype(str).tolist()
                rows = list(zip([""] * len(df), blocknames, codes, [""] * len(df)))

            self._log.info(f"板块分类获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=datetime.date.today().isoformat(),
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            self._log.warning(f"板块分类获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.time() - t0, error=str(e),
            )

    # ---- 板块指数K线 ----

    def _fetch_sector_kline(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取板块指数K线（client.index_bars）。

        mootdx index_bars(symbol, frequency=9, start, offset) 返回 DataFrame。
        frequency: 9=日线。
        """
        table = payload.table or "c1_market.sector_kline"
        columns = ["trade_date", "code", "open", "high", "low", "close", "volume", "amount"]
        symbols = payload.symbols or []
        count = int(payload.extra.get("count", 100)) if payload.extra else 100

        for code in symbols:
            t0 = time.time()
            try:
                # 提取纯代码：sh.000001 -> 000001
                raw_code = code.split(".")[-1] if "." in code else code

                bars = self._call_with_policy(
                    self._client.index_bars,
                    policy,
                    symbol=raw_code,
                    frequency=9,     # 日线
                    start=0,
                    offset=count,
                )
                rows: list[tuple] = []
                if bars is not None and not bars.empty:
                    for _, bar in bars.iterrows():
                        rows.append((
                            str(bar.get("datetime", "")),
                            code,
                            float(bar.get("open", 0) or 0),
                            float(bar.get("high", 0) or 0),
                            float(bar.get("low", 0) or 0),
                            float(bar.get("close", 0) or 0),
                            int(bar.get("vol", 0) or 0),
                            float(bar.get("amount", 0) or 0),
                        ))
                self._log.info(f"板块K线 {code}: {len(rows)} 行")
                if rows:
                    yield FetchResult(
                        table=table, columns=columns, rows=rows,
                        last_key=datetime.date.today().isoformat(),
                        elapsed_sec=time.time() - t0,
                    )
            except Exception as e:
                self._log.warning(f"板块K线 {code} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.time() - t0, error=str(e),
                )
