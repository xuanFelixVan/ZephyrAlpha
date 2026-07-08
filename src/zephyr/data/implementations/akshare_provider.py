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
        capabilities=["macro_data", "dividend", "restricted_shares", "equity_pledge"],
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
