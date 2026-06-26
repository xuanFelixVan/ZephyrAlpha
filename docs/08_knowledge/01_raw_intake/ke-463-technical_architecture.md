---
module_id: KE-415---04-ta-001
title: 5.3 与 04-TA 技术架构的关系
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5.3 与 04-TA 技术架构的关系

5.3 与 04-TA 技术架构的关系

04-TA § 定义**全局技术基线**（Python >=3.11，见 `pyproject.toml` / Redis / PostgreSQL / Parquet 等），本视图 §5 **在平面维度做下钻**——同一业务逻辑在不同平面可能选用不同技术栈（例：L04 风控 Warm Path 用 Python async，Hot Path 用 Rust 重写并通过 Aeron 对接）。**4bis 不替代 04-TA，是补充正交切面**。
