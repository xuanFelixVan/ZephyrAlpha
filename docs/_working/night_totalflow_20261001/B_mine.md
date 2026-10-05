---
ttl: task_bound
---

# L-B TI 线作业簿（重建版，全文存档=代理 transcript）

六向台账+停产根因：full_refresh（weekend_calibration 周一 03:00，分钟唯一生产者，窗口锚=月初⇒调度永远补不到 9 月）三杀梯次停产——09-21 写通道单批失败中止（1m/5m 停）、09-22/23 6h 收割+僵尸续写（15/30m 停）、09-29 调度器重启击杀（60m 停 09-28/120m 停 09-29）。死信回灌必败=manifest cols_clause=null 活表序截列错位。

施工终态：直驱脚本 ti_minute_recalc.py 已建；两轮校准 FAIL=计算核 09-19 后语义漂移实证（macd 日界冷值 0 vs 基线连续值；网格相同已排除）；**回填 HOLD**（漂移期数据不混史）；校准污染已清（ALTER DELETE 本役插入行，FINAL 40 键=原值复原）；TI 死信隔离（回灌结构性必败，重算为恢复路径）。

结构性修复卡（Owner 门位批）：计算核语义考古+full_refresh 拆 per-period+运行保障（禁维窗重启/收割白名单）+窗口锚缺口感知。前向：daily 自愈✓；分钟级 10-12 full_refresh 新语义产出或待修后统一。校验基线=09-19 run 2512 万行+audit_technical_indicator_coverage 验收闸。
