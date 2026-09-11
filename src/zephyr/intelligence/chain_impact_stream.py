# [BLUEPRINT] MOD-INT_IMPACT_STREAM | 待统筹登记（蓝图未建，真源=docs/_working/2026-09-09-news-industry-wiring-directive.md W5 行 + §3 入图交接协议）
# [MODULE] zephyr.intelligence.chain_impact_stream
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.data.ch_reader（分钟窗新闻读取，fail-open 降级）; zephyr.data.table_registry（表名解析）; zephyr.intelligence.news_chain_node_linker（W3）; zephyr.intelligence.chain_impact_resolver（W4）; zephyr.intelligence.news_sentiment_analyzer（RuleBasedSentimentScorer=L1-S0-1 情绪上游）; zephyr.regime.features.regime_data_loader（parse_tsv 复用）
# [CONSUMERS] zephyr.frontend.dashboard.api_server（/api/chain-impact-stream 只读端点）; TDM 预留节点 TDM-E-L2-09-1/2 下游消费面（偏离监控/盘中扫描/负面否决）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 单拍形态 run(now)（无 while True/常驻循环，PERM-TRIGGER 纪律——节拍由消费端拉取自然形成）；PIT 严格（publish_time<=now，now 可注入测试）；fail-open：CH 不可达/词表加载失败→degraded=True+errors 留痕返回空快照不抛（对标 MOD-DATA-063 纪律）；新闻读取口径=c3_fundamental.news_data 多版本表（无 FINAL+news_id keep-first 去重，与 news_collector 同款）；图谱词表/图数据进程级 TTL 缓存 600s（对标 api_server _CM 缓存惯例，线程锁保护）；情绪方向默认复用 MOD-INT-AISA RuleBasedSentimentScorer（L1-S0-1 已挂真锚上游），可注入替换（event_score surprise_direction 同 [-1,1] 口径）；跨新闻标的聚合=同 symbol 取置信度最高者方向与条目，sources 累计（多源同向共振观察位，方向冲突时以高置信者为准 MVP 简化）；每新闻仅 hits 非空才进 items（无图谱命中新闻不产冲击条目）
# [MODIFY-GUARD] 待统筹登记（真源=接线指令 W5 行，蓝图由施工轨补画）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ChainImpactStreamError(ZA-IT-0031)——构造参数越界（window_minutes<=0/news_limit<=0）时抛；CH/PG 运行时故障→degraded=True 留痕返回不抛（fail-open 纪律）
# [TESTS] tests/intelligence/test_chain_impact_stream.py
# [A_module] module_id=MOD-INT_IMPACT_STREAM | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 接线指令 W5（盘中消费端点选型=HTTP 只读拉式：消费方为偏离监控/盘中扫描/负面否决三类拉式场景，EventBus 推式需常驻订阅者不合 MVP；W2 实测新闻入库延迟 p50≈6min/p90≈13min，300s flush buffer 为地板）

