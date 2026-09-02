# [A_test] module_id: MOD-INF-051 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [BLUEPRINT] MOD-INF-051 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/10_llm_infrastructure.md | §4-Phase1
# [MODULE] tests.model.test_llm_runtime_gateway_phase1
# [DOMAIN] D_INTEGRATION
# [INVARIANTS] 全 mock 通道/预算门/路由器——禁真实网络/真实 LLM 调用；不改写既有测试断言
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] testing
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/model/test_llm_runtime_gateway_phase1.py
# [TTL] task_bound

"""
test_llm_runtime_gateway_phase1.py — 10号文 §4 Phase 1.1 门面 complexity/max_cost 路由分发单测
=================================================================================================
全 mock（假通道 + 假预算门 + 假/真 ModelRouter，零网络零真实 LLM）。覆盖：
- 默认 L2：complexity=simple/moderate -> ECONOMY/MINIMAL tier -> 本地通道优先（Ollama）
- 显式升 L3：complexity=complex -> STANDARD tier -> API 通道优先（DeepSeek）
- L2/L3 切换对调用方透明：同一 infer 签名，本地失败自动落到 API（status=ok 不变）
- 分发跟 ModelRouter 决策走（假路由定 tier 即定走向），max_cost 透传 max_cost_per_1k
- 缺省不传 complexity -> 不触发路由分发（E1 裁定降级链语义零变化）
- 非法 complexity -> ValueError（fail-closed 输入校验）
- LLMDeg 双闸：L1 非关键 complex -> 本地优先；L4 关键 complex -> 仅本地；
  L4 显式 API 钉死 + complexity -> blocked
- 闸门完整：预算 DENY / LSG 入口判决在 complexity 分发路径同径阻断（L2 无旁路）
- channel 显式钉死优先于 complexity 分发
"""

from __future__ import annotations

import sqlite3
from unittest.mock import patch

import pytest

gw_mod = pytest.importorskip("zephyr.integration.llm_runtime_gateway")
budget_models = pytest.importorskip("zephyr.governance.ops_governance.budget_models")
router_mod = pytest.importorskip("zephyr.governance.intelligence_governance.model_router")

LLMRuntimeGateway = gw_mod.LLMRuntimeGateway
LSGBlockedError = gw_mod.LSGBlockedError
BudgetLevel = budget_models.BudgetLevel
GateDecision = budget_models.GateDecision
GateResult = budget_models.GateResult
ModelTier = budget_models.ModelTier
TaskComplexity = router_mod.TaskComplexity
RoutingDecision = router_mod.RoutingDecision


class _FakeClient:
    """假通道客户端（ask/model 协议；exc 非空时调用即抛）。"""

    def __init__(self, model: str = "fake-model", reply: str = "fake reply", exc: Exception | None = None):
        self.model = model
        self._reply = reply
        self._exc = exc
        self.calls = 0

    def ask(self, prompt: str, *, system: str = "", temperature=None, max_tokens=None) -> str:
        self.calls += 1
        if self._exc is not None:
            raise self._exc
        return self._reply


class _FakeBudgetEngine:
    """假预算门（BudgetEngineProtocol 最小面）：可配 DENY/ALLOW×BudgetLevel。"""

    def __init__(
        self,
        decision: GateDecision = GateDecision.ALLOW,
        level: BudgetLevel = BudgetLevel.L0_NORMAL,
        reason: str = "OK",
    ):
        self._decision = decision
        self._level = level
        self._reason = reason
        self.calls: list[dict] = []
        self.recorded: list[tuple] = []

    def pre_flight_check(self, request_id, estimated_tokens=0, estimated_cost=0.0, prompt=""):
        self.calls.append({"request_id": request_id, "estimated_tokens": estimated_tokens})
        return GateResult(
            request_id=request_id,
            decision=self._decision,
            reason=self._reason,
            budget_level=self._level,
        )

    def get_model_router_recommendation(self):
        return (ModelTier.PREMIUM, 16000)

    def record_consumption(self, policy_id, tokens, cost, time_minutes):
        self.recorded.append((policy_id, tokens, cost, time_minutes))


