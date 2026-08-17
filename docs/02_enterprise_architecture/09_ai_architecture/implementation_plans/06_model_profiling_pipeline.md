---
ttl: permanent
doc_type: architecture_view
title: 模型画像→考试→护照流水线施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.0"
date: 2026-08-17
topic: model_profiling_pipeline
scope: 09_ai_architecture
---

# 模型画像→考试→护照流水线施工图

> 本文定位：模型画像（7 维评测）→ 能力考试（五轴评测）→ 能力护照（CapabilityPassport）→ 任务门控（TaskGate）的完整流水线施工。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | 模型画像→考试→护照流水线 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 自我进化层·模型路由 |
| 依赖 | MOD-INF-034（模型画像器）+ MOD-INF-036（模型能力考试） |
| 优先级 | P1——模型路由是 AI 层核心能力 |
| 状态 | draft（第 1 轮填充完成） |

---

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。AI 层需要「模型路由」能力——把不同任务（因子生成、信号判断、代码修复、文档撰写等）分配给最合适的模型。模型路由的前提是**先知道每个模型擅长什么**，即需要一条「画像→考试→护照→门控」的完整流水线。

当前各环节实测状态（2026-08-17 实测）：

| 环节 | 模块 | 现状 |
|---|---|---|
| 画像（7 维 26 项 benchmark） | MOD-INF-034 ModelProfiler | production，但自动化门禁未开（见 §2.3） |
| 考试（五轴：横/纵/速/幻/稳） | MOD-INF-036 ModelCapabilityExam | production，已产出 10 份护照 |
| 护照（CapabilityPassport） | MOD-INF-034 capability_passport.py | production，HMAC 签名+版本迁移钩子 |
| 门控（TaskGate） | MOD-INF-035 task_gate.py | production，按护照 depth.capabilities pass/fail 拦截 |
| 岗位匹配（JobMatcher） | MOD-INF-036 job_matcher.py | production，required/bonus/幻觉/成本四维加权评分 |
| 任务×模型增量学习 | MOD-INF-034 task_model_learner.py | production，composite_score 算法已落地 |

关键事实：链路各环节的**代码都已存在且标记 production**，但端到端的「自动画像→自动考试→自动发护照→自动门控」闭环**尚未打通**——护照目前靠人工触发考试生成（各护照 exam_timestamp 集中在 2026-05-08 / 2026-06-26 两批），门控消费方（AutoRuntime dispatch / 模型路由）尚未集成。

### 2.2 核心问题

| # | 问题 | 现状分析 |
|---|---|---|
| Q1 | 画像 7 维与考试五轴是否重复？ | 已实测裁定：**互补不重复**，详见 §3.2 |
| Q2 | 护照更新频率？ | 当前无自动更新机制，已裁定为触发式更新，详见 §3.3 |

补充核心问题（填充时新发现）：

- **链路未闭环**：画像/考试/护照/门控四个环节的代码各自 production，但没有自动调度器把它们串成流水线——新模型入库后不会自动考试，考试结果不会自动更新护照，护照不会自动推送门控。这是本文档要解决的主问题。
- **重复代码**：model_profiling/pipeline_routing/ 子包（6 文件）与顶层同名文件功能重叠，疑似早期实验分支，去留待裁定（见 §6 Q3）。

### 2.3 约束条件

1. **硬件约束**：单机 PC 工作站（i7-12700KF / RTX 3090 24GB 显存 <90% / 64GB RAM / 30Mbps 网络），无集群/K8s。考试必须单机串行跑，Deep 模式（2-3h）不能阻塞日常开发。
2. **自动化门禁**：MOD-INF-034 蓝图头部明确「可用 LLM 模型数 ≥3 且 Benchmark 运行次数 ≥50 且模型切换 ≥3 次/周」才允许自动化，并注明"现在不自动化"的理由。当前护照覆盖 ≥3 模型（10 份），但 benchmark 运行次数与切换频率未达标——**自动化条件不满足，只能手动/触发式执行**。
3. **成本约束**：个人资金，云端 API 调用需过 BudgetEnforcer（MOD-INF-024）；MOD-INF-036 蓝图 references 明确"考试消耗 Token 需预算管控"。
4. **治理约束**：AI 生成代码需交叉验证+依赖锁定+自治熔断（system_charter §2 硬边界）；护照带 HMAC-SHA256 签名防篡改（capability_passport.py 实测）。

