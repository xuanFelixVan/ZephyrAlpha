---
ttl: task_bound
completes_when: Owner 逐表批文+24h 日志复测+TI 解锁三项等待期结束（本件随战役归档）
session: st-disk-ch-20260921
issue: DISK-CH-CAMPAIGN-A5
---

# a5 终局交付报告 — 磁盘与 CH 线通宵班（2026-09-20 21:40 ～ 2026-09-21 05:30，st-disk-ch-20260921）

> 依据：总包乙执行令 v2.1（分包1-7）+上位真源 unified_campaign v1.0 §4/§6 + a0 总令 + 裁定#380/#381/#382。
> 证据等级标注：[亲验]=本班实测；[转报]=他会话/报告转引；[推断]=分析结论。
> 断点续班：过程全账见 a1_ledger.md；本件=终局对账。

## ⓪ 置顶：《废表呈报清单》（等 Owner 逐表批）

**13 张废表盘点卡已呈报，合计 35.39G，双副本保险先行（F+G Parquet 20.28G，行数核对+全量 sha256 全等）。
批一张删一张，未批一律保留。** 全文=同目录 `waste_table_report_list.md`；机读底档
`waste_table_inventory.yaml`；保险凭证 `waste_table_export_manifest.yaml`（13/13 验证通过 [亲验]）。
4 张 *_bak_1970clean_20260914 按裁定#382 标记治本参照原料，不进呈报、保留至 1970 治本完成。
要点：tick_data_tzbak_20260914 因甲线 p0_tick_backfill 仍作回滚通道引用，建议留观至 tick 批收口；
5 张 etf tz_bak（8.1G）建议 10-18 月度复盘后批删；news 两张旧态表（25.9G）为最大可回收项。

## ① 新增机制：废表登记册+报警（裁定#380①，永不自动删）

- 扫描器 `scripts/ch/waste_table_scanner.py`：名字族正则（_bak_\d+/_tzbak_/corrupt/_pre_tz）扫
  system.tables → 新表登记+报警"待人工盘点"；已证 17 张全命中、正常表零误报（tests 7 passed [亲验]）。
- 登记册 `waste_table_registry.yaml`：17 条在册（13 呈报+4 治本参照），条目只增不删。
- 首跑报警输出留档于 a1 台账 23:54 行。

## ② 分包1 日志滚动（S2，最急项）——DONE（24h 复测=等待项）

| 项 | 修前红证 | 修后绿证 |
|---|---|---|
| text_log level | trace（config.xml:1335）| **information**（重启后 Trace 消失、Information 在记 [亲验]）|
| 系统日志 TTL | 9 表仅 processors_profile_log 有 30d | **8 表 config TTL 全绿**：trace_log/query_log/query_thread_log/query_views_log 7 天；text_log/part_log/metric_log/processors_profile_log/asynchronous_metric_log/error_log/session_log 等其余 14 天（SHOW CREATE 全带 `TTL event_date + toIntervalDay(n)` [亲验]）|
| 日志回积 | 145G 事件后 2.5 天回积 3.97G（~1.6G/天） | 配置断根；**24h 复测 <1G/天=明日 23:05 重跑 survey_ch.py**（等待项）|

- 变更载体：VM `/etc/clickhouse-server/config.d/zz_log_rolling_diskch.xml`（extract-from-config 合并验证绿）；
  主配置已备份 `config.xml.bak_diskch_20260920`。
- 重启合规：声明板闪断窗 23:05-23:30（提前 32 分钟登记），23:05:33 执行、秒级复活，避开 02:30 夜跑带 [亲验]。
- **意外发现（移交甲线 WO-2 A4/A7）**：level=information 后暴露 hyperliquid NaN 与中信期货 TSV
  解析失败的既有灌入重试风暴 ~31 err/min——重启前被 trace 噪音淹没，非本次变更引入。

## ③ 分包3 冷储自动化三档同日试跑（Owner 批文⑤）——DONE 全绿

