# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_runtime_plane_mapping
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
"""G12: 从 depgraph.db 生成运行平面映射图

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.12
[MODULE] scripts.governance.d5_architecture.generators.generate_runtime_plane_mapping
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到01_global_architecture_diagram/
[MODIFY-GUARD] 修改需通过任务卡
[CONSUMERS] CI自动触发;人工查看01_global_architecture_diagram/runtime_plane_mapping.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1
[TESTS] tests/test_dm200910_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from domain_name_mapping import get_domain_name_zh

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_PATH = Path(
    "D:/ZephyrAlpha/docs/02_enterprise_architecture/01_global_architecture_diagram/runtime_plane_mapping.md"
)

# 运行平面中英文对照（数据库 runtime_plane 字段值 → 中文名/英文名/描述）
PLANE_META = {
    "data_plane": {
        "zh": "数据平面",
        "en": "Data Plane",
        "desc": "承载业务数据流转与实际处理（行情/因子/信号/订单等数据通路）",
    },
    "control_plane": {
        "zh": "控制平面",
        "en": "Control Plane",
        "desc": "协调与调度决策（路由/编排/策略分发/状态机驱动）",
    },
    "management_plane": {
        "zh": "管理平面",
        "en": "Management Plane",
        "desc": "配置、监控与治理管理（治理脚本/审计/注册表/运维管理）",
    },
}
UNASSIGNED_LABEL = "未标注"
UNASSIGNED_EN = "Unassigned"


def get_domain_plane_distribution(conn: sqlite3.Connection) -> list[dict]:
    """查询每个域在各运行平面的模块数量分布。"""
    cur = conn.execute(
        """SELECT n.domain_id, d.domain_name, n.runtime_plane, COUNT(*) as cnt
           FROM nodes n
           LEFT JOIN domains d ON n.domain_id = d.domain_id
           WHERE n.domain_id IS NOT NULL AND n.domain_id != ''
           GROUP BY n.domain_id, n.runtime_plane
           ORDER BY n.domain_id, n.runtime_plane"""
    )
    return [
        {
            "domain_id": r[0],
            "domain_name": r[1] or r[0],
            "runtime_plane": r[2],
            "count": r[3],
        }
        for r in cur.fetchall()
    ]


def get_plane_totals(conn: sqlite3.Connection) -> list[dict]:
    """查询各运行平面的模块总数。"""
    cur = conn.execute(
        """SELECT runtime_plane, COUNT(*) as cnt
           FROM nodes
           GROUP BY runtime_plane
           ORDER BY cnt DESC"""
    )
    return [{"runtime_plane": r[0], "count": r[1]} for r in cur.fetchall()]


def get_domain_layer_map(conn: sqlite3.Connection) -> dict[str, str]:
    """查询域→架构层映射。"""
    cur = conn.execute("SELECT domain_id, layer_id FROM domains ORDER BY domain_id")
    return {r[0]: (r[1] or "") for r in cur.fetchall()}


def plane_display(plane: str | None) -> tuple[str, str]:
    """返回运行平面的(中文, 英文)显示名。"""
    if plane and plane in PLANE_META:
        return PLANE_META[plane]["zh"], PLANE_META[plane]["en"]
    return UNASSIGNED_LABEL, UNASSIGNED_EN


def generate_runtime_plane_mapping() -> str:
    """生成运行平面映射图MD文档。"""
    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        distribution = get_domain_plane_distribution(conn)
        plane_totals = get_plane_totals(conn)
        layer_map = get_domain_layer_map(conn)
    finally:
        conn.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构建域×平面矩阵: domain_id -> {plane -> count}
    matrix: dict[str, dict[str, int]] = {}
    domain_names: dict[str, str] = {}
    for row in distribution:
        did = row["domain_id"]
        plane = row["runtime_plane"]
        matrix.setdefault(did, {})
        matrix[did][plane] = matrix[did].get(plane, 0) + row["count"]
        domain_names[did] = get_domain_name_zh(did, row["domain_name"])

    # 收集所有出现过的平面（保持稳定顺序：data/control/management/None）
    plane_order = ["data_plane", "control_plane", "management_plane", None]
    seen_planes = set()
    for row in distribution:
        seen_planes.add(row["runtime_plane"])
    ordered_planes = [p for p in plane_order if p in seen_planes]

    # 统计概览
    total_modules = sum(r["count"] for r in plane_totals)
    total_domains = len(matrix)

    lines: list[str] = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: runtime_plane_mapping")
    lines.append("title: 运行平面映射图")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split()[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 运行平面映射图 / Runtime Plane Mapping")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 展示各功能域模块在数据平面、控制平面、管理平面的分布，用于分析系统运行时职责划分。")
    lines.append("")
    lines.append("> 本文档由 generate_runtime_plane_mapping.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新 / Last updated: {now}")
    lines.append("> 数据源 / Data source: depgraph.db nodes表 runtime_plane 字段")
    lines.append("")
    lines.append("> 注：数据库 runtime_plane 字段采用 SDN 风格三平面分类（data/control/management），")
    lines.append("> 与 runtime_planes.yaml 定义的延迟平面（Hot/Warm/Cold）为正交视图。")
    lines.append("")

    # 统计概览
    lines.append("## 统计概览 / Statistics Overview")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 模块总数 / Total modules | {total_modules} |")
    lines.append(f"| 域总数 / Total domains | {total_domains} |")
    lines.append(f"| 运行平面数 / Runtime planes | {len(ordered_planes)} |")
    lines.append("")

    # 各平面模块总数
    lines.append("## 各运行平面模块总数 / Module Count by Plane")
    lines.append("")
    lines.append("| 运行平面 / Runtime Plane | 中文名 / Chinese | 模块数 / Modules | 占比 / Ratio |")
    lines.append("|------|------|:---:|:---:|")
    for plane in ordered_planes:
        zh, en = plane_display(plane)
        cnt = next((r["count"] for r in plane_totals if r["runtime_plane"] == plane), 0)
        ratio = f"{cnt / total_modules * 100:.1f}%" if total_modules > 0 else "0.0%"
        plane_key = plane if plane else "(null)"
        lines.append(f"| {plane_key} | {zh} | {cnt} | {ratio} |")
    lines.append("")

    # 运行平面定义
    lines.append("## 运行平面定义 / Runtime Plane Definitions")
    lines.append("")
    lines.append("| 运行平面 / Plane | 中文名 / Chinese | 英文名 / English | 说明 / Description |")
    lines.append("|------|------|------|------|")
    for plane in ordered_planes:
        if plane and plane in PLANE_META:
            meta = PLANE_META[plane]
            lines.append(f"| {plane} | {meta['zh']} | {meta['en']} | {meta['desc']} |")
        else:
            lines.append(
                f"| (null) | {UNASSIGNED_LABEL} | {UNASSIGNED_EN} | 未标注运行平面 / Runtime plane not assigned |"
            )
    lines.append("")

    # 域×平面映射矩阵
    lines.append("## 域×运行平面映射矩阵 / Domain × Plane Matrix")
    lines.append("")
    header_planes = " | ".join(
        f"{plane_display(p)[0]} / {plane_display(p)[1]}" if p else f"{UNASSIGNED_LABEL} / {UNASSIGNED_EN}"
        for p in ordered_planes
    )
    lines.append(f"| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | {header_planes} | 总计 / Total |")
    lines.append("|" + "------|" * (4 + len(ordered_planes)))
    for did in sorted(matrix.keys()):
        name = domain_names[did]
        layer = layer_map.get(did, "")
        cells = []
        row_total = 0
        for plane in ordered_planes:
            cnt = matrix[did].get(plane, 0)
            cells.append(str(cnt) if cnt > 0 else "-")
            row_total += cnt
        cells_str = " | ".join(cells)
        lines.append(f"| {did} | {name} | {layer} | {cells_str} | {row_total} |")
    lines.append("")

    # 各平面详情（按域列出模块数）
    for plane in ordered_planes:
        zh, en = plane_display(plane)
        plane_key = plane if plane else "(null)"
        lines.append(f"## {zh} / {en}（{plane_key}）详情")
        lines.append("")
        plane_rows = [
            (did, domain_names[did], matrix[did].get(plane, 0))
            for did in sorted(matrix.keys())
            if matrix[did].get(plane, 0) > 0
        ]
        plane_rows.sort(key=lambda x: x[2], reverse=True)
        plane_total = sum(c for _, _, c in plane_rows)
        lines.append(f"> 模块总数 / Total modules: {plane_total}")
        lines.append("")
        lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 占比 / Ratio |")
        lines.append("|------|------|:---:|:---:|")
        for did, name, cnt in plane_rows:
            ratio = f"{cnt / plane_total * 100:.1f}%" if plane_total > 0 else "0.0%"
            lines.append(f"| {did} | {name} | {cnt} | {ratio} |")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成运行平面映射图。"""
    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    content = generate_runtime_plane_mapping()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
