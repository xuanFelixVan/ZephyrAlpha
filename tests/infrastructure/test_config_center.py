# [BLUEPRINT] MOD-INF-091 | docs/03_modules/_domain_infrastructure_operations/config_center/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-091 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_config_center
# [TESTS] src/zephyr/infrastructure/config/config_center.py
"""MOD-INF-091 单元测试：config_center 统一配置中心。

蓝图验收（B1-00203/CAND-INFRASTR-001，C2）：
统一配置注册表 + 版本快照（每次 set version 递增+快照留存）+ 变更审计
日志（注入 audit_sink）+ 回滚 rollback(key, to_version) + 热更新守卫钩
子（set/rollback 前 guard 校验拒绝即 Fail-Closed）+ list_versions。
audit/guard/clock 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.config.config_center",
    reason="config_center not importable",
)

from zephyr.infrastructure.config.config_center import (  # noqa: E402
    ConfigCenter,
    ConfigCenterError,
    ConfigChange,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _center(audits: list | None = None, guard=None) -> ConfigCenter:
    return ConfigCenter(
        audit_sink=(lambda c: audits.append(c)) if audits is not None else None,
        guard=guard,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok_version_1(self) -> None:
        cc = _center()
        assert cc.register("risk.max_drawdown", 0.05, {"owner": "risk"}) == 1
        assert cc.get("risk.max_drawdown") == 0.05
        assert cc.version_of("risk.max_drawdown") == 1

    def test_duplicate_register_raises(self) -> None:
        cc = _center()
        cc.register("k", 1)
        with pytest.raises(ConfigCenterError):
            cc.register("k", 2)

    def test_empty_key_raises(self) -> None:
        with pytest.raises(ConfigCenterError):
            _center().register("", 1)


# ──────────────────────────────────────────────────────────────────────────────
# 变更（版本递增 + 审计 + 守卫）
# ──────────────────────────────────────────────────────────────────────────────


class TestSet:
    def test_unknown_key_raises(self) -> None:
        with pytest.raises(ConfigCenterError):
            _center().set("ghost", 1)

    def test_version_increments_and_snapshots(self) -> None:
        cc = _center()
        cc.register("k", 1)
        assert cc.set("k", 2) == 2
        assert cc.set("k", 3, {"reason": "tune"}) == 3
        assert cc.get("k") == 3
        assert cc.list_versions("k") == (1, 2, 3)
        assert cc.snapshot_of("k", 1).value == 1  # 快照留存
        assert cc.snapshot_of("k", 2).value == 2
        assert cc.snapshot_of("k", 3).meta == {"reason": "tune"}

    def test_audit_trail(self) -> None:
        audits: list[ConfigChange] = []
        cc = _center(audits=audits)
        cc.register("k", 1)
        cc.set("k", 2)
        assert [(c.kind, c.from_version, c.to_version) for c in audits] == [
            ("register", None, 1),
            ("set", 1, 2),
        ]
        assert all(c.at == _T0 for c in audits)

    def test_guard_reject_fail_closed_no_version_bump(self) -> None:
        cc = _center(guard=lambda k, old, new: False)
        cc.register("k", 1)
        with pytest.raises(ConfigCenterError):
            cc.set("k", 2)
        assert cc.version_of("k") == 1  # 拒绝不落新版本

    def test_guard_exception_fail_closed(self) -> None:
        def _boom(k: str, old: object, new: object) -> bool:
            raise RuntimeError("guard io")

        cc = _center(guard=_boom)
        cc.register("k", 1)
        with pytest.raises(ConfigCenterError):
            cc.set("k", 2)

    def test_guard_receives_old_new(self) -> None:
        seen: list = []
        cc = _center(guard=lambda k, old, new: seen.append((k, old, new)) or True)
        cc.register("k", 1)
        cc.set("k", 2)
        assert seen == [("k", 1, 2)]

    def test_audit_sink_exception_non_blocking(self) -> None:
        def _boom(c: ConfigChange) -> None:
            raise RuntimeError("audit io")

        cc = ConfigCenter(audit_sink=_boom, clock=lambda: _T0)
        cc.register("k", 1)  # 审计异常不阻断主路
        assert cc.get("k") == 1


# ──────────────────────────────────────────────────────────────────────────────
# 回滚
# ──────────────────────────────────────────────────────────────────────────────


class TestRollback:
    def test_rollback_creates_new_version_with_old_value(self) -> None:
        audits: list[ConfigChange] = []
        cc = _center(audits=audits)
        cc.register("k", 1)
        cc.set("k", 2)
        cc.set("k", 3)
        assert cc.rollback("k", 1) == 4
        assert cc.get("k") == 1
        assert cc.list_versions("k") == (1, 2, 3, 4)
        assert audits[-1].kind == "rollback"
        assert cc.snapshot_of("k", 4).value == 1

    def test_rollback_unknown_key_raises(self) -> None:
        with pytest.raises(ConfigCenterError):
            _center().rollback("ghost", 1)

    def test_rollback_unknown_version_raises(self) -> None:
        cc = _center()
        cc.register("k", 1)
        with pytest.raises(ConfigCenterError):
            cc.rollback("k", 99)

    def test_rollback_guarded(self) -> None:
        cc = _center(guard=lambda k, old, new: False)
        cc.register("k", 1)
        with pytest.raises(ConfigCenterError):
            cc.rollback("k", 1)


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_unknown_key_raises(self) -> None:
        with pytest.raises(ConfigCenterError):
            _center().get("ghost")

    def test_version_of_unknown_key_raises(self) -> None:
        with pytest.raises(ConfigCenterError):
            _center().version_of("ghost")

    def test_snapshot_unknown_version_raises(self) -> None:
        cc = _center()
        cc.register("k", 1)
        with pytest.raises(ConfigCenterError):
            cc.snapshot_of("k", 2)

    def test_list_versions_sorted_deterministic(self) -> None:
        cc = _center()
        cc.register("k", "a")
        for v in "bcd":
            cc.set("k", v)
        assert cc.list_versions("k") == (1, 2, 3, 4)
        assert cc.list_versions("k") == cc.list_versions("k")  # 同输入必同输出

    def test_multi_key_isolation(self) -> None:
        cc = _center()
        cc.register("a", 1)
        cc.register("b", 2)
        cc.set("a", 10)
        assert cc.get("a") == 10 and cc.get("b") == 2
        assert cc.version_of("a") == 2 and cc.version_of("b") == 1
