# [A_test] module_id: MOD-GOV-046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §C1
# [MODULE] tests.governance.test_commit_queue_c1_debounce
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_c1_debounce.py
# [MATURITY] testing
# [INVARIANTS] 全部 tmp_path 隔离，不碰真实 .runtime/commit_queue 与 git；合批只对同会话+同 worktree-root 生效；文件集并集不变（零内容改动）；absorbed qid 永不落任何状态目录
# [MODIFY-GUARD] 提速战役 T11/C1（00_MASTER_PLAN §5 批次判据：件数/日 158→<60、文件中位/件 1→>5）；A4 阶梯 S7「批均规模 ≥3」前置编排档；66 号 §6 协议不破
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_c1_debounce.py — C1 同会话短窗自动合批红绿测试。

断言清单真源（T11/C1 作业簿 + 00_MASTER_PLAN §2 红线）：
1. 红证（HEAD 现码必红）：同会话短窗两件互斥路径入队 → 现码两件 pending 不合。
2. 修后绿：20 分钟窗内同会话+同 worktree-root 自动并入前件（文件集并集、内容逐字节
   可溯源、created_at 保持前件=先来先服务不破 B4 排队键）。
3. 红线三不并：跨会话不并；跨 worktree-root 不并；窗口外（>20 分钟）不并。
4. supersedes 链正确：absorbed qid 记入目标 meta.supersedes（与 compaction 同名册）；
   后续 compaction 整体覆盖时传递累积（q3.supersedes=[q1,q2]）；absorbed qid 永不
   落 pending/processing/done/dead 任一目录（不是真队列项）。
5. 资格闸：stale/attempts>0/depends_on（任一侧）/lane 混用/base_head 不同/超 R2
   大批硬顶 → 一律不并（宁不并不错并）。
6. 开关：env ZEPHYR_CQ_C1_DEBOUNCE=0 → 关闭回退现行为（多件不合）。
7. 向后兼容：不带 worktree_root 的调用方（gateway 直调等）行为不变（不合批）。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import scripts.commit_queue as cq

DEBOUNCE_ENV = "ZEPHYR_CQ_C1_DEBOUNCE"
WINDOW_SECONDS = 1200.0


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    """队列根固定落 tmp_path（隔离真实 .runtime/commit_queue；测试隔离铁律）。"""
    return tmp_path / "commit_queue"


@pytest.fixture()
def wt1(tmp_path: Path) -> str:
    d = tmp_path / "wt_a"
    d.mkdir()
    return str(d)


@pytest.fixture()
def wt2(tmp_path: Path) -> str:
    d = tmp_path / "wt_b"
    d.mkdir()
    return str(d)


def _enqueue(root, session, msg, files, wt=None, **opt_kwargs):
    opts = cq.EnqueueOptions(worktree_root=wt, **opt_kwargs)
    return cq.enqueue_item(session, msg, files, queue_root=root, options=opts)


