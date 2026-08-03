# [A_test] module_id: MOD-GOV_exchange_partition_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_exchange_partition_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_exchange_partition_detector.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.exchange_partition_detector import ExchangePartitionDetector


class TestExchangePartitionDetectorInit:
    def test_default_empty_exchanges(self):
        detector = ExchangePartitionDetector()
        assert len(detector.known_exchanges) == 0

    def test_register_single_exchange(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        assert "NYSE" in detector.known_exchanges

    def test_register_multiple_exchanges(self):
        detector = ExchangePartitionDetector()
        for ex in ["NYSE", "NASDAQ", "HKEX"]:
            detector.register(ex)
        assert len(detector.known_exchanges) == 3


class TestDetectPartition:
    def test_no_partition_all_reachable(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        detector.register("NASDAQ")
        result = detector.detect_partition({"NYSE", "NASDAQ"})
        assert result == []

    def test_full_partition_none_reachable(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        detector.register("NASDAQ")
        result = detector.detect_partition(set())
        assert set(result) == {"NYSE", "NASDAQ"}

    def test_partial_partition(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        detector.register("NASDAQ")
        detector.register("HKEX")
        result = detector.detect_partition({"NYSE"})
        assert set(result) == {"NASDAQ", "HKEX"}

    def test_no_known_exchanges_empty_result(self):
        detector = ExchangePartitionDetector()
        result = detector.detect_partition({"NYSE"})
        assert result == []

    def test_unknown_reachable_ignored(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        result = detector.detect_partition({"NYSE", "UNKNOWN_EXCHANGE"})
        assert result == []


class TestIsPartitioned:
    def test_not_partitioned_all_reachable(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        assert detector.is_partitioned({"NYSE"}) is False

    def test_partitioned_some_unreachable(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        detector.register("NASDAQ")
        assert detector.is_partitioned({"NYSE"}) is True

    def test_not_partitioned_no_known_exchanges(self):
        detector = ExchangePartitionDetector()
        assert detector.is_partitioned(set()) is False

    def test_partitioned_none_reachable(self):
        detector = ExchangePartitionDetector()
        detector.register("NYSE")
        assert detector.is_partitioned(set()) is True

    def test_boundary_single_exchange_reachable(self):
        detector = ExchangePartitionDetector()
        detector.register("SSE")
        assert detector.is_partitioned({"SSE"}) is False
        assert detector.is_partitioned(set()) is True
