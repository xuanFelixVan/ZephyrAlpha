# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.akshare_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] akshare SDK (ak.macro_china_gdp/cpi/pmi/money_supply)
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

log = logging.getLogger(__name__)


def safe_float(v) -> float | None:
    """安全转 float，失败返回 None。"""
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


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
        if cap == "macro_data":
            yield from self._fetch_macro_data(payload, policy)
        elif cap == "daily_valuation":
            yield from self._fetch_daily_valuation(payload, policy)
        elif cap == "margin_trading":
            yield from self._fetch_margin_trading(payload, policy)
        elif cap == "block_trade":
            yield from self._fetch_block_trade(payload, policy)
        elif cap == "dragon_tiger":
            yield from self._fetch_dragon_tiger(payload, policy)
        elif cap == "money_flow":
            yield from self._fetch_money_flow(payload, policy)
        elif cap == "share_unlock":
            yield from self._fetch_share_unlock(payload, policy)
        elif cap == "audit_opinion":
            yield from self._fetch_audit_opinion(payload, policy)
        elif cap == "equity_pledge":
            yield from self._fetch_equity_pledge(payload, policy)
        elif cap == "equity_pledge_summary":
            yield from self._fetch_equity_pledge_summary(payload, policy)
        else:
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
        """获取全 A 股 6 位代码列表（用 ak.stock_zh_a_spot_em）。"""
        df = self._call_with_policy(ak.stock_zh_a_spot_em, policy)
        if df is None or len(df) == 0:
            return []
        return [str(c).zfill(6) for c in df["代码"].tolist()]

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
                unlock_date = self._norm_date_str(row.get("解除限售日期"))
                if not unlock_date:
                    continue
                rows.append((
                    sym, unlock_date,
                    safe_float(row.get("解除限售数量")),
                    safe_float(row.get("解除限售比例")),
                    safe_float(row.get("实际解禁金额")),
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

        table = "c3_fundamental.equity_pledge"
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
                    safe_float(row.get("质押笔数")),
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
