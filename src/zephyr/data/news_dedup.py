# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.news_dedup
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.provider_base
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读查询已有数据；基于标题MD5哈希去重；不修改原始FetchResult
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 去重异常->跳过去重直接返回原始数据（fail-open）
# [TESTS] tests/zephyr/data/test_news_dedup.py
# [A_module] module_id=MOD-GOV-news_dedup | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""新闻数据去重模块（MOD-L00-004 §4.3）。

基于标题 MD5 哈希对新闻数据进行查重去重。
不同新闻源（AKShare/财联社/东方财富/RSS）获取的内容可能不同，
需要基于标题去重，避免同一条新闻被多个源重复写入。

设计要点：
- 查询 ClickHouse 中最近 N 天已有新闻的标题哈希集合
- 过滤掉已存在的标题哈希
- 同时过滤同一批次内的重复标题
- fail-open：去重异常时跳过去重，返回原始数据（不阻断写入）
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime

from . import ch_reader
from .provider_base import FetchResult
from .table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_NEWS_DATA = get_registry().table("fund_news_data")

# 查重窗口（天）
_DEDUP_WINDOW_DAYS = 7

# SQL 集中化：查询最近 N 天已有新闻标题
_SQL_DEDUP_QUERY_TEMPLATE = f"SELECT title FROM {_TBL_NEWS_DATA} WHERE publish_time >= now() - INTERVAL {{days}} DAY"

# SQL 集中化：写前预检（CAND-DAT-025）
_SQL_EXISTING_IDS_TEMPLATE = f"SELECT DISTINCT news_id FROM {_TBL_NEWS_DATA} WHERE {{where}}"

# news_data 表标准列顺序（与 c3_fundamental.news_data schema 对齐）
# 必填列（无 DEFAULT）：news_id, publish_time, title, content, source, data_source
# 可选列（有 DEFAULT）：summary, source_url, category, region(默认'CN'), language(默认'zh'), ...
# #ARCH-RSS-INVESTING-403-001：显式写入 region/language，避免海外新闻被表 DEFAULT 误标 CN/zh
NEWS_DATA_COLUMNS = [
    "news_id",
    "publish_time",
    "title",
    "content",
    "summary",
    "source",
    "source_url",
    "data_source",
    "region",
    "language",
]

# title 在 NEWS_DATA_COLUMNS 中的索引（dedup_news_result 用）
_TITLE_INDEX = NEWS_DATA_COLUMNS.index("title")


def _tz_shanghai():
    """Asia/Shanghai 时区对象（dateutil 自带时区库，Windows 无 tzdata 依赖）。"""
    from dateutil import tz

    return tz.gettz("Asia/Shanghai")


def _parse_datetime(dt_str: str) -> str:
    """解析各种格式的日期时间字符串为 ClickHouse DateTime 格式。

    支持 RFC 2822（RSS）、ISO 8601（JSON Feed）、常见中文格式等。
    解析失败时返回原始字符串前 19 字符或当前时间。

    时区语义（CAND-DAT-025 固化，防 8h 漂移复发）：
    - naive 串/纯日期：一律按 Asia/Shanghai 墙钟落地（列时区解析）
    - tz-aware 串：先 astimezone(Asia/Shanghai) 再落地（同一绝对时刻）
    """
    if not dt_str or not str(dt_str).strip():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        from dateutil import parser as date_parser

        dt = date_parser.parse(str(dt_str))
        if dt.tzinfo is not None:
            dt = dt.astimezone(_tz_shanghai())
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        s = str(dt_str).strip()
        return s[:19] if len(s) >= 19 else s


def existing_news_ids(where: str) -> set[str]:
    """写前预检：库内满足 where 条件的已存在 news_id 集合（CAND-DAT-025）。

    供批量回填脚本在写入侧过滤多版本冗余行（ReplacingMergeTree 按
    (news_id, publish_time) 折叠，同 id 不同 publish_time 永不折叠——
    实证见 design_memos/67_news_data_dedup_design.md §1.2）。

    Args:
        where: SQL WHERE 谓词（不含 WHERE 关键字），调用方负责条件正确性

    Returns:
        news_id 集合；查询失败返回空集合（fail-open，与模块既有契约一致）
    """
    try:
        result = ch_reader.query(_SQL_EXISTING_IDS_TEMPLATE.format(where=where))
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.warning("写前预检查询失败，返回空集合（fail-open）: %s", e)
        return set()
    if not result:
        return set()
    return {line.strip() for line in result.strip().split("\n") if line.strip()}


