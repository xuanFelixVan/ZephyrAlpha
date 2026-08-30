# [BLUEPRINT] MOD-DATA-065 | docs/03_modules/_domain_data/tushare_news_connector/blueprint.md
# [MODULE] zephyr.data.implementations.tushare_news_connector
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（接入契约纯内存；api/clock/gate 全注入不真发请求；tushare_provider 语义参照不 import）
# [CONSUMERS] 运行时装配批（tushare 权限开通后 API 适配器绑定 / news_collector 管道挂接 / 质量门控装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] API 调用全注入(未注入 Fail-Closed 不真发请求); 去重指纹=规范化标题+时间窗桶 sha256(跨源跨批次幂等); 接受集按 (published_at,news_id) 确定性排序; 回补完整性=区间窗格全覆盖判定(缺窗清单确定性); 质量门控未注入=全通过默认; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data/tushare_news_connector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TushareNewsError(占位 ZA-DATA-UNREGISTERED-TUSHARE-NEWS)——api缺失/非法区间/空标题/时间戳越界/非法窗宽时抛
# [TESTS] tests/data/implementations/test_tushare_news_connector.py
# [A_module] module_id=MOD-DATA-065 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
TushareNewsConnector — tushare 新闻源接入器（MOD-DATA-065）。

B13-04324 系列（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DAT-019，A3数据架构）：
tushare 新闻权限开通后的接入面——API 调用全注入（不真发请求）：news 快讯
接口接入 news_collector 管道语义 + 与现有源去重（标题+时间窗指纹）+ 历史
数据回补校验（回补区间完整性检查）+ 质量门控挂接（注入 gate 回调）。
权限开通属 Owner 窗口，本件=接入契约逻辑。

查重分工（蓝图 §0）：tushare_provider=行情 PIT 数据面（本件=新闻快讯接入，
不重复行情契约）；news_collector=多源聚合管道（本件=tushare 单源适配与
去重指纹供给，不重建聚合管道）；source_health_check=源健康探活（本件只
做接入契约，不做探活）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: api 参数
#   fields: 参数 api（无注解）
#   code: tushare_news_connector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: tushare_news_connector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: gate 参数
#   fields: 参数 gate（无注解）
#   code: tushare_news_connector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dedup_window_seconds 参数
#   fields: 参数 dedup_window_seconds（无注解）
#   code: tushare_news_connector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TushareNewsConnector
#   name_en: TushareNewsConnector
#   intro: tushare 新闻源接入器（注入API + 去重指纹 + 回补校验 + 质量门控）。
#   desc: tushare 新闻源接入器（注入API + 去重指纹 + 回补校验 + 质量门控）。；公共方法（定义序）: fingerprint, fetch_latest, backfill, seen_count；源码 L13…
#   inputs: api clock gate dedup_window_seconds source
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: TushareNewsConnector
#   downstream: 运行时装配批（tushare 权限开通后 API 适配器绑定 / news_collector 管道挂接 / 质量门控装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "BackfillReport",
    "FetchReport",
    "NewsItem",
    "TushareNewsConnector",
    "TushareNewsError",
]

#: 固定纪元参照（naive datetime 算术，避免本地时区导致的非确定性）
_EPOCH: Final = datetime.datetime(1970, 1, 1)
_WS_RE: Final = re.compile(r"\s+")


class TushareNewsError(Exception):
    """新闻接入输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-TUSHARE-NEWS。
    """


@dataclass(frozen=True)
class NewsItem:
    """规范化新闻条目（frozen；接入 news_collector 管道语义的最小载体）。"""

    news_id: str
    title: str
    content: str
    published_at: datetime.datetime
    source: str


@dataclass(frozen=True)
class FetchReport:
    """单次抓取报告（确定性）。"""

    accepted: tuple[NewsItem, ...]
    dedup_dropped: int
    gate_dropped: int


@dataclass(frozen=True)
class BackfillReport:
    """回补区间完整性报告（missing_windows 确定性排序）。"""

    start: datetime.datetime
    end: datetime.datetime
    windows_expected: int
    windows_covered: int
    missing_windows: tuple[datetime.datetime, ...]
    complete: bool
    accepted: tuple[NewsItem, ...]


