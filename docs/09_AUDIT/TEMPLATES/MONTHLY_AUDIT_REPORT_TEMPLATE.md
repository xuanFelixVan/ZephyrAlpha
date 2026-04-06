---
module_id: MONTHLY_AUDIT_REPORT_TEMPLATE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 扩展功能、辅助模块
---
---
# 每月文档治理审计报告

> **核心职责**: 审计报告和审计记录
> **职责边界**: 
> - ✅ 本文档负责：审计报告和审计记录相关内容
> - ❌ 本文档不负责：其他模块内容


> **审计时间**: {audit_time}  
> **审计类型**: 每月审计 (Monthly Audit)  
> **审计范围**: 全系统所有文档  
> **审计执行者**: 自动化审计系统  

---

## 📊 审计概要

### 审计统计

| 指标 | 数值 |
|------|------|
| **审计文档数** | {total_docs} |
| **发现问题数** | {total_issues} |
| **合规率** | {compliance_rate}% |
| **审计耗时** | {duration}秒 |
| **处理速度** | {docs_per_second} 文档/秒 |

### 问题分布

| 问题类型 | 数量 | 占比 |
|---------|------|------|
| **YAML字段缺失** | {yaml_issues_count} | {yaml_issues_percent}% |
| **职责描述问题** | {responsibility_issues_count} | {responsibility_issues_percent}% |
| **Layer归属问题** | {layer_issues_count} | {layer_issues_percent}% |

---

## 🔍 详细审计发现

### 1. YAML完整性检查

**检查结果**: {yaml_completeness_result}

| 检查项 | 总数 | 完整 | 不完整 | 完整率 |
|--------|------|------|--------|--------|
| **YAML头部** | {yaml_total} | {yaml_complete} | {yaml_incomplete} | {yaml_completeness}% |

**详细问题列表**:

{yaml_issues_detail}

### 2. 职责清晰度检查

**检查结果**: {responsibility_clarity_result}

| 检查项 | 总数 | 清晰 | 不清晰 | 清晰率 |
|--------|------|------|--------|--------|
| **职责描述** | {responsibility_total} | {responsibility_clear} | {responsibility_unclear} | {responsibility_clarity}% |

**详细问题列表**:

{responsibility_issues_detail}

### 3. Layer归属正确性检查

**检查结果**: {layer_attribution_result}

| 检查项 | 总数 | 正确 | 错误 | 正确率 |
|--------|------|------|------|--------|
| **Layer归属** | {layer_total} | {layer_correct} | {layer_incorrect} | {layer_attribution}% |

**详细问题列表**:

{layer_issues_detail}

---

## 📈 合规性评估

### 合规性评分

| 评估项 | 目标值 | 实际值 | 达标状态 | 变化趋势 |
|--------|--------|--------|---------|---------|
| **YAML完整性** | 100% | {yaml_completeness}% | {yaml_completeness_status} | {yaml_trend} |
| **职责清晰度** | ≥90% | {responsibility_clarity}% | {responsibility_clarity_status} | {responsibility_trend} |
| **Layer归属正确性** | 100% | {layer_attribution}% | {layer_attribution_status} | {layer_trend} |
| **总体合规率** | ≥95% | {compliance_rate}% | {compliance_rate_status} | {overall_trend} |

### 月度趋势分析

{monthly_trend_analysis}

---

## 🎯 改进建议与行动计划

### 立即修复项 (24小时内)

{immediate_actions}

### 短期改进项 (1周内)

{short_term_actions}

### 长期优化项 (1个月内)

{long_term_actions}

---

## 📝 审计质量声明

### 审计局限性

1. **审计范围**: 本次审计覆盖全系统所有文档
2. **审计深度**: 本次审计为标准审计，包含YAML、职责、Layer三大检查
3. **审计方法**: 采用自动化脚本审计，可能存在误报

### 质量保证

1. **审计标准**: 符合专业量化机构文档治理标准v5.1
2. **审计工具**: 使用经过验证的自动化审计脚本
3. **审计报告**: 采用标准化模板，确保报告质量

### 后续审计建议

1. **下次审计时间**: {next_audit_time}
2. **审计重点**: 建议重点关注本次发现的问题修复情况
3. **审计范围**: 建议进行深度三层审计

---

**报告生成时间**: {report_time}  
**报告版本**: v1.0  
**下次审计时间**: {next_audit_time}