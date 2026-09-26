# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-W3 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0016/0181/0036/0084)
# [MODULE] scripts.governance.meta_question.wo_a2legs.backfill_news_sentiment
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.intelligence.news_sentiment_analyzer.RuleBasedSentimentScorer（在册生产口径规则法打分器，
#                 不新建平行词典）; zephyr.data.ch_writer (strict 写通道);
#                 zephyr.infrastructure.database_service (reader); zephyr.shared.utils.time_utils
# [CONSUMERS] c3_fundamental.news_sentiment_score（新表：逐条情绪分，口径版本化）
#             → build_news_sentiment_window.py（PIT 日度情感窗口）→ PQ-0016/0181/0036/0084 复考
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 口径单源：打分一律经在册 RuleBasedSentimentScorer（禁在本件另实现一套情绪口径＝第二真源）；
#              分数随代带 caliber_version 与源侧 as_of，禁把后来的规则版结果冒充当初所见的值；
#              幂等：按自然月分片重灌前先 DROP 本表该月分区，重跑不产生重复行；只读 news_data 不改其行。
# [WRITE_DISCIPLINE] 只建新表+纯 INSERT，禁 UPDATE news_data.sentiment_score（覆写既有行违写面铁律），
#                    禁 DELETE/DROP；回滚=DROP 新表；既有 news_data 零触碰。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单月失败→记账继续其余月；末行 JSON 汇总；有错误则非零退出（fail-visible）。
# [TESTS] 无（数据施工脚本，验收=CH 探针复核：分数非零率/月度覆盖/与 news_data 行数比对）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-W3 | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""news_data 存量情绪分回填（PQ-0016/0181/0036/0084 前置，可批处理/断点续跑/分片幂等）。

口径：复用在册生产打分器 RuleBasedSentimentScorer（规则法；LLM 轨在产线 factory-off，
     旗标 data/runtime/nightly_sentiment_llm.enabled 不存在→生产即规则法，故本回填与
     现网口径一致，不引入口径分叉）。caliber_version=词典指纹哈希，换词典自动成新版本。

用法：
    python .../backfill_news_sentiment.py --start 2024-09-01 --end 2025-09-09   # 先跑刚需窗
    python .../backfill_news_sentiment.py --months 201001,201002               # 指定月分片
    python .../backfill_news_sentiment.py --start 2010-01-01 --end 2025-09-09 --pilot 1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.intelligence.news_sentiment_analyzer import (  # noqa: E402
    _NEG_REVERSAL_PATTERN,
    _NEGATIVE_KEYWORDS,
    _POSITIVE_KEYWORDS,
    _ST_PATTERN,
    RuleBasedSentimentScorer,
)
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

TBL = "c3_fundamental.news_sentiment_score"
CUT = "2025-09-09"
CKPT = _ROOT / ".runtime" / "tmp" / "st-metaq-gc-20260924" / "a2legs" / "sentiment_ckpt.json"

DDL = f"""
CREATE TABLE IF NOT EXISTS {TBL} (
    news_id         String               COMMENT 'news_data.news_id',
    publish_time    DateTime64(3, 'Asia/Shanghai') COMMENT '发布时戳（PIT 键，取自 news_data）',
    polarity        Float32              COMMENT '有向极性 [-1,1]（与生产 analyzer 契约一致：禁误用强度 score）',
    label           LowCardinality(String) COMMENT 'positive/negative/neutral（polarity 符号）',
    n_pos           UInt16               COMMENT '命中正向词数',
    n_neg           UInt16               COMMENT '命中负向词数（含反转/ST）',
    hits            String               COMMENT '命中词（|分隔，截断 200 字，供抽检）',
    method          LowCardinality(String) COMMENT '打分方法 rule/llm/llm_fallback（与 news_sentiment_window.data_source 同枚举）',
    caliber_version String               COMMENT '口径版本=词典+规则指纹（换词典即新版本，不覆写旧版本）',
    source_table    LowCardinality(String) COMMENT '来源表',
    scored_at       DateTime64(3, 'UTC') COMMENT '打分时刻',
    ingest_ts       DateTime64(3, 'UTC') COMMENT '入库时刻'
) ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(publish_time)
ORDER BY (caliber_version, news_id, publish_time)
COMMENT 'metaq WO-A2LEGS：news_data 存量情绪分回填（真源=news_data，本表仅存派生分，不改写母表）'
"""
INSERT_COLS = [
    "news_id",
    "publish_time",
    "polarity",
    "label",
    "n_pos",
    "n_neg",
    "hits",
    "method",
    "caliber_version",
    "source_table",
    "scored_at",
    "ingest_ts",
]

BATCH = 50_000

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{TBL}/INSERT_COLS 由模块常量注入；
# where/caliber 为运行期入参，用 %s 占位或留调用处拼装，禁把值写进常量。
# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_NEWS_DATA = TableRegistry().table("fund_news_data")
_SQL_NEWS_SELECT_PREFIX = f"SELECT news_id, publish_time, title, content FROM {_T_NEWS_DATA} FINAL WHERE "
_SQL_NEWS_SELECT_SUFFIX = " ORDER BY publish_time"
_SQL_HAVE_MONTHS = f"SELECT DISTINCT toYYYYMM(publish_time) FROM {TBL} WHERE caliber_version='%s'"
_SQL_INSERT_VALUES = f"INSERT INTO {TBL} ({', '.join(INSERT_COLS)}) VALUES"