def _pending_items(root: Path) -> list[dict]:
    out = []
    for p in sorted((root / "pending").glob("q-*.json")):
        out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def _all_state_qids(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for state in ("pending", "processing", "done", "dead"):
        for f in sorted((root / state).glob("q-*.json")):
            assert f.stem not in out, f"零双落不变量破裂: {f.stem}"
            out[f.stem] = state
    return out


def _backdate_created_at(root: Path, qid: str, minutes: float) -> None:
    """把指定 pending 项的 created_at 回拨（模拟窗口外老件）。"""
    p = root / "pending" / f"{qid}.json"
    item = json.loads(p.read_text(encoding="utf-8"))
    item["created_at"] = (datetime.now().astimezone() - timedelta(minutes=minutes)).isoformat(timespec="seconds")
    p.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. 红证：HEAD 现码多件不合（修后转绿的同一条断言）
# ---------------------------------------------------------------------------


class TestC1RedThenGreen:
    def test_same_session_short_window_merges_into_pending_head(self, queue_root, wt1):
        """同会话+同 worktree-root+窗口内：第二件并入前件（文件并集、qid 保持前件）。"""
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        it2 = _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        # 并入前件：返回 qid=前件；absorbed 记录被吸收的提交序列号
        assert it2["qid"] == it1["qid"], "第二件应并入前件（同 qid）"
        assert it2["absorbed"]["qid"].startswith("q-") and it2["absorbed"]["qid"] != it1["qid"]
        assert it2["absorbed"]["files"] == 1
        pend = _pending_items(queue_root)
        assert len(pend) == 1, f"修后应只剩 1 件 pending，实得 {len(pend)}"
        item = pend[0]
        paths = sorted(f["path"] for f in item["files"])
        assert paths == ["a.py", "b.py"], f"文件集并集不变: {paths}"
        # 内容逐字节可溯源
        blobs = {f["path"]: f["blob_sha256"] for f in item["files"]}
        assert (queue_root / "blobs" / blobs["a.py"]).read_bytes() == b"A1"
        assert (queue_root / "blobs" / blobs["b.py"]).read_bytes() == b"B1"
        # created_at 保持前件（先来先服务，B4 排队键语义不破）
        assert item["created_at"] == it1["created_at"]
        # 吸收痕迹：supersedes 同名册 + absorbed 明细 + message 尾注
        assert item["meta"]["supersedes"] == [it2["absorbed"]["qid"]]
        assert item["meta"]["merged_count"] == 1
        assert item["meta"]["absorbed"][0]["qid"] == it2["absorbed"]["qid"]
        assert "m2" in item["message"] and item["message"].startswith("m1")

    def test_head_code_does_not_merge(self, queue_root, wt1):
        """红证锚点：开关关闭（=回退现行为）时同窗两件不合——本断言在修前修后恒真，
        与上一条合并断言构成红绿对（现码跑合并断言必红）。"""
        monkey_off = "0"
        import os

        os.environ[DEBOUNCE_ENV] = monkey_off
        try:
            _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
            _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
            assert len(_pending_items(queue_root)) == 2, "开关关闭=现行为：两件不合"
        finally:
            os.environ.pop(DEBOUNCE_ENV, None)

    def test_merged_item_lands_as_one_with_union(self, queue_root, wt1):
        """合并件排空（stub landing）：单件落地、文件数=并集、absorbed qid 不落任何目录。"""
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        it2 = _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        stats = cq.drain_queue(queue_root)
        assert stats["done"] == 1 and stats["dead"] == 0
        done = list((queue_root / "done").glob("q-*.json"))
        assert len(done) == 1 and done[0].stem == it1["qid"]
        landed = json.loads(done[0].read_text(encoding="utf-8"))
        assert len(landed["files"]) == 2
        # absorbed qid 是"序列号消耗"而非队列项——四态目录均不可见
        states = _all_state_qids(queue_root)
        assert it2["absorbed"]["qid"] not in states

    def test_same_path_overlap_still_compaction_wins(self, queue_root, wt1):
        """同路径重入仍是 compaction 覆盖语义（C1 只吃互斥路径，不改变既有机制）。"""
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        it2 = _enqueue(queue_root, "s1", "m2", [("a.py", b"A2")], wt=wt1)
        pend = _pending_items(queue_root)
        assert len(pend) == 1
        assert pend[0]["qid"] == it2["qid"], "同路径=整体覆盖：新 qid 新件（compaction 原语义）"
        assert pend[0]["meta"]["supersedes"] == [it1["qid"]]


# ---------------------------------------------------------------------------
# 2. 红线三不并 + 资格闸（修后恒真；修前因"永不合并"碰巧为真，作回归护栏）
# ---------------------------------------------------------------------------


class TestC1NoMergeGuards:
    def test_cross_session_never_merges(self, queue_root, wt1):
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        _enqueue(queue_root, "s2", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "跨会话绝不合并（红线）"

    def test_cross_worktree_never_merges(self, queue_root, wt1, wt2):
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt2)
        assert len(_pending_items(queue_root)) == 2, "跨 worktree-root 不合并（红线）"

    def test_window_expiry_no_merge(self, queue_root, wt1):
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        _backdate_created_at(queue_root, it1["qid"], minutes=(WINDOW_SECONDS / 60.0) + 1.0)
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "窗口外（>20 分钟）不合"

    def test_stale_target_no_merge(self, queue_root, wt1):
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        p = queue_root / "pending" / f"{it1['qid']}.json"
        item = json.loads(p.read_text(encoding="utf-8"))
        item["meta"]["stale"] = True
        p.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "stale 目标不吸收"

    def test_attempts_target_no_merge(self, queue_root, wt1):
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        p = queue_root / "pending" / f"{it1['qid']}.json"
        item = json.loads(p.read_text(encoding="utf-8"))
        item["attempts"] = 1
        p.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "失败退回件（attempts>0）不吸收"

    def test_incoming_depends_on_no_merge(self, queue_root, wt1):
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1, depends_on=["q-x-1"])
        assert len(_pending_items(queue_root)) == 2, "显式依赖链是调用方编排，不自动并"

    def test_target_depends_on_no_merge(self, queue_root, wt1):
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        p = queue_root / "pending" / f"{it1['qid']}.json"
        item = json.loads(p.read_text(encoding="utf-8"))
        item["meta"]["depends_on"] = ["q-y-1"]
        p.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "依赖链目标不吸收新件"

    def test_lane_mixed_no_merge(self, queue_root, wt1):
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1, meta_extra={"lane": "machine"})
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "interactive/machine 车道不混并"

    def test_lane_same_machine_merges(self, queue_root, wt1):
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1, meta_extra={"lane": "machine"})
        it2 = _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1, meta_extra={"lane": "machine"})
        assert it2["qid"] == it1["qid"], "同 lane（machine）窗口内合并"
        assert len(_pending_items(queue_root)) == 1

    def test_base_head_differs_no_merge(self, queue_root, wt1):
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1, base_head="deadbeef01")
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1, base_head="deadbeef02")
        assert len(_pending_items(queue_root)) == 2, "基底不同不并（重校验口径一致性）"

    def test_over_batch_cap_no_merge(self, queue_root, wt1, monkeypatch):
        monkeypatch.setattr(cq, "_MAX_BATCH_FILES", 2)
        _enqueue(queue_root, "s1", "m1", [("a1.py", b"1"), ("a2.py", b"2")], wt=wt1)
        _enqueue(queue_root, "s1", "m2", [("b1.py", b"3")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "R2 大批硬顶不因合批而破"

    def test_task_id_mismatch_no_merge(self, queue_root, wt1):
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1, meta_extra={"task_id": "T-1"})
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1, meta_extra={"task_id": "T-2"})
        assert len(_pending_items(queue_root)) == 2, "task_id 不同的袋不混并（死信打标归属不串）"

    def test_legacy_no_worktree_root_backward_compatible(self, queue_root):
        """不带 worktree_root 的调用方（gateway 直调等）：行为与修前逐字节一致（不合批）。"""
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")])
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")])
        assert len(_pending_items(queue_root)) == 2
        pend = _pending_items(queue_root)
        assert all("worktree_root" not in (it.get("meta") or {}) for it in pend)


