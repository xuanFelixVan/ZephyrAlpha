---
ttl: permanent
doc_type: architecture_view
title: LLM 安全栈集成施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.0"
date: 2026-08-17
topic: llm_security_integration
scope: 09_ai_architecture
---

# LLM 安全栈集成施工图

> 本文定位：LLM 安全栈（L0~L8 纵深防御）的集成施工——所有 LLM 调用必经安全栈。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，蓝图见 `docs/03_modules/_cross_layer/large_language_model_security/blueprint.md`。
> **真源边界**：L0~L8 各层的层内设计（接口契约/检测算法/代码落位）真源 = 上述蓝图（MOD-LLM_SECURITY），本文不复制；本文只负责「集成」的 why/how——即 LSG 如何嵌入 AI 层 LLM 调用链路、剩余缺口的施工顺序、与 10/16 号文的接口。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | LLM 安全栈集成 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 治理层·AI 安全 |
| 依赖 | `_cross_layer/large_language_model_security` 蓝图（LSG L0~L8 纵深栈） |
| 优先级 | P1——LLM 安全是 AI 层的信任锚点 |
| 状态 | draft（骨架填充完成） |

---

## 2. 背景

### 2.1 项目处境

LSG（LLM Security Gateway，MOD-LLM_SECURITY）**层内实现已基本完成**——蓝图 §14 施工进度总览显示 L0~L8（含 L2a）10 层全部实现，整体完整度约 80%；磁盘实测 `tests/llm_security/` 已有 60 个测试文件（蓝图 §1.2 登记 24 个，索引滞后于代码增长）。当前的真实缺口不在"层内功能"，而在**集成接线**：LSG 已存在，但 AI 层的三层运行时（L1 Trae / L2 Local Ollama / L3 API，见 [10_llm_infrastructure.md](10_llm_infrastructure.md)）尚未统一接线到 LSG 网关，"所有 LLM 调用必经安全栈"这一架构铁律在运行时层面尚未闭环验证。

L0~L8 各层当前实现状态（来源：蓝图 §14 施工进度总览 + `src/zephyr/security/llm_defense/llm_security/` 磁盘实测，2026-08-17）：

| 层 | 名称 | 蓝图声明状态 | 完整度 | 磁盘实测（代码文件存在性） | 主要剩余缺口（蓝图 §14/各层 §x.5） |
|:---:|------|------|:---:|:---:|------|
| L0 | 供应链安全 | ✅ 已实现（457行） | 85% | ✅ `layers/l0_supply_chain.py` | 多源依赖交叉验证增强；MCP 深度安全加固（蓝图 §57）部分待施工 |
| L1 | 输入防护 | ✅ 已实现（437行，三层检测） | 85% | ✅ `layers/l1_input.py` + `input_sanitizer.py` + `patterns/injection_patterns.py` | 间接注入误报调优（风险 R1）；ToolResultTransform（蓝图 §38）/编码逃逸（§59）部分待施工 |
| L2 | Prompt 保护 | ✅ 已实现（373行） | 80% | ✅ `layers/l2_prompt_protection.py` | 防泄露检测与 System Prompt 模板的持续同步 |
| L2a | 进程沙箱 | ✅ 已实现（273行） | 90% | ✅ `layers/l2a_process_sandbox.py` + `process_sandbox.py` | Docker/WASI 更强隔离（与 L3B 同属沙箱强化项） |
| L3 | 输出安全 | ✅ 已实现（336行） | 80% | ✅ `layers/l3_output.py` + `patterns/secrets.py` | L3B Docker/WASI 沙箱集成；幻觉检测深度化 |
| L4 | Agent 安全 | ✅ 已实现（498行） | 80% | ✅ `layers/l4_agent.py` + `alignment_scorer.py` | HITL 审批体验（风险 R3）；长时域攻击防御（蓝图 §56）部分待施工 |
| L5 | 资源保护 | ✅ 已实现（432行） | 80% | ✅ `layers/l5_resource_protection.py` | 延迟预算管理 `LSGPerformanceGuard`（蓝图 §40，0%）；成本估算校准（风险 R4） |
| L6 | 可观测性 | ✅ 已实现（386行） | 75% | ✅ `layers/l6_observability.py` + `behavior_audit_logger.py` + `dashboard/app.py` | 飞书告警 Webhook 对接；日志膨胀治理（风险 R5） |
| L7 | 持续验证 | ✅ 已实现（401行） | 75% | ✅ `self_protection/`（red_team_scanner/code_integrity/isolation/l7_validation/adversarial_mutator） | Threat Intel 自动拉取；CI 安全门禁 `.github/workflows/lsg_security_gate.yml` **磁盘实测不存在**（蓝图 §35.3 已设计未落盘） |
| L8 | 多 Agent 安全 | ✅ 已实现（498行） | 80% | ✅ `layers/l8_multi_agent.py` | 级联注入防御（蓝图 §45）扩展；本项目多 Agent 规模小，优先级低 |

