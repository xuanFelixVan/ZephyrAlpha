---
module_id: KE-061
status: active
title: 1. Purpose of this view / 本视图的用途
category: documentation
---

# 1. Purpose of this view / 本视图的用途

1. Purpose of this view / 本视图的用途

The Data Architecture view answers questions about the **business data objects** flowing through the system, independent of how those objects are stored, indexed, or rendered as documents.

数据架构视图回答关于"系统里**业务数据对象**"的全部问题，**独立于**这些对象具体如何存储、索引、或被渲染成文档：

- 系统里到底有哪些核心数据实体？（Data Entity Catalog / 数据实体清单）
- 数据按 冷/温/热 × 批/流 × 内/外 三维如何分类？（Data Classification / 数据分类）
- 如何确保任意时点回看的因子值"当时确实可知"？（Point-in-Time / PIT）
- 退市、停牌、合并、分拆的股票如何在历史数据里正确表达？（Survivorship Bias / 幸存者偏差）
- 一个因子值出问题时，如何反向追溯到原始 tick？（Factor Lineage / 因子血缘）
- 证券基础信息、交易所日历、Corporate Action 由谁负责单点维护？（Master Data Management）
- 数据质量在 CI 流水线中由哪些断言保护？（Data Quality Gates）
- 不同热度数据保留多久？归档到哪里？（Retention & Archival）
- 本视图与 IA / AA / TA 边界在哪？（§10）

> **本视图主要读者**：量化研究员（理解 PIT/Survivorship 不会被回测撒谎）、数据工程师（落 schema 与 lineage 注册）、风控/合规（理解数据可信链）、AI 架构师（理解 factor → signal → order 的端到端血缘）。

---
