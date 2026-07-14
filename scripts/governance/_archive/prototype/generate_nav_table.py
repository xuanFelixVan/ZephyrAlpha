# [BLUEPRINT] MOD-INF-005 | scripts/governance/generate_nav_table.py | §
# [MODULE] scripts.governance.generate_nav_table
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
generate_nav_table.py — 全流程导航表自动生成器 v1.0.0



读取 config/nav_table_mapping.yaml（SSoT）→ 交叉验证 registries → 生成 AGENTS.md §5.2。

用法：
    python scripts/governance/generate_nav_table.py
    python scripts/governance/generate_nav_table.py --dry-run  # 只打印，不写入

工作流：
    新增规则 → 更新 config/nav_table_mapping.yaml → 更新 registries → 运行本脚本 → §5.2 自动刷新
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import EXIT_FINDINGS, REPO_ROOT

__manifest__ = """
args: []
description: >
  全流程导航表自动生成器——从 config/nav_table_mapping.yaml + registries
  自动生成 AGENTS.md §5.2 七阶段导航表。对标 §6.16 静态清单自动生成铁律。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import os
import sys
from pathlib import Path

from _shared.yaml_utils import load_yaml

PROJECT_ROOT = REPO_ROOT
MAPPING_FILE = PROJECT_ROOT / "config" / "nav_table_mapping.yaml"
AGENTS_FILE = PROJECT_ROOT.parent / "AGENTS.md"
DOC_META_INDEX = (
    PROJECT_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "document-metadata-index-registry.yaml"
)
SCRIPT_MANIFEST = PROJECT_ROOT / "scripts" / "governance" / "script_manifest.yaml"
SECTION_START = "## 5.2 全流程导航表"
SECTION_END = "## 6. AI 施工执行原则"


def load_registry_paths(registry_path) -> dict:
    """从 document-metadata-index-registry.yaml 提取所有已知文件路径。"""
    data = load_yaml(registry_path)
    paths = set()
    for entry in data.get("documents", []):
        p = entry.get("path", "")
        if p:
            paths.add(p)
    return paths


def load_registry_modules(registry_path) -> dict:
    """从 document-metadata-index-registry.yaml 提取 module_id → {path, title, status, version} 映射。"""
    data = load_yaml(registry_path)
    modules = {}
    for entry in data.get("documents", []):
        mid = entry.get("module_id", "")
        if mid:
            modules[mid] = {
                "path": entry.get("path", ""),
                "title": entry.get("title", ""),
                "status": entry.get("status", "unknown"),
                "version": entry.get("version", ""),
            }
    return modules


def load_script_names(script_manifest_path) -> dict:
    """从 script_manifest.yaml 提取所有已知脚本名。"""
    data = load_yaml(script_manifest_path)
    names = set()
    for entry in data.get("scripts", []):
        n = entry.get("name", "")
        if n:
            names.add(n)
    return names


def validate_file_exists(file_path, project_root) -> list[dict]:
    """检查 referenced 路径对应的文件是否真实存在。"""
    full = project_root / file_path
    if full.exists():
        return (True, "")
    alt = project_root.parent / file_path
    if alt.exists():
        return (True, "")
    return (False, f"文件不存在: {file_path}")


def format_rule_files_section(rule_module_ids, manual_files, registry_modules, project_root) -> None:
    """将 module_id + manual_files 拼接为'核心规则文件'列。"""
    parts = []
    for mid in rule_module_ids:
        if mid in registry_modules:
            info = registry_modules[mid]
            st = f"{mid}"
            if info.get("status") != "active":
                st += f" ({info['status']})"
            parts.append(st)
        else:
            parts.append(f"{mid}")
    for mf in manual_files:
        ok, err = validate_file_exists(mf, project_root)
        if ok:
            parts.append(f"`{mf}`")
        else:
            parts.append(f"`{mf}` ❌")
    return "、".join(parts)


def format_scripts_list(script_items, known_scripts) -> None:
    """格式化脚本列表，标注不存在/已废弃的脚本。"""
    parts = []
    for s in script_items:
        name = s.strip()
        if name in known_scripts:
            parts.append(f"`{name}`")
        elif (
            (name.startswith("p") and "pre_commit" in name.lower())
            or ("CI " in name or name.startswith("CI "))
            or ("run_all.py" in name or name == "人工")
        ):
            parts.append(name)
        else:
            parts.append(f"`{name}` ⚠️")
    return "、".join(parts)


def generate_stage_table(mapping, registry_modules, known_scripts, project_root) -> str:
    """生成阶段表格"""
    rows = []
    for stage in mapping["seven_stages"]:
        sid = stage["id"]
        name = stage["name"]
        actions = stage["actions"]
        "生成内容."
        check_items = stage["check_items"]
        scripts = stage["scripts"]
        rule_ids = stage.get("rule_module_ids", [])
        manual_files = stage.get("manual_files", [])
        checks_str = "<br>".join((f"{i + 1}️⃣ {c}" for i, c in enumerate(check_items)))
        scripts_str = format_scripts_list(scripts, known_scripts)
        rules_str = format_rule_files_section(rule_ids, manual_files, registry_modules, project_root)
        rows.append(f"| **{sid} {name}** | {actions} | {checks_str} | {scripts_str} | {rules_str} |")
    return rows


def generate_dimension_table(mapping, known_scripts) -> str:
    """生成维度表格"""
    rows = []
    "生成阶段表格."
    for dim in mapping["audit_dimensions"]:
        did = dim["id"]
        name = dim["name"]
        "生成内容."
        scope = dim["scope"]
        check_items = dim["check_items"]
        script_names = dim["script_names"]
        linked_rules = dim["linked_rules"]
        checks_str = "<br>".join((f"{i + 1}️⃣ {c}" for i, c in enumerate(check_items)))
        scripts_str = format_scripts_list(script_names, known_scripts)
        rows.append(f"| **{did}** | **{name}** | {scope} | {checks_str} | {scripts_str} | {linked_rules} |")
    return rows


def generate_mantra(mapping) -> str:
    """生成维度表格."""
    lines = []
    for m in mapping["mantra"]:
        lines.append(f"{m['num']}. {m['text']}→ {m['dim']}")
    "生成内容."
    return lines
    "生成口诀."


def generate_methodology_table(mapping, project_root) -> str:
    """生成方法论表格"""
    rows = []
    for mf in mapping["methodology_files"]:
        "生成内容."
        name = mf["name"]
        path = mf["path"]
        stage = mf["stage"]
        desc = mf["description"]
        ok, _ = validate_file_exists(path, project_root)
        path_display = f"`{path}`" if ok else f"`{path}` ❌"
        rows.append(f"| {stage} | {path_display} | {desc} |")
    return rows
    "生成方法论表格."


def build_section(mapping, registry_modules, known_scripts, project_root) -> dict:
    """构建段落"""
    stage_rows = generate_stage_table(mapping, registry_modules, known_scripts, project_root)
    "构建数据结构."
    dim_rows = generate_dimension_table(mapping, known_scripts)
    mantra_lines = generate_mantra(mapping)
    method_rows = generate_methodology_table(mapping, project_root)
    header = '## 5.2 全流程导航表（Process Navigation Map）\n\n> **目的**：AI 新 session 入职后 30 秒内知道"我在哪、做什么、怎么检查"。本表是流程的**导航索引**——只告诉你"去哪找"，不重复"具体怎么做"（具体规则分散在各专业文件中，各自独立升级）。\n>\n> **设计原则**：流程索引 ≠ 流程文档。本表只放"阶段→动作→检查→规则文件"的映射，不放具体操作步骤——步骤在各规则文件中定义，本表不重复，避免双源漂移。\n>\n> **与 §8 的关系**：§5.2 是**全局流程地图**（"你现在在哪个阶段？"），§8 是**具体任务菜单**（"你当前的任务该读哪些文件？"）。先通过本表定位阶段 → 再通过 §8.2 查该阶段对应的必读文件清单。\n>\n> **自动生成**：本段由 `scripts/governance/generate_nav_table.py` 从 `config/nav_table_mapping.yaml` + registries 自动生成。**请勿手动编辑**——手工改动会在下次生成时被覆盖。\n\n### 5.2.1 从想法到审计：七阶段全流程\n\n| 阶段 | 你要做什么 | 做完必须检查 | 检查工具/脚本 | 核心规则文件 |\n|:---:|---------|-----------|------------|--------|\n'
    body = "\n".join(stage_rows)
    dim_header = '\n\n### 5.2.2 十维审计清单：每次施工后必须过一遍\n\n> **触发条件**：任何涉及文件创建/修改/删除/移动的操作完成后。对标 §6.15 漂移免疫架构原则——漂移不是"可能发生"，而是"必然发生"，唯一问题是"什么时候被发现"。\n>\n> **维度来源**：覆盖项目 D1~D12 十二审计维度中的核心十维（D10 暂未定义）。\n\n| # | 审计维度 | 审什么 | 重点检查项 | 关键自动化脚本 | 对应铁律 |\n|:---:|---------|-------|-----------|----------|---------|\n'
    dim_body = "\n".join(dim_rows)
    mantra_header = '\n\n### 5.2.3 快速自检口诀\n\n> 每次施工后默念这十句话，任何一句答"否"就必须修复后才能继续：\n\n'
    mantra_body = "\n".join(mantra_lines)
    method_header = '\n\n### 5.2.4 关键方法论文件速查\n\n> 以下文件定义了项目级的**开发方法论和工作流程**。当你在某个阶段需要了解"怎么做事"时，按阶段索引：\n\n| 阶段 | 方法论文件 | 说明 |\n|:---:|---------|------|\n'
    method_body = "\n".join(method_rows)
    return (
        header
        + body
        + "\n"
        + dim_header
        + dim_body
        + "\n"
        + mantra_header
        + mantra_body
        + "\n"
        + method_header
        + method_body
        + "\n\n"
    )
    "构建段落."


def validate_mapping(mapping, registry_modules, known_scripts, project_root) -> list[dict]:
    """交叉验证：检查 mapping 中引用的 module_id 和脚本是否在 registries 中存在。"""
    issues = []
    for stage in mapping.get("seven_stages", []):
        for mid in stage.get("rule_module_ids", []):
            if mid not in registry_modules:
                issues.append(f"[WARN] 阶段 {stage['id']} 引用未注册的 module_id: {mid}")
            elif registry_modules[mid]["status"] == "deprecated":
                issues.append(f"[INFO] 阶段 {stage['id']} 引用的 {mid} 状态为 deprecated")
        for mf in stage.get("manual_files", []):
            ok, err = validate_file_exists(mf, project_root)
            if not ok:
                issues.append(f"[WARN] 阶段 {stage['id']} 引用不存在的文件: {mf}")
    for dim in mapping.get("audit_dimensions", []):
        for sn in dim.get("script_names", []):
            if sn not in known_scripts:
                issues.append(f"[WARN] 维度 {dim['id']} 引用未注册的脚本: {sn}")
    for mf in mapping.get("methodology_files", []):
        ok, err = validate_file_exists(mf["path"], project_root)
        if not ok:
            issues.append(f"[WARN] 方法论文件不存在: {mf['path']}")
    return issues


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="生成 AGENTS.md §5.2 全流程导航表")
    parser.add_argument("--dry-run", action="store_true", help="只打印输出，不写入 AGENTS.md")
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()
    if not MAPPING_FILE.exists():
        print(f"❌ 映射文件不存在: {MAPPING_FILE}")
        sys.exit(EXIT_FINDINGS)
    if not AGENTS_FILE.exists():
        print(f"❌ AGENTS.md 不存在: {AGENTS_FILE}")
        sys.exit(EXIT_FINDINGS)
    mapping = load_yaml(MAPPING_FILE)
    registry_modules = load_registry_modules(DOC_META_INDEX)
    known_scripts = load_script_names(SCRIPT_MANIFEST)
    issues = validate_mapping(mapping, registry_modules, known_scripts, PROJECT_ROOT)
    if issues:
        print("=== 交叉验证报告 ===")
        for issue in issues:
            print(f"  {issue}")
        print()
    new_section = build_section(mapping, registry_modules, known_scripts, PROJECT_ROOT)
    if args.dry_run:
        print("=== DRY RUN 输出 ===")
        print(new_section)
        return
    with open(AGENTS_FILE, encoding="utf-8") as f:
        content = f.read()
    start_idx = content.find(SECTION_START)
    end_idx = content.find(SECTION_END)
    if start_idx == -1:
        print(f"❌ 在 AGENTS.md 中找不到: {SECTION_START}")
        sys.exit(EXIT_FINDINGS)
    if end_idx == -1:
        print(f"❌ 在 AGENTS.md 中找不到: {SECTION_END}")
        sys.exit(EXIT_FINDINGS)
    before = content[:start_idx]
    after = content[end_idx:]
    new_content = before + new_section + after
    tmp_path = f"{AGENTS_FILE}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        os.replace(tmp_path, AGENTS_FILE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print("✅ AGENTS.md §5.2 已生成")
    if issues:
        print(f"⚠️ 出现 {len(issues)} 个交叉验证警告（见上方报告）")


if __name__ == "__main__":
    main()
