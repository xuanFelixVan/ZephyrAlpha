# [TTL] permanent
# [MODULE] tests.trading.runtime.test_process_reaper_identity
# [DOMAIN] D_TRADING
"""wave7.3 缺陷②红/绿证明：孵化收割 PID 复用身份复核。

修前（红）：ledger 登记的 child_pid 被无关进程复用（create_time 不符）——
_reap_incubated_expired 只查 pid 在册，把复用者当孵化子进程进入收割判定。
修后（绿）：登记侧快照 child_create_time，收割端复核不符 → 跳过 + reported
（reason=incubation_expired_pid_reuse_skip）；快照一致仍正常收割；
旧格式无快照（legacy）行为不变（fail-open，不追溯）。

红阶段主样本全程 dry_run=True——只证明"会进入收割判定"而不真杀任何 pid
（被复用 pid 在真实环境可能是无辜活体）。
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


def _live(pid: int, create_time: float, cmdline: str = "innocent.exe --serve") -> dict[int, dict]:
    return {pid: {"pid": pid, "ppid": 1, "cmdline": cmdline, "name": "innocent", "create_time": create_time}}


# ── PID 复用身份复核（缺陷②本体）────────────────────────────────────────────


def test_pid_reuse_identity_mismatch_skips_and_reports(tmp_path, monkeypatch):
    """红→绿主样本：pid 复用（快照 1000.0 vs 活体现生）必须跳过 + reported。"""
    ledger = _make_ledger(tmp_path, monkeypatch)
    _write_records(ledger, [_record(999999, child_create_time=1000.0)])
    report = pr.ReapReport(dry_run=True)
    pr._reap_incubated_expired(_live(999999, time.time()), dry_run=True, report=report)
    assert report.killed == [], "PID 复用身份不符仍进入收割判定——误杀无辜进程"
    assert len(report.reported) == 1
    assert report.reported[0]["reason"] == "incubation_expired_pid_reuse_skip"
    assert report.reported[0]["pid"] == 999999


def test_matching_identity_still_reaped(tmp_path, monkeypatch):
    """身份一致（真快照）→ 正常收割——复核不放宽也不误伤合法收割。"""
    import psutil

    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        ct = psutil.Process(proc.pid).create_time()
        _write_records(ledger, [_record(proc.pid, child_create_time=ct)])
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(_live(proc.pid, ct), dry_run=False, report=report)
        assert len(report.killed) == 1 and report.killed[0]["killed"] is True
        rec = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        assert rec["reaped"] is True
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_legacy_record_without_snapshot_still_reaped(tmp_path, monkeypatch):
    """旧格式登记（无 child_create_time）→ 不判，收割行为不变（fail-open 不追溯）。"""
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        _write_records(ledger, [_record(proc.pid)])
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(_live(proc.pid, time.time()), dry_run=False, report=report)
        assert len(report.killed) == 1
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_incubator_record_carries_identity_snapshot():
    """登记侧契约：IncubationRecord 必须带 child_create_time 快照字段。"""
    import dataclasses

    from zephyr.shared.infra.process_incubator import IncubationRecord

    names = {f.name for f in dataclasses.fields(IncubationRecord)}
    assert "child_create_time" in names, "登记记录缺身份快照字段——收割端复核无输入"
