# [BLUEPRINT] MOD-GOV-059 | scripts/governance/gateway_post_commit_ritual.py | §
# [MODULE] tests.governance.test_gateway_post_commit_ritual
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# [A_test] module_id: MOD-GOV-059 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
"""test_gateway_post_commit_ritual.py — 网关批次收尾仪式单测（CAND-GATEMECH-005）。

全部 mock 子进程执行，不碰真实 git 仓 / 真实契约链：
- 批次信号检测（contracts / rules / 未触碰三态）
- 三步联动计划（contracts → generate+freeze+register；rules → register）
- 原子性：任一步失败 → 派生产物回滚到执行前字节快照
- main 出口码（0 无需收尾 / 0 成功 / 1 失败 / --check / --warn-only）
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts" / "governance"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import gateway_post_commit_ritual as ritual  # noqa: E402


class TestDetectBatchSignals:
    def test_contracts_touched(self) -> None:
        files = ["architecture_model/contracts/cross_layer_contracts.yaml", "src/foo.py"]
        assert ritual.detect_batch_signals(files) == (True, False)

    def test_rules_touched(self) -> None:
        files = ["docs/01_policies_and_standards/rules/trae_999_x_y.yaml"]
        assert ritual.detect_batch_signals(files) == (False, True)

    def test_neither_touched(self) -> None:
        assert ritual.detect_batch_signals(["src/zephyr/trading/x.py"]) == (False, False)

    def test_windows_separator_normalized(self) -> None:
        files = ["architecture_model\\contracts\\c.yaml"]
        assert ritual.detect_batch_signals(files) == (True, False)

    def test_shared_contracts_dir(self) -> None:
        files = ["src/zephyr/shared/contracts/ctr001.py"]
        assert ritual.detect_batch_signals(files) == (True, False)


class TestRunRitualPlan:
    def test_not_triggered_no_steps(self, tmp_path: Path) -> None:
        result = ritual.run_ritual(tmp_path, ["src/zephyr/x.py"])
        assert result.triggered is False
        assert result.steps == []
        assert result.ok is True

    def test_check_only_no_execution(self, tmp_path: Path) -> None:
        result = ritual.run_ritual(tmp_path, ["AGENTS.md"], check_only=True)
        assert result.triggered is True
        assert result.steps == []

    def test_rules_only_runs_register(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ritual, "_run_step", lambda cmd, root, env: 0)
        result = ritual.run_ritual(tmp_path, ["scripts/governance/quickstart.md"])
        assert [name for name, _ in result.steps] == ["integrity_register"]
        assert result.ok

    def test_contracts_runs_full_chain(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ritual, "_run_step", lambda cmd, root, env: 0)
        result = ritual.run_ritual(tmp_path, ["architecture_model/contracts/x.yaml"])
        assert [name for name, _ in result.steps] == [
            "generate_contracts",
            "contract_freeze",
            "integrity_register",
        ]
        assert result.ok

    def test_reconciler_mode_env_injected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: list[dict] = []
        monkeypatch.setattr(ritual, "_run_step", lambda cmd, root, env: captured.append(env) or 0)
        ritual.run_ritual(tmp_path, ["AGENTS.md"])
        assert captured and captured[0]["ZEPHYR_RECONCILER_MODE"] == "1"


class TestAtomicRollback:
    def test_failure_rolls_back_derived_outputs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """任一步失败 → 已写派生产物恢复执行前字节快照，仪式新建文件被删除。"""
        contracts_dir = tmp_path / "src" / "zephyr" / "shared" / "contracts"
        contracts_dir.mkdir(parents=True)
        existing = contracts_dir / "ctr.py"
        existing.write_bytes(b"original")
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True)

        call_count = 0

        def fake_step(cmd: list, root: Path, env: dict) -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # 第一步成功但改了派生产物 + 新建了一个文件
                existing.write_bytes(b"mutated")
                (contracts_dir / "new_gen.py").write_bytes(b"new")
                return 0
            return 2  # 第二步失败

        monkeypatch.setattr(ritual, "_run_step", fake_step)
        result = ritual.run_ritual(tmp_path, ["architecture_model/contracts/x.yaml"])

        assert result.ok is False
        assert result.rolled_back is True
        assert existing.read_bytes() == b"original"
        assert not (contracts_dir / "new_gen.py").exists()

    def test_failure_stops_chain(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        executed: list[str] = []

        def fake_step(cmd: list, root: Path, env: dict) -> int:
            executed.append(cmd[1])
            return 1  # 第一步即失败

        monkeypatch.setattr(ritual, "_run_step", fake_step)
        result = ritual.run_ritual(tmp_path, ["architecture_model/contracts/x.yaml"])
        assert len(result.steps) == 1
        assert result.ok is False


class TestMainEntry:
    def test_main_not_triggered(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["ritual", "--files", "src/zephyr/x.py"])
        assert ritual.main() == 0

    def test_main_check_mode(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
        monkeypatch.setattr(sys, "argv", ["ritual", "--check", "--files", "AGENTS.md"])
        assert ritual.main() == 1

    def test_main_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["ritual", "--files", "AGENTS.md"])
        monkeypatch.setattr(ritual, "_run_step", lambda cmd, root, env: 0)
        assert ritual.main() == 0

    def test_main_failure_warn_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["ritual", "--warn-only", "--files", "AGENTS.md"])
        monkeypatch.setattr(ritual, "_run_step", lambda cmd, root, env: 2)
        assert ritual.main() == 0

    def test_main_failure_blocking(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["ritual", "--files", "AGENTS.md"])
        monkeypatch.setattr(ritual, "_run_step", lambda cmd, root, env: 2)
        assert ritual.main() == 1
