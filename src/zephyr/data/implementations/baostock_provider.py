# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.baostock_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] baostock SDK (bs.login/bs.logout/bs.query_history_k_data_plus/bs.query_hs300_stocks/bs.query_trade_date)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] thread_local 登录模型——每线程独立 bs.login()；数据滞后约1周；匿名访问无需token
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；未登录->RuntimeError
# [TESTS] tests/zephyr/data/test_providers.py::TestBaostockProvider
# [A_module] module_id=MOD-L00-004-baostock_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Baostock 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 baostock SDK，继承 DataSourceBase。
- 匿名访问（bs.login() 无需 token）
- **thread_local 登录模型**：每线程独立 bs.login()，结束时 bs.logout()
- 数据滞后约 1 周（last_key < today-7 时标记 stale）
- 当前能力：index_constituent（沪深300成分股）/ trade_calendar（交易日历）

关键设计：
- 用 threading.local() 存储每线程的登录态
- connect() 为当前线程登录；fetch() 前确认当前线程已登录
- disconnect() 登出当前线程
"""
from __future__ import annotations

import datetime
import logging
import threading
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


class BaostockProvider(DataSourceBase):
    """Baostock 免费数据源 Provider。

    匿名访问、thread_local 登录模型。每线程独立 bs.login() 会话。
    已知问题：数据滞后约 1 周。
    """

    source_name: str = "baostock"
    meta: DataSourceMeta = DataSourceMeta(
        name="baostock",
        display_name="BaoStock 免费",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="thread_local",
        rate_limit_default=60,
        capabilities=["index_constituent", "trade_calendar", "kline_daily"],
        known_issues=["数据滞后约1周", "需thread_local登录"],
    )

    def __init__(self):
        super().__init__()
        # 线程局部存储：每线程独立的登录态
        self._tls = threading.local()

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：为当前线程登录 baostock。"""
        self._ensure_login()
        self._connected = True
        self._log.info("Baostock 已连接（thread_local 登录）")

    def _ensure_login(self) -> None:
        """确保当前线程已登录 baostock（若未登录则登录）。"""
        if not getattr(self._tls, "logged_in", False):
            import baostock as bs
            result = bs.login()
            if result.error_code != "0":
                raise RuntimeError(
                    f"baostock login failed: {result.error_code} {result.error_msg}"
                )
            self._tls.logged_in = True
            self._tls.bs = bs
            self._log.debug("baostock 线程 %s 已登录", threading.current_thread().name)

    def health_check(self) -> bool:
        """探活：尝试 import baostock + 登录。"""
        try:
            import baostock  # noqa: F401
            self._ensure_login()
            return True
        except ImportError as e:
            self._log.warning(f"Baostock 探活失败（baostock 未安装）: {e}")
            return False
        except Exception as e:
            self._log.warning(f"Baostock 探活失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：登出当前线程的 baostock 会话。"""
        if getattr(self._tls, "logged_in", False):
            try:
                self._tls.bs.logout()
            except Exception as e:
                self._log.warning(f"baostock logout 异常: {e}")
            self._tls.logged_in = False
            self._tls.bs = None
        self._connected = False
        self._log.info("Baostock 已断开")

    # ---- 拉取入口 ----

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        # 确保当前线程已登录
        try:
            self._ensure_login()
        except Exception as e:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0, error=f"baostock login failed: {e}",
            )
            return

        cap = (payload.extra or {}).get("capability")
        if cap == "index_constituent":
            yield from self._fetch_index_constituent(payload, policy)
        elif cap == "trade_calendar":
            yield from self._fetch_trade_calendar(payload, policy)
        elif cap == "kline_daily":
            yield from self._fetch_kline_daily(payload, policy)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {cap}",
            )

    # ---- 沪深300成分股 ----

    def _fetch_index_constituent(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取沪深300成分股（bs.query_hs300_stocks）。

        baostock API 变更：返回 3 列（updateDate/code/code_name），无 weight 列。
        """
        bs = self._tls.bs
        table = payload.table or "c1_market.index_constituent"
        columns = ["update_date", "code", "code_name", "weight"]
        t0 = time.time()
        try:
            rs = self._call_with_policy(bs.query_hs300_stocks, policy)
            rows: list[tuple] = []
            while rs.error_code == "0" and rs.next():
                item = rs.get_row_data()
                # API 变更后返回 3 列: updateDate, code, code_name（无 weight）
                rows.append((item[0], item[1], item[2], None))
            self._log.info(f"沪深300成分股获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=datetime.date.today().isoformat(),
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            self._log.warning(f"沪深300成分股获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.time() - t0, error=str(e),
            )

    # ---- 交易日历 ----

    def _fetch_trade_calendar(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取交易日历（bs.query_trade_dates）。

        baostock API 变更：方法名 query_trade_date → query_trade_dates（加 s）。
        返回 2 列: calendar_date, is_trading_day。
        """
        bs = self._tls.bs
        table = payload.table or "c1_market.trade_calendar"
        columns = ["calendar_date", "is_trading_day"]
        t0 = time.time()
        try:
            start = payload.start.isoformat() if payload.start else "2010-01-01"
            end = payload.end.isoformat() if payload.end else datetime.date.today().isoformat()
            rs = self._call_with_policy(
                bs.query_trade_dates, policy, start_date=start, end_date=end
            )
            rows: list[tuple] = []
            while rs.error_code == "0" and rs.next():
                item = rs.get_row_data()
                # API 变更后返回 2 列: calendar_date(item[0]), is_trading_day(item[1])
                rows.append((item[0], int(item[1]) if item[1] else 0))
            self._log.info(f"交易日历获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=end, elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            self._log.warning(f"交易日历获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[],
                last_key="", elapsed_sec=time.time() - t0, error=str(e),
            )

    # ---- 日K线（备选降级源）----

    def _fetch_kline_daily(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取日K线（bs.query_history_k_data_plus）。

        作为 iFind 降级源使用。数据滞后约1周。
        """
        bs = self._tls.bs
        table = payload.table or "c1_market.kline_daily"
        columns = ["date", "code", "open", "high", "low", "close", "volume", "amount"]
        t0 = time.time()
        symbols = payload.symbols or ["sh.600000"]
        start = payload.start.isoformat() if payload.start else "2020-01-01"
        end = payload.end.isoformat() if payload.end else datetime.date.today().isoformat()

        for code in symbols:
            try:
                rs = self._call_with_policy(
                    bs.query_history_k_data_plus,
                    policy,
                    code=code,
                    fields="date,code,open,high,low,close,volume,amount",
                    start_date=start,
                    end_date=end,
                    frequency="d",
                    adjustflag="2",  # 前复权
                )
                rows: list[tuple] = []
                while rs.error_code == "0" and rs.next():
                    item = rs.get_row_data()
                    rows.append(tuple(item))
                if rows:
                    yield FetchResult(
                        table=table, columns=columns, rows=rows,
                        last_key=end, elapsed_sec=time.time() - t0,
                    )
            except Exception as e:
                self._log.warning(f"baostock K线 {code} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.time() - t0, error=str(e),
                )
