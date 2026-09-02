# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §AICOLLAB-001-TaskBoard
# [MODULE] tests.governance.test_task_board
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.task_board
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_task_board.py
# [MATURITY] production
# [INVARIANTS] 三态机 pending→claimed→completed；重复认领 DENIED(exit 2)；CAS 并发认领仅一人胜；completed 禁删禁认领
# [MODIFY-GUARD] scripts/task_board.py CLI 面与状态机语义；66 号 §2.4 #9 schema
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_task_board.py — task_board.py 重建验收（66 号 §2.4 #9 / 65 号 §11.2.3 / §732 验收行）。

验收真源（65 号 §732）："task_board.py create/claim/start/complete；AI-02 claim
已认领任务 → 状态机正确转换，重复认领 DENIED"。
"""

from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path

import pytest

import scripts.task_board as tb


@pytest.fixture()
def board(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db = tmp_path / "task_board.db"
    monkeypatch.setenv("ZEPHYR_TASK_BOARD_DB", str(db))
    yield db


def _create(title: str = "demo", metadata: str = "") -> str:
    argv = ["create", "--title", title]
    if metadata:
        argv += ["--metadata", metadata]
    argv += ["--session", "S1"]
    assert tb.main(argv) == 0
    # task_id 是 create 唯一 stdout——从 DB 取回最新行
    conn = sqlite3.connect(os.environ["ZEPHYR_TASK_BOARD_DB"])
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT task_id FROM tasks ORDER BY created_at DESC, rowid DESC LIMIT 1").fetchone()
    conn.close()
    return row["task_id"]


class TestStateMachine:
    def test_create_pending(self, board: Path) -> None:
        tid = _create()
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (tid,)).fetchone()
        conn.close()
        assert row["status"] == "pending"
        assert row["claimed_by"] is None

    def test_claim_success(self, board: Path) -> None:
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (tid,)).fetchone()
        conn.close()
        assert row["status"] == "claimed"
        assert row["claimed_by"] == "AI-01"
        assert row["claimed_at"] is not None

    def test_duplicate_claim_denied(self, board: Path) -> None:
        """65 号 §732 验收行：AI-02 claim 已认领任务 → DENIED。"""
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        assert tb.main(["claim", tid, "--session", "AI-02"]) == 2  # DENIED
        # 同会话 60min 内重复认领也 DENIED（严格语义）
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 2

    def test_claim_nonexistent_denied(self, board: Path) -> None:
        assert tb.main(["claim", "T-nonexistent", "--session", "AI-01"]) == 2

    def test_start_keeps_claimed_and_records_event(self, board: Path) -> None:
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        assert tb.main(["start", tid, "--session", "AI-01"]) == 0
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT status FROM tasks WHERE task_id=?", (tid,)).fetchone()
        ev = conn.execute("SELECT event_type FROM task_events WHERE task_id=? ORDER BY event_id", (tid,)).fetchall()
        conn.close()
        assert row["status"] == "claimed"
        assert [e["event_type"] for e in ev] == ["created", "claimed", "started"]

    def test_start_unclaimed_denied(self, board: Path) -> None:
        tid = _create()
        assert tb.main(["start", tid, "--session", "AI-01"]) == 2

    def test_complete_by_claimer(self, board: Path) -> None:
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        assert tb.main(["complete", tid, "--session", "AI-01", "--result", "done ok"]) == 0
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (tid,)).fetchone()
        conn.close()
        assert row["status"] == "completed"
        assert row["completed_at"] is not None

    def test_complete_by_non_claimer_denied(self, board: Path) -> None:
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        assert tb.main(["complete", tid, "--session", "AI-02"]) == 2

    def test_claim_completed_denied(self, board: Path) -> None:
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        assert tb.main(["complete", tid, "--session", "AI-01"]) == 0
        assert tb.main(["claim", tid, "--session", "AI-02"]) == 2

    def test_delete_rules(self, board: Path) -> None:
        # pending 任意可删
        t1 = _create("t1")
        assert tb.main(["delete", t1, "--session", "AI-09"]) == 0
        # claimed 仅认领者可删
        t2 = _create("t2")
        assert tb.main(["claim", t2, "--session", "AI-01"]) == 0
        assert tb.main(["delete", t2, "--session", "AI-02"]) == 2
        assert tb.main(["delete", t2, "--session", "AI-01"]) == 0
        # completed 禁删
        t3 = _create("t3")
        assert tb.main(["claim", t3, "--session", "AI-01"]) == 0
        assert tb.main(["complete", t3, "--session", "AI-01"]) == 0
        assert tb.main(["delete", t3, "--session", "AI-01"]) == 2


class TestClaimTTL:
    def test_stale_claim_stealable(self, board: Path) -> None:
        """claimed_at 超 60min → 他人可抢占（防崩溃会话永久占用）。"""
        tid = _create()
        assert tb.main(["claim", tid, "--session", "AI-01"]) == 0
        conn = sqlite3.connect(str(board))
        conn.execute(
            "UPDATE tasks SET claimed_at=datetime('now','-61 minutes') WHERE task_id=?",
            (tid,),
        )
        conn.commit()
        conn.close()
        assert tb.main(["claim", tid, "--session", "AI-02"]) == 0
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT claimed_by FROM tasks WHERE task_id=?", (tid,)).fetchone()
        conn.close()
        assert row["claimed_by"] == "AI-02"


class TestDeadLetterMetadata:
    def test_metadata_roundtrip(self, board: Path) -> None:
        """66 号 §6.4：死信标签（qid+原因+属主）写入 metadata_json 承载。"""
        meta = '{"type":"dead_letter","qid":"q-20260814-sess-x-0003","reason":"FOREIGN-CHANGE","owner":"sess-x"}'
        tid = _create("dead letter demo", metadata=meta)
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT metadata_json FROM tasks WHERE task_id=?", (tid,)).fetchone()
        conn.close()
        import json

        payload = json.loads(row["metadata_json"])
        assert payload["type"] == "dead_letter"
        assert payload["qid"] == "q-20260814-sess-x-0003"
        assert payload["owner"] == "sess-x"

    def test_bad_metadata_json_rejected(self, board: Path) -> None:
        assert tb.main(["create", "--title", "x", "--metadata", "{not json"]) == 1


class TestDeadLetterTagging:
    """66 号 P1 残余小项：死信任务自动打标签可查（deadletter 子命令 + list --label）。"""

    @staticmethod
    def _meta(board: Path, tid: str) -> dict:
        import json

        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT metadata_json FROM tasks WHERE task_id=?", (tid,)).fetchone()
        conn.close()
        return json.loads(row["metadata_json"])

    def test_tag_writes_metadata_and_event(self, board: Path) -> None:
        tid = _create()
        rc = tb.main(["deadletter", tid, "--session", "sess-x", "--qid", "q-0001", "--reason", "FOREIGN-CHANGE"])
        assert rc == 0
        tag = self._meta(board, tid)["deadletter"]
        assert tag["qid"] == "q-0001"
        assert tag["reason"] == "FOREIGN-CHANGE"
        assert tag["owner"] == "sess-x"  # 缺省 owner=--session
        assert tag["tagged_at"]
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        ev = conn.execute(
            "SELECT event_type, payload_json FROM task_events WHERE task_id=? AND event_type='deadlettered'",
            (tid,),
        ).fetchall()
        conn.close()
        assert len(ev) == 1
        import json

        assert json.loads(ev[0]["payload_json"])["qid"] == "q-0001"

    def test_tag_owner_override_and_metadata_merge(self, board: Path) -> None:
        tid = _create("keep-meta", metadata='{"type":"dead_letter","note":"原 metadata 保留"}')
        rc = tb.main(
            ["deadletter", tid, "--session", "sess-x", "--qid", "q-0002", "--reason", "GATE-FAIL", "--owner", "sess-y"]
        )
        assert rc == 0
        meta = self._meta(board, tid)
        assert meta["deadletter"]["owner"] == "sess-y"
        assert meta["note"] == "原 metadata 保留"  # 打标合并不覆盖既有键

    def test_tag_completed_denied(self, board: Path) -> None:
        tid = _create()
        tb.main(["claim", tid, "--session", "AI-01"])
        tb.main(["complete", tid, "--session", "AI-01"])
        assert tb.main(["deadletter", tid, "--session", "AI-01", "--qid", "q-1", "--reason", "r"]) == 2
        assert "deadletter" not in self._meta(board, tid)

    def test_tag_nonexistent_denied(self, board: Path) -> None:
        assert tb.main(["deadletter", "T-nonexistent", "--session", "AI-01", "--qid", "q-1", "--reason", "r"]) == 2

    def test_retag_latest_wins(self, board: Path) -> None:
        tid = _create()
        tb.main(["deadletter", tid, "--session", "AI-01", "--qid", "q-1", "--reason", "首次"])
        tb.main(["deadletter", tid, "--session", "AI-01", "--qid", "q-2", "--reason", "重入队后再失败"])
        tag = self._meta(board, tid)["deadletter"]
        assert tag["qid"] == "q-2"
        assert tag["reason"] == "重入队后再失败"
        conn = sqlite3.connect(str(board))
        n = conn.execute(
            "SELECT count(*) FROM task_events WHERE task_id=? AND event_type='deadlettered'", (tid,)
        ).fetchone()[0]
        conn.close()
        assert n == 2  # 两次打标均留事件痕

    def test_list_label_filter(self, board: Path, capsys: pytest.CaptureFixture) -> None:
        t_dead = _create("dead-task")
        t_ok = _create("ok-task")
        tb.main(["deadletter", t_dead, "--session", "AI-01", "--qid", "q-1", "--reason", "r"])
        capsys.readouterr()  # 清缓冲
        assert tb.main(["list", "--label", "deadletter"]) == 0
        out = capsys.readouterr().out
        assert t_dead in out
        assert t_ok not in out
        assert tb.main(["list"]) == 0
        out_all = capsys.readouterr().out
        assert t_dead in out_all and t_ok in out_all


class TestCASConcurrency:
    def test_concurrent_claim_exactly_one_winner(self, board: Path) -> None:
        """CAS 实证：8 线程同时认领同一任务，恰一人胜（SQLite 单写者串行）。"""
        tid = _create()
        results: list[int] = []
        lock = threading.Lock()

        def _claim(n: int) -> None:
            rc = tb.main(["claim", tid, "--session", f"AI-{n:02d}"])
            with lock:
                results.append(rc)

        threads = [threading.Thread(target=_claim, args=(n,)) for n in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        winners = [rc for rc in results if rc == 0]
        denied = [rc for rc in results if rc == 2]
        assert len(winners) == 1, f"CAS 失效：{len(winners)} 个胜者 {results}"
        assert len(denied) == 7


class TestInfra:
    def test_wal_mode(self, board: Path) -> None:
        _create()
        conn = sqlite3.connect(str(board))
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode.lower() == "wal"

    def test_warn_only(self, board: Path) -> None:
        assert tb.main(["--warn-only"]) == 0

    def test_events_history_complete(self, board: Path) -> None:
        tid = _create()
        tb.main(["claim", tid, "--session", "AI-01"])
        tb.main(["start", tid, "--session", "AI-01"])
        tb.main(["complete", tid, "--session", "AI-01", "--result", "ok"])
        conn = sqlite3.connect(str(board))
        conn.row_factory = sqlite3.Row
        ev = conn.execute(
            "SELECT event_type, actor FROM task_events WHERE task_id=? ORDER BY event_id",
            (tid,),
        ).fetchall()
        conn.close()
        assert [e["event_type"] for e in ev] == ["created", "claimed", "started", "completed"]
        assert all(e["actor"] for e in ev)
