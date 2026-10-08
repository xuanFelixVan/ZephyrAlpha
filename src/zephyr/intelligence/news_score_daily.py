# [BLUEPRINT] MOD-INT-NEWS-SCORE-DAILY | docs/_working/emotion_line/gap_list_and_construction_proposal.md §5-S5（情绪线延伸件）
# [MODULE] zephyr.intelligence.news_score_daily
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.news_sentiment_analyzer（RuleBasedSentimentScorer 打分口径单源 + caliber_fingerprint 版本指纹单点）;
#                zephyr.data.ch_writer (strict 写通道); zephyr.infrastructure.database_service (reader);
#                zephyr.data.table_registry; zephyr.data.progress_store (断点续传统一范式)
# [CONSUMERS] c3_fundamental.news_sentiment_score（逐条情绪分，日更+回补唯一生产者）
#             → PQ-0016/0181/0036/0084 复考 / 下游情绪特征消费
# [STARTUP] manual + scheduler(nightly_news_score 08:50 日频, 2026-10-04 EXEC-2b 接线)
# [MATURITY] experimental
# [INVARIANTS] 口径单源：打分一律经在册 RuleBasedSentimentScorer，禁本件另实现情绪口径（第二真源）；
#              caliber_version 一律经本件 caliber_fingerprint()（词典/正则真源=analyzer 模块级
#              常量，算法与 wo_a2legs 冻结回填件同款，禁本件另设第二指纹口径）；
#              幂等：ReplacingMergeTree(ingest_ts) 同键 (caliber_version,news_id,publish_time) 替换，
#              重跑/补跑/回扫不产生重复行；只读 news_data（FINAL 去重）零改写母表；
#              服务总闸=data/runtime/news_score_daily.disabled（调度层每次触发实查，同 nightly_sentiment 惯例）；
#              断点续传=ProgressStore 统一范式（task_id=news_sentiment_score_daily/backfill，last_key=最后完成日）。
# [WRITE_DISCIPLINE] 纯 INSERT 派生分表；禁 UPDATE/DELETE/DROP news_data 与本表（回滚=DROP 本表，需 Owner 门位）。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单日失败进 failed 列表继续（fail-visible）；CH 不可达→ok=False 由调度层降级
#                  alerter 告警（不炸调度器）；本件零抛出（CLI 末行 JSON 汇总，有错非零退出）。
# [TESTS] tests/intelligence/test_news_score_daily.py（reader/client/store 全注入，tmp_path 隔离）
# [A_module] module_id=MOD-INT-NEWS-SCORE-DAILY | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""news_score_daily — news_sentiment_score 日更+缺口回补生产者（EXEC-2b P0 止血接线，2026-10-04）。

背景（断供根因，探针已核）：c3_fundamental.news_sentiment_score 7,733,898 行止 2025-09-09
（scored_at=2026-09-24），唯一写入口是 wo_a2legs 一次性回填件（硬编码 CUT=2025-09-09，
task_bound 已冻结）——表建成即无日更生产者，2025-09-10 起 13 个月断供；原料 news_data
（FINAL）鲜至当日。本件补生产者位：日更增量 + 任意区间回补（同一打分/落表路径，零口径分叉）。

口径：规则法单源（与存量 7.7M 行 method='rule' / caliber rule-a0e3f2b6d3 无缝续写；
已探针核实指纹逐字节一致）。LLM 轨不接入本件（nightly_sentiment_llm 对照期仅作用于
news_sentiment_window；逐条分表若切 LLM 须 Owner 门位+口径评审，见模块头 INVARIANTS）。

用法：
    python -m zephyr.intelligence.news_score_daily --daily                    # 日更（调度同款）
    python -m zephyr.intelligence.news_score_daily --backfill \
        --start 2025-09-10 --end 2026-10-03 [--redo] [--limit N]              # 区间回补（断点续传）

# [ALGO_FLOW] external: docs/03_modules/_domain_intelligence/algo_flow/news_score_daily.yaml
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, timedelta

from zephyr.data.table_registry import TableRegistry
from zephyr.intelligence.news_sentiment_analyzer import (
    _NEG_REVERSAL_PATTERN,
    _NEGATIVE_KEYWORDS,
    _POSITIVE_KEYWORDS,
    _ST_PATTERN,
    RuleBasedSentimentScorer,
)

__all__: list[str] = ["caliber_fingerprint", "run_news_score_batch", "run_backfill", "score_day"]

# 事件触发：scheduler.py nightly_news_score 臂 08:50 日频调用 run_news_score_batch()（事件驱动非 manual）
_EVENT_TRIGGER = "scheduler.nightly_news_score"


def caliber_fingerprint() -> str:
    """口径版本指纹=词典集+反转/ST 规则正则原文（任一变更即新版本，旧版本行不覆写）。

    算法与 wo_a2legs 冻结回填件（scripts/governance/meta_question/wo_a2legs/
    backfill_news_sentiment.py）逐字节同款；词典/正则真源=analyzer 模块级常量，
    本件零复制零旁路——产出口径 rule-a0e3f2b6d3 与存量 7.7M 行无缝续写。
    """
    h = hashlib.sha256()
    for part in (
        sorted(_POSITIVE_KEYWORDS),
        sorted(_NEGATIVE_KEYWORDS),
        [_NEG_REVERSAL_PATTERN.pattern],
        [_ST_PATTERN.pattern],
    ):
        h.update(",".join(part).encode("utf-8"))
        h.update(b"\x1f")
    return "rule-" + h.hexdigest()[:10]


# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024：禁硬编码全限定表名）
_T_NEWS_DATA = TableRegistry().table("fund_news_data")
_TARGET_TABLE = TableRegistry().table("news_sentiment_score")

_INSERT_COLUMNS = (
    "news_id, publish_time, polarity, label, n_pos, n_neg, hits, method, "
    "caliber_version, source_table, scored_at, ingest_ts"
)

# NO-BARE-SQL：SQL 集中模块级常量（§5.160.2）；日为运行期入参（score_day 入口经
# date.fromisoformat 严格校验后才允许 format，防注入）
_SQL_DAY_SELECT = (
    f"SELECT news_id, publish_time, title, content FROM {_T_NEWS_DATA} FINAL "
    "WHERE toDate(publish_time) = '{day}' ORDER BY publish_time"
)
_SQL_COVERED_DAYS = (
    f"SELECT DISTINCT toDate(publish_time) FROM {_TARGET_TABLE} "
    "WHERE caliber_version = '{caliber}' AND publish_time >= '{since}'"
)
_SQL_INSERT = f"INSERT INTO {_TARGET_TABLE} ({_INSERT_COLUMNS}) VALUES"

BATCH = 50_000  # 单批插行数（与 wo_a2legs 回填件同量级）
TASK_DAILY = "news_sentiment_score_daily"
TASK_BACKFILL = "news_sentiment_score_backfill"


def _score_rows(rows: list[tuple], scorer: RuleBasedSentimentScorer, caliber: str) -> tuple[list[list], int]:
    """纯打分变换：母表行 → 插入行（列序=_INSERT_COLUMNS）。返回 (rows, non_zero)。

    独立成函数便于注入测试（不触 DB）；打分一律经 scorer.score 单一口径。
    """
    from zephyr.shared.utils.time_utils import now_utc

    now = now_utc()
    out: list[list] = []
    nz = 0
    pos_set = scorer._pos
    for nid, pt, title, content in rows:
        polarity, hits = scorer.score(title or "", content or "")
        label = "positive" if polarity > 0 else ("negative" if polarity < 0 else "neutral")
        if polarity != 0:
            nz += 1
        n_pos = sum(1 for k in hits if k in pos_set)
        out.append(
            [
                str(nid),
                pt,
                float(polarity),
                label,
                n_pos,
                len(hits) - n_pos,
                "|".join(hits)[:200],
                "rule",
                caliber,
                _T_NEWS_DATA,
                now,
                now,
            ]
        )
    return out, nz


def _iso(day: str) -> str:
    """日参严格校验（ISO YYYY-MM-DD），通过后原样返回（SQL format 前置闸）。"""
    return date.fromisoformat(day).isoformat()


def score_day(
    client: object,
    reader: object,
    scorer: RuleBasedSentimentScorer,
    day: str,
    caliber: str,
    *,
    limit: int = 0,
) -> dict[str, int]:
    """单日分片：读母表当日行 → 打分 → 批量插（ReplacingMergeTree 同键幂等）。"""
    day = _iso(day)
    sql = _SQL_DAY_SELECT.format(day=day)
    if limit:
        sql += f" LIMIT {int(limit)}"
    rows = reader.execute(sql)
    inserted, nz = 0, 0
    for i in range(0, len(rows), BATCH):
        chunk, non_zero = _score_rows(rows[i : i + BATCH], scorer, caliber)
        nz += non_zero
        if chunk:
            client.execute(_SQL_INSERT, chunk, types_check=True)
            inserted += len(chunk)
    return {"rows_in": len(rows), "rows_written": inserted, "non_zero": nz}


def _covered_days(reader: object, caliber: str, since: str) -> set[str]:
    """已覆盖发布日集合（当日有落表行才算覆盖；空新闻日天然无需覆盖）。"""
    return {str(r[0]) for r in reader.execute(_SQL_COVERED_DAYS.format(caliber=caliber, since=since))}


