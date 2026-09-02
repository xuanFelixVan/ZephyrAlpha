# [BLUEPRINT] MOD-INT-MATRIX | docs/03_modules/_domain_integration/integration_matrix_registry/blueprint.md
# [MODULE] zephyr.integration.integration_matrix_registry
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] 无（协议核心纯内存；clock 全注入）
# [CONSUMERS] 运行时装配批（外部系统交互矩阵装配 / 数据源故障降级策略声明 / 隔离规则配置化校验）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 协议/隔离策略词表闭合; (系统,交互) 二元组唯一; 同条目重复注册幂等、冲突注册拒绝; 降级链非空且系统均已注册且不含自身; 隔离规则 schema 校验 Fail-Closed; 查询按 (系统,交互) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_integration/integration_matrix_registry/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] IntegrationMatrixError(占位 ZA-INT-UNREGISTERED-INTEGRATION-MATRIX)——空要素/未知枚举/条目冲突/未知系统/降级链非法/规则schema违约时抛
# [TESTS] tests/integration/test_integration_matrix_registry.py
# [A_module] module_id=MOD-INT-MATRIX | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""IntegrationMatrixRegistry — 集成交互矩阵注册表（MOD-INT-MATRIX）。

B14-04736（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-BACL-005，A10 v6.0）：
外部系统交互矩阵**契约注册表**（系统 × 交互 × 协议 × 隔离策略四要素）
+ 数据源故障**降级策略声明**（降级链表）+ 隔离规则**配置化**（规则 schema
+ 校验，Fail-Closed）。

查重分工：ports.py=pipeline→mcp 结构接口抽象（本件=外部系统交互契约注册，
零交集）；external_system_connector=连接器运行时（本件只登记契约不发连接）；
failover_coordinator=运行时切换执行（本件只声明降级链策略，不执行切换）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "Integration",
    "IntegrationMatrixError",
    "IntegrationMatrixRegistry",
    "IsolationPolicy",
    "ProtocolKind",
]

#: 隔离规则 schema 必填键（配置化校验真源）
_RULE_REQUIRED_KEYS: Final[frozenset[str]] = frozenset({"system", "interaction", "protocol", "isolation"})


class IntegrationMatrixError(Exception):
    """集成交互矩阵输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INT-UNREGISTERED-INTEGRATION-MATRIX。
    """


class ProtocolKind(str, Enum):
    """交互协议词表（闭合）。"""

    REST = "rest"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MQ = "mq"
    FILE = "file"
    SQL = "sql"
    IN_PROCESS = "in_process"


class IsolationPolicy(str, Enum):
    """隔离策略词表（闭合）。"""

    NONE = "none"
    PROCESS = "process"
    CONTAINER = "container"
    NETWORK = "network"
    SANDBOX = "sandbox"


@dataclass(frozen=True)
class Integration:
    """交互矩阵条目（系统×交互×协议×隔离策略四要素，frozen）。"""

    system: str
    interaction: str
    protocol: ProtocolKind
    isolation: IsolationPolicy
    registered_at: datetime.datetime


