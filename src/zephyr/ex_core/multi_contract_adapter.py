# [BLUEPRINT] MOD-EX-055 | docs/03_modules/_domain_execution_core/multi_contract_adapter/blueprint.md
# [MODULE] zephyr.ex_core.multi_contract_adapter
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D_EX_CORE域内模块 ; D_GOVERNANCE契约治理
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ContractSchema不可变; 冻结契约禁止升级; 版本只升不降; 变更通知同步推送; 审计日志全量记录
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ContractAlreadyRegisteredError(ZA-EX-055-01); ContractNotFoundError(ZA-EX-055-02); ContractFrozenError(ZA-EX-055-03); InvalidVersionError(ZA-EX-055-04)
# [TESTS] tests/ex_core/test_multi_contract_adapter.py
# [A_module] module_id=MOD-EX-055 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_EX_CORE — Multi-Contract Adapter (多契约生产适配器)

D_EX_CORE 域的契约注册中心——管理 CTR-004 (Order) / CTR-005 (Fill) /
CTR-006 (PositionSnapshot) 三份跨域契约的 Schema 元数据、版本演进、
消费者注册和变更通知。

不是契约本身的定义（契约定义在 ``zephyr.shared.contracts.*``），而是契约的
**管理面**：谁生产、谁消费、什么版本、是否冻结、变更时通知谁。

设计真源: D-EX-CORE-55 "CTR-004/005/006 Schema+版本演进+消费者注册+变更通知"
蓝图: docs/03_modules/_domain_execution_core/multi_contract_adapter/blueprint.md
SSoT: depgraph MOD-EX-055

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 契约元数据 ContractSchema
#   fields: contract_id + name + version + producer_domain + consumer_domains + frozen + ssot_path + contract_class_path
#   code: register(schema) L149；预注册 CTR_004/005/006 L347-390
# - id: I2
#   name: 消费者回调 callback
#   fields: Callable[[ContractSchema], None]（契约变更时通知）
#   code: register_consumer(contract_id, callback) L177
# - id: I3
#   name: 版本升级请求
#   fields: new_version + changelog_entry + force
#   code: upgrade_version() L198-205
# 层: 算法
# - id: A1
#   name_zh: ① 契约注册与消费者登记
#   name_en: MultiContractRegistry.register / register_consumer
#   intro: 把契约元数据登记进注册表，并为契约挂消费者回调
#   desc: contract_id 查重（重复抛 ContractAlreadyRegisteredError）→ 建 _ContractEntry 写审计日志 → 消费者回调追加到 entry.consumer_callbacks
#   inputs: I1 I2
#   outputs: 已注册 ContractSchema
#   invariant: 同一 contract_id 不可重复注册；审计日志全量记录
# - id: A2
#   name_zh: ② 版本演进与变更通知
#   name_en: MultiContractRegistry.upgrade_version
#   intro: 校验冻结与版本只升不降，生成新Schema并同步通知所有消费者
#   desc: 冻结检查（force除外）→ _parse_version 元组比较禁止降级 → replace 生成新 Schema（changelog追加，force时解冻）→ 逐个调消费者回调（失败不阻断）→ 审计日志
#   inputs: I3 A1
#   outputs: 新版 ContractSchema
#   invariant: 版本只升不降；冻结契约禁止升级（除非force）；变更通知同步推送
# - id: A3
#   name_zh: ③ 多维度查询
#   name_en: get / list_by_producer / list_by_consumer / get_audit_log
#   intro: 按契约ID、生产域、消费域查契约元数据和审计日志
#   desc: _entries 字典直查 + 条件过滤；不存在抛 ContractNotFoundError
#   inputs: A1 A2
#   outputs: ContractSchema / list[ContractSchema] / audit_log
# 层: 输出
# - id: O1
#   name_zh: 契约元数据快照 ContractSchema
#   name_en: ContractSchema
#   intro: CTR-004/005/006三份跨域契约的生产者/消费者/版本/冻结状态快照
#   invariant: frozen 不可变；变更生成新实例
#   downstream: D_EX_CORE域内模块；D_GOVERNANCE契约治理
# - id: O2
#   name_zh: 契约审计日志
#   name_en: audit_log
#   intro: REGISTER/CONSUMER_REGISTER/UPGRADE/NOTIFY 全量操作日志
#   downstream: D_GOVERNANCE契约治理
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A2
# A1 --> A2
# A1 --> A3
# A2 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A1 --> O2
# A2 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "ContractSchema",
    "MultiContractRegistry",
    "ContractAlreadyRegisteredError",
    "ContractNotFoundError",
    "ContractFrozenError",
    "InvalidVersionError",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class ContractAlreadyRegisteredError(ZephyrBaseError):
    """重复注册同一 contract_id。"""

    error_code = "ZA-EX-055-01"


