# [A_test] module_id: SRC-TST-2215 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_apply_depgraph_transition_sync
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/governance/test_apply_depgraph_transition_sync.py
# [TTL] task_bound
"""test_apply_depgraph_transition_sync.py — 状态转换后四图同步单测（ARCH-056）

覆盖 _sync_panorama_after_transition 的 4 个场景：
- blueprint_id 非空 → sync_module_panorama 被调用
- blueprint_id 为空 → 不调用
- node 不存在 → 不调用
- sync 异常 → 不抛出（warn-only）
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "governance"
    / "apply_depgraph.py"
)


@pytest.fixture(scope="module")
def adg():
    """动态加载 apply_depgraph.py（避免 __init__.py 依赖问题）"""
    spec = importlib.util.spec_from_file_location(
        "apply_depgraph_under_test", _SCRIPT_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mock_depgraph_conn(fetchone_result=None):
    """构造 mock depgraph 连接，execute 返回 fetchone_result。"""
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone_result
    conn.execute.return_value = cursor
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn


def _inject_sync_mock(monkeypatch, adg):
    """在 sys.modules 注入 mock sync_panorama_module，返回 mock 函数。"""
    sync_mock = MagicMock()
    fake_module = MagicMock()
    fake_module.sync_module_panorama = sync_mock
    monkeypatch.setitem(sys.modules, "sync_panorama_module", fake_module)
    return sync_mock


class TestSyncPanoramaAfterTransition:
    """_sync_panorama_after_transition 核心逻辑（ARCH-056）。"""

    def test_sync_called_when_blueprint_id_exists(self, adg, monkeypatch):
        """blueprint_id 非空 → sync_module_panorama 被调用"""
        conn = _mock_depgraph_conn(
            fetchone_result={"blueprint_id": "MOD-TEST"}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: conn)
        sync_mock = _inject_sync_mock(monkeypatch, adg)

        adg._sync_panorama_after_transition(42)

        sync_mock.assert_called_once_with("MOD-TEST")

    def test_sync_skipped_when_blueprint_id_empty(self, adg, monkeypatch):
        """blueprint_id 为空 → 不调用 sync"""
        conn = _mock_depgraph_conn(
            fetchone_result={"blueprint_id": ""}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: conn)
        sync_mock = _inject_sync_mock(monkeypatch, adg)

        adg._sync_panorama_after_transition(42)

        sync_mock.assert_not_called()

    def test_sync_skipped_when_node_not_found(self, adg, monkeypatch):
        """node 不存在（fetchone=None）→ 不调用 sync"""
        conn = _mock_depgraph_conn(fetchone_result=None)
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: conn)
        sync_mock = _inject_sync_mock(monkeypatch, adg)

        adg._sync_panorama_after_transition(999)

        sync_mock.assert_not_called()

    def test_sync_exception_does_not_raise(self, adg, monkeypatch):
        """sync_module_panorama 抛异常 → 不传播（warn-only）"""
        conn = _mock_depgraph_conn(
            fetchone_result={"blueprint_id": "MOD-TEST"}
        )
        monkeypatch.setattr(adg, "get_depgraph_pg_connection", lambda **kw: conn)
        sync_mock = _inject_sync_mock(monkeypatch, adg)
        sync_mock.side_effect = RuntimeError("DB down")

        # 不应抛异常
        adg._sync_panorama_after_transition(42)
