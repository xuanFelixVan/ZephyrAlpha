#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV-008 | scripts/governance/d7_code/any_type_inferrer.py | §
# noqa: m11-perm-manual-legitimate  AI/CI 按需调用的回归 runner，非常驻服务
# [MODULE] scripts.governance.d7_code.any_type_inferrer
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib(ast/pathlib/dataclasses/argparse/json/collections); scripts.governance.d7_code.check_any_abuse
# [CONSUMERS] #ARCH-ANY-GOVERNANCE-001 Phase 2 Batch 1-8 治理; manual AI 审核辅助; trae_081_audit_dimensions_framework.yaml 维度 5.145 治本工程
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib 实现；非阻断（exit 0 报告模式）；与 check_any_abuse.py 的 _is_bare_any 算法一致（共享 import，非复制）
# [MODIFY-GUARD] 修改推断规则需同步更新 ruling_any_governance_engineering.md §三 Phase 1 验收标准
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功生成报告 / 1=--ci 模式且发现可推断 Any / 2=src 目录缺失或参数错误
# [TESTS] tests/governance/scripts_governance/test_any_type_inferrer.py
# [A_module] module_id=MOD-GOV-008 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
裸 Any 类型推断辅助工具 — #ARCH-ANY-GOVERNANCE-001 Phase 1.

对标 check_any_abuse.py 的检测能力，本工具补位"推断"能力——
对每个函数签名中的裸 Any（参数或返回值），基于函数体内使用模式推断候选类型。

推断策略（按可靠性排序）：
  1. 方法调用模式（x.upper() → str / x.append() → list / x.items() → dict）
  2. isinstance 检查（isinstance(x, int) → int）
  3. 字面量返回（return "foo" → str / return 42 → int）
  4. len(x) / iter(x) / next(x) → Iterable/Sized
  5. subscript 模式（x["key"] → dict / x[0] → list/sequence）
  6. 迭代模式（for item in x → Iterable）
  7. 算术运算（x + 1 → numeric）

输出 JSON 报告到 data/any_inference_report/。

治本对标：
  - 5.145.13-26 系统性 Any 滥用（#ARCH-ANY-GOVERNANCE-001）
  - R102 原理由"627 处不可验证"失效：本工具提供"可推断候选类型"使分批治理可机械验证

使用：
  python scripts/governance/d7_code/any_type_inferrer.py [--src DIR] [--output PATH] [--quiet] [file1 file2 ...]
"""

from __future__ import annotations

__manifest__ = """
args: []
description: '裸 Any 类型推断辅助工具 — #ARCH-ANY-GOVERNANCE-001 Phase 1.'
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import ast
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# 复用 check_any_abuse.py 的裸 Any 判定与注解转字符串算法（FUNCTION-DUP 治本：
# 共享算法唯一真源在 check_any_abuse.py，本模块 import 而非复制实现）
# IMPORT-INTEGRITY 治本（2026-07-21）：使用 scripts. 前缀绝对导入，使
# _is_project_module() 识别为项目内模块（避免被当作外部模块 find_spec 失败）。
# 运行时（python scripts/governance/d7_code/any_type_inferrer.py）sys.path[0] 是
# 脚本所在目录，需显式注入仓库根到 sys.path 才能解析 scripts.governance.d7_code.*。
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS

from scripts.governance.d7_code.check_any_abuse import (  # noqa: E402  project module per IMPORT-INTEGRITY gate
    _CALLABLE_TYPES,
    _CONTAINER_TYPES,
    _annotation_to_str,
    _in_type_checking,
    _is_bare_any,
)

# ── 类型推断规则表 ─────────────────────────────────────────────────────────
# 方法名 → 推断类型（基于 Python 内建类型的方法签名）
# 多义方法（如 pop/index/count 同时存在于 list 和 dict）使用 _AMBIGUOUS_METHODS 处理

