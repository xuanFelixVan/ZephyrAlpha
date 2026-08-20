# [A_test] module_id: MOD-GOV_audit_return_contract_usage | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-279 | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-5
# [MODULE] tests.governance.test_audit_return_contract_usage
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess error->skip_test
# [TESTS] tests/governance/test_audit_return_contract_usage.py
# [A_module] module_id=MOD-TEST-279 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_audit_return_contract_usage.py — 返回契约 ok 键审计脚本单元测试

#Ruling-100PCT-AI-GOVERNANCE P2-5 治本：验证 audit_return_contract_usage.py 的检测逻辑。

病根
----
session_worktree_commit/merge/abort 等 TypedDict 返回契约已定义 ``ok: bool`` 作为
消费方判定成败的唯一入口，但 AI 生成的脚本可能误用旧键名（``committed`` / ``merged``
/ ``success``），导致 KeyError 静默失败或语义误判。

治本
----
本测试覆盖 audit_return_contract_usage.py 的：
1. ``KNOWN_MISUSE_PATTERNS`` 完整性：所有 session_worktree_* + emergency_commit 已登记
2. ``_audit_file_ast()`` AST 检测：Subscript 节点访问 forbidden key
3. ``_audit_file_regex()`` 正则检测：快速行扫描
4. ``audit_return_contract_usage()`` 去重 + 排序
5. ``audit_directory()`` 目录排除（.git/__pycache__/.pytest_cache）
6. ``main()`` CLI exit code（0=无违规，1=有 error severity 违规）

测试策略
--------
- 正向：构造各种 forbidden key 访问模式，验证被检测到
- 负向：合法 ``ok`` 键访问不触发违规；其他 dict 访问不触发
- 边界：SyntaxError 文件 skip；空文件；无 session_worktree 调用
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "governance" / "audit_return_contract_usage.py"


# ---------------------------------------------------------------------------
# 加载被测模块（独立脚本，不依赖 __init__.py）
# ---------------------------------------------------------------------------


def _load_audit_module():
    """用 importlib 加载 audit_return_contract_usage.py 为模块。

    注意：@dataclass 装饰器在 Python 3.11+ 需要 ``sys.modules[mod.__name__]`` 存在
    （dataclasses._is_type 会查 cls.__module__），故必须在 exec_module 前注册到 sys.modules。
    """
    import importlib.util

    mod_name = "_test_target_audit_return_contract_usage"
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"无法加载 {SCRIPT_PATH}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod  # 关键：dataclass 需要 sys.modules 注册
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def au():
    """加载被测模块。"""
    return _load_audit_module()


# ---------------------------------------------------------------------------
# KNOWN_MISUSE_PATTERNS 完整性测试
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


class TestKnownMisusePatterns:
    """验证 KNOWN_MISUSE_PATTERNS 涵盖所有 session_worktree_* + emergency_commit。"""

    def test_patterns_includes_all_session_worktree_funcs(self, au):
        """所有 session_worktree_* 公开函数都在 KNOWN_MISUSE_PATTERNS 中。"""
        required = {
            "session_worktree_commit",
            "session_worktree_merge",
            "session_worktree_abort",
            "session_worktree_start",
            "session_worktree_status",
            "session_worktree_sweep",
        }
        for func in required:
            assert func in au.KNOWN_MISUSE_PATTERNS, f"KNOWN_MISUSE_PATTERNS 缺少 {func}"

    def test_patterns_includes_emergency_commit(self, au):
        """P2-1 emergency_commit 也用 ok 键，必须登记。"""
        assert "emergency_commit" in au.KNOWN_MISUSE_PATTERNS

    def test_patterns_commit_forbids_committed_and_success(self, au):
        """session_worktree_commit 禁用 committed/success/status_ok。"""
        forbidden = au.KNOWN_MISUSE_PATTERNS["session_worktree_commit"]
        assert "committed" in forbidden
        assert "success" in forbidden
        assert "status_ok" in forbidden

    def test_patterns_merge_forbids_merged(self, au):
        """session_worktree_merge 禁用 merged（语义≠ok，warning severity）。"""
        assert "merged" in au.KNOWN_MISUSE_PATTERNS["session_worktree_merge"]

    def test_patterns_values_are_sets(self, au):
        """每个 function 对应的 forbidden 集合必须是 set 类型。"""
        for func, forbidden in au.KNOWN_MISUSE_PATTERNS.items():
            assert isinstance(forbidden, set), f"{func} 对应 forbidden 必须是 set，实际是 {type(forbidden)}"


