# [A_test] module_id: SRC-TST-1347 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_otel_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_otel_adapter.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.otel_adapter import OTelAdapter


class TestOTelAdapter:
    def test_default_construction(self):
        adapter = OTelAdapter()
        assert adapter.endpoint == "http://localhost:4317"

    def test_custom_construction(self):
        adapter = OTelAdapter(endpoint="http://otel-collector:4317")
        assert adapter.endpoint == "http://otel-collector:4317"

    def test_endpoint_attribute_mutable(self):
        adapter = OTelAdapter()
        adapter.endpoint = "http://custom:4318"
        assert adapter.endpoint == "http://custom:4318"

    def test_endpoint_empty_string(self):
        adapter = OTelAdapter(endpoint="")
        assert adapter.endpoint == ""

    def test_endpoint_preserves_value(self):
        adapter = OTelAdapter(endpoint="https://telemetry.example.com:4317")
        assert adapter.endpoint == "https://telemetry.example.com:4317"
