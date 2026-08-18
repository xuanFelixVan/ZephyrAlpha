# [A_test] module_id: MOD-GOV_bypass_policy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_capability_lookup_bypass_policy
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""test_capability_lookup_bypass_policy.py — CAPABILITY-LOOKUP bypass 策略共享模块单测

权威依据：capability_lookup_bypass_policy.py（#ARCH-066 治本——消除 gate/reconciler 双真源）
       trae_077_capability_lookup_scene_classify.yaml v2.0.0（rule_data SSoT）

测试组：
- TestConstants: 模块级常量值正确（BYPASS_MARKER_PREFIX / BYPASS_ENV_VAR / EXEMPT_KEYWORDS / 阈值）
- TestIsExemptReason: 白名单匹配（含归一化 _ → -）+ 非白名单拒绝 + 中文关键词
- TestHasBypassMarker: commit msg 标记检测（命中 / 未命中 / 无闭合 ]）
- TestIsEmergencyBypass: 环境变量检测
- TestLoadBypassPolicy: YAML 加载（正常 / 缺失 fail-open / 字段非法 fail-open）
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


# ---------------------------------------------------------------------------
# TestConstants — 模块级常量
# ---------------------------------------------------------------------------


class TestConstants:
    def test_bypass_marker_prefix(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            BYPASS_MARKER_PREFIX,
        )
        assert BYPASS_MARKER_PREFIX == "[no-lookup:"

    def test_bypass_env_var(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            BYPASS_ENV_VAR,
        )
        assert BYPASS_ENV_VAR == "ZEPHYR_BYPASS_LOOKUP"

    def test_exempt_keywords_loaded(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            EXEMPT_KEYWORDS,
        )
        assert isinstance(EXEMPT_KEYWORDS, frozenset)
        # v2.0.0: 16 项关键词
        assert len(EXEMPT_KEYWORDS) >= 16

    def test_thresholds_loaded(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            ESCALATION_THRESHOLD,
            WINDOW,
        )
        assert ESCALATION_THRESHOLD == 5
        assert WINDOW == 10


# ---------------------------------------------------------------------------
# TestIsExemptReason — 白名单匹配
# ---------------------------------------------------------------------------


