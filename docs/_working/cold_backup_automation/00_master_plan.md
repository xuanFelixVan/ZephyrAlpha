---
ttl: task_bound
---

# 00 备份系统全套自动化 + 冷储全套自动化 总体方案

> 定位：Owner 直属方案。覆盖六项需求（身份证/滚动归档/冷储入库/镜像自动化/数据安全/vhdx 冗余）+ 三条追加裁定（150G 定案/季度压缩/保留与清除总清单）。
> 底料：同目录 01_mining_findings.md（缺口表/数据资产清单/外部实践对照/引用链接）。
> 纪律：本方案只是文档，未动任何数据/代码/注册表；全部施工在 st-final3 战役收口后按 §10 批次执行。
> 数字口径：盘位与库内体量=2026-09-19 Owner 实测；文件行号=2026-09-20 只读核实。

## 1. 现状账（家底、窟窿、命根子）

### 1.1 盘位与角色（Owner 已拍板）

| 盘 | 介质与容量 | 角色 | 关键数字 |
|----|-----------|------|---------|
| C | NVMe 系统盘 | 系统 | —— |
| D | NVMe 731G | 项目盘 + HyperV CH 虚拟机（data.vhdx 599G，动态盘） | vhdx 599G |
| E | SATA SSD 931G | 软件 + 热数据 | 读 475/写 437 MB/s |
| F | SanDisk 2T USB（实为 SSD） | **冷储主库 + working_vault 代码版本库** | 读 374/写 340 MB/s |
| G | 东芝 4T USB 机械盘 | **备份兜底盘 + 冷储镜像** | 写 70 MB/s，小文件 11.5 files/s |

### 1.2 库内构成（CH 26.6.1 VM）

曾 631.9G 仅剩 6.6G；2026-09-19 晚 TRUNCATE 系统日志释放约 145G，清后内部剩余约 150G。活跃 566.5G 分解：

| 块 | 体量 | 说明 |
|----|------|------|
| 系统日志 | 145G（已清） | trace 级全量记录所致，待原生 TTL 治本（§8/§9） |
| 修复尸体表 | 35.4G | news_corrupt/pre_tz2/各 tz_bak，待裁定处置（批 6） |
| 契约欠账 | 24.9G | TI 窗口外 19.4G + 冷线 5.5G（批 3 清账） |
| 合规热层 | 约 361G | tick_data 141.5G（2025-01 起 21 个月，约 6.7G/月唯一增长源）+ technical_indicator 窗口内 151G + 分钟线约 66G + 日K/基本面/事件/元数据（小） |

Tick 过 2 年线后（2027 起）热层稳态约 350-400G，**有界**——这是全方案"自动化不失控"的几何基础。

### 1.3 已有自动化（能跑，别重建）

| 机制 | 触发 | 保留/轮转 | 落点 |
|------|------|----------|------|
| backup.ps1 六阶段备份 | 每日 06:00 计划任务兜底 + post-commit backup_reconciler（重要文件+8h 间隔） | —— | —— |
| working_vault 代码快照 | 同上（STAGE 3） | 14 天轮转+硬链接去重+F 盘剩余 <60G 自动逐出（最少保 3 天） | F:\working_vault |
| git bundle 全史 | 同上（STAGE 3b，≥7 天重建） | 留最新 2 份 | F:\working_vault\git_bundles |
| db_dumps | 同上（STAGE 2） | /MIR 覆盖式（仅 1 份，缺口） | F:\db_dumps |
| CH 增量备份 | 同上（STAGE 2 内） | base+inc，inc≥50%×base 自动重建基线 | CH VM 内 |
| offrepo 镜像 | 同上（STAGE 3c） | /MIR 随源滚动 | F:\offrepo_backup（含 E 冷库镜像） |
| 冷库归档 | **手动 CLI**（INV-RET-002） | manifest append-only 永久 | E:\zephyr_cold_archive（117.6G，1865+ 分区零事故） |

非库内资产：研报 90,243 件已迁 G:\zephyr_cold\30_corpus\research_reports（F 60,245 + E 29,998，零失败）。

### 1.4 核心窟窿

①归档唯一通道 archiver.py 只能手动触发（契约铁律）；②数据身份证载体存在（business_data_categories.yaml 的 lifecycle 字段）但 206/209 条都是 permanent，与契约 10 层脱节；③CH 系统日志靠事后 TRUNCATE 救火，无原生 TTL；④F→G 冷储镜像、offsite 副本、restore 演练不存在；⑤db_dumps 无版本化；⑥盘位水位无人巡检。逐条证据见 01 文档缺口表。

