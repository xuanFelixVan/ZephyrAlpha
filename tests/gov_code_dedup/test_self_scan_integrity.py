# [A_test] module_id: MOD-GOV_self_scan_integrity | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-365 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.gov_code_dedup.test_self_scan_integrity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""引擎自扫描完整性测试 — Engine Dogfooding 基础验证."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_engine_self_import():
    from zephyr.governance import __version__

    assert __version__ == "0.15.0"


def test_all_modules_importable():
    modules = [
        "scanner",
        "monoculture_guard",
        "self_scanner",
        "decision_auditor",
        "exit_codes",
        "integration_hub",
        "cli",
        "config",
        "function_discovery",
        "auto_test_generator",
    ]
    for mod_name in modules:
        mod = __import__(
            f"zephyr.testing.code_dedup.{mod_name}",
            fromlist=[mod_name],
        )
        assert mod is not None, f"Module {mod_name} import failed"


def test_config_tier_count():
    from zephyr.gov_code_quality.code_dedup.config import PROJECT_SCALE_TIERS

    assert len(PROJECT_SCALE_TIERS) == 4
