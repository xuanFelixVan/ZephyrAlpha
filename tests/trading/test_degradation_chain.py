# [A_test] module_id: MOD-GOV_degradation_chain | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §3.3
# [MODULE] tests.trading.test_degradation_chain
# [INVARIANTS] 阈值真源=蓝图§3.3四级降级链;WARNING=Lv1/CRITICAL=Lv2/EMERGENCY=Lv3
# [MODIFY-GUARD] src/zephyr/trading/resource_optimization.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] degradation_lv 返回 Lv0~Lv3
# [TESTS] tests/trading/test_degradation_chain.py
# [TTL] task_bound

"""四级降级链对齐测试（04号文 Phase 0 步骤 0.5，蓝图 §3.3 / D-INF035-05）。

蓝图 §3.3 阈值：Lv1 CPU>75%/MEM>70%；Lv2 CPU>85%/MEM>80%；Lv3 CPU>95%/MEM>90%。
04号文验收「人工压测触发 Lv1/Lv2/Lv3 各一次」以合成负载（ResourceSnapshot 注入）
+ 状态机迁移序列替代——单机施工环境不做真实压测，特此注明。
"""

from __future__ import annotations

from zephyr.shared.lifecycle.resource_optimization_models import PressureLevel, ResourceSnapshot
from zephyr.trading.resource_optimization import (
    DEGRADATION_CHAIN,
    ResourceOptimizationEngine,
    _HysteresisConfig,
    _PressureStateMachine,
    _PressureThresholds,
    degradation_lv,
)


def _classify(snap: ResourceSnapshot) -> PressureLevel:
    """绕过单例/子系统初始化，直接以默认阈值做纯分类（合成负载注入点）。"""
    engine = object.__new__(ResourceOptimizationEngine)
    engine._thresholds = _PressureThresholds()
    return engine._classify_pressure(snap)


class TestThresholdsAlignedWithBlueprint:
    def test_default_thresholds_match_blueprint_3_3(self):
        t = _PressureThresholds()
        assert t.cpu_warning_percent == 75.0
        assert t.memory_warning_percent == 70.0
        assert t.cpu_critical_percent == 85.0
        assert t.memory_critical_percent == 80.0
        assert t.cpu_emergency_percent == 95.0
        assert t.memory_emergency_percent == 90.0

    def test_lv0_normal_below_all_thresholds(self):
        snap = ResourceSnapshot(memory_percent=69.0, cpu_percent=74.0, process_count=20)
        assert _classify(snap) is PressureLevel.NORMAL

    def test_lv1_triggered_by_cpu_over_75(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=76.0, process_count=20)
        assert _classify(snap) is PressureLevel.WARNING

    def test_lv1_triggered_by_mem_over_70(self):
        snap = ResourceSnapshot(memory_percent=71.0, cpu_percent=50.0, process_count=20)
        assert _classify(snap) is PressureLevel.WARNING

    def test_lv2_triggered_by_cpu_over_85(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=86.0, process_count=20)
        assert _classify(snap) is PressureLevel.CRITICAL

    def test_lv2_triggered_by_mem_over_80(self):
        snap = ResourceSnapshot(memory_percent=81.0, cpu_percent=50.0, process_count=20)
        assert _classify(snap) is PressureLevel.CRITICAL

    def test_lv3_triggered_by_cpu_over_95(self):
        snap = ResourceSnapshot(memory_percent=50.0, cpu_percent=96.0, process_count=20)
        assert _classify(snap) is PressureLevel.EMERGENCY

    def test_lv3_triggered_by_mem_over_90(self):
        snap = ResourceSnapshot(memory_percent=91.0, cpu_percent=50.0, process_count=20)
        assert _classify(snap) is PressureLevel.EMERGENCY


class TestDegradationChainMapping:
    def test_four_levels_complete(self):
        assert set(DEGRADATION_CHAIN) == {
            PressureLevel.NORMAL,
            PressureLevel.WARNING,
            PressureLevel.CRITICAL,
            PressureLevel.EMERGENCY,
        }

    def test_lv_mapping_matches_blueprint(self):
        assert degradation_lv(PressureLevel.NORMAL) == "Lv0"
        assert degradation_lv(PressureLevel.WARNING) == "Lv1"
        assert degradation_lv(PressureLevel.CRITICAL) == "Lv2"
        assert degradation_lv(PressureLevel.EMERGENCY) == "Lv3"

    def test_lv_actions_match_blueprint_3_3(self):
        assert "StatusDashboard 降采样" in DEGRADATION_CHAIN[PressureLevel.WARNING]["actions"]
        assert "OrphanDetector 暂停" in DEGRADATION_CHAIN[PressureLevel.WARNING]["actions"]
        assert "纯增量" in DEGRADATION_CHAIN[PressureLevel.CRITICAL]["actions"]
        assert "降频30s" in DEGRADATION_CHAIN[PressureLevel.CRITICAL]["actions"]
        assert "拒绝非P0 DAG" in DEGRADATION_CHAIN[PressureLevel.EMERGENCY]["actions"]
        assert "Kill Switch" in DEGRADATION_CHAIN[PressureLevel.EMERGENCY]["actions"]


class TestStateMachineSyntheticTransitions:
    """合成负载序列驱动状态机逐级迁移（人工压测的替代留痕）。"""

    def test_escalation_lv0_to_lv3_with_confirmation(self):
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=2, cooldown_seconds=0.0))
        assert sm.current is PressureLevel.NORMAL  # Lv0

        for _ in range(2):  # Lv1：合成 CPU>75% 连续 2 轮确认
            sm.transition(_classify(ResourceSnapshot(memory_percent=50.0, cpu_percent=80.0, process_count=20)))
        assert sm.current is PressureLevel.WARNING

        for _ in range(2):  # Lv2：合成 CPU>85%
            sm.transition(_classify(ResourceSnapshot(memory_percent=50.0, cpu_percent=90.0, process_count=20)))
        assert sm.current is PressureLevel.CRITICAL

        for _ in range(2):  # Lv3：合成 CPU>95%
            sm.transition(_classify(ResourceSnapshot(memory_percent=50.0, cpu_percent=99.0, process_count=20)))
        assert sm.current is PressureLevel.EMERGENCY

        lv_path = [degradation_lv(lv) for lv in (PressureLevel.NORMAL, PressureLevel.WARNING, PressureLevel.CRITICAL, PressureLevel.EMERGENCY)]
        assert lv_path == ["Lv0", "Lv1", "Lv2", "Lv3"]

    def test_single_spike_does_not_escalate(self):
        """迟滞保护：单次合成尖峰不升级（confirmation_count=2）。"""
        sm = _PressureStateMachine(_HysteresisConfig(confirmation_count=2, cooldown_seconds=0.0))
        sm.transition(_classify(ResourceSnapshot(memory_percent=95.0, cpu_percent=50.0, process_count=20)))
        assert sm.current is PressureLevel.NORMAL
