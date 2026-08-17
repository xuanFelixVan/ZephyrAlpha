---
ttl: permanent
doc_type: blueprint
title: AI 执行层施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.0"
date: 2026-08-17
valid_from: 2026-08-17
last_verified: 2026-08-17
topic: execution_layer
scope: 09_ai_architecture
---

# AI 执行层施工图

> 本文定位：AI 执行层的施工——治理 Agent、业务 Agent、算法 Agent、自我迭代 Agent。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | AI 执行层 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 执行层 |
| 依赖 | 自我进化层（[11](11_evidence_skill_router.md)/[12](12_reflexion_multi_agent.md)/[13](13_module_factory.md) 号文）+ 基础设施层（[04](04_autoruntime_core_build.md)/[09](09_llm_security_integration.md)/[10](10_llm_infrastructure.md) 号文） |
| 优先级 | P1——AI 执行层是"AI 对治理、业务、算法自我循环迭代优化"的落地层 |
| 状态 | draft（已填充 v0.2.0） |
| 解锁条件 | U4（自我进化层 11+12+13 就绪）+ U7（交易决策侧 G04 策略定义完成），见 [00_index.md](00_index.md) §5 施工顺序真源 |

---

## 2. 背景

### 2.1 项目处境

[00_index.md](00_index.md) §1 将 AI 执行层定位为"**现有增强**"——四类 Agent（治理 / 业务 / 算法 / 自我迭代）不是四个新建系统，而是对已有能力包的角色化组织。实测（2026-08-17，LS/Grep 验证，明细见 §2.4）：

- **能力组件大量已建且 production**：`orchestrator/agent_orchestrator.py`（MOD-INF-039，多角色 Agent 路由+工具链编排+健康监控，纯内存可注入）、`governance/intelligence_governance/` 25 个文件（含 delegation_engine / model_router / agent_debate / self_benchmark / self_test 等）、`autonomy_core/`（spec_engine MOD-INF-019 蓝图→Skill 升级引擎、phase_planner、self_evolution_fidelity_gate、trigger_router、skills/ 约 60 个技能模块）、`feedback_loop/`（actors/multi_agent_orchestrator、gates/、verifiers/ 评估验证件）、`security/access_control/`（kill_switch.py VR-009 自治熔断器、guards/、detectors/）。
- **四类 Agent 的角色化入口未建**：现有组件按技术域组织（D_ORCHESTRATOR / D_FEEDBACK_LOOP / governance / autonomy_core），没有"治理 Agent / 业务 Agent / 算法 Agent / 自我迭代 Agent"四种角色入口；AI 会话施工时直接面对数十个模块，职责边界靠人肉把握，与 00_index §1 的四类 Agent 图景存在落差。
- **交易决策侧业务载体已就绪**（只读引用）：[20_first_batch_strategies](../../07_trading_decision_architecture/design_memos/20_first_batch_strategies.md)（G04，active v1.3.2，首批 3 策略=打板/多因子/事件驱动）、[30_multi_strategy_concurrency](../../07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md)（G12，active v2.6.1，Model A 独立账本+firm 风险聚合）、[62_business_registry_construction](../../07_trading_decision_architecture/design_memos/62_business_registry_construction.md)（active v1.36.1，18/18 业务注册表已建成，factor 111 条 / strategy 59 条）。
- **自我进化层接口未定型**：[11](11_evidence_skill_router.md)/[12](12_reflexion_multi_agent.md)/[13](13_module_factory.md) 号文截至 2026-08-17 仍为 v0.1.0 骨架（并行填充中）——本文对自我进化层的接口按既有 production 组件（intelligence_governance/model_router、autonomy_core/spec_engine、feedback_loop/verifiers）做保守假设，假设清单入 §6 开放问题，待依赖文档填充后核对。

### 2.2 核心问题

