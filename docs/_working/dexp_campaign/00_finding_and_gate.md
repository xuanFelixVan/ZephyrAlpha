---
ttl: task_bound
---

# D 盘应急·调查与分诊终局呈报（sid=st-dexp-20261009，2026-10-09）

> 一句话：**指令卡的核心前提被实测证伪——D 盘危机不在本仓，在 `D:\HyperV` 里一只虚拟盘；
> 但那只盘的压缩收益不是我一开始算的 160G，本仓自己的实测记录是 42G，
> 而且今晚不该做。**

## 0. 对本文件初版的自我更正（重要，勿以初版数字排窗）

我在 11:2x 生成的初版 §3 写过"压缩可回收 ≈160-170G"。**该数字作废**：它是用
"guest 空闲空间"倒推的理论上限，而本仓有明文反对据这种估算排窗的记录——
`docs/_working/disk_reorg_campaign/a6_remaining_work_order.md:108`：
「原估算作废禁按其排窗 … 实测回收仅 **≈5.5 GiB**；本行以此为唯一有效口径」。
读完两份实跑日志后真相更清楚：**该行的 5.5 GiB 是 09-28 那次实测，但该行写于 09-29，
早于 09-30 那次 42.16 GiB** ⇒ 它是"过期"不是"错"，也不支持我的 160G。有效区间见 §3。
教训同 [[three-hash-calibers-not-interchangeable]]：**别把"空闲"读成"可回收"；
引用旧数字前先查它写于哪一次实测之前。**

## 1. 实测账（每条都可复算，探针见 §6）

| 项 | 实测值 | 备注 |
|---|---|---|
| D: 总量 / 剩余 | 731.2 G / **33.6 G**（起点，96%） | 处置中已升至 39.5G（§5） |
| `D:\HyperV\VMs\zephyr-ch\data.vhdx` | **586.5 GiB**（Dynamic，虚拟上限 600 GiB） | **占全盘 80.3%** |
| `D:\ZephyrAlpha` | **88.61 G** | 12.1% |
| ├ `.runtime` | 45.30 G（`.runtime/tmp` 34.37G / 68.5 万件） | **总队 H 批地盘，我未碰** |
| ├ `.aidrafts` 106 棚 | 27.73 G | 本战役分诊面 |
| ├ `data` | 5.33 G | 生产库，红线禁碰 |
| ├ `.worktrees` 20 个 | 4.53 G | 本战役分诊面 |
| └ `.git` | 3.03 G | 各 worktree 共用对象库 |
| VM 内 `df /` | 589G 总 / 397G 用 / **162G 空** | guest 侧 |
| CH `system.disks.default` | 588.48G 总 / **161.42G 空** | CH 会写爆的面 |

VM 身份已坐实＝**生产库本体**：`zephyr-ch` State=Running；宿主多个进程 ESTABLISHED 连
`172.24.30.100:9000`（ClickHouse 原生口）；`src/zephyr/infrastructure/redis_config.py:22`
记 Redis 同 VM 共存。**属四态里的态④，一律不动。**

## 2. 指令卡三条前提的判决

**① "大件在 .aidrafts，分诊能腾 ≥80G"→ 证伪。**
我全部可分诊面 = 27.73 + 4.53 = **32.26G 天花板**；其中 25 棚有增量（6.09G 须逐件复核）、
10 棚属在岗会话（2.71G 禁动）。**100% 清空也只有 32G，到不了 80G**——这是算术不是力度。

**② Phase 2 情况A（尾部未分配可扩 D）证伪；情况B（缩邻区）物理不可行。**
D 是 **Disk 1（KINGSTON SNV2S1000G，NVMe，931.5G，GPT）第 5 个也是最后一个分区**，
`end=931.5G＝盘尾`，**尾部未分配 0.0G**，且非 vhdx 挂载。
次序：C(0.3→199.5) → Recovery(199.5→200.3) → **D(200.3→931.5)**。
⇒ 缩 C 腾出的空位落在 D 的**前面且隔着 Recovery 分区**，`Resize-Partition` 无法跨间隙向前扩 D；
要接上只能移动 D 起点＝重写下层文件系统，风险远超收益。
`Get-PartitionSupportedSize -DriveLetter D` 本权限下 `PermissionDenied`，分区操作一律需 admin。

**③ "E 220G 空闲可接虚拟盘"不成立。** 586.5G 装不进 E（剩 220.9G）；F/G 空间够但都是
**USB 外置**，且宪法 INFRA-STORE-003 定 F=唯一冷库、G=唯一备份总仓——把生产 CH 数据盘
搬到 USB 备份盘既违分工又砸延迟。

## 3. 压缩这一刀的**真实**价签（本仓实测，非我的推断）

