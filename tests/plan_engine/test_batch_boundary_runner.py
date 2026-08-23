# [A_test] module_id: MOD-PLAN-012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-012 | 待统筹登记 | 缺口总账 GAP-F-02 + 45号 §4 W2/W2b
# [MODULE] tests.plan_engine.test_batch_boundary_runner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""BatchBoundaryRunner (MOD-PLAN-012) 施工验证测试。

覆盖：
- 批量计算：多符号 kline mock → TomorrowBoundary 正确（箱体=close×(1±amp/100)）；
  输入顺序保持（确定性输出）；去重；振幅缺失/为 0 → 默认 3% 口径。
- 失败留痕：kline 缺行 → no_data；close≤0 → planner 抛 BoundaryComputeError →
  error + 错误消息（不含 session_id）；CH 通道异常 → 全量 no_data 不炸。
- 并发控制：max_workers 配置生效与上限校验（>8/0 fail-closed）。
- 结果落库：prediction_log "tomorrow_boundary" 族（module=MOD-PLAN-001 语义
  产出方，trade_date=target_date）；payload 字段齐全；幂等（重跑同键保首条）；
  persist=False 不落库；落库异常 fail-open（items 仍 ok + trace 留痕）。
全 mock CH + tmp 库隔离，不触真 governance.db 与真 ClickHouse。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.plan_engine.batch_boundary_runner import (
    BOUNDARY_MODULE_LOG_NAME,
    BOUNDARY_PREDICTION_TYPE,
    BatchBoundaryConfig,
    BatchBoundaryResult,
    BatchBoundaryRunner,
    run_batch_boundaries,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    query_predictions,
)

TRADE_DATE = "2026-08-21"
TARGET_DATE = "2026-08-24"


def _kline_tsv(rows: list[tuple]) -> str:
    """kline 行：(symbol_canonical, close, amplitude_pct)。"""
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


def _make_ch(kline_tsv: str = "", raise_on_kline: bool = False):
    def _ch(sql: str) -> str:
        if "kline_daily" in sql:
            if raise_on_kline:
                raise RuntimeError("kline boom")
            return kline_tsv
        return ""

    return _ch


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


FULL_KLINE = _kline_tsv([
    ("600000.SH", 10.0, 4.0),
    ("000001.SZ", 20.0, 2.0),
    ("300750.SZ", 100.0, 0.0),  # 振幅 0 → 默认 3%
])


# ══════════════════════════════════════════════════════════════
# 批量计算
# ══════════════════════════════════════════════════════════════


