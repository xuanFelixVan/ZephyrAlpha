---
ttl: task_bound
---
# F 盘（SanDisk2TB 冷储专项）空间被吃调查 — 实测报告

- 调查时间：**2026-09-27 09:34（Sunday，系统时钟实测）**，Windows + Git Bash
- 纪律：**全程只读**，未做任何删除/移动/改配置/写盘操作；发现的"该删项"仅登记不执行。
- 标注：`[亲验]` = 本次实测；`[读档]` = 引用台账/文档已有数字，未独立核实。

---

## 0. 卷级与顶层实况（测量已闭合，全项归因见 §3）

### 0.1 卷级读数 [亲验]（口径：1 GiB = 2^30 B；台账标注的 "GB" 经守恒复算证实实为 GiB——见 §0.2 与 §3 闭合算式）

```
Get-Volume -DriveLetter F
  FileSystemLabel : SanDisk2TB      FileSystem: NTFS     HealthStatus: Healthy
  Size            : 2000382062592 B = 2000.4 GB = 1863.00 GiB
  SizeRemaining   :  179965751296 B =  180.0 GB =  167.61 GiB   (9.00% 剩余)
  → Used          : 1820416311296 B = 1820.4 GB = 1695.39 GiB   (91.00% 已用)

df -h /f  : 1.9T total / 1.7T used / 168G avail / 92%      ← 与 Get-Volume 一致
Get-CimInstance Win32_LogicalDisk 'F:' : Size=2000382062592 / FreeSpace=179965751296  ← 双工具互验一致
```

### 0.2 与红线/台账的对账

| 项 | 台账口径 [读档] | 本次实测 [亲验] | 差 |
|---|---|---|---|
| F free | 817.8 / 43.9%（LEDGER 09-24 11:1x） | **167.61 GiB / 9.00%** | −650.2 GiB |
| F free | 766.7（LEDGER 09-25 SOP §一.1 轮） | **167.61 GiB** | −599.1 GiB |
| 红线 `backup_cold_audit_sop.md:9` | F ≥ 700 free | **167.61 → 红线已击穿 532.4 GiB** | 🔴 |

**Owner 判断成立且比预想更严重**：F 盘不是"快满"，是**已越红线 532 GiB、进入 9% 剩余区**。
更关键：**这正是处方 P-6 在 09-25 就写下的预测数字**——见 §0.4 证据 C-2。

### 0.3 F 盘顶层实况 [亲验]（`ls -la /f/`，2026-09-27 09:34）

| 顶层条目 | 类型 | mtime | 备注 |
|---|---|---|---|
| `README.md` | 文件 2177 B | 09-24 12:08 | 盘面速览册 |
| `ch_backup_disk.vhdx` | 文件 **769,138,884,608 B = 716.32 GiB**（Get-VHD FileSize=实占） | **09-26 16:14** | 动态 VHDX，虚拟上限 1024 GiB，仍挂 Running VM |
| `ch_vm_backup/` | 目录 **643,184,071,168 B = 599.01 GiB**（5 文件/6 目录） | 09-26 06:00 | 🔴 **册上说"配置级"，盘上 599 GiB——本次异常项本体** |
| `db_dumps/` | 目录 390,051,712 B = 0.36 GiB | 09-22 04:48 | README 记 0.36G 待清理（已签），逐位吻合 |
| `zephyr_cold/` | 目录 **406,300,400,569 B = 378.42 GiB**（182,937 文件/31,838 目录） | 09-26 00:58 | 本盘唯一"长期住民"，设计内入库写入 |
| `$RECYCLE.BIN/` | 系统目录 129 B（1 文件） | Jul 12 | 系统项，空 |
| `System Volume Information/` | 系统目录（robocopy rc=16 拒读） | Jul 30 | 系统项；由 §2 闭合算式反算 ≤ ~0.5 GiB |

**已核实的台账声明**：`working_vault`、`offrepo_backup`、`code_backup` 在 F 盘根**已不存在** [亲验]，
与 F:\README.md「已清偿记录：working_vault（09-23 删）、offrepo_backup（09-23 删）」一致。
→ a6_remaining_work_order §2-B「2026-09-28 到期：F:\working_vault 旧副本删除（200.7G）」**已提前于 09-23 完成**，
不是本次空间问题的原因。

## 0.4 ★ 定因主证（已锁定）

### 证据 A：`F:\ch_vm_backup\data.vhdx` = 599.00 GiB，是 09-26 一次全量 VM 备份灌进来的 [亲验]

```
Get-VHD -Path 'F:\ch_vm_backup\data.vhdx'
  FileSize      : 643175546880 B = 599.00 GiB   ← 实际落盘占用（robocopy /L 同目录合计 643,184,071,168 B = 599.01 GiB）
  Size(virtual) : 644245094400 B = 600.00 GiB
  VhdType       : Dynamic
  ls mtime      : Sep 26 06:00
F:\ch_vm_backup\boot.vhdx   FileSize = 4194304 B = 4 MiB（仅表头，未整盘复制）
F:\ch_vm_backup\zephyr-ch\  du = 4.2 MB（VM 配置目录）
```

### 证据 B：写入者 = `ZephyrAlpha-WeeklyVMBackup` 计划任务跑 `backup_ch_vm.ps1` [亲验]

`D:\ZephyrAlpha\logs\ch_vm_backup_20260926_060001.json` 全文要点：

```json
"timestamp": "2026-09-26T06:54:36+08:00"
"success": true
"backup_path": "F:\\ch_vm_backup"
"data_vhdx_gb": 599
"duration_seconds": 3258.6          ← ~54 分钟
"steps": { "stop": ok, "vhdx": { data_vhdx_gb: 599, status: ok }, "start": ok,
           "config": { files_copied: 3 } }
```

