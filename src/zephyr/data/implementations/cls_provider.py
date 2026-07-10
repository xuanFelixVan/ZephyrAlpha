# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.cls_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] requests (HTTP直连财联社电报API)
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 匿名访问；通过RSSHub获取（财联社直连API需sign加密）；分钟级财经快讯
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestClsProvider
# [A_module] module_id=MOD-L00-004-cls_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""财联社电报数据源 Provider 实现（MOD-L00-004 §4.3）。

通过RSSHub公共实例获取财联社电报，继承DataSourceBase。
- 匿名访问，无需登录
- 财联社直连API需要sign加密，改用RSSHub路由
- 分钟级财经快讯
- 当前能力：news_data（财联社电报）

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

log = logging.getLogger(__name__)

# 财联社电报（通过本地 RSSHub 实例，财联社直连API需sign加密）
# 部署：D:\RSSHub，npm start，监听 localhost:1200
from zephyr.shared.foundation.constants import DEFAULT_RSSHUB_URL
_CLS_RSSHUB_URL = f"{DEFAULT_RSSHUB_URL}/cls/telegraph"
_CLS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


class ClsProvider(DataSourceBase):
    """财联社电报数据源 Provider。

    匿名访问、shared 线程安全模型。
    已知问题：无认证，高频请求可能被限制。
    """

    source_name: str = "cls"
    meta: DataSourceMeta = DataSourceMeta(
        name="cls",
        display_name="财联社电报",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=30,
        capabilities=["news_data"],
        known_issues=["无认证", "高频请求可能被限制", "依赖本地RSSHub实例(D:\RSSHub)"],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：验证 requests 可导入。"""
        import requests  # noqa: F401
        self._connected = True
        self._log.info("财联社电报 已连接（匿名访问）")

    def health_check(self) -> bool:
        """探活：尝试 import requests。"""
        try:
            import requests  # noqa: F401
            return True
        except ImportError as e:
            self._log.warning(f"财联社探活失败（requests 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：重置状态。"""
        self._connected = False
        self._log.info("财联社电报 已断开")

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

    # ---- 财联社电报 ----

    def _fetch_news_data(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取财联社电报，写入 c3_fundamental.news_data。

        通过RSSHub公共实例 https://rsshub.app/cls/telegraph 获取（JSON格式）。
        RSSHub返回 {items: [{title, pubDate, link, description, ...}]}。
        """
        import requests

        table = payload.table or "c3_fundamental.news_data"
        columns = ["pub_date", "title", "link", "summary", "source"]
        t0 = time.time()

        try:
            params = {"format": "json"}
            resp = self._call_with_policy(
                requests.get, policy,
                _CLS_RSSHUB_URL, params=params, headers=_CLS_HEADERS, timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items") or []
            rows = self._parse_cls_news(items)
        except Exception as e:
            self._log.warning(f"财联社电报获取失败: {e}")
            yield FetchResult(
                table=table, columns=columns, rows=[], last_key="",
                elapsed_sec=time.time() - t0, error=str(e),
            )
            return

        self._log.info(f"财联社电报: {len(rows)} 行")
        yield FetchResult(
            table=table, columns=columns, rows=rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )

    @staticmethod
    def _parse_cls_news(items: list) -> list[tuple]:
        """解析RSSHub财联社电报条目为统一格式行 (pub_date, title, link, summary, source)。

        本地 RSSHub 返回 JSON Feed 格式：
        - date_published (ISO8601) / pubDate
        - title
        - url / id / link
        - summary / content_html / description
        """
        rows: list[tuple] = []
        for item in items:
            pub_date = str(
                item.get("date_published")
                or item.get("pubDate")
                or item.get("published")
                or ""
            )
            title = str(item.get("title") or "")
            link = str(item.get("url") or item.get("id") or item.get("link") or "")
            summary = str(
                item.get("summary")
                or item.get("content_html")
                or item.get("description")
                or ""
            )
            rows.append((pub_date, title, link, summary, "cls"))
        return rows
