# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_contract_catalog
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths; _common; _shared.constants.get_depgraph_pg_connection
# [CONSUMERS] 人工查看01_global_architecture_diagram/contract_catalog.md
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到01_global_architecture_diagram/
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
# [TESTS] tests/test_dm200910_generators.py
# [TTL] permanent
"""G12: 从 depgraph (PostgreSQL) 生成契约目录全景图

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.12
[MODULE] scripts.governance.d5_architecture.generators.generate_contract_catalog
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到01_global_architecture_diagram/
[CONSUMERS] 人工查看01_global_architecture_diagram/contract_catalog.md
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _common import DB_DISPLAY_NAME
from _shared.constants import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "01_global_architecture_diagram" / "contract_catalog.md"


def generate_contract_catalog() -> str:
    """生成契约目录全景图 markdown。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        # 查询所有契约
        cur = conn.execute(
            """
            SELECT contract_id, name, provider_domain, consumer_domain,
                   contract_type, schema_definition, version, promise,
                   actual_consumer, fulfillment_status
            FROM contracts
            ORDER BY contract_type, contract_id
            """
        )
        contracts = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    lines: list[str] = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 契约目录全景图")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 契约目录全景图 / Contract Catalog")
    lines.append("")
    lines.append(f"> **文档作用 / Purpose**: 以表格形式展示{len(contracts)}个跨层数据契约,用于AI接入新模块时查询\"消费了谁的契约、产出什么契约\"。")
    lines.append("")
    lines.append(f"> 本文档由 generate_contract_catalog.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 真源: architecture_model/contracts/cross_layer_contracts.yaml")
    lines.append("> 最后更新以 git log 为准")
    lines.append("")

    # 统计概览
    p0_count = sum(1 for c in contracts if c["contract_type"] == "P0")
    p1_count = sum(1 for c in contracts if c["contract_type"] == "P1")
    other_count = len(contracts) - p0_count - p1_count
    planned_count = sum(1 for c in contracts if c["fulfillment_status"] == "planned")
    design_count = sum(1 for c in contracts if c["fulfillment_status"] == "design")

    lines.append("## 1. 统计概览")
    lines.append("")
    lines.append(f"| 指标 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 契约总数 | {len(contracts)} |")
    lines.append(f"| P0(核心数据/错误/背压契约) | {p0_count} |")
    lines.append(f"| P1(蓝图签名契约) | {p1_count} |")
    lines.append(f"| 其他 | {other_count} |")
    lines.append(f"| 已冻结(planned) | {planned_count} |")
    lines.append(f"| 设计中(design) | {design_count} |")
    lines.append("")

    # 契约流向矩阵
    lines.append("## 2. 契约流向矩阵(Provider → Consumer)")
    lines.append("")
    lines.append("> 行:提供方域 | 列:消费方域 | 单元格:契约ID")
    lines.append("")

    # 收集所有域
    all_domains = set()
    for c in contracts:
        if c["provider_domain"]:
            all_domains.add(c["provider_domain"])
        if c["actual_consumer"]:
            for d in c["actual_consumer"].split(", "):
                d = d.strip()
                if d:
                    all_domains.add(d)

    sorted_domains = sorted(all_domains)
    # 表头
    header = "| Provider \\ Consumer | " + " | ".join(sorted_domains) + " |"
    sep = "|---" * (len(sorted_domains) + 1) + "|"
    lines.append(header)
    lines.append(sep)

    # 矩阵内容
    for provider in sorted_domains:
        row = [f"**{provider}**"]
        for consumer in sorted_domains:
            # 找这个 provider→consumer 的契约
            matching = []
            for c in contracts:
                if c["provider_domain"] == provider:
                    actual = c["actual_consumer"] or ""
                    if consumer in actual.split(", "):
                        matching.append(c["contract_id"])
            row.append(", ".join(matching) if matching else "—")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # 契约详情
    lines.append("## 3. 契约详情")
    lines.append("")

    for c in contracts:
        lines.append(f"### {c['contract_id']} — {c['name'] or ''}")
        lines.append("")
        lines.append(f"- **类型**: {c['contract_type'] or 'unknown'}")
        lines.append(f"- **版本**: {c['version'] or '—'}")
        lines.append(f"- **提供方**: {c['provider_domain'] or '—'}")
        lines.append(f"- **消费方**: {c['actual_consumer'] or '—'}")
        lines.append(f"- **状态**: {c['fulfillment_status'] or '—'}")
        lines.append(f"- **描述**: {c['promise'] or '—'}")

        # 解析 schema_definition
        if c["schema_definition"]:
            try:
                schema = json.loads(c["schema_definition"])
                fields = schema.get("fields", [])
                if fields:
                    lines.append("")
                    lines.append("| 字段 | 类型 | 必填 | 描述 |")
                    lines.append("|------|------|------|------|")
                    for f in fields:
                        name = f.get("name", "")
                        ftype = f.get("type", "")
                        required = "✅" if f.get("required") else "—"
                        desc = f.get("description", "")
                        lines.append(f"| {name} | {ftype} | {required} | {desc} |")
                physical_path = schema.get("physical_path", "")
                if physical_path:
                    lines.append("")
                    lines.append(f"- **物理路径**: `{physical_path}`")
            except json.JSONDecodeError:
                pass
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    content = generate_contract_catalog()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