class TestIsExemptReason:
    def test_whitelist_reason_gate_fix(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("gate-fix-urgent-patch") is True

    def test_whitelist_reason_test_fix(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("test-fix-flaky") is True

    def test_whitelist_reason_sync(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("sync-yaml-to-db") is True

    def test_normalization_underscore_to_hyphen(self):
        """root_cause_fix → 归一化 _ → - 后匹配 root-cause。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("root_cause_fix") is True

    def test_normalization_mechanical_batch(self):
        """mechanical-header-format-fix-batch-3 → 匹配 mechanical。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("mechanical-header-format-fix-batch-3") is True

    def test_normalization_research_done(self):
        """extensive-research-done → 匹配 research。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("extensive-research-done") is True

    def test_chinese_keyword(self):
        """中文关键词 调研 匹配。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("已充分调研TableRegistry接口") is True

    def test_non_whitelist_reason_rejected(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("new-feature-xxx") is False

    def test_non_whitelist_reason_random(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("random-reason") is False

    def test_empty_reason_rejected(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        assert is_exempt_reason("") is False

    def test_custom_keywords_override(self):
        """测试用自定义 keywords 参数。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_exempt_reason,
        )
        custom = frozenset({"my-custom-keyword"})
        assert is_exempt_reason("my-custom-keyword-xxx", keywords=custom) is True
        assert is_exempt_reason("gate-fix", keywords=custom) is False


# ---------------------------------------------------------------------------
# TestHasBypassMarker — commit msg 标记检测
# ---------------------------------------------------------------------------


class TestHasBypassMarker:
    def test_hit_with_reason(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            has_bypass_marker,
        )
        hit, reason = has_bypass_marker("fix: patch [no-lookup:gate-fix-xxx]")
        assert hit is True
        assert reason == "gate-fix-xxx"

    def test_hit_strips_whitespace(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            has_bypass_marker,
        )
        hit, reason = has_bypass_marker("fix [no-lookup:  gate-fix  ]")
        assert hit is True
        assert reason == "gate-fix"

    def test_no_marker(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            has_bypass_marker,
        )
        hit, reason = has_bypass_marker("fix: patch without bypass")
        assert hit is False
        assert reason == ""

    def test_none_msg(self):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            has_bypass_marker,
        )
        hit, reason = has_bypass_marker(None)
        assert hit is False
        assert reason == ""

    def test_no_closing_bracket(self):
        """[no-lookup:reason 无闭合 ] → 未命中。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            has_bypass_marker,
        )
        hit, reason = has_bypass_marker("fix [no-lookup:gate-fix")
        assert hit is False
        assert reason == ""

    def test_empty_reason_hit(self):
        """[no-lookup:] → 命中但 reason 为空（gate 层负责阻断空 reason）。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            has_bypass_marker,
        )
        hit, reason = has_bypass_marker("fix [no-lookup:]")
        assert hit is True
        assert reason == ""


# ---------------------------------------------------------------------------
# TestIsEmergencyBypass — 环境变量检测
# ---------------------------------------------------------------------------


class TestIsEmergencyBypass:
    def test_env_set_to_1(self, monkeypatch):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_emergency_bypass,
        )
        monkeypatch.setenv("ZEPHYR_BYPASS_LOOKUP", "1")
        assert is_emergency_bypass() is True

    def test_env_not_set(self, monkeypatch):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_emergency_bypass,
        )
        monkeypatch.delenv("ZEPHYR_BYPASS_LOOKUP", raising=False)
        assert is_emergency_bypass() is False

    def test_env_set_to_other_value(self, monkeypatch):
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            is_emergency_bypass,
        )
        monkeypatch.setenv("ZEPHYR_BYPASS_LOOKUP", "0")
        assert is_emergency_bypass() is False


# ---------------------------------------------------------------------------
# TestLoadBypassPolicy — YAML 加载 + fail-open
# ---------------------------------------------------------------------------


class TestLoadBypassPolicy:
    def test_loads_from_real_yaml(self):
        """从真实 trae_077 YAML 加载 16 关键词 + 阈值 5/10。"""
        from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
            load_bypass_policy,
        )
        policy = load_bypass_policy()
        assert len(policy["exempt_keywords"]) == 16
        assert policy["escalation_threshold"] == 5
        assert policy["window"] == 10

    def test_yaml_missing_fails_open(self, tmp_path):
        """YAML 文件缺失 → fail-open 返回默认值。"""
        from zephyr.gov_enforcement.commit_gates import capability_lookup_bypass_policy as mod
        with patch.object(mod, "_POLICY_YAML_PATH", tmp_path / "nonexistent.yaml"):
            policy = mod.load_bypass_policy()
        assert len(policy["exempt_keywords"]) >= 16  # 默认值
        assert policy["escalation_threshold"] == 5
        assert policy["window"] == 10

    def test_yaml_invalid_fails_open(self, tmp_path):
        """YAML 内容非法 → fail-open 返回默认值。"""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("::: not valid yaml :::")
        from zephyr.gov_enforcement.commit_gates import capability_lookup_bypass_policy as mod
        with patch.object(mod, "_POLICY_YAML_PATH", bad_yaml):
            policy = mod.load_bypass_policy()
        assert len(policy["exempt_keywords"]) >= 16
        assert policy["escalation_threshold"] == 5

    def test_yaml_top_level_not_dict_fails_open(self, tmp_path):
        """YAML 顶层非 dict → fail-open。"""
        bad_yaml = tmp_path / "list.yaml"
        bad_yaml.write_text("- item1\n- item2\n")
        from zephyr.gov_enforcement.commit_gates import capability_lookup_bypass_policy as mod
        with patch.object(mod, "_POLICY_YAML_PATH", bad_yaml):
            policy = mod.load_bypass_policy()
        assert isinstance(policy["exempt_keywords"], frozenset)

    def test_yaml_custom_keywords_loaded(self, tmp_path):
        """YAML 自定义关键词列表被正确加载。"""
        custom_yaml = tmp_path / "custom.yaml"
        custom_yaml.write_text(
            "bypass_exempt_keywords:\n"
            "  - keyword: custom-kw1\n"
            "  - keyword: custom-kw2\n"
            "thresholds:\n"
            "  escalation_threshold: 3\n"
            "  window: 7\n"
        )
        from zephyr.gov_enforcement.commit_gates import capability_lookup_bypass_policy as mod
        with patch.object(mod, "_POLICY_YAML_PATH", custom_yaml):
            policy = mod.load_bypass_policy()
        assert "custom-kw1" in policy["exempt_keywords"]
        assert "custom-kw2" in policy["exempt_keywords"]
        assert policy["escalation_threshold"] == 3
        assert policy["window"] == 7

    def test_yaml_string_keywords_loaded(self, tmp_path):
        """YAML 关键词列表项为纯字符串也被正确加载。"""
        custom_yaml = tmp_path / "str_kw.yaml"
        custom_yaml.write_text(
            "bypass_exempt_keywords:\n"
            "  - str-kw1\n"
            "  - str-kw2\n"
        )
        from zephyr.gov_enforcement.commit_gates import capability_lookup_bypass_policy as mod
        with patch.object(mod, "_POLICY_YAML_PATH", custom_yaml):
            policy = mod.load_bypass_policy()
        assert "str-kw1" in policy["exempt_keywords"]
        assert "str-kw2" in policy["exempt_keywords"]

    def test_yaml_invalid_threshold_fails_open(self, tmp_path):
        """阈值字段非法 → 用默认值。"""
        custom_yaml = tmp_path / "bad_thresh.yaml"
        custom_yaml.write_text(
            "thresholds:\n"
            "  escalation_threshold: 'not-a-number'\n"
            "  window: -5\n"
        )
        from zephyr.gov_enforcement.commit_gates import capability_lookup_bypass_policy as mod
        with patch.object(mod, "_POLICY_YAML_PATH", custom_yaml):
            policy = mod.load_bypass_policy()
        assert policy["escalation_threshold"] == 5  # 默认
        assert policy["window"] == 10  # 默认（负值 rejected）
