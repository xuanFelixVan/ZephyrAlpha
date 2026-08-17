---
ttl: permanent
doc_type: architecture_view
title: AI 层域边界定义
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.0"
date: 2026-08-17
topic: domain_boundary_definition
scope: 09_ai_architecture
---

# AI 层域边界定义

> 本文定位：定义 AI 层在 depgraph 中的域边界——哪些域归入 AI 层，AI 层是横切视图还是独立域。**本文是裁定类文档**（按"问题→选项→依据→裁定"组织）：产出是裁定方案与选项分析，最终拍板权在 Owner，AI 不作未授权裁定。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，资产盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)，外部对标见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | AI 层域边界 |
| 所属 | [00_index.md](00_index.md) §4 目录结构 |
| 依赖 | depgraph（PostgreSQL，74 域，2026-08-17 经 `extract_depgraph.py --summary` 实测）；功能域注册表 `functional_domain_registry.yaml`；`target_layer_vocabulary.yaml` |
| 优先级 | P0——AI 层所有后续工作的前提（U1 解锁点：04/05/08 号文等待本文裁定） |
| 状态 | draft（已填充，待 Owner 裁定后升 active） |
| 文档类型 | 裁定类（跳过门：通用规则 19 depgraph L1 铁律 N/A——本文不新建模块） |

---

## 2. 背景

### 2.1 项目处境

**depgraph 当前规模**（2026-08-17 经 `python scripts/governance/extract_depgraph.py --summary` 实测）：

| 指标 | 实测值 |
|---|---|
| 域总数 | 74 |
| 模块总数 | 3826 |
| 生产态节点 | 3776 |

74 域按架构层分组（真源：[domain_index.md](../../02_domain_architecture_docs/domain_index.md)，由 `generate_domain_index.py` 从 depgraph 自动生成）：L0 基础设施层 8 域、L1 基础平台层 20 域、L2 业务域层 46 域。

**AI 相关域的现状**（2026-08-17 经 `extract_depgraph.py --domains <域清单>` 实测模块数；代码路径经 LS/Glob 实测，详细资产清单真源见 [02_design_asset_inventory.md](02_design_asset_inventory.md) §3.4）：

