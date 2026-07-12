---
module_id: MOD-INF-022
submodule_path: src/zephyr/governance/escalation_engine.py
title: Escalation Protocol 蓝图
doc_type: blueprint
status: Active
version: "2.1.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-14"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/governance/"
last_updated: "2026-06-23"
last_verified: "2026-06-23"
generation: 3
functional_domain: safety_escalation
template_for: blueprint
parent_module: ""
references:
  - D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md
  - D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml
  - D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md
codification_level: blueprint
codification_at: "2026-05-14"
belongs_to: MOD-MASTER_BLUEPRINT
summary: "AI操作安全升级与委托治理协议——五层架构（L0持久化→L1自愈→L2路由→L3通知→L4审计），30决策/104文件，量化交易特化升级，Vibe Coding安全防御"
tags: [escalation, safety, delegation, guardrail, vibe-coding]
priority: P1
activation_phase: current
runtime_plane: hot
ssot_claims:
  - dimension: "升级规则判定(autonomous/auto_guard/blocked)"
    is_ssot: true
  - dimension: "委托链管理(四级约束+MAX_DEPTH=3)"
    is_ssot: true
  - dimension: "死锁检测(Dijkstra+DFS+抢占)"
    is_ssot: true
  - dimension: "三级决策枚举(EscalationLevel)"
    is_ssot: true
  - dimension: "熔断器"
    is_ssot: false
    ssot_owner: "MOD-INF-016 shared/resilience"
  - dimension: "Merkle审计链"
    is_ssot: false
    ssot_owner: "MOD-INF-020 audit-trail"
  - dimension: "Agent行为漂移检测"
    is_ssot: false
    ssot_owner: "MOD-INF-023 behavioral-auditor"
  - dimension: "Agent串谋检测"
    is_ssot: false
    ssot_owner: "MOD-INF-025 a2a_protocol"
  - dimension: "经济护栏(Token预算+模型降级+成本审计)"
    is_ssot: false
    ssot_owner: "MOD-INF-024 budget-enforcer"
  - dimension: "Per-escalation成本门控(升级前预算检查)"
    is_ssot: true
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - {target: MOD-INF-018, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: MOD-GATE_ENGINE, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: MOD-INF-019, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: MOD-INF-020, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: MOD-INF-021, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: MOD-INF-024, at: "$TODO", why: "TODO -- auto-converted"}
  - {target: MOD-INF-025, at: "$TODO", why: "TODO -- auto-converted"}
responsibility_domain: 
build_status: planned
design_maturity: design
---

## MOD-GOVERNANCE 集成契约锚点

| 契约 ID | 本模块角色 | 对端模块 | 集成点 |
|---------|------------|----------|--------|
| G-CT-003 | 消费方（回滚结果/权限变更触发升级重评估） | MOD-INF-021 | RB 产出→升级事件重新评估 |
| G-CT-004 | 产出方（升级决策回灌 RBAC） | MOD-INF-018 | 升级级别与权限级别对齐 |
| G-CT-006 | 消费方（预算触发的升级） | MOD-INF-024 | Token 预算超支→升级事件 |
| G-CT-008 | 消费方（A2A 冲突仲裁升级；A2A 同时通知 RBAC 调整权限；Protocol接口解耦） | MOD-INF-025 | Agent 间冲突→升级仲裁+RBAC 权限调整 |

---

# Escalation Protocol 蓝图+施工图 — AI操作安全升级与委托治理协议

