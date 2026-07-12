# [A_test] module_id: SRC-TST-2157 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-commit_gates | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_msg_exposure_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_msg_exposure_gate.py — MSG-EXPOSURE 门禁单测

权威依据：msg_exposure_gate.py（make_msg_exposure_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestDetectMsgExposure: 纯函数级 AST 检测（_detect_msg_exposure）
  - 路径类敏感变量命中（path/file_path/target/tx_id）
  - 凭据类命中（password/secret/token）
  - 属性访问命中（self.path / self.tx_id）
  - str() 包装命中（f"{str(path)}"）
  - BinOp 命中（f"{a + path}"）
- TestSafePatterns: 安全模式不命中
  - 字面量消息 raise Foo("literal")
  - 非异常构造 raise Foo(format_str)
  - bare raise / raise var
  - Exception()/BaseException() 无参
  - details 字段正确用法 raise Foo("msg", details={"path": str(p)})
- TestNoqaExemption: # noqa: MSG-EXPOSURE 行级豁免
- TestGatewayIntegration: mock gateway 流程
  - 新增文件全文件检测
  - 修改文件只检测 diff 新增行
  - tests/ 豁免
  - commit_gates/ 自豁免
  - fail-open on git diff 失败
  - fail-open on AST 解析失败
"""
from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.msg_exposure_gate import (  # noqa: E402
    _detect_msg_exposure,
    _f_string_has_sensitive_value,
    _filter_noqa_violations,
    _is_exception_constructor,
    _is_line_noqa,
    make_msg_exposure_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_returns_gate_spec_instance(self):
        spec = make_msg_exposure_gate()
        assert isinstance(spec, GateSpec)

    def test_gate_id(self):
        assert make_msg_exposure_gate().gate_id == "MSG-EXPOSURE"

    def test_priority_is_83(self):
        # 在 PERM-TRIGGER(82) 之后、EMPTY-HANDLER(84) 之前
        assert make_msg_exposure_gate().priority == 83


# ---------------------------------------------------------------------------
# TestDetectMsgExposure — 纯函数级检测
# ---------------------------------------------------------------------------
class TestDetectMsgExposure:
    """测试 _detect_msg_exposure 对各种模式的识别。"""

    def _detect(self, code: str) -> list[tuple[int, str, list[str]]]:
        tree = ast.parse(textwrap.dedent(code))
        return _detect_msg_exposure(tree)

    def test_path_variable_detected(self):
        violations = self._detect('''
            raise FileNotFoundError(f"file not found: {path}")
        ''')
        assert len(violations) == 1
        assert violations[0][1] == "FileNotFoundError"
        assert "path" in violations[0][2]

    def test_file_path_attribute_detected(self):
        violations = self._detect('''
            raise IOError(f"cannot read {self.file_path}")
        ''')
        assert len(violations) == 1
        assert "file_path" in violations[0][2]

    def test_tx_id_detected(self):
        violations = self._detect('''
            raise TransactionError(f"[{tx_id}] timeout")
        ''')
        assert len(violations) == 1
        assert "tx_id" in violations[0][2]

    def test_self_tx_id_attribute_detected(self):
        violations = self._detect('''
            raise TransactionError(f"[{self.tx_id}] failed")
        ''')
        assert len(violations) == 1
        assert "tx_id" in violations[0][2]

    def test_password_detected(self):
        violations = self._detect('''
            raise AuthError(f"invalid password: {password}")
        ''')
        assert len(violations) == 1
        assert "password" in violations[0][2]

    def test_secret_detected(self):
        violations = self._detect('''
            raise ValueError(f"bad secret {secret}")
        ''')
        assert len(violations) == 1
        assert "secret" in violations[0][2]

    def test_token_detected(self):
        violations = self._detect('''
            raise PermissionError(f"token expired: {token}")
        ''')
        assert len(violations) == 1
        assert "token" in violations[0][2]

    def test_str_wrapper_detected(self):
        # f"{str(path)}" 模式
        violations = self._detect('''
            raise RuntimeError(f"failed at {str(path)}")
        ''')
        assert len(violations) == 1
        assert "path" in violations[0][2]

    def test_binop_detected(self):
        # f"{prefix + path}" 模式
        violations = self._detect('''
            raise OSError(f"err: {prefix + path}")
        ''')
        assert len(violations) == 1
        assert "path" in violations[0][2]

    def test_multiple_sensitive_in_one_string(self):
        violations = self._detect('''
            raise RuntimeError(f"{path} {tx_id} {password}")
        ''')
        assert len(violations) == 1
        hits = set(violations[0][2])
        assert {"path", "tx_id", "password"}.issubset(hits)

    def test_multiple_raise_statements(self):
        violations = self._detect('''
            if x:
                raise FooError(f"a {path}")
            else:
                raise BarError(f"b {tx_id}")
        ''')
        assert len(violations) == 2


# ---------------------------------------------------------------------------
# TestSafePatterns — 不应命中的安全模式
# ---------------------------------------------------------------------------
class TestSafePatterns:
    def _detect(self, code: str) -> list:
        tree = ast.parse(textwrap.dedent(code))
        return _detect_msg_exposure(tree)

    def test_literal_string_not_detected(self):
        # 字面量消息（非 f-string）不命中
        violations = self._detect('''
            raise ValueError("file not found")
        ''')
        assert violations == []

    def test_format_method_not_detected(self):
        # .format() 不是 f-string，不命中（保守起见）
        violations = self._detect('''
            raise ValueError("err: {}".format(path))
        ''')
        assert violations == []

    def test_non_sensitive_var_not_detected(self):
        # 非敏感变量名不命中
        violations = self._detect('''
            raise ValueError(f"bad value: {value}")
        ''')
        assert violations == []

    def test_bare_raise_not_detected(self):
        violations = self._detect('''
            try:
                pass
            except Exception:
                raise
        ''')
        assert violations == []

    def test_raise_variable_not_detected(self):
        # raise some_var（非构造）不检测
        violations = self._detect('''
            exc = ValueError("msg")
            raise exc
        ''')
        assert violations == []

    def test_no_args_exception_not_detected(self):
        # Exception() 无参构造不算
        violations = self._detect('''
            raise Exception()
        ''')
        assert violations == []

    def test_details_kwarg_safe(self):
        # details 字段正确用法不命中（消息文本无敏感变量）
        violations = self._detect('''
            raise TransactionError(
                "transaction timeout",
                details={"tx_id": tx_id, "path": str(file_path)},
            )
        ''')
        assert violations == []

    def test_non_exception_function_not_detected(self):
        # 函数名不以 Error/Exception 结尾不算
        violations = self._detect('''
            raise log_event(f"processing {path}")
        ''')
        assert violations == []


# ---------------------------------------------------------------------------
# TestNoqaExemption
# ---------------------------------------------------------------------------
class TestNoqaExemption:
    def test_is_line_noqa_detects_marker(self):
        content = 'raise Foo(f"x {path}")  # noqa: MSG-EXPOSURE\n'
        assert _is_line_noqa(content, 1) is True

    def test_is_line_noqa_without_marker(self):
        content = 'raise Foo(f"x {path}")\n'
        assert _is_line_noqa(content, 1) is False

    def test_filter_noqa_removes_marked_violations(self):
        content = textwrap.dedent('''
            raise FooError(f"x {path}")  # noqa: MSG-EXPOSURE
            raise BarError(f"y {tx_id}")
        ''')
        tree = ast.parse(content)
        violations = _detect_msg_exposure(tree)
        filtered = _filter_noqa_violations(content, violations)
        # 第一行被豁免，只剩第二行
        assert len(filtered) == 1
        assert filtered[0][1] == "BarError"


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
def _make_mock_gateway(
    staged_files_am: list[str],
    staged_files_a: list[str],
    file_contents: dict[str, str],
    file_diffs: dict[str, str] | None = None,
    project_root: str = ".",
    diff_fail: bool = False,
) -> MagicMock:
    """构造 mock gateway。"""
    gw = MagicMock()
    gw.project_root = project_root

    def _run_git(cmd):
        result = MagicMock()
        if diff_fail:
            result.returncode = 1
            result.stdout = ""
            return result
        # git diff --cached --name-only --diff-filter=AM
        if "--name-only" in cmd and "--diff-filter=AM" in cmd:
            result.returncode = 0
            result.stdout = "\n".join(staged_files_am)
            return result
        # git diff --cached --name-only --diff-filter=A
        if "--name-only" in cmd and "--diff-filter=A" in cmd:
            result.returncode = 0
            result.stdout = "\n".join(staged_files_a)
            return result
        # git rev-parse --show-toplevel
        if "rev-parse" in cmd:
            result.returncode = 0
            result.stdout = project_root
            return result
        # git diff --cached --unified=0 -- <file>
        if "--unified=0" in cmd:
            py_file = cmd[-1].replace("\\", "/")
            diff = (file_diffs or {}).get(py_file, "")
            result.returncode = 0
            result.stdout = diff
            return result
        result.returncode = 0
        result.stdout = ""
        return result

    gw._run_git.side_effect = _run_git
    return gw


class TestGatewayIntegration:
    def test_new_file_violation_blocks(self, tmp_path):
        # 新增文件含敏感变量 → 阻断
        py_file = tmp_path / "bad.py"
        py_file.write_text(
            'raise FileNotFoundError(f"missing: {file_path}")\n',
            encoding="utf-8",
        )
        rel = "bad.py"
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[rel],  # 新增
            file_contents={},
            project_root=str(tmp_path),
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is False
        assert "file_path" in detail
        assert "MSG-EXPOSURE" in detail or "5.99.20" in detail

    def test_new_file_clean_passes(self, tmp_path):
        # 新增文件无敏感变量 → 通过
        py_file = tmp_path / "good.py"
        py_file.write_text(
            'raise ValueError("bad input")\n',
            encoding="utf-8",
        )
        rel = "good.py"
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[rel],
            file_contents={},
            project_root=str(tmp_path),
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is True

    def test_modified_file_only_new_lines(self, tmp_path):
        # 修改文件：只检测 diff 新增行
        py_file = tmp_path / "mod.py"
        # 完整文件 3 行：raise 在 line 2（存量），x = 1 在 line 3（新增）
        py_file.write_text(
            'import os\n'
            'raise RuntimeError(f"old {path}")\n'  # line 2：存量代码
            'x = 1\n',  # line 3：diff 新增
            encoding="utf-8",
        )
        rel = "mod.py"
        # diff: line 1-2 是 context，line 3 是 added
        diff = (
            f"+++ b/{rel}\n"
            "@@ -1,2 +1,3 @@\n"
            " import os\n"
            " raise RuntimeError(f\"old {path}\")\n"
            "+x = 1\n"
        )
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[],  # 修改
            file_contents={},
            project_root=str(tmp_path),
            file_diffs={rel: diff},
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        # raise 在 line 2（存量），不在 diff 新增行（line 3）→ 通过
        assert passed is True, f"存量违规不应触发：{detail}"

    def test_modified_file_new_violating_line_blocks(self, tmp_path):
        # 修改文件：diff 新增行含违规 → 阻断
        py_file = tmp_path / "mod2.py"
        py_file.write_text(
            'import os\n'
            'raise RuntimeError(f"new {path}")\n',  # 行 2：diff 新增
            encoding="utf-8",
        )
        rel = "mod2.py"
        diff = (
            f"+++ b/{rel}\n"
            "@@ -1,0 +2,1 @@\n"
            "+raise RuntimeError(f\"new {path}\")\n"
        )
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[],
            file_contents={},
            project_root=str(tmp_path),
            file_diffs={rel: diff},
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is False
        assert "path" in detail

    def test_tests_exempt(self, tmp_path):
        # tests/ 下文件豁免
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        py_file = tests_dir / "test_x.py"
        py_file.write_text(
            'raise ValueError(f"bad {path}")\n',
            encoding="utf-8",
        )
        rel = "tests/test_x.py"
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[rel],
            file_contents={},
            project_root=str(tmp_path),
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is True

    def test_commit_gates_self_exempt(self, tmp_path):
        # governance/commit_gates/ 下文件自豁免
        gates_dir = tmp_path / "governance" / "commit_gates"
        gates_dir.mkdir(parents=True)
        py_file = gates_dir / "some_gate.py"
        py_file.write_text(
            'raise ValueError(f"bad {path}")\n',
            encoding="utf-8",
        )
        rel = "governance/commit_gates/some_gate.py"
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[rel],
            file_contents={},
            project_root=str(tmp_path),
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is True

    def test_fail_open_on_git_diff_fail(self):
        gw = _make_mock_gateway(
            staged_files_am=[],
            staged_files_a=[],
            file_contents={},
            diff_fail=True,
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True

    def test_noqa_line_passes(self, tmp_path):
        py_file = tmp_path / "noqa.py"
        py_file.write_text(
            'raise ValueError(f"bad {path}")  # noqa: MSG-EXPOSURE\n',
            encoding="utf-8",
        )
        rel = "noqa.py"
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[rel],
            file_contents={},
            project_root=str(tmp_path),
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is True, f"noqa 行应豁免：{detail}"

    def test_no_staged_files_passes(self):
        gw = _make_mock_gateway(
            staged_files_am=[],
            staged_files_a=[],
            file_contents={},
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True

    def test_non_py_file_passes(self, tmp_path):
        # .md 文件不在检测范围
        md_file = tmp_path / "readme.md"
        md_file.write_text("some content", encoding="utf-8")
        rel = "readme.md"
        gw = _make_mock_gateway(
            staged_files_am=[rel],
            staged_files_a=[rel],
            file_contents={},
            project_root=str(tmp_path),
        )
        spec = make_msg_exposure_gate()
        passed, detail = spec.check(gw, [rel])
        assert passed is True
