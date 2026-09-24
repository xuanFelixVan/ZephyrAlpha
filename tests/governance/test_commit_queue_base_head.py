# [A_test] module_id: MOD-GOV_commit_queue_base_head | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_commit_queue_base_head
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_base_head.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev）；
#              每条尺须既能红又能绿（阳性=构造漂移必报，阴性=基底对齐必不报），恒绿尺不得进本文件
# [MODIFY-GUARD] F-AUDIT-QUEUE-04 治本回归闸：摘掉 base_head/base_blobs 接线或恢复 old_dev^ 兜底即红
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""F-AUDIT-QUEUE-04 回归尺：提交正门入袋必记基底，缺基底不得猜。

案卷真源=docs/_working/audit_all/LEDGER.md 第 9 轮 ⑥（尺T/尺U 各三控制组实证）。
病灶两面：
  ① 交互正门 git_commit.py 的 enqueue 通道不传 base_head ⇒ 生产袋全量 base_head=None
     ⇒ _conflict_reason 在 `if not base` 处早退 ⇒ 后落地快照可整覆盖任意文件；
  ② base_blob 全仓无填充点 ⇒ §6.4 陈旧基底重校验恒 continue＝结构空转；且缺 base 时
     _merge_registry_file 兜底 old_dev^，把"陈旧快照不含"读成"theirs 主动删除"。

本文件把审计班的一次性探针（尺T/尺U 在 .runtime/tmp，随清理消失）固化为永久 pytest。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REG_REL = "docs/01_policies_and_standards/_registry/catalogs/probe_registry.yaml"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cq():
    return _load("_cq_basehead", "scripts/commit_queue.py")


@pytest.fixture(scope="module")
def cql():
    return _load("_cql_basehead", "scripts/governance/commit_queue_landing.py")


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120
    )
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.stderr[:300]}"
    return r.stdout.strip()


def _book(entries: list[str]) -> str:
    body = "".join(f"  - gate_id: {e}\n    note: probe-{e}\n" for e in entries)
    return f"total_gates: {len(entries)}\ngates:\n{body}"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """tmp 真 git 仓（dev 分支）——零生产写入，口径同 test_commit_queue_landing.tmp_repo。"""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "dev")
    _git(r, "config", "user.email", "probe@local")
    _git(r, "config", "user.name", "probe")
    _git(r, "config", "core.autocrlf", "false")
    return r


def _commit(repo: Path, path: str, text: str, msg: str) -> str:
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    _git(repo, "add", "--", path)
    _git(repo, "commit", "-qm", msg)
    return _git(repo, "rev-parse", "HEAD")


def _item(cq, repo: Path, qroot: Path, path: str, body: bytes) -> dict:
    """以当前 dev 为基底入一袋（不落盘，只取回队列项）。"""
    base = _git(repo, "rev-parse", "refs/heads/dev")
    return cq.enqueue_item(
        "probe-conflict",
        "probe snapshot",
        [(path, body)],
        queue_root=str(qroot),
        options=cq.EnqueueOptions(base_head=base),
    )


# ---------------------------------------------------------------------------
# ① resolve_base_head / resolve_base_blobs 契约（含真·非仓库阴性控制组）
# ---------------------------------------------------------------------------


def test_resolve_base_head_and_blobs_contract(cql, repo: Path) -> None:
    head = _commit(repo, "docs/a.md", "v1\n", "seed")
    assert cql.resolve_base_head(repo) == head
    blobs = cql.resolve_base_blobs(repo, head, ["docs/a.md", "docs/new.md"])
    # 与 _pool_head_reader 同 id 空间（三套哈希口径不可互换——此处必须是 git blob sha）
    assert blobs["docs/a.md"] == _git(repo, "rev-parse", f"{head}:docs/a.md")
    assert blobs["docs/new.md"] is None  # 基底不存在＝新增件，不猜

    # 阴性控制组：真·非 git 目录 → None（tmp 隔离测试口径未被破坏，入队仍可用）。
    # 刻意不用 pytest tmp_path——它落在仓内（.runtime/tmp/pytest_*），git 向上穿透会
    # 命中外层仓的 refs/heads/dev，拿它做"非仓库"阴性对照是假阴性（本尺自纠实证）。
    with tempfile.TemporaryDirectory(prefix="not_a_repo_") as bare:
        assert cql.resolve_base_head(Path(bare)) is None
        assert cql.resolve_base_blobs(Path(bare), None, ["x"]) == {"x": None}


