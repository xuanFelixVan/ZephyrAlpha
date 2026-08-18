# [A_test] module_id: MOD-GOV_consumers_accuracy_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-CONSUMERS-ACCURACY-001
# [MODULE] tests.governance.commit_gates.test_consumers_accuracy_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_consumers_accuracy_gate.py — CONSUMERS-ACCURACY 门禁单测（#ARCH-CONSUMERS-ACCURACY-001 治本）

权威依据：consumers_accuracy_gate.py（make_consumers_accuracy_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestParseConsumersField: [CONSUMERS] 字段解析（4 种格式 + 边界）
- TestCheckConsumersAccuracyOrphan: orphan 违规检测（括号内函数名不存在）
- TestCheckConsumersAccuracyPhantom: phantom 违规检测（消费者模块路径不存在）
- TestCheckConsumersAccuracyExempt: 抽象代号 / CJK / noqa 豁免
- TestCheckConsumersAccuracyMethodLevel: 方法级声明逐级缩短
- TestCheckConsumersAccuracyPass: 正常通过场景
- TestGatewayIntegration: mock gateway 完整流程
  - warn-only 不阻断 commit
  - tests/ 豁免
  - 限制 _SCAN_PREFIXES（src/ + scripts/governance/）
  - fail-open（git 异常 / ast 解析失败）
  - 多文件汇总
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: E402
    _matches_any_prefix,
    _module_to_file_candidates,
)
from zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate import (  # noqa: E402
    _ABSTRACT_CODE_PREFIXES,
    _CONSUMERS_RE,
    _check_filepath_exists,
    _classify_consumer_format,
    _has_cjk,
    check_consumers_accuracy,
    make_consumers_accuracy_gate,
    parse_consumers_field,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, project_root=None, diff_fails=False,
                  diff_raises=False, staged_content_map=None):
    """构造 mock gateway：--name-only 返回 staged 文件列表；
    git show :path 返回 staged 内容。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw.run_git = _raise
        return gw

    staged_content_map = staged_content_map or {}

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        # git show :path — 返回 staged 文件内容
        if "show" in cmd and cmd and ":" in cmd[-1]:
            path = cmd[-1].lstrip(":")
            return _MockResult(0, staged_content_map.get(path, ""))
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_is_gate_spec(self):
        assert isinstance(make_consumers_accuracy_gate(), GateSpec)

    def test_gate_id(self):
        assert make_consumers_accuracy_gate().gate_id == "CONSUMERS-ACCURACY"

    def test_priority_is_116(self):
        # 109-115 已被占用（RULING-COMMIT-VERIFIED/CAPABILITY-LOOKUP-REQUIRED/
        # GATE-PRECOMMIT-OFFLINE/FOLDER-CAPACITY-HARD-LIMIT/DEPGRAPH-PRE-REGISTRATION/
        # DERIVATION-ANNOTATION/RELATIVE-PATH-LITERAL），113 与 depgraph_pre_registration
        # 冲突，迁移至 116
        assert make_consumers_accuracy_gate().priority == 116


# ---------------------------------------------------------------------------
# TestParseConsumersField
# ---------------------------------------------------------------------------
class TestParseConsumersField:
    """[CONSUMERS] 字段解析（4 种格式 + 边界）。"""

    def test_no_consumers_field(self):
        """无 [CONSUMERS] 字段 → 空列表。"""
        content = "# [BLUEPRINT] MOD-X\n# [MODULE] foo\nprint('hello')\n"
        assert parse_consumers_field(content) == []

    def test_simple_module_path(self):
        """格式1：简单模块路径（无括号）。"""
        content = "# [CONSUMERS] zephyr.foo.bar; zephyr.baz.qux\n"
        result = parse_consumers_field(content)
        assert result == [
            ("zephyr.foo.bar", ""),
            ("zephyr.baz.qux", ""),
        ]

    def test_module_with_function_names(self):
        """格式2：模块+函数名（括号内）。"""
        content = "# [CONSUMERS] zephyr.foo.bar (func1, func2); zephyr.baz (func3)\n"
        result = parse_consumers_field(content)
        assert result == [
            ("zephyr.foo.bar", "func1, func2"),
            ("zephyr.baz", "func3"),
        ]

    def test_abstract_code(self):
        """格式3：抽象代号（MOD-XXX/SH-XXX）。"""
        content = "# [CONSUMERS] MOD-INF-027(audit-orchestrator)\n"
        result = parse_consumers_field(content)
        assert result == [("MOD-INF-027", "audit-orchestrator")]

    def test_method_level_declaration(self):
        """格式4：方法级声明（module.Class.method）。"""
        content = "# [CONSUMERS] zephyr.foo.bar.Class.method\n"
        result = parse_consumers_field(content)
        assert result == [("zephyr.foo.bar.Class.method", "")]

    def test_empty_content(self):
        """[CONSUMERS] 后无内容 → 空列表。"""
        content = "# [CONSUMERS]\n"
        assert parse_consumers_field(content) == []

    def test_consumers_field_beyond_line_30(self):
        """[CONSUMERS] 在第 31 行 → 不解析（与 CREATE-GUARD 对齐，前 30 行扫描）。"""
        lines = ["# placeholder\n"] * 30
        lines.append("# [CONSUMERS] zephyr.foo\n")
        content = "".join(lines)
        assert parse_consumers_field(content) == []

    def test_consumers_field_at_line_30(self):
        """[CONSUMERS] 在第 30 行 → 解析（边界包含）。"""
        lines = ["# placeholder\n"] * 29
        lines.append("# [CONSUMERS] zephyr.foo\n")
        content = "".join(lines)
        assert parse_consumers_field(content) == [("zephyr.foo", "")]

    def test_leading_whitespace_allowed(self):
        """前导空格允许（#  [CONSUMERS] 也匹配）。"""
        content = "  # [CONSUMERS] zephyr.foo\n"
        result = parse_consumers_field(content)
        assert result == [("zephyr.foo", "")]

    def test_no_space_after_hash(self):
        """无空格也匹配（#[CONSUMERS] 也合法）。"""
        content = "#[CONSUMERS] zephyr.foo\n"
        result = parse_consumers_field(content)
        assert result == [("zephyr.foo", "")]

    def test_consumers_regex_matches_typical(self):
        """正则匹配典型格式。"""
        m = _CONSUMERS_RE.match("# [CONSUMERS] zephyr.foo.bar (func1, func2)")
        assert m is not None
        assert m.group(1) == "zephyr.foo.bar (func1, func2)"


