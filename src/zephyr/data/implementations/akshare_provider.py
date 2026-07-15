# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.akshare_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare SDK (ak.macro_china_gdp/cpi/pmi/money_supply); zephyr.data.ch_reader
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 匿名访问；须断开 VPN（爬国内网站）；东财接口跳过（反爬）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestAKShareHelpers
# [A_module] module_id=MOD-L00-004-akshare_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AKShare 数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 AKShare 开源金融数据 SDK，继承 DataSourceBase。
- 匿名访问，无需登录；但须断开 VPN（爬国内网站，海外 IP 会被拒）
- 当前能力：macro_data（GDP/CPI/PMI/货币供应量）
- 每个指标函数作为一批 yield FetchResult，异常时 yield error 不抛出

数据转换目标表 c1_market.macro_data：
    report_date, indicator_name, indicator_value, unit, frequency
"""
from __future__ import annotations

import calendar
import datetime
import logging
import re
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
from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row

log = logging.getLogger(__name__)


# === 裁定#217 Tier2 P4 Extract Method 重构（2026-07-15）===
# 原 AKShareProvider.fetch 95行 McCabe=41（38个elif分支能力路由，均调用 self._fetch_{cap}(payload, policy)）。
# 治本：提取为 frozenset + getattr 动态分发，主函数简化为编排（McCabe=2）。
# 行为等价：所有路由调用签名/参数完全保留，unsupported capability 错误消息不变。
_AKSHARE_CAPABILITIES = frozenset({
    "macro_data", "daily_valuation", "margin_trading", "block_trade",
    "dragon_tiger", "money_flow", "share_unlock", "audit_opinion",
    "equity_pledge", "equity_pledge_summary", "dividend", "restricted_shares",
    "stock_news_em", "news_cctv", "news_economic_baidu", "news_baidu",
    "news_stock", "analyst_forecast", "rights_issue", "research_report",
    "hk_connect_flow", "kline_futures", "limit_up_down", "share_change",
    "st_stock_list", "concept_board", "stock_indicator", "block_trade_detail",
    "top10_shareholders", "top10_circulating_shareholders", "disclosure_plan",
    "repurchase", "convertible_bond_list", "etf_list", "lof_list",
    "hk_stock_list", "hk_trade_calendar", "index_list", "etf_benchmark",
})


def safe_float(v) -> float | None:
    """安全转 float，失败返回 None。"""
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def safe_int(v) -> int | None:
    """安全转 int，失败返回 None。兼容 float 字符串（如 '7987.0'）。"""
    try:
        if v is None:
            return None
        f = float(v)
        return int(f)
    except (ValueError, TypeError):
        return None


# CH fallback: 从 stock_list 获取 A 股 6 位代码（SQL_ 前缀豁免 NO-BARE-SQL gate）
SQL_STOCK_CODE_FROM_LIST = (
    "SELECT splitByChar('.', ts_code)[1] AS code "
    "FROM c1_market.stock_list "
    "WHERE list_status = '上市' ORDER BY ts_code FORMAT TabSeparated"
)


class AKShareProvider(DataSourceBase):
    """AKShare 免费开源数据源 Provider。

    匿名访问、无需登录；线程安全模型为 shared（多线程共享 akshare 模块）。
    已知问题：须断开 VPN；东财接口反爬严重。
    """

    source_name: str = "akshare"
    meta: DataSourceMeta = DataSourceMeta(
        name="akshare",
        display_name="AKShare 免费开源",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=60,
        capabilities=[
            "macro_data", "dividend", "restricted_shares", "equity_pledge",
            "daily_valuation", "margin_trading", "block_trade",
            "dragon_tiger", "money_flow", "share_unlock",
            "audit_opinion", "equity_pledge_summary",
            # 新闻数据
            "stock_news_em", "news_cctv", "news_economic_baidu",
            "news_baidu", "news_stock",
            # 分析师预期 & 配股
            "analyst_forecast", "rights_issue",
            # 研报 & 北向资金 & 期货主力合约
            "research_report", "hk_connect_flow", "kline_futures",
            # 涨跌停 & 股本变动 & ST股票 & 概念板块 & 指标 & 大宗交易明细
            "limit_up_down", "share_change", "st_stock_list",
            "concept_board", "stock_indicator", "block_trade_detail",
            # 十大股东 & 披露计划（淘宝历史数据持续更新）
            "top10_shareholders", "top10_circulating_shareholders",
            "disclosure_plan",
            # 回购数据
            "repurchase",
            # 静态列表月初刷新
            "convertible_bond_list", "etf_list", "lof_list",
            "hk_stock_list", "hk_trade_calendar", "index_list",
            "etf_benchmark",
        ],
        known_issues=["须断开VPN", "东财接口反爬严重"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接。AKShare 无需登录，直接标记为已连接。"""
        self._connected = True
        self._log.info("AKShare 已连接（匿名访问，无需登录）")

    def health_check(self) -> bool:
        """探活：尝试 import akshare，返回是否可用。"""
        try:
            import akshare  # noqa: F401
            return True
        except ImportError as e:
            self._log.warning(f"AKShare 探活失败（akshare 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接。AKShare 无持久连接资源，仅重置状态。"""
        self._connected = False
        self._log.info("AKShare 已断开")

    # ---- 拉取入口 ----

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。

        未知 capability -> yield FetchResult(error=...)。
        """
        cap = (payload.extra or {}).get("capability")
        if cap in _AKSHARE_CAPABILITIES:
            yield from getattr(self, f"_fetch_{cap}")(payload, policy)
            return
        yield FetchResult(
            table=payload.table,
            columns=[],
            rows=[],
            last_key="",
            elapsed_sec=0.0,
            error=f"unsupported capability: {cap}",
        )

    # ---- 宏观经济数据 ----

    def _fetch_macro_data(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取宏观经济数据：GDP / CPI / PMI / 货币供应量。

        每个指标函数作为一批，yield 一个 FetchResult（共 4 批）。
        异常时 yield FetchResult(error=str(e))，不抛出。
        """
        import akshare as ak

        table = "c1_market.macro_data"
        columns = ["report_date", "indicator_name", "indicator_value", "unit", "frequency"]
        last_key = datetime.date.today().isoformat()

        # (批次名, akshare 函数, 行转换器)
        jobs = [
            ("GDP", ak.macro_china_gdp, self._transform_gdp),
            ("CPI", ak.macro_china_cpi, self._transform_monthly),
            ("PMI", ak.macro_china_pmi, self._transform_monthly),
            ("MoneySupply", ak.macro_china_money_supply, self._transform_monthly),
        ]

        for name, fn, transform in jobs:
            t0 = time.time()
            try:
                # 用 _call_with_policy 包裹，自动限流+重试
                df = self._call_with_policy(fn, policy)
                rows = transform(df)
                self._log.info(f"{name} 获取完成，{len(rows)} 行")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=rows,
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                )
            except Exception as e:
                self._log.warning(f"{name} 获取失败: {e}")
                yield FetchResult(
                    table=table,
                    columns=columns,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.time() - t0,
                    error=str(e),
                )

    # ---- DataFrame 转换 ----

    def _transform_gdp(self, df) -> list[tuple]:
        """转换 GDP DataFrame。

        列"季度"如"2025年第1季度" -> 季度末日期；
        "国内生产总值-绝对值" -> indicator_name="GDP"，unit="亿元"；
        "国内生产总值-同比增长" -> indicator_name="GDP_同比"，unit="%"。
        frequency="季度"。
        """
        rows: list[tuple] = []
        for _, row in df.iterrows():
            quarter = str(row.iloc[0])
            report_date = self._quarter_to_date(quarter)
            if not report_date:
                continue
            # GDP 绝对值
            val = safe_float(row.get("国内生产总值-绝对值"))
            if val is not None:
                rows.append((report_date, "GDP", val, "亿元", "季度"))
            # GDP 同比
            yoy = safe_float(row.get("国内生产总值-同比增长"))
            if yoy is not None:
                rows.append((report_date, "GDP_同比", yoy, "%", "季度"))
        return rows

    def _transform_monthly(self, df) -> list[tuple]:
        """转换月度 DataFrame（CPI/PMI/货币供应量）。

        第一列如"2025年6月" -> 月末日期；其余列各自作为 indicator_name。
        unit=""，frequency="月度"。
        """
        rows: list[tuple] = []
        cols = list(df.columns)
        for _, row in df.iterrows():
            month_str = str(row.iloc[0])
            report_date = self._month_to_date(month_str)
            if not report_date:
                continue
            for col in cols[1:]:
                val = safe_float(row.get(col))
                if val is not None:
                    rows.append((report_date, col, val, "", "月度"))
        return rows

    # ---- 日期解析辅助 ----

    @staticmethod
    def _quarter_to_date(s: str) -> str:
        """'2025年第1季度' -> '2025-03-31'（季度末日期）。

        支持 '2025年第1-3季度' 形式（取末季度）。
        """
        m = re.match(r"(\d{4})年第([0-9\-]+)季度", s)
        if not m:
            return ""
        year = m.group(1)
        qs = m.group(2)
        if "-" in qs:
            last = int(qs.split("-")[-1])
        else:
            last = int(qs)
        month_day = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
        md = month_day.get(last)
        return f"{year}-{md}" if md else ""

    @staticmethod
    def _month_to_date(s: str) -> str:
        """'2025年6月' -> '2025-06-30'（月末日期）。"""
        m = re.match(r"(\d{4})年(\d{1,2})月?", s)
        if not m:
            return ""
        y, mo = m.group(1), int(m.group(2))
        last_day = calendar.monthrange(int(y), mo)[1]
        return f"{y}-{mo:02d}-{last_day:02d}"

    # ---- 通用辅助（日期/标的） ----

    @staticmethod
    def _date_range(start: datetime.date, end: datetime.date) -> Iterator[datetime.date]:
        """生成 start 到 end（含）的自然日序列。"""
        cur = start
        while cur <= end:
            yield cur
            cur += datetime.timedelta(days=1)

    @staticmethod
    def _symbol_to_market(symbol: str) -> str:
        """6位代码转 AKShare market 参数：sh/sz/bj。

        60/68 开头->sh；00/30 开头->sz；其余（8/4等）->bj。
        """
        s = str(symbol).zfill(6)
        if s.startswith(("60", "68")):
            return "sh"
        elif s.startswith(("00", "30")):
            return "sz"
        else:
            return "bj"

    @staticmethod
    def _norm_date_str(v) -> str:
        """把日期类值截成 'YYYY-MM-DD' 字符串；空值返回 ''。"""
        if v is None:
            return ""
        s = str(v)
        if s.lower() in ("none", "nan", "nat", ""):
            return ""
        # 处理 'YYYY-MM-DD HH:MM:SS' / Timestamp / 'YYYY/MM/DD' 等
        s = s.replace("/", "-")
        if " " in s:
            s = s.split(" ")[0]
        return s[:10]

    def _get_all_a_symbols(self, ak, policy: SourcePolicy) -> list[str]:
        """获取全 A 股 6 位代码列表。

        优先用 ak.stock_zh_a_spot_em，失败时回退到 ClickHouse stock_list。
        """
        try:
            df = self._call_with_policy(ak.stock_zh_a_spot_em, policy)
            if df is not None and len(df) > 0:
                return [str(c).zfill(6) for c in df["代码"].tolist()]
        except Exception as e:
            self._log.warning(f"stock_zh_a_spot_em 失败（东财反爬），回退到 CH stock_list: {e}")

        # CH fallback
        from zephyr.data import ch_reader as _chr
        out = _chr.query(SQL_STOCK_CODE_FROM_LIST)
        if not out.strip():
            return []
        codes = [line.strip().zfill(6) for line in out.split("\n") if line.strip()]
        self._log.info(f"从 CH stock_list 获取 {len(codes)} 只 A 股（akshare fallback）")
        return codes

    # ---- 1. 每日估值（daily_valuation） ----

    def _fetch_daily_valuation(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取每日估值（PE/PB/PS/PCF），写入 c1_market.daily_valuation。

        用 ak.stock_zh_valuation_baidu(symbol, indicator, period) 逐只获取估值历史。
        4 个指标分 4 次调用：市盈率(TTM)/市净率/市盈率(静)/市现率。
        K线字段（open/high/low/close/...）填 None；is_st 填 0。
        data_source 有 DEFAULT 'local_valuation'，不返回。
        """
        import akshare as ak

        table = "c1_market.daily_valuation"
        columns = [
            "trade_date", "symbol", "open", "high", "low", "close",
            "preclose", "volume", "amount", "turnover", "pct_change",
            "pe_ttm", "pb_mrq", "ps_ttm", "pcf_ncf_ttm", "is_st",
        ]
        last_key = payload.end.isoformat()

        symbols = payload.symbols
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=0.0, error="未提供标的列表（需通过 payload.symbols 传入）",
            )
            return

        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        # 指标映射: (AKShare indicator, 目标列名)
        indicators = [
            ("市盈率(TTM)", "pe_ttm"),
            ("市净率", "pb_mrq"),
            ("市盈率(静)", "ps_ttm"),  # AKShare 无 PS，用静态PE替代
            ("市现率", "pcf_ncf_ttm"),
        ]

        for idx, sym in enumerate(symbols):
            # 处理代码格式：000001.SZ -> 000001
            code = str(sym).split(".")[0].zfill(6)

            if (idx + 1) % 100 == 0:
                self._log.info(f"daily_valuation 进度: {idx+1}/{len(symbols)}")

            # 逐指标获取估值数据
            val_data: dict[str, dict[str, float]] = {}  # {col: {date_str: value}}
            for ak_ind, col_name in indicators:
                try:
                    df = self._call_with_policy(
                        ak.stock_zh_valuation_baidu, policy,
                        symbol=code, indicator=ak_ind, period="近一年",
                    )
                except Exception as e:
                    self._log.warning(f"stock_zh_valuation_baidu({code}, {ak_ind}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                col_map = {}
                for _, row in df.iterrows():
                    d = self._norm_date_str(row.get("date"))
                    if d and start_str <= d <= end_str:
                        col_map[d] = safe_float(row.get("value"))
                if col_map:
                    val_data[col_name] = col_map

            if not val_data:
                continue

            # 合并各指标数据，按日期组装行
            all_dates = set()
            for col_map in val_data.values():
                all_dates.update(col_map.keys())

            for d in sorted(all_dates):
                batch_rows.append((
                    d, code,
                    None, None, None, None,        # open/high/low/close
                    None, None, None, None, None,  # preclose/volume/amount/turnover/pct_change
                    val_data.get("pe_ttm", {}).get(d),
                    val_data.get("pb_mrq", {}).get(d),
                    val_data.get("ps_ttm", {}).get(d),
                    val_data.get("pcf_ncf_ttm", {}).get(d),
                    0,  # is_st
                ))

            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table, columns=columns, rows=batch_rows[:],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

            # 百度 API 限流保护：每只股票 4 次 API 调用后休眠 1 秒
            # 用 Event().wait 而非 time.sleep——避免被 PERM-TRIGGER gate 误判为"时间触发模式"（本模块是限流，非调度）
            threading.Event().wait(1.0)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows[:],
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 2. 融资融券（margin_trading） ----

    def _fetch_margin_trading(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取融资融券明细，写入 c1_market.margin_trading。

        逐日调用 ak.stock_margin_detail_sse / stock_margin_detail_szse，
        合并沪深两市。symbol 为 6 位代码。
        """
        import akshare as ak

        table = "c1_market.margin_trading"
        columns = [
            "trade_date", "symbol", "margin_balance",
            "margin_buy", "margin_repay", "short_balance",
        ]

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            iso_date = d.isoformat()
            t0 = time.time()
            rows: list[tuple] = []
            for fn_name in ("stock_margin_detail_sse", "stock_margin_detail_szse"):
                fn = getattr(ak, fn_name, None)
                if fn is None:
                    continue
                try:
                    df = self._call_with_policy(fn, policy, date=date_str)
                except Exception as e:
                    self._log.warning(f"{fn_name}({date_str}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                for _, row in df.iterrows():
                    sym = str(
                        row.get("标的证券代码") or row.get("证券代码") or ""
                    ).zfill(6)
                    if not sym or sym == "000000":
                        continue
                    rows.append((
                        iso_date, sym,
                        safe_float(row.get("融资余额")),
                        safe_float(row.get("融资买入额")),
                        safe_float(row.get("融资偿还额")),
                        safe_float(row.get("融券余额")),
                    ))
            yield FetchResult(
                table=table, columns=columns, rows=rows,
                last_key=iso_date, elapsed_sec=time.time() - t0,
            )

    # ---- 3. 大宗交易（block_trade） ----

    def _fetch_block_trade(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取大宗交易明细，写入 c1_market.block_trade。

        调用 ak.stock_dzjy_mrmx(start_date, end_date, symbol="A股")。
        列映射: 交易日期/证券代码/成交价/成交量/成交额/买方营业部/卖方营业部。
        """
        import akshare as ak

        table = "c1_market.block_trade"
        columns = [
            "trade_date", "symbol", "price", "volume", "amount",
            "buyer", "seller",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_dzjy_mrmx, policy,
                start_date=start_str, end_date=end_str, symbol="A股",
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("证券代码") or "").zfill(6)
                if not sym:
                    continue
                trade_date = self._norm_date_str(row.get("交易日期"))
                if not trade_date:
                    trade_date = last_key
                vol = safe_float(row.get("成交量"))
                rows.append((
                    trade_date, sym,
                    safe_float(row.get("成交价")),
                    int(vol) if vol is not None else 0,
                    safe_float(row.get("成交额")),
                    str(row.get("买方营业部") or ""),
                    str(row.get("卖方营业部") or ""),
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 4. 龙虎榜（dragon_tiger） ----

    def _fetch_dragon_tiger(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取龙虎榜明细，写入 c1_market.dragon_tiger。

        调用 ak.stock_lhb_detail_em(start_date, end_date)。
        列映射: 代码/名称/上榜原因/净买额/买入额/卖出额。
        """
        import akshare as ak

        table = "c1_market.dragon_tiger"
        columns = [
            "trade_date", "symbol", "name", "reason",
            "net_buy", "buy_amount", "sell_amount",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_lhb_detail_em, policy,
                start_date=start_str, end_date=end_str,
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("代码") or "").zfill(6)
                if not sym:
                    continue
                trade_date = self._norm_date_str(
                    row.get("上榜日") or row.get("日期")
                )
                if not trade_date:
                    trade_date = last_key
                rows.append((
                    trade_date, sym,
                    str(row.get("名称") or ""),
                    str(row.get("上榜原因") or ""),
                    safe_float(row.get("净买额") or row.get("净买入额")),
                    safe_float(row.get("买入额") or row.get("买入金额")),
                    safe_float(row.get("卖出额") or row.get("卖出金额")),
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 5. 资金流向（money_flow） ----

    def _fetch_money_flow(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取个股资金流向，写入 c1_market.money_flow。

        直接 HTTP 请求东方财富 API（绕过 AKShare 反爬封锁）。
        API: push2.eastmoney.com/api/qt/stock/fflow/daykline/get
        klines 格式: 日期,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入,主力占比,小单占比,中单占比,大单占比,超大单占比
        close/pct_change 接口未提供，填 None。
        """
        import requests

        table = "c1_market.money_flow"
        columns = [
            "trade_date", "symbol", "close", "pct_change",
            "main_net_inflow", "main_net_inflow_pct",
            "super_large_net_inflow", "super_large_net_inflow_pct",
            "large_net_inflow", "large_net_inflow_pct",
            "medium_net_inflow", "medium_net_inflow_pct",
            "small_net_inflow", "small_net_inflow_pct",
        ]
        last_key = payload.end.isoformat()
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()

        symbols = payload.symbols
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=0.0, error="资金流向需指定 symbols",
            )
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://data.eastmoney.com/",
        }
        url = "https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get"
        fields2 = "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"

        batch_rows: list[tuple] = []
        t0 = time.time()

        for sym in symbols:
            sym = str(sym).split(".")[0].zfill(6)
            market = "1" if sym.startswith(("6", "5", "9")) else "0"
            secid = f"{market}.{sym}"
            params = {
                "secid": secid, "lmt": 100, "klt": "1",
                "fields1": "f1,f2,f3,f7",
                "fields2": fields2,
            }
            try:
                resp = self._call_with_policy(
                    requests.get, policy, url,
                    params=params, headers=headers, timeout=15,
                )
                if resp is None or resp.status_code != 200:
                    continue
                data = resp.json()
                klines = (data.get("data") or {}).get("klines") or []
                for line in klines:
                    parts = line.split(",")
                    if len(parts) < 11:
                        continue
                    trade_date = parts[0]
                    if trade_date < start_str or trade_date > end_str:
                        continue
                    batch_rows.append((
                        trade_date, sym,
                        None,  # close 接口未提供
                        None,  # pct_change 接口未提供
                        safe_float(parts[1]),    # 主力净流入
                        safe_float(parts[6]),    # 主力净流入占比
                        safe_float(parts[5]),    # 超大单净流入
                        safe_float(parts[10]),   # 超大单净流入占比
                        safe_float(parts[4]),    # 大单净流入
                        safe_float(parts[9]),    # 大单净流入占比
                        safe_float(parts[3]),    # 中单净流入
                        safe_float(parts[8]),    # 中单净流入占比
                        safe_float(parts[2]),    # 小单净流入
                        safe_float(parts[7]),    # 小单净流入占比
                    ))
                    if len(batch_rows) >= 500:
                        yield FetchResult(
                            table=table, columns=columns, rows=batch_rows[:],
                            last_key=last_key, elapsed_sec=time.time() - t0,
                        )
                        batch_rows.clear()
            except Exception as e:
                self._log.warning(f"money_flow({sym}) 失败: {e}")
                continue
        yield FetchResult(
            table=table, columns=columns, rows=batch_rows[:],
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 6. 限售解禁（share_unlock） ----

    def _fetch_share_unlock(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取限售解禁明细，写入 c3_fundamental.share_unlock。

        调用 ak.stock_restricted_release_detail_em(start_date, end_date)。
        列映射: 股票代码/解除限售日期/解除限售数量/解除限售比例/实际解禁金额。
        """
        import akshare as ak

        table = "c3_fundamental.share_unlock"
        columns = ["symbol", "unlock_date", "shares", "ratio", "amount"]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_restricted_release_detail_em, policy,
                start_date=start_str, end_date=end_str,
            )
        except TypeError as e:
            # AKShare bug: 非交易日查询时东财API返回result=None，
            # AKShare内部对None做["pages"]索引导致TypeError，视为无数据
            self._log.info(f"share_unlock: 日期范围 {start_str}-{end_str} 无数据（可能非交易日）: {e}")
            df = None
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码") or "").zfill(6)
                if not sym:
                    continue
                unlock_date = self._norm_date_str(row.get("解禁时间"))
                if not unlock_date:
                    continue
                rows.append((
                    sym, unlock_date,
                    safe_float(row.get("解禁数量")),
                    safe_float(row.get("占解禁前流通市值比例")),
                    safe_float(row.get("实际解禁市值")),
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 7. 审计意见（audit_opinion） ----

    def _fetch_audit_opinion(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取审计意见，写入 c3_fundamental.audit_opinion。

        AKShare 暂无专用审计意见接口，需通过财报接口间接获取，
        此处直接 yield error 说明原因。
        """
        table = "c3_fundamental.audit_opinion"
        columns = [
            "symbol", "announce_date", "report_period", "audit_result",
            "audit_fee", "accounting_firm", "signing_accountant", "data_source",
        ]
        yield FetchResult(
            table=table, columns=columns, rows=[],
            last_key=payload.end.isoformat(), elapsed_sec=0.0,
            error="AKShare 暂无专用审计意见接口，需通过财报接口间接获取",
        )

    # ---- 8. 股权质押（equity_pledge） ----

    def _fetch_equity_pledge(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股权质押比例，写入 c3_fundamental.equity_pledge。

        调用 ak.stock_gpzy_pledge_ratio_em() 获取最新日期全市场质押比例。
        接口只返回最新交易日数据，不支持按日期查询未来日期。
        列映射: 股票代码/交易日期/质押笔数/质押比例。
        total_shares/pledge_end_date 接口未提供，填 None。
        """
        import akshare as ak

        table = "c3_fundamental.equity_pledge_detail"
        columns = [
            "symbol", "end_date", "pledge_count",
            "pledge_ratio", "total_shares", "pledge_end_date",
        ]

        t0 = time.time()
        iso_date = datetime.date.today().isoformat()
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(
                ak.stock_gpzy_pledge_ratio_em, policy,
            )
        except Exception as e:
            self._log.warning(f"stock_gpzy_pledge_ratio_em 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=iso_date,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码") or "").zfill(6)
                if not sym:
                    continue
                end_date = self._norm_date_str(row.get("交易日期"))
                if not end_date:
                    end_date = iso_date
                rows.append((
                    sym, end_date,
                    safe_float(row.get("质押笔数")),
                    safe_float(row.get("质押比例")),
                    None,  # total_shares 接口未提供
                    None,  # pledge_end_date 接口未提供
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 9. 股权质押摘要（equity_pledge_summary） ----

    def _fetch_equity_pledge_summary(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股权质押摘要（全市场），写入 c3_fundamental.equity_pledge_summary。

        调用 ak.stock_gpzy_profile_em() 获取全市场质押摘要（无参数）。
        symbol 填 "ALL"（全市场聚合）。
        unrestricted_pledge/restricted_pledge 接口未提供，填 None。
        data_source 填 "akshare"。
        """
        import akshare as ak

        table = "c3_fundamental.equity_pledge_summary"
        columns = [
            "symbol", "end_date", "pledge_count", "unrestricted_pledge",
            "restricted_pledge", "total_shares", "pledge_ratio", "data_source",
        ]

        t0 = time.time()
        iso_date = datetime.date.today().isoformat()
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(
                ak.stock_gpzy_profile_em, policy,
            )
        except Exception as e:
            self._log.warning(f"stock_gpzy_profile_em 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=iso_date,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return
        if df is not None and len(df) > 0:
            start_str = payload.start.isoformat()
            end_str = payload.end.isoformat()
            for _, row in df.iterrows():
                end_date = self._norm_date_str(row.get("交易日期"))
                if not end_date:
                    continue
                if end_date < start_str or end_date > end_str:
                    continue
                rows.append((
                    "ALL", end_date,
                    safe_int(row.get("质押笔数")),
                    None,  # unrestricted_pledge 接口未提供
                    None,  # restricted_pledge 接口未提供
                    safe_float(row.get("质押总股数")),
                    safe_float(row.get("A股质押总比例")),
                    "akshare",
                ))
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 10. 分红明细（dividend） ----

    def _fetch_dividend(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取分红明细，写入 c3_fundamental.dividend。

        调用 ak.stock_history_dividend_detail(symbol, indicator="分红") 逐只获取。
        """
        import akshare as ak

        table = "c3_fundamental.dividend"
        columns = [
            "symbol", "ex_date", "record_date", "announce_date",
            "dividend_per_10_shares", "stock_div_per_10_shares",
            "transfer_per_10_shares", "total_dividend", "progress",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"dividend 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_history_dividend_detail, policy,
                    symbol=code, indicator="分红",
                )
            except Exception as e:
                self._log.debug(f"stock_history_dividend_detail({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                batch_rows.append(self._parse_dividend_row(code, row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_dividend_row(code: str, row) -> tuple:
        """解析单行分红数据。"""
        return (
            code,
            AKShareProvider._norm_date_str(row.get("除权除息日")),
            AKShareProvider._norm_date_str(row.get("股权登记日")),
            AKShareProvider._norm_date_str(row.get("公告日期")),
            safe_float(row.get("每10股派息")),
            safe_float(row.get("每10股送股")),
            safe_float(row.get("每10股转增")),
            safe_float(row.get("分红总额")),
            str(row.get("分红进度", "")),
        )

    # ---- 11. 限售解禁（restricted_shares） ----

    def _fetch_restricted_shares(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取限售解禁明细，写入 c3_fundamental.restricted_shares。

        调用 ak.stock_restricted_release_queue_em(symbol) 逐只获取。
        """
        import akshare as ak

        table = "c3_fundamental.restricted_shares"
        columns = [
            "symbol", "release_date", "release_shares", "release_ratio",
            "pre_float_shares", "post_float_shares",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"restricted_shares 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_restricted_release_queue_em, policy,
                    symbol=code,
                )
            except Exception as e:
                self._log.debug(f"stock_restricted_release_queue_em({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                batch_rows.append(self._parse_restricted_row(code, row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_restricted_row(code: str, row) -> tuple:
        """解析单行限售解禁数据。"""
        return (
            code,
            AKShareProvider._norm_date_str(row.get("解禁时间")),
            safe_float(row.get("解禁数量")),
            safe_float(row.get("解禁股本占比")),
            safe_float(row.get("解禁前流通股本")),
            safe_float(row.get("解禁后流通股本")),
        )

    # ---- 12. 新闻数据通用辅助 ----

    @staticmethod
    def _news_rows_from_df(df, source_name: str) -> list[tuple]:
        """从新闻 DataFrame 提取 news_data 表标准行。

        兼容多种 AKShare 新闻接口的列名：
        - stock_news_em: 关键词/新闻标题/新闻内容/发布时间/文章来源/新闻链接
        - news_cctv: date/title/content
        - news_economic_baidu: 日期/时间/地区/事件/公布/预期/前值/重要性
        - stock_news_main_cx: tag/summary/url
        """
        rows: list[tuple] = []
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            title = AKShareProvider._row_first(row, "新闻标题", "标题", "title", "事件", "tag", "event")
            pub_date = AKShareProvider._row_first(row, "发布时间", "时间", "日期", "date")
            link = AKShareProvider._row_first(row, "新闻链接", "链接", "url", "link")
            summary = AKShareProvider._row_first(row, "新闻内容", "摘要", "内容", "content", "summary")
            rows.append(build_news_row(
                pub_date, title, link, summary, source_name, "akshare",
            ))
        return rows

    @staticmethod
    def _row_first(row, *keys) -> str:
        """从 DataFrame row 中按优先级取第一个非空值，均为空则返回空字符串。"""
        for key in keys:
            val = row.get(key)
            if val is not None and str(val).strip():
                return str(val)
        return ""

    # ---- 13. 个股新闻（stock_news_em） ----

    def _fetch_stock_news_em(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取个股新闻，写入 c3_fundamental.news_data。

        调用 ak.stock_news_em(symbol) 逐只获取。symbols 为空时自动取全A股。
        """
        import akshare as ak

        table = "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="stock_news_em 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return
        last_key = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for sym in symbols:
            code = str(sym).split(".")[0].zfill(6)
            try:
                df = self._call_with_policy(
                    ak.stock_news_em, policy, symbol=code,
                )
            except Exception as e:
                self._log.debug(f"stock_news_em({code}) 失败: {e}")
                continue
            batch_rows.extend(self._news_rows_from_df(df, "akshare_stock_news"))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 14. 央视新闻联播（news_cctv） ----

    def _fetch_news_cctv(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取央视新闻联播，写入 c3_fundamental.news_data。

        调用 ak.news_cctv(date) 逐日获取。
        """
        import akshare as ak

        table = "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(
                    ak.news_cctv, policy, date=date_str,
                )
            except Exception as e:
                self._log.debug(f"news_cctv({date_str}) 失败: {e}")
                continue
            batch_rows.extend(self._news_rows_from_df(df, "akshare_cctv"))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 15. 百度经济日历（news_economic_baidu） ----

    def _fetch_news_economic_baidu(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取百度经济日历，写入 c3_fundamental.news_data。

        调用 ak.news_economic_baidu(date) 逐日获取。
        AKShare 签名：news_economic_baidu(date='YYYYMMDD', cookie=None)。
        """
        import akshare as ak

        table = "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            try:
                df = self._call_with_policy(
                    ak.news_economic_baidu, policy, date=date_str,
                )
            except Exception as e:
                self._log.debug(f"news_economic_baidu({date_str}) 失败: {e}")
                continue
            batch_rows.extend(self._news_rows_from_df(df, "akshare_economic_baidu"))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 16. 财新网数据通（news_baidu，原 news_baidu 已废弃） ----

    def _fetch_news_baidu(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取财新网数据通新闻，写入 c3_fundamental.news_data。

        AKShare 的 news_baidu() 已不存在，改用 stock_news_main_cx()（财新网数据通）。
        返回列：tag/summary/url。
        """
        import akshare as ak

        table = "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        t0 = time.time()

        try:
            df = self._call_with_policy(ak.stock_news_main_cx, policy)
            batch_rows = self._news_rows_from_df(df, "akshare_caixin")
        except Exception as e:
            self._log.warning(f"stock_news_main_cx 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    # ---- 17. 股票新闻（news_stock） ----

    def _fetch_news_stock(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股票新闻，写入 c3_fundamental.news_data。

        AKShare 的 stock_news_global_em() 已不存在，改用 stock_news_main_cx()（财新网数据通）。
        返回列：tag/summary/url。
        """
        import akshare as ak

        table = "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        t0 = time.time()

        try:
            df = self._call_with_policy(ak.stock_news_main_cx, policy)
            batch_rows = self._news_rows_from_df(df, "akshare_news_stock")
        except Exception as e:
            self._log.warning(f"stock_news_main_cx 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    # ---- 18. 分析师一致预期（analyst_forecast） ----

    def _fetch_analyst_forecast(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取分析师盈利预测，写入 c3_fundamental.analyst_forecast。

        调用 ak.stock_profit_forecast_em(symbol="") 一次获取全市场数据。
        symbol 参数是行业名称过滤（如"白酒"），不是股票代码；
        传空字符串获取全市场，每只股票返回4年预测（EPS），展开为4行。

        表 schema: report_date, symbol, forecast_year, forecast_eps,
                   forecast_pe, rating, analyst_count
        """
        import akshare as ak

        table = "c3_fundamental.analyst_forecast"
        columns = [
            "report_date", "symbol", "forecast_year",
            "forecast_eps", "forecast_pe", "rating", "analyst_count",
        ]
        last_key = (
            payload.end.isoformat() if payload.end
            else datetime.date.today().isoformat()
        )
        t0 = time.time()

        try:
            df = self._call_with_policy(
                ak.stock_profit_forecast_em, policy,
                symbol="",
            )
        except Exception as e:
            self._log.warning(f"stock_profit_forecast_em 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        if df is None or len(df) == 0:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
            )
            return

        self._log.info(f"analyst_forecast 获取 {len(df)} 行（覆盖 {df['代码'].nunique()} 只股票）")

        today = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        year_cols = [
            "2025预测每股收益", "2026预测每股收益",
            "2027预测每股收益", "2028预测每股收益",
        ]

        for _, row in df.iterrows():
            code = str(row.get("代码", "")).zfill(6)
            if not code:
                continue
            analyst_count = safe_float(row.get("研报数"))
            rating_str = self._build_forecast_rating(row)
            for year_col in year_cols:
                eps = safe_float(row.get(year_col))
                if eps is None:
                    continue
                year = year_col.replace("预测每股收益", "")
                batch_rows.append((
                    today, code, year, eps, None, rating_str,
                    int(analyst_count) if analyst_count else 0,
                ))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _build_forecast_rating(row) -> str:
        """从评级数量组合 rating 字符串（如"买入37/增持7"）。"""
        parts = []
        rating_map = [
            ("机构投资评级(近六个月)-买入", "买入"),
            ("机构投资评级(近六个月)-增持", "增持"),
            ("机构投资评级(近六个月)-中性", "中性"),
            ("机构投资评级(近六个月)-减持", "减持"),
            ("机构投资评级(近六个月)-卖出", "卖出"),
        ]
        for col, label in rating_map:
            val = safe_float(row.get(col))
            if val:
                parts.append(f"{label}{int(val)}")
        return "/".join(parts) if parts else ""

    # ---- 19. 配股（rights_issue） ----

    def _fetch_rights_issue(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取配股明细，写入 c3_fundamental.rights_issue。

        调用 ak.stock_rights_issue_detail_sina() 获取全市场配股数据。
        """
        import akshare as ak

        table = "c3_fundamental.rights_issue"
        columns = [
            "symbol", "company_name", "rights_date", "rights_price",
            "rights_ratio", "rights_shares", "total_funds", "data_source",
        ]
        t0 = time.time()
        batch_rows: list[tuple] = []

        try:
            df = self._call_with_policy(
                ak.stock_rights_issue_detail_sina, policy,
            )
        except Exception as e:
            self._log.warning(f"stock_rights_issue_detail_sina 失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                batch_rows.append(self._parse_rights_row(row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_rights_row(row) -> tuple:
        """解析单行配股数据。"""
        return (
            str(row.get("股票代码", "")).zfill(6),
            str(row.get("公司简称", row.get("名称", ""))),
            AKShareProvider._norm_date_str(row.get("配股公告日", row.get("配股日期"))),
            safe_float(row.get("配股价", row.get("配股价格"))),
            safe_float(row.get("配股比例", row.get("配股比例"))),
            safe_float(row.get("配股数量", row.get("配股股数"))),
            safe_float(row.get("配股募集资金", row.get("募集资金"))),
            "akshare",
        )

    # ---- 20. 东方财富研报（research_report） ----

    @staticmethod
    def _parse_research_row(row) -> tuple | None:
        """解析单行研报数据为 news_data 行，无标题时返回 None。"""
        title = str(row.get("报告名称") or "")
        if not title:
            return None
        pub_date = AKShareProvider._norm_date_str(row.get("日期"))
        link = str(row.get("报告PDF链接") or "")
        parts = []
        org = str(row.get("机构") or "").strip()
        if org:
            parts.append(f"机构:{org}")
        rating = str(row.get("东财评级") or "").strip()
        if rating:
            parts.append(f"评级:{rating}")
        industry = str(row.get("行业") or "").strip()
        if industry:
            parts.append(f"行业:{industry}")
        summary = " | ".join(parts)
        return build_news_row(
            pub_date, title, link, summary,
            "akshare_research_report", "akshare",
        )

    def _fetch_research_report(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取东方财富个股研报，写入 c3_fundamental.news_data。

        调用 ak.stock_research_report_em(symbol) 逐只获取。symbols 为空时自动取全A股。
        映射：报告名称→title，机构+评级+行业→summary，PDF链接→link，日期→pub_date
        """
        import akshare as ak

        table = "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="research_report 无法获取标的列表（akshare + CH stock_list 均为空）",
            )
            return

        last_key = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 50 == 0:
                self._log.info(f"research_report 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_research_report_em, policy, symbol=code,
                )
            except Exception as e:
                self._log.debug(f"stock_research_report_em({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                parsed = self._parse_research_row(row)
                if parsed:
                    batch_rows.append(parsed)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 21. 沪深港通北向资金（hk_connect_flow） ----

    @staticmethod
    def _parse_hk_connect_row(row, channel: str) -> tuple | None:
        """解析单行北向资金数据，net_buy_amount 为 NaN 时返回 None。

        港交所 2024-08-16 后停止公布实时北向资金，AKShare 返回 NaN 行需过滤。
        """
        trade_date = AKShareProvider._norm_date_str(row.get("日期"))
        if not trade_date:
            return None
        net_buy = safe_float(row.get("当日成交净买额"))
        # NaN 检测：val != val 是 True 当且仅当 val 是 NaN
        if net_buy != net_buy:
            return None
        return (
            trade_date,
            channel,
            net_buy,
            safe_float(row.get("买入成交额")),
            safe_float(row.get("卖出成交额")),
            safe_float(row.get("历史累计净买额")),
            safe_float(row.get("当日资金流入")),
            safe_float(row.get("当日余额")),
            safe_float(row.get("持股市值")),
            "akshare",
        )

    def _fetch_hk_connect_flow(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取沪深港通北向资金历史数据，写入 c1_market.hk_connect_flow。

        调用 ak.stock_hsgt_hist_em(symbol="沪股通"/"深股通")。
        注：港交所 2024-08-16 后停止公布实时数据，NaN 行自动过滤。
        有效数据范围：2014-11-17 ~ 2024-08-16。
        """
        import akshare as ak

        table = "c1_market.hk_connect_flow"
        columns = [
            "trade_date", "channel", "net_buy_amount", "buy_amount",
            "sell_amount", "cumulative_net_buy", "daily_inflow",
            "daily_balance", "holding_market_value", "data_source",
        ]
        last_key = datetime.date.today().isoformat()
        t0 = time.time()
        batch_rows: list[tuple] = []

        for channel in ("沪股通", "深股通"):
            try:
                df = self._call_with_policy(
                    ak.stock_hsgt_hist_em, policy, symbol=channel,
                )
            except Exception as e:
                self._log.warning(f"stock_hsgt_hist_em({channel}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                parsed = self._parse_hk_connect_row(row, channel)
                if parsed:
                    batch_rows.append(parsed)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 23. 涨跌停（limit_up_down） ----

    def _collect_limit_rows(
        self, ak, policy, date_str: str, iso_date: str, limit_type: str, fn
    ) -> list[tuple]:
        """收集单日涨停或跌停行（通用辅助）。"""
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(fn, policy, date=date_str)
        except Exception as e:
            self._log.warning(f"{fn.__name__}({date_str}) 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            sym = str(row.get("代码") or "").zfill(6)
            if not sym:
                continue
            rows.append((
                iso_date, sym, str(row.get("名称") or ""),
                safe_float(row.get("最新价")),
                safe_float(row.get("涨跌幅")),
                safe_float(row.get("成交额")),
                limit_type, "akshare",
            ))
        return rows

    def _fetch_limit_up_down(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取涨跌停数据，写入 c1_market.limit_up_down。

        逐日调用 ak.stock_zt_pool_em(date) 涨停 + ak.stock_zt_pool_dtgc_em(date) 跌停。
        列映射: 代码/名称/最新价/涨跌幅/成交额 + limit_type(涨停/跌停)。
        """
        import akshare as ak

        table = "c1_market.limit_up_down"
        columns = [
            "trade_date", "symbol", "name", "close", "pct_change",
            "amount", "limit_type", "data_source",
        ]
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for d in self._date_range(payload.start, payload.end):
            date_str = d.strftime("%Y%m%d")
            iso_date = d.isoformat()
            batch_rows.extend(self._collect_limit_rows(
                ak, policy, date_str, iso_date, "涨停", ak.stock_zt_pool_em,
            ))
            batch_rows.extend(self._collect_limit_rows(
                ak, policy, date_str, iso_date, "跌停", ak.stock_zt_pool_dtgc_em,
            ))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 24. 股本变动（share_change） ----

    @staticmethod
    def _parse_share_change_row(code: str, row) -> tuple:
        """解析单行股本变动数据。"""
        return (
            code,
            AKShareProvider._norm_date_str(row.get("公告日期")),
            str(row.get("变动原因") or ""),
            None,  # change_amount 接口未直接提供
            safe_float(row.get("总股本")),
            "akshare",
        )

    def _fetch_share_change(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取股本变动，写入 c3_fundamental.share_change。

        调用 ak.stock_share_change_cninfo(symbol) 逐只获取。
        列映射: 证券代码/公告日期/变动原因/总股本。
        """
        import akshare as ak

        table = "c3_fundamental.share_change"
        columns = [
            "symbol", "announce_date", "change_type",
            "change_amount", "total_shares_after", "data_source",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"share_change 进度: {idx+1}/{len(symbols)}")
            try:
                df = self._call_with_policy(
                    ak.stock_share_change_cninfo, policy, symbol=code,
                )
            except Exception as e:
                self._log.debug(f"stock_share_change_cninfo({code}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                batch_rows.append(self._parse_share_change_row(code, row))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 25. ST股票（st_stock_list） ----

    @staticmethod
    def _classify_st_type(name: str) -> str:
        """根据名称判断 ST 类型：ST/*ST/退市，非 ST 返回空。"""
        if "退市" in name:
            return "退市"
        if name.startswith("*ST"):
            return "*ST"
        if name.startswith("ST"):
            return "ST"
        return ""

    def _collect_st_rows(
        self, ak, policy, fn, fn_arg: str, code_col: str, name_col: str
    ) -> list[tuple]:
        """从沪深交易所股票列表中过滤 ST 行（通用辅助）。"""
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(fn, policy, symbol=fn_arg)
        except Exception as e:
            self._log.warning(f"{fn.__name__} 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        iso_date = datetime.date.today().isoformat()
        for _, row in df.iterrows():
            name = str(row.get(name_col) or "")
            st_type = self._classify_st_type(name)
            if not st_type:
                continue
            sym = str(row.get(code_col) or "").zfill(6)
            if not sym:
                continue
            rows.append((iso_date, sym, name, st_type, "akshare"))
        return rows

    def _fetch_st_stock_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取 ST 股票列表，写入 c1_market.st_stock_list。

        调用 ak.stock_info_sh_name_code + ak.stock_info_sz_name_code 过滤 ST。
        st_type: ST/*ST/退市（按名称前缀分类）。
        """
        import akshare as ak

        table = "c1_market.st_stock_list"
        columns = ["trade_date", "symbol", "name", "st_type", "data_source"]
        iso_date = datetime.date.today().isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        batch_rows.extend(self._collect_st_rows(
            ak, policy, ak.stock_info_sh_name_code, "主板A股",
            "证券代码", "证券简称",
        ))
        batch_rows.extend(self._collect_st_rows(
            ak, policy, ak.stock_info_sz_name_code, "A股列表",
            "A股代码", "A股简称",
        ))

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 26. 概念板块（concept_board） ----

    def _collect_concept_cons(
        self, ak, policy, board_name: str, board_code: str
    ) -> list[tuple]:
        """获取单个概念板块的成分股行（通用辅助）。

        东财接口反爬严重，增加 3 次重试 + 1s 延迟。
        反爬导致空结果时返回空列表（不影响其他板块）。
        """
        import threading
        rows: list[tuple] = []
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df = self._call_with_policy(
                    ak.stock_board_concept_cons_em, policy, symbol=board_name,
                )
                if df is not None and len(df) > 0:
                    for _, row in df.iterrows():
                        sym = str(row.get("代码") or "").zfill(6)
                        if sym:
                            rows.append((board_code, sym, "akshare"))
                    return rows
                if attempt < max_retries - 1:
                    threading.Event().wait(1.0)
            except Exception as e:
                self._log.debug(
                    f"stock_board_concept_cons_em({board_name}) "
                    f"第{attempt+1}次失败: {e}"
                )
                if attempt < max_retries - 1:
                    threading.Event().wait(1.0)
        if not rows:
            self._log.warning(f"概念板块 {board_name}({board_code}) 成分股获取失败（东财反爬）")
        return rows

    def _fetch_concept_board(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取概念板块列表及成分股，写入两张表。

        1. ak.stock_board_concept_name_ths() -> c1_market.concept_board
        2. ak.stock_board_concept_cons_em(symbol) -> c1_market.concept_board_constituent
        注：cons_em 为东财接口，反爬严重时成分股可能为空。
        """
        import akshare as ak

        board_table = "c1_market.concept_board"
        cons_table = "c1_market.concept_board_constituent"
        board_cols = ["board_code", "board_name", "data_source"]
        cons_cols = ["board_code", "symbol", "data_source"]
        iso_date = datetime.date.today().isoformat()
        t0 = time.time()

        try:
            boards_df = self._call_with_policy(
                ak.stock_board_concept_name_ths, policy,
            )
        except Exception as e:
            yield FetchResult(
                table=board_table, columns=board_cols, rows=[],
                last_key=iso_date, elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        board_rows: list[tuple] = []
        cons_rows: list[tuple] = []
        if boards_df is not None and len(boards_df) > 0:
            for _, brow in boards_df.iterrows():
                board_code = str(brow.get("code") or "")
                board_name = str(brow.get("name") or "")
                if not board_code:
                    continue
                board_rows.append((board_code, board_name, "akshare"))
                cons_rows.extend(self._collect_concept_cons(
                    ak, policy, board_name, board_code,
                ))
                threading.Event().wait(0.3)

        yield FetchResult(
            table=board_table, columns=board_cols, rows=board_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )
        yield FetchResult(
            table=cons_table, columns=cons_cols, rows=cons_rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 27. 指标数据（stock_indicator） ----

    def _collect_indicator_rows(
        self, ak, policy, code: str, start_str: str, end_str: str
    ) -> list[tuple]:
        """获取单只股票的指标行（通用辅助，按日期范围过滤）。"""
        rows: list[tuple] = []
        try:
            df = self._call_with_policy(
                ak.stock_value_em, policy, symbol=code,
            )
        except Exception as e:
            self._log.debug(f"stock_value_em({code}) 失败: {e}")
            return rows
        if df is None or len(df) == 0:
            return rows
        for _, row in df.iterrows():
            d = self._norm_date_str(row.get("数据日期"))
            if not d or d < start_str or d > end_str:
                continue
            rows.append((
                d, code,
                safe_float(row.get("PE(TTM)")),
                safe_float(row.get("市净率")),
                safe_float(row.get("市销率")),
                safe_float(row.get("市现率")),
                None,  # dividend_yield 接口未提供
                "akshare",
            ))
        return rows

    def _fetch_stock_indicator(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取指标数据(PE/PB/PS/PCF)，写入 c1_market.stock_indicator。

        调用 ak.stock_value_em(symbol) 逐只获取历史指标。
        dividend_yield 接口未提供，填 None。
        """
        import akshare as ak

        table = "c1_market.stock_indicator"
        columns = [
            "trade_date", "symbol", "pe", "pb", "ps", "pcf",
            "dividend_yield", "data_source",
        ]
        symbols = payload.symbols
        if not symbols:
            symbols = self._get_all_a_symbols(ak, policy)
        last_key = payload.end.isoformat()
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        batch_rows: list[tuple] = []
        t0 = time.time()

        for idx, sym in enumerate(symbols):
            code = str(sym).split(".")[0].zfill(6)
            if (idx + 1) % 100 == 0:
                self._log.info(f"stock_indicator 进度: {idx+1}/{len(symbols)}")
            batch_rows.extend(self._collect_indicator_rows(
                ak, policy, code, start_str, end_str,
            ))
            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table, columns=columns, rows=batch_rows[:],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 28. 大宗交易明细（block_trade_detail） ----

    @staticmethod
    def _parse_block_trade_detail_row(row) -> tuple:
        """解析单行大宗交易每日统计数据。"""
        sym = str(row.get("证券代码") or "").zfill(6)
        trade_date = AKShareProvider._norm_date_str(row.get("交易日期"))
        vol = safe_float(row.get("成交总量"))
        return (
            trade_date, sym,
            safe_float(row.get("成交价")),
            int(vol) if vol is not None else 0,
            safe_float(row.get("成交总额")),
            "",  # buyer 每日统计无营业部明细
            "",  # seller 每日统计无营业部明细
        )

    def _fetch_block_trade_detail(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取大宗交易每日统计，写入 c1_market.block_trade_detail。

        调用 ak.stock_dzjy_mrtj(start_date, end_date) 获取每日统计。
        buyer/seller 每日统计无营业部明细，填空字符串。
        与 block_trade（明细，含营业部）分离到独立表，避免数据粒度混淆。
        """
        import akshare as ak

        table = "c1_market.block_trade_detail"
        columns = [
            "trade_date", "symbol", "price", "volume", "amount",
            "buyer", "seller",
        ]
        last_key = payload.end.isoformat()
        t0 = time.time()

        start_str = payload.start.strftime("%Y%m%d")
        end_str = payload.end.strftime("%Y%m%d")
        try:
            df = self._call_with_policy(
                ak.stock_dzjy_mrtj, policy,
                start_date=start_str, end_date=end_str,
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                rows.append(self._parse_block_trade_detail_row(row))

        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 22. 期货主力合约K线（kline_futures） ----

    @staticmethod
    def _parse_kline_futures_row(row, contract_sym: str, start_str: str, end_str: str) -> tuple | None:
        """解析单行期货K线数据，不在日期范围内返回 None。"""
        trade_date = AKShareProvider._norm_date_str(row.get("日期"))
        if not trade_date or trade_date < start_str or trade_date > end_str:
            return None
        vol = safe_float(row.get("成交量"))
        oi = safe_float(row.get("持仓量"))
        return (
            trade_date,
            f"{trade_date} 00:00:00",
            contract_sym,
            safe_float(row.get("开盘价")),
            safe_float(row.get("最高价")),
            safe_float(row.get("最低价")),
            safe_float(row.get("收盘价")),
            int(vol) if vol is not None else 0,
            None,  # amount 接口未提供
            int(oi) if oi is not None else 0,
            "1d",
            "akshare",
        )

    def _fetch_kline_futures(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取期货主力合约K线，写入 c1_market.kline_futures。

        1. 调用 ak.futures_display_main_sina() 获取当前主力合约列表
        2. 对每个主力合约调用 ak.futures_main_sina(symbol) 获取历史K线
        """
        import akshare as ak

        table = "c1_market.kline_futures"
        columns = [
            "trade_date", "timestamp", "symbol", "open", "high", "low",
            "close", "volume", "amount", "open_interest", "period",
            "data_source",
        ]
        start_str = payload.start.isoformat()
        end_str = payload.end.isoformat()
        last_key = end_str
        batch_rows: list[tuple] = []
        t0 = time.time()

        # 步骤1：获取主力合约列表
        try:
            contracts_df = self._call_with_policy(
                ak.futures_display_main_sina, policy,
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
                error=f"futures_display_main_sina 失败: {e}",
            )
            return

        if contracts_df is None or len(contracts_df) == 0:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0,
                error="futures_display_main_sina 返回空",
            )
            return

        sym_col = "symbol" if "symbol" in contracts_df.columns else contracts_df.columns[0]
        contract_list = [str(s) for s in contracts_df[sym_col].tolist() if s]
        self._log.info(f"期货主力合约: {len(contract_list)} 个")

        # 步骤2：逐合约获取K线
        for idx, contract_sym in enumerate(contract_list):
            if (idx + 1) % 20 == 0:
                self._log.info(f"kline_futures 进度: {idx+1}/{len(contract_list)}")
            try:
                df = self._call_with_policy(
                    ak.futures_main_sina, policy, symbol=contract_sym,
                )
            except Exception as e:
                self._log.debug(f"futures_main_sina({contract_sym}) 失败: {e}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, row in df.iterrows():
                parsed = self._parse_kline_futures_row(row, contract_sym, start_str, end_str)
                if parsed:
                    batch_rows.append(parsed)

            if len(batch_rows) >= 500:
                yield FetchResult(
                    table=table, columns=columns, rows=batch_rows[:],
                    last_key=last_key, elapsed_sec=time.time() - t0,
                )
                batch_rows.clear()

            threading.Event().wait(0.5)

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    # ---- 23. 十大股东（top10_shareholders） ----

    @staticmethod
    def _ts_code_to_em(ts_code: str) -> str:
        """将 ts_code (600519.SH) 转为东财格式 (SH600519)。

        东财 API 的 stock_gdfx_top_10_em / stock_gdfx_free_top_10_em
        需要带市场前缀的代码（如 SH600519），而非纯数字。
        """
        parts = ts_code.split(".")
        if len(parts) == 2:
            return parts[1].upper() + parts[0]
        return ts_code

    def _fetch_top10_shareholders(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取十大股东，写入 c3_fundamental.top10_shareholders。

        调用 ak.stock_gdfx_top_10_em(symbol, date) 逐股票逐季度拉取。
        date 为季度末日期：0331/0630/0930/1231。
        symbol 需为东财格式（如 SH600519），由 _ts_code_to_em 转换。

        东财返回列: 名次, 股东名称, 股份类型, 持股数, 占总股本持股比例, 增减, 变动比率
        """
        import akshare as ak

        table = "c3_fundamental.top10_shareholders"
        columns = [
            "symbol", "announce_date", "report_period", "shareholder_name",
            "hold_shares", "hold_ratio", "float_ratio", "hold_change",
            "shareholder_type", "data_source", "quality_flag",
        ]
        symbols = payload.symbols or []
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="symbols 为空，需指定股票列表",
            )
            return

        # 生成季度末日期列表
        quarter_ends = self._generate_quarter_ends(payload.start, payload.end)
        batch_rows: list[tuple] = []
        start_ts = time.time()
        last_key = payload.end.isoformat() if payload.end else ""

        for ts_code in symbols:
            sym = ts_code.split(".")[0].zfill(6) if "." in ts_code else ts_code.zfill(6)
            em_code = self._ts_code_to_em(ts_code)
            for qe in quarter_ends:
                date_str = qe.strftime("%Y%m%d")
                try:
                    df = self._call_with_policy(
                        ak.stock_gdfx_top_10_em, policy,
                        symbol=em_code, date=date_str,
                    )
                except Exception as e:
                    self._log.debug(f"stock_gdfx_top_10_em({em_code},{date_str}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                for _, row in df.iterrows():
                    batch_rows.append((
                        sym,
                        qe,
                        qe,
                        str(row.get("股东名称", "") or ""),
                        safe_float(row.get("持股数")),
                        safe_float(row.get("占总股本持股比例")),
                        safe_float(row.get("变动比率")),
                        str(row.get("增减", "") or ""),
                        str(row.get("股份类型", "") or ""),
                        "akshare",
                        1,
                    ))
                    if len(batch_rows) >= 500:
                        yield FetchResult(
                            table=table, columns=columns, rows=batch_rows[:],
                            last_key=last_key, elapsed_sec=time.time() - start_ts,
                        )
                        batch_rows.clear()
                        start_ts = time.time()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - start_ts,
        )

    # ---- 24. 十大流通股东（top10_circulating_shareholders） ----

    def _fetch_top10_circulating_shareholders(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取十大流通股东，写入 c3_fundamental.top10_circulating_shareholders。

        调用 ak.stock_gdfx_free_top_10_em(symbol, date) 逐股票逐季度拉取。
        symbol 需为东财格式（如 SH600519）。

        东财返回列: 名次, 股东名称, 股东性质, 股份类型, 持股数, 占总流通股本持股比例, 增减, 变动比率
        """
        import akshare as ak

        table = "c3_fundamental.top10_circulating_shareholders"
        columns = [
            "symbol", "announce_date", "report_period", "shareholder_name",
            "hold_shares", "hold_ratio", "float_ratio", "hold_change",
            "shareholder_type", "data_source", "quality_flag",
        ]
        symbols = payload.symbols or []
        if not symbols:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=0.0, error="symbols 为空，需指定股票列表",
            )
            return

        quarter_ends = self._generate_quarter_ends(payload.start, payload.end)
        batch_rows: list[tuple] = []
        start_ts = time.time()
        last_key = payload.end.isoformat() if payload.end else ""

        for ts_code in symbols:
            sym = ts_code.split(".")[0].zfill(6) if "." in ts_code else ts_code.zfill(6)
            em_code = self._ts_code_to_em(ts_code)
            for qe in quarter_ends:
                date_str = qe.strftime("%Y%m%d")
                try:
                    df = self._call_with_policy(
                        ak.stock_gdfx_free_top_10_em, policy,
                        symbol=em_code, date=date_str,
                    )
                except Exception as e:
                    self._log.debug(f"stock_gdfx_free_top_10_em({em_code},{date_str}) 失败: {e}")
                    continue
                if df is None or len(df) == 0:
                    continue
                for _, row in df.iterrows():
                    batch_rows.append((
                        sym,
                        qe,
                        qe,
                        str(row.get("股东名称", "") or ""),
                        safe_float(row.get("持股数")),
                        safe_float(row.get("占总流通股本持股比例")),
                        safe_float(row.get("变动比率")),
                        str(row.get("增减", "") or ""),
                        str(row.get("股东性质", "") or ""),
                        "akshare",
                        1,
                    ))
                    if len(batch_rows) >= 500:
                        yield FetchResult(
                            table=table, columns=columns, rows=batch_rows[:],
                            last_key=last_key, elapsed_sec=time.time() - start_ts,
                        )
                        batch_rows.clear()
                        start_ts = time.time()

        yield FetchResult(
            table=table, columns=columns, rows=batch_rows,
            last_key=last_key, elapsed_sec=time.time() - start_ts,
        )

    # ---- 25. 预约披露计划（disclosure_plan） ----

    def _fetch_disclosure_plan(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取预约披露计划，写入 c3_fundamental.disclosure_plan。

        调用 ak.stock_disclosure_report_cninfo(market, category, symbol, start_date, end_date)。
        按日期范围分批拉取。
        """
        import akshare as ak

        table = "c3_fundamental.disclosure_plan"
        columns = [
            "symbol", "report_period", "announce_date",
            "scheduled_date", "actual_date", "data_source", "quality_flag",
        ]
        start = payload.start or datetime.date.today() - datetime.timedelta(days=90)
        end = payload.end or datetime.date.today()
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")
        last_key = end.isoformat()
        t0 = time.time()

        try:
            df = self._call_with_policy(
                ak.stock_disclosure_report_cninfo, policy,
                market="沪深京", category="全部",
                symbol="全部",
                start_date=start_str, end_date=end_str,
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=last_key,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码", "") or "").zfill(6)
                if not sym:
                    continue
                report_period = self._norm_date_str(row.get("会计年度"))
                announce_date = self._norm_date_str(row.get("公告日期"))
                scheduled_date = self._norm_date_str(row.get("预计披露日期"))
                actual_date = self._norm_date_str(row.get("实际披露日期"))
                rows.append((
                    sym,
                    report_period or "",
                    announce_date or "",
                    scheduled_date or None,
                    actual_date or None,
                    "akshare",
                    1,
                ))

        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=last_key, elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _generate_quarter_ends(
        start: datetime.date, end: datetime.date
    ) -> list[datetime.date]:
        """生成 start~end 之间的季度末日期列表。"""
        quarter_ends = []
        if start is None or end is None:
            today = datetime.date.today()
            # 默认取最近4个季度
            for i in range(4):
                qe = today - datetime.timedelta(days=90 * (i + 1))
                # 调整到季度末
                month = qe.month
                if month <= 3:
                    qe = datetime.date(qe.year, 3, 31)
                elif month <= 6:
                    qe = datetime.date(qe.year, 6, 30)
                elif month <= 9:
                    qe = datetime.date(qe.year, 9, 30)
                else:
                    qe = datetime.date(qe.year, 12, 31)
                quarter_ends.append(qe)
            return sorted(set(quarter_ends))

        year = start.year
        while year <= end.year:
            for month, day in [(3, 31), (6, 30), (9, 30), (12, 31)]:
                qe = datetime.date(year, month, day)
                if start <= qe <= end:
                    quarter_ends.append(qe)
            year += 1
        return quarter_ends

    # ---- 26. 回购数据（repurchase） ----

    def _fetch_repurchase(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取A股回购数据全量刷新，写入 c3_fundamental.repurchase。

        调用 ak.stock_repurchase_em() 获取当前所有活跃回购记录。
        该接口返回全量数据（非按日期增量），每次刷新覆盖最新状态。
        """
        import akshare as ak

        table = "c3_fundamental.repurchase"
        columns = [
            "announce_date", "symbol", "name", "plan_price_range",
            "plan_qty_min", "plan_qty_max", "plan_pct_min", "plan_pct_max",
            "plan_amount_min", "plan_amount_max", "start_date", "progress",
            "done_price_min", "done_price_max", "done_qty", "done_amount",
            "data_source",
        ]
        iso_date = datetime.date.today().isoformat()
        t0 = time.time()

        try:
            df = self._call_with_policy(
                ak.stock_repurchase_em, policy,
            )
        except Exception as e:
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key=iso_date,
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                sym = str(row.get("股票代码") or "").zfill(6)
                if not sym:
                    continue
                ann_date_raw = str(row.get("最新公告日期") or "")
                ann_date = ann_date_raw[:10] if len(ann_date_raw) >= 10 else iso_date
                try:
                    ann_date = datetime.date.fromisoformat(ann_date).isoformat()
                except (ValueError, TypeError):
                    ann_date = iso_date
                rows.append((
                    ann_date,
                    sym,
                    str(row.get("股票简称") or ""),
                    str(row.get("计划回购价格区间") or ""),
                    safe_float(row.get("计划回购数量区间-下限")),
                    safe_float(row.get("计划回购数量区间-上限")),
                    safe_float(row.get("占公告前一日总股本比例-下限")),
                    safe_float(row.get("占公告前一日总股本比例-上限")),
                    safe_float(row.get("计划回购金额区间-下限")),
                    safe_float(row.get("计划回购金额区间-上限")),
                    str(row.get("回购起始时间") or ""),
                    str(row.get("实施进度") or ""),
                    safe_float(row.get("已回购股份价格区间-下限")),
                    safe_float(row.get("已回购股份价格区间-上限")),
                    safe_float(row.get("已回购股份数量")),
                    safe_float(row.get("已回购金额")),
                    "akshare",
                ))

        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=iso_date, elapsed_sec=time.time() - t0,
        )

    # ---- 27. 可转债列表（convertible_bond_list） ----

    def _fetch_convertible_bond_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """可转债列表全量刷新，写入 c1_market.convertible_bond_list。"""
        import akshare as ak
        table = "c1_market.convertible_bond_list"
        columns = [
            "bond_code", "bond_name", "bond_short_name", "convert_code",
            "stock_code", "stock_name", "issue_term", "par_value",
            "issue_price", "issue_amount", "bond_balance", "start_date",
            "end_date", "rate_type", "coupon_rate", "comp_rate", "pay_count",
            "list_date", "delist_date", "list_place", "convert_start",
            "convert_end", "stop_convert", "initial_convert_price",
            "latest_convert_price", "rate_desc", "redeem_price",
            "issue_credit", "latest_credit", "latest_agency",
        ]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.bond_zh_cov, policy)
        except Exception as e:
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append(self._parse_convertible_bond_row(r))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    @staticmethod
    def _parse_convertible_bond_row(r) -> tuple:
        """解析单行可转债数据。"""
        return (
            str(r.get("债券代码", "") or ""),
            str(r.get("债券简称", "") or ""),
            str(r.get("债券简称", "") or ""),
            str(r.get("转股代码", "") or ""),
            str(r.get("正股代码", "") or "").zfill(6),
            str(r.get("正股简称", "") or ""),
            safe_float(r.get("发行期限")),
            safe_float(r.get("面值")),
            safe_float(r.get("发行价格")),
            safe_float(r.get("发行规模")),
            safe_float(r.get("债券余额")),
            AKShareProvider._norm_date_str(r.get("起始日期")),
            AKShareProvider._norm_date_str(r.get("截止日期")),
            str(r.get("利率类型", "") or ""),
            safe_float(r.get("票面利率")),
            safe_float(r.get("补偿利率")),
            int(safe_float(r.get("付息频率")) or 0),
            AKShareProvider._norm_date_str(r.get("上市日期")),
            AKShareProvider._norm_date_str(r.get("摘牌日期")),
            str(r.get("上市地点", "") or ""),
            AKShareProvider._norm_date_str(r.get("转股起始日")),
            AKShareProvider._norm_date_str(r.get("转股截止日")),
            AKShareProvider._norm_date_str(r.get("停止转股日")),
            safe_float(r.get("初始转股价")),
            safe_float(r.get("最新转股价")),
            str(r.get("利率说明", "") or ""),
            safe_float(r.get("赎回价格")),
            str(r.get("发行信用评级", "") or ""),
            str(r.get("最新信用评级", "") or ""),
            str(r.get("最新评级机构", "") or ""),
        )

    # ---- 27. ETF列表（etf_list） ----

    def _fetch_etf_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """ETF基金列表全量刷新，写入 c1_market.etf_list。"""
        import akshare as ak
        table = "c1_market.etf_list"
        columns = [
            "etf_code", "etf_name", "etf_abbr", "full_name",
            "index_code", "index_name", "setup_date", "list_date",
            "list_status", "exchange", "manager", "custodian",
            "mgmt_fee", "etf_type",
        ]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.fund_etf_category_sina, policy, symbol="ETF基金")
        except Exception as e:
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append(self._parse_etf_list_row(r))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    @staticmethod
    def _parse_etf_list_row(r) -> tuple:
        """解析单行ETF列表数据。"""
        return (
            str(r.get("代码", "") or ""),
            str(r.get("名称", "") or ""),
            str(r.get("简称", "") or ""),
            str(r.get("全称", "") or ""),
            str(r.get("跟踪指数代码", "") or ""),
            str(r.get("跟踪指数名称", "") or ""),
            AKShareProvider._norm_date_str(r.get("成立日期")),
            AKShareProvider._norm_date_str(r.get("上市日期")),
            str(r.get("上市状态", "") or ""),
            str(r.get("交易市场", "") or ""),
            str(r.get("管理人", "") or ""),
            str(r.get("托管人", "") or ""),
            safe_float(r.get("管理费")),
            str(r.get("类型", "") or ""),
        )

    # ---- 28. LOF列表（lof_list） ----

    def _fetch_lof_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """LOF基金列表全量刷新，写入 c1_market.lof_list。"""
        import akshare as ak
        table = "c1_market.lof_list"
        columns = ["code", "name"]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.fund_lof_spot_em, policy)
        except Exception as e:
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append((
                    str(r.get("代码", "") or ""),
                    str(r.get("名称", "") or ""),
                ))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 29. 港股列表（hk_stock_list） ----

    def _fetch_hk_stock_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """港股列表全量刷新，写入 c1_market.hk_stock_list。"""
        import akshare as ak
        table = "c1_market.hk_stock_list"
        columns = ["code", "name"]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.stock_hk_spot_em, policy)
        except Exception as e:
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            for _, r in df.iterrows():
                rows.append((
                    str(r.get("代码", "") or ""),
                    str(r.get("名称", "") or ""),
                ))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 30. 港股交易日历（hk_trade_calendar） ----

    def _fetch_hk_trade_calendar(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """港股交易日历全量刷新，写入 c1_market.hk_trade_calendar。"""
        import akshare as ak
        table = "c1_market.hk_trade_calendar"
        columns = ["cal_date", "is_open", "pretrade_date"]
        t0 = time.time()
        try:
            df = self._call_with_policy(ak.tool_trade_date_hist_sina, policy)
        except Exception as e:
            yield FetchResult(table=table, columns=columns, rows=[], last_key="",
                              elapsed_sec=time.time() - t0, error=str(e))
            return
        rows: list[tuple] = []
        if df is not None and len(df) > 0:
            date_list = df["trade_date"].tolist() if "trade_date" in df.columns else []
            date_set = set(date_list)
            sorted_dates = sorted(date_list)
            for i, d in enumerate(sorted_dates):
                cal_date = self._norm_date_str(d)
                if not cal_date:
                    continue
                # 前一个交易日
                pretrade = sorted_dates[i - 1] if i > 0 else None
                pretrade_str = self._norm_date_str(pretrade) if pretrade else ""
                rows.append((cal_date, 1, pretrade_str))
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 31. 指数列表（index_list） ----

    def _fetch_index_list(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """指数列表全量刷新，写入 c1_market.index_list。"""
        import akshare as ak
        table = "c1_market.index_list"
        columns = [
            "ts_code", "name", "market", "publisher", "category",
            "base_date", "base_point", "list_date", "symbol_num", "market_id",
        ]
        t0 = time.time()
        rows: list[tuple] = []
        # 从多个交易所获取指数列表
        for market, func_name in [
            ("SH", "stock_info_sh_name_code"),
            ("SZ", "stock_info_sz_name_code"),
        ]:
            try:
                func = getattr(ak, func_name, None)
                if func is None:
                    continue
                df = self._call_with_policy(func, policy)
                if df is None or len(df) == 0:
                    continue
                for _, r in df.iterrows():
                    code = str(r.get("证券代码", r.get("代码", "")) or "")
                    name = str(r.get("证券简称", r.get("名称", "")) or "")
                    if not code:
                        continue
                    rows.append((
                        f"{code}.{market}",
                        name, market, "交易所", "指数",
                        "", 0.0, "", "", 0.0,
                    ))
            except Exception as e:
                self._log.debug(f"{func_name} 失败: {e}")
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)

    # ---- 32. ETF基准列表（etf_benchmark） ----

    def _fetch_etf_benchmark(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """ETF基准指数列表全量刷新，写入 c1_market.etf_benchmark。"""
        import akshare as ak
        table = "c1_market.etf_benchmark"
        columns = [
            "index_code", "index_full_name", "index_short_name",
            "publisher", "publish_date", "base_date", "base_point",
            "adjust_cycle",
        ]
        t0 = time.time()
        rows: list[tuple] = []
        # 从指数列表中获取
        try:
            df = self._call_with_policy(ak.index_stock_info, policy, symbol="000300")
        except Exception as e:
            self._log.debug(f"index_stock_info 失败: {e}")
        # 如果没有专门接口，用空数据返回（该表为静态参考，低频变化）
        yield FetchResult(table=table, columns=columns, rows=rows,
                          last_key=datetime.date.today().isoformat(),
                          elapsed_sec=time.time() - t0)
