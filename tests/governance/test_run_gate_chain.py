# [BLUEPRINT] MOD-GOV_GATE_CHAIN | scripts/governance/run_gate_chain.py | §
# [MODULE] tests.governance.test_run_gate_chain
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_run_gate_chain.py — run_gate_chain 聚合语义三态单测（CAND-GATEMECH-001/002 治本）。

覆盖：
1. 三态聚合（CAND-GATEMECH-002）：零发现=0 / 有发现=1 / 检测器自身异常=2；
   混合时 ERROR 掩盖 FINDINGS（修复"末位非零覆盖"缺陷）；启动失败=2 不抛 traceback。
2. 报告二分（CAND-GATEMECH-001）：内容判定区 vs hook 副作用区分列；
   files-modified 副作用不计入聚合 exit。
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts" / "governance"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import run_gate_chain as rgc  # noqa: E402


def _step(name: str, rc: int | None, **kwargs) -> rgc.StepResult:
    return rgc.StepResult(name=name, returncode=rc, **kwargs)


class TestAggregateThreeStates:
    """聚合退出码三态（CAND-GATEMECH-002）。"""

    def test_all_pass_returns_zero(self) -> None:
        steps = [_step("a.py", 0), _step("b.py", 0)]
        assert rgc.aggregate_exit_code(steps) == 0

    def test_findings_returns_one(self) -> None:
        steps = [_step("a.py", 0), _step("b.py", 1)]
        assert rgc.aggregate_exit_code(steps) == 1

    def test_error_returns_two(self) -> None:
        steps = [_step("a.py", 0), _step("b.py", 2)]
        assert rgc.aggregate_exit_code(steps) == 2

    def test_error_dominates_findings(self) -> None:
        """修复点：前一步 exit 2 不被后一步 exit 1 掩盖（原 code=returncode 末位覆盖缺陷）。"""
        steps = [_step("err.py", 2), _step("findings.py", 1)]
        assert rgc.aggregate_exit_code(steps) == 2

    def test_launch_failure_is_error(self) -> None:
        steps = [_step("missing.py", None, launch_error="FileNotFoundError: x")]
        assert rgc.aggregate_exit_code(steps) == 2

    def test_negative_returncode_is_error(self) -> None:
        steps = [_step("killed.py", -9)]
        assert rgc.aggregate_exit_code(steps) == 2


class TestSideEffectsDecoupled:
    """files-modified 副作用与内容判定解耦（CAND-GATEMECH-001）。"""

    def test_side_effect_does_not_fail(self) -> None:
        """内容 PASS 但改了文件的步骤：聚合 exit 仍为 0，副作用仅标注。"""
        steps = [_step("gen.py", 0, side_effects=(" M scripts/governance/script_manifest.yaml",))]
        assert rgc.aggregate_exit_code(steps) == 0

    def test_report_has_two_sections(self, capsys: pytest.CaptureFixture) -> None:
        steps = [
            _step("clean.py", 0),
            _step("dirty.py", 0, side_effects=(" M a.yaml",)),
            _step("findings.py", 1),
        ]
        rgc._print_report(steps)
        out = capsys.readouterr().out
        assert "内容判定" in out
        assert "hook 副作用" in out
        assert "dirty.py" in out
        assert " M a.yaml" in out
        assert "findings.py" in out

    def test_report_no_side_effects(self, capsys: pytest.CaptureFixture) -> None:
        rgc._print_report([_step("clean.py", 0)])
        out = capsys.readouterr().out
        assert "hook 副作用" in out
        assert "（无）" in out


class TestSnapshotAndDiff:
    """git 快照差分（临时目录夹具，不碰真实 git 仓）。"""

    def test_snapshot_none_when_not_git_repo(self) -> None:
        """系统临时目录（repo 外）无 git 仓 → 快照 None（跳过副作用检测，不阻断）。"""
        outside = Path(tempfile.mkdtemp(prefix="rgc_nogit_"))
        assert rgc._snapshot_worktree(outside) is None

    def test_diff_snapshots_skips_unavailable(self) -> None:
        assert rgc._diff_snapshots(None, frozenset({" M a"})) == ()
        assert rgc._diff_snapshots(frozenset({" M a"}), None) == ()

    def test_diff_snapshots_delta_only(self) -> None:
        before = frozenset({"M  staged.py", "?? untracked.py"})
        after = frozenset({"M  staged.py", "?? untracked.py", " M new_change.py"})
        assert rgc._diff_snapshots(before, after) == (" M new_change.py",)


class TestRunStepEndToEnd:
    """子进程执行集成（临时目录假门禁脚本）。"""

    def _write_gate(self, tmp_path: Path, name: str, body: str) -> str:
        p = tmp_path / name
        p.write_text(body, encoding="utf-8")
        return str(p)

    def test_zero_findings_gate_pass(self, tmp_path: Path) -> None:
        gate = self._write_gate(tmp_path, "gate_pass.py", "import sys\nsys.exit(0)\n")
        step = rgc._run_step(gate, [])
        assert step.verdict == "PASS"
        assert step.returncode == 0

    def test_findings_gate(self, tmp_path: Path) -> None:
        gate = self._write_gate(tmp_path, "gate_findings.py", "import sys\nsys.exit(1)\n")
        step = rgc._run_step(gate, [])
        assert step.verdict == "FINDINGS"

    def test_broken_gate_is_error_not_traceback(self, tmp_path: Path) -> None:
        """检测器自身异常（exit>=2）→ ERROR，聚合层不崩溃不抛 traceback。"""
        gate = self._write_gate(tmp_path, "gate_broken.py", "import sys\nsys.exit(2)\n")
        step = rgc._run_step(gate, [])
        assert step.verdict == "ERROR"
        assert step.returncode == 2

    def test_abnormal_exit_code_is_error(self, tmp_path: Path) -> None:
        gate = self._write_gate(tmp_path, "gate_abnormal.py", "import sys\nsys.exit(3)\n")
        step = rgc._run_step(gate, [])
        assert step.verdict == "ERROR"

    def test_missing_gate_launch_error(self, tmp_path: Path) -> None:
        step = rgc._run_step(str(tmp_path / "no_such_gate.py"), [])
        # sys.executable 启动成功但脚本不存在 → python 自身 exit 2
        assert step.verdict == "ERROR"


class TestMainEntry:
    def test_no_args_returns_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["run_gate_chain.py"])
        assert rgc.main() == 2

    def test_main_aggregates(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        ok = tmp_path / "ok.py"
        ok.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        bad = tmp_path / "bad.py"
        bad.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["run_gate_chain.py", str(ok), str(bad)])
        assert rgc.main() == 1
