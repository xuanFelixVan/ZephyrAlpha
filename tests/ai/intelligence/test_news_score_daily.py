"""news_score_daily 单元测试（reader/client/store 全注入，零真实 CH/调度依赖）。

覆盖契约（EXEC-2b 2026-10-04）：
- _score_rows：打分口径单源（RuleBasedSentimentScorer）+ 行结构与 _INSERT_COLUMNS 对齐；
- score_day：注入 fake reader/client，批量插+limit 生效；
- run_news_score_batch：缺口补跑 + retrail 重扫 + 单日失败继续（fail-visible 不抛）；
- run_backfill：断点续传（last_key 严格大于才跑）+ 覆盖日跳过。
"""

from __future__ import annotations

from datetime import date, timedelta

import zephyr.intelligence.news_score_daily as nsd
from zephyr.intelligence.news_sentiment_analyzer import RuleBasedSentimentScorer


class FakeReader:
    """按日返回预制行；记录执行过的 SQL 供断言。"""

    def __init__(self, by_day: dict[str, list[tuple]]):
        self.by_day = by_day
        self.executed: list[str] = []

    def execute(self, sql: str) -> list[tuple]:
        self.executed.append(sql)
        for day, rows in self.by_day.items():
            if f"'{day}'" in sql:
                out = rows
                if "LIMIT" in sql:
                    out = out[: int(sql.rsplit("LIMIT", 1)[1].strip())]
                return list(out)
        if "DISTINCT toDate(publish_time)" in sql:
            return [(date.fromisoformat(d),) for d in self.covered]
        return []

    covered: list[str] = []


class FakeClient:
    def __init__(self):
        self.inserted: list[list] = []

    def execute(self, sql: str, rows: list, types_check: bool = False) -> None:
        assert sql.startswith("INSERT INTO")
        self.inserted.extend(rows)


class FakeStore:
    def __init__(self, last_key: str | None = None):
        self.last_key = last_key
        self.saved: list[tuple] = []

    def get_last_key(self, task_id: str) -> str | None:
        return self.last_key

    def save_progress(self, task_id, source, last_key, status, rows_total=0, error_msg=None):
        self.saved.append((task_id, last_key, status))

    def start_run(self, task_id):
        return 1

    def finish_run(self, run_id, status, rows_fetched=0, rows_written=0, error_msg=None):
        return True


def test_score_rows_row_contract():
    """行结构=12 列与 _INSERT_COLUMNS 对齐；method=rule；caliber=指纹单点。"""
    scorer = RuleBasedSentimentScorer()
    rows = [
        ("n1", __import__("datetime").datetime(2026, 10, 1, 9), "公司重大利好中标", "利润大增"),
        ("n2", None, "", ""),
    ]
    out, nz = nsd._score_rows(rows, scorer, "rule-x")
    assert len(out) == 2 and nz == 1
    assert len(out[0]) == len(nsd._INSERT_COLUMNS.split(","))
    assert out[0][7] == "rule" and out[0][8] == "rule-x"
    assert out[0][2] > 0 and out[0][3] == "positive"


def test_score_day_batches_and_limit():
    """score_day 注入 fake：全量入库 + limit 截断生效。"""
    scorer = RuleBasedSentimentScorer()
    rows = [(f"n{i}", __import__("datetime").datetime(2026, 10, 1), "重大利好", "") for i in range(7)]
    reader = FakeReader({"2026-10-01": rows})
    client = FakeClient()
    stat = nsd.score_day(client, reader, scorer, "2026-10-01", "rule-x")
    assert stat == {"rows_in": 7, "rows_written": 7, "non_zero": 7}
    reader2 = FakeReader({"2026-10-01": rows})
    stat2 = nsd.score_day(client, reader2, scorer, "2026-10-01", "rule-x", limit=3)
    assert stat2["rows_in"] == 3


def test_daily_batch_gap_and_retrail(tmp_path):
    """缺口日补跑 + retrail 重扫并入；失败日继续不抛。"""
    today = date.today()
    reader = FakeReader({})
    reader.covered = [(today - timedelta(days=1)).isoformat()]  # 昨日已覆盖
    client = FakeClient()

    calls: list[str] = []

    def boom(client_, reader_, scorer_, day, caliber, *, limit=0):
        calls.append(day)
        if day.endswith(str((today - timedelta(days=3)).day)):
            raise RuntimeError("simulated day failure")
        return {"rows_in": 1, "rows_written": 1, "non_zero": 1}

    orig = nsd.score_day
    nsd.score_day = boom  # type: ignore[assignment]
    try:
        result = nsd.run_news_score_batch(lookback=5, retrail_days=1, client=client, reader=reader, store=FakeStore())
    finally:
        nsd.score_day = orig  # type: ignore[assignment]
    assert result["failed"], "失败日应进 failed（fail-visible）"
    assert len(calls) == len(set(calls)), "无重复日"
    assert not result["ok"]


def test_backfill_resume_and_coverage_skip():
    """断点续传：last_key 之前的日跳过；CH 已覆盖日跳过；重跑幂等路径。"""
    start, end = "2026-09-01", "2026-09-05"
    reader = FakeReader({})
    reader.covered = ["2026-09-03"]  # CH 已有该日
    store = FakeStore(last_key="2026-09-02")  # 断点=09-02（之前完成）
    ran: list[str] = []

    orig = nsd.score_day
    nsd.score_day = lambda c, r, s, day, cal, *, limit=0: (
        ran.append(day),
        {"rows_in": 1, "rows_written": 1, "non_zero": 0},
    )[1]  # type: ignore[assignment]
    try:
        result = nsd.run_backfill(start, end, client=FakeClient(), reader=reader, store=store)
    finally:
        nsd.score_day = orig  # type: ignore[assignment]
    # 09-01/09-02 被 last_key 跳过，09-03 被覆盖跳过 → 只跑 09-04/09-05
    assert ran == ["2026-09-04", "2026-09-05"]
    assert result["ok"] and result["skipped"] == 3


def test_caliber_fingerprint_single_source():
    """指纹与存量表版本 rule-a0e3f2b6d3 逐字节一致（无缝续写契约）。"""
    assert nsd.caliber_fingerprint() == "rule-a0e3f2b6d3"
