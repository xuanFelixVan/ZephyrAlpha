# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.list_ce_files

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
list_ce_files.py — CE 文件清单生成器
=====================================
Task ID : MOD-INF-008-TASK-011
Priority: P2 (beta)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

CE_ROOT = Path(__file__).resolve().parent

CATEGORIES = {
    "source": "*.py",
    "config": "config/**/*.yaml",
    "data": "*.json",
    "other": "*.yaml",
}


def collect_files() -> dict[str, list[dict[str, str]]]:
    manifest: dict[str, list[dict[str, str]]] = {}
    for category, pattern in CATEGORIES.items():
        entries: list[dict[str, str]] = []
        for file_path in sorted(CE_ROOT.glob(pattern)):
            if file_path.name.startswith("_"):
                continue
            rel = str(file_path.relative_to(CE_ROOT))
            entries.append({"path": rel, "size_kb": f"{file_path.stat().st_size / 1024:.1f}"})
        manifest[category] = entries
    return manifest


def generate_manifest() -> str:
    data = {
        "module_id": "MOD-INF-008",
        "root": str(CE_ROOT),
        "files": collect_files(),
        "total_py_files": sum(
            1 for _ in CE_ROOT.glob("*.py")
            if not _.name.startswith("_")
        ),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    print(generate_manifest())
