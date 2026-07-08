# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §panorama-registry
# [MODULE] scripts.governance.d5_architecture.generators.generate_panorama_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] _shared.constants (get_depgraph_pg_connection, REPO_ROOT); _common (DB_DISPLAY_NAME)
# [CONSUMERS] CI自动触发(GATE-ARCH-DIAGRAM reconciler post-commit);人工查看 00_overview_entry/panorama_registry.md
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph;输出到00_overview_entry/
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph不存在→exit 1
# [TESTS] (待补)
# [TTL] permanent
"""G-panorama-registry: 自动生成全景图清单总表

功能：
  - 从 depgraph (PostgreSQL) 查询已建全景图真源健康度（domains/nodes/edges、dataflow_*、decision_*）
  - 扫描实际产物文件验证已建全景图存在性
  - 硬编码待建全景图清单（PENDING_PANORAMAS 常量）——6 个新目录 08-13 下共 16 项
  - 输出 panorama_registry.md 到 00_overview_entry/

设计要点：
  - 已建清单 BUILT_PANORAMAS：19 项，真源=数据库 + 实际产物扫描
  - 待建清单 PENDING_PANORAMAS：16 项，真源=硬编码常量（用户裁定不建 panorama_registry.yaml）
  - 待建项逐个建设时，再裁定真源类型（DB/YAML），届时从 PENDING 移到 BUILT

触发机制：
  - GATE-ARCH-DIAGRAM reconciler（priority=630）在 post-commit 自动触发
  - 触发条件：commit 了 PG 写入脚本（apply_depgraph.py / apply_dataflowgraph.py /
    apply_decisiongraph.py / sync_yaml_to_depgraph.py 等）或 YAML 真源
    （decision_graph_model.yaml / dataflow_graph_registry.yaml / capability_heatmap.yaml）
  - 与 navigation_index.py 同组，一并重生

用法
----
    python scripts/governance/d5_architecture/generators/generate_panorama_registry.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G-panorama-registry: 自动生成全景图清单总表'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import os
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402
from _common import DB_DISPLAY_NAME  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

BASE_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture"
OUTPUT_DIR = BASE_DIR / "00_overview_entry"
OUTPUT_FILE_NAME = "panorama_registry.md"
GENERATORS_DIR = REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators"


# ============================================================
# 已建全景图清单（BUILT_PANORAMAS）
# 真源：实际项目状态 + generate_navigation_index.py / generate_dataflow_diagram.py 等生成器
# 维护策略：新增已建全景图时，在此添加条目
# source_architecture 字段：标注该全景图来自哪个架构图（depgraph/dataflowgraph/decisiongraph/手工/文件系统扫描）
# ============================================================
BUILT_PANORAMAS: list[dict] = [
    # --- 00_overview_entry/ ---
    {
        "panorama_id": "PAN-BUILT-00a",
        "name": "导航索引（navigation_index）",
        "category": "入口导航",
        "category_id": "overview",
        "data_source": "文件系统扫描",
        "source_architecture": "文件系统扫描",
        "generator": "generate_navigation_index.py",
        "output_path": "00_overview_entry/",
        "artifact_path": "00_overview_entry/navigation_index.md",
        "description": "文档库导航索引，列出 02_enterprise_architecture 下所有文档",
    },
    {
        "panorama_id": "PAN-BUILT-00b",
        "name": "全景图清单总表（本文件）",
        "category": "入口导航",
        "category_id": "overview",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph + dataflowgraph + decisiongraph",
        "generator": "generate_panorama_registry.py",
        "output_path": "00_overview_entry/",
        "artifact_path": "00_overview_entry/panorama_registry.md",
        "description": "全景图清单总表，记录已建/待建全景图状态（本文件自身）",
    },
    # --- 01_global_architecture_diagram/ ---
    {
        "panorama_id": "PAN-BUILT-05",
        "name": "跨域依赖矩阵",
        "category": "依赖关系",
        "category_id": "dependency",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_cross_domain_matrix.py",
        "output_path": "01_global_architecture_diagram/",
        "artifact_path": "01_global_architecture_diagram/cross_domain_matrix.md",
        "description": "域间依赖的详细数据矩阵",
    },
    {
        "panorama_id": "PAN-BUILT-06",
        "name": "集成拓扑图",
        "category": "依赖关系",
        "category_id": "dependency",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_integration_topology.py",
        "output_path": "01_global_architecture_diagram/",
        "artifact_path": "01_global_architecture_diagram/integration_topology.md",
        "description": "43 个域之间怎么互相依赖的集成拓扑图",
    },
    {
        "panorama_id": "PAN-BUILT-08",
        "name": "路径全景（全项目目录树）",
        "category": "路径全景",
        "category_id": "path",
        "data_source": "文件系统扫描",
        "source_architecture": "文件系统扫描",
        "generator": "generate_path_tree.py",
        "output_path": "01_global_architecture_diagram/",
        "artifact_path": "01_global_architecture_diagram/full_project_tree_zh.md",
        "description": "全项目目录树（中英文双语）",
    },
    {
        "panorama_id": "PAN-BUILT-09",
        "name": "能力热力图（53域×10能力）",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_capability_heatmap.py",
        "output_path": "01_global_architecture_diagram/",
        "artifact_path": "01_global_architecture_diagram/global_capability_heatmap.md",
        "description": "53 个域 × 10 个能力维度的热力图",
    },
    {
        "panorama_id": "PAN-BUILT-10",
        "name": "资产清单配置",
        "category": "资产",
        "category_id": "asset",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_asset_catalog.py",
        "output_path": "01_global_architecture_diagram/",
        "artifact_path": "01_global_architecture_diagram/asset_catalog.md",
        "description": f"资产清单（从 {DB_DISPLAY_NAME} 派生，非运行时 CMDB）",
    },
    {
        "panorama_id": "PAN-BUILT-11",
        "name": "契约目录配置",
        "category": "资产",
        "category_id": "asset",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_contract_catalog.py",
        "output_path": "01_global_architecture_diagram/",
        "artifact_path": "01_global_architecture_diagram/contract_catalog.md",
        "description": f"契约目录（从 {DB_DISPLAY_NAME} contracts 表派生）",
    },
    # --- 02_domain_architecture_docs/ ---
    {
        "panorama_id": "PAN-BUILT-20",
        "name": "域架构文档（50 域 + domain_index）",
        "category": "域架构文档",
        "category_id": "domain_docs",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_domain_doc.py",
        "output_path": "02_domain_architecture_docs/",
        "artifact_path": "02_domain_architecture_docs/",
        "description": f"每个功能域一份详细说明书（50 个域文档 + 1 个 domain_index.md），从 {DB_DISPLAY_NAME} nodes/edges 派生",
    },
    # --- 03_governance_reports/ ---
    {
        "panorama_id": "PAN-BUILT-12",
        "name": "容量报告",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_capacity_report.py",
        "output_path": "03_governance_reports/",
        "artifact_path": "03_governance_reports/capacity_report.md",
        "description": "各功能域的模块数量与容量上限对比，识别超容域和接近超容域",
    },
    {
        "panorama_id": "PAN-BUILT-13",
        "name": "约束违规报告",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_constraint_violations.py",
        "output_path": "03_governance_reports/",
        "artifact_path": "03_governance_reports/constraint_violations.md",
        "description": "架构约束违规报告",
    },
    {
        "panorama_id": "PAN-BUILT-14",
        "name": "设计态 vs 运营态",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_design_vs_production.py",
        "output_path": "03_governance_reports/",
        "artifact_path": "03_governance_reports/design_vs_production.md",
        "description": "设计态到运营态的迁移进度对比",
    },
    # --- 04_architecture_principles_decisions/ ---
    {
        "panorama_id": "PAN-BUILT-15",
        "name": "12维架构评分矩阵",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": "手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "04_architecture_principles_decisions/",
        "artifact_path": "04_architecture_principles_decisions/dimension_audit_matrix.md",
        "description": "12 维架构评分矩阵",
    },
    {
        "panorama_id": "PAN-BUILT-17",
        "name": "依赖与路径全景图能力定位书",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": "手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "04_architecture_principles_decisions/",
        "artifact_path": "04_architecture_principles_decisions/dependency_path_panorama.md",
        "description": "依赖与路径全景图能力定位书（双态模型 + SSoT 分层 + 生命周期 + 生成器覆盖矩阵）",
    },
    # --- 05_dataflow_architecture/ ---
    {
        "panorama_id": "PAN-BUILT-18",
        "name": "数据流图（dataflowgraph Dataset/Job/Edge）",
        "category": "数据流",
        "category_id": "dataflow",
        "data_source": DB_DISPLAY_NAME + " (dataflow_* 表)",
        "source_architecture": "dataflowgraph",
        "generator": "generate_dataflow_diagram.py",
        "output_path": "05_dataflow_architecture/",
        "artifact_path": "05_dataflow_architecture/dataflow_index.md",
        "description": "数据流图 dataflowgraph（Dataset/Job/Edge），三图正交第二维度",
    },
    # --- 06_decision_architecture/ ---
    {
        "panorama_id": "PAN-BUILT-19",
        "name": "决策流图（decisiongraph L0-L6 四轨）",
        "category": "决策流",
        "category_id": "decision",
        "data_source": DB_DISPLAY_NAME + " (decision_* 表)",
        "source_architecture": "decisiongraph",
        "generator": "generate_decision_diagram.py",
        "output_path": "06_decision_architecture/",
        "artifact_path": "06_decision_architecture/decision_index.md",
        "description": "决策流图 decisiongraph（L0-L6 四轨），三图正交第三维度",
    },
    # --- generated/ ---
    {
        "panorama_id": "PAN-BUILT-04",
        "name": "模块依赖图（depgraph nodes/edges）",
        "category": "依赖关系",
        "category_id": "dependency",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "generate_domain_dependency_diagram.py",
        "output_path": "generated/domains/",
        "artifact_path": "generated/domains/",
        "description": f"每个功能域一张 .mmd 依赖图，从 {DB_DISPLAY_NAME} nodes/edges 表派生",
    },
    {
        "panorama_id": "PAN-BUILT-07",
        "name": "循环依赖检测（Tarjan SCC）",
        "category": "依赖关系",
        "category_id": "dependency",
        "data_source": DB_DISPLAY_NAME,
        "source_architecture": "depgraph",
        "generator": "内置在生成器（Tarjan SCC）",
        "output_path": "generated/",
        "artifact_path": "generated/panorama_alignment_report.md",
        "description": "内置 Tarjan SCC 算法检测循环依赖，输出循环报告",
    },
    # --- sample/ ---
    {
        "panorama_id": "PAN-BUILT-21",
        "name": "样板/模板区（7 个样板文件）",
        "category": "样板",
        "category_id": "sample",
        "data_source": "手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "sample/",
        "artifact_path": "sample/",
        "description": "给人类写文档时参考的样板（overview_entry_sample / architecture_principles_sample / manual_architecture_views_sample / d_trading_sample / 手工架构图样板 / integration_topology_sample / path_tree_sample）",
    },
    # --- target_architecture/ ---
    {
        "panorama_id": "PAN-BUILT-01",
        "name": "TOGAF 4视图 + 6正交视图",
        "category": "架构视图",
        "category_id": "target_architecture",
        "data_source": "YAML (architecture_model/) + 手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "target_architecture/",
        "artifact_path": "target_architecture/overview.md",
        "description": "TOGAF 业务/信息/应用/技术 4视图 + 安全/集成/运营/治理/前端/运行时平面/能力热力图 6正交视图",
    },
    {
        "panorama_id": "PAN-BUILT-02",
        "name": "C4 L1/L2/L3 架构图",
        "category": "架构视图",
        "category_id": "target_architecture",
        "data_source": "手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "target_architecture/diagrams/",
        "artifact_path": "target_architecture/diagrams/c4_l1_system_context.mmd",
        "description": "C4 模型 L1 系统上下文 / L2 容器 / L3 组件图（d_ex_core / d_mkt_data / d_ml_train）",
    },
    {
        "panorama_id": "PAN-BUILT-03",
        "name": "28个 Mermaid 图（拓扑/时序/数据流）",
        "category": "架构视图",
        "category_id": "target_architecture",
        "data_source": "手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "target_architecture/diagrams/",
        "artifact_path": "target_architecture/diagrams/",
        "description": "拓扑/时序/数据流/部署/激活甘特/三层治理等 28 张 Mermaid 图",
    },
    # --- 02_enterprise_architecture/ 根目录（排在最后） ---
    {
        "panorama_id": "PAN-BUILT-16",
        "name": "架构债务注册表（337项）",
        "category": "治理健康度",
        "category_id": "governance",
        "data_source": "手工",
        "source_architecture": "手工",
        "generator": "(手工维护)",
        "output_path": "02_enterprise_architecture/",
        "artifact_path": "architecture_debt_registry.md",
        "description": "全项目架构债务单一真源，337 个违规点 + 6 个根因",
    },
]


# ============================================================
# 待建全景图清单（PENDING_PANORAMAS）
# 真源：硬编码在此常量（用户裁定不建 panorama_registry.yaml）
# 维护策略：每个全景图实际建设时，逐个裁定真源类型（DB/YAML），并从本清单移到 BUILT_PANORAMAS
# 规划目录：08-13 共 6 个新目录，现在不实际建文件夹，只记录在总表待建清单
# ============================================================
PENDING_PANORAMAS: list[dict] = [
    # ===== 08_asset_panorama 资产全景 =====
    {
        "panorama_id": "PAN-ASSET-01",
        "name": "资产清单 / CMDB",
        "category": "资产全景",
        "category_id": "asset_panorama",
        "plan_folder": "08_asset_panorama/",
        "plan_generator": "generate_asset_panorama.py (待建)",
        "source_architecture": "待裁定（depgraph 扩展 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md",
            "docs/03_modules/_domain_data/data_inventory.md",
        ],
        "data_source_tbd": "待裁定：PostgreSQL 表 asset_registry（运行时服务/数据流/契约总览）vs YAML 静态配置。现有 asset_inventory.yaml 只是配置，不构成全景图",
        "priority": "高",
        "description": "一张图看完所有运行中服务/数据流/契约的总览。量化系统有大量外部数据源/券商接口，资产清单是风险管理基础",
    },
    {
        "panorama_id": "PAN-ASSET-02",
        "name": "API 契约目录",
        "category": "资产全景",
        "category_id": "asset_panorama",
        "plan_folder": "08_asset_panorama/",
        "plan_generator": "generate_api_contract_catalog.py (待建)",
        "source_architecture": "待裁定（depgraph contracts 扩展 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md",
            "docs/03_modules/_domain_integration/blueprint.md",
        ],
        "data_source_tbd": "待裁定：扩展现有 depgraph contracts 表 vs 独立 api_contracts 表。现有 PAN-BUILT-11 契约目录配置只是静态派生，缺版本号/Owner/消费方",
        "priority": "高",
        "description": "面向人类的 API 契约目录全景图（谁提供什么/谁消费什么/版本号/Owner）。量化系统接口众多（行情/交易/风控），契约目录是接入新策略的入口",
    },
    {
        "panorama_id": "PAN-ASSET-03",
        "name": "数据目录 Data Catalog",
        "category": "资产全景",
        "category_id": "asset_panorama",
        "plan_folder": "08_asset_panorama/",
        "plan_generator": "generate_data_catalog.py (待建)",
        "source_architecture": "待裁定（dataflowgraph 扩展 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_data/blueprint.md",
            "docs/03_modules/_domain_data/data_catalog.md",
            "docs/03_modules/_domain_data/data_acquisition_plan.md",
        ],
        "data_source_tbd": "待裁定：扩展现有 dataflow_datasets 表加完整性/延迟/质量字段 vs 独立 data_catalog 表。现有 data_acquisition_plan.md / data_catalog.md 不是从全景图派生",
        "priority": "高",
        "description": "从全景图派生的数据目录，含数据完整性/延迟/质量的实时视图。量化强依赖数据质量，PIT/幸存者偏差/数据缺口必须可视化",
    },
    {
        "panorama_id": "PAN-ASSET-04",
        "name": "数据血缘图 Data Lineage",
        "category": "资产全景",
        "category_id": "asset_panorama",
        "plan_folder": "08_asset_panorama/",
        "plan_generator": "generate_data_lineage.py (待建)",
        "source_architecture": "待裁定（dataflowgraph 字段级扩展 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_data/blueprint.md",
            "docs/03_modules/_cross_layer/database/blueprint.md",
        ],
        "data_source_tbd": "待裁定：扩展 dataflow_edges 表加字段级血缘 vs 独立 column_lineage 表。dataflowgraph 是作业级流图，缺字段级血缘",
        "priority": "高",
        "description": "字段级血缘图（某个因子字段上游来自哪些原始表）。因子可解释性、监管追溯、数据问题定位必备",
    },
    # ===== 09_runtime_panorama 运行时全景 =====
    {
        "panorama_id": "PAN-RUN-01",
        "name": "实时调用链拓扑 + SLO 看板",
        "category": "运行时观测",
        "category_id": "runtime_panorama",
        "plan_folder": "09_runtime_panorama/",
        "plan_generator": "generate_runtime_topology.py (待建)",
        "source_architecture": "待裁定（OpenTelemetry 采集 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md",
            "docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md",
        ],
        "data_source_tbd": "待裁定：OpenTelemetry / Prometheus 采集 vs 独立 runtime_calls 表。有 telemetry 配置但缺实时调用链拓扑/SLO 看板",
        "priority": "中",
        "description": "实时调用链拓扑 + SLO 看板。量化系统盘后/盘中运维刚需",
    },
    {
        "panorama_id": "PAN-RUN-02",
        "name": "告警热力图",
        "category": "运行时观测",
        "category_id": "runtime_panorama",
        "plan_folder": "09_runtime_panorama/",
        "plan_generator": "generate_alert_heatmap.py (待建)",
        "source_architecture": "待裁定（AlertManager API vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md",
        ],
        "data_source_tbd": "待裁定：AlertManager API 实时拉取 vs 独立 alert_history 表",
        "priority": "中",
        "description": "告警热力图，量化系统盘后/盘中运维刚需",
    },
    {
        "panorama_id": "PAN-RUN-03",
        "name": "CI/CD 流水线图",
        "category": "运行时观测",
        "category_id": "runtime_panorama",
        "plan_folder": "09_runtime_panorama/",
        "plan_generator": "generate_cicd_pipeline.py (待建)",
        "source_architecture": "待裁定（GitHub Actions API vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_governance/blueprint.md",
            "docs/03_modules/_cross_layer/pipeline/blueprint.md",
        ],
        "data_source_tbd": "待裁定：GitHub Actions API 拉取 vs 独立 cicd_pipelines 表。有 frontend_build_pipeline.mmd 但缺全项目构建/发布/部署流水线总览",
        "priority": "中",
        "description": "全项目构建/发布/部署流水线总览图",
    },
    {
        "panorama_id": "PAN-RUN-04",
        "name": "服务依赖运行时视图",
        "category": "运行时观测",
        "category_id": "runtime_panorama",
        "plan_folder": "09_runtime_panorama/",
        "plan_generator": "generate_runtime_dependency.py (待建)",
        "source_architecture": "待裁定（OpenTelemetry trace 聚合 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md",
        ],
        "data_source_tbd": "待裁定：OpenTelemetry trace 聚合 vs 独立 runtime_calls 表。现有依赖图是静态 import，缺运行时实际调用频次/延迟/失败率加权",
        "priority": "中",
        "description": "运行时实际调用频次/延迟/失败率加权的动态依赖图",
    },
    # ===== 10_security_panorama 安全全景 =====
    {
        "panorama_id": "PAN-SEC-01",
        "name": "威胁模型图 STRIDE",
        "category": "安全全景",
        "category_id": "security_panorama",
        "plan_folder": "10_security_panorama/",
        "plan_generator": "generate_stride_threat_model.py (待建)",
        "source_architecture": "待裁定（YAML 威胁建模 vs 独立表）",
        "related_blueprints": [
            "docs/02_enterprise_architecture/target_architecture/security_architecture.md",
            "docs/03_modules/_cross_layer/large_language_model_security/blueprint.md",
        ],
        "data_source_tbd": "待裁定：YAML 威胁建模（架构师手工）vs 独立 threat_models 表。有 security_architecture.md 但缺攻击面/信任边界/数据流威胁标注",
        "priority": "中",
        "description": "STRIDE 威胁模型图（攻击面/信任边界/数据流威胁标注）",
    },
    {
        "panorama_id": "PAN-SEC-02",
        "name": "合规矩阵",
        "category": "安全全景",
        "category_id": "security_panorama",
        "plan_folder": "10_security_panorama/",
        "plan_generator": "generate_compliance_matrix.py (待建)",
        "source_architecture": "待裁定（depgraph compliance 扩展 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_compliance/blueprint.md",
        ],
        "data_source_tbd": "待裁定：扩展现有 compliance 域 916 模块元信息 vs 独立 compliance_matrix 表。compliance 域有 916 模块但没规则×系统×状态看板",
        "priority": "中",
        "description": "规则×系统×状态 合规全景看板",
    },
    # ===== 11_risk_panorama 风险全景 =====
    {
        "panorama_id": "PAN-RISK-01",
        "name": "风险敞口全景图",
        "category": "风险全景",
        "category_id": "risk_panorama",
        "plan_folder": "11_risk_panorama/",
        "plan_generator": "generate_risk_exposure.py (待建)",
        "source_architecture": "待裁定（depgraph 域派生 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_risk/blueprint.md",
            "docs/03_modules/_domain_portfolio_core/blueprint.md",
        ],
        "data_source_tbd": "待裁定：从 D_RISK/D_PORTFOLIO 域派生 vs 独立 risk_exposure 表。量化特有：因子暴露/行业暴露/风格暴露/资金使用率，组合层面必须",
        "priority": "高",
        "description": "风险敞口全景图（因子暴露/行业暴露/风格暴露/资金使用率）。量化特有，组合层面必须",
    },
    # ===== 12_quant_panorama 量化全景 =====
    {
        "panorama_id": "PAN-QUANT-01",
        "name": "因子全景图",
        "category": "量化全景",
        "category_id": "quant_panorama",
        "plan_folder": "12_quant_panorama/",
        "plan_generator": "generate_factor_panorama.py (待建)",
        "source_architecture": "待裁定（depgraph 域派生 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_factor/blueprint.md",
        ],
        "data_source_tbd": "待裁定：从 D_FACTOR 域派生 vs 独立 factor_registry 表。D_FACTOR 只有依赖图，缺因子分类树 + 相关性矩阵 + IC 衰减热力图",
        "priority": "可选",
        "description": "因子分类树 + 因子相关性矩阵 + IC 衰减热力图",
    },
    {
        "panorama_id": "PAN-QUANT-02",
        "name": "策略谱系图",
        "category": "量化全景",
        "category_id": "quant_panorama",
        "plan_folder": "12_quant_panorama/",
        "plan_generator": "generate_strategy_lineage.py (待建)",
        "source_architecture": "待裁定（decisiongraph 派生 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_signal/blueprint.md",
            "docs/03_modules/_domain_research/blueprint.md",
        ],
        "data_source_tbd": "待裁定：从 decisiongraph L0-L6 派生 vs 独立 strategy_registry 表。策略→因子→数据的血缘链，目前只在 decisiongraph 里有 L0-L6 链路",
        "priority": "可选",
        "description": "策略→因子→数据 的血缘链",
    },
    {
        "panorama_id": "PAN-QUANT-03",
        "name": "回测对比看板",
        "category": "量化全景",
        "category_id": "quant_panorama",
        "plan_folder": "12_quant_panorama/",
        "plan_generator": "generate_backtest_comparison.py (待建)",
        "source_architecture": "待裁定（depgraph 域派生 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_backtest/blueprint.md",
        ],
        "data_source_tbd": "待裁定：从 D_BACKTEST 域派生 vs 独立 backtest_results 表。多策略回测结果对比（Sharpe/回撤/胜率），目前各回测孤立",
        "priority": "可选",
        "description": "多策略回测结果对比（Sharpe/回撤/胜率）全景",
    },
    {
        "panorama_id": "PAN-QUANT-04",
        "name": "订单生命周期图",
        "category": "量化全景",
        "category_id": "quant_panorama",
        "plan_folder": "12_quant_panorama/",
        "plan_generator": "generate_order_lifecycle.py (待建)",
        "source_architecture": "待裁定（depgraph 域派生 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_execution_core/blueprint.md",
        ],
        "data_source_tbd": "待裁定：从 D_TRADING/D_EX_CORE 派生 vs 独立 order_lifecycle 表。目前只有时序图 seq_order_submit.mmd，缺订单状态机 + 成交分布 + 拒单热力图",
        "priority": "可选",
        "description": "订单状态机 + 成交分布 + 拒单热力图",
    },
    # ===== 13_visualization_architecture 可视化前端架构 =====
    {
        "panorama_id": "PAN-VIS-01",
        "name": "可视化前端架构文档",
        "category": "可视化前端",
        "category_id": "visualization_architecture",
        "plan_folder": "13_visualization_architecture/",
        "plan_generator": "(手工维护 + 部分自动生成)",
        "source_architecture": "待裁定（代码扫描派生 vs 独立表）",
        "related_blueprints": [
            "docs/03_modules/_domain_frontend/blueprint.md",
            "docs/02_enterprise_architecture/target_architecture/frontend_architecture.md",
        ],
        "data_source_tbd": "待裁定：从 src/zephyr/frontend/ 代码扫描派生 vs 独立 frontend_components 表。代码进 src/zephyr/frontend/，文档进 13_visualization_architecture/",
        "priority": "中",
        "description": "可视化前端架构（Panel + HoloViz + Plotly + TradingView Lightweight Charts v5.2）组件拓扑/数据流/部署图。target_architecture/frontend_architecture.md 已有 TOGAF 视图，本目录放更细的可视化前端架构",
    },
]


# ============================================================
# 目录排序键：与目录规划顺序一致
# 顺序：00→01→02_domain→03→04→05→06→generated→sample→target_architecture→08→...→13→根目录
# 根目录文件（02_enterprise_architecture/xxx.md）排在最后
# ============================================================
_DIRECTORY_ORDER: list[str] = [
    "00_overview_entry",
    "01_global_architecture_diagram",
    "02_domain_architecture_docs",
    "03_governance_reports",
    "04_architecture_principles_decisions",
    "05_dataflow_architecture",
    "06_decision_architecture",
    "generated",
    "sample",
    "target_architecture",
    "08_asset_panorama",
    "09_runtime_panorama",
    "10_security_panorama",
    "11_risk_panorama",
    "12_quant_panorama",
    "13_visualization_architecture",
    "02_enterprise_architecture",  # 根目录文件排在最后
]
_DIR_ORDER_INDEX: dict[str, int] = {d: i for i, d in enumerate(_DIRECTORY_ORDER)}


def _directory_sort_key(dir_prefix: str) -> tuple[int, str]:
    """返回排序键 (order_index, dir_prefix)，未登记的目录排最后。"""
    return (_DIR_ORDER_INDEX.get(dir_prefix, 999), dir_prefix)


def _get_directory_prefix(item: dict) -> str:
    """从 item 提取目录前缀。"""
    if item.get("build_status") == "✅已建":
        op = item.get("output_path", "")
    else:
        op = item.get("plan_folder", "")
    if "/" in op:
        return op.split("/")[0]
    return op.rstrip("/")


# ============================================================
# DB 真源表清单（用于 DB 健康度验证）
# 每张表附 description 备注，说明该表与同组其他表的区别
# ============================================================
DB_TABLE_GROUPS: list[dict] = [
    {
        "group": "depgraph",
        "label": "依赖图 depgraph",
        "tables": [
            # 备注中的 {count} 占位符在生成时由 _generate_stats_section 用本表实时行数替换，
            # 避免硬编码数字与行数列漂移（原 nodes=4986/edges=5946 等写死值与行数列不一致）
            ("domains", "功能域清单——{count} 个域的 ID/名称/层级/容量上限等元信息（L0/L1/L2 分层）"),
            ("nodes", "模块节点——每个 .py/.yaml/.md 文件作为一个节点（module_id/path/build_status/design_maturity），{count} 个"),
            ("edges", "依赖边——节点间的依赖关系（import/契约/事件订阅），{count} 条"),
        ],
    },
    {
        "group": "dataflow",
        "label": "数据流图 dataflowgraph",
        "tables": [
            ("dataflow_datasets", "数据集——数据流转的「货物」（如 market_data.tick / factor.value_factor），含 scope/domain/pit_policy"),
            ("dataflow_jobs", "作业——处理数据的「加工者」（如 ingest.ifind_kline / compute.value_factor），含 trigger_type/run_context"),
            ("dataflow_edges", "数据流边——Job 产出/消费 Dataset 的关系（produces / consumed by），{count} 条"),
        ],
    },
    {
        "group": "decision",
        "label": "决策流图 decisiongraph",
        "tables": [
            ("decision_tracks", "决策轨——{count} 条正交决策轨（价值/动量/风险/组合），优先级+激活条件"),
            # decision_layers 行数=层数（10），原备注里的 214 是跨表引用 decision_nodes 行数，
            # 跨表引用易漂移且与行数列重复，改为不带数字的描述（节点数见 decision_nodes 行数列）
            ("decision_layers", "决策层——L0-L6 七层决策链（如 L0 信号源 / L3 组合优化 / L6 执行），承载决策节点的分层归属"),
            ("decision_nodes", "决策节点——每层内的具体决策点（如因子合成/风险检查/订单生成），含 path/module_id/evidence_hash"),
            ("decision_edges", "决策边——节点间的决策传递关系（L0→L1→...→L6 链路），{count} 条"),
        ],
    },
]


def _fetch_db_stats(conn: PgConnExecuteWrapper) -> dict:
    """从 depgraph (PostgreSQL) 获取各表统计。

    Returns:
        dict: {table_name: count_or_error_str}
    """
    stats: dict[str, object] = {}
    for group in DB_TABLE_GROUPS:
        for table, _desc in group["tables"]:
            try:
                cur = conn.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
                row = cur.fetchone()
                stats[table] = row["cnt"] if row else 0
            except Exception as e:
                stats[table] = f"❌({type(e).__name__})"
    return stats


def _check_artifact(artifact_path: str) -> tuple[str, int]:
    """检查产物存在性，返回 (状态, 数量)。

    Args:
        artifact_path: 相对 BASE_DIR 的路径

    Returns:
        (status, count)
        status: "✅存在" / "❌缺失"
        count: 文件数（目录）或 1（文件）或 0（缺失）
    """
    full_path = BASE_DIR / artifact_path
    if not full_path.exists():
        return ("❌缺失", 0)
    if full_path.is_file():
        return ("✅存在", 1)
    # 目录：统计非隐藏文件数
    files = [f for f in full_path.iterdir() if f.is_file() and not f.name.startswith(".")]
    return ("✅存在", len(files))


def _generate_stats_section(built: list[dict], pending: list[dict], db_stats: dict) -> list[str]:
    """生成统计概览章节。"""
    lines = []
    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 维度 | 值 |")
    lines.append("|------|:---:|")
    lines.append(f"| 已建全景图总数 | {len(built)} |")
    lines.append(f"| 待建全景图总数 | {len(pending)} |")
    lines.append(f"| 全景图总数 | {len(built) + len(pending)} |")
    lines.append(f"| 已建覆盖率 | {len(built) / (len(built) + len(pending)) * 100:.1f}% |")
    lines.append("")

    # 产物存在性统计
    ok_count = sum(1 for p in built if _check_artifact(p["artifact_path"])[0] == "✅存在")
    lines.append(f"| 已建产物存在 | {ok_count}/{len(built)} |")
    lines.append("")

    # DB 真源健康度
    lines.append("### 数据库真源健康度")
    lines.append("")
    lines.append(f"> 数据源：{DB_DISPLAY_NAME}")
    lines.append("")
    lines.append("| 表组 | 表名 | 行数 | 备注（各表区别） |")
    lines.append("|------|------|-----:|------|")
    for group in DB_TABLE_GROUPS:
        for table, desc in group["tables"]:
            count = db_stats.get(table, "?")
            # 将备注中的 {count} 占位符替换为本表实时行数，根治硬编码数字与行数列漂移
            desc_filled = desc.replace("{count}", str(count))
            lines.append(f"| {group['label']} | `{table}` | {count} | {desc_filled} |")
    lines.append("")
    return lines


def _generate_built_section(built: list[dict]) -> list[str]:
    """生成已建全景图清单章节。"""
    lines = []
    lines.append("## 已建全景图清单")
    lines.append("")
    lines.append(f"> 共 {len(built)} 项已建全景图。状态由生成器扫描实际产物文件自动验证。")
    lines.append(">")
    lines.append("> 排序：按输出目录顺序（00→01→02→...→target_architecture）。")
    lines.append("")

    # 按目录规划顺序排序（00→01→...→06→generated→target_architecture）
    # 用 _directory_sort_key 取代纯字符串排序，确保与目录规划顺序一致
    def _built_sort_key(p: dict) -> tuple[int, str]:
        op = p["output_path"]
        prefix = op.split("/")[0] if "/" in op else op
        return _directory_sort_key(prefix)

    sorted_built = sorted(built, key=_built_sort_key)

    lines.append("| ID | 名称 | 类别 | 来自架构图 | 真源 | 生成器 | 输出路径 | 产物状态 |")
    lines.append("|------|------|------|------|------|--------|----------|:---:|")
    for p in sorted_built:
        status, count = _check_artifact(p["artifact_path"])
        # 目录类产物追加文件数
        status_str = status
        if status == "✅存在" and count > 1:
            status_str = f"✅存在({count}文件)"

        # 输出路径改为可点击链接：
        # - 目录类产物（count > 1，如 generated/domains/ 50 个 .mmd）→ 普通文本
        # - 单文件产物 → 相对路径可点击跳转链接（兼容 DOC-REF-BROKEN 门禁，绝对路径 file:// 被该门禁当相对路径解析会误判为断链）
        output_path = p["output_path"]
        artifact_path = p["artifact_path"]
        if status == "✅存在" and count <= 1:
            # 单文件 → 可点击链接（相对路径，兼容 DOC-REF-BROKEN 门禁的相对路径解析）
            full_path = BASE_DIR / artifact_path
            link_text = output_path.rstrip("/") if output_path.endswith("/") else output_path
            rel_path = os.path.relpath(full_path, OUTPUT_DIR).replace("\\", "/")
            output_cell = f"[`{link_text}`]({rel_path})"
        else:
            # 目录类（多文件）或缺失 → 普通文本
            output_cell = f"`{output_path}`"

        lines.append(
            f"| {p['panorama_id']} | {p['name']} | {p['category']} | {p.get('source_architecture', '—')} | "
            f"{p['data_source']} | `{p['generator']}` | {output_cell} | {status_str} |"
        )
    lines.append("")
    return lines


def _generate_pending_section(pending: list[dict]) -> list[str]:
    """生成待建全景图清单章节。"""
    lines = []
    lines.append("## 待建全景图清单")
    lines.append("")
    lines.append(f"> 共 {len(pending)} 项待建全景图，分布在 6 个新目录（08-13）。")
    lines.append(">")
    lines.append("> **重要说明**：")
    lines.append("> - 真源类型（DB/YAML）逐个建设时再裁定，记录在 `data_source_tbd` 字段")
    lines.append("> - 规划目录（08-13）现在不实际建文件夹，只记录在此清单")
    lines.append("> - 每个全景图实际建设时，从本清单移到已建清单")
    lines.append("")

    # 按优先级分组
    priority_order = {"高": 0, "中": 1, "可选": 2}
    sorted_pending = sorted(pending, key=lambda x: priority_order.get(x["priority"], 99))

    lines.append("| ID | 名称 | 类别 | 规划目录 | 规划生成器 | 优先级 | 真源待裁定 |")
    lines.append("|------|------|------|----------|------------|:---:|------|")
    for p in sorted_pending:
        # 真源待裁定字段过长，截断显示
        dsb = p["data_source_tbd"]
        if len(dsb) > 60:
            dsb = dsb[:57] + "..."
        lines.append(
            f"| {p['panorama_id']} | {p['name']} | {p['category']} | `{p['plan_folder']}` | "
            f"`{p['plan_generator']}` | {p['priority']} | {dsb} |"
        )
    lines.append("")
    return lines


def _generate_detail_section(built: list[dict], pending: list[dict]) -> list[str]:
    """生成详细内容清单章节（按目录顺序分组，每组用表格，含统计表）。"""
    lines = []
    lines.append("## 详细内容清单")
    lines.append("")
    lines.append("> 按输出目录顺序排列。已建项标注真源/生成器/产物路径；待建项标注规划目录/优先级/真源待裁定。")
    lines.append("")

    # 合并已建和待建
    all_items = []
    for p in built:
        all_items.append({**p, "build_status": "✅已建"})
    for p in pending:
        all_items.append({**p, "build_status": "⏳待建"})

    # ===== 前置统计表：各架构图生成全景图数量 =====
    lines.append("### 架构图生成统计")
    lines.append("")
    lines.append("> 每个架构图各生成了多少个全景图（可视化产物）。")
    lines.append("")

    # 统计各 source_architecture 的数量
    arch_counts: dict[str, int] = {}
    for item in all_items:
        arch = item.get("source_architecture", "—")
        arch_counts[arch] = arch_counts.get(arch, 0) + 1

    # 按数量降序排序
    sorted_arches = sorted(arch_counts.items(), key=lambda x: (-x[1], x[0]))

    lines.append("| 架构图来源 | 全景图数量 | 说明 |")
    lines.append("|------|:---:|------|")
    arch_desc = {
        "depgraph": "依赖图——模块节点和依赖边，生成域文档/矩阵/拓扑/热力图/容量/违规等",
        "dataflowgraph": "数据流图——Dataset/Job/Edge，生成数据流图",
        "decisiongraph": "决策流图——L0-L6 四轨，生成决策流图",
        "手工": "人工维护的架构文档，无自动生成器",
        "文件系统扫描": "扫描实际文件系统派生，无 DB 真源",
        "depgraph + dataflowgraph + decisiongraph": "综合三个架构图派生（如本总表）",
    }
    for arch, count in sorted_arches:
        desc = arch_desc.get(arch, "待裁定真源类型")
        lines.append(f"| {arch} | {count} | {desc} |")
    lines.append(f"| **合计** | **{len(all_items)}** | 已建 {len(built)} + 待建 {len(pending)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ===== 按目录顺序分组的详细表格 =====
    # 按目录规划顺序排序（使用 _directory_sort_key）
    sorted_items = sorted(all_items, key=lambda item: _directory_sort_key(_get_directory_prefix(item)))

    # 按目录前缀分组（保持排序顺序）
    groups: dict[str, list[dict]] = {}
    group_order: list[str] = []
    for item in sorted_items:
        key = _get_directory_prefix(item)
        if key not in groups:
            groups[key] = []
            group_order.append(key)
        groups[key].append(item)

    # 类别中文名映射（按目录前缀）
    dir_name_zh = {
        "00_overview_entry": "00 入口导航",
        "01_global_architecture_diagram": "01 全局架构图",
        "02_domain_architecture_docs": "02 域架构文档",
        "02_enterprise_architecture": "根目录（架构债务注册表）",
        "03_governance_reports": "03 治理报告",
        "04_architecture_principles_decisions": "04 架构原则与决策",
        "05_dataflow_architecture": "05 数据流架构",
        "06_decision_architecture": "06 决策流架构",
        "generated": "generated 自动生成中间产物",
        "sample": "sample 样板/模板区",
        "target_architecture": "target_architecture TOGAF 目标架构",
        "08_asset_panorama": "08 资产全景（待建）",
        "09_runtime_panorama": "09 运行时全景（待建）",
        "10_security_panorama": "10 安全全景（待建）",
        "11_risk_panorama": "11 风险全景（待建）",
        "12_quant_panorama": "12 量化全景（待建）",
        "13_visualization_architecture": "13 可视化前端架构（待建）",
    }

    for key in group_order:
        items = groups[key]
        title = dir_name_zh.get(key, key)
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |")
        lines.append("|------|------|:---:|------|------|------|")
        for item in items:
            if item["build_status"] == "✅已建":
                # 已建项：真源列显示真源名 + 生成器跳转链接 + 产物跳转链接
                gen_name = item['generator']
                # 生成器做成跳转链接（如果存在）
                gen_path = GENERATORS_DIR / gen_name
                if gen_path.exists():
                    gen_rel = os.path.relpath(gen_path, OUTPUT_DIR).replace("\\", "/")
                    gen_cell = f"[`{gen_name}`]({gen_rel})"
                else:
                    gen_cell = f"`{gen_name}`"
                # 产物路径做成跳转链接（单文件跳转，目录不跳转）
                art_path = item.get("artifact_path", "")
                art_full = BASE_DIR / art_path
                if art_full.exists() and art_full.is_file():
                    art_rel = os.path.relpath(art_full, OUTPUT_DIR).replace("\\", "/")
                    art_cell = f"[`{art_path}`]({art_rel})"
                else:
                    art_cell = f"`{art_path}`"
                source_info = f"真源：{item['data_source']}<br>生成器：{gen_cell}<br>产物：{art_cell}"
            else:
                source_info = f"规划目录：`{item['plan_folder']}`<br>生成器：`{item['plan_generator']}`<br>真源待裁定：{item['data_source_tbd']}"
                # 追加相关蓝图跳转链接
                related_bps = item.get("related_blueprints", [])
                if related_bps:
                    bp_links = []
                    for bp_path in related_bps:
                        bp_full = REPO_ROOT / bp_path
                        bp_name = bp_path.split("/")[-1]  # 取文件名作为显示文本
                        bp_rel = os.path.relpath(bp_full, OUTPUT_DIR).replace("\\", "/")
                        bp_links.append(f"[`{bp_name}`]({bp_rel})")
                    source_info += f"<br>相关蓝图：{' / '.join(bp_links)}"
            lines.append(
                f"| {item['panorama_id']} | {item['name']} | {item['build_status']} | "
                f"{item.get('source_architecture', '—')} | "
                f"{item['description']} | {source_info} |"
            )
        lines.append("")
    return lines


def _generate_directory_plan_section() -> list[str]:
    """生成目录规划章节。"""
    lines = []
    lines.append("## 目录规划")
    lines.append("")
    lines.append("| 目录 | 用途 | 状态 |")
    lines.append("|------|------|:---:|")
    lines.append("| `00_overview_entry/` | 入口导航（含本总表 + navigation_index） | ✅ |")
    lines.append("| `01_global_architecture_diagram/` | 全局视图（路径树/矩阵/拓扑/热力图/资产/契约） | ✅ |")
    lines.append("| `02_domain_architecture_docs/` | 每个功能域的详细文档（50 域 + domain_index） | ✅ |")
    lines.append("| `03_governance_reports/` | 治理报告（容量/违规/设计态） | ✅ |")
    lines.append("| `04_architecture_principles_decisions/` | 架构原则和决策依据 | ✅ |")
    lines.append("| `05_dataflow_architecture/` | 数据流架构（dataflowgraph） | ✅ |")
    lines.append("| `06_decision_architecture/` | 决策流架构（decisiongraph） | ✅ |")
    lines.append("| `generated/` | 自动生成中间产物（域依赖图/对齐报告） | ✅ |")
    lines.append("| `sample/` | 样板/模板区（7 个样板文件） | ✅ |")
    lines.append("| `target_architecture/` | TOGAF 目标架构视图集 | ✅ |")
    lines.append("| `02_enterprise_architecture/`（根目录） | 架构债务注册表（根目录文件） | ✅ |")
    lines.append("| `08_asset_panorama/` | 资产/契约/数据目录/数据血缘（待建） | ⏳ |")
    lines.append("| `09_runtime_panorama/` | 运行时调用链/SLO/告警/CI-CD/服务依赖（待建） | ⏳ |")
    lines.append("| `10_security_panorama/` | STRIDE 威胁模型/合规矩阵（待建） | ⏳ |")
    lines.append("| `11_risk_panorama/` | 风险敞口全景图（待建） | ⏳ |")
    lines.append("| `12_quant_panorama/` | 因子/策略/回测/订单（待建） | ⏳ |")
    lines.append("| `13_visualization_architecture/` | 可视化前端架构（待建） | ⏳ |")
    lines.append("")
    lines.append("> **可视化前端架构归属说明**：")
    lines.append("> - 代码进 `src/zephyr/frontend/`（已存在）")
    lines.append("> - 文档进 `13_visualization_architecture/`（待建）")
    lines.append("> - `target_architecture/frontend_architecture.md` 是 TOGAF 视图集的一部分，保持不动")
    lines.append("")
    return lines


def generate_panorama_registry(db_stats: dict) -> str:
    """生成全景图清单总表。

    Args:
        db_stats: 数据库统计字典

    Returns:
        Markdown 内容字符串
    """
    lines = []
    lines.append("# 全景图清单总表 / Panorama Registry")
    lines.append("")
    lines.append("> 这是你查看 ZephyrAlpha 全景图体系的入口。从这里能看到应该有哪些全景图、哪些已建、哪些未建。")
    lines.append(">")
    lines.append("> **自动生成**：本文件由 `generate_panorama_registry.py` 自动生成。date: auto-generated，最后更新以 git log 为准")
    lines.append(f"> **已建真源**：{DB_DISPLAY_NAME} + 实际产物文件扫描")
    lines.append("> **待建真源**：硬编码在生成器代码内的 `PENDING_PANORAMAS` 常量（用户裁定不建 panorama_registry.yaml）")
    lines.append(">")
    lines.append("> **维护策略**：")
    lines.append("> - 已建全景图新增时，在生成器代码 `BUILT_PANORAMAS` 常量添加条目")
    lines.append("> - 待建全景图实际建设时，逐个裁定真源类型（DB/YAML），从 `PENDING_PANORAMAS` 移到 `BUILT_PANORAMAS`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 各章节
    lines.extend(_generate_stats_section(BUILT_PANORAMAS, PENDING_PANORAMAS, db_stats))
    lines.append("---")
    lines.append("")
    lines.extend(_generate_directory_plan_section())
    lines.append("---")
    lines.append("")
    lines.extend(_generate_built_section(BUILT_PANORAMAS))
    lines.append("---")
    lines.append("")
    lines.extend(_generate_pending_section(PENDING_PANORAMAS))
    lines.append("---")
    lines.append("")
    lines.extend(_generate_detail_section(BUILT_PANORAMAS, PENDING_PANORAMAS))

    # 修订记录
    lines.append("---")
    lines.append("")
    lines.append("## 修订记录")
    lines.append("")
    lines.append("| 日期 | 说明 |")
    lines.append("|------|------|")
    lines.append(f"| auto-generated | 自动生成 |")

    return "\n".join(lines)


def main() -> None:
    """入口：生成全景图清单总表。"""
    parser = argparse.ArgumentParser(description="G-panorama-registry: 自动生成全景图清单总表")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--output-name", type=str, default=OUTPUT_FILE_NAME, help="输出文件名")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取数据库统计
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            db_stats = _fetch_db_stats(conn)
        finally:
            conn.close()
    except Exception as e:
        print(f"[ERROR] 无法连接 {DB_DISPLAY_NAME}：{e}", file=sys.stderr)
        db_stats = {table: "❌(DB不可达)" for group in DB_TABLE_GROUPS for table in group["tables"]}

    # 生成总表
    content = generate_panorama_registry(db_stats)
    out_path = output_dir / args.output_name
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
