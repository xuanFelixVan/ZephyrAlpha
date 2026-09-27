---
ttl: task_bound
---
# F/G 冷储+备份体系外部审查案卷（只读调研）

- 审查对象：G 冷储备份仓 + F 冷储专项盘的分类与文件管理体系
- Owner 痛点：文件漂移 / 幻觉 / 文件找不到 / 文件乱放 / 重放
- 审查模式：**只读**。未做任何写操作、未改代码、未跑 git 写命令。本文件是唯一产出（`.runtime/tmp/`，24h TTL）。
- 审查日期：2026-09-28
- 证据等级标注约定：[亲验]=本人数到/跑到；[读档]=转抄既有文档声明；[推断]=由亲验数据推出的结论
- 纪律声明：本案卷**只出案卷不出裁定**。凡引用裁定编号，均已在 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 中 grep 到原文并摘录；grep 不到者一律标"未裁/在案声明"。

---

## 0. 执行摘要

一句话：**盘面上的"体系"是齐的（五张导航 + 契约 + 审计 SOP + 六阶段流水线 + CH 双链 + 夜镜像 + 假绿闸），但执法面几乎全停在文档/散文层，写者层仍在按 2026-09-24 之前的旧盘符地图动作。** 本案卷实测到 **4 条已发生的实锤级不一致**（案 A/B/C/G）与 **2 条静默账目缺陷**（案 D/E），其中案 A 是 LEDGER_final.md 处方 P-6 于 09-25 预言、09-26（周六）06:00 如期发生的事故，至今（09-28）无人回填、注册表与盘头导航仍宣称该状态成立。

案索引：**A** F 侧"配置级轻备份"被周六任务自动摧毁（599G 回灌，F free 818→167G）｜**B** G 侧唯一全量冻结镜像无刷新通道（停在 2026-08-22）｜**C** 契约指定的归档第二副本落在未登记孤儿目录、被周检判据划入"杂物"射程｜**D** archive_manifest 首行被 UTF-8 BOM 静默吞掉（archiver 读 2517/2518）｜**E** manifest 无版本列 + 35 组键碰撞 + 两读者"最新"语义相反 + checksum 覆盖仅 308/2518｜**F** 十条次级不一致清单｜**G** /MIR 传播删除在冷库链原样在役（同 2026-09-14 事故机制）。

| 痛点 | 现有防线 | 防线有无读者 | 本案卷判定 |
|---|---|---|---|
| 漂移 | P-1 一次性改锚 / P-13 探针 cfg_key 派生 | 部分有（cfg_key 在码 [亲验]） | 🟠 改锚无持续执法；实测 4 处写者仍硬编码盘符 |
| 幻觉 | INFRA-STORE-003 方法论注记 / verify_suite 哨兵 | 哨兵只查字符串在不在 HEAD，**不查数字真值** | 🔴 三处数字口径并存，注册表仍载已被证伪的"降配置级"叙述 |
| 找不到 | 五张导航 + drawers + archive_manifest + ROOR + 仪表盘两位探针 | Parquet 归档层可反查；**非归档层不可文件级反查**（drawers 仅 11 行批次级） | 🟠 半合格；规约件（AUDIT_SOP/RETENTION/导航）不在版本控制，唯一"副本"=同机 F→G 夜镜像，与案 G 同生死 |
| 乱放 | 盘头"新增必同步"纪律 + 周检 §二.1 以三张导航为期望集 | 有读者，但**判据自伤**（把契约指定第二副本区划入杂物） | 🔴 实测 6 类未登记项（含 2 类设计内组件），零写入前闸（GATE-COLD-INBOX 全仓零命中） |
| 重放 | archiver 三阶段 verify + restore checksum 守卫 | 守卫在码但**覆盖仅 308/2518 条** | 🔴 账目无版本列 + 35 组键碰撞 + 两读者语义相反；data.vhdx 现两份不同日期且 restore 与 verify 各看一份 |

---

## 1. 体系盘点：F/G 顶层目录、写入方、保留政策

### 1.1 盘上实测（[亲验]，2026-09-28 本机 `ls` / `Get-Volume`）

容量实测（`Get-Volume`，[亲验]）：**D free 18.8G｜C 26.3G｜E 295.9G｜F 167.6G｜G 1432.2G**

