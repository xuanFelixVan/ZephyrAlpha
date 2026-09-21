---
ttl: task_bound
rule_form: data
verifiability: manual
title: 裁定书草案——S4-R2：risk_layer_orchestrator 盘中定时对账 Timer 改事件触发+兜底
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
status: 待 Owner 签
---

# 裁定书草案 S4-R2：盘中对账 Timer 违规改造

## 现状（含证据锚点）

宪法红线"永久系统四要素：自动触发/自动运行/自动维护/自动关闭；reconciler 必须**事件触发**，禁 cron/Timer/sleep-loop"。`src/zephyr/ex_core/risk_layer_orchestrator.py:1781-1827` 的 `start_reconcile_loop`/`_schedule_reconcile`/`_reconcile_tick` = 自续期 `threading.Timer`（`reconcile_interval_seconds` 默认 300s，:242），由 `trading_session.py:404` 在实盘会话启动时激活；无 M10 豁免标记；tick 内宽 except 只记日志（:1822）。同子系统已有 B4 治本先例（`trading_session.py:25,1162`：09-05 删除同型 Timer 调仓改事件驱动）——本件是漏网同族。

## 选项

| 选项 | 内容 | 最坏情形 |
|---|---|---|
| A. 维持 Timer | 不动 | 铁律破窗：下一处 reconciler 照抄 Timer 形态；宽 except 下对账故障静默 |
| B. **事件触发+staleness 兜底** | 对账触发改挂 ExecutionReport/持仓变更事件（PositionReconciler 已有 `handle_execution_report` 事件范式，`position_reconciler.py:80-94`）；另设最大 staleness 上限（如 30min 无事件则兜底跑一次）——兜底仍为"状态过期事件"而非自由轮询 | 改造期回归风险——用现有对账测试+影子并行一周验证 |
| C. 登记豁免 | 给本件补 M10 豁免标记合理化 | 豁免开口=铁律稀释；且本件无"必须时间触发"的正当性（对账天然有事件源） |

## 依据

事件源真实存在（成交回报/持仓变更），对账语义=事件驱动会计核对；staleness 兜底回应"长时间无事件漏对账"的反驳者关切（S4 反驳者记录 #2）。B4 先例证明同子系统同型改造可行。

## 风险

实盘路径行为变更——须影子验证+分批启用；改造施工归常值班次（非本裁定班）。

## 建议+置信度

**建议 B，置信度高。** 解锁条件：影子并行一周零差异。

## 若不同意应看什么数据

该对账环近 30 天的 tick 日志：若发现"无成交但确实需要周期性重估"的场景证据（如市价波动导致风险敞口漂移），则兜底间隔需从 30min 收紧到 5min 档。