class ContractNotFoundError(ZephyrBaseError):
    """查询/升级不存在的契约。"""

    error_code = "ZA-EX-055-02"


class ContractFrozenError(ZephyrBaseError):
    """升级已冻结契约（无 --force）。"""

    error_code = "ZA-EX-055-03"


class InvalidVersionError(ZephyrBaseError):
    """版本号格式非法或降级。"""

    error_code = "ZA-EX-055-04"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


def _parse_version(version: str) -> tuple[int, ...]:
    """将语义版本字符串解析为可比较的元组。

    "1.0" → (1, 0); "2.1.3" → (2, 1, 3)

    Raises:
        InvalidVersionError: 格式非法。
    """
    parts = version.strip().split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError as exc:
        raise InvalidVersionError(f"版本号格式非法: {version!r} (期望 'X.Y' 或 'X.Y.Z' 语义版本)") from exc


@dataclass(frozen=True)
class ContractSchema:
    """契约元数据快照——不可变。

    描述一份跨域契约的 Schema 信息：谁生产、谁消费、什么版本、是否冻结。
    变更时生成新实例（replace），不就地修改。
    """

    contract_id: str  # "CTR-004"
    name: str  # "Order"
    version: str  # "1.0"
    producer_domain: str  # "D_EX_CORE"
    consumer_domains: tuple[str, ...]  # ("D_PORTFOLIO", "D_EX_SOR")
    frozen: bool  # 是否冻结（禁止升级）
    ssot_path: str  # "cross_layer_contracts.yaml -> CTR-004"
    contract_class_path: str  # "zephyr.shared.contracts.order.Order"
    changelog: tuple[str, ...] = ()  # 版本变更日志（每条一条）


@dataclass
class _ContractEntry:
    """可变内部状态——注册表内使用的可变条目（不对外暴露）。"""

    schema: ContractSchema
    consumer_callbacks: list[Callable[[ContractSchema], None]] = field(default_factory=list)
    audit_log: list[str] = field(default_factory=list)