class _FakeRouter:
    """假 ModelRouter：固定返回指定 tier 的 RoutingDecision，记录入参（验证 max_cost 透传）。"""

    def __init__(self, tier: ModelTier = ModelTier.ECONOMY):
        self._tier = tier
        self.calls: list[dict] = []

    def route(
        self,
        complexity=TaskComplexity.MODERATE,
        tier=None,
        max_cost_per_1k=float("inf"),
        prefer_provider="",
    ) -> RoutingDecision:
        self.calls.append(
            {
                "complexity": complexity,
                "tier": tier,
                "max_cost_per_1k": max_cost_per_1k,
                "prefer_provider": prefer_provider,
            }
        )
        return RoutingDecision(
            model_key="fake:model",
            provider="fake",
            tier=tier or self._tier,
            reason="fake-router",
            performance_score=0.0,
        )


def _clients():
    return {
        "deepseek": _FakeClient(model="deepseek-v4-flash", reply="ok-deepseek"),
        "qwen": _FakeClient(model="qwen-flash", reply="ok-qwen"),
        "ollama": _FakeClient(model="qwen3:8b", reply="ok-ollama"),
    }


def _make_gateway(tmp_path, clients, **kw):
    kw.setdefault("budget_engine", _FakeBudgetEngine())
    return LLMRuntimeGateway(clients=clients, db_path=tmp_path / "test.db", lsg_enabled=False, **kw)


def _rows(db_path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute("SELECT task_type, model, provider, status, error FROM llm_call_log ORDER BY id").fetchall()
    finally:
        conn.close()


class TestComplexityFacadeDispatch:
    """Phase 1.1：complexity 经 ModelRouter 决策分发 L2/L3——默认 L2、显式升 L3。"""

    def test_simple_complexity_defaults_to_local_l2(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("tag_completion", "打标签", complexity="simple")
        assert r.status == "ok" and r.provider == "ollama"
        assert clients["ollama"].calls == 1
        assert clients["deepseek"].calls == 0 and clients["qwen"].calls == 0

    def test_moderate_complexity_defaults_to_local_l2(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("summary_extraction", "压缩文本", complexity=TaskComplexity.MODERATE)
        assert r.status == "ok" and r.provider == "ollama"
        assert clients["deepseek"].calls == 0

    def test_complex_complexity_upgrades_to_api_chain(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("reflection_l3", "深度反思", complexity="complex")
        assert r.status == "ok" and r.provider == "deepseek"
        assert clients["deepseek"].calls == 1 and clients["ollama"].calls == 0

    def test_local_failure_falls_back_to_api_transparently(self, tmp_path):
        """L2/L3 切换对调用方透明：同一签名，本地失败自动落 API，调用方只见 status=ok。"""
        clients = _clients()
        clients["ollama"] = _FakeClient(model="qwen3:8b", exc=RuntimeError("ollama down"))
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("tag_completion", "打标签", complexity="simple")
        assert r.status == "ok" and r.provider == "deepseek"
        assert clients["ollama"].calls == 1 and clients["deepseek"].calls == 1

    def test_api_failure_on_complex_falls_back_to_local(self, tmp_path):
        clients = _clients()
        clients["deepseek"] = _FakeClient(exc=RuntimeError("deepseek 402"))
        clients["qwen"] = _FakeClient(exc=RuntimeError("qwen down"))
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("reflection_l3", "深度反思", complexity="complex")
        assert r.status == "ok" and r.provider == "ollama"
        assert clients["deepseek"].calls == 1 and clients["qwen"].calls == 1

    def test_dispatch_follows_router_decision_not_raw_complexity(self, tmp_path):
        """分发跟 ModelRouter 决策走：complex 但决策 ECONOMY -> 本地优先。"""
        clients = _clients()
        router = _FakeRouter(tier=ModelTier.ECONOMY)
        gw = _make_gateway(tmp_path, clients, model_router=router)
        r = gw.infer("reflection_l3", "深度反思", complexity="complex")
        assert r.status == "ok" and r.provider == "ollama"
        assert clients["deepseek"].calls == 0

    def test_premium_decision_on_simple_upgrades_to_api(self, tmp_path):
        """反向同理：simple 但决策 PREMIUM -> API 优先。"""
        clients = _clients()
        router = _FakeRouter(tier=ModelTier.PREMIUM)
        gw = _make_gateway(tmp_path, clients, model_router=router)
        r = gw.infer("tag_completion", "打标签", complexity="simple")
        assert r.status == "ok" and r.provider == "deepseek"
        assert clients["ollama"].calls == 0

    def test_max_cost_passed_through_to_router(self, tmp_path):
        clients = _clients()
        router = _FakeRouter(tier=ModelTier.ECONOMY)
        gw = _make_gateway(tmp_path, clients, model_router=router)
        gw.infer("tag_completion", "打标签", complexity="simple", max_cost=0.001)
        assert router.calls and router.calls[0]["max_cost_per_1k"] == 0.001

    def test_no_complexity_keeps_e1_chain_and_skips_router(self, tmp_path):
        """缺省不传 complexity：E1 裁定降级链语义零变化，且不经 ModelRouter 分发。"""
        clients = _clients()
        router = _FakeRouter()
        gw = _make_gateway(tmp_path, clients, model_router=router)
        r = gw.infer("summary_extraction", "压缩文本")
        assert r.status == "ok" and r.provider == "deepseek"  # E1 链 API 优先
        assert router.calls == []

    def test_invalid_complexity_value_error(self, tmp_path):
        gw = _make_gateway(tmp_path, _clients())
        with pytest.raises(ValueError, match="未知复杂度"):
            gw.infer("tag_completion", "打标签", complexity="galaxy-brain")

    def test_dispatch_result_recorded_in_db(self, tmp_path):
        db = tmp_path / "test.db"
        gw = _make_gateway(tmp_path, _clients())
        gw.infer("tag_completion", "打标签", complexity="simple")
        rows = _rows(db)
        assert len(rows) == 1 and rows[0][2] == "ollama" and rows[0][3] == "ok"


class TestComplexityWithLLMDeg:
    """LLMDeg-0~4 与 complexity 分发双闸同源（10号文 §3.6 降级表走向）。"""

    def test_llmdeg1_complex_noncritical_goes_local_first(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L1_WARNING))
        r = gw.infer("summary_extraction", "文本", complexity="complex")  # 非关键
        assert r.provider == "ollama"  # LLMDeg-1：非关键 API->本地降级（先于 tier 的 API 优先）
        assert clients["deepseek"].calls == 0

    def test_llmdeg4_complex_critical_local_only(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L4_EMERGENCY))
        r = gw.infer("reflection_l3", "深度反思", complexity="complex", critical=True)
        assert gw.last_llmdeg == 4
        assert r.provider == "ollama"  # LLMDeg-4：阻断一切 API，仅本地
        assert clients["deepseek"].calls == 0 and clients["qwen"].calls == 0

    def test_llmdeg4_explicit_api_pin_blocked_with_complexity(self, tmp_path):
        db = tmp_path / "test.db"
        clients = _clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L4_EMERGENCY))
        r = gw.infer("reflection_l3", "深度反思", complexity="complex", channel="deepseek")
        assert r.status == "blocked" and "llmdeg-4" in r.error
        assert clients["deepseek"].calls == 0
        assert _rows(db)[0][3] == "blocked"

    def test_llmdeg0_complex_uses_api(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients, budget_engine=_FakeBudgetEngine(level=BudgetLevel.L0_NORMAL))
        r = gw.infer("reflection_l3", "深度反思", complexity="complex")
        assert r.provider == "deepseek"


