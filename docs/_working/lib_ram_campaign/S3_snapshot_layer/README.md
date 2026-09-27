---
ttl: task_bound
title: "S3 本地快照层挖矿簿 · 目录契约判家 + 格式选型对比 + 留2份崩溃安全轮转 + 刷新挂接既有事件链"
created: 2026-09-28
sid: st-libram-s3
lane: lib_ram_campaign/S3
status: v2（G2 后缀集已闭合实测；自审=未干，缺口见⑤）
---

# S3 本地快照层挖矿簿

## ① 职责一句话

给"磁盘只留 2 份、logrotate 式轮转、新快照落盘成功才删上上代"的本地快照层定出：合法目录家（过 directory_contract 判据）、格式选型（含版本列铁律——本仓 ReplacingMergeTree 无版本列事故先例在案）、崩溃安全落盘序、以及零新增计划任务的刷新挂接点。

## ② 现状实测

### 2.1 目录契约判家（[亲验] 实读 `docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml`）

| 候选家 | 契约判定 | 证据 |
|---|---|---|
| `docs/01.../`、`docs/02.../`、`docs/03_modules/`、`architecture_model/` | **永久区**，default_ttl=permanent，新文件必经 `--allow-promote` 门禁 | contract L88-99；快照是二进制/机生运行数据，doc_type/扩展名校验 DCR-001~008 不过——**排除** |
| `docs/_working/` | **临时区**，default_ttl=task_bound，post-commit reconciler 自动归档（gate: auto_archive） | contract L134-139；快照要跨任务存续（留 2 代滚动），归档器会移动/清理——**排除**；且宪法 §9.4 永久区禁引临时区，R4 常驻服务（永久件）要读快照即违令 |
| `.runtime/sessions/<sid>/staging/` | 24h TTL 会话暂存，成果须 promote 才算交付 | 根宪法 §9.4；快照须跨会话长存——**排除**；禁向 .runtime 根直写 |
| `.runtime/tmp/` | 临时输出区；fs_collector `_SKIP_DIRS` 含 ".runtime"（`src/zephyr/library/collectors/fs_collector.py:33-50`）不入账本 | 语义="临时"，TTL 清理与"留 2 份"契约不匹配——**排除**为主家，可作中间 tmp 写跳板（`.tmp` 后缀落同目录，天然幂等可弃） |
| `data/`（拟 `data/library_snapshots/`） | **中性区**：`data/` 与 `tmp/`、`.runtime/` 同列 zone.neutral.paths（contract L174-189），default_ttl=null（文件 ttl 头部显式声明，仅对文本件适用 GATE-15），gate=none | **合法主家**。盘面先例 [亲验 ls]：`data/cache/`、`data/gate_cache/`、`data/drift_baselines/`、`data/depgraph.db` 等运行态数据目录大量存在；`.gitignore` 有 per-directory 机生数据排除先例（L176-202 `data/drift_baselines/*` 等 8 条同款）——快照目录照此登记 `data/library_snapshots/*` 即完全循例 |
| 仓外 `G:/backup/db_dumps/library`、`F:/zephyr_cold/library` | 备份双链既有落位（INFRA-STORE-003 四盘地图：G=备份总仓、F=纯冷库，**"USB 盘禁热服务/热库"**） | `scripts/backup/library_ledger_backup.py:52-53` PRIMARY_ROOT/MIRROR_ROOT；D=NVMe 生产盘。快照是**热读加速件**非备份件——落 G/F 即违反 USB 禁热红线；**排除**，但保持与备份链的分工声明（§3.6 净零） |

**判家结论**：快照层合法家 = `data/library_snapshots/`（仓内 D 盘中性区，gitignore 循 drift_baselines 先例）；备份双链（G/F）继续专属灾难恢复语义，两层不互替。

### 2.2 版本列铁律的先例证据 [亲验]

- `docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md:339-341`：tick_data 设计裁定 **#ARCH-CH-002 = ReplacingMergeTree 无版本列**（§4.0 全表策略 #ARCH-CH-009 的已登记例外，5 字段 ORDER BY 精确去重）；`:361-364` 注记 kline_daily 同型"蓝图内部矛盾——DDL 未定义 ingest_ts"。
- 同目录 `business_data_categories.yaml:5531` 硬约束："ReplacingMergeTree(ingest_ts) 版本列 latest-wins"——**本仓已把"无版本列→旧行覆盖修正行"教训立法为版本列纪律**。
- 映射到快照层：任何"同键覆盖"式快照轮换（固定文件名）若无版本列，读侧无法判定行新旧——**快照必须携 `ledger_version`（=S1 指纹 max(event_id)）列/字段，且文件侧以版本号为提交记录**（§4.3）。
- 账本侧对照事实：lib_assets 行级有 built_at/generation（S1 §2.2），快照行直接携带即天然满足铁律。