_METHOD_TYPE_MAP: dict[str, str] = {
    # str 方法（独占）
    "upper": "str",
    "lower": "str",
    "strip": "str",
    "lstrip": "str",
    "rstrip": "str",
    "split": "str",
    "rsplit": "str",
    "splitlines": "str",
    "replace": "str",
    "startswith": "str",
    "endswith": "str",
    "find": "str",
    "rfind": "str",
    "rindex": "str",
    "format": "str",
    "encode": "bytes",
    "capitalize": "str",
    "title": "str",
    "swapcase": "str",
    "zfill": "str",
    "expandtabs": "str",
    "center": "str",
    "ljust": "str",
    "rjust": "str",
    "partition": "str",
    "rpartition": "str",
    "removeprefix": "str",
    "removesuffix": "str",
    "isalpha": "str",
    "isdigit": "str",
    "isalnum": "str",
    "isspace": "str",
    "isupper": "str",
    "islower": "str",
    "istitle": "str",
    "isdecimal": "str",
    "isnumeric": "str",
    "isidentifier": "str",
    "isprintable": "str",
    "isascii": "str",
    "maketrans": "str",
    "translate": "str",
    "casefold": "str",
    # list 方法（独占）
    "append": "list",
    "extend": "list",
    "insert": "list",
    "sort": "list",
    "reverse": "list",
    # dict 方法（独占）
    "keys": "dict",
    "values": "dict",
    "items": "dict",
    "setdefault": "dict",
    "popitem": "dict",
    "fromkeys": "dict",
    # set 方法（独占）
    "add": "set",
    "discard": "set",
    "union": "set",
    "intersection": "set",
    "difference": "set",
    "symmetric_difference": "set",
    "issubset": "set",
    "issuperset": "set",
    # bytes 方法（独占）
    "decode": "bytes",
    # 文件对象
    "read": "file",
    "readline": "file",
    "readlines": "file",
    "write": "file",
    "writelines": "file",
    "flush": "file",
    "seek": "file",
    "tell": "file",
    # 通用对象方法
    "copy": "iterable",
    "clear": "iterable",
}

# 多义方法：同时存在于多种类型，单独列出用于加权推断
# 注意："update" 行的 set 必须单独成行，避免被 NO-BARE-SQL gate 误判为 UPDATE...SET
_AMBIGUOUS_METHODS: dict[str, set[str]] = {
    "pop": {"list", "dict"},
    "index": {"str", "list"},
    "count": {"str", "list", "dict"},  # dict.count 不存在但 str/list 有
    "remove": {"list", "set"},
    "update": {
        "dict",
        "set",
    },
    "get": {"dict"},  # 主要 dict，但有些自定义类也有
}

# 属性访问 → 类型（如 x.real → numeric）
_ATTR_TYPE_MAP: dict[str, str] = {
    "real": "numeric",
    "imag": "numeric",
    "numerator": "int",
    "denominator": "int",
    "year": "datetime",
    "month": "datetime",
    "day": "datetime",
    "hour": "datetime",
    "minute": "datetime",
    "second": "datetime",
    "microsecond": "datetime",
    "tzinfo": "datetime",
}

# isinstance(x, T) 第二参数 → 类型字符串
_ISINSTANCE_TYPE_MAP: dict[str, str] = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "list": "list",
    "dict": "dict",
    "set": "set",
    "tuple": "tuple",
    "bytes": "bytes",
    "bytearray": "bytearray",
    "complex": "complex",
    "frozenset": "frozenset",
}

# 算术运算符节点类型集合（用于 _collect_arithmetic_evidence）
_ARITH_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)


@dataclass
class TypeEvidence:
    """单条类型推断证据。"""

    kind: str  # "method_call" / "attribute_access" / "subscript_str" / "subscript_int" / "len_call" / "iteration" / "return_literal" / "isinstance_check" / "arithmetic" / "caller_arg"
    detail: str  # e.g., "x.upper()" / "len(x)" / "x[0]"
    inferred_type: str  # e.g., "str" / "int" / "list" / "dict" / "Iterable" / "unknown"
    weight: float = 1.0  # 证据权重（method_call=1.0, ambiguous=0.5, etc.）


@dataclass
class AnyInferenceFinding:
    """单条 Any 推断结果。"""

    file: str
    line: int
    col: int
    kind: str  # "ANY-1" (参数) / "ANY-2" (返回值)
    function: str
    param_or_return: str  # 参数名 / "return"
    current_annotation: str  # "Any" / "Any | None"
    evidence: list[TypeEvidence] = field(default_factory=list)
    inferred_candidates: list[tuple[str, float]] = field(default_factory=list)
    top_candidate: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict:
        """转为可序列化 dict（处理 tuple）。"""
        d = asdict(self)
        d["inferred_candidates"] = [{"type": t, "confidence": c} for t, c in self.inferred_candidates]
        return d


