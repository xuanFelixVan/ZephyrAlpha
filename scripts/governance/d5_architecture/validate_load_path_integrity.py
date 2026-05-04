#!/usr/bin/env python3
"""
GATE-22：AI加载路径完整性门禁（validate_load_path_integrity.py）
================================================================

__manifest__ = """
args:
- {flag: --check, type: bool, description: "验证§8.2所有路径存在"}
- {flag: --fix, type: bool, description: "报告缺失但不自动修复（路径需人工裁决）"}
description: >
  解析 AGENTS.md §8.2 任务菜单中的所有文件路径，逐条验证文件存在。
  对标 §6.18 AI加载路径不可漂移铁律——§8.2 路径映射必须永久准确。
dimensions:
- D5
priority: P0
timeout_seconds: 15
warn_only: false
"""


权威依据
--------
AGENTS.md §6.18 AI加载路径不可漂移铁律：
  §8.2 任务菜单 = AI 找到规则文件的唯一入口。
  路径变更 → MUST grep §8.2 确认无旧路径引用。

检测范围
--------
  AGENTS.md §8.2 任务菜单中所有声明的文件路径（含 base path 前缀
  `D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\`）。

门禁逻辑
--------
  - 逐条读取 §8.2 表格
  - 合并 base path + relative paths
  - 验证每条路径对应的文件存在
  - 缺失 → exit(1) 阻断提交

Usage:
    python validate_load_path_integrity.py --check
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"

BASE_PATH = REPO_ROOT / "docs" / "01_policies_and_standards"

PATH_MAP = {
    "config/": REPO_ROOT,
    "scripts/": REPO_ROOT,
    "src/": REPO_ROOT,
    "pyproject.toml": REPO_ROOT,
    ".pre-commit-config.yaml": REPO_ROOT,
}


def extract_paths_from_agents_md() -> list[str]:
    content = AGENTS_PATH.read_text(encoding="utf-8")
    paths = set()
    pattern = re.compile(r"`([a-zA-Z0-9_/.\-]+)`")

    in_section82 = False
    for line in content.split("\n"):
        if "8.2" in line and line.strip().startswith("###"):
            in_section82 = True
            continue
        if in_section82 and line.strip().startswith("###") and "8.2" not in line:
            break
        if not in_section82:
            continue

        for match in pattern.finditer(line):
            raw = match.group(1)
            if "/" not in raw and "." not in raw:
                continue
            if any(raw.endswith(ext) for ext in (".md", ".yaml", ".yml", ".py", ".toml", ".yaml")):
                paths.add(raw)
            elif raw.endswith(".yaml"):
                paths.add(raw)

    return list(paths)


def resolve_path(ref: str) -> Path | None:
    for prefix, root in PATH_MAP.items():
        if ref.startswith(prefix) or ref == prefix.rstrip("/"):
            return root / ref
    return BASE_PATH / ref.lstrip("/")


def main() -> None:
    paths = extract_paths_from_agents_md()

    if not paths:
        print("GATE-22 SKIP: 未在 §8.2 中找到可解析的路径引用。")
        sys.exit(0)

    missing = []
    found = 0
    for p in sorted(paths):
        resolved = resolve_path(p)
        if resolved.exists():
            found += 1
        else:
            missing.append(str(p))

    total = len(paths)
    if not missing:
        print(f"GATE-22 PASS: §8.2 中 {total} 条路径全部可访问。")
        sys.exit(0)

    print(f"GATE-22 FAIL: {len(missing)}/{total} 条路径不存在:")
    print(f"  已通过: {found}")
    for m in missing[:10]:
        print(f"  缺失:   {m}")
    if len(missing) > 10:
        print(f"  ... 及另外 {len(missing) - 10} 条")
    sys.exit(1)


if __name__ == "__main__":
    main()
