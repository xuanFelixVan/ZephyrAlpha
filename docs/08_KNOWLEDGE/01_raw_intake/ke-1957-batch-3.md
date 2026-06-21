---
module_id: KE-1866-------14-000
status: active
title: 2.3 Batch 3 — 集成层（14 条）
category: module_blueprint
---

# 2.3 Batch 3 — 集成层（14 条）

2.3 Batch 3 — 集成层（14 条）

创建 `D:\ZephyrAlpha\src\zephyr\contracts\capacity-assurance\batch3_integration.py`：
- CT-OT-001: OTel Span 格式（含 gen_ai.* 属性）
- CT-OT-002: W3C TraceContext 传播接口
- CT-HS-001: ZephyrHealthScore 输出格式
- CT-CT1: 与 predict-router 的容量告警联动接口
- CT-CT2: 与 market-data-ingestor 的熔断传播接口
- CT-CT3: 与 task-system 的 Token 扣减接口
- CT-CT4: 与 iguana-rebalancer 的账户熔断接口
- CT-GD-004: 双向模型切换逻辑
- CT-CR-001: change_rate_limiter 渐进式切换
- CT-AI-001: AI 行为预测维度 SLI 插桩
- CT-FB-001: 预警→修复闭环 Playbook 格式
- CT-DR-001: DR 备份与恢复契约
- CT-CP-001: 容量预测模型输入/输出
- CT-SM-001: Sandbox 策略生命周期管理
