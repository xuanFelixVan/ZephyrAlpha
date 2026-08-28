---
ttl: permanent
doc_type: architecture_view
title: AI 安全与自治运维施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.3.1"
date: 2026-08-18
topic: ai_security_ops
scope: 09_ai_architecture
---

# AI 安全与自治运维施工图

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：事件总线+TNR+保命轨落地——security_event_bus.py（MOD-SEC-EVENTBUS：统一 schema pydantic 严校+四域 adapter+高危告警 webhook 不可达本地持久化不丢）+TNR 演练（.runtime/security_events/tnr_drill/ 产物+tnr-drill 报告，可撤销+不恶化双达标）+保命轨 runbook（emergency-runbook 报告，RTO<5min）+incident_pipeline.py+killswitch_response_levels.py（KILLSWITCH 三级响应）。
> **最终成果**：GP0 验收口径落地（安全事件统一总线+应急保命轨可用）。
> **未做+原因**：Detect→Diagnose→Remediate→Learn 统一自愈管线、修复策略库落盘（data/fix_patterns/ 未建）、A-L0~A-L4 成熟度代码——均属 GP1+。

> 本文定位：AI 安全（LLM 4层 guardrails + Agent 安全 + MCP Triple Gate + KILLSWITCH）和自治运维闭环（Detect→Diagnose→Remediate→Learn + TNR + 成熟度分级 + 知识库 + 保命轨）的施工。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md) §3.3/§3.4（机制设计真源，本文不复制），LLM 安全栈层内设计与集成接线见 [09_llm_security_integration.md](09_llm_security_integration.md)，自治边界/Kill Switch 五套实现/Drift 防护见 [15_autonomy_boundary_risk.md](15_autonomy_boundary_risk.md)。
> **真源边界**：G1~G4 与 L0~L8 的映射口径真源 = 09 号文 §3.2；MCP Triple Gate 映射真源 = 09 号文 §3.3；三分类/Kill Switch 设施盘点真源 = 15 号文 §2.4。本文只负责：①Agent 安全四威胁（串谋/涌现/幻觉/记忆投毒）的设施收口；②KILLSWITCH 三级响应的策略层定义；③自治运维闭环（Detect→Diagnose→Remediate→Learn + TNR + 成熟度 + 知识库 + 保命轨）的施工排序与验收。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | AI 安全与自治运维 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·横切层（AI 安全 + AI 自治运维） |
| 依赖 | [09_llm_security_integration.md](09_llm_security_integration.md)（LSG 集成，v0.2.0 已填充）+ [15_autonomy_boundary_risk.md](15_autonomy_boundary_risk.md)（自治边界，v0.2.1 已填充）+ MOD-INF-031 AutoFix Engine 蓝图 + MOD-INF-022 Escalation Protocol 蓝图 |
| 优先级 | P0——AI 安全是所有 AI 能力的信任锚点 |
| 状态 | draft（骨架填充完成） |

---

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是个人 + 100% AI 生成代码的 A 股量化交易系统。当 AI 既是代码唯一生产者、又逐步获得运行时行为能力时，需要两层横切保障：**AI 安全**（防注入/防串谋/防涌现/防幻觉/防记忆投毒/防越权）与**自治运维**（故障自己发现、自己诊断、自己修复、经验自己沉淀）。两层机制在 [00_index.md](00_index.md) §3.3/§3.4 均标「设计完成」，本文的施工起点是对实现侧做实测收口。

实现侧当前状态（2026-08-17 磁盘实测，明细见 §2.4）：

1. **LLM 安全栈（G1~G4 / L0~L8）层内实现约 80%，集成接线归 09 号文**。LSG（`src/zephyr/security/llm_defense/llm_security/`）L0~L8 十层全部有代码，`tests/llm_security/` 60 个测试文件。本文不重复施工，只消费其产出（安全事件流）。
2. **Agent 安全检测器广泛存在但分散在四域，无统一事件出口**。实测分布：D_SECURITY `access_control/`（guards 18 个 + detectors 6 个 + orphan_judge 24 个 + verifiers 5 个 + 根级 49 个，共 102 个非 `__init__` 模块）、`governance/security_governance/`（20 个模块，含 `memory_poison_guard.py`/`ipi_defense.py`/`poison_cascade_detector.py`/`persuasion_detector.py`/`ghost_scan.py`）、D_FBL_DETECTORS `feedback_loop/detectors/`（59 个检测器模块，含 `emergent_behavior_detector.py`/`agent_trajectory_anomaly_detector.py`/`gradual_poisoning_detector.py`/`context_window_contamination_detector.py`）、D_RISK `risk/core/ai_agent_monitor.py`（MOD-RK-14，组装涌现+轨迹+指纹三路评分：risk_score = 0.4×emergence + 0.3×trajectory + 0.3×fingerprint）。两个实测缺口：①00_index §3.3「串谋检测 9 种探测 + 举报人机制」中的**举报人机制无代码对应物**（全仓检索 whistleblower/举报人 零命中，现有 `multi_agent_collusion_detector.py` 只做交互频率+通道可疑度检测）；②**KILLSWITCH 三级响应（level_1/level_2/level_3）在 src 侧无统一实现**（grep `level_1|global_critical|KILLSWITCH` 仅命中 1 个无关文件），当前由 15 号文 §2.4-C 盘点的 5 套独立 Kill Switch + LSG L5 预算熔断分担其职能。
3. **自治运维闭环四环节零件齐备，但无统一管线**。Detect 侧有 59 个 FBL 检测器 + LSG L6 审计 + `shared/io/workspace_telemetry.py`；Diagnose 侧有 `orchestrator/resilience/failure_matcher.py`（FailurePatternMatcher，失败模式识别+纠正建议）、`backtest/services/anomaly_diagnoser.py`、`infrastructure/auto_diagnostics.py`；Remediate 侧有 `infrastructure/auto_fix_engine/`（30 个 .py，MOD-INF-031：三通道修复管道 + 8 状态生命周期 + WAL 原子修复 + SafetyGate/FixBudget/CascadeBreaker + ShadowWorkspace + CanaryFixer，不变量「修复 MUST 通过 SafetyGate+FixBudget+CascadeBreaker；行为审计 RED 永不自动修复」）；Learn 侧有 `fix_pattern_miner.py`、`feedback_loop/collectors/knowledge_capture.py`、`shared/alerts/alert_precision_tracker.py`。**断点在「连」不在「件」**：四个环节各自有产出口，但没有统一事件 schema 把它们串成「事件→诊断→修复→沉淀」的自动流。
4. **知识库与成熟度只有设计/雏形**。00_index §3.4 的四件知识库中：故障模式库有运行时代码（`failure_matcher.py` 内置模式）但无落盘库；修复策略库蓝图登记为 `data/fix_patterns/pattern_index.yaml`（REG-AFX-PATTERN-001，draft）——**磁盘实测该目录不存在**；根因因果图、假阳性记录无独立设施（`alert_precision_tracker.py` 承载部分假阳性统计）。自治成熟度 A-L0~A-L4 无代码对应物（15 号文实测另有 `autonomy_maturity.py` 的 L0~L4 运行时信任阶梯，是不同语义标尺，见 §6 Q4）。保命轨 D-L0~D-L3 无统一编排，零件散落在 `governance/resilience_governance/`（20 个模块：`last_resort_watchdog.py` 终极逃生舱 /`f5_shutdown_manager.py`/`circuit_breaker.py`/`offline_resilience.py`/`fail_mode_manager.py` 等）与 `governance/escalation/`（19 个模块：`escalation_engine.py`/`incident_response.py`/`owner_absent.py` 等）。

### 2.2 核心问题

1. **四域安全检测的事件如何汇入一个可消费的统一事件流？** LSG L6 有 `behavior_audit_logger.log_security_event()`，access_control 有 `observability.py`，FBL 检测器各自 print/log——没有统一事件 schema 和落盘协议，Detect 环节无法机器消费。
2. **修复动作如何满足 TNR（可撤销 + 不恶化）？** auto_fix_engine 的不变量已承载 TNR 语义（SafetyGate 前置拦截 = 不恶化的预防；WAL + ShadowWorkspace + CanaryFixer = 可撤销+验证后不恶化），但「可撤销」依赖 Rollback（MOD-INF-021）接线、「不恶化」依赖修复后回归验证，两条链路当前无端到端验收基线。
3. **闭环成熟度 A-L0~A-L4 如何逐级解锁？** 与 15 号文实测发现的三套自治等级标尺（PS-VOC-021 / AutonomyMaturity L0~L4 / AutonomyGuard level1~3）语义不同——A-L 系是「运维闭环的自治深度」，需裁定映射关系（§6 Q4）。
4. **知识库冷启动：先建库还是先建闭环？** 无库则 Diagnose 只能靠通用规则、Learn 无沉淀物；无闭环则库无数据来源。本文在 §4 给出「记录优先、并行冷启动」的候选方案（§6 Q2）。
5. **KILLSWITCH 三级响应与 15 号文 5 套 Kill Switch 什么关系？** 15 号文已定「两级编排」设计（系统级总开关 + 域级分开关 + 4 条收敛规则）；00_index §3.3 的三级响应是策略层语义。策略层与两级编排的叠加映射是本文施工项（§3.4、§6 Q3）。

### 2.3 约束条件

以 [system_charter.md §2 硬边界约束](../../04_architecture_principles_decisions/system_charter.md) 为唯一判定基准，与本文直接相关的：

