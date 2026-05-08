---
task_id: "TASK-INF-0105"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2 RL-007/017/018/020/021/028/034/035/047 + §5.5 + §6.1 Phase 2b + §11.1 代码索引"
title: "Phase 2b 自治闭环缺口填补——RL-007/017/018/020/021/028/034/035/047 + RI-12/14/15 独立落地"
description: |
  Phase 2b 自治闭环——系统自己诊断+预演+费用自控+Owner看总结报告。
  RL-007 依赖可视化→ModuleGraph JSON+D3.js（拓扑图实时渲染）+
  RL-017 缓存→CacheLayer LRU+VMS语义+DataAffinity（命中率≥30%）+
  RL-018 自诊→AutoDiagnostics 异常→诊断+KB补充+TrustDecayTracker+SelfLimiter+
  RL-020 操作预演→DryRunSimulator sandbox预演+审批门+一致性验证套件+CrossSessionLoopDetector+
  RL-021 费用归属→CostTracker per-module LLM+CPU/内存/IO 全资源追踪+
  RL-028 Loop恢复→错误率<3%持续1h→自动恢复OR手动+
  RL-034 Cooldown分层→CRITICAL 15m/HIGH 10m/MEDIUM 5m/LOW 2m+
  RL-035 全资源追踪→CostTracker覆盖CPU/内存/IO（FinOps可见）+
  RL-047 信任衰减→误报>30%→降级"建议模式"。
  §11.1 独立落地文件：auto_diagnostics.py / dry_run_simulator.py / cost_tracker.py
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cache.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cache.py"
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\auto_diagnosis.py"
    description: "RI-12 AutoDiagnostics——HealthCheck触发→Runbook匹配→诊断报告Markdown→修复→KB补充→SelfLimiter"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\dry_run_simulator.py"
    description: "RI-14 DryRunSimulator——sandbox预演+diff报告+审批门+一致性验证套件+CrossSessionLoopDetector+SelfSimulate"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\cost_tracker.py"
    description: "RI-15 CostTracker——LLM+CPU+内存+IO调用拦截+per-module费用归属+MaintainabilityScore+预算告警+飞书日报"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cache_affinity.py"
    description: "CacheLayer DataAffinity hints——LRU+VMS语义缓存+穿透防护+命中率≥30%"
  - path: "D:\\ZephyrAlpha\\config\\runbooks\\"
    description: "常见故障 SOP YAML——AutoDiagnostics消费"
  - path: "D:\\ZephyrAlpha\\config\\llm_pricing.yaml"
    description: "LLM 定价表——CostTracker 消费"
  - path: "D:\\ZephyrAlpha\\config\\dry_run_policy.yaml"
    description: "DryRun 策略——自动/人工审批边界+一致性验证套件开关+Loop检测开关"
  - path: "D:\\ZephyrAlpha\\config\\trust_decay_policy.yaml"
    description: "TrustDecayTracker恢复窗口+trust阈值+逆过程"
  - path: "D:\\ZephyrAlpha\\config\\owner_notification_tiers.yaml"
    description: "Owner告警预算N=10、通知分层规则、休假模式激活码"
  - path: "D:\\ZephyrAlpha\\config\\cache_layer.yaml"
    description: "TTL分层/LRU/语义缓存/DataAffinity hints"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\auto_diagnostics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\dry_run_simulator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\cost_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\cache_affinity.py"
  - "D:\\ZephyrAlpha\\config\\runbooks\\**\\*.yaml"
  - "D:\\ZephyrAlpha\\config\\llm_pricing.yaml"
  - "D:\\ZephyrAlpha\\config\\dry_run_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\trust_decay_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\owner_notification_tiers.yaml"
  - "D:\\ZephyrAlpha\\config\\cache_layer.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cache.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\health.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 AutoDiagnostics/DryRunSimulator/CostTracker 代码骨架"
    reason: "AutoDecideEngine + SleepTimeProtocol + PromptCacheManager + TradingKillSwitch"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "独立落地文件路径合规"
  - module_id: "MOD-INF-002"
    section: "§6.3"
    reason: "Owner告警预算N=10+通知分层规则"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "本蓝图——§2 RL缺口、§5.3 代码骨架(AutoDecideEngine/SleepTimeProtocol/PromptCacheManager/TradingKillSwitch/ModuleSandbox)、§5.7 AI施工自治回路、§6.3 容量模型"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 35000
timeout_minutes: 120
acceptance_criteria:
  - "AutoDiagnostics: HealthCheck DOWN → 诊断报告生成 ≤ 15s（RL-018）"
  - "DryRunSimulator: 写操作 100% 可预演（RL-020）"
  - "CostTracker: LLM+CPU/内存/IO 费用归属粒度=module_id+session_id（RL-021/035）"
  - "LoopDetector: 错误率<3%持续1h→自动恢复（RL-028）"
  - "Cooldown 分层: CRITICAL 15m/HIGH 10m/MEDIUM 5m/LOW 2m（RL-034）"
  - "TrustDecayTracker: 误报>30%→降级'建议模式'（RL-047）"
  - "CacheLayer 命中率 ≥ 30%（RL-017）"
  - "ModuleGraph D3.js 实时渲染（RL-007）"
  - "CostTracker 全资源 FinOps 可见"
rollback_instructions: |
  1. 删除独立落地文件：auto_diagnostics.py / dry_run_simulator.py / cost_tracker.py
  2. 删除新增 shared 扩展：cache_affinity.py
  3. 删除新增配置：runbooks/ / llm_pricing.yaml / dry_run_policy.yaml / trust_decay_policy.yaml / owner_notification_tiers.yaml / cache_layer.yaml
  4. 如 l01_infrastructure/ 目录为新创建→检查是否空→删除目录
depends_on:
  - "TASK-INF-0104"
blocked_by: []
status: "done"
tags_fn:
  - "infra"
  - "observability"
  - "data"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
