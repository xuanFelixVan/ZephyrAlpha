# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §池化死信封印（四出口接 cq._seal_dead_letter 唯一真源）
# [MODULE] tests.governance.test_pool_dead_letter_seal
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_pool_dead_letter_seal.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp 队列根，绝不碰生产 .runtime/commit_queue——P0-C 测试隔离令）；直调 _pool_process_item/_pool_env_failure_exit（即池工真实执行路径，绕开 lease/心跳线程换取确定性）；死信袋断言面=封印五件套（owner_session/dead_signature/dead_letter_family/prescription/first_dead_at）+ dead/_recurrence_state.json 复发计数 + stats.successors_rebuilt 对账
# [MODIFY-GUARD] 2026-10-03 死信挖矿治本红蓝验收：①四池化死信出口（ghost/attempts/通用/env 耗尽）产出后袋 JSON 必带封印字段 ②同签名 3 封熔断出根因工序单 ③封印失败 best-effort 降级不炸死信主链 ④同 qid 重复封印不炸（归属字段稳定）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_pool_dead_letter_seal.py — 池化（k=4）死信出口封印红蓝验收。

病根（2026-10-03 挖矿实锤）：串行通道全部死信出口都调 _seal_dead_letter（归属
五件套+复发熔断+根因工序单+后继重建），但池化 4 个死信出口只手写
prescription/owner_session——生产主通道产生的死信无 dead_signature、不进
_recurrence_state.json、无根因工序单、无后继重建（全库 1235 死袋仅 139 封印）。

本文件直调 _pool_process_item / _pool_env_failure_exit（池工线程的真实执行体），
用 tmp 迷你队列逐出口验证封印落地；红证=封印失败注入后死信主链仍不炸（治理
附加面 best-effort 哲学）。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql

# ---------------------------------------------------------------------------
# 迷你队列基建（直调池工真实执行路径，绕开 lease/心跳线程换取确定性）
# ---------------------------------------------------------------------------


def _make_item(qid: str, sid: str, paths: tuple[str, ...] = ("docs/x.md",)) -> dict:
    """手造迷你袋：死信出口只消费 files[].path / qid / session_id / meta，
    blob_ref 无需真实存在（死信路径不做 blob IO）。"""
    return {
        "qid": qid,
        "session_id": sid,
        "message": "test",
        "files": [
            {"path": p, "action": "modify", "blob_ref": f"blobs/{qid}-{i}", "blob_sha256": "0" * 64}
            for i, p in enumerate(paths)
        ],
        "base_head": "0" * 40,
        "created_at": "2026-10-03T00:00:00+00:00",
        "meta": {},
    }


def _stage(qroot: Path, item: dict) -> Path:
    """模拟池工认领：袋直接落 processing/（真实流程=pending→processing 原子 rename）。"""
    cq._ensure_dirs(qroot)
    p = qroot / "processing" / f"{item['qid']}.json"
    cq._atomic_write(p, json.dumps(item, ensure_ascii=False).encode("utf-8"))
    return p