- **载体**：`scripts/ch/rolling_archive_reconciler.py`（复用 archiver 三阶段唯一通道，零第二套 export/verify/drop）。
- **规则真源**：契约 v1.2.0→v1.3.0（同 commit 裁定#387 原子）：INV-RET-002 修订（五重安全阀+事件触发
  自动+kill 旗回退）+ INV-RET-006 + §5B rolling_archive 参数块（滞回 1 月/批 ≤3 分区 ≤30G/熔断 3 连败/
  TI 排除表——甲线互斥回落前不自动搬/14 表保留线机读化）。
- **触发**：backup.ps1 STAGE 4b 备份成功事件钩子（零新增 schtasks；禁 cron 红线合规）。
- **三档实弹**（[亲验]）：
  - shadow：过线分区清单 **926 个**（完整月数字分区口径；etf 分钟族 2005 微分区打头），计划单落盘；
  - semi：3 分区"待确认"流验证（无 --confirm 不动）；
  - full_auto：**两轮实弹共 6 分区**（kline_etf_15min 200502..200507，64/368/336 行级微分区）
    export→verify→F 主库+G 镜像双副本→DROP→manifest 全链成功，逐分区留痕。
- **红蓝三注入**（[亲验]）：伪造备份失败→整批 SKIP✓；伪造对账不符×3→连续失败熔断✓→后续拒动✓；
  kill 旗→整批跳过✓→--resume 复位✓。单测 7 项（含注入与限量）全绿。

## ④ 分包4 冷储主库落 F（S3）——DONE

- **搬运**：E:\zephyr_cold_archive → F:\zephyr_cold\50_archive\by_project\zephyralpha，robocopy
  /E /COPY:DAT /MT:16，8 分钟 263MB/s（Git Bash 吃 `/E` 参数坑以 MSYS_NO_PATHCONV 治 [亲验]）。
- **对账**：文件数 2211=2211；字节 126,247,590,599 两侧全等；5% 哈希抽检 110 件零失败——**verdict PASS** [亲验]。
- **引用 7+1 处同 commit 改齐**：archiver.py:69/732、asset_inventory.yaml、infrastructure_registry.yaml
  （INFRA-STORE-002 口径同步 v1.3.0）、registry_of_logs.yaml、services_registry.py、backup_config.yaml、
  known_data_gaps.yaml、data_retention_contract.yaml（INV-RET-002/003+storage_matrix E 盘措辞）。
  残留扫描唯一命中=裁定注册表内**历史裁定原文**（文档性例外，禁改写）。
- **探针绿**：archiver 新家 ARCHIVE_ROOT=F 新路径，manifest 2210→2213 条全可读，stats() 正常 [亲验]。
- **E 侧留观 30 天**：E:\zephyr_cold_archive 原样封存，**2026-10-20 到期删**（等待项）。

## ⑤ 分包5 F↔G 兜底镜像+备份链增强（S4）——DONE

- **身份前置**：/mnt/chbackup_local 物理身份三分量核实=VM 第三 SCSI 盘挂 F:\ch_backup_disk.vhdx（526G，
  Get-VMHardDiskDrive 实测 [亲验]）→ 禁动解除。该 vhdx 因 VM 独占挂载锁定不可文件级镜像，其内容
  （CH 备份本体）已由 ch_vm_backup 镜像间接覆盖——记录为例外 [亲验]。
- **G 镜像五目标全 ok**（backup.ps1 STAGE 3d 生产实跑 [亲验]）：ch_vm_backup 592G（含 data.vhdx
  635,189,592,064 字节两侧全等）/offrepo 137G/zephyr_cold 137G/db_dumps 370M/git_bundles 815M，
  合计 ≈866G 落 G:\zephyr_backup_mirror；count+bytes 全对+15 件哈希抽检（终对账脚本见
  `.runtime/tmp/diskch/gmirror_verify.py`）。
