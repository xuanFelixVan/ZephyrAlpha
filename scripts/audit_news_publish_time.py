# [BLUEPRINT] MOD-DATA-067 | 待统筹登记（blueprint 未建，真源=candidate_module_registry CAND-DAT-022 行 + 2026-08-25-news-sentiment-upgrade-discussion.md §8 Q4）
# [MODULE] scripts.audit_news_publish_time
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader（CH 读取通道，注入式 query_fn 可替换）; zephyr.data.table_registry（表名真源派生）; dateutil
# [CONSUMERS] CAND-DAT-022 口径审计（Owner 拍板 Q4/P1）；审计报告落 .runtime/ 供回测可信度评估消费
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读审计：不写入 ClickHouse、不修改库内任何数据；唯一落盘物为 .runtime/ 审计报告（原子写入）；表名由 TableRegistry 派生不硬编码；CH 不可达/空样本产出 INSUFFICIENT_DATA 降级结论不崩溃
# [MODIFY-GUARD] candidate_module_registry.yaml CAND-DAT-022；design_memos/2026-08-25-news-sentiment-upgrade-discussion.md §8 Q4
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 参数非法 -> exit 2；CH 查询失败/空样本 -> 报告降级结论 + exit 0；报告写盘失败 -> exit 1（错误消息不含路径，路径仅入 details 日志字段）
# [TESTS] tests/scripts/test_audit_news_publish_time.py
# [A_module] module_id=MOD-DATA-067 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""audit_news_publish_time.py — news_data publish_time 口径审计（CAND-DAT-022，Q4/P1）。

背景
----
news_data.publish_time（记录声称的发布时间）与 crawl_time/ingest_ts（采集/入库时间）
的口径未经审计：若 publish_time 实际是采集时间填充，所有按新闻时间戳的回测都有前视
风险。本脚本抽样最近 N 天记录，比对三口径并出可信度结论：

- 口径 A：publish_time → crawl_time 延迟分布（采集延迟画像）
- 口径 B：publish_time → ingest_ts 延迟分布（入库延迟画像）
- 口径 C：同标题多源记录的 publish_time 极差（跨源口径一致性）

可疑指纹
--------
- ``publish≈crawl``：|publish_time - crawl_time| ≤ 2s 占比高 → publish_time 疑似由
  采集时间生成（假时间戳）；
- ``整点吸附``：publish_time 分/秒全为 0 的占比异常高 → 粗粒度/伪造时间戳；
- ``负延迟``：publish_time 晚于 ingest_ts 超容忍窗 → 物理不可能的"未来发布"；
- ``采集延迟``：ingest_ts 远早于 publish_time（延迟 > 24h）→ 旧闻新采；
- ``epoch 缺失``：publish_time 为 1970 纪元哨兵（发布时间缺失）。

口径结论（可信度等级）
--------------------
- TRUSTED：publish≈crawl 指纹 <5% 且负延迟 <1% 且 p95 延迟 <1h 且整点吸附 <5%；
- SUSPECT：publish≈crawl 指纹 <50% 且负延迟 <5% 且 p95 延迟 <24h；
- DISTRUSTED：其余（publish_time 不可作为回测时间戳，需重采或时间戳回推）；
- INSUFFICIENT_DATA：样本为空（CH 不可达/窗口无数据），不出结论。

用法
----
    python scripts/audit_news_publish_time.py                      # 默认 30 天 / 抽样 10000 条
    python scripts/audit_news_publish_time.py --days 7 --sample 2000
    python scripts/audit_news_publish_time.py --out .runtime/news_publish_time_audit_20260830.md
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Final, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from zephyr.data.table_registry import get_registry  # noqa: E402

log = logging.getLogger(__name__)

# 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024，门禁：禁硬编码表名）
_TBL_NEWS_DATA: Final[str] = get_registry().table("fund_news_data")

DEFAULT_DAYS: Final[int] = 30
DEFAULT_SAMPLE: Final[int] = 10_000
DEFAULT_DUP_GROUPS: Final[int] = 200  # 多源口径比对的最大同标题组数
SUSPECT_SAMPLE_LIMIT: Final[int] = 20  # 报告可疑样本清单上限

