---

module_id: DOCUMENT_CLASSIFICATION_STANDARD_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: '2026-04-07'

owner: 个人开发者

responsibility:

- 文档分类标准、分类体系、分类检查

layer: layer_10

standard_type: 专业量化机构文档

---

> **非真源声明（overlap）**：本文档为重叠副本/中间产物，仅用于追溯，不作为权威真源（canonical）。  

> **canonical_path**：`docs/09_AUDIT/STANDARDS/DOCUMENT_CLASSIFICATION_STANDARD.md`  

> **处置建议**：待真源确认后，保留为追溯或合并后删除；不得作为入口索引直接推荐。



```---



# 文档分类标准



> **核心职责**: 文档分类体系管理

> **职责边界**: 

> - ✅ 本文档负责：文档分类标准相关内容

> - ❌ 本文档不负责：其他模块内容



## 1. Layer层级分类



### Layer 0: 数据源层

- 数据源管理

- 数据接入

- 数据质量



### Layer 1: 数据质量层

- 数据清洗

- 数据标准化

- 数据验证



### Layer 2: 因子计算层

- 因子计算

- 因子分析

- 因子管理



### Layer 3: 策略开发层

- 策略开发

- 策略优化

- 策略回测



### Layer 4: 机器学习层

- 机器学习

- 模型训练

- 特征工程



### Layer 5: 组合优化层

- 组合优化

- 权重分配

- 组合构建



### Layer 6: 交易执行层

- 交易执行

- 订单管理

- 执行优化



### Layer 7: 风险管理层

- 风险管理

- 风险控制

- 风险评估



### Layer 8: 人机交互层

- 人机交互

- 界面展示

- 用户操作



### Layer 9: 研究创新层

- 研究创新

- 策略研发

- 技术探索



### Layer 10: 治理合规层

- 治理合规

- 规范管理

- 制度建设



### Layer 11: 战略决策层

- 战略决策

- 投资规划

- 资产配置



## 2. 文档类型分类



### 2.1 蓝图文档 (Blueprint)

- 架构设计

- 模块规划

- 技术方案



### 2.2 索引文档 (Index)

- 文档索引

- 导航导航

- 快速查找



### 2.3 流程文档 (Process)

- 操作流程

- 执行步骤

- 工作指南



### 2.4 标准文档 (Standard)

- 规范定义

- 质量要求

- 合规标准



### 2.5 报告文档 (Report)

- 分析报告

- 评估结果

- 审计记录



### 2.6 知识文档 (Knowledge)

- 知识库

- 经验总结

- 最佳实践



## 3. 文档状态分类



### 3.1 Active (活跃)

- 正在使用

- 持续更新

- 主要参考



### 3.2 Deprecated (弃用)

- 已过时

- 不推荐使用

- 待归档



### 3.3 Archived (归档)

- 已归档

- 历史参考

- 不再更新



## 4. 分类检查机制



### 4.1 Layer归属检查

```bash

python scripts/weekly_layer_check.py

```



### 4.2 类型分类检查

```bash

python scripts/check_document_type.py

```



### 4.3 状态分类检查

```bash

python scripts/check_document_status.py

```



## 5. 分类优化建议



### 5.1 定期审查

- 每月审查分类合理性

- 调整不合理的分类

- 优化分类标准



### 5.2 自动化分类

- 根据内容自动推断Layer

- 根据命名自动推断类型

- 根据更新频率自动推断状态



```---



**标准版本**: v1.0  

**最后更新**: 2026-04-07

