---
ttl: task_bound
title: e2e3_ops_repair (20261001 删除事故后重建)
note: 重建件
---

# E2+E3 运维簇环节簿 — lane C 触发环修复 / Ollama 供给环修复 / E9 监控补位

> **重建注记（2026-10-01）**: 本簿原落点=主区 `docs/_working/lane_c_chain_night_20261001/e2e3_ops_repair.md`，被他队清理事故删除；现按施工代理上下文原文重建于 worktree 同相对路径。内容与首写版一致（仅增本注记与 §5 排障脚本行微调）。

- 会话: st-lanech-20261001（运维簇 E2 触发环 / E3 Ollama 供给环 / E9 监控环）
- 日期: 2026-10-01 夜
- 施工区: worktree `.worktrees/st-lanech-20261001`（代码）；计划任务=系统级直改（Action 均指向主区 `D:\ZephyrAlpha` 脚本）
- 挖矿依据: 修复方案三条均经总包挖矿实证（09-26 mine SVD 崩但 exit 0 等）

## 1. E2 — `scripts/run_factory_lane_c.ps1` 吞错修复

**变更前**: 四段 `cmd.exe /c "python ... >> $log 2>&1"` 无 rc 检查——任何段崩溃后续段照跑、整批 exit 0（09-26 实证：mine 段 SVD 崩，LastTaskResult=0 掩盖失败）。另一次生 bug：尾部 `exit $LASTEXITCODE` 实际透传的是 git worktree-audit 段的 rc，不是流水线 rc。

**变更后**（照抄 `scripts/run_c4_exam.ps1:40-52` 现成模式）:
- 每段后捕获 `$LASTEXITCODE` → 写 `==== <段> exit code N ====` → 非 0 时写 `==== <段> FAILED rc=N ====`、调 Alerter ERROR、短路后续段、`exit N` 透传。
- 四段保留原命令不变: mine `--top 10` / intake `run --with-lane-b --limit-precheck 15` / construct / translate `--seeds 5`。
- rc 全绿: translate 后追加 E9 全绿行 + Alerter INFO 心跳（见 §4）。
- 尾部改 `exit $finalRc`（=$translateExit），修复被 git 覆写 `$LASTEXITCODE` 的次生 bug。

**验证**: ASCII-OK（5701 bytes）；PSParser PARSE-OK；alerter `cmd.exe /c` 双引号转义模式冒烟 rc=0（INFO 不落盘符合预期）。

**生效注记**: 计划任务 Action 指向主区脚本——wrapper 修复在 merge 回主区后生效；本窗内触发器变更即时生效。

## 2. E2 — `scripts/register_factory_lane_c_task.ps1` 周六窗改期（Owner 方案1）

| | 变更前 | 变更后 |
|---|---|---|
| 触发 | `-Weekly -DaysOfWeek Saturday -At 10:00`（DaysOfWeek=64） | `-Weekly -DaysOfWeek Monday..Friday -At 20:00`（DaysOfWeek=62） |
| NextRunTime | 2026-10-03 10:00（周六） | **2026-10-01 20:00（今天，已核实）** |
| 注释 | "weekly Sat 10:00" + 周六非交易日窗口理由 | 工作日 20:00 收盘后 E0 heavy_ok + 日历必有该日行（根治 gate_deny_calendar_unknown）；头注释/Key design/`OK registered` 文案三处同步 |

依据: Owner 已批方案1（工作日 20:00 收盘后=heavy_ok，且 trade_calendar 必有该日行）。E0 闸每次触发内重查日历，触发表仅为便利。

## 3. E3 — `scripts/register_ollama_serve_task.ps1` + ZephyrAlpha_OllamaServe 断供修复

**变更前**: 仅 LogonTrigger、无失败重启；实测 LastTaskResult=15、**State=Running（僵尸实例挂死，无进程）**、11434 无监听。

**变更后**: AtLogOn 触发 + `-RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)`（RestartOnFailure）+ StartWhenAvailable；ExecutionTimeLimit 保持 PT0S（服务器不设时限）；MultipleInstances=IgnoreNew。注释写明 RestartOnFailure 语义：非零退出才拉起（端口冲突干净退出不触发，不双实例不端口蹲占）。

### 排障实录（发现供他队复用）
1. `Register-ScheduledTask -Force` / `Set-ScheduledTask` / `schtasks /Create /F /XML` 全部 0x80070005 拒绝访问。
2. 排除法定位: 两任务 NTFS ACL 完全一致且 fanzi=(F)；COM 任务 SD 完全相同（`D:(A;ID;0x1f019f;;;BA)...(A;ID;FA;;;fanzi)(A;;FR;;;fanzi)`）；`schtasks /Change /ENABLE` 却可写。
3. **真因两层**:
   - (a) 旧任务 State=Running 挂死实例（tasklist 无 ollama 进程=纯调度器状态残留）→ `Stop-ScheduledTask` 释放后 State 4→3 Ready；
   - (b) 含 **BootTrigger**（或 `-RunLevel Highest`）的注册一律拒绝 → **标准令牌注册 BootTrigger 任务需提权**。
4. 最终落点: 放弃 AtStartup（提权不可得 + InteractiveToken 登录前本就无法启动，AtStartup 本就不产生实效），AtLogOn + RestartOnFailure 为有效覆盖。总包方案中"开机触发"一条按此降级，理由如上，XML 留档可考古。

