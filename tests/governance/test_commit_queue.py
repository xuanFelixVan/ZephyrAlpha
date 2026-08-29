# [A_test] module_id: MOD-GOV-046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §
# [MODULE] tests.governance.test_commit_queue
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 隔离，不碰真实 .runtime/commit_queue 与 git；零丢失/零重复/FIFO/死信不卡队/同键仅留最新
# [MODIFY-GUARD] 66 号 §6 协议 + §10 MVP 验收口径 + §11 红队清单；08 号文 §4.2 步骤 1/2/4 验收行
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue.py — 提交队列 MVP A 段验收（66 号 §10 MVP 行 + §11 红队清单）。

断言清单真源（66 号 §11 + 08 号文 §4.2 验收列）：
1. §11 #3 红队：路径穿越/超大 blob/空 message/.git 路径全拦（+密钥路径/session_id 注入），
   报错非静默（QueueReject 消息含原因，CLI exit 2）。
2. §11 #1 v0.4.0：3 会话并发 enqueue 50 项不丢不重（qid 全唯一）；drain 后 50 项全 done；
   FIFO 序 == qid 单调序。
3. §11 #2 故障注入：drain 中途模拟崩溃（monkeypatch kill landing callable）→ 下次自举
   幂等续跑——processing 孤儿回收重入 pending，无双落（done 按 qid 唯一）无丢失。
4. §11 #7 compaction：同 session 连续 enqueue 同文件 3 次仅留最终态；含与 drain 并发
   竞态版——终态一致、内容序为单调子序列且终值正确。
5. 死信：landing 失败项进 dead/ 带原因，后续项不受影响（DLQ 不卡队，66 号 §4 裁定 4）。
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.task_board as tb


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    """队列根固定落 tmp_path（隔离真实 .runtime/commit_queue；不经环境变量防线程间竞态）。"""
    return tmp_path / "commit_queue"


def _enqueue(root: Path, session: str, msg: str, files: list[tuple[str, bytes]]) -> dict:
    return cq.enqueue_item(session, msg, files, queue_root=root)


def _blob_content(root: Path, item: dict, path: str) -> bytes:
    sha = next(f["blob_sha256"] for f in item["files"] if f["path"] == path)
    return (root / "blobs" / sha).read_bytes()


def _all_state_qids(root: Path) -> dict[str, str]:
    """收集四态目录 {qid: state}——零双落断言用（同 qid 出现两处即违规）。"""
    out: dict[str, str] = {}
    for state in ("pending", "processing", "done", "dead"):
        for f in sorted((root / state).glob("q-*.json")):
            qid = f.stem
            assert qid not in out, f"零双落不变量破裂: {qid} 同时存在于 {out[qid]} 与 {state}"
            out[qid] = state
    return out


# ---------------------------------------------------------------------------
# 66 号 §11 #3 红队：畸形入队项全拦，报错非静默
# ---------------------------------------------------------------------------


