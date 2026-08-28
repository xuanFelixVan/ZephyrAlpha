---
ttl: permanent
doc_type: architecture_view
title: Context Engine 施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.3.0"
date: 2026-08-17
topic: context_engine_build
scope: 09_ai_architecture
---

# Context Engine 施工图

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：对齐收口完成——context_engine 蓝图 v1.2.6（2026-08-22 起持续演进）；tests/context/ 46 测试文件+tests/ce/ 7 测试文件实证；CE depgraph 边缺口 7 项已闭环 5 项（syncer 过滤器治本 generated/testing/stable 三态+蓝图依赖表对齐 depgraph 26 实测出边）。
> **最终成果**：GP0 收口目标达成（956 测试绿运行口径留痕）。
> **未做+原因**：inject 段生产空段（context_injector.py 返回空 InjectedContext）/llm_summary 压缩档/InProcessContextEngine 未落地——均属 GP1+；boot_hooks 接线归 Q2 Owner 项。

> 本文定位：Context Engine（上下文引擎）剩余未实现部分的施工计划。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | Context Engine 施工 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 执行层·业务 Agent |
| 依赖 | MOD-CONTEXT_ENGINE 蓝图（部分实现）；04 v0.2.1 §3.5 已双向对齐（Q2 部分成立，boot 接线缺口见 §6）；10 v0.2.2 / 14 v0.2.0 已填充但均无 CE 产出承接（Q3/Q4 证伪登记，见 §6） |
| 优先级 | P1——上下文管理是 AI 层核心能力 |
| 状态 | draft（v0.3.0：Agent 记忆四层候选登记 + 接口复审回填完成） |

---

## 2. 背景

### 2.1 项目处境

Context Engine（MOD-CONTEXT_ENGINE）的代码落位在 `src/zephyr/autonomy_core/context/`。实测（2026-08-17，`Get-ChildItem -Recurse -Filter *.py`）该目录共 **39 个 .py 文件**（含 `__init__.py`，38 个模块），全部 38 个模块的代码头均标注 `[MATURITY] production`。蓝图/指令集中"22 个 .py 文件"的描述已过时（漂移详见 §6 Q7）。

四段流水线 `build→compress→validate→inject` 的代码现状：

| 环节 | 实现载体 | 实现程度 |
|---|---|---|
| build | `context_assembler.py`（632 行）：manifest 文件采集→拼接；另有 `build_context()` 从 VMS 四 Collection（ke_entries/vibe_rules/blueprints/failure_patterns）检索原始上下文 | production，含 VMS 不可用降级（embedded_defaults）与同 session 5 分钟缓存 |
| compress | `context_assembler._compress_context()` 内联触发 `DocCompressor`（`src/zephyr/shared/io/doc_compressor.py`）；`context_evictor.py` 提供条目级三维逐出 | production，但仅规则式压缩单档落地（见 §3.3） |
| validate | `ContextAssembler.validate()`（G3 门禁：文件存在可读 + token ≤ 预算 + file_count > 0）；`integrity_check.py` 注入后完整性 | production |
| inject | `context_injector.py`（485 行）：`inject_by_task_id/module_id/keyword` 三种模式 API 完整，但**生产返回空 InjectedContext**（源码注释："Production retrieval is handled out-of-band by the context pipeline"） | API 就绪、数据源未接线 |
| 组合根 | `context_pipeline.py`：`run_context_four_stage()` 显式编排上述四段，`run_context_four_stage_or_raise()` 硬门禁版本 | production |
| 自动化 | `context_pipeline_auto.py`：EventBus 订阅（TASK_STARTED/COMPLETED/FAILED）+ KillSwitch 熔断 + 超时自动关闭 | production，但代码内实测无 src 内消费方（头部 [CONSUMERS] 声称 zephyr.trading.boot_hooks——实测该文件存在但并未 import 本模块，属 [CONSUMERS] 漂移） |

关键事实：四段流水线中 **build/compress/validate 三段已生产可用**，**inject 是唯一的生产空段**；接口规范 `context_engine_interface.md` §4.1 定义的 `InProcessContextEngine`（三源汇聚 async 版，落位 `src/zephyr/orchestration/context_management/in_process.py`）**未落地**（该目录实测不存在）。

### 2.2 核心问题

