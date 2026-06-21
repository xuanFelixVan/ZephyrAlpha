# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_layer_deps.py | §
"""validate_layer_deps.py — 跨层依赖违规检测



对标：PS-STD-003 COND-30~32（跨层调用 / contracts 放业务层）
     GOV-DOC-002 trae_028_doc_structure_naming.yaml（层依赖纪律）
     MOD-INF-005 蓝图 §3.2（不包含的职责）

检测内容：
- 解析 frontmatter 中的 layer/depends_on 字段
- 检测层间依赖方向违规（下级依赖上级、跨多层的依赖）
- 检测 contracts 文件的位置（应在 _registry/contracts/ 而非业务层）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations
from _shared.encoding import ensure_utf8_stdout
ensure_utf8_stdout()

__manifest__ = """
args: []
description: 跨层依赖违规检测（COND-30~32 — 层纪律）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, REPO_ROOT, SCAN_EXTENSIONS_MD, EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

LAYER_NUMBERS = {
    "L00": 0,
    "L01": 1,
    "L02": 2,
    "L03": 3,
    "L04": 4,
    "L05": 5,
    "L06": 6,
    "L07": 7,
    "L08": 8,
    "L09": 9,
    "L10": 10,
    "L11": 11,
    "L12": 12,
    "L13": 13,
    "L14": 14,
    "cross_layer": -1,
}

CONTRACT_FORBIDDEN_DIRS = {
    "02_enterprise_architecture",
    "03_modules",
}

_EXTRA_EXCLUDE = EXCLUDE_DIRS | {"scripts"}


def scan_layer_violations() -> tuple[list[dict], int]:
    """扫描层级依赖违规."""
    findings: list[dict] = []
    """扫描并返回发现列表."""
    files_scanned = 0
    docs_dir = REPO_ROOT / "docs"

    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        files_scanned += 1
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue

        rel = str(filepath.relative_to(REPO_ROOT))

        layer = fm.get("layer", "")
        layer_num = LAYER_NUMBERS.get(layer, -1)

        depends_on = fm.get("depends_on", [])
        if isinstance(depends_on, list):
            for dep in depends_on:
                if isinstance(dep, dict):
                    dep_target = dep.get("target", dep.get("module_id", ""))
                    dep_layer_str = dep.get("layer", "")
                elif isinstance(dep, str):
                    dep_target = dep
                    dep_layer_str = ""
                else:
                    continue

                dep_layer_num = LAYER_NUMBERS.get(dep_layer_str, -1)
                if layer_num > 0 and dep_layer_num > 0 and dep_layer_num > layer_num:
                    findings.append(
                        {
                            "file": rel,
                            "layer": layer,
                            "depends_on_target": dep_target,
                            "dep_layer": dep_layer_str,
                            "violation": f"\u4f9d\u8d56\u5c42\u7ea7\u65b9\u5411\u9519\u8bef: {layer} \u2192 {dep_layer_str}\uff08\u4e0b\u7ea7\u4e0d\u80fd\u4f9d\u8d56\u4e0a\u7ea7\uff09",
                            "severity": "MEDIUM",
                        }
                    )

        if "contracts" in rel.lower() and any(d in rel for d in CONTRACT_FORBIDDEN_DIRS):
            findings.append(
                {
                    "file": rel,
                    "violation": "contracts \u6587\u4ef6\u4e0d\u5728 _registry/contracts/ \u4e2d",
                    "severity": "HIGH",
                }
            )

    return findings, files_scanned
    """扫描层级依赖违规."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="\u8de8\u5c42\u4f9d\u8d56\u8fdd\u89c4\u68c0\u6d4b")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    findings, files_scanned = scan_layer_violations()

    direction_violations = [f for f in findings if "\u65b9\u5411\u9519\u8bef" in f.get("violation", "")]
    contract_violations = [f for f in findings if "contracts" in f.get("violation", "")]

    print(f"\n[LAYER-DEPS] \u626b\u63cf {files_scanned} \u4e2a .md \u6587\u4ef6", file=sys.stderr)
    print(f"  \u65b9\u5411\u8fdd\u89c4: {len(direction_violations)}", file=sys.stderr)
    print(f"  Contracts \u8fdd\u89c4: {len(contract_violations)}", file=sys.stderr)

    for f in direction_violations[:10]:
        print(f"\n  [{f['severity']}] {f['file']}", file=sys.stderr)
        print(f"     {f['violation']}", file=sys.stderr)

    for f in contract_violations[:10]:
        print(f"\n  [{f['severity']}] {f['file']}", file=sys.stderr)
        print(f"     {f['violation']}", file=sys.stderr)

    if findings:
        print(f"\n\u26a0 {len(findings)} \u4e2a\u5c42\u4f9d\u8d56\u8fdd\u89c4\uff01", file=sys.stderr)
        if not args.warn_only:
            sys.exit(EXIT_FINDINGS)
        sys.exit(EXIT_PASS)

    print("\n\u2705 \u65e0\u5c42\u4f9d\u8d56\u8fdd\u89c4", file=sys.stderr)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
