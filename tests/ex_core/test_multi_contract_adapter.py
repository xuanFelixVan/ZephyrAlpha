# [BLUEPRINT] MOD-EX-056 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""测试 multi_contract_adapter——契约注册中心。"""

from __future__ import annotations

import pytest

from zephyr.ex_core.multi_contract_adapter import (
    CTR_004_ORDER,
    CTR_005_FILL,
    CTR_006_POSITION,
    ContractAlreadyRegisteredError,
    ContractFrozenError,
    ContractNotFoundError,
    ContractSchema,
    InvalidVersionError,
    MultiContractRegistry,
    create_default_registry,
)

# ──────────────────────────────────────────────────────────────────────────────
# fixtures
# ──────────────────────────────────────────────────────────────────────────────


def make_schema(
    contract_id: str = "CTR-TEST",
    name: str = "Test",
    version: str = "1.0",
    producer: str = "D_TEST",
    consumers: tuple[str, ...] = ("D_CONSUMER",),
    frozen: bool = False,
    changelog: tuple[str, ...] = ("v1.0: test",),
) -> ContractSchema:
    return ContractSchema(
        contract_id=contract_id,
        name=name,
        version=version,
        producer_domain=producer,
        consumer_domains=consumers,
        frozen=frozen,
        ssot_path="test.yaml",
        contract_class_path="test.Test",
        changelog=changelog,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注册测试
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_single(self):
        reg = MultiContractRegistry()
        schema = make_schema()
        reg.register(schema)
        assert reg.count == 1
        assert reg.get("CTR-TEST") is schema

    def test_register_duplicate_raises(self):
        reg = MultiContractRegistry()
        reg.register(make_schema())
        with pytest.raises(ContractAlreadyRegisteredError, match="已注册"):
            reg.register(make_schema())

    def test_register_multiple(self):
        reg = MultiContractRegistry()
        reg.register(make_schema("CTR-A"))
        reg.register(make_schema("CTR-B"))
        reg.register(make_schema("CTR-C"))
        assert reg.count == 3


# ──────────────────────────────────────────────────────────────────────────────
# 消费者注册测试
# ──────────────────────────────────────────────────────────────────────────────


class TestConsumerRegistration:
    def test_register_consumer(self):
        reg = MultiContractRegistry()
        reg.register(make_schema())
        called: list[ContractSchema] = []

        def callback(schema: ContractSchema) -> None:
            called.append(schema)

        reg.register_consumer("CTR-TEST", callback)
        # 升级以触发回调
        reg.upgrade_version("CTR-TEST", "1.1", "test change")
        assert len(called) == 1
        assert called[0].version == "1.1"

    def test_register_consumer_not_found(self):
        reg = MultiContractRegistry()
        with pytest.raises(ContractNotFoundError):
            reg.register_consumer("CTR-MISSING", lambda s: None)

    def test_multiple_consumers_notified(self):
        reg = MultiContractRegistry()
        reg.register(make_schema())
        calls: list[str] = []

        reg.register_consumer("CTR-TEST", lambda s: calls.append("A"))
        reg.register_consumer("CTR-TEST", lambda s: calls.append("B"))
        reg.upgrade_version("CTR-TEST", "1.1", "change")
        assert calls == ["A", "B"]


# ──────────────────────────────────────────────────────────────────────────────
# 版本升级测试
# ──────────────────────────────────────────────────────────────────────────────


class TestVersionUpgrade:
    def test_upgrade_success(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=False))
        new_schema = reg.upgrade_version("CTR-TEST", "1.1", "新增字段")
        assert new_schema.version == "1.1"
        assert reg.get("CTR-TEST").version == "1.1"
        assert "v1.0→v1.1: 新增字段" in new_schema.changelog

    def test_upgrade_preserves_old_changelog(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=False, changelog=("v1.0: init",)))
        new_schema = reg.upgrade_version("CTR-TEST", "2.0", "大版本升级")
        assert "v1.0: init" in new_schema.changelog
        assert "v1.0→v2.0: 大版本升级" in new_schema.changelog

    def test_upgrade_not_found(self):
        reg = MultiContractRegistry()
        with pytest.raises(ContractNotFoundError):
            reg.upgrade_version("CTR-MISSING", "1.1", "change")

    def test_upgrade_frozen_raises(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=True))
        with pytest.raises(ContractFrozenError, match="已冻结"):
            reg.upgrade_version("CTR-TEST", "1.1", "change")

    def test_upgrade_frozen_force(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=True))
        new_schema = reg.upgrade_version(
            "CTR-TEST", "1.1", "强制升级", force=True
        )
        assert new_schema.version == "1.1"
        assert new_schema.frozen is False  # force 升级解除冻结

    def test_upgrade_downgrade_raises(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(version="2.0", frozen=False))
        with pytest.raises(InvalidVersionError, match="降级"):
            reg.upgrade_version("CTR-TEST", "1.0", "downgrade")

    def test_upgrade_same_version_raises(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(version="1.0", frozen=False))
        with pytest.raises(InvalidVersionError, match="降级或未变"):
            reg.upgrade_version("CTR-TEST", "1.0", "no change")

    def test_upgrade_invalid_version_format(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=False))
        with pytest.raises(InvalidVersionError, match="格式非法"):
            reg.upgrade_version("CTR-TEST", "abc", "bad version")

    def test_upgrade_multi_digit(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(version="1.10", frozen=False))
        new_schema = reg.upgrade_version("CTR-TEST", "1.11", "patch")
        assert new_schema.version == "1.11"

    def test_upgrade_notifies_consumers(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=False))
        notified: list[str] = []
        reg.register_consumer("CTR-TEST", lambda s: notified.append(s.version))
        reg.upgrade_version("CTR-TEST", "1.1", "change")
        assert notified == ["1.1"]

    def test_upgrade_consumer_callback_error_doesnt_block(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=False))

        def bad_callback(s: ContractSchema) -> None:
            raise RuntimeError("callback error")

        reg.register_consumer("CTR-TEST", bad_callback)
        # 升级不应被回调异常阻断
        new_schema = reg.upgrade_version("CTR-TEST", "1.1", "change")
        assert new_schema.version == "1.1"


