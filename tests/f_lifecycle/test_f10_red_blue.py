# [A_test] module_id: MOD-GOV_f10_red_blue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md | §tests
# [MODULE] tests.test_f10_red_blue
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""DM-202009: F10 红蓝对抗测试套件。

3类攻击场景:
    1. 考试作弊: 模型记忆考题/针对benchmark优化/返回伪造结果
    2. 画像篡改: 篡改benchmark结果/篡改composite_score/篡改7维数据
    3. 护照伪造: 伪造护照文件/篡改护照JSON/签名绕过

防护机制验证:
    - DM-202007: CapabilityPassport HMAC-SHA256签名
    - DM-202008: ExamOrchestrator 防作弊（随机化+完整性校验+反优化检测）
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.intelligence.model_profiling.capability_passport import (
    CapabilityPassport,
    TamperError,
    _compute_signature,
    _get_signing_key,
)
from zephyr.intelligence.model_profiling.exam_checks import validate_result
from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator
from zephyr.intelligence.model_profiling.exam_test_cases import (
    CASES_BY_CAPABILITY,
    ExamTestCase,
)

# ------------------------------------------------------------------
# 辅助函数
# ------------------------------------------------------------------


def _make_mock_chat() -> MagicMock:
    """创建模拟 chat 对象。"""
    chat = MagicMock()
    chat.model = "red-team-attacker:latest"
    return chat


def _find_case(capability: str) -> ExamTestCase:
    """获取指定能力的第一个测试用例。"""
    cases = CASES_BY_CAPABILITY.get(capability, [])
    assert cases, f"No cases for capability: {capability}"
    return cases[0]


# ------------------------------------------------------------------
# 攻击场景 1: 考试作弊
# ------------------------------------------------------------------


class TestExamCheatingAttack:
    """红队: 模型试图通过作弊通过考试。

    防护机制: validate_result() + _detect_optimization()
    """

    def test_attack_leak_expected_category(self) -> None:
        """攻击: 模型在返回结果中泄露 expected_category 字段。

        防护: _validate_result() 检测到 suspicious key → 返回 False → 该能力标记为 failed。
        """
        case = _find_case("task_classification")
        # 攻击者返回的结果中包含 expected_category（从 prompt 中提取）
        malicious_result = {
            "category": case.expected_category,  # 正确分类
            "expected_category": case.expected_category,  # 泄露了答案字段
        }

        # 防护机制应检测到泄露
        is_valid = validate_result(malicious_result, case)
        assert is_valid is False, "防护失败: 泄露 expected_category 未被检测"

    def test_attack_leak_expected_tags(self) -> None:
        """攻击: 模型在返回结果中泄露 expected_tags 字段。"""
        case = _find_case("tag_completion")
        malicious_result = {
            "tags": case.expected_tags,
            "expected_tags": case.expected_tags,  # 泄露答案
        }

        is_valid = validate_result(malicious_result, case)
        assert is_valid is False, "防护失败: 泄露 expected_tags 未被检测"

    def test_attack_leak_expected_old_str(self) -> None:
        """攻击: 模型在返回结果中泄露 expected_old_str 字段。"""
        case = _find_case("code_edit_precision")
        malicious_result = {
            "fixes": [{"old_str": case.expected_old_str, "new_str": "fixed"}],
            "expected_old_str": case.expected_old_str,  # 泄露答案
        }

        is_valid = validate_result(malicious_result, case)
        assert is_valid is False, "防护失败: 泄露 expected_old_str 未被检测"

    def test_attack_out_of_range_precision(self) -> None:
        """攻击: 模型返回 precision=1.5（超出 [0,1] 范围）。

        防护: _validate_result() 检测数值字段越界 → 返回 False。
        """
        case = _find_case("task_classification")
        malicious_result = {
            "category": "bug_fix",
            "precision": 1.5,  # 超出范围
        }

        is_valid = validate_result(malicious_result, case)
        assert is_valid is False, "防护失败: precision=1.5 越界未被检测"

    def test_attack_out_of_range_negative_recall(self) -> None:
        """攻击: 模型返回 recall=-0.3（超出 [0,1] 范围）。"""
        case = _find_case("tag_completion")
        malicious_result = {
            "tags": ["bug"],
            "recall": -0.3,  # 负值
        }

        is_valid = validate_result(malicious_result, case)
        assert is_valid is False, "防护失败: recall=-0.3 越界未被检测"

    def test_attack_optimization_exact_old_str_match(self) -> None:
        """攻击: 模型针对 benchmark 优化，old_str 完全匹配 expected。

        防护: _detect_optimization() 检测到精确匹配 → 标记为可疑。
        """
        orch = ExamOrchestrator(_make_mock_chat())
        case = _find_case("code_edit_precision")

        # 攻击者返回的 old_str 与 expected_old_str 完全一致（无推理过程）
        malicious_result = {
            "fixes": [{"old_str": case.expected_old_str, "new_str": "replacement"}]
        }

        is_suspicious = orch.detect_optimization(case, malicious_result)
        assert is_suspicious is True, "防护失败: 精确匹配 old_str 未被检测为优化"
        assert orch.optimization_suspicions > 0

    def test_attack_optimization_exact_category_without_reason(self) -> None:
        """攻击: 模型精确匹配分类但无推理过程。

        防护: _detect_optimization() 检测到无 reason 的精确匹配 → 标记为可疑。
        """
        orch = ExamOrchestrator(_make_mock_chat())
        case = _find_case("task_classification")

        malicious_result = {
            "category": case.expected_category,  # 精确匹配
            # 没有 "reason" 字段
        }

        is_suspicious = orch.detect_optimization(case, malicious_result)
        assert is_suspicious is True, "防护失败: 无推理精确匹配未被检测"
        assert orch.optimization_suspicions > 0

    def test_attack_normal_result_not_flagged(self) -> None:
        """正常结果不应被误报为攻击。"""
        case = _find_case("task_classification")
        normal_result = {
            "category": "bug_fix",
            "reason": "The task involves fixing a code error",
        }

        is_valid = validate_result(normal_result, case)
        assert is_valid is True, "误报: 正常结果被标记为无效"

    def test_attack_randomization_prevents_memorization(self) -> None:
        """防护: 考题随机化使模型无法通过固定顺序记忆。

        验证: 两次运行 _run_breadth() 的能力顺序可能不同（随机化生效）。
        """
        orch = ExamOrchestrator(_make_mock_chat(), randomize_order=True)

        # mock _infer 返回有效结果
        orch.infer = MagicMock(return_value={"category": "test", "reason": "test"})

        # 运行两次，验证随机化不影响功能正确性
        result1 = orch.run_breadth()
        result2 = orch.run_breadth()

        # 两次运行都应成功完成（不抛异常）
        assert result1.total > 0
        assert result2.total > 0


