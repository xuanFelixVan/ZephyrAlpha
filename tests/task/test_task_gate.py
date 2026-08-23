# [A_test] module_id: MOD-GOV_task_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_task_gate
# [INVARIANTS] TaskGate依赖CapabilityPassport;测试使用mock构造护照
# [MODIFY-GUARD] src/zephyr/runtime/task_gate.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] can_dispatch返回tuple[bool,str];get_safe_capabilities返回list
# [TESTS] tests/test_task_gate.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

from zephyr.intelligence.model_profiling.capability_passport import (
    CapabilityPassport,
    DepthCapabilityResult,
    DepthResult,
    Recommendations,
)
from zephyr.trading.task_gate import TaskGate


def _make_passport(
    model_id: str = "test-model",
    safe_caps: list[str] | None = None,
    unsafe_caps: list[str] | None = None,
    depth_caps: dict[str, DepthCapabilityResult] | None = None,
    grade: str = "B",
    score: float = 0.75,
) -> CapabilityPassport:
    safe = safe_caps if safe_caps is not None else ["task_classification", "tag_completion"]
    unsafe = unsafe_caps if unsafe_caps is not None else ["code_fix"]
    caps = depth_caps or {
        "task_classification": DepthCapabilityResult(pass_=True, grade="B", precision=0.8, recall=0.7, f1=0.75),
        "tag_completion": DepthCapabilityResult(pass_=True, grade="B", precision=0.7, recall=0.7, f1=0.7),
        "code_fix": DepthCapabilityResult(
            pass_=False, grade="F", precision=0.3, recall=0.2, f1=0.25, failure_reason="low_precision_below_threshold"
        ),
    }
    return CapabilityPassport(
        model_id=model_id,
        overall_grade=grade,
        overall_score=score,
        depth=DepthResult(overall_score=0.6, capabilities=caps),
        recommendations=Recommendations(safe_capabilities=safe, unsafe_capabilities=unsafe),
    )


class TestTaskGateInit:
    def test_empty_initially(self):
        gate = TaskGate()
        assert gate.has_passport("any-model") is False
        assert gate.summary()["models"] == 0


class TestLoadPassport:
    def test_load_passport_success(self):
        passport = _make_passport("model-a")
        gate = TaskGate()
        with patch.object(CapabilityPassport, "load", return_value=passport):
            result = gate.load_passport("model-a")
        assert result is not None
        assert gate.has_passport("model-a") is True

    def test_load_passport_not_found(self):
        gate = TaskGate()
        with patch.object(CapabilityPassport, "load", return_value=None):
            result = gate.load_passport("missing-model")
        assert result is None
        assert gate.has_passport("missing-model") is False


class TestLoadPassports:
    def test_load_multiple(self):
        p1 = _make_passport("model-a")
        p2 = _make_passport("model-b")
        gate = TaskGate()
        with (
            patch.object(CapabilityPassport, "list_all", return_value=["model-a", "model-b"]),
            patch.object(CapabilityPassport, "load", side_effect=[p1, p2]),
        ):
            count = gate.load_passports()
        assert count == 2
        assert gate.has_passport("model-a") is True
        assert gate.has_passport("model-b") is True

    def test_load_empty(self):
        gate = TaskGate()
        with patch.object(CapabilityPassport, "list_all", return_value=[]):
            count = gate.load_passports()
        assert count == 0


class TestCanDispatch:
    def test_dispatch_safe_capability(self):
        passport = _make_passport("model-a")
        gate = TaskGate()
        gate.passports["model-a"] = passport
        ok, reason = gate.can_dispatch("model-a", "task_classification")
        assert ok is True
        assert reason == "ok"

    def test_dispatch_unsafe_capability(self):
        passport = _make_passport("model-a")
        gate = TaskGate()
        gate.passports["model-a"] = passport
        ok, reason = gate.can_dispatch("model-a", "code_fix")
        assert ok is False
        assert "low_accuracy" in reason

    def test_dispatch_no_passport(self):
        gate = TaskGate()
        ok, reason = gate.can_dispatch("unknown-model", "task_classification")
        assert ok is False
        assert reason == "no_passport"

    def test_dispatch_no_depth_data(self):
        passport = _make_passport("model-a")
        passport.depth = DepthResult(overall_score=0.0, capabilities={})
        gate = TaskGate()
        gate.passports["model-a"] = passport
        ok, reason = gate.can_dispatch("model-a", "task_classification")
        assert ok is False
        assert reason == "no_depth_data"

    def test_dispatch_capability_not_tested(self):
        passport = _make_passport("model-a")
        gate = TaskGate()
        gate.passports["model-a"] = passport
        ok, reason = gate.can_dispatch("model-a", "unknown_capability")
        assert ok is False
        assert reason == "capability_not_tested"


class TestCanDoAny:
    def test_has_safe_capabilities(self):
        passport = _make_passport("model-a")
        gate = TaskGate()
        gate.passports["model-a"] = passport
        assert gate.can_do_any("model-a") is True

    def test_no_safe_capabilities(self):
        passport = _make_passport("model-a", safe_caps=[], unsafe_caps=["code_fix"])
        gate = TaskGate()
        gate.passports["model-a"] = passport
        assert gate.can_do_any("model-a") is False

    def test_no_passport(self):
        gate = TaskGate()
        assert gate.can_do_any("unknown") is False


