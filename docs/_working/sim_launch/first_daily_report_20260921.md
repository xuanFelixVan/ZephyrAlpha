---
ttl: task_bound
completes_when: 首日样张被日常日报流程替代后归档
---

# 模拟盘日报样张 2026-09-21（首日）

> 数据层=c1_backtest.sim_daily_report（判定/结算分离）；本样张由台账行渲染，判定列=当日，结算列=已回填

## 一、平台总览

| 口径 | 钱包数 |
|---|---|
| sim_daily | 4 |
| sim_observe | 5 |

- 事件数（sim_trade_log 当日）: 4
- 行情新鲜度: kline_index(000300) max=2026-09-21 OK（FIX-1 时点感知后首绿）
- 在册外钱包哨兵: STR-AUTO-001 / STR-MULTIFACTOR-001（SSOT 卫兵生效后不再续开户，存量处置呈 Owner）

## 二、钱包明细

| 策略 | 口径 | 权益 | 信号 |
|---|---|---|---|
| STR-AUTO-001 | sim_daily | 1,000,000.00 | open |
| STR-E-TIMING-001 | sim_daily | 1,000,000.00 | open |
| STR-MULTIFACTOR-001 | sim_daily | 1,000,000.00 | open |
| STR-VREV-025 | sim_daily | 1,000,000.00 | cash |
| CAND-06d4cf3d7dcc | sim_observe | 999,262.61 | holding |
| CAND-091fee38cd01 | sim_observe | 1,000,000.00 | cash |
| CAND-12286499cb19 | sim_observe | 1,000,000.00 | cash |
| CAND-14d3e787ea4b | sim_observe | 1,000,000.00 | cash |
| CAND-1970782c2adb | sim_observe | 1,000,000.00 | cash |

## 三、判定台账（plan 桥/E4 观察档/平台）

| 来源 | 对象 | 姿态/信号 | 结算方法 | 结算分 |
|---|---|---|---|---|
| e4_replay | CAND-06d4cf3d7dcc | 目标仓位 1.0（holding） | replay_consistent | 1.0 |
| e4_replay | CAND-091fee38cd01 | 目标仓位 0（cash） | replay_consistent | 1.0 |
| e4_replay | CAND-12286499cb19 | 目标仓位 0（cash） | replay_consistent | 1.0 |
| e4_replay | CAND-14d3e787ea4b | 目标仓位 0（cash） | replay_consistent | 1.0 |
| e4_replay | CAND-1970782c2adb | 目标仓位 0（cash） | replay_consistent | 1.0 |
| plan_bridge | index:000300.SH | unexecutable（实际场景 S1_attack） | None | None |
| platform | platform | 心跳 1 新鲜 1 | heartbeat_check | 1.0 |

## 四、丁线日计划接电口径（披露）
- 计划 MOD-PLAN-030 三场景与盘中五态部分映射：防御→S2 可机械执行为空仓；进攻/震荡动作无订单语义，如实记 unexecutable，待 Owner 批订单映射后扩。
- 09-21 实际归类=S1_attack（进攻），计划姿态=不可执行（无订单映射），结算 posture_check=1.0（口径自洽）。
