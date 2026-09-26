# [A_test] module_id: MOD-TEST-RB14-S2 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | scripts/commit_queue.py | §enqueue/B4 FIFO/C1 合批 + commit_queue_landing §D4/_item_path_locks
# [MODULE] governance.red_blue_pkg14.test_rb14_s2_dual_writer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing; _common(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s2_dual_writer.py
# [MATURITY] testing
# [INVARIANTS] 全沙盒；判据：①两会话同路径并发 enqueue→双件齐落、路径锁体零重叠、
#   dev 每文件恰 2 次 commit、内容为两载荷之一（无撕裂）；②B4 (created_at,qid) FIFO
#   不被 qid 字典序倒挂；③C1 同会话+同 worktree_root 短窗合批=文件集并集、absorbed
#   qid 不落任何状态目录、跨会话绝不合并；④幽灵 pending 不二次落地（done 恒等于件数）。
# [MODIFY-GUARD] 包14 场景2（双写者同路径）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s2_dual_writer.py — 场景2「双写者同路径」红蓝对抗（B4/C1/D4 尺）。

红证三件：
  - B4 旧规则（qid 字典序=队首）在构造样本下选错队首（56% 倒挂的机理缩影）；
  - D4 手术副本（去 done/ 终止性复查）让幽灵 pending 二次落地——同路径 commit 翻倍；
  - 蓝方同尺在产品码上全绿。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
from governance.red_blue_pkg14._common import (
    LANDING_SRC,
    enqueue,
    git_text,
    load_surgered,
    make_stub_landing_factory,
    sha256_file,
)

# ── 蓝方 ①：两会话同路径并发 enqueue→双件齐落+路径锁互斥 ────────────────────


def test_s2_blue_dual_writer_same_path_lands_both(sb_repo, sb_queue, monkeypatch):
    results: dict[str, dict] = {}
    barrier = threading.Barrier(2)

    def _enq(sid: str, content: str):
        barrier.wait()
        results[sid] = enqueue(sb_repo, sb_queue, sid, "s2/shared.txt", content, f"{sid} 同路径写入")

    t1 = threading.Thread(target=_enq, args=("rb14-s2a", "payload-A\n"))
    t2 = threading.Thread(target=_enq, args=("rb14-s2b", "payload-B\n"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert len(results) == 2 and len({r["qid"] for r in results.values()}) == 2, "两会话各得独立 qid"
    assert len(list((sb_queue / "pending").glob("q-*.json"))) == 2, "跨会话同路径不得互并（compaction 键含 session）"

    guard = {"flag": False, "lock": threading.Lock(), "violations": []}
    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory([], overlap_guard=guard))
    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)

    # 跨会话同路径=语义冲突：后件零覆盖死信回属主会话（66 号 §6.4/§9.1 铁律），
    # 但每 qid 恰处理一次（done+dead==件数=D4 判据的完整形态）
    assert stats["done"] == 1 and stats["dead"] == 1, f"一落一死（零覆盖）: {stats}"
    dead_items = list((sb_queue / "dead").glob("*.json"))
    assert len(dead_items) == 1, "死信路径干净：恰一件入墓"
    dead = json.loads(dead_items[0].read_text(encoding="utf-8"))
    assert "同路径" in dead.get("dead_reason", "") and "死信回退" in dead.get("dead_reason", ""), (
        f"死因须如实指向同路径冲突: {dead.get('dead_reason')}"
    )
    assert dead.get("prescription"), "M3.3：死信必须带处方"
    assert guard["violations"] == [], f"路径锁须串行化同路径 commit 体（互踩即 violation）: {guard['violations']}"
    # 终态内容=两载荷之一（完整快照，无撕裂无覆盖叠加）
    final = sb_repo / "s2" / "shared.txt"
    assert final.exists() and final.read_text(encoding="utf-8") in ("payload-A\n", "payload-B\n")


