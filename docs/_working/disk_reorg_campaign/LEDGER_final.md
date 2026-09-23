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
