# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.baostock_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] baostock SDK (bs.login/bs.logout/bs.query_history_k_data_plus/bs.query_hs300_stocks/bs.query_trade_date)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] thread_local 登录模型——每线程独立 bs.login()；数据滞后约1周；匿名访问无需token
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)；未登录->RuntimeError
# [TESTS] tests/zephyr/data/test_providers.py::TestBaostockProvider
# [A_module] module_id=MOD-GOV-baostock_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Baostock 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 baostock SDK，继承 IngestProviderBase。
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
    IngestProviderBase,
    IngestProviderMeta,
    FetchPayload,
    FetchResult,
    CapabilityContract,
)
from ..policy_registry import SourcePolicy
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_INDEX_CONSTITUENT = get_registry().table("market_index_constituent")
_TBL_TRADE_CALENDAR = get_registry().table("market_trade_calendar")
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")


def _bs_code_to_symbol(bs_code: str) -> str:
    """baostock 代码（sh.600000/sz.000001）→ 项目 canonical（600000.SH/000001.SZ）。

    #ARCH-DATA-015：index_constituent 表 symbol_canonical MATERIALIZED 列依赖
    '代码.交易所大写' 格式推导，小写前缀格式会导致派生列为空串。
    """
    code = (bs_code or "").strip()
    if "." in code:
        exch, num = code.split(".", 1)
        return f"{num}.{exch.upper()}"
    return code


class BaostockProvider(IngestProviderBase):
    """Baostock 免费数据源 Provider。

    匿名访问、thread_local 登录模型。每线程独立 bs.login() 会话。
    已知问题：数据滞后约 1 周。
    """

    source_name: str = "baostock"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="baostock",
        display_name="BaoStock 免费",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="thread_local",
        rate_limit_default=60,
        capabilities=[
            # 治本修复#ARCH-CAP-NULL-SYMBOLS-001（2026-07-23）：
            # baostock 的 index_constituent/trade_calendar 均为全量查询接口
            # （bs.query_hs300_stocks / bs.query_trade_dates 不接受 symbols 参数），
            # 显式声明 supports_symbols_null=True 消除 WARN。
            CapabilityContract("index_constituent", supports_symbols_null=True),
            CapabilityContract("trade_calendar", supports_symbols_null=True),
            CapabilityContract("kline_daily", supports_symbols_null=False),
        ],
        known_issues=["数据滞后约1周", "需thread_local登录"],
    )

    def __init__(self):
        super().__init__()
        # 线程局部存储：每线程独立的登录态
        self._tls = threading.local()

    # ---- 公共属性（R5: 消除测试私有访问） ----

    @property
    def tls(self) -> threading.local:
        """线程局部存储（只读暴露，供测试验证 per-thread 登录态）。"""
        return self._tls

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
                # #ARCH-DATA-015: 登录失败（如 10001011 IP黑名单）时 baostock 库不释放
                # 底层 socket，filterwarnings=error 下泄漏的 ResourceWarning 会被放大为
                # 测试 ExceptionGroup；失败路径显式 logout 关闭 socket。
                try:
                    bs.logout()
                except Exception:  # noqa: BLE001 — 清理动作不掩盖原始错误
                    pass
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            self._log.warning(f"Baostock 探活失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：登出当前线程的 baostock 会话。"""
        if getattr(self._tls, "logged_in", False):
            try:
                self._tls.bs.logout()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        #ARCH-DATA-015：列名对齐 index_constituent 表 schema（08-10 SCD-2 重建后
        旧列名 update_date/code/code_name 与表零交集，write_result 过滤后只剩
        weight 一列静默空写——300 行丢失的病根）。weight 无数据源置 0（同 miniqmt 口径）。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_INDEX_CONSTITUENT
        columns = ["trade_date", "index_code", "symbol", "weight", "action", "data_source"]
        t0 = time.time()
        try:
            rs = self._call_with_policy(bs.query_hs300_stocks, policy)
            rows: list[tuple] = []
            while rs.error_code == "0" and rs.next():
                item = rs.get_row_data()
                # API 变更后返回 3 列: updateDate, code(sh.600000), code_name
                rows.append((item[0], "000300.SH", _bs_code_to_symbol(item[1]), 0, "", "baostock"))
            self._log.info(f"沪深300成分股获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=datetime.date.today().isoformat(),
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        #ARCH-DATA-015：列名对齐 trade_calendar 表 schema（exchange/cal_date/is_open/
        pretrade_date；旧列名 calendar_date/is_trading_day 与表零交集静默空写）。
        pretrade_date=上一开市日（首个开市日取自身）。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_TRADE_CALENDAR
        columns = ["exchange", "cal_date", "is_open", "pretrade_date"]
        t0 = time.time()
        try:
            start = payload.start.isoformat() if payload.start else "2010-01-01"
            end = payload.end.isoformat() if payload.end else datetime.date.today().isoformat()
            rs = self._call_with_policy(
                bs.query_trade_dates, policy, start_date=start, end_date=end
            )
            rows: list[tuple] = []
            last_open: str | None = None
            while rs.error_code == "0" and rs.next():
                item = rs.get_row_data()
                # API 变更后返回 2 列: calendar_date(item[0]), is_trading_day(item[1])
                cal_date, is_open = item[0], int(item[1]) if item[1] else 0
                rows.append(("SSE", cal_date, is_open, last_open or cal_date))
                if is_open:
                    last_open = cal_date
            self._log.info(f"交易日历获取完成，{len(rows)} 行")
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=end, elapsed_sec=time.time() - t0,
            )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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

        作为日K线降级源使用。数据滞后约1周。
        """
        bs = self._tls.bs
        table = payload.table or _TBL_KLINE_DAILY
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
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._log.warning(f"baostock K线 {code} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.time() - t0, error=str(e),
                )
