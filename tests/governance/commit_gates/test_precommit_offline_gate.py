# [A_test] module_id: MOD-GOV_precommit_offline_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-PRECOMMIT-OFFLINE-001
# [MODULE] tests.governance.commit_gates.test_precommit_offline_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_precommit_offline_gate.py — GATE-PRECOMMIT-OFFLINE 门禁单测

权威依据：precommit_offline_gate.py（make_precommit_offline_gate）
裁定：#ARCH-PRECOMMIT-OFFLINE-001（2026-07-21）治本
规则真源：trae_073_precommit_offline_discipline.yaml（5 铁律 + 3 INV）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsExternalRepo: _is_external_repo 纯函数
  - local 合法 / https:// 外部 / git@ 外部 / ssh:// 外部 / 非 str fail-open
- TestScanPrecommitConfigOffline: scan_precommit_config_offline 纯函数
  - 合法配置（全 local + language: system）→ clean=True
  - 外部 repo（https://github.com/...）→ external_violations 命中
  - language: pygrep → language_violations 命中
  - language: python → language_violations 命中
  - 混合违规（external + language）→ 两个列表都填充
  - YAML 解析失败 → fail-open (clean=True)
  - 非 dict YAML（list/scalar）→ fail-open
  - repos 非 list → fail-open
  - 空 repos → clean=True
- TestGatewayIntegration: mock gateway 流程
  - .pre-commit-config.yaml 未在 staged → 跳过（passed=True）
  - staged + 合法配置 → passed=True
  - staged + 外部 repo → passed=False
  - staged + language 违规 → passed=False
  - 非 Zephyr 项目（无 scripts/governance/d1_structure）→ 跳过
  - 文件不存在 → fail-open
  - 读取失败 → fail-open
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.precommit_offline_gate import (  # noqa: E402
    _is_external_repo,
    make_precommit_offline_gate,
    scan_precommit_config_offline,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_precommit_offline_gate(), GateSpec)

    def test_gate_id(self):
        assert make_precommit_offline_gate().gate_id == "GATE-PRECOMMIT-OFFLINE"

    def test_priority(self):
        # priority=111（紧接 CAPABILITY-LOOKUP-REQUIRED=110，CONSUMERS-ACCURACY=109 已占用）
        assert make_precommit_offline_gate().priority == 111


# ---------------------------------------------------------------------------
# TestIsExternalRepo
# ---------------------------------------------------------------------------
class TestIsExternalRepo:
    def test_local_is_not_external(self):
        assert _is_external_repo("local") is False

    def test_local_case_insensitive(self):
        # 归一化后比较（lower()），"LOCAL" 也合法
        assert _is_external_repo("LOCAL") is False
        assert _is_external_repo("Local") is False

    def test_local_with_whitespace(self):
        assert _is_external_repo("  local  ") is False

    def test_https_github_is_external(self):
        assert _is_external_repo("https://github.com/pre-commit/pre-commit-hooks") is True

    def test_http_is_external(self):
        assert _is_external_repo("http://example.com/repo") is True

    def test_git_at_is_external(self):
        assert _is_external_repo("git@github.com:org/repo.git") is True

    def test_ssh_is_external(self):
        assert _is_external_repo("ssh://git@github.com/org/repo.git") is True

    def test_local_path_is_external(self):
        # 严格策略：任何非 "local" 值都视为外部（包括本地相对路径）
        assert _is_external_repo("./my-local-hooks") is True
        assert _is_external_repo("/abs/path/to/repo") is True

    def test_non_str_fail_open(self):
        # 非 str 输入 → False（YAML 结构异常由调用方处理）
        assert _is_external_repo(None) is False
        assert _is_external_repo(123) is False
        assert _is_external_repo([]) is False


