# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (CommitGateRegistry, GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed（裁定#351，2026-09-19）——任一 enabled gate 装载失败（YAML 损坏/import 失败/getattr 失败/register 失败）→ 抛 GateAutoRegistrationError 阻断提交并逐台报 gate_id+错误；装载数≠名册数（条数↔total_gates、去重 gate_id 集合↔实际注册集合）→ 硬告警（logger.error+抛错阻断）；名册文件缺失=0 门装载 warn 留痕（测试 harness/嵌入式合法用法，防蒸发归 REGISTRY-MASS-DELETION gate）；enabled=false 跳过；register 幂等（同 gate_id 覆盖，与显式注册共存不冲突）；YAML 真源 in_process_gate_registry.yaml
# [MODIFY-GUARD] gate_id="GATE-AUTO-REGISTRAR"（无独立 gate，本模块是注册器非门禁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] auto_register_gates/load_gate_entries 门册损坏或任一门装载失败时抛 GateAutoRegistrationError（fail-closed 阻断提交链路——坏门静默免检比提交冻结危害更大；可用性代价已被裁定#351 接受，逃生=emergency_commit）
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
1. **fail-closed（裁定#351，2026-09-19）**：任一 enabled gate 装载失败 → 抛
   GateAutoRegistrationError 阻断 GitCommitGateway.__init__（即阻断提交），逐台报
   gate_id+错误。旧 fail-open（logger.warning 不阻断）的病根：装载数≠名册数无报警，
   坏门静默免检——门禁装载器自身的故障不得以"放行全部 commit"收场。可用性代价
   （一台坏门=全员冻结）由裁定#351 明示接受；逃生=emergency_commit。
   分层：名册文件**缺失**=该环境未声明任何门（0 门装载+warn 留痕；生产仓根/工作树
   恒有名册，测试 harness 合法用法；防蒸发责任在 REGISTRY-MASS-DELETION gate）；
   名册**存在**但损坏/为空/任一门装载失败/对账不一致 → 一律 fail-closed。
   装载数对账：条数↔头部 total_gates 声明 + enabled 去重 gate_id 集合↔实际注册集合，
   不一致 → 硬告警（logger.error）+抛错（并入 fail_open_register 台账族治理）。
2. **register 幂等共存**：CommitGateRegistry.register 幂等（同 gate_id 覆盖），
   auto_registrar 与 git_commit_gateway.py 显式注册可过渡期共存，不冲突。
   Phase 4 逐步删除显式注册。
3. **enabled 字段**：支持禁用 gate（不删除条目，保留历史），对标 capability registry 设计。
4. **不覆盖 priority**：priority 从 GateSpec 读取（factory_function 返回的 GateSpec 含 priority），
   YAML 的 priority 字段仅 informational，不覆盖代码真源。

Usage::

    from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates

    # 在 GitCommitGateway.__init__ 中调用（替代 75 个显式 register）
    # 装载失败/对账不一致 → GateAutoRegistrationError（fail-closed，阻断提交）
    auto_register_gates(self._gate_registry, self.project_root)

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/rule_bridge/gate_auto_registrar.yaml
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import yaml

# === #ARCH-ANY-GOVERNANCE-001 Phase 2 Batch 8 治本（2026-07-21） ===
# 替换 registry bare Any（CommitGateRegistry 延迟 import 避免循环依赖）
if TYPE_CHECKING:
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry

logger = logging.getLogger(__name__)

__all__: Final = ["GateAutoRegistrationError", "auto_register_gates", "load_gate_entries", "REGISTRY_REL_PATH"]

# in_process_gate_registry.yaml 相对项目根的路径
REGISTRY_REL_PATH = "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"


class GateAutoRegistrationError(RuntimeError):
    """门册损坏/门装载失败/装载数对账不一致——fail-closed 阻断提交（裁定#351）。

    信息承载约定：message 必含逐台 gate_id+错误详情，供提交链路直接透出定位。
    """


def _read_roster(project_root: Path) -> dict[str, Any] | None:
    """读取并结构校验门册 YAML。名册缺失返回 None；名册存在但损坏抛 GateAutoRegistrationError。

    分层契约（裁定#351）：文件缺失=该环境未声明任何门（测试 harness/嵌入式合法用法，
    防蒸发责任在 REGISTRY-MASS-DELETION gate）；文件存在但解析失败/根非 dict/gates 非
    list/含非 dict 条目=名册损坏，无法证明门禁装载完整，一律 fail-closed。
    """
    registry_path = project_root / REGISTRY_REL_PATH
    if not registry_path.exists():
        return None
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — fail-closed 收集后转抛（裁定#351）
        raise GateAutoRegistrationError(f"gate roster unreadable ({REGISTRY_REL_PATH}): {type(e).__name__}: {e}") from e
    if not isinstance(data, dict):
        raise GateAutoRegistrationError(f"gate roster root is not dict ({REGISTRY_REL_PATH}): {type(data).__name__}")
    gates = data.get("gates", []) or []
    if not isinstance(gates, list):
        raise GateAutoRegistrationError(
            f"gate roster 'gates' is not list ({REGISTRY_REL_PATH}): {type(gates).__name__}"
        )
    bad_indexes = [i for i, g in enumerate(gates) if not isinstance(g, dict)]
    if bad_indexes:
        raise GateAutoRegistrationError(
            f"gate roster has non-dict entries at indexes {bad_indexes[:10]} ({REGISTRY_REL_PATH})"
        )
    return data


