"""retail_comment_signals 测试（st-infoaxis P2 千股千评首刀）——假 reader 全离线，ch 全 mock。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import pytest  # noqa: E402

import zephyr.alt_data.retail_comment_signals as mod  # noqa: E402
from schemas.categories.market import alt_stock_comment_signal as schema  # noqa: E402
from zephyr.alt_data.retail_comment_signals import (  # noqa: E402
    assemble_signals,
    maybe_emit_retail_comment_signals,
    run_signals,
)

# 母体 std([10,20,30]) = sqrt(200/3)
_PSTDEV = (200.0 / 3.0) ** 0.5

TODAY_3 = "600519.SH\t10.0\t0.1\t70.0\n000001.SZ\t20.0\t0.2\t60.0\n300750.SZ\t30.0\t0.3\t50.0\n"
PRIOR_3 = "600519.SH\t2026-10-12\t5.0\n000001.SZ\t2026-10-12\t25.0\n300750.SZ\t2026-10-12\t20.0\n"


def _q(today="", prior="", fail=False):
    def q(sql: str) -> str:
        if fail:
            raise RuntimeError("down")
        if "max(trade_date)" in sql:
            return prior
        if "alt_stock_comment" in sql:
            return today
        raise AssertionError(sql[:70])

    return q


def test_zscore_math_chg_and_reverse_proxy():
    res = assemble_signals("2026-10-13", ch_query=_q(today=TODAY_3, prior=PRIOR_3))
    by = {r["symbol"]: r for r in res["rows"]}
    assert abs(by["600519.SH"]["attention_z"] - (10 - 20) / _PSTDEV) < 1e-12
    assert abs(by["300750.SZ"]["attention_z"] - (30 - 20) / _PSTDEV) < 1e-12
    assert abs(by["600519.SH"]["attention_chg"] - 5.0) < 1e-12  # 10-5
    assert abs(by["000001.SZ"]["attention_chg"] - (-5.0)) < 1e-12  # 20-25
    assert by["600519.SH"]["retail_sentiment_proxy"] == -70.0  # 反向
    assert by["600519.SH"]["org_participation"] == 0.1  # 透传
    assert by["600519.SH"]["composite_score"] == 70.0
    assert "prior_date=2026-10-12" in by["600519.SH"]["detail"]
    assert "attention_index=10.0" in by["600519.SH"]["detail"]
    assert res["stats"]["zscore_rows"] == 3 and res["stats"]["chg_rows"] == 3
    assert res["stats"]["prior_date"] == "2026-10-12"

    dry = run_signals("2026-10-13", dry_run=True, ch_query=_q(today=TODAY_3, prior=PRIOR_3))
    assert dry["action"] == "dry_run"
    assert "\t600519.SH\t" in dry["tsv"]
    assert "None" not in dry["tsv"]  # 禁把 Python None 字面量写进 TSV


def test_std_guard_null_and_first_day():
    flat = "600519.SH\t50.0\t0.1\t70.0\n000001.SZ\t50.0\t0.2\t60.0\n"
    res = assemble_signals("2026-10-13", ch_query=_q(today=flat))
    assert all(r["attention_z"] is None for r in res["rows"])  # std<1e-9→None
    assert res["stats"]["zscore_rows"] == 0

    nully = "688001.SH\t\\N\t0.4\t\\N\n600519.SH\t30.0\t0.5\t55.0\n"
    res2 = assemble_signals("2026-10-13", ch_query=_q(today=nully))
    by = {r["symbol"]: r for r in res2["rows"]}
    assert by["688001.SH"]["attention_z"] is None  # 原生 NULL 不进横截面
    assert by["688001.SH"]["retail_sentiment_proxy"] is None  # composite NULL→proxy NULL
    assert by["688001.SH"]["attention_chg"] is None
    assert by["600519.SH"]["attention_z"] is None  # 单值横截面 len<2→保护
    assert by["688001.SH"]["detail"] == "attention_index=\\N"  # 原始值留痕（\\N=源 NULL）

    res3 = assemble_signals("2026-10-13", ch_query=_q(today=TODAY_3, prior=""))
    assert all(r["attention_chg"] is None for r in res3["rows"])  # 首日无先值
    assert res3["stats"]["prior_date"] == ""


def test_empty_table_fail_open_and_unreachable():
    res = assemble_signals("2026-10-13", ch_query=_q(today="", prior=""))
    assert res["rows"] == [] and "error" not in res["stats"]  # 空表 fail-open 不报错
    empty = run_signals("2026-10-13", ch_query=_q(today="", prior=""))
    assert empty["action"] == "emitted_empty"

    down = assemble_signals("2026-10-13", ch_query=_q(fail=True))
    assert "不可达" in down["stats"]["error"]  # 禁静默：错误留因
    run_down = run_signals("2026-10-13", ch_query=_q(fail=True))
    assert run_down["action"] == "error" and "不可达" in run_down["error"]


def test_write_port_paren_cols_and_chunking(monkeypatch: pytest.MonkeyPatch):
    big = "\n".join(f"{i:06d}\t{(i % 100) + 1}.0\t0.5\t60.0" for i in range(2500))
    calls: list[tuple[str, str, str]] = []

    def w(table: str, cols: str, tsv: str) -> bool:
        calls.append((table, cols, tsv))
        return True

    res = run_signals("2026-10-13", ch_query=_q(today=big, prior=""), writer=w)
    assert res["action"] == "emitted" and res["signal_rows"] == 2500
    assert all(c[0] == schema.TABLE_NAME for c in calls)
    assert all(c[1] == "(" + ",".join(schema.INSERT_COLUMNS) + ")" for c in calls)  # 写口括号形
    assert all("None" not in c[2] for c in calls)  # 禁 Python None 字面量入 TSV
    first_fields = calls[0][2].split("\n")[0].split("\t")
    assert len(first_fields) == len(schema.INSERT_COLUMNS)

    # 默认写口分块：mock 掉 ch_writer.write_tsv（ch 全 mock 红线），断言 1000 行/块
    ch_calls: list[int] = []

    def fake_write_tsv(table: str, cols: str, body: bytes, *a, **k) -> bool:
        ch_calls.append(len(body.decode("utf-8").split("\n")))
        assert table == schema.TABLE_NAME and cols == "(" + ",".join(schema.INSERT_COLUMNS) + ")"
        return True

    import zephyr.data.ch_writer as ch_writer_mod

    monkeypatch.setattr(ch_writer_mod, "write_tsv", fake_write_tsv)
    assert mod._chunked_writer()(schema.TABLE_NAME, "(" + ",".join(schema.INSERT_COLUMNS) + ")", big) is True
    assert ch_calls == [1000, 1000, 500]  # 分块 1000 行/块


def test_hook_five_states(monkeypatch: pytest.MonkeyPatch):
    # ① 非唤醒词跳过
    assert maybe_emit_retail_comment_signals(task_id="daily_kline", success=True)["action"] == "skipped_wake_point"
    # ② 前置任务失败跳过
    assert (
        maybe_emit_retail_comment_signals(task_id="alt_stock_comment_daily", success=False)["action"]
        == "skipped_wake_point"
    )
    # ③ 唤醒+有数=emitted
    import zephyr.alt_data.retail_comment_signals as m

    monkeypatch.setattr(m, "run_signals", lambda **kw: {"action": "emitted", "rows": 1})
    assert maybe_emit_retail_comment_signals(task_id="alt_stock_comment_daily", success=True)["action"] == "emitted"
    # ④ 唤醒+空表=emitted_empty
    monkeypatch.setattr(m, "run_signals", lambda **kw: {"action": "emitted_empty", "signal_rows": 0})
    assert maybe_emit_retail_comment_signals(task_id="stock_comment_daily", success=True)["action"] == "emitted_empty"
    # ⑤ 唤醒+失败=error 留因（禁静默）＋异常不反噬
    monkeypatch.setattr(m, "run_signals", lambda **kw: {"action": "error", "error": "CH 写入未确认"})
    r5 = maybe_emit_retail_comment_signals(task_id="alt_stock_comment_daily", success=True)
    assert r5["action"] == "error" and "CH 写入未确认" in r5["reason"]
    monkeypatch.setattr(m, "run_signals", lambda **kw: (_ for _ in ()).throw(RuntimeError("boom")))
    r6 = maybe_emit_retail_comment_signals(task_id="alt_stock_comment_daily", success=True)
    assert r6["action"] == "error" and "boom" in r6["reason"]
