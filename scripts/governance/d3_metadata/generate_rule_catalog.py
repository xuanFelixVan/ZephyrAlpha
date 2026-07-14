# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_rule_catalog.py | §
# [MODULE] scripts.governance.d3_metadata.generate_rule_catalog
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
# [CONSUMERS]
# [STARTUP] event_driven
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

    python generate_rule_catalog.py [--scan-dir DIR] [--output FILE]
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
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
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
        # title 含「唯一真源(SSoT)」声明：让新AI第一眼识别这是规则索引真源
        # （向内收4原则之"新AI可发现性"——无歧义标记真源性质）
        "title": "规则路径目录（唯一真源 SSoT）",
        "status": "active",
        "generated_at": gen_ts,
        "generated_by": "scripts/governance/d3_metadata/generate_rule_catalog.py",
        # maintenance 字段治本（2026-06-29）：声明 auto 让 generate_registry_master_index.py
        # 正确标记本表为自动维护——原缺省填 manual 是标记滞后根因（registry_master_index L167 误标 manual）
        "maintenance": "auto",
        "total_files": len(entries),
        "total_rules": total_rules,
        "tier_distribution": tier_distribution,
        "files": entries,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    atomic_write_safe(
        output,
        yaml.dump(catalog, allow_unicode=True, default_flow_style=False, sort_keys=False),
    )
    print(f"Generated catalog with {len(entries)} entries -> {output_path}", file=sys.stderr)


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
    args = parser.parse_args()

    print(f"Scanning: {args.scan_dir}", file=sys.stderr)
    entries = scan_directory(args.scan_dir, REPO_ROOT)
    print(f"Found {len(entries)} files with frontmatter", file=sys.stderr)

    generate_catalog(entries, args.output)

    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
