# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.registry
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.schema.schemas; zephyr.shared.infra.observer
# [CONSUMERS] orchestration.runtime_core.orchestrator.contract_registry
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha — shared/contracts/registry.py

CTR-VER-001: ContractRegistry / 契约版本注册与查询服务

运行时契约注册表。实现 VER-R1~R5 版本协商规则的可执行部分。
所有消费者在启动时 MUST 通过本注册表查询依赖契约的当前 active 版本。

设计原则
--------
- SSoT-backed: 启动时从 cross_layer_contracts.yaml 加载契约元数据
- 版本协商: 实现 VER-R1~R5 的运行时行为
- 消费者追踪: 记录哪些模块依赖哪些契约，用于影响分析
- 升级通知: 发布 contract_version_change 事件到 遥测 Telemetry
- 双版本支持: 过渡期内同时提供新旧版本适配器

用法
----
    from zephyr.shared.contracts.core.registry import ContractRegistry, get_registry

    registry = get_registry()
    registry.initialize()

    # 查询依赖契约的当前版本
    version = registry.get_active_version("CTR-001")
    adapter = registry.get_adapter("CTR-001", current_version=version)

    # 验证入站数据版本
    if not registry.check_version("CTR-001", incoming_schema_version):
        raise ContractViolationError(...)

SSoT: cross_layer_contracts.yaml -> CTR-VER-001
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.schema.schemas import Priority
from zephyr.shared.io.paths import REPO_ROOT

_logger = logging.getLogger("zephyr.shared.contracts.registry")


@dataclass
class ContractMeta:
    contract_id: str
    name: str
    schema_version: str
    source_layer: str
    target_layers: list[str] = field(default_factory=list)
    stability: str = ""
    frozen: bool = True
    priority: Priority = Priority.P0
    physical_path: str = ""
    description: str = ""


@dataclass
class VersionTransition:
    contract_id: str
    old_version: str
    new_version: str
    announced_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    migration_window_ms: int = 2_592_000_000  # 30 days in ms
    active: bool = True


class VersionMismatchError(ValueError):
    """VER-R2: MAJOR 版本不匹配时抛出。"""
    error_code = "ZA-SH-0026"

    def __init__(self, contract_id: str, expected_major: int, actual_major: int, *, error_code: str | None = None) -> None:
        self.contract_id = contract_id
        self.expected_major = expected_major
        self.actual_major = actual_major
        super().__init__(f"{contract_id}: MAJOR 版本不匹配 — 期望 MAJOR={expected_major}, 实际 MAJOR={actual_major}")
        if error_code is not None:
            self.error_code = error_code