| 域 | depgraph 模块数 | 生产节点 | 代码对应（实测路径） | 边界问题 |
|---|---:|---:|---|---|
| D_AUTONOMY_CORE | 131 | 131 | `src/zephyr/autonomy_core/` | 无争议——AI 层事实核心域 |
| D_INTELLIGENCE | 33 | 31 | `src/zephyr/intelligence/`（画像/考试/护照/岗位匹配）+ `autonomy_core/context/` | 上下文管理归属清晰 |
| D_ORCHESTRATOR | 72 | 70 | `src/zephyr/orchestrator/` | 与"不做 agent 编排系统"裁定（61 号备忘 §2.3）的角色张力待界定 |
| D_ML_TRAIN | 15 | 6 | `src/zephyr/ml_train/`（骨架态）+ `src/zephyr/intelligence/model_profiling/`+`model_evaluation/`（注册表 ssot_path 归属） | 画像/考试代码物理位置与域归属分离 |
| D_ML_SERVE | 7 | 7 | `src/zephyr/ml_serve/`（骨架态） | 未登记入 `target_layer_vocabulary.yaml` 44 合法值 |
| D_KNOWLEDGE | 1 | 0 | 无独立代码包；唯一节点是蓝图 `docs/03_modules/_domain_knowledge/vector_memory/blueprint.md` | 空壳域：注册表 ssot_path 指向 `src/zephyr/integration/vector_memory/`，但该代码在 depgraph 挂在 D_INTEGRATION 下 |
| D_SECURITY_LLM | 0 | 0 | 代码 `src/zephyr/security/llm_defense/`（L0~L8）在 depgraph 挂在 D_SECURITY（171 模块）下 | 空域：注册表有 ssot_module=MOD-LLM_SECURITY，depgraph 零节点 |
| D_AUTONOMY_PERM | 2 | 2 | `src/zephyr/autonomy_perm/` | 小域，归属清晰 |
| D_INTEGRATION_GATEWAY | 0 | 0 | MCP 服务端代码 `src/zephyr/integration/mcp/` 挂在 D_INTEGRATION（71 模块）下 | 空域：注册表有 MOD-INF-013（11 个 MCP 服务端），depgraph 零节点 |
| D_FEEDBACK_LOOP | 125 | 125 | `src/zephyr/feedback_loop/` | 自我迭代闭环（evolution/ 含 self_reflection 等），是否归入 AI 层待定 |
| D_FBL_DETECTORS / D_FBL_DIAGNOSERS / D_FBL_VERIFICATION | 65 / 76 / 71 | 65 / 76 / 71 | `src/zephyr/feedback_loop/detectors|diagnosers|gates|verifiers` | 反馈三子域，同上待定 |
| D_GOV_DRIFT | 72 | 72 | `src/zephyr/gov_drift/` | 漂移检测是 AI 自治边界（15 号文）的依赖，域本身属治理体系 |
| D_BEHAVIORAL_AUDIT | 0 | 0 | 注册表指向 `src/zephyr/gov_drift/detector_core/` | 空域 |
| D_INFRA_RUNTIME | 172 | 171 | `src/zephyr/infra_runtime/` 等 | 三层运行时（L1/L2/L3）承载域，超容（172/150） |
| D_INFRA_A2A | 72 | 72 | `src/zephyr/infrastructure/a2a_protocol/` | Agent 通信基础设施 |
| D_GOVERNANCE | 467 | 467 | `src/zephyr/governance/` 等 | 超容（467/150）；`intelligence_governance/` 25 文件挂在此域下（05 号文整合对象） |

**关键观察**：

1. **AI 设施物理散布**：AI 层相关代码已分布在 10+ 个既有域中（自治核心/智能/编排/安全/反馈/基础设施/治理），不存在一个"尚未认领的 AI 空地"。任何域边界方案都必须以这个分布现实为前提。
2. **三个空域**：D_SECURITY_LLM、D_INTEGRATION_GATEWAY、D_BEHAVIORAL_AUDIT 在 depgraph 中零节点，但注册表均有 ssot_module 登记——注册表声明与图节点不一致。
3. **一个空壳域**：D_KNOWLEDGE 仅 1 个蓝图节点、0 生产节点，其注册表声明的 ssot_path 代码实际挂在 D_INTEGRATION 下。
4. **词表已有分组先例**：`target_layer_vocabulary.yaml` v1.0.0 已按「AI/智能域」分组登记 5 域（D_AUTONOMY_CORE / D_AUTONOMY_PERM / D_INTELLIGENCE / D_ML_TRAIN / D_KNOWLEDGE），证明"AI 域分组"以词表视图形式存在，但未升级为 depgraph 结构。
5. **标签载体已存在**：depgraph schema（`src/zephyr/governance/depgraph_schema.py`）nodes 表与 nodes_metadata 表均有 `tags TEXT` 字段，edges 表有 `cross_domain` 标志——横切打标无需 schema 变更。
6. **派生视图机制未建**：[00_index.md](00_index.md) §5.2 规划的 `derived_graphs/`（含 01_ai_layer_dependency_topology 跨域 AI 层依赖拓扑）目录尚未建立，`09_ai_architecture/` 下当前只有 `implementation_plans/`。

### 2.2 核心问题

