---
module_id: FACTOR_README_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---


# ic_reports/ - 因子IC验证报告

> 因子预测能力验证报告集中管理


## 目录说明

本目录存放**因子IC（Information Coefficient）验证报告**，用于评估单个因子的预测能力。


## 报告分类

| 类别 | 因子范围 | 文件名 |
|------|---------|--------|
| 趋势跟踪 | ALPHA_001-014 | ALPHA_001-014_趋势类_IC.md |
| 均值回归 | ALPHA_015-026 | ALPHA_015-026_均值回归类_IC.md |
| 价值 | ALPHA_027-037 | ALPHA_027-037_value_factors_IC.md |
| 成长 | ALPHA_038-047 | ALPHA_038-047_成长类_IC.md |
| 质量 | ALPHA_048-064 | ALPHA_048-064_质量类_IC.md |
| 动量 | ALPHA_065-075 | ALPHA_065-075_动量类_IC.md |
| 情绪 | ALPHA_076-087 | ALPHA_076-087_情绪类_IC.md |


## 报告模板

```markdown
# {因子类型} IC验证报告

## 因子列表
| 因子ID | 因子名称 | IC值 | IC分位 | 状态 |
| ALPHA_001 | MA5 | 0.15 | 60% | ✅ |

## IC统计
- 平均IC: 0.12
- IC标准差: 0.08
- IC胜率: 65%

## 相关性分析
[相关性矩阵]

## 结论
[验证结果]
```


## 相关文档

| 文档 | 说明 |
|------|------|
| [../01_METHODOLOGY/ic_analysis.md](../../01_METHODOLOGY/ic_analysis.md) | IC分析体系 |
| [../02_ALPHA_FACTORS_INDEX.md](../../02_ALPHA_FACTORS_INDEX.md) | 因子索引表 |


**版本**: 1.0 | **更新**: 2026-03-28