- **备份链三增强**（本 commit）：
  1. **db_dumps 版本化 14 天滚动**（批文⑦）：/MIR 覆盖式→日期化快照目录+rotation（config
     `db_dumps.retention_days: 14`），**rotation 闸=CH 备份 ok**（删除最旧快照前确认数据本体在库——
     兑现 Owner 数据公理）；旧 /MIR 散件冻结为额外保险。
  2. **STAGE 3d G 盘兜底镜像**（g_mirror 五目标，/MIR /XJ，Mode=ch 跳过）。
  3. **STAGE 4b** 备份成功钩子：滚动归档 full_auto 评估+vhdx 季度预检（见⑦）。
- **实跑验证**：backup.ps1 全链实弹一轮（00:43-05:15）：CH 增量备份 ok（ratio 0.24<0.5 重刷线）、
  五阶段全过、STAGE 3d/4b 生产首飞成功。
- **病灶根治**：backup_state.json 停更病（09-16 failed 假象 vs 09-20 21:04 报告实为 ok）根因=
  PS5.1 `Get-Content` 无 `-Encoding UTF8` 对无 BOM UTF-8 按 ANSI 读→ConvertFrom-Json 炸→状态永不
  更新（报告写了状态没写）。本班实证+双修复：state 文件 ASCII-only 纪律+backup.ps1 两处读点补
  `-Encoding UTF8`（跨语言回读实测 ok/ok [亲验]）。**已知移交**：PG dump exit 1（backup 链老病，
  globals/sqlite 正常，不属本线，建议归备份维护批）。

## ⑥ 分包6 宿主清偿（S5）——DONE（D 盘验收达标）

| 项 | 前 | 后 |
|---|---|---|
| D 盘剩余 | **28G（97% 满，全战役硬闸）** | **61G ≥60G 验收达标** [亲验] |
| .runtime/tmp | 43G（568 项已收口战役临时产物） | 机械分类清理 35.15G（>24h+非活跃会话；两轮 chmod；pc_cache 1 项系统锁跳过登记）|
| models/ 15G | qwen25-7b 两目录 | **有引用**（ml_train/run_sft_train 等 4 脚本+测试）→按 a0 W5"有引用登记处理"保留 D 盘，待 ml 线改路径批 |
| db_dumps | /MIR 单份 | 版本化 14 天滚动（见⑤）|

- 研报 E 侧删除：对账已核（2019_bundle 29,998=29,998 [转报 dataqa]），**执行日 ≥2026-10-18**（等待项）。
- D:\nonexistent 8KB 旧实验残件：体量微小，登记遗留不清（禁为 8KB 冒三层验证外风险）。

## ⑦ 分包7 vhdx 排班化（批文④唯一点名项）——DONE（不压缩不停机）

- 排班条目：`--precheck` 模式挂 backup.ps1 STAGE 4b（备份成功事件链）——季初首 7 天或距上次压缩
  ≥90 天触发预检单生成；**提醒条目绝不自动执行**（裁定#380④/#381 唯一点名边界）。
- 首张预检单：`vhdx_precheck_20260920.md`（VM 内部空闲 154.7G 绿/vhdx 599G/距上次压缩从未/备份新鲜绿）。
- 通知机制设计稿：`vhdx_quarterly_notice_design.md`（晨报一行+仪表盘横幅接口约定，不弹窗；
  含 Owner 点名后的全局冻结档执行剧本）。
- **实际压缩：等 Owner 点名**（等待项）。

## ⑧ 红蓝对抗与恢复演练（WO-11）

| 演练 | 结果 |
|---|---|
| 搬运复对账① E→F 冷库 | 2211 文件/字节全等/110 件哈希抽检零失败 PASS [亲验] |
| 搬运复对账② 废表 F↔G 双副本 | 13/13 sha256 全等；auction_book 抽件 F/G/manifest 三方一致 PASS [亲验] |
| 搬运复对账③ F→G 兜底镜像 | 五目标 count+bytes 全对+15 件抽哈希 PASS（gmirror_verify.py）|
| 恢复演练① archiver restore | kline_etf_15min 200502 从 F 冷库恢复 64/64 行（checksum 守卫路径）→复 drop 净值零 PASS [亲验] |
| 恢复演练② G 侧可用性 | 原计划"G vhdx 分区恢复"需挂载 592G 虚拟盘=通宵窗高危，**降级执行**：ch_vm_backup 文件级全等+db_dumps/git_bundles 哈希复验+dump 可读性——降级理由记录在案 |
| 冷储自动化失败注入 | 备份失败拒动/对账不符三败熔断/kill 旗回退 三项全绿 [亲验] |

