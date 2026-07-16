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

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path

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


# ============== Provider 路由-meta 一致性校验（Phase 4.3/4.4 共用，裁定 #ARCH-CH-022） ==============
# 治本本次 8 条 ERROR 根因："fetch 路由支持某 capability 但 meta.capabilities 遗漏声明"。
# AST 解析 provider 文件，提取路由能力集（字典/frozenset/if-elif）+ meta.capabilities，
# 对比一致性。Phase 4.3 运行时 WARN（scheduler 启动），Phase 4.4 commit gate ERROR 阻断。

# 路由能力集变量名约定：_*_CAPABILITIES 或 _*_ROUTES（如 _KLINE_CAPABILITIES / _DIRECT_ROUTES / _ROUTES）
# 匹配 _ 开头 + 以 CAPABILITIES 或 ROUTES 结尾的变量名（覆盖 _ROUTES / _KLINE_CAPABILITIES 等所有变体）
_ROUTE_VAR_PATTERN = re.compile(r'^_.*(CAPABILITIES|ROUTES)$')


def _extract_str_constant(node: ast.AST, out: set[str]) -> None:
    """从 AST 节点提取字符串常量（非字符串则跳过）。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.add(node.value)


def _extract_str_from_container(node: ast.AST, out: set[str]) -> None:
    """从 Set/Tuple 容器节点提取所有字符串常量。"""
    if isinstance(node, (ast.Set, ast.Tuple)):
        for elt in node.elts:
            _extract_str_constant(elt, out)


def _extract_route_keys_from_value(value: ast.expr, out: set[str]) -> None:
    """从赋值值提取路由能力 key（dict keys / set elts / frozenset elts）。"""
    if isinstance(value, ast.Dict):
        for key in value.keys:
            _extract_str_constant(key, out)
    elif isinstance(value, ast.Set):
        for elt in value.elts:
            _extract_str_constant(elt, out)
    elif (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
          and value.func.id == "frozenset" and value.args):
        # frozenset({...}) — akshare _AKSHARE_CAPABILITIES 模式
        if isinstance(value.args[0], ast.Set):
            for elt in value.args[0].elts:
                _extract_str_constant(elt, out)


def _route_caps_from_tree(tree: ast.Module) -> set[str]:
    """从已解析的 AST 提取路由能力集（pure AST，无文件 I/O）。

    检测模式：
    1. 模块级赋值，变量名匹配 _*_CAPABILITIES / _*_ROUTES：
       - dict 字面量 {key: ...}: 提取 keys
       - set/frozenset({...}): 提取 elts
    2. fetch 方法体内 ``capability == "xxx"`` / ``capability in {...}``: 提取字符串常量

    覆盖三 provider 路由模式：
    - akshare: frozenset(_AKSHARE_CAPABILITIES)
    - miniqmt: 多个 dict(_KLINE_CAPABILITIES/_FINANCIAL_CAPABILITIES/_DIRECT_ROUTES/...)
    - ifind: if-elif 链(capability == "xxx")
    """
    route_caps: set[str] = set()

    # 模式1: 模块级 _*_CAPABILITIES / _*_ROUTES 赋值
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if not _ROUTE_VAR_PATTERN.match(target.id):
                continue
            _extract_route_keys_from_value(node.value, route_caps)

    # 模式2: fetch 方法体内 capability == "xxx" / capability in {...}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not (isinstance(node.left, ast.Name) and node.left.id == "capability"):
            continue
        if len(node.ops) != 1 or len(node.comparators) != 1:
            continue
        op, cmp = node.ops[0], node.comparators[0]
        if isinstance(op, ast.Eq):
            _extract_str_constant(cmp, route_caps)
        elif isinstance(op, ast.In):
            _extract_str_from_container(cmp, route_caps)

    return route_caps


def extract_route_capabilities(file_path: Path) -> set[str] | None:
    """AST 解析 provider 文件，提取所有路由能力集。

    文件不存在/解析失败返回 None（fail-open）。
    内容解析逻辑委托给 ``_route_caps_from_tree``（pure AST）。

    Args:
        file_path: provider .py 文件路径

    Returns:
        路由能力全集；文件不存在/解析失败返回 None（fail-open）
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None
    return _route_caps_from_tree(tree)