### 2.3 格式库可用性（[亲验] python -c import 实测，Python 3.12.8）

duckdb 1.5.2 OK｜pyarrow 19.0.1 OK｜orjson 3.11.8 OK｜sqlite3 内置 OK｜pandas 2.3.3 OK｜zstandard **MISSING**（压缩选型受影响）。

## ③ 六向台账

### 3.1 真源
- 快照**非真源**：PG 两表恒为唯一真源（S1 §3.1）；快照=可派生镜像（内收判据"同真源可派生"），任何时刻可整删重建——删除观察期/冷库红线不适用于它（它属热层缓存件非档案件）。
- 版本水位真源=`lib_events.max(event_id)` [亲验 2,231,744]（S1 案 B）。

### 3.2 写者
- 唯一快照写者（拟建）：单一带 `_SQL_COPY`/SELECT 全读 + 序列化的脚本/模块；写通道走 tmp→fsync→rename 原子序（§4.3）。
- 复用底座：`get_depgraph_pg_connection()` reader 角色（`library_ledger_backup.py:49` 同款导入先例）；生成器纪律"静态清单禁手工维护"（根宪法 §9.5）→ 快照目录内 manifest 由写者机生。

### 3.3 消费者
- S2 世代缓存层的**冷启动源**：新进程首查若 PG 可达→直连+（可选）异步落快照；若 PG 不可达→读快照兜底（降级面）。
- `lookup_assets`/CLI 的 PG-down 兜底路径（现状 PG down 即抛，`lookup.py:13` ERROR_CONTRACT 上抛——快照提供第二条只读通路，行为增强不破坏）。
- restore_drill 语义邻件：`scripts/backup/restore_drill.py:57` 已把 lib_assets/lib_events 列为演练表（CSV 流式核验 [亲验 grep]）——快照核验可同型复用其抽样比对思路。

### 3.4 漂移史
- S5 簿 §2.2 三快照漂移=**视图层**无世代锚事故；磁盘快照层同型风险=读旧快照判新——版本列/manifest 承载代际即免（§4.2）。
- `library_ledger_backup.py` manifest 先例（`:132-145` `_prune_old_backups`/`_load_manifest`，滚动 30 天+月 1 日 pin）——轮转+manifest 双件在本仓已有成熟形态，快照层是"retention=2 的同类件"。
- CAS 残渣前科（S1 簿 E1 类 59 条 .tmp 被当真源引用）：快照 tmp 后缀文件必须同目录幂等覆盖写，崩溃残渣由下次写覆盖，禁被引用。

### 3.5 冲突面
- 避让铁律六件（见任务书）：快照刷新**不挂** library_regen_reconciler/reconciliation_registry/library_new_module_reconciler（零 import 零改）。
- `library_ledger_backup.py`/`backup.ps1` **不在避让清单**，是设计上的首选挂接宿主；但二者属 disaster_recovery_backup 蓝图域（MOD-INF-043，`library_ledger_backup.py:1-2`），改动需同步其 blueprint/algo_flow（施工批仪式链）。
- fs_collector 白名单含 data/（S5 簿 §2.3 记载 8 根）：**[亲验] `_TEXT_SUFFIXES` 全集 15 项**（`fs_collector.py:75-92`：.py/.md/.yaml/.yml/.json/.csv/.ps1/.sh/.sql/.txt/.toml/.cfg/.ini/.html + 前置批），过滤在 `:146-147`——`.parquet/.db/.gz/.jsonl/.zstd` **均不在册** → 快照数据文件（任一候选格式除 manifest）**不入账本，无自注册 churn**；唯 **`.json` 在册**→ §4.2 的 manifest 若用 .json 后缀=每次轮换给同一稳定 asset_id 行加 built_at/generation（单行 upsert 有界噪音，可容忍）或改嵌 parquet footer metadata（零 manifest 文件方案，施工批二选一）。

