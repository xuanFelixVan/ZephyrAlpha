# [BLUEPRINT] MOD-AU-002 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.1-S0.3
# [MODULE] zephyr.autonomy_core.kill_switch_orchestrator
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] (lazy) zephyr.security.access_control.kill_switch; zephyr.autonomy_core.skills.skill_kill_switch; zephyr.trading.trading_contracts.risk.trading_kill_switch; zephyr.infrastructure.rollback.kill_switch; zephyr.infrastructure.capacity_assurance.kill_switch
# [CONSUMERS] tests/autonomy/test_kill_switch_orchestrator.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 编排器不持有开关状态(状态分散在各开关本体,编排器故障则各开关独立可用); 复位须 approver 非空(Owner 批准语义); 系统级 TRIPPED 时域级一致生效且域级不可单独复位
# [MODIFY-GUARD] Owner approval required; 变更须同步 15号文 §3.4 收敛规则
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] trip()/reset()/route_incident()/is_tripped()/check_consistency() 永不抛异常; 失败收入 OrchestrationResult.errors
# [TESTS] tests/autonomy/test_kill_switch_orchestrator.py
# [A_module] module_id=MOD-AU-002 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""KillSwitchOrchestrator — Kill Switch 两级编排器（MOD-AU-002）.

设计真源：15号文（15_autonomy_boundary_risk.md）§3.4 / §4.1-S0.3：
- 两级：系统级总开关（security/access_control/kill_switch.py，MOD-INF-018）
  + 域级分开关（trading 五级 / rollback 三级 / skills 熔断 / capacity 保障）。
  编排器只做路由与收敛，不持有开关状态、不改写既有 5 套实现（适配器包装，lazy import）。
- 收敛规则（§3.4）：①影响资金 → 先交易级、系统级兜底；②影响代码库/会话 → 系统级；
  ③域内故障 → 域级先行；④全局事故 → 只拉系统级总开关（域级一致生效由编排器传播保障）。
- 纪律：系统级 TRIPPED → 域级一致生效（对支持全域拉闸的域级开关传播 trip，
  查询面 is_tripped 走支配语义）；复位须 approver 非空（Owner 批准）；
  编排器自身故障 → 各开关独立可用（fail-open 分散态）。
- 事件产出按 16号文 §4.2 P0-1 统一事件 schema 落盘
  （.runtime/audit/kill_switch_orchestrator.jsonl，source_domain=access_control）。

scope 语法：
- level="system"：scope 为自由标签（默认 "global"），系统级开关为单实例全局语义。
- level="domain"：scope 为 "<域名>" 或 "<域名>:<目标>"；域名 = skills / trading / rollback /
  capacity（register_default_switches 默认注册）或自定义注册名。域内目标语法由适配器定义：
  skills→skill_id；trading→KillSwitchLevel 值（如 CIRCUIT_BREAKER，空=全部五级）；
  rollback→"L1_SESSION:<id>" / "L2_SKILL:<id>" / "L3_GLOBAL:<target>"（L3 需 BREAK_GLASS token，
  无 token 时底层抛错并收入 errors）；capacity→忽略目标（单实例 fuse）。
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final, Protocol, final, runtime_checkable

logger = logging.getLogger(__name__)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

SCHEMA_VERSION: Final[str] = "1.0"
SOURCE_DOMAIN: Final[str] = "access_control"


class SwitchLevel(str, Enum):
    """编排级别."""

    SYSTEM = "system"
    DOMAIN = "domain"


class GlobalTripUnsupported(Exception):
    """域级开关不支持空目标全域拉闸（逐目标粒度 / token-gated），编排器按 skipped 处理."""


def _level_value(level: str | SwitchLevel) -> str:
    """归一化 level 入参为字符串（兼容 SwitchLevel 枚举）."""
    return level.value if isinstance(level, SwitchLevel) else str(level).strip().lower()


@runtime_checkable
class SwitchAdapter(Protocol):
    """域级/系统级开关适配器协议（鸭子类型；编排器只依赖本协议）."""

    name: str
    supports_global_trip: bool  # 是否支持空目标全域拉闸（系统级 TRIPPED 传播对象）

    def trip(self, scope: str, reason: str) -> None: ...

    def reset(self, scope: str) -> None: ...

    def is_tripped(self, scope: str) -> bool: ...