## 2. 核心冲突与裁决路径（头号议题）

契约 `data_retention_contract.yaml` 铁律 INV-RET-002 明文"进 Cold 层必须手动触发，不自动迁移"（v1.0.0，2026-07-14 Owner 裁定）；INFRA-STORE-002 的 access_method 写死"手动触发，禁接 scheduler"；registry_of_logs.yaml LOG-OPS-001 挂同口径。宪法 §9.11 规定 Owner 意向须经裁定登记/正式通道生效，对话口头指令不构成门禁豁免——**Owner 现要求自动化，唯一合法路径 = 修订契约 + ruling_registry 新裁定同 commit 原子（RULE-RULING）**，同 commit 修订 INFRA-STORE-002 与 LOG-OPS-001 两处派生表述（消除文档矛盾，宪法 §4.3）。

两个选项：

- **选项 A（推荐终态）：全自动**。INV-RET-002 修订为："进 Cold 层默认手动；启用滚动归档 reconciler 后，**同时满足五重安全阀**（§5.3）的过线分区允许事件触发自动归档；kill switch 一键回退手动模式"。附滞回条款（归档线=保留期+1 个月，防边界抖动）与批限量条款（≤3 分区且 ≤30G/次）。
- **选项 B（过渡态）：半自动**。守护者每日生成归档计划单（dry-run 清单：表/分区/行数/预计体积/安全阀逐项状态），Owner 一键批执行 archiver。

**推荐：三步走，A 为终态、B 为必经过渡**——shadow（只 export+verify 不 drop，人工核对首月清单）→ 半自动 B → 全自动 A。理由：①安全阀序列已把"先备份先验证再动手"固化为机器流程，全自动的边际风险低于人工遗忘风险；②半自动每天要点一次，长期必然退化为摆设（人的可靠性劣于机器熔断器）；③150G 冗余提供约 22 个月失灵缓冲（§8.1），熔断+kill switch 保证任何时刻可回手动。

宪法红线遵从声明：reconciler 挂**备份成功事件链**（每日 06:00 备份 ok 之后才评估归档——备份成功本身就是安全事件，backup_daily_trigger.ps1 已确立该事件流的合法地位），不新增任何 schtasks/Timer/sleep-loop。

契约修订草案要点（批 0 落地时的 diff 骨架，供裁定文书引用）：

```
INV-RET-002 修订前: 进 Cold 层必须手动触发——不自动迁移
INV-RET-002 修订后: 进 Cold 层默认手动触发。启用滚动归档 reconciler 后，同时满足五重
  安全阀（备份新鲜/export/verify/第二副本/批限量）的过线完整月分区允许事件触发自动
  归档；归档线=保留期+1 个月滞回；单批 ≤3 分区且 ≤30G；连续 3 分区失败熔断；kill
  switch 一键回退手动。业务数据"永不删除"铁律（INV-RET-001）不变，自动迁移仍走
  archiver.py 三阶段唯一通道。
新增 INV-RET-006: 滚动归档的触发、限量、滞回、熔断参数属规则数据，真源=本契约，
  reconciler 启动时加载，禁止码内第二真源。
changelog v1.3.0: 上述修订 + 删除"tasks.yaml retention 字段"消费者声明（改挂品类
  真源 business_data_categories.lifecycle，见身份证章节）+ ruling_registry 裁定号回填。
```

## 3. 目标架构（文字版全景图）

```
【入库】 新数据经 scheduler/灌入链 → 落 CH（c1/c3）
           └─ 入库即领身份证：business_data_categories.lifecycle（对齐契约 10 层）
              新表登记义务：无身份证 → gate 拦截；无类别默认 permanent+告警（宁可不滚、不可误滚）
【热层】 CH 只存窗口内数据（tick 2 年/分钟 5 年/日K 10 年/TI 滑窗 3月~5 年）
           └─ 每月新分区进、最老分区出，热层稳态 350-400G 有界
【滚动】 每日 06:00 备份成功（事件）→ ROLLING-ARCHIVE-RECONCILER
           └─ 找出过线月分区（≤今天-25 个月，滞回 1 月）→ 批限量（≤3 分区且 ≤30G）
              → 五重安全阀 → export→verify→第二副本→drop → 失败即熔断
【冷储】 F:\zephyr_cold_archive（主库：Parquet 按库/表/分区，manifest append-only）
           └─ G:\zephyr_cold（抽屉制：00_manifest/10_inbox/20_raw/30_corpus/50_archive/90_tmp）
              新资料走 inbox 事件化入库（§6）；F 冷库每夜镜像到 G（§7.2）
【镜像】 backup.ps1 六阶段（现状保留）+ 新增 STAGE 3d：F 冷库→G 镜像
【兜底】 git bundle（F）+ db_dumps（F，待版本化）+ G 兜底镜像 + 季度 restore 演练（§7.3）
【冗余】 VM 内部空闲 ≥150G 红线 + 季度压缩巡检（预检单半自动，§8.3）
```

