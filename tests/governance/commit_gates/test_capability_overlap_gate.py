# [A_test] module_id: SRC-TST-2206 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-capability_overlap_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_capability_overlap_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
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

from zephyr.governance.commit_gates.capability_overlap_gate import (  # noqa: E402
    _tokenize,
    make_capability_overlap_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

import zephyr.governance.capability_lookup as _cap_lookup  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回新增文件列表。"""
    gw = MagicMock()
    gw.project_root = str(_PROJECT_ROOT)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


def _point_registry_at(monkeypatch, tmp_path, content):
    """将 capability_lookup.REGISTRY_YAML 指向 tmp_path 文件并写入 content。"""
    yaml_path = tmp_path / "capability_registry.yaml"
    yaml_path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(_cap_lookup, "REGISTRY_YAML", yaml_path)
    return yaml_path


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
