# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.eastmoney_news_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (HTTP直连东方财富7x24快讯API)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 匿名访问；HTTP直连无需登录；7x24小时财经快讯
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestEastmoneyNewsProvider
# [A_module] module_id=MOD-L00-004-eastmoney_news_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""东方财富新闻数据源 Provider 实现（MOD-L00-004 §4.3）。

HTTP直连东方财富7x24快讯API，继承DataSourceBase。
- 匿名访问，无需登录
- 7x24小时财经快讯
- 当前能力：news_data（东方财富快讯）

数据转换目标表 c3_fundamental.news_data：
    pub_date, title, link, summary, source
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
from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row

log = logging.getLogger(__name__)

# 东方财富7x24快讯API
_EM_NEWS_URL = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
_EM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://kuaixun.eastmoney.com/",
}


class EastmoneyNewsProvider(DataSourceBase):
    """东方财富新闻数据源 Provider。

    匿名访问、shared 线程安全模型。
    已知问题：无认证，高频请求可能被限制。
    """

    source_name: str = "eastmoney_news"
    meta: DataSourceMeta = DataSourceMeta(
        name="eastmoney_news",
        display_name="东方财富新闻",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=30,
        capabilities=["news_data"],
        known_issues=["无认证", "高频请求可能被限制"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：验证 requests 可导入。"""
        import requests  # noqa: F401
        self._connected = True
        self._log.info("东方财富新闻 已连接（匿名访问）")

    def health_check(self) -> bool:
        """探活：尝试 import requests。"""
        try:
            import requests  # noqa: F401
            return True
        except ImportError as e:
            self._log.warning(f"东方财富新闻探活失败（requests 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：重置状态。"""
        self._connected = False
        self._log.info("东方财富新闻 已断开")

    # ---- 拉取入口 ----

    def fetch(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        cap = (payload.extra or {}).get("capability")
        if cap == "news_data":
            yield from self._fetch_news_data(payload, policy)
        else:
            yield FetchResult(
                table=payload.table, columns=[], rows=[],
                last_key="", elapsed_sec=0.0,
                error=f"unsupported capability: {cap}",
            )

    # ---- 东方财富7x24快讯 ----

    def _fetch_news_data(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取东方财富7x24快讯，写入 c3_fundamental.news_data。

        HTTP直连 https://np-listapi.eastmoney.com/comm/web/getNewsByColumns。
        支持分页：通过 payload.extra["page_size"] 控制每批数量（默认50）。
        """
        import requests

        table = payload.table or "c3_fundamental.news_data"
        columns = NEWS_DATA_COLUMNS
        page_size = (payload.extra or {}).get("page_size", 50)
        t0 = time.time()

        try:
            params = {
                "client": "web",
                "biz": "web_724",
                "column": "350",
                "order": "1",
                "needInteractData": "0",
                "page_index": "1",
                "page_size": str(page_size),
                "req_trace": str(int(time.time() * 1000)),
            }
            resp = self._call_with_policy(
                requests.get, policy,
                _EM_NEWS_URL, params=params, headers=_EM_HEADERS, timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            news_list = (data.get("data") or {}).get("list") or []
            rows = self._parse_em_news(news_list)
        except Exception as e:
            self._log.warning(f"东方财富新闻获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        self._log.info(f"东方财富新闻: {len(rows)} 行")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_em_news(news_list: list) -> list[tuple]:
        """解析东方财富新闻列表为 news_data 表标准行。

        实测字段名：title, showTime, uniqueUrl, summary, mediaName, url。
        兼容 Art_Title 等旧格式。
        """
        rows: list[tuple] = []
        for item in news_list:
            title = str(
                item.get("title")
                or item.get("Art_Title")
                or item.get("Title")
                or ""
            )
            pub_date = str(
                item.get("showTime")
                or item.get("Art_ShowTime")
                or item.get("ShowTime")
                or item.get("ptime")
                or ""
            )
            link = str(
                item.get("uniqueUrl")
                or item.get("url")
                or item.get("Art_UniqueUrl")
                or ""
            )
            summary = str(
                item.get("summary")
                or item.get("digest")
                or item.get("Art_Summary")
                or ""
            )
            rows.append(build_news_row(
                pub_date, title, link, summary, "eastmoney", "eastmoney_news",
            ))
        return rows