| 问题 | 实测现状 | 缺口 |
|---|---|---|
| Token 预算管控 | `DEFAULT_CONTEXT_TOKEN_BUDGET = 8000`（`src/zephyr/infrastructure/capacity_assurance/token_budget.py`，含 L1=500/L2=1500/L3=8000 三级配额 + 7200 降级阈值）；`context_budget_tracker.py` 三级阈值告警；`context_budget.py` 四种截断策略（newest_first/oldest_first/summary_first/relevance_first） | 预算机制完整，缺生产环境超限行为验证 |
| 上下文压缩 | `DocCompressor`（规则式：保留 Markdown 标题/frontmatter/不可变块）已接入 Assembler | 接口规范 §4.1 设计的 llm_summary（本地 Qwen 分 slot 摘要）/rule_based/truncate 三档策略仅落地规则式一档 |
| 记忆检索 | `build_context()` 经 `vector_bridge.py`（VMSSearchProtocol，5s 超时，VMS 不可用降级）；`memory_bank.py` 提供 6 个结构化 .md 跨 session 持久上下文；D_INTELLIGENCE 域 `unified_memory_api.py` 提供 recall/write/search | inject 段未接 UnifiedMemoryAPI；检索结果无质量评分 |
| 一致性 | 组合根已消除"Assembler ≠ 四段"的审计歧义 | 蓝图漂移（22 vs 39 文件、§1.1 索引仅 1 行、build_status=planned vs 代码 production）误导新 session |

> **边界注记（记忆 vs 知识域）**：源 21-D-KNOWLEDGE §0/§6——D-AUTONOMY-05 管"怎么记住"（存储机制/检索机制/记忆生命周期），D-KNOWLEDGE 管"记住什么"（知识结构/知识关系/知识质量），两者正交；类比：海马体（记忆存取）vs 新皮层（知识表征）。落到 CE 语境：本文管"上下文怎么进 prompt"，记忆存取机制的分层候选见 §3.5，知识结构本体归 D-KNOWLEDGE。

### 2.3 约束条件

- **硬件**（[system_charter.md §2](../../04_architecture_principles_decisions/system_charter.md) 约束二）：单机 RTX 3090 24GB（显存 <90%）/ 64GB RAM。本地 LLM（llama.cpp + GPTQ INT4）有效上下文有限，Token 预算 8000 是硬约束，压缩与逐出是必选项。
- **人力**（约束一）：1 人全栈 + AI 协作者。39 个文件的认知与维护负荷已偏重，需收敛核心子集（见 §4 Phase 0）。
- **交易路径隔离**（约束三/四）：miniQMT Tick=3 秒、日频及以上。CE 服务代码生成/审计等 AI 施工任务，不在交易低延迟路径上，同步 API 足够。
- **范式**（约束六）：AI 生成代码需交叉验证——CE 的 shadow 副本（G3 审计证据）与 integrity_check 即为此服务。

### 2.4 已施工设施盘点

验证命令：`Get-ChildItem -Recurse -Filter *.py src\zephyr\autonomy_core\context`（39 个文件）；各文件行数经 `(Get-Content).Count` 实测（总行数）；MATURITY 经头部 `[MATURITY]` 字段逐个提取。

#### 代码模块（39 个 .py，全部 [MATURITY] production）

