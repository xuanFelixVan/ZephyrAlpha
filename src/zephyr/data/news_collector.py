# [MODULE] zephyr.data.news_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] pandas; zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.regime.features.regime_data_loader
# [CONSUMERS] scripts/ml/build_eval_set.py; P1-E3 NLP 管道
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 查询 fund_news_data 表，返回标准列 DataFrame；PIT 严格（publish_time <= 指定截止时间）
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_data/news_collector/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] NewsCollectorError(ZA-DATA-0020)
# [TESTS] tests/data/test_news_collector.py
# [A_module] module_id=MOD-DATA-NEWS-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-NLP-PIPELINE-001 Phase 1

"""MOD-DATA-NEWS-001 NewsCollector — 新闻数据采集器。

从 ClickHouse ``fund_news_data`` 表按条件查询新闻，返回标准列 DataFrame。
供 P1-E3 NLP 管道（评估集构建、批量推理）使用。

设计原则：
- 复用 ``ch_reader.query()`` + ``regime_data_loader.parse_tsv``，不重复造 TSV 解析轮子
- 列顺序对齐 ``news_dedup.NEWS_DATA_COLUMNS``
- PIT 严格：``publish_time <= end_date``，不泄漏未来新闻

依据: P1-E3_NLP管道架构裁定与施工方案.md Phase 1
SSoT: depgraph MOD-DATA-NEWS-001
Version: 0.1.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Final

import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.regime.features.regime_data_loader import parse_tsv

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# fund_news_data 表名（经 table_registry 解析）
_TBL_NEWS: Final[str] = get_registry().table("fund_news_data")

# 标准查询列（对齐 NEWS_DATA_COLUMNS，供 NLP 处理的核心字段）
_NEWS_QUERY_COLUMNS: Final[list[str]] = [
    "news_id",
    "publish_time",
    "title",
    "content",
    "source",
    "region",
    "language",
]

_NCOLS: Final[int] = len(_NEWS_QUERY_COLUMNS)


class NewsCollectorError(ZephyrBaseError):
    """ZA-DATA-0020: NewsCollector 错误。"""

    error_code = "ZA-DATA-0020"


def collect_news(
    start_date: str,
    end_date: str,
    *,
    region: str = "CN",
    language: str = "zh",
    limit: int = 0,
) -> pd.DataFrame:
    """从 fund_news_data 表采集新闻数据。

    Parameters
    ----------
    start_date : 起始日期（含），格式 'YYYY-MM-DD'。
    end_date   : 截止日期（含），格式 'YYYY-MM-DD'。PIT 严格——不返回此日期之后的新闻。
    region     : 区域过滤，默认 'CN'（A 股）。
    language   : 语言过滤，默认 'zh'。
    limit      : 返回行数上限，0=不限。

    Returns
    -------
    DataFrame，列 = _NEWS_QUERY_COLUMNS，索引 = RangeIndex。
    空结果返回空 DataFrame（仍含正确列名）。

    Raises
    ------
    NewsCollectorError
        日期格式非法或 ClickHouse 查询失败。
    """
    # 参数校验
    for label, date_str in (("start_date", start_date), ("end_date", end_date)):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as exc:
            raise NewsCollectorError(f"{label} 格式非法（期望 YYYY-MM-DD）: {date_str}") from exc

    cols = ", ".join(_NEWS_QUERY_COLUMNS)
    sql = (
        f"SELECT {cols} "
        f"FROM {_TBL_NEWS} "
        f"WHERE region = '{region}' "
        f"AND language = '{language}' "
        f"AND publish_time >= toDateTime('{start_date} 00:00:00') "
        f"AND publish_time <= toDateTime('{end_date} 23:59:59') "
        f"ORDER BY publish_time"
    )
    if limit > 0:
        sql += f" LIMIT {limit}"

    _logger.info(
        "collect_news: querying %s from %s to %s (region=%s, lang=%s, limit=%s)",
        _TBL_NEWS, start_date, end_date, region, language, limit or "unlimited",
    )

    tsv = ch_reader.query(sql)
    if not tsv or not tsv.strip():
        _logger.warning("collect_news: 查询返回空结果 (%s ~ %s)", start_date, end_date)
        return pd.DataFrame(columns=_NEWS_QUERY_COLUMNS)

    rows = parse_tsv(tsv, ncols=_NCOLS)
    if not rows:
        return pd.DataFrame(columns=_NEWS_QUERY_COLUMNS)

    df = pd.DataFrame(rows, columns=_NEWS_QUERY_COLUMNS)
    # publish_time 转 datetime
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    _logger.info("collect_news: 采集到 %d 条新闻", len(df))
    return df


def collect_news_by_ids(news_ids: list[str]) -> pd.DataFrame:
    """按 news_id 列表精确查询新闻（供评估集回溯验证用）。

    Parameters
    ----------
    news_ids : news_id 字符串列表。

    Returns
    -------
    DataFrame，列同 ``collect_news``。
    """
    if not news_ids:
        return pd.DataFrame(columns=_NEWS_QUERY_COLUMNS)

    cols = ", ".join(_NEWS_QUERY_COLUMNS)
    # ClickHouse IN 语法
    id_list = ", ".join(f"'{nid}'" for nid in news_ids)
    sql = f"SELECT {cols} FROM {_TBL_NEWS} WHERE news_id IN ({id_list}) ORDER BY publish_time"

    tsv = ch_reader.query(sql)
    if not tsv or not tsv.strip():
        return pd.DataFrame(columns=_NEWS_QUERY_COLUMNS)

    rows = parse_tsv(tsv, ncols=_NCOLS)
    df = pd.DataFrame(rows, columns=_NEWS_QUERY_COLUMNS)
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    return df


__all__: Final = ["NewsCollectorError", "collect_news", "collect_news_by_ids"]