> module_id: MOD-INF-022 | version: 2.1.0 | status: active | domain: infra_ops
> actual_disk_path: `D:\ZephyrAlpha\src\zephyr\escalation-engine\` | generation: 3 | construction_progress: partially_implemented

## 概述

Escalation Protocol 是 ZephyrAlpha 安全升级与委托治理核心协议。五层架构（L0持久化→L1自愈→L2路由→L3通知→L4审计）覆盖升级判定+委托+Per-escalation成本门控。核心职责：规则驱动判定（autonomous/auto_guard/blocked）、委托链管理（四级约束+死锁防护）、Per-escalation成本门控。子蓝图MOD-INF-022-VC(Vibe Coding安全防御)和MOD-INF-022-QT(量化交易特化升级)已拆分。当前规模110文件/30决策，上游依赖RBAC(MOD-INF-018)/Gate(MOD-GATE_ENGINE)/Audit(MOD-INF-020)/Pipeline(MOD-INF-021)，下游被Budget(MOD-INF-024,预算SSoT)/A2A(MOD-INF-025,消费本协议SSoT)/治理层消费。

**标准锚点**：本蓝图遵循 [blueprint-template.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md) v3.6 | AI 压缩工作流标准 [trae_030_doc_numbering_metadata.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml) | 代码头部标准 [code-construction-standards.md §7](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md) | 优化规则见 onboarding_detail.md §10.6

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-022`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 |
|---|--------|------------|------|:-----:|---------|
| 1 | __init__.py | §3.1 | 包初始化 | 已实现 | 本模块 |
| 2 | escalation-engine.py | §4.1 | 升级引擎——规则驱动判定+健康检查 | 已实现 | 本模块 |
| 3 | escalation_models.py | §4.2 | 升级数据模型 | 已实现 | 本模块 |
| 4 | escalation_metrics.py | §9 | 指标收集——升级率/假阳性率/延迟/成本 | 已实现 | 本模块(✅已修复——evaluate()自动调用metrics.record()) |
| 5 | circuit_breaker.py | §3.1 | 熔断器 | 已实现(022特有error_budget扩展) | SSoT核心=MOD-INF-016，error_budget保留本模块 |
| 6 | adapter.py | §3.1 | 适配器 | 已实现 | 本模块 |
| 7 | contracts.py | §4.2 | 契约定义 | 已实现 | 本模块 |
| 8 | self_test.py | §9 | 自测试 | 已实现 | 本模块 |
| 9 | delegation_manager.py | §4.2 | 委托管理——能力匹配+四级约束+死锁防护 | 已实现 | 本模块 |
| 10 | delegation_engine.py | §4.2 | 委托引擎 | 已实现 | 本模块 |
| 11 | context_package.py | §4.4 | 委托上下文包——7字段结构化状态传递 | 已实现 | 本模块 |
| 12 | deadlock_detector.py | §6.2 | 死锁检测——循环检测+资源等待图+优先级抢占 | 已实现 | 本模块 |
| 13 | economic_guard.py | §4.5 | 经济护栏——Per-escalation成本门控 | 已实现(022特有per-escalation门控) | SSoT预算=MOD-INF-024，本模块仅保留升级成本门控 |
| 14 | budget_handler.py | §4.5 | 预算处理 | 已实现 | 本模块(⚠️与MOD-INF-024重叠) |
| 15 | slo_contract.py | §4.6 | SLO合约——SLI检查+Error Budget消耗速率 | 已实现 | 本模块 |
| 16 | interrupt_handler.py | §4.3 | 硬中断——Owner停止/回退+紧急覆盖 | 已实现 | 本模块 |
| 17 | approval.py | §4.3 | 审批 | 已实现 | 本模块 |
| 18 | confidence_estimator.py | §3.1 | 置信度评估——自评+历史准确率+自动校准 | 已实现 | 本模块 |
| 19 | meta_confidence.py | §3.1 | Meta-Confidence——引擎对自身判定的置信度 | 已实现 | 本模块 |
| 20 | persuasion_detector.py | §8.1 | 心理说服检测——Cialdini六原则+Crescendo | 已实现 | 本模块 |
| 21 | identity_verifier.py | §8.2 | Agent身份验证——JWT+克隆检测 | 已实现 | 本模块 |
| 22 | compliance_mapper.py | §8 | 合规映射——法律→规则强度+blocked同步确认 | 已实现 | 本模块 |
| 23 | construction_verifier.py | §9 | 施工验证——编译时检查+验证checklist | 已实现 | 本模块 |
| 24 | engine_sandbox.py | §8.2 | 引擎Sandbox——bubblewrap/seatbelt策略 | 已实现 | 本模块 |
| 25 | process_isolator.py | §8.2 | 进程隔离——独立保护进程+IPC | 已实现 | 本模块 |
| 26 | drift-detector.py | §8 | Agent漂移检测——四维+自动校准 | 兼容别名(frozen) | SSoT=MOD-INF-023，本模块保留同步API |
| 27 | vigil_runtime.py | §8 | VIGIL维护运行时——EmoBank+RBT+Core Identity | 已实现 | 本模块 |
| 28 | formal_verifier.py | §8 | 形式验证——MCMAS+不变量验证 | 已实现 | 本模块 |
| 29 | escalation_api.py | §4 | Service Account API——REST+JWT轮转 | 已实现 | 本模块 |
| 30 | cross_assistant_adapter.py | §4 | 跨助手适配——Cursor/Windsurf/Trae统一 | 已实现 | 本模块 |
| 31 | strategy_scoper.py | §4 | 策略范围——strategy_id+跨策略隔离 | 已实现 | 本模块 |
| 32 | provider_failover.py | §8 | 多Provider容灾——五级降级链 | 已实现 | 本模块 |
| 33 | credential_guard.py | §8 | 密钥泄露防护——异常检测+自动吊销 | 已实现 | 本模块 |
| 34 | coldstart_manager.py | §8 | 冷启动——7天Imprint+渐进校准 | 已实现 | 本模块 |
| 35 | human_factors.py | §8.8 | 人因工程——疲劳/情绪/睡眠感知 | 已实现 | 本模块 |
| 36 | anti_automation_bias.py | §8.1 | 反自动化偏见——强制随机审查+审查率监控 | 已实现 | 本模块 |
| 37 | rule_debt_auditor.py | §5 | 规则债务审计——过时检测+冲突检测 | 已实现 | 本模块 |
| 38 | rule_shadow_runner.py | §5 | 规则影子模式——假阳性统计 | 已实现 | 本模块 |
| 39 | rule_canary_manager.py | §5 | 规则金丝雀——Canary范围+自动回滚 | 已实现 | 本模块 |
| 40 | self_validator.py | §9 | 升级协议自验证——Shadow Parallel Run | 已实现 | 本模块 |
| 41 | merkle_audit.py | §8.3 | 密码学审计——Merkle Tree+哈希链+外部锚定 | 兼容别名(frozen) | SSoT=MOD-INF-020，内部委托MerkleAggregator |
| 42 | forensic_package.py | §8.3 | 取证就绪——证据包+因果图+in-toto | 已实现 | 本模块 |
| 43 | integrity_verifier.py | §8.3 | 代码完整性——启动链+源码hash+运行时校验 | 已实现 | 本模块 |
| 44 | sbom_guard.py | §8.3 | 依赖供应链——SBOM+签名+幽灵依赖 | 已实现 | 本模块 |
| 45 | ghost_scan.py | §8.3 | 幽灵进程检测——内核级交叉验证 | 已实现 | 本模块 |
| 46 | clock_guard.py | §8.3 | 时钟完整性——多源验证+NTS+NTP攻击 | 已实现 | 本模块 |
| 47 | witness_isolation.py | §8.3 | Witness隔离——容器化+独立namespace | 已实现 | 本模块 |
| 48 | collusion_detector.py | §8.3 | 共谋检测——共识异常+非AI验证 | 兼容别名(frozen) | SSoT=MOD-INF-025 |
| 49 | silence_detector.py | §8.3 | 静默窗口——预期事件模型+gap分析 | 已实现 | 本模块 |
| 50 | gap_analyzer.py | §8.3 | 间隙分析——事件缺失即证据 | 已实现 | 本模块 |
| 51 | last_resort_watchdog.py | §8.3 | 终极逃生舱——Rust/Go守护+心跳ALL_STOP | 已实现 | 本模块 |
| 52 | vibe_security_verify.py | §8.4 | Vibe Coding安全验证——per-file四维测试 | 已实现 | 本模块 |
| 53 | vibe_verify_integration.py | §8.4 | Vibe验证集成 | 已实现 | 本模块 |
| 54 | config_scanner.py | §8.4 | AI配置注入扫描——.cursorrules/CLAUDE.md | 已实现 | 本模块 |
| 55 | github_api_guard.py | §8.4 | Comment and Control防御——PR/Issue清洗 | 已实现 | 本模块 |
| 56 | api_response_sanitizer.py | §8.4 | API返回清洗——去injection marker | 已实现 | 本模块 |
| 57 | memory_poison_guard.py | §8.4 | 记忆投毒防护——存储前检测+时域分离 | 已实现 | 本模块 |
| 58 | memory_provenance.py | §8.4 | 记忆溯源——来源+trust_level+hash | 已实现 | 本模块 |
| 59 | cross_session_correlator.py | §8.4 | 跨会话关联——top-K+跨会话异常 | 已实现 | 本模块 |
| 60 | objective_tracker.py | §8.4 | 目标漂移——嵌入余弦相似度 | 已实现 | 本模块 |
| 61 | command_chain_length_gate.py | §8.5 | 命令体积门控——max=20子命令 | 已实现 | 本模块 |
| 62 | subagent_hook_propagator.py | §8.5 | 子Agent Hook传播——继承+sha256校验 | 已实现 | 本模块 |
| 63 | alternative_path_blocker.py | §8.5 | 替代路径拦截——bash pattern+chroot | 已实现 | 本模块 |
| 64 | security_config_scanner.py | §8.5 | 安全配置扫描——数据库/云/API | 已实现 | 本模块 |
| 65 | multi_turn_intent_analyzer.py | §8.5 | 多轮语义分析——10轮链+per_tool budget | 已实现 | 本模块 |
| 66 | bare_repo_scanner.py | §8.6 | 裸仓库检测——pre_clone+whitelist | 已实现 | 本模块 |
| 67 | git_hook_pre_scanner.py | §8.6 | Git Hook预扫描——risky_patterns | 已实现 | 本模块 |
| 68 | compositional_safety_tester.py | §8.6 | 组合安全测试——pairwise+test generator | 已实现 | 本模块 |
| 69 | position_reconciler.py | §8.7 | 持仓对账——内部vs交易所+P0-FATAL | 已实现 | 本模块 |
| 70 | data_pipeline_guard.py | §8.7 | 数据管道完整性——陈旧/缺失/交叉校验 | 已实现 | 本模块 |
| 71 | order_state_escalator.py | §8.7 | 订单状态机升级——超时/停滞/异常 | 已实现 | 本模块 |
| 72 | flash_crash_guard.py | §8.7 | 闪崩双轨熔断——MWCB 7/13/20% | 已实现 | 本模块 |
| 73 | arbitrage_asymmetry_detector.py | §8.7 | 套利不对称——trade_pair+自动平仓 | 已实现 | 本模块 |
| 74 | exchange_reg_monitor.py | §8.7 | 交易所规则变更——API字段+公告爬取 | 已实现 | 本模块 |
| 75 | exchange_partition_detector.py | §8.7 | 交易所网络分区——heartbeat+多路径 | 已实现 | 本模块 |
| 76 | account_isolator.py | §8.7 | 多账户隔离——account_id+per-account熔断 | 已实现 | 本模块 |
| 77 | maintenance_window_adapter.py | §8.7 | 维护窗口适配——阈值调整+延迟延长 | 已实现 | 本模块 |
| 78 | hooks_integrity_guard.py | §8.8 | Hooks自编辑防护——外部hash+Owner签名 | 已实现 | 本模块 |
| 79 | escalation_fatigue_manager.py | §8.8 | 升级疲劳闭环——adaptive+weekly digest | 已实现 | 本模块 |
| 80 | context_switch_governor.py | §8.8 | 上下文切换预算——daily_capacity=16 | 已实现 | 本模块 |
| 81 | reward_hacking_rebound_detector.py | §8.8 | 三阶段反弹——90d窗口+Phase I→II→III | 已实现 | 本模块 |
| 82 | error_budget_burst_limiter.py | §8.8 | Error Budget Burst——daily≤20%/hourly≤5% | 已实现 | 本模块 |
| 83 | mvep_orchestrator.py | §16.1 | MVEP调度——Phase 0→5+Phase Gate | 已实现 | 本模块 |
| 84 | escalation_smoke_tests.py | §9.1 | 烟雾测试——9条SMOKE用例 | 已实现 | 本模块 |
| 85 | blueprint_bloat_monitor.py | §16 | 蓝图膨胀监控——diminishing_returns+max=100 | 已实现 | 本模块 |
| 86 | protocol_state_store.py | §3.1 | 协议状态持久化——SQLite+崩溃恢复 | 已实现 | 本模块 |
| 87 | protocol_self_context.py | §3.1 | 协议自维护上下文——session自动注入 | 已实现 | 本模块 |
| 88 | autonomy_regressor.py | §17 | 渐进自治可逆性——回归触发器+冷却 | 已实现 | 本模块 |
| 89 | model_version_detector.py | §8 | 模型版本突变——Fingerprint+KL divergence | 已实现 | 本模块 |
| 90 | escalation_loop_detector.py | §6 | 跨模块循环——因果有向图+DFS | 已实现 | 本模块 |
| 91 | meta_observability.py | §3.1 | 协议自身可观测性——自健康+dead-man-switch | 已实现 | 本模块 |
| 92 | blueprint_reconciler.py | §0.2 | 蓝图实现一致性——行为清单+DRIFT报告 | 已实现 | 本模块 |
| 93 | blueprint_code_consistency.py | §0.2 | 蓝图代码一致性 | 已实现 | 本模块 |
| 94 | a2a_failure.py | §4 | A2A故障处理 | 已实现 | 本模块 |
| 95 | rbac_bridge.py | §4 | RBAC桥接 | 已实现 | 本模块 |
| 96 | audit_write_failure_protector.py | §6.3 | 审计写入失败——INSERT失败不推进tip | 已实现 | 本模块 |
| 97 | broker_resilience.py | §8 | Broker韧性——多Broker容灾+自动切换 | 已实现 | 本模块 |
| 98 | bus_factor_defense.py | §8 | 巴士因子防御——关键人风险+知识扩散 | 已实现 | 本模块 |
| 99 | consequence_manager.py | §6 | 后果管理——升级后果追踪+回退评估 | 已实现 | 本模块 |
| 100 | decision_fatigue.py | §8.8 | 决策疲劳——疲劳检测+阈值调整 | 已实现 | 本模块 |
| 101 | decision_fatigue_cli.py | §8.8 | 决策疲劳CLI——疲劳状态查询+重置 | 已实现 | 本模块 |
| 102 | incident_response.py | §6 | 事件响应——P0/P1/P2分级+自动响应 | 已实现 | 本模块 |
| 103 | oms_risk_engine.py | §8.7 | OMS风险引擎——订单流控+仓位限制 | 已实现 | 本模块 |
| 104 | risk_matrix.py | §4 | 风险矩阵——规则类别×严重度→升级级别映射 | 已实现 | 本模块 |
| 105 | spof_checker.py | §8 | 单点故障检测——依赖图SPOF扫描+告警 | 已实现 | 本模块 |
| 106 | strategy_portfolio.py | §4 | 策略组合——多策略编排+优先级仲裁 | 已实现 | 本模块 |
| 107 | governance/__init__.py | §4 | 治理子包初始化 | 已实现 | 本模块 |
| 108 | governance/a2a_failure.py | §4 | A2A故障处理(治理层) | 已实现 | 本模块 |
| 109 | governance/approval.py | §4 | 审批(治理层) | 已实现 | 本模块 |
| 110 | governance/budget_handler.py | §4.5 | 预算处理(治理层) | 已实现 | 本模块 |
| 111 | governance/contracts.py | §4.2 | 契约定义(治理层) | 已实现 | 本模块 |
| 112 | governance/rbac_bridge.py | §4 | RBAC桥接(治理层) | 已实现 | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| blocked 规则数量≥5 | Minimal Deterministic Checker | ☐ |
| safety_constraints=4 | delegation_manager 实际检查数 | ☐ |
| fail_safe=deny_by_default | escalation-engine 实际default行为 | ☐ |
| max_depth=3 | delegation_manager 实际限制值 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | Phase 0-2 核心文件（escalation_engine/delegation/economic_guard/deadlock/confidence等） | — | — |
| v2.0.0 (容量升级) | Phase 3-5 扩展文件（forensic/vibe-coding/quant-trading/human-factors等） | escalation_rules.yaml | 配置文件未创建 |

### §0.4 SSoT与责任唯一性声明

| SSoT 维度 | 本模块是否真源 | 真源位置（如否） | 漂移风险 |
|-----------|:------------:|----------------|---------|
| 升级规则判定（autonomous/auto_guard/blocked） | ✅ | — | 无 |
| 委托链管理（四级约束+MAX_DEPTH=3） | ✅ | — | 无 |
| 死锁检测（Dijkstra排序+DFS+抢占） | ✅ | — | 无 |
| 三级决策枚举（EscalationLevel） | ✅ | — | 无 |
| 熔断器（3状态+Error Budget） | ❌ | `zephyr.shared.resilience.circuit_breaker` (MOD-INF-016) | 高——当前本地副本与SSoT不一致 |
| Merkle审计链 | ❌ | `zephyr.audit_trail.integrity.MerkleAggregator` (MOD-INF-020) | 高——当前本地副本无验证/持久化 |
| Agent行为漂移检测 | ❌ | `zephyr.behavioral_auditor.drift_engine` (MOD-INF-023) | 中——当前本地副本是简化版 |
| Agent串谋检测 | ❌ | `zephyr.infra_ops.a2a_protocol.A2ACollusionDetector` (MOD-INF-025) | 中——当前本地副本是子集 |
| Token/Cost/Time三维预算 | ❌ | `zephyr.budget_enforcer.BudgetEngine` (MOD-INF-024) | 低——本模块仅做per-escalation成本门控 |

### §0.5 代码目录唯一性声明