### 2.4 已施工设施盘点

以下每一行均实测存在（LS/Read/Grep 验证）：

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | src/zephyr/intelligence/model_profiling/ | 18 个 .py 文件：profiler(563行)/exam_orchestrator(1436行)/exam_test_cases(2510行)/capability_passport(489行)/benchmark_suite(429行)/exam_rubric(337行)/exam_checks(326行)/job_matcher(298行)/exam_judge(280行)/task_model_learner(276行)/cli(179行)/model_discovery(178行)/results_writer(176行)/exam_executor(154行)/case_assembler(130行)/provider_data(67行)/deepseek_v4_chat(608行)/__init__(157行) | production |
| 代码模块（重复） | src/zephyr/intelligence/model_profiling/pipeline_routing/ | 6 个 .py 文件，与顶层同名文件功能重叠（如 profiler.py 612 行 vs 顶层 563 行），疑似早期实验分支 | draft（去留待裁定，§6 Q3） |
| 代码模块 | src/zephyr/trading/task_gate.py | TaskGate 任务门控（MOD-INF-035），can_dispatch(model_id, capability) 按护照 depth pass/fail 判定，返回 (bool, reason) | production |
| 数据资产 | data/brain/passports/ | 10 份能力护照 JSON：deepseek-v4-flash(pro)×(thinking/non-thinking) 4 份、deepseek_r1_8b/14b、qwen2.5-coder_14b（含重复命名 qwen2.5_coder_14b）、qwen3-coder_30b、qwen3_8b | production |
| 数据资产 | data/brain/deepseek_v4_exam_results.json、ollama_exam_results.json、v4_pro_exam_results.json | 3 份考试结果原始记录 | production |
| 数据资产 | data/brain/job_matrix.yaml | 岗位匹配矩阵真源（required/bonus/max_hallucination/幻觉维度权重/成本维度） | production |
| 数据资产 | data/brain/quick_profiles/ | QuickProfile 落盘目录（目录存在，passport 引用） | production |
| 数据资产 | data/model_learning/、data/model_profiles/ | 任务×模型增量学习数据目录、画像结果目录（目录存在，内容未逐一盘点） | production |
| 蓝图 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | MOD-INF-034 Model Profiler 蓝图 v2.2.3，含自动化准入门禁 | Active |
| 蓝图 | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md | MOD-INF-036 Model Capability Exam 蓝图 v2.3.5，三级考试模式+九维幻觉+岗位匹配 | Active |
| 测试 | tests/test_model_profiler/、tests/test_job_matcher.py、tests/test_exam_orchestrator.py | 画像器/岗位匹配/考试主控测试（MOD-INF-036 蓝图 §0.1 记载 job_matcher 36 tests） | production |

护照数据结构实测要点（deepseek_r1_14b.json / qwen3_8b.json 样本）：passport_version=1.0.0，含 breadth（横轴 passed/total）、depth（分能力 precision/recall/f1/grade/failure_reason）、speed（P50/P95/P99 延迟）、hallucination（fabrication/inconsistency/refusal）、drift（稳轴，当前样本 tested=false）、recommendations（safe/unsafe capabilities + max_concurrent_tasks + note）。
---

## 3. 设计决策

### 3.1 为什么分四步：画像→考试→护照→门控

**决策**：不把「评测」和「门控」揉成一个模块，保持画像→考试→护照→门控四步流水线。