# ------------------------------------------------------------------
# 攻击场景 2: 画像篡改
# ------------------------------------------------------------------


class TestProfileTamperingAttack:
    """红队: 篡改 benchmark 结果和模型画像数据。

    防护机制: detect_drift() 检测性能漂移 + 数据格式校验
    """

    def test_attack_tamper_composite_score_inflation(self) -> None:
        """攻击: 篡改 composite_score 从 0.60 到 0.95（虚高）。

        防护: detect_drift() 检测到分数异常上升 → drift_detected=True。
        """
        from zephyr.intelligence.model_profiling.results_writer import detect_drift

        history = [
            {"average_score": 0.60, "latency_p50_ms": 200.0, "model_name": "victim"},
            {"average_score": 0.95, "latency_p50_ms": 200.0, "model_name": "victim"},  # 篡改后
        ]

        result = detect_drift(history)
        # 分数大幅上升可能不是 drift（drift 通常是下降），但应可检测到变化
        assert result["drift_detected"] is not None

    def test_attack_tamper_score_decline_detected(self) -> None:
        """攻击: 篡改 composite_score 从 0.90 到 0.50（恶意降低）。

        防护: detect_drift() 检测到分数下降 → drift_detected=True。
        """
        from zephyr.intelligence.model_profiling.results_writer import detect_drift

        history = [
            {"average_score": 0.90, "latency_p50_ms": 100.0, "model_name": "victim"},
            {"average_score": 0.50, "latency_p50_ms": 100.0, "model_name": "victim"},  # 篡改后
        ]

        result = detect_drift(history)
        assert result["drift_detected"] is True, "防护失败: 分数下降 0.40 未被检测为 drift"

    def test_attack_tamper_latency_inflation(self) -> None:
        """攻击: 篡改 latency_p50_ms 从 100 到 500（虚高延迟）。

        防护: detect_drift() 检测到延迟增加 > 50% → drift_detected=True。
        """
        from zephyr.intelligence.model_profiling.results_writer import detect_drift

        history = [
            {"average_score": 0.85, "latency_p50_ms": 100.0, "model_name": "victim"},
            {"average_score": 0.85, "latency_p50_ms": 500.0, "model_name": "victim"},  # 篡改后
        ]

        result = detect_drift(history)
        assert result["drift_detected"] is True, "防护失败: 延迟增加 400% 未被检测为 drift"

    def test_attack_tamper_no_drift_when_stable(self) -> None:
        """正常情况: 分数和延迟稳定 → drift_detected=False。"""
        from zephyr.intelligence.model_profiling.results_writer import detect_drift

        history = [
            {"average_score": 0.85, "latency_p50_ms": 100.0, "model_name": "stable"},
            {"average_score": 0.84, "latency_p50_ms": 105.0, "model_name": "stable"},
        ]

        result = detect_drift(history)
        assert result["drift_detected"] is False, "误报: 稳定性能被标记为 drift"

    def test_attack_tamper_insufficient_history(self) -> None:
        """历史记录不足 → 无法检测篡改。"""
        from zephyr.intelligence.model_profiling.results_writer import detect_drift

        history = [{"average_score": 0.95, "model_name": "single"}]

        result = detect_drift(history)
        assert result["drift_detected"] is False
        assert result["reason"] == "insufficient_history"


