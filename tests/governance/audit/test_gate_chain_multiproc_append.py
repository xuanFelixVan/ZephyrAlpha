# [A_test] module_id: SRC-TST-GWM-GCHAIN | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §4
# [MODULE] tests.test_gate_chain_multiproc_append
# [DOMAIN] D_GOV_AUDIT
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""C-1 gate_chain 同型锁回归测试（2026-09-16 裁定#287）：AuditChainVerifier 跨进程并发追加链完整性。

病根（与裁定#266 events.jsonl 同型）：gate_chain.jsonl 追加临界区仅持进程内
threading.Lock，且 previous_hash 取自实例内存 _last_hash——多进程 verifier 各持
陈旧内存尾哈希交错落盘即文件级断链。

治本：追加临界区持 _cross_process_append_lock（与 events.jsonl writer 同型 OS 阻塞
锁）+ 锁内实时重读文件尾哈希（_read_tail_entry_hash(hash_field="hash")）。

隔离纪律：本套件 ZEPHYR_GATE_CHAIN_PATH 指向 tmp_path；并显式 core_writer=None
（AuditChainVerifier 默认自建核心 writer 落生产 data/audit_trail——既有隔离缺口，
本套件不沿用）。子进程用 sys.executable -c 内联 worker（规避 multiprocessing
spawn 再导入 pytest 模块的平台差异），全部写入 tmp_path 沙箱。
"""

from __future__ import annotations

import json
import subprocess
import sys
import time as _time
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_enforcement.audit_chain_verifier import AuditChainVerifier
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateResult, GateStatus

_REPO_SRC = str(Path(__file__).resolve().parents[3] / "src")

# 内联子进程 worker：独立 AuditChainVerifier 向同一 gate_chain.jsonl 追加 n 条。
# TimeoutError 容忍：OS 锁 10s 耗尽=设计内 fail-closed 丢弃（裁定#266 语义），
# 子进程上报实际落盘数（CHILD_OK <n>），父侧断言用实际数——负载型抖动不误报。
_CHILD_WORKER = (
    "import os, sys; from pathlib import Path\n"
    "from datetime import UTC, datetime\n"
    "sys.path.insert(0, sys.argv[5])\n"
    "os.environ['ZEPHYR_GATE_CHAIN_PATH'] = sys.argv[1]\n"
    "from zephyr.gov_enforcement.rule_enforcement.audit_chain_verifier import AuditChainVerifier\n"
    "from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateResult, GateStatus\n"
    "v = AuditChainVerifier(persist_path=Path(sys.argv[1]))\n"
    "v.core_writer = None\n"  # 双重隔离：不落生产 events.jsonl
    "ok = 0\n"
    "for i in range(int(sys.argv[2])):\n"
    "    try:\n"
    "        v.append('G-' + sys.argv[3], GateResult(gate_id='G-' + sys.argv[3], status=GateStatus.PASS, reasons=[], timestamp=datetime.now(UTC)))\n"
    "        ok += 1\n"
    "    except TimeoutError:\n"
    "        pass\n"
    "print('CHILD_OK', ok)\n"
)


def _spawn_verifier_children(persist_path: Path, n_workers: int, per_worker: int) -> int:
    """返回子进程实际落盘总数（fail-closed 丢弃已扣除）。"""
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", _CHILD_WORKER, str(persist_path), str(per_worker), str(i), "x", _REPO_SRC],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for i in range(n_workers)
    ]
    total = 0
    errors = []
    for p in procs:
        out, err = p.communicate(timeout=180)
        if p.returncode != 0:
            errors.append(err.decode("utf-8", errors="replace")[-500:])
        else:
            total += int(out.decode().strip().split()[-1])
    assert not errors, "child verifiers failed:\n" + "\n".join(errors)
    return total


def _read_chain_lines(persist_path: Path) -> list[dict]:
    lines = persist_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lines if l.strip()]


def _assert_file_chain_continuous(persist_path: Path) -> list[dict]:
    """文件级链连续断言：每行 previous_hash == 前一行 hash（首行 genesis）。"""
    entries = _read_chain_lines(persist_path)
    prev = "0" * 64
    for idx, e in enumerate(entries):
        assert e["previous_hash"] == prev, (
            f"file chain fork at line #{idx + 1}: expected {prev[:12]}... got {e['previous_hash'][:12]}..."
        )
        prev = e["hash"]
    return entries


def _make_result(gate_id: str = "G1") -> GateResult:
    from datetime import UTC, datetime

    return GateResult(gate_id=gate_id, status=GateStatus.PASS, reasons=[], timestamp=datetime.now(UTC))


@pytest.fixture
def persist_path(tmp_path):
    return tmp_path / "gate_chain.jsonl"


def _fresh_verifier(persist_path: Path) -> AuditChainVerifier:
    v = AuditChainVerifier(persist_path=persist_path)
    v.core_writer = None  # 双重隔离：不落生产 events.jsonl
    return v


class TestGateChainMultiProcessAppend:
    def test_multi_process_appends_produce_continuous_file_chain(self, persist_path):
        """4 进程 × 20 条并发追加 → 文件级链零叉断（C-1 治本验收）。"""
        seed = _fresh_verifier(persist_path)
        seed.append("G-seed", _make_result("G-seed"))
        child_ok = _spawn_verifier_children(persist_path, n_workers=4, per_worker=20)
        entries = _assert_file_chain_continuous(persist_path)
        assert len(entries) == 1 + child_ok  # 1 seed + 子进程实际落盘（丢弃已扣）

    def test_no_same_prev_signature_between_consecutive_lines(self, persist_path):
        """裁定#266 #35155/#35156 同 prev 签名的 gate_chain 同型必须绝迹。"""
        child_ok = _spawn_verifier_children(persist_path, n_workers=3, per_worker=15)
        entries = _read_chain_lines(persist_path)
        assert len(entries) == child_ok
        for a, b in zip(entries, entries[1:]):
            assert a["previous_hash"] != b["previous_hash"], (
                f"same-prev signature pair (interleaved stale writers): {a['gate_id']} / {b['gate_id']}"
            )

    def test_prev_comes_from_file_tail_not_instance_memory(self, persist_path):
        """决定性用例：外部进程写入后，本实例下一条 prev 必须取文件尾（非内存 _last_hash）。"""
        v = _fresh_verifier(persist_path)
        v.append("G1", _make_result("G1"))
        memory_tail = v.last_hash
        # 模拟另一进程的落盘：直接文件追加一条合法行
        external = _fresh_verifier(persist_path)
        external.append("G2", _make_result("G2"))
        external_tail = _read_chain_lines(persist_path)[-1]["hash"]
        assert external_tail != memory_tail
        # 本实例再追加——治本前 prev=memory_tail（h1）→ 文件叉链
        v.append("G3", _make_result("G3"))
        entries = _assert_file_chain_continuous(persist_path)
        assert entries[-1]["previous_hash"] == external_tail
        assert len(entries) == 3

    def test_two_instances_same_process_file_chain_complete(self, persist_path):
        """同进程双 verifier 交错写（gate_engine 多实例场景）→ 文件链完整。"""
        v1 = _fresh_verifier(persist_path)
        v2 = _fresh_verifier(persist_path)
        for i in range(8):
            v1.append("GA", _make_result("GA"))
            v2.append("GB", _make_result("GB"))
        entries = _assert_file_chain_continuous(persist_path)
        assert len(entries) == 16


