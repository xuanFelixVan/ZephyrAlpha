---
ttl: task_bound
title: W1·F06 周六窗故障根因册（st-examchief-20261009）——PS5.1 存活中写 stderr=终止级地雷
created: "2026-10-09"
sid: st-examchief-20261009
family_id: EXAMCARD-CAMPAIGN
status: root_cause_fixed_rehearsal_running
---

# W1·F06 周六窗故障根因册

## 0. 一句话

`run_f06_grid.ps1` 的 `$ErrorActionPreference="Stop"` + `*>>` 全流重定向下，**仍存活的 python 子进程写出第一行 stderr（pandas FutureWarning，首次 eval 必喷）即成终止级 NativeCommandError：PS 停管线→杀死子进程→rc=1、零日志**——三窗（09-19/26/10-03 23:00）全灭于此，本件从 09-15 出生起没成功过一次。

## 1. 症状

- `.runtime/logs/f06_grid.log` 仅三行 fired（23:00:01），零 python 输出、零 batch exit 行；文件 177 字节逐字节核验。
- 计划任务 ZephyrAlpha_F06Grid LastTaskResult=1；下次触发 2026-10-10 23:00（硬死线）。
- 三窗均无 `data/strategy_intake/grid_2026*` 产出目录。

## 2. 侦查证伪链（五层排除）

| 嫌疑 | 证伪证据 |
|---|---|
| ①控制台形态 stderr 地雷（09-15 车道C 注记所指形态） | 同机控制台红蓝实验：EAP=Stop+`*>>` 下 stderr 被捕获、wrapper 存活写 exit 行（w1_redblue 实验） |
| ②reaper 误杀 | 击杀日志三窗当夜零匹配记录；扫描节拍 10min 对不上 t+30s 死亡；`factory_grid_executor` 在 keep 名册；级联杀只向下不杀父 |
| ③deadman/guard 类看门狗 | deadman_switch.ps1 逐行核=纯只读心跳监视；worktree_drift_watchdog 零 kill 逻辑；九个持 kill 模块全为杀自己子进程 |
| ④python 原生崩溃 | Windows 应用/系统事件日志零记录（access violation 必有 WER） |
| ⑤python 未启动/PATH 失败 | 探针1（同 wrapper 结构+立退存根）经真实计划任务跑=rc=0、日志完整 |

## 3. 决定性陷阱（w1_evidence/red_trap_trace）

0.5s 分辨率哨兵 + 生产保真探针B（任务上下文、同 wrapper 形态、存根=沉默20s→写1行stderr→再活40s）：

```
19:06:37.6 BORN python（沉默装载）
19:06:59.2 DIED(PYTHON)   ← t+21.6s，正是写完第一行 stderr 之后
19:07:03.4 DIED(PS)       ← 随死 4s
日志：仅 fired 行；任务 rc=1
```

与生产实弹（18:49 触发真任务：python t+31s 死于数据装载后期、wrapper +6s、零日志、rc=1）完全同构。
**判别实验**：探针1（<1s 内写完 stderr 即退出）存活——错误记录在管线排空期到达=非终止；**存活中写 stderr=终止**。探针D（EAP 局部降级 Continue）存活；探针C（cmd.exe /c 原生重定向）存活且日志干净。

## 4. 修复（对齐仓库既证模式）

`scripts/tasks/run/run_f06_grid.ps1` 两处 python 调用改为 `cmd.exe /c "python ... >> $log 2>&1"`（车道C/C4 同款，日日绿先例）：
- `--n-samples 6000/99999`、seed、stratify-dims、subspace-json 语义逐字保留；
- 批B JSON 经引号实测定型：PS 单引号外层字面量保 `\"` 原文送达 python argv（双写形会被 cmd 剥引号致 json.loads 失败——w1_quoting 实验）；
- N ledger 自动登记在 executor 侧 summary 时点（`_auto_record_and_advance`），不经 wrapper，零影响。

## 5. 验收状态

- 解析：PS Parser ParseFile OK。
- 蓝探针（真实计划任务上下文）：stderr 连喷存活、exit=0、日志完整（w1_evidence/blue_probeC_fixed_wrapper_green.md）。
- 实弹彩排：19:17 触发真任务，119+ 条 FutureWarning 流过日志（历史必杀行现已无害）、python 存活进 eval 循环、grid_20261009-191707 目录已建；批A 完成时验 manifest+rc=0。
- 正式验收=2026-10-11（周六）23:00 窗：manifest.csv 有产出且 rc=0。

## 6. 副产发现（顺手登记不扩面）

- token 册盘面缺 HEAD 3 条（quant_methodology 07/08/12 占位骨架，陈旧快照压盘）——已按工具处方增量补回（只增不减，禁整片覆盖纪律遵守）。
- reconcile_worker 孵化账每 10-30min 被孵化超期收割且击杀日志 cmd 字段归因错位（name=bash.exe 而 cmd=reconcile_worker）——非本案面，留观不扩。
