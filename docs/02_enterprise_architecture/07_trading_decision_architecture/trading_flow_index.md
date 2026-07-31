---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
---

# 交易决策架构总览（07_ 视图）

> 版本：v1.0.0 | 2026-07-31
> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）
> 写法：大白话为主。本视图是 decisiongraph 的业务流程视图，不是新图。

## 这是什么？大白话讲交易决策架构

这份文档是**交易决策架构视图**——把 decisiongraph 里的决策节点按「交易动作」
（选股→买入→卖出→仓位→执行→对账）重新组织，串成一条「钱怎么赚」的完整流程。

和 [06_decision_architecture/](../06_decision_architecture/decision_index.md) 的区别：
- 06_ 是**零件决策流**（按层/轨拆分的节点清单，回答「决策怎么分层」）
- 07_ 是**交易决策架构**（按业务流程串成的叙事，回答「钱怎么赚、每步做什么」）

## 怎么用这份文档指挥 AI

1. 找到你要改的流程阶段（选股/买入/卖出/仓位/执行）
2. 看该阶段的「指挥 AI 提示」，知道改这个流程要动哪些模块
3. 用 module_id 锚点让 AI 定位到具体代码文件（链回 depgraph）
4. AI 改之前必须先查 decisiongraph 确认节点存在（防幻觉）

## 四轨并行架构

交易决策不是单条流水线，而是四条轨道同时跑，按优先级接管：
  ① 模型驱动轨（主力）—— L0数据→L1因子→L2信号→L3策略→L4风控，正常交易走这条
  ② 数据驱动轨（补充）—— 端到端 DL 信号，模型驱动轨信号不足时补充
  ③ 人工指令轨（干预）—— 人工买入/卖出/调仓/风控干预，优先级高于自动轨
  ④ 应急保命轨（兜底）—— 全系统降级到最简规则，仅执行卖出 + 硬编码上限
四轨的输出在 L3 策略组合层融合，按优先级仲裁。人工指令 > 模型驱动 > 数据驱动；
应急保命轨触发时压制所有其他轨。


## 共享信号注入层

选股、买入、卖出三个流程共享同一批信号源——不重复造信号。
信号工厂统一产出 Insight（方向/置信度/时间跨度），注入到：
  - 选股流：信号作为筛选漏斗的输入
  - 买入流：信号作为四轨融合的输入
  - 卖出流：信号反转作为卖出触发之一
信号仓位分离铁律：signal 节点不能直接连 order，必须经 portfolio_target 中转。


## 6 阶段业务流程

| 阶段 | 文档 | 运营态节点 | 设计态节点 | 产出 |
|---|---|---|---|---|
| [选股决策流](01_stock_selection.md) | 01_stock_selection.md | 0 | 0 | `candidate_pool` |
| [买入决策流](02_buy_flow.md) | 02_buy_flow.md | 0 | 0 | `buy_signal` |
| [卖出决策流](03_sell_flow.md) | 03_sell_flow.md | 0 | 0 | `sell_signal` |
| [仓位裁决](04_position_flow.md) | 04_position_flow.md | 0 | 0 | `target_position` |
| [执行](05_execution_flow.md) | 05_execution_flow.md | 0 | 0 | `executed_order` |
| [对账](?) | ? | 0 | 0 | `reconciliation_report` |

## 应急保命降级路径

当模型/策略/信号失效时，系统逐级降级保命：
  - L2 信号失效 → 硬编码均线信号
  - L3 策略失效 → 固定比例仓位
  - L4 风控失效 → 硬编码 10% 单票上限
  - 数据断流   → 仅执行卖出（不买入）
降级触发由 Kill Switch 熔断 + 数据健康监控驱动。


## 三态图例

- **运营态（production）**：实盘主链路节点，主图展示
- **设计态（design, approved）**：通过四问过滤、待施工，附录1展示
- **候选库（deferred/rejected）**：过度工程/超前设计，附录2展示（Phase C 从 candidate_module_registry 提取）

## 四模式开关

详见 [06_modes.md](06_modes.md)（回测/Paper/Shadow/实盘）

> 数据源：depgraph (PostgreSQL) + trading_flow_narrative.yaml
