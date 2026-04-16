---
module_id: KE-015
title: "数据质量监控：实时完整性/准确性/时效性/一致性检查"
category: blueprint_decision
source_file: "docs/01_FRAMEWORK/DATA_QUALITY_MONITORING_BLUEPRINT.md (deleted in git history)"
extracted_date: "2026-04-16"
version: "1.0.0"
status: Active
layer: L04
owner: ZephyrAlpha-Owner
source_git_deleted: true
original_path: "docs/01_FRAMEWORK/DATA_QUALITY_MONITORING_BLUEPRINT.md"
deleted_in_commit: "d73e28c0c868b5a5101f01882e76789ed748c830"
recovery_date: "2026-04-16"
---

# 数据质量监控设计

## 核心定位

从 git 历史恢复的文档定义了数据质量监控的完整架构，实现专业机构级的数据质量管理。

## Module ID
- `DATA_QUALITY_MONITORING_FRAMEWORK_001`
- Layer 4 (机器学习层)

## 专业机构参考模型

- **Bridgewater Data Quality**: 桥水基金数据质量管理
- **Two Sigma Data Governance**: Two Sigma 数据治理
- **Citadel Data Validation**: Citadel 数据验证

## 核心职责

### 1. 实时数据质量检查
- **完整性检查**: 检查数据是否完整，无缺失值
- **准确性检查**: 检查数据是否准确，无异常值
- **时效性检查**: 检查数据是否及时，无延迟
- **一致性检查**: 检查数据是否一致，无冲突

### 2. 数据质量评估
- **质量评分**: 对数据质量进行评分
- **质量报告**: 生成数据质量报告
- **质量趋势**: 分析数据质量趋势
- **质量告警**: 数据质量问题告警

### 3. 数据质量改进
- **问题定位**: 定位数据质量问题
- **根因分析**: 分析数据质量问题根因
- **改进建议**: 提供数据质量改进建议
- **效果验证**: 验证改进效果

## 技术实现要点

### 数据质量维度
| 维度 | 检查内容 | 阈值 |
|------|---------|------|
| **完整性** | 缺失值比例 | < 5% |
| **准确性** | 异常值比例 | < 1% |
| **时效性** | 数据延迟 | < 5分钟 |
| **一致性** | 冲突记录比例 | < 0.1% |

### 开源方案
- **Great Expectations**: 数据验证框架
- **Deequ**: AWS 开源数据质量库
- **Apache Griffin**: 数据质量解决方案

## 个人量化系统适用性

### 最小可行方案
1. **基础检查**: 检查价格数据是否缺失
2. **异常检测**: 检测价格异常波动
3. **延迟监控**: 监控数据延迟
4. **简单报告**: 生成数据质量报告

### 实施建议
- **工具**: Great Expectations（功能全面）
- **范围**: 重点监控价格、成交量数据
- **频率**: 每日检查一次
