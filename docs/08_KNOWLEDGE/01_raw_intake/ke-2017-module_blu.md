---
module_id: KE-1926
status: active
title: 2.6 多轮审计扩展风险
category: module_blueprint
---

# 2.6 多轮审计扩展风险

2.6 多轮审计扩展风险

在 `risk-register.yaml` 和 `risk_mitigation.py` 中补充：
- 盲点 #14 → R9: hash 链校验性能退化（大文件 hash 计算随 Provenance 增长而退化）
- 盲点 #15 → R10: Token 预估模型白盒包裹风险（AI 构造特殊 input 格式导致预估失败）
- 盲点 #16 → R11: Kill Switch 双通道竞态（环境变量 + 文件信号并写竞态）
- 盲点 #26 → R12: 累计 Error Budget 消耗不变式破坏（Δ=累计-Σ分窗口，|Δ|>1% 未被检测）
- 盲点 #38 → R13: SLO 配置泄露到应用日志（敏感阈值信息通过 structlog 泄露）
- 盲点 #49 → R14: 多 Batch 迁移中 ContractBus 崩溃恢复失败（部分契约已迁移、部分未迁移的中间态）
- 盲点 #65 → R15: wchar_t 路径匹配失败（Windows Unicode 路径与 ASCII 路径不一致）
- 盲点 #66 → R16: ChromaDB 线程池泄漏（长期运行后线程数持续增长）