"""
MOD-INT_IMPACT_STREAM ChainImpactStream — 盘中事件冲击流编排器（接线 W5）。

端到端链路（单拍 run 一次执行）：
    新闻分钟窗拉取（c3_fundamental.news_data，PIT ≤now）
    → 逐条情绪打分（MOD-INT-AISA RuleBasedSentimentScorer，L1-S0-1 上游）
    → 产业链节点传导（MOD-INT_NEWS_CHAIN link，W3）
    → 冲击标的生成（MOD-INT_CHAIN_IMPACT resolve，W4）
    → 跨新闻标的聚合 → ChainImpactSnapshot（frozen，api_server 端点序列化透出）

缓存：词表+图数据进程级 TTL 600s（W3/W4 from_pg 成本摊销）；
     快照本身不缓存（分钟窗查询+规则匹配毫秒级，由消费端节拍拉取）。

不做什么：不写库（冲击流是只读视图）；不挂调度任务（PERM-TRIGGER：拉式消费
         自然成节拍；如需推式由调度族另接 run()）；不做前端渲染。

依据: docs/_working/2026-09-09-news-industry-wiring-directive.md W5 行
SSoT: depgraph MOD-INT_IMPACT_STREAM（design 态 node 见 depgraph DB）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: now 参数
#   fields: 参数 now，datetime | None
#   code: run 方法形参（PIT 截止，None=真实当前时刻）
# - id: I2
#   name: 新闻分钟窗
#   fields: news_id/publish_time/title/source 四列
#   code: c3_fundamental.news_data 查询产出
# 层: 算法
# - id: A1
#   name_zh: ① 分钟窗新闻拉取
#   name_en: fetch_news
#   intro: PIT 窗口 SQL 拉新闻，parse_tsv 解析+news_id 去重。
#   desc: 窗口=[now-window_minutes, now]；limit 截断最新；CH 故障→degraded 留痕。
#   inputs: I1 I2
#   outputs: list[ChainNewsItem]
#   invariant: publish_time≤now（PIT）
# - id: A2
#   name_zh: ② 逐条传导打分
#   name_en: _link_one
#   intro: 情绪打分→节点链接→标的生成，单条异常跳过留痕不炸批。
#   desc: polarity 死区内跳过 W3/W4（无方向冲击无意义）。
#   inputs: A1
#   outputs: list[NewsChainImpact]
#   invariant: 单条异常不炸批
# - id: A3
#   name_zh: ③ 跨新闻标的聚合
#   name_en: _aggregate
#   intro: 同 symbol 取置信度最高条目，sources 累计，排序输出。
#   desc: 聚合口径见模块 INVARIANTS（方向冲突以高置信者为准 MVP 简化）。
#   inputs: A2
#   outputs: tuple[ImpactTarget, ...]
#   invariant: symbol 唯一；排序确定（hop, -conf, symbol）
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Final
from zoneinfo import ZoneInfo

from zephyr.intelligence.chain_impact_resolver import (
    DIRECTION_DEAD_ZONE,
    ChainImpactResolver,
    ImpactTarget,
    direction_label,
)
from zephyr.intelligence.news_chain_node_linker import (
    ChainNodeHit,
    ChainNodeLinker,
)
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "GRAPH_CACHE_TTL_SECONDS",
    "SHANGHAI_TZ",
    "ChainImpactSnapshot",
    "ChainImpactStream",
    "ChainImpactStreamError",
    "NewsChainImpact",
    "ChainNewsItem",
]


class ChainImpactStreamError(ZephyrBaseError):
    """ZA-IT-0031: 盘中事件冲击流错误（构造参数越界等）。"""

    error_code = "ZA-IT-0031"


GRAPH_CACHE_TTL_SECONDS: Final[float] = 600.0

# publish_time 列时区（RULE-SCHEMA-TZ：业务列 DateTime64(3,'Asia/Shanghai')）——
# 窗口边界按上海墙钟拼 SQL，与列口径一致
SHANGHAI_TZ: Final[ZoneInfo] = ZoneInfo("Asia/Shanghai")

# SQL 常量（NO-BARE-SQL gate 豁免：_SQL_ 前缀）。多版本表读法与 news_collector 同款：
# 无 FINAL+news_id keep-first 去重（SCD 修正稿取最早版本，采集层统一口径）
_SQL_NEWS_WINDOW: Final[str] = (
    "SELECT news_id, publish_time, title, source FROM {table} "  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
    "WHERE publish_time >= toDateTime64('{start}', 3, 'Asia/Shanghai') "  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
    "AND publish_time <= toDateTime64('{end}', 3, 'Asia/Shanghai') "  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
    "ORDER BY publish_time DESC LIMIT {limit}"  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
)


@dataclass(frozen=True)
class ChainNewsItem:
    """窗口内单条新闻（传导输入）。"""

    news_id: str
    publish_time: str  # ISO 字符串（frozen dataclass 便于序列化）
    title: str
    source: str


@dataclass(frozen=True)
class NewsChainImpact:
    """单条新闻的传导结果（hits 非空才产出）。"""

    news: ChainNewsItem
    polarity: float
    direction_label: str
    hits: tuple[ChainNodeHit, ...]
    targets: tuple[ImpactTarget, ...]


@dataclass(frozen=True)
class ChainImpactSnapshot:
    """盘中事件冲击流单拍快照（api_server 端点透出载体）。"""

    window_start: str
    window_end: str
    news_count: int  # 窗口内新闻总数
    matched_count: int  # 其中图谱命中数
    items: tuple[NewsChainImpact, ...]
    all_targets: tuple[ImpactTarget, ...]  # 跨新闻聚合（symbol 唯一）
    vocab_size: int
    graph_size: tuple[int, int, int]
    latency_ms: int
    degraded: bool = False
    errors: tuple[str, ...] = field(default=())

    def to_dict(self) -> dict[str, Any]:
        """端点序列化（datetime 已在构造期转 ISO 字符串，纯 JSON 可序列化）。"""
        return {
            "ok": not self.degraded,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "news_count": self.news_count,
            "matched_count": self.matched_count,
            "items": [
                {
                    "news_id": it.news.news_id,
                    "publish_time": it.news.publish_time,
                    "title": it.news.title,
                    "source": it.news.source,
                    "polarity": round(it.polarity, 4),
                    "direction_label": it.direction_label,
                    "hits": [vars(h) for h in it.hits],
                    "targets": [_target_dict(t) for t in it.targets],
                }
                for it in self.items
            ],
            "all_targets": [_target_dict(t) for t in self.all_targets],
            "vocab_size": self.vocab_size,
            "graph_size": list(self.graph_size),
            "latency_ms": self.latency_ms,
            "degraded": self.degraded,
            "errors": list(self.errors),
        }


# 进程级图谱缓存（词表+图数据 600s 摊销 from_pg 成本；线程锁保护——FastAPI
# sync 端点跑 threadpool，多线程并发拉取同一缓存）
_GRAPH_CACHE: dict[str, Any] = {"loaded_at": 0.0, "linker": None, "resolver": None}
_GRAPH_CACHE_LOCK = threading.Lock()


class ChainImpactStream:
    """盘中事件冲击流编排器（新闻窗→情绪→图谱传导→标的聚合，单拍）。"""

    def __init__(
        self,
        linker: ChainNodeLinker | None = None,
        resolver: ChainImpactResolver | None = None,
        scorer: Callable[[str, str], tuple[float, tuple[str, ...]]] | None = None,
        *,
        window_minutes: int = 30,
        news_limit: int = 500,
        ch_query: Callable[[str], str] | None = None,
        news_table: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        linker / resolver / scorer : 注入（测试/离线）；None=生产路径（from_pg+
            RuleBasedSentimentScorer，图谱走进程级缓存）。scorer 签名 (title,
            content)→(polarity, keywords)，与 MOD-INT-AISA RuleBasedSentimentScorer 同。
        window_minutes / news_limit : 新闻窗口宽与条数上限（须>0）。
        ch_query : CH 查询函数注入（测试 mock）；None 走 ch_reader.query。
        news_table : 表名覆盖（测试注入临时表名用）；None 经 table_registry 解析。
        """
        if window_minutes <= 0:
            raise ChainImpactStreamError(f"window_minutes 须>0: {window_minutes}")
        if news_limit <= 0:
            raise ChainImpactStreamError(f"news_limit 须>0: {news_limit}")
        self._window_minutes = window_minutes
        self._news_limit = news_limit
        self._linker = linker
        self._resolver = resolver
        self._scorer = scorer
        self._ch_query = ch_query
        self._news_table = news_table

    # ------------------------------------------------------------------
    # 依赖装配（惰性）
    # ------------------------------------------------------------------

    def _get_linker(self) -> ChainNodeLinker:
        if self._linker is not None:
            return self._linker
        linker, resolver = _load_graph_bundle()
        self._resolver = self._resolver or resolver
        self._linker = linker
        return linker

    def _get_resolver(self) -> ChainImpactResolver:
        if self._resolver is not None:
            return self._resolver
        linker, resolver = _load_graph_bundle()
        self._linker = self._linker or linker
        self._resolver = resolver
        return resolver

    def _get_scorer(self) -> Callable[[str, str], tuple[float, tuple[str, ...]]]:
        if self._scorer is not None:
            return self._scorer
        from zephyr.intelligence.news_sentiment_analyzer import RuleBasedSentimentScorer

        self._scorer = RuleBasedSentimentScorer().score  # 绑定方法 (title, content)→(polarity, keywords)
        return self._scorer

    def _get_ch_query(self) -> Callable[[str], str]:
        if self._ch_query is not None:
            return self._ch_query
        from zephyr.data import ch_reader

        self._ch_query = ch_reader.query
        return self._ch_query

    def _get_news_table(self) -> str:
        if self._news_table is not None:
            return self._news_table
        from zephyr.data.table_registry import get_registry

        self._news_table = get_registry().table("fund_news_data")
        return self._news_table

    # ------------------------------------------------------------------
    # 单拍执行
    # ------------------------------------------------------------------

    def run(self, now: Any = None) -> ChainImpactSnapshot:
        """单拍：新闻窗→情绪→传导→标的聚合（fail-open，异常降级留痕不抛）。

        now 语义：None=真实当前时刻（now_utc SSoT→Asia/Shanghai 墙钟，与
        publish_time 列时区同口径）；注入 naive datetime 视为上海墙钟（测试）。
        """
        started = time.perf_counter()
        errors: list[str] = []
        structural_failure = False
        end = now if now is not None else now_utc().astimezone(SHANGHAI_TZ)
        start = end - timedelta(minutes=self._window_minutes)
        window_start_s = start.strftime("%Y-%m-%d %H:%M:%S")
        window_end_s = end.strftime("%Y-%m-%d %H:%M:%S")

        # ① 分钟窗新闻拉取
        news: list[ChainNewsItem] = []
        try:
            news = self._fetch_news(window_start_s, window_end_s)
        except Exception as exc:  # noqa: BLE001 — fail-open 纪律：CH 故障降级留痕
            structural_failure = True
            errors.append(f"news_fetch_failed: {type(exc).__name__}: {exc}")

        vocab_size = 0
        graph_size = (0, 0, 0)
        items: list[NewsChainImpact] = []
        if news:
            try:
                linker = self._get_linker()
                resolver = self._get_resolver()
                vocab_size = linker.vocab_size()
                graph_size = resolver.graph_size()
            except Exception as exc:  # noqa: BLE001 — fail-open 纪律：图谱加载故障降级留痕
                structural_failure = True
                errors.append(f"graph_load_failed: {type(exc).__name__}: {exc}")
            else:
                # ② 逐条传导打分（单条异常跳过留痕，不炸批）
                for item in news:
                    try:
                        one = self._link_one(linker, resolver, item)
                    except Exception as exc:  # noqa: BLE001 — 单条异常跳过不炸批（fail-open）
                        errors.append(f"link_failed[{item.news_id}]: {type(exc).__name__}: {exc}")
                        continue
                    if one is not None:
                        items.append(one)

        # ③ 跨新闻标的聚合
        all_targets = _aggregate_targets([one.targets for one in items])
        latency_ms = int((time.perf_counter() - started) * 1000)
        return ChainImpactSnapshot(
            window_start=window_start_s,
            window_end=window_end_s,
            news_count=len(news),
            matched_count=len(items),
            items=tuple(items),
            all_targets=all_targets,
            vocab_size=vocab_size,
            graph_size=graph_size,
            latency_ms=latency_ms,
            degraded=structural_failure,
            errors=tuple(errors),
        )

    # ------------------------------------------------------------------
    # 内部步骤
    # ------------------------------------------------------------------

    def _fetch_news(self, start_s: str, end_s: str) -> list[ChainNewsItem]:
        """分钟窗新闻拉取（PIT≤end；parse_tsv+news_id keep-first 去重）。"""
        from zephyr.regime.features.regime_data_loader import parse_tsv

        sql = _SQL_NEWS_WINDOW.format(
            table=self._get_news_table(), start=start_s, end=end_s, limit=self._news_limit
        )
        tsv = self._get_ch_query()(sql)
        rows = parse_tsv(tsv, ncols=4)
        seen: set[str] = set()
        out: list[ChainNewsItem] = []
        for news_id, publish_time, title, source in rows:
            if news_id in seen:
                continue  # 多版本 SCD 去重（keep-first=最早版本，news_collector 同款）
            seen.add(news_id)
            out.append(
                ChainNewsItem(
                    news_id=news_id,
                    publish_time=publish_time,
                    title=title,
                    source=source,
                )
            )
        return out

    def _link_one(
        self,
        linker: ChainNodeLinker,
        resolver: ChainImpactResolver,
        item: ChainNewsItem,
    ) -> NewsChainImpact | None:
        """单条新闻传导（情绪→节点→标的）；死区/无命中返回 None。"""
        polarity, _keywords = self._get_scorer()(item.title, "")
        hits = linker.link(item.title)
        if not hits:
            return None
        targets = resolver.resolve(hits, polarity)
        if not targets:
            return None  # 死区（中性）无方向冲击
        dir_int = int(polarity >= DIRECTION_DEAD_ZONE) - int(polarity <= -DIRECTION_DEAD_ZONE)
        return NewsChainImpact(
            news=item,
            polarity=polarity,
            direction_label=direction_label(dir_int),
            hits=hits,
            targets=targets,
        )