关键判断：**LSG 是"已建成的安全网关"，本文档的施工重心是（a）运行时统一接线、（b）剩余 20% 缺口收尾、（c）v2.0.0 信号总线（蓝图 §0-升级 D6-D16，`signal_bus/` 未实现）的启动条件**。

### 2.2 核心问题

1. **所有 LLM 调用是否必经安全栈？** 架构要求 fail-closed 全量拦截（蓝图 §12），但三层运行时的 LLM 客户端当前未强制统一走 `gateway.py`——存在"新写的 AI 代码直接调用 LLM 客户端、绕过 LSG"的结构性风险。集成施工的第一要务是**消除绕过路径**（统一入口 + 静态检查 + 运行时拦截三重保障）。
2. **哪些调用路径可能绕过安全栈？** 按调用来源排查：① 三层运行时的推理调用（10 号文域）；② MCP 工具调用触发的 LLM 请求（蓝图 §16 集成目标 MOD-INF-013）；③ RAG/向量检索结果注入（间接注入面，蓝图 §16 MOD-INF-011 集成点）；④ 治理脚本内嵌的 LLM 调用（v2.0.0 信号总线消费侧）；⑤ 测试/调试通道（本地模型直连）。
3. **各层防御的完备性如何收口？** 蓝图侧剩余缺口（L3B 沙箱、飞书 Webhook、Threat Intel 拉取、性能预算管理）与本文档侧集成接线，需要统一的优先级排序，避免"层内收尾"和"集成接线"两条线互相等待。
4. **层间协同如何验证？** L0~L8 单层测试已绿，但跨层链路（如 L1 拦截→L6 记录→L7 回归→L4 阻断）的端到端验证需要集成测试基线。

### 2.3 约束条件

1. **延迟约束**：LSG 主链路同步检查总预算 < 20ms，单次请求 P95 < 50ms / P99 < 100ms（蓝图 §40.1/§40.3）。异步检查（L1C 越狱 LLM 辅助检测、L3D 幻觉检测、L3B 沙箱）不计入主链路。**交易链路不在 LLM 实时调用路径上**（T+1、Tick=3 秒，LLM 用于研究/代码生成/治理，不在下单热路径），但 guardrails 延迟仍不能阻塞交互式施工体验（1 人在 TRAE 上多 AI 并发施工）。
2. **硬件约束**：单机 i7-12700KF + 64GB RAM + RTX 3090 24GB（显存 < 90% 硬上限），LSG 安全信号处理可用 4 核、GPU 不参与（蓝图 §1.4）。LLM 辅助检测（L1C/L3D）必须走本地小模型或异步排队，不得挤占推理 GPU。
3. **人力约束**：1 人 + AI 维护——安全自动化优先，人工仅做决策确认（蓝图 §26）；规则库维护必须 AI 辅助（风险 R7：1 人维护 200+ 条检测规则不可持续）。
4. **运维约束**：单机无热备，RTO < 5 分钟；fail-closed 意味着 LSG 自身故障会拒绝所有 LLM 流量（风险 R8），必须有分层健康检查 + Owner 手动 override 通道。
5. **网络约束**：30Mbps——禁止依赖外部安全服务（第三方内容审核 API 延迟和成本不可控，见 §5）。

### 2.4 已施工设施盘点

