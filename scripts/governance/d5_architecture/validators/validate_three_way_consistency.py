# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_three_way_consistency.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_three_way_consistency
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
# [TTL] task_bound
"""validate_three_way_consistency.py — 三方一致性检查



对标：AGENTS.md §6.2（原子事务模式）
     PS-STD-001 §4（status 受控词表）

检测内容：
- 文件 frontmatter（status, version）vs 正文 blockquote（status, version）
- 文件 frontmatter（status, version）vs rule_catalog_registry.yaml 注册条目
- 三方（frontmatter / blockquote / registry）的 status 和 version 是否一致

扫描范围：docs/01_policies_and_standards/ 下有 module_id 的 .md 文件

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args: []
description: 三方一致性检查（frontmatter vs 正文blockquote vs rule_catalog_registry.yaml 的
  status/version 对账）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.frontmatter import parse_frontmatter_from_file as parse_frontmatter_raw_from_file
from _shared.walk import iter_files

BLOCKQUOTE_PATTERN = re.compile("module_id:\\s*(\\S+).*?version:\\s*(\\S+).*?status:\\s*(\\S+)")


def _extract_blockquote_info(content: str) -> dict[str, str] | None:
    """_extract_blockquote_info implementation."""
    for line in content.split("\n"):
        line_stripped = line.strip()
        if not line_stripped.startswith(">"):
            continue
        clean = re.sub("\\*\\*|`", "", line_stripped)
        m = BLOCKQUOTE_PATTERN.search(clean)
        if m:
            return {"module_id": m.group(1), "version": m.group(2), "status": m.group(3)}
    return None


def _load_registry_index(registry_path: Path) -> dict[str, dict]:
    """_load_registry_index implementation."""
    index: dict[str, dict] = {}
    if not registry_path.exists():
        return index
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(data, dict):
        return index
    files = data.get("files", [])
    for entry in files:
        if not isinstance(entry, dict):
            continue
        mid = entry.get("module_id", "")
        if mid:
            index[mid] = entry
    return index


def _resolve_registry_status(raw_status: str) -> str:
    """_resolve_registry_status implementation."""
    return raw_status.strip()


def scan_three_way_consistency(docs_dir: Path, registry_path: Path) -> tuple[list[dict], int, int]:
    """扫描三方一致性"""
    findings: list[dict] = []
    "扫描三方一致性."
    registry_index = _load_registry_index(registry_path)
    files_scanned = 0
    files_with_mid = 0
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        files_scanned += 1
        fm, content = parse_frontmatter_raw_from_file(filepath)
        if not fm:
            continue
        mid = fm.get("module_id", "")
        if not mid:
            continue
        files_with_mid += 1
        rel = str(filepath.relative_to(REPO_ROOT))
        fm_status = str(fm.get("status", ""))
        fm_version = str(fm.get("version", ""))
        bq = _extract_blockquote_info(content) if content else None
        bq_status = bq.get("status", "") if bq else ""
        bq_version = bq.get("version", "") if bq else ""
        reg_entry = registry_index.get(mid)
        reg_status = _resolve_registry_status(str(reg_entry.get("status", ""))) if reg_entry else ""
        reg_version = str(reg_entry.get("version", "")) if reg_entry else ""
        if bq and fm_status and bq_status and (fm_status != bq_status):
            findings.append(
                {
                    "file": rel,
                    "module_id": mid,
                    "severity": "MEDIUM",
                    "violation": f"frontmatter.status={fm_status} ≠ blockquote.status={bq_status}",
                    "check_type": "fm_vs_blockquote",
                    "field": "status",
                }
            )
        if bq and fm_version and bq_version and (fm_version != bq_version):
            findings.append(
                {
                    "file": rel,
                    "module_id": mid,
                    "severity": "MEDIUM",
                    "violation": f"frontmatter.version={fm_version} ≠ blockquote.version={bq_version}",
                    "check_type": "fm_vs_blockquote",
                    "field": "version",
                }
            )
        if reg_entry and fm_status and reg_status and (fm_status != reg_status):
            findings.append(
                {
                    "file": rel,
                    "module_id": mid,
                    "severity": "MEDIUM",
                    "violation": f"frontmatter.status={fm_status} ≠ registry.status={reg_status}",
                    "check_type": "fm_vs_registry",
                    "field": "status",
                }
            )
        if reg_entry and fm_version and reg_version and (fm_version != reg_version):
            findings.append(
                {
                    "file": rel,
                    "module_id": mid,
                    "severity": "HIGH",
                    "violation": f"frontmatter.version={fm_version} ≠ registry.version={reg_version}",
                    "check_type": "fm_vs_registry",
                    "field": "version",
                }
            )
        if bq and reg_entry and bq_version and reg_version and (bq_version != reg_version):
            findings.append(
                {
                    "file": rel,
                    "module_id": mid,
                    "severity": "MEDIUM",
                    "violation": f"blockquote.version={bq_version} ≠ registry.version={reg_version}",
                    "check_type": "blockquote_vs_registry",
                    "field": "version",
                }
            )
    return (findings, files_scanned, files_with_mid)
    "扫描三方一致性."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="三方一致性检查（frontmatter vs blockquote vs registry）")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()
    registry_path = GOV_DOCS_DIR / "_registry" / "catalogs" / "rule_catalog_registry.yaml"
    findings, files_scanned, files_with_mid = scan_three_way_consistency(GOV_DOCS_DIR, registry_path)
    fm_bq = [f for f in findings if f.get("check_type") == "fm_vs_blockquote"]
    fm_reg = [f for f in findings if f.get("check_type") == "fm_vs_registry"]
    bq_reg = [f for f in findings if f.get("check_type") == "blockquote_vs_registry"]
    total = len(findings)
    print(f"\n[THREE-WAY] 扫描 {files_scanned} 个 .md 文件（其中 {files_with_mid} 个有 module_id）", file=sys.stderr)
    print(f"  frontmatter ≠ blockquote: {len(fm_bq)}", file=sys.stderr)
    print(f"  frontmatter ≠ registry: {len(fm_reg)}", file=sys.stderr)
    print(f"  blockquote ≠ registry: {len(bq_reg)}", file=sys.stderr)
    for f in fm_bq[:10]:
        print(f"\n  [{f['severity']}] {f['file']}", file=sys.stderr)
        print(f"     {f['violation']}", file=sys.stderr)
    for f in fm_reg[:10]:
        print(f"\n  [{f['severity']}] {f['file']}", file=sys.stderr)
        print(f"     {f['violation']}", file=sys.stderr)
    for f in bq_reg[:10]:
        print(f"\n  [{f['severity']}] {f['file']}", file=sys.stderr)
        print(f"     {f['violation']}", file=sys.stderr)
    hidden = total - min(10, len(fm_bq)) - min(10, len(fm_reg)) - min(10, len(bq_reg))
    if hidden > 0:
        print(f"\n  ... 和 {hidden} 个更多不一致（limit=10/类别）", file=sys.stderr)
    if total > 0:
        print(f"\n⚠ {total} 个三方不一致！", file=sys.stderr)
        if not args.warn_only:
            sys.exit(EXIT_FINDINGS)
        sys.exit(EXIT_PASS)
    print("\n✅ 三方一致！", file=sys.stderr)
    sys.exit(EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