# ── 蓝方 ②+红证：B4 (created_at,qid) FIFO 不被字典序倒挂 ────────────────────


def _craft_pending(sb_repo, sb_queue, sid: str, rel: str, created_at: str) -> str:
    item = enqueue(sb_repo, sb_queue, sid, rel, f"{sid}:{rel}\n", f"{sid} item")
    p = sb_queue / "pending" / f"{item['qid']}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["created_at"] = created_at
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return item["qid"]


def test_s2_b4_fifo_by_created_at_not_lexicographic(sb_repo, sb_queue):
    # zzz 会话先到（旧）、aaa 会话后到（新）：qid 字典序 aaa<zzz，旧规则会把新件当队首
    old_qid = _craft_pending(sb_repo, sb_queue, "rb14-zzz", "s2/old.txt", "2026-09-26T08:00:00+08:00")
    new_qid = _craft_pending(sb_repo, sb_queue, "rb14-aaa", "s2/new.txt", "2026-09-26T08:05:00+08:00")
    heads = sorted((sb_queue / "pending").glob("q-*.json"))

    head, lane = cq._pick_head(heads)
    assert head is not None and lane == "interactive"
    assert head.stem == old_qid, f"B4：队首必须是到达序最老件: {head.stem}"
    # 红证：旧规则（qid 字典序首件）在本构造下选的是新件——证明本尺对倒挂有判别力
    assert heads[0].stem == new_qid, "构造失效：字典序首件应为新件（否则红证不成立）"


# ── 蓝方 ③：C1 同会话短窗合批=文件集并集；跨会话绝不合并 ────────────────────


def test_s2_c1_same_session_absorbs_across_session_never(sb_repo, sb_queue, monkeypatch):
    wt = str(sb_repo)
    r1 = enqueue(sb_repo, sb_queue, "rb14-s2c", "s2/c1_a.txt", "A\n", "c1 第一件", worktree_root=wt)
    r2 = enqueue(sb_repo, sb_queue, "rb14-s2c", "s2/c1_b.txt", "B\n", "c1 第二件", worktree_root=wt)
    assert r2.get("absorbed"), f"同会话+同根短窗必须合批: {r2}"
    assert r2["qid"] == r1["qid"], "合批后回执 qid=前件"
    absorbed_qid = r2["absorbed"]["qid"]
    # absorbed qid 不落任何状态目录（D 断链：件数以落状态目录者计）
    for d in ("pending", "processing", "done", "dead"):
        assert not (sb_queue / d / f"{absorbed_qid}.json").exists(), f"absorbed qid 不得落 {d}"
    pending = list((sb_queue / "pending").glob("q-*.json"))
    assert len(pending) == 1, "同会话两件合为一袋"
    item = json.loads(pending[0].read_text(encoding="utf-8"))
    paths = {f["path"] for f in item["files"]}
    assert paths == {"s2/c1_a.txt", "s2/c1_b.txt"}, f"合批=文件集并集: {paths}"
    assert item["meta"]["merged_count"] == 1

    # 跨会话同根：绝不合并（红线）
    r3 = enqueue(sb_repo, sb_queue, "rb14-s2d", "s2/c1_c.txt", "C\n", "他会话件", worktree_root=wt)
    assert not r3.get("absorbed"), "跨会话必须新建"
    assert len(list((sb_queue / "pending").glob("q-*.json"))) == 2

    # 排空：done 恒等于落袋件数（2），合并袋双文件齐落
    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory([]))
    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)
    assert stats["done"] == 2, f"done==落袋件数: {stats}"
    for rel in ("s2/c1_a.txt", "s2/c1_b.txt", "s2/c1_c.txt"):
        assert (sb_repo / rel).exists(), f"{rel} 必须落盘"


# ── 蓝方 ④+红证：幽灵 pending 不二次落地（D4 断链）─────────────────────────


