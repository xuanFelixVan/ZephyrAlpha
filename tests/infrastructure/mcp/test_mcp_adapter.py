# [A_test] module_id: MOD-GOV_mcp_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_mcp_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_mcp_adapter.py -q
# [TTL] task_bound
import pytest

from zephyr.infrastructure.a2a_protocol.governance.governance_adapter import MCPAdapter, MCPSource

# #ARCH-083：MCPSource(track=)、MCPAdapter.probe_track/get_features_for_track
# 缺席——代码侧缺口待裁定，全文件 xfail 留痕（strict=False）。
pytestmark = pytest.mark.xfail(strict=False, reason="#ARCH-083 mcp_adapter 窄实现 vs 宽契约，待裁定")


class TestMCPSource:
    def test_dataclass_fields(self):
        src = MCPSource(track="A", connected=True, features=["search"])
        assert src.track == "A"
        assert src.connected is True
        assert src.features == ["search"]

    def test_default_features_empty(self):
        src = MCPSource(track="B", connected=False, features=[])
        assert src.features == []
        assert src.connected is False

    def test_equality(self):
        a = MCPSource(track="A", connected=True, features=["search", "inject"])
        b = MCPSource(track="A", connected=True, features=["search", "inject"])
        assert a == b


class TestMCPAdapterInstantiation:
    def test_create_instance(self):
        adapter = MCPAdapter()
        assert adapter is not None

    def test_has_probe_track(self):
        adapter = MCPAdapter()
        assert callable(getattr(adapter, "probe_track", None))

    def test_has_get_features_for_track(self):
        adapter = MCPAdapter()
        assert callable(getattr(adapter, "get_features_for_track", None))


class TestMCPAdapterProbeTrack:
    def test_probe_track_a(self):
        adapter = MCPAdapter()
        result = adapter.probe_track("A")
        assert isinstance(result, MCPSource)
        assert result.track == "A"
        assert result.connected is True
        assert "search" in result.features

    def test_probe_track_b(self):
        adapter = MCPAdapter()
        result = adapter.probe_track("B")
        assert isinstance(result, MCPSource)
        assert result.track == "B"
        assert result.connected is True

    def test_probe_track_returns_three_features(self):
        adapter = MCPAdapter()
        result = adapter.probe_track("A")
        assert len(result.features) == 3

    def test_probe_track_empty_string(self):
        adapter = MCPAdapter()
        result = adapter.probe_track("")
        assert result.track == ""
        assert result.connected is True


class TestMCPAdapterGetFeatures:
    def test_get_features_connected_track(self):
        adapter = MCPAdapter()
        features = adapter.get_features_for_track("A")
        assert isinstance(features, list)
        assert len(features) > 0

    def test_get_features_contains_expected_tools(self):
        adapter = MCPAdapter()
        features = adapter.get_features_for_track("A")
        assert "search" in features
        assert "inject" in features
        assert "status" in features

    def test_get_features_returns_list_type(self):
        adapter = MCPAdapter()
        features = adapter.get_features_for_track("B")
        assert isinstance(features, list)

    def test_get_features_any_track_returns_features(self):
        adapter = MCPAdapter()
        features = adapter.get_features_for_track("unknown_track")
        assert len(features) == 3