| 项 | 在册/实测值 | 出处（我亲自读到行/跑过查询） |
|---|---|---|
| 09-28 实跑回收 | **5.5 GiB**（643,175,546,880 → 637,269,966,848 B），success=True | `logs/ch_vm_backup_20260927_205312.json` `compaction` 段 |
| 09-28 实跑耗时 | **17,440 s ＝ 4.84 小时** | 同上 `duration_seconds` |
| 09-30 实跑回收 | **42.16 GiB**（637,236,412,416 → 591,971,483,648 B），success=True | `logs/ch_vm_backup_20260930_022243.json` |
| 09-30 实跑耗时 | **15,373 s ＝ 4.27 小时** | 同上 |
| 预检单宣称的窗 | "停机 **60-120 分钟**" | `vhdx_precheck()` 产出的预检单文末 |
| 9 天回填速度 | vhdx 551.3 → 586.5 GiB（**≈3.9 GiB/天**） | 与 09-30 日志对拍 |

⇒ **两笔都真，且是相隔两天的两次实跑，不是台账打架。** 收益**方差极大（5.5 ～ 42 GiB）**，
而**耗时稳定在 4.3～4.8 小时**。`a6_remaining_work_order.md:108` 写"实测回收仅 ≈5.5 GiB；
本行以此为唯一有效口径"，该行日期是 **2026-09-29**——**早于 09-30 那次 42.16 GiB 的实跑**，
所以它当时正确、如今**过期**（不是我初版猜的"两本账矛盾"）。

⇒ 给 Owner 的两个必须纠正的预期：
（a）**收益按 5.5～42 GiB 区间排窗**，绝不是 160G；
（b）**停机时长两次实测都是 4.3～4.8 小时**，预检单的"60-120 分钟"被自家两份日志同时证伪，
照它排窗必然爽约。
（另有一条未定版口径待裁：压缩前红线该锚 `df` 面还是 `system.disks.default` 面，
`a6_remaining_work_order.md:100-102` 明文"本班不改判据不择一"，我不代择；
今日两面实测只差 ~0.4 GiB，历史 11 GiB 分歧今日不可复现。）

唯一可能抬高收益的新事实：我今天在 VM 内跑过 `sudo fstrim -v /`，返回
**"71.2 GiB trimmed"**——动态 VHDX 只认被 discard 的块，trim 后再压缩**或许**比 09-30 收得多。
**这是推断不是实测**，且 fstrim 本身未让宿主掉任何字节（已复测 df）。

## 4. 现在**不该**压缩的三条独立理由（我逐条亲验，不是转述）

1. **CH 备份链正处"无完整增量"的空窗。** `system.backups` 实测：10-05/06/07/08 与
   10-09 01:05→01:37 五连 `BACKUP_CREATED`，但 **2026-10-09 03:30:55Z 起一条
   `CREATING_BACKUP` 仍在写**（我查到 `system.processes` 里该 query 已跑 958s，
   total_size 191.70 GiB），而按 `backup.ps1` 逻辑旧 `inc.zip` 已被删除。
   ⇒ 此刻压缩若出问题，恢复只能退到 10-03 base。
2. **"压缩前先取新鲜 VM 镜像"的执行体已被 Owner 封存。**
   `scripts/backup/backup_ch_vm.ps1:2` 「RETIRED 2026-10-04 (Owner conditional approval)…
   SEALED」，`:147-154` 早退 `exit 0`。既有剧本 `vhdx_quarterly_notice_design.md` 第 1 步
   「F 新鲜备份前置」指向的正是**今晚 21:45-23:00 被摘盘的 F**。
3. **备份冗余正在塌成一份。** `system.disks` 里 `backups` 与 `backups2` 报**同一组数值**
   （1006.85/630.76 完全相同）＝同一文件系统经 `mount --bind`（`LEDGER_final.md:735`）；
   叠加今晚 F 摘盘＝在链路合并的当口再叠一个物理不可逆操作，最坏排序。

3. **备份"双链"此刻其实是单设备。** 我在 guest 内实测 `lsblk`：只有 **`sdd`(1T) 挂在
   `/mnt/chbackup_local`**，而 **`sdc`(1T) 无挂载点**；CH `system.disks` 里 `backups` 与
   `backups2` 报**完全相同**的 1006.85/630.76 GiB（我本人查询）＝同一文件系统
   （`LEDGER_final.md:735` 记 07:58 曾 `mount --bind`）。
   ⇒ 宪法 §5 数据驻留公理要求的安全网当下**不成立**，而今晚 21:45-23:00 F 还要被摘盘——
   在链路合并的当口再叠一个物理不可逆操作，是最坏排序。

