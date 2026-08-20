# [A_test] module_id: SRC-TST-2711 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | docs/01_policies_and_standards/policies/workspace_governance_policy.md | §ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002
# [MODULE] tests.governance.audit.test_workspace_hygiene_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_workspace_hygiene_reconciler.py — 工作区卫生自动清理 reconciler 单测。

ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002 消除（2026-07-20）。

测试 make_workspace_hygiene_reconciler 工厂函数：
- factory 返回正确 ReconcilerSpec（gate_id=GATE-WORKSPACE-HYGIENE, priority=890）
- trigger 永远返回 True（任何 commit 都触发）
- _is_auto_sync_product 前缀匹配（含新增 data/audit-trail/, data/cache/,
  docs/02_enterprise_architecture/00_overview_entry/）
- _parse_porcelain 解析 git status --porcelain 输出（跳过 ??/D/R/A）
- _git_status_porcelain fail-open（失败/超时返回空列表）
- reconcile: skip / clean / warn 判定 + 永不抛异常 + 使用 GitCommandBatcher.git_restore_batch
  （GIT-BUDGET-INV-002 合规：N 文件 = 1 subprocess，不逐个重试）

测试隔离：用 tmp_path + mock + 真实 git 仓库（end-to-end）。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec  # noqa: E402
from zephyr.governance.audit.workspace_hygiene_reconciler import (  # noqa: E402
    _AUTO_SYNC_PREFIXES,
    _GATE_ID,
    _PRIORITY,
    _git_status_porcelain,
    _is_auto_sync_product,
    _parse_porcelain,
    make_workspace_hygiene_reconciler,
)

# ============================================================================
# 辅助函数
# ============================================================================


def _git_env() -> dict:
    """构造 git 测试环境变量。"""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    return env


def _init_git_repo(repo_dir: Path) -> None:
    """初始化最小 git 仓库（含初始 commit）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = _git_env()
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    # 禁用 autocrlf——避免 Windows 上 git 自动将 \n 转 \r\n 导致内容比对失败
    subprocess.run(
        ["git", "config", "core.autocrlf", "false"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    (repo_dir / "README.md").write_bytes(b"init\n")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _commit_file(repo_dir: Path, path: str, content: str) -> None:
    """创建/修改文件并 commit 到 HEAD。"""
    env = _git_env()
    fpath = repo_dir / path
    fpath.parent.mkdir(parents=True, exist_ok=True)
    # 使用 write_bytes 避免 Windows write_text 的 \n→\r\n 自动转换
    fpath.write_bytes(content.encode("utf-8"))
    subprocess.run(["git", "add", path], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {path}"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root。"""

    def __init__(self, project_root: Path):
        self.project_root = project_root


# ============================================================================
# 工厂函数测试
# ============================================================================


class TestFactorySpec:
    """make_workspace_hygiene_reconciler 工厂返回值测试。"""

    def test_factory_returns_spec(self, tmp_path):
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)
        assert spec.gate_id == _GATE_ID == "GATE-WORKSPACE-HYGIENE"
        assert spec.priority == _PRIORITY == 890
        assert callable(spec.trigger)
        assert callable(spec.reconcile)

    def test_trigger_always_true(self, tmp_path):
        # 任何 commit 都触发——工作区卫生是全局关注
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        assert spec.trigger([]) is True
        assert spec.trigger(["src/foo.py"]) is True
        assert spec.trigger(["docs/anything.md"]) is True


# ============================================================================
# _is_auto_sync_product 前缀匹配测试
# ============================================================================


