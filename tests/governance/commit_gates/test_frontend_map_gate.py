# [A_test] module_id: MOD-GOV_frontend_map_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_FRONTEND_MAP_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_frontend_map_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_FRONTEND_MAP_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_frontend_map_gate.py — FRONTEND-MAP 门禁单测（六图对齐 commit 链闭环）

测试组：
- GateSpec 字段（gate_id/priority=137）
- 真源健康（当前仓库 frontend_map.yaml fail=0）→ 放行
- fail 注入（monkeypatch run_checks 返回 fail）→ 阻断
- YAML 异常 → fail-closed 阻断（真源损坏须先修）
- 校验器加载失败 → fail-closed

测试隔离：monkeypatch check_frontend_map.run_checks（不读真实仓库外部状态）；
真源健康用例直接读真实 frontend_map.yaml（只读，验证端到端接线）。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.gov_enforcement.commit_gates.frontend_map_gate as g  # noqa: E402
from zephyr.gov_enforcement.commit_gates.frontend_map_gate import (  # noqa: E402
    make_frontend_map_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@pytest.fixture()
def gate():
    return make_frontend_map_gate()


@pytest.fixture()
def gw(tmp_path):
    gw = MagicMock()
    gw.project_root = str(tmp_path)
    return gw


@pytest.fixture(autouse=True)
def _ensure_checker_loaded():
    """强制加载 check_frontend_map（gate 动态 import 的目标），保证 monkeypatch 目标存在。"""
    checkers_dir = str(
        Path(__file__).resolve().parents[3] / "scripts" / "governance" / "d5_architecture" / "generators"
    )
    if checkers_dir not in sys.path:
        sys.path.insert(0, checkers_dir)
    import check_frontend_map  # noqa: F401



class TestGateSpecFields:
    def test_gate_id_and_priority(self, gate):
        assert isinstance(gate, GateSpec)
        assert gate.gate_id == "FRONTEND-MAP"
        assert gate.priority == 137


class TestCheckBehaviour:
    def test_healthy_truth_source_passes(self, gate, gw):
        """真源健康（当前仓库 fail=0）→ 放行。"""
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_fail_blocks(self, gate, gw, monkeypatch):
        monkeypatch.setattr(
            "check_frontend_map.run_checks",
            lambda: (["R1 X: backend_ref 悬空"], ["R2 Y warn"], 302),
        )
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "FRONTEND-MAP" in detail
        assert "R1 X" in detail

    def test_yaml_error_blocks_fail_closed(self, gate, gw, monkeypatch):
        import yaml

        def boom():
            raise yaml.YAMLError("E:\\q 转义炸先例复现")

        monkeypatch.setattr("check_frontend_map.run_checks", boom)
        passed, detail = gate.check(gw, [])
        assert passed is False
        assert "真源损坏" in detail
