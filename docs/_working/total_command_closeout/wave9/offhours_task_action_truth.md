---
ttl: task_bound
completes_when: "在册盘后/盘前计划任务逐个 schtasks /query /tn <task> /xml 取 ACTION 原文入卷；'双入口分叉'真伪有判定与证据；若证伪则写明撤销建议"
---

# W-141 · 盘后/盘前计划任务 ACTION 原文取证（波 9.2）——判"双入口分叉"真伪

turn_budget: 取数 4 块内完成（枚举 1、XML 批量 1、旁证 2）；其余块只落盘
verified: 见 §5（全部为 `schtasks /query ... /xml` 原文与 `ls` 存在性实测；只读，未动任何任务）
assumed: 见 §5-b
input_set_disjoint_with: 本卷只碰 Windows 计划任务只读查询 + 主仓/车道盘上文件存在性 `ls` + 脚本原文直读；不碰 9.1 的 git grep 闸表（另卷 `compliance_gate_wiring.md`）、不碰 DB、不改任务（禁 /change /delete /end，本卷仅 /query）
evidence_ref.cmd: §6 命令清单原文照录

## 0. 在册命题（被检对象）

- ⚑-1② 原呈（`01_adjudication_master.md:139` 照录）："盘后结算计划任务的 ACTION 指向要改指统一入口（现双入口分叉且两区日志路径都不存在）"。
- X-62（`02_field_corrections_and_new_cases.md:122`）：RT2 判"双入口分叉不成立（两区 ps1 都在）"；本班当时未复验（GBK 坑）⇒ 降为待复验，新增 W-141＝取 xml 判真伪；"若确为单入口则撤销该项呈裁"。
- X-32 前测（`review_int_number_audit.md` I7 行，194 行起）：已录 `\ZephyrAlpha_PostSettlement` ACTION=conhost 直调 python `run_post_settlement.py`，与本卷独立复测一致（见 §2）。
- 在册判据（本仓纪律）：⚑呈待裁前必检索是否已裁——dossier_H H-23 行在册：`#ARCH-DAILY-CYCLE-GAP23-001` status=decided，但"裁的是 GAP-2/GAP-3 施工登记，未裁'计划任务 ACTION 改指'"（该句为 dossier_H 在册原文转述，非本卷新裁）。

## 1. 在册盘后/盘前任务枚举（实测）

枚举命令：`cmd //c "schtasks /query /fo csv" | iconv -f GBK -t UTF-8 | grep -i zephyr`（全盘 429 行任务，Zephyr 族约 50 条）。取与盘后/盘前时段相关的 10 件：

| 任务 | 下次触发（实测读数） | 时段属性 |
|---|---|---|
| ZephyrAlpha_PostSettlement | 2026/9/28 15:30（周一-五，PT30M 时限） | 盘后（被检主对象） |
| ZephyrAlpha_PaperSession | 2026/9/27 9:25 | 盘前/开盘 |
| ZephyrAlpha_ConfigCheck | 2026/9/27 8:05 | 盘前 |
| ZephyrAlpha_QMTWatchdog | 2026/9/27 8:45 | 盘前 |
| ZephyrAlpha_DecisionChainSentinel | 2026/9/27 9:40 | 盘中 |
| ZephyrAlpha_SimBridgeExecute | 2026/9/27 9:35 | 盘中 |
| ZephyrAlpha_IndexMinuteEOD | 2026/9/27 15:10 | 盘后 |
| ZephyrAlpha_SectorSnapshot | 2026/9/27 16:40 | 盘后 |
| ZephyrAlpha_TTLRejudgeDaily | 2026/9/27 18:05 | 盘后 |
| ZephyrAlpha_NightlySentiment | 2026/9/26 22:30 | 夜间 |

## 2. ACTION 原文（逐任务 `/xml` 的 `<Exec>` 节点，照录）

