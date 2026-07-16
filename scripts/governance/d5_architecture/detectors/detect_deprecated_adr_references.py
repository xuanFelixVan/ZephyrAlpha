# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py | §
# [MODULE] scripts.governance.d5_architecture.detectors.detect_deprecated_adr_references
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.detectors.__init__
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
"""detect_deprecated_adr_references.py — 废弃 ADR 引用检测



对标：COND-38（引用 Deprecated ADR 作为当前决策依据为条件禁止）

检测内容：
- 扫描 Markdown 中 ADR 引用
- 检查被引 ADR 的 status 是否为 deprecated
- deprecated ADR 不应作为当前决策依据

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 废弃 ADR 引用检测（COND-38 — 禁止引用deprecated ADR）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import DB_PATH, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

ADR_REF_PATTERN = re.compile("(?:ADR|adr)[-_]?\\d{1,4}", re.IGNORECASE)


def build_adr_status_map() -> dict[str, str]:
    """构建 KB 决策记录状态映射——优先从 KB SQLite 读取，回退到物理目录"""
    status_map = {}
    db_path = REPO_ROOT / "data" / "databases" / "governance.db"
    if db_path.exists():
        try:
            import sqlite3

            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.execute("SELECT ke_id, status FROM knowledge WHERE category = 'architecture_decision'")
                for row in cur:
                    status_map[row[0]] = row[1]
            finally:
                conn.close()
        except Exception:
            pass
    adr_dirs = [
        REPO_ROOT / "" / "docs" / "01_policies_and_standards" / "governance" / "architecture" / "adr",
        REPO_ROOT / "docs" / "01_policies_and_standards" / "governance" / "architecture" / "adr",
    ]
    for adr_dir in adr_dirs:
        if not adr_dir.exists():
            continue
        for filepath in iter_files(adr_dir, extensions=SCAN_EXTENSIONS_MD):
            fm = parse_frontmatter_from_file(filepath)
            if fm:
                mid = fm.get("module_id", "")
                status = fm.get("status", "")
                if mid:
                    status_map[mid] = status
                name_match = re.search("\\d{1,4}", filepath.name)
                if name_match:
                    adr_num = f"ADR-{name_match.group().zfill(4)}"
                    status_map[adr_num] = status
                    status_map[f"adr-{name_match.group().zfill(4)}"] = status
    return status_map
    "build adr status map."


def scan_deprecated_adr_refs() -> list[dict]:
    """扫描废弃 ADR 引用"""
    findings = []
    adr_status = build_adr_status_map()
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        fm = parse_frontmatter_from_file(filepath)
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        for match in ADR_REF_PATTERN.finditer(content):
            ref = match.group(0)
            ref_upper = ref.upper().replace("_", "-")
            status = adr_status.get(ref_upper) or adr_status.get(ref) or adr_status.get(ref.lower().replace("_", "-"))
            if status == "deprecated":
                line = content[: match.start()].count("\n") + 1
                findings.append({"file": rel, "line": line, "ref": ref, "severity": "MEDIUM"})
    return findings
    "scan deprecated adr refs."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="废弃 ADR 引用检测（COND-38）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = scan_deprecated_adr_refs()
    if findings:
        print(f"\n[DEPR-ADR] {len(findings)} 个废弃 ADR 引用:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
            print(f"    引用 {f['ref']}（status=deprecated）", file=sys.stderr)
    else:
        print("[DEPR-ADR] 无废弃 ADR 引用", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