class IntegrationMatrixRegistry:
    """集成交互矩阵注册表（四要素契约 + 降级链 + 隔离规则校验）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._entries: dict[tuple[str, str], Integration] = {}
        self._fallback_chains: dict[str, tuple[str, ...]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _entry(self, system: str, interaction: str) -> Integration:
        entry = self._entries.get((system, interaction))
        if entry is None:
            raise IntegrationMatrixError(f"未知交互: ({system!r}, {interaction!r})（未注册）")
        return entry

    def _require_system(self, system: str) -> None:
        if not any(e.system == system for e in self._entries.values()):
            raise IntegrationMatrixError(f"未知系统: {system!r}（无任何已注册交互）")

    # ── 四要素注册 ────────────────────────────────────────────────────────

    def register(
        self,
        system: str,
        interaction: str,
        protocol: ProtocolKind,
        isolation: IsolationPolicy,
    ) -> Integration:
        """登记四要素条目：同条目幂等；同键冲突（协议/隔离不同）拒绝。"""
        if not system:
            raise IntegrationMatrixError("system 为空")
        if not interaction:
            raise IntegrationMatrixError("interaction 为空")
        if not isinstance(protocol, ProtocolKind):
            raise IntegrationMatrixError(f"非法协议: {protocol!r}")
        if not isinstance(isolation, IsolationPolicy):
            raise IntegrationMatrixError(f"非法隔离策略: {isolation!r}")
        key = (system, interaction)
        existing = self._entries.get(key)
        if existing is not None:
            if existing.protocol is protocol and existing.isolation is isolation:
                return existing  # 幂等
            raise IntegrationMatrixError(
                f"条目冲突: {key!r} 已登记 {existing.protocol.value}/{existing.isolation.value}，"
                f"拒绝覆盖为 {protocol.value}/{isolation.value}"
            )
        entry = Integration(
            system=system,
            interaction=interaction,
            protocol=protocol,
            isolation=isolation,
            registered_at=self._clock(),
        )
        self._entries[key] = entry
        return entry

    # ── 隔离规则配置化（schema 校验） ───────────────────────────────────────

    def register_rule(self, rule: Mapping) -> Integration:
        """隔离规则配置化入口：schema 校验通过则登记四要素条目。"""
        self.validate_isolation_rule(rule)
        return self.register(
            system=rule["system"],
            interaction=rule["interaction"],
            protocol=ProtocolKind(rule["protocol"]),
            isolation=IsolationPolicy(rule["isolation"]),
        )

    @staticmethod
    def validate_isolation_rule(rule: Mapping) -> None:
        """隔离规则 schema 校验（Fail-Closed）：必填键/类型/枚举取值域。"""
        if not isinstance(rule, Mapping):
            raise IntegrationMatrixError(f"规则须为 Mapping: {type(rule).__name__}")
        missing = _RULE_REQUIRED_KEYS - rule.keys()
        if missing:
            raise IntegrationMatrixError(f"规则缺必填键: {sorted(missing)}")
        for key in ("system", "interaction", "protocol", "isolation"):
            if not isinstance(rule[key], str) or not rule[key]:
                raise IntegrationMatrixError(f"规则键 {key!r} 须为非空字符串")
        try:
            ProtocolKind(rule["protocol"])
        except ValueError as exc:
            raise IntegrationMatrixError(f"非法协议取值: {rule['protocol']!r}") from exc
        try:
            IsolationPolicy(rule["isolation"])
        except ValueError as exc:
            raise IntegrationMatrixError(f"非法隔离策略取值: {rule['isolation']!r}") from exc

    # ── 故障降级链（策略声明） ──────────────────────────────────────────────

    def set_fallback_chain(self, system: str, chain: tuple[str, ...] | list[str]) -> None:
        """声明系统故障降级链：链非空、无重复、不含自身、链内系统均已注册。"""
        self._require_system(system)
        chain_t = tuple(chain)
        if not chain_t:
            raise IntegrationMatrixError("降级链为空")
        if len(set(chain_t)) != len(chain_t):
            raise IntegrationMatrixError(f"降级链含重复系统: {chain_t!r}")
        if system in chain_t:
            raise IntegrationMatrixError(f"降级链含自身: {system!r}")
        for member in chain_t:
            self._require_system(member)
        self._fallback_chains[system] = chain_t
        _log.info("降级链已声明: %s -> %s", system, chain_t)

    def fallback_chain_of(self, system: str) -> tuple[str, ...]:
        """系统降级链视图（未声明 → 空 tuple）。"""
        self._require_system(system)
        return self._fallback_chains.get(system, ())

    def resolve_fallback(self, system: str, failed: frozenset[str] | set[str]) -> str | None:
        """按链解析首个未故障降级目标；链空或全故障 → None（不抛）。"""
        self._require_system(system)
        for member in self._fallback_chains.get(system, ()):
            if member not in failed:
                return member
        return None

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get(self, system: str, interaction: str) -> Integration:
        """单条目查询（未知 → Fail-Closed）。"""
        return self._entry(system, interaction)

    def interactions_of(self, system: str) -> tuple[Integration, ...]:
        """系统全部交互（按交互名确定性排序）。"""
        self._require_system(system)
        return tuple(
            sorted(
                (e for e in self._entries.values() if e.system == system),
                key=lambda e: e.interaction,
            )
        )

    def matrix(self) -> tuple[Integration, ...]:
        """全矩阵视图（按 (system, interaction) 确定性排序）。"""
        return tuple(sorted(self._entries.values(), key=lambda e: (e.system, e.interaction)))