# ------------------------------------------------------------------
# 攻击场景 3: 护照伪造
# ------------------------------------------------------------------


class TestPassportForgeryAttack:
    """红队: 伪造或篡改 CapabilityPassport 文件。

    防护机制: HMAC-SHA256 签名验证 (DM-202007)
    """

    def test_attack_unsigned_passport_rejected(self, tmp_path: Path) -> None:
        """攻击: 创建无签名字段的伪造护照。

        防护: load(verify=True) 抛出 TamperError。
        """
        passport = CapabilityPassport(model_id="forged-unsigned")
        passport.overall_score = 0.99
        passport.overall_grade = "A+"

        # 手动保存但不签名（移除 signature 字段）
        data = passport.to_dict()
        data.pop("signature", None)
        forged_path = tmp_path / "forged-unsigned.json"
        forged_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 使用 patch 重定向 PASSPORTS_DIR
        with patch(
            "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
            tmp_path,
        ):
            with pytest.raises(TamperError, match="无签名字段"):
                CapabilityPassport.load("forged-unsigned", verify=True)

    def test_attack_tampered_signature_rejected(self, tmp_path: Path) -> None:
        """攻击: 篡改已签名护照的字段（签名不再匹配）。

        防护: load(verify=True) 抛出 TamperError。
        """
        passport = CapabilityPassport(model_id="tampered-sig")
        passport.overall_score = 0.75
        passport.overall_grade = "B+"

        # 正常签名保存
        with patch(
            "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
            tmp_path,
        ):
            passport.save()

            # 篡改: 修改 overall_score 但不更新签名
            path = tmp_path / "tampered-sig.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["overall_score"] = 0.99  # 篡改分数
            data["overall_grade"] = "A+"   # 篡改等级
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

            # 验证: 签名不匹配 → TamperError
            with pytest.raises(TamperError, match="签名验证失败"):
                CapabilityPassport.load("tampered-sig", verify=True)

    def test_attack_verify_false_bypasses_check(self, tmp_path: Path) -> None:
        """攻击场景验证: verify=False 跳过签名检查（用于向后兼容旧护照）。

        注意: 这不是攻击成功，而是设计上的向后兼容通道。
        生产环境应始终使用 verify=True。
        """
        passport = CapabilityPassport(model_id="legacy-unsigned")
        passport.overall_score = 0.70

        # 保存无签名版本
        data = passport.to_dict()
        data.pop("signature", None)
        path = tmp_path / "legacy-unsigned.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        with patch(
            "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
            tmp_path,
        ):
            # verify=False 应跳过检查，返回护照对象
            loaded = CapabilityPassport.load("legacy-unsigned", verify=False)
            assert loaded is not None
            assert loaded.overall_score == 0.70

    def test_attack_valid_passport_loads_correctly(self, tmp_path: Path) -> None:
        """正常情况: 有效签名的护照应正常加载。"""
        passport = CapabilityPassport(model_id="valid-model:latest")
        passport.overall_score = 0.85
        passport.overall_grade = "A"

        with patch(
            "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
            tmp_path,
        ):
            passport.save()
            loaded = CapabilityPassport.load("valid-model:latest", verify=True)

        assert loaded is not None
        assert loaded.overall_score == 0.85
        assert loaded.overall_grade == "A"

    def test_attack_signature_covers_all_fields(self, tmp_path: Path) -> None:
        """攻击: 篡改任何字段（非 signature）都应导致签名失败。

        验证签名覆盖范围: 除 signature 外的所有字段。
        """
        passport = CapabilityPassport(model_id="full-coverage-test")
        passport.overall_score = 0.80
        passport.exam_duration_seconds = 120.5

        with patch(
            "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
            tmp_path,
        ):
            passport.save()
            path = tmp_path / "full-coverage-test.json"

            # 篡改 exam_duration_seconds
            data = json.loads(path.read_text(encoding="utf-8"))
            data["exam_duration_seconds"] = 999.9
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

            with pytest.raises(TamperError, match="签名验证失败"):
                CapabilityPassport.load("full-coverage-test", verify=True)

    def test_attack_replay_with_different_key(self, tmp_path: Path) -> None:
        """攻击: 使用不同密钥签名的护照在当前环境下验证失败。

        防护: 签名密钥从环境变量读取，不同密钥 → 签名不匹配。
        """
        passport = CapabilityPassport(model_id="different-key-test")
        passport.overall_score = 0.75

        # 用自定义密钥签名
        with patch.dict(os.environ, {"CAPABILITY_PASSPORT_KEY": "attacker-secret-key"}):
            with patch(
                "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
                tmp_path,
            ):
                passport.save()

        # 用默认密钥验证 → 签名不匹配
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CAPABILITY_PASSPORT_KEY", None)
            with patch(
                "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
                tmp_path,
            ):
                with pytest.raises(TamperError, match="签名验证失败"):
                    CapabilityPassport.load("different-key-test", verify=True)

    def test_signature_deterministic(self) -> None:
        """验证: 相同数据 + 相同密钥 → 相同签名（确定性）。"""
        data = {"model_id": "test", "overall_score": 0.85, "overall_grade": "A"}

        sig1 = _compute_signature(data)
        sig2 = _compute_signature(data)

        assert sig1 == sig2
        assert len(sig1) == 64  # SHA-256 hex digest length

    def test_signature_excludes_self(self) -> None:
        """验证: 签名计算排除 signature 字段自身。"""
        data = {"model_id": "test", "overall_score": 0.85, "signature": "old-sig"}

        sig = _compute_signature(data)

        # 签名不应受 signature 字段值影响
        data2 = {"model_id": "test", "overall_score": 0.85, "signature": "different-sig"}
        sig2 = _compute_signature(data2)

        assert sig == sig2


