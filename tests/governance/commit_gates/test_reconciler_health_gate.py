# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_reconciler_health_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_reconciler_health_gate.py — RECONCILER-HEALTH 门禁单测

权威依据：reconciler_health_gate.py
（make_reconciler_health_gate，#ARCH-DATAQUALITY-V1.7）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCheckDualLevel: mock _check_recent_blocks / _check_recent_critical_warns
  - block_next 记录存在 → 阻断
  - critical_warn 记录存在 → 放行 + warning
  - 无记录 → 放行
  - 查询异常 → fail-open 放行

测试隔离：monkeypatch 替换 _check_recent_blocks / _check_recent_critical_warns，
不依赖真实 governance.db。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.reconciler_health_gate import (  # noqa: E402
    make_reconciler_health_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway：仅暴露 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec) 字段校验。"""

    def test_gate_id(self):
        gate = make_reconciler_health_gate()
        assert gate.gate_id == "RECONCILER-HEALTH"

    def test_priority(self):
        gate = make_reconciler_health_gate()
        assert gate.priority == 64

    def test_is_gate_spec(self):
        gate = make_reconciler_health_gate()
        assert isinstance(gate, GateSpec)

    def test_check_callable(self):
        gate = make_reconciler_health_gate()
        assert callable(gate.check)


class TestCheckDualLevel:
    """dual-level 检查：block_next 阻断 / critical_warn 警告 / 无记录放行。"""

    def test_no_records_pass(self, tmp_path: Path, monkeypatch):
        """无 block_next / critical_warn 记录 → 放行。"""
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            lambda root: [],
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            lambda root: [],
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "OK" in detail

    def test_block_next_blocks(self, tmp_path: Path, monkeypatch):
        """有 block_next 记录 → 硬阻断。"""
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            lambda root: [
                {
                    "gate_id": "GATE-DEPGRAPH-OPS",
                    "logged_at": "2026-07-19T00:00:00Z",
                    "detail": "depgraph ops sync failed",
                }
            ],
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            lambda root: [],
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "blocking reconciler failure" in detail
        assert "GATE-DEPGRAPH-OPS" in detail

    def test_critical_warn_passes_with_warning(self, tmp_path: Path, monkeypatch):
        """有 critical_warn 记录但无 block_next → 放行 + 警告。"""
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            lambda root: [],
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            lambda root: [
                {
                    "gate_id": "GATE-DRIFT-SCAN",
                    "logged_at": "2026-07-19T00:00:00Z",
                    "detail": "drift scan failed",
                }
            ],
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "WARN" in detail
        assert "GATE-DRIFT-SCAN" in detail

    def test_block_next_takes_priority_over_critical_warn(self, tmp_path: Path, monkeypatch):
        """同时有 block_next 和 critical_warn → 阻断（block_next 优先）。"""
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            lambda root: [
                {
                    "gate_id": "GATE-BLOCK",
                    "logged_at": "2026-07-19T00:00:00Z",
                    "detail": "hard block",
                }
            ],
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            lambda root: [
                {
                    "gate_id": "GATE-WARN",
                    "logged_at": "2026-07-19T00:00:00Z",
                    "detail": "soft warn",
                }
            ],
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "GATE-BLOCK" in detail


class TestFailOpen:
    """fail-open：查询异常时不阻断。"""

    def test_blocks_query_exception_passes(self, tmp_path: Path, monkeypatch):
        """_check_recent_blocks 抛异常 → fail-open 放行。"""

        def _raise(root):
            raise RuntimeError("db connection failed")

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            _raise,
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            lambda root: [],
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_warns_query_exception_passes(self, tmp_path: Path, monkeypatch):
        """_check_recent_critical_warns 抛异常 → fail-open 放行。"""
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            lambda root: [],
        )

        def _raise(root):
            raise RuntimeError("db connection failed")

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            _raise,
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True

    def test_both_query_exception_passes(self, tmp_path: Path, monkeypatch):
        """两个查询都抛异常 → fail-open 放行。"""

        def _raise(root):
            raise RuntimeError("db connection failed")

        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            _raise,
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            _raise,
        )
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True


class TestWarnBannerDedup:
    """T5 告警卫生（2026-08-14）：critical_warn 横幅 24h dedup。"""

    _WARNS = [
        {
            "gate_id": "GATE-DRIFT-SCAN",
            "logged_at": "2026-08-14T00:00:00Z",
            "detail": "drift scan failed",
        }
    ]

    def _patch_warns(self, monkeypatch, warns):
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_blocks",
            lambda root: [],
        )
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.reconciler_health_gate.check_recent_critical_warns",
            lambda root: warns,
        )

    def test_first_warn_prints(self, tmp_path: Path, monkeypatch, capsys):
        """首次告警 → 打印横幅 + dedup 状态落盘。"""
        self._patch_warns(monkeypatch, self._WARNS)
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "GATE-DRIFT-SCAN" in capsys.readouterr().out
        assert (tmp_path / ".runtime" / "reconciler_health_warn_dedup.json").exists()

    def test_same_signature_deduped_within_24h(self, tmp_path: Path, monkeypatch, capsys):
        """同签名告警 24h 内第二次 → 不打印（仍放行 + detail 保留）。"""
        self._patch_warns(monkeypatch, self._WARNS)
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        gate.check(gw, [])
        capsys.readouterr()  # 清掉首次输出
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert "WARN" in detail  # 语义不变
        assert capsys.readouterr().out == ""  # 但不再刷屏

    def test_new_signature_prints_again(self, tmp_path: Path, monkeypatch, capsys):
        """告警内容变化（新签名）→ 24h 内也照常打印（真告警不被淹没）。"""
        self._patch_warns(monkeypatch, self._WARNS)
        gw = _make_gateway(tmp_path)
        gate = make_reconciler_health_gate()
        gate.check(gw, [])
        capsys.readouterr()
        self._patch_warns(
            monkeypatch,
            self._WARNS + [{"gate_id": "GATE-NEW", "logged_at": "2026-08-14T01:00:00Z", "detail": "new failure"}],
        )
        passed, _ = gate.check(gw, [])
        assert passed is True
        assert "GATE-NEW" in capsys.readouterr().out
