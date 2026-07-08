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
# [TTL] permanent
"""G7: 从 depgraph (PostgreSQL) domains 表生成域容量报告MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_capacity_report
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/capacity_report.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/capacity_report.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# 治本（2026-07-04）：DB_DISPLAY_NAME 前移到 __manifest__ 之前，避免 f-string 求值时 NameError。
# _common.py 与本文件同目录（generators/），CLI 运行时 sys.path[0]=本目录，可直接 import。
from _common import DB_DISPLAY_NAME  # noqa: E402

__manifest__ = f"""
args: []
description: 'G7: 从 {DB_DISPLAY_NAME} domains 表生成域容量报告MD文档'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from domain_name_mapping import get_domain_name_zh
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "capacity_report.md"


def get_domain_capacity(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询所有域的容量信息（ARCH-CAP-001: production_nodes 口径）。"""
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                  d.max_modules, d.target_modules, d.description, d.production_nodes
           FROM domains d
           ORDER BY d.domain_id"""
    )
    return [
        {
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"] or "",
            "layer_id": r["layer_id"] or "",
            "current_modules": r["current_modules"] or 0,
            "max_modules": r["max_modules"] or 150,
            "target_modules": r["target_modules"],
            "description": r["description"] or "",
            "production_nodes": r["production_nodes"] or 0,
        }
        for r in cur.fetchall()
    ]


def generate_capacity_report() -> str:
    """生成域容量报告MD文档。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        domains = get_domain_capacity(conn)
    finally:
        conn.close()

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: audit_report")
    lines.append("title: 域容量报告")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 域容量报告")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 展示各功能域的模块数量与容量上限对比，识别超容域和接近超容域，为域拆分决策提供依据。")
    lines.append("")
    lines.append(f"> 本文档由 generate_capacity_report.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} domains表 + nodes表")
    lines.append("")

    # 统计概览
    total_domains = len(domains)
    over_capacity = [d for d in domains if d["production_nodes"] > d["max_modules"]]
    near_capacity = [
        d
        for d in domains
        if d["max_modules"] > 0 and d["production_nodes"] / d["max_modules"] > 0.8 and d["production_nodes"] <= d["max_modules"]
    ]
    empty_domains = [d for d in domains if d["production_nodes"] == 0]

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
            over = d["production_nodes"] - d["max_modules"]
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['production_nodes']} | "
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
            usage = d["production_nodes"] / d["max_modules"] * 100
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['production_nodes']} | "
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
            usage = d["production_nodes"] / d["max_modules"] * 100
            if d["production_nodes"] > d["max_modules"]:
                status = "超容"
            elif usage > 80:
                status = "接近超容"
            elif d["production_nodes"] == 0:
                status = "空"
            else:
                status = "正常"
        else:
            usage = 0
            status = "无上限"
        lines.append(
            f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['layer_id']} | "
            f"{d['production_nodes']} | {d['max_modules']} | {usage:.1f}% | {status} |"
        )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域容量报告。"""
    content = generate_capacity_report()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