对照历史 `logs/ch_vm_backup_*.json` 尺寸（SKIP 记录恒为 293 B，真跑记录 >1 KB）[亲验]：

| 运行时间 | 日志大小 | 判定 |
|---|---|---|
| 08-01 / 08-15 / 08-29 / 09-05 / 09-12 / 09-19 | 293 B | `-AutoCheck` SKIP（零占用） |
| 08-08 | 1106 B | 全量真跑 |
| 08-22 | 1214 B | 全量真跑 |
| **09-26 06:00→06:54** | **1089 B** | **全量真跑 → 灌 F 盘 599 GiB** |

代码侧根因 [亲验 `scripts/backup/backup_ch_vm.ps1`]：
```
line  5  : [BLUEPRINT] MOD-INF-043 | Section 3.6
line  6  : "Backs up the zephyr-ch VM (boot.vhdx + data.vhdx + VM config) to F:\ch_vm_backup\."
line 50  : $BackupRoot = "F:\ch_vm_backup"          ← P-6 点名的同一行，未改
line 287 : $rcArgs = @($VmRoot, $BackupRoot, "boot.vhdx", "data.vhdx", ...)   ← 无脑 robocopy 两个 vhdx
```
→ **P-6 从"处方待办"变成"已发生事故"**：09-24 裁定 F 侧 ch_vm_backup 降为配置级，
但脚本 `$BackupRoot` 未改，`ZephyrAlpha-WeeklyVMBackup` 计划任务（现存且 Enabled）在
09-26（周六）06:00 自动触发，把 D:\HyperV\VMs\zephyr-ch\data.vhdx 整盘 599 GiB 复制回 F。

### 证据 C：数字守恒——599 GiB 就是 F 盘跌穿红线的全部缺口 [亲验+读档]

```
09-25 SOP §一.1 轮 F free = 766.7        [读档 LEDGER_final.md:238]
09-27 实测         F free = 167.61 GiB   [亲验 Get-Volume]
差 = 766.7 − 167.61 = 599.09 GiB
data.vhdx 实测 FileSize = 643,175,546,880 B = 599.00 GiB   ← 吻合到 0.09 GiB（<0.02%）
```
等价校验（用"已用"侧）：09-24 11:1x F used=1,045.2 [读档 LEDGER:92] → 本次 1,695.39 GiB，
增量 650.2 GiB = data.vhdx 599.00 + 冷库入库增量 ~51.1 + ch_backup_disk 已含于基线。

→ **红线击穿 532.4 GiB 中，599.00 GiB 由这一份 data.vhdx 造成**；
`ch_backup_disk.vhdx` 与 `zephyr_cold` 在 09-25 后未发生同量级变化（见 §2 mtime）。

### 证据 C-2：P-6 的预测数字被逐字复现 [读档 LEDGER:249/292 + 亲验]

LEDGER 09-25 审计项 ⑥ / 处方 P-6 原文：
> 「若哪个周六 config 漂移触发真跑，脚本会向已被 Owner 降为"配置级"的 F 侧再灌 ~591G
> （**F free 766.7G→约 175G**，直接击穿 SOP §一.1 的 F≥700G 红线并推翻 10-05 摘盘预算）」

实测：09-26（正是周六）06:00 真跑 → **F free 766.7 → 167.61 GiB**（预测 175，误差 4%）。
P-6 由"处方待办"**升级为"已发生事故"**，且事发后端台账未记（LEDGER 最后一条第二链日检为 09-27，
无 09-26 VM 全量备份回灌条目）。

### 证据 C-3：为什么会"真跑"——AutoCheck 是 fail-open [亲验代码]

`scripts/backup/backup_ch_vm.ps1` AutoCheck 判定式（第 196 行附近）：
```powershell
if ($version -and $hash -and $version -eq $lastVersion -and $hash -eq $lastHash) { ... SKIP ... }
else { Write-Warn "AutoCheck: $reason -- proceeding to full backup" }   # ← 探针取空 = 走全量
```
另有三处同向 fail-open：`.env.ch_backup` 缺失→"forcing full backup"；
SSH 探针 `exit_code -ne 0`→"forcing full backup"。
09-26 报告里 `ch_version=""` / `ch_config_hash=""` **两个字段皆空** → 判定为"变更"→ 全量。
即：**SSH 探测一次拿不到版本号，代价就是 599 GiB 落盘 + CH 停机 54 分钟**。
`data/databases/backup_state.json` 现状 [亲验]：
`last_ch_vm_backup_time=2026-09-26T06:54:36+08:00`、`last_ch_vm_backup_path="F:\ch_vm_backup"`、
`last_ch_vm_autocheck_result="full_backup_done"`（此前 08-29/09-05/09-12/09-19 均 skipped_unchanged）。

### 证据 C-4：为什么没被"空间守卫"拦住 [亲验代码+算术]

`backup_ch_vm.ps1:238-246` 的 F 盘守卫是**唯一**保险：
```powershell
$freeGB = $fVol.SizeRemaining/1GB ; $needGB = $dataSizeGB + 20
if ($freeGB -lt $needGB) { Write-Err "..."; exit 1 }
```
09-26 06:00 时：free ≈ 766.7，need = 599 + 20 = 619 → **766.7 > 619，守卫放行**。
守卫只看"装得下装不下"，**不含 SOP §一.1 的 F≥700G 红线**，也不含 10-05 摘盘预算 →
装得下就写满，写完后 free 167.61 已远低于任何红线。这是守卫判据本身的缺陷（登记，不改）。
**复现风险已解除但仍在窗口边**：下一个周六 10-03 06:00 若探针再取空，
届时 free 167.61 < 619 → 守卫会 exit 1 拦停（且拦在停 VM 之前），不会再灌第二次。