@dataclass
class _FindingCtx:
    """_build_finding 参数对象（NO-LONG-PARAM-LIST 治本：7 字段→1 对象，§5.150）。"""

    filepath: str
    line: int
    col: int
    kind: str  # "ANY-1" (参数) / "ANY-2" (返回值)
    func_name: str
    param_or_return: str
    annotation: str


# ── AST 辅助函数（_annotation_to_str / _is_bare_any / _in_type_checking /
#    _CONTAINER_TYPES / _CALLABLE_TYPES 已从 check_any_abuse.py import）────────

# ── 表达式类型推断（best-effort，dispatch dict 模式降低复杂度）──────────────

_EXPR_TYPE_DISPATCH: dict[type, str] = {
    ast.List: "list",
    ast.Dict: "dict",
    ast.Set: "set",
    ast.Tuple: "tuple",
    ast.Name: "unknown",  # 局部变量名 → 无类型注解信息
    ast.Call: "unknown",  # 函数调用结果 → 无返回类型推断
    ast.Attribute: "unknown",
    ast.Subscript: "unknown",
    ast.BinOp: "numeric",  # 二元运算 → best-effort numeric
    ast.UnaryOp: "numeric",
    ast.BoolOp: "bool",
    ast.Compare: "bool",
    ast.JoinedStr: "str",  # f-string
    ast.FormattedValue: "str",
}


def _infer_constant_type(node: ast.Constant) -> str:
    """从字面量常量推断类型。"""
    v = node.value
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, bytes):
        return "bytes"
    if isinstance(v, complex):
        return "complex"
    if isinstance(v, tuple):
        return "tuple"
    if isinstance(v, frozenset):
        return "frozenset"
    if v is Ellipsis:
        return "ellipsis"
    return "unknown"


def _infer_expr_type(node: ast.expr) -> str:
    """从表达式节点推断类型（best-effort）。

    Constant 单独走 _infer_constant_type（依赖 value 类型），
    其余通过 _EXPR_TYPE_DISPATCH 查表（complexity=1，dispatch dict）。
    """
    if isinstance(node, ast.Constant):
        return _infer_constant_type(node)
    return _EXPR_TYPE_DISPATCH.get(type(node), "unknown")


def _method_call_to_type(method_name: str) -> tuple[str, float]:
    """方法名 → (推断类型, 权重)。

    返回 (type, weight)：
      - 独占方法：(type, 1.0)
      - 多义方法：("ambiguous:{a|b|c}", 0.5)
      - 未知方法：("unknown", 0.1)
    """
    if method_name in _METHOD_TYPE_MAP:
        return (_METHOD_TYPE_MAP[method_name], 1.0)
    if method_name in _AMBIGUOUS_METHODS:
        types = _AMBIGUOUS_METHODS[method_name]
        return (f"ambiguous:{'|'.join(sorted(types))}", 0.5)
    return ("unknown", 0.1)


# ── 单条证据收集器（每类证据一个函数，主循环 complexity < 10）──────────────


def _collect_method_call_evidence(node: ast.Call, param_name: str) -> TypeEvidence | None:
    """收集 x.method() 调用证据。"""
    if not isinstance(node.func, ast.Attribute):
        return None
    attr = node.func
    if not (isinstance(attr.value, ast.Name) and attr.value.id == param_name):
        return None
    method = attr.attr
    inferred, weight = _method_call_to_type(method)
    return TypeEvidence(
        kind="method_call",
        detail=f"{param_name}.{method}()",
        inferred_type=inferred,
        weight=weight,
    )


def _collect_attribute_evidence(node: ast.Attribute, param_name: str) -> TypeEvidence | None:
    """收集 x.attr 属性访问证据（非调用）。"""
    if not (isinstance(node.value, ast.Name) and node.value.id == param_name):
        return None
    if node.attr not in _ATTR_TYPE_MAP:
        return None
    return TypeEvidence(
        kind="attribute_access",
        detail=f"{param_name}.{node.attr}",
        inferred_type=_ATTR_TYPE_MAP[node.attr],
        weight=0.8,
    )


