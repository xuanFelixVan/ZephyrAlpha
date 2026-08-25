# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.announcement_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.news_dedup; zephyr.data.table_registry; requests/feedparser（延迟 import）
# [CONSUMERS] zephyr.data.scheduler（P1 接线：tasks.yaml announcement_news 任务）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 匿名访问；单源失败跳过不中断；写表前必经 news_dedup 去重；http_post/http_get/feed_parse 注入式（单测不触网）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 单源异常→log warning+跳过该源；不支持 capability→FetchResult(error=...)
# [TESTS] tests/zephyr/data/test_announcement_provider.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""巨潮/交易所公告采集器（CAND-DAT-013 / B10-01344，交易所公告/新闻源）。

深挖裁定=做(P1)：库内新闻读取器 news_collector 已有（MOD-DATA-NEWS-001），
rss_provider 覆盖财经媒体 RSS，但巨潮/交易所公告上游 HTTP/RSS 采集器缺口。
本模块对齐 rss_provider 的 IngestProviderBase 模式：

1. 巨潮 HTTP API：``www.cninfo.com.cn/new/hisAnnouncement/query``（POST 表单，
   epoch 毫秒时间戳 → 标准时间，adjunctUrl → static.cninfo.com.cn 全链接）。
2. 交易所 RSS：feeds 注入（默认空——具体路由待 Owner 确认后经 tasks.yaml
   extra.feeds 配置，不虚构官方路由），feedparser 解析。
3. 落库形态：``build_news_row`` 对齐 NEWS_DATA_COLUMNS 写 fund_news_data 表；
   每批必经 ``dedup_news_result``（标题 MD5，批内+已库 7 日窗口）去重。
"""

from __future__ import annotations

import datetime
import logging
import time
from typing import Callable, Iterator
from urllib.parse import urlparse

from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row, dedup_news_result
from ..provider_base import (
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024，对齐 rss_provider）
_TBL_NEWS_DATA = get_registry().table("fund_news_data")

_CNINFO_QUERY_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
_CNINFO_STATIC_PREFIX = "http://static.cninfo.com.cn/"
_CNINFO_PAGE_SIZE = 30

_CST = datetime.timezone(datetime.timedelta(hours=8))  # 公告时间口径=北京时间


class AnnouncementProvider(IngestProviderBase):
    """巨潮/交易所公告 Provider——announcement_news 能力。

    匿名访问、shared 线程安全模型。生产 HTTP 走 requests（延迟 import）；
    单测注入 http_post/http_get/feed_parse 不触网。
    """

    source_name: str = "announcement"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="announcement",
        display_name="巨潮/交易所公告",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,
        capabilities=["announcement_news"],
        known_issues=["cninfo 偶发反爬需限速", "交易所 RSS 路由待 Owner 确认配置"],
    )

    def __init__(
        self,
        http_post: Callable[..., dict] | None = None,
        http_get: Callable[[str], str] | None = None,
        feed_parse: Callable | None = None,
        feeds: tuple[str, ...] = (),
    ) -> None:
        super().__init__()
        self._http_post = http_post or self._default_http_post
        self._http_get = http_get or self._default_http_get
        self._feed_parse = feed_parse
        self._feeds = tuple(feeds)

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：匿名访问，仅验证 requests 可导入。"""
        import requests  # noqa: F401

        self._connected = True
        self._log.info("公告采集器已连接（匿名访问）")

    def health_check(self) -> bool:
        """探活：尝试 import requests。"""
        try:
            import requests  # noqa: F401

            return True
        except ImportError as e:
            self._log.warning(f"公告采集器探活失败（requests 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：重置状态。"""
        self._connected = False
        self._log.info("公告采集器已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由。"""
        capability = (payload.extra or {}).get("capability")
        if capability != "announcement_news":
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )
            return
        yield from self._fetch_announcements(payload, policy)

    # ---- 公告采集 ----

    def _fetch_announcements(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """巨潮 HTTP + 交易所 RSS 合并一批，经 news_dedup 去重后 yield。"""
        t0 = time.time()
        table = payload.table or _TBL_NEWS_DATA
        rows: list[tuple] = []
        rows.extend(self._fetch_cninfo(payload, policy))
        rows.extend(self._fetch_exchange_rss())
        if not rows:
            return
        result = FetchResult(
            table=table,
            columns=NEWS_DATA_COLUMNS,
            rows=rows,
            last_key=datetime.date.today().isoformat(),
            elapsed_sec=time.time() - t0,
        )
        # 走 news_dedup 去重（标题 MD5：批内重复 + 已库 7 日窗口；fail-open）
        yield dedup_news_result(result)

    def _fetch_cninfo(self, payload: FetchPayload, policy) -> list[tuple]:
        """巨潮 HTTP API → 标准新闻行。"""
        form = {
            "pageNum": 1,
            "pageSize": _CNINFO_PAGE_SIZE,
            "column": "sse,szse",
            "tabName": "fulltext",
            "seDate": f"{payload.start}~{payload.end}",
            "isHLtitle": "true",
        }
        try:
            if policy is not None:
                js = self._call_with_policy(self._http_post, policy, _CNINFO_QUERY_URL, data=form)
            else:
                js = self._http_post(_CNINFO_QUERY_URL, data=form)
        except Exception as e:  # noqa: BLE001 — 单源失败不中断（对齐 rss_provider 口径）
            self._log.warning(f"巨潮公告获取失败，跳过该源: {e}")
            return []
        rows: list[tuple] = []
        for ann in (js or {}).get("announcements") or []:
            title = ann.get("announcementTitle", "")
            if not title:
                continue
            ts_ms = ann.get("announcementTime")
            pub = (
                datetime.datetime.fromtimestamp(ts_ms / 1000, tz=_CST).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if ts_ms
                else ""
            )
            adjunct = ann.get("adjunctUrl", "")
            link = f"{_CNINFO_STATIC_PREFIX}{adjunct}" if adjunct else _CNINFO_QUERY_URL
            sec = ann.get("secName") or ann.get("secCode") or ""
            summary = f"{sec} 公告" if sec else "交易所公告"
            rows.append(
                build_news_row(pub, title, link, summary, "cninfo", self.source_name)
            )
        self._log.info(f"巨潮公告: {len(rows)} 行")
        return rows

    def _fetch_exchange_rss(self) -> list[tuple]:
        """交易所公告 RSS（feeds 注入，默认空——路由待 Owner 确认配置）。"""
        if not self._feeds:
            return []
        parse = self._feed_parse
        if parse is None:
            import feedparser

            parse = feedparser.parse
        rows: list[tuple] = []
        for feed_url in self._feeds:
            try:
                parsed = parse(self._http_get(feed_url))
                source = urlparse(feed_url).netloc or "exchange"
                for entry in parsed.entries:
                    pub_date = entry.get("published", entry.get("updated", ""))
                    title = entry.get("title", "")
                    if not title:
                        continue
                    rows.append(
                        build_news_row(
                            pub_date,
                            title,
                            entry.get("link", ""),
                            entry.get("summary", entry.get("description", "")),
                            source,
                            self.source_name,
                        )
                    )
            except Exception as e:  # noqa: BLE001
                self._log.warning(f"交易所 RSS {feed_url} 获取失败，跳过: {e}")
        return rows

    # ---- 生产默认 HTTP（单测注入替代） ----

    @staticmethod
    def _default_http_post(url: str, data: dict | None = None) -> dict:
        import requests

        resp = requests.post(url, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _default_http_get(url: str) -> str:
        import requests

        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content
