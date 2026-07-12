# [A_test] module_id: SRC-TST-1565 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_self_scanner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.self_scanner import (
    SelfScanner,
    SelfScanResult,
)


class TestSelfScanner:
    def test_instantiation_default(self):
        scanner = SelfScanner()
        assert scanner is not None

    def test_instantiation_with_dir(self):
        scanner = SelfScanner(engine_dir="src/zephyr/l01-infrastructure/code_dedup_engine")
        assert scanner is not None

    def test_scan_self(self):
        scanner = SelfScanner(engine_dir="src/zephyr/l01-infrastructure/code_dedup_engine")
        result = scanner.scan_self()
        assert isinstance(result, (SelfScanResult, dict, list))
