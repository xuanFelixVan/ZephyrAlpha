# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.capability_symbol_gate
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.capability_validator（AST 提取真源复用：_ROUTE_VAR_PATTERN/_extract_str_constant/_meta_caps_from_tree，同 D_DATA 域）
# [CONSUMERS] commit gate（gov_enforcement commit_gates，装配批接入）; 调用方（provider 声明-实现一致性校验）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 双向校验一次 AST 扫描完成（17 号 §5.8 项4）; 正向=self._fetch_xxx 调用与路由表 _fetch_ 方法引用必须类内定义; 反向范围=frozenset/set 与 CapabilityContract 声明（memo §5.5 口径，纯 meta 字符串不查）; 参数化路由表（dict tuple/非 _fetch_ 值）与共享方法路由（capability in <var>）不算残留; 解析失败 fail-open
# [MODIFY-GUARD] 17_special_trading_days_data_assets.md §5.5/§5.8
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无（违规以字符串列表返回，空=通过）
# [TESTS] tests/zephyr/data/test_capability_symbol_gate.py
# [A_module] module_id=MOD-GOV-capability_symbol_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: provider .py 文件内容（字符串）
# F1: _collect_method_defs（全部 ClassDef 方法名并集）+ _has_dynamic_fetch_dispatch（getattr(self, f"_fetch_{cap}") 动态分发检测）
# F2: 正向校验（self._fetch_*(...) 调用 + 路由表 dict 的 _fetch_ 字符串值引用 → 必须类内定义，防 internal_compute 式 AttributeError 半截工程）
# F3: 反向校验（memo §5.5 范围=frozenset/set + CapabilityContract 声明：无 _fetch_<cap> 方法 且 无路由证据（==/in 字面量比较、共享方法路由 in <var>、dict 方法引用已定义）→ 声明残留）
# O1: 违规描述列表（空=通过；语法错误 fail-open 空）
# [/ALGO_FLOW]
"""
Provider 声明-实现符号一致性双向 AST gate（17 号 §5.5 施工项 4，§5.8 定稿最优先）。

针对缺陷：internal_compute 曾出现「fetch 路由调用方法、方法却不存在」的 AttributeError
状态；akshare 曾出现 frozenset/Contract 声明了 capability 但对应 ``_fetch_<cap>`` 方法
不存在的「声明残留」（§4.2 L169/L363，getattr 动态分发运行时才炸）。

双向校验（同一 AST 扫描一次完成，17 号 §5.8 定稿）：
  - 正向：路由调用 ``self._fetch_xxx(...)`` 与路由表 dict 的 ``_fetch_`` 方法名引用
    （miniqmt ``_DIRECT_ROUTES`` 形态），每个被引用方法必须在类体内真实定义；
  - 反向（memo §5.5 范围=capability frozenset 与 CapabilityContract(...) 声明）：
    每个声明必须有 ``_fetch_<cap>`` 实现，**除非**有其他路由证据——
    ``capability == "x"``/``in {"x"}`` 字面量比较（elif 路由）、
    ``capability in <var>`` 共享方法路由（miniqmt 参数化路由表形态）、
    或同 capability 经 dict 方法引用路由且方法已定义。
    纯 meta 字符串声明不查（memo 范围外）；``getattr(self, f"_fetch_{cap}")``
    动态分发文件（akshare 形态）中 frozenset 声明不适用共享路由豁免——
    其实现契约就是 ``_fetch_<cap>`` 命名约定本身。

依据: 17_special_trading_days_data_assets §5.5/§5.8（#ARCH-DATA-002 施工项 4）
Version: 0.2.0（按真实 provider 路由形态校准反向豁免规则，消除参数化路由表误报）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: capability_symbol_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 Path
#   code: capability_symbol_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① check_declaration_impl_consistency_content
#   name_en: check_declaration_impl_consistency_content
#   intro: 校验 provider 文件内容（字符串）的声明-实现符号一致性（17 号 §5.8 项 4）。
#   desc: 校验 provider 文件内容（字符串）的声明-实现符号一致性（17 号 §5.8 项 4）。 Returns: 违规描述列表（空=一致；语法错误 fail-open 返回空）…；源码 L241-L295
#   inputs: content
#   outputs: list[str]
# - id: A2
#   name_zh: ② check_declaration_impl_consistency
#   name_en: check_declaration_impl_consistency
#   intro: 校验 provider 文件的声明-实现符号一致性（文件读取后委托 content 版，真源唯一）。
#   desc: 校验 provider 文件的声明-实现符号一致性（文件读取后委托 content 版，真源唯一）。；源码 L298-L304
#   inputs: file_path
#   outputs: list[str]
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: commit gate（gov_enforcement commit_gates，装配批接入）; 调用方（provider 声明-实现一致性校验）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Final

from zephyr.data.capability_validator import (
    _ROUTE_VAR_PATTERN,
    _extract_str_constant,
    _meta_caps_from_tree,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "check_declaration_impl_consistency",
    "check_declaration_impl_consistency_content",
]

_FETCH_PREFIX = "_fetch_"
#: fetch 路由中 capability 变量的常见命名（akshare 用 cap，其余用 capability）
_CAP_VAR_NAMES: Final = ("capability", "cap")


def _collect_method_defs(tree: ast.Module) -> set[str]:
    """收集文件内全部 ClassDef 的方法名并集（FunctionDef/AsyncFunctionDef）。"""
    methods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(child.name)
    return methods


def _collect_self_fetch_calls(tree: ast.Module) -> set[str]:
    """收集 ``self._fetch_xxx(...)`` 路由调用的方法名。"""
    called: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "self"
            and func.attr.startswith(_FETCH_PREFIX)
        ):
            called.add(func.attr)
    return called


def _has_dynamic_fetch_dispatch(tree: ast.Module) -> bool:
    """检测 ``getattr(self, f"_fetch_{cap}")`` 动态分发（akshare 形态）。

    该形态下 frozenset 声明的实现契约=``_fetch_<cap>`` 命名约定本身，
    不适用「共享方法路由」豁免（否则 akshare 式声明残留永远漏检）。
    """
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr"):
            continue
        for arg in node.args[1:]:
            if isinstance(arg, ast.JoinedStr):
                for value in arg.values:
                    if (
                        isinstance(value, ast.Constant)
                        and isinstance(value.value, str)
                        and _FETCH_PREFIX in value.value
                    ):
                        return True
    return False


def _is_cap_compare(node: ast.Compare) -> bool:
    return isinstance(node.left, ast.Name) and node.left.id in _CAP_VAR_NAMES


def _collect_route_evidence(tree: ast.Module) -> tuple[set[str], set[str]]:
    """路由证据：(字面量比较 caps, in <var> 比较引用的路由变量名)。"""
    literal_caps: set[str] = set()
    var_refs: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or not _is_cap_compare(node):
            continue
        if len(node.ops) != 1 or len(node.comparators) != 1:
            continue
        op, cmp = node.ops[0], node.comparators[0]
        if isinstance(op, ast.Eq):
            _extract_str_constant(cmp, literal_caps)
        elif isinstance(op, ast.In):
            if isinstance(cmp, ast.Name):
                var_refs.add(cmp.id)
            elif isinstance(cmp, (ast.Set, ast.Tuple)):
                for elt in cmp.elts:
                    _extract_str_constant(elt, literal_caps)
    return literal_caps, var_refs


def _collect_route_vars(tree: ast.Module) -> tuple[dict[str, set[str]], dict[str, dict[str, str]]]:
    """路由变量提取：set/frozenset 变量 {var: caps}；dict 变量 {var: {cap: value_str}}。"""
    set_vars: dict[str, set[str]] = {}
    dict_vars: dict[str, dict[str, str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and _ROUTE_VAR_PATTERN.match(t.id) for t in node.targets):
            continue
        var_name = next(t.id for t in node.targets if isinstance(t, ast.Name))
        value = node.value
        if isinstance(value, ast.Dict):
            entries: dict[str, str] = {}
            for k, v in zip(value.keys, value.values, strict=False):
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    entries[k.value] = v.value if isinstance(v, ast.Constant) and isinstance(v.value, str) else ""
            dict_vars[var_name] = entries
        else:
            caps: set[str] = set()
            if isinstance(value, ast.Set):
                for elt in value.elts:
                    _extract_str_constant(elt, caps)
            elif (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id == "frozenset"
                and value.args
                and isinstance(value.args[0], (ast.Set, ast.Tuple))
            ):
                for elt in value.args[0].elts:
                    _extract_str_constant(elt, caps)
            if caps:
                set_vars[var_name] = caps
    return set_vars, dict_vars


def _collect_contract_caps(tree: ast.Module) -> set[str]:
    """meta capabilities 中 CapabilityContract(...) 声明（memo 反向范围）；纯字符串不取。"""
    caps: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg != "capabilities" or not isinstance(kw.value, ast.List):
                continue
            for elt in kw.value.elts:
                if (
                    isinstance(elt, ast.Call)
                    and isinstance(elt.func, ast.Name)
                    and elt.func.id == "CapabilityContract"
                    and elt.args
                ):
                    _extract_str_constant(elt.args[0], caps)
    return caps


def check_declaration_impl_consistency_content(content: str) -> list[str]:
    """校验 provider 文件内容（字符串）的声明-实现符号一致性（17 号 §5.8 项 4）。

    Returns:
        违规描述列表（空=一致；语法错误 fail-open 返回空）：
        - 正向：self._fetch_xxx 调用 / 路由表 _fetch_ 方法引用，类内未定义（半截工程）
        - 反向：frozenset/set 或 CapabilityContract 声明的 capability 无实现且无路由证据（声明残留）
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []  # 解析失败，fail-open
    method_defs = _collect_method_defs(tree)
    dynamic_dispatch = _has_dynamic_fetch_dispatch(tree)
    literal_caps, compared_vars = _collect_route_evidence(tree)
    set_vars, dict_vars = _collect_route_vars(tree)
    violations: list[str] = []

    # 正向①：self._fetch_xxx(...) 调用必须类内定义
    for name in sorted(_collect_self_fetch_calls(tree) - method_defs):
        violations.append(
            f"路由调用 self.{name}(...) 但类体内未定义该方法"
            f"（半截工程，17 号施工项 4 正向；或方法在跨文件基类，需人工确认）"
        )
    # 正向②：路由表 dict 的 _fetch_ 字符串值引用必须类内定义（miniqmt _DIRECT_ROUTES 形态）
    dict_routed_caps: set[str] = set()
    for var_name, entries in dict_vars.items():
        for cap, value in entries.items():
            if value.startswith(_FETCH_PREFIX):
                dict_routed_caps.add(cap)
                if value not in method_defs:
                    violations.append(
                        f"路由表 {var_name}['{cap}'] 引用方法 {value} 但类体内未定义（半截工程，17 号施工项 4 正向）"
                    )
            else:
                dict_routed_caps.add(cap)  # 参数化路由表（共享方法实现）

    # 反向：frozenset/set + CapabilityContract 声明（memo §5.5 范围）
    declared: set[str] = set().union(*set_vars.values()) if set_vars else set()
    declared |= _collect_contract_caps(tree)
    for cap in sorted(declared):
        if f"{_FETCH_PREFIX}{cap}" in method_defs:
            continue  # 命名约定实现（akshare/直接路由形态）
        if cap in literal_caps:
            continue  # elif 字面量路由证据
        if not dynamic_dispatch and any(var in compared_vars and cap in caps for var, caps in set_vars.items()):
            continue  # 共享方法路由（capability in <set var>，miniqmt 形态）
        if cap in dict_routed_caps and any(
            var in compared_vars for var, entries in dict_vars.items() if cap in entries
        ):
            continue  # dict 路由表 + in <var> 路由证据（方法引用已定义或参数化共享实现）
        violations.append(
            f"capability 声明 '{cap}' 无对应 {_FETCH_PREFIX}{cap} 方法定义且无路由证据（声明残留，17 号施工项 4 反向）"
        )
    return violations


def check_declaration_impl_consistency(file_path: Path) -> list[str]:
    """校验 provider 文件的声明-实现符号一致性（文件读取后委托 content 版，真源唯一）。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []  # 文件不可读，fail-open
    return check_declaration_impl_consistency_content(content)