def load_gate_entries(project_root: Path) -> list[dict[str, Any]]:
    """从 in_process_gate_registry.yaml 加载 gate 注册条目。

    Args:
        project_root: 项目根路径。

    Returns:
        gate 条目列表（每条含 gate_id / module_path / factory_function / enabled）。
        名册文件缺失返回空列表（0 门声明，warn 留痕）。

    Raises:
        GateAutoRegistrationError: 名册存在但损坏（fail-closed，裁定#351）。
    """
    roster = _read_roster(project_root)
    if roster is None:
        logger.warning(
            "gate_auto_registrar: gate roster not found (%s) — 0 gates declared "
            "(missing-roster tolerance; anti-evaporation owned by REGISTRY-MASS-DELETION gate)",
            REGISTRY_REL_PATH,
        )
        return []
    return roster.get("gates", [])


def auto_register_gates(
    registry: CommitGateRegistry,
    project_root: Path,
) -> list[tuple[str, str]]:
    """从 YAML 动态 import + register 所有 enabled 的 in-process gate（fail-closed）。

    Args:
        registry: CommitGateRegistry 实例（须有 register / list_gate_ids 方法）。
        project_root: 项目根路径（用于定位 YAML）。

    Returns:
        成功时空列表（兼容旧签名；失败不再以返回值表达）。

    Raises:
        GateAutoRegistrationError: 任一 enabled gate 装载失败（逐台报 gate_id+错误），
            或装载数对账不一致（条数↔total_gates、enabled 去重集合↔实际注册集合）。
            fail-closed（裁定#351）：调用方（GitCommitGateway.__init__）异常外溢即阻断提交。
    """
    roster = _read_roster(project_root)
    if roster is None:
        logger.warning(
            "gate_auto_registrar: gate roster not found (%s) — 0 gates declared, skipping auto-register "
            "(missing-roster tolerance; anti-evaporation owned by REGISTRY-MASS-DELETION gate)",
            REGISTRY_REL_PATH,
        )
        return []
    entries = roster.get("gates", [])
    if not entries:
        raise GateAutoRegistrationError(
            f"gate roster present but empty (0 entries) — refusing fail-open load ({REGISTRY_REL_PATH})"
        )

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
        except Exception as e:  # noqa: BLE001 — 逐台收集后统一 fail-closed（裁定#351）
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
            ft = entry.get("files_trigger")
            if ft:
                spec.files_trigger = tuple(ft) if isinstance(ft, list) else (str(ft),)
            registry.register(spec)
            registered_count += 1
        except Exception as e:  # noqa: BLE001 — 逐台收集后统一 fail-closed（裁定#351）
            failures.append((gate_id, f"register failed: {type(e).__name__}: {e}"))
            continue

    if failures:
        detail = "; ".join(f"{gid}: {err}" for gid, err in failures)
        logger.error(f"gate_auto_registrar FAIL-CLOSED: {len(failures)}/{len(entries)} gates failed: {detail}")
        raise GateAutoRegistrationError(
            f"gate auto-registration fail-closed (裁定#351): {len(failures)}/{len(entries)} gate(s) failed to load: {detail}"
        )

    # ── 装载数对账（硬告警，裁定#351：并入 fail_open_register 台账族）──
    mismatch_parts: list[str] = []

    declared_total = roster.get("total_gates")
    if isinstance(declared_total, int) and declared_total != len(entries):
        mismatch_parts.append(f"roster entries {len(entries)} != declared total_gates {declared_total}")

    expected_ids = [e.get("gate_id", "") for e in entries if e.get("enabled", True)]
    expected_set = set(expected_ids)
    if len(expected_set) != len(expected_ids):
        dupes = sorted({gid for gid in expected_ids if expected_ids.count(gid) > 1})
        mismatch_parts.append(f"duplicate enabled gate_id(s) in roster: {dupes[:10]}")
    registered_ids = set(registry.list_gate_ids())
    missing_ids = expected_set - registered_ids
    if missing_ids:
        mismatch_parts.append(
            f"{len(missing_ids)} enabled gate(s) declared but not registered: {sorted(missing_ids)[:10]}"
        )

    if mismatch_parts:
        detail = "; ".join(mismatch_parts)
        logger.error(f"gate_auto_registrar 装载对账硬告警（装载数≠名册数）: {detail}")
        raise GateAutoRegistrationError(f"gate roster reconciliation failed (装载数≠名册数): {detail}")

    logger.info(
        f"gate_auto_registrar: registered {registered_count}/{len(entries)} gates successfully "
        f"(roster reconciled: {len(expected_set)} unique enabled gate_id, declared total_gates={declared_total})"
    )
    return []


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
