---
ttl: task_bound
completes_when: 随战役归档
---

# 模拟盘日报 2026-09-22（判定台账渲染，生成于 09-23 晨）

> 真源=c1_backtest.sim_daily_report/sim_pocket_daily/sim_platform_journal（无第二真源）；
> 本日为回补定稿日：09-22 白天四步链未挂接（前日只挂日刊），09-23 凌晨回补+结算。

## 平台总览

| 项 | 值 |
|---|---|
| 日刊（收盘定稿档） | 47 钱包 / 总权益 44,490,280.84 / 事件 6 笔 |
| 数据新鲜度 | fresh=1（kline max=09-22） |
| 账本心跳 | ok=1 |
| degraded | 1（在册外钱包隔离哨兵：STR-AUTO-001, STR-MULTIFACTOR-001——FIX-2 卫兵上线前开户，存量处置呈 Owner） |

## 判定台账（plan 面）

| source | subject | posture/action | 结算 |
|---|---|---|---|
| plan_bridge | index:000300.SH | 震荡→S3_oscillation→**unexecutable**（无订单语义，如实记录） | posture_check=1.0 |
| plan_execute | SIM-PLAN-001 | none（无动作日，65,055 股持仓顺延） | no_action_position_unchanged=1.0（结算语义修正后） |

## E4 观察档（sim_observe 平面）

- 重放 44/48 成功（4 例数据面缺口如实留错：68cc 基本面列缺失 / 93aa 成分窗缺失 / 8664+e2e7 NaN 尾行被卫兵隔离）
- 44 钱包合计权益 50,583,474.52；持仓 16（7 只权益>名义本金）/ 空仓 28
- 信号分布：entry 5 / exit 2 / holding 11 / cash 26
- TOP5：CAND-5301c5d9d7c8（9.35M holding）/ CAND-9c0424f53fe4（1.87M entry）/ CAND-99873fd0bc17 / CAND-311220235636 / CAND-c72318f2da1c（均 ~1.0M）

## 结算

- 09-22 全部 48+ 行结算完成（evaluated_by=sim_settler），unresolvable=0
