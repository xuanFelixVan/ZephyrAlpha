# [MODULE] tests.scripts.test_session_worktree_promote
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] scripts.session_worktree (promote)
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 全部在 tmp 仓（REPO_ROOT 重定向，零生产写）；防覆盖=整单拒绝；审计行随 verdict 落盘
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] task_bound
"""test_session_worktree_promote.py — promote 子命令单测（D11-S05 收口件）。

真源: docs/_working/mine_fullchain_20261015/delivery_fig11/D11-S05_staging_promote.md
测试组:
- test_promote_moves_files_preserving_relative_paths: mv 通道原相对路径迁入
- test_promote_removes_emptied_staging_dir: 成果迁空后 staging 就地拆除
- test_promote_refuses_existing_dest: 目标目录已存在=拒绝+审计留痕
- test_promote_refuses_conflict_all_or_nothing: 任一同名目标存在=整单拒绝零迁移
- test_promote_empty_or_missing_staging_errors: staging 缺席/为空=响亮报错
- test_promote_bad_sid_shape_rejected: sid 形状白名单（防路径穿越）
- test_promote_audit_row_landed: PROMOTED verdict 审计行字段齐全
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "session_worktree.py"


def _load_module(repo: Path, monkeypatch: pytest.MonkeyPatch):
    spec = importlib.util.spec_from_file_location("session_worktree_promote_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "REPO_ROOT", repo)
    monkeypatch.setattr(mod, "WORKTREE_ROOT", repo / ".worktrees")
    return mod


def _args(sid: str) -> argparse.Namespace:
    return argparse.Namespace(session_id=sid)


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    mod = _load_module(repo, monkeypatch)
    staging = repo / ".runtime" / "sessions" / "sid-x" / "staging"
    staging.mkdir(parents=True)
    return mod, repo, staging


def test_promote_moves_files_preserving_relative_paths(env):
    mod, repo, staging = env
    (staging / "deep" / "nest").mkdir(parents=True)
    (staging / "a.md").write_text("A", encoding="utf-8")
    (staging / "deep" / "nest" / "b.json").write_text("{}", encoding="utf-8")
    rc = mod.cmd_promote(_args("sid-x"))
    assert rc == 0
    dest = repo / "docs" / "_working" / "sid-x-promoted"
    assert (dest / "a.md").read_text(encoding="utf-8") == "A"
    assert (dest / "deep" / "nest" / "b.json").read_text(encoding="utf-8") == "{}"
    assert not (staging / "a.md").exists()  # mv 通道：原件不在


def test_promote_removes_emptied_staging_dir(env):
    mod, repo, staging = env
    (staging / "x.txt").write_text("x", encoding="utf-8")
    assert mod.cmd_promote(_args("sid-x")) == 0
    assert not staging.exists()  # 迁空后就地拆除
    assert (repo / ".runtime" / "sessions" / "sid-x").is_dir()  # session 壳其余不动


def test_promote_refuses_existing_dest(env):
    mod, repo, staging = env
    (staging / "a.md").write_text("A2", encoding="utf-8")
    dest = repo / "docs" / "_working" / "sid-x-promoted"
    dest.mkdir(parents=True)
    assert mod.cmd_promote(_args("sid-x")) == 1
    assert (staging / "a.md").exists()  # 零迁移
    rows = _audit_rows(repo)
    assert rows[-1]["verdict"] == "REFUSED_DEST_EXISTS"


def test_promote_refuses_conflict_all_or_nothing(env):
    mod, repo, staging = env
    (staging / "a.md").write_text("A", encoding="utf-8")
    (staging / "b.md").write_text("B", encoding="utf-8")
    dest = repo / "docs" / "_working" / "sid-x-promoted" / "sub"
    dest.mkdir(parents=True)
    (dest.parent / "a.md").write_text("old", encoding="utf-8")  # 同名冲突（子路径 a.md）
    assert mod.cmd_promote(_args("sid-x")) == 1
    assert (staging / "b.md").exists()  # 整单拒绝：无冲突的 b.md 也不迁
    assert (dest.parent / "a.md").read_text(encoding="utf-8") == "old"  # 原值未动
    rows = _audit_rows(repo)
    assert rows[-1]["verdict"] == "REFUSED_CONFLICT"


def test_promote_empty_or_missing_staging_errors(env, capsys):
    mod, repo, staging = env
    assert mod.cmd_promote(_args("sid-x")) == 1  # 空 staging
    assert mod.cmd_promote(_args("sid-none")) == 1  # 缺席 staging
    err = capsys.readouterr().err
    assert "staging 为空" in err or "staging 目录不存在" in err


def test_promote_bad_sid_shape_rejected(env):
    mod, _repo, _staging = env
    assert mod.cmd_promote(_args("../evil")) == 1
    assert mod.cmd_promote(_args("")) == 1
    assert mod.cmd_promote(_args(".")) == 1


def test_promote_audit_row_landed(env):
    mod, repo, staging = env
    (staging / "a.md").write_text("A", encoding="utf-8")
    (staging / "b.md").write_text("B", encoding="utf-8")
    assert mod.cmd_promote(_args("sid-x")) == 0
    rows = _audit_rows(repo)
    assert rows and rows[-1]["verdict"] == "PROMOTED"
    r = rows[-1]
    assert r["session_id"] == "sid-x"
    assert r["moved_count"] == 2
    assert sorted(r["moved"]) == ["a.md", "b.md"]
    assert r["source_removed"] is True
    assert r["timestamp"] and r["pid"]


def test_promote_source_removal_blocked_keeps_delivered(env, monkeypatch, capsys):
    """删源受阻（闸拦）：成果不回迁、WARN 出声、source_removed=false 留痕、rc=0。"""
    mod, repo, staging = env
    (staging / "a.md").write_text("A", encoding="utf-8")

    def _blocked(*a, **k):
        raise RuntimeError("[OPS-GUARD] 模拟保护区拦截")

    monkeypatch.setattr(mod.shutil, "rmtree", _blocked)
    assert mod.cmd_promote(_args("sid-x")) == 0
    dest = repo / "docs" / "_working" / "sid-x-promoted"
    assert (dest / "a.md").read_text(encoding="utf-8") == "A"  # 成果在位不回迁
    assert staging.exists()  # 源残留（WARN 留痕交 TTL/人工）
    err = capsys.readouterr().err
    assert "WARN" in err and "源清理被阻" in err
    rows = _audit_rows(repo)
    assert rows[-1]["verdict"] == "PROMOTED" and rows[-1]["source_removed"] is False


def _audit_rows(repo: Path) -> list[dict]:
    f = repo / ".runtime" / "gate_audit" / "staging_promote.jsonl"
    if not f.exists():
        return []
    return [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]
