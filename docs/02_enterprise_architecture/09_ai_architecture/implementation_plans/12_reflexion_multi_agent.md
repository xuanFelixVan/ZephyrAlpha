---
ttl: permanent
doc_type: architecture_view
title: 自反Agent与多Agent协作施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.3.0"
date: 2026-08-17
topic: reflexion_multi_agent
scope: 09_ai_architecture
---

# 自反Agent与多Agent协作施工图

> 本文定位：自反Agent（Actor→Evaluator→SelfReflection + L1/L2/L3 反思 + PreFlect + Agent-R + ReflCtrl）和多Agent协作（投票优先 + FactorMAD + R&D-Agent + 涌现行为检测）的施工。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，对标见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md)，全局资产盘点真源见 [02_design_asset_inventory.md](02_design_asset_inventory.md)（本文 §2.4 只列本主题设施）。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | 自反Agent与多Agent协作 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 自我进化层 |
| 依赖 | 自我进化核心组件（[11_evidence_skill_router.md](11_evidence_skill_router.md)，已填充 v0.2.0） |
| 对标 | TiMi（数学反思闭环）/ FactorMAD / R&D-Agent-Quant |
| 优先级 | P1——自反Agent是"AI 对算法自我循环迭代优化"的核心机制 |
| 状态 | draft（已填充 v0.3.0） |

---

## 2. 背景

### 2.1 项目处境

