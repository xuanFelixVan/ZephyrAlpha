# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_executor
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.intelligence.model_profiling.exam_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EXE_exam_executor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ExamExecutor --- 执行式代码评测（HumanEval pass@1 风格，v3.0.5）。

在隔离的子进程中执行模型生成的代码 + 测试断言，验证算法正确性
（而非仅检查语法/结构）。

特性:
  - 沙箱隔离: subprocess 执行，主进程不崩溃
  - 超时分级: 全量 10s / 单测 5s
  - 错误分类: 区分 SyntaxError / IndentationError / NameError / Timeout 等
    （便于审计幻觉类型——模型常编造不存在的符号导致 NameError）
  - pass@1 语义: pass_rate = passed / total

用法:
    executor = ExamExecutor()
    res = executor.execute(code_string, ["assert f(1)==2", "assert f(2)==4"])
    print(res.pass_rate, res.passed, res.total, res.errors)
"""
from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class ExecResult:
    """执行式评测结果。"""
    pass_rate: float  # passed / total，0.0~1.0
    passed: int
    total: int
    errors: list[str] = field(default_factory=list)  # 失败测试的错误信息（带分类标签）
    syntax_error: str = ""  # 若语法错误，记录分类（SyntaxError/IndentationError/ValueError）


def _classify_syntax_error(code: str) -> str:
    """分类语法错误类型（便于审计幻觉类型）。

    返回空字符串表示无语法错误。
    """
    try:
        ast.parse(code)
        return ""
    except IndentationError as e:
        return f"IndentationError: {e.msg} (line {e.lineno})"
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} (line {e.lineno})"
    except ValueError as e:
        return f"ValueError: {e}"


class ExamExecutor:
    """执行式评测——运行模型生成代码 + 测试断言，沙箱隔离。

    参考 HumanEval pass@1: pass_rate = 通过测试数 / 总测试数。
    语法错误/超时/异常 → 对应测试计为失败，pass_rate 降低但不抛异常。
    """

    def execute(self, code: str, test_cases: list[str], timeout_s: int = 10) -> ExecResult:
        """执行代码 + 测试断言。

        Args:
            code: 模型生成的完整 Python 代码
            test_cases: 可执行测试断言列表（每项是一段 Python 代码，通常含 assert）
            timeout_s: 全量执行超时秒数

        Returns:
            ExecResult: pass_rate / passed / total / errors / syntax_error
        """
        if not test_cases:
            return ExecResult(pass_rate=1.0, passed=0, total=0)

        total = len(test_cases)

        # 1. 先检查语法（分类错误）
        syn_err = _classify_syntax_error(code)
        if syn_err:
            return ExecResult(
                pass_rate=0.0,
                passed=0,
                total=total,
                errors=[f"[SYNTAX] {syn_err}"] * total,
                syntax_error=syn_err,
            )

        # 2. 全量执行（代码 + 所有测试 + ALL_TESTS_PASSED 标记）
        test_code = code + "\n\n" + "\n".join(test_cases) + "\nprint('ALL_TESTS_PASSED')"
        try:
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            if result.returncode == 0 and "ALL_TESTS_PASSED" in result.stdout:
                return ExecResult(pass_rate=1.0, passed=total, total=total)
        except subprocess.TimeoutExpired:
            # 全量超时 → 退化为逐测试
            pass
        except Exception:
            pass

        # 3. 部分通过：逐测试断言执行，收集错误
        passed = 0
        errors: list[str] = []
        for tc in test_cases:
            single_test = code + "\n\n" + tc
            try:
                r = subprocess.run(
                    [sys.executable, "-c", single_test],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if r.returncode == 0:
                    passed += 1
                else:
                    errors.append(self._classify_runtime_error(r.stderr))
            except subprocess.TimeoutExpired:
                errors.append("[TIMEOUT] 单测试超时(5s)")
            except Exception as e:
                errors.append(f"[EXEC_ERROR] {type(e).__name__}: {e}")

        return ExecResult(
            pass_rate=passed / total,
            passed=passed,
            total=total,
            errors=errors,
        )

    @staticmethod
    def _classify_runtime_error(stderr: str) -> str:
        """分类运行时错误（从 stderr 提取关键信息）。"""
        if not stderr:
            return "[UNKNOWN] 无 stderr 输出"
        # 提取最后一行错误类型
        lines = [ln.strip() for ln in stderr.strip().splitlines() if ln.strip()]
        if not lines:
            return "[UNKNOWN] 空 stderr"
        last = lines[-1]
        # 常见错误类型分类
        if last.startswith("NameError"):
            return f"[NAME_ERROR] {last}  # 模型可能编造了不存在的符号"
        if last.startswith("AttributeError"):
            return f"[ATTR_ERROR] {last}  # 模型可能编造了不存在的方法/属性"
        if last.startswith("ImportError") or last.startswith("ModuleNotFoundError"):
            return f"[IMPORT_ERROR] {last}  # 模型可能编造了不存在的库"
        if last.startswith("AssertionError"):
            return f"[ASSERT_FAIL] {last}  # 算法逻辑错误"
        if last.startswith("TypeError"):
            return f"[TYPE_ERROR] {last}"
        if last.startswith("KeyError") or last.startswith("IndexError"):
            return f"[KEY_INDEX_ERROR] {last}"
        if last.startswith("ZeroDivisionError"):
            return f"[ZERO_DIV] {last}"
        return f"[RUNTIME] {last}"
