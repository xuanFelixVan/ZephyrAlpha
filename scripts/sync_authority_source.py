#!/usr/bin/env python3
"""
Authority Source Sync Script
Usage: python scripts/sync_authority_source.py [--dry-run] [--validate-only]
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

DOCS_ROOT = Path("docs")

AUTHORITY_SOURCES = {
    "layer_11": {
        "authority_doc": DOCS_ROOT / "11_STRATEGIC_DECISION" / "complete-blueprint-overview.md",
        "derived_docs": [
            DOCS_ROOT / "11_STRATEGIC_DECISION" / "blueprint-index.md",
            DOCS_ROOT / "11_STRATEGIC_DECISION" / "responsibility-boundary-matrix.md",
        ]
    }
}


def parse_frontmatter(file_path: Path) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from markdown file"""
    if not file_path.exists():
        return {}, ""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
        except:
            fm = {}
        body = content[match.end():]
    else:
        fm, body = {}, content

    return fm, body


def write_frontmatter(file_path: Path, fm: Dict, body: str):
    """Write YAML frontmatter to markdown file"""
    yaml_str = yaml.dump(fm, allow_unicode=True, sort_keys=False)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"---\n{yaml_str}---\n\n{body}")


def get_authority_data(authority_doc: Path) -> Dict:
    """Extract key data from authority source"""
    fm, _ = parse_frontmatter(authority_doc)
    return {
        "version": fm.get("version", "unknown"),
        "blueprint_count": fm.get("blueprint_count", 0),
        "missing_count": fm.get("missing_count", 0),
        "last_updated": fm.get("last_updated", "unknown"),
    }


def sync_derived_doc(authority_doc: Path, derived_doc: Path, dry_run: bool) -> bool:
    """Sync derived document with authority source"""
    authority_data = get_authority_data(authority_doc)
    fm, body = parse_frontmatter(derived_doc)

    updates = {
        "version": authority_data["version"],
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "authority_source_synced": True,
        "authority_source": str(authority_doc),
        "synced_at": datetime.now().isoformat(),
    }
    fm.update(updates)

    if dry_run:
        print(f"  [DRY-RUN] Will update: {derived_doc.name} -> version={authority_data['version']}")
        return True

    try:
        write_frontmatter(derived_doc, fm, body)
        print(f"  [OK] Synced: {derived_doc.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed: {derived_doc.name} - {e}")
        return False


def validate_sync(authority_doc: Path, derived_doc: Path) -> List[str]:
    """Validate if derived doc is in sync with authority"""
    issues = []
    auth_data = get_authority_data(authority_doc)
    fm, _ = parse_frontmatter(derived_doc)

    if fm.get("version") != auth_data["version"]:
        issues.append(f"Version mismatch: {fm.get('version')} vs {auth_data['version']}")

    if not fm.get("authority_source_synced"):
        issues.append("Missing authority_source_synced flag")

    return issues


def sync_layer(layer_name: str, validate_only: bool, dry_run: bool) -> bool:
    """Sync a specific layer"""
    if layer_name not in AUTHORITY_SOURCES:
        print(f"[ERROR] Unknown layer: {layer_name}")
        return False

    config = AUTHORITY_SOURCES[layer_name]
    authority_doc = config["authority_doc"]
    derived_docs = config["derived_docs"]

    print(f"\n{'='*60}")
    print(f"[LAYER] Processing: {layer_name}")
    print(f"[AUTH]  Authority: {authority_doc.name}")
    print(f"{'='*60}")

    if not authority_doc.exists():
        print(f"[ERROR] Authority doc not found: {authority_doc}")
        return False

    # Check if already marked as authority source
    fm, _ = parse_frontmatter(authority_doc)
    if not fm.get("authority_source"):
        print("[MARK] Marking as authority source...")
        if not dry_run:
            fm["authority_source"] = True
            fm["authority_scope"] = "Layer 11 Blueprint List"
            fm["derived_documents"] = [d.name for d in derived_docs]
            fm["sync_rule"] = "Must sync all derived docs when updated"
            _, body = parse_frontmatter(authority_doc)
            write_frontmatter(authority_doc, fm, body)
            print(f"[OK] Marked {authority_doc.name} as authority source")
        else:
            print(f"[DRY-RUN] Would mark {authority_doc.name} as authority source")
    else:
        print(f"[OK] Already marked as authority source")

    # Get authority data
    auth_data = get_authority_data(authority_doc)
    print(f"\n[DATA] Version: {auth_data['version']}")
    print(f"[DATA] Blueprints: {auth_data['blueprint_count']}")
    print(f"[DATA] Missing: {auth_data['missing_count']}")

    # Sync derived docs
    all_ok = True
    for derived_doc in derived_docs:
        print(f"\n[CHECK] {derived_doc.name}")

        if not derived_doc.exists():
            print(f"  [WARN] Not found, skipping")
            continue

        issues = validate_sync(authority_doc, derived_doc)
        if issues:
            print(f"  [WARN] Issues found:")
            for issue in issues:
                print(f"    - {issue}")

            if not validate_only:
                if not sync_derived_doc(authority_doc, derived_doc, dry_run):
                    all_ok = False
        else:
            print(f"  [OK] In sync")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Authority Source Sync Tool")
    parser.add_argument("--validate-only", action="store_true", help="Validate only, no sync")
    parser.add_argument("--dry-run", action="store_true", help="Dry run, no actual changes")
    args = parser.parse_args()

    print("="*60)
    print("[SYNC] Authority Source Sync Tool")
    print("="*60)

    if args.validate_only:
        print("\n[MODE] Validate only")
    elif args.dry_run:
        print("\n[MODE] Dry run")
    else:
        print("\n[MODE] Execute")

    success = sync_layer("layer_11", args.validate_only, args.dry_run)

    print("\n" + "="*60)
    if success:
        print("[OK] Sync completed")
    else:
        print("[WARN] Sync issues found")
    print("="*60)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
