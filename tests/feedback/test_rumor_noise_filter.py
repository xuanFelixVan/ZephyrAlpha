# [A_test] module_id: SRC-TST-1497 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_rumor_noise_filter
# [INVARIANTS] min_sources>=1; CONFIRMED only when unique_sources>=min_sources
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_rumor_noise_filter.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.rumor_noise_filter import (
    RumorNoiseFilter,
    SignalCredibility,
)


class TestSignalCredibility:
    def test_enum_values(self):
        assert SignalCredibility.CONFIRMED == "CONFIRMED"
        assert SignalCredibility.UNVERIFIED == "UNVERIFIED"
        assert SignalCredibility.RUMOR == "RUMOR"
        assert SignalCredibility.FALSE == "FALSE"


class TestRumorNoiseFilterInstantiation:
    def test_default_params(self):
        obj = RumorNoiseFilter()
        assert obj.min_sources == 2
        assert obj.corroboration_window == 300.0
        assert obj.pending_signals == {}

    def test_custom_params(self):
        obj = RumorNoiseFilter(min_sources=3, corroboration_window=600.0)
        assert obj.min_sources == 3
        assert obj.corroboration_window == 600.0


class TestRumorNoiseFilterIngestSignal:
    def test_first_signal_returns_unverified(self):
        obj = RumorNoiseFilter(min_sources=2)
        result = obj.ingest_signal("sig-1", "source-a", "content")
        assert result == SignalCredibility.UNVERIFIED

    def test_second_source_confirms(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        result = obj.ingest_signal("sig-1", "source-b", "content")
        assert result == SignalCredibility.CONFIRMED

    def test_same_source_does_not_confirm(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        result = obj.ingest_signal("sig-1", "source-a", "content")
        assert result == SignalCredibility.UNVERIFIED

    def test_min_sources_three(self):
        obj = RumorNoiseFilter(min_sources=3)
        obj.ingest_signal("sig-1", "source-a", "content")
        obj.ingest_signal("sig-1", "source-b", "content")
        result = obj.ingest_signal("sig-1", "source-c", "content")
        assert result == SignalCredibility.CONFIRMED

    def test_min_sources_three_insufficient(self):
        obj = RumorNoiseFilter(min_sources=3)
        obj.ingest_signal("sig-1", "source-a", "content")
        result = obj.ingest_signal("sig-1", "source-b", "content")
        assert result == SignalCredibility.UNVERIFIED

    def test_different_signals_independent(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        result = obj.ingest_signal("sig-2", "source-b", "content")
        assert result == SignalCredibility.UNVERIFIED


class TestRumorNoiseFilterCanActOn:
    def test_cannot_act_on_unknown_signal(self):
        obj = RumorNoiseFilter(min_sources=2)
        assert obj.can_act_on("unknown") is False

    def test_can_act_on_confirmed_signal(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        obj.ingest_signal("sig-1", "source-b", "content")
        assert obj.can_act_on("sig-1") is True

    def test_cannot_act_on_unverified_signal(self):
        obj = RumorNoiseFilter(min_sources=3)
        obj.ingest_signal("sig-1", "source-a", "content")
        assert obj.can_act_on("sig-1") is False


class TestRumorNoiseFilterGetUnverifiedCount:
    def test_no_signals_zero_count(self):
        obj = RumorNoiseFilter(min_sources=2)
        assert obj.get_unverified_count() == 0

    def test_unverified_count_single_signal(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        assert obj.get_unverified_count() == 1

    def test_confirmed_not_counted(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        obj.ingest_signal("sig-1", "source-b", "content")
        assert obj.get_unverified_count() == 0

    def test_mixed_signals(self):
        obj = RumorNoiseFilter(min_sources=2)
        obj.ingest_signal("sig-1", "source-a", "content")
        obj.ingest_signal("sig-2", "source-a", "content")
        obj.ingest_signal("sig-2", "source-b", "content")
        assert obj.get_unverified_count() == 1
