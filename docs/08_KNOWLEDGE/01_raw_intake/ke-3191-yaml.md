---
module_id: KE-3085
status: active
title: 七、与 YAML 规则的对应
category: session_log
---

# 七、与 YAML 规则的对应

七、与 YAML 规则的对应

本 Markdown 文档是 `D:\ZephyrAlpha\config\session_state_machine.yaml` 的人类可读版本。
YAML 文件是机器可执行的权威来源，本文档是解释性参考。

差异说明：
- YAML 中使用 `idle` 状态，本文档使用 `INIT`（语义相同，命名对齐 KBG-0035 三阶段模型）
- YAML 中有 `archived` 状态，本文档将其归入 `COMPLETED` 的出口动作（归档是完成后的自动行为，非独立状态）