### 3.6 净零方案
- 与备份双链分工：备份=灾难恢复（30 天滚动+月 pin，人读语义"可回滚历史"）；快照=读加速（仅 2 份，无历史价值）——**不并家不互替**，快照可整删无损失，备份不可；两 manifest 各记各的代际防混读。
- 不新增计划任务（Owner 定版+宪法 §9.3）：刷新搭既有 `ZephyrAlpha_LibraryLedgerBackup` schtasks 链路（`library_ledger_backup.py:5` CONSUMERS 头在案）或生成链后置，见 §4.4。
- 快照不建新表零 DDL（不引入 lib_snapshot 表——磁盘件不进真源平面，避免 RULE-SSOT 双向漂移）。

## ④ 施工处方（设计案，供施工批直接开工）

### 4.1 格式选型对比表

| 维度 | duckdb 文件 | sqlite | parquet(pyarrow) | jsonl(orjson) |
|---|---|---|---|---|
| 44,963 行全量读延迟 | 亚毫秒~ms（mmap 列存）[推断] | ms 级（行存+B-tree）[推断] | ms 级（pyarrow 列存直读）[推断] | 10–40ms（JSON 解析+dict 构造）[推断] |
| 写原子性 | 单文件 CREATE/ATTACH，崩溃可毁整库（WAL 弱） | 事务+WAL 强 | 单文件写完才 rename，天然原子（文件级） | append 不原子→整文件 tmp+rename 后原子 | 
| 版本列承载 | 表列 | 表列 | 列+footer | 每行冗余或 sidecar manifest |
| 仓内宪法摩擦 | **"零裸 duckdb"红线**（根宪法 §9.1+`library_ledger_backup.py:8` INVARIANTS 演练件刻意"零裸 duckdb"先例）——开 duckdb 读快照=正面冲撞house style，需豁免论证 | DatabaseService 只管 governance db；新 db 文件直连 sqlite3=灰色（禁的是裸 duckdb，sqlite 先例=data/depgraph.db 历史件）——摩擦中 | 与冷库归档同格式族（INFRA-STORE-003 Parquet 冷档案、L208 tick 归档"Parquet zstd"）**但本机 zstandard MISSING** [亲验]（须 gzip 或引依赖） | 零红线摩擦；与 `library_ledger_backup.py` CSV+gzip 备份同族纯文本流 |
| fs_collector 入账风险 | 低（.db 不在后缀集） | 低（.db/.sqlite 不在集） | 低（.parquet 不在集） | 低（**.jsonl 不在集** [亲验 L75-92 全集 15 项]；唯 .json sidecar manifest 入账——单行有界噪音或 footer 内嵌规避，见 §3.5） |
| 无版本列事故面 | 建表 DDL 带 `ledger_version bigint` | 同 | schema 字段 `version` + 全局写者注入 | manifest.json 记 version + 行内可选 |

**选型建议**（案卷级，非批文）：**首选 parquet（gzip 帧，pyarrow 现成 [亲验 19.0.1]，不引 zstd 依赖）**——列存读延迟最优、单文件即原子提交单元、与冷库 Parquet 档案格式族对齐、避开 duckdb 裸连宪法摩擦；备选 jsonl.gz（完全循 `library_ledger_backup.py` CSV gzip 家法，实现最薄）。duckdb 文件因 §9.1 红线**不荐**；sqlite 因灰色直连面**不荐**。终案留 Owner/施工批按红蓝实测读延迟定夺（差距若 <5ms 则取实现最薄的 jsonl.gz）。

### 4.2 快照内容规格

- 行集=lib_assets 全 21 列（实库列集 [亲验 §S1 2.1]）+ **快照级元数据**：`ledger_version`(=构建时 `max(event_id)`)、`built_at_utc`、`row_count`、`sha256`、`columns`（manifest 承载，行级 built_at/generation 原生自带满足版本列铁律）。
- 只收 `status <> 'deceased' OR disposition_authority IS NOT NULL` 全量即收（不裁行——裁行=第二裁判，违"整表镜像"）。
- 命名：`lib_snapshot.v<ledger_version>.<ext>`（文件名携版本=可读的代际声明）+ 稳定入口 `lib_snapshot_latest.manifest.json`（内容 pointer，tmp+rename 写）。

### 4.3 留 2 份轮转的崩溃安全序（"新快照落盘成功才删上上代"）