| 类别 | 文件（行数） | 内容简述 |
|---|---|---|
| 流水线核心 | context_assembler.py（632） | 装配/压缩/G3 校验/影子副本 + build_context VMS 检索 |
| 流水线核心 | context_injector.py（485） | inject 三模式 API（生产返回空） |
| 流水线核心 | context_budget.py（385） | 预算配额 + 四种截断策略 |
| 流水线核心 | context_budget_tracker.py（338） | Token 预算追踪 + 三级阈值告警 |
| 流水线核心 | context_rot_model.py（266） | Context Rot 注意力衰减数学模型 |
| 流水线核心 | vector_bridge.py（224） | CE↔VMS 检索桥接（协议 + 5s 超时 + 降级） |
| 流水线核心 | context_pipeline_auto.py（205） | 三层自动化（自动启动/事件驱动/自动关闭） |
| 流水线核心 | context_rule_registry.py（199） | 按 task_type/tags/keywords 注入治理规则 |
| 流水线核心 | memory_bank.py（175） | 6 个结构化 .md 跨 session 持久上下文 |
| 流水线核心 | context_pipeline.py（173） | 四段组合根 run_context_four_stage |
| 流水线核心 | context_evictor.py（165） | 优先级×新鲜度×相关性三维逐出 |
| 治理辅助 | context_evaluator.py（78） | AI 引用率评估 |
| 治理辅助 | curation_loop.py（74） | Per-Turn 策展 |
| 治理辅助 | fallback_staleness_gate.py（70） | 兜底层自腐检测 |
| 工具/CLI | ce_file_lister.py（64） | CE 文件清单生成器 |
| 治理辅助 | context_outcome_tracker.py（63） | 因果链追踪 |
| 治理辅助 | checkpoint_manager.py（52） | Inject 前快照 |
| 工具/CLI | ce_bootstrap.py（55） | CE 自举（CE_MVP/FUNCTIONAL/FULL_CE 三级） |
| 治理辅助 | context_debt_score.py（46） | 上下文债务评分 |
| 工具/CLI | ce_explain_cli.py（44） | KE inclusion rationale 解释 CLI |
| 工具/CLI | ce_vibe_shortcuts.py（49） | Vibe/Strict 模式切换 |
| 治理辅助 | integrity_check.py（43） | 注入后完整性校验 |
| 治理辅助 | context_model_strategy.py（43） | 模型选择策略 |
| 治理辅助 | mode_manager.py（43） | 模式管理器 |
| 治理辅助 | diversity_constraint.py（41） | 多样性约束 |
| 包入口 | __init__.py（39） | 38 模块导出（无初始化逻辑） |
| 治理辅助 | staleness_manager.py（40） | 全局过期检测 |
| 治理辅助 | position_optimizer.py（40） | 注入位置优化 |
| 治理辅助 | domain_decay_config.py（41） | 每领域半衰期配置 |
| 治理辅助 | diff_injector.py（40） | 增量注入 |
| 治理辅助 | context_value_attribution.py（41） | KE 级 ROI 归因 |
| 治理辅助 | context_health_score.py（39） | 统一健康分 |
| 治理辅助 | complexity_budget.py（39） | Token 预算复杂度因子 |
| 治理辅助 | cold_start_booster.py（38） | 冷启动加速 |
| 治理辅助 | shadow_canary.py（38） | 金丝雀部署 |
| 接口骨架 | contextual_fetch_api.py（37） | GET /api/ce/session/{id} 骨架（硬编码返回） |
| 工具/实验 | context_playground.py（39） | 上下文沙箱 dry-run |
| 工具/实验 | ce_playground_v2.py（38） | V2 Playground（全决策链） |
| 流水线核心 | atomic_injector.py（35） | 原子注入（temp-file + os.replace） |

#### 配套组件与规则

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 基础设施 | `src/zephyr/infrastructure/capacity_assurance/token_budget.py` | Token 估算 SSoT：DEFAULT_CONTEXT_TOKEN_BUDGET=8000、estimate_tokens、三级配额 | production |
| 基础设施 | `src/zephyr/shared/io/doc_compressor.py` | DocCompressor 规则式压缩（CompressionPolicy 5 不变量） | production |
| 跨域依赖 | `src/zephyr/intelligence/model_evaluation/unified_memory_api.py` | UnifiedMemoryAPI（D_INTELLIGENCE）：recall/write/search，inject 段候选数据源 | production |
| 相邻治理 | `src/zephyr/governance/context_governance/` | 14 个 .py（含 __init__.py，13 个模块：context_manager/context_budget/prompt_lifecycle 等会话上下文治理，非本模块） | production |
| 测试 | `tests/context/` | 50 个 .py 测试文件 | production |
| 测试 | `tests/ce/` | 7 个 .py 测试文件 | production |
| 测试 | `tests/autonomy/`、`tests/cold/`、`tests/config/` | 71/5/10 个 .py（蓝图 §1.2 列出其中 21 个 CE 相关用例） | production |
| 脚本 | `scripts/context/generate_architecture_context.py` | 预编译 architecture-context.json（run_context_four_stage 可前置注入） | production |
| 蓝图 | `docs/03_modules/_cross_layer/context_engine/blueprint.md` | MOD-CONTEXT_ENGINE v1.1.3 集成索引（存在漂移，见 §6 Q7） | Active |
| 接口规范 | `docs/03_modules/_cross_layer/_b_track_interfaces/context_engine_interface.md` | CE 接口规范 v1.0.2：四段 API + MCP 通道矩阵 + 降级策略 | Active |
| 注册表 | `docs/03_modules/blueprint_registry.yaml`、`docs/03_modules/path_ownership_map.yaml` | MOD-CONTEXT_ENGINE 注册条目 | production |
| 资产盘点 | [02_design_asset_inventory.md](02_design_asset_inventory.md) | CE 资产一行式盘点（"部分实现"） | draft v0.3.0 |

---

## 3. 设计决策

### 3.1 为什么保留 build→compress→validate→inject 四段管道

**决策**：保留四段，以 `context_pipeline.py` 组合根为唯一显式编排入口。

