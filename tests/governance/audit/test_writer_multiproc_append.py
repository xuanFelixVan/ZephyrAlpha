# [A_test] module_id: SRC-TST-GWA-MULTI | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.4
# [MODULE] tests.test_writer_multiproc_append
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-020 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""GW-A 治本回归测试（2026-09-16）：AuditWriter 跨进程并发 append 链完整性。

根因（主仓取证实证）：多写方各持陈旧内存 _last_hash 交错落盘——events.jsonl
5,595 处 prev 断链，签名=#35155/#35156 同 prev_hash 同秒（两写方并发）。
治本：append 临界区跨进程文件锁（_cross_process_append_lock，msvcrt/fcntl
字节排他锁）+ 锁内实时重读文件尾哈希（_read_tail_entry_hash）。

子进程用 sys.executable -c 内联 worker（规避 pytest 测试模块被
multiprocessing spawn 再导入的平台差异），全部写入 tmp_path 沙箱。
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time as _time
from pathlib import Path

import pytest

from zephyr.gov_audit.integrity import IntegrityVerifier
from zephyr.gov_audit.writer import (
    _GENESIS_HASH,
    _cross_process_append_lock,
    _read_tail_entry_hash,
    AuditWriter,
)

_REPO_SRC = str(Path(__file__).resolve().parents[3] / "src")

# 内联子进程 worker：独立 AuditWriter 实例向同一 events.jsonl 追加 n 条事件
_CHILD_WORKER = (
    "import sys; from pathlib import Path\n"
    "sys.path.insert(0, sys.argv[4])\n"
    "from zephyr.gov_audit.writer import AuditWriter\n"
    "w = AuditWriter(data_dir=Path(sys.argv[1]), enable_merkle=False, hmac_key='test-key')\n"
    "for i in range(int(sys.argv[2])):\n"
    "    w.write({'event_type': 'generic', 'agent_id': 'writer-' + sys.argv[3], 'seq': i})\n"
)


def _spawn_writer_children(data_dir: Path, n_workers: int, per_worker: int) -> None:
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", _CHILD_WORKER, str(data_dir), str(per_worker), str(i), _REPO_SRC],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        for i in range(n_workers)
    ]
    errors = []
    for p in procs:
        _, err = p.communicate(timeout=120)
        if p.returncode != 0:
            errors.append(err.decode("utf-8", errors="replace")[-500:])
    assert not errors, "child writers failed:\n" + "\n".join(errors)


def _read_events(data_dir: Path) -> list[dict]:
    lines = (data_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lines if l.strip()]


@pytest.fixture
def data_dir(tmp_path):
    d = tmp_path / "audit_trail"
    d.mkdir()
    return d


class TestMultiProcessAppend:
    def test_multi_process_appends_produce_complete_chain(self, data_dir):
        """4 进程 × 25 事件并发追加 → 全链 verify_chain 零 issue（GW-A 治本验收）。"""
        seed = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        seed.write({"event_type": "generic", "agent_id": "seed"})
        _spawn_writer_children(data_dir, n_workers=4, per_worker=25)

        report = IntegrityVerifier(event_log_path=data_dir / "events.jsonl", hmac_key="test-key").verify_chain()
        assert report["events_checked"] == 101
        assert report["status"] == "valid", f"chain issues: {report['issues'][:5]}"

    def test_no_same_prev_signature_between_consecutive_events(self, data_dir):
        """#35155/#35156 同 prev_hash 签名必须绝迹：相邻两事件 prev_hash 不得相同。"""
        _spawn_writer_children(data_dir, n_workers=3, per_worker=20)
        events = _read_events(data_dir)
        assert len(events) == 60
        for a, b in zip(events, events[1:]):
            assert a["prev_hash"] != b["prev_hash"], (
                f"same-prev signature pair detected (interleaved stale writers): "
                f"{a['entry_id']} / {b['entry_id']}"
            )

    def test_two_instances_same_process_chain_complete(self, data_dir):
        """同进程双 AuditWriter 实例交错写（gate_engine 双实例场景）→ 链完整。

        两实例均在首写前构造（持同一陈旧 _last_hash）——治本前此场景必断链。
        """
        w1 = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        w2 = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        for i in range(10):
            w1.write({"event_type": "generic", "agent_id": "inst-1", "seq": i})
            w2.write({"event_type": "generic", "agent_id": "inst-2", "seq": i})
        report = IntegrityVerifier(event_log_path=data_dir / "events.jsonl", hmac_key="test-key").verify_chain()
        assert report["events_checked"] == 20
        assert report["status"] == "valid", f"chain issues: {report['issues'][:5]}"