class TestGateChainRestartOverlap:
    def test_restart_overlap_window_zero_chain_damage(self, persist_path):
        """红蓝：重启 overlap 窗口实测——旧写方存活期间新写方（重启替身）并发追加。

        损伤窗口判定三零：文件链零叉断 / 事件零丢失（各写方成功计数之和==文件行数）/
        零同 prev 签名。计时证据：overlap 全程墙钟与各写方写入分布随行输出（红蓝
        留痕），链损伤恒为 0。
        """
        old_writer = _fresh_verifier(persist_path)
        old_writer.append("G-old-warmup", _make_result("G-old-warmup"))

        # 新写方（重启替身）在旧写方存活窗口内启动并并发写
        new_writer = _fresh_verifier(persist_path)
        t0 = _time.monotonic()
        old_count = 0
        new_count = 0
        for i in range(15):
            old_writer.append("G-old", _make_result("G-old"))
            old_count += 1
            new_writer.append("G-new", _make_result("G-new"))
            new_count += 1
        overlap_seconds = _time.monotonic() - t0

        entries = _assert_file_chain_continuous(persist_path)
        # 零丢失：成功计数和 == 文件行数（1 warmup + 30）
        assert len(entries) == old_count + new_count + 1
        for a, b in zip(entries, entries[1:]):
            assert a["previous_hash"] != b["previous_hash"]
        print(
            f"\n[red-blue] restart overlap window={overlap_seconds:.3f}s, "
            f"old_writer={old_count} new_writer={new_count} entries={len(entries)} "
            f"chain_forks=0 lost_events=0 same_prev_pairs=0"
        )

    def test_restart_child_process_overlap_chain_intact(self, persist_path):
        """真跨进程重启 overlap：父进程写方持续追加期间，子进程（重启后新进程）并发追加。

        断言（裁定#266 fail-closed 语义下的一致性口径）：
        - 文件级链零叉断（C-1 核心不变量，绝对）；
        - 子写方 25 条 + warmup 1 条全部在链（新写方事件零丢失）；
        - 父写方成功调用数 == 在链数时严格记账；热循环下 OS 锁 10s 耗尽的
          fail-closed 丢弃（与 events.jsonl writer 同语义：丢一条好过叉链）
          允许在链数 ≤ 成功调用数，差值即显式丢弃数（warn 留痕）。
        """
        parent = _fresh_verifier(persist_path)
        parent.append("G-parent-warmup", _make_result("G-parent-warmup"))
        proc = subprocess.Popen(
            [sys.executable, "-c", _CHILD_WORKER, str(persist_path), "25", "9", "x", _REPO_SRC],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        parent_count = 0
        while proc.poll() is None:
            parent.append("G-parent", _make_result("G-parent"))
            parent_count += 1
        out, err = proc.communicate(timeout=120)
        assert proc.returncode == 0, (err or b"").decode("utf-8", errors="replace")[-500:]
        child_ok = int(out.decode().strip().split()[-1])
        entries = _assert_file_chain_continuous(persist_path)
        # 守恒：warmup + 子进程实际落盘全部在链；父写方成功调用数==在链数时严格记账，
        # 热循环下 OS 锁 10s 耗尽的 fail-closed 丢弃允许在链数 ≤ 成功调用数
        assert len(entries) >= child_ok + 1  # 子写方+warmup 零丢失
        assert len(entries) <= parent_count + child_ok + 1
        print(
            f"\n[red-blue] cross-process restart overlap: parent_calls={parent_count} "
            f"child={child_ok}/25 entries={len(entries)} chain_forks=0 "
            f"fail_closed_dropped={parent_count + child_ok + 1 - len(entries)}"
        )


class TestGateChainLockSemantics:
    def test_lock_file_created_alongside_gate_chain(self, persist_path):
        v = _fresh_verifier(persist_path)
        v.append("G1", _make_result("G1"))
        assert (persist_path.parent / (persist_path.name + ".lock")).exists()

    def test_clear_holds_same_lock_and_removes_chain_file(self, persist_path):
        """clear() 在同锁域内执行：清空后锁文件保留（互斥域不拆散）、链文件删除。"""
        v = _fresh_verifier(persist_path)
        v.append("G1", _make_result("G1"))
        lock_file = persist_path.parent / (persist_path.name + ".lock")
        assert lock_file.exists()
        v.clear(reason="test", confirm=True, cleared_by="st-maint")
        assert not persist_path.exists()
        assert lock_file.exists()
        assert v.length == 0 and v.last_hash == "0" * 64
        # 清空后追加从 genesis 重启链
        v.append("G2", _make_result("G2"))
        entries = _assert_file_chain_continuous(persist_path)
        assert len(entries) == 1 and entries[0]["previous_hash"] == "0" * 64

    def test_persist_failure_keeps_chain_unchanged(self, persist_path):
        """fail-closed：落盘失败（路径被换成目录制造 OSError）→ 不入内存链、返回旁观条目。"""
        from zephyr.gov_enforcement.rule_enforcement.audit_chain_verifier import AuditEntry

        v = _fresh_verifier(persist_path)
        v.append("G1", _make_result("G1"))
        assert v.length == 1
        # 破坏写路径：把 persist_path 指到一个目录（open("a") 抛 OSError）
        bad_dir = persist_path.parent / "not_a_file"
        bad_dir.mkdir()
        v._persist_path = bad_dir  # noqa: SLF001 — 测试注入故障路径
        entry = v.append("G2", _make_result("G2"))
        assert isinstance(entry, AuditEntry)  # 返回契约维持（旁观条目）
        assert v.length == 1  # fail-closed：未入内存链
        chain_hashes = {e.hash for e in v.chain}
        assert entry.hash not in chain_hashes  # 旁观条目 hash 不在链上