**关于那颗红灯**：预检唯一红项 `backup_fresh`（`last_backup_status=failed`）经取证＝
**仪表造成的假红**——`logs/backup_report_20261009_052740.json` 里唯一 failed 节点是
`offrepo_backup/targets/trae_memory`：「source missing: `C:\Users\fanzi\.trae-cn\memory`」
（我复核：`.trae-cn` 存在但其下**确无 memory 子目录**），与 ClickHouse 数据安全无关；
CH 腿当天只是"24h 节律未到"的 skipped。
**但结论不是"绿灯可压"**：红灯该留着，因为上面三条是真阻塞。

另两处**在册缺陷（只上报，未自改）**：
- `vhdx_precheck()` 的 `days_since_last_compaction` 读 `rolling_archive_state.json`，
  而压缩成功记录写在 `data/databases/backup_state.json`（`last_vhdx_compaction_result=ok`）
  ——两本账不同源 ⇒ 该指标**从未生效**、`due` 恒真。
- `_backup_fresh()` 要求 `last_ch_backup_status=='ok'`，而写侧正常态就是 `skipped`
  （整轮节律 8h vs CH 24h）⇒ **完全健康的流水线每天约有 2/3 时间报红**。
  历史为证：09-27 预检单就是红在 `skipped`。
- 机读红线块 `scripts/backup/backup_config.yaml:139-142` 只有 `F: 700 / G: 500`，
  而注释 `:130` 声明的红线含 **D≥50G**——**D 线无机读读者**；当前 D=39.5G 已在线下无人拦。

## 5. 本战役已交付（不等 Owner，全部已跑）

- 校准批：布局+体积归因（§1-2）。
- **126 棚/worktree 四态分诊全覆盖**：态① 91 个/23.88G、态② 25 个/6.09G、态④ 10 个/2.71G。
  在岗 10 棚全是真活队（deadcure chief/g1/g2/promote/restore、chiefc×2、libfront、
  fullflow2、本会话），判据有判别力不是 blanket。
- 判据**双向验真**：注入一枚被 `.gitignore` 命中的 3MB 非垃圾件即翻态②，还原即回态①。
- **查出并修掉我自己一处 fail-open**：`git status` 默认不列被忽略件，而本仓
  `.gitignore:265` 是 `/*`（顶层默认全忽略），且 porcelain 把被忽略目录折叠成 `!! output/`
  一行——初版判据会把"棚内藏数 G 非 dev 内容"误判成可删。已改 `--ignored=matching`
  ＋目录递归展开，并加第二道闸：91 个态① 棚逐个反查 ≥20MB 非 tracked 件，**0 命中**。
- 串行处置进行中：逐件 df 对拍＋每件带 `worktree add <path> <branch>` 回滚命令入账。
  当前 33.6G → **39.55G**（21/91 件）。
- 未用正口 API `WorktreeManager.cleanup_session_worktree()`，因它**连分支一起 `--force` 强删并
  丢弃改动**，比态①需要的"零损失＋可原样重建"更激进；我走非 force `git worktree remove`
  并保留分支（态①判据＝HEAD 是 dev 祖先，分支零独有对象，保留不占额外空间）。

## 6. Owner 只需回这几种话

| 你回 | 我做什么 | 诚实价签 |
|---|---|---|
| **"排压缩窗"** | 交完整执行序（停 VM→admin `Optimize-VHD -Mode Full`→起 VM→探针→df 对拍） | **D 只 +5.5~42G**（非 160G）；**停机实测 4.3h** 非 1-2h；须等 §4 三条解除＋admin 权限（我当前无） |
| **"先把仪表修对"** | 落 §4 三条在册缺陷的修法（预检改读 `system.backups` 新鲜度＝比现判据**更严**；reader 迁移到 E-5 的 sticky `last_success_*`；`trae_memory` 源路径按 RULE-SSOT 回 `config/asset_inventory.yaml` 收口） | 纯观测面，不动安全阀 #1，零数据风险。**但都是改判据，按宪法须你点头** |
| **"只管今晚别塌链"** | 核 F 摘盘后 CH 恢复链是否退化为单份、`backups2` bind 是否解除 | 这是比腾空间更要命的一件 |
| **"要长期方案"** | 出热层归档路线（`technical_indicator` 曾被记为 165.3G 且被 `excluded_tables` 挡在自动归档外＝只涨不缩根因；车道在测今日构成） | 业务资产门位，只出方案不自裁 |
| **"加盘"** | 出规格建议（Disk1 已无未分配，须新物理盘） | **花钱门位** |
| **"分诊继续"** | 走完 91 棚处置＋态② 逐件复核 | 上限 +24G，D 停在约 57G，vhdx 仍以 3.9G/天回填 |

## 7. 红线遵守