1. **ZephyrAlpha_PostSettlement**（争议对象）：
   - `Command` = `C:\Windows\System32\conhost.exe`
   - `Arguments` = `--headless -- "C:\Windows\System32\cmd.exe" /c cd /d "D:\ZephyrAlpha" && "C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe" -u "D:\ZephyrAlpha\scripts\run_post_settlement.py" >> "D:\ZephyrAlpha\data\runtime\post_settlement_last_run.log" 2>&1`
   - `WorkingDirectory` = `D:\ZephyrAlpha`；Triggers=周一-五 15:30（StartBoundary 2026-09-24T15:30+08:00）；ExecutionTimeLimit=PT30M
   - **单 Exec、直调 .py，不经任何 .ps1**。与 `scripts/register_post_settlement_task.ps1:36-48`（logPath/action 拼装，:43 注记"conhost --headless"）**逐字段一致**⇒ 任务态=登记器设计态。
2. ZephyrAlpha_PaperSession：`powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\ZephyrAlpha\scripts\start_paper_session_daily.ps1"`（单 Exec）
3. ZephyrAlpha_ConfigCheck：`Python312\pythonw.exe -m zephyr.infra_ops.config_effect_checker`（单 Exec）
4. ZephyrAlpha_QMTWatchdog：`powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\ZephyrAlpha\scripts\qmt_watchdog.ps1"`（单 Exec）
5. ZephyrAlpha_IndexMinuteEOD：`conhost.exe --headless -- cmd.exe /c cd /d D:\ZephyrAlpha && pythonw.exe "D:\ZephyrAlpha\scripts\data\collect_index_minute_eod.py" >> "D:\ZephyrAlpha\logs\index_minute_eod.log" 2>&1`（单 Exec）
6. ZephyrAlpha_SectorSnapshot：`pythonw.exe "D:\ZephyrAlpha\scripts\data\run_sector_snapshot.py"`（单 Exec）
7. ZephyrAlpha_TTLRejudgeDaily：`wscript.exe "D:\ZephyrAlpha\scripts\launch_hidden.vbs" "D:\ZephyrAlpha\scripts\run_ttl_rejudge_daily.ps1"`（单 Exec，vbs 包装非分叉）
8. ZephyrAlpha_NightlySentiment：`python.exe scripts/data/run_nightly_sentiment.py`（单 Exec）
9. ZephyrAlpha_DecisionChainSentinel：`pythonw.exe "D:\ZephyrAlpha\scripts\governance\decision_chain_sentinel.py"`（单 Exec）
10. ZephyrAlpha_SimBridgeExecute：`powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\ZephyrAlpha\scripts\run_sim_bridge_execute_daily.ps1"`（单 Exec）

⇒ **10 件在册盘后/盘前任务全部单 `<Exec>`；无任何一件存在两个并行动作入口。**

## 3. "双入口分叉"判定

**判：作为"运行态双入口分叉"——伪；作为"磁盘面存在第二个孤儿入口脚本＋头注声明漂移"——有一桩真实但降级的卫生案。** 证据链：

1. 任务侧唯一入口：PostSettlement 的 ACTION（§2-1）直调 `run_post_settlement.py`，调度器**从不**经过 `run_post_settlement_daily.ps1` ⇒ 不存在"任务可能走 A 也可能走 B"的分叉。RT2 的"不成立"方向对，但其论据"两区 ps1 都在"不是判据（都在≠都被调度）。
2. X-32 的"cmd 直调 python 绕过 ps1"与 §2-1 实测一致——两说在"任务走 .py"这点上同真，不互斥。
3. 原呈第二子句"**两区日志路径都不存在**"——**伪**：
   - `D:\ZephyrAlpha\data\runtime\post_settlement_last_run.log` **存在**，5673 B，mtime **Sep 25 15:30**（＝任务 09-25 真跑过并写出）；
   - `D:\ZephyrAlpha\.runtime\logs\post_settlement.log`（ps1 内日志路径）**不存在**——但这恰因 ps1 从未被调度，非"双入口"证据。
