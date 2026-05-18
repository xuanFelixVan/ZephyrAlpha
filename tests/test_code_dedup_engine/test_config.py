# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_config
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""config.py 加载测试."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_config_import():
    from zephyr.l01_infrastructure.code_dedup_engine.config import PROJECT_SCALE_TIERS
    assert len(PROJECT_SCALE_TIERS) == 4
    assert "Tier1_small" in PROJECT_SCALE_TIERS


def test_get_tier_for_small_project():
    from zephyr.l01_infrastructure.code_dedup_engine.config import get_tier_for_project
    tier = get_tier_for_project(3000)
    assert tier["name"] == "小型项目"


def test_get_tier_for_large_project():
    from zephyr.l01_infrastructure.code_dedup_engine.config import get_tier_for_project
    tier = get_tier_for_project(30000)
    assert tier["name"] == "大型项目"


def test_path_thresholds():
    from zephyr.l01_infrastructure.code_dedup_engine.config import PATH_THRESHOLDS
    assert PATH_THRESHOLDS["shared"] == 0.3
    assert PATH_THRESHOLDS["tests"] == 0.9