**验证**: 注册成功；Triggers=MSFT_TaskLogonTrigger(Enabled=True, UserId=范清风\fanzi)；Settings RestartCount=3 / RestartInterval=PT1M / ExecutionTimeLimit=PT0S / IgnoreNew / StartWhenAvailable=True；版本前置 0.34.1 > 0.32.1 crash-bearing ceiling 通过；手动 `Start-ScheduledTask` 后 **11434 探活 UP**（HTTP 200，`{"models":[{"name":"qwen3:14b"...`，60 秒重试窗内秒级即通），任务 State=Running。`ollama.exe serve` 已在 reaper keep 名单（`data/runtime/process_reaper_keep.txt`），不会被误杀。

## 4. E9 — 监控最小补位（在 §1 wrapper 内落地）

- rc 全绿: log 写 `==== lane C full chain rc all green (mine/intake/construct/translate) - E9 heartbeat ====` + `Alerter().notify('factory_lane_c', 'lane C full chain rc all green', 'INFO')`。签名已按 `src/zephyr/data/alerter.py` 核对: `notify(task_id, error, level=LEVEL_ERROR, source=None, extra=None)`；INFO 只写 logging 不落盘，持久痕迹=log 行+计划任务历史。
- 任一段 FAILED: `notify('factory_lane_c', '<段> FAILED rc=N (后续段 skipped)', 'ERROR')`——ERROR 落盘 `data/failures/` JSON（同 task_id 冷却 300s 防刷），经 cmd.exe 包装进日志不反噬退出码。
- **deadman 心跳表扩展建议（只登记，不动手——deadman_switch.ps1 归他队监控面）**: 建议心跳表增加 factory_lane_c 行，消费 `.runtime/logs/factory_lane_c.log` 的 `==== lane C full chain rc all green` 行作为心跳信号；新窗为工作日 20:00，建议 >26h 无该行即告警。

## 5. 任务定义留档（均在主区 `.runtime/tmp/`，清理事故未波及）

| 文件 | 内容 |
|---|---|
| `ZephyrAlpha_FactoryLaneC.pre_e2e3_20261001.xml` | 变更前（Sat 10:00） |
| `ZephyrAlpha_FactoryLaneC.post_e2e3_20261001.xml` | 变更后（Mon-Fri 20:00） |
| `ZephyrAlpha_OllamaServe.pre_e2e3_20261001.xml` | 变更前（LogonTrigger 裸任务） |
| `ZephyrAlpha_OllamaServe.post_e2e3_20261001.xml` | 变更后（LogonTrigger+RestartOnFailure） |
| `ZephyrAlpha_OllamaServe.new_e3_20261001.xml` | BootTrigger 版生成物（未采用，0x80070005 实证留证） |
| `probe_e3_perm.ps1` / `set_ollama_task_e3.ps1` / `gen_ollama_xml_e3.ps1` / `read_task_sd_e3.ps1` / `verify_ollama_e3.ps1` / `verify_laneC_e2.ps1` / `parse_check_e2e3.ps1` | 排障与验证脚本（临时区，随 TTL 回收） |

## 6. 六向台账

- **代码**: worktree 3 文件（diff stat 中本簇份额 +49/+12/+15），零新建文件，三文件纯 ASCII + PSParser 双验证。同 worktree 存在他簇改动（factory_intake_pipeline.py / lane_c_formula_miner.py / trend.py / test_lane_c_formula_miner.py）——非本簇所改，未触碰。
- **系统**: 计划任务 2 个变更（FactoryLaneC 触发器 / OllamaServe 定义+重启设置）；临时任务 `ZephyrAlpha_E3XmlGen` 注册后立即 Unregister 已清、`ZephyrAlpha_E3PermProbe` 被拒未落地；无其他系统面残留；一次 `Stop-ScheduledTask`（清僵尸状态，无进程被杀）。
- **文档**: 本簿（e2/e3 合簿）；首写于主区 docs/_working 被清理事故删除，现重建于 worktree（随本簇代码同分支交付）；主区 promote 由总包收口。
- **数据**: 零 DB 操作（RULE-DATA-OPS 未触发）；alerter 冒烟为 INFO 级，未落任何文件、未碰 data/failures/。
- **冲突**: 未触碰 deadman_switch.ps1 及他队文件；三文件 claim 全程持有并已 release（`lock_files list` = CLEAN）。
- **风险**: (a) wrapper rc 修复待 merge 回主区才对计划任务生效（未 merge 前工作日 20:00 仍跑旧吞错 wrapper——功能不受损，仅缺 rc 短路与心跳）；(b) RestartOnFailure 未经历真实死亡回归（探活为手动 Start，非失败自动拉起）——建议观察窗内遇一次真实断供即验证；(c) BootTrigger 缺席=重启后首次登录前 11434 空窗（InteractiveToken 结构性限制，与修复前持平，如需根治须 Owner 提权一次性注册，XML 已留档）。

## 7. 自审闸三态

- **合规态**: .ps1 纯 ASCII ✅ / PSParser ✅ / 零 git add-commit-push ✅ / 只碰授权 3 文件 ✅ / 任务变更前先导出留档 ✅ / deadman 未触碰 ✅ / claim acquire→release 闭环 ✅ / 注册表等热文件零改动 ✅ / 生成器 i18n 不适用 / RULE-ENV Python 3.12.8 ✅ / RULE-GUARDIAN reaper 在岗（scanned=18 killed=0）✅
- **疑点态**: `Stop-ScheduledTask` 清僵尸实例属系统级操作，但无破坏性（无存活进程被杀，仅调度器状态复位）；E9 ERROR 路径会写 `data/failures/` 生产路径——alerter 本身设计如此（production 成件），非测试污染。
- **未决态**: (a) wrapper 生效依赖 merge；(b) RestartOnFailure 真实拉起待回归；(c) BootTrigger 提权注册留待 Owner 需要时执行。
- **移交总包**: 本簿为新建 .md，CREATE-GUARD creation_token 登记责任随 commit 侧收口（重建版落 worktree，随代码同分支提交）。