自反Agent与多Agent协作是 [00_index.md](00_index.md) §1 目标架构"AI 自我进化层（设计已有，待施工）"的两个组件；[01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §1 对照表将自反Agent标注为"设计完成，未施工"。经 §2.4 实测盘点（扫描日期 2026-08-17），真实处境呈"两极分化"：

- **自反Agent：近乎全空白**。全 src 实测不存在 reflexion/preflect/reflctrl 命名模块；`intelligence/` 下无反思组件；`docs/03_modules/` 下无反思蓝图；`data/brain/` 下无反思数据。唯一沾边的 `feedback_loop/evolution/self_reflection.py`（MOD-FEEDBACK_LOOP）是 30 行桩实现——`reflect()` 固定返回 `["Consider alternative root causes"]`，且语义是"FLE 运维诊断自质疑"（盲点 R75），不是研究侧"策略/因子/代码生成质量"的反思。Actor→Evaluator→SelfReflection 三角色、L1/L2/L3 反思、PreFlect、Agent-R、ReflCtrl 全部为设计态，需新建。
- **多Agent协作：基座极重、业务消费为零**。`infrastructure/a2a_protocol/`（MOD-INF-025）实测 89 个 .py 全部 production——加权投票引擎（`a2a_voting.py`：approve/reject/abstain + quorum 法定人数 + 声誉权重）、结构化辩论协议（`a2a_debate.py`：主张→反驳→合成三轮）、仲裁器、编排基座（`multi_agent.py`）一应俱全，配套 `tests/a2a/` 48 个测试文件。但投票/辩论引擎**没有任何量化业务消费方**（因子评审、策略评审、代码生成选优均未接线）；`feedback_loop/actors/multi_agent_orchestrator.py` 同样是桩（`delegate()` 只查字典 key）。同时治理裁定明确约束落地形态：61 号备忘 §2.3 裁定"不做 agent 编排系统，多 AI 协作是人调度多会话非 agent 自治"；交易决策侧 [30_multi_strategy_concurrency](../../07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §5 对"LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索"持暂缓口径，且关联裁定 CC-14"投票优先多 Agent 协作"已降级为可选模式（#ARCH-OE-011，2026-08-11）——solo 单 session 主导用单 Agent 决策 + red_blue_validator 红蓝对抗承接（只读引用，不展开）。
- **涌现行为检测：检测器已 production，告警介入未闭环**。`feedback_loop/detectors/anomaly/emergent_behavior_detector.py`（组件间相关性>0.70/熵降>0.30/滞回>0.15 三信号 + STABLE→CORRELATING→CRITICAL→HYSTERETIC 状态机）、`agent_trajectory_anomaly_detector.py`（drift/cycle/missing_step 轨迹静默故障）、`a2a_behavior_fingerprint.py`（行为指纹）三件已组装进 `risk/core/ai_agent_monitor.py`（MOD-RK-14：risk_score=0.4×涌现+0.3×轨迹+0.3×指纹，is_breached=score>0.6 或 CRITICAL）。但 MOD-RK-14 的消费方仅登记 MOD-L04-001（风控编排器），"非预期涌现→告警→人工介入"的处置链路未接线。

### 2.2 核心问题

1. **L1/L2/L3 反思如何分工？** 三级反思的抽象层级（执行/策略/目标）、触发频率、token 成本各不相同，不分级=要么反思不足（错误重复发生），要么反思泛滥（算力成本失控）。TiMi 的数学反思闭环（[01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §2.3）证明金融反思需要"可计算的数学对象"载体，但 TiMi 无频率控制——ReflCtrl 是本项目在单机约束下的必要补充。
2. **反思产出流向哪里？** 反思不是自我安慰，产出必须结构化沉淀：失败原因进证据链（11 号文证据关联）、验证过的失败模式进 PreFlect 预反思库、生成类任务的失败案例回流模块工厂再生成（[13_module_factory.md](13_module_factory.md) §4.7 已预留接口假设）。反思组件若不接下游，等于白反思。
3. **投票优先已降级为可选模式，协作主路径是什么？** 30 号文 §5 关联裁定（#ARCH-OE-011）：CC-14 投票优先多 Agent 协作降级为可选模式，主路径=solo 单 session 单 Agent 决策 + red_blue_validator 红蓝对抗承接。00_index §1 目标架构的"投票优先（3-5 Agent 投票→选最优）"与该裁定的口径张力需登记（§6 Q2）；本文按裁定为真源——投票评审壳作为可选模式设施保留施工（消费既有 a2a_voting 引擎、人即协调器、文件落盘交接），不替代单 Agent 主路径。
4. **涌现检测如何闭环？** 检测器 production 但"检出后怎么办"没有链路——is_breached 信号需要接告警与人工介入 SOP，且深度安全语义（串谋/目标劫持/边界违反）归 [15_autonomy_boundary_risk.md](15_autonomy_boundary_risk.md) 与 [16_ai_security_ops.md](16_ai_security_ops.md)，本文只负责检测信号的消费与介入接线。
5. **a2a 编排基座与"不做编排系统"裁定如何共存？** 89 个 production 文件已在仓，全部退役不现实也无必要——投票/辩论引擎单件可被"人调度多会话"形态直接消费；编排层（任务分派/自治协调）不启用。处置边界见 §6 Q5。

### 2.3 约束条件

- **硬件与成本**：单机 RTX 3090 24GB + 64GB RAM，无集群——反思调用消耗 LLM token，ReflCtrl 频率控制目标节省 20-80% token（本文自定设计目标：分层频率区间预估——执行层 ~80%/战术层 ~50%/战略层 ~20%，见 §3.4；ReflCtrl 原论文实测 33.6%。⚠️口径修正：00_index §1 实测无此数字，v0.2.0 误引为"00_index §1 设计口径"，本版更正；[13_module_factory.md](13_module_factory.md) §4.7 按"12 号骨架约束"引用此区间——真源在本文）；禁止"每步都反思"的无约束循环。
- **治理裁定**：不做 agent 编排系统（61 号备忘 §2.3）；投票优先多 Agent 协作已降级为可选模式（30 号文 §5，#ARCH-OE-011），主路径=solo 单 session 单 Agent 决策 + red_blue_validator 红蓝对抗；"LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索"按 30 号文 §5 口径暂缓——FactorMAD 式对抗互评降级为"人发起"的可选评审增强，不做自治辩论循环。
- **频率约束**：Tick=3 秒、日频及以上根频率——反思/投票/涌现复核全部发生在盘后离线窗口（TiMi"开发/部署解耦"的外部印证，见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §2.3），不进盘中、不进下单热路径。
- **一人+AI 施工**：反思触发规则、投票裁决规则、涌现介入阈值全部显式化可审计，不用黑盒学习模型决定"何时反思"。
- **交接纪律**：AI 会话间不直接通信（61 号备忘 §2.2），多会话投票的候选收集与结果发布全部文件落盘。
- **依赖锁定**：投票/辩论引擎消费 MOD-INF-025 既有实现，不改其结构；涌现检测消费 MOD-RK-14 输出（MODIFY-GUARD=blueprint.md），不新造检测器；证据链接口以 [11_evidence_skill_router.md](11_evidence_skill_router.md)（v0.2.0）为真源；模块工厂接口以 [13_module_factory.md](13_module_factory.md)（v0.2.0）§4.7 为真源。

### 2.4 已施工设施盘点

以下全部经实际读取/扫描验证（扫描日期 2026-08-17）。全局资产盘点真源是 [02_design_asset_inventory.md](02_design_asset_inventory.md)，本节只列本主题相关设施。

**自反Agent相关**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | `src/zephyr/feedback_loop/evolution/self_reflection.py` | 30 行桩：SelfReflection.reflect() 固定返回单条建议；语义=FLE 运维诊断自质疑（盲点 R75），非研究侧质量反思 | production（桩实现，语义不同，仅可参考不可复用） |
| 代码模块 | 研究侧反思设施（reflexion/preflect/reflctrl） | 实测不存在——全 src 按 reflex/reflect/preflect/emergent 扫描，研究向反思模块零命中（上述桩除外） | 未施工 |
| 测试 | `tests/self_check/test_self_reflection.py` | 既有桩的测试 | production |
| 蓝图 | `docs/03_modules/` 下反思蓝图 | 实测不存在（按 reflexion/自反Agent/PreFlect/ReflCtrl 全文扫描零命中） | 未施工 |
| 配置/数据 | `data/brain/` 反思数据 | 实测不存在（无 reflection 相关文件） | 未施工 |

**多Agent协作相关**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | `src/zephyr/infrastructure/a2a_protocol/`（实测 89 个 .py） | A2A 协议全栈（MOD-INF-025）：layer1 发现/layer2 通信/layer3 协调/governance 四层，全部 production | production（编排层不启用，见 §2.2-5） |
| 代码模块 | `.../layer3_coordination/a2a_voting.py` | A2AVoting 加权投票引擎：approve/reject/abstain 三动作 + quorum 法定人数 + 角色/声誉权重，输出 VotingResult | production |
| 代码模块 | `.../layer3_coordination/a2a_debate.py` | A2ADebate 结构化辩论：主张→反驳→合成三轮，输出 DebateResult（winner/consensus/synthesis） | production |
| 代码模块 | `.../layer3_coordination/arbitrator.py`、`multi_agent.py` | 仲裁器与编排基座（MultiAgentRole 六角色 AgentCard） | production（编排基座不启用） |
| 代码模块 | `src/zephyr/governance/intelligence_governance/multi_model_consensus.py` | 多模型共识协议枚举（MAJORITY/WEIGHTED/UNANIMOUS）+ 辩论三轮 + escalate_to_owner，骨架级 | production（骨架规模） |
| 代码模块 | `src/zephyr/governance/intelligence_governance/agent_debate.py` | 双模型辩论裁决（DebateVerdict：AGREE/A_SUPERIOR/B_SUPERIOR/OVERRIDE）+ ModelResponse hash 契约 | production |
| 代码模块 | `src/zephyr/feedback_loop/actors/multi_agent_orchestrator.py` | 桩实现：delegate() 仅查 agents 字典 key（盲点 R159b） | production（桩实现，不扩为编排器，见 §5） |
| 代码模块 | `src/zephyr/security/access_control/detectors/multi_agent_collusion_detector.py` | MultiAgentCollusionDetector（MOD-INF-018）：交互频率+隐蔽通道（covert/hidden/side）合谋检测，阈值 3 次 | production |
| 代码模块 | `src/zephyr/security/llm_defense/llm_security/layers/l8_multi_agent.py` | L8 多Agent安全层（MOD-LLM_SECURITY）：跨 agent 认证（admin scope 默认拒）、边界执行 | production |
| 蓝图 | `docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md`（MOD-INF-025） | A2A 协议蓝图（配套 arbitration_rules.yaml / trigger_config.yaml） | production |
| 测试 | `tests/a2a/`（实测 48 个文件）+ `tests/agent/test_agent_debate.py` + `tests/multi/test_multi_agent_collusion_detector.py` 等 | 投票/辩论/合谋/共识测试覆盖 | production |

**涌现行为检测相关**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | `src/zephyr/feedback_loop/detectors/anomaly/emergent_behavior_detector.py` | EmergentBehaviorDetector：组件间相关性（阈值 0.70）+熵降（0.30）+滞回（0.15），四态状态机 STABLE→CORRELATING→CRITICAL→HYSTERETIC（代码实测枚举声明序；迁移逻辑实测：高相关对≥3→CRITICAL，≥1→CORRELATING，无高相关但已设压前基线→HYSTERETIC，否则→STABLE。⚠️16 号文 §2.4 写作"STABLE→CORRELATING→HYSTERETIC→CRITICAL"，与代码实测颠倒，登记 §6 Q8） | production |
| 代码模块 | `src/zephyr/feedback_loop/detectors/correlation/agent_trajectory_anomaly_detector.py` | Agent 轨迹静默故障检测（drift/cycle/missing_step，对标 IBM arXiv 2511.04032） | production |
| 代码模块 | `src/zephyr/infrastructure/a2a_protocol/layer3_coordination/a2a_behavior_fingerprint.py` | Agent 行为指纹偏差检测 | production |
| 代码模块 | `src/zephyr/risk/core/ai_agent_monitor.py` | MOD-RK-14 组装件：risk_score=0.4×涌现+0.3×轨迹+0.3×指纹，is_breached=score>0.6 或 CRITICAL；消费方仅 MOD-L04-001 | production（告警介入未接线） |
| 测试 | `tests/audit/test_emergent_behavior_detector.py`、`tests/risk/core/test_ai_agent_monitor.py` | 检测器与组装件测试 | production |

**治理裁定与主路径承接设施**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 设计备忘 | [61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §2.3 | "不做 agent 编排系统，多 AI 协作是人调度多会话非 agent 自治"（已定稿，只读引用） | active |
| 设计备忘 | [30_multi_strategy_concurrency.md](../../07_trading_decision_architecture/design_memos/30_multi_strategy_concurrency.md) §5 | "LLM 多 Agent 辩论 / R&D-Agent 自进化策略搜索"暂缓（重评条件=可控性方案验证可靠）；关联裁定 CC-14 投票优先多 Agent 协作降级为可选模式（#ARCH-OE-011，2026-08-11），solo 单 session 主导用单 Agent 决策 + red_blue_validator 承接（只读引用） | active |
| 代码模块 | `src/zephyr/security/adversarial_validation/`（实测 25 个 .py）+ `src/zephyr/red_blue_validator/__init__.py` | 红蓝对抗验证设施（#ARCH-OE-011 裁定的单 Agent 主路径承接方）：validator/attack_registry/constitution_engine/circuit_breaker/game_day 等 | production |

---

## 3. 设计决策

> 本节只写 why（为什么选这个方案、考虑过哪些替代），实现细节由蓝图/代码维护。

### 3.1 L1/L2/L3 三级反思设计

**决策**：新建自反Agent组件（落点 `src/zephyr/intelligence/reflexion/`），反思按抽象层级×触发频率分三级——**L1 单轨迹反思**（执行层：单次任务结束后，对该次执行轨迹做结构化复盘，产出"成功/失败+原因+改进点"，触发频率最高、成本最低）；**L2 同类任务反思**（策略层：同类任务累积 N=5 次后触发，跨轨迹归纳共性失败模式与有效参数区间，产出进 PreFlect 库与证据链）；**L3 跨任务反思**（目标层：跨任务类型审视研究方向与目标对齐，Phase 3 远期，显式标注远期属性）。三级共用同一套结构化反思记录 schema（任务标识/输入摘要/结果指标/归因分类/改进建议/置信度），反思载体是可计算的结构化对象而非自由文本感想。

**L2 反思增强——TiMi 数学反思闭环**：L2 归纳出的"有效参数区间"对可形式化参数（仓位/阈值/成本类）不走 LLM 直觉调整——试运行反馈形式化为约束优化问题（例：max Sharpe s.t. 最大回撤<5%、换手率<200%），用 scipy.optimize 精确求解替代 LLM 直觉（数学求解保证最优性，LLM 调整可能陷入局部最优）；仅限可形式化的参数优化，策略逻辑变更不适用（源：学习系统架构 §8.1 Step5 + 20-D-RESEARCH §12.11.2，R-07 裁定✅纯 Python 可建）。

**第四维度——元反思（Meta-Reflection）**：L1/L2/L3 反思的对象是任务执行，元反思的对象是"反思过程本身"——四步闭环：经验回放（回放历史成功/失败案例）→反思提炼（从案例中提炼可复用的反思模式）→技能注册（反思模式注册为可复用技能，走 11 号文技能沉淀流程，不自建通道）→元反思（评估反思过程本身的质量→改进反思策略，如调整归因分类粒度/触发阈值）。频率硬约束 ≤1 次/周，防过度反思消耗资源（源：12-D-ML-TRAIN §10.1 维度6，R-45 裁定✅纯 Python）。远期属性与 L3 同档：反思记录积累不足时"反思反思"无统计意义，随 L3 一并在 Phase 3 评估启动。

**Why 分级而非单一反思**：无分级的反思只有两种失败模式——每次任务都深度反思（token 成本失控，违反 §2.3 成本约束）或从不反思（错误重复发生）。L1 高频低成本管"这一次哪里错了"，L2 中频管"这类事的规律是什么"，L3 低频管"方向对不对"，元反思管"反思得好不好"——频率与抽象层级正相关是算力约束下的必然结构。TiMi 的数学反思闭环（对标细节见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §2.3，本文不重复）印证了"金融反思需要可计算对象"，本项目三级划分与之同构且粒度更细。

**Why 结构化记录而非自由文本**：反思产出要被下游机读消费——证据链挂接（11 号文）、PreFlect 库检索、模块工厂再生成 prompt 注入（13 号文 §4.7）都要求字段化；自由文本无法规则化处理，与 11 号文"结构化存储而非纯文档"的裁定同因。

**考虑过的替代方案**：Reflexion 原始范式（Shinn et al. 通用文本反思，无金融对象无分级）——未采纳，取舍真源在 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §2.3；CRITIC 工具校验框架（只校验输出不含优化闭环）——未采纳，同源登记。

### 3.2 Actor→Evaluator→SelfReflection 三角色设计

**决策**：三角色逻辑分离——Actor 产出候选（代码/因子/参数），Evaluator 按结构化量规打分（评估报告格式对齐 13 号文 §3.5 四级报告的接口假设，见 §4.6），SelfReflection 消费评估报告+执行轨迹产出反思记录。三角色是逻辑角色而非三个常驻进程：同一 LLM 会话内可分步扮演，也可经模型路由（11 号文级联控制器）把 Evaluator 分派给低成本模型。

**多模型分工反馈循环（三角色的模型层具体化）**：生成/批判/裁决分派给不同模型——Generator（GLM-5.1）生成候选，Critic（DeepSeek V4 Pro）审查批判（识别逻辑漏洞/过拟合风险/代码缺陷），Generator 按 Critic 反馈修正→Critic 再审→收敛，收敛条件=Critic 无新批评 或 达到最大轮数（≤3 轮），最终 Judge（Claude）综合评估裁决（源：12-D-ML-TRAIN §9.2 分析师Agent反馈循环 + 20-D-RESEARCH §12.12.1；外部依据：Man Group AlphaGPT 反馈循环使 IC 从 0.58%→2.23%）。与 13 号文的分工：13 号文 §3.4 是**生产侧流水线**（DSL+AST 沙箱+模板骨架受控生成+第二会话交叉验证），本文是**反思侧**——负责"何时触发反思/由谁批判裁决/评估报告如何产出与分流"；多模型反馈循环的触发与收敛评估归本文，生成物生产管道本身归 13 号文。

**Why 分离而非单角色自问自答**：生成与评估共用同一上下文会系统性高估自身产出（无对立视角）；Evaluator 独立上下文+结构化量规是廉价的对抗性。同时分离后可按角色路由模型——Evaluator/SelfReflection 用本地模型、Actor 用强模型，直接压 token 成本（与 ReflCtrl 叠加，§3.4）。

### 3.3 PreFlect 前瞻反思设计

**决策**：PreFlect = 执行前的预反思——任务启动时检索失败模式库（L2 沉淀的共性失败模式+历史人审驳回原因），把"上次怎么死的"注入本次执行上下文。失败模式库是结构化条目（模式描述/触发条件/规避建议/来源反思 ID），人工可编辑。

**Why 预反思补事后反思**：事后反思（L1/L2）纠正的是"已发生的错误"，预反思防止的是"重复发生的错误"——后者成本更低。量化场景同一类错误（如前视偏差、未来函数、交易成本漏算）会跨任务反复出现，单次事后反思挡不住下一任务再犯。冷启动期失败模式库允许人工种子集（见 §6 Q6）。

### 3.4 Agent-R 与 ReflCtrl 频率控制设计

**决策**：Agent-R 实时反思受 ReflCtrl 频率闸门控制——显式触发规则集：①评估置信度低于阈值；②验证失败（回测/单测/人审驳回）；③涌现/漂移异常信号；④L2 累积计数达标（N=5）。规则之外不反思；连续反思深度设上限（单任务反思轮次上限可配置）。全部反思在盘后离线窗口批量执行，盘中零调用。

**触发规则具体参数**（源：Agent架构 §6.2/§6.4/§6.5 草稿）：

- **L1 强制触发三条件**（默认 L1 可被 ReflCtrl 跳过，但以下情形强制）：执行结果与预期偏差>20% / 风控否决 / 执行失败。
- **Agent-R 轨迹内异常四场景**：信号强度偏离历史均值>2σ（源设计实时档延迟目标 <500ms）；实际滑点>预估滑点×2（<200ms）；风控参数偏离基准值>10%（<1s，修正动作含回滚基准值+触发 L2）；市场状态突变（状态转换概率>90% 但未触发，<3s）。⚠️延迟目标为源设计实时档参数；本项目 §2.3 盘后批量约束下实时档不启用，四场景阈值作为盘后轨迹复盘的异常检测规则使用。
- **HITL 低置信触发**（反思侧消费接口登记）：置信度 50-69%→触发 L1；置信度 <50%→触发 L1+L2（源：23-D-AUT-PERM §10.6.2）。置信度分级处置阶梯的真源在 15 号文（其有界自治 L0~L3 阶梯 + `autonomy_regressor.py` confidence<0.3 回归已 production），本文只登记反思侧消费接口；15 号文 v0.2.0 尚无 50-69% 刻度，阈值最终口径登记 §6 Q9 待裁定。
- **分层频率控制**：执行层仅异常时触发（预估 token 节省 ~80%）；战术层每 5 次同类任务 L1+每日 L2（~50%）；战略层每次任务 L1+每周 L2+每月 L3（~20%，战略决策必须反思）。
- **频率控制决策矩阵**：连续优秀（超出预期）≥5 次→跳过 L1 仅记录成功模式（连续成功说明策略有效，反思边际收益低）；正常（符合预期）≥3 次→跳过 L1 仅 L2 聚合反思；轻微偏差→执行 L1；严重偏差→执行 L1+立即 L2；失败→执行 L1+立即 L2+触发 L3。

**Why 频率控制是一等功能而非优化项**：反思消耗 LLM token，无闸门的反思循环=算力成本失控，单机约束下这是生存性问题（节省 20-80% token 为本文自定设计目标——下限=战略层 ~20%、上限=执行层 ~80%，ReflCtrl 原论文实测 33.6%；00_index §1 实测无此数字，v0.2.0 误引已修正，见 §2.3）。显式规则集同时满足"一人+AI"可审计约束——何时反思必须能回答"哪条规则触发的"。

**考虑过的替代方案**：置信度自适应学习触发（学一个"何时值得反思"的模型）——训练数据稀薄+不可审计，过度工程，列入 §5。

### 3.5 修正闭环与效果验证设计

**决策**：执行→评估→反思→修正闭环的"后半段"显式化——**修正应用按三分类分流**（复用 15 号文 ai_modifiable/human_gated/immutable 边界，不另建修正权限体系）：参数微调（ai_modifiable）自动应用；规则调整（human_gated）提交审批后应用（回测 V3+V4 门禁验证，审批拒绝→不应用）；策略优化建议（immutable）仅记录不自动应用。**修正效果验证**：修正后执行 N=5 次同类任务（与 L2 累积计数同口径，§3.1），对比修正前后效果（Sharpe/IC/准确率）；改善>阈值→确认修正；改善<阈值或效果下降>5%→回滚。确认修正→写入情景记忆+更新 Agent Card（源：Agent架构 §6.6 策略自我修正闭环，经 12-D-ML-TRAIN §A7 搬入节核实）。

**Why 验证后半段必须显式**：反思不修正是白反思，修正不验证是盲改——无验证的自动修正可能把系统越改越差（负优化）。"下降>5%→回滚"是机械判据，与"一人+AI"可审计约束一致；N=5 对比与 L2 同口径避免双阈值。确认后写情景记忆+更新 Agent Card 让修正成果进入可检索资产，而非停留在一次性 diff。

### 3.6 多Agent协作设计（可选模式设施，主路径为单 Agent + 红蓝对抗）

**决策**：协作主路径按 30 号文 §5 关联裁定（#ARCH-OE-011）执行——solo 单 session 单 Agent 决策 + red_blue_validator 红蓝对抗承接（设施已 production，§2.4），本文不为该主路径新增施工项。投票优先多Agent协作为**可选模式设施**：投票评审壳（新建，<100 行编排壳，落点 `intelligence/reflexion/` 内）在需要多候选裁决的高价值场景由人启用——人多开的 3-5 个 AI 会话（或多模型 API 并行）各自产出候选→壳收集候选文件→调用既有 A2AVoting 引擎（approve/reject/abstain + quorum + 权重）计票→选最优落盘→全程文件交接。FactorMAD 式对抗互评（辩论制评审）按 30 号文 §5 暂缓口径降级为 Phase 2 可选增强：由人发起、调用既有 A2ADebate/agent_debate 设施跑"主张→反驳→合成"，不做自治辩论循环（重评条件=可控性方案验证可靠）。

**Why 主路径单 Agent + 红蓝对抗而非多 Agent 常驻**：#ARCH-OE-011 已裁定——solo 单 session 主导下，多 Agent 常驻协作的协调成本高于其决策质量收益；红蓝对抗（对抗性验证既有设施）以单 Agent 成本获得对立视角，是单人项目的性价比最优解。00_index §1 目标架构仍写"投票优先"，两处口径张力登记 §6 Q2 待人裁定（00_index 归 AI-FILL-00 维护，本文只登记不修改）。

**Why 可选模式仍保留投票壳施工**：①引擎（A2AVoting）已 production，壳体 <100 行，沉没成本极低；②"可选模式"不是"废弃"——高价值评审场景（如因子入库终审）多候选裁决仍有真实需求；③壳施工即获得启用能力，避免需要时临时赶工。辩论优先未采纳为主机制：多轮串行交互成本数倍于投票，且"人调度多会话"形态下辩论需要人做多轮搬运工（FactorMAD 对抗互评的取舍分析见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §4 FactorMAD 条目）。

**Why 消费既有引擎而非新造**：A2AVoting/A2ADebate 均 production 且有测试覆盖（§2.4），新造投票逻辑=双真源；"<100 行"指编排壳（候选收集+调引擎+落盘），不含引擎本体（§6 Q2）。

### 3.7 涌现行为检测设计

**决策**：不新造检测器——消费 MOD-RK-14（ai_agent_monitor）既有输出，施工点是**介入闭环接线**：is_breached/CRITICAL 信号 → 告警（复用 `shared/alerts/alert_escalation.py` 既有升级设施）→ 人工介入 SOP（查看状态机/轨迹异常明细/指纹偏差三源明细→裁定降级或暂停）→ 严重情形联动既有 kill switch 设施（skill 治理链已 production，见 11 号文 §2.4）。深度安全语义（串谋 9 种/目标劫持/自治边界违反）归 15/16 号文，本文不重复。

**Why 接线而非重建**：检测三件套+组装件全部 production 且有测试，缺口只在"检出后怎么办"；重建检测=推翻既有资产。告警介入按日频/周频批量复核（§2.3），不做实时自动处置——自动处置的裁定权在 15 号文自治边界。

### 3.8 与证据/技能/模块工厂的协同设计

**决策**：反思产出三向分流（全部日频批量）——①失败原因与归因挂证据链（11 号文 MOD-EVIDENCE_CHAIN，planned）：反思记录作为证据条目支撑/反驳相关假设；②验证过的失败模式入 PreFlect 库（§3.3）；③生成类任务的失败案例回流模块工厂作再生成负案例（13 号文 §4.7 接口）。L2 归纳出的有效模式（非失败）按 11 号文技能沉淀流程提交候选，自反Agent不直接写技能库。

**Why 分流而非集中存储**：三类产出的消费方、验证门、生命周期都不同——证据条目随假设生灭、失败模式需人工确认才进预反思库、再生成负案例直接进 prompt。集中存储会让三类语义互相污染；分流后每类流向单一真源，与 11 号文"单向三段闭环"裁定同构。

---

## 4. 施工计划

> depgraph L1 铁律：凡新建模块，第一步用 `apply_depgraph`（`scripts/governance/apply_depgraph.py`）登记设计态（status=planned），验证通过后最后一步翻转 production。禁止先施工后补登记。

### 4.1 第 0 步：depgraph 登记（L1 铁律，先于一切施工）

1. 用 `apply_depgraph --add-design-node` 将以下依赖登记到 depgraph 设计态（status=planned）：
   - `MOD-REFLEXION_AGENT`（新，自反Agent：三角色+L1/L2/L3+PreFlect+ReflCtrl，落点 `src/zephyr/intelligence/reflexion/`）→ 消费：`MOD-EVIDENCE_CHAIN`（11 号文登记，planned，证据挂链）；产出消费方：模块工厂（13 号文，负案例回流）、PreFlect 库（自维护）
   - `MOD-VOTE_REVIEW_SHELL`（新，投票评审壳，可选模式设施见 §3.6，落点 `src/zephyr/intelligence/reflexion/` 内）→ 消费：`MOD-INF-025`（A2AVoting/A2ADebate 引擎，只消费不改结构）
   - 涌现介入接线不新建节点——消费 `MOD-RK-14` 既有输出，接线改动落在既有告警/运维设施的消费侧
2. 全部施工验证通过后，最后一步统一 `--transition-design-maturity` 将上述登记项 status planned → production（见 §4.7）。

### 4.2 Phase 0（P0）：L1 单轨迹反思 + 三角色骨架

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P0-1 | 反思记录 schema | 结构化反思记录契约（任务标识/输入摘要/结果指标/归因分类/改进建议/置信度），JSON 落盘 `data/brain/reflections/` | schema 校验单测通过；缺必填字段被拒 |
| P0-2 | 三角色骨架 | Actor→Evaluator→SelfReflection 逻辑角色分离的可调用流程，Evaluator 输出结构化评估报告 | 同一任务分角色跑通全流程；评估报告字段完整可追溯 |
| P0-3 | L1 反思器 | 单轨迹复盘：消费执行轨迹+评估报告→产出 L1 反思记录 | 人工构造失败轨迹→归因分类与改进建议非空且可追溯到轨迹片段 |
| P0-4 | 批量入口 | 盘后批量触发入口（手动+计划任务挂点），盘中零调用 | 批量跑 N 条历史任务轨迹产出反思记录落盘；盘中路径零调用（静态扫描佐证） |

### 4.3 Phase 1（P1）：ReflCtrl + 投票评审壳 + PreFlect 库

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P1-1 | ReflCtrl 频率闸门 | §3.4 显式触发规则集（含 L1 强制三条件/Agent-R 四场景阈值/分层频率/决策矩阵参数）+单任务反思轮次上限，规则可配置可审计 | 规则外触发请求被拒；每次放行可追溯到触发规则；token 消耗统计落盘 |
| P1-2 | 投票评审壳（可选模式设施） | 候选文件收集→调 A2AVoting 计票→选最优落盘，壳体 <100 行（引擎复用）；默认不启用，由人在高价值评审场景触发 | 3 候选构造集跑通 approve/reject/abstain+quorum 全路径；MOD-INF-025 源文件零改动（git diff 佐证）；壳体行数实测 <100；无自动触发路径（静态扫描佐证） |
| P1-3 | PreFlect 失败模式库 | 失败模式条目 schema（模式/触发条件/规避建议/来源反思 ID）+任务启动时检索注入 | L2 产出可入库；注入内容含来源反思 ID；人工编辑接口可用 |
| P1-4 | 多会话投票 SOP（可选模式） | "人多开 3-5 会话并行产出→收齐→计票"的操作规程（文档化，文件落盘交接约定），与单 Agent 主路径的启用边界写清 | SOP 走完一次真实评审；交接文件齐全无口头传递；启用边界文档化 |

### 4.4 Phase 2（P2）：L2 同类任务反思 + 对抗互评增强 + 涌现介入接线

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P2-1 | L2 反思器 | 同类任务累积 N=5 触发，跨轨迹归纳共性失败模式与有效参数区间，产出分流（§3.8） | 构造 5 条同类轨迹→归纳产出含共性模式；不足 N=5 不触发 |
| P2-2 | FactorMAD 式对抗互评 | 人发起的辩论制评审：调 A2ADebate/agent_debate 跑主张→反驳→合成，用于因子评审等高价值场景 | 一次真实因子评审跑通三轮；DebateResult 落盘含 synthesis；无自治循环（静态扫描佐证无定时自触发） |
| P2-3 | 涌现告警介入接线 | MOD-RK-14 is_breached/CRITICAL → 告警升级 → 人工介入 SOP（三源明细查看→裁定）→ 严重联动 kill switch | 故障注入构造 CRITICAL→告警到达+SOP 启动留痕；MOD-RK-14 源文件零改动 |
| P2-4 | 证据链挂接 | 反思记录作为证据条目挂接 MOD-EVIDENCE_CHAIN（11 号文 Phase 0 落地后对齐条目格式，见 §6 Q4） | 抽样验证反思 ID 与证据条目外键一致；日频批量写入盘中零实时 |
| P2-5 | 修正闭环与效果验证 | §3.5 后半段落地：修正按三分类分流（ai_modifiable 自动/human_gated 审批/immutable 仅记录）+修正后 N=5 次同类任务效果对比（Sharpe/IC/准确率）+下降>5% 回滚+确认后写情景记忆/更新 Agent Card | 构造修正前后对照集→验证判定与回滚留痕可追溯；三分类分流与 15 号文注册表判定一致；immutable 类零自动应用（静态扫描佐证） |

### 4.5 Phase 3（P3，远期）：L3 跨任务反思 + 模块工厂闭环

> 远期属性显式标注：L3 需大量任务数据积累才有意义，启动条件=L1/L2 稳定运行且反思记录 ≥100 条。

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P3-1 | L3 反思器 | 跨任务类型审视方向与目标对齐，输出研究方向建议（人工裁定后生效）；元反思（§3.1 第四维度）随 L3 同期评估启动，频率 ≤1 次/周 | 建议清单产出且全部经人工裁定留痕；无自动方向变更 |
| P3-2 | 模块工厂闭环接线 | "生成→验证→反思→再生成"闭环：反思负案例注入再生成 prompt（13 号文 §4.7 接口） | 失败模块经反思后再生成的 prompt 含结构化负案例；闭环全链路留痕 |

### 4.6 与其他文档的接口

**与 [11_evidence_skill_router.md](11_evidence_skill_router.md) 的接口（反思→证据/技能）**：11 号文已填充 v0.2.0——证据关联组件 MOD-EVIDENCE_CHAIN 登记为 planned（其 §4.1），条目含三态+来源+假设外键+hash 固化。本文反思记录作为证据条目挂链时遵循其 schema；条目格式的字段级对齐待其 Phase 0 落地后核对（§6 Q4）。有效模式→技能候选走其 §3.2 登记流程，本文不直接写技能库。

**与 [13_module_factory.md](13_module_factory.md) 的接口（反思→再生成）**：13 号文已填充 v0.2.0，其 §4.7 已登记接口假设——①输入方向：L1/L2 反思输出（验证失败/人审驳回的结构化原因）作再生成 prompt 负案例；②输出方向：模块工厂验证失败案例+人审拦截记录作反思语料；③Evaluator 评估报告格式与其 §3.5 四级报告兼容；④批量触发不逐条实时。本文 §3.1/§3.2/§3.4 已按此假设设计（schema 字段含归因分类=负案例载体、Evaluator 报告格式对齐、ReflCtrl 批量纪律），其 Q3 与本文 §6 Q3 联动关闭。另：其 §4.7 引用的"节省 20-80% token"为本文自定设计目标（§2.3 口径修正），非 00_index 口径。

**与 [15_autonomy_boundary_risk.md](15_autonomy_boundary_risk.md) / [16_ai_security_ops.md](16_ai_security_ops.md) 的接口（涌现→安全运维）**：涌现检测的深度安全语义（串谋/目标劫持/自治边界）与自动处置裁定权归 15/16 号文（当前均为骨架，见 §6 Q7）；本文只做 MOD-RK-14 信号的告警介入接线（§4.4 P2-3），若 15/16 填充后定义不同的介入链路，以其为真源修订本文。另：HITL 低置信→反思触发的消费接口登记——置信度 50-69%→L1 / <50%→L1+L2（草稿源 23-D-AUT-PERM §10.6.2），置信度分级处置阶梯真源在 15 号文；15 号文 v0.2.0 尚无 50-69% 刻度（现有 confidence<0.3 回归+L0~L3 阶梯），阈值口径登记 §6 Q9 待裁定。修正闭环的三分类分流（§3.5）复用 15 号文 ai_modifiable/human_gated/immutable 注册表判定。

**与交易决策侧的关系**：只读不改。61 号备忘 §2.3、30 号文 §5 为引用真源；投票评审用于策略/因子评审时不进下单热路径；发现需同步改的记 §6 待用户裁定。

### 4.7 收尾验证与 depgraph 状态翻转

1. Phase 0/1 全部验收项通过，Phase 2 滚动推进，Phase 3 满足 §4.5 启动条件后启动；
2. 新增组件专项测试全绿，既有测试（tests/a2a/、test_ai_agent_monitor、test_emergent_behavior_detector、test_agent_debate 等）回归全绿（证明只消费未破坏基座）；
3. MOD-INF-025 / MOD-RK-14 源文件零改动复核（git diff 佐证"只消费不改结构"）；
4. 反思记录落盘可追溯（schema 完整+ReflCtrl 触发留痕）；
5. 上述全部满足后，`apply_depgraph --transition-design-maturity` 将 §4.1 登记项 status planned → production。

---

## 5. 不做什么

| # | 不做项 | 理由 |
|---|------|------|
| 1 | 不做 agent 编排系统 | 61 号备忘 §2.3 已定稿裁定：多 AI 协作=人调度多会话；`multi_agent_orchestrator.py` 桩不扩为编排器，a2a 编排基座（任务分派/自治协调）不启用 |
| 2 | 不做运行时自治多Agent通信/消息队列 | AI 会话间不直接通信（61 号备忘 §2.2），候选收集与结果发布全部文件落盘交接 |
| 3 | 不做自治 LLM 多Agent辩论循环 / R&D-Agent 自进化策略搜索；不把投票优先当常驻主路径 | 30 号文 §5：辩论/自进化搜索暂缓（重评条件=可控性方案验证可靠）；CC-14 投票优先已降级为可选模式（#ARCH-OE-011），主路径=单 Agent 决策+red_blue_validator；FactorMAD 式对抗互评降级为人发起的 Phase 2 可选增强（§3.6） |
| 4 | 不做 L3 跨任务反思近期施工 | Phase 3 远期（§4.5 启动条件显式标注）；数据积累不足时跨任务归纳无统计意义 |
| 5 | 不做盘中实时反思/投票/涌现复核 | 日频批量盘后窗口（§2.3 频率约束+TiMi 开发/部署解耦印证）；不进下单热路径；Agent-R 四场景延迟目标为源设计实时档参数，本项目不启用实时档（§3.4） |
| 6 | 不新造投票/辩论/仲裁引擎 | MOD-INF-025 89 个 production 文件已覆盖（§2.4），新造=双真源；编排壳只消费 |
| 7 | 不新造涌现检测器 | MOD-RK-14 组装件 production（§2.4）；本文只接告警介入链路，深度安全语义归 15/16 号文 |
| 8 | 不做自由文本感想式反思 | 反思载体是结构化可计算对象（§3.1），下游机读消费要求字段化 |
| 9 | 不做学习式反思触发模型 | 反思触发用显式规则集（ReflCtrl，§3.4），可审计；学习模型数据稀薄且不可审计 |
| 10 | 不做无闸门连续反思 | ReflCtrl 频率控制是一等功能（§3.4），无约束反思循环=token 成本失控；元反思频率 ≤1 次/周（§3.1） |

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | 自反Agent的施工顺序——先 L1 单轨迹反思还是直接上 L1+L2？ | 待裁定 | §4 已按"L1 先行（Phase 0）、L2 待 N=5 累积（Phase 2）"排期；与 00_index §7 Q3 同源联动裁定 |
| Q2 | 投票优先的口径张力与"投票<100行代码"是否足够？ | 待裁定 | 30 号文 §5（#ARCH-OE-011）已将 CC-14 投票优先降级为可选模式，00_index §1 目标架构仍写"投票优先（3-5 Agent 投票→选最优）"——两处口径待人裁定统一（00_index 归 AI-FILL-00 维护，本文只登记）；本文按裁定为真源把投票壳定位为可选模式设施（§3.6），<100 行指编排壳（候选收集+调引擎+落盘），引擎本体复用 MOD-INF-025 A2AVoting |
| Q3 | 与 13 号文 §4.7 接口假设是否对齐？ | 待联动关闭 | 13 号文已填充 v0.2.0，其 §4.7 假设（负案例 schema/Evaluator 报告格式/批量触发）与本文 §3.1/§3.2/§3.4 设计一致（§4.6 逐条核对）；其 Q3 与本文联动，待人确认后双关 |
| Q4 | 反思记录挂证据链的字段级格式？ | 待 11 号文 Phase 0 落地 | 11 号文 v0.2.0 已登记 MOD-EVIDENCE_CHAIN（planned），证据条目三态+外键+hash 结构已定；反思 ID↔证据条目外键的字段映射待其 Phase 0 实现后核对（§4.4 P2-4） |
| Q5 | a2a_protocol 89 文件编排基座与"不做编排系统"裁定的处置边界？ | 待裁定 | 本文口径：投票/辩论引擎单件被"人调度多会话"消费（不违反裁定），编排层不启用；基座其余设施（layer1/2 通信、54 个 layer3 协调件）的保留/精简处置涉及 depgraph 域裁定，超出本文范围，待用户裁定（可转 03/05 号文范围） |
| Q6 | PreFlect 失败模式库冷启动是否允许人工种子集？ | 待裁定 | L2 反思累积前库为空，预反思无输入；建议允许人工编写首批种子条目（来源标注 manual_seed），待裁定 |
| Q7 | 涌现介入链路与 15/16 号文的最终分工？ | 待 15/16 号文填充 | 15/16 号文当前为骨架；本文 §4.4 P2-3 按"告警+人工介入 SOP"施工，若其定义自动处置/不同介入链路，以其为真源修订本文（§4.6） |
| Q8 | 涌现检测状态机顺序口径——16 号文 §2.4 与代码实测颠倒 | 待 AI-FILL-16 修正 | 代码实测（`emergent_behavior_detector.py`）：枚举声明序 STABLE→CORRELATING→CRITICAL→HYSTERETIC，迁移逻辑=高相关对≥3→CRITICAL / ≥1→CORRELATING / 无高相关但已设压前基线→HYSTERETIC / 否则→STABLE；本文 §2.1/§2.4 口径与代码一致，16 号文 §2.4 写作"STABLE→CORRELATING→HYSTERETIC→CRITICAL"与代码颠倒——16 号文归 AI-FILL-16 维护，本文只登记不修改 |
| Q9 | HITL 低置信→反思触发的置信度阈值口径 | 待 15 号文裁定 | 草稿源 23-D-AUT-PERM §10.6.2：置信度 50-69%→触发 L1，<50%→触发 L1+L2；15 号文 v0.2.0 尚无对应置信度阶梯（现有 `autonomy_regressor.py` confidence<0.3 回归 + L0~L3 有界自治阶梯）；本文 §3.4 登记为候选触发规则，最终阈值以 15 号文裁定为准 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景（实测盘点：自反Agent 零设施/多Agent 89 文件基座零消费/涌现检测已 production 未闭环；吸收 30 号文 §5 #ARCH-OE-011 裁定——投票优先降级为可选模式）、§3 设计决策（三级反思/三角色/PreFlect/ReflCtrl/多Agent协作可选模式/涌现接线/协同分流七节 why+替代方案）、§4 施工计划（depgraph 登记先行+Phase 0~3+11/13/15/16 接口对齐）、§5 不做什么 10 项、§6 开放问题扩至 Q1~Q7 | AI-FILL-12 按指令块执行填充 |
| 2026-08-17 | 0.3.0 | 草稿源回填+口径修正：①§3.1 增补 L2 TiMi 数学反思闭环增强（约束优化 scipy 精确求解，仅限可形式化参数）与元反思第四维度（经验回放→反思提炼→技能注册→元反思，≤1 次/周，R-45）；②§3.4 ReflCtrl 补具体参数（L1 强制三条件/Agent-R 四场景阈值+延迟目标/分层频率 80-50-20%/决策矩阵）并登记 HITL 低置信触发（50-69%→L1、<50%→L1+L2，23-D-AUT-PERM §10.6.2）；③§3.2 补 Generator(GLM-5.1)/Critic(DeepSeek V4 Pro)/Judge(Claude) 多模型分工反馈循环（收敛≤3 轮）及与 13 号文生产侧分工注记；④新增 §3.5 修正闭环与效果验证（三分类分流/N=5 对比/下降>5% 回滚/写情景记忆+Agent Card），原 §3.5~3.7 顺延为 §3.6~3.8，§4.4 补 P2-5、§4.5 P3-1 挂元反思；⑤口径修正："节省 20-80% token"实测非 00_index §1 口径，更正为本文自定设计目标（ReflCtrl 论文实测 33.6%）；⑥涌现状态机顺序按代码实测核实（本文口径与代码一致，16 号文 §2.4 颠倒登记 Q8）；⑦开放问题新增 Q8/Q9 | AI-FILL-12-R2 按指令块执行回填 |

---

*维护者：AI 架构协调者*