# [A_test] module_id: SRC-TST-1734 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_temporal_event_store
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.temporal_event_store
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_temporal_event_store.py
# [TTL] task_bound


from zephyr.feedback_loop.collectors.temporal_event_store import TemporalEventStore


class TestTemporalEventStoreInstantiation:
    def test_default_events_is_empty_list(self):
        tes = TemporalEventStore()
        assert tes.events == []

    def test_events_with_initial_data(self):
        initial = [{"ts": "2026-01-01", "type": "alert"}]
        tes = TemporalEventStore(events=initial)
        assert tes.events == initial
        assert len(tes.events) == 1


class TestTemporalEventStoreAppend:
    def test_append_single_event(self):
        tes = TemporalEventStore()
        tes.append({"ts": "2026-01-01T00:00:00", "type": "alert", "source": "cpu"})
        assert len(tes.events) == 1
        assert tes.events[0]["type"] == "alert"

    def test_append_multiple_events(self):
        tes = TemporalEventStore()
        tes.append({"ts": "2026-01-01", "type": "alert"})
        tes.append({"ts": "2026-01-02", "type": "resolve"})
        tes.append({"ts": "2026-01-03", "type": "alert"})
        assert len(tes.events) == 3

    def test_append_preserves_insertion_order(self):
        tes = TemporalEventStore()
        tes.append({"order": 1})
        tes.append({"order": 2})
        tes.append({"order": 3})
        orders = [e["order"] for e in tes.events]
        assert orders == [1, 2, 3]


class TestTemporalEventStoreBoundaries:
    def test_append_empty_dict(self):
        tes = TemporalEventStore()
        tes.append({})
        assert len(tes.events) == 1
        assert tes.events[0] == {}

    def test_append_event_with_nested_data(self):
        tes = TemporalEventStore()
        event = {"ts": "2026-01-01", "payload": {"key": "value", "nested": {"deep": True}}}
        tes.append(event)
        assert tes.events[0]["payload"]["nested"]["deep"] is True

    def test_append_shares_reference_with_initial_list(self):
        initial = [{"ts": "2026-01-01"}]
        tes = TemporalEventStore(events=initial)
        tes.append({"ts": "2026-01-02"})
        assert len(initial) == 2
        assert initial[1]["ts"] == "2026-01-02"