| 盘/目录 | 用途（声明真源） | 写入组件 | 保留/轮转政策在册处 | 实测状态 [亲验] | 一致性 |
|---|---|---|---|---|---|
| `F:\zephyr_cold\` | 冷库主库（六区 00/10/20/30/40/50/90） | 人工入库四步 + `scripts/ch/archiver.py`（50_archive）+ `rolling_archive_reconciler.py` | `F:\zephyr_cold\README.md`+`RETENTION.md`+`data_retention_contract.yaml`+`F:\zephyr_cold\AUDIT_SOP.md` | 存在；另含 README 未声明的 `library/`、`AUDIT_SOP.md`、`RETENTION.md` | 🟡 未登记顶层 |
| `F:\ch_vm_backup\` | "已降为**配置级**（boot.vhdx + 配置；data.vhdx 冻结在 G）"（`F:\README.md:15`、INFRA-STORE-003 note） | `scripts/backup/backup_ch_vm.ps1`（周六 06:00 -AutoCheck） | `G:\backup\README.md:14,21`（冻结档不轮转） | **`data.vhdx` = 643,175,546,880 B（599 GiB），mtime 2026-09-26 06:00** | 🔴 **与声明方向相反**（案 A） |
| `F:\ch_backup_disk.vhdx` | CH 第一备份链盘（VM SCSI 直挂，运行期禁搬） | CH `BACKUP`（VM 内） | 无政策册；10-05 计划摘盘 | 在盘 | 🟢 |
| `F:\db_dumps\` | 旧散件 dump 遗留（声明 0.36G，"待清理（已签）"） | 无（已改家 G） | `backup_config.yaml:49-53` 真源在 G | 存在 `20260921/` + 根 4 件 + `zephyr_quarantine/` | 🟡 无主遗留 |
| `G:\backup\working_vault\` | 代码+配置日期化版本快照 | `backup.ps1` STAGE 3（硬链接去重） | `backup_config.yaml:43-47`：14 天 / free_floor 60GB / min_keep 3 | 存在 | 🟢 |
| `G:\backup\db_dumps\` | PG/SQLite 日期化 dump | `backup.ps1` STAGE 3（`/E` 进日目录） | `backup_config.yaml:49-53`：14 天，轮转闸=CH ok | 存在；另有嵌套 `db_dumps/db_dumps`（旧 /MIR 根冻结件） | 🟡 嵌套旧根待清 |
| `G:\backup\git_bundles\` | git 全史 bundle，7 天一造留 2 份 | `backup.ps1` STAGE 3b | `G:\backup\README.md:12,20` | 存在；另有嵌套 `git_bundles/git_bundles`（09-14/09-15，853.7MB） | 🟡 嵌套旧根待清 |
| `G:\backup\offrepo\` | 仓外关键资产镜像（4 targets） | `backup.ps1` STAGE 3c（`/MIR /XJ`） | `backup_config.yaml:97-110`，登记真源 `config/asset_inventory.yaml` | 存在；另有嵌套 `offrepo/offrepo_backup`（136.6GiB 旧树） | 🟡 嵌套旧根待清 |
| `G:\backup\ch_vm_backup\` | "CH 虚拟机全量镜像（**冻结档**）…CH 升级时由 backup_ch_vm.ps1 重做全量" | **声明写者=backup_ch_vm.ps1** | `G:\backup\README.md:14,21` | `data.vhdx` mtime **2026-08-22 06:00**（37 天前），**backup_ch_vm.ps1 全文 0 处 G: 引用** | 🔴 **刷新通道不存在**（案 B） |
| `G:\backup\predelete_deltas\` | 删除前证据包（永不删除） | 人工审计留痕 | `G:\backup\README.md:15` | 存在 | 🟢 |
| `G:\ch_backup_disk2.vhdx` | CH 第二备份链盘 | CH BACKUP 双写 rsync | 无册；10-05 后升唯一链 | 在盘 | 🟢 |
| `G:\zephyr_cold\{00,10,20,30,40,50,90}` | F 冷库迁移原件留观 | 已停写（留观中） | "2026-10-21 删"（`G:\zephyr_cold\README.md:41`） | 存在 | 🟡 到期删除依赖人工 |
| `G:\zephyr_cold\60_mirror\zephyr_cold_main` | F 冷库夜镜像 | `backup.ps1` STAGE 3d（`/MIR /XJ`） | `backup_config.yaml:65-73` | 存在 | 🟢 |
| `G:\zephyr_cold\60_mirror\zephyr_cold_archive` | **滚动归档第二副本落点** | `rolling_archive_reconciler.py`（`_second_copy`） | `data_retention_contract.yaml:441` `mirror_root` | 存在，305 件，**mtime 停在 2026-09-21 16:07** | 🔴 不在 g_mirror 目标、不在 README（案 C） |
| `G:\zephyr_cold\60_mirror\zephyralpha_ch_waste_tables_{20260920,1970clean_20260922}` | 废表 export 双副本历史落点 | 人工/废表批 | 无册 | 存在 | 🟡 无主目录 |
| `G:\zephyr_cold\00_charter.md` / `passed_candidates.yaml` / `s1_candidates.yaml` | **st-pqmine-20260927 战役在途工文件** | 他会话直写 | **无任何声明/登记** | mtime 2026-09-27 05:04 | 🔴 备份盘根混入在途工（§3.4） |

### 1.2 架构定案与政策真源层级

- 四盘分工唯一真源 = `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml:214-229`（INFRA-STORE-003）；冷归档层=同文件 `:197-211`（INFRA-STORE-002，host 已指 `F:/zephyr_cold/50_archive/by_project/zephyralpha`）。
- 保留层真源 = `docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml` v1.3.0（`:43/:47` 版本；INV-RET-001~006 在 `:53-84`；§5B rolling_archive 参数块 `:430-441`）。
- 盘上导航四件自述"**禁止成为第二真源**"（`F:\README.md:3`、`G:\README.md:3`），机器真源=backup_config + drawers.jsonl + INFRA-STORE-003。
- 冷库三红线：`docs/_working/altdata_line/10_g_drive_cold_storage_sop.md:38-42`（immutable / 禁双真源 / 回测数据的家不在冷库）。
- 审计节奏真源 = `F:\zephyr_cold\AUDIT_SOP.md` v1.1（日 5min / 周 30min / 月 2h / 季半天）。
- 3-2-1 落点：D 生产 + F 冷主 + G 备份总仓；offsite=Owner 月度手动第三块盘（`docs/_working/disk_reorg_campaign/offsite_monthly_manual.md` 首段）。**裁定原文可摘出的仅 #380⑥"撤销=异地备份 Owner 自办（拔盘存放其他电脑），执行线不建异地机制"、#380⑦/#381"db_dumps 快照 14 天滚动"、#380⑤"影子→半自动→全自动当天一次性全流程试跑跑通（原三步走作废）"、#383"storage_tiering.py 纸面模块退役"**（`ruling_registry.yaml:5007/5039/5076`，本卷已逐条摘原文）。

---

## 2. 文档 ↔ 实现一致性（审查重点）

### 案 A【实锤·最高优先】F 侧"配置级轻备份"已被自动摧毁，文档未更新

| 面 | 说的是 | 实测 |
|---|---|---|
| `F:\README.md:15` | "ch_vm_backup\\ 已降为配置级…data.vhdx 全量镜像冻结于 G:\\backup\\ch_vm_backup…2026-09-24 瘦身完成" | `F:\ch_vm_backup\data.vhdx` **643,175,546,880 B，mtime 2026-09-26 06:00** [亲验] |
| `infrastructure_registry.yaml:229`（在 git 内的注册表 note） | "全机镜像 data.vhdx（591.57G…）**仅存**冻结档 G:/backup/ch_vm_backup…F:/ch_vm_backup **降配置级**" | "仅存"已不成立：盘上两份（F 新 + G 旧）[亲验] |
| 写者 | 无人预期周六会真跑 | `logs/ch_vm_backup_20260926_060001.json`：`success:true`、`backup_path:"F:\\ch_vm_backup"`、`data_vhdx_gb:599`、`duration_seconds:3258.6`、`stop=ok/start=ok`；`data/databases/backup_state.json`：`last_ch_vm_autocheck_result="full_backup_done"`；`Get-ScheduledTask ZephyrAlpha-WeeklyVMBackup` last=2026/9/26 6:00:00 result=0（2026-09-26=周六）[亲验] |
| 后果 | `F:\zephyr_cold\AUDIT_SOP.md:9` 日检判据 F≥700G free | F free **167.6G**（全盘 1863G 的 9.0%，同时跌破冷库 SOP §7"剩余<10% 报备"）[亲验] |
| 根因 | — | `scripts/backup/backup_ch_vm.ps1:50` `$BackupRoot = "F:\ch_vm_backup"`（全文 0 处 G:）。**LEDGER_final.md:249 处方 P-6 预言的分支于 09-26 如期发生**："若哪个周六 config 漂移触发真跑，脚本会向已被 Owner 降为'配置级'的 F 侧再灌 ~591G（F free 766.7→约 175G，击穿 F≥700G 红线并推翻 10-05 摘盘预算）" |

**加重项（[亲验] 代码+日志）**：该次报告 `ch_version:""`、`ch_config_hash:""`（VM 重启后第 6 步探测失败），而 `backup_ch_vm.ps1:429-430` 仅非空才写 state → state 停留在 09-19 旧基线。更关键：`backup_ch_vm.ps1:169-179` **AutoCheck SSH 探测失败即 "forcing full backup"**——fail-open 到最重代价分支（停 VM + 599G 拷贝 + 54 分钟 CH 停机）。故 10-03 周六在 `.env.ch_backup` 缺失或 SSH 抖动时会再来一次，届时 F 已无 600G，`:243-245` 空间闸将 `exit 1`＝**"要么灌爆 F、要么全量镜像永不做"**的二选一，而 G 冻结档仍停在 8-22。

### 案 B【实锤】G 侧唯一"全量冻结镜像"没有任何工具能刷新

`G:\backup\README.md:14` 声明"CH 升级时由 backup_ch_vm.ps1 重做全量"；`backup_ch_vm.ps1` 全文不写 G。实测 `G:\backup\ch_vm_backup\data.vhdx` mtime **2026-08-22 06:00**、635,189,592,064 B [亲验] → 37 天陈旧；`restore.ps1 vm` 若执行即回灌 8 月旧基座（与 LEDGER_final.md:249 判断同向，本案卷独立复算证实）。定性：**文档声称的刷新通道与实际写入路径分属两块盘**。

### 案 C【实锤】归档"第二副本"落点是未登记孤儿目录，且被周检判据划入"杂物"射程

- `data_retention_contract.yaml:441`：`mirror_root: "G:/zephyr_cold/60_mirror/zephyr_cold_archive"`（drop 前第二副本的**契约指定家**）。
- `backup_config.yaml:70-73`：g_mirror.targets 只有 1 条（`zephyr_cold → G:\zephyr_cold\60_mirror\zephyr_cold_main`）→ **第二副本区不在任何镜像/轮转/对账通道内**。
- `G:\zephyr_cold\README.md:39` 声明本目录"现存：六区 + 60_mirror（F 冷库夜镜像）+ README.md"→ 未承认 `zephyr_cold_archive` 与两棵 `zephyralpha_ch_waste_tables_*`。
- 实测：`60_mirror\zephyr_cold_archive\c1_market\kline_etf_15min\…` 305 件、mtime 2026-09-21 16:07（7 天零更新）[亲验]。
- 交叉危害：`AUDIT_SOP.md:18` 周检 §二.1 判据="多出的顶层条目=未登记杂物（下次审计清理）"。**若某班照字面执行，会把已 DROP 分区唯一的第二副本当杂物清理**。[推断，三条前置均 [亲验]]

### 案 D【实锤·账目】archive_manifest 首行被 BOM 静默吞掉

- `scripts/ch/archiver.py:465-475` `_read_manifest()` 以 `encoding="utf-8"` 打开，解析失败 `continue`（静默）。
- `F:\zephyr_cold\50_archive\by_project\zephyralpha\archive_manifest.jsonl` 前 3 字节 = `EF BB BF` [亲验]。
- 本人用 **archiver 原逻辑**复跑：`records read = 2517 / silently skipped lines = 1`，被吞的是首条 `c1_market.kline_60min / 200007` [亲验]。
- 影响面：`list` / `stats` / `_is_archived` / `_manifest_checksum` / `restore` 全走 `_read_manifest` → 该分区对账目不可见（文件在盘）。
- 数字口径并置 [亲验]：实测 2,518 行 / 2,517 可读；LEDGER_final.md:235 称"全量 2,515 行"、§十六 称"清单 2515 件在位"。

### 案 E【实锤·账目键碰撞】manifest 无版本列、`(table,partition)` 非唯一

- 字段覆盖 [亲验]：`rows/checksum_md5/ch_size_bytes/compress_ratio` 仅 **308/2518** 条具备；`period` 仅 64 条 → **88% 记录无 checksum**，`archiver.py:806-816` 的 restore checksum 守卫对它们返回 None 直接放行（"无校验=放行"）。
- 键碰撞 [亲验]：`(table,partition)` 去重后 2483，**35 组碰撞涉及 70 行**；例 `c1_market.technical_indicator`+`201901` 同时存在 `…/60min/201901.parquet` 与 `…/120min/201901.parquet`，**两条都无 period 字段**。
- 读者语义互斥 [亲验]：`_is_archived()`（`:477-487`）取**第一条**命中、`_manifest_checksum()`（`:626-636`）取**最后一条**命中 → 同一 append-only 日志两个相反的"最新"定义；重跑归档时断点续传可能因另一频率同名分区被判"已归档"而跳过。

### 案 F【不一致清单·其余】

| # | 文档声明 | 实现/实测 | 证据 |
|---|---|---|---|
| F-1 | `a5_delivery_report.md:76`"G 镜像**五目标**全 ok（含 ch_vm_backup 592G）" | `backup_config.yaml:70-73` 现仅 **1** 目标（ch_vm_backup 09-24 摘除） | [亲验] 配置 vs [读档] 报告；报告非机生，不随配置刷新 |
| F-2 | `00_master_plan.md:42/:46/:257` working_vault=`F:\working_vault`、offrepo=`F:\offrepo_backup`（标"**已自动化**"） | 两者实测 **MISSING**（09-21 改家 G） | [亲验] `os.path.exists`；而 00 册被 `a4_go_signal.md:52`、`w_line_b_disk_ch.md:18` 登记为**在役母方案/施工真源** |
| F-3 | `backup.ps1:17` 头注释"DB dumps: robocopy /MIR（overwrite by design; each dump replaces the old one）" | STAGE 3 实为日期目录 + `/E` + 14 天轮转（`:677`、`:690-693`） | [亲验] 注释与实现相反 |
| F-4 | `10_g_drive_cold_storage_sop.md` 全篇以 **G:\zephyr_cold** 为冷库主体（标题/§1/§7） | 冷库主库已定案为 **F**；`F:\zephyr_cold\README.md:1` 标题仍写"（G 盘）"，与 `G:\zephyr_cold\README.md` 近乎完全重复 | [亲验] → 违反三红线之二"禁双真源"，且真源口径本身过期 |
| F-5 | `config/asset_inventory.yaml:139` 冷归档路径 | `yaml.safe_load` 后实际值 = `F:\\zephyr_cold\\50_archive\\by_project\\zephyralpha`（**双反斜杠**），与 INFRA-STORE-002 的 `F:/zephyr_cold/...` 字面不等 | [亲验] → 任何跨册字符串等值对账必判不一致 |
| F-6 | 冷库"先登记后建目录"（SOP `:14`、§2 四步） | `F:\zephyr_cold\library\{20260924..20260927}`、`G:\zephyr_cold\00_charter.md`+两个 `*_candidates.yaml` 均未登记、不在三张导航、不在 drawers.jsonl | [亲验] 目录列表 vs drawers 11 行逐行比对无对应项 |
| F-7 | 台账唯一真源 | `src/zephyr/data/implementations/akshare_alt_provider.py:423` `_CW_MANIFEST = Path("G:/zephyr_cold/00_manifest/drawers.jsonl")` 仍指 **G 侧旧库**（G 原抽屉库已签 10-21 删） | [亲验] 源码 + G 侧 drawers 仅 6 行/停在 09-18，F 侧 11 行 → **同一台账两份，活写者在写旧的那份** |
| F-8 | 契约 `:60-62` 滚动归档"事件触发自动（五重安全阀）" | `backup.ps1:965-978` STAGE 4b 以 `--mode full_auto` 挂备份成功事件（与裁定#380⑤ 一致，非违规）；但 `data/databases/rolling_archive_state.json` = `{"consecutive_failures": 1, "kill_switch": false, "circuit_open": false}`，`data/audit-trail/rolling_archive_plan_shadow.jsonl` 末批为 2026-09-21 **合成测试数据**（`table:"t0"/"t1"`、`rows:1`、`bytes_on_disk:4000000000`） | [亲验] → 全自动通道在役且带 1 次连败；唯一留痕是假数据写进生产审计面（宪法 §9.6 测试隔离反例）；真实自动归档产出无在案证据 |
| F-9 | `00_master_plan.md:174-179`"三红线固化为代码检查（GATE-COLD-INBOX）" | 全仓 grep `GATE-COLD-INBOX` **零命中** | [亲验] → 装饰件判据命中：三红线目前只有 README 散文，无执法读者 |
| F-10 | `00_master_plan.md:204`"把 git_bundles 目录纳入 3d 即可" | `backup_config.yaml:70-73` g_mirror 无 git_bundles 目标 | [亲验] → git 全史只在 G 单盘，3-2-1 的 bundle 腿未离场 |
| F-11 | 冷库 SOP `:30`"体积 >10GB 的批次登记时**必须带 sha256**"（三红线之外的第 4 条硬规则） | `F:\zephyr_cold\00_manifest\drawers.jsonl` 全 11 行中**只有 1 行**有非空 sha256；两个 >10GB 批次登记值为 `"sha256": null`——第 7 行全库迁移 147.8G、第 8 行 C4 考试 PDF 缓存 56.6G/60,245 件 | [亲验] 逐行核；且 `AUDIT_SOP.md:25` 周检 §二.7 只判"逐行 json.loads 合法 + path 在盘"，**不判 sha256 有无** ⇒ 该硬规则既无写者自查也无读者尺（装饰件判据再次命中） |

（§2 一致性清单续见 **案 G**（/MIR 传播删除·冷库链，见 §6）与 §6 盘面实况补充；restore/reconciler 侧实测记在 §5-6 条与 §6.1-6.2。）

### 反向记录：确实在役且可信的防线（避免本卷只报忧）

- `scripts/backup/backup_reconciler.py:8` 不变式 **INV-11**（假绿闸：落 ok 前用 `system.backup_log` 当窗 `BACKUP_CREATED` 交叉核验，不过则降级 `ch_log_missing` 并连带摘除 `last_ch_backup_status` 的 ok）/ **INV-12**（lock-skip 分因、不推进计时、不降级真实状态）/ **INV-13**（P-7 点火-托管分离，沿活 PPID 链免疫级联收割）三条**均在码**，核验 SQL 集中化为唯一消费点 `query_backup_log_created`（`:154-157`、`:305`）[亲验]；且**读取端已统一 `utf-8-sig`**（`:374`、模块注释 `:62`）⇒ 案 D 的 BOM 坑在 reconciler 侧已治、在 archiver 侧未同治，是同一坑的两次踩法。
- `backup.ps1:494-514` 版本化快照 + 硬链接去重 + `free_floor_gb` 空间保险实现与 `backup_config.yaml:37-47` 一致 [亲验]；P-15 跨零点日期撕裂已用 `$RunAt` 单点锚定（`backup.ps1:40` 注释 + LEDGER_final.md:390）[亲验码注释]。
- `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` 现 `total_gates: 181` 且 `gate_id:` 实数 **181** ⇒ LEDGER_final.md:447 处方 P-21（180 vs 174 派生标量漂移）**已由生成器重算闭合** [亲验]。这条正是 §5 第 4/7 条建议要复制的范式：派生数一律生成器重算，不手改标量。

---

## 3. 五痛点现状判定

### 3.1 漂移（路径写死 / 绝对路径漂移）

- 现有防线：①P-1 一次性改锚（LEDGER_final.md:287，2,210 行 E→F 前缀替换 + `.bak` + sha256 入 drawers 第 11 行）[读档]，本次亲验 `.bak` 在盘；②P-13 仪表盘探针"从 backup_config 派生真源、盘上字面量降为 fallback"（`services_registry.py:250` `cfg_key: "working_vault"`）[亲验]；③`restore.ps1:75-78` 同款 config 派生（vault/dumps 两家从 `backup_config.yaml` 正则解析，字面量仅作 fallback）[亲验]。
- 防线有无读者：**派生通道有读者**（restore/dashboard 两处确实在读 config）；**改锚无读者**——是一次性人工动作，全仓不存在"manifest 路径 vs ARCHIVE_ROOT 一致性"检查项，也不存在"注册表路径 vs 盘面存在性"检查项。
- 散布的硬编码盘符（[亲验] 逐条定位）：**写者侧 3 处** = `scripts/backup/backup_ch_vm.ps1:50`（F:\ch_vm_backup，全仓唯一未跟 config 化的备份写者）、`src/zephyr/data/implementations/akshare_alt_provider.py:422-423`（G:/zephyr_cold 快照区 + 台账）、`src/zephyr/data/implementations/irm_provider.py:91`（`_SNAPSHOT_ROOT = Path("G:/zephyr_cold/30_corpus/web_snapshots")`，而 G 原抽屉库已签 2026-10-21 删）；**登记/配置侧 2 处** = `config/asset_inventory.yaml:139`（双反斜杠，案 F-5）、`backup_config.yaml:33`（`code_backup.target: "F:\\code_backup"`，实测 MISSING，注释自称"保留供回滚参考"）。
- 缺口：**根因不是路径字符串，而是"写者硬编码盘符 + 无存在性尺"**——案 A/B/F-7 各一例；改一次锚不阻止下一次漂移，而 G 侧那两处写者一旦 10-21 按期删库即成新断链（当前无探针会红，因为 dashboard 只探 F 侧）。

### 3.2 幻觉（文档数字/副本数与实际不符）

- 现有防线：INFRA-STORE-003 方法论注记"同名+同尺寸判重≠内容等值，等值判定必须全量 hash"（`:229`）[读档]；LEDGER_final.md:14 记"三份等值口径作废"（09-24 三方 hash 证伪后写注册表，commit 364aefa2）[读档]；`verify_suite.py` 31 项含"注册表口径在 HEAD"哨兵 [读档 LEDGER_final.md:33/:54]。
- 防线有无读者：哨兵只查**标记字符串是否在 HEAD**（防蒸发），**不查数字是否为真**。故本轮实测的失真全部穿过：①"F 已降配置级"仍在注册表（案 A）；②a5"五目标"对 1 目标（F-1）；③manifest 2,515/2,517/2,518 三口径（案 D）；④`drawers.jsonl` 第 3 行仍写"研报库(F盘6万+E盘3万**未来迁入**)"，而 E 侧 3 万已于 09-24 删且内容已在 F [亲验 台账文本]。
- 缺口：**没有任何机制把"文档里的体积/件数/副本数"与盘面实测绑定**（无件数/字节快照册，无 regen-clean 对账项）。

### 3.3 文件找不到（统一索引）

- 现有防线：三张盘上 README（顶层导航）+ `00_manifest/drawers.jsonl`（抽屉台账）+ `archive_manifest.jsonl`（Parquet 逐分区）+ `registry_of_logs.yaml:808`（把仓外 manifest 路径登记进 ROOR）+ `services_registry.py:230-251`（cold_archive/code_backup 探针）。
- 能否从仓库反查盘上文件？分层判：**Parquet 归档层=能**（逐件 + ROOR 指针 + 探针）；**非归档层=不能**——drawers.jsonl 全 11 行只覆盖约 9 个批次，137.55G 研报语料、C4 52.7G 等只有批次级一行且 `sha256: null`，无文件级清单；G:\backup 侧只有目录级 README 表，无文件级索引。
- 缺口：①**索引自身两个真源且已分叉**（F 11 行 / G 6 行，活写者指 G——F-7）；②**规约只存 USB 盘**：`F:\zephyr_cold\AUDIT_SOP.md`、`RETENTION.md` 不在 git、不在图书馆，盘坏/盘离即规约不可读、无版本史、无 diff（`F:\README.md:3` 是有意识的取舍，但代价未对冲）。

### 3.4 文件乱放（无主/未登记）

- 现有防线：盘头纪律"新增顶层必同步本文件+注册表，否则视为未登记杂物"（`F:\README.md:4`、`G:\README.md:4`）；`AUDIT_SOP.md:18` 周检 §二.1 以三张导航为期望集。
- 防线有无读者：**有读者但判据自伤**——09-25 班确实执行过并判"逐项全等，零未登记杂物"🟢（LEDGER_final.md:226）[读档]；但同一判据把契约指定的第二副本区（案 C）划入清理射程。
- 实测无主/未登记项 [亲验]：`F:\zephyr_cold\library\{20260924,20260925,20260926,20260927}`（每日 03:30 出现，与 `ZephyrAlpha_LibraryLedgerBackup` 任务时刻吻合——该任务 last=2026/9/27 3:30:01 result=0）、`G:\zephyr_cold\00_charter.md`/`passed_candidates.yaml`(164,238B)/`s1_candidates.yaml`(25,646B)（他会话在途工直写备份盘根）、`G:\zephyr_cold\60_mirror\zephyralpha_ch_waste_tables_*`（两棵）、`G:\backup\{offrepo\offrepo_backup, db_dumps\db_dumps, git_bundles\git_bundles}`（三棵嵌套旧根，LEDGER_final.md:394 处方 P-16 已在案待批）、`F:\zephyr_cold\90_tmp\{drill_gov.db 201,347,072B, drill_bundle, conv_etflof}`（30 天 TTL 遗件，09-25/26 起至今未清）。
- 缺口：**没有写入前的"该盘该层是否允许写"闸**（F-9）。

### 3.5 重放（同一数据多副本无版本列 / 旧行覆盖修正行）

- 账目面：见案 D/E——append-only、无版本列、无唯一键、无 schema 版本，两读者语义相反，35 组键碰撞实测。
- 副本面 [亲验]：`data.vhdx` 两份不同日期（F 09-26 / G 08-22）无权威标签；`G:\backup\db_dumps\db_dumps`（0.36G）+ `F:\db_dumps` 根 4 件（含 193,933,312B 的 governance_backup.db，09-21 冻结）与日期化快照并存；LEDGER_final.md:394 已证其中 **2 件为全树独有**（"禁并入删除批"）[读档]。
- 表引擎面 [推断，未核]：Owner 所点"CH ReplacingMergeTree 无版本列导致旧行覆盖修正行"——本卷只读范围未逐表核 DDL，仅见 LEDGER_final.md:135 对 `kline_etf_15min = ReplacingMergeTree ORDER BY(symbol,trade_time)` 的读档记录（未列版本列）。**列为待查项 R-1，不判真伪。**
- 防线有无读者：checksum/行数 verify 是 archiver 三阶段真闸（`archiver.py:494-520` 在码 [亲验]），但**覆盖仅 308/2518** → 对存量 88% 记录，"重放/静默腐坏"防线是装饰件。

---

## 4. 机构与社区对标（可借鉴点 / 不匹配点）

> 说明：本册对标的是"机制族"，不引具体论文/版本号；不确定处已标 [推断]。项目自身已用过该语汇——`00_master_plan.md:184` 标题即"现状到 **3-2-1-1-0** 的映射"，说明立法者知道行业标准式，缺的是后两腿（1 offline / 0 errors=verify）。

| 族 | 成熟做法 | 可借鉴点（对本仓） | 不匹配点（为何不能整块搬） |
|---|---|---|---|
| **3-2-1 + 不可变快照** | ZFS `snapshot` + `hold`/`readonly`；NetApp Snapshot + SnapLock；AWS Backup **backup vault lock**（WORM，retention 期内不可删）；S3 **Object Lock**（governance/compliance 模式）；ReFS 完整性流 | 本仓"删除前两份验证副本+留观 30 天"（a3 通则 1）本质是**流程式不可变**，可升级为**属性式**：冷库 20/30/50 已声明 immutable（SOP §4 红线 1），但盘上是普通可写文件——给 50_archive 已归档分区目录设只读位/SDDL 拒写，即可让"只进不改"从散文变物理约束（本案卷案 C 的误删风险同时被拦） | 无 ZFS/Storage Spaces 奇偶校验层；F/G 是 USB 单盘、NTFS 普通卷，快照要靠 VHDX（项目已有 VHDX 压缩机制，但压缩=破坏快照式时点）；`robocopy /MIR` 的设计前提就是"可传播删除"，与不可变哲学正面冲突（`00_master_plan.md:293` 也承认该张力） |
| **数据湖表格式（时间旅行 / schema 登记）** | Apache **Iceberg**：catalog → snapshot → manifest list → manifest file，每条记录带 `status`（EXISTING/ADDED/DELETED）、`file_size`、分区统计、schema-id、spec-id；**Delta Lake**：`_delta_log/` 事务日志（JSON commit + checkpoint）天然版本化；**Hudi**：timeline + commit/deltacommit + Metadata Table；三家共同点=**"清单本身有版本、有状态列、有唯一提交序列"** | 直接对症本案卷案 D/E：`archive_manifest.jsonl` 缺的正是 (a) `status` 列（现仅 verified/dropped 两个布尔，无 ADDED/DELETED 语义）、(b) 版本/提交序列、(c) 唯一键。最低成本借鉴=**在 jsonl 记录里加 `rev` 单调序号 + 把 `(table,partition,period,frequency)` 定成唯一键**，读者一律"取 max(rev)"（消灭 `_is_archived` 取首条 / `_manifest_checksum` 取末条的语义对立） | 全量迁 Iceberg/Delta 需 catalog 与写侧运行时（Iceberg 需 py-iceberg 或 Dremio、Delta 写侧要 JVM、Hudi 纯 JVM），与项目现查询路径"DuckDB 直读 Parquet"（`F:\zephyr_cold\RETENTION.md:42-43` 明写）冲突；2,518 个文件的量级用不上 manifest 分区统计优化；DuckDB 有 iceberg 扩展但读侧只解决查询不解决写侧治理 [推断] |
| **Parquet 分区目录约定** | Hive 风格 `db/table/year=YYYY/month=MM/` 或 `dt=YYYY-MM-DD`；分区列进目录名而非仅文件名，避免"同表同分区不同频率"互相遮蔽 | 本案卷实测到的 35 组键碰撞根因就在这里：`…/technical_indicator/60min/201901.parquet` 与 `…/120min/201901.parquet` 都只把 `201901` 记进 `partition`，频率层级丢了 `period` 字段（仅 64/2518 条有）。改法是**路径即键**：把目录层级里的 `60min/120min` 写进每条记录，而不是继续靠 `period` 可选字段 | 存量 2,210 条刚做过一次性改锚（P-1），再动键形即二次改账；须"新行新形 + 存量补算"双轨，不能一刀切 |
| **清单式账本（校验和清单）** | **BagIt**（RFC 8493）：`bagit.txt` + `bag-info.txt` + `manifest-<alg>.txt`（**每个 payload 文件一行 校验和+路径**）+ `tagmanifest-<alg>.txt`；**Frictionless Data Package / datapackage.json**：resources 里每条带 `path`/`bytes`/`rows`/`hash`/`mediatype` + `schema` | 对症 §3.3"文件找不到"与 §3.2"幻觉"：`drawers.jsonl` 现在 11 行、`sha256: null` 普遍（本次实测 F 侧 11 行仅 1 行有 sha256）→ 一个 >10GB 批次的抽屉只有一行批次登记（C4 56.6G/60,245 件 = 1 行）。BagIt 式"逐件校验和清单 + 批次 tagmanifest"即可让**任何抽屉可独立自检**，季检"路径幻觉扫描"（`F:\zephyr_cold\AUDIT_SOP.md:38`）也才有可跑的尺；`G:\backup\predelete_deltas\` 已经是证据包形态，只差按 BagIt 补齐 `bag-info` 与 payload 清单 | BagIt 逐件清单对 90,243 件研报会产生 ~9 万行/抽屉的清单文件（机械盘可接受，但必须决定"清单在哪本册子上"，否则又成第二真源）；Data Package 的 `schema` 强约束对本仓"原文快照"类数据价值有限 |
| **元数据登记（找得到）** | **DataHub / OpenMetadata / Amundsen**：dataset 唯一 URN + owner + schema + lineage + 可信标记 + "发现"检索；轻量同族=Federation 式 registry（本仓已有 ROOR 的概念同构） | 本仓已有等价物（ROOR `registry_of_registries.yaml` + `infrastructure_registry` + `library`），**缺的不是目录软件而是"盘上资产进目录"**：`G:\zephyr_cold\60_mirror\*`、`F:\zephyr_cold\library\`、三棵嵌套旧根都没进任何册子（§3.4）→ 最小动作是给 `config/asset_inventory.yaml` 扩一个 `drive_assets` 段，把"每个盘每个顶层条目 + 写入方 + 政策真源"登记成机读表，然后**由它生成三张 README**（一物两用：既补登记又消灭手工清单漂移，正合宪法 §9.5） | 上 DataHub/OpenMetadata 需要服务栈（ES/PG/kafka 或 server+DB），与"个人量化 + 全 AI 施工 + 上下文预算"不匹配；且这类工具解决"人找数据"，本仓痛点是"AI 写数据不登记"——治理点在生产侧不在检索侧 |
| **备份 verify / prune 语义** | **restic**：内容寻址 + 快照是树不是副本；`check`（结构完整性）/`check --read-data`（全量重读）/`verify --read-data-subset=5%`（随机抽读证明真能恢复）；`prune --keep-daily 14 --keep-within 7d` 由**策略**算保留集合并显式列出待删；**borg/borg2**：`archives` + `borg check`/`borg verify` + `--keep-within`；两家共同点=**"恢复演练是内建命令，不是人工脚本"**，且 **"删除是策略求解的结果，不是 Remove-Item 的位置参数"** | 对症两处：①本仓 vault 轮转是 `backup.ps1:661-665` 直接 `Remove-Item` 老日期目录，无"求解+清单留档"，与 a3 通则"任何删除先出清单留档"不一致；②灾备"演练"目前靠人跑 `restore.ps1 verify` + 一次性 `ZEPHYR-RESTORE-DRILL`，而 verify **不重读被恢复的那份数据**（本案卷 §5-7 条指出 verify 查 G、Do-Vm 用 F）。可借的是**语义**不是二进制：给 vault/dumps/镜像三链各加一条"抽读 N% 并留 JSON 报告"的事件钩子（项目已有 sha256 抽样法证能力，见 LEDGER_final.md:12-13 的逐 16MiB 块差分，把它固化成 `--read-data-subset` 式的常设探针） | restic/borg 把仓库换成内容寻址后，现有硬链接日快照 + robocopy 对账 + restore 分阶段脚本全部作废，改造半径=整个备份层；且 USB-HDD 上 restic 全仓 `check` 一次要跑满 4T（本项目 G 盘小文件 11.5 files/s 已实测是瓶颈，LEDGER_final.md:279）→ 成本上不可常设，只能"子集抽读" |
| **备份仓锁定 / 空气隙（air-gap）** | Veeam **immutable repository**（S3/对象锁或 Linux 不可变属性）；AWS Backup vault lock；离线副本=一次写一次读 | 本仓的"1 离场"腿=Owner 手动月度拿第三块盘（`offsite_monthly_manual.md`，且裁定#380⑥ 明文"执行线不建异地机制"）→ **不匹配点写死在这里**：任何"自动化离场副本"的建议都与在册裁定冲突，本卷只提"核对能不能证明真离过场"，不提"建机制"（§6-R3：`Get-Volume` 见 H: 但 Size/Free=0，无离场日志，故该腿目前不可证） | 见左 |
| **AI/vibe-coding 社区惯例** | "docs as data"（清单由真源生成，不手写计数）；单写者原则（one asset one writer）；机器可判不变式入 CI；ADR 记不可逆决定；"任何清单+计数若可派生则必派生" | 本仓宪法 §4.3 与 §9.5 已把这两条写成硬规则（"计数用字段不写死散文""静态清单禁手工维护"），**盘面五张 README 正是违反自己宪法的存量**（`F:\README.md:10` 写"2026-09-24 实测口径"、`:17` 写 0.36G、`G:\zephyr_cold\README.md:39` 写 ~327.2G，全是手写数）→ 与本案卷案 A 同源：手写数必然过期，过期叙述被后续会话当事实引用 | 无冲突，是纯内务；唯一约束=不得新增册子（宪法 §4.1 全资产净零），所以只能"改造现有导航件为生成物"，不能另起一套 |

---

## 5. 可抄作业清单（最小改动 × 落在现有执法面）

> 每条只给"落点文件 / 挂哪个现有机制 / 为什么不需要新增执法面"。**本卷不改判据、不改阈值**（凡涉阈值一律写"待 Owner 表态"）。

1. **manifest 路径改由真源重算 + 一次性 BOM 治本**（案 D、§3.1）
   - 落点：`scripts/ch/archiver.py`（`_read_manifest()` 改 `encoding="utf-8-sig"`，并把 P-1 的"一次性人工改锚"升级为 `--rebase-paths` 子命令：按 `ARCHIVE_ROOT` 重算 `parquet_path`，其余字段逐行 byte 不变，改前落 `.bak` + sha256 进 drawers——沿用 LEDGER_final.md:287 已验证过的动作，只是把它做成可重跑的工具）。
   - 挂点：把"manifest 每行 `parquet_path` 必须以 `str(ARCHIVE_ROOT)` 开头"作为一条断言测试进 `tests/scripts/backup/` 同族目录；无需新 gate（这是唯一写者自查，符合 RULE-SSOT"规则数据改 YAML 同步 DB"的方向性）。
2. **manifest 补版本列与唯一键**（案 E、§3.5"重放"）
   - 落点：`archiver.py:_manifest_record()` 增 `rev`（单调序号，读时 `max` 取最新）+ 把 `period`/频率层级写入**每条**记录（不再可选）；`_is_archived()` 与 `_manifest_checksum()` 统一改为"取该键 max(rev)"，消灭两读者相反语义。
   - 配套：新记录强制 `rows`/`checksum_md5`（现 308/2518 覆盖），存量补算走一次性脚本 + drawers 登记一行（同 P-1 留痕范式）。零判据改动。
3. **`backup_ch_vm.ps1` 写入家改读 config + AutoCheck fail-closed**（案 A/B，P-6 的治本形态）
   - 落点：`scripts/backup/backup_config.yaml` 新增 `ch_vm_backup: {config_home, image_home}`（键名自定），`backup_ch_vm.ps1:50` 的 `$BackupRoot="F:\ch_vm_backup"` 改为与 `restore.ps1:75-78` 同一套"从 backup_config.yaml 解析"的现成惯例（**restore.ps1 已经这么做了，backup_ch_vm.ps1 是唯一没跟上的写者**）；`:169-179` 探测失败分支从 `forcing full backup` 改为 `skip + 标红 + 报告`（fail-open→fail-closed，属"改变最坏结局方向"，涉生产流转，**待 Owner 表态**）。
   - 执法面：`tests/dr/` 已有一条 ps1 锁语义常驻尺先例（P-9，commit `ac1df94d42`，487 行）→ 同形再加"写入家与 config 同源"一案即可，不新建机制。
4. **盘面导航改生成物，并顺带补齐"盘上资产登记册"**（§3.2 幻觉、§3.4 乱放、§3.3 找不到）
   - 落点：`config/asset_inventory.yaml` 扩 `drive_assets` 段（每盘每顶层条目 + 写入方 + 政策真源指针 + 允许的子区），由它生成 `F:\README.md`/`G:\README.md`/`G:\backup\README.md`/两侧 `zephyr_cold\README.md` 的"顶层清单表"（计数与体积一律取实测刷新，不再手写）；仓库内保留该生成物的副本（进 `docs/` 生成区），使"规约不再只活在 USB 盘上"。
   - 挂点：生成器归 `scripts/governance/generators/`，事件触发复用现成"备份成功事件链"（`01_mining_findings.md` 意外发现 5 已论证该链是合法载体，禁新增 schtasks）→ 同时满足宪法 §9.5。
   - 顺手修：`asset_inventory.yaml:139` 的双反斜杠（案 F-5）+ 生成期做 `\`→`/` 归一后再与 INFRA-STORE-002/003 比对。
5. **冷库/备份双链对账 reconciler（把 AUDIT_SOP 的周检从人肉变事件）**（案 C、§3.4）
   - 落点：新 `ReconcilerSpec` 挂 `ReconciliationRegistry`（`01_mining_findings.md` §1 行 8 明写这是合法挂载点，且"异常降级 warn 不阻断"），三查：
     (a) **drawers 双真源合一**——`akshare_alt_provider.py:423` 的 `_CW_MANIFEST`/`_CW_SNAPSHOT_DIR` 与 `:91`（`irm_provider.py`）改读单一常量源（建议 `zephyr.shared` 或 config 派生），并断言"F 侧 drawers 是唯一活册、G 侧只读"（F-7）；
     (b) **60_mirror 子树白名单**——把契约 `mirror_root`（`data_retention_contract.yaml:441`）与 g_mirror.targets 的落点合成"60_mirror 允许子目录集合"，逐目录判定，命中"允许但 README 未声明"=生成导航，命中"两者皆无"=红项，**避免周检 §二.1 把第二副本判成杂物**（案 C）；
     (c) 报告落 `data/audit-trail/`，红项进 `services_registry.py` 新探测位（与现有 cold_archive/code_backup 两位同形，带 `cfg_key` 派生）。
6. **"实际会用哪份"进恢复就绪尺**（案 B、§3.5）
   - 落点：`scripts/backup/restore.ps1`——`Do-Verify`（`:357-368`）目前只验 `G:\backup\ch_vm_backup\data.vhdx` 在位，而 `Do-Vm`（`:615-622`）在 `F:\ch_vm_backup\data.vhdx` **存在时优先用 F**；两者当前分属不同日期的两份镜像（F=09-26 / G=08-22，均 [亲验]）。改法：verify 输出"本次将实际使用的镜像路径 + 大小 + mtime + 抽样 hash"，并在两份并存且不同源时报 WARN（不改任何判据阈值，只把已量到的事实印出来）。
   - 执法面：`tests/scripts/backup/` 同族加一案（与既有 44 例测试同批）。
7. **数字口径单一来源（把"手写计数"从册子上清出去）**（§3.2、宪法 §4.3/§9.5 的自查）
   - 落点：`infrastructure_registry.yaml:229`（INFRA-STORE-003 note）与两侧 `zephyr_cold/README.md` 的状态段里的体积/件数改为指向生成物（第 4 条）字段名，**不再在散文里写数字**；本案卷案 A 之所以能存活 4 天不被发现，正是因为注册表 note 是散文、无对账尺。
   - 挂点：沿用 `ZephyrAlpha_ResourceRegenCheck`（`schtasks` 实测 last=2026/9/27 9:21:22）这条既有 regen-clean 通道，把"注册表数字字段 vs 盘面实测"列一项。
8. **第二链/镜像新鲜度改成"读者可判定"的时戳源**（案 C 7 天零更新、§3.2）
   - 落点：`rolling_archive_reconciler.py:283` 的默认 `mirror_root` 字面量与契约同值=双写（违反 INV-RET-006"禁码内第二真源"的字面），改为"仅从 `load_contract_params()` 取，缺键即拒绝该阀"（fail-closed）；并在每次 `_second_copy` 成功后把目标目录 mtime/件数写进 `rolling_archive_state.json` 旁的报告，使"第二副本是否真的在长"可被日检直接读（现该目录停在 09-21 而状态文件只记 `consecutive_failures:1`，看不出第二副本 7 天零写入）。

---

## 6. 盘面实况补充（本轮新实测，2026-09-28）

| # | 实测 | 关联 |
|---|---|---|
| 6.1 | 最新一轮备份 `logs/backup_report_20260926_220344.json`：`timestamp=2026-09-27T07:57:22+08:00`、`duration_seconds=35617.9`（**9.9 小时**）、`code_backup.copied=180,415` / `hardlinked=0` / `failures=0`，`g_mirror` 1 目标 ok，`offrepo_backup` 4 目标 ok，`git_bundle count=2 status=skipped(age 1.29d)`，`databases.clickhouse=skipped(24h cadence)` | **P-2（`.worktrees` 未入排除清单）仍未落地**：单轮物理拷 18 万件，与 LEDGER_final.md:279-280 的"worktree 占 93.8%"诊断同量级；P-8b（bundle≥2）已生效 [亲验] |
| 6.2 | `ZephyrAlpha-DailyBackup` `ExecutionTimeLimit` 仍 = **PT4H**、`ZephyrAlpha-WeeklyVMBackup` 亦 PT4H；而实测轮时长出现 3.9h / 9.1h / 9.9h 三种 | **P-10 原样在册未动**（属 Owner 门位，本卷不改判据）；9.9h > 4h ⇒"任务实例 4h 处判死、真进程继续跑"的双真象分裂条件仍成立 |
| 6.3 | 四盘 free：**D 18.8G｜E 295.9G｜F 167.6G｜G 1432.2G** | `F:\zephyr_cold\AUDIT_SOP.md:9` 日检判据 F≥700G、D≥50G ⇒ **F、D 两线同时破**；D 从 09-25 案的 45.7G 进一步降到 18.8G。D 是 CH 虚拟机 `data.vhdx` 所在盘，也是 06:00 备份链的源盘 |
| 6.4 | `G:\zephyr_cold\60_mirror\zephyr_cold_main\` 内含 `library`（mtime 2026-09-27 07:52） | F 侧 `library` 虽未登记（案 F-6 / §3.4），但**确被夜镜像覆盖**，问题只在登记面不在副本面（如实记，不夸大） |

### 案 G【实锤·结构性最高危】/MIR 传播删除：被事故证实过的病根只在代码链治了，冷库链原样保留

- 事故与治本记录 [读档 + 亲验码]：`backup_config.yaml:20-24`"v2.1.0 变更（2026-09-14，#B1 删除事故防线）：代码备份从 robocopy /MIR 单镜像改为按日期目录版本化快照——**/MIR 会传播删除：2026-09-14 docs/_working 误删事故实证 /MIR 摧毁最后恢复源**"；`backup.ps1:13-14` 同口径；`a3_safe_construction_checklist.md:14` 通则 1"源目录永远最后删，冷储原件留观 30 天"。
- 同一机制仍在役 [亲验码]：`backup.ps1:874` STAGE 3d 对 **F 冷库 → G 唯一夜镜像**执行 `robocopy /MIR /XJ`；`backup_config.yaml:65-73` 仅此一个目标，无日期目录、无历史可退。
- "源 immutable 所以风险可控"的前提已被盘面削弱 [亲验]：`F:\zephyr_cold` 如今混入**每日可变住民**——`library/`（`scripts/backup/library_ledger_backup.py:53` 每日 03:30 写）、`90_tmp/`（30 天 TTL，现仍存 09-25/26 遗件）、`50_archive\by_project\zephyralpha\archive_manifest.jsonl.prepathfix_20260926.bak`（人工改锚备份件直接躺在归档区）。⇒ **任何一次 F 侧误删（人或上游），当晚即在 G 侧同步成真删除，而 G 是第 3 副本唯一载体。**
- 判据缺口 [亲验]：`AUDIT_SOP.md:19` 周检对镜像只判"顶层 mtime ≤48h"（新鲜度），**没有一条判"镜像相对源少了一批昨天还在的文件"**；09-25 班做过一次人肉结构差分（LEDGER_final.md:227"镜像独有=0、源独有仅 AUDIT_SOP.md"），但那是法证不是常设尺。

---

## 7. 待查项 / 未采信叙述

- **R-1**：CH 业务表 ReplacingMergeTree 版本列覆盖率（需逐表查 DDL，属数据面专班）——本卷未核，Owner 所列"旧行覆盖修正行"**不判真伪**。
- **R-2**：**已定位**——`F:\zephyr_cold\library\` 的写者 = `scripts/backup/library_ledger_backup.py`（`:53` `MIRROR_ROOT = Path("F:/zephyr_cold/library")`；`:8` 不变式"备份=双链落位（G:/backup 主 + F:/zephyr_cold 镜像），滚动保留 30 天且每月 1 日留档不清"），载体 = `ZephyrAlpha_LibraryLedgerBackup` 计划任务（`Get-ScheduledTask` last=2026/9/27 3:30:01 result=0 [亲验]）。⇒ 定性从"无主杂物"改判为"**设计内组件，但未进任何登记册/导航**"。
- **R-3**：offsite 第三块盘是否真离场过——`Get-Volume` 见 H: 但 Size/Free=0 [亲验]；`offsite_monthly_manual.md` 自述"建议采购 ≥2T 专盘"；无任何离场日志 ⇒ 3-2-1 的"1 离场"腿目前**不可证**。（在册裁定#380⑥ 原文："撤销=异地备份 Owner 自办（拔盘存放其他电脑），执行线不建异地机制"，`ruling_registry.yaml:5007` 段内——故本卷只问"可否举证"，不提"建机制"。）
- **R-4**：案 A 发生（09-26 06:00）至今 4 天，`F:\README.md` 与 INFRA-STORE-003 note **均未回填**；LEDGER_final.md 最后一笔心跳是 09-27 05:0x 的第二链日检第 3/14 天（`:704`）[读档]，其中不含 ch_vm 全量重跑的任何记述 ⇒ 该事故目前**不在任何在役账本的观测面内**。
- **R-5**（反向澄清，防本卷被误读）：`01_mining_findings.md` §3 意外发现 2 所记"契约声明 tasks.yaml retention 消费者=空头支票"已在 v1.3.0 随版删除；`裁定#383` 判 `storage_tiering.py` 退役（原文已摘，见 §1.2）——这两条**不属于**本次的不一致清单。

