# [A_test] module_id: SRC-TST-0305 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_alert_router
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_alert_router.py -q

from datetime import UTC, datetime
from unittest.mock import patch

from zephyr.ops.actors.alert_router import Alert, AlertRouter


class TestAlertInstantiation:
    def test_required_fields_populated(self):
        alert = Alert(
            alert_id="a1",
            module_id="MOD-X",
            detector_id="det-001",
            drift_dimension="D5",
            severity="HIGH",
            tier="P0",
            message="test alert",
        )
        assert alert.alert_id == "a1"
        assert alert.module_id == "MOD-X"
        assert alert.detector_id == "det-001"
        assert alert.drift_dimension == "D5"
        assert alert.severity == "HIGH"
        assert alert.tier == "P0"
        assert alert.message == "test alert"

    def test_default_optional_fields(self):
        alert = Alert(
            alert_id="a2",
            module_id="MOD-Y",
            detector_id="det-002",
            drift_dimension="D3",
            severity="LOW",
            tier="P2",
            message="default check",
        )
        assert alert.timestamp == ""
        assert alert.ack_required is False
        assert alert.acked is False
        assert alert.acked_at is None

    def test_explicit_optional_fields(self):
        now_iso = datetime.now(UTC).isoformat()
        alert = Alert(
            alert_id="a3",
            module_id="MOD-Z",
            detector_id="det-003",
            drift_dimension="contract_violation",
            severity="HIGH",
            tier="P0_CRITICAL",
            message="explicit fields",
            timestamp=now_iso,
            ack_required=True,
            acked=True,
            acked_at=now_iso,
        )
        assert alert.timestamp == now_iso
        assert alert.ack_required is True
        assert alert.acked is True
        assert alert.acked_at == now_iso


class TestAlertRouterInstantiation:
    def test_init_creates_empty_sent_alerts(self):
        router = AlertRouter()
        assert router._sent_alerts == {}

    def test_init_focus_start_is_none(self):
        router = AlertRouter()
        assert router._focus_start is None

    def test_class_constants(self):
        assert AlertRouter.DEDUP_WINDOW_HOURS == 6
        assert AlertRouter.PERSISTENT_THRESHOLD == 3
        assert AlertRouter.SILENCE_NIGHT_START == 22
        assert AlertRouter.SILENCE_NIGHT_END == 8
        assert AlertRouter.FOCUS_TIME_HOURS == 2


class TestClassify:
    def test_high_severity_contract_returns_p0_critical(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "contract_violation", "HIGH") == "P0_CRITICAL"

    def test_high_severity_security_returns_p0_critical(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "security_breach", "HIGH") == "P0_CRITICAL"

    def test_high_severity_p0_keyword_returns_p0_critical(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "p0_issue", "HIGH") == "P0_CRITICAL"

    def test_high_severity_ssot_returns_p0_critical(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "ssot_drift", "HIGH") == "P0_CRITICAL"

    def test_high_severity_other_returns_p0(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "performance", "HIGH") == "P0"

    def test_medium_severity_returns_p1(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "D5", "MEDIUM") == "P1"

    def test_low_severity_returns_p2(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "D5", "LOW") == "P2"

    def test_boundary_severity_unknown_returns_p2(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "D5", "CRITICAL") == "P2"

    def test_boundary_empty_severity_returns_p2(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "D5", "") == "P2"

    def test_boundary_contract_keyword_case_insensitive(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "CONTRACT_DRIFT", "HIGH") == "P0_CRITICAL"

    def test_boundary_security_keyword_embedded(self):
        router = AlertRouter()
        assert router.classify("MOD-X", "data_security_layer", "HIGH") == "P0_CRITICAL"


