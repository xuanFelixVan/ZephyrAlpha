# [A_test] module_id: SRC-TST-GWM-ROTLOCK | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] tests.test_log_rotation_append_lock
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

"""C-2 log_rotation 接锁回归测试（2026-09-16 裁定#287）：轮转与追加并发零互踩。

病根（GW11 实证）：LogRotationManager.rotate() 的 read→archive→truncate 全程无锁，
与 AuditWriter 追加并发互踩——轮转窗口内写入的事件既不在归档也不在清空后的活跃段
（丢失）或半行撕裂（破坏哈希链）。取证期"冻结一切轮转"（16befe06 留痕）。

治本：轮转临界区持与追加方同一把跨进程文件锁（writer._cross_process_append_lock）；
核心不可变链目录（data/audit_trail）整目录禁轮转（retention.py 不变量同源）。

隔离纪律：全部写入 tmp_path 沙箱；AuditWriter 显式 hmac_key（不触生产密钥），
enable_merkle=False。
"""

from __future__ import annotations

import gzip
import json
import threading
import time as _time
from pathlib import Path

import pytest

from zephyr.gov_audit.log_rotation import LogRotation, LogRotationManager
from zephyr.gov_audit.writer import AuditWriter


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "audit_history"


def _writer(data_dir: Path) -> AuditWriter:
    return AuditWriter(data_dir=data_dir, enable_merkle=False, hmac_key="test-key")