class TestIsAutoSyncProduct:
    """_is_auto_sync_product 路径匹配测试。

    验证 workspace_governance_policy.md §2.1 派生的 auto-sync 产物路径正确匹配。
    特别验证新增的 3 个路径：
    - data/audit-trail/
    - data/cache/
    - docs/02_enterprise_architecture/00_overview_entry/
    """

    def test_prefix_match_audit_trail_dir(self):
        # 新增 auto-sync 路径：data/audit-trail/
        assert _is_auto_sync_product("data/audit-trail/2026-07-20.jsonl") is True
        assert _is_auto_sync_product("data/audit-trail/subdir/file.json") is True

    def test_prefix_match_cache_dir(self):
        # 新增 auto-sync 路径：data/cache/
        assert _is_auto_sync_product("data/cache/index.json") is True
        assert _is_auto_sync_product("data/cache/sub/dir/data.bin") is True

    def test_prefix_match_overview_entry_dir(self):
        # 新增 auto-sync 路径：docs/02_enterprise_architecture/00_overview_entry/
        assert _is_auto_sync_product("docs/02_enterprise_architecture/00_overview_entry/index.md") is True
        assert _is_auto_sync_product("docs/02_enterprise_architecture/00_overview_entry/sub/file.yaml") is True

    def test_prefix_match_generated_dir(self):
        assert _is_auto_sync_product("docs/02_enterprise_architecture/generated/diagram.mmd") is True

    def test_prefix_match_domain_architecture_docs(self):
        assert _is_auto_sync_product("docs/02_enterprise_architecture/02_domain_architecture_docs/d_foo.md") is True

    def test_prefix_match_full_project_tree(self):
        assert (
            _is_auto_sync_product(
                "docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_root.txt"
            )
            is True
        )

    def test_prefix_match_telemetry_dir(self):
        assert _is_auto_sync_product("data/telemetry/dev/metrics.jsonl") is True
        assert _is_auto_sync_product("data/telemetry/blueprint_reads.jsonl") is True

    def test_prefix_match_runtime_violation_snapshot(self):
        assert _is_auto_sync_product("data/runtime_violation_snapshot/latest.json") is True

    def test_prefix_match_reports(self):
        assert _is_auto_sync_product("data/reports/dashboard.json") is True
        assert _is_auto_sync_product("data/reports/reconciliation-report.md") is True

    def test_prefix_match_asset_index(self):
        assert _is_auto_sync_product("data/asset_index/unified-asset-index.yaml") is True

    def test_prefix_match_scans(self):
        assert _is_auto_sync_product("data/scans/raw-asset-scan.json") is True

    def test_prefix_match_architecture_health(self):
        assert _is_auto_sync_product("data/architecture_health/latest.json") is True

    def test_prefix_match_classified(self):
        assert _is_auto_sync_product("data/classified/classified-assets.json") is True

    def test_prefix_match_budget(self):
        assert _is_auto_sync_product("data/budget/shutdown_snapshot.json") is True

    def test_prefix_match_metrics(self):
        assert _is_auto_sync_product("data/metrics/kill_switch_probes.jsonl") is True

    def test_prefix_match_scripts_governance(self):
        # rules_integrity_db.json 已移除出 auto-sync（2026-08-02 audit-02 治本）：
        # 该文件是 validate_rules_integrity.py --register 的写入产物（golden hash DB），
        # 列入 auto-sync 导致 register() 写入的新 hash 被 git restore 还原回 HEAD，
        # 形成"写入→还原"循环。post-flush re-register 负责提交 DB 变更。
        assert _is_auto_sync_product("scripts/governance/meta/rules_integrity_db.json") is False
        assert _is_auto_sync_product("scripts/governance/script_manifest.yaml") is True
        assert _is_auto_sync_product("scripts/script_manifest.yaml") is True

    def test_prefix_match_architecture_model(self):
        assert _is_auto_sync_product("architecture_model/index.yaml") is True

    def test_prefix_match_pg_schema_migration(self):
        assert _is_auto_sync_product("scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql") is True
        assert _is_auto_sync_product("scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql") is True

    def test_prefix_match_debt_registry(self):
        assert _is_auto_sync_product("docs/_archive/architecture_debt_registry_v2.md") is True

    def test_blueprint_md_in_modules_dir(self):
        # #ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001 (2026-07-21): blueprint.md 已从 auto-sync 清单移除
        # 原因：blueprint.md 是混合文件（frontmatter 派生 + 正文手写），文件级分类误伤正文编辑
        # frontmatter 变更由 blueprint_frontmatter_reconciler.commit_auto 自动提交，无需 auto-restore
        assert _is_auto_sync_product("docs/03_modules/_domain_foo/blueprint.md") is False
        assert _is_auto_sync_product("docs/03_modules/_cross_layer/bar/blueprint.md") is False

    def test_blueprint_md_not_in_modules_dir(self):
        # 其他目录下的 blueprint.md 不是 auto-sync 产物
        assert _is_auto_sync_product("docs/blueprint.md") is False
        assert _is_auto_sync_product("src/foo/blueprint.md") is False

    def test_blueprint_md_body_edit_not_restored(self):
        """#ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001 回归测试。

        模拟 AI 编辑 blueprint.md 正文（如迁移公告），确认 _is_auto_sync_product
        返回 False——正文编辑不被 session_worktree_start 的 _restore_auto_sync_batch 清空。
        """
        # 这些路径都是 AI 手动编辑过的 blueprint.md（迁移公告场景）
        paths = [
            "docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md",
            "docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md",
            "docs/03_modules/_domain_governance/governance_automation/blueprint.md",
            "docs/03_modules/_domain_foo/bar/blueprint.md",
        ]
        for p in paths:
            assert _is_auto_sync_product(p) is False, (
                f"blueprint.md 误判为 auto-sync：{p}——正文编辑会被 _restore_auto_sync_batch 清空"
            )

    def test_blueprint_md_regression_no_false_positive(self):
        """#ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001 回归——防误判。

        确保旧规则（L165-167 已删除）不会通过其他路径重新匹配 blueprint.md。
        验证 _AUTO_SYNC_PREFIXES 中没有匹配 docs/03_modules/ 的前缀。
        """
        # _AUTO_SYNC_PREFIXES 不应包含匹配 docs/03_modules/ 的前缀
        for prefix in _AUTO_SYNC_PREFIXES:
            assert not prefix.startswith("docs/03_modules/"), (
                f"_AUTO_SYNC_PREFIXES 误含 docs/03_modules/ 前缀：{prefix}"
            )

    def test_registry_catalogs_yaml(self):
        # 特殊规则：docs/01_policies_and_standards/_registry/catalogs/ 下的
        # rule_catalog_registry.yaml 和 registry_master_index.yaml 是 auto-sync 产物
        assert (
            _is_auto_sync_product("docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml")
            is True
        )
        assert (
            _is_auto_sync_product("docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml")
            is True
        )

    def test_registry_catalogs_other_yaml_not_matched(self):
        # 其他 YAML 不应匹配
        assert _is_auto_sync_product("docs/01_policies_and_standards/_registry/catalogs/other.yaml") is False

    def test_real_code_changes_not_matched(self):
        # 真实代码修改不应匹配（关键：避免误 restore 真实改动）
        assert _is_auto_sync_product("src/zephyr/foo.py") is False
        assert _is_auto_sync_product("tests/test_foo.py") is False
        assert _is_auto_sync_product("docs/02_enterprise_architecture/my_design.md") is False

    def test_unrelated_data_dir_not_matched(self):
        # data/ 下非 auto-sync 路径不匹配
        assert _is_auto_sync_product("data/other/file.json") is False
        assert _is_auto_sync_product("data/foo.yaml") is False


