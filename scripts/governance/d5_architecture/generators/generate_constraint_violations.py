# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_constraint_violations
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
"""G9: 从 depgraph (PostgreSQL) arch_constraints 表生成架构约束违规报告MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_constraint_violations
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/constraint_violations.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/constraint_violations.md
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
description: 'G9: 从 {DB_DISPLAY_NAME} arch_constraints 表生成架构约束违规报告MD文档'
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

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "constraint_violations.md"


def get_all_constraints(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询所有架构约束。"""
    cur = conn.execute(
        """SELECT constraint_id, name, constraint_type, from_domain, to_domain,
                  rule_definition, severity, enforcement, description,
                  violation_status, details, detected_at
           FROM arch_constraints
           ORDER BY violation_status DESC, severity DESC, constraint_id"""
    )
    return [
        {
            "constraint_id": r["constraint_id"] or "",
            "name": r["name"] or "",
            "constraint_type": r["constraint_type"] or "",
            "from_domain": r["from_domain"] or "",
            "to_domain": r["to_domain"] or "",
            "rule_definition": r["rule_definition"] or "",
            "severity": r["severity"] or "",
            "enforcement": r["enforcement"] or "",
            "description": r["description"] or "",
            "violation_status": r["violation_status"] or "",
            "details": r["details"] or "",
            "detected_at": r["detected_at"] or "",
        }
        for r in cur.fetchall()
    ]


def generate_constraint_violations() -> str:
    """生成架构约束违规报告。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        constraints = get_all_constraints(conn)
    finally:
        conn.close()

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: audit_report")
    lines.append("title: 架构约束违规报告")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 架构约束违规报告")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。")
    lines.append("")
    lines.append(f"> 本文档由 generate_constraint_violations.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} arch_constraints表")
    lines.append("")

    # 统计概览
    total = len(constraints)
    open_violations = [c for c in constraints if c["violation_status"] == "open"]
    resolved = [c for c in constraints if c["violation_status"] == "resolved"]
    other_status = [c for c in constraints if c["violation_status"] not in ("open", "resolved")]

    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 约束总数 | {total} |")
    lines.append(f"| Open（未解决） | {len(open_violations)} |")
    lines.append(f"| Resolved（已解决） | {len(resolved)} |")
    lines.append(f"| 其他状态 | {len(other_status)} |")
    lines.append("")

    # 按严重程度分组
    severity_groups: dict[str, list[dict]] = {}
    for c in constraints:
        sev = c["severity"] or "unknown"
        severity_groups.setdefault(sev, []).append(c)

    lines.append("## 按严重程度分组")
    lines.append("")
    lines.append("| 严重程度 / Severity | 数量 / Count |")
    lines.append("|---------|:---:|")
    for sev in sorted(severity_groups.keys()):
        lines.append(f"| {sev} | {len(severity_groups[sev])} |")
    lines.append("")

    # 按约束类型分组
    type_groups: dict[str, list[dict]] = {}
    for c in constraints:
        ct = c["constraint_type"] or "unknown"
        type_groups.setdefault(ct, []).append(c)

    lines.append("## 按约束类型分组")
    lines.append("")
    lines.append("| 约束类型 / Constraint Type | 数量 / Count |")
    lines.append("|---------|:---:|")
    for ct in sorted(type_groups.keys()):
        lines.append(f"| {ct} | {len(type_groups[ct])} |")
    lines.append("")

    # Open 违规清单
    if open_violations:
        lines.append("## Open 违规清单（需处理）")
        lines.append("")
        lines.append("| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |")
        lines.append("|--------|------|------|------|--------|---------|---------|------|")
        for c in open_violations:
            desc_short = c["description"][:60] + "..." if len(c["description"]) > 60 else c["description"]
            lines.append(
                f"| {c['constraint_id']} | {c['name']} | {c['constraint_type']} | "
                f"{c['from_domain']} | {c['to_domain']} | {c['severity']} | "
                f"{c['enforcement']} | {desc_short} |"
            )
        lines.append("")

    # 完整约束清单
    lines.append("## 完整约束清单")
    lines.append("")
    lines.append("| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |")
    lines.append("|--------|------|------|------|--------|---------|------|")
    for c in constraints:
        lines.append(
            f"| {c['constraint_id']} | {c['name']} | {c['constraint_type']} | "
            f"{c['from_domain']} | {c['to_domain']} | {c['severity']} | "
            f"{c['violation_status']} |"
        )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成架构约束违规报告。"""
    content = generate_constraint_violations()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
