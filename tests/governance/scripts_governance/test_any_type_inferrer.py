# [BLUEPRINT] MOD-TEST-310 | tests/governance/scripts_governance/test_any_type_inferrer.py | §
# [MODULE] tests.governance.scripts_governance.test_any_type_inferrer
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.any_type_inferrer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 tmp_path 构造虚拟文件，不扫描真实仓库
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-TEST-310 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_any_type_inferrer.py — any_type_inferrer.py 单元测试。

#ARCH-ANY-GOVERNANCE-001 Phase 1 验收测试。

覆盖场景：
1. 裸 Any 检测（与 check_any_abuse.py 算法一致，回归测试）
2. 容器型 Any 豁免（dict[str, Any] 不算裸 Any）
3. TYPE_CHECKING 块内 Any 豁免
4. 方法调用推断（x.upper() → str）
5. 容器方法推断（x.append() → list, x.items() → dict）
6. isinstance 检查推断（isinstance(x, int) → int）
7. subscript 推断（x["key"] → dict, x[0] → list）
8. 迭代推断（for item in x → Iterable）
9. 返回字面量推断（return "foo" → str）
10. 无证据场景（confidence=0）
11. 多证据聚合（confidence 加权计算）
12. dunder 方法豁免（__init__ 的 Any 返回值不报）
13. CLI smoke test（生成 JSON 报告）
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

# 加入 scripts/governance/d7_code 到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[3]
_D7_CODE = _REPO_ROOT / "scripts" / "governance" / "d7_code"
if str(_D7_CODE) not in sys.path:
    sys.path.insert(0, str(_D7_CODE))

import any_type_inferrer as ati  # noqa: E402

# ── 辅助函数 ──────────────────────────────────────────────────────────


def _scan_code(code: str, filename: str = "test.py") -> list[ati.AnyInferenceFinding]:
    """扫描代码字符串，返回推断结果。"""
    tree = ast.parse(code, filename=filename)
    scanner = ati._FunctionScanner(filename)
    scanner.visit(tree)
    return scanner.findings


def _scan_func(code: str, func_name: str) -> ati.AnyInferenceFinding | None:
    """从代码中提取指定函数的 finding（应只有 1 个）。"""
    findings = _scan_code(code)
    matches = [f for f in findings if f.function == func_name]
    return matches[0] if matches else None


# ── 1. 裸 Any 检测 ──────────────────────────────────────────────────────


def test_bare_any_param_detected():
    """裸 Any 参数 → 检出 ANY-1。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    pass
"""
    findings = _scan_code(code)
    assert len(findings) == 1
    assert findings[0].kind == "ANY-1"
    assert findings[0].function == "foo"
    assert findings[0].param_or_return == "x"


def test_bare_any_return_detected():
    """裸 Any 返回值 → 检出 ANY-2。"""
    code = """
from typing import Any
def foo(x: int) -> Any:
    return x
"""
    findings = _scan_code(code)
    assert len(findings) == 1
    assert findings[0].kind == "ANY-2"
    assert findings[0].function == "foo"
    assert findings[0].param_or_return == "return"


def test_any_or_none_detected():
    """Any | None 联合类型 → 检出。"""
    code = """
from typing import Any
def foo(x: Any | None) -> None:
    pass
"""
    findings = _scan_code(code)
    assert len(findings) == 1
    assert findings[0].kind == "ANY-1"


# ── 2. 容器型 Any 豁免 ──────────────────────────────────────────────────


def test_container_any_not_flagged():
    """dict[str, Any] / list[Any] 等容器型 → 不算裸 Any。"""
    code = """
from typing import Any
def foo(x: dict[str, Any], y: list[Any], z: tuple[Any, ...]) -> None:
    pass
"""
    findings = _scan_code(code)
    assert len(findings) == 0, f"容器型 Any 应豁免，实际检出: {findings}"


def test_callable_any_not_flagged():
    """Callable[..., Any] → 不算裸 Any。"""
    code = """
from typing import Any, Callable
def foo(cb: Callable[..., Any]) -> None:
    pass
"""
    findings = _scan_code(code)
    assert len(findings) == 0


def test_kwargs_any_not_flagged():
    """**kwargs: Any → 豁免。"""
    code = """
from typing import Any
def foo(**kwargs: Any) -> None:
    pass
"""
    findings = _scan_code(code)
    assert len(findings) == 0


def test_vararg_any_not_flagged():
    """*args: Any → 豁免。"""
    code = """
from typing import Any
def foo(*args: Any) -> None:
    pass
"""
    findings = _scan_code(code)
    assert len(findings) == 0


# ── 3. TYPE_CHECKING 块豁免 ────────────────────────────────────────────


