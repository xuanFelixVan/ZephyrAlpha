---
module_id: DW-RISK-TEMPLATE
title: <主题> 风险登记簿
doc_type: register
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: YYYY-MM-DD
summary: 本登记簿覆盖 <主题>，记录已识别的风险、概率、影响、缓解策略与当前状态。
completeness: "unknown"

date: '2026-04-22'
ttl: permanent
template_for: risk-register
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
风险登记簿模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/d3_metadata/check_template_compliance.py <文档路径> --template risk-register
-->
<!--
REQUIRED_SECTIONS:
  s1: "1. 登记规则"
  s2: "2. 登记表"
  s3: "3. 优先级计算"
  s4: "4. 状态定义"
  s5: "5. 修订记录"
END_REQUIRED_SECTIONS
-->

# <主题> 风险登记簿

## 1. 登记规则

- 新增风险：按 `R-NNN` 编号追加到第 2 节登记表
- **不删除**已识别的风险，只标状态变化（open → mitigated → closed / accepted）

## 2. 登记表

| # | 风险描述 | 概率 | 影响 | 优先级 | 缓解策略 | 状态 | 登记日期 | 最后更新 |
|---|---------|------|------|-------|---------|------|---------|---------|
| R-001 | 示例 | 中 | 高 | P1 | ... | open | YYYY-MM-DD | YYYY-MM-DD |

## 3. 优先级计算

```
优先级 = 概率 × 影响
  P0 = 高 × 高
  P1 = 高 × 中 或 中 × 高
  P2 = 中 × 中
  P3 = 其他
```

## 4. 状态定义

| 状态 | 含义 |
|-----|------|
| open | 已识别，未处理 |
| mitigating | 正在执行缓解动作 |
| mitigated | 缓解动作完成，风险降低但未消除 |
| accepted | 决定接受此风险（无法/不值得缓解） |
| closed | 风险已消除 |

## 5. 修订记录

| 日期 | 说明 |
|------|------|
| YYYY-MM-DD | 初版 |