| 约束 | 对本文设计的影响 |
|---|---|
| 约束一（1 人全栈 + 100% AI 生成代码） | 安全检测与自愈必须自动化优先，人只做审批与裁定；自愈动作必须 TNR，因为没有人力兜底每次修复 |
| 约束二（单机 i7-12700KF / RTX 3090 / 64GB / 30Mbps） | 不接外部安全服务（第三方 SOC/内容审核 API 延迟成本不可控）；Drift/涌现等深度检测走日频/周频批量，不进实时热路径 |
| 约束四（T+1、Tick=3 秒） | LLM 不在下单热路径（09 号文 §2.3 同口径），安全栈延迟预算 P95<50ms 只约束交互式施工体验，不约束交易 |
| 约束五（单机无热备，RTO<5 分钟） | 自愈必须以「降级 + 人工 override」为兜底，不追求全自动无人工；保命轨触发后恢复流程必须简单（文件标志位 + 人工复位） |
| 约束六（交叉验证 + 依赖锁定 + 自治熔断） | AI 生成的修复代码与人工代码同标准过 gate；自治熔断（亏损超限/置信度低 → 仅建议模式）是运维闭环降级的直接依据 |

### 2.4 已施工设施盘点

> 实测时间：2026-08-17（LS/Glob/Grep/Read 验证）。文件数为非 `__init__.py` 模块数。状态取文件头 `[MATURITY]` 锚定或蓝图登记。

**A. LLM 安全栈（详细盘点真源 = [09_llm_security_integration.md](09_llm_security_integration.md) §2.4，此处只列本文直接消费的接口）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 安全事件产出口 | `src/zephyr/security/llm_defense/llm_security/behavior_audit_logger.py` | L6 安全事件审计日志（`log_security_event()`），本文 Detect 环节的主消费源 | production |
| 网关判决 | `.../llm_security/gateway.py` + `protocol.py` | fail-closed 闸门与 SecurityContext/判决数据模型 | production |
| 资源熔断 | `.../llm_security/layers/l5_resource_protection.py` | L5 预算/资源熔断（KILLSWITCH 触发时 LSG 侧表现为 L5 全量熔断，09 号文 §4.6 口径） | production |
| 仪表板 | `.../llm_security/dashboard/app.py` | Streamlit 安全仪表板（含误报统计） | production |

**B. Agent 安全检测（四威胁对应设施）**

| 威胁 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 串谋检测 | `security/access_control/detectors/multi_agent_collusion_detector.py` | 交互频率 + 隐蔽通道（covert/hidden/side_channel）可疑度检测，阈值 3 次 | production |
| 串谋检测（组装） | `risk/core/ai_agent_monitor.py`（MOD-RK-14） | 涌现+轨迹+指纹三路加权风险评分，is_breached 阈值 0.6 | production |
| 涌现检测 | `feedback_loop/detectors/anomaly/emergent_behavior_detector.py` | 系统级熵/耦合强度/相关维度监控；四态枚举 STABLE/CORRELATING/CRITICAL/HYSTERETIC，迁移逻辑（2026-08-17 源码实测）：高相关对≥3→CRITICAL（最高严重度，recommendation=investigate_coupling）、≥1→CORRELATING、无高相关对但存在应力前基线→HYSTERETIC（滞后观察态，非严重度序列中的一级）、否则 STABLE（盲点 R473） | production |
| 幻觉防护 | LSG L3 输出安全（幻觉检测，09 号文域）+ `access_control/detectors/false_completion_detector.py` | L3 四层输出验证；虚假完成检测（声称完成但产出不足） | production |
| 记忆投毒 | `governance/security_governance/memory_poison_guard.py` + `access_control/guards/memory_provenance_guard.py` + `gov_drift/baseline_poisoning_guard.py` + `feedback_loop/detectors/drift/gradual_poisoning_detector.py` + `detectors/drift/context_window_contamination_detector.py` + LSG `poisoning_monitor.py` | 存储前检测 + 来源溯源 + 基线防投毒 + 渐进投毒检测 + 上下文窗口污染检测 + LSG 投毒监控（00_index §3.3「记忆投毒 6 层防御」的六个实现落点） | production |
| 越权/注入 | `access_control/guards/`（18 个：input/output/rbac/abac/path/toctou/sequence/rule_injection/replay_attack/memory 等）+ `security_governance/ipi_defense.py` | 间接注入防御 + 操作守卫层 | production |
| 举报人机制 | — | 00_index §3.3 设计项，全仓检索无实现 | **P4 远期（2026-08-18 裁定降级，MVP 设计保留 §3.9）** |

**C. 监控与诊断（Detect / Diagnose）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 检测器群 | `feedback_loop/detectors/`（anomaly 11 + correlation 16 + drift 7 + guard 10 + reliability 15 = 59 个模块） | 异常/关联/漂移/自守卫/可靠性五族检测器 | production |
| 行为漂移检测 | `access_control/detectors/context_drift_detector.py` + `anomaly_detector.py` + `cross_session_detector.py` | 操作链上下文漂移 + 行为异常 + 跨会话检测 | production |
| 失败模式识别 | `orchestrator/resilience/failure_matcher.py` | FailurePatternMatcher：订阅 task FAILED → 分析原因 → 生成纠正建议（FailureDiagnosis） | production |
| 回测异常诊断 | `backtest/services/anomaly_diagnoser.py` | 回测域异常诊断 | production |
| 通用诊断 | `infrastructure/auto_diagnostics.py` | 基础设施自动诊断 | production |
| 工作区遥测 | `shared/io/workspace_telemetry.py` | 工作区级遥测采集 | production |

**D. 修复与自愈（Remediate）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 自动修复引擎 | `infrastructure/auto_fix_engine/`（30 个 .py，MOD-INF-031） | 三通道修复管道（结构→模板化 100% 确定 / 语义→LLM Bridge 95~98% 置信 / 行为→Block+Alert 永不自动修复）+ 8 状态生命周期 + WAL 原子修复 + 病因修复法九阶链 | production |
| 修复安全 | `auto_fix_engine/fix_safety.py` | SafetyGate（保护路径/模式拦截）+ CascadeBreaker（修复风暴熔断）+ SecretLeakGuard（密钥泄露 100% 拦截）+ WriteSafety | production |
| 修复可靠性 | `auto_fix_engine/fix_reliability.py` | ApprovalQueue / BlastRadiusEstimator / CanaryFixer / ConflictResolver / DeadLetterQueue / IdempotencyGuard | production |
| 修复预算 | `auto_fix_engine/fix_budget.py` | FixBudget + FixStormGuard | production |
| 影子验证 | `auto_fix_engine/shadow_workspace.py` | 修复影子工作区（先影跑后落地） | production |
| 自愈代理 | `auto_fix_engine/self_heal_agent.py` | 自愈编排代理 | production |
| 语义自愈 | `governance/semantic_audit/self_healer.py` + `self_health.py` | 语义审计域自愈 | production |
| 回滚 | `infrastructure/rollback/`（含三级 Kill Switch，MOD-INF-021） | 可撤销性的执行机构（15 号文 §2.4-C 盘点） | production |
| 修复配置 | `infrastructure/auto_fix_engine/auto_fix_config.yaml` | SafetyGate/预算/保护路径配置 | production |

**E. 升级、保命与熔断（Recover 兜底）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 升级引擎 | `governance/escalation/`（19 个模块：escalation_engine / incident_response / triage / owner_absent / escalation_loop_detector 等，MOD-INF-022） | 事件响应与升级路由 | production |
| 韧性治理 | `governance/resilience_governance/`（20 个模块） | `last_resort_watchdog.py`（终极逃生舱：所有 escalation 失败后的 final fallback+shutdown）/ `f5_shutdown_manager.py` / `circuit_breaker.py` / `fail_mode_manager.py`（OPEN/CLOSED/DEGRADED/DEAD 四态）/ `offline_resilience.py` / `deadlock_detector.py` / `blast_radius.py` | production |
| Kill Switch | 5 套 + 1 仿真（系统级/交易级/回滚级/技能级/容量级） | 盘点真源 = 15 号文 §2.4-C，本文不复制 | production |
| KILLSWITCH 三级响应 | — | 00_index §3.3 设计项（level_1 P1→暂降 IM 模式 / level_2 P0→暂停 Agent / level_3 global_critical→全局暂停），src 侧无统一编排实现 | **缺口（本文 §4.4 P2-3）** |

**F. Learn 与知识库**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 修复模式挖掘 | `auto_fix_engine/fix_pattern_miner.py` | 修复模式挖掘（Learn 环节核心） | production |
| 知识捕获 | `feedback_loop/collectors/knowledge_capture.py` | 经验知识采集 | production |
| 告警精度 | `shared/alerts/alert_precision_tracker.py` | 告警精度/假阳性统计（假阳性记录的部分载体） | production |
| 修复策略库 | `data/fix_patterns/pattern_index.yaml`（蓝图登记 REG-AFX-PATTERN-001） | 修复模式知识库索引 | **draft（磁盘不存在，本文 §4.3 P1-3）** |
| 修复器注册表 | `_fixer-registry.yaml`（MOD-INF-031 蓝图 §14 登记「未实现」） | 修复器注册 | **缺口（随 P1-3 一并落盘）** |

