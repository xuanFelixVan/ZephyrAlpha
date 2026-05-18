# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_scanner_raw
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""scanner 单文件测试."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_scanner_tokenize():
    from zephyr.l01_infrastructure.code_dedup_engine.scanner import Scanner
    s = Scanner()
    result = s.scan_file(Path(__file__))
    assert result.token_count > 0
    assert len(result.minhash) > 0


def test_scanner_minhash():
    from zephyr.l01_infrastructure.code_dedup_engine.scanner import Scanner
    s = Scanner()
    r1 = s.scan_file(Path(__file__))
    r2 = s.scan_file(Path(__file__))
    assert r1.minhash == r2.minhash
