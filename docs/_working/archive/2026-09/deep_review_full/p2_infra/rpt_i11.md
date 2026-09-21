---
ttl: task_bound
title: 深度审查报告——I11 缺口探测（backfill_checker）
object: I11 缺口探测
target: src/zephyr/data/backfill_checker.py:176（detect_missing_dates L176-204、_discover_backfill_tables L321-368、run_weekend_backfill L1121、run_daily_backfill L1204）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I11 缺口探测 backfill_checker（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：L10 周末/L10.5 每日缺口检测+精准补下载、动态表发现（慢变化表排除裁决）、kline_index 专用 symbol 级差集路径、known_data_gaps 历史缺口注册表。
- 测试：头注 [TESTS] 空；tests/ 仅 test_backfill_checker_kline_index.py（专用路径有测、主路径无测）——**主链缺口**。
- 变更热力：24 commits。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| B | **P2 tick 补下载通道未随桥迁移**：backfill_tick_data 依赖 `from xtquant import xtdata`（miniQMT 客户端）+ 补写 data_source 恒 "miniqmt"；miniQMT 9/18 退役后 ImportError→返回 0，tick 缺口检测照常报缺但永远补不上——缺口探测存活、修复通道死亡（断链不自知的典型形态）；且桥模式产出 data_source=qmt_bridge，xtdata 补写行混入 miniqmt 标记污染溯源 | backfill_checker.py:510-534,497 | P2 | 退役后跑 run_daily_backfill 看 tick 缺口是否持续且 rows=0 |
| A | **P2 晚班时段被 17:00 daily_backfill 系统性误补**：run_daily_backfill(days=1) 在 17:00 检测"当日"，而 daily_capital(18:00)/daily_event(19:00)/research_nightly(20:30)/nightly_financial(22:00)/consensus(23:30)/daily_alt_fx(23:35) 的表当日 0 行<threshold → 判缺 → run_task 提前重跑 → 晚班正点再跑一遍：每日双跑+首跑可能是半量数据+0 行告警噪声（与注释"正常情况下几秒完成"矛盾） | backfill_checker.py:1204-1237,842-883 + schedule.yaml 时段表 | P2 | grep run log "通过 scheduler.run_task 补下载" 的 17:00 命中清单 |
| A | CH 查询失败与"0 行"不可分：detect_missing_dates 里 `_ch_query` 失败返 None→count=0→判缺——CH 故障窗口触发全表假缺口+补下载风暴（写侧有本地兜底兜住，但 xtdata 配额/时长浪费） | backfill_checker.py:192-204,102-105 | P3 | 断 CH 跑检测看假缺口清单 |
| A | run_weekend_backfill 除"拿不到交易日"外恒 success=True——补下载失败/全缺不反映在 success（_run_special_schedule 据此定任务成败=假完成态，checklist #12 邻接） | backfill_checker.py:1153-1199 + scheduler.py:212-217 | P3 | 构造补下载失败看返回 success |
| D | 慢变化表双裁决（static_refresh schedule + business_event_date 列）+快照积累表边界（daily_* incremental=false 保留检测）——口径裁决完备，登记性强 | backfill_checker.py:227-244,356-367 | 已查无 | 对 known_data_gaps 案例表 |
| A | kline_index symbol 级差集+显式窗口回填（绕开 last_key 超前推进）设计正确，是全仓唯一显式窗口补通道 | backfill_checker.py:632-755 | 已查无 | 读码+专测存在 |
| E | known_gap empty_table 只告警不自动补（需人工）——职责边界正确 | backfill_checker.py:1094-1107 | 已查无 | 读码 |

## 3 SOTA 对照
- "查实际行数而非游标"的缺口检测（reconciliation-first）与数据平台 data-reconciliation 惯例一致；symbol 级差集检测超出表级行数检测的平均水平。**对等已有（偏优）**。来源：数据质量对账工程通识（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。

## 4 缺陷清单
1. P2 tick 补下载通道死亡（miniQMT 退役后）：修法=桥模式补通道（读沙箱历史 dump/桥侧回补工具接线）或显式声明"tick 缺口转人工"并停用自动 tick 补（消除断链假象）。
2. P2 17:00 误补晚班时段：修法=daily_backfill 按 task.schedule 截止时刻过滤（只检 17:00 前应完成档），或检测窗口改"前一交易日"。
3. P3：CH 故障假缺口风暴、success 语义过宽。

## 5 挂起疑问
- xtdata 在 9/18 后是否彻底不可用取决于 miniQMT 实际退役执行情况（93 备忘口径）——若保留双跑则 P2-1 降级为溯源标记污染（P3）。

## 6 完备性自评
六轴全查。长尾：known_data_gaps.yaml 全量条目未逐条核（在途改动文件）；backfill_tick_data 的 QMT 下载耗时/配额未实测。
