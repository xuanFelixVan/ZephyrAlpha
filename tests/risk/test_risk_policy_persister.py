# [BLUEPRINT] MOD-RK-044 | docs/03_modules/_domain_risk/risk_policy_persister/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RK-044 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.risk.test_risk_policy_persister
# [TESTS] src/zephyr/risk/risk_policy_persister.py
"""MOD-RK-044 单元测试：risk_policy_persister 风控策略持久化器。

蓝图验收（B13-04311/CAND-RSK-048，A3 D-RISK-49）：
risk_policy/risk_limit/risk_policy_version 三表 DDL（注入 sqlite 内存连接）+
版本递增不可变 + 激活版本原子热加载 + 与 risk_limits 双向同步校验（漂移清单）。
sqlite :memory: + 时钟注入，不触网不落盘。
"""

from __future__ import annotations

import datetime
import sqlite3
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.risk_policy_persister",
    reason="risk_policy_persister not importable",
)

from zephyr.risk.risk_policy_persister import (  # noqa: E402
    PolicyDrift,
    RiskPolicy,
    RiskPolicyError,
    RiskPolicyPersister,
)

_T0 = datetime.datetime(2026, 8, 25, 18, 0, 0)

_LIMITS_V1 = {
    "max_single_position": Decimal("0.10"),
    "max_gross_leverage": Decimal("1.0"),
}
_LIMITS_V2 = {
    "max_single_position": Decimal("0.08"),
    "max_gross_leverage": Decimal("1.0"),
    "max_sector_concentration": Decimal("0.30"),
}


@pytest.fixture()
def conn():
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


def _persister(conn, **overrides) -> RiskPolicyPersister:
    kwargs = {"conn": conn, "clock": lambda: _T0}
    kwargs.update(overrides)
    return RiskPolicyPersister(**kwargs)


def _policy(limits=None, policy_id: str = "risk-core") -> RiskPolicy:
    return RiskPolicy(
        policy_id=policy_id,
        name="核心风控策略",
        limits=_LIMITS_V1 if limits is None else limits,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造 + DDL
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_conn_not_injected_raises(self) -> None:
        with pytest.raises(RiskPolicyError):
            RiskPolicyPersister(conn=None, clock=lambda: _T0)

    def test_ddl_creates_three_tables(self, conn) -> None:
        _persister(conn)
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        assert [r[0] for r in rows] == [
            "risk_limit",
            "risk_policy",
            "risk_policy_version",
        ]

    def test_ddl_idempotent(self, conn) -> None:
        _persister(conn)
        _persister(conn)  # CREATE IF NOT EXISTS 幂等不抛


# ──────────────────────────────────────────────────────────────────────────────
# 版本递增不可变
# ──────────────────────────────────────────────────────────────────────────────


class TestVersioning:
    def test_save_returns_incrementing_versions(self, conn) -> None:
        p = _persister(conn)
        assert p.save_policy(_policy()) == 1
        assert p.save_policy(_policy(limits=_LIMITS_V2)) == 2
        assert p.list_versions("risk-core") == (1, 2)

    def test_versions_isolated_per_policy(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy(policy_id="risk-core"))
        assert p.save_policy(_policy(policy_id="risk-alt")) == 1

    def test_old_version_immutable_snapshot(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.save_policy(_policy(limits=_LIMITS_V2))
        v1 = p.get_version("risk-core", 1)
        assert v1.limits == _LIMITS_V1  # v1 不受 v2 影响
        assert v1.created_at == _T0
        assert v1.is_active is False

    def test_save_empty_policy_id_raises(self, conn) -> None:
        with pytest.raises(RiskPolicyError):
            _persister(conn).save_policy(_policy(policy_id=""))

    def test_save_empty_limits_raises(self, conn) -> None:
        with pytest.raises(RiskPolicyError):
            _persister(conn).save_policy(_policy(limits={}))

    def test_save_non_decimal_value_raises(self, conn) -> None:
        with pytest.raises(RiskPolicyError):
            _persister(conn).save_policy(_policy(limits={"k": 0.1}))

    def test_unknown_version_raises(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        with pytest.raises(RiskPolicyError):
            p.get_version("risk-core", 99)
        with pytest.raises(RiskPolicyError):
            p.get_version("ghost", 1)


# ──────────────────────────────────────────────────────────────────────────────
# 激活版本原子热加载
# ──────────────────────────────────────────────────────────────────────────────


class TestActivation:
    def test_activate_hot_loads_active_pointer(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.save_policy(_policy(limits=_LIMITS_V2))
        active = p.activate("risk-core", 2)
        assert active.is_active is True
        assert p.active_policy("risk-core").limits == _LIMITS_V2

    def test_activate_switch_is_atomic_single_active(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.save_policy(_policy(limits=_LIMITS_V2))
        p.activate("risk-core", 1)
        p.activate("risk-core", 2)
        rows = conn.execute(
            "SELECT COUNT(*) FROM risk_policy_version WHERE policy_id='risk-core' AND is_active=1"
        ).fetchone()
        assert rows[0] == 1  # 任意时刻仅一个激活版本
        assert p.active_policy("risk-core").version == 2

    def test_activate_unknown_version_raises(self, conn) -> None:
        p = _persister(conn)
        with pytest.raises(RiskPolicyError):
            p.activate("risk-core", 1)
        assert p.active_policy("risk-core") is None

    def test_active_pointer_recovered_on_reinit(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.activate("risk-core", 1)
        p2 = _persister(conn)  # 重建（热加载语义：从库内恢复激活指针）
        assert p2.active_policy("risk-core").version == 1


# ──────────────────────────────────────────────────────────────────────────────
# 与 risk_limits 双向同步校验（漂移清单）
# ──────────────────────────────────────────────────────────────────────────────


class TestSyncCheck:
    def test_no_drift_when_aligned(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.activate("risk-core", 1)
        assert p.sync_check("risk-core", dict(_LIMITS_V1)) == ()

    def test_value_mismatch_drift(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.activate("risk-core", 1)
        drifts = p.sync_check(
            "risk-core",
            {"max_single_position": Decimal("0.12"), "max_gross_leverage": Decimal("1.0")},
        )
        assert drifts == (
            PolicyDrift(
                limit_key="max_single_position",
                persisted=Decimal("0.10"),
                live=Decimal("0.12"),
            ),
        )

    def test_bidirectional_missing_keys(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.activate("risk-core", 1)
        drifts = p.sync_check(
            "risk-core",
            {"max_single_position": Decimal("0.10"), "max_drawdown_limit": Decimal("0.05")},
        )
        # 双向：persisted 缺 max_drawdown_limit / live 缺 max_gross_leverage
        assert [(d.limit_key, d.persisted, d.live) for d in drifts] == [
            ("max_drawdown_limit", None, Decimal("0.05")),
            ("max_gross_leverage", Decimal("1.0"), None),
        ]

    def test_drift_sorted_by_key(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.activate("risk-core", 1)
        drifts = p.sync_check("risk-core", {})
        assert [d.limit_key for d in drifts] == sorted(d.limit_key for d in drifts)

    def test_sync_check_without_active_raises(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())  # 未激活
        with pytest.raises(RiskPolicyError):
            p.sync_check("risk-core", dict(_LIMITS_V1))

    def test_sync_check_uses_active_version(self, conn) -> None:
        p = _persister(conn)
        p.save_policy(_policy())
        p.save_policy(_policy(limits=_LIMITS_V2))
        p.activate("risk-core", 2)
        assert p.sync_check("risk-core", dict(_LIMITS_V2)) == ()
