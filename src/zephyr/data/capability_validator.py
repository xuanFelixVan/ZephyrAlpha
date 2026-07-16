# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.capability_validator
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 启动时校验 task.capability 与 provider.meta.capability_contracts 一致性; supports_symbols_null=False 只 warn 不阻断（渐进式收紧）; capability 不存在则 ERROR 阻断
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validate 返回 Violation 列表; 空列表=通过; 非空=有问题（severity 区分 ERROR/WARN）
# [TESTS] tests/zephyr/data/test_capability_validator.py
# [A_module] module_id=MOD-L00-004-capability_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Provider Capability 行为契约校验器（裁定 #ARCH-CH-022）。

在 scheduler 启动时校验 tasks.yaml 的 task 声明与 provider.meta.capability_contracts
的行为契约一致性，把"注释契约"升级为"机器可执行契约"。

校验规则：
1. task.capability 必须在 provider.meta.capability_contracts 中（按 capability_id 匹配）
   - 不存在 → ERROR（阻断启动）
2. task.symbols=null 时，对应 capability 应声明 supports_symbols_null=True
   - supports_symbols_null=False → WARN（不阻断，渐进式收紧；向后兼容字符串声明）
   - supports_symbols_null=True → PASS（已声明支持）
3. task.incremental=true 时，对应 capability 应声明 supports_incremental=True
   - supports_incremental=False → WARN

设计原则（遵循 architecture_debt_registry 裁定1）：
- 不新增 .md 规则文档，转化为启动时校验（reconciler 式）
- 初期 WARN-only 收集数据，逐步收紧为 ERROR（渐进式治理）
- 100% AI 开发模式下，只有机器可执行契约才能达到 ~100% 遵守率

公共接口：
- Violation: 校验违规（severity + message + task_id + capability_id）
- validate_task_capability_contracts(tasks, providers): 校验入口
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from zephyr.data.provider_base import DataSourceMeta

log = logging.getLogger(__name__)


@dataclass
class Violation:
    """契约校验违规。

    Attributes:
        severity: "ERROR"（阻断启动）或 "WARN"（记录但不阻断）
        message: 违规描述
        task_id: 任务 ID（如 "top10_shareholders_incremental"）
        capability_id: capability 标识（如 "top10_shareholders"）
        rule_id: 规则标识（如 "CAP-NULL-SYMBOLS"）
    """
    severity: str  # "ERROR" or "WARN"
    message: str
    task_id: str
    capability_id: str
    rule_id: str


def _get_meta_for_task(
    task: dict, metas: dict[str, DataSourceMeta]
) -> DataSourceMeta | None:
    """根据 task.source 获取 Provider 的 DataSourceMeta。"""
    source = task.get("source")
    if not source:
        return None
    return metas.get(source)


def _check_capability_exists(
    task: dict, meta: DataSourceMeta, violations: list[Violation],
) -> bool:
    """规则1: task.capability 必须在 provider.meta 中（ERROR 阻断）。"""
    cap_id = task.get("capability")
    if not cap_id:
        return True  # 无 capability 字段的 task 不校验
    contract = meta.get_capability_contract(cap_id)
    if contract is None:
        violations.append(Violation(
            severity="ERROR",
            message=f"task 声明 capability='{cap_id}' 但 provider '{meta.name}' 未声明此能力。"
                    f"已声明: {meta.capabilities_as_strings()[:10]}...",
            task_id=task.get("task_id") or task.get("id") or "?",
            capability_id=cap_id,
            rule_id="CAP-NOT-FOUND",
        ))
        return False
    return True


def _check_symbols_null(
    task: dict, meta: DataSourceMeta, violations: list[Violation],
) -> None:
    """规则2: task.symbols=null 时，capability 应声明 supports_symbols_null=True（WARN）。"""
    symbols = task.get("symbols")
    if symbols is not None:
        return  # symbols 非 null，不校验
    cap_id = task.get("capability")
    if not cap_id:
        return
    contract = meta.get_capability_contract(cap_id)
    if contract is None:
        return  # 规则1 已报 ERROR，不重复报
    if not contract.supports_symbols_null:
        violations.append(Violation(
            severity="WARN",
            message=f"task '{task.get('task_id') or task.get('id') or '?'}' 声明 symbols=null 但 capability '{cap_id}' "
                    f"未声明 supports_symbols_null=True。Provider 可能在 symbols=None 时直接报错。"
                    f"如需支持全市场，请在 {meta.name}_provider.py 的 meta.capabilities 中用 "
                    f"CapabilityContract('{cap_id}', supports_symbols_null=True) 显式声明。",
            task_id=task.get("task_id") or task.get("id") or "?",
            capability_id=cap_id,
            rule_id="CAP-NULL-SYMBOLS",
        ))


def _check_incremental(
    task: dict, meta: DataSourceMeta, violations: list[Violation],
) -> None:
    """规则3: task.incremental=true 时，capability 应声明 supports_incremental=True（WARN）。"""
    extra = task.get("extra") or {}
    incremental = extra.get("incremental", True)  # 默认增量
    if not incremental:
        return  # 全量模式，不校验增量
    cap_id = task.get("capability")
    if not cap_id:
        return
    contract = meta.get_capability_contract(cap_id)
    if contract is None:
        return  # 规则1 已报 ERROR
    if not contract.supports_incremental:
        violations.append(Violation(
            severity="WARN",
            message=f"task '{task.get('task_id') or task.get('id') or '?'}' 声明 incremental 但 capability '{cap_id}' "
                    f"未声明 supports_incremental=True。",
            task_id=task.get("task_id") or task.get("id") or "?",
            capability_id=cap_id,
            rule_id="CAP-INCREMENTAL",
        ))


def validate_task_capability_contracts(
    tasks: list[dict],
    metas: dict[str, DataSourceMeta],
) -> list[Violation]:
    """校验 tasks.yaml 的 task 声明与 provider 行为契约一致性。

    Args:
        tasks: tasks.yaml 加载的任务列表
        metas: {source_name: DataSourceMeta} 字典（通过 Provider 类的 meta 类属性获取，无需实例化）

    Returns:
        Violation 列表。空列表=全部通过。
        有 ERROR 级违规 → scheduler 应阻断启动
        仅有 WARN 级违规 → scheduler 记录日志但继续启动
    """
    violations: list[Violation] = []
    for task in tasks:
        # 跳过 disabled 任务
        if (task.get("extra") or {}).get("disabled"):
            continue
        meta = _get_meta_for_task(task, metas)
        if meta is None:
            # provider 不存在由 scheduler._validate_provider_and_policy 处理，不重复报
            continue
        # 规则1: capability 存在性（ERROR）
        if not _check_capability_exists(task, meta, violations):
            continue  # capability 不存在，跳过后续规则
        # 规则2: symbols=null 契约（WARN）
        _check_symbols_null(task, meta, violations)
        # 规则3: incremental 契约（WARN）
        _check_incremental(task, meta, violations)
    return violations


def has_blocking_violations(violations: list[Violation]) -> bool:
    """判断是否存在 ERROR 级违规（阻断启动）。"""
    return any(v.severity == "ERROR" for v in violations)


def format_violations(violations: list[Violation]) -> str:
    """格式化违规列表为日志字符串。"""
    if not violations:
        return "无契约违规"
    lines = [f"共 {len(violations)} 条违规:"]
    for v in violations:
        lines.append(f"  [{v.severity}] {v.rule_id} task={v.task_id} cap={v.capability_id}: {v.message}")
    return "\n".join(lines)
