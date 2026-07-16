# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_deprecated_dependents.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_deprecated_dependents
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
# [TTL] permanent
"""validate_deprecated_dependents.py — 废弃文件活跃引用检测



对标：LFC-001（退役前所有引用该 module_id 的文件已迁移）
     PS-STD-009 §5（废弃文件依赖方迁移检查）

检测内容：
- 扫描 status=deprecated 文件的 module_id
- 检查是否有 status=active 的文件在 depends_on 中引用该 module_id
- 活跃文件引用废弃文件 = 迁移未完成

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 废弃文件活跃引用检测（LFC-001 / PS-STD-009 §5）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse


def scan_deprecated_dependents() -> list[dict]:
    """扫描已废弃模块的依赖者."""
    findings = []
    """扫描并返回发现列表."""
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"

    all_files = []
    deprecated_ids = set()

    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        module_id = fm.get("module_id", "")
        status = fm.get("status", "")
        depends_on = fm.get("depends_on", [])
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")

        all_files.append(
            {
                "filepath": filepath,
                "rel": rel,
                "module_id": module_id,
                "status": status,
                "depends_on": depends_on,
            }
        )

        if status == "deprecated" and module_id:
            deprecated_ids.add(module_id)

    if not deprecated_ids:
        return findings

    for info in all_files:
        if info["status"] != "active":
            continue

        deps = info["depends_on"]
        if not isinstance(deps, list):
            continue

        for dep in deps:
            if isinstance(dep, dict):
                target = dep.get("target", dep.get("module_id", ""))
            elif isinstance(dep, str):
                target = dep
            else:
                continue

            if target in deprecated_ids:
                findings.append(
                    {
                        "active_file": info["rel"],
                        "active_module": info["module_id"],
                        "deprecated_target": target,
                        "severity": "HIGH",
                    }
                )

    return findings
    """扫描已废弃模块的依赖者."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="废弃文件活跃引用检测（LFC-001 / PS-STD-009 §5）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    findings = scan_deprecated_dependents()

    if findings:
        print(f"\n[DEPR-DEP] {len(findings)} 个活跃文件引用废弃模块:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['active_module']} ({f['active_file']})", file=sys.stderr)
            print(f"    depends_on 废弃模块: {f['deprecated_target']}", file=sys.stderr)
    else:
        print("[DEPR-DEP] 无活跃文件引用废弃模块", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)


if __name__ == "__main__":
    main()
