---
ttl: task_bound
creation_token: m5-sched-silent-failures-20260925
---

# M5 分册 04：静默失败模式专册（哪些死了没人知道 + 探活）

> 编号 S1..S18。每案：现象/根因/状态/修法归属。当前活病=S1/S2/S3；其余为已修史（防复发判据进 05 册）。

## 一、当前活病（挖矿当日实证）

### S1【高危】PostSettlement 注册脚本已被回退到坏形态——重注册即复断
- 现象：live 任务 09-24 15:30 跑成（exit 0），但 `scripts/register_post_settlement_task.ps1` 在 HEAD 是坏形态：`New-ScheduledTaskAction -Execute python.exe -Argument '-u ... >> log 2>&1'`。
- 根因：8f0e5feba9（09-24，st-schedfix）修好（conhost --headless + cmd /c 真重定向）；**同日 bc76efe3bf（st-library-final，commit 主题=lookup 接入，与该文件无关）把 action 块整段改回坏形态**——典型的他会话 staged 旧版整册覆盖/FOREIGN_CHANGE 恶性链。
- 影响：任何人执行"重注册"（幂等 Set-ScheduledTask 惯例）即把 Owner 批的 15:30 结算自动化打回 argparse exit 2——与 09-15~09-24 期间"从未跑成过"完全同构，且无声。
- 修法：revert bc76efe3bf 中该文件 action 块（10 行）；另查 bc76efe 是否吞了同批其他修复。归属：提交链/施工车道（本车道只读）。