> 实测时间：2026-08-17。盘点范围：LSG 代码、测试、配置、蓝图、治理集成。状态以蓝图 §14 + 磁盘实测交叉验证。

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 蓝图 | `docs/03_modules/_cross_layer/large_language_model_security/blueprint.md` | MOD-LLM_SECURITY 九层纵深防御蓝图（实测 6093 行，§0-§61，含 OWASP/ATLAS/MCP 覆盖矩阵、接口契约、容量升级计划） | production（v1.0.0 基线已实现；v1.1.0 D1-D5 规划中；v2.0.0 D6-D16 待施工） |
| 网关入口 | `src/zephyr/security/llm_defense/llm_security/gateway.py` | LSGSecurityGateway 统一入口（fail-closed 闸门） | production |
| 运行时拦截 | `src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py` | LLM 请求/响应拦截器 | production |
| 协议契约 | `src/zephyr/security/llm_defense/llm_security/protocol.py` | 安全上下文/判决数据模型（Pydantic V2） | production |
| 输入侧 | `src/zephyr/security/llm_defense/llm_security/input_sanitizer.py`、`layers/l1_input.py`、`layers/l2_prompt_protection.py`、`patterns/injection_patterns.py` | L1 三层注入检测 + L2 Prompt 保护 + 注入特征库 | production |
| 输出侧 | `src/zephyr/security/llm_defense/llm_security/layers/l3_output.py`、`patterns/secrets.py`、`sensitivity_classifier.py` | L3 四层输出验证 + PII/Secret 模式库 + 敏感度分类 | production |
| Agent/资源侧 | `layers/l4_agent.py`、`layers/l5_resource_protection.py`、`layers/l8_multi_agent.py`、`alignment_scorer.py` | L4 权限/HITL/金融合规 + L5 预算熔断 + L8 多Agent + 对齐评分 | production |
| 供应链/沙箱 | `layers/l0_supply_chain.py`、`layers/l2a_process_sandbox.py`、`process_sandbox.py` | L0 模型/依赖验证 + L2a 进程级沙箱 | production |
| 可观测 | `layers/l6_observability.py`、`behavior_audit_logger.py`、`poisoning_monitor.py`、`dashboard/app.py` | L6 安全日志/告警 + 行为审计 + 投毒监控 + Streamlit 仪表板 | production |
| 持续验证 | `self_protection/`（red_team_scanner.py、code_integrity.py、isolation.py、l7_validation.py、adversarial_mutator.py） | L7 Red Team 扫描（271行/200+载荷/16 用例）+ 代码完整性 + 隔离 | production |
| 载荷库 | `payloads/`（injection_payloads.yaml、red_team_payloads.yaml、leak_probe_phrases.yaml、tool_call_payloads.yaml）、`red_team_corpus.yaml` | 攻击载荷与泄露探针语料 | production |
| 兜底安全网 | `solo_dev_safety_net.py`、`lsg_pattern_tracker.py`、`adversarial_robustness.py` | 1 人开发兜底 + LSG 模式追踪 + 对抗鲁棒性 | production |
| 安全专项测试 | `tests/llm_security/`（实测 60 个 .py 测试文件，其中 LSG 层内专项约 24 个，其余为集成/关联测试；需按命名空间细化归属） | L0~L8 逐层测试 + fail-closed/E2E/隔离/跨模块集成测试 | production |
| 根级测试 | `tests/` 根级（蓝图 §61.2 登记 test_input_sanitizer.py 等 4 个早期单元测试） | 早期单元测试 | **待核实（磁盘实测未找到，疑似已迁移进 `tests/llm_security/`，见 §6 Q4）** |
| 对抗验证设施 | `src/zephyr/security/adversarial_validation/`（attack_registry/defense_runner/game_day_scheduler/injection_engine 等 27 个 .py/.yaml 文件）+ `tests/safety/` 31 个测试 | 对抗演练/游戏日/混沌注入（与本栈 L7 协同） | production |
| CI 安全门禁 | `.github/workflows/lsg_security_gate.yml` | 蓝图 §35.3 已设计 | **draft（磁盘不存在，未落盘）** |
| Gate 注册 | `src/zephyr/gates/_registry.yaml` | GCT-026 LSG Security Gateway 门禁 | production（蓝图 §17a 登记 ✅） |
| Phase 管理 | `src/zephyr/governance/phase_manager.py` | gate_lsg_security 挂到 Phase 1 | production（蓝图 §17a 登记 ✅） |
| Phase 检查 | `src/zephyr/governance/phase_check_registry.py` | check_lsg_security 函数 | **draft（蓝图 §17a 标 🔒 锁定，待补）** |
| 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 版本号/完整度同步 | draft（蓝图 §17a 标"待更新"） |

> ⚠️ **路径漂移提示**：蓝图 §60/§61/§17a 中部分路径写作 `src/zephyr/llm_security/`，磁盘实测该目录不存在；实际代码落位为 `src/zephyr/security/llm_defense/llm_security/`（蓝图 §3~§11 各层接口注释中的路径为正确路径）。此漂移属蓝图维护范畴，本文只记录不修改（见 §6 开放问题 Q4）。
---

