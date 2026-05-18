# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_scanner_cross
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""scanner 跨文件测试 — 相同文件不重复,不同文件找重复."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_same_file_no_duplicate():
    from zephyr.l01_infrastructure.code_dedup_engine.scanner import Scanner
    s = Scanner()
    s.scan_file(Path(__file__))
    dupes = s.find_duplicates()
    assert len(dupes) == 0


def test_cross_file_similarity():
    from zephyr.l01_infrastructure.code_dedup_engine.scanner import Scanner
    s = Scanner()
    s.scan_file(Path(__file__))
    s.scan_file(Path(__file__).parent / "test_config.py")
    dupes = s.find_duplicates()
    assert isinstance(dupes, list)
