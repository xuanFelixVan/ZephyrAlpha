# [A_test] module_id=SRC-TST-2140 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §67
# [MODULE] tests.red_blue.test_commit_trigger
# [INVARIANTS] tests MUST use tmp_path isolation; never write to real data/red_blue/trigger_queue; mock validator + circuit
# [MODIFY-GUARD] Adding consumer paths MUST add _process_one coverage here
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_commit_trigger.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# 直接加载 commit_trigger，绕过 zephyr 包 __init__ import 链断裂风险
import importlib.util as _ilu
from zephyr.shared.io.paths import REPO_ROOT

_spec = _ilu.spec_from_file_location(
    "_commit_trigger_under_test",
    REPO_ROOT
    / "src"
    / "zephyr"
    / "security"
    / "adversarial_validation"
    / "commit_trigger.py",
)
assert _spec is not None and _spec.loader is not None
ct = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(ct)

detect_formal_files = ct.detect_formal_files
write_trigger_record = ct.write_trigger_record
RedBlueTriggerConsumer = ct.RedBlueTriggerConsumer
FORMAL_HEADER_RE = ct.FORMAL_HEADER_RE


# ── detect_formal_files ─────────────────────────────────────────────


class TestDetectFormalFiles:
    def _write(self, tmp_path: Path, name: str, lines: list[str]) -> str:
        p = tmp_path / name
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(p)

    def test_blueprint_header_matched(self, tmp_path):
        f = self._write(tmp_path, "a.py", [
            "# [BLUEPRINT] MOD-INF-030 | docs/.../blueprint.md | §1",
            "# [MODULE] zephyr.xxx",
            "import os",
        ])
        result = detect_formal_files([f])
        assert result == [f]

    def test_module_header_matched(self, tmp_path):
        f = self._write(tmp_path, "b.py", [
            "# [MODULE] zephyr.security.adversarial_validation.commit_trigger",
            "from __future__ import annotations",
        ])
        assert detect_formal_files([f]) == [f]

    def test_no_header_not_matched(self, tmp_path):
        f = self._write(tmp_path, "c.py", [
            "import os",
            "import sys",
            "# regular comment",
        ])
        assert detect_formal_files([f]) == []

    def test_blueprint_no_brackets_not_matched(self, tmp_path):
        # registry YAML 头部 `# blueprint:` (无方括号) 必须不命中
        f = self._write(tmp_path, "reg.yaml", [
            "# --- 治理锚定 ---",
            "# blueprint: MOD-INF-005 | docs/.../blueprint.md | §",
            "# module_id: MOD-INF-005",
        ])
        assert detect_formal_files([f]) == []

    def test_header_beyond_scan_lines_not_matched(self, tmp_path):
        # 第 6 行才出现 [BLUEPRINT]，超出 5 行扫描窗口，不命中
        lines = [f"# line {i}" for i in range(5)]
        lines.append("# [BLUEPRINT] MOD-INF-030")
        f = self._write(tmp_path, "d.py", lines)
        assert detect_formal_files([f]) == []

    def test_nonexistent_file_skipped(self, tmp_path):
        # OSError 被吞，不抛异常
        result = detect_formal_files([str(tmp_path / "nope.py")])
        assert result == []

    def test_mixed_files(self, tmp_path):
        formal = self._write(tmp_path, "ok.py", ["# [MODULE] zephyr.x"])
        plain = self._write(tmp_path, "plain.py", ["import os"])
        result = detect_formal_files([plain, formal, str(tmp_path / "nope.py")])
        assert result == [formal]


# ── write_trigger_record ────────────────────────────────────────────


class TestWriteTriggerRecord:
    def test_writes_valid_json_and_fields(self, tmp_path):
        out = write_trigger_record(
            "abc123def456", "sess-1", ["a.py", "b.py"], queue_dir=tmp_path,
        )
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["commit_hash"] == "abc123def456"
        assert data["session_id"] == "sess-1"
        assert data["formal_files"] == ["a.py", "b.py"]
        assert "emitted_at" in data

    def test_filename_uses_hash8(self, tmp_path):
        out = write_trigger_record("0123456789abcdef", "s", [], queue_dir=tmp_path)
        # 文件名格式 <ts>_<hash8>.json
        assert out.name.endswith("_01234567.json")
        assert out.name.endswith(".json")

    def test_no_tmp_residue(self, tmp_path):
        write_trigger_record("hash1234567890", "s", ["x.py"], queue_dir=tmp_path)
        tmps = list(tmp_path.glob("*.tmp"))
        assert tmps == [], f"tmp residue found: {tmps}"

    def test_creates_queue_dir(self, tmp_path):
        nested = tmp_path / "deep" / "queue"
        out = write_trigger_record("h1234567890", "s", [], queue_dir=nested)
        assert nested.exists()
        assert out.exists()


