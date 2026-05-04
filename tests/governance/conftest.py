"""治理脚本测试 — pytest 共享 Fixture"""
from __future__ import annotations

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="session")
def gov_dir(repo_root: Path) -> Path:
    return repo_root / "scripts" / "governance"


@pytest.fixture(scope="session")
def manifest(gov_dir: Path) -> dict:
    import sys
    import yaml
    sys.path.insert(0, str(gov_dir))
    manifest_path = gov_dir / "script_manifest.yaml"
    with open(manifest_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def script_entries(manifest: dict) -> list[dict]:
    return [
        e for e in manifest.get("scripts", [])
        if e.get("name") != "d1_structure/run_script_smoke_test.py"
    ]