# ---------------------------------------------------------------------------
# TestCheckConsumersAccuracyOrphan
# ---------------------------------------------------------------------------
class TestCheckConsumersAccuracyOrphan:
    """orphan 违规检测——括号内函数名在当前文件中不存在。

    注：测试需先创建消费者模块文件让 phantom 检测通过，才能测试 orphan。
    """

    def _create_consumer_module(self, tmp_path, module_path="zephyr/foo/bar.py"):
        """在 tmp_path 下创建消费者模块文件（让 phantom 检测通过）。"""
        full = tmp_path / "src" / module_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text("# consumer module\n", encoding="utf-8")

    def test_orphan_function_violation(self, tmp_path):
        """括号内函数名不存在于当前文件 → orphan 违规。"""
        self._create_consumer_module(tmp_path)
        content = (
            "# [CONSUMERS] zephyr.foo.bar (nonexistent_function)\n"
            "def existing_function():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert len(violations) == 1
        assert "orphan function 'nonexistent_function'" in violations[0]

    def test_orphan_multiple_violations(self, tmp_path):
        """多个 orphan 函数名 → 多条违规。"""
        self._create_consumer_module(tmp_path, "zephyr/foo.py")
        content = (
            "# [CONSUMERS] zephyr.foo (ghost1, ghost2)\n"
            "def real_func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert len(violations) == 2
        assert any("ghost1" in v for v in violations)
        assert any("ghost2" in v for v in violations)

    def test_existing_function_no_orphan(self, tmp_path):
        """括号内函数名都存在于当前文件 → 无违规。"""
        self._create_consumer_module(tmp_path, "zephyr/foo.py")
        content = (
            "# [CONSUMERS] zephyr.foo (func1, func2)\n"
            "def func1():\n"
            "    pass\n"
            "def func2():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_async_function_recognized(self, tmp_path):
        """async 函数也能被识别——不算 orphan。"""
        self._create_consumer_module(tmp_path, "zephyr/foo.py")
        content = (
            "# [CONSUMERS] zephyr.foo (async_func)\n"
            "async def async_func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []


# ---------------------------------------------------------------------------
# TestCheckConsumersAccuracyPhantom
# ---------------------------------------------------------------------------
class TestCheckConsumersAccuracyPhantom:
    """phantom 违规检测——消费者模块路径在项目内不存在。"""

    def test_phantom_module_violation(self, tmp_path):
        """消费者模块路径在项目内不存在 → phantom 违规。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module.path\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert len(violations) == 1
        assert "phantom consumer 'zephyr.nonexistent.module.path'" in violations[0]

    def test_phantom_no_orphan_check(self, tmp_path):
        """phantom 违规时不检测 orphan（模块都不存在，orphan 无意义）。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module (ghost_func)\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        # 只应有 1 条 phantom 违规，不应有 orphan 违规
        assert len(violations) == 1
        assert "phantom" in violations[0]

    def test_existing_module_no_phantom(self, tmp_path):
        """消费者模块路径在项目内存在 → 无 phantom 违规。"""
        # 创建一个假的模块文件
        module_path = tmp_path / "src" / "zephyr" / "foo" / "bar.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text("# fake module\n", encoding="utf-8")

        content = (
            "# [CONSUMERS] zephyr.foo.bar\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/baz.py", content, tmp_path
        )
        assert violations == []

    def test_existing_module_as_init_file(self, tmp_path):
        """消费者模块路径是包（__init__.py）→ 无 phantom 违规。"""
        # 创建 __init__.py
        init_path = tmp_path / "src" / "zephyr" / "foo" / "__init__.py"
        init_path.parent.mkdir(parents=True, exist_ok=True)
        init_path.write_text("# package init\n", encoding="utf-8")

        content = (
            "# [CONSUMERS] zephyr.foo\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/baz.py", content, tmp_path
        )
        assert violations == []


# ---------------------------------------------------------------------------
# TestConsumerFormatClassification (#ARCH-CONSUMERS-ACCURACY-004 治本)
# ---------------------------------------------------------------------------
class TestConsumerFormatClassification:
    """consumer 声明格式分类——4 种格式分别处理（治本 phantom 误报）。"""

    def test_classify_dotted_module_path(self):
        """dotted 模块路径（a.b.c）→ 'dotted'。"""
        assert _classify_consumer_format("zephyr.foo.bar") == "dotted"
        assert _classify_consumer_format("zephyr.gov_enforcement.commit_gates.create_guard") == "dotted"

    def test_classify_filepath_with_slash(self):
        """slash 文件路径（含 /）→ 'filepath'。"""
        assert _classify_consumer_format("scripts/git_commit.py") == "filepath"
        assert _classify_consumer_format("scripts/governance/session_worktree_cli.py") == "filepath"
        assert _classify_consumer_format("src/zephyr/governance/") == "filepath"

    def test_classify_filepath_with_extension(self):
        """以文件扩展名结尾（无 /）→ 'filepath'。"""
        assert _classify_consumer_format("git_commit.py") == "filepath"
        assert _classify_consumer_format("config.yaml") == "filepath"

    def test_classify_glob_pattern(self):
        """glob 模式（含 * 或 ?）→ 'glob'。"""
        assert _classify_consumer_format("scripts/governance/*") == "glob"
        assert _classify_consumer_format("scripts/governance/*.py") == "glob"
        assert _classify_consumer_format("tests/test_*.py") == "glob"

    def test_classify_descriptive_with_cjk(self):
        """含 CJK 字符 → 'descriptive'。"""
        assert _classify_consumer_format("AI 对话启动时调用") == "descriptive"
        assert _classify_consumer_format("AI 同步 YAML→DB 时调用") == "descriptive"

    def test_classify_descriptive_with_space(self):
        """含空格 → 'descriptive'。"""
        assert _classify_consumer_format("manual CLI") == "descriptive"
        assert _classify_consumer_format("post-commit hook") == "descriptive"

    def test_classify_descriptive_with_paren_prefix(self):
        """以括号开头 → 'descriptive'。"""
        assert _classify_consumer_format("(manual CLI)") == "descriptive"
        assert _classify_consumer_format("(invoked by AI)") == "descriptive"

    def test_check_filepath_exists_relative(self, tmp_path):
        """文件路径存在性检查——相对路径。"""
        (tmp_path / "scripts" / "git_commit.py").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "scripts" / "git_commit.py").write_text("# fake\n", encoding="utf-8")
        assert _check_filepath_exists("scripts/git_commit.py", tmp_path) is True

    def test_check_filepath_not_exists(self, tmp_path):
        """文件路径不存在性检查。"""
        assert _check_filepath_exists("scripts/nonexistent.py", tmp_path) is False

    def test_check_filepath_exists_with_src_prefix(self, tmp_path):
        """文件路径存在性检查——src/ 前缀路径。"""
        (tmp_path / "zephyr" / "foo.py").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "zephyr" / "foo.py").write_text("# fake\n", encoding="utf-8")
        assert _check_filepath_exists("src/zephyr/foo.py", tmp_path) is True


# ---------------------------------------------------------------------------
# TestConsumersAccuracyFilepathFormat (#ARCH-CONSUMERS-ACCURACY-004 治本)
# ---------------------------------------------------------------------------
class TestConsumersAccuracyFilepathFormat:
    """filepath 格式的 [CONSUMERS] 声明不再误报 phantom（治本验证）。"""

    def test_filepath_consumer_exists_no_phantom(self, tmp_path):
        """文件路径格式的 consumer 文件存在 → 不报 phantom（治本核心用例）。

        病根：原算法将 scripts/git_commit.py 当 dotted 路径处理，
        _module_to_file_candidates 生成错误候选路径 → 误报 phantom。
        """
        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "git_commit.py").write_text("# fake\n", encoding="utf-8")
        content = (
            "# [CONSUMERS] scripts/git_commit.py\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/gateway.py", content, tmp_path
        )
        assert violations == []

    def test_filepath_consumer_not_exists_phantom(self, tmp_path):
        """文件路径格式的 consumer 文件不存在 → 报 phantom。"""
        content = (
            "# [CONSUMERS] scripts/nonexistent.py\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/gateway.py", content, tmp_path
        )
        assert len(violations) == 1
        assert "phantom consumer 'scripts/nonexistent.py'" in violations[0]
        assert "文件路径" in violations[0]

    def test_glob_consumer_exempt(self, tmp_path):
        """glob 模式的 consumer 豁免（不检测 phantom）。"""
        content = (
            "# [CONSUMERS] scripts/governance/*\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_descriptive_consumer_exempt(self, tmp_path):
        """描述性文字的 consumer 豁免（不检测 phantom）。"""
        content = (
            "# [CONSUMERS] AI 对话启动时调用（AGENTS.md 规则）\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_mixed_formats(self, tmp_path):
        """混合格式：dotted + filepath + glob + descriptive 同时存在。"""
        (tmp_path / "src" / "zephyr" / "real_module.py").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / "zephyr" / "real_module.py").write_text("# fake\n", encoding="utf-8")
        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "real_cli.py").write_text("# fake\n", encoding="utf-8")
        content = (
            "# [CONSUMERS] zephyr.real_module; scripts/real_cli.py; "
            "scripts/governance/*; AI 手动调用\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        # 4 种格式：dotted 存在 + filepath 存在 + glob 豁免 + descriptive 豁免 → 无违规
        assert violations == []

    def test_real_world_git_commit_gateway_case(self, tmp_path):
        """真实用例：git_commit_gateway.py 的 [CONSUMERS] 声明不再误报。

        原声明: zephyr.governance.persistence.task_repo.TaskRepository.auto_commit_on_completion; scripts/git_commit.py
        """
        # 模拟项目结构
        (tmp_path / "src" / "zephyr" / "governance" / "persistence").mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / "zephyr" / "governance" / "persistence" / "task_repo.py").write_text(
            "# fake\n", encoding="utf-8"
        )
        (tmp_path / "scripts").mkdir(exist_ok=True)
        (tmp_path / "scripts" / "git_commit.py").write_text("# fake\n", encoding="utf-8")
        content = (
            "# [CONSUMERS] zephyr.governance.persistence.task_repo.TaskRepository.auto_commit_on_completion; scripts/git_commit.py\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
            content, tmp_path
        )
        assert violations == []


# ---------------------------------------------------------------------------
# TestCheckConsumersAccuracyExempt
# ---------------------------------------------------------------------------
class TestCheckConsumersAccuracyExempt:
    """豁免场景——抽象代号 / CJK / noqa。"""

    def test_abstract_code_mod_exempt(self, tmp_path):
        """MOD-XXX 抽象代号豁免——不检测 phantom/orphan。"""
        content = (
            "# [CONSUMERS] MOD-INF-027(audit-orchestrator)\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_abstract_code_sh_exempt(self, tmp_path):
        """SH-XXX 抽象代号豁免。"""
        content = (
            "# [CONSUMERS] SH-ABBR-001\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_abstract_code_cfg_exempt(self, tmp_path):
        """CFG-XXX 抽象代号豁免。"""
        content = (
            "# [CONSUMERS] CFG-noqa-exempt-registry\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_is_abstract_code_all_prefixes(self):
        """_matches_any_prefix 对所有抽象前缀返回 True。"""
        for prefix in _ABSTRACT_CODE_PREFIXES:
            assert _matches_any_prefix(f"{prefix}XXX-001", _ABSTRACT_CODE_PREFIXES) is True

    def test_is_abstract_code_non_abstract(self):
        """非抽象代号返回 False。"""
        assert _matches_any_prefix("zephyr.foo.bar", _ABSTRACT_CODE_PREFIXES) is False
        assert _matches_any_prefix("scripts.governance.foo", _ABSTRACT_CODE_PREFIXES) is False

    def test_cjk_in_parens_skipped(self, tmp_path):
        """括号内含 CJK 字符 → 视为描述性文字，跳过 orphan 检测。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module (审计编排器)\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        # 仍有 phantom 违规（模块不存在），但无 orphan 违规（CJK 跳过）
        assert len(violations) == 1
        assert "phantom" in violations[0]

    def test_has_cjk_detects_chinese(self):
        """_has_cjk 检测中文。"""
        assert _has_cjk("审计") is True
        assert _has_cjk("hello 世界") is True
        assert _has_cjk("hello world") is False
        assert _has_cjk("func1, func2") is False

    def test_noqa_file_exempt(self, tmp_path):
        """noqa: consumers-accuracy 文件级豁免——返回空列表。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module (ghost_func)\n"
            "def func():\n"
            "    pass\n"
            "# noqa: consumers-accuracy  过渡期豁免：历史漂移文件待修复\n"
        )
        noqa_files = {"src/zephyr/foo.py"}
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path, noqa_files=noqa_files
        )
        assert violations == []

    def test_noqa_other_file_not_exempt(self, tmp_path):
        """noqa 文件级豁免只对集合内文件生效——其他文件仍检测。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
        )
        noqa_files = {"src/zephyr/other.py"}
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path, noqa_files=noqa_files
        )
        assert len(violations) == 1
        assert "phantom" in violations[0]


# ---------------------------------------------------------------------------
# TestCheckConsumersAccuracyMethodLevel
# ---------------------------------------------------------------------------
class TestCheckConsumersAccuracyMethodLevel:
    """方法级声明逐级缩短——module.Class.method → module.Class → module。"""

    def test_method_level_shortens_to_module(self, tmp_path):
        """module.Class.method → 缩短到 module 找到文件 → 无 phantom 违规。"""
        # 创建模块文件
        module_path = tmp_path / "src" / "zephyr" / "foo" / "bar.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text("# fake module\n", encoding="utf-8")

        content = (
            "# [CONSUMERS] zephyr.foo.bar.ClassName.method_name\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/baz.py", content, tmp_path
        )
        assert violations == []

    def test_method_level_all_shortened_fail(self, tmp_path):
        """逐级缩短全部失败 → phantom 违规。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.ClassName.method_name\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert len(violations) == 1
        assert "phantom" in violations[0]


# ---------------------------------------------------------------------------
# TestCheckConsumersAccuracyPass
# ---------------------------------------------------------------------------
class TestCheckConsumersAccuracyPass:
    """正常通过场景。"""

    def test_no_consumers_field_passes(self, tmp_path):
        """无 [CONSUMERS] 字段 → 通过（CREATE-GUARD 负责存在性）。"""
        content = (
            "# [BLUEPRINT] MOD-X\n"
            "# [MODULE] foo\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_empty_consumers_passes(self, tmp_path):
        """[CONSUMERS] 空内容 → 通过。"""
        content = (
            "# [CONSUMERS]\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert violations == []

    def test_real_world_scenario_passes(self, tmp_path):
        """真实场景——模块路径存在 + 函数名存在 → 通过。"""
        # 创建消费者模块
        consumer_path = tmp_path / "src" / "zephyr" / "gov_enforcement" / "foo.py"
        consumer_path.parent.mkdir(parents=True, exist_ok=True)
        consumer_path.write_text("# consumer module\n", encoding="utf-8")

        content = (
            "# [CONSUMERS] zephyr.gov_enforcement.foo (make_foo, _internal_helper)\n"
            "def make_foo():\n"
            "    pass\n"
            "def _internal_helper():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/gov_enforcement/bar.py", content, tmp_path
        )
        assert violations == []


# ---------------------------------------------------------------------------
# TestModuleToFileCandidates
# ---------------------------------------------------------------------------
class TestModuleToFileCandidates:
    """_module_to_file_candidates 候选路径生成。"""

    def test_generates_four_candidates(self):
        """生成 4 个候选路径。"""
        candidates = _module_to_file_candidates("zephyr.foo.bar")
        assert len(candidates) == 4
        assert "src/zephyr/foo/bar.py" in candidates
        assert "src/zephyr/foo/bar/__init__.py" in candidates
        assert "zephyr/foo/bar.py" in candidates
        assert "zephyr/foo/bar/__init__.py" in candidates

    def test_single_segment_module(self):
        """单段模块路径也能生成候选。"""
        candidates = _module_to_file_candidates("foo")
        assert "src/foo.py" in candidates
        assert "src/foo/__init__.py" in candidates


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    """mock gateway 完整流程。"""

    def test_warn_only_does_not_block(self):
        """warn-only——检出违规但仍 passed=True（不阻断 commit）。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["src/zephyr/foo.py"],
            staged_content_map={"src/zephyr/foo.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["src/zephyr/foo.py"])
        # warn-only: passed=True 但 detail 有内容
        assert passed is True
        assert "CONSUMERS-ACCURACY" in detail
        assert "phantom" in detail

    def test_no_violations_passes_clean(self):
        """无违规 → passed=True + 空 detail。"""
        # 创建存在的模块
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            module_path = tmp_path / "src" / "zephyr" / "foo.py"
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("# module\n", encoding="utf-8")

            content = (
                "# [CONSUMERS] zephyr.foo\n"
                "def func():\n"
                "    pass\n"
            )
            gw = _make_gateway(
                staged_files=["src/zephyr/bar.py"],
                staged_content_map={"src/zephyr/bar.py": content},
                project_root=str(tmp_path),
            )
            gate = make_consumers_accuracy_gate()
            passed, detail = gate.check(gw, ["src/zephyr/bar.py"])
            assert passed is True
            assert detail == ""

    def test_tests_directory_exempt(self):
        """tests/ 目录豁免——不检测。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["tests/test_foo.py"],
            staged_content_map={"tests/test_foo.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["tests/test_foo.py"])
        assert passed is True
        assert detail == ""

    def test_non_scanned_prefix_skipped(self):
        """非 _SCAN_PREFIXES 路径的文件跳过——如 docs/。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["docs/some_file.py"],  # 不在 scripts/governance/ 或 src/
            staged_content_map={"docs/some_file.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["docs/some_file.py"])
        assert passed is True
        assert detail == ""

    def test_scripts_governance_scanned(self):
        """scripts/governance/ 路径在扫描范围内。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["scripts/governance/foo.py"],
            staged_content_map={"scripts/governance/foo.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["scripts/governance/foo.py"])
        assert passed is True
        assert "phantom" in detail

    def test_fail_open_git_diff_fails(self):
        """git diff --name-only 失败 → fail-open 放行。"""
        gw = _make_gateway(diff_fails=True)
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_fail_open_git_diff_raises(self):
        """git diff 异常 → fail-open 放行。"""
        gw = _make_gateway(diff_raises=True)
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_fail_open_no_project_root(self):
        """gateway.project_root 为 None → fail-open 放行。"""
        content = "# [CONSUMERS] zephyr.foo\n"
        gw = MagicMock()
        gw.project_root = None
        # _get_staged_py_files 需要的 _run_git
        gw.run_git.return_value = _MockResult(
            0, "src/zephyr/foo.py"
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["src/zephyr/foo.py"])
        assert passed is True
        assert detail == ""

    def test_multiple_files_aggregated(self):
        """多文件违规 → 汇总到一条 detail。"""
        content1 = (
            "# [CONSUMERS] zephyr.nonexistent1.module\n"
            "def func():\n"
            "    pass\n"
        )
        content2 = (
            "# [CONSUMERS] zephyr.nonexistent2.module\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["src/zephyr/foo.py", "src/zephyr/bar.py"],
            staged_content_map={
                "src/zephyr/foo.py": content1,
                "src/zephyr/bar.py": content2,
            },
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(
            gw, ["src/zephyr/foo.py", "src/zephyr/bar.py"]
        )
        assert passed is True
        assert "nonexistent1" in detail
        assert "nonexistent2" in detail

    def test_noqa_file_exempt_in_gateway(self):
        """noqa: consumers-accuracy 文件级豁免在 gateway 流程中生效。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
            "# noqa: consumers-accuracy  过渡期豁免：历史漂移文件待修复\n"
        )
        gw = _make_gateway(
            staged_files=["src/zephyr/foo.py"],
            staged_content_map={"src/zephyr/foo.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["src/zephyr/foo.py"])
        assert passed is True
        assert detail == ""

    def test_warning_truncation_at_50(self):
        """违规超过 50 条时截断 + 显示 more 计数。"""
        # 构造 60 个 phantom 违规（60 个不存在的模块）
        consumers = "; ".join(
            f"zephyr.nonexistent{i}.module" for i in range(60)
        )
        content = (
            f"# [CONSUMERS] {consumers}\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["src/zephyr/foo.py"],
            staged_content_map={"src/zephyr/foo.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["src/zephyr/foo.py"])
        assert passed is True
        assert "+10 more" in detail

    def test_warning_detail_contains_remediation_hint(self):
        """违规 detail 含修复提示（病根 + 修复步骤）。"""
        content = (
            "# [CONSUMERS] zephyr.nonexistent.module\n"
            "def func():\n"
            "    pass\n"
        )
        gw = _make_gateway(
            staged_files=["src/zephyr/foo.py"],
            staged_content_map={"src/zephyr/foo.py": content},
        )
        gate = make_consumers_accuracy_gate()
        passed, detail = gate.check(gw, ["src/zephyr/foo.py"])
        assert "病根" in detail
        assert "修复" in detail
        assert "noqa: consumers-accuracy" in detail  # 逃生通道提示


# ---------------------------------------------------------------------------
# TestFailOpenEdgeCases
# ---------------------------------------------------------------------------
class TestFailOpenEdgeCases:
    """fail-open 边界场景。"""

    def test_check_consumers_accuracy_ast_failure_fail_open(self, tmp_path):
        """文件内容含语法错误 → _collect_function_names 返回空集 → orphan 不误报。"""
        # 先创建消费者模块让 phantom 检测通过
        module_path = tmp_path / "src" / "zephyr" / "foo" / "bar.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text("# module\n", encoding="utf-8")

        # 语法错误会让 ast.parse 失败，_collect_function_names 返回 set()
        # 此时所有括号内函数名都会被视为 orphan——但实际是 fail-open 设计
        # 此测试验证 fail-open 行为：ast 失败时 defined_functions=set()，
        # 因此所有括号内函数名都会触发 orphan（fail-open 是向下安全：误报不漏检）
        content = (
            "# [CONSUMERS] zephyr.foo.bar (func1)\n"
            "def func1(\n"  # 语法错误：缺少右括号
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        # ast 失败 → defined_functions=set() → func1 视为 orphan
        # 但这只是 fail-open 的"向下安全"（不漏检），实际场景中语法错误文件
        # 会在更早阶段（如 syntax check）失败
        assert any("orphan" in v for v in violations)

    def test_check_consumers_accuracy_empty_parens(self, tmp_path):
        """括号内容为空 → 无 orphan 检测。"""
        # 创建模块以避免 phantom
        module_path = tmp_path / "src" / "zephyr" / "foo" / "bar.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text("# module\n", encoding="utf-8")

        content = (
            "# [CONSUMERS] zephyr.foo.bar ()\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/baz.py", content, tmp_path
        )
        assert violations == []

    def test_check_consumers_accuracy_multiple_consumers_mixed(self, tmp_path):
        """多消费者混合：一个 phantom 一个正常 → 只报 phantom。"""
        # 创建正常模块
        module_path = tmp_path / "src" / "zephyr" / "good" / "module.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text("# module\n", encoding="utf-8")

        content = (
            "# [CONSUMERS] zephyr.good.module; zephyr.bad.nonexistent\n"
            "def func():\n"
            "    pass\n"
        )
        violations = check_consumers_accuracy(
            "src/zephyr/foo.py", content, tmp_path
        )
        assert len(violations) == 1
        assert "phantom" in violations[0]
        assert "bad.nonexistent" in violations[0]
