# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_rule_catalog.py | §
# [MODULE] scripts.governance.d3_metadata.generate_rule_catalog
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出文件名必须为 rule_catalog_registry.yaml（snake_case 硬约束）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan_dir 不存在 → stderr 警告并返回空列表
# [TESTS]
# [TTL] task_bound
#!/usr/bin/env python3
"""Scan docs/01_policies_and_standards and emit _registry/catalogs/rule_catalog_registry.yaml.

Parses Markdown/YAML frontmatter (and YAML comment headers where applicable).

CLI::

    python generate_rule_catalog.py [--scan-dir DIR] [--output FILE] [--compare FILE]
"""

# Governance script manifest (YAML fragment for tooling/consumers; not evaluated as code).
__manifest__ = """
args: []
description: >
  Scan policy tree; aggregate frontmatter into rule_catalog_registry.yaml.
  Aligns with static-manifest SSOT for governance scripts (section 6.16-style workflow).
dimensions:
  - D3
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

# ── _shared 模块 import bootstrap（一次性极简 bootstrap 找 _shared；REPO_ROOT 真源
#    为 zephyr.shared.io.paths，经 _shared.constants re-export，符合 project_memory 铁律）──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import (  # noqa: E402
    EXCLUDE_DIRS,
    EXIT_FINDINGS,
    EXIT_PASS,
    GOV_DOCS_DIR,
    REPO_ROOT,
    SCAN_EXTENSIONS_MD_YAML,
)
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.frontmatter import parse_frontmatter  # noqa: E402
from _shared.walk import iter_files  # noqa: E402

ensure_utf8_stdout()


def extract_yaml_header(content: str) -> dict | None:
    """Extract header fields from a .yaml file.

    #ARCH-024 治本修复：原逻辑依赖 schema_version/doc_type 关键字判断是否
    调用 yaml.safe_load，导致 48 个无此字段的 trae_*.yaml 规则文件被跳过
    （只扫到 12/60）。修复：始终尝试 yaml.safe_load，注释头解析作为回退。
    """
    fields: dict = {}
    # 1. 始终尝试 yaml.safe_load（#ARCH-024 修复：不依赖关键字判断）
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
                        # 以下字段用于派生 _index.yaml 独有的规则元数据
                        # （#ARCH-024 治本：catalog 扩展为唯一规则索引）
                        "severity",
                        "tags",
                        "aliases",
                        "sections",
                    )
                }
            )
    except yaml.YAMLError:
        pass
    # 2. 回退：注释头解析（覆盖纯注释头文件，如脚本头部 BLUEPRINT 注释）
    if not fields:
        for line in content.split("\n"):
            if not line.startswith("#") and line.strip() != "":
                break
            if line.startswith("#"):
                m = re.match(r"#\s*(\w+)[\uff1a:]\s*(.+)", line)
                if m:
                    fields[m.group(1)] = m.group(2).strip()
    return fields if fields else None


def _extract_tier_from_tags(tags) -> str:
    """从 tags 列表中提取 tier（L0/L1/L2），无则返回空串。

    tier 真源为规则文件 frontmatter 的 tags 字段中的 Lx 元素（#ARCH-024 治本）。
    """
    if not isinstance(tags, list):
        return ""
    for tag in tags:
        if isinstance(tag, str) and re.match(r"^L[0-2]$", tag):
            return tag
    return ""


def _count_sections(sections) -> int:
    """计算 sections 字典的 section 数量。"""
    if isinstance(sections, dict):
        return len(sections)
    return 0


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
            fm = parse_frontmatter(raw)[0]
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
            # 以下4字段原由 rules/_index.yaml 手工维护（#ARCH-024 治本：改为自动派生）
            "severity": fm.get("severity", ""),
            "tier": _extract_tier_from_tags(fm.get("tags", [])),
            "aliases": fm.get("aliases", []),
            "section_count": _count_sections(fm.get("sections", {})),
        }
        results.append(entry)

    return results


def generate_catalog(entries: list[dict], output_path: str) -> None:
    """Write rule_catalog_registry.yaml（原子写入：tmp + os.replace）."""
    gen_ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 派生 tier_distribution 和 total_rules（仅统计有 tier 的规则文件）
    # #ARCH-024 治本：原由 rules/_index.yaml 手工维护，现从 entries 自动派生
    tier_distribution: dict[str, int] = {}
    total_rules = 0
    for e in entries:
        tier = e.get("tier", "")
        if tier:
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            total_rules += 1

    catalog = {
        "schema_version": "1.0.0",
        "module_id": "PS-REG-018",
        "doc_type": "register",
        "title": "规则路径目录",
        "status": "active",
        "generated_at": gen_ts,
        "generated_by": "scripts/governance/d3_metadata/generate_rule_catalog.py",
        "total_files": len(entries),
        "total_rules": total_rules,
        "tier_distribution": tier_distribution,
        "files": entries,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = f"{output}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(catalog, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, output)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"Generated catalog with {len(entries)} entries -> {output_path}", file=sys.stderr)


def compare_with_registry(catalog_entries: list[dict], registry_path: str) -> int:
    """Compare auto-generated catalog with existing registry (drift detection)."""
    reg_path = Path(registry_path)
    if not reg_path.exists():
        print(f"WARNING: Registry file not found: {registry_path}", file=sys.stderr)
        return EXIT_PASS

    with open(reg_path, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    reg_list = registry.get("files") or registry.get("rules") or []
    if not reg_list:
        print(
            "WARNING: Registry has no 'files' or 'rules' list (skipped compare)",
            file=sys.stderr,
        )
        return EXIT_PASS

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
        print("\n  \u2705 100% match! Auto-generated catalog is identical to registry.", file=sys.stderr)

    return len(only_in_catalog) + len(differences)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="Generate rule catalog from frontmatter")
    parser.add_argument(
        "--scan-dir",
        default=str(GOV_DOCS_DIR),
        help="Directory to scan",
    )
    parser.add_argument(
        "--output",
        default=str(GOV_DOCS_DIR / "_registry" / "catalogs" / "rule_catalog_registry.yaml"),
        help="Output YAML file",
    )
    parser.add_argument(
        "--compare",
        default=None,
        help="Compare with existing registry (drift detection; default: disabled)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="仅比对报告差异；不因差异而退出非零（CI 可加严）",
    )
    args = parser.parse_args()

    print(f"Scanning: {args.scan_dir}", file=sys.stderr)
    entries = scan_directory(args.scan_dir, REPO_ROOT)
    print(f"Found {len(entries)} files with frontmatter", file=sys.stderr)

    generate_catalog(entries, args.output)

    if args.compare:
        diff_count = compare_with_registry(entries, args.compare)
        if diff_count and diff_count > 0 and not args.warn_only:
            sys.exit(EXIT_FINDINGS)

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