def test_resolve_base_blobs_chunks_large_path_list(cql, repo: Path) -> None:
    """分块控制组：>50 路径（Windows 命令行长度上限）仍逐块解析，一块不丢。"""
    paths = [f"docs/f{i:03d}.md" for i in range(120)]
    for p in paths:
        _commit(repo, p, f"body {p}\n", f"seed {p}")
    head = _git(repo, "rev-parse", "HEAD")
    blobs = cql.resolve_base_blobs(repo, head, paths)
    assert len(blobs) == 120
    assert all(blobs[p] == _git(repo, "rev-parse", f"{head}:{p}") for p in paths[:5])
    assert sum(1 for v in blobs.values() if v) == 120


# ---------------------------------------------------------------------------
# ② 裸 CLI enqueue 自取基底（正门与 CLI 两套入口同口径）
# ---------------------------------------------------------------------------


def test_cli_enqueue_records_base_head_and_blob(cq, repo: Path, tmp_path: Path) -> None:
    head = _commit(repo, "docs/x.md", "one\n", "seed")
    qr = tmp_path / "queue"
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "commit_queue.py"),
            "--queue-root",
            str(qr),
            "enqueue",
            "--worktree-root",
            str(repo),
            "--session",
            "probe-base",
            "--files",
            "docs/x.md",
            "--message",
            "probe",
            "--no-bootstrap",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    assert r.returncode == 0, r.stdout[-400:] + r.stderr[-400:]
    item = json.loads(next(qr.glob("pending/*.json")).read_text(encoding="utf-8"))
    assert item["base_head"] == head, "CLI 入袋必须自取基底（QUEUE-04 前恒 None）"
    entry = item["files"][0]
    assert entry["base_blob"] == _git(repo, "rev-parse", f"{head}:docs/x.md")
    # 填了 base_blob ⇒ §6.4 重校验从此可达（尺T 证明的"结构空转"面关闭）
    ok, mism = cq._revalidate_stale_base(item, lambda p: entry["base_blob"])
    assert ok and mism == []


# ---------------------------------------------------------------------------
# ③ 正门接线守卫（审计判据 grep 的永久化）
# ---------------------------------------------------------------------------


def test_maindoor_enqueue_channel_passes_base(cq) -> None:
    src = (REPO_ROOT / "scripts" / "git_commit.py").read_text(encoding="utf-8")
    assert "resolve_base_head(" in src and "base_head=base_head" in src, (
        "git_commit.py 的 enqueue 通道不再传基底＝QUEUE-04 复发（任意文件可被整覆盖）"
    )
    assert "base_blobs=base_blobs" in src, "base_blob 填充点被摘除＝§6.4 重校验退回空转"


# ---------------------------------------------------------------------------
# ④ 红测主案：A 入队（基底 X）→ B 先落地（HEAD 变 Y）→ A 落地必检出漂移
# ---------------------------------------------------------------------------


