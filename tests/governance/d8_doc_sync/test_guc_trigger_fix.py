# [BLUEPRINT] MOD-GOV_GUC_TRIGGER_FIX | tests/governance/d8_doc_sync/test_guc_trigger_fix.py | §ARCH-GUC-TRIGGER-FIX-001
# [MODULE] tests.governance.d8_doc_sync.test_guc_trigger_fix
# [DOMAIN] D_GOV_DOCS
# [DEPENDENCIES] scripts.governance.d8_doc_sync.sync_yaml_to_depgraph; scripts.governance.shared.constants
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 __guc_fix_test_* 前缀的测试行，结束时强制清理（escape hatch）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-GOV_GUC_TRIGGER_FIX | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_guc_trigger_fix.py — GUC 触发器缺陷修复的端到端 smoke test（#ARCH-GUC-TRIGGER-FIX-001）

验证裁定 A（P0）的修复效果：
  1. protect_dataflow_design_maturity() 触发器函数使用 current_setting(..., true) 而非 SHOW
  2. protect_decision_design_maturity() 触发器函数使用 current_setting(..., true) 而非 SHOW
  3. sync_dataflow_registry(cur) 完整执行成功（不再因 GUC 未注册而失败）
  4. DELETE design 行被 ARCH-053 阻断（ARCH-MM-002: prototype 已删除，仅保护 design）
  5. UPDATE design 行降级被 ARCH-053 阻断
  6. 逃生通道 SET app.allow_design_maturity_delete=on 正常工作

背景：
  原触发器用 `SHOW app.allow_design_maturity_delete INTO v_allow`，但该 GUC 未在
  sync session 中 SET，SHOW 抛 UndefinedObject 异常，导致 sync_dataflow_registry 失败，
  reconciler 重试 23 次仍失败。修复：替换为 `current_setting(..., true)`，GUC 未注册时
  返回 NULL，不抛异常。

  修复过程中还发现第二个 bug：触发器函数跨 3 表共享时，COALESCE(OLD.entity_name, OLD.job_name)
  会求值所有参数，访问不存在列抛异常。修复：改用 OLD::text。

测试隔离：
  - 使用 __guc_fix_test_* 前缀的测试行名，避免与真实数据冲突
  - 测试结束（无论成功/失败）都用 escape hatch 强制清理测试行
  - 测试使用独立连接，不影响其他 session
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 路径设置
_REPO_ROOT = Path(__file__).resolve().parents[3]  # tests/governance/d8_doc_sync/ -> repo root
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(_REPO_ROOT / "scripts" / "governance"))
sys.path.insert(0, str(_REPO_ROOT / "scripts" / "governance" / "d8_doc_sync"))


def _get_val(row, idx):
    """从 RealDictRow (dict) 或 tuple 按 index 取值。"""
    if isinstance(row, dict):
        return list(row.values())[idx]
    return row[idx]


def _get_conn():
    """获取 depgraph PG 连接，失败则 skip 测试。"""
    try:
        from _shared.constants import get_depgraph_pg_connection

        return get_depgraph_pg_connection(autocommit=False, superuser=True)
    except Exception as e:
        pytest.skip(f"无法连接 PostgreSQL depgraph DB: {e}")


def _cleanup_test_rows(cur, conn):
    """强制清理测试行（使用 escape hatch）。"""
    try:
        cur.execute("SET app.allow_design_maturity_delete = 'on'")
        cur.execute("DELETE FROM dataflow_jobs WHERE job_name LIKE '__guc_fix_test_%'")
        cur.execute("DELETE FROM dataflow_datasets WHERE entity_name LIKE '__guc_fix_test_%'")
        cur.execute("DELETE FROM dataflow_edges WHERE from_entity_id < 0 OR to_entity_id < 0")
        cur.execute("SET app.allow_design_maturity_delete = 'off'")
        conn.commit()
    except Exception:
        conn.rollback()