**理由**：
1. **关注点分离**：画像（MOD-INF-034 profiler.py）关注「跑分排名」——综合评分用于选型排序；考试（MOD-INF-036 exam_orchestrator.py）关注「上岗资格」——每个能力单独 pass/fail，阈值由 DEPTH_THRESHOLDS 按能力硬编码（实测 0.50~0.65 不等）。两者粒度与用途不同，合并会导致评分逻辑臃肿。
2. **护照是稳定数据契约**：CapabilityPassport 是链路中唯一被下游消费的产物，带 HMAC 签名防篡改、带 passport_version 迁移钩子。TaskGate 只读护照，不关心护照由谁产生——上游可独立演进（如 v3.0.5 新增 21 能力、九维幻觉）而不改下游。
3. **门控是最后防线**：即使画像/考试有漏洞，TaskGate 在 dispatch 前按护照拦截——防御纵深原则在模型路由层的体现。
4. **与已有代码对齐**：四步结构与 model_profiling/ 现有模块划分（profiler / exam_orchestrator / capability_passport / task_gate）一致，不是新发明，而是对既有结构的确认。

**考虑过的替代方案**：
- **单模块方案**：一个 ModelEvaluator 同时输出跑分和门禁结论。否决理由：评分与门禁耦合，调阈值需改两处；画像结果无法独立用于选型（不入门禁场景）。
- **多层门控方案**：画像门控+考试门控+运行时门控三层。否决理由：过度工程——单人项目一层 TaskGate 足够，多层门控维护成本远超收益。

### 3.2 7 维 vs 五轴的互补性裁定

**裁定**：画像 7 维与考试五轴**互补**，不重复。画像 = 静态能力基线，考试 = 动态任务表现。

| 维度 | 画像（MOD-INF-034，7 维 26 项） | 考试（MOD-INF-036，五轴） |
|---|---|---|
| 目标 | 跑分排名、选型参考 | 上岗资格、门禁拦截 |
| 粒度 | 模型级综合评分（ModelProfile.average_score/rank） | 能力级 pass/fail（depth.capabilities.{cap}） |
| 内容 | 延迟/吞吐/正确率/幻觉率/质量评分/综合评分 | 横轴覆盖 + 纵轴精度 + 速轴 + 幻轴（9 维）+ 稳轴漂移 |
| 消费方 | 模型选型、成本分析 | TaskGate、模型路由 |
| 触发频率 | 低（模型入库/选型时） | 较高（能力复核/漂移告警时） |

重叠能力（如 code_generate 两边都测）是有意设计：画像给相对排名，考试给绝对资格。冲突时**以考试为准**——门禁不看排名看资格（TaskGate 实测只读 depth.capabilities pass/fail，不读画像评分）。

### 3.3 护照更新策略：触发式更新

**决策**：采用**触发式更新**，不做定时全量重考。触发条件：

1. **新模型入库**：ModelDiscovery 发现新模型 → 触发 Quick 考试（5-8min，MOD-INF-036 蓝图三级模式之 Quick）→ 生成 QuickProfile/临时护照 → 人工确认后转 Standard。
2. **模型版本变更**：Ollama pull 新版本 / API 提供商换版本 → 触发 Standard 考试（20-30min）。
3. **能力漂移告警**：TaskGate 对某模型连续拦截（low_accuracy）次数超阈值 → 触发 Deep 考试复核（2-3h，夜间跑）。
4. **人工触发**：Owner 手动跑考试 CLI（model_profiling/cli.py 已存在，179 行）。

**不考虑定时更新的理由**：个人项目模型数量少（护照 10 份）、变化频率低；MOD-INF-034 蓝图自动化门禁本身就要求"运行次数 ≥50"才允许自动化，当前远未达标；定时全量考试浪费 GPU/Token 预算。触发式与蓝图门禁方向一致。

**远期方向（非本期）**：当 MOD-INF-034 自动化门禁三条件达标后，可升级为「定时+触发」混合模式，宿主按蓝图为 CircadianScheduler hour=6。此为远期工程，不算过度工程。

---

## 4. 施工计划

> depgraph L1 铁律：凡涉及新建模块的步骤，第一步用 apply_depgraph 登记设计态（status=planned），验证通过后最后一步 status planned→production。

