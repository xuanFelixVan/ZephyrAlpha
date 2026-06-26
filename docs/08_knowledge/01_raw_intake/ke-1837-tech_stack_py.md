---
module_id: KE-1746-----tech-stack-py-000
status: active
title: 2.2 创建 `tech_stack.py`
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 创建 `tech_stack.py`

2.2 创建 `tech_stack.py`

在 `D:\ZephyrAlpha\src\\zephyr\\shared\\tech_stack.py` 中实现 `TechStackValidator`：
- `validate()`: 启动时逐一校验 16 项组件的可用性
- `check_pydantic_v2()`: 确认 Pydantic v2 可用
- `check_sqlite()`: 确认 SQLite 可用
- `check_otel_sdk()`: 确认 OpenTelemetry SDK 可用
- `check_pytest()`: 确认 pytest 可用
- `check_chromadb()`: 确认 ChromaDB 可用
- `check_psutil()`: 确认 psutil 可用
- `report()`: 输出组件可用性报告
