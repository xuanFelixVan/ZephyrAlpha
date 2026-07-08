# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_asset_catalog
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths; _common; _shared.constants.get_depgraph_pg_connection
# [CONSUMERS] 人工查看01_global_architecture_diagram/asset_catalog.md
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等;只读depgraph (PostgreSQL);输出到01_global_architecture_diagram/
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
# [TESTS]
# [TTL] permanent
"""G13: 从 depgraph (PostgreSQL) 生成资产清单全景图

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.13
[MODULE] scripts.governance.d5_architecture.generators.generate_asset_catalog
[INVARIANTS] 输出幂等;只读depgraph (PostgreSQL);输出到01_global_architecture_diagram/
[CONSUMERS] 人工查看01_global_architecture_diagram/asset_catalog.md
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _common import DB_DISPLAY_NAME
from _shared.constants import get_depgraph_pg_connection
from zephyr.shared.io.paths import REPO_ROOT

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "01_global_architecture_diagram" / "asset_catalog.md"


def generate_asset_catalog() -> str:
    """生成资产清单全景图 markdown。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        # 查询各类资产
        # 1. 数据源资产
        cur = conn.execute("""
            SELECT source_id, name, name_en, type, category, vendor, status, coverage, api_count
            FROM data_source_assets ORDER BY type, category, source_id
        """)
        data_sources = [dict(r) for r in cur.fetchall()]

        # 2. 服务资产
        cur = conn.execute("""
            SELECT service_id, name, type, domain, port, host, protocol, status, description
            FROM service_assets ORDER BY type, service_id
        """)
        services = [dict(r) for r in cur.fetchall()]

        # 3. 配置项资产
        cur = conn.execute("""
            SELECT file_path, file_name, size_bytes, last_modified
            FROM config_assets ORDER BY file_path
        """)
        configs = [dict(r) for r in cur.fetchall()]

        # 4. 基础设施组件
        cur = conn.execute("""
            SELECT component_id, component_type, address, status, sla
            FROM infrastructure_components ORDER BY component_id
        """)
        infra = [dict(r) for r in cur.fetchall()]

        # 5. 契约资产
        cur = conn.execute("""
            SELECT contract_id, name, provider_domain, contract_type, fulfillment_status
            FROM contracts ORDER BY contract_type, contract_id
        """)
        contracts = [dict(r) for r in cur.fetchall()]

        # 6. 数据流作业
        cur = conn.execute("SELECT COUNT(*) AS c FROM dataflow_jobs")
        dataflow_jobs = cur.fetchone()["c"]
        cur = conn.execute("SELECT COUNT(*) AS c FROM dataflow_datasets")
        dataflow_datasets = cur.fetchone()["c"]

        # 7. 数据源 API 清单（join data_source_assets 取源名）
        cur = conn.execute("""
            SELECT a.api_id, a.source_id, s.name AS source_name,
                   a.category, a.api_name, a.short_name, a.function_desc,
                   a.params, a.returns_format, a.frequency_codes, a.data_scope,
                   a.test_status, a.test_result, a.section_ref, a.notes
            FROM data_source_apis a
            LEFT JOIN data_source_assets s ON a.source_id = s.source_id
            ORDER BY a.source_id, a.api_id
        """)
        apis = [dict(r) for r in cur.fetchall()]

    finally:
        conn.close()

    total = len(data_sources) + len(services) + len(configs) + len(infra) + len(contracts) + len(apis)

    lines: list[str] = []
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 资产清单全景图")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 资产清单全景图 / Asset Catalog")
    lines.append("")
    lines.append(f"> **文档作用 / Purpose**: 一张图看完所有运行中服务/数据流/契约/数据源/数据源 API/配置的总览,共{total}项资产。AI接入新功能前必查此图确认可复用资产。")
    lines.append("")
    lines.append(f"> 本文档由 generate_asset_catalog.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 真源: data_sources_registry.yaml + data_source_apis_registry.yaml + service_registry.yaml + config/*.yaml + cross_layer_contracts.yaml")
    lines.append("")

    # 统计概览
    lines.append("## 1. 统计概览")
    lines.append("")
    lines.append("| 资产类型 | 数量 | 真源 |")
    lines.append("|----------|------|------|")
    lines.append(f"| 外部数据源 | {len(data_sources)} | data_sources_registry.yaml |")
    lines.append(f"| 数据源 API | {len(apis)} | data_source_apis_registry.yaml |")
    lines.append(f"| 服务资产 | {len(services)} | service_registry.yaml |")
    lines.append(f"| 基础设施组件 | {len(infra)} | infrastructure_components.yaml |")
    lines.append(f"| 契约资产 | {len(contracts)} | cross_layer_contracts.yaml |")
    lines.append(f"| 配置项 | {len(configs)} | config/*.yaml |")
    lines.append(f"| 数据流作业 | {dataflow_jobs} | dataflow_graph_registry.yaml |")
    lines.append(f"| 数据集 | {dataflow_datasets} | dataflow_graph_registry.yaml |")
    lines.append(f"| **合计** | **{total}** | |")
    lines.append("")

    # 数据源资产
    lines.append("## 2. 外部数据源资产")
    lines.append("")
    lines.append("| ID | 名称 | 类型 | 类别 | 供应商 | 状态 | API数 | 覆盖范围 |")
    lines.append("|----|------|------|------|--------|------|-------|----------|")
    for ds in data_sources:
        lines.append(f"| {ds['source_id']} | {ds['name']} | {ds['type']} | {ds['category']} | {ds['vendor']} | {ds['status']} | {ds['api_count']} | {ds['coverage'] or '—'} |")
    lines.append("")

    # 服务资产
    lines.append("## 3. 服务资产")
    lines.append("")
    lines.append("| ID | 名称 | 类型 | 域 | 端口 | 协议 | 状态 | 描述 |")
    lines.append("|----|------|------|-----|------|------|------|------|")
    for svc in services:
        port = str(svc['port']) if svc['port'] else '—'
        lines.append(f"| {svc['service_id']} | {svc['name']} | {svc['type']} | {svc['domain'] or '—'} | {port} | {svc['protocol'] or '—'} | {svc['status']} | {svc['description'] or '—'} |")
    lines.append("")

    # 基础设施组件
    lines.append("## 4. 基础设施组件")
    lines.append("")
    lines.append("| ID | 类型 | 地址 | 状态 | SLA |")
    lines.append("|----|------|------|------|-----|")
    for ic in infra:
        lines.append(f"| {ic['component_id']} | {ic['component_type']} | {ic['address'] or '—'} | {ic['status']} | {ic['sla'] or '—'} |")
    lines.append("")

    # 契约资产
    lines.append("## 5. 契约资产")
    lines.append("")
    lines.append(f"> 详细流向矩阵和字段定义见 [contract_catalog.md](contract_catalog.md)")
    lines.append("")
    lines.append("| ID | 名称 | 类型 | 提供方 | 状态 |")
    lines.append("|----|------|------|--------|------|")
    for c in contracts:
        lines.append(f"| {c['contract_id']} | {c['name'] or '—'} | {c['contract_type']} | {c['provider_domain'] or '—'} | {c['fulfillment_status']} |")
    lines.append("")

    # 配置项
    lines.append("## 6. 配置项清单(元数据)")
    lines.append("")
    lines.append("> 仅记录元数据(文件名/大小/修改时间),不复制内容。内容真源为 config/*.yaml 文件本身。")
    lines.append("")
    lines.append("| 文件路径 | 大小(KB) | 最后修改 |")
    lines.append("|----------|---------|----------|")
    for cfg in configs:
        size_kb = f"{cfg['size_bytes'] / 1024:.1f}" if cfg['size_bytes'] else '—'
        lm = cfg['last_modified'].strftime('%Y-%m-%d') if cfg['last_modified'] else '—'
        lines.append(f"| `{cfg['file_path']}` | {size_kb} | {lm} |")
    lines.append("")

    # 数据源 API 清单（按数据源分组，每个 API 一行）
    lines.append("## 7. 数据源 API 清单")
    lines.append("")
    lines.append(f"> 共 {len(apis)} 个 API,按数据源分组。真源: `architecture_model/data/data_source_apis_registry.yaml`,参数坑/调用示例见 [data_source_operation_manual.md](../../03_modules/_domain_data/data_source_operation_manual.md)。")
    lines.append("")
    lines.append("**测试状态图例**: ✅ verified | 🟡 partial | ⚠️ untested | ❌ deprecated")
    lines.append("")

    # 按数据源分组
    apis_by_source: dict[str, list[dict]] = {}
    for api in apis:
        apis_by_source.setdefault(api["source_id"], []).append(api)

    for idx, (source_id, source_apis) in enumerate(apis_by_source.items(), start=1):
        source_name = source_apis[0]["source_name"] or source_id
        verified_count = sum(1 for a in source_apis if a["test_status"] == "verified")
        deprecated_count = sum(1 for a in source_apis if a["test_status"] == "deprecated")
        untested_count = sum(1 for a in source_apis if a["test_status"] == "untested")
        partial_count = sum(1 for a in source_apis if a["test_status"] == "partial")

        lines.append(f"### 7.{idx} {source_name}（`{source_id}`，{len(source_apis)} API）")
        lines.append("")
        lines.append(f"测试状态: ✅ {verified_count} verified / 🟡 {partial_count} partial / ⚠️ {untested_count} untested / ❌ {deprecated_count} deprecated")
        lines.append("")
        lines.append("| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |")
        lines.append("|--------|--------|------|------|------|------|:----:|----------|")

        status_symbol = {
            "verified": "✅",
            "partial": "🟡",
            "untested": "⚠️",
            "deprecated": "❌",
        }
        for a in source_apis:
            sym = status_symbol.get(a["test_status"], "—")
            api_name = a["api_name"] or "—"
            category = a["category"] or "—"
            func = a["function_desc"] or "—"
            freq = a["frequency_codes"] or "—"
            scope = a["data_scope"] or "—"
            section_ref = a["section_ref"] or "—"
            lines.append(f"| `{a['api_id']}` | `{api_name}` | {category} | {func} | {freq} | {scope} | {sym} | {section_ref} |")

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    content = generate_asset_catalog()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
