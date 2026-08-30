# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (CommitGateRegistry, GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-open——YAML 解析失败/import 失败/getattr 失败时 logger.warning 不阻断 commit（registry 故障是环境异常，禁止阻断所有 commit）；enabled=false 跳过；register 幂等（同 gate_id 覆盖，与显式注册共存不冲突）；YAML 真源 in_process_gate_registry.yaml
# [MODIFY-GUARD] gate_id="GATE-AUTO-REGISTRAR"（无独立 gate，本模块是注册器非门禁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] auto_register_gates 永不抛异常——YAML/import/getattr 异常降级为 fail-open（logger.warning + 返回失败列表）
# [TESTS] tests/governance/rule_bridge/test_gate_auto_registrar.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
gate_auto_registrar.py — YAML 驱动的 in-process gate 自动注册器（#ARCH-GATE-REGISTRY-AUTO-001 Phase 3）

从 in_process_gate_registry.yaml 读取 gate 注册信息，动态 import + register，
替代 git_commit_gateway.py 中的 75 个显式 import + register 硬编码。

病根（第一性原理）
-----------------
git_commit_gateway.py 是 75 个 gate 的硬编码注册中心：
  1. 违反开闭原则——每个新 gate 都要改此文件
  2. 多 session 并发修改冲突频发（HELD-OVERLAP / heartbeat_daemon 还原竞态）
  3. 与 trae_072 跨 commit 原子性铁律1冲突——gate 文件 + import + register
     MUST 同 commit，但多 session 并发修改同一文件时无法保证原子性

治本方案
--------
YAML 列表追加比 Python 函数插入更易合并：
  1. 新 gate 只需在 in_process_gate_registry.yaml 追加条目
  2. gate_auto_registrar.py 动态 import + register
  3. gate 文件 + YAML 条目可在同 commit 原子提交（无需修改 git_commit_gateway.py）

设计权衡
--------
1. **fail-open**：YAML/import/getattr 异常不阻断 commit。registry 故障是环境异常，
   fail-closed 会让所有 commit 卡死，违反"治理工具不能成为单点故障"原则。
   对标 import_integrity_gate.py fail-open 设计。
2. **register 幂等共存**：CommitGateRegistry.register 幂等（同 gate_id 覆盖），
   auto_registrar 与 git_commit_gateway.py 显式注册可过渡期共存，不冲突。
   Phase 4 逐步删除显式注册。
3. **enabled 字段**：支持禁用 gate（不删除条目，保留历史），对标 capability registry 设计。
4. **不覆盖 priority**：priority 从 GateSpec 读取（factory_function 返回的 GateSpec 含 priority），
   YAML 的 priority 字段仅 informational，不覆盖代码真源。

Usage::

    from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates

    # 在 GitCommitGateway.__init__ 中调用（替代 75 个显式 register）
    failed = auto_register_gates(self._gate_registry, self.project_root)
    if failed:
        logger.warning(f"gate_auto_registrar failed for {len(failed)} gates: {failed}")

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: gate_auto_registrar.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: registry 参数
#   fields: 参数 registry，类型注解 CommitGateRegistry
#   code: gate_auto_registrar.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① load_gate_entries
#   name_en: load_gate_entries
#   intro: 从 in_process_gate_registry.yaml 加载 gate 注册条目。
#   desc: 从 in_process_gate_registry.yaml 加载 gate 注册条目。 Args: project_root: 项目根路径。 Returns: gate 条目…；源码 L126-L149
#   inputs: project_root
#   outputs: list[dict[str, Any]]
# - id: A2
#   name_zh: ② auto_register_gates
#   name_en: auto_register_gates
#   intro: 从 YAML 动态 import + register 所有 enabled 的 in-process gate。
#   desc: 从 YAML 动态 import + register 所有 enabled 的 in-process gate。 Args: registry: CommitGateRegis…；源码 L152-L224
#   inputs: registry project_root
#   outputs: list[tuple[str, str]]
# 层: 输出
# - id: O1
#   name_zh: list[dict[str, Any]]
#   name_en: list[dict[str, Any]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# - id: O2
#   name_zh: list[tuple[str, str]]
#   name_en: list[tuple[str, str]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

