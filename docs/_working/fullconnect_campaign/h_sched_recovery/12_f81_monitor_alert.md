---
ttl: task_bound
title: F81 监控告警（alert_threshold 册+health_monitor+status_dashboard+deadman）——L08 复飞矿道案卷
session: zc-l08-20260927
---

# F81 · 监控告警

> 总册行：I 段 F81，状态 built，P1，alert_threshold"38 条"+health_monitor+status_dashboard+deadman。M0=S6。
> 本卷=09-27 复飞复测。基册=补挖波_20260925/04_perf_watermark.md §一·层 3（阈值 SSoT）+m5_scheduling/02 册 §三（DeadmanSwitch）+m6_frontend/01 册（告警前端消费）。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml（REG-ATH-001 阈值 SSoT，v1.6.0 起；**09-27 实测唯一 THD 条目去重 51 条**）；config/alert_rules.yaml system.* 5 规则；三卫士心跳/deadman 告警流 |
| 下游消费 | health_monitor.py（:58 _load_pressure_thresholds THD-HEALTH-001..004 import 期 fail-closed）；status_dashboard.py（MOD-INF-035，TUI+JSON 双模式）；api_server OpsAlertFeed 30s tick（api_server.py:4415-4449，M6 前端四态灯数据源）；晨报 |
| 自动化触发 | ZephyrAlpha_DeadmanSwitch PT5M（09-27 实测 Ready result 0，NextRun 06:52:46；纯 ps1 零 Python 依赖读 3 心跳，陈旧>10min 告警 tmp/deadman_switch_alerts.log+Windows 事件日志）；三卫士心跳 09-27 实测 scheduler.heartbeat=06:54:16（新鲜） |
| 真源与注册表 | REG-ATH-001（阈值唯一真源，threshold_loader.py fail-closed 统读，缺文件/缺条目直接报错禁第二真源）；alert_rules.yaml（MOD-INF-015 系统水位规则） |
| 门禁与质量尺 | fail-closed 双向（阈值加载缺条目报错；规则不可读宁漏不假绿）；THD-ALERT-003/004 死信积压+冷却、THD-ALERT-007 belt 离线>24h、THD-TRD-001..004 交易五级熔断（**status=design 未落码**） |
| 当前运行状态 | **绿（带结构黄）**：deadman/心跳/阈值册三层活探齐；结构黄=①告警"落文件/事件日志/前端晋升页"≠"推到人"（Feishu 09-15 裁撤后无带外通道，M5 横断 3）②THD-TRD 熔断四条 design 未落码③F74 触达缺铃铛同构 |

## 二、子模块三级枚举

1. **阈值 SSoT**：alert_threshold_registry.yaml（09-27 实测 THD-* 去重 **51** 条：HEALTH 4/ALERT 3..007/SYS 5/TRD 4 design/各域条目）；threshold_loader.py（AI-THD-001 九模块统读后码内硬编码清零）。
2. **运行时监控件**：health_monitor.py（PressureThresholds/ProbeResult/ReconciliationReport/HealthMonitor+monitor_thread+register_probe，:58-180 实扫）；status_dashboard.py（TUI+JSON 双模式，auto_runtime 装配体属性）；deadman_switch.ps1（监护者独立于被监者）。
3. **告警通道**：deadman→tmp/deadman_switch_alerts.log+事件日志；资源族→--publish-alerts；OpsAlertFeed→前端横幅/晋升页；晨报（06:31）。**无 SMTP/IM 带外通道**。

## 三、接线四态独立复核

- 总册 built → **维持 built**（三层当日活探齐）。
- **骨架勘误**：总册 F81"alert_threshold 38 条"→ 09-25 实测 49、**09-27 实测 51**（v1.4→v1.6 增补未回写+仍在增补；文档应引字段/计数器不写死）。附勘误：THD-TRD-001..004（交易五级熔断阈值）status=design 未落码——"监控告警 built"不含熔断阈值面，防高估。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | **告警无带外通道**（落文件≠推到人；F74 人工门铃同构、BoardIndexRealtime 盘中断供无人知同构） | Owner 裁定带外通道（与 F74 堵点 3 同一次裁定可并案：晨报承接/邮件/死件开关） | **P0**（横断） |
| 2 | THD-TRD-001..004 交易熔断阈值 design 未落码 | 随实盘域接线批落码 | P1 |
| 3 | 阈值册计数三口径（38/49/51）漂移 | 回写 51+引用字段化 | P2 |
| 4 | C 类守护件 28 件中 alert_aggregator 零调用方（今日清单 §1.6 装饰 2 之一） | 装饰件接线批（2.1-C5）或退役裁 | P1 |
| 5 | heartbeat_daemon 无对应计划任务（§1.6 D 类）——与 deadman/守护心跳三套机制重叠 | 内收判据合并（今日清单 2.3-5 门位：held_overlap 计数账先落地） | P1（Owner 门位） |
| STALE 13/假绿 5 | **不属 F81**（数据管线腿；但"两 build 崩停更 8-12 天无人知"证明本环节观测面缺口——归 F77 修复+本卷缺口 1 触达） | — | P1（联动） |

## 五、自审闸三态

**部分挖干（复核维持）**：04 补挖册阈值链双向闭环证（红队 36 用例在册）+02 册 deadman 四向证+本卷三层当日活探（心跳/任务码/THD 计数）；缺口=告警触达面带外通道（结构缺，非证据缺）。三态=**维持 built（带外触达缺口 P0 横断挂账）**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -o "THD-[A-Z0-9-]*" docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml | sort -u | wc -l   # 51
cat tmp/scheduler.heartbeat; cat tmp/tick_subscriber.heartbeat; cat tmp/ch_health_probe.heartbeat   # strip BOM 比对
powershell -NoProfile -Command '(Get-ScheduledTaskInfo -TaskName ZephyrAlpha_DeadmanSwitch)|fl LastRunTime,LastTaskResult'
tail -5 tmp/deadman_switch_alerts.log 2>/dev/null    # 无新告警=三卫士心跳新鲜
sed -n '58,72p' src/zephyr/trading/health_monitor.py  # THD-HEALTH fail-closed 加载
```
