---
ttl: task_bound
---

# 安全施工清单 v3 — 备份总仓落 G + 冷储专项落 F（2026-09-21 Owner 定案）

> 架构定案（Owner 2026-09-21 拍板）：**D=生产；F=冷储专项（纯冷库）；G=备份总仓（一套完整备份）；offsite=Owner 手动月度拿第三块盘离场**。此组合=标准 3-2-1（3 副本 D+G+离场 / 2 介质 内置+USB / 1 离场）。
> 与旧方案关系：W1（尸体表）/W2（日志 TTL）/W3（冷储迁 F）/影子滚动归档与本章**完全兼容，在飞团队继续干**；被取代的只有旧 W4（备份层归宿），由本清单阶段 4 取代。
> 启动条件：在飞团队手上批次收口 + Owner 6 项签字（INV-RET-002 修订/尸体表处置/vhdx 压缩复决/text_log 级别/offsite 盘采购）。工作目录：docs/_working/disk_reorg_campaign/，台账 a1_ledger.md。
> **排期定案（Owner 2026-09-21）：收口当晚立即开工，通宵连跑阶段 0-4（约 10-17h，含 vhdx 压缩若 Owner 在场），次日白天收尾 5/6/8。删除类动作全部垫观察期自动到期（7-30 天），不占工时、不需人守。**

## 安全施工通则（每阶段逐条自检）

1. **先 copy → 后 verify → 最后才动源**：源目录永远最后删，删前留观 ≥7 天（冷储原件 30 天）；任何删除先出清单留档。
2. **每阶段一个回滚点**：配置改动单 commit 可 revert；搬运保留源；删源前 ls -R 清单存台账。
3. **对账三件套**：文件数 + 字节数全量比对 + 5% 抽样 hash；三项全平才算过。
4. **失败即停**：任何对账不平/探针红 → 停本阶段 → 登记原因 → 换下一独立阶段，禁硬闯。
5. **停机窗集中**：CH 重启（阶段2）与 VM 挂载（4.7）与 vhdx 压缩（阶段7）尽量合并同一维护窗。
6. **全程台账**：每步记 时间/动作/实测数字/证据指针；每阶段完跑自审循环（连续两轮 0 问题才进下一阶段）。
7. **数据第一公理**：任何 drop/删除前必须有两份验证过的副本。

## 阶段 0 · 前置与基线（半天，不动任何数据）

- [x] 0.1 ✅st-disk-ch-20260921 甲线 WO-1/WO-2 已落地（226db0d2bc/363e4fa1ed）；6 项签字=裁定#380/#381 十项全批在册
- [x] 0.2 ✅st-disk-ch-20260921 survey_result.json（五盘/CH parts/日志表基线）+ a1_ledger 21:55 行
- [x] 0.3 ✅st-disk-ch-20260921 09-20 00:43-05:15 全链实跑（CH 增量 ok/报告 backup_report_20260921_004339.json）
- [x] 0.4 ✅st-disk-ch-20260921 09-20 00:20 暂停→05:15 恢复 Ready（声明板 done 行）；阶段4 迁移期将再暂停

## 阶段 1 · 冷储主库落 F（与在飞团队 W3 同源，若已做则核对后跳过）

- [x] 1.1 ✅st-disk-ch-20260921 09-20 23:16 robocopy 8 分钟/263MB/s/对账 PASS
- [x] 1.2 ✅st-disk-ch-20260921 09-21 13:36 迁移 95,188 文件/137.6G/31 分钟零失败（60_mirror 镜像区排除随迁；5 个 ff 遗留目录~10MB 随迁登记）；G 侧只读保留 30 天至 2026-10-21
- [x] 1.3 ✅st-disk-ch-20260921 09-20 23:28 对账 PASS（2211 文件/字节全等/110 件哈希）；drawers 核对随 1.2 补
- [x] 1.4 ✅st-disk-ch-20260921 6684ba5d83 改齐 7/8（services_registry 探测器归仪表盘批，E 留观期内安全）；残留唯一=历史裁定原文（豁免）
- [x] 1.5 ✅st-disk-ch-20260921 archiver 新家 stats()/manifest 2213 条全读；DuckDB 抽查随 1.2 后补
- [x] 1.6 改名 deviations：E 侧保持原名留观（.migrating 改名会使 dashboard 旧探测器红），登记 2026-10-20 到期删——探测器切 F 后同批改名

## 阶段 2 · CH 日志滚动永久化（最急，独立 30 分钟小窗；若在飞团队已做则跳过）

