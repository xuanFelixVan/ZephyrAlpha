# [TTL] permanent
# [MODULE] tests.data.data.data.test_ti_backfill_value_skip_and_shard_windows
# [DOMAIN] D_DATA
"""dwm 指标回填三件止血判据的测试（2026-10-10 终清总队，dexp 战役 §11 P1/P3/P4 落地面）。

大白话三件事：
① 值级跳过（P1）——夜跑每晚把全史重灌一遍，而重灌出来的数跟库里上一版只差浮点末位
   （实测 9.1e-13，量级 130）。现在写之前先比：整行每列相对差都 ≤1e-9 就不写。
   两条必红判据：把某列改 1e-6 ⇒ 必须写；改 1e-13 ⇒ 必须跳。
② 单实例互斥（P3）——计划任务和手动续跑以前可以并行/接力（10-08 21:32 与 10-09 02:30
   两趟叠加即为实证）。现在入口一把 OS 级文件锁，第二个实例必须让路。
   必红判据：同目录连取两次锁，第二次必须是 None（锁不是装饰件）。
③ 年切窗 + 超时留态（P4）——一片 100 标的 × 5.6 年撑不过 7200s，旧写法一超时
   整片 state 不落，于是那片每晚从头再来（shard_024 至今无 state 即为实证）。
   必红判据：窗超时也必须写下 exit="timeout" 的 state，且续跑只补没跑完的窗。

零网络零生产写：state 目录与锁文件一律落 tmp_path；CH 读面全部替身。
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[4]
RUNNER = ROOT / "scripts" / "data" / "tilib_dwm_shard_runner.py"
BACKFILL = ROOT / "scripts" / "data" / "backfill_technical_indicator_dwm.py"


def _load(path: Path, alias: str):
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


runner = _load(RUNNER, "dwm_runner_under_test")
backfill = _load(BACKFILL, "dwm_backfill_under_test")


# ────────────────────────────── P1 值级跳过 ──────────────────────────────


class TestValueSkipRelTol:
    """批复阈值 1e-9 的两侧：真变更必写、浮点末位噪声必跳。"""

    def test_one_e_minus_6_change_must_be_written(self):
        """红证①：把一列改成相对差 1e-6（>1e-9）⇒ 判"变了"⇒ 必须 INSERT。"""
        assert backfill.row_rel_diverged([130.000130], [130.0]) is True

    def test_float_tail_noise_must_be_skipped(self):
        """红证②：实测末位噪声 9.1e-13（量级 130）⇒ 判"没变"⇒ 必须跳过。"""
        assert backfill.row_rel_diverged([130.0 + 9.1e-13], [130.0]) is False

    def test_identical_row_is_not_changed(self):
        assert backfill.row_rel_diverged([1615.89908, None, 66.93], [1615.89908, None, 66.93]) is False

    def test_null_flip_counts_as_changed(self):
        """一侧缺值一侧有值＝口径变了，方向保守：判变（宁多写不漏写）。"""
        assert backfill.row_rel_diverged([None], [1.0]) is True
        assert backfill.row_rel_diverged([1.0], [None]) is True

    def test_threshold_is_relative_not_absolute(self):
        """判据是相对尺不是绝对尺：同一个 1e-8 绝对差，在大数上没变、在小数上变了。

        判别力证明——若实现被写成绝对尺 `abs(new-old) > 1e-9`，两句都会是 True，
        第一句立刻翻红；反过来把阈值放松到 1e-3，第二句又会漏成真变更。
        """
        assert backfill.row_rel_diverged([1e6 + 1e-8], [1e6]) is False  # 相对 1e-14＝噪声级
        assert backfill.row_rel_diverged([1e-3 + 1e-8], [1e-3]) is True  # 相对 1e-5＝真变更
        assert backfill.row_rel_diverged([1e-3 + 1e-13], [1e-3]) is False  # 相对 1e-10＜1e-9

    def test_tighter_threshold_would_swallow_real_change(self):
        """判别力自检：阈值若被放松到 1e-3，1e-6 的真变更就会被吞——说明上面的判据真有牙齿。"""
        assert backfill.row_rel_diverged([130.000130], [130.0], tol=1e-3) is False


class TestSplitUnchangedRows:
    """按键分堆：库里没有的键必写；键在且值没变才跳。"""

    _COLUMNS = ["symbol", "trade_time", "period", "ma_5", "rsi_6"]
    _VCOLS = ["ma_5", "rsi_6"]

    def test_new_key_is_written_not_skipped(self):
        rows = [("000001", datetime.datetime(2026, 8, 10), "daily", 1.0, 2.0)]
        kept, skipped = backfill.split_unchanged_rows(rows, self._COLUMNS, {}, self._VCOLS)
        assert kept == rows and skipped == 0

    def test_same_key_same_value_is_skipped(self):
        day = datetime.datetime(2026, 8, 10)
        rows = [("000001", day, "daily", 100.0, 50.0)]
        stored = {("000001", "2026-08-10"): [100.0, 50.0]}
        kept, skipped = backfill.split_unchanged_rows(rows, self._COLUMNS, stored, self._VCOLS)
        assert kept == [] and skipped == 1

    def test_same_key_changed_value_is_kept(self):
        day = datetime.datetime(2026, 8, 10)
        rows = [("000001", day, "daily", 100.0001, 50.0)]
        stored = {("000001", "2026-08-10"): [100.0, 50.0]}
        kept, skipped = backfill.split_unchanged_rows(rows, self._COLUMNS, stored, self._VCOLS)
        assert len(kept) == 1 and skipped == 0

    def test_key_format_must_match_storage_side_or_everything_is_new(self):
        """两侧日粒度归一是比对成立的前提：库侧 '2026-08-10 00:00:00.000'，行侧 datetime。"""
        assert backfill._norm_day(datetime.datetime(2026, 8, 10, 0, 0)) == "2026-08-10"
        assert backfill._norm_day("2026-08-10 00:00:00.000") == "2026-08-10"


class TestBatchFilterDegradeIsLoud:
    """比对基失灵只准"少省"，且必须在度量里留痕——静默退回全量写＝装饰件。"""

    def _result(self):
        return SimpleNamespace(
            columns=["symbol", "trade_time", "period", "ma_5"],
            rows=[("000001", datetime.datetime(2026, 8, 10), "daily", 100.0)],
            rows_fetched=1,
            last_key="2026-08-10",
            elapsed_sec=0.0,
            table="x",
            error=None,
        )

    def test_no_comparable_columns_marks_degraded(self):
        result = self._result()
        filtered, stats = backfill.value_skip_batch(result, "daily", frozenset(), "db.tbl")
        assert filtered is result
        assert stats["degraded"] == "no-comparable-columns"

    def test_base_fetch_failure_propagates_to_caller(self):
        """现读失败必须往上抛，由调用方记 degraded 批次数——不在被调处静默吞掉。"""
        result = self._result()

        def _boom(*a, **k):
            raise RuntimeError("CH 不可达")

        monkey = pytest.MonkeyPatch()
        monkey.setattr(backfill, "fetch_base_for_batch", _boom)
        try:
            with pytest.raises(RuntimeError):
                backfill.value_skip_batch(result, "daily", frozenset({"ma_5"}), "db.tbl")
        finally:
            monkey.undo()

    def test_marker_line_parses_into_state(self):
        out = (
            "2026-10-10 03:00:00 INFO [daily] 回填开始\n"
            'TI_VALUE_SKIP {"period": "daily", "mode": "on", "skipped_rows": 7}\n'
        )
        assert runner.parse_value_skip_marker(out) == {
            "period": "daily",
            "mode": "on",
            "skipped_rows": 7,
        }
        assert runner.parse_value_skip_marker("no marker here") is None


class TestBaseFetchCircuitBreaker:
    """比对基持续取不到时必须熔断停用——否则每批白烧一轮 TCP+HTTP 重试，夜跑被拖垮。"""

    @staticmethod
    def _run(monkeypatch, tmp_path: Path, batches: int, fail_all: bool):
        from zephyr.data.provider_base import FetchResult

        calls: list[int] = []
        written: list[int] = []

        class _FakeWriter:
            def __init__(self, *a, **k) -> None:
                pass

            def add(self, result) -> bool:
                written.append(len(result.rows))
                return True

            def flush(self) -> bool:
                return True

        class _FakeProvider:
            def fetch(self, payload, policy):
                for b in range(batches):
                    yield FetchResult(
                        table="t",
                        columns=["symbol", "trade_time", "period", "ma_5"],
                        rows=[(f"S{b}", datetime.datetime(2026, 8, 10), "daily", 1.0)],
                        last_key="k",
                        elapsed_sec=0.0,
                    )

            def _get_symbols(self, payload, period):
                return ["S0"]

        def _fetch_base(*a, **k):
            calls.append(1)
            if fail_all:
                raise RuntimeError("Code: 241 memory limit exceeded")
            return {}

        monkeypatch.setattr(backfill, "BufferedWriter", _FakeWriter)
        monkeypatch.setattr(backfill, "numeric_indicator_columns", lambda t: frozenset({"ma_5"}))
        monkeypatch.setattr(backfill, "fetch_base_for_batch", _fetch_base)
        rows_total, metrics = backfill.backfill_period(
            _FakeProvider(), "daily", "2026-08-10", "2026-08-10", False, value_skip=True
        )
        return rows_total, metrics, calls, written

    def test_persistent_failure_trips_breaker_and_never_under_writes(self, monkeypatch, tmp_path: Path):
        rows_total, metrics, calls, written = self._run(monkeypatch, tmp_path, batches=8, fail_all=True)
        assert sum(written) == rows_total == 8, "熔断前后一行都不能少写——失灵只准少省"
        assert len(calls) == backfill._MAX_CONSECUTIVE_BASE_FAILURES, (
            f"熔断后不得继续逐批重试现读：实试 {len(calls)} 次"
        )
        assert metrics["mode"].startswith("disabled-after"), metrics["mode"]
        assert metrics["skipped_rows"] == 0

    def test_healthy_path_does_not_trip_breaker(self, monkeypatch, tmp_path: Path):
        rows_total, metrics, calls, written = self._run(monkeypatch, tmp_path, batches=4, fail_all=False)
        assert len(calls) == 4, "正常路径应每批都取比对基（熔断没误伤）"
        assert metrics["mode"] == "on", metrics["mode"]


# ────────────────────────────── P3 单实例互斥 ──────────────────────────────


class TestSingleInstanceLock:
    """锁不是装饰件：第二次取必须拿不到，且第二实例真让路。"""

    def test_second_acquire_in_same_dir_returns_none(self, tmp_path: Path):
        old = runner.STATE_DIR
        runner.STATE_DIR = tmp_path
        try:
            first = runner.acquire_instance_lock()
            assert first is not None, "首次取锁必须成功，否则下面的判据是空的"
            second = runner.acquire_instance_lock()
            assert second is None, "锁已被活体句柄持有，第二次拿到＝装饰件"
            first.close()
            third = runner.acquire_instance_lock()
            assert third is not None, "持锁句柄关闭后应可再取（句柄随进程生死，不留 stale）"
            third.close()
        finally:
            runner.STATE_DIR = old

    def test_main_declines_without_touching_subprocess(self, monkeypatch, tmp_path: Path):
        calls: list[list[str]] = []

        class _Fake:
            def run(self, cmd, **kwargs):  # noqa: ANN001, ANN002, ANN003
                calls.append(list(cmd))
                return SimpleNamespace(returncode=0, stdout="", stderr="")

        monkeypatch.setattr(runner, "subprocess", _Fake())
        monkeypatch.setattr(runner, "acquire_instance_lock", lambda: None)
        monkeypatch.setattr(runner, "load_symbols", lambda period, start: ["S1", "S2"])
        monkeypatch.setattr(
            sys,
            "argv",
            ["x", "--periods", "daily", "--shard-size", "2", "--state-dir", str(tmp_path)],
        )
        assert runner.main() == 0, "让路是正确行为不是故障，但必须零重灌"
        assert calls == [], "第二个实例不得起任何回填子进程"
        assert list(tmp_path.glob("daily_shard_*.json")) == [], "让路不得留下片态"


# ────────────────────────────── P4 年切窗与超时留态 ──────────────────────────────


class TestYearWindows:
    def test_windows_cover_start_to_end_without_gap(self):
        w = runner.year_windows("2021-06-15", "2023-02-03")
        assert w == [("2021-06-15", "2021-12-31"), ("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-02-03")]

    def test_single_year_window_is_clipped_to_input(self):
        assert runner.year_windows("2026-08-01", "2026-08-20") == [("2026-08-01", "2026-08-20")]

    def test_reversed_range_raises(self):
        with pytest.raises(ValueError):
            runner.year_windows("2026-05-01", "2026-04-01")


class TestTimeoutShardMustLeaveState:
    """R3 治本判据：超时片必须落 state，否则该片每晚从头再来且账面查无痕迹。"""

    def _setup(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(runner, "STATE_DIR", tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)

    def test_timeout_writes_exit_timeout_state(self, monkeypatch, tmp_path: Path):
        self._setup(monkeypatch, tmp_path)

        class _Boom:
            def __init__(self) -> None:
                self.n = 0

            def run(self, cmd, **kwargs):  # noqa: ANN001, ANN002, ANN003
                self.n += 1
                raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout", 0))

        monkeypatch.setattr(runner, "subprocess", _Boom())
        rec = runner.run_shard("daily", 24, ["S1", "S2"], "2021-01-01", "2021-12-31")
        sj = tmp_path / "daily_shard_024.json"
        assert sj.exists(), "超时片必须留态——旧写法这里直接抛出去，state 一支不落"
        saved = json.loads(sj.read_text(encoding="utf-8"))
        assert saved["exit"] == "timeout"
        assert saved["timed_out_window"] == ["2021-01-01", "2021-12-31"]
        assert rec["exit"] == "timeout"

    def test_timeout_record_is_not_treated_as_done(self):
        today = datetime.datetime.now().isoformat(timespec="seconds")
        assert runner.shard_already_done({"exit": "timeout", "finished_at": today}) is False

    def test_completed_windows_are_reused_on_resume(self, monkeypatch, tmp_path: Path):
        self._setup(monkeypatch, tmp_path)
        seen: list[tuple[str, str]] = []

        class _Recorder:
            def run(self, cmd, **kwargs):  # noqa: ANN001, ANN002, ANN003
                i = cmd.index("--end")
                seen.append((cmd[cmd.index("--start-daily") + 1], cmd[i + 1]))
                return SimpleNamespace(returncode=0, stdout="", stderr="")

        monkeypatch.setattr(runner, "subprocess", _Recorder())
        runner.run_shard("daily", 7, ["S1"], "2021-01-01", "2023-12-31", resume=[("2021-01-01", "2021-12-31")])
        assert [w[0] for w in seen] == ["2022-01-01", "2023-01-01"], "已完成的窗不得重跑"

    def test_resume_is_refused_when_symbol_set_changes(self, monkeypatch, tmp_path: Path):
        self._setup(monkeypatch, tmp_path)
        today = datetime.datetime.now().isoformat(timespec="seconds")
        rec = {
            "finished_at": today,
            "symbols_sha256": "deadbeefdeadbeef",
            "start_daily": "2021-01-01",
            "end": "2023-12-31",
            "done_windows": [["2021-01-01", "2021-12-31"]],
        }
        assert runner.resumable_windows(rec, "1111111111111111", "2021-01-01", "2023-12-31") == []
        assert runner.resumable_windows(rec, "deadbeefdeadbeef", "2021-01-01", "2023-12-31") == [
            ("2021-01-01", "2021-12-31")
        ], "同指纹同起止才该接续"

    def test_resume_expires_next_day(self):
        y = (datetime.date.today() - datetime.timedelta(days=1)).isoformat() + "T02:40:00"
        rec = {
            "finished_at": y,
            "symbols_sha256": "abc",
            "start_daily": "2021-01-01",
            "end": "2021-12-31",
            "done_windows": [["2021-01-01", "2021-12-31"]],
        }
        assert runner.resumable_windows(rec, "abc", "2021-01-01", "2021-12-31") == []

    def test_state_written_before_first_window_so_killed_shard_is_visible(self, monkeypatch, tmp_path: Path):
        """跑之前就落"在跑"态：硬杀/断电也看得见，不再只有"跑过但查无此片"。"""
        monkeypatch.setattr(runner, "STATE_DIR", tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)
        states: list[str] = []

        class _Peek:
            def run(self, cmd, **kwargs):  # noqa: ANN001, ANN002, ANN003
                sj = tmp_path / "daily_shard_000.json"
                states.append(json.loads(sj.read_text(encoding="utf-8"))["exit"] if sj.exists() else "MISSING")
                return SimpleNamespace(returncode=0, stdout="", stderr="")

        monkeypatch.setattr(runner, "subprocess", _Peek())
        runner.run_shard("daily", 0, ["S1"], "2021-01-01", "2021-12-31")
        assert states[0] == "running", "第一个窗开跑前 state 就该存在"
