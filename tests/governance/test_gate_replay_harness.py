"""test_gate_replay_harness.py — 重放基线安全网的**红证**测试（能红才算有效尺）

三件事（本仓一晚四次假绿教训在前，恒绿尺＝无效尺）：

1. :func:`test_tree_view_added_lines_captures_single_line_change`
   构造两棵仅差一行的临时提交树，断言 :class:`CommitTreeView` 的 added_lines
   **恰好**捕获那一行（多一行少一行都算失败）。
2. :func:`test_comparator_flags_verdict_drift_and_clears_on_clean_noise`
   往"外来噪声文件"里注入一条违规（真 index 之外的可控注入），断言比较器立刻
   判出 verdict 漂移；把噪声换成干净内容后断言漂移消失——正反两向都判得动。
3. :func:`test_tree_view_never_reads_working_tree`
   探针计数=0：视图四类观测 + 存在性观测一律走 rev 域，不触发进程内磁盘直读；
   同测试反证探针**不是**摆设（宿主 helper ``is_git_tracked`` 经视图通道时必被记)。

pytest 纪律：``-p no:cacheprovider``；输出只落 ``tmp_path``；跨目录跑必验
``__file__`` 落在预期树（worktree conftest 会把主仓根插到 sys.path[0]，
不验就会"在 A 树测 B 码"——假红假绿双向都可能）。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.governance.replay_gate_verdicts import (  # noqa: E402
    DivergenceTracker,
    ReplayHost,
    WriteSandbox,
    load_gate_specs,
    run_gate_once,
)
from zephyr.gov_enforcement.commit_gates import _tree_view as tv_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates._tree_view import (  # noqa: E402
    CommitTreeView,
    MemoryNoiseSource,
    SharedIndexCommitTreeView,
    WorktreeReadProbe,
)

# ── 树归因自检：本测必须测到"本树"的代码，而不是 editable install 指向的别处 ──
_EXPECTED_SRC_ROOT = (_REPO_ROOT / "src").resolve()


def _in_expected_tree(module) -> bool:
    f = Path(str(getattr(module, "__file__", ""))).resolve()
    return str(f).startswith(str(_EXPECTED_SRC_ROOT))


def test_modules_resolve_to_this_tree():
    """防"在 worktree 跑测试却测到主仓旧码"（假红假绿的共同上游）。"""
    assert _in_expected_tree(tv_mod), f"_tree_view 解析到外来树：{tv_mod.__file__}"
    import scripts.governance.replay_gate_verdicts as driver_mod

    expect_scripts = (_REPO_ROOT / "scripts").resolve()
    assert str(Path(driver_mod.__file__).resolve()).startswith(str(expect_scripts)), driver_mod.__file__


# ══════════════════════════════════════════════════════════════════════════
# 一次性 scratch git 仓（只落 tmp_path，不碰生产仓 objects/refs）
# ══════════════════════════════════════════════════════════════════════════
_PROBE_BODY = """\"\"\"probe module.\"\"\"

ALPHA = 1
BETA = 2
"""

_PROBE_BODY_EDITED = """\"\"\"probe module.\"\"\"

