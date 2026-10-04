# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §align_all_coverage
# [MODULE] tests.governance.generators.test_align_all_orphan_census
# [DOMAIN] D_GOV_SCRIPTS
# [MODIFY-GUARD] none（纯逻辑测试，tmp 零写盘零 PG 零 git）
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.align_all (_orphan_census_verdict)
# [CONSUMERS] align_all 第十二节阈值判定质量守卫（31 号报告 §接入方案 exit 语义的用例化）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只测纯逻辑核心 _orphan_census_verdict（不触 PG/git/文件系统）；阈值语义=31 号报告
#   §接入方案三行的可执行规约：report-only 恒 0 硬；硬模式 orphans>threshold 计硬；
#   悬空键不随阈值宽限恒硬
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""align_all 第十二节·覆盖账本普查阈值判定单测（裁定#481 接入件，st-joinchk-20261004）。

四情形全覆盖：
1. report-only（threshold=None）：孤儿/悬空键再大也恒 0 硬（首跑基线期 Owner 看数字不阻断）；
2. 硬模式超额：orphans>threshold → 1 硬；
3. 硬模式悬空键：dangling>0 恒计硬（不随阈值宽限，禁静默）；
4. 硬模式达标：orphans≤threshold 且 dangling=0 → 0 硬。
"""

import sys
from pathlib import Path

_GEN_DIR = str(Path(__file__).resolve().parents[3] / "scripts" / "governance" / "d5_architecture" / "generators")
if _GEN_DIR not in sys.path:
    sys.path.insert(0, _GEN_DIR)

from align_all import _orphan_census_verdict  # noqa: E402


def _report(orphans: int, dangling: int) -> dict:
    return {
        "orphans": [{"file": "src/x/i.py"} for _ in range(orphans)],
        "dangling_keys": [{"key": f"MOD-X-{i}", "source_map": "TDM"} for i in range(dangling)],
    }


def test_report_only_always_zero_hard():
    """情形1：threshold=None 恒 0 硬——首跑基线期不阻断（数字进总览报告）。"""
    hard, msgs = _orphan_census_verdict(_report(orphans=2067, dangling=2), None)
    assert hard == 0
    assert any("悬空键" in m for m in msgs)  # 禁静默：仍要播报


def test_hard_mode_orphans_over_threshold():
    """情形2：orphans>threshold → 1 硬。"""
    hard, msgs = _orphan_census_verdict(_report(orphans=101, dangling=0), 100)
    assert hard == 1
    assert any("threshold=100" in m for m in msgs)


def test_hard_mode_dangling_always_hard():
    """情形3：悬空键不随阈值宽限——orphans 达标但 dangling>0 仍 1 硬。"""
    hard, msgs = _orphan_census_verdict(_report(orphans=50, dangling=2), 100)
    assert hard == 1
    assert any("恒硬" in m for m in msgs)


def test_hard_mode_clean_pass():
    """情形4：orphans≤threshold 且 dangling=0 → 0 硬。"""
    hard, msgs = _orphan_census_verdict(_report(orphans=100, dangling=0), 100)
    assert hard == 0
    assert msgs == []


def test_combined_orphans_and_dangling_two_hard():
    """复合：超额+悬空键=2 硬（各计其一）。"""
    hard, _ = _orphan_census_verdict(_report(orphans=999, dangling=3), 100)
    assert hard == 2