def _day_range(start: date, end: date) -> list[str]:
    out: list[str] = []
    d = start
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def run_news_score_batch(
    *,
    lookback: int = 30,
    retrail_days: int = 2,
    client: object = None,
    reader: object = None,
    store: object = None,
) -> dict[str, object]:
    """日频调度入口（schedule nightly_news_score）：近 lookback 日缺口补跑 + 近 retrail 日增量重扫。

    - 覆盖判定按 caliber_version 发布日差集；缺口日逐日 score_day（幂等，可安全重跑）；
    - retrail 重扫近 N 日：吸收 SCD 晚到版本/晚发新闻（同键替换，零重复）；
    - 永不抛（单日失败进 failed 继续）；CH 不可达整体 ok=False 交调度层降级告警；
    - client/reader/store 可注入（测试 mock）；None=ch_writer/DatabaseService/ProgressStore 正门。
    """
    today = date.today()
    result: dict[str, object] = {
        "ok": False,
        "scored": [],
        "failed": [],
        "rows": 0,
        "skipped": 0,
        "caliber_version": caliber_fingerprint(),
    }
    try:
        if client is None:
            from zephyr.data.ch_writer import get_client

            client = get_client()
        if reader is None:
            from zephyr.infrastructure.database_service import DatabaseService

            reader = DatabaseService().get_clickhouse_conn(role="reader")
        if store is None:
            from zephyr.data.progress_store import get_store

            store = get_store()
    except Exception as exc:  # noqa: BLE001 — 依赖不可达整体降级
        result["failed"].append(f"deps:{exc}")
        return result

    since = (today - timedelta(days=lookback)).isoformat()
    try:
        covered = _covered_days(reader, result["caliber_version"], since)
    except Exception as exc:  # noqa: BLE001 — 读侧故障整体降级
        result["failed"].append(f"ch_read:{exc}")
        return result

    gap = [d for d in _day_range(today - timedelta(days=lookback), today) if d not in covered]
    retrail = [(today - timedelta(days=k)).isoformat() for k in range(1, retrail_days + 1)]
    days = sorted(set(gap) | set(retrail))
    result["skipped"] = max(0, lookback + 1 - len(gap))

    scorer = RuleBasedSentimentScorer()
    for day in days:
        try:
            stat = score_day(client, reader, scorer, day, result["caliber_version"])
            result["scored"].append(day)
            result["rows"] += stat["rows_written"]
            store.save_progress(TASK_DAILY, "internal", day, "SUCCESS", rows_total=stat["rows_written"])
        except Exception as exc:  # noqa: BLE001 — 单日失败继续
            result["failed"].append(f"{day}:{type(exc).__name__}:{str(exc)[:120]}")
            store.save_progress(TASK_DAILY, "internal", day, "FAILED", error_msg=str(exc)[:200])
    result["ok"] = not result["failed"]
    return result


def run_backfill(
    start: str,
    end: str,
    *,
    redo: bool = False,
    limit: int = 0,
    client: object = None,
    reader: object = None,
    store: object = None,
) -> dict[str, object]:
    """区间回补（断点续传）：[start, end] 发布日逐日打分落表，ProgressStore last_key 续跑。

    断点协议（§7.2）：启动读 last_key（=最后完成日）→ 严格大于 last_key 的日才跑；
    每日落库即 save_progress；异常中断后重启自动续传。已覆盖日（CH 差集）默认跳过，
    --redo 强制全量重灌（同键替换仍幂等）。
    """
    result: dict[str, object] = {
        "ok": False,
        "start": start,
        "end": end,
        "scored": [],
        "failed": [],
        "skipped": 0,
        "rows": 0,
        "caliber_version": caliber_fingerprint(),
    }
    try:
        if client is None:
            from zephyr.data.ch_writer import get_client

            client = get_client()
        if reader is None:
            from zephyr.infrastructure.database_service import DatabaseService

            reader = DatabaseService().get_clickhouse_conn(role="reader")
        if store is None:
            from zephyr.data.progress_store import get_store

            store = get_store()
        last_key = store.get_last_key(TASK_BACKFILL)
    except Exception as exc:  # noqa: BLE001 — 依赖不可达整体降级
        result["failed"].append(f"deps:{exc}")
        return result

    days = _day_range(date.fromisoformat(start), date.fromisoformat(end))
    scorer = RuleBasedSentimentScorer()
    run_id = store.start_run(TASK_BACKFILL)
    total = 0
    if not redo:
        # 已覆盖日（CH 差集）跳过：与日更/前次回补续写幂等衔接，省重灌
        try:
            covered = _covered_days(reader, result["caliber_version"], start)
            days = [d for d in days if d not in covered]
            result["skipped"] = len(_day_range(date.fromisoformat(start), date.fromisoformat(end))) - len(days)
        except Exception:  # noqa: BLE001 — 覆盖查询失败不阻断（退化为全量重灌，同键幂等兜底）
            covered = set()
    else:
        covered = set()
    for day in days:
        if not redo and last_key and day <= last_key:
            result["skipped"] += 1
            continue
        try:
            stat = score_day(client, reader, scorer, day, result["caliber_version"], limit=limit)
            result["scored"].append(day)
            total += stat["rows_written"]
            result["rows"] = total
            store.save_progress(TASK_BACKFILL, "internal", day, "SUCCESS", rows_total=total)
            print(json.dumps({"day": day, **stat}, ensure_ascii=False), flush=True)
        except Exception as exc:  # noqa: BLE001 — 单日失败记账继续
            result["failed"].append(f"{day}:{type(exc).__name__}:{str(exc)[:120]}")
            store.save_progress(TASK_BACKFILL, "internal", day, "FAILED", rows_total=total, error_msg=str(exc)[:200])
    if run_id:
        store.finish_run(run_id, "SUCCESS" if not result["failed"] else "FAILED", rows_written=total)
    result["ok"] = not result["failed"]
    return result
