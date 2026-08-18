# [A_test] module_id: MOD-GOV_registry_code_anchor_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_registry_code_anchor_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_REGISTRY_CODE_ANCHOR_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_registry_code_anchor_gate.py — REGISTRY-CODE-ANCHOR 门禁A + 指纹对账B 单测（#ARCH-BREG-002）

测试组：
- TestAnchorChecker: check_registry_code_anchor 校验逻辑（存在性/目录锚点/注释剥离/deprecated豁免/AST符号）
- TestFingerprint: compute_fingerprint 稳定性与漂移检测 + reconcile fix-in-place
- TestGateSpecFields / TestGateTrigger: gate 触发与双分支（注册表 staged / 代码删除反查）

测试隔离：tmp_path 夹具 + MagicMock gateway + monkeypatch checker 模块 REPO_ROOT/_CATALOGS，
不读/不写真实仓库（checker 经 importlib 按文件位置加载）。
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _load_module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _PROJECT_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


anchor = _load_module(
    "check_registry_code_anchor",
    "scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py",
)
fingerprint = _load_module(
    "check_registry_code_fingerprint",
    "scripts/governance/d5_architecture/checkers/check_registry_code_fingerprint.py",
)

from zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate import (  # noqa: E402
    _deleted_or_renamed_py,
    _find_anchor_references,
    _staged_registry_files,
    make_registry_code_anchor_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ---------------------------------------------------------------- fixtures

_REG_YAML = """module_id: MOD-GOVERNANCE
registry_id: REG-FCT-001
factors:
- factor_id: "FCT-T-001"
  status: "active"
  code_path: "{code_path}"
  code_symbol: {code_symbol}
- factor_id: "FCT-T-002"
  status: "deprecated"
  code_path: "src/dead/removed.py"
"""

_PY_CODE = '''def calc_alpha(x):
    """docstring."""
    return x * 2


class Runner:
    def run(self):
        """doc."""
        return calc_alpha(1)
'''

_PY_CODE_V2 = '''def calc_alpha(x):
    """docstring changed — 指纹应不变。"""
    return x * 2
'''

_PY_CODE_V3 = '''def calc_alpha(x):
    """docstring."""
    return x * 3
'''


def _write(tmp_path: Path, rel: str, content: str) -> Path:
    p = tmp_path.joinpath(*rel.split("/"))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    """工作区夹具：tmp REPO_ROOT + catalogs。"""
    monkeypatch.setattr(anchor, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(fingerprint, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(fingerprint, "_CATALOGS", tmp_path / "cat")
    return tmp_path


# ---------------------------------------------------------------- anchor checker

class TestAnchorChecker:
    def test_valid_file_anchor(self, ws):
        _write(ws, "src/a.py", _PY_CODE)
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/a.py", code_symbol="null"))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_missing_code_path(self, ws):
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/missing.py", code_symbol="null"))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert len(v) == 1 and "FCT-T-001" in v[0] and "code_path 不存在" in v[0]

    def test_directory_anchor_ok(self, ws):
        _write(ws, "src/pkg/__init__.py", "")
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/pkg/", code_symbol="null"))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_annotation_suffix_stripped(self, ws):
        _write(ws, "src/a.py", _PY_CODE)
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/a.py（主力实现）", code_symbol="null"))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_deprecated_entry_exempt(self, ws):
        # FCT-T-002 deprecated + code_path 不存在 → 豁免
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/missing.py", code_symbol="null"))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert all("FCT-T-002" not in x for x in v)

    def test_code_symbol_valid(self, ws):
        _write(ws, "src/a.py", _PY_CODE)
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/a.py", code_symbol='"src/a.py::calc_alpha"'))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_code_symbol_method_valid(self, ws):
        _write(ws, "src/a.py", _PY_CODE)
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/a.py", code_symbol='"src/a.py::Runner.run"'))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_code_symbol_missing_symbol(self, ws):
        _write(ws, "src/a.py", _PY_CODE)
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/a.py", code_symbol='"src/a.py::nope"'))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert len(v) == 1 and "符号不存在" in v[0]

    def test_code_symbol_bad_format(self, ws):
        _write(ws, "src/a.py", _PY_CODE)
        reg = _write(ws, "factor_registry.yaml", _REG_YAML.format(
            code_path="src/a.py", code_symbol='"src/a.py#calc_alpha"'))
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert len(v) == 1 and "::" in v[0]


# ---------------------------------------------------------------- list-purity（#118）

_DAR_YAML = """module_id: MOD-GOVERNANCE
sources: []
datasets:
{datasets_block}
jobs:
{jobs_block}
"""


class TestListPurity:
    """#118（2026-08-17，DS-104 错位实证治本）：条目 id 键 vs 所在列表纯净性。"""

    def _write_dar(self, ws, datasets_block: str, jobs_block: str):
        return _write(ws, "data_asset_registry.yaml", _DAR_YAML.format(
            datasets_block=datasets_block, jobs_block=jobs_block))

    def test_dataset_misplaced_into_jobs_flagged(self, ws):
        """dataset 条目混入 jobs 列表（DS-104 形态）→ [List-Purity] 违规。"""
        reg = self._write_dar(
            ws,
            "- dataset_id: DS-T-001\n  entity_type: dataset\n  status: production",
            "- job_id: JOB-T-001\n  entity_type: job\n  status: production\n"
            "- dataset_id: DS-T-002\n  entity_type: dataset\n  status: production",
        )
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert len(v) == 1
        assert "List-Purity" in v[0] and "DS-T-002" in v[0] and "dataset_id" in v[0]
        assert "job_id" in v[0]  # 期望键提示

    def test_correct_placement_no_violation(self, ws):
        """dataset/job 各归其位 → 零违规（不误报）。"""
        reg = self._write_dar(
            ws,
            "- dataset_id: DS-T-001\n  entity_type: dataset\n  status: production",
            "- job_id: JOB-T-001\n  entity_type: job\n  status: production",
        )
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_job_misplaced_into_datasets_flagged(self, ws):
        """反向形态：job 条目混入 datasets 列表 → 同样被抓。"""
        reg = self._write_dar(
            ws,
            "- dataset_id: DS-T-001\n  entity_type: dataset\n  status: production\n"
            "- job_id: JOB-T-009\n  entity_type: job\n  status: production",
            "- job_id: JOB-T-001\n  entity_type: job\n  status: production",
        )
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert len(v) == 1 and "JOB-T-009" in v[0] and "List-Purity" in v[0]

    def test_entry_without_any_id_no_false_positive(self, ws):
        """缺 id 但无外键的条目不报（保持现状语义，不扩大打击面）。"""
        reg = self._write_dar(
            ws,
            "- entity_type: dataset\n  status: candidate",
            "- job_id: JOB-T-001\n  entity_type: job\n  status: production",
        )
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert v == []

    def test_deprecated_misplaced_still_flagged(self, ws):
        """deprecated tombstone 错位同样被抓（错位不豁免）。"""
        reg = self._write_dar(
            ws,
            "- dataset_id: DS-T-001\n  entity_type: dataset\n  status: production",
            "- dataset_id: DS-T-OLD\n  entity_type: dataset\n  status: deprecated",
        )
        v: list[str] = []
        anchor.check_registry_file(reg, v)
        assert len(v) == 1 and "DS-T-OLD" in v[0]


# ---------------------------------------------------------------- fingerprint

class TestFingerprint:
    def test_docstring_change_stable(self, ws):
        p1 = _write(ws, "a.py", _PY_CODE)
        p2 = _write(ws, "b.py", _PY_CODE_V2)
        assert fingerprint.compute_fingerprint(p1, "calc_alpha") == fingerprint.compute_fingerprint(p2, "calc_alpha")

    def test_body_change_drifts(self, ws):
        p1 = _write(ws, "a.py", _PY_CODE)
        p3 = _write(ws, "c.py", _PY_CODE_V3)
        assert fingerprint.compute_fingerprint(p1, "calc_alpha") != fingerprint.compute_fingerprint(p3, "calc_alpha")

    def test_method_symbol(self, ws):
        p1 = _write(ws, "a.py", _PY_CODE)
        fp = fingerprint.compute_fingerprint(p1, "Runner.run")
        assert isinstance(fp, str) and len(fp) == 16

    def test_unknown_symbol_none(self, ws):
        p1 = _write(ws, "a.py", _PY_CODE)
        assert fingerprint.compute_fingerprint(p1, "ghost") is None

    def _mk_registry(self, ws, fp_value):
        (ws / "cat").mkdir(parents=True, exist_ok=True)
        return _write(ws, "cat/factor_registry.yaml", f"""module_id: M
factors:
- factor_id: "FCT-T-001"
  status: "active"
  code_symbol: "src/a.py::calc_alpha"
  code_fingerprint: {fp_value}
""")

    def test_reconcile_missing_snapshot_fix(self, ws, monkeypatch):
        _write(ws, "src/a.py", _PY_CODE)
        monkeypatch.setattr(fingerprint, "_is_merge_in_progress", lambda: False)
        reg = self._mk_registry(ws, "null")
        rc = fingerprint.reconcile(fix_in_place=True)
        assert rc == 0
        text = reg.read_text(encoding="utf-8")
        expected = fingerprint.compute_fingerprint(ws / "src/a.py", "calc_alpha")
        assert f'code_fingerprint: "{expected}"' in text

    def test_reconcile_drift_exit1(self, ws, monkeypatch):
        _write(ws, "src/a.py", _PY_CODE)
        monkeypatch.setattr(fingerprint, "_is_merge_in_progress", lambda: False)
        self._mk_registry(ws, '"deadbeefdeadbeef"')
        rc = fingerprint.reconcile(fix_in_place=False)
        assert rc == 1


# ---------------------------------------------------------------- gate

@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


def _make_gateway(project_root, deleted=()):
    gw = MagicMock()
    gw.project_root = project_root

    def _run_git(cmd):
        cmd_str = " ".join(cmd)
        if "diff" in cmd_str and "--cached" in cmd_str:
            lines = "".join(f"D\t{d}\n" for d in deleted)
            return _MockResult(0, lines)
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


class TestGateSpecFields:
    def test_spec(self):
        spec = make_registry_code_anchor_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "REGISTRY-CODE-ANCHOR"
        assert spec.priority == 129


class TestGateTrigger:
    def test_no_trigger_pass(self, ws):
        gw = _make_gateway(ws)
        spec = make_registry_code_anchor_gate()
        ok, _ = spec.check(gw, [str(ws / "src/foo.py")])
        assert ok is True

    def test_staged_registry_runs_checker(self, ws, monkeypatch):
        cat = ws / "docs/01_policies_and_standards/_registry/catalogs"
        reg = _write(ws, "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", "module_id: M\nfactors: []\n")
        _write(ws, "scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py", "# stub")
        calls = {}

        def fake_run_checker(path, args, cwd=None, timeout=None):
            calls["args"] = args
            return _MockResult(0, "OK")

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate.run_checker_script",
            fake_run_checker,
        )
        gw = _make_gateway(ws)
        spec = make_registry_code_anchor_gate()
        ok, _ = spec.check(gw, [str(reg)])
        assert ok is True
        assert "--files" in calls["args"]

    def test_staged_registry_violation_blocks(self, ws, monkeypatch):
        reg = _write(ws, "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", "module_id: M\nfactors: []\n")
        _write(ws, "scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py", "# stub")
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate.run_checker_script",
            lambda *a, **kw: _MockResult(1, "violations here"),
        )
        gw = _make_gateway(ws)
        spec = make_registry_code_anchor_gate()
        ok, detail = spec.check(gw, [str(reg)])
        assert ok is False
        assert "REGISTRY_CODE_ANCHOR_VIOLATION" in detail

    def test_checker_error_fail_open(self, ws, monkeypatch):
        reg = _write(ws, "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", "module_id: M\nfactors: []\n")
        _write(ws, "scripts/governance/d5_architecture/checkers/check_registry_code_anchor.py", "# stub")
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.registry_code_anchor_gate.run_checker_script",
            lambda *a, **kw: _MockResult(2, "env error"),
        )
        gw = _make_gateway(ws)
        spec = make_registry_code_anchor_gate()
        ok, _ = spec.check(gw, [str(reg)])
        assert ok is True

    def test_deleted_py_with_reference_blocks(self, ws):
        _write(ws, "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", (
            "module_id: M\nfactors:\n"
            '- factor_id: "FCT-T-001"\n'
            '  status: "active"\n'
            '  code_path: "src/zephyr/factor/mom.py"\n'
        ))
        gw = _make_gateway(ws, deleted=["src/zephyr/factor/mom.py"])
        spec = make_registry_code_anchor_gate()
        ok, detail = spec.check(gw, [str(ws / "src/zephyr/factor/mom.py")])
        assert ok is False
        assert "FCT-T-001" in detail

    def test_deleted_py_deprecated_reference_pass(self, ws):
        _write(ws, "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", (
            "module_id: M\nfactors:\n"
            '- factor_id: "FCT-T-001"\n'
            '  status: "deprecated"\n'
            '  code_path: "src/zephyr/factor/mom.py"\n'
        ))
        gw = _make_gateway(ws, deleted=["src/zephyr/factor/mom.py"])
        spec = make_registry_code_anchor_gate()
        ok, _ = spec.check(gw, [str(ws / "src/zephyr/factor/mom.py")])
        assert ok is True

    def test_deleted_py_no_reference_pass(self, ws):
        _write(ws, "docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml", "module_id: M\nfactors: []\n")
        gw = _make_gateway(ws, deleted=["src/zephyr/factor/other.py"])
        spec = make_registry_code_anchor_gate()
        ok, _ = spec.check(gw, [str(ws / "src/zephyr/factor/other.py")])
        assert ok is True


class TestDeletedPyParse:
    def test_rename_old_path(self, ws):
        gw = _make_gateway(ws)
        def _run_git(cmd):
            if "diff" in " ".join(cmd):
                return _MockResult(0, "R100\tsrc/old/mom.py\tsrc/new/mom.py\n")
            return _MockResult(0, "")
        gw.run_git = _run_git
        assert _deleted_or_renamed_py(gw) == ["src/old/mom.py"]

    def test_non_py_ignored(self, ws):
        gw = _make_gateway(ws)
        def _run_git(cmd):
            if "diff" in " ".join(cmd):
                return _MockResult(0, "D\tsrc/data/x.csv\nD\tdocs/a.md\n")
            return _MockResult(0, "")
        gw.run_git = _run_git
        assert _deleted_or_renamed_py(gw) == []
