# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_audit_rename_completeness | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""audit_rename_completeness.py 回归测试（红蓝对抗逻辑永久化）。

测试覆盖（红蓝对抗矩阵）：
- 蓝队 B1: cmd_rename_domain + 后置校验钩子触发，0 残留
- 蓝队 B2: EXCLUDE_COLUMNS 含 blueprint_id，改名后 0 误报
- 红队 R1: 改名到已存在 new_id 应失败（禁止覆盖）
- 红队 R2: 改名不存在 old_id 应失败
- 红队 R3: import 失败应 graceful 降级，不崩溃
- 红队 R5: --check-files 负向先行断言排除 MOD- 前缀误匹配

测试库隔离：用 pytest tmp_path fixture 创建生产库副本，测试后自动清理。
符合 project_memory 强制约束："测试脚本必须严格隔离生产库"。
"""
import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

# 配置 sys.path（tests/ 无 conftest，自行 insert）
from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

# 测试库不需要 git 备份（隔离生产库）
os.environ.setdefault("ZEPHYR_SKIP_BACKUP_CHECK", "1")

from apply_depgraph import _post_rename_residual_check, cmd_rename_domain  # noqa: E402
from d8_doc_sync.audit_rename_completeness import (  # noqa: E402
    EXCLUDE_COLUMNS,
    scan_files_residual,
    scan_residual,
)

PROD_DB = REPO_ROOT / "data" / "databases" / "depgraph"

# P2迁移：depgraph 已从 SQLite 迁移到 PostgreSQL，PROD_DB (depgraph SQLite) 不再是真源。
# cmd_rename_domain/scan_residual 均基于 SQLite 连接，PRAGMA wal_checkpoint 不适用 PG。
# TODO(P2-migration): 后续需将本测试改造为 PG 适配版本（用 get_db_connection + PG 库副本替代 SQLite 文件复制 + PRAGMA wal_checkpoint），当前 skip。
pytestmark = pytest.mark.skip(
    reason="P2迁移：depgraph 已迁移到 PG，SQLite 文件复制 + PRAGMA wal_checkpoint + sqlite3 连接测试不适用"
)


@pytest.fixture
def test_db(tmp_path):
    """创建生产库副本（隔离生产库），tmp_path 由 pytest 自动清理。"""
    dst = tmp_path / "test_rename.db"
    conn = sqlite3.connect(str(PROD_DB))
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    shutil.copy2(str(PROD_DB), str(dst))
    yield str(dst)


class TestBlueTeam:
    """蓝队：正常流程验证。"""

    def test_b1_post_rename_check_triggers(self, test_db, capsys):
        """B1: 改名后后置校验钩子触发，0 残留。"""
        n = cmd_rename_domain("D_GOV_DOCS", "D-TEST_B1", dry_run=False, db_path=test_db)
        assert n >= 0, f"改名失败: affected={n}"
        # 后置校验钩子（不抛异常即通过）
        _post_rename_residual_check("D_GOV_DOCS", test_db)
        captured = capsys.readouterr()
        assert "[POST-RENAME-CHECK] OK" in captured.out, f"后置校验未输出 OK: {captured.out}"
        # new_id 存在，old_id 消失
        conn = sqlite3.connect(test_db)
        try:
            assert conn.execute(
                "SELECT COUNT(*) FROM domains WHERE domain_id='D-TEST_B1'"
            ).fetchone()[0] == 1
            assert conn.execute(
                "SELECT COUNT(*) FROM domains WHERE domain_id='D_GOV_DOCS'"
            ).fetchone()[0] == 0
        finally:
            conn.close()

    def test_b2_exclude_blueprint_id_no_false_positive(self, test_db):
        """B2: EXCLUDE_COLUMNS 含 blueprint_id，改名后 blueprint_id 列 0 误报。"""
        assert "blueprint_id" in EXCLUDE_COLUMNS, f"EXCLUDE_COLUMNS 缺 blueprint_id: {EXCLUDE_COLUMNS}"
        cmd_rename_domain("D_GOV_DOCS", "D-TEST_B2", dry_run=False, db_path=test_db)
        conn = sqlite3.connect(test_db)
        try:
            residuals = scan_residual(conn, ["D_GOV_DOCS"], check_all_text_columns=True)
        finally:
            conn.close()
        blueprint_res = [r for r in residuals if r["column"] == "blueprint_id"]
        assert len(blueprint_res) == 0, f"blueprint_id 误报: {blueprint_res}"
        assert sum(r["count"] for r in residuals) == 0, f"改名后有残留: {residuals}"


class TestRedTeam:
    """红队：极限/破坏测试。"""

    def test_r1_rename_to_existing_blocked(self, test_db):
        """R1: 改名到已存在 new_id 应失败（禁止覆盖）。"""
        n = cmd_rename_domain(
            "D_SECURITY_LLM", "D_GOV_ENFORCEMENT", dry_run=False, db_path=test_db
        )
        assert n == -1, f"应禁止覆盖已存在 new_id，但 return={n}"

    def test_r2_rename_nonexistent_old_fails(self, test_db):
        """R2: 改名不存在 old_id 应失败。"""
        n = cmd_rename_domain(
            "D-NONEXISTENT", "D-WHATEVER", dry_run=False, db_path=test_db
        )
        assert n == -1, f"不存在的 old_id 应失败，但 return={n}"

    def test_r3_import_fail_graceful(self, test_db, monkeypatch, capsys):
        """R3: audit_rename_completeness import 失败应 graceful 降级，不崩溃。"""
        import builtins
        orig_import = builtins.__import__

        def fail_import(name, *args, **kwargs):
            if name == "audit_rename_completeness":
                raise ImportError("simulated R3 test")
            return orig_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fail_import)
        monkeypatch.delitem(sys.modules, "audit_rename_completeness", raising=False)
        # 不抛异常即通过
        _post_rename_residual_check("D_GOV_DOCS", test_db)
        captured = capsys.readouterr()
        assert "[POST-RENAME-CHECK] SKIP" in captured.err, f"未降级输出 SKIP: {captured.err}"

    def test_r5_check_files_excludes_mod_prefix(self, tmp_path):
        """R5: --check-files 负向先行断言排除 MOD- 前缀误匹配。

        MOD-GOV-DOCS 中的 D_GOV_DOCS 子串不应匹配（MODULE ID），
        但独立的 D_GOV_DOCS 应匹配（DOMAIN ID 残留）。
        """
        f = tmp_path / "test_residual.py"
        f.write_text(
            "# [BLUEPRINT] MOD-GOV-DOCS | test file\n# D_GOV_DOCS domain reference\n",
            encoding="utf-8",
        )
        res = scan_files_residual([str(f)], ["D_GOV_DOCS"])
        real = [r for r in res if r["old_id"] == "D_GOV_DOCS"]
        # 仅第二行真实残留应匹配（第一行 MOD 前缀被负向先行断言排除）
        assert len(real) == 1, f"应仅匹配第二行真实残留，实际匹配 {len(real)} 处: {real}"
        assert real[0]["line"] == 2, f"残留应在第 2 行，实际在第 {real[0]['line']} 行"
