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
        """蓝图路径为空且文件不存在 → 标记缺失跳过，不创建文件（exit 0）"""
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOBP", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": "",
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", tmp_path)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOBP") == 0
        # 验证文件未被创建（标记缺失，不自动创建）
        assert not (tmp_path / "docs" / "03_modules" / "MOD-NOBP.md").exists()

    def test_module_not_in_depgraph(self, bfr, monkeypatch):
        """模块不在 depgraph → exit 3"""
        conn = _mock_depgraph_conn(None)
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-MISSING") == 3

    def test_blueprint_file_not_exist_skip(self, bfr, tmp_path, monkeypatch):
        """蓝图路径不为空但文件不存在 → 标记缺失跳过，不创建文件（exit 0）"""
        bp_path = tmp_path / "new_module" / "blueprint.md"
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NEW", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(bp_path),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NEW") == 0
        # 文件不应被创建（标记缺失，不自动创建）
        assert not bp_path.exists()

    def test_blueprint_path_no_extension_adds_md(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 无扩展名 → 补 .md 后文件不存在则跳过（DCR-005 合规）"""
        bp_path_no_ext = tmp_path / "docs" / "03_modules" / "MOD-NOEXT"
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOEXT", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(bp_path_no_ext),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", tmp_path)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOEXT") == 0
        # 补 .md 后文件不存在 → 不创建
        expected = tmp_path / "docs" / "03_modules" / "MOD-NOEXT.md"
        assert not expected.exists()
        assert not bp_path_no_ext.exists()

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

    def test_blueprint_path_empty_and_no_convention_file_skip(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 为空且命名约定路径不存在 → 标记缺失跳过，不创建文件（exit 0）"""
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOPATH", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": "",
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", tmp_path)
        result = bfr.reconcile_blueprint_frontmatter("MOD-NOPATH")
        assert result == 0
        # 验证文件未被创建（标记缺失，不自动创建）
        bp_file = tmp_path / "docs" / "03_modules" / "MOD-NOPATH.md"
        assert not bp_file.exists(), "不应自动创建蓝图文件"


# ============================================================================
# 极限测试（ARCH-056 Phase 3 — edge/extreme cases）
# ============================================================================


def _mock_depgraph_conn_multi(rows):
    """构造 mock depgraph 连接（多行版本）。

    rows: list[dict] | None。None 或 [] 模拟无数据。
    fetchall 返回 rows，fetchone 返回 rows[0] 或 None。
    用于测试跨域多行聚合（多数投票/min rank/first-non-empty）。
    """
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = rows[0] if rows else None
    cursor.fetchall.return_value = rows or []
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn


class TestExtremeAggregation:
    """多行聚合极限测试——跨域/平局/全空/最design状态/first-non-empty。"""

    def test_cross_domain_majority_vote(self, bfr, tmp_path, monkeypatch):
        """D_A×2 + D_B×1 → domain_id=D_A（多数投票）"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-X\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-X", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": str(bp)},
            {"blueprint_id": "MOD-X", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "", "blueprint_path": ""},
            {"blueprint_id": "MOD-X", "domain_id": "D_B", "design_maturity": "design",
             "build_status": "", "blueprint_path": ""},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-X") == 0
        assert "responsibility_domain: D_A" in bp.read_text(encoding="utf-8")

    def test_tie_takes_first_encountered(self, bfr, tmp_path, monkeypatch):
        """平局 D_FIRST×1 + D_SECOND×1 → Counter.most_common 取第一个（按插入顺序）"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-TIE\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-TIE", "domain_id": "D_FIRST", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": str(bp)},
            {"blueprint_id": "MOD-TIE", "domain_id": "D_SECOND", "design_maturity": "production",
             "build_status": "", "blueprint_path": ""},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-TIE") == 0
        assert "responsibility_domain: D_FIRST" in bp.read_text(encoding="utf-8")

    def test_all_empty_domain_id_writes_empty(self, bfr, tmp_path, monkeypatch):
        """所有行 domain_id 为空 → responsibility_domain 写空值"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-EMPTY\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-EMPTY", "domain_id": "", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": str(bp)},
            {"blueprint_id": "MOD-EMPTY", "domain_id": "", "design_maturity": "",
             "build_status": "", "blueprint_path": ""},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-EMPTY") == 0
        content = bp.read_text(encoding="utf-8")
        # responsibility_domain 被更新为空（OLD 被替换为空）
        assert "responsibility_domain:" in content
        assert "responsibility_domain: OLD" not in content

    def test_design_maturity_takes_most_design(self, bfr, tmp_path, monkeypatch):
        """production + design + prototype → design（min rank，最保守）"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-MM\ndesign_maturity: old\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-MM", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": str(bp)},
            {"blueprint_id": "MOD-MM", "domain_id": "D_A", "design_maturity": "design",
             "build_status": "", "blueprint_path": ""},
            {"blueprint_id": "MOD-MM", "domain_id": "D_A", "design_maturity": "prototype",
             "build_status": "", "blueprint_path": ""},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-MM") == 0
        assert "design_maturity: design" in bp.read_text(encoding="utf-8")

    def test_design_maturity_unknown_value_rank99(self, bfr, tmp_path, monkeypatch):
        """未知 design_maturity 值 → rank 99，不优先于已知值 prototype(rank 1)"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-UNK\ndesign_maturity: old\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-UNK", "domain_id": "D_A", "design_maturity": "weird_value",
             "build_status": "stable", "blueprint_path": str(bp)},
            {"blueprint_id": "MOD-UNK", "domain_id": "D_A", "design_maturity": "prototype",
             "build_status": "", "blueprint_path": ""},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-UNK") == 0
        # prototype (rank 1) < weird_value (rank 99)
        assert "design_maturity: prototype" in bp.read_text(encoding="utf-8")

    def test_build_status_takes_first_non_empty(self, bfr, tmp_path, monkeypatch):
        """build_status 取第一个非空（空行在前不取，取 stable 不取 planned）"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-BS\nbuild_status: old\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-BS", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "", "blueprint_path": str(bp)},
            {"blueprint_id": "MOD-BS", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": ""},
            {"blueprint_id": "MOD-BS", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "planned", "blueprint_path": ""},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-BS") == 0
        assert "build_status: stable" in bp.read_text(encoding="utf-8")

    def test_blueprint_path_takes_first_non_empty(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 取第一个非空行（第一行空，第二行有路径）"""
        bp = tmp_path / "real_bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-BP\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-BP", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": ""},
            {"blueprint_id": "MOD-BP", "domain_id": "D_A", "design_maturity": "production",
             "build_status": "stable", "blueprint_path": str(bp)},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-BP") == 0
        assert "responsibility_domain: D_A" in bp.read_text(encoding="utf-8")

    def test_all_fields_empty_writes_empty_strings(self, bfr, tmp_path, monkeypatch):
        """所有字段为空 → 写入空值（不阻断，不创建文件）"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: OLD\nresponsibility_domain: OLD\ndesign_maturity: old\n"
            "build_status: old\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn_multi([
            {"blueprint_id": "MOD-ALLEMPTY", "domain_id": "", "design_maturity": "",
             "build_status": "", "blueprint_path": str(bp)},
        ])
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-ALLEMPTY") == 0
        content = bp.read_text(encoding="utf-8")
        assert "module_id: MOD-ALLEMPTY" in content
        assert "responsibility_domain:" in content
        # design_maturity / build_status 原本存在 → 更新为空
        assert "design_maturity: old" not in content
        assert "build_status: old" not in content


