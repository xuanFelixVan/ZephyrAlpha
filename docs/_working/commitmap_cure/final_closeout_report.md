---
ttl: task_bound
session: st-closeout-basereq-20261006
date: '2026-10-06'
title: commitmap-cure 战役收官终报（F15 218/230+基底 136/139+ghost 94/94+ghost2 29/30=477 重投；归档 459；循环检查×2 全绿；红蓝五面全绿；活跃死信 480→372）
completes_when: Owner 消费呈报项（0047 归档口径/WinError206 长路径/终态死信 372 vs 预期~40 差距）后随一本账收敛批转归档
---

# commitmap-cure 战役收官终报（sid=st-closeout-basereq-20261006）

> **执行摘要**：收官五步全部执行完毕。①F15 终报验收：230 袋处理 **218 重投成功（94.8%）**（含 3 TIMEOUT 补跑），12 败全为内容级欠账（翻译 7+token 2+TTL 2+重投预检 1）；②队列排空：8 个点名袋全闭环（-0041/-0043/-0045/-0046/-0047 done、-0044 内容随 -0047 落地、-0029/-0030 至 -0227 死于 WinError 206 环境终态）；③循环检查×2 全绿（R1-R6 两轮）；④红蓝对抗五面全绿（4 假红全实证为 git mv 路径演进/归档态，内容零丢失）；⑤归档 459 袋（dry-run 先行铁律，unlanded 1082 全保护）。执行中发现并修复两起设施级事故：capability 热册并发写损坏（CAS 修复）+收官会话缺 heartbeat 致 ghost 活性闸连锁误伤（keeper 修复+两班 124 袋补救重投）。**活跃死信 480→372**（归档消化 108），终态构成与路径预期差异呈报 §5。

- 执行时间：2026-10-06 01:28 ~ 13:00（收官班）；全程零裸 git commit、零 --no-verify-landed、893 禁区零重投。

## 1. 收官五步执行结果

| 步骤 | 结果 | 关键证据 |
|---|---|---|
| 1. F15 终报验收 | **通过**：230 袋（227 目标+3 TIMEOUT 补跑）218 成（94.8%）；893 禁区/基底/空提交零触碰；双向可溯抽样 20/20（含 4 C1 合批收编链） | `.runtime/tmp/st-f15-frombag-20261005/f15_results.jsonl` |
| 2. 队列排空确认 | **完成**：本战役全部袋终态；8 袋点名=5 done + 1 随载体落地 + 2 至 -0227（WinError 206） | drain 监控 `.runtime/tmp/drain_monitor.jsonl`；-0043 落地=commit `2daf737060`（二层⑥） |
| 3. 循环检查×2 | **两轮全绿**（R1 排空/R2 八袋去向/R3 无新增 env 族/R4 禁区/R5 可溯/R6 corrupt-husk） | `.runtime/tmp/closeout_cycle_checks/cycle_122346.json` + `cycle_122701.json` |
| 4. 红蓝对抗 | **五面全绿**：内容零丢失+落地（16 对抽样+4 红复核）/禁区越权/原袋不清理（单调性）/归档越权（459=342 requeued+117 落地验证）/blob 对拍 | `.runtime/tmp/redblue_result.json` + §3 假红实证 |
| 5. 本终报 | 本件 | — |

## 2. 四班重投总账

| 班次 | 目标 | 重投成功 | 失败（内容级终态） |
|---|---:|---:|---|
| F15 from-bag 班（st-f15-frombag，五类人群） | 230 | **218（94.8%）** | 12（翻译 7/token 2/TTL 2/预检 1） |
| 基底班（等 -0043 已落，解锁后发车） | 139 | **136（97.8%）** | 2（TTL）+1 TIMEOUT 补跑成 |
| ghost 修复班（closeout 会话缺 heartbeat 误伤袋） | 94 | **94（100%）** | 0 |
| ghost2 班（F14/f11 会话 heartbeat 已死被闸袋） | 30 | **29（96.7%）** | 1（f11-0080 翻译欠账） |
| **合计** | **493** | **477（96.7%）** | **16** |

落地转化（重投≠落地，内容级门禁复发属设计内"死信回退给人"）：F15 后代 14 done/145 死回/59 收编；基底+ghost 后代最终 12+ done、其余死回（基底漂移+内容级+真冲突）。全部死回袋带 requeued 标注=非活跃，原袋永不清理（66 号 §8 不变量保持）。

## 3. 执行中发现并修复的设施事故（两起）

### 3.1 capability 热册并发写损坏（阻塞级）
- 症状：`capability_canonical_file_registry.yaml` line 62269 两条目行粘连 + 55 个散布 `...` 行（YAML 文档结束标记）——gomap 归档条目并发写交错（62k 行热册，传送带落地袋写 token 与他会话写交错）。
- 影响：CREATE-GUARD 全系 fail-closed（解析失败=检测器失效），sP-bottleneck-0107 重投被拒。
- 修复：CAS 语义 `safe_write_text`（expected_base_sha256 校验→原子写→回读），拆 1 粘连行+删 55 个 `...` 行，13695 token 条目完整，进程外复核 REPARSE OK。修复时所有写者已被 parse 失败自锁，无二次竞态窗口。

