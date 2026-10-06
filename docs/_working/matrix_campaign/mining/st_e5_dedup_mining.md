---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e5_dedup —— E5 协同去重（SPM 5 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 新考过的策略与台账既有策略做相关性/同源去重，防同一阿尔法重复入库。
- 计数: 5 = 1 stage(built) + 4 mech（全 built，**全图唯一零缺口层**）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E5 | 协同去重（stage） | built | MOD-BT-086 | SPM:L330 |
| FAC-E5-M-001 | 策略协同去重器 | built | MOD-BT-086 | SPM:L3780 |
| FAC-E5-M-002 | ④ 差异报告组装 | built | MOD-BT-024 | SPM:L3795 |
| FAC-E5-M-003 | 信号去重 | built | dir:_domain_signal_quality/signal_dedup | SPM:L3811 |
| FAC-E5-M-004 | 协同去重基准因子配置 | built | cfg:synergy_dedup | SPM:L3823 |

## 2. 接线现状与缺口判定

- 已接线：去重器+差异报告+信号级去重+基准配置四件套齐；配置真源 cfg:synergy_dedup。
- 缺口：无（本层 built 5/5）。可考性：工厂内部门，不进回测考卷；其执法效果体现在 E6 台账（同源策略拦截率）——效果审计=not_mined（需台账统计，超本车道预算）。

## 3. 修复建议（一句话）

零缺口层无需修复；唯一建议=对 synergy_dedup 配置做一次年度阈值复核（治理节奏项，非缺口）。

## 4. 交叉验证

- TDM 侧无同名环节（TDM 决策图不管工厂内务）——E5 是纯工厂域层。
- 宪法 RULE-CLONEGUARD（extract 级克隆无逃生）是代码层去重纪律，与 E5 策略层去重正交互补。
- chief B1 ENV-17 计数一致；census 无交集（补充挖矿完成层内构成）。