一句话：**数据生下来领身份证，住在热层有期限，到期自动搬去冷库（先抄两份再搬），冷库每晚照镜子到 G 盘，所有家当每天早上 6 点自动备份一遍，人只在每季度按一次压缩扳机、处置告警清单。**

## 4. 数据身份证机制设计（需求 1）

**载体裁定：不新建文件，启用现有字段。** `docs/03_modules/_cross_layer/database/business_data_categories.yaml` 是表名/品类唯一真源（裁定 #ARCH-CH-024，114 条品类），每条已有 `lifecycle` 字段——这就是身份证的卡槽，只是从未按契约填过。施工四步：

1. **字段对齐**：lifecycle 枚举扩为 `permanent / hot_Nd / retain_2y / retain_5y / retain_10y / derived_slide`（向后兼容旧值），值域真源=契约 layers 表；technical_indicator 等派生表挂 §2A 滑窗规则（1min 3 月/5min 1 年/15min 3 年/30min 5 年/60·120min 跟源/日周月永久）。
2. **入库打证**：table_registry 启动加载 lifecycle 映射并暴露 `lifecycle(table)` API；scheduler/新表登记校验"表必有身份证"（gate：新增品类缺 lifecycle → block；<1GiB 小研究表按 INV-RET-005 永久热层，爆量后按年龄线重估——契约已有此条款）。契约头部"tasks.yaml retention 字段"的空头支票就此删除（01 文档发现 2），消费者改挂品类真源，不两处维护。
3. **无类别默认策略**：未登记 lifecycle 的表默认 `permanent`（宁可不滚、不可误滚）+ 每周告警清单催登记；告警进飞书（复用 alerter 链路）。
4. **身份证→滚动联动**：滚动 reconciler 只认身份证取归档线；身份证缺失或 permanent 的表 reconciler 自动跳过并计入"跳过清单"（可审计，防漏防误两头堵）。

验收：114 条品类全有身份证且与契约 10 层机查零矛盾；gate 对新表生效（演练一次拦截）。

## 5. 滚动归档 reconciler 设计（需求 2 + §2 冲突裁决落地）

### 5.1 触发与载体

- 载体：`ReconciliationRegistry.register(ReconcilerSpec(gate_id="ROLLING-ARCHIVE-RECONCILER", trigger, reconcile, priority, file_ops))`，与 backup_reconciler 同模式（事件触发、异常降级 warn 不阻断、状态持久化）。
- 触发事件：每日 06:00 备份成功（`backup_state.json` 的 last_backup_status=ok **且** last_ch_backup_status=ok）→ 才评估归档。备份失败或 CH 备份失败的日子**整日不归档**——备份新鲜是归档的第一道安全阀，不是可选项。

### 5.2 归档线与滞回（防抖）

- 归档线 = 完整月分区且 `partition_end < 今天 - (保留期 + 1 个月)`。tick 保留 2 年 → 实际 25 个月才动；分钟线 5 年 → 61 个月才动；TI 滑窗同理各加 1 月。滞回吸收迟到数据、月末分区未满、日历抖动，杜绝"刚过线就动、回退又拉回"的振荡。
- 复用 archiver.py 现成函数（archive_partition/archive_range 可 import），不写第二套 export/verify/drop——唯一通道原则（契约 §2A 原则 3）；FINAL 注入、行数容差、抽样比对全部白得。

### 5.3 安全阀五重检查（顺序不可换，缺一即跳过本批）

| 序 | 阀 | 通过条件 | 失败动作 |
|----|----|---------|---------|
| 1 | 备份新鲜 | 当日备份 ok 且 CH 阶段 ok | 整批跳过，次日再评 |
| 2 | export | 分区导出 Parquet 到 F 冷库主库 | 删除残件，该分区待重试 |
| 3 | verify | 行数比对（>100 万行 ±1 容差）+ 抽样 100 行字段值比对 | 删除不可信 Parquet，待重试 |
| 4 | 第二副本 | 该 Parquet 落 G 镜像并核验（robocopy /L 或 sha256 抽检）——**drop 前必须两份验证副本** | 不 drop，待镜像夜批补齐 |
| 5 | 批限量 | 单次 ≤3 个分区且 ≤30G（tick 月分区约 6.7G/个，一批约 20G；G 盘 70MB/s 写约 5 分钟） | 余量留到下一事件 |