class TestReadTailEntryHash:
    def test_missing_file_returns_genesis(self, tmp_path):
        assert _read_tail_entry_hash(tmp_path / "nope.jsonl") == _GENESIS_HASH

    def test_empty_file_returns_genesis(self, tmp_path):
        p = tmp_path / "events.jsonl"
        p.write_bytes(b"")
        assert _read_tail_entry_hash(p) == _GENESIS_HASH

    def test_returns_last_complete_event_hash(self, data_dir):
        w = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        h1 = w.write({"event_type": "generic", "agent_id": "a"})
        h2 = w.write({"event_type": "generic", "agent_id": "b"})
        assert _read_tail_entry_hash(data_dir / "events.jsonl") == h2
        assert h1 != h2

    def test_skips_torn_tail_line(self, data_dir):
        """崩溃残留半行（无换行）→ 跳过，回溯最后一条完整事件。"""
        w = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        h1 = w.write({"event_type": "generic", "agent_id": "a"})
        with open(data_dir / "events.jsonl", "ab") as f:
            f.write(b'{"partial": tru')  # 撕裂尾行
        assert _read_tail_entry_hash(data_dir / "events.jsonl") == h1

    def test_large_file_beyond_first_chunk(self, data_dir):
        """尾行跨块（>64KB 缓冲）：大体积完整行仍可定位。"""
        w = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        w.write({"event_type": "generic", "agent_id": "small"})
        big_hash = w.write({"event_type": "generic", "agent_id": "big", "payload": "x" * 200_000})
        assert _read_tail_entry_hash(data_dir / "events.jsonl") == big_hash


class TestCrossProcessAppendLock:
    def test_lock_file_created_alongside_event_log(self, data_dir):
        w = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        w.write({"event_type": "generic", "agent_id": "a"})
        assert (data_dir / "events.jsonl.lock").exists()

    def test_blocking_acquire_waits_then_succeeds_after_release(self, data_dir):
        """互斥阻塞语义：持有期间竞争者阻塞不进入，释放后立即获取（OS 阻塞锁）。"""
        held = threading.Event()
        release = threading.Event()

        def hold():
            with _cross_process_append_lock(data_dir / "events.jsonl"):
                held.set()
                release.wait(30)

        t = threading.Thread(target=hold)
        t.start()
        assert held.wait(10), "holder thread did not acquire"

        entered = threading.Event()
        box: list[bool] = []

        def contender():
            with _cross_process_append_lock(data_dir / "events.jsonl"):
                entered.set()
                box.append(True)

        c = threading.Thread(target=contender)
        c.start()
        _time.sleep(0.5)  # 给竞争者进入阻塞的时间窗口（OS 阻塞等待）
        assert not box and not entered.is_set(), "contender entered while lock was held (mutual exclusion broken)"
        release.set()
        assert entered.wait(20), "contender not released after holder exited"
        c.join(5)
        t.join(5)
        assert box, "contender did not complete after release"

    def test_lock_auto_released_after_holder_process_crash(self, data_dir):
        """持锁进程被强杀 → OS 关句柄自动释放，无 stale 锁残留。"""
        marker = data_dir / "lock_held.marker"
        child = (
            "import pathlib, sys, time\n"
            "sys.path.insert(0, sys.argv[2])\n"
            "from zephyr.gov_audit.writer import _cross_process_append_lock\n"
            "with _cross_process_append_lock(pathlib.Path(sys.argv[1])):\n"
            "    pathlib.Path(sys.argv[3]).write_text('held')\n"
            "    time.sleep(30)\n"
        )
        p = subprocess.Popen(
            [sys.executable, "-c", child, str(data_dir / "events.jsonl"), _REPO_SRC, str(marker)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            deadline = _time.monotonic() + 20.0
            while not marker.exists():
                assert p.poll() is None, "holder process died before acquiring lock"
                assert _time.monotonic() < deadline, "holder never acquired lock (OS wait exhausted?)"
                _time.sleep(0.05)
        finally:
            p.kill()
            p.wait(timeout=10)
        # 子进程死后锁必须立即可获取（OS 释放，无残留）
        with _cross_process_append_lock(data_dir / "events.jsonl"):
            pass
