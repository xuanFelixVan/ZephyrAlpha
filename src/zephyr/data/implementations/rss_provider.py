# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.rss_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] feedparser SDK (feedparser.parse) + requests
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 匿名访问；偶发SSL错误需重试；须尊重robots.txt；财经新闻爬虫
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestRSSProvider
# [A_module] module_id=MOD-L00-004-rss_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RSS 财经新闻数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 feedparser + requests，继承 DataSourceBase。
- 匿名访问，无需登录
- 偶发 SSL 错误需重试（policy.retry_on=["SSLError", ...]）
- 须尊重 robots.txt（policy.respect_robots_txt=True 时先查 robots.txt）
- 当前能力：news_data（财经新闻）

关键设计：
- connect() 仅验证 feedparser 可导入
- fetch() 用 requests.get 拉取 RSS XML，feedparser.parse 解析
- respect_robots_txt=True 时先检查 robots.txt 是否允许抓取
"""
from __future__ import annotations

import datetime
import logging
import time
from typing import Iterator
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from ..provider_base import (
    DataSourceBase,
    DataSourceMeta,
    FetchPayload,
    FetchResult,
)
from ..policy_registry import SourcePolicy

log = logging.getLogger(__name__)


# 默认财经 RSS 源（国内可访问 + 本地 RSSHub 路由）
# 依赖本地 RSSHub 实例（D:\RSSHub，pm2 守护，监听 localhost:1200）
from zephyr.shared.foundation.constants import DEFAULT_RSSHUB_URL
_DEFAULT_RSS_FEEDS = [
    "https://36kr.com/feed",                              # 36氪（直连）
    "https://www.tmtpost.com/feed",                       # 钛媒体（直连）
    f"{DEFAULT_RSSHUB_URL}/wallstreetcn/news",            # 华尔街见闻（本地RSSHub）
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/strategyreport",  # 东方财富-策略报告（本地RSSHub）
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/macresearch",     # 东方财富-宏观研究（本地RSSHub）
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/brokerreport",    # 东方财富-券商晨报（本地RSSHub）
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/industry",        # 东方财富-行业研报（本地RSSHub）
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/stock",           # 东方财富-个股研报（本地RSSHub）
]


class RSSProvider(DataSourceBase):
    """RSS 财经新闻数据源 Provider。

    匿名访问、shared 线程安全模型。
    已知问题：偶发 SSL 错误；须尊重 robots.txt。
    """

    source_name: str = "rss"
    meta: DataSourceMeta = DataSourceMeta(
        name="rss",
        display_name="RSS 财经新闻",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,
        capabilities=["news_data"],
        known_issues=["偶发SSL错误", "须尊重robots.txt", "依赖本地RSSHub实例(D:\RSSHub)"],
    )

    # robots.txt 缓存（per-domain）
    _robots_cache: dict[str, RobotFileParser | None] = {}

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：验证 feedparser 可导入。"""
        import feedparser  # noqa: F401
        self._connected = True
        self._log.info("RSS 已连接（匿名访问）")

    def health_check(self) -> bool:
        """探活：尝试 import feedparser。"""
        try:
            import feedparser  # noqa: F401
            return True
        except ImportError as e:
            self._log.warning(f"RSS 探活失败（feedparser 未安装）: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接：重置状态。"""
        self._connected = False
        self._log.info("RSS 已断开")

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

    # ---- 财经新闻 ----

    def _fetch_news_data(
        self, payload: FetchPayload, policy: SourcePolicy
    ) -> Iterator[FetchResult]:
        """获取财经新闻（feedparser.parse）。

        每个 RSS 源作为一批 yield FetchResult。
        用 requests.get 拉取 XML（支持 SSL 重试），feedparser.parse 解析。
        """
        import feedparser
        import requests

        table = payload.table or "c3_fundamental.news_data"
        columns = ["pub_date", "title", "link", "summary", "source"]
        feeds = payload.symbols or _DEFAULT_RSS_FEEDS
        respect_robots = policy.respect_robots_txt if policy else True

        for feed_url in feeds:
            t0 = time.time()
            try:
                # 检查 robots.txt
                if respect_robots and not self._is_allowed(feed_url):
                    self._log.info(f"RSS {feed_url} 被 robots.txt 禁止，跳过")
                    continue

                # 用 _call_with_policy 包裹 requests.get（支持 SSL 重试）
                response = self._call_with_policy(
                    requests.get,
                    policy,
                    feed_url,
                    timeout=30,
                    headers={"User-Agent": "ZephyrAlpha-DataBot/1.0"},
                )
                response.raise_for_status()

                # feedparser 解析 XML
                parsed = feedparser.parse(response.content)
                rows: list[tuple] = []
                source_name = self._extract_source_name(feed_url)
                for entry in parsed.entries:
                    pub_date = entry.get("published", entry.get("updated", ""))
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    rows.append((pub_date, title, link, summary, source_name))

                self._log.info(f"RSS {source_name}: {len(rows)} 行")
                if rows:
                    yield FetchResult(
                        table=table, columns=columns, rows=rows,
                        last_key=datetime.date.today().isoformat(),
                        elapsed_sec=time.time() - t0,
                    )
            except Exception as e:
                self._log.warning(f"RSS {feed_url} 获取失败: {e}")
                yield FetchResult(
                    table=table, columns=columns, rows=[],
                    last_key="", elapsed_sec=time.time() - t0, error=str(e),
                )

    # ---- source_name 提取 ----

    @staticmethod
    def _extract_source_name(feed_url: str) -> str:
        """从 feed URL 提取可区分的 source 标识。

        - 直连 RSS（36kr/tmtpost）：用 netloc（如 36kr.com）
        - 本地 RSSHub 路由（localhost:1200）：用路径段（如 eastmoney/report/industry）
        """
        parsed = urlparse(feed_url)
        host = parsed.netloc.lower()
        if host.startswith("localhost") or host.startswith("127.0.0.1"):
            path = parsed.path.strip("/")
            return path if path else host
        return host

    # ---- robots.txt 检查 ----

    def _is_allowed(self, url: str) -> bool:
        """检查 robots.txt 是否允许抓取该 URL。

        缓存 per-domain 的 RobotFileParser。
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self._robots_cache:
            rp = RobotFileParser()
            rp.set_url(f"{domain}/robots.txt")
            try:
                rp.read()
                self._robots_cache[domain] = rp
            except Exception as e:
                # robots.txt 读取失败 -> 默认允许（fail-open）
                self._log.debug(f"robots.txt 读取失败 {domain}: {e}，默认允许")
                self._robots_cache[domain] = None

        rp = self._robots_cache[domain]
        if rp is None:
            return True  # fail-open
        return rp.can_fetch("ZephyrAlpha-DataBot", url)