class TestGucTriggerFix:
    """#ARCH-GUC-TRIGGER-FIX-001: GUC 触发器缺陷修复验证。"""

    def test_trigger_functions_use_current_setting_not_show(self):
        """验证两个触发器函数都已修复为 current_setting，不再使用 SHOW。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT t.proname, pg_get_functiondef(t.oid) as func_def
                FROM pg_proc t
                WHERE t.proname IN (
                    'protect_dataflow_design_maturity',
                    'protect_decision_design_maturity'
                )
                ORDER BY t.proname
                """
            )
            rows = cur.fetchall()
            assert len(rows) == 2, f"Expected 2 trigger functions, got {len(rows)}"

            for r in rows:
                name = _get_val(r, 0)
                func_def = _get_val(r, 1)
                assert "SHOW app." not in func_def, f"{name} still uses SHOW (BROKEN)"
                assert "current_setting" in func_def, f"{name} does not use current_setting (not fixed)"
        finally:
            cur.close()
            conn.close()

    def test_current_setting_returns_null_or_off_when_not_set(self):
        """验证 current_setting(..., true) 在 GUC 未注册/未 SET 时返回 NULL 或 'off'。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT current_setting('app.allow_design_maturity_delete', true) as val")
            val = _get_val(cur.fetchone(), 0)
            # GUC 可能未注册（NULL）或被 SET 为 'off'，两者都表示保护激活
            assert val is None or val == "off", f"Expected NULL or 'off', got {val!r}"
        finally:
            cur.close()
            conn.close()

    def test_delete_production_rows_succeeds(self):
        """验证 DELETE production 行成功（触发器不保护 production）。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                DELETE FROM dataflow_jobs
                WHERE design_maturity = 'production' AND job_name = '__nonexistent_test__'
                """
            )
            conn.commit()
            # 0 rows affected, but no exception
        finally:
            cur.close()
            conn.close()

    def test_delete_design_rows_blocked_by_arch_053(self):
        """验证 DELETE design 行被 ARCH-053 阻断。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            # 插入测试 design 行
            cur.execute(
                """
                INSERT INTO dataflow_jobs (job_name, entity_type, scope, design_maturity, build_status)
                VALUES ('__guc_fix_test_delete__', 'job', 'production', 'design', 'planned')
                ON CONFLICT (job_name) DO UPDATE SET
                    design_maturity = 'design', build_status = 'planned'
                RETURNING job_id
                """
            )
            job_id = _get_val(cur.fetchone(), 0)
            assert job_id > 0

            # 尝试 DELETE（应失败）
            with pytest.raises(Exception) as exc_info:
                cur.execute("DELETE FROM dataflow_jobs WHERE job_name = '__guc_fix_test_delete__'")
            assert "ARCH-053" in str(exc_info.value), f"Expected ARCH-053 error, got: {exc_info.value}"
        finally:
            _cleanup_test_rows(cur, conn)
            cur.close()
            conn.close()

    def test_update_design_to_production_blocked_by_arch_053(self):
        """验证 UPDATE design→production 被 ARCH-053 阻断。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO dataflow_jobs (job_name, entity_type, scope, design_maturity, build_status)
                VALUES ('__guc_fix_test_update__', 'job', 'production', 'design', 'planned')
                ON CONFLICT (job_name) DO UPDATE SET
                    design_maturity = 'design', build_status = 'planned'
                """
            )
            cur.execute("SAVEPOINT sp_update_test")
            try:
                cur.execute(
                    """
                    UPDATE dataflow_jobs SET design_maturity = 'production'
                    WHERE job_name = '__guc_fix_test_update__'
                    """
                )
                pytest.fail("UPDATE should have been blocked by ARCH-053")
            except Exception as e:
                assert "ARCH-053" in str(e), f"Expected ARCH-053, got: {e}"
            cur.execute("ROLLBACK TO SAVEPOINT sp_update_test")

            # 验证 design_maturity 仍为 design
            cur.execute("SELECT design_maturity FROM dataflow_jobs WHERE job_name = '__guc_fix_test_update__'")
            row = cur.fetchone()
            assert row is not None
            dm = _get_val(row, 0)
            assert dm == "design", f"Expected 'design', got {dm!r}"
        finally:
            _cleanup_test_rows(cur, conn)
            cur.close()
            conn.close()

    def test_escape_hatch_allows_delete(self):
        """验证逃生通道 SET app.allow_design_maturity_delete=on 允许 DELETE design 行。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO dataflow_jobs (job_name, entity_type, scope, design_maturity, build_status)
                VALUES ('__guc_fix_test_escape__', 'job', 'production', 'design', 'planned')
                ON CONFLICT (job_name) DO UPDATE SET
                    design_maturity = 'design', build_status = 'planned'
                """
            )
            # 启用逃生通道
            cur.execute("SET app.allow_design_maturity_delete = 'on'")
            cur.execute("DELETE FROM dataflow_jobs WHERE job_name = '__guc_fix_test_escape__'")
            cur.execute("SET app.allow_design_maturity_delete = 'off'")
            conn.commit()

            # 验证行已被删除
            cur.execute("SELECT count(*) FROM dataflow_jobs WHERE job_name = '__guc_fix_test_escape__'")
            count = _get_val(cur.fetchone(), 0)
            assert count == 0, f"Expected 0 rows after escape hatch delete, got {count}"
        finally:
            _cleanup_test_rows(cur, conn)
            cur.close()
            conn.close()

    def test_sync_dataflow_registry_executes_successfully(self):
        """端到端验证：sync_dataflow_registry(cur) 完整执行成功。"""
        conn = _get_conn()
        cur = conn.cursor()
        try:
            from sync_yaml_to_depgraph import sync_dataflow_registry

            sync_dataflow_registry(cur)
            conn.commit()
        except Exception as e:
            conn.rollback()
            pytest.fail(f"sync_dataflow_registry failed: {type(e).__name__}: {e}")
        finally:
            cur.close()
            conn.close()
