#!/usr/bin/env python3
"""Scan docs/01_policies_and_standards and emit _registry/catalogs/rule-catalog.yaml.

Parses Markdown/YAML frontmatter (and YAML comment headers where applicable).

CLI::

    python generate_rule_catalog.py [--scan-dir DIR] [--output FILE] [--compare FILE]
"""

# Governance script manifest (YAML fragment for tooling/consumers; not evaluated as code).
__manifest__ = """
args: []
description: >
  Scan policy tree; aggregate frontmatter into rule-catalog.yaml.
  Aligns with static-manifest SSOT for governance scripts (section 6.16-style workflow).
dimensions:
  - D3
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, SCAN_EXTENSIONS_MD_YAML
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter
from _shared.walk import iter_files

ensure_utf8_stdout()


def extract_yaml_header(content: str) -> dict | None:
    """Extract header fields from a .yaml file (comment-based header)."""
    fields: dict = {}
    for line in content.split("\n"):
        if not line.startswith("#") and line.strip() != "":
            break
        if line.startswith("#"):
            m = re.match(r"#\s*(\w+)[\uff1a:]\s*(.+)", line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
    if "schema_version" in content or "doc_type" in content:
        try:
            full_yaml = yaml.safe_load(content)
            if isinstance(full_yaml, dict):
                fields.update(
                    {
                        k: v
                        for k, v in full_yaml.items()
                        if k
                        in (
                            "module_id",
                            "doc_type",
                            "status",
                            "version",
                            "title",
                            "rule_form",
                            "scope",
                            "stability",
                            "layer",
                            "owner",
                            "ttl",
                            "superseded_by",
                        )
                    }
                )
        except yaml.YAMLError:
            pass
    return fields if fields else None


def scan_directory(scan_dir: str, repo_root: Path) -> list[dict]:
    """Scan directory for .md and .yaml files, extract frontmatter."""
    results: list[dict] = []
    scan_path = Path(scan_dir).resolve()
    repo_root = repo_root.resolve()

    if not scan_path.exists():
        print(f"ERROR: Scan directory does not exist: {scan_dir}", file=sys.stderr)
        return results

    for fpath in iter_files(
        scan_path, extensions=SCAN_EXTENSIONS_MD_YAML, exclude_dirs=EXCLUDE_DIRS | {".audit_cache"}
    ):
        fname = fpath.name
        try:
            rel_path = str(fpath.resolve().relative_to(repo_root)).replace("\\", "/")
        except ValueError:
            try:
                rel_path = str(fpath.resolve().relative_to(scan_path)).replace("\\", "/")
            except ValueError:
                rel_path = str(fpath.resolve())

        try:
            raw = fpath.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"WARNING: Cannot read {fpath}: {e}", file=sys.stderr)
            continue

        if fname.endswith(".md"):
            fm = parse_frontmatter(raw)
        else:
            fm = extract_yaml_header(raw)

        if fm is None:
            continue

        entry = {
            "path": rel_path,
            "module_id": fm.get("module_id", ""),
            "title": fm.get("title", ""),
            "doc_type": fm.get("doc_type", ""),
            "status": str(fm.get("status", "")).lower(),
            "version": str(fm.get("version", "")),
            "rule_form": fm.get("rule_form", ""),
            "scope": fm.get("scope", ""),
            "stability": fm.get("stability", ""),
            "layer": fm.get("layer", ""),
            "superseded_by": fm.get("superseded_by", ""),
        }
        results.append(entry)

    return results


SCOPE_NOTE_DOCUMENT_METADATA = (
    "本文件仅索引 docs/01_policies_and_standards/ 下带治理 frontmatter 的 Markdown（及本树登记引用）。"
    " docs/02_enterprise_architecture/、docs/09_audit/findings/、architecture-model 施工树等不在此表——见各目录 "
    "INDEX.md 与 architecture-model/SCOPE.yaml。"
)


def generate_catalog(
    entries: list[dict],
    output_path: str,
    metadata_path: str | None = None,
) -> None:
    """Write rule-catalog.yaml and optionally document-metadata-index.yaml."""
    gen_ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    catalog = {
        "schema_version": "1.0.0",
        "module_id": "PS-REG-018",
        "doc_type": "register",
        "title": "规则路径目录",
        "status": "active",
        "generated_at": gen_ts,
        "generated_by": "scripts/governance/d3_metadata/generate_rule_catalog.py",
        "total_files": len(entries),
        "files": entries,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        yaml.dump(catalog, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"Generated catalog with {len(entries)} entries -> {output_path}", file=sys.stderr)

    if metadata_path:
        meta_out = Path(metadata_path)
        meta_out.parent.mkdir(parents=True, exist_ok=True)
        document_metadata = {
            "schema_version": 1.0,
            "module_id": "PS-REG-002",
            "doc_type": "register",
            "title": "文档元数据索引",
            "status": "active",
            "generated_at": gen_ts,
            "generated_from": "generate_rule_catalog.py（与 rule-catalog.yaml 同批同步）",
            "scope_note": SCOPE_NOTE_DOCUMENT_METADATA,
            "total_files": len(entries),
            "files": entries,
        }
        with open(meta_out, "w", encoding="utf-8") as mf:
            yaml.dump(document_metadata, mf, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"Generated document metadata index -> {metadata_path}", file=sys.stderr)


def compare_with_registry(catalog_entries: list[dict], registry_path: str) -> int:
    """Compare auto-generated catalog with manual registry."""
    reg_path = Path(registry_path)
    if not reg_path.exists():
        print(f"WARNING: Registry file not found: {registry_path}", file=sys.stderr)
        return 0

    with open(reg_path, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    reg_list = registry.get("files") or registry.get("rules") or []
    if not reg_list:
        print(
            "WARNING: Registry has no 'files' or 'rules' list (skipped compare)",
            file=sys.stderr,
        )
        return 0

    reg_entries = {r.get("path", ""): r for r in reg_list}
    cat_entries = {e["path"]: e for e in catalog_entries}

    only_in_catalog = set(cat_entries.keys()) - set(reg_entries.keys())
    only_in_registry = set(reg_entries.keys()) - set(cat_entries.keys())
    common = set(cat_entries.keys()) & set(reg_entries.keys())

    differences: list[dict] = []
    for path in sorted(common):
        cat = cat_entries[path]
        reg = reg_entries[path]
        for field in ("module_id", "doc_type", "status", "version", "rule_form"):
            cat_val = str(cat.get(field, "")).lower()
            reg_val = str(reg.get(field, "")).lower()
            if cat_val != reg_val and cat_val and reg_val:
                differences.append(
                    {
                        "path": path,
                        "field": field,
                        "catalog_value": cat_val,
                        "registry_value": reg_val,
                    }
                )

    print(f"  Only in catalog:  {len(only_in_catalog)}", file=sys.stderr)
    print(f"  Only in registry: {len(only_in_registry)}", file=sys.stderr)
    print(f"  Field differences: {len(differences)}", file=sys.stderr)

    if only_in_catalog:
        print("\n  Files only in catalog:", file=sys.stderr)
        for p in sorted(only_in_catalog)[:10]:
            print(f"    + {p}", file=sys.stderr)

    if only_in_registry:
        print("\n  Files only in registry:", file=sys.stderr)
        for p in sorted(only_in_registry)[:10]:
            print(f"    - {p}", file=sys.stderr)

    if differences:
        print("\n  Field differences:", file=sys.stderr)
        for d in differences[:20]:
            print(
                f"    {d['path']} [{d['field']}]: catalog={d['catalog_value']} vs registry={d['registry_value']}",
                file=sys.stderr,
            )

    if not only_in_catalog and not only_in_registry and not differences:
        print("\n  \u2705 100% match! Auto-generated catalog is identical to manual registry.", file=sys.stderr)

    return len(only_in_catalog) + len(differences)


def main() -> None:
    """入口函数."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    parser = argparse.ArgumentParser(description="Generate rule catalog from frontmatter")
    parser.add_argument(
        "--scan-dir",
        default=str(repo_root / "docs" / "01_policies_and_standards"),
        help="Directory to scan",
    )
    parser.add_argument(
        "--output",
        default=str(repo_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule-catalog.yaml"),
        help="Output YAML file",
    )
    parser.add_argument(
        "--metadata-output",
        default=str(
            repo_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "document-metadata-index.yaml"
        ),
        help="同步写出 document-metadata-index.yaml（默认启用）",
    )
    parser.add_argument(
        "--no-metadata-output",
        action="store_true",
        help="不同步写出 document-metadata-index.yaml",
    )
    parser.add_argument(
        "--compare",
        default=str(
            repo_root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "document-metadata-index.yaml"
        ),
        help="Compare with existing registry",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="仅比对报告差异；不因差异而退出非零（CI 可加严）",
    )
    args = parser.parse_args()

    print(f"Scanning: {args.scan_dir}", file=sys.stderr)
    entries = scan_directory(args.scan_dir, repo_root)
    print(f"Found {len(entries)} files with frontmatter", file=sys.stderr)

    meta_path = None if args.no_metadata_output else args.metadata_output
    generate_catalog(entries, args.output, metadata_path=meta_path)

    if args.compare:
        diff_count = compare_with_registry(entries, args.compare)
        if diff_count and diff_count > 0 and not args.warn_only:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
