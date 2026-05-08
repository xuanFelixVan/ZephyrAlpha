"""治理脚本测试 — pytest 共享 Fixture"""

from __future__ import annotations

from pathlib import Path

import pytest

_SMOKE_TEST = "governance/d1_structure/run_script_smoke_test.py"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="session")
def gov_dir(repo_root: Path) -> Path:
    return repo_root / "scripts" / "governance"


@pytest.fixture(scope="session")
def manifest(repo_root: Path) -> dict:
    import sys

    import yaml

    manifest_path = repo_root / "scripts" / "script_manifest.yaml"
    sys.path.insert(0, str(repo_root / "scripts"))
    with open(manifest_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def script_entries(manifest: dict) -> list[dict]:
    return [
        e for e in manifest.get("scripts", [])
        if e.get("path", "").startswith("governance/")
        and e.get("path") != _SMOKE_TEST
    ]
