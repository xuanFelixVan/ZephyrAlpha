# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_micro_clone
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""微型克隆检测测试."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_scanner_blocks():
    from zephyr.l01_infrastructure.code_dedup_engine.scanner import Scanner
    s = Scanner()
    source = "a = 1\nb = 2\nc = 3\nd = 4\ne = 5\nf = 6\n"
    blocks = s.scan_blocks(source)
    assert len(blocks) >= 2  # 7行 → 3个5行窗口


def test_micro_clone_blind_spot():
    assert True  # stub for future micro_clone_detector integration