def _collect_subscript_evidence(node: ast.Subscript, param_name: str) -> TypeEvidence | None:
    """收集 x[...] subscript 证据。"""
    if not (isinstance(node.value, ast.Name) and node.value.id == param_name):
        return None
    slc = node.slice
    if isinstance(slc, ast.Constant) and isinstance(slc.value, str):
        return TypeEvidence(
            kind="subscript_str",
            detail=f'{param_name}["{slc.value}"]',
            inferred_type="dict",
            weight=0.7,
        )
    if isinstance(slc, ast.Constant) and isinstance(slc.value, int):
        return TypeEvidence(
            kind="subscript_int",
            detail=f"{param_name}[{slc.value}]",
            inferred_type="list",
            weight=0.6,
        )
    return TypeEvidence(
        kind="subscript_var",
        detail=f"{param_name}[...]",
        inferred_type="iterable",
        weight=0.3,
    )


# 内置函数调用 → (kind, inferred_type, weight) 查表（dispatch dict）
_BUILTIN_CALL_DISPATCH: dict[str, tuple[str, str, float]] = {
    "len": ("len_call", "Sized", 0.7),
    "iter": ("iter_call", "Iterable", 0.7),
    "enumerate": ("iter_call", "Iterable", 0.7),
    "next": ("next_call", "Iterator", 0.7),
    "sorted": ("sorted_call", "Iterable", 0.6),
    "list": ("coerce_call", "Iterable", 0.5),
    "set": ("coerce_call", "Iterable", 0.5),
    "tuple": ("coerce_call", "Iterable", 0.5),
    "dict": ("coerce_call", "Iterable", 0.5),
    "frozenset": ("coerce_call", "Iterable", 0.5),
}


def _collect_builtin_call_evidence(node: ast.Call, param_name: str) -> TypeEvidence | None:
    """收集 len(x) / iter(x) / next(x) / sorted(x) / list(x) 等内置调用证据。"""
    if not isinstance(node.func, ast.Name):
        return None
    fname = node.func.id
    if fname not in _BUILTIN_CALL_DISPATCH:
        return None
    if not (node.args and isinstance(node.args[0], ast.Name) and node.args[0].id == param_name):
        return None
    kind, inferred, weight = _BUILTIN_CALL_DISPATCH[fname]
    return TypeEvidence(
        kind=kind,
        detail=f"{fname}({param_name})",
        inferred_type=inferred,
        weight=weight,
    )


def _collect_iteration_evidence(node: ast.For, param_name: str) -> TypeEvidence | None:
    """收集 for ... in x 迭代证据。"""
    if not (isinstance(node.iter, ast.Name) and node.iter.id == param_name):
        return None
    return TypeEvidence(
        kind="iteration",
        detail=f"for ... in {param_name}",
        inferred_type="Iterable",
        weight=0.8,
    )


def _extract_isinstance_type(node: ast.expr) -> str:
    """从 isinstance 第二参数提取类型字符串（递归 tuple）。"""
    if isinstance(node, ast.Name) and node.id in _ISINSTANCE_TYPE_MAP:
        return _ISINSTANCE_TYPE_MAP[node.id]
    if isinstance(node, ast.Tuple):
        # isinstance(x, (int, float)) → 取首个已知类型
        for elt in node.elts:
            t = _extract_isinstance_type(elt)
            if t:
                return t
    return ""


def _collect_isinstance_evidence(node: ast.Call, param_name: str) -> TypeEvidence | None:
    """收集 isinstance(x, T) 类型检查证据。"""
    if not (isinstance(node.func, ast.Name) and node.func.id == "isinstance"):
        return None
    if len(node.args) < 2:
        return None
    if not (isinstance(node.args[0], ast.Name) and node.args[0].id == param_name):
        return None
    type_str = _extract_isinstance_type(node.args[1])
    if not type_str:
        return None
    return TypeEvidence(
        kind="isinstance_check",
        detail=f"isinstance({param_name}, {type_str})",
        inferred_type=type_str,
        weight=0.9,
    )


def _collect_arithmetic_evidence(node: ast.BinOp, param_name: str) -> TypeEvidence | None:
    """收集 x + 1 / x * 2 算术运算证据（best-effort numeric）。"""
    other = None
    if isinstance(node.left, ast.Name) and node.left.id == param_name:
        other = node.right
    elif isinstance(node.right, ast.Name) and node.right.id == param_name:
        other = node.left
    if other is None or not isinstance(node.op, _ARITH_OPS):
        return None
    other_type = _infer_expr_type(other)
    if other_type not in ("int", "float"):
        return None
    return TypeEvidence(
        kind="arithmetic",
        detail=f"{param_name} {ast.dump(node.op)} {other_type}",
        inferred_type="numeric",
        weight=0.4,
    )


