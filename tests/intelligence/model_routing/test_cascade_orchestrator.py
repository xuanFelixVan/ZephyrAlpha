# [BLUEPRINT] MOD-MODEL_ROUTER_ORCH | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/11_evidence_skill_router.md | §
# [MODULE] tests.intelligence.model_routing.test_cascade_orchestrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""
test_cascade_orchestrator.py — 模型路由级联编排单测（11号文 §4.3，P1-1~P1-5）
====================================================================================
三基座（护照/JobMatcher/task_model_learner）与 MOD-INF-024 ModelRouter 全 fake，
零 LLM/DB/网络。覆盖验收点：
- P1-1：伪造/篡改护照验签失败被拒；不满足 required 的模型不进入 L2
- P1-2：融合排序与两源分数手工复算一致；样本=0 静态映射兜底生效
- P1-3：路由决策字段完整（reason+estimated_cost_per_1k+performance_score）
- P1-4：L1/L2/L3 逐段故障注入——每次故障均有降级产物+告警，不中断路由返回
- P1-5：12 类规则命中；时段受限本地only；配置变更不改代码；
  风控类任务不可降级性（L3 故障注入仍落外部 API，不落本地/规则引擎）
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
import yaml

orch_mod = pytest.importorskip("zephyr.intelligence.model_routing.cascade_orchestrator")
budget_models = pytest.importorskip("zephyr.governance.ops_governance.budget_models")
router_mod = pytest.importorskip("zephyr.governance.intelligence_governance.model_router")
cp_mod = pytest.importorskip("zephyr.intelligence.model_profiling.capability_passport")

CascadeOrchestrator = orch_mod.CascadeOrchestrator
CascadeRoutingError = orch_mod.CascadeRoutingError
TamperError = cp_mod.TamperError
ModelTier = budget_models.ModelTier
RoutingDecision = router_mod.RoutingDecision
TaskComplexity = router_mod.TaskComplexity

TASK = "strategy_codegen"
CAP = "strategy_codegen"
MODEL_A = "qwen3:8b"
MODEL_B = "qwen2.5-coder:14b"


def _policy_dict():
    return yaml.safe_load(orch_mod.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def policy_path(tmp_path):
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.safe_dump(_policy_dict(), allow_unicode=True), encoding="utf-8")
    return path


def _passport(safe):
    return SimpleNamespace(recommendations=SimpleNamespace(safe_capabilities=list(safe)))


def _passport_loader(table):
    """table: model_id -> passport / None(no_passport) / TamperError 实例。"""

    def _load(model_id, verify=False):
        assert verify is True  # L1 必须验签加载
        entry = table.get(model_id)
        if isinstance(entry, Exception):
            raise entry
        return entry

    return _load


def _profile_loader(model_id):
    return SimpleNamespace(model_id=model_id)


class _FakeMatcher:
    def __init__(self, score_by_model):
        self._scores = score_by_model

    def match(self, profile):
        return [
            SimpleNamespace(job_id="code_generator", match_score=self._scores.get(profile.model_id, 0.0)),
        ]


class _FakeLearner:
    def __init__(self, snapshot, exc=None):
        self._snapshot = snapshot
        self._exc = exc

    def snapshot(self):
        if self._exc is not None:
            raise self._exc
        return self._snapshot


class _FakeRouter:
    def __init__(self, exc=None):
        self._exc = exc
        self.calls = 0

    def route(self, complexity=TaskComplexity.MODERATE, **_kw):
        self.calls += 1
        if self._exc is not None:
            raise self._exc
        return RoutingDecision(
            model_key="deepseek:pro",
            provider="deepseek",
            tier=ModelTier.STANDARD,
            reason="fake-perf-aware",
            estimated_cost_per_1k=(0.001, 0.002),
            performance_score=0.5,
        )


def _orch(policy_path, **kw):
    defaults = {
        "passport_loader": _passport_loader({MODEL_A: _passport([CAP]), MODEL_B: _passport([CAP])}),
        "profile_loader": _profile_loader,
        "job_matcher": _FakeMatcher({}),
        "learner": _FakeLearner({}),
        "model_router": _FakeRouter(),
    }
    defaults.update(kw)
    return CascadeOrchestrator(policy_path=policy_path, **defaults)


class TestL1CapabilityGate:
    def test_tampered_passport_rejected(self, policy_path):
        orch = _orch(
            policy_path,
            passport_loader=_passport_loader({
                MODEL_A: TamperError("签名验证失败"),
                MODEL_B: _passport([CAP]),
            }),
        )
        d = orch.route(TASK, [MODEL_A, MODEL_B])
        assert d.model_key != MODEL_A  # 伪造/篡改护照 -> 验签失败被拒，不进入 L2
        assert any("验签失败被拒" in a and MODEL_A in a for a in d.alerts)

    def test_required_not_met_excluded_from_l2(self, policy_path):
        orch = _orch(
            policy_path,
            passport_loader=_passport_loader({
                MODEL_A: _passport(["naming_suggest"]),  # safe 交集不含 required
                MODEL_B: _passport([CAP]),
            }),
        )
        d = orch.route(TASK, [MODEL_A, MODEL_B], required_capabilities=[CAP])
        assert d.model_key == MODEL_B
        assert any("required 硬门不满足" in a for a in d.alerts)

    def test_all_no_passport_degrades_l1_unfiltered(self, policy_path):
        orch = _orch(policy_path, passport_loader=_passport_loader({MODEL_A: None, MODEL_B: None}))
        d = orch.route(TASK, [MODEL_A, MODEL_B])
        assert "L1" in d.degraded_stages
        assert d.model_key  # 不中断路由返回
        assert any("无护照" in a for a in d.alerts)


