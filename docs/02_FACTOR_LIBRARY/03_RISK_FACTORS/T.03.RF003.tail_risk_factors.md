---
module_id: RISK_TAIL_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 尾部风险因子

> 尾部风险因子用于衡量和管理极端市场情况下的损失风�?

---

## 风险度量因子

| 因子名称 | 计算方法 | 说明 |
|----------|----------|------|
| VaR(5%) | 5%分位数收益率 | 95%置信度下的最大损�?|
| CVaR | 期望损失 | 极端损失的平均�?|
| 最大回�?| Max(Drawdown) | 历史最大跌�?|
| 波动�?20�? | Std(Return_20d) | 短期波动 |
| 下行波动�?| Std(Negative_Return) | 负收益波�?|
| 偏度 | Skewness(Return) | 收益分布偏斜 |
| 峰度 | Kurtosis(Return) | 收益分布尖峰 |
| Gamma | 期权希腊�?| 期权风险 |

---

## 使用场景

| 场景 | 适用因子 |
|------|----------|
| 极端风险控制 | VaR, CVaR |
| 波动率策�?| 波动�? 下行波动�?|
| 收益分布分析 | 偏度, 峰度 |
| 期权对冲 | Gamma |

---

> **维护部门**: 清风量化研究�?
> **更新时间**: 2026-03-28