# ──────────────────────────────────────────────────────────────────────────────
# 查询测试
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_not_found(self):
        reg = MultiContractRegistry()
        with pytest.raises(ContractNotFoundError):
            reg.get("CTR-MISSING")

    def test_list_contracts(self):
        reg = MultiContractRegistry()
        reg.register(make_schema("CTR-A"))
        reg.register(make_schema("CTR-B"))
        ids = [s.contract_id for s in reg.list_contracts()]
        assert set(ids) == {"CTR-A", "CTR-B"}

    def test_list_by_producer(self):
        reg = MultiContractRegistry()
        reg.register(make_schema("CTR-A", producer="D_EX_CORE"))
        reg.register(make_schema("CTR-B", producer="D_REPORTING"))
        result = reg.list_by_producer("D_EX_CORE")
        assert len(result) == 1
        assert result[0].contract_id == "CTR-A"

    def test_list_by_consumer(self):
        reg = MultiContractRegistry()
        reg.register(
            make_schema("CTR-A", consumers=("D_RISK", "D_REPORTING"))
        )
        reg.register(make_schema("CTR-B", consumers=("D_REPORTING",)))
        risk_result = reg.list_by_consumer("D_RISK")
        assert len(risk_result) == 1
        assert risk_result[0].contract_id == "CTR-A"
        report_result = reg.list_by_consumer("D_REPORTING")
        assert len(report_result) == 2


# ──────────────────────────────────────────────────────────────────────────────
# 审计日志测试
# ──────────────────────────────────────────────────────────────────────────────