# 判定阈值（秒 / 比率）
FINGERPRINT_TOLERANCE_SEC: Final[float] = 2.0  # |publish-crawl|≤2s 视为"采集时间填充"指纹
NEGATIVE_LAG_TOLERANCE_SEC: Final[float] = 300.0  # publish 晚于 ingest >5min 判负延迟异常
COLLECTION_DELAY_WARN_SEC: Final[float] = 86_400.0  # ingest 早于 publish >24h 判采集延迟
MULTI_SOURCE_SPREAD_WARN_SEC: Final[float] = 86_400.0  # 同标题跨源发布时间极差 >24h 可疑
EPOCH_SENTINEL_YEAR: Final[int] = 1971  # publish_time < 1971 = 纪元哨兵（发布时间缺失）

# 可信度等级
VERDICT_TRUSTED: Final[str] = "TRUSTED"
VERDICT_SUSPECT: Final[str] = "SUSPECT"
VERDICT_DISTRUSTED: Final[str] = "DISTRUSTED"
VERDICT_INSUFFICIENT: Final[str] = "INSUFFICIENT_DATA"

_REPORT_NAME: Final[str] = "news_publish_time_audit_20260830.md"

# SQL 模板（days/sample 为 argparse int 校验值，表名为注册表真源，无注入面）
_SQL_SAMPLE: Final[str] = (
    "SELECT news_id, publish_time, crawl_time, ingest_ts, source, title "
    "FROM {table} WHERE publish_time >= now() - INTERVAL {days} DAY "
    "ORDER BY rand() LIMIT {sample}"
)
_SQL_MULTI_SOURCE: Final[str] = (
    "SELECT title, source, publish_time "
    "FROM {table} "
    "WHERE publish_time >= now() - INTERVAL {days} DAY AND title IN ("
    "SELECT title "
    "FROM {table} "
    "WHERE publish_time >= now() - INTERVAL {days} DAY "
    "GROUP BY title HAVING uniqExact(source) > 1 ORDER BY count() DESC LIMIT {dup_groups})"
)


@dataclass(frozen=True, slots=True)
class NewsTimeRecord:
    """单条新闻的三口径时间戳（publish=记录声称发布时间，crawl=采集，ingest=入库）。"""

    news_id: str
    publish_time: datetime | None
    crawl_time: datetime | None
    ingest_ts: datetime | None
    source: str
    title: str


@dataclass(frozen=True, slots=True)
class DelayStats:
    """延迟分布画像（秒）。"""

    n: int
    p50: float
    p95: float
    max: float
    mean: float
    n_negative: int  # publish 晚于基准超容忍窗（物理不可能方向）
    n_delayed: int  # 基准晚于 publish 超 24h（采集/入库延迟）


@dataclass(frozen=True, slots=True)
class MultiSourceSpread:
    """同标题多源 publish_time 极差画像。"""

    n_groups: int
    p50_hours: float
    p95_hours: float
    max_hours: float
    n_suspect: int  # 极差 > 24h 的组数
    samples: tuple[tuple[str, str, float], ...]  # (title 截断, sources, spread_hours)


@dataclass(frozen=True, slots=True)
class NewsTimeAuditReport:
    """publish_time 口径审计报告（内存形态，render_markdown 落盘）。"""

    table: str
    window_days: int
    sample_size: int
    crawl_delay: DelayStats
    ingest_delay: DelayStats
    fingerprint_ratio: float  # publish≈crawl（±2s）占比——假时间戳主指纹
    hourly_snap_ratio: float  # publish_time 分秒全 0 占比——粗粒度指纹
    epoch_missing: int  # publish_time 纪元哨兵条数
    multi_source: MultiSourceSpread
    suspect_samples: tuple[tuple[str, str, str], ...]  # (news_id, source, 原因)
    verdict: str
    verdict_reasons: tuple[str, ...] = field(default_factory=tuple)


def parse_ch_datetime(raw: str) -> datetime | None:
    """解析 CH TSV 时间戳（DateTime64 带时区/毫秒两种形态）为 UTC aware datetime。

    naive 串按 None 返回（口径不明不猜）；解析失败返回 None（审计不中断）。
    """
    text = (raw or "").strip()
    if not text:
        return None
    try:
        from dateutil import parser as date_parser

        dt = date_parser.parse(text)
    except Exception:  # noqa: BLE001 — 审计容错：单行坏时间戳不阻断整体
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def parse_sample_tsv(tsv: str) -> list[NewsTimeRecord]:
    """解析抽样 TSV（news_id/publish_time/crawl_time/ingest_ts/source/title 六列）。"""
    records: list[NewsTimeRecord] = []
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 6:
            continue
        records.append(
            NewsTimeRecord(
                news_id=parts[0],
                publish_time=parse_ch_datetime(parts[1]),
                crawl_time=parse_ch_datetime(parts[2]),
                ingest_ts=parse_ch_datetime(parts[3]),
                source=parts[4],
                title=parts[5],
            )
        )
    return records