class MultiContractRegistry:
    """契约注册表——管理契约元数据、版本演进、消费者注册和变更通知。

    用法::

        registry = ContractRegistry()
        registry.register(CTR_004_SCHEMA)
        registry.register_consumer("CTR-004", my_callback)
        # 升级契约版本时，my_callback 会被自动调用
        registry.upgrade_version("CTR-004", "1.1", "新增 time_in_force 字段")
    """

    def __init__(self) -> None:
        self._entries: dict[str, _ContractEntry] = {}

    # ── 注册 ──────────────────────────────────────────────────────────────

    def register(self, schema: ContractSchema) -> ContractSchema:
        """注册一份新契约。

        Raises:
            ContractAlreadyRegisteredError: contract_id 已存在。
        """
        if schema.contract_id in self._entries:
            raise ContractAlreadyRegisteredError(f"契约 {schema.contract_id} 已注册，不可重复注册")
        entry = _ContractEntry(schema=schema)
        entry.audit_log.append(
            f"REGISTER: {schema.contract_id} v{schema.version} "
            f"producer={schema.producer_domain} "
            f"consumers={list(schema.consumer_domains)} "
            f"frozen={schema.frozen}"
        )
        self._entries[schema.contract_id] = entry
        logger.info(
            "契约注册: %s (%s) v%s, producer=%s, consumers=%s",
            schema.contract_id,
            schema.name,
            schema.version,
            schema.producer_domain,
            list(schema.consumer_domains),
        )
        return schema

    def register_consumer(
        self,
        contract_id: str,
        callback: Callable[[ContractSchema], None],
    ) -> None:
        """为指定契约注册一个消费者回调（变更时通知）。

        Raises:
            ContractNotFoundError: contract_id 不存在。
        """
        entry = self._require_entry(contract_id)
        entry.consumer_callbacks.append(callback)
        entry.audit_log.append(f"CONSUMER_REGISTER: callback={callback.__qualname__}")
        logger.debug("消费者注册: %s <- %s", contract_id, callback.__qualname__)

    # ── 版本演进 ──────────────────────────────────────────────────────────

    def upgrade_version(
        self,
        contract_id: str,
        new_version: str,
        changelog_entry: str,
        *,
        force: bool = False,
    ) -> ContractSchema:
        """升级契约版本。

        生成新的 ContractSchema（版本递增 + changelog 追加），
        通知所有已注册消费者回调。

        Args:
            contract_id: 契约 ID。
            new_version: 新版本号（必须大于当前版本）。
            changelog_entry: 变更说明。
            force: 是否强制升级冻结契约。

        Raises:
            ContractNotFoundError: contract_id 不存在。
            ContractFrozenError: 契约已冻结且 force=False。
            InvalidVersionError: 版本号非法或降级。
        """
        entry = self._require_entry(contract_id)
        old_schema = entry.schema

        # 冻结检查
        if old_schema.frozen and not force:
            raise ContractFrozenError(
                f"契约 {contract_id} 已冻结 (frozen=True)，禁止版本升级。如需强制升级，使用 force=True"
            )

        # 版本降级检查
        old_parsed = _parse_version(old_schema.version)
        new_parsed = _parse_version(new_version)
        if new_parsed <= old_parsed:
            raise InvalidVersionError(f"版本降级或未变: {old_schema.version} -> {new_version} (新版本必须大于当前版本)")

        # 生成新 schema
        new_changelog = old_schema.changelog + (f"v{old_schema.version}→v{new_version}: {changelog_entry}",)
        new_schema = replace(
            old_schema,
            version=new_version,
            changelog=new_changelog,
            # force 升级时解除冻结
            frozen=old_schema.frozen if not force else False,
        )
        entry.schema = new_schema
        entry.audit_log.append(
            f"UPGRADE: {contract_id} {old_schema.version} -> {new_version}"
            f"{' (FORCE)' if force and old_schema.frozen else ''}"
            f" | {changelog_entry}"
        )

        logger.info(
            "契约升级: %s %s -> %s%s | %s",
            contract_id,
            old_schema.version,
            new_version,
            " (FORCE)" if force and old_schema.frozen else "",
            changelog_entry,
        )

        # 通知消费者
        notified = 0
        for cb in entry.consumer_callbacks:
            try:
                cb(new_schema)
                notified += 1
            except Exception:  # noqa: BLE001 — 通知失败不阻断升级
                logger.warning(
                    "消费者通知失败: %s <- %s",
                    contract_id,
                    cb.__qualname__,
                    exc_info=True,
                )
        entry.audit_log.append(f"NOTIFY: {notified}/{len(entry.consumer_callbacks)} consumers notified")

        return new_schema

    # ── 查询 ──────────────────────────────────────────────────────────────

    def get(self, contract_id: str) -> ContractSchema:
        """查询契约元数据。

        Raises:
            ContractNotFoundError: contract_id 不存在。
        """
        return self._require_entry(contract_id).schema

    def list_contracts(self) -> list[ContractSchema]:
        """列出所有已注册契约。"""
        return [e.schema for e in self._entries.values()]

    def list_by_producer(self, domain: str) -> list[ContractSchema]:
        """按生产域查询契约。"""
        return [e.schema for e in self._entries.values() if e.schema.producer_domain == domain]

    def list_by_consumer(self, domain: str) -> list[ContractSchema]:
        """按消费域查询契约。"""
        return [e.schema for e in self._entries.values() if domain in e.schema.consumer_domains]

    def get_audit_log(self, contract_id: str) -> list[str]:
        """获取契约的审计日志。

        Raises:
            ContractNotFoundError: contract_id 不存在。
        """
        return list(self._require_entry(contract_id).audit_log)

    @property
    def count(self) -> int:
        """已注册契约数量。"""
        return len(self._entries)

    # ── 内部 ──────────────────────────────────────────────────────────────

    def _require_entry(self, contract_id: str) -> _ContractEntry:
        """获取条目，不存在则抛 ContractNotFoundError。"""
        entry = self._entries.get(contract_id)
        if entry is None:
            raise ContractNotFoundError(f"契约 {contract_id} 未注册")
        return entry