class TestAuditLog:
    def test_register_audit(self):
        reg = MultiContractRegistry()
        reg.register(make_schema())
        log = reg.get_audit_log("CTR-TEST")
        assert any("REGISTER" in entry for entry in log)

    def test_upgrade_audit(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=False))
        reg.upgrade_version("CTR-TEST", "1.1", "change")
        log = reg.get_audit_log("CTR-TEST")
        assert any("UPGRADE" in entry for entry in log)
        assert any("NOTIFY" in entry for entry in log)

    def test_consumer_register_audit(self):
        reg = MultiContractRegistry()
        reg.register(make_schema())
        reg.register_consumer("CTR-TEST", lambda s: None)
        log = reg.get_audit_log("CTR-TEST")
        assert any("CONSUMER_REGISTER" in entry for entry in log)

    def test_force_upgrade_audit(self):
        reg = MultiContractRegistry()
        reg.register(make_schema(frozen=True))
        reg.upgrade_version("CTR-TEST", "1.1", "force", force=True)
        log = reg.get_audit_log("CTR-TEST")
        assert any("FORCE" in entry for entry in log)

    def test_audit_log_not_found(self):
        reg = MultiContractRegistry()
        with pytest.raises(ContractNotFoundError):
            reg.get_audit_log("CTR-MISSING")


# ──────────────────────────────────────────────────────────────────────────────
# 预注册 / 默认注册表测试
# ──────────────────────────────────────────────────────────────────────────────


class TestDefaultRegistry:
    def test_create_default_registry(self):
        reg = create_default_registry()
        assert reg.count == 3
        assert reg.get("CTR-004").name == "Order"
        assert reg.get("CTR-005").name == "Fill"
        assert reg.get("CTR-006").name == "PositionSnapshot"

    def test_default_contracts_frozen(self):
        reg = create_default_registry()
        for cid in ("CTR-004", "CTR-005", "CTR-006"):
            assert reg.get(cid).frozen is True

    def test_default_ctr004_consumers(self):
        reg = create_default_registry()
        schema = reg.get("CTR-004")
        assert "D_PORTFOLIO" in schema.consumer_domains
        assert "D_EX_SOR" in schema.consumer_domains

    def test_default_ctr006_consumers(self):
        reg = create_default_registry()
        schema = reg.get("CTR-006")
        assert "D_RISK" in schema.consumer_domains
        assert "D_REPORTING" in schema.consumer_domains
        assert "D_ML" in schema.consumer_domains

    def test_default_list_by_producer(self):
        reg = create_default_registry()
        ex_core_contracts = reg.list_by_producer("D_EX_CORE")
        assert len(ex_core_contracts) == 3

    def test_default_frozen_upgrade_raises(self):
        reg = create_default_registry()
        with pytest.raises(ContractFrozenError):
            reg.upgrade_version("CTR-004", "1.1", "change")

    def test_ctr004_constant(self):
        assert CTR_004_ORDER.contract_id == "CTR-004"
        assert CTR_004_ORDER.version == "1.0"

    def test_ctr005_constant(self):
        assert CTR_005_FILL.contract_id == "CTR-005"
        assert CTR_005_FILL.frozen is True

    def test_ctr006_constant(self):
        assert CTR_006_POSITION.contract_id == "CTR-006"
        assert len(CTR_006_POSITION.consumer_domains) == 3


# ──────────────────────────────────────────────────────────────────────────────
# ContractSchema 不可变性测试
# ──────────────────────────────────────────────────────────────────────────────


class TestImmutability:
    def test_schema_is_frozen(self):
        schema = make_schema()
        with pytest.raises(AttributeError):
            schema.version = "2.0"  # type: ignore[misc]

    def test_schema_replace_creates_new(self):
        schema = make_schema()
        from dataclasses import replace

        new_schema = replace(schema, version="1.1")
        assert schema.version == "1.0"
        assert new_schema.version == "1.1"
        assert new_schema is not schema