# ============================================================================
# _parse_porcelain 测试
# ============================================================================


class TestParsePorcelain:
    """_parse_porcelain 解析 git status --porcelain 输出测试。"""

    def test_empty_output(self):
        assert _parse_porcelain("") == []

    def test_parse_modified_worktree(self):
        # " M" = worktree modified
        output = " M src/foo.py\n M src/bar.py\n"
        result = _parse_porcelain(output)
        assert set(result) == {"src/foo.py", "src/bar.py"}

    def test_parse_modified_staged(self):
        # "M " = staged modified
        output = "M  src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_parse_modified_both(self):
        # "MM" = staged + worktree modified
        output = "MM src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_skip_untracked(self):
        # "??" = untracked，应跳过
        output = "?? src/untracked.py\n M src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_skip_deleted(self):
        # " D" = deleted，应跳过
        output = " D src/deleted.py\n M src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_skip_renamed(self):
        # "R" = renamed，应跳过
        output = "R  src/old.py -> src/new.py\n M src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_skip_added(self):
        # "A " = added，应跳过（新增文件不是 auto-sync 产物）
        output = "A  src/added.py\n M src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_handle_windows_backslash_paths(self):
        # Windows 上 git status 可能输出反斜杠路径
        output = " M src\\zephyr\\foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/zephyr/foo.py"]

    def test_handle_crlf_line_endings(self):
        # Windows CRLF 兼容
        output = " M src/foo.py\r\n M src/bar.py\r\n"
        result = _parse_porcelain(output)
        assert set(result) == {"src/foo.py", "src/bar.py"}

    def test_skip_short_lines(self):
        # 短行（<4 字符）跳过
        output = "ab\n M src/foo.py\n"
        result = _parse_porcelain(output)
        assert result == ["src/foo.py"]

    def test_handle_quoted_paths(self):
        # 含特殊字符的路径会被引号包裹
        output = ' M "src/with space.py"\n'
        result = _parse_porcelain(output)
        assert result == ["src/with space.py"]