class TestComplexityGatesIntact:
    """闸门完整：complexity 分发路径同过预算硬门 + LSG 入口闸门（L2 无旁路）。"""

    def test_budget_deny_blocks_complexity_dispatch(self, tmp_path):
        clients = _clients()
        engine = _FakeBudgetEngine(decision=GateDecision.DENY, level=BudgetLevel.L5_HARD_STOP, reason="daily 120%")
        gw = _make_gateway(tmp_path, clients, budget_engine=engine)
        r = gw.infer("tag_completion", "打标签", complexity="simple")
        assert r.status == "blocked" and "budget_denied" in r.error
        assert gw.last_llmdeg == 4
        assert all(c.calls == 0 for c in clients.values())

    def test_lsg_entry_block_on_complexity_path_no_channel_calls(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients)
        with patch.object(gw_mod, "enforce_input", side_effect=LSGBlockedError("LSG 输入判决 block")):
            r = gw.infer("tag_completion", "恶意 prompt", complexity="simple")
        assert r.status == "blocked"
        assert all(c.calls == 0 for c in clients.values())  # L2 路径同过入口闸门

    def test_explicit_channel_overrides_complexity(self, tmp_path):
        clients = _clients()
        gw = _make_gateway(tmp_path, clients)
        r = gw.infer("summary_extraction", "文本", complexity="simple", channel="qwen")
        assert r.status == "ok" and r.provider == "qwen"
        assert clients["ollama"].calls == 0 and clients["deepseek"].calls == 0
