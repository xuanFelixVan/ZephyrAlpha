---
module_id: FACTOR_IC_REPORTS_IC_001_L02_README
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 说明文档
applicable_scope: 全系统
compliance_level: 专业标准
---



# ic_reports/ - 因子IC验证报告

> 因子预测能力验证报告集中管理


## 目录说明

本目录存�?*因子IC（Information Coefficient）验证报�?*，用于评估单个因子的预测能力�?


## 报告分类

| 类别 | 因子范围 | 文件�?|
|------|---------|--------|
| 趋势跟踪 | ALPHA_001-014 | ALPHA_001-014_趋势类_IC.md |
| 均值回�?| ALPHA_015-026 | ALPHA_015-026_均值回归类_IC.md |
| 价�?| ALPHA_027-037 | ALPHA_027-037_value_factors_IC.md |
| 成长 | ALPHA_038-047 | ALPHA_038-047_成长类_IC.md |
| 质量 | ALPHA_048-064 | ALPHA_048-064_质量类_IC.md |
| 动量 | ALPHA_065-075 | ALPHA_065-075_动量类_IC.md |
| 情绪 | ALPHA_076-087 | ALPHA_076-087_情绪类_IC.md |


## 报告模板

```markdown
# {因子类型} IC验证报告

## 因子列表
| 因子ID | 因子名称 | IC�?| IC分位 | 状�?|
| ALPHA_001 | MA5 | 0.15 | 60% | �?|

## IC统计
- 平均IC: 0.12
- IC标准�? 0.08
- IC胜率: 65%

## 相关性分�?
[相关性矩阵]

## 结论
[验证结果]
```


## 相关文档

| 文档 | 说明 |
|------|------|
| [../01_STANDARDS/IC_ANALYSIS.md](../../01_STANDARDS/IC_ANALYSIS.md) | IC分析体系 |
| [../02_ALPHA_FACTORS_INDEX.md](../../02_ALPHA_FACTORS_INDEX.md) | 因子索引�?|


**版本**: 1.0 | **更新**: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