class TushareNewsConnector:
    """tushare 新闻源接入器（注入API + 去重指纹 + 回补校验 + 质量门控）。"""

    def __init__(
        self,
        *,
        api: Callable[[datetime.datetime, datetime.datetime], Iterable[Mapping]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        gate: Callable[[NewsItem], bool] | None = None,
        dedup_window_seconds: int = 300,
        source: str = "tushare",
    ) -> None:
        if dedup_window_seconds <= 0:
            raise TushareNewsError(f"dedup_window_seconds 非法: {dedup_window_seconds!r}（须 > 0）")
        if not source:
            raise TushareNewsError("source 为空")
        self._api = api
        self._clock = clock or datetime.datetime.now
        self._gate = gate
        self._window = dedup_window_seconds
        self._source = source
        self._seen: set[str] = set()

    # ── 指纹 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _bucket_of(published_at: datetime.datetime, window_seconds: int) -> datetime.datetime:
        """时间窗桶（固定纪元算术，时区无关确定性）。"""
        secs = int((published_at - _EPOCH).total_seconds())
        bucketed = secs - (secs % window_seconds)
        return _EPOCH + datetime.timedelta(seconds=bucketed)

    @classmethod
    def fingerprint(
        cls,
        title: str,
        published_at: datetime.datetime,
        *,
        window_seconds: int = 300,
    ) -> str:
        """去重指纹：sha256(规范化标题 | 时间窗桶)（跨源幂等判定基准）。"""
        normalized = _WS_RE.sub(" ", title.strip()).lower()
        bucket = cls._bucket_of(published_at, window_seconds)
        raw = f"{normalized}|{bucket.isoformat()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ── 归一化 ────────────────────────────────────────────────────────────

    def _normalize(self, raw: Mapping, start: datetime.datetime, end: datetime.datetime) -> NewsItem:
        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            raise TushareNewsError(f"新闻条目空标题: {raw!r}")
        published_raw = raw.get("published_at")
        if isinstance(published_raw, str):
            published_at = datetime.datetime.fromisoformat(published_raw)
        elif isinstance(published_raw, datetime.datetime):
            published_at = published_raw
        else:
            raise TushareNewsError(f"新闻条目时间戳非法: {published_raw!r}")
        if not (start <= published_at <= end):
            raise TushareNewsError(
                f"新闻时间戳越界: {published_at.isoformat()} 不在 "
                f"[{start.isoformat()}, {end.isoformat()}]（API 契约违反）"
            )
        content = raw.get("content", "")
        if not isinstance(content, str):
            raise TushareNewsError(f"新闻条目 content 非法: {type(content).__name__}")
        news_id = raw.get("news_id")
        if not isinstance(news_id, str) or not news_id:
            fp = self.fingerprint(title, published_at, window_seconds=self._window)
            news_id = f"{self._source}-{fp[:12]}"  # 确定性派生 id
        return NewsItem(
            news_id=news_id,
            title=title.strip(),
            content=content,
            published_at=published_at,
            source=self._source,
        )

    # ── 抓取（news 快讯 → 管道语义） ───────────────────────────────────────

    def _fetch(self, start: datetime.datetime, end: datetime.datetime) -> FetchReport:
        if self._api is None:
            raise TushareNewsError("api 回调未注入（不真发请求，禁止旁路）")
        if not (start < end):
            raise TushareNewsError(f"非法区间: start={start.isoformat()} 须早于 end={end.isoformat()}")
        raws = list(self._api(start, end))
        accepted: list[NewsItem] = []
        dedup_dropped = 0
        gate_dropped = 0
        batch_seen: set[str] = set()
        for raw in raws:
            item = self._normalize(raw, start, end)
            fp = self.fingerprint(item.title, item.published_at, window_seconds=self._window)
            if fp in self._seen or fp in batch_seen:
                dedup_dropped += 1
                continue
            batch_seen.add(fp)
            if self._gate is not None and not self._gate(item):
                gate_dropped += 1
                continue
            accepted.append(item)
        accepted.sort(key=lambda it: (it.published_at, it.news_id))  # 确定性
        self._seen.update(batch_seen)
        _log.info(
            "tushare 新闻抓取: 接受 %d / 去重丢弃 %d / 门控丢弃 %d",
            len(accepted),
            dedup_dropped,
            gate_dropped,
        )
        return FetchReport(
            accepted=tuple(accepted),
            dedup_dropped=dedup_dropped,
            gate_dropped=gate_dropped,
        )

    def fetch_latest(self, start: datetime.datetime, end: datetime.datetime) -> FetchReport:
        """增量抓取：归一化 → 指纹去重（含历史已见）→ 质量门控 → 确定性排序。"""
        return self._fetch(start, end)

    # ── 回补（区间完整性校验） ────────────────────────────────────────────

    def backfill(self, start: datetime.datetime, end: datetime.datetime) -> BackfillReport:
        """历史回补：抓取 + 回补区间完整性检查（窗格全覆盖判定）。"""
        report = self._fetch(start, end)
        expected: list[datetime.datetime] = []
        cursor = self._bucket_of(start, self._window)
        while cursor < end:
            if cursor >= start or cursor + datetime.timedelta(seconds=self._window) > start:
                expected.append(cursor)
            cursor += datetime.timedelta(seconds=self._window)
        covered = {self._bucket_of(item.published_at, self._window) for item in report.accepted}
        missing = tuple(w for w in expected if w not in covered)  # expected 已升序
        return BackfillReport(
            start=start,
            end=end,
            windows_expected=len(expected),
            windows_covered=len(expected) - len(missing),
            missing_windows=missing,
            complete=not missing,
            accepted=report.accepted,
        )

    # ── 观测 ─────────────────────────────────────────────────────────────

    def seen_count(self) -> int:
        """已见指纹数（跨抓取去重累积）。"""
        return len(self._seen)