4. 残存的真实病灶（降级为工程卫生，不配 Owner 门位）：`scripts/run_post_settlement_daily.ps1`（878 B，mtime 08-22）头注 `[CONSUMERS] Windows scheduled task ZephyrAlpha_PostSettlement (daily 15:30)` **声明漂移**——它自称是任务的消费者入口，实测任务不叫它；两入口语义亦有差（ps1 带 `--if-trading-day` 守卫＋另一日志路径；任务直调不带该旗标，靠 CLI 自解非交易日 SKIPPED，见 `register_post_settlement_task.ps1` 头注与 `run_post_settlement.py:162/:493-494` 实测）。修法＝退役该 ps1 或改锚声明，属 W-156 孤儿件治理同类，**零门位**。

## 4. 结论与撤销建议

- **"双入口分叉"作为 ⚑-1② 的呈裁前提：证伪**（调度器单入口、确定走 .py、且该入口日志实存、任务在跑）。
- **建议：撤销该呈裁项**——"ACTION 指向要改指统一入口"无的放矢：现 ACTION 已是唯一在册入口且与登记器一致；要改的不是"指向"而是"清掉那个假称自己被调度的 ps1"。按在册纪律（证伪要撤案），⚑-1 定稿时第②项应改为：删除/降档，衍生工程项并入 W-156（孤儿件治理）与 93 册相应行订正；X-62 的"降为待复验"可凭本卷闭环。
- 附注：本卷未做（也无需做）任何 `/change`；若 Owner 未来处置该 ps1，必经其门位流程，与本判定无关。

## 5. verified（实测）

1. 10 任务 `/xml` Exec 原文（§2，命令 §6-cmd2）；全部单 Exec。
2. PostSettlement ACTION 与登记器 `register_post_settlement_task.ps1:36-48` 逐字段一致（原文直读）。
3. `post_settlement_last_run.log` 存在/5673 B/mtime 09-25 15:30；`.runtime/logs/post_settlement.log` 不存在（`ls` 实测）。
4. `run_post_settlement_daily.ps1` 在盘（878 B，ls 照录 mtime "Aug 22 02:42"）；其 `[CONSUMERS]` 头注与 `--if-trading-day` 语义直读。
5. `run_post_settlement.py` 支持 `--if-trading-day`（:162/:493-494）但任务参数未带——两入口行为差属实（只影响"若走 ps1 会怎样"的反事实，不影响 §3-1 判定）。
6. 全盘任务 CSV 枚举 429 行（含同名多行=复数 trigger 的正常现象，如 IntradayFundFlow 5 行）。

## 5-b. assumed（未测项）

1. 同名多行任务（如 `ZephyrAlpha_BeltDaemon` 出现两次）按"一个任务定义、CSV 每 trigger 一行"理解，未逐一 /xml 展开（非盘后/盘前主责窗口，且与被检命题无关）。
2. 主仓 dev 若在本卷落盘后改了 register 脚本，则 §2-1 一致性需复跑；判据命令已留 §6。
3. "两区"若指车道/主仓两工作树而非"两入口"，原呈语义更不成立（任务只挂在 `D:\ZephyrAlpha` 主仓路径，WorkingDirectory 实测）——两种读法均不救活"分叉"说。

## 6. 复算命令

```bash
# cmd1 枚举（GBK→UTF-8 转码，只读）：
cmd //c "schtasks /query /fo csv" | iconv -f GBK -t UTF-8 | grep -i zephyr
# cmd2 逐任务取 ACTION 原文（本卷所取 10 件同名替换）：
cmd //c "schtasks /query /tn ZephyrAlpha_PostSettlement /xml" | iconv -f GBK -t UTF-8 | sed -n '/<Exec>/,/<\/Exec>/p'
# cmd3 日志存在性：
ls -la "D:/ZephyrAlpha/data/runtime/post_settlement_last_run.log" "D:/ZephyrAlpha/.runtime/logs/post_settlement.log"
# cmd4 登记器对照：
sed -n '36,48p' scripts/register_post_settlement_task.ps1   # 车道或主仓同文
# cmd5 孤儿 ps1 声明与语义：
sed -n '1,20p' scripts/run_post_settlement_daily.ps1
# cmd6 反事实核对（.py 是否认 --if-trading-day）：
grep -n "if-trading-day\|if_trading_day" scripts/run_post_settlement.py
```
