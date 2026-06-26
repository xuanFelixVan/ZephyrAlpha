---
module_id: KE-3521
title: 2.1 三层定义速查
category: governance
ttl: permanent
---

# 2.1 三层定义速查

2.1 三层定义速查

| 层 | 大白话定位 | 职责 | 典型产物 |
|---|---|---|---|
| **Policy 层** | 规章制度部门 | 定规则/存规则/版本化/append-only review | Markdown 规则、ADR、folder-charters、Rego |
| **Factory 层** | 纪委工具组 | 把规则编译成可执行检查器 + 工具链管理 | ruff/mypy 配置、fitness function、arch_guard |
| **Runtime 层** | 巡查队+审计处+档案室 | 拦截+审计+反馈回写 Policy | pre-commit、CI、OPA sidecar、audit-log |
