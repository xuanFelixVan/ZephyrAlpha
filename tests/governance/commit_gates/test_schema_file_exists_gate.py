# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-SSOT-REFERENCE-INTEGRITY-001
# [MODULE] tests.governance.commit_gates.test_schema_file_exists_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# -*- coding: utf-8 -*-
"""test_schema_file_exists_gate.py — SCHEMA-FILE-EXISTS 门禁单测

权威依据：schema_file_exists_gate.py（make_schema_file_exists_gate）

裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 1：SSoT 存在性强制。

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCheckSchemaFilesExist: _check_schema_files_exist 直接调用
  - YAML 未 staged → [] (fail-open)
  - YAML 解析错误 → [] (fail-open)
  - YAML 顶层非 list → [] (fail-open)
  - 全部 schema_file 存在 → []
  - 单个 schema_file 不存在 → 违规消息
  - schema_file=null → 跳过
  - schema_file 缺失字段 → 跳过
  - 多违规 → 全部返回
- TestCheckClosure: _check 闭包行为
  - files 不含 YAML → pass（提前返回）
  - files 含 YAML 全部 schema_file 存在 → pass
  - files 含 YAML 含悬空 schema_file → block
  - YAML 解析错误 → fail-open pass
  - git show 不可达 → fail-open pass
  - Windows 反斜杠归一化
  - 多违规截断到 30 条 + (...+N more)
  - 返回 tuple[bool, str]

测试隔离：MagicMock 模拟 gateway.run_git；monkeypatch os.path.exists 模拟文件存在性。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file  # noqa: E402
from zephyr.gov_enforcement.commit_gates.schema_file_exists_gate import (  # noqa: E402
    _check_schema_files_exist,
    make_schema_file_exists_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# business_data_categories.yaml 相对路径（与 schema_file_exists_gate.py 中 _YAML_REL 一致）
_YAML_REL = "docs/03_modules/_cross_layer/database/business_data_categories.yaml"


class _MockResult:
    """模拟 subprocess.run 返回值。"""

    def __init__(self, returncode: int = 0, stdout: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout


def _make_mock_gateway(
    yaml_content: str | None,
    project_root: str = "/test",
    git_show_rc: int = 0,
) -> MagicMock:
    """构造 mock gateway，模拟 _run_git 返回 staged YAML 内容。

    Args:
        yaml_content: YAML 文件内容；None 表示 git show 失败（returncode=1）。
        project_root: 项目根路径。
        git_show_rc: git show returncode。
    """

    def _run_git(cmd):
        if "show" in cmd and ":" + _YAML_REL in cmd:
            return _MockResult(
                git_show_rc,
                yaml_content if yaml_content is not None else "",
            )
        return _MockResult(1, "")

    gw = MagicMock()
    gw.run_git = _run_git
    gw.project_root = Path(project_root)
    return gw


# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        gate = make_schema_file_exists_gate()
        assert gate.gate_id == "SCHEMA-FILE-EXISTS"

    def test_priority(self) -> None:
        gate = make_schema_file_exists_gate()
        assert gate.priority == 121

    def test_is_gate_spec(self) -> None:
        gate = make_schema_file_exists_gate()
        assert isinstance(gate, GateSpec)

    def test_check_callable(self) -> None:
        gate = make_schema_file_exists_gate()
        assert callable(gate.check)


# ============================================================================
# TestCheckSchemaFilesExist
# ============================================================================


class TestCheckSchemaFilesExist:
    """_check_schema_files_exist 直接调用。"""

    def test_yaml_not_staged_returns_empty(self, tmp_path: Path) -> None:
        """YAML 未 staged（git show rc=1）→ [] (fail-open)。"""
        gw = _make_mock_gateway(yaml_content=None, git_show_rc=1)
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_yaml_parse_error_returns_empty(self, tmp_path: Path) -> None:
        """YAML 解析失败 → [] (fail-open)。"""
        gw = _make_mock_gateway(yaml_content="invalid: yaml: [")
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_non_list_yaml_returns_empty(self, tmp_path: Path) -> None:
        """YAML 顶层非 list → [] (fail-open)。"""
        gw = _make_mock_gateway(yaml_content="foo: bar\n")
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_all_schema_files_exist_returns_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """所有 schema_file 存在 → [] (通过)。"""
        yaml_content = (
            "- category_id: cat_a\n"
            "  schema_file: schemas/categories/market_tick.py\n"
            "- category_id: cat_b\n"
            "  schema_file: schemas/categories/market_index.py\n"
        )
        gw = _make_mock_gateway(yaml_content=yaml_content)
        # monkeypatch os.path.exists 全返回 True
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: True,
        )
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_broken_schema_file_returns_violation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """单个 schema_file 不存在 → 违规消息。"""
        # 在 tmp_path 下创建 market_tick.py（存在的），nonexistent.py 不创建
        (tmp_path / "schemas" / "categories").mkdir(parents=True, exist_ok=True)
        (tmp_path / "schemas" / "categories" / "market_tick.py").touch()

        yaml_content = (
            "- category_id: market_tick\n"
            "  schema_file: schemas/categories/market_tick.py\n"
            "- category_id: broken_cat\n"
            "  schema_file: schemas/categories/nonexistent.py\n"
        )
        gw = _make_mock_gateway(yaml_content=yaml_content)
        # 真实 os.path.exists（不 mock，依赖 tmp_path 下的真实文件）
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert len(result) == 1
        assert "broken_cat" in result[0]
        assert "nonexistent.py" in result[0]
        assert "声明层→存在层断裂" in result[0]

    def test_null_schema_file_skipped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """schema_file=null → 跳过。"""
        yaml_content = "- category_id: null_cat\n  schema_file: null\n"
        gw = _make_mock_gateway(yaml_content=yaml_content)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: True,  # 即使存在也不该被调用
        )
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_missing_schema_file_field_skipped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """缺 schema_file 字段 → 跳过。"""
        yaml_content = "- category_id: no_field_cat\n  description: some metadata table\n"
        gw = _make_mock_gateway(yaml_content=yaml_content)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: True,
        )
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_empty_schema_file_skipped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """schema_file='' → 跳过（falsy）。"""
        yaml_content = "- category_id: empty_cat\n  schema_file: ''\n"
        gw = _make_mock_gateway(yaml_content=yaml_content)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: True,
        )
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert result == []

    def test_multiple_violations_all_returned(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """多违规全部返回。"""
        yaml_lines = []
        for i in range(3):
            yaml_lines.append(f"- category_id: broken_cat_{i}\n  schema_file: schemas/categories/broken_{i}.py\n")
        yaml_content = "".join(yaml_lines)
        gw = _make_mock_gateway(yaml_content=yaml_content)
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: False,
        )
        result = _check_schema_files_exist(gw, str(tmp_path))
        assert len(result) == 3
        for i in range(3):
            assert f"broken_cat_{i}" in result[i]
            assert f"broken_{i}.py" in result[i]


# ============================================================================
# TestCheckClosure
# ============================================================================


class TestCheckClosure:
    """_check 闭包行为测试。"""

    def test_yaml_not_in_files_passes(self, tmp_path: Path) -> None:
        """files 不含 YAML → pass（提前返回）。"""
        gw = _make_mock_gateway(yaml_content=None)
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=["src/zephyr/foo.py"])
        assert passed is True
        assert detail == ""

    def test_all_schema_files_exist_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """files 含 YAML，所有 schema_file 存在 → pass。"""
        yaml_content = "- category_id: cat_a\n  schema_file: schemas/categories/market_tick.py\n"
        gw = _make_mock_gateway(yaml_content=yaml_content, project_root=str(tmp_path))
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: True,
        )
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=[_YAML_REL])
        assert passed is True
        assert detail == ""

    def test_broken_schema_file_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """files 含 YAML 含悬空 schema_file → block。"""
        yaml_content = "- category_id: broken_cat\n  schema_file: schemas/categories/nonexistent.py\n"
        gw = _make_mock_gateway(yaml_content=yaml_content, project_root=str(tmp_path))
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: False,
        )
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=[_YAML_REL])
        assert passed is False
        assert "SCHEMA-FILE-EXISTS" in detail
        assert "broken_cat" in detail
        assert "nonexistent.py" in detail
        assert "ARCH-SSOT-REFERENCE-INTEGRITY-001" in detail

    def test_yaml_parse_error_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """YAML 解析失败 → fail-open pass。"""
        gw = _make_mock_gateway(
            yaml_content="invalid: yaml: [",
            project_root=str(tmp_path),
        )
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=[_YAML_REL])
        assert passed is True
        assert detail == ""

    def test_git_show_unreachable_fail_open(self, tmp_path: Path) -> None:
        """git show 不可达 → fail-open pass。"""
        gw = _make_mock_gateway(
            yaml_content=None,  # 模拟 git show 失败
            project_root=str(tmp_path),
            git_show_rc=1,
        )
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=[_YAML_REL])
        assert passed is True
        assert detail == ""

    def test_windows_path_separator_normalized(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Windows 反斜杠路径归一化（files 含反斜杠）。"""
        yaml_content = "- category_id: cat_a\n  schema_file: schemas/categories/market_tick.py\n"
        gw = _make_mock_gateway(yaml_content=yaml_content, project_root=str(tmp_path))
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: True,
        )
        gate = make_schema_file_exists_gate()
        # Windows 反斜杠
        win_path = _YAML_REL.replace("/", "\\")
        passed, detail = gate.check(gw, files=[win_path])
        assert passed is True

    def test_multiple_violations_truncated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """多于 30 条违规 → 截断到 30 + (...+N more)。"""
        yaml_lines = []
        for i in range(35):
            yaml_lines.append(f"- category_id: cat_{i}\n  schema_file: schemas/categories/broken_{i}.py\n")
        yaml_content = "".join(yaml_lines)
        gw = _make_mock_gateway(yaml_content=yaml_content, project_root=str(tmp_path))
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: False,
        )
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=[_YAML_REL])
        assert passed is False
        assert "(+5 more)" in detail  # 35 - 30 = 5

    def test_returns_tuple(self, tmp_path: Path) -> None:
        """check 返回 tuple[bool, str]。"""
        gw = _make_mock_gateway(yaml_content=None, project_root=str(tmp_path))
        gate = make_schema_file_exists_gate()
        result = gate.check(gw, files=["unrelated.py"])
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)


# ============================================================================
# TestIntegrationWithRealYaml
# ============================================================================


class TestIntegrationWithRealYaml:
    """集成测试：使用真实 business_data_categories.yaml 验证（已知 10/10 valid）。"""

    def test_real_yaml_all_valid(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """真实 business_data_categories.yaml 所有 schema_file 都存在 → pass。

        前置：项目根 d:\\ZephyrAlpha 包含完整 schemas/ 目录。
        """
        real_root = Path(__file__).resolve().parents[3]
        real_yaml_path = real_root / _YAML_REL

        if not real_yaml_path.exists():
            pytest.skip(f"real YAML not found: {real_yaml_path}")

        yaml_content = real_yaml_path.read_text(encoding="utf-8")
        gw = _make_mock_gateway(
            yaml_content=yaml_content,
            project_root=str(real_root),
        )
        # 真实 os.path.exists（不 mock，用 lambda 包装 Path.exists）
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.schema_file_exists_gate.os.path.exists",
            lambda p: Path(p).exists(),
        )
        gate = make_schema_file_exists_gate()
        passed, detail = gate.check(gw, files=[_YAML_REL])
        assert passed is True, f"real YAML has broken refs: {detail}"