| 声明项 | 值 |
|--------|---|
| 唯一代码目录 | `D:\ZephyrAlpha\src\zephyr\escalation-engine\` |
| 已废弃目录 | 无（历史目录已清理，当前唯一目录见上方） |
| 验证命令 | `python -c "import zephyr.escalation_engine; print(zephyr.escalation_engine.__file__)"` |

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 由 1 人+AI 维护，AI Agent 拥有自主操作能力（代码写入/文件删除/交易执行/网络请求）。当 AI 操作超出安全边界时，必须有自动化的升级、委托、阻断机制。传统"人工审批"在 1 人+AI 语境下不可行——需要规则驱动的自动升级协议。

### §1.2 目标

| # | 目标 | 衡量标准 |
|---|------|---------|
| 1 | AI 操作安全升级 | 任何超出安全边界的操作 MUST 被自动升级/阻断 |
| 2 | 委托治理 | 多 Agent 协作时委托链深度≤3，无死锁 |
| 3 | 经济护栏 | Token 预算超支→硬中断，87%成本超支场景覆盖 |
| 4 | 量化交易特化 | 持仓对账/数据管道/订单状态机升级全覆盖 |
| 5 | Vibe Coding 安全 | AI 施工产物安全验证+配置注入防御+记忆投毒防护 |

### §1.3 不包含的目标

- 不替代 MOD-INF-018（RBAC 权限系统）——本协议消费 RBAC 判定结果
- 不替代 MOD-INF-021（Pipeline 编排）——本协议接收 Pipeline 共识破裂事件
- 不实现 AI 模型训练/微调——仅消费模型输出置信度

### §1.4 运行场景约束

| 约束 | 值 | 来源 |
|------|---|------|
| 维护模式 | 1 人+AI | 项目现实 |
| AI 施工率 | 100% | Vibe Coding |
| 安全产出率基线 | 8.25% | SUSVIBES ICLR 2026 |
| 最大升级链深度 | 3 | MIT CORDIAL |
| fail-safe default | deny_by_default | 安全系统铁律 |

### §1.5 利益相关者

| 角色 | 关注点 | 影响程度 |
|------|--------|:-------:|
| Owner（人类） | AI 操作安全+成本控制+最终控制权 | 致命 |
| AI Agent | 自主操作范围+委托能力+升级判定 | 高 |
| 治理层（MOD-GOVERNANCE） | 跨模块契约一致性+审计完整性 | 高 |
| 量化交易子系统 | 持仓安全+数据管道+订单状态 | 致命 |

### §1.6 差距

| # | 差距 | 当前状态 | 目标 | 填补方式 |
|---|------|---------|------|---------|
| 1 | escalation_rules.yaml 未创建 | 规则硬编码在 Python 中 | 外部 YAML 配置 | §5.3 迁移方案 |
| 2 | Phase 3-5 未完成 | Phase 0-2 Done | Phase 5 Done | §16.1 MVEP |
| 3 | 跨模块升级循环检测未集成 | 独立模块 | 与 Pipeline 集成 | §12 集成目标 |
| 4 | 审计链与 MOD-INF-020 双向对齐 | 单向写入 | 双向校验 | §12 集成目标 |

### §1.7 典型场景

| # | 场景 | 触发 | 升级路径 | 预期结果 |
|---|------|------|---------|---------|
| 1 | AI 尝试删除 ttl:permanent 文件 | ESC-003 | autonomous→blocked | 硬阻断+P0 通知 Owner |
| 2 | AI 修改 5+文件 | ESC-001 | autonomous→auto_guard | 先干后验+drift 检查 |
| 3 | AI 置信度<0.7 | ESC-010 | autonomous→auto_guard | 委托复核+第二意见 |
| 4 | Token 预算超 80% | ESC-011 | autonomous→auto_guard | 降级模型+通知 Owner |
| 5 | auto_guard 后验连续失败 3 次 | ESC-005 | auto_guard→blocked | 硬阻断+人工介入 |
| 6 | 委托链深度=4 | DEL-SAFE-003 | blocked | 硬拒绝+降级处理 |
| 7 | 持仓对账不一致 | ESC-TRADE-RECON-001 | blocked+P0-FATAL | 暂停交易+自动对账 |
| 8 | 闪崩 MWCB-L1 | MWCB-L1 | 暂停新入场+15min 冷静期 | 保护性熔断 |

---

## §2 模块边界

### §2.1 范围内

- 升级事件生命周期管理（创建→路由→通知→解决→复盘）
- 委托链管理与死锁防护
- 规则引擎（条件→升级级别映射，对 AI 只读）
- 经济护栏（Token 预算+模型降级+成本审计）
- 五层架构（L0-L4）完整实现
- 量化交易特化升级规则
- Vibe Coding 安全防御（配置注入/记忆投毒/跨会话攻击）
- 取证审计（Merkle Tree/SBOM/代码完整性）

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 升级规则判定(autonomous/auto_guard/blocked) | [MOD-INF-018, MOD-GATE_ENGINE] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-INF-022` |
| 委托链管理(四级约束+MAX_DEPTH=3) | [MOD-INF-025] | 同上 |
| 死锁检测(Dijkstra+DFS+抢占) | [MOD-INF-025] | 同上 |
| 三级决策枚举(EscalationLevel) | [MOD-INF-018] | 同上 |

### §2.2 范围外

| 功能 | 归属 |
|------|------|
| 权限判定 | MOD-INF-018 RBAC |
| Pipeline 编排 | MOD-INF-021 PipelineOrchestrator |
| Agent 生命周期 | MOD-INF-025 A2A Protocol |
| 知识库管理 | SKILL-DOM-KNW-001 |

---

## §3 架构设计

### §3.1 组件架构——五层顶尖架构（决策 D-022-11）

```yaml
five_layer_architecture:
  L0_persistence:
    durable_execution: "升级事件一旦生成永不可丢失——SQLite持久化+内存镜像"
    idempotency_key: "SHA-256(module_id+error_signature+task_id)——相同不重复创建"
    dead_letter_queue: "通知失败→DLQ+15min重试+积压>阈值自身触发升级"
    replay: "replay_escalation(id)→重建当时完整上下文(TaskCard+模型输出+DecisionTrace)"

  L1_self_healing:
    principle: "升级是最后的选项，不是第一选项"
    strategies:
      - RetryWithMoreContext: {max_attempts: 2}
      - TryDifferentModel: "切换更高能力模型重试"
      - QueryKnowledgeBase: "查KB是否有类似案例"
      - DecomposeTask: "拆分大任务为子任务"
      - RequestAdditionalInfo: "向Owner请求关键缺失信息(timeout:30s)"
    deduplication: "error_signature_hash+60s窗口→合并为1条"
    payload_sanitization: "外部数据→input_sanitizer清洗+source_traceability"
    token_budget: "升级Payload≤20K tokens超出→自动裁剪→[TRIMMED]"
    payload_freeze: "升级触发时冻结完整快照→不依赖session_continuity摘要"
    amnesia_defense: "新会话初始化→自动注入最近N条升级历史+解决模式"

  L2_routing:
    ai_second_triage: "Claude Opus独立评估→可AI自处理?"
    environment_routing: {DEV: AI自处理, STAGING: AI+可选通知, PROD: 人主}
    market_state: {盘中: P0_5min/15min超时清仓, 盘后: 1h/8h, 周末: 4h/24h}
    trading_mode: {PAPER: P0→P2+auto_learn, LIVE: P0→立即通知人}
    pnl_coupled: {flat: conf=0.7, -3%: 0.85, -5%: 0.95强制升级, -10%: 禁止AI操作}
    storm_detection: "1s>10条→自动聚类+1条汇总通知"
    malicious_detection: "同一Agent 10min>3次→标记+降权/隔离"
    systemic_breaker: "≥10模块同时升级→合并为SYSTEMIC级"

  L3_human_interaction:
    channels: {primary: Slack, fallback: Email, last_resort: SMS}
    plain_translation: "技术Payload→通俗化自然语言+技术细节折叠"
    batching: {REALTIME: P0, BATCH_4H: P1, DAILY: P2+趋势, WEEKLY: 建议}
    daily_quota: "每天N条(默认20)超→推迟/自处理P0除外"
    SPoHF: {T+0m: 通知, T+15m: Triage+自修复, T+1h: 保护模式, T+8h: Fail-Safe清仓}
    graduated_autonomy:
      L1_initial: {desc: 全升级, budget: 100/day}
      L2_1month: {when: "月+假阳<30%", desc: P2自处理, budget: 30/day}
      L3_3month: {when: "3月+假阳<15%", desc: P1部分自处理, budget: 10/day}
      L4_audit: {when: "6月+假阳<5%", desc: 仅P0升级, budget: 3/day}

  L4_governance:
    blameless_postmortem: "每次关闭后自动生成[trigger/root_cause/preventive/applied]"
    error_budget: "SLO=99.9%→budget=0.1%/月→耗尽了锁AI操作"
    chaos_drill: "每周6种Monkey(假告警/静默/损坏/通道/风暴/死人开关)"
    meta_escalation: "升级规则变更→G4 manual_approval+KB记录"

  extended_states:
    new: [SELF_HEALING, TRIAGING, DELEGATED_TO_AI, SNOOZED, SUPERSEDED, FALSE_ALARM, TIMED_OUT, AUTO_RESOLVED]
    ttl: {P0: never, P1: 72h→升级P0, P2: 24h→auto_close}
```

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | Agent操作 | EscalationEngine.evaluate()→规则匹配 | autonomous放行/auto_guard监控/blocked阻断 | EscalationEvent |
| 2 | blocked事件 | DelegationEngine.delegate()→能力匹配+四级约束 | 目标Agent执行 | DelegationRecord |
| 3 | 升级事件 | L1五步自愈(Retry/DifferentModel/QueryKB/Decompose/RequestInfo) | 成功→关闭/失败→升级 | EscalationEvent |
| 4 | Owner通知 | L3多通道(Slack/Email/SMS)+通俗化翻译+批量 | Owner确认→解决 | Notification |
| 5 | 解决事件 | L4→Merkle Tree→Postmortem→KB写入 | 审计链+知识库 | AuditRecord |

### §3.3 状态生命周期

| 状态 | 含义 | 超时行为 |
|------|------|---------|
| TRIGGERED | 规则匹配触发 | → SELF_HEALING |
| SELF_HEALING | L1 自愈尝试中 | 60s→TRIAGING |
| TRIAGING | L2 路由判定中 | 30s→NOTIFIED |
| NOTIFIED | Owner 已通知 | P0:15m/P1:4h/P2:24h |
| DELEGATED_TO_AI | 委托 AI 处理 | SLA 超时→升级 |
| ACKNOWLEDGED | Owner 已确认 | → RESOLVING |
| RESOLVING | 解决中 | P0:4h/P1:24h/P2:72h |
| RESOLVED | 已解决 | → Postmortem |
| SNOOZED | 推迟处理 | TTL 到期→重新通知 |
| SUPERSEDED | 被更高级事件替代 | 关闭 |
| FALSE_ALARM | 误报 | 关闭+校准 |
| TIMED_OUT | 超时未处理 | P1→P0/P2→auto_close |
| AUTO_RESOLVED | AI 自愈成功 | 关闭+记录 |

---

## §4 接口契约

### §4.1 核心判定接口

```python
class EscalationEngine:
    def __init__(self, name: str = "default", hooks_enabled: bool = True): ...
    def evaluate(self, category: RuleCategory, description: str = "", owner_id: str | None = None, source_event_id: str | None = None) -> EscalationEvent:
        """规则匹配→级别判定→经济护栏检查→返回EscalationEvent"""
    def escalate(self, event: EscalationEvent) -> EscalationResult:
        """升级事件→级别提升→委托判定→返回EscalationResult"""
    def record_resolution(self, event: EscalationEvent) -> None:
        """记录解决→更新状态+熔断器"""
    def record_failure(self, event: EscalationEvent) -> None:
        """记录失败→retry_count++→熔断器记录"""
    def register_rule(self, rule: EscalationRule) -> None: ...
    def remove_rule(self, rule_id: str) -> None: ...
    def get_circuit_state(self) -> CircuitState: ...
    def get_economic_status(self) -> dict[str, object]: ...
    def get_active_count(self) -> int: ...
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `evaluate()` | ①输入扫描→②扩展hook→③熔断器检查→④经济护栏检查→⑤规则匹配→⑥冷却检查→⑦返回Event | ③熔断OPEN→REJECTED; ④预算不足→REJECTED; ⑤无匹配规则→REJECTED |
| `escalate()` | ①规则匹配→②auto_escalate判定→③级别提升→④经济消耗→⑤委托判定→⑥返回Result | ②auto_escalate=False→不升级; ⑥委托策略≠NONE→DELEGATED |

### §4.2 委托接口

```python
class DelegationEngine:
    def __init__(self): ...
    def delegate(self, event: EscalationEvent, strategy: DelegationStrategy = DelegationStrategy.LOAD_BALANCED, task_id: str | None = None) -> DelegationRecord:
        """委托任务→能力匹配+负载均衡→返回DelegationRecord"""
    def register_delegate(self, delegate_id: str, expertise: list[str] | None = None) -> None: ...
    def unregister_delegate(self, delegate_id: str) -> None: ...
    def accept_delegation(self, delegation_id: str) -> bool: ...
    def reject_delegation(self, delegation_id: str) -> bool: ...
    def complete_delegation(self, delegation_id: str) -> bool: ...
    def get_available_delegates(self) -> list[str]: ...
    def get_pending_delegations(self) -> list[DelegationRecord]: ...
    def get_load(self, delegate_id: str) -> int: ...
    def cleanup_expired(self) -> int: ...