class TestShouldSilence:
    def test_daytime_weekday_not_silenced(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 20, 14, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is False

    def test_night_hours_silenced(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 20, 23, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is True

    def test_weekend_night_silenced(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 23, 23, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is True

    def test_weekend_daytime_not_silenced(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 23, 14, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is False

    def test_focus_time_active_night_silenced(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 20, 23, 30, 0, tzinfo=UTC)
        router._focus_start = datetime(2026, 5, 20, 23, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is True

    def test_focus_time_expired_not_silenced(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 20, 17, 0, 0, tzinfo=UTC)
        router._focus_start = datetime(2026, 5, 20, 14, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is False

    def test_boundary_hour_exactly_at_silence_start(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 20, 22, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is True

    def test_boundary_hour_exactly_at_silence_end(self):
        router = AlertRouter()
        fake_now = datetime(2026, 5, 20, 8, 0, 0, tzinfo=UTC)
        with patch("zephyr.observability.feedback_loop.actors.alert_router.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            result = router.should_silence()
        assert result is False


class TestStartFocusTime:
    def test_sets_focus_start(self):
        router = AlertRouter()
        assert router._focus_start is None
        router.start_focus_time()
        assert router._focus_start is not None

    def test_focus_start_is_utc_datetime(self):
        router = AlertRouter()
        router.start_focus_time()
        assert router._focus_start.tzinfo is not None


class TestShouldDeduplicate:
    def test_first_occurrence_not_deduplicated(self):
        router = AlertRouter()
        assert router.should_deduplicate("key-new") is False

    def test_second_occurrence_deduplicated(self):
        router = AlertRouter()
        router.record_alert("key-dup")
        assert router.should_deduplicate("key-dup") is True

    def test_persistent_threshold_not_deduplicated(self):
        router = AlertRouter()
        for _ in range(3):
            router.record_alert("key-persist")
        assert router.should_deduplicate("key-persist") is False

    def test_boundary_two_occurrences_still_deduplicated(self):
        router = AlertRouter()
        router.record_alert("key-two")
        router.record_alert("key-two")
        assert router.should_deduplicate("key-two") is True

    def test_boundary_four_occurrences_not_deduplicated(self):
        router = AlertRouter()
        for _ in range(4):
            router.record_alert("key-four")
        assert router.should_deduplicate("key-four") is False

    def test_different_keys_independent(self):
        router = AlertRouter()
        router.record_alert("key-a")
        assert router.should_deduplicate("key-b") is False
        assert router.should_deduplicate("key-a") is True


class TestRecordAlert:
    def test_records_new_key(self):
        router = AlertRouter()
        router.record_alert("key-rec")
        assert "key-rec" in router._sent_alerts
        assert len(router._sent_alerts["key-rec"]) == 1

    def test_appends_to_existing_key(self):
        router = AlertRouter()
        router.record_alert("key-multi")
        router.record_alert("key-multi")
        assert len(router._sent_alerts["key-multi"]) == 2

    def test_timestamp_is_utc(self):
        router = AlertRouter()
        router.record_alert("key-tz")
        ts = router._sent_alerts["key-tz"][0]
        assert ts.tzinfo is not None


class TestRoute:
    def _make_alert(
        self, alert_id="a1", tier="P0_CRITICAL", severity="HIGH", drift_dimension="contract_violation", message="test"
    ):
        return Alert(
            alert_id=alert_id,
            module_id="MOD-X",
            detector_id="det-001",
            drift_dimension=drift_dimension,
            severity=severity,
            tier=tier,
            message=message,
        )

    def test_route_p0_critical_always_routed(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P0_CRITICAL")
        with patch.object(router, "should_silence", return_value=True):
            actions = router.route([alert])
        assert len(actions) == 1
        assert actions[0]["tier"] == "P0_CRITICAL"

    def test_route_non_critical_silenced_at_night(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P1", severity="MEDIUM", drift_dimension="D5")
        with patch.object(router, "should_silence", return_value=True):
            actions = router.route([alert])
        assert len(actions) == 0

    def test_route_non_critical_not_silenced_daytime(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P1", severity="MEDIUM", drift_dimension="D5")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        assert len(actions) == 1

    def test_route_deduplicates_non_critical(self):
        router = AlertRouter()
        alert1 = self._make_alert(alert_id="a1", tier="P1", severity="MEDIUM", drift_dimension="D5")
        alert2 = self._make_alert(alert_id="a2", tier="P1", severity="MEDIUM", drift_dimension="D5")
        with patch.object(router, "should_silence", return_value=False):
            router.route([alert1])
            actions = router.route([alert2])
        assert len(actions) == 0

    def test_route_action_fields(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P0_CRITICAL")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        action = actions[0]
        assert action["alert_id"] == "a1"
        assert action["module_id"] == "MOD-X"
        assert action["tier"] == "P0_CRITICAL"
        assert action["channel"] == "feishu"
        assert action["ack_required"] is True
        assert action["escalation_timeout_min"] == 30
        assert action["aggregation"] == "none"

    def test_route_p0_aggregation_hourly(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P0", severity="HIGH", drift_dimension="performance")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        assert actions[0]["aggregation"] == "hourly"

    def test_route_p1_aggregation_daily(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P1", severity="MEDIUM", drift_dimension="D5")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        assert actions[0]["aggregation"] == "daily"

    def test_route_p2_aggregation_none(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P2", severity="LOW", drift_dimension="D5")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        assert actions[0]["aggregation"] == "none"

    def test_route_empty_list(self):
        router = AlertRouter()
        actions = router.route([])
        assert actions == []

    def test_route_p0_critical_ack_required_true(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P0_CRITICAL")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        assert actions[0]["ack_required"] is True

    def test_route_non_critical_ack_required_false(self):
        router = AlertRouter()
        alert = self._make_alert(tier="P1", severity="MEDIUM", drift_dimension="D5")
        with patch.object(router, "should_silence", return_value=False):
            actions = router.route([alert])
        assert actions[0]["ack_required"] is False


class TestBatchAlerts:
    def _make_alert(self, alert_id, tier="P2"):
        return Alert(
            alert_id=alert_id,
            module_id="MOD-X",
            detector_id="det",
            drift_dimension="D5",
            severity="LOW",
            tier=tier,
            message="msg",
        )

    def test_batch_ten_or_fewer_simple_batch(self):
        router = AlertRouter()
        alerts = [self._make_alert(f"a{i}") for i in range(10)]
        result = router.batch_alerts(alerts)
        assert result["batched"] is True
        assert result["count"] == 10
        assert result["top"] == []

    def test_batch_zero_alerts(self):
        router = AlertRouter()
        result = router.batch_alerts([])
        assert result["batched"] is True
        assert result["count"] == 0

    def test_batch_eleven_alerts_top3_and_remaining(self):
        router = AlertRouter()
        alerts = [self._make_alert(f"a{i}", tier="P1") for i in range(11)]
        result = router.batch_alerts(alerts)
        assert result["batched"] is True
        assert result["count"] == 11
        assert len(result["top3"]) == 3
        assert result["remaining"] == 8

    def test_batch_sorts_by_tier_priority(self):
        router = AlertRouter()
        alerts = [
            self._make_alert("low1", tier="P2"),
            self._make_alert("crit1", tier="P0_CRITICAL"),
            self._make_alert("mid1", tier="P1"),
            self._make_alert("low2", tier="P2"),
            self._make_alert("crit2", tier="P0_CRITICAL"),
            self._make_alert("mid2", tier="P1"),
            self._make_alert("low3", tier="P2"),
            self._make_alert("high1", tier="P0"),
            self._make_alert("low4", tier="P2"),
            self._make_alert("low5", tier="P2"),
            self._make_alert("low6", tier="P2"),
        ]
        result = router.batch_alerts(alerts)
        assert result["top3"][0]["tier"] == "P0_CRITICAL"
        assert result["top3"][1]["tier"] == "P0_CRITICAL"
        assert result["top3"][2]["tier"] == "P0"

    def test_boundary_exactly_ten_alerts(self):
        router = AlertRouter()
        alerts = [self._make_alert(f"a{i}") for i in range(10)]
        result = router.batch_alerts(alerts)
        assert "top3" not in result
        assert result["top"] == []

    def test_boundary_exactly_eleven_alerts(self):
        router = AlertRouter()
        alerts = [self._make_alert(f"a{i}") for i in range(11)]
        result = router.batch_alerts(alerts)
        assert "top3" in result
        assert result["remaining"] == 8

    def test_batch_top3_structure(self):
        router = AlertRouter()
        alerts = [self._make_alert(f"a{i}", tier="P1") for i in range(15)]
        result = router.batch_alerts(alerts)
        for entry in result["top3"]:
            assert "module_id" in entry
            assert "dimension" in entry
            assert "tier" in entry