def test_stale_snapshot_conflict_detected_when_base_drifts(cq, cql, repo: Path, tmp_path: Path) -> None:
    """用户口径红测：A 入队（基底 X）→ B 先落地（HEAD 变 Y）→ A 必检出基底漂移。"""
    _commit(repo, "docs/notes.md", "v1 owner draft\n", "seed")
    base_x = _git(repo, "rev-parse", "refs/heads/dev")
    qroot = tmp_path / "queue"
    item = _item(cq, repo, qroot, "docs/notes.md", b"v2 bag snapshot\n")
    assert item["base_head"] == base_x
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "wt")

    # 阴性控制①：dev 推进但未触及同路径 ⇒ 快进放行（防过度拦，证明非"见推进即红"）
    unrelated = _commit(repo, "docs/other.md", "unrelated\n", "unrelated path moved")
    assert landing._conflict_reason(item, unrelated) is None

    # 阳性（主案）：B 先落地触及同路径 ⇒ 必须拦，而不是整文件覆盖 B 已落地内容
    head_y = _commit(repo, "docs/notes.md", "v3 other package content\n", "same path landed")
    reason = landing._conflict_reason(item, head_y)
    assert isinstance(reason, str) and "快进判定失败" in reason, (
        f"陈旧快照未被拦（={reason!r}）＝QUEUE-04 复发，A 会整覆盖 B 的已落地内容"
    )

    # 阴性控制②：基底对齐不得报（证明上一条的红不是恒红）
    assert landing._conflict_reason(item, base_x) is None


# ---------------------------------------------------------------------------
# ⑤ 注册表合并：记了基底按记的来；没记基底死信，绝不兜底 old_dev^
# ---------------------------------------------------------------------------


def test_registry_merge_uses_recorded_base_not_guessed_parent(cq, cql, repo: Path, tmp_path: Path) -> None:
    c0 = _commit(repo, REG_REL, _book(["A"]), "C0 true base")
    _commit(repo, REG_REL, _book(["A", "B"]), "C1 other adds B")
    old_dev = _commit(repo, REG_REL, _book(["A", "B", "C"]), "C2 other adds C")
    theirs = _book(["A", "D"]).encode("utf-8")  # 陈旧快照：C0 上开工，不含 B/C

    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue", worktree_path=tmp_path / "wt")
    item_true_base = {"qid": "q-probe", "base_head": c0, "files": [{"path": REG_REL}]}
    text = landing._merge_registry_file(item_true_base, REG_REL, theirs, old_dev).decode("utf-8")
    assert "gate_id: B" in text and "gate_id: C" in text, "记了真基底后他人条目必存活"
    assert "gate_id: D" in text, "本会话新增条目必落"

    # 反证（尺非恒绿）：无基底项必须死信，而不是兜底 old_dev^ 把 B 判成"被 theirs 删除"
    item_no_base = {"qid": "q-probe-2", "base_head": None, "files": [{"path": REG_REL, "base_blob": None}]}
    with pytest.raises(RuntimeError, match="拒绝以"):
        landing._merge_registry_file(item_no_base, REG_REL, theirs, old_dev)

    # 旁路修复面：base_head 不可达时退用 base_blob（同样救回 B/C）
    blob_c0 = _git(repo, "rev-parse", f"{c0}:{REG_REL}")
    item_blob_only = {"qid": "q-probe-3", "base_head": "0" * 40, "files": [{"path": REG_REL, "base_blob": blob_c0}]}
    text2 = landing._merge_registry_file(item_blob_only, REG_REL, theirs, old_dev).decode("utf-8")
    assert "gate_id: B" in text2 and "gate_id: C" in text2


def test_revalidate_stale_base_is_live_once_filled(cq, repo: Path) -> None:
    """§6.4 陈旧基底重校验：base_blob 填了就必须能红（尺T"结构空转"的反证）。"""
    head = _commit(repo, "cfg/demo.yaml", "one\n", "seed")
    blob = _git(repo, "rev-parse", f"{head}:cfg/demo.yaml")
    item = {"base_head": head, "files": [{"path": "cfg/demo.yaml", "base_blob": blob}]}
    ok, mism = cq._revalidate_stale_base(item, lambda p: blob)
    assert ok and mism == []  # 阴性：一致必放行
    _commit(repo, "cfg/demo.yaml", "two\n", "drift")
    drifted = _git(repo, "rev-parse", "refs/heads/dev:cfg/demo.yaml")
    ok2, mism2 = cq._revalidate_stale_base(item, lambda p: drifted)
    assert not ok2 and mism2 == ["cfg/demo.yaml"]  # 阳性：漂移必报