**理由**：
1. **职责分离**：build 管"从哪来"（manifest + VMS 检索），compress 管"怎么瘦身"（DocCompressor + 逐出器），validate 管"能不能用"（G3 门禁），inject 管"补什么"（KB 知识注入）。边界清晰，单段可替换可独立测试。
2. **契约已固化**：`context_engine_interface.md` §4.1 将四段定义为 Protocol 级契约；`context_pipeline.py` 注释明确该组合根就是为了消除"Assembler ≠ 四段"的审计歧义而建。变更段数会破坏既有契约 CT-ORC-CE-001。
3. **与 Token 硬约束匹配**：8000 Token 预算下，无独立 compress 段则 build 产物直接溢出；无 validate 段则 G3 门禁无处挂载。

**考虑过的替代方案**：
- **两段（build→inject）**：否决——无 compress 则超预算；无 validate 则门禁缺失。这是 §4 过度工程审查的结论：四段对当前约束是必要的下限，非过度设计。
- **五段（增加 post-inject verify）**：否决——个人项目无需增加回环复杂度，integrity_check 已覆盖注入后校验。

### 3.2 与 D_INTELLIGENCE 的边界

**决策**：CE（D_AUTONOMY_CORE 域）= 上下文**注入管道**（装配/压缩/校验/注入）；D_INTELLIGENCE = 上下文**数据层**（知识存储/索引/检索）。二者经 `VMSSearchProtocol` 单向桥接。

**实测边界划分**：

| 职责 | Context Engine（D_AUTONOMY_CORE） | D_INTELLIGENCE |
|---|---|---|
| 数据流方向 | 消费端——从 VMS/文件系统拉取组装 | 供应端——知识条目写入与检索 |
| 代表模块 | context_assembler / vector_bridge / context_injector | unified_memory_api（MOD-INF-036） |
| 协议 | VMSSearchProtocol（只读检索协议） | ChromaDB 封装（recall/write/search） |
| Token 管控 | 预算/截断/逐出 | 不参与 |
| 生命周期 | 单任务级（session 内） | 跨任务持久化 |

另外注意区分第三块相邻设施：`src/zephyr/governance/context_governance/`（14 个 .py，含 __init__.py）是**会话上下文治理**（预算治理/切换治理/膨胀检测），属治理域，不是 CE 管道的一部分。三块设施职责互不重叠：数据层（D_INTELLIGENCE）→ 管道（CE）→ 治理（context_governance）。

### 3.3 压缩策略：摘要 vs 向量化 vs 关键词提取

**决策**：当前落地规则式压缩（DocCompressor）；llm_summary（本地小模型摘要）列为 Phase 1 增强；向量化不做为压缩手段。

**对比**：

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| 规则式（去 boilerplate + 首尾裁剪 + 保结构） | 零延迟、零显存、确定性、保留 provenance | 语义保真一般 | **当前落地**（DocCompressor） |
| LLM 摘要（本地 Qwen 分 slot 摘要） | 语义保真好 | 占显存、增加延迟、摘要本身可能幻觉（约束六需交叉验证） | Phase 1 增强，接口规范 §4.1 已预留 strategy 参数 |
| 关键词提取 | 快 | 丢上下文连贯性，代码场景不可用 | 否决 |
| 向量化（embedding 检索代替全文） | 适合大规模库 | 这是"检索"不是"压缩"；VMS 检索已在 build 段承担 | 不做为压缩手段（定位不同） |

**补充**：条目级"逐出"（context_evictor 三维加权）与内容级"压缩"（DocCompressor）在不同粒度工作，互补不互斥。

### 3.4 考虑过的替代方案（记录备查）

- **`InProcessContextEngine` 三源汇聚全量版**（接口规范 §4.1：VMS RRF multi_search + NetworkX entity-graph + 文件系统兜底 rg/grep）：当前仅落地 manifest + VMS 两源。entity-graph 依赖未建，列为远期（P4）。
- **HTTP API 服务化**（接口规范 §4.2 beta 骨架）：单机单人场景无需 HTTP 层，不启用（见 §5）。
- **多 IDE MCP 通道矩阵**（接口规范 §5：Cursor/Trae/Claude-Desktop 三通道）：当前施工方式仅 TRAE 单 IDE，全矩阵属远期。

### 3.5 Agent 记忆层（候选——分层记忆最小设计登记）

> 来源：草稿《Agent架构》§7.1~7.5（`.runtime/aidrafts/09_drafts_audit/架构图/Agent架构.md`）+《21-D-KNOWLEDGE》§10 知识库架构第 5 条与 A7 搬入段 +《12-D-ML-TRAIN》§A7（LP-002）。本节为**设计候选登记**：四层中情景/语义/程序三层是跨会话持久层，与 §5 第 2 条"不做跨会话长期记忆"的既有边界存在冲突——本节不擅自改动 §5，冲突登记为 §6 Q9 待 Owner 裁定。