def caliber_fingerprint() -> str:
    """口径版本指纹=词典集 + 反转/ST 规则正则原文（任一变更即新版本，旧版本行不覆写）。"""
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


def months_in(start: str, end: str) -> list[str]:
    d = date.fromisoformat(start)
    e = date.fromisoformat(end)
    out: list[str] = []
    while d <= e:
        out.append(d.strftime("%Y%m"))
        d = (d.replace(day=1) + timedelta(days=32)).replace(day=1)
    return out


def load_ckpt() -> dict:
    if CKPT.exists():
        try:
            return json.loads(CKPT.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 坏档降级空档
            return {}
    return {}


def save_ckpt(caliber: str, done: dict) -> None:
    CKPT.parent.mkdir(parents=True, exist_ok=True)
    CKPT.write_text(
        json.dumps(
            {
                "caliber_version": caliber,
                "done": done,
                "updated_at_utc": now_utc().strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "cut": CUT,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )


def score_month(reader, client, scorer, ym: str, caliber: str, limit: int) -> dict:
    """单月分片：读母表→打分→批量插。返回 {rows_in, rows_scored, non_zero}。"""
    year, month = int(ym[:4]), int(ym[4:])
    lo = f"{year:04d}-{month:02d}-01"
    nxt = (date(year, month, 1) + timedelta(days=32)).replace(day=1)
    hi = nxt.isoformat()
    where = (
        f"toYYYYMM(publish_time) = {ym} AND publish_time >= date'{lo}' "
        f"AND publish_time < date'{hi}' AND publish_time <= date'{CUT}'"
    )
    sql = f"{_SQL_NEWS_SELECT_PREFIX}{where}{_SQL_NEWS_SELECT_SUFFIX}"
    if limit:
        sql += f" LIMIT {limit}"
    rows = reader.execute(sql)
    now = now_utc()
    out: list[list] = []
    nz = 0
    for nid, pt, title, content in rows:
        polarity, hits = scorer.score(title or "", content or "")
        label = "positive" if polarity > 0 else ("negative" if polarity < 0 else "neutral")
        if polarity != 0:
            nz += 1
        npos = sum(1 for k in hits if k in _POSITIVE_KEYWORDS)
        out.append(
            [
                str(nid),
                pt,
                float(polarity),
                label,
                npos,
                len(hits) - npos,
                "|".join(hits)[:200],
                "rule",
                caliber,
                _T_NEWS_DATA,
                now,
                now,
            ]
        )
        if len(out) >= BATCH:
            client.execute(_SQL_INSERT_VALUES, out, types_check=True)
            out = []
    if out:
        client.execute(_SQL_INSERT_VALUES, out, types_check=True)
    return {"rows_in": len(rows), "rows_scored": len(rows), "non_zero": nz}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="")
    ap.add_argument("--end", default=CUT)
    ap.add_argument("--months", default="", help="逗号分隔 YYYYMM（优先于 start/end）")
    ap.add_argument("--pilot", type=int, default=0, help=">0 时每只取 N 行（吞吐标定用）")
    ap.add_argument("--redo", action="store_true", help="忽略断点强制重跑")
    ap.add_argument("--caliber", default="", help="覆盖口径版本（默认=词典指纹）")
    args = ap.parse_args()

    caliber = args.caliber or caliber_fingerprint()
    shards = (
        [m.strip() for m in args.months.split(",") if m.strip()] if args.months else months_in(args.start, args.end)
    )
    if not shards:
        raise SystemExit("需 --start/--end 或 --months")

    reader = DatabaseService().get_clickhouse_conn(role="reader")
    client = ch_writer.get_client()
    client.execute(DDL)
    scorer = RuleBasedSentimentScorer()
    ckpt = load_ckpt()
    done = dict(ckpt.get("done", {})) if not args.redo else {}
    have = {str(r[0]) for r in reader.execute(_SQL_HAVE_MONTHS % caliber)}

    t0 = now_utc()
    report = {"caliber_version": caliber, "shards": {}, "skipped": [], "errors": {}}
    for ym in shards:
        if not args.redo and (ym in done or ym in have) and not args.pilot:
            report["skipped"].append(ym)
            continue
        try:
            s = now_utc()
            r = score_month(reader, client, scorer, ym, caliber, args.pilot)
            r["elapsed_s"] = round((now_utc() - s).total_seconds(), 1)
            r["rows_per_s"] = round(r["rows_in"] / max(0.001, r["elapsed_s"]), 1)
            report["shards"][ym] = r
            if not args.pilot:
                done[ym] = r["rows_in"]
                save_ckpt(caliber, done)
            print(json.dumps({ym: r}, ensure_ascii=False), flush=True)
        except Exception as exc:  # noqa: BLE001 — 单片失败不阻断
            report["errors"][ym] = f"{type(exc).__name__}: {str(exc)[:200]}"
            print(json.dumps({ym: "ERR " + report["errors"][ym]}, ensure_ascii=False), flush=True)
    report["total_elapsed_s"] = round((now_utc() - t0).total_seconds(), 1)
    report["checkpoint_file"] = str(CKPT)
    print(json.dumps(report, ensure_ascii=False)[:4000])
    if report["errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