## 3. 设计决策

### 3.1 L0~L8 分层设计 why

**决策**：保留九层纵深防御（L0 供应链 → L1 输入 → L2 Prompt → L2a 进程沙箱 → L3 输出 → L4 Agent → L5 资源 → L6 可观测 → L7 持续验证 → L8 多Agent），不合并、不裁层。

**理由**：
1. **单层必被绕过**——注入检测（L1）再强也有逃逸样本，输出审查（L3）是第二道闸；权限最小化（L4）保证即使前后都被穿透，损害半径仍受限。纵深防御的本质是"任何单点失效不致命"。
2. **威胁覆盖矩阵要求九层**——蓝图 D-INF014-02 决策记录：OWASP Top 10 for LLM 2025 + MITRE ATLAS v5.4 + NIST AI RMF 三框架全覆盖需要九层（蓝图 §2/§20/§22 有逐条映射）。4 层/6 层方案在蓝图评审时已被否决（覆盖不全），本文不翻案。
3. **合并无收益**——层内代码已实现约 80%、60 个专项测试已在库；此时合并层只会破坏已有测试资产和接口契约（蓝图 §4 有 Tier 1 消费者：Gate Engine / Context Engine / MCP Servers / Agent RBAC），属于为"简洁"付双倍代价。
4. **过度工程自检结论**（对应第 6 轮审查）：九层对个人项目看似重，但 ①层内实现已完成，维护成本是边际的；②蓝图 §26 专门设计了 1 人+AI 维护加固（自动化率目标、Owner 注意力保护、自愈）；③L7 供应链安全并未超出个人项目范围——AI 生成代码 100% 依赖第三方包，Slopsquatting（AI 幻觉包，蓝图 §37）正是个人项目最脆弱的入口。**结论：保留九层**。

**考虑过的替代方案**：
| 替代方案 | 否决理由 |
|---------|---------|
| 4 层 guardrails（G1~G4）替代九层 | 覆盖不全（无供应链/持续验证/多Agent），蓝图 D-INF014-02 已否决 |
| 6 层合并（L2a 并入 L2、L8 并入 L4） | 蓝图 D-INF014-03 已否决 L2a 合并（进程沙箱有独立部署/测试需求）；L8 独立是因多Agent 信任链与单 Agent 权限是不同威胁模型 |
| 外挂第三方安全网关（如托管式 LLM Firewall） | 违反网络约束（30Mbps）与 §5 不做外部安全服务；且 fail-closed 语义无法外包 |

### 3.2 四层 guardrails（G1~G4）与 L0~L8 的关系

**结论口径（待 Owner 确认，见 §6 Q1）**：G1~G4 与 L0~L8 不是两套并行机制，而是**同一套 LSG 的两种视图**——G 系是 [00_index.md](00_index.md) §3.3 面向架构速览的"运行时四段"表达，L 系是蓝图面向施工的"纵深防御栈"表达。**LSG L0~L8 是实现载体，G1~G4 是其摘要映射**。

映射关系（本文分析，供 16 号文对齐引用）：

| G 系（00_index §3.3） | 内容 | 映射到 LSG 层 |
|------|------|--------------|
| G1 输入过滤 | Prompt 注入检测 + Spotlighting 分隔 | L1 输入防护（直接/间接/越狱三层检测）+ L2 Prompt 保护（System Prompt 隔离） |
| G2 模型运行 | 工具调用验证 + 意图分类 + 目标偏移检测 | L4 Agent 安全（工具调用验证）+ `alignment_scorer.py`（意图/目标对齐）+ L5 资源保护（运行约束）+ L8 多Agent（跨Agent 行为） |
| G3 输出审查 | 幻觉检测 + 敏感信息 + Schema 检查 | L3 输出安全（四层输出验证含幻觉检测/PII 脱敏/Schema） |
| G4 权限审计 | 最小权限 + 操作审计 + 实时阻断 | L4 权限最小化/HITL + L6 可观测性（行为审计日志/实时告警） |
| （G 系未覆盖） | — | L0 供应链（构建时）+ L2a 进程沙箱（执行隔离）+ L7 持续验证（离线回归）——这三层在 G 系视图之外，属"非运行时"防御 |

由此回答核心问题"安全栈是否包含 guardrails"：**是——G1~G4 的全部能力由 LSG 对应层承载；LSG 额外提供 G 系未表达的构建时（L0）、隔离（L2a）、离线验证（L7）三段防御**。两者无功能重叠冲突，只有表达粒度差异。

