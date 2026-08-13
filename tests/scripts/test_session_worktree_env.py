# [MODULE] tests.scripts.test_session_worktree_env
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts.session_worktree
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 环境三件套幂等；单步失败不阻断其余步骤
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] permanent
"""session_worktree 环境三件套单测（#ARCH-WORKTREE-ENV-001 P2-8）。

覆盖 _provision_worktree_env 的三步备置：PG 配置复制 / lookup_audit 初始化 /
activate_env.ps1 生成，以及主仓 PG 配置缺失时的降级告警路径。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# scripts/ 非包目录，按路径加载被测模块（对标 tests/scripts/ 既有惯例）
_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "session_worktree.py"


def _load_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """加载 session_worktree 并把 REPO_ROOT/WORKTREE_ROOT 重定向到临时树。"""
    spec = importlib.util.spec_from_file_location("session_worktree_under_test", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # 隔离 zephyr 依赖：_provision_worktree_env 不触达，但模块顶层有 import
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    repo = tmp_path / "repo"
    (repo / "config").mkdir(parents=True)
    monkeypatch.setattr(mod, "REPO_ROOT", repo)
    monkeypatch.setattr(mod, "WORKTREE_ROOT", repo / ".worktrees")
    return mod, repo


def test_provision_happy_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """三件套齐备：PG 配置内容一致 + 审计目录存在 + 激活脚本含 PYTHONPATH。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    (repo / "config" / ".env.postgres").write_text("PGHOST=localhost\n", encoding="utf-8")
    wt = repo / ".worktrees" / "AI-T-001"
    wt.mkdir(parents=True)

    notes = mod._provision_worktree_env(wt)

    assert (wt / "config" / ".env.postgres").read_text(encoding="utf-8") == "PGHOST=localhost\n"
    assert (wt / ".runtime" / "lookup_audit").is_dir()
    activate = (wt / "activate_env.ps1").read_text(encoding="utf-8")
    assert f"$env:PYTHONPATH = '{wt}\\src'" in activate
    assert not any(n.startswith("WARN") for n in notes)


def test_provision_degrades_when_pg_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """主仓无 PG 配置：仅告警，其余两件套照常备置（环境治理不挡施工）。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    wt = repo / ".worktrees" / "AI-T-002"
    wt.mkdir(parents=True)

    notes = mod._provision_worktree_env(wt)

    assert not (wt / "config" / ".env.postgres").exists()
    assert (wt / ".runtime" / "lookup_audit").is_dir()
    assert (wt / "activate_env.ps1").exists()
    assert any("PG" in n and n.startswith("WARN") for n in notes)


def test_provision_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """重复执行幂等：不报错、内容不漂移。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    (repo / "config" / ".env.postgres").write_text("PGHOST=localhost\n", encoding="utf-8")
    wt = repo / ".worktrees" / "AI-T-003"
    wt.mkdir(parents=True)

    mod._provision_worktree_env(wt)
    notes = mod._provision_worktree_env(wt)

    assert (wt / "config" / ".env.postgres").exists()
    assert not any(n.startswith("WARN") for n in notes)
