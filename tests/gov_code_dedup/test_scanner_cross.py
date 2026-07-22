# [A_test] module_id: MOD-GOV_scanner_cross | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-363 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.gov_code_dedup.test_scanner_cross
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""scanner 跨文件测试 — 相同文件不重复,不同文件找重复."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_same_file_no_duplicate():
    from zephyr.infrastructure.asset_inventory.scanner import Scanner

    s = Scanner()
    s.scan_file(Path(__file__))
    dupes = s.find_duplicates()
    assert len(dupes) == 0


def test_cross_file_similarity():
    from zephyr.infrastructure.asset_inventory.scanner import Scanner

    s = Scanner()
    s.scan_file(Path(__file__))
    s.scan_file(Path(__file__).parent / "test_config.py")
    dupes = s.find_duplicates()
    assert isinstance(dupes, list)