class TestL2FusionRanking:
    def test_fused_ranking_matches_manual_recompute(self, policy_path):
        learner = _FakeLearner({
            TASK: {
                MODEL_A: {"sample_count": 5, "composite_score": 0.6},
                MODEL_B: {"sample_count": 4, "composite_score": 0.9},
            }
        })
        matcher = _FakeMatcher({MODEL_A: 0.8, MODEL_B: 0.4})
        orch = _orch(policy_path, learner=learner, job_matcher=matcher)
        d = orch.route(TASK, [MODEL_B, MODEL_A])  # 入序打乱，证明排序生效
        # 手工复算：A fused=0.5*0.8+0.5*0.6=0.70；B fused=0.5*0.4+0.5*0.9=0.65 -> A 胜
        assert d.model_key == MODEL_A
        assert d.match_score == pytest.approx(0.8)
        assert d.composite_score == pytest.approx(0.6)
        assert "l2:fused" in d.reason

    def test_fused_ranking_flips_when_scores_flip(self, policy_path):
        learner = _FakeLearner({
            TASK: {
                MODEL_A: {"sample_count": 5, "composite_score": 0.6},
                MODEL_B: {"sample_count": 4, "composite_score": 0.9},
            }
        })
        matcher = _FakeMatcher({MODEL_A: 0.4, MODEL_B: 0.8})
        orch = _orch(policy_path, learner=learner, job_matcher=matcher)
        d = orch.route(TASK, [MODEL_A, MODEL_B])
        # B fused=0.5*0.8+0.5*0.9=0.85 > A 0.55 -> B 胜
        assert d.model_key == MODEL_B
        assert d.match_score == pytest.approx(0.8)
        assert d.composite_score == pytest.approx(0.9)

    def test_zero_samples_static_mapping_fallback(self, policy_path):
        orch = _orch(policy_path, learner=_FakeLearner({}))  # 零样本
        d = orch.route(TASK, [MODEL_A, MODEL_B])
        # static_mapping[strategy_codegen]=[qwen2.5-coder:14b, qwen3:8b] -> B 优先
        assert d.model_key == MODEL_B
        assert "static_mapping" in d.reason


class TestL3CostRouting:
    def test_api_decision_fields_complete(self, policy_path):
        # paper_reading preferred=api -> ModelRouter 终裁；字段完整（P1-3）
        orch = _orch(
            policy_path,
            passport_loader=_passport_loader({m: None for m in ("deepseek:pro",)}),
        )
        d = orch.route("paper_reading", ["deepseek:pro"])
        assert d.provider == "deepseek" and d.model_key == "deepseek:pro"
        assert d.reason and "api-router" in d.reason
        assert d.estimated_cost_per_1k == (0.001, 0.002)
        assert d.performance_score == pytest.approx(0.5)
        assert d.tier == ModelTier.STANDARD.value
        payload = d.to_dict()
        assert set(payload) >= {
            "task_type", "model_key", "provider", "tier", "reason",
            "estimated_cost_per_1k", "performance_score", "source",
            "risk_locked", "degraded_stages", "alerts",
        }


class TestCascadeDegradationChain:
    def test_l1_fault_degrades_and_returns(self, policy_path):
        def _boom(model_id, verify=False):
            raise RuntimeError("passport store down")

        orch = _orch(policy_path, passport_loader=_boom)
        d = orch.route(TASK, [MODEL_A, MODEL_B])
        assert "L1" in d.degraded_stages
        assert d.model_key  # 降级产物存在，不中断返回
        assert any("L1 异常降级" in a for a in d.alerts)

    def test_l2_fault_degrades_and_returns(self, policy_path):
        orch = _orch(policy_path, learner=_FakeLearner({}, exc=RuntimeError("matrix corrupted")))
        d = orch.route(TASK, [MODEL_B, MODEL_A])
        assert "L2" in d.degraded_stages
        assert d.model_key == MODEL_B  # 降级按候选原序取本地首位
        assert any("L2 异常降级" in a for a in d.alerts)

    def test_l3_fault_degrades_to_static_mapping(self, policy_path):
        orch = _orch(
            policy_path,
            passport_loader=_passport_loader({"deepseek:pro": None}),
            model_router=_FakeRouter(exc=RuntimeError("router down")),
        )
        d = orch.route("paper_reading", ["deepseek:pro"])
        assert "L3" in d.degraded_stages
        assert d.source == "static_mapping"
        assert d.model_key  # 降级产物存在
        assert any("L3 异常降级" in a for a in d.alerts)

    def test_each_stage_fault_yields_artifact_and_alert(self, policy_path):
        # 三段同时故障：仍返回且三段降级留痕齐全
        def _boom(model_id, verify=False):
            raise RuntimeError("l1 down")

        orch = _orch(
            policy_path,
            passport_loader=_boom,
            learner=_FakeLearner({}, exc=RuntimeError("l2 down")),
            model_router=_FakeRouter(exc=RuntimeError("l3 down")),
        )
        d = orch.route("paper_reading", ["deepseek:pro"])
        assert set(d.degraded_stages) == {"L1", "L2", "L3"}
        assert len(d.alerts) >= 3
        assert d.model_key