**四层记忆模型**（2025-2026 行业共识 Mem0/Letta/LangMem/Zep 等，单机 Redis+SQLite+Parquet 轻量落地）：

| 层 | 存储 | 生命周期/保留策略 | 容量约束 | 用途 | 对应域 |
|---|---|---|---|---|---|
| 工作记忆 | Redis（内存） | 单次会话，会话结束清空 | 上下文窗口 4K-32K tokens；窗口使用 >80% 触发摘要压缩（压缩早期对话、保留关键决策点） | 当前对话上下文、中间推理步骤、临时计算结果 | D-INFRA-RUNTIME |
| 情景记忆 | Redis 热区 + SQLite 温区 | 90 天热 → 1 年温 → 7 年冷（Parquet） | 热区近 1000 条决策轨迹 | 决策轨迹、反思记录、异常事件日志 | D-AUTONOMY-CORE |
| 语义记忆 | SQLite + Parquet | 永久保留，版本化管理 | 无硬上限 | 市场知识、因子定义、策略规则、用户偏好 | D-KNOWLEDGE |
| 程序记忆 | 文件系统（SKILL.md + scripts/） | 版本化保留，旧版保留 ≥5 年 | 技能库（草稿口径 28 项，本文未实测） | 技能模板、成功模式、执行流程、最佳实践 | D-AUTONOMY-CORE |

**巩固 / 去重 / 五阶段流水线**（巩固去重参考 LangMem 与 AgentDock；五阶段参考 CoALA/TMLR 2024、Mem0/Letta/Zep 生产实践）：

- **巩固（情景→语义固化）**：同类事件出现 ≥3 次 → 提取共性事实写入语义记忆（草稿示例："连续 3 次该因子在震荡市 IC<0.01"→"该因子在震荡市无效"）。
- **去重**：语义记忆新增时向量相似度检测，相似度 >0.95 合并（区别于信号去重阈值 >0.9）。
- **五阶段流水线**：①写入（原始交互入工作记忆，Redis 实时）→ ②抽取（LLM 提取关键事实/模式入语义记忆 SQLite）→ ③整合（>0.95 去重 + 冲突解决 + 时间戳版本化）→ ④检索（按相关性召回：FAISS 向量检索 + SQLite 结构化查询）→ ⑤遗忘（90 天热→1 年温→7 年冷分级衰减）。

**记忆安全约束**（草稿 §7.5）：

- 敏感数据（持仓/金额/交易记录）不写入任何记忆层，写入前脱敏过滤；
- 情景记忆写入后**不可篡改**（不可变日志 + 哈希校验，仅可追加反思）；
- **跨层一致性**：同一事实在情景/语义/程序记忆中不可矛盾，写入时做跨层一致性检查；
- 情景记忆 **RPO=0**（崩溃后可从 Parquet 冷存储恢复），语义记忆定期快照。

**风险警示**：Databricks 2026-04 研究——无策展的记忆会把一次性错误固化成"永久谎言"（Agent 引用既往运行的错误输出，再以更高信心复用）。草稿的缓解路径是自反 Agent 反思机制 + 上述巩固去重；落到 CE 语境，对应 §3.3 压缩保 provenance 与 validate 段校验职责——记忆写入链不经策展/校验即入库即为此风险的具象化。

**硬件约束注记**（12-D-ML-TRAIN §A7 LP-002 / 21-D-KNOWLEDGE LP 段裁定）：Agent 记忆向量检索（RAG）判"暂缓（不能建）"——嵌入模型约需 2GB 显存，挤占盘中 8-10GB 本地 LLM 配额，且量化系统记忆核心是结构化数据而非自然语言。MVP 替代：SQLite FTS5 全文检索 + Redis 缓存，语义记忆用结构化表（因子定义/策略规则/市场状态映射）。故上表"FAISS 向量检索"在硬件门禁（GPU 显存 ≥48GB 等 LP-002 门禁条件）解除前降级为 FTS5。

**与 CE 既有设计的关系**：工作记忆的">80% 摘要压缩"与 §3.3 压缩策略同族（压缩对象从 manifest 文档扩展到会话历史）；memory_bank.py（6 个结构化 .md 跨 session 持久上下文）是分层记忆的最小既有实现，可视为语义/情景记忆的纯手工雏形。是否将四层记忆从候选升级为施工范围，以及升级后的域归属（CE 管道 / D-AUTONOMY-CORE / D-KNOWLEDGE 分层承接），统一由 §6 Q9 裁定。

---

## 4. 施工计划