### 3.3 MCP Triple Gate 与 L0~L8 的映射

[00_index.md](00_index.md) §3.3 的 MCP Triple Gate（Gate1 输入过滤 + Gate2 对齐审查 + Gate3 权限隔离）同样由 LSG 承载，且蓝图已有 MCP 专项设计（§30 OWASP MCP Top 10 覆盖矩阵、§31 Sampling 攻击防御、§57 MCP STDIO RCE 深度供应链防御）：

| Triple Gate | 映射到 LSG | 蓝图依据 |
|------|------|------|
| Gate1 输入过滤 | L1 输入防护（MCP 工具返回内容按间接注入扫描）+ 蓝图 §38 ToolResultTransform 防御点 | §4 L1 / §38 |
| Gate2 对齐审查 | L4 Agent 安全（`alignment_scorer.py` 意图对齐 + 工具描述审计 `tool_descriptor_audit()`）+ 蓝图 §31.4 Sampling 防御 | §7 L4 / §31 |
| Gate3 权限隔离 | L4 权限最小化 + L0 `verify_mcp_server()` 供应链验证（MCP 服务器身份/来源校验） | §7 L4 / §3 L0 / §16 集成目标 MOD-INF-013 |

**why 不单独建 MCP 安全层**：MCP 威胁（工具投毒/Sampling 劫持/STDIO RCE）的攻击面与 L0/L1/L4 高度重叠，独立建层会造成同一威胁两处防御、判决不一致；蓝图选择"能力内嵌到现有层 + 专项节描述"是正确取舍，本文遵循。

### 3.4 fail-closed 原则的集成含义 why

蓝图 D-INF014-01：LSG 不可用时拒绝所有 LLM 流量——宁可停服不可裸奔。该原则对**集成施工**有三条硬性推论：

1. **统一入口必须是唯一入口**：`gateway.py` 是所有 LLM 调用的必经闸门；任何"直连 LLM 客户端"的代码路径都等价于绕过 fail-closed。因此集成验收的核心指标是"绕过路径数 = 0"（见 §4.2 静态检查 + 运行时拦截）。
2. **例外层必须显式分级**：蓝图 §12 已定 L6（日志降级 stderr）/L7（不阻断）为 fail-open 例外，其余 L0~L5/L8 全部 fail-closed。集成接线不得改变此分级——尤其不得为了"不阻塞施工"把 L1/L3 改成 fail-open。
3. **LSG 自身可用性成为 SLO**：fail-closed 把 LSG 故障放大为全系统 LLM 中断（风险 R8），因此 §4 施工计划包含分层健康检查独立化 + Owner override 通道，且 LSG 进程的资源预算（CPU<5%、内存<256MB，蓝图 §40.3）纳入验收。

### 3.5 集成方式：网关拦截 why

**决策**：采用"统一网关 + 运行时拦截 + 静态检查"三重集成，而非"各调用点自觉调用 LSG"。

**理由**：100% AI 生成代码的施工方式下，"调用点自觉"不可持续——新 AI 会话冷启动时不知道有 LSG，必然产生绕过路径。只有结构性约束（客户端构造即注入网关）+ 静态检查（CI/预提交扫描直连模式）+ 运行时兜底（`runtime_interceptor.py` 拦截未过网关的调用并告警）三者叠加，才能把"必经安全栈"从约定变成不变量。这与蓝图 §1 核心职能（"任何 AI agent 发起 LLM 请求前必须经过 L0/L1/L2 检测"）和 §16 集成目标一致。
---

## 4. 施工计划

> 真源边界：层内剩余功能（L3B 沙箱/Threat Intel 等）的**设计细节**见蓝图对应 §x.5 施工状态节，本文只排集成与收尾的**顺序、验收、接口**。

### 4.1 第 0 步：depgraph 登记（L1 铁律，先于一切施工）

按通用规则 19，本施工涉及的依赖关系先登记后施工：

1. 用 `apply_depgraph` 将以下依赖登记到 depgraph 设计态（status=planned）：
   - `MOD-LLM_SECURITY` → 三层运行时 LLM 客户端（10 号文域，待其模块定名后补挂）
   - `MOD-LLM_SECURITY` → `MOD-INF-013`（MCP Servers，L0/L4 校验，蓝图 §16 已声明）
   - `MOD-LLM_SECURITY` → `MOD-INF-020`（Audit Trail，L6 审计链，蓝图 §16 已声明）
   - `MOD-LLM_SECURITY` → `MOD-CONTEXT_ENGINE`（L1 注入前扫描，蓝图 §16 已声明）
   - `signal_bus/`（v2.0.0 新增模块）→ `MOD-GATE_ENGINE` 信号消费（蓝图 §0-升级 §0.5 容量责任划分）