def _percentile(sorted_vals: Sequence[float], q: float) -> float:
    """线性插值百分位；空序列返回 0.0。"""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return float(sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac)


def _lag_seconds(rec: NewsTimeRecord, attr: str) -> float | None:
    """基准时间 - publish_time（秒）；任一侧缺失/纪元哨兵返回 None。"""
    base = getattr(rec, attr)
    if base is None or rec.publish_time is None:
        return None
    if rec.publish_time.year < EPOCH_SENTINEL_YEAR:
        return None
    return (base - rec.publish_time).total_seconds()


def compute_delay_stats(records: Sequence[NewsTimeRecord], attr: str) -> DelayStats:
    """publish_time → 基准（crawl_time/ingest_ts）延迟分布。

    正值=正常方向（先发布后采集/入库）；负值超容忍窗=负延迟异常。
    """
    lags = [lag for rec in records if (lag := _lag_seconds(rec, attr)) is not None]
    if not lags:
        return DelayStats(0, 0.0, 0.0, 0.0, 0.0, 0, 0)
    ordered = sorted(lags)
    return DelayStats(
        n=len(lags),
        p50=_percentile(ordered, 0.50),
        p95=_percentile(ordered, 0.95),
        max=ordered[-1],
        mean=sum(lags) / len(lags),
        n_negative=sum(1 for v in lags if v < -NEGATIVE_LAG_TOLERANCE_SEC),
        n_delayed=sum(1 for v in lags if v > COLLECTION_DELAY_WARN_SEC),
    )


def compute_fingerprint_ratio(records: Sequence[NewsTimeRecord]) -> float:
    """publish≈crawl（±2s）占比——publish_time 由采集时间填充的主指纹。"""
    pairs = [
        abs((rec.crawl_time - rec.publish_time).total_seconds())
        for rec in records
        if rec.crawl_time is not None and rec.publish_time is not None
    ]
    if not pairs:
        return 0.0
    return sum(1 for v in pairs if v <= FINGERPRINT_TOLERANCE_SEC) / len(pairs)


def compute_hourly_snap_ratio(records: Sequence[NewsTimeRecord]) -> float:
    """publish_time 分/秒/毫秒全 0 占比——整点吸附=粗粒度/伪造时间戳指纹。"""
    pts = [rec.publish_time for rec in records if rec.publish_time is not None]
    if not pts:
        return 0.0
    snapped = sum(1 for dt in pts if dt.minute == 0 and dt.second == 0 and dt.microsecond == 0)
    return snapped / len(pts)


def count_epoch_missing(records: Sequence[NewsTimeRecord]) -> int:
    """publish_time 为纪元哨兵（发布时间缺失）的条数。"""
    return sum(1 for rec in records if rec.publish_time is not None and rec.publish_time.year < EPOCH_SENTINEL_YEAR)


def compute_multi_source_spread(tsv: str) -> MultiSourceSpread:
    """同标题多源记录的 publish_time 极差分布（口径 C：跨源一致性）。"""
    groups: dict[str, list[tuple[str, datetime]]] = {}
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        pt = parse_ch_datetime(parts[2])
        if pt is None or pt.year < EPOCH_SENTINEL_YEAR:
            continue
        groups.setdefault(parts[0], []).append((parts[1], pt))
    spreads: list[float] = []
    suspects: list[tuple[str, str, float]] = []
    for title, items in groups.items():
        sources = {src for src, _ in items}
        if len(sources) < 2:
            continue
        pts = [pt for _, pt in items]
        spread_h = (max(pts) - min(pts)).total_seconds() / 3600.0
        spreads.append(spread_h)
        if spread_h * 3600.0 > MULTI_SOURCE_SPREAD_WARN_SEC:
            suspects.append((title[:40], "/".join(sorted(sources)), spread_h))
    ordered = sorted(spreads)
    suspects.sort(key=lambda s: -s[2])
    return MultiSourceSpread(
        n_groups=len(spreads),
        p50_hours=_percentile(ordered, 0.50),
        p95_hours=_percentile(ordered, 0.95),
        max_hours=ordered[-1] if ordered else 0.0,
        n_suspect=len(suspects),
        samples=tuple(suspects[:SUSPECT_SAMPLE_LIMIT]),
    )