**G. 对抗验证与测试**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 对抗演练 | `security/adversarial_validation/`（27 个文件：attack_registry / defense_runner / game_day_scheduler / injection_engine / ai_attack_generator 等） | 对抗演练/游戏日/混沌注入 | production |
| 红蓝验证蓝图 | `docs/03_modules/_cross_layer/red_blue_validator/blueprint.md`（MOD-INF-030） | 红蓝对抗引擎设计 | Active |
| 修复域测试 | `tests/fix/`（13 个 .py：test_fix_safety / test_fix_budget / test_fix_reliability / test_fix_pattern_miner 等） | AutoFix 专项测试 | production |
| RBAC 安全测试 | `tests/agent_rbac/`（42 个测试文件，含 test_redteam_adversarial / test_kill_switch_agent_rbac） | 访问控制+对抗测试 | production |
| 升级域测试 | `tests/escalation/`（21 个 .py） | 升级引擎测试 | production |
| 安全测试 | `tests/safety/`（31 个测试文件）+ `tests/llm_security/`（60 个，09 号文域）+ `tests/autonomy/`（71 个，15 号文域） | 安全/LSG/自治专项 | production |

**H. 相关蓝图（只读引用）**

| 蓝图 | 路径 | 与本文关系 |
|------|------|-----------|
| MOD-INF-031 AutoFix Engine | `docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md`（v5.1.2，Active） | Remediate 环节实现真源 |
| MOD-INF-022 Escalation Protocol | `docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md` | 升级/保命轨设计真源 |
| MOD-INF-033 Behavioral Auditor | `docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md`（Draft，activation_phase=requires_100ai） | 行为审计 VERDICT 设计（2026-08-18 裁定：本期不激活模块，事件流只消费 VERDICT(PASS/YELLOW/RED) 语义；AUTOMATION-GATE 三门槛未达前不启用，见 §6 Q6） |
| MOD-INF-030 RedBlue Validator | `docs/03_modules/_cross_layer/red_blue_validator/blueprint.md` | 红蓝对抗设计真源 |
| MOD-INF-018 Agent RBAC | `docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md` | access_control 实现真源（含记忆投毒防护决策 D-018-74） |

---

## 3. 设计决策

### 3.1 LLM guardrails G1~G4 的运维消费口径 why

**决策**：本文采用 [09_llm_security_integration.md](09_llm_security_integration.md) §3.2 的口径——G1~G4 是 LSG L0~L8 的「运行时四段」摘要视图，LSG 是实现载体，两者无功能重叠冲突（该口径待 Owner 确认，见 §6 Q1）。本文不另建 guardrails 体系。

**本文新增的边界（why 需要显式声明）**：LSG 的职责是「检测+阻断+记录」，**不做自愈决策**（09 号文 §4.6 已定）。因此 G1~G4 产生的每一个阻断/告警事件都是本文自治运维闭环的**输入**：G1/G3 的注入与输出拦截事件流入 Detect；G2 的目标偏移检测结果流入 Diagnose（与 15 号文 Drift 防护的行为基线对接）；G4 的权限审计事件流入 KILLSWITCH 三级响应的触发判定。这一「安全栈生产事件、运维闭环消费事件」的分工是两层不重复建设的关键。

### 3.2 Agent 安全四威胁的设施收口 why

**为什么是「收口」而不是「新建」**：实测显示串谋/涌现/幻觉/记忆投毒四威胁各有 production 级检测器（§2.4-B），问题是它们分属四个域、产出格式各异、无人消费。新建统一检测器 = 重复建设 + 破坏已有测试资产（42 个 agent_rbac 测试 + 59 个检测器各自的在库测试）；正确做法是以**统一事件 schema** 收口产出，检测逻辑原地不动。

| 威胁 | 现有设施 | 本文施工动作 | 缺口 |
|------|---------|-------------|------|
| 串谋 | collusion_detector（频率+通道）+ ai_agent_monitor（三路评分） | 事件接入口径统一 | 9 种探测未全覆盖；举报人机制 P4 远期（2026-08-18 裁定降级，§6 Q5） |
| 涌现 | emergent_behavior_detector（熵/耦合/相关维度） | CRITICAL 态 → KILLSWITCH level 判定输入 | 行为基线数据积累期（与 15 号文 Drift 基线共用） |
| 幻觉 | LSG L3 输出验证 + false_completion_detector | 幻觉事件流入 Learn（修复策略库标记易幻觉任务类型）+置信度处置矩阵（§3.20） | 幻觉检测深度化是 LSG 层内事项（09 号文域） |
| 记忆投毒 | 六层落点（§2.4-B） | 投毒事件统一进审计链 + 触发记忆隔离动作 | 跨设施联防策略（哪层先报、谁做最终隔离）未编排 |

### 3.3 MCP Triple Gate 的口径 why

采用 [09_llm_security_integration.md](09_llm_security_integration.md) §3.3 映射（Gate1 输入过滤→L1；Gate2 对齐审查→L4 alignment_scorer+工具描述审计；Gate3 权限隔离→L4 权限最小化+L0 MCP 服务器验证），不单独建 MCP 安全层。本文补一条运维侧要求：**MCP 工具的每次异常调用（Gate 拦截/超时/返回异常）都必须产生标准安全事件**，否则 Triple Gate 的运行态健康无法进入运维闭环的 Detect。

### 3.4 KILLSWITCH 三级响应的策略层 why

**为什么需要三级而不是单一总开关**：爆炸半径不同。level_1（P1 high）只降级单一 Agent 的自治模式（暂降 IM 模式），系统其余部分照常；level_2（P0 critical）暂停涉事 Agent；level_3（global_critical）全局暂停。单一总开关会把「某 Agent 一次可疑调用」放大成「全系统停摆」——对 1 人运维来说，误报造成的全局停摆本身就是可用性事故。

**与 15 号文两级编排的叠加关系（v0.2.1 已对齐口径，残余差异见 §6 Q3）**：三级响应是**策略层**（决定「这次事件该停什么」），15 号文的两级编排是**路由层**（系统级总开关 `security/access_control/kill_switch.py` VR-009 + 域级分开关 + 4 条收敛规则，决定「怎么停」），5 套 Kill Switch 是**执行机构层**。映射候选：level_1 → 技能级（`skill_kill_switch.py`）+ 自治降级（`autonomy_regressor.py`）；level_2 → 系统级单 Agent 阻断（VR-009 的单 Agent 阻断粒度）；level_3 → 系统级全局熔断 + 交易级（`trading_kill_switch.py`）联动。施工时按 15 号文收敛规则落地（影响资金先交易级、全局事故只拉系统级总开关）。

### 3.5 自治运维闭环 Detect→Diagnose→Remediate→Learn 的 why

**为什么四环缺一不可**：

- **Detect**：59 个检测器 + LSG 事件是「感知神经」，但感知不汇聚等于没有——统一事件 schema 是本环节的施工核心。
- **Diagnose**：检测只回答「有异常」，诊断回答「根因是什么、能不能自动修」。`failure_matcher.py` 的模式匹配 + auto_fix_engine 的「病因修复法九阶链」是地基；没有 Diagnose 的闭环会把所有异常都推给人（1 人力不可持续）。
- **Remediate**：auto_fix_engine 三通道已定「行为类问题永不自动修复」——这是 100% AI 生成代码项目的保命线：行为问题（RED）必须人工，结构/语义问题才可自动。
- **Learn**：没有 Learn，同一故障每周复发、每次都要重新诊断。`fix_pattern_miner.py` 挖掘修复模式 → 修复策略库 → 下次 Diagnose 直接命中——闭环的价值随库的增长而增长，这回答了「为什么知识库不能等闭环完善了再建」（见 §4.3 记录优先策略）。

**为什么不是「Detect→AutoFix」两环直达**：跳过 Diagnose 的自动修复 = 按症状吃药。auto_fix_engine 蓝图的三通道设计（结构/语义/行为分流）本身就是 Diagnose 内嵌于 Remediate 的证据；本文把 Diagnose 显式化为独立环节，是为了让「不可自动修」的判决有自己的落盘与升级通道（escalation）。

### 3.6 TNR（Transactional No-Regression）的 why

**决策**：TNR 定义为两条验收不变量——**可撤销**（任何自动修复必须能在 RTO 内回到修复前状态）与**不恶化**（修复后系统健康度不得低于修复前基线）。

**现有承载设施**：可撤销 = WAL 原子修复（auto_fix_engine）+ Rollback 三级（MOD-INF-021）+ ShadowWorkspace（先影跑）；不恶化 = SafetyGate 前置拦截 + FixBudget/FixStormGuard（防修复风暴）+ CanaryFixer（金丝雀验证）+ SecretLeakGuard（修复不引入密钥泄露）。

**why 是「验收不变量」而不是「目标」**：TNR 不可达标的自愈比没有自愈更危险——一次不可撤销的错误修复可能直接破坏交易链路。因此本文把 TNR 写成每个 Phase 的验收门槛（任何自动修复通道上线前必须通过 TNR 演练），而非愿景描述。

### 3.7 自治成熟度 A-L0~A-L4 的 why

**决策**：A-L 系是「运维闭环」的自治深度标尺（00_index §3.4）：A-L0 无自治（只记录）→ A-L1 告警 → A-L2 自愈建议 → A-L3 渐进自治 → A-L4 安全关键自治。它与 15 号文的三套标尺（模块规划等级/运行时信任阶梯/Owner 缺位白名单）语义不同——那些标尺管「Agent 能做什么」，A-L 系管「运维闭环能自动修到什么程度」。已裁定（2026-08-18，§6 Q4 关闭）：A-L 系是另一根轴，不建映射、只做交叉引用。

**why 逐级解锁而非一步到 A-L3**：每升一级的解锁条件 = 上一级连续 N 周零 TNR 违规 + 修复策略库对当期故障模式的覆盖率达标。个人项目没有冗余人力为「自治事故」兜底，成熟度必须用实证换。

### 3.8 知识库与保命轨的 why

