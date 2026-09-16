# [A_test] module_id: SRC-TST-GWM-WREST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.4
# [MODULE] tests.test_writer_restart_overlap
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

"""C-3 长驻写方重启 overlap 红蓝测试（2026-09-16 裁定#287）：重启窗口并发追加零链损伤。

场景：长驻写方（旧实例/旧进程）存活期间，重启替身（新实例/新进程）启动并并发追加。

机理（裁定#266 治本的直接推论）：append 临界区=跨进程文件锁+锁内实时重读文件尾——
新旧实例并发追加被 OS 锁逐条串行化，锁等待即"overlap 损伤窗口"的上界，链分叉窗口
恒为 0（任何一方的 prev 都来自持锁瞬间的文件真实尾部）。本套件以计时留证实证：
overlap 墙钟窗口内 链分叉=0、事件丢失=0（计入显式 fail-closed 丢弃）、同 prev 签名=0。

隔离纪律：全部写入 tmp_path 沙箱；显式 hmac_key；enable_merkle=False。
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
from zephyr.gov_audit.writer import AuditWriter

_REPO_SRC = str(Path(__file__).resolve().parents[3] / "src")

# 内联子进程 worker：独立进程写方向同一 events.jsonl 追加 n 条。
# TimeoutError 容忍：OS 锁 10s 耗尽=设计内 fail-closed 丢弃（裁定#266 语义），
# 子进程上报实际落盘数（CHILD_OK <n>），父侧断言用实际数——负载型抖动不误报。
_CHILD_WORKER = (
    "import sys; from pathlib import Path\n"
    "sys.path.insert(0, sys.argv[4])\n"
    "from zephyr.gov_audit.writer import AuditWriter\n"
    "w = AuditWriter(data_dir=Path(sys.argv[1]), enable_merkle=False, hmac_key='test-key')\n"
    "ok = 0\n"
    "for i in range(int(sys.argv[2])):\n"
    "    try:\n"
    "        w.write({'event_type': 'generic', 'agent_id': 'writer-' + sys.argv[3], 'seq': i})\n"
    "        ok += 1\n"
    "    except TimeoutError:\n"
    "        pass\n"
    "print('CHILD_OK', ok)\n"
)


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "audit_trail"


def _assert_zero_chain_damage(data_dir: Path, expected_min: int) -> int:
    report = IntegrityVerifier(event_log_path=data_dir / "events.jsonl", hmac_key="test-key").verify_chain()
    assert report["status"] == "valid", f"chain damage in restart overlap window: {report['issues'][:5]}"
    assert report["events_checked"] >= expected_min
    lines = [json.loads(l) for l in (data_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    for a, b in zip(lines, lines[1:]):
        assert a["prev_hash"] != b["prev_hash"], "same-prev signature pair (stale-tail fork)"
    return report["events_checked"]


class TestWriterRestartOverlap:
    def test_old_and_new_instance_overlap_window(self, data_dir):
        """同进程重启 overlap：旧实例存活，新实例并发追加——损伤窗口计时留证。"""
        old_writer = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        old_writer.write({"event_type": "generic", "agent_id": "old-warmup"})
        new_writer = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")

        wait_times: list[float] = []
        guard = threading.Lock()

        def timed_write(w, agent, n):
            for i in range(n):
                t0 = _time.monotonic()
                w.write({"event_type": "generic", "agent_id": agent, "seq": i})
                with guard:
                    wait_times.append(_time.monotonic() - t0)

        t0 = _time.monotonic()
        threads = [
            threading.Thread(target=timed_write, args=(old_writer, "old-inst", 60)),
            threading.Thread(target=timed_write, args=(new_writer, "new-inst", 60)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(60)
        window = _time.monotonic() - t0

        checked = _assert_zero_chain_damage(data_dir, expected_min=121)
        with guard:
            max_wait = max(wait_times)
        print(
            f"\n[red-blue] same-process restart overlap: window={window:.3f}s writes={checked} "
            f"chain_forks=0 max_single_write={max_wait * 1000:.1f}ms (serialization upper bound)"
        )

    def test_old_process_alive_new_process_overlap(self, data_dir):
        """跨进程重启 overlap：旧进程写线程持续追加，新进程（重启替身）并发追加。"""
        old_writer = AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")
        old_writer.write({"event_type": "generic", "agent_id": "old-proc-warmup"})

        old_success = 0
        old_fail_closed_drops = 0
        old_errors: list[Exception] = []
        stop = threading.Event()

        def old_loop():
            nonlocal old_success, old_fail_closed_drops, old_errors
            seq = 0
            while not stop.is_set():
                try:
                    old_writer.write({"event_type": "generic", "agent_id": "old-proc", "seq": seq})
                    old_success += 1
                    seq += 1
                except TimeoutError:
                    # OS 锁 10s 耗尽=设计内 fail-closed 丢弃（裁定#266 语义，未落盘）。
                    # 全量负载下可发生；链完整性断言不受影响（丢弃≠叉链≠成功丢失）。
                    old_fail_closed_drops += 1
                except Exception as exc:  # noqa: BLE001 — 非超时异常才是真故障
                    old_errors.append(exc)

        t0 = _time.monotonic()
        th = threading.Thread(target=old_loop, daemon=True)
        th.start()
        proc = subprocess.Popen(
            [sys.executable, "-c", _CHILD_WORKER, str(data_dir), "30", "new-proc", _REPO_SRC],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            out, err = proc.communicate(timeout=180)
            assert proc.returncode == 0, (err or b"").decode("utf-8", errors="replace")[-500:]
        finally:
            stop.set()
            th.join(60)
        window = _time.monotonic() - t0
        assert not old_errors, f"old writer non-timeout failures: {old_errors[:3]}"
        child_ok = int(out.decode().strip().split()[-1])  # 子进程实际落盘数

        checked = _assert_zero_chain_damage(data_dir, expected_min=old_success + child_ok + 1)
        print(
            f"\n[red-blue] cross-process restart overlap: window={window:.3f}s "
            f"old_proc={old_success} new_proc={child_ok}/30 total={checked} "
            f"fail_closed_drops(parent)={old_fail_closed_drops} "
            f"chain_forks=0 lost_events=0"
        )
