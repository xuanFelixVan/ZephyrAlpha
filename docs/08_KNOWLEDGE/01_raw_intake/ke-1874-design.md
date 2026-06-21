---
module_id: KE-1783----------------------d-02-006
status: active
title: 2.21 五层顶尖架构 —— 反应式→预防式（决策 D-022-11）
category: module_blueprint
---

# 2.21 五层顶尖架构 —— 反应式→预防式（决策 D-022-11）

2.21 五层顶尖架构 —— 反应式→预防式（决策 D-022-11）

> **决策 D-022-11**：升级协议从三级升级升级为五层架构——L0持久化→L1自愈→L2决策路由→L3通知交互→L4审计治理。范式：从"出了问题才升级"到"在操作前就知道该升级"。
> **对标**：Google SRE + Temporal Durable Execution + Netflix Chaos Engineering + Anthropic RSP ASL。

```
┌───────────────────────────────────────────────────────┐
│              升级协议五层顶尖架构                        │
│  L4: 审计治理——Blameless Postmortem/SLO报告/混沌测试    │
│  L3: 通知交互——多通道/通俗化/batch/SPoHF/渐进自治       │
│  L2: 决策路由——Triage/环境感知/市场/PnL/风暴/恶意/熔断   │
│  L1: 自愈预处理——五步自愈/去重/清洗/Token控制/冻结/记忆  │
│  L0: 持久化韧性——Durable Exe/幂等/DLQ/回放              │
└───────────────────────────────────────────────────────┘
```

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
    ttl: {P
