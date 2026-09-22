---
ttl: task_bound
---

# 磁盘重整总方案 v1 — D 盘腾挪 + 四盘分工（2026-09-19）

> 勘察工具：WizTree v4.31 CLI export（MFT 直读，D/E 全量 300 万行 CSV，存 `.runtime/tmp/wiztree_{d,e}.csv`，解析器 `parse_wiztree.py` 可重跑）。
> 勘察范围：五盘容量、D/E 逐目录体积、注册表卸载项、计划任务、Windows 服务、HyperV VM 状态、仓内路径引用全文检索。
> 关联 SOP：`docs/_working/altdata_line/10_g_drive_cold_storage_sop.md`（G 盘冷库 SOP，本方案 §4 挂接它，不另造规范）。

## 0. 一句话结论

**D 盘 83% 被 ClickHouse 虚拟机磁盘占用（`D:\HyperV\VMs\zephyr-ch\data.vhdx` = 599GB），不是软件。**
D 盘全部软件加起来 ≈16GB。"把 D 盘软件全迁 E 盘"收益 16GB、代价是十几套软件的注册表手术——**不建议做**。
真正有效的三件事：① 停机窗压缩 data.vhdx（预期回收数百 GB）② 清理仓内 `.runtime` 债务 45GB ③ E 盘冷储/研报原料 ≈226GB 迁 G（其中研报 85GB 昨晚已复制完，只欠对账+删除）。

## 1. 盘面底数（2026-09-19 实测）

| 盘 | 盘体 | 容量/剩余 | 角色（现状） | 大头 |
|---|---|---|---|---|
| C | NVMe 分区 | 199G / 62G | 系统 | — |
| D | NVMe 分区 | 731G / **20.9G** | 项目+CH 虚拟机 | HyperV 608.4（data.vhdx 599）、ZephyrAlpha 74.73（.runtime 45.27、models 14.29）、APP 13.88、其余 ≈2.4 |
| E | SATA WD 1T | 931G / 134G | 软件+热数据 | 三角洲行动(游戏)197.1、数据下载 137.9、zephyr_cold_archive 117.6、国金证券QMT 84.1、OllamaModels 40.3、QMT模拟 39.0、ai短剧 28.7、微信记录 26.9、手游助手 21.7、pagefile 32G |
| F | SanDisk 2T USB | 1863G / 557G | **备份盘**（已在役） | ch_backup_disk.vhdx 526G（09-19 新鲜）、working_vault/db_dumps/offrepo_backup/ch_vm_backup |
| G | 东芝 4T USB | 3726G / 3588G | **冷储盘**（昨晚已立项） | zephyr_cold 抽屉库（研报 90,243 件已入：F 盘 60,245 + E 盘 29,998，抽样 bad=0） |

## 2. D 盘逐项处置清单

