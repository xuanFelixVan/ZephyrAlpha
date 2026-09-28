---
ttl: task_bound
title: F78 belt daemon（提交带补位常驻消费者）——L08 复飞矿道案卷
session: zc-l08-20260927
---

# F78 · belt daemon（提交传送带）

> 总册行：I 段 F78，状态 built，P2，`src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py`。M0=S3。
> 本卷=09-27 复飞复测。基册=m5_scheduling/02 册 §一+04 册已修史 S7/S8/S9。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | 提交队列（commit_queue enqueue 项）；纪元信号（re-exec 判据）；keep-list 登记（register_belt_daemon_task.ps1 自动写入 process_reaper_keep.txt） |
| 下游消费 | 队列落地（真 drain）；心跳文件 .runtime/commit_queue/belt_daemon.heartbeat；单例锁 belt_daemon.lock |
| 自动化触发 | `ZephyrAlpha_BeltDaemon` PT1M 探测拉起：09-27 实测 State=**Ready，LastRun 06:50:28 result=0，NextRun 06:51:18**（注：09-25 时点为 Running 常态——Ready/Running 随探测-退出循环摆动，皆属正常形态） |
| 真源与注册表 | scripts/register_belt_daemon_task.ps1（真源）；commit_belt_daemon.py（k=4 池化 thresholds `commit_queue_landing_pool_workers`；心跳线程化 st-k4-20260923 :274/:793；纪元 re-exec 裁定#281①） |
| 门禁与质量尺 | 单例锁 PID+TTL 600s+僵尸检测；reaper keep-list 豁免；"守护杀守护"四旧病对治（in-place/Parallel/TimeLimit=0/退避）已建制 |
| 当前运行状态 | **绿**：任务 PT1M result 0（09-27 实测）；09-25 基线 pid 23356/heartbeat age=0s（02 册）；盲区维持=纪元子树不含 scripts/commit_queue.py（改判据不换血）+lease_unavailable 静默 skipped |

## 二、子模块三级枚举

1. **任务层**：ZephyrAlpha_BeltDaemon（LogOn+PT1M+Time 09-22 保底；conhost --headless 探测壳；Get-CimInstance 查活即跳过，否则 Start-Process python -m ...commit_belt_daemon）。
2. **进程层**：主消费者=入队方内联自举；daemon=补位（夜间/无人窗口）；k=4 池化排空；30s 独立心跳线程（上线即打首心跳 :784）。
3. **监护层**：belt_daemon.lock（PID+TTL 600s+僵尸检测）；process_reaper_keep.txt 白名单（自动登记）；THD-ALERT-007 belt 离线>24h 告警阈值（S7 事故补课，09-27 阈值册 51 条实测含）。

## 三、接线四态独立复核

- 总册 built → **维持 built**（任务/进程/心跳/锁四向当日可探）。
- **骨架勘误**：无（本环节总册判定与实态一致；P2 定级合理）。附注：P2 与其"提交链唯一夜间兜底消费者"的实际地位相比偏低——S7 belt 死 4 天无人知事故后已加 THD-ALERT-007+PT1M 兜底，风险已收敛，维持 P2 有据。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | 纪元子树不含 scripts/commit_queue.py（改判据不换血） | 第三子树扩面（12_belt E3 挂账维持） | P1 |
| 2 | lease_unavailable 静默 skipped | 计数落 status 输出 | P2 |
| 3 | 会话拉起型 belt（Start-Process 手拉）死于终端的旧病 | start_*.ps1 明令禁用维持（横断 7） | P2 |
| 4 | 队列项 dead 处置依赖人工 requeue（dead_reason 修正） | 宪法 §2.6 正门流程维持，无自动化欠账 | P2 |
| STALE 13/假绿 5 | **不属 F78**（归 F77 §四） | — | — |

## 五、自审闸三态

**挖干（复核维持）**：02 册四向全证+本卷任务级当日活探（Ready/0/NextRun PT1M）。三态=**维持 built**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon --status    # 心跳/pid/pool
cat .runtime/commit_queue/belt_daemon.heartbeat 2>/dev/null
schtasks //query //tn ZephyrAlpha_BeltDaemon //v //fo LIST | grep -E "Status|Last Run|Last Result" 2>/dev/null || powershell -NoProfile -Command '(Get-ScheduledTaskInfo -TaskName ZephyrAlpha_BeltDaemon)|fl LastRunTime,LastTaskResult,NextRunTime'
grep -n "commit_belt_daemon" data/runtime/process_reaper_keep.txt           # keep 豁免在
```