### 证据 D：ch_backup_disk.vhdx 仍挂着运行中的 VM [亲验]

```
Get-VM                              → zephyr-ch  State=Running  Uptime=1天02:28:54
Get-VMHardDiskDrive -VMName zephyr-ch:
  SCSI 0,1  D:\HyperV\VMs\zephyr-ch\boot.vhdx     ← VM 系统盘（在 D）
  SCSI 0,2  D:\HyperV\VMs\zephyr-ch\data.vhdx     ← VM 数据盘（在 D）
  SCSI 0,3  F:\ch_backup_disk.vhdx                ← 第一备份链，仍在挂载
  SCSI 0,4  G:\ch_backup_disk2.vhdx               ← 第二备份链（10-05 摘盘后的去处）

Get-VHD 'F:\ch_backup_disk.vhdx': FileSize=769138884608 (716.32 GiB 实占)
                                  Size=1099511627776 (1024 GiB 虚拟上限)
                                  VhdType=Dynamic
```
→ **动态膨胀风险仍在**：已用 716.32/1024.00 GiB，还能再涨 **307.68 GiB**（=330.4 GB），
而 F 只剩 **167.61 GiB** → **不摘盘则 F 必然被写满**（写满还会连带第一链备份盘与冷库同盘同毁的风险面）。
mtime 09-26 16:14；LEDGER 09-24/25 记 716.32 GiB [读档] → 本次实测 **716.32 GiB，09-25 后零增长**。

### 证据 E：F 盘上没有任何"未在册"目录 [亲验]

```
F:\ 根实测条目（ls -la /f/） = README.md + ch_backup_disk.vhdx + ch_vm_backup/ + db_dumps/ + zephyr_cold/
                               + $RECYCLE.BIN（129 B，空）+ System Volume Information（ACL 拒读）
```
逐一存在性核验 [亲验]：`F:\code_backup` = **NO**、`F:\offrepo_backup` = **NO**、`F:\working_vault` = **NO**。
→ 与 LEDGER 09-25 §二.1 审计结论"与 F:/README.md 声明清单逐项全等，零未登记杂物"仍然成立
（**唯一的偏差是 ch_vm_backup 的内容物级，不是目录级**——见证据 A）。

### 证据 F：DailyBackup 六阶段已不写 F [亲验 logs]

`logs/backup_report_20260926_060003.json` stage_timeline [亲验]：
```
Stage 1 Pre-check 0.3s | Stage 2 DB dump 0.4s | Stage 3 Code backup 247.6s
Stage 3b Git bundle 7795.6s | Stage 3c Off-repo mirror 7795.6s | Stage 3d G-fallback 7799s
```
对照 `backup_config.yaml`：`working_vault.base=G:\backup\working_vault`、
`db_dumps.target=G:\backup\db_dumps`、`git_bundle.base=G:\backup\git_bundles`、
`offrepo_backup.base=G:\backup\offrepo`、`g_mirror.base=G:\zephyr_cold`
→ **STAGE 3/3b/3c/3d 全部落 G**；F 侧仅 `g_mirror.source=F:\zephyr_cold`（读，不写）
+ `asset_inventory` cold_archive 源（读）。故 09-26 起 F 的写入者只剩两个：
① `backup_ch_vm.ps1`（灌 data.vhdx）②CH VM 经 SCSI 直挂写 `ch_backup_disk.vhdx`（mtime 09-26 16:14 印证）。

### 证据 G：CH 双链与 10-05 摘盘条件 [亲验+读档]

| 链 | 宿主盘文件 | 实占 [亲验] | 挂载 | 状态 |
|---|---|---|---|---|
| 第一链 | `F:\ch_backup_disk.vhdx` | 716.32 GiB（虚拟上限 1024） | SCSI 0:3，VM Running | 10-05 拟摘除，回收 716.32 GiB |
| 第二链 | `G:\ch_backup_disk2.vhdx` | 585.34 GiB（628,512,260,096 B，mtime 09-26 18:02） | SCSI 0:4，VM Running | 承接链，仍在被写 |

第二链 14 天证据链进度 [读档 LEDGER:704]：**09-27 = 第 3/14 天**（09-25 第 2、09-26 第 2）。
→ 摘盘前置（G 第二链连续 14 天日检 PASS）**尚未满足**，10-05 摘盘本身存在"到期但证据不足"的排期冲突；
且本次事故又吃掉 599 GiB，使 10-05 摘盘后的 F 余量从台账预估的"used 328.9"变成"used 928~995"。

---

## 1. 三态对账表（盘上条目 ↔ 在册真源）

真源集合：`config/asset_inventory.yaml` / `scripts/backup/backup_config.yaml` /
`F:\README.md` / `G:\README.md` / `G:\backup\README.md` /
`infrastructure_registry.yaml::INFRA-STORE-003` / `docs/_working/disk_reorg_campaign/LEDGER_final.md` /
`docs/_working/disk_reorg_campaign/a6_remaining_work_order.md`

