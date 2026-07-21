# [A_test] module_id: MOD-GOV_vector_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_vector_bridge
# [INVARIANTS] no_vms_returns_degraded;exception_returns_degraded;results_sorted_by_score
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_vector_bridge.py
# [TTL] task_bound

from unittest.mock import MagicMock

from zephyr.autonomy_core.context.vector_bridge import (
    VectorBridge,
    VectorSearchResponse,
    VectorSearchResult,
    VMSSearchProtocol,
)


class TestVectorSearchResult:
    def test_defaults(self):
        r = VectorSearchResult()
        assert r.content == ""
        assert r.score == 0.0
        assert r.metadata == {}
        assert r.collection == ""

    def test_custom(self):
        r = VectorSearchResult(content="hello", score=0.95, metadata={"k": "v"}, collection="test")
        assert r.content == "hello"
        assert r.score == 0.95


class TestVectorSearchResponse:
    def test_defaults(self):
        r = VectorSearchResponse()
        assert r.results == []
        assert r.total_found == 0
        assert r.degraded is False
        assert r.error == ""

    def test_degraded_response(self):
        r = VectorSearchResponse(degraded=True, error="timeout")
        assert r.degraded is True
        assert r.error == "timeout"


class TestVectorBridgeNoVms:
    def test_no_vms_returns_degraded(self):
        bridge = VectorBridge()
        resp = bridge.search("ke_entries", "test query")
        assert resp.degraded is True
        assert resp.total_found == 0
        assert "not available" in resp.error

    def test_is_available_false(self):
        bridge = VectorBridge()
        assert bridge.is_available is False

    def test_search_all_collections_no_vms(self):
        bridge = VectorBridge()
        responses = bridge.search_all_collections("test")
        assert len(responses) == len(VectorBridge.CT_CE_VMS_COLLECTIONS)
        for r in responses:
            assert r.degraded is True


class TestVectorBridgeWithVms:
    def _make_vms(self, return_value=None):
        vms = MagicMock()
        vms.search.return_value = return_value or []
        return vms

    def test_is_available_true(self):
        bridge = VectorBridge(self._make_vms())
        assert bridge.is_available is True

    def test_default_timeout(self):
        bridge = VectorBridge(self._make_vms())
        assert bridge.timeout_s == 5.0

    def test_custom_timeout(self):
        bridge = VectorBridge(self._make_vms(), default_timeout_s=10.0)
        assert bridge.timeout_s == 10.0

    def test_successful_search(self):
        vms = self._make_vms(
            [
                {"content": "result1", "score": 0.9, "metadata": {"k": "v"}},
                {"content": "result2", "score": 0.7, "metadata": {}},
            ]
        )
        bridge = VectorBridge(vms)
        resp = bridge.search("ke_entries", "test query", top_k=5)
        assert resp.degraded is False
        assert resp.total_found == 2
        assert len(resp.results) == 2
        assert resp.collection == "ke_entries"

    def test_results_sorted_by_score(self):
        vms = self._make_vms(
            [
                {"content": "low", "score": 0.3},
                {"content": "high", "score": 0.9},
                {"content": "mid", "score": 0.6},
            ]
        )
        bridge = VectorBridge(vms)
        resp = bridge.search("test", "q")
        scores = [r.score for r in resp.results]
        assert scores == sorted(scores, reverse=True)

    def test_string_results(self):
        vms = self._make_vms(["plain text result"])
        bridge = VectorBridge(vms)
        resp = bridge.search("test", "q")
        assert resp.results[0].content == "plain text result"

    def test_exception_returns_degraded(self):
        vms = MagicMock()
        vms.search.side_effect = RuntimeError("VMS down")
        bridge = VectorBridge(vms)
        resp = bridge.search("test", "q")
        assert resp.degraded is True
        assert "VMS down" in resp.error

    def test_search_all_collections(self):
        vms = self._make_vms([{"content": "r", "score": 0.5}])
        bridge = VectorBridge(vms)
        responses = bridge.search_all_collections("test")
        assert len(responses) == len(VectorBridge.CT_CE_VMS_COLLECTIONS)
        for r in responses:
            assert r.degraded is False

    def test_elapsed_ms_recorded(self):
        vms = self._make_vms([])
        bridge = VectorBridge(vms)
        resp = bridge.search("test", "q")
        assert resp.elapsed_ms >= 0

    def test_collection_in_response(self):
        vms = self._make_vms([])
        bridge = VectorBridge(vms)
        resp = bridge.search("my_collection", "q")
        assert resp.collection == "my_collection"


class TestVMSSearchProtocol:
    def test_protocol_check(self):
        class GoodVMS:
            def search(self, collection, query, top_k):
                return []

        assert isinstance(GoodVMS(), VMSSearchProtocol)

    def test_protocol_fails_for_bad_impl(self):
        class BadVMS:
            pass

        assert not isinstance(BadVMS(), VMSSearchProtocol)
