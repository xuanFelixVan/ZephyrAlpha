---
ttl: task_bound
doc_type: report
title: 状态层历史回放深窗·执行报告（985 日全窗零失败）
created: 2026-09-24
sid: st-pipeline-final-20260924
lane: sector_line
status: done
---

# 状态层历史回放深窗·执行报告

## 结论

**深窗回放全窗落地：968/968 日零失败**（3 日烟测 + 965 日全窗），`c1_market.sector_state` 从 7,973 行/17 日（活值）增至 **425,787 行/985 日**（2022-09-01→2026-09-23 全骨架）。

## 对拍两轮（案卷完成判据）

| 轮次 | kline_sector_880 链 hash | 判定 |
|---|---|---|
| 回放前 | `710fe24490fbfe29dcbf90daf5f53904883add86782492bcd6cc6663f440ddd0` | 与冻结 manifest MATCH |
| 回放后 | 同上（逐位不变） | MATCH——880 表只读不变式成立 |

state 链由 `011d4528…`（活值快照）演进为 `8d8f95ce…`（含回放行）=设计内变化（日期不相交方案：回放只写活值 17 日窗之外日期，键空间零冲突）。

## 执行参数

- 驱动：`.runtime/tmp/pipeline_final/replay_deep_window.py`（零改公式，逐日调 `run_close_final(T)`，落地源=st-secbuild 20885a28f2 批的 sector_state_pipeline.py）
- 窗口径：板数≥367 的 985 日（深度案卷 §2 修正版），活值已有行逐日跳过（读前判重）
- 节流：逐日 0.3s；失败熔断阈值 30（未触发）

## 回放后 NULL 普查（与案卷 §1 预测一致）

| 列 | NULL | 判读 |
|---|---|---|
| capital_score | 425,787/425,787 (100%) | 该轴活值从未落值，回放如实产 NULL（案卷 §1 同判） |
| strength / net_inflow_pct | 406,185 / 406,494 | 早期日期缺 limit_up_pool/money_flow 原料（原料窗 17/45 日的回放侧体现） |
| momentum_pct | 2,175 | 价轴主判面近全覆盖（985 日窗有效） |

## 边界与移交

- `stage='pre_open'` 不回放（案卷 §3 T1：不可历史驱动），`sector_preference` 不写（run_pre_open 副表）
- T2 六段情绪=INSUFFICIENT 收口维持；D2 双轴主判悬于情绪真值窗 ≥120 日（v1 §F.3 预承诺，冻结卡 v2 已注记）
- GPU 板块条件矩阵输入包（案卷 §6）的物化可基于本回放面开工
