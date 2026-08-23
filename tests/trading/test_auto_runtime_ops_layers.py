# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §6.2
# [MODULE] tests.trading.test_auto_runtime_ops_layers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/trading/test_auto_runtime_ops_layers.py -q
# [TTL] permanent

"""AutoRuntime 三层运营中心轻量骨架（MOD-INF-035 缩减补齐）单元测试——
监控/调度/自愈三层接口位可用性与降级语义。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.runtime_config import RuntimeConfig


def _make_core(tmp_path) -> AutoRuntimeCore:
    config = RuntimeConfig(
        audit_log_dir=tmp_path / "audit",
        capability_card_dir=tmp_path / "cards",
        night_shift_storage_path=tmp_path / "night.jsonl",
        work_dag_dir=tmp_path / "dags",
        dream_archive_dir=tmp_path / "dream",
        feedback_proposal_dir=tmp_path / "feedback",
        health_snapshot_dir=tmp_path / "health",
        auto_start_l2=False,
    )
    with patch("zephyr.trading.auto_runtime_core.AutoRuntimeCore.init_a2a"):
        return AutoRuntimeCore(config)


class TestOpsLayerAccessor:
    def test_monitor_layer_wired(self, tmp_path):
        core = _make_core(tmp_path)
        assert core.ops_layer("monitor") is core.health_monitor

    def test_scheduler_layer_none_by_default(self, tmp_path):
        core = _make_core(tmp_path)
        assert core.ops_layer("scheduler") is None

    def test_scheduler_layer_prefers_local_scheduler(self, tmp_path):
        core = _make_core(tmp_path)
        fake = MagicMock(name="LocalModelScheduler")
        core.local_scheduler = fake
        assert core.ops_layer("scheduler") is fake

    def test_scheduler_layer_falls_back_to_fle(self, tmp_path):
        core = _make_core(tmp_path)
        fake = MagicMock(name="FeedbackLoopScheduler")
        core.fle_scheduler = fake
        assert core.ops_layer("scheduler") is fake

    def test_self_heal_layer_returns_engine(self, tmp_path):
        core = _make_core(tmp_path)
        engine = core.ops_layer("self_heal")
        assert engine is not None
        assert type(engine).__name__ == "ResourceOptimizationEngine"

    def test_unknown_layer_rejected(self, tmp_path):
        core = _make_core(tmp_path)
        with pytest.raises(ValueError):
            core.ops_layer("nope")


class TestOpsLayersStatus:
    def test_status_shape(self, tmp_path):
        core = _make_core(tmp_path)
        status = core.ops_layers_status()
        assert set(status) == {"monitor", "scheduler", "self_heal"}
        assert status["monitor"]["available"] is True
        assert status["scheduler"]["available"] is False
        assert status["self_heal"]["available"] is True
        assert status["self_heal"]["degraded"] is False

    def test_self_heal_degraded_when_boot_marked(self, tmp_path):
        core = _make_core(tmp_path)
        core._resource_engine_degraded = True
        status = core.ops_layers_status()
        assert status["self_heal"]["available"] is False
        assert status["self_heal"]["degraded"] is True

    def test_scheduler_available_after_wire(self, tmp_path):
        core = _make_core(tmp_path)
        core.local_scheduler = MagicMock(name="LocalModelScheduler")
        assert core.ops_layers_status()["scheduler"]["available"] is True
