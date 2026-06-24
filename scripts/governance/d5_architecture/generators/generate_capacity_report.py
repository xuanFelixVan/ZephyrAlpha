# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_capacity_report
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""G7: 从 depgraph.db domains 表生成域容量报告MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_capacity_report
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到generated/capacity_report.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/capacity_report.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1
[TESTS] tests/test_dm200911_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from domain_name_mapping import get_domain_name_zh

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_PATH = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/capacity_report.md")


def get_domain_capacity(conn: sqlite3.Connection) -> list[dict]:
    """查询所有域的容量信息。"""
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                  d.max_modules, d.target_modules, d.description,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes
           FROM domains d
           ORDER BY d.domain_id"""
    )
    return [
        {
            "domain_id": r[0],
            "domain_name": r[1] or "",
            "layer_id": r[2] or "",
            "current_modules": r[3] or 0,
            "max_modules": r[4] or 200,
            "target_modules": r[5],
            "description": r[6] or "",
            "actual_nodes": r[7],
        }
        for r in cur.fetchall()
    ]


def generate_capacity_report() -> str:
    """生成域容量报告MD文档。"""
    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        domains = get_domain_capacity(conn)
    finally:
        conn.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: capacity_report")
    lines.append("title: 域容量报告")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split()[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 域容量报告")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 展示各功能域的模块数量与容量上限对比，识别超容域和接近超容域，为域拆分决策提供依据。")
    lines.append("")
    lines.append("> 本文档由 generate_capacity_report.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新: {now}")
    lines.append("> 数据源: depgraph.db domains表 + nodes表")
    lines.append("")

    # 统计概览
    total_domains = len(domains)
    over_capacity = [d for d in domains if d["actual_nodes"] > d["max_modules"]]
    near_capacity = [
        d
        for d in domains
        if d["max_modules"] > 0 and d["actual_nodes"] / d["max_modules"] > 0.8 and d["actual_nodes"] <= d["max_modules"]
    ]
    empty_domains = [d for d in domains if d["actual_nodes"] == 0]

    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 | {total_domains} |")
    lines.append(f"| 超容域 | {len(over_capacity)} |")
    lines.append(f"| 接近超容域（>80%） | {len(near_capacity)} |")
    lines.append(f"| 空域（0模块） | {len(empty_domains)} |")
    lines.append("")

    # 超容域清单
    if over_capacity:
        lines.append("## 超容域清单（需拆分）")
        lines.append("")
        lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 超出 / Over |")
        lines.append("|------|--------|:---:|:---:|:---:|")
        for d in over_capacity:
            over = d["actual_nodes"] - d["max_modules"]
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['actual_nodes']} | "
                f"{d['max_modules']} | +{over} |"
            )
        lines.append("")

    # 接近超容域清单
    if near_capacity:
        lines.append("## 接近超容域清单（>80%，需关注）")
        lines.append("")
        lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |")
        lines.append("|------|--------|:---:|:---:|:---:|")
        for d in near_capacity:
            usage = d["actual_nodes"] / d["max_modules"] * 100
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['actual_nodes']} | "
                f"{d['max_modules']} | {usage:.1f}% |"
            )
        lines.append("")

    # 空域清单
    if empty_domains:
        lines.append("## 空域清单（0模块，待开发）")
        lines.append("")
        lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |")
        lines.append("|------|--------|--------|:---:|")
        for d in empty_domains:
            lines.append(f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['layer_id']} | {d['max_modules']} |")
        lines.append("")

    # 完整容量清单
    lines.append("## 完整域容量清单")
    lines.append("")
    lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |")
    lines.append("|------|--------|--------|:---:|:---:|:---:|------|")
    for d in domains:
        if d["max_modules"] > 0:
            usage = d["actual_nodes"] / d["max_modules"] * 100
            if d["actual_nodes"] > d["max_modules"]:
                status = "超容"
            elif usage > 80:
                status = "接近超容"
            elif d["actual_nodes"] == 0:
                status = "空"
            else:
                status = "正常"
        else:
            usage = 0
            status = "无上限"
        lines.append(
            f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['layer_id']} | "
            f"{d['actual_nodes']} | {d['max_modules']} | {usage:.1f}% | {status} |"
        )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域容量报告。"""
    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    content = generate_capacity_report()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
