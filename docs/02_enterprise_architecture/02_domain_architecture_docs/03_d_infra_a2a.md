---
doc_type: architecture_view
title: D_INFRA_A2A A2A通信架构文档
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 03_d_infra_a2a / A2A通信域 / A2A Communication

> **功能简介 / Overview**: Agent 与 Agent 之间的通信协议层，负责 AI 代理间的消息传递、请求路由和协议适配

> **文档作用 / Purpose**: 展示 A2A通信（D_INFRA_A2A）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/03_d_infra_a2a.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 03 | Number | 03 |
| 域ID | D_INFRA_A2A | Domain ID | D_INFRA_A2A |
| 域名称 | A2A通信 | Domain Name | A2A Communication |
| 层级 | L0 基础设施层 | Layer | L0 Infrastructure |
| 模块数 | 72 | Module Count | 72 |
| 域内依赖 | 42 | Internal Dependencies | 42 |
| 跨域入边 | 15 | Cross-domain Incoming | 15 |
| 跨域出边 | 10 | Cross-domain Outgoing | 10 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 72 | Production Modules | 72 |
| 容量 | 72/150 (正常) | Capacity | 72/150 (正常) |
| 描述 | A2A Card注册与发现(card_registry) | Description | A2A Card注册与发现(card_registry) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 72 个模块（生产态 72 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py["a2a_protocol/a2a_card_registry<br/>A2A Card Registry — 全局 Agent Card 注册单例<br/>文件: a2a_protocol/a2a_card_registry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py["layer2_communication/context_package<br/>Context Package — A2A 上下文包<br/>文件: layer2_communication/context_package.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py["layer2_communication/handoff_manager<br/>Handoff Manager — Agent 间任务交接<br/>文件: layer2_communication/handoff_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py["layer2_communication/message_router<br/>Message Router — A2A 消息路由<br/>文件: layer2_communication/message_router.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py["layer2_communication/push_notifier<br/>Push Notifier — A2A 推送通知<br/>文件: layer2_communication/push_notifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py["layer2_communication/streaming<br/>Streaming — A2A 流式传输<br/>文件: layer2_communication/streaming.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py["layer2_communication/trigger_monitor<br/>触发监控器<br/>文件: layer2_communication/trigger_monitor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py["layer3_coordination/_consensus<br/>基础设施/layer3 coordination包的consensus模块<br/>文件: layer3_coordination/_consensus.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py["layer3_coordination/_core_coordination<br/>基础设施/layer3<br/>coordination包的core_coordination模块<br/>文件: layer3_coordination/_core_coordination.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py["layer3_coordination/_intelligence<br/>基础设施/layer3 coordination包的intelligence模块<br/>文件: layer3_coordination/_intelligence.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py["layer3_coordination/_security_and_economics<br/>基础设施/layer3<br/>coordination包的security_and_economics模块<br/>文件: layer3_coordination<br/>/_security_and_economics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py["layer3_coordination/a2a_agent_blocklist<br/>A2A Agent 黑名单管理（重命名自<br/>a2a_protocol_security.py，AI-14 审计 P5 修复）<br/>文件: layer3_coordination/a2a_agent_blocklist.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py["layer3_coordination/a2a_carbon<br/>A2A 碳足迹追踪<br/>文件: layer3_coordination/a2a_carbon.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py["layer3_coordination/a2a_checkpoint<br/>A2A 检查点管理器<br/>文件: layer3_coordination/a2a_checkpoint.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py["layer3_coordination/a2a_consent<br/>P2: Agent同意管理<br/>文件: layer3_coordination/a2a_consent.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py["layer3_coordination/a2a_constitutional<br/>P2: 宪法性Agent管理<br/>文件: layer3_coordination/a2a_constitutional.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py["layer3_coordination/a2a_context_rot<br/>上下文腐烂检测<br/>文件: layer3_coordination/a2a_context_rot.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py["layer3_coordination/a2a_dashboard<br/>A2A 监控仪表盘 — Agent 集群运行状态可视化面板<br/>文件: layer3_coordination/a2a_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py["layer3_coordination/a2a_formal_verification<br/>A2A 形式化验证 — 协议属性模型检查<br/>文件: layer3_coordination<br/>/a2a_formal_verification.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py["layer3_coordination/a2a_frame_negotiation<br/>A2A ANP 帧协商协议 — Agent Negotiation Protocol<br/>帧层协商<br/>文件: layer3_coordination<br/>/a2a_frame_negotiation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py["layer3_coordination/a2a_hardware_router<br/>A2A 硬件路由器——GPU/CPU 调度<br/>文件: layer3_coordination/a2a_hardware_router.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py["layer3_coordination/a2a_hibernate<br/>P2: Agent休眠管理<br/>文件: layer3_coordination/a2a_hibernate.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py["layer3_coordination/a2a_immune<br/>A2A 免疫系统<br/>文件: layer3_coordination/a2a_immune.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py["layer3_coordination/a2a_metrics<br/>A2A 指标收集<br/>文件: layer3_coordination/a2a_metrics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py["layer3_coordination/a2a_protocol_gateway<br/>A2A 协议网关 — Agent 间请求分发与协议转换<br/>文件: layer3_coordination<br/>/a2a_protocol_gateway.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py["layer3_coordination/a2a_tracing<br/>A2A 分布式追踪 — 跨 Agent 请求链追踪<br/>(Span-based)<br/>文件: layer3_coordination/a2a_tracing.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py["layer3_coordination/a2a_vector_reputation<br/>向量化信誉系统<br/>文件: layer3_coordination<br/>/a2a_vector_reputation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py["layer3_coordination/spec_sync<br/>A2A Living Spec 同步 — 蓝图与实现的双向漂移管理<br/>文件: layer3_coordination/spec_sync.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_local_first_arch_py["a2a_protocol/local_first_arch<br/>基础设施/a2a protocol包的local_first_arch模块<br/>文件: a2a_protocol/local_first_arch.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_migration_strategy_py["a2a_protocol/migration_strategy<br/>基础设施/a2a protocol包的migration_strategy模块<br/>文件: a2a_protocol/migration_strategy.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_multi_agent_py["a2a_protocol/multi_agent<br/>multi_agent.py —— Multi-Agent 编排基座（Phase<br/>14 / 盲点 B33）<br/>文件: a2a_protocol/multi_agent.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py["a2a_protocol/multi_model_consensus<br/>基础设施/a2a<br/>protocol包的multi_model_consensus模块<br/>文件: a2a_protocol/multi_model_consensus.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py["a2a_protocol/offline_autonomy<br/>基础设施/a2a protocol包的offline_autonomy模块<br/>文件: a2a_protocol/offline_autonomy.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_offline_resilience_py["a2a_protocol/offline_resilience<br/>基础设施/a2a protocol包的offline_resilience模块<br/>文件: a2a_protocol/offline_resilience.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_phase_hold_py["a2a_protocol/phase_hold<br/>Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他<br/>Phase 3 模块不可并发施工.<br/>文件: a2a_protocol/phase_hold.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py["a2a_protocol/prompt_lifecycle<br/>基础设施/a2a protocol包的prompt_lifecycle模块<br/>文件: a2a_protocol/prompt_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_realtime_streaming_py["a2a_protocol/realtime_streaming<br/>基础设施/a2a protocol包的realtime_streaming模块<br/>文件: a2a_protocol/realtime_streaming.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py ~~~ src_zephyr_infrastructure_a2a_protocol_local_first_arch_py
    src_zephyr_infrastructure_a2a_protocol_local_first_arch_py ~~~ src_zephyr_infrastructure_a2a_protocol_migration_strategy_py
    src_zephyr_infrastructure_a2a_protocol_migration_strategy_py ~~~ src_zephyr_infrastructure_a2a_protocol_multi_agent_py
    src_zephyr_infrastructure_a2a_protocol_multi_agent_py ~~~ src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py
    src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py ~~~ src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py
    src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py ~~~ src_zephyr_infrastructure_a2a_protocol_offline_resilience_py
    src_zephyr_infrastructure_a2a_protocol_offline_resilience_py ~~~ src_zephyr_infrastructure_a2a_protocol_phase_hold_py
    src_zephyr_infrastructure_a2a_protocol_phase_hold_py ~~~ src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py
    src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py ~~~ src_zephyr_infrastructure_a2a_protocol_realtime_streaming_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py["layer2_communication/a2a_schemas<br/>A2A Message/Part 系统 — Layer 2 Communication<br/>文件: layer2_communication/a2a_schemas.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py["layer3_coordination/a2a_anomaly_detector<br/>A2A 统计异常检测引擎 — 基线学习 + 实时异常判断<br/>文件: layer3_coordination<br/>/a2a_anomaly_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py["layer3_coordination/a2a_behavior_fingerprint<br/>A2A 行为指纹 — Agent 行为模式学习与画像<br/>文件: layer3_coordination<br/>/a2a_behavior_fingerprint.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py["layer3_coordination/a2a_blame_attribution<br/>A2A 责任归属引擎 — 因果链分析 + 责任分配<br/>文件: layer3_coordination<br/>/a2a_blame_attribution.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py["layer3_coordination/a2a_causal_trace<br/>A2A 因果追踪 — 跨 Agent 操作因果链图谱<br/>文件: layer3_coordination/a2a_causal_trace.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py["layer3_coordination/a2a_collusion_detector<br/>A2A 合谋检测器 — Agent 间串通模式识别<br/>文件: layer3_coordination<br/>/a2a_collusion_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py["layer3_coordination<br/>/a2a_cross_agent_semantic_flow<br/>A2A 跨 Agent 语义流追踪 — 知识+意图在 Agent<br/>间传递<br/>文件: layer3_coordination<br/>/a2a_cross_agent_semantic_flow.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py["layer3_coordination/a2a_debate<br/>A2A 结构化辩论协议 — 多轮主张->反驳->合成<br/>文件: layer3_coordination/a2a_debate.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py["layer3_coordination/a2a_economics<br/>A2A 经济学——Token/API成本追踪<br/>文件: layer3_coordination/a2a_economics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py["layer3_coordination/a2a_forgetting<br/>A2A 遗忘机制<br/>文件: layer3_coordination/a2a_forgetting.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py["layer3_coordination/a2a_idempotency<br/>A2A 幂等性保证<br/>文件: layer3_coordination/a2a_idempotency.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py["layer3_coordination/a2a_idle_guard<br/>A2A 空闲守卫<br/>文件: layer3_coordination/a2a_idle_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py["layer3_coordination/a2a_knowledge_distill<br/>A2A 知识蒸馏 — 跨 Agent 经验提炼与共享<br/>文件: layer3_coordination<br/>/a2a_knowledge_distill.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py["layer3_coordination/a2a_latent_comm<br/>A2A 隐性通信检测 — 检测 Agent 通过副作用隐式通信<br/>文件: layer3_coordination/a2a_latent_comm.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py["layer3_coordination/a2a_negotiation<br/>A2A 协商协议 — Agent 间资源/任务分配协商<br/>文件: layer3_coordination/a2a_negotiation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py["layer3_coordination/a2a_red_team<br/>A2A 红队测试 — 攻击向量定义与执行框架<br/>文件: layer3_coordination/a2a_red_team.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py["layer3_coordination/a2a_saga<br/>A2A Saga 事务协议 — 多 Agent 跨步分布式事务<br/>文件: layer3_coordination/a2a_saga.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py["layer3_coordination/a2a_temporal_admission<br/>时序准入控制<br/>文件: layer3_coordination<br/>/a2a_temporal_admission.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py["layer3_coordination/a2a_voting<br/>A2A 加权投票协议 — 多 Agent 共识达成机制<br/>文件: layer3_coordination/a2a_voting.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py["layer3_coordination/a2a_work_steal<br/>A2A 工作窃取调度器 — 跨 Agent 负载均衡<br/>文件: layer3_coordination/a2a_work_steal.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py["layer3_coordination/arbitrator<br/>A2A 三级仲裁引擎 — priority -> rule -><br/>escalation<br/>文件: layer3_coordination/arbitrator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py["layer3_coordination/cascade_guard<br/>级联守卫——防止失败在Agent间级联<br/>文件: layer3_coordination/cascade_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py["layer3_coordination/conflict_detector<br/>A2A 冲突检测引擎 — 语义+文本+资源三维冲突检测<br/>文件: layer3_coordination/conflict_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py["layer3_coordination/construction_verifier<br/>施工后验证器 —<br/>自指悖论防御：不橡胶图章，真正验证 A2A<br/>协议模块的施工完整性<br/>文件: layer3_coordination<br/>/construction_verifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py["layer3_coordination/deadlock_guard<br/>P2: 死锁守卫<br/>文件: layer3_coordination/deadlock_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py["layer3_coordination/livelock_detector<br/>P2: 活锁检测器<br/>文件: layer3_coordination/livelock_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py["layer3_coordination/semantic_diff<br/>A2A 语义差异引擎 — 结构感知的 Agent 间差异检测<br/>文件: layer3_coordination/semantic_diff.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py["layer1_discovery/a2a_registry<br/>A2A Registry — Agent Card 注册与发现<br/>文件: layer1_discovery/a2a_registry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py["layer1_discovery/identity_verifier<br/>Identity Verifier — JWT 身份验证器<br/>文件: layer1_discovery/identity_verifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py["layer3_coordination/a2a_delegation_chain<br/>委托链<br/>文件: layer3_coordination<br/>/a2a_delegation_chain.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py["layer3_coordination/a2a_security<br/>A2A 安全内容扫描器 — 六大类威胁检测<br/>文件: layer3_coordination/a2a_security.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py["layer3_coordination/session_smuggling_defense<br/>A2A Session 走私防御 — 防止跨 Agent session<br/>上下文伪造<br/>文件: layer3_coordination<br/>/session_smuggling_defense.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py["layer3_coordination/supervisor<br/>Supervisor — A2A Layer 3 Coordination<br/>文件: layer3_coordination/supervisor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py["layer1_discovery/agent_card<br/>Agent Card 模型 — A2A Layer 1 Discovery<br/>文件: layer1_discovery/agent_card.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py["layer2_communication/a2a_state<br/>A2A Task 状态机 — Layer 2 Communication<br/>文件: layer2_communication/a2a_state.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py
    src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_multi_agent_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_offline_resilience_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py
    D_INFRA_RUNTIME["运行时集成<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>Runtime Integration<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_infrastructure_a2a_protocol_phase_hold_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_infrastructure_a2a_protocol_phase_hold_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py,src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py,src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py,src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py,src_zephyr_infrastructure_a2a_protocol_local_first_arch_py,src_zephyr_infrastructure_a2a_protocol_migration_strategy_py,src_zephyr_infrastructure_a2a_protocol_multi_agent_py,src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py,src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py,src_zephyr_infrastructure_a2a_protocol_offline_resilience_py,src_zephyr_infrastructure_a2a_protocol_phase_hold_py,src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py,src_zephyr_infrastructure_a2a_protocol_realtime_streaming_py production
    class D_SHARED,D_GOV_OPS_RESILIENCE,D_INFRA_RUNTIME,D_GOVERNANCE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 72 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py["a2a_protocol/a2a_card_registry<br/>A2A Card Registry — 全局 Agent Card 注册单例<br/>文件: a2a_protocol/a2a_card_registry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py["layer2_communication/context_package<br/>Context Package — A2A 上下文包<br/>文件: layer2_communication/context_package.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py["layer2_communication/handoff_manager<br/>Handoff Manager — Agent 间任务交接<br/>文件: layer2_communication/handoff_manager.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py["layer2_communication/message_router<br/>Message Router — A2A 消息路由<br/>文件: layer2_communication/message_router.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py["layer2_communication/push_notifier<br/>Push Notifier — A2A 推送通知<br/>文件: layer2_communication/push_notifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py["layer2_communication/streaming<br/>Streaming — A2A 流式传输<br/>文件: layer2_communication/streaming.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py["layer2_communication/trigger_monitor<br/>触发监控器<br/>文件: layer2_communication/trigger_monitor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py["layer3_coordination/_consensus<br/>基础设施/layer3 coordination包的consensus模块<br/>文件: layer3_coordination/_consensus.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py["layer3_coordination/_core_coordination<br/>基础设施/layer3<br/>coordination包的core_coordination模块<br/>文件: layer3_coordination/_core_coordination.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py["layer3_coordination/_intelligence<br/>基础设施/layer3 coordination包的intelligence模块<br/>文件: layer3_coordination/_intelligence.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py["layer3_coordination/_security_and_economics<br/>基础设施/layer3<br/>coordination包的security_and_economics模块<br/>文件: layer3_coordination<br/>/_security_and_economics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py["layer3_coordination/a2a_agent_blocklist<br/>A2A Agent 黑名单管理（重命名自<br/>a2a_protocol_security.py，AI-14 审计 P5 修复）<br/>文件: layer3_coordination/a2a_agent_blocklist.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py["layer3_coordination/a2a_carbon<br/>A2A 碳足迹追踪<br/>文件: layer3_coordination/a2a_carbon.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py["layer3_coordination/a2a_checkpoint<br/>A2A 检查点管理器<br/>文件: layer3_coordination/a2a_checkpoint.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py["layer3_coordination/a2a_consent<br/>P2: Agent同意管理<br/>文件: layer3_coordination/a2a_consent.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py["layer3_coordination/a2a_constitutional<br/>P2: 宪法性Agent管理<br/>文件: layer3_coordination/a2a_constitutional.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py["layer3_coordination/a2a_context_rot<br/>上下文腐烂检测<br/>文件: layer3_coordination/a2a_context_rot.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py["layer3_coordination/a2a_dashboard<br/>A2A 监控仪表盘 — Agent 集群运行状态可视化面板<br/>文件: layer3_coordination/a2a_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py["layer3_coordination/a2a_formal_verification<br/>A2A 形式化验证 — 协议属性模型检查<br/>文件: layer3_coordination<br/>/a2a_formal_verification.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py["layer3_coordination/a2a_frame_negotiation<br/>A2A ANP 帧协商协议 — Agent Negotiation Protocol<br/>帧层协商<br/>文件: layer3_coordination<br/>/a2a_frame_negotiation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py["layer3_coordination/a2a_hardware_router<br/>A2A 硬件路由器——GPU/CPU 调度<br/>文件: layer3_coordination/a2a_hardware_router.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py["layer3_coordination/a2a_hibernate<br/>P2: Agent休眠管理<br/>文件: layer3_coordination/a2a_hibernate.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py["layer3_coordination/a2a_immune<br/>A2A 免疫系统<br/>文件: layer3_coordination/a2a_immune.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py["layer3_coordination/a2a_metrics<br/>A2A 指标收集<br/>文件: layer3_coordination/a2a_metrics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py["layer3_coordination/a2a_protocol_gateway<br/>A2A 协议网关 — Agent 间请求分发与协议转换<br/>文件: layer3_coordination<br/>/a2a_protocol_gateway.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py["layer3_coordination/a2a_tracing<br/>A2A 分布式追踪 — 跨 Agent 请求链追踪<br/>(Span-based)<br/>文件: layer3_coordination/a2a_tracing.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py["layer3_coordination/a2a_vector_reputation<br/>向量化信誉系统<br/>文件: layer3_coordination<br/>/a2a_vector_reputation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py["layer3_coordination/spec_sync<br/>A2A Living Spec 同步 — 蓝图与实现的双向漂移管理<br/>文件: layer3_coordination/spec_sync.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_local_first_arch_py["a2a_protocol/local_first_arch<br/>基础设施/a2a protocol包的local_first_arch模块<br/>文件: a2a_protocol/local_first_arch.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_migration_strategy_py["a2a_protocol/migration_strategy<br/>基础设施/a2a protocol包的migration_strategy模块<br/>文件: a2a_protocol/migration_strategy.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_multi_agent_py["a2a_protocol/multi_agent<br/>multi_agent.py —— Multi-Agent 编排基座（Phase<br/>14 / 盲点 B33）<br/>文件: a2a_protocol/multi_agent.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py["a2a_protocol/multi_model_consensus<br/>基础设施/a2a<br/>protocol包的multi_model_consensus模块<br/>文件: a2a_protocol/multi_model_consensus.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py["a2a_protocol/offline_autonomy<br/>基础设施/a2a protocol包的offline_autonomy模块<br/>文件: a2a_protocol/offline_autonomy.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_offline_resilience_py["a2a_protocol/offline_resilience<br/>基础设施/a2a protocol包的offline_resilience模块<br/>文件: a2a_protocol/offline_resilience.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_phase_hold_py["a2a_protocol/phase_hold<br/>Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他<br/>Phase 3 模块不可并发施工.<br/>文件: a2a_protocol/phase_hold.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py["a2a_protocol/prompt_lifecycle<br/>基础设施/a2a protocol包的prompt_lifecycle模块<br/>文件: a2a_protocol/prompt_lifecycle.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_realtime_streaming_py["a2a_protocol/realtime_streaming<br/>基础设施/a2a protocol包的realtime_streaming模块<br/>文件: a2a_protocol/realtime_streaming.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py ~~~ src_zephyr_infrastructure_a2a_protocol_local_first_arch_py
    src_zephyr_infrastructure_a2a_protocol_local_first_arch_py ~~~ src_zephyr_infrastructure_a2a_protocol_migration_strategy_py
    src_zephyr_infrastructure_a2a_protocol_migration_strategy_py ~~~ src_zephyr_infrastructure_a2a_protocol_multi_agent_py
    src_zephyr_infrastructure_a2a_protocol_multi_agent_py ~~~ src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py
    src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py ~~~ src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py
    src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py ~~~ src_zephyr_infrastructure_a2a_protocol_offline_resilience_py
    src_zephyr_infrastructure_a2a_protocol_offline_resilience_py ~~~ src_zephyr_infrastructure_a2a_protocol_phase_hold_py
    src_zephyr_infrastructure_a2a_protocol_phase_hold_py ~~~ src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py
    src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py ~~~ src_zephyr_infrastructure_a2a_protocol_realtime_streaming_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py["layer2_communication/a2a_schemas<br/>A2A Message/Part 系统 — Layer 2 Communication<br/>文件: layer2_communication/a2a_schemas.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py["layer3_coordination/a2a_anomaly_detector<br/>A2A 统计异常检测引擎 — 基线学习 + 实时异常判断<br/>文件: layer3_coordination<br/>/a2a_anomaly_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py["layer3_coordination/a2a_behavior_fingerprint<br/>A2A 行为指纹 — Agent 行为模式学习与画像<br/>文件: layer3_coordination<br/>/a2a_behavior_fingerprint.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py["layer3_coordination/a2a_blame_attribution<br/>A2A 责任归属引擎 — 因果链分析 + 责任分配<br/>文件: layer3_coordination<br/>/a2a_blame_attribution.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py["layer3_coordination/a2a_causal_trace<br/>A2A 因果追踪 — 跨 Agent 操作因果链图谱<br/>文件: layer3_coordination/a2a_causal_trace.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py["layer3_coordination/a2a_collusion_detector<br/>A2A 合谋检测器 — Agent 间串通模式识别<br/>文件: layer3_coordination<br/>/a2a_collusion_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py["layer3_coordination<br/>/a2a_cross_agent_semantic_flow<br/>A2A 跨 Agent 语义流追踪 — 知识+意图在 Agent<br/>间传递<br/>文件: layer3_coordination<br/>/a2a_cross_agent_semantic_flow.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py["layer3_coordination/a2a_debate<br/>A2A 结构化辩论协议 — 多轮主张->反驳->合成<br/>文件: layer3_coordination/a2a_debate.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py["layer3_coordination/a2a_economics<br/>A2A 经济学——Token/API成本追踪<br/>文件: layer3_coordination/a2a_economics.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py["layer3_coordination/a2a_forgetting<br/>A2A 遗忘机制<br/>文件: layer3_coordination/a2a_forgetting.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py["layer3_coordination/a2a_idempotency<br/>A2A 幂等性保证<br/>文件: layer3_coordination/a2a_idempotency.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py["layer3_coordination/a2a_idle_guard<br/>A2A 空闲守卫<br/>文件: layer3_coordination/a2a_idle_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py["layer3_coordination/a2a_knowledge_distill<br/>A2A 知识蒸馏 — 跨 Agent 经验提炼与共享<br/>文件: layer3_coordination<br/>/a2a_knowledge_distill.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py["layer3_coordination/a2a_latent_comm<br/>A2A 隐性通信检测 — 检测 Agent 通过副作用隐式通信<br/>文件: layer3_coordination/a2a_latent_comm.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py["layer3_coordination/a2a_negotiation<br/>A2A 协商协议 — Agent 间资源/任务分配协商<br/>文件: layer3_coordination/a2a_negotiation.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py["layer3_coordination/a2a_red_team<br/>A2A 红队测试 — 攻击向量定义与执行框架<br/>文件: layer3_coordination/a2a_red_team.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py["layer3_coordination/a2a_saga<br/>A2A Saga 事务协议 — 多 Agent 跨步分布式事务<br/>文件: layer3_coordination/a2a_saga.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py["layer3_coordination/a2a_temporal_admission<br/>时序准入控制<br/>文件: layer3_coordination<br/>/a2a_temporal_admission.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py["layer3_coordination/a2a_voting<br/>A2A 加权投票协议 — 多 Agent 共识达成机制<br/>文件: layer3_coordination/a2a_voting.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py["layer3_coordination/a2a_work_steal<br/>A2A 工作窃取调度器 — 跨 Agent 负载均衡<br/>文件: layer3_coordination/a2a_work_steal.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py["layer3_coordination/arbitrator<br/>A2A 三级仲裁引擎 — priority -> rule -><br/>escalation<br/>文件: layer3_coordination/arbitrator.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py["layer3_coordination/cascade_guard<br/>级联守卫——防止失败在Agent间级联<br/>文件: layer3_coordination/cascade_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py["layer3_coordination/conflict_detector<br/>A2A 冲突检测引擎 — 语义+文本+资源三维冲突检测<br/>文件: layer3_coordination/conflict_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py["layer3_coordination/construction_verifier<br/>施工后验证器 —<br/>自指悖论防御：不橡胶图章，真正验证 A2A<br/>协议模块的施工完整性<br/>文件: layer3_coordination<br/>/construction_verifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py["layer3_coordination/deadlock_guard<br/>P2: 死锁守卫<br/>文件: layer3_coordination/deadlock_guard.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py["layer3_coordination/livelock_detector<br/>P2: 活锁检测器<br/>文件: layer3_coordination/livelock_detector.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py["layer3_coordination/semantic_diff<br/>A2A 语义差异引擎 — 结构感知的 Agent 间差异检测<br/>文件: layer3_coordination/semantic_diff.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py["layer1_discovery/a2a_registry<br/>A2A Registry — Agent Card 注册与发现<br/>文件: layer1_discovery/a2a_registry.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py["layer1_discovery/identity_verifier<br/>Identity Verifier — JWT 身份验证器<br/>文件: layer1_discovery/identity_verifier.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py["layer3_coordination/a2a_delegation_chain<br/>委托链<br/>文件: layer3_coordination<br/>/a2a_delegation_chain.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py["layer3_coordination/a2a_security<br/>A2A 安全内容扫描器 — 六大类威胁检测<br/>文件: layer3_coordination/a2a_security.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py["layer3_coordination/session_smuggling_defense<br/>A2A Session 走私防御 — 防止跨 Agent session<br/>上下文伪造<br/>文件: layer3_coordination<br/>/session_smuggling_defense.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py["layer3_coordination/supervisor<br/>Supervisor — A2A Layer 3 Coordination<br/>文件: layer3_coordination/supervisor.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py["layer1_discovery/agent_card<br/>Agent Card 模型 — A2A Layer 1 Discovery<br/>文件: layer1_discovery/agent_card.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py["layer2_communication/a2a_state<br/>A2A Task 状态机 — Layer 2 Communication<br/>文件: layer2_communication/a2a_state.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py ~~~ src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py
    src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py
    src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py
    src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py
    src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_a2a_protocol_a2a_card_registry_py,src_zephyr_infrastructure_a2a_protocol_layer1_discovery_a2a_registry_py,src_zephyr_infrastructure_a2a_protocol_layer1_discovery_agent_card_py,src_zephyr_infrastructure_a2a_protocol_layer1_discovery_identity_verifier_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_schemas_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_a2a_state_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_context_package_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_handoff_manager_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_message_router_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_push_notifier_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_streaming_py,src_zephyr_infrastructure_a2a_protocol_layer2_communication_trigger_monitor_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_consensus_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_core_coordination_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_intelligence_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_security_and_economics_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_agent_blocklist_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_anomaly_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_behavior_fingerprint_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_blame_attribution_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_carbon_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_causal_trace_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_checkpoint_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_collusion_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_consent_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_constitutional_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_context_rot_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_cross_agent_semantic_flow_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_dashboard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_debate_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_delegation_chain_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_economics_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_forgetting_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_formal_verification_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_frame_negotiation_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hardware_router_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_hibernate_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idempotency_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_idle_guard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_immune_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_knowledge_distill_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_latent_comm_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_metrics_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_negotiation_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_protocol_gateway_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_red_team_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_saga_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_security_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_temporal_admission_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_tracing_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_vector_reputation_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_voting_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_a2a_work_steal_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_arbitrator_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_cascade_guard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_conflict_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_construction_verifier_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_deadlock_guard_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_livelock_detector_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_semantic_diff_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_session_smuggling_defense_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_spec_sync_py,src_zephyr_infrastructure_a2a_protocol_layer3_coordination_supervisor_py,src_zephyr_infrastructure_a2a_protocol_local_first_arch_py,src_zephyr_infrastructure_a2a_protocol_migration_strategy_py,src_zephyr_infrastructure_a2a_protocol_multi_agent_py,src_zephyr_infrastructure_a2a_protocol_multi_model_consensus_py,src_zephyr_infrastructure_a2a_protocol_offline_autonomy_py,src_zephyr_infrastructure_a2a_protocol_offline_resilience_py,src_zephyr_infrastructure_a2a_protocol_phase_hold_py,src_zephyr_infrastructure_a2a_protocol_prompt_lifecycle_py,src_zephyr_infrastructure_a2a_protocol_realtime_streaming_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | A2A 三级仲裁引擎 — priority -> rule -> escalation (layer... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Escalation Protocol data models — MOD-INF-022 (escalatio... | 导入依赖 / import_depends |
| 2 | Agent Card 模型 — A2A Layer 1 Discovery (layer1_discover... | → | D_SHARED 共享服务: A2A Registry and Agent Card contracts — discovery and id... | 导入依赖 / import_depends |
| 3 | A2A Message/Part 系统 — Layer 2 Communication (layer2_co... | → | D_SHARED 共享服务: A2A data structure contracts — Message, Task, and StateM... | 导入依赖 / import_depends |
| 4 | A2A Task 状态机 — Layer 2 Communication (layer2_communic... | → | D_SHARED 共享服务: A2A data structure contracts — Message, Task, and StateM... | 导入依赖 / import_depends |
| 5 | Context Package — A2A 上下文包 (layer2_communication/con... | → | D_SHARED 共享服务: A2A data structure contracts — Message, Task, and StateM... | 导入依赖 / import_depends |
| 6 | Handoff Manager — Agent 间任务交接 (layer2_communication... | → | D_SHARED 共享服务: A2A data structure contracts — Message, Task, and StateM... | 导入依赖 / import_depends |
| 7 | A2A 三级仲裁引擎 — priority -> rule -> escalation (layer... | → | D_SHARED 共享服务: A2A Coordination — shared interface definitions for mult... | 导入依赖 / import_depends |
| 8 | 施工后验证器 — 自指悖论防御：不橡胶图章，真正验证 A2A 协... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 9 | Supervisor — A2A Layer 3 Coordination (layer3_coordinati... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 10 | multi_agent.py —— Multi-Agent 编排基座（Phase 14 | 盲点... | → | D_SHARED 共享服务: A2A Coordination — shared interface definitions for mult... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: 治理集成 / Re-export bridge for layer3_coordination gover... | → | A2A 监控仪表盘 — Agent 集群运行状态可视化面板 (layer3_co... | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: 治理集成 / Re-export bridge for layer3_coordination gover... | → | A2A 形式化验证 — 协议属性模型检查 (layer3_coordination/a... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: 治理集成 / Re-export bridge for layer3_coordination gover... | → | A2A ANP 帧协商协议 — Agent Negotiation Protocol 帧层协商... | 导入依赖 / import_depends |
| 4 | D_GOVERNANCE 生命周期管理: 治理集成 / Re-export bridge for layer3_coordination gover... | → | A2A 协议网关 — Agent 间请求分发与协议转换 (layer3_coordi... | 导入依赖 / import_depends |
| 5 | D_GOVERNANCE 生命周期管理: 治理集成 / Re-export bridge for layer3_coordination gover... | → | A2A 分布式追踪 — 跨 Agent 请求链追踪 (Span-based) (layer... | 导入依赖 / import_depends |
| 6 | D_GOVERNANCE 生命周期管理: 治理集成 / Re-export bridge for layer3_coordination gover... | → | A2A Living Spec 同步 — 蓝图与实现的双向漂移管理 (layer3_... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: A2A Phase 4 Hold 测试 — Phase 3 未完成时禁止 Phase 4 启... | → | Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他 Phase 3 ... | 测试依赖 / test_depends |
| 8 | D_GOVERNANCE 生命周期管理: Phase Gates + 依赖审计隔离 + A2A Phase 4 Hold 测试. (shar... | → | Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他 Phase 3 ... | 测试依赖 / test_depends |
| 9 | D_GOV_OPS_RESILIENCE 运维弹性治理: F5BootIntegration — F5 自动启动/关闭集成 (MOD-INF-022 §... | → | A2A 三级仲裁引擎 — priority -> rule -> escalation (layer... | 导入依赖 / import_depends |
| 10 | D_GOV_OPS_RESILIENCE 运维弹性治理: F5EventSubscriber — F5 事件启动机制 (MOD-INF-022 §3). (... | → | A2A 三级仲裁引擎 — priority -> rule -> escalation (layer... | 导入依赖 / import_depends |
| 11 | D_GOV_OPS_RESILIENCE 运维弹性治理: resilience_governance/offline_autonomy.py | → | a2a_protocol/offline_autonomy.py | 导入依赖 / import_depends |
| 12 | D_GOV_OPS_RESILIENCE 运维弹性治理: resilience_governance/offline_resilience.py | → | a2a_protocol/offline_resilience.py | 导入依赖 / import_depends |
| 13 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | A2A Card Registry — 全局 Agent Card 注册单例 (a2a_protoc... | 导入依赖 / import_depends |
| 14 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑） (tradin... | → | A2A 协议网关 — Agent 间请求分发与协议转换 (layer3_coordi... | 导入依赖 / import_depends |
| 15 | D_INFRA_RUNTIME 运行时集成: trading/capability_sync.py | → | A2A Registry — Agent Card 注册与发现 (layer1_discovery/a... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 10 条 + 入边 15 条 = 25 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_INFRA_A2A["D_INFRA_A2A<br/>A2A通信"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INFRA_A2A -->|9条 导入依赖 / import_depends| D_SHARED
    D_INFRA_A2A -->|1条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOVERNANCE -->|8条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_A2A
    D_GOV_OPS_RESILIENCE -->|4条 导入依赖 / import_depends| D_INFRA_A2A
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_INFRA_A2A
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