# ---------------------------------------------------------------------------
# ⑥ 红蓝对抗面：收紧 fail-closed 之后，合法形态不得被误杀
# ---------------------------------------------------------------------------


def test_legitimate_new_registry_file_is_not_dead_lettered(cq, cql, repo: Path, tmp_path: Path) -> None:
    """新增册（base_head 有效但该路径不在基树上）必须走"无 base 侧"合并语义，不得死信。

    这是 fail-closed 收紧最危险的误伤面：若把"基底无此文件"错判成"基底不可知"，
    所有新建注册表的落地都会被自己拦死。
    """
    _commit(repo, "README.md", "seed" + chr(10), "seed commit so dev exists")
    base = _git(repo, "rev-parse", "refs/heads/dev")
    _commit(repo, REG_REL, _book(["A"]), "file created after base")
    old_dev = _git(repo, "rev-parse", "refs/heads/dev")
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue", worktree_path=tmp_path / "wt")
    theirs = _book(["A", "B"]).encode("utf-8")
    item = {"qid": "q-new", "base_head": base, "files": [{"path": REG_REL, "base_blob": None}]}
    out = landing._merge_registry_file(item, REG_REL, theirs, old_dev)
    assert out is not None and b"gate_id: B" in out, "新增件落地不得被 fail-closed 误杀"


def test_malformed_item_degrades_to_dead_letter_not_crash(cql, repo: Path, tmp_path: Path) -> None:
    """畸形项（files 缺 base_blob/整键缺失）→ 带处方的死信，不抛非受控异常。"""
    base = _commit(repo, REG_REL, _book(["A"]), "seed")
    old_dev = _commit(repo, REG_REL, _book(["A", "B"]), "dev moves")
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue", worktree_path=tmp_path / "wt")
    for item in (
        {"qid": "q-m1", "files": [{"path": REG_REL}]},  # 连 base_head 都没有
        {"qid": "q-m2", "base_head": None, "files": []},  # files 空
        {"qid": "q-m3", "base_head": base[:8] + "x" * 32, "files": [{"path": REG_REL, "base_blob": "0" * 40}]},
    ):  # 假对象
        with pytest.raises(RuntimeError) as ei:
            landing._merge_registry_file(item, REG_REL, _book(["A", "C"]).encode("utf-8"), old_dev)
        assert "requeue" in str(ei.value) or "不可读" in str(ei.value), str(ei.value)[:120]


def test_legacy_guard_is_conservative_on_unparseable_time(cql, repo: Path, tmp_path: Path) -> None:
    """存量袋时间基底兜底：时间不可解析/无会话名 → 保守放行（绝不误杀无辜历史项）。"""
    _commit(repo, "docs/a.md", "one\n", "seed")
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue", worktree_path=tmp_path / "wt")
    dev = _git(repo, "rev-parse", "refs/heads/dev")
    for item in (
        {"session_id": "", "created_at": "2026-09-24T99:99:99+08:00", "files": [{"path": "docs/a.md"}]},
        {"session_id": "probe", "created_at": "", "files": [{"path": "docs/a.md"}]},
    ):
        assert landing._conflict_reason(item, dev) is None