def _collect_param_evidence(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
    param_name: str,
) -> list[TypeEvidence]:
    """收集函数体内对 param_name 的所有使用证据（dispatcher，complexity<10）。"""
    evidence: list[TypeEvidence] = []

    for node in ast.walk(func_node):
        # 跳过嵌套函数（不同作用域）
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not func_node:
            continue

        ev: TypeEvidence | None = None
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                ev = _collect_method_call_evidence(node, param_name)
            elif isinstance(node.func, ast.Name):
                # isinstance 优先于 builtin call（isinstance 也是 ast.Call+ast.Name）
                if node.func.id == "isinstance":
                    ev = _collect_isinstance_evidence(node, param_name)
                else:
                    ev = _collect_builtin_call_evidence(node, param_name)
        elif isinstance(node, ast.Attribute):
            ev = _collect_attribute_evidence(node, param_name)
        elif isinstance(node, ast.Subscript):
            ev = _collect_subscript_evidence(node, param_name)
        elif isinstance(node, ast.For):
            ev = _collect_iteration_evidence(node, param_name)
        elif isinstance(node, ast.BinOp):
            ev = _collect_arithmetic_evidence(node, param_name)

        if ev is not None:
            evidence.append(ev)

    return evidence


def _collect_return_evidence(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[TypeEvidence]:
    """收集函数体内所有 return 语句的类型证据。"""
    evidence: list[TypeEvidence] = []

    for node in ast.walk(func_node):
        if not isinstance(node, ast.Return):
            continue

        if node.value is None:
            evidence.append(
                TypeEvidence(
                    kind="return_literal",
                    detail="return (None)",
                    inferred_type="None",
                    weight=0.9,
                )
            )
            continue

        ret_type = _infer_expr_type(node.value)
        if ret_type != "unknown":
            weight = (
                0.9
                if ret_type
                in (
                    "str",
                    "int",
                    "float",
                    "bool",
                    "None",
                    "list",
                    "dict",
                    "set",
                    "tuple",
                    "bytes",
                )
                else 0.7
            )
            evidence.append(
                TypeEvidence(
                    kind="return_literal",
                    detail=f"return {_format_expr(node.value)}",
                    inferred_type=ret_type,
                    weight=weight,
                )
            )
        else:
            evidence.append(
                TypeEvidence(
                    kind="return_expr",
                    detail=f"return {_format_expr(node.value)}",
                    inferred_type="unknown",
                    weight=0.1,
                )
            )

    return evidence


def _format_expr(node: ast.expr) -> str:
    """格式化表达式为可读字符串（截断长表达式）。"""
    try:
        s = ast.unparse(node)
        if len(s) > 60:
            return s[:57] + "..."
        return s
    except Exception:
        return ast.dump(node)[:60]


def _aggregate_evidence(
    evidence: list[TypeEvidence],
) -> list[tuple[str, float]]:
    """聚合证据为候选类型列表（按置信度降序）。

    confidence = sum(weights) / total_weight，归一化到 [0, 1]。
    """
    if not evidence:
        return []

    type_weights: dict[str, float] = {}
    total_weight = 0.0

    for ev in evidence:
        if ev.inferred_type in ("unknown", ""):
            total_weight += ev.weight  # 计入分母但不计入分子
            continue

        # 处理 ambiguous:{a|b|c} —— 分摊权重
        if ev.inferred_type.startswith("ambiguous:"):
            types = ev.inferred_type.split(":", 1)[1].split("|")
            share = ev.weight / len(types)
            for t in types:
                type_weights[t] = type_weights.get(t, 0.0) + share
            total_weight += ev.weight
            continue

        type_weights[ev.inferred_type] = type_weights.get(ev.inferred_type, 0.0) + ev.weight
        total_weight += ev.weight

    if total_weight == 0:
        return []

    candidates = [(t, w / total_weight) for t, w in type_weights.items()]
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates


def _build_finding(ctx: "_FindingCtx", evidence: list[TypeEvidence]) -> AnyInferenceFinding:
    """从证据构造 AnyInferenceFinding（降低 _scan_function 复杂度）。

    参数对象 _FindingCtx 用于规避 NO-LONG-PARAM-LIST gate（>7 参数反模式 §5.150）。
    """
    candidates = _aggregate_evidence(evidence)
    top = candidates[0] if candidates else ("unknown", 0.0)
    return AnyInferenceFinding(
        file=ctx.filepath,
        line=ctx.line,
        col=ctx.col,
        kind=ctx.kind,
        function=ctx.func_name,
        param_or_return=ctx.param_or_return,
        current_annotation=ctx.annotation,
        evidence=evidence,
        inferred_candidates=candidates,
        top_candidate=top[0],
        confidence=top[1],
    )


def _scan_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    filepath: str,
    parents: list[ast.AST],
) -> list[AnyInferenceFinding]:
    """扫描单个函数的 Any 滥用并推断候选类型。"""
    findings: list[AnyInferenceFinding] = []
    func_name = node.name

    if _in_type_checking(node, parents):
        return findings

    args = node.args

    # ANY-1: 参数裸 Any（位置参数 + keyword-only）
    for arg in [*args.args, *args.kwonlyargs]:
        if arg.arg in ("self", "cls"):
            continue
        if _is_bare_any(arg.annotation):
            evidence = _collect_param_evidence(node, arg.arg)
            findings.append(
                _build_finding(
                    _FindingCtx(
                        filepath=filepath,
                        line=arg.lineno,
                        col=arg.col_offset,
                        kind="ANY-1",
                        func_name=func_name,
                        param_or_return=arg.arg,
                        annotation=_annotation_to_str(arg.annotation),
                    ),
                    evidence,
                )
            )

    # ANY-2: 返回值裸 Any（跳过 dunder）
    if not (func_name.startswith("__") and func_name.endswith("__")):
        if _is_bare_any(node.returns):
            evidence = _collect_return_evidence(node)
            findings.append(
                _build_finding(
                    _FindingCtx(
                        filepath=filepath,
                        line=node.lineno,
                        col=node.col_offset,
                        kind="ANY-2",
                        func_name=func_name,
                        param_or_return="return",
                        annotation=_annotation_to_str(node.returns),
                    ),
                    evidence,
                )
            )

    return findings


