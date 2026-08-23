# [BLUEPRINT] MOD-INF-054 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §
# [MODULE] tests.model.test_exam_trigger_scheduler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""
test_exam_trigger_scheduler.py — 触发式考试调度器单测（06号文 §4 Phase 1，P1-2/P1-3）
=====================================================================================
LLM/模型/DB 全 mock：ModelDiscovery 假发现、Quick 考试假 runner（零真实考试）、
护照/QuickProfile 目录重定向 tmp_path。覆盖：
- 新模型自动 Quick 考试 -> QuickProfile 落盘（P1-2 验收点）；远程 API 模型跳过；已知模型不重复触发
- 单模型考试失败不中断批量 + seen 快照防重复触发风暴
- TaskGate 连续 low_accuracy 超阈 -> 复核建议（只发建议 human_gated，Standard/Deep 不自动执行）
- 放行/非 low_accuracy 拦截计数清零；check_and_record 透传判定且建议落盘 JSONL
- 阈值非法/快照损坏 fail-closed（ExamTriggerError ZA-IT-0011）
"""

from __future__ import annotations

import json

import pytest

cp_mod = pytest.importorskip("zephyr.intelligence.model_profiling.capability_passport")
md_mod = pytest.importorskip("zephyr.intelligence.model_profiling.model_discovery")
sched_mod = pytest.importorskip("zephyr.intelligence.model_profiling.exam_trigger_scheduler")

ExamTriggerError = sched_mod.ExamTriggerError
ExamTriggerScheduler = sched_mod.ExamTriggerScheduler
QuickProfile = cp_mod.QuickProfile
DiscoveredModel = md_mod.DiscoveredModel


class _FakeDiscovery:
    """假模型发现器（模型清单注入，零 Ollama/API 调用）。"""

    def __init__(self, models):
        self._models = models
        self.calls = 0

    def discover_all(self):
        self.calls += 1
        return list(self._models)


def _ollama(name):
    return DiscoveredModel(name=name, source="ollama")


def _remote(name):
    return DiscoveredModel(name=name, source="remote_api", provider=name.split(":")[0])


def _fake_runner(profile_by_model, errors=()):
    """假 Quick 考试 runner：按注入表返回 QuickProfile；errors 名单内模型抛异常。"""

    def _run(model_id: str) -> QuickProfile:
        if model_id in errors:
            raise RuntimeError(f"fake exam crash: {model_id}")
        profile = profile_by_model.get(model_id) or QuickProfile(model_id=model_id, overall_score=0.5)
        return profile

    return _run


@pytest.fixture()
def isolated_dirs(tmp_path, monkeypatch):
    """护照/QuickProfile 目录重定向到 tmp（不触碰 data/brain 真目录）。"""
    passports = tmp_path / "passports"
    quick = tmp_path / "quick_profiles"
    monkeypatch.setattr(cp_mod, "PASSPORTS_DIR", passports)
    monkeypatch.setattr(cp_mod, "QUICK_PROFILES_DIR", quick)
    return {"passports": passports, "quick": quick}


class TestNewModelQuickExam:
    def test_new_ollama_model_produces_quick_profile_on_disk(self, isolated_dirs, tmp_path):
        discovery = _FakeDiscovery([_ollama("qwen3:8b"), _remote("deepseek:pro")])
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=tmp_path / "seen.json",
        )
        report = sched.trigger_quick_exams()
        assert report["examined"] == ["qwen3:8b"]  # 远程 API 模型不触发本地 Quick 考试
        assert report["failed"] == {}
        saved = isolated_dirs["quick"] / "qwen3_8b.json"
        assert saved.exists()  # P1-2 验收点：QuickProfile 落盘 quick_profiles/
        data = json.loads(saved.read_text(encoding="utf-8"))
        assert data["model_id"] == "qwen3:8b" and data["exam_mode"] == "quick"

    def test_known_model_with_quick_profile_skipped(self, isolated_dirs, tmp_path):
        QuickProfile(model_id="qwen3:8b").save()  # 已有 QuickProfile -> 非新模型
        discovery = _FakeDiscovery([_ollama("qwen3:8b"), _ollama("qwen2.5-coder:14b")])
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=tmp_path / "seen.json",
        )
        assert sched.scan_new_models() == ["qwen2.5-coder:14b"]

    def test_seen_store_prevents_retrigger(self, isolated_dirs, tmp_path):
        discovery = _FakeDiscovery([_ollama("qwen3:8b")])
        seen_path = tmp_path / "seen.json"
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=seen_path,
        )
        sched.trigger_quick_exams()
        assert sched.scan_new_models() == []
        # 新实例加载同一快照 -> 仍不重复触发（跨会话幂等）
        sched2 = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=_fake_runner({}),
            seen_store_path=seen_path,
        )
        report = sched2.trigger_quick_exams()
        assert report["targets"] == [] and report["examined"] == []

    def test_exam_failure_does_not_break_batch(self, isolated_dirs, tmp_path):
        discovery = _FakeDiscovery([_ollama("bad:7b"), _ollama("good:7b")])
        runner = _fake_runner({}, errors=("bad:7b",))
        sched = ExamTriggerScheduler(
            discovery=discovery,
            quick_exam_runner=runner,
            seen_store_path=tmp_path / "seen.json",
        )
        report = sched.trigger_quick_exams()
        assert report["examined"] == ["good:7b"]
        assert "bad:7b" in report["failed"] and "fake exam crash" in report["failed"]["bad:7b"]
        # 失败模型也记 seen（防每次扫描重复触发风暴）
        assert sched.scan_new_models() == []

    def test_explicit_model_list_runs_regardless_of_known(self, isolated_dirs, tmp_path):
        QuickProfile(model_id="qwen3:8b").save()
        sched = ExamTriggerScheduler(
            discovery=_FakeDiscovery([]),
            quick_exam_runner=_fake_runner({}),
            seen_store_path=tmp_path / "seen.json",
        )
        report = sched.trigger_quick_exams(["qwen3:8b"])  # 显式名单=人工点名复跑 Quick（human 触发）
        assert report["examined"] == ["qwen3:8b"]


class TestLowAccuracyReviewSuggestion:
    def _sched(self, tmp_path, threshold=3):
        return ExamTriggerScheduler(
            discovery=_FakeDiscovery([]),
            quick_exam_runner=_fake_runner({}),
            low_accuracy_threshold=threshold,
            suggestion_sink_path=tmp_path / "suggestions.jsonl",
        )

    def test_consecutive_low_accuracy_triggers_suggestion_at_threshold(self, tmp_path):
        sched = self._sched(tmp_path)
        reason = "low_accuracy: low_precision_below_threshold"
        assert sched.record_gate_decision("qwen3:8b", "code_fix", False, reason) is None
        assert sched.record_gate_decision("qwen3:8b", "code_fix", False, reason) is None
        suggestion = sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert suggestion is not None
        assert suggestion["type"] == "review_exam_suggestion"
        assert suggestion["consecutive_low_accuracy"] == 3
        assert suggestion["suggested_mode"] == "standard"
        assert suggestion["human_gated"] is True  # 只发建议：Standard/Deep 始终人工确认
        # 同一连续段不重复发建议
        assert sched.record_gate_decision("qwen3:8b", "code_fix", False, reason) is None
        assert len(sched.suggestions) == 1

    def test_suggestion_persisted_to_jsonl_sink(self, tmp_path):
        sched = self._sched(tmp_path, threshold=2)
        reason = "low_accuracy: f1_below_threshold"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sink = tmp_path / "suggestions.jsonl"
        lines = sink.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1  # P1-3 验收点：拦截日志含触发建议记录
        record = json.loads(lines[0])
        assert record["model_id"] == "qwen3:8b" and record["capability"] == "code_fix"

    def test_allowed_decision_resets_streak(self, tmp_path):
        sched = self._sched(tmp_path)
        reason = "low_accuracy: low_precision_below_threshold"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert sched.record_gate_decision("qwen3:8b", "code_fix", True, "ok") is None
        assert sched.block_streaks == {}
        # 重新累计需再满阈值才发建议
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert sched.suggestions == []

    def test_non_low_accuracy_block_resets_streak(self, tmp_path):
        sched = self._sched(tmp_path)
        reason = "low_accuracy: low_precision_below_threshold"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        sched.record_gate_decision("qwen3:8b", "code_fix", False, "no_passport")  # 非 low_accuracy
        assert sched.block_streaks == {}
        assert sched.suggestions == []

    def test_streaks_tracked_per_model_capability_pair(self, tmp_path):
        sched = self._sched(tmp_path, threshold=2)
        reason = "low_accuracy: x"
        sched.record_gate_decision("qwen3:8b", "code_fix", False, reason)
        assert sched.record_gate_decision("qwen3:8b", "refactor", False, reason) is None
        assert sched.suggestions == []  # 不同能力各自计数，互不累计

    def test_check_and_record_passthrough_and_suggestion(self, tmp_path):
        class _FakeGate:
            def __init__(self, verdict):
                self._verdict = verdict

            def can_dispatch(self, model_id, capability):
                return self._verdict

        sched = self._sched(tmp_path, threshold=2)
        gate = _FakeGate((False, "low_accuracy: low_precision_below_threshold"))
        assert sched.check_and_record(gate, "qwen3:8b", "code_fix") == (False, "low_accuracy: low_precision_below_threshold")
        ok, _ = sched.check_and_record(gate, "qwen3:8b", "code_fix")
        assert ok is False
        assert len(sched.suggestions) == 1


class TestFailClosed:
    def test_invalid_threshold(self, tmp_path):
        with pytest.raises(ExamTriggerError) as exc_info:
            ExamTriggerScheduler(low_accuracy_threshold=0)
        assert exc_info.value.error_code == "ZA-IT-0011"

    def test_corrupted_seen_store(self, tmp_path):
        seen_path = tmp_path / "seen.json"
        seen_path.write_text("{not-json", encoding="utf-8")
        with pytest.raises(ExamTriggerError, match="seen 快照损坏"):
            ExamTriggerScheduler(seen_store_path=seen_path)