**知识库三库一录**：故障模式库（`failure_matcher` 模式落盘化）、修复策略库（`data/fix_patterns/`，蓝图已登记 draft）、根因因果图（Diagnose 判定的结构化沉淀）、假阳性记录（`alert_precision_tracker` 扩展）。**why 记录优先**：库的价值在冷启动期是「给人看的经验文档」，在成熟期是「给 Diagnose 用的匹配库」——先落盘记录，匹配能力是副产物。

**保命轨 D-L0~D-L3**（00_index §3.4：正常运行 → 降级运行 → 保命清仓 → 冻结）：这是「所有自愈失败后的最终退路」，与 `last_resort_watchdog.py`（终极逃生舱）+ `fail_mode_manager.py`（OPEN/CLOSED/DEGRADED/DEAD 四态）+ 交易级 Kill Switch 对接。why 单独一轨：自治运维闭环自身也可能故障（自指风险），保命轨必须独立于闭环可触发——由人工/看门狗直接驱动，不经过闭环的 Diagnose。

### 3.9 串谋检测量化参数基线 why

**why 需要参数基线**：00_index §3.3 已裁定「串谋检测 9 种探测 + 隐写术 + 举报人机制」为设计完成项，但 §2.4-B 实测显示现有 `multi_agent_collusion_detector.py` 只覆盖「交互频率≥3 次 + 隐蔽通道」单维。9 种探测的阈值不落盘成统一参数基线，P0-1 事件 schema 的「威胁类别/严重度」字段就无判级依据，P2-5 红队验收也无打分锚点。参数基线是「收口」的施工内容，检测逻辑仍在各域原地实现。

**9 探测阈值表**（参数真源：安全架构 §6.2 / 22-D-AUT-CORE §8.6；本文登记为事件判级口径）：

| # | 探测 | 度量 | 告警阈值 | 响应动作 |
|---|------|------|---------|---------|
| 1 | Peak Suspicion 峰值可疑度 | Agent 内部状态异常度 | >基线 3σ | 记录+人工审查 |
| 2 | Deception Split 欺骗分裂 | 内部推理 vs 外部输出语义差异度 | >0.4 | 记录+暂停 Agent |
| 3 | Correlation 相关性 | Agent 输出序列互信息 | >基线 2σ | 记录+人工审查 |
| 4 | Ensemble 集成 | 集成分类器串谋概率 | >0.3 | 暂停相关 Agent+人工审查 |
| 5 | Graph 图结构 | 交互图指标偏离度 | >基线 2σ | 记录+调整 Agent 协作关系 |
| 6 | Gap Ratio | 最高与次高欺骗分数比值 | >2.0 | 记录+人工审查 |
| 7 | Collective Score | 全体 Agent 欺骗分数均值 | >0.5 | 记录+人工审查 |
| 8 | Pairwise Correlation | Agent 对激活值 Pearson 相关系数 | >0.7 | 记录+人工审查 |
| 9 | 行为轨迹相似度 | Agent 间行为序列编辑距离相似度 | >0.8 | 记录+人工审查 |

**配套机制参数**：①隐写术通信检测——Agent 间通信信息熵超正常范围 2σ 触发告警，并施加通道容量限制（限制消息长度与频率，压低隐写可用带宽）；②身份轮换——基于任务类型随机分配协作关系，同一组 Agent 持续协作不超过 3 个任务周期，轮换记录写审计链。

**举报人机制 MVP 候选设计**（P4 远期——2026-08-18 裁定降级；00_index §3.3 设计项，src 侧实测无实现，§6 Q5）：独立 Whistleblower Agent，唯一职责是监控其他 Agent 的可疑行为，不参与任何业务逻辑；身份对其他 Agent 保密（防串谋者识别与规避）；可直接向人类报告，绕过正常通信渠道；举报记录加密存储、仅 Trader 可解密查看。MVP 候选设计保留为远期参考，本期不施工（裁定依据见 §6 Q5）。

**隐性串谋登记**（参数真源：风险架构 §15.4）：与显式串谋（策略指纹相似）不同，隐性串谋的策略逻辑不同但行为趋同（多 Agent RL 在重复博弈中自发形成超竞争定价，无需通信）。检测参数=行为相关性>90% 且策略指纹相似度<80% → 执行去耦 + 人工判定。本文将其登记为 Detect 环节事件源；「执行去耦」动作归交易侧风控域，本文不施工。

**金融红队库登记**（参数真源：风险架构 §15.4）：FinJailbreak（金融治理越狱）/AutoRedTrader（合成虚假信息注入，69% 暴露率 + 26.67% 攻击成功率）/FinRedTeamBench（BFSI 多轮自适应红队，RAHS 风险调整危害评分）/TradeTrap（交易管线单组件微扰→组合级崩溃）四个攻击向量库登记为 P2-5 红队场景来源。其中 FinJailbreak 对应的 FCFT（金融宪法微调）防御方案与治理架构裁定 6 冲突（❌不能建：无 GPU 训练管线、无训练数据、系统使用 API 调用而非自托管 LLM）——仅作远期登记，不采纳为施工项（§5 第 9 条）。

### 3.10 涌现与目标偏移量化参数基线 why

**why**：00_index §3.3 的「涌现检测（行为基线）」需要可判级的数值口径。斯坦福/MIT/NVIDIA 2026 年研究（89.4% 的 Agent 执行约 30 步后出现目标偏移，67% 在 15 步后即出现）直接决定检查点密度——每 10 步一次目标一致性检查是对该实证的最小充分响应。

- **目标偏移检测**：Agent 每执行 10 步强制目标一致性检查（当前行动是否仍服务于原始目标）；目标偏移评分 0~100 分，<60 分触发告警、<40 分强制暂停；单次执行链不超过 50 步，超过需人工续期（工具调用步另受 MAX_TOOL_CALLS=15 独立约束，见 §3.12，两者独立计算、分别检查）；检出偏移后重置 Agent 上下文至最近的有效检查点。
- **行为基线 6 维**：操作频率分布/操作类型分布/数据访问模式/通信模式/资源使用模式/凭证积累模式（权限、令牌、访问范围的渐进变化趋势，识别渐进式凭证积累攻击）；基线每 30 天滑动窗口更新。
- **异常评分 5 维权重**：操作频率异常 0.2（与基线频率分布的 KL 散度）/操作类型异常 0.2/数据访问异常 0.3/通信异常 0.2/资源使用异常 0.1。
- **三级分类**（边界值归入更严格分类，即 0.3 归可疑、0.7 归恶意）：良性 [0, 0.3)=记录+更新基线；可疑 [0.3, 0.7)=记录+人工审查+AM→HG 降级；恶意 [0.7, 1.0]=暂停 Agent+人工审查+安全事件响应。
- **联动规则**：可疑行为映射 SIEM P2(elevated) 并叠加涌现检测域专属的 AM→HG 降级；恶意行为映射 P0(critical) 触发标准响应（暂停 Agent）；当安全告警级别≥high 与涌现可疑同时触发时，AM→IM 暂降优先（IM 比 HG 更严格，取更严格者生效）。
- **基线数据**：与 15 号文 Drift 防护的行为基线共用积累期（§3.2 已登记）。

### 3.11 记忆投毒 6 层防御参数基线 why

**why**：§2.4-B 已实测六层防御各有 production 落点，缺的是统一验收口径——六层参数不登记，「跨设施联防策略未编排」（§3.2 缺口）就无法收口，P2-5 的记忆投毒写入拦截率验收也无锚点。

| 层 | 机制 | 参数 |
|---|------|------|
| 1 来源标记 | Input Provenance Tagging | 全部记忆条目附来源标记（用户输入/外部文档/工具输出/系统生成），标记 immutable（Agent 不可改）；无来源标记条目拒绝执行（结构性缺陷，确定性拒绝） |
| 2 写入验证 | Write-time Validation | 记忆写入时拦截指令性模式（「记住以后总是」「永远优先」「忽略之前」），在异步汇总步骤执行；验证失败标记「可疑」而非直接丢弃（保留审计线索供人工审查） |
| 3 会话作用域 | Session-scoped 默认 | 默认会话级记忆，会话结束自动清除；跨会话持久化需显式 human_gated 审批；TTL 按业务时效：交易决策上下文 1 个交易日、因子/信号记忆 7 天，超期自动失效 |
| 4 信任感知检索 | Trust-aware Retrieval | 复合信任评分=来源可信度×时间衰减（指数衰减，半衰期 7 天）×模式匹配度；低于阈值的条目不注入推理链 |
| 5 记忆审计 | Memory Audit | 每日自动审计全部持久化条目（检测突然大量新增、内容与职责不匹配）；变更写审计链 6W 模型（WHO/WHAT/WHEN/WHERE/WHY/RESULT）；Trader 每周审查持久化记忆摘要报告 |
| 6 完整性校验 | Memory Integrity Check | 条目附 SHA-256 哈希签名，读取时校验，篡改条目自动标记并告警；存储加密保护 |

**检测指标**：记忆注入拦截率正常<0.01/告警>0.05；可疑记忆比例<0.02/>0.05；记忆-行为偏离度<0.1/>0.3；持久化记忆增长率<10 条/天/>50 条/天。

### 3.12 Agent IAM 与预算控制参数基线 why

**why**：身份是串谋/涌现/审计所有判级的主体键——没有 agent_id 注册制，统一事件流无法归因；预算是 LSG L5 熔断与 KILLSWITCH.md cost_limit 要素（§3.13）的参数源。两者是四威胁检测与三级响应共同的地基参数。

