---
module_id: KE-module_blu-12_6______p0-003
title: 12.6 降级路径 P0
category: module_blueprint
---

# 12.6 降级路径 P0

12.6 降级路径 P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-D1 | DEGRADE-001 触发 | mock VMS degraded | build | fs_fallback 激活，ce_degrade.log 记录 |
| P0-D2 | DEGRADE-002 触发 | 删除 Qwen 模型 | compress | 规则降级，ce_degrade.log 记录 |
| P0-D3 | DEGRADE-003 触发 | mock 所有 MCP 通道失败 | inject | 降级 prompts + 丢 slot，ce_degrade.log 记录 |

---
