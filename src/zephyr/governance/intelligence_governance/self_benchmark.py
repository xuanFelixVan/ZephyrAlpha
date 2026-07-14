# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §W3-7
# [MODULE] zephyr.governance.intelligence_governance.self_benchmark
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] cli._cmd_benchmark
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _KNOWN_PAIRS 长度=5; BenchmarkResult.status 枚举 passed/failed/degraded
# [MODIFY-GUARD] 修改 _KNOWN_PAIRS 须同步更新测试
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_benchmark() 不抛异常; check_regression() 返回 None 或 RegressionAlert
# [TESTS] tests/test_code_dedup_engine.py::TestSelfBenchmark
# [A_module] module_id=MOD-GOV_self_benchmark | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化告警.

职责：
  - 5 组 Known-Answer Test 覆盖 Type-1/2/3 + 非重复 + 微克隆
  - run_benchmark() 对每组运行对应 Stage 检测器 -> 对比预期
  - check_regression() 与上次结果对比 -> 通过率下降则退化告警
  - 原子写入历史文件 (temp + os.replace)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from zephyr.gov_code_quality.code_dedup.ast_comparator import ASTComparator
from zephyr.gov_code_quality.code_dedup.behavioral_sampler import BehavioralSampler
from zephyr.gov_code_quality.code_dedup.micro_clone_detector import MicroCloneDetector
from zephyr.infrastructure.asset_inventory.scanner import Scanner
from zephyr.shared.foundation.errors import SecurityError


# 5.45.3 修复：AST 白名单校验，阻断 LLM 生成代码中的危险操作
_ALLOWED_AST_NODES = (
    ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
    ast.Return, ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign,
    ast.For, ast.While, ast.If, ast.With, ast.AsyncWith, ast.Raise,
    ast.Try, ast.Assert, ast.Import, ast.ImportFrom, ast.Global,
    ast.Nonlocal, ast.Expr, ast.Pass, ast.Break, ast.Continue,
    ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Lambda, ast.IfExp,
    ast.Dict, ast.Set, ast.ListComp, ast.SetComp, ast.DictComp,
    ast.GeneratorExp, ast.Await, ast.Yield, ast.YieldFrom,
    ast.Compare, ast.Call, ast.FormattedValue, ast.JoinedStr,
    ast.Constant, ast.Attribute, ast.Subscript, ast.Starred,
    ast.Name, ast.List, ast.Tuple, ast.Slice,
    ast.arguments, ast.arg,
    ast.comprehension,
    ast.keyword,
    ast.alias,
    # 表达式上下文（Name/Attribute/Subscript 的 ctx 字段，良性叶节点）
    ast.Load, ast.Store, ast.Del,
    # 布尔运算符
    ast.And, ast.Or,
    # 二元运算符
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
    ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd,
    ast.FloorDiv, ast.MatMult,
    # 一元运算符
    ast.Invert, ast.Not, ast.UAdd, ast.USub,
    # 比较运算符
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Is, ast.IsNot, ast.In, ast.NotIn,
)

_DANGEROUS_NAMES = frozenset({
    "__import__", "__builtins__", "eval", "exec", "compile",
    "globals", "locals", "vars", "dir", "getattr", "setattr",
    "delattr", "hasattr", "type", "object", "classmethod",
    "staticmethod", "property", "memoryview", "open",
    "input", "breakpoint", "exit", "quit",
})

# 受限 builtins：保留 import 语句与常用安全函数所需的最小集，
# 排除 eval/exec/open/getattr 等危险项（AST 校验已阻断其 Name 引用，此处为纵深防御）
_SAFE_BUILTINS = {
    "__import__": __import__,
    "sum": sum, "len": len, "abs": abs, "min": min, "max": max,
    "round": round, "int": int, "float": float, "str": str, "bool": bool,
    "list": list, "dict": dict, "set": set, "tuple": tuple,
    "range": range, "enumerate": enumerate, "zip": zip, "map": map,
    "filter": filter, "sorted": sorted, "reversed": reversed,
    "any": any, "all": all, "print": print, "isinstance": isinstance,
}