- [x] 2.1 ✅st-disk-ch-20260921 config.d/zz_log_rolling_diskch.xml（合并验证绿；MergeTree 日志无 max_size 轮转概念=TTL+level 即体积治理，记录口径）
- [x] 2.2 ✅st-disk-ch-20260921 09-20 23:05:33 闪断窗执行秒级复活（声明板 done）
- [x] 2.3 ✅st-disk-ch-20260921 09-21 19:27 复测：20.4h 日志合计 1.02G（外推 ~1.2G/天，略超 1G 系当日 250+ 分区归档/演练/备份Repair 活动噪音；text_log 本体 1.4G→0.28G/天=information 修复 5 倍生效实锤）；明日无修库活动数字为干净基线，滚动归档自动续评

## 阶段 3 · CH 库内清偿（W1）

- [x] 3.1 导出半 ✅st-disk-ch-20260921 13/13 双副本+行数+sha256 全等（waste_table_export_manifest.yaml）；**drop 等 Owner 晨批（裁定#382 逐表批制）=等待项**
- [x] 3.2 ✅st-disk-ch-20260921 09-21 滚动归档有界循环 24 轮：冷线/etf 过线分区全链归档（TI 按契约排除）；manifest append-only 留痕
- [x] 3.3 部分 ✅st-disk-ch-20260921 VM 内部空闲 134.7G（+冷线归档释放）；尸体清零与 ≥200G 终验等 Owner 逐表批（35.4G）+TI 19.4G 甲线回落

## 阶段 4 · 备份总仓落 G（新架构核心）

- [x] 4.1 ✅st-disk-ch-20260921 G:ackup\{working_vault,db_dumps,git_bundles,offrepo,ch_vm_backup} 骨架建；昨夜 G 镜像五目标同卷改名到位（db_dumps/git_bundles/offrepo/ch_vm_backup→G:ackup\*，zephyr_cold→G:\zephyr_cold0_mirror\zephyr_cold_main 作 4.6 种子）
- [x] 4.2 ✅st-disk-ch-20260921 种子 09-21 18:53 完成（1,156,584 文件/200.7G 逻辑量/零失败；跨卷硬链接展开已知成本）；对账三件套 **PASS**（双侧 1,156,584 全等+57,829 件哈希零失败）；config 三切已落（本表 4.3/4.5 同批）；F 旧 vault 留观 7 天至 09-28
- [x] 4.3 ✅st-disk-ch-20260921 G:\backup\db_dumps 数据就位（昨夜镜像迁移+今日同卷改名）；config 切换随 4.2 种子完成后原子批
- [x] 4.4 ✅st-disk-ch-20260921 G:\backup\git_bundles 就位；git_bundle.base 配置化+STAGE 3b 补丁已落（PS1 OK）
- [x] 4.5 ✅st-disk-ch-20260921 G:\backup\offrepo 就位（137G 同卷改名）；offrepo_backup.base 切换随原子批
- [x] 4.6 ✅st-disk-ch-20260921 种子就位（60_mirror\zephyr_cold_main 592G 期内容）+STAGE 3d per-target 改址补丁（PS1 OK）；首夜全量对账随 4.8 实跑
- [x] 4.7 ✅st-disk-ch-20260921 09-21 **零停机达成**：SCSI 热挂 G:\ch_backup_disk2.vhdx（1TB 动态）免停 VM；VM 内 mkfs(8) ext4（首格 mkfs D 态卡死系种子占满 G 盘 IO，残留清后重格成功）+挂载 /mnt/chbackup2+fstab(UUID,nofail) 持久化；CH backups2 盘 config.d/backup_disk2.xml+SYSTEM RELOAD CONFIG 激活；权限 chown clickhouse；第二链写读清全链验证（fetch_perf 103 行 RESTORED）；backup.ps1 CH 段增双写 rsync 步+首跑 inc.zip 71G 入 G 链；market.zip 基线同步在飞
- [x] 4.8 ✅st-disk-ch-20260921 09-21 20:05 换 G 实跑（CH 增量 90.3GiB verified+双写 96.9G 入 G 链+vault 快照落 G:\backup\working_vault\20260921+db_dumps\20260921+bundle 447M+offrepo 冷档 136.88G）；3d 段解析缺陷修复后手工收口收敛；DailyBackup 已恢复 Ready（06:00 起全自动全绿复验）

## 阶段 5 · CH 现役备份盘处置 + F 纯化

- [ ] 5.1 双写稳定运行 14 天后：`ch_backup_disk.vhdx` 退役评估——停 VM 摘盘 → 转 G 归档或删（F 彻底纯冷库）；保守派可保留三链过渡一个季度
- [ ] 5.2 `F:\ch_vm_backup` 635G 处置（Owner 已在 A 保留/B 瘦身/C 退役中拍板；默认建议 B 瘦身为配置级轻备份，C 退役须三处同步：删目录+退 backup_ch_vm.ps1+退 restore.ps1 vm 模式+退 config 条目）

## 阶段 6 · 宿主清偿（W5+W6）