def _flag_record(rec: NewsTimeRecord) -> list[str]:
    """单条记录可疑标记（负延迟/采集延迟/整点吸附/纪元哨兵/采集时间填充指纹）。"""
    flags: list[str] = []
    if rec.publish_time is None:
        return ["publish_time 解析失败"]
    if rec.publish_time.year < EPOCH_SENTINEL_YEAR:
        flags.append("publish_time 纪元哨兵（发布时间缺失）")
        return flags
    lag_ingest = _lag_seconds(rec, "ingest_ts")
    if lag_ingest is not None and lag_ingest < -NEGATIVE_LAG_TOLERANCE_SEC:
        flags.append(f"负延迟：publish 晚于 ingest {-lag_ingest / 60.0:.1f}min（物理不可能方向）")
    if lag_ingest is not None and lag_ingest > COLLECTION_DELAY_WARN_SEC:
        flags.append(f"采集延迟：ingest 晚于 publish {lag_ingest / 3600.0:.1f}h（旧闻新采）")
    if rec.publish_time.minute == 0 and rec.publish_time.second == 0 and rec.publish_time.microsecond == 0:
        flags.append("整点吸附（分秒全 0）")
    if rec.crawl_time is not None:
        gap = abs((rec.crawl_time - rec.publish_time).total_seconds())
        if gap <= FINGERPRINT_TOLERANCE_SEC:
            flags.append("publish≈crawl（±2s，疑似采集时间填充）")
    return flags


def _collect_suspects(records: Sequence[NewsTimeRecord]) -> tuple[tuple[str, str, str], ...]:
    """可疑样本清单（按标记数降序，截断 SUSPECT_SAMPLE_LIMIT）。"""
    flagged: list[tuple[str, str, str]] = []
    for rec in records:
        flags = _flag_record(rec)
        if flags:
            flagged.append((rec.news_id, rec.source, "；".join(flags)))
    flagged.sort(key=lambda row: -row[2].count("；"))
    return tuple(flagged[:SUSPECT_SAMPLE_LIMIT])


def assess_verdict(
    fingerprint_ratio: float,
    negative_ratio: float,
    p95_lag_sec: float,
    hourly_snap_ratio: float,
    n: int,
) -> tuple[str, tuple[str, ...]]:
    """口径可信度评级（阈值见模块 docstring；n=0 → INSUFFICIENT_DATA）。"""
    if n == 0:
        return VERDICT_INSUFFICIENT, ("样本为空（CH 不可达或窗口内无数据），不出口径结论",)
    reasons = (
        f"publish≈crawl 指纹占比 {fingerprint_ratio:.1%}（阈值 5%/50%）",
        f"负延迟占比 {negative_ratio:.2%}（阈值 1%/5%）",
        f"publish→crawl p95 延迟 {p95_lag_sec / 60.0:.1f}min（阈值 1h/24h）",
        f"整点吸附占比 {hourly_snap_ratio:.1%}（阈值 5%）",
    )
    if fingerprint_ratio < 0.05 and negative_ratio < 0.01 and p95_lag_sec < 3600.0 and hourly_snap_ratio < 0.05:
        return VERDICT_TRUSTED, reasons
    if fingerprint_ratio < 0.50 and negative_ratio < 0.05 and p95_lag_sec < 86400.0:
        return VERDICT_SUSPECT, reasons
    return VERDICT_DISTRUSTED, reasons


def build_report(
    records: Sequence[NewsTimeRecord],
    multi_source_tsv: str,
    *,
    table: str,
    window_days: int,
) -> NewsTimeAuditReport:
    """装配审计报告（纯函数：记录序列 + 多源 TSV → NewsTimeAuditReport）。"""
    crawl_delay = compute_delay_stats(records, "crawl_time")
    ingest_delay = compute_delay_stats(records, "ingest_ts")
    fingerprint = compute_fingerprint_ratio(records)
    snap = compute_hourly_snap_ratio(records)
    multi = compute_multi_source_spread(multi_source_tsv)
    neg_ratio = (crawl_delay.n_negative / crawl_delay.n) if crawl_delay.n else 0.0
    verdict, reasons = assess_verdict(fingerprint, neg_ratio, crawl_delay.p95, snap, len(records))
    return NewsTimeAuditReport(
        table=table,
        window_days=window_days,
        sample_size=len(records),
        crawl_delay=crawl_delay,
        ingest_delay=ingest_delay,
        fingerprint_ratio=fingerprint,
        hourly_snap_ratio=snap,
        epoch_missing=count_epoch_missing(records),
        multi_source=multi,
        suspect_samples=_collect_suspects(records),
        verdict=verdict,
        verdict_reasons=reasons,
    )