---

## 8. 本卷判定的三个最严重缺口（供 Owner 排优先级）

1. **写者按旧盘符地图动作，真源册按新定案叙述**（案 A/B，处方 P-6 的预言已兑现）：`backup_ch_vm.ps1:50` 是全仓唯一硬编码 `F:\ch_vm_backup` 的写者，周六任务已实际把 599G 灌回 F（free 818→167G，击穿 F≥700G 日检线并推翻 10-05 摘盘预算），而 G 侧唯一全量冻结镜像停在 **2026-08-22**、无任何工具能刷新，`restore.ps1 verify` 仍报 ALL CHECKS PASSED（它验 G、`Do-Vm` 用 F）。AutoCheck"探测失败即强制全量"（fail-open）⇒ 10-03 周六会再撞一次。
2. **冷库第 3 副本靠 /MIR，而源已不再 immutable**（案 G）：2026-09-14"误删摧毁最后恢复源"的同一条机制至今是 F→G 冷储镜像的实现；`F:\zephyr_cold` 里如今每日有可变住民（library / 90_tmp / 人工 .bak），且**没有任何在役尺能判"镜像比源少了一批昨天还在的文件"**。这是对"数据第一公理"最直接的结构性威胁。
3. **账目面无版本列、无唯一键、校验和覆盖 12%、首行被 BOM 静默吞掉，且台账真源两份分叉**（案 D/E/F-7）：2,518 行中 checksum 仅 308 行、35 组键碰撞、`_is_archived` 取首条而 `_manifest_checksum` 取末条、首条记录对所有对账不可见；活写者 `akshare_alt_provider.py:423` 仍在写计划 10-21 删除的 G 侧旧册。后果不是数据丢失，而是**任何"全量核对=绿"的结论都不可信**——这正是"幻觉"痛点的技术本体。
