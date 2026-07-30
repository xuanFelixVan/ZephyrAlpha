# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.rss_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] feedparser SDK (feedparser.parse) + requests
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 匿名访问；偶发SSL错误需重试；须尊重robots.txt；财经新闻爬虫
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 异常->yield FetchResult(error=str)
# [TESTS] tests/zephyr/data/test_providers.py::TestRSSProvider
# [A_module] module_id=MOD-GOV-rss_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RSS 财经新闻数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 feedparser + requests，继承 IngestProviderBase。
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
    IngestProviderBase,
    IngestProviderMeta,
    FetchPayload,
    FetchResult,
)
from ..policy_registry import SourcePolicy
from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# ============== Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）==============
_TBL_NEWS_DATA = get_registry().table("fund_news_data")


# 默认财经 RSS 源（国内源 + 海外源）
# 国内源：直连 RSS + 本地 RSSHub 路由（V2rayN 规则模式国内域名直连，不走代理）
# 海外源：Yahoo Finance 经 RSSHub 代理走 V2rayN SOCKS5(10808)；Investing.com 直连可达
# 依赖本地 RSSHub 实例（D:\RSSHub，pm2 守护，监听 localhost:1200，ecosystem.config.cjs 配 PROXY_URI）
from zephyr.shared.foundation.constants import DEFAULT_RSSHUB_URL
_DEFAULT_RSS_FEEDS = [
    # ---- 国内源：直连 RSS ----
    "https://36kr.com/feed",                              # 36氪（直连）
    "https://www.tmtpost.com/feed",                       # 钛媒体（直连）
    # ---- 国内源：本地 RSSHub 路由 ----
    f"{DEFAULT_RSSHUB_URL}/wallstreetcn/news",            # 华尔街见闻
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/strategyreport",  # 东方财富-策略报告
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/macresearch",     # 东方财富-宏观研究
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/brokerreport",    # 东方财富-券商晨报
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/industry",        # 东方财富-行业研报
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/stock",           # 东方财富-个股研报
    f"{DEFAULT_RSSHUB_URL}/yicai/news",                   # 第一财经
    f"{DEFAULT_RSSHUB_URL}/caixin/latest",                # 财新网
    f"{DEFAULT_RSSHUB_URL}/36kr/newsflashes",             # 36氪快讯
    f"{DEFAULT_RSSHUB_URL}/jin10/index",                  # 金十数据
    # ---- 海外源：Yahoo Finance（RSSHub 路由，出站走 SOCKS5 代理）----
    # 路由 /yahoo/news/:region/:category，财经类 category：hk=business / tw=finance / us=business
    f"{DEFAULT_RSSHUB_URL}/yahoo/news/us/business",       # Yahoo Finance 美国-商业（英文，全球财经）
    f"{DEFAULT_RSSHUB_URL}/yahoo/news/hk/business",       # Yahoo 財經 香港（中文，港股/全球）
    f"{DEFAULT_RSSHUB_URL}/yahoo/news/tw/finance",        # Yahoo 財經 台湾（中文，台股/全球）
    # ---- 海外源：Investing.com 直连 RSS（bot UA 可访问，robots.txt 403 fail-open）----
    "https://www.investing.com/rss/news_1.rss",           # Investing.com 头条
    "https://www.investing.com/rss/news_25.rss",          # Investing.com 股市新闻
]


class RSSProvider(IngestProviderBase):
    """RSS 财经新闻数据源 Provider。

    匿名访问、shared 线程安全模型。
    已知问题：偶发 SSL 错误；须尊重 robots.txt。
    """

    source_name: str = "rss"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="rss",
        display_name="RSS 财经新闻",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,
        capabilities=["news_data"],
        known_issues=["偶发SSL错误", "须尊重robots.txt", r"依赖本地RSSHub实例(D:\RSSHub)"],
    )

    # robots.txt 缓存（per-domain）
    _robots_cache: dict[str, RobotFileParser | None] = {}
    robots_cache: dict[str, RobotFileParser | None] = _robots_cache  # public alias（Stage 4 公共化）

    def is_allowed(self, url: str) -> bool:
        """公共接口（R5 公共化）：robots.txt 是否允许抓取该 URL。委托 _is_allowed。"""
        return self._is_allowed(url)


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

        table = payload.table or _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
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
                    rows.append(build_news_row(
                        pub_date, title, link, summary, source_name, "rss",
                    ))

                self._log.info(f"RSS {source_name}: {len(rows)} 行")
                if rows:
                    yield FetchResult(
                        table=table, columns=columns, rows=rows,
                        last_key=datetime.date.today().isoformat(),
                        elapsed_sec=time.time() - t0,
                    )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 单源失败不中断整个任务：scheduler._fetch_and_write 遇 FetchResult.error 会 break，
                # 若此处 yield error 会导致后续 feed（含海外源）永不被抓取（如 domestic 源 503 时
                # 海外 Yahoo/Investing.com 排在其后会被跳过）。仅记录告警并跳过该源，继续抓取后续 feed。
                # 失败可见性由本 warning 日志保证；全部源均 0 行时 scheduler 会发 "SUCCESS 但 0 行写入" 告警。
                self._log.warning(f"RSS {feed_url} 获取失败，跳过该源继续后续 feed: {e}")

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
                # RobotFileParser 对 401/403 不抛异常，而是内部置 disallow_all=True
                # （CPython urllib.robotparser.read 行为）。站点拒绝公开 robots.txt
                # （如 Cloudflare 默认 403）时，按 fail-open 处理——无法读取规则即不强制，
                # 而非误判为"全站禁止"。显式 Disallow: / 走 parse() 仍会被正常尊重。
                if rp.disallow_all:
                    self._log.debug(f"robots.txt 不可读(401/403) {domain}，默认允许")
                    self._robots_cache[domain] = None
                else:
                    self._robots_cache[domain] = rp
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                # robots.txt 读取失败 -> 默认允许（fail-open）
                self._log.debug(f"robots.txt 读取失败 {domain}: {e}，默认允许")
                self._robots_cache[domain] = None

        rp = self._robots_cache[domain]
        if rp is None:
            return True  # fail-open
        return rp.can_fetch("ZephyrAlpha-DataBot", url)