def test_type_checking_block_exempt():
    """TYPE_CHECKING 块内 Any → 豁免。"""
    code = """
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    def foo(x: Any) -> Any:
        return x
"""
    findings = _scan_code(code)
    assert len(findings) == 0


# ── 4. 方法调用推断 ────────────────────────────────────────────────────


def test_method_call_str_inference():
    """x.upper() → 推断 str。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    y = x.upper()
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "str"
    assert finding.confidence > 0.5


def test_method_call_list_inference():
    """x.append() → 推断 list。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    x.append(1)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "list"


def test_method_call_dict_inference():
    """x.items() → 推断 dict。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    for k, v in x.items():
        print(k, v)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "dict"


def test_method_call_set_inference():
    """x.add() → 推断 set。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    x.add(1)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "set"


# ── 5. isinstance 推断 ──────────────────────────────────────────────────


def test_isinstance_int_inference():
    """isinstance(x, int) → 推断 int。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    if isinstance(x, int):
        print(x)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "int"
    assert finding.confidence > 0.5


def test_isinstance_str_inference():
    """isinstance(x, str) → 推断 str。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    if isinstance(x, str):
        print(x)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "str"


# ── 6. subscript 推断 ──────────────────────────────────────────────────


def test_subscript_str_key_dict_inference():
    """x["key"] → 推断 dict。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    y = x["name"]
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "dict"


def test_subscript_int_key_list_inference():
    """x[0] → 推断 list。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    y = x[0]
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "list"


# ── 7. 迭代推断 ─────────────────────────────────────────────────────────


def test_for_iter_inference():
    """for item in x → 推断 Iterable。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    for item in x:
        print(item)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "Iterable"


def test_len_call_inference():
    """len(x) → 推断 Sized。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    n = len(x)
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "Sized"


# ── 8. 返回值推断 ──────────────────────────────────────────────────────


def test_return_str_inference():
    """return "foo" → 推断 str。"""
    code = """
from typing import Any
def foo() -> Any:
    return "hello"
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.kind == "ANY-2"
    assert finding.top_candidate == "str"


def test_return_int_inference():
    """return 42 → 推断 int。"""
    code = """
from typing import Any
def foo() -> Any:
    return 42
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "int"


def test_return_none_inference():
    """return None → 推断 None。"""
    code = """
from typing import Any
def foo() -> Any:
    return None
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "None"


def test_return_list_inference():
    """return [1, 2, 3] → 推断 list。"""
    code = """
from typing import Any
def foo() -> Any:
    return [1, 2, 3]
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "list"


# ── 9. dunder 方法豁免 ──────────────────────────────────────────────────


def test_dunder_return_any_exempt():
    """__init__ 等 dunder 的 Any 返回值不报。"""
    code = """
from typing import Any
class Foo:
    def __init__(self, x: Any) -> Any:
        self.x = x
"""
    findings = _scan_code(code)
    # __init__ 的 Any 返回值豁免，但 __init__ 的参数 x 仍检出
    any2_findings = [f for f in findings if f.kind == "ANY-2"]
    assert len(any2_findings) == 0, f"dunder ANY-2 应豁免: {any2_findings}"


# ── 10. 无证据场景 ──────────────────────────────────────────────────────


def test_no_evidence_zero_confidence():
    """无证据时 confidence=0。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    pass
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.confidence == 0.0
    assert finding.top_candidate == "unknown"
    assert len(findings := finding.inferred_candidates) == 0


# ── 11. 多证据聚合 ──────────────────────────────────────────────────────


def test_multi_evidence_aggregation():
    """多个 str 证据聚合 → 高置信度 str。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    a = x.upper()
    b = x.lower()
    c = x.strip()
    d = x.split(',')
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    assert finding.top_candidate == "str"
    assert finding.confidence >= 0.95  # 4 个 str 证据应聚合到高置信度
    assert len(finding.evidence) >= 4


def test_conflicting_evidence():
    """冲突证据（str + int）→ 两者都有候选，按权重排序。"""
    code = """
from typing import Any
def foo(x: Any) -> None:
    if isinstance(x, str):
        y = x.upper()
    elif isinstance(x, int):
        z = x + 1
"""
    finding = _scan_func(code, "foo")
    assert finding is not None
    # 应该有 str 和 int 两个候选
    types = [t for t, _ in finding.inferred_candidates]
    assert "str" in types
    assert "int" in types


# ── 12. scan_file / scan_directory ──────────────────────────────────────


def test_scan_file(tmp_path):
    """scan_file 读取真实文件并扫描。"""
    f = tmp_path / "test.py"
    f.write_text("""
from typing import Any
def foo(x: Any) -> Any:
    return x.upper()
""", encoding="utf-8")
    findings = ati.scan_file(f)
    assert len(findings) == 2  # ANY-1 + ANY-2
    kinds = {f.kind for f in findings}
    assert kinds == {"ANY-1", "ANY-2"}


