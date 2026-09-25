# [TTL] permanent
"""S1 门禁咽喉 own-tree 化红测（st-commitspeed-tbl-20260924 包9）。

每把尺先自证能红（本仓一晚四次假绿的教训在册）。钉住六件不可回退的事：
- own-tree 生效时四入口代理读到的文件集合=树内集合：工作树有（脏改/未跟踪
  违规件）而树内没有的文件，门 verdict 必须不看见（磁盘回落=口径偷换，绊线红）。
- CommitTreeView 工作树直读探针常开两通道：视图自身 fs 直读恒 0；工作树类
  git 命令被命令通道计数（探针自证能红）。
- flag OFF 回退路径：无视图存在处四入口逐字走旧路径（argv 原样），
  _build_own_tree_view 返回本体 gateway。
- 15 台分道：check_all(shared_index_gateway=本体) 时名单内台拿本体 gateway、
  名单外台拿视图；缺省（重放器式直调）零分派——两台都拿视图（现行为）。
- 接线 base 语义：base_rev=门禁时刻 HEAD（本件父提交）——HEAD~1 off-by-one
  修正的回归钉（旧错会让 read_head_file 读到祖父版本）。
- 新指标"树内外来 staged 数恒 0"：污染树→审计留痕；干净树→零记录。

真源：docs/_working/commit_speedup_campaign/20_target_arch/A4_migration_ladder.md S1 段。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import MethodType, SimpleNamespace

import pytest

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _get_added_lines,
    _get_staged_py_files,
    _own_tree_view,
    _read_head_file,
    _read_staged_file,
)
from zephyr.gov_enforcement.commit_gates._tree_view import (
    SHARED_INDEX_WITHOUT_OWN_SCOPE,
    CommitTreeView,
    WorktreeReadProbe,
)
from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw_mod
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateSpec,
)

_CANARY = "src/zephyr/own_canary.py"
_VIOLATION_LINE = "_TS = time.time()\n"


def _run_git(repo: Path, *argv: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *argv], capture_output=True, text=True, errors="replace")
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _fake_host(repo: Path) -> SimpleNamespace:
    """带真实 git 的本体 gateway 替身（run_git 契约同 GitCommitGateway）。"""

    def run_git(argv, cwd=None):
        return subprocess.run(argv, cwd=str(repo), capture_output=True, text=True, errors="replace")

    return SimpleNamespace(run_git=run_git, project_root=str(repo))


def _make_repo(tmp_path: Path, *, staged_violation: bool = True) -> Path:
    """scratch 仓：c1/c2 两笔干净提交 + 暂存区挂 canary 违规改（未提交）。"""
    repo = tmp_path / "repo"
    (repo / "src" / "zephyr").mkdir(parents=True)

    def git(*a: str) -> str:
        return _run_git(repo, *a)

    git("init", "-q", "--initial-branch=main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / _CANARY).write_text("VALUE = 1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "c1")
    (repo / _CANARY).write_text("VALUE = 2\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "c2")
    if staged_violation:
        (repo / _CANARY).write_text("VALUE = 2\n" + _VIOLATION_LINE, encoding="utf-8")
        git("add", _CANARY)
    return repo


def _own_view(repo: Path, host) -> CommitTreeView:
    """接线同款视图：base=门禁时刻 HEAD，head=write-tree。"""
    return CommitTreeView(
        _run_git(repo, "rev-parse", "HEAD"),
        _run_git(repo, "write-tree"),
        gateway=host,
        view_label="own_tree_gate_chain",
        probe=WorktreeReadProbe(),
    )


# ═══ 1. own-tree 文件集合=树内集合（工作树有、树内没有 ⇒ 门必须看不见）═══
def test_helpers_through_view_read_tree_not_worktree(tmp_path):
    repo = _make_repo(tmp_path)
    # 工作树面：canary 脏改（未暂存，多一条违规）+ 未跟踪违规件——两者都不在树内
    (repo / _CANARY).write_text("VALUE = 2\n" + _VIOLATION_LINE + "_TS2 = time.time()\n", encoding="utf-8")
    ghost = repo / "src" / "zephyr" / "ghost_violation.py"
    ghost.write_text("G = time.time()\n", encoding="utf-8")
    view = _own_view(repo, _fake_host(repo))

    assert view.staged_files() == [_CANARY]
    # 树内内容=暂存快照，不是磁盘脏改（磁盘回落=口径偷换）
    assert view.read_staged_file(_CANARY) == "VALUE = 2\n" + _VIOLATION_LINE
    assert view.read_staged_file(str(ghost.relative_to(repo))) is None  # 盘上有、树内无
    assert view.read_head_file(_CANARY) == "VALUE = 2\n"

    # 四入口代理同口径
    assert _get_staged_py_files(view, "TEST") == [_CANARY]
    assert _read_staged_file(view, _CANARY) == "VALUE = 2\n" + _VIOLATION_LINE
    assert _read_staged_file(view, "src/zephyr/ghost_violation.py") is None
    assert _read_head_file(view, _CANARY) == "VALUE = 2\n"
    added = _get_added_lines(view, _CANARY, "TEST")
    assert [(n, t) for n, t in added] and added[0][1].strip() == "_TS = time.time()"


def test_real_gate_verdict_cannot_see_worktree_only_files(tmp_path):
    """真门（DATETIME-NOW-FORBIDDEN）经视图跑：只看见树内 1 处违规；
    盘上脏改第二处+未跟踪违规件不进 verdict（hits 恒 1、名字不出现）。"""
    from zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate import (
        make_datetime_now_forbidden_gate,
    )

    repo = _make_repo(tmp_path)
    (repo / _CANARY).write_text("VALUE = 2\n" + _VIOLATION_LINE + "_TS2 = time.time()\n", encoding="utf-8")
    (repo / "src" / "zephyr" / "ghost_violation.py").write_text("G = time.time()\n", encoding="utf-8")
    view = _own_view(repo, _fake_host(repo))

    passed, detail = make_datetime_now_forbidden_gate().check(view, [_CANARY], session_id=None)
    assert passed is False
    assert detail.count("time.time() 调用") == 1  # 树内恰好一处
    assert "ghost_violation" not in detail
    assert "_TS2" not in detail  # 脏改行不在暂存快照里


# ═══ 2. 绊线：视图自身 fs 直读恒 0；探针两通道自证能红 ═══
def test_probe_view_own_fs_reads_zero_and_channels_go_red(tmp_path):
    repo = _make_repo(tmp_path)
    host = _fake_host(repo)
    view = _own_view(repo, host)
    with view.probe.arm(project_root=str(repo)):
        # 视图四入口全跑一遍——不得触碰工作树文件系统
        view.read_staged_file(_CANARY)
        view.staged_files()
        view.added_lines(_CANARY)
        view.read_head_file(_CANARY)
        summary = view.probe.summary()
        assert summary["view_own_fs_reads"] == 0
        assert summary["fs_reads"] == 0
        # 进程内通道自证能红：测试自身读工作树文件→被归因记录
        (repo / _CANARY).read_text(encoding="utf-8")
        assert view.probe.summary()["fs_reads"] >= 1
    # 命令通道自证能红：工作树类 git 命令被计数（测量模式透传不阻断）
    view.run_git(["git", "status", "--porcelain"])
    assert view.probe.summary()["git_worktree_reads"] >= 1


# ═══ 3. flag OFF 回退：无视图处逐字旧路径 ═══
def test_helpers_take_legacy_path_with_plain_gateway(tmp_path):
    repo = _make_repo(tmp_path)
    host = _fake_host(repo)
    assert _own_tree_view(host) is None  # 本体 gateway≠视图
    assert _read_staged_file(host, _CANARY) == "VALUE = 2\n" + _VIOLATION_LINE
    assert _read_head_file(host, _CANARY) == "VALUE = 2\n"
    assert _get_staged_py_files(host, "TEST") == [_CANARY]
    assert _get_added_lines(host, _CANARY, "TEST")


def test_wiring_flag_off_returns_self(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path)
    fake = _fake_host(repo)
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: False)
    assert gw_mod.GitCommitGateway._build_own_tree_view(fake, [_CANARY], "s") is fake


# ═══ 4. 15 台分道：check_all 逐台 gateway 分发 ═══
def _spy_registry(seen: dict):
    reg = CommitGateRegistry()

    def _mk(gid: str, prio: int):
        def _check(gw, files, **kw):
            seen[gid] = gw
            return True, ""

        return GateSpec(gate_id=gid, check=_check, priority=prio)

    reg.register(_mk("CH-BATCH-SIZE", 1))  # 名单内（A3 shared_index_without_own_scope）
    reg.register(_mk("DATETIME-NOW-FORBIDDEN", 2))  # 名单外
    return reg


def test_check_all_routes_exempt_gate_to_shared_index_gateway(tmp_path):
    repo = _make_repo(tmp_path)
    host = _fake_host(repo)
    view = _own_view(repo, host)
    seen: dict = {}
    reg = _spy_registry(seen)
    reg.check_all(view, [_CANARY], shared_index_gateway=host)
    assert seen["CH-BATCH-SIZE"] is host  # 名单内：本体 gateway（读真共享暂存区）
    assert seen["DATETIME-NOW-FORBIDDEN"] is view  # 名单外：视图替身


def test_check_all_without_shared_index_gateway_zero_dispatch(tmp_path):
    """重放器式直调（不传 shared_index_gateway）＝零分派：名单内台也拿视图（现行为）。"""
    repo = _make_repo(tmp_path)
    host = _fake_host(repo)
    view = _own_view(repo, host)
    seen: dict = {}
    _spy_registry(seen).check_all(view, [_CANARY])
    assert seen["CH-BATCH-SIZE"] is view
    assert seen["DATETIME-NOW-FORBIDDEN"] is view


def test_check_all_same_object_zero_dispatch(tmp_path):
    """flag OFF 链（shared_index_gateway 即 gateway）＝零分派零行为变更。"""
    repo = _make_repo(tmp_path)
    host = _fake_host(repo)
    seen: dict = {}
    _spy_registry(seen).check_all(host, [_CANARY], shared_index_gateway=host)
    assert seen["CH-BATCH-SIZE"] is host
    assert seen["DATETIME-NOW-FORBIDDEN"] is host


# ═══ 5. 接线 base 语义：base_rev=门禁时刻 HEAD（HEAD~1 off-by-one 回归钉）═══
def _bind_audit(fake: SimpleNamespace) -> SimpleNamespace:
    fake._audit_own_tree_foreign = MethodType(gw_mod.GitCommitGateway._audit_own_tree_foreign, fake)
    return fake


def test_wiring_base_rev_is_chain_head_not_grandparent(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path)
    fake = _bind_audit(_fake_host(repo))
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: True)
    view = gw_mod.GitCommitGateway._build_own_tree_view(fake, [_CANARY], "s")
    assert isinstance(view, CommitTreeView)
    assert view.base_rev == _run_git(repo, "rev-parse", "HEAD")  # =c2（父提交），≠c2^
    assert view.head_rev == _run_git(repo, "write-tree")
    # 旧 bug（base=HEAD~1）会让本断言读到 c1 的 "VALUE = 1"
    assert view.read_head_file(_CANARY) == "VALUE = 2\n"


def test_wiring_view_failure_falls_back_to_self(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path)

    def _boom(argv, cwd=None):
        raise OSError("git exploded")

    fake = _bind_audit(SimpleNamespace(run_git=_boom, project_root=str(repo)))
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: True)
    assert gw_mod.GitCommitGateway._build_own_tree_view(fake, [_CANARY], "s") is fake


# ═══ 6. 新指标：树内外来 staged 文件数恒 0 ═══
def test_own_tree_foreign_metric_audits_polluted_tree(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path)
    # 污染：他会话 staged 件混进共享 index（声明清单只有 canary）
    (repo / "src" / "zephyr" / "foreign_staged.py").write_text("F = 1\n", encoding="utf-8")
    _run_git(repo, "add", "src/zephyr/foreign_staged.py")
    fake = _bind_audit(_fake_host(repo))
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: True)
    view = gw_mod.GitCommitGateway._build_own_tree_view(fake, [_CANARY], "s")
    assert isinstance(view, CommitTreeView)
    audit = repo / ".runtime" / "gate_audit" / "own_tree_scope_foreign_staged.jsonl"
    assert audit.exists()
    rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert rec["gate"] == "OWN-TREE-SCOPE"
    assert rec["foreign_count"] == 1
    assert rec["foreign_files"] == ["src/zephyr/foreign_staged.py"]


def test_own_tree_foreign_metric_silent_on_clean_tree(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path, staged_violation=False)
    fake = _bind_audit(_fake_host(repo))
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: True)
    # 声明清单覆盖树内全部文件 → 干净
    view = gw_mod.GitCommitGateway._build_own_tree_view(fake, [_CANARY], "s")
    assert isinstance(view, CommitTreeView)
    assert not (repo / ".runtime" / "gate_audit" / "own_tree_scope_foreign_staged.jsonl").exists()


# ═══ 7. 名单完整性：代码常量 ↔ A3 矩阵真源逐台相等 ═══
def test_shared_index_exemption_set_matches_a3_matrix():
    import yaml

    a3 = Path(__file__).resolve().parents[2] / (
        "docs/_working/commit_speedup_campaign/20_target_arch/A3_gate_repointing_matrix.yaml"
    )
    data = yaml.safe_load(a3.read_text(encoding="utf-8"))
    expected = {
        g["gate_id"] for g in data["gates"] if g.get("reads_shared_index") and not g.get("narrows_to_own_scope_in_code")
    }
    assert frozenset(expected) == SHARED_INDEX_WITHOUT_OWN_SCOPE
    assert len(SHARED_INDEX_WITHOUT_OWN_SCOPE) == 15
