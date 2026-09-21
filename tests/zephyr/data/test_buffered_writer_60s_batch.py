# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_buffered_writer_60s_batch
# [DOMAIN] D_DATA
# [DEPENDENCIES] pytest; zephyr.data.buffered_writer; zephyr.data.config.tasks.yaml
# [CONSUMERS] pytest 车道
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全程 monkeypatch ch_writer（零真实 CH 写入）; 单表单批 flush 语义=一次 INSERT 全量行
# [ERROR_CONTRACT] 断言式失败即测试失败
# [A_module] module_id=MOD-L00-004-BW60-TEST | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""12 小表 60s 攒批窗（WO-3，ch_health §3.3 parts 爆炸治理）红证双向。

红证（改前语义证伪——若 buffer 窗形同虚设，本组用例必红）：
  ①单表单批：max_seconds=60 下小批 add 不触发自动 flush（<60s），手动 flush 一次写全量行、
    flush 计数=1、行数守恒（ch_health「1 行/part」病灶的对照语义）；
  ②窗满触发：monkeypatch time.time 前跳 ≥60s 后，下一次 add 自动 flush（攒批窗真实生效，
    非摆设）；未到 60s 不 flush；
  ③配置契约：tasks.yaml 中所有写 12 小表的任务 buffer_max_seconds==60（防回归漂移）。
全程 monkeypatch ch_writer 三个出口（get_insertable_columns_set / write_tsv_outcome /
scrub_1970_date_sentinels），零真实 ClickHouse 写入，零生产路径触碰。
"""

from __future__ import annotations

from pathlib import Path

import yaml

import zephyr.data.buffered_writer as bw
from zephyr.data.buffered_writer import BufferedWriter


class _FakeResult:
    """FetchResult 形状最小桩（table/columns/rows/error）。"""

    def __init__(self, table: str, columns: list[str], rows: list[tuple]):
        self.table = table
        self.columns = columns
        self.rows = rows
        self.error = None


class _FakeOutcome:
    is_ch_committed = True


TABLE = "c1_market.macro_credit_money"
COLS = ["report_date", "indicator", "value"]
ROWS = [("2026-09-01", "m2", "1.0"), ("2026-09-01", "m1", "2.0"), ("2026-09-01", "shrzgm", "3.0")]


def _patch_ch(monkeypatch, flush_log: list):
    """ch_writer 三个出口全部打桩：列集合放行、写记账、1970 守卫透传。"""
    monkeypatch.setattr(bw.ch_writer, "get_insertable_columns_set", lambda table: set(COLS))
    monkeypatch.setattr(bw.ch_writer, "scrub_1970_date_sentinels", lambda cols, rows, table="": (rows, 0))

    def fake_write_tsv_outcome(table, cols_clause, tsv_bytes):
        flush_log.append((table, cols_clause, len(tsv_bytes.splitlines())))
        return _FakeOutcome()

    monkeypatch.setattr(bw.ch_writer, "write_tsv_outcome", fake_write_tsv_outcome)


def test_single_table_single_batch_one_flush(monkeypatch):
    """①单表单批：60s 窗内不自动 flush，手动 flush 一次全量落、行数守恒。"""
    flush_log: list = []
    _patch_ch(monkeypatch, flush_log)
    w = BufferedWriter(TABLE, max_seconds=60)
    assert w.add(_FakeResult(TABLE, COLS, ROWS)) is True
    assert len(flush_log) == 0, "60s 窗内小批 add 不得自动 flush（攒批语义）"
    assert w.add(_FakeResult(TABLE, COLS, ROWS[:1])) is True
    assert len(flush_log) == 0, "仍应在窗内继续攒批"
    assert w.flush() is True
    assert len(flush_log) == 1, "单批应恰一次 INSERT（对照 1 行/part 病灶）"
    table, cols, n_lines = flush_log[0]
    assert table == TABLE and n_lines == 4  # 3+1 行全量
    assert w.total_flushed == 4 and w.flush_count == 1
    # 再 flush 空缓冲=True 幂等（ERROR_CONTRACT）
    assert w.flush() is True and len(flush_log) == 1


def test_window_expiry_triggers_auto_flush(monkeypatch):
    """②攒批窗真实生效：未满 60s 不 flush；≥60s 后下一次 add 自动 flush。"""
    flush_log: list = []
    _patch_ch(monkeypatch, flush_log)
    now = [1000.0]
    monkeypatch.setattr(bw.time, "time", lambda: now[0])
    w = BufferedWriter(TABLE, max_seconds=60)
    assert w.add(_FakeResult(TABLE, COLS, ROWS)) is True
    now[0] = 1030.0  # +30s（旧默认窗已到，新窗未到）——若仍是 30s 语义会提前 flush，本用例即红
    assert w.add(_FakeResult(TABLE, COLS, ROWS[:1])) is True
    assert len(flush_log) == 0, "30~60s 区间必须继续攒批（30s 旧窗语义在此证伪）"
    now[0] = 1061.0  # +61s ≥ 60s 窗满
    assert w.add(_FakeResult(TABLE, COLS, ROWS[:1])) is True
    assert len(flush_log) == 1, "窗满后 add 应自动 flush"
    assert flush_log[0][2] == 5 and w.total_flushed == 5


def test_tasks_yaml_small_tables_config_contract():
    """③配置契约：12 小表全部任务 buffer_max_seconds==60（parts 爆炸治理防回归）。"""
    targets = {
        "alt_regime_signal",
        "alt_shipping_index",
        "macro_data",
        "rate_decision_calendar",
        "macro_credit_money",
        "macro_price_gauge",
        "macro_activity_gauge",
        "us_index",
        "rights_issue",
        "alt_sz_weather_warning",
        "ex_dividend_event",
        "repurchase",
    }
    cfg = yaml.safe_load(
        (Path(__file__).resolve().parents[3] / "src" / "zephyr" / "data" / "config" / "tasks.yaml").read_text(
            encoding="utf-8"
        )
    )
    hit = 0
    for task in cfg["tasks"]:
        short = str(task.get("table", "")).split(".")[-1]
        if short in targets:
            assert task.get("buffer_max_seconds") == 60, f"{task.get('task_id')} 写 parts 爆炸小表但未配 60s 攒批窗"
            hit += 1
    assert hit >= 12, f"12 表任务覆盖数异常: {hit}"
