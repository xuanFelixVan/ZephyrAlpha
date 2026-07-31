---
ttl: permanent
doc_type: architecture_view
---

# 交易决策架构视图能力定位书

> 版本：V1.0.0 | 2026-07-31
> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）
> 写法：大白话为主。变更历史见 git log。本文档只保留当前有效的设计规格和裁定结论。

> **文档责任范围**：本文档定义**交易决策架构视图**（07_）的能力定位、设计决策和裁定记录。
> 它是 decisiongraph 的业务流程视图，不是新图，不进四图对齐。
> 合并后覆盖：交易决策流程叙事（选股/买入/卖出/仓位/执行/对账 6 阶段）+ 四模式开关 + 应急保命降级。
> 不包含：决策节点的结构化定义（见 decision_graph_model.yaml）、决策节点实例数据（见 decisiongraph PostgreSQL）。

---

## 一、交易决策架构视图是什么？（一句话）

**交易决策架构视图是 decisiongraph 的业务流程视角——把决策节点按"交易动作"（选股→买入→卖出→仓位→执行→对账）串成"钱怎么赚"的完整流程，用大白话 + ASCII 框图呈现，供人类指挥 AI 用。**

它存在 `docs/02_enterprise_architecture/07_trading_decision_architecture/` 目录下（7 个 MD），由生成器 [generate_trading_flow_diagram.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_trading_flow_diagram.py) 从 decisiongraph (PostgreSQL) + [trading_flow_narrative.yaml](file:///d:/ZephyrAlpha/architecture_model/domain/trading_flow_narrative.yaml) 派生。

**和 06_decision_architecture 的区别**：
- 06_ 是**零件决策流**（按层/轨拆分的节点清单，回答"决策怎么分层"）
- 07_ 是**交易决策架构**（按业务流程串成的叙事，回答"钱怎么赚、每步做什么"）

---

## 二、它解决什么问题？

它解决 AI 开发和人类指挥的三个老毛病：

| 毛病 | 07_ 视图怎么治 |
|------|------------|
| **没有作战地图** — 人不知道整个交易流程长什么样 | 07_ 用 ASCII 框图画出选股→买入→卖出→仓位→执行→对账的完整链路，一眼看清 |
| **AI 不知道改哪里** — 人说"改买入流"，AI 不知道动哪些模块 | 07_ 每个流程步骤带 module_id 锚点，AI 能从 MD 定位→decision_node→module_id→代码文件 |
| **零件和装配脱节** — 06_ 只有零件清单，没有装配图 | 07_ 是装配图+故事线，06_ 是零件手册，两者互补 |

**本质**：让人类有一张"作战指挥图"，通过它指挥 AI 改量化系统。

---

## 三、它不是什么？（边界要画清楚）

| 不是这个 | 为什么不是 |
|---------|-----------|
| 新的全景图（第五图） | 07_ 是 decisiongraph 的视图，不是新图。全景图只有三个（depgraph/dataflowgraph/decisiongraph） |
| decisiongraph 的替代 | 07_ 从 decisiongraph 派生，decisiongraph 是真源。07_ 改了不影响 DB，DB 改了重跑生成器更新 07_ |
| 策略文档 | 07_ 只描述决策流程架构，不描述具体策略参数（策略参数在策略蓝图里） |
| 代码文档 | 07_ 不记录函数签名，只记录"这个流程步骤对应哪个 module_id" |
| 过度工程设计 | 07_ 主图只画实盘主链路（production 节点），过度工程（KAN/Mamba 等）进 candidate_module_registry，07_ 附录2 展示 |

---

## 四、它由哪几部分组成？

交易决策架构视图由三部分组成：

### 4.1 规则真源（YAML）

| 文件 | 内容 |
|------|------|
| [decision_graph_model.yaml](file:///d:/ZephyrAlpha/architecture_model/domain/decision_graph_model.yaml) §flow_stages | 6 阶段定义（stage_id/名称/映射layer/产出契约） |
| [trading_flow_narrative.yaml](file:///d:/ZephyrAlpha/architecture_model/domain/trading_flow_narrative.yaml) | 6 阶段叙事（大白话/ASCII框图/ai_directive/sub_flows/module_anchors）+ 横切层（四轨/共享信号/应急降级/四模式） |

### 4.2 架构真源（PostgreSQL）

| 表 | 字段 | 内容 |
|----|------|------|
| decision_nodes | flow_stage | 业务流程阶段标注（stock_selection/buy_flow/sell_flow/position_management/execution/reconciliation） |
| decision_nodes | design_maturity | production（主图）/ design（附录1·待施工） |

### 4.3 生成产物（07_ 目录，7 个 MD）

| 文件 | 内容 |
|------|------|
| trading_flow_index.md | 总览（四轨+6阶段+三态图例+指挥AI用法+共享信号注入） |
| 01_stock_selection.md | 选股6层漏斗 |
| 02_buy_flow.md | 买入决策流+四轨融合 |
| 03_sell_flow.md | 卖出八层架构 |
| 04_position_flow.md | 仓位裁决 |
| 05_execution_flow.md | 订单生命周期状态机 |
| 06_modes.md | 回测/Paper/Shadow/实盘 四模式开关 + 应急保命降级 |

---

## 五、数据源与真源链路

```
规则真源（YAML）                    架构真源（PostgreSQL）
┌─────────────────────────┐       ┌─────────────────────────┐
│ decision_graph_model.yaml│       │ decisiongraph            │
│   §flow_stages（6阶段）  │       │   decision_nodes         │
│ trading_flow_narrative   │       │     .flow_stage          │
│   .yaml（叙事）          │       │     .design_maturity     │
└───────────┬─────────────┘       └───────────┬─────────────┘
            │                                  │
            └──────────────┬───────────────────┘
                           ▼
                  generate_trading_flow_diagram.py
                           │
                           ▼
            ┌──────────────────────────────────┐
            │ 07_trading_decision_architecture/ │（派生产物）
            │   7 个 MD（人类视图）             │
            └──────────────────────────────────┘
```

**SSoT 铁律**：
- 改叙事 → 改 trading_flow_narrative.yaml → 重跑生成器
- 改节点 flow_stage → 用 apply_decisiongraph.py --set-flow-stage → 重跑生成器
- 禁止直接改 07_ MD（派生产物，会被生成器覆盖）

---

## 六、三态展示机制

07_ MD 内部按三态分层展示：

| 态 | 来源 | 展示位置 | 说明 |
|----|------|---------|------|
| 运营态（production） | decisiongraph DB | 主图 | 实盘主链路节点 |
| 设计态（design, approved） | decisiongraph DB | 附录1 | 通过四问过滤、待施工 |
| 候选库（deferred/rejected） | candidate_module_registry.yaml | 附录2 | 过度工程/超前设计，附四问结果 |

**治理合规**：过度工程不进 decisiongraph（四问过滤铁律），只进候选库。07_ 附录2 从候选库提取，按 `panorama_position.decisiongraph.target_layer` 归类到对应阶段章节。

---

## 七、与四图对齐的关系

- **不进四图对齐**：07_ 是视图不是图，和 application_flows.md 同待遇（PAN-BUILT-03 先例）
- **通过 module_id 天然锚定**：07_ MD 每个节点链回 decisiongraph + depgraph
- **panorama_registry 登记**：PAN-BUILT-21（decisiongraph 业务流程视图）

---

## 八、变更历史

- v1.0.0 (2026-07-31): 初版——07_ 视图建立。6 阶段 flow_stage + 叙事 YAML + 生成器 + 能力定位书 + PAN-BUILT-21 登记。对标草稿 v9.0 剥离过度工程，只留实盘主链路。