# ---------------------------------------------------------------------------
# 3. supersedes 链与开关
# ---------------------------------------------------------------------------


class TestC1ChainAndFlag:
    def test_supersedes_chain_transitive_through_compaction(self, queue_root, wt1):
        """吸收链传递：q2 并入 q1（q1.supersedes=[q2]）→ q3 整体覆盖 q1 →
        compaction 传递累积 ⇒ q3.supersedes=[q1,q2]。"""
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        it2 = _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        absorbed_qid = it2["absorbed"]["qid"]
        it3 = _enqueue(queue_root, "s1", "m3", [("a.py", b"A2"), ("b.py", b"B2")], wt=wt1)
        assert it3["qid"] != it1["qid"]
        assert it3["meta"]["supersedes"] == [it1["qid"], absorbed_qid], "覆盖链传递累积（直接前驱在前）"
        assert len(_pending_items(queue_root)) == 1

    def test_double_absorb_chain(self, queue_root, wt1):
        """三件连发：q2、q3 依次并入 q1，supersedes 保序累积，merged_count=2。"""
        it1 = _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        it2 = _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        it3 = _enqueue(queue_root, "s1", "m3", [("c.py", b"C1")], wt=wt1)
        assert it3["qid"] == it1["qid"]
        pend = _pending_items(queue_root)
        assert len(pend) == 1
        assert sorted(f["path"] for f in pend[0]["files"]) == ["a.py", "b.py", "c.py"]
        assert pend[0]["meta"]["supersedes"] == [it2["absorbed"]["qid"], it3["absorbed"]["qid"]]
        assert pend[0]["meta"]["merged_count"] == 2

    def test_flag_off_disables_merge(self, queue_root, wt1, monkeypatch):
        monkeypatch.setenv(DEBOUNCE_ENV, "0")
        _enqueue(queue_root, "s1", "m1", [("a.py", b"A1")], wt=wt1)
        _enqueue(queue_root, "s1", "m2", [("b.py", b"B1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 2, "开关 OFF=回退现行为"
        monkeypatch.setenv(DEBOUNCE_ENV, "false")
        _enqueue(queue_root, "s1", "m3", [("c.py", b"C1")], wt=wt1)
        assert len(_pending_items(queue_root)) == 3


# ---------------------------------------------------------------------------
# 4. CLI 层：--worktree-root 透传 + C1-MERGED 回执
# ---------------------------------------------------------------------------


class TestC1Cli:
    def test_cli_enqueue_merges_within_window(self, queue_root, tmp_path, capsys):
        wt = tmp_path / "wt_cli"
        wt.mkdir()
        # 夹具内容须 ruff 稳定的合法 Python：CLI 入队口现挂确定性 ruff 快检（Rx-5
        # st-finaldel-crx-20260929，RUFF-PRECLEAN），`A1` 裸表达式在预检即被拦到不了
        # C1 合批——本尺守卫意图是「CLI 短窗合批回执 C1-MERGED」，文件内容与判据无关。
        (wt / "a.py").write_bytes(b"A1 = 1\n")
        (wt / "b.py").write_bytes(b"B1 = 1\n")
        rc1 = cq.main(
            [
                "--queue-root",
                str(queue_root),
                "enqueue",
                "--session",
                "c1cli",
                "--files",
                "a.py",
                "--message",
                "m1",
                "--worktree-root",
                str(wt),
                "--no-bootstrap",
            ]
        )
        assert rc1 == 0
        out1 = capsys.readouterr().out
        assert "ENQUEUED" in out1
        rc2 = cq.main(
            [
                "--queue-root",
                str(queue_root),
                "enqueue",
                "--session",
                "c1cli",
                "--files",
                "b.py",
                "--message",
                "m2",
                "--worktree-root",
                str(wt),
                "--no-bootstrap",
            ]
        )
        assert rc2 == 0
        out2 = capsys.readouterr().out
        assert "C1-MERGED" in out2, f"CLI 应回执合批: {out2}"
        assert len(_pending_items(queue_root)) == 1
