# [A_test] module_id: SRC-TST-2199 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-panorama_alignment_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §panorama-alignment-gate
# [MODULE] tests.governance.commit_gates.test_panorama_alignment_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_panorama_alignment_gate.py — 四图模块对齐门禁单测（GATE-PANORAMA-ALIGNMENT，ARCH-056 四图升级）

权威依据：panorama_alignment_gate.py（make_panorama_alignment_gate）

测试组：
- TestGateSpecFields: gate_id / priority 字段正确
- TestShouldTrigger: _should_trigger 路径匹配（命中/不命中/Windows 反斜杠）
- TestCheckNoTrigger: staged 文件不触及三图 → 跳过检测（passed=True）
- TestCheckTriggerClean: 触发但报告无问题 → passed=True
- TestCheckTriggerBlockDomainMismatch: 三图内部不一致（dataflow/decision）→ **阻断**（passed=False）【ARCH-056 四图升级】
- TestCheckTriggerBlockDomainMismatchWithOrphans: 三图内部不一致+orphans → 仍阻断
- TestCheckTriggerBlueprintOnlyMismatchWarns: blueprint-only 不一致 → warn-only（passed=True）【ARCH-056 四图升级】
- TestCheckTriggerWarnOrphans: 触发且孤儿超阈值 → warn-only（passed=True）
- TestCheckTriggerWarnDrift: 触发且状态漂移超阈值 → warn-only（passed=True）
- TestCheckPanoramaEmpty: run_alignment 抛 PanoramaEmptyError → 跳过（passed=True）
- TestCheckRunAlignmentException: run_alignment 抛通用异常 → fail-open（passed=True）
- TestCheckGitDiffFails: git diff 返回非零 → fail-open（passed=True）
- TestCheckGitDiffRaises: git diff 抛异常 → fail-open（passed=True）