def _extract_caps_from_meta_call(call: ast.Call, out: set[str]) -> None:
    """从 DataSourceMeta(...) 调用的 capabilities keyword 提取 capability_id。"""
    for kw in call.keywords:
        if kw.arg != "capabilities" or not isinstance(kw.value, ast.List):
            continue
        for elt in kw.value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                out.add(elt.value)
            elif (isinstance(elt, ast.Call) and isinstance(elt.func, ast.Name)
                  and elt.func.id == "CapabilityContract" and elt.args):
                _extract_str_constant(elt.args[0], out)


def _meta_caps_from_tree(tree: ast.Module) -> set[str]:
    """从已解析的 AST 提取 DataSourceMeta(capabilities=[...]) 的 capability_id 集合（pure AST）。

    检测 ``meta = DataSourceMeta(..., capabilities=[...])`` 中的：
    - ``"xxx"`` 字符串字面量
    - ``CapabilityContract("xxx", ...)`` 构造调用的第一个参数

    同时检测 AnnAssign（类属性 ``meta: DataSourceMeta = DataSourceMeta(...)``）、
    Assign with Name target（类属性 ``meta = DataSourceMeta(...)`` 无注解）、
    和 Assign with Attribute target（实例级 ``self.meta = DataSourceMeta(...)``）。
    """
    meta_caps: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            if not (isinstance(node.target, ast.Name) and node.target.id == "meta"):
                continue
            if isinstance(node.value, ast.Call):
                _extract_caps_from_meta_call(node.value, meta_caps)
        elif isinstance(node, ast.Assign):
            has_meta_target = any(
                (isinstance(t, ast.Attribute) and t.attr == "meta")
                or (isinstance(t, ast.Name) and t.id == "meta")
                for t in node.targets
            )
            if not has_meta_target:
                continue
            if isinstance(node.value, ast.Call):
                _extract_caps_from_meta_call(node.value, meta_caps)
    return meta_caps


def extract_meta_capabilities(file_path: Path) -> set[str] | None:
    """AST 解析 provider 文件，提取 DataSourceMeta(capabilities=[...]) 的 capability_id 集合。

    文件不存在/解析失败返回 None（fail-open）。
    内容解析逻辑委托给 ``_meta_caps_from_tree``（pure AST）。

    Args:
        file_path: provider .py 文件路径

    Returns:
        meta 能力集；文件不存在/解析失败返回 None（fail-open）
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None
    return _meta_caps_from_tree(tree)


def check_route_meta_consistency_content(content: str) -> list[str]:
    """校验 provider 文件内容（字符串）的路由-meta 一致性（裁定 #ARCH-CH-022 Phase 4.4）。

    Phase 4.4 commit gate 的入口：gate 从 staged index 读取文件内容后调用本函数，
    无需写临时文件。与 ``check_route_meta_consistency(file_path)`` 共享同一比较逻辑
    （真源唯一），仅输入形态不同（content vs file_path）。

    Args:
        content: provider .py 文件完整内容（UTF-8 字符串）

    Returns:
        违规描述列表（空列表=一致或解析失败 fail-open）：
        - 路由支持但 meta 未声明（本次 8 条 ERROR 根因）
        - meta 声明但路由不支持（死声明，如 financial_statement）
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []  # 解析失败，fail-open
    route_caps = _route_caps_from_tree(tree)
    meta_caps = _meta_caps_from_tree(tree)

    violations: list[str] = []
    route_not_in_meta = route_caps - meta_caps
    if route_not_in_meta:
        violations.append(
            f"路由支持但 meta.capabilities 未声明: {sorted(route_not_in_meta)}"
        )
    meta_not_in_route = meta_caps - route_caps
    if meta_not_in_route:
        violations.append(
            f"meta.capabilities 声明但路由不支持（死声明）: {sorted(meta_not_in_route)}"
        )
    return violations


def check_route_meta_consistency(file_path: Path) -> list[str]:
    """校验 provider 文件的路由能力集 vs meta.capabilities 一致性（裁定 #ARCH-CH-022）。

    治本本次 8 条 ERROR 根因：fetch 路由支持某 capability 但 meta.capabilities 遗漏声明。
    文件读取后委托给 ``check_route_meta_consistency_content``（真源唯一）。

    Args:
        file_path: provider .py 文件路径

    Returns:
        违规描述列表（空列表=一致或解析失败 fail-open）：
        - 路由支持但 meta 未声明（本次 8 条 ERROR 根因）
        - meta 声明但路由不支持（死声明，如 financial_statement）
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []  # 文件不可读，fail-open
    return check_route_meta_consistency_content(content)
