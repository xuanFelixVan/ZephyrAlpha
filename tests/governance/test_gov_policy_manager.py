# [BLUEPRINT] MOD-GOV-052 | docs/03_modules/_domain_governance/gov_policy_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-052 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.governance.test_gov_policy_manager
# [TESTS] src/zephyr/governance/gov_policy_manager.py
"""MOD-GOV-052 单元测试：gov_policy_manager 治理策略管理器。

蓝图验收（B9-10877/CAND-WORKTREE-003，B9 D-GOVERNANCE-01）：
GOV-* 策略 CRUD + 版本递增历史留存 + sqlite 注入持久化 +
状态机 draft→active→suspended→retired。
sqlite 用 :memory: 内存连接，时钟全注入固定值，不触盘不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.governance.gov_policy_manager",
    reason="gov_policy_manager not importable",
)

from zephyr.governance.gov_policy_manager import (  # noqa: E402
    GovPolicyError,
    GovPolicyManager,
    PolicyState,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _manager(conn: sqlite3.Connection | None = None) -> GovPolicyManager:
    return GovPolicyManager(clock=lambda: _T0, sqlite_conn=conn)


def _mem_conn() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")


# ──────────────────────────────────────────────────────────────────────────────
# 创建（Fail-Closed 校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_create_ok_v1_draft(self) -> None:
        mgr = _manager()
        rec = mgr.create_policy("GOV-RISK-001", "回撤≤5%")
        assert rec.version == 1
        assert rec.state is PolicyState.DRAFT
        assert rec.content == "回撤≤5%"
        assert rec.updated_at == _T0

    def test_empty_policy_id_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().create_policy("", "x")

    def test_non_gov_prefix_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().create_policy("RISK-001", "x")

    def test_empty_content_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().create_policy("GOV-RISK-001", "")

    def test_duplicate_create_raises(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        with pytest.raises(GovPolicyError):
            mgr.create_policy("GOV-RISK-001", "v2")


# ──────────────────────────────────────────────────────────────────────────────
# 更新 / 版本历史
# ──────────────────────────────────────────────────────────────────────────────


class TestVersioning:
    def test_update_increments_version_keeps_state(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.transition("GOV-RISK-001", PolicyState.ACTIVE)
        rec = mgr.update_policy("GOV-RISK-001", "v2 内容")
        assert rec.version == 3
        assert rec.state is PolicyState.ACTIVE
        assert rec.content == "v2 内容"

    def test_history_retains_all_versions(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.update_policy("GOV-RISK-001", "v2")
        mgr.update_policy("GOV-RISK-001", "v3")
        history = mgr.history("GOV-RISK-001")
        assert [r.version for r in history] == [1, 2, 3]
        assert [r.content for r in history] == ["v1", "v2", "v3"]

    def test_get_specific_version(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.update_policy("GOV-RISK-001", "v2")
        assert mgr.get_policy("GOV-RISK-001").content == "v2"
        assert mgr.get_policy("GOV-RISK-001", version=1).content == "v1"

    def test_get_unknown_policy_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().get_policy("GOV-GHOST-001")

    def test_get_unknown_version_raises(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        with pytest.raises(GovPolicyError):
            mgr.get_policy("GOV-RISK-001", version=9)

    def test_update_unknown_policy_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().update_policy("GOV-GHOST-001", "x")

    def test_update_retired_raises(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.transition("GOV-RISK-001", PolicyState.RETIRED)
        with pytest.raises(GovPolicyError):
            mgr.update_policy("GOV-RISK-001", "v2")


# ──────────────────────────────────────────────────────────────────────────────
# 状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestStateMachine:
    def test_full_lifecycle(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        assert mgr.transition("GOV-RISK-001", PolicyState.ACTIVE).state is PolicyState.ACTIVE
        assert mgr.transition("GOV-RISK-001", PolicyState.SUSPENDED).state is PolicyState.SUSPENDED
        assert mgr.transition("GOV-RISK-001", PolicyState.ACTIVE).state is PolicyState.ACTIVE
        assert mgr.transition("GOV-RISK-001", PolicyState.RETIRED).state is PolicyState.RETIRED

    def test_draft_to_suspended_rejected(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        with pytest.raises(GovPolicyError):
            mgr.transition("GOV-RISK-001", PolicyState.SUSPENDED)

    def test_retired_is_terminal(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.transition("GOV-RISK-001", PolicyState.RETIRED)
        with pytest.raises(GovPolicyError):
            mgr.transition("GOV-RISK-001", PolicyState.ACTIVE)

    def test_invalid_state_type_raises(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        with pytest.raises(GovPolicyError):
            mgr.transition("GOV-RISK-001", "active")

    def test_transition_unknown_policy_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().transition("GOV-GHOST-001", PolicyState.ACTIVE)


# ──────────────────────────────────────────────────────────────────────────────
# 删除 / 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestDeleteAndQuery:
    def test_delete_draft_ok(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.delete_policy("GOV-RISK-001")
        with pytest.raises(GovPolicyError):
            mgr.get_policy("GOV-RISK-001")

    def test_delete_active_rejected(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.transition("GOV-RISK-001", PolicyState.ACTIVE)
        with pytest.raises(GovPolicyError):
            mgr.delete_policy("GOV-RISK-001")

    def test_list_policies_sorted_and_filtered(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-B-002", "b")
        mgr.create_policy("GOV-A-001", "a")
        mgr.transition("GOV-A-001", PolicyState.ACTIVE)
        all_latest = mgr.list_policies()
        assert [r.policy_id for r in all_latest] == ["GOV-A-001", "GOV-B-002"]
        active = mgr.list_policies(state=PolicyState.ACTIVE)
        assert [r.policy_id for r in active] == ["GOV-A-001"]

    def test_list_invalid_state_raises(self) -> None:
        with pytest.raises(GovPolicyError):
            _manager().list_policies(state="active")


# ──────────────────────────────────────────────────────────────────────────────
# sqlite 持久化（注入 :memory: 连接）
# ──────────────────────────────────────────────────────────────────────────────


class TestPersistence:
    def test_rows_mirrored_with_history(self) -> None:
        conn = _mem_conn()
        mgr = _manager(conn)
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.update_policy("GOV-RISK-001", "v2")
        mgr.transition("GOV-RISK-001", PolicyState.ACTIVE)
        rows = conn.execute(
            "SELECT policy_id, version, content, state, updated_at FROM gov_policies ORDER BY version"
        ).fetchall()
        assert [(r[0], r[1], r[2], r[3]) for r in rows] == [
            ("GOV-RISK-001", 1, "v1", "draft"),
            ("GOV-RISK-001", 2, "v2", "draft"),
            ("GOV-RISK-001", 3, "v2", "active"),
        ]
        assert rows[0][4] == _T0.isoformat()

    def test_delete_removes_rows(self) -> None:
        conn = _mem_conn()
        mgr = _manager(conn)
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.delete_policy("GOV-RISK-001")
        assert conn.execute("SELECT COUNT(*) FROM gov_policies").fetchone()[0] == 0

    def test_sqlite_failure_fail_closed(self) -> None:
        conn = _mem_conn()
        mgr = _manager(conn)
        mgr.create_policy("GOV-RISK-001", "v1")
        conn.close()  # 后续写入必失败
        with pytest.raises(GovPolicyError):
            mgr.update_policy("GOV-RISK-001", "v2")
        # 库写失败 → 内存不产生半态（仍为 v1）
        assert mgr.get_policy("GOV-RISK-001").version == 1

    def test_memory_only_without_conn(self) -> None:
        mgr = _manager()
        mgr.create_policy("GOV-RISK-001", "v1")
        mgr.transition("GOV-RISK-001", PolicyState.ACTIVE)
        assert mgr.get_policy("GOV-RISK-001").state is PolicyState.ACTIVE

    def test_determinism_same_input_same_output(self) -> None:
        def _run() -> list:
            mgr = _manager()
            mgr.create_policy("GOV-A-001", "a")
            mgr.update_policy("GOV-A-001", "a2")
            mgr.transition("GOV-A-001", PolicyState.ACTIVE)
            return [(r.policy_id, r.version, r.content, r.state, r.updated_at) for r in mgr.history("GOV-A-001")]

        assert _run() == _run()