# ============================================================================
# _git_status_porcelain 测试
# ============================================================================


class TestGitStatusPorcelain:
    """_git_status_porcelain fail-open 测试。"""

    def test_returns_modified_files(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        # 修改但未 stage
        (tmp_path / "src" / "foo.py").write_text("v2\n", encoding="utf-8")
        result = _git_status_porcelain(str(tmp_path))
        assert "src/foo.py" in result

    def test_returns_empty_when_clean(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        # 无修改
        result = _git_status_porcelain(str(tmp_path))
        assert result == []

    def test_failed_git_status_returns_empty(self, tmp_path):
        # 非 git 仓库 → git status 失败 → 返回空列表（fail-open）
        # 注意：必须用 tmp_path 下的子目录，避免 tmp_path 本身落在主仓库内
        # （--basetemp 可能指向仓库内路径，导致 git status 命中主仓库）
        result = _git_status_porcelain(str(tmp_path / "nonexistent_subdir"))
        assert result == []

    def test_timeout_returns_empty(self, tmp_path):
        _init_git_repo(tmp_path)
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            result = _git_status_porcelain(str(tmp_path))
        assert result == []

    def test_generic_exception_returns_empty(self, tmp_path):
        _init_git_repo(tmp_path)
        with patch("subprocess.run", side_effect=OSError("disk full")):
            result = _git_status_porcelain(str(tmp_path))
        assert result == []


# ============================================================================
# reconcile 测试
# ============================================================================


class TestReconcile:
    """reconcile 主函数测试。"""

    def test_skip_when_workspace_clean(self, tmp_path):
        # 无 modified 文件 → skip
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile(["src/foo.py"], "test-session")
        assert result.action == "skip"
        assert "clean" in result.detail.lower()
        assert result.gate_id == _GATE_ID

    def test_reconcile_restores_new_auto_sync_paths(self, tmp_path):
        # e2e: 验证新增的 3 个 auto-sync 路径能被正确 restore
        # （data/audit-trail/, data/cache/, docs/02_enterprise_architecture/00_overview_entry/）
        _init_git_repo(tmp_path)
        # 创建 auto-sync 产物文件并 commit
        auto_sync_files = [
            "data/audit-trail/2026-07-20.jsonl",
            "data/cache/index.json",
            "docs/02_enterprise_architecture/00_overview_entry/overview.md",
            "data/telemetry/dev/metrics.jsonl",
        ]
        for path in auto_sync_files:
            _commit_file(tmp_path, path, "v1\n")
        # 修改这些 auto-sync 产物
        for path in auto_sync_files:
            (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / path).write_text("v2-modified\n", encoding="utf-8")
        # 验证 git status 看到修改
        modified = _git_status_porcelain(str(tmp_path))
        assert set(modified) == set(auto_sync_files)
        # 执行 reconcile
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile(auto_sync_files, "test-session")
        # 应该是 clean（auto-sync 产物已 restore）
        assert result.action == "clean", f"expected clean, got {result.action}: {result.detail}"
        assert "restored" in result.detail
        # 验证文件被还原到 HEAD 版本
        for path in auto_sync_files:
            content = (tmp_path / path).read_text(encoding="utf-8")
            assert content == "v1\n", f"{path} not restored: {content!r}"

    def test_reconcile_warn_when_restore_fails(self, tmp_path):
        # mock git_restore_batch 返回空列表（模拟 restore 失败）→ warn
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "data/telemetry/dev/metrics.jsonl", "v1\n")
        # 修改 auto-sync 产物
        (tmp_path / "data" / "telemetry" / "dev" / "metrics.jsonl").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "data" / "telemetry" / "dev" / "metrics.jsonl").write_text("v2-modified\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        # 必须在 patch 上下文内创建 spec，否则 factory 会创建真实 GitCommandBatcher 实例
        # （patch 类对已创建的实例无效）
        with patch("zephyr.governance.audit.workspace_hygiene_reconciler.GitCommandBatcher") as mock_batcher_cls:
            mock_batcher = mock_batcher_cls.return_value
            mock_batcher.git_restore_batch.return_value = []
            spec = make_workspace_hygiene_reconciler(gw)
            result = spec.reconcile(["data/telemetry/dev/metrics.jsonl"], "test-session")
        # restore 失败 → warn
        assert result.action == "warn"
        assert "failed" in result.detail.lower() or "restore" in result.detail.lower()
        assert result.gate_id == _GATE_ID

    def test_reconcile_warn_when_real_changes(self, tmp_path):
        # 真实代码修改 → warn（不自动处理）
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        # 修改真实代码文件
        (tmp_path / "src" / "foo.py").write_text("v2-modified\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile(["src/foo.py"], "test-session")
        # 真实代码修改 → warn
        assert result.action == "warn"
        assert "non-auto-sync" in result.detail.lower() or "real" in result.detail.lower()
        # 真实代码文件不应被 restore
        content = (tmp_path / "src" / "foo.py").read_text(encoding="utf-8")
        assert content == "v2-modified\n"

    def test_reconcile_clean_when_only_auto_sync_restored(self, tmp_path):
        # 仅 auto-sync 产物 + restore 成功 → clean
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "data/reports/dashboard.json", '{"v":1}\n')
        (tmp_path / "data" / "reports").mkdir(parents=True, exist_ok=True)
        (tmp_path / "data" / "reports" / "dashboard.json").write_text('{"v":2}\n', encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile(["data/reports/dashboard.json"], "test-session")
        assert result.action == "clean"
        assert "restored" in result.detail
        # 文件被还原
        content = (tmp_path / "data" / "reports" / "dashboard.json").read_text(encoding="utf-8")
        assert content == '{"v":1}\n'

    def test_reconcile_warn_when_both_auto_sync_and_real_changes(self, tmp_path):
        # 同时有 auto-sync + 真实代码修改 → restore auto-sync + warn 真实代码修改
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "data/telemetry/dev/metrics.jsonl", "v1\n")
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        # 修改两类文件
        (tmp_path / "data" / "telemetry" / "dev").mkdir(parents=True, exist_ok=True)
        (tmp_path / "data" / "telemetry" / "dev" / "metrics.jsonl").write_text("v2-auto\n", encoding="utf-8")
        (tmp_path / "src" / "foo.py").write_text("v2-real\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile(["data/telemetry/dev/metrics.jsonl", "src/foo.py"], "test-session")
        # 有真实代码修改 → warn
        assert result.action == "warn"
        assert "non-auto-sync" in result.detail.lower() or "real" in result.detail.lower()
        assert "restored" in result.detail  # auto-sync 仍被 restore
        # auto-sync 文件被还原
        auto_content = (tmp_path / "data" / "telemetry" / "dev" / "metrics.jsonl").read_text(encoding="utf-8")
        assert auto_content == "v1\n"
        # 真实代码文件不被还原
        real_content = (tmp_path / "src" / "foo.py").read_text(encoding="utf-8")
        assert real_content == "v2-real\n"

    def test_reconcile_never_raises_on_exception(self, tmp_path):
        # 异常降级为 warn（reconciler 永不抛异常）
        gw = _FakeGateway(tmp_path)
        spec = make_workspace_hygiene_reconciler(gw)
        # mock _git_status_porcelain 抛异常——必须 patch 私有名 _git_status_porcelain
        # （_reconcile 调用的是私有函数，patch 公共别名 git_status_porcelain 无效）
        with patch(
            "zephyr.governance.audit.workspace_hygiene_reconciler._git_status_porcelain",
            side_effect=RuntimeError("simulated failure"),
        ):
            result = spec.reconcile(["any"], "test-session")
        # 异常 → warn（不抛出）
        assert result.action == "warn"
        assert "error" in result.detail.lower() or "fail" in result.detail.lower()
        assert result.gate_id == _GATE_ID


# ============================================================================
# GIT-BUDGET-INV-002 合规性测试
# ============================================================================


class TestGitBudgetCompliance:
    """GIT-BUDGET-INV-002 合规性验证：N 文件 = 1 subprocess。"""

    def test_reconcile_uses_git_restore_batch(self, tmp_path):
        # 验证 reconcile 调用 batcher.git_restore_batch（而非逐文件 subprocess）
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "data/telemetry/dev/metrics.jsonl", "v1\n")
        (tmp_path / "data" / "telemetry" / "dev").mkdir(parents=True, exist_ok=True)
        (tmp_path / "data" / "telemetry" / "dev" / "metrics.jsonl").write_text("v2\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        # 必须在 patch 上下文内创建 spec，否则 factory 会创建真实 GitCommandBatcher 实例
        with patch("zephyr.governance.audit.workspace_hygiene_reconciler.GitCommandBatcher") as mock_batcher_cls:
            mock_batcher = mock_batcher_cls.return_value
            mock_batcher.git_restore_batch.return_value = ["data/telemetry/dev/metrics.jsonl"]
            spec = make_workspace_hygiene_reconciler(gw)
            result = spec.reconcile(["data/telemetry/dev/metrics.jsonl"], "test-session")
        # 验证 git_restore_batch 被调用一次（批量，非逐个）
        assert mock_batcher.git_restore_batch.call_count == 1
        # 验证传入的是文件列表（非单个文件）
        call_args = mock_batcher.git_restore_batch.call_args
        files_arg = call_args[0][0]  # 第一个位置参数
        assert isinstance(files_arg, list)
        assert "data/telemetry/dev/metrics.jsonl" in files_arg
        assert result.action == "clean"

    def test_no_individual_retry_on_batch_failure(self, tmp_path):
        # 关键：批量失败时不逐个重试（GIT-BUDGET-INV-002 反模式）
        _init_git_repo(tmp_path)
        # 创建 3 个 auto-sync 产物并修改
        files = [
            "data/telemetry/dev/metrics.jsonl",
            "data/telemetry/blueprint_reads.jsonl",
            "data/cache/index.json",
        ]
        for f in files:
            _commit_file(tmp_path, f, "v1\n")
            (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / f).write_text("v2\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        # 必须在 patch 上下文内创建 spec，否则 factory 会创建真实 GitCommandBatcher 实例
        with patch("zephyr.governance.audit.workspace_hygiene_reconciler.GitCommandBatcher") as mock_batcher_cls:
            mock_batcher = mock_batcher_cls.return_value
            mock_batcher.git_restore_batch.return_value = []
            spec = make_workspace_hygiene_reconciler(gw)
            result = spec.reconcile(files, "test-session")
        # 验证 git_restore_batch 只被调用一次（不逐个重试）
        assert mock_batcher.git_restore_batch.call_count == 1
        # 批量失败 → warn
        assert result.action == "warn"


# ============================================================================
# #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001 治本测试
# ============================================================================


class _FakeBatcher:
    """模拟 BatchedAutoCommitter，仅提供 buffered_files() 方法。"""

    def __init__(self, buffered: set[str] | None = None):
        self._buffered = buffered or set()

    def buffered_files(self) -> set[str]:
        return set(self._buffered)


class TestBufferedFileExclusion:
    """#ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001 治本回归测试。

    病根：GATE-ASSET-INDEX(priority=170) bootstrap 写索引文件后 buffer() 延迟提交，
    workspace_hygiene(priority=890) 若 git restore 该文件 → flush() 时 NOTHING_TO_COMMIT，
    但 reconciler 已记 auto_committed，造成"日志说已重生实际未重生"的治理盲区。

    治本：workspace_hygiene 跳过 batcher.buffered_files() 中的文件，让 flush() 正常提交。
    """

    def test_auto_sync_skips_buffered_files(self, tmp_path):
        # buffered 中的 auto-sync 文件不应被 restore——让 flush() 正常提交
        _init_git_repo(tmp_path)
        asset_index = "data/asset_index/unified-asset-index.yaml"
        _commit_file(tmp_path, asset_index, "v1\n")
        (tmp_path / asset_index).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / asset_index).write_text("v2-regenerated\n", encoding="utf-8")
        # 验证 git status 看到修改
        assert asset_index in _git_status_porcelain(str(tmp_path))
        # gateway 带 _batcher，标记 asset_index 为 buffered
        gw = _FakeGateway(tmp_path)
        gw._batcher = _FakeBatcher(buffered={asset_index})
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile([asset_index], "test-session")
        # buffered 文件被排除后无 auto_sync_files 可 restore，也无 real_changes → clean
        # （skip 仅用于工作区完全无 modified 文件；此处有 modified 但全部被 buffer 排除）
        assert result.action == "clean", f"expected clean, got {result.action}: {result.detail}"
        # 关键：文件未被还原（仍是 v2-regenerated，等待 flush 提交）
        content = (tmp_path / asset_index).read_text(encoding="utf-8")
        assert content == "v2-regenerated\n", (
            f"buffered 文件被错误还原为 HEAD 版本：{content!r}——flush() 将 NOTHING_TO_COMMIT"
        )

    def test_mixed_buffered_and_unbuffered_auto_sync(self, tmp_path):
        # 混合场景：buffered 文件跳过，未 buffered 的 auto-sync 文件仍被 restore
        _init_git_repo(tmp_path)
        buffered_file = "data/asset_index/unified-asset-index.yaml"
        unbuffered_file = "data/reports/dashboard.json"
        for f in (buffered_file, unbuffered_file):
            _commit_file(tmp_path, f, "v1\n")
            (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / f).write_text("v2\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        gw._batcher = _FakeBatcher(buffered={buffered_file})
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile([buffered_file, unbuffered_file], "test-session")
        # 有 unbuffered auto-sync 被 restore → clean
        assert result.action == "clean"
        assert "restored" in result.detail
        # buffered 文件未被还原
        assert (tmp_path / buffered_file).read_text(encoding="utf-8") == "v2\n"
        # unbuffered 文件被还原到 HEAD
        assert (tmp_path / unbuffered_file).read_text(encoding="utf-8") == "v1\n"

    def test_no_batcher_fail_open_restores_all(self, tmp_path):
        # gateway 无 _batcher（旧路径/降级场景）→ fail-open，所有 auto-sync 文件正常 restore
        # 这保证治本改动向后兼容，不破坏无 batcher 的调用方
        _init_git_repo(tmp_path)
        asset_index = "data/asset_index/unified-asset-index.yaml"
        _commit_file(tmp_path, asset_index, "v1\n")
        (tmp_path / asset_index).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / asset_index).write_text("v2\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)  # 无 _batcher 属性
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile([asset_index], "test-session")
        # fail-open：无 batcher → 不排除 → 正常 restore
        assert result.action == "clean"
        assert (tmp_path / asset_index).read_text(encoding="utf-8") == "v1\n"

    def test_buffered_file_with_real_change_still_warns(self, tmp_path):
        # buffered auto-sync 文件 + 真实代码修改 → warn 真实代码修改，
        # 但 buffered 文件不被 restore
        _init_git_repo(tmp_path)
        buffered_file = "data/asset_index/unified-asset-index.yaml"
        real_file = "src/foo.py"
        for f in (buffered_file, real_file):
            _commit_file(tmp_path, f, "v1\n")
        (tmp_path / buffered_file).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / buffered_file).write_text("v2-buffered\n", encoding="utf-8")
        (tmp_path / "src" / "foo.py").write_text("v2-real\n", encoding="utf-8")
        gw = _FakeGateway(tmp_path)
        gw._batcher = _FakeBatcher(buffered={buffered_file})
        spec = make_workspace_hygiene_reconciler(gw)
        result = spec.reconcile([buffered_file, real_file], "test-session")
        # 有真实代码修改 → warn
        assert result.action == "warn"
        assert "non-auto-sync" in result.detail.lower() or "real" in result.detail.lower()
        # buffered 文件未被还原
        assert (tmp_path / buffered_file).read_text(encoding="utf-8") == "v2-buffered\n"
        # 真实代码文件未被还原
        assert (tmp_path / "src" / "foo.py").read_text(encoding="utf-8") == "v2-real\n"