> 组织方式：目标→现状→改动→验证（01 号规范 §4.4 施工类）。
> **depgraph 守门**：本计划不新建模块——全部改动在 MOD-CONTEXT_ENGINE 既有落位（`src/zephyr/autonomy_core/context/`）内补缺/整合。若任何步骤演变为新建模块，必须先 `apply_depgraph` 登记设计态（status=planned），验收通过后转 production，禁止先施工后补登记。

### Phase 0：对齐收口（消除漂移，0~2 周）

**目标**：蓝图/文档/代码三方一致，明确维护范围。
**现状**：蓝图声称 22 文件/partially_implemented/§1.1 仅 1 行；实际 39 文件/production。
**改动**：

| # | 步骤 | 优先级 |
|---|---|---|
| P0-1 | 核对 depgraph 中 MOD-CONTEXT_ENGINE 节点与依赖边（对 VMS/TaskSystem/LSG/AutoRuntime 四条依赖）是否与蓝图 §依赖关系一致；缺失则用 apply_depgraph 补登（status=planned） | P0 |
| P0-2 | 发起蓝图同步（蓝图不在本文修改权限内，提交流程见 §6 Q7）：文件清单 22→39、construction_progress 修正、§1.1 索引重生成 | P0 |
| P0-3 | 标记核心子集 15 文件（见下）vs 辅助/候选废弃 24 文件：不删除，仅在蓝图标注维护优先级 | P1 |
| P0-4 | 跑通既有测试基线：`tests/context/`（50 个）+ `tests/ce/`（7 个）+ 蓝图 §1.2 列出的 autonomy/cold/config 用例 | P0 |

**核心子集（15）**：context_pipeline、context_assembler、context_injector、context_budget、context_budget_tracker、context_evictor、vector_bridge、context_pipeline_auto、memory_bank、context_rule_registry、integrity_check、checkpoint_manager、atomic_injector、ce_bootstrap、\_\_init\_\_。
**辅助/候选废弃（24）**：context_rot_model、context_evaluator、curation_loop、fallback_staleness_gate、ce_file_lister、context_outcome_tracker、context_debt_score、ce_explain_cli、ce_vibe_shortcuts、context_model_strategy、mode_manager、diversity_constraint、staleness_manager、position_optimizer、domain_decay_config、diff_injector、context_value_attribution、context_health_score、complexity_budget、cold_start_booster、shadow_canary、contextual_fetch_api、context_playground、ce_playground_v2。

**验证**：蓝图 §1.1 与磁盘 `Get-ChildItem` 输出一致；测试基线全绿。

### Phase 1：补缺（inject 接线 + 压缩增强，2~4 周）

**目标**：inject 段从空占位升级为可用；压缩从单档升级为三档降级。
**现状**：inject_by_* 返回空；DocCompressor 仅规则式。
**改动**：

| # | 步骤 | 优先级 |
|---|---|---|
| P1-1 | inject 接线：将 `ContextInjector` 数据源接至 `UnifiedMemoryAPI`（D_INTELLIGENCE，经 VMSSearchProtocol 协议注入，不跨域硬编码）；`inject_by_keyword()` 返回非空 InjectedContext（含 sources + provenances）。前置裁定：§6 Q6 | P1 |
| P1-2 | 压缩三档：llm_summary（本地 Qwen INT4 分 slot 摘要）→ rule_based（现状）→ truncate 降级链；摘要结果须经 integrity_check 校验后方可替换原文（约束六交叉验证） | P2 |
| P1-3 | 接口规范 §4.1 sync/async 偏差裁定：维持 sync 主用 + 按需 async wrapper，或升级 async——决策记录回填本文 §3 | P2 |

**验证**：`inject_by_keyword` 集成测试非空且 provenance 可解析；三档压缩各有测试用例；预算超限场景端到端测试通过。

### Phase 2：集成接线（依赖 04/10/14 填充后，4~6 周）

**目标**：CE 与运行时底座、LLM 基础设施、执行层双向对齐。
**现状**：04 v0.2.1 / 10 v0.2.2 / 14 v0.2.0 均已填充（2026-08-17 接口复审实测）；Q2 经 04 §3.5 双向对齐判部分成立，Q3/Q4 判证伪——CE 产出（final_context）目前无下游契约承接方，契约归属待 Owner 裁定（§6 Q2~Q4）。
**改动**：

