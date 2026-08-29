# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S1.2
# [MODULE] tests.autonomy.test_agent_ticket_queue
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pytest ; zephyr.autonomy_core.agents.ticket_queue
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部落盘断言只认 tmp runtime_dir（不污染仓根 .runtime）；多会话认领冲突用线程真实竞争验证
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4-S1.2 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无（测试件）
# [TESTS] 自测
# [A_test] module_id=MOD-EXE-AGENTS | layer=test | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""S1.2 工单队列落盘化测试（14号文 §4-S1.2 验收口径）.

被测对象：src/zephyr/autonomy_core/agents/ticket_queue.py（.runtime/agent_runs/_queue/
四态 pending/claimed/done/dead 落盘队列；61号文 §3.6 三件套=design_memo 引用+
depgraph path+占用者字段；O_EXCL 原子认领防多会话抢单；claimed 断点恢复/重派）。

覆盖：入队信封（schema_version/human_gated/三件套）→ 认领原子性（含线程并发）
→ done/dead 四态流转 → recover 断点重派（孤儿会话/陈旧认领）→ CLI 四子命令。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from zephyr.autonomy_core.agents import ticket_queue
from zephyr.autonomy_core.agents.ticket_queue import TicketQueue

DESIGN_MEMO = "docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/20_first_batch_strategies.md"
DEPGRAPH_PATH = "src/zephyr/pf_core/strategies/"


