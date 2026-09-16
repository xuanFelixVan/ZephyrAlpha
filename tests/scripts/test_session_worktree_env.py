# [MODULE] tests.scripts.test_session_worktree_env
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts.session_worktree
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 环境三件套幂等；单步失败不阻断其余步骤；连接配置=PG+CH 全量遍历 _CONN_ENV_FILES；source_root 优先于模块 REPO_ROOT（队列侧契约）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 自指
# [TTL] permanent
"""session_worktree 环境三件套单测（#ARCH-WORKTREE-ENV-001 P2-8）。

覆盖 _provision_worktree_env 的三步备置：连接配置复制（PG+CH）/ lookup_audit 初始化 /
activate_env.ps1 生成，主仓配置缺失时的降级告警路径，以及 source_root 显式指定
（提交队列 serializer 调用侧：import 进程的模块 REPO_ROOT 可能锚在别处）。
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


def _seed_conn_configs(repo: Path) -> None:
    """主仓两份连接配置就位（内容可区分，供逐份断言）。"""
    (repo / "config" / ".env.postgres").write_text("PGHOST=localhost\n", encoding="utf-8")
    (repo / "config" / ".env.clickhouse").write_text("CLICKHOUSE_HOST=10.0.0.9\n", encoding="utf-8")


def test_provision_happy_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """三件套齐备：PG+CH 配置内容一致 + 审计目录存在 + 激活脚本含 PYTHONPATH。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    _seed_conn_configs(repo)
    wt = repo / ".worktrees" / "AI-T-001"
    wt.mkdir(parents=True)

    notes = mod._provision_worktree_env(wt)

    assert (wt / "config" / ".env.postgres").read_text(encoding="utf-8") == "PGHOST=localhost\n"
    assert (wt / "config" / ".env.clickhouse").read_text(encoding="utf-8") == "CLICKHOUSE_HOST=10.0.0.9\n"
    assert (wt / ".runtime" / "lookup_audit").is_dir()
    activate = (wt / "activate_env.ps1").read_text(encoding="utf-8")
    assert f"$env:PYTHONPATH = '{wt}\\src'" in activate
    assert not any(n.startswith("WARN") for n in notes)


def test_provision_degrades_when_pg_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """主仓无 PG 配置：仅告警，其余两件套照常备置（环境治理不挡施工）。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    (repo / "config" / ".env.clickhouse").write_text("CLICKHOUSE_HOST=10.0.0.9\n", encoding="utf-8")
    wt = repo / ".worktrees" / "AI-T-002"
    wt.mkdir(parents=True)

    notes = mod._provision_worktree_env(wt)

    assert not (wt / "config" / ".env.postgres").exists()
    assert (wt / "config" / ".env.clickhouse").exists()
    assert (wt / ".runtime" / "lookup_audit").is_dir()
    assert (wt / "activate_env.ps1").exists()
    assert any("PG" in n and n.startswith("WARN") for n in notes)
    assert not any("CH" in n and n.startswith("WARN") for n in notes)


def test_provision_degrades_when_all_conn_configs_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PG+CH 全缺：两份都告警，且 _CONN_ENV_FILES 登记的每份都在 notes 里出现。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    wt = repo / ".worktrees" / "AI-T-004"
    wt.mkdir(parents=True)

    notes = mod._provision_worktree_env(wt)

    for cfg_name, _label in mod._CONN_ENV_FILES:
        assert not (wt / "config" / cfg_name).exists()
        assert any(n.startswith("WARN") and cfg_name in n for n in notes), cfg_name
    assert (wt / ".runtime" / "lookup_audit").is_dir()


def test_provision_uses_explicit_source_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """source_root 覆盖模块 REPO_ROOT：队列 serializer 侧调用契约（真源=主仓，非 import 锚点）。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    real = tmp_path / "real_main"
    (real / "config").mkdir(parents=True)
    (real / "config" / ".env.postgres").write_text("PGHOST=real\n", encoding="utf-8")
    (real / "config" / ".env.clickhouse").write_text("CLICKHOUSE_HOST=real\n", encoding="utf-8")
    (repo / "config" / ".env.postgres").write_text("PGHOST=fake\n", encoding="utf-8")
    wt = repo / ".worktrees" / "AI-T-005"
    wt.mkdir(parents=True)

    notes = mod._provision_worktree_env(wt, source_root=real)

    assert not any(n.startswith("WARN") for n in notes)
    assert (wt / "config" / ".env.postgres").read_text(encoding="utf-8") == "PGHOST=real\n"
    assert (wt / "config" / ".env.clickhouse").read_text(encoding="utf-8") == "CLICKHOUSE_HOST=real\n"


def test_provision_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """重复执行幂等：不报错、内容不漂移。"""
    mod, repo = _load_module(tmp_path, monkeypatch)
    _seed_conn_configs(repo)
    wt = repo / ".worktrees" / "AI-T-003"
    wt.mkdir(parents=True)

    mod._provision_worktree_env(wt)
    first = (wt / "config" / ".env.postgres").read_bytes()
    notes = mod._provision_worktree_env(wt)

    assert (wt / "config" / ".env.postgres").read_bytes() == first
    assert not any(n.startswith("WARN") for n in notes)