- [x] 6.1 ✅st-disk-ch-20260921 09-20 00:35 机械分类清偿 35.15G（>24h+非活跃会话两轮 chmod；memo_recon_20260920 若存活=豁免核对中）
- [x] 6.2 ✅st-disk-ch-20260921 有引用（ml_train/run_sft_train 等 4 脚本+测试）→按 a0 W5 有引用登记处理保留 D 盘
- [x] 6.3 ✅st-disk-ch-20260921 db_dumps 版本化 14 天滚动落地（config+STAGE 3）；D:
onexistent 8KB 登记遗留
- [x] 6.4 ✅st-disk-ch-20260921 2019_bundle 29,998=29,998 已核[转报 dataqa]；E 删 ≥2026-10-18 等待
- [x] 6.5 ✅st-disk-ch-20260921 D=61G 达标（09-20 00:40 实测）
- [x] 6.6 ✅st-disk-ch-20260921 offsite_monthly_manual.md 落档（第三块盘月度流程六步+红线+加演条件；建议采购 ≥2T 专盘）

## 阶段 7 · vhdx 压缩（Owner 在场窗，与 4.7/2.2 尽量合并维护窗）

- [ ] 7.1 前置：F/G 备份新鲜 + VM 内空闲 ≥150G 核对
- [ ] 7.2 停 VM → 管理员 Optimize-VHD -Path D:\HyperV\VMs\zephyr-ch\data.vhdx -Mode Full → 起 VM
- [ ] 7.3 全链健康探针：表 count 抽查 + dashboard + 一条 tick 查询
- [x] 7.4 ✅st-disk-ch-20260921 --precheck 挂 STAGE 4b+两日预检单在盘（裁定#380④ 提醒条目，禁执行）
- [ ] 7.5 验收：vhdx 文件 ≤450G + 内部空闲维持 ≥150G + D 剩余显著回升

## 阶段 8 · 终验红蓝（全部阶段后）

- [ ] 8.1 数字对账：五盘容量前后对照表 + CH 热层体量 + 备份链清单（G 总仓全绿）
- [x] 8.2 ✅st-disk-ch-20260921 残留扫描：代码/配置面 E:\zephyr_cold_archive 零命中（历史裁定原文豁免）
- [ ] 8.3 搬运抽 hash 复测（每类抽 10 文件）
- [x] 8.4 ✅st-disk-ch-20260921 三演练：①CH 基线恢复 weather_data（RESTORED+时点行数语义）+第二链 fetch_perf 103 行双验 ②冷储 Parquet 恢复 kline_etf_15min 200502 64/64 行+复 drop 净值零 ③vault 快照 pyproject.toml 哈希=live 一致；报告见 a1
- [ ] 8.5 红蓝一轮：红队攻击=对账假绿/搬运丢文件/引用改漏/TTL 写错日志早丢/backup.ps1 首跑失败隐瞒/双写链只有单链在写
- [ ] 8.6 临时件清 + GitCommitGateway 全落地 + 终局交付报告（终极目标逐条+前后对照表+Owner 待签归零情况）

## 顺序总览（一屏版）

```
在飞团队(兼容批次 W1/W2/W3/影子归档) 收口
  → 阶段0 基线+冻结 → 阶段1 冷储落F → 阶段2 日志TTL → 阶段3 CH清偿
  → 阶段4 备份总仓落G(working_vault/db_dumps/git/offrepo/冷储镜像/CH双写)
  → 阶段5 CH旧盘处置+F纯化 → 阶段6 宿主清偿+offsite手册
  → 阶段7 vhdx压缩(Owner窗) → 阶段8 终验红蓝+恢复演练 → 交付
```


---

## 夜班交接（st-disk-ch-20260921，2026-09-21 19:10）

**只剩一件事卡着：4.2 working_vault 种子**（53G/115.6 万小件，F→G HDD，11:45 点火在飞，robocopy PID 15592）。
完成后顺序（脚本全备妥）：
1. 对账三件套：`python .runtime/tmp/diskch/verify_working_vault_seed.py`（先建：count+bytes+5% hash，源=F:\working_vault，目标=G:\backup\working_vault）
2. 配置三切：`python .runtime/tmp/diskch/switch_configs_to_g.py`（working_vault/db_dumps/offrepo→G + g_mirror 两目标改址，CAS 已备）
3. 4.8 实跑：`powershell -File scripts/backup/backup.ps1 -Force`（首跑会写 G 总仓+STAGE 3d 冷库镜像增量+CH 双写 sync+4b 归档评估）
4. 恢复计划任务：`Enable-ScheduledTask -TaskName "ZephyrAlpha-DailyBackup"`
5. F 侧旧 vault/offrepo 留观 7 天（09-28 到期删）
注意：market.zip(266.6G)+inc.zip(71G) 双写基线已同步完（09-21 15:00 实测两侧同尺寸）；CH backups2 盘已激活并全链验证。
