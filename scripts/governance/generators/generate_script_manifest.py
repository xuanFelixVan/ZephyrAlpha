"""
generate_script_manifest.py — 脚本清单自动生成器

扫描 scripts/governance/ 下所有 .py 文件 → 提取 __manifest__ YAML 块 →
生成 script_manifest.yaml。

对标 §6.16 静态清单自动生成铁律。
__manifest__ 块格式：
    __manifest__ = \"\"\"
    dimensions: [D5, D8]
    priority: P0
    timeout_seconds: 30
    description: >
      校验蓝图 §16 与磁盘实际文件的一致性。
    \"\"\"

Usage:
    python scripts/governance/generators/generate_script_manifest.py
    python scripts/governance/generators/generate_script_manifest.py --check
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import REPO_ROOT
from _shared.yaml_utils import load_yaml
from _shared.encoding import ensure_utf8_stdout

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 15
args:
  - {flag: --check, type: bool, description: "检测漂移 + 报告 missing manifest"}
  - {flag: --output, type: str, description: "输出路径"}
warn_only: false
description: >
  扫描 scripts/governance/**/*.py 的 __manifest__ 块，自动生成 script_manifest.yaml。
  对标 §6.16 静态清单自动生成铁律。
"""

SCRIPTS_DIR = REPO_ROOT / "scripts" / "governance"
DEFAULT_OUTPUT = SCRIPTS_DIR / "script_manifest.yaml"

EXCLUDE_DIRS = frozenset({"_shared", "__pycache__"})


def extract_manifest_from_source(source: str) -> dict | None:
    pattern = r'__manifest__\s*=\s*"""\s*\n(.*?)"""'
    match = re.search(pattern, source, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def scan_scripts() -> list[dict]:
    scripts = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        parts = py_file.relative_to(SCRIPTS_DIR).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if py_file.name == "__init__.py":
            continue

        rel_path = str(py_file.relative_to(SCRIPTS_DIR)).replace("\\", "/")
        source = py_file.read_text(encoding="utf-8")
        manifest = extract_manifest_from_source(source)

        if manifest is None:
            scripts.append({
                "name": rel_path,
                "dimensions": [],
                "priority": "P2",
                "timeout_seconds": 60,
                "args": [],
                "warn_only": False,
                "description": "⚠ __manifest__ 缺失——请添加元数据块",
                "_manifest_missing": True,
            })
            continue

        scripts.append({
            "name": rel_path,
            "dimensions": manifest.get("dimensions", []),
            "priority": manifest.get("priority", "P2"),
            "timeout_seconds": manifest.get("timeout_seconds", 60),
            "args": manifest.get("args", []),
            "warn_only": manifest.get("warn_only", False),
            "description": manifest.get("description", ""),
        })

    return scripts


def generate() -> dict:
    scripts = scan_scripts()
    missing = sum(1 for s in scripts if s.get("_manifest_missing"))
    total = len(scripts)
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/governance/generators/generate_script_manifest.py",
        "source": f"scripts/governance/**/*.py → __manifest__ 块",
        "total_scripts": total,
        "with_manifest": total - missing,
        "missing_manifest": missing,
        "scripts": scripts,
    }


def main() -> None:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="从 __manifest__ 块自动生成 script_manifest.yaml")
    parser.add_argument("--check", action="store_true", help="检测漂移 + 报告 missing manifest")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="输出路径")
    args = parser.parse_args()

    result = generate()

    if args.check:
        missing = result["missing_manifest"]
        if missing > 0:
            print(f"WARNING: {missing}/{result['total_scripts']} 个脚本缺少 __manifest__ 块")
        existing = load_yaml(args.output)
        ex_scripts = existing.get("scripts", [])
        if len(ex_scripts) != result["total_scripts"]:
            print(f"DRIFT: 磁盘 {len(ex_scripts)} 脚本 ≠ 实际 {result['total_scripts']} 脚本")
            sys.exit(1)
        print(f"OK: 脚本清单与实际一致（{result['total_scripts']} 个脚本）")
        return

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# 自动生成于 {result['generated_at']}\n")
        f.write(f"# 来源: scripts/governance/**/*.py __manifest__ 块\n")
        f.write(f"# 手工编辑无效——修改请通过各 .py 文件的 __manifest__ 块\n\n")
        yaml.dump(result, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"已生成 {result['total_scripts']} 个脚本清单 → {args.output}")
    if result["missing_manifest"]:
        print(f"⚠ {result['missing_manifest']} 个脚本缺少 __manifest__ 块")


if __name__ == "__main__":
    main()
