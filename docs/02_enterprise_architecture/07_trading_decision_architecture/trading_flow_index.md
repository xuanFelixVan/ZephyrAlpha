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

## 总指挥图（一张图看全流程）

> 详见 [00_panorama.md](00_panorama.md)——全部决策节点按6阶段分层，单张 Mermaid 大图 + 可缩放 HTML。

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
| [选股决策流](01_stock_selection.md) | 01_stock_selection.md | 0 | 5 | `candidate_pool` |
| [买入决策流](02_buy_flow.md) | 02_buy_flow.md | 0 | 13 | `buy_signal` |
| [卖出决策流](03_sell_flow.md) | 03_sell_flow.md | 0 | 19 | `sell_signal` |
| [仓位裁决](04_position_flow.md) | 04_position_flow.md | 0 | 37 | `target_position` |
| [执行](05_execution_flow.md) | 05_execution_flow.md | 0 | 56 | `executed_order` |
| [对账](06_reconciliation.md) | 06_reconciliation.md | 0 | 11 | `reconciliation_report` |

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
- **候选库（candidate/deferred/rejected）**：过度工程/超前设计，附录2展示（从 candidate_module_registry.yaml 提取）

## 四模式开关

详见 [07_modes.md](07_modes.md)（回测/Paper/Shadow/实盘）

## 附录·跨阶段候选（基础设施类）

以下候选不归属任何交易流阶段（回测/仿真/灾备/死域等），共 **5291 条**（candidate×5283、deferred×5、rejected×3）。

> 完整清单见 `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`。

样例（前10条）：

| 候选ID | 名称 | 状态 | 优先级 | 卡在哪问 | 解决什么痛点 |
|---|---|---|---|---|---|
| CAND-SIGLEGACY-001 | D_SIGLEGACY 多策略引擎 | rejected | P2 | q3 | (已解决)多策略编排已由 D_PF_CORE PC-01 承担 |
| CAND-WFO-001 | Walk-Forward Optimizer / 滚动前进优化器 | deferred | P2 | q2 | 回测参数过拟合风险——单一全样本优化容易拟合历史噪声,实盘表现衰退 |
| CAND-PC-001 | Policy Compiler / 策略编译器 | rejected | P2 | q4 | 策略规则到检查器代码的翻译需自动化,避免手工编写检查器 |
| CAND-DR-001 | Offsite Backup / 异地备份 | rejected | P2 | q2 | audit 7.7 发现本地 restic 备份与主库同物理站点,不满足 3-2-1 备份原则的异地要求 |
| CAND-SIM-002 | Experiment Queue Scheduler / 实验队列调度 | deferred | P2 | q2 | 并发实验>10时,顺序执行导致等待时间长 |
| CAND-BT-001 | Backtest v2.0 Auxiliary Modules / 回测v2.0辅助模块 | deferred | P2 | q2 | 回测需批量调度/衰减监控/自动报告/结果缓存时,无对应辅助模块 |
| CAND-DAT-001 | DataFrame to Pydantic Migration / DataFrame迁移Pydantic | deferred | P2 | q2 | DataFrame无运行时类型校验,下游D_FACTOR消费端要求Pydantic强类型契约 |
| CAND-PFALLOC-001 | Min-Variance & Risk-Parity Rebalance Modes / 最小方差与风险平价再平衡模式 | deferred | P1 | none | 实盘组合分配只能用 equal_weight/signal_weight,无法执行最小方差/风险平价这两种基础量化... |
| CAND-HARVEST-0001 | Data Ingestion & Management 数据接入与管理 | candidate | P2 | pending | C 001：数据接入与管理 |
| CAND-HARVEST-0002 | Factor Factory 因子工厂 | candidate | P2 | pending | C 027：因子工厂（P0） |

> 数据源：depgraph (PostgreSQL) + trading_flow_narrative.yaml + candidate_module_registry.yaml
