# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-W5 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0016/0181/0036/0084)
# [MODULE] scripts.governance.meta_question.wo_a2legs.build_news_sentiment_window
# [DOMAIN] D_DATA
# [DEPENDENCIES] c3_fundamental.news_sentiment_score（WO-A2LEGS 派生分数表）;
#                 zephyr.data.ch_writer (strict 写通道); zephyr.infrastructure.database_service (reader);
#                 zephyr.shared.utils.time_utils (RULE-SCHEMA-TZ：禁裸 datetime.now)
# [CONSUMERS] c1_market.news_sentiment_window 历史段（window_type='1d', scope='market'）
#             → PQ-0016/0181 日度情感分位 vs 次日全A中位数收益；PQ-0036/0084 与资金流互相关
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 写面三验证：必要性=news_sentiment_window 现表起点 2026-02-24（切点前 0 行）而闭卷窗复考需
#              2010~2025 日度序列；真实性=仅聚合已回填的逐条分数（母表 news_data 100% 覆盖已核 0 缺失），
#              聚合口径逐字对齐生产 SentimentAggregator（sentiment_index=窗口平均极性）与本表 DDL 注释
#              （total_count=news_id 去重后条数，防 SCD 修正稿膨胀）；可逆性=只 INSERT 新键
#              （window_type='1d' 为全新取值，既有 night/1h 行零触碰），回滚=按新键 DELETE 本批（登记不执行）；
#              禁 UPDATE/覆写既有行、禁 DROP；MATERIALIZED 列（window_date/exchange/symbol_canonical）禁入列清单；
#              PIT=仅取 publish_time<=2025-09-09，归属日=发布时戳自然日（Asia/Shanghai），无未来信息；
#              幂等=同 (scope,symbol,window_type,window_ts) 键重跑前先探已存在则跳过该日。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无分数分区→打印空报告退出 0；写后复核不过→SystemExit(6) fail-visible。
# [TESTS] 无（数据施工脚本，验收=CH 探针复核：日覆盖/与分数表逐日条数对账）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-W5 | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""按发布时戳 PIT 生成 c1_market.news_sentiment_window 历史日度段（服务端聚合，零数据搬运）。

用法：
    python .../build_news_sentiment_window.py --start 2010-01-01 --end 2025-09-09 [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

SCORE = "c3_fundamental.news_sentiment_score"
#: 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
WIN = TableRegistry().table("market_news_sentiment_window")
CUT = date(2025, 9, 9)
WINDOW_TYPE = "1d"

# 非 MATERIALIZED 列清单（window_date/exchange/symbol_canonical 为派生列，禁入——Code 44）
WIN_COLS = [
    "window_ts",
    "window_end",
    "window_type",
    "scope",
    "symbol",
    "sentiment_index",
    "avg_polarity",
    "positive_count",
    "negative_count",
    "neutral_count",
    "total_count",
    "top_events_json",
    "data_source",
    "ingest_ts",
]

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{WIN}/{WINDOW_TYPE}/WIN_COLS 由模块常量注入；
# new_days 的 PIT 日期用 %s 占位由调用方传入，禁把日期字面量写进常量。
_SQL_HAVE_DAYS = f"SELECT DISTINCT toDate(window_ts) FROM {WIN} WHERE window_type='{WINDOW_TYPE}'"
_SQL_INSERT_VALUES = f"INSERT INTO {WIN} ({', '.join(WIN_COLS)}) VALUES"
_SQL_ONE = (
    f"SELECT count(), min(window_ts), max(window_ts), sum(total_count) FROM {WIN} FINAL "
    f"WHERE window_type='{WINDOW_TYPE}'"
)
_SQL_DAYS_1D = f"SELECT uniqExact(toDate(window_ts)) FROM {WIN} WHERE window_type='{WINDOW_TYPE}'"
_SQL_NEW_DAYS = (
    f"SELECT uniqExact(toDate(window_ts)) FROM {WIN} FINAL WHERE window_type='{WINDOW_TYPE}' "
    "AND window_ts >= date'%s' AND window_ts < date'%s'"
)
_SQL_NIGHT_ROWS = f"SELECT count() FROM {WIN} WHERE window_type='night'"


def _sql_agg(caliber: str, start: date, end: date) -> str:
    """字面量拼式（caliber 经白名单正则校验、日期由 date 对象产出，无注入面）。

    本 CH 版本对 `{name:Type}` 查询参数在 CTE 内替换会抛 Code 456（实测），故走字面量。
    """
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", caliber):
        raise SystemExit(f"caliber 非法：{caliber!r}")
    return f"""
WITH dedup AS (
    SELECT toDate(publish_time, 'Asia/Shanghai') AS d,
           news_id,
           argMin(polarity, publish_time) AS pol
    FROM {SCORE} FINAL
    WHERE caliber_version = '{caliber}'
      AND publish_time >= date'{start.isoformat()}' AND publish_time <= date'{end.isoformat()}'
    GROUP BY d, news_id
)
SELECT d,
       avg(pol)                                        AS sentiment_index,
       countIf(pol > 0)                                AS pos,
       countIf(pol < 0)                                AS neg,
       countIf(pol = 0)                                AS neu,
       count()                                         AS tot
FROM dedup GROUP BY d ORDER BY d
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2010-01-01")
    ap.add_argument("--end", default=CUT.isoformat())
    ap.add_argument("--caliber", default="rule-a0e3f2b6d3")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    end = min(date.fromisoformat(args.end), CUT)  # PIT 硬上限：闭卷切点
    start = date.fromisoformat(args.start)
    reader = DatabaseService().get_clickhouse_conn(role="reader")
    rows = reader.execute(_sql_agg(args.caliber, start, end))
    if not rows:
        print(json.dumps({"days": 0, "note": "该窗内无已回填分数"}, ensure_ascii=False))
        return
    have = {str(r[0]) for r in reader.execute(_SQL_HAVE_DAYS)}
    ing = now_utc()
    payload = []
    for d, sidx, pos, neg, neu, tot in rows:
        if str(d) in have:
            continue
        ts = f"{d} 00:00:00"
        payload.append(
            [
                ts,
                str(d + timedelta(days=1)),
                WINDOW_TYPE,
                "market",
                "",
                float(sidx),
                float(sidx),
                int(pos),
                int(neg),
                int(neu),
                int(tot),
                "",
                "rule",
                ing,
            ]
        )
    if args.dry_run:
        print(
            json.dumps(
                {
                    "days_agg": len(rows),
                    "days_to_insert": len(payload),
                    "days_already_present": len(rows) - len(payload),
                },
                ensure_ascii=False,
            )
        )
        return
    if payload:
        ch_writer.get_client().execute(_SQL_INSERT_VALUES, payload, types_check=True)
    one = reader.execute(_SQL_ONE)[0]
    days_1d = reader.execute(_SQL_DAYS_1D)[0][0]
    new_days = reader.execute(_SQL_NEW_DAYS % (start.isoformat(), (end + timedelta(days=1)).isoformat()))[0][0]
    ok = one[0] > 0 and new_days > 0
    print(
        json.dumps(
            {
                "inserted": len(payload),
                "window_1d_rows": one[0],
                "window_1d_days": days_1d,
                "window_1d_news_total": one[3],
                "range": [str(one[1]), str(one[2])],
                "days_in_requested_range": new_days,
                "night_rows_untouched": reader.execute(_SQL_NIGHT_ROWS)[0][0],
                "verify": "PASS" if ok else "FAIL",
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    if not ok:
        raise SystemExit(6)


if __name__ == "__main__":
    main()