2. 全部施工验证通过后，最后一步统一将上述登记项 status 由 planned → production（见 §4.7）。

### 4.2 Phase 0（P0）：输入/输出主链路贯通 + 绕过路径清零

> 指令口径"Phase 0：L0（输入过滤）+ L1（输出审查）优先"按蓝图分层落地为：**输入侧（L1）+ 输出侧（L3）主链路优先贯通，L0 供应链以启动时验证方式随行**（L0 运行时开销 <1ms，蓝图 §40.1）。蓝图分层定义（L0=供应链/L1=输入/L3=输出）为唯一真源。

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P0-1 | 统一入口接线 | 三层运行时的 LLM 客户端构造点统一注入 `gateway.py`；本地 Ollama / API / Trae 三类通道同一闸门 | 任一类通道发起 LLM 调用，L6 审计日志均有对应 L1/L3 判决记录；`tests/llm_security/test_gateway_e2e.py` 扩展用例通过 |
| P0-2 | 绕过路径静态检查 | 预提交/CI 扫描"直连 LLM 客户端"模式（绕过网关的 import/构造） | 扫描规则入库；全仓扫描报告绕过路径数 = 0（豁免项白名单登记） |
| P0-3 | 运行时拦截兜底 | `runtime_interceptor.py` 对未过网关的调用实时拦截+告警 | 人工注入一条绕过路径的探针代码，拦截器 100% 捕获并产生 L6 告警事件 |
| P0-4 | L0 启动时验证接线 | 模型/依赖加载前走 `l0_supply_chain` 验证，验证结果缓存 | 篡改任一依赖哈希的探针测试：加载被拒（fail-closed 生效） |
| P0-5 | fail-closed 演练 | 逐层故障注入（L1/L3/L4/L5 各挂一次） | 每次故障→对应流量被拒 + Owner override 通道可用（蓝图 §12 分级表逐项验证）；`tests/llm_security/test_fail_closed.py` 通过 |

### 4.3 Phase 1（P1）：蓝图剩余缺口收尾（层内 80% → 95%）

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P1-1 | L6 飞书告警 Webhook | 蓝图 §9 剩余项：高危安全事件实时推送 Owner | 注入高危探针事件 → Webhook 送达（含降级策略：Webhook 不可达时本地持久化不丢事件） |
| P1-2 | L7 CI 安全门禁落盘 | 蓝图 §35.3 已设计的 `.github/workflows/lsg_security_gate.yml` 落盘（当前磁盘不存在） | PR 触发门禁：golden 回归集（蓝图 §35.1 已设计，`tests/llm_security/golden/` 磁盘不存在，随本任务一并落盘）全绿才放行 |
| P1-3 | L5 性能预算管理 | 蓝图 §40.4 `LSGPerformanceGuard`（当前 0%）：延迟埋点 + 超预算自动降级 | 压测验证 P95<50ms；人为制造延迟超预算 → 按 §40.4 降级顺序自动降级且"永不可降级项"（L1A/L3B/L4/L5 成本熔断）不被降级 |
| P1-4 | phase_check_registry 补挂 | 蓝图 §17a 第 7 项：`check_lsg_security` 函数补入（当前 🔒 锁定） | `phase_manager` Phase 1 门禁检查可正常消费 LSG 健康状态 |
| P1-5 | 蓝图注册表同步 | 蓝图 §17a 第 1 项：`blueprint_registry.yaml` 版本号/完整度同步 | 注册表与蓝图 §14 完整度一致 |

