# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/batch_create_index_md.py | §
# [MODULE] scripts.governance.d1_structure.batch_create_index_md
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
#!/usr/bin/env python3
"""Batch create index.md for all directories under docs/ that lack one."""

from __future__ import annotations

__manifest__ = """
args: []
description: 批量创建 index.md（扫描缺失 index.md 的目录并生成）
dimensions:
- D1
- D3
priority: P2
timeout_seconds: 30
warn_only: true
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

# --- Directory responsibility map (from GOV-DOC-002 + project knowledge) ---
# Key = relative path under docs/ (using forward slashes)
# Value = (responsibility_cn, exclusion_rules: list of (wrong_thing -> correct_path) tuples)

RESPONSIBILITY_MAP = {
    # === Level 1: docs/ root dirs ===
    "": (
        "项目文档体系根目录（Drawer System 入口）",
        [
            ("治理规范/标准/协议（非 migration-declaration 的其他 .md）", "01_policies_and_standards/"),
            ("架构视图/ADR", "02_enterprise_architecture/"),
            ("模块蓝图/施工图/交付", "03_modules/"),
            ("AI 服务接口合同", "03_modules/_cross_layer/_b_track_interfaces/"),
            ("审计报告/状态", "_working/audit/"),
        ],
    ),
    "02_enterprise_architecture": (
        "企业架构文档 — TOGAF 视图 + ADR + 架构模型 YAML + 架构快照",
        [
            ("治理规范/标准/协议", "01_policies_and_standards/"),
            ("模块蓝图/施工图", "03_modules/"),
            ("代码文件", "src/zephyr/"),
        ],
    ),
    "03_modules": (
        "C 轨镜像：14 层模块生命周期文档（蓝图 → 施工图 → 交付记录）。每个模块一个子目录，所有阶段产物在同一目录下",
        [
            ("5 大 AI 服务的接口文档", "03_modules/_cross_layer/_b_track_interfaces/"),
            ("项目级元计划/DevOps 流程", "01_policies_and_standards/operational/devops/"),
            ("治理规范/标准", "01_policies_and_standards/governance/"),
            ("企业架构视图/ADR", "02_enterprise_architecture/"),
        ],
    ),
    "08_knowledge": (
        "知识库 — 项目经验教训（KE）、最佳实践、可复用知识资产",
        [
            ("治理规则/标准", "01_policies_and_standards/"),
            ("模块蓝图", "03_modules/"),
        ],
    ),
    "_working/audit": (
        "审计报告与审计状态数据（Ex-post — 执行得怎样）—— 已合并入 docs/_working/ 临时区",
        [
            ("治理规范/合规标准", "01_policies_and_standards/"),
            ("架构文档", "02_enterprise_architecture/"),
        ],
    ),
    # === Level 2 ===
    "01_policies_and_standards/_registry": (
        "注册表体系 — catalogs（自动注册表）、contracts（验证契约）、schemas（JSON Schema）、vocabularies（受控词表）",
        [
            (".md 治理文档", "01_policies_and_standards/governance/ 或 operational/"),
            ("手动编辑的注册表文件", "01_policies_and_standards/governance/ 对应子域（非 catalogs）"),
        ],
    ),
    "01_policies_and_standards/domains": (
        "层域特定规则（D_DATA/D_FACTOR/D_RISK/D_REPORTING）— 每个层域下有 governance/ + operational/",
        [
            ("全局规则（影响所有层）", "01_policies_and_standards/governance/ 或 operational/"),
        ],
    ),
    "01_policies_and_standards/operational": (
        "过程式操作手册 — vibe_coding/（VC 操作）、devops/（CI/部署）、migration/（迁移）",
        [
            ("声明式治理规则", "01_policies_and_standards/governance/"),
            ("层域特定规则", "01_policies_and_standards/domains/"),
        ],
    ),
    "01_policies_and_standards/scripts": (
        "自动化脚本 — governance/（治理脚本）",
        [
            (".md 文档", "01_policies_and_standards/governance/ 或 operational/"),
            ("治理规则/标准", "01_policies_and_standards/governance/"),
        ],
    ),
    "01_policies_and_standards/templates": (
        "文档模板 — policy/standard/runbook/playbook/ADT/blueprint/construction-plan/roadmap/risk-register 模板",
        [
            ("正式规则文件", "01_policies_and_standards/governance/ 或 operational/"),
            ("模块文档", "03_modules/"),
        ],
    ),
    "02_enterprise_architecture/adr": (
        "架构决策记录（Architecture Decision Records）— adr-nnnn-*.md",
        [
            ("治理规范", "01_policies_and_standards/"),
            ("模块蓝图", "03_modules/"),
        ],
    ),
    "02_enterprise_architecture/designs": (
        "设计决策框架 — 架构决策辅助文档",
        [
            ("ADR", "02_enterprise_architecture/adr/"),
        ],
    ),
    "_working/audit/reports": (
        "审计报告 — 架构合规性审计、SSoT 验证扫描报告",
        [
            ("治理规范", "01_policies_and_standards/"),
            ("Finding / 事件初稿", "_working/audit/findings/"),
        ],
    ),
    "_working/audit/findings": (
        "安全与合规 Finding、事件响应初稿 Markdown（对齐 target_architecture/06-security_architecture.md）",
        [
            ("审计总控", "_working/audit/index.md"),
            ("审计报告", "_working/audit/reports/"),
        ],
    ),
    # === Level 3 ===
    "01_policies_and_standards/_registry/catalogs": (
        "脚本自动生成的 YAML 注册表（rule_catalog_registry.yaml / master-document-inventory-registry.md / task-card-meta-registry.md）",
        [
            ("手动编辑的文件", "governance/ 对应子域"),
            (".md 文件", "governance/ 或 operational/"),
        ],
    ),
    "01_policies_and_standards/_registry/contracts": (
        "CI 消费的 YAML 验证契约",
        [
            (".md 文件", "governance/"),
        ],
    ),
    "01_policies_and_standards/_registry/schemas": (
        "脚本生成的 JSON Schema（如 frontmatter_schema.json）",
        [
            ("手动编辑的文件", "governance/"),
        ],
    ),
    "01_policies_and_standards/_registry/vocabularies": (
        "AI 消费的 YAML 受控词表（doc_type / rule_form / status）",
        [
            (".md 文件", "governance/"),
        ],
    ),
    "01_policies_and_standards/operational/architecture": (
        "架构操作文档",
        [
            ("声明式架构治理规则", "01_policies_and_standards/governance/architecture/"),
        ],
    ),
    "01_policies_and_standards/operational/devops": (
        "DevOps 操作 — pre_commit/CI/部署流程",
        [
            ("声明式 DevOps 策略", "governance/module/ 或 governance/security/"),
        ],
    ),
    "01_policies_and_standards/operational/migration": (
        "迁移操作 — 迁移审计/迁移步骤",
        [
            ("声明式迁移策略", "governance/"),
        ],
    ),
    "01_policies_and_standards/operational/vibe_coding": (
        "Vibe Coding 操作 — 上下文规则/session 状态机/门禁清单/事件响应",
        [
            ("VC 声明式约束", "01_policies_and_standards/governance/ 对应子域"),
        ],
    ),
    "01_policies_and_standards/scripts/governance": (
        "治理相关自动化脚本",
        [
            (".md 文档", "01_policies_and_standards/governance/"),
        ],
    ),
}

# DOMAIN LAYER RESPONSIBILITIES
DOMAIN_LAYER_MAP = {
    "L00_data_source": "D_DATA 数据接入域 — 数据源连接/清洗规则/Connector 治理与操作",
    "L02_alpha_factor": "D_FACTOR 因子域 — 因子质量门禁/因子上线流程",
    "L04_risk_management": "D_RISK 风控域 — 风险限额策略/止损配置",
    "L07_post_trade_analytics": "D_REPORTING 归因分析域 — 盘后报告策略/分析流水线",
}

MODULE_LAYER_MAP = {
    "data": "D_DATA 数据接入域 — 数据源连接器 / 行情 / 基本面 / 另类数据",
    "infrastructure_runtime_integration": "基础设施域 — AI 基础设施（容量保障 / 运行时集成 / KMS / Vibe Coding 管线 / 触发器路由）",
    "factor": "D_FACTOR 因子域 — 多频段因子计算 / 衍生因子",
    "signal": "D_SIGNAL 信号生成域 — 因子融合 / 信号聚合 / Alpha 组合优化",
    "risk": "D_RISK 风控域 — 头寸限额 / 组合风控 / 实时止损",
    "pf_core": "D_PORTFOLIO_CORE 组合构建域 — 优化器 / 权重再平衡 / 交易指令生成",
    "ex_core": "D_EXECUTION_CORE 交易执行域 — 算法交易 / Order Management / EMS 连接",
    "pf_core": "D_REPORTING 归因分析域 — 绩效归因 / 交易成本分析 / 盘后报表",
    "frontend": "D_FRONTEND 人机界面域 — Dashboard / 可视化 / 告警通知 / 决策控制台",
    "research": "D_RESEARCH 研究创新域 — 策略回测 / 因子研究 / 研究管理",
    "compliance": "D_COMPLIANCE 合规域 — 交易前合规 / 持仓合规 / 监管报送",
    "ml_train": "D_ML_TRAIN ML 平台域 — 模型训练 / 推理服务 / 特征存储 / 模型注册",
    "observability": "遥测域 — 指标 / 日志 / 链路追踪 / AI 行为遥测",
    "integration": "实验管线域 — A/B 测试 / 实验管理 / 参数优化",
}

BOOTSTRAP_LAYER_MAP = {
    "cross_cutting": "过渡期横切施工图（历史）",
}

for k, v in MODULE_LAYER_MAP.items():
    BOOTSTRAP_LAYER_MAP[k] = f"过渡期 {v.split('—')[1].strip() if '—' in v else v} 施工图（历史）"


def get_file_description(filename, dir_path) -> Optional[str]:
    """Generate a human-readable description for a file."""
    name = filename.lower()

    if name.endswith(".yaml") or name.endswith(".yml"):
        if "registry" in name:
            return "YAML 注册表"
        if "contract" in name:
            return "YAML 契约"
        if "schema" in name:
            return "YAML Schema"
        if "vocabulary" in name:
            return "受控词表"
        if "inventory" in name:
            return "文档清单"
        return "YAML 结构定义"

    if name.endswith(".json"):
        return "JSON Schema"

    if name.endswith(".mmd"):
        return "Mermaid 架构图"

    if name.endswith(".py"):
        return "Python 自动化脚本"

    if name.endswith(".ps1"):
        return "PowerShell 脚本"

    if name == "readme.md":
        return "目录说明（人类可读）"
    if name == "index.md":
        return "目录索引（AI 入口）"
    if name.startswith("adr-"):
        nums = name.replace("adr-", "").replace(".md", "")
        return f"架构决策记录 ADR-{nums.upper()}"
    if name == "_template.md":
        return "ADR 模板"
    if name == "blueprint.md":
        return "模块蓝图"
    if name == "construction.md" or name == "construction-plan.md":
        return "模块施工图"
    if name.endswith("-policy.md"):
        return "策略文档"
    if name.endswith("-standard.md"):
        return "标准文档"
    if name.endswith("-protocol.md"):
        return "协议文档"
    if name.endswith("-template.md"):
        return "文档模板"
    if name.endswith("-runbook.md"):
        return "操作手册"
    if name.endswith("-playbook.md"):
        return "操作剧本"
    if name.endswith("-checklist.md") or name.endswith("-gate.md"):
        return "门禁清单"
    if name.endswith("-rules.md"):
        return "规则文档"
    if name.endswith("-declaration.md"):
        return "声明文档"
    if name.endswith("-state-machine.md"):
        return "状态机定义"
    if name.endswith("-taxonomy.md"):
        return "分类法"
    if name.endswith("-architecture.md"):
        return "架构视图"
    if name.endswith("-framework.md"):
        return "决策框架"
    if name.endswith("-log.md"):
        return "日志"
    if name.endswith("-map.md"):
        return "权威映射"
    if name.endswith("-schema.md"):
        return "Schema 定义"

    return "文档"


def build_index_content(rel_dir, files) -> dict:
    """Build index.md content for a directory."""
    dir_name = rel_dir.split("/")[-1] if rel_dir else "docs"
    display_name = dir_name.replace("_", " ").replace("-", " ")

    # Look up responsibility
    resp_info = RESPONSIBILITY_MAP.get(rel_dir) or RESPONSIBILITY_MAP.get(dir_name)

    # Check for domain layers
    if not resp_info and dir_name.startswith("L") and "_" in dir_name:
        idx = dir_name.upper()
        desc = DOMAIN_LAYER_MAP.get(dir_name) or DOMAIN_LAYER_MAP.get(idx, "")
        if desc:
            resp_info = (
                desc,
                [
                    ("全局规则", "01_policies_and_standards/governance/"),
                ],
            )

    # Check for module layers
    if not resp_info and dir_name.startswith("l") and dir_name[1:3].isdigit():
        desc = MODULE_LAYER_MAP.get(dir_name, "")
        if desc:
            resp_info = (
                desc,
                [
                    ("非 C 轨业务层文档", "03_modules/_cross_layer/_b_track_interfaces/ 或 01_policies_and_standards/"),
                ],
            )

    # Check for bootstrap layers
    if not resp_info:
        desc = BOOTSTRAP_LAYER_MAP.get(dir_name, "")
        if desc:
            resp_info = (
                desc,
                [
                    ("新模块施工图", "03_modules/l<NN>_<layer>/<module>/"),
                ],
            )

    # Check sub-contexts: governance/operational under domains
    if not resp_info:
        parent_name = os.path.basename(os.path.dirname(rel_dir)) if "/" in rel_dir else ""
        grandparent = os.path.basename(os.path.dirname(os.path.dirname(rel_dir))) if rel_dir.count("/") >= 2 else ""

        if dir_name == "governance" and parent_name.startswith("L"):
            resp_info = (f"{parent_name} 层声明式治理规则", [("过程式操作规则", "../operational/")])
        elif dir_name == "operational" and parent_name.startswith("L"):
            resp_info = (f"{parent_name} 层过程式操作规则", [("声明式治理规则", "../governance/")])

        # 03_modules module subdirectories
        elif parent_name.startswith("l") and parent_name[1:3].isdigit():
            module_desc = dir_name.replace("-", " ").replace("_", " ")
            resp_info = (f"{parent_name} 层模块 — {module_desc}", [("其他模块文档", "../")])

        # delivery subdirectories under modules
        elif dir_name == "delivery":
            mod_name = parent_name.replace("-", " ").replace("_", " ")
            resp_info = (f"模块交付记录 — {mod_name}", [("蓝图/施工图", "../")])

    if not resp_info:
        resp_info = (f"{display_name}", [])

    responsibility, exclusions = resp_info

    # Build content
    lines = []
    lines.append("---")
    lines.append("doc_type: index")
    lines.append("status: active")
    lines.append(f"generated: '{date.today().isoformat()}'")
    lines.append("---")
    lines.append("")
    lines.append(f"# {dir_name.replace('_', ' ').replace('-', ' ').title()} — 目录索引")
    lines.append("")
    lines.append("## 责任声明（Single Responsibility）")
    lines.append("")
    lines.append(f"本目录只存放：**{responsibility}**。")
    lines.append("")

    # File listing
    if files:
        lines.append("## 文件清单")
        lines.append("")
        lines.append("| 文件 | 说明 |")
        lines.append("|------|------|")

        # Sort: index.md first, then README.md, then others
        priority_order = {"index.md": 0, "readme.md": 1}
        sorted_files = sorted(files, key=lambda f: (priority_order.get(f.lower(), 99), f.lower()))

        for f in sorted_files:
            desc = get_file_description(f, rel_dir)
            lines.append(f"| {f} | {desc} |")

        lines.append("")
    else:
        lines.append("## 文件清单")
        lines.append("")
        lines.append("*（当前为空目录——待填充）*")
        lines.append("")

    # Exclusion rules
    if exclusions:
        lines.append("## 排除规则（不应放入本目录的内容）")
        lines.append("")
        for wrong, correct in exclusions:
            lines.append(f"- ❌ {wrong} → `{correct}`")
        lines.append("")

    # Parent context
    if rel_dir:
        parent = os.path.dirname(rel_dir) if "/" in rel_dir else "."
        parent_name = os.path.basename(parent) if parent != "." else "docs"
        lines.append("## 父级目录")
        lines.append("")
        if parent == ".":
            lines.append("- 父级：[docs 根目录](../index.md)")
        else:
            parent_index = "../index.md"
            lines.append(f"- 父级：[{parent_name}]({parent_index})")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    created = 0
    skipped = 0

    # Collect all directories
    all_dirs = []
    for root, dirs, files in os.walk(DOCS_ROOT):
        rel = os.path.relpath(root, DOCS_ROOT).replace("\\", "/")
        if rel == ".":
            rel = ""
        all_dirs.append((root, rel, files))

    # Sort by depth (shallow first)
    all_dirs.sort(key=lambda x: x[1].count("/"))

    for root_path, rel_dir, files in all_dirs:
        index_path = os.path.join(root_path, "index.md")

        if os.path.exists(index_path):
            skipped += 1
            continue

        # Get non-index, non-readme files for listing
        list_files = [f for f in files if not f.lower().startswith((".git", "thumbs.db", "desktop.ini"))]

        content = build_index_content(rel_dir, list_files)

        try:
            atomic_write_safe(index_path, content)
            print(f"  CREATED: {rel_dir or 'docs/'}/index.md")
            created += 1
        except OSError as e:
            print(f"  ERROR: {rel_dir or 'docs/'}/index.md — {e}", file=sys.stderr)

    print("\n=== Summary ===")
    print(f"Created: {created}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Total directories: {len(all_dirs)}")


if __name__ == "__main__":
    sys.exit(main() or 0)