全过 → `ALTER TABLE DROP PARTITION` → manifest append-only 记录（rows/checksum_md5/compress_ratio）。

### 5.4 状态机与熔断

```
idle → (备份ok事件) → 筛选过线分区 → 逐分区 [export → verify → replicate → drop] → idle
                │                        └─ 任一步失败：该分区记 retry_queue
                └─ 连续 3 个分区失败 → circuit_open（状态文件+飞书告警+停止自动）
                                      人工排查复位 → 回 idle
```

kill switch：复用 `zephyr.security.access_control.kill_switch` 登记 flag（如 `rolling_archive_disabled`），置位即全体跳过回手动模式；kill switch 状态纳入每周巡检。

### 5.5 三步走

- **第一步 shadow（1 个月）**：只 export+verify+生成计划单，不 drop。计划单字段：table/partition/rows/ch_size/parquet_size/safety_valve_status。人工核对与实测体积后进入下一步。
- **第二步半自动（选项 B）**：每日计划单 + `archiver archive-range` 一键批执行——本质是把安全阀跑给人看一个月。
- **第三步全自动（选项 A）**：reconciler 接管 + 熔断 + kill switch。

### 5.6 参数汇总表（reconciler 配置唯一真源=契约 v1.3.0，此处为方案口径）

| 参数 | 值 | 说明 |
|------|-----|------|
| 触发事件 | 每日备份 ok（含 CH 阶段） | 非 ok 整日不归档 |
| 归档线滞回 | 保留期 + 1 个月 | tick 实际 25 个月/分钟线 61 个月 |
| 批限量 | ≤3 分区且 ≤30G/次 | 一批约 5 分钟 G 盘写入 |
| 熔断阈值 | 连续 3 分区失败 | 状态文件+飞书告警+人工复位 |
| shadow 期 | 1 个月 | 只 export+verify+计划单 |
| kill switch | flag `rolling_archive_disabled` | 复用 access_control.kill_switch |
| 跳过清单 | permanent/无身份证表自动跳过 | 可审计，每周告警催登记 |

### 5.7 失灵兜底算术

滚动链路完全停摆也不触顶：150G 冗余 ÷ tick 6.7G/月 ≈ 22 个月缓冲；期间归档欠账指标（应归未归 GB 数）每日可见，玩不丢。

## 6. 冷储入库自动化设计（需求 3）

G 盘 SOP 四步（落箱→登记→归位→清箱）事件化，三红线固化为代码检查：

1. **落箱事件化**：采集/下载任务完成 hook 自动落 `10_inbox\YYYYMMDD_来源_说明\`（命名 SOP §3 强制：全小写 snake_case，禁中文空格）。
2. **登记自动化**：inbox 巡检随每日备份成功事件（同 §5.1 载体，GATE-COLD-INBOX）扫描未登记目录 → 自动写 `00_manifest\drawers.jsonl`（>10GB 强制 sha256，SOP §2）→ 无 skeleton_ref 的挂告警清单回 01 骨架图补中类（SOP 铁律：先补图再建抽屉）。
3. **归位自动化**：按登记 drawer 入 20_raw/30_corpus/50_archive，immutable 只写一次；清箱移除。
4. **红线拦截**：reconciler 内置三红线——发现"已清洗回测数据"（c1/c3 表数据）申请入冷储直接拒绝并告警（回测数据的家在 CH+数据盘，SOP 第一公理）；CH 归档 Parquet 走 §5 通道自带 manifest 登记，本身就是 CH 侧的冷储入库自动化；禁止从冷库反向更新 CH。
5. **巡检半自动**：90_tmp 30 天 TTL 到期清单 + manifest 与实际目录月度对账（多目录少登记=事故，SOP §7）+ 整盘剩余 <10% 报备——三项进每日巡检脚本。

## 7. 备份链 3-2-1 与 F→G 镜像自动化（需求 4）

### 7.1 现状到 3-2-1-1-0 的映射

| 维度 | 现状 | 动作 |
|------|------|------|
| 3 副本 | CH 热层（D 内 vhdx）+ 冷库 Parquet（E，批 1 后=F）+ F offrepo 镜像 | 批 1 后=D 热 + F 冷主 + G 镜像，成立 |
| 2 介质 | NVMe / SATA SSD / USB SSD / USB HDD | 天然满足（4 种） |
| 1 offsite | 无 | Owner 拍板（§12.4）：月度轮换盘或云归档小体量优先 |
| 1 immutable/offline | G 20 区 immutable 先例；git bundle 留 2 份 | 月度拔盘轮换 G（离线副本，防勒索/误删最后一手），挂季度巡检提醒 |
| 0 错误 | 有产物检查，无恢复演练 | 季度演练自动化：随机抽 2 个已归档分区 `archiver restore` 到临时库，行数+checksum 比对（restore 自带 checksum 守卫），报告落档 |

### 7.2 F→G 镜像（新增 STAGE 3d）

- backup.ps1 新增 STAGE 3d，机制复用 offrepo：`robocopy F:\zephyr_cold_archive → G:\zephyr_cold\60_mirror\zephyr_cold_archive /MIR /XJ`。配置即在 backup_config.yaml 的 offrepo_backup.targets 增加一条：

```yaml
    - id: cold_archive_mirror
      source: "F:\\zephyr_cold_archive"