```
1. 读指纹 v_new = max(event_id)                     [PG 单查询, 3.4ms 实测]
2. v_new == manifest.version 且 latest 文件存在      → 跳过（幂等，0 IO）
3. 全表 SELECT → 内存 → 写 lib_snapshot.v<new>.<ext>.tmp（同目录）
4. flush + fsync(.tmp) → os.replace(.tmp → v<new> 正式名)   ← 提交点①：文件级原子
5. manifest tmp → fsync → os.replace                  ← 提交点②：代际记录生效
6. 列举目录：按文件名版本排序，保留 v_new 与其前一代，
   删除其余（=上上代起）                              ← 仅在②成功后执行
7. 任一步失败：.tmp 残留无害（下次覆盖/幂等清理），
   manifest 未换=读者恒见旧 pair，两代快照从未被删——
   崩溃窗口内磁盘状态恒 ∈ {旧 pair, 新 pair+旧}，无第三态
```

- 判据核：删旧动作**严格后置**于 manifest 提交（步骤 5→6 序），满足 Owner"新快照落盘成功才删上上代"；"成功"定义=fsync+rename 双完成（落盘语义），非"写调用返回"。
- 读侧配平：读者取 manifest（单文件点读）→校验 version 与目标文件名前缀一致→打开；不一致=半途损坏，视为无快照。
- 目录级互斥：写者进程锁（复用 `lock_files.py` 语义或目录内 `writer.lock` O_EXCL 创建+TTL 自愈——施工批择一，禁双写者）。

### 4.4 刷新挂接点（禁新增计划任务）

| 候选 | 链 | 判据 |
|---|---|---|
| **A（荐）** `library_ledger_backup.py backup` 成功尾步 | 既有 schtasks `ZephyrAlpha_LibraryLedgerBackup`（`CONSUMERS` 头 `:5`，register_library_ledger_backup_task.ps1 在册）→ run_backup 双链落位成功后同进程追调 snapshot_writer.refresh()（fail-open：快照失败只记 warning 不改备份退出码） | 零新计划任务✓ 事件驱动=备份事件✓ 备份已全表流式导出 CSV——快照复用同一读事务/同批行数据 [施工批可把 _dump_table_csv 行流喂给快照，省一次全表扫] |
| B `generate_library_index.py` 生成尾步 | 该件已被 library_regen_reconciler（避让件）调用，且自身 act() 自登记（S5 簿 §3.2）；挂尾步=经"生成事件链"刷新，改的是非避让件 | 事件源=post-commit 触发链（宪法 §9.3 事件触发✓）；账本刷新频率=采集入账频率，与 B 的 reconciler 节奏天然同步；缺点：CLI 手跑也会触发写盘（无害） |
| C 读路径惰性刷新（S2 缓存 miss→重载成功时旁路落快照） | 纯读驱动，零新链 | 违反"读路径不做大 IO"倾向（全表序列化在用户请求路径内），仅可做 low-priority 后台线程——线程≠sleep-loop（一次性 submit 非轮询）可接受但复杂度高 |

选 A 为主、B 为补（生成链事件也刷，幂等秒退由步骤 2 版本比对保证）。全链无 cron/Timer/sleep-loop 新增（复用既有系统级 schtasks 备份调度=不违令，先例判据 `library_ledger_backup.py:21` "调度走 schtasks（系统级调度，reaper keep 登记放行）"）。

## ⑤ 自审闸三态

**判定：未干**。已干面：目录契约四候选判家（contract 实读 file:line）、版本列铁律先例 [亲验]、格式对比表、崩溃安全 7 步序、挂接点三案。

| # | 缺口 | 等级 |
|---|---|---|
| G1 | 各格式 44,963 行实测读延迟未跑（表内全 [推断]）——**可施工前一次性 bench 消项** | 中 |
| G2 | ~~fs_collector `_TEXT_SUFFIXES` 未读全~~ **已闭**（§3.5/§4.1：全集 15 项 [亲验]，候选格式全部免入账，manifest .json 单行噪音已给双规避案） | 已闭 |
| G3 | `data/library_snapshots/` 新目录是否需 .gitignore 之外登记（directory_contract 生成器豁免区/DCR 扩展名校验细则 DCR-005/006 未逐条读） | 中 |
| G4 | backup.ps1 STAGE 2 与 library_ledger_backup.py 的触发时序未验证（两链独立 schtasks？同日双跑竞争窗口） | 低（挂接点 A 在其自身链内，不受 backup.ps1 影响） |
| G5 | reaper keep 登记（`data/runtime/process_reaper_keep.txt`）对快照写者进程是否需要——快照写=短任务应不需，未实测 | 低 |
