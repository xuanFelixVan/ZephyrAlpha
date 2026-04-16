---
module_id: KE-035
title: "数据质量控制系统架构"
category: best_practice
source_file: "docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_QUALITY.md"
source_git_deleted: true
original_path: "docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_QUALITY.md"
deleted_in_commit: "bd24db31c1887d2660d165af4cf25fcac210f1c6"
recovery_date: "2026-04-16"
extracted_date: "2026-04-16"
version: "1.0.0"
status: Active
layer: L01
owner: ZephyrAlpha-Owner
---

# 数据质量控制系统架构

## 核心内容摘要

数据质量控制系统确保进入量化分析的数据满足质量要求，防止"垃圾进，垃圾出"(GIGO)。系统定义了六个数据质量维度：完整性（数据无缺失）、有效性（数据在合理范围内）、一致性（数据格式统一）、时效性（数据及时更新）、准确性（数据正确无误）、去重性（无重复记录）。

系统采用Python dataclass实现核心类设计，包括`Severity`枚举（CRITICAL/WARNING/INFO三级严重程度）、`DataIssue`数据问题类（记录问题详情）、`DataQualityResult`质量检查结果类（含质量评分0-1）。每个维度都有对应的检查方法和修复策略。

## 关键设计要点

1. **质量评分机制**：基础分1.0，CRITICAL问题乘以0.5，WARNING问题乘以0.8，实现量化质量评估

2. **问题分类体系**：按严重程度分级，CRITICAL导致数据不可用，WARNING数据可用但需注意

3. **检查方法覆盖**：
   - 缺失值检测（完整性）
   - 有效性规则（有效性）
   - 格式校验（一致性）
   - 时间戳检查（时效性）
   - 合理性验证（准确性）
   - 重复检测（去重性）

4. **修复策略**：提供填充、删除、标记等多种修复方式，支持自动化修复流程

## 适用场景

- L01数据接入层的数据清洗模块实现
- 数据管道中的质量检查节点
- 数据仓库ETL流程的质量控制
- 实时数据流的质量监控

## 原始文件

- 恢复命令：`git show bd24db31c1887d2660d165af4cf25fcac210f1c6^:docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_QUALITY.md`
