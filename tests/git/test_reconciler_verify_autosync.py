# [BLUEPRINT] MOD-INF-005 | tests/git/test_reconciler_verify_autosync.py | §reconciler-verify-autosync-tests
# [MODULE] tests.git.test_reconciler_verify_autosync
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.git_commit; zephyr.governance.audit.workspace_hygiene_reconciler
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，禁止污染生产 depgraph/governance.db
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_reconciler_verify_autosync.py — --reconciler-verify auto-sync 产物豁免测试。

治本 2026-07-24 (#ARCH-RECONCILER-VERIFY-AUTOSYNC-001): --reconciler-verify 模式要求主工作区
clean，但后台进程（scanner/classifier/telemetry）持续更新 auto-sync 产物，导致误阻断。
修复后 auto-sync 产物被豁免——仅非派生文件的未提交变更才阻断。

覆盖:
1. auto-sync 产物单独修改 → 放行（return None）+ [RECONCILER-VERIFY] 标记追加
2. 真实代码修改 → 阻断（return 1）
3. auto-sync + 真实代码混合 → 阻断（真实代码是阻断源）
4. 工作区 clean → 放行
5. registry catalog 派生产物（rule_catalog_registry.yaml）→ 放行（验证分类器复用而非仅前缀）

测试隔离: 所有测试用 tmp_path 临时 git 仓库，不污染生产库。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.git_commit import _validate_reconciler_verify  # noqa: E402


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_clean_repo(repo_dir: Path) -> None:
    """在 tmp_path 初始化一个最小 git 仓库（含初始 commit）。

    仅用于测 _validate_reconciler_verify 的条件1（工作区 clean 检查），
    不需要 fail-closed gate stub——本测试不触发完整 commit 流程。
    """
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _make_args(allow_concurrent: bool = True) -> SimpleNamespace:
    """构造 _validate_reconciler_verify 所需的 args 对象。

    allow_concurrent=True 跳过条件2（活跃 session 检查），隔离测试条件1（clean 检查）。
    allow_overlap=False（与 reconciler-verify 互斥，正常路径）。
    """
    return SimpleNamespace(
        reconciler_verify=True,
        allow_concurrent=allow_concurrent,
        allow_overlap=False,
        claim_only=False,
        release_only=False,
    )


def _commit_file(repo_dir: Path, rel_path: str, content: str) -> None:
    """创建并 commit 一个文件（建立 HEAD 基线）。"""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "--", rel_path], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {rel_path}", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _modify_file(repo_dir: Path, rel_path: str, content: str) -> None:
    """修改已 commit 的文件（产生未提交变更）。"""
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# 测试用例
# ---------------------------------------------------------------------------
def test_autosync_only_passes(tmp_path: Path) -> None:
    """auto-sync 产物单独修改 → 放行 + [RECONCILER-VERIFY] 标记追加。"""
    repo = tmp_path / "repo"
    _init_clean_repo(repo)
    _commit_file(repo, "data/asset_index/unified-asset-index.yaml", "initial: v1\n")
    _modify_file(repo, "data/asset_index/unified-asset-index.yaml", "initial: v2\n")

    exit_code, msg = _validate_reconciler_verify(
        _make_args(), is_pure_claim=False, message="test msg", project_root=str(repo)
    )
    assert exit_code is None, f"auto-sync-only should pass, got exit_code={exit_code}"
    assert "[RECONCILER-VERIFY]" in msg, f"marker should be appended, got msg={msg!r}"


def test_real_code_blocks(tmp_path: Path) -> None:
    """真实代码修改 → 阻断（return 1）。"""
    repo = tmp_path / "repo"
    _init_clean_repo(repo)
    _commit_file(repo, "src/zephyr/foo.py", "x = 1\n")
    _modify_file(repo, "src/zephyr/foo.py", "x = 2\n")

    exit_code, msg = _validate_reconciler_verify(
        _make_args(), is_pure_claim=False, message="test msg", project_root=str(repo)
    )
    assert exit_code == 1, f"real code should block, got exit_code={exit_code}"
    assert "[RECONCILER-VERIFY]" not in msg


def test_mixed_autosync_and_real_blocks(tmp_path: Path) -> None:
    """auto-sync + 真实代码混合 → 阻断（真实代码是阻断源）。"""
    repo = tmp_path / "repo"
    _init_clean_repo(repo)
    _commit_file(repo, "data/asset_index/unified-asset-index.yaml", "v1\n")
    _commit_file(repo, "src/zephyr/bar.py", "y = 1\n")
    _modify_file(repo, "data/asset_index/unified-asset-index.yaml", "v2\n")
    _modify_file(repo, "src/zephyr/bar.py", "y = 2\n")

    exit_code, msg = _validate_reconciler_verify(
        _make_args(), is_pure_claim=False, message="test msg", project_root=str(repo)
    )
    assert exit_code == 1, f"mixed should block (real code present), got exit_code={exit_code}"


def test_clean_workspace_passes(tmp_path: Path) -> None:
    """工作区 clean → 放行。"""
    repo = tmp_path / "repo"
    _init_clean_repo(repo)
    _commit_file(repo, "data/asset_index/unified-asset-index.yaml", "v1\n")

    exit_code, msg = _validate_reconciler_verify(
        _make_args(), is_pure_claim=False, message="test msg", project_root=str(repo)
    )
    assert exit_code is None, f"clean workspace should pass, got exit_code={exit_code}"
    assert "[RECONCILER-VERIFY]" in msg


def test_registry_catalog_autosync_passes(tmp_path: Path) -> None:
    """registry catalog 派生产物 → 放行（验证复用 _is_auto_sync_product 而非仅前缀匹配）。

    回归 #ARCH-RECONCILER-VERIFY-AUTOSYNC-001: 原实现仅 import _AUTO_SYNC_PREFIXES 做前缀
    匹配，漏掉 registry catalogs 后缀分类，导致 rule_catalog_registry.yaml 误阻断。
    """
    repo = tmp_path / "repo"
    _init_clean_repo(repo)
    _commit_file(
        repo,
        "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
        "initial: v1\n",
    )
    _modify_file(
        repo,
        "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
        "initial: v2\n",
    )

    exit_code, msg = _validate_reconciler_verify(
        _make_args(), is_pure_claim=False, message="test msg", project_root=str(repo)
    )
    assert exit_code is None, f"registry catalog autosync should pass (classifier reuse), got exit_code={exit_code}"
    assert "[RECONCILER-VERIFY]" in msg


def test_non_autosync_yaml_in_catalogs_blocks(tmp_path: Path) -> None:
    """registry catalogs 下非派生 yaml → 阻断（验证后缀分类精度，不误放行）。"""
    repo = tmp_path / "repo"
    _init_clean_repo(repo)
    _commit_file(
        repo,
        "docs/01_policies_and_standards/_registry/catalogs/some_manual.yaml",
        "v1\n",
    )
    _modify_file(
        repo,
        "docs/01_policies_and_standards/_registry/catalogs/some_manual.yaml",
        "v2\n",
    )

    exit_code, msg = _validate_reconciler_verify(
        _make_args(), is_pure_claim=False, message="test msg", project_root=str(repo)
    )
    assert exit_code == 1, f"non-autosync yaml in catalogs should block, got exit_code={exit_code}"
