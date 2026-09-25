# [A_test] module_id: MOD-GOV_commit_queue_snapshot_selfconsistency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_commit_queue_snapshot_selfconsistency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_snapshot_selfconsistency.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev）；
#              被检对象（入队/判定/合并/requeue）一律真函数直调，禁 mock；
#              每条攻击尺配阴性控制组（他会话漂移仍拦=原行为保持；正常并行不误杀）
# [MODIFY-GUARD] H 队快照自洽见证层回归闸（st-ff-snapself-20260926）：摘除
#                assert_snapshot_selfconsistent / _witness_stale_carry / from-bag 原袋基底 /
#                合并器携带不复活闸 任一接线即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""快照自洽见证层永久尺（H 队，2026-09-26）——F 队案卷三条打穿通道的复现固化。

案卷真源=F 队红队复现案卷 lane_stale_channel_repro（2026-09-26，chain_fullflow_20260926
战役，由该案卷所属车道另行落地；本尺按其所载三条打穿通道钉死）。
结构病根（案卷 ATK-3 判据级发现）：既有四机制（逐文件快进/基底重校验/注册表合并器/
同会话豁免）的判据集=「dev 移动 × 袋路径集」，**没有任何一层比「袋字节 × 袋自身基底
树」**——R1/ATK-2 的吃字节皆为其特化。本文件把三条 tmp 复现钉成永久 pytest 尺：

  H1（ATK-3 形态，生产可达）：同会话盲区——袋内"未动路径"字节恰等其自身基底
      （纯陈旧携带），dev 上该路径已被**本会话自己**前袋推进（快进判定被同会话豁免
      短路），落地即用旧字节回退在册内容。修前红=回退成功；修后绿=见证剥除该路径
      （部分命中）或整袋死信点名（全部命中），在册字节保住。
  H2（ATK-2）：requeue --from-bag 把 base 填成"重投时刻的 dev 尖"，旧袋字节以
      「本包改动」身份绕过全部判定吃非注册表热件。修前红=base==tip 且字节被吃；
      修后绿=base 取原袋基底、陈旧覆盖在快进判定现红。
  H3（ATK-1）：注册表条目级三向合并把他人已落地的删除复活（加侧无闸）。修前红=
      E7 复活；修后绿=theirs 条目与其基底逐字节同＝陈旧携带不采纳；theirs 真改过
      该条目仍按 W2 采纳恢复（合并语义不回归）。

活性护栏尺（L 组）钉死"判据收紧到 stale-path 级"的口径：正常并行（同会话连投、
多文件正常改+一枚安全携带）零误杀；整袋拒（等值即杀）会误杀的形态单独计数上报。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CAT = "docs/01_policies_and_standards/_registry/catalogs"
FAMILY_REL = f"{CAT}/family_probe.yaml"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cq():
    return _load("_cq_snapself", "scripts/commit_queue.py")


@pytest.fixture(scope="module")
def cql():
    return _load("_cql_snapself", "scripts/governance/commit_queue_landing.py")


def _git(cwd: Path, *args: str, binary: bool = False):
    r = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=not binary,
        encoding=None if binary else "utf-8",
        errors="replace",
        timeout=180,
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {(r.stderr if not binary else r.stderr[:300])}"
    return r.stdout if binary else r.stdout.strip()


def _show(cwd: Path, rev: str, rel: str) -> bytes | None:
    r = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=str(cwd), capture_output=True, timeout=180)
    return r.stdout if r.returncode == 0 else None


def _write(root: Path, rel: str, body: bytes) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(body)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """tmp 真 git 仓（dev 分支）——零生产写入，口径同 test_commit_queue_base_head.repo。"""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "dev")
    _git(r, "config", "user.email", "snapself@local")
    _git(r, "config", "user.name", "snapself")
    _git(r, "config", "core.autocrlf", "false")
    return r


def _commit(repo: Path, rel: str, body: bytes, msg: str) -> str:
    _write(repo, rel, body)
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-qm", msg)
    return _git(repo, "rev-parse", "HEAD")