### Phase 0：手动跑通链路（当前，无新模块）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P0-1 | 验证 10 份护照可被 TaskGate 正常加载 | TaskGate().load_passports() 返回 10 | 待执行 |
| P0-2 | 验证 safe/unsafe 门控判定符合护照内容 | 实测样本：can_dispatch("qwen3:8b","naming_suggest") → True（护照 pass_=true）；can_dispatch("deepseek-r1:14b","code_generate") → False（护照 pass_=false, failure_reason=breadth_failed） | 待执行 |
| P0-3 | 手动触发一次新模型 Quick 考试，验证护照落盘+HMAC 签名加载 | 新 passport JSON 生成且 CapabilityPassport.load() 不抛 TamperError | 待执行 |
| P0-4 | 盘点 data/model_profiles/ 与 data/model_learning/ 实际内容，回填 §2.4 | 目录内容写入设施盘点 | 待执行 |

### Phase 1：触发式更新闭环（涉及 1 个新模块：考试调度器）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P1-1 | **depgraph 登记**：将「触发式考试调度器」（挂 MOD-INF-036 下）登记到 depgraph 设计态（status=planned） | depgraph 设计态新增条目 | 待施工 |
| P1-2 | 实现新模型入库触发：ModelDiscovery 发现新模型 → Quick 考试 → QuickProfile | 新模型自动产生 QuickProfile 落盘 data/brain/quick_profiles/ | 待施工 |
| P1-3 | 实现门控拦截计数：TaskGate 连续 low_accuracy 拦截超阈值 → 发出复核考试建议（只发建议，不自动跑 Deep） | 拦截日志含触发建议记录 | 待施工 |
| P1-4 | 测试通过后 depgraph status planned→production | depgraph 状态翻转 | 待施工 |

> Phase 1 纪律：触发器只产生「建议/临时护照」，Standard/Deep 考试始终人工确认后执行——对齐 capability_passport.py 头 AI_AUTONOMY=human_gated。

### Phase 2：与模型路由集成（依赖 11_evidence_skill_router.md）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P2-1 | 与 11 号文对齐「护照→路由」接口契约 | 接口字段双方一致 | 阻塞（11 未填充，见 §6 Q4） |
| P2-2 | TaskGate 接入 dispatch 链路（消费方：AutoRuntime/交易决策流水线，按 MOD-INF-036 蓝图 depends_on MOD-INF-035/MOD-GATE_ENGINE） | dispatch 前自动过门控 | 待施工（接口对齐后） |
| P2-3 | JobMatcher 推荐结果接入模型路由决策参考 | 路由日志含 match_score | 待施工（接口对齐后） |

### Phase 3：成本感知（依赖 10_llm_infrastructure.md）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P3-1 | 与 10 号文对齐 LLM 运行时/计费接口 | 接口契约双方一致 | 阻塞（10 未填充，见 §6 Q5） |
| P3-2 | 考试 Token 消耗过 BudgetEnforcer（MOD-INF-024） | 考试执行含预算检查记录 | 待施工（接口对齐后） |
| P3-3 | 路由决策纳入 cost_score（D-MCE-07：成本是维度非硬门，JobMatcher 权重 0.10 已实现） | 路由日志含成本评分 | 待施工（接口对齐后） |

### 接口假设（依赖文档未填充，按降级处理记入开放问题）

**对 11_evidence_skill_router.md 的接口假设**：
- 输入：CapabilityPassport 的 recommendations.safe_capabilities、overall_score、depth.capabilities.{cap}.f1、CostBreakdown.cost_score
- 约束：TaskGate 是路由前置门禁，路由只在 safe_capabilities 交集内选模型
- 产出：task_type → model_id 的路由决策（可结合 task_model_learner.py 的 composite_score 增量学习）

**对 10_llm_infrastructure.md 的接口假设**：
- 考试/画像的 LLM 调用走 10 号文的三层运行时（本地 Ollama 走 llama.cpp+GPTQ INT4，显存 <90%；云端走 API）
- 云端调用过 BudgetEnforcer 预算管控
- 成本数据（price_per_1k）由 provider_data.py 现有 DEFAULT_PROVIDERS 提供，远期可从 10 号文计费接口读取
---

