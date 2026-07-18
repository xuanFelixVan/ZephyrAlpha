# [A_test] module_id: SRC-TST-0116 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-273 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
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
        if e.get("path", "").startswith("governance/") and e.get("path") != _SMOKE_TEST
    ]