class TestGetSafeCapabilities:
    def test_returns_safe(self):
        passport = _make_passport("model-a", safe_caps=["task_classification", "tag_completion"])
        gate = TaskGate()
        gate.passports["model-a"] = passport
        caps = gate.get_safe_capabilities("model-a")
        assert "task_classification" in caps
        assert "tag_completion" in caps

    def test_no_passport(self):
        gate = TaskGate()
        assert gate.get_safe_capabilities("unknown") == []


class TestGetUnsafeCapabilities:
    def test_returns_unsafe(self):
        passport = _make_passport("model-a", unsafe_caps=["code_fix", "refactor"])
        gate = TaskGate()
        gate.passports["model-a"] = passport
        caps = gate.get_unsafe_capabilities("model-a")
        assert "code_fix" in caps
        assert "refactor" in caps

    def test_no_passport(self):
        gate = TaskGate()
        assert gate.get_unsafe_capabilities("unknown") == []


class TestGetPassport:
    def test_existing(self):
        passport = _make_passport("model-a")
        gate = TaskGate()
        gate.passports["model-a"] = passport
        assert gate.get_passport("model-a") is passport

    def test_missing(self):
        gate = TaskGate()
        assert gate.get_passport("unknown") is None


class TestSummary:
    def test_summary_with_models(self):
        p1 = _make_passport("model-a", grade="B", score=0.75)
        p2 = _make_passport("model-b", grade="A", score=0.9)
        gate = TaskGate()
        gate.passports["model-a"] = p1
        gate.passports["model-b"] = p2
        s = gate.summary()
        assert s["models"] == 2
        assert "model-a" in s["details"]
        assert s["details"]["model-a"]["grade"] == "B"

    def test_summary_empty(self):
        gate = TaskGate()
        s = gate.summary()
        assert s["models"] == 0
        assert s["details"] == {}


class TestRepr:
    def test_repr(self):
        gate = TaskGate()
        assert repr(gate) == "TaskGate(models=0)"
        gate.passports["m1"] = _make_passport("m1")
        assert repr(gate) == "TaskGate(models=1)"


class TestPassportIdCaliber:
    """护照 ID 口径统一（清单 2.9 / GP0 #255④ 裁定口径）双向兼容读取。

    口径裁定（2026-08-22 #255④ + 2026-08-24 H2 核查）：
    - 真源 = 护照 JSON 内 model_id 字段（Ollama 名保留冒号，如 qwen3:8b）；
    - 文件名是 `:`/`/`→`_` 有损安全编码（qwen3_8b.json），不可反推；
    - TaskGate dict 键 = 真源形态；dispatch 链可能持任一形态查询——
      冒号形态与下划线形态 MUST 命中同一本护照（双向兼容读取）。
    """

    def _gate_with_colon_model(self) -> TaskGate:
        gate = TaskGate()
        # 真源键 = 冒号形态（Ollama qwen3:8b 落盘 qwen3_8b.json 的同款场景）
        gate.passports["qwen3:8b"] = _make_passport("qwen3:8b")
        return gate

    def test_can_dispatch_colon_form(self):
        gate = self._gate_with_colon_model()
        ok, reason = gate.can_dispatch("qwen3:8b", "task_classification")
        assert ok is True
        assert reason == "ok"

    def test_can_dispatch_underscore_form_hits_same_passport(self):
        """dispatch 链持文件名/下划线形态查询，不得 no_passport 假阴性。"""
        gate = self._gate_with_colon_model()
        ok, reason = gate.can_dispatch("qwen3_8b", "task_classification")
        assert ok is True
        assert reason == "ok"

    def test_has_passport_both_forms(self):
        gate = self._gate_with_colon_model()
        assert gate.has_passport("qwen3:8b") is True
        assert gate.has_passport("qwen3_8b") is True

    def test_get_passport_both_forms_same_object(self):
        gate = self._gate_with_colon_model()
        assert gate.get_passport("qwen3_8b") is gate.get_passport("qwen3:8b")

    def test_get_safe_capabilities_underscore_form(self):
        gate = self._gate_with_colon_model()
        caps = gate.get_safe_capabilities("qwen3_8b")
        assert "task_classification" in caps

    def test_can_do_any_underscore_form(self):
        gate = self._gate_with_colon_model()
        assert gate.can_do_any("qwen3_8b") is True

    def test_unknown_model_still_misses(self):
        """归一化不得放大命中面——不相关模型仍 no_passport。"""
        gate = self._gate_with_colon_model()
        ok, reason = gate.can_dispatch("qwen2.5-coder_14b", "task_classification")
        assert ok is False
        assert reason == "no_passport"
        assert gate.has_passport("other_model") is False

    def test_canonical_key_preserved(self):
        """存储键保持真源形态（冒号），归一化只发生在查询侧。"""
        gate = self._gate_with_colon_model()
        gate.can_dispatch("qwen3_8b", "task_classification")
        assert "qwen3:8b" in gate.passports
        assert "qwen3_8b" not in gate.passports