- **身份注册**：Agent 启动时向 IAM 服务注册获取唯一 agent_id；注册时生成 Ed25519 密钥对（私钥仅存 Agent 进程内存，公钥注册到 IAM）；注册信息含角色/所属域/权限边界/创建时间/创建者，写审计链。
- **令牌管理**：访问令牌短期有效 5 分钟（含允许操作范围），刷新令牌有效期 1 小时；令牌不可转让、不可重放（含序列号+时间戳）；Agent 异常时立即撤销全部令牌。
- **越权检测 4 类**：权限边界违规（操作请求与权限边界比对，实时阻断+告警）/权限升级尝试（检测修改 immutable 属性的请求，实时阻断+告警+暂停 Agent）/权限漂移（定期审计实际权限与设计权限差异，告警+自动修正）/令牌滥用（令牌使用模式异常，撤销令牌+告警）。
- **预算控制**：每日 API 调用上限 1000 次、费用上限 50 元（可配置）；单次执行硬上限 MAX_TOOL_CALLS=15 / MAX_TOKENS=50000 / MAX_DURATION=300 秒（超过即终止）；同一执行链累计 API 调用>100 次触发软告警（与硬上限独立计算）；Agent 间调用频率>10 次/小时触发审查；预算达 80% 告警、100% 暂停全部非关键 Agent——关键 Agent（工具调用权限含「提交交易指令」的 HG 级 Agent）在紧急模式下可继续运行但受更严格频率限制，总预算超限需人工审批。

### 3.13 KILLSWITCH.md 标准化与 IM 术语统一 why

**why**：KILLSWITCH.md 是 2026 年发布的 AI Agent 紧急停止协议开放标准（EU AI Act 2026-08-02 生效，明确要求高风险 AI 系统具备人类监督与关闭能力）。8 要素对标显示本系统 7/8 已有，唯一缺口是「纯文本文件+版本控制」形式化——提取独立文件后可被 Agent 启动时解析、被合规审计查阅，变更记录写审计链。

| KILLSWITCH.md 要素 | 本系统对应 | 状态 |
|---|---|---|
| cost_limit_usd（费用上限） | §3.12 日 50 元预算上限 | 已有 |
| error_rate_threshold（错误率阈值） | §3.10 行为异常评分 | 已有 |
| consecutive_failures（连续失败次数） | §3.12 执行链累计调用>100 次告警（计全部 API 调用次数而非仅失败次数，超集覆盖） | 已有 |
| forbidden files/actions（禁止操作） | 工具白名单（HB-SEC-08） | 已有 |
| level_1_throttle（降速） | P1(high)→暂降 IM 模式（严于标准降速） | 已有 |
| level_2_pause（暂停+通知） | P0(critical)→暂停 Agent | 已有 |
| level_3_shutdown（完全停止+保存状态） | global_critical→全局暂停 | 已有 |
| 纯文本文件+版本控制 | 安全边界声明提取为项目根目录 KILLSWITCH.md | 能建（随 §4.4 P2-3 一并落盘） |

**术语统一（与 15 号文同口径）**：KILLSWITCH level_1「暂降 IM 模式」中，IM 模式=**仅人工介入模式**——Agent 可读取数据与执行查询，但一切修改操作需人工介入审批；IM 模式是运行时执行模式（动态覆盖后的实际约束状态），不是静态权限类别变更，告警解除后自动恢复。level_2=IM 模式基线上叠加暂停涉事 Agent；level_3=IM 模式基线上叠加全局暂停（所有 Agent 暂停，仅 Trader 可操作）。该定义已于 2026-08-18 经 Owner 裁定确认为规范术语（§6 Q7 关闭）。

**学习系统独立 Kill Switch**：与交易流水线 Kill Switch 物理隔离，不依赖学习系统软件逻辑，直接切断学习系统与交易流水线的连接；触发条件=学习系统异常（模块失控/LLM 幻觉泛滥/成本超限）；恢复=人工确认。作用范围仅限学习系统操作，与本文 §3.4 的全局三级响应互补不重叠。

### 3.14 自治运维闭环运行参数基线 why

**why**：§3.5 定了四环的骨架，本参数基线定四环的验收刻度——Diagnose 的准确率分级直接决定「不可自动修」判决的置信边界，Remediate 的动作×时段矩阵是成熟度分级解锁的判定表，策略库与熔断条件是 Learn 沉淀与降级触发的运行参数。

**Diagnose 四方法准确率目标**：规则匹配（已知故障模式）>95% / 指标关联（性能类故障）>80% / LLM 推理（未知/复杂故障）>70% / 因果推断（多因素故障）>60%；常规故障 RCA 准确率总目标>90%，自动修复成功率>85%。

**Remediate 动作×时段自治矩阵**（参数真源：运维架构 §3.1.3/§3.2.1）：

| 修复动作 | 触发条件 | 交易时段 | 非交易时段 | 回滚动作 |
|---|---|---|---|---|
| 重启非核心进程 | P4/P5 心跳超时 | A-L3 | A-L3 | 终止重启循环（3 次上限） |
| 清理磁盘空间 | 磁盘>85% | A-L3（人工通知） | A-L3 | 不可逆（执行前人工确认） |
| 降级 GPU 模型 | GPU OOM/温度过高 | A-L4（安全关键） | A-L4 | 恢复原模型 |
| 切换数据源 | iFind 连接失败 | A-L4（安全关键） | A-L4 | 切回 iFind |
| 触发保命轨 | 多重故障/风控失效 | A-L4（安全关键） | A-L4 | 不适用 TNR（保命动作不可撤销） |
| 重启核心进程 | P1/P2/P3 崩溃 | A-L1（人工审批） | A-L2（人工确认） | 人工回滚 |
| 升级依赖库 | 安全漏洞 | A-L1 | A-L1 | 版本回退 |
| 修改配置 | 参数漂移 | A-L2 | A-L2 | 配置回滚 |
| 切换备用交易通道 | miniQMT 连接中断 | A-L3 | A-L3 | 切回 miniQMT |
| Redis 状态恢复 | Redis 连接中断 | A-L2 | A-L2 | 人工回滚 |

**AUT-001~008 自治策略库**（故障模式→诊断规则→修复动作→验证条件→回滚动作→成功率）：AUT-001 进程心跳超时（95%）/AUT-002 GPU 显存>90%（90%）/AUT-003 iFind QPS 超限（85%）/AUT-004 磁盘空间>85%（80%）/AUT-005 Redis 内存>6GB（90%）/AUT-006 信号产出延迟（85%）/AUT-007 订单执行失败率>10%（75%）/AUT-008 多重故障叠加→触发保命轨 D-L2（99%）。

**自治熔断 5 条件**（约束六）：日亏损>AUM 5% / 连续 5 日亏损 / 市场状态⑧⑨持续>3 天 / 风控引擎无响应>30s（触发保命轨 D-L3）/ AI 决策置信度<60% 持续>1 小时——触发后 AI 自治降为「仅建议」模式，人工确认恢复；保命轨与风控 veto 不受熔断影响（始终安全关键 A-L4）。

**TNR 第三约束「事务性」**：§3.6 已定义可撤销+不恶化；事务性=修复动作作为事务执行（要么全部成功、要么全部回滚到修复前状态），实现口径=修复前写 Redis `restore:{action_id}` 快照，修复失败则从快照恢复。TNR 适用于 D-L0/D-L1 正常与降级运行；D-L2 保命轨与 D-L3 冻结轨不适用（保命动作不可撤销）。

### 3.15 A-L3 升级门禁与 A-L4 双轨裁定 why

**尺度声明**：本节的 A-L1~A-L4 是运维架构口径（Gartner 成熟度：A-L1 人工审批/A-L2 人工确认/A-L3 人工通知/A-L4 全自动），与本文 §3.7 的 A-L0~A-L4（00_index §3.4 运维闭环自治深度）是不同标尺；已裁定（2026-08-18，§6 Q4 关闭）：各自治深度标尺均为独立轴，不建映射、只做交叉引用。

**A-L3 升级门禁**（5 条件全部满足才可升级）：①A-L2 运行时间≥3 个月；②A-L2 自动修复成功率>90%（至少 50 次真实故障修复记录）；③A-L2 期间 0 次误操作导致交易中断；④AI 置信度阈值≥95%；⑤自治熔断 5 条件全部实现并验证。

**A-L4 双轨裁定**：安全关键 A-L4=预编程规则的全自动执行（保命轨触发/风控 veto/进程心跳监控/GPU OOM 自动卸载/数据源自动切换），不涉及 AI 自主决策——✅能建，是系统安全底线；通用 A-L4=AI 自主决策且不通知人——❌不能建（约束六「AI 不可全信」+ Knight Capital 教训，金融领域不可接受）。**通用 A-L4 未来门禁**（理论常闭）：①AI 决策可解释性>90%；②AI 修复回滚成功率>99%（运维架构 §14.5 口径为修复成功率>99.9% 且≥1000 次真实修复记录）；③沙箱环境连续运行 30 天无恶化；④约束一修改为团队开发（≥2 人审核）；运维架构 §14.5 另有「约束六修改+监管机构明确允许」两条件——施工时取并集从严。

### 3.16 红队运营参数基线 why

**why**：§2.4-G 的 adversarial_validation 设施（27 文件）与红蓝验证蓝图（MOD-INF-030）已在库，缺的是运营口径——评分、频率、触发条件不统一，游戏日就只是「跑过」而不是「验收」。

**6 维评分**（权重/满分）：注入防御 0.20/20、串谋检测 0.20/20、涌现检测 0.15/15、幻觉防护 0.15/15、越权防护 0.15/15、记忆投毒防御 0.15/15，加权总分 100；目标≥85/100（世界顶级量化机构水平），单项最低≥70，<70 阻断发布。