## ⑨ 五盘对照表（终态）

| 盘 | 班前 | 班后 | 变化 |
|---|---|---|---|
| C（NVMe 系统） | 61G free | 61G free | 未动 |
| D（NVMe 项目+VM） | **28G free（97%）** | **61G free** | **+33G（.runtime 清偿）≥60G 达标** |
| E（SSDC 热） | 134G free | ~252G free | +117.6G（冷库迁出，留观 30 天后原目录删）|
| F（USB SSD 冷储主库） | 557G free | ~280G free | -277G（承接 E 冷库 118G+废表双副本 20G+zephyr_cold 主库，+G 镜像读压力为瞬时）|
| G（USB HDD 兜底） | 3.6T free | 2.7T free | -0.9T（兜底镜像五目标 866G 落位）3-2-1 的 G 侧成立 |

- CH 内部：VM default 盘 155G 空闲（班前 155G；日志 TTL 断根+6 微分区归档；34.9G 尸体表待 Owner
  逐表批后释放——释放 VM 内部空间，D 侧真实回收靠 vhdx 压缩=Owner 点名项）。

## ⑩ 提交与队列账

- 落地提交：q-0009（18→19 文件主批：裁定#383/#387+契约 v1.3.0+两新模块+archiver 修复+引用改齐+
  备份链增强+翻译+token+depgraph 节点+ALGO_FLOW 补锚）；q-0010（本件+战役文档全家福）。
- 死信学费（全数闭环）：q-0001 ANY-2 裸 Any→修；q-0002 UP037 注解引号→修；q-0003/0005 锁外预检被
  外来 staged 连坐→skip-preflight（序列器 own-scope 真门禁兜底）+claim TTL 30 分钟过期→落地前重 claim；
  q-0006 NEW-FILE-DEPGRAPH→apply_depgraph 两节点；q-0007 SSOT PROJECT_ROOT 重定义→canonical 导入；
  q-0008 循环复杂度 25→拆分 _plan_batch/_execute_partition。
- 心跳教训（入配方册）：idle-timeout daemon 30 分钟自杀（last_activity 仅 register/claim 刷新）→
  长盘操作班需 session keeper（.runtime/tmp/diskch/session_keeper.py，12h 自限）。

## ⑪ 等待项清单（不算失败，全部有据）

| # | 项 | 等什么 | 到期/触发 |
|---|---|---|---|
| 1 | **废表逐表批**（13 张 35.39G，呈报清单置顶） | Owner 逐表批 | 随时（批一张删一张）|
| 2 | 日志 24h 膨胀复测 <1G/天 | 时钟 | 2026-09-21 23:05 重跑 survey_ch.py |
| 3 | E 冷库留观期删除 | 时钟 | 2026-10-20 |
| 4 | 研报 E 侧删除 | 时钟 | ≥2026-10-18 |
| 5 | vhdx 实际压缩 | Owner 点名 | 预检单已备 |
| 6 | TI 自动归档解锁 | 甲线 C-5/批10 健康回落公告 | 甲线通知 |
| 7 | models/ 15G 迁移 | ml 线路径批 | 登记在案 |
| 8 | tick_data_tzbak_20260914 删 | 甲线 tick 补批收口 | 甲线通知 |
| 9 | PG dump exit 1 | 备份维护批（非本线） | 移交 |

## ⑫ 未达成项（如实申报）

- 无整包未达成。轻微降级两处（均已记录）：恢复演练② 降级为文件级验证（挂载 592G vhdx 通宵高危）；
  pc_cache 1 目录因系统锁跳过（8KB 级）。日志 24h 复测因班次时长物理所限列为等待项（探针已备）。

—— 乙线总包 st-disk-ch-20260921 敬呈