def _fmt_sec(sec: float) -> str:
    """秒数人性化（<2h 用分钟，否则用小时）。"""
    if abs(sec) < 7200.0:
        return f"{sec / 60.0:.1f}min"
    return f"{sec / 3600.0:.1f}h"


def render_markdown(report: NewsTimeAuditReport) -> str:
    """NewsTimeAuditReport → markdown 报告文本。"""
    lines = [
        "# news_data publish_time 口径审计报告（CAND-DAT-022）",
        "",
        f"- 审计表：`{report.table}`",
        f"- 窗口：最近 {report.window_days} 天",
        f"- 样本量：{report.sample_size} 条（随机抽样）",
        "",
        "## 口径 A：publish_time → crawl_time（采集延迟画像）",
        "",
        f"- n={report.crawl_delay.n}，p50={_fmt_sec(report.crawl_delay.p50)}，"
        f"p95={_fmt_sec(report.crawl_delay.p95)}，max={_fmt_sec(report.crawl_delay.max)}，"
        f"mean={_fmt_sec(report.crawl_delay.mean)}",
        f"- 负延迟（publish 晚于 crawl 超 5min，物理不可能方向）：{report.crawl_delay.n_negative} 条",
        f"- 采集延迟超 24h（旧闻新采）：{report.crawl_delay.n_delayed} 条",
        "",
        "## 口径 B：publish_time → ingest_ts（入库延迟画像）",
        "",
        f"- n={report.ingest_delay.n}，p50={_fmt_sec(report.ingest_delay.p50)}，"
        f"p95={_fmt_sec(report.ingest_delay.p95)}，max={_fmt_sec(report.ingest_delay.max)}，"
        f"mean={_fmt_sec(report.ingest_delay.mean)}",
        f"- 负延迟：{report.ingest_delay.n_negative} 条；入库延迟超 24h：{report.ingest_delay.n_delayed} 条",
        "",
        "## 口径 C：同标题多源 publish_time 极差（跨源一致性）",
        "",
        f"- 多源组数：{report.multi_source.n_groups}，极差 p50={report.multi_source.p50_hours:.2f}h，"
        f"p95={report.multi_source.p95_hours:.2f}h，max={report.multi_source.max_hours:.2f}h",
        f"- 极差超 24h 可疑组：{report.multi_source.n_suspect} 组",
        "",
        "## 可疑指纹汇总",
        "",
        f"- publish≈crawl（±2s）占比：{report.fingerprint_ratio:.1%}（高占比=publish_time 实为采集时间）",
        f"- 整点吸附（分秒全 0）占比：{report.hourly_snap_ratio:.1%}（高占比=粗粒度/伪造时间戳）",
        f"- publish_time 纪元哨兵（发布时间缺失）：{report.epoch_missing} 条",
        "",
        "## 可疑样本清单（Top %d）" % SUSPECT_SAMPLE_LIMIT,
        "",
        "| news_id | source | 可疑原因 |",
        "|---|---|---|",
    ]
    for news_id, source, reason in report.suspect_samples:
        lines.append(f"| `{news_id}` | {source} | {reason} |")
    if not report.suspect_samples:
        lines.append("| — | — | 无可疑样本 |")
    lines += [
        "",
        "## 多源极差可疑组（同标题跨源发布时间差 >24h）",
        "",
        "| 标题（截断） | 源 | 极差(h) |",
        "|---|---|---|",
    ]
    for title, sources, spread_h in report.multi_source.samples:
        lines.append(f"| {title} | {sources} | {spread_h:.2f} |")
    if not report.multi_source.samples:
        lines.append("| — | — | — |")
    lines += [
        "",
        "## 口径结论",
        "",
        f"**publish_time 可信度等级：{report.verdict}**",
        "",
    ]
    lines += [f"- {r}" for r in report.verdict_reasons]
    lines.append("")
    if report.verdict == VERDICT_DISTRUSTED:
        lines.append(
            "> 处置建议：publish_time 不可作为回测事件时间戳（前视风险）。修复方向=重采源站真实发布时间"
            "（full_publish_time 回填）或按源时间戳回推；过渡期回测 MUST 以 crawl_time 保守口径对齐。"
        )
    elif report.verdict == VERDICT_SUSPECT:
        lines.append("> 处置建议：部分记录口径可疑，回测使用时按源分层评估；优先排查 publish≈crawl 指纹高发源。")
    elif report.verdict == VERDICT_TRUSTED:
        lines.append("> publish_time 可作为回测事件时间戳使用（抽样口径内未见系统性伪造指纹）。")
    else:
        lines.append("> 样本不足，需 CH 可达后重跑。")
    lines.append("")
    return "\n".join(lines)


