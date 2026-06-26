---
module_id: KE-3172
title: 10.1 边界四象限
category: documentation
ttl: permanent
---

# 10.1 边界四象限

10.1 边界四象限

| 视图 | 关心 | 不关心 | 与 DA 的接口 |
|------|------|-------|-------------|
| **02-IA** Information Architecture | `docs/` 21 抽屉、文档生命周期、frontmatter schema | 业务数据对象 | **零重叠**——IA 是"文档抽屉"，DA 是"业务实体"，两者完全正交 |
| **03-AA** Application Architecture | 14 层 src/、模块边界、ACL、扩展点 | 数据实体的字段定义 | DA 的实体被 AA 的层处理：L00 落 Tick/Bar、L02 算 FactorValue、L06 产 Order/Fill、L07 算 PnL/RiskMetric |
| **04-TA** Technology Architecture | 时序库选型、对象存储选型、调度器选型 | 数据实体本身有什么字段 | DA 给出"温度 × 节奏"分类，TA 据此选具体技术栈（DA 不指定 PostgreSQL 还是 ClickHouse） |
| **06-Security**（待建） | 字段级访问控制、PII 脱敏 | 数据怎么计算 | DA 给出 `classification` 标签，Security 据此设权限 |
| **09_data_platform/** 下属域 | 字段级 schema、SQL DDL、具体调度脚本 | 跨域数据原则 | DA 是"原则与契约"，09 是"schema 真源与执行" |
