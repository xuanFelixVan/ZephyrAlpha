---
module_id: WEEKLY_AUDIT_REPORT_TEMPLATE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 审计报告、合规检查

---
---

# 每周文档治理审计报告
> **核心职责**: 分析报告和评估结果
> **职责边界**: 
> - ✅ 本文档负责：分析报告和评估结果相关内容
> - ❌ 本文档不负责：其他模块内容


> **审计时间**: {audit_time}  
> **审计类型**: 每周审计 (Weekly Audit)  
> **审计范围**: 最近7天修改的文档  
> **审计执行者**: 自动化审计系统  

---

## 📊 审计概要

### 审计统计

| 指标 | 数值 |
|------|------|
| **审计文档数** | {total_checked} |
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

### 1. YAML字段缺失问题

**问题描述**: 以下文档缺少必填的YAML字段

| 文档路径 | 缺失字段 | 严重程度 |
|---------|---------|---------|
{yaml_issues_table}

**修复建议**:
- 使用 `scripts/add_yaml_headers.py` 批量添加缺失字段
- 手动检查并补充字段内容

### 2. 职责描述问题

**问题描述**: 以下文档的职责描述过短或缺失

| 文档路径 | 当前职责描述 | 问题描述 |
|---------|-------------|---------|
{responsibility_issues_table}

**修复建议**:
- 使用 `scripts/fix_responsibility_descriptions.py` 批量修复
- 参考职责描述模板，补充详细说明

### 3. Layer归属问题

**问题描述**: 以下文档缺少Layer归属或格式不正确

| 文档路径 | 当前Layer | 问题描述 |
|---------|----------|---------|
{layer_issues_table}

**修复建议**:
- 使用 `scripts/layer_attribution_check.py` 检查Layer归属
- 根据文档内容确定正确的Layer归属

---

## 📈 合规性评估

### 合规性评分

| 评估项 | 目标值 | 实际值 | 达标状态 |
|--------|--------|--------|---------|
| **YAML完整性** | 100% | {yaml_completeness}% | {yaml_completeness_status} |
| **职责清晰度** | ≥90% | {responsibility_clarity}% | {responsibility_clarity_status} |
| **Layer归属正确性** | 100% | {layer_attribution}% | {layer_attribution_status} |
| **总体合规率** | ≥95% | {compliance_rate}% | {compliance_rate_status} |

### 风险评估

| 风险等级 | 问题描述 | 影响范围 | 优先级 |
|---------|---------|---------|--------|
{risk_assessment_table}

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

1. **审计范围**: 本次审计仅覆盖最近7天修改的文档
2. **审计深度**: 本次审计为快速审计，未进行深度内容分析
3. **审计方法**: 采用自动化脚本审计，可能存在误报

### 质量保证

1. **审计标准**: 符合专业量化机构文档治理标准v5.1
2. **审计工具**: 使用经过验证的自动化审计脚本
3. **审计报告**: 采用标准化模板，确保报告质量

### 后续审计建议

1. **下次审计时间**: {next_audit_time}
2. **审计重点**: 建议重点关注本次发现的问题修复情况
3. **审计范围**: 建议扩大审计范围，覆盖更多文档

---

## 📎 附录

### A. 审计工具列表

| 工具名称 | 路径 | 功能 |
|---------|------|------|
| 每周审计脚本 | `scripts/weekly_audit.py` | 自动化每周审计 |
| YAML修复脚本 | `scripts/add_yaml_headers.py` | 批量添加YAML字段 |
| 职责修复脚本 | `scripts/fix_responsibility_descriptions.py` | 批量修复职责描述 |
| Layer检查脚本 | `scripts/layer_attribution_check.py` | 检查Layer归属 |

### B. 参考标准文档

- [专业文档治理审计指南](../TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
- [文档治理审计检查清单](../TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)
- [审计质量标准v5.1](../STANDARDS/AUDIT_STANDARDS_v5.1.md)

### C. 术语表

| 术语 | 定义 |
|------|------|
| **YAML头部** | 文档开头的元数据部分，包含module_id、version等字段 |
| **职责描述** | responsibility字段，描述文档的核心职责 |
| **Layer归属** | layer字段，标识文档所属的系统层级 |
| **合规率** | 符合标准的文档数占总文档数的比例 |

---

**报告生成时间**: {report_time}  
**报告版本**: v1.0  
**下次审计时间**: {next_audit_time}
