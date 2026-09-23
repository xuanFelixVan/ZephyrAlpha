# [A_test] module_id: MOD-LIB-BLOODGATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-BLOODGATE | docs/_working/ultimate_library/12_ulib3_directive.md | §1
# [MODULE] tests.gov_enforcement.test_library_blood_flesh_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-BLOODGATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_library_blood_flesh_gate.py — BLOOD-FLESH 血肉门单测

权威依据：library_blood_flesh_gate.py（make_library_blood_flesh_gate）

测试组：
- TestGateSpecFields: gate_id / priority=133 / 默认 warn
- TestFaceA: staged 新增 .py 翻译条目缺 name_zh 触发 warn；name_zh 齐放行；
  plain_zh 缺失不归本闸（不重复罚）
- TestFaceB: 翻译册相对 HEAD 新增条目——缺 name_zh/plain_zh/generic 触发；
  双全放行；存量条目不追溯
- TestFailOpen: loader 不可达 fail-open；HEAD 不可读 B 面跳过
- TestMode: block 升硬 passed=False

测试隔离：monkeypatch _load_loader（fake loader），MagicMock 模拟 run_git，
tmp_path 造临时翻译册，不读/不写真实仓库。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.gov_enforcement.commit_gates.library.library_blood_flesh_gate as g  # noqa: E402
from zephyr.gov_enforcement.commit_gates.library.library_blood_flesh_gate import (  # noqa: E402
    make_library_blood_flesh_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

_REG_REL = g.TRANSLATION_REGISTRY_REL_PATH
_SRC_REL = "src/zephyr/trading/new_module.py"


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_root: Path, staged_py: list[str] | None = None, head_registry: str | None = "") -> MagicMock:
    gw = MagicMock()
    gw.project_root = str(tmp_root)

    def _run_git(cmd, *a, **k):
        cmd = list(cmd)
        if "--name-only" in cmd and "--diff-filter=A" in cmd:
            return _MockResult(returncode=0, stdout="\n".join(staged_py or []))
        if "show" in cmd and any("HEAD:" in c for c in cmd):
            if head_registry is None:
                return _MockResult(returncode=128, stdout="")
            return _MockResult(returncode=0, stdout=head_registry)
        return _MockResult(returncode=0, stdout="")

    gw.run_git = _run_git
    return gw


def _write(tmp_root: Path, rel: str, content: str) -> None:
    path = tmp_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fake_loader(entries: dict[str, dict[str, str]]):
    def _get(module_path):
        return entries.get(module_path)

    def _is_generic(plain):
        return plain.strip() in ("提供功能。", "该模块提供功能实现。")

    def _is_generic_suffix(plain, name_zh):
        return bool(name_zh) and plain.strip() == f"{name_zh}模块。"

    return _get, _is_generic, _is_generic_suffix


def _install_loader(monkeypatch, entries):
    monkeypatch.setattr(g, "_load_loader", lambda: _fake_loader(entries))


class TestGateSpecFields:
    def test_gate_id_and_priority(self):
        spec = make_library_blood_flesh_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "BLOOD-FLESH"
        assert spec.priority == 133

    def test_mode_constant_default_warn(self):
        assert g.BLOOD_FLESH_GATE_MODE == "warn"


class TestFaceA:
    def test_missing_name_zh_warns(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {_SRC_REL: {"name_zh": "", "plain_zh": "ok"}})
        _write(tmp_path, _SRC_REL, "x = 1\n")
        gw = _make_gateway(tmp_path, staged_py=[_SRC_REL])
        passed, detail = make_library_blood_flesh_gate().check(gw, [str(tmp_path / _SRC_REL)])
        assert passed is True  # 观察期 warn-only
        assert "BLOOD-FLESH" in detail
        assert "name_zh" in detail
        audit = tmp_path / ".runtime" / "gate_audit" / "library_blood_flesh.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert rec["mode"] == "warn"

    def test_complete_blood_passes_silent(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {_SRC_REL: {"name_zh": "新模块", "plain_zh": "ok"}})
        _write(tmp_path, _SRC_REL, "x = 1\n")
        gw = _make_gateway(tmp_path, staged_py=[_SRC_REL])
        passed, detail = make_library_blood_flesh_gate().check(gw, [str(tmp_path / _SRC_REL)])
        assert passed is True
        assert detail == ""

    def test_plain_zh_missing_not_our_job(self, tmp_path, monkeypatch):
        # plain_zh 空但 name_zh 在 → 不归本闸（TRANSLATION-COVERAGE 硬闸管辖）
        _install_loader(monkeypatch, {_SRC_REL: {"name_zh": "新模块", "plain_zh": ""}})
        _write(tmp_path, _SRC_REL, "x = 1\n")
        gw = _make_gateway(tmp_path, staged_py=[_SRC_REL])
        passed, detail = make_library_blood_flesh_gate().check(gw, [str(tmp_path / _SRC_REL)])
        assert passed is True
        assert detail == ""

    def test_no_new_py_silent(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {})
        gw = _make_gateway(tmp_path, staged_py=[])
        passed, detail = make_library_blood_flesh_gate().check(gw, ["docs/x.md"])
        assert passed is True
        assert detail == ""