class TestEnqueueRedTeam:
    @pytest.mark.parametrize(
        "bad_path",
        [
            "../evil.txt",  # 上溯穿越
            "docs/../../evil.txt",  # 内嵌 ..
            "C:/Windows/system32.ini",  # 盘符绝对路径
            "/etc/passwd",  # POSIX 绝对路径
            "~/secret.txt",  # home 穿越
            "docs\\evil.txt",  # 反斜杠（Windows 路径注入）
            "docs//evil.txt",  # 空段
            "./evil.txt",  # 当前目录段
            ".git/config",  # .git 路径
            ".git",  # .git 本体
            "docs/.env",  # 密钥文件名
            "certs/server.pem",  # 密钥扩展名
            "home/id_rsa",  # 私钥文件名
        ],
    )
    def test_malformed_paths_rejected(self, queue_root: Path, bad_path: str) -> None:
        with pytest.raises(cq.QueueReject) as exc_info:
            _enqueue(queue_root, "AI-T1", "msg", [(bad_path, b"x")])
        assert str(exc_info.value).strip(), "报错非静默：拒绝原因 MUST 非空"

    def test_oversize_blob_rejected(self, queue_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # 阈值调小避免写 10MB 真实文件（阈值真源 66 号 §6.1：10MB，此处仅验拦截行为）
        monkeypatch.setattr(cq, "_MAX_BLOB_BYTES", 1024)
        with pytest.raises(cq.QueueReject, match="超大 blob"):
            _enqueue(queue_root, "AI-T1", "msg", [("big.bin", b"x" * 2048)])

    @pytest.mark.parametrize("bad_msg", ["", "   ", None])
    def test_empty_message_rejected(self, queue_root: Path, bad_msg) -> None:
        with pytest.raises(cq.QueueReject, match="空 message"):
            _enqueue(queue_root, "AI-T1", bad_msg, [("a.txt", b"x")])

    @pytest.mark.parametrize("bad_sid", ["", "a/b", "a\\b", "../escape", "has space", "x" * 65])
    def test_malformed_session_id_rejected(self, queue_root: Path, bad_sid: str) -> None:
        with pytest.raises(cq.QueueReject, match="session_id"):
            _enqueue(queue_root, bad_sid, "msg", [("a.txt", b"x")])

    def test_duplicate_path_in_one_item_rejected(self, queue_root: Path) -> None:
        with pytest.raises(cq.QueueReject, match="路径重复"):
            _enqueue(queue_root, "AI-T1", "msg", [("a.txt", b"1"), ("a.txt", b"2")])

    def test_empty_file_list_rejected(self, queue_root: Path) -> None:
        with pytest.raises(cq.QueueReject, match="空文件清单"):
            _enqueue(queue_root, "AI-T1", "msg", [])

    def test_cli_exit_2_and_stderr_non_silent(self, queue_root: Path, capsys: pytest.CaptureFixture) -> None:
        rc = cq.main(
            [
                "--queue-root",
                str(queue_root),
                "enqueue",
                "--session",
                "AI-T1",
                "--files",
                "../evil.txt",
                "--message",
                "x",
                "--worktree-root",
                str(queue_root),
            ]
        )
        assert rc == 2
        assert "DENIED" in capsys.readouterr().err, "CLI 报错非静默"


# ---------------------------------------------------------------------------
# 66 号 §11 #1 v0.4.0：3 会话并发 enqueue 50 项——不丢不重 + FIFO 序
# ---------------------------------------------------------------------------


class TestConcurrentEnqueue:
    def test_3_sessions_50_items_zero_loss_zero_dup_fifo(self, queue_root: Path) -> None:
        sessions = ["AI-A", "AI-B", "AI-C"]
        shards = [range(0, 17), range(17, 34), range(34, 50)]  # 共 50 项
        qids: list[str] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def worker(sid: str, indices: range) -> None:
            for i in indices:
                try:
                    # 每会话不同文件——本用例不触发 compaction（compaction 专项见下）
                    item = _enqueue(queue_root, sid, f"msg {sid} #{i}", [(f"docs/f{i:03d}.txt", f"content-{i}".encode())])
                    with lock:
                        qids.append(item["qid"])
                except BaseException as exc:  # noqa: BLE001 - 测试收集一切异常
                    with lock:
                        errors.append(exc)

        threads = [threading.Thread(target=worker, args=(sid, idx)) for sid, idx in zip(sessions, shards)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"并发 enqueue 出现异常: {errors}"
        # 零重复：50 个 qid 全唯一（66 号 §11 #1：50 个 enqueue 不丢不重，无 qid 碰撞）
        assert len(qids) == 50 and len(set(qids)) == 50
        # 零丢失：50 项全落 pending
        assert len(list((queue_root / "pending").glob("q-*.json"))) == 50

        # 排空（默认桩仅标记 done）
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 50 and stats["dead"] == 0
        # 零丢失收口：50 项全 done，无残留 pending/processing
        states = _all_state_qids(queue_root)
        assert set(states) == set(qids)
        assert all(s == "done" for s in states.values())
        # FIFO 序断言：处理序 == qid 单调序（字典序 == seq 数值序，66 号 §6.1 seq:04d 零填充）
        assert stats["processed_qids"] == sorted(qids)
        # 同会话 FIFO 子序：每会话内按 seq 升序
        for sid in sessions:
            own = [q for q in stats["processed_qids"] if f"-{sid}-" in q]
            assert own == sorted(own), f"{sid} 会话内 FIFO 破裂"
        # 快照入袋：逐项 blob 内容与入队一致（防内容丢失核心语义）
        for done_file in (queue_root / "done").glob("q-*.json"):
            item = json.loads(done_file.read_text(encoding="utf-8"))
            src_idx = int(item["files"][0]["path"].split("f")[1].split(".")[0])
            assert _blob_content(queue_root, item, item["files"][0]["path"]) == f"content-{src_idx}".encode()


# ---------------------------------------------------------------------------
# 66 号 §11 #2 故障注入：drain 中途崩溃 → 下次自举幂等续跑（无双落无丢失）
# ---------------------------------------------------------------------------


class _SimulatedCrash(BaseException):
    """模拟 drain 中途进程崩溃。

    继承 BaseException 而非 Exception——普通 Exception 语义是「单项处理失败→死信」，
    进程被杀（kill/断电）不会给 landing 抛 Exception 的机会；drain 对 BaseException
    不捕获向上传播，当前项留 processing/ 成孤儿，等下次自举回收（66 号 §8）。
    """


class TestCrashRecovery:
    def test_crash_mid_drain_then_idempotent_resume(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        qids = [
            _enqueue(queue_root, "AI-C1", f"m{i}", [(f"f{i}.txt", f"v{i}".encode())])["qid"] for i in range(5)
        ]
        landing_calls: list[str] = []

        def killer(item: dict, root: Path) -> cq.LandingResult:
            # monkeypatch kill landing callable：第 3 项处理中「进程崩溃」
            landing_calls.append(item["qid"])
            if len(landing_calls) == 3:
                raise _SimulatedCrash("simulated process kill at 3rd item")
            return cq.LandingResult(ok=True, landed_id=f"stub:{item['qid']}")

        monkeypatch.setattr(cq, "default_landing_stub", killer)
        with pytest.raises(_SimulatedCrash):
            cq.drain_queue(queue_root)

        # 崩溃现场：前 2 项已 done，第 3 项留 processing 成孤儿，后 2 项仍在 pending
        assert len(list((queue_root / "done").glob("q-*.json"))) == 2
        orphans = list((queue_root / "processing").glob("q-*.json"))
        assert len(orphans) == 1
        orphan_qid = orphans[0].stem
        assert orphan_qid == qids[2]
        assert len(list((queue_root / "pending").glob("q-*.json"))) == 2

        # 下次自举（恢复默认桩）：孤儿回收续跑，幂等完成全部 5 项
        monkeypatch.undo()
        stats = cq.drain_queue(queue_root)
        assert stats["recovered"] == 1, "processing 孤儿 MUST 回收重入 pending"
        assert stats["done"] == 3  # 孤儿 + 2 个 pending
        states = _all_state_qids(queue_root)
        assert set(states) == set(qids), "无丢失：全部入队项有终态"
        assert all(s == "done" for s in states.values())
        # 无双落：done 目录按 qid 唯一（_all_state_qids 已内置跨目录重复断言）；
        # 且崩溃前已 done 的 2 项不被重跑（landing 调用记录恰为前 3 项各一次）
        assert landing_calls == qids[:3]
        done_files = list((queue_root / "done").glob("q-*.json"))
        assert len(done_files) == 5 and len({f.stem for f in done_files}) == 5

    def test_orphan_with_existing_terminal_state_not_double_landed(self, queue_root: Path) -> None:
        """防御性分支：孤儿项已有 done 终态 → 回收时删除防双落（不重复 landing）。"""
        item = _enqueue(queue_root, "AI-C2", "m", [("a.txt", b"v")])
        # 手工构造：同一 qid 同时落 processing 与 done（模拟崩溃发生在 rename 之后的极端窗口）
        src = queue_root / "pending" / f"{item['qid']}.json"
        payload = src.read_text(encoding="utf-8")
        (queue_root / "processing").mkdir(parents=True, exist_ok=True)
        os.replace(src, queue_root / "processing" / src.name)
        (queue_root / "done").mkdir(parents=True, exist_ok=True)
        (queue_root / "done" / src.name).write_text(payload, encoding="utf-8")
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 0, "已有终态的孤儿不得重跑 landing（防双落）"
        assert not list((queue_root / "processing").glob("q-*.json")), "孤儿应被清理"
        assert len(list((queue_root / "done").glob("q-*.json"))) == 1


# ---------------------------------------------------------------------------
# 66 号 §11 #7 compaction：同键 (session_id, path) 仅留最终态 + 并发竞态安全
# ---------------------------------------------------------------------------


class TestCompaction:
    def test_same_key_3_enqueues_keep_only_latest(self, queue_root: Path) -> None:
        i1 = _enqueue(queue_root, "AI-K1", "m1", [("docs/hot.txt", b"v1")])
        i2 = _enqueue(queue_root, "AI-K1", "m2", [("docs/hot.txt", b"v2")])
        i3 = _enqueue(queue_root, "AI-K1", "m3", [("docs/hot.txt", b"v3")])

        pending = list((queue_root / "pending").glob("q-*.json"))
        assert [p.stem for p in pending] == [i3["qid"]], "同键 3 连提交仅留最终态"
        latest = json.loads(pending[0].read_text(encoding="utf-8"))
        assert set(latest["meta"]["supersedes"]) == {i1["qid"], i2["qid"]}
        assert _blob_content(queue_root, latest, "docs/hot.txt") == b"v3", "快照整体替换=最终态"
        assert not list((queue_root / "done").glob("q-*.json")), "done/ 无中间态记录"

        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 1, "被 compact 的旧项不得再落盘"

    def test_partial_overlap_shrinks_old_item(self, queue_root: Path) -> None:
        """部分覆盖：旧项仅 x.txt 被新项覆盖 → 旧项缩减保留 y.txt（键级精确语义）。"""
        ia = _enqueue(queue_root, "AI-K2", "mA", [("x.txt", b"x1"), ("y.txt", b"y1")])
        ib = _enqueue(queue_root, "AI-K2", "mB", [("x.txt", b"x2")])
        states = _all_state_qids(queue_root)
        assert states == {ia["qid"]: "pending", ib["qid"]: "pending"}
        shrunk = json.loads((queue_root / "pending" / f"{ia['qid']}.json").read_text(encoding="utf-8"))
        assert [f["path"] for f in shrunk["files"]] == ["y.txt"], "被覆盖的 x.txt 从旧项移除"
        assert shrunk["meta"].get("compacted_partial") is True

    def test_cross_session_same_path_no_compaction(self, queue_root: Path) -> None:
        """跨会话同文件不产生覆盖（键不同，66 号 §6.2）——走正常 FIFO。"""
        i1 = _enqueue(queue_root, "AI-K3", "m1", [("same.txt", b"from-A")])
        i2 = _enqueue(queue_root, "AI-K4", "m2", [("same.txt", b"from-B")])
        assert len(list((queue_root / "pending").glob("q-*.json"))) == 2
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 2

    def test_compaction_vs_drain_concurrent_race(self, queue_root: Path) -> None:
        """§11 #7 竞态版：同键连续入队与 drain 并发——无丢失无双落，终态==最后快照。"""
        landed_contents: list[bytes] = []
        errors: list[BaseException] = []
        stop = threading.Event()

        def landing_rec(item: dict, root: Path) -> cq.LandingResult:
            for f in item["files"]:
                landed_contents.append((root / f["blob_ref"]).read_bytes())
            return cq.LandingResult(ok=True, landed_id=f"stub:{item['qid']}")

        def producer() -> None:
            try:
                for v in range(1, 21):
                    _enqueue(queue_root, "AI-K5", f"m{v}", [("hot.txt", f"v{v}".encode())])
                    time.sleep(0)  # 让步制造交错
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)
            finally:
                stop.set()

        def consumer() -> None:
            while not stop.is_set():
                try:
                    cq.drain_queue(queue_root, landing=landing_rec, lease_timeout=0.2)
                except cq.LeaseUnavailable:
                    pass  # 与生产者自举/其他 drain 竞争 lease——正常跳过
                except BaseException as exc:  # noqa: BLE001
                    errors.append(exc)
                    return

        threads = [threading.Thread(target=producer), threading.Thread(target=consumer)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f"并发竞态出现异常: {errors}"
        cq.drain_queue(queue_root, landing=landing_rec)  # 兜底排空

        # 终值正确：最后落盘内容 == 最后入队快照 v20（compaction 语义=最终态正确）
        assert landed_contents, "至少一次落盘"
        assert landed_contents[-1] == b"v20"
        # 内容序单调递增（FIFO+compaction：被覆盖的跳过，落盘的保序）
        seqs = [int(c.decode().lstrip("v")) for c in landed_contents]
        assert seqs == sorted(seqs) and len(seqs) == len(set(seqs))
        # 无丢失无双落：四态目录 qid 无重复（_all_state_qids 内置断言），
        # 未落终态的 qid 均为 compaction 移除（supersedes 链可追溯）
        states = _all_state_qids(queue_root)
        assert all(s in ("done", "pending") for s in states.values())


# ---------------------------------------------------------------------------
# 死信：landing 失败项进 dead/ 带原因，后续项不受影响（66 号 §4 裁定 4 / §6.4）
# ---------------------------------------------------------------------------


class TestDeadLetter:
    def test_failed_item_goes_dead_and_queue_continues(self, queue_root: Path) -> None:
        q1 = _enqueue(queue_root, "AI-D1", "m1", [("ok1.txt", b"1")])["qid"]
        q2 = _enqueue(queue_root, "AI-D1", "m2", [("bad.txt", b"2")])["qid"]
        q3 = _enqueue(queue_root, "AI-D1", "m3", [("ok2.txt", b"3")])["qid"]

        def flaky(item: dict, root: Path) -> cq.LandingResult:
            if any(f["path"] == "bad.txt" for f in item["files"]):
                return cq.LandingResult(ok=False, reason="boom-模拟门禁失败")
            return cq.LandingResult(ok=True, landed_id=f"stub:{item['qid']}")

        stats = cq.drain_queue(queue_root, landing=flaky)
        assert stats["done"] == 2 and stats["dead"] == 1
        # 死信不卡队：三项按 FIFO 全部处理
        assert stats["processed_qids"] == [q1, q2, q3]
        # 死信 JSON：附失败原因 + 属主 + 时间（task_board 打标签 B 段联动点）
        dead_files = list((queue_root / "dead").glob("q-*.json"))
        assert len(dead_files) == 1
        dead = json.loads(dead_files[0].read_text(encoding="utf-8"))
        assert dead["qid"] == q2 and dead["session_id"] == "AI-D1"
        assert "boom-模拟门禁失败" in dead["dead_reason"]
        assert dead["dead_at"]
        # 后续项不受影响：q3 正常 done
        states = _all_state_qids(queue_root)
        assert states[q1] == "done" and states[q2] == "dead" and states[q3] == "done"

    def test_landing_exception_becomes_dead_letter(self, queue_root: Path) -> None:
        """landing 抛普通 Exception = 单项失败 → 死信（与 BaseException 崩溃语义分界）。"""
        _enqueue(queue_root, "AI-D2", "m1", [("x.txt", b"1")])
        _enqueue(queue_root, "AI-D2", "m2", [("y.txt", b"2")])

        def raiser(item: dict, root: Path) -> cq.LandingResult:
            if item["files"][0]["path"] == "x.txt":
                raise RuntimeError("landing 内部错误")
            return cq.LandingResult(ok=True)

        stats = cq.drain_queue(queue_root, landing=raiser)
        assert stats["dead"] == 1 and stats["done"] == 1
        dead = json.loads(next((queue_root / "dead").glob("q-*.json")).read_text(encoding="utf-8"))
        assert "RuntimeError" in dead["dead_reason"]


# ---------------------------------------------------------------------------
# 死信 → task_board 标签联动（66 号 §6.4，P1 2026-08-28 落地）
# ---------------------------------------------------------------------------


class TestDeadLetterTaskBoardLinkage:
    """联动口径：队列项 meta.task_id 存在 → 死信时 task_board metadata_json.deadletter 打标；
    任务不存在/已完成/板不可达/无 task_id → 跳过不阻断排空（宁漏不误）。"""

    @pytest.fixture()
    def board_db(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        db = tmp_path / "task_board.db"
        monkeypatch.setenv("ZEPHYR_TASK_BOARD_DB", str(db))
        return db

    @staticmethod
    def _create_task(title: str = "demo") -> str:
        assert tb.main(["create", "--title", title, "--session", "AI-TEST"]) == 0
        conn = sqlite3.connect(os.environ["ZEPHYR_TASK_BOARD_DB"])
        try:
            row = conn.execute(
                "SELECT task_id FROM tasks ORDER BY created_at DESC, rowid DESC LIMIT 1"
            ).fetchone()
        finally:
            conn.close()
        return row[0]

    @staticmethod
    def _read_metadata(db: Path, task_id: str) -> dict:
        conn = sqlite3.connect(str(db))
        try:
            row = conn.execute("SELECT metadata_json FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        finally:
            conn.close()
        return json.loads(row[0])

    @staticmethod
    def _fail_all(item: dict, root: Path) -> cq.LandingResult:
        return cq.LandingResult(ok=False, reason="boom-模拟门禁失败")

    def _enqueue_with_task(self, root: Path, task_id: str | None) -> dict:
        options = cq.EnqueueOptions(meta_extra={"task_id": task_id} if task_id else None)
        return cq.enqueue_item("AI-DL", "m", [("a.txt", b"1")], queue_root=root, options=options)

    def test_dead_letter_tags_task_board(self, queue_root: Path, board_db: Path) -> None:
        tid = self._create_task()
        item = self._enqueue_with_task(queue_root, tid)
        stats = cq.drain_queue(queue_root, landing=self._fail_all)
        assert stats["dead"] == 1
        tag = self._read_metadata(board_db, tid)["deadletter"]
        assert tag["qid"] == item["qid"]
        assert "boom-模拟门禁失败" in tag["reason"]
        assert tag["owner"] == "AI-DL"
        assert tag["tagged_at"]
        # 事件留痕
        conn = sqlite3.connect(str(board_db))
        try:
            ev = conn.execute(
                "SELECT event_type, actor, payload_json FROM task_events WHERE task_id=? AND event_type='deadlettered'",
                (tid,),
            ).fetchone()
        finally:
            conn.close()
        assert ev is not None and ev[1] == "commit_queue"
        assert json.loads(ev[2])["qid"] == item["qid"]

    def test_task_not_found_skips_without_blocking(self, queue_root: Path, board_db: Path) -> None:
        """meta.task_id 指向不存在任务 → 打标跳过，drain 正常死信落盘。"""
        self._enqueue_with_task(queue_root, "T-nonexistent")
        stats = cq.drain_queue(queue_root, landing=self._fail_all)
        assert stats["dead"] == 1
        assert len(list((queue_root / "dead").glob("q-*.json"))) == 1

    def test_completed_task_rejects_tag_without_blocking(self, queue_root: Path, board_db: Path) -> None:
        tid = self._create_task()
        assert tb.main(["claim", tid, "--session", "AI-TEST"]) == 0
        assert tb.main(["complete", tid, "--session", "AI-TEST"]) == 0
        self._enqueue_with_task(queue_root, tid)
        stats = cq.drain_queue(queue_root, landing=self._fail_all)
        assert stats["dead"] == 1
        assert "deadletter" not in self._read_metadata(board_db, tid)

    def test_no_task_id_no_linkage(self, queue_root: Path, board_db: Path) -> None:
        """无 meta.task_id → 不联动（board DB 文件不被创建）。"""
        self._enqueue_with_task(queue_root, None)
        stats = cq.drain_queue(queue_root, landing=self._fail_all)
        assert stats["dead"] == 1
        assert not board_db.exists()

    def test_board_unreachable_does_not_block_drain(self, queue_root: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """板路径不可写（父路径是文件）→ 联动异常吞掉，drain 不阻断。"""
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        monkeypatch.setenv("ZEPHYR_TASK_BOARD_DB", str(blocker / "task_board.db"))
        self._enqueue_with_task(queue_root, "T-any")
        stats = cq.drain_queue(queue_root, landing=self._fail_all)
        assert stats["dead"] == 1
        assert len(list((queue_root / "dead").glob("q-*.json"))) == 1


# ---------------------------------------------------------------------------
# Serializer lease：活体占用跳过 / 僵尸回收 / TTL 过期回收（66 号 §8 v0.4.0）
# ---------------------------------------------------------------------------


class TestSerializerLease:
    def test_live_lease_blocks_drain_and_bootstrap_skips(self, queue_root: Path) -> None:
        cq._ensure_dirs(queue_root)
        _enqueue(queue_root, "AI-L1", "m", [("a.txt", b"v")])
        # 活体持有：当前进程 PID + 新鲜时间戳
        (queue_root / "serializer.lease").write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": time.time()}), encoding="utf-8"
        )
        with pytest.raises(cq.LeaseUnavailable):
            cq.drain_queue(queue_root, lease_timeout=0.2)
        result = cq.try_bootstrap_drain(queue_root)
        assert result["skipped"] is True and result["reason"] == "lease_unavailable"
        # 项未被动：仍在 pending（等下次自举，66 号 §8 自举放弃语义）
        assert len(list((queue_root / "pending").glob("q-*.json"))) == 1

    def test_zombie_lease_reclaimed(self, queue_root: Path) -> None:
        _enqueue(queue_root, "AI-L2", "m", [("a.txt", b"v")])
        # 僵尸持有：不可能存活的 PID（Windows PID 远小于此值且为 4 的倍数）
        (queue_root / "serializer.lease").write_text(
            json.dumps({"pid": 0x3FFFFFFC, "acquired_at": time.time()}), encoding="utf-8"
        )
        stats = cq.drain_queue(queue_root, lease_timeout=1.0)
        assert stats["done"] == 1, "僵尸 lease MUST 被检测回收后排空"

    def test_expired_lease_reclaimed(self, queue_root: Path) -> None:
        _enqueue(queue_root, "AI-L3", "m", [("a.txt", b"v")])
        # TTL 过期：活 PID 但 acquired_at 超 300s
        (queue_root / "serializer.lease").write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": time.time() - 400}), encoding="utf-8"
        )
        stats = cq.drain_queue(queue_root, lease_timeout=1.0)
        assert stats["done"] == 1

    def test_lease_released_after_drain(self, queue_root: Path) -> None:
        cq.drain_queue(queue_root)
        assert not (queue_root / "serializer.lease").exists(), "排空后 lease MUST 释放"


# ---------------------------------------------------------------------------
# status（66 号 §6.6 落盘确认接口）+ meta.depends_on schema 预留
# ---------------------------------------------------------------------------


class TestStatus:
    def test_counts_and_session_filter(self, queue_root: Path) -> None:
        _enqueue(queue_root, "AI-S1", "m1", [("a.txt", b"1")])
        _enqueue(queue_root, "AI-S2", "m2", [("b.txt", b"2")])
        report = cq.queue_status(queue_root)
        assert report["counts"]["pending"] == 2 and report["total"] == 2
        own = cq.queue_status(queue_root, session_id="AI-S1")
        assert own["total"] == 1 and own["items"][0]["session_id"] == "AI-S1"

    def test_depends_on_schema_reserved(self, queue_root: Path) -> None:
        """meta.depends_on 预留字段落盘（P1 起 drain 级联标记消费该字段，66 号 §6.4）。"""
        item = cq.enqueue_item(
            "AI-S3",
            "m",
            [("a.txt", b"1")],
            queue_root=queue_root,
            options=cq.EnqueueOptions(depends_on=["q-20260821-x-0001"]),
        )
        assert item["meta"]["depends_on"] == ["q-20260821-x-0001"]
        on_disk = json.loads((queue_root / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert on_disk["meta"]["depends_on"] == ["q-20260821-x-0001"]


# ---------------------------------------------------------------------------
# P1 级联标记（66 号 §6.4 + 08 号文 §4.3，2026-08-29 落地）：
# X 成功落盘后 depends_on 含 X.qid / base_head 经由 X 的 pending 项标 stale；
# stale 项重校验基底——仍适用清标放行，不适用降死信候选（cascade_stale）
# ---------------------------------------------------------------------------


def _inject_base_blob(root: Path, qid: str, path: str, base_blob: str) -> None:
    """模拟 B 段填充 base_blob（A 段 enqueue 恒为 None）——手写 pending 项 JSON。"""
    p = root / "pending" / f"{qid}.json"
    item = json.loads(p.read_text(encoding="utf-8"))
    for f in item["files"]:
        if f["path"] == path:
            f["base_blob"] = base_blob
    p.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


class TestCascadeStale:
    def test_depends_on_hit_marked_stale_then_cleared_and_landed(self, queue_root: Path) -> None:
        ix = _enqueue(queue_root, "AI-X", "mx", [("x.txt", b"x")])
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")],
            queue_root=queue_root, options=cq.EnqueueOptions(depends_on=[ix["qid"]]),
        )
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 2 and stats["dead"] == 0
        assert stats["cascade_marked"] == 1, "depends_on 含 X.qid 的后续项 MUST 标 stale"
        # base_blob 全空（A 段口径）→ 重校验放行，清标
        assert stats["stale_cleared"] == 1
        done_y = json.loads((queue_root / "done" / f"{iy['qid']}.json").read_text(encoding="utf-8"))
        assert "stale" not in done_y["meta"], "重校验通过 MUST 清 stale 标"
        assert done_y["meta"]["stale_by"] == ix["qid"], "stale_by 保留作审计溯源"
        assert done_y["meta"]["stale_cleared_at"]

    def test_base_head_equality_marked_stale(self, queue_root: Path) -> None:
        """base_head 经由 X（同基底入队）的后续项标 stale；不同基底不标。"""
        ix = cq.enqueue_item("AI-X", "mx", [("x.txt", b"x")], queue_root=queue_root,
                             options=cq.EnqueueOptions(base_head="sha-base"))
        iy = cq.enqueue_item("AI-Y", "my", [("y.txt", b"y")], queue_root=queue_root,
                             options=cq.EnqueueOptions(base_head="sha-base"))
        iz = cq.enqueue_item("AI-Z", "mz", [("z.txt", b"z")], queue_root=queue_root,
                             options=cq.EnqueueOptions(base_head="sha-other"))
        stats = cq.drain_queue(queue_root)
        assert stats["cascade_marked"] == 1
        done_y = json.loads((queue_root / "done" / f"{iy['qid']}.json").read_text(encoding="utf-8"))
        assert done_y["meta"]["stale_by"] == ix["qid"]
        done_z = json.loads((queue_root / "done" / f"{iz['qid']}.json").read_text(encoding="utf-8"))
        assert "stale_by" not in done_z["meta"], "base_head 不同（非经由 X）不标 stale"

    def test_unrelated_items_not_marked(self, queue_root: Path) -> None:
        """无 depends_on 且 base_head 均空 → 零级联标记。"""
        _enqueue(queue_root, "AI-X", "m1", [("a.txt", b"1")])
        _enqueue(queue_root, "AI-Y", "m2", [("b.txt", b"2")])
        stats = cq.drain_queue(queue_root)
        assert stats["cascade_marked"] == 0 and stats["stale_cleared"] == 0
        assert stats["done"] == 2

    def test_stale_revalidate_mismatch_goes_dead_cascade_stale(self, queue_root: Path) -> None:
        """stale 项基底重校验不一致 → 降死信候选（dead_reason=cascade_stale），不消耗 landing。"""
        ix = _enqueue(queue_root, "AI-X", "mx", [("x.txt", b"x")])
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")],
            queue_root=queue_root, options=cq.EnqueueOptions(depends_on=[ix["qid"]]),
        )
        _inject_base_blob(queue_root, iy["qid"], "y.txt", "blob-old")
        landed: list[str] = []

        def rec(item: dict, root: Path) -> cq.LandingResult:
            landed.append(item["qid"])
            return cq.LandingResult(ok=True)

        stats = cq.drain_queue(queue_root, landing=rec, head_reader=lambda path: "blob-new")
        assert stats["done"] == 1 and stats["dead"] == 1
        assert landed == [ix["qid"]], "stale 重校验不适用 MUST 直接降死信候选，不消耗 landing"
        dead = json.loads(next((queue_root / "dead").glob("q-*.json")).read_text(encoding="utf-8"))
        assert dead["qid"] == iy["qid"]
        assert "cascade_stale" in dead["dead_reason"]
        assert "y.txt" in dead["dead_reason"]

    def test_stale_revalidate_match_passes(self, queue_root: Path) -> None:
        """stale 项基底重校验逐文件一致 → 清标放行走正常 landing。"""
        ix = _enqueue(queue_root, "AI-X", "mx", [("x.txt", b"x")])
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")],
            queue_root=queue_root, options=cq.EnqueueOptions(depends_on=[ix["qid"]]),
        )
        _inject_base_blob(queue_root, iy["qid"], "y.txt", "blob-y")
        stats = cq.drain_queue(queue_root, head_reader=lambda path: "blob-y")
        assert stats["done"] == 2 and stats["dead"] == 0
        assert stats["stale_cleared"] == 1

    def test_stale_base_blob_without_head_reader_fail_closed(self, queue_root: Path) -> None:
        """base_blob 非空而 head_reader 缺失 → fail-closed 降死信候选（无法确认仍适用）。"""
        ix = _enqueue(queue_root, "AI-X", "mx", [("x.txt", b"x")])
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")],
            queue_root=queue_root, options=cq.EnqueueOptions(depends_on=[ix["qid"]]),
        )
        _inject_base_blob(queue_root, iy["qid"], "y.txt", "blob-y")
        stats = cq.drain_queue(queue_root)  # head_reader=None
        assert stats["done"] == 1 and stats["dead"] == 1
        dead = json.loads(next((queue_root / "dead").glob("q-*.json")).read_text(encoding="utf-8"))
        assert dead["qid"] == iy["qid"]
        assert "cascade_stale" in dead["dead_reason"]
        assert "head_reader" in dead["dead_reason"]

    def test_stale_mark_persisted_on_disk_before_processing(self, queue_root: Path) -> None:
        """级联标记落盘留痕：max_items=1 仅处理 X，Y 留 pending 且盘上带 stale 标。"""
        ix = _enqueue(queue_root, "AI-X", "mx", [("x.txt", b"x")])
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")],
            queue_root=queue_root, options=cq.EnqueueOptions(depends_on=[ix["qid"]]),
        )
        stats = cq.drain_queue(queue_root, max_items=1)
        assert stats["done"] == 1 and stats["cascade_marked"] == 1
        pending_y = json.loads((queue_root / "pending" / f"{iy['qid']}.json").read_text(encoding="utf-8"))
        assert pending_y["meta"]["stale"] is True
        assert pending_y["meta"]["stale_by"] == ix["qid"]
        assert pending_y["meta"]["stale_at"]


# ---------------------------------------------------------------------------
# P1 死信重新入队（66 号 §6.4 死信闭环 + 08 号文 §4.3，2026-08-29 落地）：
# 从 dead/ 取回，基于当前工作区重建快照重新入队（新 qid 排尾），取回留痕
# ---------------------------------------------------------------------------


class TestRequeue:
    @staticmethod
    def _make_dead(root: Path, files: list[tuple[str, bytes]] | None = None, task_id: str | None = None) -> dict:
        options = cq.EnqueueOptions(meta_extra={"task_id": task_id} if task_id else None)
        item = cq.enqueue_item("AI-R", "m-orig", files or [("a.txt", b"v1")], queue_root=root, options=options)
        stats = cq.drain_queue(root, landing=lambda i, r: cq.LandingResult(ok=False, reason="boom-模拟门禁失败"))
        assert stats["dead"] == 1
        return item

    def test_requeue_rebuilds_snapshot_from_current_worktree(self, queue_root: Path, tmp_path: Path) -> None:
        old = self._make_dead(queue_root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2-current")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        # 新 qid 口径：不复用原 qid，排 FIFO 队尾
        assert result["new_qid"] != result["old_qid"]
        new_item = result["item"]
        assert new_item["meta"]["requeued_from"] == old["qid"]
        assert _blob_content(queue_root, new_item, "a.txt") == b"v2-current", "基于当前工作区重建快照"
        assert (queue_root / "pending" / f"{result['new_qid']}.json").exists()
        # 取回留痕：原死信项留 dead/（永不清理）追加 requeued 标注
        dead = json.loads((queue_root / "dead" / f"{old['qid']}.json").read_text(encoding="utf-8"))
        assert dead["requeued"]["new_qid"] == result["new_qid"]
        assert dead["requeued"]["at"]
        assert dead["dead_reason"]  # 死信事实留痕不抹除

    def test_requeue_closed_loop_lands(self, queue_root: Path, tmp_path: Path) -> None:
        """死信取回重入队闭环演示（66 号 §10 P1 验收行）：dead → requeue → drain → done。"""
        old = self._make_dead(queue_root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 1 and stats["dead"] == 0
        states = _all_state_qids(queue_root)
        assert states[old["qid"]] == "dead", "原死信项留 dead/ 留痕"
        assert states[result["new_qid"]] == "done"

    def test_requeue_non_dead_qid_error(self, queue_root: Path, tmp_path: Path) -> None:
        item = _enqueue(queue_root, "AI-R", "m", [("a.txt", b"v")])  # 仍在 pending
        with pytest.raises(cq.RequeueError, match="不在 dead/"):
            cq.requeue_dead_item(item["qid"], queue_root=queue_root, worktree_root=tmp_path)
        with pytest.raises(cq.RequeueError, match="不在 dead/"):
            cq.requeue_dead_item("q-20260829-AI-X-0001", queue_root=queue_root, worktree_root=tmp_path)

    def test_requeue_qid_path_traversal_rejected(self, queue_root: Path) -> None:
        """qid 拼 dead/ 文件路径——路径穿越必须 fail-closed 拒绝。"""
        with pytest.raises(cq.RequeueError, match="非法 qid"):
            cq.requeue_dead_item("../../etc/passwd", queue_root=queue_root)
        with pytest.raises(cq.RequeueError, match="非法 qid"):
            cq.requeue_dead_item("q-20260829-a b-0001", queue_root=queue_root)

    def test_requeue_missing_worktree_file_error(self, queue_root: Path, tmp_path: Path) -> None:
        old = self._make_dead(queue_root)  # 引用 a.txt
        wt = tmp_path / "wt"
        wt.mkdir()  # 空工作区
        with pytest.raises(cq.RequeueError, match="无法重建快照"):
            cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        assert not list((queue_root / "pending").glob("q-*.json")), "取回失败 MUST 不产生新项"
        dead = json.loads((queue_root / "dead" / f"{old['qid']}.json").read_text(encoding="utf-8"))
        assert "requeued" not in dead, "取回失败 MUST 不留 requeued 标注"

    def test_requeue_delete_entry_passthrough(self, queue_root: Path, tmp_path: Path) -> None:
        """action=delete 条目走 deletes 通道（无 blob，不读工作区）。"""
        item = cq.enqueue_item(
            "AI-R", "m-del", [], queue_root=queue_root,
            options=cq.EnqueueOptions(deletes=["gone.txt"]),
        )
        cq.drain_queue(queue_root, landing=lambda i, r: cq.LandingResult(ok=False, reason="boom"))
        result = cq.requeue_dead_item(item["qid"], queue_root=queue_root, worktree_root=tmp_path)
        new_item = result["item"]
        assert [f["path"] for f in new_item["files"]] == ["gone.txt"]
        assert new_item["files"][0]["action"] == "delete"
        assert new_item["files"][0]["blob_sha256"] is None

    def test_requeue_taskboard_annotation(self, queue_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """task_board 死信标签同步标注 requeued（标签不解除，死信事实留痕）。"""
        db = tmp_path / "task_board.db"
        monkeypatch.setenv("ZEPHYR_TASK_BOARD_DB", str(db))
        assert tb.main(["create", "--title", "demo", "--session", "AI-TEST"]) == 0
        conn = sqlite3.connect(str(db))
        try:
            tid = conn.execute("SELECT task_id FROM tasks LIMIT 1").fetchone()[0]
        finally:
            conn.close()
        old = self._make_dead(queue_root, task_id=tid)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        result = cq.requeue_dead_item(old["qid"], queue_root=queue_root, worktree_root=wt)
        conn = sqlite3.connect(str(db))
        try:
            metadata = json.loads(
                conn.execute("SELECT metadata_json FROM tasks WHERE task_id=?", (tid,)).fetchone()[0]
            )
            ev = conn.execute(
                "SELECT actor, payload_json FROM task_events WHERE task_id=? AND event_type='requeued'", (tid,)
            ).fetchone()
        finally:
            conn.close()
        tag = metadata["deadletter"]
        assert tag["qid"] == old["qid"], "死信标签不解除"
        assert tag["requeued"]["old_qid"] == old["qid"]
        assert tag["requeued"]["new_qid"] == result["new_qid"]
        assert tag["requeued"]["requeued_at"]
        assert ev is not None and ev[0] == "commit_queue"
        assert json.loads(ev[1])["new_qid"] == result["new_qid"]
        # 新项继承 task_id——再失败可继续打标同一任务（闭环可持续）
        assert result["item"]["meta"]["task_id"] == tid

    def test_requeue_cli(self, queue_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        old = self._make_dead(queue_root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2")
        rc = cq.main([
            "--queue-root", str(queue_root),
            "requeue", old["qid"], "--worktree-root", str(wt), "--no-bootstrap",
        ])
        assert rc == 0
        assert "REQUEUED" in capsys.readouterr().out
        # CLI 错误路径：非死信 qid → exit 1（ERROR 非静默）
        rc = cq.main([
            "--queue-root", str(queue_root),
            "requeue", "q-20260829-AI-X-0001", "--no-bootstrap",
        ])
        assert rc == 1
        assert "ERROR" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# P1 done/ TTL 清理（66 号 §12 Q3：done 7 天 TTL / dead 永不自动清理，
# 2026-08-29 落地）——dead 永不清理不变量专测钉死
# ---------------------------------------------------------------------------


def _age_done_item(root: Path, qid: str, days: float) -> None:
    """手工陈化 done 项 landed_at（TTL 判定基准）。"""
    p = root / "done" / f"{qid}.json"
    item = json.loads(p.read_text(encoding="utf-8"))
    item["landed_at"] = (datetime.now().astimezone() - timedelta(days=days)).isoformat(timespec="seconds")
    p.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


class TestDoneTtlCleanup:
    def test_expired_done_removed_fresh_kept(self, queue_root: Path) -> None:
        i1 = _enqueue(queue_root, "AI-T1", "m1", [("a.txt", b"1")])
        i2 = _enqueue(queue_root, "AI-T1", "m2", [("b.txt", b"2")])
        cq.drain_queue(queue_root)
        _age_done_item(queue_root, i1["qid"], days=8)
        result = cq.cleanup_done(queue_root, ttl_days=7)
        assert result["removed"] == [i1["qid"]]
        assert result["kept"] == 1
        assert not (queue_root / "done" / f"{i1['qid']}.json").exists()
        assert (queue_root / "done" / f"{i2['qid']}.json").exists()

    def test_dead_never_cleaned_invariant(self, queue_root: Path) -> None:
        """不变量钉死（66 号 §8）：dead/ 永不自动清理——超龄死信 + TTL=0 极端值也不动。"""
        i1 = _enqueue(queue_root, "AI-T2", "m1", [("a.txt", b"1")])
        _enqueue(queue_root, "AI-T2", "m2", [("b.txt", b"2")])
        cq.drain_queue(
            queue_root,
            landing=lambda i, r: cq.LandingResult(ok=False, reason="boom")
            if any(f["path"] == "b.txt" for f in i["files"])
            else cq.LandingResult(ok=True),
        )
        _age_done_item(queue_root, i1["qid"], days=30)
        dead_path = next((queue_root / "dead").glob("q-*.json"))
        dead = json.loads(dead_path.read_text(encoding="utf-8"))
        dead["dead_at"] = (datetime.now().astimezone() - timedelta(days=30)).isoformat(timespec="seconds")
        dead_path.write_text(json.dumps(dead, ensure_ascii=False, indent=2), encoding="utf-8")
        result = cq.cleanup_done(queue_root, ttl_days=0)  # TTL=0 极端值
        assert result["removed"] == [i1["qid"]], "超龄 done 全清理"
        assert dead_path.exists(), "dead/ 永不自动清理不变量破裂"
        on_disk = json.loads(dead_path.read_text(encoding="utf-8"))
        assert on_disk["dead_reason"] == "boom", "dead/ 内容不被清理流程改动"

    def test_ttl_configurable(self, queue_root: Path) -> None:
        i1 = _enqueue(queue_root, "AI-T3", "m1", [("a.txt", b"1")])
        cq.drain_queue(queue_root)
        _age_done_item(queue_root, i1["qid"], days=3)
        result = cq.cleanup_done(queue_root, ttl_days=7)
        assert result["removed"] == [] and result["kept"] == 1, "3 天 < 7 天 TTL 保留"
        result = cq.cleanup_done(queue_root, ttl_days=2)
        assert result["removed"] == [i1["qid"]], "3 天 > 2 天 TTL 清理（可配置生效）"

    def test_drain_auto_cleanup(self, queue_root: Path) -> None:
        """drain 收尾自动清理（lease 内单写者）：超龄 done 项随排空移除。"""
        i1 = _enqueue(queue_root, "AI-T4", "m1", [("a.txt", b"1")])
        cq.drain_queue(queue_root)
        _age_done_item(queue_root, i1["qid"], days=8)
        i2 = _enqueue(queue_root, "AI-T4", "m2", [("b.txt", b"2")])
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 1
        assert stats["done_cleaned"] == 1
        assert not (queue_root / "done" / f"{i1['qid']}.json").exists()
        assert (queue_root / "done" / f"{i2['qid']}.json").exists()

    def test_cleanup_cli(self, queue_root: Path, capsys: pytest.CaptureFixture) -> None:
        i1 = _enqueue(queue_root, "AI-T5", "m1", [("a.txt", b"1")])
        cq.drain_queue(queue_root)
        _age_done_item(queue_root, i1["qid"], days=8)
        rc = cq.main(["--queue-root", str(queue_root), "cleanup"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "CLEANUP" in out and "removed=1" in out