| # | 步骤 | 优先级 |
|---|---|---|
| P2-1 | 与 14_execution_layer.md 对齐：确认业务 Agent 经 Orchestrator 以 `TaskCard.context_assembly_manifest` 触发 `run_context_four_stage()` 的消费链（CT-ORC-CE-001）；该消费链在 14 v0.2.0 中实测不存在，前置裁定：§6 Q4 | P1 |
| P2-2 | 与 10_llm_infrastructure.md 对齐：定义 final_context 到 LLM prompt 的传递契约（system/user 分配、预算扣减顺序）；10 v0.2.2 实测无 final_context 承接，前置裁定：§6 Q3 | P1 |
| P2-3 | 与 04_autoruntime_core_build.md 对齐：04 §3.5 已确认 boot 触发注册 + EventBus 事件驱动（非逐任务调度）；剩余缺口为 boot_hooks.py 未 import CE 的实际接线（§6 Q2） | P2 |
| P2-4 | 压缩后 provenance 自动化校验入 validate 段（source_traces 可解析 + stale 标记） | P1 |

**验证**：04/10/14 填充文档与本节接口描述双向一致；新增校验用例入 tests/context/。

### Phase 3：远期演进（P4，仅登记不施工）

- MCP 通道注入（接口规范 §5 IDE 能力矩阵，当前仅 TRAE 单通道需要）。
- entity-graph 第三源汇聚（接口规范 §4.1 build 全量版）。
- contextual_fetch_api 从硬编码骨架升级为真实 session 查询。

---

## 5. 不做什么