class TestExtremeDBException:
    """DB 异常极限测试——验证 [ERROR_CONTRACT] 声明的 exit 4。

    [ERROR_CONTRACT] 声明 "DB异常→exit 4"，但 _query_module_bp 和
    reconcile_blueprint_frontmatter 都没有 try-except 捕获 DB 异常。
    以下测试断言 exit 4，若失败则暴露声明 vs 实现的 gap。
    """

    def test_db_connection_exception_returns_4(self, bfr, monkeypatch):
        """get_depgraph_pg_connection 抛异常 → 应返回 4（[ERROR_CONTRACT]）"""
        def raise_exc(**kw):
            raise ConnectionError("DB down")
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", raise_exc)
        result = bfr.reconcile_blueprint_frontmatter("MOD-DBERR")
        assert result == 4, f"DB 连接异常应返回 4，实际返回 {result}"

    def test_db_cursor_execute_exception_returns_4(self, bfr, monkeypatch):
        """cursor.execute 抛异常 → 应返回 4（[ERROR_CONTRACT]）"""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.execute.side_effect = RuntimeError("SQL syntax error")
        conn.cursor.return_value.__enter__.return_value = cursor
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        result = bfr.reconcile_blueprint_frontmatter("MOD-SQLERR")
        assert result == 4, f"SQL 执行异常应返回 4，实际返回 {result}"

    def test_db_fetchall_exception_returns_4(self, bfr, monkeypatch):
        """cursor.fetchall 抛异常 → 应返回 4（[ERROR_CONTRACT]）"""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchall.side_effect = OSError("network error")
        conn.cursor.return_value.__enter__.return_value = cursor
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        result = bfr.reconcile_blueprint_frontmatter("MOD-FETCHERR")
        assert result == 4, f"fetchall 异常应返回 4，实际返回 {result}"


