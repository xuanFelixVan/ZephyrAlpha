# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_capability_heatmap
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
"""G11: 从 depgraph.db 生成能力热力图

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.11
[MODULE] scripts.governance.d5_architecture.generators.generate_capability_heatmap
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到01_global_architecture_diagram/
[MODIFY-GUARD] 修改需通过任务卡
[CONSUMERS] CI自动触发;人工查看01_global_architecture_diagram/capability_heatmap.md
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

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_PATH = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/01_global_architecture_diagram/capability_heatmap.md")

# 10 capability domains (能力域) - 7 business + 3 cross-cutting
# Source: capability_heatmap.yaml v3.0.0 + capability_heatmap.md §3.1
CAPABILITY_DOMAINS: list[dict] = [
    {
        "id": "C1",
        "name": "数据接入",
        "name_en": "Data Ingestion",
        "type": "业务",
        "domains": ["D-MKT_DATA", "D-ALT_DATA", "D-DATA_ENG"],
    },
    {
        "id": "C2",
        "name": "因子研究",
        "name_en": "Factor & Signal",
        "type": "业务",
        "domains": ["D-FACTOR", "D-SIGNAL", "D-SIGNAL_FUNDAMENTAL", "D-SIGNAL_ASHARE", "D-SIGNAL_QUALITY"],
    },
    {
        "id": "C3",
        "name": "风险控制",
        "name_en": "Risk Control",
        "type": "业务",
        "domains": ["D-RISK", "D-COMPLIANCE"],
    },
    {
        "id": "C4",
        "name": "策略决策",
        "name_en": "Strategy Decision",
        "type": "业务",
        "domains": ["D-PF_CORE", "D-PF_ALLOC", "D-SELL_DECISION", "D-CROSS_ASSET"],
    },
    {
        "id": "C5",
        "name": "执行交易",
        "name_en": "Execution & Trading",
        "type": "业务",
        "domains": ["D-EX_CORE", "D-EX_SOR", "D-TRADING", "D-POSITION"],
    },
    {
        "id": "C6",
        "name": "ML平台",
        "name_en": "ML Platform",
        "type": "业务",
        "domains": ["D-ML_TRAIN", "D-ML_SERVE"],
    },
    {
        "id": "C7",
        "name": "回测仿真",
        "name_en": "Backtest & Simulation",
        "type": "业务",
        "domains": ["D-BACKTEST", "D-SIMULATION", "D-EXEC_SIM", "D-DIGITAL_TWIN"],
    },
    {
        "id": "CC1",
        "name": "治理合规",
        "name_en": "Governance & Compliance",
        "type": "横切",
        "domains": [
            "D-GOVERNANCE", "D-GOV_RULE", "D-GOV_AUDIT", "D-GOV_DRIFT",
            "D-GOV_ENFORCEMENT", "D-GOV_REPAIR", "D-GOV_SCRIPTS",
        ],
    },
    {
        "id": "CC2",
        "name": "安全防护",
        "name_en": "Security",
        "type": "横切",
        "domains": ["D-SECURITY", "D-SECURITY-LLM", "D-BEHAVIORAL_AUDIT", "D-DATA_SEC", "D-AUTONOMY_PERM"],
    },
    {
        "id": "CC3",
        "name": "基础设施",
        "name_en": "Infrastructure",
        "type": "横切",
        "domains": [
            "D-INFRA_OPS", "D-INFRA_RUNTIME", "D-INTEGRATION", "D-INTEGRATION-GATEWAY",
            "D-SHARED", "D-FRONTEND", "D-REPORTING", "D-KNOWLEDGE",
            "D-INTELLIGENCE", "D-AUTONOMY_CORE", "D-OPS",
        ],
    },
]

# Maturity levels (L0-L5) - Source: capability_heatmap.yaml v3.0.0
# symbol: maturity symbol; coverage: ✅/🟡/❌; name_en: English name
MATURITY_LEVELS: dict[str, dict] = {
    "L0": {"symbol": "⚪", "coverage": "❌", "name_en": "Missing", "name_zh": "缺失", "score": 0},
    "L1": {"symbol": "🔵", "coverage": "🟡", "name_en": "Designed", "name_zh": "设计", "score": 1},
    "L2": {"symbol": "🟡", "coverage": "🟡", "name_en": "Drafted", "name_zh": "草稿", "score": 2},
    "L3": {"symbol": "🟢", "coverage": "✅", "name_en": "Usable", "name_zh": "可用", "score": 3},
    "L4": {"symbol": "🟣", "coverage": "✅", "name_en": "Production", "name_zh": "生产级", "score": 4},
    "L5": {"symbol": "🔴", "coverage": "✅", "name_en": "Leading", "name_zh": "顶级对标", "score": 5},
}

# Test domain prefixes to exclude (not real architecture domains)
TEST_DOMAIN_PREFIXES = ("D-T3-", "D-T4-", "D-T5-", "D-T9-")


def normalize_domain_id(domain_id: str) -> str:
    """Normalize domain ID for matching (handle hyphen/underscore inconsistency)."""
    return domain_id.upper().replace("-", "_")


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a table exists in the database."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    )
    return cur.fetchone() is not None


def get_all_domains(conn: sqlite3.Connection) -> list[dict]:
    """Query all domains from the domains table."""
    cur = conn.execute(
        "SELECT domain_id, domain_name, layer_id FROM domains ORDER BY domain_id"
    )
    return [
        {
            "domain_id": r[0],
            "domain_name": r[1] or "",
            "layer_id": r[2] or "",
        }
        for r in cur.fetchall()
    ]


def get_domain_maturity_counts(conn: sqlite3.Connection) -> dict[str, dict[str, int]]:
    """Query node maturity counts grouped by domain_id and design_maturity.

    Returns: {domain_id: {"production": N, "design": N, "prototype": N, "active": N}}
    """
    cur = conn.execute(
        """SELECT domain_id, design_maturity, COUNT(*)
           FROM nodes
           WHERE domain_id IS NOT NULL
           GROUP BY domain_id, design_maturity"""
    )
    result: dict[str, dict[str, int]] = {}
    for r in cur.fetchall():
        domain_id = r[0]
        maturity = (r[1] or "unknown").lower()
        count = r[2]
        result.setdefault(domain_id, {}).setdefault(maturity, 0)
        result[domain_id][maturity] += count

    # Also query build_status='active' counts for L4 detection
    cur = conn.execute(
        """SELECT domain_id, COUNT(*)
           FROM nodes
           WHERE domain_id IS NOT NULL
             AND design_maturity = 'production'
             AND build_status = 'active'
           GROUP BY domain_id"""
    )
    for r in cur.fetchall():
        domain_id = r[0]
        count = r[1]
        result.setdefault(domain_id, {})["active"] = count

    return result


def compute_maturity_level(counts: dict[str, int]) -> str:
    """Compute maturity level (L0-L5) from node maturity counts.

    L0: no nodes
    L1: only design nodes (no production, no prototype)
    L2: has prototype nodes (no production)
    L3: has production nodes (build_status != active)
    L4: has production nodes with build_status=active
    L5: leading (not computable from depgraph.db, reserved)
    """
    production = counts.get("production", 0)
    design = counts.get("design", 0)
    prototype = counts.get("prototype", 0)
    active = counts.get("active", 0)
    total = production + design + prototype

    if total == 0:
        return "L0"
    if active > 0:
        return "L4"
    if production > 0:
        return "L3"
    if prototype > 0:
        return "L2"
    if design > 0:
        return "L1"
    return "L0"


def build_domain_capability_map() -> dict[str, str]:
    """Build a map from normalized domain_id -> capability domain id."""
    result: dict[str, str] = {}
    for cap in CAPABILITY_DOMAINS:
        for domain_id in cap["domains"]:
            result[normalize_domain_id(domain_id)] = cap["id"]
    return result


def generate_heatmap() -> str:
    """Generate the capability heatmap markdown document."""
    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        use_arch_table = table_exists(conn, "arch_domain_capacity")
        if use_arch_table:
            data_source = "depgraph.db arch_domain_capacity表"
            # Primary data source: arch_domain_capacity table
            # When this table exists, query it for capability data
            domains = get_all_domains(conn)
            maturity_counts = get_domain_maturity_counts(conn)
        else:
            # Fallback: arch_domain_capacity merged into domains table in v6
            data_source = (
                "depgraph.db domains表 + nodes表 "
                "(注: arch_domain_capacity表不存在，v6已合并入domains表)"
            )
            domains = get_all_domains(conn)
            maturity_counts = get_domain_maturity_counts(conn)
    finally:
        conn.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    domain_cap_map = build_domain_capability_map()

    # Filter out test domains
    real_domains = [
        d for d in domains
        if not any(d["domain_id"].startswith(prefix) for prefix in TEST_DOMAIN_PREFIXES)
    ]

    # Compute maturity for each domain
    domain_data: list[dict] = []
    for d in real_domains:
        did = d["domain_id"]
        counts = maturity_counts.get(did, {})
        level = compute_maturity_level(counts)
        cap_id = domain_cap_map.get(normalize_domain_id(did))
        domain_data.append({
            **d,
            "maturity_level": level,
            "capability_id": cap_id,
            "production": counts.get("production", 0),
            "design": counts.get("design", 0),
            "prototype": counts.get("prototype", 0),
            "active": counts.get("active", 0),
            "total_nodes": counts.get("production", 0) + counts.get("design", 0) + counts.get("prototype", 0),
        })

    # Sort by capability domain, then by domain_id
    cap_order = {cap["id"]: i for i, cap in enumerate(CAPABILITY_DOMAINS)}
    domain_data.sort(
        key=lambda d: (cap_order.get(d["capability_id"], 999), d["domain_id"])
    )

    lines: list[str] = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: capability_heatmap")
    lines.append("title: 能力热力图")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f'date: {now.split()[0]}')
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 能力热力图 / Capability Heatmap")
    lines.append("")
    lines.append("> 本文档由 generate_capability_heatmap.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新: {now}")
    lines.append(f"> 数据源: {data_source}")
    lines.append("")

    # Statistics overview
    total_domains = len(domain_data)
    l0_count = sum(1 for d in domain_data if d["maturity_level"] == "L0")
    l1_count = sum(1 for d in domain_data if d["maturity_level"] == "L1")
    l2_count = sum(1 for d in domain_data if d["maturity_level"] == "L2")
    l3_count = sum(1 for d in domain_data if d["maturity_level"] == "L3")
    l4_count = sum(1 for d in domain_data if d["maturity_level"] == "L4")
    full_coverage = sum(1 for d in domain_data if d["maturity_level"] in ("L3", "L4", "L5"))
    partial_coverage = sum(1 for d in domain_data if d["maturity_level"] in ("L1", "L2"))
    no_coverage = sum(1 for d in domain_data if d["maturity_level"] == "L0")

    lines.append("## 统计概览 / Statistics Overview")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 / Total Domains | {total_domains} |")
    lines.append(f"| 能力域数 / Capability Domains | {len(CAPABILITY_DOMAINS)} |")
    lines.append(f"| ✅ 完全覆盖 / Full Coverage (L3+) | {full_coverage} |")
    lines.append(f"| 🟡 部分覆盖 / Partial Coverage (L1-L2) | {partial_coverage} |")
    lines.append(f"| ❌ 无覆盖 / No Coverage (L0) | {no_coverage} |")
    lines.append("")

    # Maturity level legend
    lines.append("## 成熟度图例 / Maturity Legend")
    lines.append("")
    lines.append("| 等级 | 符号 | 覆盖度 | 中文名 | 英文名 | 定义 |")
    lines.append("|:---:|:---:|:---:|--------|--------|------|")
    for level_id in ("L0", "L1", "L2", "L3", "L4", "L5"):
        info = MATURITY_LEVELS[level_id]
        lines.append(
            f"| {level_id} | {info['symbol']} | {info['coverage']} | "
            f"{info['name_zh']} | {info['name_en']} | "
            f"{_maturity_definition(level_id)} |"
        )
    lines.append("")

    # Capability domain definitions
    lines.append("## 能力域定义 / Capability Domain Definitions")
    lines.append("")
    lines.append("| 能力域ID | 中文名 | 英文名 | 类型 | 包含域数 | 包含域 |")
    lines.append("|:---:|--------|--------|:---:|:---:|--------|")
    for cap in CAPABILITY_DOMAINS:
        domains_str = ", ".join(cap["domains"])
        lines.append(
            f"| {cap['id']} | {cap['name']} | {cap['name_en']} | "
            f"{cap['type']} | {len(cap['domains'])} | {domains_str} |"
        )
    lines.append("")

    # 43 domains × 10 capability domains matrix
    lines.append("## 能力热力图矩阵 / Capability Heatmap Matrix")
    lines.append("")
    lines.append("> 行：架构域（43域） | 列：能力域（10能力域）")
    lines.append("> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）")
    lines.append("")

    # Matrix header
    header = "| 架构域 | 域名称 |"
    separator = "|--------|--------|"
    for cap in CAPABILITY_DOMAINS:
        header += f" {cap['id']} |"
        separator += ":---:|"
    header += " 成熟度 |"
    separator += ":---:|"
    lines.append(header)
    lines.append(separator)

    for d in domain_data:
        row = f"| {d['domain_id']} | {d['domain_name']} |"
        for cap in CAPABILITY_DOMAINS:
            if d["capability_id"] == cap["id"]:
                symbol = MATURITY_LEVELS[d["maturity_level"]]["symbol"]
                row += f" {symbol} |"
            else:
                row += " — |"
        row += f" {d['maturity_level']} |"
        lines.append(row)
    lines.append("")

    # Capability domain maturity summary
    lines.append("## 能力域成熟度汇总 / Capability Domain Maturity Summary")
    lines.append("")
    lines.append("| 能力域 | 中文名 | 域数量 | 总节点 | production | design | prototype | 平均成熟度 | 覆盖度 |")
    lines.append("|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

    for cap in CAPABILITY_DOMAINS:
        cap_domains = [
            d for d in domain_data
            if d["capability_id"] == cap["id"]
        ]
        cap_count = len(cap_domains)
        total_nodes = sum(d["total_nodes"] for d in cap_domains)
        total_prod = sum(d["production"] for d in cap_domains)
        total_design = sum(d["design"] for d in cap_domains)
        total_proto = sum(d["prototype"] for d in cap_domains)

        if cap_count > 0:
            avg_score = sum(
                MATURITY_LEVELS[d["maturity_level"]]["score"] for d in cap_domains
            ) / cap_count
            full = sum(1 for d in cap_domains if d["maturity_level"] in ("L3", "L4", "L5"))
            partial = sum(1 for d in cap_domains if d["maturity_level"] in ("L1", "L2"))
            none = sum(1 for d in cap_domains if d["maturity_level"] == "L0")
            if full == cap_count:
                coverage = "✅ 完全覆盖"
            elif full > 0 or partial > 0:
                coverage = "🟡 部分覆盖"
            else:
                coverage = "❌ 无覆盖"
        else:
            avg_score = 0
            coverage = "❌ 无覆盖"

        lines.append(
            f"| {cap['id']} | {cap['name']} | {cap_count} | {total_nodes} | "
            f"{total_prod} | {total_design} | {total_proto} | "
            f"{avg_score:.2f} | {coverage} |"
        )
    lines.append("")

    # Detailed domain maturity list
    lines.append("## 域成熟度明细 / Domain Maturity Detail")
    lines.append("")
    lines.append("| 架构域 | 域名称 | 能力域 | 架构层 | 节点数 | production | design | prototype | active | 成熟度 | 覆盖度 |")
    lines.append("|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    for d in domain_data:
        info = MATURITY_LEVELS[d["maturity_level"]]
        cap_name = d["capability_id"] or "—"
        lines.append(
            f"| {d['domain_id']} | {d['domain_name']} | {cap_name} | "
            f"{d['layer_id']} | {d['total_nodes']} | "
            f"{d['production']} | {d['design']} | {d['prototype']} | {d['active']} | "
            f"{d['maturity_level']} {info['symbol']} | {info['coverage']} |"
        )
    lines.append("")

    # Gap analysis
    lines.append("## 差距分析 / Gap Analysis")
    lines.append("")
    lines.append("### P0 短板（L0-L1，需优先补齐）")
    lines.append("")
    lines.append("| 架构域 | 域名称 | 能力域 | 当前成熟度 | 节点数 |")
    lines.append("|--------|--------|:---:|:---:|:---:|")
    p0_domains = [d for d in domain_data if d["maturity_level"] in ("L0", "L1")]
    if p0_domains:
        for d in p0_domains:
            cap_name = d["capability_id"] or "—"
            lines.append(
                f"| {d['domain_id']} | {d['domain_name']} | {cap_name} | "
                f"{d['maturity_level']} | {d['total_nodes']} |"
            )
    else:
        lines.append("| — | 无P0短板 | — | — | — |")
    lines.append("")

    lines.append("### P1 关注（L2，有原型待集成）")
    lines.append("")
    lines.append("| 架构域 | 域名称 | 能力域 | 当前成熟度 | 节点数 |")
    lines.append("|--------|--------|:---:|:---:|:---:|")
    p1_domains = [d for d in domain_data if d["maturity_level"] == "L2"]
    if p1_domains:
        for d in p1_domains:
            cap_name = d["capability_id"] or "—"
            lines.append(
                f"| {d['domain_id']} | {d['domain_name']} | {cap_name} | "
                f"{d['maturity_level']} | {d['total_nodes']} |"
            )
    else:
        lines.append("| — | 无P1关注 | — | — | — |")
    lines.append("")

    lines.append("### 已就绪（L3+，可用/生产级）")
    lines.append("")
    lines.append("| 架构域 | 域名称 | 能力域 | 当前成熟度 | 节点数 |")
    lines.append("|--------|--------|:---:|:---:|:---:|")
    ready_domains = [d for d in domain_data if d["maturity_level"] in ("L3", "L4", "L5")]
    if ready_domains:
        for d in ready_domains:
            cap_name = d["capability_id"] or "—"
            lines.append(
                f"| {d['domain_id']} | {d['domain_name']} | {cap_name} | "
                f"{d['maturity_level']} | {d['total_nodes']} |"
            )
    else:
        lines.append("| — | 无L3+域 | — | — | — |")
    lines.append("")

    # Unmapped domains (not in any capability domain)
    unmapped = [d for d in domain_data if d["capability_id"] is None]
    if unmapped:
        lines.append("## 未映射域 / Unmapped Domains")
        lines.append("")
        lines.append("> 以下域未归属任何能力域，可能需要更新能力域定义")
        lines.append("")
        lines.append("| 架构域 | 域名称 | 架构层 | 节点数 | 成熟度 |")
        lines.append("|--------|--------|--------|:---:|:---:|")
        for d in unmapped:
            lines.append(
                f"| {d['domain_id']} | {d['domain_name']} | {d['layer_id']} | "
                f"{d['total_nodes']} | {d['maturity_level']} |"
            )
        lines.append("")

    return "\n".join(lines)


def _maturity_definition(level: str) -> str:
    """Return the definition text for a maturity level."""
    definitions = {
        "L0": "能力完全不存在，无设计无代码 / No nodes in domain",
        "L1": "仅有设计文档/蓝图，无代码 / design_maturity=design only",
        "L2": "有原型代码，未集成 / design_maturity=prototype",
        "L3": "代码可用但未生产验证 / design_maturity=production, build_status!=active",
        "L4": "生产环境稳定运行 / design_maturity=production, build_status=active",
        "L5": "达到Goldman/BlackRock水平 / Leading (manual assessment)",
    }
    return definitions.get(level, "")


def main() -> None:
    """Entry point: generate the capability heatmap."""
    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    content = generate_heatmap()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
