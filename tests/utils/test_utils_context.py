# [A_test] module_id: MOD-GOV_utils_context | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_utils_context

# [INVARIANTS] RequestContext不可变;contextvars传播;set_context返回Token

# [MODIFY-GUARD] context.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_utils_context.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.utils.context import (
    RequestContext,
    current_context,
    get_request_id,
    set_context,
    set_request_id,
)


@pytest.fixture(autouse=True)
def _clear_context():
    ctx = current_context()
    if ctx is not None:
        from zephyr.shared.utils.context import _current_context

        _current_context.set(None)
    yield
    ctx2 = current_context()
    if ctx2 is not None:
        from zephyr.shared.utils.context import _current_context

        _current_context.set(None)


class TestRequestContext:
    def test_default_values(self):
        ctx = RequestContext()
        assert ctx.tenant_id == "default"
        assert ctx.session_id == ""
        assert ctx.agent_id == ""
        assert ctx.priority == 5
        assert ctx.trace_id != ""
        assert ctx.span_id != ""

    def test_custom_values(self):
        ctx = RequestContext(
            tenant_id="t-001",
            session_id="s-abc",
            agent_id="agent-build",
            priority=1,
        )
        assert ctx.tenant_id == "t-001"
        assert ctx.session_id == "s-abc"
        assert ctx.agent_id == "agent-build"
        assert ctx.priority == 1

    def test_frozen(self):
        ctx = RequestContext()
        with pytest.raises(AttributeError):
            ctx.tenant_id = "changed"

    def test_replace_creates_derived(self):
        ctx = RequestContext(tenant_id="original", priority=5)
        derived = ctx.replace(tenant_id="derived", priority=1)
        assert derived.tenant_id == "derived"
        assert derived.priority == 1
        assert ctx.tenant_id == "original"

    def test_new_span_preserves_trace(self):
        ctx = RequestContext()
        new = ctx.new_span("child")
        assert new.trace_id == ctx.trace_id
        assert new.span_id != ctx.span_id
        assert "child" in new.span_id

    def test_to_dict(self):
        ctx = RequestContext(tenant_id="t-001", request_id="req-123")
        d = ctx.to_dict()
        assert d["tenant_id"] == "t-001"
        assert d["request_id"] == "req-123"
        assert "trace_id" in d
        assert "span_id" in d

    def test_extra_field(self):
        ctx = RequestContext(extra={"custom": "value"})
        assert ctx.extra == {"custom": "value"}


class TestCurrentContext:
    def test_initially_none(self):
        assert current_context() is None

    def test_set_and_get(self):
        ctx = RequestContext(tenant_id="test-tenant")
        token = set_context(ctx)
        assert current_context() is ctx
        from zephyr.shared.utils.context import _current_context

        _current_context.reset(token)

    def test_set_and_reset(self):
        ctx = RequestContext(tenant_id="temp")
        token = set_context(ctx)
        from zephyr.shared.utils.context import _current_context

        _current_context.reset(token)
        assert current_context() is None


class TestGetRequestId:
    def test_without_context_generates_id(self):
        rid = get_request_id()
        assert isinstance(rid, str)
        assert len(rid) > 0

    def test_with_context_returns_set_id(self):
        ctx = RequestContext(request_id="req-456")
        token = set_context(ctx)
        assert get_request_id() == "req-456"
        from zephyr.shared.utils.context import _current_context

        _current_context.reset(token)


class TestSetRequestId:
    def test_sets_context_with_request_id(self):
        set_request_id("manual-req-789")
        ctx = current_context()
        assert ctx is not None
        assert ctx.request_id == "manual-req-789"
