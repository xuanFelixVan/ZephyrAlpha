---
blueprint_id: MOD-SIG-126
module_name: stock_relation_gnn
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/stock_relation_gnn.py
granularity: file
---

# MOD-SIG-126 stock_relation_gnn 蓝图（股票关系GNN基类）

> **module_id**: MOD-SIG-126 | **域**: D_ASHARE_SIGNAL | **优先级**: P2
> **来源**: B10-01830（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-049，A1 §29.6）
> 代码：`src/zephyr/signal_ashare/stock_relation_gnn.py`

## 0. 定位

StockRelationGNN基类：3种邻接图（供应链/同行业/概念共现词表闭合）+GAT/GCN两路聚合（注意力/度归一化均值聚合，纯numpy内存实现不引PyG）+邻居聚合特征接密度预测（注入predictor回调）+图规模护栏。canonical承接TESTB-034/046归并。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/signal_ashare/test_stock_relation_gnn.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
