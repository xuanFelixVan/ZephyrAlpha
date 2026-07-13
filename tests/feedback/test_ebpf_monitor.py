# [A_test] module_id: SRC-TST-0826 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_ebpf_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ebpf_monitor.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.reliability.ebpf_monitor import EBPFMonitor


class TestEBPFMonitorInstantiation:
    def test_default_instantiation(self):
        monitor = EBPFMonitor()
        assert monitor is not None

    def test_default_disabled(self):
        monitor = EBPFMonitor()
        assert monitor.enabled is False

    def test_enabled_instantiation(self):
        monitor = EBPFMonitor(enabled=True)
        assert monitor.enabled is True

    def test_is_dataclass(self):
        monitor = EBPFMonitor()
        assert hasattr(monitor, "__dataclass_fields__")


class TestEnabledAttribute:
    def test_can_toggle_enabled(self):
        monitor = EBPFMonitor()
        assert monitor.enabled is False
        monitor.enabled = True
        assert monitor.enabled is True

    def test_can_toggle_back(self):
        monitor = EBPFMonitor(enabled=True)
        monitor.enabled = False
        assert monitor.enabled is False

    def test_multiple_instances_independent(self):
        m1 = EBPFMonitor(enabled=True)
        m2 = EBPFMonitor(enabled=False)
        assert m1.enabled is True
        assert m2.enabled is False