## 5. 不做什么

1. **不做模型训练/微调**：画像只评估现有模型，不涉及训练、微调、LoRA。模型能力提升靠换模型，不靠改模型。
2. **不做分布式评测**：单机评测（本地 Ollama + 云端 API），不建评测集群、不做分布式调度。Deep 模式 2-3h 单机串行可接受（MOD-INF-036 蓝图 references MOD-INF-005 分布式执行仅为参考，非本期施工项）。
3. **不做通用 LLM 评测**：只评测与本项目相关的任务能力（题库 29 道标准题，覆盖代码/摘要/分类/幻觉等能力），不跑 MMLU/GSM8K 等通用 benchmark。
4. **不做定时全量重考**：触发式更新足够（§3.3）；定时自动化属远期，且被 MOD-INF-034 蓝图自动化门禁明确拦截。
5. **不做多层门控**：一层 TaskGate 足够，不加画像门控/运行时门控（§3.1 替代方案已否决）。
6. **不处理 pipeline_routing 子包**：疑似早期实验分支，去留属代码治理范畴，记入 §6 Q3 待 Owner 裁定，本施工图不动它。
7. **不做 100 模型并发容量**：MOD-INF-036 蓝图"目标容量 100 模型并发"是远期愿景，个人项目当前 ~10 模型，并发调度不施工。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|---|---|---|
| Q1 | 模型画像 7 维评测与能力考试五维评测的关系？ | 已裁定 | 互补不重复：画像=静态跑分排名，考试=动态上岗资格；重叠能力冲突时以考试 pass/fail 为准。见 §3.2 |
| Q2 | 能力护照的更新频率？ | 已裁定 | 触发式更新（新模型入库/版本变更/漂移告警/人工触发），非定时。见 §3.3 |
| Q3 | model_profiling/pipeline_routing/ 子包与顶层文件功能重叠，是否保留？ | 待用户裁定 | 实测 6 文件与顶层同名文件高度相似但行数有差异（profiler.py 612 vs 563 行等），疑似早期实验分支。建议确认后删除或合并，需 Owner 决策 |
| Q4 | 11_evidence_skill_router.md 的「护照→模型路由」接口契约 | 阻塞（依赖未填充） | 11 号文尚未填充，§4 Phase 2 接口为假设，待 11 填充后双方对齐；若 11 定义不同，以 11 为准并修订本文 |
| Q5 | 10_llm_infrastructure.md 的 LLM 运行时/计费接口契约 | 阻塞（依赖未填充） | 10 号文尚未填充，§4 Phase 3 接口为假设，待 10 填充后双方对齐 |
| Q6 | data/model_profiles/、data/model_learning/、data/brain/quick_profiles/ 目录内容未逐一盘点 | 待补充 | 目录存在性已实测，内容清单列入 Phase 0 P0-4 执行后回填 §2.4 |
| Q7 | 护照数据时间陈旧（最近一批 2026-06-26） | 待用户裁定 | 现有 10 份护照是否需要在 Phase 0 全部重考刷新？涉及 GPU/Token 预算，需 Owner 决策 |
| Q8 | 本目录文件曾被隔离事件 | 待用户裁定 | 2026-08-17 晚 implementation_plans/ 整目录被移至 .runtime/quarantine/gova_leftover_20260817/（reflog 3c9bb5a60b 记载该批文件因 TTL-METADATA 门禁未收），后已恢复。本文档在恢复后的骨架上填充 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 第 1 轮填充：§2 背景（处境/核心问题/约束/设施盘点，全实测）+ §3 设计决策（四步链路 why/7维vs五轴互补裁定/触发式更新）+ §4 施工计划（Phase 0-3，含 depgraph L1）+ §5 不做什么（7 项）+ §6 开放问题（Q1/Q2 裁定，新增 Q3-Q8） | AI-FILL-06 按指令集填充 |

---

*维护者：AI 架构协调者*