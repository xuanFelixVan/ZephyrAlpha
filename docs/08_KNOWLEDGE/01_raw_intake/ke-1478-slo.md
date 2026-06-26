---
module_id: KE-1388-----slo-003
title: 11.2 冷启动 SLO
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 11.2 冷启动 SLO

11.2 冷启动 SLO

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程 import | ≤ 1 s | 仅 import llm-security |
| 规则文件加载 | ≤ 300 ms | yaml + 正则编译 |
| detect-secrets 初始化 | ≤ 500 ms | 插件加载 |
| schema registry 初始化 | ≤ 200 ms | 首批 schema 预注册 |
| 首次 `validate_input()` | ≤ 50 ms | - |
| **总冷启动到可用** | **≤ 3 s** | - |

---