# ──────────────────────────────────────────────────────────────────────────────
# 预注册: CTR-004 / CTR-005 / CTR-006
# ──────────────────────────────────────────────────────────────────────────────

#: CTR-004 Order 契约 Schema（D_EX_CORE 生产 → D_PORTFOLIO / D_EX_SOR 消费）
CTR_004_ORDER: Final[ContractSchema] = ContractSchema(
    contract_id="CTR-004",
    name="Order",
    version="1.0",
    producer_domain="D_EX_CORE",
    consumer_domains=("D_PORTFOLIO", "D_EX_SOR"),
    frozen=True,
    ssot_path="cross_layer_contracts.yaml -> CTR-004",
    contract_class_path="zephyr.shared.contracts.order.Order",
    changelog=("v1.0: 初始版本 (冻结)",),
)

#: CTR-005 Fill 契约 Schema（D_EX_CORE 生产 → D_REPORTING 消费）
CTR_005_FILL: Final[ContractSchema] = ContractSchema(
    contract_id="CTR-005",
    name="Fill",
    version="1.0",
    producer_domain="D_EX_CORE",
    consumer_domains=("D_REPORTING",),
    frozen=True,
    ssot_path="cross_layer_contracts.yaml -> CTR-005",
    contract_class_path="zephyr.shared.contracts.fill.Fill",
    changelog=("v1.0: 初始版本 (冻结)",),
)

#: CTR-006 PositionSnapshot 契约 Schema（D_EX_CORE 生产 → D_RISK / D_REPORTING / D_ML 消费）
CTR_006_POSITION: Final[ContractSchema] = ContractSchema(
    contract_id="CTR-006",
    name="PositionSnapshot",
    version="1.0",
    producer_domain="D_EX_CORE",
    consumer_domains=("D_RISK", "D_REPORTING", "D_ML"),
    frozen=True,
    ssot_path="cross_layer_contracts.yaml -> CTR-006",
    contract_class_path="zephyr.shared.contracts.position.PositionSnapshot",
    changelog=("v1.0: 初始版本 (冻结)",),
)

#: 全部预注册契约
DEFAULT_CONTRACTS: Final[tuple[ContractSchema, ...]] = (
    CTR_004_ORDER,
    CTR_005_FILL,
    CTR_006_POSITION,
)


def create_default_registry() -> MultiContractRegistry:
    """创建并返回预注册了 CTR-004/005/006 的契约注册表。

    用法::

        registry = create_default_registry()
        # registry 已包含 CTR-004/005/006，可直接注册消费者或查询
    """
    registry = MultiContractRegistry()
    for schema in DEFAULT_CONTRACTS:
        registry.register(schema)
    return registry
