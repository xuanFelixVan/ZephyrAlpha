# [A_test] module_id: MOD-GOV_e_exchange_partition_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_exchange_partition_detector
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.exchange_partition_detector import ExchangePartitionDetector


class TestExchangePartitionDetectorInit:
    def test_default_state(self):
        epd = ExchangePartitionDetector()
        assert epd._known_exchanges == set()


class TestExchangePartitionDetectorRegister:
    def test_adds_single_exchange(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        assert epd._known_exchanges == {"binance"}

    def test_adds_multiple_exchanges(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        epd.register("ftx")
        epd.register("coinbase")
        assert len(epd._known_exchanges) == 3

    def test_duplicate_is_noop(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        epd.register("binance")
        assert len(epd._known_exchanges) == 1


class TestExchangePartitionDetectorDetectPartition:
    def test_no_registered_exchanges(self):
        epd = ExchangePartitionDetector()
        result = epd.detect_partition({"binance"})
        assert result == []

    def test_all_reachable(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        epd.register("ftx")
        result = epd.detect_partition({"binance", "ftx"})
        assert result == []

    def test_some_unreachable(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        epd.register("ftx")
        epd.register("coinbase")
        result = epd.detect_partition({"binance"})
        assert set(result) == {"ftx", "coinbase"}


class TestExchangePartitionDetectorIsPartitioned:
    def test_no_registered_not_partitioned(self):
        epd = ExchangePartitionDetector()
        assert epd.is_partitioned({"binance"}) is False

    def test_all_reachable_not_partitioned(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        assert epd.is_partitioned({"binance"}) is False

    def test_partial_reachable_is_partitioned(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        epd.register("ftx")
        assert epd.is_partitioned({"binance"}) is True

    def test_completely_unreachable_is_partitioned(self):
        epd = ExchangePartitionDetector()
        epd.register("binance")
        assert epd.is_partitioned(set()) is True