| # | F 盘顶层条目 | 实测字节 [亲验] | 态 | 在册指针 | 备注 |
|---|---|---|---|---|---|
| 1 | `zephyr_cold\` | **406,300,400,569 B = 378.42 GiB**（182,937 文件 / 31,838 目录） | 🟢 **在册** | F:README 顶层清单 / INFRA-STORE-003 `host` / asset_inventory:139 / backup_config `g_mirror.source` / library_ledger_backup `MIRROR_ROOT` | 本盘唯一定义的长期住民 |
| 2 | `ch_backup_disk.vhdx` | 769,138,884,608 = **716.32 GiB** | 🟢 **在册** | F:README / INFRA-STORE-003 access_method（"主链，VM 挂载留 F"）/ LEDGER:93,96 | 动态盘，仍挂 Running VM |
| 3 | `ch_vm_backup\data.vhdx` | （见下：`ch_vm_backup` 合计 643,184,071,168 B = **599.01 GiB**） | 🔴 **无主（盘上有、册上无）** | **零登记**：F:README 明写本目录="boot.vhdx + zephyr-ch 配置，data.vhdx 已冻结于 G"；backup_config.yaml **无 ch_vm_backup 的 F 侧 target**；asset_inventory 无 | 09-26 06:00 由 backup_ch_vm.ps1 自动灌回；P-6 预测事故 |
| 4 | `ch_vm_backup\boot.vhdx` | 4,194,304 = 4 MiB | 🟢 在册 | F:README"配置级轻备份" | 册上声明的应有件 |
| 5 | `ch_vm_backup\zephyr-ch\` | 4,400,000 ≈ 4.2 MiB | 🟢 在册 | F:README（VM 配置目录） | 应有件 |
| 6 | `db_dumps\` | **390,051,712 = 0.36 GiB**（9 文件 / 5 目录） | 🟡 在册但已签待删 | F:README"待清理（已签）" / a6 §2-C④ / LEDGER:96 口径 | 与 F:README 记 0.36G 逐位吻合；du 与 robocopy 两法互验同值 |
| 7 | `README.md` | 2,177 B | 🟢 在册（盘面导航册本体） | F:README 自述 | — |
| 8 | `$RECYCLE.BIN\` | 129 B（1 文件 / 2 目录） | ⚪ 系统项（非资产） | 无需登记 | 空，无回收站滞留 |
| 9 | `System Volume Information\` | **无法直测**（robocopy rc=16 拒绝访问；vssadmin 需管理员） | ⚪ 系统项 | 无需登记 | 由 §3 闭合算式反算 ≤ ~0.5 GiB，无 VSS 膨胀 |

**幽灵登记（册上写 F、盘上无）**：

| # | 在册位置 | 册上写的 F 路径 | 盘上实测 | 判定 |
|---|---|---|---|---|
| G1 | `config/asset_inventory.yaml:118`（注释） | `F:\offrepo_backup`（"每日镜像到 F:\offrepo_backup"） | **NO** | 🔴 陈旧注释（真源 `backup_config.yaml offrepo_backup.base` 已于 a3 阶段4.5 切 G） |
| G2 | `scripts/backup/backup_config.yaml:33` | `code_backup.target = "F:\code_backup"` | **NO** | 🟡 半幽灵：字段自注"target 保留供回滚参考"，但字面值仍是已消失目录，易被第三方工具/人误读 |
| G3 | `backup_config.yaml:44` | 注释"F 旧 vault 留观 7 天" | `F:\working_vault` **NO** | 🟢 留观已兑现（09-23 删，见下） |
| G4 | `F:\README.md:15` | "ch_vm_backup 已降为配置级（data.vhdx 冻结于 G）" | 盘上 data.vhdx = 599.00 GiB | 🔴 **描述性幽灵（反向）**：册上说的状态已被 09-26 自动跑推翻，F:README 现为假 |
| G5 | `zephyr_cold\00_manifest\drawers.jsonl` | 3 条抽屉 path 仍写 `G:/zephyr_cold/30_corpus/...` | 实体在 F | 🟡 抽屉台账陈旧（09-20 迁 F 未回改） |

**已核实清偿（不是本次原因）**：
- `F:\working_vault` 旧副本 200.7 GiB（a6 §2-B 排期 09-28 到期）→ **实删于 09-23**（F:README:21 [读档]，
  盘上不存在 [亲验]）。a6 排期比实际晚 5 天，属台账排期未回写，非漏做。
- `F:\offrepo_backup` 136.6 GiB → 09-23 删 [读档 F:README:21]，盘上不存在 [亲验]。
- `F:\zephyr_c4_pdf_cache` 52.7 GiB → 09-24 迁入 `zephyr_cold\50_archive\by_project\zephyralpha_c4_exam_pdf_cache`
  [读档 F:README:21]，目录确在 [亲验]。

---

## 2. 增长定因（mtime / 写入者）

| 项 | 大小 | 目录/文件 mtime | 判读 |
|---|---|---|---|
| `F:\ch_vm_backup\data.vhdx` | 599.00 GiB | **2026-09-26 06:00** | **唯一 09-25 之后的量级变化**。写入者 = `ZephyrAlpha-WeeklyVMBackup`（周六 06:00，`-AutoCheck`）→ `backup_ch_vm.ps1` robocopy `D:\HyperV\VMs\zephyr-ch\data.vhdx` → `F:\ch_vm_backup`。证据 B/C/C-3 |
| `F:\ch_backup_disk.vhdx` | 716.32 GiB | 2026-09-26 16:14 | 与 LEDGER 09-24/25 记 716.32 GiB **逐位等值 → 09-25 后零增长** [读档+亲验]。写入者 = CH 每日增量（SCSI 直挂，非备份脚本）。LEDGER:704 第二链日检 09-27 行"mtime=09-26 16:14 备份完成同步"与之自洽 |
| `F:\zephyr_cold\` | **378.42 GiB**（406,300,400,569 B，182,937 文件/31,838 目录） | 根 09-26 00:58 | 分区 mtime：`50_archive\c1_market` **09-25 00:52–01:06 新建**（kline_etf/lof 1/5/15/30/60min 六个 Parquet 抽屉）、`20_raw` 09-24 23:58（14.44 GiB）、`30_corpus` 09-24 23:46、`library` 每日 03:30（`library_ledger_backup.py` MIRROR_ROOT，09-24~09-27 四日目录，104,467,160 B）、`90_tmp` 09-26 00:35（857,245,576 B，内含 09-25 演练遗件 drill_gov.db 201,347,072 B，LEDGER:368 已签待清）、`40_migration` 0 B、`10_inbox` 0 B。→ 属**设计内冷储入库**，非异常写入 |
| `F:\db_dumps\` | 0.36 GiB | 09-22 04:48 | 冻结遗件，09-22 后无写入（STAGE 已切 G） |

冷库 zephyr_cold 体积差 [读档+亲验]：09-24 README 记 ~327.2 GiB（30_corpus 137.55 + 50_archive 189.59 + 微量），
本次实测 **378.42 GiB** → **+51.2 GiB**，与 LEDGER 09-24→09-25 F used 1,045.2→1,096.3（+51.1）**逐位吻合**，
落点即 09-25 新建的 `50_archive/c1_market` 分钟线族抽屉 + 09-24 `20_raw/etf_lof_minute_history_20260924`。
**判为正常入库**（一次性批量入抽屉，非稳态增长速率），但 10-05 摘盘后 F 只剩冷库时必须按 SOP 复报容量。

**闭合算式（全链 [亲验]，"零未解释空间"的证明）**：
```
used                                     1,820,416,311,296 B
- F:\ch_backup_disk.vhdx                   769,138,884,608   (Get-VHD FileSize)
- F:\ch_vm_backup\                         643,184,071,168   (robocopy /L)
- F:\zephyr_cold\                          406,300,400,569   (robocopy /L)
- F:\db_dumps\                               390,051,712     (robocopy /L 与 du 两法互验同值)
- F:\README.md + $RECYCLE.BIN\                     2,306
= 未归因余额                               1,402,900,933 B = 1.31 GiB
```
NTFS 元数据 [亲验 `fsutil fsinfo ntfsinfo F:`]：Mft 有效数据长度 **766.50 MB** + MFT 保留区 104.50 MB
+ 总保留簇 4.0 MB ≈ **0.81 GiB** → 余 **~0.5 GiB** 归 `System Volume Information`
（robocopy rc=16 拒绝访问，vssadmin 需管理员，无法直测）。
**判：SVI/VSS 无膨胀**——若存在百 GB 级卷影副本，未归因余额会是三位数 GiB 量级。

容量读数四工具互验 [亲验]：`Get-Volume` = `Win32_LogicalDisk` = `df -h` = `fsutil`（空闲簇 43,937,975 × 4 KiB = 167.6 GiB），一致。
测量法注记：`du -sb` 在本 USB 盘上 45 分钟未跑完 30_corpus（MSYS stat 瓶颈），
改用 **只读 `robocopy /L`**（182,937 文件 / 5 秒出总量）；`/L` = 仅列表不改盘，全程零写操作。

---

## 3. 定量归因表（本次结论主体）

F 盘 1863.00 GiB 总量，used 1695.39 GiB（91.00%），free 167.61 GiB（9.00%）。红线 = free ≥ 700（`backup_cold_audit_sop.md:9`），**已破 532.4 GiB**。

| 归因项 | 实测 [亲验] | 占 used | 定性 | 依据 | 台账计划回收 | 回收后 free |
|---|---|---|---|---|---|---|
| **① `F:\ch_vm_backup\data.vhdx`** | **599.00 GiB** | 35.33% | 🔴 **真异常**（无主+违反 09-24 裁定+P-6 事故落地） | 三处真源均无登记；F:README 反着写；09-26 06:00 由计划任务自动灌入 | **无排期**（台账未记此次回灌）→ 需按 09-24 裁定恢复原状；**本调查只登记不执行** | 167.61 → **766.61**（自洽复算：正好回到 09-25 台账值 766.7） |
| **② `F:\ch_backup_disk.vhdx`** | 716.32 GiB | 42.25% | 🟢 **正常过渡态**（双链并跑，第一链待退役） | INFRA-STORE-003 + F:README + LEDGER:93/96 在册；09-25 后零增长 | **2026-10-05 摘盘**（前置：G 第二链连续 14 天日检证据）→ 实测前置仅 **3/14 天**，10-05 条件未熟 | ②摘除后再 +716.32 → **1482.93** |
| **③ `F:\zephyr_cold\`** | **378.42 GiB**（182,937 文件/31,838 目录） | 22.32% | 🟢 **正常设计住民** | 本盘唯一定义住民；+51.2 GiB 来自 09-25 新建 `50_archive/c1_market` 分钟线抽屉入库，与 LEDGER 09-24→09-25 F used 增量 +51.1 逐位吻合 | 不回收（长期增长项，10-05 后按 SOP 容量警戒复报） | — |
| ④ `F:\db_dumps\` | 0.36 GiB | 0.02% | 🟡 在册已签待删 | F:README + a6 §2-C④ | a6 排期 **10-05** | +0.36 → 1483.29 |
| ⑤ `ch_vm_backup\boot.vhdx`+`zephyr-ch\` | 8.6 MB | ~0% | 🟢 在册应有件 | F:README"配置级轻备份" | 不回收 | — |
| ⑥ `$RECYCLE.BIN` | 129 B | ~0% | ⚪ 系统项，空 | 实测 | — | — |
| ⑦ NTFS 元数据 + `System Volume Information` | 1.31 GiB（其中元数据 0.81 [亲验 fsutil]，SVI ≈0.5 反算） | 0.08% | ⚪ 可忽略，无 VSS 膨胀 | 闭合算式余额；Mft 仅 766.5 MB | — | — |
| **合计** | 716.32 + 599.01 + 378.42 + 0.36 + 1.31 = **1,695.42 GiB**（vs used 1,695.39，差 0.03 GiB 取整误差） | 100% | **零未解释空间** | — | — | — |

**守恒自校验（这是本表可信度的关键）**：
`167.61 (当前 free) + 599.00 (①) = 766.61` ≈ `766.7 (LEDGER 09-25 实测 free) [读档]` →
**①单独解释了 09-25 之后 F 盘的全部空间损失，误差不超过 0.1 GiB。**

---

## 4. 结论：(c) 两者叠加，但红线击穿 100% 由"真异常"那一项造成

1. **Owner 判断方向正确，量级更严重**：F 不是"快满"，是 **91.00% 已用 / free 167.61 GiB，已击穿 F≥700 红线 532.4 GiB**。
2. **不是"2T 备份本该这么满"——设计态被实测复算出来了**：
   设计内合理占用 = ②716.32（待 10-05 退役）+ ③378.42（冷库本体）+ ④0.36 + ⑦1.31 = **1096.41 GiB**
   → 对应 free 应为 **766.59 GiB**。这与 LEDGER 09-25 实测 free **766.7** [读档] 相差 0.11 GiB。
   即 **"F 盘 free ≈766 GiB / 已用 ≈1.1 TiB"就是 F 的设计态**，Owner 估的"合理备份应该只有 2T 左右"
   对应的其实是**整盘 1863 GiB 中设计占用 1096 GiB**——设计占用只占盘的五成九，不是"快满"。
   现在多出的 599.01 GiB 是**唯一一个异常项**，且它单独把 free 从 766.59 打到 167.61。
3. **定性 = 叠加，但可完全分离**：
   - 真异常（可回收，回收即回到设计态）：**① 599.01 GiB = 35.33%**，单一文件、无主、由自动化在无人授权窗灌入。
   - 正常过渡态（有排期，但排期前置未熟）：**② 716.32 GiB = 42.25%**。
   - 正常设计住民：**③ 378.42 GiB = 22.32%**。
   → **不存在"无主目录"（顶层 5 条资产全部在册），不存在"重复镜像簇"**——
   G 侧历史三份 591.57 GiB 等值 ch_vm_backup（a6 §2-C③ 待办）经本次实测**已收敛为一份**：
   `G:\backup\ch_vm_backup` 在位（du=592G）[亲验]，
   `G:\zephyr_backup_mirror`、`G:\zephyr_cold\ch_vm_backup` 均已不存在（ls 报 No such file）[亲验]。
   F 侧这份是**时间维上"旧状态被自动化复活"**，不是空间维的复制堆积。
   唯一异常仍是"脚本写错家"——即 P-6 指出的 `backup_ch_vm.ps1 $BackupRoot="F:\ch_vm_backup"`，
   且 P-6 的预测数字（766.7→约 175）被 09-26 逐字复现（→167.61，误差 4%）。
4. **触发红线清单（本次实测判定）**：
   | 红线 | 判据 | 实测 | 判定 |
   |---|---|---|---|
   | SOP §一.1 容量红线 | F free ≥ 700 | 167.61 | 🔴 **破线 532.4** |
   | F 盘"纯冷储/immutable 只进不改" | 禁可变工作目录 | 599 GiB 单文件被周级重写 | 🔴 破设计 |
   | 10-05 摘盘预算 | 摘后 F used ≈ 328.9（台账预估）[读档 LEDGER:96] | 实况：只摘②→ used 979.07 / free 883.93；先回滚①再摘②→ used **380.06** / free **1482.94**（台账预估被冷库 +51.2 入库自然刷新，仍属可控） | 🟡 预算需刷新；**真正的问题是摘盘前置未熟**（见下） |
   | 10-05 摘盘前置 | G 第二链连续 14 天日检证据 | 实测最后一条 = **09-27 第 3/14 天** [读档 LEDGER:704] | 🔴 **到期时（10-05）最多累计 11/14，前置必然不熟 → 摘盘将跳票或被迫降标准执行** |
   | LEDGER 处方 P-6 | 归属 Owner（数据面+排程面双门位） | 09-26 已发生，事后无台账补记 | 🔴 未闭环 |
   | 数据第一公理（两份验证副本） | VM 全量镜像 | F 09-26 份(599.00) + G 08-22 冻结份(591.57)，**两者差 7.44 GiB 非等值** | 🟡 见 §5-C |
   | D 盘（顺带） | free ≥ 50 | `df` D 剩 19G / 98% | 🔴 LEDGER 09-25 已标红，未解 |

---

## 5. 登记事项（**只登记，未执行任何删除/移动/改配置**）

- **A（事故本体）**：`F:\ch_vm_backup\data.vhdx` 599.00 GiB 与 2026-09-24 Owner 裁定（F 侧降配置级）冲突，
  由 `ZephyrAlpha-WeeklyVMBackup`（周六 06:00，`-AutoCheck`）在 09-26 06:00→06:54 自动全量灌入。
  事后 LEDGER **无对应事故条目**（最后一条第二链日检为 09-27，未记本次回灌）。待 Owner 定向处置。
- **B（根因与缺陷共五处，全部未改）**
  ① `backup_ch_vm.ps1:50` `$BackupRoot="F:\ch_vm_backup"`（家指错）；
  ② 同脚本 AutoCheck **fail-open**：版本/哈希取空即"proceeding to full backup"，
    一次 SSH 探测失败的代价被定成 599 GiB 落盘 + CH 停机 54 分钟；
  ③ 同脚本 `:238-246` F 盘空间守卫判据是"装得下就写"（free ≥ size+20GB），
    **不含 F≥700G 红线、不含 10-05 摘盘预算** → 09-26 以 766.7 > 619 放行。
  ④ 同脚本**无互斥锁** [亲验 grep]：`backup_ch_vm.ps1` 全文对 `backup.lock` / `Test-BackupLock` /
    `.runtime` **0 命中** → 与 `ZephyrAlpha-DailyBackup` 在 09-26 同刻并发
    （实测产物 `ch_vm_backup_20260926_060001.json` @06:00:01 与
    `backup_report_20260926_060003.json` @06:00:03，相差 2 秒，后者跑了 7997.2s）。
    且前者在此期间 **Stop-VM 停 CH 达 54 分钟**，正是 LEDGER 审计项 ② 预警的撞车窗，09-26 首次真实兑现。
  ⑤ 复发窗口：下一个周六 **2026-10-03 06:00**。届时 free 167.61 < 619 → 守卫会 `exit 1` 拦停，
    **不会再灌第二份**；但只要 A/B①②不修，F 盘一旦因别的原因腾出 619 GiB，同事故可复现。
- **C（处置前必须先看的一面，属数据面门位，不属本调查权限）**：
  现存的 VM 全量镜像只有两份且**互不等值**：F 份 09-26（643,175,546,880 B）
  与 G:/backup/ch_vm_backup 冻结份 08-22（635,189,592,064 B，实测目录 du=592G），差 7.44 GiB。
  若直接按 09-24 裁定删 F 份，全量镜像将退回 08-22 基座，而 `restore.ps1 vm` 正是用它回灌
  → **可能恢复出旧库**（P-6 后半段风险，至今无工具能刷新 G 冻结档）。
  可选路径（均需 Owner 批，本调查未选任何一条）：
  (a) 先把 F 09-26 份刷进 `G:/backup/ch_vm_backup`（**G free 实测 1,537,808,191,488 B = 1431.35 GiB** [亲验]，
      新旧并置需 591.57+599.01=1190.58 GiB，容得下；刷完 verify 再按 `G:/backup/README.md:21`
      "冻结档不轮转，CH 升级重做全量后旧档人工清" 处理旧档）→ 再删 F 份；
  (b) 认定 CH 数据真身由双链 `BACKUP TO Disk` 增量覆盖，全量镜像留 08-22 即可，直删 F 份；
  (c) 整机制退役 `backup_ch_vm.ps1`（a0 §6-W4 的 C 案）。
- **D（在册但已假）**：`F:\README.md:15` 对 ch_vm_backup 的描述（"已降为配置级，boot.vhdx + zephyr-ch 配置；
  data.vhdx 全量镜像冻结于 G:\backup\ch_vm_backup"）与盘面实况（data.vhdx 599.01 GiB 在位）**相反**。
  而 F:README 正是 SOP §二.1 顶层对账的"期望集"（LEDGER:226 本轮以三张盘面 README 为期望集执行）。
  好消息：该审计法确实下探到件数+体积（09-25 记 "ch_vm_backup/(4 件 8.5MB=配置级✓)"），
  所以**照法复跑会立刻抓到**；风险在于"信册不信盘"的读法会把 599 GiB 合理化成"设计内"。
  建议与 A 同批回写（本调查未改）。
- **H（监控缺口，本次事故未被任何自动化看见）**：
  `LEDGER_final.md` 最后写入 **09-27 07:18** [亲验 ls]，最新两条是【第二链日检 09-26】/【09-27】，
  但**§一.1 四盘容量红线自 09-25 的 "F 766.7G ✓(≥700)" [读档 LEDGER:238] 之后无新读数**——
  即 F 于 09-26 06:54 破线（→167.61），09-26、09-27 两个晨间轮次均未复测容量，事故在台账里**零记录**。
  09-27 那条日检甚至已经读到 `ch_backup_disk.vhdx 的 mtime=09-26 16:14`，说明写者当时就在看这块盘，
  却没看卷 free。**判：F≥700 红线目前是"人肉轮次项"，不是自动化探针** → 检测延迟实测 ≥2 天且仍未触发。
  （仅登记；本调查未新增/修改任何探针或脚本。）
- **E（陈旧登记）**：`config/asset_inventory.yaml:118` 注释仍写"每日镜像到 `F:\offrepo_backup`"（该目录 09-23 已删、真源已切 G）；
  `backup_config.yaml:33` `code_backup.target="F:\code_backup"` 指向不存在目录（字段自注"仅供回滚参考"，
  但 09-26 夜班已按 P-13 把仪表盘探针改为跟随单一真源，故不再恒红，残留仅此注释/字段）；
  `zephyr_cold/00_manifest/drawers.jsonl` 有 3 条抽屉 path 仍写 `G:/zephyr_cold/...`。
- **F（排期与实况不符）**：a6 §2-B 排 09-28 删 `F:\working_vault`（200.7G）→ **实况 09-23 已删**，
  本项无需再动；a6 §2-C① 的 10-05 摘盘预期回收 "526G" 应更新为 **716.32 GiB**（LEDGER:93 已自纠）。
- **G（顺带发现，非 F 盘范围）**：D 盘 98% 满（free 19G，LEDGER 09-25 已标 🔴 破 50G 线），
  活 VM 的 `boot.vhdx`/`data.vhdx` 都在 D:\HyperV\VMs\zephyr-ch；a6 §2-E 的 vhdx 压缩（预期回收 200G+）
  仍等 Owner 点名窗。F 与 D 同处告急，而 09-26 那次全量备份恰好是"D 读 599G → F 写 599G"，
  说明压缩窗与 F 处置窗宜同批规划（仅登记，未动）。

---

## 6. 复算用的原始命令与读数（供独立复核）

```bash
# 容量（四工具互验一致）
powershell -NoProfile -Command "Get-Volume -DriveLetter F | Format-List ... "
  Size=2000382062592 SizeRemaining=179965751296