# ---------------------------------------------------------------------------
# _audit_file_ast 测试
# ---------------------------------------------------------------------------


class TestAuditFileAst:
    """AST 检测 Subscript 节点访问 forbidden key。"""

    def test_detects_subscript_committed_access(self, au, tmp_path):
        """``r = session_worktree_commit(...); if r["committed"]:`` → 命中。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit
            r = session_worktree_commit("sess-1", ["a.py"], "msg")
            if r["committed"]:
                print("ok")
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert len(violations) == 1
        v = violations[0]
        assert v.function == "session_worktree_commit"
        assert v.forbidden_key == "committed"
        assert v.severity == "error"
        assert v.pattern == "subscript_access"

    def test_detects_subscript_success_access(self, au, tmp_path):
        """``r["success"]`` → 命中 error severity。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_start("sess-1")
            x = r["success"]
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert len(violations) == 1
        assert v_forbidden_key(violations, "session_worktree_start") == "success"

    def test_detects_merged_as_warning(self, au, tmp_path):
        """``r["merged"]`` 语义≠ok → warning severity（非 error）。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_merge("sess-1")
            if r["merged"]:
                pass
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert len(violations) == 1
        v = violations[0]
        assert v.forbidden_key == "merged"
        assert v.severity == "warning"

    def test_detects_emergency_commit_committed(self, au, tmp_path):
        """emergency_commit 返回值访问 ``["committed"]`` → 命中。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
            r = emergency_commit(files=["a.py"], message="m", session_id="s1")
            if r["committed"]:
                pass
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert len(violations) == 1
        assert violations[0].function == "emergency_commit"
        assert violations[0].forbidden_key == "committed"
        assert violations[0].severity == "error"

    def test_detects_attribute_call_binding(self, au, tmp_path):
        """``r = sw.session_worktree_commit(...)`` 属性调用也能检测。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            import zephyr.gov_enforcement.rule_bridge.session_worktree as sw
            r = sw.session_worktree_commit("sess-1", ["a.py"], "msg")
            print(r["success"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert len(violations) == 1
        assert violations[0].function == "session_worktree_commit"

    def test_legitimate_ok_key_no_violation(self, au, tmp_path):
        """合法 ``r["ok"]`` 访问不触发违规（ok 不在 forbidden 集合）。"""
        f = tmp_path / "legit.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("sess-1", ["a.py"], "msg")
            if r["ok"]:
                print("ok")
            if r["commit_hash"]:
                print(r["commit_hash"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert violations == []

    def test_unrelated_dict_access_no_violation(self, au, tmp_path):
        """非 session_worktree_* 返回值的 dict 访问不触发违规。"""
        f = tmp_path / "legit.py"
        f.write_text(
            textwrap.dedent("""
            d = {"committed": True, "success": False}
            if d["committed"]:
                print("ok")
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert violations == []

    def test_syntax_error_file_skipped(self, au, tmp_path):
        """SyntaxError 文件 skip（返回空列表，不抛异常）。"""
        f = tmp_path / "broken.py"
        f.write_text("def broken(:\n    pass\n", encoding="utf-8")
        violations = au.audit_file_ast(f)
        assert violations == []

    def test_no_call_no_violation(self, au, tmp_path):
        """无 session_worktree_* 调用 → 无违规。"""
        f = tmp_path / "plain.py"
        f.write_text(
            textwrap.dedent("""
            x = {"committed": True}
            print(x["committed"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert violations == []

    def test_violation_includes_line_col_snippet(self, au, tmp_path):
        """Violation 包含 line/col/snippet 字段。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("sess-1", ["a.py"], "msg")
            if r["committed"]:
                pass
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_ast(f)
        assert len(violations) == 1
        v = violations[0]
        assert v.line > 0
        assert v.col >= 0
        assert "committed" in v.snippet


def v_forbidden_key(violations, function_name):
    """从 violations 中找出指定 function 的 forbidden_key。"""
    for v in violations:
        if v.function == function_name:
            return v.forbidden_key
    return None


# ---------------------------------------------------------------------------
# _audit_file_regex 测试
# ---------------------------------------------------------------------------


class TestAuditFileRegex:
    """正则检测 forbidden key 访问（快速行扫描）。"""

    def test_detects_committed_regex(self, au, tmp_path):
        """``r["committed"]`` 被正则命中。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("sess-1", ["a.py"], "msg")
            if r["committed"]:
                print("ok")
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_regex(f)
        assert len(violations) >= 1
        keys = {v.forbidden_key for v in violations}
        assert "committed" in keys

    def test_detects_single_quote_access(self, au, tmp_path):
        """``r['success']`` 单引号也能命中。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_start("sess-1")
            x = r['success']
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_regex(f)
        assert len(violations) >= 1
        assert any(v.forbidden_key == "success" for v in violations)

    def test_no_binding_no_violation(self, au, tmp_path):
        """无 session_worktree_* 调用赋值 → 正则不命中。"""
        f = tmp_path / "plain.py"
        f.write_text(
            textwrap.dedent("""
            d = {"committed": True}
            print(d["committed"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_regex(f)
        assert violations == []

    def test_merged_regex_is_warning(self, au, tmp_path):
        """``r["merged"]`` 正则命中 warning severity。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_merge("sess-1")
            print(r["merged"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_file_regex(f)
        assert len(violations) >= 1
        merged_v = [v for v in violations if v.forbidden_key == "merged"]
        assert len(merged_v) >= 1
        assert all(v.severity == "warning" for v in merged_v)


# ---------------------------------------------------------------------------
# audit_return_contract_usage 测试（去重 + 排序）
# ---------------------------------------------------------------------------


class TestAuditReturnContractUsage:
    """audit_return_contract_usage 主 API。"""

    def test_dedup_ast_regex_overlap(self, au, tmp_path):
        """AST + regex 命中同一行 → 去重为 1 条。"""
        f = tmp_path / "misuse.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("sess-1", ["a.py"], "msg")
            if r["committed"]:
                pass
        """),
            encoding="utf-8",
        )
        violations = au.audit_return_contract_usage([f])
        # AST 和 regex 都会命中，但去重后只保留 1 条
        committed_v = [v for v in violations if v.forbidden_key == "committed"]
        assert len(committed_v) == 1

    def test_sorting_by_file_line_col(self, au, tmp_path):
        """多文件多违规按 (file, line, col) 排序。"""
        f1 = tmp_path / "a.py"
        f1.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            x = r["committed"]
            y = r["success"]
        """),
            encoding="utf-8",
        )
        f2 = tmp_path / "b.py"
        f2.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            z = r["success"]
        """),
            encoding="utf-8",
        )
        violations = au.audit_return_contract_usage([f1, f2])
        # 验证排序
        for i in range(len(violations) - 1):
            cur = (violations[i].file, violations[i].line, violations[i].col)
            nxt = (violations[i + 1].file, violations[i + 1].line, violations[i + 1].col)
            assert cur <= nxt, f"排序错误: {cur} > {nxt}"

    def test_directory_traversal(self, au, tmp_path):
        """传入目录 → 递归扫描 .py 文件。"""
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "misuse.py").write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            print(r["committed"])
        """),
            encoding="utf-8",
        )
        (tmp_path / "plain.py").write_text("x = 1\n", encoding="utf-8")
        violations = au.audit_return_contract_usage([tmp_path])
        assert len(violations) >= 1
        assert any("misuse.py" in v.file for v in violations)

    def test_non_python_file_ignored(self, au, tmp_path):
        """非 .py 文件被忽略。"""
        f = tmp_path / "misuse.txt"
        f.write_text('r = session_worktree_commit(...)\nr["committed"]\n', encoding="utf-8")
        violations = au.audit_return_contract_usage([f])
        assert violations == []

    def test_empty_paths_returns_empty(self, au):
        """空路径列表 → 空违规列表。"""
        assert au.audit_return_contract_usage([]) == []

    def test_nonexistent_path_skipped(self, au, tmp_path):
        """不存在的路径 → skip（不抛异常）。"""
        fake = tmp_path / "does_not_exist.py"
        violations = au.audit_return_contract_usage([fake])
        assert violations == []


# ---------------------------------------------------------------------------
# audit_directory 测试（排除 .git/__pycache__/.pytest_cache）
# ---------------------------------------------------------------------------


class TestAuditDirectory:
    """目录扫描 + 排除逻辑。"""

    def test_excludes_git_dir(self, au, tmp_path):
        """.git/ 目录下的 .py 文件不扫描。"""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "hook.py").write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            print(r["committed"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_directory(tmp_path)
        assert all(".git" not in v.file for v in violations), ".git/ 目录文件不应被扫描"

    def test_excludes_pycache(self, au, tmp_path):
        """__pycache__/ 目录不扫描。"""
        pc = tmp_path / "__pycache__"
        pc.mkdir()
        (pc / "cached.py").write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            print(r["committed"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_directory(tmp_path)
        assert all("__pycache__" not in v.file for v in violations)

    def test_custom_exclude_dirs(self, au, tmp_path):
        """额外排除目录。"""
        exclude_me = tmp_path / "exclude_me"
        exclude_me.mkdir()
        (exclude_me / "misuse.py").write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            print(r["committed"])
        """),
            encoding="utf-8",
        )
        violations = au.audit_directory(tmp_path, exclude_dirs={"exclude_me"})
        assert all("exclude_me" not in v.file for v in violations)

    def test_scans_real_violations_in_subdir(self, au, tmp_path):
        """子目录中的真实违规被扫描到。"""
        sub = tmp_path / "scripts"
        sub.mkdir()
        (sub / "bad.py").write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            if r["committed"]:
                pass
        """),
            encoding="utf-8",
        )
        violations = au.audit_directory(tmp_path)
        assert len(violations) >= 1
        assert any("bad.py" in v.file and v.forbidden_key == "committed" for v in violations)


# ---------------------------------------------------------------------------
# main() CLI 测试
# ---------------------------------------------------------------------------


class TestMainCli:
    """CLI 入口 exit code 与输出。"""

    def test_main_exit_zero_no_violations(self, au, tmp_path):
        """无违规 → exit 0。"""
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n", encoding="utf-8")
        rc = au.main.__wrapped__() if hasattr(au.main, "__wrapped__") else None
        # 直接用 subprocess 跑 CLI，避免 argv 污染
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert "0 violations" in result.stdout

    def test_main_exit_one_with_error_violation(self, au, tmp_path):
        """有 error severity 违规 → exit 1。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            if r["committed"]:
                pass
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 1
        assert "committed" in result.stdout

    def test_main_json_output(self, au, tmp_path):
        """--json 输出 JSON 数组。"""
        f = tmp_path / "bad.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_commit("s", ["f"], "m")
            print(r["committed"])
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--json", str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # 即使有违规，JSON 也应能解析
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "forbidden_key" in data[0]
        assert "file" in data[0]
        assert "line" in data[0]

    def test_main_only_warning_exit_zero(self, au, tmp_path):
        """只有 warning（merged）无 error → exit 0（warning 不阻断）。"""
        f = tmp_path / "warn.py"
        f.write_text(
            textwrap.dedent("""
            r = session_worktree_merge("s")
            print(r["merged"])
        """),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(f)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # warning 不算 error，exit 0
        assert result.returncode == 0
        assert "merged" in result.stdout


# ---------------------------------------------------------------------------
# e2e 真实仓库 smoke test
# ---------------------------------------------------------------------------


class TestE2ERealRepo:
    """在真实 ZephyrAlpha 仓库上跑审计，验证不崩溃且当前无 error 违规。"""

    def test_real_repo_audit_no_errors(self, au):
        """真实仓库 src/ + scripts/ 无 error severity 违规。"""
        violations = au.audit_directory(REPO_ROOT / "src")
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], (
            f"src/ 发现 {len(errors)} 个 error severity 违规（应为 0）: "
            f"{[(v.file, v.line, v.forbidden_key) for v in errors[:5]]}"
        )

    def test_real_repo_audit_scripts_no_errors(self, au):
        """真实仓库 scripts/ 无 error severity 违规。"""
        violations = au.audit_directory(REPO_ROOT / "scripts")
        errors = [v for v in violations if v.severity == "error"]
        assert errors == [], (
            f"scripts/ 发现 {len(errors)} 个 error severity 违规（应为 0）: "
            f"{[(v.file, v.line, v.forbidden_key) for v in errors[:5]]}"
        )