def _wt_at(repo: Path, dest: Path, sha: str) -> Path:
    _git(repo, "worktree", "add", "--detach", str(dest), sha)
    return dest


def _enqueue(cq, cql, wt: Path, qroot: Path, sid: str, msg: str, rels: list[str]) -> dict:
    """从工作区盘字节真入袋（基底=快照真源，与生产 git_commit --enqueue 同源接线）。"""
    files = [(rel, (wt / rel).read_bytes()) for rel in rels]
    base = cql.resolve_base_head(wt)
    blobs = cql.resolve_base_blobs(wt, base, rels)
    return cq.enqueue_item(
        sid,
        msg,
        files,
        queue_root=str(qroot),
        options=cq.EnqueueOptions(base_head=base, base_blobs=blobs),
    )


def _land(cql, cq_mod, repo: Path, qroot: Path, tmp_path: Path, item: dict, n: int):
    """走生产判定链的最小落地：_conflict_reason → 见证 → _apply_snapshot → 带
    [GW:sid:qid] 标记提交 + update-ref dev（模拟 serializer 推进 dev）。被检对象
    全部真函数；绕过的只有门禁链（案卷边界声明同口径——量的是判据与快照语义）。
    返回 ('conflict', reason) / ('dead', reason) / ('landed', sha) / ('noop', tip)。
    """
    tip = _git(repo, "rev-parse", "refs/heads/dev")
    wt = tmp_path / f"landwt{n}"
    _wt_at(repo, wt, tip)
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=wt)
    reason = landing._conflict_reason(item, tip)
    if reason:
        return "conflict", reason
    witness = getattr(landing, "_witness_stale_carry", None)
    if witness is not None:  # 修前缺席（行为红由字节断言呈现，不由 AttributeError 呈现）
        verdict = witness(item, Path(qroot), tip)
        if verdict is not None and not verdict.ok:
            return "dead", verdict.reason
    applied = landing._apply_snapshot(item, Path(qroot), tip)
    if not applied:
        return "noop", tip
    rels = [str(Path(p).relative_to(wt)).replace("\\", "/") for p in applied]
    _git(wt, "add", "--", *rels)
    _git(wt, "commit", "-qm", f"[GW:{item['session_id']}:{item['qid']}] {item['message']}")
    new = _git(wt, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/heads/dev", new, tip)
    return "landed", new


def _family(entries: list[tuple[str, str]]) -> bytes:
    body = "".join(f"  - id: {e}\n    name: {n}\n" for e, n in entries)
    return f"total_entries: {len(entries)}\nentries:\n{body}".encode()


# ===========================================================================
# H1（ATK-3 形态）：同会话盲区里的纯陈旧携带——修前回退在册，修后 stale-path 级剥除
# ===========================================================================


def test_h1_stale_carry_in_same_session_blind_spot(cq, cql, repo: Path, tmp_path: Path) -> None:
    base = _commit(repo, "hot.yaml", b"value: v0\n", "seed hot")
    base = _commit(repo, "notes.txt", b"n0\n", "seed notes")
    qroot = tmp_path / "q-h1"
    wt_old = _wt_at(repo, tmp_path / "wt_old", base)

    # 前件①：本会话（laneSelf）先合法落地 hot v0->v1（带 [GW] 标记，serializer 形态）
    _write(wt_old, "hot.yaml", b"value: v1\n")
    bag1 = _enqueue(cq, cql, wt_old, qroot, "laneSelf", "bag1 hot v1", ["hot.yaml"])
    kind1, _ = _land(cql, cq, repo, qroot, tmp_path, bag1, 1)
    assert kind1 == "landed"
    tip1 = _git(repo, "rev-parse", "refs/heads/dev")
    assert _show(repo, tip1, "hot.yaml") == b"value: v1\n"

    # 前件②：工作区停在 base 未同步（并行常态）；盘上 hot 停留旧字节 v0（外部回退/
    # 未收敛形态），notes 是真改动。袋=真改 notes + 陈旧携带 hot。
    _write(wt_old, "hot.yaml", b"value: v0\n")
    _write(wt_old, "notes.txt", b"n1 own edit\n")
    bag2 = _enqueue(cq, cql, wt_old, qroot, "laneSelf", "bag2 mixed", ["notes.txt", "hot.yaml"])
    assert bag2["base_head"] == base
    bag2_asis = json.loads(json.dumps(bag2))  # _land 就地剥除，见证读数用落地前副本

    # 行为级（主案）：修前此袋会把 dev hot 回退成 v0（同会话豁免短路了快进判定）；
    # 修后：hot 剥除不落地、notes 正常落地，在册 v1 保住。
    kind2, _ = _land(cql, cq, repo, qroot, tmp_path, bag2, 2)
    assert kind2 in ("landed", "noop")
    tip2 = _git(repo, "rev-parse", "refs/heads/dev")
    assert _show(repo, tip2, "notes.txt") == b"n1 own edit\n", "真实改动不得被连坐"
    assert _show(repo, tip2, "hot.yaml") == b"value: v1\n", (
        "ATK-3 复发：袋字节恰等其自身基底的陈旧携带路径回退了 dev 在册内容"
    )

    # 见证函数级读数（修前缺席即红——本尺的存在性半段；用落地前副本，_land 会就地剥除）
    fn = getattr(cql, "assert_snapshot_selfconsistent", None)
    assert fn is not None, "assert_snapshot_selfconsistent 未装配（H 队见证层缺失）"
    dangerous, safe = fn(bag2_asis, queue_root=qroot, repo_root=repo, current_dev=tip1)
    assert dangerous == ["hot.yaml"], f"陈旧携带路径必须被点名，实得 dangerous={dangerous} safe={safe}"
    assert safe == []

    # 阴性控制①（原行为保持）：漂移若出自**他会话**，既有快进判定仍须判红（见证不接管）
    _commit(repo, "hot.yaml", b"value: v2 by other\n", "foreign landing [GW:other-sid:q-x]")
    tip_other = _git(repo, "rev-parse", "refs/heads/dev")
    bag3 = _enqueue(cq, cql, wt_old, qroot, "laneSelf", "bag3 after foreign", ["notes.txt", "hot.yaml"])
    probe = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "w")
    assert "快进判定失败" in str(probe._conflict_reason(bag3, tip_other)), "他会话漂移仍拦=原行为保持"