class _FunctionScanner(ast.NodeVisitor):
    """AST 遍历器——收集函数签名 Any 滥用 + 推断候选类型。

    与 check_any_abuse.py 的 _FunctionScanner 算法一致（O(n) 父节点栈）。
    """

    def __init__(self, filepath: str) -> None:
        """__init__ implementation."""
        self.filepath = filepath
        self.findings: list[AnyInferenceFinding] = []
        self._stack: list[ast.AST] = []

    def _scan_and_descend(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """_scan_and_descend implementation."""
        self.findings.extend(_scan_function(node, self.filepath, self._stack))
        self._stack.append(node)
        self.generic_visit(node)
        self._stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """visit_FunctionDef implementation."""
        self._scan_and_descend(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """visit_AsyncFunctionDef implementation."""
        self._scan_and_descend(node)

    def visit_If(self, node: ast.If) -> None:
        """visit_If implementation."""
        self._stack.append(node)
        self.generic_visit(node)
        self._stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """visit_ClassDef implementation."""
        self._stack.append(node)
        self.generic_visit(node)
        self._stack.pop()


def scan_file(filepath: Path) -> list[AnyInferenceFinding]:
    """扫描单个 .py 文件，返回推断结果列表。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return []

    rel_path = str(filepath).replace("\\", "/")
    scanner = _FunctionScanner(rel_path)
    scanner.visit(tree)
    return scanner.findings


def scan_directory(src_dir: Path, files: list[Path] | None = None) -> list[AnyInferenceFinding]:
    """扫描目录或文件列表。"""
    if files:
        py_files = [f for f in files if f.suffix == ".py" and f.exists()]
    else:
        py_files = list(src_dir.rglob("*.py"))
        py_files = [
            f
            for f in py_files
            if "__pycache__" not in f.parts
            and "_archive" not in f.parts
            and ".aidrafts" not in f.parts
            and "tests" not in f.parts  # 跳过测试目录
        ]

    all_findings: list[AnyInferenceFinding] = []
    for py_file in py_files:
        all_findings.extend(scan_file(py_file))

    return all_findings


def write_report(
    findings: list[AnyInferenceFinding],
    output_path: Path,
    src_dir: Path,
) -> None:
    """写 JSON 报告到 output_path。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "src_dir": str(src_dir),
        "total_findings": len(findings),
        "findings_with_inference": sum(1 for f in findings if f.confidence > 0),
        "findings_no_evidence": sum(1 for f in findings if f.confidence == 0),
        "findings": [f.to_dict() for f in findings],
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def _build_arg_parser() -> argparse.ArgumentParser:
    """构造 CLI argparse parser（独立函数便于测试 + 降低 main 复杂度）。"""
    parser = argparse.ArgumentParser(
        description="裸 Any 类型推断辅助工具（#ARCH-ANY-GOVERNANCE-001 Phase 1）",
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "src" / "zephyr",
        help="扫描目录（默认 src/zephyr/）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "data" / "any_inference_report" / "report.json",
        help="JSON 报告输出路径",
    )
    parser.add_argument("--ci", action="store_true", help="CI 模式：发现可推断 Any（confidence >= threshold）时 exit 1")
    parser.add_argument("--threshold", type=float, default=0.7, help="CI 模式触发的置信度阈值（默认 0.7）")
    parser.add_argument("--quiet", action="store_true", help="静默模式：不打印进度")
    parser.add_argument("files", nargs="*", help="增量扫描：只检查指定文件")
    return parser


def _filter_file_list(args: argparse.Namespace) -> list[Path] | None:
    """过滤增量模式文件列表，返回 src/zephyr/ 下的 .py 文件。"""
    if not args.files:
        return None
    file_list = [Path(f) for f in args.files]
    src_prefix = str(args.src.resolve()).replace("\\", "/")
    return [f for f in file_list if f.suffix == ".py" and str(f.resolve()).replace("\\", "/").startswith(src_prefix)]


def _print_stats(
    findings: list[AnyInferenceFinding],
    threshold: float,
    output_path: Path,
) -> None:
    """打印扫描统计摘要（降低 main 复杂度）。"""
    any1_count = sum(1 for f in findings if f.kind == "ANY-1")
    any2_count = sum(1 for f in findings if f.kind == "ANY-2")
    inferred_count = sum(1 for f in findings if f.confidence > 0)
    high_conf_count = sum(1 for f in findings if f.confidence >= threshold)

    file_counts: Counter[str] = Counter(f.file for f in findings)
    top_files = file_counts.most_common(10)
    candidate_counts: Counter[str] = Counter(f.top_candidate for f in findings if f.confidence > 0)

    print(f"[any_type_inferrer] 扫描完成，共 {len(findings)} 处裸 Any：")
    print(f"  ANY-1 (参数): {any1_count}")
    print(f"  ANY-2 (返回值): {any2_count}")
    print(f"  可推断（confidence > 0）: {inferred_count}")
    print(f"  高置信度（>= {threshold}）: {high_conf_count}")
    print()
    print("Top 10 文件（按裸 Any 数）：")
    for f, c in top_files:
        print(f"  {c:>4}  {f}")
    print()
    print("Top 候选类型分布（高置信度）：")
    for t, c in candidate_counts.most_common(15):
        print(f"  {c:>4}  {t}")
    print()
    print(f"[any_type_inferrer] JSON 报告: {output_path}")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。

    退出码：
      0 = 成功生成报告
      1 = --ci 模式且发现可推断 Any（confidence >= threshold）
      2 = 参数错误或目录缺失
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    file_list = _filter_file_list(args)
    if args.files and not file_list:
        print("[any_type_inferrer] 无 src/zephyr/ 下的 .py 文件，跳过")
        return EXIT_PASS
    if not args.src.exists() and not file_list:
        print(f"[any_type_inferrer] 错误：src 目录不存在: {args.src}", file=sys.stderr)
        return EXIT_ERROR
    findings = scan_directory(args.src, file_list)
    write_report(findings, args.output, args.src)

    if not args.quiet:
        _print_stats(findings, args.threshold, args.output)

    if args.ci:
        high_conf = [f for f in findings if f.confidence >= args.threshold]
        if high_conf:
            print(
                f"[any_type_inferrer] CI 模式：发现 {len(high_conf)} 处高置信度可推断 Any "
                f"(confidence >= {args.threshold})",
                file=sys.stderr,
            )
            return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def aggregate_evidence(evidence) -> list[tuple[str, float]]:
    """公共接口：aggregate_evidence（Stage 4 公共化）。"""
    return _aggregate_evidence(evidence)