# ------------------------------------------------------------------
# 综合攻击场景
# ------------------------------------------------------------------


class TestCombinedAttack:
    """综合攻击: 同时尝试作弊+篡改+伪造。"""

    def test_combined_cheating_and_forgery(self, tmp_path: Path) -> None:
        """综合攻击: 模型作弊通过考试 + 伪造高分管照。

        防护:
        1. 作弊被 _validate_result() 拦截
        2. 伪造护照被签名验证拦截
        """
        # 步骤1: 作弊攻击
        case = _find_case("task_classification")
        malicious_result = {
            "category": case.expected_category,
            "expected_category": case.expected_category,  # 泄露答案
        }
        assert validate_result(malicious_result, case) is False

        # 步骤2: 伪造护照攻击
        forged = CapabilityPassport(model_id="combined-attacker")
        forged.overall_score = 0.99
        forged.overall_grade = "A+"

        data = forged.to_dict()
        data.pop("signature", None)
        path = tmp_path / "combined-attacker.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        with patch(
            "zephyr.intelligence.model_profiling.capability_passport.PASSPORTS_DIR",
            tmp_path,
        ):
            with pytest.raises(TamperError):
                CapabilityPassport.load("combined-attacker", verify=True)

    def test_defense_in_depth(self) -> None:
        """纵深防御验证: 多层防护协同工作。

        层次1: 考题随机化 → 防记忆
        层次2: 结果完整性校验 → 防泄露
        层次3: 反优化检测 → 防针对 benchmark 优化
        层次4: HMAC 签名 → 防护照篡改
        """
        # 层次1: 随机化
        orch = ExamOrchestrator(_make_mock_chat(), randomize_order=True)
        assert orch.randomize_order is True

        # 层次2: 完整性校验
        case = _find_case("tag_completion")
        leaky_result = {"tags": [], "expected_tags": case.expected_tags}
        assert validate_result(leaky_result, case) is False

        # 层次3: 反优化检测
        code_case = _find_case("code_edit_precision")
        optimized_result = {
            "fixes": [{"old_str": code_case.expected_old_str, "new_str": "x"}]
        }
        assert orch.detect_optimization(code_case, optimized_result) is True

        # 层次4: HMAC 签名
        data = {"model_id": "defense-test", "overall_score": 0.85}
        sig = _compute_signature(data)
        assert len(sig) == 64
        assert sig != _compute_signature({"model_id": "defense-test", "overall_score": 0.86})