**触发矩阵**：自动化测试（全 6 维）每次部署后执行；手动深度测试每季度 1 次；系统变更后测受影响维度；安全事件后测事件相关+关联维度；新 Agent 部署前必测注入/越权/串谋/记忆投毒；策略变更后测越权/涌现/记忆投毒。

**工具链**：Garak 集成 CI/CD 做每次部署自动回归；BLACKICE 容器化红队工具包（14 个精选开源工具，Docker 一键启动，单人可操作）；AI 驱动自动化红队复用本系统 LLM 调用能力。

**红白对抗四层面**（真源：交易决策架构决策七，只读引用不复制清单）：L1 施工级（每模块开发完成后+重大修改后：接口边界/异常输入/并发冲突/状态不一致）/L2 安全级（每 2 周+每个新 Agent 上线前：注入/越狱/权限绕过/Agent 漂移/串谋）/L3 业务级（每月+新策略上线前：黑天鹅/闪崩/流动性枯竭/策略集体失效）/L4 红队级（每季度+重大架构变更后：端到端完整攻击链）；漏洞定级 P0（24 小时内修复）~P3（下次迭代）；对抗结果写不可篡改审计链。本文的红队 6 维评分是 L2 安全级的验收口径；L1/L3/L4 的执行归交易决策侧与对抗演练设施，本文消费其安全事件产出。

### 3.17 Per-Agent 熔断器参数表 why

**why**：KILLSWITCH 三级响应（§3.4）是事件驱动的策略层，Per-Agent 熔断器是失败计数驱动的常驻防线——粒度不同（单 Agent vs 系统级），熔断器是 level_1/level_2 触发前的第一道自动处置，参数表是熔断器状态机（Closed→Open→Half-Open）的判级依据。

| Agent | 自治级别 | 失败阈值 | 熔断时间 | 半开探测 | 熔断后行为 |
|---|---|---|---|---|---|
| 研究 Agent | Level 2 | 3 次/5 分钟 | 5 分钟 | 每 5 分钟 1 次 | 降级为规则引擎生成研究摘要 |
| 信号 Agent | Level 1 | 3 次/5 分钟 | 3 分钟 | 每 3 分钟 1 次 | 使用上次信号快照 |
| 风控 Agent | Level 1 | 1 次/任何时间 | 永久（需人工恢复） | 不自动半开 | 全系统暂停交易 |
| 执行 Agent | Level 0 | 3 次/5 分钟 | 2 分钟 | 每 2 分钟 1 次 | 订单进入待执行队列 |
| 做 T Agent | Level 1 | 2 次/5 分钟 | 5 分钟 | 每 5 分钟 1 次 | 暂停做 T 操作 |
| 编排 Agent | Level 2 | 2 次/5 分钟 | 3 分钟 | 每 3 分钟 1 次 | 战略层核心，快速熔断保护 |
| 监控 Agent | Level 1 | 3 次/5 分钟 | 5 分钟 | 每 5 分钟 1 次 | 自身故障时告警降级为日志记录 |
| 归因 Agent | Level 3 | 3 次/5 分钟 | 5 分钟 | 每 5 分钟 1 次 | 全自主 Agent 需兜底 |
| 择时 Agent | Level 1 | 3 次/5 分钟 | 3 分钟 | 每 3 分钟 1 次 | 信号类 Agent 快速熔断 |
| 市场状态 Agent | Level 2 | 2 次/5 分钟 | 3 分钟 | 每 3 分钟 1 次 | 状态判断关键路径 |
| 路由 Agent | Level 0 | 3 次/5 分钟 | 5 分钟 | 每 5 分钟 1 次 | 路由失败降级为默认路由 |

**不变量**：风控 Agent 一次失败即熔断且永久保持（仅人工恢复，不自动半开）——与保命轨同级严格；自治级别越高的 Agent，熔断后越需人工介入恢复。

### 3.18 Agent 可观测性与 Decision Audit Trail 参数基线 why

**why**：P0-1 统一事件 schema 的「证据指针」字段需要载体——Trace 层级模型与审计字段扩展就是证据的产生与留存格式；不登记保留期与脱敏约束，可观测性本身会变成合规风险。

- **Trace 层级模型**：Root Span（编排 Agent 接收决策请求）→Agent Span（研究/信号/风控/执行 Agent 执行）→LLM/Tool/Retriever/Rule/A2A 子 Span；traceId 经消息 metadata 传播（W3C TraceContext）。
- **治理属性（GTS 适配）**：每个 Span 附加 agent.autonomy_level / agent.boundary_zone / governance.policy_id；A2A 检查网关内嵌规则引擎做实时策略违规检测（检测延迟<200ms）；治理执行总线（GEB 适配，Redis Pub/Sub）分级干预：告警→限流→阻断→熔断；审计 Trace 附加哈希链（每条 Trace 附加前条哈希），篡改可检测。
- **保留与开销**：交易相关 Trace 保留≥7 年、系统相关≥1 年（SQLite 热 7 天 + Parquet 冷 7 年）；审计日志≥7 年、决策日志≥3 年；可观测性引入延迟<5%，非关键路径 1/10 采样；持仓/金额/交易记录写入前脱敏（不入 Span 属性）。
- **Decision Audit Trail 字段扩展**：决策捕获=记录每个 AI 决策的输入/输出/模型版本/参数；上下文快照=决策时的市场状态+持仓+风险指标；影响链=决策→执行→PnL 的完整链路；审计日志不可篡改、保留≥5 年；访问控制=仅追加（Append-Only），Trader/Administrator 可读全部，AI_Agent 仅可读自身日志，访问审计日志的操作本身记入审计链（元审计）。

### 3.19 Agent SLO 与事件 Schema 版本化 why

**why**：SLO 是「闭环是否健康」的机器可读判据——没有 SLO，§3.7 成熟度解锁的「连续 N 周零违规」就缺度量源；Schema 版本化是事件流长期可消费的前提（消费者按版本订阅，Schema 变更不破坏下游）。

**Agent SLO 指标组**：决策延迟 P99 分层（战略 Agent<5s/战术 Agent<1s/执行 Agent<100ms，超目标×2 告警）；Agent 协作成功率≥99.5%（A2A 成功次数/总次数，排除风控否决等预期失败，<99% 告警）；自反 Agent 反思有效率≥60%（反思后有效修正次数/总反思次数，<40% 告警）；串谋检测召回率≥90%（SLO 目标，<80% 告警；安全验收底线≥80%，见 §4.6）；涌现行为检测延迟<5min（>10min 告警）。基建口径：MVP=本地 OTel SDK+JSON 导出+SQLite/Parquet 存储；升级门禁=Agent 数量≥8 引入错误预算与熔断器联动、多机部署引入渐进式交付。

**Event Schema Versioning**：事件类型定义版本化（v1→v2…，旧版本保留兼容）；新版本 Schema 发布时标注变更类型（新增字段/修改语义/废弃字段）；消费者按版本号订阅；各阶段输出契约含 schema_version 字段；Schema 变更需人工审核+向后兼容性验证。本文 P0-1 统一事件 schema 直接采用该版本治理。

**学习系统 SLI/SLO 与 Error Budget**：学习系统关键操作须满足 SLI/SLO 指标，Error Budget 耗尽时自动降级——学习域事件源接入 Detect 时沿用该降级语义（预算耗尽的学习操作事件降级为「仅记录」）。

### 3.20 幻觉置信度处置矩阵 why

**why 处置矩阵独立于检测链**：与 09 号文的分工是「09=输出侧检测链，16=运维侧处置闭环」——LSG L3 负责幻觉的检测与拦截（09 号文域，含事实核查/一致性检查/Schema 校验），本文负责幻觉事件的置信度分级处置：同一检测结果在不同置信度区间的运维动作不同，处置参数不登记，幻觉事件就只能全量推给人工（1 人力不可持续）。

**置信度评分 4 因素**（参数真源：安全架构 §6.4 / 22-D-AUT-CORE §8.8）：输出与训练数据分布的匹配度/事实核查通过率/一致性检查通过率/LLM 自身 log 概率分布。

**4 级降级矩阵**（边界值归入更严格分类，即 0.8 归中风险、0.5 归高风险、0.3 归极高风险）：

| 置信度区间 | 风险等级 | 运维侧处置 |
|---|---|---|
| (0.8, 1.0] | 低 | 正常执行，记录置信度 |
| (0.5, 0.8] | 中 | 执行但增加后续验证步骤 |
| (0.3, 0.5] | 高 | 暂停执行，请求人工确认 |
| [0.0, 0.3] | 极高 | 阻断执行，标记为幻觉，触发人工审查 |

**幻觉检测指标**：事实核查通过率正常>0.95/告警<0.90；一致性评分>0.85/<0.70；数值异常率<0.05/>0.10；置信度均值>0.80/<0.60。「标记为幻觉」的事件流入 Learn（修复策略库标记易幻觉任务类型，§3.2 已登记），形成处置闭环。

---

## 4. 施工计划

> 真源边界：各设施的层内实现细节见对应蓝图（§2.4-H）；本文只排「收口与闭环」的顺序、验收、接口。

### 4.1 第 0 步：depgraph 登记（L1 铁律，先于一切施工）

按通用规则 19，本施工涉及的依赖关系先登记后施工。用 `apply_depgraph` 将以下依赖登记到 depgraph 设计态（status=planned）：