@dataclass(frozen=True)
class OrchestrationResult:
    """单次编排动作结果（不可变）."""

    event_id: str
    action: str  # "trip" | "reset"
    level: str
    scope: str
    success: bool
    reason: str = ""
    approver: str = ""
    tripped: tuple[str, ...] = ()  # 本次实际动作的开关名
    skipped: tuple[str, ...] = ()  # 不支持全域拉闸而跳过的域级开关名
    errors: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""


# ── 既有五套开关的适配器（只包装，不改写；被包装对象经构造注入） ──────────────


@final
class _SystemSwitchAdapter:
    """系统级总开关适配器（security/access_control/kill_switch.py，MOD-INF-018）."""

    name = "system"
    supports_global_trip = True

    def __init__(self, switch: Any) -> None:
        self._switch = switch

    def trip(self, scope: str, reason: str) -> None:
        self._switch.trigger(
            trigger_name="orchestrator", reason=reason or f"orchestrator system trip: {scope}"
        )

    def reset(self, scope: str) -> None:
        self._switch.reset()

    def is_tripped(self, scope: str) -> bool:
        return bool(self._switch.is_global_tripped())


@final
class _SkillSwitchAdapter:
    """技能熔断适配器（skills/skill_kill_switch.py，MOD-INF-019；逐技能粒度，不支持全域拉闸）."""

    name = "skills"
    supports_global_trip = False

    def __init__(self, switch_cls: Any) -> None:
        self._switch_cls = switch_cls

    def trip(self, scope: str, reason: str) -> None:
        if not scope:
            raise GlobalTripUnsupported("skills 域为逐技能粒度，无全域拉闸语义")
        self._switch_cls.kill(scope, reason, trigger="orchestrator")

    def reset(self, scope: str) -> None:
        if not scope:
            raise GlobalTripUnsupported("skills 域为逐技能粒度，无全域复位语义")
        self._switch_cls.revive(scope)

    def is_tripped(self, scope: str) -> bool:
        return bool(scope) and bool(self._switch_cls.is_killed(scope))


@final
class _TradingSwitchAdapter:
    """交易五级熔断适配器（trading_kill_switch.py，MOD-INF-016；空目标=全部五级）."""

    name = "trading"
    supports_global_trip = True

    def __init__(self, module: Any) -> None:
        self._module = module

    def trip(self, scope: str, reason: str) -> None:
        if scope:
            level = self._module.KillSwitchLevel(scope)
            if not self._module.trigger(level):
                raise RuntimeError(f"交易开关触发失败: {scope}")
        else:
            for level in self._module.KillSwitchLevel:
                self._module.trigger(level)

    def reset(self, scope: str) -> None:
        if scope:
            level = self._module.KillSwitchLevel(scope)
            if not self._module.reset(level):
                raise RuntimeError(f"交易开关复位失败: {scope}")
        else:
            for level in self._module.KillSwitchLevel:
                self._module.reset(level)

    def is_tripped(self, scope: str) -> bool:
        if scope:
            switch = self._module.get_switch(self._module.KillSwitchLevel(scope))
            return bool(switch and switch.active)
        return bool(self._module.active_switches())


@final
class _RollbackSwitchAdapter:
    """回滚三级开关适配器（rollback/kill_switch.py，MOD-INF-021；L3 token-gated 不支持全域传播）."""

    name = "rollback"
    supports_global_trip = False

    def __init__(self, manager: Any) -> None:
        self._manager = manager

    def _parse_scope(self, scope: str) -> tuple[Any, str]:
        from zephyr.infrastructure.rollback.kill_switch import KillLevel

        if ":" in scope:
            level_name, _, target = scope.partition(":")
            return KillLevel(level_name.strip().upper()), target.strip()
        return KillLevel.L2_SKILL, scope.strip()

    def trip(self, scope: str, reason: str) -> None:
        if not scope:
            raise GlobalTripUnsupported("rollback L3_GLOBAL 为 token-gated，全域传播跳过")
        level, target = self._parse_scope(scope)
        self._manager.activate(level, target, reason)

    def reset(self, scope: str) -> None:
        if not scope:
            raise GlobalTripUnsupported("rollback 复位须显式目标")
        level, target = self._parse_scope(scope)
        self._manager.deactivate(level, target)

    def is_tripped(self, scope: str) -> bool:
        from zephyr.infrastructure.rollback.kill_switch import KillLevel

        if not scope:
            return bool(self._manager.status().global_killed)
        level, target = self._parse_scope(scope)
        if level is KillLevel.L1_SESSION:
            return bool(self._manager.is_killed(session_id=target)[0])
        if level is KillLevel.L3_GLOBAL:
            return bool(self._manager.status().global_killed)
        return bool(self._manager.is_killed(skill_id=target)[0])


