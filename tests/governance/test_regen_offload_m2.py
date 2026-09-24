# [TTL] permanent
"""M2/T5 衍生再生出窗判别测试（B0_3 §4 红测永久化，st-commitspeed-tbl-20260924）。

钉住四件不可回退的事：
- P-3 逃生口只抑制执行不抑制记账：ZEPHYR_SKIP_REGENERATE=1 时意图账 ledger.jsonl
  仍必须有记录（现码红：检查在记账前直接 return 0，且根本没有 ledger）。
- R2b 去抖不丢：锁活跃窗内连触 5 次 → spawn=1 而 ledger=5，且落 pending_rerun
  供尾事件补跑（现码红：锁跳过零留痕）。
- R2a（flag main_only）：worktree 语境只记账不 spawn（出厂 any_worktree 保持现行为）。
- 根钉定（R2c 前置）：worktree 的 .git 指针文件能解析出主区根——锁/账/编排器
  spawn 全部落主区，跨工单点（现码红：_REPO_ROOT=parents[3] 恒为脚本所在 worktree）。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import scripts.governance.git_hooks.post_commit_regen_yaml as pcr


@pytest.fixture()
def fake_roots(tmp_path, monkeypatch):
    """伪主区+伪 worktree 语境：把触发器的全部路径常量钉到 tmp。"""
    main = tmp_path / "main"
    (main / ".runtime" / "locks").mkdir(parents=True)
    (main / "config").mkdir(parents=True)
    (main / "config" / "flags.yaml").write_text(
        "flags:\n  git_operations:\n    enabled: true\n    regen_scope: any_worktree\n", encoding="utf-8"
    )
    for attr, val in (
        ("_REPO_ROOT", tmp_path / "wt"),
        ("_MAIN_ROOT", main),
        ("_IS_WORKTREE_CTX", True),
        ("_REGISTRY_YAML", tmp_path / "gen_reg.yaml"),
        ("_ORCHESTRATOR", main / "scripts" / "governance" / "reconcile_generators.py"),
        ("_LOCK_FILE", main / ".runtime" / "locks" / "reconcile_stale.pid"),
        ("_DIRTY_DIR", main / ".runtime" / "derived_dirty"),
        ("_LEDGER_FILE", main / ".runtime" / "derived_dirty" / "ledger.jsonl"),
        ("_PENDING_RERUN", main / ".runtime" / "derived_dirty" / "pending_rerun"),
        ("_committed_yaml_files", lambda: ["docs/_registry/catalogs/fake_input.yaml"]),
        ("_generator_yaml_inputs", lambda: {"docs/_registry/catalogs/fake_input.yaml"}),
        ("_generator_yaml_outputs", lambda: set()),
    ):
        monkeypatch.setattr(pcr, attr, val)
    spawns: list[list] = []

    def fake_popen(*args, **kwargs):  # noqa: ANN002, ANN003 — 记数桩
        spawns.append(args[0] if args else kwargs.get("args"))

    monkeypatch.setattr(pcr.subprocess, "Popen", fake_popen)
    return {"main": main, "spawns": spawns}


def _ledger_lines(main: Path) -> list[dict]:
    f = main / ".runtime" / "derived_dirty" / "ledger.jsonl"
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_skip_regenerate_still_accounts(fake_roots, monkeypatch):
    """P-3：逃生口抑制执行，不抑制记账。"""
    monkeypatch.setenv("ZEPHYR_SKIP_REGENERATE", "1")
    assert pcr.main() == 0
    assert fake_roots["spawns"] == []
    entries = _ledger_lines(fake_roots["main"])
    assert len(entries) == 1, "SKIP_REGENERATE 下意图账必须有记录（P-3）"
    assert entries[0]["ctx"] == "worktree"


def test_lock_active_debounces_and_marks_rerun(fake_roots):
    """R2b：锁活跃窗连触 5 次 → spawn=1、ledger=5、pending_rerun 落标。"""
    fake_roots["main"].joinpath(".runtime", "locks", "reconcile_stale.pid").write_text("999999\n", encoding="utf-8")
    for _ in range(5):
        assert pcr.main() == 0
    assert fake_roots["spawns"] == [], "锁活跃期不得 spawn"
    assert len(_ledger_lines(fake_roots["main"])) == 5, "每次触发都必须留意图（去抖不丢）"
    assert fake_roots["main"].joinpath(".runtime", "derived_dirty", "pending_rerun").exists()


def test_main_only_flag_suppresses_worktree_spawn(fake_roots):
    """R2a（flag 面）：main_only + worktree 语境 → 只记账不 spawn。"""
    fake_roots["main"].joinpath("config", "flags.yaml").write_text(
        "flags:\n  git_operations:\n    enabled: true\n    regen_scope: main_only\n", encoding="utf-8"
    )
    assert pcr.main() == 0
    assert fake_roots["spawns"] == []
    assert len(_ledger_lines(fake_roots["main"])) == 1


def test_default_scope_spawns_pinned_to_main(fake_roots, monkeypatch):
    """出厂 any_worktree：照旧 spawn，但 cwd/编排器钉主区（R2c 单点）。"""
    monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)
    cwd_seen: list[str] = []

    def spy_popen(args, **kwargs):  # noqa: ANN001, ANN003
        cwd_seen.append(str(kwargs.get("cwd")))
        fake_roots["spawns"].append(args)

    monkeypatch.setattr(pcr.subprocess, "Popen", spy_popen)
    assert pcr.main() == 0
    assert len(fake_roots["spawns"]) == 1
    assert cwd_seen == [str(fake_roots["main"])], "spawn cwd 必须钉主区"


def test_resolve_main_root_via_gitdir_pointer(tmp_path):
    """R2c 前置：worktree .git 指针 → 主区根。"""
    main = tmp_path / "repo"
    main_git = main / ".git"
    main_git.mkdir(parents=True)
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / ".git").write_text(f"gitdir: {main_git.as_posix()}/worktrees/w0\n", encoding="utf-8")
    assert pcr._resolve_main_root(wt) == main
    assert pcr._resolve_main_root(main) == main  # 主区原样返回


def test_resolve_main_root_fail_safe(tmp_path):
    """指针解析失败回落原值（fail-safe 不变行为）。"""
    wt = tmp_path / "broken"
    wt.mkdir()
    (wt / ".git").write_text("garbage line\n", encoding="utf-8")
    assert pcr._resolve_main_root(wt) == wt
    empty = tmp_path / "plain"
    empty.mkdir()
    assert pcr._resolve_main_root(empty) == empty
