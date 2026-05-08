---
module_id: KE-documentat-11_1_experimental-003
title: 11.1 experimental 最小响应流程
category: documentation
---

# 11.1 experimental 最小响应流程

11.1 experimental 最小响应流程

当 D6 任一 P0 事件发生（`secret_alert` / `sandbox_violation` / `llm_injection_detected`）：

1. **自动**：LSG/Sandbox/Scanner 立即拦截 + 写 audit 事件 + FLE 异常上报
2. **10 分钟内**：飞书 Bot 推送告警（优先级 P0 / P1）
3. **1 小时内**：人工确认 + 决定是否启动手动响应
4. **24 小时内**：写 `docs/09_audit/findings/incident-YYYYMMDD-<id>.md`（时间线 + 根因 + 缓解）
5. **7 天内**：复盘 + 产出 ADR（如需要架构修改）