def test_h1_whole_bag_stale_is_dead_letter_named(cq, cql, repo: Path, tmp_path: Path) -> None:
    """全袋皆陈旧危险携带 ⇒ 拒落、死信回属主，message 点名路径与"这不是你的改动"。"""
    base = _commit(repo, "hot.yaml", b"value: v0\n", "seed")
    qroot = tmp_path / "q-h1d"
    wt_old = _wt_at(repo, tmp_path / "wt_d", base)
    _write(wt_old, "hot.yaml", b"value: v1\n")
    bag1 = _enqueue(cq, cql, wt_old, qroot, "laneOwn", "own bag1", ["hot.yaml"])
    assert _land(cql, cq, repo, qroot, tmp_path, bag1, 11)[0] == "landed"
    _write(wt_old, "hot.yaml", b"value: v0\n")
    bag2 = _enqueue(cq, cql, wt_old, qroot, "laneOwn", "bag2 pure carry", ["hot.yaml"])
    tip = _git(repo, "rev-parse", "refs/heads/dev")
    assert getattr(cql.WorktreeLanding, "_witness_stale_carry", None) is not None, "_witness_stale_carry 未装配"
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "wt_x")
    verdict = landing._witness_stale_carry(bag2, qroot, tip)
    assert verdict is not None and not verdict.ok, "整袋陈旧携带必须拒落"
    assert "hot.yaml" in verdict.reason and "这不是你的改动" in verdict.reason
    # 死因须按 item 性分类并带可行动处方（新增死因族三处补齐之"测试"处）
    assert cq.classify_dead_reason(verdict.reason) == "item"
    assert "同步" in cq.dead_letter_prescription(verdict.reason)
    # 阴性控制：dev 回指到袋基底（携带路径无人动过，写=noop）⇒ 不得拒落
    assert landing._witness_stale_carry(json.loads(json.dumps(bag2)), qroot, base) is None, (
        "安全携带（袋==基底==dev）拒落＝整袋误杀形态回归"
    )