class TestBatchCompute:
    def test_all_ok(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH", "000001.SZ", "300750.SZ"], target_date=TARGET_DATE)
        assert result.total == 3
        assert result.ok_count == 3
        assert result.error_count == 0
        assert result.no_data_count == 0
        items = {i.symbol: i for i in result.items}
        b1 = items["600000.SH"].boundary
        assert b1 is not None
        assert b1.box_upper == pytest.approx(10.0 * 1.04)
        assert b1.box_lower == pytest.approx(10.0 * 0.96)
        b3 = items["300750.SZ"].boundary
        assert b3 is not None
        assert b3.box_upper == pytest.approx(100.0 * 1.03)  # 振幅 0 → 默认 3%

    def test_order_preserved(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["300750.SZ", "600000.SH", "000001.SZ"])
        assert [i.symbol for i in result.items] == ["300750.SZ", "600000.SH", "000001.SZ"]

    def test_dedupe(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH", "600000.SH", "000001.SZ"])
        assert result.total == 2

    def test_empty_symbols(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, [])
        assert result.total == 0
        assert result.items == ()

    def test_no_data_symbol(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH", "999999.SH"])
        items = {i.symbol: i for i in result.items}
        assert items["600000.SH"].status == "ok"
        assert items["999999.SH"].status == "no_data"
        assert items["999999.SH"].boundary is None
        assert result.no_data_count == 1

    def test_compute_error_trace(self, tmp_db: Path) -> None:
        kline = _kline_tsv([("600000.SH", -1.0, 4.0)])  # 非法收盘价 → planner 抛
        runner = BatchBoundaryRunner(ch_client=_make_ch(kline), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH"])
        item = result.items[0]
        assert item.status == "error"
        assert item.error is not None
        assert "收盘价异常" in item.error
        assert "session_id" not in item.error
        assert result.error_count == 1

    def test_ch_error_all_no_data(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(raise_on_kline=True), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH", "000001.SZ"])
        assert result.no_data_count == 2
        assert result.trace["channels"]["kline_daily"].startswith("error:")

    def test_invalid_input_fail_closed(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        with pytest.raises(ValueError):
            runner.run("2026-13-99", ["600000.SH"])
        with pytest.raises(ValueError):
            runner.run(TRADE_DATE, ["600000.SH"], target_date="bad-date")
        with pytest.raises(ValueError):
            runner.run(TRADE_DATE, ["600000.SH;DROP TABLE"])  # SQL 注入字符拒收
        with pytest.raises(ValueError):
            runner.run(TRADE_DATE, [""])
        with pytest.raises(ValueError):
            BatchBoundaryConfig(max_workers=0)
        with pytest.raises(ValueError):
            BatchBoundaryConfig(max_workers=9)  # 超 RULE-SEVEN 上限 8


# ══════════════════════════════════════════════════════════════
# 并发控制
# ══════════════════════════════════════════════════════════════


class TestConcurrency:
    def test_max_workers_config_accepted(self, tmp_db: Path) -> None:
        cfg = BatchBoundaryConfig(max_workers=8)
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db, config=cfg)
        result = runner.run(TRADE_DATE, ["600000.SH", "000001.SZ", "300750.SZ"])
        assert result.ok_count == 3
        assert result.trace["max_workers"] == 8


# ══════════════════════════════════════════════════════════════
# 结果落库
# ══════════════════════════════════════════════════════════════


class TestPersistence:
    def test_rows_written(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH", "000001.SZ"], target_date=TARGET_DATE)
        assert len(result.persisted_row_ids) == 2
        rows = query_predictions(
            trade_date=TARGET_DATE,
            module=BOUNDARY_MODULE_LOG_NAME,
            prediction_type=BOUNDARY_PREDICTION_TYPE,
            db_path=tmp_db,
        )
        assert len(rows) == 2
        payload = json.loads(rows[0]["payload_json"])
        assert payload["symbol"] in ("600000.SH", "000001.SZ")
        assert payload["box_upper"] > payload["box_lower"]
        assert payload["source_trade_date"] == TRADE_DATE
        assert payload["target_date"] == TARGET_DATE
        assert payload["max_add_position"] == pytest.approx(0.30)

    def test_default_target_date_is_trade_date(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        result = runner.run(TRADE_DATE, ["600000.SH"])
        assert result.target_date == TRADE_DATE
        rows = query_predictions(
            trade_date=TRADE_DATE, module=BOUNDARY_MODULE_LOG_NAME,
            prediction_type=BOUNDARY_PREDICTION_TYPE, db_path=tmp_db,
        )
        assert len(rows) == 1

    def test_idempotent_rerun(self, tmp_db: Path) -> None:
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db)
        r1 = runner.run(TRADE_DATE, ["600000.SH"], target_date=TARGET_DATE)
        r2 = runner.run(TRADE_DATE, ["600000.SH"], target_date=TARGET_DATE)
        assert r1.persisted_row_ids == r2.persisted_row_ids
        rows = query_predictions(
            module=BOUNDARY_MODULE_LOG_NAME, prediction_type=BOUNDARY_PREDICTION_TYPE, db_path=tmp_db,
        )
        assert len(rows) == 1

    def test_persist_disabled(self, tmp_db: Path) -> None:
        cfg = BatchBoundaryConfig(persist=False)
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_db, config=cfg)
        result = runner.run(TRADE_DATE, ["600000.SH"])
        assert result.ok_count == 1
        assert result.persisted_row_ids == ()
        rows = query_predictions(module=BOUNDARY_MODULE_LOG_NAME, db_path=tmp_db)
        assert rows == []

    def test_persist_failure_fail_open(self, tmp_path: Path) -> None:
        # db_path 指向目录 → 建表/写库必失败 → fail-open：items 仍 ok + trace 留痕
        runner = BatchBoundaryRunner(ch_client=_make_ch(FULL_KLINE), db_path=tmp_path)
        result = runner.run(TRADE_DATE, ["600000.SH"])
        assert result.ok_count == 1
        assert result.persisted_row_ids == ()
        assert result.trace["persist_errors"] >= 1

    def test_module_entry(self, tmp_db: Path) -> None:
        result = run_batch_boundaries(
            TRADE_DATE, ["600000.SH", "999999.SH"],
            ch_client=_make_ch(FULL_KLINE), db_path=tmp_db, target_date=TARGET_DATE,
        )
        assert isinstance(result, BatchBoundaryResult)
        assert result.ok_count == 1
        assert result.no_data_count == 1
        d = result.to_dict()
        json.dumps(d, ensure_ascii=False)  # JSON 可序列化