class _BoomLanding:
    """桩落地器：__call__ 抛非瞬态异常 → 通用死信出口（出口③）。

    repo_root 指 tmp 根——_emit_landing_phase_stat 的审计写盘随 tmp 走（P0-C）。
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _item_paths(self, item: dict) -> list[str]:
        return []

    def __call__(self, item: dict, root: Path):
        # 消息刻意不含任何瞬态特征串（WinError/index.lock 等）——确保走通用
        # 死信分支而非 _is_transient_env_failure 截收。
        raise RuntimeError("TestBoom 确定性物品失败")


def _run_one(landing, qroot: Path, processing_path: Path) -> tuple[dict, dict]:
    """单件过池工真实执行体 _pool_process_item（worker 线程内调用的就是它）。"""
    stats = {
        "dead": 0,
        "done": 0,
        "processed_qids": [],
        "landed_index": [],
        "cascade_marked": 0,
        "stale_cleared": 0,
        "successors_rebuilt": 0,
    }
    lock = threading.Lock()
    shared = {"processed": 0, "env_aborted": False, "budget_left": None, "claimed": set()}
    cql._pool_process_item(landing, qroot, processing_path, stats, lock, shared)
    return stats, shared


def _read_dead(qroot: Path, qid: str) -> dict:
    return json.loads((qroot / "dead" / f"{qid}.json").read_text(encoding="utf-8"))


def _read_recurrence(qroot: Path) -> dict:
    return json.loads((qroot / "dead" / "_recurrence_state.json").read_text(encoding="utf-8"))


def _assert_sealed(bag: dict, sid: str) -> str:
    """封印五件套统一断言（与串行出口产出的袋字段口径全等）。"""
    assert bag["owner_session"] == sid
    assert bag["dead_signature"]  # 签名非空（族:头部特征）
    assert bag["dead_letter_family"]
    assert bag["prescription"]
    assert bag["first_dead_at"]
    return bag["dead_signature"]


# ---------------------------------------------------------------------------
# 蓝证①：通用 landing 失败死信出口（出口③）封印 + 复发计数 + 后继重建
# ---------------------------------------------------------------------------


class TestGenericDeadExitSeal:
    def test_generic_dead_exit_seals_bag_and_bumps_recurrence(self, tmp_path: Path):
        qroot = tmp_path / "commit_queue"
        item = _make_item("q-20261003-sess-a-0001", "sess-a")
        p = _stage(qroot, item)

        stats, shared = _run_one(_BoomLanding(tmp_path), qroot, p)

        assert stats["dead"] == 1
        assert stats["processed_qids"] == [item["qid"]]
        bag = _read_dead(qroot, item["qid"])
        signature = _assert_sealed(bag, "sess-a")
        assert bag["recurrence_count"] == 1
        # 死信已进同签名复发表（此前池化死信不封印 ⇒ 此文件恒缺席）
        entry = _read_recurrence(qroot)["signatures"][signature]
        assert entry["count"] == 1
        assert entry["owner_sessions"] == ["sess-a"]

    def test_successor_rebuild_marks_pending_sharer(self, tmp_path: Path):
        # 死者与其后同路径 pending 袋：封印的后继重建面（矿③ 影子标记可观测）
        qroot = tmp_path / "commit_queue"
        dead_item = _make_item("q-20261003-sess-a-0001", "sess-a", paths=("docs/shared.md",))
        succ_item = _make_item("q-20261003-sess-a-0002", "sess-a", paths=("docs/shared.md",))
        p = _stage(qroot, dead_item)
        cq._ensure_dirs(qroot)
        cq._atomic_write(
            qroot / "pending" / f"{succ_item['qid']}.json",
            json.dumps(succ_item, ensure_ascii=False).encode("utf-8"),
        )

        stats, _shared = _run_one(_BoomLanding(tmp_path), qroot, p)

        assert stats["dead"] == 1
        assert stats["successors_rebuilt"] == 1  # 后继重建扇出对账可见（此前池化恒 0）
        shadow = cq._read_stale_shadow(qroot, succ_item["qid"])
        assert shadow is not None and shadow["stale_by"] == dead_item["qid"]

    def test_recurrence_fuse_after_three_same_signature(self, tmp_path: Path):
        # 同签名第 3 封熔断：recurrence_fused + 根因工序单落 dead/_root_cause/
        qroot = tmp_path / "commit_queue"
        for seq in (1, 2, 3):
            item = _make_item(f"q-20261003-sess-a-{seq:04d}", "sess-a")
            p = _stage(qroot, item)
            stats, _ = _run_one(_BoomLanding(tmp_path), qroot, p)
            assert stats["dead"] == 1

        bag3 = _read_dead(qroot, "q-20261003-sess-a-0003")
        assert bag3["recurrence_fused"] is True
        ticket = qroot / bag3["root_cause_ticket"]
        assert ticket.is_file()
        ticket_json = json.loads(ticket.read_text(encoding="utf-8"))
        assert ticket_json["root_cause_required"] is True
        assert ticket_json["signature"] == bag3["dead_signature"]


# ---------------------------------------------------------------------------
# 蓝证②：ghost 幽灵出口（出口①）封印
# ---------------------------------------------------------------------------


class TestGhostDeadExitSeal:
    def test_ghost_exit_seals_bag(self, tmp_path: Path):
        qroot = tmp_path / "commit_queue"
        item = _make_item("q-20261003-sess-dead-0001", "sess-dead")
        p = _stage(qroot, item)
        # 判定真源：runtime_root/sessions/<sid>/heartbeat.jsonl 末行 status=exited
        hb = tmp_path / "sessions" / "sess-dead" / "heartbeat.jsonl"
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text(json.dumps({"status": "exited"}) + "\n", encoding="utf-8")

        stats, _shared = _run_one(_BoomLanding(tmp_path), qroot, p)

        assert stats["dead"] == 1
        bag = _read_dead(qroot, item["qid"])
        signature = _assert_sealed(bag, "sess-dead")
        assert bag["meta"]["ghost"] is True
        entry = _read_recurrence(qroot)["signatures"][signature]
        assert entry["count"] == 1


# ---------------------------------------------------------------------------
# 蓝证③：attempts 耗尽出口（出口②）封印
# ---------------------------------------------------------------------------


class TestAttemptsDeadExitSeal:
    def test_attempts_exhausted_exit_seals_bag(self, tmp_path: Path, monkeypatch):
        monkeypatch.delenv(cq._ATTEMPTS_BACKOFF_ENV, raising=False)  # 开关缺省 ON，防环境残留干扰
        qroot = tmp_path / "commit_queue"
        item = _make_item("q-20261003-sess-poison-0001", "sess-poison")
        item["attempts"] = cq._ATTEMPTS_DEAD_THRESHOLD  # 毒药件拾取即死信
        item["last_failure"] = "env: 测试末次失败"
        p = _stage(qroot, item)

        stats, _shared = _run_one(_BoomLanding(tmp_path), qroot, p)

        assert stats["dead"] == 1
        bag = _read_dead(qroot, item["qid"])
        signature = _assert_sealed(bag, "sess-poison")
        assert bag["dead_reason"].startswith("attempts_exhausted")
        entry = _read_recurrence(qroot)["signatures"][signature]
        assert entry["count"] == 1


# ---------------------------------------------------------------------------
# 蓝证④：env 重试耗尽升级死信出口（出口④，_pool_env_failure_exit）封印
# ---------------------------------------------------------------------------


class TestEnvRetryExhaustedSeal:
    def test_env_retry_exhausted_upgrades_to_sealed_dead(self, tmp_path: Path):
        qroot = tmp_path / "commit_queue"
        item = _make_item("q-20261003-sess-envy-0001", "sess-envy")
        item["meta"]["env_retry"] = cql._RETRY_META_MAX - 1  # 再撞一次即耗尽
        p = _stage(qroot, item)
        ledger = cql._PoolLedger(
            {"dead": 0, "done": 0, "processed_qids": [], "successors_rebuilt": 0},
            threading.Lock(),
            {"processed": 0},
        )

        cql._pool_env_failure_exit(qroot, p, item, item["qid"], cq.LandingEnvironmentError("TestEnvBoom"), ledger)

        assert ledger.stats["dead"] == 1
        bag = _read_dead(qroot, item["qid"])
        signature = _assert_sealed(bag, "sess-envy")
        assert "env_retry" in bag["dead_reason"]
        entry = _read_recurrence(qroot)["signatures"][signature]
        assert entry["count"] == 1


# ---------------------------------------------------------------------------
# 红证⑤：封印失败 best-effort——死信主链不炸，归属五件套降级注入仍在
# ---------------------------------------------------------------------------


class TestSealFailureSafety:
    def test_seal_failure_does_not_break_dead_letter_path(self, tmp_path: Path, monkeypatch, caplog):
        qroot = tmp_path / "commit_queue"
        item = _make_item("q-20261003-sess-a-0001", "sess-a")
        p = _stage(qroot, item)

        def _boom(root, item):
            raise OSError("封印设施故障注入")

        monkeypatch.setattr(cq, "_seal_dead_letter", _boom)
        with caplog.at_level("WARNING"):
            stats, _shared = _run_one(_BoomLanding(tmp_path), qroot, p)

        # 死信主链完好：袋照落 dead/、stats 照记（封印只是治理附加面）
        assert stats["dead"] == 1
        bag = _read_dead(qroot, item["qid"])
        # 降级注入：归属五件套仍在（纯内存 attribution，无 IO 不会失败在盘上）
        _assert_sealed(bag, "sess-a")
        assert any("死信封印失败" in r.message for r in caplog.records)

    def test_double_seal_same_item_does_not_crash(self, tmp_path: Path):
        # 同 qid 重复封印不炸（任务约束）：归属字段稳定（setdefault 幂等），
        # 复发计数按「每死一计」累加——与串行通道语义全等（同波双出口由认领
        # rename+claimed 集互斥防住，此用例锁定的只是「不炸+字段稳定」下限）。
        qroot = tmp_path / "commit_queue"
        cq._ensure_dirs(qroot)
        item = _make_item("q-20261003-sess-a-0001", "sess-a")
        item["dead_at"] = "2026-10-03T00:00:00+00:00"
        item["dead_reason"] = "landing 异常: RuntimeError: TestBoom 确定性物品失败"

        cql._pool_seal_dead_letter(qroot, item)
        sig_first = item["dead_signature"]
        cql._pool_seal_dead_letter(qroot, item)  # 二次封印：不炸

        assert item["dead_signature"] == sig_first
        assert item["owner_session"] == "sess-a"
        assert item["recurrence_count"] == 2  # 每死一计（与串行 _seal_dead_letter 全等）


# ---------------------------------------------------------------------------
# 蓝证⑥：drain_queue_pool stats 对账面——successors_rebuilt 键与串行口径同形
# ---------------------------------------------------------------------------


class TestPoolStatsShape:
    def test_pool_stats_has_successors_rebuilt_key(self, tmp_path: Path, monkeypatch):
        # 真跑一次空队列 k=2 池化排空（工构桩化——空队列不触 landing，桩只挡
        # worktree 备置开销），锁 stats 原生键形状：successors_rebuilt 与串行
        # cq.drain_queue 的 stats 同键（此前池化死信不封印 ⇒ 对账面缺列）。
        qroot = tmp_path / "q"
        cq._ensure_dirs(qroot)
        monkeypatch.setattr(cql, "make_worker_landing", lambda *a, **kw: None)
        stats = cql.drain_queue_pool(queue_root=qroot, repo_root=tmp_path, workers=2)
        assert stats["dead"] == 0
        assert "successors_rebuilt" in stats
        assert stats["successors_rebuilt"] == 0
