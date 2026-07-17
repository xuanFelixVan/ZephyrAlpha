# [BLUEPRINT] MOD-GOV-commit_gate_registry | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] (none — pure stdlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] CommitGateRegistry.register 幂等（同 gate_id 覆盖旧 spec）；check_all 按 priority 升序执行所有 gate；单个 gate 异常降级为 fail-closed（passed=False，安全优先），不阻断后续 gate 执行
# [MODIFY-GUARD] GateSpec 字段结构；GateResult 语义；TEST_EXEMPT_PREFIXES / is_test_exempt（tests/ 豁免真源）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_all 永不抛异常——单个 gate 异常降级为 GateResult(passed=False)
# [TESTS] tests/test_commit_gate_registry.py
# [A_module] module_id=MOD-GOV-commit_gate_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""commit_gate_registry.py — GitCommitGateway pre-commit 门禁注册表（架构债务 #AD-001 治本）

把 ``commit()`` 方法体中硬编码的 ``_check_*`` 调用升级为声明式 registry：
每个 pre-commit gate 注册一个 ``GateSpec``，commit 前由 registry 统一调度。

设计理由（架构债务 #AD-001 治本）
--------------------------------
``git_commit_gateway.py`` 职责过重（2500+ 行，11 个硬编码 ``_check_*`` 门禁 +
reconciler 注册 + commit 编排 + stash 隔离），多 session 频繁修改同一文件是
搭便车事故的根因之一（模式6 与 GATE-ARCH-MODEL 同文件冲突）。注册制后新增
门禁只需 ``register(spec)``，不改 ``commit()`` 方法体，消除冲突源。

设计参考 ReconciliationRegistry（post-commit reconciler 注册表），纯 stdlib
解耦，便于 mutation testing 用 ``importlib.util.spec_from_file_location``
直接加载。

命名区隔（防混淆）
------------------
本模块的 ``GateSpec`` / ``CommitGateRegistry`` 管 **commit-gateway pre-commit
门禁检查**，与 ``ReconciliationRegistry``（post-commit 漂移对账）是**完全不同的
关注点**（pre-commit 阻断 vs post-commit 对账），勿混淆。

Usage::

    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
        GateResult, GateSpec, CommitGateRegistry,
    )

    registry = CommitGateRegistry()
    registry.register(GateSpec(
        gate_id="HELD-OVERLAP",
        check=lambda gw, files, **kw: gw._check_held_overlap(
            kw["session_id"], files, kw.get("allow_overlap", False)
        ),
        priority=50,
    ))
    results = registry.check_all(gateway, files, session_id="sess-001", allow_overlap=False)
    # results == [GateResult(gate_id="HELD-OVERLAP", passed=True, detail="")]