- **Q1（主裁定）**：AI 层是横切视图还是独立域？——D_AUTONOMY_CORE / D_ORCHESTRATOR / D_INTELLIGENCE / D_ML_TRAIN / D_ML_SERVE / D_KNOWLEDGE / D_SECURITY_LLM 等哪些归入 AI 层？还是 AI 层不作为 depgraph 域、只作为跨域视图存在？
- **Q2（从属裁定）**：D_KNOWLEDGE（1 蓝图节点、0 生产节点、无独立代码包）保留、合并还是退役？
- **Q3（衍生）**：三个空域（D_SECURITY_LLM / D_INTEGRATION_GATEWAY / D_BEHAVIORAL_AUDIT）与一个错挂（intelligence_governance 25 文件挂 D_GOVERNANCE）如何归位？
- **为什么现在必须裁定**：U1 解锁点——04（AutoRuntime）、05（intelligence_governance 整合）、08（多 AI 并发治理）号文都依赖"设施归哪个域"的答案才能确定施工归属。

### 2.3 约束条件

| 约束 | 来源 | 对域边界裁定的影响 |
|---|---|---|
| 1 人全栈 + 100% AI 生成代码 | [system_charter.md §2](../../04_architecture_principles_decisions/system_charter.md) 约束一 | 域治理负担必须单人可维护；新增域=新增注册表/容量/文档维护面 |
| 单机无集群 | system_charter §2 约束二 | 域划分不考虑分布式部署边界 |
| AI 生成代码需交叉验证 | system_charter §2 约束六 | 域归属必须机器可查（注册表+depgraph），不能靠 AI 记忆 |
| 架构手动来 | [00_index.md](00_index.md) §4（用户明确） | **域结构变更=架构决策，只能由 Owner 拍板**——本文只出方案 |
| 不做 agent 编排系统 | 61 号备忘 §2.3（已定稿） | D_ORCHESTRATOR 的"编排"语义已冻结，域角色界定不能复活编排路线 |
| depgraph 程序化访问 | TRAE-054 v1.6.0（frozen，immutable_core） | 任何域调整必须走 `apply_depgraph.py`，禁止直接改 DB |
| 过度工程红线 | 通用规则 5 + system_charter §2 | 74 域已 6 个超容；新增 D_AI 域需充分理由，否则 = 过度工程 |

### 2.4 已施工设施盘点

