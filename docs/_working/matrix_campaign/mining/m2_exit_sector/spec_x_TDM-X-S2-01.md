---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-09 | TDM-X-S2-01 执行方式路由

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写，只考日级投影子集）
- 开源依据: qlib TopkDropout 的卖出清册=持仓中跌出 topk 者卖出+最差 n_drop 强制换出（GitHub
  Issue #828 证实换手不对称语义）——"按紧迫度/仓位切分卖出批次"在向量化框架的等价物=
  卖出日的权重路径切分。真源: `config/trading_decision_map.yaml#TDM-X-S2-01`（D70 流动性三查/D95 豁免）

## 1. 机制定义与考卷切分

TDM 路由表：紧迫度>0.8 或小仓(<2%)→一次性市价；中等紧迫+大仓→分批（3 批×1/3，间隔 5 分钟）；
不急+流动性差→尾盘集中；隔夜风险单→竞价挂跌停价逃命。卖出前三查：单笔≤买一档挂单量 /
日量×10% 参与率 / 持仓市值÷20日均额>1% 禁市价。

考卷可考子集（日级投影）：
- **一次性 vs 分批**：分批=连续 3 个交易日各卖 1/3（5 分钟间隔降维为日间间隔——失真如实披露）；
- **参与率帽**（D70 第二查）：`order_shares / day_shares ≤ 10%` 硬顶（INV-UNIT-001 口径，
  分子分母同纲"股"）；
- **市值/均额比>1% 禁市价**：映射为该标的卖出成交价加惩罚滑点档（或递延至次日）。

不可考：5 分钟批次间隔、买一档挂单量、IS 急卖 λ 曲线、ICEBERG 随机化、恐慌拦截 30 分钟窗
（负结果 #2）。

## 2. 计算式

```
notional_i = w_exit[t,i] × portfolio_nav
route_i    = 一次性  if urgency>0.8 or notional_i < 2%×nav
             分批3日 if 0.5<urgency≤0.8
             递延+惩罚 else
参与率闸    = sell_shares_{t,i} ≤ 0.10 × volume_{t,i}      # 超=当日卖不完→顺延次日（T+1 天然兼容）
```

## 3. 向量化实现要点

顺延递延=权重路径行循环（残余仓 w 带到 t+1）——与 X-S1-02 同循环体合并（一次循环完成
触发+路由+顺延），不新增独立循环。参与率闸=逐元素 min。

## 4. 引擎接法（M 级）

并入 `apply_stop_family` 行循环的出口段；schema 维 `X_route=[off, one_shot, scaled_3d]`。
框架在册配套（不进考卷、供 T3c 模拟盘考）：matching_engine ADV 五分位滑点腿（INV-COST-LEGS）
+参与率冲击语义（INV-UNIT-001）。

## 5. 考法（T0 口径声明）

依赖仓级行循环：**激活即 T3b-T0 强制重标定 per_point_seconds（禁用 0.53s/格口径），
fail-closed**。分批 3 日档与 D1_rebalance_freq 交互（调仓日本身有卖出）——同日合并卖出的
归属审计进 X-FLOW 列，防双计。

## 6. 数据列名

`c1_market.kline_daily`：volume, amount（股数参与率分子分母同纲，INV-UNIT-001）。
