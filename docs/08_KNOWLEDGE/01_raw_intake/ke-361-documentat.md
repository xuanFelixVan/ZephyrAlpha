---
module_id: KE-326
status: active
title: 4.2 核心设计原则
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.2 核心设计原则

4.2 核心设计原则

1. **fail-closed**：任何校验器故障 → 拒绝调用（而非放行）。**与其他 6 大核心服务的 degraded=True 降级不同**，LSG 是唯一必须 fail-closed 的服务
2. **四层防御**：L1 输入分类 → L2 System Prompt 隔离 → L3 输出 Schema → L4 Pattern 巡检
3. **Pydantic v2 + `extra='forbid'`**：所有输入输出都有严格 Schema，未知字段一律拒绝
4. **零信任 LLM 响应**：即便是本地 Qwen2.5-3B 的输出也必须经 L3/L4 校验
5. **审计完整性**：每次调用生成 `request_id` + `input_hash` + `output_hash` 写入 Session Log
