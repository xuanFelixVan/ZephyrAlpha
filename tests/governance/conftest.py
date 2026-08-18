# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-273 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.conftest
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-273 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""治理脚本测试 — pytest 共享 Fixture"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

_SMOKE_TEST = "governance/d1_structure/run_script_smoke_test.py"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def gov_dir(repo_root: Path) -> Path:
    return repo_root / "scripts" / "governance"


@pytest.fixture(scope="session")
def manifest(repo_root: Path) -> dict:
    import sys

    import yaml

    manifest_path = repo_root / "scripts" / "script-manifest.yaml"
    sys.path.insert(0, str(repo_root / "scripts"))
    with open(manifest_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def script_entries(manifest: dict) -> list[dict]:
    return [
        e
        for e in manifest.get("scripts", [])
        if e.get("path", "").startswith("governance/") and e.get("path", "") != _SMOKE_TEST
    ]


# Phase 1 legacy gate: governance 架构已演进到 20+ 子模块目录，
# test_no_orphan_directories 检查的 8-module 约束已过时（裁定 2026-07-21）
_LEGACY_PHASE1_SKIPS = {"test_no_orphan_directories"}


def pytest_collection_modifyitems(config, items):
    skip = pytest.mark.skip(reason="Phase 1 legacy gate: governance architecture evolved beyond 8-module layout")
    for item in items:
        if item.name in _LEGACY_PHASE1_SKIPS:
            item.add_marker(skip)
