# [TTL] permanent
# [MODULE] tests.trading.runtime.test_process_reaper_identity
# [DOMAIN] D_TRADING
"""孵化收割身份复核的红/绿证明（wave7.3 缺陷②＋backfix 批复① 通道对齐）。

修前（红）：ledger 登记的 child_pid 被无关进程复用（create_time 不符）——
_reap_incubated_expired 只查 pid 在册，把复用者当孵化子进程进入收割判定。
修后（绿）：登记侧快照 child_create_time，收割端三要素复核（born/image/cmd）任一不符
→ 赦免 + 记 identity_mismatches + 非 dry_run 时销账 exited_at；身份全符仍正常收割；
旧格式无 create_time 快照（legacy）时该要素弃权，但 image/cmd 两要素照判，收割照做。

通道改判依据=465f2779（backfix 批复①，2026-10-10）：旧通道
reason=incubation_expired_pid_reuse_skip 已退役，本件断言随之对齐（同 v7 先例）。
**正证与反向钉桩成对**：验收割的两支样本把活体身份取自真起的 sleeper（登记=活体同源），
若图省事用无关 name/cmd，465f2779 的 image/cmd 复核会先赦免⇒"收割正证"退化成空跑；
另有一支 test_identity_alignment_is_load_bearing 把这点钉死（只把 cmd 改歧⇒必不杀）。
红阶段主样本全程 dry_run=True——只证判定不真杀（被复用 pid 在真实环境可能是无辜活体）。
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
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


def _live(
    pid: int, create_time: float, cmdline: str = "innocent.exe --serve", name: str = "innocent"
) -> dict[int, dict]:
    return {
        pid: {
            "pid": pid,
            "ppid": 1,
            "cmdline": cmdline,
            "name": name,
            "create_time": create_time,
        }
    }


# ── PID 复用身份复核（缺陷②本体）────────────────────────────────────────────


def test_pid_reuse_identity_mismatch_skips_and_reports(tmp_path, monkeypatch):
    """红→绿主样本：pid 复用（快照 1000.0 vs 活体现生）必须跳过 + reported。"""
    ledger = _make_ledger(tmp_path, monkeypatch)
    _write_records(ledger, [_record(999999, child_create_time=1000.0)])
    report = pr.ReapReport(dry_run=True)
    pr._reap_incubated_expired(_live(999999, time.time()), dry_run=True, report=report)
    assert report.killed == [], "PID 复用身份不符仍进入收割判定——误杀无辜进程"
    # 通道按 465f2779 对齐：身份不符=赦免并记 identity_mismatches（旧 reported 通道已退役）
    assert len(report.identity_mismatches) == 1, "身份不符未进 identity_mismatches=留痕通道丢失"
    assert report.identity_mismatches[0]["pid"] == 999999
    assert "born_after_registration" in report.identity_mismatches[0]["reason"], "pid 复用机读标记丢失"
    assert report.reported == [], "旧通道已退役——双通道重复记账即红"


def test_matching_identity_still_reaped(tmp_path, monkeypatch):
    """身份一致（真快照）→ 正常收割——复核不放宽也不误伤合法收割。"""
    import psutil

    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        ps = psutil.Process(proc.pid)
        ct = ps.create_time()
        live_cmd = " ".join(ps.cmdline())
        live_name = ps.name()
        _write_records(ledger, [_record(proc.pid, child_create_time=ct, cmd=live_cmd, name=live_name)])
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(_live(proc.pid, ct, cmdline=live_cmd, name=live_name), dry_run=False, report=report)
        assert len(report.killed) == 1 and report.killed[0]["killed"] is True
        rec = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
        assert rec["reaped"] is True
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_legacy_record_without_snapshot_still_reaped(tmp_path, monkeypatch):
    """旧格式登记（无 child_create_time）→ 该要素弃权（born 锚退回 spawned_at），
    image/cmd 两要素照判，收割行为不变（fail-open 不追溯）。"""
    ledger = _make_ledger(tmp_path, monkeypatch)
    proc = _spawn_sleeper()
    try:
        import psutil

        ps = psutil.Process(proc.pid)
        live_cmd = " ".join(ps.cmdline())
        live_name = ps.name()
        reg_at = time.time() - 3600.0
        _write_records(ledger, [_record(proc.pid, spawned_at=reg_at, cmd=live_cmd, name=live_name)])
        report = pr.ReapReport(dry_run=False)
        pr._reap_incubated_expired(
            _live(proc.pid, reg_at - 5.0, cmdline=live_cmd, name=live_name), dry_run=False, report=report
        )
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


def test_identity_alignment_is_what_enables_reaping(tmp_path, monkeypatch):
    """判别力反向钉桩（保住上面两支正证的意义）：同一 pid、同一 create_time、同一 name，
    **只把 cmd 一个要素改歧**，必从"收割"翻成"赦免+留痕"。若有人为了省事把活体身份写成
    无关 name/cmd，正证会静默退化成空跑——本支让那种改法当场见红。"""
    ledger = _make_ledger(tmp_path, monkeypatch)
    ct = time.time() - 120.0
    rec = _record(65001, spawned_at=ct - 3600.0, child_create_time=ct, cmd="python worker.py", name="python.exe")
    _write_records(ledger, [rec])
    report = pr.ReapReport(dry_run=True)
    pr._reap_incubated_expired(
        _live(65001, ct, cmdline="python totally_other.py", name="python.exe"), dry_run=True, report=report
    )
    assert report.killed == [], "cmd 已歧仍进入收割=身份复核这道闸失效"
    assert len(report.identity_mismatches) == 1, "cmd_diverged 未留痕"
    assert "cmd_diverged" in report.identity_mismatches[0]["reason"]
