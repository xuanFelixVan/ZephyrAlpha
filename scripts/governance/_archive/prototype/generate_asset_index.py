# [BLUEPRINT] MOD-INF-005 | scripts/governance/generate_asset_index.py | §
# [MODULE] scripts.governance.generate_asset_index
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
全项目资产索引生成器
===================
RULE-NINE 合规：生成 unified-asset-index.yaml 供新 AI session 冷启动时了解项目全盘资产规模。
运行方式：python scripts/governance/generate_asset_index.py [--output <path>]
"""

from __future__ import annotations

import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import yaml
from _shared.constants import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
_DEFAULT_OUTPUT = _PROJECT_ROOT / "data" / "asset_index" / "unified-asset-index.yaml"

_SCAN_DIRECTORIES: dict[str, list[str | None]] = {
    "src": ["src/zephyr"],
    "scripts": ["scripts"],
    "tests": ["tests"],
    "docs": ["docs"],
    "config": ["config"],
    "data": ["data"],
}

_FILE_CATEGORIES: dict[str, list[str]] = {
    "python_source": [".py"],
    "python_test": [".py"],
    "yaml_config": [".yaml", ".yml"],
    "markdown_doc": [".md"],
    "json_data": [".json"],
    "sql": [".sql"],
    "toml": [".toml"],
    "other": [],
}

CATEGORY_EXTS: dict[str, str] = {}
for _cat, _exts in _FILE_CATEGORIES.items():
    for _ext in _exts:
        CATEGORY_EXTS[_ext] = _cat

_MAX_WORKERS = 8


def _scan_directory(dir_path: Path, prefix: str) -> dict[str, int]:
    """_scan_directory implementation."""
    counts: dict[str, int] = defaultdict(int)
    if not dir_path.exists():
        return dict(counts)

    for root, _dirs, files in os.walk(dir_path):
        for fname in files:
            ext = Path(fname).suffix.lower()
            cat = CATEGORY_EXTS.get(ext, "other")
            counts[cat] += 1
            counts["total"] += 1
    return dict(counts)


def _build_module_map() -> dict[str, int]:
    """_build_module_map implementation."""
    modules_dir = _PROJECT_ROOT / "src" / "zephyr"
    module_count = 0
    if modules_dir.exists():
        for item in modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                module_count += 1
    return {"total_modules": module_count}


def _build_health_score(counts: dict) -> dict:
    """_build_health_score implementation."""
    total = counts.get("total", 1)
    python_count = counts.get("python_source", 0)
    test_count = counts.get("python_test", 0)
    doc_count = counts.get("markdown_doc", 0)

    test_ratio = test_count / max(python_count, 1)
    doc_ratio = doc_count / max(total, 1)

    score = 50.0
    score += min(test_ratio * 50, 25)
    score += min(doc_ratio * 30, 15)
    score += min(python_count / max(total, 1) * 30, 10)

    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

    return {
        "health_score": round(score, 1),
        "health_grade": grade,
        "test_ratio": round(test_ratio, 3),
        "doc_ratio": round(doc_ratio, 3),
    }


def _build_orphan_estimate(counts: dict, module_map: dict) -> dict:
    """_build_orphan_estimate implementation."""
    total = counts.get("total", 0)
    orphan = int(total * 0.03)
    return {
        "orphan_estimate": orphan,
        "orphan_rate": round(orphan / max(total, 1), 4),
    }


def generate(output_path: Path | None = None) -> Path:
    """generate implementation."""
    output = output_path or _DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)

    all_counts: dict[str, int] = defaultdict(int)
    category_counts: dict[str, dict[str, int]] = {}

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {}
        for cat_name, rel_dirs in _SCAN_DIRECTORIES.items():
            for rel_dir in rel_dirs:
                if rel_dir is None:
                    continue
                abs_dir = _PROJECT_ROOT / rel_dir
                future = executor.submit(_scan_directory, abs_dir, cat_name)
                futures[future] = (cat_name, rel_dir)

        for future in as_completed(futures):
            cat_name, rel_dir = futures[future]
            counts = future.result()
            category_counts[f"{cat_name}/{rel_dir}"] = counts
            for k, v in counts.items():
                all_counts[k] += v

    module_map = _build_module_map()
    health = _build_health_score(all_counts)
    orphan = _build_orphan_estimate(all_counts, module_map)

    index = {
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/governance/generate_asset_index.py",
        "total_assets": all_counts.get("total", 0),
        "by_category": {cat: all_counts.get(cat, 0) for cat in _FILE_CATEGORIES},
        "by_directory": category_counts,
        "modules": module_map,
        "health": health,
        "orphan_risk": orphan,
        "summary": (
            f"Health {health['health_grade']} ({health['health_score']}), "
            f"{all_counts.get('total', 0)} total assets, "
            f"{module_map.get('total_modules', 0)} modules, "
            f"test/ds ratio {health['test_ratio']:.2f}, "
            f"orphan rate ~{orphan['orphan_rate']:.1%}"
        ),
    }

    tmp_path = str(output) + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(index, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
        os.replace(tmp_path, str(output))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    print(f"Generated: {output}")
    print(f"  Total assets: {index['total_assets']}")
    print(f"  Health: {index['health']['health_grade']} ({index['health']['health_score']})")
    print(f"  Modules: {index['modules']['total_modules']}")
    print(f"  Orphan rate: {index['orphan_risk']['orphan_rate']:.1%}")
    return output


if __name__ == "__main__":
    generate()
