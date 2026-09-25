# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.conftest
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""tests/ai_layer/scheduling 共享夹具：policy 加载（真实治理常量只读）与事件 journal 隔离。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import pytest

from zephyr.ai_layer.scheduling.maturity import load_gate_policy
from zephyr.ai_layer.scheduling.scheduling_events import SchedulingJournal

REPO: Final = Path(__file__).resolve().parents[3]


@pytest.fixture()
def policy() -> dict[str, Any]:
    """真实治理常量层（config/schedule_gate_policy.yaml 只读——测试禁写生产路径）。"""
    return load_gate_policy()


@pytest.fixture()
def journal(tmp_path: Path) -> SchedulingJournal:
    return SchedulingJournal(state_dir=tmp_path / "ai_scheduling")