| 目录 | 体积 | 判定 | 说明 |
|---|---|---|---|
| `D:\HyperV` | 608.4G | **批1 压缩** | zephyr-ch VM 运行中（23h）。压缩必须停机窗做（§3 批1）。**禁迁 G/F**（USB 盘跑热库=红线）。若压后 ≤350GB 可评估整 VM 迁 E（内部 SATA），届时 D 全让给项目 |
| `D:\ZephyrAlpha` | 74.7G | 留（项目本体） | 其中 `.runtime` 45.3G=会话暂存债务（批1 清）；`models` 14.3G（qwen25-7b-base 等）查引用后可挪 G/E；`.worktrees` 4G+`.aidrafts` 3.7G 随收尾循环自然消化 |
| `D:\APP` | 13.9G | **不迁** | 微信/WPS/百度网盘/QQ音乐/美图/剪映/WinRAR/向日葵/腾讯会议/千牛等。挂载点：WPS 更新计划任务×2、千牛 AliUpdater 任务、向日葵 SunloginService（stopped）。理由：总收益 16G vs 注册表手术风险；要迁走"卸载→重装到 E:\Apps"正解（§3 批3） |
| `D:\AI\Trae CN` | 1.6G | 不迁（IDE 活跃） | 注册表有 InstallLocation |
| `D:\国金QMT交易端` | 0.3G | 不迁（QMT 主端） | 交易端，动它风险>收益 |
| `D:\tmp_db_dumps` | 0.2G | 批1 轮转 | DB 备份中转（`backup_config.yaml dump_dir`），F:\db_dumps 已收 |
| `D:\ZephyrAlpha-stash-archive` | 0.13G | 批1 归档 | F:\offrepo_backup\stash_archive 已镜像，可移 G:\zephyr_cold\50_archive |
| tesseract OCR / Node.js / RSSHub / 清风 / 龙虾 / 临时工作区 / tmp / nonexistent | ≈1.6G | 确认后清/留 | 单件都小；`nonexistent`（名字即异常）确认后删 |
| TP-LINK 无线网卡驱动（`D:\APP\TP-LINK...`） | — | **绝不可动** | AicWifiService RUNNING，WiFi 硬件驱动，移动即断网 |

## 3. 执行批次

### 批1 · D 盘立即回收（不动任何软件，零注册表风险）
1. `.runtime` 45G 清理：先跑 `classify_workspace_wip.py`（铁律，禁肉眼判罚）→ 按 TTL 清会话暂存/staging/commit_queue 陈货；
2. `models` 14.3G：`rg "qwen25-7b|models/"` 查消费方 → 无引用则挪 G 50_archive；
3. tmp_db_dumps 轮转 + stash-archive 归档 G + 垃圾小目录确认清；
4. **data.vhdx 压缩（Owner 拍板停机窗）**：VM 内先 `df` 看虚拟盘内部空闲（已归档分区是否已 DROP 回收）→ 停 VM → 管理员 `Optimize-VHD -Path D:\HyperV\VMs\zephyr-ch\data.vhdx -Mode Full` → 起 VM。压缩前置：F:\ch_backup_disk.vhdx 已是 09-19 新鲜备份，压前再手动刷一次 backup.ps1；
5. 预期：D 剩余 20.9G → 批1a（清垃圾）≈66G；批1b（压缩）视 VM 内空闲再 +数十~数百 G。

