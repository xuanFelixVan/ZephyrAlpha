---
ttl: permanent
doc_type: architecture_view
title: 策略生命周期与多 AI 协作
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.13.3"
date: 2026-08-15
topic: lifecycle_multi_ai
scope: 07_trading_decision_architecture
---

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**（机制落地状态——本篇为治理/生命周期规范文档，无单一施工批次归属）：①多 AI 协作交接纪律与并发文件级冲突纪律已落地运营——GitCommitGateway 唯一提交入口 + session_worktree 物理隔离 + lock_files 文件锁 + claim 前移声明全链路 production（65/66 号基建承载）；②模块创建 4 步（creation_token + capability/translation/ARCH 登记）为现行治理常态；③§3.9 退役判据量化标准的执行体已由 55 号 AI-MON-001 落码（`governance/lifecycle_governance/strategy_retirement_evaluator.py`，五判据+评审制铁律，四条阈值已转正 active）；④BM-RES 研究知识流水线拍板（轻量 Markdown+Git+frontmatter）与研究环境否定式裁定（不建沙箱/编排/Notebook）已闭合，无代码承诺遗留。
>
> **最终成果**（2026-08-19 代码实证）：生命周期 6 阶段框架以 design_memo status + depgraph build_status 双字段运营（§4.3 简化方案，无独立状态机服务）；退役判据执行体在位；mSPRT / Drift Observatory 四层编排 / 退役 5 步工作流 / strategy_archive/ 目录在 src 全仓零命中——均为设计规范伪代码未落码，与 §2.4 盘点"⚠️设计规范伪代码，代码待施工"自评一致。⚠️ 复核发现跨文档漂移：本篇以 MLflow alias（@champion/@challenger/@archived）为晋升/回滚/归档载体（§3.3 纪律 1/2/7/9、§3.9 归档四件套），但 51 号已裁定完全卸载 MLflow（2026-08-16，src 零命中实证）——落地载体需重裁定（experiment_tracking FallbackBackend 或注册表状态机等价物），不影响本篇裁定的语义有效性，但伪代码不可按 MLflow 直读施工。
>
> **未做事项及原因**：
> - Champion-Challenger mSPRT 晋升通道（§3.3 纪律 1 伪代码）——未施工；且因 MLflow 退役，落地形态需先重裁定载体；54 号 §6 亦标注其阻塞 BM-REC-02-B 绩效归因。裁定=未来工程-大型（需载体裁定+统计组件施工）。
> - Drift Observatory 四层编排（§3.3 纪律 4 编排伪代码）——未施工；首批策略未上线无消费方，设计内延期。裁定=未来工程-大型（随首批上线后监控批）。
> - 退役 5 步工作流（§3.9 伪代码）——未施工；判据执行体已由 55 号承载，工作流编排待首个退役策略触发。裁定=未来工程-小型。
> - strategy_archive/ 目录（§3.9 归档四件套第④条）——未建；待首个退役策略触发即建，设计内延期。裁定=未来工程-小型。
> - BM-MT-02-A/B 灰度+影子部署+对抗鲁棒性——未施工（设计态）；随策略上线 MLOps Level 2 批。裁定=未来工程-大型。
> - AI 行为基线+异常告警（BM-RC-04-F，§3.6）——未施工；白名单/额度已由 wrapper/git_guard/Gateway 部分承载，行为统计告警为增量。裁定=未来工程-小型。
> - 冷启动 T0/T1/T2 渐进建仓（§3.1）——设计态；随首批策略上线由 53 号迁移路径承载。裁定=未来工程-小型。
> - LLM 驱动 alpha 挖掘远期候选（§3.2 登记表）/独立 Lifecycle Manager 服务（§4.3）/KFP-KServe-K8s（§4.2）/多 Agent 编排（§4.1）——本篇已逐项裁定 Phase 5+/暂缓/拒绝，不施工；裁定=过度工程（当前阶段）。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原"退役工作流/归档/行为基线未施工"已大面积过时：governance/lifecycle_governance/ 下 strategy_retirement_evaluator.py+retirement_workflow.py（退役 5 步工作流）+strategy_archive.py（归档四件套）+ai_behavior_baseline.py（BM-RC-04-F）全部 production；pf_core/core/msprt_champion_challenger.py（MOD-PF-008 统计内核，design 态）在库。
> **仍真实未完工**：Drift Observatory 四层编排零命中（设计内延期）；mSPRT 晋升编排层/消费方未建（内核在库）；BM-MT-02-A/B 灰度+影子部署未施工。

> ## 结案报告回填（2026-08-30 载体重裁定闭环，ARCH-298）
> **mSPRT 晋升编排层载体重裁定已正式闭环（ARCH-298）**：MLflow 退役后载体归宿 = 因子生命周期状态机 MOD-L02-013（注册表状态机等价物），替代原 §3.3 纪律 1/2/7/9 与 §3.9 的 MLflow alias（@champion/@challenger/@archived）。语义不变——mSPRT 序贯晋升判定逻辑不受载体切换影响，仅物理执行层由 alias 换为 FSM 状态转换。三件套已在库 production：统计内核 msprt_champion_challenger.py（MOD-PF-008）+ 晋升编排层 msprt_promotion_channel.py + 因子消费方 factor_promotion_wiring.py（2026-08-24 ARCH-210 落地，因子侧以 MOD-L02-013 为等价载体、仅终局裁决产 FSM 副作用）。**上条 2026-08-28 回填中"mSPRT 晋升编排层/消费方未建"自此作废**。残余阻塞：ExecutionReport delta 产出逻辑（CTR-P1-007）未施工，delta 当前为合成/外部源——54号文 BM-REC-02-B 绩效归因待其解锁。仍真实未完工收敛为：Drift Observatory 四层编排（设计内延期）+ BM-MT-02-A/B 灰度影子部署 + CTR-P1-007 delta 产出。

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
- 00_index 已建立段位编号制（0x-9x）与骨架先行工作流（最新篇数与状态台账以 [00_index_trading_decision](00_index_trading_decision.md) §0 目录为准），需在本备忘锁定生命周期各阶段的文档治理衔接
### 2.2 核心问题
- 生命周期 6 阶段跨作战地图，缺跨阶段总纲串成状态机
- 多 AI 协作缺分工与交接纪律——"AI 间不直接通信"原则下须防交接断裂
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

