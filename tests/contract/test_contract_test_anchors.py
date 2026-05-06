"""contract_test_anchors.yaml 中登记的路径必须存在。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ANCHORS = REPO_ROOT / "tests/contract/contract_test_anchors.yaml"


def _paths_for_entry(rel: Any) -> list[str]:
    if isinstance(rel, list):
        return [str(x).replace("\\", "/") for x in rel]
    return [str(rel).replace("\\", "/")]


def test_anchor_files_exist() -> None:
    data = yaml.safe_load(ANCHORS.read_text(encoding="utf-8"))
    anchors = data.get("anchors", {})
    assert anchors, "anchors 为空"
    for contract_id, rel in anchors.items():
        for rel_one in _paths_for_entry(rel):
            path = REPO_ROOT / rel_one
            assert path.is_file(), f"{contract_id} → {path} 不存在"