### 4.4 Phase 2（P2）：纵深增强与跨层链路验证

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P2-1 | L3B Docker/WASI 沙箱 | 蓝图 §6.5/§11 剩余项：代码执行沙箱从进程级升级到容器/WASI 级 | 恶意代码执行探针在容器内被隔离；Windows 单机可用（WSL2/Hyper-V 后端），不引入集群依赖 |
| P2-2 | L7 Threat Intel 自动拉取 | 蓝图 §10 剩余项：威胁情报周期性更新（30Mbps 网络约束下低频批量） | 拉取任务可手动触发 + 周频自动；失败不影响已有规则库（fail-safe 于本项） |
| P2-3 | 跨层链路 E2E 基线 | L1 拦截→L6 记录→L7 回归→L4 阻断的端到端测试基线 | `tests/llm_security/test_cross_module_integration_llm_security.py` 扩展：跨层时序断言通过 |
| P2-4 | L1 误报调优闭环 | 风险 R1/R10：误报反馈→白名单豁免→规则降权（AI 辅助维护，风险 R7） | 连续 2 周误报率下降趋势（L6 仪表板可观测）；白名单审批留痕 |
| P2-5 | L8 级联注入扩展 | 蓝图 §45：跨 Agent 链级联注入防御扩展（与 12 号文多 Agent 投票施工联动） | 级联注入探针（Agent A 输出污染 Agent B 输入）被 L8 信任评分+通信隔离阻断 |

### 4.5 v2.0.0 信号总线（D6-D16）启动条件

蓝图 §0-升级已定 v2.0.0：`signal_bus/`（IngestBuffer/SignalRouter/DedupCache/SessionContextManager/BackpressureController/CrossSignalCorrelator，asyncio.Queue 方案，D-INF014-04~07）。**本文不动其设计**，只定启动门：

- **启动前提**：① Phase 0/1 全部验收通过；② 治理脚本并发量达到蓝图 §17.1 容量基线临界点（LSG 安全信号事件量持续逼近 100/天 或并发 LLM 调用 >3）；③ 06/07/08 号文对应设施（画像/Context Engine/多 AI 并发治理）已就位于消费侧。
- **未达前提不施工**——当前容量基线（<100 信号/天、1-3 并发）下现有直连消费模式足够，提前施工信号总线 = 过度工程。

### 4.6 与其他文档的接口

**与 [10_llm_infrastructure.md](10_llm_infrastructure.md) 的接口（LLM 推理时如何嵌入安全栈）**：
- 接口假设（10 号文当前为骨架 v0.1.0，见 §6 Q2）：三层运行时的 LLM 客户端工厂是唯一集成点——客户端实例化时强制包裹 LSG 网关；运行时向 LSG 提供 `SecurityContext`（调用方身份/会话/预算标签），LSG 回传安全判决（放行/脱敏后放行/阻断）。
- 推理优化（llama.cpp+GPTQ）与 LSG 无耦合：量化模型加载走 L0 验证，推理过程不经 LSG（LSG 只守门请求/响应，不进推理热路径，满足 §2.3 GPU 约束）。
- MCP 工具调用：10 号文 MCP Client 的每次工具调用过 L4 `authorize_tool_call()`，工具返回内容过 L1 间接注入扫描（蓝图 §16 MOD-INF-013 集成点）。

**与 [16_ai_security_ops.md](16_ai_security_ops.md) 的接口（安全事件如何流入运维闭环）**：
- 接口假设（16 号文当前为骨架 v0.1.0，见 §6 Q3）：L6 安全事件经 `behavior_audit_logger.log_security_event()` 写入审计链（蓝图 §16 MOD-INF-020 集成点），16 号文的 Detect 环节消费该事件流；KILLSWITCH 三级响应触发时，LSG 侧表现为 L5 全量熔断 + fail-closed 闸门关闭。
- 职责边界：LSG 负责"检测+阻断+记录"，16 号文负责"诊断+修复+学习"——LSG 不做自愈决策，自愈动作由 16 号文闭环下达（如规则库更新、白名单调整），LSG 提供执行接口。

**与交易决策侧的关系**：只读不改。LSG 对交易链路的唯一要求是"LLM 不介入下单热路径"（§2.3 已满足）；金融合规门禁（蓝图 §52，L4 内）的消费侧在交易决策侧，发现需同步改的记 §6。

### 4.7 收尾验证与 depgraph 状态翻转

1. 全部 Phase 0/1 验收项通过，Phase 2 按优先级滚动推进；
2. `tests/llm_security/` 专项测试 + 根级测试（需先核实根级测试是否已迁移）全绿；
3. 绕过路径静态扫描连续一周零新增；
4. LSG P95 延迟 < 50ms 实测达标（L6 仪表板读数）；
5. 上述全部满足后，`apply_depgraph` 将 §4.1 登记项 status planned → production。
---

## 5. 不做什么