阻断契约（ARCH-056 四图升级）：
- 三图内部 domain_mismatches>0（dataflow/decision 列非"-"）→ passed=False（阻断 commit）
- blueprint-only 域不一致（仅 blueprint 列不一致）→ warn-only（passed=True）
- orphans / state_drifts 超阈值 → warn-only（passed=True）
- run_alignment / git diff 异常 → fail-open（passed=True）
"""
from __future__ import annotations

import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.panorama_alignment_gate import (
    _ORPHAN_WARN_THRESHOLD,
    _STATE_DRIFT_WARN_THRESHOLD,
    _TRIGGER_PATTERNS,
    _should_trigger,
    make_panorama_alignment_gate,
)


# ---------------------------------------------------------------------------
# 辅助：fake 报告 / fake git 结果 / fake gateway
# ---------------------------------------------------------------------------


@dataclass
class FakeReport:
    """模拟 PanoramaAlignmentReport（仅门禁需要的字段）。"""

    orphans: list = field(default_factory=list)
    state_drifts: list = field(default_factory=list)
    domain_mismatches: list = field(default_factory=list)
    design_only_in_one: list = field(default_factory=list)


@dataclass
class FakeCompleted:
    """模拟 subprocess.CompletedProcess。"""

    returncode: int = 0
    stdout: str = ""


def _make_gateway(
    project_root: Path,
    diff_stdout: str = "",
    diff_rc: int = 0,
    diff_raises: BaseException | None = None,
) -> MagicMock:
    """构造 mock gateway，模拟 _run_git + project_root。"""
    gw = MagicMock()
    gw.project_root = project_root
    if diff_raises is not None:
        gw._run_git.side_effect = diff_raises
    else:
        gw._run_git.return_value = FakeCompleted(returncode=diff_rc, stdout=diff_stdout)
    return gw


def _install_fake_align_module(
    monkeypatch,
    *,
    run_alignment=None,
    raises: BaseException | None = None,
) -> None:
    """注入 fake align_panoramas 模块到 sys.modules（含父包链）。

    门禁 _check 内部动态 import：
        from governance.d5_architecture.generators.align_panoramas import PanoramaEmptyError, run_alignment
    通过 sys.modules 注入避免依赖真实 scripts/ 路径与 PG 连接。
    """

    class PanoramaEmptyError(RuntimeError):
        pass

    # 父包链
    for name in (
        "governance",
        "governance.d5_architecture",
        "governance.d5_architecture.generators",
    ):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    fake = types.ModuleType("governance.d5_architecture.generators.align_panoramas")
    fake.PanoramaEmptyError = PanoramaEmptyError

    if raises is not None:
        fake.run_alignment = lambda *a, **k: (_ for _ in ()).throw(raises)
    else:
        fake.run_alignment = run_alignment

    monkeypatch.setitem(
        sys.modules, "governance.d5_architecture.generators.align_panoramas", fake
    )
    return fake


# ---------------------------------------------------------------------------
# 1. GateSpec 字段
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id(self):
        gate = make_panorama_alignment_gate()
        assert gate.gate_id == "GATE-PANORAMA-ALIGNMENT"

    def test_priority(self):
        gate = make_panorama_alignment_gate()
        assert gate.priority == 830


# ---------------------------------------------------------------------------
# 2. _should_trigger 纯函数
# ---------------------------------------------------------------------------


class TestShouldTrigger:
    """_should_trigger 路径匹配。"""

    def test_matching_path_triggers(self):
        assert _should_trigger(
            ["src/zephyr/governance/depgraph_schema.py"]
        ) is True

    def test_non_matching_path_no_trigger(self):
        assert _should_trigger(["README.md", "docs/index.md"]) is False

    def test_windows_backslash_normalized(self):
        # Windows 反斜杠路径也应命中
        assert _should_trigger(
            ["src\\zephyr\\governance\\depgraph_schema.py"]
        ) is True

    def test_trigger_patterns_nonempty(self):
        # 健全性：触发模式表非空（防止配置丢失静默失效）
        assert len(_TRIGGER_PATTERNS) > 0

    def test_each_pattern_can_trigger(self):
        # 每个模式都能触发（防止死模式）
        for pattern in _TRIGGER_PATTERNS:
            assert _should_trigger([pattern]) is True, f"pattern 未触发: {pattern}"


# ---------------------------------------------------------------------------
# 3. _check 闭包——warn-only 契约（永远 passed=True）
# ---------------------------------------------------------------------------


class TestCheckNoTrigger:
    """staged 文件不触及三图 → 跳过检测（passed=True）。"""

    def test_no_trigger_skips(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_stdout="README.md\n")
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckTriggerClean:
    """触发但报告无问题 → passed=True。"""

    def test_trigger_clean_report(self, tmp_path, monkeypatch):
        _install_fake_align_module(
            monkeypatch, run_alignment=lambda *a, **k: FakeReport()
        )
        gw = _make_gateway(
            tmp_path, diff_stdout="src/zephyr/governance/depgraph_schema.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckTriggerBlockDomainMismatch:
    """触发且 domain_mismatches>0 → **阻断**（passed=False）【ARCH-056 升级】。"""

    def test_domain_mismatch_blocks_commit(self, tmp_path, monkeypatch):
        # 三图内部不一致（depgraph vs dataflow）→ 阻断
        report = FakeReport(
            domain_mismatches=[
                {"module_id": "MOD-X", "depgraph": "D_A", "dataflow": "D_B",
                 "decision": "-", "blueprint": "-"}
            ]
        )
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path, diff_stdout="scripts/governance/apply_depgraph.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "domain_id" in detail
        assert "1" in detail
        assert "sync_panorama_module.py" in detail

    def test_multiple_domain_mismatches_block(self, tmp_path, monkeypatch):
        # 3 处三图内部不一致 → 阻断
        report = FakeReport(
            domain_mismatches=[
                {"module_id": "MOD-A", "depgraph": "D_A", "dataflow": "D_X",
                 "decision": "-", "blueprint": "-"},
                {"module_id": "MOD-B", "depgraph": "D_B", "dataflow": "D_Y",
                 "decision": "-", "blueprint": "-"},
                {"module_id": "MOD-C", "depgraph": "D_C", "decision": "D_Z",
                 "dataflow": "-", "blueprint": "-"},
            ]
        )
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path, diff_stdout="scripts/governance/generate_project_depgraph.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "3" in detail


class TestCheckTriggerBlockDomainMismatchWithOrphans:
    """domain_mismatch + orphans 同时存在 → 仍阻断（domain_mismatch 优先）。"""

    def test_domain_mismatch_with_orphans_still_blocks(self, tmp_path, monkeypatch):
        # 三图内部不一致 + orphans → 仍阻断（domain_mismatch 优先）
        report = FakeReport(
            domain_mismatches=[{"module_id": "MOD-X", "depgraph": "D_A",
                                "dataflow": "D_B", "decision": "-", "blueprint": "-"}],
            orphans=[{"m": "x"}] * (_ORPHAN_WARN_THRESHOLD + 5),
        )
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path, diff_stdout="scripts/governance/apply_depgraph.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "domain_id" in detail


class TestCheckTriggerBlueprintOnlyMismatchWarns:
    """blueprint-only 域不一致 → warn-only（passed=True，ARCH-056 四图升级）。

    blueprint 是 depgraph 的派生数据，其域不一致属同步延迟问题，
    不阻断 commit，仅 warn 提示运行 sync_panorama_module.py 对齐。
    """

    def test_blueprint_only_mismatch_warns_only(self, tmp_path, monkeypatch):
        # 仅 depgraph vs blueprint 不一致（dataflow/decision 一致）→ warn-only
        report = FakeReport(
            domain_mismatches=[
                {"module_id": "MOD-X", "depgraph": "D_A", "dataflow": "D_A",
                 "decision": "D_A", "blueprint": "D_B"}
            ]
        )
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path, diff_stdout="scripts/governance/apply_depgraph.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True  # blueprint-only 不阻断
        assert detail == ""

    def test_multiple_blueprint_only_mismatches_warn_only(self, tmp_path, monkeypatch):
        # 多处 blueprint-only 不一致 → 仍 warn-only
        report = FakeReport(
            domain_mismatches=[
                {"module_id": "MOD-A", "depgraph": "D_A", "dataflow": "D_A",
                 "decision": "D_A", "blueprint": "D_X"},
                {"module_id": "MOD-B", "depgraph": "D_B", "dataflow": "D_B",
                 "decision": "D_B", "blueprint": "D_Y"},
            ]
        )
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path, diff_stdout="scripts/governance/apply_depgraph.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckTriggerWarnOrphans:
    """触发且孤儿超阈值 → warn-only（passed=True，不阻断）。"""

    def test_orphans_over_threshold_warns_only(self, tmp_path, monkeypatch):
        report = FakeReport(orphans=[{"m": "x"}] * (_ORPHAN_WARN_THRESHOLD + 1))
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path, diff_stdout="scripts/governance/apply_depgraph.py\n"
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True  # warn-only 不阻断
        assert detail == ""


class TestCheckTriggerWarnDrift:
    """触发且状态漂移超阈值 → warn-only（passed=True）。"""

    def test_drift_over_threshold_warns_only(self, tmp_path, monkeypatch):
        report = FakeReport(
            state_drifts=[{"m": "x"}] * (_STATE_DRIFT_WARN_THRESHOLD + 1)
        )
        _install_fake_align_module(monkeypatch, run_alignment=lambda *a, **k: report)
        gw = _make_gateway(
            tmp_path,
            diff_stdout="docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml\n",
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckPanoramaEmpty:
    """run_alignment 抛 PanoramaEmptyError → 跳过（passed=True）。"""

    def test_panorama_empty_skips(self, tmp_path, monkeypatch):
        class PanoramaEmptyError(RuntimeError):
            pass

        _install_fake_align_module(monkeypatch, raises=PanoramaEmptyError("empty"))
        gw = _make_gateway(
            tmp_path,
            diff_stdout="scripts/governance/d5_architecture/generators/align_panoramas.py\n",
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckRunAlignmentException:
    """run_alignment 抛通用异常 → fail-open（passed=True）。"""

    def test_run_alignment_exception_fail_open(self, tmp_path, monkeypatch):
        _install_fake_align_module(monkeypatch, raises=RuntimeError("db down"))
        gw = _make_gateway(
            tmp_path,
            diff_stdout="scripts/governance/generate_project_depgraph.py\n",
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckGitDiffFails:
    """git diff 返回非零 → fail-open（passed=True）。"""

    def test_git_diff_nonzero_fail_open(self, tmp_path, monkeypatch):
        # 即使触发模式命中，git diff 失败也应 fail-open
        _install_fake_align_module(
            monkeypatch, run_alignment=lambda *a, **k: FakeReport()
        )
        gw = _make_gateway(
            tmp_path,
            diff_stdout="src/zephyr/governance/depgraph_schema.py\n",
            diff_rc=1,
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


class TestCheckGitDiffRaises:
    """git diff 抛异常 → fail-open（passed=True）。"""

    def test_git_diff_raises_fail_open(self, tmp_path, monkeypatch):
        _install_fake_align_module(
            monkeypatch, run_alignment=lambda *a, **k: FakeReport()
        )
        gw = _make_gateway(
            tmp_path,
            diff_raises=OSError("spawn failed"),
        )
        gate = make_panorama_alignment_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""