class TestRoutingTableAndPeriod:
    def test_risk_veto_hits_rule_engine(self, policy_path):
        orch = _orch(policy_path)
        d = orch.route("risk_veto", [MODEL_A])
        assert d.source == "rule_engine"
        assert d.provider == "rule_engine"  # 附表 A 第 1 行：确定性规则无 LLM

    def test_trading_period_restricts_general_task_to_local(self, policy_path):
        orch = _orch(
            policy_path,
            passport_loader=_passport_loader({
                MODEL_A: _passport(["paper_reading"]),
                "deepseek:pro": None,  # API 候选无护照 -> L1 排除
            }),
        )
        # paper_reading preferred=api 但 kind=general，盘中受限 -> 本地only
        d = orch.route("paper_reading", [MODEL_A, "deepseek:pro"], period="trading")
        assert d.provider == "ollama"
        assert d.model_key == MODEL_A
        assert "period-local-only" in d.reason

    def test_trading_period_allows_reflection_kind_api(self, policy_path):
        orch = _orch(policy_path, passport_loader=_passport_loader({"deepseek:pro": None}))
        # reflection_l23 kind=reflection 在 api_allowed_kinds -> 盘中仍可用 API
        d = orch.route("reflection_l23", ["deepseek:pro"], period="trading")
        assert d.provider == "deepseek"

    def test_config_change_without_code_change(self, policy_path, tmp_path):
        modified = _policy_dict()
        modified["task_routes"]["signal_generation"]["preferred"] = "api"
        path2 = tmp_path / "policy2.yaml"
        path2.write_text(yaml.safe_dump(modified, allow_unicode=True), encoding="utf-8")
        orch = _orch(path2, passport_loader=_passport_loader({"deepseek:pro": None}))
        d = orch.route("signal_generation", ["deepseek:pro"])
        assert d.provider == "deepseek"  # 配置从 local 改 api 即生效，代码零改动


class TestRiskNonDegradable:
    def test_risk_task_l3_fault_still_external_api(self, policy_path):
        orch = _orch(
            policy_path,
            passport_loader=_passport_loader({"deepseek:pro": None}),
            model_router=_FakeRouter(exc=RuntimeError("router down")),
        )
        d = orch.route("risk_diagnosis", ["deepseek:pro", MODEL_A])
        assert d.risk_locked is True
        assert d.provider == "deepseek"  # HB-09：故障注入仍落外部 API，不落本地/规则引擎
        assert d.model_key == "deepseek:pro"  # risk_api_default
        assert "L3" in d.degraded_stages
        assert any("risk_api_default" in a for a in d.alerts)

    def test_risk_task_l1_fault_still_external_api(self, policy_path):
        def _boom(model_id, verify=False):
            raise RuntimeError("passport store down")

        orch = _orch(policy_path, passport_loader=_boom)
        d = orch.route("compliance_review", [MODEL_A, "deepseek:pro"])
        assert d.risk_locked is True
        assert d.provider == "deepseek"  # 不可降级：L1 故障也不落本地候选
        assert "L1" in d.degraded_stages

    def test_risk_task_ignores_period_restriction(self, policy_path):
        orch = _orch(policy_path, passport_loader=_passport_loader({"deepseek:pro": None}))
        d = orch.route("risk_diagnosis", ["deepseek:pro"], period="trading")
        assert d.provider == "deepseek"  # 附表 C：成本/时段规则对风控类任务不适用


class TestPolicyFailClosed:
    def test_missing_policy_file(self, tmp_path):
        with pytest.raises(CascadeRoutingError) as exc_info:
            CascadeOrchestrator(policy_path=tmp_path / "nope.yaml")
        assert exc_info.value.error_code == "ZA-IT-0012"

    def test_policy_missing_section(self, tmp_path):
        bad = _policy_dict()
        del bad["task_routes"]
        path = tmp_path / "bad.yaml"
        path.write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
        with pytest.raises(CascadeRoutingError, match="缺段"):
            CascadeOrchestrator(policy_path=path)

    def test_empty_candidates_fail_closed(self, policy_path):
        orch = _orch(policy_path)
        with pytest.raises(CascadeRoutingError, match="candidates 为空"):
            orch.route(TASK, [])
