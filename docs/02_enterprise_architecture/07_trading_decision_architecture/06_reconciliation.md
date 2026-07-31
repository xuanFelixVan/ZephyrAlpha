---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
flow_stage: reconciliation
---

# 对账

> flow_stage: `reconciliation` | 映射层: ['L4'] | 产出契约: `reconciliation_report`

## 大白话讲这个流程

对账是成交后的核对和持久化。
流程：fill → 合规检查 → 持仓更新 → 成交记录 → 对账。
  - 合规检查：成交是否符合合规规则（T+1/涨跌停/持仓比例）
  - 持仓更新：成交后更新持仓表
  - 成交记录：记录成交明细（价格/数量/时间/渠道）
  - 对账：和券商/交易所的成交数据核对，发现差异告警
对账是实盘的最后一道防线，确保系统持仓和真实持仓一致。


## 流程框图

```
fill（成交）
    │
    ▼
合规检查（T+1/涨跌停/持仓比例）
    │
    ▼
持仓更新 ──→ 持仓表 position
    │
    ▼
成交记录 ──→ 成交明细表
    │
    ▼
对账（vs 券商/交易所）──→ 差异告警

```

## 运营态节点（实盘主链路）

_（暂无已标定节点，待 Phase B 全量标定）_


## 指挥 AI 提示

改对账流时，先查 decisiongraph 里 flow_stage=reconciliation 的节点（compliance_check 类型）。
常见改动：加合规规则、改持仓更新逻辑、加对账校验项。
注意：对账差异必须告警，不能静默吞掉。


## 子流程

### 合规检查

成交是否符合合规规则。

模块锚点: `MOD-L04-001`

### 持仓更新

成交后更新持仓表。

模块锚点: `MOD-L05-001`

### 成交记录

记录成交明细。

模块锚点: `MOD-L05-001`

### 对账核对

和券商/交易所成交数据核对。

模块锚点: `MOD-L04-001`

## 附录1·待施工（设计态节点）

| node_id | 决策名称 | 节点类型 | layer | module_id | path |
|---|---|---|---|---|---|
| 166 | AI Compliance Validator AI合规验证 | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_01` |
| 167 | 决策溯源链 Decision Provenance Chain | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_02` |
| 168 | TraceCompleteness TC≥0.997 | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_03` |
| 169 | AI合规边界 Tier 1/2/3风险分级 | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_04` |
| 170 | Pre-Trade合规检查三模式 Pre-Trade 3-Mode Check | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_05` |
| 171 | Kill Switch <1秒响应 Kill Switch <1s Response | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_06` |
| 172 | 人类监督四层级 L0~L3 Human Oversight 4-Level | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_07` |
| 173 | AI决策可追溯性 AI Decision Traceability | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_08` |
| 174 | AI决策可解释性门控 AI Decision Explainability Gate | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_09` |
| 175 | 监管报告 Regulatory Report | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_10` |
| 176 | 法域冲突解决 CrossBorderReg Navigator | compliance_check | L4 | MOD-L04-001 | `decision/compliance/cmp_11` |


## 附录2·未来增强（候选库）

_从 candidate_module_registry.yaml 按 target_track 归类到本阶段；基础设施类候选（回测/仿真/灾备/死域）见 [总览](trading_flow_index.md) 跨阶段附录_

_（本阶段暂无候选模块）_

