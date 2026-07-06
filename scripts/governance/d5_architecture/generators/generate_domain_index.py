# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_index
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
# [TTL] task_bound
"""G5: 从 depgraph (PostgreSQL) domains+nodes 表生成域总览索引MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_index
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/domain_index.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/domain_index.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
[TESTS] tests/test_dm200911_generators.py
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# 治本（2026-07-04）：DB_DISPLAY_NAME 前移到 __manifest__ 之前，避免 f-string 求值时 NameError。
# _common.py 与本文件同目录（generators/），CLI 运行时 sys.path[0]=本目录，可直接 import。
from _common import DB_DISPLAY_NAME  # noqa: E402

__manifest__ = f"""
args: []
description: 'G5: 从 {DB_DISPLAY_NAME} domains+nodes 表生成域总览索引MD文档'
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

from domain_name_mapping import get_domain_name_zh, get_domain_name_en, get_layer_name_bilingual
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

# 治本（2026-07-06）：复用 generate_domain_doc 的编号映射，确保索引链接与文件名一致
_GENERATORS_DIR = _THIS_FILE.parent
if str(_GENERATORS_DIR) not in sys.path:
    sys.path.insert(0, str(_GENERATORS_DIR))
from generate_domain_doc import build_numbering_map  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "02_domain_architecture_docs" / "domain_index.md"


def get_all_domains(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询所有域及其模块统计。"""
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                  d.max_modules, d.description,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production_count,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design_count,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'prototype') as prototype_count
           FROM domains d
           ORDER BY d.domain_id"""
    )
    return [
        {
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"] or "",
            "layer_id": r["layer_id"] or "",
            "current_modules": r["current_modules"] or 0,
            "max_modules": r["max_modules"] or 200,
            "description": r["description"] or "",
            "actual_nodes": r["actual_nodes"],
            "production_count": r["production_count"],
            "design_count": r["design_count"],
            "prototype_count": r["prototype_count"],
        }
        for r in cur.fetchall()
    ]


def generate_domain_index() -> str:
    """生成域总览索引MD文档。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        domains = get_all_domains(conn)
        numbering_map = build_numbering_map(conn)
    finally:
        conn.close()

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: index")
    lines.append("title: 域总览索引")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 域总览索引")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。")
    lines.append("")
    lines.append(f"> 本文档由 generate_domain_index.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} domains表 + nodes表")
    lines.append("")

    # 统计概览
    total_domains = len(domains)
    total_nodes = sum(d["actual_nodes"] for d in domains)
    total_production = sum(d["production_count"] for d in domains)
    total_design = sum(d["design_count"] for d in domains)
    total_prototype = sum(d["prototype_count"] for d in domains)

    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 | {total_domains} |")
    lines.append(f"| 模块总数 | {total_nodes} |")
    lines.append(f"| 生产态模块 | {total_production} |")
    lines.append(f"| 设计态模块 | {total_design} |")
    lines.append(f"| 原型态模块 | {total_prototype} |")
    lines.append("")

    # 按架构层分组
    layers: dict[str, list[dict]] = {}
    for d in domains:
        layer = d["layer_id"] or "未分类"
        layers.setdefault(layer, []).append(d)

    lines.append("## 域清单（按架构层分组）")
    lines.append("")

    for layer in sorted(layers.keys()):
        layer_domains = layers[layer]
        layer_zh, layer_en = get_layer_name_bilingual(layer)
        lines.append(f"### {layer_zh} / {layer_en} ({len(layer_domains)} 个域 / {len(layer_domains)} domains)")
        lines.append("")
        lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |")
        lines.append("|------|--------|:---:|:---:|:---:|:---:|------|------|")
        for d in layer_domains:
            capacity = f"{d['actual_nodes']}/{d['max_modules']}"
            capacity_status = "OK" if d["actual_nodes"] <= d["max_modules"] else "超容"
            safe_name = d["domain_id"].replace("-", "_").lower()
            number = numbering_map.get(d["domain_id"], 0)
            if number:
                doc_link = f"[{number:02d}_{safe_name}.md]({number:02d}_{safe_name}.md)"
            else:
                doc_link = f"[{safe_name}.md](未编号)"
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} / {get_domain_name_en(d['domain_id'])} | {d['actual_nodes']} | "
                f"{d['production_count']} | {d['design_count']} | {d['prototype_count']} | "
                f"{capacity} ({capacity_status}) | {doc_link} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域总览索引。"""
    content = generate_domain_index()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
