---
ttl: task_bound
title: T0-CONDITIONAL-V2 作废声明（VOID）
sid: st-t0-matrix-20260924
created: "2026-09-24"
status: void
void_target: docs/_working/t0_matrix/t0_conditional_e4_v2_result.yaml
replacement: docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md（T0-CONDITIONAL-V3）
---

# 作废声明

`docs/_working/t0_matrix/t0_conditional_e4_v2_result.yaml`、`t0_conditional_e4_v2_pairs.csv`
与本目录下 `t0_conditional_v2_prereg_card.md` **作为作废证据原样保留，字节不改不删**，
任何后续判读**不得引用**其数值。

## 作废原因（承 V3 卡 §0.2 实测红证）

V2 卡 §4.1 的材料合格性判据只过滤**单笔记录格式**（timestamp 是否含时分），
未约束**配对来源身份**。而 `cost_trio_exam.build_pairs()` 的键=`(symbol, trade_date)` 无 run 维，
导致 60 个 `bt-*.json`（7 个策略族、32 个不同日志、39 件为同日志换 run_id 的逐字节重放）
被合并成同一"往返"：

- 全窗 pool 出 1,996 对，其中 **1,970 对的买侧 run 集与卖侧 run 集完全不相交**
  ⇒ 没有任何组合同时持有买卖两腿，往返在会计意义上不存在。
- gross_bp 最大 **+5,271bp=+52.7%**、|gross|>100bp 占 50.3% ⇒ 超 A 股单日涨跌停理论极限，
  那是两套回测执行模型对同一 symbol-day 的**报价分歧**，不是任何人捕获到的价差。
- V2 实测产物即体现该污染的后果：primary=0 / secondary=0 / control=28 /
  verdict=`STATE_GATE_NEVER_TRIGGERED`（28 对的 T-1 全部未过宏观门）。

## V2 中仍然有效、被 V3 继承的部分

1. **情绪门接线的正确性**：V2 §2.2 把情绪门数据源从注册定性为币圈面板的 `sentiment_panel`
   改指六段相位物化真源，该接线被 V3 全盘继承，且已被 v1 考件守卫实测触发
   （`FAIL: 情绪门历史已可用…按卡纪律作废重开`）。
2. **考窗起点** 2026-06-01（真源=第三方 frozen 卡 t0_regime §3）。
3. **三态门语义**（`allow / deny / unevaluable_day`，不路由日禁并入对照）与
   主考/副考/对照三集切分逻辑（V3 直接 import 复用 `t0_conditional_e4_v2_exam.split_gates`）。
4. **M-1 日内粒度过滤**（V3 保留为四判据之一）。

作废只因为**材料身份判据不完备**，与判据数值、门规则、六段接线无关——后三者零改动。
