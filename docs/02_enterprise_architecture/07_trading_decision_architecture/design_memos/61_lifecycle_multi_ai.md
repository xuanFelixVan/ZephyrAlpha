---
ttl: permanent
doc_type: architecture_view
title: 策略生命周期与多 AI 协作
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.13.1"
date: 2026-08-12
topic: lifecycle_multi_ai
scope: 07_trading_decision_architecture
---

# 策略生命周期与多 AI 协作

> 本备忘记录策略从孵化到退役的完整生命周期规范，以及多 AI 协作的分工与交接纪律。
> 性质：永久态设计记录，可随项目演进而修订，不是不可推翻的裁定。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G28 策略生命周期与多 AI 协作 |
| 所属 | 跨作战地图 01/02/03/04/10/11 |
| 依赖 | 全局（生命周期贯穿全流程） |
| 对标 | MLOps 生命周期 / Champion-Challenger 晋升 / 机构策略研发流程 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3（治理类，可后置） |
| 状态 | ✅ 已定稿 |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发：用户开启多个 AI 会话，每个会话认领一个主题组（G01-G28）并行推进
- 当前"多 AI"实质是 **单 AI 多会话** + **另一 AI 独立做 regime**——不是多 agent 运行时编排系统
- 策略从想法到退役要跨 6 个作战地图阶段（01 孵化→02 训练→03 回测→04 模拟→10 实盘→11 对账退役），每阶段有独立的 why 层空白
- 00_index 已建立段位编号制（0x-9x）与骨架先行工作流（最新篇数与状态台账以 [00_index_trading_decision](00_index_trading_decision.md) §0 目录为准——v2.3.0 时 38 篇 = 15 active/draft + 23 骨架，后续有新增占用），需在本备忘锁定生命周期各阶段的文档治理衔接

### 2.2 核心问题
策略生命周期 6 阶段跨越多个作战地图，每阶段都有"准入门禁→运行监控→降级/晋升→退出"的流转，但缺少一份跨阶段的总纲把 6 阶段串成一条状态机。同时多 AI 协作需要明确分工与交接纪律，防止"AI 间不直接通信"原则下出现交接断裂。

### 2.3 约束条件
- 个人项目：无团队协作平台（无 Jira/Confluence），交接靠文档（design_memo）+ 代码注册表（depgraph）
- AI 开发：每个会话独立上下文，不能假设"上一个 AI 留了什么在内存里"——所有交接必须落盘
- 治理硬约束：模块创建必须生成 creation_token + 登记 capability_canonical_file_registry.yaml + module_translation_registry.yaml + architecture_issue_registry.yaml（ARCH 条目）
- 不做 agent 编排系统：30_multi_strategy §5 已暂缓"LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索"，多 AI 协作是"人调度多会话"非"agent 自治"

### 2.4 已施工设施盘点

> 通用规则 #11：先清楚有什么 → 才能知道怎么改 → 才能知道该删除/退役什么。本节盘点与本备忘主题（策略生命周期 + 多 AI 协作）相关的全部已建设施与配套（代码/注册表验证 2026-08-12）。

| 设施 | 路径 / 位置 | 施工状态 | 与本备忘关系 |
|---|---|---|---|
| 三阶段迁移门禁 | `src/zephyr/governance/lifecycle_governance/paper_live_transition.py`（MOD-GOVERNANCE） | ✅ production | §3.1 状态机 ④模拟→⑤实盘 的阶段门禁承载（PARALLEL/SHADOW/GRAY_RAMP，53 号 G24 真源） |
| 回测门控 + 偏差监控 | `src/zephyr/backtest/core/decision_gate.py` | ✅ production | §3.4 回测阶段准入门禁（IS→WFA→OOS + 参数悬崖检测 + `monitor_backtest_live_deviation` warn>30%/retire>50%） |
| rolling DSR | `src/zephyr/simulation/deflated_sharpe_calculator.py`（MOD-SIM-024） | ✅ production | §3.3 漂移 vs 过拟合鉴别（DSR 排除过拟合）+ §3.4 过拟合检测维度 |
| 前瞻偏差检测 | `src/zephyr/simulation/look_ahead_bias_detector.py`（MOD-SIM-022） | ✅ production | §3.2 PIT 铁律 + §3.4 回测可信硬底线的检测层 |
| 实验追踪 | `src/zephyr/experiment_tracking/`（config/models/query）+ [50_backtest_observability_workplan](50_backtest_observability_workplan.md)（draft v1.0.2，MLflow 体系调研已定） | 代码已有，体系 draft | §3.2 第 3 条可复现性（四要素记录）+ §3.3 Champion-Challenger 的 MLflow alias 生命周期（@champion/@challenger/@archived） |
| 系统级生命周期管理器 | `src/zephyr/trading/lifecycle_manager.py`（BootReport/ShutdownReport） | ✅ production | ⚠️是**系统启动/关闭**生命周期（进程级），**非策略生命周期**——与 D-SIGNAL-14 7 状态无对应关系，勿混淆 |
| D-SIGNAL-14 策略状态机 | [battle_map_12](../battle_map/battle_map_12_cross_cutting.md) 横切条目（研发/测试/灰度/生产/观察/废弃/归档） | 设计态（无独立代码） | §3.1 状态机映射真源；个人项目用 design_memo status + depgraph build_status 双字段替代（§4.3） |
| depgraph 治理脚本 | `scripts/governance/apply_depgraph.py` / `sync_panorama_module.py` / `d5_architecture/generators/align_panoramas.py` | ✅ production（含 commit gate：depgraph_pre_registration_gate / depgraph_freshness_gate / panorama_alignment_gate 等） | §3.8 模块创建 4 步的执行工具链 |
| 治理注册表 | `capability_canonical_file_registry.yaml` / `module_translation_registry.yaml` / `architecture_issue_registry.yaml` / `candidate_module_registry.yaml` | ✅ 运营中 | §3.8 creation_token 登记 + ARCH/CAND 分流纪律的载体 |
| 退役归档目录 | `strategy_archive/<strategy_id>/` | ❌ 设计态（未建，待首个退役策略触发时施工） | §3.9 归档四件套第④条的物理终点 |
| 多 AI 协作交接 | design_memo 产出物 + depgraph path + 00_index §7.3 占用表 | ✅ 运营中（人调度多会话） | §3.6 交接纪律的载体（无 agent 编排系统） |
| 漂移检测/退役监控 | 本备忘 §3.3 Drift Observatory / §3.9 退役量化阈值 | ⚠️设计规范伪代码（mSPRT/四层编排/退役 5 步），代码待施工 | G28 核心设计产出，待 55 号（G26 骨架）定型后落地告警联动 |
| 市场仿真域 | `simulation/` 15 模块（[71_d_simulation](../../02_domain_architecture_docs/71_d_simulation.md)） | ✅ production | §3.5 模拟阶段的市场仿真侧（what-if，≠paper trading；BM-SIM-05 数字孪生已降级 #ARCH-OE-010） |
| 模拟→实盘迁移路径 | [53_simulation_live_path](53_simulation_live_path.md)（active）+ §2.4 设施盘点 | ✅ 已定稿 | §3.1 ④模拟→⑤实盘 的迁移路径承接（PARALLEL/SHADOW/GRAY_RAMP 门禁 + 灰度上线） |
## 3. 决策

### 3.1 策略生命周期 6 阶段状态机

> 一个策略从想法到退役，经历 6 个阶段，每阶段有准入门禁与退出条件。状态机对齐 D-SIGNAL-14 Lifecycle Manager 的 7 状态（研发/测试/灰度/生产/观察/废弃/归档，真源条目见 [battle_map_12_cross_cutting](../battle_map/battle_map_12_cross_cutting.md) §跨切横切表；⚠️当前无独立代码实现，个人项目用 design_memo status + depgraph build_status 双字段替代，见 §4.3 简化方案）。

| 阶段 | 作战地图 | 状态机映射 | 准入门禁 | 退出条件 | 关键环节 |
|---|---|---|---|---|---|
| ① 孵化 | 01 (BM-RES) | 研发 | 假设登记（BM-RES-03）+ 知识沉淀 | 策略规格产出 + 模块工厂匹配（BM-RES-10） | BM-RES-01 数据特征→BM-RES-02 实验追踪→BM-RES-03 假设→BM-RES-06 LLM Agent→BM-RES-07 策略迭代 |
| ② 训练 | 02 (BM-MT) | 测试 | 孵化产出的策略规格 + 训练基座（BM-MT-01-A） | 模型通过 Champion-Challenger 晋升（BM-MT-02） | BM-MT-01 训练流水线→BM-MT-02 实验追踪晋升→BM-MT-03 AutoML→BM-MT-04 因子发现→BM-MT-05 漂移检测 |
| ③ 回测 | 03 (BM-BT) | 测试 | 训练产出的模型 + PIT 正确特征 | IS→WFA→OOS 全过 + 过拟合检测三维度通过 + Deflated Sharpe 通过 | BM-BT-01~07（详见 52_backtest_framework_docking） |
| ④ 模拟 | 04 (BM-SIM) | 灰度 | 回测通过 + 模拟环境就绪 | 模拟时长达标 + sim↔实盘 divergence 可接受 | paper/shadow 模式（battle_map_12 四模式开关） |
| ⑤ 实盘 | 10 (BM-EXE) | 生产 | 模拟通过 + 上线审批 + 冷启动协议（BM-MT-02 v3.5） | 连续跑输 / 逻辑失效 → 进入观察 | BM-EXE-01/02（40_execution_broker 已施工） |
| ⑥ 退役 | 11 (BM-REC) | 观察→废弃→归档 | 实盘触发退役标准（G26） | 归档到策略归档区（§3.9 策略归档机制：MLflow @archived + design_memo deprecated + strategy_archive/ 目录） | BM-REC 对账归因 + D-SIGNAL-14 废弃审批 |

**冷启动协议**（BM-MT-02 v3.5）：新策略上线后观察期 + 渐进建仓，仓位上限 = 正常 × 30%，风控驱动与市场无关，可与分批建仓叠加。这是 ④模拟→⑤实盘 的过渡机制。

**渐进建仓节奏细化**（2026-08 补充）：冷启动不是一次性给 30% 然后跳到 100%，而是按**时间+表现双门控**阶梯式放量（[youngju.dev 2026-03](https://www.youngju.dev/blog/ai-platform/2026-03-04-ai-platform-model-registry-ab-deploy-2026)：渐进流量梯度；[kindatechnical 2026-03](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)：post-deployment monitoring）：
| 阶段 | 仓位上限 | 持续时长 | 晋升门控 |
|---|---|---|---|
| **T0 观察** | 正常 × 30% | 5-10 个交易日 | 无重大偏离（实盘 vs 模拟 divergence < 阈值）+ 风控未触发降级 |
| **T1 小仓** | 正常 × 60% | 10-20 个交易日 | T0 期间 Rolling Sharpe ≥ 回测 OOS Sharpe × 0.7 + 无连续 3 日亏损超限 |
| **T2 常规** | 正常 × 100% | — | T1 期间 Rolling Sharpe ≥ 回测 OOS Sharpe × 0.85 + Decay Detection 5 监控点无告警 |

任一阶段门控未达标 → **回退上一阶段**（T2 回 T1，T1 回 T0，T0 回退到模拟阶段）；连续 2 次回退 → 进入 §3.9 退役阶段量化标准。**冷启动期间暂停重训练**——冷启动数据不足以判断"漂移"还是"正常波动"，等 T2 常规阶段后再启用漂移检测触发重训练。

### 3.2 研究孵化阶段（BM-RES）规范

承接 [battle_map_01_research_incubation](../battle_map/battle_map_01_research_incubation.md)（33 环节，17 锚点）：

**核心纪律**：
1. **PIT 铁律**（BM-RES-01-B）：特征分在线/离线双套存，拉特征只返回当时已知值，绝不偷看未来——回测可信的硬底线。Feature Store 不可用 → 回退原始数据直算（无 PIT，仅探索用，禁止入回测）
2. **假设驱动**（BM-RES-03）：研究不是瞎试——每个想法写成假设挂证据，状态机 提出→验证→接受/拒绝 全程留痕，防止灵感流失与重复造轮子
3. **可复现性**（BM-RES-02）：超参 + 数据版本 + 代码 commit + 随机种子四要素完整记录，是一键复现的硬门禁
4. **模块工厂**（BM-RES-10）：研究发现映射到现有模块（复用），找不到则标准 4 步创建（创建→注册→接入→验证），不手动搬代码

> **策略规格产出物**（§3.1 ①孵化阶段退出条件"策略规格产出"的承接）：以 [20_first_batch_strategies](20_first_batch_strategies.md)（G04，active）为首批范式——sleeve 定位 / 容量测算 / 持仓周期 / 风控参数四要素齐备才算"规格产出"，方可进入 ② 训练阶段。

**当前状态**：BM-RES-01（数据特征存储）已运营态；BM-RES-02/06/07 设计态待施工；BM-RES-03/04/05/08/09/10/11 缺失态（无锚点，BM-INV-001 违例）。

**研究知识流水线拍板**（2026-08-12 作战地图全覆盖补丁，一次拍板闭合 §7.2 登记的 BM-RES-03/08/09 缺失态待定问题）：

1. **BM-RES-03-B 研究发现知识库**（design）→ **轻量建设：Markdown+Git+frontmatter 标签检索**。定位：假设被接受/研究发现产出后的知识沉淀环节（下游 D-KNOWLEDGE）。裁定：不上 SQLite/Neo4j/ChromaDB 独立知识库——个人项目知识条目量级（数十至数百条）用 Markdown 文件 + Git 版本化 + frontmatter 标签检索足够，呼应 §7.2"Markdown+Git 替代独立系统"既定思路；向量检索属过度工程，重评条件：知识条目 >500 且关键词检索失效。契约（建设项）：知识条目以单文件 Markdown 存于研究知识目录，frontmatter 模板四字段必填——`hypothesis`（假设陈述）/ `evidence`（证据列表：回测结果/数据切片/文献出处）/ `conclusion`（接受/拒绝+理由）/ `tags`（关联因子/策略标签，对接 §3.2 第 2 条假设状态机）；条目生命周期随假设状态机流转（提出→验证→接受/拒绝 全程留痕即知识沉淀）。
2. **BM-RES-08 知识清洗与结构化 + BM-RES-08-A 知识清洗流水线**（design）→ **轻量建设：LLM 单次抽取 + Markdown 结构化模板承载**。定位：原始研究材料（论文/研报/新闻文本）→清洗→结构化→沉淀 BM-RES-03 假设。裁定：不上独立 NLP 清洗栈（实体抽取/关系抽取/语义去重工程对个人项目过重）；清洗四动作（去重/去噪/实体链接/质量评分）由"LLM 单次抽取 + Markdown 结构化模板"承载——LLM 一次性输出结构化条目，人工复核后入库；重评条件：日采集量 >50 篇且人工复核成为瓶颈。契约（建设项）：Markdown 结构化模板字段——`source`（来源+时间+置信度元数据）/ `dedup_key`（标题哈希，承载去重）/ `entities`（实体链接：关联因子/策略/标的标签）/ `quality_score`（LLM 自评 1-5 + 人工复核标记）；去重=标题哈希比对（Git 已有历史），去噪=quality_score <3 不入库，与 BM-RES-03-B 条目模板共用 frontmatter 规范。
3. **BM-RES-09 知识分类与策略提取 + BM-RES-09-A 知识类型分类体系**（design）→ **轻量建设：frontmatter 标签承载 5 类知识**。定位：结构化知识→按类型分类→策略提取→BM-RES-07 策略迭代。裁定：知识类型分类体系（原定义 5 类：事实型/规则型/策略型/案例型/元知识型）由 frontmatter `knowledge_type` 单字段承载，不建独立分类模型/置信度体系；策略提取=人工阅读 `knowledge_type=strategy` 条目后走 §3.2 第 2 条假设登记进入状态机——分类体系与假设状态机直接衔接，无中间层。重评条件：知识条目 >500 且人工分类不一致。契约（建设项）：frontmatter `knowledge_type` 枚举 `fact/rule/strategy/case/meta` 必填；策略提取产出物=假设登记条目（`knowledge_type=strategy` 条目引用 + 假设陈述），走 §3.2 第 2 条状态机。

**研究环境否定式裁定**（2026-08-12 作战地图全覆盖补丁，否定式裁定闭合 4 个 BM-RES 环境/编排环节）：

1. **BM-RES-01-C 研究数据沙箱**（design）→ **裁定不建设容器沙箱**。定位：研究隔离环境（container/vm/process 三级隔离原设计）。裁定：研究隔离 = venv/目录级隔离 + 审计日志——与 [65_git_safety_governance](65_git_safety_governance.md) §9"不引入沙箱/容器隔离"裁定呼应（Windows 无 macOS Seatbelt 等效物，Docker/WSL 对量化交易开发过重）；个人单研究员无多租户隔离需求，venv 依赖隔离 + 研究目录与生产目录物理分离 + Git 审计日志已覆盖"数据隔离+代码隔离"诉求；资源隔离（CPU/内存限额）无需求（单机研究任务错峰人工调度）。重评条件：引入不可信第三方代码/数据需隔离执行时。
2. **BM-RES-05-A Notebook 集成与一键转生产**（design）→ **裁定不建设**。定位：JupyterLab + papermill 参数化执行 + 一键转生产管线。裁定：研究环境 = VSCode + 纯 Python 脚本，不建 JupyterLab/papermill——个人项目现实：AI 会话直接产出 .py 脚本（非交互式 notebook 探索），"一键转生产"诉求由 §3.8 模块创建 4 步（创建→注册→接入→验证）承载，脚本即生产形态无需转换层。BM-RES-05 父环节（Notebook 与协作）协作侧由 §3.6 多 AI 协作分工承载（design_memo 产出物 + depgraph path 交接，"AI 间不直接通信"纪律），notebook_backend/collaboration_mode 参数随之消解。重评条件：无（除非研究模式转向交互式探索驱动）。
3. **BM-RES-04 研究工作流编排 + BM-RES-04-A DAG 编排与任务调度**（production/design）→ **裁定不建 Prefect 级编排**。定位：假设接受后触发研究工作流 DAG（任务调度/依赖解析/重试/并行）。裁定：研究工作流 = 人工串联 + [64_data_source_download_spec](64_data_source_download_spec.md) §6.4 调度基座复用——APScheduler 常驻进程 + task_queue DAG 依赖管理 + 指数退避重试 + 降级告警已是 production（数据下载域 15 时段条目运营中），研究侧定时任务（如论文追踪定时爬取）直接复用该基座登记新 DAG 节点即可，不另建 Prefect/Airflow 级编排；§4.2 已拒绝 KFP 企业级编排栈，本节补研究域的完整闭环（拒绝理由同 §4.2：个人项目无 K8s 运维能力）。重评条件：研究工作流 >10 节点且人工串联成为瓶颈。
4. **BM-RES-06-B 论文追踪**（design）→ **远期候选登记**。定位：arXiv/SSRN 爬取→去重→摘要→趋势检测→下游 LLM 研究助手。裁定：arXiv 爬取 + 标题/DOI 去重 + LLM 摘要的轻量版 <200 行可标 Phase 3 立项（复用 64 号 §6.4 APScheduler 调度基座 + BM-RES-08 清洗模板）；当前 interim 载体 = [90_methodology_open_questions](90_methodology_open_questions.md)/[91_density_prediction](91_density_prediction.md) 的人工文献整合实践（18 轮 arXiv 审查已产出 20+ 候选登记，人工检索+LLM 精读模式已运转有效，无自动化爬取刚需）。重评条件：Phase 3 且周新增相关论文 >20 篇人工精读成为瓶颈。

**BM-RES-06-A LLM 研究助手**（design）：Phase 5+ 重评条件本节"LLM 驱动 alpha 挖掘远期候选"已写明（因子库扩张 + LLM 能力成熟后评估，§2.3"不做 agent 编排系统"约束），确认无需动作。

**BM-RES-07-A 策略进化与因子挖掘**（design）：当前承载 = 人工 + §3.2 第 2 条假设状态机 + [62_business_registry_construction](62_business_registry_construction.md) §4.12 ADAPT_STRATEGY 衰减后适应算法（归因回流→权重调整→升级方案需审批）；FactorMiner Experience Memory（成功模式+失败约束可检索 memory）与 AlphaMemo APV（失败路径不对称否决）为 Phase 3 轻量契合点（可脱离 LLM 独立实现，<100 行，见本节远期候选登记）；LLM 化（CogAlpha/Hubble 式自主挖掘）为 Phase 5+ 远期候选，与 §2.3 约束一致不立即施工。

**LLM 驱动 alpha 挖掘远期候选**（2026-08 补充，00_index G28 讨论要点回填）：本项目 100% AI 开发模式天然契合"量化行业从因子竞争转向智能体竞争"趋势，但当前手动因子研究足够，以下 LLM 驱动自动化方案记为远期候选，待因子库扩张 + LLM 能力成熟后评估：
- **QuantEvolver RFT（Reinforcement Fine-Tuning）——下一代方向**（[arXiv:2605.15412, 2026-05-14](https://arxiv.org/pdf/2605.15412)，[代码 github.com/QuantLLM/QuantEvolver](https://github.com/QuantLLM/QuantEvolver)）：用 **RFT 强化微调**替代标准 LLM"generate-evaluate-feedback"提示词循环——将可执行量化评估转化为**策略更新**（policy updates），Miner LLM 通过参数学习内化因子挖掘经验，而非在提示词中追加膨胀的历史候选/反馈。**核心架构优势**：① 逃离上下文窗口限制（prompt-loop 的历史累积导致 context explosion + feedback drift + search stagnation，RFT 把学习信号移入 LLM 权重彻底绕过）；② 组件：Factor DSL 生成 + Regime Backtest + Diversity-Complementarity Reward + Mined Factor Database；③ 三大真实市场基准验证持续优于 LLM-based baseline。**与 QuantaAlpha 的本质区别**：QuantaAlpha 是 prompt 级**轨迹进化**（evolves trajectories，不更新权重），QuantEvolver 是权重级**策略内化**（evolves the model's policy via RFT）——RFT 比 trajectory evolution 更深一层，是 LLM alpha 挖掘的下一代范式
- **QuantaAlpha LLM-driven Alpha Mining**（[arXiv:2602.07085, 2026-02](https://arxiv.org/abs/2602.07085)）：LLM 用进化算法挖掘 alpha 因子，trajectory-level evolution，diversified planning initialization + trajectory quality + semantic anchoring + experience transfer 四组件，比 RD-Agent/AlphaAgent 更高 IC
- **EvoQuant Self-Evolving Verifier-Guided Strategy Optimization**（[arXiv:2607.12455, 2026-07-14](https://arxiv.org/abs/2607.12455)，HKUST(GZ)）：LLM 深度诊断性能瓶颈→生成语义控制候选编辑→多阶段验证管线选最优→蒸馏优化经验为可复用知识实现持续自我改进。7 策略实证（4 A 股+3 Crypto）：平均 test Sharpe 从 -0.298 提升至 0.538。**与 QuantaAlpha 的区别**：QuantaAlpha 是"LLM 挖因子"（alpha 生成），EvoQuant 是"LLM 优化策略代码"（策略迭代）
- **Strategy-Dev-Manager paper→factor→decay 流水线**（Vibe-Trading 2026-07）：paper PDF → LLM 提取因子公式 → Signal Engine 实现 → IC/IR 评估 → decay monitoring 自动禁用
- **不过度工程审查**：上述四方案均涉及 LLM 自主生成/优化策略代码，与 §2.3 约束"不做 agent 编排系统"（30_multi_strategy §5 已暂缓 LLM 多 Agent 辩论）一致——当前手动策略迭代足够，记为远期候选不立即施工。**三方案范式定位**：QuantaAlpha = prompt 级轨迹进化（alpha 生成）/ EvoQuant = LLM 优化策略代码（策略迭代）/ **QuantEvolver RFT = 权重级策略内化（下一代方向，逃离上下文窗口限制）**。未来评估时：EvoQuant 的多阶段验证管线（防 LLM 幻觉编辑+策略漂移+回测过拟合）是防失控重点参考；QuantEvolver 的 RFT 范式在 LLM 能力成熟 + 因子库扩张后是首选升级路径
- **2026-07/08 LLM Alpha 挖掘最新研究（中国市场实证，2026-08-10 补充）**：2026-07~08 出现 3 篇含中国市场实验的 LLM alpha 挖掘论文，比 QuantaAlpha/EvoQuant/QuantEvolver 更新且更贴合 A 股：
  - **AlphaSchema 交易语义空间探索**（[arXiv:2607.26642v1, 2026-07-29](https://arxiv.org/html/2607.26642v1)）：构建结构化语义空间（Event/Context/Qualities/Direction/Output 五元组 schema plan），**解耦 exploration 与 implementation**——LLM 将 schema plan 翻译为可执行因子，奖励累积学习语义空间上的 surrogate model，iterative selection 平衡 global exploration / surrogate-guided exploitation / local mutation。**关键发现**："同一 schema plan 由不同 LLM 实现，预测质量可比"——alpha mining 质量对 LLM 选择鲁棒。**实验直接在中国股票市场进行**，包含因子衰减分析（Appendix B）。**与 QuantaAlpha 的区别**：QuantaAlpha 是 trajectory-level evolution（进化整个研究轨迹），AlphaSchema 是 schema-level exploration（探索因子语义空间的结构化表达）——后者解耦了"想什么因子"（schema plan）与"怎么实现"（LLM 翻译），更模块化
  - **XALPHA 记忆驱动 AI 量化研究员**（[arXiv:2607.08332v1, 2026-07-09](https://arxiv.org/abs/2607.08332v1)）：多源研究记忆系统（report-grounded 知识 + 发现反馈）+ 三脑架构（Macro Brain 规划研究主题选 Archetypes / Micro Brain 将假设池转为可执行因子代码并验证 hypothesis-code-financial plausibility 三重对齐 tri-alignment / Cross Brain 整合经验结果为 generation-level 反馈+cycle-level 摘要+archetype-level 研究线索）。**将 alpha mining 从孤立因子生成升级为闭环研究过程**（read→hypothesize→implement→validate→reflect→evolve）。**实验在 CSI300 进行**，记忆系统可累积 A 股投研知识。**与 EvoQuant 的区别**：EvoQuant 是"LLM 优化策略代码"（诊断→候选→验证→蒸馏），XALPHA 是"LLM 闭环研究过程"（假设→实现→验证→反思→进化）——后者覆盖完整研究循环非仅代码优化
  - **EFS 进化因子搜索用于稀疏组合优化**（[arXiv:2507.17211v2, 2026-08-07](https://arxiv.org/abs/2507.17211v2)）：LLM+进化算法自动生成/演化 alpha 因子用于**稀疏组合构建**（非 IC level 优化）——将资产选择重构为因子引导的 ranking 任务，redundancy-aware weight allocation 模块结合 random-matrix-theory 去噪与正则化 QP。**直接在 portfolio level 优化因子**（非传统 IC level）。**包含美国、香港、中国大陆三个股票市场实验**。**与 QuantaAlpha/AlphaSchema 的区别**：前两者在因子 level 优化（挖好因子再组合），EFS 直接在 portfolio level 优化（因子服务于组合而非孤立 IC）——后者更贴近实盘（实盘关心组合 PnL 非单因子 IC）
  - **AlphaCrafter 全栈多 Agent 框架**（[arXiv:2605.05580](https://www.themoonlight.io/file?url=https%3A%2F%2Farxiv.org%2Fpdf%2F2605.05580)）：统一**假设-验证-执行闭环**的三 Agent 全栈框架——① **Miner Agent**（因子挖掘：`generate` 提候选因子 + `validate` 用 IC/ICIR/turnover/decay profile 跨 regime 验证 + `update` 记忆 + `revalidate` 周期性复验并剪枝衰减因子）；② **Screener Agent**（regime-conditioned 因子集成：`assess_regime` 诊断 trend/volatility/correlation 三维 regime + `suitability` 评估因子适配度 + `diversify` 多样性约束 + `assign_weight_and_direction` 多空方向加权）；③ **Trader Agent**（策略构造：`construct_strategy` 用复合分数 `φᵢₜ=Σwⱼ·dⱼ·fⱼ(xᵢₜ)` 排序选 top-N long/bottom-N short + `backtest` 风险调整目标 + `live_trading` 执行）。**核心创新**：把"因子挖掘→regime 适配→策略执行"三阶段统一到一个 Agent 闭环，对抗"静态因子集 + 持久性假设"的传统缺陷。**实证**：AlphaCrafter 与 RD-Agent/AlphaAgent 一样在连续半年期保持稳定 IC，证明动态因子管理对抗 alpha decay 优于静态因子集。**与 QuantaAlpha/EvoQuant 的区别**：QuantaAlpha 是"LLM 挖因子"（单一 Miner 环节），AlphaCrafter 是"Miner+Screener+Trader 全栈闭环"（覆盖因子→regime 适配→策略执行全链路）——后者最完整但最重，与 30 号已暂缓的"LLM 多 Agent 辩论"约束直接冲突
  - **FactorMiner 自进化 Agent + Ralph Loop**（[arXiv:2602.14670](https://arxiv.org/pdf/2602.14670v1)）：轻量级自进化 Agent 框架，两大创新——① **Modular Skill Architecture**（将系统性金融评估封装为可执行工具，区别于 black-box 神经预测器，保持公式可解释性满足监管合规）；② **Experience Memory**（将历史挖掘试验蒸馏为可复用洞见：成功模式 + 失败约束），通过 **Ralph Loop 范式**（retrieve 检索相关记忆→generate 生成候选→evaluate 评估→distill 蒸馏新经验）迭代使用记忆先导引探索，**减少冗余搜索同时聚焦有前景方向**。**核心价值**：随着因子库增长，新因子与已有因子冗余度上升（"Correlation Red Sea"约束），FactorMiner 的 Experience Memory 累积"哪些方向已试过/哪些约束须遵守"，避免重复试错。**与 AlphaAgent AST 相似度的区别**：AlphaAgent 的 AST 相似度是"事中过滤"（生成时检测冗余），FactorMiner 的 Experience Memory 是"事前引导"（检索记忆优先探索有前景方向）——两者正交可叠加。**A 股因子库实证**：发布 110 因子全 A 股因子库，因子间相关性矩阵显示低冗余
  - **CogAlpha 代码级认知式 Alpha 挖掘**（[arXiv:2511.18850](https://arxiv.org/abs/2511.18850)，ACL 2026 Oral，港大+九天研究院+Grace Investment Machine）：**将 alpha 从"公式"升级为"代码"**——Python 代码级表示（带注释/逻辑/可执行/可检查）极大扩展搜索空间，超越公式表达能力限制。**7 层 21 Agent 结构化探索体系**（模拟人类量化研究团队分工）：① 市场结构与周期层（长期趋势+阶段切换）→ ② 极端风险与脆弱性层（尾部风险+崩盘前兆）→ ③ 价量关系层（流动性+买卖失衡）→ ④ 趋势延续/短期反转/波动聚集层 → ⑤ 多尺度复杂性层（回撤结构+分形粗糙度）→ ⑥ **稳定性与 Regime 门控层**（AgentRegimeGating+AgentStability，评估时间稳定性+构建自适应门控机制按市场状态调节信号激活）→ ⑦ 几何特征与融合层（K 线形态+多因子融合+非线性改写）。**进化机制**：生成候选→代码可执行性检查→IC/RankIC/ICIR/RankICIR/MI 五指标筛选（>65 分位合格，>80 分位精英进入下一代演化）→变异/交叉/进化迭代。**多样化提示策略**防保守化：轻度改写（稳定）/ 中度改写（自然变体）/ 创造性改写（不同研究角度重新理解同一方向）。**实证**：5 数据集 3 市场（中美港），CSI300 10 天预测任务年化超额收益 16.39%、IR 1.8999，稳定跑赢 21 个基线方法。**关键发现**：闭源模型并无天然优势，推理型模型表现偏弱——alpha 挖掘比的不是"谁更聪明"而是"谁的结构更适合探索/筛选/演化"。**与六篇候选的本质区别**：QuantaAlpha/EvoQuant/QuantEvolver/AlphaSchema/XALPHA/EFS 均为**公式级** alpha（数学表达式），CogAlpha 是**代码级** alpha（Python 程序）——搜索空间从有限算子组合扩展到任意可执行逻辑，表达能力质变。**与 AlphaCrafter 的区别**：AlphaCrafter 是 3 Agent 全栈闭环（Miner+Screener+Trader 覆盖因子→regime→策略执行），CogAlpha 是 7 层 21 Agent 深度探索（覆盖宏观→微观全研究链路但不做策略执行）——前者广（全栈）后者深（研究深度）。**Level ⑥ 稳定性与 Regime 门控层与本项目 10 号 regime 检测器天然契合**——CogAlpha 的 AgentRegimeGating 可消费 10 号 12 态 regime 作为门控信号，按 regime 调节因子信号激活/抑制，是 LLM alpha 挖掘与 regime 系统的唯一显式集成点。**定位**：Phase 5+ 远期候选，ACL 2026 Oral 是候选中学术 venue 等级最高者，代码级表示是范式升级方向
  - **Hubble 安全可复现 Agentic Alpha 发现框架**（[arXiv:2604.09601](https://arxiv.org/abs/2604.09601)，2026-04）：LLM 驱动的 agentic 框架，核心解决自动 alpha 发现的三大工程痛点——搜索空间组合爆炸、日频数据低信噪比、无约束程序生成的操作安全性。**五组件闭环**：① **DSL-Constrained Generator**（LLM 在受限算子树结构内生成候选 alpha 公式，算子注册表含算术/时序 TS_SMA/TS_STD/截面 CS_RANK/CS_ZSCORE/逻辑 IF，覆盖 OPEN/HIGH/LOW/CLOSE/VOLUME/VWAP 原始 panel）；② **AST Validation Sandbox（exec-free 安全栈）**——三层验证：**结构安全**（仅白名单 AST 节点类型，防任意代码执行）+ **复杂度控制**（超深度/超节点数拒绝）+ **语义有效性**（算子名/arity/变量名严格匹配 DSL），整个验证过程**无需执行代码**（exec-free），是九篇候选中唯一显式建模"生成安全性"的框架；③ **Dual-Channel RAG**——**Positive RAG** 检索代表性公式/蒸馏模板鼓励探索 under-covered 机制，**Negative RAG** 检索 crowded/over-explored 模板作为"须避免的 motif"——主动塑造探索方向而非仅事实增强，控制因子拥挤；④ **Deterministic Evaluation Engine**（RankIC/Pearson IC + 操作指标 coverage/drop ratio/bucket returns/long-short spread/turnover + Bartlett-kernel HAC 显著性检验）；⑤ **Weighted Scoring with Family-Aware Selection**（tanh 标准化 + family-aware 生态多样性选择，防同族因子堆积）。**与九篇候选的本质区别**：QuantaAlpha~CogAlpha 均聚焦"生成-评估-进化"范式，Hubble 是唯一显式建模**安全性（exec-free AST 沙盒）+ 拥挤控制（负 RAG）+ 可复现性（确定性评估引擎）**的工程框架——三者是 LLM alpha 挖掘从研究原型到生产部署的**工程必需件**。**与 AlphaAgent AST 相似度的互补**：AlphaAgent 的 AST 相似度是"事中过滤"（生成时检测与已有因子冗余），Hubble 的负 RAG 是"事前引导"（检索 crowded 模板主动避免）+ AST 沙盒是"事前安全"（生成时拦截不安全代码）——三者构成"事前安全→事前引导→事中过滤"的**防同质化+安全施工三层链**。**与 CogAlpha 的区别**：CogAlpha 是代码级 alpha（Python 程序，搜索空间最广但无安全约束），Hubble 是公式级 alpha（DSL 受限，搜索空间窄但 exec-free 安全）——前者深度后者安全，生产部署需 Hubble 式安全栈 + CogAlpha 式表达能力。**对本项目的独特价值**：本项目"可解释性优先+不过度工程"原则下，Hubble 的 exec-free AST 沙盒是 LLM alpha 挖掘安全施工的**最低门槛**——即使未来引入 CogAlpha 代码级 alpha，也须先部署 Hubble 式 AST 验证沙盒（白名单节点+复杂度控制+语义校验）防 LLM 生成危险代码（如无限循环/文件 IO/网络调用）。**定位**：Phase 5+ 远期候选的安全施工参考——LLM alpha 挖掘启动前须先建 AST 沙盒（<200 行代码，独立于 LLM 可先施工），负 RAG 拥挤控制与 AlphaAgent AST 相似度同期评估（因子库 >20 时）
  - **AlphaMemo 结构化搜索过程记忆的自进化 alpha 挖掘 agent**（[arXiv:2606.20625](https://arxiv.org/abs/2606.20625), 2026-05-26, Yu/Zheng/Pan/Liu/Wang/He, University of Sydney + University of Edinburgh）：核心解决 LLM alpha mining 四大痛点——组合搜索空间爆炸 / 噪声非平稳反馈 / 冗余发现累积 / 朴素复用过往成功导致过拟合。**核心创新：记忆整个搜索过程而非仅记忆最终因子或失败列表**——结构化搜索过程记忆含残差、决策、AST 差异。**四大组件**：① **Parent-Edit Action Space**（基于父代因子的编辑动作空间——LLM 在父代因子 AST 上做局部编辑而非空白生成，搜索空间从"全空间生成"压缩到"父代邻域编辑"大幅降低组合爆炸，与 CogAlpha 代码级表示正交：CogAlpha 扩展单点表达能力，Parent-Edit 压缩搜索空间广度）；② **Structured Search-Process Memory**（结构化搜索过程记忆——残差记忆 residual process memory 作为教师修正信号，记忆"教师（标准 IC/IR 评估）对候选因子的修正方向"使后续生成偏向教师认可方向，机理是 residual memory as teacher correction + bounded deviation from the teacher，与 FactorMiner Experience Memory 区别：FactorMiner 记忆"经验洞见"语义级，AlphaMemo 记忆"搜索过程"AST 级含残差/决策/编辑模体粒度更细可执行性更强）；③ **Edit Motifs from AST Differences**（从 AST 差异提取编辑模体——将父子代因子的 AST diff 结构化为可复用"编辑模体"，成功模体可复用加速搜索，与 AlphaAgent AST 相似度区别：AlphaAgent 用 AST 相似度做事中过滤防同质化，AlphaMemo 用 AST diff 做编辑模体复用加速搜索——前者防冗余后者促复用正交可叠加）；④ **Asymmetric Process Veto / APV**（不对称过程否决——成功路径可被复用但不强制，失败路径产生否决信号阻止后续生成重复同一失败模式，**不对称性**：只对失败路径产生否决避免错误传播，成功路径不产生强制复用信号避免过拟合）。**关键洞见 1：过程记忆 > 结果记忆**——记忆整个搜索过程（含残差/决策/AST 差异）比仅记忆最终因子或失败列表更有效，因为搜索过程的决策路径包含"为什么这样选"的因果信息。**关键洞见 2：失败否决不对称性**——失败路径的否决信号比成功路径的复用更重要（不对称），因为错误传播的代价高于错过复用的收益，与本项目 §3.2 假设驱动状态机"拒绝假设也是有效产出"纪律一致。**实验**：20-trading-day formulaic alpha-mining protocol 下，OOS 因子池表现 + 固定预算发现效率均优于代表性基线；消融证实 residual learning / confidence gating / AST-diff edit motifs / APV 各自独立贡献。**与现有 LLM 算法关系**：CogAlpha = 7 层 21 Agent 结构化探索（代码级认知）/ Hubble = 五组件闭环 + AST 安全沙盒 + 负 RAG 防拥挤 / AlphaAgent = AST 相似度正则化防同质化 / AlphaCrafter = 全栈多 Agent 动态因子管理 / FactorMiner = Modular Skill Architecture + Experience Memory / **AlphaMemo = 结构化搜索过程记忆 + 不对称过程否决（本节）**——AlphaMemo 与 FactorMiner 都显式建模 Memory 维度但粒度不同（FactorMiner 语义级经验洞见 vs AlphaMemo AST 级搜索过程），与 AlphaAgent 都用 AST 但用途不同（AlphaAgent 相似度防冗余 vs AlphaMemo diff 促复用），三者可叠加。**与 Autonomous Formulaic Alpha Discovery 六组件框架映射**：Representation = Parent-Edit Action Space（父代邻域编辑定义搜索空间）/ Variation = AST-diff Edit Motifs（编辑模体生成候选）/ Fitness = 沿用标准 IC/IR / Selection = Asymmetric Process Veto（不对称否决更新因子池）/ **Memory = Structured Search-Process Memory（AlphaMemo 核心创新——记忆搜索过程含残差/决策/AST 差异非仅结果，强化六组件中 Memory 维度）** / Adaptation = Residual learning + confidence gating（教师修正 + 置信度门控响应市场变化）。**定位**：Phase 5+ 远期候选（与 CogAlpha/Hubble 同期）。**对本项目的独特价值**：AlphaMemo 的"过程记忆 > 结果记忆"与"失败否决不对称性"两个洞见可脱离 LLM 独立应用于本项目 §3.2 假设驱动状态机——将假设验证的"拒绝路径"（失败）结构化为可检索的否决 memory，辅助人工因子研究避免重复试错（Phase 3 候选，<80 行代码无需 LLM，与 FactorMiner Experience Memory 正交可叠加：FactorMiner 记忆"什么方向有前景"，AlphaMemo 记忆"什么编辑模式会失败"）。**Parent-Edit Action Space + APV 简化伪代码**：

    ```python
    # AlphaMemo: Parent-Edit Action Space + Asymmetric Process Veto (APV) 简化实现
    # arXiv:2606.20625 Yu et al. 2026-05-26
    # 核心：基于父代因子 AST 编辑生成候选 + 失败路径不对称否决

    class EditMotif:
        """AST 差异编辑模体（父子代因子的结构化 diff）"""
        def __init__(self, name, ast_diff, success=0, fail=0):
            self.name = name            # 编辑模体名（如 "add_ts_rank" / "negate"）
            self.ast_diff = ast_diff    # AST 差异（父→子编辑操作）
            self.success = success
            self.fail = fail

    class AlphaMemoSearch:
        """结构化搜索过程记忆 + 不对称过程否决（简化版）"""
        def __init__(self):
            self.process_memory = []     # Structured Search-Process Memory
            self.vetoed_motifs = set()   # APV: 被否决的失败编辑模体
            self.edit_motifs = {}        # AST-diff Edit Motifs 库

        def generate(self, parent_ast):
            """Parent-Edit Action Space：基于父代 AST 编辑生成候选（非从头生成）"""
            candidates = []
            for name, motif in self.edit_motifs.items():
                if name in self.vetoed_motifs:       # APV 不对称否决：跳过失败模体
                    continue
                child_ast = apply_ast_edit(parent_ast, motif.ast_diff)
                candidates.append((name, child_ast))
            return candidates

        def evaluate_and_update(self, name, parent_ast, child_ast,
                                child_ic, child_ir, teacher_correction):
            """评估 + 更新过程记忆 + APV 不对称否决"""
            residual = teacher_correction               # 残差记忆 = 教师修正方向
            success = child_ic > 0.03 and child_ir > 0.5

            # 过程记忆 > 结果记忆：记录完整搜索过程（残差/决策/AST diff）
            self.process_memory.append({
                "parent": parent_ast, "child": child_ast, "motif": name,
                "ic": child_ic, "ir": child_ir, "residual": residual,
                "success": success,
            })

            motif = self.edit_motifs[name]
            if success:
                motif.success += 1
                # 成功路径：可复用但不强制（避免过拟合——不对称性的另一面）
            else:
                motif.fail += 1
                # APV：失败次数超阈值且失败率远高于成功率 → 否决（阻止错误传播）
                if motif.fail >= 3 and motif.fail > motif.success * 2:
                    self.vetoed_motifs.add(name)        # 失败否决信号
    ```
  - **本项目定位**：十一篇均记为 Phase 5+ 远期候选（LLM alpha mining 整体是远期候选，当前手动因子研究足够）。**评估优先级**：AlphaSchema > FactorMiner > AlphaMemo > Hubble > AlphaCrafter > XALPHA > EFS——AlphaSchema 的"schema 解耦 + LLM 鲁棒性"最模块化（可先实现 schema 词汇表辅助人工因子研究）；FactorMiner 的"Ralph Loop + Experience Memory"最轻量（Modular Skill 可先实现评估工具辅助人工，Experience Memory 是"经验沉淀"非 LLM 自主生成）；**Hubble 的"exec-free AST 沙盒 + 负 RAG"是 LLM alpha 挖掘安全施工的最低门槛**（AST 沙盒<200 行可先于 LLM 施工，负 RAG 与 AlphaAgent AST 相似度同期评估）；AlphaCrafter 全栈闭环最完整但与 30 号"LLM 多 Agent 辩论暂缓"约束冲突最直接；XALPHA 的"闭环研究过程"最完整但最重；EFS 的"portfolio level 优化"最贴近实盘但依赖因子库成熟。**不过度工程审查**：六篇均涉及 LLM 自主生成因子代码，与 §2.3 约束一致——记为远期候选不立即施工，待因子库扩张 + LLM 能力成熟后评估。**防同质化正则化补充**——[AlphaAgent](https://arxiv.org/abs/2502.16789)（arXiv:2502.16789, KDD 2025, 中山大学）的三机制（AST 相似度原创性强制 + 假设-因子语义对齐 + AST 结构复杂度控制）防因子同质化，在 CSI 500 + S&P 500 验证抗 alpha decay——其 **AST 相似度正则化独立于 LLM**，可用于传统因子挖掘阶段检测新生成因子与已有因子库的同质化程度，与五骑士 ① Crowding 41% 直接对应（资本涌入→信号被套利→价差压缩的本质就是因子同质化），Phase 2 候选评估（因子库 >20 时用 AST 相似度防同质化，<50 行代码无需 LLM）。**FactorMiner Experience Memory 与本项目的轻量契合点**：FactorMiner 的"经验沉淀"思想（成功模式+失败约束）可脱离 LLM 独立实现——本项目因子孵化阶段（§3.2）已有"假设驱动+证据挂载"状态机，FactorMiner 的 Experience Memory 是该状态机的"跨假设经验累积"层（Phase 3 候选：因子库 >20 时将已验证假设的成功/失败模式结构化为可检索 memory，辅助人工因子研究，<100 行代码无需 LLM）。**AlphaMemo APV 与本项目的轻量契合点**：AlphaMemo 的"失败否决不对称性"可脱离 LLM 独立实现——将假设验证的"拒绝路径"（失败）结构化为可检索的否决 memory，辅助人工因子研究避免重复试错（Phase 3 候选，<80 行代码无需 LLM，与 FactorMiner Experience Memory 正交可叠加：FactorMiner 记忆"什么方向有前景"，AlphaMemo 记忆"什么编辑模式会失败"）。**Hubble AST 沙盒的轻量契合点**：Hubble 的 exec-free AST 验证沙盒可脱离 LLM 独立实现——本项目因子孵化阶段若引入 LLM 生成因子代码，须先部署 AST 白名单（仅允许算术/时序/截面/逻辑算子节点，拒绝 import/open/exec/eval 等危险节点）+ 复杂度控制（深度≤10/节点数≤50）+ 语义校验（算子名匹配因子算子注册表），是 LLM alpha 挖掘的安全前提（Phase 5 候选，<200 行代码，可先于 LLM 施工作为安全基础设施）
- **统一理论框架参照**（[arXiv:2608.01789, 2026-08-03](https://arxiv.org/html/2608.01789v1)，上海大学+西交利物浦）：综述论文提出自主公式化 alpha 发现的**六组件统一框架**——① Representation（定义搜索空间）/ ② Variation（生成候选 alpha）/ ③ Fitness Evaluation（评估 alpha 质量）/ ④ Selection（更新因子池）/ ⑤ Memory（累积验证经验）/ ⑥ Adaptation（响应市场 regime 变化）。系统综述了方法演化谱系（人工公式库→GP/EA→RL→Pool-Aware→Distributional→Graph-Based→MCTS→LLM→Agentic 九代），并给出未来路线图（可靠 Fitness/经济多样性/可解释性/多目标/代理辅助/验证记忆/人在环/可复现基准）。**对本项目的价值**：六组件框架可作为上述九篇候选的**统一分类视角**——QuantaAlpha=Variation+Selection+Memory（轨迹进化）/ QuantEvolver=Variation+Adaptation（RFT 权重内化）/ AlphaSchema=Representation+Selection（语义空间探索）/ FactorMiner=Memory+Adaptation（经验沉淀+Ralph Loop）/ AlphaCrafter=全六组件（全栈闭环）/ XALPHA=全六组件（闭环研究过程）/ EFS=Fitness+Selection（portfolio level 优化）/ EvoQuant=Variation+Fitness+Memory（策略代码优化+经验蒸馏）/ CogAlpha=Representation+Variation+Fitness+Selection+Adaptation（代码级表示+7层21Agent深度探索）/ **Hubble=Representation+Fitness+Selection（DSL 受限表示+确定性评估+family-aware 选择，独特贡献是 Representation 组件的安全约束——exec-free AST 沙盒是其他九篇均未建模的"安全表示"维度）** / **AlphaMemo=Memory+Selection+Variation（结构化搜索过程记忆+不对称过程否决+AST-diff 编辑模体，独特贡献是 Memory 组件的过程级记忆——记忆搜索过程含残差/决策/AST 差异非仅结果，是候选中 Memory 维度最强的显式建模）**。**关键洞见 1**：候选在 Memory 组件上覆盖最薄弱——仅 FactorMiner（Experience Memory）、EvoQuant（经验蒸馏）和 AlphaMemo（Structured Search-Process Memory）三者显式建模，其余均为"生成-评估"范式无跨试验经验累积。**AlphaMemo 是 Memory 维度最强的显式建模**——不仅记忆结果（FactorMiner）或蒸馏经验（EvoQuant），而是记忆完整搜索过程（残差/决策/AST 差异），"过程记忆 > 结果记忆"是 Memory 组件的范式升级。FactorMiner Experience Memory 和 AlphaMemo APV 均可在无 LLM 条件下独立实现（Phase 3 轻量契合点，两者正交可叠加）。**关键洞见 2**：九篇候选在 Representation 的**安全约束**上覆盖最薄弱——仅 Hubble 显式建模 exec-free AST 沙盒，其余均允许 LLM 生成任意代码/公式无安全验证。这印证 Hubble AST 沙盒作为 Phase 5 安全基础设施的**独特价值**——它是 LLM alpha 挖掘从研究原型到生产部署的安全门槛。综述登记为理论参照非新算法，不改变 Phase 5+ 远期候选评估优先级，但六组件框架揭示的两个覆盖薄弱点（Memory+安全表示）分别由 FactorMiner、AlphaMemo（Memory 维度过程级记忆强化——"过程记忆 > 结果记忆"是 Memory 组件范式升级）和 Hubble（安全表示）填补

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RES-03-A | 假设生命周期管理 | §3.2 纪律 2 假设驱动（状态机 提出→验证→接受/拒绝 全程留痕） | design 待施工 |
| BM-RES-10-A | 模块工厂架构 | §3.2 纪律 4 模块工厂 + §3.8 creation_token/depgraph 登记 4 步流程 | design 待施工 |

### 3.3 模型训练阶段（BM-MOD）规范

承接 [battle_map_02_model_training](../battle_map/battle_map_02_model_training.md)（14 环节，10 锚点）：

**核心纪律**：
1. **Champion-Challenger 晋升**（BM-MT-02）：新模型不直接全量上线——A/B 实验对比，统计显著更好才自动晋升为 Champion，否则留 Challenger 观察。**默认动作：证据不足时保留 Champion**（[MetricGate 2026-04](https://metricgate.com/blogs/champion-challenger-model-testing/)）。**统计检验方法**：采用 **mSPRT 混合序贯概率比检验**（mixture Sequential Probability Ratio Test）而非固定样本量 t-test——mSPRT 在每笔交易后累加似然比，达边界即判定（接受 H1 晋升 / 接受 H0 保留 / 继续观察），无需预设样本量，显著减少判定所需交易数。**mSPRT 相对经典 SPRT 的关键升级**（[burning-cost 2026-03-24](https://burning-cost.github.io/2026/03/24/sequential-ab-testing-insurance-champion-challenger/)，Johari et al. 2022）：mSPRT 产生 **e-process**，满足 `P(ever exceeds 1/α) ≤ α` 在所有停时成立，可**任意频次查看无"偷看惩罚"**——经典 SPRT/固定样本 t-test 若中途偷看（如月度检查 12 个月实验），Type I 错误率从 5% 膨胀到 ~25%；mSPRT 保持精确 Type I 控制，配合 anytime-valid 置信序列（Howard et al. 2021）提供时间一致区间。**陷阱**：tau（先验效应大小）标定错误会严重失效，须用历史 OOS 效应量分布标定 tau。**流量切分**：95/5 不对称分流（champion 已"赢得"生产，challenger 必须证明值得替换，[MetricGate 2026-04](https://metricgate.com/blogs/champion-challenger-model-testing/)）——**blast-radius（爆炸半径）原则**：5% 切分上限按「challenger 失效最多波及多少资金」反推而非按速度，风险遏制优先于收益验证（[MetricGate A/B 2026-04](https://metricgate.com/blogs/model-deployment-ab-testing/)：5-10% 不平衡切分而非 50/50，原因：风险遏制+收益保留+序贯数学仍工作）+ 护栏指标 guardrail metrics；[theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/intermediate/champion-challenger/)：金融业 SR 26-02 要求 4-12 周并行验证 + 预注册假设（效应量/显著性/停止规则在并行期开始前文档化，非结果后挑选）。**双指标纪律**（[MetricGate A/B 2026-04](https://metricgate.com/blogs/model-deployment-ab-testing/)）：模型 A/B 测试是**双指标问题**非单指标——① **业务指标**（Sharpe/expectancy/年化收益，衡量"赚不赚钱"）；② **ML 指标**（AUC/IC/Calibration ECE，衡量"模型质量好不好"）。**Challenger 必须两项都优于或等于 Champion 才晋升**——只赢业务指标但 ML 指标退化 = 可能是运气好而非模型好（短期噪声），只赢 ML 指标但业务指标不涨 = 模型改善未转化为收益（可能有执行成本/延迟抵消）。**ECE 校准门控**（[MetricGate A/B 2026-04](https://metricgate.com/blogs/model-deployment-ab-testing/)）：Expected Calibration Error `ECE = Σ (n_b/n) × |p̄_b - ȳ_b|` 衡量预测概率与实际频率的偏差——模型排名好但校准差会导致下游阈值/仓位规则在错误时机触发（discount threshold / bid / reserve price）。Challenger 的 ECE 不得显著高于 Champion。**护栏指标**（guardrail）：除双指标外设护栏——最大回撤/换手率/滑点偏离超限立即终止实验，防止 Challenger 主指标好但尾部风险恶化。**E-values 理论基础**（[MetricGate 2026-06](https://metricgate.com/blogs/e-value-vs-p-value-evidence/)）：mSPRT 产生 e-process 的底层是 **e-value 框架**——e-value 是"对原假设下注"的赔付因子，`E_{H₀}[E] ≤ 1`（原假设下期望不超过 1），e-values **可乘**：独立批次的 e-value 之积构成 **test martingale** `M_n = ∏E_i`，由 **Ville 不等式** `P(sup_n M_n ≥ 1/α) ≤ α` 保证"无论偷看多少次、何时停，超过 1/α 的概率 ≤ α"——这是 anytime-valid 的数学根基。e-value → p-value 转换：`p = min(1, 1/E)`。**与经典 p-value 的本质区别**：p-value 是"跑一次程序"的声明，e-value 是"持续累积的下注"的声明，无论查看多少次都保持有效——这就是为什么 e-values 天然适配序贯监测而 p-value 不行。**序贯检验方法谱系**：① **mSPRT**（mixture SPRT，本项目选用）——对先验效应大小做 mixture 积分，产生 e-process；② **GSPRT**（Generalized SPRT）——允许更广义的备择假设，Netflix/Uber 等大厂采用（[weisberg knowledge_base 2026-02](https://github.com/weisberg/knowledge_base_public/wiki/02g.-When-Is-an-Experiment-Done-Decision-Thresholds-Beyond-Statistical-Significance/Home)）；③ **Always Valid P-Value** `p_n = 1/max_{t≤n} Λ_t`——报告"至今最大证据"的 p-value 变体；④ **Free Anytime Validity**（[Koning & van Meer, arXiv:2501.03982 2025](https://arxiv.org/html/2501.03982v3)）——证明任何有效检验都可通过序贯化获得 anytime validity 且不损失功效，序贯化 z-test/t-test 在 N 时刻与传统检验一致。**贝叶斯替代范式**（[weisberg 2026-02](https://github.com/weisberg/knowledge_base_public/wiki/02g.-When-Is-an-Experiment-Done-Decision-Thresholds-Beyond-Statistical-Significance/Home)，VWO/Statsig 采用）：不同于 mSPRT 的频率学派路径，贝叶斯方法用后验概率做决策——① **Expected Loss**（期望损失）= `P(B 更好) × (B-A 的预期收益差)`，当 Expected Loss < 业务可接受阈值即停止实验；② **Probability to Be Best**（最优概率）= `P(Challenger > Champion | 数据)`，>95% 即晋升。**贝叶斯 vs mSPRT 取舍**：贝叶斯更直觉（直接回答"Challenger 更好的概率"）、可任意频次查看，但依赖先验设定且解释口径不同（后验概率非 Type I 错误率控制）；mSPRT 保持频率学派 Type I 控制 + 无先验依赖（mixture 积分）。**本项目选 mSPRT 理由**：金融监管（SR 26-2）偏好频率学派 Type I 错误率控制框架，且 mSPRT 的 e-value 可转化为 p-value 对接传统报告。**序贯检验 vs 固定样本取舍**（[experimenthq 2026-12](https://www.experimenthq.io/blog/sequential-testing-vs-fixed-horizon)）：序贯检验复杂但允许早期停止（减少判定所需交易数），固定样本简单但须严格不偷看——**最坏实践是"用固定样本方法但偷看"**（Type I 从 5% 膨胀到 20-30%）。本项目选序贯（mSPRT）因交易笔数累积慢、需要早期停止能力

   **mSPRT 施工伪代码**（2026-08-10 补充，施工算法缺失填补——理论描述完整但无可执行形态，核心三要素：似然比累加 + tau 标定 + 边界判定）：

   ```python
   # mSPRT Champion-Challenger 序贯晋升（Johari et al. 2022 高斯 mixture 闭式解）
   # H0: Challenger ≤ Champion（无改善）  H1: Challenger > Champion（有改善）
   class MSPRTChampionChallenger:
       def __init__(self):
           self.alpha = 0.05              # Type I 错误率上限（SR 26-2 频率学派偏好）
           self.threshold = 1 / self.alpha  # = 20，Ville 不等式边界 P(sup M_n ≥ 1/α) ≤ α
           self.tau = self._calibrate_tau()  # 先验效应大小（见标定流程）
           self.M = 1.0                   # test martingale 初始化（e-process 累乘，E_{H0}[E]≤1）
           self.n = 0                     # 已观测交易笔数
           self.delta_history = []        # 增量收益差序列（Challenger - Champion）

       def _calibrate_tau(self):
           """tau 标定流程（一次性，部署前完成）——文档警告'tau 标定错误会严重失效'"""
           # 收集历史 OOS 效应量（Champion 历次晋升的 Sharpe 差 ΔSharpe 序列）
           historical_effects = mlflow.get_promotion_effects()  # 至少 5 个历史 OOS 效应量
           if len(historical_effects) < 5:
               return 0.2  # 冷启动兜底：无足够历史数据时用保守默认值
           tau = np.std(historical_effects)  # mixture 先验宽度对齐历史效应分布
           # 下限保护：tau 过小 → 退化为固定效应 SPRT（失去 mixture 任意时刻有效性）
           return max(tau, 0.1 * np.median(historical_effects))

       def update(self, champion_pnl, challenger_pnl):
           """每笔交易后更新（anytime-valid，可任意频次查看无偷看惩罚）"""
           self.n += 1
           delta = challenger_pnl - champion_pnl
           self.delta_history.append(delta)
           sigma = np.std(self.delta_history[-30:]) or 1e-6  # 滚动波动率（30 笔窗口）
           mean_delta = np.mean(self.delta_history)
           # mSPRT mixture 似然比（高斯 mixture，Johari et al. 2022 闭式解）
           # 对效应大小 δ ~ N(0, τ²) 做 mixture 积分得 LR_n
           var_n = self.n * sigma**2
           lr = np.sqrt(self.tau**2 / (self.tau**2 + var_n)) * \
                np.exp((mean_delta**2 * self.n * self.tau**2) / (2 * sigma**2 * (var_n + self.tau**2)))
           self.M *= lr  # test martingale 累乘（e-values 可乘性，M_n = ∏E_i）

           # 边界判定（Ville 不等式 anytime-valid）
           if self.M >= self.threshold:           # M ≥ 1/α → 拒绝 H0，晋升 Challenger
               return "PROMOTE_CHALLENGER"        # e-value ≥ 20，统计显著优于 Champion
           # 接受 H0：样本耗尽且证据不足 → 默认保留 Champion
           if self.n >= self.max_sample_size and self.M < 1 / self.threshold:
               return "RETAIN_CHAMPION"           # 证据不足时默认动作（MetricGate 2026-04）
           return "CONTINUE"                      # 继续观察
   ```
   **施工要点**：① α=0.05 对齐 SR 26-2 频率学派 Type I 控制；② tau 用历史 OOS 效应量标准差标定（≥5 个历史点，冷启动兜底 0.2）；③ 边界 1/α=20（Ville 不等式）；④ 似然比用高斯 mixture 闭式解（Johari et al. 2022）；⑤ 流量切分通过 MLflow alias 路由——Challenger 注册 @challenger alias，信号扇出时 5% 订单流走 Challenger 推理路径（blast-radius 上限），95% 走 @champion；晋升时 alias 切换 @champion←@challenger，旧 Champion 自动落 @archived

   **多策略选择演进路径**（选项之外更好的答案算法，2026-08 补充）：上述 mSPRT 是"champion vs challenger"**成对**序贯检验，适配 3-5 策略规模。当策略数扩张（G11 第二批次上线后 >8），成对比较的 O(N²) 组合数成为瓶颈，且 pairwise 多次比较的 **family-wise error rate（FWER）会膨胀**（Bonferroni 修正过于保守），须升级为"N 选 K"多策略并行淘汰算法：
   - **ASHA Tournament-Based Strategy Selection**（[FerroQuant 2026-03 white paper](https://arxiv.org/abs/1808.08926)，原始 ASHA by Li et al. 2018）：将超参优化领域的 Asynchronous Successive Halving Algorithm 适配为实时策略选择——successive halving（逐轮淘汰底部半数）+ 异步并行评估，以最小样本量识别最优策略。FerroQuant 实证：1056 标的×5 资产类×178 活跃策略实时 regime-conditional 过滤。**与 mSPRT 的关系**：mSPRT 是"二选一"（pairwise），ASHA 是"N 选 K"（tournament）——ASHA 有样本复杂度理论保证（形式化探索-利用权衡），策略数 >8 时 successive halving 比 pairwise 更高效
   - **SERPANT — 基于 e-process 的在线排序与剪枝**（[Gu, Sun, Gang, Xia ICML 2026](https://openreview.net/forum?id=7Y8xRnGQ47)，[代码](https://github.com/ranzer30/serpant_python)）：把"N 个模型两两比较"形式化为假设检验族，用 **e-process**（与上述 mSPRT 同源的 e-value 框架）在任意监测时刻控制 **FWER**——pairwise mSPRT 只控制单次比较的 Type I，多策略两两比较时 FWER 会膨胀。SERPANT 引入 **tournament sampling** 自适应选比较对（基于历史结果优先比较有希望的候选），支持 top-k 识别 + early stopping 节省评估成本。**与 ASHA 的关系**：ASHA 给的是"排序/淘汰算法"（successive halving），SERPANT 给的是"统计检验框架"（e-process + FWER 控制）——两者正交可组合：ASHA 决定"淘汰谁"，SERPANT 保证"淘汰决策统计可靠"
   - **本项目定位**：当前 3-5 策略用 pairwise mSPRT 足够；G11 第二批次上线后策略数 >8 时评估 ASHA（淘汰算法）+ SERPANT（统计框架）组合替代 pairwise，记为 **Phase 2+ 候选**。**不过度工程审查**：3-5 策略规模下引入 ASHA/SERPANT 是净负担（tournament 采样 + FWER 控制的实现成本 > pairwise 简单性收益），不立即施工
2. **灰度 + 影子部署**（BM-MT-02-A）：渐进流量梯度 5% → 25% → 50% → 100%，每阶段自动比较指标，异常自动回滚流量；影子模式并行预测不改决策 → 全量晋升或回滚（[youngju.dev 2026-03](https://www.youngju.dev/blog/ai-platform/2026-03-04-ai-platform-model-registry-ab-deploy-2026)：점진적 트래픽 증가 5%→10%→25%→50%→100%）。**影子模式持续时长量化**（2026-08 补充）：影子模式须持续足够时长覆盖至少 1 个完整 regime 周期，避免只在单一 regime 验证就晋升——A 股日内策略 2-4 周（覆盖 1-2 个情绪周期），隔夜/波段策略 8-12 周（覆盖 1 个季度 regime 切换），至少 30-50 笔影子交易才具备统计意义（[theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/intermediate/champion-challenger/)：SR 26-02 金融业 4-12 周并行验证；[LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)：30-50 笔早期预警，100+ 笔确认）。**影子模式异步架构**（[mljar 2026](https://mljar.com/ai-prompts/mlops/model-monitoring/prompt-shadow-mode/)）：Champion 服务所有请求，Challenger 异步接收请求副本做推理——**fire-and-forget + timeout**，Challenger 超时或出错只记日志不影响 Champion 响应（challenger call must never block or slow the champion response）。**每日对比分析**：① agreement rate（Champion vs Challenger 预测一致率）；② score correlation（Pearson 相关性）；③ distribution comparison（KS 检验两者分数分布）；④ disagreement analysis（分歧时抽样 50 笔人工检查谁对）；⑤ latency comparison（Challenger p99 须满足 SLA）。**成本警示**：影子模式翻倍计算成本——Challenger 用较小副本数降成本
3. **对抗鲁棒性**（BM-MT-02-B）：上线前 FGSM/PGD 对抗扰动测试，输入被轻微扰动就翻盘的模型不准上生产
4. **漂移检测多方法 Drift Observatory**（BM-MT-05，2026-08 升级）：单一 PSI 只能抓边际特征漂移，抓不住多变量联合分布漂移和概念漂移。升级为多方法组合：
   - **特征漂移**（covariate shift）：PSI（>0.1 调查 / >0.25 材料性漂移，[theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/advanced/population-stability-index-psi/)）+ KS 检验（连续特征分布偏移，Bonferroni 多重比较校正）+ MMD（多变量联合分布漂移，RBF 核 + 随机傅里叶特征近似 O(n²)→O(n)，[Ledger-Lenz #35 2026-06](https://github.com/Ledger-Lenz/Ledgerlens-data/issues/35)）+ **Wasserstein 距离**（Earth Mover's Distance / EMD，[mikenguyen13 2026](https://mikenguyen13.github.io/ai_in_action/932-data-drift-detection.html)）：将分布 P 搬运到 Q 所需的最小"工作量"（质量×距离），有直观物理释义——比 KS（只看最大差异点）更敏感于整体分布形状变化，比 MMD 计算更轻量（一维 Wasserstein O(n log n)）。**Wasserstein vs MMD 取舍**：MMD 通过核函数隐式映射到高维空间捕获非线性关系（多变量联合分布），Wasserstein 在一维上有最优传输理论保证且计算高效——多变量场景用 MMD，单变量连续特征用 Wasserstein 补充 KS 的盲区
   - **概念漂移**（concept drift）：ADWIN（Adaptive Windowing）在滚动误差率上检测结构突变——X→y 映射关系变了，PSI 抓不住（[stockalpha.ai 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-alpha-decays)）
   - **残差漂移**：CUSUM / Page-Hinkley 在模型残差上检测持续偏移——预测系统性偏高/偏低。**CUSUM 参数标准设置**（[mathandmarkets 2026-02-22](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)）：单侧 CUSUM 统计量 `S⁺ₜ = max(0, S⁺ₜ₋₁ + (μ₀ - xₜ) - k)`，其中 μ₀ 为 OOS 验证期均值（**禁止用全回测均值**——包含待检测 regime），k=0.5σ（allowance，标准设置），h=4σ（threshold，平衡检测速度与误报率，约 0.5 次/年误报）。**实证**：Sharpe~1 策略 changepoint 后约 50 交易日检出（2 个月），优于等 Rolling Sharpe 趋势转负的 6+ 个月（[mathandmarkets 2026-02-22](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)：simulated changepoint at day 200, CUSUM alarm at day 250）。**关键限制**：μ₀ 须用 clean OOS 验证期均值，非全回测均值（包含待检测 regime 会污染基线）。**CUSUM 重尾失效风险**（[arXiv:2605.23419 2026-05-22](https://arxiv.org/html/2605.23419v1)）：经典 CUSUM 假设高斯分布，**金融数据有重尾特性**（收益率超额峰度常 >20），经典 CUSUM 在超重尾数据上 **100% 误报**——解法是**广义随机逼近 LLR**（Generalized Stochastic Approximation LLR）：在多项式/对数/分数幂广义随机基上逼近对数似然比，仅用至 3 阶矩，无需分布解析形式，在超重尾数据上仍有效，Kunchenko 概率误差界控制误报（核心定理用 Lean 4 形式化验证）。**CUSUM 自相关失效风险**（[arXiv:2607.16106 2026-07-20](https://arxiv.org/pdf/2607.16106)）：经典 CUSUM 假设 IID，**金融时间序列有自相关**（AR(p) 特性），IID 检测器在时间相关时失效——解法是 **AR(p)-focus 算法**：将 GLR 统计量扩展到 p 阶自回归过程，适配 focus 算法，每迭代平均 O(log n) 复杂度，适合高频流，存在时间相关时比 IID 检测器更强大。**CUSUM 单窗口局限**（[arXiv:2606.05072 2026-06-15](https://arxiv.org/html/2606.05072v2)，Aalto + Princeton, H.V. Poor）：经典 CUSUM 用单一固定窗口，无法自适应不同尺度的变点——**PM-CuSum（Predictive-Mixture CuSum）** 在 CuSum 递归中组合不同长度滑动窗口构造的预测分布，自适应权重基于近期预测性能，达到**一阶渐近最优**，且渐近延迟界的余项阶数比单固定窗口（甚至 oracle 窗口）更小。**本项目定位**：CUSUM 作为基线检测器保留，重尾场景（如打板策略涨停板收益率分布）+ 自相关场景（如动量策略 AR(1) 收益序列）须升级为广义随机逼近 LLR / AR(p)-focus，PM-CuSum 作为 Phase 4 鲁棒性候选。**Phase 1 缓解措施**（2026-08-10 补充，施工算法缺失填补——经典 CUSUM 在金融重尾数据 100% 误报是实盘生存级问题，但广义随机逼近 LLR/AR(p)-focus/PM-CuSum 都是 Phase 3/4 候选，Phase 1 须有可施工的缓解措施避免误报风暴）：
   - **① 收益稳健预处理**：CUSUM 输入前对收益做 winsorize（截尾到 1%/99% 分位），将超额峰度从 >20 压到 <5，使高斯假设近似成立——CUSUM 在 winsorize 后的收益上误报率从 100% 降至可接受水平（稳健统计标准实践，<10 行代码）
   - **② CUSUM 降权 + MMD 提权**：composite drift score（§3.3 第 4 条）中 CUSUM 分量权重从默认降低（如 0.15→0.05），MMD 分量权重提高（MMD FPR=0%/检测率 99.9%，royxforge 20 种子基准 #1）——MMD 作主检测器，CUSUM 仅作残差漂移辅助
   - **③ 确认窗口**（复用 MMDEW 思路）：CUSUM 告警后加 3-5 日确认窗口（连续 N 次超标才触发 alert 级响应），过滤重尾单日极值导致的孤立超标——与 MMDEW confirmation window 同理（striim-labs 2026-03）
   - **④ 残差而非原始收益**：CUSUM 跑在模型残差（预测误差）上而非原始收益上——残差的尾部比原始收益轻（模型已捕获大部分可预测成分），CUSUM 在残差上的高斯假设更接近成立
   - **施工优先级**：①+④ 为 Phase 1 必做（<15 行代码，零外部依赖）；②+③ 为 Phase 1 推荐（composite score 权重调整 + 确认窗口，<20 行代码）。Phase 3 升级到广义随机逼近 LLR / AR(p)-focus 时，①④ 的预处理仍保留（预处理与重尾检测器正交可叠加）
   - **预测漂移**（prediction drift / output distribution shift）：模型输出分布发生变化——即使输入分布未变，模型预测的得分分布也可能因 calibration 漂移或模型更新而偏移（[vectraops 2026-07-15](https://www.vectraops.com/content/how-to-detect-model-drift-in-machine-learning-pipelines/download-pdf/)：Prediction drift occurs when the distribution of model outputs changes, may happen because inputs changed but also from model update or calibration issue；[agencyscript 2026-03](https://www.agencyscript.com/blog/ai-agency-data-drift-detection)：Prediction drift is often the most visible type to end users）。**检测方法**：对模型输出分数做 PSI/KS 检验（与 OOS 验证期输出分布对比），分数分布向均值坍缩或双峰分裂是漂移信号（[llmops.report 2026-04-27](https://llmops.report/posts/concept-drift-detection-in-production/)：score distribution collapsing toward mean or bimodally splitting is a signal worth chasing even without label data）。**对量化交易的特殊意义**：信号置信度分布偏移 = 模型在"什么时候该交易"的判断上漂移，即使 IC 暂未下降，prediction drift 是 IC 下降的先行指标
   - **标签漂移**（label drift / target prior shift）：目标变量先验分布变化——如 A 股市场牛市/熊市切换导致正收益股票比例变化，与特征漂移和概念漂移正交（[vectraops 2026-07-15](https://www.vectraops.com/content/how-to-detect-model-drift-in-machine-learning-pipelines/download-pdf/)：Label drift occurs when the distribution of true labels changes；[agencyscript 2026-03](https://www.agencyscript.com/blog/ai-agency-data-drift-detection)：base rate of churn increases from 5% to 12% after a price increase）。**检测方法**：监控实际收益率分布的滚动统计量（均值/偏度/峰度），与 regime 检测器联动——标签漂移往往是 regime 切换的统计表征。**与 regime 检测器的关系**：标签漂移检测是 regime 检测器（10号 spec）的互补视角——regime 检测器从特征空间聚类，标签漂移从目标分布统计
   - **三层检测架构**（[vectraops 2026-07-15](https://www.vectraops.com/content/how-to-detect-model-drift-in-machine-learning-pipelines/download-pdf/) + [llmops.report 2026-04-27](https://llmops.report/posts/concept-drift-detection-in-production/) 交叉验证）：上述五类漂移按三层架构组织——① **Layer 1 输入监控**（特征漂移 PSI/KS/MMD，无需 ground truth，最快预警）；② **Layer 2 预测监控**（预测漂移 + 残差漂移，无需 ground truth，连接输入变化到模型行为）；③ **Layer 3 延迟结果监控**（概念漂移 ADWIN + 标签漂移，需延迟 ground truth，最终验证）。三层递进：Layer 1 预警"输入变了" → Layer 2 确认"模型行为变了" → Layer 3 验证"预测质量变了"——避免单一层误报（[vectraops 2026-07-15](https://www.vectraops.com/content/how-to-detect-model-drift-in-machine-learning-pipelines/download-pdf/)：A drift alert becomes meaningful only when you can connect it to model behavior or downstream outcomes；[llmops.report 2026-04-27](https://llmops.report/posts/concept-drift-detection-in-production/)：Data drift is a leading indicator, not proof of model failure）
   - **composite drift score**（复合漂移分）：加权组合 `0.3×PSI_max + 0.2×MMD + 0.2×KS_max + 0.15×CvM_max + 0.15×concept_drift_rate`，超阈值 0.35 触发重训练（[Ledger-Lenz #35 2026-06](https://github.com/Ledger-Lenz/Ledgerlens-data/issues/35)）。**CvM（Cramér–von Mises）比 KS 对尾部漂移更敏感**——KS 只看最大差异点，CvM 积分全分布差异，尾部偏移是金融数据漂移的常见模式（[Ledger-Lenz #35 2026-06](https://github.com/Ledger-Lenz/Ledgerlens-data/issues/35)）
   - **MMD 严格基准实证**（[royxforge 2026-06-15](https://github.com/royxforge/production-drift-detection/blob/main/README.md) 20 种子严格基准，5 特征 2000 参考样本 漂移幅度 2.0 = 10 批渐进 + 40 批满强度）：**MMD 复合排名 #1（0.9225）**——FPR=0.0% / 检测率 99.9% / ROC AUC=1.0000 / Cohen's d=6.38；PSI 检测率 100% 但 **FPR 高达 39.9%**（误报率过高）；KL Divergence FPR=0% 但检测率 95.2%；ADWIN FPR=46.5%。**结论**：MMD 是多变量漂移检测的最优选择（低误报 + 高检测率），PSI 单独使用误报率不可接受须配合 MMD 交叉验证。所有检测器中位延迟为 0 批次（同批即检出）。**MMD 流式部署工程陷阱——MMDEW**（[striim-labs/MMDEW 2026-03](https://github.com/striim-labs/online-drift-detection-mmdew)，Kalinke et al. 2025 扩展）：MMD 在流式（streaming）部署中有**自相关陷阱**——连续 MMD² 值的 lag-1 自相关约 0.87，超标事件不独立发生而是**聚类成长串**（stationary Uniform 数据在 95th 百分位阈值下产生 21+ 连续超标，超过 20 的确认窗口 → 触发误报重检测）。**解法**：MMDEW（MMD Early Warning）引入三机制——① **automatic recalibration**（检测后自动重校准基线，避免误报重检测）；② **confirmation window**（确认窗口，连续 N 次超标才告警，过滤自相关聚类）；③ **adaptive thresholding**（自适应阈值，用 99th 百分位替代 95th 降低误报，max run length 从 21 降至 12）。**本项目启示**：MMD 批量检测（每日盘后）无此问题（各批独立），但若未来升级为盘中流式 MMD（tick 级漂移监控），须采用 MMDEW 的确认窗口 + 自适应阈值，否则 lag-1 自相关会导致误报风暴
   - **WMAPE 整体精度监控**（[CSDN 2026-08-08](https://blog.csdn.net/wanghaiwen69/article/details/163591186) 2026-08-08 15:02 发布）：PSI 检测特征分布漂移（阈值 0.1/0.2/0.4 三级）+ CUSUM 检测误差序列突变点（累积和超控制限告警）+ **WMAPE（加权平均绝对百分比误差）监控整体精度**滚动均值偏离基线 1.5σ 告警。三者分别覆盖"特征分布 / 误差突变 / 整体精度"三层——PSI 抓不住误差突变，CUSUM 抓不住整体精度慢漂移，WMAPE 对高销量项加权更稳定。**与本项目 composite drift score 的关系**：WMAPE 可作为 composite score 的第六分量（精度层），与 PSI（特征层）+ CUSUM（残差层）+ ADWIN（概念层）正交补充
   - **多重检验校正**：多检测器并行 → 误报率膨胀，用 Benjamini-Hochberg FDR 校正保持告警率可控（[stockalpha.ai 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-alpha-decays)）
   - **下游影响门控**（downstream impact gating，[llmops.report 2026-04-27](https://llmops.report/posts/concept-drift-detection-in-production/)）：**"统计显著性不等于业务显著性"**——统计检验（KS/chi-squared/MMD）在有足够数据时几乎总能检测到"分布不同"，但真正的问题是"漂移是否大到影响预测质量"。**纪律**：特征漂移告警须经过下游影响估计过滤——在验证期建立"特征偏移幅度 → 预测误差影响"的近似映射，仅当估计的下游影响超过业务关心阈值时才告警（[llmops.report 2026-04-27](https://llmops.report/posts/concept-drift-detection-in-production/)：Statistical significance without effect size is noise; gate feature drift alerts through a downstream impact estimate; only fire when estimated impact on downstream accuracy crosses a threshold you actually care about）。**对量化交易的意义**：多数特征因季节性/regime 切换/数据源变更而持续漂移（良性漂移），若所有特征漂移都告警则告警疲劳——下游影响门控是减少误报的工程纪律
   - **三闭环保留**：事前 composite drift score 预警 → 事中在线适应（EWMA/Stage2 缩放）→ 事后 C-007 离线重训
   - **漂移 vs 过拟合鉴别——Deflated Sharpe Ratio**（[mental-momentum 2026-06-14](https://research.mental-momentum.ai/r/non-stationarity-concept-drift-trading-d1jnvx)）：检测到"漂移"信号后，须先用 **Deflated Sharpe Ratio**（DSR）排除过拟合可能——Traders often misdiagnose backtest overfitting as market drift，necessitating advanced frameworks like the Deflated Sharpe Ratio to validate true market breaks。DSR 调整回测 Sharpe 以反映"多次试错后的最佳结果"（multiple testing penalty），若 DSR 仍显著 > 0 则漂移是真市场结构变化，若 DSR 降至不显著则原策略本身是过拟合产物（漂移是假象）。**流程**：漂移告警 → 跑 DSR 验证 → DSR 显著走重训练/退役流程，DSR 不显著走"策略本身无效"诊断（回到 §3.2 孵化阶段重新假设）
   - **分级响应阶梯**（staged operational responses，[stockalpha.ai 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-alpha-decays)）：漂移检测不应直接跳到"重训练"，而是按严重程度分级响应——① **alert**（告警，仅通知，策略正常运行）；② **reduce size**（减仓至 50%，降低风险敞口）；③ **stop new entries**（停止新建仓，仅平存量）；④ **quarantine**（隔离，暂停策略等待诊断）；⑤ **retrain**（触发重训练）。每级响应有明确进入/退出条件，避免"一有漂移就重训练"的过度反应（重训练成本高 + 可能过拟合新数据）

   **四层 Drift Observatory 联动编排伪代码**（2026-08-10 补充，施工算法缺失填补——上述四层架构 + 分级响应阶梯 + 下游影响门控 + CUSUM→calibration flush 联动均为分散描述，缺一份"四层如何聚合告警→如何映射分级响应"的可执行编排逻辑）：

   ```python
   def drift_observatory_orchestrate(strategy_id, features, model_output, realized_pnl):
       """四层 Drift Observatory 联动编排（2026-08-10 施工填补）

       四层递进逻辑：Layer 1 预警"输入变了"→ Layer 2 确认"模型行为变了"
       → Layer 3 验证"预测质量变了" → Layer 4 可证"覆盖保证破了"
       分级响应：alert → reduce_size → stop_entries → quarantine → retrain
       核心纪律：单一层告警不触发高级响应，须多层确认（避免过度反应）
       """
       # === 四层并行检测，各层独立产出 severity 0.0-1.0 ===
       l1 = input_monitor.check(features)           # PSI/KS/MMD/Wasserstein 特征漂移
       l2 = prediction_monitor.check(model_output)  # prediction drift + CUSUM 残差漂移
       l3 = outcome_monitor.check(realized_pnl)     # ADWIN 概念漂移 + 标签漂移（延迟 ground truth）
       l4 = conformal_layer.check_coverage()        # 数学保证：实际覆盖 < 名义 (1-α) 即漂移

       # 下游影响门控：Layer 1 特征漂移须经业务影响估计过滤
       # （statistical significance ≠ business significance，llmops.report 纪律）
       if l1.severity > 0 and not downstream_impact_gate(l1):
           l1.severity = 0  # 良性漂移（季节性/regime），降级避免告警疲劳

       # CUSUM→calibration flush 联动：Layer 2 残差 CUSUM 告警触发 Layer 4 校准集冲刷
       if l2.cusum_alarm:
           conformal_layer.flush_calibration_set()  # 丢弃陈旧校准集，post-drift 重建（minimax 最优）
           bc_aci.correct_bias(l2.residual_bias)    # BC-ACI 在线纠正残余偏置（宽度+中心双重保护）

       # === 告警聚合：加权 composite score ===
       # Layer 4 权重最高（可证覆盖非启发式）→ Layer 3（结果验证）→ Layer 2（行为确认）→ Layer 1（先行预警）
       weights = {1: 0.15, 2: 0.20, 3: 0.25, 4: 0.40}
       composite = sum(weights[L] * sev for L, sev in [(1,l1.severity),(2,l2.severity),(3,l3.severity),(4,l4.severity)])

       # === 分级响应映射（stockalpha staged responses，不直接跳重训练）===
       if l4.coverage_breach or composite >= 0.80:
           response = "RETRAIN"             # 严重：Layer 4 可证覆盖破 或 多层共振
           trigger_retraining(strategy_id)  # §3.3 第 8 条 性能触发
       elif composite >= 0.60:
           response = "QUARANTINE"          # 隔离：暂停策略等待诊断
           order_manager.disable(strategy_id)
       elif composite >= 0.40:
           response = "STOP_NEW_ENTRIES"    # 停新建仓，仅平存量
           order_manager.disable_new_entries(strategy_id)
       elif composite >= 0.20:
           response = "REDUCE_SIZE"         # 减仓至 50%
           position_sizer.scale(strategy_id, 0.5)
       else:
           response = "ALERT"               # 仅通知，策略正常运行
       # 时序纪律：Layer 1 单独告警（composite<0.40）→ ALERT 级，等 Layer 2/3 确认后再升级
       notify(strategy_id, response, composite)
       return response, composite
   ```
   **施工要点**：① 四层权重 Layer 4 最高（0.40，可证覆盖非启发式）反映"数学保证 > 经验阈值"优先级；② 下游影响门控仅作用于 Layer 1（特征漂移多为良性），Layer 2-4 已直接关联模型行为不门控；③ CUSUM→calibration flush 复用 §3.3 残差漂移 CUSUM 基础设施（同一检测器既检残差漂移又触发 CP 校准集冲刷）；④ 分级响应阈值 0.20/0.40/0.60/0.80 对应 alert/reduce/stop/quarantine/retrain 五级，与 stockalpha staged responses 对齐；⑤ Layer 4 `coverage_breach`（可证覆盖破）直接触发 RETRAIN 绕过 composite 阈值——数学保证层的告警不可被其他层"稀释"

   **downstream_impact_gate + trigger_retraining 施工伪代码**（2026-08-10 补充，施工算法缺失填补——上述 drift_observatory_orchestrate 在 L200 调用 `downstream_impact_gate(l1)` 和 L216 调用 `trigger_retraining(strategy_id)` 均为悬空 helper，与 54 号补全 get_sector/current_session_id/aggregate 同类跨文档悬空 helper 缺口；drift_observatory_orchestrate + BettingMartingaleCoverageMonitor 均已有施工伪代码，仅剩这两个 helper 未落地则四层 Drift Observatory 编排逻辑无法闭环执行）：

   ```python
   def downstream_impact_gate(l1):
       """Layer 1 特征漂移的下游影响门控（2026-08-10 施工填补）

       纪律：statistical significance ≠ business significance
             （llmops.report 2026-04-27：统计显著但无 effect size 是噪声）
       职责：过滤"统计显著但业务不显著"的特征漂移，避免告警疲劳
       输入：l1 = input_monitor.check(features) 的返回值
             含 strategy_id / severity(0.0-1.0) / drifted_features(list) /
                 psi_scores / ks_scores / mmd_score
       输出：bool — True=有业务影响(保留告警) / False=良性漂移(降级 severity=0)

       四步检查（任一"业务影响显著"即 True；全部"良性"才 False）：
       ① regime 解释：当前 regime 是否在已知良性 regime 列表（季节性/假期/已知切换）
       ② IC 衰减：漂移特征对应的滚动 IC 是否显著衰减
       ③ Sharpe 退化：漂移窗口的滚动 Sharpe 是否同步退化
       ④ 残差膨胀：漂移窗口的模型残差/损失是否显著增加

       与 SHAP Drift Attribution（§3.3 第 4 条候选）的关系：
           本函数回答"漂移是否有业务影响"（过滤误报），
           SHAP 回答"漂移根因是哪个特征"（加速诊断）——两者互补。
       与 ARM 变点归因（arXiv:2608.01691 候选）的关系：
           ARM 回答"哪些维度真正变了"（有限样本证书），
           本函数回答"变了之后业务影响多大"——两者在"是否漂移→哪些维度→业务影响"链路分工。
       """
       strategy_id = l1.strategy_id  # input_monitor.check 时注入

       # ① regime 解释：良性 regime（季节性/假期/已知切换）→ 漂移可解释
       #    复用 10 号 regime 检测器的 12 态分类
       current_regime = regime_detector.current_state(strategy_id)
       benign_regimes = {"季节性_年末调仓", "假期_春节缩量", "已知切换_牛熊转折"}
       regime_explained = current_regime in benign_regimes

       # ② IC 衰减：漂移特征的滚动 IC(20d) vs baseline IC
       #    |ΔIC| > 0.05 连续 3 日 = 业务影响显著
       #    （IC 是因子预测力的直接度量，IC 衰减=漂移已传导到预测力）
       ic_degraded = False
       for feat in l1.drifted_features:
           rolling_ic = ic_tracker.get_rolling_ic(strategy_id, feat, window=20)
           baseline_ic = ic_tracker.get_baseline_ic(strategy_id, feat)
           if abs(rolling_ic - baseline_ic) > 0.05:  # IC 衰减超 5 个百分点
               ic_degraded = True
               break

       # ③ Sharpe 退化：漂移窗口的滚动 Sharpe vs baseline
       #    Rolling Sharpe < baseline × 0.7 = 业务影响显著
       #    （与 §3.3 第 5 条 Decay Detection 第 1 监控点 Rolling Sharpe degradation 对齐：
       #     30-50 笔早期预警，100+ 笔确认；此处 50 笔窗口作确认级）
       rolling_sharpe = performance_tracker.get_rolling_sharpe(strategy_id, window=50)
       baseline_sharpe = performance_tracker.get_baseline_sharpe(strategy_id)
       sharpe_degraded = rolling_sharpe < baseline_sharpe * 0.7

       # ④ 残差膨胀：漂移窗口的模型残差/损失 vs baseline
       #    loss > baseline × 1.3 = 业务影响显著
       #    （与 §3.3 第 7 条回滚触发阈值表 MAPE > baseline × 1.3 连续 3 天对齐）
       recent_loss = loss_tracker.get_recent_loss(strategy_id, window=10)
       baseline_loss = loss_tracker.get_baseline_loss(strategy_id)
       loss_inflated = recent_loss > baseline_loss * 1.3

       # 复合判定：regime 可解释 AND (IC/Sharpe/残差)均无显著退化 → 良性漂移(降级)
       # 否则 → 有业务影响(保留告警)
       # 逻辑：regime 可解释是必要非充分条件——即使 regime 良性，若 IC/Sharpe/残差
       #       已退化，说明漂移已穿透到模型性能，仍须告警（regime 解释≠性能免疫）
       if regime_explained and not ic_degraded and not sharpe_degraded and not loss_inflated:
           return False  # 良性漂移：季节性/regime 导致的特征分布变化，模型性能未受影响
       return True  # 有业务影响：特征漂移已传导到 IC/Sharpe/残差，须保留告警
   ```

   ```python
   def trigger_retraining(strategy_id, trigger_source="performance"):
       """重训练触发分级逻辑（2026-08-10 施工填补，§3.3 第 8 条性能触发落地）

       三触发策略（§3.3 第 8 条，kindatechnical 2026-03 验证）：
       - 定时（schedule-based）：盘后每日增量重训练（保底）
       - 性能（performance-based）：漂移告警触发全量重训练（加速）
       - 数据量（data-volume-based）：新数据 ≥10000 行触发增量重训练
       个人项目默认用定时+性能双触发（定时保底+性能加速）

       输入：strategy_id
             trigger_source="performance"（drift_observatory_orchestrate L216 调用）
                            ="schedule"（盘后定时任务调用）
                            ="data_volume"（数据累积达标调用）
       输出：retrain_job_id（MLflow run id，用于追踪重训练过程）

       分级重训练逻辑：
       - 突发漂移（abrupt，composite ≥0.80 或 Layer 4 coverage_breach）→ 全量重训练
       - 渐进漂移（gradual，性能触发但未达 composite 0.80）→ 增量重训练
       - 定时/数据量触发 → 增量重训练（保底）

       与 §3.3 第 7 条自动回滚的边界：
           回滚=新 Champion 上线 24h-7天内紧急恢复（alias 秒级切换）；
           重训练=Champion 长期退化（盘后离线训练）——本函数是后者。
       与 SBS（arXiv:2607.28577）纪律：
           对比基线是维护态 Champion（持续更新）非部署时 checkpoint。
       """
       # 评估漂移类型：从 drift_observatory 获取最近 composite score 与漂移模式
       composite_score = drift_observatory.get_latest_composite(strategy_id)
       coverage_breach = drift_observatory.get_coverage_breach(strategy_id)
       drift_mode = drift_observatory.classify_drift_mode(strategy_id)  # "abrupt" / "gradual" / "none"

       # 分级决策：突发漂移 → 全量重训练；渐进/定时/数据量 → 增量重训练
       if trigger_source == "performance" and (composite_score >= 0.80 or coverage_breach or drift_mode == "abrupt"):
           retrain_mode = "full"          # 全量重训练：warm-refit 从零训练
       else:
           retrain_mode = "incremental"   # 增量重训练：在现有权重上微调
           # Phase 3 候选：渐进漂移可用 knowledge distillation（§3.3 第 6 条 EWC+伪回放 叠加）
           # teacher=旧 Champion / student=微调后模型，比全量重训练成本低 5-10x
           # （newline.co 2026-04-21：渐进漂移不一定需要全量重训练）

       # 回滚保险：保留旧 Champion 为 @challenger（§3.3 第 7 条自动回滚机制）
       # SBS 纪律（arXiv:2607.28577）：对比基线是维护态 Champion 非部署时 checkpoint
       old_champion_version = mlflow.get_alias_version(strategy_id, "@champion")
       mlflow.set_alias(strategy_id, old_champion_version, "@challenger")  # 旧 Champion 降级为 Challenger

       # 执行重训练：warm-refit Challenger 在服务路径外（不在 @champion 上直接训练）
       # 训练数据用滚动窗口（§3.3 第 9 条 current without being amnesiac）
       retrain_job_id = training_pipeline.fit(
           strategy_id=strategy_id,
           mode=retrain_mode,                           # "full" / "incremental"
           data_window=rolling_window.get_window(),     # 滚动窗口（当前 regime 优先 + 长参考窗口记忆压力事件）
           ewc_regularization=True,                     # §3.3 第 6 条 EWC 防遗忘
           pseudo_replay=True,                          # §3.3 第 6 条 伪回放防灾难性遗忘
           baseline_champion=old_champion_version,      # SBS：对比基线是维护态 Champion
       )

       # 晋升门禁（§3.3 第 9 条）：新模型不自动替换 Champion，须通过量化门禁
       # OOS Sharpe ≥ Champion × 0.9 / profit factor > 1.5 / MaxDD ≤ Champion × 1.2
       # / 子周期一致性 / Sortino + Calmar 三角验证
       promotion_gate = PromotionGate(
           min_oos_sharpe_ratio=0.9,      # OOS Sharpe ≥ Champion × 0.9
           min_profit_factor=1.5,         # profit factor > 1.5
           max_dd_ratio=1.2,              # MaxDD ≤ Champion × 1.2
           subperiod_consistency=True,    # 3-4 子段 Sharpe 均 > 0
           sortino_calmar_check=True,     # Sortino + Calmar 三角验证
       )
       new_version = training_pipeline.get_model_version(retrain_job_id)
       if promotion_gate.evaluate(new_version, baseline=old_champion_version):
           # 门禁通过：新模型晋升 @champion，旧 Champion 保留 7-30 天回滚保险
           mlflow.set_alias(strategy_id, new_version, "@champion")
           rollback_manager.arm_rollback(strategy_id, old_champion_version, ttl_days=30)
           notify(strategy_id, "PROMOTED", f"新 Champion {new_version} 通过门禁晋升")
       else:
           # 门禁未通过：保留旧 Champion，新模型落 @archived 待诊断
           mlflow.set_alias(strategy_id, new_version, "@archived")
           notify(strategy_id, "PROMOTION_FAILED",
                  f"新模型 {new_version} 未通过门禁，保留 Champion {old_champion_version}")

       return retrain_job_id
   ```

   **施工要点**：① downstream_impact_gate 四步检查遵循"regime 可解释 + IC/Sharpe/残差均无退化 = 良性"的复合判定，避免单一指标误判（如仅 regime 可解释但 IC 已崩塌仍应告警——regime 解释是必要非充分条件）；② IC 衰减阈值 0.05 / Sharpe 退化阈值 0.7 / 残差膨胀阈值 1.3 三者与 §3.3 第 5 条 Decay Detection + §3.3 第 7 条回滚阈值对齐，非独立标定；③ trigger_retraining 分级决策——突发漂移（composite ≥0.80 / coverage_breach）全量重训练，渐进漂移/定时/数据量增量重训练，Phase 3 渐进漂移可升级 knowledge distillation（比全量重训练成本低 5-10x）；④ 回滚保险遵循 SBS 纪律（arXiv:2607.28577）：对比基线是维护态 Champion 非部署时 checkpoint，新模型经 §3.3 第 9 条晋升门禁后才晋升 @champion，旧 Champion 保留 30 天回滚窗口；⑤ trigger_source 参数区分三触发来源（performance/schedule/data_volume），performance 触发走全量重训练路径，schedule/data_volume 走增量重训练保底路径——与 §3.3 第 8 条"个人项目默认定时+性能双触发"对齐；⑥ 两个函数复用 drift_observatory / ic_tracker / performance_tracker / loss_tracker / regime_detector / training_pipeline / mlflow / promotion_gate / rollback_manager 等现有组件，无新基础设施——符合 MVP 分批原则

   - **选项之外更好的算法候选——GMM unexplained mass drift detection**（[arXiv:2607.16811v2 2026-07-27](https://arxiv.org/pdf/2607.16811v2)）：将 GMM（Gaussian Mixture Model）每个 Gaussian component 视为一个 named "regime"，stream window 中匹配 no regime 的样本比例（unexplained mass）即为 drift signal，drift alarm 同时报告"哪个 regime 失效"。**与本项目 regime 检测器天然契合**——现有 HMM regime 检测器（10_regime_detector_spec）的 12 态可对应 GMM 的 12 个 Gaussian component，GMM unexplained mass 可作为 regime 检测器的 drift 守护层。优势：①可解释（每个 alarm 归因到具名 regime）；②单一模型同时做异常检测 + 漂移检测；③benchmark 显示在"漂移形成新 regime"场景匹配 MMD 检测能力（[arXiv:2607.16811v2 2026-07-27](https://arxiv.org/pdf/2607.16811v2)：MMD is the strongest pure detector, but the interpretable unexplained-mass statistic matches it when anomalies form novel regimes）。**定位**：Phase 4 鲁棒性候选（与 Wasserstein HMM 并列），C1 验证 + 漂移检测主路径稳定后评估融合可行性
   - **选项之外更好的算法候选——knowledge distillation 渐进漂移适应**（[newline.co 2026-04-21](https://www.newline.co/@Dipen/top-5-reinforcement-methods-for-finance-2026--3d4582d3)）：渐进漂移（gradual drift）不一定需要全量重训练——**knowledge distillation** 从历史模型提取知识（teacher）+ 用新分布数据微调（student），既适应新分布又不丢历史知识（比 EWC 更轻量）。**与本项目 §3.3 第 6 条 EWC + 伪回放的关系**：EWC 是"防遗忘"正则项，knowledge distillation 是"教师-学生"迁移，两者可叠加——EWC 约束 student 不偏离 teacher 的关键权重，distillation 软标签辅助 student 学习新分布。**定位**：渐进漂移场景的轻量适应候选（比全量重训练成本低 5-10x），突发漂移仍走全量重训练。Phase 3 候选验证
   - **选项之外更好的算法候选——SHAP Drift Attribution 漂移归因**（[emitechlogic 2026-04-14](https://emitechlogic.com/how-to-detect-and-fix-production-drift-in-machine-learning-complete-guide/)）：上述漂移检测方法（PSI/KS/MMD/CUSUM）回答"是否漂移"，但不回答"哪个特征导致了漂移"——**SHAP Drift Attribution** 用 SHAP 值归因漂移到具体特征，实现漂移定位（drift localization）。**流程**：检测到漂移 → 对漂移窗口样本计算 SHAP 值 → 对比基线窗口 SHAP 分布 → SHAP 偏移最大的特征即为漂移根因。**与 §3.3 第 4 条下游影响门控的关系**：下游影响门控过滤"统计显著但业务不显著"的漂移，SHAP 归因回答"漂移根因是哪个特征"——两者互补，前者减误报，后者加速诊断。**学术支撑**（[arXiv:2602.19790 2026-04](https://arxiv.org/pdf/2602.19790.pdf)，Bielefeld University）：Conformal-prediction-based drift localization 替代 local testing，在高维低信号场景下优于传统局部检验。**定位**：Phase 3 诊断增强候选（漂移告警后加速根因定位，减少人工排查时间）
  - **选项之外更好的算法候选——Modular CP via Residual Decomposition 多阶段不确定性归因**（[arXiv:2510.04406](https://arxiv.org/abs/2510.04406)，2025-10）：上述 SHAP Drift Attribution 归因到"哪个特征漂移"（特征级），ARM 归因到"哪些坐标/资产变了"（资产级），但量化 pipeline 是多阶段系统（特征工程→因子合成→组合优化→执行），**漂移可能发生在任一阶段且向上/向下传导**——某阶段漂移可能是上游传导（如特征漂移导致因子合成失效）而非该阶段自身问题。**Modular CP（Modular Conformal Prediction via Residual Decomposition）**将多阶段系统的总预测残差 R 分解为上游预测误差（ΔR₁）和下游模型误差（R₂），实现**阶段特异性不确定性归因**——`R ≤ ΔR₁ + R₂`，通过分离组件量化各阶段贡献，定位漂移根因（上游特征漂移 vs 下游模型失效）。**核心机制**：每个 pipeline 阶段维护独立的 conformal calibration set + 残差分解，总残差分解为各阶段残差之和，每阶段残差用该阶段校准集做 conformal coverage 检验——某阶段覆盖失效即定位到该阶段为漂移根因。**与 SHAP Drift Attribution 的互补**：SHAP 定位具体特征漂移（特征级），Modular CP 定位阶段失效（阶段级），构成"特征级+阶段级"二级诊断链——SHAP 回答"哪个特征漂移了"，Modular CP 回答"漂移发生在 pipeline 哪个阶段"。**与 ARM 变点归因的关系**：ARM 归因"哪些坐标/资产变了"（资产级），Modular CP 归因"哪个阶段失效"（阶段级）——三者构成"特征级→阶段级→资产级"三级漂移归因体系。**对量化交易的特殊意义**：本项目 pipeline 阶段数 >3（特征工程→因子合成→组合优化→执行），某阶段漂移可能是上游传导而非该阶段自身问题——Modular CP 能区分"传导性漂移"与"原生漂移"，避免误诊断后重训练错误阶段（如特征漂移导致因子失效时重训练因子合成而非修复特征工程是浪费资源）。**与 Layer 4 Conformal Prediction 的关系**：Layer 4 CP 用单一校准集做全局覆盖保证，Modular CP 用多阶段校准集做分阶段覆盖保证——后者是前者的"精细化"（从全局覆盖到阶段级覆盖），填补"全局覆盖失效但无法定位到哪个阶段"的盲区。**本项目定位**：Phase 3 漂移诊断增强候选，与 SHAP 归因同期评估——当 pipeline 阶段数 >3 时，Modular CP 的阶段归因价值显著（单阶段 pipeline 无归因需求）。**不过度工程审查**：Modular CP 需维护各阶段残差分解 + 阶段间误差传递矩阵 + 各阶段独立校准集，~150-200 行增量，是 SHAP/ARM 归因的阶段级补充非独立组件——符合 MVP 分批原则
   - **选项之外更好的算法候选——Drift Robustness 模型漂移鲁棒性评估**（[emitechlogic 2026-04-14](https://emitechlogic.com/how-to-detect-and-fix-production-drift-in-machine-learning-complete-guide/)）："Not all models age the same way"——不同模型架构对漂移的鲁棒性差异显著（如树模型对特征尺度漂移鲁棒但对特征重要性漂移敏感，线性模型反之）。**评估方法**：在验证期注入可控漂移（controlled augmentation，如均值平移/方差缩放/特征旋转），测量不同模型的性能退化曲线——退化斜率小的模型漂移鲁棒性更强。**与 §3.3 第 3 条对抗鲁棒性的关系**：对抗鲁棒性测试输入被"恶意扰动"的极端情况，漂移鲁棒性测试输入被"自然漂移"的渐进情况——两者正交，均属上线前鲁棒性门禁。**定位**：Phase 3 Champion-Challenger 选型辅助（Challenger 不仅比 Champion 业务指标好，还须漂移鲁棒性不劣于 Champion）
   - **选项之外更好的答案算法——Conformal Prediction 可证覆盖层（Layer 4 数学保证，2026-08 重大发现）**：上述所有漂移检测方法（PSI/KS/MMD/CUSUM/ADWIN/Wasserstein/composite drift score）都是**启发式阈值**——"PSI > 0.25 = 材料性漂移""CUSUM 超 4σ = 告警"等阈值依赖经验标定，无数学保证。**Conformal Prediction（保形预测）** 提供根本性更强的保证——**有限样本覆盖保证**（finite-sample coverage guarantee）：`P(Y_{n+1} ∈ Ĉ(X_{n+1})) ≥ 1 - α`，对任意分布、任意模型、任意样本量成立，仅需可交换性（exchangeability，比 IID 更弱假设）（[marketmaker.cc 2026-06-12](https://marketmaker.cc/en/blog/post/conformal-prediction-trading/)：If you ask for 90% coverage, you get at least 90% coverage — regardless of whether returns are Gaussian, fat-tailed, skewed, or heteroskedastic；[bcub3 2026-06-22](https://www.bcub3.com/en/blog/conformal-prediction-intervalles-confiance-industrie/)：the only method offering finite-sample coverage guarantee without assuming anything about the error distribution or the model）。**核心机制**（split conformal 四步）：① 训练集拟合模型 μ̂；② 校准集计算非一致性分数 `sᵢ = |yᵢ - μ̂(xᵢ)|`（"模型错多少"）；③ 取 `(1-α)` 分位数 q̂；④ 新样本预测区间 `Ĉ = [μ̂(x) - q̂, μ̂(x) + q̂]`。q̂ 是经验分位数，无需分布假设——模型越差区间越宽，但覆盖保证始终成立。**三层应用价值**：① **漂移检测（Layer 4 可证层）**——监控实际覆盖率，当实际覆盖 < 名义覆盖 (1-α) 时漂移已发生（**数学保证的漂移信号，非启发式阈值**）；bonnie-mcconnell/model_monitor 四层架构 Layer 4 = Conformal coverage "Provable model quality bound, Mathematical guarantee, not heuristic"（[model_monitor 2026-06](https://github.com/bonnie-mcconnell/model_monitor)）；② **仓位管理**——预测区间宽度 = 动态风险信号，区间宽时不确定性高→保守仓位，区间窄时→可放大仓位（[suenot/278 2026-03](https://github.com/suenot/278-prediction-intervals-trading)：interval width serves as a dynamic risk signal, wider intervals trigger more conservative position sizing；[marketmaker.cc 2026-06-12](https://marketmaker.cc/en/blog/post/conformal-prediction-trading/)：Conformal Prediction for Risk-Aware Position Sizing）；③ **VaR 校准**——regime-weighted conformal calibration (RWC) 用指数时间衰减 + regime 相似性权重构建安全缓冲，wrap 任意条件分位数预测器，在 CRSP 指数 + 16 个美国股票组合 Basel 99%/97.5% 级别验证（[arXiv:2602.03903v3 2026-08-03](https://arxiv.org/html/2602.03903v3)，Oxford, Marc Schmitt）——**直接对接本项目 36号 var_calculator 的 VaR 校准**。**金融收益特殊处理——可交换性违反**（[conformal.marketmaker.cc Soloviov 2026](https://conformal.marketmaker.cc/) 180 实验 14 方法）：金融收益违反可交换性（波动率聚集/均值漂移/regime 突变），经典 conformal 边际覆盖在平稳依赖下仍存活（iid/AR(1)/GARCH: 0.901/0.901/0.895），仅突变 DGP 轻微下降（0.877）；**条件覆盖是真正 casualty**——GARCH 下绝对分数区间在波动率三分位覆盖 0.952/0.915/0.820（最需要诚实的高波动区低估 8 个百分点）；**修复方案**：① **EWMA 波动率归一化分数**（spread 0.134→0.040，几乎无成本）；② **ACI（Adaptive Conformal Inference）**突变后修复（0.562→0.700-0.875，宽度成本 1.12-1.14× oracle）；**配方**：normalize conformal scores by volatility proxy + add ACI when breaks are a concern + treat parametric narrowness as coverage liability。**CP ↔ VaR 等价**（[PMLR 266 Retzlaff et al. 2025](https://proceedings.mlr.press/v266/retzlaff25a.html)）：建立 CP 与 VaR 形式等价，使 VaR 回测方法（Dynamic Binary Test / Geometric Conformal Backtesting）可用于统计检验 CP 覆盖——本项目 var_calculator 的 VaR 回测基础设施可直接复用于 CP 覆盖检验。**流式非平稳扩展——DASC**（[arXiv:2606.15953v2 2026-07](https://arxiv.org/html/2606.15953v2)，Drift-Aware Spectral Conformal Prediction）：用谱相似性加权校准残差（recurring regimes 跨时共享信息），追踪 drift score 标记校准池与当前 regime 不匹配，在线调整误覆盖水平；在**金融波动率**真实数据验证（§12 Real Data: Financial Volatility）——**与本项目 regime 检测器天然契合**（regime 相似性权重 = HMM regime 距离）。**本项目定位**：Conformal Prediction 是 Drift Observatory 的 **Layer 4 可证覆盖层**——Layer 1-3（特征/预测/结果监控）是启发式检测（快但有误报），Layer 4 是数学保证检测（慢但零误报）。**施工优先级**：Phase 3 候选（C1 验证 + 漂移检测主路径稳定后），先在 var_calculator（36号）试点 RWC VaR 校准（已有 VaR 回测基础设施可复用），再扩展到信号置信度区间 + 仓位管理。**不过度工程审查**：CP 是 wrapper（wrap 已有模型，不改模型本身），实现成本 = 校准集分位数计算 + 覆盖率监控 <100 行，且 VaR 校准试点可复用 36号现有回测设施——符合 MVP 分批原则
   - **Conformal Prediction 流式突变处理——ACI 缺陷与 calibration flush 最优解（2026-02/07 最新研究重大修正）**：上述 Layer 4 提到"ACI 突变后修复（0.562→0.875）"，但 2026-02 最新研究证明 **ACI 本身在 regime shift 后有严重缺陷**——ACI 的覆盖保证是**边际覆盖**（marginal coverage），即"长期时间平均覆盖率 ≥ 1-α"，但此保证**允许方法在 regime shift 后持续 60-80 步严重欠覆盖**，只要后续过覆盖补偿即可——欠覆盖期与恢复期平均掉，纸面 valid 但实盘在"最需要有效区间"的时段"飞行盲打"（[burning-cost 2026-03-31](https://burning-cost.github.io/2026/03/31/optimal-regret-online-conformal-prediction-distribution-drift/)：ACI gamma=0.005 在 +20% step shift 下首半程覆盖 66.7%、后半程 91.7%，长期平均可接受但首半程严重欠覆盖）。**minimax 最优解——calibration flush 非 ACI 被动降权**（[arXiv:2602.16537](https://arxiv.org/pdf/2602.16537)，Liang, Ren & Chen, Princeton/Wharton 2026-02）：论文证明 minimax 最优算法不是 ACI 的被动降权（passive decay），而是 **CUSUM 漂移检测 + 校准集冲刷**——CUSUM 检测到 regime change 时**完全丢弃陈旧校准集**，用 drift 后新分数重建（flush calibration set, rebuild from post-drift scores）；minimax 下界 O(√(KT))（K=变点数，T=时域长度）证明无算法可超越此率，calibration flush 达到此率。**训练条件遗憾**（training-conditional regret）是比边际覆盖更严格的准则——不平均所有可能训练历史，而是条件于实际部署的那个模型（"marginal coverage 是组合损失率，训练条件遗憾是单账户视角"）。**ACI 符号覆盖误差局限**（[arXiv:2607.26577](https://arxiv.org/abs/2607.26577)，Vaze 2026-07-29）：ACI 仅控制**有符号**长期覆盖误差——持续单向欠覆盖可被后续过覆盖"符号抵消"掩盖；论文提出**同时控制绝对非抵消覆盖违反 + 预测集效率**，对抗设定下利用 ACI 更新即 pinball loss 上的投影在线梯度下降导出对任意单调 Lipschitz 效率目标的同时保证，随机设定下提出 sliding-window quantile tracker 并建立 matching minimax 下界（rate-optimal）。**TCP 框架实证**（[arXiv:2507.05470v5](https://arxiv.org/html/2507.05470v5)，Aich et al. 2025-12）：Temporal Conformal Prediction = 滚动 split-conformal + 分位数预测器 + TCP-RM 变体加 Robbins-Monro 在线偏移，在 S&P 500/Bitcoin/Gold 三资产类 95% 覆盖验证，危机窗口（2020-03）区间带随波动率飙升/回落 promptly 扩张/收缩。**本项目定位修正**：Layer 4 Conformal Prediction 的突变处理**不依赖 ACI 被动降权**，而采用 **CUSUM 漂移检测（§3.3 第 4 条残差漂移已有 CUSUM 基础设施）+ calibration flush**——CUSUM 告警时丢弃陈旧校准集、用 post-drift 分数重建。这与残差漂移 CUSUM 检测器天然复用（同一 CUSUM 既能检残差漂移又能触发 CP 校准集冲刷），且 calibration flush 的"完全丢弃"比 ACI"缓慢降权"在 regime shift 后恢复更快（ACI 需 60-80 步补偿，flush 立即重建）。**不过度工程审查**：calibration flush = CUSUM 已有检测器 + 校准集清空操作，<20 行增量代码，复用 §3.3 CUSUM 基础设施——符合 MVP 分批原则
   - **BC-ACI 偏置校正——ACI/calibration flush 的宽度 vs 中心盲区（2026-04 最新研究，施工算法缺失补充）**：上述 calibration flush 解决了 regime shift 后的"陈旧校准集"问题（宽度调整），但 **ACI 和 calibration flush 都只调整分位数阈值（区间宽度），无法移动区间中心**——当部署的模型在分布漂移后产生**持续预测偏置**（persistent prediction bias，如 regime 切换后模型系统性高估/低估），ACI 被迫对称膨胀区间以维持覆盖，宽度开销正比于 `2|b|`（b 为偏置幅度）（[arXiv:2604.13253](https://arxiv.org/pdf/2604.13253)，Lade et al. 2026-04）。**实证**：ridge regression 在 level shift δ=5 后残差均值 b≈3.99，ACI 区间宽度 8.67，oracle（已知偏置）宽度仅 3.43（60% 削减），BC-ACI 在线估计偏置并纠正非一致性分数后宽度 5.50（37% 削减）。**BC-ACI 机制**：在 ACI 的 `α_{t+1}=α_t+γ(α-err_t)` 更新规则之上，叠加 per-horizon 在线指数加权偏置估计 `b̂_t = EWMA(e_t)`，纠正非一致性分数 `s̃_t = s_t - b̂_t` 后再计算分位数，配合自适应死区阈值（MAD-based dead-zone）防止估计噪声在无偏置时退化区间。**关键特性**：① 保留 ACI 渐近覆盖保证（Theorem 3）；② 有偏置模型（ridge regression after level shift）Winkler 分数改善 32%，自校正模型（ARIMA）中性无副作用（<0.2% 开销，Theorem 5）；③ **对量化交易的特殊意义**——模型在 regime 切换后常产生持续方向偏置（如牛市训练的模型在熊市系统性高估），BC-ACI 纠正中心 + calibration flush 重建宽度 = **双重保护**（宽度+中心），而非二选一。**与 calibration flush 的关系**：calibration flush 是"完全丢弃陈旧校准集重建"（解决宽度问题），BC-ACI 是"在线估计并纠正偏置中心"（解决中心问题）——两者正交互补，可叠加使用：CUSUM 告警 → calibration flush 重建校准集 → BC-ACI 持续纠正残余偏置。**不过度工程审查**：BC-ACI = ACI 更新规则 + EWMA 偏置估计 + 死区阈值，<30 行增量代码，与 calibration flush 叠加无冲突——符合 MVP 分批原则
   - **选项之外更好的算法候选——SA-BCP 时空解耦贝叶斯共形预测**（[arXiv:2605.00432](https://arxiv.org/html/2605.00432v1)，2026-05，台湾大学 Fang & Lee）：上述 Layer 4 Conformal Prediction 的 ACI（反馈驱动自适应）与 Bayesian CP（时间折扣）面临持续困境——ACI 在突变时系统性边际欠覆盖 + 区间方差高，Bayesian CP 防覆盖坍缩但结构滞后 + 区间膨胀。**SA-BCP（State-Adaptive Bayesian Conformal Prediction）**实现**时空最优解耦**——用空间核密度证据门控长期时间惯性：识别到历史 regime 时主动扩展区间（proactive expansion），稳定态时保持紧效率。**核心贡献**：① 时空解耦 CP 框架（平衡近期惯性与历史模式记忆，基于认知密度的激活机制）；② 严格理论分析证明空间匹配参数 K 决定 minimax bias-variance 权衡下的最优性（Theorem 4 给出最优 K 的闭式界）；③ 在波动金融数据集（2016-2026，AMD/Gold/GBP/USD）上，SA-BCP 在所有置信水平上一致最小化 Winkler 分数，**解决 ACI 变体的系统性欠覆盖同时将 Bayesian CP 的区间膨胀减少 10%-37%**。**与 ACI/calibration flush 的关系**：ACI 是纯反馈驱动（被动适应），calibration flush 是突变后完全丢弃重建（激进重建），SA-BCP 是空间证据门控的时间惯性（主动预防）——三者代表"被动适应→激进重建→主动预防"的 CP 突变处理谱系。**与 BC-ACI 的关系**：BC-ACI 纠正全局序列偏置（中心问题），SA-BCP 用空间证据门控时间惯性（结构问题）——两者正交：BC-ACI 管偏置中心，SA-BCP 管区间结构。**与 DASC 的关系**：DASC 用谱相似性加权校准残差（regime 循环场景），SA-BCP 用空间核密度证据门控时间惯性（regime 识别场景）——两者互补：DASC 管 regime 循环信息共享，SA-BCP 管 regime 识别主动扩展。**对量化交易的特殊意义**：A 股 regime 切换频繁（牛→熊→震荡），SA-BCP 的"识别到历史 regime 时主动扩展区间"可在 regime 切换前提前加宽区间（而非 ACI 的事后补偿或 calibration flush 的事后重建），对 T+1 制度下"当日决策次日执行"的场景尤其有价值——预测区间在决策时已反映 regime 风险。**本项目定位**：Phase 4 鲁棒性候选——Layer 4 CP 主路径（calibration flush + BC-ACI）稳定后，当"ACI 突变欠覆盖"或"Bayesian CP 区间膨胀"成为瓶颈时评估 SA-BCP 升级。**不过度工程审查**：SA-BCP 需空间核密度估计 + 认知密度激活机制 + K 参数标定（minimax 最优 K 需数据驱动估计），比 calibration flush（<20 行）重，记为 Phase 4 候选不立即施工
  - **CPTC 变点检测替代——calibration flush 的经验替代路径（NeurIPS 2025，选项之外更好的答案算法）**：上述 calibration flush 是 minimax 最优的理论解，但 [arXiv:2509.02844](https://arxiv.org/abs/2509.02844)（Zaffran/Goude/Dieuleveut，NeurIPS 2025）提出 **Conformal Prediction with Change Points (CPTC)** 作为经验替代——用 **RED-SDS**（Recurrent Explicit Duration Switching Dynamical System）结构断裂检测器替代 CUSUM，检测到 regime change 时**立即重置 conformal 分位数**到新 regime 的校准分位数（而非 calibration flush 的"丢弃重建"）。**关键差异**：① CPTC 每个 regime 独立学习率（per-regime learning rate）而非全局单一 γ；② RED-SDS 比简单 CUSUM 对噪声非平稳时序更鲁棒（维护 regime 后验概率，非二元告警）；③ 经验覆盖间隙 3-5pp（CPTC）vs 20pp（ACI）vs 12pp（FACI）——在突变后前 12 步内显著优于 ACI/FACI。**与 calibration flush 的取舍**：calibration flush 理论更强（minimax 最优 O(√(KT))）+ 实现更轻（复用 CUSUM）；CPTC 经验覆盖间隙更小（3-5pp vs flush 的理论界）+ 检测器更鲁棒（RED-SDS vs CUSUM），但 RED-SDS 需训练循环切换动力学系统（重得多）。**本项目定位**：calibration flush 为主路径（复用 CUSUM 基础设施 + minimax 最优 + <20 行），CPTC 作为 Phase 4 鲁棒性候选（当 CUSUM 误报率高时评估升级到 RED-SDS + per-regime 学习率）。**不过度工程审查**：CPTC 需训练 RED-SDS（循环神经网络）+ 多 regime 状态管理，对个人项目当前阶段过重，记为 Phase 4 候选不立即施工
   - **WCTM 统一框架——适应/检测/诊断三合一（ICML 2025，选项之外更好的答案算法）**：上述 mSPRT（§3.3 第 1 条 Champion-Challenger）和 Conformal Prediction（Layer 4）是两条独立路径——mSPRT 做序贯检验（二元 reject/accept），Conformal 做覆盖保证（区间宽度）。[arXiv:2505.04608](https://arxiv.org/html/2505.04608v2)（WATCH: Weighted-Conformal Test Martingales, ICML 2025）提出 **WCTM** 把"在线适应轻度协变量漂移（不告警）+ 快速检测严重漂移（concept shift / 极端 out-of-support covariate shift）+ 根因分析"统一到一个加权 conformal test martingale 框架——现有 CTM（Conformal Test Martingale）不支持在线适应（要么检测要么不检测），WCTM 用加权机制实现"轻度漂移自适应、严重漂移才告警"的分级响应。**与现有方法的关系**：mSPRT 是"检验"框架，Conformal Prediction 是"覆盖"框架，WCTM 是"适应+检测+诊断"三合一框架——三者正交，WCTM 填补了"轻度漂移不应告警但应自适应"的中间地带（当前靠 retraining 触发，粗粒度）。**本项目定位**：Phase 4 鲁棒性候选——当前 CUSUM+Conformal 分工（CUSUM 检测+Conformal 覆盖）已覆盖"检测+覆盖"，WCTM 可提供细粒度在线自适应。**不过度工程审查**：WCTM 需维护加权 test martingale + 在线适应机制，比 CUSUM+Conformal 重，记为 Phase 4 候选不立即施工
   - **DASC 谱共形 Phase 4 候选登记——regime 循环场景的 CP 校准升级**（[arXiv:2606.15953v2, 2026-07](https://arxiv.org/html/2606.15953v2)，Opoku & Banahene, UT Rio Grande Valley）：上述 Conformal Prediction Layer 4 主路径用 calibration flush（CUSUM 检测+完全丢弃重建）处理突变，但 **regime 循环场景**（recurring regimes，如 A 股季节性模式周期性重现）下完全丢弃会丢失"跨时共享信息"。**DASC（Drift-Aware Spectral Conformal Prediction）**用**谱相似性加权校准残差**——recurring regimes 跨时共享信息，追踪 drift score 标记校准池与当前 regime 不匹配，在线调整误覆盖水平。**三大组件**：① drift-gated calibration window（漂移门控校准窗口）；② spectral similarity weighting（谱相似性加权，regime 距离 = 谱距离）；③ DASC diagnostic triangle（drift score + coverage gap + reliability index 三角诊断）。**理论保证**：在"谱 Lipschitz 条件"（残差分布的可测性质）下证明 per-step 覆盖界。**金融实证**：论文 §12 在**金融波动率**真实数据验证，对比 EnbPI/AgACI baseline。**与 calibration flush 的关系**：calibration flush 是"突变后完全丢弃重建"（minimax 最优但丢循环信息），DASC 是"谱加权保留循环 regime 信息"（regime 循环场景更优）——两者互补：突变走 flush，循环走 DASC。**与本项目 regime 检测器契合**：DASC 的谱相似性权重 = HMM regime 距离，现有 10号 regime 检测器的 12 态可直接作为谱加权输入。**本项目定位**：**Phase 4 鲁棒性候选**——Phase 3 基础 CP（calibration flush 主路径）稳定后，当 regime 循环（季节性模式重现）成为校准瓶颈时评估升级到 DASC 谱加权。**不过度工程审查**：DASC 需维护谱相似性矩阵 + drift-gated 窗口 + diagnostic triangle，比 calibration flush（<20 行）重，记为 Phase 4 候选不立即施工
   - **Conformal Kelly 交叉引用断点——漂移检测层→仓位管理层的缺失桥梁（arXiv:2608.01494, 2026-08-02 最新研究，施工算法缺失补充）**：上述 Conformal Prediction Layer 4 已对接 36 号 VaR 校准（RWC regime-weighted conformal），但**未对接 31 号 Kelly 仓位计算 / 35 号 Conformal Kelly drawdown dial**——Conformal 区间宽度变化（漂移信号）未传导到仓位 sizing，是"检测→响应"链路的断点。[arXiv:2608.01494](https://arxiv.org/html/2608.01494v1)（Conformal Kelly: Conformal Prediction Intervals as the Scale in Fractional Kelly Position Sizing, 2026-08-02）填补此断点——**将 conformal prediction 区间用作仓位 sizing 的"标度"**：区间变宽→缩仓（不确定性增加）；区间变窄→加仓（不确定性减少）。**核心设计原则（与现有文献相悖）**：所有让区间更快适应当前市场的方法都损失 0.7-5.3 个百分点年化增长——**最好的是最简单的 slow/unweighted per-asset rolling conformal quantiles**，因为"作为仓位标度时，宽度的稳定性比局部锐度更重要"。**实证**：2016-2021 开发窗口 28.5% 年化 log 增长，Sharpe 1.34，最大回撤 27.7%；当 conformal 区间在 downside 上 miss 远超历史率时削减杠杆，回撤从 27.7% 降到 20.3%。**三层传导链补全**：Layer 4 Conformal（漂移检测+区间宽度）→ 35 号 `conformal_kelly_drawdown_dial`（v1.19.0 §3.19 已有施工骨架：slow unweighted rolling miss rate + 线性 leverage 缩减 + 0.5 下限防 cash-lock）→ 31 号 Kelly（仓位计算）。当前文档仅覆盖 Layer 4→36 号 VaR，缺 Layer 4→35 号→31 号链路——本次补全交叉引用断点，Layer 4 的区间宽度变化应作为 35 号 conformal_scale 的**上游输入**
   - **Report the Floor 强基线参照——ConformalNaive 5 行代码击败 NPTS 家族（arXiv:2606.09473, 2026-06）**：[arXiv:2606.09473](https://arxiv.org/pdf/2606.09473v1)（Report the Floor: A Training-Free Conformal Interval Is a Mandatory Baseline, 2026-06）在 2,217 个真实序列上实证——**最简单的 ConformalNaive**（最后值点预测 + split-conformal 残差分位数，5 行代码无训练）在一步预测上**击败整个 NPTS 家族**（NPTS 73%、SeasonalNPTS 64% 序列胜出）和 CSP 方法（71% 背书），与简单学习型 conformal 持平，只输给显式跟踪分布漂移的 adaptive-online 方法（SPCI/ACI/AgACI，落后 9-33%）。**对本项目的意义**：Layer 4 Conformal Prediction 实现时，**ConformalNaive 是 mandatory baseline**——先实现 5 行 ConformalNaive 作为 floor，再叠加 ACI/calibration flush/BC-ACI 等自适应方法，若自适应方法不能显著超越 ConformalNaive 则不值得其复杂度。还发现 DeepNPTS 在校准上是最差方法（66% vs 名义 95%）——警示不要盲目使用复杂模型
   - **远期候选登记（不过度工程审查）**：① **CEP**（Continuous Evolution Pool, [arXiv:2506.14790](https://arxiv.org/pdf/2506.14790v2)）——针对循环概念漂移（recurring drift，季节性模式周期性重现但模型在非重现期遗忘），维护专用预测器动态池 + 统计基因解耦概念识别与预测，无需历史 ground truth 即可 >20% 误差降低。**不过度工程审查**：CEP 的"预测器动态池+检索+进化+淘汰"闭环对个人项目过重（需维护多模型池+检索机制），与 MVP 分批+风险优先原则不符，记为远期候选（策略数 >10 且循环漂移成为主要故障模式时评估）；② **ProteuS**（[arXiv:2509.11844](https://arxiv.org/html/2509.11844v1)，代码 github.com/cetrulin/regime-switching-series-generator）——ARMA-GARCH 拟合真实 ETF 数据仿真渐进/突变体制转换，提供已知 ground truth 的结构断点作为漂移检测评测基准。**本项目定位**：Phase 3 验证阶段候选——当前漂移检测器（CUSUM/ADWIN/PSI/KS/MMD/Wasserstein）缺乏统一评测平台，ProteuS 可作为"已知断点回测"基准工具；③ **FIDI Z-Score**（[dataforcee 2026-03](https://dataforcee.us/2026/03/23/neuro-symbolic-fraud-detection-catching-concept-drift-before-f1-drops-label-free/)）——零标签检测概念漂移，5/5 seed 全检出有时在 F1 下降前触发，~50 行代码。**重要局限**：covariate drift 是盲区需独立原始特征监控器。**本项目定位**：与现有 CUSUM/ADWIN 互补（标签自由检测），但 covariate drift 盲区限制其独立使用，记为远期观察
   - **T+1 标签延迟漂移检测——DT-GOL 双轨几何在线学习**（[arXiv:2606.22950, 2026-06-22](https://arxiv.org/abs/2606.22950)，施工算法缺失填补）：上述 Drift Observatory Layer 3（ADWIN 概念漂移 + 标签漂移）已标注"延迟 ground truth"但**未提供标签延迟的处理机制**——A 股 T+1 制度下当日买入次日才能卖出，收益标签天然延迟 1 天，Layer 3 的概念漂移检测须等标签到达才能触发，检测延迟 = 标签延迟 + 检测算法延迟。**DT-GOL（Dual-Track Geometric Online Learning）**专解标签延迟问题——用特征空间的实时拓扑演化作为不可观测概念变化的**几何代理**（无需等待标签），通过动态证据校准把几何信息蒸馏成感知不确定性的**软标签**。**双轨架构**：① 主学习器（严格用延迟真值更新，稳定锚，不受软标签噪声污染）；② 瞬态分支（用几何软知识前向适配，低风险，标签到达前即可响应）。**与现有 Layer 3 的关系**：Layer 3 的 ADWIN 须等标签到达才检测概念漂移（被动），DT-GOL 的瞬态分支用几何代理在标签到达前即可预警（主动）——两者互补：DT-GOL 做早期预警，ADWIN 做标签到达后的确认。**本项目定位**：Phase 3 候选——T+1 标签延迟是 A 股固有约束，DT-GOL 的双轨设计让主模型不被软标签噪声污染同时瞬态分支能快速响应盘中信号变化。**不过度工程审查**：DT-GOL 需维护特征空间拓扑演化 + 几何代理 + 软标签蒸馏，比简单 ADWIN 重，但 T+1 标签延迟是 A 股硬约束非可选优化——记为 Phase 3 候选（C1 验证 + 漂移检测主路径稳定后评估），Phase 1 用"标签到达后 ADWIN 检测 + 标签到达前 Layer 1/2 特征/预测漂移先行预警"的简化方案过渡
   - **表演性漂移检测——CB-PDD 检测策略自身交易导致的市场反馈漂移**（[arXiv:2412.10545v2, 2025-04](https://arxiv.org/pdf/2412.10545v2)，选项之外更好的算法候选）：上述所有漂移检测方法（PSI/KS/MMD/CUSUM/ADWIN/Conformal）都假设漂移是**外生的**（市场环境变化导致分布偏移），但量化交易存在一类特殊漂移——**表演性漂移（performative drift）**：模型自身的预测/交易行为反过来引发未来分布变化（如自动交易的自实现/自否定反馈环、alpha 被自身交易套利掉）。**CB-PDD（CheckerBoard Performative Drift Detection）**能区分"内在漂移"（exogenous，市场环境变了）与"表演性漂移"（endogenous，策略自身交易导致），避免传统漂移检测器无法区分漂移来源的盲点。**对量化交易的特殊意义**：alpha 衰减的 Five Horsemen ① Crowding（41%）本质就是表演性漂移——资本涌入→信号被套利→价差压缩，传统 CUSUM/ADWIN 能检测到"分布变了"但无法归因到"是自己交易导致的还是市场环境变了"。**与 §3.3 第 5 条五骑士分类法的关系**：五骑士是定性归因框架（事后），CB-PDD 是检测框架（事中）——CB-PDD 在漂移告警时即可判断"是外生还是自致"，加速五骑士归因中的 ① Crowding 判定。**本项目定位**：Phase 3 候选——个人项目资金量小，自身交易对市场冲击可忽略，但同一信号被多人使用（如开源因子/公开策略）时仍产生表演性效应；CB-PDD 可用于诊断"策略是否在自我消耗 alpha"。**不过度工程审查**：CB-PDD 需建立"策略交易行为→市场反馈"的因果模型，对个人项目当前阶段偏重，记为 Phase 3 候选（策略 AUM 扩大或检测到 crowding 类衰减时评估）
   - **Anytime-valid 共形覆盖监测——Layer 4 覆盖率监测的偷看惩罚填补（arXiv:2602.04364, 2026-02，Hultberg/Bates/Candès，施工算法缺失填补）**：上述 Layer 4 说"监控实际覆盖率，当实际覆盖 < 名义覆盖 (1-α) 时漂移已发生"，但**覆盖率监测本身存在多重检验问题**——若每月检查一次覆盖率（标准治理实践），12 个月跑 12 次检验，每次 α=0.10，则 family-wise error rate 膨胀至 `1-(1-0.10)^12 ≈ 72%`（[burning-cost 2026-04](https://burning-cost.github.io/2026/04/04/anytime-valid-conformal-monitoring-coverage-sequential-testing/)：标准覆盖率监测不是监测系统而是"制造工作"的机制）。**这是 Layer 4 与 §3.3 第 1 条 mSPRT 完全同构的问题**——mSPRT 解决 Champion-Challenger 月度偷看的 FPR 膨胀（25%），Layer 4 覆盖率监测月度偷看同样膨胀（72%），却用固定样本思维处理序贯监测。**解法——betting martingale（下注鞅）**：每步到达一个覆盖指示 `Z_t = 1[Y_t ∈ Ĉ(X_t)] ∈ {0,1}`，原假设 `H₀: E[Z_t] ≥ 1-α`（正确校准下 i.i.d. Bernoulli(1-α)），构造下注鞅 `M_t = ∏_{s=1}^{t}(1 + λ_s·(Z_s - (1-α)))`，其中 `λ_s ∈ [0, 1/(1-α))` 为看到 `Z_s` 前选定的下注大小——`M_t` 在 H₀ 下是非负鞅，由 Ville 不等式 `P(sup_t M_t ≥ 1/α) ≤ α` 保证"无论何时停、查看多少次，超过 1/α 的概率 ≤ α"。**与 mSPRT 的关系**：mSPRT 用 Gaussian mixture 似然比构造 e-process（Champion-Challenger 收益差序贯检验），覆盖率监测用 betting martingale 构造 e-process（Bernoulli 覆盖指示序贯检验）——**两者同属 e-value/anytime-valid 框架，是同一数学根基在两类问题上的应用**。**与 calibration flush/BC-ACI 的正交关系**：calibration flush 解决"regime shift 后陈旧校准集导致覆盖失效"（宽度重建），BC-ACI 解决"持续偏置导致中心偏离"（中心纠正），**betting martingale 解决"覆盖率监测过程本身的统计有效性"**（监测层）——三者正交：flush/BC-ACI 是校准集维护层，betting martingale 是监测告警层。缺 betting martingale 则覆盖率监测用固定样本 p-value 月度偷看，72% 概率产生假告警触发不必要的重校准。**本项目定位**：Layer 4 施工时须配套 betting martingale 覆盖率监测（与 mSPRT 同属 e-value 框架，复用同一数学基础设施）——Phase 3 候选（与 Layer 4 CP 主路径同期落地）。**不过度工程审查**：betting martingale = 下注大小 λ_s 选择（可用简化恒定 λ 或 ONS 在线学习）+ 鞅累乘 + Ville 边界判定，<30 行增量代码，与 mSPRT 的 `M *= lr` 累乘同构——符合 MVP 分批原则

   **Betting Martingale 覆盖率监测施工伪代码**（2026-08-10 补充，施工算法缺失填补——Layer 4 覆盖率监测的理论描述完整但无可执行形态，与 mSPRT 施工伪代码同构需配套）：

   ```python
   # Anytime-valid conformal coverage monitoring using betting martingale
   # H0: E[Z_t] >= 1-alpha (正确校准)  H1: E[Z_t] < 1-alpha (覆盖失效=漂移)
   # 与 mSPRT 同属 e-value 框架：mSPRT 用 Gaussian mixture LR，本类用 betting martingale
   class BettingMartingaleCoverageMonitor:
       def __init__(self, alpha=0.10):
           self.alpha = alpha                    # 名义覆盖水平 1-alpha
           self.target_coverage = 1 - self.alpha # 期望覆盖率（如 0.90）
           # 下注大小 lambda: 0 < lambda < 1/(1-alpha)，保守取中值
           # lambda 过大→方差高，lambda 过小→检测慢；0.5/(1-alpha) 是 risk-neutral 折中
           self.lambda_s = 0.5 / (1 - self.alpha)
           self.M = 1.0                         # 初始 martingale 资金（e-process 累乘，E_{H0}[M]<=1）
           self.n = 0                           # 已观测预测笔数
           self.coverage_history = []           # 覆盖指示序列 Z_t = 1[Y_t in C_t]

       def update(self, coverage_indicator):
           """每笔预测后更新（anytime-valid，可任意频次查看无偷看惩罚）

           coverage_indicator: 1 if Y_t in C_t (实际值在预测区间内), else 0
           """
           self.n += 1
           self.coverage_history.append(coverage_indicator)
           # 更新 betting martingale: M_t = M_{t-1} * (1 + lambda*(Z_t - (1-alpha)))
           # Z_t - (1-alpha): 正=覆盖好于名义(赢注)，负=覆盖差于名义(输注)
           self.M *= (1 + self.lambda_s * (coverage_indicator - self.target_coverage))

           # 边界判定（Ville 不等式 anytime-valid，与 mSPRT 的 1/alpha 边界同构）
           if self.M >= 1 / self.alpha:
               return "COVERAGE_BREACH"         # M >= 1/alpha → 拒绝 H0，覆盖保证被破坏=漂移
           # 持续覆盖良好（M 远低于 1）→ 模型校准正常
           if self.n >= self.max_sample_size and self.M < 0.1:
               return "WELL_CALIBRATED"          # 证据充分且覆盖良好，可降频监测
           return "CONTINUE_MONITORING"          # 继续监测
   ```
   **施工要点**：① alpha=0.10 对齐 Layer 4 Conformal Prediction 名义覆盖水平（90% 区间）；② lambda_s=0.5/(1-alpha) 是 risk-neutral 折中（区间 (0, 1/(1-alpha)) 的中点偏保守），ONS 在线学习可替代恒定 lambda 但个人项目用恒定足够；③ 边界 1/alpha=10（Ville 不等式，与 mSPRT 的 1/alpha=20 同构但 alpha 不同——覆盖率监测 alpha=0.10 vs Champion-Challenger alpha=0.05）；④ coverage_indicator 从 Layer 4 Conformal Prediction 的 `Y_t ∈ Ĉ(X_t)` 判定获取（延迟 ground truth 到达后才能计算）；⑤ 与 mSPRT 的 `M *= lr` 累乘同构，复用同一 test martingale 基础设施——两者是 e-value 框架在"收益差序贯检验"和"覆盖率序贯监测"两类问题上的应用
   - **Conditional CTM——betting martingale test-time contamination 的污染修复（arXiv:2602.13848v2, 2026-06-12, Shaer et al., ICML 2026，施工算法缺失填补）**：上述 BettingMartingaleCoverageMonitor 的覆盖指示 `Z_t = 1[Y_t ∈ Ĉ(X_t)]` 依赖预测区间 `Ĉ(X_t)`，而 Layer 4 的 ACI/BC-ACI/calibration flush **用历史 `Z_s` 自适应更新 `Ĉ`**——测试统计量 `M_t` 与被测对象 `Ĉ` 形成**反馈环**：ACI 在 miss 后加宽区间→下一个 `Z_t` 更可能为 1→鞅误判"覆盖良好"即使真实条件覆盖已失效。这是**test-time contamination**（测试过程污染被测量）——用"自适应区间产生的覆盖指示"去检验"自适应区间的覆盖保证"是循环论证，anytime-valid 的 Type I 控制在 contamination 下可能退化。[Conditional Test Martingale (CTM)](https://arxiv.org/abs/2602.13848) 修复此污染——**固定参考集**（frozen calibration set，非自适应校准集）计算非一致性分数构造 test martingale，**鲁棒 betting function** 显式建模有限参考集的估计误差。**三项保证**：① anytime Type I 控制（任意时刻停 ≤ α）；② power-one 性质（H1 下几乎必然拒绝）；③ 有界检测延迟（regime shift 后有限步内检出）。**与现有 betting martingale 的关系**：BettingMartingaleCoverageMonitor 是"朴素版"（用自适应 `Z_t`，受 contamination），CTM 是"去污染版"（用固定参考集 `Z_t`，统计有效）——后者是前者的**有效性升级**，不改检测目标（都是覆盖率监测）只改分数来源（自适应→固定参考集）。**与 mSPRT 的对比**：mSPRT 的 e-process 用 Champion-Challenger 收益差（两路独立 PnL，无 contamination），betting martingale 的 e-process 用自适应区间的覆盖指示（单路自反馈，有 contamination）——CTM 让两者都达到 contamination-free 的 anytime-valid。**本项目定位**：Phase 3 候选——与 Layer 4 CP + betting martingale 同期落地时，betting martingale 的分数来源须用 CTM 的固定参考集而非自适应校准集（否则 anytime-valid 保证在 contamination 下退化）。**不过度工程审查**：CTM 是 betting martingale 的分数来源替换（自适应 `Z_t`→固定参考集 `Z_t` + 鲁棒 betting function），~30-40 行增量，复用现有 test martingale 累乘基础设施——符合 MVP 分批原则，是 betting martingale 统计有效性的必要补强非可选优化
   - **Legendre Jumper Martingales——betting martingale 的一阶矩→高阶矩漂移检测升级（arXiv:2606.20859v2, 2026-07-12, Szabadváry，选项之外更好的答案算法）**：上述 BettingMartingaleCoverageMonitor 检测**一阶矩漂移**（`E[Z_t]` 偏离 `1-α`，即覆盖率漂移），但金融数据还有**高阶矩漂移**——方差漂移（波动率 regime 切换，A 股最常见）、偏度漂移（尾部风险结构变化）、峰度漂移（重尾程度变化），一阶矩不变的方差漂移会让 betting martingale 完全失明（覆盖率没变但分布形状已变）。[Legendre Jumper Martingales](https://arxiv.org/abs/2606.20859) 用**移位 Legendre 多项式**作 betting function 将 Simple Jumper 扩展到高阶矩——多项式阶数 k 对应检测第 k 阶矩漂移（k=1 均值/覆盖率，k=2 方差/波动率，k=3 偏度），**Variational Legendre Jumper** 实现常数时间更新（每步 O(1) 非重新计算全历史）。**与 betting martingale 的关系**：betting martingale（k=1）检测覆盖率漂移，Legendre Jumper（k≥2）检测方差/偏度漂移——两者**正交互补**：betting martingale 管"区间是否覆盖"，Legendre Jumper 管"分布形状是否漂移"。**对量化交易的特殊意义**：A 股方差漂移 = 波动率 regime 切换（牛→熊/低波→高波），是策略衰减的第二大根因（五骑士 ② Regime 28%）——Legendre Jumper 的 k=2 阶可检测"波动率 regime 切换但收益均值未变"的早期漂移，比 Layer 3 ADWIN（须等标签）和 Layer 1 MMD（特征分布）更直接地定位到"波动率结构变化"。**与 10 号 regime 检测器的关系**：10 号 HMM regime 检测是状态分类（离散态），Legendre Jumper k=2 是连续方差漂移检测（连续量）——前者管"当前在哪个 regime"，后者管"方差是否在 regime 内部漂移"，两者互补。**本项目定位**：Phase 3 候选——与 betting martingale 同期落地时配套 k=2 阶 Legendre Jumper 检测方差漂移（波动率 regime 早期预警），k=1 阶复用现有 betting martingale。**不过度工程审查**：Legendre Jumper 是 betting martingale 的阶数扩展（增加 k≥2 多项式 betting function），~40-50 行增量，Variational 版本 O(1) 更新无计算负担——符合 MVP 分批原则，方差漂移检测是 A 股波动率 regime 切换的刚需
   - **Subgroup Under-Coverage Auditing——Layer 4 边际覆盖→条件覆盖的静默失效诊断（arXiv:2608.04254, 2026-08-06，选项之外更好的答案算法，施工算法缺失填补）**：上述 Layer 4 Conformal Prediction 保证**边际覆盖** `P(Y∈Ĉ)≥1-α`（全样本平均），但**特定子组**（如高波动率 regime / 特定行业 / 小盘股池）可能**静默欠覆盖**——边际覆盖 90% 持平但高波动率子组实际覆盖仅 70%，Layer 4 的 BC-ACI 纠正全局偏置无法发现子组级欠覆盖（全局平均掩盖局部失效）。这是"边际覆盖是条件覆盖的 casualty"（conformal.marketmaker.cc 180 实验已证：GARCH 三分位条件覆盖 0.952/0.915/0.820，高波动区低估 8 个百分点）。[Subgroup Under-Coverage Auditing](https://arxiv.org/abs/2608.04254)（2026-08-06）提供**有限样本保证的子组欠覆盖审计**——在预定义子组（如 regime 态/行业/市值分位）上检测实际覆盖是否显著低于名义水平，控制审计本身的 FWER。**与 RLCP 的关系**：RLCP（arXiv:2608.06206，Phase 4 候选）是**修复**条件覆盖（局部化校准），Subgroup Auditing 是**诊断**条件覆盖失效（告诉你何时/何处需要 RLCP）——两者是"诊断→修复"链路：Subgroup Auditing 在 Phase 3 先部署检测哪些子组欠覆盖，RLCP 在 Phase 4 针对欠覆盖子组做局部化校准。**与 ARM 变点归因的关系**：ARM 归因"哪些维度变了"（漂移归因），Subgroup Auditing 审计"哪些子组覆盖失效"（覆盖归因）——两者正交：ARM 管漂移检测归因，Subgroup Auditing 管覆盖保证归因。**本项目定位**：Phase 3 诊断候选——Layer 4 CP 主路径稳定后，部署 Subgroup Auditing 按 regime 态（10 号 12 态）/行业（22 号板块）/市值分位审计条件覆盖，识别需 RLCP 局部化校准的子组。**不过度工程审查**：Subgroup Auditing 是 Layer 4 CP 的诊断层（按子组计算覆盖+FWER 校正），~100-150 行增量，是 RLCP 局部化校准的前置诊断非独立组件——符合 MVP 分批原则，填补"边际覆盖掩盖子组失效"的静默盲区
   - **SCORE e-value FDR 增强——序贯多 Champion 检验的功率提升（ICML 2026，Kuang/Gang/Xia，选项之外更好的答案算法）**：上述 mSPRT 第 1 条的 e-process `M_n = ∏E_i` 达到边界 1/α 时拒绝 H₀ 晋升 Challenger，但**"超调"（overshoot，M_n 远超 1/α 的部分）被丢弃**——e-value 超过拒绝阈值后的多余证据 traditionally 浪费。[SCORE 框架](https://openreview.net/forum?id=qX4Nm7eNM5)（Sequential Control with Overshoot Refund for E-values）利用不等式 `I(y≥1) ≤ y − (y−1)₊`（对所有 y≥0 成立）回收这部分"浪费"的证据，产生 SCORE-LOND/SCORE-LORD/SCORE-SAFFRON 严格优于原始对应方法且保持有限样本 FDR 控制的方法。**对量化交易的意义**：当多个 Challenger 在时间流上**序贯**进入测试（如策略候选池持续产出新 Challenger，第 1 个晋升后再测第 2 个），这是**在线多重检验（online multiple testing）**场景——每次 mSPRT 检验消耗 α-wealth，SCORE 的 overshoot refund 让"强证据拒绝"（M_n 远超 1/α）比"刚好过线拒绝"（M_n ≈ 1/α）回收更多 α-wealth 给后续检验，提升整体功率（更多真 Challenger 被发现）。**与 §3.3 多策略选择演进路径（ASHA+SERPANT）的关系**：ASHA/SERPANT 解决"N 选 K 排序"（空间维度多策略并行），SCORE 解决"序贯检验功率"（时间维度多 Challenger 串行）——两者正交：策略数 >8 并行用 ASHA+SERPANT，策略候选池持续产出串行用 SCORE 增强 mSPRT。**配套研究**（[arXiv:2603.24792v3, Xu/Fischer/Ramdas CMU 2026-07](https://arxiv.org/html/2603.24792v3)）：online e-closure 原则 + compound e-values via donations，O(log t) 每步决策，严格优于 e-value 和 p-value 过程；[arXiv:2607.14380 Sun&Wang 2026-07](https://arxiv.org/pdf/2607.14380.pdf) 给出 e-value FDR 过程的 admissibility 完整类分析。**本项目定位**：Phase 2+ 候选——当前 3-5 策略 pairwise mSPRT 足够（单次检验无 overshoot 回收需求）；策略候选池成熟、Challenger 序贯产出频率高时评估 SCORE 增强 mSPRT（α-wealth 回收提升发现率）。**不过度工程审查**：SCORE 是 mSPRT 的 wrapper（包在现有 e-process 之外做 overshoot refund），不改 mSPRT 核心，<20 行增量——符合 MVP 分批原则，记为 Phase 2+ 候选不立即施工
   - **联合 VaR+ES 共形——Layer 4→36号 VaR 链路的正确形式（MDPI Mathematics 2026-08-06，Ye et al.，选项之外更好的答案算法）**：上述 Layer 4→36号 VaR 链路用 RWC（regime-weighted conformal）校准单一 VaR 分位数，但 **ES（Expected Shortfall）单独不可 elicitable**——无法像分位数（VaR）那样通过 pinball score 直接校准，而**pair (VaR_τ, ES_τ) 联合可 elicitable**（Fissler-Ziegel loss）。[联合 VaR+ES 共形](https://www.mdpi.com/2227-7390/14/15/2847)（2026-08-06 发表）用 conformal risk control 在有界单调损失上校准单一膨胀参数，该损失**耦合 VaR 突破频率与突破幅度（按模型预测的 VaR-ES gap 归一化）**—— guarantee 是对 tail-gap-normalized exceedance-severity surrogate。**关键理论贡献**：① 可交换性下有限样本期望风险控制；② 非可交换金融时序用 non-exchangeable swap-distance bound + regime-drift bound（显式累积 β-mixing cost）+ heavy-tail rate `D^(p-1)/p`；③ 因果地从上月 FRED-MD vintages 构建 regimes，在 8 汇率+Bitcoin+GIFT-Eval 金融域验证。**与现有 RWC（arXiv:2602.03903）的关系**：RWC 校准单一 VaR 分位数（VaR 可 elicitable），联合 VaR+ES 共形校准 (VaR, ES) pair（ES 须联合 VaR 才可 elicitable）——后者是更完整的尾部风险量化（ES 是 Basel 99%/97.5% 要求的尾部期望损失，VaR 只是分位数）。**与 36 号 var_calculator 的关系**：36 号 VaR/ES 监控须同时输出 VaR + ES（Basel 要求），联合共形提供两者的**联合**有限样本保证而非分别校准——消除"VaR 校准好但 ES 校准差"的盲区。**本项目定位**：Phase 3 候选——Layer 4 CP 主路径（calibration flush）稳定后，将 36 号 VaR 校准从 RWC（单一 VaR）升级到联合 VaR+ES 共形（pair），对接 Basel 99%/97.5% 双级别。**不过度工程审查**：联合 VaR+ES 共形是 RWC 的扩展（增加 ES 维度 + Fissler-Ziegel 联合损失），实现成本 = RWC + ES 校准项，复用 36 号现有 VaR/ES 计算设施——符合 MVP 分批原则
   - **Shadow Before Swap (SBS)——维护态 Champion vs 重训练 checkpoint 的关键区分（arXiv:2607.28577, 2026-07-30，Dutta Emory，施工算法缺失补充）**：上述 Champion-Challenger 第 1-2 条隐含假设"Champion 是静态 checkpoint"，但生产 Champion 是**维护态系统**（maintained incumbent）——在两次重训练之间持续更新归一化统计、消费成熟标签、适配预测头。[SBS](https://arxiv.org/html/2607.28577v1)（Shadow Before Swap，加密市场 48 UTC 周 8 标的 2 合约 3 seed 回放）的关键洞察：**重训练的候选不一定胜过持续维护的 Champion**——"a retrained candidate does not necessarily outperform a continuously maintained incumbent that has continued to learn"。**SBS 策略**：warm-refit Challenger 在服务路径外→在同一周延迟标签上与维护态 Champion 配对评估→仅在固定 paired NLL 优势后晋升。**实证**：SBS 在 528 个 Challenger 中仅晋升 114 个（减少 78.4% 模型状态切换），同时改善服务轨迹（NLL 相对日历替换 -0.1472%、相对计划匹配自动晋升 -0.0755%、相对持续维护 -0.0428%）。**与 §3.3 第 1 条 mSPRT + blast-radius 的关系**：SBS 验证了 mSPRT（序贯检验）+ 95/5 blast-radius（风险隔离）的核心设计，但补充了关键区分——**Champion 不是冻结的旧版本，而是持续学习的维护态系统**，Challenger 须证明胜过"维护态 Champion"而非"初始 checkpoint"。**对 53 号模拟→实盘路径的意义**：53 号灰度晋升门禁应明确"对比基线是维护态 Champion（持续更新）而非部署时 checkpoint"，避免"Challenger 胜过旧 checkpoint 但输给维护态 Champion"的假晋升。**本项目定位**：Phase 1 纪律补强（无新代码，仅明确 Champion 维护态语义 + 配对评估在延迟标签上）——53 号灰度门禁的 Champion 基线须是"当前维护态"非"部署时快照"。**不过度工程审查**：SBS 是 mSPRT 的语义补强（Champion 定义从 checkpoint 扩展到 maintained state），不引入新机制，零代码增量——符合 MVP 分批原则
   - **Drift2Act 预算干预框架——漂移检测→动作的正式决策层（arXiv:2603.08578v1, 2026-03-09，选项之外更好的答案算法，施工算法缺失填补）**：上述四层 Drift Observatory 联动编排（§3.3 第 4 条）的"分级响应阶梯"（alert→reduce_size→stop_entries→quarantine→retrain）是**启发式阈值映射**——composite score 0.20/0.40/0.60/0.80 对应五级响应，但阈值本身依赖经验标定，无数学保证。**Drift2Act（Drift-to-Action Controllers）**将漂移监控重构为"带安全约束的决策制定"——sensing layer 检测漂移 + active risk certificate 在**预算约束**下触发干预（如重训练/降仓），提供**在线风险证书保证**（online risk certificates）。**核心创新**：从"检测漂移"升级为"在漂移下安全决策"，将监控与动作耦合——不再问"是否漂移"而是问"在当前漂移程度下，什么干预动作的安全成本最低"。**与分级响应阶梯的关系**：分级响应是"检测→动作"的启发式映射（composite score→response level），Drift2Act 是"检测→动作"的**形式化决策框架**（risk certificate→budgeted intervention）——前者是 Drift2Act 的简化特例。**对量化交易的特殊意义**：T+1 市场重训练预算有限（盘后才能重训练+训练数据有限+过拟合风险），Drift2Act 的 budgeted intervention 直接对应"何时重训练/何时降仓/何时隔离"的资源分配决策——不是"检测到漂移就重训练"，而是"在预算约束下选择安全成本最低的干预"。**本项目定位**：Phase 3 候选——Phase 1 用分级响应阶梯（启发式阈值）过渡，Phase 3 漂移检测主路径稳定后评估升级到 Drift2Act 的 risk certificate 框架（将 composite score 阈值替换为可证风险证书）。**不过度工程审查**：Drift2Act 需 sensing layer + risk certificate + 决策器（~1000-1500 行），对个人项目 Phase 1 偏重，记为 Phase 3 候选不立即施工
   - **KDD 2026 漂移检测基准框架——14 检测器标准化评测（arXiv:2606.07789, KDD 2026 2026-08-09~13 韩国济州岛，选项之外更好的答案算法）**：上述 Drift Observatory 涉及 10+ 漂移检测器（PSI/KS/MMD/Wasserstein/CUSUM/ADWIN/Page-Hinkley/CvM/conformal coverage/betting martingale），但**缺乏跨数据集可比的标准化评测框架**——每个检测器的阈值/参数/适用场景依赖经验标定，无统一基准。[KDD 2026 漂移检测基准框架](https://arxiv.org/abs/2606.07789)首次提供**基于 Monte Carlo 试验的 drift simulation framework**——向真实数据集注入可控分布变化（abrupt/gradual × 4 种漂移类型），提出 **timing-aware 评估指标**（F1 detection score + normalized detection time），用 **leave-one-dataset-out 超参数优化协议**基准化 14 种主流检测器（CUSUM/Page-Hinkley/DDM/EDDM/ADWIN 等）在 7 个真实数据集上的表现。**核心创新**：解决两大痛点——① I1（方法论不一致：各论文用不同数据集/指标/参数，结果不可比）；② I2（真实数据无 ground truth：不知漂移何时发生）。**与本项目的关系**：本项目的 10+ 漂移检测器目前各自独立标定阈值，缺乏统一评测——KDD 2026 基准框架可直接用于 A 股因子衰减检测的**基准化评估**（注入可控漂移到 A 股收益序列，对比各检测器的 F1/detection time）。**与 ProteuS（arXiv:2509.11844，已登记 Phase 3 验证候选）的关系**：ProteuS 是"仿真器"（生成已知断点数据），KDD 2026 基准是"评测协议"（标准化指标+leave-one-out 超参优化）——两者互补：ProteuS 生成数据，KDD 2026 基准评测检测器。**本项目定位**：Phase 3 验证候选——漂移检测主路径稳定后，用 KDD 2026 基准框架 + ProteuS 仿真器对所有检测器做统一评测，淘汰 F1/detection time 劣势显著的检测器。**不过度工程审查**：KDD 2026 基准是评测工具非生产组件，~1500 行（drift injection + 14 检测器 wrapper + 评估协议），记为 Phase 3 验证候选不立即施工
   - **Conformal Abstention Layer——漂移响应"空仓"决策的形式化（arXiv:2606.11949v3, 2026-08-04，选项之外更好的答案算法）**：上述分级响应阶梯的"stop new entries"（停止新建仓）和"quarantine"（隔离）是启发式响应，但**何时从"减仓"升级到"空仓"缺乏形式化判据**。[Online Shift Detection + Conformal Abstention](https://arxiv.org/abs/2606.11949v3)（2026-08-04 发表，800 单元析因基准）提出 **Conformal Abstention Layer**——当模型对当前输入的预测置信度低于 conformal 保证的阈值时，模型**主动弃权**（abstain，不做预测），对应量化交易的"空仓"决策（不交易是最安全的默认动作）。**双模式**：① unweighted（标准 conformal abstain）；② weighted-on-alarm（漂移告警时加权 abstain，提高弃权灵敏度）。**800 单元析因基准发现**：检测难度由 classifier×shift 交互主导（η²=0.185，非单一因素），且 generative embeddings 下 weighted conformal prediction 存在 **silent failure**（density-ratio estimation 崩溃，须投影到 ≤32 维恢复 coverage）。**与分级响应阶梯的关系**：分级响应是"composite score→response level"的启发式映射，Conformal Abstention 是"conformal coverage→abstain decision"的**数学保证映射**——后者是前者的形式化升级（从"分数阈值"到"覆盖保证"）。**与 Layer 4 Conformal Prediction 的关系**：Layer 4 已用 conformal coverage 检测漂移，Conformal Abstention Layer 进一步用 conformal coverage 决定"是否交易"——同一数学基础（conformal prediction）从"检测层"扩展到"决策层"。**本项目定位**：Phase 3 候选——Layer 4 CP 主路径稳定后，将"stop new entries"升级为 Conformal Abstention Layer（覆盖保证的空仓决策），"quarantine"升级为 weighted-on-alarm abstention（漂移告警时加权弃权）。**不过度工程审查**：Conformal Abstention Layer 是 Layer 4 CP 的决策层扩展（复用 conformal 基础设施），~200-400 行增量，但 800 单元析因基准的 silent failure 发现提示 generative embeddings 须投影到 ≤32 维——记为 Phase 3 候选（与 Layer 4 CP 同期评估）
   - **Ranking by Lifts——Champion-Challenger 的成本收益 FDR 控制（arXiv:2407.01036v2, Basu & Berman Wharton/ISB，选项之外更好的答案算法）**：上述 mSPRT Champion-Challenger 第 1 条的 e-process 达到 1/α 阈值即晋升 Challenger，但**晋升决策只考虑统计显著性（e-value≥20）不考虑财务成本**——"错误晋升"（false promotion，Challenger 实际不优于 Champion 但被晋升）的财务成本被忽略。[Ranking by Lifts (RBL)](https://arxiv.org/abs/2407.01036v2)提出**成本收益 FDR 控制框架**——基于 local false discovery rate (lfdr) 的贪心 knapsack oracle 规则，按"期望 lift / 错误切换成本"比率排序，在大规模 champion-challenger 实验中**最大化利润同时控制 FDR**。**核心创新**：将 A/B 测试从"统计显著性问题"重构为"成本收益优化问题"——不仅控制 false discovery rate（多少比例的晋升是错误的），还控制 false discovery 的**财务成本**（错误晋升消耗多少资金）。**与 mSPRT 的关系**：mSPRT 控制 Type I 错误率（P(false promotion) ≤ α），RBL 控制 FDR + 财务成本（E[false promotion cost] ≤ budget）——后者是前者的成本感知升级。**与 SCORE 的关系**：SCORE 是 mSPRT 的功率增强（overshoot refund），RBL 是 mSPRT 的成本感知增强（lfdr knapsack）——两者正交可组合：SCORE 提升"发现真 Challenger 的概率"，RBL 控制"错误晋升的财务成本"。**本项目定位**：Phase 2+ 候选——当前 3-5 策略 pairwise mSPRT 的错误晋升成本可控（blast-radius 5% 限制），策略数扩张后（>8）错误晋升的累积成本显著时评估 RBL（将 mSPRT 的 1/α 阈值替换为 lfdr knapsack 排序）。**不过度工程审查**：RBL 需 lfdr 估计 + knapsack 优化（~400-600 行），3-5 策略规模下错误晋升成本可控（5% blast-radius 已限制），记为 Phase 2+ 候选不立即施工
   - **evalinger futility monitoring——策略退役的提前放弃框架（arXiv:2602.06379v1, 2026-02-06，选项之外更好的答案算法，施工算法缺失填补）**：上述 §3.9 退役流程的"触发式移除纪律"（机械执行消除沉没成本/损失厌恶/过度自信）是**事后退役**——须等 Decay Detection 持续告警 ≥10 日才触发。但**事前 futility monitoring**（无效性监测）能在策略"尚有微弱 edge 但统计上已无希望恢复"时提前放弃，避免继续浪费研究资源/资金。[evalinger R 包](https://arxiv.org/abs/2602.06379v1)（2026-02-06，对齐 FDA 2026-01 Bayesian 指南草案）提供**自适应临床试验的 E-value 实践指南**——betting-martingale 构造的 e-process 支持**复合 null 假设** + **futility monitoring**（无效性监测）+ platform-trial multiplicity。**关键发现**：在连续监控下 e-value 的 power **反超** group sequential 方法（传统临床试验的固定时点检查）。**与 §3.9 退役流程的关系**：退役流程是"事后退役"（Decay Detection 告警 ≥10 日 → 触发），futility monitoring 是"事前放弃"（e-value 持续低于 futility 阈值 → 提前放弃）——前者是"已衰减到不可接受"，后者是"统计上已无希望恢复"。**与 mSPRT 的关系**：mSPRT 用 e-process 做 Champion-Challenger 晋升检验（H1: Challenger > Champion），futility monitoring 用同一 e-process 做反向检验（H0: 策略 edge ≤ 0 的证据是否足够强到提前放弃）——**同一 e-value 框架在晋升和退役两个方向的应用**。**本项目定位**：Phase 2 候选——将 §3.9 退役流程的"触发式移除"（事后）升级为"触发式移除 + futility monitoring"（事前+事后），在策略尚有微弱 edge 但 e-value 持续低于 futility 阈值时提前启动退役评估，避免继续浪费资源。**不过度工程审查**：futility monitoring 复用 mSPRT 的 e-process 基础设施（同一 test martingale，反向阈值判定），<50 行增量代码——符合 MVP 分批原则
   - **ARM 检测器无关变点归因——漂移检测"哪些维度变了"的有限样本证书（arXiv:2608.01691, 2026-08-03，北京工业大学+南洋理工，选项之外更好的答案算法）**：上述 SHAP Drift Attribution 用 SHAP 值归因漂移到特征，但 SHAP 在高维重尾金融数据上不稳定且无 FWER 控制。[ARM（Attribution by Rank Maxima）](https://arxiv.org/abs/2608.01691)是**检测器无关的变点归因 wrapper**——接受任意检测器（CUSUM/ADWIN/MMD/PSI）定位的变点，返回"已认证变化"的坐标集合，每个带 location/scale 类型标签。**核心算法**：用 max-over-splits rank 统计量，使证书对变点估计方式与精度**不变**，rank-based 对 A 股重尾分布天然鲁棒。**三项有限样本保证**：① per-coordinate validity（任意检测器下成立）；② 精确 FWER 控制（Westfall-Young 联合置换，distribution-free Holm 兜底）——传统两样本检验在高维下 FWER 膨胀到 0.66+ 完全失效；③ 高维 FDR 控制（Benjamini-Yekutieli 与 e-BH）。**金融实证**：2008 危机前后 5 条金融序列，ARM 把 scale change 归因到每个资产类别并正确排除控制坐标。**与 SHAP Drift Attribution 的关系**：SHAP 归因到"哪个特征"（特征级），ARM 归因到"哪个坐标/资产"（资产级）——两者正交：SHAP 管单策略特征漂移归因，ARM 管多策略/多资产面板"哪个先变"。**与下游影响门控的关系**：下游影响门控过滤"统计显著但业务不显著"，ARM 进一步回答"哪些维度真正变了"——三者在"是否漂移→哪些维度漂移→业务影响多大"链路分工。**本项目定位**：Phase 3 诊断增强候选——多策略面板监控（如 3-5 策略 PnL 面板+多行业因子面板）中"哪个策略/行业先漂移"的归因工具，与 SHAP Drift Attribution 并列。**不过度工程审查**：ARM 是 wrapper（包在现有检测器之外做归因），~200-300 行增量，rank-based 无需分布假设——符合 MVP 分批原则
   - **DPitG 双停止准则——mSPRT "可停但不决"的决断性补充（arXiv:2608.05301, 2026-08-05，Kazin，选项之外更好的答案算法，施工算法缺失填补）**：上述 mSPRT 的 anytime-valid 保证"任意时刻停都保持 Type I 控制"，但**"可停"≠"能决"**——mSPRT 停止时可能仍处于"证据不足"的 CONTINUE 状态（M_n 既未达 1/α 也未达下界），导致 Champion-Challenger 实验陷入"持续观察无结论"的僵局。[DPitG（Decisive Precision is the Goal）](https://arxiv.org/abs/2608.05301)提出**双停止准则**——同时要求"精度目标（HDI 宽度 ω）"与"决定性裁决"两者都满足才停：① 精度目标：后验最高密度区间宽度 < ω（参数估计足够精确）；② 决定性裁决：HDI 与 ROPE（Region of Practical Equivalence）关系明确——完全在 ROPE 内接受 H0（保留 Champion）/ 完全在 ROPE 外接受 H1（晋升 Challenger）/ 与 ROPE 重叠则继续。**实证**：公平硬币仿真（ω=0.08, ROPE=0.5±0.05），DPitG 把 PitG 的 62% 不确定率降到 2%，仅多花 5% 样本，**零假阳性**；HDI+ROPE 只有以假阳性为代价才能达到相近决定性。**与 mSPRT 的关系**：mSPRT 管"任意时停的 Type I 有效性"（频率学派），DPitG 管"停了就要下结论"（贝叶斯 HDI+ROPE）——两者互补：mSPRT 保证安全性，DPitG 保证决断性。**与 §3.9 退役流程的关系**：退役流程的"触发式移除"须有明确结论（retire/reoptimize/pause），DPitG 的双停止准则可应用于退役决策的"何时必须有结论而非继续观察"。**本项目定位**：Phase 2+ 候选——当前 mSPRT 用 max_sample_size 兜底（样本耗尽强制 RETAIN_CHAMPION），DPitG 提供"精度+决断性"双准则替代粗暴的样本上限。**不过度工程审查**：DPitG 是 mSPRT 停止规则的升级（贝叶斯后验 HDI 计算 + ROPE 判定），<40 行增量代码，复用 mSPRT 的 e-process 累积——符合 MVP 分批原则
   - **Betting on Bets 随机优势序贯检验——Champion-Challenger 从"均值比较"升级到"分布比较"（arXiv:2604.21851v3, 2026-08-01，选项之外更好的答案算法）**：上述 mSPRT 的 H1 是"Challenger 均值收益 > Champion 均值收益"（均值比较），但**均值相同但左尾更厚的策略不优于均值相同但左尾更薄的策略**——量化交易关心整个收益分布而非仅均值（左尾厚度 = 爆仓风险）。[Betting on Bets](https://arxiv.org/abs/2604.21851v3)用 e-process 构造**一阶/高阶随机优势（Stochastic Dominance, SD）的序贯 anytime-valid 检验**——GRO（growth-rate optimal）betting 策略 + predictably mixed e-processes，给出渐近 power-one 保证。**核心创新**：区分"是否有 upside"（一阶 SD）与"均值是否占优"——对相似均值或序数结果特别有用（如 Challenger 均值略低但下行风险更小，一阶 SD 可能仍占优）。**与 mSPRT 的关系**：mSPRT 检验均值差（Δ = E[C] - E[Ch]），Betting on Bets 检验分布优势（P(C ≥ x) ≥ P(Ch ≥ x) ∀x）——后者是前者的分布级升级（均值占优是分布优势的必要非充分条件）。**与 §3.3 第 9 条晋升门禁的关系**：晋升门禁已用 Sortino + Calmar 三角验证下行风险，Betting on Bets 提供序贯版本的分布级检验——将"三角验证"从固定样本升级为 anytime-valid。**本项目定位**：Phase 3 候选——当 Challenger 均值略低于 Champion 但下行风险显著更小时，mSPRT 不会晋升但 Betting on Bets 的一阶 SD 检验可能支持晋升（更优的风险调整分布）。**不过度工程审查**：Betting on Bets 复用 mSPRT 的 e-process 框架（同一 test martingale，换似然比构造），<50 行增量——符合 MVP 分批原则
   - **RLCP 局部化保形预测——Layer 4 从边际覆盖到条件覆盖的有限样本升级（arXiv:2608.06206, 2026-08-06，选项之外更好的答案算法）**：上述 Layer 4 Conformal Prediction 的覆盖保证是**边际覆盖**（marginal coverage，长期时间平均 P(Y∈Ĉ)≥1-α），但**条件覆盖**（conditional coverage，给定 X 的 P(Y∈Ĉ|X)≥1-α）是更强保证——Layer 4 用 BC-ACI 纠正全局偏置，但 BC-ACI 是全局序列自适应非局部条件校准。[RLCP（Randomly Localized Conformal Prediction）](https://arxiv.org/abs/2608.06206)首次给出**对已实现局部邻域的有限样本联合保证**——条件覆盖 gap + 相对 oracle 的长度误差，分解为 O(h^β) 局部偏置与校准项。**对 conformalized quantile regression** 进一步分解为 score 估计误差。**与 BC-ACI 的关系**：BC-ACI 聚焦"全局序列自适应"（纠正持续偏置中心），RLCP 聚焦"局部条件校准"（测试点附近的条件覆盖）——两者互补：BC-ACI 管时间维度的全局偏置，RLCP 管特征维度的局部条件。**与 calibration flush 的关系**：calibration flush 解决"regime shift 后陈旧校准集"（突变重建），RLCP 解决"不同特征区域条件覆盖不一"（局部校准）——三者正交：flush 管突变、BC-ACI 管偏置、RLCP 管局部。**本项目定位**：Phase 4 鲁棒性候选——Layer 4 CP 主路径（calibration flush + BC-ACI）稳定后，当"不同 regime/不同特征区域的条件覆盖差异"成为瓶颈时评估 RLCP 升级。**不过度工程审查**：RLCP 需局部核权重计算 + 局部分位数估计，比全局 split conformal 重，记为 Phase 4 候选不立即施工
   - **Decaying-ε-FOCuS 多流最快变点检测——多策略/多资产轮巡监测（arXiv:2601.22561v5, 2026-08-01，Stony Brook/Georgia Tech，选项之外更好的答案算法）**：上述 Drift Observatory 各检测器（CUSUM/ADWIN/MMD/PSI）假设"每条流都被持续监控"，但**多策略/多资产面板场景下计算预算有限**——无法同时对所有策略/所有行业因子做高频漂移检测。[Decaying-ε-FOCuS](https://arxiv.org/abs/2601.22561v5)是**bandit 最快变点检测**——M 条独立流中一条均值未知漂移，每步只能采样一条，用 Decaying-ε-greedy 切换规则 + GLR 检测。**首次**在无离散化、无漂移幅度下界假设下给出近似一阶最优保证（sub-Gaussian 与有界支撑）。**与单流 CUSUM 的关系**：CUSUM 单流监测（每条流独立检测），Decaying-ε-FOCuS 多流轮巡（bandit 分配采样预算给"最可能漂移"的流）——后者在计算预算受限的多流场景更高效。**与 ARM 变点归因的关系**：ARM 归因"哪些维度变了"（事后），Decaying-ε-FOCuS 决定"先监测哪条流"（事前）——两者正交：FOCuS 管采样分配，ARM 管归因证书。**本项目定位**：Phase 3-4 候选——多策略（>5）或多行业因子（>10）面板场景下，用 bandit 策略轮巡监测而非全量并行检测，降低计算开销。**不过度工程审查**：Decaying-ε-FOCuS 需 bandit 采样策略 + GLR 检测器（~300-400 行），3-5 策略规模下全量并行 CUSUM 足够（计算开销可接受），记为 Phase 3-4 候选（策略数 >8 或因子数 >15 时评估）
   - **DTD 动态阈值确定——Drift Observatory 固定阈值→自适应阈值（arXiv:2511.09953v1, AAAI 2026，Lu et al. UTS，选项之外更好的答案算法，施工算法缺失填补）**：上述四层 Drift Observatory 联动编排的分级响应阶梯用**固定阈值**（composite score 0.20/0.40/0.60/0.80→alert/reduce/stop/quarantine/retrain），PSI 用固定 0.1/0.25 阈值，CUSUM 用固定 h=4σ 阈值——所有阈值一经标定即固定不变。**DTD（Dynamic Threshold Determination）**证明**动态阈值可证明优于任何单一固定阈值**——核心定理：将每个数据段的最佳阈值组合构造的动态策略，保证不劣于任何跨所有段的单一阈值。DTD 在现有检测器上增加**比较阶段（comparison phase）**——检测到漂移后不立即响应，先用不同阈值在比较窗口评估模型性能，选择性能最优的阈值作为后续段的检测阈值。**实证**：DTD 在图像和表格数据上显著增强 SOTA 检测器，复杂场景（渐变漂移/循环漂移）收益更大，且对比较阶段时长 K 鲁棒。**与分级响应阶梯的关系**：分级响应阶梯用固定 composite score 阈值映射响应级别，DTD 将阈值从"固定经验标定"升级为"动态性能驱动"——前者是 DTD 的退化特例（所有段用同一阈值）。**与 Drift2Act 的关系**：Drift2Act 解决"检测→动作"的形式化决策层（risk certificate），DTD 解决"检测阈值本身"的自适应标定——两者正交：DTD 管检测器灵敏度，Drift2Act 管响应决策。**本项目定位**：Phase 3 候选——Phase 1 用固定阈值（PSI 0.1/0.25、CUSUM 4σ、composite 0.20/0.40/0.60/0.80）过渡，Phase 3 漂移检测主路径稳定后评估 DTD 升级（将固定阈值替换为动态阈值）。**不过度工程审查**：DTD 是现有检测器的 wrapper（包在外围增加比较阶段），~200-300 行增量，对 K 鲁棒（无须精调 K）——符合 MVP 分批原则
   - **COP 共形乐观预测——Layer 4 CP 在可预测模式下产生更紧区间（arXiv:2512.07770v2, 2026-02-24，Nankai/Tsinghua，选项之外更好的答案算法）**：上述 Layer 4 Conformal Prediction 的 ACI/calibration flush/BC-ACI 都在**完全对抗环境**（fully adversarial，任意分布变化）下设计，产生**过度保守**的预测区间——当数据存在可预测模式（如 A 股季节性/周期性）时，对抗性方法无法利用这些模式收紧区间。**COP（Conformal Optimistic Prediction）**将底层**数据模式**纳入更新规则——通过估计非一致性分数的累积分布函数（CDF），当存在可预测模式时产生**更紧预测区间**，同时在估计不准时仍保持覆盖保证。**理论保证**：建立覆盖与遗憾的联合界，证明 COP 在任意学习率下实现 distribution-free 有限样本覆盖，且在 i.i.d. 分数下收敛。**与 ACI/BC-ACI 的关系**：ACI/BC-ACI 是"纯对抗"路径（不假设可预测模式），COP 是"分布知情"路径（利用可预测模式）——后者在前者基础上利用数据模式收紧区间，是更乐观（optimistic）的校准。**与 DASC 的关系**：DASC 用谱相似性加权校准残差（regime 循环场景），COP 用 CDF 估计利用可预测模式（周期性场景）——两者互补：DASC 管 regime 循环，COP 管可预测模式。**本项目定位**：Phase 3+ 候选——Layer 4 CP 主路径（calibration flush + BC-ACI）稳定后，当"对抗性方法产生过宽区间"成为瓶颈时评估 COP（利用 A 股季节性/周期性模式收紧区间）。**不过度工程审查**：COP 是 ACI 的 wrapper（增加 CDF 估计 + 乐观更新规则），~100-200 行增量，与 calibration flush/BC-ACI 叠加无冲突——符合 MVP 分批原则
   - **鲁棒序贯实验设计——mSPRT 在模型误设下的鲁棒性（arXiv:2605.12899v1, 2026-05-13，Wen/Wu/Shi et al. LSE，选项之外更好的答案算法）**：上述 mSPRT Champion-Challenger 第 1 条的高斯 mixture 闭式解假设收益差服从高斯分布，但 **A 股收益有重尾特性**（超额峰度 >20），高斯假设在重尾数据上可能失效——mSPRT 的似然比构造依赖分布假设，模型误设下 Type I 控制可能退化。**鲁棒序贯实验设计（Robust Sequential Experimental Design）**在**模型误设**下研究 A/B 测试的序贯设计——统一覆盖 contextual bandit 和动态设置，证明其设计**界定处理效应估计的最坏情况均方误差（worst-case MSE）**。**与 mSPRT 的关系**：mSPRT 假设高斯 mixture（参数化），鲁棒序贯设计在最小假设下工作（非参数化）——后者在前者分布假设失效时提供安全网。**与 CUSUM 重尾缓解（§3.3 第 4 条 Phase 1 措施）的关系**：CUSUM 重尾缓解用 winsorize 预处理使高斯假设近似成立，鲁棒序贯设计从检验框架层面消除分布假设——两者互补：winsorize 管预处理，鲁棒序贯设计管检验框架。**本项目定位**：Phase 3 候选——Phase 1 用 winsorize + mSPRT 高斯 mixture 过渡，Phase 3 当"winsorize 后仍重尾"或"mSPRT 误设退化"时评估鲁棒序贯设计替代 mSPRT。**不过度工程审查**：鲁棒序贯设计需 worst-case MSE 界计算 + 非参数序贯设计（~500-800 行），比 mSPRT 高斯闭式解重，记为 Phase 3 候选（winsorize+mSPRT 误设退化时评估）
5. **Decay Detection 5 监控点**（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/) + [LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/) 交叉验证）：策略衰减检测不能只看单一指标（"亏钱才退役"是零售思维），须五维度并行监控：
   - **Rolling Sharpe degradation**：滚动 Sharpe 持续下滑（30-50 笔交易早期预警，100+ 笔确认；[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Rolling Sharpe degradation）
   - **Drawdown frequency 增加**：回撤频次上升 = edge 在压缩（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Increasing drawdown frequency）
   - **Correlation instability**：与其他策略相关性不稳定 = alpha 来源在被套利（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Correlation instability）
   - **Execution cost drift**：实际滑点/冲击成本相对回测假设漂移 = 容量饱和（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Execution cost drift）
   - **Volatility mismatch**：策略波动率与历史不匹配 = regime 切换未适应（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Volatility mismatch）
   - **Half-life of alpha 数学模型**（[mathandmarkets 2026-02-22](https://mathandmarkets.com/p/half-lives-of-alpha-why-every-strategy)）：alpha 衰减服从指数衰减 `α(t) = α₀·e^(-λt)`，半衰期 `t½ = 0.693/λ`；考虑 transaction cost floor（如 1.5% 年化），可用半衰期 = `-ln(cost_floor/α₀) / λ`。**用途**：根据 λ 估计预测策略何时退至 cost floor 以下，提前规划替代策略研发（与 §3.1 ⑥ 退役阶段联动）。**实证**：[DeepTradeX 2026-07](https://deeptradex.zendesk.com/hc/en-us/articles/16820285969295-Strategy-Lifecycle-Management-Great-Trading-Strategies-Are-Managed-Not-Just-Built)：68% 系统化策略在 18-24 个月内需要重大修改或退役；[Maven Securities via breakingalpha 2025-12](https://breakingalpha.io/insights/alpha-decay-detection-purchased-trading-strategies)：alpha 衰减率美国市场年均 5.6%、欧洲市场年均 9.9%，且衰减率随时间递增（市场效率提升+AI 普及加速套利）。**农耕心态**（[positioned.app 2026-02](https://positioned.app/traders-glossary/alpha-decay)）：管理 alpha 衰减须从"金矿心态"（找到一个永赚策略）转向"农耕心态"（持续研发流水线补新策略，旧策略衰减时新策略已就绪）——不依赖单一"皇冠策略"，而是管理"信号组合"（portfolio of signals），部分衰减时部分新生
   - **选项之外更好的答案算法：双曲线衰减模型**（2026-08-10 算法审查补充，[arXiv:2512.11913](https://arxiv.org/html/2512.11913v1) Lee 2025-12 KAIST）：指数衰减 `α(t)=α₀·e^(-λt)` 是经验拟合的"默认选择"，但 [arXiv:2512.11913](https://arxiv.org/html/2512.11913v1) 从**博弈论 Nash 均衡**严格推导出因子 alpha 衰减的特定函数形式——**双曲线衰减**：

     ```
     α(t) = K / (1 + λt)

     其中：
       K = alpha capacity（初始 alpha 总量，固定"蛋糕"）
       λ = strategy discovery rate（策略发现速率，单位 1/时间）
       t = 自策略被发现/发表以来的时间

     推导：N 个 agent 发现同一信号 → Nash 均衡下每人赚 α_i = K/N
           随时间 t 有 λt 个新 agent 进入 → N(t) = 1 + λt
           → α(t) = K / (1 + λt)
     ```

     **核心实证**（8 个 Fama-French 因子 1963-2024）：① **机械因子符合双曲线衰减**——动量因子双曲线 R²=0.65，**优于指数衰减 R²=0.61 和线性衰减 R²=0.51**，验证博弈论地基；② **判断型因子不符合**——价值/质量因子不拟合双曲线模型（信号模糊性使套利者进入速度慢，不满足"策略发现速率恒定"假设，呼应 Hua & Sun "barriers to entry" 信号模糊性分类）；③ **2015 后拥挤加速**——OOS 测试模型**高估**剩余 alpha（预测 0.30 vs 实际 0.15），与因子 ETF 增长负相关 ρ=-0.63；④ **拥挤预测尾部风险而非均值**——拥挤的反转因子 crash 概率 1.7-1.8×，拥挤的动量因子 crash 概率 0.38×（p=0.006）。

     | 衰减模型 | 公式 | 动量因子 R² | 理论基础 | 适用因子 |
     |---|---|---|---|---|
     | **指数衰减**（当前） | `α₀·e^(-λt)` | 0.61 | 经验拟合（数学便利） | 通用（默认） |
     | **双曲线衰减** | `K/(1+λt)` | **0.65** | **博弈论 Nash 均衡** | **机械因子**（动量/反转） |
     | 线性衰减 | `α₀·(1-λt)` | 0.51 | 最简近似 | 短期粗估 |

     **与本项目对齐**：本项目首批 3 策略中，**打板**（[24 号](24_daban_strategy_detail.md)）和**事件驱动**（[26 号](26_event_driven_strategy_detail.md)）属机械因子（价量驱动、规则明确、易被套利），应优先采用双曲线衰减模型预测其 alpha 寿命；**多因子**（[25 号](25_multifactor_strategy_detail.md)）含价值/质量等判断型因子，指数衰减仍可适用。**裁定**：Phase 1 退役门禁仍用指数衰减（简单、通用、已在 §3.3 Decay Detection 实施）；**双曲线衰减记为 Phase 2 候选**——用于机械因子策略的退役时机精算（双曲线比指数衰减更准确地预测"alpha 何时退至 cost floor 以下"）。升级条件：首批策略 6+ 月 PnL 后，对比指数 vs 双曲线模型的预测残差，若双曲线显著优于指数（OOS 拟合 R² 差 >0.05）则升级。**与 [55 号](55_monitoring_review.md) 协同**（⚠️55 号为 draft v0.1.0 骨架待讨论，G26 监控告警 why 层未定稿）：Decay Detection 5 监控点的 half-life 估算可切换衰减模型（当前指数，Phase 2 双曲线），无需重写监控框架

   - **选项之外更好的答案算法：策略容量理论（break-even capacity + profit-maximising size）**（2026-08-10 算法审查补充，[hftradingbook 2026-06-04](https://hftradingbook.com/performance/capacity-and-alpha-decay) + Gatheral 2010 "No-dynamic-arbitrage and market impact"）：alpha 衰减不只有时间维度，还有**规模维度**——容量（capacity）是策略在市场冲击吃掉 alpha 前能承载的最大资金。基于平方根律 `impact = Y·σ·√(Q/V)`：

     ```
     net_edge(Q) = g - c·√Q           （每单位净 edge = 毛edge - 单位冲击成本）
       g = 毛edge per unit（固定）
       c = Y·σ/√V（冲击系数，Y 标定常数，σ 波动率，V 日成交量）

     break-even capacity:  Q* = (g/c)²    （net edge = 0 时的资金量）
     profit-maximising size:  Q_max = (2g/3c)² = 4/9 · Q*   （总净 PnL 最大化点）
     ```

     **核心洞察**：利润最大化的资金量仅为 break-even capacity 的 **4/9（44%）**——远在达到容量天花板之前就该停止加仓，因为每多投入一单位资金边际收益递减而冲击成本递增。**反直觉**：`total_net_PnL = g·Q - c·Q^(3/2)` 对 Q 求导 = 0 得 Q_max = 4/9·Q*，而非 Q*。

     **与本项目对齐**：① [31 号仓位算法](31_position_sizing.md) 的 Kelly 精裁决产出 f_i 后，FirmRiskAggregator 裁剪到单票 8% 上限——但 8% 上限是**风险约束**非**容量约束**。容量理论提示：打板策略（24 号）单票容量极小（几万~几十万），实际可部署资金可能远低于 8% 上限，应按 `Q_max = 4/9·Q*` 估算策略级容量天花板；② [55 号监控](55_monitoring_review.md)（⚠️draft v0.1.0 骨架待讨论，监控告警 why 层未定稿）Decay Detection 第 4 监控点"Execution cost drift"正是容量饱和的信号——实际滑点/冲击成本相对回测假设漂移 = 策略接近 break-even capacity。**裁定**：MVP 阶段不实施容量理论形式化（打板策略容量天然受限，8% 上限已足够保守）；**记为 Phase 2 候选**——多因子/事件驱动策略资金规模扩大后，用 `Q_max=4/9·Q*` 精算策略级容量上限，避免"资金超容量部署导致 net edge 归零"。升级条件：单策略 AUM > 50 万 或 实际冲击成本持续 > 回测假设 1.5× 时触发评估
   - **Edge Decay 五骑士分类法 + 实证数据**（[smartfinancedata 2026-08](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 127 策略追踪）：策略衰减有五种根因机制，按影响占比排序——

     | 衰减骑士 | 影响占比 | 机制 | 经典案例 |
     |---|---|---|---|
     | **① Crowding 拥挤** | 41% | 资本涌入→信号被套利→价差压缩 | Monday Effect 1980s 发表后 1990s 消失 |
     | **② Regime Change 状态切换** | 28% | 市场结构/波动率 regime 变化→策略设计前提失效 | Carry Trade 2008 危机后零利率崩溃 |
     | **③ Overfitting 过拟合** | 18% | 原本无 edge，回测拟合了噪声→OOS 必然失败 | 参数 >7 / Sharpe >2.5 / 规则任意 |
     | **④ Technology Evolution 技术演进** | 9% | 执行速度提升/价差压缩→依赖慢扩散的策略被套利 | Post-Earnings Drift 从周级压缩到小时级 |
     | **⑤ Regulatory Change 监管变更** | 4% | 规则变更（卖空/保证金/涨跌停）→策略变非法或不实用 | 2007 SEC 取消 uptick rule |

     **关键实证**（[smartfinancedata 2026-08](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 127 策略）：83% 策略在 18 个月内失效；中位失效时间 14.3 个月；性能半衰期 11.2 个月；67% 在 1 年内失效；仅 8% 存活 3 年。**用途**：退役诊断时按五骑士分类归因——不同根因对应不同应对（crowding→换策略/regime→等回归/overfitting→回孵化重做/technology→降级或退/regulatory→退），而非笼统"策略失效"
   - **IC by forward horizon 衰减剖面**（[alphanume 2026-06-03](https://www.alphanume.com/blog/what-is-signal-decay)）：在 1d / 5d / 21d / 63d 多个前瞻窗口计算 IC（信息系数），绘制 IC-horizon 曲线即为衰减剖面。**两种信号衰减尺度**（[alphanume 2026-06-03](https://www.alphanume.com/blog/what-is-signal-decay)）：① **intra-signal horizon decay**（单次观测内信号预测力随时间衰减，决定最优持仓周期与换手频率——IC 半衰期数天的信号需高换手实现，数周的信号可低频）；② **secular alpha decay**（策略级 alpha 长期侵蚀，随信号被发表/采用/拥挤而衰减——McLean-Pontiff 实证：发表后异常收益显著衰减）。**与 half-life 模型的关系**：half-life 描述 secular decay 的宏观趋势，IC-horizon 描述 intra-signal decay 的微观结构——两者互补，前者指导"何时退役"，后者指导"持仓多久/换手多频繁"。**mismatch 风险**：换手频率与实际 IC 衰减率不匹配是最常见且最昂贵的实施错误（[alphanume 2026-06-03](https://www.alphanume.com/blog/what-is-signal-decay)：Mismatching the rebalance frequency to the actual decay rate is one of the most common and costly implementation errors）
   - **Bootstrap IC 半衰期置信区间 + 最优再平衡频率推荐**（[quantskills/skill-factor-decay 2026-07-16](https://github.com/quantskills/skill-factor-decay)）：IC 衰减剖面不只画曲线，须**量化不确定性**——多期限 Rank IC 衰减曲线 → 指数/幂律/双指数三种模型拟合 → **Bootstrap 重采样计算半衰期置信区间**（避免单点估计的过度自信）→ 换手衰减 + Q5-Q1 分组收益衰减交叉验证 → 推荐最优再平衡频率。**流程**：① 计算 1d/5d/21d/63d Rank IC；② 三模型拟合选 AIC 最优；③ Bootstrap 1000 次重采样得半衰期 95% CI；④ 若半衰期 CI 下界 > 持仓周期则换手过频（成本浪费），若 CI 上界 < 持仓周期则换手不足（alpha 流失）。**与 half-life 模型的关系**：half-life 给点估计，Bootstrap CI 给区间估计——区间估计更诚实，避免"半衰期=11.2 月"的虚假精确
   - **Factor Specificity Index (FSI) 拥挤度量化指标**（[CSDN WorldQuant 2026-06-04](https://wenku.csdn.net/column/h4wn2p5dhgm)）：对因子收益做市场基准回归，滚动计算残差 R²，`FSI = 1 - mean(rolling_R²)`。**FSI < 0.4 表明因子已被市场充分消化**（拥挤度高）——某动量因子在 2020-03 流动性危机期间 FSI 从 0.68 骤降至 0.31，预示后续 11 个月失效期。**与五骑士 ① Crowding 的关系**：FSI 是 crowding 的量化指标——FSI 下降 = 资本涌入因子 = 拥挤加深，是 Crowding 衰减的先行信号。**实施**：滚动 60 日窗口 OLS 回归 + 残差 R² 计算，<30 行代码
   - **策略类型衰减速度经验表**（[smartfinancedata 2026-08](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 127 策略）：不同类型策略的衰减速度差异显著——简单直觉模式最易被发现和套利故衰减最快，复杂多因子存活最久但发现也更难：

     | 策略类型 | 中位存活 | 1 年失败率 | 主要衰减根因 |
     |---|---|---|---|
     | 简单技术形态 | 8.2 个月 | 79% | Crowding |
     | 动量策略 | 11.4 个月 | 71% | Crowding |
     | 均值回归 | 13.7 个月 | 64% | Regime Change |
     | 季节性/日历效应 | 15.9 个月 | 58% | Crowding |
     | 波动率套利 | 19.3 个月 | 52% | Technology |
     | 统计套利 | 24.1 个月 | 43% | Crowding |
     | 多因子模型 | 28.6 个月 | 35% | Regime Change |

     **规律**：简单模式衰减最快（易发现易套利），复杂多因子存活最久（需基础设施+研究深度）。**与本项目对齐**：本项目打板策略（24号）属"简单技术形态"类（涨停形态识别），预期中位存活 ~8-12 个月，须按此节奏规划迭代；多因子策略（25号）属"多因子模型"类，预期中位存活 ~24-28 个月
   - **AI 不是 alpha 衰减的解药**（[CSDN 2026-08-07](https://blog.csdn.net/2601_95872481/article/details/162839541) 2026-08-07 发布）：AI/ML 策略同样受 alpha 衰减宿命制约，无"永不失效"特权——① AI 学的是历史模式，依然受"过去不代表未来"限制；② AI 训练数据若有过拟合，结果只会**更隐蔽地**过拟合（深度学习黑箱使过拟合更难被人察觉）；③ AI 学到的"规律"若被大家用，一样被市场套利掉（AI 策略拥挤 = 新的 crowding 衰减）；④ AI 无"自主进化"，该退就要退，跟人一样。**本项目纪律**：§3.3 Champion-Challenger + Drift Observatory + Decay Detection 三件套**同等适用于 AI/ML 策略和非 AI 策略**——AI 策略不因"更先进"而豁免退役标准。**策略失灵是默认假设非意外**（[CSDN 2026-08-07](https://blog.csdn.net/2601_95872481/article/details/162839541)：策略失灵不是 bug 是宿命，一个被广泛使用的策略必然失效——市场效率定理的直接推论）——系统健康 = 失灵了能识别/切换/恢复，不是"永远不失灵"
6. **防遗忘**（BM-MT-05-A）：EWC + 伪回放，新模型适应新分布又不丢历史知识
7. **自动回滚机制**：新 Champion 上线后旧 Champion 保留 7-30 天作为回滚安全保险（[icyfenix.cn](https://ai.icyfenix.cn/ai-infra-engineering/mlops/model-lifecycle.html)）；部署后 24 小时内监控检测到显著指标 drop → 自动回滚到旧 Champion（[kindatechnical 2026-03](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)：automatically trigger rollback when post-deployment monitoring detects significant accuracy drop within first 24 hours）；一键回滚 = 切换 MLflow alias @champion 指针 + 告警（[mlflow.org 2026-06](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)：automated rollback restores previous version without manual intervention）。**回滚触发阈值表**（2026-08-10 补充，施工算法缺失填补——原"显著指标 drop"未量化指标名/drop 幅度/持续时长）：

   | 指标 | drop 幅度 | 持续时长 | 触发动作 | 来源 |
   |---|---|---|---|---|
   | **实盘 Rolling Sharpe** | < 旧 Champion 同期 × 0.5 | 连续 3 个交易日 | 立即回滚（MLflow alias 切换） | 晋升门禁 §3.3 第 9 条对齐 |
   | **ECE 校准误差** | > 旧 Champion × 1.5 | 连续 3 个交易日 | 立即回滚 | MetricGate A/B 双指标纪律 |
   | **最大回撤** | > 旧 Champion MaxDD × 1.3 | 单日突破 | 立即回滚 + 风控告警 | 护栏指标 guardrail |
   | **MAPE 预测误差** | > baseline × 1.3 | 连续 3 天 | 回滚评估（人工审批） | 重训练触发 §3.3 第 8 条对齐 |
   | **订单拒绝率** | > 5%（正常 <1%） | 连续 1 日 | 立即回滚 | 执行层护栏 |
   | **护栏指标**（换手率/滑点偏离） | 任一超限 | 即时 | 立即终止实验 | MetricGate guardrail |

   **回滚 vs 重训练边界**：回滚是"新 Champion 上线 24h-7 天内的紧急恢复"（切换回旧 Champion，新 Champion 落 @challenger 待诊断）；重训练是"Champion 长期退化"（§3.3 第 8 条，保留 Champion 但触发再训练）。回滚是即时动作（秒级 alias 切换），重训练是离线动作（盘后训练）
8. **重训练触发三策略**（[kindatechnical 2026-03](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)）：
   - **定时**（schedule-based）：固定周期重训练（如盘后每日/每周），适合数据量大、更多数据持续改善预测的场景
   - **性能**（performance-based）：监控检测到模型退化超阈值才触发重训练（如 MAPE 退化 1.3x baseline 连续 3 天），更高效但需健壮监控
   - **数据量**（data-volume-based）：新数据累积到一定量（如 10000 行）才重训练，适合数据到达不规律的场景
   - 个人项目默认用**定时+性能双触发**：定时保底（盘后每日重训练），性能触发加速（退化时提前重训练不等定时窗口）
9. **晋升门禁量化指标**（[PMTS 2026-06](https://pmts.elysiumdubai.net/blog/machine-learning-model-retraining-adaptive-ai-trading-pmts-2026-06-18/)）：新模型不自动替换 Champion，须在 OOS 数据上通过量化门禁：
   - **最低 OOS Sharpe**：不低于 Champion 当前 Sharpe × 0.9（允许略低但不可崩塌）
   - **profit factor 下限**：>1.5（总盈利/总亏损，低于此则策略无正期望）
   - **最大回撤上限**：不超过 Champion 当前 MaxDD × 1.2
   - **子周期一致性**：不依赖少数大交易——将 OOS 期间分 3-4 子段，每段 Sharpe 均 >0（避免"一笔暴利掩盖整体平庸"）
   - **Sortino + Calmar 辅助**：下行波动率调整收益 + 回撤调整收益，与 Sharpe 三角验证
10. **滚动数据窗口**（[PMTS 2026-06](https://pmts.elysiumdubai.net/blog/machine-learning-model-retraining-adaptive-ai-trading-pmts-2026-06-18/)）：训练数据用滚动窗口而非无限增长归档——旧观测降权或丢弃，模型优先学习当前活跃 regime；同时保留更长参考窗口记忆罕见但反复出现的压力事件。结果：模型当前但不失忆（current without being amnesiac）
11. **数据/特征版本管理 + 模型血缘**（[mlflow.org 2026-06-15](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)，2026-08 补充）：§3.2 第 3 条可复现性要求"超参+数据版本+代码commit+随机种子"四要素，但数据版本管理与模型血缘追踪需明确机制。**数据版本化**：训练数据集用内容哈希（content hash）或 DVC（Data Version Control）标记版本，每次重训练记录 `dataset_version` → MLflow run params。**特征版本化**：Feature Store（§3.2 第 1 条）的特征定义作为 versioned artifact，防止 training-serving skew（[mlflow.org 2026-06](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)：Feature definitions and data lineage treated as versioned artifacts prevent training-serving skew, one of the most common causes of production failure）。**模型血缘**（model lineage）：MLflow Model Registry 的每个 model version 携带指向 `training_run_id` + `dataset_version` + `code_commit` 的指针，支持从生产模型反查训练数据与代码（[mlflow.org 2026-06-15](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)：Every model artifact in the Mlflow model registry carries a pointer to the exact dataset version and training run that produced it）。**审计场景**：策略异常时，从 MLflow @champion alias 反查 → training_run → dataset_version → code_commit → 定位是数据问题还是代码问题还是模型问题。**个人项目实现**：MLflow 已内置 params/tags/artifacts 追踪，无需额外工具；数据版本用文件 hash + git submodule 管理（不上 DVC/LakeFS）

**行业对标（2026）**：
- Champion-Challenger 是 2026 模型晋升标准模式（[icyfenix.cn](https://ai.icyfenix.cn/ai-infra-engineering/mlops/model-lifecycle.html)、[PAASUP 2026-06](https://ideas.paasup.io/global/mlops-pipeline-en/)）
- MLflow alias 生命周期：@champion / @challenger / @archived（[PAASUP 2026-06](https://ideas.paasup.io/global/mlops-pipeline-en/)）
- **监管引用更新**：原 SR 11-7（2011）已于 **2026-04-17 被 SR 26-2 / OCC Bulletin 2026-13 正式替代**（[Federal Reserve SR 26-02 2026-04-17](https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf)、[risktemplate.com 2026-06-10](https://risktemplate.com/blog/2026-06-10-occ-bulletin-2026-13-model-risk-management-sr-11-7-what-changed/)、[riskpublishing 2026-07-23](https://riskpublishing.com/model-risk-management-sr-11-7-guidance/)）。三大变化：①Risk-based proportionality 替代 implied annual cadence（社区银行/小规模获豁免）；②简化 validation framework（保留 conceptual soundness + outcomes analysis + ongoing monitoring 三核心，移除 VaR backtesting 等具体规定）；③弱化 independence 强调（rigor and effectiveness of review 优先于组织结构）。**GenAI 被显式排除在范围之外**（agency 承诺单独发 AI RFI，截至 2026-06 未落地）。**个人项目定位**：非监管对象（资产 <30B），但 SR 26-02 三核心纪律（conceptual soundness / outcomes analysis / ongoing monitoring）仍可借鉴为模型治理基线——这恰与本项目 Champion-Challenger + 晋升门禁量化 + Decay Detection 5 监控点对应
- MLflow 2026-06 生命周期管理：8-10 阶段循环（开发→staging→生产），governance 是全管线属性非末端检查点（[mlflow.org 2026-06](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)）
- **2026-08 金融非平稳性综述**（[Neurocomputing 2026-08-02 综述](https://m.ebiotrade.com/newsf/2026-8/20260802000456268.htm)）：金融时间序列非平稳性是系统性问题，影响资本配置/风险限额/对冲决策/压力测试/模型治理/监管报告全流程。统一 structural breaks / regimes / concept drift / dataset shift 术语体系，融合时间/统计/空间/本体/因果五维分类。**与本项目对齐**：本项目漂移检测（§3.3 第 4 条 Drift Observatory）+ regime 检测器（10号 spec）+ Decay Detection 5 监控点（§3.3 第 5 条）三件套正是该综述推荐的"漂移感知表征 + 变化检测 + 持续适应"三支柱落地
- **EU AI Act 2026-08-02 强制执行**（[aioutlooks 2026-05-13](https://aioutlooks.com)、[aiunpacker 2026-03-19](https://aiunpacker.com)、[decodethefuture 2026-04-03](https://decodethefuture.org)）：EU AI Act 高风险 AI 系统的**上市后监测义务于 2026-08-02 正式强制执行**，成为本月所有漂移监测讨论的合规底线——高风险 AI 系统（含金融信用评估/交易算法）须建立持续监测机制，检测并响应运行中的性能衰减与漂移。**与本项目对齐**：本项目 Drift Observatory + Decay Detection + 重训练触发机制已满足 EU AI Act 上市后监测义务的技术要求；虽然个人项目非 EU 市场主体（无强制合规义务），但这些纪律是"合规级"治理基线，未来若扩展到机构合作或海外市场可平滑对接

**MLOps 成熟度定位**（[ML-OS/MLOps.md](https://github.com/rohanmistry231/ML-OS/blob/main/MLOps.md)）：
- **Level 0**（手动）：人工训练→人工部署→无监控——**拒绝**（模型是活系统，不是一次性交付物）
- **Level 1**（训练管线自动化）：自动化训练流水线，但手动部署——**起步阶段**
- **Level 2**（CI/CD 自动化）：自动化训练+部署+监控+回滚——**个人项目目标**（MLflow alias + 手动审批门禁 + Champion-Challenger + 自动回滚 + 漂移检测）
- **Level 3**（CI/CD+元学习）：Level 2 + 元学习自动调参——远期（BM-MT-06 元学习）
- **Level 4**（自适应）：模型自动重训练 + multi-armed bandits + Champion-Challenger 持续运行——远期演进（策略数 >5 且手动管理成负担时）
- **定位结论**：个人项目当前处于 Level 1→Level 2 过渡，BM-MT-02-A/B 灰度+影子+对抗鲁棒性施工完成后达成 Level 2

**个人项目简化**：不上 KFP/KServe/K8s 编排；用 MLflow Model Registry alias 管理生命周期 + 手动审批门禁。BM-MT-02 已有 ExperimentTracker（stable），BM-MT-02-A/B 设计态待施工。

**模型训练两环节裁定**（2026-08-12 作战地图全覆盖补丁）：

1. **BM-MT-01-B AI 辅助代码生成与分析师 Agent 反馈**（battle_map 标 production，实际仅 AST 沙箱落地）→ **登记裁定：生成-反馈闭环并入 §3.2 远期候选**。定位：ModuleRequirementSpec→LLM 生成→Critic 审查→反馈收敛→AST 沙箱→人工审核注册。裁定：Generator/Critic/Judge 生成-反馈闭环 + 分析师 Agent 与 §2.3"不做 agent 编排系统"约束冲突，并入 §3.2 LLM 驱动 alpha 挖掘远期候选（Hubble/EvoQuant 已登记同类范式，Phase 5+ 重评）；**安全栈已落地**——[62_business_registry_construction](62_business_registry_construction.md) §4.34② factor_registry schema `llm_safety_stack` 5 字段（ast_validation/dsl_constrained/complexity_control/dual_channel_rag/family_aware_selection）已承载 Hubble AST 验证沙箱契约，Phase 2+ 启用 LLM 因子生成时 MUST 声明全 true。同时登记**battle_map 成熟度标注倒挂真源修正建议**：BM-MT-01-B 标 production 但 `ml_train/ai_operator/` 仅 AST 沙箱部分落地、生成-反馈闭环未施工，成熟度应 production→design，写入 §7 待定项由 battle_map owner 会话裁决。
2. **BM-MT-01-C 策略数字孪生**（design）→ **裁定不做镜像副本**。定位：每策略实时镜像副本→策略健康评估+衰减预警。裁定：不建策略行为镜像副本——"策略健康评估+衰减预警"诉求已由 §3.9 退役 8 维量化阈值（Rolling Sharpe/Drawdown 超历史/profit factor/Win rate+expectancy/Equity curve 斜率/Half-life 预测/Regime 失配/逻辑失效）+ §3.3 Drift Observatory 五类漂移四层架构完整承载，镜像副本属重复建设且单机维护一份实时镜像的仿真成本高。**与 #ARCH-OE-010 边界消歧**：#ARCH-OE-010 裁的是 SIM 域数字孪生 + 世界模型 DreamerV3（市场仿真侧，BM-SIM-05 已降级），本环节是策略行为镜像，两者正交——本裁定不触碰 SIM 域既有裁定。重评条件：策略数 >10 且 8 维阈值+Drift Observatory 出现系统性误报/漏报时。

### 3.4 回测阶段（BM-BT）规范

承接 [battle_map_03_backtest_validation](../battle_map/battle_map_03_backtest_validation.md)（BM-BT-01~07 环节视图）+ [52_backtest_framework_docking](52_backtest_framework_docking.md)（⚠️G23 设计备忘 draft v0.1.0 骨架待讨论——回测门控 why 层未定稿；IS→WFA→OOS 门控当前真源为代码 `src/zephyr/backtest/core/decision_gate.py`）。本节锁定生命周期视角的回测准入门禁与退出条件。

**核心纪律**：
1. **IS→WFA→OOS 三段式门控**（battle_map_03 BM-BT-01~07 + 代码 `decision_gate.py`）：In-Sample 训练 → Walk-Forward Analysis 滚动验证 → Out-of-Sample 样本外验证，三段全过才准入模拟阶段。**WFA 是核心**——固定参数 IS 训练 + 滚动窗口 OOS 验证，模拟"参数不知道未来"的真实场景，防止参数过拟合
2. **过拟合检测三维度**（battle_map_03 BM-BT-05 + [kagels-trading 2026-08-01](https://www.kagels-trading.de/trading-edge/)）：
   - **Deflated Sharpe Ratio**（DSR）：调整回测 Sharpe 反映"多次试错后的最佳结果"（multiple testing penalty），DSR 仍显著 > 0 才算真 edge（与 §3.3 第 4 条漂移检测的 DSR 鉴别复用同一方法）
   - **PBO（Probability of Backtest Overfitting）**：Combinatorially Symmetric Cross-Validation 计算"过拟合概率"，PBO > 50% 则策略大概率过拟合（11号文档已降级为 perturbation PBO 替代）
   - **参数稳定性**：邻近参数产生相似结果（非孤立最优），若轻微调参就性能剧变 = 过拟合
3. **PIT 铁律继承**：回测特征必须用 §3.2 第 1 条 PIT 正确特征（AS OF JOIN + Embargo），无 PIT 特征禁止入回测——这是回测可信的硬底线
4. **现实成本注入**：回测必须注入现实交易成本（滑点 + 佣金 + 冲击成本 + 涨跌停限制 + T+1 约束），不注入则回测 vs 实盘 reality gap 巨大（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Many strategies that pass validation fail at pre-deployment because costs were underestimated, liquidity was assumed infinite, turnover was unrealistic）

**退出条件**（准入模拟阶段）：IS→WFA→OOS 全过 + 过拟合三维度通过 + Deflated Sharpe 显著 + 现实成本注入后 OOS 仍正期望。任一未过 → 回 §3.2 孵化阶段重新假设。

### 3.5 模拟阶段（BM-SIM）规范

承接 [battle_map_04_simulation_validation](../battle_map/battle_map_04_simulation_validation.md) + [53_simulation_live_path](53_simulation_live_path.md)（三阶段迁移 + 4 级 Kill Switch + Alpha Decay，active）。本节锁定生命周期视角的模拟准入门禁与退出条件。

**核心纪律**：
1. **paper → shadow → live 三阶段迁移**（53 号）：paper trading（虚拟撮合，验证逻辑）→ shadow mode（实盘行情 + 虚拟撮合，验证信号）→ live trading（实盘小额，验证执行）。每阶段有独立退出条件
2. **sim↔实盘 divergence 监控**：模拟阶段核心指标是"模拟 vs 实盘"偏离度——若模拟环境与实盘环境差异过大（如撮合逻辑不同、行情延迟不同），则模拟通过不等于实盘能通过。divergence 阈值：成交价偏离 < 0.2%、成交时延偏离 < 1 tick、持仓偏离 = 0（持仓不一致 = 严重 bug）
3. **模拟时长达标**：模拟须持续足够时长覆盖至少 1 个完整 regime 周期 + 至少 30-50 笔模拟交易（与 §3.3 第 2 条影子模式持续时长量化对齐）。模拟时长不足 → 统计显著性不够 → 不准入实盘
4. **4 级 Kill Switch**（53 号）：模拟阶段须配置 4 级 Kill Switch（策略级/组合级/系统级/手动级），任一触发立即停止模拟。模拟阶段是验证 Kill Switch 本身可靠性的最后机会——上线后发现 Kill Switch 失效是灾难

**退出条件**（准入实盘阶段）：三阶段迁移全过 + divergence 可接受 + 时长达标 + Kill Switch 验证可靠 + 上线审批（人工）。任一未过 → 回 §3.4 回测阶段或继续模拟。

### 3.6 多 AI 协作分工规范

**分工现状**（00_index §5/§7）：
- **另一 AI**：持续做 regime（G02 spec / G03 验证 / C1 对比器 / Shrinkage）——正交轨道
- **本边（多会话）**：3 条并行轨道——A 轨道 Alpha 链（G04-G11）/ B 轨道组合风控链（G12-G18）/ C 轨道执行运营链（G19-G26）
- **治理类**（G27/G28）：可后置，本文属此类

**交接纪律**（00_index §7.2 + 01_spec §2.2）：
1. **AI 间不直接通信**——通过产出物（design_memo）+ depgraph path 交接
2. **认领前置阅读**：认领 G05 必须先读 G04 产出物；认领 G12 必须先读 30_multi_strategy §2.1；所有 AI 必读 30_multi_strategy + 00_index
3. **三层分治**（01_spec §2）：生成器管 what is / design_memo 管 why / depgraph 管 what will be——AI 不得越层（生成器不写 why，备忘不写 what is 细节，depgraph 不写 why）
4. **段位编号**（01_spec §4.1）：新文档按业务域入段（0x-9x），段内取下一个空号，不预留坑位——AI 认领时在 00_index §7.3 占用表登记，避免编号撞车
5. **并发文件级冲突纪律**（2026-08-12 实战教训补，#ARCH-WORKTREE-GATE-001）：多会话并发施工共享主工作区 git index——未 commit 到分支的修改随时可能被并发会话的 stash/reset/checkout 抹掉（**未落分支的修改不算完成**）。强制：①Edit 前先 `python scripts/git_commit.py --claim-only` 前移声明持有（搭便车防护）；②commit 唯一入口 `python scripts/git_commit.py --session <id> --files <f> --message <msg>`（GitCommitGateway 串行锁+stash 隔离，裸 git commit 被 GATE-COMMIT-GW 阻断）；③检测到其他活跃 session 时 WORKTREE gate 阻断主工作区 commit，须 `python scripts/session_worktree.py create/exec/merge` 物理隔离（本备忘 v2.11.0 修订即经此流程落地）。**行业背书**（2026-08）：CMU CAID（[arXiv:2603.21489](https://arxiv.org/pdf/2603.21489)，2026-03）实证 branch-and-merge + git worktree 是多 agent 协作的核心协调机制（PaperBench +26.7% / Commit0 +14.3%）；VS Code 2026-08-07 起为 Copilot/Claude/Codex agent session 默认启用 git worktree 隔离（[luonghongthuan 2026-08-10](https://luonghongthuan.com/en/blog/vscode-copilot-agent-worktree-isolation-2026/)）——"并发 agent 未提交修改被静默覆盖"是 2026-08 行业公认失败模式，worktree 隔离是其标准解法

**运行时风险治理小节**（2026-08-12 作战地图全覆盖补丁，与 §3.6 多 AI 协作衔接——多会话 AI 开发模式下的 AI/Agent 行为治理两环节设计）：

> 本项目"多 AI = 人调度多会话"（§3.6），AI 会话通过 git/脚本/depgraph 等工具链作用于代码库与文档库——**AI 行为的运行时风险治理**是"人调度"模式的必要配套：会话产出物（代码修改/注册表变更/文档修订）须在有界自治边界内运行，越界即熔断。以下两环节设计不改变"AI 间不直接通信、所有交接落盘"的既有纪律，而是在纪律之上加运行时护栏。

1. **BM-RC-09 AI/Agent 风险治理**（design）→ **设计三件套：有界自治边界 + 治理漂移防护 + ARS 双轨结算裁定**。定位：Agent 自治行为发生时的治理基线（原定义：有界自治 Bounded Autonomy / 保障缺口管理 / 治理漂移防护 / Agent 行为监控 / ARS 双轨结算模型）。设计：
   - **有界自治边界**（自治动作白名单 + 额度）：AI 会话可自治执行的动作收敛为白名单——①文档读写（design_memos/域文档）；②脚本执行（scripts/ 下已登记治理脚本）；③注册表变更（capability/translation/ARCH 登记，经 §3.8 4 步流程）。**额度**：单会话单次任务修改文件数 ≤10（超出须拆任务）、禁止动作黑名单（删除 production 代码文件/修改治理 gate 脚本本身/绕过 git_commit.py 裸 commit——后者已被 GATE-COMMIT-GW 硬阻断）。白名单外动作一律升级人工审批，对应 BM-RC-09 原"保障缺口管理"——白名单覆盖的动作即"保障内"，黑名单+未列举动作即"保障缺口"须人工兜底。
   - **治理漂移防护**（规则版本锁定 + 变更审计）：治理规则（gate 脚本/阈值 yaml/白名单本身）是"治理的治理"——规则文件随 Git 版本锁定，任何变更走 §3.8 登记 + 修订记录留痕（变更审计），防止"AI 会话逐步放宽约束"的治理漂移（如修改阈值让门禁通过）。与 §3.2 纪律的关系：§3.2 假设状态机管"研究内容"的提出→验证→接受/拒绝留痕，本节管"AI 行为"的白名单→额度→熔断留痕——内容治理与行为治理双层并行，共用 Git 落盘载体。
   - **ARS 双轨结算裁定**：AI 会话产出物的结算分双轨——**快轨**（白名单内 + 额度内 + gate 全过 → 会话自治结算，commit 即生效）/ **慢轨**（白名单外/额度超/gate 不过 → 人工审批结算，审批通过前修改不落分支）。裁定：当前"人调度多会话"模式下慢轨占比高属正常（个人项目人工即用户本人），不设自动化结算比例指标；重评条件：会话数 >5 且慢轨人工审批成为瓶颈时，评估扩大白名单（而非降低门禁）。
   - **与 VR-009 AI 自治熔断器的关系**：[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md) §2.4 已落地 VR-009（`security/access_control/kill_switch.py`，MOD-INF-018）——Agent 越界/模型漂移 PSI/自治等级跳变/资源消耗/连续否决 5 条件触发 NORMAL/TRIPPED/COOLDOWN 状态机，human_gated。本节白名单+额度是 **VR-009 的上游预防层**（边界内运行减少熔断触发），VR-009 是 **本节的下游兜底**（边界被突破时机械熔断）；BM-RC-09 原"漂移超限→触发 BM-RC-03 Kill Switch 熔断"降级链即 VR-009 承载。
2. **BM-RC-04-F AI/Agent 风险监控**（design）→ **设计三件套：行为基线+异常告警 + OWASP 映射检查表 + 告警通道衔接**。定位：盘中持续的 AI 风险监控（原定义：OWASP Agentic Security Top10 扫描 + AST 对抗测试 + MCP 协议安全映射，depgraph 无实现）。设计：
   - **Agent 行为基线 + 异常告警**：从 Git 提交历史/会话日志统计 AI 会话行为基线——操作频率（单会话 commit 次数/小时）、操作类型分布（文档 vs 代码 vs 注册表修改占比）、涉及模块分布；偏离基线（如单会话突增 10× commit 频率、首次触碰从未涉及的 production 模块）即异常告警。实现轻量：复用 §3.6 第 5 条 git_commit.py 会话登记日志 + depgraph 变更记录，统计脚本 <150 行，无独立监控服务。
   - **OWASP Agentic Top10 映射检查表**：OWASP Agentic Security Top10（ASI01 目标操纵/ASI02 工具滥用/ASI03 权限妥协/ASI04 资源过载/ASI05 供应链/ASI06 提示注入/ASI07 不安全输出/ASI08 拒绝服务/ASI09 记忆污染/ASI10 多 agent 信任）逐项映射本项目控制点——ASI02 工具滥用→白名单（BM-RC-09 本节）；ASI03 权限妥协→GATE-COMMIT-GW 硬阻断；ASI06 提示注入→65_git_safety_governance wrapper 命令过滤；ASI07 不安全输出→62 §4.34② llm_safety_stack AST 沙箱；ASI10 多 agent 信任→§3.6"AI 间不直接通信"纪律。检查表随新会话认领时人工过一遍（非自动化扫描），对应原定义"OWASP ASI+AST+MCP 完整映射"阈值的个人项目轻量替代。
   - **与 55_monitoring_review 告警通道衔接**：AI 行为异常告警复用 G26 监控告警通道（[55_monitoring_review](55_monitoring_review.md)，⚠️draft v0.1.0 骨架待讨论——告警通道 why 层未定稿，本节登记的告警需求待 55 号定型后承接落地，与 §3.9 退役告警同一衔接模式）；当前 interim 载体 = 会话日志人工审查 + git_guard 审计输出。重评条件：55 号定型且会话数 >5 时自动化告警通道。

### 3.7 文档治理（段位编号体系）

承接 00_index §8 + 01_spec §4：

- **段位语义**：0x=meta｜1x=地基（regime/数据特征）｜2x=Alpha 策略｜3x=组合仓位与风控｜4x=交易执行｜5x=验证与可观测性｜6x=跨切治理｜9x=开放问题与远期
- **骨架先行工作流**（00_index v2.3.0，2026-08-09）：design_memos 骨架先行（最新篇数台账以 00_index §0 目录为准——v2.3.0 时 38 篇 = 15 active/draft + 23 骨架，后续有新增占用；frontmatter status=draft，仅含 §1 主题组信息 + §7 讨论要点清单）。工作流：先逐篇讨论填空（骨架→active）再施工对应模块
- **status 枚举**：active（已定稿/已落地）/ draft（草案/待讨论/待施工）/ deprecated（废弃）
- **文档种类适配**（01_spec §4.4）：决策备忘按八节模板；spec/工程详设按对象内在结构；诊断报告按因果时间线；施工计划按施工流程；索引/规范/清单按职能。两条硬约束：必须有修订记录 + 必须有开放问题等价节

### 3.8 creation_token / depgraph 登记流程

承接 01_spec §2.2 三层协作流程 + 项目治理硬约束：

**模块创建 4 步**（对齐 BM-RES-10 模块工厂）：
1. **创建**：写 design_memo（why）→ 用 `scripts/governance/apply_depgraph.py` 登记模块到 depgraph 设计态（what will be，build_status=planned）→ **生成 creation_token**
2. **注册**：在 `capability_canonical_file_registry.yaml` 登记模块的 canonical file 路径；在 `module_translation_registry.yaml` 登记 plain_zh 翻译条目
3. **接入**：`scripts/governance/sync_panorama_module.py` 自动派生其余 3 图，`scripts/governance/d5_architecture/generators/align_panoramas.py` 验证五图对齐
4. **验证**：施工后 build_status 从 planned → production；生成器（battle_map 等）从 depgraph 派生当前状态视图（what is）

**ARCH 登记纪律**（项目治理硬约束）：
- 新增模块必须在 `architecture_issue_registry.yaml` 登记 ARCH 条目
- **CAND ≠ ARCH**：候选库/点子池 → `candidate_module_registry.yaml`（CAND-XXX-NNN，登记未来可能做的功能）；架构议题表 → `architecture_issue_registry.yaml`（#ARCH-XXX，登记当前需解决的 bug/决策/治理/技术债）。登记前自问：功能→CAND，问题→ARCH
- 模块 translation 必须在 `module_translation_registry.yaml` 登记 plain_zh 翻译条目

### 3.9 退役阶段量化标准（G26 联动）

> §3.1 状态机 ⑥ 退役阶段原"连续跑输 / 逻辑失效"为定性描述，本节升级为量化标准。**核心原则**：A strategy is retired not when it loses money, but when it loses statistical validity（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：策略退役不是亏钱时，而是失去统计有效性时）。区别于 30_multi_strategy §2.5 Drawdown Protocol（8/15/20/25% 回撤风控阈值，是**风控**触发降级/暂停），退役是**策略级**判定——edge 已结构性失效，不是临时回撤。

**三选一决策矩阵**（[LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)：Reoptimize / Pause-Cut Size / Retire）：

| 决策 | 触发条件 | 动作 |
|---|---|---|
| **Reoptimize（重新优化）** | 核心逻辑仍 fits 当前市场结构 + OOS 仍正期望（扣成本后）+ 邻近参数产生相似结果（非孤立最优） | 参数重优化 + 重新走 §3.3 训练→回测→模拟→实盘 全流程 |
| **Pause / Cut Size（暂停/降仓）** | 证据混合 + expectancy 接近 0 + drawdown 高于正常但仍在可防守风险区间 | 仓位减半（非停止）+ 继续收集证据 + 监控是否恢复 |
| **Retire（退役）** | OOS expectancy 转负 + walk-forward 持续失败 + 现实成本侵蚀 edge + 原始市场前提不再成立 | 归档到策略归档区（§3.9 策略归档机制） |

**退役量化阈值**（多维度并行，单一信号不触发退役决策，[arrowalgo 2026-05-14](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)：Look for a pattern of signals across multiple dimensions）：

| 维度 | 退役阈值 | 数据来源 |
|---|---|---|
| **Rolling Sharpe** | 滚动 100+ 笔交易 Sharpe < 0 持续 2 个独立窗口（[LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)：30-50 笔早期预警，100+ 笔确认；[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/)：Rolling Sharpe degradation） | §3.3 第 5 条 Decay Detection |
| **Drawdown 超历史** | 实盘 drawdown > 回测历史最大 drawdown × 1.5（[arrowalgo 2026-05-14](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)：exceeds that level by 50% or more warrants investigation；[LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)：1.5x-2x prior realized maximum） | Drawdown Protocol 联动 |
| **Profit factor** | profit factor 滑向 1.0（盈亏平衡）持续 2 个独立窗口（[LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)：sliding from 1.5-2.0 toward 1.0 after realistic costs） | 晋升门禁量化指标复用 |
| **Win rate + expectancy 同时下降** | 胜率下降 10-15 个百分点 + 平均交易 expectancy 同时恶化（[arrowalgo 2026-05-14](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)：both win rate and average trade expectancy deteriorating；[LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)：down 10-15 percentage points across back-to-back windows） | 滚动窗口监控 |
| **Equity curve 斜率丧失** | equity curve 平台或下降持续数周/数月（非单周，[arrowalgo 2026-05-14](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)：flat or declining for a meaningful period — not a single week, but several weeks or months） | 净值曲线监控 |
| **Half-life 预测** | 半衰期模型 `α(t) = α₀·e^(-λt)` 预测 alpha 已降至 transaction cost floor 以下（[mathandmarkets 2026-02-22](https://mathandmarkets.com/p/half-lives-of-alpha-why-every-strategy)：可用半衰期 = `-ln(cost_floor/α₀) / λ`） | §3.3 第 5 条 half-life 数学模型 |
| **Regime 失配持续** | 当前 regime 与策略设计 regime 持续不匹配 + 该 regime 历史回测也表现差（[arrowalgo 2026-05-14](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)：market regime has shifted and your strategy was not built to handle the new environment） | regime 检测器联动（10号 spec） |
| **逻辑失效（结构性）** | 原始市场前提不再成立（如打板策略遇 2026 量化占比 35%+ + 程序化新规 + 连板炸板率 68%，[24_daban_strategy_detail](24_daban_strategy_detail.md) 已记录） | 人工判断 + 设计备忘登记 |

**退役流程**（与 G26 [55_monitoring_review](55_monitoring_review.md) 联动——⚠️55 号为 draft v0.1.0 骨架待讨论，监控告警 why 层未定稿；退役量化标准当前由本节承载，55 号定型后承接运营侧告警联动）：
1. **触发**：Decay Detection 5 监控点（§3.3 第 5 条）任一持续告警 → 进入"观察"状态（D-SIGNAL-14 状态机映射）
2. **诊断**：跑最近 3-6 个月数据回测 + 检查策略日志 + 对比其他策略（区分"单策略坏"还是"全策略同时坏=regime 切换"，[arrowalgo 2026-05-14](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)）
3. **决策**：按三选一矩阵裁定（Reoptimize / Pause-Cut / Retire）
4. **退役执行**：仓位减半→暂停新建仓→平掉存量→归档到策略归档区（详见下方"策略归档机制"）+ D-SIGNAL-14 废弃审批 + design_memo status 改 deprecated + depgraph build_status 改 retired
5. **复盘**：归因退役原因按**五骑士分类法**（§3.3 第 5 条）分类——① Crowding 拥挤（41%）→ 换策略/降低拥挤度/寻找新 alpha 源；② Regime Change 状态切换（28%）→ 等待 regime 回归或适配新 regime；③ Overfitting 过拟合（18%）→ 回 §3.2 孵化阶段重新假设；④ Technology Evolution 技术演进（9%）→ 降级或退役；⑤ Regulatory Change 监管变更（4%）→ 退役。归因结论沉淀到 90_methodology_open_questions 防止同类策略再被孵化

**触发式移除纪律**（[quanthedgeai 2026-07-13](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)）：**"希望不是策略；触发式移除才是"**——防止操作者靠希望持有亏损策略。退役流程须**预定义触发器并在触发时机械执行**，不允许"再观察一下"/"可能是暂时回撤"/"下个月再说"等人为延迟。**心理防线**：操作者面对亏损策略的常见心理陷阱是"沉没成本谬误"（已投入大量研究时间）+ "损失厌恶"（不愿实现亏损）+ "过度自信"（相信会回归）——触发式移除用机械规则消除人为判断的偏差。**触发器实现**：在 G26 监控告警中硬编码退役阈值（§3.9 退役量化阈值表）——⚠️55 号为 draft v0.1.0 骨架待讨论，告警硬编码落地待其定型；当前阈值真源为本备忘本节。阈值触发即自动进入"观察"状态并通知，不允许人工抑制（人工只能审批"延长观察"或"加速退役"，不能"取消退役"）

**策略归档机制**（2026-08-10 补充，修复断裂交叉引用）：原引用"策略墓地（30_multi_strategy §3.1 #8 A/B 并行统计保留）"经核实为**断裂引用**——30 号 §3.1 实际是"Model B 拒绝"不含"A/B 并行统计保留"内容；60 号（跨切清理）§3.1 已将"#8 A/B 并行统计"列为 A 模型消除项**删除**（A 模型自然叠加等价实现，无需跨策略仲裁）；"策略墓地"一词全局搜索无任何文档定义。退役策略的归档终点须在本节明确定义，不再依赖已删除的 30 号 #8：
- **归档四件套**：① MLflow Model Registry model version 移至 `@archived` alias（与 @champion/@challenger 并列，[PAASUP 2026-06](https://ideas.paasup.io/global/mlops-pipeline-en/)：MLflow alias 生命周期 @champion/@challenger/@archived）；② design_memo `status` 改 `deprecated`；③ depgraph `build_status` 改 `retired`；④ 策略产物（PnL 曲线 + 参数快照 + training_run_id + 退役原因五骑士归因）归档到 `strategy_archive/<strategy_id>/` 目录（⚠️设计态：目录未建，待首个退役策略触发时施工——代码核查 2026-08-12 `strategy_archive/` 不存在）（⚠️设计态：目录未建，待首个退役策略触发时施工——代码核查 2026-08-12 `strategy_archive/` 不存在）
- **保留统计的意义**（替代已删除的"A/B 并行统计保留"）：归档非"丢弃"，保留退役策略的历史表现作为**基准线**——新策略孵化时须对比"是否优于已退役的同类型策略"（如新动量策略须优于已退役动量策略的 PnL 曲线），避免重新孵化已失败的策略模式（与 §3.2 第 2 条"假设驱动"呼应：已退役策略的失败假设不再重复验证）。A 模型定型后无需跨策略 A/B 投票仲裁（30 号 §3.1 #8 已删），但"同类型策略历史基准对比"仍是有价值的归档用途
- **复活机制**：退役策略归档后不永久封存——若 regime 检测器确认五骑士 ② Regime Change 类退役的 regime 已回归，可经 §3.2 孵化阶段重新评估复活可行性（须重新走训练→回测→模拟→实盘全流程，非直接重启）

**退役流程 5 步施工伪代码**（2026-08-10 补充，施工算法缺失填补——原 5 步仅流程描述无可执行形态）：

```python
def retirement_workflow(strategy_id):
    # Step 1: 触发——Decay Detection 任一监控点持续告警
    decay_alerts = decay_detection.get_active_alerts(strategy_id)
    # "持续"定义：单一监控点连续告警 ≥10 个交易日（约 2 周，过滤单日噪声）
    sustained = [a for a in decay_alerts if a.consecutive_days >= 10]
    if not sustained:
        return  # 未达持续阈值，继续监控
    lifecycle.set_state(strategy_id, "OBSERVING")  # D-SIGNAL-14 状态机

    # Step 2: 诊断——跑最近 3-6 个月回测 + 对比其他策略
    backtest_result = backtest_engine.run(strategy_id, lookback_days=126)  # ~6 个月
    peer_check = compare_with_peers(strategy_id)  # 区分"单策略坏"vs"全策略坏=regime"
    regime_state = regime_detector.current_state()
    diagnosis = {
        "oos_sharpe": backtest_result.sharpe,
        "is_regime_wide": peer_check.all_strategies_degrading,
        "regime_mismatch": strategy_id.design_regime != regime_state,
    }

    # Step 3: 决策——按三选一矩阵裁定
    if diagnosis["oos_sharpe"] > 0 and diagnosis["regime_mismatch"]:
        decision = "REOPTIMIZE"      # 核心逻辑仍有效，重新优化参数
    elif diagnosis["oos_sharpe"] > -0.2 and not diagnosis["is_regime_wide"]:
        decision = "PAUSE_CUT_SIZE"  # 证据混合，降仓继续观察
    else:
        decision = "RETIRE"          # edge 结构性失效，退役

    # Step 4: 退役执行（仅 decision == "RETIRE" 时）
    if decision == "RETIRE":
        position_sizer.scale(strategy_id, 0.5)          # 仓位减半
        order_manager.disable_new_entries(strategy_id)  # 暂停新建仓
        order_manager.flatten(strategy_id)              # 平掉存量
        # 归档四件套（见上方"策略归档机制"）
        mlflow.transition_alias(strategy_id, "@archived")
        design_memo.set_status(strategy_id, "deprecated")
        depgraph.set_build_status(strategy_id, "retired")
        archive_to(strategy_id, f"strategy_archive/{strategy_id}/")
        lifecycle.set_state(strategy_id, "ARCHIVED")    # D-SIGNAL-14 废弃审批

    # Step 5: 复盘——五骑士归因沉淀到 90_methodology_open_questions
    knight = classify_decay_knight(diagnosis)  # Crowding/Regime/Overfitting/Tech/Regulatory
    methodology_log.record(strategy_id, knight, diagnosis, decision)
```

**与回撤 Protocol 的边界**（重要）：
- **回撤 Protocol**（30_multi_strategy §2.5，8/15/20/25%）：是**风控**触发——仓位降级/暂停，但策略本身可能仍有效（临时回撤）
- **退役标准**（本节）：是**策略级**判定——edge 已结构性失效，归档不再启用
- **两者关系**：回撤 Protocol 是"短期防御"，退役是"长期判决"。回撤 Protocol 触发 25% 后若 Decay Detection 5 监控点也持续告警 → 进入退役流程；若 Decay Detection 未告警 → 仅风控降级，策略保留

**2026-08 量化双杀实证**（[新浪财经 2026-08-06](https://finance.sina.com.cn/stock/zqgd/2026-08-06/doc-inimiqxp4745521.shtml)）：2026年7月 A 股量化遭遇 alpha+beta 罕见双杀——沪深300增强超额 -1.51%、中证500增强超额 -4.54%、中证1000增强超额 -1.69%、**动量因子单月回撤 20 个百分点**（"过去十年都非常少见"）。这是上述退役量化阈值的**2026-08 实时验证案例**：动量因子单月-20pp 会触发"Drawdown 超历史 ×1.5"和"Rolling Sharpe < 0 持续 2 个独立窗口"两条退役阈值，印证 alpha decay 加速趋势。**AI 加速修正**（[Meng & Chen 2026, arXiv:2605.23905](https://arxiv.org/pdf/2605.23905)）：AI 普及后 alpha 信号半衰期从 5-7 年缩至 18 个月（Alpha Half-Life Theorem `h(φ)=ln2/[θ+δ(φ)]`，当前 φ≈0.7 采纳率时 h≈18 月），§3.3 第 5 条 Decay Detection 的 half-life 模型 `α(t)=α₀·e^(-λt)` 须以 18 个月为基准校准 λ（λ_AI > λ_pre-AI），而非 mathandmarkets 的 20 个月（pre-AI 基准）。

## 4. 考虑过的替代方案

### 4.1 多 Agent 运行时编排系统 —— 拒绝
- **拒绝理由**：30_multi_strategy §5 已暂缓"LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索"——AI 写 AI 的失控风险高，可控性方案（沙箱+审批+回滚）未验证可靠
- 个人项目的"多 AI"是"人调度多会话"（用户开启多个 AI 对话并行推进），不是"agent 自治编排"——不需要 agent 间通信协议、任务调度器、冲突解决器等重型机制
- 用 design_memo + depgraph path 作为交接点足够：AI 间不直接通信，所有交接落盘可追溯

### 4.2 企业级 MLOps 编排栈（KFP + KServe + K8s）—— 拒绝
- **拒绝理由**：[PAASUP 2026-06](https://ideas.paasup.io/global/mlops-pipeline-en/) 的 KFP+MLflow+KServe 栈是 Kubernetes 原生企业方案，个人项目无 K8s 集群、无运维团队
- 个人项目简化版：MLflow Model Registry alias（@champion/@challenger/@archived）+ 手动审批门禁 + 本地训练脚本——满足 Champion-Challenger 纪律，无 K8s 运维负担
- BM-MT-02 ExperimentTracker 已有 stable 实现，BM-MT-02-A/B 灰度+影子+对抗鲁棒性设计态待施工，不需要 KFP 编排

### 4.3 完整 7 状态机实时编排 —— 简化
- D-SIGNAL-14 Lifecycle Manager 的 7 状态（研发/测试/灰度/生产/观察/废弃/归档）是机构级完整状态机
- 个人项目简化：用 6 阶段（孵化/训练/回测/模拟/实盘/退役）映射 7 状态，状态流转用 design_memo status + depgraph build_status 双字段标记，不建独立的状态机编排服务
- 重评条件：策略数 >5 且手动状态管理成为负担时，考虑建独立 Lifecycle Manager 服务

### 4.4 团队协作平台（Jira/Confluence）—— 拒绝
- **拒绝理由**：个人 + 100% AI 开发无团队，design_memo（why）+ depgraph（what will be）+ 00_index 占用表（分工认领）已覆盖交接需求
- 引入 Jira/Confluence 增加外部依赖与维护负担，且 AI 会话无法直接读写

## 5. 上限定义

### 5.1 系统上限
- **策略数**：3-5 个独立 StrategyBook（30_multi_strategy §4.1 上限）
- **生命周期阶段**：6 阶段（孵化/训练/回测/模拟/实盘/退役），映射 D-SIGNAL-14 7 状态
- **多 AI 协作**：人调度多会话，非 agent 编排；交接靠 design_memo + depgraph path
- **模型晋升**：Champion-Challenger + MLflow alias + 手动审批，无 KFP/KServe 编排；渐进流量梯度 5%→25%→50%→100%；自动回滚（24h 内指标 drop → 切回旧 Champion）；重训练双触发（定时保底+性能加速）见 §3.3；晋升门禁量化（OOS Sharpe≥Champion×0.9 / profit factor>1.5 / MaxDD≤Champion×1.2 / 子周期一致性 + Sortino+Calmar 三角验证）见 §3.3；**双指标纪律**（业务指标 Sharpe/expectancy + ML 指标 AUC/IC/ECE，两项都优于或等于才晋升）+ **ECE 校准门控**（Challenger ECE 不得显著高于 Champion）+ **mSPRT 混合序贯检验**（anytime-valid 无偷看惩罚，月度偷看 12 月 t-test FPR 膨胀至 25% vs mSPRT 保持 5%）+ **e-value 框架**（Ville 不等式 test martingale，e-value 可乘性是 anytime-valid 数学根基）+ **序贯检验方法谱系**（mSPRT/GSPRT/Always Valid P-Value/Free Anytime Validity）+ **贝叶斯替代范式**（Expected Loss/Probability to Be Best，本项目选 mSPRT 因 SR 26-2 频率学派偏好）+ 护栏指标见 §3.3；**影子模式异步架构**（fire-and-forget + timeout + 每日对比分析 5 维度：agreement rate / score correlation / KS distribution / disagreement analysis / latency comparison）见 §3.3；**多策略选择演进路径**（pairwise mSPRT 适配 3-5 策略；策略数 >8 时 Phase 2+ 候选 ASHA tournament successive halving + SERPANT e-process FWER 控制，ASHA 决定"淘汰谁" + SERPANT 保证"淘汰决策统计可靠"，两者正交可组合）见 §3.3；**SCORE e-value FDR 增强**（ICML 2026 overshoot refund 回收 mSPRT e-process 超过 1/α 阈值的"浪费"证据，序贯多 Challenger 串行检验功率提升，Phase 2+ 候选）+ **Shadow Before Swap 维护态 Champion 语义**（Champion 是持续学习的维护态系统非冻结 checkpoint，Challenger 须胜过维护态 Champion 而非初始快照，53 号灰度门禁 Champion 基线须为当前维护态）+ **DPitG 双停止准则**（mSPRT "可停但不决"的决断性补充，精度目标 HDI 宽度+决定性裁决 ROPE 双准则，Phase 2+ 候选）+ **Betting on Bets 随机优势序贯检验**（Champion-Challenger 从均值比较升级到分布比较，一阶/高阶随机优势 anytime-valid 检验，Phase 3 候选）+ **Ranking by Lifts 成本收益 FDR**（mSPRT 的成本感知升级，lfdr knapsack 排序最大化利润同时控制错误晋升财务成本，与 SCORE 正交可组合，Phase 2+ 候选）+ **evalinger futility monitoring 事前放弃**（e-process 反向检验策略 edge≤0 的证据，§3.9 退役从事后升级到事前+事后，<50 行复用 mSPRT 基础设施，Phase 2 候选）+ **鲁棒序贯实验设计**（mSPRT 在模型误设下的鲁棒性安全网，A 股重尾数据高斯假设失效时替代 mSPRT，界定 worst-case MSE，Phase 3 候选）见 §3.3
- **漂移检测**：多方法 Drift Observatory（五类漂移**四层**架构——Layer 1 输入监控：PSI+KS+MMD+Wasserstein 特征漂移（MMD 20 种子基准 FPR=0%/检测率 99.9%/Cohen's d=6.38 为最优，PSI 单独 FPR=39.9% 须配合 MMD；Wasserstein 一维最优传输 O(n log n) 补充 KS 盲区）/ Layer 2 预测监控：预测漂移+CUSUM 残差漂移（CUSUM 重尾失效→广义随机逼近 LLR / 自相关失效→AR(p)-focus / 单窗口局限→PM-CuSum）/ Layer 3 延迟结果监控：ADWIN 概念漂移+标签漂移 / **Layer 4 可证覆盖层：Conformal Prediction**（有限样本覆盖保证 `P(Y∈Ĉ)≥1-α` 任意分布任意模型成立，数学保证的漂移信号非启发式阈值；金融收益须 EWMA 波动率归一化分数 + **CUSUM 漂移检测 + calibration flush 突变处理**（ACI 被动降权在 regime shift 后 60-80 步严重欠覆盖，calibration flush 完全丢弃陈旧校准集立即重建为 minimax 最优 O(√(KT))；复用 §3.3 残差漂移 CUSUM 基础设施）+ **BC-ACI 偏置校正**（在线 EWMA 估计持续预测偏置并纠正区间中心，与 calibration flush 宽度调整正交互补双重保护，<30 行增量）+ **CPTC 变点检测替代**（RED-SDS 结构断裂检测 Phase 4 候选）；RWC regime-weighted conformal 对接 36号 VaR 校准；DASC 谱相似性加权对接 regime 检测器） / composite drift score 阈值 0.35 + CvM 尾部敏感 / WMAPE 整体精度监控 / **MMDEW 流式 MMD 自相关陷阱**（lag-1 ~0.87 须确认窗口+自适应阈值） / Benjamini-Hochberg FDR 校正 / **下游影响门控**统计显著性≠业务显著性 / **SHAP Drift Attribution 漂移归因**（定位根因特征）/ **Drift Robustness 模型漂移鲁棒性评估**（Champion-Challenger 选型辅助）+ **WCTM 统一框架**（适应/检测/诊断三合一 Phase 4 候选）+ **Conformal Kelly 交叉引用**（Layer 4→35号 conformal_kelly_drawdown_dial→31号 Kelly 三层传导链）+ **Report the Floor 基线**（ConformalNaive mandatory baseline）+ **Anytime-valid 共形覆盖监测**（betting martingale 解决覆盖率监测月度偷看 FWER 膨胀至 72%，与 mSPRT 同属 e-value 框架，<30 行）+ **联合 VaR+ES 共形**（ES 单独不可 elicitable 但 pair (VaR,ES) 联合可 elicitable，Layer 4→36号 VaR 链路从单一 VaR 升级到 pair，Phase 3 候选）+ **DT-GOL 双轨几何在线学习**（T+1 标签延迟漂移检测，几何代理无需等标签，Phase 3 候选）+ **CB-PDD 表演性漂移检测**（区分外生漂移 vs 策略自致漂移，加速五骑士 Crowding 归因，Phase 3 候选）+ **ARM 检测器无关变点归因**（漂移检测"哪些维度变了"的有限样本证书，rank-based 对 A 股重尾天然鲁棒，FWER/FDR 控制，Phase 3 诊断增强候选）+ **RLCP 局部化保形预测**（Layer 4 从边际覆盖到条件覆盖的有限样本升级，Phase 4 鲁棒性候选）+ **Decaying-ε-FOCuS 多流最快变点检测**（bandit 多策略/多资产轮巡监测，Phase 3-4 候选）+ **Drift2Act 预算干预框架**（漂移检测→动作的形式化决策层，active risk certificate 在预算约束下触发干预，分级响应阶梯的 risk certificate 升级，ICLR 2026 CAO Workshop，Phase 3 候选）+ **Conformal Abstention Layer 空仓决策**（conformal coverage→abstain decision 数学保证映射，"stop new entries"升级为覆盖保证空仓决策，800 单元析因基准，Phase 3 候选）+ **KDD 2026 漂移检测基准框架**（14 检测器标准化评测，Monte Carlo drift simulation + timing-aware F1/detection time + leave-one-dataset-out 超参优化，Phase 3 验证候选）+ **DTD 动态阈值确定**（固定阈值→自适应阈值，证明动态阈值可证明优于任何单一固定阈值，AAAI 2026，Phase 3 候选）+ **COP 共形乐观预测**（Layer 4 CP 在可预测模式下产生更紧区间，CDF 估计利用 A 股季节性/周期性模式，Nankai/Tsinghua，Phase 3+ 候选）+ **Conditional CTM 污染修复**（betting martingale test-time contamination 修复——自适应区间 Z_t 与被测 Ĉ 形成反馈环，CTM 用固定参考集去污染，anytime Type I+power-one+有界延迟，ICML 2026，Phase 3 与 betting martingale 同期落地）+ **Legendre Jumper Martingales 高阶矩漂移**（betting martingale 一阶矩→k 阶矩扩展，k=2 检测方差/波动率 regime 切换，Variational 版 O(1) 更新，2026-07，Phase 3 候选）+ **Subgroup Under-Coverage Auditing 子组欠覆盖审计**（Layer 4 边际覆盖→条件覆盖的静默失效诊断，按 regime 态/行业/市值分位审计，RLCP 局部化校准的前置诊断，2026-08-06，Phase 3 诊断候选））见 §3.3
- **衰减检测**：Decay Detection 5+4+1 监控点（Rolling Sharpe / Drawdown frequency / Correlation instability / Execution cost drift / Volatility mismatch + Half-life 数学模型（Maven Securities：美国 5.6%/年 欧洲 9.9%/年衰减率递增）+ **五骑士分类法归因** Crowding 41%/Regime 28%/Overfitting 18%/Technology 9%/Regulatory 4% + **IC by forward horizon** 衰减剖面 1d/5d/21d/63d + **Bootstrap IC 半衰期置信区间**（1000 次重采样 95% CI，避免单点估计虚假精确）+ **FSI 拥挤度指标** <0.4 预警 + **策略类型衰减速度经验表** + **AI 不是解药纪律**（AI 策略同等受衰减制约无豁免特权）+ **农耕心态**（信号组合替代皇冠策略））见 §3.3
- **训练数据**：滚动窗口（非无限增长归档），旧观测降权，保留更长参考窗口记忆压力事件
- **MLOps 成熟度**：当前 Level 1→Level 2 过渡，BM-MT-02-A/B 施工完成后达成 Level 2（CI/CD 自动化）；Level 4（自适应）为远期演进见 §3.3

### 5.2 演进路径
- **第一阶段（当前）**：6 阶段状态机用文档+注册表标记，Champion-Challenger 用 MLflow alias + 手动审批
- **第二阶段（策略数 >5 或手动状态管理成负担）**：考虑建独立 Lifecycle Manager 服务（对齐 D-SIGNAL-14 完整 7 状态机）
- **第三阶段（可控性方案验证可靠后）**：重评多 Agent 自治编排（30_multi_strategy §5 暂缓项）

### 5.3 为何是上限而非妥协
- 机构 MLOps（KFP+KServe+SR 11-7 合规）解决的是"多团队 + 多模型 + 监管审计"问题，个人项目无此约束
- "人调度多会话"已能并行推进 28 个主题组（00_index §5 三条轨道），不需要 agent 自治
- Champion-Challenger 纪律（行业 2026 共识）用 MLflow alias 即可实现，不需要 K8s 编排——个人项目的上限是纪律的极致，不是工具的堆叠

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索 | 30_multi_strategy §5 已暂缓；AI 写 AI 失控风险高 | 可控性方案（沙箱+审批+回滚）验证可靠 |
| 独立 Lifecycle Manager 服务（完整 7 状态机编排） | 当前 6 阶段用文档+注册表标记足够 | 策略数 >5 且手动状态管理成为负担 |
| BM-RES-03/08/09 缺失态环节施工（✅ 已解决，v2.13.0 §3.2 研究知识流水线拍板落地） | 原 7 个缺失态环节中 03/08/09 已由 §3.2"研究知识流水线拍板"轻量闭合（Markdown+Git+frontmatter）；04/05 已由 §3.2"研究环境否定式裁定"闭合（不建编排/Notebook）；10 模块工厂已由 §3.8 4 步承载；11 多模态采集随 08/09 轻量方案消解 | —（已拍板，仅余 BM-RES-06-B 论文追踪 Phase 3 远期候选） |
| 企业级 MLOps 编排栈（KFP+KServe+K8s） | 个人项目无 K8s 运维能力 | 团队扩大或模型数显著增加（>10 并行训练） |

## 7. 待定问题

### 7.1 退役标准量化（✅ 已解决，v1.3.0 §3.9 落地）
⑥ 退役阶段的"连续跑输 / 逻辑失效"原为定性描述，已于 **§3.9 退役阶段量化标准**（v1.3.0 起）升级为量化体系——**三选一决策矩阵**（Reoptimize / Pause-Cut / Retire）+ **8 维退役量化阈值表**（Rolling Sharpe<0 持续 2 窗口 / Drawdown 超历史×1.5 / profit factor 滑向 1.0 / Win rate+expectancy 同时下降 / Equity curve 斜率丧失 / Half-life 预测退至 cost floor / Regime 失配持续 / 逻辑失效结构性）+ **退役流程 5 步施工伪代码**（触发≥10 日持续告警→诊断 6 月回测+同类对比→三选一决策→归档四件套→五骑士归因）+ **触发式移除纪律**（机械执行消除沉没成本/损失厌恶/过度自信心理陷阱）+ **策略归档机制**（MLflow @archived + design_memo deprecated + depgraph retired + strategy_archive/ 目录）。与回撤 Protocol（30_multi_strategy §2.5，8/15/20/25% 风控阈值）的边界已在 §3.9 明确：回撤是短期防御（临时降级），退役是长期判决（edge 结构性失效归档）。

### 7.2 BM-RES 缺失态环节的施工优先级（✅ 已解决，v2.13.0 §3.2 拍板落地）
battle_map_01 原有 7 个缺失态环节（BM-RES-03/04/05/08/09/10/11，无锚点），曾是研究孵化域最大空白。**v2.13.0 已一次拍板闭合**：① BM-RES-03-B/08/08-A/09/09-A 由 §3.2"研究知识流水线拍板"轻量建设闭合（Markdown+Git+frontmatter 标签检索，即本节原登记的"Markdown+Git 替代独立系统"思路的正式落地）；② BM-RES-01-C/04/04-A/05-A 由 §3.2"研究环境否定式裁定"闭合（不建容器沙箱/Prefect 编排/JupyterLab，venv+目录隔离+64 号 §6.4 APScheduler 调度基座复用）；③ BM-RES-10 模块工厂已由 §3.8 模块创建 4 步承载；④ BM-RES-11 多模态采集随 08/09 轻量方案消解（LLM 单次抽取即采集后处理）；⑤ BM-RES-06-B 论文追踪登记 Phase 3 远期候选（interim 载体=90/91 号人工文献整合实践）。仅余 BM-RES-06-B 一项远期候选待 Phase 3 评估。

### 7.3 多 AI 会话的上下文交接模板（需人决策）
当前交接靠"认领前置阅读"纪律，但缺少标准化的交接模板。是否需要定义一份"AI 会话交接 brief"模板（包含：前序产出物路径 / 当前状态 / 待决问题 / 不可越的硬约束）？还是依赖 design_memo frontmatter（status/depends_on/related_issues）足够？

### 7.4 00_index 漂移与 52/55 号骨架联动登记（2026-08-12 审查新增，不越界改仅登记）

- **00_index 待同步**（其 owner 会话处理）：①§3 G26 行标 55 号"active v1.21.0"、§0 目录标 52 号"active v1.7.4"/55 号"active v1.21.0"——git log 实证 52/55 号从未离开 draft v0.1.0 骨架（仅 3 个 commit），均为虚构版本；②§0 目录标本备忘 v2.9.1 滞后（实际 v2.10.0+）；③§2 三层快照标 01/02/04 阶段"why 层空白"滞后（本备忘 §3.2/§3.3/§3.5 已承载）；④§3 G24 行标 53 号"待讨论"且产出物名误为 `53_simulation_live_path_simulation_live_path.md`（topic 重复）。

- **52/55 号骨架联动**：52 号（G23 回测 why 层）/55 号（G26 监控告警 why 层）均为 draft v0.1.0 骨架待讨论。本备忘 §3.4/§3.9 已先行承载生命周期侧设计（回测准入门禁、退役量化标准），引用均已标注骨架状态；52/55 号定型后须回填双向联动并复核本备忘 §3.4/§3.9 边界。

### 7.5 BM-MT-01-B battle_map 成熟度标注倒挂（真源修正建议，battle_map owner 会话裁决）
BM-MT-01-B（AI 辅助代码生成与分析师 Agent 反馈）在 battle_map_02 标 **production**，但代码实证 `src/zephyr/ml_train/ai_operator/` 仅 AST 沙箱部分落地、Generator/Critic/Judge 生成-反馈闭环未施工——成熟度标注倒挂，建议真源修正 production→design。本备忘不越界改 battle_map，登记待 battle_map owner 会话裁决（与 §7.4 00_index 漂移登记同一"不越界改仅登记"模式）。

## 8. 引用

### 8.1 相关作战地图与备忘
- [battle_map_01_research_incubation.md](../battle_map/battle_map_01_research_incubation.md)（孵化阶段 33 环节，BM-RES 规范真源）
- [battle_map_02_model_training.md](../battle_map/battle_map_02_model_training.md)（训练阶段 14 环节，BM-MOD 规范真源，Champion-Challenger）
- [battle_map_12_cross_cutting.md](../battle_map/battle_map_12_cross_cutting.md)（D-SIGNAL-14 Lifecycle Manager 7 状态真源条目 + 四模式开关——§3.1 状态机映射与 §3.5 模拟阶段 paper/shadow 模式的横切依据）
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G28 / §5（三轨道）/ §7（多 AI 分工）/ §8（命名规范）
- [01_design_memo_management_spec.md](01_design_memo_management_spec.md) §2.2（三层协作流程）/ §4（命名与结构）/ §4.4（文档种类适配）
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) §5（暂缓项：多 Agent / 数字孪生）/ §2.5（Drawdown Protocol 退役相邻）
- [52_backtest_framework_docking.md](52_backtest_framework_docking.md)（③ 回测阶段，⚠️draft v0.1.0 骨架待讨论——G23 why 层未定稿；回测门控当前真源为代码 `src/zephyr/backtest/core/decision_gate.py` + [battle_map_03](../battle_map/battle_map_03_backtest_validation.md)）
- [53_simulation_live_path.md](53_simulation_live_path.md)（④ 模拟与实盘验证路径，active）
- [55_monitoring_review.md](55_monitoring_review.md)（⑥ 退役标准运营侧承接，⚠️draft v0.1.0 骨架待讨论——G26 监控告警 why 层未定稿；退役量化标准当前由本备忘 §3.9 承载；§3.6 运行时风险治理小节 AI 行为异常告警通道亦待其定型承接）
- [62_business_registry_construction.md](62_business_registry_construction.md) §4.12（ADAPT_STRATEGY 衰减后适应——BM-RES-07-A 当前承载之一）/ §4.34②（factor_registry `llm_safety_stack` 5 字段——BM-MT-01-B 安全栈已落地契约）
- [64_data_source_download_spec.md](64_data_source_download_spec.md) §6.4（APScheduler + task_queue DAG 调度基座——BM-RES-04 研究工作流编排复用真源）
- [65_git_safety_governance.md](65_git_safety_governance.md) §9（不引入沙箱/容器裁定——BM-RES-01-C 研究数据沙箱否定式裁定呼应）
- [90_methodology_open_questions.md](90_methodology_open_questions.md) / [91_density_prediction.md](91_density_prediction.md)（BM-RES-06-B 论文追踪 interim 载体——18 轮 arXiv 人工文献整合实践）

### 8.2 治理注册表
- `capability_canonical_file_registry.yaml`（模块 canonical file 登记）
- `module_translation_registry.yaml`（模块 plain_zh 翻译登记）
- `architecture_issue_registry.yaml`（ARCH 条目登记）
- `candidate_module_registry.yaml`（CAND 候选库）

### 8.3 行业实证（2026）
- [实验追踪与模型注册](https://ai.icyfenix.cn/ai-infra-engineering/mlops/model-lifecycle.html)（icyfenix.cn）—— Champion-Challenger 是 Staging→Production 标准晋升模式；旧 Champion 保留 7-30 天作为回滚安全保险
- [End-to-End MLOps Pipeline with KFP, MLflow, and KServe](https://ideas.paasup.io/global/mlops-pipeline-en/)（PAASUP, 2026-06）—— MLflow alias 生命周期 @champion/@challenger/@archived + 人工审批门禁
- [Champion-Challenger Testing for ML Models](https://metricgate.com/blogs/champion-challenger-model-testing/)（MetricGate, 2026-04）—— 95/5 流量切分 + 序贯检验（SPRT）+ 护栏指标 + "证据不足保留 Champion"
- [Champion / Challenger: Testing AI Models in Production](https://theneuralbase.com/ai-for-finance/learn/intermediate/champion-challenger/)（theneuralbase, 2026-04）—— 金融业 SR 11-7 要求 4-12 周并行验证 + 预注册假设 + 人工审批；交易信号 2-4 周（日内）/ 8-12 周（隔夜）
- [ML Lifecycle Management Explained for Engineers](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)（mlflow.org, 2026-06-15）—— 8-10 阶段循环（开发→staging→生产）；governance 是全管线属性非末端检查点；automated rollback restores previous version without manual intervention
- [Automated Retraining and Model Selection](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)（kindatechnical, 2026-03）—— 重训练触发三策略（定时/性能/数据量）；部署后 24h 内 accuracy drop → 自动回滚；Champion-Challenger 框架代码实现
- [AI 플랫폼 모델 레지스트리와 A/B 배포 파이프라인 설계](https://www.youngju.dev/blog/ai-platform/2026-03-04-ai-platform-model-registry-ab-deploy-2026)（youngju.dev, 2026-03-04）—— 渐进流量梯度 5%→10%→25%→50%→100%，每阶段自动比较指标，异常自动回滚
- [The Complete Production ML Reference — MLOps.md](https://github.com/rohanmistry231/ML-OS/blob/main/MLOps.md)（ML-OS）—— MLOps 成熟度模型 Level 0-4；Level 2 是大多数团队甜蜜点；模型回滚与事件响应 §11；三定律（Living Model / Production Parity / Detection Over Trust）
- [Concept Drift Alarms for Quant Signals](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-alpha-decays)（stockalpha.ai, 2026-02）—— PSI >0.2 moderate / >0.4 high；KS + change-point (PELT/Bayesian) + residual (CUSUM/Page-Hinkley)；Benjamini-Hochberg FDR 多重检验校正；staged operational responses (alert→reduce size→stop entries→quarantine→retrain)
- [Population Stability Index (PSI)](https://theneuralbase.com/ai-for-finance/learn/advanced/population-stability-index-psi/)（theneuralbase, 2026-04）—— PSI >0.10 investigate / >0.25 material drift；SR 11-7 监管要求持续监控；PSI 只检测输入分布偏移不检测概念漂移
- [Multi-Method Drift Observatory](https://github.com/Ledger-Lenz/Ledgerlens-data/issues/35)（Ledger-Lenz, 2026-06）—— PSI + MMD + KS + CvM + ADWIN concept drift 多方法组合；composite drift score 加权 `0.3×PSI + 0.2×MMD + 0.2×KS + 0.15×CvM + 0.15×concept`；阈值 0.35 触发重训练
- [Adaptive Intelligence: How PMTS Re-Trains Its ML Models](https://pmts.elysiumdubai.net/blog/machine-learning-model-retraining-adaptive-ai-trading-pmts-2026-06-18/)（PMTS, 2026-06-18）—— 双时钟重训练（scheduled + event-driven on feature distribution + realized error）；滚动数据窗口（current without being amnesiac）；walk-forward validation；晋升门禁（OOS Sharpe + profit factor + max DD + sub-period consistency + Sortino + Calmar）
- [Shadow Deployment: Test ML Models Without Risk](https://atlan.com/know/shadow-deployment-for-ml-models/)（atlan, 2026-03）—— traffic mirroring + output logging + drift detection + promotion criteria；phased rollout (shadow → canary → full)
- [Why Historical Edge Decays — The Data Behind Strategy Failure](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/)（smartfinancedata, 2026-08）—— 127 策略追踪：83% 18 个月内失效 / 半衰期 11.2 个月 / 仅 8% 存活 3 年；五骑士分类法（Crowding 41% / Regime 28% / Overfitting 18% / Technology 9% / Regulatory 4%）；策略类型衰减速度表
- [What Is Signal Decay in Quant Strategies?](https://www.alphanume.com/blog/what-is-signal-decay)（alphanume, 2026-06-03）—— 两种信号衰减尺度（intra-signal horizon decay + secular alpha decay）；IC by forward horizon（1d/5d/21d/63d 衰减剖面）；McLean-Pontiff 发表后衰减实证
- [How to Detect Model Drift in Machine Learning Pipelines](https://www.vectraops.com/content/how-to-detect-model-drift-in-machine-learning-pipelines/download-pdf/)（vectraops, 2026-07-15）—— 漂移三层架构（input → prediction → outcome）；prediction drift / label drift / concept drift 区分；drift alert 须连接到 model behavior
- [Implementing Data Drift Detection in Production ML](https://www.agencyscript.com/blog/ai-agency-data-drift-detection)（agencyscript, 2026-03）—— 四类漂移（feature / concept / prediction / label）定义与影响；prediction drift 是最可见的漂移类型
- [Concept Drift Detection in Production: Practical Thresholds](https://llmops.report/posts/concept-drift-detection-in-production/)（llmops.report, 2026-04-27）—— 统计显著性不等于业务显著性；gate feature drift alerts through downstream impact estimate；score distribution collapsing toward mean 是漂移信号
- [别只盯着夏普比率：WorldQuant 没明说的 Alpha 失效预警与持续监控实战](https://wenku.csdn.net/column/h4wn2p5dhgm)（CSDN WorldQuant, 2026-06-04）—— Factor Specificity Index (FSI) <0.4 因子已被消化；因子拥挤度监测；Alpha 衰减六大隐秘信号
- [A/B Testing ML Model Deployments: Safe Rollouts](https://metricgate.com/blogs/model-deployment-ab-testing/)（MetricGate, 2026-04）—— 模型 A/B 是双指标问题（business metric + ML metric）；ECE 校准门控；流量切分策略（shadow 0%/canary 1-5%/balanced 50-50/bandit adaptive）
- [Shadow Mode Evaluation AI Prompt](https://mljar.com/ai-prompts/mlops/model-monitoring/prompt-shadow-mode/)（mljar, 2026）—— fire-and-forget async + timeout；每日对比分析 5 维度（agreement rate / score correlation / KS distribution / disagreement analysis / latency comparison）；shadow mode 翻倍计算成本
- [Signal Decay in Algo Trading: Why Strategies Lose Edge](https://algotradingdesk.com/signal-decay-algo-trading-strategies/)（algotradingdesk, 2026-04-25）—— HFT 视角信号衰减五因（market efficiency / crowding / latency arms race / structural changes / overfitting）；continuous strategy rotation + multi-strategy portfolio + adaptive models
- [Sequential A/B Testing for Insurance Champion-Challenger](https://burning-cost.github.io/2026/03/24/sequential-ab-testing-insurance-champion-challenger/)（burning-cost, 2026-03-24）—— mSPRT mixture SPRT 产生 e-process anytime-valid 无偷看惩罚；月度偷看 12 月 t-test FPR 膨胀至 25% vs mSPRT 保持 5%；Johari et al. 2022 + Howard et al. 2021 anytime-valid 置信序列
- [Production Drift Detection Benchmark](https://github.com/royxforge/production-drift-detection/blob/main/README.md)（royxforge, 2026-06-15）—— 20 种子严格基准：MMD 复合排名 #1（FPR=0%/检测率 99.9%/Cohen's d=6.38）vs PSI（FPR=39.9%）vs KL（检测率 95.2%）vs ADWIN（FPR=46.5%）；中位延迟 0 批次
- [PSI+CUSUM+WMAPE 三法联合漂移检测](https://blog.csdn.net/wanghaiwen69/article/details/163591186)（CSDN, 2026-08-08 15:02）—— PSI 特征分布（0.1/0.2/0.4 三级）+ CUSUM 误差突变 + WMAPE 整体精度偏离基线 1.5σ；三层覆盖"特征分布/误差突变/整体精度"
- [Generalized Stochastic Approximation LLR for Robust Change Detection](https://arxiv.org/html/2605.23419v1)（arXiv:2605.23419, 2026-05-22）—— 经典 CUSUM 在超重尾数据（超额峰度>20）100% 误报；广义随机逼近仅用 3 阶矩无需分布解析形式；Kunchenko 误差界；Lean 4 形式化验证
- [AR(p)-focus: Online Changepoint Detection for Autocorrelated Data](https://arxiv.org/pdf/2607.16106)（arXiv:2607.16106, 2026-07-20, Lancaster+Fearnhead+Eckley）—— GLR 扩展到 p 阶自回归；O(log n) 每迭代；金融时间序列自相关使 IID 检测器失效
- [PM-CuSum: Predictive-Mixture CuSum](https://arxiv.org/html/2606.05072v2)（arXiv:2606.05072, 2026-06-15, Aalto+Princeton, H.V. Poor）—— 多窗口预测分布组合；一阶渐近最优；余项阶数比单固定窗口更小
- [Factor Decay Analysis Skill](https://github.com/quantskills/skill-factor-decay)（quantskills, 2026-07-16）—— 多期限 Rank IC → 指数/幂律/双指数拟合 → Bootstrap 1000 次半衰期 95% CI → 换手衰减 + Q5-Q1 分组收益 → 推荐最优再平衡频率
- [Implementing a Multi-Strategy Portfolio End-to-End](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)（quanthedgeai, 2026-07-13）—— "希望不是策略；触发式移除才是"；研究候选（复合分<0.05）→纸面 6 月→半仓 6 月+DSR→全仓→触发式移除
- [EU AI Act Post-Market Monitoring Obligations](https://aioutlooks.com)（aioutlooks, 2026-05-13 + aiunpacker 2026-03-19 + decodethefuture 2026-04-03）—— EU AI Act 高风险 AI 系统上市后监测义务 2026-08-02 强制执行；金融交易算法属高风险类别须持续监测漂移与性能衰减
- [E-Value vs P-Value for Sequential Evidence](https://metricgate.com/blogs/e-value-vs-p-value-evidence/)（MetricGate, 2026-06）—— e-value 是"对原假设下注"的赔付因子，e-values 可乘构成 test martingale，Ville 不等式保证 anytime-valid；e-value → p-value 转换 p=min(1,1/E)
- [When Is an Experiment Done: Decision Thresholds Beyond Statistical Significance](https://github.com/weisberg/knowledge_base_public/wiki/02g.-When-Is-an-Experiment-Done-Decision-Thresholds-Beyond-Statistical-Significance/Home)（weisberg knowledge_base, 2026-02）—— mSPRT + GSPRT 序贯检验方法谱系；贝叶斯 Expected Loss / Probability to Be Best 替代范式；Always Valid P-Value
- [Free Anytime Validity by Sequentializing a Test](https://arxiv.org/html/2501.03982v3)（Koning & van Meer, arXiv:2501.03982, 2025）—— 任何有效检验都可通过序贯化获得 anytime validity 且不损失功效；序贯化 z-test/t-test 在 N 时刻与传统检验一致
- [Sequential Testing vs Fixed-Horizon: When to Use Each](https://www.experimenthq.io/blog/sequential-testing-vs-fixed-horizon)（experimenthq, 2026-12 更新）—— 序贯 vs 固定样本取舍；最坏实践是"用固定样本方法但偷看"（Type I 从 5% 膨胀到 20-30%）
- [258 Data Drift Detection Methods](https://mikenguyen13.github.io/ai_in_action/932-data-drift-detection.html)（mikenguyen13, 2026）—— Wasserstein 距离（Earth Mover's Distance）物理释义：最小搬运工作量；比 KS 更敏感于整体分布形状变化
- [MMDEW: Production-Grade Streaming Drift Detection](https://github.com/striim-labs/online-drift-detection-mmdew)（striim-labs, 2026-03-24，Kalinke et al. 2025 扩展）—— MMD 流式部署自相关陷阱（lag-1 ~0.87 超标聚类）；MMDEW 三机制：automatic recalibration + confirmation window + adaptive thresholding
- [Alpha Decay Detection in Purchased Trading Strategies](https://breakingalpha.io/insights/alpha-decay-detection-purchased-trading-strategies)（breakingalpha, 2025-12）—— Maven Securities：alpha 衰减率美国 5.6%/年、欧洲 9.9%/年且递增；衰减生命周期（discovery→crowding→decay→exhaustion）；decay-resistant design 原则
- [Alpha Decay](https://positioned.app/traders-glossary/alpha-decay)（positioned.app, 2026-02-24）—— "金矿心态"→"农耕心态"转变；portfolio of signals 替代单一皇冠策略；half-life 概念
- [为什么回测年化 35% 的策略实盘四个月击穿历史最大回撤——Alpha Decay](https://blog.csdn.net/2601_95872481/article/details/162839541)（CSDN, 2026-08-07）—— 策略失灵不是 bug 是宿命（市场效率定理推论）；AI 不是解药（AI 学历史模式、更隐蔽过拟合、AI 策略拥挤、无自主进化）；StrategyLifecycle 显式暂停规则
- [Conformal Prediction for Risk-Aware Position Sizing](https://marketmaker.cc/en/blog/post/conformal-prediction-trading/)（marketmaker.cc, 2026-06-12）—— 有限样本覆盖保证 `P(Y∈Ĉ)≥1-α` 任意分布任意模型成立；split conformal 四步；非一致性分数 = 绝对残差；区间宽度 = 动态风险信号→保守仓位
- [Conformal Prediction: Guaranteed Confidence Intervals for Industrial ML](https://www.bcub3.com/en/blog/conformal-prediction-intervalles-confiance-industrie/)（bcub3, 2026-06-22）—— 唯一提供 finite-sample coverage guarantee 且不假设误差分布/模型的方法；CQR 处理异方差；可交换性破坏下的局限
- [Taming Tail Risk: Conformal Calibration for Nonstationary Portfolio VaR](https://arxiv.org/html/2602.03903v3)（arXiv:2602.03903v3, Oxford Marc Schmitt, 2026-08-03）—— regime-weighted conformal calibration (RWC) 指数时间衰减+regime 相似性权重；CRSP 指数+16 美股组合 Basel 99%/97.5% 验证；smooth regime drift 下覆盖界无需 weighted exchangeability
- [Conformal Prediction for Financial Returns: Where Coverage Survives and Breaks](https://conformal.marketmaker.cc/)（Soloviov, 2026, 180 实验 14 方法）—— 边际覆盖在 AR(1)/GARCH 存活(0.901/0.901/0.895)仅突变降(0.877)；条件覆盖是 casualty(GARCH 三分位 0.952/0.915/0.820)；修复：EWMA 波动率归一化分数 spread 0.134→0.040 + ACI 突变修复 0.562→0.875
- [Testing Coverage in Conformal Prediction via VaR Backtesting](https://proceedings.mlr.press/v266/retzlaff25a.html)（PMLR 266, Retzlaff et al. 2025）—— CP ↔ VaR 形式等价；Dynamic Binary Test + Geometric Conformal Backtesting 检验边际+条件覆盖；金融时间序列非平稳评估
- [Drift-Aware Spectral Conformal Prediction (DASC)](https://arxiv.org/html/2606.15953v2)（arXiv:2606.15953v2, 2026-07）—— 谱相似性加权校准残差（recurring regimes 跨时共享信息）；drift score 标记校准池不匹配；金融波动率真实数据验证（§12）；per-step 覆盖界
- [model_monitor: 4-Layer Drift Detection](https://github.com/bonnie-mcconnell/model_monitor)（bonnie-mcconnell, 2026-06）—— Layer 4 = Conformal coverage "Provable model quality bound, Mathematical guarantee, not heuristic"；Layer 1-3 启发式 + Layer 4 可证
- [How to Detect and Fix Production Drift (Complete Guide)](https://emitechlogic.com/how-to-detect-and-fix-production-drift-in-machine-learning-complete-guide/)（emitechlogic, 2026-04-14）—— SHAP Drift Attribution 漂移归因（定位根因特征）；Drift Robustness（Not all models age the same way）；Score Distribution Monitoring；Flag Rate Constraint
- [Drift Localization using Conformal Predictions](https://arxiv.org/pdf/2602.19790.pdf)（arXiv:2602.19790, Bielefeld University, 2026-04）—— conformal-prediction-based drift localization 替代 local testing；高维低信号场景优于传统局部检验
- [Prediction Intervals and Uncertainty Bounds for Trading Forecasts](https://github.com/suenot/278-prediction-intervals-trading)（suenot, 2026-03）—— CQR/MAPIE/jackknife+；interval width = dynamic risk signal；non-stationary 下 adaptive recalibration
- [Optimal Training-Conditional Regret for Online Conformal Prediction](https://arxiv.org/pdf/2602.16537)（arXiv:2602.16537, Liang, Ren & Chen, Princeton/Wharton, 2026-02）—— ACI 边际覆盖保证在 regime shift 后允许 60-80 步严重欠覆盖；minimax 最优算法是 calibration flush（CUSUM 检测 + 完全丢弃陈旧校准集重建）非 ACI 被动降权；训练条件遗憾 O(√(KT)) 是比边际覆盖更严格的准则
- [When Your Coverage Guarantee Means Nothing: Optimal Regret in Online Conformal Prediction under Drift](https://burning-cost.github.io/2026/03/31/optimal-regret-online-conformal-prediction-distribution-drift/)（burning-cost, 2026-03-31）—— ACI gamma=0.005 在 +20% step shift 下首半程覆盖 66.7%/后半程 91.7%，长期平均 valid 但首半程严重欠覆盖"飞行盲打"；calibration flush 代码示例（split-conformal + CUSUM drift detection, on alarm flush calibration set）
- [Simultaneous Coverage and Efficiency Guarantee in Online Conformal Prediction](https://arxiv.org/abs/2607.26577)（arXiv:2607.26577, Vaze, 2026-07-29）—— ACI 仅控制有符号长期覆盖误差（持续单向欠覆盖被符号抵消掩盖）；提出同时控制绝对非抵消覆盖违反 + 预测集效率；对抗设定利用 ACI 更新即 pinball loss 投影在线梯度下降；随机设定 sliding-window quantile tracker + matching minimax 下界
- [Temporal Conformal Prediction (TCP): Adaptive Risk Forecasting](https://arxiv.org/html/2507.05470v5)（arXiv:2507.05470v5, Aich et al., 2025-12）—— TCP = 滚动 split-conformal + 分位数预测器 + TCP-RM 变体（Robbins-Monro 在线偏移）；S&P 500/Bitcoin/Gold 三资产类 95% 覆盖验证；危机窗口（2020-03）区间带 promptly 扩张/收缩
- [BC-ACI: Bias-Corrected Adaptive Conformal Inference](https://arxiv.org/pdf/2604.13253)（arXiv:2604.13253, Lade et al., 2026-04）—— ACI/calibration flush 只调区间宽度无法移动中心；BC-ACI 在线 EWMA 估计持续预测偏置并纠正非一致性分数；ridge regression level shift 后 Winkler 分数改善 32%，自校正模型中性无副作用；与 calibration flush 正交互补（宽度+中心双重保护）
- [Conformal Prediction with Change Points (CPTC)](https://arxiv.org/abs/2509.02844)（arXiv:2509.02844, Zaffran/Goude/Dieuleveut, NeurIPS 2025）—— RED-SDS 结构断裂检测器替代 CUSUM；per-regime 独立学习率；经验覆盖间隙 3-5pp vs ACI 20pp vs FACI 12pp；calibration flush 经验替代路径（Phase 4 候选）
- [Champion/Challenger Model Evaluation Architecture](https://www.aicassindra.com/blogs/ai/ai_champion_challenger.html)（aicassindra, 2026-07-13）—— shadow evaluation 信息价值/风险不对称；promotion 是"measured uncertainty 下的决策"非 faith；segmented significance test 防 aggregate win 隐藏 segment loss；continuous proving ground 保持 champion 诚实
- [Champion vs Challenger: Bank Model Validation](https://www.analyticslane.com/2026/08/04/champion-vs-challenger-como-los-bancos-validan-modelos-nuevos-antes-de-ponerlos-en-produccion/amp/)（analyticslane, 2026-08-04）—— 银行业 Champion vs Challenger 标准：歧视指标（Gini/KS）+ concordance + 迁移矩阵 + Lorenz 曲线 + 分段分析 + 估计财务影响；监管合规上下文
- [WATCH: Weighted-Conformal Test Martingales](https://arxiv.org/html/2505.04608v2)（ICML 2025）—— WCTM 统一框架：在线适应轻度协变量漂移+快速检测严重漂移+根因分析三合一，现有 CTM 不支持在线适应
- [Conformal Kelly: Conformal Prediction Intervals as the Scale in Fractional Kelly Position Sizing](https://arxiv.org/html/2608.01494v1)（2026-08-02）—— conformal 区间作仓位标度：区间宽→缩仓/窄→加仓；slow unweighted per-asset rolling quantiles 优于自适应方法（0.7-5.3pp 年化增长）；downside miss 远超历史率时削减杠杆（回撤 27.7%→20.3%）
- [Report the Floor: A Training-Free Conformal Interval Is a Mandatory Baseline](https://arxiv.org/pdf/2606.09473v1)（2026-06）—— ConformalNaive 5 行代码击败 NPTS 家族（73%/64% 序列胜出），mandatory baseline 先实现 floor 再叠加自适应方法
- [Continuous Evolution Pool (CEP)](https://arxiv.org/pdf/2506.14790v2)（2026-01）—— 循环概念漂移专用预测器动态池+统计基因解耦，无需 ground truth 降误差 >20%；远期候选（策略数>10 评估）
- [ProteuS: Regime-Switching Series Generator](https://arxiv.org/html/2509.11844v1)（2025-08）—— ARMA-GARCH 仿真渐进/突变体制转换，漂移检测评测基准工具；Phase 3 验证候选
- [FIDI Z-Score: Label-Free Neuro-Symbolic Drift Detection](https://dataforcee.us/2026/03/23/neuro-symbolic-fraud-detection-catching-concept-drift-before-f1-drops-label-free/)（2026-03）—— 零标签检测 5/5 seed 全检出有时在 F1 下降前；covariate drift 盲区需独立监控器
- [ASHA: Asynchronous Successive Halving Algorithm](https://arxiv.org/abs/1808.08926)（Li et al. 2018 + FerroQuant 2026-03 white paper）—— 超参优化领域 successive halving 适配为实时策略选择；1056 标的×5 资产类×178 活跃策略 regime-conditional 过滤；N 选 K tournament 比 pairwise 更高效（策略数 >8 时）
- [SERPANT: Anytime-Valid Inference for Online Ranking](https://openreview.net/forum?id=7Y8xRnGQ47)（Gu, Sun, Gang, Xia, ICML 2026，[代码](https://github.com/ranzer30/serpant_python)）—— e-process 控制多模型两两比较的 FWER；tournament sampling 自适应选比较对 + top-k 识别 + early stopping；与 ASHA 正交可组合（排序算法 + 统计框架）
- [QuantaAlpha: LLM-driven Alpha Mining](https://arxiv.org/abs/2602.07085)（2026-02）—— LLM 进化算法挖掘 alpha 因子 trajectory-level evolution；diversified planning + trajectory quality + semantic anchoring + experience transfer 四组件
- [EvoQuant: Self-Evolving Verifier-Guided Strategy Optimization](https://arxiv.org/abs/2607.12455)（2026-07-14, HKUST(GZ)）—— LLM 诊断瓶颈→生成候选编辑→多阶段验证→蒸馏知识自进化；7 策略实证 test Sharpe -0.298→0.538
- [QuantEvolver: RFT for LLM-Based Alpha Factor Discovery](https://arxiv.org/pdf/2605.15412)（2026-05-14，[代码](https://github.com/QuantLLM/QuantEvolver)）—— RFT 强化微调替代 prompt-loop，将量化评估转化为策略更新内化到 LLM 权重，逃离上下文窗口限制；与 QuantaAlpha 轨迹进化本质区别（权重级 vs prompt 级），下一代 alpha 挖掘范式
- [AlphaCrafter: A Full-Stack Multi-Agent Framework for Cross-Sectional Quantitative Trading](https://arxiv.org/pdf/2605.05580)（arXiv:2605.05580）—— Miner Agent（因子挖掘+周期复验剪枝）+ Screener Agent（regime-conditioned 因子集成）+ Trader Agent（策略构造执行）三 Agent 全栈闭环；动态因子管理对抗 alpha decay 优于静态因子集
- [FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery](https://arxiv.org/pdf/2602.14670v1)（arXiv:2602.14670, Tsinghua）—— Modular Skill Architecture（可执行评估工具）+ Experience Memory（成功模式+失败约束）+ Ralph Loop（retrieve→generate→evaluate→distill）；110 因子全 A 股因子库低冗余实证；"Correlation Red Sea"约束下减少冗余搜索
- [AlphaMemo: Structured Search-Process Memory for Self-Evolving Alpha Mining Agents](https://arxiv.org/abs/2606.20625)（arXiv:2606.20625, 2026-05-26, Yu/Zheng/Pan/Liu/Wang/He, University of Sydney + University of Edinburgh）—— 结构化搜索过程记忆（残差/决策/AST 差异）+ Parent-Edit Action Space + AST-diff Edit Motifs + Asymmetric Process Veto（APV）；过程记忆 > 结果记忆，失败否决不对称性；20-trading-day OOS 因子池 + 固定预算发现效率优于基线
- [When Does Your Conformal Model Break? Anytime-Valid Coverage Monitoring](https://burning-cost.github.io/2026/04/04/anytime-valid-conformal-monitoring-coverage-sequential-testing/)（burning-cost, 2026-04-04，基于 [arXiv:2602.04364 Hultberg/Bates/Candès 2026-02](https://arxiv.org/abs/2602.04364)）—— 覆盖率监测的多重检验问题：月度偷看 12 次 α=0.10 则 FWER 膨胀至 72%；解法 betting martingale `M_t=∏(1+λ_s(Z_s-(1-α)))` Ville 不等式 anytime-valid；与 mSPRT 同属 e-value 框架
- [SCORE: Sequential Control with Overshoot Refund for E-values](https://openreview.net/forum?id=qX4Nm7eNM5)（Kuang/Gang/Xia, ICML 2026）—— e-value 超过拒绝阈值后的"超调"证据回收（不等式 `I(y≥1)≤y−(y−1)₊`）；SCORE-LOND/LORD/SAFFRON 严格优于原始方法保持 FDR 控制；序贯多 Challenger 串行检验功率提升
- [Improving Online FDR via Online e-closure and Compound e-values](https://arxiv.org/html/2603.24792v3)（arXiv:2603.24792v3, Xu/Fischer/Ramdas CMU, 2026-07）—— online e-closure 原则 + compound e-values via donations，O(log t) 每步决策，严格优于 e-value/p-value 过程；SCORE 配套研究
- [Admissibility and Complete Classes for FDR Control with E-values](https://arxiv.org/pdf/2607.14380.pdf)（arXiv:2607.14380, Sun&Wang, 2026-07）—— e-value FDR 过程的 admissibility 完整类分析；理论支撑
- [Finite-Sample Conformal Risk Bounds for Joint VaR and ES Forecasting](https://www.mdpi.com/2227-7390/14/15/2847)（MDPI Mathematics, Ye et al., 2026-08-06）—— ES 单独不可 elicitable 但 pair (VaR,ES) 联合可 elicitable（Fissler-Ziegel）；conformal risk control 耦合 VaR 突破频率与突破幅度（VaR-ES gap 归一化）；非可交换 swap-distance + regime-drift β-mixing bound + heavy-tail rate；8 汇率+Bitcoin+GIFT-Eval 验证
- [Train Often, Deploy Selectively: Forward-Gated Model Replacement (SBS)](https://arxiv.org/html/2607.28577v1)（arXiv:2607.28577, Dutta Emory, 2026-07-30）—— Shadow Before Swap：重训练候选不一定胜过持续维护 Champion；warm-refit 路径外+延迟标签配对评估+NLL 优势晋升；528 Challenger 仅晋升 114（减 78.4% 切换）改善轨迹；维护态 Champion vs checkpoint 关键区分
- [E-Values Expand the Scope of Conformal Prediction](https://arxiv.org/html/2503.13050v3)（arXiv:2503.13050v3, Gauthier/Bach/Jordan, 2025-05）—— conformal e-prediction 替代 p-value rank；batch anytime-valid conformal + fixed-size conformal sets + ambiguous ground truth 三应用；e-value 框架扩展 CP 工具箱
- [ARM: Attribution by Rank Maxima for Change Point Analysis](https://arxiv.org/abs/2608.01691)（arXiv:2608.01691, 北京工业大学+南洋理工, 2026-08-03）—— 检测器无关的变点归因 wrapper；rank-based 对重尾分布鲁棒；FWER（Westfall-Young）+ FDR（Benjamini-Yekutieli/e-BH）有限样本控制；2008 危机金融实证
- [DPitG: Decisive Precision is the Goal](https://arxiv.org/abs/2608.05301)（arXiv:2608.05301, Kazin, 2026-08-05）—— 双停止准则（精度 HDI 宽度 + 决定性 ROPE 裁决）；62% 不确定率降到 2% 零假阳性；mSPRT 决断性补充
- [Betting on Bets: Anytime-Valid Testing for Stochastic Dominance](https://arxiv.org/abs/2604.21851v3)（arXiv:2604.21851v3, 2026-08-01）—— 一阶/高阶随机优势序贯 anytime-valid 检验；GRO betting + predictably mixed e-processes；区分 upside vs 均值占优；均值比较的分布级升级
- [RLCP: Randomly Localized Conformal Prediction](https://arxiv.org/abs/2608.06206)（arXiv:2608.06206, Conrad/Isaev/Belomestny/Moulines/Samson, 2026-08-06）—— 局部化保形预测首次有限样本条件覆盖保证；条件覆盖 gap + oracle 长度误差分解 O(h^β)；BC-ACI 全局 vs RLCP 局部互补
- [Decaying-ε-FOCuS: Multi-Stream Quickest Change Point Detection](https://arxiv.org/abs/2601.22561v5)（arXiv:2601.22561v5, Kartzman/Hawkins/Hale Stony Brook/Georgia Tech, 2026-08-01）—— bandit 多流最快变点检测；Decaying-ε-greedy + GLR；无离散化/无漂移幅度下界假设一阶最优；多策略轮巡监测
- [Drift-to-Action Controllers: Budgeted Interventions with Online Risk Certificates](https://arxiv.org/abs/2603.08578v1)（arXiv:2603.08578v1, Lamaakal et al., ICLR 2026 CAO Workshop, 2026-03-09）—— Drift2Act 将漂移监控重构为"带安全约束的决策制定"；sensing layer + active risk certificate 产生 anytime-valid 风险上界 Ut(δ)；Ut(δ)≤τ 低成本动作（重校准/测试时适配）/ Ut(δ)>τ 弃权+回滚+重训练；WILDS Camelyon17/DomainNet 近零安全违反
- [KDD 2026 Drift Detection Benchmark Framework](https://arxiv.org/abs/2606.07789)（arXiv:2606.07789, KDD 2026, 2026-08-09~13 韩国济州岛）—— 14 检测器标准化评测；Monte Carlo drift simulation（abrupt/gradual × 4 漂移类型注入真实数据）；timing-aware 评估指标（F1 detection score + normalized detection time）；leave-one-dataset-out 超参优化协议；7 真实数据集基准
- [Online Shift Detection + Conformal Abstention Layer](https://arxiv.org/abs/2606.11949v3)（arXiv:2606.11949v3, 2026-08-04）—— Conformal Abstention Layer 覆盖保证→弃权决策映射；unweighted + weighted-on-alarm 双模式；800 单元析因基准发现检测难度由 classifier×shift 交互主导（η²=0.185）；generative embeddings silent failure 须投影≤32 维
- [Ranking by Lifts: Cost-Benefit FDR Control for Champion-Challenger](https://arxiv.org/abs/2407.01036v2)（arXiv:2407.01036v2, Basu & Berman, Wharton/ISB）—— 成本收益 FDR 控制框架；lfdr 贪心 knapsack oracle 按"期望 lift/错误切换成本"排序；最大化利润同时控制 FDR + 财务成本；mSPRT 的成本感知升级，与 SCORE 正交可组合
- [evalinger: E-value Practice Guide for Adaptive Clinical Trials](https://arxiv.org/abs/2602.06379v1)（arXiv:2602.06379v1, 2026-02-06）—— 对齐 FDA 2026-01 Bayesian 指南草案；betting-martingale e-process 支持复合 null + futility monitoring + platform-trial multiplicity；连续监控下 e-value power 反超 group sequential；策略退役事前放弃框架
- [DTD: Dynamic Threshold Determination for Concept Drift Detection](https://arxiv.org/abs/2511.09953v1)（arXiv:2511.09953v1, AAAI 2026, Lu et al. UTS）—— 动态阈值可证明优于任何单一固定阈值；检测器 wrapper 增加比较阶段（comparison phase）评估不同阈值在比较窗口的性能选最优；复杂场景（渐变/循环漂移）收益更大且对比较阶段时长 K 鲁棒
- [COP: Conformal Optimistic Prediction](https://arxiv.org/abs/2512.07770v2)（arXiv:2512.07770v2, 2026-02-24, Nankai/Tsinghua）—— 将底层可预测数据模式纳入更新规则；估计非一致性分数 CDF 在存在可预测模式时产生更紧预测区间，估计不准时仍保持覆盖保证；覆盖与遗憾联合界 + distribution-free 有限样本覆盖 + i.i.d. 收敛
- [Robust Sequential Experimental Design under Model Misspecification](https://arxiv.org/abs/2605.12899v1)（arXiv:2605.12899v1, 2026-05-13, Wen/Wu/Shi et al. LSE）—— 模型误设下 A/B 测试序贯设计；统一覆盖 contextual bandit 和动态设置；界定处理效应估计的最坏情况均方误差（worst-case MSE）；mSPRT 高斯假设在重尾数据失效时的安全网
- [Conditional Test Martingales via Model Polling](https://arxiv.org/abs/2602.13848)（arXiv:2602.13848v2, Shaer et al., ICML 2026, 2026-06-12）—— 固定参考集避免 test-time contamination；鲁棒 betting function 显式建模有限参考集估计误差；anytime type-I + power-one + 有界检测延迟；betting martingale 覆盖率监测的污染修复
- [Betting on Moments: Legendre Jumper Martingales](https://arxiv.org/abs/2606.20859)（arXiv:2606.20859v2, Szabadváry, 2026-07-12）—— 移位 Legendre 多项式 betting function 将 Simple Jumper 扩展到高阶矩（k=2 方差/k=3 偏度）；Variational Legendre Jumper 常数时间更新；betting martingale 一阶矩→高阶矩漂移检测升级
- [Auditing Conformal Prediction Coverage for Subgroups](https://arxiv.org/abs/2608.04254)（arXiv:2608.04254, 2026-08-06）—— 有限样本保证的子组欠覆盖审计；预定义子组（regime/行业/市值分位）检测实际覆盖显著低于名义水平；FWER 控制；Layer 4 边际覆盖→条件覆盖的静默失效诊断
- [CAID: Centralized Asynchronous Isolated Delegation](https://arxiv.org/pdf/2603.21489)（arXiv:2603.21489, CMU Geng & Neubig, 2026-03）—— 多 agent 异步协作三核心 SWE 原语：centralized task delegation + asynchronous execution + **isolated workspaces（git worktree）**；实证 branch-and-merge 是多 agent 协作的核心协调机制，PaperBench +26.7% / Commit0 +14.3%——本备忘 §3.6 第 5 条并发文件级冲突纪律的学术背书
- [VS Code Agent Sessions Git-Worktree Isolation](https://luonghongthuan.com/en/blog/vscode-copilot-agent-worktree-isolation-2026/)（luonghongthuan, 2026-08-10）—— GitHub 2026-08-07 起为 Copilot/Claude/Codex agent session 默认启用 git worktree 隔离（每 session 独立工作目录+index，共享 .git 对象库）；"并发 agent 未提交修改被静默覆盖"是行业公认失败模式——本备忘 §3.6 第 5 条的行业标准背书

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G28 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active：回填全部 6 项讨论要点（6 阶段状态机/BM-RES 规范/BM-MOD Champion-Challenger 规范/多 AI 协作分工/文档治理段位编号/creation_token+depgraph 登记）；新增过度工程审查（§4.1 多 Agent 编排拒绝/§4.2 企业级 MLOps 栈拒绝）；补 2026 行业实证 | 策略生命周期总纲定型；2026 行业共识验证 Champion-Challenger + MLflow alias 是模型晋升标准；明确个人项目"多 AI = 人调度多会话"非 agent 编排，拒绝重型协作机制 |
| 2026-08-10 | 1.1.0 | 施工环节补充：§3.3 核心纪律 5→7 条（新增第 6 条自动回滚机制——旧 Champion 保留 7-30 天 + 24h 内指标 drop 自动回滚 + MLflow alias 一键切换；第 7 条重训练触发三策略——定时/性能/数据量 + 个人项目定时+性能双触发）；第 2 条灰度补渐进流量梯度 5%→25%→50%→100%；新增"MLOps 成熟度定位"小节（Level 0-4，个人项目 Level 1→Level 2 过渡）；§5.1 补模型晋升回滚+流量梯度+重训练+MLOps 成熟度上限；§8.3 补 4 条 2026 行业实证 | 2026-08 全网搜索发现施工算法缺失：Champion-Challenger 只有晋升无回滚、灰度无流量梯度、重训练无触发策略、无 MLOps 成熟度定位——晋升与回滚是 Champion-Challenger 的两面，缺回滚则新模型上线后劣化无法自动恢复 |
| 2026-08-10 | 1.2.0 | 施工环节补充：§3.3 核心纪律 7→9 条——第 4 条漂移检测从单一 PSI 升级为多方法 Drift Observatory（PSI+KS+MMD 特征漂移 / ADWIN 概念漂移 / CUSUM 残差漂移 / composite drift score 阈值 0.35 / Benjamini-Hochberg FDR 校正）；新增第 8 条晋升门禁量化指标（OOS Sharpe≥Champion×0.9 / profit factor>1.5 / MaxDD≤Champion×1.2 / 子周期一致性 + Sortino+Calmar 三角验证）；新增第 9 条滚动数据窗口（current without being amnesiac）；§5.1 系统上限补漂移检测+晋升门禁+训练数据三项；§8.3 行业实证补充 6 条 2026 来源（stockalpha drift alarms / theneuralbase PSI / Ledger-Lenz Drift Observatory / PMTS retraining / atlan shadow deployment / ML-OS 三定律） | 2026-08 全网搜索发现施工算法缺失：漂移检测单一 PSI 抓不住多变量联合分布漂移和概念漂移（PSI 只检测边际特征漂移）；晋升无量化门禁则新模型可能"一笔暴利掩盖整体平庸"通过；训练数据无限增长归档则模型学习过时 regime——多方法 Drift Observatory + 量化晋升门禁 + 滚动窗口是 2026 机构级交易系统标准实践 |
| 2026-08-10 | 1.3.0 | 新增 §3.9 退役阶段量化标准（G26 联动）：三选一决策矩阵（Reoptimize/Pause-Cut/Retire）+ 8 维退役量化阈值表（Rolling Sharpe/Drawdown 超历史/Profit factor/Win rate+expectancy/Equity curve 斜率/Half-life 预测/Regime 失配/逻辑失效）+ 退役流程 5 步（触发→诊断→决策→执行→复盘）；§3.3 第 5 条 Decay Detection 补 half-life 数学模型 `α(t)=α₀·e^(-λt)` | 2026-08 全网搜索发现退役标准只有定性描述"连续跑输/逻辑失效"无量化阈值——退役是策略级判定（edge 结构性失效）区别于回撤风控（临时降级），需多维度并行信号模式 + 半衰期模型预测 alpha 衰减到成本地板以下 |
| 2026-08-10 | 1.4.0 | 第五轮审查施工环节流程算法缺失+2026-08 最新研究补充：①§3.3 第 4 条 Drift Observatory 增加预测漂移（prediction drift / output distribution shift）+ 标签漂移（label drift / target prior shift）两类缺失漂移类型（vectraops/agencyscript 4 来源交叉验证 prediction drift 是 IC 下降先行指标）；②新增三层检测架构（Layer 1 输入监控→Layer 2 预测监控→Layer 3 延迟结果监控，递进式避免单一层误报）；③新增下游影响门控（statistical significance ≠ business significance，特征漂移告警须经过下游影响估计过滤，llmops.report 验证）；④§3.3 第 5 条 Decay Detection 增加五骑士分类法（smartfinancedata 127 策略追踪：Crowding 41%/Regime 28%/Overfitting 18%/Technology 9%/Regulatory 4% + 83% 18 月内失效 + 11.2 月半衰期 + 仅 8% 存活 3 年）；⑤增加 IC by forward horizon 衰减剖面（1d/5d/21d/63d，两种信号衰减尺度 intra-signal + secular，alphanume 验证）；⑥增加 FSI 拥挤度量化指标（FSI<0.4 因子已被消化，CSDN WorldQuant 验证）；⑦增加策略类型衰减速度经验表（简单技术形态 8.2 月→多因子 28.6 月，smartfinancedata 127 策略）；⑧§3.3 第 1 条 Champion-Challenger 增加双指标纪律（业务指标+ML 指标两项都优于才晋升）+ ECE 校准门控（MetricGate A/B 验证）；⑨§3.3 第 2 条影子模式增加异步架构（fire-and-forget+timeout+每日对比分析 5 维度，mljar 验证）；⑩§3.9 退役复盘更新为五骑士分类法归因；⑪§5.1 系统上限同步更新双指标+ECE+SPRT+影子异步架构+五类漂移三层架构+下游影响门控+五骑士+IC 衰减剖面+FSI+策略类型衰减表；⑫§8.3 行业实证补充 9 条 2026 来源 | 2026-08-08 全网搜索发现施工算法缺失：①预测漂移+标签漂移缺失则 Drift Observatory 只覆盖 3/5 类漂移（特征/概念/残差），prediction drift 是 IC 下降先行指标（vectraops/agencyscript/llmops.report 3 来源验证）；②下游影响门控缺失则所有特征漂移都告警→告警疲劳（llmops.report：statistical significance without effect size is noise）；③五骑士分类法缺失则退役复盘归因无标准框架（smartfinancedata 127 策略实证五根因影响占比）；④IC by forward horizon 缺失则只有宏观 half-life 无微观衰减剖面→换手频率与 IC 衰减率不匹配是最贵实施错误（alphanume 验证）；⑤FSI 缺失则 crowding 只有定性描述无量化指标（CSDN WorldQuant：FSI<0.4 预警）；⑥双指标纪律缺失则 Challenger 只赢业务指标但 ML 指标退化仍可能晋升（MetricGate：model A/B is a two-metric problem）；⑦影子模式异步架构缺失则 Challenger 阻塞 Champion 响应风险（mljar：challenger call must never block champion response）。七项均为 2026 MLOps+量化交易工程共识最低门槛 |
| 2026-08-10 | 1.5.0 | 第六轮审查施工算法完整性+2026-08-08 最新研究补充（全网搜索 2026-08-08 命中）：①§3.3 第 1 条 Champion-Challenger 统计检验从 SPRT 升级为 **mSPRT 混合序贯概率比检验**（anytime-valid e-process 无偷看惩罚，月度偷看 12 月 t-test FPR 膨胀至 25% vs mSPRT 保持 5%，burning-cost/Johari 2022 验证）+ 95/5 不对称分流 + 预注册假设；②§3.3 第 4 条 Drift Observatory 增加 **WMAPE 整体精度监控**（PSI+CUSUM+WMAPE 三法联合，CSDN 2026-08-08 15:02 命中——特征分布/误差突变/整体精度三层覆盖）；③增加 **MMD 严格基准实证**（royxforge 20 种子：MMD FPR=0%/检测率 99.9%/Cohen's d=6.38 复合排名 #1 vs PSI FPR=39.9%，证明 PSI 单独使用误报不可接受须配合 MMD）；④增加 **CvM 比 KS 尾部更敏感**说明；⑤§3.3 第 4 条 CUSUM 增加三大失效风险与解法——**重尾失效**（金融数据超额峰度>20 经典 CUSUM 100% 误报→广义随机逼近 LLR 仅用 3 阶矩，arXiv:2605.23419）+ **自相关失效**（金融时间序列 AR(p) 使 IID 检测器失效→AR(p)-focus 算法 O(log n)，arXiv:2607.16106）+ **单窗口局限**（→PM-CuSum 多窗口预测分布一阶渐近最优，arXiv:2606.05072 H.V. Poor）；⑥§3.3 第 5 条 Decay Detection 增加 **Bootstrap IC 半衰期置信区间**（1000 次重采样 95% CI 避免单点估计虚假精确，quantskills/skill-factor-decay 验证）；⑦§3.9 退役增加 **触发式移除纪律**（"希望不是策略；触发式移除才是"，机械执行消除沉没成本/损失厌恶/过度自信心理陷阱，quanthedgeai 验证）；⑧行业对标增加 **EU AI Act 2026-08-02 强制执行**（高风险 AI 上市后监测义务，本月所有漂移监测合规底线）；⑨§5.1 系统上限同步更新 mSPRT+MMD 基准+CUSUM 三失效+Bootstrap CI+触发式移除；⑩§8.3 行业实证补充 9 条 2026-08 来源 | 2026-08-08 全网搜索发现施工算法缺失与升级空间：①SPRT 固定样本若中途偷看 FPR 膨胀至 25%，mSPRT anytime-valid 是 2026 序贯检验升级（burning-cost/Johari 2022）；②WMAPE 缺失则 Drift Observatory 只覆盖特征/残差/概念漂移无整体精度层（CSDN 2026-08-08 命中）；③MMD 无严格基准数据则选用缺乏依据（royxforge 20 种子证明 MMD 最优 PSI 误报不可接受）；④CUSUM 假设高斯+IID 在金融重尾+自相关数据上 100% 误报是严重盲点（arXiv:2605.23419 + arXiv:2607.16106）；⑤IC 半衰期单点估计过度自信，Bootstrap CI 量化不确定性（quantskills）；⑥退役无触发式移除纪律则人为延迟（沉没成本谬误/损失厌恶/过度自信），quanthedgeai "希望不是策略"；⑦EU AI Act 2026-08-02 强制执行是本月合规底线。七项均为 2026-08 最新研究实践共识 |
| 2026-08-10 | 1.6.0 | 第七轮审查施工算法完整性+选项之外更好的答案算法+2026-08 最新研究补充（全网搜索 2026-08 命中）：①§3.3 第 1 条 Champion-Challenger 增加 **e-value 框架理论基础**（Ville 不等式 test martingale，e-value 可乘性是 anytime-valid 数学根基，MetricGate 2026-06 验证）+ **序贯检验方法谱系**（mSPRT/GSPRT/Always Valid P-Value/Free Anytime Validity 四方法对比，weisberg 2026-02 + Koning arXiv:2501.03982 2025）+ **贝叶斯替代范式**（Expected Loss/Probability to Be Best，VWO/Statsig 采用，本项目选 mSPRT 因 SR 26-2 频率学派偏好）+ **序贯 vs 固定样本取舍**（最坏实践是用固定样本但偷看，experimenthq 2026-12）；②§3.3 第 4 条 Drift Observatory 增加 **Wasserstein 距离**（Earth Mover's Distance，一维最优传输 O(n log n) 补充 KS 盲区，mikenguyen13 2026）+ **MMDEW 流式 MMD 自相关陷阱**（lag-1 ~0.87 超标聚类导致误报风暴，MMDEW 三机制：recalibration+confirmation window+adaptive thresholding，striim-labs 2026-03）；③§3.3 第 5 条 Decay Detection 增加 **Maven Securities alpha 衰减率**（美国 5.6%/年 欧洲 9.9%/年且递增，breakingalpha 2025-12）+ **农耕心态**（金矿→农耕转变，portfolio of signals 替代皇冠策略，positioned.app 2026-02）+ **AI 不是解药纪律**（AI 策略同等受衰减制约无豁免特权，CSDN 2026-08-07）；④§5.1 系统上限同步更新 e-value+序贯谱系+贝叶斯替代+Wasserstein+MMDEW+Maven衰减率+AI不是解药+农耕心态；⑤§8.3 行业实证补充 8 条 2026 来源 | 2026-08-10 全网搜索发现选项之外更好的答案算法与施工算法缺失：①mSPRT 提到 e-process 但未解释 e-value 框架本身——e-value 可乘性+Ville 不等式是 anytime-valid 数学根基，缺失则 mSPRT 选用理由不完整（MetricGate 2026-06）；②mSPRT 之外有 GSPRT/Always Valid P-Value/Free Anytime Validity/贝叶斯四替代路径，缺失则方法选型无横向对比（weisberg/Koning/experimenthq）；③漂移检测缺 Wasserstein 距离则一维连续特征只有 KS 无最优传输方法（mikenguyen13）；④MMD 流式部署自相关陷阱（lag-1 ~0.87）缺失则未来升级盘中流式 MMD 会遇误报风暴（striim-labs MMDEW）；⑤alpha 衰减率无 Maven Securities 实证数据则 half-life 模型无宏观基准（breakingalpha）；⑥缺"农耕心态"则策略管理哲学停留在"找一个永赚策略"（positioned.app）；⑦缺"AI 不是解药"则可能对 AI 策略过度信任不设退役标准（CSDN 2026-08-07）。七项均为 2026-08 最新研究实践与选项之外更好的答案算法 |
| 2026-08-10 | 1.7.0 | 第八轮审查施工算法完整性+选项之外更好的答案算法+2026-08 最新研究补充（全网搜索 2026-08 命中）：①§3.3 第 4 条 Drift Observatory 新增 **Conformal Prediction 可证覆盖层（Layer 4 数学保证）**——三层架构升级为四层（Layer 1-3 启发式检测→Layer 4 数学保证检测），有限样本覆盖保证 `P(Y∈Ĉ)≥1-α` 任意分布任意模型成立，数学保证的漂移信号非启发式阈值（marketmaker.cc/bcub3/model_monitor 3 来源验证）；三层应用价值（漂移检测覆盖率退化+仓位管理区间宽度+VaR 校准 RWC 对接 36号）；金融收益特殊处理（EWMA 波动率归一化分数 spread 0.134→0.040 + ACI 突变修复 0.562→0.875，conformal.marketmaker.cc 180 实验）；CP↔VaR 等价（PMLR 266 Retzlaff，36号 VaR 回测设施可复用）；DASC 谱相似性加权对接 regime 检测器（arXiv:2606.15953 金融波动率验证）；②新增 **SHAP Drift Attribution 漂移归因**（定位根因特征，emitechlogic + arXiv:2602.19790 conformal-based localization）；③新增 **Drift Robustness 模型漂移鲁棒性评估**（Not all models age the same way，Champion-Challenger 选型辅助）；④§5.1 系统上限三层架构→四层架构+Conformal Prediction+SHAP+Drift Robustness；⑤§8.3 行业实证补充 9 条 2026 来源 | 2026-08-10 全网搜索发现选项之外更好的答案算法：①Drift Observatory 全部是启发式阈值（PSI>0.25/CUSUM>4σ/composite>0.35），无数学保证——Conformal Prediction 提供有限样本覆盖保证 `P(Y∈Ĉ)≥1-α`，是根本性更强的保证层（marketmaker.cc/bcub3/model_monitor/arXiv:2602.03903/conformal.marketmaker.cc/PMLR 266/arXiv:2606.15953 6 来源交叉验证）；②arXiv:2602.03903（2026-08-03 Oxford）RWC regime-weighted conformal VaR 校准在 CRSP+16 美股组合 Basel 99%/97.5% 验证，直接对接本项目 36号 var_calculator；③conformal.marketmaker.cc 180 实证揭示金融收益可交换性违反的修复配方（EWMA 归一化+ACI），缺失则 CP 在 GARCH 下条件覆盖 casualty（高波动区低估 8 个百分点）；④SHAP Drift Attribution 缺失则检测到漂移但不知根因特征（emitechlogic）；⑤Drift Robustness 缺失则 Champion-Challenger 只比业务指标不比漂移鲁棒性（emitechlogic）。五项均为 2026-08 最新研究，Conformal Prediction 是本次审查最大发现——从启发式阈值升级到数学保证 |
| 2026-08-10 | 1.8.0 | 第九轮审查施工算法完整性+选项之外更好的答案算法+2026-08 最新研究补充（全网搜索 2026-08-08 命中）：①§3.3 第 5 条 Decay Detection 新增 **双曲线衰减模型** `α(t)=K/(1+λt)`（arXiv:2512.11913 Lee 2025-12 KAIST，博弈论 Nash 均衡严格推导——N 个 agent 发现同一信号每人赚 K/N，随时间 λt 个新 agent 进入 → α(t)=K/(1+λt)；动量因子双曲线 R²=0.65 优于指数 R²=0.61 优于线性 R²=0.51，验证博弈论地基；机械因子符合双曲线衰减，判断型因子不符合——信号模糊性使套利者进入速度慢；拥挤预测尾部风险而非均值：拥挤反转因子 crash 1.7-1.8×、拥挤动量因子 crash 0.38× p=0.006；与本项目对齐：打板/事件驱动属机械因子应优先用双曲线衰减预测 alpha 寿命，多因子含判断型因子指数衰减仍适用）；②新增 **策略容量理论 break-even capacity + profit-maximising size**（hftradingbook 2026-06-04 + Gatheral 2010 平方根律——net_edge(Q)=g-c·√Q，break-even capacity Q*=(g/c)²，profit-maximising size Q_max=4/9·Q* 即利润最大化资金量仅为容量天花板的 44%；与本项目对齐：31号 Kelly 8%上限是风险约束非容量约束，打板策略容量天然受限 8% 已足够保守，Phase 2 多因子资金扩大后用 Q_max=4/9·Q* 精算策略级容量上限避免"超容量部署导致 net edge 归零"） | 2026-08-10 全网搜索发现选项之外更好的答案算法：①alpha 衰减当前用指数衰减 `α₀·e^(-λt)` 是经验拟合默认选择，但 arXiv:2512.11913 从博弈论 Nash 均衡严格推导出双曲线衰减 `K/(1+λt)` 拟合更优（R²=0.65 vs 0.61 vs 0.51），且区分机械因子（符合双曲线）vs 判断型因子（不符合）——这是"选项之外更好的答案算法"，缺失则 alpha 寿命预测用错误函数形式；②alpha 衰减只有时间维度无规模维度——容量理论 break-even capacity + profit-maximising size=4/9·Q* 提供规模维度约束，缺失则可能"资金超容量部署导致 net edge 归零"（hftradingbook + Gatheral 2010）。两项均为 2026-08 最新研究，双曲线衰减是博弈论推导非经验拟合，容量理论是平方根律的直接推论 |
| 2026-08-10 | 1.9.0 | 第十轮审查施工算法完整性+交叉引用同步：①§3.1 冷启动协议补"渐进建仓节奏细化"T0/T1/T2 三阶段表（时间+表现双门控阶梯式放量：T0 观察 30%×5-10 交易日→T1 小仓 60%×10-20 交易日→T2 常规 100%，门控未达标回退上一阶段+连续 2 次回退进入 §3.9 退役诊断+冷启动期间暂停重训练，youngju.dev/kindatechnical 2026-03 验证）；②§3.3 第 2 条灰度补"影子模式持续时长量化"（须覆盖至少 1 个完整 regime 周期：A 股日内 2-4 周/隔夜波段 8-12 周+至少 30-50 笔影子交易才具统计意义，theneuralbase SR 26-02 4-12 周+LuxAlgo 30-50 笔验证）；③§3.3 新增第 11 条"数据/特征版本管理+模型血缘"（数据版本化 content hash+特征版本化 versioned artifact 防 training-serving skew+模型血缘 MLflow Model Registry 指针 training_run_id+dataset_version+code_commit，mlflow.org 2026-06 验证）；④§3.9 退役阈值表交叉引用 24 号 v1.1.0→v1.2.0 同步；⑤§8.1 引用 52 号 v1.6.1→v1.7.1 同步；⑥§3.3 Conformal Prediction 段新增 **BC-ACI 偏置校正**（ACI/calibration flush 只调区间宽度无法移动中心→BC-ACI 在线 EWMA 估计持续预测偏置并纠正区间中心，与 calibration flush 宽度调整正交互补双重保护，arXiv:2604.13253 Lade et al. 2026-04 验证）；⑦新增 **CPTC 变点检测替代**（RED-SDS 结构断裂检测器替代 CUSUM，per-regime 独立学习率，经验覆盖间隙 3-5pp vs ACI 20pp，arXiv:2509.02844 NeurIPS 2025 验证，Phase 4 候选）；⑧§5.1 系统上限同步更新 BC-ACI+CPTC；⑨§8.3 行业实证补充 BC-ACI+CPTC 2 条 arXiv 来源 | 施工算法完整性审查发现三处缺口+一处宽度 vs 中心盲区：①冷启动协议原仅"30% 仓位上限"无阶梯式放量细化，T0/T1/T2 三阶段表填补"渐进建仓"的施工形态——一次性给 30% 然后跳到 100% 违反"渐进"本意，双门控阶梯式放量是 2026 MLOps 标准实践；②影子模式原仅"渐进流量梯度"无持续时长量化，缺失则可能在单一 regime 验证就晋升——A 股日内 2-4 周/隔夜 8-12 周+30-50 笔是统计显著性最低门槛；③数据版本管理原仅"四要素"原则无明确机制，缺失则 training-serving skew 是生产故障常见根因（mlflow.org 验证）。三项均为 2026 MLOps 工程共识最低门槛。24 号/52 号交叉引用同步因 G04/G23-AI 并发审查升版；④BC-ACI 缺失则 regime shift 后模型持续方向偏置（如牛市训练模型在熊市系统性高估）无法纠正中心，ACI 被迫对称膨胀区间宽度开销正比 2|b|（arXiv:2604.13253 实证：ridge regression level shift 后 ACI 宽度 8.67 vs oracle 3.43 vs BC-ACI 5.50，37% 削减），BC-ACI 与 calibration flush 正交互补（宽度+中心双重保护）；⑤CPTC 缺失则 calibration flush 是唯一变点处理路径，RED-SDS 经验覆盖间隙 3-5pp 优于 flush 理论界但实现更重（NeurIPS 2025 验证），记为 Phase 4 候选保留升级路径。BC-ACI+CPTC 两项均为 2026-04/2025-12 最新 conformal prediction 研究，填补 calibration flush 的宽度 vs 中心盲区 |
| 2026-08-10 | 2.0.0 | 第十一轮审查施工算法完整性+2026-08-08 最新研究补充：①§3.3 Champion-Challenger 第 1 条流量切分补**blast-radius（爆炸半径）原则**（5% 切分上限按「challenger 失效最多波及多少资金」反推非按速度，风险遏制优先于收益验证，MetricGate A/B 2026-04 验证）；②§3.3 Conformal Prediction 段新增 **WCTM 统一框架**（Weighted-Conformal Test Martingales, ICML 2025, arXiv:2505.04608）——适应/检测/诊断三合一，填补 mSPRT（检验）+Conformal（覆盖）之外的"轻度漂移自适应"中间地带，Phase 4 候选；③新增 **Conformal Kelly 交叉引用断点补全**（arXiv:2608.01494, 2026-08-02）——Layer 4 Conformal 区间宽度变化未传导到仓位 sizing，补全三层传导链 Layer 4→35号 conformal_kelly_drawdown_dial→31号 Kelly，slow unweighted per-asset rolling quantiles 优于自适应方法（0.7-5.3pp 年化增长优势）；④新增 **Report the Floor 强基线参照**（arXiv:2606.09473, 2026-06）——ConformalNaive 5 行代码击败 NPTS 家族，Layer 4 实现时 mandatory baseline 先实现 floor 再叠加自适应方法；⑤新增 **远期候选登记**——CEP（循环漂移预测器池，arXiv:2506.14790，远期候选策略数>10 评估）/ ProteuS（漂移检测评测基准，arXiv:2509.11844，Phase 3 验证候选）/ FIDI Z-Score（标签自由检测，dataforcee 2026-03，远期观察 covariate drift 盲区）；⑥§5.1 系统上限同步补 WCTM+Conformal Kelly+Report the Floor；⑦§8.3 行业实证补充 6 条 2026 来源 | 2026-08-08 全网搜索+代码核实发现施工算法缺失两处：①Conformal Kelly 交叉引用断点——Layer 4 Conformal Prediction 已对接 36号 VaR 校准但未对接 31号 Kelly/35号 Conformal Kelly drawdown dial，Conformal 区间宽度变化（漂移信号）未传导到仓位 sizing 是"检测→响应"链路断点（arXiv:2608.01494 2026-08-02 填补：conformal 区间作仓位标度，区间宽→缩仓/窄→加仓，slow unweighted 优于自适应 0.7-5.3pp）；②blast-radius 术语缺失——95/5 不对称分流已实现风险隔离但未明确以"爆炸半径"作为切分原则论述（MetricGate A/B 2026-04：5-10% 不平衡切分非 50/50，风险遏制+收益保留+序贯数学仍工作）。WCTM/Report the Floor/CEP/ProteuS/FIDI 为选项之外更好的答案算法或远期候选，均已做过度工程审查（WCTM Phase 4 候选/Report the Floor mandatory baseline/CEP 远期候选/ProteuS Phase 3 验证候选/FIDI 远期观察） |
| 2026-08-10 | 2.1.0 | 第十二轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08-08 最新研究补充：①§3.3 Champion-Challenger 第 1 条补 **多策略选择演进路径**（选项之外更好的答案算法）——ASHA Tournament-Based Strategy Selection（FerroQuant 2026-03，successive halving N 选 K tournament，策略数 >8 时比 pairwise 更高效，样本复杂度理论保证）+ SERPANT e-process 在线排序（Gu et al. ICML 2026，e-process 控制多模型两两比较 FWER + tournament sampling 自适应选比较对 + top-k 识别 + early stopping；与 ASHA 正交可组合：ASHA 决定"淘汰谁"+SERPANT 保证"淘汰决策统计可靠"），记为 Phase 2+ 候选（3-5 策略规模 pairwise mSPRT 足够不立即施工）；②§3.2 BM-RES 补 **LLM 驱动 alpha 挖掘远期候选**（00_index G28 讨论要点回填）——QuantaAlpha LLM-driven Alpha Mining（arXiv:2602.07085 进化算法挖因子 trajectory-level evolution）+ EvoQuant Self-Evolving Verifier-Guided Strategy Optimization（arXiv:2607.12455 LLM 优化策略代码，7 策略实证 Sharpe -0.298→0.538）+ Strategy-Dev-Manager paper→factor→decay 流水线（Vibe-Trading），三方案均涉及 LLM 自主生成/优化策略代码与 §2.3"不做 agent 编排系统"约束一致记为远期候选；③§3.1 修正 §3.9 命名引用一致性（"退役流程诊断"→"退役阶段量化标准"）；④§5.1 系统上限补多策略选择演进路径；⑤§8.3 行业实证补充 4 条 2026 来源（ASHA/SERPANT/QuantaAlpha/EvoQuant） | 2026-08-08 全网搜索发现施工算法完整性两项补充：①多策略选择缺"N 选 K"演进路径——pairwise mSPRT 适配 3-5 策略但策略数 >8 时 O(N²) 组合数+FWER 膨胀须升级 tournament（ASHA+SERPANT 正交组合是选项之外更好的答案算法，ICML 2026 最新）；②§3.2 BM-RES 缺 LLM 驱动 alpha 挖掘远期候选登记（00_index G28 讨论要点已列但未回填 61 号 body）。两项均为 2026 生命周期管理+策略选择工程共识，补强后多策略选择+研究孵化双路径完整 |
| 2026-08-10 | 2.2.0 | 第十三轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08 最新研究补充：①§3.3 第 1 条补 **mSPRT 施工伪代码**（MSPRTChampionChallenger 类：高斯 mixture 似然比累加+tau 标定流程+Ville 不等式边界判定 1/α=20+冷启动兜底，Johari et al. 2022 闭式解，施工算法缺失填补——理论描述完整但无可执行形态）；②§3.3 第 4 条补 **CUSUM 重尾失效 Phase 1 缓解措施**（金融数据超额峰度>20 经典 CUSUM 100% 误报是实盘生存级问题，Phase 1 四措施：winsorize 1%/99% 截尾+CUSUM 降权 MMD 提权+3-5 日确认窗口+残差替代原始收益，<35 行代码零外部依赖，Phase 3 升级广义随机逼近 LLR/AR(p)-focus 时预处理仍保留）；③§3.3 第 7 条补 **回滚触发阈值表**（6 指标量化：Rolling Sharpe<旧×0.5 连续 3 日/ECE>旧×1.5/MaxDD>旧×1.3 单日/MAPE>baseline×1.3 连续 3 天/订单拒绝率>5%/护栏任一超限，原"显著指标 drop"未量化指标名/drop 幅度/持续时长）；④§3.9 补 **退役流程 5 步施工伪代码**（retirement_workflow：触发≥10 日持续告警→诊断 6 月回测+同类对比→三选一决策矩阵→退役执行归档四件套→五骑士归因，原 5 步仅流程描述无可执行形态）+ **策略归档机制**（修复断裂"策略墓地"引用——30 号 §3.1 #8 已删/A 模型消除，新建归档四件套：MLflow @archived+design_memo deprecated+depgraph retired+strategy_archive/ 目录，保留统计作基准线+复活机制）；⑤§3.3 第 4 条补 **四层 Drift Observatory 联动编排伪代码**（drift_observatory_orchestrate：四层并行检测+下游影响门控 Layer 1+CUSUM→calibration flush 联动 Layer 2→4+加权 composite score Layer 4 权重 0.40 最高+五级分级响应映射 alert/reduce/stop/quarantine/retrain+Layer 4 coverage_breach 直接触发 RETRAIN 绕过阈值，施工算法缺失填补——四层架构+分级响应+门控+联动均为分散描述缺可执行编排逻辑）；⑥§3.2 补 **QuantEvolver RFT 范式**（arXiv:2605.15412 2026-05，RFT 强化微调替代 prompt-loop 将量化评估转化为策略更新内化到 LLM 权重逃离上下文窗口限制，与 QuantaAlpha 轨迹进化本质区别权重级 vs prompt 级，标注为下一代 alpha 挖掘方向）；⑦§3.3 第 4 条补 **DASC 谱共形 Phase 4 候选登记**（arXiv:2606.15953v2 2026-07，谱相似性加权校准残差 regime 循环场景跨时共享信息+drift-gated 窗口+diagnostic triangle，与 calibration flush 互补突变走 flush 循环走 DASC，金融波动率真实数据验证，Phase 4 鲁棒性候选）；⑧版本号同步 4 处（24 号 v1.2.0→v1.5.0/35 号 v1.11.0→v1.18.0/52 号 v1.7.1→v1.7.2/55 号 v1.8.0→v1.12.0）；⑨§8.3 行业实证补充 QuantEvolver 引用 | 施工环节流程算法完整性审查发现 5 处施工缺口+2 处选项之外更好的答案算法+1 处断裂引用修复：①mSPRT 理论完整但无可执行形态（似然比累加/tau 标定/边界判定三要素缺施工伪代码）；②CUSUM 重尾 100% 误报是实盘生存级问题但 Phase 3/4 解法（广义随机逼近 LLR/AR(p)-focus/PM-CuSum）都是远期，Phase 1 须有可施工缓解措施避免误报风暴；③回滚触发"显著指标 drop"未量化则新 Champion 上线后劣化无法机械判定回滚时机；④退役流程 5 步仅描述无可执行形态+"策略墓地"引用断裂（30 号 #8 已删）则退役策略归档终点不明；⑤四层 Drift Observatory 各层+分级响应+门控+联动分散描述缺编排逻辑则施工时各层如何聚合告警映射响应无据。五项均为施工算法闭环必需。QuantEvolver RFT（arXiv:2605.15412）是 2026-05 最新 LLM alpha 挖掘研究，RFT 权重级内化比 QuantaAlpha prompt 级轨迹进化更深一层是下一代方向；DASC（arXiv:2606.15953v2）是 2026-07 最新 conformal 研究，谱加权 regime 循环场景是 calibration flush 的互补升级，金融波动率验证直接契合本项目 |
| 2026-08-10 | 2.3.0 | 第十四轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08-08 最新研究补充（全网搜索 2026-08 命中）：①§3.3 第 4 条补 **DT-GOL 双轨几何在线学习**（arXiv:2606.22950 2026-06-22，T+1 标签延迟漂移检测施工算法缺失填补——Layer 3 ADWIN 标注"延迟 ground truth"但未提供标签延迟处理机制，A 股 T+1 收益标签天然延迟 1 天，DT-GOL 用特征空间实时拓扑演化作几何代理无需等标签，双轨架构主学习器严格用延迟真值+瞬态分支几何软知识前向适配，Phase 3 候选）；②§3.3 第 4 条补 **CB-PDD 表演性漂移检测**（arXiv:2412.10545v2 2025-04，选项之外更好的算法——所有漂移检测假设漂移外生但量化交易存在表演性漂移即策略自身交易导致分布变化，CB-PDD 区分 exogenous vs endogenous 漂移，加速五骑士 ① Crowding 41% 归因，Phase 3 候选）；③§3.3 第 4 条补 **Anytime-valid 共形覆盖监测 betting martingale**（arXiv:2602.04364 Hultberg/Bates/Candès 2026-02，施工算法缺失填补——Layer 4 说"监控覆盖率<名义覆盖即漂移"但覆盖率监测本身有多重检验问题：月度偷看 12 次 α=0.10 则 FWER 膨胀至 72%，与 mSPRT 解决 Champion-Challenger 月度偷看 FPR 25% 完全同构，解法 betting martingale `M_t=∏(1+λ_s(Z_s-(1-α)))` Ville 不等式 anytime-valid，与 mSPRT 同属 e-value 框架复用同一数学基础设施，<30 行，Phase 3 与 Layer 4 CP 同期落地）；④§3.3 第 1 条补 **SCORE e-value FDR 增强**（ICML 2026 Kuang/Gang/Xia，选项之外更好的答案算法——mSPRT e-process 超过 1/α 阈值的"超调"证据被丢弃，SCORE 用不等式 `I(y≥1)≤y−(y−1)₊` 回收 overshoot 提升 FDR 功率，序贯多 Challenger 串行检验场景适用，与 ASHA+SERPANT 空间维度正交 SCORE 是时间维度，Phase 2+ 候选；配套 arXiv:2603.24792v3 compound e-values via donations + arXiv:2607.14380 admissibility 完整类）；⑤§3.3 第 4 条补 **联合 VaR+ES 共形**（MDPI Mathematics 2026-08-06 Ye et al.，选项之外更好的答案算法——Layer 4→36号 VaR 链路当前用 RWC 校准单一 VaR 分位数，但 ES 单独不可 elicitable 须 pair (VaR,ES) 联合可 elicitable Fissler-Ziegel loss，联合共形耦合 VaR 突破频率与突破幅度 VaR-ES gap 归一化，非可交换 swap-distance+regime-drift β-mixing bound+heavy-tail rate，Phase 3 候选升级 RWC→pair）；⑥§3.3 第 1-2 条补 **Shadow Before Swap 维护态 Champion 语义**（arXiv:2607.28577 2026-07-30 Dutta Emory，施工算法缺失补充——Champion-Challenger 隐含假设 Champion 是静态 checkpoint 但生产 Champion 是持续学习的维护态系统，重训练候选不一定胜过维护态 Champion，SBS 528 Challenger 仅晋升 114 减 78.4% 切换改善轨迹，53 号灰度门禁 Champion 基线须为当前维护态非部署时快照，Phase 1 纪律补强零代码增量）；⑦§5.1 系统上限同步更新 SCORE+SBS+anytime-valid 共形覆盖监测+联合 VaR+ES+DT-GOL+CB-PDD；⑧§8.3 行业实证补充 7 条 2026 来源；⑨§7.1 退役标准量化标记为"✅ 已解决"（v1.3.0 §3.9 已落地，原 stale pending 清理）；⑩版本引用同步 52 号 v1.7.2→v1.7.3 / 53 号 v1.6.2→v1.6.3 / 55 号 v1.12.0→v1.13.0 / 35 号 v1.18.0→v1.19.0 | 施工环节流程算法完整性审查发现 3 处施工缺口+4 处选项之外更好的答案算法：①Layer 3 标注"延迟 ground truth"但 T+1 标签延迟是 A 股硬约束，缺处理机制则概念漂移检测延迟=标签延迟+算法延迟（DT-GOL 双轨几何代理填补）；②Layer 4 覆盖率监测用固定样本思维处理序贯监测，月度偷看 FWER 膨胀至 72% 是与 mSPRT 同构的偷看惩罚问题（betting martingale 填补，与 mSPRT 同属 e-value 框架）；③Champion-Challenger 隐含 Champion 是静态 checkpoint 但生产 Champion 是维护态系统（SBS 填补语义区分，53 号灰度门禁须明确维护态基线）。四项选项之外更好的答案算法：①SCORE overshoot refund 提升 mSPRT 序贯多检验功率（ICML 2026）；②联合 VaR+ES 共形是 Layer 4→36号 VaR 链路的正确形式（ES 须联合 VaR 才可 elicitable）；③CB-PDD 区分外生 vs 表演性漂移加速 Crowding 归因；④DT-GOL 几何代理解 T+1 标签延迟。七项均为 2026-08 最新研究，DT-GOL/betting martingale/SBS 为施工算法闭环必需，SCORE/联合 VaR+ES/CB-PDD 为选项之外更好的答案算法 |
| 2026-08-10 | 2.4.0 | 第十五轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08-08 最新研究补充（全网搜索 2026-08-01~08 命中）：①§3.3 第 4 条补 **ARM 检测器无关变点归因**（arXiv:2608.01691 2026-08-03 北京工业大学+南洋理工，选项之外更好的答案算法——SHAP Drift Attribution 用 SHAP 值归因漂移到特征但高维重尾不稳定且无 FWER 控制，ARM 是检测器无关 wrapper 接受任意检测器定位变点返回"已认证变化"坐标集+location/scale 标签，rank-based 对 A 股重尾天然鲁棒，三项有限样本保证 per-coordinate validity+精确 FWER 控制 Westfall-Young+高维 FDR 控制 BY/e-BH，2008 危机金融实证，与 SHAP 正交 SHAP 管特征级 ARM 管资产级，Phase 3 诊断增强候选）；②§3.3 第 1 条补 **DPitG 双停止准则**（arXiv:2608.05301 2026-08-05 Kazin，选项之外更好的答案算法+施工算法缺失填补——mSPRT anytime-valid 保证"任意时刻停都保持 Type I 控制"但"可停"≠"能决"，停止时可能仍处于 CONTINUE 证据不足状态导致 Champion-Challenger 陷入"持续观察无结论"僵局，DPitG 双停止准则同时要求精度目标 HDI 宽度 ω+决定性裁决 ROPE 完全在内接受 H0/完全在外接受 H1/重叠继续，公平硬币仿真 62% 不确定率降到 2% 零假阳性仅多花 5% 样本，Phase 2+ 候选替代粗暴 max_sample_size 兜底）；③§3.3 第 1 条补 **Betting on Bets 随机优势序贯检验**（arXiv:2604.21851v3 2026-08-01，选项之外更好的答案算法——mSPRT H1 是 Challenger 均值收益>Champion 均值收益均值比较但均值相同左尾更厚策略不优于左尾更薄策略，量化交易关心整个收益分布非仅均值，Betting on Bets 用 e-process 构造一阶/高阶随机优势序贯 anytime-valid 检验 GRO betting+predictably mixed e-processes 渐近 power-one 保证，区分 upside vs 均值占优，mSPRT 均值差的分布级升级，Phase 3 候选）；④§3.3 第 4 条补 **RLCP 局部化保形预测**（arXiv:2608.06206 2026-08-06 Conrad et al.，选项之外更好的答案算法——Layer 4 覆盖保证是边际覆盖但条件覆盖是更强保证，BC-ACI 纠正全局偏置非局部条件校准，RLCP 首次给出对已实现局部邻域有限样本联合保证条件覆盖 gap+oracle 长度误差分解 O(h^β)，BC-ACI 全局序列 vs RLCP 局部条件互补，calibration flush 管突变+BC-ACI 管偏置+RLCP 管局部三者正交，Phase 4 鲁棒性候选）；⑤§3.3 第 4 条补 **Decaying-ε-FOCuS 多流最快变点检测**（arXiv:2601.22561v5 2026-08-01 Stony Brook/Georgia Tech，选项之外更好的答案算法——Drift Observatory 各检测器假设每条流持续监控但多策略/多资产面板计算预算有限无法全量高频检测，Decaying-ε-FOCuS bandit 最快变点检测 M 条流一条均值未知漂移每步采样一条 Decaying-ε-greedy+GLR 首次无离散化无漂移幅度下界假设一阶最优，CUSUM 单流 vs FOCuS 多流轮巡，ARM 归因哪些维度变了事后 vs FOCuS 决定先监测哪条流事前正交，Phase 3-4 候选策略数>8 或因子数>15 时评估）；⑥§5.1 系统上限同步更新 ARM+DPitG+Betting on Bets+RLCP+Decaying-ε-FOCuS；⑦§8.3 行业实证补充 5 条 2026-08 来源 | 施工环节流程算法完整性审查发现 2 处施工缺口+5 处选项之外更好的答案算法：①mSPRT "可停但不决"——anytime-valid 保证任意时刻停的 Type I 有效性但不保证停止时有明确结论，DPitG 双停止准则填补决断性（HDI 宽度+ROPE 裁决）；②SHAP Drift Attribution 高维重尾不稳定且无 FWER 控制——ARM rank-based wrapper 填补检测器无关变点归因+有限样本 FWER/FDR 控制。五项选项之外更好的答案算法：①ARM 漂移检测哪些维度变了的有限样本证书（rank-based A 股重尾鲁棒）；②DPitG mSPRT 决断性补充（62%→2% 不确定率零假阳性）；③Betting on Bets 均值比较的分布级升级（随机优势 anytime-valid）；④RLCP 边际覆盖到条件覆盖有限样本升级（局部化保形）；⑤Decaying-ε-FOCuS 多流轮巡监测（bandit 采样预算分配）。七项均为 2026-08-01~08 最新研究，DPitG 为施工算法闭环必需（mSPRT 决断性），ARM/DPitG/Betting on Bets/RLCP/Decaying-ε-FOCuS 为选项之外更好的答案算法 |
| 2026-08-10 | 2.5.0 | 第十六轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08-08 最新研究补充（全网搜索 2026-08 命中）：①§3.3 第 4 条补 **Drift2Act 预算干预框架**（arXiv:2603.08578v1 ICLR 2026 CAO Workshop Lamaakal et al. 2026-03-09，选项之外更好的答案算法+施工算法缺失填补——四层 Drift Observatory 联动编排的分级响应阶梯 alert/reduce/stop/quarantine/retrain 是启发式阈值映射 composite score→response level，阈值依赖经验标定无数学保证，Drift2Act 将漂移监控重构为"带安全约束的决策制定"——sensing layer 检测漂移+active risk certificate 在预算约束下触发干预，online risk certificate Ut(δ)≤τ 低成本动作（重校准/测试时适配）/ Ut(δ)>τ 弃权+回滚+重训练，WILDS Camelyon17/DomainNet 近零安全违反，Phase 3 候选）；②§3.3 第 4 条补 **KDD 2026 漂移检测基准框架**（arXiv:2606.07789 KDD 2026 2026-08-09~13 韩国济州岛，选项之外更好的答案算法——Drift Observatory 涉及 10+ 检测器但缺乏跨数据集可比的标准化评测框架，KDD 2026 首次提供 Monte Carlo drift simulation 向真实数据注入可控分布变化+timing-aware 评估指标 F1 detection score+normalized detection time+leave-one-dataset-out 超参优化协议基准化 14 种主流检测器在 7 真实数据集上表现，与 ProteuS 互补 ProteuS 生成数据 KDD 2026 基准评测检测器，Phase 3 验证候选）；③§3.3 第 4 条补 **Conformal Abstention Layer 空仓决策**（arXiv:2606.11949v3 2026-08-04，选项之外更好的答案算法——分级响应阶梯的 stop new entries/quarantine 是启发式响应，何时从减仓升级到空仓缺乏形式化判据，Conformal Abstention Layer 当模型预测置信度低于 conformal 保证阈值时主动弃权对应量化交易空仓决策，unweighted+weighted-on-alarm 双模式，800 单元析因基准发现检测难度由 classifier×shift 交互主导 η²=0.185+generative embeddings silent failure 须投影≤32 维，Phase 3 候选与 Layer 4 CP 同期评估）；④§3.3 第 1 条补 **Ranking by Lifts 成本收益 FDR**（arXiv:2407.01036v2 Basu&Berman Wharton/ISB，选项之外更好的答案算法——mSPRT 晋升决策只考虑统计显著性 e-value≥20 不考虑财务成本，错误晋升的财务成本被忽略，RBL 基于 lfdr 贪心 knapsack oracle 按"期望 lift/错误切换成本"排序最大化利润同时控制 FDR+财务成本，与 mSPRT 关系 mSPRT 控制 P(false promotion)≤α RBL 控制 E[false promotion cost]≤budget 是成本感知升级，与 SCORE 关系 SCORE 管功率 RBL 管成本正交可组合，Phase 2+ 候选策略数>8 时评估）；⑤§3.3 第 5 条/§3.9 补 **evalinger futility monitoring 事前放弃**（arXiv:2602.06379v1 2026-02-06 对齐 FDA 2026-01 Bayesian 指南草案，选项之外更好的答案算法+施工算法缺失填补——§3.9 退役流程的"触发式移除纪律"是事后退役须等 Decay Detection 持续告警≥10 日才触发，事前 futility monitoring 能在策略尚有微弱 edge 但统计上已无希望恢复时提前放弃，evalinger R 包 betting-martingale e-process 支持复合 null+futility monitoring+platform-trial multiplicity，连续监控下 e-value power 反超 group sequential，与 mSPRT 关系 mSPRT 用 e-process 做晋升检验 H1:Challenger>Champion futility monitoring 用同一 e-process 做反向检验 H0:策略 edge≤0 是同一 e-value 框架在晋升和退役两个方向的应用，<50 行增量复用 mSPRT 基础设施 Phase 2 候选）；⑥§5.1 系统上限同步更新 Drift2Act+KDD 2026 基准+Conformal Abstention+Ranking by Lifts+evalinger futility（Champion-Challenger 行补 RBL+evalinger/漂移检测行补 Drift2Act+Conformal Abstention+KDD 2026）；⑦§8.3 行业实证补充 5 条 2026 来源（Drift2Act arXiv:2603.08578v1/KDD 2026 arXiv:2606.07789/Conformal Abstention arXiv:2606.11949v3/RBL arXiv:2407.01036v2/evalinger arXiv:2602.06379v1） | 施工环节流程算法完整性审查发现 2 处施工缺口+5 处选项之外更好的答案算法：①分级响应阶梯是启发式阈值映射无数学保证（Drift2Act risk certificate 填补"检测→动作"的形式化决策层）；②stop new entries/quarantine 何时升级到空仓缺乏形式化判据（Conformal Abstention Layer 填充覆盖保证→弃权决策映射）。五项选项之外更好的答案算法：①Drift2Act 预算干预框架（online risk certificate 在预算约束下触发干预，ICLR 2026）；②KDD 2026 漂移检测基准框架（14 检测器标准化评测 Monte Carlo simulation+timing-aware 指标）；③Conformal Abstention Layer（conformal coverage→abstain decision 数学保证映射）；④Ranking by Lifts（mSPRT 成本感知升级 lfdr knapsack 最大化利润控制 FDR+财务成本）；⑤evalinger futility monitoring（e-process 反向检验策略退役事前放弃）。七项均为 2026-08 最新研究，Drift2Act/Conformal Abstention 为施工算法闭环必需（漂移检测→动作的形式化决策层），KDD 2026/RBL/evalinger 为选项之外更好的答案算法 |
| 2026-08-10 | 2.6.0 | 第十七轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08 最新研究补充（全网搜索 2026-08 命中）：①§3.3 第 4 条补 **DTD 动态阈值确定**（arXiv:2511.09953v1 AAAI 2026 Lu et al. UTS，选项之外更好的答案算法+施工算法缺失填补——Drift Observatory 四层联动编排的分级响应阶梯用固定阈值 composite 0.20/0.40/0.60/0.80，PSI 固定 0.1/0.25，CUSUM 固定 h=4σ，所有阈值一经标定即固定，DTD 证明动态阈值可证明优于任何单一固定阈值，核心定理：每段最佳阈值组合的动态策略保证不劣于任何跨所有段的单一阈值，在现有检测器上增加比较阶段 comparison phase 检测到漂移后不立即响应用不同阈值在比较窗口评估性能选最优，复杂场景渐变/循环漂移收益更大且对比较阶段时长 K 鲁棒，Phase 3 候选）；②§3.3 第 4 条补 **COP 共形乐观预测**（arXiv:2512.07770v2 2026-02-24 Nankai/Tsinghua，选项之外更好的答案算法——Layer 4 CP 的 ACI/calibration flush/BC-ACI 都在完全对抗环境 fully adversarial 下设计产生过度保守预测区间，当数据存在可预测模式如 A 股季节性/周期性时对抗性方法无法利用这些模式收紧区间，COP 将底层数据模式纳入更新规则通过估计非一致性分数 CDF 在存在可预测模式时产生更紧预测区间估计不准时仍保持覆盖保证，覆盖与遗憾联合界+distribution-free 有限样本覆盖+i.i.d. 收敛，与 ACI/BC-ACI 纯对抗路径互补 COP 是分布知情路径，与 DASC 互补 DASC 管 regime 循环 COP 管可预测模式，Phase 3+ 候选）；③§3.3 第 1 条补 **鲁棒序贯实验设计**（arXiv:2605.12899v1 2026-05-13 Wen/Wu/Shi et al. LSE，选项之外更好的答案算法——mSPRT 高斯 mixture 闭式解假设收益差服从高斯但 A 股收益有重尾特性超额峰度>20 高斯假设可能失效模型误设下 Type I 控制可能退化，鲁棒序贯实验设计在模型误设下研究 A/B 测试序贯设计统一覆盖 contextual bandit 和动态设置证明界定处理效应估计的最坏情况均方误差 worst-case MSE，与 mSPRT 关系 mSPRT 假设高斯 mixture 参数化鲁棒序贯设计在最小假设下工作非参数化后者在前者分布假设失效时提供安全网，与 CUSUM 重尾缓解 winsorize 预处理互补 winsorize 管预处理鲁棒序贯设计管检验框架，Phase 3 候选 winsorize 后仍重尾或 mSPRT 误设退化时评估）；④§5.1 系统上限同步更新 DTD+COP+鲁棒序贯实验设计；⑤§8.3 行业实证补充 3 条 2026 来源（DTD arXiv:2511.09953v1/COP arXiv:2512.07770v2/Robust Sequential Design arXiv:2605.12899v1） | 施工环节流程算法完整性审查发现 1 处施工缺口+3 处选项之外更好的答案算法：①Drift Observatory 全部检测器用固定阈值——DTD 证明动态阈值可证明优于任何单一固定阈值，比较阶段 wrapper 是 Phase 3 自适应升级路径（AAAI 2026）。三项选项之外更好的答案算法：①DTD 固定阈值→自适应阈值（comparison phase 性能驱动选阈值）；②COP 对抗性 CP→分布知情 CP（CDF 估计利用可预测模式收紧区间）；③鲁棒序贯设计 mSPRT 模型误设安全网（worst-case MSE 界）。四项均为 2026-08 最新研究，DTD 为施工算法闭环必需（固定阈值是 Drift Observatory 全栈的共性盲点），COP/鲁棒序贯设计为 Layer 4 CP/mSPRT 的精度与鲁棒性升级 |
| 2026-08-10 | 2.7.0 | 第十八轮审查施工环节流程算法完整性+选项之外更好的答案算法+2026-08 最新研究补充（全网搜索 2026-08-08~10 命中，arXiv 周末停发最新停在 08-07）：①§3.3 第 4 条补 **Conditional CTM 污染修复**（arXiv:2602.13848v2 Shaer et al. ICML 2026 2026-06-12，施工算法缺失填补——BettingMartingaleCoverageMonitor 的覆盖指示 Z_t=1[Y_t∈Ĉ(X_t)] 依赖预测区间 Ĉ(X_t)，而 Layer 4 的 ACI/BC-ACI/calibration flush 用历史 Z_s 自适应更新 Ĉ 形成反馈环——ACI 在 miss 后加宽区间→下一个 Z_t 更可能为 1→鞅误判覆盖良好即使真实条件覆盖已失效，这是 test-time contamination 用自适应区间产生的覆盖指示检验自适应区间的覆盖保证是循环论证 anytime-valid Type I 控制在 contamination 下可能退化，CTM 用固定参考集 frozen calibration set 非自适应校准集计算非一致性分数构造 test martingale+鲁棒 betting function 显式建模有限参考集估计误差，三项保证 anytime Type I+power-one+有界检测延迟，与现有 betting martingale 关系 朴素版 vs 去污染版不改检测目标只改分数来源，与 mSPRT 对比 mSPRT 用两路独立 PnL 无 contamination betting martingale 用单路自反馈有 contamination CTM 让两者都 contamination-free，Phase 3 与 Layer 4 CP+betting martingale 同期落地 ~30-40 行增量）；②§3.3 第 4 条补 **Legendre Jumper Martingales 高阶矩漂移检测**（arXiv:2606.20859v2 Szabadváry 2026-07-12，选项之外更好的答案算法——BettingMartingaleCoverageMonitor 检测一阶矩漂移 E[Z_t] 偏离 1-α 即覆盖率漂移，但金融数据还有高阶矩漂移方差漂移波动率 regime 切换 A 股最常见/偏度漂移尾部风险结构变化/峰度漂移重尾程度变化，一阶矩不变的方差漂移会让 betting martingale 完全失明，Legendre Jumper 用移位 Legendre 多项式作 betting function 将 Simple Jumper 扩展到高阶矩 k 阶多项式对应检测第 k 阶矩漂移 k=1 均值/k=2 方差/k=3 偏度，Variational Legendre Jumper 常数时间更新 O(1)，与 betting martingale 正交互补 k=1 覆盖率 vs k≥2 方差/偏度，对量化交易特殊意义 A 股方差漂移=波动率 regime 切换是五骑士 ② Regime 28% 第二大根因 k=2 阶可检测波动率 regime 切换但收益均值未变的早期漂移，与 10 号 regime 检测器互补 HMM 离散态分类 vs Legendre 连续方差漂移检测，Phase 3 候选 ~40-50 行增量）；③§3.3 第 4 条补 **Subgroup Under-Coverage Auditing 子组欠覆盖审计**（arXiv:2608.04254 2026-08-06，选项之外更好的答案算法+施工算法缺失填补——Layer 4 Conformal Prediction 保证边际覆盖 P(Y∈Ĉ)≥1-α 全样本平均，但特定子组如高波动率 regime/特定行业/小盘股池可能静默欠覆盖边际覆盖 90% 持平但高波动率子组实际覆盖仅 70%，BC-ACI 纠正全局偏置无法发现子组级欠覆盖全局平均掩盖局部失效，conformal.marketmaker.cc 180 实验已证 GARCH 三分位条件覆盖 0.952/0.915/0.820 高波动区低估 8 个百分点，Subgroup Auditing 提供有限样本保证的子组欠覆盖审计在预定义子组上检测实际覆盖是否显著低于名义水平控制审计本身 FWER，与 RLCP 关系 RLCP Phase 4 是修复条件覆盖 Subgroup Auditing 是诊断条件覆盖失效诊断→修复链路 Phase 3 先部署检测哪些子组欠覆盖 Phase 4 RLCP 针对性局部化校准，与 ARM 关系 ARM 归因哪些维度变了漂移归因 vs Subgroup 审计哪些子组覆盖失效覆盖归因正交，Phase 3 诊断候选 ~100-150 行增量是 RLCP 前置诊断）；④§5.1 系统上限同步更新 Conditional CTM+Legendre Jumper+Subgroup Auditing（漂移检测行补 3 项）；⑤§8.3 行业实证补充 3 条 2026 来源（CTM arXiv:2602.13848/Legendre Jumper arXiv:2606.20859/Subgroup Auditing arXiv:2608.04254） | 施工环节流程算法完整性审查发现 2 处施工缺口+2 处选项之外更好的答案算法：①BettingMartingaleCoverageMonitor 的覆盖指示依赖自适应更新的预测区间形成 test-time contamination 反馈环——用自适应区间产生的覆盖指示检验自适应区间的覆盖保证是循环论证，anytime-valid Type I 控制在 contamination 下可能退化（CTM 固定参考集去污染填补，ICML 2026）；②Layer 4 边际覆盖掩盖子组静默欠覆盖——全局 90% 覆盖但高波动率子组实际 70%，BC-ACI 全局偏置纠正无法发现子组级失效（Subgroup Auditing 有限样本子组审计填补，2026-08-06）。两项选项之外更好的答案算法：①Conditional CTM 是 betting martingale 的有效性升级（自适应 Z_t→固定参考集 Z_t，统计有效性必要补强非可选优化）；②Legendre Jumper 是 betting martingale 的一阶矩→高阶矩扩展（k=2 检测方差/波动率 regime 切换，A 股波动率 regime 切换是五骑士第二大根因 28% 的刚需）。2026-08-08~10 全网搜索确认：arXiv 周末停发最新停在 08-07，CTM 仍是修复 test-time contamination 的 SOTA 无直接击败者，DTD 仍是动态阈值 SOTA 无直接竞品，Legendre Jumper 是 CTM 在高阶矩漂移检测上的互补非替代。四项均为 2026-08 最新研究，Conditional CTM/Subgroup Auditing 为施工算法闭环必需（betting martingale 统计有效性+Layer 4 条件覆盖静默盲区），Legendre Jumper 为 A 股波动率 regime 切换的刚需检测 |
| 2026-08-10 | 2.8.0 | 第十九轮审查施工环节流程算法完整性+悬空 helper 补全：①§3.3 第 4 条补 **downstream_impact_gate 施工伪代码**（Layer 1 特征漂移的下游影响门控——四步检查 regime 解释+IC 衰减+Sharpe 退化+残差膨胀，复合判定"regime 可解释 AND IC/Sharpe/残差均无退化=良性漂移降级，否则保留告警"，IC 阈值 0.05/Sharpe 阈值 0.7/残差阈值 1.3 与 §3.3 第 5 条 Decay Detection + §3.3 第 7 条回滚阈值对齐非独立标定，与 SHAP Drift Attribution/ARM 变点归因在"是否漂移→哪些维度→业务影响"链路分工，施工算法缺失填补——drift_observatory_orchestrate L200 调用 downstream_impact_gate(l1) 悬空 helper 无定义则四层 Drift Observatory 编排逻辑无法闭环执行，与 54 号 v1.13.0 补全 get_sector/current_session_id/aggregate 同类跨文档悬空 helper 缺口）；②§3.3 第 4 条补 **trigger_retraining 施工伪代码**（重训练触发分级逻辑——三触发策略定时/性能/数据量+分级决策突发漂移 composite≥0.80/coverage_breach 全量重训练 vs 渐进/定时/数据量增量重训练+回滚保险 SBS 纪律对比基线维护态 Champion+晋升门禁 §3.3 第 9 条 OOS Sharpe≥Champion×0.9/profit factor>1.5/MaxDD≤Champion×1.2/子周期一致性/Sortino+Calmar 三角验证，Phase 3 渐进漂移可升级 knowledge distillation 比全量重训练成本低 5-10x，施工算法缺失填补——drift_observatory_orchestrate L216 调用 trigger_retraining(strategy_id) 悬空 helper 无定义则 RETRAIN 响应无法执行）；③两个函数复用 drift_observatory/ic_tracker/performance_tracker/loss_tracker/regime_detector/training_pipeline/mlflow/promotion_gate/rollback_manager 现有组件无新基础设施符合 MVP 分批原则 | 施工环节流程算法完整性审查发现 2 处悬空 helper 缺口：①downstream_impact_gate 在 drift_observatory_orchestrate L200 被调用但无定义——Layer 1 特征漂移的下游影响门控是"statistical significance ≠ business significance"纪律（llmops.report 2026-04-27）的落地，缺失则所有统计显著的特征漂移都告警导致告警疲劳；②trigger_retraining 在 drift_observatory_orchestrate L216 被调用但无定义——重训练触发是 §3.3 第 8 条三策略（定时/性能/数据量）的落地，缺失则 RETRAIN 响应无法执行。两个悬空 helper 与 54 号 v1.13.0 补全的 get_sector/current_session_id/aggregate 同属跨文档悬空 helper 缺口，drift_observatory_orchestrate + BettingMartingaleCoverageMonitor 均已有施工伪代码仅剩这两个未落地则四层 Drift Observatory 编排逻辑无法闭环执行。两项均为施工算法闭环必需 |
| 2026-08-10 | 2.9.0 | 第二十轮审查文档结构/顺序/内容+2026-08 最新研究补充（全网搜索 2026-08 命中）：①§3.2 LLM alpha 挖掘远期候选补 **AlphaCrafter 全栈多 Agent 框架**（arXiv:2605.05580，Miner Agent 因子挖掘+周期复验剪枝 / Screener Agent regime-conditioned 因子集成 / Trader Agent 策略构造执行 三 Agent 闭环，动态因子管理对抗 alpha decay 优于静态因子集，与 QuantaAlpha 单一 Miner 环节区别是全栈闭环，与 30 号"LLM 多 Agent 辩论暂缓"约束冲突最直接记为 Phase 5+ 远期候选）；②§3.2 补 **FactorMiner 自进化 Agent + Ralph Loop**（arXiv:2602.14670 Tsinghua，Modular Skill Architecture 可执行评估工具 + Experience Memory 成功模式+失败约束 + Ralph Loop retrieve→generate→evaluate→distill，110 因子全 A 股因子库低冗余实证，与 AlphaAgent AST 相似度正交——AST 事中过滤 vs Memory 事前引导，**FactorMiner Experience Memory 与本项目的轻量契合点**：经验沉淀思想可脱离 LLM 独立实现，本项目因子孵化 §3.2 已有"假设驱动+证据挂载"状态机，Experience Memory 是该状态机的"跨假设经验累积"层，Phase 3 候选因子库 >20 时将已验证假设的成功/失败模式结构化为可检索 memory 辅助人工因子研究 <100 行代码无需 LLM）；③§3.2 本项目定位从"三篇"升级为"五篇"，评估优先级更新为 AlphaSchema > FactorMiner > AlphaCrafter > XALPHA > EFS（FactorMiner 的 Ralph Loop+Experience Memory 最轻量可先实现评估工具辅助人工）；④§8.3 行业实证补充 2 条 2026 来源（AlphaCrafter arXiv:2605.05580 / FactorMiner arXiv:2602.14670） | 2026-08-10 全网搜索发现 §3.2 LLM alpha 挖掘远期候选列表缺 AlphaCrafter 和 FactorMiner 两篇 2026 最新研究：①AlphaCrafter 是唯一覆盖"因子挖掘→regime 适配→策略执行"全链路的三 Agent 闭环框架（QuantaAlpha/EvoQuant/QuantEvolver/AlphaSchema/XALPHA/EFS 均只覆盖其中一环），缺失则远期候选评估无全栈闭环参照；②FactorMiner 的 Ralph Loop+Experience Memory 是唯一"经验沉淀"范式（其他均为"生成-评估"范式无跨试验经验累积），且其 Experience Memory 可脱离 LLM 独立实现（<100 行代码）与本项目 §3.2 假设驱动状态机天然契合是 Phase 3 可施工的轻量增强。两项均为 2026 最新 LLM alpha 挖掘研究，AlphaCrafter 为全栈闭环参照，FactorMiner 为经验沉淀范式+Phase 3 轻量契合点 |
| 2026-08-10 | 2.10.0 | 第二十一轮审查施工算法完整性+2026-08 最新研究补充（全网搜索 2026-05 命中）：①§3.2 LLM alpha 挖掘远期候选补 **AlphaMemo 结构化搜索过程记忆的自进化 alpha 挖掘 agent**（[arXiv:2606.20625](https://arxiv.org/abs/2606.20625), Yu et al. 2026-05-26, University of Sydney + University of Edinburgh）——4 大组件（Parent-Edit Action Space 父代邻域编辑动作空间 / Structured Search-Process Memory 残差过程记忆教师修正 / AST-diff Edit Motifs 编辑模体 / Asymmetric Process Veto 不对称过程否决），核心创新是记忆整个搜索过程（含残差/决策/AST 差异）非仅结果，关键洞见"过程记忆 > 结果记忆"+"失败否决不对称性"；②§3.2 六组件统一框架映射补 AlphaMemo=Memory+Selection+Variation（强化 Memory 维度——过程级记忆是 Memory 组件范式升级），关键洞见 1 更新 Memory 维度覆盖从 FactorMiner+EvoQuant 扩展到含 AlphaMemo 三者；③§3.2 本项目定位评估优先级补 AlphaMemo（AlphaSchema > FactorMiner > AlphaMemo > Hubble > ...），补 AlphaMemo APV 轻量契合点（失败否决不对称性可脱离 LLM 独立实现 Phase 3 候选 <80 行代码，与 FactorMiner Experience Memory 正交可叠加）；④§8.3 行业实证补充 AlphaMemo arXiv:2606.20625 | 2026-08-10 全网搜索发现 §3.2 LLM alpha 挖掘远期候选缺 AlphaMemo（arXiv:2606.20625 2026-05-26）——AlphaMemo 的结构化搜索过程记忆是唯一显式建模"过程级 Memory"的候选（FactorMiner 记忆语义级经验洞见，EvoQuant 蒸馏经验，AlphaMemo 记忆完整搜索过程含残差/决策/AST 差异），且其 APV 不对称否决可脱离 LLM 独立实现（Phase 3 候选 <80 行代码），与 FactorMiner Experience Memory 正交可叠加（FactorMiner 记忆"什么方向有前景"，AlphaMemo 记忆"什么编辑模式会失败"）。AlphaMemo 为 2026-05 最新 LLM alpha 挖掘研究，填补六组件框架 Memory 维度的过程级记忆空白 |
| 2026-08-12 | 2.11.0 | 第二十二轮审查（幻觉引用清除 + 已施工设施盘点 + 版本漂移修复）：①**幻觉引用修正**——git log 实证 52/55 号从未离开 draft v0.1.0 骨架，但 v2.10.0 前 §3.4/§8.1 引用其"IS→WFA→OOS 门控 + 7-gate 审计 v1.7.3 / active v1.13.0"为虚构（00_index v2.5.0 批量同步错标 52-55 号 active 导致连环幻觉）：§3.4 承接行+核心纪律①②改为 battle_map_03 + 代码真源 `backtest/core/decision_gate.py`；§8.1 52/55 号条目改骨架待讨论标注；§3.3 双曲线段/容量段 2 处"55 号协同"补骨架标注；§3.9 退役流程 2 处 55 号联动补骨架标注并明确"退役量化标准当前由本备忘 §3.9 承载"；②**版本漂移修复**——53 号 v1.6.3→v1.7.0 / 24 号 v1.5.0→v1.9.7 / 54 号 v1.13.0→v1.14.0（body，修订记录历史不动）；③**新增 §2.4 已施工设施盘点**（通用规则 #11——14 行设施表：paper_live_transition / decision_gate / deflated_sharpe / look_ahead_bias_detector / experiment_tracking / 系统级 lifecycle_manager（⚠️澄清：进程级启动关闭≠策略生命周期）/ D-SIGNAL-14（设计态无代码）/ depgraph 脚本链 / 治理注册表 / strategy_archive（设计态未建）/ 多 AI 交接载体 / 漂移检测（伪代码待施工）/ simulation 域 / 53 号）；④§3.1 D-SIGNAL-14 补 battle_map_12 真源链接+无独立代码标注；⑤§3.8 三脚本补稳定路径；⑥§3.9 归档四件套④补 strategy_archive/ 设计态标注；⑦§2.1/§3.7 "38 篇"计数去漂移化（指向 00_index §0 台账）；⑧新增 §7.4 开放问题（00_index 四处漂移登记 + 52/55 骨架联动，不越界改）；⑨§8.1 补 battle_map_12 条目 | 通用规则 #11 已施工设施盘点 + 交叉引用实证审查：git log 证明 52/55 号从未有 active 版本（v1.7.3/v1.13.0 均为 00_index 错标后的连环幻觉）；代码核查确认 strategy_archive/ 未建、trading/lifecycle_manager.py 为系统进程级非策略级。⚠️施工备注：本次修订期间检测到并发会话（arch-review-g10-g06）worktree 操作导致工作区多次回滚，采用批量替换+立即提交固化 |
| 2026-08-12 | 2.12.0 | 第二十三轮审查（缺失环节补齐）：①§3.6 交接纪律补第 5 条**并发文件级冲突纪律**（2026-08-12 实战教训：多会话并发共享主工作区 git index，未落分支的修改随时被并发会话 stash/reset 抹掉——本次审查过程中工作区修改被多次回滚实证；强制 `git_commit.py --claim-only` 前移声明 + GitCommitGateway 唯一 commit 入口 + `session_worktree.py` 物理隔离，#ARCH-WORKTREE-GATE-001）；②§3.2 补**策略规格产出物**承接（§3.1 ①孵化阶段退出条件"策略规格产出"原无承接定义，补 20 号 G04 首批范式：sleeve 定位/容量测算/持仓周期/风控参数四要素齐备方可进入 ② 训练阶段） | 第 3 轮缺失环节审查发现：①多 AI 协作交接纪律缺"并发文件级冲突"处置——治理设施（git_commit.py claim 协议 / session_worktree）已存在但本备忘 §3.6 未登记，AI 会话不知情则修改必丢；②孵化→训练准入的"策略规格产出"缺承接定义。53 号 v1.7.1 同步精简正文过渡文本（修改原则合规） |
| 2026-08-12 | 2.12.1 | 第二十四轮审查（2026-08 最新研究搜索整合）：①§3.6 第 5 条补**行业背书**——CMU CAID（arXiv:2603.21489，2026-03）实证 branch-and-merge+git worktree 是多 agent 协作核心协调机制（PaperBench +26.7%/Commit0 +14.3%）；VS Code 2026-08-07 起 Copilot/Claude/Codex agent session 默认 git worktree 隔离（luonghongthuan 2026-08-10），"并发 agent 未提交修改被静默覆盖"为 2026-08 行业公认失败模式；②§8.3 补 CAID + VS Code worktree 2 条来源；③53 号侧 2026-08 搜索（paper→live 迁移 + canary deployment）确认现有三阶段+5 级 ramp+key_gates 与最新实践（x3algo/algovantis/futureagi 四阶段 gate/theneuralbase gradual rollout/metricgate shadow-canary 方差分析）一致，零新增内容需求 | 第 4 轮 2026-08 最新研究全网搜索：multi-AI collaboration 方向命中 CAID（CMU 学术实证）+ VS Code 官方 worktree 隔离（2026-08-07 上线）双重背书本备忘 §3.6 第 5 条；paper trading/canary deployment 方向确认 53 号现有设计与行业 SOTA 一致无缺口 |
| 2026-08-12 | 2.12.2 | 第 5/6 轮审查（过度工程零发现 + 一致性去版本化）：①**过度工程审查零发现**——多 AI 协作规范（§3.6 五条均为已有治理设施的使用纪律非新建重型机制，§4.1 已拒绝 agent 编排）/ BM-RES+BM-MOD 规范（MVP 部分为 MLOps Level 2 行业标准最小集，20+ arXiv 重型候选全部标 Phase 2-5 远期不施工）/ 53 号三阶段灰度（比 nexusfi 7 阶段精简且有 paper_live_transition.py 代码承载，§5.3 已论证）/ 实盘差异监控（key_gates 8 维度为已定义代码门禁，日频滚动计算单机可承受）——全部符合硬边界约束，远期项标注合规不删；②**一致性去版本化**——body 中对 53 号（§2.4/§3.5/§8.1）/24 号（§3.9）/54 号（§3.3）的版本号引用全部去除（引文档用稳定 path 不带版本，修订记录保留历史版本），消除连环漂移源；③53 号与 01 号 §2.2/battle_map_01（33 环节 17 锚点）/battle_map_02（14 环节 10 锚点）/20 号 §4.4 四阶段交叉复核一致 | 第 5 轮过度工程审查对照 system_charter §2 硬边界逐项判定零发现（单 AI 多会话+单机 PC+小资金+T+1 约束下无超界机制）；第 6 轮一致性审查发现版本号引用是连环漂移源（53 号升版即致 61 号引用滞后），按 01 号规范"交叉引用全用稳定 path"去版本化 |
| 2026-08-12 | 2.13.0 | 作战地图全覆盖补丁——研究知识流水线拍板+研究环境否定式裁定+运行时风险治理小节（BM-RES-01-C/03-B/04/05/06/07/08/09/11 关联、BM-MT-01-B/C、BM-RC-09/04-F）：①§3.2 新增**研究知识流水线拍板**（BM-RES-03-B 研究发现知识库/BM-RES-08+08-A 知识清洗/BM-RES-09+09-A 知识分类——轻量方案 Markdown+Git+frontmatter 标签检索，闭合 §7.2 登记的缺失态待定问题）；②§3.2 新增**研究环境否定式裁定**（BM-RES-01-C 不建容器沙箱=venv/目录隔离+65 号 §9 呼应 / BM-RES-05-A 不建 JupyterLab+papermill / BM-RES-04+04-A 不建 Prefect 编排=人工串联+64 号 §6.4 APScheduler 调度基座复用 / BM-RES-06-B 论文追踪 Phase 3 远期候选，interim=90/91 号人工文献整合）；③§3.2 补 BM-RES-06-A/07-A 定位句（Phase 5+ 重评已写明确认无需动作 / 当前=人工+假设状态机+62 §4.12 ADAPT_STRATEGY，FactorMiner/AlphaMemo Phase 3 轻量契合点）；④§3.3 新增**模型训练两环节裁定**（BM-MT-01-B 生成-反馈闭环并入 §3.2 远期候选+62 §4.34② llm_safety_stack 5 字段安全栈已落地+battle_map 成熟度标注倒挂真源修正建议登记 §7.5 / BM-MT-01-C 策略数字孪生裁定不做镜像副本=§3.9 退役 8 维+Drift Observatory 承载，与 #ARCH-OE-010 边界消歧）；⑤§3.6 新增**运行时风险治理小节**（BM-RC-09 有界自治边界白名单+额度/治理漂移防护规则版本锁定+变更审计/ARS 双轨结算裁定，与 35 §2.4 VR-009 AI 自治熔断器上/下游关系 / BM-RC-04-F Agent 行为基线+异常告警/OWASP Agentic Top10 映射检查表/55 号告警通道衔接）；⑥§6 待裁定表 BM-RES 缺失态行标记已解决；⑦§7.2 标记已解决+新增 §7.5（BM-MT-01-B 成熟度倒挂登记）；⑧§8.1 补 62/64/65/90/91 号引用 | 作战地图 16 个环节（研究孵化域 12 + 模型训练域 2 + 风控域 2）在 61 号 why 层无定位/裁定/契约记录——研究孵化域 7 缺失态环节（BM-INV-001 违例）是最大空白，本次按"轻量拍板+否定式裁定+远期登记"三模式一次闭合；AI 风险治理两环节（BM-RC-09/04-F）随多会话 AI 开发模式实战化（§3.6 第 5 条并发冲突纪律落地后）需运行时护栏配套 |
| 2026-08-12 | 2.13.1 | 作战地图环节映射补强——锚定 BM-RES-03-A、BM-RES-10-A | §3.2 末尾补映射块，环节级可追溯 |
