# [TTL] permanent
# [MODULE] tests.trading.runtime.test_process_reaper_incubation
# [DOMAIN] D_TRADING
"""M3 治理战役验收单测：孵化-收割闭环（reaper 消费 incubator 登记表）。

覆盖：
- 超寿存活进程 → 树杀 + ledger 回写 reaped 戳（真实 sleep 子进程）
- 未超寿 → 不杀；whitelist 命中 → 不杀只 report；已退出/已收割 → 跳过
- 双端契约：reaper 的 ledger 路径常量与 process_incubator.ledger_dir() 对齐
  （零 zephyr import 隔离下的路径漂移防线）
- ledger 损坏行跳过；缺席 = 零动作

测试隔离：ledger 路径 monkeypatch 到 tmp_path；不碰生产 data/runtime/process_reaper_keep.txt。
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.trading import process_reaper as pr  # noqa: E402


def _make_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """ledger 路径重定向 tmp（绝对文件 Path 参与拼接时 pathlib 取绝对侧，天然生效）。"""
    ledger = tmp_path / "process_incubator" / "ledger.jsonl"
    monkeypatch.setattr(pr, "_INCUBATOR_LEDGER_REL", ledger)
    return ledger


def _write_records(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


def _spawn_sleeper(seconds: int = 30) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-c", f"import time; time.sleep({seconds})"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _record(pid: int, **kw) -> dict:
    base = {
        "record_id": kw.pop("record_id", "rec-" + str(pid)),
        "child_pid": pid,
        "parent_pid": 1,
        "root_pid": 1,
        "ancestor_chain": [pid, 1],
        "name": "sleeper",
        "cmd": " ".join([sys.executable, "-c", "sleep"]),
        "spawned_at": time.time() - 3600,
        "expected_lifetime_s": 60.0,
        "owner": "test",
        "exited_at": None,
        "reaped": False,
    }
    base.update(kw)
    return base


def _all_procs(pid: int) -> dict[int, dict]:
    return {pid: {"pid": pid, "ppid": 1, "cmdline": sys.executable, "name": "python"}}


# ── 收割判定 ─────────────────────────────────────────────────────────────────


def test_expired_alive_process_killed_and_marked(tmp_path, monkeypatch):
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        _write_records(ledger, [_record(proc.pid, expected_lifetime_s=60.0)])  # 1h 前孵化，寿命 60s → 超寿
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(_all_procs(proc.pid), dry_run=False, report=report)
        assert len(report.killed) == 1
        assert report.killed[0]["reason"].startswith("incubation_expired")
        assert report.killed[0]["killed"] is True
        # ledger 回写 reaped
        rec = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        assert rec["reaped"] is True and rec["reaped_at"] > 0
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_not_expired_not_killed(tmp_path, monkeypatch):
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        _write_records(ledger, [_record(proc.pid, spawned_at=time.time(), expected_lifetime_s=3600.0)])
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(_all_procs(proc.pid), dry_run=False, report=report)
        assert report.killed == []
        assert proc.poll() is None  # 仍活
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_whitelisted_reported_not_killed(tmp_path, monkeypatch):
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        rec = _record(proc.pid, cmd="sacred-keep-pattern --run")
        _write_records(ledger, [rec])
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(
            _all_procs(proc.pid),
            dry_run=False,
            report=report,
            whitelist_res=[],
            keep_subs=["sacred-keep-pattern"],
        )
        assert report.killed == []
        assert len(report.reported) == 1
        assert report.reported[0]["reason"] == "incubation_expired_whitelisted"
        assert proc.poll() is None
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_dead_and_reaped_records_skipped(tmp_path, monkeypatch):
    ledger = _make_ledger(tmp_path, monkeypatch)
    _write_records(
        ledger,
        [
            _record(4294901760, exited_at=time.time()),  # 已退出
            _record(4294901761, reaped=True),  # 已收割
            _record(0),  # 非法 pid
        ],
    )
    report = pr.ReapReport(dry_run=False)
    pr._reap_incubated_expired({4294901760: {}, 4294901761: {}}, dry_run=False, report=report)
    assert report.killed == []


def test_dry_run_reports_without_mark(tmp_path, monkeypatch):
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        _write_records(ledger, [_record(proc.pid)])
        report = pr.ReapReport(dry_run=True)
        pr._reap_incubated_expired(_all_procs(proc.pid), dry_run=True, report=report)
        assert len(report.killed) == 1 and report.killed[0]["killed"] is False
        rec = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        assert rec["reaped"] is False  # dry-run 不回写
    finally:
        proc.terminate()
        proc.wait(timeout=10)


# ── 健壮性与双端契约 ─────────────────────────────────────────────────────────


def test_corrupt_ledger_lines_skipped(tmp_path, monkeypatch):
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        good = _record(proc.pid)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text("{broken\n" + json.dumps(good) + "\n", encoding="utf-8")
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(_all_procs(proc.pid), dry_run=False, report=report)
        assert len(report.killed) == 1
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_missing_ledger_noop(tmp_path, monkeypatch):
    _make_ledger(tmp_path, monkeypatch)  # 不写文件
    report = pr.ReapReport(dry_run=False)
    pr._reap_incubated_expired({123: {}}, dry_run=False, report=report)
    assert report.killed == []


def test_ledger_path_contract_with_incubator():
    """双端契约：reaper 的 ledger 相对路径与 process_incubator.ledger_dir() 对齐。"""
    import zephyr.shared.infra.process_incubator as inc

    expected = inc.ledger_dir() / "ledger.jsonl"
    assert pr.REPO_ROOT / pr._INCUBATOR_LEDGER_REL == expected, (
        "reaper 与 incubator 的 ledger 路径漂移——收割闭环断链，须同步两侧常量"
    )