1. **四类 Agent 如何分工？** 治理=gate 检查/规则执行；业务=因子/策略/组合运营；算法=信号/模型/训练实验；自我迭代=评估/优化/反馈。四者与现有技术域包（orchestrator / intelligence_governance / feedback_loop / autonomy_core）的映射关系需要显式定义，否则 AI 会话越权施工、职责漂移。
2. **如何与自我进化层协同？** 执行层是"用手"，自我进化层是"学本事"——执行层消费 11 号模型路由、12 号自反闭环、13 号模块工厂的产出，并把执行结果（gate verdict / 实验指标 / 审计记录）回喂给自我进化层作证据。
3. **如何不违反已定裁定？** [61_lifecycle_multi_ai](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §4.1 已拒绝"多 Agent 运行时编排系统"（AI 写 AI 失控风险高、个人项目无运维能力），本项目的"多 AI"=人调度多会话+落盘交接。四类 Agent 必须在此边界内实现——是角色化薄入口，不是自治运行时。

### 2.3 约束条件

- **system_charter §2 硬边界**（见 [system_charter.md](../04_architecture_principles_decisions/system_charter.md) §2）：①人力=1 人全栈+AI 协作者，代码 100% AI 生成；②硬件=单机 PC（i7-12700KF / RTX 3090 24GB / 64GB RAM），无集群/K8s；③资金与接口=miniQMT 10 笔/秒、Tick=3 秒；④交易规则=T+1、涨跌停、融券受限；⑤运维=单机无热备，交易时段 RTO<5 分钟；⑥范式=AI 生成代码需交叉验证+依赖锁定+自治熔断（置信度低→降级"仅建议"）。
- **61 号备忘裁定**：不做多 Agent 运行时编排系统；AI 间不直接通信，所有交接落盘可追溯（design_memo + depgraph path + 占用表）。
- **30 号文 §5 暂缓项**：LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索暂缓（远期候选，Phase 5+ 重评）。
- **依赖未就绪**：自我进化层（11/12/13 号文）施工完成前，算法 Agent 与自我迭代 Agent 只能做 Phase 0 手动形态。

### 2.4 已施工设施盘点

> 全部路径经 LS/Grep/Read 实测（2026-08-17）；状态以文件头 [MATURITY] 标记或包级实测为准。

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| Agent 编排 | `src/zephyr/orchestrator/agent_orchestrator.py` | MOD-INF-039，多角色 Agent 路由+工具链编排+健康监控，纯内存可注入，不读写 TaskCard.status | production |
| Agent 健康 | `src/zephyr/orchestrator/agent_health_monitor.py` | Agent 健康监控 | production |
| 治理能力包 | `src/zephyr/governance/intelligence_governance/`（25 文件，含 __init__.py） | delegation_engine / delegation_manager / model_router / provider_failover / agent_debate / cross_agent_conflict_detector / multi_model_consensus / self_benchmark / self_test / self_validator / ai_self_diagnosis / autonomy_dashboard / continuous_trust / aisg_sandbox / memory_provider / meta_confidence / confidence_estimator / subagent_hook_propagator 等；整合方案由 [05 号文](05_intelligence_governance_consolidation.md)负责 | production（包级），整合待 05 号文 |
| Agent Spec | `src/zephyr/autonomy_core/spec_engine.py` | MOD-INF-019，蓝图→Skill 升级引擎（discover→generate→validate→register 四阶段） | production（蓝图登记） |
| 自我进化保真 | `src/zephyr/autonomy_core/self_evolution_fidelity_gate.py` | EchoTrap/RAGEN 自进化保真度门控 | production（蓝图登记） |
| 任务/相位路由 | `src/zephyr/autonomy_core/trigger_router.py`、`src/zephyr/autonomy_core/phase_planner.py` | MOD-INF-019 配套：任务路由表+相位计划 | production（蓝图登记） |
| 技能库 | `src/zephyr/autonomy_core/skills/`（约 60 个 skill_* 模块 + skill-registry.yaml） | 技能注册/发现/执行/评估/反馈/生命周期/沙箱/kill_switch 等 | production |
| 反馈闭环 | `src/zephyr/feedback_loop/actors/multi_agent_orchestrator.py`、`actors/agent_lifecycle.py` | FLE 多 Agent 协调（v0.12.0）、Agent 生命周期 | production |
| 反馈闭环 gate | `src/zephyr/feedback_loop/gates/`（safety_gate L1~L67 等） | 安全/治理/运维/安全门闸组 | production |
| 反馈闭环验证 | `src/zephyr/feedback_loop/verifiers/`（verification_engine / ab_test / auto_rollback 等） | 评估验证件组（自我迭代 Agent 的"评估"能力底座） | production |
| A2A 协议 | `src/zephyr/infrastructure/a2a_protocol/`（multi_agent / agent_card / blocklist 等） | Agent 间通信协议（治理运行时用，非策略编排，见 02 号文盘点） | production |
| Agent 身份/契约 | `src/zephyr/shared/contracts/identity/agent_identity.py`、`src/zephyr/shared/protocols/a2a/a2a_schemas.py` | Agent 身份契约、A2A schema | production |
| 自治熔断 | `src/zephyr/security/access_control/kill_switch.py` | VR-009 AI 自治熔断器（5 条件触发状态机，human_gated） | production |
| Agent 创建策略 | `src/zephyr/security/access_control/agent_creation_policy.py` | Agent 创建白名单策略 | production |
| 串谋检测 | `src/zephyr/security/access_control/detectors/multi_agent_collusion_detector.py`、`src/zephyr/feedback_loop/forensic/sub_agent_collusion.py` | 多 Agent 串谋检测 | production |
| Agent 风险监控 | `src/zephyr/risk/core/ai_agent_monitor.py` | AI Agent 行为风险监控 | production |
| LLM 防线 | `src/zephyr/security/llm_defense/llm_security/layers/l4_agent.py`、`l8_multi_agent.py` | LLM 安全栈 Agent 层/多 Agent 层 | production |
| Agent 治理配套 | `src/zephyr/governance/agent_spec/`（a2a_failure / rbac_bridge）、`src/zephyr/governance/ops_governance/agent_dispatch.py`、`src/zephyr/gov_audit/agent_signer.py` | Agent 规格治理/派发/签名审计 | production |
| 基础设施 Agent 桥 | `src/zephyr/infrastructure/pipeline/pipeline_agent_bridge.py`、`src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py`、`src/zephyr/infrastructure/rollback/agent_cooldown.py` | 流水线 Agent 桥/自愈 Agent/回滚冷却 | production |
| 业务能力包 | `src/zephyr/factor/`、`signal_ashare/`、`signal_fundamental/`、`signal_quality/`、`pf_alloc/`、`pf_core/`、`position/`、`backtest/`、`regime/`、`research/`、`experiment_tracking/`、`sell_decision/`、`trading/` | 因子/信号/组合/仓位/回测/regime/研究/实验追踪/交易执行域包（业务 Agent 的操作对象） | production（包级） |
| 算法能力包 | `src/zephyr/ml_train/`、`ml_serve/`、`intelligence/`（model_evaluation / model_profiling） | 模型训练/推理/评估/画像域包（算法 Agent 的操作对象） | production（包级） |
| 业务注册表 | `docs/registry_of_registries.yaml` + 18 个业务注册表（factor 111 条 / strategy 59 条等） | 62 号文施工成果，业务 Agent 的读取真源 | production |
| 交易决策侧设计 | 20 号文（G04 首批 3 策略）/ 30 号文（G12 Model A）/ 61 号文（生命周期多 AI 边界） | 业务 Agent 的策略载体与行为边界（只读引用） | active |

---

## 3. 设计决策

### 3.0 总决策：四类 Agent = 角色化薄入口层（role façade），非新建运行时

**决策**：四类 Agent 各实现为一个薄入口模块（角色 façade），只做"职责边界声明 + 能力包组装 + 工单/产出落盘"，内部零新业务逻辑；物理上不新建进程、不建消息总线、不建调度器。

**Why**：
1. **00_index §1 定位即"现有增强"**——能力组件（§2.4）已 production，缺的是角色化组织而非新系统。
2. **61 号备忘 §4.1 已拒绝多 Agent 运行时编排系统**——任何"Agent 自治运行时+agent 间通信+任务调度"形态都越界；人调度多会话+落盘交接是唯一合规形态。
3. **约束一（1 人）+ 约束五（单机 RTO<5 分钟）**——四套独立 Agent 运行时的运维成本个人项目承担不起；薄入口层故障面≈零（无常驻进程）。
4. **归因清晰度是生存项**（30 号文 §1.3）——角色入口把"哪个 Agent 能碰哪些包"显式化，AI 会话越权施工可在 review 时一眼识别。

**考虑过的替代方案**：
| 方案 | 结论 | 理由 |
|---|---|---|
| 四个独立 Agent 运行时进程 + 消息总线 | 拒绝 | 违反 61 号 §4.1 裁定；超约束一/二/五 |
| 不建执行层，AI 会话直接用能力包 | 拒绝 | 无职责边界，越权施工不可防；00_index §1 四类图景落空 |
| 合并为两类（治理+业务） | 备选，待裁定 | 见 §6 Q2——本文按 00_index §1 四类保留，但施工顺序允许先建两类入口 |

### 3.1 治理 Agent（gate 检查 / 规则执行）

**职责**（按"输入→处理→输出→验证→不做"组织）：
- 输入：施工/运行工单（落盘文件）+ gate 触发事件。
- 处理：调用 intelligence_governance/ 治理能力包 + feedback_loop/gates/ 门闸组 + security/access_control/ guards，执行 gate 检查与规则判定。
- 输出：gate verdict + 审计落盘（复用现有 audit 落盘纪律）。
- 验证：现有 gate 测试套件 + self_test.py / self_benchmark.py 自检。
- 不做：不修改规则本身（规则修订走治理流程，human_gated）。

**Why**：治理 Agent 是其他三类的前置——凡动作先过 gate（charter 约束六自治熔断的上游）。能力已在（intelligence_governance 25 文件 + gates L1~L67），薄入口只解决"统一角色入口"问题（05 号文 Q1 同款问题：包无统一入口）。**Why 不并入 05 号文**：05 号文负责 intelligence_governance 包内整合（技术域视角），本文治理 Agent 负责角色入口（执行层视角），入口依赖 05 号文的整合出口，二者是 consumer/provider 关系，不重复建设。

### 3.2 业务 Agent（因子 / 策略 / 组合运营）

**职责**：
- 输入：业务运营工单（如"新增因子候选评估""策略注册表查询""组合状态核对"）。
- 处理：读 18 个业务注册表（62 号文真源）+ 读 20 号文策略定义 + 按 30 号文 Model A 边界组织因子/策略/组合信息；操作对象为 factor/ signal_*/ pf_*/ position/ backtest/ regime/ 等域包。
- 输出：业务运营报告/施工工单落盘（design_memo + depgraph path）。
- 验证：注册表查询结果可回核（registry_of_registries.yaml）；工单产出人审。
- 不做：**不做任何自动交易决策/下单**——交易决策在交易决策侧（G12 firm 层 + G19/G20 执行），业务 Agent 只做运营辅助，产出一律"仅建议"（charter 约束六）。

**Why**：U7 解锁点已满足（G04 策略定义 active），业务载体（3 策略定义 + 18 注册表）是四类 Agent 中唯一"输入真源全部就绪"的，故业务 Agent 可在 Phase 0 与治理 Agent 并行先行。**Why 业务 Agent 不碰 regime 择时**：30 号文已裁定 regime 只做风险节流不做 alpha 择时，业务 Agent 读 regime 输出仅限风险节流语义，越此边界即违反已定稿决策。

### 3.3 算法 Agent（信号 / 模型 / 训练实验）

**职责**：
- 输入：算法实验工单（模型训练/评估/信号实验请求）。
- 处理：操作 ml_train/ ml_serve/ intelligence/（model_evaluation、model_profiling）+ backtest/ 域包；模型选择走模型路由（11 号文接口，当前以 intelligence_governance/model_router.py production 实现为假设锚点）；新模块生成走模块工厂（13 号文接口，当前以 autonomy_core/spec_engine.py 蓝图→Skill 链路为假设锚点）。
- 输出：实验记录（experiment_tracking）+ 模型评估报告落盘。
- 验证：实验可复现（experiment_tracking 记录）+ 回测零前瞻（PIT 铁律）。
- 不做：不做全自动策略搜索（30 号文 §5 暂缓项）；不做 GPU 集群训练（约束二单卡 RTX 3090，显存 <90%）。

**Why**：算法实验是算力密集+试错密集环节，角色入口的价值在"实验纪律"（登记→排程→记录→评估），防止 AI 会话无登记乱起实验耗尽单卡资源。**依赖降级说明**：11/13 号文未填充，本节接口为保守假设（见 §6 Q3），Phase 0 阶段算法 Agent 只手动触发既有训练/评估入口，不依赖未建接口。

### 3.4 自我迭代 Agent（评估 / 优化 / 反馈）

**职责**：
- 输入：执行结果证据（gate verdict / 实验指标 / 审计记录）。
- 处理：用 feedback_loop/verifiers/ 评估件做效果评估；用 autonomy_core/self_evolution_fidelity_gate.py 做自进化保真门控；反思闭环走 12 号文自反 Agent 接口（未填充，假设锚点=feedback_loop actors + verifiers 现有闭环）。
- 输出：优化建议工单 + 反馈记录落盘（回喂自我进化层作证据）。
- 验证：fidelity gate 保真校验 + 人审（Phase 2 前优化建议一律 human_gated）。
- 不做：不做权重自更新/自进化策略搜索（远期候选）；不做自动改架构（架构手动，00_index §1 顶层原则）。

**Why**：自我迭代是"AI 对自我循环迭代优化"的收口环节，但也是失控风险最高环节——故其输入只消费落盘证据（不实时挂钩运行时），输出只产建议工单（不直接改码），Phase 1 才启动施工（U4 解锁点后）。

### 3.5 四类 Agent 协同设计（治理→业务→算法→迭代闭环）

**协同形态**：人调度多会话 + 落盘交接（61 号备忘 §3.6 交接纪律）。闭环：

```
人（调度者）
  → 治理 Agent：工单过 gate（放行/驳回落盘）
  → 业务 Agent：读注册表/策略定义，产业务运营工单
  → 算法 Agent：执行实验，产实验记录
  → 自我迭代 Agent：消费证据，产优化建议工单
  → 人审优化建议 → 下一轮工单
```

**Why 不用 A2A 协议做 Agent 间实时通信**：infrastructure/a2a_protocol/ 定位为治理运行时用（02 号文盘点），非执行层 Agent 编排；61 号裁定"AI 间不直接通信"。执行层四类 Agent 之间只通过落盘文件（design_memo / depgraph path / 工单 / 注册表）交接，天然可追溯、可审计、可回滚。

**Why 闭环顺序固定为治理先行**：gate 未放行的工单不进入业务/算法环节——这是 charter 约束六（自治熔断）与 VR-009（kill_switch）的上游预防层分工（61 号文 BM-RC-09 同款分层：边界内运行减少熔断触发，熔断做下游兜底）。

---

## 4. 施工计划

> depgraph L1 铁律：凡新建模块，第一步登记 apply_depgraph.py --add-design-node（status=planned），验证通过后最后一步 --transition-design-maturity <NODE_ID> production。禁止先施工后补登记。

### Phase 0：单 Agent 手动触发（治理 + 业务先行）

**步骤 S0.1：depgraph 设计态登记**
- 为四个角色入口模块登记 depgraph 设计态节点（status=planned），声明依赖：治理入口→intelligence_governance/feedback_loop.gates/security.access_control；业务入口→业务注册表真源/factor/signal/pf 域包；算法入口→ml_train/intelligence/backtest；迭代入口→feedback_loop.verifiers/autonomy_core。
- 验收：apply_depgraph.py 查询可见 4 个 planned 节点且依赖边完整。
- 注：worktree 会话内只登记不流转，merge 回 dev 后随第一次重建自动转 production（AGENTS.md RULE-DEPGRAPH 场景分流）。

**步骤 S0.2：治理 Agent 入口施工（P0-1）**
- 建薄入口模块（目标 <200 行，只组装不重写）：声明治理职责边界、组装 intelligence_governance + gates + access_control 调用面、工单读写落盘。
- 依赖：05 号文整合出口（若 05 号文未定型，入口直接组装包级 __all__ 导出，记 §6 Q3 核对项）。
- 验收：①一个样例 gate 检查工单端到端跑通（输入工单→gate verdict→审计落盘）；②入口模块自身过全部既有 gate；③无新业务逻辑（code review 确认纯组装）。

**步骤 S0.3：业务 Agent 入口施工（P0-2，与 S0.2 可并行）**
- 建薄入口模块：注册表查询（registry_of_registries.yaml 真源）+ 20 号文策略定义读取 + 业务工单生成。
- 验收：①"查询某因子注册状态""生成新增因子候选评估工单"两个样例端到端跑通；②产出物 100% 落盘且标注"仅建议"；③不触碰任何交易执行路径（Grep 验证无 miniQMT/下单调用）。

**步骤 S0.4：算法 Agent 入口施工（P0-3，手动形态）**
- 建薄入口模块：实验登记→既有训练/评估入口调用→experiment_tracking 落盘。
- 验收：①一个样例模型评估实验端到端跑通且可复现；②实验登记先于执行（无登记不执行）；③单卡显存占用 <90% 硬上限不破（约束二）。

**步骤 S0.5：自我迭代 Agent 入口施工（P0-4，仅评估只读形态）**
- 建薄入口模块（只读证据+产建议工单）：消费 gate verdict/实验指标落盘文件，经 verifiers 评估+fidelity gate 保真，产优化建议工单。
- 验收：①消费一份真实实验记录产出建议工单；②建议工单 human_gated 标记齐全；③无任何代码自改路径。

**步骤 S0.6：验证转正**
- 各入口验收通过后，merge 回 dev 并实证核验 depgraph 节点 planned→production（worktree 分流路径）或 --transition-design-maturity 手动转正（主工作区路径）。

### Phase 1：多 Agent 半自动（人调度多会话，U4 解锁后）

- S1.1：四类入口接入 11 号模型路由 / 12 号自反闭环 / 13 号模块工厂正式接口（依赖 U4 解锁点；接口以依赖文档填充后为准，替换 Phase 0 假设锚点）。
- S1.2：工单队列落盘化（复用 61 号文 §3.6 交接载体：design_memo + depgraph path + 占用表），支持人调度多会话并行施工。
- S1.3：业务 Agent 细化（U7 深化）：对接 G04 首批 3 策略运营场景（打板/多因子/事件驱动的因子-策略-组合状态核对）。
- 验收：①一次完整闭环（治理→业务→算法→迭代）全程落盘可追溯；②任一会话中断可从落盘文件恢复（约束五断点恢复语义）；③全部产出仍 human_gated。

### Phase 2+（远期，不在本文施工范围）

半自动→更高自治的演进由 [17 号文](17_phase_roadmap.md)统一排期；Phase 2 保留人工审核（13 号文约束同款）。远期属性：Phase 2+ 为远期愿景，不属过度工程，但本文不展开。

---

## 5. 不做什么

1. **不做 agent 编排系统**——[61 号文](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §4.1 已裁定拒绝（多 Agent 运行时编排/任务调度器/冲突解决器一律不建）。
2. **不做实时 Agent 通信**——四类 Agent 间只文件落盘交接（61 号文 §3.6）；A2A 协议限治理运行时使用，不向执行层开放编排语义。
3. **不做全自动业务 Agent**——业务 Agent 产出一律"仅建议"+human_gated；Phase 2 仍保留人工审核；交易决策/下单属交易决策侧（G12/G19/G20），本文不碰。
4. **不做 LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索**——30 号文 §5 已暂缓（远期候选，Phase 5+ 重评）。
5. **不做四类 Agent 独立运行时进程/消息总线/K8s/分布式调度**——超 system_charter §2 约束一/二/五（1 人、单机、无集群）。
6. **不重写已有能力组件**——入口层只组装；intelligence_governance 包内整合归 05 号文，自反机制归 12 号文，模块生成归 13 号文。
7. **不做权重自更新/架构自改**——架构手动（00_index §1 顶层原则），自我迭代 Agent 只产建议工单。
8. **不做 GPU 超用实验排程**——单卡 RTX 3090 显存 <90% 硬上限，算法 Agent 不建多卡/集群抽象（约束二）。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | 四个 Agent 的施工顺序？ | 待裁定 | 本文 §4 建议：治理（S0.2)+业务（S0.3）先行并行→算法（S0.4)→迭代（S0.5 只读形态）。依据：治理是其他三类前置（gate 先行），业务输入真源唯一全就绪（U7 已满足）。待人确认 |
| Q2 | 四类是否可简化为两类（治理+业务）先行？ | 待裁定 | 00_index §1 为四类图景，本文按四类薄入口设计；若人力紧张，允许 Phase 0 只建治理+业务两入口，算法/迭代入口延后——物理上是薄入口，简化为两类不破坏四类终态 |
| Q3 | 对自我进化层的接口假设核对 | 待核对 | 11/12/13 号文截至 2026-08-17 为 v0.1.0 骨架（并行填充中）。本文假设锚点：①模型路由=intelligence_governance/model_router.py（production 已有）；②自反闭环=feedback_loop actors+verifiers 现有闭环；③模块生成=autonomy_core/spec_engine.py（MOD-INF-019）。待三文档填充后逐项核对，不一致处修订本文并升版本 |
| Q4 | 四个入口模块的域归属与模块编号 | 待裁定 | 候选：归入既有 D_ORCHESTRATOR 域 vs 新建执行层域。涉及 functional_domain_registry 变更，需人裁定后按规则登记 |
| Q5 | 执行层 Agent 自治等级（L0~L3）划分 | 待核对 | 15 号文（自治边界）截至 2026-08-17 为 v0.1.0 骨架。本文暂定四类入口全部按最低自治（手动触发+human_gated 产出）施工；待 15 号文填充后对齐有界自治 5 级映射 |
| Q6 | 治理 Agent 入口与 05 号文整合出口的衔接 | 待核对 | 05 号文截至 2026-08-17 为 v0.1.0 骨架。若 05 号文产出统一入口，治理 Agent 入口改为消费该出口；若 05 号文维持包级导出，治理入口直接组装 __all__。待 05 号文填充后核对 |
| Q7 | 本目录 18 篇骨架的 doc_type 合规性 | 待裁定 | 骨架统一用 doc_type=implementation_plan，但 doc_type_vocabulary.yaml 受控词表无此值（construction_plan 已于 2026-06-29 合并入 blueprint），TTL-METADATA 门禁硬阻断。本文已改 doc_type=blueprint（并补 valid_from/last_verified）以过门禁；00_index.md 用 architecture_design 同样不在词表。建议协调者统一裁定本目录 doc_type 取值后回填各文 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成（doc_type 由 implementation_plan 修正为 blueprint——受控词表无 implementation_plan 值，门禁硬阻断，见 Q7）：§2 背景（项目处境/核心问题/约束/已施工设施盘点实测清单）、§3 设计决策（总决策=角色化薄入口+四类 Agent why+协同闭环）、§4 施工计划（Phase 0 五步+Phase 1 三步，含 depgraph L1 登记）、§5 不做什么（8 条边界）、§6 开放问题（Q1~Q6） | AI-FILL-14 填充；依赖文档（05/11/12/13/15 号文）未填充的接口假设降级入 §6 Q3/Q5/Q6 |

---

*维护者：AI 架构协调者*