1. **不做通用对话记忆**——CE 仅服务量化交易相关的代码生成/审计/策略分析任务上下文，不做开放域聊天式对话管理。
2. **不做跨会话长期记忆**——单会话内上下文归 CE；跨会话长期记忆由技能库/证据库/memory_bank（6 个结构化 .md）负责，CE 不扩展为通用记忆系统。（注：§3.5 登记的四层记忆候选与该条存在张力，是否突破由 §6 Q9 裁定，本条在裁定前维持有效。）
3. **不做多模态上下文**——仅处理文本（代码/markdown/日志），图表/音频/视频不在范围。
4. **不做 HTTP API 服务化**——接口规范 §4.2 的 HTTP 骨架不启用；单机单人场景 Python 库调用足够。
5. **不做多 IDE MCP 通道全矩阵**——当前施工方式仅 TRAE 单 IDE；Cursor/Claude-Desktop 通道列远期。
6. **不做分布式上下文同步**——单机文件锁 + 单会话上下文足够，不引入 Redis/Kafka。
7. **不做自动上下文猜测**——manifest 必须由人类或上层 Agent 显式指定，CE 不主动猜测用户意图。
8. **不新建模块/子包**——39 个文件已偏多，Phase 0 只做标记收敛，物理删除需 Owner 裁定（§6 Q5）。
9. **不替 04/10/14 号文档定接口**——三者均已填充（04 v0.2.1 / 10 v0.2.2 / 14 v0.2.0）；Q2 已与 04 双向对齐（部分成立），Q3/Q4 证伪后契约归属待 Owner 裁定（§6 Q3/Q4），本文不擅自补定。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | Context Engine 与 D_INTELLIGENCE 的关系？ | 待裁定 | 边界已在 §3.2 按实测划分（CE=注入管道/D_INTELLIGENCE=数据层，经 VMSSearchProtocol 单向桥接）。遗留点：`vector_bridge.py` 是否应物理迁移到 D_INTELLIGENCE 域，需 Owner 裁定。 |
| Q2 | CE 与 04 AutoRuntime Core 的接口？ | 部分成立（2026-08-17 接口复审） | 04 号文 v0.2.1 §3.5 已将本文原假设精确化并双向确认：大脑角色为 **boot 触发注册方 + EventBus 事件驱动订阅源**，不逐任务编排四段流水线；蓝图 references"大脑消费上下文注入"成立。**实测缺口**：`context_pipeline_auto.py` 头部 [CONSUMERS] 声明 `zephyr.trading.boot_hooks`，但实测 `boot_hooks.py` 存在却未 import CE（[CONSUMERS] 声明漂移，src 内亦无其他消费方 import 本模块）——事件驱动机制代码 production、boot 触发链当前无实际接线。接线归属（04 侧补接 vs 蓝图/头部声明修正）待 Owner 裁定。 |
| Q3 | CE 与 10 LLM 基础设施的上下文传递契约？ | 已证伪（2026-08-17 接口复审），契约归属待 Owner 裁定 | 10 号文 v0.2.2 已填充，全文实测无 `final_context`/`ContextFourStageResult`/`run_context_four_stage` 承接——原接口假设不成立。CE 产出（final_context）目前无下游契约承接方，与 Q4 同为 18 篇中唯一"接口无人认领"区。归属候选：07 自定义 / 10 门面承接 / 14 消费链定义。 |
| Q4 | CE 与 14 执行层业务 Agent 的消费接口？ | 已证伪（2026-08-17 接口复审），契约归属待 Owner 裁定 | 14 号文 v0.2.0 已填充，全文实测无 `TaskCard.context_assembly_manifest` 触发链、无 `run_context_four_stage()`/`final_context` 消费链——原接口假设（CT-ORC-CE-001 消费方）不成立。同 Q3：归属候选 07 自定义 / 10 门面承接 / 14 消费链定义。 |
| Q5 | 24 个辅助文件是否物理删除？ | 待裁定 | Phase 0 建议仅标记 deprecated_candidate 不删除。若 Owner 确认 playground/CLI 类永不再用，可物理删除以减维护面。 |
| Q6 | inject 空占位的修复优先级？ | 待裁定 | inject_by_* 生产返回空（实测源码注释确认）。修复需接 UnifiedMemoryAPI。若 14 号业务 Agent 仅消费 manifest 组装结果，inject 可继续为空——优先级取决于 14 号填充结论。 |
| Q8 | doc_type 词表不合规阻断 Gateway 提交？ | 已闭环（2026-08-17） | frontmatter `doc_type` 已迁移为受控词表内 `architecture_view`，v0.2.2 已经 Gateway 提交（commit e9087fa902）。原"暂存待提交"表述作废。 |
| Q7 | 蓝图漂移同步责任与机制？ | 待裁定 | MOD-CONTEXT_ENGINE 蓝图 v1.1.3 实测漂移：22 vs 39 文件、§1.1 索引仅列 `__init__.py`、build_status=planned vs 代码全 production、[CONSUMERS] 声称的 zephyr.trading.boot_hooks 实测存在但未 import 本模块。蓝图不在本文修改权限内——需裁定由谁同步、是否改为 depgraph 单向派生。 |
| Q9 | §3.5 四层记忆候选是否突破 §5"不做跨会话长期记忆"边界？ | 待裁定 | §3.5 登记的四层记忆中情景/语义/程序三层为跨会话持久层，与 §5 第 2 条既有边界冲突。选项：A. 维持 §5，§3.5 降级为远期参考（P4 登记）；B. 将记忆层纳入施工范围——需同时裁定域归属（CE 管道 / D-AUTONOMY-CORE / D-KNOWLEDGE 分层承接）与硬件门禁（LP-002：RAG 向量检索暂缓，FTS5+Redis MVP 替代）。裁定前 §5 第 2 条维持有效。 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 填充 §2 背景（处境/核心问题/约束/39 文件设施盘点）、§3 设计决策（四段管道/D_INTELLIGENCE 边界/压缩策略/替代方案）、§4 施工计划（Phase 0~3）、§5 不做什么、§6 开放问题（Q1~Q7） | AI-FILL-07 首轮骨架填充；实测修正"22 文件"为 39 文件、inject 空占位、蓝图漂移等关键事实 |
| 2026-08-17 | 0.2.2 | 新增 Q8：Gateway 提交被 TTL-METADATA 门禁阻断（doc_type=implementation_plan 不在受控词表 9 值内），文件暂存待 Owner 裁定词表后提交；去除文件 BOM 以通过 frontmatter 解析 | AI-FILL-07 git 提交闭环执行结果：门禁 hard block，按规则 7 降级为暂存+标注 |
| 2026-08-17 | 0.2.1 | 红蓝对抗修正：文件行数统一更正为总行数口径（(Get-Content).Count）；boot_hooks.py 存在性误判更正（文件存在但未 import CE，属 [CONSUMERS] 漂移）；context_governance 文件数 13→14（含 __init__.py）；修复 system_charter.md 相对链接层级 | AI-FILL-07 第 5/6/7 轮审查发现的事实性偏差 |
| 2026-08-17 | 0.3.0 | §3.5 新增 Agent 记忆四层候选登记（工作/情景/语义/程序 + 巩固≥3次固化 + 去重>0.95 + 五阶段流水线 + 记忆安全约束 + Databricks 2026 无策展警示 + LP-002 硬件门禁 FTS5 降级）；§2.2 补记忆 vs 知识域边界注记（21-D-KNOWLEDGE §0/§6）；接口复审回填：Q2 部分成立（04 §3.5 精确化 + boot_hooks 未接线漂移登记）、Q3/Q4 证伪（10/14 无 CE 产出承接）、Q8 闭环、新增 Q9（记忆候选 vs §5 边界）；§1/§4 Phase 2/§5-2/§5-9 同步实测口径 | AI-FILL-07-R2 回填：草稿源（Agent架构 §7.1~7.5 / 21-D-KNOWLEDGE §10 第5条·A7 段 / 12-D-ML-TRAIN §A7）+ 04/10/14 接口复审实测 |

---

*维护者：AI 架构协调者*