---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-20
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-20 竞价命中判定（日内唯一带墙钟窗闸的段）

## 1. 定义

dloop 盘中族段 `auction_hit`：10:00 判定（MOD-PLAN-015），墙钟窗闸限 10:00–10:30（非排班槽，代码内窗闸）；窗是「走势数据是否已闭合」的判据，判定输入全部以数据时间戳为界（PIT 语义）。只被 16:45 圈或人工逃生口调用→簿 07 判「自动圈下恒在窗外=结构性失效」。决策问题：窗闸在自动圈下开过吗？窗外 skipped 与窗内命中在这张图上能区分吗？

地图在册态：wiring=unwired_slot_hollow（我段 4 个之一）、build=partial、red_reason=unwired、window_gate_dead_under_auto_loop=true、自动圈下 0 拍（恒 skipped）。

**本矿代码新证（2026-10-15 实核）**：`src/zephyr/plan_engine/daily_loop_master_switch.py:343-369` 已落 **EXEC-3 治本（2026-10-04，针对本格结构性失效，fig13 簿09）**——≥10:30 回看补判照常落库（late_eval 留痕，判定口径不变），<10:00 数据未闭合仍 skipped；幂等=prediction_log 内容 hash 保首条。即 16:45 圈调用现已能产出 late_eval 记录，地图「恒 skipped」红态滞后于代码治本（该文件工作树另有他会话在途未提交修改，本矿不判罚不代修）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | D13-11 竞价快照+走势窗数据（SQL 恒 ≤trend_window_end 10:00，PIT 界） | `src/zephyr/plan_engine/daily_loop_master_switch.py:344-347`（PIT 语义 docstring 实核）；`src/zephyr/plan_engine/auction_hit_recorder.py`（record_auction_hit） |
| 输出面 | 竞价命中记录（窗内 hit / 窗外 late_eval 补判，幂等 hash 保首条） | `daily_loop_master_switch.py:357-369`（实核：late_eval=True 落库路径） |
| SSOT 真源 | 图13 节点契约（行 1611-1678）+ 簿 07 §1.4 段 11 + EXEC-3 治本注 | `config/trading_day_cycle_map.yaml#D13-20`；`docs/_working/map_build/fig13_daycycle/07_dloop十六段解剖.md`；daily_loop_master_switch.py:348-351（治本 docstring） |
| 代码模块 | _stage_auction_hit 段+窗闸常量（10:00-10:30）+recorder | `src/zephyr/plan_engine/daily_loop_master_switch.py:75`（_AUCTION_WINDOW 实核）、`:343`（段）、`:294`（地图锚） |
| 门禁约束 | 墙钟窗是数据闭合判据非排班约束；fail-open 留痕（与 position_checkup 窗闸同款）；禁伪造持仓/判定数据 | `daily_loop_master_switch.py:275`（fail-open 注释）；`config/trading_day_cycle_map.yaml#D13-20` gap_refs A4 |
| 自动化触发 | mechanism=C_inprocess_stage（dloop_stages=[auction_hit]）；declared=dloop 段内窗闸；observed=自动圈下 0 拍（恒 skipped，治本前口径）；in_phase_stages.auction_hit=true | `config/trading_day_cycle_map.yaml#D13-20` cadence_zh/machine_facts.dloop_facts；feedback_loops D13-32→D13-20 边 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 竞价与走势数据边界（PIT）在 docstring 钉死 |
| 输出面 | warn | 治本后 late_eval 路径在位，但治本后首个交易日的落库读数未见复判（地图态停在治本前） |
| SSOT 真源 | warn | 地图 red 态/window_gate_dead_under_auto_loop=true 滞后于代码 EXEC-3 治本（两处不同步） |
| 代码模块 | pass | 段+窗闸+recorder 实存实核 |
| 门禁约束 | pass | PIT 语义+fail-open 留痕+幂等三件在位 |
| 自动化触发 | warn | 驱动关系存在（16:45 圈）但产出形态已从「恒 skipped」变「late_eval 补判」，observed 口径待复测 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：**unwired_slot_hollow 5 个之一**（benchmark:A4 窗内应产 1 拍实产 0）。
- 建议：①下一交易日复跑观测 late_eval 落库后，回写图13 节点态（unwired_slot_hollow→partial/wired）与 skeleton 🔨/⬜ 状态——本矿只登记证据不改图（热文件纪律）；②若产品语义要求「窗内实时判定」而非「收盘后回看」，需 Owner 裁定是否给 auction_hit 配 10:00-10:30 的真实盘中触发器（当前 dloop_post 16:45 是唯一自动圈）。
