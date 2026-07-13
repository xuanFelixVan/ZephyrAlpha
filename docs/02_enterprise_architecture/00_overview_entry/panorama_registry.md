# 全景图清单总表 / Panorama Registry

> 这是你查看 ZephyrAlpha 全景图体系的入口。从这里能看到应该有哪些全景图、哪些已建、哪些未建。
>
> **自动生成**：本文件由 `generate_panorama_registry.py` 自动生成。date: auto-generated，最后更新以 git log 为准
> **已建真源**：depgraph (PostgreSQL) + 实际产物文件扫描
> **待建真源**：硬编码在生成器代码内的 `PENDING_PANORAMAS` 常量（用户裁定不建 panorama_registry.yaml）
>
> **维护策略**：
> - 已建全景图新增时，在生成器代码 `BUILT_PANORAMAS` 常量添加条目
> - 待建全景图实际建设时，逐个裁定真源类型（DB/YAML），从 `PENDING_PANORAMAS` 移到 `BUILT_PANORAMAS`

---

## 统计概览

| 维度 | 值 |
|------|:---:|
| 已建全景图总数 | 22 |
| 待建全景图总数 | 16 |
| 全景图总数 | 38 |
| 已建覆盖率 | 57.9% |

| 已建产物存在 | 22/22 |

### 数据库真源健康度

> 数据源：depgraph (PostgreSQL)

