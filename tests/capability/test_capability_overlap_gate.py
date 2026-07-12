# [A_test] module_id: SRC-TST-2032 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-capability_overlap_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §capability-overlap-gate
# [MODULE] tests.test_capability_overlap_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_capability_overlap_gate.py — CAPABILITY-OVERLAP warn-only gate 单测（P2-2，2026-06-30）

权威依据：capability_overlap_gate.py（make_capability_overlap_gate）

测试组：
- TestGateSpecFields: gate_id / priority 字段正确
- TestNoStagedNewFiles: git diff 无新增文件 → 放行
- TestNoPyNoYaml: 新增文件但非 .py 非 _registry/.yaml → 放行
- TestPyOverlap: .py 文件名与 capability alias token 重叠 → warn-only 放行 + warning
- TestPyNoOverlap: .py 文件名无重叠 → 放行无 warning
- TestTestsDirExcluded: tests/ 下 .py 文件不检测
- TestYamlSecondSource: _registry/ 下新建 .yaml 与同目录现有 .yaml token ≥2 重叠 → warning
- TestFailLoudGitDiff: git diff 失败 → fail-loud（passed=True 保留 warn-only 契约 + logger.warning 告警检测器失效）
- TestFailLoudYamlMissing: REGISTRY_YAML 不存在 → fail-loud
- TestFailLoudYamlParse: YAML 解析失败 → fail-loud
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.governance.commit_gates.capability_overlap_gate import (
    make_capability_overlap_gate,
)

_LOGGER_NAME = "zephyr.governance.commit_gates.capability_overlap_gate"

# 最小 capability registry fixture：gate 只读 capability_id + aliases
_MINIMAL_REGISTRY_YAML = """\
capabilities:
  - capability_id: session_handoff_continuity
    aliases:
      - session_handoff
      - handoff
    description: minimal test fixture
"""


def _make_git_result(stdout: str = "", returncode: int = 0) -> MagicMock:
    """构造 mock git diff 结果对象。"""
    r = MagicMock()
    r.returncode = returncode
    r.stdout = stdout
    return r


def _make_gateway(
    stdout: str = "",
    returncode: int = 0,
    exc: Exception | None = None,
) -> MagicMock:
    """构造 mock gateway，模拟 _run_git（git diff --cached --name-only --diff-filter=A）。

    Args:
        stdout: git diff stdout（每行一个文件相对路径）。
        returncode: git diff returncode（非 0 → fail-open）。
        exc: 若非 None，_run_git 抛此异常（测试安全降级）。
    """
    gw = MagicMock()
    if exc is not None:
        gw._run_git.side_effect = exc
    else:
        gw._run_git.return_value = _make_git_result(stdout, returncode)
    return gw


def _setup_registry(tmp_path, monkeypatch, content: str = _MINIMAL_REGISTRY_YAML):
    """monkeypatch REGISTRY_YAML 指向 tmp_path 下临时 YAML（避免触碰真源）。"""
    registry = tmp_path / "registry.yaml"
    registry.write_text(content, encoding="utf-8")
    monkeypatch.setattr(
        "zephyr.governance.capability_lookup.REGISTRY_YAML",
        registry,
    )


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        spec = make_capability_overlap_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "CAPABILITY-OVERLAP"
        assert spec.priority == 200


class TestNoStagedNewFiles:
    """git diff 无新增文件 → 放行。"""

    def test_empty_staged(self, tmp_path, monkeypatch):
        _setup_registry(tmp_path, monkeypatch)
        gw = _make_gateway(stdout="")
        gate = make_capability_overlap_gate()
        passed, detail = gate.check(gw, [], session_id="s1")
        assert passed is True
        assert detail == ""


class TestNoPyNoYaml:
    """新增文件但非 .py 非 _registry/.yaml → 放行。"""

    def test_only_md_files(self, tmp_path, monkeypatch):
        _setup_registry(tmp_path, monkeypatch)
        gw = _make_gateway(stdout="docs/foo.md")
        gate = make_capability_overlap_gate()
        passed, detail = gate.check(gw, ["docs/foo.md"], session_id="s1")
        assert passed is True
        assert detail == ""


class TestPyOverlap:
    """.py 文件名与 capability alias token 重叠 → warn-only 放行 + warning。"""

    def test_py_overlap_warns(self, tmp_path, monkeypatch, caplog):
        _setup_registry(tmp_path, monkeypatch)
        # session_handoff_loader → tokens {session, handoff, loader}
        # capability session_handoff_continuity → tokens {session, handoff, continuity}
        # overlap {session, handoff} → warning
        new_file = "src/zephyr/foo/session_handoff_loader.py"
        gw = _make_gateway(stdout=new_file)
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(gw, [new_file], session_id="s1")
        assert passed is True  # warn-only 永不阻断
        assert detail == ""
        assert any("session_handoff_loader" in r.message for r in caplog.records)


