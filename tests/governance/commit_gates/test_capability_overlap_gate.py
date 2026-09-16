# [A_test] module_id: MOD-GOV_capability_overlap_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_CAPABILITY_OVERLAP_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_capability_overlap_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_CAPABILITY_OVERLAP_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_capability_overlap_gate.py — CAPABILITY-OVERLAP 门禁单测

权威依据：capability_overlap_gate.py（make_capability_overlap_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestTokenize: _tokenize 分词（_/-/. 分隔 + 短 token 过滤）
- TestGatewayIntegration: mock gateway + monkeypatch REGISTRY_YAML
  - warn-only 契约：overlap 命中也 passed=True（永不阻断）
  - 无 overlap → 放行
  - tests/ 豁免
  - git diff 失败/异常 → fail-loud 仍 passed=True
  - registry 缺失/解析失败/非 dict → fail-loud 仍 passed=True

注意：warn-only gate 永远返回 (True, "")——fail-closed 语义=告警而非阻断。
REGISTRY_YAML 通过 monkeypatch 指向 tmp_path 文件，不读真实仓库。
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

import zephyr.governance.capability_lookup as _cap_lookup  # noqa: E402
from zephyr.gov_enforcement.commit_gates.capability_overlap_gate import (  # noqa: E402
    _tokenize,
    make_capability_overlap_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回新增文件列表。"""
    gw = MagicMock()
    gw.project_root = _PROJECT_ROOT  # Path object — gate code uses project_root / "scripts"

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


def _point_registry_at(monkeypatch, tmp_path, content):
    """将 capability_lookup.REGISTRY_YAML 指向 tmp_path 文件并写入 content。"""
    yaml_path = tmp_path / "capability_registry.yaml"
    yaml_path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(_cap_lookup, "REGISTRY_YAML", yaml_path)
    return yaml_path


@pytest.fixture(autouse=True)
def _no_real_clone_guard(monkeypatch):
    """本文件不测 CloneGuard 引擎本体：真调引擎 ≈31s/例，且结果随索引状态漂移。

    返回 None = "CloneGuard 不可用"分支（warn-only 兜底），正是这些例所断言的路径。
    需要阻断发现的例在体内再 monkeypatch 覆盖本桩（见 TestCosmeticTouchTaxExemption）。
    """
    import zephyr.gov_enforcement.commit_gates.capability_overlap_gate as _cog

    monkeypatch.setattr(_cog, "_run_clone_guard_check", lambda files: None)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_capability_overlap_gate(), GateSpec)

    def test_gate_id(self):
        assert make_capability_overlap_gate().gate_id == "CAPABILITY-OVERLAP"

    def test_priority(self):
        assert make_capability_overlap_gate().priority == 200


# ---------------------------------------------------------------------------
# TestTokenize — 分词纯函数
# ---------------------------------------------------------------------------
class TestTokenize:
    def test_underscore_split(self):
        assert _tokenize("data_loader") == {"data", "loader"}

    def test_hyphen_split(self):
        assert _tokenize("data-loader") == {"data", "loader"}

    def test_dot_split(self):
        assert _tokenize("data.loader") == {"data", "loader"}

    def test_filters_short_tokens(self):
        # "a" / "bc" < 4 字符被过滤
        assert _tokenize("a_bc") == set()

    def test_lowercase(self):
        # _tokenize 不拆 camelCase，仅按 _/-/. 分隔后小写
        assert _tokenize("DataLoader") == {"dataloader"}

    def test_mixed_separators(self):
        assert _tokenize("data-loader.v2") == {"data", "loader"}

    def test_empty_returns_empty(self):
        assert _tokenize("") == set()

    # --- #ARCH-CAPABILITY-OVERLAP-001 治本测试（2026-07-22）---

    def test_gate_token_filtered_as_stopword(self):
        """'gate' token 被 _STOP_WORDS 过滤——避免 *_gate.py 确定性误报。"""
        assert "gate" not in _tokenize("issue_resolved_integrity_gate")
        assert "gate" not in _tokenize("vocab_hardcode_gate")
        assert "gate" not in _tokenize("data_loader_gate")

    def test_test_token_filtered_as_stopword(self):
        """'test' token 被 _STOP_WORDS 过滤。"""
        assert "test" not in _tokenize("test_rollback_executor")
        assert "test" not in _tokenize("rollback_test_helper")

    def test_init_token_filtered_as_stopword(self):
        """'init' token 被 _STOP_WORDS 过滤。"""
        assert "init" not in _tokenize("init_loader")
        assert "init" not in _tokenize("data_init")

    def test_meaningful_4char_tokens_preserved(self):
        """有诊断价值的 4 字符 token 保留（data/core/base 等不过滤）。"""
        tokens = _tokenize("data_loader")
        assert "data" in tokens  # 4 字符但非 stop-word
        assert "loader" in tokens

    def test_no_gate_overlap_between_gate_files(self):
        """两个 *_gate.py 文件不应因 'gate' token 产生 overlap（治本验证）。"""
        tokens_a = _tokenize("issue_resolved_integrity_gate")
        tokens_b = _tokenize("vocab_hardcode_gate")
        # 'gate' 被过滤后，两文件无共同 token（功能不重叠）
        overlap = tokens_a & tokens_b
        assert "gate" not in overlap
        assert overlap == set(), f"意外 overlap: {overlap}"

    def test_real_overlap_still_detected(self):
        """真正功能重叠的文件名仍能检测（stop-word 不影响诊断价值）。"""
        tokens_a = _tokenize("rollback_executor")
        tokens_b = _tokenize("rollback_handler")
        overlap = tokens_a & tokens_b
        assert "rollback" in overlap  # 真正的语义重叠


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway + warn-only 契约
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_overlap_still_passes_warn_only(self, tmp_path, monkeypatch):
        _point_registry_at(
            monkeypatch,
            tmp_path,
            "capabilities:\n  - capability_id: data_loader\n    aliases:\n      - data-loader\n",
        )
        gw = _make_gateway(staged_files=["src/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # warn-only：命中 overlap 仍放行
        assert msg == ""

    def test_no_overlap_passes(self, tmp_path, monkeypatch):
        _point_registry_at(
            monkeypatch,
            tmp_path,
            "capabilities:\n  - capability_id: auth_manager\n    aliases: []\n",
        )
        gw = _make_gateway(staged_files=["src/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        gw = _make_gateway(staged_files=["tests/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # tests/ 豁免
        assert msg == ""

    def test_empty_staged_passes(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        gw = _make_gateway(staged_files=[])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_loud_git_diff_failure(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # fail-loud：仍 return True
        assert msg == ""

    def test_fail_loud_git_diff_exception(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_yaml_missing_still_passes(self, tmp_path, monkeypatch):
        # REGISTRY_YAML 指向不存在的文件
        yaml_path = tmp_path / "missing.yaml"
        monkeypatch.setattr(_cap_lookup, "REGISTRY_YAML", yaml_path)
        gw = _make_gateway(staged_files=["src/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # fail-loud：registry 缺失仍放行
        assert msg == ""

    def test_yaml_parse_error_still_passes(self, tmp_path, monkeypatch):
        yaml_path = tmp_path / "bad.yaml"
        yaml_path.write_text("\tbad: indent\n", encoding="utf-8")
        monkeypatch.setattr(_cap_lookup, "REGISTRY_YAML", yaml_path)
        gw = _make_gateway(staged_files=["src/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # fail-loud：YAML 解析失败仍放行
        assert msg == ""

    def test_non_dict_yaml_still_passes(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "just a string\n")
        gw = _make_gateway(staged_files=["src/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # fail-loud：顶层非 dict 仍放行
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path, monkeypatch):
        _point_registry_at(
            monkeypatch,
            tmp_path,
            "capabilities:\n  - capability_id: data_loader\n    aliases: []\n",
        )
        gw = _make_gateway(staged_files=["src/data_loader.txt"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed  # 非 .py / 非 _registry yaml 被忽略
        assert msg == ""

    def test_empty_registry_passes(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        gw = _make_gateway(staged_files=["src/data_loader.py"])
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed
        assert msg == ""


# ---------------------------------------------------------------------------
# TestCosmeticTouchTaxExemption — 裁定#273 CloneGuard 触碰税豁免
# ---------------------------------------------------------------------------
class TestCosmeticTouchTaxExemption:
    """阻断项源文件若与 HEAD 去 docstring 后 AST 等价 → 既有克隆不判给本批。

    fail-closed 方向同步行测试：真实语义变更/新增件/读不到，一律照常硬阻断。
    """

    HEAD_A = '"""说明\n\n# [ALGO_FLOW]\n# 层: 输入\n# [/ALGO_FLOW]\n"""\n\n\ndef dup():\n    return 1\n'
    STAGED_COSMETIC_A = '# [ALGO_FLOW] external: docs/x.yaml\n"""说明。"""\n\n\ndef dup():\n    return 1\n'
    STAGED_REAL_A = '"""说明。"""\n\n\ndef dup():\n    return 2\n'

    def _gw(self, head_blobs, staged_blobs):
        gw = MagicMock()
        gw.project_root = _PROJECT_ROOT

        def _run_git(cmd):
            arg = cmd[-1]
            if arg.startswith("HEAD:"):
                text = head_blobs.get(arg[5:])
                return _MockResult(0, text) if text is not None else _MockResult(1, "")
            if arg.startswith(":"):
                text = staged_blobs.get(arg[1:])
                return _MockResult(0, text) if text is not None else _MockResult(1, "")
            if "--name-only" in cmd:
                return _MockResult(0, "\n".join(sorted(staged_blobs)))
            return _MockResult(0, "")

        gw.run_git = _run_git
        return gw

    def _stub_blocking_findings(self, monkeypatch, sources):
        from zephyr.clone_guard.orchestrator import CheckResult

        import zephyr.gov_enforcement.commit_gates.capability_overlap_gate as cog

        findings = []
        for src in sources:
            f = MagicMock()
            f.source_file, f.source_function = src, "dup"
            f.existing_file, f.existing_function, f.existing_lineno = "src/zephyr/other.py", "dup", 7
            f.similarity, f.severity, f.clone_type = 1.0, "extract", "exact"
            findings.append(f)
        monkeypatch.setattr(
            cog,
            "_run_clone_guard_check",
            lambda files: CheckResult(passed=False, findings=findings, checked_files=len(files)),
        )
        return cog

    def test_docstring_only_source_is_exempt(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        self._stub_blocking_findings(monkeypatch, ["src/a.py"])
        gw = self._gw({"src/a.py": self.HEAD_A}, {"src/a.py": self.STAGED_COSMETIC_A})
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed is True
        assert msg == ""

    def test_executable_change_still_blocks(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        self._stub_blocking_findings(monkeypatch, ["src/a.py"])
        gw = self._gw({"src/a.py": self.HEAD_A}, {"src/a.py": self.STAGED_REAL_A})
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed is False
        assert "src/a.py:dup" in msg

    def test_new_file_is_not_exempt(self, tmp_path, monkeypatch):
        """HEAD 无此件（新增）→ 读不到即不豁免（新增克隆正是本门禁要拦的）。"""
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        self._stub_blocking_findings(monkeypatch, ["src/a.py"])
        gw = self._gw({}, {"src/a.py": self.STAGED_REAL_A})
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed is False
        assert "src/a.py" in msg

    def test_unparseable_staged_fails_closed(self, tmp_path, monkeypatch):
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        self._stub_blocking_findings(monkeypatch, ["src/a.py"])
        gw = self._gw({"src/a.py": self.HEAD_A}, {"src/a.py": "def dup(:"})
        passed, _ = make_capability_overlap_gate().check(gw, [])
        assert passed is False

    def test_mixed_batch_blocks_only_on_real_changes(self, tmp_path, monkeypatch):
        """同批混有纯文档串件与真实变更件：豁免只吃掉前者，后者照常阻断且点名。"""
        _point_registry_at(monkeypatch, tmp_path, "capabilities: []\n")
        self._stub_blocking_findings(monkeypatch, ["src/a.py", "src/b.py"])
        gw = self._gw(
            {"src/a.py": self.HEAD_A, "src/b.py": self.HEAD_A},
            {"src/a.py": self.STAGED_COSMETIC_A, "src/b.py": self.STAGED_REAL_A},
        )
        passed, msg = make_capability_overlap_gate().check(gw, [])
        assert passed is False
        assert "src/b.py" in msg
        assert "src/a.py" not in msg