# === #ARCH-ANY-GOVERNANCE-001 Phase 2 Batch 8 治本（2026-07-21） ===
# 替换 registry bare Any（CommitGateRegistry 延迟 import 避免循环依赖）
if TYPE_CHECKING:
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry

logger = logging.getLogger(__name__)

__all__ = ["auto_register_gates", "load_gate_entries", "REGISTRY_REL_PATH"]

# in_process_gate_registry.yaml 相对项目根的路径
REGISTRY_REL_PATH = "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"


def load_gate_entries(project_root: Path) -> list[dict[str, Any]]:
    """从 in_process_gate_registry.yaml 加载 gate 注册条目。

    Args:
        project_root: 项目根路径。

    Returns:
        gate 条目列表（每条含 gate_id / module_path / factory_function / enabled）。
        YAML 解析失败时返回空列表（fail-open）。
    """
    registry_path = project_root / REGISTRY_REL_PATH
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(f"gate_auto_registrar: YAML parse failed ({type(e).__name__}: {e}), returning empty list")
        return []
    if not isinstance(data, dict):
        logger.warning(f"gate_auto_registrar: YAML root is not dict ({type(data).__name__}), returning empty list")
        return []
    gates = data.get("gates", []) or []
    if not isinstance(gates, list):
        logger.warning(f"gate_auto_registrar: gates is not list ({type(gates).__name__}), returning empty list")
        return []
    return [g for g in gates if isinstance(g, dict)]


def auto_register_gates(
    registry: CommitGateRegistry,
    project_root: Path,
) -> list[tuple[str, str]]:
    """从 YAML 动态 import + register 所有 enabled 的 in-process gate。

    Args:
        registry: CommitGateRegistry 实例（须有 register 方法）。
        project_root: 项目根路径（用于定位 YAML）。

    Returns:
        失败列表：[(gate_id, error_message), ...]。成功时为空列表。
        失败不抛异常（fail-open），调用方可 logger.warning。
    """
    entries = load_gate_entries(project_root)
    if not entries:
        logger.warning("gate_auto_registrar: no gate entries loaded from YAML, skipping auto-register")
        return []

    failures: list[tuple[str, str]] = []
    registered_count = 0

    for entry in entries:
        gate_id = entry.get("gate_id", "")
        module_path = entry.get("module_path", "")
        factory_function = entry.get("factory_function", "")
        enabled = entry.get("enabled", True)

        if not enabled:
            logger.info(f"gate_auto_registrar: skipping disabled gate {gate_id}")
            continue

        if not gate_id or not module_path or not factory_function:
            failures.append(
                (
                    gate_id or "?",
                    f"missing required field (gate_id={gate_id!r}, module_path={module_path!r}, factory_function={factory_function!r})",
                )
            )
            continue

        # 动态 import
        try:
            module = importlib.import_module(module_path)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            failures.append((gate_id, f"import failed: {type(e).__name__}: {e}"))
            continue

        # getattr 工厂函数
        try:
            factory = getattr(module, factory_function)
        except AttributeError as e:
            failures.append((gate_id, f"factory function not found: {factory_function} in {module_path}: {e}"))
            continue

        # 调用工厂函数 + register
        try:
            spec = factory()
            registry.register(spec)
            registered_count += 1
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            failures.append((gate_id, f"register failed: {type(e).__name__}: {e}"))
            continue

    if failures:
        logger.warning(
            f"gate_auto_registrar: registered {registered_count}/{len(entries)} gates, "
            f"{len(failures)} failures: {[f[0] for f in failures[:5]]}"
        )
    else:
        logger.info(f"gate_auto_registrar: registered {registered_count}/{len(entries)} gates successfully")

    return failures


if __name__ == "__main__":
    """CLI 入口——验证 in_process_gate_registry.yaml 中所有 gate 可正确注册。

    用途：
      python -m zephyr.gov_enforcement.rule_bridge.gate_auto_registrar

    退出码：0=全部成功，1=有失败。
    """
    import sys

    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
    from zephyr.shared.io.paths import REPO_ROOT

    registry = CommitGateRegistry()
    failures = auto_register_gates(registry, Path(REPO_ROOT))
    print(f"Registered {len(registry._specs)} gates, {len(failures)} failures")
    for gate_id, err in failures:
        print(f"  FAIL: {gate_id}: {err}")
    sys.exit(0 if not failures else 1)
