# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S1.1
# [MODULE] tests.autonomy.test_execution_layer_s11_wiring
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pytest ; zephyr.autonomy_core.agents.algorithm_agent_entry ; zephyr.autonomy_core.agents.self_iteration_agent_entry ; zephyr.intelligence.model_routing.cascade_orchestrator ; zephyr.intelligence.reflexion
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 落盘断言只认 tmp runtime_dir；11/12/13号文接线全 fake 注入（零网络零真 LLM）；默认 None 缝零行为变化由既有 S0.4/S0.5 用例兜底、本文件显式复核
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4-S1.1 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无（测试件）
# [TESTS] 自测
# [A_test] module_id=MOD-EXE-AGENTS | layer=test | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""S1.1 接口接线测试（14号文 §4-S1.1 验收口径）.

被测对象：
- algorithm_agent_entry 接 11号文 CascadeOrchestrator（实验模型选择裁决留痕）
  + 13号文 ModuleMapper（新模块生成工单四选一裁决留痕）；
- self_iteration_agent_entry 接 12号文 ReflCtrlGate（频率闸门，拒则 denied 留痕
  不反思）+ run_three_role_flow/L1 反思（ReflectionRecord 落 ReflectionStore）。

全 fake 注入缝；默认 None 零行为变化；产出信封仍 100% human_gated。
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.autonomy_core.agents import algorithm_agent_entry, self_iteration_agent_entry
from zephyr.experiment_tracking.config import ExperimentTrackingConfig
from zephyr.governance.intelligence_governance.model_router import TaskComplexity
from zephyr.intelligence.model_routing.cascade_orchestrator import CascadeDecision
from zephyr.intelligence.reflexion.reflctrl_gate import ReflCtrlDecision
from zephyr.intelligence.reflexion.reflection_schema import (
    ImprovementSuggestion,
    ReflectionRecord,
)
from zephyr.intelligence.reflexion.roles import (
    EvaluationReport,
    Trajectory,
    TrajectoryStep,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


# ── fake 注入件 ──────────────────────────────────────────


class _FakeCascade:
    """11号文 CascadeOrchestrator 同签名 fake（记录调用参数）."""

    def __init__(self, decision: CascadeDecision) -> None:
        self.calls: list[dict] = []
        self._decision = decision

    def route(self, task_type, candidates, *, complexity, period, required_capabilities):
        self.calls.append({
            "task_type": task_type,
            "candidates": list(candidates),
            "complexity": complexity,
            "period": period,
            "required_capabilities": required_capabilities,
        })
        return self._decision


class _FakeMapper:
    """13号文 ModuleMapper 同签名 fake."""

    def __init__(self, spec) -> None:
        self.calls: list[tuple] = []
        self._spec = spec

    def map_knowledge(self, item, classification, *, schema_plan=None):
        self.calls.append((item, classification, schema_plan))
        return self._spec


class _FakeReflGate:
    """12号文 ReflCtrlGate.decide 同签名 fake."""

    def __init__(self, decision: ReflCtrlDecision) -> None:
        self.requests: list = []
        self._decision = decision

    def decide(self, request):
        self.requests.append(request)
        return self._decision


class _FakeReflStore:
    """ReflectionStore 同签名 fake（内存记录+path 属性）."""

    def __init__(self) -> None:
        self.records: list = []
        self.path = Path("fake/reflections.jsonl")

    def append(self, record):
        self.records.append(record)
        return self.path


def _decision() -> CascadeDecision:
    return CascadeDecision(
        task_type="model_evaluation", model_key="qwen3:8b", provider="ollama",
        tier="UNTIERED", reason="fake-cascade", source="cascade",
    )


def _mapper_spec():
    return SimpleNamespace(
        verdict="variant_of", target_registry="strategy_registry", rationale="r",
        retrieval_channel="fts_only", degraded=True,
        candidates=(SimpleNamespace(entry_id="STR-DABAN-001", registry="strategy_registry",
                                    score=0.75, retired=False),),
        draft_notes=("人审分配编号",), human_gate_required=True,
    )


def _seed_run(fallback_dir: Path) -> None:
    run_dir = fallback_dir / "c1-validation" / "run-demo-001"
    run_dir.mkdir(parents=True)
    (run_dir / "run_meta.json").write_text(json.dumps({
        "run_id": "run-demo-001", "component": "c1-validation", "run_name": "demo",
        "status": "FINISHED", "start_time": "2026-08-22T10:00:00",
        "end_time": "2026-08-22T10:05:00", "metrics": {"passed": 1.0},
        "tags": {}, "artifacts": [],
    }, ensure_ascii=False), encoding="utf-8")


def _algo_ticket(**extra) -> dict:
    ticket = {
        "ticket_id": "algo-s11-001", "experiment_type": "model_evaluation",
        "target_id": "EXP-DEMO", "run_id": "run-demo-001", "component": "c1-validation",
    }
    ticket.update(extra)
    return ticket


def _run_algo(ticket, tmp_path, **seams):
    return algorithm_agent_entry.run_algorithm_experiment_ticket(
        ticket, runtime_dir=tmp_path / "rt", repo_root=REPO_ROOT,
        gpu_stats_provider=lambda: {"available": False},
        tracking_config=ExperimentTrackingConfig(fallback_dir=tmp_path / "fb"),
        **seams,
    )


def _latest_run_dir(tmp_path: Path, role: str) -> Path:
    return next(p for p in (tmp_path / "rt" / "agent_runs" / role).iterdir() if p.is_dir())


class TestAlgorithmCascadeWiring:
    """S1.1-A：实验工单接 11号文 cascade 模型选择（注入缝默认 None 零行为变化）."""

    def test_cascade_decision_landed_and_call_args(self, tmp_path):
        _seed_run(tmp_path / "fb")
        fake = _FakeCascade(_decision())
        report = _run_algo(_algo_ticket(
            model_candidates=["qwen3:8b", "deepseek:7b"],
            complexity="complex", period="post_close",
            required_capabilities=["model_evaluation"],
        ), tmp_path, cascade_router=fake)
        assert report["status"] == "completed"
        assert report["steps"] == ["registered", "model_routed", "not_available", "evaluated"]
        call = fake.calls[0]
        assert call["task_type"] == "model_evaluation"
        assert call["candidates"] == ["qwen3:8b", "deepseek:7b"]
        assert call["complexity"] is TaskComplexity.COMPLEX
        assert call["period"] == "post_close"
        assert call["required_capabilities"] == ["model_evaluation"]
        landed = json.loads(
            (_latest_run_dir(tmp_path, "algorithm") / "model_routing.decision.json")
            .read_text(encoding="utf-8")
        )
        assert landed["ai_autonomy"] == "human_gated"
        assert landed["status"] == "routed"
        assert landed["decision"]["model_key"] == "qwen3:8b"
        assert landed["decision"]["source"] == "cascade"
        assert report["model_routing"]["decision"]["model_key"] == "qwen3:8b"

    def test_cascade_router_without_candidates_marks_skipped(self, tmp_path):
        _seed_run(tmp_path / "fb")
        fake = _FakeCascade(_decision())
        report = _run_algo(_algo_ticket(), tmp_path, cascade_router=fake)
        assert fake.calls == []  # 无候选不调路由（cascade 契约：空候选 fail-closed）
        assert report["steps"][1] == "model_route_skipped"
        landed = json.loads(
            (_latest_run_dir(tmp_path, "algorithm") / "model_routing.decision.json")
            .read_text(encoding="utf-8")
        )
        assert landed["status"] == "skipped_no_candidates"

    def test_default_none_router_zero_behavior_change(self, tmp_path):
        _seed_run(tmp_path / "fb")
        report = _run_algo(_algo_ticket(), tmp_path)
        assert report["steps"] == ["registered", "not_available", "evaluated"]
        assert "model_routing" not in report
        assert not (_latest_run_dir(tmp_path, "algorithm") / "model_routing.decision.json").exists()


class TestAlgorithmModuleMapperWiring:
    """S1.1-B：新模块生成类工单接 13号文 ModuleMapper 四选一裁决留痕."""

    _KNOWLEDGE = {"knowledge_id": "kn-1", "title": "打板情绪变体", "content": "正文",
                  "source_ref": "20号文"}
    _CLASSIFICATION = {
        "quality": {"relevance": 0.9, "timeliness": 0.8, "information": 0.7,
                    "reliability": 0.9},
        "target_kind": "strategy", "strategy_class": "daban",
    }

    def test_module_generation_ticket_mapped_and_landed(self, tmp_path):
        fake = _FakeMapper(_mapper_spec())
        report = _run_algo(_algo_ticket(
            experiment_type="module_generation", run_id="",
            knowledge=self._KNOWLEDGE, classification=self._CLASSIFICATION,
        ), tmp_path, module_mapper=fake)
        assert report["steps"][:2] == ["registered", "module_mapped"]
        item, classification, _ = fake.calls[0]
        assert item.title == "打板情绪变体"
        assert classification.verdict == "classified"
        assert classification.classification.strategy_class == "daban"
        landed = json.loads(
            (_latest_run_dir(tmp_path, "algorithm") / "module_mapping.spec.json")
            .read_text(encoding="utf-8")
        )
        assert landed["ai_autonomy"] == "human_gated"
        assert landed["verdict"] == "variant_of"
        assert landed["target_registry"] == "strategy_registry"
        assert landed["candidates"][0]["entry_id"] == "STR-DABAN-001"
        assert landed["human_gate_required"] is True
        assert report["module_mapping"]["verdict"] == "variant_of"

    def test_invalid_classification_fails_closed_not_raises(self, tmp_path):
        fake = _FakeMapper(_mapper_spec())
        bad = {"quality": {"relevance": 0.9, "timeliness": 0.8, "information": 0.7,
                           "reliability": 0.9},
               "target_kind": "strategy"}  # 缺 strategy_class → pydantic 拒收
        report = _run_algo(_algo_ticket(
            experiment_type="module_generation", run_id="",
            knowledge=self._KNOWLEDGE, classification=bad,
        ), tmp_path, module_mapper=fake)
        assert fake.calls == []  # 载荷非法不进映射（fail-closed）
        assert "module_map_error" in report["steps"]
        landed = json.loads(
            (_latest_run_dir(tmp_path, "algorithm") / "module_mapping.spec.json")
            .read_text(encoding="utf-8")
        )
        assert landed["status"] == "error" and landed["verdict"] == "error"

    def test_default_none_mapper_zero_behavior_change(self, tmp_path):
        _seed_run(tmp_path / "fb")
        report = _run_algo(_algo_ticket(
            experiment_type="module_generation",
            knowledge=self._KNOWLEDGE, classification=self._CLASSIFICATION,
        ), tmp_path)
        assert report["status"] == "completed"
        assert report["steps"] == ["registered", "not_available", "evaluated"]
        assert not (_latest_run_dir(tmp_path, "algorithm") / "module_mapping.spec.json").exists()


# ── 12号文反思接线 ───────────────────────────────────────


def _refl_ticket(**extra) -> dict:
    ticket = {
        "ticket_id": "refl-s11-001", "kind": "reflection_review",
        "task_description": "复盘打板信号实验", "layer": "execution",
        "requested_level": "L1", "outcome": "failure",
    }
    ticket.update(extra)
    return ticket


def _flow_result(task):
    trajectory = Trajectory(
        task_id=task.task_id,
        steps=[TrajectoryStep(step_index=0, action="执行", observation="中止: 数据缺失")],
        final_output="", succeeded=False, error="任务执行失败: 数据缺失",
    )
    report = EvaluationReport(task_id=task.task_id, score=0.3,
                              dimensions={"完整性": 0.3}, defects=["step[0] 中止"])
    record = ReflectionRecord(
        reflection_id="refl-fake-1", task_id=task.task_id, trajectory_ref="traj-ref",
        outcome="failure", failure_category="数据错误",
        improvement_suggestions=[ImprovementSuggestion(
            category="数据错误", suggestion="补齐数据源后重跑", evidence_ref="step[0]")],
    )
    return trajectory, report, record


class TestSelfIterationReflectionWiring:
    """S1.1-C：迭代评审工单接 12号文（闸门→三角色反思→ReflectionStore）."""

    def test_allowed_flow_produces_record_into_store(self, tmp_path):
        gate = _FakeReflGate(ReflCtrlDecision(
            allowed=True, matched_rules=("L1-FORCE-EXECUTION-FAILURE",),
            granted_levels=("L1", "L2", "L3"),
        ))
        store = _FakeReflStore()
        flow_calls: list = []
        report = self_iteration_agent_entry.run_reflection_review(
            _refl_ticket(), runtime_dir=tmp_path / "rt", repo_root=REPO_ROOT,
            refl_gate=gate, flow_runner=lambda task: (flow_calls.append(task), _flow_result(task))[1],
            reflection_store=store,
        )
        assert report["status"] == "completed"
        assert gate.requests[0].task_id == "refl-s11-001"  # task_id 缺省回填 ticket_id
        assert gate.requests[0].layer == "execution"
        assert len(flow_calls) == 1 and flow_calls[0].description == "复盘打板信号实验"
        assert len(store.records) == 1  # ReflectionRecord 落 ReflectionStore
        assert store.records[0].reflection_id == "refl-fake-1"
        run_dir = _latest_run_dir(tmp_path, "self_iteration")
        gate_landed = json.loads((run_dir / "reflection_gate.json").read_text(encoding="utf-8"))
        assert gate_landed["allowed"] is True
        assert gate_landed["matched_rules"] == ["L1-FORCE-EXECUTION-FAILURE"]
        assert gate_landed["ai_autonomy"] == "human_gated"
        record_landed = json.loads((run_dir / "reflection_record.json").read_text(encoding="utf-8"))
        assert record_landed["record"]["outcome"] == "failure"
        assert record_landed["record"]["improvement_suggestions"][0]["category"] == "数据错误"

    def test_denied_by_gate_skips_reflection(self, tmp_path):
        gate = _FakeReflGate(ReflCtrlDecision(allowed=False, denied_by="DENIED-NO-RULE"))
        flow_called: list = []
        report = self_iteration_agent_entry.run_reflection_review(
            _refl_ticket(outcome="success"), runtime_dir=tmp_path / "rt", repo_root=REPO_ROOT,
            refl_gate=gate,
            flow_runner=lambda task: flow_called.append(task) or _flow_result(task),
            reflection_store=_FakeReflStore(),
        )
        assert report["status"] == "denied_by_reflctrl"
        assert report["gate"]["denied_by"] == "DENIED-NO-RULE"
        assert flow_called == []  # 闸门拒则不反思
        run_dir = _latest_run_dir(tmp_path, "self_iteration")
        assert not (run_dir / "reflection_record.json").exists()
        run_record = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        assert run_record["status"] == "denied_by_reflctrl"

    def test_default_seams_use_real_gate_flow_and_store(self, tmp_path):
        """默认缝=真 ReflCtrlGate（stats 落 runtime）+合成三角色+真 ReflectionStore."""
        report = self_iteration_agent_entry.run_reflection_review(
            _refl_ticket(), runtime_dir=tmp_path / "rt", repo_root=REPO_ROOT,
        )
        assert report["status"] == "completed"  # outcome=failure 命中强制规则放行
        reflections = tmp_path / "rt" / "reflections" / "reflections.jsonl"
        lines = [json.loads(x) for x in reflections.read_text(encoding="utf-8").splitlines() if x.strip()]
        assert len(lines) == 1 and lines[0]["task_id"] == "refl-s11-001"
        decisions = tmp_path / "rt" / "reflctrl" / "reflctrl_decisions.jsonl"
        assert decisions.exists()  # 闸门裁决留痕落在 runtime 下（不污染 data/brain）

    def test_default_real_gate_denies_ruleless_request(self, tmp_path):
        report = self_iteration_agent_entry.run_reflection_review(
            _refl_ticket(outcome="success"), runtime_dir=tmp_path / "rt", repo_root=REPO_ROOT,
        )
        assert report["status"] == "denied_by_reflctrl"
        assert report["gate"]["denied_by"] == "DENIED-NO-RULE"

    def test_invalid_layer_fails_closed(self, tmp_path):
        with pytest.raises(ValueError, match="layer"):
            self_iteration_agent_entry.run_reflection_review(
                _refl_ticket(layer="bogus"), runtime_dir=tmp_path / "rt", repo_root=REPO_ROOT,
            )

    def test_cli_dispatch_reflection_review(self, tmp_path):
        ticket_file = tmp_path / "ticket.json"
        ticket_file.write_text(json.dumps(_refl_ticket(), ensure_ascii=False), encoding="utf-8")
        assert self_iteration_agent_entry.main(
            ["--ticket", str(ticket_file), "--runtime-dir", str(tmp_path / "rt")]
        ) == 0
        assert (tmp_path / "rt" / "reflections" / "reflections.jsonl").exists()

    def test_iteration_review_default_path_unchanged(self, tmp_path):
        report = self_iteration_agent_entry.run_iteration_review(
            {"ticket_id": "iter-keep", "evidence_paths": []},
            runtime_dir=tmp_path, repo_root=REPO_ROOT,
        )
        assert report["kind"] == "iteration_suggestion"
        assert report["suggestions"][0]["topic"] == "常规巡检"
