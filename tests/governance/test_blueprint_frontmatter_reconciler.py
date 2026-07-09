# [A_test] module_id: SRC-TST-2212 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-SYNC-PANORAMA | docs/_working/2026-07-09-panorama_module_sync_engine.md | §Phase3
# [MODULE] tests.governance.test_blueprint_frontmatter_reconciler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_blueprint_frontmatter_reconciler.py — 蓝图 frontmatter 对齐单测（ARCH-056 Phase 3）"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# depgraph hint: 让 generate_project_depgraph.py AST 扫描器检测 test→module 依赖边
# 实际测试用 importlib 动态加载（scripts/ 非 Python 包），此 import 运行时必失败
try:
    from scripts.governance.d5_architecture.syncers.blueprint_frontmatter_reconciler import reconcile_blueprint_frontmatter  # noqa: F401
except ImportError:
    pass

_SCRIPT_PATH = (Path(__file__).resolve().parents[2] /
                "scripts" / "governance" / "d5_architecture" / "syncers" /
                "blueprint_frontmatter_reconciler.py")


@pytest.fixture(scope="module")
def bfr():
    spec = importlib.util.spec_from_file_location("bfr_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mock_depgraph_conn(fetchone_result):
    """构造 mock depgraph 连接。

    同时设置 fetchone 和 fetchall，兼容 LIMIT 1 和聚合查询两种模式。
    fetchall 返回 [fetchone_result]（单行列表），fetchone_result=None 时返回 []。
    """
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone_result
    cursor.fetchall.return_value = [fetchone_result] if fetchone_result else []
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn


class TestReconcileBlueprint:
    def test_updates_frontmatter_core_fields(self, bfr, tmp_path, monkeypatch):
        """depgraph 核心字段 → blueprint.md frontmatter 写入"""
        bp = tmp_path / "blueprint.md"
        bp.write_text(
            "---\nmodule_id: MOD-TEST\nstatus: Active\nresponsibility_domain: old_domain\n"
            "---\n# Test\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-TEST", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-TEST") == 0
        content = bp.read_text(encoding="utf-8")
        assert "D_NEW" in content

    def test_no_blueprint_skip(self, bfr, tmp_path, monkeypatch):
        """蓝图路径为空 → 自动创建命名约定蓝图（exit 0）"""
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOBP", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": "",
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", tmp_path)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOBP") == 0
        # 验证文件被创建在 tmp_path 下（非真实项目目录）
        assert (tmp_path / "docs" / "03_modules" / "MOD-NOBP.md").exists()

    def test_module_not_in_depgraph(self, bfr, monkeypatch):
        """模块不在 depgraph → exit 3"""
        conn = _mock_depgraph_conn(None)
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-MISSING") == 3

    def test_blueprint_file_not_exist_auto_create(self, bfr, tmp_path, monkeypatch):
        """蓝图路径不为空但文件不存在 → 自动创建最小蓝图（exit 0）"""
        bp_path = tmp_path / "new_module" / "blueprint.md"
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NEW", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(bp_path),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NEW") == 0
        # 文件应被创建
        assert bp_path.exists()
        content = bp_path.read_text(encoding="utf-8")
        # 验证 frontmatter 4 核心字段
        assert "module_id: MOD-NEW" in content
        assert "responsibility_domain: D_TEST" in content
        assert "design_maturity: design" in content
        assert "build_status: planned" in content

    def test_blueprint_path_no_extension_adds_md(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 无扩展名 → 自动补 .md 创建（DCR-005 合规）"""
        # depgraph 中 blueprint_path 无扩展名（如 docs/03_modules/MOD-XXX/）
        bp_path_no_ext = tmp_path / "docs" / "03_modules" / "MOD-NOEXT"
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOEXT", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(bp_path_no_ext),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", tmp_path)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOEXT") == 0
        # 应创建 .md 文件而非无扩展名文件
        expected = tmp_path / "docs" / "03_modules" / "MOD-NOEXT.md"
        assert expected.exists()
        assert not bp_path_no_ext.exists()  # 无扩展名文件不应存在

    def test_updates_design_maturity_if_present(self, bfr, tmp_path, monkeypatch):
        """frontmatter 有 design_maturity 字段时更新"""
        bp = tmp_path / "blueprint.md"
        bp.write_text(
            "---\nmodule_id: MOD-TEST\ndesign_maturity: old\n---\n# Test\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-TEST", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-TEST") == 0
        content = bp.read_text(encoding="utf-8")
        assert "design_maturity: production" in content

    def test_no_frontmatter_skip(self, bfr, tmp_path, monkeypatch):
        """蓝图无 frontmatter → 跳过写入（exit 0）"""
        bp = tmp_path / "blueprint.md"
        bp.write_text("# Just a title\nNo frontmatter here\n", encoding="utf-8")
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOFM", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOFM") == 0
        # 内容不应改变
        assert bp.read_text(encoding="utf-8") == "# Just a title\nNo frontmatter here\n"

    def test_blueprint_path_empty_uses_naming_convention(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 为空但 docs/03_modules/<module_id>.md 存在 → 更新该文件"""
        # 模拟 _REPO_ROOT/docs/03_modules/MOD-FALLBACK.md
        repo_root = tmp_path
        modules_dir = repo_root / "docs" / "03_modules"
        modules_dir.mkdir(parents=True)
        bp_file = modules_dir / "MOD-FALLBACK.md"
        bp_file.write_text(
            "---\nmodule_id: MOD-FALLBACK\nresponsibility_domain: D_OLD\n---\n# Test\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-FALLBACK", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": "",  # 空路径
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", repo_root)
        assert bfr.reconcile_blueprint_frontmatter("MOD-FALLBACK") == 0
        content = bp_file.read_text(encoding="utf-8")
        assert "responsibility_domain: D_NEW" in content

    def test_blueprint_path_empty_and_no_convention_file_auto_create(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 为空且命名约定路径不存在 → 自动创建最小蓝图（exit 0）"""
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOPATH", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": "",
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", tmp_path)
        result = bfr.reconcile_blueprint_frontmatter("MOD-NOPATH")
        assert result == 0
        # 验证文件被自动创建
        bp_file = tmp_path / "docs" / "03_modules" / "MOD-NOPATH.md"
        assert bp_file.exists(), "最小蓝图应被自动创建"
        content = bp_file.read_text(encoding="utf-8")
        assert "module_id: MOD-NOPATH" in content
        assert "responsibility_domain: D_TEST" in content
        assert "design_maturity: design" in content
        assert "build_status: planned" in content