@final
class _CapacitySwitchAdapter:
    """容量保障开关适配器（capacity_assurance/kill_switch.py；单实例 fuse）."""

    name = "capacity"
    supports_global_trip = True

    def __init__(self, switch: Any) -> None:
        self._switch = switch

    def trip(self, scope: str, reason: str) -> None:
        self._switch.fuse_on = True
        self._switch.trigger_shutdown()

    def reset(self, scope: str) -> None:
        self._switch.reset()

    def is_tripped(self, scope: str) -> bool:
        return bool(self._switch.fuse_on)


# ── 编排器 ────────────────────────────────────────────────────


@final
class KillSwitchOrchestrator:
    """Kill Switch 两级编排器（只编排不持态）.

    用法::

        orch = KillSwitchOrchestrator()  # 默认注册系统级 + 4 套域级开关
        orch.trip("domain", "skills:skill-x", "技能连续失败")   # 域内故障 → 域级先行
        orch.trip("system", "global", "全局事故")               # 全局事故 → 只拉系统级
        orch.reset("system", "global", approver="Owner")        # 复位须 Owner 批准

    编排器自身不保存任何开关状态——is_tripped/check_consistency 每次实时查询
    各开关本体；编排器实例销毁/故障不影响各开关独立可用（fail-open 分散态）。
    """

    def __init__(
        self,
        runtime_dir: str | Path | None = None,
        repo_root: str | Path | None = None,
        *,
        register_defaults: bool = True,
        system_switch: Any = None,
        project_root: str | Path | None = None,
    ) -> None:
        self._repo_root = Path(repo_root) if repo_root else _REPO_ROOT
        self._runtime_dir = Path(runtime_dir) if runtime_dir else self._repo_root / ".runtime"
        self._audit_path = self._runtime_dir / "audit" / "kill_switch_orchestrator.jsonl"
        self._system: SwitchAdapter | None = None
        self._domains: dict[str, SwitchAdapter] = {}
        self._audit_handle: Any = None
        if register_defaults:
            failures = self.register_default_switches(
                system_switch=system_switch, project_root=project_root
            )
            if failures:
                logger.warning("KillSwitchOrchestrator 默认开关注册存在失败项: %r", failures)

    # ── 注册 ──────────────────────────────────────────────────

    def register_system(self, adapter: Any) -> None:
        """注册系统级总开关适配器（须实现 SwitchAdapter 协议）."""
        self._require_adapter(adapter)
        self._system = adapter

    def register_domain(self, name: str, adapter: Any) -> None:
        """注册域级开关适配器（须实现 SwitchAdapter 协议）."""
        self._require_adapter(adapter)
        self._domains[str(name)] = adapter

    @staticmethod
    def _require_adapter(adapter: Any) -> None:
        for method in ("trip", "reset", "is_tripped"):
            if not callable(getattr(adapter, method, None)):
                raise TypeError(f"开关适配器缺少方法 {method}（SwitchAdapter 协议）: {adapter!r}")

    def register_default_switches(
        self, system_switch: Any = None, project_root: str | Path | None = None
    ) -> dict[str, str]:
        """注册既有 5 套开关（lazy import；单套导入失败不阻断其余，返回失败表）."""
        failures: dict[str, str] = {}
        try:
            if system_switch is None:
                from zephyr.security.access_control.kill_switch import get_kill_switch

                system_switch = get_kill_switch()
            self.register_system(_SystemSwitchAdapter(system_switch))
        except Exception as exc:  # noqa: BLE001 — 单套失败不阻断其余注册
            failures["system"] = repr(exc)
        try:
            from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch

            self.register_domain("skills", _SkillSwitchAdapter(SkillKillSwitch))
        except Exception as exc:  # noqa: BLE001
            failures["skills"] = repr(exc)
        try:
            from zephyr.trading.trading_contracts.risk import trading_kill_switch

            self.register_domain("trading", _TradingSwitchAdapter(trading_kill_switch))
        except Exception as exc:  # noqa: BLE001
            failures["trading"] = repr(exc)
        try:
            from zephyr.infrastructure.rollback.kill_switch import KillSwitchManager

            manager = KillSwitchManager(
                project_root=Path(project_root) if project_root else None
            )
            self.register_domain("rollback", _RollbackSwitchAdapter(manager))
        except Exception as exc:  # noqa: BLE001
            failures["rollback"] = repr(exc)
        try:
            from zephyr.infrastructure.capacity_assurance.kill_switch import (
                KillSwitch as CapacityKillSwitch,
            )

            self.register_domain("capacity", _CapacitySwitchAdapter(CapacityKillSwitch()))
        except Exception as exc:  # noqa: BLE001
            failures["capacity"] = repr(exc)
        return failures

    # ── 核心 API ──────────────────────────────────────────────

    def trip(
        self, level: str | SwitchLevel, scope: str, reason: str = ""
    ) -> OrchestrationResult:
        """拉闸（永不抛异常）.

        level="system"：拉系统级总开关，并向支持全域拉闸的域级开关传播（一致生效）。
        level="domain"：只拉指定域级开关（域内故障域级先行），系统级不动。
        """
        lvl = _level_value(level)
        scope_str = str(scope or "")
        try:
            if lvl == SwitchLevel.SYSTEM.value:
                result = self._trip_system(scope_str or "global", str(reason))
            elif lvl == SwitchLevel.DOMAIN.value:
                result = self._trip_domain(scope_str, str(reason))
            else:
                result = self._result(
                    "trip", lvl, scope_str, False,
                    reason=str(reason),
                    errors={"level": f"未知级别: {level!r}（合法值: system/domain）"},
                )
        except Exception as exc:  # noqa: BLE001 — ERROR_CONTRACT：永不抛异常
            result = self._result(
                "trip", lvl, scope_str, False,
                reason=str(reason), errors={"orchestrator": repr(exc)},
            )
        severity = "critical" if result.level == SwitchLevel.SYSTEM.value else "elevated"
        self._trace(result, severity=severity, threat_category="kill_switch_trip")
        return result

    def reset(
        self, level: str | SwitchLevel, scope: str, approver: str = ""
    ) -> OrchestrationResult:
        """复位（永不抛异常；approver 非空 = Owner 批准语义，既有不变量不破）."""
        lvl = _level_value(level)
        scope_str = str(scope or "")
        approver_str = str(approver or "").strip()
        try:
            if not approver_str:
                result = self._result(
                    "reset", lvl, scope_str, False,
                    errors={"approver": "复位须 Owner 批准：approver 不能为空"},
                )
            elif lvl == SwitchLevel.SYSTEM.value:
                result = self._reset_system(scope_str or "global", approver_str)
            elif lvl == SwitchLevel.DOMAIN.value:
                result = self._reset_domain(scope_str, approver_str)
            else:
                result = self._result(
                    "reset", lvl, scope_str, False, approver=approver_str,
                    errors={"level": f"未知级别: {level!r}（合法值: system/domain）"},
                )
        except Exception as exc:  # noqa: BLE001
            result = self._result(
                "reset", lvl, scope_str, False,
                approver=approver_str, errors={"orchestrator": repr(exc)},
            )
        self._trace(result, severity="info", threat_category="kill_switch_reset")
        return result

    def route_incident(
        self, incident_kind: str, reason: str = "", target: str = ""
    ) -> OrchestrationResult:
        """按 §3.4 收敛规则路由事故信号.

        funds/trading → 交易级先行，失败则系统级兜底；codebase/session → 系统级；
        domain（target="<域名>[:<目标>]"）→ 域级先行；global → 只拉系统级总开关。
        """
        kind = str(incident_kind).strip().lower()
        if kind in ("funds", "capital", "trading"):
            scope = f"trading:{target}" if target else "trading"
            first = self.trip(SwitchLevel.DOMAIN, scope, reason or "资金异常")
            if first.success:
                return first
            fallback = self.trip(
                SwitchLevel.SYSTEM, "global", f"交易级拉闸失败，系统级兜底: {reason or '资金异常'}"
            )
            return replace(
                fallback,
                errors={**fallback.errors, "trading_first_attempt": str(first.errors)},
            )
        if kind in ("codebase", "session", "repo"):
            return self.trip(SwitchLevel.SYSTEM, "global", reason or "代码库/会话越权")
        if kind == "domain":
            if not target:
                result = self._result(
                    "trip", SwitchLevel.DOMAIN.value, "", False,
                    reason=str(reason),
                    errors={"target": "domain 事故须指定 target=<域名>[:<目标>]"},
                )
                self._trace(result, severity="elevated", threat_category="kill_switch_trip")
                return result
            return self.trip(SwitchLevel.DOMAIN, str(target), reason)
        if kind == "global":
            return self.trip(SwitchLevel.SYSTEM, "global", reason or "全局事故")
        result = self._result(
            "trip", SwitchLevel.SYSTEM.value, "", False,
            reason=str(reason),
            errors={"incident_kind": f"未知事故类型: {incident_kind!r}"},
        )
        self._trace(result, severity="elevated", threat_category="kill_switch_trip")
        return result

    # ── 查询面（实时查开关本体，编排器不持态） ──────────────────

    def is_tripped(self, level: str | SwitchLevel, scope: str = "") -> bool:
        """有效状态查询：系统级 TRIPPED 时域级查询一致返回 True（支配语义）.

        查询失败（开关本体异常）返回 False 并告警——查询面 fail-open，
        拉闸/复位的权威判定走 trip()/reset() 的 errors 通道。
        """
        try:
            lvl = _level_value(level)
            if lvl == SwitchLevel.SYSTEM.value:
                return bool(self._system and self._system.is_tripped(str(scope or "")))
            if self._system is not None and self._system.is_tripped(""):
                return True
            name, _, target = str(scope).partition(":")
            adapter = self._domains.get(name)
            return bool(adapter and adapter.is_tripped(target))
        except Exception as exc:  # noqa: BLE001 — 查询面不抛异常
            logger.warning("is_tripped 查询失败: %r", exc)
            return False

    def check_consistency(self) -> dict[str, Any]:
        """两级一致性检查：系统级 TRIPPED 时，支持全域拉闸的域级开关须一致生效.

        返回报告字典：consistent 为总判；domains 给出各域 own_tripped 实测；
        任何开关查询异常都记入 errors 并判 inconsistent（检查本身永不抛异常）。
        """
        report: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "system_registered": self._system is not None,
            "system_tripped": False,
            "domains": {},
            "errors": {},
            "consistent": True,
        }
        system_tripped = False
        try:
            system_tripped = bool(self._system and self._system.is_tripped(""))
        except Exception as exc:  # noqa: BLE001
            report["errors"]["system"] = repr(exc)
            report["consistent"] = False
        report["system_tripped"] = system_tripped
        for name, adapter in self._domains.items():
            supports_global = bool(getattr(adapter, "supports_global_trip", False))
            entry: dict[str, Any] = {"supports_global_trip": supports_global, "own_tripped": None}
            try:
                entry["own_tripped"] = bool(adapter.is_tripped(""))
            except Exception as exc:  # noqa: BLE001
                report["errors"][name] = repr(exc)
                report["consistent"] = False
            if system_tripped and supports_global and entry["own_tripped"] is not True:
                # 系统级 TRIPPED 而全域型域级未物理生效 = 不一致（如传播被静默吞掉）
                report["consistent"] = False
            report["domains"][name] = entry
        return report

    def close(self) -> None:
        """关闭审计文件句柄（测试/探针场景显式调用）."""
        if self._audit_handle is not None:
            try:
                self._audit_handle.close()
            except OSError:
                pass
            self._audit_handle = None

    # ── 内部实现 ──────────────────────────────────────────────

    def _trip_system(self, scope: str, reason: str) -> OrchestrationResult:
        tripped: list[str] = []
        skipped: list[str] = []
        errors: dict[str, str] = {}
        if self._system is None:
            errors["system"] = "系统级开关未注册"
        else:
            try:
                self._system.trip(scope, reason)
                tripped.append("system")
            except Exception as exc:  # noqa: BLE001 — 单开关失败不阻断其余传播
                errors["system"] = repr(exc)
        # §3.4 收敛规则④：全局事故只拉系统级总开关；域级一致生效由编排器传播保障
        propagation_reason = f"系统级拉闸传播: {reason}" if reason else "系统级拉闸传播"
        for name, adapter in self._domains.items():
            if not getattr(adapter, "supports_global_trip", False):
                skipped.append(name)
                continue
            try:
                adapter.trip("", propagation_reason)
                tripped.append(name)
            except GlobalTripUnsupported:
                skipped.append(name)
            except Exception as exc:  # noqa: BLE001
                errors[name] = repr(exc)
        success = "system" in tripped and not errors
        return self._result(
            "trip", SwitchLevel.SYSTEM.value, scope, success,
            reason=reason, tripped=tripped, skipped=skipped, errors=errors,
        )

    def _trip_domain(self, scope: str, reason: str) -> OrchestrationResult:
        name, _, target = scope.partition(":")
        adapter = self._domains.get(name)
        tripped: list[str] = []
        errors: dict[str, str] = {}
        if adapter is None:
            errors[name or "scope"] = f"域级开关未注册: {name!r}"
        else:
            try:
                adapter.trip(target, reason)
                tripped.append(name)
            except Exception as exc:  # noqa: BLE001
                errors[name] = repr(exc)
        return self._result(
            "trip", SwitchLevel.DOMAIN.value, scope, not errors and bool(tripped),
            reason=reason, tripped=tripped, errors=errors,
        )

    def _reset_system(self, scope: str, approver: str) -> OrchestrationResult:
        tripped: list[str] = []
        skipped: list[str] = []
        errors: dict[str, str] = {}
        # 先复位域级（规避"系统级 TRIPPED 时域级不可单独复位"的公开面约束），再复位系统级
        for name, adapter in self._domains.items():
            if not getattr(adapter, "supports_global_trip", False):
                skipped.append(name)
                continue
            try:
                if adapter.is_tripped(""):
                    adapter.reset("")
                    tripped.append(name)
            except GlobalTripUnsupported:
                skipped.append(name)
            except Exception as exc:  # noqa: BLE001
                errors[name] = repr(exc)
        if self._system is None:
            errors["system"] = "系统级开关未注册"
        else:
            try:
                self._system.reset(scope)
                tripped.append("system")
            except Exception as exc:  # noqa: BLE001
                errors["system"] = repr(exc)
        success = "system" in tripped and not errors
        return self._result(
            "reset", SwitchLevel.SYSTEM.value, scope, success,
            approver=approver, tripped=tripped, skipped=skipped, errors=errors,
        )

    def _reset_domain(self, scope: str, approver: str) -> OrchestrationResult:
        name, _, target = scope.partition(":")
        adapter = self._domains.get(name)
        tripped: list[str] = []
        errors: dict[str, str] = {}
        if adapter is None:
            errors[name or "scope"] = f"域级开关未注册: {name!r}"
        else:
            try:
                if self._system is not None and self._system.is_tripped(""):
                    errors["state"] = "系统级 TRIPPED 时域级一致生效，禁止单独复位域级；请先复位系统级"
                else:
                    adapter.reset(target)
                    tripped.append(name)
            except Exception as exc:  # noqa: BLE001
                errors[name] = repr(exc)
        return self._result(
            "reset", SwitchLevel.DOMAIN.value, scope, not errors and bool(tripped),
            approver=approver, tripped=tripped, errors=errors,
        )

    @staticmethod
    def _result(
        action: str,
        level: str,
        scope: str,
        success: bool,
        reason: str = "",
        approver: str = "",
        tripped: list[str] | None = None,
        skipped: list[str] | None = None,
        errors: dict[str, str] | None = None,
    ) -> OrchestrationResult:
        return OrchestrationResult(
            event_id=uuid.uuid4().hex[:12],
            action=action,
            level=level,
            scope=scope,
            success=success,
            reason=reason,
            approver=approver,
            tripped=tuple(tripped or ()),
            skipped=tuple(skipped or ()),
            errors=dict(errors or {}),
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _trace(self, result: OrchestrationResult, severity: str, threat_category: str) -> None:
        """编排动作留痕（16号文 §4.2 P0-1 统一事件 schema；IO 失败不阻断）."""
        try:
            record = {
                "schema_version": SCHEMA_VERSION,
                "event_id": result.event_id,
                "timestamp": result.timestamp,
                "source_domain": SOURCE_DOMAIN,
                "event_type": "kill_switch_orchestration",
                "threat_category": threat_category,
                "severity": severity,
                "session_id": "",
                "evidence": {
                    "tripped": list(result.tripped),
                    "skipped": list(result.skipped),
                    "errors": dict(result.errors),
                },
                "action": result.action,
                "level": result.level,
                "scope": result.scope,
                "success": result.success,
                "reason": result.reason,
                "approver": result.approver,
            }
            if self._audit_handle is None:
                self._audit_path.parent.mkdir(parents=True, exist_ok=True)
                self._audit_handle = open(self._audit_path, "a", encoding="utf-8", buffering=1)
            self._audit_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._audit_handle.flush()
        except OSError as exc:
            logger.warning("kill_switch_orchestrator 审计留痕写入失败（动作仍生效）: %r", exc)


__all__ = [
    "SCHEMA_VERSION",
    "SOURCE_DOMAIN",
    "GlobalTripUnsupported",
    "KillSwitchOrchestrator",
    "OrchestrationResult",
    "SwitchAdapter",
    "SwitchLevel",
]
