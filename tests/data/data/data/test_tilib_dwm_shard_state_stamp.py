# [TTL] permanent
# [MODULE] tests.data.data.data.test_tilib_dwm_shard_state_stamp
# [DOMAIN] D_DATA
"""dwm 分片完成态的"当日戳"判据测试（2026-10-09 批复 P2，两文件同袋的另一半）。

大白话：夜跑脚本以前靠"每晚删掉整个完成态目录"来逼它重来，结果每一晚都把全史重灌一遍
（实测单趟插入 11,227,985 行）。现在改成"只有当天完成的片才跳过"，于是
同一晚重启＝零重灌，隔到次日＝照旧全量重算（不牺牲新鲜度）。
三条红证缺一不算修完：①当日 exit=0 跳过且二次启动零插入 ②昨日 exit=0 必重算
③当日 exit!=0 必重算。零网络零生产写（state 目录走 tmp_path）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[4]
RUNNER = ROOT / "scripts" / "data" / "tilib_dwm_shard_runner.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("tilib_dwm_shard_runner_under_test", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


runner = _load_runner()


class _FakeSubprocess:
    """替掉子进程真跑：只记账并返回 exit=0（可切换成 exit=1）。"""

    def __init__(self, returncode: int = 0) -> None:
        self.calls: list[list[str]] = []
        self.returncode = returncode

    def run(self, cmd, **kwargs):  # noqa: ANN002, ANN003 — 替身需吞掉任意关键字
        self.calls.append(list(cmd))
        return SimpleNamespace(returncode=self.returncode, stdout="", stderr="")


def _shards_worked(fake: _FakeSubprocess) -> int:
    """数"跑过几片"而不是"起了几个子进程"——P4 之后一片按年切窗，一片＝多个子进程。

    判据仍然咬得住原意：同一片的所有窗共用同一个 --symbols-file，去重即片数。
    """
    return len({c[c.index("--symbols-file") + 1] for c in fake.calls if "--symbols-file" in c})


def _run_main(monkeypatch, tmp_path: Path, fake: _FakeSubprocess, shards: int = 2) -> int:
    monkeypatch.setattr(runner, "subprocess", fake)
    # P3 单实例锁必须替掉：本用例一晚连跑两次是设计语义，若让真锁活着，
    # 第二次会走"让路退出"分支而把 calls==0 的断言喂成假绿（测的是锁，不是幂等）。
    monkeypatch.setattr(runner, "acquire_instance_lock", lambda: object())
    monkeypatch.setattr(runner, "load_symbols", lambda period, start: [f"S{i}" for i in range(shards * 2)])
    monkeypatch.setattr(
        sys,
        "argv",
        ["tilib_dwm_shard_runner.py", "--periods", "daily", "--shard-size", "2", "--state-dir", str(tmp_path)],
    )
    return runner.main()


def _state_files(tmp_path: Path) -> list[Path]:
    return sorted(tmp_path.glob("daily_shard_*.json"))


class TestShardStampPredicate:
    """纯判据腿：日期戳缺失/过期/非零退出都必须重算。"""

    def test_today_zero_exit_is_done(self):
        rec = {"exit": 0, "finished_at": datetime.now().isoformat(timespec="seconds")}
        assert runner.shard_already_done(rec) is True

    def test_yesterday_zero_exit_must_recompute(self):
        y = (date.today() - timedelta(days=1)).isoformat() + "T03:14:00"
        assert runner.shard_already_done({"exit": 0, "finished_at": y}) is False

    def test_today_nonzero_exit_must_recompute(self):
        today = datetime.now().isoformat(timespec="seconds")
        assert runner.shard_already_done({"exit": 1, "finished_at": today}) is False

    def test_missing_stamp_must_recompute(self):
        """旧格式 state（无 finished_at）不得被当成已完成——宁重灌不冻结。"""
        assert runner.shard_already_done({"exit": 0}) is False


class TestNightlyRestartIdempotence:
    """红证①：同一晚二次启动，已完成片零重灌（这才是"止血"本体）。"""

    def test_second_pass_within_same_day_inserts_nothing(self, monkeypatch, tmp_path: Path):
        first = _FakeSubprocess()
        assert _run_main(monkeypatch, tmp_path, first) == 0
        assert _shards_worked(first) == 2, "首趟应跑两片"
        assert len(_state_files(tmp_path)) == 2

        second = _FakeSubprocess()
        assert _run_main(monkeypatch, tmp_path, second) == 0
        assert second.calls == [], f"当晚重启不得重灌任何片：{second.calls}"

    def test_next_day_state_forces_full_recompute(self, monkeypatch, tmp_path: Path):
        """红证②：把 state 改成昨天 ⇒ 必须整片重算（否则日频指标会冻结）。"""
        first = _FakeSubprocess()
        _run_main(monkeypatch, tmp_path, first)
        y = (date.today() - timedelta(days=1)).isoformat() + "T02:40:00"
        for sj in _state_files(tmp_path):
            rec = json.loads(sj.read_text(encoding="utf-8"))
            rec["finished_at"] = y
            sj.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        again = _FakeSubprocess()
        _run_main(monkeypatch, tmp_path, again)
        assert _shards_worked(again) == 2, "隔日必须重算，跳过＝指标停摆"

    def test_failed_shard_recomputes_within_same_day(self, monkeypatch, tmp_path: Path):
        """红证③：当日 exit!=0 的片必须重算（旧行为会因 state 存在而... 不，旧行为是无条件跳过 exit=0）。"""
        bad = _FakeSubprocess(returncode=1)
        assert _run_main(monkeypatch, tmp_path, bad) == 1, "有失败片时汇总 rc 必须非零"
        assert _shards_worked(bad) == 2
        retry = _FakeSubprocess(returncode=1)
        assert _run_main(monkeypatch, tmp_path, retry) == 1
        assert _shards_worked(retry) == 2, "exit!=0 的片即便当日也必须重算"


def test_entry_script_no_longer_wipes_state():
    """入口脚本必须不再抹掉完成态（否则当日戳判据被绕过＝每晚全史重灌复发）。"""
    ps1 = (ROOT / "scripts" / "data" / "backfill_night.ps1").read_text(encoding="utf-8", errors="replace")
    live = [ln for ln in ps1.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert not [ln for ln in live if "dwm_shard_state" in ln], "生产行里不得再出现抹 state 的语句"
    assert RUNNER.exists()