**渐进建仓节奏细化**：冷启动不是一次性给 30% 然后跳到 100%，而是按**时间+表现双门控**阶梯式放量（[youngju.dev 2026-03](https://www.youngju.dev/blog/ai-platform/2026-03-04-ai-platform-model-registry-ab-deploy-2026)：渐进流量梯度；[kindatechnical 2026-03](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)：post-deployment monitoring）：

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

**研究知识流水线拍板**（一次拍板闭合 §7.2 登记的 BM-RES-03/08/09 缺失态待定问题）：

1. **BM-RES-03-B 研究发现知识库**（design）→ **轻量建设：Markdown+Git+frontmatter 标签检索**。定位：假设被接受/研究发现产出后的知识沉淀环节（下游 D-KNOWLEDGE）。裁定：不上 SQLite/Neo4j/ChromaDB 独立知识库——个人项目知识条目量级（数十至数百条）用 Markdown + Git 版本化 + frontmatter 标签检索足够；向量检索属过度工程，重评条件：知识条目 >500 且关键词检索失效。契约：知识条目单文件 Markdown 存于研究知识目录，frontmatter 四字段必填——`hypothesis`（假设陈述）/ `evidence`（证据列表）/ `conclusion`（接受/拒绝+理由）/ `tags`（关联因子/策略标签，对接 §3.2 第 2 条假设状态机）；条目生命周期随假设状态机流转。
2. **BM-RES-08 知识清洗与结构化 + BM-RES-08-A 知识清洗流水线**（design）→ **轻量建设：LLM 单次抽取 + Markdown 结构化模板承载**。定位：原始研究材料→清洗→结构化→沉淀 BM-RES-03 假设。裁定：不上独立 NLP 清洗栈；清洗四动作（去重/去噪/实体链接/质量评分）由"LLM 单次抽取 + Markdown 模板"承载，人工复核后入库；重评条件：日采集量 >50 篇且人工复核成为瓶颈。契约：模板字段——`source`（来源+时间+置信度）/ `dedup_key`（标题哈希，承载去重）/ `entities`（实体链接标签）/ `quality_score`（LLM 自评 1-5 + 人工复核标记）；去重=标题哈希比对，去噪=quality_score <3 不入库，与 BM-RES-03-B 共用 frontmatter 规范。
3. **BM-RES-09 知识分类与策略提取 + BM-RES-09-A 知识类型分类体系**（design）→ **轻量建设：frontmatter 标签承载 5 类知识**。定位：结构化知识→按类型分类→策略提取→BM-RES-07 策略迭代。裁定：知识类型分类体系（事实型/规则型/策略型/案例型/元知识型）由 frontmatter `knowledge_type` 单字段承载，不建独立分类模型；策略提取=人工阅读 `knowledge_type=strategy` 条目后走 §3.2 第 2 条假设登记进入状态机。重评条件：知识条目 >500 且人工分类不一致。契约：`knowledge_type` 枚举 `fact/rule/strategy/case/meta` 必填；策略提取产出物=假设登记条目。

**研究环境否定式裁定**（否定式裁定闭合 4 个 BM-RES 环境/编排环节）：

1. **BM-RES-01-C 研究数据沙箱**（design）→ **裁定不建设容器沙箱**。裁定：研究隔离 = venv/目录级隔离 + 审计日志——与 [65_git_safety_governance](65_git_safety_governance.md) §9"不引入沙箱/容器隔离"裁定呼应（Windows 无 macOS Seatbelt 等效物，Docker/WSL 对量化交易开发过重）；venv 依赖隔离 + 研究目录与生产目录物理分离 + Git 审计日志已覆盖"数据隔离+代码隔离"诉求；资源隔离无需求（单机错峰人工调度）。重评条件：引入不可信第三方代码/数据需隔离执行时。
2. **BM-RES-05-A Notebook 集成与一键转生产**（design）→ **裁定不建设**。裁定：研究环境 = VSCode + 纯 Python 脚本，不建 JupyterLab/papermill——AI 会话直接产出 .py 脚本，"一键转生产"诉求由 §3.8 模块创建 4 步承载，脚本即生产形态无需转换层。BM-RES-05 父环节协作侧由 §3.6 多 AI 协作分工承载，notebook_backend/collaboration_mode 参数随之消解。重评条件：无（除非研究模式转向交互式探索驱动）。
3. **BM-RES-04 研究工作流编排 + BM-RES-04-A DAG 编排与任务调度**（production/design）→ **裁定不建 Prefect 级编排**。裁定：研究工作流 = 人工串联 + [64_data_source_download_spec](64_data_source_download_spec.md) §6.4 调度基座复用——APScheduler 常驻进程 + task_queue DAG 依赖管理 + 指数退避重试 + 降级告警已是 production，研究侧定时任务直接复用该基座登记新 DAG 节点即可，不另建 Prefect/Airflow 级编排（拒绝理由同 §4.2：个人项目无 K8s 运维能力）。重评条件：研究工作流 >10 节点且人工串联成为瓶颈。
4. **BM-RES-06-B 论文追踪**（design）→ **远期候选登记**。裁定：arXiv 爬取 + 标题/DOI 去重 + LLM 摘要的轻量版 <200 行可标 Phase 3 立项（复用 64 号 §6.4 APScheduler 调度基座 + BM-RES-08 清洗模板）；当前 interim 载体 = [90_methodology_open_questions](90_methodology_open_questions.md)/[91_density_prediction](91_density_prediction.md) 的人工文献整合实践（18 轮 arXiv 审查已产出 20+ 候选登记，人工检索+LLM 精读模式已运转有效，无自动化爬取刚需）。重评条件：Phase 3 且周新增相关论文 >20 篇人工精读成为瓶颈。

**BM-RES-06-A LLM 研究助手**（design）：Phase 5+ 重评条件本节"LLM 驱动 alpha 挖掘远期候选"已写明（因子库扩张 + LLM 能力成熟后评估，§2.3"不做 agent 编排系统"约束），确认无需动作。

**BM-RES-07-A 策略进化与因子挖掘**（design）：当前承载 = 人工 + §3.2 第 2 条假设状态机 + [62_business_registry_construction](62_business_registry_construction.md) §4.12 ADAPT_STRATEGY 衰减后适应算法（归因回流→权重调整→升级方案需审批）；FactorMiner Experience Memory 与 AlphaMemo APV 为 Phase 3 轻量契合点（可脱离 LLM 独立实现，<100 行，见本节远期候选登记）；LLM 化（CogAlpha/Hubble 式自主挖掘）为 Phase 5+ 远期候选，与 §2.3 约束一致不立即施工。

**LLM 驱动 alpha 挖掘远期候选**（00_index G28 讨论要点回填）：本项目 100% AI 开发模式天然契合"量化行业从因子竞争转向智能体竞争"趋势，但当前手动因子研究足够，以下 LLM 驱动自动化方案记为远期候选（Phase 5+），待因子库扩张 + LLM 能力成熟后评估。**评估优先级**：AlphaSchema > FactorMiner > AlphaMemo > Hubble > AlphaCrafter > XALPHA > EFS。

| 候选 | 出处 | 核心范式 | 与本项目关系 |
|---|---|---|---|
| **QuantEvolver RFT** | [arXiv:2605.15412, 2026-05](https://arxiv.org/pdf/2605.15412)（[代码](https://github.com/QuantLLM/QuantEvolver)） | **权重级策略内化**——RFT 强化微调替代 prompt-loop，将可执行量化评估转化为 policy updates，逃离上下文窗口限制（prompt-loop 的历史累积导致 context explosion）；组件：Factor DSL + Regime Backtest + Diversity-Complementarity Reward + Factor Database | 下一代方向；比 QuantaAlpha 轨迹进化更深一层 |
| **QuantaAlpha** | [arXiv:2602.07085, 2026-02](https://arxiv.org/abs/2602.07085) | prompt 级**轨迹进化**挖因子（不更新权重），diversified planning + trajectory quality + semantic anchoring + experience transfer 四组件，比 RD-Agent/AlphaAgent 更高 IC | Phase 5+ |
| **EvoQuant** | [arXiv:2607.12455, 2026-07](https://arxiv.org/abs/2607.12455)（HKUST(GZ)） | LLM 优化策略代码（诊断瓶颈→候选编辑→多阶段验证→蒸馏知识）；7 策略实证 test Sharpe -0.298→0.538 | Phase 5+；其多阶段验证管线（防幻觉编辑+策略漂移+回测过拟合）是防失控重点参考 |
| **Strategy-Dev-Manager** | Vibe-Trading 2026-07 | paper PDF→LLM 提取因子公式→Signal Engine 实现→IC/IR 评估→decay monitoring 自动禁用 | Phase 5+ |
| **AlphaSchema** | [arXiv:2607.26642v1, 2026-07-29](https://arxiv.org/html/2607.26642v1) | schema 级语义空间探索（Event/Context/Qualities/Direction/Output 五元组），解耦 exploration 与 implementation；关键发现：alpha mining 质量对 LLM 选择鲁棒；中国 A 股实证含因子衰减分析 | 优先级最高——可先实现 schema 词汇表辅助人工因子研究 |
| **XALPHA** | [arXiv:2607.08332v1, 2026-07-09](https://arxiv.org/abs/2607.08332v1) | 记忆驱动闭环研究过程（read→hypothesize→implement→validate→reflect→evolve），三脑架构（Macro/Micro/Cross），tri-alignment 三重对齐；CSI300 实证 | Phase 5+，最完整但最重 |
| **EFS** | [arXiv:2507.17211v2, 2026-08-07](https://arxiv.org/abs/2507.17211v2) | portfolio level 因子优化（非 IC level）——资产选择重构为因子引导 ranking + random-matrix-theory 去噪 + 正则化 QP；美/港/A 股三市场实证 | Phase 5+，最贴近实盘但依赖因子库成熟 |
| **AlphaCrafter** | [arXiv:2605.05580](https://arxiv.org/pdf/2605.05580) | Miner+Screener+Trader 三 Agent 全栈闭环（因子挖掘→regime 适配→策略执行），动态因子管理对抗 alpha decay 优于静态因子集 | Phase 5+；与 30 号"LLM 多 Agent 辩论暂缓"约束冲突最直接 |
| **FactorMiner** | [arXiv:2602.14670](https://arxiv.org/pdf/2602.14670v1)（Tsinghua） | Modular Skill Architecture（可执行评估工具保公式可解释）+ **Experience Memory**（成功模式+失败约束可检索 memory）+ **Ralph Loop**（retrieve→generate→evaluate→distill）；110 因子全 A 股库低冗余实证 | **Phase 3 轻量契合点**：Experience Memory 可脱离 LLM 独立实现——§3.2 假设状态机的"跨假设经验累积"层，因子库 >20 时将已验证假设的成功/失败模式结构化为可检索 memory 辅助人工研究，<100 行无需 LLM |
| **CogAlpha** | [arXiv:2511.18850](https://arxiv.org/abs/2511.18850)（ACL 2026 Oral） | **代码级 alpha**（Python 程序，搜索空间质变）+ 7 层 21 Agent 结构化探索；CSI300 年化超额 16.39%、IR 1.8999；关键发现：闭源模型无天然优势 | Phase 5+；**Level ⑥ Regime 门控层可消费 10 号 12 态 regime 作门控信号**——LLM alpha 挖掘与 regime 系统的唯一显式集成点 |
| **Hubble** | [arXiv:2604.09601, 2026-04](https://arxiv.org/abs/2604.09601) | DSL 受限生成 + **exec-free AST 验证沙盒**（白名单节点+复杂度控制+语义校验，无需执行代码）+ **Dual-Channel RAG**（负 RAG 检索 crowded 模板防拥挤）+ 确定性评估引擎——唯一显式建模生成安全性的框架 | **AST 沙盒是 LLM alpha 挖掘安全施工的最低门槛**：引入 LLM 生成因子代码前须先部署（白名单算术/时序/截面/逻辑算子，拒绝 import/open/exec/eval，深度≤10/节点≤50，<200 行可先于 LLM 施工，Phase 5 安全基础设施） |
| **AlphaMemo** | [arXiv:2606.20625, 2026-05-26](https://arxiv.org/abs/2606.20625)（Sydney+Edinburgh） | **结构化搜索过程记忆**（残差/决策/AST 差异，粒度比 FactorMiner 语义级更细）+ Parent-Edit Action Space（父代邻域编辑压缩搜索空间）+ AST-diff Edit Motifs + **APV 不对称过程否决**（失败路径否决防错误传播，成功路径不强制复用防过拟合）；关键洞见：过程记忆 > 结果记忆 | **Phase 3 轻量契合点**：APV 可脱离 LLM 独立实现——将假设验证"拒绝路径"结构化为可检索否决 memory，<80 行无需 LLM；与 FactorMiner 正交可叠加（FactorMiner 记"什么方向有前景"，AlphaMemo 记"什么编辑模式会失败"） |

- **防同质化补充**：[AlphaAgent](https://arxiv.org/abs/2502.16789)（arXiv:2502.16789, KDD 2025）AST 相似度原创性强制 + 假设-因子语义对齐 + 复杂度控制——**AST 相似度正则化独立于 LLM**，可用于传统因子挖掘阶段检测新因子与已有因子库同质化，与五骑士 ① Crowding 41% 直接对应，Phase 2 候选（因子库 >20 时用，<50 行无需 LLM）。
- **统一理论框架参照**（[arXiv:2608.01789, 2026-08-03](https://arxiv.org/html/2608.01789v1)）：自主公式化 alpha 发现六组件框架——Representation / Variation / Fitness / Selection / Memory / Adaptation。候选映射揭示两个覆盖薄弱点：Memory 维度（仅 FactorMiner/EvoQuant/AlphaMemo 显式建模，**AlphaMemo 过程级记忆是 Memory 组件范式升级**）与 Representation 安全约束（仅 Hubble 显式建模 exec-free AST 沙盒）——分别由 FactorMiner/AlphaMemo 和 Hubble 填补。综述登记为理论参照非新算法，不改变评估优先级。
- **不过度工程审查**：上述方案均涉及 LLM 自主生成/优化策略代码，与 §2.3 约束"不做 agent 编排系统"（30_multi_strategy §5 已暂缓 LLM 多 Agent 辩论）一致——记为远期候选不立即施工，待因子库扩张 + LLM 能力成熟后评估。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RES-03-A | 假设生命周期管理 | §3.2 纪律 2 假设驱动（状态机 提出→验证→接受/拒绝 全程留痕） | design 待施工 |
| BM-RES-10-A | 模块工厂架构 | §3.2 纪律 4 模块工厂 + §3.8 creation_token/depgraph 登记 4 步流程 | design 待施工 |
### 3.3 模型训练阶段（BM-MOD）规范
承接 [battle_map_02_model_training](../battle_map/battle_map_02_model_training.md)（14 环节，10 锚点）：

**核心纪律**：
1. **Champion-Challenger 晋升**（BM-MT-02）：新模型不直接全量上线——A/B 实验对比，统计显著更好才晋升为 Champion，否则留 Challenger 观察。**默认动作：证据不足时保留 Champion**（[MetricGate 2026-04](https://metricgate.com/blogs/champion-challenger-model-testing/)）。**统计检验：mSPRT 混合序贯概率比检验**——每笔交易后累加似然比，达边界即判定（接受 H1 晋升 / 接受 H0 保留 / 继续观察），无需预设样本量；mSPRT 产生 **e-process**，满足 `P(ever exceeds 1/α) ≤ α` 在所有停时成立，可任意频次查看无"偷看惩罚"（经典 SPRT/固定样本 t-test 月度偷看 12 个月实验，Type I 从 5% 膨胀到 ~25%）（[burning-cost 2026-03-24](https://burning-cost.github.io/2026/03/24/sequential-ab-testing-insurance-champion-challenger/)，Johari et al. 2022）。**e-value 理论根基**（[MetricGate 2026-06](https://metricgate.com/blogs/e-value-vs-p-value-evidence/)）：e-value 可乘，独立批次之积构成 test martingale `M_n = ∏E_i`，Ville 不等式保证 anytime-valid；e-value→p-value 转换 `p = min(1, 1/E)`。**陷阱**：tau（先验效应大小）标定错误会严重失效，须用历史 OOS 效应量分布标定。**流量切分**：95/5 不对称分流——**blast-radius 原则**：5% 上限按「challenger 失效最多波及多少资金」反推而非按速度，风险遏制优先于收益验证（[MetricGate A/B 2026-04](https://metricgate.com/blogs/model-deployment-ab-testing/)）+ 护栏指标 guardrail metrics；[theneuralbase 2026-04](https://theneuralbase.com/ai-for-finance/learn/intermediate/champion-challenger/)：金融业 SR 26-02 要求 4-12 周并行验证 + 预注册假设（效应量/显著性/停止规则并行期开始前文档化）。**双指标纪律**：①业务指标（Sharpe/expectancy/年化收益）+ ②ML 指标（AUC/IC/Calibration ECE），**Challenger 两项都优于或等于 Champion 才晋升**——只赢业务指标可能是运气，只赢 ML 指标可能未转化为收益。**ECE 校准门控**：`ECE = Σ (n_b/n) × |p̄_b - ȳ_b|`，Challenger ECE 不得显著高于 Champion（排名好但校准差会导致下游阈值/仓位规则错误触发）。**护栏指标**：最大回撤/换手率/滑点偏离超限立即终止实验。**方法谱系与选型理由**：GSPRT / Always Valid P-Value / Free Anytime Validity（[Koning & van Meer 2025](https://arxiv.org/html/2501.03982v3)）/ 贝叶斯替代范式（Expected Loss / Probability to Be Best，VWO/Statsig 采用）——本项目选 mSPRT 因金融监管（SR 26-2）偏好频率学派 Type I 控制 + 无先验依赖 + e-value 可转 p-value 对接传统报告；**最坏实践是"用固定样本方法但偷看"**（Type I 膨胀至 20-30%，[experimenthq 2026-12](https://www.experimenthq.io/blog/sequential-testing-vs-fixed-horizon)），本项目选序贯因交易笔数累积慢、需要早期停止能力。

   **mSPRT 施工伪代码**（核心三要素：似然比累加 + tau 标定 + 边界判定）：

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
           var_n = self.n * sigma**2
           lr = np.sqrt(self.tau**2 / (self.tau**2 + var_n)) * \
                np.exp((mean_delta**2 * self.n * self.tau**2) / (2 * sigma**2 * (var_n + self.tau**2)))
           self.M *= lr  # test martingale 累乘（e-values 可乘性，M_n = ∏E_i）

           # 边界判定（Ville 不等式 anytime-valid）
           if self.M >= self.threshold:           # M ≥ 1/α → 拒绝 H0，晋升 Challenger
               return "PROMOTE_CHALLENGER"
           if self.n >= self.max_sample_size and self.M < 1 / self.threshold:
               return "RETAIN_CHAMPION"           # 证据不足时默认保留 Champion
           return "CONTINUE"
   ```
   **施工要点**：① α=0.05 对齐 SR 26-2 频率学派 Type I 控制；② tau 用历史 OOS 效应量标准差标定（≥5 个历史点，冷启动兜底 0.2）；③ 边界 1/α=20（Ville 不等式）；④ 似然比用高斯 mixture 闭式解（Johari et al. 2022）；⑤ 流量切分通过 MLflow alias 路由——Challenger 注册 @challenger alias，信号扇出时 5% 订单流走 Challenger 推理路径（blast-radius 上限），95% 走 @champion；晋升时 alias 切换 @champion←@challenger，旧 Champion 自动落 @archived。

   **多策略选择演进路径**：mSPRT 是"champion vs challenger"**成对**序贯检验，适配 3-5 策略规模；策略数 >8（G11 第二批次上线后）时成对比较 O(N²) 组合数 + FWER 膨胀（Bonferroni 过保守），升级为"N 选 K"：**ASHA Tournament**（successive halving 逐轮淘汰底部半数 + 异步并行，[FerroQuant 2026-03](https://arxiv.org/abs/1808.08926)，1056 标的×178 策略实证）+ **SERPANT**（e-process 控制两两比较 FWER + tournament sampling 自适应选比较对 + top-k + early stopping，[Gu et al. ICML 2026](https://openreview.net/forum?id=7Y8xRnGQ47)）——ASHA 决定"淘汰谁"，SERPANT 保证"淘汰决策统计可靠"，正交可组合。记为 **Phase 2+ 候选**：3-5 策略规模下引入是净负担，不立即施工。
2. **灰度 + 影子部署**（BM-MT-02-A）：渐进流量梯度 5% → 25% → 50% → 100%，每阶段自动比较指标，异常自动回滚流量；影子模式并行预测不改决策 → 全量晋升或回滚。**影子模式持续时长量化**：须覆盖至少 1 个完整 regime 周期——A 股日内策略 2-4 周，隔夜/波段策略 8-12 周，至少 30-50 笔影子交易才具备统计意义（SR 26-02 金融业 4-12 周并行验证；30-50 笔早期预警，100+ 笔确认）。**影子模式异步架构**（[mljar 2026](https://mljar.com/ai-prompts/mlops/model-monitoring/prompt-shadow-mode/)）：Champion 服务所有请求，Challenger 异步接收请求副本——**fire-and-forget + timeout**，Challenger 超时/出错只记日志绝不阻塞 Champion 响应。**每日对比分析 5 维度**：agreement rate / score correlation / KS 分布比较 / disagreement 抽样 50 笔人工检查 / latency（Challenger p99 须满足 SLA）。**成本警示**：影子模式翻倍计算成本，Challenger 用较小副本数降成本。
3. **对抗鲁棒性**（BM-MT-02-B）：上线前 FGSM/PGD 对抗扰动测试，输入被轻微扰动就翻盘的模型不准上生产。
4. **漂移检测多方法 Drift Observatory**（BM-MT-05）：单一 PSI 只能抓边际特征漂移，抓不住多变量联合分布漂移和概念漂移。升级为多方法组合：
   - **特征漂移**（covariate shift）：PSI（>0.1 调查 / >0.25 材料性漂移）+ KS 检验（Bonferroni 多重比较校正）+ MMD（多变量联合分布漂移，RBF 核 + 随机傅里叶特征近似 O(n²)→O(n)）+ **Wasserstein 距离**（Earth Mover's Distance，一维 O(n log n)，比 KS 更敏感于整体分布形状变化）——多变量场景用 MMD，单变量连续特征用 Wasserstein 补充 KS 盲区。
   - **概念漂移**（concept drift）：ADWIN（Adaptive Windowing）在滚动误差率上检测结构突变——X→y 映射关系变了，PSI 抓不住。
   - **残差漂移**：CUSUM / Page-Hinkley 在模型残差上检测持续偏移。**CUSUM 参数标准设置**：单侧 `S⁺ₜ = max(0, S⁺ₜ₋₁ + (μ₀ - xₜ) - k)`，μ₀ 为 OOS 验证期均值（**禁止用全回测均值**——包含待检测 regime 会污染基线），k=0.5σ，h=4σ（约 0.5 次/年误报）；实证 Sharpe~1 策略 changepoint 后约 50 交易日检出，优于 Rolling Sharpe 转负的 6+ 个月。**三大失效风险与解法**：①重尾失效（金融收益超额峰度常 >20，经典 CUSUM 100% 误报 → 广义随机逼近 LLR，仅用至 3 阶矩，[arXiv:2605.23419](https://arxiv.org/html/2605.23419v1)）；②自相关失效（AR(p) 特性使 IID 检测器失效 → AR(p)-focus 算法，每迭代 O(log n)，[arXiv:2607.16106](https://arxiv.org/pdf/2607.16106)）；③单窗口局限（→ PM-CuSum 多窗口预测分布组合，一阶渐近最优，[arXiv:2606.05072](https://arxiv.org/html/2606.05072v2)）。**Phase 1 缓解措施**（重尾 100% 误报是实盘生存级问题，LLR/AR(p)-focus/PM-CuSum 均为 Phase 3/4 候选，Phase 1 须可施工）：**① 收益稳健预处理**——CUSUM 输入前 winsorize 截尾到 1%/99% 分位，超额峰度从 >20 压到 <5（<10 行代码）；**② CUSUM 降权 + MMD 提权**——composite drift score 中 CUSUM 权重 0.15→0.05，MMD 提权作主检测器；**③ 确认窗口**——告警后加 3-5 日确认窗口（连续 N 次超标才触发），过滤重尾单日极值；**④ 残差而非原始收益**——残差尾部更轻，高斯假设更接近成立。①+④ 为 Phase 1 必做（<15 行零依赖），②+③ 为推荐（<20 行）；Phase 3 升级后预处理仍保留（与重尾检测器正交可叠加）。
   - **预测漂移**（prediction drift）：模型输出分布变化——即使输入分布未变，分数分布也可能因 calibration 漂移或模型更新而偏移。检测：对输出分数做 PSI/KS 对比 OOS 验证期分布，分数向均值坍缩或双峰分裂是漂移信号。**对量化交易的特殊意义**：信号置信度分布偏移 = 模型在"什么时候该交易"的判断上漂移，是 IC 下降的先行指标。
   - **标签漂移**（label drift）：目标变量先验分布变化（如 A 股牛熊切换导致正收益股票比例变化），与特征/概念漂移正交。检测：监控实际收益率分布滚动统计量（均值/偏度/峰度），与 regime 检测器联动——标签漂移往往是 regime 切换的统计表征（regime 检测器从特征空间聚类，标签漂移从目标分布统计，互补视角）。
   - **三层检测架构**：① **Layer 1 输入监控**（特征漂移 PSI/KS/MMD，无需 ground truth，最快预警）；② **Layer 2 预测监控**（预测漂移 + 残差漂移，无需 ground truth，连接输入变化到模型行为）；③ **Layer 3 延迟结果监控**（概念漂移 ADWIN + 标签漂移，需延迟 ground truth，最终验证）。三层递进：Layer 1 预警"输入变了" → Layer 2 确认"模型行为变了" → Layer 3 验证"预测质量变了"，避免单一层误报。
   - **composite drift score**：加权组合 `0.3×PSI_max + 0.2×MMD + 0.2×KS_max + 0.15×CvM_max + 0.15×concept_drift_rate`，超阈值 0.35 触发重训练。**CvM（Cramér–von Mises）比 KS 对尾部漂移更敏感**——KS 只看最大差异点，CvM 积分全分布差异，尾部偏移是金融数据漂移的常见模式。**多重检验校正**：多检测器并行 → 误报率膨胀，用 Benjamini-Hochberg FDR 校正保持告警率可控。
   - **MMD 严格基准实证**（[royxforge 2026-06-15](https://github.com/royxforge/production-drift-detection/blob/main/README.md) 20 种子基准）：**MMD 复合排名 #1（0.9225）**——FPR=0.0% / 检测率 99.9% / ROC AUC=1.0000 / Cohen's d=6.38；PSI 检测率 100% 但 **FPR 高达 39.9%** 单独使用不可接受须配合 MMD；ADWIN FPR=46.5%。所有检测器中位延迟 0 批次。**流式部署陷阱——MMDEW**（[striim-labs 2026-03](https://github.com/striim-labs/online-drift-detection-mmdew)）：流式 MMD² 值 lag-1 自相关约 0.87，超标事件聚类成长串导致误报风暴——解法三机制：automatic recalibration + confirmation window（连续 N 次超标才告警）+ adaptive thresholding（99th 百分位替代 95th）。本项目批量检测（每日盘后）各批独立无此问题；若升级盘中流式 MMD 须采用 MMDEW 机制。**WMAPE 整体精度监控**：滚动均值偏离基线 1.5σ 告警——PSI 抓不住误差突变，CUSUM 抓不住整体精度慢漂移，WMAPE 可作 composite score 第六分量（精度层），与 PSI（特征层）+ CUSUM（残差层）+ ADWIN（概念层）正交补充。
   - **下游影响门控**（downstream impact gating）：**"统计显著性不等于业务显著性"**——特征漂移告警须经下游影响估计过滤：在验证期建立"特征偏移幅度 → 预测误差影响"近似映射，仅当估计下游影响超业务阈值才告警。多数特征因季节性/regime 切换/数据源变更持续漂移（良性漂移），全部告警则告警疲劳。
   - **漂移 vs 过拟合鉴别——Deflated Sharpe Ratio**：检测到漂移信号后先用 DSR 排除过拟合可能——DSR 调整回测 Sharpe 反映多次试错惩罚，DSR 仍显著 > 0 则漂移是真市场结构变化走重训练/退役流程，DSR 不显著则原策略本身是过拟合产物（漂移是假象），走"策略本身无效"诊断回 §3.2 孵化阶段重新假设。
   - **三闭环保留 + 分级响应阶梯**（staged operational responses）：事前 composite drift score 预警 → 事中在线适应（EWMA/Stage2 缩放）→ 事后 C-007 离线重训；响应不直接跳到重训练，按严重程度分级——① **alert**（仅通知，策略正常运行）；② **reduce size**（减仓至 50%）；③ **stop new entries**（停止新建仓，仅平存量）；④ **quarantine**（隔离暂停待诊断）；⑤ **retrain**（触发重训练）。每级有明确进入/退出条件，避免"一有漂移就重训练"的过度反应。

   **Layer 4 可证覆盖层——Conformal Prediction**：Layer 1-3 是启发式阈值（快但有误报），**Conformal Prediction 提供有限样本覆盖保证** `P(Y_{n+1} ∈ Ĉ(X_{n+1})) ≥ 1 - α`，对任意分布、任意模型、任意样本量成立，仅需可交换性。**split conformal 四步**：① 训练集拟合 μ̂；② 校准集算非一致性分数 `sᵢ = |yᵢ - μ̂(xᵢ)|`；③ 取 `(1-α)` 分位数 q̂；④ 预测区间 `Ĉ = [μ̂(x) - q̂, μ̂(x) + q̂]`。**三层应用**：① 漂移检测（监控实际覆盖率，实际覆盖 < 名义 (1-α) 即漂移——数学保证信号非启发式阈值）；② 仓位管理（区间宽度 = 动态风险信号，宽→保守/窄→放大）；③ VaR 校准（RWC regime-weighted conformal 直接对接 36 号 var_calculator，CRSP+16 美股组合 Basel 99%/97.5% 验证，[arXiv:2602.03903](https://arxiv.org/html/2602.03903v3)）。**金融收益特殊处理**（[conformal.marketmaker.cc](https://conformal.marketmaker.cc/) 180 实验）：边际覆盖在 AR(1)/GARCH 下存活（0.901/0.895），仅突变微降；**条件覆盖是 casualty**（GARCH 高波动三分位低估 8 个百分点）——修复：EWMA 波动率归一化分数（spread 0.134→0.040）。**CP ↔ VaR 等价**（[PMLR 266 Retzlaff 2025](https://proceedings.mlr.press/v266/retzlaff25a.html)）：36 号 VaR 回测设施可直接复用于 CP 覆盖检验。**施工定位**：Phase 3 候选，CP 是 wrapper 不改模型，实现 <100 行；先在 36 号试点 RWC VaR 校准再扩展。**mandatory baseline**：先实现 5 行 ConformalNaive 作 floor，自适应方法不能显著超越则不值得复杂度（[arXiv:2606.09473](https://arxiv.org/pdf/2606.09473v1)）。

   **突变处理主路径——CUSUM + calibration flush（minimax 最优）+ BC-ACI 中心纠正**：
   - **calibration flush**（[arXiv:2602.16537](https://arxiv.org/pdf/2602.16537)，Princeton/Wharton 2026-02）：ACI 的边际覆盖保证允许 regime shift 后持续 60-80 步严重欠覆盖（首半程 66.7%，纸面 valid 但实盘"飞行盲打"）；minimax 最优解是 **CUSUM 检测 + 完全丢弃陈旧校准集用 post-drift 分数重建**（下界 O(√(KT)) 证明无算法可超越）。复用 §3.3 残差漂移 CUSUM 基础设施（同一检测器既检残差漂移又触发 CP 校准集冲刷），<20 行增量。
   - **BC-ACI 偏置校正**（[arXiv:2604.13253](https://arxiv.org/pdf/2604.13253)，Lade et al. 2026-04）：ACI/flush 只调区间宽度无法移动中心——模型持续预测偏置时 ACI 被迫对称膨胀（宽度开销 2|b|）；BC-ACI 叠加 per-horizon EWMA 偏置估计 `b̂_t = EWMA(e_t)` 纠正非一致性分数 `s̃_t = s_t - b̂_t` + MAD 死区阈值，ridge level shift 后 Winkler 分数改善 32%（宽度 8.67→5.50，37% 削减），自校正模型中性无副作用。**与 flush 正交互补**：flush 管宽度重建，BC-ACI 管中心纠正，双重保护（牛市训练模型在熊市系统性高估等场景），<30 行。
   - **联动**：CUSUM 告警 → calibration flush 重建校准集 → BC-ACI 持续纠正残余偏置。

   **四层 Drift Observatory 联动编排伪代码**（四层告警聚合→分级响应映射的可执行编排逻辑）：

   ```python
   def drift_observatory_orchestrate(strategy_id, features, model_output, realized_pnl):
       """四层 Drift Observatory 联动编排
       四层递进：Layer 1 预警"输入变了"→ Layer 2 确认"模型行为变了"
       → Layer 3 验证"预测质量变了" → Layer 4 可证"覆盖保证破了"
       分级响应：alert → reduce_size → stop_entries → quarantine → retrain
       核心纪律：单一层告警不触发高级响应，须多层确认"""
       # === 四层并行检测，各层独立产出 severity 0.0-1.0 ===
       l1 = input_monitor.check(features)           # PSI/KS/MMD/Wasserstein 特征漂移
       l2 = prediction_monitor.check(model_output)  # prediction drift + CUSUM 残差漂移
       l3 = outcome_monitor.check(realized_pnl)     # ADWIN 概念漂移 + 标签漂移（延迟 ground truth）
       l4 = conformal_layer.check_coverage()        # 数学保证：实际覆盖 < 名义 (1-α) 即漂移

       # 下游影响门控：Layer 1 特征漂移须经业务影响估计过滤
       if l1.severity > 0 and not downstream_impact_gate(l1):
           l1.severity = 0  # 良性漂移（季节性/regime），降级避免告警疲劳

       # CUSUM→calibration flush 联动：Layer 2 残差 CUSUM 告警触发 Layer 4 校准集冲刷
       if l2.cusum_alarm:
           conformal_layer.flush_calibration_set()  # 丢弃陈旧校准集，post-drift 重建（minimax 最优）
           bc_aci.correct_bias(l2.residual_bias)    # BC-ACI 在线纠正残余偏置（宽度+中心双重保护）

       # === 告警聚合：加权 composite score ===
       # Layer 4 权重最高（可证覆盖非启发式）→ Layer 3 → Layer 2 → Layer 1
       weights = {1: 0.15, 2: 0.20, 3: 0.25, 4: 0.40}
       composite = sum(weights[L] * sev for L, sev in [(1,l1.severity),(2,l2.severity),(3,l3.severity),(4,l4.severity)])

       # === 分级响应映射（不直接跳重训练）===
       if l4.coverage_breach or composite >= 0.80:
           response = "RETRAIN"             # 严重：Layer 4 可证覆盖破 或 多层共振
           trigger_retraining(strategy_id)
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
   **施工要点**：① 四层权重 Layer 4 最高（0.40，可证覆盖非启发式）反映"数学保证 > 经验阈值"优先级；② 下游影响门控仅作用于 Layer 1（特征漂移多为良性），Layer 2-4 已直接关联模型行为不门控；③ CUSUM→calibration flush 复用残差漂移 CUSUM 基础设施；④ 分级响应阈值 0.20/0.40/0.60/0.80 对应五级响应；⑤ Layer 4 `coverage_breach` 直接触发 RETRAIN 绕过 composite 阈值——数学保证层告警不可被其他层"稀释"。

   **downstream_impact_gate / trigger_retraining 施工规格**（编排伪代码两个 helper 的逻辑规格）：
   - `downstream_impact_gate(l1)`——Layer 1 特征漂移业务影响四步检查：① **regime 解释**（当前 regime ∈ 已知良性列表：季节性/假期/已知切换，复用 10 号 regime 检测器 12 态）；② **IC 衰减**（漂移特征 rolling IC(20d) vs baseline，|ΔIC| > 0.05 = 显著）；③ **Sharpe 退化**（Rolling Sharpe(50 笔窗口) < baseline × 0.7 = 显著，对齐第 5 条 Decay Detection 监控点 1）；④ **残差膨胀**（recent loss(10) > baseline × 1.3 = 显著，对齐第 7 条回滚阈值 MAPE 行）。**复合判定**：regime 可解释 AND ②③④均无显著退化 → 良性漂移降级 severity=0，否则保留告警——regime 可解释是必要非充分条件（即使 regime 良性，IC/Sharpe/残差已退化说明漂移已穿透到模型性能仍须告警）。与 SHAP 归因（哪个特征）/ARM 归因（哪些维度）在"是否漂移→哪些维度→业务影响"链路分工互补。
   - `trigger_retraining(strategy_id, trigger_source)`——三触发（performance / schedule / data_volume，第 8 条）。**分级决策**：突发漂移（composite ≥0.80 / coverage_breach / abrupt）→ 全量重训练；渐进漂移/定时/数据量 → 增量重训练（Phase 3 渐进漂移可升级 knowledge distillation，成本比全量低 5-10x）。**回滚保险（SBS 纪律）**：旧 Champion 版本先落 @challenger；warm-refit 在服务路径外（不在 @champion 上直接训练），滚动窗口数据 + EWC + 伪回放；新模型经第 9 条晋升门禁（OOS Sharpe ≥ Champion × 0.9 / profit factor > 1.5 / MaxDD ≤ Champion × 1.2 / 子周期一致性 / Sortino+Calmar 三角验证）通过 → 晋升 @champion + 旧版保留 30 天回滚窗口；未通过 → 落 @archived 待诊断，保留旧 Champion。与第 7 条回滚的边界：回滚=新 Champion 上线 24h-7 天内紧急恢复（秒级 alias 切换），重训练=Champion 长期退化（盘后离线动作）。

   **候选登记表**（均完成不过度工程审查，不立即施工；触发条件随条目保留）：

   | 分组 | 候选（出处内联）与定位 / Phase / 触发条件 |
   |---|---|
   | **Phase 1 纪律补强** | **SBS 维护态 Champion 语义**（[arXiv:2607.28577, 2026-07-30](https://arxiv.org/html/2607.28577v1)，Dutta Emory）：生产 Champion 是**持续学习的维护态系统**非冻结 checkpoint——重训练候选须胜过维护态 Champion（warm-refit 路径外 + 同周延迟标签配对评估 + 固定 paired NLL 优势才晋升；528 Challenger 仅晋升 114，减 78.4% 切换）；53 号灰度门禁 Champion 基线须为当前维护态非部署时快照。零代码增量 |
   | **Phase 2/2+（晋升/退役检验增强）** | **SCORE overshoot refund**（[ICML 2026, Kuang/Gang/Xia](https://openreview.net/forum?id=qX4Nm7eNM5)）：回收 mSPRT e-process 超过 1/α 阈值的"超调"证据（`I(y≥1) ≤ y − (y−1)₊`），序贯多 Challenger 串行检验功率提升——时间维度，与 ASHA/SERPANT（空间维度并行）正交，wrapper <20 行；**DPitG 双停止准则**（[arXiv:2608.05301, 2026-08-05](https://arxiv.org/abs/2608.05301)，Kazin）：精度目标（HDI 宽度 < ω）+ 决定性裁决（HDI 完全在 ROPE 内接受 H0 / 完全在外接受 H1 / 重叠继续），补 mSPRT"可停但不决"（62%→2% 不确定率零假阳性，替代 max_sample_size 粗暴兜底，<40 行）；**Ranking by Lifts 成本收益 FDR**（[arXiv:2407.01036v2, Basu & Berman](https://arxiv.org/abs/2407.01036v2)）：lfdr 贪心 knapsack 按"期望 lift/错误切换成本"排序，最大化利润同时控制 FDR + 财务成本（与 SCORE 正交：SCORE 管功率，RBL 管成本；策略数 >8 时）；**evalinger futility 事前放弃**（[arXiv:2602.06379v1, 2026-02-06](https://arxiv.org/abs/2602.06379v1)）：同一 e-process 反向检验 H0: 策略 edge ≤ 0，§3.9 退役升级为事前+事后（连续监控下 e-value power 反超 group sequential，<50 行复用 mSPRT） |
   | **Phase 3 监测有效性（与 Layer 4 同期）** | **betting martingale 覆盖监测**（[arXiv:2602.04364, 2026-02](https://arxiv.org/abs/2602.04364)，Hultberg/Bates/Candès）：Layer 4 覆盖率月度偷看 12 次 α=0.10 则 FWER 膨胀至 72%（与 mSPRT 同构）——覆盖指示 `Z_t = 1[Y_t ∈ Ĉ(X_t)]` 构造下注鞅 `M_t = ∏(1 + λ_s·(Z_s − (1−α)))`，λ 取 0.5/(1−α)，Ville 边界 1/α=10（同属 e-value 框架复用同一基础设施，<30 行）；与 flush/BC-ACI 正交（它们管校准集维护，本项管监测告警层）；**Conditional CTM 污染修复**（[arXiv:2602.13848v2, ICML 2026](https://arxiv.org/abs/2602.13848)，Shaer et al.）：自适应区间 `Ĉ` 与覆盖指示 `Z_t` 形成 test-time contamination 反馈环（ACI miss 后加宽→下一 Z_t 更可能为 1→鞅误判）——用固定参考集计算分数 + 鲁棒 betting function，anytime Type I + power-one + 有界检测延迟（~30-40 行，是 betting martingale 统计有效性的必要补强）；**Legendre Jumper 高阶矩**（[arXiv:2606.20859v2, 2026-07](https://arxiv.org/abs/2606.20859)，Szabadváry）：移位 Legendre 多项式 betting function，k=2 检测方差/波动率漂移（A 股波动率 regime 切换=五骑士 ② 28% 第二大根因的早期预警，一阶矩不变时朴素鞅完全失明），Variational 版 O(1) 更新；与 10 号 regime 检测器互补（离散态分类 vs 连续方差漂移，~40-50 行）；**Subgroup 欠覆盖审计**（[arXiv:2608.04254, 2026-08-06](https://arxiv.org/abs/2608.04254)）：子组（regime 态/行业/市值分位）欠覆盖有限样本审计 + FWER 控制——边际 90% 掩盖局部 70% 的静默失效，RLCP 前置诊断（~100-150 行） |
   | **Phase 3 归因诊断** | **ARM 变点归因**（[arXiv:2608.01691, 2026-08-03](https://arxiv.org/abs/2608.01691)，北京工业大学+南洋理工）：检测器无关 wrapper 返回"已认证变化"坐标集 + location/scale 标签，rank-based 对 A 股重尾天然鲁棒，FWER（Westfall-Young）+ FDR（BY/e-BH）有限样本保证——管资产级（~200-300 行）；**SHAP Drift Attribution**（[emitechlogic 2026-04-14](https://emitechlogic.com/how-to-detect-and-fix-production-drift-in-machine-learning-complete-guide/) + [arXiv:2602.19790](https://arxiv.org/pdf/2602.19790.pdf)）：漂移窗口 SHAP 偏移定位根因特征——管特征级；**Modular CP 多阶段归因**（[arXiv:2510.04406, 2025-10](https://arxiv.org/abs/2510.04406)）：pipeline 残差分解 `R ≤ ΔR₁ + R₂` 分阶段覆盖检验，区分传导性 vs 原生漂移——管阶段级（pipeline 阶段数 >3 时）；三者构成"特征级→阶段级→资产级"三级归因链；**Drift Robustness 鲁棒性评估**（emitechlogic 同上）：验证期注入可控漂移（均值平移/方差缩放/特征旋转）测退化曲线，Challenger 须漂移鲁棒性不劣于 Champion（与对抗鲁棒性正交：恶意扰动 vs 自然漂移） |
   | **Phase 3 框架/方法升级** | **Drift2Act 预算干预框架**（[arXiv:2603.08578v1, ICLR 2026 CAO](https://arxiv.org/abs/2603.08578v1)，Lamaakal et al.）：分级响应阶梯是启发式阈值映射——重构为"带安全约束的决策"：sensing layer + active risk certificate 在预算约束下触发干预（online risk certificates），不问"是否漂移"而问"当前漂移程度下什么干预安全成本最低"（漂移检测主路径稳定后）；**KDD 2026 漂移检测基准**（[arXiv:2606.07789](https://arxiv.org/abs/2606.07789)）：14 检测器标准化评测（Monte Carlo 可控漂移注入 + timing-aware F1/detection time + leave-one-dataset-out 超参优化），与 ProteuS 互补（ProteuS 生成数据，本框架评测检测器）；**Conformal Abstention 空仓决策**（[arXiv:2606.11949v3, 2026-08-04](https://arxiv.org/abs/2606.11949v3)）：预测置信度低于 conformal 保证阈值时主动弃权——"stop new entries"升级为覆盖保证的空仓决策，"quarantine"升级为 weighted-on-alarm abstention（generative embeddings silent failure 须投影 ≤32 维，与 Layer 4 同期评估）；**Betting on Bets 随机优势检验**（[arXiv:2604.21851v3, 2026-08-01](https://arxiv.org/abs/2604.21851v3)）：一阶/高阶随机优势序贯 anytime-valid 检验（GRO betting + predictably mixed e-processes，power-one）——均值比较的分布级升级，Challenger 均值略低但下行风险显著更小时可支持晋升（第 9 条三角验证的序贯版，<50 行）；**DTD 动态阈值**（[arXiv:2511.09953v1, AAAI 2026](https://arxiv.org/abs/2511.09953v1)，Lu et al. UTS）：可证明优于任何单一固定阈值——wrapper 增加比较阶段（comparison phase）在比较窗口评估不同阈值性能选最优，对 K 鲁棒（Phase 1 用固定阈值过渡）；**COP 共形乐观预测**（[arXiv:2512.07770v2, 2026-02-24](https://arxiv.org/abs/2512.07770v2)，Nankai/Tsinghua）：估计非一致性分数 CDF，存在可预测模式（A 股季节性/周期性）时产生更紧区间且保持覆盖（与 DASC 互补：DASC 管 regime 循环，COP 管可预测模式；过宽区间成为瓶颈时）；**鲁棒序贯实验设计**（[arXiv:2605.12899v1, 2026-05-13](https://arxiv.org/abs/2605.12899v1)，LSE）：mSPRT 高斯 mixture 在 A 股重尾可能失效——模型误设下界定处理效应 worst-case MSE，与 winsorize 预处理互补（winsorize 后仍重尾或 mSPRT 误设退化时）；**knowledge distillation 渐进漂移适应**（[newline.co 2026-04-21](https://www.newline.co/@Dipen/top-5-reinforcement-methods-for-finance-2026--3d4582d3)）：teacher-student 迁移适应新分布不丢历史知识，比全量重训练低 5-10x（渐进漂移场景；突发漂移仍全量）；**DT-GOL 双轨几何在线学习**（[arXiv:2606.22950, 2026-06-22](https://arxiv.org/abs/2606.22950)）：T+1 标签延迟——特征空间实时拓扑演化作几何代理 + 软标签蒸馏，主学习器严格用延迟真值，瞬态分支标签到达前响应（Phase 1 用"标签到达后 ADWIN + 到达前 Layer 1/2 先行预警"过渡；T+1 是 A 股硬约束非可选优化）；**CB-PDD 表演性漂移检测**（[arXiv:2412.10545v2, 2025-04](https://arxiv.org/pdf/2412.10545v2)）：区分外生漂移 vs 策略自致漂移——五骑士 ① Crowding 41% 本质是表演性漂移（AUM 扩大或检测到 crowding 类衰减时）；**ProteuS 漂移评测基准**（[arXiv:2509.11844](https://arxiv.org/html/2509.11844v1)，[代码](https://github.com/cetrulin/regime-switching-series-generator)）：ARMA-GARCH 仿真渐进/突变体制转换，已知 ground truth 断点作评测基准（验证候选） |
   | **Phase 3 链路补全** | **联合 VaR+ES 共形**（[MDPI Mathematics 2026-08-06, Ye et al.](https://www.mdpi.com/2227-7390/14/15/2847)）：ES 单独不可 elicitable，pair (VaR,ES) 联合可 elicitable（Fissler-Ziegel loss）——conformal risk control 耦合 VaR 突破频率与幅度，36 号 VaR 校准从 RWC 单一 VaR 升级 pair 对接 Basel 99%/97.5% 双级别（Layer 4 主路径稳定后）；**Conformal Kelly 链路补全**（[arXiv:2608.01494, 2026-08-02](https://arxiv.org/html/2608.01494v1)）：conformal 区间宽度作仓位 sizing 标度（宽→缩仓/窄→加仓），slow unweighted per-asset rolling quantiles 最优（自适应方法损失 0.7-5.3pp 年化——作仓位标度时宽度稳定性比局部锐度重要），补全 Layer 4→35 号 conformal_kelly_drawdown_dial→31 号 Kelly 三层传导链（交叉引用断点已补全，登记性质） |
   | **Phase 3-4 多流监测** | **Decaying-ε-FOCuS 多流变点检测**（[arXiv:2601.22561v5, 2026-08-01](https://arxiv.org/abs/2601.22561v5)，Stony Brook/Georgia Tech）：多策略/多资产面板计算预算有限——bandit 最快变点检测（M 条流每步采样一条，Decaying-ε-greedy + GLR，无离散化/无幅度下界假设一阶最优）；FOCuS 管采样分配（事前），ARM 管归因（事后）——策略数 >8 或因子数 >15 时评估 |
   | **Phase 4 鲁棒性（Layer 4 主路径稳定后）** | **SA-BCP 时空解耦贝叶斯 CP**（[arXiv:2605.00432, 2026-05](https://arxiv.org/html/2605.00432v1)，台湾大学）：空间核密度证据门控长期时间惯性——识别历史 regime 时主动扩展区间（ACI 被动适应 / flush 激进重建 / SA-BCP 主动预防），金融实证一致最小化 Winkler 分数、区间膨胀减 10%-37%，对 T+1"当日决策次日执行"尤其有价值；**CPTC 变点检测替代**（[arXiv:2509.02844, NeurIPS 2025](https://arxiv.org/abs/2509.02844)，Zaffran/Goude/Dieuleveut）：RED-SDS 替代 CUSUM + per-regime 独立学习率，检测即重置分位数，经验覆盖间隙 3-5pp（vs ACI 20pp）——flush 理论更强更轻（复用 CUSUM），CPTC 检测器更鲁棒但重（CUSUM 误报率高时）；**WCTM 统一框架**（[arXiv:2505.04608, ICML 2025](https://arxiv.org/html/2505.04608v2)）：加权 conformal test martingale——轻度漂移在线自适应（不告警）+ 严重漂移快速检测 + 根因分析三合一，补"轻度漂移不应告警但应自适应"的中间地带；**DASC 谱共形**（[arXiv:2606.15953v2, 2026-07](https://arxiv.org/html/2606.15953v2)，UT Rio Grande Valley）：谱相似性加权校准残差——regime 循环场景跨时共享信息（flush 完全丢弃会丢循环信息），谱距离 = 10 号 HMM regime 距离，金融波动率实证（突变走 flush，循环走 DASC；regime 循环成为校准瓶颈时）；**RLCP 局部化保形预测**（[arXiv:2608.06206, 2026-08-06](https://arxiv.org/abs/2608.06206)）：边际→条件覆盖有限样本升级（局部邻域联合保证，误差分解 O(h^β)）——flush 管突变 / BC-ACI 管偏置 / RLCP 管局部，三者正交；**GMM unexplained mass**（[arXiv:2607.16811v2, 2026-07-27](https://arxiv.org/pdf/2607.16811v2)）：GMM component = named regime，未解释质量即漂移信号且归因具名 regime——对接 10 号 HMM 12 态作 drift 守护层（C1 验证 + 主路径稳定后） |
   | **远期候选/观察** | **CEP 循环漂移预测器池**（[arXiv:2506.14790](https://arxiv.org/pdf/2506.14790v2)）：循环概念漂移专用预测器动态池 + 统计基因解耦，无需历史 ground truth 降误差 >20%（策略数 >10 且循环漂移成主要故障模式时）；**FIDI Z-Score**（[dataforcee 2026-03](https://dataforcee.us/2026/03/23/neuro-symbolic-fraud-detection-catching-concept-drift-before-f1-drops-label-free/)）：零标签概念漂移检测（5/5 seed 全检出有时在 F1 下降前，~50 行；covariate drift 盲区需独立监控器，远期观察） |

5. **Decay Detection 5 监控点**（[linitics 2026-04](https://linitics.com/quant-strategy-lifecycle-idea-to-decay/) + [LuxAlgo 2026-08-03](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/) 交叉验证）：策略衰减检测不能只看单一指标（"亏钱才退役"是零售思维），须五维度并行监控：
   - **Rolling Sharpe degradation**：滚动 Sharpe 持续下滑（30-50 笔交易早期预警，100+ 笔确认）
   - **Drawdown frequency 增加**：回撤频次上升 = edge 在压缩
   - **Correlation instability**：与其他策略相关性不稳定 = alpha 来源在被套利
   - **Execution cost drift**：实际滑点/冲击成本相对回测假设漂移 = 容量饱和
   - **Volatility mismatch**：策略波动率与历史不匹配 = regime 切换未适应
   - **Half-life of alpha 数学模型**（[mathandmarkets 2026-02-22](https://mathandmarkets.com/p/half-lives-of-alpha-why-every-strategy)）：alpha 衰减服从指数衰减 `α(t) = α₀·e^(-λt)`，半衰期 `t½ = 0.693/λ`；考虑 transaction cost floor（如 1.5% 年化），可用半衰期 = `-ln(cost_floor/α₀) / λ`。**用途**：根据 λ 估计预测策略何时退至 cost floor 以下，提前规划替代策略研发（与 §3.1 ⑥ 退役阶段联动）。**实证**：68% 系统化策略在 18-24 个月内需要重大修改或退役；alpha 衰减率美国年均 5.6%、欧洲 9.9%，且随时间递增。**农耕心态**：管理 alpha 衰减须从"金矿心态"（找一个永赚策略）转向"农耕心态"（持续研发流水线补新策略）——管理"信号组合"（portfolio of signals），部分衰减时部分新生。
   - **双曲线衰减模型**（[arXiv:2512.11913](https://arxiv.org/html/2512.11913v1) Lee 2025-12 KAIST）：指数衰减是经验拟合默认选择，双曲线衰减从**博弈论 Nash 均衡**严格推导——`α(t) = K / (1 + λt)`（K=alpha capacity 初始总量，λ=策略发现速率；N 个 agent 瓜分同一信号，N(t)=1+λt）。**核心实证**（8 个 Fama-French 因子 1963-2024）：① 机械因子符合双曲线——动量因子双曲线 R²=0.65 优于指数 0.61 和线性 0.51；② 判断型因子（价值/质量）不符合（信号模糊性使套利者进入慢）；③ 2015 后拥挤加速，OOS 高估剩余 alpha（预测 0.30 vs 实际 0.15），与因子 ETF 增长 ρ=-0.63；④ 拥挤预测尾部风险而非均值（拥挤反转因子 crash 1.7-1.8×，拥挤动量 0.38×，p=0.006）。

     | 衰减模型 | 公式 | 动量因子 R² | 理论基础 | 适用因子 |
     |---|---|---|---|---|
     | **指数衰减**（当前） | `α₀·e^(-λt)` | 0.61 | 经验拟合（数学便利） | 通用（默认） |
     | **双曲线衰减** | `K/(1+λt)` | **0.65** | **博弈论 Nash 均衡** | **机械因子**（动量/反转） |
     | 线性衰减 | `α₀·(1-λt)` | 0.51 | 最简近似 | 短期粗估 |

     **与本项目对齐**：首批 3 策略中**打板**（[24 号](24_daban_strategy_detail.md)）和**事件驱动**（[26 号](26_event_driven_strategy_detail.md)）属机械因子，应优先用双曲线衰减预测 alpha 寿命；**多因子**（[25 号](25_multifactor_strategy_detail.md)）含判断型因子，指数衰减仍适用。**裁定**：Phase 1 退役门禁仍用指数衰减（简单、通用、已实施）；**双曲线衰减记为 Phase 2 候选**——机械因子策略退役时机精算。升级条件：首批策略 6+ 月 PnL 后对比两模型预测残差，双曲线 OOS 拟合 R² 差 >0.05 则升级。**与 [55 号](55_monitoring_review.md) 协同**（⚠️55 号为 draft v0.1.0 骨架待讨论，G26 监控告警 why 层未定稿）：half-life 估算可切换衰减模型，无需重写监控框架。
   - **策略容量理论（break-even capacity + profit-maximising size）**（[hftradingbook 2026-06-04](https://hftradingbook.com/performance/capacity-and-alpha-decay) + Gatheral 2010 平方根律）：alpha 衰减还有**规模维度**——`net_edge(Q) = g - c·√Q`（g=毛 edge/unit，c=Y·σ/√V 冲击系数）→ break-even capacity `Q* = (g/c)²`，profit-maximising size `Q_max = (2g/3c)² = 4/9 · Q*`。**核心洞察**：利润最大化资金量仅为容量天花板的 **44%**——远在达到容量天花板前就该停止加仓。**与本项目对齐**：① [31 号仓位算法](31_position_sizing.md) 的 8% 单票上限是**风险约束**非**容量约束**——打板策略（24 号）单票容量极小，应按 `Q_max = 4/9·Q*` 估算策略级容量天花板；② [55 号监控](55_monitoring_review.md)（⚠️draft 骨架待讨论）Decay Detection 第 4 监控点"Execution cost drift"正是容量饱和信号。**裁定**：MVP 阶段不实施容量理论形式化（打板容量天然受限，8% 已足够保守）；**记为 Phase 2 候选**——升级条件：单策略 AUM > 50 万 或 实际冲击成本持续 > 回测假设 1.5× 时触发评估。
   - **Edge Decay 五骑士分类法 + 实证数据**（[smartfinancedata 2026-08](https://www.smartfinancedata.com/is-your-trading-edge-fading-signs-of-historical-edge-decay/) 127 策略追踪）：策略衰减五种根因机制按影响占比排序——

     | 衰减骑士 | 影响占比 | 机制 | 经典案例 |
     |---|---|---|---|
     | **① Crowding 拥挤** | 41% | 资本涌入→信号被套利→价差压缩 | Monday Effect 1980s 发表后 1990s 消失 |
     | **② Regime Change 状态切换** | 28% | 市场结构/波动率 regime 变化→策略设计前提失效 | Carry Trade 2008 危机后零利率崩溃 |
     | **③ Overfitting 过拟合** | 18% | 原本无 edge，回测拟合了噪声→OOS 必然失败 | 参数 >7 / Sharpe >2.5 / 规则任意 |
     | **④ Technology Evolution 技术演进** | 9% | 执行速度提升/价差压缩→依赖慢扩散的策略被套利 | Post-Earnings Drift 从周级压缩到小时级 |
     | **⑤ Regulatory Change 监管变更** | 4% | 规则变更（卖空/保证金/涨跌停）→策略变非法或不实用 | 2007 SEC 取消 uptick rule |

     **关键实证**：83% 策略 18 个月内失效；中位失效时间 14.3 个月；性能半衰期 11.2 个月；仅 8% 存活 3 年。**用途**：退役诊断按五骑士分类归因——不同根因对应不同应对（crowding→换策略/regime→等回归/overfitting→回孵化重做/technology→降级或退/regulatory→退），而非笼统"策略失效"。
   - **IC by forward horizon 衰减剖面**（[alphanume 2026-06-03](https://www.alphanume.com/blog/what-is-signal-decay)）：在 1d / 5d / 21d / 63d 多前瞻窗口计算 IC 绘制衰减剖面。**两种信号衰减尺度**：① intra-signal horizon decay（单次观测内预测力衰减，决定最优持仓周期与换手频率）；② secular alpha decay（策略级长期侵蚀，McLean-Pontiff 实证发表后异常收益显著衰减）。half-life 描述宏观趋势指导"何时退役"，IC-horizon 描述微观结构指导"持仓多久/换手多频繁"。**mismatch 风险**：换手频率与实际 IC 衰减率不匹配是最常见且最昂贵的实施错误。
   - **Bootstrap IC 半衰期置信区间**（[quantskills/skill-factor-decay 2026-07-16](https://github.com/quantskills/skill-factor-decay)）：多期限 Rank IC 衰减曲线 → 指数/幂律/双指数三模型 AIC 选优 → **Bootstrap 1000 次重采样得半衰期 95% CI**（避免单点估计过度自信）→ 换手衰减 + Q5-Q1 分组收益交叉验证 → 推荐最优再平衡频率。半衰期 CI 下界 > 持仓周期则换手过频（成本浪费），CI 上界 < 持仓周期则换手不足（alpha 流失）。
   - **FSI 拥挤度量化指标**（[CSDN WorldQuant 2026-06-04](https://wenku.csdn.net/column/h4wn2p5dhgm)）：因子收益对市场基准回归，滚动残差 R²，`FSI = 1 - mean(rolling_R²)`。**FSI < 0.4 表明因子已被市场充分消化**——某动量因子 2020-03 流动性危机 FSI 从 0.68 骤降至 0.31，预示后续 11 个月失效期。FSI 是五骑士 ① Crowding 的量化先行信号。实施：滚动 60 日 OLS + 残差 R²，<30 行代码。
   - **策略类型衰减速度经验表**（smartfinancedata 127 策略）：简单直觉模式最易被发现和套利故衰减最快，复杂多因子存活最久——

     | 策略类型 | 中位存活 | 1 年失败率 | 主要衰减根因 |
     |---|---|---|---|
     | 简单技术形态 | 8.2 个月 | 79% | Crowding |
     | 动量策略 | 11.4 个月 | 71% | Crowding |
     | 均值回归 | 13.7 个月 | 64% | Regime Change |
     | 季节性/日历效应 | 15.9 个月 | 58% | Crowding |
     | 波动率套利 | 19.3 个月 | 52% | Technology |
     | 统计套利 | 24.1 个月 | 43% | Crowding |
     | 多因子模型 | 28.6 个月 | 35% | Regime Change |

     **与本项目对齐**：打板策略（24号）属"简单技术形态"类，预期中位存活 ~8-12 个月，须按此节奏规划迭代；多因子策略（25号）属"多因子模型"类，预期 ~24-28 个月。
   - **AI 不是 alpha 衰减的解药**（[CSDN 2026-08-07](https://blog.csdn.net/2601_95872481/article/details/162839541)）：AI/ML 策略同样受衰减宿命制约——① AI 学历史模式受"过去不代表未来"限制；② AI 过拟合**更隐蔽**（黑箱使过拟合更难察觉）；③ AI 策略拥挤 = 新的 crowding 衰减；④ AI 无"自主进化"，该退就要退。**本项目纪律**：Champion-Challenger + Drift Observatory + Decay Detection 三件套**同等适用于 AI/ML 策略和非 AI 策略**——AI 策略不因"更先进"而豁免退役标准。**策略失灵是默认假设非意外**（市场效率定理直接推论）——系统健康 = 失灵了能识别/切换/恢复，不是"永远不失灵"。
6. **防遗忘**（BM-MT-05-A）：EWC + 伪回放，新模型适应新分布又不丢历史知识。
7. **自动回滚机制**：新 Champion 上线后旧 Champion 保留 7-30 天作为回滚安全保险（[icyfenix.cn](https://ai.icyfenix.cn/ai-infra-engineering/mlops/model-lifecycle.html)）；部署后 24 小时内监控检测到显著指标 drop → 自动回滚到旧 Champion（[kindatechnical 2026-03](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)）；一键回滚 = 切换 MLflow alias @champion 指针 + 告警。**回滚触发阈值表**：

   | 指标 | drop 幅度 | 持续时长 | 触发动作 | 来源 |
   |---|---|---|---|---|
   | **实盘 Rolling Sharpe** | < 旧 Champion 同期 × 0.5 | 连续 3 个交易日 | 立即回滚（MLflow alias 切换） | 晋升门禁第 9 条对齐 |
   | **ECE 校准误差** | > 旧 Champion × 1.5 | 连续 3 个交易日 | 立即回滚 | MetricGate A/B 双指标纪律 |
   | **最大回撤** | > 旧 Champion MaxDD × 1.3 | 单日突破 | 立即回滚 + 风控告警 | 护栏指标 guardrail |
   | **MAPE 预测误差** | > baseline × 1.3 | 连续 3 天 | 回滚评估（人工审批） | 重训练触发第 8 条对齐 |
   | **订单拒绝率** | > 5%（正常 <1%） | 连续 1 日 | 立即回滚 | 执行层护栏 |
   | **护栏指标**（换手率/滑点偏离） | 任一超限 | 即时 | 立即终止实验 | MetricGate guardrail |

   **回滚 vs 重训练边界**：回滚是"新 Champion 上线 24h-7 天内的紧急恢复"（切回旧 Champion，新 Champion 落 @challenger 待诊断）；重训练是"Champion 长期退化"（第 8 条，保留 Champion 但触发再训练）。回滚是即时动作（秒级 alias 切换），重训练是离线动作（盘后训练）。
8. **重训练触发三策略**（[kindatechnical 2026-03](https://kindatechnical.com/time-series-analysis/automated-retraining-and-model-selection.html)）：
   - **定时**（schedule-based）：固定周期重训练（如盘后每日/每周），适合数据量大、更多数据持续改善预测的场景
   - **性能**（performance-based）：监控检测到模型退化超阈值才触发（如 MAPE 退化 1.3x baseline 连续 3 天），更高效但需健壮监控
   - **数据量**（data-volume-based）：新数据累积到一定量（如 10000 行）才重训练，适合数据到达不规律的场景
   - 个人项目默认用**定时+性能双触发**：定时保底（盘后每日重训练），性能触发加速（退化时提前重训练不等定时窗口）
9. **晋升门禁量化指标**（[PMTS 2026-06](https://pmts.elysiumdubai.net/blog/machine-learning-model-retraining-adaptive-ai-trading-pmts-2026-06-18/)）：新模型不自动替换 Champion，须在 OOS 数据上通过量化门禁：
   - **最低 OOS Sharpe**：不低于 Champion 当前 Sharpe × 0.9（允许略低但不可崩塌）
   - **profit factor 下限**：>1.5（总盈利/总亏损，低于此则策略无正期望）
   - **最大回撤上限**：不超过 Champion 当前 MaxDD × 1.2
   - **子周期一致性**：不依赖少数大交易——将 OOS 期间分 3-4 子段，每段 Sharpe 均 >0（避免"一笔暴利掩盖整体平庸"）
   - **Sortino + Calmar 辅助**：下行波动率调整收益 + 回撤调整收益，与 Sharpe 三角验证
10. **滚动数据窗口**（[PMTS 2026-06](https://pmts.elysiumdubai.net/blog/machine-learning-model-retraining-adaptive-ai-trading-pmts-2026-06-18/)）：训练数据用滚动窗口而非无限增长归档——旧观测降权或丢弃，模型优先学习当前活跃 regime；同时保留更长参考窗口记忆罕见但反复出现的压力事件。结果：模型当前但不失忆（current without being amnesiac）。
11. **数据/特征版本管理 + 模型血缘**（[mlflow.org 2026-06-15](https://mlflow.org/articles/ml-lifecycle-management-explained-for-engineers/)）：§3.2 第 3 条可复现性四要素的机制落地。**数据版本化**：训练数据集用内容哈希（content hash）或 DVC 标记版本，每次重训练记录 `dataset_version` → MLflow run params。**特征版本化**：Feature Store 特征定义作为 versioned artifact，防止 training-serving skew（生产故障最常见根因之一）。**模型血缘**：MLflow Model Registry 每个 model version 携带指向 `training_run_id` + `dataset_version` + `code_commit` 的指针，支持从生产模型反查训练数据与代码。**审计场景**：策略异常时从 @champion alias 反查 → training_run → dataset_version → code_commit → 定位数据/代码/模型问题。**个人项目实现**：MLflow 已内置 params/tags/artifacts 追踪；数据版本用文件 hash + git submodule 管理（不上 DVC/LakeFS）。

**行业对标（2026）**：
- Champion-Challenger 是 2026 模型晋升标准模式（[icyfenix.cn](https://ai.icyfenix.cn/ai-infra-engineering/mlops/model-lifecycle.html)、[PAASUP 2026-06](https://ideas.paasup.io/global/mlops-pipeline-en/)）；MLflow alias 生命周期：@champion / @challenger / @archived；MLflow 2026-06 生命周期管理为 8-10 阶段循环，governance 是全管线属性非末端检查点。
- **监管引用更新**：原 SR 11-7（2011）已于 **2026-04-17 被 SR 26-2 / OCC Bulletin 2026-13 正式替代**（[Federal Reserve SR 26-02](https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf)、[risktemplate.com 2026-06-10](https://risktemplate.com/blog/2026-06-10-occ-bulletin-2026-13-model-risk-management-sr-11-7-what-changed/)）。三大变化：①Risk-based proportionality 替代 implied annual cadence；②简化 validation framework（保留 conceptual soundness + outcomes analysis + ongoing monitoring 三核心）；③弱化 independence 强调。**GenAI 被显式排除在范围之外**。**个人项目定位**：非监管对象（资产 <30B），但 SR 26-02 三核心纪律仍可借鉴为模型治理基线——恰与本项目 Champion-Challenger + 晋升门禁量化 + Decay Detection 5 监控点对应。
- **2026-08 金融非平稳性综述**（[Neurocomputing 2026-08-02](https://m.ebiotrade.com/newsf/2026-8/20260802000456268.htm)）：统一 structural breaks / regimes / concept drift / dataset shift 术语体系——本项目漂移检测 + regime 检测器 + Decay Detection 三件套正是该综述"漂移感知表征 + 变化检测 + 持续适应"三支柱落地。
- **EU AI Act 2026-08-02 强制执行**：高风险 AI 系统（含金融信用评估/交易算法）**上市后监测义务正式强制执行**——须建立持续监测机制检测并响应性能衰减与漂移。本项目 Drift Observatory + Decay Detection + 重训练触发机制已满足其技术要求；个人项目非 EU 市场主体无强制合规义务，但这些纪律是"合规级"治理基线，未来扩展机构合作或海外市场可平滑对接。

**MLOps 成熟度定位**（[ML-OS/MLOps.md](https://github.com/rohanmistry231/ML-OS/blob/main/MLOps.md)）：
- **Level 0**（手动）：人工训练→人工部署→无监控——**拒绝**（模型是活系统，不是一次性交付物）
- **Level 1**（训练管线自动化）：自动化训练流水线，但手动部署——**起步阶段**
- **Level 2**（CI/CD 自动化）：自动化训练+部署+监控+回滚——**个人项目目标**（MLflow alias + 手动审批门禁 + Champion-Challenger + 自动回滚 + 漂移检测）
- **Level 3**（CI/CD+元学习）/ **Level 4**（自适应：自动重训练 + multi-armed bandits + Champion-Challenger 持续运行）——远期演进（Level 4 触发：策略数 >5 且手动管理成负担时）
- **定位结论**：个人项目当前处于 Level 1→Level 2 过渡，BM-MT-02-A/B 灰度+影子+对抗鲁棒性施工完成后达成 Level 2。

**个人项目简化**：不上 KFP/KServe/K8s 编排；用 MLflow Model Registry alias 管理生命周期 + 手动审批门禁。BM-MT-02 已有 ExperimentTracker（stable），BM-MT-02-A/B 设计态待施工。

**模型训练两环节裁定**：

1. **BM-MT-01-B AI 辅助代码生成与分析师 Agent 反馈**（battle_map 标 production，实际仅 AST 沙箱落地）→ **登记裁定：生成-反馈闭环并入 §3.2 远期候选**。定位：ModuleRequirementSpec→LLM 生成→Critic 审查→反馈收敛→AST 沙箱→人工审核注册。裁定：Generator/Critic/Judge 生成-反馈闭环 + 分析师 Agent 与 §2.3"不做 agent 编排系统"约束冲突，并入 §3.2 LLM 驱动 alpha 挖掘远期候选（Hubble/EvoQuant 已登记同类范式，Phase 5+ 重评）；**安全栈已落地**——[62_business_registry_construction](62_business_registry_construction.md) §4.34② factor_registry schema `llm_safety_stack` 5 字段（ast_validation/dsl_constrained/complexity_control/dual_channel_rag/family_aware_selection）已承载 Hubble AST 验证沙箱契约，Phase 2+ 启用 LLM 因子生成时 MUST 声明全 true。同时登记**battle_map 成熟度标注倒挂真源修正建议**：BM-MT-01-B 标 production 但 `ml_train/ai_operator/` 仅 AST 沙箱部分落地、生成-反馈闭环未施工，成熟度应 production→design，写入 §7.5 由 battle_map owner 会话裁决。
2. **BM-MT-01-C 策略数字孪生**（design）→ **裁定不做镜像副本**。裁定：不建策略行为镜像副本——"策略健康评估+衰减预警"诉求已由 §3.9 退役 8 维量化阈值 + §3.3 Drift Observatory 五类漂移四层架构完整承载，镜像副本属重复建设且单机维护实时镜像仿真成本高。**与 #ARCH-OE-010 边界消歧**：#ARCH-OE-010 裁的是 SIM 域数字孪生 + 世界模型 DreamerV3（市场仿真侧，BM-SIM-05 已降级），本环节是策略行为镜像，两者正交——本裁定不触碰 SIM 域既有裁定。重评条件：策略数 >10 且 8 维阈值+Drift Observatory 出现系统性误报/漏报时。
### 3.4 回测阶段（BM-BT）规范
承接 [battle_map_03_backtest_validation](../battle_map/battle_map_03_backtest_validation.md)（BM-BT-01~07 环节视图）+ [52_backtest_framework_docking](52_backtest_framework_docking.md)（⚠️G23 设计备忘 draft v0.1.0 骨架待讨论——回测门控 why 层未定稿；IS→WFA→OOS 门控当前真源为代码 `src/zephyr/backtest/core/decision_gate.py`）。本节锁定生命周期视角的回测准入门禁与退出条件。

**核心纪律**：
1. **IS→WFA→OOS 三段式门控**（battle_map_03 BM-BT-01~07 + 代码 `decision_gate.py`）：In-Sample 训练 → Walk-Forward Analysis 滚动验证 → Out-of-Sample 样本外验证，三段全过才准入模拟阶段。**WFA 是核心**——固定参数 IS 训练 + 滚动窗口 OOS 验证，模拟"参数不知道未来"的真实场景，防止参数过拟合。
2. **过拟合检测三维度**（battle_map_03 BM-BT-05 + [kagels-trading 2026-08-01](https://www.kagels-trading.de/trading-edge/)）：
   - **Deflated Sharpe Ratio**（DSR）：调整回测 Sharpe 反映"多次试错后的最佳结果"（multiple testing penalty），DSR 仍显著 > 0 才算真 edge（与 §3.3 第 4 条漂移检测的 DSR 鉴别复用同一方法）
   - **PBO（Probability of Backtest Overfitting）**：Combinatorially Symmetric Cross-Validation 计算"过拟合概率"，PBO > 50% 则策略大概率过拟合（11号文档已降级为 perturbation PBO 替代）
   - **参数稳定性**：邻近参数产生相似结果（非孤立最优），若轻微调参就性能剧变 = 过拟合
3. **PIT 铁律继承**：回测特征必须用 §3.2 第 1 条 PIT 正确特征（AS OF JOIN + Embargo），无 PIT 特征禁止入回测——这是回测可信的硬底线。
4. **现实成本注入**：回测必须注入现实交易成本（滑点 + 佣金 + 冲击成本 + 涨跌停限制 + T+1 约束），不注入则回测 vs 实盘 reality gap 巨大。

**退出条件**（准入模拟阶段）：IS→WFA→OOS 全过 + 过拟合三维度通过 + Deflated Sharpe 显著 + 现实成本注入后 OOS 仍正期望。任一未过 → 回 §3.2 孵化阶段重新假设。
### 3.5 模拟阶段（BM-SIM）规范
承接 [battle_map_04_simulation_validation](../battle_map/battle_map_04_simulation_validation.md) + [53_simulation_live_path](53_simulation_live_path.md)（三阶段迁移 + 4 级 Kill Switch + Alpha Decay，active）。本节锁定生命周期视角的模拟准入门禁与退出条件。

**核心纪律**：
1. **paper → shadow → live 三阶段迁移**（53 号）：paper trading（虚拟撮合，验证逻辑）→ shadow mode（实盘行情 + 虚拟撮合，验证信号）→ live trading（实盘小额，验证执行）。每阶段有独立退出条件。
2. **sim↔实盘 divergence 监控**：模拟阶段核心指标是"模拟 vs 实盘"偏离度——若模拟环境与实盘环境差异过大（如撮合逻辑不同、行情延迟不同），则模拟通过不等于实盘能通过。divergence 阈值：成交价偏离 < 0.2%、成交时延偏离 < 1 tick、持仓偏离 = 0（持仓不一致 = 严重 bug）。
3. **模拟时长达标**：模拟须持续足够时长覆盖至少 1 个完整 regime 周期 + 至少 30-50 笔模拟交易（与 §3.3 第 2 条影子模式持续时长量化对齐）。模拟时长不足 → 统计显著性不够 → 不准入实盘。
4. **4 级 Kill Switch**（53 号）：模拟阶段须配置 4 级 Kill Switch（策略级/组合级/系统级/手动级），任一触发立即停止模拟。模拟阶段是验证 Kill Switch 本身可靠性的最后机会——上线后发现 Kill Switch 失效是灾难。

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
5. **并发文件级冲突纪律——队列+worktree 双层**（#ARCH-WORKTREE-GATE-001；升硬口径 2026-08-29，66 号 §10 P1/§12 #2）：多会话并发施工共享主工作区 git index——未 commit 到分支的修改随时可能被并发会话的 stash/reset/checkout 抹掉（**未落分支的修改不算完成**）。**第一层=提交队列串行化**（66 号，MVP 已验收生产在跑）：改完立即入队（AGENTS.md §10.0 铁律），会话提交=快照入袋即返回，落盘由单写者 Serializer 在专用 worktree 内经 GitCommitGateway 全门禁完成，会话不再直接 commit。**第二层=worktree 强制（队列落地后可达）**：①Edit 前先 `python scripts/git_commit.py --claim-only` 前移声明持有（搭便车防护）；②WORKTREE-REQUIRED gate 只管 Serializer 专用 worktree 之外的会话直接 git 操作——检测到其他活跃 session 时阻断主工作区 commit，须 `python scripts/session_worktree.py create/exec/merge` 物理隔离（本备忘 v2.11.0 修订即经此流程落地；裸 git commit 仍被 GATE-COMMIT-GW 阻断）。**行业背书**（2026-08）：CMU CAID（[arXiv:2603.21489](https://arxiv.org/pdf/2603.21489)，2026-03）实证 branch-and-merge + git worktree 是多 agent 协作的核心协调机制（PaperBench +26.7% / Commit0 +14.3%）；VS Code 2026-08-07 起为 Copilot/Claude/Codex agent session 默认启用 git worktree 隔离（[luonghongthuan 2026-08-10](https://luonghongthuan.com/en/blog/vscode-copilot-agent-worktree-isolation-2026/)）——"并发 agent 未提交修改被静默覆盖"是 2026-08 行业公认失败模式，worktree 隔离是其标准解法。

**运行时风险治理小节**（多会话 AI 开发模式下的 AI/Agent 行为治理两环节设计）：

> 本项目"多 AI = 人调度多会话"（§3.6），AI 会话经 git/脚本/depgraph 工具链作用于代码库与文档库。**定位**：AI 行为运行时风险治理是"人调度"模式的必要配套——会话产出物须在有界自治边界内运行，越界即熔断；不改变"AI 间不直接通信、所有交接落盘"既有纪律，在其上加运行时护栏。

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
- **骨架先行工作流**（00_index v2.3.0，2026-08-09）：design_memos 骨架先行（最新篇数台账以 00_index §0 目录为准；frontmatter status=draft，仅含 §1 主题组信息 + §7 讨论要点清单）。工作流：先逐篇讨论填空（骨架→active）再施工对应模块
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
| **Rolling Sharpe** | 滚动 100+ 笔交易 Sharpe < 0 持续 2 个独立窗口（30-50 笔早期预警，100+ 笔确认） | §3.3 第 5 条 Decay Detection |
| **Drawdown 超历史** | 实盘 drawdown > 回测历史最大 drawdown × 1.5（超 50% 即须调查；1.5x-2x prior realized maximum） | Drawdown Protocol 联动 |
| **Profit factor** | profit factor 滑向 1.0（盈亏平衡）持续 2 个独立窗口（从 1.5-2.0 滑向 1.0，扣现实成本后） | 晋升门禁量化指标复用 |
| **Win rate + expectancy 同时下降** | 胜率下降 10-15 个百分点 + 平均交易 expectancy 同时恶化（back-to-back 窗口） | 滚动窗口监控 |
| **Equity curve 斜率丧失** | equity curve 平台或下降持续数周/数月（非单周） | 净值曲线监控 |
| **Half-life 预测** | 半衰期模型 `α(t) = α₀·e^(-λt)` 预测 alpha 已降至 transaction cost floor 以下（可用半衰期 = `-ln(cost_floor/α₀) / λ`） | §3.3 第 5 条 half-life 数学模型 |
| **Regime 失配持续** | 当前 regime 与策略设计 regime 持续不匹配 + 该 regime 历史回测也表现差 | regime 检测器联动（10号 spec） |
| **逻辑失效（结构性）** | 原始市场前提不再成立（如打板策略遇 2026 量化占比 35%+ + 程序化新规 + 连板炸板率 68%，[24_daban_strategy_detail](24_daban_strategy_detail.md) 已记录） | 人工判断 + 设计备忘登记 |

**退役流程**（与 G26 [55_monitoring_review](55_monitoring_review.md) 联动——⚠️55 号为 draft v0.1.0 骨架待讨论，监控告警 why 层未定稿；退役量化标准当前由本节承载，55 号定型后承接运营侧告警联动）：
1. **触发**：Decay Detection 5 监控点（§3.3 第 5 条）任一持续告警 → 进入"观察"状态（D-SIGNAL-14 状态机映射）
2. **诊断**：跑最近 3-6 个月数据回测 + 检查策略日志 + 对比其他策略（区分"单策略坏"还是"全策略同时坏=regime 切换"）
3. **决策**：按三选一矩阵裁定（Reoptimize / Pause-Cut / Retire）
4. **退役执行**：仓位减半→暂停新建仓→平掉存量→归档到策略归档区（详见下方"策略归档机制"）+ D-SIGNAL-14 废弃审批 + design_memo status 改 deprecated + depgraph build_status 改 retired
5. **复盘**：归因退役原因按**五骑士分类法**（§3.3 第 5 条）分类——① Crowding 拥挤（41%）→ 换策略/降低拥挤度/寻找新 alpha 源；② Regime Change 状态切换（28%）→ 等待 regime 回归或适配新 regime；③ Overfitting 过拟合（18%）→ 回 §3.2 孵化阶段重新假设；④ Technology Evolution 技术演进（9%）→ 降级或退役；⑤ Regulatory Change 监管变更（4%）→ 退役。归因结论沉淀到 90_methodology_open_questions 防止同类策略再被孵化。

**触发式移除纪律**（[quanthedgeai 2026-07-13](https://www.quanthedgeai.com/blog/implementing-a-multi-strategy-portfolio-end-to-end/)）：**"希望不是策略；触发式移除才是"**——防止操作者靠希望持有亏损策略。退役流程须**预定义触发器并在触发时机械执行**，不允许"再观察一下"/"可能是暂时回撤"/"下个月再说"等人为延迟。**心理防线**：操作者面对亏损策略的常见心理陷阱是"沉没成本谬误"（已投入大量研究时间）+ "损失厌恶"（不愿实现亏损）+ "过度自信"（相信会回归）——触发式移除用机械规则消除人为判断的偏差。**触发器实现**：在 G26 监控告警中硬编码退役阈值（§3.9 退役量化阈值表）——⚠️55 号为 draft v0.1.0 骨架待讨论，告警硬编码落地待其定型；当前阈值真源为本备忘本节。阈值触发即自动进入"观察"状态并通知，不允许人工抑制（人工只能审批"延长观察"或"加速退役"，不能"取消退役"）。

**策略归档机制**（修复断裂交叉引用）：原引用"策略墓地（30_multi_strategy §3.1 #8 A/B 并行统计保留）"经核实为**断裂引用**——30 号 §3.1 实际是"Model B 拒绝"不含"A/B 并行统计保留"内容；60 号（跨切清理）§3.1 已将"#8 A/B 并行统计"列为 A 模型消除项**删除**；"策略墓地"一词全局搜索无任何文档定义。退役策略的归档终点须在本节明确定义，不再依赖已删除的 30 号 #8：
- **归档四件套**：① MLflow Model Registry model version 移至 `@archived` alias（与 @champion/@challenger 并列）；② design_memo `status` 改 `deprecated`；③ depgraph `build_status` 改 `retired`；④ 策略产物（PnL 曲线 + 参数快照 + training_run_id + 退役原因五骑士归因）归档到 `strategy_archive/<strategy_id>/` 目录（⚠️设计态：目录未建，待首个退役策略触发时施工——代码核查 2026-08-12 `strategy_archive/` 不存在）
- **保留统计的意义**（替代已删除的"A/B 并行统计保留"）：归档非"丢弃"，保留退役策略的历史表现作为**基准线**——新策略孵化时须对比"是否优于已退役的同类型策略"（如新动量策略须优于已退役动量策略的 PnL 曲线），避免重新孵化已失败的策略模式（与 §3.2 第 2 条"假设驱动"呼应：已退役策略的失败假设不再重复验证）。A 模型定型后无需跨策略 A/B 投票仲裁（30 号 §3.1 #8 已删），但"同类型策略历史基准对比"仍是有价值的归档用途。
- **复活机制**：退役策略归档后不永久封存——若 regime 检测器确认五骑士 ② Regime Change 类退役的 regime 已回归，可经 §3.2 孵化阶段重新评估复活可行性（须重新走训练→回测→模拟→实盘全流程，非直接重启）。

**退役流程 5 步施工伪代码**：

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
- **两者关系**：回撤 Protocol 是"短期防御"，退役是"长期判决"。回撤 Protocol 触发 25% 后若 Decay Detection 5 监控点也持续告警 → 进入退役流程；若 Decay Detection 未告警 → 仅风控降级，策略保留。

**2026-08 量化双杀实证**（[新浪财经 2026-08-06](https://finance.sina.com.cn/stock/zqgd/2026-08-06/doc-inimiqxp4745521.shtml)）：2026年7月 A 股量化遭遇 alpha+beta 罕见双杀——沪深300增强超额 -1.51%、中证500增强超额 -4.54%、**动量因子单月回撤 20 个百分点**（"过去十年都非常少见"）。这是上述退役量化阈值的**实时验证案例**：动量因子单月-20pp 会触发"Drawdown 超历史 ×1.5"和"Rolling Sharpe < 0 持续 2 个独立窗口"两条退役阈值，印证 alpha decay 加速趋势。**AI 加速修正**（[Meng & Chen 2026, arXiv:2605.23905](https://arxiv.org/pdf/2605.23905)）：AI 普及后 alpha 信号半衰期从 5-7 年缩至 18 个月（Alpha Half-Life Theorem `h(φ)=ln2/[θ+δ(φ)]`，当前 φ≈0.7 采纳率时 h≈18 月），§3.3 第 5 条 half-life 模型 `α(t)=α₀·e^(-λt)` 须以 18 个月为基准校准 λ（λ_AI > λ_pre-AI），而非 mathandmarkets 的 20 个月（pre-AI 基准）。
## 4. 考虑过的替代方案
### 4.1 多 Agent 运行时编排系统 —— 拒绝
- **拒绝理由**：30_multi_strategy §5 已暂缓"LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索"——AI 写 AI 的失控风险高，可控性方案（沙箱+审批+回滚）未验证可靠
- 个人项目的"多 AI"是"人调度多会话"（用户开启多个 AI 对话并行推进），不是"agent 自治编排"——不需要 agent 间通信协议、任务调度器、冲突解决器等重型机制；用 design_memo + depgraph path 作为交接点足够（AI 间不直接通信，所有交接落盘可追溯）
### 4.2 企业级 MLOps 编排栈（KFP + KServe + K8s）—— 拒绝
- **拒绝理由**：[PAASUP 2026-06](https://ideas.paasup.io/global/mlops-pipeline-en/) 的 KFP+MLflow+KServe 栈是 Kubernetes 原生企业方案，个人项目无 K8s 集群、无运维团队
- 个人项目简化版：MLflow Model Registry alias（@champion/@challenger/@archived）+ 手动审批门禁 + 本地训练脚本——满足 Champion-Challenger 纪律，无 K8s 运维负担；BM-MT-02 ExperimentTracker 已有 stable 实现，BM-MT-02-A/B 灰度+影子+对抗鲁棒性设计态待施工，不需要 KFP 编排
### 4.3 完整 7 状态机实时编排 —— 简化
- D-SIGNAL-14 Lifecycle Manager 的 7 状态（研发/测试/灰度/生产/观察/废弃/归档）是机构级完整状态机
- 个人项目简化：用 6 阶段（孵化/训练/回测/模拟/实盘/退役）映射 7 状态，状态流转用 design_memo status + depgraph build_status 双字段标记，不建独立的状态机编排服务
- 重评条件：策略数 >5 且手动状态管理成为负担时，考虑建独立 Lifecycle Manager 服务
### 4.4 团队协作平台（Jira/Confluence）—— 拒绝
- **拒绝理由**：个人 + 100% AI 开发无团队，design_memo（why）+ depgraph（what will be）+ 00_index 占用表（分工认领）已覆盖交接需求
- 引入 Jira/Confluence 增加外部依赖与维护负担，且 AI 会话无法直接读写
## 5. 上限定义
### 5.1 系统上限
- **策略数**：3-5 个独立 StrategyBook（30_multi_strategy §4.1 上限）；**生命周期阶段**：6 阶段（孵化/训练/回测/模拟/实盘/退役），映射 D-SIGNAL-14 7 状态
- **多 AI 协作**：人调度多会话，非 agent 编排；交接靠 design_memo + depgraph path
- **模型晋升**（§3.3）：Champion-Challenger + MLflow alias + 手动审批，无 KFP/KServe 编排；渐进流量梯度 5%→25%→50%→100%；自动回滚（6 指标阈值表，24h-7 天窗口）；重训练定时+性能双触发；晋升门禁（OOS Sharpe≥Champion×0.9 / profit factor>1.5 / MaxDD≤Champion×1.2 / 子周期一致性 + Sortino+Calmar 三角验证）；双指标纪律（业务+ML 两项都优于或等于才晋升）+ ECE 校准门控 + mSPRT anytime-valid（e-value/Ville 框架，无偷看惩罚，SR 26-2 频率学派偏好）+ 95/5 blast-radius + 护栏指标 + 预注册假设；影子模式异步架构（fire-and-forget + timeout + 每日对比 5 维度）；演进候选：ASHA+SERPANT 多策略 N 选 K（Phase 2+，策略数 >8）/ SCORE overshoot refund + DPitG 双停止 + RBL 成本收益 FDR（Phase 2+）/ Betting on Bets 随机优势 + 鲁棒序贯设计（Phase 3）/ SBS 维护态 Champion 语义（Phase 1 纪律）/ evalinger futility 事前放弃（Phase 2）
- **漂移检测**（§3.3 第 4 条）：五类漂移四层架构——Layer 1 输入监控（PSI+KS+MMD+Wasserstein；MMD 20 种子基准 FPR=0%/检测率 99.9% 最优，PSI 单独 FPR=39.9% 须配合 MMD）/ Layer 2 预测监控（预测漂移 + CUSUM 残差漂移，重尾/自相关/单窗口三失效 Phase 1 缓解：winsorize+CUSUM 降权+确认窗口+残差输入）/ Layer 3 延迟结果监控（ADWIN 概念漂移 + 标签漂移）/ **Layer 4 可证覆盖层 Conformal Prediction**（有限样本覆盖保证 `P(Y∈Ĉ)≥1-α` 任意分布任意模型；EWMA 波动率归一化 + CUSUM→calibration flush minimax 最优 + BC-ACI 中心纠正双重保护；RWC 对接 36 号 VaR；ConformalNaive mandatory baseline）/ composite drift score 阈值 0.35 + CvM 尾部敏感 + WMAPE 精度层 + MMDEW 流式自相关陷阱 + Benjamini-Hochberg FDR + 下游影响门控 + 分级响应 5 级（0.20/0.40/0.60/0.80）；候选：betting martingale+Conditional CTM+Legendre Jumper+Subgroup Auditing（Phase 3 与 Layer 4 同期）、联合 VaR+ES、DT-GOL（T+1 标签延迟）、CB-PDD、ARM、SHAP 归因、Modular CP、Drift Robustness、Drift2Act、Conformal Abstention、KDD 2026 基准、DTD 动态阈值、COP、ProteuS（Phase 3）/ SA-BCP、CPTC、WCTM、DASC、RLCP、GMM unexplained mass、Decaying-ε-FOCuS（Phase 3-4/4）——全部条目见 §3.3 第 4 条候选登记表
- **衰减检测**（§3.3 第 5 条）：Decay Detection 5 监控点（Rolling Sharpe / Drawdown frequency / Correlation instability / Execution cost drift / Volatility mismatch）+ half-life 指数模型（Maven：美 5.6%/欧 9.9% 年衰减递增；AI 时代 λ 按 18 个月半衰期校准）+ 五骑士分类法归因（Crowding 41%/Regime 28%/Overfitting 18%/Technology 9%/Regulatory 4%）+ IC by forward horizon 衰减剖面（1d/5d/21d/63d）+ Bootstrap 半衰期 95% CI + FSI<0.4 拥挤预警 + 策略类型衰减速度经验表 + AI 不是解药纪律（AI 策略无豁免）+ 农耕心态（信号组合替代皇冠策略）；双曲线衰减（机械因子，Phase 2 候选）+ 策略容量理论 `Q_max=4/9·Q*`（Phase 2 候选）
- **训练数据**：滚动窗口（旧观测降权，保留长参考窗口记忆压力事件，current without being amnesiac）；数据/特征版本化 + 模型血缘（§3.3 第 11 条）
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
| BM-RES-03/08/09 缺失态环节施工 | ✅ 已解决（v2.13.0 §3.2 拍板，闭合明细见 §7.2） | — |
| 企业级 MLOps 编排栈（KFP+KServe+K8s） | 个人项目无 K8s 运维能力 | 团队扩大或模型数显著增加（>10 并行训练） |
## 7. 待定问题
### 7.1 退役标准量化（✅ 已解决，v1.3.0 §3.9 落地）
✅ 已由 §3.9 落地（v1.3.0）：三选一决策矩阵 + 8 维量化阈值表 + 退役 5 步伪代码 + 触发式移除纪律 + 归档四件套；与回撤 Protocol（30_multi_strategy §2.5 风控阈值）边界见 §3.9（短期防御 vs 长期判决）。
### 7.2 BM-RES 缺失态环节的施工优先级（✅ 已解决，v2.13.0 §3.2 拍板落地）
✅ 已由 §3.2 一次拍板闭合（v2.13.0）：03-B/08/09 轻量建设（Markdown+Git+frontmatter）/ 01-C/04/05-A 否定式裁定（不建沙箱/编排/Notebook）/ 10 由 §3.8 4 步承载 / 11 随 08/09 消解；仅余 BM-RES-06-B 论文追踪 Phase 3 远期候选（interim 载体=90/91 号人工文献整合）。
### 7.3 多 AI 会话的上下文交接模板（需人决策）
当前交接靠"认领前置阅读"纪律，但缺少标准化的交接模板。是否需要定义一份"AI 会话交接 brief"模板（包含：前序产出物路径 / 当前状态 / 待决问题 / 不可越的硬约束）？还是依赖 design_memo frontmatter（status/depends_on/related_issues）足够？
### 7.4 00_index 漂移与 52/55 号骨架联动登记（不越界改仅登记）
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
> 凡出处链接已随正文条目内联者（含 §3.2 / §3.3 第 4 条候选登记表全部远期候选、mSPRT/Conformal/退役阈值等主路径来源）不再重复单列；本节仅保留正文未内联的引用。

- [Concept Drift Alarms for Quant Signals](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-alpha-decays)（stockalpha.ai, 2026-02）—— ADWIN 概念漂移；Benjamini-Hochberg FDR 校正；分级响应阶梯 alert→reduce→stop→quarantine→retrain
- [Population Stability Index (PSI)](https://theneuralbase.com/ai-for-finance/learn/advanced/population-stability-index-psi/)（theneuralbase, 2026-04）—— PSI >0.10 调查 / >0.25 材料性漂移；只检测输入分布偏移不检测概念漂移
- [Multi-Method Drift Observatory](https://github.com/Ledger-Lenz/Ledgerlens-data/issues/35)（Ledger-Lenz, 2026-06）—— composite drift score 加权 `0.3×PSI + 0.2×MMD + 0.2×KS + 0.15×CvM + 0.15×concept`，阈值 0.35；CvM 尾部敏感
- [Shadow Deployment: Test ML Models Without Risk](https://atlan.com/know/shadow-deployment-for-ml-models/)（atlan, 2026-03）—— traffic mirroring + phased rollout (shadow → canary → full)
- [How to Detect Model Drift in ML Pipelines](https://www.vectraops.com/content/how-to-detect-model-drift-in-machine-learning-pipelines/download-pdf/)（vectraops, 2026-07-15）—— 漂移三层架构（input → prediction → outcome）；prediction drift / label drift 定义
- [Implementing Data Drift Detection in Production ML](https://www.agencyscript.com/blog/ai-agency-data-drift-detection)（agencyscript, 2026-03）—— 四类漂移定义；prediction drift 是最可见类型
- [Concept Drift Detection in Production: Practical Thresholds](https://llmops.report/posts/concept-drift-detection-in-production/)（llmops.report, 2026-04-27）—— 统计显著性≠业务显著性；downstream impact gating；score distribution collapsing 是漂移信号
- [PSI+CUSUM+WMAPE 三法联合漂移检测](https://blog.csdn.net/wanghaiwen69/article/details/163591186)（CSDN, 2026-08-08）—— WMAPE 整体精度偏离基线 1.5σ 告警
- [EU AI Act Post-Market Monitoring Obligations](https://aioutlooks.com)（aioutlooks, 2026-05-13 + aiunpacker + decodethefuture）—— 高风险 AI 上市后监测义务 2026-08-02 强制执行
- [When Is an Experiment Done](https://github.com/weisberg/knowledge_base_public/wiki/02g.-When-Is-an-Experiment-Done-Decision-Thresholds-Beyond-Statistical-Significance/Home)（weisberg knowledge_base, 2026-02）—— mSPRT/GSPRT 谱系；贝叶斯 Expected Loss / Probability to Be Best 替代范式
- [258 Data Drift Detection Methods](https://mikenguyen13.github.io/ai_in_action/932-data-drift-detection.html)（mikenguyen13, 2026）—— Wasserstein 距离物理释义；比 KS 更敏感于整体分布形状
- [Alpha Decay Detection in Purchased Trading Strategies](https://breakingalpha.io/insights/alpha-decay-detection-purchased-trading-strategies)（breakingalpha, 2025-12）—— Maven Securities：衰减率美国 5.6%/年、欧洲 9.9%/年且递增
- [Alpha Decay](https://positioned.app/traders-glossary/alpha-decay)（positioned.app, 2026-02）—— "金矿心态"→"农耕心态"；portfolio of signals
- [Conformal Prediction for Risk-Aware Position Sizing](https://marketmaker.cc/en/blog/post/conformal-prediction-trading/)（marketmaker.cc, 2026-06-12）—— 有限样本覆盖保证任意分布成立；区间宽度 = 动态风险信号
- [Conformal Prediction: Guaranteed Confidence Intervals for Industrial ML](https://www.bcub3.com/en/blog/conformal-prediction-intervalles-confiance-industrie/)（bcub3, 2026-06-22）—— 唯一提供 finite-sample coverage guarantee 的方法
- [model_monitor: 4-Layer Drift Detection](https://github.com/bonnie-mcconnell/model_monitor)（bonnie-mcconnell, 2026-06）—— Layer 4 = Conformal coverage "Mathematical guarantee, not heuristic"
- [Prediction Intervals and Uncertainty Bounds for Trading Forecasts](https://github.com/suenot/278-prediction-intervals-trading)（suenot, 2026-03）—— interval width = dynamic risk signal → 保守仓位
- [When Your Coverage Guarantee Means Nothing](https://burning-cost.github.io/2026/03/31/optimal-regret-online-conformal-prediction-distribution-drift/)（burning-cost, 2026-03-31）—— ACI 在 step shift 下首半程覆盖 66.7% 严重欠覆盖"飞行盲打"
- [Simultaneous Coverage and Efficiency Guarantee in Online CP](https://arxiv.org/abs/2607.26577)（arXiv:2607.26577, Vaze, 2026-07-29）—— ACI 仅控制有符号覆盖误差；同时控制绝对非抵消违反 + 预测集效率
- [Temporal Conformal Prediction (TCP)](https://arxiv.org/html/2507.05470v5)（Aich et al., 2025-12）—— 滚动 split-conformal + 分位数预测器；S&P 500/Bitcoin/Gold 95% 覆盖验证；危机窗口区间 promptly 扩张/收缩
- [Champion/Challenger Model Evaluation Architecture](https://www.aicassindra.com/blogs/ai/ai_champion_challenger.html)（aicassindra, 2026-07-13）—— segmented significance test 防 aggregate win 隐藏 segment loss
- [Champion vs Challenger: Bank Model Validation](https://www.analyticslane.com/2026/08/04/champion-vs-challenger-como-los-bancos-validan-modelos-nuevos-antes-de-ponerlos-en-produccion/amp/)（analyticslane, 2026-08-04）—— 银行业标准：歧视指标 + 迁移矩阵 + 分段分析
- [E-Values Expand the Scope of Conformal Prediction](https://arxiv.org/html/2503.13050v3)（arXiv:2503.13050v3, Gauthier/Bach/Jordan, 2025-05）—— conformal e-prediction；batch anytime-valid conformal
## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G28 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active：回填全部 6 项讨论要点（6 阶段状态机/BM-RES 规范/BM-MOD Champion-Challenger 规范/多 AI 协作分工/文档治理段位编号/creation_token+depgraph 登记）；新增过度工程审查（§4.1/§4.2） | 策略生命周期总纲定型；明确"多 AI = 人调度多会话"非 agent 编排 |
| 2026-08-10 | 1.1.0-1.9.0 | 九轮施工算法完整性审查：§3.3 纪律扩至 11 条（自动回滚+回滚阈值表/重训练三策略/晋升门禁量化/滚动窗口/数据版本血缘/Drift Observatory 五类漂移/三层→四层 Conformal 架构/composite score/下游影响门控/分级响应/影子异步/双指标+ECE/mSPRT 升级/e-value 谱系/Wasserstein/MMDEW/WMAPE/CUSUM 三失效+Phase 1 缓解/MMD 基准/SHAP/Drift Robustness/BC-ACI/CPTC）+ §3.9 退役量化体系（三选一矩阵+8 维阈值+5 步流程+触发式移除+归档机制）+ §3.1 冷启动 T0/T1/T2 + 第 5 条 half-life/五骑士/IC 剖面/FSI/策略类型表/双曲线衰减/容量理论/Bootstrap CI | 对齐 2026 MLOps+量化交易工程共识最低门槛：回滚/晋升门禁/多方法漂移检测/数学保证层补齐，退役从定性升级为量化 |
| 2026-08-10 | 2.0.0-2.10.0 | 十一轮"选项之外更好的答案算法"+施工伪代码填补：blast-radius/ASHA+SERPANT/LLM alpha 候选 11 篇（QuantaAlpha→AlphaMemo）/mSPRT+四层编排+退役 5 步三段施工伪代码/两悬空 helper（downstream_impact_gate/trigger_retraining）/DT-GOL/CB-PDD/betting martingale/SCORE/联合 VaR+ES/SBS/ARM/DPitG/Betting on Bets/RLCP/FOCuS/Drift2Act/KDD 2026/Conformal Abstention/RBL/evalinger/DTD/COP/鲁棒序贯/Conditional CTM/Legendre Jumper/Subgroup Auditing/WCTM/Conformal Kelly 链路/Report the Floor/CEP/ProteuS/FIDI/DASC/GMM unexplained mass/knowledge distillation/Modular CP/SA-BCP/CPTC——全部完成不过度工程审查登记为 Phase 1-5 候选 | 施工算法闭环（理论→可执行形态）+ 远期候选全登记；"策略墓地"断裂引用同期修复为归档四件套 |
| 2026-08-12 | 2.11.0 | 幻觉引用清除（52/55 号从未离开 draft 骨架，引用改 battle_map_03+代码真源）+ 新增 §2.4 已施工设施盘点（通用规则 #11）+ 版本漂移修复 + 新增 §7.4 登记 | git log 实证 52/55 号 active 版本为 00_index 错标后的连环幻觉；strategy_archive/ 未建 |
| 2026-08-12 | 2.12.0 | §3.6 交接纪律补第 5 条并发文件级冲突纪律（#ARCH-WORKTREE-GATE-001：claim 前移声明+GitCommitGateway 唯一入口+session_worktree 物理隔离）；§3.2 补策略规格产出物承接 | 多会话并发共享 git index，未落分支修改随时被并发会话抹掉；治理设施已存在但备忘未登记则 AI 会话不知情 |
| 2026-08-12 | 2.12.1 | §3.6 第 5 条补行业背书（CMU CAID + VS Code worktree 默认隔离） | "并发 agent 未提交修改被静默覆盖"是 2026-08 行业公认失败模式 |
| 2026-08-12 | 2.12.2 | 过度工程审查零发现 + 一致性去版本化（body 交叉引用全部改稳定 path） | 版本号引用是连环漂移源 |
| 2026-08-12 | 2.13.0 | 作战地图全覆盖补丁：§3.2 研究知识流水线拍板（BM-RES-03-B/08/09 轻量建设）+ 研究环境否定式裁定（01-C/04/05-A 不建/06-B 远期）+ §3.3 训练两环节裁定（BM-MT-01-B/C）+ §3.6 运行时风险治理小节（BM-RC-09/04-F）；§6/§7.2 标记已解决；新增 §7.5 | 作战地图 16 个环节在 61 号 why 层无定位/裁定/契约记录，按"轻量拍板+否定式裁定+远期登记"三模式一次闭合 |
| 2026-08-12 | 2.13.1 | 作战地图环节映射补强——锚定 BM-RES-03-A、BM-RES-10-A | §3.2 末尾补映射块，环节级可追溯 |
| 2026-08-14 | 2.13.2 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001） | §3.2 LLM 远期候选与 §3.3 候选条目由长篇散文折叠为结构化登记表（链接/Phase/触发条件保留）；downstream_impact_gate/trigger_retraining 伪代码折叠为施工规格（阈值与判定逻辑保留）；betting martingale 伪代码折叠为公式规格；§8.3 与正文内联重复的引用去重（链接零丢失）；§9 同日迭代审查行跨度合并；协作规则/状态机/转换条件/裁定/开放问题零丢失 |
| 2026-08-15 | 2.13.3 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-10） | §2.2 核心问题散文要点化；§3.6 运行时治理引言去冗；§6/§7.1/§7.2 已闭合项改一行指针（详情真源 §3.9/§3.2，闭合史见 v1.3.0/v2.13.0 条目）；过程性日期标签清理（"2026-08-10 补充/2026-08-12 补丁"等小节注记，时间线由修订记录承载）；多 AI 协作规则条文/状态机/裁定/BM-XXX/#ARCH-XXX/跨文档链接零丢失 |