未碰 `.runtime/commit_queue/blobs`、未碰 `data/` 生产库、未碰任何态④/态③、未动 G 盘、
未自行停机/压缩/改判据阈值。`.runtime/tmp`（34.4G）属总队 H 批地盘，我只测量未处置。
VM 内执行过 `sudo fstrim -v /`（discard 提示，非删数据，已如实记于 §3 并复测宿主零变化）。
两枚 10-08 遗留的他人 worktree `index.lock` 与他会话在跑的 3 个 git.exe **均未清理**（不代裁）。

## 8. ⑤-c 存量契约普查（机生表；复算命令 `python scripts/governance/wave1a/ch_read_shape_ruler.py --census`）

总统筹批复⑤（b+c 组合）第②步产物。尺沿用 W-180.2 形状尺的同一套路径分级 `_severity_for`
（同真源不另立第二把判据），新增 `--census` 模式；调用点用 **AST** 识别——先前的行正则版
命中 473 处，其中含 `.md` 文档面与注释行（如某册里"禁用 `ch_reader.count()`"这句话本身），
改 AST 后 349 处（另补符号别名/模块别名两种写法，`count as row_count` 第一版会漏计——
由 `test_census_recognizes_imported_aliases` 现抓现修）。

现读数（扫 HEAD 树，普查面不完整=0）：

| 分类 | 处数 | 处置 |
|---|---|---|
| 待迁 strict（判据路径 × 静默契约 `count()/query()/query_table()`） | **49** | 逐件迁 `count_strict()/query_rows()`；这是"未知即抛"翻转前的清零对象 |
| 展示可留（非判据路径） | 248 | 可暂留存量契约，不阻断 |
| 豁免（reader/writer/probe 本体与测试） | 21 | 尺对它们只作 INFO |
| 已在 strict 通道 | 31 | 无需动作 |

待迁面 17 个文件的逐件行号由上表命令现算，勿在本册抄录（抄数必漂移，宪法 §4.3）。
**翻转判据**：待迁 49→0 且普查面不完整恒为 0，才具备"全量未知即抛"呈批条件。

## 9. 指标表体积与增长新证（并更正 02 号件的分区归属）

2026-10-09 19:3x 现读 `system.parts`（active）：`c1_market.technical_indicator` =
**404,316,435 行 / 224.56 GiB**，是 D 盘最大单表（§6 旧记 165.3G 已过期）。按 period 分区体积：
1min 85.9／**daily 43.1**／5min 33.1／15min 23.4／30min 19.9／60min 10.8／120min 5.0／weekly 2.7／monthly 0.6 GiB。

- **可回收集中在 daily 段**：daily 全史键 8,925,969 / 行 23,112,162 = **2.59× 行膨胀**，
  max 7 版/键；去重后约 15.6 GiB ⇒ **理论回收 ≈ 27.5 GiB**（前提：OPTIMIZE 需 VM 内临时空间，
  且回收后仍须 vhdx 压缩才归还宿主）。
- **02 号件原句"A 型（分钟级）另占约 25-30 GiB"的分区归属判错**：2026-08-13 逐 period 实测
  分钟级 dup_ratio 全为 0（已随合并自愈），那个量级的可回收在 **daily 段**——数值巧合，不是同一件事。
  02 号件随袋在途（本班不重投他人袋），更正以本节为准。
- **增源未减**：dwm 指标回填（`scripts/data/tilib_dwm_shard_runner.py`，02:30 计划任务＋手动续跑）
  在 10-08 21:32／10-09 04:42／06:51／10:38 各跑一遍**全史**，旧键照灌（抽样 2026-01-05 的
  `ingest_ts` 最晚=10-09 11:28）；两次现读之间 2026 daily 段 2,039,333 → 2,409,575 行（+18%）。
  ⇒ 只要回填口径不变，224.5 GiB 这张表只涨不缩，D 盘减压不能指望分诊袋而要靠这张表。
- **读侧影响的诚实口径**：同键多版之间目前**只差浮点末位**——2026-08-13 逐列实测最大绝对差
  ma_5 5.7e-14／ma_20 9.1e-13／boll_upper 1.2e-9（量级 130-143），分叉键数
  boll_upper 3,398／ma_20 906／ma_5 23／atr_14 1，rsi_6=macd_hist=kdj_j=0；
  fexam 面板（float32）新旧语义对拍 2026-08-03..27 七列各 ~105,000 格 **changed=0**。
  ⇒ 批复③-a/③-b 今晚**不改任何数字**，它们改的是"哪一版被读到"的**确定性**；
  一旦重算口径真变（后复权族先例），行序就不再是 harmless。
- **建议（业务资产面＝Owner 门位，本班不自裁）**：二选一或并用——
  ①给 dwm 回填加"同键同值不重灌"前置判据（止住增量）；②按季 OPTIMIZE 收敛 daily 段（回收存量）。