1. **不做外部安全服务集成**——不接第三方内容审核 API / 托管式 LLM Firewall：30Mbps 网络下延迟与成本不可控，且 fail-closed 语义无法外包（§3.1 替代方案表）。
2. **不做形式化安全验证**——个人项目以"对抗测试 + 黄金回归集 + 审计"替代（蓝图 §35 回归测试 + §18 风险表已覆盖该取舍）。
3. **不做零知识证明/决策溯源链 DAG/AI 伦理声明**——[00_index.md](00_index.md) v0.4.0 已裁定 A6 AI 合规过度工程并移除，本文不复活。
4. **不重写 L0~L8 层内已实现逻辑**——层内设计真源是蓝图；本文只排集成与收尾顺序。任何层内重构需求回到蓝图流程（蓝图修改条件表：接口契约变更需 Owner 审批）。
5. **不做多模态注入防御专项施工**——蓝图 §55（L1a 多模态层，0%）降级为远期：本项目 LLM 交互以文本/代码为主，图像/音频通道当前无攻击面；待多模态输入实际引入时再从蓝图启动。
6. **不做内核级/FPGA 级安全隔离**——Windows 用户态 + Python 的现实上限是进程沙箱（L2a）+ 容器沙箱（P2-1）；硬件级隔离超出单机 PC 约束（system_charter §2）。
7. **不提前施工 v2.0.0 信号总线**——未达 §4.5 启动门前，现有容量（<100 信号/天）下施工即过度工程。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | LLM 安全栈与 A5 安全架构中 LLM 4层 guardrails 的关系？ | 待裁定 | 本文 §3.2 已给出分析口径：G1~G4 是 L0~L8 的"运行时四段"摘要视图，LSG 是实现载体，G 系全部能力由 L 系承载、无重叠冲突；L0/L2a/L7 在 G 系视图之外。**该口径需 Owner 确认后，由 00_index/16 号文对齐引用**（本文只改自己，不越界改 00_index） |
| Q2 | 与 10 号文的运行时集成点假设是否成立？ | 待确认（接口假设） | 10 号文当前为骨架 v0.1.0。本文 §4.6 假设"LLM 客户端工厂统一注入网关 + SecurityContext 传递 + MCP 工具调用过 L4"。若 10 号文填充后采用不同集成方式（如代理侧车/独立安全进程），本文 §4.2/§4.6 需对齐修订 |
| Q3 | 与 16 号文的安全事件流接口假设是否成立？ | 待确认（接口假设） | 16 号文当前为骨架 v0.1.0。本文 §4.6 假设"L6 事件 → 审计链 → 16 号文 Detect 消费；KILLSWITCH 触发 → L5 全量熔断"。若 16 号文定义不同事件总线/消费协议，需对齐修订 |
| Q4 | 蓝图路径漂移如何修正？ | 待用户裁定（蓝图侧，本文只读） | 蓝图 §60/§61/§17a 多处写 `src/zephyr/llm_security/`，磁盘实测不存在；实际落位 `src/zephyr/security/llm_defense/llm_security/`。另 `.github/workflows/lsg_security_gate.yml` 蓝图已设计未落盘（本文 P1-2 已排施工）。蓝图修正属蓝图 owner 流程，本文不越界改 |
| Q5 | 00_index §5.2 列出的 `derived_graphs/06_llm_security_stack.md` 磁盘不存在 | 待 AI-FILL-00/用户裁定 | 00_index 目录树引用该派生图但文件未建。本文可发现性不依赖该图（本文从 00_index §5.2 implementation_plans 目录树可达），仅记录待办 |
| Q6 | L7 红队扫描的算力排期？ | 待裁定 | 蓝图风险 R6 要求红队不使用生产 API；本地模型红队需占用 RTX 3090（显存 <90% 硬上限与推理任务竞争）。周频批量 vs 触发式（代码变更时）的排期策略需 Owner 裁定 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景（L0~L8 各层实现状态实测表/核心问题/约束/设施盘点 20 行）、§3 设计决策（九层保留 why/G1~G4 与 L0~L8 映射/MCP Triple Gate 映射/fail-closed 集成含义/网关拦截 why，含替代方案表）、§4 施工计划（depgraph 登记→Phase 0 主链路贯通→Phase 1 蓝图缺口收尾→Phase 2 纵深增强→v2.0.0 启动门→10/16 号文接口→收尾验证）、§5 不做什么 7 项、§6 开放问题扩至 Q1~Q6 | 按 AI-FILL-09 指令执行填充；10/16 号文未填充，接口假设降级写入开放问题 Q2/Q3 |

---

*维护者：AI 架构协调者*