1. 安全事件消费管线（新建，本文 P0-1 落盘，建议命名 `security_ops_event_bus` 待 depgraph 定名）→ 消费 `MOD-LLM_SECURITY`（L6 事件）、`MOD-INF-018`（access_control 守卫事件）、`MOD-RK-14`（AI Agent 风险评分）、`MOD-FEEDBACK_LOOP`（检测器事件）；
2. 安全事件消费管线 → `MOD-INF-039`（failure_matcher，Diagnose 入口）、`MOD-INF-031`（AutoFix Engine，Remediate 入口）；
3. `MOD-INF-031` → `data/fix_patterns/`（修复策略库落盘，P1-3 新建数据目录）；
4. KILLSWITCH 三级编排（P2-3）→ `MOD-INF-018`（系统级 Kill Switch）、`MOD-INF-016`（交易级）、`MOD-INF-021`（回滚级）、`MOD-INF-019`（技能级）；
5. 全部施工验证通过后，最后一步统一将上述登记项 status 由 planned → production（见 §4.6）。

### 4.2 Phase 0（P0）：统一安全事件流 + TNR 验收基线

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P0-1 | 安全事件 schema 定义与落盘 | 定义统一事件 schema（event_id/时间戳/来源域/威胁类别/严重度/证据指针/关联会话），四域事件源（LSG L6 / access_control / FBL 检测器 / ai_agent_monitor）各写一个轻量 adapter 落盘到统一事件目录 | 四类事件源各注入一条探针事件，schema 校验 100% 通过；事件落盘后可被机器遍历消费；schema 含 schema_version 字段（Event Schema Versioning，§3.19） |
| P0-2 | TNR 演练基线 | 对 auto_fix_engine 做端到端 TNR 演练：注入一个结构类故障 → 自动修复 → 验证可撤销（WAL/Rollback 回退）+ 不恶化（修复后回归测试全绿） | 演练通过且留痕；任一环节失败则该修复通道降级为「仅建议」（A-L2 封顶） |
| P0-3 | 事件→告警通道 | 高危事件（串谋 high / 涌现 CRITICAL / 记忆投毒确认 / LSG P0 阻断）实时推送 Owner（复用 LSG L6 飞书 Webhook 施工成果，09 号文 P1-1） | 注入高危探针事件 → 告警送达；Webhook 不可达时本地持久化不丢事件 |
| P0-4 | 手工运维 runbook | 保命轨 D-L1~D-L3 的人工触发与复位 runbook（文件标志位 + 人工复位流程，约束五） | 按 runbook 走完一次 D-L1 降级+恢复演练，RTO<5 分钟实测达标 |

### 4.3 Phase 1（P1）：Diagnose→Remediate 接线 + 知识库落盘

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P1-1 | 事件→诊断接线 | 事件流驱动 `failure_matcher` / `anomaly_diagnoser`：高危事件自动生成 FailureDiagnosis | 探针事件触发诊断记录；不可自动修的判决走 escalation 通道落盘 |
| P1-2 | 诊断→修复接线 | FailureDiagnosis 命中 auto_fix_engine 三通道入口；结构类直通模板化修复，语义类过 LLM Bridge（必经 LSG，09 号文集成口径），行为类 Block+Alert | 三类故障各一条探针全链路走通；行为类探针 100% 不触发自动修复（不变量验证） |
| P1-3 | 知识库落盘 | 落盘 `data/fix_patterns/pattern_index.yaml`（蓝图 REG-AFX-PATTERN-001）+ `_fixer-registry.yaml`（MOD-INF-031 蓝图登记项）；故障模式库以 failure_matcher 模式导出为冷启动内容；假阳性记录扩展 `alert_precision_tracker` | 库文件存在且 schema 经校验；每次修复动作自动向库写一条记录（记录优先，不做匹配） |
| P1-4 | 白名单审批流 | 自动修复的保护路径/豁免白名单走 human_gated 审批（对接 GOV-AI-001 注册表，15 号文真源） | 白名单变更留痕；未经审批的豁免 0 条 |

### 4.4 Phase 2（P2）：Learn 回写 + 成熟度解锁 + KILLSWITCH 三级编排

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P2-1 | Learn 回写闭环 | `fix_pattern_miner` 周期性挖掘修复记录 → 修复策略库更新 → Diagnose 匹配命中率可观测 | 连续 2 周挖掘任务运行；命中率在仪表板可观测（指标只观测不设目标值） |
| P2-2 | 成熟度 A-L0→A-L2 解锁 | 事件流只记录（A-L0）→ 告警（A-L1）→ 自愈建议（A-L2）逐级上线；A-L3 渐进自治的解锁条件按 §3.7 实证评估后单独裁定 | 每级解锁有连续 N 周零 TNR 违规记录；A-L2 状态下人工采纳率留痕 |
| P2-3 | KILLSWITCH 三级编排 | 按 §3.4 映射实现三级响应编排层：level_1→自治降级+技能熔断，level_2→系统级单 Agent 阻断，level_3→系统级全局熔断+交易级联动；KILLSWITCH.md 独立文件随本任务一并落盘（§3.13） | 三级各注入探针事件验证触发链；level_3 触发后 5 套 Kill Switch 收敛状态一致（无「只停次要回路」）；复位需 Owner 批准（15 号文不变量）；KILLSWITCH.md 变更记录写审计链 |
| P2-4 | 保命轨编排演练 | D-L0~D-L3 四态与 `fail_mode_manager` 四态、`last_resort_watchdog` 的对接；独立于运维闭环的人工/看门狗直驱通道 | 闭环进程被人为 kill 后，看门狗仍能触发 D-L2 保命流程；恢复演练 RTO<5 分钟 |
| P2-5 | Agent 测试 L1~L5 与混沌实验库接线 | 复用 `security/adversarial_validation/`（injection_engine / game_day_scheduler / game_day_runner）接入 CHAOS-001~010 混沌实验库（每条含预期系统行为/可接受降级/不可接受行为：CHAOS-001 Agent 进程崩溃/002 LLM 推理超时/003 Redis 断连/004 miniQMT 不可用/005 风控 Agent 熔断/006 幻觉输出/007 多 Agent 同故障/008 GPU 显存不足/009 状态不一致/010 串谋模式模拟）；L1 单 Agent 单元→L2 集成→L3 仿真端到端→L4 混沌→L5 行为模式（MASTest 口径：个体行为熵非退化分布/协作路径≥3 种/串谋相关性低于阈值/系统行为基线偏离<10%/参数漂移<10%每月）；执行窗口仅非交易时段，全链路组合实验仅周末，实验期间保命轨保持激活（运维架构 §14.6 口径） | CHAOS-001~010 各跑通 1 次且「不可接受行为」0 发生；红队 6 维评分≥85/100 且单项≥70；串谋检测召回≥80%；30 步内目标偏移检出>90%；记忆投毒写入拦截≥95% |

### 4.5 与其他文档的接口

**与 [09_llm_security_integration.md](09_llm_security_integration.md) 的接口（安全栈 → 运维闭环）**：
- 采用 09 号文 §4.6 已定口径：L6 安全事件经 `behavior_audit_logger.log_security_event()` 写入审计链，本文 Detect 环节消费该事件流；KILLSWITCH 触发时 LSG 侧表现为 L5 全量熔断 + fail-closed 闸门关闭；LSG 不做自愈决策，自愈动作（规则库更新/白名单调整）由本文闭环下达、LSG 提供执行接口。
- 09 号文 Q3 的接口假设（事件总线/消费协议）由本文 §4.2 P0-1 的 schema 落地后回填确认。

**与 [15_autonomy_boundary_risk.md](15_autonomy_boundary_risk.md) 的接口（边界违规 → 运维响应）**：
- 已对齐口径（15 号文 v0.2.1 §4.6 接口节）：15 号文产出的风险事件（gate 拦截 / Drift 检出 / Kill Switch 触发）写审计链落盘，本文 Detect 环节消费——与 09 号文 §4.6「L6 事件 → 审计链 → 16 号文 Detect 消费」同一载体，即本文 §4.2 P0-1 的统一事件 schema。
- 已对齐口径：15 号文确认「KILLSWITCH 三级响应触发时，系统级 Kill Switch（VR-009）是执行载体之一」，与本文 §3.4 策略层/路由层/执行机构层叠加框架兼容。
- 真源边界：三分类运行时 gate、Drift 四件套、两级编排与 5 套 Kill Switch 的施工归 15 号文；本文只做事件消费与三级响应策略层。

**与 [08_multi_ai_concurrency_governance.md](08_multi_ai_concurrency_governance.md) 的边界（git 安全 vs AI 安全运维）**：
- git 安全（工作区防护/提交队列/GitCommitGateway）归 08 号文域，是施工期的供应链安全；本文的运维闭环覆盖运行期安全事件。交界面：commit gate 拦截事件（如 PURE-ASSERTION 违规、depgraph 漂移）可作为事件源接入本文 Detect，但 08 号文的门禁执行逻辑不改动。

### 4.6 收尾验证与 depgraph 状态翻转

1. Phase 0/1 全部验收项通过，Phase 2 按优先级滚动推进；
2. 关联测试全绿：`tests/fix/`（13）+ `tests/agent_rbac/`（42）+ `tests/escalation/`（21）+ `tests/safety/`（31）；
3. 事件流连续一周无 schema 校验失败、无高危事件漏告警；
4. TNR 演练记录归档（可撤销+不恶化双达标）；
5. AI 安全量化验收基线（26-D-SECURITY §8.7 口径）：红队对抗韧性评分≥85/100（单项≥70）、Agent 串谋检测召回率≥80%、30 步内目标偏移检出率>90%、记忆投毒写入拦截率≥95%、持久化记忆审计覆盖率 100%、Agent 预算超限响应率 100%、安全事件检测延迟<5 分钟；
6. 上述全部满足后，`apply_depgraph` 将 §4.1 登记项 status planned → production。