### 批2 · E→G 冷储迁移（挂接 G 盘 SOP §6，一次一批、前后对账、5% hash 抽检、E 侧留 30 天）
| 源 | 体积 | 动作 |
|---|---|---|
| `E:\数据下载\研报` | 84.7G | **已复制完**（G 2019_bundle 29,998=29,998）。剩：对账（字节数+抽检）→ 等 30 天窗（2026-10-18）→ 删 E 侧 |
| `E:\zephyr_cold_archive` | 117.6G | 复制 → `G:\zephyr_cold\50_archive\by_project\zephyralpha\zephyr_cold_archive\`（内部结构原名保留）； drawers.jsonl 登记（skeleton_ref 关联 data_retention_contract INV-RET）；同 commit 更新下方引用清单；E 侧改 `.migrating` 留观 30 天后删 |
| `E:\数据下载\产业链数据` | 12.4G | 复制 → 20_raw（A-J 抽屉由数据线按骨架大类认定） |
| `E:\数据下载\新闻文本数据2000-2024` | 11.5G | 复制 → 20_raw\C_text |
| `E:\数据下载\` 分钟/分笔归档族 ≈22G（ETF分钟/指数分笔/1分钟/5分钟/tick缺口等） | 22G | **暂留 E**（潜在恢复源+活跃管线；量小不急，未来批再议） |
| `E:\数据下载\P1归一 / P2语料` | 3.2G | **留 E**（industry_graph RAG 活跃语料，代码直读） |

**zephyr_cold_archive 迁移必改引用清单（同 commit 原子落地）：**
1. `scripts/ch/archiver.py:69` `ARCHIVE_ROOT` + `:732` `disk_usage("E:\\")`；
2. `config/asset_inventory.yaml:139` offrepo_assets cold_archive path；
3. `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml:200-203` INFRA-STORE-002 host/access_method；
4. `docs/registry_of_logs.yaml:808`；
5. `src/zephyr/frontend/dashboard/services_registry.py:118-120`（detect dir + 名称"E 盘冷存储"→"G 盘冷存储"）；
6. `scripts/backup/backup_config.yaml:88-89` offrepo mirror source（E→G，F 镜像继续兜底）；
7. 核对 `data_retention_contract.yaml` 是否含路径表述。
历史档（`docs/_archive/18_cold_archive_build_plan.md` 等）按裁定 #360a 归档面免断链豁免，不改。

**迁移配方**：`robocopy <src> <dst> /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /MT:16` → 源/目文件数+字节双对账 → 5% 抽样 hash → 改引用 → E 侧留观 → 删。迁移前后各记一次体积与文件数（SOP §6 纪律）。

预期：E 剩余 134G → 批2 完 ≈360G。

### 批3 · 软件迁移（**默认不做**，Owner 坚持才执行）
正解=逐个卸载→重装到 `E:\Apps\<名>`（安装器自己写注册表），禁直接剪切已装软件。每件挂载点：卸载项（HKLM/HKCU Uninstall）、服务（AicWifiService 留 D）、计划任务（WPS×2/千牛）、PATH、快捷方式、文件关联。微信重装后存储路径重定向到既有 `E:\微信聊天记录存储` 即可。

## 4. 四盘分工规范 v1（挂接 G 盘 SOP，此处只记增量）

| 盘 | 角色 | 禁则 |
|---|---|---|
| C | 系统 | — |
| D | 项目盘：ZephyrAlpha + CH 虚拟机 + 必要驱动/常驻软件 | 禁新增与项目无关的顶层目录；临时输出只走 `.runtime/tmp` |
| E | 软件盘+热数据：所有应用装 `E:\Apps`；行情热数据（QMT/xtquant/iFinD/wind）；活跃管线工作目录 | 禁放"唯一副本"的冷数据 |
| F | 备份盘：working_vault 版本化快照 / db_dumps / offrepo 镜像 / VM 备份 | 只写不改，禁当工作盘 |
| G | 冷储盘：`G:\zephyr_cold` 抽屉库唯一入口（00_manifest 先登记后建目录 / 10_inbox / 20_raw / 30_corpus / 40_migration / 50_archive / 90_tmp） | USB 属性：禁热服务/热库/游戏/编译；immutable、禁双真源、回测数据家不在冷库（SOP §4 三红线） |

登记义务：入 G 走 `drawers.jsonl` 四步入库（SOP §2）；仓外资产入 `config/asset_inventory.yaml` offrepo_assets；备份链新增一条"G 冷储 → F offrepo 镜像"。

## 5. WizTree 评估与开源替代

- **WizTree v4.31（已装）留用**：MFT 直读，本方案 D/E 底数即其 CLI export 产出（秒级 1.8M 行）。命令：`WizTree64.exe D: /export=<csv> /exportfolders=1 /exportfiles=0`。个人免费（商用收费，闭源）。
- 开源替代：[Squirreldisk](https://github.com/adileo/squirreldisk)（跨平台，颜值流）、[WinDirStat](https://github.com/windirstat/windirstat)（祖师爷但慢）、ncdu（CLI）。搭配 [Everything](https://www.voidtools.com/)（文件名秒搜，闭源免费）找散落大文件。

## 6. 待 Owner 拍板

1. ~~批1b 压缩停机窗时间~~ **已被 Owner 裁定修订（09-19 晚）**：不做压缩，改为 VM 内清库分析（见 §7 v2）；
2. `models/` 14.3G 处置（查引用后挪 G/E/留）；
3. 批3 软件迁移是否坚持（默认不做）；
4. E 盘自有大头（三角洲行动 197G/ai短剧 28.7G/手游助手 21.7G）是否处置——本方案未动它们。

---

# v2 增补（2026-09-19 晚：磁盘实测 + CH 库内勘察后修订）

> Owner 三项新指令：① 不压缩，改为分析 CH 库内到底多少数据、哪些可进冷储（热数据存量政策）；② F/G 角色评估调换（实测速度）；③ 讨论数据库迁 E vs 留 D。本章为调查结论与修订方案。

## 7.1 四盘实测速度（2026-09-19，1GB 顺序 + 4K 随机 QD1）

| 盘 | 盘体 | 顺序读 | 顺序写(fsync) | 4K 随机 | 定性 |
|---|---|---|---|---|---|
| D | NVMe 分区（经 vhdx 文件读） | **1482 MB/s** | — | 4776 IOPS | 最快，回测主力盘 |
| E | SATA（WD Green，实测为 SSD 级） | 475 MB/s | 437 MB/s | 4316 IOPS | 快，软件+热数据 |
| F | SanDisk 2T USB | 374 MB/s | 340 MB/s | 3082 IOPS | **USB SSD**，接近内置 SATA |
| G | 东芝 4T USB | （批量小文件 57 MB/s） | **70 MB/s** | （11.5 files/s） | 机械盘，容量大但慢 5 倍 |

**结论：Owner 的 F↔G 调换直觉正确。** F（SSD）配冷储（回测重演/研报语料要读，快盘值得），G（机械）配备份（顺序大文件写为主，70MB/s 够用）。

## 7.2 CH 库内底数（system.parts 实测，26.6.1）

- **VM 内部磁盘濒满**：`/var/lib/clickhouse` 631.9G 总量，**仅剩 6.6G**——这是比"D 盘 20.9G"更紧急的一颗雷。
- **活跃数据总量 566.5G**，拆开是三笔账：
  | 类别 | 体积 | 定性 |
  |---|---|---|
  | ClickHouse 系统日志（text_log 97.9 + query_log 18.4 + processors_profile 16.0 + trace 7.8 + 其余） | **≈145G** | 纯垃圾，可 TRUNCATE+调日志级别，非业务数据不受契约铁律约束 |
  | 修复尸体表（news_corrupt 13.0 + news_pre_tz2 12.9 + kline_etf_*_tz_bak 8.1 + 其余 _bak） | **≈35.4G** | 历次时区/修复操作的残留副本，核对活表后处置 |
  | 契约欠账（TI 窗口外 19.4 + news/kline 冷线 5.5） | **≈24.9G** | 走 archiver.py 三阶段归档到冷储新家 |
  | **合规业务热层（真实回测工作集）** | **≈361G** | tick 141.5（2025-01 起 21 个月）+ 技术指标窗口内 151 + 分钟线 66 + 日K及基本面/事件/元数据全部 |

- **归档纪律执行得很好**：契约冷线欠账全库仅 24.9G（TI 1min 从 202605 起、5min 从 202508 起、60/120min 从 202109 起，滑动窗口全部贴线）。热层数字可信。

## 7.3 热数据存量政策（契约已定，此处量化收口）

`data_retention_contract.yaml`（Owner 铁律）已回答"存多少/存哪些/存多久"：
- **存哪些（全留 Hot）**：L3 日K全史（<1G）、L5 基本面、L7 图谱、L9 宏观、L10 元数据 + 一切 <1GiB 研究型表（INV-RET-005）；
- **存多久（滑动窗口）**：L1 Tick ≥2 年（当前 2025-01 起，2027 年起 2025 段过线可归档）；L2 分钟/L4 资金面/L8 衍生 ≥5 年；L6 新闻 ≥10 年；TI 派生表按周期 3月/1年/3年/5年贴线；
- **量化稳态**：tick ≈6.7G/月是唯一大头，≥2 年线开始裁剪后（2027 起）**热层稳态 ≈350-400G，不再无限增长**——"数据一直涨所以压缩无意义"的担忧，在契约纪律下不成立：涨的是冷储层，热层有界。

## 7.4 修订后的执行批次

**批 A（VM 内清库，最高优先——比 D 盘告急更急）**：预计内部释放 ≈205G，6.6G 剩余 → ≈210G，等于给未来 2.5 年增长空间，**全程不需要压缩 vhdx**（尊重 Owner 裁定）：
1. 系统日志：`TRUNCATE system.text_log/query_log/...` + config 调 text_log 级别（trace→information/warning）+ 设轮转上限（97.9G/年病态，疑似 trace 级在跑）；
2. 尸体表：先核对应活表行数，导 Parquet 入冷储后 DROP（或 Owner 裁定修复工件豁免直删）；
3. 欠账 24.9G：archiver.py archive-range 批处理（注意 ARCHIVE_ROOT 届时应已指向冷储新家）。

**批 B（F↔G 调换，替代 v1 批2 的落点）**：
- **F（USB SSD）= 冷储主库 + 代码版本库**：G:\zephyr_cold 抽屉库整体迁 F（研报 9 万件再搬一次约 1-2h）；zephyr_cold_archive 117.6G 迁 F；working_vault（小文件高频写，11.5 files/s 的机械盘扛不住，SSD 合适）留/迁 F；
- **G（机械 4T）= 备份兜底盘**：ch_backup_disk.vhdx 526G、db_dumps、offrepo 大镜像迁入；并新增一条"**F 冷储 → G 镜像**"备份关系（重要冷数据两盘各一份，3-2-1 原则落地）；
- 引用清单 v1 §3 的 7+1 处不变，落点从 G 改 F；`data_retention_contract.yaml` §5"E盘Parquet"字样改为"F盘Parquet"。

**批 C（数据库去留 = Owner 问题二的答案）**：
- **留 D，不迁 E。** D 实测 1482 MB/s vs E 475 MB/s，回测顺序扫描快 3 倍；
- 容量账：批 A 后 VM 内部 ~210G 余量 ≈ 2.5 年增长；vhdx 文件维持 599G 不动，D 盘靠 v1 批1（.runtime 45G 清理）缓解到 ~66G 剩余；
- E 不需要为数据库腾地方（即便删游戏腾到 ~586G 也装不下 599G 的 vhdx，还差一截）；E 腾出的空间留给软件增长与温层；
- **诚实的中期预警**：D 盘（731G）装"项目 75G + vhdx 599G"已是极限，2-3 年后若热层稳态被 vhdx 惰性顶破，正解是**加一块内置盘**（NVMe/SATA 均可，1-2T 级），而非在现有四盘间辗转；届时若必须迁，先批 A 清库再压缩 vhdx（届时压缩只回收垃圾空洞，不占未来空间），400G 体量迁 E 才可行。

## 7.5 v2 待拍板

1. 批 A 三项（日志级别调整窗口 + 尸体表处置方式：先归档 or 豁免直删）；
2. 批 B 调换执行窗（F↔G 搬运约 1.1T 跨 USB，建议过夜；搬前 backup.ps1 手动刷一次）；
3. working_vault 留 F 的例外是否接受（小文件 IO 理由）；
4. /mnt/chbackup_local（VM 内第二块"备份盘"1081G/余 698G）的物理身份待核实（疑似 F:\ch_vm_backup 映射），调换后需同步改映射。

> v2 后续演进见 `docs/_working/disk_reorg_campaign/a0_master_order.md`（收口六波总令）与 `docs/_working/cold_backup_automation/00_master_plan.md`（冷储备份自动化方案）。本文档于 2026-09-20 深夜被他会话 sweep 吞失一次，已由原作会话从对话权威底稿原样重建。
