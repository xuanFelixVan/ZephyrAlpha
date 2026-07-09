# [A_test] module_id: SRC-TST-2227 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-id_uniqueness_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_id_uniqueness_gate
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_id_uniqueness_gate.py — ID-UNIQUENESS 门禁单测

权威依据：id_uniqueness_gate.py（make_id_uniqueness_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestConfigConstants: _CONFIG_REL / _CHECK_SCRIPT 路径常量
- TestGatewayIntegration: mock gateway + mock subprocess.run 三态
  - .pre-commit-config.yaml 不在 files → 不触发，放行
  - exit 0 → 放行（clean）
  - exit 1 → 阻断（fail-closed，violations）
  - exit 2 → fail-open 放行（script error）
  - 配置文件不在磁盘 → 不触发
  - exit 1 消息含 ID-UNIQUENESS

注意：gate 用 subprocess.run 调用 check 脚本——monkeypatch 隔离，不执行真实脚本。
配置文件用 tmp_path 真实创建（os.path.isfile 检查需要）。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.id_uniqueness_gate import (  # noqa: E402
    _CHECK_SCRIPT,
    _CONFIG_REL,
    make_id_uniqueness_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


def _make_gateway(project_root=None):
    """构造 mock gateway——本 gate 只读 gateway.project_root。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)
    return gw


def _install_subprocess(monkeypatch, returncode=0, stdout="", stderr=""):
    """mock subprocess.run 返回指定 returncode/stdout/stderr。"""
    import zephyr.governance.commit_gates.id_uniqueness_gate as mod

    def _run(cmd, **kwargs):
        class _R:
            pass
        r = _R()
        r.returncode = returncode
        r.stdout = stdout
        r.stderr = stderr
        return r

    monkeypatch.setattr(mod.subprocess, "run", _run)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_id_uniqueness_gate(), GateSpec)

    def test_gate_id(self):
        assert make_id_uniqueness_gate().gate_id == "ID-UNIQUENESS"

    def test_priority(self):
        assert make_id_uniqueness_gate().priority == 86


# ---------------------------------------------------------------------------
# TestConfigConstants — 路径常量
# ---------------------------------------------------------------------------
class TestConfigConstants:
    def test_config_rel_value(self):
        assert _CONFIG_REL == ".pre-commit-config.yaml"

    def test_check_script_value(self):
        assert _CHECK_SCRIPT.endswith("check_precommit_id_uniqueness.py")


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway + 三态 exit code
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_no_config_in_files_passes(self, tmp_path):
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [])
        assert passed
        assert "no .pre-commit-config.yaml" in msg

    def test_exit_zero_passes(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        cfg.write_text("repos: []\n", encoding="utf-8")
        _install_subprocess(monkeypatch, returncode=0)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert passed
        assert "passed" in msg

    def test_exit_one_blocked(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        cfg.write_text("repos: []\n", encoding="utf-8")
        _install_subprocess(
            monkeypatch, returncode=1, stdout="duplicate id: my-hook"
        )
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert not passed  # fail-closed
        assert "ID-UNIQUENESS" in msg

    def test_exit_two_fail_open(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        cfg.write_text("repos: []\n", encoding="utf-8")
        _install_subprocess(monkeypatch, returncode=2, stderr="traceback")
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert passed  # fail-open
        assert "fail-open" in msg or "exit=2" in msg

    def test_config_not_on_disk_not_triggered(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        # 不创建文件——os.path.isfile 失败 -> 不触发
        _install_subprocess(monkeypatch, returncode=1)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert passed
        assert "no .pre-commit-config.yaml" in msg

    def test_exit_one_message_contains_duplicate(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        cfg.write_text("repos: []\n", encoding="utf-8")
        _install_subprocess(
            monkeypatch, returncode=1, stdout="duplicate hook id: foo"
        )
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert not passed
        assert "duplicate" in msg

    def test_exit_two_does_not_block(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        cfg.write_text("repos: []\n", encoding="utf-8")
        # exit 2 即使 stdout 含 "duplicate" 也不阻断
        _install_subprocess(
            monkeypatch, returncode=2, stdout="duplicate id"
        )
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert passed

    def test_other_file_does_not_trigger(self, tmp_path, monkeypatch):
        other = tmp_path / "other.py"
        other.write_text("x = 1\n", encoding="utf-8")
        _install_subprocess(monkeypatch, returncode=1)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(other)])
        assert passed
        assert "no .pre-commit-config.yaml" in msg

    def test_exit_zero_message_clean(self, tmp_path, monkeypatch):
        cfg = tmp_path / _CONFIG_REL
        cfg.write_text("repos: []\n", encoding="utf-8")
        _install_subprocess(monkeypatch, returncode=0)
        gw = _make_gateway(project_root=str(tmp_path))
        passed, msg = make_id_uniqueness_gate().check(gw, [str(cfg)])
        assert passed
        assert "uniqueness check passed" in msg