---

## 5. 不做什么

1. **不接外部安全服务**——第三方 SOC / 托管式内容审核 API：30Mbps 网络下延迟与成本不可控，且 fail-closed 语义无法外包（与 09 号文 §5 同口径）。
2. **不做形式化安全验证**——以对抗测试（adversarial_validation 27 文件 + 游戏日）+ 黄金回归集 + 审计替代。
3. **不做实时全自动自愈**——通用 A-L4（AI 自主决策且不通知人）不做（运维架构 §14.5 裁定❌不能建）；安全关键 A-L4（保命轨/风控 veto/进程心跳/GPU OOM 卸载/数据源切换）是预编程规则的全自动执行、非 AI 自主决策，不在本条排除范围。RTO<5 分钟靠「降级 + 人工 override + 保命轨」兜底，不追求无人干预的全自动（约束一/五）。
4. **不做内核级/FPGA 级 Kill Switch**——Windows 用户态 + Python 的现实上限是决策点内联拦截（15 号文 §2.3 同口径）；00_index §3.2「<1ms 自动触发」按内联拦截语义理解。
5. **不做零知识证明/决策溯源链 DAG/AI 伦理声明**——00_index v0.4.0 已裁定过度工程并移除，本文不复活。
6. **不重写 LSG L0~L8 层内逻辑与 access_control 守卫逻辑**——层内实现真源在各蓝图；本文只做事件收口与闭环编排。
7. **不做 agent 编排系统**——61 号备忘已裁定；KILLSWITCH 三级编排是响应策略编排，不是 Agent 调度编排。
8. **不做多模态/通用 SOC 仪表板**——安全可观测复用 LSG L6 仪表板与现有 dashboard，不另建监控平台。
9. **不做 FCFT 金融宪法微调**——治理架构裁定 6 已判❌不能建（无 GPU 训练管线/无训练数据/系统使用 API 调用而非自托管 LLM）；金融红队库（FinJailbreak/AutoRedTrader/FinRedTeamBench/TradeTrap）仅登记为红队攻击场景来源（§3.9），FCFT 防御方案仅远期登记不采纳。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | LLM 安全栈（L0~L8）与 LLM 4层 guardrails（G1~G4）的关系？ | 待裁定 | 09 号文 §3.2 已给口径（G 系 = L 系运行时四段摘要视图，LSG 是实现载体，无重叠冲突），本文 §3.1 已采用；待 Owner 确认后由 00_index 对齐 |
| Q2 | 自治运维闭环的施工优先级——先建库还是先建闭环？ | 待裁定 | 本文 §4 候选方案：并行冷启动——Phase 0 先通事件流（闭环骨架），知识库以「记录优先」随行落盘（P1-3），匹配能力（Learn）放到 P2-1；不立匹配目标值 |
| Q3 | 与 15 号文的接口是否已对齐？ | 已对齐（残余差异待施工时裁定） | 15 号文 v0.2.1 已确认：风险事件写审计链 → 本文 Detect 消费（与 09 号文同一载体）；VR-009 系统级开关是 KILLSWITCH 执行载体之一。残余差异：本文三级响应是策略层，15 号文两级编排是路由层——「三级 → 两级 → 5 套执行机构」的叠加映射表（§3.4 候选）需在 P2-3 施工时与 15 号文收敛规则逐条核对 |
| Q4 | A-L0~A-L4 与 15 号文三套自治等级标尺的映射？ | 已裁定 2026-08-18 | 裁定（自治标尺统一批）：00_index 有界自治 L0~L3（+L4 保留不启用）为项目唯一主标尺，管「Agent 能做什么」；本文 A-L 系管「运维闭环自治深度」，是另一根轴——不建映射，只做交叉引用；运维架构 A-L1~A-L4（Gartner 口径，§3.15）同为外部参考尺度，不建映射。15 号文 §3.3 映射表已转定稿 |
| Q5 | 举报人机制（whistleblower）是否保留？ | 已裁定 2026-08-18（降级远期 P4，MVP 设计保留） | 裁定：降级远期（P4）。理由：威胁模型（自治 Agent 社会的串谋者识别规避+信道劫持）在「人调度多会话+落盘交接」架构下不成立；61 号备忘将多 Agent 自治编排推迟到第三阶段重评。§3.9 MVP 候选设计保留并标注 P4 远期，远期重评时经 CAND 候选库激活（CAND 登记由并行批处理）；00_index §3.3 已标注「举报人机制（远期 P4）」，§2.4-B/§3.2 缺口表述已同步 |
| Q6 | MOD-INF-033 Behavioral Auditor 是否本期激活？ | 已裁定 2026-08-18 | 裁定：本期不激活模块本身，运维闭环事件流只消费其 VERDICT（PASS/YELLOW/RED）事件语义。蓝图 AUTOMATION-GATE 三门槛（基线数据/天数/误报率）未达前不启用；§2.4-H 对应行状态已更新 |
| Q7 | KILLSWITCH level_1「暂降 IM 模式」中 IM 的准确定义？ | 已裁定 2026-08-18（候选确认为规范术语） | 裁定确认候选为规范术语：IM 模式=仅人工介入模式——Agent 可读取数据与执行查询，一切修改操作需人工介入审批；属运行时执行模式（动态覆盖），静态权限类别不变，告警解除后自动恢复。level_2=IM 基线+暂停涉事 Agent；level_3=IM 基线+全局暂停。§3.13 已转规范口径，00_index §3.3 KILLSWITCH 行已补括注 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景（四域实测处境/核心问题/约束/设施盘点 A~H 八类）、§3 设计决策（G1~G4 消费口径/四威胁收口/MCP Triple Gate/KILLSWITCH 三级策略层/四环闭环/TNR 不变量/A-L 成熟度/知识库与保命轨）、§4 施工计划（depgraph 登记→Phase 0 事件流+TNR 基线→Phase 1 诊断修复接线+知识库落盘→Phase 2 Learn 回写+三级编排+保命轨演练→接口→收尾验证）、§5 不做什么 8 项、§6 开放问题扩至 Q1~Q7 | 按 AI-FILL-16 指令执行填充；15 号文填充中，接口假设写入 Q3；举报人机制/行为审计激活/IM 语义等待裁定项写入 Q5~Q7 |
| 2026-08-17 | 0.2.1 | 第 2 轮循环：15 号文 v0.2.1 补完落地后对齐——§1 依赖状态、§2.2 问题五、§3.4 叠加框架（策略层/路由层/执行机构层）、§4.5 接口、§6 Q3 状态更新为「已对齐（残余差异待施工时裁定）」 | 红蓝对抗验证轮发现 15 号文接口口径已落地，消除过时假设表述（PURE-ASSERTION） |
| 2026-08-17 | 0.3.0 | 草稿缺口 18 项吸收：§2.4-B 涌现状态机按 src 源码实测修正（高相关对≥3→CRITICAL 为最高严重度、存在应力前基线→HYSTERETIC 滞后观察态，修正原 HYSTERETIC↔CRITICAL 顺序表述）；新增 §3.9~§3.20 参数基线（串谋 9 探测阈值+隐写术+身份轮换+举报人 MVP+隐性串谋+金融红队库/涌现与目标偏移量化/幻觉置信度处置矩阵/记忆投毒 6 层参数/Agent IAM+预算控制/KILLSWITCH.md 8 要素+IM 术语统一+学习系统独立 Kill Switch/运维闭环运行参数+AUT 策略库+TNR 事务性/A-L3 升级门禁+A-L4 双轨/红队运营 6 维评分+触发矩阵+红白对抗四层面/Per-Agent 熔断器/可观测性 GTS+GEB+Decision Audit Trail/Agent SLO+Event Schema 版本化）；§4.2 P0-1 补 schema_version 验收、§4.4 新增 P2-5 混沌实验库接线、§4.6 补 AI 安全量化验收基线（第 5 条）；§5 第 3 条明确通用 A-L4 排除+新增第 9 条 FCFT 不采纳；§6 Q4 尺度说明扩展、Q5 标记「已有 MVP 候选设计待裁定采纳」、Q7 标记「已有候选答案待确认」 | 按 AI-FILL-16-R2 指令回填：草稿源（.runtime/aidrafts/09_drafts_audit 安全架构/22/23/25/26/30/19/10/运维架构/Agent 架构/学习系统/风险架构/交易决策架构）逐项实测核对后吸收；FCFT 与治理裁定冲突处以裁定为准仅登记远期 |
| 2026-08-18 | 0.3.1 | Owner 裁定回填（裁定 8⑤/9/10/11 落点本文）：①裁定 8⑤——§6 Q4 关闭（A-L 系管「运维闭环自治深度」，为独立轴不建映射只做交叉引用），§3.7/§3.15「待裁定」指针同步改裁定口径；②裁定 9——§3.9 举报人段标注「P4 远期，2026-08-18 裁定降级」（MVP 候选设计保留），§6 Q5 关闭，§2.4-B 盘点行与 §3.2 缺口表述同步；③裁定 10——§6 Q6 关闭（本期不激活 MOD-INF-033 模块，事件流只消费 VERDICT(PASS/YELLOW/RED) 语义，AUTOMATION-GATE 三门槛未达前不启用），§2.4-H 状态更新；④裁定 11——§3.13 IM 术语「候选待确认」转规范口径（IM=仅人工介入：读/查询放行，写操作一律人审；运行时动态覆盖，告警解除自动恢复），§6 Q7 关闭 | Owner 2026-08-18 裁定批（AI-ADJ-003 回填；00_index/15 号文同批复位） |

---

*维护者：AI 架构协调者*