### S2【高】tilib_indicator_backfill_nightly 每夜 exit 1——夜回填疑似整链死
- 现象：LastTaskResult=1（09-24 02:30）；`backfill_night.bat` 第一步日志重定向目标 `.runtime\tmp\tilib-probe\` 目录已不存在（cmd 下重定向失败=该行不执行），第二步还依赖 `.runtime\tmp\tilib-probe\night_probe.py`——**探测脚本住在 tmp 里，tmp 卫生一清即指空**。
- 根因：脚本把日志目录+探针脚本放进 `.runtime/tmp`（宪法 §9.4 明示 tmp 是可清区）；合规卫生机制反杀脚本自身。
- 影响：技术指标 DWM 夜间回填+夜探自 09-2x 起可能从未成功（每日 exit 1 常态化=报警疲劳掩盖）。
- 修法：bat 落仓内 logs 目录；night_probe.py 正名入 scripts/data/；禁引用 .runtime/tmp。归属：数据链车道/施工。

### S3【中】SimBridgeExecute 09-24 13:05 班次：无日志+异常退出码 4294770688(0xFFFD0000)
- 现象：任务 LastRun=09-24 13:05，LastResult=4294770688（非标准调度码）；`.runtime/logs/sim_bridge_execute.log` 末条停在 09-23 13:05 exit 0。
- 判读：09-24 两班（09:35 应也触发）均未产生包装层日志——包装 ps1 在 Write-SimLog 前即死（交易日闸/PATH/解码类）或被 OS 杀；非标准码意味着不是脚本约定 exit 0/1。
- 风险：模拟盘下单桥静默断链（正是裁定 #339 担心的"指令写入死桥"反面向：桥活着、饲养员死了）。
- 修法：先取证（Windows 事件日志 Task Scheduler 操作通道 09-24 13:05 记录）再修；ps1 首行前加 file-level 旁落日志。归属：M2 回测模拟链/施工。

### S4【中】订单类工单守护建成未接线
- `order_daemon`（L5 工单生成）零生产 spawn：无 __main__、无 register 脚本、无计划任务。现在不响=预期；一旦有人以为它"在守"，即是静默期待落空。接线时必须按 journal 事件触发（宪法 §9.3），禁加 cron。

### S5【中】BoardIndexRealtime 盘中断供无监护
- 09:20 复活件只保证"开盘时活着"；盘中死（ticks3 缺→exit 3 或 CH 断连崩）无人拉起。探活=CH `board_index_tick` max(ts) 滞后 >60s（盘中）即黄。归属：数据链车道评估是否入 guard 族。

### S6【低】报警疲劳常态化非零码
- ResourceRegenCheck exit 3（=检出漂移发布告警语义）、ConfigCheck/GateFullTreeAudit/F06Grid exit 1 连日如此——LastTaskResult 非零已失去信号价值。修法：各 CLI 把"检出问题"与"自身崩溃"分码（如 3=检出/0=干净/非 0,1,3=崩溃），并让晨报生成器消费该字段而非人工盯。归属：M3 治理链。

## 二、已修史（防复发判据来源；探活判据已固化进 05 册）
| # | 事故 | 根因 | 根修（真源） |
|---|---|---|---|
| S7 | belt 死 4 天无人知（09-18~09-22） | 补位消费者定位→死后无感；无自启主人 | register_belt_daemon_task.ps1 PT1M 探测+keep-list |
| S8 | belt 心跳失写/假死 6 例（夜班四轮实证定性） | 心跳写在事件循环间隙，池化长 drain 单波不可达 | st-k4-20260923 心跳线程化（30s 独立线程；commit_belt_daemon.py:274/793） |
| S9 | daemon 吃启动时代码 | epoch 子树不含 scripts/commit_queue.py→改判据不换血（#ARCH-323 同构） | 纪元合成+安全点 re-exec（#281①）；第三子树扩面仍挂 12_belt E3 |
| S10 | powershell 闪窗风暴（每 5min×3）+ AI-Wrapper-Inject 僵尸 0x800710E0 | 控制台子系统 Interactive 拉起先建窗；-WindowStyle Hidden 来不及 | 09-08 十任务统一 wscript+launch_hidden.vbs；pythonw 换装；design_memos/93 |
| S11 | PostSettlement 09-15 起从未跑成 | '>>' 是 shell 重定向 token，直喂 python=argparse exit 2 | 8f0e5feba9 conhost+cmd /c（live 任务）；注册脚本回退=S1 |
| S12 | guard 双杀/僵尸占位（07-22 守护被重注册杀；08-06/07 两天断供） | Unregister 杀在跑实例；IgnoreNew 让僵尸占坑 | register 脚本 in-place Set-ScheduledTask 铁律；MultipleInstances=Parallel+心跳接管 |
| S13 | 50 实例堆积内存耗尽（#99，08-16） | RestartOnFailure 无退避链式重启 | 注册表内烤退避 3×10min+msvcrt 字节锁 |
| S14 | guard 每 3 天被 OS 杀 | ExecutionTimeLimit 默认 3 天 | guard 族 TimeLimit=0（reaper 反向自限 10min=one-shot 自食狗粮） |
| S15 | ide_health_daemon 时代：stale PID+夜生 60+ python | 常驻监护者自身=残留风险；违规者从不登记 | 08-28 裁定废常驻改 reaper one-shot+keep-list |
| S16 | daily_crypto 从未自动跑成 | executor `light` 不存在，APScheduler 注册不校验→每日 lookup failed 移除 job | 09-16 改挂 default（schedule.yaml 在案）——**教训：新槽必查 executor 白名单** |
| S17 | 09-20 周窗未 firing（daban 链断 5 日） | weekend_calibration cron 周日 vs 周一差一天（周日 QMT 不可达+维护窗双杀） | cron "1"+catchup_guard overdue 过渡 |
| S18 | monthly_static 整月批错过 32h（9/1 调度器 10:37 才被拉起） | cron 错过无补跑 | L10.7 catchup_guard 05:30 档期对账 |
| S19 | ch_health_probe 8/2 静默退出 13h 空窗 | 无 guard keepalive | guard 三卫士族建制（#ARCH-CH-PROBE-GUARD） |
| S20 | scheduler 管道缓冲死锁（#ARCH-BOOT-002 F） | 重定向管道满→WaitForExit 永不返回 | 轮询 HasExited（禁"优化"回 WaitForExit——start_*.ps1 头注明文警告） |

## 三、横断失效模式（分类学，供红蓝用）
1. **单点哑发射**：Task Scheduler 只管点火不管成败——LastResult 需人看，无消费者。
2. **报警疲劳**：常态化非零退出码（S6）淹没真失败。
3. **落文件≠推到人**：DeadmanSwitch/哨兵告警只落 tmp/事件日志/前端晋升页（Feishu 已裁撤）；人不在屏前=无人知。
4. **依赖放错区**：脚本依赖 .runtime/tmp（S2）或库外绝对路径（RestartMiniQmt、NightlySentiment 0x80070002、TraeCacheCleanup）。
5. **注册脚本↔live 任务漂移**：live 被手修/他 commit 回退脚本（S1/S11）——重注册=回滚。
6. **守护杀守护**：Unregister/TimeLimit/IgnoreNew/无退避四旧病，全有 in-place/Parallel/TimeLimit=0/退避对治，重注册仍可能复发。
7. **会话级进程冒充常驻**：belt 曾活在 AI 会话进程树下，会话退即死（S7 根因）；现 belt 由任务拉起已解，但 Start-Process 手拉 guard 仍会死于终端（start_*.ps1 明令禁用）。

## 四、复核命令
```
git show bc76efe3bf -- scripts/register_post_settlement_task.ps1 | head -40     # S1 回退证据
schtasks /query /tn tilib_indicator_backfill_nightly /v /fo LIST               # S2 exit 1
ls ".runtime/tmp/tilib-probe" 2>&1                                             # S2 目录缺失
powershell -NoProfile -Command '(Get-ScheduledTaskInfo -TaskName "ZephyrAlpha_SimBridgeExecute").LastTaskResult'  # S3
grep -rn "OrderDaemon(" src/ --include="*.py" | grep -v test                   # S4 零接线
python -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon --status       # S7/S8 探活
```