class ContractRegistry:
    """运行时契约注册表。

    属性
    ----
    contracts : Dict[str, ContractMeta]
        已注册的契约元数据
    consumers : Dict[str, List[str]]
        {contract_id: [consumer_module_names]}
    transitions : List[VersionTransition]
        进行中的版本迁移
    """

    _ssot_path: str = (
        "architecture_model/contracts/cross_layer_contracts.yaml"
    )

    def __init__(self, repo_root: Path | None = None) -> None:
        self._contracts: dict[str, ContractMeta] = {}
        self._consumers: dict[str, list[str]] = defaultdict(list)
        self._transitions: list[VersionTransition] = []
        self._adapters: dict[str, dict[str, Any]] = {}
        self._initialized = False

        if repo_root is None:
            self._repo_root = REPO_ROOT
        else:
            self._repo_root = repo_root

    @property
    def contracts(self) -> dict[str, ContractMeta]:
        return dict(self._contracts)

    @property
    def consumers(self) -> dict[str, list[str]]:
        return dict(self._consumers)

    @property
    def transitions(self) -> list[VersionTransition]:
        return list(self._transitions)

    def initialize(self) -> None:
        """从 SSoT YAML 加载契约元数据，初始化注册表。

        VER-R5: 消费者在启动时 MUST 调用此方法查询契约的 active 版本。
        """
        if self._initialized:
            return

        yaml_path = self._repo_root / self._ssot_path
        if not yaml_path.exists():
            _logger.warning(
                "[ContractRegistry] SSoT YAML 未找到: %s — 使用空注册表",
                yaml_path,
            )
            self._initialized = True
            return

        try:
            import yaml

            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception as e:
            _logger.error("[ContractRegistry] YAML 加载失败: %s", e, exc_info=True)
            self._initialized = True
            return

        contracts = data.get("contracts", [])
        for ctr in contracts:
            meta = ContractMeta(
                contract_id=ctr["id"],
                name=ctr.get("name", ""),
                schema_version=ctr.get("schema_version", "1.0"),
                source_layer=ctr.get("source_layer", ""),
                target_layers=ctr.get("target_layers", []),
                stability=ctr.get("stability", ""),
                frozen=ctr.get("frozen", True),
                priority=Priority(ctr.get("priority", Priority.P1.value)),
                physical_path=ctr.get("physical_path", ""),
                description=ctr.get("description", ""),
            )
            self._contracts[ctr["id"]] = meta

        _logger.info(
            "[ContractRegistry] 已加载 %d 条契约定义",
            len(self._contracts),
        )
        self._initialized = True

    def get_active_version(self, contract_id: str) -> str | None:
        """VER-R5: 查询契约当前 active 版本。

        返回 schema_version 字符串 (如 "1.0")，如果契约不存在返回 None。
        """
        meta = self._contracts.get(contract_id)
        return meta.schema_version if meta else None

    def check_version(self, contract_id: str, incoming_version: str) -> bool:
        """VER-R1+R2: 检查入站数据的版本兼容性。

        返回 True 表示兼容（同 MAJOR），False 表示不兼容（MAJOR 不同）。
        不兼容时，调用者 MUST 拒绝处理并上报 遥测 Telemetry。
        """
        active = self.get_active_version(contract_id)
        if active is None:
            _logger.debug(
                "[ContractRegistry] %s 未注册 — 跳过版本检查",
                contract_id,
            )
            return True

        expected_major = self._parse_major(active)
        actual_major = self._parse_major(incoming_version)

        if expected_major != actual_major:
            _logger.error(
                "[ContractRegistry] VER-R2 触发: %s MAJOR=%d ≠ %d",
                contract_id,
                expected_major,
                actual_major,
            )
            return False

        return True

    def require_version(self, contract_id: str, incoming_version: str) -> None:
        """VER-R2: 强制版本检查——不兼容时抛出异常。"""
        if not self.check_version(contract_id, incoming_version):
            raise VersionMismatchError(
                contract_id,
                self._parse_major(self.get_active_version(contract_id) or "0"),
                self._parse_major(incoming_version),
            )

    def register_consumer(self, contract_id: str, module_name: str) -> None:
        """注册消费者模块。用于 VER-R3 升级通知广播。"""
        if module_name not in self._consumers.get(contract_id, []):
            self._consumers.setdefault(contract_id, []).append(module_name)
            _logger.debug(
                "[ContractRegistry] %s 注册消费者: %s",
                contract_id,
                module_name,
            )

    def announce_major_upgrade(self, contract_id: str, new_version: str) -> VersionTransition:
        """VER-R3: 发布 MAJOR 版本升级公告。

        自动通知所有注册消费者。过渡窗口默认 30 天。
        """
        transition = VersionTransition(
            contract_id=contract_id,
            old_version=self.get_active_version(contract_id) or "1.0",
            new_version=new_version,
        )
        self._transitions.append(transition)

        consumers = self._consumers.get(contract_id, [])
        _logger.warning(
            "[ContractRegistry] VER-R3: %s MAJOR 升级 %s -> %s — 通知 %d 个消费者，过渡窗口=%d ms",
            contract_id,
            transition.old_version,
            new_version,
            len(consumers),
            transition.migration_window_ms,
        )

        try:
            from zephyr.shared.infra.observer import EventType, Observer

            bus = Observer()
            bus.emit(
                EventType.METRIC_EVENT,
                {
                    "metric_name": "contract_violation",
                    "value": 1.0,
                    "unit": "count",
                    "labels": {
                        "contract_id": contract_id,
                        "old_version": transition.old_version,
                        "new_version": new_version,
                    },
                },
            )
        except Exception:
            _logger.debug(
                "[ContractRegistry] 无法发送 METRIC_EVENT: %s",
                contract_id,
                exc_info=True,
            )

        return transition

    def get_active_transitions(self) -> list[VersionTransition]:
        """返回当前进行中的版本迁移。"""
        now = datetime.now(UTC)
        active = []
        for t in self._transitions:
            elapsed = (now - t.announced_at).total_seconds() * 1000
            if elapsed < t.migration_window_ms and t.active:
                active.append(t)
        return active

    def register_adapter(
        self,
        contract_id: str,
        version: str,
        adapter: Any,
    ) -> None:
        """注册特定版本的契约适配器（VER-R4 双版本过渡期使用）。"""
        self._adapters.setdefault(contract_id, {})[version] = adapter
        _logger.info(
            "[ContractRegistry] 注册适配器: %s v%s",
            contract_id,
            version,
        )

    def get_adapter(self, contract_id: str, current_version: str) -> Any | None:
        """获取适配器——优先精确版本，回退到最新兼容版本。"""
        adapters_for_contract = self._adapters.get(contract_id, {})
        if current_version in adapters_for_contract:
            return adapters_for_contract[current_version]

        target_major = self._parse_major(current_version)
        for ver, adapter in sorted(adapters_for_contract.items(), reverse=True):
            if self._parse_major(ver) == target_major:
                return adapter

        return None

    def get_contract_meta(self, contract_id: str) -> ContractMeta | None:
        """查询契约元数据。"""
        return self._contracts.get(contract_id)

    def list_p0_contracts(self) -> list[ContractMeta]:
        """列出所有 P0 契约。"""
        return [m for m in self._contracts.values() if m.priority is Priority.P0]

    def list_by_layer(self, layer: str) -> list[ContractMeta]:
        """列出指定层涉及的所有契约（作为 source 或 target）。"""
        result: list[ContractMeta] = []
        for meta in self._contracts.values():
            if meta.source_layer == layer or layer in meta.target_layers:
                result.append(meta)
        return result

    def get_stats(self) -> dict[str, int]:
        """返回注册表统计信息。"""
        initialized = self._initialized
        return {
            "total_contracts": len(self._contracts),
            "p0_count": len([m for m in self._contracts.values() if m.priority is Priority.P0]),
            "p1_count": len([m for m in self._contracts.values() if m.priority is Priority.P1]),
            "registered_consumers": sum(len(c) for c in self._consumers.values()),
            "active_transitions": len(self.get_active_transitions()),
            "registered_adapters": sum(len(a) for a in self._adapters.values()),
            "initialized": initialized,
        }

    @staticmethod
    def _parse_major(version: str) -> int:
        try:
            return int(version.split(".")[0])
        except (ValueError, IndexError):
            return 0


from collections import defaultdict
import threading

_registry: ContractRegistry | None = None
_registry_lock = threading.Lock()


def get_registry(repo_root: Path | None = None) -> ContractRegistry:
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = ContractRegistry(repo_root=repo_root)
                _registry.initialize()
    return _registry


def reset_registry() -> None:
    global _registry
    _registry = None
