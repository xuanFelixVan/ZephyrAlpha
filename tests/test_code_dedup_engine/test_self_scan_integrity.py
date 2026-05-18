# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_self_scan_integrity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""引擎自扫描完整性测试 — Engine Dogfooding 基础验证."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_engine_self_import():
    from zephyr.l01_infrastructure.code_dedup_engine import __version__
    assert __version__ == "0.10.0"


def test_all_modules_importable():
    modules = [
        "cache_manager",
        "diff_detector",
        "signature_matcher",
        "scanner",
        "ast_comparator",
        "degradation",
        "report",
        "health_monitor",
        "config",
        "extraction_safety",
        "doom_loop_guard",
        "shared_lifecycle_manager",
        "monoculture_guard",
        "grandfather_manager",
        "atomic_fixer",
    ]
    for mod_name in modules:
        mod = __import__(
            f"zephyr.l01_infrastructure.code_dedup_engine.{mod_name}",
            fromlist=[mod_name],
        )
        assert mod is not None, f"Module {mod_name} import failed"


def test_config_tier_count():
    from zephyr.l01_infrastructure.code_dedup_engine.config import PROJECT_SCALE_TIERS
    assert len(PROJECT_SCALE_TIERS) == 4
