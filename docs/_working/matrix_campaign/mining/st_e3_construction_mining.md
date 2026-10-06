---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e3_construction —— E3 构造与翻译（SPM 80 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 想法→可回测代码的构造与翻译，主体=C4 翻译件族 35 条验收集 + 价值/选股策略翻译件群。
- 计数: 80 = 1 stage(partial) + 79 mech（built 78 / pending 1）。

## 1. 族内节点全清单

| 节点段 | 数 | 内容 | 状态 | module | 行 |
|---|---|---|---|---|---|
| FAC-E3 | 1 | 构造与翻译（stage） | partial | MOD-BT-041..075 | SPM:L277 |
| FAC-E3-M-001 | 1 | C4 翻译件族（35 条验收集） | built | MOD-BT-041..075 | SPM:L1523 |
| FAC-E3-M-002~004 | 3 | C3 试点：SVR 多因子(挂起)/MA 金叉死叉/zscore 均值回归 | built | MOD-BT-036/037/038 | SPM:L1534~1576 |
| FAC-E3-M-005~039 | 35 | C4 翻译 041~075（BIAS_QL 金叉…沪深300ETF 双均线，逐条验收集） | built | MOD-BT-041~075 一一对应 | SPM:L1576~2069 |
| FAC-E3-M-040~042 | 3 | 精选价值十强 / 恐慌反弹深度化 / _valuation_engine | built | MOD-BT-088/092/096 | SPM:L2069~2131 |
| FAC-E3-M-043 | 1 | C4 翻译 | built | MOD-BT-102 | SPM:L2131 |
| FAC-E3-M-044~046 | 3 | Slater 价值精选/精选35/价值55改进版 | built | MOD-BT-103/104/105 | SPM:L2145~2175 |
| FAC-E3-M-047~048 | 2 | 小市值高低波动 / 蛇皮走位小市值 | built | MOD-BT-130/156 | SPM:L2189~2203 |
| FAC-E3-M-049~061 | 13 | 价值族：PB破净高股息/低PE/低PB/高股息/PE+PB/中证500低PE/漂亮50/原文口径/向导式价值/中信低PB/超稳股息/高股息率/价值投资 | built | MOD-BT-157~172 | SPM:L2217~2399 |
| FAC-E3-M-062~075 | 14 | 向导式成长四门/五门、低估值低负债、ROE改善、PEG 族×4、业绩增长、大市值价值×2、菜场大妈、麦克连×2、新手五门 | built | MOD-BT-173~186 | SPM:L2399~2595 |
| FAC-E3-M-076 | 1 | 管线事件持久化与消费编排 | built | MOD-BT-190 | SPM:L2595 |
| FAC-E3-M-077 | 1 | 代码生成模型适配器——E3 翻译生成力 | **pending** | dir:_domain_ml_serve/codegen_model_adapter | SPM:L2626 |
| FAC-E3-M-078 | 1 | 签名特征抽取 | built | dir:_domain_factor/signature_feature_extractor | SPM:L2638 |
| FAC-E3-M-079 | 1 | C4 翻译共享引擎（**原 E4 误挂，2026-10-04 总筹归位 E3**） | built | MOD-BT-039 | SPM:L2650 |

段计数核对：1+1+3+35+3+1+3+2+13+14+1+1+1+1 = 80 ✓（mech 79）。

## 2. 接线现状与缺口判定

- 已接线：翻译件族 75+ 枚 built，是全图 built 密度最高的层；M-079 归位记录证明图内有纠错机制在运转（节点名自述 2026-10-04 归位）。
- 缺口：FAC-E3-M-077 代码生成模型适配器 pending——AI 生成→代码的自动化翻译力未接，现靠人工/半自动翻译。
- 可考性：E3 产物（翻译件）正是考卷的被考对象；C4 翻译件族与 E4 批测/考卷链路（MOD-BT-076 快筛入口，SPM:L2883）直连。
- 层内风险位：M-002 SVR 多因子名称自述"挂起"（SPM:L1534）——图内标注的挂起件，未计 pending（build_status 仍 built），状态语义不一致疑点（登记不判）。

## 3. 修复建议（一句话）

M-077 代码生成适配器补齐以关闭"AI 假说→代码"全自动最后一公里；M-002"挂起"字样与 build_status 的语义冲突由图侧统一（登记给图战役域）。

## 4. 交叉验证

- H9 §1.9 TDM-E-L9-D1（决策假设·因子组合挖掘）的产物进 E3 翻译——两图在此握手（TDM:L5646 ↔ SPM E1C/E3）。
- chief B1 §3.2"FACTORY 341 节点仅 17 边"——E3 层内 79 件无层内边，翻译件与考卷的依赖关系只存在于模块层不在图边层，矩阵考试读图时防误判"零依赖"。
- census 未触 E3 层内构成——本册为补充挖矿。
