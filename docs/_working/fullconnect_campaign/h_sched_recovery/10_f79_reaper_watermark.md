---
ttl: task_bound
title: F79 reaper 与水位监控（进程收割+RAM/commit 水位+保命链）——L08 复飞矿道案卷
session: zc-l08-20260927
---

# F79 · reaper 与水位监控

> 总册行：I 段 F79，状态 built，P1，`src/zephyr/trading/process_reaper.py`。M0=S4。
> 本卷=09-27 复飞复测。基册=m5_scheduling/02 册 §二+补挖波_20260925/04_perf_watermark.md（三层水位闸合账）+90_backfill_wave（09-25 深夜曾判"reaper 任务每轮 exit 1、水位台账 22h 未刷新"红）。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | psutil 进程采样（逐进程 mem_mb :417）；系统 probe（host_resource_governor.check_system_watermark :224）；config/alert_rules.yaml system.* 5 规则（ALERT-SYS-001..005）；keep 白名单 data/runtime/process_reaper_keep.txt（**09-27 实测 208 行**） |
| 下游消费 | --status 输出（breaches/watermark）；应急保命轨 BRK-078+系统水位 BRK-066 保命链评估（process_reaper.py:1037-1100）；收割决策 |
| 自动化触发 | `ZephyrAlpha_ProcessReaper` LogOn+PT10M：09-27 实测 Ready，LastRun **06:47:23 result=0**，NextRun 06:57:22——**90_backfill 波 09-25 深夜"每轮 exit 1"红已不复现**（当日复探归位绿） |
| 真源与注册表 | scripts/register_process_reaper_task.ps1；_DANGEROUS_MEM_GB=10.0（:161）；判定权三分互斥铁律（:57 头注：incubator 拒生/reaper 收割/host_resource_governor 准入，三面互不长草） |
| 门禁与质量尺 | ExecutionTimeLimit=10min（自食狗粮防僵尸）；keep 白名单 cmdline 子串命中豁免；水位规则不可读=本周期不评估"宁漏不假绿" |
| 当前运行状态 | **绿**：09-27 --status 实测 `last_run=2026-09-27 06:51:28 scanned=21 whitelist_hits=15 killed=0 ghosts 0/0/0`；watermark `ram 63.85GB 总/25.52 可用/60.0%、commit 62.1%、cpu 43.7%、degraded=False breached=[]`；safety_wires `emergency_track_state=normal breaches=1（累计计数位，当态 normal）` |

## 二、子模块三级枚举

1. **层 1 进程级收割**：pythonw one-shot（LogOn+PT10M）；孤儿/超龄/失控/幽灵四类判（ghosts tracked 0）；_DANGEROUS_MEM_GB 10GB 阈；keep-list 豁免（belt/git_commit/backup/长班次登记，STALE 13 腿相关 6 行命中=kline_sector/stock_basic/daily_valuation/restricted_shares/share_change/top10 族——**防误杀循环核对义务与 F77 联动**）。
2. **层 2 系统级水位闸**：host_resource_governor.check_system_watermark（probe→alert_rules.yaml 判→通知板 publish 永不抛）；reaper 每轮附跑保命链（水位看护失能只报 error 不反噬收割主链 :1069-1071）。
3. **层 3 阈值 SSoT 接入**：alert_threshold_registry.yaml（REG-ATH-001）→threshold_loader.py fail-closed；reaper/水位相关条目经统一 loader（AI-THD-001 九模块统读）。

## 三、接线四态独立复核

- 总册 built → **维持 built**（任务 0/采样/水位 breached=[]/保命链 normal 四证当日齐）。
- **骨架勘误**：①总册 F71 堵点"内存二级防线 Windows 空，兜底只剩 reaper 水位"成立——本环节实为全仓内存防线最后一闸，P1 定级恰当；②90_backfill 波 09-25"reaper exit 1 每轮"判读与 09-27 实测不符——红已消失（间歇性或已自愈），追认 F79 绿但保留"exit 1 成因未归档"一笔（待裁）。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | keep 白名单 208 行与 STALE 13 腿防误杀循环逐腿核对 | 与 F77 §四-1 同批（逐腿核对防"误杀→重跑→再 stale"循环） | P1 |
| 2 | 09-25 exit 1 成因未归档 | 若复发按 04 册分案取证（任务历史/事件日志） | 待裁 |
| 3 | reaper 无心跳（stateless one-shot by design） | 健康判据=last_run<12min（05 册判据维持），已可探 | P2 |
| 4 | 水位准入（host_resource_governor）与收割的互斥边界测试面 | 归容量保障域红蓝批 | P2 |
| STALE 13/假绿 5 | STALE 13 腿**跨 F77/F79 两带**（tasks.yaml 在册=F77；keep 白名单防误杀=F79）；假绿 5 腿纯归 F77 | 双带分账已在本卷/08 卷分别落锚 | P1 |

## 五、自审闸三态

**挖干（复核维持+红点当日复探）**：02 册+04 补挖册三层闸全证+本卷 --status/任务码/白名单行数当日三探。开口=exit 1 成因归档。三态=**维持 built**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -m zephyr.trading.process_reaper --status | head -8     # last_run/scanned/watermark/breached
powershell -NoProfile -Command '(Get-ScheduledTaskInfo -TaskName ZephyrAlpha_ProcessReaper)|fl LastRunTime,LastTaskResult'
wc -l data/runtime/process_reaper_keep.txt                     # 208
grep -c "kline_sector\|stock_basic\|daily_valuation\|restricted_shares\|share_change\|top10" data/runtime/process_reaper_keep.txt   # 6
sed -n '155,165p' src/zephyr/trading/process_reaper.py          # 10GB 阈
```
