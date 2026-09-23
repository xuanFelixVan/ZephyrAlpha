---
ttl: task_bound
completes_when: 八包监控收官（本包 0600-VERIFY-PASS 或其 FAIL 闭环+批注清零+终报+自动化自删）
session: st-backup-cold-20260924
creation_token: eight-pack-commander-ledger-ledger-final-20260923
---

# st-backup-cold 台账（总指挥代开）
【总指挥批注 R1·00:35】你的 f9c2024074（restore.ps1 段日目录感知+磁盘减压收尾）已落地验收过 ✓。但你的台账此前未建——已代开此文件，后续你的每轮心跳/进展/待裁定都写这里（30 分钟制我读）。当前请续报：冷抽屉全盘 hash 是否收尾？mirror 差分进展？双证齐即按已批删除链执行。

【续报 R1·01:35 回执】R1 所问三项全部已完成（本包上任即收口，详证=a1_ledger.md 备份冷储总包班段）：
①冷抽屉全盘 hash：finished_at 09-23 23:14:24，正本 G:/backup ≡ 冷抽屉 G:/zephyr_cold 全 5 件 sha256 逐位等值（data.vhdx=f963a773…b77b）——证一成立。
②mirror 差分：09-24 00:0x 完成，46GiB 逐 16MiB 共 2944 块，唯一疑点块（40.75GiB）经逐字节法证=prefix_truncation（417 万差异字节全部 mirror 侧为零），独有字节集合=∅——证二成立。
③双证齐→删除链已执行：删 G:/zephyr_backup_mirror/ 净腾 591.57GB，G 空闲 228.4→819.9GB=22.0%（≥20% 停手线触发，冷抽屉留 10-21 原排期禁动）；注册表新口径已落册 commit 364aefa2（三份等值口径作废+WizTree 方法论注记）。证据包=G:/backup/predelete_deltas/G_zephyr_backup_mirror_torn_evidence_20260924/。
【心跳 01:35】干完=总令五任务①-⑤+三 commit（d2afbd43 假绿闸/364aefa2 注册表/f9c20240 verify 治本）；在干=F/G 两盘定义对账审计（F 已完：冷库 274.5G+CH 两件 1143.76G+新发现 zephyr_c4_pdf_cache 52.7G 与个人文件 0.99G 待总指挥定性；G 已量 5/9 项，60_mirror/嵌套/working_vault/会话目录 USB 盘磨盘中）；卡住=无。下一步=①挂 30 分钟监控自动化（本轮即挂）②扫描出数后补全审计表③06:20 后验 DailyBackup 首个完整轮（report+20260924 vault/dumps 目录+state=backed_up）。
【监控自动化】已挂+下次触发时间=02:09:40（automation-9e033ca5-156e-4b78-8e47-840fe27a67c1，每 30 分钟一轮 */30；收官判据/自删序在 prompt 内）；触发条件②原删除链触发已关闭勿重跑。

【总指挥三裁定执行回执 01:5x】三件新发现全部闭环：
①F:/zephyr_c4_pdf_cache 52.7G→已迁冷库：入库四步（drawers.jsonl 第 8 行登记先行）→同卷 mv 原子移位至 F:/zephyr_cold/50_archive/by_project/zephyralpha_c4_exam_pdf_cache（年份分层 2017-2021 保留原名，snake_case 合规）→验证 60,245 件/56,591,048,267B 件数字节全等+20 件 sha256 抽样全等；F 根目录该项清零。
②F:/个人文件 0.99G：Owner 已亲迁 E 盘，F 侧已不存在，账面确认清零。
③G:/zephyr_cold 五会话目录：F/G 双侧逐目录件数字节全等（G=迁移镜像副本）→五个目录整体 6.2MiB（1839 件，RECEIPT/补丁/对抗测试输出全保）归档至 F:/zephyr_cold/50_archive/by_project/zephyralpha_session_workdirs_final3_20260918_19→验证全等→F/G 双侧原件删除，残留检查零；drawers.jsonl 第 9 行登记。
【心跳 01:5x】干完=三裁定执行+G 盘审计 5/9 项；在干=60_mirror/嵌套 zephyr_cold du 磨盘（USB HDD 慢，自动化轮巡收割）；卡住=无。下一步=补全审计表→06:20 后 0600 验收→候批注。

## 收官前终态（03:50，st-backup-cold-20260924）

