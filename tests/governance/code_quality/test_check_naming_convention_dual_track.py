# [A_test] module_id: SRC-TST-2096 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-643 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_check_naming_convention_dual_track
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
GATE-11 module_id 双轨制单测（裁定#208 R1/R4 + R2 治本修订）
================================================

权威依据：`docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml`
（L1044-1048 模块ID格式 condition — layer-master 轨 + domain-functional 派生轨，R2 治本修订后）

R2 治本修订（2026-07-05）：
  - 废除 D-XXX-NNN 作为 module_id 派生轨的合法地位
  - D-XXX-NNN 重定义为 submodule_id 专用（见 trae_028 gov_doc_009）
  - module_id 仅保留双轨：layer-master 轨 + domain-functional 派生轨（均为 MOD- 前缀）
  - validate_module_id_naming.py 新增 SUBMODULE_ID_RE + is_valid_submodule_id 函数

测试组：
- TestDualTrackRegexes：双轨正则常量逐值校验（layer-master / domain-derived / shared）
- TestSubmoduleIdRegexes：submodule_id 正则常量逐值校验（R2 治本修订新增）
- TestN06DualTrackFormat：_check_n06_dual_track_format helper 端到端校验
- TestIsValidModuleId：is_valid_module_id 函数直接校验（R2 治本修订后 D- 前缀触发 fail）
- TestValidateSsotLinkage：_validate_ssot_linkage SSoT 机械联动校验
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "scripts" / "governance" / "d3_metadata"))

from check_naming_convention import (  # noqa: E402
    _MODULE_ID_DOMAIN_DERIVED_RE,
    _MODULE_ID_LAYER_MASTER_RE,
    _MODULE_ID_SHARED_RE,
    _SUBMODULE_ID_RE,
    _check_n06_dual_track_format,
    _validate_ssot_linkage,
    _is_valid_module_id,
)


def _rules(violations: list) -> set[str]:
    return {v.rule for v in violations}


# ---------------------------------------------------------------------------
# TestDualTrackRegexes：双轨正则常量逐值校验
# ---------------------------------------------------------------------------


class TestDualTrackRegexes:
    """裁定#208 R1/R4 + R2 治本修订：双轨正则 MOD-{LAYER}-{SEQ} + MOD-{DOMAIN_FRAGMENT}[-NNN] + SH-{ABBR}-{NNN}。"""

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

    # shared 轨 pass（序号必填）
    def test_shared_pass_sh_db_001(self):
        assert _MODULE_ID_SHARED_RE.match("SH-DB-001")

    def test_shared_fail_no_seq_sh_db(self):
        assert _MODULE_ID_SHARED_RE.match("SH-DB") is None


# ---------------------------------------------------------------------------
# TestSubmoduleIdRegexes：submodule_id 正则常量逐值校验（R2 治本修订新增）
# ---------------------------------------------------------------------------


class TestSubmoduleIdRegexes:
    """R2 治本修订（2026-07-05）：submodule_id 正则 D-{DOMAIN}-NNN。

    D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用。
    真源：trae_028 gov_doc_009_submodule_id_convention
          validate_module_id_naming.py::SUBMODULE_ID_RE
    """

    # submodule_id pass
    def test_submodule_pass_d_factor_01(self):
        assert _SUBMODULE_ID_RE.match("D-FACTOR-01")

    def test_submodule_pass_d_signal_12(self):
        assert _SUBMODULE_ID_RE.match("D-SIGNAL-12")

    def test_submodule_pass_d_mkt_data_03(self):
        assert _SUBMODULE_ID_RE.match("D-MKT_DATA-03")

    # submodule_id fail（无序号）
    def test_submodule_fail_no_seq_d_factor(self):
        assert _SUBMODULE_ID_RE.match("D-FACTOR") is None

    # submodule_id fail（下划线格式——这是 domain_id 格式，不是 submodule_id）
    def test_submodule_fail_underscore_format(self):
        assert _SUBMODULE_ID_RE.match("D_FACTOR_01") is None

    # submodule_id fail（小写）
    def test_submodule_fail_lowercase(self):
        assert _SUBMODULE_ID_RE.match("d-factor-01") is None


# ---------------------------------------------------------------------------
# TestN06DualTrackFormat：_check_n06_dual_track_format helper 端到端
# ---------------------------------------------------------------------------