def _iter_segment_lines(paths: list[Path]) -> list[dict]:
    events: list[dict] = []
    for p in paths:
        if p.name.endswith(".gz"):
            events.extend(
                json.loads(l)
                for l in gzip.open(p, "rt", encoding="utf-8").read().splitlines()
                if l.strip()
            )
        else:
            events.extend(json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    return events


class TestLogRotationManagerAppendLock:
    def test_rotate_concurrent_writer_zero_event_loss(self, data_dir):
        """追加线程与轮转并发 → 守恒律：成功写入数==Σ有效轮转归档数+最终活跃段数。

        记账口径：
        - writer.write 抛 TimeoutError=OS 锁 10s 耗尽的设计内 fail-closed 丢弃
          （裁定#266 既有语义，未落盘），不计入"应恢复"集合；
        - 归档名为按日命名（audit-trail-<date>），同日多次 force 轮转后段覆写前段
          （既有契约），故"零丢失"守恒律经由 RotationRecord.entries_rotated 计数
          链证明：每条成功落盘事件要么计入某次有效轮转、要么仍在活跃段——GW11
          伤型（成功落盘却两头落空）当且仅当锁互斥被破坏时出现。
        """
        data_dir.mkdir(parents=True)
        w = _writer(data_dir)
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=True)

        successes = 0
        fail_closed_drops = 0
        rotated_total = 0
        lock = threading.Lock()

        def writer_loop():
            nonlocal successes, fail_closed_drops
            for i in range(80):
                try:
                    w.write({"event_type": "generic", "agent_id": "rot-lock-test", "seq": i})
                    with lock:
                        successes += 1
                except TimeoutError:
                    with lock:
                        fail_closed_drops += 1
                _time.sleep(0.005)

        t = threading.Thread(target=writer_loop)
        t.start()
        for _ in range(6):
            record = manager.rotate(force=True)
            if record is not None:
                with lock:
                    rotated_total += record.entries_rotated
            _time.sleep(0.01)
        t.join(120)
        active_events = _iter_segment_lines([data_dir / "events.jsonl"])

        # 守恒律：成功落盘 == 已归档计入 + 活跃段现存（差值=轮转窗口互踩=GW11 伤型）
        with lock:
            assert successes == rotated_total + len(active_events), (
                f"event loss during rotation: written={successes} "
                f"archived_accounted={rotated_total} active_now={len(active_events)} "
                f"fail_closed_drops={fail_closed_drops}"
            )
        entry_ids = [e["entry_id"] for e in active_events]
        assert len(entry_ids) == len(set(entry_ids)), "duplicate entry_id (interleave corruption)"

    def test_rotate_blocks_while_append_lock_held(self, data_dir):
        """互斥语义：追加锁被持有时 rotate 阻塞不进入临界区（与追加方同锁域）。"""
        from zephyr.gov_audit.writer import _cross_process_append_lock

        data_dir.mkdir(parents=True)
        active = data_dir / "events.jsonl"
        active.write_text('{"seq": 0}\n', encoding="utf-8")
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=False)

        release = threading.Event()
        holder_entered = threading.Event()

        def hold():
            with _cross_process_append_lock(active):
                holder_entered.set()
                release.wait(30)

        threading.Thread(target=hold, daemon=True).start()
        assert holder_entered.wait(10)

        rotated_box: list[object] = []
        rotate_done = threading.Event()

        def rotate_call():
            rotated_box.append(manager.rotate(force=True))
            rotate_done.set()

        threading.Thread(target=rotate_call, daemon=True).start()
        _time.sleep(0.5)
        assert not rotate_done.is_set(), "rotate entered critical section while append lock was held"
        release.set()
        assert rotate_done.wait(30), "rotate not released after lock holder exited"
        assert rotated_box[0] is not None, "rotate did not complete after release"

    def test_rotate_reset_chain_starts_at_genesis(self, data_dir):
        """轮转后新段从 genesis 重链（锁内重读空尾）——分断合法语义下链不出叉。"""
        data_dir.mkdir(parents=True)
        w = _writer(data_dir)
        w.write({"event_type": "generic", "agent_id": "pre-rotate"})
        manager = LogRotationManager(data_dir=data_dir, compress_rotated=False)
        record = manager.rotate(force=True)
        assert record is not None and record.entries_rotated == 1
        w.write({"event_type": "generic", "agent_id": "post-rotate"})
        lines = [json.loads(l) for l in (data_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == 1
        assert lines[0]["prev_hash"] == "0" * 64  # 锁内实时重读尾=空 → genesis
        # 归档段内容原样保全
        archived = next(data_dir.glob("audit-trail-*.jsonl"))
        assert len(archived.read_text(encoding="utf-8").splitlines()) == 1


class TestLogRotationCoreChainGuard:
    def test_core_chain_dir_files_skipped(self, tmp_path, monkeypatch):
        """核心不可变链目录（AUDIT_DATA_DIR 指向处）整目录禁轮转——skip 留痕。"""
        import zephyr.shared.io.paths as paths_mod

        fake_core = tmp_path / "audit_trail"
        fake_core.mkdir()
        (fake_core / "events.jsonl").write_text('{"core": true}\n', encoding="utf-8")
        monkeypatch.setattr(paths_mod, "AUDIT_DATA_DIR", fake_core)

        other = tmp_path / "audit_history"
        other.mkdir()
        (other / "tool.jsonl").write_text('{"tool": true}\n', encoding="utf-8")

        rot = LogRotation(log_dir=other, extra_dirs=(fake_core,))  # 核心目录在覆盖面内才会被枚举
        result = rot.rotate()  # not dry_run——守卫必须对真轮转生效
        # 核心链文件被跳过且原样保全
        assert (fake_core / "events.jsonl").exists()
        assert {"file": "events.jsonl", "action": "skip", "reason": "core_immutable_chain"} in result["details"]
        assert result["compressed"] == 0
        # 超限的工具日志（默认 100MB 阈值未超）不动——仅验证守卫不误伤

    def test_oversized_jsonl_compressed_under_lock(self, tmp_path):
        """超限 .jsonl 走压缩路径（持锁段内完成 compress+remove）。"""
        d = tmp_path / "logs"
        d.mkdir()
        big = d / "tool.jsonl"
        big.write_text('{"pad": "' + "x" * 200 + '"}\n', encoding="utf-8")
        rot = LogRotation(log_dir=d, extra_dirs=(), max_size_mb=0)  # 0MB 阈值 → 必超限
        result = rot.rotate()
        assert result["compressed"] == 1
        assert not big.exists()
        assert (d / "tool.jsonl.gz").exists()