df -h            # F: 1.9T 1.7T 168G 92%
powershell Get-CimInstance Win32_LogicalDisk 'F:'   # Size/FreeSpace 同上
MSYS_NO_PATHCONV=1 fsutil fsinfo ntfsinfo F:        # 空闲簇 43,937,975×4KiB=167.6GB; Mft 766.50MB

ls -la /f/       # 顶层 5 资产条目 + 2 系统条目
powershell Get-VHD -Path 'F:\ch_backup_disk.vhdx'    # FileSize=769138884608 Size=1099511627776 Dynamic
powershell Get-VHD -Path 'F:\ch_vm_backup\data.vhdx' # FileSize=643175546880 Size=644245094400 Dynamic
powershell Get-VHD -Path 'F:\ch_vm_backup\boot.vhdx' # FileSize=4194304
powershell Get-VM                                    # zephyr-ch Running, Uptime 1.02:28:54
powershell Get-VMHardDiskDrive -VMName zephyr-ch     # 0:1 D:boot 0:2 D:data 0:3 F:ch_backup_disk 0:4 G:ch_backup_disk2
du -sb /f/db_dumps/*                                 # 390,051,712 B 合计
du -sb '/f/$RECYCLE.BIN'                             # 129 B

# 逐目录字节+件数（只读列举；本 USB 盘上 du 45min 未出，robocopy /L 5s 出全量）
# /L = 仅列举不改动，配 /E /BYTES /XJ /NFL /NDL /NJH /NP；源=目标以杜绝任何误写目标
robocopy "F:\zephyr_cold"  "F:\zephyr_cold"  /L /E /BYTES /XJ /NFL /NDL /NJH /NP
  -> 目录 31,838 / 文件 182,937 / 字节 406,300,400,569
robocopy "F:\ch_vm_backup" "F:\ch_vm_backup" /L /E /BYTES /XJ ...  -> 6/5/643,184,071,168
robocopy "F:\db_dumps"     "F:\db_dumps"     /L /E /BYTES /XJ ...  -> 5/9/390,051,712
robocopy "F:\$RECYCLE.BIN" "F:\$RECYCLE.BIN" /L /E /BYTES /XJ ...  -> 2/1/129
robocopy "F:\System Volume Information" ... -> rc=16 拒绝访问（无管理员令牌）
powershell Get-Volume -DriveLetter G        # Size 4,000,769,372,160 / SizeRemaining 1,537,808,191,488
du -sh /g/backup/ch_vm_backup               # 592G（G 侧冻结全量镜像，在册）

powershell Get-ScheduledTask | ...                   # ZephyrAlpha-DailyBackup / -WeeklyVMBackup / _LibraryLedgerBackup
cat logs/ch_vm_backup_20260926_060001.json           # 全量真跑，599GB，3258.6s，backup_path=F:\ch_vm_backup
ls -la logs/ch_vm_backup_*.json                      # 293B=SKIP 记录 vs >1KB=真跑记录（尺寸即状态）
grep -o '"last_ch_vm[^"]*"[^,]*' data/databases/backup_state.json
python ... logs/backup_report_20260926_060003.json   # stage_timeline 全落 G
grep -n 'BackupRoot' scripts/backup/backup_ch_vm.ps1 # :50 = "F:\ch_vm_backup"
sed -n '196,206p;238,246p' scripts/backup/backup_ch_vm.ps1   # fail-open 判定式 + 空间守卫
ls -la docs/_working/disk_reorg_campaign/LEDGER_final.md     # mtime 09-27 07:18（末条=第二链日检 09-27）
```

## 7. 测量窗口稳定性复测 [亲验]

同一调查窗口内二次读数（09:34 → 09:40，间隔 6 分钟）：

| 项 | 首次 [亲验] | 复测 [亲验] | 判定 |
|---|---|---|---|
| F SizeRemaining | 179,965,751,296 B（167.61 GiB） | 179,965,751,296 B | **逐位相同，窗口内零漂移** |
| F Size | 2,000,382,062,592 B | 2,000,382,062,592 B | 同 |
| `ch_backup_disk.vhdx` FileSize | 769,138,884,608 B（716.32 GiB） | 769,138,884,608 B | 同（CH 增量非连续写，当日 16:14 那轮已结束） |

→ 归因表无"测量期间被并发写入污染"的风险；VM `zephyr-ch` 全程 Running（Uptime 1天02:28→02:34 连续），
本调查未停 VM、未摘盘、未触发任何备份任务。

---

> 本报告全程只读：所有列举命令均为 `Get-*` / `du` / `ls` / `robocopy /L` / `fsutil fsinfo`，
> 未执行任何 copy / move / delete / /MIR / git / 配置写入。发现的 599.01 GiB 异常件、
> 五处脚本缺陷（§5-B ①~④）、五处在册与实况冲突（§1 G1~G5 + §5-D），**一律只登记，未执行**。