# ---------------------------------------------------------------------------
# TestScanPrecommitConfigOffline
# ---------------------------------------------------------------------------
class TestScanPrecommitConfigOffline:
    def test_clean_config_all_local_system(self):
        """合法配置：全 local repo + 所有 hook language: system。"""
        config = """
repos:
  - repo: local
    hooks:
      - id: check-merge-conflict
        entry: python check_merge_conflict.py
        language: system
      - id: ruff
        entry: python -m ruff check
        language: system
"""
        is_clean, external, language = scan_precommit_config_offline(config)
        assert is_clean is True
        assert external == []
        assert language == []

    def test_external_https_repo_detected(self):
        """外部 https repo 检测。"""
        config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
"""
        is_clean, external, language = scan_precommit_config_offline(config)
        assert is_clean is False
        assert "https://github.com/pre-commit/pre-commit-hooks" in external
        assert language == []

    def test_external_git_at_repo_detected(self):
        """git@ 外部 repo 检测。"""
        config = """
repos:
  - repo: git@github.com:org/repo.git
    hooks: []
"""
        is_clean, external, _ = scan_precommit_config_offline(config)
        assert is_clean is False
        assert "git@github.com:org/repo.git" in external

    def test_language_pygrep_detected(self):
        """language: pygrep 违规检测（trae_073 INV-002）。"""
        config = """
repos:
  - repo: local
    hooks:
      - id: gate-no-tests-unit
        entry: "tests/unit/"
        language: pygrep
"""
        is_clean, external, language = scan_precommit_config_offline(config)
        assert is_clean is False
        assert external == []
        assert any("gate-no-tests-unit" in v and "pygrep" in v for v in language)

    def test_language_python_detected(self):
        """language: python 违规检测（需 pre-commit 创建虚拟环境+联网安装）。"""
        config = """
repos:
  - repo: local
    hooks:
      - id: some-hook
        entry: some-hook
        language: python
