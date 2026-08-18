# [A_test] module_id: MOD-requirements_version_sync_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-requirements_version_sync | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] tests.scripts.governance.d8_doc_sync.test_requirements_version_sync_reconciler
# [TESTS] —
# [TTL] permanent
"""test_requirements_version_sync_reconciler.py — requirements↔pyproject 依赖一致性校验 reconciler 测试

对标 requirements_version_sync_reconciler.py（AI-01 P1 治本，header [TESTS] 声明兑现）。
覆盖：无漂移/缺失/多余/版本不一致/-r跳过/包名规范化/触发条件/容错降级。

治本病根（2026-08-01，AI-01 P1）：reconciler 已实现+已注册 git_commit_gateway，唯一缺口是
header [TESTS] 声明的测试文件不存在。本文件兑现声明，建立回归保护。
"""
from __future__ import annotations

import sys
from pathlib import Path

# 将 scripts/governance/d8_doc_sync 加入 sys.path 以导入被测 reconciler
# tests/scripts/governance/d8_doc_sync/ → parents[4] = 项目根
_SCRIPT_DIR = Path(__file__).resolve().parents[4] / "scripts" / "governance" / "d8_doc_sync"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import pytest
import requirements_version_sync_reconciler as _rvsr  # noqa: E402
from requirements_version_sync_reconciler import (  # noqa: E402
    _check_pair,
    _normalize_name,
    _parse_pyproject_dependencies,
    _parse_pyproject_optional,
    _parse_requirements_file,
    _split_name_version,
    _trigger,
    make_requirements_version_sync_reconciler,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(autouse=True)
def _repin_project_root():
    """重钉模块全局 _project_root：工厂 make_*(project_root) 会 global 改写模块级
    _project_root（gateway L866-867 eager 注册时已钉到 tmp 根）——防跨测试全局污染。"""
    _rvsr.make_requirements_version_sync_reconciler(_PROJECT_ROOT)
    yield
    _rvsr.make_requirements_version_sync_reconciler(_PROJECT_ROOT)


# ── 辅助：构造临时 pyproject.toml + requirements 文件 ──

_PYPROJECT_TEMPLATE = """\
[build-system]
requires = ["setuptools>=68.0"]

[project]
name = "zephyr"
version = "5.34.1"
dependencies = [{main_deps}]

[project.optional-dependencies]
dev = [{dev_deps}]
demo = [{demo_deps}]
"""


def _write_pyproject(tmp_path: Path, main_deps: list[str], dev_deps: list[str], demo_deps: list[str]) -> Path:
    """在 tmp_path 下写 pyproject.toml，返回路径。"""
    def _fmt(deps: list[str]) -> str:
        return ", ".join(f'"{d}"' for d in deps)
    content = _PYPROJECT_TEMPLATE.format(
        main_deps=_fmt(main_deps),
        dev_deps=_fmt(dev_deps),
        demo_deps=_fmt(demo_deps),
    )
    p = tmp_path / "pyproject.toml"
    p.write_text(content, encoding="utf-8")
    return p


def _write_requirements(tmp_path: Path, name: str, lines: list[str]) -> Path:
    """在 tmp_path 下写 requirements 文件，返回路径。"""
    p = tmp_path / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


# ── 单元测试：解析函数 ──

class TestNormalizeName:
    """包名规范化（PEP 508 大小写/分隔符不敏感）。"""

    def test_lowercase(self):
        assert _normalize_name("Pydantic") == "pydantic"

    def test_hyphen_to_underscore(self):
        assert _normalize_name("import-lib") == "import_lib"

    def test_already_normalized(self):
        assert _normalize_name("pytest") == "pytest"

    def test_mixed_case_hyphen(self):
        assert _normalize_name("PyYAML-Lib") == "pyyaml_lib"


class TestSplitNameVersion:
    """PEP 508 依赖规格分离。"""

    def test_with_version_constraint(self):
        name, version = _split_name_version("pydantic>=2.0.0,<3.0.0")
        assert name == "pydantic"
        assert version == ">=2.0.0,<3.0.0"

    def test_without_version(self):
        name, version = _split_name_version("requests")
        assert name == "requests"
        assert version == ""

    def test_with_extras(self):
        name, version = _split_name_version("package[extra]>=1.0")
        assert name == "package"
        assert version == ">=1.0"


class TestParsePyproject:
    """pyproject.toml 依赖解析。"""

    def test_parse_main_dependencies(self, tmp_path):
        p = _write_pyproject(tmp_path, ["pydantic>=2.0.0", "pytest>=8.0.0"], [], [])
        text = p.read_text(encoding="utf-8")
        deps = _parse_pyproject_dependencies(text)
        assert deps == {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}

    def test_parse_optional_dev(self, tmp_path):
        p = _write_pyproject(tmp_path, [], ["ruff>=0.5.0", "mypy>=1.10.0"], [])
        text = p.read_text(encoding="utf-8")
        deps = _parse_pyproject_optional(text, "dev")
        assert deps == {"ruff": ">=0.5.0", "mypy": ">=1.10.0"}

    def test_parse_optional_demo(self, tmp_path):
        p = _write_pyproject(tmp_path, [], [], ["streamlit>=1.30.0"])
        text = p.read_text(encoding="utf-8")
        deps = _parse_pyproject_optional(text, "demo")
        assert deps == {"streamlit": ">=1.30.0"}

    def test_empty_dependencies(self, tmp_path):
        p = _write_pyproject(tmp_path, [], [], [])
        text = p.read_text(encoding="utf-8")
        assert _parse_pyproject_dependencies(text) == {}
        assert _parse_pyproject_optional(text, "dev") == {}
        assert _parse_pyproject_optional(text, "demo") == {}


class TestParseRequirementsFile:
    """requirements 文件解析（跳过注释/-r/空行/行内注释/环境标记）。"""

    def test_basic_parse(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements.txt", [
            "pydantic>=2.0.0",
            "pytest>=8.0.0",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}

    def test_skip_comments(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements.txt", [
            "# This is a comment",
            "pydantic>=2.0.0",
            "# Another comment",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"pydantic": ">=2.0.0"}

    def test_skip_dash_r(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements-dev.txt", [
            "-r requirements.txt",
            "ruff>=0.5.0",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"ruff": ">=0.5.0"}

    def test_skip_dash_e(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements.txt", [
            "-e .",
            "pytest>=8.0.0",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"pytest": ">=8.0.0"}

    def test_skip_inline_comment(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements.txt", [
            "pydantic>=2.0.0 # ORM",
            "pytest>=8.0.0",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}

    def test_strip_env_marker(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements.txt", [
            "pydantic>=2.0.0; python_version>='3.12'",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"pydantic": ">=2.0.0"}

    def test_skip_empty_lines(self, tmp_path):
        p = _write_requirements(tmp_path, "requirements.txt", [
            "",
            "pydantic>=2.0.0",
            "",
            "",
            "pytest>=8.0.0",
            "",
        ])
        deps = _parse_requirements_file(p)
        assert deps == {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}


# ── 单元测试：对比函数 ──

class TestCheckPair:
    """依赖集对比（缺失/多余/版本不一致）。"""

    def test_no_drift(self):
        req = {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}
        py = {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}
        assert _check_pair(req, py, "label") == []

    def test_missing_in_requirements(self):
        req = {"pydantic": ">=2.0.0"}
        py = {"pydantic": ">=2.0.0", "pytest": ">=8.0.0"}
        findings = _check_pair(req, py, "label")
        assert len(findings) == 1
        assert "缺失" in findings[0]
        assert "pytest" in findings[0]

    def test_extra_in_requirements(self):
        req = {"pydantic": ">=2.0.0", "orphan": ">=1.0"}
        py = {"pydantic": ">=2.0.0"}
        findings = _check_pair(req, py, "label")
        assert len(findings) == 1
        assert "缺失" in findings[0] or "多余" in findings[0]
        assert "orphan" in findings[0]

    def test_version_constraint_mismatch(self):
        req = {"pydantic": ">=2.0.0"}
        py = {"pydantic": ">=2.0.0,<3.0.0"}
        findings = _check_pair(req, py, "label")
        assert len(findings) == 1
        assert "版本约束不一致" in findings[0]
        assert "pydantic" in findings[0]


# ── 单元测试：触发条件 ──

class TestTrigger:
    """触发条件：pyproject.toml 或 requirements*.txt 变更才触发。"""

    def test_trigger_on_pyproject(self):
        assert _trigger(["pyproject.toml"]) is True

    def test_trigger_on_requirements_main(self):
        assert _trigger(["requirements.txt"]) is True

    def test_trigger_on_requirements_dev(self):
        assert _trigger(["requirements-dev.txt"]) is True

    def test_trigger_on_requirements_demo(self):
        assert _trigger(["requirements-demo.txt"]) is True

    def test_no_trigger_on_unrelated_file(self):
        assert _trigger(["src/zephyr/core.py"]) is False

    def test_no_trigger_on_empty(self):
        assert _trigger([]) is False

    def test_trigger_mixed_files(self):
        assert _trigger(["src/zephyr/core.py", "requirements.txt"]) is True

    def test_trigger_with_path_prefix(self):
        """触发条件匹配相对路径（非仅纯文件名）。"""
        # 环境无关化：硬编码主仓盘符路径在 worktree 下 relpath 出界——改动态拼当前仓根
        assert _trigger([str(_PROJECT_ROOT / "requirements.txt").replace("\\", "/")]) is True


# ── 集成测试：reconciler 端到端 ──

class TestReconcilerEndToEnd:
    """reconciler 工厂 + _reconcile 端到端（用 tmp_path 构造完整场景）。"""

    def test_no_drift_returns_auto_committed(self, tmp_path):
        """三组完全对齐 → auto_committed。"""
        _write_pyproject(
            tmp_path,
            main_deps=["pydantic>=2.0.0", "pytest>=8.0.0"],
            dev_deps=["ruff>=0.5.0"],
            demo_deps=["streamlit>=1.30.0"],
        )
        _write_requirements(tmp_path, "requirements.txt", [
            "pydantic>=2.0.0",
            "pytest>=8.0.0",
        ])
        _write_requirements(tmp_path, "requirements-dev.txt", [
            "-r requirements.txt",
            "ruff>=0.5.0",
        ])
        _write_requirements(tmp_path, "requirements-demo.txt", [
            "-r requirements.txt",
            "streamlit>=1.30.0",
        ])

        spec = make_requirements_version_sync_reconciler(tmp_path)
        result = spec.reconcile([str(tmp_path / "pyproject.toml")], "test-session")

        assert result.action == "auto_committed"
        assert "一致" in result.detail

    def test_missing_dependency_warns(self, tmp_path):
        """requirements.txt 缺失 pyproject 中的依赖 → warn。"""
        _write_pyproject(
            tmp_path,
            main_deps=["pydantic>=2.0.0", "pytest>=8.0.0"],
            dev_deps=[],
            demo_deps=[],
        )
        # requirements.txt 缺 pytest
        _write_requirements(tmp_path, "requirements.txt", ["pydantic>=2.0.0"])
        _write_requirements(tmp_path, "requirements-dev.txt", ["-r requirements.txt"])
        _write_requirements(tmp_path, "requirements-demo.txt", ["-r requirements.txt"])

        spec = make_requirements_version_sync_reconciler(tmp_path)
        result = spec.reconcile([str(tmp_path / "requirements.txt")], "test-session")

        assert result.action == "warn"
        assert "缺失" in result.detail
        assert "pytest" in result.detail

    def test_extra_dependency_warns(self, tmp_path):
        """requirements.txt 有 pyproject 中没有的依赖 → warn。"""
        _write_pyproject(
            tmp_path,
            main_deps=["pydantic>=2.0.0"],
            dev_deps=[],
            demo_deps=[],
        )
        # requirements.txt 多了 orphan
        _write_requirements(tmp_path, "requirements.txt", [
            "pydantic>=2.0.0",
            "orphan>=1.0.0",
        ])
        _write_requirements(tmp_path, "requirements-dev.txt", ["-r requirements.txt"])
        _write_requirements(tmp_path, "requirements-demo.txt", ["-r requirements.txt"])

        spec = make_requirements_version_sync_reconciler(tmp_path)
        result = spec.reconcile([str(tmp_path / "requirements.txt")], "test-session")

        assert result.action == "warn"
        assert "orphan" in result.detail

    def test_version_constraint_mismatch_warns(self, tmp_path):
        """版本约束不一致 → warn。"""
        _write_pyproject(
            tmp_path,
            main_deps=["pydantic>=2.0.0,<3.0.0"],
            dev_deps=[],
            demo_deps=[],
        )
        # requirements.txt 版本约束不同
        _write_requirements(tmp_path, "requirements.txt", ["pydantic>=2.0.0"])
        _write_requirements(tmp_path, "requirements-dev.txt", ["-r requirements.txt"])
        _write_requirements(tmp_path, "requirements-demo.txt", ["-r requirements.txt"])

        spec = make_requirements_version_sync_reconciler(tmp_path)
        result = spec.reconcile([str(tmp_path / "requirements.txt")], "test-session")

        assert result.action == "warn"
        assert "版本约束不一致" in result.detail

    def test_dev_extras_drift_warns(self, tmp_path):
        """dev extras 漂移 → warn。"""
        _write_pyproject(
            tmp_path,
            main_deps=["pydantic>=2.0.0"],
            dev_deps=["ruff>=0.5.0", "mypy>=1.10.0"],
            demo_deps=[],
        )
        _write_requirements(tmp_path, "requirements.txt", ["pydantic>=2.0.0"])
        # requirements-dev.txt 缺 mypy
        _write_requirements(tmp_path, "requirements-dev.txt", [
            "-r requirements.txt",
            "ruff>=0.5.0",
        ])
        _write_requirements(tmp_path, "requirements-demo.txt", ["-r requirements.txt"])

        spec = make_requirements_version_sync_reconciler(tmp_path)
        result = spec.reconcile([str(tmp_path / "requirements-dev.txt")], "test-session")

        assert result.action == "warn"
        assert "mypy" in result.detail

    def test_pyproject_read_failure_warns(self, tmp_path):
        """pyproject.toml 缺失 → warn 降级（不阻断）。"""
        # 不写 pyproject.toml，只写 requirements
        _write_requirements(tmp_path, "requirements.txt", ["pydantic>=2.0.0"])
        _write_requirements(tmp_path, "requirements-dev.txt", ["-r requirements.txt"])
        _write_requirements(tmp_path, "requirements-demo.txt", ["-r requirements.txt"])

        spec = make_requirements_version_sync_reconciler(tmp_path)
        result = spec.reconcile([str(tmp_path / "pyproject.toml")], "test-session")

        assert result.action == "warn"
        assert "读取失败" in result.detail or "pyproject" in result.detail


# ── 工厂函数测试 ──

class TestFactory:
    """make_requirements_version_sync_reconciler 工厂函数。"""

    def test_returns_spec_with_gate_id(self, tmp_path):
        spec = make_requirements_version_sync_reconciler(tmp_path)
        assert spec.gate_id == "GATE-REQUIREMENTS-VERSION-SYNC"

    def test_returns_spec_with_trigger(self, tmp_path):
        spec = make_requirements_version_sync_reconciler(tmp_path)
        assert callable(spec.trigger)

    def test_returns_spec_with_reconcile(self, tmp_path):
        spec = make_requirements_version_sync_reconciler(tmp_path)
        assert callable(spec.reconcile)

    def test_priority_is_int(self, tmp_path):
        spec = make_requirements_version_sync_reconciler(tmp_path)
        assert isinstance(spec.priority, int)
        assert spec.priority > 0
