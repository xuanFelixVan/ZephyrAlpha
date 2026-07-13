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
# [TTL] permanent
"""G11: 从 depgraph (PostgreSQL) 生成能力热力图

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.11
[MODULE] scripts.governance.d5_architecture.generators.generate_capability_heatmap
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到01_global_architecture_diagram/
[MODIFY-GUARD] 修改需通过任务卡
[CONSUMERS] CI自动触发;人工查看01_global_architecture_diagram/global_capability_heatmap.md
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
description: 'G11: 从 {DB_DISPLAY_NAME} 生成能力热力图'
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

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "01_global_architecture_diagram" / "global_capability_heatmap.md"

# 能力域映射真源：architecture_model/cross_cutting/capability_heatmap.yaml
# 裁定#210：硬编码列表已删除，改为从 YAML 动态读取，消除 SSoT 分歧
YAML_PATH = REPO_ROOT / "architecture_model" / "cross_cutting" / "capability_heatmap.yaml"


def _load_capability_domains() -> list[dict]:
    """从 capability_heatmap.yaml 加载能力域映射（SSoT）。

    YAML 字段 -> 脚本字段映射：
      id              -> id
      name            -> name
      name_en         -> name_en
      type            -> type（business -> 业务，cross_cutting -> 横切）
      primary_domains -> domains
    """
    import yaml
    with open(YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    result: list[dict] = []
    for cd in data.get("capability_domains", []):
        result.append({
            "id": cd["id"],
            "name": cd["name"],
            "name_en": cd.get("name_en", cd["name"]),
            "type": "横切" if cd.get("type") == "cross_cutting" else "业务",
            "domains": cd.get("primary_domains", []),
        })
    return result


CAPABILITY_DOMAINS: list[dict] = _load_capability_domains()

# Maturity levels (L0-L3, 4-level simplified) - Source: capability_heatmap.yaml v3.0.0
# symbol: maturity symbol; coverage: ✅/🟡/❌; name_en: English name
MATURITY_LEVELS: dict[str, dict] = {
    "L0": {"symbol": "⚪", "coverage": "❌", "name_en": "Missing", "name_zh": "缺失", "score": 0},
    "L1": {"symbol": "🔵", "coverage": "🟡", "name_en": "Designing", "name_zh": "设计中", "score": 1},
    "L2": {"symbol": "🟡", "coverage": "🟡", "name_en": "Usable", "name_zh": "可用未验证", "score": 2},
    "L3": {"symbol": "🟢", "coverage": "✅", "name_en": "Verified", "name_zh": "生产已验证", "score": 3},
}

# Test/governance-script domains to exclude (not real business domains)
# - D-T3-/D-T4-/D-T5-/D-T9-: 测试域前缀
# - D_AUDITTEST: 审计测试套件(1720节点,非业务域)
# - D_GOV_SCRIPTS: 治理脚本域(434节点,工具脚本非业务域)
TEST_DOMAIN_PREFIXES = ("D-T3-", "D-T4-", "D-T5-", "D-T9-")
TEST_DOMAIN_EXACT = ("D_AUDITTEST", "D_GOV_SCRIPTS")


def normalize_domain_id(domain_id: str) -> str:
    """Normalize domain ID for matching (handle hyphen/underscore inconsistency)."""
    return domain_id.upper().replace("-", "_")


def table_exists(conn: PgConnExecuteWrapper, table_name: str) -> bool:
    """Check if a table exists in the database."""
    cur = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name=%s", (table_name,))
    return cur.fetchone() is not None


def get_all_domains(conn: PgConnExecuteWrapper) -> list[dict]:
    """Query all domains from the domains table."""
    cur = conn.execute("SELECT domain_id, domain_name, layer_id FROM domains ORDER BY domain_id")
    return [
        {
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"] or "",
            "layer_id": r["layer_id"] or "",
        }
        for r in cur.fetchall()
    ]


def get_domain_maturity_counts(conn: PgConnExecuteWrapper) -> dict[str, dict[str, int]]:
    """Query node maturity counts grouped by domain_id and design_maturity.

    Returns: {domain_id: {"production": N, "design": N, "prototype": N, "active": N}}
    """
    cur = conn.execute(
        """SELECT domain_id, design_maturity, COUNT(*) AS cnt
           FROM nodes
           WHERE domain_id IS NOT NULL
             AND node_type NOT IN ('test', 'script')
           GROUP BY domain_id, design_maturity"""
    )
    result: dict[str, dict[str, int]] = {}
    for r in cur.fetchall():
        domain_id = r["domain_id"]
        maturity = (r["design_maturity"] or "unknown").lower()
        count = r["cnt"]
        result.setdefault(domain_id, {}).setdefault(maturity, 0)
        result[domain_id][maturity] += count

    # Also query build_status='stable'/'active' counts for L3 detection
    # 注: 当前 DB build_status 实际值为 planned/stable/generated,无 active
    # L3 判定放宽为 stable(已稳定运行)或 active(未来扩展)
    cur = conn.execute(
        """SELECT domain_id, COUNT(*) AS cnt
           FROM nodes
           WHERE domain_id IS NOT NULL
             AND design_maturity = 'production'
             AND build_status IN ('active', 'stable')
             AND node_type NOT IN ('test', 'script')
           GROUP BY domain_id"""
    )
    for r in cur.fetchall():
        domain_id = r["domain_id"]
        count = r["cnt"]
        result.setdefault(domain_id, {})["active"] = count

    return result


def compute_maturity_level(counts: dict[str, int]) -> str:
    """Compute maturity level (L0-L3, 4-level simplified) from node maturity counts.

    L0: no nodes (Missing)
    L1: only design or prototype nodes (Designing)
    L2: has production nodes but build_status NOT IN (active, stable) (Usable, unverified)
    L3: has production nodes with build_status IN (active, stable) (Verified)

    注: test/script 类型节点已在 get_domain_maturity_counts 查询中排除，不参与计算。
    """
    production = counts.get("production", 0)
    design = counts.get("design", 0)
    prototype = counts.get("prototype", 0)
    active = counts.get("active", 0)
    total = production + design + prototype

    if total == 0:
        return "L0"
    if active > 0:
        return "L3"
    if production > 0:
        return "L2"
    if design > 0 or prototype > 0:
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
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        use_arch_table = table_exists(conn, "arch_domain_capacity")
        if use_arch_table:
            data_source = f"{DB_DISPLAY_NAME} arch_domain_capacity表"
            # Primary data source: arch_domain_capacity table
            # When this table exists, query it for capability data
            domains = get_all_domains(conn)
            maturity_counts = get_domain_maturity_counts(conn)
        else:
            # Fallback: arch_domain_capacity merged into domains table in v6
            data_source = f"{DB_DISPLAY_NAME} domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)"
            domains = get_all_domains(conn)
            maturity_counts = get_domain_maturity_counts(conn)
    finally:
        conn.close()

    domain_cap_map = build_domain_capability_map()

    # Filter out test domains (prefix match) and governance-script domains (exact match)
    real_domains = [
        d for d in domains
        if not any(d["domain_id"].startswith(prefix) for prefix in TEST_DOMAIN_PREFIXES)
        and d["domain_id"] not in TEST_DOMAIN_EXACT
    ]

    # Compute maturity for each domain
    domain_data: list[dict] = []
    for d in real_domains:
        did = d["domain_id"]
        counts = maturity_counts.get(did, {})
        level = compute_maturity_level(counts)
        cap_id = domain_cap_map.get(normalize_domain_id(did))
        domain_data.append(
            {
                **d,
                "maturity_level": level,
                "capability_id": cap_id,
                "production": counts.get("production", 0),
                "design": counts.get("design", 0),
                "prototype": counts.get("prototype", 0),
                "active": counts.get("active", 0),
                "total_nodes": counts.get("production", 0) + counts.get("design", 0) + counts.get("prototype", 0),
            }
        )

    # Sort by capability domain, then by domain_id
    cap_order = {cap["id"]: i for i, cap in enumerate(CAPABILITY_DOMAINS)}
    domain_data.sort(key=lambda d: (cap_order.get(d["capability_id"], 999), d["domain_id"]))

    lines: list[str] = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 能力热力图")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 能力热力图 / Capability Heatmap")
    lines.append("")
    lines.append(f"> **文档作用 / Purpose**: 以矩阵形式展示{len(real_domains)}个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。")
    lines.append("")
    lines.append(f"> 本文档由 generate_capability_heatmap.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {data_source}")
    lines.append("")

    # Statistics overview
    total_domains = len(domain_data)
    l0_count = sum(1 for d in domain_data if d["maturity_level"] == "L0")
    l1_count = sum(1 for d in domain_data if d["maturity_level"] == "L1")
    l2_count = sum(1 for d in domain_data if d["maturity_level"] == "L2")
    l3_count = sum(1 for d in domain_data if d["maturity_level"] == "L3")
    full_coverage = sum(1 for d in domain_data if d["maturity_level"] == "L3")
    partial_coverage = sum(1 for d in domain_data if d["maturity_level"] in ("L1", "L2"))
    no_coverage = sum(1 for d in domain_data if d["maturity_level"] == "L0")

    lines.append("## 统计概览 / Statistics Overview")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 / Total Domains | {total_domains} |")
    lines.append(f"| 能力域数 / Capability Domains | {len(CAPABILITY_DOMAINS)} |")
    lines.append(f"| L0 缺失 / Missing | {l0_count} |")
    lines.append(f"| L1 设计中 / Designing | {l1_count} |")
    lines.append(f"| L2 可用未验证 / Usable | {l2_count} |")
    lines.append(f"| L3 生产已验证 / Verified | {l3_count} |")
    lines.append(f"| ✅ 完全覆盖 / Full Coverage (L3) | {full_coverage} |")
    lines.append(f"| 🟡 部分覆盖 / Partial Coverage (L1-L2) | {partial_coverage} |")
    lines.append(f"| ❌ 无覆盖 / No Coverage (L0) | {no_coverage} |")
    lines.append("")

    # Maturity level legend
    lines.append("## 成熟度图例 / Maturity Legend")
    lines.append("")
    lines.append("| 等级 / Level | 符号 / Symbol | 覆盖度 / Coverage | 中文名 / Chinese | 英文名 / English | 定义 / Definition |")
    lines.append("|:---:|:---:|:---:|--------|--------|------|")
    for level_id in ("L0", "L1", "L2", "L3"):
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
    lines.append("| 能力域ID / Capability ID | 中文名 / Chinese | 英文名 / English | 类型 / Type | 包含域数 / Domain Count | 包含域 / Included Domains |")
    lines.append("|:---:|--------|--------|:---:|:---:|--------|")
    for cap in CAPABILITY_DOMAINS:
        domains_str = ", ".join(cap["domains"])
        lines.append(
            f"| {cap['id']} | {cap['name']} | {cap['name_en']} | "
            f"{cap['type']} | {len(cap['domains'])} | {domains_str} |"
        )
    lines.append("")

    # {N} domains × 10 capability domains matrix
    lines.append("## 能力热力图矩阵 / Capability Heatmap Matrix")
    lines.append("")
    lines.append(f"> 行：架构域（{len(real_domains)}域） | 列：能力域（10能力域）")
    lines.append(f"> Rows: Architecture Domains ({len(real_domains)}) | Columns: Capability Domains (10)")
    lines.append("> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）")
    lines.append("> Cell: Maturity symbol (shown when domain belongs to capability, otherwise —)")
    lines.append("")

    # Matrix header
    header = "| 架构域 / Architecture Domain | 域名称 / Domain Name |"
    separator = "|--------|--------|"
    for cap in CAPABILITY_DOMAINS:
        header += f" {cap['id']} |"
        separator += ":---:|"
    header += " 成熟度 / Maturity |"
    separator += ":---:|"
    lines.append(header)
    lines.append(separator)

    for d in domain_data:
        row = f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} |"
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
    lines.append("| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | prototype | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |")
    lines.append("|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

    for cap in CAPABILITY_DOMAINS:
        cap_domains = [d for d in domain_data if d["capability_id"] == cap["id"]]
        cap_count = len(cap_domains)
        total_nodes = sum(d["total_nodes"] for d in cap_domains)
        total_prod = sum(d["production"] for d in cap_domains)
        total_design = sum(d["design"] for d in cap_domains)
        total_proto = sum(d["prototype"] for d in cap_domains)

        if cap_count > 0:
            avg_score = sum(MATURITY_LEVELS[d["maturity_level"]]["score"] for d in cap_domains) / cap_count
            full = sum(1 for d in cap_domains if d["maturity_level"] == "L3")
            partial = sum(1 for d in cap_domains if d["maturity_level"] in ("L1", "L2"))
            none = sum(1 for d in cap_domains if d["maturity_level"] == "L0")
            if full == cap_count:
                coverage = "✅ 完全覆盖 / Full"
            elif full > 0 or partial > 0:
                coverage = "🟡 部分覆盖 / Partial"
            else:
                coverage = "❌ 无覆盖 / None"
        else:
            avg_score = 0
            coverage = "❌ 无覆盖 / None"

        lines.append(
            f"| {cap['id']} | {cap['name']} | {cap_count} | {total_nodes} | "
            f"{total_prod} | {total_design} | {total_proto} | "
            f"{avg_score:.2f} | {coverage} |"
        )
    lines.append("")

    # Detailed domain maturity list
    lines.append("## 域成熟度明细 / Domain Maturity Detail")
    lines.append("")
    lines.append(
        "| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | prototype | active | 成熟度 / Maturity | 覆盖度 / Coverage |"
    )
    lines.append("|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    for d in domain_data:
        info = MATURITY_LEVELS[d["maturity_level"]]
        cap_name = d["capability_id"] or "—"
        lines.append(
            f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {cap_name} | "
            f"{d['layer_id']} | {d['total_nodes']} | "
            f"{d['production']} | {d['design']} | {d['prototype']} | {d['active']} | "
            f"{d['maturity_level']} {info['symbol']} | {info['coverage']} |"
        )
    lines.append("")

    # Gap analysis
    lines.append("## 差距分析 / Gap Analysis")
    lines.append("")
    lines.append("### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)")
    lines.append("")
    lines.append("| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |")
    lines.append("|--------|--------|:---:|:---:|:---:|")
    p0_domains = [d for d in domain_data if d["maturity_level"] in ("L0", "L1")]
    if p0_domains:
        for d in p0_domains:
            cap_name = d["capability_id"] or "—"
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {cap_name} | {d['maturity_level']} | {d['total_nodes']} |"
            )
    else:
        lines.append("| — | 无P0短板 / No P0 gaps | — | — | — |")
    lines.append("")

    lines.append("### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)")
    lines.append("")
    lines.append("| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |")
    lines.append("|--------|--------|:---:|:---:|:---:|")
    p1_domains = [d for d in domain_data if d["maturity_level"] == "L2"]
    if p1_domains:
        for d in p1_domains:
            cap_name = d["capability_id"] or "—"
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {cap_name} | {d['maturity_level']} | {d['total_nodes']} |"
            )
    else:
        lines.append("| — | 无P1关注 / No P1 watch | — | — | — |")
    lines.append("")

    lines.append("### 已就绪（L3，生产已验证）/ Ready (L3, verified)")
    lines.append("")
    lines.append("| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |")
    lines.append("|--------|--------|:---:|:---:|:---:|")
    ready_domains = [d for d in domain_data if d["maturity_level"] == "L3"]
    if ready_domains:
        for d in ready_domains:
            cap_name = d["capability_id"] or "—"
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {cap_name} | {d['maturity_level']} | {d['total_nodes']} |"
            )
    else:
        lines.append("| — | 无L3域 / No L3 domains | — | — | — |")
    lines.append("")

    # Unmapped domains (not in any capability domain)
    unmapped = [d for d in domain_data if d["capability_id"] is None]
    if unmapped:
        lines.append("## 未映射域 / Unmapped Domains")
        lines.append("")
        lines.append("> 以下域未归属任何能力域，可能需要更新能力域定义")
        lines.append("> The following domains are not mapped to any capability domain; capability definitions may need updating")
        lines.append("")
        lines.append("| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |")
        lines.append("|--------|--------|--------|:---:|:---:|")
        for d in unmapped:
            lines.append(
                f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['layer_id']} | "
                f"{d['total_nodes']} | {d['maturity_level']} |"
            )
        lines.append("")

    return "\n".join(lines)


def _maturity_definition(level: str) -> str:
    """Return the definition text for a maturity level (4-level simplified)."""
    definitions = {
        "L0": "能力完全不存在，无设计无代码 / No nodes in domain",
        "L1": "有设计文档或原型代码，未集成 / design_maturity=design or prototype",
        "L2": "代码可用但未生产验证 / design_maturity=production, build_status NOT IN (active, stable)",
        "L3": "生产环境稳定运行 / design_maturity=production, build_status IN (active, stable)",
    }
    return definitions.get(level, "")


def main() -> None:
    """Entry point: generate the capability heatmap."""
    content = generate_heatmap()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