def test_scan_directory(tmp_path):
    """scan_directory 递归扫描目录。"""
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "mod.py").write_text("""
from typing import Any
def foo(x: Any) -> None: pass
""", encoding="utf-8")
    (tmp_path / "b.py").write_text("""
from typing import Any
def bar(x: Any) -> None: pass
""", encoding="utf-8")
    # __pycache__ 应被排除
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "ignored.py").write_text("""
from typing import Any
def ignored(x: Any) -> None: pass
""", encoding="utf-8")

    findings = ati.scan_directory(tmp_path)
    funcs = {f.function for f in findings}
    assert "foo" in funcs
    assert "bar" in funcs
    assert "ignored" not in funcs


def test_scan_file_syntax_error_returns_empty(tmp_path):
    """语法错误文件 → 返回空列表（不抛异常）。"""
    f = tmp_path / "bad.py"
    f.write_text("def foo(:\n", encoding="utf-8")
    findings = ati.scan_file(f)
    assert findings == []


# ── 13. 报告写入 ────────────────────────────────────────────────────────


def test_write_report(tmp_path):
    """write_report 输出有效 JSON。"""
    findings = [
        ati.AnyInferenceFinding(
            file="test.py", line=1, col=0, kind="ANY-1",
            function="foo", param_or_return="x",
            current_annotation="Any",
            evidence=[ati.TypeEvidence("method_call", "x.upper()", "str", 1.0)],
            inferred_candidates=[("str", 1.0)],
            top_candidate="str",
            confidence=1.0,
        )
    ]
    output = tmp_path / "report.json"
    ati.write_report(findings, output, Path("/tmp/src"))
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["total_findings"] == 1
    assert data["findings_with_inference"] == 1
    assert data["findings"][0]["top_candidate"] == "str"
    assert data["findings"][0]["inferred_candidates"][0] == {"type": "str", "confidence": 1.0}


# ── 14. CLI smoke test ──────────────────────────────────────────────────


def test_cli_main_smoke(tmp_path, capsys):
    """main() CLI 可执行并生成报告。"""
    src = tmp_path / "src"
    src.mkdir()
    (src / "test.py").write_text("""
from typing import Any
def foo(x: Any) -> Any:
    return x.upper()
""", encoding="utf-8")
    output = tmp_path / "report.json"

    exit_code = ati.main(["--src", str(src), "--output", str(output)])
    assert exit_code == 0
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["total_findings"] == 2  # ANY-1 + ANY-2


def test_cli_missing_src(tmp_path):
    """src 目录不存在 → exit 2。"""
    exit_code = ati.main(["--src", str(tmp_path / "nonexistent")])
    assert exit_code == 2


def test_cli_ci_mode_with_high_confidence(tmp_path):
    """--ci 模式 + 高置信度 → exit 1。"""
    src = tmp_path / "src"
    src.mkdir()
    (src / "test.py").write_text("""
from typing import Any
def foo(x: Any) -> Any:
    return x.upper()
""", encoding="utf-8")
    output = tmp_path / "report.json"

    # --threshold 0.5 + 高置信度 str → exit 1
    exit_code = ati.main([
        "--src", str(src),
        "--output", str(output),
        "--ci",
        "--threshold", "0.5",
        "--quiet",
    ])
    assert exit_code == 1


# ── 15. _aggregate_evidence 单元测试 ────────────────────────────────────


def test_aggregate_evidence_empty():
    """空证据 → 空候选。"""
    assert ati.aggregate_evidence([]) == []


def test_aggregate_evidence_single_type():
    """单类型证据 → 100% 置信度。"""
    ev = [ati.TypeEvidence("method_call", "x.upper()", "str", 1.0)]
    cands = ati.aggregate_evidence(ev)
    assert len(cands) == 1
    assert cands[0] == ("str", 1.0)


def test_aggregate_evidence_mixed():
    """混合证据 → 按权重分配置信度。"""
    ev = [
        ati.TypeEvidence("method_call", "x.upper()", "str", 1.0),
        ati.TypeEvidence("isinstance_check", "isinstance(x, int)", "int", 0.9),
    ]
    cands = ati.aggregate_evidence(ev)
    assert len(cands) == 2
    # str 应该排第一（权重更高）
    assert cands[0][0] == "str"
    assert cands[1][0] == "int"
    # 总置信度 = 1.0
    assert cands[0][1] + cands[1][1] >= 0.99


def test_aggregate_evidence_ambiguous():
    """ambiguous 方法（如 pop）→ 分摊到多个候选。"""
    ev = [ati.TypeEvidence("method_call", "x.pop()", "ambiguous:list|dict", 0.5)]
    cands = ati.aggregate_evidence(ev)
    types = {t for t, _ in cands}
    assert types == {"list", "dict"}
