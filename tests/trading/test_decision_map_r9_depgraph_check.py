# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [DOMAIN] D_TRADING
# [TESTS] tests/trading/test_decision_map_r9_depgraph_check.py
# [TTL] permanent
"""R9 depgraph 存在性检查红测——审计失明清单#5 修复守卫。

历史病根：_SQL 查 nodes.module_id（不存在列）→ psycopg2.UndefinedColumn 被
except 吞掉 → 垃圾 module_ref 恒 True = R9 死检查（AUDIT_REPORT 失明清单#5）。
本文件三测：垃圾必 False、真锚必 True、SQL 列名错必抛（fail-open 只许 DB 不可用）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))
from check_decision_map import _module_exists_in_depgraph  # noqa: E402


def _depgraph_reachable() -> bool:
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection()
        conn.close()
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _depgraph_reachable(), reason="depgraph PG 不可达")


def test_bogus_module_ref_returns_false():
    assert _module_exists_in_depgraph("TOTALLY-BOGUS-MOD-999") is False


def test_known_good_ref_returns_true():
    assert _module_exists_in_depgraph("src/zephyr/plan_engine/daily_warroom_pipeline.py") is True


def test_sql_column_error_raises():
    """SQL 语法/列名错必须抛（fail-open 豁免只限 DB 不可用）——死检查防复发锚。"""
    import check_decision_map as cdm

    original = cdm._SQL_CHECK_MODULE_FILE_EXISTS
    cdm._SQL_CHECK_MODULE_FILE_EXISTS = "SELECT 1 FROM nodes WHERE no_such_column_xyz_audit = %s LIMIT 1"
    try:
        with pytest.raises(Exception):
            cdm._module_exists_in_depgraph("src/zephyr/plan_engine/daily_warroom_pipeline.py")
    finally:
        cdm._SQL_CHECK_MODULE_FILE_EXISTS = original
