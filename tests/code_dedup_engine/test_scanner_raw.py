# [A_test] module_id: SRC-TST-0536 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-364 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_scanner_raw
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""scanner 单文件测试."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_scanner_tokenize():
    from zephyr.infrastructure.asset_inventory.scanner import Scanner

    s = Scanner()
    result = s.scan_file(Path(__file__))
    assert result.token_count > 0
    assert len(result.minhash) > 0


def test_scanner_minhash():
    from zephyr.infrastructure.asset_inventory.scanner import Scanner

    s = Scanner()
    r1 = s.scan_file(Path(__file__))
    r2 = s.scan_file(Path(__file__))
    assert r1.minhash == r2.minhash
