"""prediction_calibration_monitor 单元测试（92号清单 §8.7 M4-④，44号备忘 §12.1）。

覆盖：
- 统计器（合成 prediction_log 序列）：全命中/全不命中/混合命中率正确；无真值
  hit_rate=None；窗口外样本剔除；孤儿 outcome（无当日预测匹配）不计样本；
  非法 outcome（缺 hit:bool）计 invalid；calibration_trigger 族不计入预测数；
  趋势 improving/worsening/stable/insufficient_data；
- record_outcome 真值回写：outcome 族落库可查；非 dict/缺 hit/hit 非 bool
  fail-closed；
- 样本量守卫：29 样本不触发（insufficient_data）/30 样本进入阈值评估（触发）；
- 阈值行为：0.54 触发（below_threshold）/0.56 hold；自定义 config 阈值与守卫；
- 异常 fail-open：统计异常（无表库）不触发+reason='error' 不外抛；注入 stats
  时落盘失败不翻转判定（persistence_error 留痕）；
- 事件落盘：触发写 prediction_log calibration_trigger 族（同日同内容幂等）
  +评审建议工单落 runtime_dir（含 G04/纪律声明文本）；hold/insufficient 零落盘；
- 输入/config 校验 fail-closed；默认工单目录走 MAIN_REPO_ROOT SSoT（monkeypatch）。
全 tmp 隔离，不触真 governance.db 与真 .runtime/。
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from zephyr.reporting import prediction_calibration_monitor as pcm
from zephyr.reporting.prediction_calibration_monitor import (
    CalibrationConfig,
    CalibrationStats,
    compute_hit_rate_stats,
    evaluate_calibration_trigger,
    record_outcome,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
    query_predictions,
)

MODULE = "signal_ashare.boundary_revision"


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """tmp 库 + 幂等建表（DDL 真源=prediction_log_writer 常量）。"""
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


def _iso(days_ago: int) -> str:
    return (date.today() - timedelta(days=days_ago)).isoformat()


def _seed_pairs(db: Path, module: str, hits: list[bool], start_days_ago: int | None = None) -> None:
    """按时间序播种 预测+真值 对（hits[0]=最旧，默认最新一对落在今天）。"""
    n = len(hits)
    base = start_days_ago if start_days_ago is not None else n - 1
    for i, hit in enumerate(hits):
        d = _iso(base - i)
        log_prediction(
            trade_date=d,
            module=module,
            prediction_type="boundary_revision",
            payload={"seq": i},
            db_path=db,
        )
        record_outcome(
            trade_date=d,
            module=module,
            outcome_payload={
                "hit": hit,
                "revision_direction": "up",
                "actual_direction": "up" if hit else "down",
            },
            db_path=db,
        )


def _stats(module: str, sample_size: int, hit_rate: float | None) -> CalibrationStats:
    """手工构造统计快照（注入 evaluate 用，绕过统计器）。"""
    return CalibrationStats(
        module=module,
        window_days=60,
        window_start=_iso(59),
        window_end=_iso(0),
        prediction_count=sample_size,
        sample_size=sample_size,
        hit_count=int(round(sample_size * (hit_rate or 0.0))),
        hit_rate=hit_rate,
        recent_hit_rate=hit_rate,
        previous_hit_rate=hit_rate,
        trend="stable",
    )


# ── 统计器：命中率口径 ──


class TestHitRateStats:
    def test_all_hits(self, tmp_db: Path) -> None:
        _seed_pairs(tmp_db, MODULE, [True] * 10)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.sample_size == 10
        assert st.hit_count == 10
        assert st.hit_rate == pytest.approx(1.0)
        assert st.prediction_count == 10

    def test_all_misses(self, tmp_db: Path) -> None:
        _seed_pairs(tmp_db, MODULE, [False] * 10)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.hit_rate == pytest.approx(0.0)
        assert st.hit_count == 0

    def test_mixed_hit_rate(self, tmp_db: Path) -> None:
        hits = [True, False, True, True, False, True, False, True, False, True]  # 6 中 4 不中
        _seed_pairs(tmp_db, MODULE, hits)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.sample_size == 10
        assert st.hit_count == 6
        assert st.hit_rate == pytest.approx(0.6)

    def test_no_outcomes_hit_rate_none(self, tmp_db: Path) -> None:
        """只有预测无真值回写：样本 0，hit_rate=None，趋势 insufficient_data。"""
        log_prediction(
            trade_date=_iso(1), module=MODULE, prediction_type="boundary_revision", payload={"seq": 0}, db_path=tmp_db
        )
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.sample_size == 0
        assert st.hit_rate is None
        assert st.trend == "insufficient_data"
        assert st.prediction_count == 1

    def test_window_cutoff(self, tmp_db: Path) -> None:
        """窗口外（100 日前）样本剔除；放宽窗口到 120 日可见。"""
        _seed_pairs(tmp_db, MODULE, [True] * 5, start_days_ago=100)
        st60 = compute_hit_rate_stats(MODULE, window_days=60, db_path=tmp_db)
        assert st60.sample_size == 0
        st120 = compute_hit_rate_stats(MODULE, window_days=120, db_path=tmp_db)
        assert st120.sample_size == 5
        assert st120.window_start == _iso(119)
        assert st120.window_end == _iso(0)

    def test_orphan_outcome_excluded(self, tmp_db: Path) -> None:
        """无当日预测匹配的 outcome=孤儿，计 orphan 不计样本。"""
        _seed_pairs(tmp_db, MODULE, [True] * 5)
        record_outcome(trade_date=_iso(30), module=MODULE, outcome_payload={"hit": True}, db_path=tmp_db)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.sample_size == 5
        assert st.orphan_outcome_count == 1

    def test_invalid_outcome_counted(self, tmp_db: Path) -> None:
        """缺 hit:bool 的 outcome 行（非 record_outcome 写入）计 invalid 不计样本。"""
        _seed_pairs(tmp_db, MODULE, [True] * 5)
        log_prediction(
            trade_date=_iso(2),
            module=MODULE,
            prediction_type="outcome",
            payload={"note": "缺 hit 字段"},
            db_path=tmp_db,
        )
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.sample_size == 5
        assert st.invalid_outcome_count == 1

    def test_trigger_rows_not_counted_as_predictions(self, tmp_db: Path) -> None:
        """calibration_trigger 族不计入 prediction_count（防自引用计数）。"""
        _seed_pairs(tmp_db, MODULE, [True] * 5)
        log_prediction(
            trade_date=_iso(1),
            module=MODULE,
            prediction_type="calibration_trigger",
            payload={"reason": "below_threshold"},
            db_path=tmp_db,
        )
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.prediction_count == 5
        assert st.sample_size == 5

    def test_module_isolation(self, tmp_db: Path) -> None:
        """统计只认本模块——他模块预测/真值不混入。"""
        _seed_pairs(tmp_db, MODULE, [True] * 5)
        _seed_pairs(tmp_db, "other.module", [False] * 5)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.sample_size == 5
        assert st.hit_rate == pytest.approx(1.0)


# ── 统计器：窗口趋势 ──


class TestTrend:
    def test_improving(self, tmp_db: Path) -> None:
        """前段全不命中+近段全命中 → improving（近1.0 vs 前0.0）。"""
        _seed_pairs(tmp_db, MODULE, [False] * 5 + [True] * 5)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.trend == "improving"
        assert st.previous_hit_rate == pytest.approx(0.0)
        assert st.recent_hit_rate == pytest.approx(1.0)

    def test_worsening(self, tmp_db: Path) -> None:
        _seed_pairs(tmp_db, MODULE, [True] * 5 + [False] * 5)
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.trend == "worsening"

    def test_stable(self, tmp_db: Path) -> None:
        # 前段 [T,F,T,F,F]=0.4，近段 [F,T,F,T,F]=0.4——差 0 ≤ 容忍带 → stable
        _seed_pairs(tmp_db, MODULE, [True, False, True, False, False, False, True, False, True, False])
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.trend == "stable"
        assert st.recent_hit_rate == pytest.approx(st.previous_hit_rate)

    def test_insufficient_data_single_sample(self, tmp_db: Path) -> None:
        _seed_pairs(tmp_db, MODULE, [True])
        st = compute_hit_rate_stats(MODULE, db_path=tmp_db)
        assert st.trend == "insufficient_data"
        assert st.recent_hit_rate is None
        assert st.previous_hit_rate is None


# ── record_outcome 真值回写 ──


class TestRecordOutcome:
    def test_write_outcome_row(self, tmp_db: Path) -> None:
        """outcome 族落库可查（prediction_type='outcome'，payload 原样）。"""
        rid = record_outcome(
            trade_date=_iso(1),
            module=MODULE,
            outcome_payload={"hit": True, "actual_direction": "up"},
            db_path=tmp_db,
        )
        assert rid >= 1
        rows = query_predictions(module=MODULE, prediction_type="outcome", db_path=tmp_db)
        assert len(rows) == 1
        assert json.loads(rows[0]["payload_json"]) == {"hit": True, "actual_direction": "up"}

    def test_idempotent_rewrite(self, tmp_db: Path) -> None:
        """同日同模块同内容重复回写=幂等跳过保首条（同 id 仅一行）。"""
        kwargs = {"trade_date": _iso(1), "module": MODULE, "outcome_payload": {"hit": True}, "db_path": tmp_db}
        assert record_outcome(**kwargs) == record_outcome(**kwargs)
        assert len(query_predictions(module=MODULE, db_path=tmp_db)) == 1

    def test_reject_non_dict_payload(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="outcome_payload"):
            record_outcome(trade_date=_iso(1), module=MODULE, outcome_payload="命中", db_path=tmp_db)

    def test_reject_missing_hit(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="hit"):
            record_outcome(trade_date=_iso(1), module=MODULE, outcome_payload={"note": "x"}, db_path=tmp_db)

    def test_reject_non_bool_hit(self, tmp_db: Path) -> None:
        """hit=1（int）不是 bool——fail-closed 拒收（防静默降级判定口径）。"""
        with pytest.raises(ValueError, match="hit"):
            record_outcome(trade_date=_iso(1), module=MODULE, outcome_payload={"hit": 1}, db_path=tmp_db)

    def test_reject_bad_trade_date(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="trade_date"):
            record_outcome(trade_date="2026-02-30", module=MODULE, outcome_payload={"hit": True}, db_path=tmp_db)


# ── 样本量守卫 ──


class TestSampleGuard:
    def test_29_samples_not_triggered(self, tmp_db: Path) -> None:
        """29 样本（全不命中，命中率 0 也）不足守卫 → insufficient_data 不触发。"""
        _seed_pairs(tmp_db, MODULE, [False] * 29)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=tmp_path_dir(tmp_db))
        assert v.triggered is False
        assert v.reason == "insufficient_data"
        assert v.suggested_action == ""
        assert v.evidence["sample_size"] == 29

    def test_30_samples_enter_evaluation(self, tmp_db: Path) -> None:
        """30 样本（全不命中）达标进入阈值评估 → 触发 below_threshold。"""
        _seed_pairs(tmp_db, MODULE, [False] * 30)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=tmp_path_dir(tmp_db))
        assert v.triggered is True
        assert v.reason == "below_threshold"
        assert v.evidence["sample_size"] == 30

    def test_custom_min_samples(self, tmp_db: Path) -> None:
        """config 化守卫：min_samples=50 时 40 样本不触发。"""
        _seed_pairs(tmp_db, MODULE, [False] * 40)
        cfg = CalibrationConfig(min_samples=50)
        v = evaluate_calibration_trigger(MODULE, config=cfg, db_path=tmp_db, runtime_dir=tmp_path_dir(tmp_db))
        assert v.reason == "insufficient_data"


def tmp_path_dir(db: Path) -> Path:
    """由 tmp 库路径派生本用例的工单落盘目录（同 tmp 隔离域）。"""
    return db.parent / "runtime_out"


# ── 阈值行为 ──


class TestThreshold:
    def test_hit_rate_054_triggers(self, tmp_db: Path) -> None:
        """27/50=0.54 < 0.55 默认阈值 → 触发。"""
        _seed_pairs(tmp_db, MODULE, [True] * 27 + [False] * 23)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=tmp_path_dir(tmp_db))
        assert v.triggered is True
        assert v.reason == "below_threshold"
        assert v.evidence["hit_rate"] == pytest.approx(0.54)
        assert "G04" in v.suggested_action
        assert MODULE in v.suggested_action

    def test_hit_rate_056_holds(self, tmp_db: Path) -> None:
        """28/50=0.56 ≥ 0.55 → hold 不触发，零落盘。"""
        _seed_pairs(tmp_db, MODULE, [True] * 28 + [False] * 22)
        rt = tmp_path_dir(tmp_db)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=rt)
        assert v.triggered is False
        assert v.reason == "hold"
        assert not rt.exists()
        assert query_predictions(module=MODULE, prediction_type="calibration_trigger", db_path=tmp_db) == []

    def test_custom_threshold(self, tmp_db: Path) -> None:
        """config 化阈值：21/40=0.525——默认 0.55 触发；阈值 0.50 则 hold。"""
        _seed_pairs(tmp_db, MODULE, [True] * 21 + [False] * 19)
        v_default = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=tmp_path_dir(tmp_db))
        assert v_default.triggered is True
        v_custom = evaluate_calibration_trigger(
            MODULE,
            config=CalibrationConfig(hit_rate_threshold=0.50),
            db_path=tmp_db,
            runtime_dir=tmp_path_dir(tmp_db),
        )
        assert v_custom.triggered is False
        assert v_custom.reason == "hold"


# ── 异常 fail-open ──


class TestFailOpen:
    def test_stats_error_fail_open(self, tmp_path: Path) -> None:
        """统计异常（库无表）→ 不触发+reason='error'+error 留痕，绝不外抛。"""
        ghost = tmp_path / "no_table.db"
        v = evaluate_calibration_trigger(MODULE, db_path=ghost, runtime_dir=tmp_path / "rt")
        assert v.triggered is False
        assert v.reason == "error"
        assert "error" in v.evidence
        assert v.evaluated_at

    def test_persistence_failure_does_not_flip_verdict(self, tmp_path: Path) -> None:
        """注入 stats+落盘库无表：判定仍 triggered=True，persistence_error 留痕不外抛。"""
        st = _stats(MODULE, sample_size=30, hit_rate=0.40)
        v = evaluate_calibration_trigger(
            MODULE,
            stats=st,
            db_path=tmp_path / "no_table.db",
            runtime_dir=tmp_path / "rt",
        )
        assert v.triggered is True
        assert v.reason == "below_threshold"
        assert "persistence_error" in v.evidence
        assert "persisted_row_id" not in v.evidence
        # 工单落盘独立于事件落盘——仍产出（评审建议不丢）
        assert Path(v.evidence["work_order_path"]).exists()

    def test_provided_stats_skip_computation(self, tmp_path: Path) -> None:
        """注入 stats 时不碰库——hold 判定即使库路径是 ghost 也正常返回。"""
        st = _stats(MODULE, sample_size=40, hit_rate=0.80)
        v = evaluate_calibration_trigger(MODULE, stats=st, db_path=tmp_path / "ghost.db")
        assert v.reason == "hold"


# ── 事件落盘 ──


class TestEventPersistence:
    def test_trigger_event_and_work_order(self, tmp_db: Path) -> None:
        """触发：calibration_trigger 族落库 + 工单落 runtime_dir（文本含 G04/纪律声明）。"""
        _seed_pairs(tmp_db, MODULE, [True] * 16 + [False] * 24)  # 16/40=0.40
        rt = tmp_path_dir(tmp_db)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=rt)
        assert v.triggered is True

        rows = query_predictions(module=MODULE, prediction_type="calibration_trigger", db_path=tmp_db)
        assert len(rows) == 1
        payload = json.loads(rows[0]["payload_json"])
        assert payload["reason"] == "below_threshold"
        assert payload["hit_rate"] == pytest.approx(0.40)
        assert payload["sample_size"] == 40
        assert payload["threshold"] == pytest.approx(0.55)
        assert rows[0]["id"] == v.evidence["persisted_row_id"]

        wo = Path(v.evidence["work_order_path"])
        assert wo.exists() and wo.parent == rt
        text = wo.read_text(encoding="utf-8")
        assert MODULE in text
        assert "G04" in text
        assert "评审建议" in text
        assert "永不自治修改任何参数" in text

    def test_trigger_event_idempotent_same_day(self, tmp_db: Path) -> None:
        """同日同统计内容重复评估：触发事件幂等（仍仅一行）。"""
        _seed_pairs(tmp_db, MODULE, [False] * 40)
        rt = tmp_path_dir(tmp_db)
        evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=rt)
        evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=rt)
        rows = query_predictions(module=MODULE, prediction_type="calibration_trigger", db_path=tmp_db)
        assert len(rows) == 1

    def test_insufficient_data_no_persistence(self, tmp_db: Path) -> None:
        """样本守卫拦截：零触发事件零工单。"""
        _seed_pairs(tmp_db, MODULE, [False] * 10)
        rt = tmp_path_dir(tmp_db)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db, runtime_dir=rt)
        assert v.reason == "insufficient_data"
        assert query_predictions(module=MODULE, prediction_type="calibration_trigger", db_path=tmp_db) == []
        assert not rt.exists()

    def test_default_work_order_dir_ssot(self, tmp_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """runtime_dir=None 走 MAIN_REPO_ROOT/.runtime/calibration_review（monkeypatch 指 tmp）。"""
        fake_root = tmp_db.parent / "repo_root"
        monkeypatch.setattr(pcm, "MAIN_REPO_ROOT", fake_root)
        _seed_pairs(tmp_db, MODULE, [False] * 30)
        v = evaluate_calibration_trigger(MODULE, db_path=tmp_db)
        wo = Path(v.evidence["work_order_path"])
        assert wo.exists()
        assert wo.parent == fake_root / ".runtime" / "calibration_review"


# ── 输入/config 校验 fail-closed ──


class TestValidation:
    def test_reject_empty_module(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="module"):
            compute_hit_rate_stats("  ", db_path=tmp_db)
        with pytest.raises(ValueError, match="module"):
            evaluate_calibration_trigger("", db_path=tmp_db)

    def test_reject_bad_window_days(self, tmp_db: Path) -> None:
        for bad in (0, -1, True, "60"):
            with pytest.raises(ValueError, match="window_days"):
                compute_hit_rate_stats(MODULE, window_days=bad, db_path=tmp_db)

    def test_reject_bad_config_type(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="config"):
            evaluate_calibration_trigger(MODULE, config={"hit_rate_threshold": 0.5}, db_path=tmp_db)

    def test_reject_bad_stats_type(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="stats"):
            evaluate_calibration_trigger(MODULE, stats={"sample_size": 40}, db_path=tmp_db)

    def test_config_field_validation(self) -> None:
        for bad in (0.0, 1.0, -0.1, "0.55", True):
            with pytest.raises(ValueError, match="hit_rate_threshold"):
                CalibrationConfig(hit_rate_threshold=bad)
        for bad in (0, -5, 1.5, True):
            with pytest.raises(ValueError, match="min_samples"):
                CalibrationConfig(min_samples=bad)
        for bad in (0, -1, 2.5, False):
            with pytest.raises(ValueError, match="window_days"):
                CalibrationConfig(window_days=bad)

    def test_default_config_values(self) -> None:
        cfg = CalibrationConfig()
        assert cfg.hit_rate_threshold == pytest.approx(0.55)
        assert cfg.min_samples == 30
        assert cfg.window_days == 60
