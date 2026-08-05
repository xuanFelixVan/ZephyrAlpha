---
doc_type: audit_report
title: 四图对齐报告
version: "1.0"
status: active
date: 2026-08-05
owner: auto-generator
ttl: permanent
---

# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-08-05 04:28:36
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=938 / dataflow=1088 / decision=693 / blueprint=165
- 问题总数: 6
  - 孤儿（仅一图）: 5
  - 状态漂移（blueprint 缺 design_maturity）: 0
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 1

## 1. 孤儿节点（仅一图存在）

| module_id | graph | 名称 / Name | entity_name |
|---|---|---|---|
| MOD-H1-REDIS-HOT | dataflow | H1 Redis 热缓存 / H1 Redis Hot Cache | MOD-H1-REDIS-HOT |
| CFG-rule-enforcement-registry | decision | 规则执行注册表层 / Rule Enforcement Registry Layer | layer:CFG-rule-enforcement-registry |
| CFG-rule-registry-collection | decision | 规则注册表收集层 / Rule Registry Collection Layer | layer:CFG-rule-registry-collection |
| CFG-scripts-registry | decision | 脚本注册表层 / Scripts Registry Layer | layer:CFG-scripts-registry |
| CFG-test-suite-registry | decision | 测试套件注册表层 / Test Suite Registry Layer | layer:CFG-test-suite-registry |

## 2. 状态漂移（blueprint 缺 design_maturity 字段）

> 无状态漂移。

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

| module_id | graph | 名称 / Name | entity_name |
|---|---|---|---|
| MOD-H1-REDIS-HOT | dataflow | H1 Redis 热缓存 / H1 Redis Hot Cache | MOD-H1-REDIS-HOT |

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）
- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）
- 设计态孤立：评估设计态是否需要同步到另三图