```

  （原 `cold_archive` 条目的 source 从 E 盘改 F 盘，批 1 同 commit。）冷库 Parquet 大文件少，G 盘小文件 11.5 files/s 瓶颈不触发；117.6G 全量约 28 分钟，增量夜备分钟级。
- **不镜像 working_vault 到 G**：海量小文件 × 11.5 files/s 拖垮窗口，且跨卷复制丢失硬链接去重（14 天版本×全量体积爆炸）；git 历史已有 bundle 单文件兜底，把 git_bundles 目录纳入 3d 即可。
- G 盘同时承担研报主库（60,245 件）+ 冷库镜像，4T 容量充裕；SOP §7 水位红线（剩余 <10% 报备）纳入巡检。

### 7.3 db_dumps 版本化缺口

backup.ps1:590 现为 /MIR 覆盖式（"unchanged /MIR, overwrite by design"）——dump 时刻坏了无前份可退。建议日期化目录 + 保留 14 天轮转（与 working_vault 同参数，复用其轮转/空间保险逻辑）。保留天数需 Owner 拍板（§12.5）。

## 8. vhdx 冗余测算与压缩节奏（需求 6 + 追加裁定 1）

### 8.1 冗余定案：150G（Owner 追加裁定"按大的来算"）

内部空闲按 **150G** 留（实测清后剩余约 150G；不采纳 100G 激进档）。依据三条：

1. **增长缓冲**：tick 约 6.7G/月是唯一增长大头，150G ÷ 6.7 ≈ **22 个月**纯增长缓冲——就算滚动归档链路彻底停摆一年半也不会写满库；
2. **稳态几何**：滚动运行后热层稳态 350-400G + 系统日志滚动 ≤10G + 临时余量约 20G + 冗余 150G ≈ **530-580G**，落在现有 vhdx 599G 之内——**无需扩容 vhdx**，也不会反复膨胀（增长有界）；
3. **停机成本**：压缩需停机，冗余越足压缩频率越低；150G 档位支撑"季度一次"节奏（8.2）。

### 8.2 压缩节奏：季度例行 + 触发式加演

VHDX 动态盘只增不缩：guest 内 TRUNCATE/归档释放的空间，宿主 D 盘拿不回来，压缩（Optimize-VHD）把 vhdx 文件缩回实际用量。本次清账实例：若现在压缩，宿主 D 盘理论可回收最多约 150G（vhdx 从 599G 回落到 450-470G 量级）。

- **节奏**：每季度首个周六例行一次；触发式加演条件（任一）：①内部空闲 <150G 红线；②大批量释放落地后（尸体表 35.4G + 欠账 24.9G 清账后合计约 60G 垃圾空洞，值得马上压一次）；③距上次成功压缩 ≥90 天。
- **预计停机**：60-120 分钟（599G vhdx 在 D 盘 NVMe 上 compact，耗时与垃圾量成正比）。

### 8.3 半自动流程：自动预检单 + 一键执行 + 收尾自动验证

- **预检单自动生成**（只读，随每日备份成功事件检查）：内部空闲实测 / 垃圾量估算（CH 空闲 + guest 文件系统差额）/ 最近备份新鲜度 / 归档欠账 / 距上次压缩天数——五项全绿才生成"可压缩"预检单呈 Owner。
- **一键执行**：Owner 批准预检单 → 脚本按序：停 VM → Optimize-VHD → 开 VM → 收尾自动验证（CH 恢复服务、ch_parts_monitor 无告警、关键表行数抽检、当日备份补跑 ok）。
- **为什么这一步保留人工扳机（诚实版）**：压缩必须停机=CH 停写，这是全方案唯一"数据面不可写"的操作；无人值守时若压缩中途卡死/宿主断电，没有人在场止损，且停机窗撞上交易时段=资金链路中断——属宪法 §5 high 域（production 流转/资金破坏性操作）门位，本就不该全自动。除此之外，全链路无人值守。
- **合窗**：系统日志 TTL config 需重启 CH 生效（§9 第 1 行），与季度压缩同一停机窗一次做完（批 2+批 7 同窗）。

### 8.4 压缩复决讨论（回应"是否恢复 vhdx 压缩"）

Owner 曾否决压缩，理由"怕占未来空间"——彼时担忧：压缩后 vhdx 变小，后续增长又要把 vhdx 重新长大，反复扩缩。该担忧在滚动归档建立后自然消解：热层稳态 350-400G 有界（tick 过 2 年线就搬走），vhdx 最多长到约 530-580G 封顶，**不存在无限增长反复压缩的循环**。不压缩的量化代价：宿主 D 盘常驻约 150G"guest 已释放但宿主未回收"的空洞——D 盘 731G 上项目+vhdx 本就拥挤，150G 不是小数。**结论建议：恢复压缩**，季度节奏+触发式加演，半自动扳机（8.3），与滚动归档互为前提（滚动给压缩供给垃圾、压缩给滚动腾宿主空间）。

## 9. 保留与清除总清单（追加裁定 2，大白话版）

> 读法：每行回答四个问题——这东西现在多大？留多久？怎么没的？机器自动还是得人管？注意：对业务数据，"清除"永远等于"搬去冷储"——项目铁律是数据永不删除，删除的只是热库里的"原件"。

| # | 对象 | 现状体量 | 保留多久 | 清除机制 | 自动化实现 | 需重启/裁定 |
|---|------|---------|---------|---------|-----------|------------|
| 1 | CH 系统日志 9 表（text_log/query_log/trace_log/part_log/metric_log/processors_profile_log/asynchronous_metric_log/error_log/background_schedule_pool_log） | 曾合计约 145G（2026-09-19 已 TRUNCATE 清一次，现从零起步） | 分级：trace_log 7 天（最肥）；query_thread_log/text_log/processors_profile_log/background_schedule_pool_log 14 天；query_log/part_log/metric_log/asynchronous_metric_log 30 天；error_log 90 天（体量小、排障价值高） | CH 原生 config `<ttl>event_date + INTERVAL N DAY</ttl>`，CH 后台按天自滚自清，无需人管 | 写进 config 即全自动 | **需 VM 重启生效**（并入季度压缩停机窗）；思路已获 Owner 认可 |
| 2 | text_log 噪音源 | level=trace 全量记录是 145G 大头 | —— | level 调 information，源头减量 1-2 个量级（真排障临时调回 trace） | 同一 config 同次重启 | 同上 |
| 3 | 尸体表/_bak 表（news_corrupt/pre_tz2/tz_bak） | 35.4G | 处置后清零；今后临时/备份表命名强制带日期后缀 `_bak_yyyymmdd`，超 30 天自动告警 | 事件触发 reconciler 扫 system.tables 匹配 `_bak_\d{8}`/`_corrupt`/`_tz2` → 生成处置清单 → Owner 批准后 export→verify→drop（与业务数据同一安全通道） | 清单自动、执行一键（半自动） | **需 Owner 裁定**（批 6） |
| 4 | 业务热层 L1 tick_data | 141.5G（21 个月） | 热层 2 年（+1 月滞回=25 个月） | 过线月分区搬冷储（export→verify→双副本→drop），数据永不删除 | 批 5 reconciler（shadow→全自动） | **需契约裁定**（§12.1） |
| 5 | 业务热层 L2 分钟线 | 约 66G | 热层 5 年（+1 月滞回） | 同上 | 同上 | 同上 |
| 6 | L3 日K/L4 资金面/L6 新闻 | 均小或未到线（2010 起未满 10/5 年线；L6 pre-2010 已归档） | 10 年/5 年/10 年 | 未到线不动；到线后同上 | 身份证标注，reconciler 自动管理 | 无 |
| 7 | L5 基本面/L7 产业链/L9 宏观/L10 元数据及全部 <1GiB 小表 | 小 | 永久热层（INV-RET-005：省不了几 G，毁了即查研究） | 不清除 | 身份证标 permanent，reconciler 自动跳过 | 无 |
| 8 | 派生表 technical_indicator | 窗口内 151G | 滑窗：1min 3 月/5min 1 年/15min 3 年/30min 5 年/60·120min 跟源 ≥5 年/日周月永久 | 窗口外唯一通道=archiver 三阶段；可从源重算（原则 4） | 欠账批 3 清；此后并入滚动 reconciler | 无（契约 §2A 既有） |
| 9 | 契约欠账（TI 窗口外 19.4G+冷线 5.5G） | 24.9G | 清账后归零 | archiver 手动批执行（兼人工演练全链路） | 一次性手动 | 无 |
| 10 | working_vault 代码快照 | 每日快照+硬链接去重 | 14 天轮转（F 盘剩余 <60G 自动逐出，最少保 3 天） | backup.ps1 STAGE 3 自动轮转 | **已自动化** | 无 |
| 11 | git bundle | 单文件全史 | ≥7 天重建，留最新 2 份 | STAGE 3b 自动 | **已自动化** | 无 |
| 12 | db_dumps | 最新 1 份（/MIR 覆盖） | 建议 14 天日期化（缺口） | 现无版本化 | 缺口：批 8 落地 | **建议拍板**（§12.5） |
| 13 | offrepo 镜像（trae_memory/qmt_bridge/stash_archive/cold_archive） | 含冷库镜像 117.6G | 随源滚动 | robocopy /MIR 每日镜像到 F:\offrepo_backup | **已自动化**（批 1 后源改 F 路径） | 无 |
| 14 | F 冷库→G 镜像 | 0（未建） | 随 F 滚动 | 新增 STAGE 3d（§7.2） | 批 1 后**全自动** | 无（建议项） |
| 15 | .runtime/sessions 暂存 | 会话级 | 24h TTL | promote 或 TTL 清理（宪法 §9.4） | 治理链已有 | 无 |
| 16 | 冷储 90_tmp | 中转临时 | 30 天 TTL | SOP §7（现每月人工清） | 缺口：巡检生成到期清单（半自动） | 无 |
| 17 | 冷储 20_raw/30_corpus（含研报 90,243 件） | G 主库 | 永久 immutable | **永不清除**（发现错误写 _errata.md 附旁，不覆盖） | 不适用 | 无 |

**每天发生什么（大白话）**：早上 6 点机器自动备份全部家当；备份成功后机器看一眼"有没有整月的旧行情满 2 年了"——有就先抄两份（F 冷库+G 镜像）、逐行核对无误，才删掉热库里那份原件（数据本身永远在冷库躺着）；CH 运行日志按 7~90 天像浏览器历史一样自己滚；代码快照留 14 天、git 全史留 2 份、临时目录 30 天清。人只需要：每季度看一次压缩预检单、处置告警清单、拍板例外。

## 10. 执行批次（st-final3 战役收口后，每批带验收标准）

| 批 | 内容 | 验收标准 |
|----|------|---------|
| 0 裁定批 | 契约 v1.3.0（INV-RET-002 修订+滞回+批限量条款）+ ruling_registry 新裁定同 commit 原子；INFRA-STORE-002/LOG-OPS-001/asset_inventory 注记同 commit 对齐 | ruling 可检索；契约 changelog 完整；三处派生表述机查零矛盾 |
| 1 冷储主库迁移 | E:\zephyr_cold_archive（117.6G）→ F:\zephyr_cold_archive（robocopy+sha256 抽检+manifest 全量可读核验）；7+1 引用点同 commit 改（含新挖出的 known_data_gaps.yaml，01 文档 §3.1）；同批上线 STAGE 3d F→G 镜像+offrepo 源路径更新 | services_registry cold_archive 探测绿；manifest 1865+ 条全可读；G 镜像首夜完成；E 盘原目录保留 30 天双备份期后清（SOP §6） |
| 2 系统日志滚动 | 9 表 config TTL + text_log level=information；与季度压缩同停机窗 | 重启后各表 event_date 跨度 ≤ 保留天数；一周后系统日志日增 MB 级（对比 trace 时代 GB 级） |
| 3 欠账清账 | archiver 手动批：TI 窗口外 19.4G+冷线 5.5G | manifest 全 verified+dropped；CH 内释放约 24.9G；本批兼作滚动链路人工彩排 |
| 4 身份证 | business_data_categories lifecycle 对齐契约 10 层 + table_registry API + 新表 gate | 114 条机查零矛盾；新表缺身份证被 gate 拦截（演练一次） |
| 5 滚动归档 reconciler | shadow 1 个月 → 半自动计划单 → 全自动+熔断+kill switch | shadow 清单与人工核算零差异；熔断演练（人为置备份失败→reconciler 拒动）；kill switch 回退演练 |
| 6 尸体表处置 | Owner 裁定后 export→verify→（归档或弃）→DROP 35.4G；_bak 命名规则 gate 化 | manifest 记录完整；CH 内释放 35.4G；新 _bak 表强制日期后缀 |
| 7 压缩巡检机制 | 预检单脚本+一键执行+收尾自动验证（§8.3）；与批 2 同窗演练一次 | 压缩后内部空闲 ≥150G 红线；ch_parts_monitor 无告警；当日备份恢复 ok |
| 8 收尾 | db_dumps 版本化 + 季度 restore 演练自动化 + 90_tmp/manifest 对账巡检 | F:\db_dumps 出现日期化目录；演练报告落档 |

依赖：0 →（1/2/3 可并行）→ 4 → 5；6 依赖 0；7 依赖 2（同窗）；8 独立。批 3 建议先行——它就是全链路的人工彩排。

## 11. 风险与回滚（数据不能坏的硬保障）

**铁律：任何 drop 前必须①当日备份 ok ②export verify 行数+抽样通过 ③F 主库+G 镜像两份验证副本落盘 ④manifest 记录。四缺一即熔断。**

- **回退机制**：kill switch 一键停自动回手动；shadow 模式全程不删任何东西；熔断状态文件+飞书告警——人不在场时机器只会"少干活"，不会"多干活"。
- **可恢复性**：restore 自带 checksum 守卫（manifest md5 不符即拒绝，防冷库盘静默腐坏）；manifest append-only 全程可审计；误删兜底=F 镜像+G 兜底+git bundle 三层。
- **失败模式表**：

| 风险 | 缓解 |
|------|------|
| G 盘机械慢（写 70 MB/s/小文件 11.5 files/s） | 只放镜像不放在线链路；Parquet 大文件不触发小文件瓶颈 |
| F 盘 USB SSD 寿命/单盘故障 | 冷库双副本（G 镜像）+季度 checksum 抽检+研报另有 F/E 双份 |
| /MIR 传播删除 | 代码快照已版本化（v2.1）；冷库源 immutable 风险可控且 G 镜像是第二份；offrepo 目标清单变更走 asset_inventory 登记制 |
| 滚动 reconciler 误判（迟到数据/时区） | 滞回 1 月+只动"完整月"分区+verify 抽样比对三重防 |
| CH TTL 配置兼容性（26.6.1） | 系统日志 config TTL 是 CH 原生特性；最坏效果只是"日志没按期清"，不碰业务数据 |
| 压缩中途故障（唯一停机操作） | 半自动扳机+预检单五项全绿才执行+收尾自动验证（§8.3） |
| 全链停摆 | 150G≈22 个月缓冲；欠账指标每日可见（§5.7） |

## 12. 待 Owner 拍板清单

1. **契约铁律修订裁定**（头号议题）：INV-RET-002"手动触发"→"五重安全阀+事件触发自动+滞回 1 月+批限量+kill switch"，三步走（shadow→半自动→全自动）；ruling_registry 同 commit 原子；INFRA-STORE-002/LOG-OPS-001 同 commit 修订。
2. **尸体表 35.4G 处置**：export→verify 后 DROP（推荐，冷库留档）？部分留存？
3. **vhdx 压缩复决**：推荐恢复——滚动建立后库内有稳态空闲，压缩只回收垃圾空洞不占未来空间；节奏=季度+触发式（§8.2），半自动扳机（§8.3）。
4. **offsite 异地副本形式**：月度轮换盘（拔盘带离场）还是云归档（研报清单/manifest 等小体量优先上云）？
5. **db_dumps 版本化保留天数**：建议 14 天（与代码快照对齐）。
6. **批次排期**：st-final3 收口后批 0-3 是否一个窗口连做；批 5 shadow 期起算日。

## 13. 需求→章节对照表（自检收尾）

| Owner 需求 | 对应章节 |
|-----------|---------|
| 1 数据身份证 | §4（载体=lifecycle 字段+gate+默认 permanent） |
| 2 滚动归档自动化 | §2（冲突裁决）+§5（reconciler 设计）+§10 批 5 |
| 3 冷储入库自动化 | §6（inbox 事件化+三红线拦截） |
| 4 备份+冷储镜像自动化 | §7（3-2-1-1-0 映射+STAGE 3d） |
| 5 数据安全最高优先 | §5.3 五重安全阀+§11 铁律与失败模式；挖矿底账=01 文档 §1/§2 |
| 6 vhdx 冗余测算+压缩复决 | §8（8.1 定案/8.2 节奏/8.3 半自动/8.4 复决） |
| 追加 1：150G 定案+季度压缩+人工扳机解释 | §8.1-8.3 |
| 追加 2：《保留与清除总清单》 | §9 表格（17 行） |
| 追加 3：日志滚动大白话 | §9 表+表后"每天发生什么"段 |