def _target_dict(t: ImpactTarget) -> dict[str, Any]:
    """ImpactTarget→JSON dict（含派生 direction_label，confidence 定精度）。"""
    d = vars(t).copy()
    d["confidence"] = round(t.confidence, 4)
    d["role_confidence"] = round(t.role_confidence, 4)
    d["direction_label"] = t.direction_label
    d["path"] = list(t.path)
    return d


def _aggregate_targets(
    per_news: list[tuple[ImpactTarget, ...]],
) -> tuple[ImpactTarget, ...]:
    """跨新闻标的聚合：同 symbol 取置信度最高条目，sources 累计（INVARIANTS 口径）。"""
    best: dict[str, ImpactTarget] = {}
    sources: dict[str, int] = {}
    for targets in per_news:
        for t in targets:
            sources[t.symbol] = sources.get(t.symbol, 0) + 1
            prev = best.get(t.symbol)
            if prev is None or t.confidence > prev.confidence:
                best[t.symbol] = t
    out = [ImpactTarget(**{**t.__dict__, "sources": sources[t.symbol]}) for t in best.values()]
    out.sort(key=lambda t: (t.hop, -t.confidence, t.symbol))
    return tuple(out)


def _load_graph_bundle() -> tuple[ChainNodeLinker, ChainImpactResolver]:
    """进程级图谱缓存读取（600s TTL；加载失败异常上抛由调用方降级）。"""
    with _GRAPH_CACHE_LOCK:
        age = time.monotonic() - float(_GRAPH_CACHE["loaded_at"])
        if _GRAPH_CACHE["linker"] is not None and age < GRAPH_CACHE_TTL_SECONDS:
            return _GRAPH_CACHE["linker"], _GRAPH_CACHE["resolver"]
        linker = ChainNodeLinker.from_pg()
        resolver = ChainImpactResolver.from_pg()
        _GRAPH_CACHE["loaded_at"] = time.monotonic()
        _GRAPH_CACHE["linker"] = linker
        _GRAPH_CACHE["resolver"] = resolver
        return linker, resolver
