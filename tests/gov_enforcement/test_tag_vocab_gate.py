# [A_test] module_id: MOD-LIB-TAGVOCAB-GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-TAGVOCAB-GATE | docs/_working/ultimate_library/12_ulib3_directive.md | §1
# [MODULE] tests.gov_enforcement.test_tag_vocab_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-TAGVOCAB-GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_tag_vocab_gate.py — TAG-VOCAB 标签枚举门单测

权威依据：tag_vocab_gate.py（make_tag_vocab_gate）

测试组：
- TestGateSpecFields: gate_id / priority=134 / isinstance(GateSpec) / 默认 warn
- TestResolve: 标准词命中 / 别名解析 / 枚举外 None
- TestGatewayIntegration:
  * 枚举内 tags 放行（warn=0）
  * 别名放行
  * 非枚举词触发 warn（passed=True + detail + 审计 jsonl）
  * 词库缺失 fail-open / 词库损坏 fail-open
  * 词库本尊 staged：重复 canonical / 别名冲突进 findings
  * 非 yaml / 非 catalogs 范围不触发
  * block 模式升级（passed=False）

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 造临时词库与 staged yaml，
不读/不写真实仓库。
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

import zephyr.gov_enforcement.commit_gates.library.tag_vocab_gate as g  # noqa: E402
from zephyr.gov_enforcement.commit_gates.library.tag_vocab_gate import (  # noqa: E402
    _load_vocab,
    make_tag_vocab_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

_VOCAB_REL = g.TAG_VOCAB_REGISTRY_REL_PATH
_CATALOG_REL = "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml"


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_root: Path) -> MagicMock:
    gw = MagicMock()
    gw.project_root = str(tmp_root)

    def _run_git(cmd, *a, **k):
        cmd = list(cmd)
        if "rev-parse" in cmd:
            return _MockResult(returncode=0, stdout=str(tmp_root))
        return _MockResult(returncode=0, stdout="")

    gw.run_git = _run_git
    return gw


def _write(tmp_root: Path, rel: str, content: str) -> None:
    path = tmp_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


_VOCAB_YAML = """\
values:
  - {value: 均线, aliases: [MA, 移动平均]}
  - {value: 反转, aliases: [翻转]}
  - {value: 风控, aliases: []}
"""


class TestGateSpecFields:
    def test_gate_id_and_priority(self):
        spec = make_tag_vocab_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "TAG-VOCAB"
        assert spec.priority == 134

    def test_mode_constant_default_warn(self):
        assert g.TAG_VOCAB_GATE_MODE == "warn"


class TestResolve:
    def test_load_vocab_structure(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, _VOCAB_YAML)
        vocab = _load_vocab(str(tmp_path))
        assert vocab is not None
        assert vocab.defects == []
        assert vocab.resolve("均线") == "均线"
        assert vocab.resolve("MA") == "均线"
        assert vocab.resolve("翻转") == "反转"
        assert vocab.resolve("歪词") is None

    def test_duplicate_canonical_defect(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, "values:\n  - {value: 均线, aliases: []}\n  - {value: 均线, aliases: []}\n")
        vocab = _load_vocab(str(tmp_path))
        assert any("重复标准词" in d for d in vocab.defects)

    def test_alias_conflict_defect(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, "values:\n  - {value: 均线, aliases: [MA]}\n  - {value: 反转, aliases: [MA]}\n")
        vocab = _load_vocab(str(tmp_path))
        assert any("别名冲突" in d for d in vocab.defects)


class TestGatewayIntegration:
    def test_in_vocab_tags_pass_silent(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, _VOCAB_YAML)
        _write(tmp_path, _CATALOG_REL, "entries:\n  - id: A\n    tags: [均线, 风控]\n")
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_CATALOG_REL])
        assert passed is True
        assert detail == ""

    def test_alias_tag_passes_silent(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, _VOCAB_YAML)
        _write(tmp_path, _CATALOG_REL, "entries:\n  - id: A\n    tags: [MA, 翻转]\n")
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_CATALOG_REL])
        assert passed is True
        assert detail == ""

    def test_out_of_vocab_tag_warns_but_passes(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, _VOCAB_YAML)
        _write(tmp_path, _CATALOG_REL, "entries:\n  - id: A\n    tags: [均线, 歪词]\n")
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_CATALOG_REL])
        assert passed is True  # 观察期 warn-only 放行
        assert "TAG-VOCAB" in detail
        assert "歪词" in detail
        audit = tmp_path / ".runtime" / "gate_audit" / "tag_vocab.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert rec["mode"] == "warn"
        assert _CATALOG_REL in rec["findings"]

    def test_vocab_missing_fail_open(self, tmp_path):
        _write(tmp_path, _CATALOG_REL, "entries:\n  - id: A\n    tags: [歪词]\n")
        assert not (tmp_path / _VOCAB_REL).exists()
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_CATALOG_REL])
        assert passed is True
        assert detail == ""

    def test_vocab_corrupted_fail_open(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, "values: [ {broken\n  ::%%%yaml")
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_CATALOG_REL])
        assert passed is True
        assert detail == ""

    def test_vocab_self_staged_defects_reported(self, tmp_path):
        _write(
            tmp_path,
            _VOCAB_REL,
            "values:\n  - {value: 均线, aliases: [MA]}\n  - {value: 均线, aliases: [移动平均]}\n",
        )
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_VOCAB_REL])
        assert passed is True
        assert "重复标准词" in detail

    def test_non_yaml_and_out_of_scope_skipped(self, tmp_path):
        _write(tmp_path, _VOCAB_REL, _VOCAB_YAML)
        py_rel = "scripts/tools/foo.py"
        _write(tmp_path, py_rel, "x = 1\n")
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [py_rel])
        assert passed is True
        assert detail == ""

    def test_block_mode_escalation(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "TAG_VOCAB_GATE_MODE", "block")
        _write(tmp_path, _VOCAB_REL, _VOCAB_YAML)
        _write(tmp_path, _CATALOG_REL, "entries:\n  - id: A\n    tags: [歪词]\n")
        gw = _make_gateway(tmp_path)
        passed, detail = make_tag_vocab_gate().check(gw, [_CATALOG_REL])
        assert passed is False  # 升硬后 fail-closed
        assert "TAG-VOCAB" in detail