### 红蓝对抗+修复战果（子代理并发施工）
- 红队①reconciler：16 发现（P0×2/P1×7/P2×7）→ **10 项已修**（P0-1 半修=state 真源 stdout 锚定、P1-3 lock-skip 反转、P1-4/P2-10 探针复查、P1-7 skipped 分因、P1-9 endpoint fail-closed、P2-12/13/14a/14b/15a/15b、P1-8 半修 CAS 写）+ commit 47e9673e
- 红队②PS1 栈：21 发现（P0×1/P1×7/P2×13）→ **6 项已修**（R1-P0 pg/sqlite 日期目录感知、R2 DROP 前验 base、R3 inc 带 base_backup+失败响亮、R6 ON_ERROR_STOP、B1 预检真实盘族、B2 聚合状态、B3 dual-write --timeout 14400（第二链自愈真凶=30s 超时）、B5 retention 读配置、B10 注释）+ 同批
- 红队③证据链独立审计：**7/7 全 PASS**（哈希链/两证数字/C4/会话归档/台账引用零抄错）
- 其余 21 项入加固 backlog（见下），均为结构性/需 Owner 窗口/任务重注册类，无一项是"需裁定"

### 收官仪表（verify_suite.py 31 项）
- **Round D 31/31 全绿 + Round E 31/31 全绿 = 连续两轮零问题 ✓**（Owner 判据达成，0600 验收前基线）
- 覆盖：单测44/ruff/commit 祖先/注册表口径/残件区不存在/G 空闲/证据包 sha256/两证 JSON/drawers 9 行/C4 终态/会话归档/个人文件/PS1 语法 ASCII/config 键/reaper 护栏/台账/防复活哨兵

### G 盘审计终表（实测收齐）
| 项 | 实测 | 定性 |
|---|---|---|
| backup\ch_vm_backup | 591.57GiB | 定义内（现行镜像） |
| backup\working_vault | 1,328,858 件/239.9GiB | 定义内（14 天版本化，较 09-21 种子 200G 增长属正常滚动） |
| backup\offrepo | 273.62GiB | 定义内（G⑥ 翻倍待核） |
| backup\db_dumps+git_bundles+predelete_deltas | ~2.5GiB | 定义内 |
| ch_backup_disk2.vhdx | 503.2GiB | 定义内（第二链） |
| zephyr_cold0_mirror | 98,037 件/293.8GiB | 定义内（F 冷库 327.2GiB 的夜镜像，C4 迁入后次夜 /MIR 追平） |
| zephyr_cold\zephyr_cold 嵌套 | 97,714 件/274.49GiB | 已签阶段5-⑤解析归位（与 a6 在案数字分毫不差） |
| zephyr_cold\{00-50,90} 原抽屉库 | ~137.6GiB（a1 迁移记录） | 已签 10-21 删 |
| zephyr_cold\ch_vm_backup 冷抽屉 | 591.57GiB | 已签 10-21 删 |
| 会话目录×5 | 0（已归档清除） | ✓ |

### 蒸发战争记录（cross-session，归维护班根治）
- 364aefa2(直落)→被传送带落袋重建甩链悬空；78d4b985(直落)→被 c5b70a8ff8(st-audit-all, stale-index)回退；ad574f63(重落)→被 53cdc66e06(st-align-dirty 翻译批)再回退；d12f3196(三落)+后续核验存活中
- 队列死信定性：q-0001=外来暂存吸收型**禁复活**；q-0003/0004=registry 三向合并地雷族（内容已直连重落）**禁 requeue**；q-0005=被 47e9673e 直连吸收型，落袋即 noop 或死信均**勿 requeue**
- capability 册 token 缺口：eight-pack-commander-ledger 第 5 行条目因 REGISTRY-MASS-DELETION 正确拦截（stale 副本含 14 行净删）暂缓，待维护班修册后按 drawers 同款补登
- verify_suite 已把"注册表口径在 HEAD+State saved 通道+无 sleep 字面"设为常查哨兵，任何再蒸发下一轮即红

### 加固 backlog（11 项，非阻塞，均有处方）
T1 SLO 哨兵接入计划任务 action｜T2 计划任务 S4U 化｜T3 logs 轮转｜B4 skipped 不覆写 ok｜B6 sudo NOPASSWD 确认｜B7 锁 PID 探活｜B8 长任务拆分（g_mirror 周级化）｜B9 G/D 空间闸扩展｜B11 ASYNC 超时孤儿核销｜R4/R5/R7 restore 双链枚举与 code 恢复排除状态文件｜V1 周六 VM 备份错峰+state 原子化｜P0-2 结构修（backup_log 核验下沉 ps1）+P1-5 钟差监控+P1-8 ps1 侧原子写——补偿控制=本包 30 分钟监控自动化在岗