def _ticket(ticket_id: str = "tq-001", role: str = "business") -> dict:
    return {
        "ticket_id": ticket_id,
        "role": role,
        "kind": "g04_strategy_ops_check",
        "payload": {"ticket_id": ticket_id, "kind": "g04_strategy_ops_check"},
        "design_memo": DESIGN_MEMO,
        "depgraph_path": DEPGRAPH_PATH,
        "note": "S1.2 测试工单",
    }


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestEnqueue:
    """入队：pending 落盘 + 信封纪律 + 三件套字段 + 非法拒收."""

    def test_enqueue_lands_pending_with_envelope_and_handover_trio(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        path = queue.enqueue(_ticket())
        assert path == tmp_path / "agent_runs" / "_queue" / "pending" / "tq-001.json"
        landed = _read(path)
        assert landed["schema_version"] == ticket_queue.SCHEMA_VERSION
        assert landed["ai_autonomy"] == "human_gated"
        assert landed["state"] == "pending"
        assert landed["role"] == "business"
        assert landed["kind"] == "g04_strategy_ops_check"
        # 61号文 §3.6 三件套：design_memo 引用 + depgraph path + 占用者
        assert landed["design_memo"] == DESIGN_MEMO
        assert landed["depgraph_path"] == DEPGRAPH_PATH
        assert landed["owner"] == ""
        assert landed["payload"]["kind"] == "g04_strategy_ops_check"
        assert landed["attempts"] == 0
        assert landed["claimed_at"] is None

    def test_enqueue_payload_defaults_to_non_envelope_fields(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        ticket = {"ticket_id": "tq-raw", "role": "algorithm", "kind": "experiment",
                  "experiment_type": "model_evaluation", "run_id": "r-1"}
        queue.enqueue(ticket)
        landed = _read(tmp_path / "agent_runs" / "_queue" / "pending" / "tq-raw.json")
        assert landed["payload"] == {"experiment_type": "model_evaluation", "run_id": "r-1"}
        assert landed["design_memo"] == "" and landed["depgraph_path"] == ""

    def test_enqueue_rejects_duplicate_across_states(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket())
        with pytest.raises(ValueError, match="已存在"):
            queue.enqueue(_ticket())
        claimed = queue.claim("sess-a")
        assert claimed is not None
        with pytest.raises(ValueError, match="已存在"):
            queue.enqueue(_ticket())  # claimed 态同 id 也拒

    def test_enqueue_rejects_invalid_ticket_id(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        for bad in ("", "../escape", "a/b", "a\\b", "x" * 129):
            with pytest.raises(ValueError, match="ticket_id"):
                queue.enqueue(_ticket(ticket_id=bad) if bad else {**_ticket(), "ticket_id": ""})

    def test_enqueue_requires_role_and_kind(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        with pytest.raises(ValueError, match="role|kind"):
            queue.enqueue({"ticket_id": "tq-x"})


class TestClaim:
    """认领：O_EXCL 原子性 + 占用者落盘 + 多会话/多线程防抢."""

    def test_claim_moves_pending_to_claimed_and_sets_owner(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-a"))
        queue.enqueue(_ticket("tq-b"))
        claimed = queue.claim("sess-1")
        assert claimed is not None and claimed["ticket_id"] == "tq-a"  # 先入先出
        assert claimed["owner"] == "sess-1"
        assert claimed["state"] == "claimed"
        assert claimed["claimed_at"]
        base = tmp_path / "agent_runs" / "_queue"
        assert not (base / "pending" / "tq-a.json").exists()
        assert _read(base / "claimed" / "tq-a.json")["owner"] == "sess-1"
        assert (base / "pending" / "tq-b.json").exists()

    def test_claim_filters_by_role_and_empty_queue_returns_none(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-biz", role="business"))
        assert queue.claim("sess-1", role="algorithm") is None
        claimed = queue.claim("sess-1", role="business")
        assert claimed is not None and claimed["ticket_id"] == "tq-biz"
        assert queue.claim("sess-2") is None

    def test_claim_conflict_second_session_gets_nothing(self, tmp_path):
        """多会话抢同一单：O_EXCL 保证只有先到先得者成功，后者不双领."""
        queue_a = TicketQueue(runtime_dir=tmp_path)  # 会话 A 视角
        queue_b = TicketQueue(runtime_dir=tmp_path)  # 会话 B 视角（同队列目录）
        queue_a.enqueue(_ticket("tq-race"))
        assert queue_a.claim("sess-a", ticket_id="tq-race") is not None
        assert queue_b.claim("sess-b", ticket_id="tq-race") is None  # 已被 A 领走
        landed = _read(tmp_path / "agent_runs" / "_queue" / "claimed" / "tq-race.json")
        assert landed["owner"] == "sess-a"  # 占用者不被覆盖

    def test_claim_concurrent_threads_single_winner(self, tmp_path):
        """真实线程竞争：4 会话同时抢 1 单，恰好 1 个赢家（O_EXCL 原子认领）."""
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-thread"))
        barrier = threading.Barrier(4)
        results: list[dict | None] = []
        errors: list[Exception] = []

        def worker(session: str) -> None:
            try:
                barrier.wait(timeout=10)
                results.append(queue.claim(session))
            except Exception as exc:  # noqa: BLE001 — 测试收集线程异常主线程断言
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(f"sess-{i}",)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=20)
        assert not errors
        winners = [r for r in results if r is not None]
        assert len(winners) == 1
        assert len(list((tmp_path / "agent_runs" / "_queue" / "claimed").glob("*.json"))) == 1


class TestDoneDead:
    """done/dead 流转：占用者校验 + 未认领拒完结."""

    def test_done_requires_claim_owner_session(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket())
        queue.claim("sess-owner")
        with pytest.raises(PermissionError, match="owner"):
            queue.done("tq-001", "sess-intruder")
        path = queue.done("tq-001", "sess-owner", status="completed",
                          summary={"run_dir": ".runtime/agent_runs/business/x"})
        landed = _read(path)
        assert landed["state"] == "done"
        assert landed["result_status"] == "completed"
        assert landed["finished_at"]
        assert landed["summary"]["run_dir"].endswith("business/x")
        assert not (tmp_path / "agent_runs" / "_queue" / "claimed" / "tq-001.json").exists()

    def test_done_rejects_unclaimed_ticket(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket())
        with pytest.raises(ValueError, match="claimed"):
            queue.done("tq-001", "sess-a")

    def test_mark_dead_from_pending_and_claimed(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-p1"))
        dead_path = queue.mark_dead("tq-p1", reason="人工判死：工单口径作废")
        assert _read(dead_path)["state"] == "dead"
        assert _read(dead_path)["dead_reason"] == "人工判死：工单口径作废"
        queue.enqueue(_ticket("tq-c1"))
        queue.claim("sess-a", ticket_id="tq-c1")
        with pytest.raises(PermissionError, match="owner"):
            queue.mark_dead("tq-c1", reason="x", session_id="sess-b")
        queue.mark_dead("tq-c1", reason="执行失败", session_id="sess-a")
        assert _read(tmp_path / "agent_runs" / "_queue" / "dead" / "tq-c1.json")["state"] == "dead"

    def test_mark_dead_unknown_ticket_rejected(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        with pytest.raises(ValueError, match="不存在"):
            queue.mark_dead("tq-ghost", reason="x")


class TestRecover:
    """断点恢复：会话中断后 claimed 扫描重派（孤儿会话/陈旧认领两口径）."""

    def test_recover_requeues_orphaned_claimed_ticket(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-orphan"))
        queue.enqueue(_ticket("tq-alive"))
        queue.claim("dead-session", ticket_id="tq-orphan")
        queue.claim("live-session", ticket_id="tq-alive")
        requeued = queue.recover(alive_sessions={"live-session"})
        assert requeued == ["tq-orphan"]
        landed = _read(tmp_path / "agent_runs" / "_queue" / "pending" / "tq-orphan.json")
        assert landed["state"] == "pending"
        assert landed["owner"] == ""
        assert landed["claimed_at"] is None
        assert landed["attempts"] == 1  # 重派计数留痕
        assert _read(tmp_path / "agent_runs" / "_queue" / "claimed" / "tq-alive.json")["state"] == "claimed"
        assert queue.claim("sess-new") is not None  # 重派后可再被认领

    def test_recover_stale_claim_by_age(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket())
        queue.claim("sess-a")
        claimed_file = tmp_path / "agent_runs" / "_queue" / "claimed" / "tq-001.json"
        stale = _read(claimed_file)
        stale["claimed_at"] = "2020-01-01T00:00:00+00:00"  # 手工造陈旧认领
        claimed_file.write_text(json.dumps(stale, ensure_ascii=False), encoding="utf-8")
        assert queue.recover(stale_minutes=60) == ["tq-001"]
        assert queue.recover(stale_minutes=60) == []  # 已回 pending，无 claimed 可收

    def test_recover_requires_criterion(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        with pytest.raises(ValueError, match="alive_sessions|stale_minutes"):
            queue.recover()

    def test_recover_skips_done_and_dead(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-done"))
        queue.claim("sess-a", ticket_id="tq-done")
        queue.done("tq-done", "sess-a")
        assert queue.recover(alive_sessions=set()) == []


class TestListAndCli:
    """队列扫描 + CLI 四子命令端到端."""

    def test_list_aggregates_states_and_dedupes(self, tmp_path):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-1"))
        queue.enqueue(_ticket("tq-2"))
        queue.enqueue(_ticket("tq-3"))
        queue.claim("sess-a", ticket_id="tq-2")
        queue.claim("sess-a", ticket_id="tq-3")
        queue.done("tq-3", "sess-a")
        all_tickets = queue.list_tickets()
        by_id = {t["ticket_id"]: t["state"] for t in all_tickets}
        assert by_id == {"tq-1": "pending", "tq-2": "claimed", "tq-3": "done"}
        assert [t["ticket_id"] for t in queue.list_tickets(state="pending")] == ["tq-1"]
        assert [t["ticket_id"] for t in queue.list_tickets(state="claimed")] == ["tq-2"]
        assert [t["ticket_id"] for t in queue.list_tickets(state="done")] == ["tq-3"]
        assert queue.list_tickets(state="dead") == []

    def test_cli_enqueue_list_claim_done(self, tmp_path, capsys):
        ticket_file = tmp_path / "ticket.json"
        ticket_file.write_text(json.dumps(_ticket("tq-cli"), ensure_ascii=False),
                               encoding="utf-8")
        rt = str(tmp_path / "rt")
        assert ticket_queue.main(["enqueue", "--ticket", str(ticket_file),
                                  "--runtime-dir", rt]) == 0
        out = json.loads(capsys.readouterr().out)
        assert out["enqueued"] == "tq-cli" and out["state"] == "pending"

        assert ticket_queue.main(["list", "--runtime-dir", rt]) == 0
        listed = json.loads(capsys.readouterr().out)
        assert [t["ticket_id"] for t in listed] == ["tq-cli"]

        assert ticket_queue.main(["claim", "--session-id", "sess-cli",
                                  "--runtime-dir", rt]) == 0
        claimed = json.loads(capsys.readouterr().out)
        assert claimed["claimed"]["owner"] == "sess-cli"

        assert ticket_queue.main(["done", "--ticket-id", "tq-cli", "--session-id",
                                  "sess-cli", "--status", "completed",
                                  "--runtime-dir", rt]) == 0
        done = json.loads(capsys.readouterr().out)
        assert done["done"] == "tq-cli"
        final = _read(tmp_path / "rt" / "agent_runs" / "_queue" / "done" / "tq-cli.json")
        assert final["state"] == "done" and final["design_memo"] == DESIGN_MEMO

    def test_cli_recover(self, tmp_path, capsys):
        queue = TicketQueue(runtime_dir=tmp_path)
        queue.enqueue(_ticket("tq-cli-rec"))
        queue.claim("ghost-session")
        capsys.readouterr()
        assert ticket_queue.main(["recover", "--alive-sessions", "other-session",
                                  "--runtime-dir", str(tmp_path)]) == 0
        out = json.loads(capsys.readouterr().out)
        assert out["requeued"] == ["tq-cli-rec"]