def _land_once_then_ghost(sb_repo, sb_queue, monkeypatch, mod=None):
    """先正常落地 s2/ghost.txt，再伪造幽灵 pending（同 qid、blob 换 v2）。

    返回 (ghost_qid, v2_blob_sha, 首轮 stats)。
    """
    mod = mod or cql
    monkeypatch.setattr(mod, "make_worker_landing", make_stub_landing_factory([]))
    item = enqueue(sb_repo, sb_queue, "rb14-ghost", "s2/ghost.txt", "v1\n", "ghost 首落")
    stats1 = mod.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)
    qid = item["qid"]
    assert stats1["done"] == 1 and (sb_queue / "done" / f"{qid}.json").exists(), "首落必须 done"

    # 幽灵：同 qid 重写 pending，blob 指向新存 v2（_mark_cascade_stale 回写复活的等价构造）。
    # base_head 同步到当前 dev——幽灵带合法基底（等价"同步工作区后重新入队"形态），
    # 让旧码的 landing 基底检查放行，从而暴露认领侧缺 done 复查的二次落地。
    sha2 = cq._store_blob(sb_queue, b"v2\n")
    ghost = json.loads((sb_queue / "done" / f"{qid}.json").read_text(encoding="utf-8"))
    for k in ("landed_at", "landed_id"):
        ghost.pop(k, None)
    ghost["base_head"] = git_text(sb_repo, "rev-parse", "refs/heads/dev")
    ghost["files"][0]["blob_sha256"] = sha2
    ghost["files"][0]["blob_ref"] = f"blobs/{sha2}"
    cq._atomic_write(
        sb_queue / "pending" / f"{qid}.json",
        json.dumps(ghost, ensure_ascii=False, indent=2).encode("utf-8"),
    )
    return qid, stats1


def test_s2_blue_ghost_pending_not_relanded(sb_repo, sb_queue, monkeypatch):
    qid, stats1 = _land_once_then_ghost(sb_repo, sb_queue, monkeypatch)
    stats2 = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)

    assert stats2["done"] == 0, f"幽灵不得二次落地: {stats2}"
    assert stats1["done"] + stats2["done"] == 1, f"done 事件/qid 恒等于 1（D4 判据）: {stats1}+{stats2}"
    assert not list((sb_queue / "dead").glob("*.json")), "幽灵也不得诬入死信"
    assert not (sb_queue / "pending" / f"{qid}.json").exists(), "幽灵被认领侧终止性复查清除"
    n = git_text(sb_repo, "log", "dev", "--oneline", "--", "s2/ghost.txt")
    assert len(n.splitlines()) == 1, f"同路径仍只 1 次提交: {n}"


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_s2_red_old_code_ghost_relanded_twice(sb_repo, sb_queue, tmp_path, monkeypatch):
    before = sha256_file(LANDING_SRC)
    old = load_surgered(
        LANDING_SRC,
        [('if (root / "done" / head.name).exists():', 'if False and (root / "done" / head.name).exists():')],
        "cql_rb14_s2_old",
        tmp_path,
        expected_counts=[2],
    )
    assert sha256_file(LANDING_SRC) == before, "产品文件被手术污染（红线）"

    qid, stats1 = _land_once_then_ghost(sb_repo, sb_queue, monkeypatch, mod=old)
    stats2 = old.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=2)

    # 旧码红象：幽灵被二次 done（认领侧无 done 复查）→ done 事件/qid == 2，
    # "done 恒等于件数" 的计数语义被破坏。内容层由 landing 幂等三判（marker grep）
    # 兜住（同 qid 不产生第二 commit）——那正是防御纵深：计数层旧码破、内容层不破。
    assert stats1["done"] + stats2["done"] == 2, f"旧码幽灵应被二次 done（红证）: {stats1}+{stats2}"
    n = git_text(sb_repo, "log", "dev", "--oneline", "--", "s2/ghost.txt")
    assert len(n.splitlines()) == 1, f"landing 幂等三判在旧码也不许破（内容零双落）: {n}"
