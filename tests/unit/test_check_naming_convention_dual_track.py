# [A_test] module_id: SRC-TST-2026 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-643 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_check_naming_convention_dual_track
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
GATE-11 module_id 双轨制单测（裁定#208 R1/R4）
================================================

权威依据：`docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml`（版本号动态读取并拼入消息；双轨制生效性由关键词实质性校验，不硬编码版本下界）
（L1037-1040 模块ID格式 condition — layer-master 轨 + domain-functional 派生轨 scoped 适用）

测试组：
- TestDualTrackRegexes：双轨正则常量逐值校验（layer-master / domain-derived / D-prefix）
- TestN06DualTrackFormat：_check_n06_dual_track_format helper 端到端校验
- TestValidateSsotLinkage：_validate_ssot_linkage SSoT 机械联动校验
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "scripts" / "governance" / "d3_metadata"))

from check_naming_convention import (  # noqa: E402
    _MODULE_ID_D_PREFIX_RE,
    _MODULE_ID_DOMAIN_DERIVED_RE,
    _MODULE_ID_LAYER_MASTER_RE,
    _check_n06_dual_track_format,
    _validate_ssot_linkage,
)


def _rules(violations: list) -> set[str]:
    return {v.rule for v in violations}


# ---------------------------------------------------------------------------
# TestDualTrackRegexes：双轨正则常量逐值校验
# ---------------------------------------------------------------------------


class TestDualTrackRegexes:
    """裁定#208 R1/R4：双轨正则 MOD-{LAYER}-{SEQ} + MOD-{DOMAIN_FRAGMENT}[-NNN] + D-XXX-{SEQ}。"""

    # layer-master 轨 pass（序号必填）
    def test_layer_master_pass_mod_l00_001(self):
        assert _MODULE_ID_LAYER_MASTER_RE.match("MOD-L00-001")

    def test_layer_master_pass_mod_inf_005(self):
        assert _MODULE_ID_LAYER_MASTER_RE.match("MOD-INF-005")

    def test_layer_master_pass_mod_l01_012(self):
        assert _MODULE_ID_LAYER_MASTER_RE.match("MOD-L01-012")

    # layer-master 轨 fail（无序号）
    def test_layer_master_fail_no_seq_mod_inf(self):
        assert _MODULE_ID_LAYER_MASTER_RE.match("MOD-INF") is None

    def test_layer_master_fail_pure_number_mod_001(self):
        assert _MODULE_ID_LAYER_MASTER_RE.match("MOD-001") is None

    # domain-functional 派生轨 pass（序号可选）
    def test_domain_derived_pass_no_seq_ashare_signal(self):
        assert _MODULE_ID_DOMAIN_DERIVED_RE.match("MOD-ASHARE_SIGNAL")

    def test_domain_derived_pass_with_seq_ashare_signal_001(self):
        assert _MODULE_ID_DOMAIN_DERIVED_RE.match("MOD-ASHARE_SIGNAL-001")

    def test_domain_derived_pass_single_word_data(self):
        assert _MODULE_ID_DOMAIN_DERIVED_RE.match("MOD-DATA")

    # D-前缀派生轨 pass（序号必填）
    def test_d_prefix_pass_mkt_data_001(self):
        assert _MODULE_ID_D_PREFIX_RE.match("D-MKT_DATA-001")

    def test_d_prefix_fail_no_seq(self):
        assert _MODULE_ID_D_PREFIX_RE.match("D-MKT_DATA") is None


# ---------------------------------------------------------------------------
# TestN06DualTrackFormat：_check_n06_dual_track_format helper 端到端
# ---------------------------------------------------------------------------


class TestN06DualTrackFormat:
    """裁定#208 R4：scope 前缀通过后，校验 MOD-*/D-* module_id 双轨格式。"""

    def test_underscore_mod_prefix_violation(self):
        """MOD_XX_001 — MOD 前缀后必须用连字符，禁止下划线。"""
        content = "module_id: MOD_XX_001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert "N-06" in _rules(vs)
        assert any("MOD 前缀后必须用连字符" in v.message for v in vs)

    def test_underscore_d_prefix_violation(self):
        """D_MKT_001 — D 前缀后必须用连字符，禁止下划线。"""
        content = "module_id: D_MKT_001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert "N-06" in _rules(vs)

    def test_layer_master_pass(self):
        content = "module_id: MOD-L00-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_domain_derived_no_seq_pass(self):
        content = "module_id: MOD-ASHARE_SIGNAL\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_domain_derived_with_seq_pass(self):
        content = "module_id: MOD-ASHARE_SIGNAL-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_d_prefix_pass(self):
        content = "module_id: D-MKT_DATA-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_pure_number_violation(self):
        """MOD-001 — 既非 layer-master（层码需字母开头）也非派生轨（需域片段）。"""
        content = "module_id: MOD-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert "N-06" in _rules(vs)

    def test_layer_code_no_seq_format_pass(self):
        """MOD-INF — 格式层 pass（domain-derived 正则匹配单字大写），
        语义判定交 N-17 token 共享测试（裁定#208 §五 R3）。"""
        content = "module_id: MOD-INF\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_multiple_mixed_values(self):
        """多 module_id 同文件：违规与合规共存，仅违规被报。"""
        content = (
            "module_id: MOD_XX_001\n"
            "module_id: MOD-ASHARE_SIGNAL\n"
            "module_id: MOD-L00-001\n"
            "module_id: D_MKT_002\n"
        )
        vs = _check_n06_dual_track_format("fake.yaml", content)
        rules = _rules(vs)
        assert "N-06" in rules
        # 应有 2 个违规（MOD_XX_001 + D_MKT_002）
        assert len(vs) == 2

    def test_code_block_skipped(self):
        """markdown 代码块内的 module_id 示例不误判。"""
        content = "```\nmodule_id: MOD_XX_001\n```\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_dedup_same_value(self):
        """同一 module_id 多次出现只报一次。"""
        content = "module_id: MOD_XX_001\nmodule_id: MOD_XX_001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert len(vs) == 1


# ---------------------------------------------------------------------------
# TestValidateSsotLinkage：SSoT 机械联动校验（裁定#208 R4）
# ---------------------------------------------------------------------------


class TestValidateSsotLinkage:
    """裁定#208 R4：SSoT(trae_028) 与脚本双轨正则机械联动一致。"""

    def test_linkage_returns_true(self):
        """SSoT 双轨制 condition 已生效，联动校验应通过（版本号动态，不硬编码）。"""
        ok, msg = _validate_ssot_linkage()
        assert ok is True, msg
        # 版本号由被测函数从 YAML 动态读取并拼入 msg；测试仅校验格式（下界校验已从被测函数
        # 删除——版本号只升不降使 >= 1.3.0 永真为死代码；保留则 (1,3,0) 在被测函数+测试双处
        # 硬编码，真源缺位，违背真源唯一原则。双轨制 enforcement 由 check 2 正则定义存在性兜底）
        m = re.search(r"v(\d+)\.(\d+)\.(\d+)", msg)
        assert m, f"msg 未含版本号模式: {msg}"
        assert "一致" in msg
