"""
generate_registry_master_index.py — 登记表总索引自动生成器

扫描 _registry/catalogs/ 下所有 .yaml 文件 → 提取 frontmatter →
生成 registry-master-index.yaml 的 registries 列表。

对标 §6.16 静态清单自动生成铁律。
手工 overlay（如 manual_notes、review_status）通过独立的 overlay.yaml 注入。

Usage:
    python scripts/governance/generators/generate_registry_master_index.py
    python scripts/governance/generators/generate_registry_master_index.py --check
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.registry_entry_count import count_primary_registry_entries
from _shared.yaml_utils import load_yaml

__manifest__ = """
dimensions: [D1, D5]
priority: P1
timeout_seconds: 15
args:
  - {flag: --check, type: bool, description: "检测漂移"}
  - {flag: --output, type: str, description: "输出路径"}
warn_only: false
description: >
  扫描 _registry/catalogs/*.yaml 的 frontmatter/comment_meta，自动生成 registry-master-index.yaml。
  对标 §6.16 静态清单自动生成铁律。
"""

CATALOGS_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
DEFAULT_OUTPUT = CATALOGS_DIR / "registry-master-index.yaml"

CATEGORY_FROM_DOC_TYPE = {
    "register": "governance_rule",
    "vocabulary": "vocabulary",
    "contract": "contract",
}


def extract_registry_info(yaml_path: Path) -> dict | None:
    content = yaml_path.read_text(encoding="utf-8")

    # BOM 免疫：部分文件可能含 UTF-8 BOM — 导致注释解析器在首行就 break
    if content and content[0] == "\ufeff":
        content = content[1:]

    comment_meta = {}
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("# "):
            if not stripped.startswith("#"):
                break
            continue
        if ":" in stripped[2:]:
            key, _, val = stripped[2:].partition(":")
            comment_meta[key.strip()] = val.strip()

    data: dict | None = None
    try:
        data = load_yaml(yaml_path)
    except Exception:
        data = None

    module_id = None
    if isinstance(data, dict):
        module_id = data.get("module_id") or data.get("registry_id")
    if not module_id:
        module_id = comment_meta.get("module_id") or comment_meta.get("registry_id")
    if not module_id:
        return None
    mid = str(module_id)
    if not (
        mid.startswith("REG-")
        or mid.startswith("PS-REG-")
        or mid.startswith("PS-IDX-")
        or mid.startswith("DOM-")
        or mid.startswith("GOV-")
    ):
        return None

    fm = parse_frontmatter_from_file(yaml_path)
    if fm is None:
        fm = {}
    if isinstance(data, dict):
        fm = {**data, **fm}

    name = fm.get("title") or fm.get("name") or comment_meta.get("name") or yaml_path.stem
    doc_type = str(fm.get("doc_type") or comment_meta.get("doc_type", "") or "")
    category = CATEGORY_FROM_DOC_TYPE.get(doc_type, "governance_rule")
    maintenance = str(fm.get("maintenance") or comment_meta.get("maintenance", "manual"))
    status = str(fm.get("status") or comment_meta.get("status", "unknown"))

    entry_count = 0
    if isinstance(data, dict):
        entry_count = count_primary_registry_entries(data, yaml_path.stem)
    elif isinstance(data, list):
        entry_count = len(data)

    return {
        "registry_id": str(module_id),
        "name": name,
        "category": category,
        "physical_path": str(yaml_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "format": "yaml",
        "maintenance": maintenance,
        "entry_count": entry_count,
        "status": status,
    }


def scan_catalogs() -> list[dict]:
    registries = []
    skipped = []
    for yf in sorted(CATALOGS_DIR.glob("*.yaml")):
        if yf.name == "registry-master-index.yaml":
            continue
        info = extract_registry_info(yf)
        if info:
            registries.append(info)
        else:
            content = yf.read_text(encoding="utf-8")
            if content and content[0] == "\ufeff":
                content = content[1:]
            for line in content.split("\n")[:30]:
                if "module_id:" in line or "registry_id:" in line:
                    skipped.append(yf.name)
                    break
    if skipped:
        print(f"WARNING: {len(skipped)} 个文件含 module_id 但未被收录（检查 frontmatter/YAML 兼容性）:")
        for s in skipped:
            print(f"  - {s}")
    return registries


def generate() -> dict:
    registries = scan_catalogs()
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/governance/generators/generate_registry_master_index.py",
        "source": "_registry/catalogs/*.yaml → frontmatter",
        "total_registries": len(registries),
        "registries": registries,
    }


def main() -> None:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="从 _registry/ YAML frontmatter 自动生成总索引")
    parser.add_argument("--check", action="store_true", help="检测漂移")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="输出路径")
    args = parser.parse_args()

    result = generate()

    if args.check:
        existing = load_yaml(args.output)
        ex_regs = existing.get("registries", [])
        if len(ex_regs) != result["total_registries"]:
            print(f"DRIFT: 磁盘 {len(ex_regs)} 张登记表 ≠ 生成 {result['total_registries']} 张")
            sys.exit(1)
        print("OK: 登记表总索引与实际一致")
        return

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# 自动生成于 {result['generated_at']}\n")
        f.write("# 来源: _registry/catalogs/*.yaml frontmatter\n")
        f.write("# 手工编辑无效——修改请通过各登记表的 frontmatter\n\n")
        yaml.dump(result, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"已生成 {result['total_registries']} 张登记表索引 → {args.output}")


if __name__ == "__main__":
    main()
