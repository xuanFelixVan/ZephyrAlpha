# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/analyzers/measure_deprecation_cascade.py | §
# [MODULE] scripts.governance.d5_architecture.analyzers.measure_deprecation_cascade
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.analyzers.__init__
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
"""measure_deprecation_cascade.py — 废弃级联影响度量



对标：LFC-003（级联影响 >= 5 个文件时需 Owner 批准）

检测内容：
- 对每个 status=deprecated 的文件，计算级联影响文件数
- 级联影响 = 直接 depends_on 该 module_id 的文件 + 间接依赖
- >= 5 个文件时输出 WARNING

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 废弃级联影响度量（LFC-003 — 级联>=5文件需Owner批准）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import sys
from collections import defaultdict, deque
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.thresholds import get
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

CASCADE_THRESHOLD = get("lifecycle_refs.cascade_threshold", 5)


def build_reverse_dep_graph() -> tuple[dict[str, list[str]], set[str]]:
    """构建反向依赖图"""
    reverse_deps: dict[str, list[str]] = defaultdict(list)
    deprecated_ids = set()
    "构建反向依赖图."
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD_YAML):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        module_id = fm.get("module_id", "")
        status = fm.get("status", "")
        depends_on = fm.get("depends_on", [])
        if status == "deprecated" and module_id:
            deprecated_ids.add(module_id)
        if isinstance(depends_on, list):
            for dep in depends_on:
                if isinstance(dep, dict):
                    target = dep.get("target", dep.get("module_id", ""))
                elif isinstance(dep, str):
                    target = dep
                else:
                    continue
                if target and module_id:
                    reverse_deps[target].append(module_id)
    return (dict(reverse_deps), deprecated_ids)
    "build reverse dep graph."


def measure_cascade(reverse_deps: dict[str, list[str]], deprecated_ids: set[str]) -> list[dict]:
    """度量级联影响"""
    findings = []
    "度量级联影响."
    for dep_id in deprecated_ids:
        affected = set()
        queue = deque([dep_id])
        while queue:
            current = queue.popleft()
            for dependent in reverse_deps.get(current, []):
                if dependent not in affected:
                    affected.add(dependent)
                    queue.append(dependent)
        count = len(affected)
        if count >= CASCADE_THRESHOLD:
            findings.append(
                {"deprecated_id": dep_id, "cascade_count": count, "affected": sorted(affected), "severity": "MEDIUM"}
            )
    return findings
    "measure cascade."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="废弃级联影响度量（LFC-003）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    reverse_deps, deprecated_ids = build_reverse_dep_graph()
    findings = measure_cascade(reverse_deps, deprecated_ids)
    if findings:
        print(f"\n[CASCADE] {len(findings)} 个废弃模块级联影响 >= {CASCADE_THRESHOLD} 个文件:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['deprecated_id']} — 影响 {f['cascade_count']} 个文件", file=sys.stderr)
            for aff in f["affected"][:10]:
                print(f"    ← {aff}", file=sys.stderr)
            if len(f["affected"]) > 10:
                print(f"    ... 还有 {len(f['affected']) - 10} 个", file=sys.stderr)
    else:
        print(f"[CASCADE] 无级联影响 >= {CASCADE_THRESHOLD} 的废弃模块", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