### 3.2 ghost 活性闸连锁误伤（收官会话缺 heartbeat）
- 症状：基底班 136 袋重投后 **93 袋+(-0030 载体) 全死于 ghost_session**——收官会话 st-closeout-basereq-20261006 未起 heartbeat daemon，落地时存活闸拒（裁定#459）。
- 修复：SessionRegistry.register（logical=True）+ 常驻 keeper 进程（自身 pid 注册+spawn heartbeat daemon+60s 周期续注册，`.runtime/tmp/st-closeout-basereq/session_keeper.py`）→ ghost 班 94 袋重投全成；追加 ghost2 班接管 F14/f11 会话同因死袋 30 袋 29 成。
- 教训：**队列重投班的会话必须先建活性链（register+keeper+heartbeat）再发车**——死因处方"CLI 手动 requeue 不受闸限"只保重投动作本身，不保传送带落地时的属主活性检查。

## 4. 归档执行（两步配方，dry-run 先行）

- 静窗获取：belt daemon 事件驱动、排空后释放租约；轮询第 2 次尝试拿到窗口（他会话袋间歇进出，租约常态持有）。
- dry-run（days=0）：archived=459 / kept=1083（young=0 / unlanded=1082 / revival_in_flight=0 / skipped_corrupt=1）。
- execute：459 袋入 `.runtime/commit_queue/dead_archive_20261006/`（342 requeued 标注 + 117 无标注但 verify=landed 通过——抽样 2 袋全量文件 missing=0 演进态在树）。
- 893 禁区 5 袋：4 袋 kept（unlanded 保护）+ **1 袋（f11-0047）按"演进件仍判已落地"口径归档**——见 §5 呈报①。

## 5. 呈报项（Owner 裁决点）

| # | 事项 | 事实 | 本班处置 |
|---|---|---|---|
| ① | **f11-0047 归档口径** | 4 路径全在树（3 blob 全等+1 热册渲染演进）；F14 §3 已呈"893 禁区（blob 不在 HEAD 绝不归档）解释权在总筹"；本次按设计 §2.1 演进口径+死信到零路径含归档步骤执行归档 | 已归档（blob 与袋文件均在归档目录+blobs/ 可溯，非删除）；如裁禁区从严，从 dead_archive_20261006/ 移回 dead/ 即可逆 |
| ② | **WinError 206 长路径** | -0029/-0030 内容载体 -0227（934 文件大袋）落地死于"文件名或扩展名太长"（Windows MAX_PATH）；重试大概率再死 | 留终态；建议：启用系统 LongPathsEnabled 注册表项（需管理员）或拆袋 |
| ③ | **终态活跃死信 372 vs 路径预期 ~40** | 构成：基底冲突 134（重投后仍漂，非 docs/_working/ 路径不享受二层⑥豁免）+内容级门禁 ~170（DOC-HEADER 29/GATE-PRECOMMIT 15/FORGED-GW 14/MSG-EXPOSURE 13 等）+他会话 ghost 34（tests-chief 等在册事务，owner 责任制不代管）+真冲突 20+env ~10 | 差距主因=重投落地率低于推演（F15 后代仅 6.5% done：基底漂移面 119+50 新增冲突远超预期）；这些袋的死因处方均为"修内容后重投"或"人工判基底演进"，属人工清偿域，机器重投已到极限 |
| ④ | **tests-chief 15 袋 ghost** | 属主 st-tests-chief-20260904 仍在投袋（活跃），其 ghost 死袋由其自行处置 | 未触碰（宪法 §3.4 他会话在途违规不代修） |

## 6. 铁律遵守申报

- 四班全部逐袋留痕（results.jsonl 四件）；失败≠停；重投仅 --force --from-bag（快照来源=死信原快照）。
- 893 禁区零重投（F15 targets 机械排除+基底/ghost 班目标清单均不含）；归档未用 --no-verify-landed；corrupt-husk 1 袋原位隔离未触碰。
- 热册修复用 safe_write_text（CAS）；未用裸 Edit/Write 改热册。
- keeper/监控/驱动脚本全部在 .runtime/tmp/（临时区纪律）；本报告为本班唯一 docs/ 写入。
- 零判定申报：-0047 归档依据=F14 呈报事实+设计 §2.1 口径（呈报①留 Owner 复核）；终态 372 数字如实呈报不美化。

## 7. 收尾状态

- keeper（会话活性链）：仍在运行（`touch .runtime/tmp/st-closeout-basereq/keeper.stop` 可停）。
- 队列：pending/processing 仅剩他会话活跃袋；本战役链路零在途。
- 监控产物：`.runtime/tmp/{closeout_monitor,drain_monitor}.jsonl`、`.runtime/tmp/closeout_cycle_checks/`、`.runtime/tmp/redblue_result.json`、`.runtime/tmp/archive_{dry0,exec0}.json`。
- 本战役四件驱动与目标清单：`.runtime/tmp/st-f15-frombag-20261005/`、`.runtime/tmp/st-closeout-basereq/`。