> 通用规则 11：与"域边界裁定"主题相关的全部已建设施。全部路径 2026-08-17 实测存在。

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 数据库 | depgraph（PostgreSQL localhost:5432，经 `config/.env.postgres` 连接） | 74 域 / 3826 模块 / 3776 生产节点；domains/nodes/edges/domain_dependencies 等表 | production |
| Schema | `src/zephyr/governance/depgraph_schema.py` | 域/节点/边 DDL；nodes.tags + nodes_metadata.tags（横切标签载体）+ edges.cross_domain | production |
| 脚本 | `scripts/governance/extract_depgraph.py` | 只读提取入口（--summary/--domains/--modules/--top/--paths/--stats） | production |
| 脚本 | `scripts/governance/apply_depgraph.py` | depgraph 唯一合法写入口（PG 事务回滚 + 物理备份） | production |
| 脚本 | `scripts/governance/generate_project_depgraph.py` / `diagnose_depgraph.py` | 图生成器 / 诊断 | production |
| 脚本 | `scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py` | functional_domain_registry.yaml → depgraph 同步（domain_name_zh 口径） | production |
| 注册表 | `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | REG-FUNC-DOMAIN-001 v0.4.0：82 条 domain 条目（治理/基础设施/AI 域 ssot_module 映射真源，交易核心域另见 cross_layer_contracts.yaml） | active |
| 词表 | `docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml` | PS-VOC-006 v1.0.0：44 合法值；已有「AI/智能域」分组（5 域） | active |
| 契约 | `architecture_model/contracts/cross_layer_contracts.yaml` | 交易核心域 domain_id 契约真源 | active |
| 域索引 | `docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md` | 74 域总览（generate_domain_index.py 自动生成） | active（派生） |
| 蓝图目录 | `docs/03_modules/` | 29 个 `_domain_*` 目录（2026-08-17 实测目录数）+ `_cross_layer`/`_master_blueprint`/`_system_master`；与 depgraph 域 ID 非一一对应 | production |
| 提交门禁 | `src/zephyr/gov_enforcement/commit_gates/`（depgraph_pre_registration_gate / depgraph_freshness_gate / depgraph_write_path_gate / rename_depgraph_sync_gate / new_file_depgraph_gate） | 域归属/图新鲜度/写路径五道 commit 门禁 | production |
| 规则 | `docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml` | depgraph 程序化访问协议（frozen） | frozen |
| 域文档 | `docs/02_enterprise_architecture/02_domain_architecture_docs/`（74 篇 D_* 域文档） | 各域模块清单与状态 | active（派生） |
| 相关文档 | [00_index.md](00_index.md) §1 目标架构 / §4 约束；[02_design_asset_inventory.md](02_design_asset_inventory.md) §3.3 已有域盘点；61 号备忘 §2.3 | 裁定上游输入 | active/draft |

---

## 3. 设计决策

> 裁定类组织：问题→选项→依据→裁定。本节只做选项分析与依据汇总，**所有裁定标「待裁定」**，由 Owner 拍板后以修订升版方式回填。

### 3.1 Q1 选项分析：AI 层是横切视图还是独立域？

#### 选项 A：横切视图（不新增域，跨现有域打 AI 标签）

- **机制**：AI 层不作为 depgraph 域存在；用 nodes.tags 打 `ai_layer` 标签（载体已存在，见 §2.4 Schema 行），AI 层视图 = 标签查询结果 + `09_ai_architecture/` 文档树 + 未来 derived_graphs 派生图。
- **成本**：零迁移、零注册表变更；需补一个 tags 受控词表（防标签拼写漂移）和 extract 脚本的标签过滤能力。
- **风险**：标签治理依赖纪律——无门禁时标签会腐烂；域级容量/依赖统计看不到"AI 层总量"。
- **与约束兼容性**：完全兼容"1 人维护"（不加治理面）；兼容现有 74 域归属不动。

#### 选项 B：独立域（新增 D_AI 域，迁入相关模块）

- **机制**：新建 D_AI 域，将 autonomy_core/intelligence/ml_train 等 AI 模块迁入，AI 层 = 一个物理域。
- **成本**：大规模迁移——仅 D_AUTONOMY_CORE 就 131 模块；涉及 path_ownership_map、ssot_path、blueprint 锚定、五道 commit 门禁口径、import 路径、测试引用的全链路改动；74 域已 6 个超容，再加一个巨型域加剧容量治理。
- **风险**：迁移期间 depgraph 预登记门禁（new_file_depgraph_gate 等）会大面积拦截；AI 设施与治理/安全/反馈设施本就交织（如 llm_defense 既是安全也是 AI），一刀切归属制造新争议。
- **与约束兼容性**：与"1 人维护"冲突（迁移+双写期治理负担翻倍）；与"架构手动来"兼容但工程量大。

#### 选项 C：混合（核心域保持独立 + 横切标签标出散布设施）

- **机制**：承认 D_AUTONOMY_CORE / D_INTELLIGENCE / D_ML_TRAIN / D_ML_SERVE / D_AUTONOMY_PERM 已是事实上的 AI 核心域（词表「AI/智能域」分组已登记此 5 域中的 4 个+D_KNOWLEDGE），不迁任何代码；对散布在 D_SECURITY（llm_defense）、D_FEEDBACK_LOOP（evolution/self_reflection）、D_GOVERNANCE（intelligence_governance）、D_INFRA_A2A、D_INTEGRATION（MCP/vector_memory）等域的 AI 设施打横切标签；AI 层 = "AI 核心域集合 ∪ 横切标签集合"的派生视图。
- **成本**：零迁移；标签词表 + 一次存量打标 + extract 标签过滤。
- **风险**："哪些算 AI 核心域"需要一份显式清单（本文 §3.4 给出草案）；标签与域两套口径需防 drift。
- **与约束兼容性**：兼容全部约束；与词表现状（已有 AI/智能域分组）无缝衔接。

#### 三选项对比矩阵

| 维度 | A 横切视图 | B 独立域 D_AI | C 混合 |
|---|---|---|---|
| 代码迁移量 | 0 | 极大（≥数百模块） | 0 |
| 注册表/门禁改动 | 小（+1 词表） | 全链路 | 小（+1 词表） |
| 单人可维护性 | 高 | 低 | 高 |
| AI 层可见性 | 中（标签查询） | 高（物理边界） | 高（核心域清单+标签） |
| 与代码分布现实吻合度 | 高 | 低（强行收拢） | 最高 |
| 过度工程风险 | 无 | 高（触发红线） | 无 |
| 可逆性 | 高（删标签即回滚） | 低 | 高 |

**分析倾向（供裁定参考，非裁定结论）**：选项 C 在全部维度不劣于 A/B，且与词表已有「AI/智能域」分组、61 号备忘编排冻结裁定、代码散布现实三者同时兼容；选项 B 触发过度工程红线（大规模迁移、新增超容域），仅在未来 AI 设施规模翻倍且标签治理失效时才有重评价值。**最终裁定：待裁定（Owner 拍板）**。

### 3.2 Q2 选项分析：D_KNOWLEDGE 处置

现状（§2.1）：1 蓝图节点、0 生产节点；注册表 ssot_path=`src/zephyr/integration/vector_memory/`，但该代码挂在 D_INTEGRATION 下；`docs/03_modules/_domain_knowledge/` 目录存在（vector_memory 蓝图）。

| 选项 | 机制 | 成本 | 风险 | 适配性 |
|---|---|---|---|---|
| C1 保留 | 维持域登记，待 13 号文模块工厂/知识库施工时填充 | 零 | 空壳域长期存在稀释域口径 | 知识库是模块工厂（13 号文）采集→入库的落点方向，保留等于留位 |
| C2 合并入 D_INTELLIGENCE | 蓝图节点迁 D_INTELLIGENCE，注册表条目改挂，退役 D_KNOWLEDGE | 小（1 节点+1 注册表条目+1 目录） | 丢失"知识管理"独立语义；词表「AI/智能域」分组需同步改 | 与"知识=智能层子能力"观点兼容 |
| C3 退役 | 参照 ARCH-045（D_SIGLEGACY 删除）先例退役，蓝图归入 D_INTEGRATION（与代码同域） | 小 | 若 13 号文落地知识库需重建域 | 与"代码在哪域就在哪"的物理一致原则兼容 |

**分析倾向（供裁定参考）**：C1 与 C3 各有依据——若 13 号文模块工厂路线确认施工，C1 留位成本最低；若 Phase 0 不施工知识库，C3 更符合物理一致。C2 改动语义最大、收益最小。**最终裁定：待裁定（与 13 号文路线联动）**。

### 3.3 Q3 衍生边界问题分析

| # | 问题 | 现状实测 | 选项 | 分析倾向（供参考） |
|---|---|---|---|---|
| D1 | D_SECURITY_LLM 空域 | 注册表有 MOD-LLM_SECURITY + 代码 `security/llm_defense/`（L0~L8），depgraph 0 节点，代码挂 D_SECURITY(171，超容) | ①代码节点改挂 D_SECURITY_LLM（顺注册表）②退役空域、维持挂 D_SECURITY（顺物理） | 倾向①：D_SECURITY 已超容（171/150），LLM 防御独立成域正好减压，且 09 号文以 L0~L8 独立施工 |
| D2 | D_INTEGRATION_GATEWAY 空域 | 注册表有 MOD-INF-013（11 MCP 服务端），depgraph 0 节点，MCP 代码挂 D_INTEGRATION(71) | ①MCP 节点改挂 ②退役空域 | 倾向①：D_INTEGRATION 未超容但 MCP 是 10 号文的独立施工面，语义独立 |
| D3 | D_BEHAVIORAL_AUDIT 空域 | 注册表指向 `gov_drift/detector_core/`，depgraph 0 节点 | ①补挂 ②退役并入 D_GOV_DRIFT | 倾向②：功能与 D_GOV_DRIFT(72) 同源同路径，独立域语义弱 |
| D4 | intelligence_governance 25 文件挂 D_GOVERNANCE(467，超容) | 代码在 `src/zephyr/governance/intelligence_governance/` | ①维持现归属+横切标签 ②改挂 D_INTELLIGENCE ③新建子域 | 倾向①：05 号文职责是包整合（统一入口），域迁移超出其范围；打标签即可见；③=过度工程 |
| D5 | D_ORCHESTRATOR 角色界定 | 72 模块（生命周期/沙箱/回滚/健康监控）production；61 号备忘冻结"编排系统" | ①维持域+文档明确"生命周期基础设施≠编排"②域改名去 orchestrator 语义 | 倾向①：改名成本高（路径/注册表/蓝图全链路），语义澄清零成本 |
| D6 | D_ML_SERVE 未入 target_layer 词表 | 词表 44 值无 D_ML_SERVE；注册表与 depgraph 均有此域（7 模块） | ①词表补登 ②不管 | 倾向①：词表自述与注册表/契约保持一致的 SSoT 链路，缺值=链路断裂 |

以上 D1~D6 均为**待裁定**；D1~D3 若裁定"改挂/补挂"，执行走 TRAE-054 协议（apply_depgraph.py），不属于本文档施工范围。

### 3.4 裁定依据汇总

| 依据 | 内容 | 支撑的倾向 |
|---|---|---|
| 代码分布现实 | AI 设施散布 10+ 域（§2.1），无空白 AI 用地 | 选项 C / 反对 B |
| 词表先例 | `target_layer_vocabulary.yaml` 已有「AI/智能域」5 域分组 | 选项 C（零成本衔接） |
| 标签载体 | nodes.tags / nodes_metadata.tags / edges.cross_domain 已在 schema | 选项 A/C 可行 |
| 容量现状 | 74 域中 6 个超容（domain_index 容量列口径：D_GOVERNANCE 467/150、D_GOV_SCRIPTS 438/150、D_GOV_CODE_QUALITY 244/150、D_DATA 209/150、D_GOV_AUDIT 200/150、D_SHARED 188/150；extract 的 module_count 与容量列计数口径不同，容量状态以 domain_index 为准） | 反对新增巨型域（B）；支持空域减压（D1） |
| 已定稿裁定 | 61 号备忘 §2.3 不做 agent 编排系统；00_index §4 架构手动来 | D5 倾向①；全部裁定权归 Owner |
| 过度工程红线 | 通用规则 5 | 反对 B、反对 D4③ |

**AI 核心域清单草案（若裁定选项 C，此清单为「AI 层=核心域∪标签」的核心域部分）**：
D_AUTONOMY_CORE、D_INTELLIGENCE、D_ML_TRAIN、D_ML_SERVE、D_AUTONOMY_PERM、D_KNOWLEDGE（依 Q2 裁定联动）、D_SECURITY_LLM（依 D1 裁定联动）。
**横切标签候选（打 `ai_layer` 标签的散布设施）**：`security/llm_defense/`（若 D1 不迁）、`governance/intelligence_governance/`、`feedback_loop/evolution/`（self_reflection 等）、`infrastructure/a2a_protocol/`、`integration/mcp/`、`integration/vector_memory/`、`infra_runtime/`（三层运行时）、`ml_train/ai_operator/`（MOD-ML-002，design 态）。

### 3.5 考虑过的替代方案

| 替代方案 | 为什么不推荐 |
|---|---|
| 以 `docs/03_modules/` 29 个 `_domain_*` 目录为 AI 层划分基准 | 目录与 depgraph 域 ID 非一一对应（02 号文 §3.3 实测），以目录为基准会制造第二套口径；depgraph 才是真源 |
| 把 AI 层边界画在架构层（L0~L2）上 | AI 设施跨 L0/L1/L2 三层（infra_runtime 在 L0、autonomy_core 在 L1、intelligence 在 L2），层级无法表达 AI 边界 |
| 沿用 battle_map_domain_policy.yaml 的研究/业务域分组视角 | 该文件面向作战地图锚定纪律，不分组 AI 设施；复用会混淆两份职责 |
| 等 derived_graphs 建成后再裁定 | derived_graphs 未建（§2.1 观察 6），等待会阻塞 U1→04/05/08；先裁定域归属，派生图是后续可视化而非前置条件 |

---

## 4. 施工计划

> 本文档是裁定类文档：**本文档自身的"施工"= 完成裁定分析并提交 Owner 拍板**。以下为分阶段计划与各裁定分支的执行路径。通用规则 19（depgraph L1 铁律）不适用——本文档不涉及新建模块/依赖变更；分支路径中凡涉 depgraph 变更的步骤均由对应施工文档（04/05/09/10 号文等）按规则 19 自行登记，本文不出手。

### 4.1 本文档完成路径（Phase 0，当前）

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 1 | 盘点 depgraph 74 域与 AI 相关设施（已完成，§2） | 全部数字可经 `extract_depgraph.py` 复现 |
| 2 | 选项分析与依据汇总（已完成，§3） | 三选项+对比矩阵+倾向标注，无假裁定 |
| 3 | 提交 Owner 裁定 | 本文档 git 提交并进入评审 |
| 4 | Owner 拍板后回填裁定结论 | 升版本+修订记录记裁定编号；status draft→active |

### 4.2 分支 A：若裁定「横切视图」

1. 新建 tags 受控词表条目（`ai_layer` 值定义+适用范围），登记入词表体系。
2. 用 `apply_depgraph.py` 对 §3.4 横切标签候选清单批量打标（dry-run→执行→extract 验证，遵循 TRAE-054 备份协议）。
3. 增强 extract 查询：按 tags 过滤输出 AI 层视图（若现有参数不支持，记为工具缺口，由后续工具文档承接）。
4. 验收：`extract_depgraph.py` 能输出完整 AI 层节点清单，与 §3.4 清单一致。

### 4.3 分支 B：若裁定「独立域 D_AI」

1. 由 Owner 指定承接文档编写 D_AI 域详细设计（本文不出设计，见 §5）。
2. 评估迁移清单（模块/蓝图/注册表条目/门禁口径/测试引用），出迁移影响报告。
3. 按 TRAE-054 协议分批迁移，每批 dry-run+备份+验证。
4. 验收：D_AI 域节点数=迁移清单数；五道 depgraph 门禁全绿；无残留引用旧归属。

### 4.4 分支 C：若裁定「混合」（分析倾向）

1. 确认 §3.4 AI 核心域清单（Owner 可增删）。
2. 同分支 A 步骤 1~2：词表登记 `ai_layer` 标签 + 存量打标（仅横切候选部分）。
3. 在 [00_index.md](00_index.md) §1 目标架构与本文之间建立"AI 层=核心域∪标签"口径链接（由 AI-FILL-00 更新时落地）。
4. 验收：核心域清单+标签清单并集覆盖 00_index §1 目标架构全部组件；04/05/08 号文可按此口径确定设施归属（U1 解锁）。

### 4.5 D_KNOWLEDGE 与衍生问题执行路径

- Q2 裁定后：C1=不动；C2/C3=走 TRAE-054 协议改挂/退役（1 节点量级，单批可完成）。
- D1~D3 裁定后：改挂/补挂/退役均走 TRAE-054 协议，由 Owner 指定执行会话。
- D6 裁定后：词表补登按词表自身 SSoT 链路纪律执行。
- 全部 depgraph 变更动作不在本文档执行（本文只读引用 depgraph）。

### 4.6 与依赖文档的接口假设

- 04 号文（AutoRuntime）：假设归属口径为"AutoRuntime 设施=核心域 D_INFRA_RUNTIME/D_AUTONOMY_CORE 承载+横切标签"，若最终裁定分支 B 则需回填。
- 05 号文（intelligence_governance 整合）：假设 D4 倾向①成立（不改挂，只整合+标签）。
- 09/10 号文：假设 D1/D2 倾向（空域归位）不改变其施工面划分，只改变 depgraph 挂靠。

---

## 5. 不做什么

1. **不做 depgraph 结构重构**：本文只出裁定方案；74 域全局架构（层级/容量/依赖）调整不在本文范围。
2. **不做跨域代码迁移**：迁移方案只到"选项+清单"粒度；任何物理迁移由 Owner 拍板后的专门施工承接。
3. **不做 D_AI 新域详细设计**：若裁定分支 B，新域设计由后续专门文档补充，本文不越权设计。
4. **不改任何注册表/词表/depgraph**：functional_domain_registry、target_layer_vocabulary、depgraph 均为只读引用；本文发现的词表缺值（D6）只登记开放问题。
5. **不改交易决策侧文档**：61 号备忘等只读引用；其裁定（不做编排）作为本文输入而非修订对象。
6. **不新建派生图/视图工具**：derived_graphs 建设、extract 标签过滤增强均登记为后续工作，不在本文施工。
7. **不做域容量治理**：6 个超容域的拆分/扩容是 depgraph 全局治理议题，本文仅在裁定依据中引用其现状。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | AI 层是横切视图还是独立域？ | 待裁定 | §3.1 三选项分析：A 横切标签 / B 独立域 D_AI / C 混合；分析倾向 C；Owner 拍板后回填 |
| Q2 | D_KNOWLEDGE（1 蓝图节点、0 生产节点）保留、合并还是退役？ | 待裁定 | §3.2 三选项（C1 保留/C2 合并入 D_INTELLIGENCE/C3 退役）；与 13 号文模块工厂路线联动 |
| Q3 | D_SECURITY_LLM / D_INTEGRATION_GATEWAY / D_BEHAVIORAL_AUDIT 三个空域如何归位？ | 待裁定 | §3.3 D1~D3：代码改挂顺注册表 vs 退役空域顺物理 |
| Q4 | intelligence_governance 25 文件的域归属？ | 待裁定 | §3.3 D4：维持 D_GOVERNANCE+标签（倾向）/ 改挂 D_INTELLIGENCE / 新建子域（过度工程）；与 05 号文边界联动 |
| Q5 | D_ORCHESTRATOR 域角色如何与 61 号备忘"不做编排"裁定对齐？ | 待裁定 | §3.3 D5：语义澄清（倾向）vs 域改名 |
| Q6 | D_ML_SERVE 是否补登 target_layer_vocabulary.yaml？ | 待裁定 | §3.3 D6：词表 44 值缺此域，SSoT 链路断裂 |
| Q7 | 02 号文 Q4（depgraph 节点级计数查询入口）已由本文实测解答——`extract_depgraph.py --summary/--domains` 即入口，02 号文 §3.3 口径是否回填为节点级？ | 待用户裁定 | 本文只读引用 02 号文，不代改；回填与否及回填时机由 Owner/02 号文维护者决定 |
| Q8 | 04/05/08 号文在 U1 裁定落地前的接口假设（§4.6）是否与各自填充口径冲突？ | 待裁定 | 若其他子代理已按不同假设填充，以 Owner 裁定为准回填对齐 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景（depgraph 74 域/3826 模块经 extract_depgraph.py 实测，AI 相关 17 域现状表，depgraph 设施盘点）+ §3 设计决策（Q1 横切/独立/混合三选项对比矩阵、Q2 D_KNOWLEDGE 三选项、Q3 衍生问题 D1~D6、裁定依据汇总、替代方案）+ §4 施工计划（裁定流程+三分支执行路径）+ §5 不做什么 + §6 开放问题 Q1~Q8（全部待裁定，无假裁定） | AI-FILL-03 按指令集填充裁定类文档；U1 解锁点前置工作 |

---

*维护者：AI 架构协调者*