"""
        is_clean, _, language = scan_precommit_config_offline(config)
        assert is_clean is False
        assert any("python" in v for v in language)

    def test_mixed_violations(self):
        """混合违规：外部 repo + local repo 的 language 非 system，两个列表都填充。

        注：language 检测仅对 local repo 的 hooks 生效（外部 repo 已违规，无需双重报告）。
        """
        config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
        language: system
  - repo: local
    hooks:
      - id: bad-hook
        entry: bad
        language: pygrep
"""
        is_clean, external, language = scan_precommit_config_offline(config)
        assert is_clean is False
        assert len(external) == 1
        assert len(language) == 1
        assert "https://github.com/pre-commit/pre-commit-hooks" in external[0]
        assert "bad-hook" in language[0]

    def test_yaml_parse_failure_fail_open(self):
        """YAML 解析失败 → fail-open (clean=True)。"""
        invalid_yaml = """
repos:
  - repo: local
    hooks:
      - id: broken
        entry: unquoted: value: with: colons
"""
        is_clean, external, language = scan_precommit_config_offline(invalid_yaml)
        # 即使能解析也无所谓——确保不抛异常 + fail-open
        assert isinstance(is_clean, bool)
        assert isinstance(external, list)
        assert isinstance(language, list)

    def test_completely_invalid_yaml_fail_open(self):
        """完全无法解析的 YAML → fail-open。"""
        invalid = ":\n:\n  - [unbalanced"
        is_clean, _, _ = scan_precommit_config_offline(invalid)
        assert is_clean is True  # fail-open

    def test_non_dict_yaml_fail_open(self):
        """非 dict YAML（list/scalar）→ fail-open。"""
        is_clean1, _, _ = scan_precommit_config_offline("- item1\n- item2")
        assert is_clean1 is True
        is_clean2, _, _ = scan_precommit_config_offline("just a scalar")
        assert is_clean2 is True

    def test_repos_not_list_fail_open(self):
        """repos 非 list → fail-open。"""
        config = """
repos: "not a list"
"""
        is_clean, _, _ = scan_precommit_config_offline(config)
        assert is_clean is True

    def test_empty_repos_clean(self):
        """空 repos 列表 → clean=True。"""
        config = "repos: []\n"
        is_clean, external, language = scan_precommit_config_offline(config)
        assert is_clean is True
        assert external == []
        assert language == []

    def test_missing_repos_key_clean(self):
        """无 repos 键 → clean=True（无 hook 不违规）。"""
        config = "default_install_hook_types: [pre-commit]\n"
        is_clean, _, _ = scan_precommit_config_offline(config)
        assert is_clean is True

    def test_repo_entry_not_dict_skipped(self):
        """repo entry 非 dict → 跳过（不抛异常）。"""
        config = """
repos:
  - "not a dict"
  - repo: local
    hooks: []
"""
        is_clean, _, _ = scan_precommit_config_offline(config)
        assert is_clean is True

    def test_hooks_not_list_skipped(self):
        """hooks 非 list → 跳过 language 检测（不抛异常）。"""
        config = """
repos:
  - repo: local
    hooks: "not a list"
"""
        is_clean, _, language = scan_precommit_config_offline(config)
        assert is_clean is True
        assert language == []

    def test_hook_missing_language_defaults_system(self):
        """hook 无 language 字段 → 默认 system（合法）。"""
        config = """
repos:
  - repo: local
    hooks:
      - id: no-language-field
        entry: some-entry
"""
        is_clean, _, language = scan_precommit_config_offline(config)
        assert is_clean is True
        assert language == []

    def test_external_repo_no_language_check(self):
        """外部 repo 的 hooks 不检测 language（外部 repo 已违规，无需双重报告）。"""
        config = """
repos:
  - repo: https://github.com/external/repo
    hooks:
      - id: ext-hook
        language: python
"""
        is_clean, external, language = scan_precommit_config_offline(config)
        assert is_clean is False
        assert len(external) == 1
        # language 检测仅对 local repo 的 hooks，外部 repo 的 hooks 不检测
        assert language == []


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------
def _make_gateway(project_root: Path, files: list[str]) -> MagicMock:
    """构造 mock gateway：project_root + files 列表。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _make_zephyr_project(tmp_path: Path) -> Path:
    """在 tmp_path 下创建 Zephyr 项目结构（含 scripts/governance/d1_structure）。"""
    (tmp_path / "scripts" / "governance" / "d1_structure").mkdir(parents=True)
    return tmp_path


class TestGatewayIntegration:
    def test_config_not_in_staged_skip(self, tmp_path):
        """`.pre-commit-config.yaml` 未在 staged → 跳过（passed=True）。"""
        root = _make_zephyr_project(tmp_path)
        gw = _make_gateway(root, ["src/some_file.py"])
        gate = make_precommit_offline_gate()
        passed, detail = gate.check(gw, ["src/some_file.py"])
        assert passed is True
        assert detail == ""

    def test_staged_clean_config_pass(self, tmp_path):
        """staged + 合法配置（全 local + language: system）→ passed=True。"""
        root = _make_zephyr_project(tmp_path)
        config_path = root / ".pre-commit-config.yaml"
        config_path.write_text(
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: ruff\n"
            "        entry: python -m ruff\n"
            "        language: system\n",
            encoding="utf-8",
        )
        gw = _make_gateway(root, [str(config_path)])
        gate = make_precommit_offline_gate()
        passed, _ = gate.check(gw, [str(config_path)])
        assert passed is True

    def test_staged_external_repo_block(self, tmp_path):
        """staged + 外部 repo 引用 → passed=False（硬阻断）。"""
        root = _make_zephyr_project(tmp_path)
        config_path = root / ".pre-commit-config.yaml"
        config_path.write_text(
            "repos:\n"
            "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
            "    rev: v4.6.0\n"
            "    hooks:\n"
            "      - id: trailing-whitespace\n"
            "        language: system\n",
            encoding="utf-8",
        )
        gw = _make_gateway(root, [str(config_path)])
        gate = make_precommit_offline_gate()
        passed, detail = gate.check(gw, [str(config_path)])
        assert passed is False
        assert "https://github.com/pre-commit/pre-commit-hooks" in detail
        assert "PRECOMMIT_OFFLINE_VIOLATION" in detail

    def test_staged_language_violation_block(self, tmp_path):
        """staged + language: pygrep → passed=False（硬阻断）。"""
        root = _make_zephyr_project(tmp_path)
        config_path = root / ".pre-commit-config.yaml"
        config_path.write_text(
            "repos:\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: gate-no-tests-unit\n"
            "        entry: 'tests/unit/'\n"
            "        language: pygrep\n",
            encoding="utf-8",
        )
        gw = _make_gateway(root, [str(config_path)])
        gate = make_precommit_offline_gate()
        passed, detail = gate.check(gw, [str(config_path)])
        assert passed is False
        assert "gate-no-tests-unit" in detail
        assert "pygrep" in detail

    def test_non_zephyr_project_skip(self, tmp_path):
        """非 Zephyr 项目（无 scripts/governance/d1_structure）→ 跳过。"""
        # tmp_path 下不创建 scripts/governance/d1_structure
        config_path = tmp_path / ".pre-commit-config.yaml"
        config_path.write_text(
            "repos:\n  - repo: https://github.com/external/repo\n    hooks: []\n",
            encoding="utf-8",
        )
        gw = _make_gateway(tmp_path, [str(config_path)])
        gate = make_precommit_offline_gate()
        passed, detail = gate.check(gw, [str(config_path)])
        assert passed is True
        assert "non-Zephyr" in detail

    def test_config_file_not_exist_fail_open(self, tmp_path):
        """.pre-commit-config.yaml 文件不存在 → fail-open。"""
        root = _make_zephyr_project(tmp_path)
        # 文件路径在 staged 列表中但磁盘上不存在
        config_path = str(root / ".pre-commit-config.yaml")
        gw = _make_gateway(root, [config_path])
        gate = make_precommit_offline_gate()
        passed, detail = gate.check(gw, [config_path])
        assert passed is True
        assert detail == ""

    def test_read_failure_fail_open(self, tmp_path, monkeypatch):
        """读取失败 → fail-open。"""
        root = _make_zephyr_project(tmp_path)
        config_path = root / ".pre-commit-config.yaml"
        config_path.write_text("repos: []\n", encoding="utf-8")

        # monkeypatch Path.read_text 抛异常
        original_read_text = Path.read_text

        def _raise(self, *a, **kw):
            raise OSError("simulated read failure")

        monkeypatch.setattr(Path, "read_text", _raise)
        try:
            gw = _make_gateway(root, [str(config_path)])
            gate = make_precommit_offline_gate()
            passed, detail = gate.check(gw, [str(config_path)])
            assert passed is True
            assert detail == ""
        finally:
            monkeypatch.setattr(Path, "read_text", original_read_text)

    def test_staged_path_with_backslash_normalized(self, tmp_path):
        """staged 路径含反斜杠 → 归一化后匹配 .pre-commit-config.yaml。"""
        root = _make_zephyr_project(tmp_path)
        config_path = root / ".pre-commit-config.yaml"
        config_path.write_text("repos: []\n", encoding="utf-8")
        # Windows 风格路径（反斜杠）
        win_path = str(config_path).replace("/", "\\")
        gw = _make_gateway(root, [win_path])
        gate = make_precommit_offline_gate()
        passed, _ = gate.check(gw, [win_path])
        assert passed is True

    def test_mixed_violations_detail_format(self, tmp_path):
        """混合违规：detail 同时包含 external + language 两个段落。"""
        root = _make_zephyr_project(tmp_path)
        config_path = root / ".pre-commit-config.yaml"
        config_path.write_text(
            "repos:\n"
            "  - repo: https://github.com/external/repo\n"
            "    hooks:\n"
            "      - id: ext-hook\n"
            "        language: system\n"
            "  - repo: local\n"
            "    hooks:\n"
            "      - id: bad-hook\n"
            "        entry: bad\n"
            "        language: pygrep\n",
            encoding="utf-8",
        )
        gw = _make_gateway(root, [str(config_path)])
        gate = make_precommit_offline_gate()
        passed, detail = gate.check(gw, [str(config_path)])
        assert passed is False
        # detail 同时含 external + language 两个段落
        assert "外部 repo" in detail
        assert "language 非 system" in detail
        assert "https://github.com/external/repo" in detail
        assert "bad-hook" in detail