def test_legacy_guard_blocks_foreign_landing_on_same_path(cql, repo: Path, tmp_path: Path) -> None:
    """阳性：存量袋（无 base_head）在他会话落过同路径之后必须被判冲突。

    构造真 dev 历史：先建一笔带 `[GW:other-session:q-…]` 标记的提交触及同路径，
    再让一个 created_at 早于它的无基底袋去过判定。
    """
    early = _commit(repo, "docs/shared.md", "v1\n", "seed")
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=tmp_path / "queue", worktree_path=tmp_path / "wt")
    foreign = _commit(
        repo,
        "docs/shared.md",
        "v2 by other session\n",
        "landed work [GW:other-session:q-20260924-other-session-0001] x",
    )
    item = {
        "session_id": "probe-stale",
        "created_at": "2000-01-01T00:00:00+08:00",
        "files": [{"path": "docs/shared.md"}],
    }
    reason = landing._conflict_reason(item, foreign)
    assert isinstance(reason, str) and "时间基底" in reason, f"他会话后落同路径必须拦，实得 {reason!r}"
    # 阴性①：无他人触及的同路径文件，本会话自己后落一笔不算冲突
    own = _commit(repo, "docs/own.md", "v1\n", "seed own")
    _commit(repo, "docs/own.md", "v2\n", "[GW:probe-stale:q-x] own progress")
    own_now = _git(repo, "rev-parse", "refs/heads/dev")
    item_own = {
        "session_id": "probe-stale",
        "created_at": "2000-01-01T00:00:00+08:00",
        "files": [{"path": "docs/own.md"}],
    }
    assert landing._conflict_reason(item_own, own_now) is None, "同会话自己的推进不得判冲突（防系统性假死信）"
    # 阴性②：dev 回指到他人落地之前的点 ⇒ 放行（同一把尺在两个 dev 点位上给出不同答案）
    assert landing._conflict_reason(item, early) is None


# ---------------------------------------------------------------------------
# F-AUDITFIX-STALE-01｜基底口径＝快照真源（2026-09-24 晚：口径错比缺失更致命）
#
# 实证病形：q-20260924-st-commitspeed-tbl-20260924-0005 **带着** base_head 入袋，值是
# 入队那一刻看到的 dev 尖 e500df6dfe，而快照字节来自更早的工作区 ⇒ diff(base, dev) 恒空
# ⇒ 快进判定失明 ⇒ 把在册的 4442b1b4f6（本文件 S-12 那一批）整文件覆回旧版。
# 故本段量的是"基底取的是谁的点位"，不是"有没有基底"。
# ---------------------------------------------------------------------------


def _wt_at(repo: Path, dest: Path, sha: str) -> Path:
    """在 sha 上挂一个 detached 工作区——构造"工作区落后/旁支 dev"的真实形态。"""
    _git(repo, "worktree", "add", "--detach", str(dest), sha)
    return dest


def _show_bytes(repo: Path, rev: str) -> bytes:
    """dev 上某路径的**字节真身**（不经 text 解码——CRLF 会被吃掉，此处必须按字节比）。"""
    r = subprocess.run(["git", "show", rev], cwd=str(repo), capture_output=True, timeout=120)
    assert r.returncode == 0, r.stderr[:200]
    return r.stdout


def test_resolve_base_head_returns_snapshot_provenance(cql, repo: Path, tmp_path: Path) -> None:
    """工作区落后 dev 时，基底必须＝该工作区自己的 HEAD，绝不＝dev 尖。"""
    base = _commit(repo, "docs/p.md", "v1\n", "seed")
    tip = _commit(repo, "docs/p.md", "v2 by other [GW:other-sid:q-x]\n", "foreign landing")
    stale_wt = _wt_at(repo, tmp_path / "stale_wt", base)
    got = cql.resolve_base_head(stale_wt)
    assert got == base, f"基底＝快照真源 {base[:10]}，实得 {got}（取 dev 尖则陈旧工作区永远判不出漂移）"
    assert got != tip  # 阴性：证明本尺不是"两个口径恰好同值"的恒绿


