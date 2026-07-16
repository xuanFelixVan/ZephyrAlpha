# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/lifecycle/validate_lifecycle_refs.py | §
# [MODULE] scripts.governance.d5_architecture.validators.lifecycle.validate_lifecycle_refs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
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
"""validate_lifecycle_refs.py — 生命周期引用约束合规检查



对标：PS-STD-001 §4.1.1 LRC-001~005（生命周期引用约束）
     AGENTS.md §6.2（原子事务模式——引用链不超过3层）

检测内容：
- LRC-001：active 文件通过 depends_on 引用 draft 文件
- LRC-004：draft 文件被 3+ 个 active 文件引用（实质活跃应升格）
- LRC-005：draft 文件被多个 active 文件引用时标记 MEDIUM Finding

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args: []
description: 生命周期引用约束合规检查（LRC-001~005：active→draft depends_on 违规 + draft被3+active引用检测）
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
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.thresholds import get
from _shared.walk import iter_files

LRC_HIGH_REF_THRESHOLD = get("lifecycle_refs.high_ref_threshold", 3)


def _resolve_target(
    target: str, source_file: Path, module_id_to_file: dict[str, Path], file_to_fm: dict[str, dict]
) -> tuple[Path | None, dict | None]:
    """_resolve_target implementation."""
    if target in module_id_to_file:
        fp = module_id_to_file[target]
        return (fp, file_to_fm.get(str(fp)))
    norm_target = target.replace("\\", "/")
    if norm_target.startswith("D:/") or norm_target.startswith("d:/"):
        fp = Path(norm_target)
        if fp.exists():
            fm = parse_frontmatter_from_file(fp) if fp.suffix == ".md" else None
            return (fp, fm)
    candidate = (source_file.parent / norm_target).resolve()
    if candidate.exists():
        fm = parse_frontmatter_from_file(candidate) if candidate.suffix == ".md" else None
        return (candidate, fm)
    return (None, None)


def _build_index(docs_dir: Path) -> tuple[dict[str, Path], dict[str, dict], dict[str, str]]:
    """_build_index implementation."""
    module_id_to_file: dict[str, Path] = {}
    file_to_fm: dict[str, dict] = {}
    file_to_status: dict[str, str] = {}
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        rel = str(filepath)
        file_to_fm[rel] = fm
        file_to_status[rel] = str(fm.get("status", ""))
        mid = fm.get("module_id", "")
        if mid:
            module_id_to_file[mid] = filepath
    return (module_id_to_file, file_to_fm, file_to_status)


def scan_lifecycle_violations(docs_dir: Path) -> tuple[list[dict], int, int]:
    """扫描生命周期引用违规"""
    findings: list[dict] = []
    "扫描生命周期引用违规."
    module_id_to_file, file_to_fm, file_to_status = _build_index(docs_dir)
    files_scanned = len(file_to_fm)
    active_files = {fp for fp, st in file_to_status.items() if st == "active"}
    draft_ref_counts: dict[str, list[str]] = {}
    for fp, fm in file_to_fm.items():
        if file_to_status.get(fp) != "active":
            continue
        depends_on = fm.get("depends_on", [])
        if not isinstance(depends_on, list):
            continue
        source_file = Path(fp)
        rel = str(source_file.relative_to(REPO_ROOT))
        for dep in depends_on:
            target = ""
            if isinstance(dep, dict):
                target = dep.get("target", dep.get("module_id", ""))
            elif isinstance(dep, str):
                target = dep
            if not target:
                continue
            resolved_fp, resolved_fm = _resolve_target(target, source_file, module_id_to_file, file_to_fm)
            if resolved_fp and resolved_fm:
                dep_status = str(resolved_fm.get("status", ""))
                if dep_status == "draft":
                    dep_rel = str(resolved_fp.relative_to(REPO_ROOT))
                    dep_mid = resolved_fm.get("module_id", "")
                    findings.append(
                        {
                            "file": rel,
                            "severity": "MEDIUM",
                            "violation": f"LRC-001: active 文件引用 draft 文件 {dep_mid or dep_rel} via depends_on",
                            "depends_on_target": target,
                            "target_file": dep_rel,
                            "target_module_id": dep_mid,
                            "target_status": "draft",
                        }
                    )
                    draft_key = dep_rel
                    if draft_key not in draft_ref_counts:
                        draft_ref_counts[draft_key] = []
                    draft_ref_counts[draft_key].append(rel)
    for draft_key, refs in draft_ref_counts.items():
        if len(refs) >= LRC_HIGH_REF_THRESHOLD:
            draft_fm = file_to_fm.get(draft_key, {})
            draft_mid = draft_fm.get("module_id", "")
            draft_file = Path(draft_key)
            draft_rel = str(draft_file.relative_to(REPO_ROOT))
            findings.append(
                {
                    "file": draft_rel,
                    "severity": "MEDIUM",
                    "violation": f"LRC-004: draft 文件被 {len(refs)} 个 active 文件引用（阈值: {LRC_HIGH_REF_THRESHOLD}）——实质活跃，应评估升格",
                    "draft_module_id": draft_mid,
                    "reference_count": len(refs),
                    "referenced_by": refs[:10],
                }
            )
    return (findings, files_scanned, len(active_files))
    "扫描生命周期引用违规."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="生命周期引用约束合规检查（LRC-001~005）")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument(
        "--scope",
        default="docs",
        help="扫描范围: docs（默认，docs/ 下所有 .md）| policies（仅 docs/01_policies_and_standards/）",
    )
    args = parser.parse_args()
    if args.scope == "policies":
        docs_dir = REPO_ROOT / "docs" / "01_policies_and_standards"
    else:
        docs_dir = REPO_ROOT / "docs"
    findings, files_scanned, active_count = scan_lifecycle_violations(docs_dir)
    lrc001 = [f for f in findings if "LRC-001" in f.get("violation", "")]
    lrc004 = [f for f in findings if "LRC-004" in f.get("violation", "")]
    print(f"\n[LIFECYCLE-REFS] 扫描 {files_scanned} 个 .md 文件", file=sys.stderr)
    print(f"  其中 active: {active_count}", file=sys.stderr)
    print(f"  LRC-001（active→draft 引用）: {len(lrc001)}", file=sys.stderr)
    print(f"  LRC-004（draft 被 3+ active 引用）: {len(lrc004)}", file=sys.stderr)
    for f in lrc001[:10]:
        print(
            f"\n  [MEDIUM] {f['file']}\n     LRC-001: 引用 draft 文件 {f.get('target_module_id') or f.get('target_file')}",
            file=sys.stderr,
        )
    for f in lrc004[:10]:
        print(
            f"\n  [MEDIUM] {f['file']}\n     LRC-004: 被 {f.get('reference_count')} 个 active 文件引用", file=sys.stderr
        )
    if findings:
        hidden = len(lrc001) - 10 if len(lrc001) > 10 else 0
        hidden_draft = len(lrc004) - 10 if len(lrc004) > 10 else 0
        if hidden or hidden_draft:
            print(f"\n  ... 和 {hidden + hidden_draft} 个更多违规（limit=10/类别）", file=sys.stderr)
        print(f"\n⚠ 发现 {len(findings)} 个生命周期引用违规！", file=sys.stderr)
        if not args.warn_only:
            sys.exit(EXIT_FINDINGS)
        sys.exit(EXIT_PASS)
    print("\n✅ 无生命周期引用违规", file=sys.stderr)
    sys.exit(EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
