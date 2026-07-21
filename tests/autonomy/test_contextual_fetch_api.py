# [A_test] module_id: MOD-GOV_contextual_fetch_api | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_contextual_fetch_api
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_contextual_fetch_api.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.context.contextual_fetch_api import (
    ContextualFetchAPI,
    FetchSession,
)


class TestFetchSession:
    def test_default_sources(self):
        session = FetchSession(session_id="S-001", context_type="full", token_count=500)
        assert session.sources == []

    def test_custom_sources(self):
        session = FetchSession(
            session_id="S-002",
            context_type="summary",
            token_count=200,
            sources=["KE-001", "KE-002"],
        )
        assert session.sources == ["KE-001", "KE-002"]

    def test_fields_assigned(self):
        session = FetchSession(session_id="S-003", context_type="full", token_count=300)
        assert session.session_id == "S-003"
        assert session.context_type == "full"
        assert session.token_count == 300


class TestContextualFetchAPIInit:
    def test_instantiation(self):
        api = ContextualFetchAPI()
        assert hasattr(api, "fetch")


class TestContextualFetchAPIFetch:
    def test_fetch_full_context(self):
        api = ContextualFetchAPI()
        session = api.fetch("S-100", context_type="full")
        assert isinstance(session, FetchSession)
        assert session.session_id == "S-100"
        assert session.context_type == "full"

    def test_fetch_summary_context(self):
        api = ContextualFetchAPI()
        session = api.fetch("S-101", context_type="summary")
        assert session.context_type == "summary"

    def test_fetch_default_context_type(self):
        api = ContextualFetchAPI()
        session = api.fetch("S-102")
        assert session.context_type == "full"

    def test_fetch_returns_token_count(self):
        api = ContextualFetchAPI()
        session = api.fetch("S-103")
        assert session.token_count == 500

    def test_fetch_returns_sources(self):
        api = ContextualFetchAPI()
        session = api.fetch("S-104")
        assert session.sources == ["KE-001", "CT-001"]

    def test_fetch_empty_session_id(self):
        api = ContextualFetchAPI()
        session = api.fetch("")
        assert session.session_id == ""

    def test_fetch_unicode_session_id(self):
        api = ContextualFetchAPI()
        session = api.fetch("会话-001")
        assert session.session_id == "会话-001"

    def test_fetch_preserves_context_type_value(self):
        api = ContextualFetchAPI()
        session = api.fetch("S-105", context_type="custom_type")
        assert session.context_type == "custom_type"