class TestN06DualTrackFormat:
    """裁定#208 R4 + R2 治本修订：scope 前缀通过后，校验 MOD-*/SH-* module_id 双轨格式。

    R2 治本修订后：D-XXX-NNN 不再是合法 module_id，触发 ERROR。
    """

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

    def test_d_prefix_now_violates_module_id(self):
        """R2 治本修订（2026-07-05）：D-MKT_DATA-001 不再是合法 module_id，触发 ERROR。

        D-XXX-NNN 重定义为 submodule_id 专用，禁止作为 module_id 使用。
        应改用 MOD-{DOMAIN_FRAGMENT}[-NNN] 派生轨（如 MOD-MKT_DATA[-NNN]）。
        """
        content = "module_id: D-MKT_DATA-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert "N-06" in _rules(vs)
        assert any("D-前缀已废弃" in v.message for v in vs)

    def test_d_prefix_simple_now_violates_module_id(self):
        """R2 治本修订：D-GOVERNANCE-001 不再是合法 module_id，触发 ERROR。"""
        content = "module_id: D-GOVERNANCE-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert "N-06" in _rules(vs)

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

    def test_shared_prefix_pass(self):
        """SH-DB-001 — 跨域共享模块 SH-{ABBR}-{NNN} pass。"""
        content = "module_id: SH-DB-001\n"
        vs = _check_n06_dual_track_format("fake.yaml", content)
        assert vs == []

    def test_multiple_mixed_values(self):
        """多 module_id 同文件：违规与合规共存，仅违规被报。

        R2 治本修订后：
          - MOD_XX_001 → 违规（MOD 前缀后必须用连字符）
          - MOD-ASHARE_SIGNAL → pass
          - MOD-L00-001 → pass
          - D_MKT_002 → 违规（D 前缀后必须用连字符）
          - D-MKT_DATA-003 → 违规（D-前缀已废弃为 module_id）
        """
        content = (
            "module_id: MOD_XX_001\n"
            "module_id: MOD-ASHARE_SIGNAL\n"
            "module_id: MOD-L00-001\n"
            "module_id: D_MKT_002\n"
            "module_id: D-MKT_DATA-003\n"
        )
        vs = _check_n06_dual_track_format("fake.yaml", content)
        rules = _rules(vs)
        assert "N-06" in rules
        # 应有 3 个违规（MOD_XX_001 + D_MKT_002 + D-MKT_DATA-003）
        assert len(vs) == 3

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
# TestIsValidModuleId：is_valid_module_id 函数直接校验（R2 治本修订后）
# ---------------------------------------------------------------------------


class TestIsValidModuleId:
    """R2 治本修订后：is_valid_module_id 函数对 D- 前缀触发 fail。

    真源：validate_module_id_naming.py::is_valid_module_id
    """

    def test_layer_master_pass(self):
        ok, reason = _is_valid_module_id("MOD-L00-001")
        assert ok is True
        assert reason == ""

    def test_domain_derived_pass(self):
        ok, reason = _is_valid_module_id("MOD-ASHARE_SIGNAL-001")
        assert ok is True
        assert reason == ""

    def test_shared_pass(self):
        ok, reason = _is_valid_module_id("SH-DB-001")
        assert ok is True
        assert reason == ""

    def test_d_prefix_now_fails_as_module_id(self):
        """R2 治本修订：D-MKT_DATA-001 不再是合法 module_id。"""
        ok, reason = _is_valid_module_id("D-MKT_DATA-001")
        assert ok is False
        assert "废弃" in reason or "已不再" in reason

    def test_d_prefix_simple_now_fails_as_module_id(self):
        """R2 治本修订：D-GOVERNANCE-001 不再是合法 module_id。"""
        ok, reason = _is_valid_module_id("D-GOVERNANCE-001")
        assert ok is False
        assert "废弃" in reason or "已不再" in reason

    def test_unknown_prefix_fails(self):
        ok, reason = _is_valid_module_id("XYZ-001")
        assert ok is False
        assert "MOD" in reason or "SH" in reason


# ---------------------------------------------------------------------------
# TestValidateSsotLinkage：SSoT 机械联动校验（裁定#208 R4）
# ---------------------------------------------------------------------------


class TestValidateSsotLinkage:
    """裁定#208 R4 + R2 治本修订：SSoT(trae_028) 与脚本双轨正则机械联动一致。"""

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
