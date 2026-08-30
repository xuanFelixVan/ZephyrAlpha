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
"""
RSS 财经新闻数据源 Provider 实现（MOD-L00-004 §4.3）。

封装 feedparser + requests，继承 IngestProviderBase。
- 匿名访问，无需登录
- 偶发 SSL 错误需重试（policy.retry_on=["SSLError", ...]）
- 须尊重 robots.txt（policy.respect_robots_txt=True 时先查 robots.txt）
- 当前能力：news_data（财经新闻）

关键设计：
- connect() 仅验证 feedparser 可导入
- fetch() 用 requests.get 拉取 RSS XML，feedparser.parse 解析
- respect_robots_txt=True 时先检查 robots.txt 是否允许抓取

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: rss_provider.py
# 层: 算法
# - id: A1
#   name_zh: ① RSSProvider
#   name_en: RSSProvider
#   intro: RSS 财经新闻数据源 Provider。
#   desc: RSS 财经新闻数据源 Provider。 匿名访问、shared 线程安全模型。 已知问题：偶发 SSL 错误；须尊重 robots.txt。；公共方法（定义序）: is_allowed, connect, heal…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RSSProvider
#   downstream: zephyr.data.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import socket
import time
from typing import Iterator
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from ..news_dedup import NEWS_DATA_COLUMNS, build_news_row
from ..policy_registry import SourcePolicy
from ..provider_base import (
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from ..table_registry import get_registry

log = logging.getLogger(__name__)

# ============== Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）==============
_TBL_NEWS_DATA = get_registry().table("fund_news_data")


# 默认财经 RSS 源（国内源 + 海外源）
# 国内源：直连 RSS + 本地 RSSHub 路由（V2rayN 规则模式国内域名直连，不走代理）
# 海外源：国际主流财经媒体原生 RSS 直连，走 V2rayN SOCKS5(10808) 代理
# 依赖本地 RSSHub 实例（D:\RSSHub，pm2 守护，监听 localhost:1200，ecosystem.config.cjs 配 PROXY_URI）
from zephyr.shared.foundation.constants import DEFAULT_HTTP_UA, DEFAULT_RSSHUB_URL

_DEFAULT_RSS_FEEDS = [
    # ---- 国内源：直连 RSS ----
    "https://36kr.com/feed",  # 36氪（直连）
    "https://www.tmtpost.com/feed",  # 钛媒体（直连）
    # ---- 国内源：本地 RSSHub 路由 ----
    f"{DEFAULT_RSSHUB_URL}/wallstreetcn/news",  # 华尔街见闻
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/strategyreport",  # 东方财富-策略报告
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/macresearch",  # 东方财富-宏观研究
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/brokerreport",  # 东方财富-券商晨报
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/industry",  # 东方财富-行业研报
    f"{DEFAULT_RSSHUB_URL}/eastmoney/report/stock",  # 东方财富-个股研报
    f"{DEFAULT_RSSHUB_URL}/yicai/news",  # 第一财经
    f"{DEFAULT_RSSHUB_URL}/caixin/latest",  # 财新网
    f"{DEFAULT_RSSHUB_URL}/36kr/newsflashes",  # 36氪快讯
    f"{DEFAULT_RSSHUB_URL}/jin10/index",  # 金十数据
    # 注：Yahoo Finance RSSHub 路由已移除（#ARCH-RSS-001，2026-08-09）——
    # Yahoo 对 RSSHub 请求返回 403（美国版反爬）+ 香港/台湾版连接超时，
    # V2rayN 节点直连 Yahoo Finance 正常（HTTP 200），确认是 RSSHub 路由被反爬盯死。
    # 海外新闻由下方 5 个直连源（BBC/CNBC/NYT/Guardian/Bloomberg）覆盖，无需 Yahoo。
    # 注：Investing.com 直连源已移除（#ARCH-RSS-INVESTING-403-001）——bot UA 触发 WAF 间歇 403，
    # 内容与 Yahoo Finance 重叠。
    # ---- 海外源：直连 RSS（#ARCH-EDB-EXPAND，2026-08-04）----
    # 国际主流财经媒体原生 RSS，直连（非 RSSHub 中转），走 V2rayN SOCKS5 代理。
    # 无 RSSHub 单点依赖，内容权威（BBC/CNBC/NYT/Guardian/Bloomberg）。
    # 注：Reuters RSS 已移除（#ARCH-RSS-REUTERS-404-001）——reutersagency.com/feed 返回 404，
    # Reuters 2020 年后大幅削减 RSS 支持，URL 不稳定。
    "https://feeds.bbci.co.uk/news/business/rss.xml",  # BBC Business（英国，英文）
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",  # CNBC Business（美国，英文）
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",  # NYT Business（美国，英文）
    "https://www.theguardian.com/business/rss",  # Guardian Business（英国，英文）
    "https://feeds.bloomberg.com/markets/news.rss",  # Bloomberg Markets（美国，英文）
]

# 海外直连 RSS 域名 → (region, language) 映射（#ARCH-EDB-EXPAND）
# _extract_region_language 按域名查此表；国内源默认 (CN, zh)。
_OVERSEAS_DIRECT_REGION_MAP: dict[str, tuple[str, str]] = {
    "feeds.bbci.co.uk": ("UK", "en"),
    "www.cnbc.com": ("US", "en"),
    "rss.nytimes.com": ("US", "en"),
    "www.theguardian.com": ("UK", "en"),
    "feeds.bloomberg.com": ("US", "en"),
}

# 海外源 URL 特征——海外直连域名。
# VPN 关闭时（SOCKS5 10808 未监听）跳过所有海外源，国内源正常拉取。
# 新增海外源时需同步更新此列表。
_OVERSEAS_FEED_PATTERNS = (
    "feeds.bbci.co.uk",
    "www.cnbc.com",
    "rss.nytimes.com",
    "www.theguardian.com",
    "feeds.bloomberg.com",
)

# 海外直连域名（需 requests 走 SOCKS5 代理）
# _http_get 重写时按此列表判断是否注入 proxies。
_OVERSEAS_DIRECT_DOMAINS = tuple(_OVERSEAS_DIRECT_REGION_MAP.keys())

# V2rayN SOCKS5 代理监听端口（RSSHub PROXY_URI 指向此端口）
_VPN_SOCKS5_PORT = 10808


def _is_vpn_ready(port: int = _VPN_SOCKS5_PORT, timeout: float = 1.0) -> bool:
    """探测 V2rayN SOCKS5 代理端口是否在监听（VPN 开关状态）。

    海外新闻源（BBC/CNBC/NYT/Guardian/Bloomberg）依赖 VPN 走 SOCKS5 代理。
    VPN 关闭时 SOCKS5 端口不监听，本函数快速返回 False（1s 超时），
    避免海外源请求超时拖慢整轮 RSS 拉取。

    Returns: True 如果 VPN 开启（端口监听中），False 如果 VPN 关闭。
    """
    # 资源泄漏治本：OSError 失败路径原实现不 close socket——VPN 关闭时每次探测
    # 泄漏一个 socket，GC 时触发 PytestUnraisableExceptionWarning（测试结果随
    # VPN 开关状态翻转）。with 语境保证任意路径关闭。
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _is_overseas_feed(feed_url: str) -> bool:
    """判断 feed 是否为海外源（依赖 VPN/SOCKS5 代理）。"""
    return any(p in feed_url for p in _OVERSEAS_FEED_PATTERNS)


# #ARCH-RSS-INVESTING-403-001：海外新闻显式标记 region/language，避免被表 DEFAULT 误标 CN/zh


def _extract_region_language(feed_url: str) -> tuple[str, str]:
    """从 feed URL 提取 (region, language) 标记。

    海外直连源按域名查 _OVERSEAS_DIRECT_REGION_MAP；
    国内源（直连 + 本地 RSSHub 国内路由）默认 (CN, zh)。
    """
    # 海外直连源（#ARCH-EDB-EXPAND）：按域名查 _OVERSEAS_DIRECT_REGION_MAP
    host = urlparse(feed_url).netloc.lower()
    if host in _OVERSEAS_DIRECT_REGION_MAP:
        return _OVERSEAS_DIRECT_REGION_MAP[host]
    return ("CN", "zh")


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

    def _http_get(
        self,
        url: str,
        timeout: float = 30,
        headers: dict | None = None,
        params: dict | None = None,
    ):
        """HTTP GET + raise_for_status（重写基类，#ARCH-EDB-EXPAND 海外直连源走 SOCKS5）。

        海外直连源（BBC/CNBC/NYT/Guardian/Bloomberg）需 V2rayN SOCKS5 代理；
        国内源 + 本地 RSSHub 路由（localhost:1200）不走代理（RSSHub 内部处理代理）。
        VPN 关闭时海外源已在 _fetch_news_data 循环外跳过，此处不重复探测。
        """
        import requests

        proxies = None
        host = urlparse(url).netloc.lower()
        if host in _OVERSEAS_DIRECT_DOMAINS:
            proxies = {
                "https": f"socks5h://127.0.0.1:{_VPN_SOCKS5_PORT}",
                "http": f"socks5h://127.0.0.1:{_VPN_SOCKS5_PORT}",
            }
        resp = requests.get(
            url,
            timeout=timeout,
            headers=headers or {},
            params=params,
            proxies=proxies,
        )
        resp.raise_for_status()
        return resp

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

    def fetch(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """按 payload.extra["capability"] 路由到具体获取方法。"""
        capability = (payload.extra or {}).get("capability")
        if capability == "news_data":
            yield from self._fetch_news_data(payload, policy)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- 财经新闻 ----

    def _fetch_news_data(self, payload: FetchPayload, policy: SourcePolicy) -> Iterator[FetchResult]:
        """获取财经新闻（feedparser.parse）。

        每个 RSS 源作为一批 yield FetchResult。
        用 self._http_get 拉取 XML 并校验状态码（含 raise_for_status，纳入重试循环：
        5xx 重试、4xx 不重试），feedparser.parse 解析。
        """
        import feedparser

        table = payload.table or _TBL_NEWS_DATA
        columns = NEWS_DATA_COLUMNS
        feeds = payload.symbols or _DEFAULT_RSS_FEEDS
        respect_robots = policy.respect_robots_txt if policy else True

        # 海外源 VPN 状态探测（治本 2026-07-31）：
        # 海外直连源（BBC/CNBC/NYT/Guardian/Bloomberg）依赖 V2rayN SOCKS5(10808)。
        # VPN 关闭时若仍请求海外源，连接会超时，串行拖慢整轮（含国内源）。
        # 探测一次缓存结果：VPN 关→跳过海外源（快速失败），国内源正常；VPN 开→正常拉取。
        # 下一轮（≤3min）重新探测，VPN 开了自动恢复海外源——实现"海外源与 VPN 开关绑定"。
        vpn_ready = _is_vpn_ready()
        if not vpn_ready:
            overseas_count = sum(1 for f in feeds if _is_overseas_feed(f))
            if overseas_count:
                self._log.info(
                    f"VPN 未开启（SOCKS5 {_VPN_SOCKS5_PORT} 未监听），"
                    f"跳过 {overseas_count} 个海外新闻源；国内源正常拉取"
                )

        for feed_url in feeds:
            if _is_overseas_feed(feed_url) and not vpn_ready:
                continue  # VPN 关闭，跳过海外源（已在循环外统一告警）
            t0 = time.time()
            try:
                # 检查 robots.txt
                if respect_robots and not self._is_allowed(feed_url):
                    self._log.info(f"RSS {feed_url} 被 robots.txt 禁止，跳过")
                    continue

                # 用 _call_with_policy 包裹 self._http_get（含 raise_for_status）
                # #ARCH-RSS-INVESTING-403-001：raise_for_status 纳入重试循环——
                # 5xx 匹配 retry_on 重试；4xx（WAF 403）不匹配 → 立即抛出不重试
                response = self._call_with_policy(
                    self._http_get,
                    policy,
                    feed_url,
                    timeout=30,
                    headers={"User-Agent": DEFAULT_HTTP_UA},
                )

                # feedparser 解析 XML
                parsed = feedparser.parse(response.content)
                rows: list[tuple] = []
                source_name = self._extract_source_name(feed_url)
                region, language = _extract_region_language(feed_url)
                for entry in parsed.entries:
                    pub_date = entry.get("published", entry.get("updated", ""))
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    rows.append(
                        build_news_row(
                            pub_date,
                            title,
                            link,
                            summary,
                            source_name,
                            "rss",
                            region=region,
                            language=language,
                        )
                    )

                self._log.info(f"RSS {source_name}: {len(rows)} 行")
                if rows:
                    yield FetchResult(
                        table=table,
                        columns=columns,
                        rows=rows,
                        last_key=datetime.date.today().isoformat(),
                        elapsed_sec=time.time() - t0,
                    )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                # 单源失败不中断整个任务：scheduler._fetch_and_write 遇 FetchResult.error 会 break，
                # 若此处 yield error 会导致后续 feed（含海外源）永不被抓取（如 domestic 源 503 时
                # 海外源排在其后会被跳过）。仅记录告警并跳过该源，继续抓取后续 feed。
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