# ── RedBlueTriggerConsumer._process_one ──────────────────────────────


def _make_queue_file(qdir: Path, commit_hash: str = "deadbeef1234") -> Path:
    qdir.mkdir(parents=True, exist_ok=True)
    record = {
        "commit_hash": commit_hash,
        "session_id": "test",
        "formal_files": ["src/x.py"],
        "emitted_at": "2026-06-26T20:00:00+00:00",
    }
    qf = qdir / "1700000000_deadbeef.json"
    qf.write_text(json.dumps(record), encoding="utf-8")
    return qf


class TestProcessOneGateClosed:
    def test_gate_closed_logs_and_unlinks_no_run(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ZEPHYR_RED_BLUE_AUTO_ENABLED", raising=False)
        consumer = RedBlueTriggerConsumer(queue_dir=tmp_path)
        # 注入 mock validator 探针：若被调则证明门禁失效
        mock_validator = MagicMock()
        consumer._validator = mock_validator
        qf = _make_queue_file(tmp_path)
        consumer._process_one(qf)
        assert not qf.exists(), "gate closed should unlink queue file"
        mock_validator.run_adversarial_session.assert_not_called()


class TestProcessOneGateOpenCircuitClosed:
    def test_gate_open_runs_validator_and_after_run(self, tmp_path, monkeypatch):
        monkeypatch.setenv("ZEPHYR_RED_BLUE_AUTO_ENABLED", "1")
        consumer = RedBlueTriggerConsumer(queue_dir=tmp_path)
        # mock circuit：before_run 不抛、after_run 记录
        mock_circuit = MagicMock()
        consumer._circuit = mock_circuit
        # mock validator：返回 fake report
        fake_report = MagicMock()
        fake_report.blocked = 14
        fake_report.bypassed = 0
        fake_report.total_scenarios = 14
        fake_report.total = 14
        mock_validator = MagicMock()
        mock_validator.run_adversarial_session.return_value = fake_report
        consumer._validator = mock_validator

        qf = _make_queue_file(tmp_path, "cafebabe1234")
        consumer._process_one(qf)

        mock_circuit.before_run.assert_called_once()
        mock_validator.run_adversarial_session.assert_called_once()
        # 断言传 tier=TIER_1, blast_radius=FILE
        kwargs = mock_validator.run_adversarial_session.call_args.kwargs
        assert kwargs.get("blast_radius") is not None  # BlastRadiusLevel.FILE
        mock_circuit.after_run.assert_called_once_with(fake_report)
        assert not qf.exists(), "successful run should unlink queue file"


class TestProcessOneGateOpenCircuitOpen:
    def test_circuit_open_skips_and_keeps_queue(self, tmp_path, monkeypatch):
        from zephyr.security.adversarial_validation.circuit_breaker import (
            CircuitBreakerOpenError,
        )

        monkeypatch.setenv("ZEPHYR_RED_BLUE_AUTO_ENABLED", "1")
        consumer = RedBlueTriggerConsumer(queue_dir=tmp_path)
        mock_circuit = MagicMock()
        mock_circuit.before_run.side_effect = CircuitBreakerOpenError("OPEN")
        consumer._circuit = mock_circuit
        mock_validator = MagicMock()
        consumer._validator = mock_validator

        qf = _make_queue_file(tmp_path, "feedface5678")
        consumer._process_one(qf)

        mock_circuit.before_run.assert_called_once()
        mock_validator.run_adversarial_session.assert_not_called()
        mock_circuit.after_run.assert_not_called()
        assert qf.exists(), "circuit open should KEEP queue file for retry"


# ── 消费者生命周期 ──────────────────────────────────────────────────


class TestConsumerLifecycle:
    def test_start_idempotent(self, tmp_path):
        consumer = RedBlueTriggerConsumer(queue_dir=tmp_path)
        consumer.start()
        first = consumer._thread
        consumer.start()  # 幂等，不应起第二个
        assert consumer._thread is first
        consumer.stop()
        assert consumer._thread is not None

    def test_drain_empty_dir_no_error(self, tmp_path):
        consumer = RedBlueTriggerConsumer(queue_dir=tmp_path)
        # 空目录不应抛
        consumer._drain_queue()
        # 不存在的目录也不抛
        consumer._queue_dir = tmp_path / "nonexistent"
        consumer._drain_queue()