ALPHA = 1
BETA = 2
GAMMA = 4
"""


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "csx-probe",
            "GIT_AUTHOR_EMAIL": "csx-probe@invalid",
            "GIT_COMMITTER_NAME": "csx-probe",
            "GIT_COMMITTER_EMAIL": "csx-probe@invalid",
            "GIT_CONFIG_NOSYSTEM": "1",
        },
    )
    assert proc.returncode == 0, f"git {' '.join(args)} 失败：{proc.stderr[:300]}"
    return proc.stdout.strip()


@pytest.fixture(scope="module")
def scratch_repo(tmp_path_factory) -> Path:
    """两棵仅差一行的提交树（base: ALPHA/BETA=2；head: BETA=2 + 新增 GAMMA=4）。"""
    repo = tmp_path_factory.mktemp("csx_scratch_repo")
    _git(repo, "init", "-q", "--initial-branch=csx")
    _git(repo, "config", "core.autocrlf", "false")
    target = repo / "pkg" / "probe.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_PROBE_BODY, encoding="utf-8", newline="")
    (repo / "README.md").write_text("# scratch\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base tree")
    base = _git(repo, "rev-parse", "HEAD")
    target.write_text(_PROBE_BODY_EDITED, encoding="utf-8", newline="")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "single line added")
    head = _git(repo, "rev-parse", "HEAD")
    _SCRATCH_INFO.update({"base": base, "head": head, "path": "pkg/probe.py"})
    return repo


_SCRATCH_INFO: dict = {}


@pytest.fixture(scope="module")
def real_host() -> ReplayHost:
    return ReplayHost(_REPO_ROOT)


def _scratch_view(repo: Path, **kw) -> CommitTreeView:
    info = _SCRATCH_INFO
    return CommitTreeView(info["base"], info["head"], project_root=repo, **kw)


# ══════════════════════════════════════════════════════════════════════════
# ① added_lines 恰好捕获那一行
# ══════════════════════════════════════════════════════════════════════════
def test_tree_view_added_lines_captures_single_line_change(scratch_repo: Path):
    view = _scratch_view(scratch_repo)
    path = _SCRATCH_INFO["path"]
    assert view.staged_files() == [path]
    lines = view.added_lines(path)
    # 仅新增一行 GAMMA = 4（BETA 行未变，不该出现在 added 里）；GAMMA 居第 5 行
    assert lines == [(5, "GAMMA = 4")], lines
    assert view.read_staged_file(path) == _PROBE_BODY_EDITED
    assert view.read_head_file(path) == _PROBE_BODY
    # 删除侧同样可复现：改一行＝一删一增
    info = _SCRATCH_INFO
    v2 = CommitTreeView(info["base"], info["head"], project_root=scratch_repo)
    assert v2.added_lines(path) == [(5, "GAMMA = 4")]
    assert view.own_files() == [path]


def test_tree_view_command_mapping_table():
    """改写表逐条硬绑——语义漂移＝静默假绿，故此处钉死。"""
    base, head = "BASE", "HEADX"
    cases = [
        (["git", "show", ":a.py"], "index->tree", f"git show {head}:a.py"),
        (["git", "show", "HEAD:a.py"], "head->base", f"git show {base}:a.py"),
        (
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            "index->tree",
            f"git diff {base} {head} --name-only --diff-filter=AM",
        ),
        (
            ["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", "a.py"],
            "index->tree",
            f"git diff {base} {head} --unified=0 --ignore-cr-at-eol -- a.py",
        ),
        (["git", "ls-files", "--cached", "--", "a.py"], "index->tree", f"git ls-tree -r --name-only {head} -- a.py"),
        (["git", "cat-file", "-e", "HEAD:a.py"], "head->base", f"git cat-file -e {base}:a.py"),
        (["git", "status", "--porcelain"], "worktree", None),
        (["git", "diff", "--", "a.py"], "worktree", None),
        (["git", "diff", "HEAD", "--", "a.py"], "worktree", None),
    ]
    for argv, want_kind, want_str in cases:
        mapped = tv_mod.map_git_command(argv, base, head)
        assert mapped.kind == want_kind, (argv, mapped.kind, want_kind)
        if want_str:
            assert " ".join(mapped.argv) == want_str, (argv, mapped.argv)


# ══════════════════════════════════════════════════════════════════════════
# ② 比较器判得动 verdict 漂移（正反两向）
# ══════════════════════════════════════════════════════════════════════════
# 候选台：内容扫描型、无 own-scope 收窄者（噪声注入应致其 verdict 翻转）
_DRIFT_CANDIDATES = {
    "MUTABLE-CONST-WITHOUT-FINAL",
    "NO-IMPORT-SIDE-EFFECT",
    "DATETIME-NOW-FORBIDDEN",  # 已 own-scope 收窄的对照组（不应翻转）
    "UNSAFE-DICT-SPREAD",
}
_NOISY_BODY = "from dataclasses import dataclass\n\nSHARED_CACHE = {}\n\nREGISTRY_TABLE = []\n"
_CLEAN_BODY = "from dataclasses import dataclass\n\nSHARED_CACHE: Final[dict] = {}\n"
_NOISE_PATH = "src/zephyr/gov_enforcement/commit_gates/_csx_replay_noise_probe.py"


def _run_pair(host: ReplayHost, gate, own: list[str], base: str, head: str, noise: dict[str, str], sandbox):
    va = CommitTreeView(base, head, gateway=host, probe=WorktreeReadProbe())
    vb = SharedIndexCommitTreeView(
        base, head, gateway=host, noise_source=MemoryNoiseSource(noise), probe=WorktreeReadProbe()
    )
    ra = run_gate_once(gate, va, own, host, "", sandbox=sandbox, use_probe=False)
    rb = run_gate_once(gate, vb, own, host, "", sandbox=sandbox, use_probe=False)
    return ra, rb


def test_comparator_flags_verdict_drift_and_clears_on_clean_noise(real_host: ReplayHost, tmp_path: Path):
    import json
    import re

    roster = _REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"
    assert roster.exists(), roster
    # 名册可读（同 driver 的装载面）
    text = roster.read_text(encoding="utf-8")
    assert "gate_id:" in text and re.search(r"total_gates:\s*\d+", text)

    gates, failures = load_gate_specs(_REPO_ROOT, set(_DRIFT_CANDIDATES))
    assert gates, f"候选台零装载成功：{failures}"
    loaded = {g.gate_id for g in gates}
    # 取真实历史提交的本件清单作为 own 面（不造生产提交）
    commits = (
        subprocess.run(
            ["git", "log", "--no-merges", "-n", "1", "--format=%H%x09%P"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        .stdout.strip()
        .split("\t")
    )
    head, base = commits[0], commits[1].split()[0]
    own = CommitTreeView(base, head, gateway=real_host).own_files()
    sandbox = WriteSandbox(_REPO_ROOT, tmp_path / "sandbox")

    tracker = DivergenceTracker()
    flipped: dict[str, tuple[str, str]] = {}
    for gate in gates:
        ra, rb = _run_pair(real_host, gate, own, base, head, {_NOISE_PATH: _NOISY_BODY}, sandbox)
        assert ra["verdict"] in {"pass", "fail", "skip", "error"}, ra
        assert rb["verdict"] in {"pass", "fail", "skip", "error"}, rb
        if ra["verdict"] != rb["verdict"] or ra["hits"] != rb["hits"]:
            flipped[gate.gate_id] = (
                f"{ra['verdict']}/{ra['hits']}",
                f"{rb['verdict']}/{rb['hits']}",
            )
        tracker.add(head, ra, rb)
    # 尺必须能红：至少一台门的 verdict/hits 随 index 规模（外来噪声）漂移
    assert flipped, f"注入外来违规后无一台判据漂移——尺恒绿即无效尺（gates={loaded}）"
    assert tracker.examples, "比较器未记录差异样例"
    assert any(e["gate_id"] in flipped for e in tracker.examples)
    # 对照组：DATETIME-NOW-FORBIDDEN 有 own-scope 收窄，噪声不该惊动它
    if "DATETIME-NOW-FORBIDDEN" in loaded:
        assert "DATETIME-NOW-FORBIDDEN" not in flipped, "own-scope 收窄台被噪声惊动＝收窄失效"

    # 反向：噪声内容干净后，同一批台的漂移必须消失（否则判据与内容无关＝尺不灵）
    flipped_clean = {}
    for gate in gates:
        if gate.gate_id not in flipped:
            continue
        ra, rb = _run_pair(real_host, gate, own, base, head, {_NOISE_PATH: _CLEAN_BODY}, sandbox)
        if ra["verdict"] != rb["verdict"] or ra["hits"] != rb["hits"]:
            flipped_clean[gate.gate_id] = (ra["verdict"], rb["verdict"])
    assert not flipped_clean, f"干净噪声仍判漂移（误报）：{flipped_clean}"
    assert json.dumps({"ok": True}) == '{"ok": true}'  # sanity：序列化面可用


# ══════════════════════════════════════════════════════════════════════════
# ③ 视图零磁盘直读 + 探针非摆设（反证）
# ══════════════════════════════════════════════════════════════════════════
def test_tree_view_never_reads_working_tree(scratch_repo: Path):
    path = _SCRATCH_INFO["path"]
    view = _scratch_view(scratch_repo, probe=WorktreeReadProbe())
    with view.probe.arm(scratch_repo):
        view.staged_files()
        view.added_lines(path)
        view.read_staged_file(path)
        view.read_head_file(path)
        view.repo_state_has_file(path)
        view.own_files()
        assert view.probe.view_own_fs_reads == [], view.probe.summary()
        assert view.probe.fs_reads == [], view.probe.summary()
        assert view.probe.git_worktree_reads == [], view.probe.summary()

    # 反证：探针不是摆设——宿主 helper 走视图通道时，工作树读必须被记下来
    view2 = _scratch_view(scratch_repo, probe=WorktreeReadProbe())
    view2.is_git_tracked(path)
    assert view2.probe.git_worktree_reads, "ls-files 类工作树读未被记账＝绊线形同虚设"

    # 反证 2：strict 模式下工作树直读当场抛，不静默降级
    strict_view = _scratch_view(scratch_repo, probe=WorktreeReadProbe(), strict=True)
    with pytest.raises(tv_mod.WorktreeReadBlocked):
        strict_view.run_git(["git", "status", "--porcelain"])


def test_probe_records_in_process_disk_reads(scratch_repo: Path):
    """探针在"真有人读磁盘"时确实计数（否则 ③ 的 0 值无意义）。"""
    probe = WorktreeReadProbe()
    with probe.arm(scratch_repo):
        (scratch_repo / "README.md").read_text(encoding="utf-8")
    assert probe.fs_reads, "磁盘直读未被记账"
    assert any("README.md" in e.detail for e in probe.fs_reads)


def test_write_sandbox_keeps_production_runtime_untouched(real_host: ReplayHost, tmp_path: Path):
    """门禁在重放里写 ``.runtime/**`` 必须改道沙盒（防污染生产遥测）。"""
    sandbox = WriteSandbox(_REPO_ROOT, tmp_path / "sandbox")
    target = _REPO_ROOT / ".runtime" / "gate_audit" / "_csx_probe_should_not_exist.jsonl"
    with sandbox():
        Path(target).write_text("x\n", encoding="utf-8")
    assert not target.exists(), "写盘穿透到生产 .runtime——重放面会伪造治理遥测"
    assert sandbox.events, "改道未留痕"
