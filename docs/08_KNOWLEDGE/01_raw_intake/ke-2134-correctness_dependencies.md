---
module_id: KE-2042
title: 3.1 Correctness Dependencies（正确运行依赖）
category: module_blueprint
---

# 3.1 Correctness Dependencies（正确运行依赖）

3.1 Correctness Dependencies（正确运行依赖）

| 依赖 | 具体对象 | 路径 |
|------|---------|------|
| SSoT Registry | Pydantic v2 models | `src/zephyr/shared/pydantic_v2_migrator.py` |
| Context & Doc Compressor | context docs | `src/zephyr/context-engine/doc_compressor.py` |
| Structured Logging | 结构化日志 | `src/zephyr/shared/zephyr_logger.py` |
| MCP Tool Rate Limiting | tool_contract.yaml | `src/zephyr/mcp/tool-contracts.yaml` |
| Config Auto-Reload Logic | ai_context_policy.yaml 构建规则 | `config/capacity/ai_context_policy.yaml` |
