---
ttl: permanent
doc_type: architecture_view
title: 模型画像→考试→护照流水线施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.3.1"
date: 2026-08-18
topic: model_profiling_pipeline
scope: 09_ai_architecture
---

# 模型画像→考试→护照流水线施工图

> 本文定位：模型画像（7 维评测）→ 能力考试（五轴评测）→ 能力护照（CapabilityPassport）→ 任务门控（TaskGate）的完整流水线施工。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)；模型路由消费侧见 [11_evidence_skill_router.md](11_evidence_skill_router.md)，LLM 运行时环境见 [10_llm_infrastructure.md](10_llm_infrastructure.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | 模型画像→考试→护照流水线 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 自我进化层·模型路由（级联控制器，本地/API 分时分任务） |
| 依赖 | MOD-INF-034（模型画像器）+ MOD-INF-036（模型能力考试）+ MOD-INF-035（TaskGate 任务门控，蓝图锚点已对齐 2026-08-18，§6 Q13 已关闭） |
| 优先级 | P1——模型路由是 AI 层核心能力，护照是路由的能力真源 |
| 状态 | draft（v0.3.0：第 2 轮实测纠错 + 10/11 号文接口对齐完成） |

---

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是个人+100%AI 开发的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。AI 层需要「模型路由」能力——把不同任务（因子生成、信号判断、代码修复、文档撰写等）分配给最合适的模型（[00_index.md](00_index.md) §1 自我进化层·模型路由：级联控制器，本地/API 分时分任务）。模型路由的前提是**先知道每个模型擅长什么**，即需要一条「画像→考试→护照→门控」的完整流水线。

当前各环节实测状态（2026-08-18 实测，验证方式见 §2.4）：

| 环节 | 模块 | 现状 |
|---|---|---|
| 画像（7 维 26 项 benchmark） | MOD-INF-034 `profiler.py`（648 行） | production，但自动化门禁未开（见 §2.3） |
| 考试（五轴：横/纵/速/幻/稳） | MOD-INF-036 `exam_orchestrator.py`（1665 行） | production，已产出 **7 份**护照 |
| 护照（CapabilityPassport） | MOD-INF-034 `capability_passport.py`（571 行） | production，HMAC-SHA256 签名+版本迁移钩子 |
| 门控（TaskGate） | MOD-INF-035 `src/zephyr/trading/task_gate.py` | production，`can_dispatch(model_id, capability)` 按护照 depth.capabilities pass/fail 返回 (bool, reason)（蓝图锚点已对齐 2026-08-18，§6 Q13 已关闭） |
| 岗位匹配（JobMatcher） | MOD-INF-036 `job_matcher.py`（351 行） | production，required/bonus/幻觉/成本四维加权评分 |
| 任务×模型增量学习 | MOD-INF-034 `task_model_learner.py`（313 行） | production，composite_score = speed×0.40 + quality×0.35 + consistency×0.25（代码实测） |

关键事实：链路各环节的**代码都已存在且标记 production**，但端到端的「自动画像→自动考试→自动发护照→自动门控」闭环**尚未打通**——

1. 护照靠人工触发考试生成：7 份护照的 exam_timestamp 集中在 2026-05-08（1 份）/ 2026-06-23（3 份）/ 2026-06-25（1 份）/ 2026-06-26（2 份）四个批次，此后近两个月无新护照。
2. 门控消费方（AutoRuntime dispatch / 模型路由）尚未集成：TaskGate 的 `[CONSUMERS]` 头为空，11 号文的级联路由（MOD-MODEL_ROUTER_ORCH）尚在施工计划中。
3. 增量学习矩阵为空：`data/model_learning/task-model-matrix.json` 实测 `matrix: {}`（只有 M1~M7 基准分），说明运行时表现数据尚未回流。

### 2.2 核心问题

| # | 问题 | 现状分析 |
|---|---|---|
| Q1 | 画像 7 维与考试五轴是否重复？ | 已实测裁定：**互补不重复**，详见 §3.2 |
| Q2 | 护照更新频率？ | 当前无自动更新机制，已裁定为触发式更新，详见 §3.3 |

补充核心问题（填充时新发现）：

- **链路未闭环**：画像/考试/护照/门控四个环节的代码各自 production，但没有自动调度器把它们串成流水线——新模型入库后不会自动考试，考试结果不会自动更新护照，护照不会自动推送门控。这是本文档要解决的主问题。
- **重复代码（已裁定合并 2026-08-18）**：`model_profiling/pipeline_routing/` 子包（6 文件，2690 行）与顶层同名文件功能重叠（如 profiler.py 715 行 vs 顶层 648 行、benchmark_suite.py 964 行 vs 顶层 446 行），确认为早期实验分支——已裁定合并：顶层为唯一真源，profiler 上移 6 个公共 API、task_model_learner 上移 3 个 def（纯超集判定，零行为丢弃），消费方已重定向，子包 6 文件删除（commit de393cc0fc，§6 Q3 已关闭）。
- **护照落盘 schema 滞后于代码模型**：代码已有 `CostBreakdown`（cost_score）与 Tool 轴能力阈值（function_calling/tool_chaining），但 7 份落盘护照均无 cost/tool 字段（2026-08-18 Grep 实测）；成本数据目前只记录在考试结果原始文件（`deepseek_v4_exam_results.json` 含 `cost.total_cost_rmb`）。下次 Standard 考试刷新护照时会自然补齐，不单独施工。

### 2.3 约束条件

1. **硬件约束**：单机 PC 工作站（i7-12700KF / RTX 3090 24GB 显存 <90% / 64GB RAM / 30Mbps 网络），无集群/K8s。考试必须单机串行跑，Deep 模式（2-3h）不能阻塞日常开发，只能夜间/空闲时段执行。
2. **自动化门禁**：MOD-INF-034 蓝图头部「AUTOMATION-GATE」明确三条件——可用 LLM 模型数 ≥3、Benchmark 运行次数 ≥50、模型切换 ≥3 次/周——全满足才允许自动化，并注明"现在不自动化"的理由（采样不足无统计意义）。2026-08-18 实测：护照覆盖 5 个模型族 7 个变体（≥3 ✓）；但 `data/model_profiles/` 无有效运行记录（原 24 个 0 字节 `.tmp` 残留已于 2026-08-18 清除，commit de23915d1f；<50 ✗）；模型切换频率无记录（✗）。**自动化条件不满足，只能手动/触发式执行**——这是 §3.3 触发式更新的硬依据。
3. **成本约束**：个人资金，云端 API 调用需过预算门（MOD-INF-024 Budget Enforcer 蓝图；运行时预算预检 BudgetEngine.pre_flight_check 见 10 号文 §2.4）；MOD-INF-036 蓝图 references 明确"考试消耗 Token 需预算管控"。考试成本实测量级：deepseek-v4-flash-thinking 单次考试 `total_cost_rmb=0.056`（3 万 token）——单次便宜，但全量重考 7 变体 ×多轮仍须走预算审批。
4. **治理约束**：AI 生成代码需交叉验证+依赖锁定+自治熔断（system_charter §2 硬边界）；护照带 HMAC-SHA256 签名防篡改，`capability_passport.py`/`exam_orchestrator.py`/`exam_test_cases.py`/`benchmark_suite.py`/`deepseek_v4_chat.py` 头部均为 `AI_AUTONOMY=human_gated`（实测）——考试题库、护照结构、考试主控的改动都需人工批准，本文施工计划全程遵守。

### 2.4 已施工设施盘点

以下每一行均实测存在（2026-08-18，LS/Read/Grep/Get-Content 验证）：

**代码模块**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 画像/考试主包 | `src/zephyr/intelligence/model_profiling/` | 顶层 18 个 .py 文件（合计 12701 行）：exam_test_cases(5408)/exam_orchestrator(1665)/deepseek_v4_chat(666)/profiler(648)/capability_passport(571)/benchmark_suite(446)/cli(432)/exam_rubric(411)/exam_checks(385)/job_matcher(351)/exam_judge(337)/task_model_learner(313)/model_discovery(208)/results_writer(203)/exam_executor(178)/__init__(173)/case_assembler(152)/provider_data(154) | production |
| 代码模块（重复，已合并删除 2026-08-18） | ~~`src/zephyr/intelligence/model_profiling/pipeline_routing/`~~ | 原 6 个 .py 文件（合计 2690 行）与顶层同名文件功能重叠，确认为早期实验分支——已裁定合并：顶层为唯一真源，profiler 上移 6 个公共 API、task_model_learner 上移 3 个 def（纯超集判定，零行为丢弃），消费方（pipeline_orchestrator/integration __init__/5 个测试文件）已重定向，子包 6 文件删除（commit de393cc0fc，790 测试绿，§6 Q3 已关闭） | 已删除 |
| 任务门控 | `src/zephyr/trading/task_gate.py` | TaskGate（MOD-INF-035）：`load_passports()` 加载全部护照、`can_dispatch(model_id, capability) → (bool, reason)` 按 depth.capabilities pass_/failure_reason 判定（no_passport/no_depth_data/capability_not_tested/low_accuracy 四类拒绝原因） | production |
| Quick 模式 CLI | `scripts/quick_profile.py` | Quick 模式入口（--from-passport/--model/--list），MOD-INF-036 蓝图 §0.1 登记 | production |

**数据资产**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 能力护照 | `data/brain/passports/` | **7 份**签名护照 JSON（清单见下表），HMAC 签名+passport_version=1.0.0 | production |
| 考试结果原始记录 | `data/brain/deepseek_v4_exam_results.json`、`ollama_exam_results.json`、`v4_pro_exam_results.json` | 3 份考试结果（数组结构，含 variant/thinking/五轴分数/safe/unsafe 清单/cost 段） | production |
| 岗位匹配矩阵 | `data/brain/job_matrix.yaml` | v1.0.0（2026-06-27）：九维幻觉权重（总和 1.00）+ 成本维度（weight 0.10）+ 6 示例岗位（骨架） | production |
| QuickProfile 落盘 | `data/brain/quick_profiles/` | 1 份：`qwen3_8b.json`（QuickProfile 不带 HMAC 签名，capability_passport.py 实测） | production |
| 增量学习数据 | `data/model_learning/task-model-matrix.json` | `matrix: {}`（空）+ benchmark_baseline（M1~M7 维度，qwen3:8b / deepseek-r1:8b 基准分） | production |
| 画像结果 | `data/model_profiles/` | 原 24 个 `benchmark_*.jsonl.tmp`（2026-07-17 ~ 2026-08-03）0 字节残留**已清除**，results_writer 原子写入已加异常清理（治本加固，commit de23915d1f，§6 Q9 已关闭）；当前无正式 .jsonl | 已清理 |

**护照清单（7 份，2026-08-18 实测）**

| 文件 | model_id | exam_timestamp | overall_grade | overall_score |
|---|---|---|---|---|
| qwen3_8b.json | qwen3:8b | 2026-05-08 | C+ | 0.627 |
| deepseek-v4-flash-thinking.json | deepseek-v4-flash-thinking | 2026-06-23 | B+ | — |
| deepseek-v4-flash-non-thinking.json | deepseek-v4-flash-non-thinking | 2026-06-23 | B+ | — |
| deepseek-v4-pro-non-thinking.json | deepseek-v4-pro-non-thinking | 2026-06-23 | B+ | — |
| qwen3-coder_30b.json | qwen3-coder_30b | 2026-06-25 | B | — |
| deepseek-v4-pro-thinking.json | deepseek-v4-pro-thinking | 2026-06-26 | B+ | — |
| qwen2.5-coder_14b.json | qwen2.5-coder_14b | 2026-06-26 | B | — |

> 覆盖 5 个模型族（deepseek-v4-flash / deepseek-v4-pro / qwen3:8b / qwen3-coder_30b / qwen2.5-coder_14b），其中 deepseek-v4 两个模型族各分 thinking/non-thinking 两个变体。**注意**：无 deepseek-r1 系列护照（v0.2.0 稿误记为存在 deepseek_r1_8b/14b 护照，本轮实测纠正）。

**蓝图与测试**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 蓝图 | `docs/03_modules/_cross_layer/model_profiler/blueprint.md` | MOD-INF-034 Model Profiler v2.2.3：7 维 26 项 benchmark + 任务×模型增量学习 + AUTOMATION-GATE 准入门禁 + 自动化宿主 CircadianScheduler hour=6（远期） | Active |
| 蓝图 | `docs/03_modules/_cross_layer/model_capability_exam/blueprint.md` | MOD-INF-036 Model Capability Exam v2.3.5：五轴考试 + 三级模式（Quick 5-8min / Standard 20-30min / Deep 2-3h）+ 九维幻觉 + 三轨评分 + 岗位匹配 + 29 道标准题（v2.3.2 扩展后全量 127 题） | Active |
| 蓝图 | `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`（MOD-INF-035 登记锚点，v6.0.2） | TaskGate 蓝图锚点**已对齐（2026-08-18）**：task_gate.py 与 test_task_gate.py 头注已对齐 MOD-INF-035+auto_runtime_core 真实路径，`src/zephyr/__init__.py` MOD-INF-002 锚点同修，model_capability_exam 蓝图 3 处不存在的 runtime/task_gate.py 引用已勘正（commit 3bb6651c2f，§6 Q13 已关闭） | 已对齐 |
| 测试 | `tests/model/`（23 个文件） | 关键：test_profiler.py / test_model_capability_exam.py / test_job_matcher.py（蓝图记载 36 tests）/ test_exam_orchestrator.py / test_exam_test_cases.py；另有 test_benchmark_suite.py / test_model_router.py / test_model_drift_detector.py 等（与 11 号文 §2.4 盘点一致） | production |
| 测试 | `tests/budget/test_budget_profile_manager.py` | 预算画像管理测试（考试预算管控的配套） | production |

### 2.5 护照与考试结果数据结构实测要点

**CapabilityPassport**（样本 `qwen3_8b.json` 全文读取）：

- 元信息：`passport_version=1.0.0`、`model_id`、`exam_timestamp`、`exam_duration_seconds`、`git_commit`（当前样本为空串）、`overall_grade`（A+~F 分级）、`overall_score`。
- 五轴：`breadth`（横轴 passed/total/failed_capabilities）、`depth`（纵轴分能力 precision/recall/f1/grade/failure_reason/samples_tested）、`speed`（avg/P50/P95/P99 延迟 + tokens_per_second）、`hallucination`（overall/fabrication/inconsistency/refusal——当前落盘护照为三维幻觉，九维为代码模型已扩展、落盘待下次考试刷新）、`drift`（稳轴，全部样本 `tested=false`——漂移考试从未实际跑过）。
- 建议：`recommendations.safe_capabilities` / `unsafe_capabilities` / `max_concurrent_tasks` / `note`（人读建议，如 qwen3:8b "代码修改类任务建议使用更强模型"）。
- 代码侧补充（capability_passport.py 实测）：`load(model_id, verify=False)`——verify=True 时校验 HMAC 签名，失败抛 `TamperError`；版本迁移钩子 `_migrate_passport_data` 当前为占位实现；`CostBreakdown.cost_score`（0-1，越高越便宜，local 默认 1.0）已建模但未落盘。

**考试结果原始记录**（样本 `deepseek_v4_exam_results.json` 首条读取）：按 variant（模型×thinking 组合）记录五轴分数、safe/unsafe 清单、`cost.total_cost_rmb`（如 flash-thinking 单次 0.056 元 / 30534 token）——成本数据真源目前在考试结果文件，不在护照。

---

## 3. 设计决策

> 按 01 号规范 §4.4 流水线类组织：输入→处理→输出→验证→不做。本流水线：输入=模型清单与题库（§3.1/§3.4），处理=画像+考试两阶段评测（§3.2），输出=签名护照（§3.3），验证=门控拦截+红蓝复核（§3.1 决策 3、§4 Phase 0），不做=§5。

### 3.0 流水线总览

```
┌──────────┐   ┌──────────┐   ┌───────────────┐   ┌──────────┐
│ 画像      │ → │ 考试      │ → │ 护照           │ → │ 门控      │
│ Profiler │   │ Exam     │   │ Passport      │   │ TaskGate │
│ 7维26项   │   │ 五轴三级  │   │ HMAC签名      │   │ pass/fail│
│ (输入处理)│   │ (处理)    │   │ (输出·数据契约)│   │ (验证防线)│
└──────────┘   └──────────┘   └───────────────┘   └──────────┘
 MOD-INF-034    MOD-INF-036    data/brain/passports/ MOD-INF-035
 跑分排名·选型   上岗资格·门禁   7份落盘·下游唯一消费    dispatch前拦截
```

**总决策：四步不合并**（替代方案审查见 §3.1）。画像回答"哪个模型更强"（相对排名），考试回答"这个模型能不能上岗"（绝对资格），护照是两者的稳定数据契约，门控是 dispatch 前的最后防线。

### 3.1 为什么分四步：画像→考试→护照→门控

**决策**：不把「评测」和「门控」揉成一个模块，保持画像→考试→护照→门控四步流水线。

**理由**：

1. **关注点分离**：画像（`profiler.py`）关注「跑分排名」——综合评分用于选型排序；考试（`exam_orchestrator.py`）关注「上岗资格」——每个能力单独 pass/fail，阈值由 `DEPTH_THRESHOLDS` 按能力硬编码（32 项阈值实测 0.50~0.65，默认 0.55）。两者粒度与用途不同，合并会导致评分逻辑臃肿。
2. **护照是稳定数据契约**：CapabilityPassport 是链路中唯一被下游消费的产物，带 HMAC 签名防篡改、带 passport_version 迁移钩子。TaskGate 只读护照，不关心护照由谁产生——上游可独立演进（如 v3.0.5 新增 21 能力、九维幻觉）而不改下游。11 号文 §2.3 已把"护照 Schema 以 capability_passport.py 为准、路由侧不反向修改"固化为依赖锁定条款。
3. **门控是最后防线**：即使画像/考试有漏洞，TaskGate 在 dispatch 前按护照拦截——防御纵深原则在模型路由层的体现。TaskGate 的拒绝语义已细化（no_passport / no_depth_data / capability_not_tested / low_accuracy），便于路由侧区分"没考过"与"考不过"。
4. **与已有代码对齐**：四步结构与 model_profiling/ 现有模块划分（profiler / exam_orchestrator / capability_passport / task_gate）一致，不是新发明，而是对既有结构的确认。

**考虑过的替代方案**：

- **单模块方案**：一个 ModelEvaluator 同时输出跑分和门禁结论。否决理由：评分与门禁耦合，调阈值需改两处；画像结果无法独立用于选型（不入门禁场景，如成本分析）。
- **多层门控方案**：画像门控+考试门控+运行时门控三层。否决理由：过度工程——单人项目一层 TaskGate 足够，多层门控维护成本远超收益。11 号文的 L1 能力门不是新增门控层（是路由内部候选过滤，可降级），与本裁定不冲突（见 §3.6）。

### 3.2 7 维 vs 五轴的互补性裁定

**裁定**：画像 7 维与考试五轴**互补**，不重复。画像 = 静态能力基线（选型参考），考试 = 动态任务表现（上岗资格）。

| 维度 | 画像（MOD-INF-034，7 维 26 项） | 考试（MOD-INF-036，五轴） |
|---|---|---|
| 目标 | 跑分排名、选型参考 | 上岗资格、门禁拦截 |
| 粒度 | 模型级综合评分（ModelProfile.average_score/rank） | 能力级 pass/fail（depth.capabilities.{cap}） |
| 内容 | 延迟/吞吐/正确率/幻觉率/质量评分/综合评分 | 横轴覆盖 + 纵轴精度 + 速轴 + 幻轴（九维）+ 稳轴漂移 |
| 消费方 | 模型选型、成本分析 | TaskGate、模型路由（11 号文 L1 能力门） |
| 触发频率 | 低（模型入库/选型时） | 较高（能力复核/漂移告警时） |
| 产物 | ModelProfile（data/model_profiles/） | CapabilityPassport（data/brain/passports/） |

重叠能力（如 code_generate 两边都测）是有意设计：画像给相对排名，考试给绝对资格。冲突时**以考试为准**——门禁不看排名看资格（TaskGate 实测只读 depth.capabilities pass/fail，不读画像评分）。

### 3.3 护照更新策略：触发式更新

**决策**：采用**触发式更新**，不做定时全量重考。触发条件与动作：

| 触发源 | 检测方式 | 动作 | 考试级别 | 人工确认 |
|---|---|---|---|---|
| 新模型入库 | ModelDiscovery 发现新模型（cli discover 已有枚举能力） | 跑 Quick 考试 → QuickProfile 落盘 quick_profiles/ | Quick（5-8min） | 转 Standard 需人工 |
| 模型版本变更 | Ollama pull 新版本 / API 提供商换版本（人工登记） | 跑 Standard 考试 → 刷新正式护照 | Standard（20-30min） | 是 |
| 能力漂移告警 | TaskGate 对某模型连续 low_accuracy 拦截超阈值 | 发出复核建议（不自动跑） | Deep（2-3h，夜间） | 是 |
| 人工触发 | Owner 手动跑 CLI | 按指定级别执行 | 任意 | — |

**不考虑定时更新的理由**：个人项目模型数量少（护照 7 份）、变化频率低；MOD-INF-034 蓝图 AUTOMATION-GATE 本身要求"Benchmark 运行 ≥50 次"才允许自动化，实测远未达标（§2.3）；定时全量考试浪费 GPU/Token 预算。触发式与蓝图门禁方向一致。

**远期方向（非本期）**：AUTOMATION-GATE 三条件达标后，可升级为「定时+触发」混合模式，自动化宿主按蓝图为 CircadianScheduler hour=6 + FLE `_periodic_checks()`。此为蓝图明示的远期工程，不算过度工程。

### 3.4 阈值与评分设计 why

**决策**：资格判定用「按能力硬编码阈值 + 三轨评分」，不用单一综合分。

- **按能力阈值**：`DEPTH_THRESHOLDS`（capability_passport.py 实测）共 32 项——原 9 能力（0.50~0.60）+ v3.0.5 新增 21 能力（0.55~0.65）+ Tool 轴 2 能力（0.55），默认 0.55（exam_orchestrator.py:413）。高误判代价能力阈值更高（ambiguity_detect/impact_analysis 0.65），低风险的命名/分诊类放宽（0.50）。why：不同能力的误判代价不同，一刀切阈值会让高风险能力漏过或低风险能力误杀。
- **三轨评分**：rubric 轨（`exam_rubric.py`，规则打分）/ executor 轨（`exam_executor.py`，确定性执行比对）/ judge 轨（`exam_judge.py`，LLM/确定性裁判）。why：单一评分轨对代码类任务不可靠（纯规则打不了语义分，纯 LLM 裁判不可复现），三轨交叉是"AI 生成代码需交叉验证"治理约束在考试环节的落地。
- **能力分级**：`compute_grade_simple` A/B/C/D/F（A≥0.75 精通 / B≥0.60 熟练 / C≥0.45 合格 / D≥0.30 初级 / F<0.30 不胜任，job_matrix.yaml 头注实测）——分级供 JobMatcher 岗位匹配消费，pass/fail 供 TaskGate 门控消费，两者不混用。
- **题库边界**：29 道标准题（9 能力 × 3 难度 + OLYMPIAD），v2.3.2 扩展后全量 127 题（23 孤儿激活 + 2 负例对照等），只覆盖本项目任务能力（代码/摘要/分类/幻觉/工具调用），不追求通用 LLM 评测覆盖面（§5）。

### 3.5 幻觉与成本的定位：评分维度，非一票否决

**决策**（沿用 MOD-INF-036 蓝图 D-MCE-07 并确认）：幻觉率与成本均为正常评分维度，不做硬门。

- **幻觉九维**：fabrication(0.20)/inconsistency(0.15)/overclaim(0.12)/context_drift(0.12)/source_confusion(0.12)/instruction_drift(0.10)/refusal(0.08)/format_hallucination(0.06)/quantity_hallucination(0.05)，权重总和 1.00（job_matrix.yaml 实测）。why 九维不三维：落盘护照的三维（fabrication/inconsistency/refusal）区分度不足——"编造 API"和"忘记指令结构"的处置完全不同（前者换模型，后者改 prompt）；九维权重让 JobMatcher 能按岗位容忍度加权（如文档岗容忍 format_hallucination，交易岗零容忍 fabrication）。
- **成本维度**：cost_score 在 match_score 中占 10% 权重（job_matrix.yaml cost_dimension 实测：weight 0.10，free_threshold 0.01 USD / expensive_threshold 1.0 USD）；本地模型≈0 成本，云端按 provider_data.py 定价估算。why 非硬门：claude 贵但必要时仍可用——成本是岗位匹配的考量维度之一，不是否决项；真正的成本硬约束由预算门（MOD-INF-024）在调用前执行，与画像流水线职责分离。

### 3.6 与 11 号文模型路由的边界（已对齐）

11 号文（[11_evidence_skill_router.md](11_evidence_skill_router.md) v0.3.0）已填充，双门控歧义已消除，接口复审结论"部分成立"。本文确认边界：

- **职责边界**：本文管「护照怎么生产/更新」，11 号文管「护照怎么被路由消费」。护照 Schema 真源是 `capability_passport.py`（STABILITY=stable，HMAC 签名），路由侧不得反向修改（11 §2.3 依赖锁定）。
- **双门控不重叠**：TaskGate（本文，dispatch 前最终硬门，不可绕过）vs L1 能力门（11 §3.3，路由内部候选过滤，无护照时可降级静态映射）。前置关系：L1 输出候选集 ⊆ safe_capabilities 交集，TaskGate 对选中模型 pass/fail 兜底——防御纵深，不是重复门控。
- **以本文为真源的待落地项**：护照更新频率（§3.3 触发式）、cost_score 在路由决策中的权重口径（10%，§3.5）——11 号文 §4.6/§6 Q3 已声明待本文落地后修订对齐。

### 3.7 前沿演进方向（2026 年登记，不引入）

按指令集规则 6 检索 2026 年最新实践，登记如下（只登记不施工，已定决策不变）：

| 来源 | 内容 | 对本项目的启示 | 处置 |
|---|---|---|---|
| RouterBench（Martian/Berkeley，arXiv 2403.12031） | 多 LLM 路由系统评测基准，405k 推理结果数据集 | 路由效果可用"性能-成本曲线"系统评估 | 远期可参考其评估方法论，不引入其数据集 |
| Cascade Router（2026-06 白皮书） | C++/ONNX 亚 5ms 预测式路由代理，成本降 75% | 高并发 SaaS 场景的极致延迟优化 | 不引入——单机低频场景无延迟预算压力，Python 级联足够 |
| Cluster-Route-Escalate（arXiv 2606.27457，2026-06） | 两阶段级联：聚类路由+质量估计升级 | 与 11 号文级联路由同构，QE 升级思路可参考 | 登记为 11 号文远期参考 |
| 生产路由三模式（cometapi，2026-08） | 静态规则/级联/预测路由三模式与成本数学 | 静态规则先行、级联补充的渐进路径与本文 Phase 划分一致 | 已对齐，无需变更 |
| 路由策略对比（daddaops，2026-02） | 启发式 68%/嵌入 83%/LLM-judge 91%/级联 88% 准确率对比 | 嵌入路由性价比最高；本项目 EmbeddingRouter（BGE-M3）已存在 | 登记为 11 号文 L2 排序参考 |

共同特征：上述工作均面向**高并发、多租户、强延迟/成本约束**的推理服务场景。本项目是个人单机、日频任务、分钟级延迟可接受——护照+门控+级联路由（11 号文已定）已足够，不引入预测式 ML 路由模型（还需额外训练数据与维护成本，违反过度工程红线）。

---

## 4. 施工计划

> depgraph L1 铁律：凡涉及新建模块的步骤，第一步用 apply_depgraph 将依赖关系登记到 depgraph 设计态（status=planned），验证通过后最后一步 status planned→production。禁止先施工后补登记。

### Phase 0：手动跑通链路（当前，无新模块）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P0-1 | 验证 7 份护照可被 TaskGate 正常加载 | `TaskGate().load_passports()` 返回 7 | 待执行 |
| P0-2 | 验证 safe/unsafe 门控判定符合护照内容 | 实测样本（qwen3_8b.json 已读）：`can_dispatch("qwen3:8b","naming_suggest")` → (True,"ok")；`can_dispatch("qwen3:8b","code_fix")` → (False,"low_accuracy: low_precision_below_threshold")；`can_dispatch("deepseek-r1:8b",...)` → (False,"no_passport") | 待执行 |
| P0-3 | 手动触发一次 Quick 考试，验证 QuickProfile 落盘 | `python scripts/quick_profile.py --model <model>` 生成 quick_profiles/<model>.json；注意 QuickProfile 不带 HMAC 签名（代码实测），转正式护照须跑 Standard | 待执行 |
| P0-4 | 盘点 data/model_learning/ 与 data/model_profiles/ 实际内容，回填 §2.4 | ✅ 已完成（2026-08-18）：model_learning=task-model-matrix.json（matrix 空+baseline M1~M7）；model_profiles=24 个 .tmp 残留；quick_profiles=qwen3_8b.json | 已完成 |
| P0-5 | 验证画像 CLI 可用性 | `python -m zephyr.intelligence.model_profiling.cli history` 能读历史记录（子命令：discover/quick/benchmark/drift/best/history，cli.py docstring 实测） | 待执行 |

### Phase 1：触发式更新闭环（涉及 1 个新模块：触发式考试调度器）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P1-1 | **depgraph 登记**：将「触发式考试调度器」（挂 MOD-INF-036 下）登记到 depgraph 设计态（status=planned） | depgraph 设计态新增条目 | 待施工 |
| P1-2 | 实现新模型入库触发：ModelDiscovery 发现新模型 → Quick 考试 → QuickProfile | 新模型自动产生 QuickProfile 落盘 data/brain/quick_profiles/ | 待施工 |
| P1-3 | 实现门控拦截计数：TaskGate 连续 low_accuracy 拦截超阈值 → 发出复核考试建议（只发建议，不自动跑 Deep） | 拦截日志含触发建议记录 | 待施工 |
| P1-4 | 测试通过后 depgraph status planned→production | depgraph 状态翻转 | 待施工 |

> Phase 1 纪律：触发器只产生「建议/QuickProfile」，Standard/Deep 考试始终人工确认后执行——对齐 capability_passport.py / exam_orchestrator.py 头部 `AI_AUTONOMY=human_gated`（实测）。

### Phase 2：与模型路由集成（11 号文 v0.3.0 已填充，本文作为配合方）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P2-1 | 护照生产接口稳定性确认：11 号文消费的字段（recommendations.safe_capabilities / depth.capabilities.{cap}.f1 / CostBreakdown.cost_score）在下次护照刷新时完整落盘 | 新护照含 cost 段；11 §4.6 字段清单逐一命中 | 待施工（随下次 Standard 考试自然完成） |
| P2-2 | TaskGate 接入 dispatch 链路（消费方：11 号文 MOD-MODEL_ROUTER_ORCH 级联路由 + AutoRuntime，落点 src/zephyr/intelligence/model_routing/ 归 11 号文施工） | dispatch 前自动过门控；TaskGate [CONSUMERS] 头不再为空 | 待施工（11 号文 Phase 1 落地后） |
| P2-3 | JobMatcher 推荐结果接入路由决策参考 | 路由日志含 match_score | 待施工（11 号文 Phase 1 落地后） |

> 本文在 Phase 2 的角色是**接口提供方**：不改护照 Schema 定义权（归 MOD-INF-036 蓝图），只保证字段稳定与刷新及时；路由编排本身（L1 能力门/L2 增量学习排序/L3 成本路由）归 11 号文。

### Phase 3：成本与运行时对齐（10 号文 v0.3.0 已填充）

| 步骤 | 内容 | 验收标准 | 状态 |
|---|---|---|---|
| P3-1 | 考试/画像的 LLM 调用路径登记：本地模型走 OllamaChat（GGUF，10 号文 §3.3 主路径；GPTQ INT4 已实证否决，本文不采用）、云端走 DeepSeekChat/LLMGateway；均带预算预检 | 考试执行路径与 10 号文运行时清单一致 | 待施工（核账性质，工作量小） |
| P3-2 | 考试 Token 消耗过预算门（BudgetEngine.pre_flight_check，src/zephyr/governance/ops_governance/budget_engine.py，10 号文 §2.4 实测；治理蓝图 MOD-INF-024） | 考试执行含预算检查记录；DENY 场景不执行 | 待施工 |
| P3-3 | cost_score 权重口径固化为 10%（D-MCE-07：成本是维度非硬门，job_matrix.yaml cost_dimension.weight=0.10 已实现）——此为 11 号文等待的真源裁定 | job_matrix.yaml 与本文一致；11 号文据以修订 | 已裁定（本文即真源），待 11 修订 |
| P3-4 | 配合 10 号文 Phase 2.4：用本文 exam 链路对 qwen3:8b 跑基线考试，成绩单存档 data/model_profiles/ | 基线成绩落盘（10 号文验收项，本文提供链路） | 待施工（10 号文驱动） |

### 接口契约（与 10/11 号文对齐结论，2026-08-18）

**与 11 号文（护照→模型路由）——已对齐**：

- 消费字段：`recommendations.safe_capabilities`、`depth.capabilities.{cap}.f1`、`CostBreakdown.cost_score`——与 capability_passport.py 实测结构一致（11 §4.6 复审"部分成立"；cost_score 已建模未落盘，随下次考试补齐）。
- 门控语义：TaskGate 是路由前置最终硬门，路由只在 safe_capabilities 交集内选模型；L1 能力门（路由内部，可降级）与 TaskGate 属防御纵深不重叠（§3.6）。
- 本文输出 → 11 输入：task_type → 候选模型集（safe 交集）+ 五轴评分；11 输出：路由决策（结合 task_model_learner composite_score 增量学习）。

**与 10 号文（画像/考试的运行时环境）——已对齐**：

- 本地推理：Ollama 托管 GGUF 量化模型（qwen3:8b 等），显存 <90% 服从时段配额表；**不走 GPTQ INT4**（10 号文 §3.3 实证否决——3090 Ampere 无 INT4 tensor core，单流解码反慢 1.3~2.2×）。
- 云端推理：DeepSeekChat 直连 / LLMGateway；所有调用过 BudgetEngine.pre_flight_check，DENY 即阻断。
- 成本数据：当前由 provider_data.py 的 DEFAULT_PROVIDERS 定价估算 + 考试结果 cost 段实测记录；远期可从 10 号文计费接口（config/model_pricing.yaml 对账后）读取。
- AutoRuntime Core（MOD-INF-035）承担 Ollama 进程生命周期与本地模型栈启动编排——本文流水线不自建进程管理。

---

## 5. 不做什么

1. **不做模型训练/微调**：画像只评估现有模型，不涉及训练、微调、LoRA。模型能力提升靠换模型，不靠改模型。
2. **不做分布式评测**：单机评测（本地 Ollama + 云端 API），不建评测集群、不做分布式调度。Deep 模式 2-3h 单机串行可接受（MOD-INF-036 蓝图 references MOD-INF-005 分布式执行仅为参考，非本期施工项）。
3. **不做通用 LLM 评测**：只评测与本项目相关的任务能力（题库 29 道标准题、扩展后 127 题，覆盖代码/摘要/分类/幻觉/工具调用等能力），不跑 MMLU/GSM8K 等通用 benchmark。
4. **不做定时全量重考**：触发式更新足够（§3.3）；定时自动化属远期，且被 MOD-INF-034 蓝图 AUTOMATION-GATE 明确拦截（实测三条件未全满足，§2.3）。
5. **不做多层门控**：一层 TaskGate 足够，不加画像门控/运行时门控（§3.1 替代方案已否决；11 号文 L1 能力门是路由内部过滤，非新增门控层）。
6. **不处理 pipeline_routing 子包（已闭环 2026-08-18）**：该疑似早期实验分支已裁定合并——顶层为唯一真源，子包 6 文件已删除（commit de393cc0fc），本条目仅保留闭环记录（§6 Q3）。
7. **不做 100 模型并发容量**：MOD-INF-036 蓝图"目标容量 100 模型并发"、MOD-INF-034"目标容量 30-50 模型"均为远期愿景，个人项目当前 ~5 模型族，并发调度不施工。
8. **不引入预测式 ML 路由/独立路由代理**：2026 年前沿（Cascade/ONNX 路由代理、QE 升级分类器等，§3.7）面向高并发服务场景，本项目单机低频不需要；路由排序增强归 11 号文远期。
9. **不做评测平台化**：不做 Web UI/多租户/公开榜单/评测即服务——CLI + JSON 落盘 + 人工触发已满足单人工作流。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|---|---|---|
| Q1 | 模型画像 7 维评测与能力考试五轴评测的关系？ | 已裁定 | 互补不重复：画像=静态跑分排名，考试=动态上岗资格；重叠能力冲突时以考试 pass/fail 为准。见 §3.2 |
| Q2 | 能力护照的更新频率？ | 已裁定 | 触发式更新（新模型入库/版本变更/漂移告警/人工触发），非定时。见 §3.3 |
| Q3 | model_profiling/pipeline_routing/ 子包与顶层文件功能重叠，是否保留？ | **已裁定+已施工 2026-08-18** | 已裁定合并：顶层为唯一真源——profiler 上移 6 个公共 API、task_model_learner 上移 3 个 def（纯超集判定，零行为丢弃），消费方（pipeline_orchestrator/integration __init__/5 个测试文件）已重定向，子包 6 文件删除（commit de393cc0fc），790 测试绿 |
| Q4 | 11 号文「护照→模型路由」接口契约 | 已对齐（2026-08-18） | 11 号文 v0.3.0 已填充：字段接口复审成立、双门控歧义已消除（§3.6）；剩余跟踪项=护照刷新时补齐 cost 段落盘（P2-1）、11 据本文 §3.3/§3.5 真源修订其 §4.6 |
| Q5 | 10 号文 LLM 运行时/计费接口契约 | 已对齐（2026-08-18） | 10 号文 v0.3.0 已填充：本地 GGUF/Ollama 主路径（GPTQ 否决）、预算门 pre_flight_check、10 Phase 2.4 复用本文考试链路跑 qwen3:8b 基线（§4 Phase 3） |
| Q6 | data/model_profiles/、data/model_learning/、data/brain/quick_profiles/ 目录内容盘点 | 已回填（2026-08-18） | 实测完成并写入 §2.4：model_learning=task-model-matrix.json（matrix 空）、model_profiles=24 个 .tmp 残留、quick_profiles=qwen3_8b.json |
| Q7 | 护照数据时间陈旧（最近一批 2026-06-26，距今约 53 天） | 待用户裁定 | 现有 7 份护照是否需要在 Phase 0 全部重考刷新？涉及 GPU/Token 预算（单次云端考试约 0.06 元量级+本地 GPU 时长），需 Owner 决策 |
| Q8 | 本目录文件曾被隔离事件 | 待用户裁定 | 2026-08-17 晚 implementation_plans/ 整目录被移至 .runtime/quarantine/gova_leftover_20260817/（reflog 3c9bb5a60b 记载该批文件因 TTL-METADATA 门禁未收），后已恢复。本文档在恢复后的骨架上填充 |
| Q9 | data/model_profiles/ 下 24 个 .tmp 残留文件 | **已裁定+已施工 2026-08-18** | 24 个 0 字节 .tmp 残留已清除；results_writer 原子写入已加异常清理（治本加固，异常路径不再留 0 字节 .tmp），commit de23915d1f |
| Q10 | 护照落盘 schema 滞后（无 cost/tool 段、幻觉三维 vs 代码九维、drift 全 tested=false） | 已登记（不单独施工） | 代码模型已扩展，落盘待下次 Standard/Deep 考试自然刷新；若 Q7 裁定全量重考则一并解决 |
| Q11 | 00_index.md §5.2 对本文的版本标注滞后 | 已登记（归 AI-FILL-00） | 00_index §5.2 标注本文"draft v0.2.0"，本文已升 v0.3.0；00_index 刷新归 AI-FILL-00 职责，本文不越权修改 |
| Q12 | MOD-INF-036 蓝图自身不一致 | 已登记（不越权修改） | 其 §0.6 file_count 声明 14 vs depgraph 16（蓝图已自标 ❌"以 depgraph 为准"）；MOD-INF-024 蓝图 submodule_path（src/zephyr/governance/budget_engine.py）与实测落点（ops_governance/budget_engine.py）不一致——均属蓝图维护侧待办，本文只登记 |
| Q13 | TaskGate 蓝图锚点悬空 | **已裁定+已施工 2026-08-18** | 锚点已对齐双注册表口径：task_gate.py 与 test_task_gate.py 头注已对齐 MOD-INF-035 + `_cross_layer/auto_runtime_core/blueprint.md` 真实路径，`src/zephyr/__init__.py` MOD-INF-002 锚点同修，model_capability_exam 蓝图 3 处不存在的 runtime/task_gate.py 引用已勘正（commit 3bb6651c2f） |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 第 1 轮填充：§2 背景+§3 设计决策+§4 施工计划+§5 不做什么+§6 开放问题 | AI-FILL-06 按指令集填充 |
| 2026-08-18 | 0.3.0 | 第 2 轮（红蓝对抗纠错+依赖对齐+扩充）：①实测纠错——护照 10 份→7 份（无 deepseek-r1 护照）、18 文件行数全部按 Get-Content 实测更新、tests 路径 tests/model/（23 文件）、pipeline_routing 行数更正；②Q4/Q5 闭环——10/11 号文 v0.3.0 均已填充，接口假设升级为已对齐契约（§3.6/§4 接口契约节），修正"llama.cpp+GPTQ INT4"过时假设（10 号文已实证否决 GPTQ）；③Q6 回填——三个数据目录内容实测入 §2.4；④新增 §3.0 总览/§3.4 阈值与评分/§3.5 幻觉与成本定位/§3.7 前沿演进（2026 登记 5 项）；⑤新增开放问题 Q9~Q13（.tmp 残留/schema 滞后/00_index 版本标注/蓝图不一致/TaskGate 锚点悬空）；⑥P0-4 标记完成、P0 验收样本按实测护照修正 | 第 1 轮数据凭首轮快照未逐条实测，本轮按指令集规则 15/17 全量实测纠正；10/11 号文填充完成消除阻塞 |
| 2026-08-18 | 0.3.1 | Owner 裁定回填+施工事实登记（裁定 3/4/5）：①Q3 关闭——pipeline_routing 子包已裁定合并，顶层为唯一真源（profiler 上移 6 公共 API、task_model_learner 上移 3 def，纯超集零行为丢弃；消费方 pipeline_orchestrator/integration __init__/5 测试文件已重定向；子包 6 文件删除，commit de393cc0fc，790 测试绿），§2.2/§2.4/§5 第 6 条同步更新为已合并口径；②Q9 关闭——24 个 0 字节 .tmp 已清除，results_writer 原子写入加异常清理治本加固（commit de23915d1f），§2.3/§2.4 同步；③Q13 关闭——task_gate.py 与 test_task_gate.py 头注对齐 MOD-INF-035+auto_runtime_core 真实路径，src/zephyr/__init__.py MOD-INF-002 锚点同修，model_capability_exam 蓝图 3 处不存在引用勘正（commit 3bb6651c2f），§1/§2.1/§2.4 同步 | AI-ADJ-004 按 Owner 裁定回填 |

---

*维护者：AI 架构协调者*
