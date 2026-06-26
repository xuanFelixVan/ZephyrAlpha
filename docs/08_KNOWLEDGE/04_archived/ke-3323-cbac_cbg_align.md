---
module_id: KE-3204--------cbac---cbg---align-002
title: 2.10 三件套新组件（CBAC / CBG / AlignmentMonitor，**Wave 1 R83/R84 增补**）
category: documentation
ttl: permanent
---

# 2.10 三件套新组件（CBAC / CBG / AlignmentMonitor，**Wave 1 R83/R84 增补**）

2.10 三件套新组件（CBAC / CBG / AlignmentMonitor，**Wave 1 R83/R84 增补**）

| 组件 | 路径 | 权限 | 判定理由 | 审批要求 |
|------|------|------|---------|---------|
| CBACRegistry / capabilities.yaml | `config/capabilities.yaml` | **Immutable Core** | 注册表 schema 是治理"宪法"，AI 不可改 | Owner + R-XXX |
| CapabilityChecker | `src/zephyr/shared/capability.py` | Immutable Core | 校验逻辑核心 | Owner + R-XXX |
| CircuitBreakerGateway | `src/zephyr/gates/circuit_breaker.py` | Immutable Core | 熔断不可由 AI 禁用 | Owner + R-XXX |
| circuit_breaker_state 表 | `data/circuit_breaker.db` | Immutable Core（追加专用） | 状态历史不可改写 | Owner |
| AlignmentMonitor| `src/zephyr/feedback-loop/alignment_monitor.py` | Human-Gated | 评估算法可演进，阈值需审批 | Owner 审批 |
| L2b 沙箱 ACL（KBG-0018）| 项目外 OS 级 | Immutable Core | OS 级 ACL 不由 RI 改（**Wave 1 C-03 裁决**）| Owner |