def test_stale_provenance_blocks_reverting_landed_fix(cql, cq, repo: Path, tmp_path: Path) -> None:
    """阳性＝真源基底拦下"把在册修复覆回旧版"；反事实＝旧口径（dev 尖）必放行。

    两半合起来才是判别尺：只测阳性无法区分"守卫有效"与"路径本来没重叠"。
    """
    base = _commit(repo, "docs/p.md", "v1\n", "seed")
    tip = _commit(repo, "docs/p.md", "v2 landed by other [GW:other-sid:q-y]\n", "foreign landing")
    qroot = tmp_path / "queue"
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "wt")
    # 陈旧工作区在它那一版上做的活（字节里根本没有 v2 的内容＝整覆盖会吃掉他人落地）
    item = cq.enqueue_item(
        "probe-stale",
        "stale worktree bag",
        [("docs/p.md", b"v1 + my own edit\n")],
        queue_root=str(qroot),
        options=cq.EnqueueOptions(base_head=base),
    )
    reason = landing._conflict_reason(item, tip)
    assert isinstance(reason, str) and "快进判定失败" in reason, f"真源基底必须判红，实得 {reason!r}"
    stale_caliber = json.loads(json.dumps(item))
    stale_caliber["base_head"] = tip  # 反事实＝修复前的口径（入队时看到的 dev 尖）
    assert landing._conflict_reason(stale_caliber, tip) is None, (
        "反事实须为 None——否则本红来自路径重叠而非基底口径，尺子就没有判别力"
    )


def test_base_ahead_of_dev_does_not_false_red(cql, cq, repo: Path, tmp_path: Path) -> None:
    """基底含自有未并入提交（工作区在旁支）⇒ 不得把"dev 从没改过"的路径判成冲突。"""
    base = _commit(repo, "docs/p.md", "v1\n", "seed")
    side = _wt_at(repo, tmp_path / "side_wt", base)
    own = _commit(side, "docs/mine.md", "mine v1\n", "session work on side branch")
    _commit(repo, "docs/unrelated.md", "u1 [GW:other-sid:q-z]\n", "dev advances elsewhere")
    tip = _git(repo, "rev-parse", "refs/heads/dev")
    qroot = tmp_path / "queue2"
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "wt2")
    item = cq.enqueue_item(
        "probe-side",
        "side branch bag",
        [("docs/mine.md", b"mine v2\n")],
        queue_root=str(qroot),
        options=cq.EnqueueOptions(base_head=own),
    )
    assert landing._conflict_reason(item, tip) is None, (
        "会话分支自有未并入提交不得假红（直接 diff(base, dev) 会把它自己算成 dev 侧漂移）"
    )


def test_noop_overwrite_short_circuit_is_discriminating(cql, cq, repo: Path, tmp_path: Path) -> None:
    """同内容后落地＝覆盖无操作 ⇒ 放行；同路径不同内容 ⇒ 仍判红（短接不得恒绿）。"""
    base = _commit(repo, "docs/p.md", "v1\n", "seed")
    tip = _commit(repo, "docs/p.md", "v2 [GW:other-sid:q-w]\n", "foreign landing")
    qroot = tmp_path / "queue3"
    landing = cql.WorktreeLanding(repo_root=repo, queue_root=qroot, worktree_path=tmp_path / "wt3")
    same = cq.enqueue_item(
        "probe-same",
        "already-landed bytes re-submitted",
        [("docs/p.md", _show_bytes(repo, f"{tip}:docs/p.md"))],
        queue_root=str(qroot),
        options=cq.EnqueueOptions(base_head=base),
    )
    assert landing._conflict_reason(same, tip) is None, "字节与 dev 现态一致 ⇒ 覆盖是 noop，不得误杀"
    different = cq.enqueue_item(
        "probe-diff",
        "genuinely divergent",
        [("docs/p.md", b"my own v3\n")],
        queue_root=str(qroot),
        options=cq.EnqueueOptions(base_head=base),
    )
    assert "快进判定失败" in str(landing._conflict_reason(different, tip)), "不同内容必须仍判红"