class TestExtremePathEdge:
    """路径边界极限测试——中文/空格/目录/相对路径。"""

    def test_chinese_blueprint_path(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 含中文 → 正常写入"""
        bp = tmp_path / "蓝图.md"
        bp.write_text(
            "---\nmodule_id: MOD-CN\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-CN", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-CN") == 0
        assert "D_NEW" in bp.read_text(encoding="utf-8")

    def test_space_in_blueprint_path(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 含空格 → 正常写入"""
        bp = tmp_path / "my blueprint.md"
        bp.write_text(
            "---\nmodule_id: MOD-SP\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-SP", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-SP") == 0
        assert "D_NEW" in bp.read_text(encoding="utf-8")

    def test_blueprint_path_is_directory_raises(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 指向目录（名为 *.md 的目录）→ read_text 抛 IsADirectoryError

        当前代码无 try-except → 异常传播。此测试记录当前行为（gap）。
        """
        dir_path = tmp_path / "mydir.md"
        dir_path.mkdir()
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-DIR", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(dir_path),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        # 目录存在 (exists()==True) 但 read_text 抛 IsADirectoryError
        with pytest.raises((IsADirectoryError, PermissionError, OSError)):
            bfr.reconcile_blueprint_frontmatter("MOD-DIR")

    def test_relative_blueprint_path(self, bfr, tmp_path, monkeypatch):
        """相对路径 blueprint_path → 拼接 _REPO_ROOT"""
        repo_root = tmp_path
        modules_dir = repo_root / "docs" / "03_modules"
        modules_dir.mkdir(parents=True)
        bp_file = modules_dir / "MOD-REL.md"
        bp_file.write_text(
            "---\nmodule_id: MOD-REL\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-REL", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": "docs/03_modules/MOD-REL",  # 相对路径无扩展名
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        monkeypatch.setattr(bfr, "_REPO_ROOT", repo_root)
        assert bfr.reconcile_blueprint_frontmatter("MOD-REL") == 0
        assert "D_NEW" in bp_file.read_text(encoding="utf-8")

    def test_blueprint_path_with_dotmd_directory(self, bfr, tmp_path, monkeypatch):
        """blueprint_path 无扩展名且补 .md 后指向已存在目录 → 跳过（exists()=True 但读取异常）

        补 .md 后路径恰好是目录名 → exists()==True → 进入 read_text → 抛异常。
        记录当前行为（gap：目录路径未防护）。
        """
        # tmp_path/MOD-DIR2.md 是目录
        dir_path = tmp_path / "MOD-DIR2"  # 无扩展名
        dir_path.mkdir()
        # 补 .md 后 = tmp_path/MOD-DIR2.md（不存在，是目录 MOD-DIR2 的兄弟）
        # 实际上 with_suffix(".md") 对无扩展名路径 = path + ".md"
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-DIR2", "domain_id": "D_TEST",
            "design_maturity": "design", "build_status": "planned",
            "blueprint_path": str(dir_path),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        # MOD-DIR2.md 不存在 → 标记缺失跳过
        assert bfr.reconcile_blueprint_frontmatter("MOD-DIR2") == 0


class TestExtremeFrontmatter:
    """frontmatter 边界极限测试——空/冒号/重复key/仅frontmatter/字段缺失。"""

    def test_empty_frontmatter_with_blank_line(self, bfr, tmp_path, monkeypatch):
        """空 frontmatter（含一个空行）→ 追加 module_id/responsibility_domain"""
        bp = tmp_path / "bp.md"
        bp.write_text("---\n\n---\n# Body\n", encoding="utf-8")
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-EFM", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-EFM") == 0
        content = bp.read_text(encoding="utf-8")
        assert "module_id: MOD-EFM" in content
        assert "responsibility_domain: D_NEW" in content

    def test_truly_empty_frontmatter_no_match(self, bfr, tmp_path, monkeypatch):
        """frontmatter ---\\n---\\n（无空行）→ 正则不匹配 → 视为无 frontmatter 跳过"""
        bp = tmp_path / "bp.md"
        bp.write_text("---\n---\n# Body\n", encoding="utf-8")
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-TEFM", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-TEFM") == 0
        # 正则不匹配 → 内容不变
        assert bp.read_text(encoding="utf-8") == "---\n---\n# Body\n"

    def test_value_contains_colon(self, bfr, tmp_path, monkeypatch):
        """frontmatter 值含冒号 → partition 只切第一个冒号，正确解析与更新"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD:WEIRD\nresponsibility_domain: D:OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD:WEIRD", "domain_id": "D:NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD:WEIRD") == 0
        content = bp.read_text(encoding="utf-8")
        assert "module_id: MOD:WEIRD" in content
        assert "responsibility_domain: D:NEW" in content
        assert "D:OLD" not in content

    def test_duplicate_keys_both_replaced(self, bfr, tmp_path, monkeypatch):
        """重复 key → re.sub 替换所有匹配行（两行都被更新）"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: A\nmodule_id: B\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-DUP", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-DUP") == 0
        content = bp.read_text(encoding="utf-8")
        # re.sub 替换所有匹配，两行都变成 module_id: MOD-DUP
        assert content.count("module_id: MOD-DUP") == 2

    def test_only_frontmatter_no_body(self, bfr, tmp_path, monkeypatch):
        """仅 frontmatter 无正文 → 正常更新"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-NOBODY\nresponsibility_domain: OLD\n---\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOBODY", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOBODY") == 0
        assert "responsibility_domain: D_NEW" in bp.read_text(encoding="utf-8")

    def test_design_maturity_not_appended_if_absent(self, bfr, tmp_path, monkeypatch):
        """frontmatter 无 design_maturity 字段 → 不追加该字段"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-NODM\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NODM", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NODM") == 0
        assert "design_maturity" not in bp.read_text(encoding="utf-8")

    def test_build_status_not_appended_if_absent(self, bfr, tmp_path, monkeypatch):
        """frontmatter 无 build_status 字段 → 不追加该字段"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: MOD-NOBS\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-NOBS", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-NOBS") == 0
        assert "build_status" not in bp.read_text(encoding="utf-8")


class TestExtremeIdempotency:
    """幂等性极限测试——连续调用两次结果一致。"""

    def test_idempotent_double_call(self, bfr, tmp_path, monkeypatch):
        """连续调用两次 → 第二次内容无变化"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: OLD\nresponsibility_domain: OLD\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-IDEM", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-IDEM") == 0
        content_after_first = bp.read_text(encoding="utf-8")
        # 第二次调用（内容已对齐，不应再写）
        assert bfr.reconcile_blueprint_frontmatter("MOD-IDEM") == 0
        content_after_second = bp.read_text(encoding="utf-8")
        assert content_after_first == content_after_second

    def test_idempotent_with_dm_and_bs(self, bfr, tmp_path, monkeypatch):
        """含 design_maturity/build_status 的幂等性"""
        bp = tmp_path / "bp.md"
        bp.write_text(
            "---\nmodule_id: OLD\nresponsibility_domain: OLD\ndesign_maturity: old\n"
            "build_status: old\n---\n# T\n",
            encoding="utf-8",
        )
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-IDEM2", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        bfr.reconcile_blueprint_frontmatter("MOD-IDEM2")
        first = bp.read_text(encoding="utf-8")
        bfr.reconcile_blueprint_frontmatter("MOD-IDEM2")
        second = bp.read_text(encoding="utf-8")
        assert first == second


class TestExtremeFileIO:
    """文件 I/O 异常极限测试——read_text/write_text 抛异常。"""

    def test_read_text_io_error_propagates(self, bfr, tmp_path, monkeypatch):
        """read_text 抛 OSError → 异常传播（当前无 try-except，gap）"""
        bp = tmp_path / "bp.md"
        bp.write_text("---\nmodule_id: MOD-IO\n---\n# T\n", encoding="utf-8")
        conn = _mock_depgraph_conn({
            "blueprint_id": "MOD-IO", "domain_id": "D_NEW",
            "design_maturity": "production", "build_status": "stable",
            "blueprint_path": str(bp),
        })
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)

        original_read = Path.read_text

        def raise_io(self, *a, **kw):
            raise OSError("disk read error")

        monkeypatch.setattr(Path, "read_text", raise_io)
        with pytest.raises(OSError):
            bfr.reconcile_blueprint_frontmatter("MOD-IO")
        monkeypatch.setattr(Path, "read_text", original_read)


class TestWeightedVoting:
    def test_test_file_downweighted(self, bfr, tmp_path, monkeypatch):
        """测试文件降权：2源码(D_GOV_SCRIPTS) vs 2测试(D_AUDITTEST) → D_GOV_SCRIPTS"""
        bp = tmp_path / "blueprint.md"
        bp.write_text(
            "---\nmodule_id: MOD-GOV-SYNC-PANORAMA\nresponsibility_domain: old\n---\n# T\n",
            encoding="utf-8",
        )
        conn = MagicMock()
        cursor = MagicMock()
        # 行顺序：测试文件行在前 → Counter 平局时取 D_AUDITTEST（先插入）；
        # 加权投票时 D_GOV_SCRIPTS(2.0) > D_AUDITTEST(0.2) → D_GOV_SCRIPTS 胜出
        cursor.fetchall.return_value = [
            {"blueprint_id": "MOD-GOV-SYNC-PANORAMA", "domain_id": "D_AUDITTEST",
             "design_maturity": "production", "build_status": "stable",
             "blueprint_path": None, "path": "tests/test_gov.py"},
            {"blueprint_id": "MOD-GOV-SYNC-PANORAMA", "domain_id": "D_AUDITTEST",
             "design_maturity": "production", "build_status": "stable",
             "blueprint_path": None, "path": "tests/test_gov2.py"},
            {"blueprint_id": "MOD-GOV-SYNC-PANORAMA", "domain_id": "D_GOV_SCRIPTS",
             "design_maturity": "production", "build_status": "stable",
             "blueprint_path": str(bp), "path": "scripts/gov.py"},
            {"blueprint_id": "MOD-GOV-SYNC-PANORAMA", "domain_id": "D_GOV_SCRIPTS",
             "design_maturity": "production", "build_status": "stable",
             "blueprint_path": str(bp), "path": "scripts/gov2.py"},
        ]
        cursor.fetchone.return_value = None
        conn.cursor.return_value.__enter__.return_value = cursor
        monkeypatch.setattr(bfr, "get_depgraph_pg_connection", lambda **kw: conn)
        assert bfr.reconcile_blueprint_frontmatter("MOD-GOV-SYNC-PANORAMA") == 0
        content = bp.read_text(encoding="utf-8")
        assert "D_GOV_SCRIPTS" in content
        assert "D_AUDITTEST" not in content
