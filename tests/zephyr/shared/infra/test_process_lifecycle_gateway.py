# [A_test] module_id: SRC-TST-2093 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-710 | tests/zephyr/shared/infra/test_process_lifecycle_gateway.py | §
# [TTL] task_bound
"""
Tests for ProcessLifecycleGateway.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT

PROJECT_ROOT = REPO_ROOT


@pytest.fixture
def gateway():
    from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway

    gw = ProcessLifecycleGateway()
    yield gw
    gw.terminate_all()
    gw.shutdown()


class TestProcessLifecycleGateway:
    def test_launch_returns_pooled_process(self, gateway):
        entry = gateway.launch("test-echo", [sys.executable, "-c", "import time; time.sleep(5)"])
        assert entry is not None
        assert entry.is_alive
        assert entry.pid > 0

    def test_launch_reuses_existing(self, gateway):
        e1 = gateway.launch("test-reuse", [sys.executable, "-c", "import time; time.sleep(5)"])
        e2 = gateway.launch("test-reuse", [sys.executable, "-c", "import time; time.sleep(1)"])
        assert e1 is not None
        assert e2 is not None
        assert e1.pid == e2.pid

    def test_terminate_kills_process(self, gateway):
        entry = gateway.launch("test-kill", [sys.executable, "-c", "import time; time.sleep(300)"])
        assert entry is not None
        assert entry.is_alive
        gateway.terminate("test-kill")
        time.sleep(0.5)
        assert not entry.is_alive

    def test_terminate_all_clears_pool(self, gateway):
        gateway.launch("test-all-1", [sys.executable, "-c", "import time; time.sleep(5)"])
        gateway.launch("test-all-2", [sys.executable, "-c", "import time; time.sleep(5)"])
        count = gateway.terminate_all()
        assert count >= 2
        stats = gateway.get_stats()
        assert stats.active_processes == 0

    def test_launch_nonexistent_cmd_returns_none(self, gateway):
        entry = gateway.launch("test-missing", ["_nonexistent_command_xyz_"])
        assert entry is None

    def test_launch_daemon_registers(self, gateway):
        ok = gateway.launch_daemon("test-daemon", [sys.executable, "-c", "import time; time.sleep(5)"])
        assert ok is True


class TestGateScanner:
    def test_gate_detects_bare_popen(self, tmp_path: Path):
        from zephyr.governance.rule_enforcement.invariants.en_process_lifecycle_gateway import scan_file

        bad_code = tmp_path / "bad.py"
        bad_code.write_text(
            "import subprocess\nsubprocess.Popen(['cmd'])\n",
            encoding="utf-8",
        )
        violations = scan_file(str(bad_code))
        assert len(violations) >= 1

    def test_gate_allows_gateway_consumer(self, tmp_path: Path):
        from zephyr.governance.rule_enforcement.invariants.en_process_lifecycle_gateway import scan_file

        good_code = tmp_path / "good.py"
        good_code.write_text(
            "from zephyr.shared.infra.process_lifecycle_gateway import ProcessLifecycleGateway\n"
            "gw = ProcessLifecycleGateway()\n"
            "gw.launch('test', ['python'])\n",
            encoding="utf-8",
        )
        violations = scan_file(str(good_code))
        assert len(violations) == 0
