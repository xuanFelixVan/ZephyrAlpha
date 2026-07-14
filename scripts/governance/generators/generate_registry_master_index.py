# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_registry_master_index.py | §
# [MODULE] scripts.governance.generators.generate_registry_master_index
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.generators.__init__
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
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.constants import EXIT_FINDINGS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
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
DEFAULT_OUTPUT = CATALOGS_DIR / "registry_master_index.yaml"

# 真源单一化：registry_category 是 doc_type 的属性，由 doc_type_vocabulary.yaml 唯一维护。
# 本模块直接消费词表（非同步复制），词表改即生效。禁止在此硬编码值名或分类。
_DOC_TYPE_VOCAB_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "doc_type_vocabulary.yaml"
)


def _load_registry_categories() -> dict[str, str]:
    """从 doc_type_vocabulary.yaml 加载 value→registry_category 映射。"""
    data = load_yaml(_DOC_TYPE_VOCAB_PATH)
    return {
        v["value"]: v["registry_category"]
        for v in data.get("values", [])
        if "registry_category" in v
    }


CATEGORY_FROM_DOC_TYPE: dict[str, str] = _load_registry_categories()


def _parse_code_header(first_line: str) -> dict:
    """解析 trae_047 代码头格式: # [A_<type>] module_id=X | key=val | ...

    该格式是项目代码文件的 canonical 头部(trae_047 §十五字段),
    与 YAML frontmatter 并存。本函数提取 pipe-separated key=value 对。

    返回 dict;若首行不是代码头格式则返回空 dict。
    """
    if not first_line.startswith("# [A_"):
        return {}
    header_body = first_line.lstrip("# ").strip()
    # 去掉 [A_<type>] 前缀
    if "]" in header_body:
        header_body = header_body.split("]", 1)[1].strip()
    result = {}
    for pair in header_body.split("|"):
        pair = pair.strip()
        if "=" in pair:
            k, _, v = pair.partition("=")
            result[k.strip()] = v.strip()
    return result


def extract_registry_info(yaml_path: Path) -> dict | None:
    """extract_registry_info implementation."""
    content = yaml_path.read_text(encoding="utf-8")

    # BOM 免疫：部分文件可能含 UTF-8 BOM — 导致注释解析器在首行就 break
    if content and content[0] == "\ufeff":
        content = content[1:]

    # trae_047 代码头解析(优先级最高): # [A_config] module_id=CFG-xxx | layer=...
    # 治理锚定块(# module_id: MOD-GOVERNANCE)是父蓝图引用,不是文件自身 module_id,
    # 必须被代码头覆盖——否则会提取到错误的 MOD-GOVERNANCE 而非 CFG-xxx。
    first_line = content.split("\n", 1)[0].strip() if content else ""
    code_header_meta = _parse_code_header(first_line)

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

    # 代码头优先级高于治理锚定块(后者是父蓝图引用,非文件自身 module_id)
    comment_meta = {**comment_meta, **code_header_meta}

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
        or mid.startswith("CFG-")
    ):
        return None

    fm = parse_frontmatter_from_file(yaml_path)
    if isinstance(fm, tuple):
        fm = fm[0] if fm else {}
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
    """scan_catalogs implementation."""
    registries = []
    skipped = []
    for yf in sorted(CATALOGS_DIR.glob("*.yaml")):
        # N-16 snake_case: 实际文件名是 registry_master_index.yaml(下划线),
        # 此前误用连字符导致自跳过失效——生成器会处理自己的输出文件并误报警告。
        if yf.name == "registry_master_index.yaml":
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
    """generate implementation."""
    registries = scan_catalogs()
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/governance/generators/generate_registry_master_index.py",
        "source": "_registry/catalogs/*.yaml → frontmatter",
        "total_registries": len(registries),
        "registries": registries,
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
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
            sys.exit(EXIT_FINDINGS)
        print("OK: 登记表总索引与实际一致")
        return

    content = (
        f"# 自动生成于 {result['generated_at']}\n"
        "# 来源: _registry/catalogs/*.yaml frontmatter\n"
        "# 手工编辑无效——修改请通过各登记表的 frontmatter\n\n"
        + yaml.dump(result, allow_unicode=True, default_flow_style=False, sort_keys=False)
    )
    atomic_write_safe(args.output, content)
    print(f"已生成 {result['total_registries']} 张登记表索引 → {args.output}")


if __name__ == "__main__":
    main()
