---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 包1——B0 决赛前 15 条 backlog 收尾（F01 落库 + F03 分桶判缺处置）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
session: st-flashbiz-20260918
---

# 包1 · B0 前 15 条收尾（P6 §2 状态表逐条终态）

判据真源：REG-VALM-001 exec_quality（validation_method_registry.yaml，20/40bp 土规线）+ BT-P0-003 frozen plan（threshold_status=frozen @2026-09-12）。
执行会话：st-flashbiz-20260918（2026-09-18 凌晨）。

## 1. 逐条终态表（15/15 全部收尾，零悬账）

| # | object_id | 节点 | P6 状态 | 本班终态 | 证据 |
|---|---|---|---|---|---|
| 1 | BT-P2-042 | TDM-E-L4 容器 | 已完考（随批） | **valid（已落库）** | run_id=VAL-20260918-015408，15 行全 valid |
| 2 | BT-P1-027 | E-L4-01 分批建仓 | 已完考 | **valid（已落库）** | 同上（slip 2.56bp，triggers 1467≥30） |
| 3 | BT-P1-028 | E-L4-02 买入时序 | 已完考 | **valid（已落库）** | 同上 |
| 4 | BT-P2-043 | E-L4-03 价格锚定 | 已完考 | **valid（已落库）** | 同上（decision_price 真基准） |
| 5 | BT-P2-044 | E-L4-04 资金分配 | 已完考 | **valid（已落库）** | 同上 |
| 6 | BT-P2-045 | E-L4-05 打板执行专项 | 已完考（代理受限） | **valid（代理口径已落库）+ 真分桶判缺处置完毕** | 分桶真考不可行→见 §3；plan 判据已冻结修订（backtest_backlog.yaml BT-P2-045） |
| 7 | BT-P2-046 | E-L4-06 执行算法 | 已完考（代理受限） | **valid（代理口径已落库）+ algo_id 缺口登记+判据口径修订** | 见 §3；known_data_gaps `bt_trade_log_attribution_fields_missing` |
| 8 | BT-P2-047 | E-L4-07 条件触发队列 | 已完考 | **valid（已落库）** | run 同上 |
| 9 | BT-P2-048 | E-L4-08 突破失败降级 | 已完考 | **valid（已落库）** | run 同上 |
| 10 | BT-P2-049 | E-L4-10 订单生命周期 | 已完考（代理） | **valid（已落库）** | 成交率轴不可评=既定披露口径，hit_ratio 空 |
| 11 | BT-P2-050 | E-L4-11 部分成交处理 | 已完考（代理） | **valid（已落库）** | run 同上 |
| 12 | BT-P2-051 | E-L4-12 订单预检 | 已完考 | **valid（已落库）** | run 同上 |
| 13 | BT-P2-052 | E-L4-13 执行容灾对账 | 已完考（代理） | **valid（已落库）** | reconciliation_differences 0 行不阻断 |
| 14 | BT-P2-053 | E-L4-14 成本反馈回写 | 已完考 | **valid（已落库）** | commission 1467/1467 实算闭环 |
| 15 | BT-P0-003 | 成本三件套（4 节点聚合） | 部分完考 | **E-L4-09/X-S2-01 过；P-P2-01/P-P2-03 存疑（insufficient_samples）→包2 披露件** | E-L4-09 随 L4 批落库；P-P2 两条=只出报告不改放行（Owner 指令） |

## 2. F01 台账落库（P6 交接包①，完成）

- 执行：`run_validation(batch='L4')` 非 dry——**run_id=VAL-20260918-015408，15 行 verdict 全 valid（slip_within_tolerance，significance=ok）写入 c1_backtest.node_verdict**；trailing 衰减巡检随批。
- 落库前快照（审计锚）：node_verdict 全表 41 pending + 2 valid；TDM-E-L4% 旧行 16 条（append-only 不删，前端按节点最新行渲染）。
- run 档案已 finalize：`data/backtest_artifacts/runs/VAL-20260918-015408/`（01_survey~verdict.md 七件齐；该目录 gitignore，档案只在盘）。
- SOP-B 护栏③ 冻结留痕核对：runner 土规 20bp（apply_soil_rules）与 BT-P0-003 plan.thresholds（slip_bp_valid=20.0/pending=40.0，frozen_by=st-backtest-20260912@2026-09-12）与 REG-VALM-001 verdict_mapping 三方同源一致，零平移。
- 验收（F01 机读判据）：`SELECT verdict, count() WHERE run_id='VAL-20260918-015408' GROUP BY verdict` → `[('valid', 15)]` ✓
- 回滚：append-only 铁律不删行；误判走新 run_id 覆盖节点最新态。

## 3. F03 分桶真考（P6 交接包③，判缺处置完成）

- 就绪核查（机读）：60 件 `data/backtest_artifacts/bt-*.json` trade_log 全量扫描——**order_type 无一非 market、algo_id 无一非空 → 分桶真考不可行（数据缺口，非工程量问题）**。
- E-L4-05（order_type 分桶）：按 F03 分桶脚本逻辑对全量 fill 复核，全部落 (market, na) 单桶——排板/限价桶独立出数的前提字段不存在；不编造，维持代理口径。
- E-L4-06（algo_id）：缺口登记 `src/zephyr/data/config/known_data_gaps.yaml` 条目 **bt_trade_log_attribution_fields_missing**（resolution_plan=归属 X 流验证批 TradeRecord 扩展，字段落地后新 fill 才可分桶，旧产物不回补）。
- 判据口径修订（批次决策点公开修订，SOP-B 护栏③）：backtest_backlog.yaml BT-P2-045/046 由 `plan: null` 填为冻结 plan——阈值引 REG-VALM-001 既定 20/40bp 零平移 + caliber_note 记录分桶字段前置与代理口径（frozen_by=st-flashbiz-20260918@2026-09-18；不改判定线，只登记真判据形态与代理前提）。

## 4. 边界与诚实清单

1. B0 15 条全部收尾；verdict 均为 D 后 4 交易日（09-10~09-15）窗口、11 个 walk-forward run 混 run 聚合口径（P6 §4 披露原样有效）。
2. P-P2-01/P-P2-03 存疑件未落台账行（涉钱配对结论=只出报告，见 biz2；F02 交接包注明可选落库，本班选择不落、留 Owner）。
3. 分桶真考待 TradeRecord 字段落地后对新 fill 重跑（F03 脚本就绪，判据同线）。
