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
    """构造 mock depgraph 连接。"""
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone_result
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

    def test_no_blueprint_skip(self, bfr, monkeypatch):
        """蓝图路径为空 → 跳过（exit 0）"""
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOBP", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": "",
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOBP") == 0

    def test_module_not_in_depgraph(self, bfr, monkeypatch):
        """模块不在 depgraph → exit 3"""
        conn = _mock_depgraph_conn(None)
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-MISSING") == 3

    def test_blueprint_file_not_exist_skip(self, bfr, monkeypatch):
        """蓝图路径不为空但文件不存在 → 跳过（exit 0）"""
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-GHOST", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": "/nonexistent/path/blueprint.md",
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-GHOST") == 0

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
