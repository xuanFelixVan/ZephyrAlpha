# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/inject_manifests.py | §
# [MODULE] scripts.governance.generators.inject_manifests
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.generators.__init__
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
inject_manifests.py — __manifest__ 批量注入器

从现有的 script_manifest.yaml（手工维护、117 条目）提取元数据，
注入到对应的 .py 文件中作为 __manifest__ 块。
无 manifest 记录的脚本：从 docstring + 目录路径自动推断。

对标 §6.16 静态清单自动生成铁律：
手工维护的静态清单 → 迁移为脚本内嵌的 __manifest__ Schema 输入。

Usage:
    python scripts/governance/generators/inject_manifests.py --dry-run
    python scripts/governance/generators/inject_manifests.py
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.yaml_utils import load_yaml
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 15
args:
  - {flag: --dry-run, type: bool, description: "仅预览，不修改文件"}
warn_only: false
description: >
  从现有 script_manifest.yaml 批量提取元数据，注入到各 .py 文件中作为 __manifest__ 块。
  对标 §6.16 静态清单自动生成铁律。一次性迁移工具。
"""

SCRIPTS_DIR = REPO_ROOT / "scripts" / "governance"
MANIFEST_PATH = SCRIPTS_DIR / "script_manifest.yaml"

EXCLUDE_DIRS = frozenset({"_shared", "__pycache__", "test_fixtures", "_archive"})  # 治本(ARCH-036 P0-C): 对齐 generate_script_manifest.py，归档目录不注入

DIM_FROM_DIR = {
    "d1_structure": ["D1"],
    "d2_links": ["D2"],
    "d3_metadata": ["D3"],
    "d4_paths": ["D4"],
    "d5_architecture": ["D5"],
    "d6_security": ["D6"],
    "d7_code": ["D7"],
    "d8_doc_sync": ["D8"],
    "d9_knowledge": ["D9"],
    "d10_performance": ["D10"],
    "d11_compliance": ["D11"],
    "d12_ai_hallucination": ["D12"],
    "generators": ["D1", "D5"],
}


def extract_first_docstring_line(source: str) -> str:
    """提取 docstring 中第一行有效描述（跳过元数据头/Usage/Exit codes）。

    治本(ARCH-036 P0-C): 原 logic 会提取到 [BLUEPRINT]/[MODULE] 等元数据行，
    而非实际功能描述。跳过 [ 开头的行可提取到真正的描述。
    """
    m = re.search(r'"""(.*?)"""', source, re.DOTALL)
    if not m:
        return ""
    text = m.group(1).strip()
    lines = [l.strip().lstrip("-").strip() for l in text.split("\n") if l.strip()]
    for l in lines:
        if l and not l.startswith("Usage") and not l.startswith("Exit codes") and not l.startswith("["):
            return l[:120]
    return lines[0][:120] if lines else ""


def infer_dimensions(rel_path: str) -> list[str]:
    """infer_dimensions implementation."""
    for dir_name, dims in DIM_FROM_DIR.items():
        if rel_path.startswith(dir_name + "/") or rel_path == dir_name:
            return dims
    return ["D1"]


def has_manifest(content: str) -> bool:
    """has_manifest implementation."""
    return "__manifest__" in content


def inject_manifest(content: str, manifest_data: dict) -> str:
    """在 docstring 结束后插入 __manifest__ 块。

    治本(ARCH-036 P0-C): 修复注入位置 bug——原 find(空行, find(首三引号))
    会匹配到 docstring 内部空行，导致 __manifest__ 被插入到 docstring 中间。
    正确做法：找 docstring 结束的第二个三引号后的空行。
    """
    yaml_block = yaml.dump(manifest_data, allow_unicode=True, default_flow_style=False).strip()
    block = f'__manifest__ = """\n{yaml_block}\n"""\n'
    # 找 docstring 结束位置（第二个 """）
    first_triple = content.find('"""')
    pos = -1
    if first_triple != -1:
        second_triple = content.find('"""', first_triple + 3)
        if second_triple != -1:
            pos = content.find("\n\n", second_triple + 3)
    # fallback: 找 import/from 语句
    if pos == -1:
        pos = content.find("\nimport")
    if pos == -1:
        pos = content.find("\nfrom ")
    if pos == -1:
        return block + "\n" + content
    return content[: pos + 1] + "\n" + block + "\n" + content[pos + 1 :]


def build_manifest_entry(entry: dict) -> dict:
    """build_manifest_entry implementation."""
    return {
        "dimensions": entry.get("dimensions", []),
        "priority": entry.get("priority", "P2"),
        "timeout_seconds": entry.get("timeout_seconds", 60),
        "args": entry.get("args", []),
        "warn_only": entry.get("warn_only", False),
        "description": entry.get("description", ""),
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="批量注入 __manifest__ 块到治理脚本")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不修改文件")
    args = parser.parse_args()

    existing = load_yaml(MANIFEST_PATH)
    manifest_entries: dict[str, dict] = {}
    for entry in existing.get("scripts", []):
        manifest_entries[entry["name"]] = entry

    injected = 0
    skipped = 0
    missing = []

    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        parts = py_file.relative_to(SCRIPTS_DIR).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue
        if py_file.name == "__init__.py":
            continue

        rel_path = str(py_file.relative_to(SCRIPTS_DIR)).replace("\\", "/")
        content = py_file.read_text(encoding="utf-8")

        if has_manifest(content):
            skipped += 1
            continue

        entry = manifest_entries.get(rel_path)
        if entry and not entry.get("_manifest_missing"):
            # manifest 中有有效记录（非缺失）→ 用 manifest 元数据
            md = build_manifest_entry(entry)
        else:
            # manifest 缺失或 _manifest_missing=true → 从 docstring 推断 description
            # 治本(ARCH-036 P0-C): 原 logic 对 _manifest_missing 文件会提取到 "⚠ 缺失" 警告作 description
            md = {
                "dimensions": (entry.get("dimensions") if entry else None) or infer_dimensions(rel_path),
                "priority": (entry.get("priority") if entry else "P2") or "P2",
                "timeout_seconds": (entry.get("timeout_seconds") if entry else 60) or 60,
                "args": (entry.get("args") if entry else []) or [],
                "warn_only": (entry.get("warn_only") if entry else False) or False,
                "description": extract_first_docstring_line(content) or "⚠ 请补充 description",
            }
            missing.append(rel_path)

        new_content = inject_manifest(content, md)

        if args.dry_run:
            print(f"[DRY-RUN] 将注入: {rel_path}")
        else:
            atomic_write_safe(py_file, new_content)

        injected += 1

    total = injected + skipped
    coverage_pct = (total / (total + len(missing))) * 100 if (total + len(missing)) > 0 else 0

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}结果:")
    print(f"  已注入: {injected} 个脚本")
    print(f"  已有 manifest: {skipped} 个脚本")
    print(f"  无 manifest 数据: {len(missing)} 个脚本（已自动推断）")
    print(f"  总覆盖: {total}/{total + len(missing)} = {coverage_pct:.1f}%")

    if missing:
        print("\n  以下脚本无 manifest 记录，已从 docstring 自动推断:")
        for m in missing[:5]:
            print(f"    - {m}")
        if len(missing) > 5:
            print(f"    ... 及另外 {len(missing) - 5} 个脚本")


if __name__ == "__main__":
    main()
