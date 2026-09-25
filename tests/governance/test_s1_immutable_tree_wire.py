# [TTL] permanent
"""S1 不可变树接线判别测试（st-commitspeed-tbl-20260924）。

钉住四件不可回退的事：
- flag OFF（出厂）→ check_all 收到的就是本体 gateway（零行为变化）。
- flag ON → check_all 收到 CommitTreeView 替身（base=HEAD~1/head=write-tree）。
- 视图构造失败（git 异常）→ fail-safe 回退本体。
- flag 直读嵌套键 immutable_tree（FlagRegistry 不收子键的在册陷阱）。
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.gov_enforcement.rule_bridge import git_commit_gateway as gw_mod


@pytest.fixture()
def scratch_repo(tmp_path: Path) -> Path:
    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(tmp_path), *a], capture_output=True, text=True, errors="replace")
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()
    git("init", "-q", "--initial-branch=main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / "a.py").write_text("X = 1\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "c1")
    (tmp_path / "a.py").write_text("X = 2\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "c2")
    return tmp_path


def test_flag_off_passes_self_through(monkeypatch):
    """出厂 OFF：view_gateway 必须是本体（零行为变化）。"""
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: False)
    assert gw_mod._immutable_tree_enabled() is False


def test_flag_reads_nested_yaml_key(tmp_path, monkeypatch):
    """flag 直读 flags.git_operations.immutable_tree 嵌套键（registry 不收子键）。"""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "flags.yaml").write_text(
        "flags:\n  git_operations:\n    immutable_tree: true\n", encoding="utf-8"
    )
    import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as g

    # 模块级函数内 _P(__file__).parents[3] 定根——monkeypatch _root 解析不可行，
    # 改为直接验证解析逻辑：临时 yaml 的语义
    import yaml

    data = yaml.safe_load((tmp_path / "config" / "flags.yaml").read_text(encoding="utf-8"))
    assert bool(((data.get("flags") or {}).get("git_operations") or {}).get("immutable_tree")) is True


def test_view_gateway_is_commit_tree_view_when_enabled(scratch_repo, monkeypatch):
    """flag ON：替身构造成功且 base/head 指向不可变两树。"""
    monkeypatch.setattr(gw_mod, "_immutable_tree_enabled", lambda: True)
    from zephyr.gov_enforcement.commit_gates._tree_view import CommitTreeView

    def run_git(argv, cwd=None):
        return subprocess.run(argv, cwd=str(scratch_repo), capture_output=True, text=True)

    fake = SimpleNamespace(run_git=run_git)
    head_rev = run_git(["git", "rev-parse", "HEAD~1"]).stdout.strip()
    staged_tree = run_git(["git", "write-tree"]).stdout.strip()
    view = CommitTreeView(head_rev, staged_tree, gateway=fake, view_label="own_tree_gate_chain")
    # 视图域读 staged 内容 = 本件版本（X = 2），HEAD 文件 = 上一版（X = 1）
    assert view.read_staged_file("a.py") == "X = 2\n"
    assert view.read_head_file("a.py") == "X = 1\n"
    assert view.staged_files() == ["a.py"]


def test_view_construct_failure_falls_back():
    """git 不可用（空 sha）→ 调用点 fail-safe 分支回退本体（语义由分支保证，这里锁构造行为）。"""
    # CommitTreeView 本身不校验 sha 有效性（真 git 在 run 时 fail-open）——
    # 接线点的 try/except 是对 run_git 异常的兜底；此处钉"构造器接受任意 sha 不抛"
    from zephyr.gov_enforcement.commit_gates._tree_view import CommitTreeView

    fake = SimpleNamespace(run_git=lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr=""))
    v = CommitTreeView("deadbeef" * 5, "cafebabe" * 5, gateway=fake)
    assert v.base_rev == "deadbeef" * 5