def fetch_sample(query_fn: Callable[[str], str], days: int, sample: int) -> str:
    """抽样最近 days 天 sample 条（注入式 CH 读取通道）。"""
    return query_fn(_SQL_SAMPLE.format(table=_TBL_NEWS_DATA, days=days, sample=sample))


def fetch_multi_source(query_fn: Callable[[str], str], days: int, dup_groups: int) -> str:
    """拉取同标题多源记录（口径 C 输入，注入式）。"""
    return query_fn(_SQL_MULTI_SOURCE.format(table=_TBL_NEWS_DATA, days=days, dup_groups=dup_groups))


def _atomic_write(path: Path, content: str) -> None:
    """原子写入（RULE-ONE：tmp+replace，防多实例并发截断）。"""
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _default_report_path() -> Path:
    return Path(__file__).resolve().parents[1] / ".runtime" / _REPORT_NAME


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="news_data publish_time 口径审计（CAND-DAT-022）")
    p.add_argument("--days", type=int, default=DEFAULT_DAYS, help=f"审计窗口天数（默认 {DEFAULT_DAYS}）")
    p.add_argument("--sample", type=int, default=DEFAULT_SAMPLE, help=f"随机抽样条数（默认 {DEFAULT_SAMPLE}）")
    p.add_argument(
        "--dup-groups",
        type=int,
        default=DEFAULT_DUP_GROUPS,
        help=f"多源比对最大同标题组数（默认 {DEFAULT_DUP_GROUPS}）",
    )
    p.add_argument("--out", default="", help="报告输出路径（默认 .runtime/ 下固定名）")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    if args.days <= 0 or args.sample <= 0 or args.dup_groups <= 0:
        print("[ERROR] --days/--sample/--dup-groups 须为正整数", file=sys.stderr)
        return 2

    from zephyr.data import ch_reader  # 延迟 import：测试路径不触 CH

    records = parse_sample_tsv(fetch_sample(ch_reader.query, args.days, args.sample))
    multi_tsv = fetch_multi_source(ch_reader.query, args.days, args.dup_groups)
    report = build_report(records, multi_tsv, table=_TBL_NEWS_DATA, window_days=args.days)

    out_path = Path(args.out) if args.out else _default_report_path()
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(out_path, render_markdown(report))
    except OSError as exc:
        log.error("报告写盘失败: type=%s detail=%s", type(exc).__name__, exc)
        print("[ERROR] 报告写盘失败（详见日志）", file=sys.stderr)
        return 1

    print(
        f"[audit] 表={report.table} 窗口={report.window_days}d 样本={report.sample_size} "
        f"指纹publish≈crawl={report.fingerprint_ratio:.1%} 整点吸附={report.hourly_snap_ratio:.1%} "
        f"结论={report.verdict}"
    )
    print(f"[audit] 报告已落盘（{out_path.name}，.runtime/ 运行时区）")
    return 0


__all__: Final = [
    "NewsTimeAuditReport",
    "DelayStats",
    "MultiSourceSpread",
    "NewsTimeRecord",
    "VERDICT_DISTRUSTED",
    "VERDICT_INSUFFICIENT",
    "VERDICT_SUSPECT",
    "VERDICT_TRUSTED",
    "assess_verdict",
    "build_report",
    "compute_delay_stats",
    "compute_fingerprint_ratio",
    "compute_hourly_snap_ratio",
    "compute_multi_source_spread",
    "count_epoch_missing",
    "fetch_multi_source",
    "fetch_sample",
    "main",
    "parse_ch_datetime",
    "parse_sample_tsv",
    "render_markdown",
]


if __name__ == "__main__":
    sys.exit(main())