| 表组 | 表名 | 行数 | 备注（各表区别） |
|------|------|-----:|------|
| 依赖图 depgraph | `domains` | 63 | 功能域清单——63 个域的 ID/名称/层级/容量上限等元信息（L0/L1/L2 分层） |
| 依赖图 depgraph | `nodes` | 5009 | 模块节点——每个 .py/.yaml/.md 文件作为一个节点（module_id/path/build_status/design_maturity），5009 个 |
| 依赖图 depgraph | `edges` | 5805 | 依赖边——节点间的依赖关系（import/契约/事件订阅），5805 条 |
| 数据流图 dataflowgraph | `dataflow_datasets` | 14 | 数据集——数据流转的「货物」（如 market_data.tick / factor.value_factor），含 scope/domain/pit_policy |
| 数据流图 dataflowgraph | `dataflow_jobs` | 182 | 作业——处理数据的「加工者」（如 ingest.ifind_kline / compute.value_factor），含 trigger_type/run_context |
| 数据流图 dataflowgraph | `dataflow_edges` | 28 | 数据流边——Job 产出/消费 Dataset 的关系（produces / consumed by），28 条 |
| 数据流图 dataflowgraph | `dataflow_datasets_metadata` | 0 | Dataset 扩展属性——physical_type/pit_policy/contract_ref，0 行（0=未填，AI 查 dataflow 会幻觉物理类型） |
| 数据流图 dataflowgraph | `dataflow_jobs_metadata` | 0 | Job 扩展属性——source_code_ref/trigger_type/run_context，0 行（0=未填，AI 查 job 找不到源码） |
| 数据流图 dataflowgraph | `dataflow_runs` | 0 | 运行记录——job 执行历史（status/耗时/参数），0 行（0=无运行时观测，依赖观测系统回填） |
| 决策流图 decisiongraph | `decision_tracks` | 5 | 决策轨——5 条正交决策轨（价值/动量/风险/组合），优先级+激活条件 |
| 决策流图 decisiongraph | `decision_layers` | 179 | 决策层——L0-L6 七层决策链（如 L0 信号源 / L3 组合优化 / L6 执行），承载决策节点的分层归属 |
| 决策流图 decisiongraph | `decision_nodes` | 214 | 决策节点——每层内的具体决策点（如因子合成/风险检查/订单生成），含 path/module_id/evidence_hash |
| 决策流图 decisiongraph | `decision_edges` | 213 | 决策边——节点间的决策传递关系（L0→L1→...→L6 链路），213 条 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `contracts` | 65 | 跨层契约——P0/P1 契约的 ID/提供方/消费方/字段定义，真源 cross_layer_contracts.yaml，65 条 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `data_source_apis` | 124 | 数据源 API 清单——外部数据源的 API 函数/参数/测试状态，真源 data_source_apis_registry.yaml，124 个 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `data_source_assets` | 12 | 外部数据源——行情/交易/风控等外部数据源资产，真源 data_sources_registry.yaml，12 个 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `service_assets` | 10 | 服务资产——内部服务 ID/端口/协议/状态，真源 service_registry.yaml，10 个 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `config_assets` | 33 | 配置项元数据——config/*.yaml 文件名/大小/修改时间（内容真源为文件系统，非 YAML 单文件），33 项 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `infrastructure_components` | 14 | 基础设施组件——基础服务地址/健康检查/SLA，真源 infrastructure_registry.yaml，14 个 |
| 资产配置 assets（YAML→DB 同步，DB 为只读缓存） | `interface_contracts` | 5 | 接口级契约——模块对外 API（函数名/参数签名/返回值/消费方），5 行（仅 5=大部分模块接口未登记，AI 会幻觉函数名） |

---

## 目录规划

| 目录 | 用途 | 状态 |
|------|------|:---:|
| `00_overview_entry/` | 入口导航（含本总表 + navigation_index） | ✅ |
| `01_global_architecture_diagram/` | 全局视图（路径树/矩阵/拓扑/热力图/资产/契约） | ✅ |
| `02_domain_architecture_docs/` | 每个功能域的详细文档（50 域 + domain_index） | ✅ |
| `03_governance_reports/` | 治理报告（容量/违规/设计态） | ✅ |
| `04_architecture_principles_decisions/` | 架构原则和决策依据 | ✅ |
| `05_dataflow_architecture/` | 数据流架构（dataflowgraph） | ✅ |
| `06_decision_architecture/` | 决策流架构（decisiongraph） | ✅ |
| `generated/` | 自动生成中间产物（域依赖图/对齐报告） | ✅ |
| `sample/` | 样板/模板区（7 个样板文件） | ✅ |
| `target_architecture/` | TOGAF 目标架构视图集 | ✅ |
| `02_enterprise_architecture/`（根目录） | 架构债务注册表（根目录文件） | ✅ |
| `08_asset_panorama/` | 资产/契约/数据目录/数据血缘（待建） | ⏳ |
| `09_runtime_panorama/` | 运行时调用链/SLO/告警/CI-CD/服务依赖（待建） | ⏳ |
| `10_security_panorama/` | STRIDE 威胁模型/合规矩阵（待建） | ⏳ |
| `11_risk_panorama/` | 风险敞口全景图（待建） | ⏳ |
| `12_quant_panorama/` | 因子/策略/回测/订单（待建） | ⏳ |
| `13_visualization_architecture/` | 可视化前端架构（待建） | ⏳ |

> **可视化前端架构归属说明**：
> - 代码进 `src/zephyr/frontend/`（已存在）
> - 文档进 `13_visualization_architecture/`（待建）
> - `target_architecture/frontend_architecture.md` 是 TOGAF 视图集的一部分，保持不动

---

## 已建全景图清单

> 共 22 项已建全景图。状态由生成器扫描实际产物文件自动验证。
>
> 排序：按输出目录顺序（00→01→02→...→target_architecture）。

| ID | 名称 | 类别 | 来自架构图 | 真源 | 生成器 | 输出路径 | 产物状态 |
|------|------|------|------|------|--------|----------|:---:|
| PAN-BUILT-00a | 导航索引（navigation_index） | 入口导航 | 文件系统扫描 | 文件系统扫描 | `generate_navigation_index.py` | [`00_overview_entry`](navigation_index.md) | ✅存在 |
| PAN-BUILT-00b | 全景图清单总表（本文件） | 入口导航 | depgraph + dataflowgraph + decisiongraph | depgraph (PostgreSQL) | `generate_panorama_registry.py` | [`00_overview_entry`](panorama_registry.md) | ✅存在 |
| PAN-BUILT-05 | 跨域依赖矩阵 | 依赖关系 | depgraph | depgraph (PostgreSQL) | `generate_cross_domain_matrix.py` | [`01_global_architecture_diagram`](../01_global_architecture_diagram/cross_domain_matrix.md) | ✅存在 |
| PAN-BUILT-06 | 集成拓扑图 | 依赖关系 | depgraph | depgraph (PostgreSQL) | `generate_integration_topology.py` | [`01_global_architecture_diagram`](../01_global_architecture_diagram/integration_topology.md) | ✅存在 |
| PAN-BUILT-08 | 路径全景（全项目目录树） | 路径全景 | 文件系统扫描 | 文件系统扫描 | `generate_path_tree.py` | [`01_global_architecture_diagram`](../01_global_architecture_diagram/full_project_tree_zh.md) | ✅存在 |
| PAN-BUILT-09 | 能力热力图（53域×10能力） | 治理健康度 | depgraph | depgraph (PostgreSQL) | `generate_capability_heatmap.py` | [`01_global_architecture_diagram`](../01_global_architecture_diagram/global_capability_heatmap.md) | ✅存在 |
| PAN-BUILT-10 | 资产清单配置 | 资产 | depgraph | depgraph (PostgreSQL) | `generate_asset_catalog.py` | [`01_global_architecture_diagram`](../01_global_architecture_diagram/asset_catalog.md) | ✅存在 |
| PAN-BUILT-11 | 契约目录配置 | 资产 | depgraph | depgraph (PostgreSQL) | `generate_contract_catalog.py` | [`01_global_architecture_diagram`](../01_global_architecture_diagram/contract_catalog.md) | ✅存在 |
| PAN-BUILT-20 | 域架构文档（50 域 + domain_index） | 域架构文档 | depgraph | depgraph (PostgreSQL) | `generate_domain_doc.py` | `02_domain_architecture_docs/` | ✅存在(64文件) |
| PAN-BUILT-12 | 容量报告 | 治理健康度 | depgraph | depgraph (PostgreSQL) | `generate_capacity_report.py` | [`03_governance_reports`](../03_governance_reports/capacity_report.md) | ✅存在 |
| PAN-BUILT-13 | 约束违规报告 | 治理健康度 | depgraph | depgraph (PostgreSQL) | `generate_constraint_violations.py` | [`03_governance_reports`](../03_governance_reports/constraint_violations.md) | ✅存在 |
| PAN-BUILT-14 | 设计态 vs 运营态 | 治理健康度 | depgraph | depgraph (PostgreSQL) | `generate_design_vs_production.py` | [`03_governance_reports`](../03_governance_reports/design_vs_production.md) | ✅存在 |
| PAN-BUILT-17 | 依赖与路径全景图能力定位书 | 治理健康度 | 手工 | 手工 | `(手工维护)` | [`04_architecture_principles_decisions`](../04_architecture_principles_decisions/dependency_path_panorama.md) | ✅存在 |
| PAN-BUILT-18 | 数据流图（dataflowgraph Dataset/Job/Edge） | 数据流 | dataflowgraph | depgraph (PostgreSQL) (dataflow_* 表) | `generate_dataflow_diagram.py` | [`05_dataflow_architecture`](../05_dataflow_architecture/dataflow_index.md) | ✅存在 |
| PAN-BUILT-19 | 决策流图（decisiongraph L0-L6 四轨） | 决策流 | decisiongraph | depgraph (PostgreSQL) (decision_* 表) | `generate_decision_diagram.py` | [`06_decision_architecture`](../06_decision_architecture/decision_index.md) | ✅存在 |
| PAN-BUILT-04 | 模块依赖图（depgraph nodes/edges） | 依赖关系 | depgraph | depgraph (PostgreSQL) | `generate_domain_dependency_diagram.py` | `generated/domains/` | ✅存在(63文件) |
| PAN-BUILT-07 | 循环依赖检测（Tarjan SCC） | 依赖关系 | depgraph | depgraph (PostgreSQL) | `内置在生成器（Tarjan SCC）` | [`generated`](../generated/panorama_alignment_report.md) | ✅存在 |
| PAN-BUILT-21 | 样板/模板区（7 个样板文件） | 样板 | 手工 | 手工 | `(手工维护)` | `sample/` | ✅存在(7文件) |
| PAN-BUILT-01 | TOGAF 4视图 + 6正交视图 | 架构视图 | 手工 | YAML (architecture_model/) + 手工 | `(手工维护)` | [`target_architecture`](../target_architecture/overview.md) | ✅存在 |
| PAN-BUILT-02 | C4 L1/L2/L3 架构图 | 架构视图 | 手工 | 手工 | `(手工维护)` | [`target_architecture/diagrams`](../target_architecture/diagrams/c4_l1_system_context.mmd) | ✅存在 |
| PAN-BUILT-03 | 28个 Mermaid 图（拓扑/时序/数据流） | 架构视图 | 手工 | 手工 | `(手工维护)` | `target_architecture/diagrams/` | ✅存在(29文件) |
| PAN-BUILT-16 | 架构债务注册表（337项） | 治理健康度 | 手工 | 手工 | `(手工维护)` | [`02_enterprise_architecture`](../architecture_debt_registry.md) | ✅存在 |

---

## 待建全景图清单

> 共 16 项待建全景图，分布在 6 个新目录（08-13）。
>
> **重要说明**：
> - 真源类型（DB/YAML）逐个建设时再裁定，记录在 `data_source_tbd` 字段
> - 规划目录（08-13）现在不实际建文件夹，只记录在此清单
> - 每个全景图实际建设时，从本清单移到已建清单

| ID | 名称 | 类别 | 规划目录 | 规划生成器 | 优先级 | 真源待裁定 |
|------|------|------|----------|------------|:---:|------|
| PAN-ASSET-01 | 资产清单 / CMDB | 资产全景 | `08_asset_panorama/` | `generate_asset_panorama.py (待建)` | 高 | 待裁定：PostgreSQL 表 asset_registry（运行时服务/数据流/契约总览）vs YAML 静态... |
| PAN-ASSET-02 | API 契约目录 | 资产全景 | `08_asset_panorama/` | `generate_api_contract_catalog.py (待建)` | 高 | 待裁定：扩展现有 depgraph contracts 表 vs 独立 api_contracts 表。现有 PA... |
| PAN-ASSET-03 | 数据目录 Data Catalog | 资产全景 | `08_asset_panorama/` | `generate_data_catalog.py (待建)` | 高 | 待裁定：扩展现有 dataflow_datasets 表加完整性/延迟/质量字段 vs 独立 data_catal... |
| PAN-ASSET-04 | 数据血缘图 Data Lineage | 资产全景 | `08_asset_panorama/` | `generate_data_lineage.py (待建)` | 高 | 待裁定：扩展 dataflow_edges 表加字段级血缘 vs 独立 column_lineage 表。data... |
| PAN-RISK-01 | 风险敞口全景图 | 风险全景 | `11_risk_panorama/` | `generate_risk_exposure.py (待建)` | 高 | 待裁定：从 D_RISK/D_PORTFOLIO 域派生 vs 独立 risk_exposure 表。量化特有：因... |
| PAN-RUN-01 | 实时调用链拓扑 + SLO 看板 | 运行时观测 | `09_runtime_panorama/` | `generate_runtime_topology.py (待建)` | 中 | 待裁定：OpenTelemetry / Prometheus 采集 vs 独立 runtime_calls 表。有... |
| PAN-RUN-02 | 告警热力图 | 运行时观测 | `09_runtime_panorama/` | `generate_alert_heatmap.py (待建)` | 中 | 待裁定：AlertManager API 实时拉取 vs 独立 alert_history 表 |
| PAN-RUN-03 | CI/CD 流水线图 | 运行时观测 | `09_runtime_panorama/` | `generate_cicd_pipeline.py (待建)` | 中 | 待裁定：GitHub Actions API 拉取 vs 独立 cicd_pipelines 表。有 fronte... |
| PAN-RUN-04 | 服务依赖运行时视图 | 运行时观测 | `09_runtime_panorama/` | `generate_runtime_dependency.py (待建)` | 中 | 待裁定：OpenTelemetry trace 聚合 vs 独立 runtime_calls 表。现有依赖图是静态... |
| PAN-SEC-01 | 威胁模型图 STRIDE | 安全全景 | `10_security_panorama/` | `generate_stride_threat_model.py (待建)` | 中 | 待裁定：YAML 威胁建模（架构师手工）vs 独立 threat_models 表。有 security_arch... |
| PAN-SEC-02 | 合规矩阵 | 安全全景 | `10_security_panorama/` | `generate_compliance_matrix.py (待建)` | 中 | 待裁定：扩展现有 compliance 域 916 模块元信息 vs 独立 compliance_matrix 表... |
| PAN-VIS-01 | 可视化前端架构文档 | 可视化前端 | `13_visualization_architecture/` | `(手工维护 + 部分自动生成)` | 中 | 待裁定：从 src/zephyr/frontend/ 代码扫描派生 vs 独立 frontend_componen... |
| PAN-QUANT-01 | 因子全景图 | 量化全景 | `12_quant_panorama/` | `generate_factor_panorama.py (待建)` | 可选 | 待裁定：从 D_FACTOR 域派生 vs 独立 factor_registry 表。D_FACTOR 只有依赖图... |
| PAN-QUANT-02 | 策略谱系图 | 量化全景 | `12_quant_panorama/` | `generate_strategy_lineage.py (待建)` | 可选 | 待裁定：从 decisiongraph L0-L6 派生 vs 独立 strategy_registry 表。策略... |
| PAN-QUANT-03 | 回测对比看板 | 量化全景 | `12_quant_panorama/` | `generate_backtest_comparison.py (待建)` | 可选 | 待裁定：从 D_BACKTEST 域派生 vs 独立 backtest_results 表。多策略回测结果对比（S... |
| PAN-QUANT-04 | 订单生命周期图 | 量化全景 | `12_quant_panorama/` | `generate_order_lifecycle.py (待建)` | 可选 | 待裁定：从 D_TRADING/D_EX_CORE 派生 vs 独立 order_lifecycle 表。目前只有... |

---

## 表级缺口清单

> 共 10 项表级缺口。与上方 16 项待建全景图区分：全景图是最终产物，表级缺口是底层 DB 真源的实际状态。
>
> **两类缺口的区别**：
> - 待建全景图（16 项）= 最终要给 AI/人看的产物目录，真源类型待裁定
> - 表级缺口（10 项）= 底层 DB 表的真实状态（空表/部分缺失/完全缺失/数据污染/字段值缺失），真源类型已确定
> - 一个表级缺口对应一个待建全景图（见 panorama_ref 列），但反过来不一定

| 缺口ID | 表名 | 状态 | 实际行数 | 应有行数 | 缺什么 | AI 风险 | 怎么修 | 优先级 | 真源形式 | 对应全景图 |
|------|------|:---:|:---:|------|------|------|------|:---:|------|------|
| GAP-TBL-01 | `dataflow_datasets_metadata` | 空表待填 | 0 | 14 行（每个 dataset 一行扩展属性） | Dataset 的 physical_type / pit_policy / contract_ref 未填 | AI 查 dataflow 只能看到空壳名字，会幻觉编造物理类型（误把 ClickHouse 表当 PostgreSQL） | 从 YAML 真源同步设计态扩展属性 | P0 必做 | YAML 真源 + DB 缓存 | PAN-ASSET-03 |
| GAP-TBL-02 | `dataflow_jobs_metadata` | 空表待填 | 0 | 13 行（每个 job 一行扩展属性） | Job 的 source_code_ref / trigger_type / run_context 未填 | AI 查 job 找不到源码文件，不知道怎么触发（定时/事件/手动），改代码会找错文件 | 从代码扫描派生（解析每个 job 的源码文件和触发配置） | P0 必做 | 代码扫描派生 + DB 缓存 | PAN-ASSET-03 |
| GAP-TBL-07 | `nodes (build_status 字段)` | 字段值缺失 | 0 | 应有 active 值（production 节点且实际运行中） | build_status 字段只有 planned/stable/generated 三种值，0 个 active。能力热力图算法 require build_status='active' 才判 L3，导致 L3 永远无法触发 | AI 看能力热力图会误判所有域最多 L2（可用未验证），无法区分「已上线验证」和「有代码但没跑过」，决策施工优先级时误判 | 1. 修 generate_capability_heatmap.py 算法：build_status='stable' 也算 L3；2. 排除 D_AUDITTEST/D_GOV_SCRIPTS 等测试/脚本域；3. 补 build_status 字段值 | P0 必做 | DB 直写（数据修复）+ 生成器算法修复 | PAN-BUILT-09 |
| GAP-TBL-08 | `decision_edges` | 空表待填 | 213 | 200+ 行（214 个 decision_nodes 之间的决策传递边） | decision_nodes 有 214 个节点，但 decision_edges=0。同步脚本只同步了节点，没有同步边。历史曾有 213 条边，现已被清空（数据丢失或重建时遗漏） | AI 写新策略时看决策链路只有孤立节点，看不到 L0→L1→...→L6 的流向，无法判断策略在决策链中的位置和上下游依赖 | 从 decision_graph_model.yaml 的 §edges 段重新同步边到 decision_edges 表 | P0 必做 | YAML 真源 + DB 缓存 | PAN-BUILT-19 |
| GAP-TBL-09 | `contracts` | 数据污染 | 65 | 30-40 行（真正的 P0/P1 契约，真源 cross_layer_contracts.yaml） | DB contracts 表 294 条是从代码注释正则提取的占位符（schema_definition 只有 description 壳子，promise/actual_consumer/gap/last_reviewed 全 None，fulfillment_status 全 unresolved，contract_type 全 'C'）。真正的契约在 cross_layer_contracts.yaml 里（CTR-001~006 + CTR-ERR + CTR-BP + P1×15 等），未同步到 DB | AI 查 contracts 表会看到 294 条垃圾数据，误以为是真契约，基于占位符做决策（幻觉根源）。真正的契约在 YAML 里 AI 不知道去查 | 1. 清空 contracts 表的占位符数据；2. 从 cross_layer_contracts.yaml 重新同步真契约到 contracts 表 | P0 必做 | YAML 真源 + DB 缓存 | PAN-ASSET-02 |
| GAP-TBL-04 | `interface_contracts` | 部分缺失 | 5 | 50+ 行（每个暴露接口的模块一行） | 50 个域只登记了 5 个模块接口（MOD-DATA/BACKTEST/TRADING/GOVERNANCE/INF-012B） | AI 调用别的模块时不知道暴露什么函数/参数签名，会瞎编函数名和参数 | 从代码扫描补全 exposed_interfaces / consumed_by_modules | P1 应做 | YAML 真源 + DB 缓存 | PAN-ASSET-02 |
| GAP-TBL-10 | `domains (layer_id 字段)` | 字段值缺失 | 2 | 0 个 NULL（50 个域都应有 layer_id：L0_infrastructure / L1_foundation / L2_domain） | domains 表 50 行中有 2 行 layer_id 为 NULL，无法归入 L0/L1/L2 分层 | AI 按层级筛选域时会漏掉这 2 个域，导致它们在热力图/容量报告/域文档中缺失或归类错误 | 从 ddd_model.yaml 或 domain 映射表补全这 2 个域的 layer_id | P1 应做 | YAML 真源 + DB 缓存 | PAN-BUILT-20 |
| GAP-TBL-03 | `dataflow_runs` | 空表待填 | 0 | 运行时动态产生（每个 job 每次执行一行） | 无任何 job 执行记录（status/耗时/参数） | AI 排查问题时看不到运行历史，只看到设计态（应该每天跑），看不到实际态（三天没跑成功了） | 依赖观测系统先建好，再回填 DB | P2 延后 | DB 直写（运行时动态产生） | PAN-RUN-01 |
| GAP-TBL-05 | `runtime_observations（待建）` | 完全缺失 | —（表不存在） | 新建表，记录运行时指标（延迟/错误率/吞吐） | 搜索 runtime/telemetry/metric/trace/observ = 0 张表 | AI 无法获得运行时性能数据，不知道哪个任务慢/哪个错误率高 | 新建 runtime_observations 表 + 观测系统采集 | P2 延后 | DB 直写（运行时动态产生） | PAN-RUN-01 / PAN-RUN-04 |
| GAP-TBL-06 | `field_lineage（待建）` | 完全缺失 | —（表不存在） | 新建表，记录 source_field → transformation → target_field | field_vocabularies（321 行）只是字段枚举字典，不是血缘；dataflow_edges（28 行）是表级血缘，不够字段级 | AI 改一个字段时不知道下游哪些字段受影响（改 close 不知道 ma20/macd 都依赖它），会漏改下游 | 从代码静态分析派生（解析每个 job 的 SQL/Python 字段映射）或运行时追踪 | P2 延后 | 代码分析派生 + DB 缓存 | PAN-ASSET-04 |

---

## 详细内容清单

> 按输出目录顺序排列。已建项标注真源/生成器/产物路径；待建项标注规划目录/优先级/真源待裁定。

### 架构图生成统计

> 每个架构图各生成了多少个全景图（可视化产物）。

| 架构图来源 | 全景图数量 | 说明 |
|------|:---:|------|
| depgraph | 11 | 依赖图——模块节点和依赖边，生成域文档/矩阵/拓扑/热力图/容量/违规等 |
| 手工 | 6 | 人工维护的架构文档，无自动生成器 |
| 待裁定（depgraph 域派生 vs 独立表） | 4 | 待裁定真源类型 |
| 文件系统扫描 | 2 | 扫描实际文件系统派生，无 DB 真源 |
| dataflowgraph | 1 | 数据流图——Dataset/Job/Edge，生成数据流图 |
| decisiongraph | 1 | 决策流图——L0-L6 四轨，生成决策流图 |
| depgraph + dataflowgraph + decisiongraph | 1 | 综合三个架构图派生（如本总表） |
| 待裁定（AlertManager API vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（GitHub Actions API vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（OpenTelemetry trace 聚合 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（OpenTelemetry 采集 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（YAML 威胁建模 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（dataflowgraph 字段级扩展 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（dataflowgraph 扩展 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（decisiongraph 派生 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（depgraph compliance 扩展 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（depgraph contracts 扩展 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（depgraph 扩展 vs 独立表） | 1 | 待裁定真源类型 |
| 待裁定（代码扫描派生 vs 独立表） | 1 | 待裁定真源类型 |
| **合计** | **38** | 已建 22 + 待建 16 |

---

### 00 入口导航

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-00a | 导航索引（navigation_index） | ✅已建 | 文件系统扫描 | 文档库导航索引，列出 02_enterprise_architecture 下所有文档 | 真源：文件系统扫描<br>生成器：[`generate_navigation_index.py`](../../../scripts/governance/d5_architecture/generators/generate_navigation_index.py)<br>产物：[`00_overview_entry/navigation_index.md`](navigation_index.md) |
| PAN-BUILT-00b | 全景图清单总表（本文件） | ✅已建 | depgraph + dataflowgraph + decisiongraph | 全景图清单总表，记录已建/待建全景图状态（本文件自身） | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_panorama_registry.py`](../../../scripts/governance/d5_architecture/generators/generate_panorama_registry.py)<br>产物：[`00_overview_entry/panorama_registry.md`](panorama_registry.md) |

### 01 全局架构图

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-05 | 跨域依赖矩阵 | ✅已建 | depgraph | 域间依赖的详细数据矩阵 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_cross_domain_matrix.py`](../../../scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py)<br>产物：[`01_global_architecture_diagram/cross_domain_matrix.md`](../01_global_architecture_diagram/cross_domain_matrix.md) |
| PAN-BUILT-06 | 集成拓扑图 | ✅已建 | depgraph | 43 个域之间怎么互相依赖的集成拓扑图 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_integration_topology.py`](../../../scripts/governance/d5_architecture/generators/generate_integration_topology.py)<br>产物：[`01_global_architecture_diagram/integration_topology.md`](../01_global_architecture_diagram/integration_topology.md) |
| PAN-BUILT-08 | 路径全景（全项目目录树） | ✅已建 | 文件系统扫描 | 全项目目录树（中英文双语） | 真源：文件系统扫描<br>生成器：[`generate_path_tree.py`](../../../scripts/governance/d5_architecture/generators/generate_path_tree.py)<br>产物：[`01_global_architecture_diagram/full_project_tree_zh.md`](../01_global_architecture_diagram/full_project_tree_zh.md) |
| PAN-BUILT-09 | 能力热力图（53域×10能力） | ✅已建 | depgraph | 53 个域 × 10 个能力维度的热力图 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_capability_heatmap.py`](../../../scripts/governance/d5_architecture/generators/generate_capability_heatmap.py)<br>产物：[`01_global_architecture_diagram/global_capability_heatmap.md`](../01_global_architecture_diagram/global_capability_heatmap.md) |
| PAN-BUILT-10 | 资产清单配置 | ✅已建 | depgraph | 资产清单（从 depgraph (PostgreSQL) 派生，非运行时 CMDB） | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_asset_catalog.py`](../../../scripts/governance/d5_architecture/generators/generate_asset_catalog.py)<br>产物：[`01_global_architecture_diagram/asset_catalog.md`](../01_global_architecture_diagram/asset_catalog.md) |
| PAN-BUILT-11 | 契约目录配置 | ✅已建 | depgraph | 契约目录（从 depgraph (PostgreSQL) contracts 表派生） | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_contract_catalog.py`](../../../scripts/governance/d5_architecture/generators/generate_contract_catalog.py)<br>产物：[`01_global_architecture_diagram/contract_catalog.md`](../01_global_architecture_diagram/contract_catalog.md) |

### 02 域架构文档

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-20 | 域架构文档（50 域 + domain_index） | ✅已建 | depgraph | 每个功能域一份详细说明书（50 个域文档 + 1 个 domain_index.md），从 depgraph (PostgreSQL) nodes/edges 派生 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_domain_doc.py`](../../../scripts/governance/d5_architecture/generators/generate_domain_doc.py)<br>产物：`02_domain_architecture_docs/` |

### 03 治理报告

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-12 | 容量报告 | ✅已建 | depgraph | 各功能域的模块数量与容量上限对比，识别超容域和接近超容域 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_capacity_report.py`](../../../scripts/governance/d5_architecture/generators/generate_capacity_report.py)<br>产物：[`03_governance_reports/capacity_report.md`](../03_governance_reports/capacity_report.md) |
| PAN-BUILT-13 | 约束违规报告 | ✅已建 | depgraph | 架构约束违规报告 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_constraint_violations.py`](../../../scripts/governance/d5_architecture/generators/generate_constraint_violations.py)<br>产物：[`03_governance_reports/constraint_violations.md`](../03_governance_reports/constraint_violations.md) |
| PAN-BUILT-14 | 设计态 vs 运营态 | ✅已建 | depgraph | 设计态到运营态的迁移进度对比 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_design_vs_production.py`](../../../scripts/governance/d5_architecture/generators/generate_design_vs_production.py)<br>产物：[`03_governance_reports/design_vs_production.md`](../03_governance_reports/design_vs_production.md) |

### 04 架构原则与决策

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-17 | 依赖与路径全景图能力定位书 | ✅已建 | 手工 | 依赖与路径全景图能力定位书（双态模型 + SSoT 分层 + 生命周期 + 生成器覆盖矩阵） | 真源：手工<br>生成器：`(手工维护)`<br>产物：[`04_architecture_principles_decisions/dependency_path_panorama.md`](../04_architecture_principles_decisions/dependency_path_panorama.md) |

### 05 数据流架构

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-18 | 数据流图（dataflowgraph Dataset/Job/Edge） | ✅已建 | dataflowgraph | 数据流图 dataflowgraph（Dataset/Job/Edge），三图正交第二维度 | 真源：depgraph (PostgreSQL) (dataflow_* 表)<br>生成器：[`generate_dataflow_diagram.py`](../../../scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py)<br>产物：[`05_dataflow_architecture/dataflow_index.md`](../05_dataflow_architecture/dataflow_index.md) |

### 06 决策流架构

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-19 | 决策流图（decisiongraph L0-L6 四轨） | ✅已建 | decisiongraph | 决策流图 decisiongraph（L0-L6 四轨），三图正交第三维度 | 真源：depgraph (PostgreSQL) (decision_* 表)<br>生成器：[`generate_decision_diagram.py`](../../../scripts/governance/d5_architecture/generators/generate_decision_diagram.py)<br>产物：[`06_decision_architecture/decision_index.md`](../06_decision_architecture/decision_index.md) |

### generated 自动生成中间产物

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-04 | 模块依赖图（depgraph nodes/edges） | ✅已建 | depgraph | 每个功能域一张 .mmd 依赖图，从 depgraph (PostgreSQL) nodes/edges 表派生 | 真源：depgraph (PostgreSQL)<br>生成器：[`generate_domain_dependency_diagram.py`](../../../scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py)<br>产物：`generated/domains/` |
| PAN-BUILT-07 | 循环依赖检测（Tarjan SCC） | ✅已建 | depgraph | 内置 Tarjan SCC 算法检测循环依赖，输出循环报告 | 真源：depgraph (PostgreSQL)<br>生成器：`内置在生成器（Tarjan SCC）`<br>产物：[`generated/panorama_alignment_report.md`](../generated/panorama_alignment_report.md) |

### sample 样板/模板区

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-21 | 样板/模板区（7 个样板文件） | ✅已建 | 手工 | 给人类写文档时参考的样板（overview_entry_sample / architecture_principles_sample / manual_architecture_views_sample / d_trading_sample / 手工架构图样板 / integration_topology_sample / path_tree_sample） | 真源：手工<br>生成器：`(手工维护)`<br>产物：`sample/` |

### target_architecture TOGAF 目标架构

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-01 | TOGAF 4视图 + 6正交视图 | ✅已建 | 手工 | TOGAF 业务/信息/应用/技术 4视图 + 安全/集成/运营/治理/前端/运行时平面/能力热力图 6正交视图 | 真源：YAML (architecture_model/) + 手工<br>生成器：`(手工维护)`<br>产物：[`target_architecture/overview.md`](../target_architecture/overview.md) |
| PAN-BUILT-02 | C4 L1/L2/L3 架构图 | ✅已建 | 手工 | C4 模型 L1 系统上下文 / L2 容器 / L3 组件图（d_ex_core / d_mkt_data / d_ml_train） | 真源：手工<br>生成器：`(手工维护)`<br>产物：[`target_architecture/diagrams/c4_l1_system_context.mmd`](../target_architecture/diagrams/c4_l1_system_context.mmd) |
| PAN-BUILT-03 | 28个 Mermaid 图（拓扑/时序/数据流） | ✅已建 | 手工 | 拓扑/时序/数据流/部署/激活甘特/三层治理等 28 张 Mermaid 图 | 真源：手工<br>生成器：`(手工维护)`<br>产物：`target_architecture/diagrams/` |

### 08 资产全景（待建）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-ASSET-01 | 资产清单 / CMDB | ⏳待建 | 待裁定（depgraph 扩展 vs 独立表） | 一张图看完所有运行中服务/数据流/契约的总览。量化系统有大量外部数据源/券商接口，资产清单是风险管理基础 | 规划目录：`08_asset_panorama/`<br>生成器：`generate_asset_panorama.py (待建)`<br>真源待裁定：待裁定：PostgreSQL 表 asset_registry（运行时服务/数据流/契约总览）vs YAML 静态配置。现有 asset_inventory.yaml 只是配置，不构成全景图<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md) / [`data_inventory.md`](../../03_modules/_domain_data/data_inventory.md) |
| PAN-ASSET-02 | API 契约目录 | ⏳待建 | 待裁定（depgraph contracts 扩展 vs 独立表） | 面向人类的 API 契约目录全景图（谁提供什么/谁消费什么/版本号/Owner）。量化系统接口众多（行情/交易/风控），契约目录是接入新策略的入口 | 规划目录：`08_asset_panorama/`<br>生成器：`generate_api_contract_catalog.py (待建)`<br>真源待裁定：待裁定：扩展现有 depgraph contracts 表 vs 独立 api_contracts 表。现有 PAN-BUILT-11 契约目录配置只是静态派生，缺版本号/Owner/消费方<br>相关蓝图：[`contracts_blueprint.md`](../../03_modules/_cross_layer/shared_core/contracts_blueprint.md) / [`blueprint.md`](../../03_modules/_domain_integration/blueprint.md) |
| PAN-ASSET-03 | 数据目录 Data Catalog | ⏳待建 | 待裁定（dataflowgraph 扩展 vs 独立表） | 从全景图派生的数据目录，含数据完整性/延迟/质量的实时视图。量化强依赖数据质量，PIT/幸存者偏差/数据缺口必须可视化 | 规划目录：`08_asset_panorama/`<br>生成器：`generate_data_catalog.py (待建)`<br>真源待裁定：待裁定：扩展现有 dataflow_datasets 表加完整性/延迟/质量字段 vs 独立 data_catalog 表。现有 data_acquisition_plan.md / data_catalog.md 不是从全景图派生<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_data/blueprint.md) / [`data_catalog.md`](../../03_modules/_domain_data/data_catalog.md) / [`data_acquisition_plan.md`](../../03_modules/_domain_data/data_acquisition_plan.md) |
| PAN-ASSET-04 | 数据血缘图 Data Lineage | ⏳待建 | 待裁定（dataflowgraph 字段级扩展 vs 独立表） | 字段级血缘图（某个因子字段上游来自哪些原始表）。因子可解释性、监管追溯、数据问题定位必备 | 规划目录：`08_asset_panorama/`<br>生成器：`generate_data_lineage.py (待建)`<br>真源待裁定：待裁定：扩展 dataflow_edges 表加字段级血缘 vs 独立 column_lineage 表。dataflowgraph 是作业级流图，缺字段级血缘<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_data/blueprint.md) / [`blueprint.md`](../../03_modules/_cross_layer/database/blueprint.md) |

### 09 运行时全景（待建）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-RUN-01 | 实时调用链拓扑 + SLO 看板 | ⏳待建 | 待裁定（OpenTelemetry 采集 vs 独立表） | 实时调用链拓扑 + SLO 看板。量化系统盘后/盘中运维刚需 | 规划目录：`09_runtime_panorama/`<br>生成器：`generate_runtime_topology.py (待建)`<br>真源待裁定：待裁定：OpenTelemetry / Prometheus 采集 vs 独立 runtime_calls 表。有 telemetry 配置但缺实时调用链拓扑/SLO 看板<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md) / [`blueprint.md`](../../03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md) |
| PAN-RUN-02 | 告警热力图 | ⏳待建 | 待裁定（AlertManager API vs 独立表） | 告警热力图，量化系统盘后/盘中运维刚需 | 规划目录：`09_runtime_panorama/`<br>生成器：`generate_alert_heatmap.py (待建)`<br>真源待裁定：待裁定：AlertManager API 实时拉取 vs 独立 alert_history 表<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md) |
| PAN-RUN-03 | CI/CD 流水线图 | ⏳待建 | 待裁定（GitHub Actions API vs 独立表） | 全项目构建/发布/部署流水线总览图 | 规划目录：`09_runtime_panorama/`<br>生成器：`generate_cicd_pipeline.py (待建)`<br>真源待裁定：待裁定：GitHub Actions API 拉取 vs 独立 cicd_pipelines 表。有 frontend_build_pipeline.mmd 但缺全项目构建/发布/部署流水线总览<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_governance/blueprint.md) / [`blueprint.md`](../../03_modules/_cross_layer/pipeline/blueprint.md) |
| PAN-RUN-04 | 服务依赖运行时视图 | ⏳待建 | 待裁定（OpenTelemetry trace 聚合 vs 独立表） | 运行时实际调用频次/延迟/失败率加权的动态依赖图 | 规划目录：`09_runtime_panorama/`<br>生成器：`generate_runtime_dependency.py (待建)`<br>真源待裁定：待裁定：OpenTelemetry trace 聚合 vs 独立 runtime_calls 表。现有依赖图是静态 import，缺运行时实际调用频次/延迟/失败率加权<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md) |

### 10 安全全景（待建）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-SEC-01 | 威胁模型图 STRIDE | ⏳待建 | 待裁定（YAML 威胁建模 vs 独立表） | STRIDE 威胁模型图（攻击面/信任边界/数据流威胁标注） | 规划目录：`10_security_panorama/`<br>生成器：`generate_stride_threat_model.py (待建)`<br>真源待裁定：待裁定：YAML 威胁建模（架构师手工）vs 独立 threat_models 表。有 security_architecture.md 但缺攻击面/信任边界/数据流威胁标注<br>相关蓝图：[`security_architecture.md`](../target_architecture/security_architecture.md) / [`blueprint.md`](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| PAN-SEC-02 | 合规矩阵 | ⏳待建 | 待裁定（depgraph compliance 扩展 vs 独立表） | 规则×系统×状态 合规全景看板 | 规划目录：`10_security_panorama/`<br>生成器：`generate_compliance_matrix.py (待建)`<br>真源待裁定：待裁定：扩展现有 compliance 域 916 模块元信息 vs 独立 compliance_matrix 表。compliance 域有 916 模块但没规则×系统×状态看板<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_compliance/blueprint.md) |

### 11 风险全景（待建）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-RISK-01 | 风险敞口全景图 | ⏳待建 | 待裁定（depgraph 域派生 vs 独立表） | 风险敞口全景图（因子暴露/行业暴露/风格暴露/资金使用率）。量化特有，组合层面必须 | 规划目录：`11_risk_panorama/`<br>生成器：`generate_risk_exposure.py (待建)`<br>真源待裁定：待裁定：从 D_RISK/D_PORTFOLIO 域派生 vs 独立 risk_exposure 表。量化特有：因子暴露/行业暴露/风格暴露/资金使用率，组合层面必须<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_risk/blueprint.md) / [`blueprint.md`](../../03_modules/_domain_portfolio_core/blueprint.md) |

### 12 量化全景（待建）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-QUANT-01 | 因子全景图 | ⏳待建 | 待裁定（depgraph 域派生 vs 独立表） | 因子分类树 + 因子相关性矩阵 + IC 衰减热力图 | 规划目录：`12_quant_panorama/`<br>生成器：`generate_factor_panorama.py (待建)`<br>真源待裁定：待裁定：从 D_FACTOR 域派生 vs 独立 factor_registry 表。D_FACTOR 只有依赖图，缺因子分类树 + 相关性矩阵 + IC 衰减热力图<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_factor/blueprint.md) |
| PAN-QUANT-02 | 策略谱系图 | ⏳待建 | 待裁定（decisiongraph 派生 vs 独立表） | 策略→因子→数据 的血缘链 | 规划目录：`12_quant_panorama/`<br>生成器：`generate_strategy_lineage.py (待建)`<br>真源待裁定：待裁定：从 decisiongraph L0-L6 派生 vs 独立 strategy_registry 表。策略→因子→数据的血缘链，目前只在 decisiongraph 里有 L0-L6 链路<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_signal/blueprint.md) / [`blueprint.md`](../../03_modules/_domain_research/blueprint.md) |
| PAN-QUANT-03 | 回测对比看板 | ⏳待建 | 待裁定（depgraph 域派生 vs 独立表） | 多策略回测结果对比（Sharpe/回撤/胜率）全景 | 规划目录：`12_quant_panorama/`<br>生成器：`generate_backtest_comparison.py (待建)`<br>真源待裁定：待裁定：从 D_BACKTEST 域派生 vs 独立 backtest_results 表。多策略回测结果对比（Sharpe/回撤/胜率），目前各回测孤立<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_backtest/blueprint.md) |
| PAN-QUANT-04 | 订单生命周期图 | ⏳待建 | 待裁定（depgraph 域派生 vs 独立表） | 订单状态机 + 成交分布 + 拒单热力图 | 规划目录：`12_quant_panorama/`<br>生成器：`generate_order_lifecycle.py (待建)`<br>真源待裁定：待裁定：从 D_TRADING/D_EX_CORE 派生 vs 独立 order_lifecycle 表。目前只有时序图 seq_order_submit.mmd，缺订单状态机 + 成交分布 + 拒单热力图<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_execution_core/blueprint.md) |

### 13 可视化前端架构（待建）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-VIS-01 | 可视化前端架构文档 | ⏳待建 | 待裁定（代码扫描派生 vs 独立表） | 可视化前端架构（Panel + HoloViz + Plotly + TradingView Lightweight Charts v5.2）组件拓扑/数据流/部署图。target_architecture/frontend_architecture.md 已有 TOGAF 视图，本目录放更细的可视化前端架构 | 规划目录：`13_visualization_architecture/`<br>生成器：`(手工维护 + 部分自动生成)`<br>真源待裁定：待裁定：从 src/zephyr/frontend/ 代码扫描派生 vs 独立 frontend_components 表。代码进 src/zephyr/frontend/，文档进 13_visualization_architecture/<br>相关蓝图：[`blueprint.md`](../../03_modules/_domain_frontend/blueprint.md) / [`frontend_architecture.md`](../target_architecture/frontend_architecture.md) |

### 根目录（架构债务注册表）

| ID | 名称 | 状态 | 来自架构图 | 内容描述 | 真源/规划 |
|------|------|:---:|------|------|------|
| PAN-BUILT-16 | 架构债务注册表（337项） | ✅已建 | 手工 | 全项目架构债务单一真源，337 个违规点 + 6 个根因 | 真源：手工<br>生成器：`(手工维护)`<br>产物：[`architecture_debt_registry.md`](../architecture_debt_registry.md) |

---

## 修订记录

| 日期 | 说明 |
|------|------|
| auto-generated | 自动生成 |