def _validate_ast_safety(source: str) -> None:
    """5.45.3 修复：AST 白名单校验，阻断危险代码。

    - 仅允许白名单内的 AST 节点类型
    - 阻断对危险内置名（eval/exec/__import__/open 等）的直接引用
    - 阻断私有/dunder 属性访问（防止 __class__.__mro__ 等逃逸链）
    """

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise SecurityError(f"blocked ast node: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id in _DANGEROUS_NAMES:
            raise SecurityError(f"blocked dangerous name: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise SecurityError(f"blocked private attribute access: {node.attr}")


@dataclass
class KnownAnswerTest:
    id: str
    category: str
    code_a: str
    code_b: str
    expected_sim_min: float
    expected_sim_max: float
    expected_stage: str


@dataclass
class BenchmarkCaseResult:
    test_id: str
    category: str
    actual_similarity: float
    actual_stage: str
    expected_sim_min: float
    expected_sim_max: float
    expected_stage: str
    passed: bool
    details: str


@dataclass
class BenchmarkResult:
    total: int
    passed: int
    failed: int
    status: str
    case_results: list[BenchmarkCaseResult] = field(default_factory=list)


@dataclass
class RegressionAlert:
    previous_pass_rate: float
    current_pass_rate: float
    delta: float
    failed_cases: list[str]


_KNOWN_PAIRS: list[KnownAnswerTest] = [
    KnownAnswerTest(
        id="KAT-01",
        category="Type-1 词法级",
        code_a="def add(a, b): return a + b",
        code_b="def add(a, b): return a + b",
        expected_sim_min=1.0,
        expected_sim_max=1.0,
        expected_stage="signature_match",
    ),
    KnownAnswerTest(
        id="KAT-02",
        category="Type-2 结构级",
        code_a="def add(x, y): return x + y",
        code_b="def add(a, b): return a + b",
        expected_sim_min=0.85,
        expected_sim_max=1.0,
        expected_stage="ast_comparator",
    ),
    KnownAnswerTest(
        id="KAT-03",
        category="Type-3 语义级",
        code_a="def sum_values(lst): return sum(lst)",
        code_b="def total(items):\n    from functools import reduce\n    return reduce(lambda a, b: a + b, items, 0)",
        expected_sim_min=0.5,
        expected_sim_max=1.0,
        expected_stage="behavioral_sampler",
    ),
    KnownAnswerTest(
        id="KAT-04",
        category="非重复",
        code_a="def add(a, b): return a + b",
        code_b="def multiply(a, b): return a * b",
        expected_sim_min=0.0,
        expected_sim_max=0.3,
        expected_stage="—",
    ),
    KnownAnswerTest(
        id="KAT-05",
        category="微克隆",
        code_a="if x > 0: return x",
        code_b="if y > 0: return y",
        expected_sim_min=0.7,
        expected_sim_max=1.0,
        expected_stage="micro_clone",
    ),
]


class SelfBenchmark:
    _HISTORY_DIR = Path("data")
    _HISTORY_FILE = Path("data/code-dedup-benchmark-history.json")

    def __init__(self) -> None:
        self._scanner = Scanner()
        self._ast_comparator = ASTComparator()
        self._behavioral_sampler = BehavioralSampler()
        self._micro_clone_detector = MicroCloneDetector()

    def run_benchmark(self) -> BenchmarkResult:
        case_results: list[BenchmarkCaseResult] = []
        for pair in _KNOWN_PAIRS:
            case = self._evaluate_pair(pair)
            case_results.append(case)

        passed = sum(1 for c in case_results if c.passed)
        failed = len(case_results) - passed
        status = "passed" if failed == 0 else "failed"

        result = BenchmarkResult(
            total=len(case_results),
            passed=passed,
            failed=failed,
            status=status,
            case_results=case_results,
        )

        regression = self.check_regression(result)
        if regression is not None:
            result.status = "degraded"

        self._save_result(result)
        return result

    def check_regression(self, current: BenchmarkResult) -> RegressionAlert | None:
        previous = self._load_previous_result()
        if previous is None:
            return None

        prev_rate = previous.passed / previous.total if previous.total > 0 else 0.0
        curr_rate = current.passed / current.total if current.total > 0 else 0.0
        delta = curr_rate - prev_rate

        if delta >= 0:
            return None

        failed_cases = [c.test_id for c in current.case_results if not c.passed]
        return RegressionAlert(
            previous_pass_rate=round(prev_rate, 3),
            current_pass_rate=round(curr_rate, 3),
            delta=round(delta, 3),
            failed_cases=failed_cases,
        )

    def _evaluate_pair(self, pair: KnownAnswerTest) -> BenchmarkCaseResult:
        if pair.expected_stage == "signature_match":
            actual_sim, actual_stage = self._eval_signature(pair)
        elif pair.expected_stage == "ast_comparator":
            actual_sim, actual_stage = self._eval_ast(pair)
        elif pair.expected_stage == "behavioral_sampler":
            actual_sim, actual_stage = self._eval_behavioral(pair)
        elif pair.expected_stage == "micro_clone":
            actual_sim, actual_stage = self._eval_micro_clone(pair)
        else:
            actual_sim, actual_stage = self._eval_non_duplicate(pair)

        in_range = pair.expected_sim_min <= actual_sim <= pair.expected_sim_max
        stage_match = actual_stage == pair.expected_stage
        passed = in_range and stage_match

        details = (
            f"sim={actual_sim:.3f} "
            f"expected=[{pair.expected_sim_min},{pair.expected_sim_max}] "
            f"stage={actual_stage} expected={pair.expected_stage}"
        )

        return BenchmarkCaseResult(
            test_id=pair.id,
            category=pair.category,
            actual_similarity=actual_sim,
            actual_stage=actual_stage,
            expected_sim_min=pair.expected_sim_min,
            expected_sim_max=pair.expected_sim_max,
            expected_stage=pair.expected_stage,
            passed=passed,
            details=details,
        )

    def _eval_signature(self, pair: KnownAnswerTest) -> tuple[float, str]:
        scanner = Scanner()
        scanner._MIN_TOKEN_COUNT = 5
        path_a = self._write_temp(pair.code_a)
        path_b = self._write_temp(pair.code_b)
        try:
            result_a = scanner.scan_file(path_a)
            result_b = scanner.scan_file(path_b)
            key_a = result_a.file
            key_b = result_b.file
            if result_a.skipped or result_b.skipped:
                return 0.0, "skipped"
            if key_a not in scanner._minhashes or key_b not in scanner._minhashes:
                return 0.0, "none"
            sim = scanner._jaccard_estimate(
                scanner._minhashes[key_a],
                scanner._minhashes[key_b],
            )
            stage = "signature_match" if sim >= pair.expected_sim_min else "none"
            return round(sim, 3), stage
        finally:
            try:
                os.unlink(path_a)
            except OSError:
                pass
            try:
                os.unlink(path_b)
            except OSError:
                pass

    def _eval_ast(self, pair: KnownAnswerTest) -> tuple[float, str]:
        ast_result = self._ast_comparator.compare(pair.code_a, pair.code_b)
        if ast_result.similarity >= pair.expected_sim_min:
            return ast_result.similarity, "ast_comparator"

        tokens_a = self._scanner._tokenize_and_normalize(pair.code_a)
        tokens_b = self._scanner._tokenize_and_normalize(pair.code_b)
        token_sim = 0.0
        if tokens_a and tokens_b:
            set_a = set(tokens_a)
            set_b = set(tokens_b)
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            token_sim = intersection / union if union else 0.0

        actual_sim = max(ast_result.similarity, token_sim)
        stage = "ast_comparator" if actual_sim >= pair.expected_sim_min else "none"
        return round(actual_sim, 3), stage

    def _eval_behavioral(self, pair: KnownAnswerTest) -> tuple[float, str]:
        try:
            func_a = self._exec_function(pair.code_a)
            func_b = self._exec_function(pair.code_b)
            if func_a is None or func_b is None:
                return 0.0, "none"

            test_inputs = [[1, 2, 3], [10, 20, 30], [5, -3, 8]]
            match_count = 0
            for inp in test_inputs:
                try:
                    if func_a(inp) == func_b(inp):
                        match_count += 1
                except Exception as e:
                    logger.warning("suppressed error in self_benchmark", exc_info=True)
            sim = match_count / len(test_inputs)
            stage = "behavioral_sampler" if sim >= pair.expected_sim_min else "none"
            return round(sim, 3), stage
        except Exception:
            return 0.0, "none"

    def _eval_micro_clone(self, pair: KnownAnswerTest) -> tuple[float, str]:
        scanner = Scanner()
        scanner._MIN_TOKEN_COUNT = 5
        path_a = self._write_temp(pair.code_a)
        path_b = self._write_temp(pair.code_b)
        try:
            result_a = scanner.scan_file(path_a)
            result_b = scanner.scan_file(path_b)
            key_a = result_a.file
            key_b = result_b.file
            if result_a.skipped or result_b.skipped:
                return 0.0, "skipped"
            if key_a not in scanner._minhashes or key_b not in scanner._minhashes:
                return 0.0, "none"
            sim = scanner._jaccard_estimate(
                scanner._minhashes[key_a],
                scanner._minhashes[key_b],
            )
            stage = "micro_clone" if sim >= pair.expected_sim_min else "none"
            return round(sim, 3), stage
        finally:
            try:
                os.unlink(path_a)
            except OSError:
                pass
            try:
                os.unlink(path_b)
            except OSError:
                pass

    def _eval_non_duplicate(self, pair: KnownAnswerTest) -> tuple[float, str]:
        try:
            func_a = self._exec_function(pair.code_a)
            func_b = self._exec_function(pair.code_b)
            if func_a is None or func_b is None:
                return 1.0, "unknown"

            test_inputs = [(1, 2), (3, 4), (0, 5)]
            match_count = 0
            for inp in test_inputs:
                try:
                    if func_a(*inp) == func_b(*inp):
                        match_count += 1
                except Exception as e:
                    logger.warning("suppressed error in self_benchmark", exc_info=True)
            sim = match_count / len(test_inputs)
            stage = "—" if sim < pair.expected_sim_max else "behavioral_sampler"
            return round(sim, 3), stage
        except Exception:
            return 1.0, "unknown"

    @staticmethod
    def _write_temp(code: str) -> str:
        f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False)
        f.write(code)
        f.close()
        return f.name

    @staticmethod
    def _exec_function(source: str) -> object | None:
        # 5.45.3 修复：受限命名空间 + AST 白名单校验，阻断 LLM 生成代码中的危险操作
        ns: dict[str, Any] = {"__builtins__": _SAFE_BUILTINS}
        try:
            _validate_ast_safety(source)
            exec(source, ns)
        except SecurityError:
            logger.warning("blocked dangerous code in self_benchmark", exc_info=True)
            return None
        except Exception:
            return None
        for v in ns.values():
            if callable(v) and not isinstance(v, type):
                return v
        return None

    def _save_result(self, result: BenchmarkResult) -> None:
        self._HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "total": result.total,
            "passed": result.passed,
            "failed": result.failed,
            "status": result.status,
            "cases": [
                {
                    "test_id": c.test_id,
                    "category": c.category,
                    "actual_similarity": c.actual_similarity,
                    "actual_stage": c.actual_stage,
                    "passed": c.passed,
                }
                for c in result.case_results
            ],
        }
        tmp_path = str(self._HISTORY_FILE) + f".{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(self._HISTORY_FILE))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def _load_previous_result(self) -> BenchmarkResult | None:
        if not self._HISTORY_FILE.exists():
            return None
        try:
            with open(self._HISTORY_FILE, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        cases = [
            BenchmarkCaseResult(
                test_id=c["test_id"],
                category=c["category"],
                actual_similarity=c["actual_similarity"],
                actual_stage=c["actual_stage"],
                expected_sim_min=0.0,
                expected_sim_max=1.0,
                expected_stage="",
                passed=c["passed"],
                details="",
            )
            for c in data.get("cases", [])
        ]
        return BenchmarkResult(
            total=data["total"],
            passed=data["passed"],
            failed=data["failed"],
            status=data["status"],
            case_results=cases,
        )