class TestFaceB:
    _HEAD_REG = (
        "entries:\n"
        "- module_path: src/zephyr/old.py\n"
        "  name_zh: 旧模块\n"
        "  plain_zh: 旧的大白话说明。\n"
    )

    def test_new_entry_missing_blood_warns(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {})
        staged = (
            "entries:\n"
            "- module_path: src/zephyr/old.py\n"
            "  name_zh: 旧模块\n"
            "  plain_zh: 旧的大白话说明。\n"
            "- module_path: src/zephyr/new.py\n"
            "  name_zh: ''\n"
            "  plain_zh: ''\n"
        )
        _write(tmp_path, _REG_REL, staged)
        gw = _make_gateway(tmp_path, head_registry=self._HEAD_REG)
        passed, detail = make_library_blood_flesh_gate().check(gw, [_REG_REL])
        assert passed is True
        assert "src/zephyr/new.py" in detail
        assert "name_zh" in detail and "plain_zh" in detail

    def test_new_entry_generic_plain_warns(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {})
        staged = (
            "entries:\n"
            "- module_path: src/zephyr/new.py\n"
            "  name_zh: 新模块\n"
            "  plain_zh: 该模块提供功能实现。\n"
        )
        _write(tmp_path, _REG_REL, staged)
        gw = _make_gateway(tmp_path, head_registry=self._HEAD_REG)
        passed, detail = make_library_blood_flesh_gate().check(gw, [_REG_REL])
        assert passed is True
        assert "通用模板" in detail

    def test_new_entry_complete_passes_silent(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {})
        staged = (
            "entries:\n"
            "- module_path: src/zephyr/new.py\n"
            "  name_zh: 新模块\n"
            "  plain_zh: 把行情快照按交易日切片入库的大白话说明。\n"
        )
        _write(tmp_path, _REG_REL, staged)
        gw = _make_gateway(tmp_path, head_registry=self._HEAD_REG)
        passed, detail = make_library_blood_flesh_gate().check(gw, [_REG_REL])
        assert passed is True
        assert detail == ""

    def test_existing_entries_not_retrochecked(self, tmp_path, monkeypatch):
        # 存量条目（HEAD 已有）即使缺血肉也不追溯（bootstrap 豁免）
        _install_loader(monkeypatch, {})
        _write(tmp_path, _REG_REL, self._HEAD_REG)
        gw = _make_gateway(tmp_path, head_registry=self._HEAD_REG)
        passed, detail = make_library_blood_flesh_gate().check(gw, [_REG_REL])
        assert passed is True
        assert detail == ""

    def test_registry_not_staged_skips_face_b(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {})
        gw = _make_gateway(tmp_path, head_registry=self._HEAD_REG)
        passed, detail = make_library_blood_flesh_gate().check(gw, ["docs/other.yaml"])
        assert passed is True
        assert detail == ""


class TestFailOpen:
    def test_loader_unavailable_fail_open(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "_load_loader", lambda: None)
        _write(tmp_path, _SRC_REL, "x = 1\n")
        gw = _make_gateway(tmp_path, staged_py=[_SRC_REL])
        passed, detail = make_library_blood_flesh_gate().check(gw, [str(tmp_path / _SRC_REL)])
        assert passed is True
        assert detail == ""

    def test_head_unreadable_face_b_skipped(self, tmp_path, monkeypatch):
        _install_loader(monkeypatch, {})
        staged = "entries:\n- module_path: src/zephyr/new.py\n  name_zh: ''\n  plain_zh: ''\n"
        _write(tmp_path, _REG_REL, staged)
        gw = _make_gateway(tmp_path, head_registry=None)  # HEAD 不可读（首次提交）
        passed, detail = make_library_blood_flesh_gate().check(gw, [_REG_REL])
        assert passed is True
        assert detail == ""


class TestMode:
    def test_block_mode_escalation(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "BLOOD_FLESH_GATE_MODE", "block")
        _install_loader(monkeypatch, {_SRC_REL: {"name_zh": "", "plain_zh": "ok"}})
        _write(tmp_path, _SRC_REL, "x = 1\n")
        gw = _make_gateway(tmp_path, staged_py=[_SRC_REL])
        passed, detail = make_library_blood_flesh_gate().check(gw, [str(tmp_path / _SRC_REL)])
        assert passed is False
        assert "BLOOD-FLESH" in detail
