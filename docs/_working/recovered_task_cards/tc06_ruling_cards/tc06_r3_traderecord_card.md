---
ttl: task_bound
completes_when: Owner 点单后转 archived
---

# TC-06 R3 裁定卡——TradeRecord 扩展立项（基线修正后呈报，禁自裁）

> 这是什么：回测产物 TradeRecord 缺 algo_id/order_type 真实枚举，策略归因到引擎执行层
> 断链。为何要 Owner 点单：挂哪个验证批=排班权。基线已按 09-21 实况修正（原判据件已灭失）。

## 修正后的基线（本班复核 tc_06 卡 A 级取证）

- TradeRecord=src/zephyr/backtest/io/backtest_result_sink.py:70 附近：已有
  decision_price/order_type 字段位，**无 algo_id**。
- 最新产物实态：order_type 恒 market、algo_id 全空——引擎产侧根本没有第二枚举值，
  字段位是摆设。
- 原判据件 F03 随 .runtime/tmp/exp/ 整棵消失（tmp 被清），**不可再生自 tmp**；
  判据重建源=docs/_working/kimi_audit/lane_reports/P6.md 判据节+known_data_gaps
  resolution_plan 节（文本完备）。
- 病根登记：不可再生判据落 tmp 是本次悬空的直接原因——重建件必须落 docs 或 scripts。

## 工作量构成（若批）

- 引擎产侧真实 order_type 枚举（限价/市价/条件单真实落字段）+algo_id 贯通
  （策略→引擎→成交记录三层）。
- 建议落点：判据件落 docs/_working/kimi_audit/lane_reports/（禁 tmp），代码随 X 流验证批。

## 选项

| 选项 | 内容 | 理由 |
|---|---|---|
| A（建议） | 挂 X 流验证批（下一次验证类施工顺路做） | 归因链缺口在每次策略考试都复利放大概率误判，早接早收益；单独立项工量不值 |
| B | 单独立项施工 | 归因链独立优先级最高时选 |
| C | 挂起不修 | 仅当 algo_id 由上游更高优先级重构（如 pf_alloc 车道）顺路覆盖时才成立 |

## 边界

- 本卡零代码改动；R2/R4 两卡同批呈报，裁定互相独立。