"""

from __future__ import annotations

from typing import Final
import logging
from dataclasses import dataclass
from typing import Any, Callable

logger = logging.getLogger(__name__)

__all__ = [
    "GateResult",
    "GateSpec",
    "CommitGateRegistry",
    "TEST_EXEMPT_PREFIXES",
    "is_test_exempt",
]


# ---------------------------------------------------------------------------
# tests/ 豁免真源（治本2，2026-06-30）
# ---------------------------------------------------------------------------
# 病根：tests/ 豁免前缀在 create_guard.py / capability_overlap_gate.py 两处硬编码，
# 且实现不一致（create_guard L99 先归一再比对；capability_overlap_gate L87 直接 startswith，
# 未归一化——Windows 反斜杠路径会漏豁免，latent bug）。
#
# 治本（向内收·真源唯一）：提取到本模块（gate 基础设施真源），两 gate import 复用。
# 放此处而非 capability_lookup.py：tests/ 豁免是 gate 行为配置（哪些文件跳过 token 检查），
# 非能力索引关注点——关注点分离。
#
# 安全约束：本常量是高价值篡改目标（加 "src/" 可豁免所有源码绕过 create_guard），
# 已纳入 validate_rules_integrity.py RULES_MANIFEST C 层 golden hash 保护。
TEST_EXEMPT_PREFIXES: Final[tuple[str, ...]] = ("tests/",)


def is_test_exempt(file_path: str) -> bool:
    """判断文件是否在 tests/ 豁免区（归一化反斜杠后比对，消除 Windows 路径漂移）。

    治本2：封装归一化+比对逻辑，消除两 gate 实现不一致（create_guard 归一化、
    capability_overlap_gate 未归一化）。调用方不再自行实现 startswith 判断。

    Args:
        file_path: 文件相对路径（可能含正斜杠或反斜杠）。

    Returns:
        True 表示文件在 tests/ 豁免区（不需要 creation_token / 不检测 capability 重叠）。
    """
    normalized = file_path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in TEST_EXEMPT_PREFIXES)


@dataclass
class GateResult:
    """pre-commit 门禁检查结果。

    passed=True 时通过，passed=False 时阻断（detail 含违规信息）。
    """

    gate_id: str
    passed: bool
    detail: str = ""


@dataclass
class GateSpec:
    """单个 pre-commit 门禁声明。

    Attributes:
        gate_id: 门禁标识（如 "HELD-OVERLAP"）。
        check: 执行检查，返回 ``(passed, detail)``。
            签名 ``(gateway, files: list[str], **kwargs) -> tuple[bool, str]``。
            gate 是闭包，注册时捕获所需上下文。
        priority: 执行优先级（升序，数字小先执行）；同 priority 按 register 顺序。
    """

    gate_id: str
    check: Callable[..., tuple[bool, str]]
    priority: int = 100


class CommitGateRegistry:
    """pre-commit 门禁注册表（声明式，参考 ReconciliationRegistry）。

    register 幂等（同 gate_id 覆盖旧 spec）。
    check_all 按 priority 升序执行所有 gate，单个 gate 异常降级为 fail-closed
    （passed=False，安全优先），不阻断后续 gate 执行。
    """

    def __init__(self) -> None:
        self._specs: dict[str, GateSpec] = {}

    def register(self, spec: GateSpec) -> None:
        """注册门禁（幂等，同 gate_id 覆盖；同 priority 不同 gate_id 告警）。

        治本（2026-07-17）：同 priority 不同 gate_id 会导致 sorted() 稳定排序
        后执行顺序依赖 dict 插入顺序（非显式），违反"显式优于隐式"原则。
        检测到 priority 重复时记录 WARNING（不阻断注册，兼容存量）。
        """
        for existing_id, existing_spec in self._specs.items():
            if existing_spec.priority == spec.priority and existing_id != spec.gate_id:
                logger.warning(
                    "CommitGateRegistry: priority=%s 冲突——gate '%s' 与已注册的 '%s' 同 priority，"
                    "执行顺序依赖注册顺序（非显式）。建议分配唯一 priority。",
                    spec.priority, spec.gate_id, existing_id,
                )
                break
        self._specs[spec.gate_id] = spec

    def check_all(self, gateway: object, files: list[str], **kwargs: Any) -> list[GateResult]:
        """按 priority 升序执行所有 gate，返回结果列表。

        单个 gate 异常降级为 fail-closed（passed=False，安全优先），
        不阻断后续 gate 执行。
        """
        results: list[GateResult] = []
        for spec in sorted(self._specs.values(), key=lambda s: s.priority):
            try:
                passed, detail = spec.check(gateway, files, **kwargs)
                results.append(GateResult(
                    gate_id=spec.gate_id, passed=passed, detail=detail
                ))
            except Exception as e:
                logger.warning(
                    "CommitGateRegistry: gate %s 异常降级为 fail-closed: %s",
                    spec.gate_id, e, exc_info=True
                )
                results.append(GateResult(
                    gate_id=spec.gate_id,
                    passed=False,
                    detail=f"gate 异常（fail-closed）: {e}",
                ))
        return results

    def get(self, gate_id: str) -> GateSpec | None:
        """按 gate_id 获取已注册的 GateSpec（_commit_auto 复用 DCR gate 用）。

        Returns:
            GateSpec 或 None（gate_id 未注册时）。
        """
        return self._specs.get(gate_id)