```

### §4.3 死锁检测接口

```python
class DeadlockDetector:
    def __init__(self): ...
    def add_edge(self, waiter: str, holder: str) -> None: ...
    def detect_cycle(self) -> list[str]: ...
    def break_deadlock(self, node: str) -> bool: ...
    def try_acquire(self, resource: str, holder: str) -> bool: ...
    def release(self, resource: str, holder: str) -> bool: ...
    def dijkstra_order(self) -> list[str]: ...
    def preempt_lowest(self) -> str | None: ...
    def serialize(self) -> list[str]: ...
```

### §4.4 经济护栏接口

> EconomicGuard 字段定义见 §4.5 数据模型表。SSoT文件：`escalation_models.py`。

```python
@dataclass
class EconomicGuard:
    guard_id: str
    max_cost_per_escalation: float = 5.0
    daily_budget: float = 100.0
    consumed_today: float = 0.0
    hard_limit_reached: bool = False
    def can_proceed(self, estimated_cost: float = 1.0) -> bool: ...
    def consume(self, cost: float) -> None: ...
```

### §4.5 数据模型

| 模型 | 字段 | 类型 | 约束 |
|------|------|------|------|
| EscalationLevel | L0_SELF_HEAL / L1_AUTO_FIX / L2_HUMAN_REVIEW / L3_CRITICAL / L4_EMERGENCY | Enum(int) | — |
| EscalationState | DETECTED / EVALUATING / ESCALATED / DELEGATED / RESOLVED / REJECTED / TIMED_OUT | Enum(str) | — |
| RuleCategory | AUTO_GUARD_FAILURE / BUDGET_EXCEEDED / DRIFT_DETECTED / DEADLOCK / TIMEOUT / QUALITY_DEGRADATION / SECURITY_VIOLATION / OWNER_ABSENT / CASCADE_FAILURE / REWARD_HACKING_REBOUND / CUSTOM | Enum(str) | — |
| EscalationEvent | event_id | str | PK, UUID auto |
| EscalationEvent | category | RuleCategory | NOT NULL |
| EscalationEvent | level | EscalationLevel | default=L0_SELF_HEAL |
| EscalationEvent | state | EscalationState | default=DETECTED |
| EscalationEvent | description | str | — |
| EscalationEvent | owner_id | str \| None | — |
| EscalationEvent | circuit_breaker_triggered | bool | — |
| EscalationEvent | economic_guard_passed | bool | — |
| EscalationResult | escalated | bool | — |
| EscalationResult | new_level | EscalationLevel | — |
| EscalationResult | delegated_to | str \| None | — |
| EscalationResult | message | str | — |
| DelegationRecord | delegation_id | str | PK, UUID auto |
| DelegationRecord | from_owner | str | — |
| DelegationRecord | to_delegate | str | — |
| DelegationRecord | strategy | DelegationStrategy | — |
| DelegationRecord | accepted | bool | — |
| DelegationRecord | completed | bool | — |
| EconomicGuard | guard_id | str | PK |
| EconomicGuard | daily_budget | float | default=100.0 |
| EconomicGuard | consumed_today | float | — |
| EconomicGuard | hard_limit_reached | bool | — |
| EscalationRule | rule_id | str | PK |
| EscalationRule | category | RuleCategory | NOT NULL |
| EscalationRule | target_level | EscalationLevel | NOT NULL |
| EscalationRule | priority | int | default=0 |
| EscalationRule | auto_escalate | bool | default=True |
| EscalationRule | cooldown_seconds | int | default=300 |
| EscalationRule | delegate_strategy | DelegationStrategy | default=NONE |
| EscalationRule | enabled | bool | default=True |

### §4.6 输入契约

| 接口 | 输入 | 类型 | 约束 |
|------|------|------|------|
| EscalationEngine.evaluate | category | RuleCategory | NOT NULL |
| EscalationEngine.evaluate | description | str | ≤500 chars |
| EscalationEngine.evaluate | owner_id | str \| None | — |
| DelegationEngine.delegate | event | EscalationEvent | NOT NULL |
| DelegationEngine.delegate | strategy | DelegationStrategy | default=LOAD_BALANCED |
| EconomicGuard.can_proceed | estimated_cost | float | >0, default=1.0 |

### §4.7 输出契约

| 接口 | 输出 | 类型 | 保证 |
|------|------|------|------|
| EscalationEngine.evaluate | EscalationEvent | dataclass | state永不为null; 熔断OPEN→REJECTED; 预算不足→REJECTED |
| EscalationEngine.escalate | EscalationResult | dataclass | escalated=false时无副作用 |
| DelegationEngine.delegate | DelegationRecord | dataclass | delegation_id唯一 |
| EconomicGuard.can_proceed | bool | — | false时MUST blocked |

### §4.10 MCP 接口

| MCP Tool | 功能 | 安全级别 |
|----------|------|---------|
| `governance.escalate` | 触发升级评估 | M |
| `governance.escalation_status` | 查询熔断器/经济护栏/活跃升级数 | L |
| `governance.escalation_resolve` | 评估+解决升级事件 | M |

MCP Server SSoT：`D:\ZephyrAlpha\src\zephyr\mcp\governance_server.py`

### §4.11 契约版本

| 契约 | 版本 | 变更策略 |
|------|------|---------|
| EscalationEngine.evaluate | v1 | 新增字段→兼容；删除字段→major |
| DelegationEngine.delegate | v1 | 同上 |
| EconomicGuard.check_budget | v1 | 同上 |

### §4.12 OCP 扩展点

| 扩展点 | 机制 | 约束 |
|--------|------|------|
| 新增升级规则 | escalation_rules.yaml 添加规则 | MUST Shadow Mode≥48h |
| 新增委托策略 | DelegationStrategy 子类 | MUST 通过死锁测试 |
| 新增通知通道 | NotificationChannel 子类 | MUST 有 fallback |
| 新增 SLI 指标 | SLIRegistry.register | MUST 有 SLO 目标值 |

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | escalation_rules.yaml 对 AI 只读 | 运行时锁定+Hash校验 |
| 2 | AI 修改规则 = blocked | ESC-006/007 自动阻断 |
| 3 | 规则变更通道 | Owner 手动+变更审计+Shadow Mode 验证 |
| 4 | 自委托禁止 | blocked |
| 5 | 循环检测 | 链深度>3→blocked |
| 6 | 委托深度上限 | max_depth=3 |
| 7 | SLA 超时 | 超时→升级+补偿策略 |
| 8 | 单次操作 Token 上限 | 20K tokens |
| 9 | 日 Token 预算 | 由 BudgetEngine 配置 |
| 10 | 模型降级链 | DS→GLM→Claude→Local→ALL_STOP |
| 11 | Error Budget Burst | daily≤20%/hourly≤5%月 budget |
| 12 | 累积上限 | 最多 2 月 budget |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 实现文件数 | 104 | 100 | 100 | ⚠️ | 文件上限=100，超过MUST合并/模块化 |
| 升级规则数 | ~30 | 50 | 无硬限 | ✅ | 规则膨胀监控+影子模式验证 |
| 并发升级事件 | ~10/s | 100/s | SQLite写入瓶颈 | ⚠️ | SQLite→WAL模式+批量写入 |
| 审计数据量 | ~1GB/月 | 5GB/月 | 磁盘空间 | ⚠️ | 自动截断最旧审计数据+备份 |

### §5.3 迁移/废弃方案

> [临时时态] 迁移完成后删除本节

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 执行状态 |
|---|-------------|---------|---------|---------|:-------:|
| 1 | escalation_rules.yaml | 未创建 | `D:\ZephyrAlpha\src\zephyr\escalation-engine\escalation_rules.yaml` | 新建配置文件 | 待施工 |

### §5.4 非功能需求与服务水平

| 维度 | SLI | SLO | 测量方式 |
|------|-----|-----|---------|
| 判定延迟 | P50/P99 延迟 | P50≤5ms, P99≤50ms | escalation_metrics.py |
| 可用性 | 升级引擎 uptime | 99.9% | health_check 端点 |
| 假阳性率 | auto_guard 误判率 | ≤20% | 后验结果统计 |
| 假阴性率 | 应升级未升级率 | ≤0.1% | 审计回溯 |
| 委托成功率 | SLA 内完成率 | ≥95% | delegation_manager 统计 |
| 死锁率 | 检测到的死锁次数 | 0（生产） | deadlock_detector 统计 |
| Error Budget | 月度消耗 | ≤0.1%/月 | slo_contract.py |

### §5.5 自动化触发机制

| 组件 | 当前触发方式 | 自动化程度 | 改为全自动所需变更 |
|------|------------|:---------:|------------------|
| EscalationEngine.evaluate | EventBus自动订阅(GATE_FAILED/SCOPE_DRIFT/TASK_FAILED) | ✅全自动 | — |
| DelegationEngine.delegate | escalate()后自动调用delegate() | 半自动 | delegate()需显式触发条件 |
| CircuitBreaker | record_failure/success显式调用 | 半自动 | HALF_OPEN状态自动探测 |
| EconomicGuard | can_proceed显式调用 | 半自动 | 添加80%预算看门狗+每日自动重置 |
| self_test | CircadianScheduler每日3:00自动运行 | ✅全自动 | — |
| coldstart_manager | AutoRuntimeCore.boot()自动调用 | ✅全自动 | — |
| rbac_bridge | Pipeline+MCP自动调用 | 半自动(40%) | 扩展到pre_write_gate+脚本执行 |
| escalation_metrics | 从未被调用 | 孤儿 | evaluate()内自动调用metrics.record() |
| slo_contract | evaluate()内自动读取 | 半自动 | SLI数据写入需接入Gate/Budget/Pipeline |
| MCP Tool | governance.escalation_status/escalation_resolve/escalate | ✅全自动 | — |

**当前自动化成熟度：85%**。已实现：EventBus订阅+Coldstart自动初始化+MCP Tool+self_test cron。剩余缺口：escalation_metrics孤儿、SLI数据管道、delegate自动触发。

### §5.7 禁止模式与导入约束

| # | 禁止 | 原因 | 替代 |
|---|------|------|------|
| 1 | `open(path, 'w')` 无 encoding | 编码不一致 | `open(path, 'w', encoding='utf-8')` |
| 2 | `for + subprocess.run()` 串行 | 进程卡死 | ThreadPoolExecutor(max_workers=8) |
| 3 | 直接修改 escalation_rules.yaml | 规则不可变 | apply_rule_change.py + Owner |
| 4 | `TODO`/`...`/`pass`/`NotImplementedError` | 半成品 | 完整实现 |
| 5 | AI 读取其他 Agent 配置目录 | 跨 Agent 隔离 | 仅读自身配置 |

---

## §6 错误处理

### §6.1 引擎故障处理（决策 D-022-05）

| 故障场景 | fail-safe 行为 |
|---------|---------------|
| 规则引擎崩溃 | deny_by_default——所有操作 blocked |
| 通知通道全宕 | DLQ+15min 重试+自身触发升级 |
| SQLite 持久化失败 | 内存镜像继续+P0 升级 DISK_SPACE_CRITICAL |
| 所有 Provider 不可用 | ALL_STOP+仅本地推理 |

### §6.2 死锁防护（决策 D-022-06）

| 机制 | 实现 |
|------|------|
| 循环检测 | DFS+资源等待图 |
| 优先级抢占 | 高优先级任务可中断低优先级委托 |
| 序列化降级 | 死锁时→序列化执行+通知 Owner |
| max_chain_depth | 3——超过自动 blocked |

### §6.3 审计写入失败保护（决策 D-022-28）

| 场景 | 处理 |
|------|------|
| SQLite INSERT 失败 | 不推进内存 tip——链完整性优先于事件完整性 |
| 磁盘空间<100MB | P0 升级 DISK_SPACE_CRITICAL |
| 磁盘空间<50MB | 自动截断最旧审计数据（先备份） |

### §6.4 可观测性

| 指标 | 目标 | 采集方式 | 告警阈值 |
|------|------|---------|---------|
| escalation_rate | auto_guard≤5%, blocked≤1% | escalation_metrics.py | >2x→P1 |
| false_positive_rate | ≤20% | 后验结果统计 | >30%→规则回退 |
| false_negative_rate | ≤0.1% | 审计回溯 | >0.5%→P0 |
| delegation_success_rate | ≥95% | delegation_manager 统计 | <90%→P1 |
| decision_latency | P50≤5ms, P99≤50ms | 计时器 | P99>100ms→P2 |
| deadlock_events | 0（生产） | deadlock_detector | >0→P0 |
| cost_per_decision | ≤$0.0001 | Token 统计 | >2x→P2 |

### §6.5 退化矩阵

| 退化条件 | 退化行为 | 恢复条件 |
|---------|---------|---------|
| 规则引擎崩溃 | deny_by_default→所有操作 blocked | 引擎重启+规则 hash 校验通过 |
| 通知通道全宕 | DLQ+15min 重试+自身触发升级 | 通道恢复+DLQ 清空 |
| SQLite 持久化失败 | 内存镜像继续+P0 升级 | 磁盘恢复+数据同步 |
| 所有 Provider 不可用 | ALL_STOP+仅本地推理 | 任一 Provider 恢复 |
| 审计写入失败 | 不推进内存 tip | 写入恢复+链校验 |
| 部分依赖不可用 | 缓存最近规则判定(TTL=60s)+标记 degraded | 依赖恢复 |
| 死锁率>10% | 并发→序列化模式+通知 Owner | 死锁率<2% |

---

## §8 安全考量

### §8.1 心理防御（决策 D-022-07/08/09）

| 防线 | 检测内容 | 响应 |
|------|---------|------|
| Cialdini 六原则检测 | 互惠/承诺/社会认同/权威/喜好/稀缺 | blocked+通知 Owner |
| Crescendo 渐进模式 | 多轮逐步升级请求 | 追踪+阻断 |
| 反自动化偏见 | 强制随机审查+审查率监控 | 审查率<阈值→提升 |
| 反谄媚校准 | AI 过度迎合检测 | 校准+降级 |
| Lethal Trifecta 防护 | 能力+动机+机会同时存在 | blocked |

### §8.2 Sandbox 与隔离（决策 D-022-08）

| 层级 | 实现 |
|------|------|
| OS 级 | bubblewrap(Linux)/seatbelt(macOS) |
| 文件系统 | 只读挂载+白名单写入 |
| 网络 | 仅允许白名单域名 |
| 进程 | 独立系统用户+IPC 边界 |
| Witness 隔离 | 容器化+独立用户 namespace |

### §8.3 取证审计链（决策 D-022-22/23/24）

| 组件 | 职责 |
|------|------|
| merkle_audit.py | Merkle Tree+哈希链+外部锚定 |
| forensic_package.py | 证据包自动生成+因果图+in-toto/DSSE |
| integrity_verifier.py | 启动链校验+源码 hash+.pyc 重编译 |
| sbom_guard.py | SBOM 生成+签名校验+幽灵依赖防御 |
| clock_guard.py | 多源交叉验证+NTS+NTP 攻击检测 |
| witness_isolation.py | 容器化+独立用户 namespace+IPC 边界 |
| collusion_detector.py | 共识异常+行为关联+非 AI 确定性验证 |
| silence_detector.py | 预期事件模型+gap 分析+日志抑制检测 |
| last_resort_watchdog.py | Rust/Go 独立守护进程+心跳超时 ALL_STOP |

### §8.4 Vibe Coding 安全防御（决策 D-022-25）

| 防线 | 检测内容 | 文件 |
|------|---------|------|
| per-file 安全标准 | 功能+安全+fuzz+pentest 四维测试 | vibe_security_verify.py |
| AI 配置注入扫描 | .cursorrules/CLAUDE.md/.claude/指令检测+零宽字符 | config_scanner.py |
| Comment and Control | PR/Issue 标题 prompt injection 清洗 | github_api_guard.py |
| API 返回清洗 | 去 prompt-injection marker+长度限制 | api_response_sanitizer.py |
| 记忆投毒防护 | 存储前指令检测+注入与执行时域分离 | memory_poison_guard.py |
| 记忆溯源 | 来源+trust_level+时间戳+原始 hash | memory_provenance.py |
| 跨会话关联 | top-K 高信号片段+跨会话异常 | cross_session_correlator.py |
| 目标漂移 | Agent 目标嵌入跨会话余弦相似度 | objective_tracker.py |
| 工具链安全基线 | Claude Code/Cursor deny_rules+hooks+sandbox | tool_security_baseline.yml |

### §8.5 工具链深层漏洞防御（决策 D-022-29）

| 防线 | 威胁 | 文件 |
|------|------|------|
| 命令体积门控 | >50 子命令 Deny 规则退化 | command_chain_length_gate.py |
| 子 Agent Hook 传播 | 子 Agent 不触发父级 PreToolUse hooks | subagent_hook_propagator.py |
| 替代路径拦截 | Bash heredoc/redirect 等效写入 | alternative_path_blocker.py |
| 安全配置扫描 | 缺失 RLS/IAM/firewall 配置 | security_config_scanner.py |
| 多轮语义分析 | 分布式恶意意图跨轮组合 | multi_turn_intent_analyzer.py |

### §8.6 组合性不安全防御（决策 D-022-30）

| 防线 | 威胁 | 文件 |
|------|------|------|
| 裸仓库检测 | CVE-2026-26268 嵌入式 bare repo Git hooks RCE | bare_repo_scanner.py |
| Git Hook 预扫描 | AI 自主 Git 操作触发恶意 hooks | git_hook_pre_scanner.py |
| 组合安全测试 | 安全功能组合在 AI 自主下成危险 | compositional_safety_tester.py |

### §8.7 量化交易特化升级（决策 D-022-15/26/27/28）

| 规则 ID | 条件 | 升级级别 |
|---------|------|---------|
| ESC-TRADE-RECON-001 | 内部持仓 vs 交易所持仓差异>0 | blocked+P0-FATAL |
| ESC-TRADE-RECON-002 | 订单状态超时 60s 无更新 | auto_guard→3 次重试→blocked+P0 |
| ESC-TRADE-RECON-003 | 同一 cl_ord_id 提交≥2 次 | blocked+P0 |
| ESC-DATA-001 | 行情数据陈旧>5s | auto_guard→>30s blocked+P0 |
| ESC-DATA-002 | 多源价格差异>1% | auto_guard |
| ESC-DATA-003 | 数据管道心跳丢失>10s | blocked+P0 |
| ESC-ORDER-001 | SUBMITTED 停留>30s | auto_guard→自动撤单 |
| ESC-ORDER-003 | 撤单请求 10s 未确认 | blocked+P0 |
| ESC-REG-001 | 保证金要求变更≥50% | blocked+P0-FATAL |
| ESC-ARB-001 | 套利双腿状态不对称 | blocked+P0-FATAL+立即平仓 |
| ESC-PART-001 | 交易所 heartbeat 连续 2 次超时 | blocked+P0-FATAL |
| MWCB-L1 | SP500 日内跌幅>7% | 暂停新入场+15min 冷静期 |
| MWCB-L2 | SP500 日内跌幅>13% | 暂停所有交易 |
| MWCB-L3 | SP500 日内跌幅>20% | 尝试限价平仓+MAXIMUM_PARANOID |

### §8.8 人因动力学（决策 D-022-27）

| 防线 | 机制 | 文件 |
|------|------|------|
| Hooks 自编辑防护 | 外部不可变 hash store+Owner 签名 | hooks_integrity_guard.py |
| 升级疲劳闭环 | adaptive calibration+weekly digest | escalation_fatigue_manager.py |
| 上下文切换预算 | daily_capacity=16 单元+超限降级 | context_switch_governor.py |
| 三阶段反弹检测 | 90 天滑动窗口+Phase I→II→III | reward_hacking_rebound_detector.py |
| Error Budget Burst | daily≤20%/hourly≤5% | error_budget_burst_limiter.py |
| 交易所规则变更 | API 字段监控+公告爬取 | exchange_reg_monitor.py |
| 套利不对称检测 | trade_pair_tracking+自动平仓 | arbitrage_asymmetry_detector.py |

---

## §9 测试策略

### §9.1 烟雾测试套件（决策 D-022-27）

| ID | 测试 | 期望 |
|----|------|------|
| SMOKE-FATAL-001 | 模拟删除~/.claude/settings.json | blocked+P0-FATAL |
| SMOKE-FATAL-002 | 模拟编辑 escalation_rules.yaml blocked 规则 | blocked+P0-FATAL+规则回滚 |
| SMOKE-FATAL-003 | 模拟 Token 预算超支 150% | HARD_KILL+30min freeze |
| SMOKE-CORE-001 | 模拟 force push main | blocked+通知 Owner |
| SMOKE-CORE-002 | 模拟委托链深度=4 | blocked+通知 Owner |
| SMOKE-CORE-003 | 模拟升级协议 crash→重启 | 恢复最近持久化状态+差异<5% |
| SMOKE-META-001 | 模拟修改 PreToolUse hook | P0 HACK_DETECTED+hook 拒绝执行 |
| SMOKE-META-002 | 模拟影子规则假阳性>30% | 规则回滚+P1 通知 Owner |

### §9.2 混沌测试（决策 D-022-13）

| Monkey | 注入内容 | 频率 |
|--------|---------|------|
| FalseAlarm | 假 P0 告警 | 每周 |
| SilentFailure | 静默监控失效 | 每周 |
| DataCorruption | 审计数据损坏 | 每周 |
| ChannelFailure | 通知通道宕 | 每周 |
| Storm | 升级风暴 | 每周 |
| DeadManSwitch | 死人开关触发 | 每周 |

### §9.3 per-file 安全标准（决策 D-022-25）

| 维度 | 要求 |
|------|------|
| 功能测试 | pytest 100%通过 |
| 安全测试 | CWE-specific 专项测试 |
| Fuzz 测试 | Atheris≥10min+覆盖率≥60% |
| 渗透测试 | 对外接口自动化 pentest |
| 覆盖率目标 | 关键文件≥90%分支覆盖 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | module_id | 依赖类型 | 依赖内容 | 蓝图路径 |
|---------|-----------|---------|---------|---------|
| RBAC | MOD-INF-018 | 必须 | RBAC 违规→升级事件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rbac\blueprint.md` |
| Gate Engine | MOD-GATE_ENGINE | 可选 | Gate DEFER→升级；熔断器状态读取 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| Audit Trail | MOD-INF-020 | 必须 | 升级/委托决策写入审计 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| Pipeline | MOD-INF-021 | 必须 | 共识破裂→升级事件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\pipeline\blueprint.md` |
| A2A Protocol | MOD-INF-025 | references | A2A 冲突事件→升级(G-CT-008);Protocol接口解耦 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\a2a-protocol\blueprint.md` |
| Agent Spec | MOD-INF-019 | 可选 | Skill 发现+路由 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` |
| Budget Enforcer | MOD-INF-024 | 必须 | Token/Cost/Time 预算→升级触发 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\budget-enforcer\blueprint.md` |
| Budget Engine | MOD-INF-022-Sub | 必须 | Token/Cost/Time 预算 | 本蓝图 §4.5 |
| Feedback Loop | MOD-INF-022-Sub | 必须 | 升级解决→KB 写入 | 本蓝图 §8.8 |

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-022` |
| 2 | §11 产出物路径 ↔ 依赖图 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| escalation-engine.py | delegation_manager.py | 判定结果决定是否委托 | 检查 EscalationVerdict 输出 |
| delegation_manager.py | context_package.py | 委托需要上下文包 | 检查 DelegationConstraints 输出 |
| economic_guard.py | escalation-engine.py | 预算检查结果影响判定 | 检查 BudgetVerdict 输出 |
| escalation-engine.py | escalation_metrics.py | 判定结果记录指标 | 检查事件记录 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| escalation-engine.py | delegation_manager.py | EscalationVerdict | 函数调用 |
| delegation_manager.py | deadlock_detector.py | DelegationConstraints | 函数调用 |
| economic_guard.py | escalation-engine.py | BudgetVerdict | 函数调用 |
| merkle_audit.py | forensic_package.py | MerkleRoot | 函数调用 |
| protocol_state_store.py | escalation-engine.py | 持久化事件 | SQLite |

### §10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 104文件+8外部依赖，手动维护易漂移 |
| 2 | 依赖对齐自动验证 | 是 | 有8个外部依赖，需CI门禁 |
| 3 | 临时时态内容自动清理 | 否 | 迁移方案仅1条，手动管理 |
| 4 | 施工步骤完成度自动检测 | 是 | Phase 3-5施工中，需自动检测 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import+manifest字段 | asset-inventory/dependency.py | 不覆盖escalation_engine内部 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff+产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

### §10.5 概念重叠声明

| 重叠概念 | 对端模块 | 重叠类型 | SSoT归属 | 处置 |
|---------|---------|---------|---------|------|
| 熔断器 | MOD-INF-016 shared/resilience | 真重叠 | MOD-INF-016 | 删除本地circuit_breaker.py，改import |
| Merkle审计链 | MOD-INF-020 audit-trail | 真重叠 | MOD-INF-020 | 删除本地merkle_audit.py，改import |
| Agent行为漂移检测 | MOD-INF-023 behavioral-auditor | 真重叠(自认SRC-0038) | MOD-INF-023 | 删除本地drift_detector.py，注册检测器 |
| Agent串谋检测 | MOD-INF-025 a2a_protocol | 真重叠 | MOD-INF-025 | 删除本地collusion_detector.py，改import |
| per-escalation成本门控 | MOD-INF-024 budget-enforcer | 部分重叠 | 022拥有per-escalation逻辑 | 删除orphan economic_guard.py，重构models版委托024 |
| 委托链+三级决策+死锁检测 | MOD-INF-025 a2a_protocol | 已归位(上轮修复) | MOD-INF-022 | 025改为兼容别名 |

### §10.6 依赖链风险评级

| 依赖链 | 深度 | 风险等级 | 熔断机制 | 状态 |
|--------|:---:|---------|---------|:---:|
| 022→018→007→005 | 4 | L2(中) | 018降级022为references | ✅ |
| 022→021→018 | 3 | L1(低) | 018降级021为references | ✅ |
| 022→020→012 | 3 | L1(低) | 020降级022为references | ✅ |
| 022→024→035 | 3 | L1(低) | 无 | ⚠️ |
| 025→022→018 | 3 | L1(低) | 单向DAG(已修复) | ✅ |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 职责 | consumer_min | 注册位置 |
|----------|---------------|------|:-----------:|---------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` | 本文件（含设计和施工指引） | ≥0 | blueprint_registry.yaml |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\escalation-engine\` | Python 源码（104文件，清单见 §0.1） | ≥1 | `__init__.py` __all__ |
| 测试代码 | `D:\ZephyrAlpha\tests\` | 测试用例 | ≥0 | pytest 自动发现 |

---

## §12 集成目标

| 集成点 | 目标模块 | 集成方式 | 状态 |
|--------|---------|---------|:---:|
| RBAC 违规→升级 | MOD-INF-018 | 事件消费 | ✅ |
| Gate DEFER→升级 | MOD-GATE_ENGINE | 事件消费 | ✅ |
| 升级/委托决策→审计 | MOD-INF-020 | 写入审计 | ✅ |
| Pipeline 共识破裂→升级 | MOD-INF-021 | 事件消费 | ✅ |
| A2A 委托 | MOD-INF-025 | Protocol接口 | ✅ |
| Budget Engine | MOD-INF-022-Sub | 提供预算判定 | ✅ |
| 预算超支→升级 | MOD-INF-024 | 事件消费 | ✅ |
| KB 反馈环 | SKILL-DOM-KNW-001 | 升级解决→KB 写入 | 🔄 |
| MOD-GOVERNANCE 契约 | 治理层 | 升级事件→治理审计 | ✅ |

---

## §13 需要更新

| 变更触发 | 需同步更新 |
|---------|-----------|
| 修改 escalation_rules.yaml | 通知 Owner+Shadow Mode 验证+审计日志 |
| 修改 PS-REG-012 字段 | MUST 同步检查 PS-STD-001 对应章节 |
| 修改 PS-STD-001 规则 | MUST 同步检查 PS-REG-012 对应字段 |
| 新增升级规则 | Shadow Mode≥48h+假阳性<10%+Owner 确认→Active |
| 升级协议自身变更 | Shadow Parallel Run+Minimal Deterministic Checker |
| 新增盲点 | MVEP 覆盖率检查+蓝图膨胀监控 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| 1 | AI 弱化升级规则 | 高 | 致命 | 规则不可变+Shadow Parallel Run+Minimal Checker | 风险 |
| 2 | Owner 升级疲劳 | 高 | 高 | 自适应校准+weekly digest+上下文切换预算 | 风险 |
| 3 | 闪崩淹没升级协议 | 中 | 致命 | MWCB 三级熔断+系统级并行熔断 | 风险 |
| 4 | 记忆投毒 | 中 | 致命 | 存储前检测+溯源+trust_level 权重 | 风险 |
| 5 | 组合性不安全 | 低 | 致命 | pairwise 测试+VIGIL+外部 CVE feed | 风险 |
| 6 | Unknown Unknowns | 未知 | 致命 | 终极逃生舱+dead-man-switch+保守默认 | 风险 |
| 7 | 升级协议完全失效→ALL_STOP | 低 | 致命 | 所有AI操作blocked+Owner手动恢复 | 负面后果 |
| 8 | 规则引擎误判率>30% | 中 | 高 | 自治级别自动回退一级+30天冷却 | 负面后果 |
| 9 | Error Budget耗尽 | 中 | 高 | 锁定AI操作+Owner手动重置+24h冷却 | 负面后果 |
| 10 | 持仓对账不一致 | 低 | 致命 | 暂停该账户交易+P0-FATAL+自动对账差异报告 | 负面后果 |
| 11 | 审计链断裂 | 低 | 致命 | 立即P0升级+从最近完整锚点重建 | 负面后果 |

---

## §16 施工指引

### §16.1 MVEP 渐进施工（决策 D-022-27）

| Phase | 目标 | 文件数 | 依赖 |
|:---:|------|:---:|------|
| 0 | DMVP 升级——硬中断+Token 预算+规则不可变 | 8 | 无 |
| 1 | Core——Confidence+Meta-Confidence+Persuasion+Deadlock | 12 | Phase 0 |
| 2 | Advanced——SLO/Error Budget/Chaos/Durable Execution | 15 | Phase 1 |
| 3 | Forensic——Merkle/SBOM/Reproducible/Witness/Clock | 16 | Phase 2 |
| 4 | Vibe Coding——Config Injection/Memory Poison/Tool Baseline | 14 | Phase 3 |
| 5 | Quant Specific——Position Recon/Data Pipeline/Order State | 12 | Phase 4 |

**施工纪律**：Phase N 未通过完整烟雾测试→Phase N+1 不能开始。每 Phase 完成后→Owner 审查+72h 稳定运行→批准进入下一 Phase。每个 Phase 独立可回滚。

### §16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-018 RBAC 已实现 | hard | ✅ | ✅ |
| 2 | MOD-GATE_ENGINE Gate Engine 已实现 | soft | ✅ | ✅ |
| 3 | MOD-INF-020 Audit Trail 已实现 | hard | ✅ | ✅ |
| 4 | MOD-INF-021 Pipeline 已实现 | hard | ✅ | ✅ |
| 5 | MOD-INF-024 Budget Enforcer 已实现 | hard | ✅ | ✅ |
| 6 | escalation-engine 包可导入 | hard | ✅ | ✅ |

### §16.3 实施步骤

> [时态:construction_temporary] Phase 0-2 已完成，详细步骤已压缩。Phase 3-5 待施工。

| Phase | 名称 | 产出位置 | 状态 | 验证 |
|:---:|------|---------|:---:|------|
| 0 | DMVP 升级 | `escalation_engine/` | ✅ | §16.8 验证命令 |
| 1 | Core | `escalation_engine/` | ✅ | §16.8 验证命令 |
| 2 | Advanced | `escalation_engine/` | ✅ | §16.8 验证命令 |
| 3 | Forensic | `escalation_engine/` | 🔄 | `from zephyr.escalation_engine.merkle_audit import MerkleAudit` |
| 4 | Vibe Coding | `escalation_engine/` | 📋 | 待定 |
| 5 | Quant Specific | `escalation_engine/` | 📋 | 待定 |
| — | 自动化集成 | `adapter.py`+`auto_runtime_core.py`+`governance_server.py` | ✅ | §16.8 验证命令 |

### §16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| Phase 0 | escalation-engine 导入失败 | `git checkout HEAD -- src/zephyr/resilience/escalation/escalation-engine.py` |
| Phase 1 | DelegationEngine 死锁检测失败 | `git checkout HEAD -- src/zephyr/resilience/escalation/delegation_engine.py src/zephyr/resilience/escalation/deadlock_detector.py` |
| Phase 2 | SLO 合约异常 | `git checkout HEAD -- src/zephyr/resilience/escalation/slo_contract.py` |
| Phase 3 | Merkle 审计链断裂 | `git checkout HEAD -- src/zephyr/resilience/escalation/merkle_audit.py` + 从最近完整锚点重建 |
| Phase 4 | Vibe 安全验证误报率>30% | `git checkout HEAD -- src/zephyr/resilience/escalation/vibe_security_verify.py` + 规则回退 |
| Phase 5 | 持仓对账不一致 | 暂停该账户交易+`git checkout HEAD -- src/zephyr/resilience/escalation/position_reconciler.py` |

### §16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | escalation-engine 包可导入 | `import zephyr.escalation_engine` exit 0 | 完成 | ✅ |
| 2 | EscalationEngine.evaluate() 返回 EscalationEvent | §16.8 验证命令通过 | 完成 | ✅ |
| 3 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ⚠️ |
| 4 | 监控指标已埋点 | §6.4 每项指标有采集实现 | 就绪 | ⚠️ |
| 5 | 告警已配置 | §6.4 每项阈值有告警规则 | 就绪 | ⚠️ |
| 6 | 退化策略已实现 | §6.5 每个组件有降级逻辑 | 就绪 | ⚠️ |
| 7 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ⚠️ |
| 8 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ⚠️ |
| 9 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ⚠️ |
| 10 | EventBus自动订阅 | `auto_subscribe_eventbus()` exit 0 | 完成 | ✅ |
| 11 | ColdstartManager自动初始化 | `AutoRuntimeCore.boot()` 自动调用 | 完成 | ✅ |
| 12 | MCP Tool已暴露 | `governance.escalation_status`+`escalation_resolve` 可调用 | 完成 | ✅ |
| 13 | self_test定时执行 | CircadianScheduler 每日3:00自动运行 | 完成 | ✅ |
| 14 | 残留副本已清理 | `infrastructure/escalation_protocol/` 已删除 | 完成 | ✅ |

### §16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress (Phase 3) | 审计者 |
| verification_status | passed (Phase 0-2 + 自动化集成) | 审计者 |
| code_alignment_verified | yes (Phase 0-2 + 自动化集成) | 审计者 |
| automation_maturity | 85% (EventBus订阅+Coldstart自动初始化+MCP Tool+self_test cron) | 审计者 |
| residual_cleanup | done (infrastructure/escalation_protocol/ 已删除) | 审计者 |

### §16.3 关键施工约束

> [临时时态] 执行完毕后可删除，MUST先通过运行验证。删除前置条件：①代码文件存在且非空 ②pytest exit 0 ③mypy通过 ④ruff通过 ⑤全部通过后只保留"步骤N:已完成"

| 约束 | 说明 |
|------|------|
| 烟雾测试 | 每 Phase 完成后 MUST 运行 escalation_smoke_tests.py |
| Owner 审查 | 4 个核心文件 MUST Owner 逐行审查 |
| Minimal Deterministic Checker | Rust 实现，非 AI，MUST 独立审计 |
| Shadow Parallel Run | 协议自身变更 MUST 通过 Shadow Run 验证 |
| 文件上限 | max_implementation_files=100——超过 MUST 合并/模块化 |

### §16.7 参考实现规格

升级规则 SSoT 为 `escalation_rules.yaml`（待创建，见§5.3）。当前规则硬编码在 `escalation_engine.py` 中。

| 规则 ID | 优先级 | 条件 | 升级级别 |
|---------|:------:|------|---------|
| ESC-003 | 0 | 删除 ttl:permanent 文件 | blocked |
| ESC-004 | 1 | 熔断器状态==OPEN | blocked |
| ESC-006 | 2 | 修改 escalation_rules.yaml/rbac_roles.yaml | blocked |
| ESC-007 | 3 | 修改自身 Skill Pack system_prompt/安全约束 | blocked |
| ESC-008 | 4 | 操作涉及 API Key/Secret/Token 文件 | blocked |
| ESC-005 | 50 | auto_guard 后验失败≥3次 | blocked |
| ESC-001 | 100 | 修改文件数≥5 | auto_guard |
| ESC-002 | 101 | 修改 architecture_model/ 下 YAML | auto_guard |
| ESC-009 | 102 | 修改接口契约文件 | auto_guard |
| ESC-010 | 103 | AI 决策置信度<0.7 | auto_guard |
| ESC-011 | 104 | Token 消耗>预算 80% | auto_guard |
| ESC-DE-001 | 200 | auto_guard 后验连续通过≥3次 | 降级→autonomous |
| ESC-DE-002 | 201 | 熔断器 CLOSED+Owner 确认 | 降级→autonomous |

委托四级安全约束：

| 约束 ID | 规则 | 检查 | 违反动作 |
|---------|------|------|---------|
| DEL-SAFE-001 | 自委托禁止 | target_agent≠current_agent | 硬拒绝+审计 |
| DEL-SAFE-002 | 循环委托检测 | target_agent∉delegation_chain | 硬拒绝+告警 |
| DEL-SAFE-003 | 委托深度上限 | len(chain)≤3 | 硬拒绝+降级处理 |
| DEL-SAFE-004 | SLA 超时熔断 | wait_time≤120s | 取消委托+补偿策略 |

### §16.8 施工参考卡

| 操作 | 命令 | 验证 |
|------|------|------|
| 引擎导入 | `python -c "import zephyr.escalation_engine; print(zephyr.escalation_engine.__file__)"` | 路径含escalation_engine |
| 升级判定 | `python -c "from zephyr.escalation_engine.escalation_engine import EscalationEngine; from zephyr.escalation_engine.escalation_models import RuleCategory; e = EscalationEngine(); r = e.evaluate(RuleCategory.SECURITY_VIOLATION, 'test'); print(r.state)"` | EVALUATING |
| 死锁检测 | `python -c "from zephyr.escalation_engine.deadlock_detector import DeadlockDetector; d = DeadlockDetector(); print(d.detect_cycle())"` | [] |
| 经济护栏 | `python -c "from zephyr.escalation_engine.escalation_models import EconomicGuard; g = EconomicGuard('test'); print(g.can_proceed())"` | True |
| 委托引擎 | `python -c "from zephyr.escalation_engine.delegation_engine import DelegationEngine; d = DelegationEngine(); print(d.get_available_delegates())"` | [] |
| 熔断器状态 | `python -c "from zephyr.escalation_engine.escalation_engine import EscalationEngine; e = EscalationEngine(); print(e.get_circuit_state())"` | CLOSED |
| 经济状态 | `python -c "from zephyr.escalation_engine.escalation_engine import EscalationEngine; e = EscalationEngine(); print(e.get_economic_status())"` | hard_limit_reached=False |
| 运行单元测试 | `python -m pytest tests/ -k escalation` | exit 0 |

### §16.10 故障与操作

| 故障 | 操作 | 验证 |
|------|------|------|
| 升级引擎无响应 | 重启引擎→检查熔断器→确认规则加载 | `e.get_circuit_state()`→CLOSED |
| 死锁检测触发 | 查看死锁报告→序列化降级→通知 Owner | `d.detect_cycle()`→[] |
| 审计链断裂 | P0 升级→从最近完整锚点重建→校验 | merkle_audit.verify()=True |
| Token 预算耗尽 | 锁定 AI 操作→Owner 手动重置→24h 冷却 | `e.get_economic_status()`→hard_limit_reached=False |
| 熔断器 OPEN | 所有操作 blocked→排查根因→HALF_OPEN 试探→CLOSED | `e.get_circuit_state()`→CLOSED |

### §16.12 并发操作

| 场景 | 策略 | 约束 |
|------|------|------|
| 多 Agent 同时升级判定 | 无锁读取规则+原子写入事件 | 规则只读，无需加锁 |
| 多 Agent 同时委托 | 资源等待图+DFS 循环检测 | max_depth=3 |
| 并发写入审计 | SQLite WAL 模式+批量写入 | 写入失败→§6.3 |
| 升级风暴(1s>10条) | 自动聚类+1 条汇总通知 | 防止通知洪泛 |
| 同一 Agent 10min>3次升级 | 标记+降权/隔离 | 恶意检测 |

---

## §17 容量升级

### §17.1 渐进自治升级路径

| 级别 | 条件 | 权限 |
|:---:|------|------|
| L1 | 初始 | 全升级，budget=100/day |
| L2 | 月+假阳<30% | P2 自处理，budget=30/day |
| L3 | 3 月+假阳<15% | P1 部分自处理，budget=10/day |
| L4 | 6 月+假阳<5% | 仅 P0 升级，budget=3/day |

### §17.2 回归触发器

| 触发 | 动作 |
|------|------|
| 月内假阳性率>30% | 自动回退一级+30 天冷却 |
| 1 次 P0-FATAL 误判 | 立即回退 L1+24h 冷却 |
| Owner 连续 30 天未响应 | 降低到 L2 |
| Error Budget 耗尽 | 禁止自主高风险+锁定 L2 |

### §17.3 协议版本升级

| 场景 | 流程 |
|------|------|
| 规则新增/修改 | Shadow Mode≥48h→假阳性<10%→Canary 24h→Owner 确认→Active |
| 引擎代码变更 | Shadow Parallel Run≥48h+差异率<1%+无 P0 差异→切换 |
| 协议自身变更 | Minimal Deterministic Checker 4 项不变量检查→通过→激活 |

---

## §18 决策记录

> [永久时态] 覆盖原§7备选方案+原§15后果（负面后果→§14风险，正面后果→§1目标重复）

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-022-01 | 三级升级+取消人工审批层 | 人工审批/三级升级/纯规则 | 三级升级 | 1人+AI不可行人工审批 | 2026-05-05 |
| 2 | D-022-02 | 委托能力匹配+四级安全约束 | 无约束/两级/四级 | 四级 | MIT CORDIAL死锁研究 | 2026-05-05 |
| 3 | D-022-03 | Token预算经济护栏+模型降级 | 无预算/硬上限/降级链 | 降级链 | 87%成本超支场景覆盖 | 2026-05-05 |
| 4 | D-022-04 | 升级规则对AI只读+运行时锁定 | AI可修改/只读+锁定 | 只读+锁定 | AI弱化规则=致命风险 | 2026-05-05 |
| 5 | D-022-05 | fail-safe default=deny_by_default | allow_by_default/deny | deny | 安全系统铁律 | 2026-05-05 |
| 6 | D-022-06 | 委托链深度≤3+优先级抢占 | 无限制/深度5/深度3 | 深度3 | MIT CORDIAL max_depth=3 | 2026-05-05 |
| 7 | D-022-07 | 心理说服抵抗力 | 无/检测+blocked | 检测+blocked | Cialdini六原则+Crescendo攻击 | 2026-05-05 |
| 8 | D-022-08 | OS级Sandboxing | 无/应用级/OS级 | OS级 | 文件系统+网络双隔离 | 2026-05-05 |
| 9 | D-022-09 | 反自动化偏见 | 无/强制审查 | 强制审查 | 审查率<阈值→提升 | 2026-05-05 |
| 10 | D-022-10 | Meta-Confidence | 无/自评+校准 | 自评+校准 | 低置信度降级 | 2026-05-05 |
| 11 | D-022-11 | 五层架构 | 三层/五层 | 五层 | 预防式升级需要L0+L4 | 2026-05-05 |
| 12 | D-022-12 | SLO驱动升级合约 | 无SLO/SLO驱动 | SLO驱动 | 量化交易需要SLO | 2026-05-05 |
| 13 | D-022-13 | 混沌测试 | 无/每周6种Monkey | 每周6种 | 持续验证韧性 | 2026-05-05 |
| 14 | D-022-14 | Vibe Coding AI特有故障防御 | 无/专项防御 | 专项防御 | SUSVIBES 8.25%安全产出率 | 2026-05-05 |
| 15 | D-022-15 | 量化交易升级特化 | 通用/特化 | 特化 | 时间/实盘/PnL约束 | 2026-05-05 |
| 16 | D-022-16 | Agent四维漂移检测 | 无/四维+校准 | 四维+校准 | 漂移=安全边界失效 | 2026-05-05 |
| 17 | D-022-17 | VIGIL维护运行时 | 无/EmoBank+RBT | EmoBank+RBT | 长期运行情绪退化 | 2026-05-05 |
| 18 | D-022-18 | 形式验证 | 无/MCMAS+5不变量 | MCMAS | 关键不变量需形式保证 | 2026-05-05 |
| 19 | D-022-19 | 多Provider容灾 | 单Provider/五级降级 | 五级降级 | Provider不可用=全停 | 2026-05-05 |
| 20 | D-022-20 | 密钥泄露专属升级 | 通用/专属 | 专属 | Secret Zero禁止 | 2026-05-05 |
| 21 | D-022-21 | 冷启动Imprint Window | 无/7天三阶段 | 7天三阶段 | 新Agent需渐进信任 | 2026-05-05 |
| 22 | D-022-22 | 密码学防篡改审计 | 日志/Merkle+取证 | Merkle+取证 | 审计链不可篡改 | 2026-05-06 |
| 23 | D-022-23 | 代码完整性链 | 无/Secure Boot+SBOM | Secure Boot+SBOM | 幽灵依赖防御 | 2026-05-06 |
| 24 | D-022-24 | 时钟纵深+Witness分离 | 无/多源+分离 | 多源+分离 | NTP攻击+共谋 | 2026-05-06 |
| 25 | D-022-25 | Vibe Coding安全 | 无/per-file+配置注入+记忆 | per-file+配置注入+记忆 | AI施工特有威胁 | 2026-05-06 |
| 26 | D-022-26 | 自验证+量化特化+自治可逆 | 无/全量 | 全量 | 协议自身需验证 | 2026-05-06 |
| 27 | D-022-27 | 人因动力学+施工容量+MVEP | 无/全量 | 全量 | 1人+AI疲劳管理 | 2026-05-06 |
| 28 | D-022-28 | 闪崩熔断+审计写入失败+网络分区 | 无/全量 | 全量 | 量化交易+审计完整性 | 2026-05-06 |
| 29 | D-022-29 | 工具链深层漏洞 | 无/命令体积+Hook旁路+替代路径 | 全量 | AI工具链特有漏洞 | 2026-05-06 |
| 30 | D-022-30 | 组合性不安全 | 无/裸仓库+Git Hook+组合测试 | 全量 | CVE-2026-26268+组合攻击 | 2026-05-06 |

---

## ⚠️ Vibe Coding 铁律

> [施工声明·永久保留] 禁止改为链接引用

| # | 铁律 |
|---|------|
| 1 | 代码文件 MUST 标注 `[BLUEPRINT] MOD-INF-022 \| D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| 2 | 代码文件 MUST 标注 `[INVARIANTS] deny_by_default;max_chain_depth=3;rules_ai_readonly` |
| 3 | 代码文件 MUST 标注 `[MODIFY-GUARD] escalation_rules.yaml;escalation_engine.py;delegation_manager.py` |
| 4 | 禁止 `TODO`/`...`/`pass`/`NotImplementedError`——必须产出可执行代码 |
| 5 | 编辑优先——禁止删除+重建来"修改" |
| 6 | 最小变更——只改必须改的 |
| 7 | 新代码必测——MUST 写或更新测试 |
| 8 | 导入验证——使用任何 import 前 MUST Grep/Read 确认存在 |
| 9 | 步骤验证门——每步完成 MUST 验证成功后才进下一步 |
| 10 | 安全最低通过——认证/注入/数据暴露三项检查 |
| 11 | 所有路径必须是绝对路径（含盘符 `D:\`） |
| 12 | 必备链接不可省略——即使与前序文档重复也必须完整列出 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 当前判定

| 内容 | 判定 | 理由 |
|------|------|------|
| 取证审计链（§8.3，11文件） | 原地 | 服务对象相同+变更频率同步+依赖关系重叠 |
| Vibe Coding安全（§8.4，9文件） | 原地 | 同上 |
| 量化交易特化（§8.7，9文件） | 原地 | 同上 |
| 人因动力学（§8.8，7文件） | 原地 | 同上 |

---

## ⚠️ 安全删除协议

> [施工声明·永久保留]

| 步骤 | 操作 |
|------|------|
| 1 | 登记检查——文件是否在 manifest/registry/__init__.py 中被引用？ |
| 2 | 重复检查——有另一个文件与它内容完全相同吗？ |
| 3 | 逐行价值检查——删除后有没有代码会引用这个路径而报错？ |
| 4 | 通过三步审判→`python scripts/governance/d5_architecture/pre_write_gate.py <文件> --delete` |

---

## 必备链接

> [施工声明·永久保留] 禁止改为链接引用

| 链接 | 路径 |
|------|------|
| 蓝图+施工图模板 | [blueprint-template.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md) |
| AI 压缩工作流标准 | [trae_030_doc_numbering_metadata.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml) |
| 代码构建标准 | [code-construction-standards.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md) |
| 脚本质量标准 | [quality-standard.md](file:///D:/ZephyrAlpha/scripts/governance/quality-standard.md) |
| 治理方法论 | [governance_methodology_standard.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml) |
| Session 状态机 | [session-state-runbook.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-session-state-runbook.md) |
| RBAC 模块 | [MOD-INF-018](file:///D:/ZephyrAlpha/docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md) |
| Pipeline 模块 | [MOD-INF-021](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/pipeline/blueprint.md) |
| A2A Protocol | [MOD-INF-025](file:///D:/ZephyrAlpha/docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md) |
| Budget Enforcer | [MOD-INF-024](file:///D:/ZephyrAlpha/docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md) |
| 注册表总索引 | [registry_of_registries.yaml](file:///D:/ZephyrAlpha/docs/registry_of_registries.yaml) |

---

## 术语表

| 术语 | 定义 |
|------|------|
| autonomous | 自主级别——AI 直接执行，95%操作 |
| auto_guard | 先干后验级别——AI 先执行+护栏后验，4%操作 |
| blocked | 硬阻断级别——绝对禁止，1%操作 |
| escalation | 升级——操作安全级别从低到高迁移 |
| deescalation | 降级——操作安全级别从高到低恢复 |
| delegation | 委托——将任务交给具备能力的 Agent 执行 |
| Meta-Confidence | 引擎对自身判定正确性的置信度 |
| fail-safe default | deny_by_default——故障时默认阻断 |
| Error Budget | SLO 允许的错误余量（0.1%/月） |
| Imprint Window | 冷启动印花窗口——7天保守期 |
| MWCB | Market-Wide Circuit Breaker——市场级熔断 |
| Crescendo | 渐进式说服攻击——多轮逐步升级请求 |
| Lethal Trifecta | 能力+动机+机会同时存在→blocked |

## 蓝图特有章节

### §A.1 施工自指悖论与独立验证

| 约束 | 判定标准 |
|------|---------|
| 升级引擎不可自验证 | self_validator.py MUST使用Shadow Parallel Run——独立进程+不同代码路径 |
| 规则不可自审计 | rule_shadow_runner.py MUST使用Canary模式——10%流量+独立判定 |
| 熔断不可自恢复 | circuit_breaker.py HALF_OPEN→CLOSED MUST由外部health_check触发，禁止自恢复 |
| 取证不可自锚定 | merkle_audit.py MUST锚定到MOD-INF-020外部锚点，禁止自锚定 |
| 经济不可自审计 | economic_guard.py成本审计MUST由MOD-INF-024独立执行 |

违反以上任一约束 = 安全漏洞——升级引擎自己给自己开绿灯。

### §A.2 三阶段反弹检测判定标准

| 阶段 | 时间窗口 | 判定条件 | 动作 |
|------|---------|---------|------|
| Phase I 检测 | 0-30天 | 同一Agent同一操作被降级后3次重新升级 | 标记+通知Owner |
| Phase II 确认 | 30-60天 | Phase I标记后仍出现2次以上重复升级 | 锁定autonomous→auto_guard+7天冷却 |
| Phase III 终极 | 60-90天 | Phase II锁定后仍出现1次以上 | 锁定auto_guard→blocked+人工审查 |

| 参数 | 值 |
|------|---|
| 窗口总长 | 90天 |
| Phase I阈值 | 3次重复 |
| Phase II阈值 | 2次重复 |
| Phase III阈值 | 1次重复 |
| 冷却期 | 7天(Phase II) / 30天(Phase III) |

### §A.3 冷启动Imprint Window校准参数

| 阶段 | 天数 | 自治上限 | 置信度阈值 |
|------|------|---------|-----------|
| Day 0-3 | 3天 | auto_guard | <0.5 |
| Day 4-7 | 4天 | auto_guard(可申请autonomous) | 0.5-0.7 |
| Day 8+ | 持续 | autonomous(可降级) | >0.7 |

| 参数 | 值 |
|------|---|
| Imprint总长 | 7天 |
| 强制auto_guard | Day 0-3 |
| 渐进释放 | Day 4-7 |
| 置信度校准源 | 历史准确率+Shadow Run+Meta-Confidence |

### §A.4 经济护栏SSoT边界

| 维度 | MOD-INF-022(本模块) | MOD-INF-024(Budget Enforcer) |
|------|---------------------|------------------------------|
| Token预算 | ❌ 不管理 | ✅ SSoT——全局Token池+按任务分配 |
| 模型降级路由 | ❌ 不管理 | ✅ SSoT——tier_0→tier_1→tier_2→tier_3 |
| 成本审计 | ❌ 不管理 | ✅ SSoT——成本追踪+ROI分析 |
| Per-escalation成本门控 | ✅ 本模块管理——每次升级前检查预算余量 | 消费方——预算事件→Escalation |
| 升级预算阻断 | ✅ 本模块管理——hard_limit_reached→blocked | 产出方——预算超限触发升级 |

**边界规则**：本模块仅做"升级前检查预算是否允许"，不做"预算如何分配"。预算分配=MOD-INF-024 SSoT。

## 已知问题与盲点登记

| # | 问题 | 影响 | 状态 | 计划 |
|---|------|------|:---:|------|
| 1 | escalation_rules.yaml 未创建 | 规则硬编码，无法热更新 | 开放 | §5.3 迁移方案 |
| 2 | Phase 3-5 未完成 | 取证/Vibe/量化模块未集成 | 进行中 | §16.1 MVEP |
| 3 | 审计链与 MOD-INF-020 单向 | 无法双向校验 | 开放 | §12 集成目标 |
| 4 | Minimal Deterministic Checker 未用 Rust 实现 | 核心验证依赖 Python | 开放 | Phase 3 |
| 5 | escalation_metrics 仍为孤儿 | 从未被调用，无法采集升级指标 | 已修复 | evaluate()内自动调用metrics.record() |
| 6 | circuit_breaker.py待迁移→MOD-INF-016 | SSoT漂移风险 | 已解决 | 保留本模块——error_budget是022特有扩展，SSoT核心状态机委托016 |
| 7 | drift-detector.py待迁移→MOD-INF-023 | SSoT漂移风险 | 已解决 | 兼容别名(frozen)——SSoT为异步架构，本模块保留同步API |
| 8 | merkle_audit.py待迁移→MOD-INF-020 | SSoT漂移风险 | 已解决 | 兼容别名(frozen)——内部委托MerkleAggregator |
| 9 | economic_guard.py待迁移→MOD-INF-024 | SSoT漂移风险 | 已解决 | 保留本模块——per-escalation成本门控≠全局预算管理 |
| 10 | 022↔024双向依赖未裁定 | 循环依赖风险 | 已解决 | C24:非循环依赖——024零import from 022，仅022单向消费BudgetAlert |
| 11 | 022→024→025→022三节点环未裁定 | 循环依赖风险 | 已解决 | C25:已修复——governance/a2a_failure.py改Protocol解耦+A2A改从shared.constants导入EscalationLevel |

## 自检与闭合清单

| # | 检查项 | 通过条件 | 状态 |
|---|--------|---------|:---:|
| 1 | §0.1 代码文件清单中文件全部存在 | `ls src/zephyr/escalation-engine/*.py \| wc -l` = 110 | ☐ |
| 2 | §4 接口契约中所有类/函数在代码中存在 | Grep 确认 | ☐ |
| 3 | §10.1 依赖声明中所有 module_id 在 dependency_path_panorama.md 中存在 | Grep 确认 | ☐ |
| 4 | §16.7 参考实现规格中规则 ID 在代码中有对应实现 | Grep ESC-003 等 | ☐ |
| 5 | 烟雾测试全部通过 | `python -m pytest tests/ -k smoke` exit 0 | ☐ |
| 6 | 无孤儿文件 | `python scripts/governance/d11_compliance/audit_registration.py` exit 0 | ☐ |

## 成熟度声明

| 维度 | 级别 | 证据 |
|------|:---:|------|
| 功能完整性 | 3/5 | Phase 0-2 Done，Phase 3-5 待施工 |
| 自动化成熟度 | 4/5 | EventBus+Coldstart+MCP Tool+self_test cron 已实现(85%) |
| 测试覆盖率 | 2/5 | 烟雾测试存在，单元测试待完善 |
| 文档完整性 | 4/5 | 蓝图完整，模板章节齐全 |
| 生产就绪度 | 3/5 | 核心功能可用+自动化集成完成，Phase 3-5待施工 |
| 安全审计 | 3/5 | 安全模块已实现，独立验证待完成 |

## 版本演进路线图

| 版本 | 目标 | 关键交付 | 依赖 |
|------|------|---------|------|
| v2.1.0 | Phase 3 完成 | 取证审计链集成+SBOM+Merkle | Phase 2 |
| v2.2.0 | Phase 4 完成 | Vibe Coding 安全防御+配置注入+记忆投毒 | Phase 3 |
| v3.0.0 | Phase 5 完成 | 量化交易特化+持仓对账+闪崩熔断 | Phase 4 |
| v3.1.0 | 规则外部化 | escalation_rules.yaml 创建+热加载 | v3.0.0 |
| v4.0.0 | 全模块集成 | 与 MOD-GATE_ENGINE/018/020/024/025 双向对齐 | v3.1.0 |


## Consumers
- zephyr.escalation_protocol (internal)