# ===========================================================================
# H2（ATK-2）：requeue --from-bag 必须取原袋基底，不得取重投时刻的 dev 尖
# ===========================================================================


def _bake_dead(qroot: Path, item: dict, reason: str) -> None:
    """把 pending 项搬进 dead/（复现夹具：死亡是前情，被检对象是 requeue 的基底重算）。"""
    (qroot / "dead").mkdir(exist_ok=True)
    meta = json.loads((qroot / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
    meta["dead_reason"] = reason
    (qroot / "dead" / f"{item['qid']}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (qroot / "pending" / f"{item['qid']}.json").unlink()


def test_h2_from_bag_requeue_keeps_original_base(cq, cql, repo: Path, tmp_path: Path) -> None:
    c0 = _commit(repo, "hot.yaml", b"value: v0\n", "C0")
    qroot = tmp_path / "q-h2"
    wt0 = _wt_at(repo, tmp_path / "wt_h2", c0)
    # 属主会话在 C0 上做的活：hot v0->vA，随后该袋死亡（模拟门禁死因）
    _write(wt0, "hot.yaml", b"value: vA\n")
    bag = _enqueue(cq, cql, wt0, qroot, "laneQ", "stale bag vA", ["hot.yaml"])
    _bake_dead(qroot, bag, "模拟死亡：门禁拦截")
    # 他人合法把 hot 推进到 vB
    _commit(repo, "hot.yaml", b"value: vB\n", "foreign landing [GW:laneR:q-r1]")
    tip = _git(repo, "rev-parse", "refs/heads/dev")

    new = cq.requeue_dead_item(str(bag["qid"]), queue_root=str(qroot), worktree_root=str(repo), from_bag=True)
    nb = new["item"]
    # 主案：基底=原袋基底（内容真源），不得=重投时刻 dev 尖
    assert nb["base_head"] == c0, (
        f"ATK-2 复发：--from-bag 重投把 base 填成当下 dev 尖 {tip[:10]}（袋字节比声称基底更旧）"
    )
    ent = nb["files"][0]
    assert ent["base_blob"] == _git(repo, "rev-parse", f"{c0}:hot.yaml"), "base_blob 必须随基底重算"
    assert ent["blob_sha256"] == bag["files"][0]["blob_sha256"], "内容仍取原袋（from-bag 语义不变）"

    # 行为级：陈旧覆盖在快进判定现红（修前：base==tip ⇒ 判据失明 ⇒ vB 被 vA 吃掉）
    verdict = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "wt_l2")._conflict_reason(
        nb, tip
    )
    assert verdict is not None and "快进判定失败" in verdict, f"from-bag 重投袋必须判红，实得 {verdict!r}"

    # 阴性控制：默认（工作区重建）重投口径不变——基底仍=重建工作区自己的 HEAD
    _write(repo, "hot.yaml", b"value: vC owner reworked\n")
    _git(repo, "add", "--", "hot.yaml")
    _git(repo, "commit", "-qm", "[GW:laneQ] sync to dev first")
    tip2 = _git(repo, "rev-parse", "refs/heads/dev")
    _bake_dead(qroot, nb, "模拟死亡二：快进判定失败")
    new2 = cq.requeue_dead_item(str(nb["qid"]), queue_root=str(qroot), worktree_root=str(repo), from_bag=False)
    assert new2["item"]["base_head"] == tip2, "非 from-bag 重投=工作区真源，口径零变更"


# ===========================================================================
# H3（ATK-1）：注册表合并器加侧闸——陈旧携带条目不得复活他人已落地的删除
# ===========================================================================


def test_h3_registry_carry_does_not_resurrect_deleted_entry(cq, cql, repo: Path, tmp_path: Path) -> None:
    fam0 = _family([("E1", "one"), ("E2", "two"), ("E7", "seven")])
    c0 = _commit(repo, FAMILY_REL, fam0, "基底三条目")
    _commit(repo, FAMILY_REL, _family([("E1", "one"), ("E2", "two")]), "dev 直提退役 E7 [allow-mass-deletion:single]")
    tip = _git(repo, "rev-parse", "refs/heads/dev")
    assert b"E7" not in (_show(repo, tip, FAMILY_REL) or b"")
    blob_c0 = _git(repo, "rev-parse", f"{c0}:{FAMILY_REL}")

    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "q-h3", worktree_path=tmp_path / "w3")
    # 主案（修前红）：旧基底袋（theirs==base 逐字节同＝纯携带）重投 ⇒ E7 复活
    item = {
        "qid": "q-carry",
        "session_id": "laneZ",
        "base_head": c0,
        "files": [{"path": FAMILY_REL, "base_blob": blob_c0}],
    }
    out = landing._merge_registry_file(item, FAMILY_REL, fam0, tip)
    assert out is None or b"E7" not in out, "ATK-1 复发：陈旧携带（袋条目恰等其基底）复活了 dev 已落地的删除"

    # 合并语义不回归控制①：theirs **真改过**该条目（编辑=反向意图）⇒ 维持 W2 采纳恢复
    fam_edit = _family([("E1", "one"), ("E2", "two"), ("E7", "seven-restored")])
    out2 = landing._merge_registry_file(item, FAMILY_REL, fam_edit, tip)
    assert out2 is not None and b"seven-restored" in out2, "theirs 确实编辑过的条目仍按 W2 采纳（不得一刀切）"

    # 控制②：常规新增条目（base 无）不受加侧闸影响
    fam_add = _family([("E1", "one"), ("E2", "two"), ("E9", "brand-new")])
    out3 = landing._merge_registry_file(item, FAMILY_REL, fam_add, tip)
    assert out3 is not None and b"E9" in out3 and b"E7" not in out3

    # 控制③：dev 未删除时，携带条目原样共存（不误删在册）
    _commit(repo, "docs/other.md", b"x\n", "unrelated dev move")
    tip2 = _git(repo, "rev-parse", "refs/heads/dev")
    item_keep = {
        "qid": "q-carry2",
        "session_id": "laneZ",
        "base_head": tip,
        "files": [{"path": FAMILY_REL, "base_blob": _git(repo, "rev-parse", f"{tip}:{FAMILY_REL}")}],
    }
    out4 = landing._merge_registry_file(item_keep, FAMILY_REL, _family([("E1", "one"), ("E2", "two")]), tip2)
    assert out4 is None, "dev 现状==袋携带 ⇒ noop 跳过（既有语义零变更）"


# ===========================================================================
# L 组（活性护栏）：正常并行零误杀——stale-path 级收紧口径钉死
# ===========================================================================


def test_liveness_two_same_session_bags_not_killed(cq, cql, repo: Path, tmp_path: Path) -> None:
    """形态(a) 同会话连投两袋，第二袋携带第一袋已落内容 ⇒ 必落、零误杀。"""
    base = _commit(repo, "hot.yaml", b"v0\n", "seed")
    qroot = tmp_path / "q-la"
    wt = _wt_at(repo, tmp_path / "wt_la", base)
    _write(wt, "hot.yaml", b"v1\n")
    bag1 = _enqueue(cq, cql, wt, qroot, "laneL", "bag1", ["hot.yaml"])
    assert _land(cql, cq, repo, qroot, tmp_path, bag1, 21)[0] == "landed"
    # 工作区同步后连投：hot 已是"携带且 dev==袋"（安全携带）+ 新文件真改动
    _git(wt, "checkout", "-f", "--detach", _git(repo, "rev-parse", "refs/heads/dev"))
    _write(wt, "new.md", b"brand new content\n")
    bag2 = _enqueue(cq, cql, wt, qroot, "laneL", "bag2", ["new.md", "hot.yaml"])
    dangerous, safe = cql.assert_snapshot_selfconsistent(
        bag2,
        queue_root=qroot,
        repo_root=repo,
        current_dev=_git(repo, "rev-parse", "refs/heads/dev"),
    )
    assert dangerous == [] and safe == ["hot.yaml"], (
        "安全携带（袋==基底==dev，写=noop）不得进拒落名单——等值即杀＝整袋拒形态误杀"
    )
    assert _land(cql, cq, repo, qroot, tmp_path, bag2, 22)[0] == "landed"
    tip = _git(repo, "rev-parse", "refs/heads/dev")
    assert _show(repo, tip, "new.md") == b"brand new content\n"
    assert _show(repo, tip, "hot.yaml") == b"v1\n"


def test_liveness_multi_file_normal_change_one_carry(cq, cql, repo: Path, tmp_path: Path) -> None:
    """形态(b) 正常改多文件、其中一个是陈旧携带 ⇒ 只剥 stale 路径，其余全落。"""
    base = _commit(repo, "a.md", b"a0\n", "seed a")
    _commit(repo, "b.md", b"b0\n", "seed b")
    _commit(repo, "stale.md", b"s0\n", "seed stale")
    qroot = tmp_path / "q-lb"
    wt = _wt_at(repo, tmp_path / "wt_lb", base)
    _git(wt, "checkout", "--detach", _git(repo, "rev-parse", "refs/heads/dev"))
    # 本会话先合法落 stale s0->s1（制造"dev 已推进且是自家推进"的盲区前件）
    _write(wt, "stale.md", b"s1\n")
    bag1 = _enqueue(cq, cql, wt, qroot, "laneL2", "own prior", ["stale.md"])
    assert _land(cql, cq, repo, qroot, tmp_path, bag1, 31)[0] == "landed"
    # 工作区停在已同步点，外部进程把盘上 stale.md 回退成 s0（ATK-3 盘陈旧到达形态），
    # 会话本人不知情，正常改 a/b 并把 stale.md 一并列入 --files
    _write(wt, "stale.md", b"s0\n")
    _write(wt, "a.md", b"a2 own edit\n")
    _write(wt, "b.md", b"b2 own edit\n")
    bag2 = _enqueue(cq, cql, wt, qroot, "laneL2", "normal work + one carry", ["a.md", "b.md", "stale.md"])
    tip = _git(repo, "rev-parse", "refs/heads/dev")
    dangerous, safe = cql.assert_snapshot_selfconsistent(bag2, queue_root=qroot, repo_root=repo, current_dev=tip)
    assert dangerous == ["stale.md"] and safe == []
    assert _land(cql, cq, repo, qroot, tmp_path, bag2, 32)[0] == "landed", "部分命中不得整袋死"
    tip2 = _git(repo, "rev-parse", "refs/heads/dev")
    assert _show(repo, tip2, "a.md") == b"a2 own edit\n"
    assert _show(repo, tip2, "b.md") == b"b2 own edit\n"
    assert _show(repo, tip2, "stale.md") == b"s1\n", "陈旧携带路径必须被剥除而非落袋"


def test_landing_pipeline_wiring_guards() -> None:
    """接线守卫（grep 形态，先例=test_maindoor_enqueue_channel_passes_base）：
    见证缺席 __call__ 主链＝静默回退旧判据集，行为尺未必能及时发现，钉死源码接线。"""
    src = (REPO_ROOT / "scripts" / "governance" / "commit_queue_landing.py").read_text(encoding="utf-8")
    call_body = src.split("def __call__", 1)[1].split("def _pool_cas_replay", 1)[0]
    assert "_witness_stale_carry(" in call_body, "__call__ 主链未接快照自洽见证＝ATK-3 复发面"
    assert "def assert_snapshot_selfconsistent" in src
    ins = src.split("def _plan_insert_splices", 1)[1].split("def _render_selfcheck", 1)[0]
    assert "base_idx[key][2].data == t_block.data" in ins, "合并器加侧携带闸被摘＝ATK-1 复发面"
    rq = (REPO_ROOT / "scripts" / "commit_queue.py").read_text(encoding="utf-8")
    body = rq.split("def requeue_dead_item", 1)[1].split("def cleanup_done", 1)[0]
    assert 'old_item.get("base_head")' in body, "--from-bag 不再取原袋基底＝ATK-2 复发面"