class TestPyNoOverlap:
    """.py 文件名无重叠 → 放行无 warning。"""

    def test_py_no_overlap(self, tmp_path, monkeypatch, caplog):
        _setup_registry(tmp_path, monkeypatch)
        gw = _make_gateway(stdout="src/zephyr/foo/completely_unrelated.py")
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(
                gw, ["src/zephyr/foo/completely_unrelated.py"], session_id="s1",
            )
        assert passed is True
        assert detail == ""
        assert not caplog.records


class TestTestsDirExcluded:
    """tests/ 下 .py 文件不检测（gate L87 排除 tests/ 前缀）。"""

    def test_tests_dir_excluded(self, tmp_path, monkeypatch, caplog):
        _setup_registry(tmp_path, monkeypatch)
        gw = _make_gateway(stdout="tests/test_session_handoff.py")
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(
                gw, ["tests/test_session_handoff.py"], session_id="s1",
            )
        assert passed is True
        assert detail == ""
        assert not caplog.records


class TestYamlSecondSource:
    """_registry/ 下新建 .yaml 与同目录现有 .yaml token ≥2 重叠 → warning。"""

    def test_yaml_token_overlap(self, tmp_path, monkeypatch, caplog):
        _setup_registry(tmp_path, monkeypatch)
        # 在 tmp_path 下创建 _registry/contracts/ 目录 + 现有 yaml
        registry_dir = (
            tmp_path / "docs" / "01_policies_and_standards" / "_registry" / "contracts"
        )
        registry_dir.mkdir(parents=True)
        # 现有文件 directory_contract.yaml → tokens {directory, contract}
        (registry_dir / "directory_contract.yaml").write_text("test", encoding="utf-8")
        # 新文件 contract_directory.yaml → tokens {contract, directory}
        # overlap {directory, contract} → len=2 ≥ 2 → warning
        new_yaml_rel = (
            "docs/01_policies_and_standards/_registry/contracts/contract_directory.yaml"
        )
        monkeypatch.chdir(tmp_path)  # 让 glob 能找到现有文件
        gw = _make_gateway(stdout=new_yaml_rel)
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(gw, [new_yaml_rel], session_id="s1")
        assert passed is True  # warn-only
        assert any("contract_directory" in r.message for r in caplog.records)


class TestFailLoudGitDiff:
    """git diff 失败 → fail-loud（passed=True 保留 warn-only 契约 + logger.warning 告警检测器失效）。

    治本1（2026-06-30）：warn-only gate 的 fail-closed 语义=告警而非阻断。
    create_guard 已 fail-closed 阻断（同一 git diff），本 gate 无需重复阻断，
    但须 logger.warning 防静默漂移。
    """

    def test_git_diff_nonzero_returncode(self, tmp_path, monkeypatch, caplog):
        _setup_registry(tmp_path, monkeypatch)
        gw = _make_gateway(stdout="", returncode=1)
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(gw, ["src/foo.py"], session_id="s1")
        assert passed is True  # warn-only 契约：仍 return True
        assert detail == ""
        assert any("fail-loud" in r.message for r in caplog.records)

    def test_git_diff_exception(self, tmp_path, monkeypatch, caplog):
        _setup_registry(tmp_path, monkeypatch)
        gw = _make_gateway(exc=RuntimeError("git down"))
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(gw, ["src/foo.py"], session_id="s1")
        assert passed is True  # warn-only 契约：仍 return True
        assert detail == ""
        assert any("fail-loud" in r.message for r in caplog.records)


class TestFailLoudYamlMissing:
    """REGISTRY_YAML 不存在 → fail-loud（passed=True 保留 warn-only 契约 + logger.warning 告警）。"""

    def test_yaml_missing(self, tmp_path, monkeypatch, caplog):
        # 指向不存在的文件
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            tmp_path / "nonexistent.yaml",
        )
        gw = _make_gateway(stdout="src/zephyr/foo/session_handoff_loader.py")
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(
                gw, ["src/zephyr/foo/session_handoff_loader.py"], session_id="s1",
            )
        assert passed is True  # warn-only 契约：仍 return True
        assert detail == ""
        assert any("fail-loud" in r.message for r in caplog.records)


class TestFailLoudYamlParse:
    """YAML 解析失败 → fail-loud（passed=True 保留 warn-only 契约 + logger.warning 告警）。"""

    def test_yaml_invalid(self, tmp_path, monkeypatch, caplog):
        _setup_registry(
            tmp_path, monkeypatch, content="invalid: yaml: content:",
        )
        gw = _make_gateway(stdout="src/zephyr/foo/session_handoff_loader.py")
        gate = make_capability_overlap_gate()
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            passed, detail = gate.check(
                gw, ["src/zephyr/foo/session_handoff_loader.py"], session_id="s1",
            )
        assert passed is True  # warn-only 契约：仍 return True
        assert detail == ""
        assert any("fail-loud" in r.message for r in caplog.records)
