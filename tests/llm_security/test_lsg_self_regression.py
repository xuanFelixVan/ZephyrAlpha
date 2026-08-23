# [A_test] module_id: MOD-LLM_SECURITY_self_regression | layer=test | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §35.1
# [MODULE] tests.llm_security.test_lsg_self_regression
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""LSG 自身安全回归测试（蓝图 §35.1 / 09 号文 §4.3 P1-2）。

验证安全规则未被意外削弱：golden 正样本必须全部阻断、负样本不得误拦。
golden 集纯追加演进（蓝图 §35.1：每次发现新攻击模式 → 追加到 golden set）。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.security.llm_defense.llm_security.layers.l1_input import (
    InputDefenseLayer,
    SourceType,
)

_GOLDEN_DIR = Path(__file__).parent / "golden"


def _load_golden(filename: str) -> list[dict[str, str]]:
    path = _GOLDEN_DIR / filename
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{filename}: 顶层必须是 mapping"
    cases = data.get("cases")
    assert isinstance(cases, list) and cases, f"{filename}: cases 必须是非空列表"
    return cases


class TestGoldenSetSchema:
    @pytest.mark.parametrize("filename", ["injection_positive.yaml", "benign_negative.yaml"])
    def test_ids_unique_and_payloads_non_empty(self, filename: str) -> None:
        cases = _load_golden(filename)
        ids = [c["id"] for c in cases]
        assert len(ids) == len(set(ids)), f"{filename}: id 重复"
        for case in cases:
            assert case.get("name"), f"{filename}:{case.get('id')}: name 缺失"
            assert str(case.get("payload", "")).strip(), f"{filename}:{case.get('id')}: payload 为空"


class TestLSGSelfRegression:
    """LSG 自身的安全回归测试——验证安全规则未被意外削弱。"""

    def test_known_injection_patterns_still_detected(self) -> None:
        """验证所有已知注入/越狱模式仍被 L1 正确阻断。"""
        layer = InputDefenseLayer()
        for case in _load_golden("injection_positive.yaml"):
            result = layer.sanitize_and_wrap(case["payload"], SourceType.DIRECT)
            assert result.blocked, f"REGRESSION: {case['id']} '{case['name']}' not blocked!"

    def test_known_bypass_patterns_not_in_positive_set(self) -> None:
        """验证已知良性输入未被误拦（false positive regression）。"""
        layer = InputDefenseLayer()
        for case in _load_golden("benign_negative.yaml"):
            result = layer.sanitize_and_wrap(case["payload"], SourceType.DIRECT)
            assert not result.blocked, f"FALSE POSITIVE: {case['id']} '{case['name']}' blocked! hits={result.hits}"

    # 2026-08-24 实测基线：LLM01 全量 25 变体中 8 条被 L1 拦截（32%）。
    # 未拦截 17 条（中文注入/拆字绕过/多轮渐进/base64 提及等）属 L1 regex
    # 覆盖缺口——蓝图 §40 L1C LLM 辅助检测正是该缺口的设计解法，本批次
    # 登记为发现项（见 CELSG 报告），此处冻结基线防退步，不做假绿断言。
    _LLM01_BLOCKED_BASELINE = 8

    def test_red_team_llm01_payloads_replay(self) -> None:
        """回放 Red Team 载荷库 LLM01（注入类）——拦截数不得低于冻结基线。"""
        payloads_path = (
            Path(__file__).parents[2]
            / "src"
            / "zephyr"
            / "security"
            / "llm_defense"
            / "llm_security"
            / "payloads"
            / "red_team_payloads.yaml"
        )
        data = yaml.safe_load(payloads_path.read_text(encoding="utf-8"))
        layer = InputDefenseLayer()
        blocked = 0
        total = 0
        for entry in data.get("payloads", []):
            if entry.get("category") != "LLM01":
                continue
            for variant in entry.get("variants", []):
                variant = variant.replace("{base64_encoded_payload}", "aWdub3Jl").replace(
                    "{malicious_command}", "id"
                )
                total += 1
                if layer.sanitize_and_wrap(variant, SourceType.DIRECT).blocked:
                    blocked += 1
        assert total == 25, f"LLM01 载荷库规模漂移：期望 25，实测 {total}"
        assert blocked >= self._LLM01_BLOCKED_BASELINE, (
            f"REGRESSION: LLM01 拦截数 {blocked} 低于基线 {self._LLM01_BLOCKED_BASELINE}"
        )
