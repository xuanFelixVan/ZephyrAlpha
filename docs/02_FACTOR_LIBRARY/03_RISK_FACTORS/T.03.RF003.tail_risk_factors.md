---
module_id: FACTOR_DOC_001
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

# 尾部风险因子

> 尾部风险因子用于衡量和管理极端市场情况下的损失风险

---

## 风险度量因子

| 因子名称 | 计算方法 | 说明 |
|----------|----------|------|
| VaR(5%) | 5%分位数收益率 | 95%置信度下的最大损失 |
| CVaR | 期望损失 | 极端损失的平均值 |
| 最大回撤 | Max(Drawdown) | 历史最大跌幅 |
| 波动率(20日) | Std(Return_20d) | 短期波动 |
| 下行波动率 | Std(Negative_Return) | 负收益波动 |
| 偏度 | Skewness(Return) | 收益分布偏斜 |
| 峰度 | Kurtosis(Return) | 收益分布尖峰 |
| Gamma | 期权希腊值 | 期权风险 |

---

## 使用场景

| 场景 | 适用因子 |
|------|----------|
| 极端风险控制 | VaR, CVaR |
| 波动率策略 | 波动率, 下行波动率 |
| 收益分布分析 | 偏度, 峰度 |
| 期权对冲 | Gamma |

---

> **维护部门**: 清风量化研究部
> **更新时间**: 2026-03-28