def build_news_row(
    pub_date: str,
    title: str,
    link: str,
    summary: str,
    source: str,
    data_source: str,
    region: str = "CN",
    language: str = "zh",
) -> tuple:
    """构造 news_data 表标准行，对齐 ClickHouse schema。

    自动计算 news_id（MD5 of source+title+publish_time），
    解析 pub_date 为标准 DateTime 格式。

    Args:
        pub_date: 发布时间（各种格式，RSS/JSON/API 原始值）
        title: 标题
        link: 原文链接 → source_url
        summary: 摘要/内容 → 同时填入 content 和 summary
        source: 来源标识
        data_source: 数据源名称（Provider 的 source_name）
        region: 区域标记（默认 CN；海外源应传 US/HK/TW 等，
            #ARCH-RSS-INVESTING-403-001：避免海外新闻被表 DEFAULT 误标 CN）
        language: 语言标记（默认 zh；英文源应传 en）

    Returns:
        tuple: (news_id, publish_time, title, content, summary, source,
                source_url, data_source, region, language)
    """
    publish_time = _parse_datetime(str(pub_date))
    title_str = str(title) or ""
    content_str = str(summary) or ""
    summary_str = str(summary) or ""
    source_str = str(source) or ""
    source_url_str = str(link) or ""
    data_source_str = str(data_source) or ""
    region_str = str(region) or "CN"
    language_str = str(language) or "zh"

    news_id = hashlib.md5(f"{source_str}{title_str}{publish_time}".encode("utf-8")).hexdigest()

    return (
        news_id,
        publish_time,
        title_str,
        content_str,
        summary_str,
        source_str,
        source_url_str,
        data_source_str,
        region_str,
        language_str,
    )


def _title_hash(title: str) -> str:
    """计算标题的 MD5 哈希。

    对标题做 strip + lower 处理后计算 MD5，
    消除首尾空格和大小写差异导致的重复。
    """
    normalized = title.strip().lower()
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def _get_existing_hashes(days: int = _DEDUP_WINDOW_DAYS) -> set[str]:
    """查询最近 N 天已有新闻的标题哈希集合。

    Returns:
        标题 MD5 哈希集合，查询失败时返回空集合（fail-open）。
    """
    sql = _SQL_DEDUP_QUERY_TEMPLATE.format(days=days)
    result = ch_reader.query(sql)
    if not result:
        return set()
    hashes: set[str] = set()
    for line in result.strip().split("\n"):
        if line:
            hashes.add(_title_hash(line))
    return hashes


def dedup_news_result(result: FetchResult) -> FetchResult:
    """对 FetchResult 中的新闻数据去重。

    基于 title 的 MD5 哈希，过滤掉已存在于 ClickHouse 中的重复新闻。
    同时过滤同一批次内的重复新闻。

    Args:
        result: 原始 FetchResult，rows 格式为 NEWS_DATA_COLUMNS 对应的 tuple

    Returns:
        去重后的 FetchResult（替换 rows 和 rows_fetched）
    """
    if not result.rows:
        return result

    try:
        existing_hashes = _get_existing_hashes()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.warning("查询已有新闻哈希失败，跳过去重: %s", e)
        return result

    seen_hashes: set[str] = set()
    deduped_rows: list[tuple] = []
    skipped = 0

    for row in result.rows:
        title = str(row[_TITLE_INDEX]) if len(row) > _TITLE_INDEX else ""
        h = _title_hash(title)
        if h in existing_hashes or h in seen_hashes:
            skipped += 1
            continue
        seen_hashes.add(h)
        deduped_rows.append(row)

    if skipped > 0:
        log.info(
            "新闻去重: 原始 %d 行 -> 去重后 %d 行（跳过 %d 条重复）",
            len(result.rows),
            len(deduped_rows),
            skipped,
        )

    return FetchResult(
        table=result.table,
        columns=result.columns,
        rows=deduped_rows,
        last_key=result.last_key,
        elapsed_sec=result.elapsed_sec,
        rows_fetched=len(deduped_rows),
        error=result.error,
    )
