---
ttl: task_bound
---
# F/G 冷储体系纳入图书馆 + Qoder MCP 现状案卷（只读调研）

> 生成：2026-09-28，只读调研会话。零写改：本文件是**唯一**产出物，落在 `.runtime/tmp/`（根宪法 §9 条目 4 许可的临时输出区）；未触碰任何仓库源文件、注册册、Qoder 配置。
> 环境：`python --version` = **3.12.8** [亲验]。仓库内模块调用形态 = `PYTHONPATH=src python -m …`。
> 证据等级：**[亲验]**=本次命令/读取直接观察；**[读档]**=仓库既有文件所载（已用 Read/Grep 验存在）；**[推断]**=基于前两者的推论。

---

# 【A】G 冷储 / F 盘备份 "纳入图书馆" 现状

## A0. 一句话结论

**图书馆早已为"基建与备份"开好了馆、留好了 kind 枚举，但馆内藏书 = 0，且历史上唯一一条 F 盘冷储资产已被自家对账机制判死（deceased，去向未评估）。** 缺的不是图书馆的"入口"，而是**一个能持续产出 `backup`/`infra` kind 的采集器**；任何手工登记的仓外资产若没有采集器每轮复现，必然被 ghost→机械可证注销链条吃掉。推荐路线：**从既有真源 `infrastructure_registry.yaml` 的 INFRA-STORE-* 条目派生资产（登记册条目锚定 home），零领地冲突。**

## A1. 图书馆系统的真源与入口

| 面 | 事实 | 证据 |
|---|---|---|
| 查询总口 | `python -m zephyr.library.lookup <关键词> [limit]`，可加 `--kind/--owner-domain/--tags/--status/--home-prefix/--limit/--no-alias`，另有 `--backtest[--strategy/--since/--until]`、`--feeds <kw>`（供数反查，裁定#410）、`commit-guide:<topic>` 三个特殊查询面 | [亲验] `src/zephyr/library/lookup.py` L20-27、L307-330；实跑成功 |
| 返回结构 | stdout TSV：`asset_id \t kind \t status \t home`，deceased 行追加 `\t-> 去向`；全表无 active 而有 deceased 时追加 `(moved: …)` 行。API 侧 `lookup_assets()` → `list[dict]`（键 asset_id/kind/home/status/title/built_at/disposition_authority/successor_of） | [读档] lookup.py L288-294、ledger_schema.py `_SQL_LOOKUP` L160-166 |
| 匹配语义 | 仅 `asset_id ILIKE %q% OR home ILIKE %q% OR title ILIKE %q%`，`ORDER BY asset_id LIMIT n`；**不索引文件内容、不索引注册表条目内部 ID** | [读档] ledger_schema.py L160-166 [亲验] 实测（见 A3 INFRA-STORE 0 命中） |
| 别名轴 G15-① | 查询词先过 `library_tag_vocabulary.yaml`（aliases + match_tokens）展开再合并；fail-open | [读档] lookup.py L51-98 |
| **真源平面** | **PostgreSQL `lib_assets` / `lib_events`**（depgraph 库共生，表前缀 `lib_`）；`docs/library/*.md` 全是**生成视图** | [读档] ledger_schema.py L17-21、L66-103 |
| 唯一写路径 | `zephyr.library.librarian.Librarian.act()` / `register_batch()`（事件与状态同事务；`delete` 必须带处置预授权 authority） | [读档+亲验] librarian.py L24-29、act()/register_batch() |
| 谁生成馆页 | `scripts/governance/generators/generate_library_index.py` → `docs/library/{INDEX,code,data,doc,rule,gate,pipeline,backup}.md`；`scripts/governance/generators/generate_front_door.py` → `FRONT_DOOR.md`（其 frontmatter `generated_by:` 自证） | [亲验] 两文件均存在；FRONT_DOOR.md 头部 GENERATED FILE 声明 |
| 相关册子 | `docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml`（词表）、`registry_master_index.yaml`、`capability_canonical_file_registry.yaml`（他队领地）、`docs/registry_of_registries.yaml`（ROOR）。`docs/library/regulations.md` **不在七馆表内**（七馆=code/data/doc/rule/gate/pipeline/backup），来源存疑 [推断] | [亲验] ls + INDEX/FRONT_DOOR 表对照 |

## A2. 收录判据：一个资产要怎么才能进图书馆

1. **字段（户籍）** — `lib_assets` 列（`_SQL_ENSURE_ASSETS`）：`asset_id, kind, home, family_id, fingerprint_sha256, fingerprint_aux, built_at, generation, status, owner_domain, retention_class, disposition_authority, successor_of, registered_at/by, title, one_liner, ai_contract, tags[], ext, potential_consumers`。[读档]
2. **身份派生唯一公式** — `derive_asset_id(kind, home) = "<PREFIX>:<home>"`（反斜杠→正斜杠），`_KIND_PREFIX` 12 枚举：module→MOD / file→FILE / table→TBL / registry→REG / doc→DOC / task→TASK / mcp_tool→TOOL / **backup→BAK** / pipeline_node→PIPE / factor_strategy→FCT / prompt_agent→PRA / **infra→INF**。`STATUSES` = active/stale/orphan/archived/deceased/ghost/blind。[读档] **关键：`home` 只校验非空，不校验是否在仓内 ⇒ 索书号层面本来就容得下 `F:/…`、`G:/…` 或合成前缀。**
3. **入账唯一现实通道 = 采集器**。`zephyr.library.collectors` 注册表固定六路：`fs / pg / ch / schtasks / mcp / logs`，`collect_all()` → `ingest_all()` → `register_batch()`。[亲验] `collectors/__init__.py` L31-41。
4. **"仓外资产"有没有登记通道？→ 有，而且已经有 4 个先例，用的都是"合成 home 前缀"而不是文件路径**：
   - `schtasks_collector`：`home = f"schtasks:{task_name}"` → `TASK:schtasks:…`，tags `["schtasks","外溢资产"]`（Windows 计划任务=纯仓外实体）[亲验]
   - `pg_collector`：`home = f"pg:{name}"`；`ch_collector`：`home = f"ch:{database}.{name}"`（数据库对象，非盘路径）[亲验 grep，实测 346 条 table active]
   - `mcp_collector`：`home = f"mcp:{server}"` → `TOOL:mcp:…`（29 条 active）[亲验]
   - `logs_collector`：对**占位/模板/仓外 path**明确改为 `home = f"{LOG_REGISTRY_REL}#{log_id}"`，源码注释直书"**此类改以登记册条目本身定位（不猜真实路径，禁猜配先例）**"，并用 `placeholder = any(ch in path for ch in "{}<>（:")` 识别脏 path。[亲验] ← **这条就是仓外盘资产该抄的模板。**
   - 反之 `fs_collector`：`_SCAN_ROOTS = (src, scripts, tests, docs, config, data, schemas, architecture_model)`，`collect(root=".")` 纯仓内相对路径 rglob ⇒ **文件系统层零仓外扫描通道**。[亲验]
5. **防自裁约束（决定路线可行性的硬机制）**：
   - `library_regen_reconciler.py`（他队领地，只读）post-commit 跑 `collect_all()` → `ingest_with_shrink_guard()` → `generate_library_index.py` → `check_library_coverage.py`；触发面 `_TRIGGER_PREFIXES = ("src/","scripts/","data/","docs/01_policies_and_standards/_registry/")`（⇒ **改 infrastructure_registry.yaml 会自动触发图书馆刷新，无需碰 reconciler**）。[亲验]
   - `check_library_coverage.py`：`_SQL_IDS` 取 `kind IN ('file','module','doc','registry') AND status NOT IN ('deceased','archived')`，与 `fs_collect(".")` 盘面做双向差集：`ghost = 馆有盘无`。[亲验]
   - ⇒ **[推断，机制链完整] 任何以 `kind='file'` 手登记、home 指向仓外盘的资产，必然出现在 ghost 集里**（盘扫描永远不产出它），从而被"机械可证注销"。这正是 F 盘那条资产的确切死因（见 A4）。

## A3. 六词实测（`PYTHONPATH=src python -m zephyr.library.lookup <q> --limit 8`）

| 查询词 | 结果 | 关键细节 |
|---|---|---|
| `冷储` | **1 命中，且唯一命中是死账** | `FILE:F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl（仓外绝对路径——冷储主库 F 盘）` / kind=**file** / status=**deceased** / 追加 `(moved: … -> 去向未评估)` |
| `备份` | **0 命中** `(no results for '备份')` | 全库无 title/home/asset_id 含"备份"的在编资产 |
| `zephyr_cold` | **同上 1 条死账**（同一行） | 注意：它能被 `冷储` 命中，**纯粹因为 home 里混进了中文括号注释**——home 污染反而是唯一可发现性来源 |
| `backup` | 8 命中，**全是 `DOC:` 仓内文档** | `[alias] 'backup' -> backup -> 备份`；命中含 `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/{backup_inventory,blueprint,dr_runbook,index,storage_map}.md`、`algo_flow/backup_tick_poller.yaml`（active）+ 2 条 `docs/_working/…`（archived）。**0 条 `BAK:` / `INF:` / `F:` / `G:`** |
| `INFRA-STORE` | **0 命中** `(no results for 'INFRA-STORE')` | 而根宪法 §7 明文引用"地图=INFRA-STORE-003" ⇒ **宪法引用在图书馆里查不到**（原因：该 ID 只活在 yaml 文件内容里，见 A4-L1） |
| `asset_inventory` | 8 命中，全是 `DOC:docs/03_modules/_domain_infrastructure/algo_flow/asset_inventory/*.yaml` | 未见 `MOD:` 行——**方法学坑：`ORDER BY asset_id` 使 `DOC:` 恒排在 `MOD:` 前，limit 小时被 doc 挤满**；需 `--kind module` 复核 |

> 方法学注记：本轮首次实跑在管道里读 `$?`，取到的是 `head` 的退出码（恒 0），**不能**作为 lookup 退出码证据；源码契约是 0=有结果 / 1=无结果或用法错误（lookup.py L300-306、L218）。此点标 [读档] 不标 [亲验]。

**总账现状（只读 SQL 实测，`get_depgraph_pg_connection`）[亲验]：**

| kind | active | archived | deceased |
|---|---|---|---|
| doc | 5465 | 1539 | 11 |
| file | 24658 | 8923 | 53 |
| module | 3778 | — | 12 |
| table | 346 | — | 19 |
| registry | 79 | | |
| task | 50 | | |
| mcp_tool | 29 | | |
| **backup** | **0** | 0 | 0 |
| **infra** | **0** | 0 | 0 |

- 显式 `SELECT count(*) … kind IN ('backup','infra')` = **(0,)**。
- active 合计 5465+24658+3778+346+79+50+29 = **34405**，与 `docs/library/INDEX.md` 声明的"在编资产总数 34405"**逐位吻合**（生成器口径 `status NOT IN ('deceased','archived')`）⇒ 馆页与总账当前无计数漂移。[亲验]
- 非死档 home 前缀 Top20（`left(home,8)` 分组）里 **没有任何 `F:/` 或 `G:/` 开头项**（最大外仓式前缀是 `ch:c1_ma` 203 条）。[亲验]
- 那条唯一 F 盘资产的完整墓碑：`title='CH 冷归档清单'`、`successor_of=NULL`（= 去向未评估）、`disposition_authority='自裁[机械可证注销：st-ulib3c-20260923 终验班 coverage 清零，Owner 2026-09-23 批两步处置；逐件盘上缺失反证 317/317（先例=st-ulib2-20260921 验收轮 12/12 口径）；ghost=他会话产物已删/轮转目录已排除入册，账实修正]'`。[亲验]
  - 注：字面串"机械可证注销"在 `src/`+`scripts/` 的 .py 里 grep 不到（[亲验] 0 命中）⇒ 它是**历史会话写入 `disposition_authority` 的自由文本**，不是当前代码模板产物。机制归因以 `check_library_coverage` 的 ghost 定义为准。[推断]

## A4. F/G 体系现在登记在哪、断在哪

**三层已存在，第三层是断点：**

- **L1 架构册（真源，机器可读）已登记** — `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`：
  - L181 `infra_id: "INFRA-STORE-001"`、L197 `INFRA-STORE-002`、L214 `INFRA-STORE-003` [亲验 grep 行号]
  - INFRA-STORE-002 `host: "F:/zephyr_cold/50_archive/by_project/zephyralpha"`（L202）+ `access_method`（archiver.py 四命令 / rolling_archive_reconciler.py / DuckDB 直读 Parquet / `archive_manifest.jsonl` 清单）（L203）
  - INFRA-STORE-003 `host: "F:/zephyr_cold + G:/backup"`（L219）、`description`（L217）载四盘分工 D/E/F/G+offsite、3-2-1、CH 双备份链 `ch_backup_disk.vhdx`(F 主)/`ch_backup_disk2.vhdx`(G 二)、`G:/backup/{working_vault,db_dumps,git_bundles,offrepo}`、冷库三红线；`note`（L229）载 2026-09-24 ch_vm_backup 收敛终态与 10-05 摘盘遗留。
  - **图书馆对 L1 的覆盖粒度 = 整个文件一条**：实测存在 `REG:docs/…/infrastructure_registry.yaml`(active, title=infrastructure_registry.yaml) 与一条同名 `FILE:`(archived) 行 [亲验]；**册内 3 个 INFRA-STORE 条目不是资产** ⇒ `lookup INFRA-STORE` 必 0 命中。
- **L2 永久手册（人/AI 可读）已登记且可查** — `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/`（module_id **MOD-INF-043**）：`storage_map.md`（frontmatter title 自署"INFRA-STORE-003 永久手册"，summary 关键词锚=冷库/冷储/备份/backup/四盘/storage；§1 四盘表、§2 关键词→落点速查、§3 五条铁律、§4 遗留指针）、`backup_inventory.md`(v1.2.0，F 盘目录树+7 类备份组件来源/目标/方法/频率表)、`dr_runbook.md`、`blueprint.md`、`index.md`。这些在图书馆里**是 active `DOC:` 资产**（`backup` 查询 8 命中即含它们）。[亲验]
  - 注：`storage_map.md` §1/§2 与 `backup_inventory.md` §1-§2 口径有**时代差**：后者仍以 F 为唯一备份目标盘（2026-09-15 数据），前者已是 D/E/F/G+offsite 四盘定案（2026-09-23）。[亲验 读档对照] 属文档内文一致性债，非图书馆缺口。
- **L3 总账 lib_assets = 断点** — `backup`/`infra` kind **0 行**；七馆之一的**基建与备份馆 `docs/library/backup.md` 条目数 0**，`INDEX.md` 与 `FRONT_DOOR.md` 同步报 0；唯一一条 F 盘历史资产已 deceased 且去向未评估。[亲验]

**断点的三处根因（精确到行）[亲验/读档]：**
1. `generate_library_index.py` L58：`("backup", "基建与备份馆", lambda kind, home: kind in ("backup", "infra"))` ⇒ **馆的入馆谓词只认这两个 kind**；而全仓 `grep "'backup'|'infra'"` 在 `src/zephyr/library/` + 两个 generators 里**只有 schema 定义与 relations/馆谓词引用，零个采集器产出它们** ⇒ 馆恒空是**数学必然而非疏漏**。
2. `fs_collector._SCAN_ROOTS` 八个仓内根 + `collect(root=".")` ⇒ 没有盘级通道（见 A2-3）。
3. `check_library_coverage._SQL_IDS`（kind 含 file）× `ghost = 馆有盘无` ⇒ 手登记的仓外 `FILE:` 资产必被判 ghost。F 盘那条即死于 2+3 的合围；它的 home 还带了中文注释（违反"home=可定位路径"洁癖，`logs_collector` 后来专门为此加了 `placeholder` 识别），属**双重姿势错误**。

## A5. 两条候选路线

### 路线一（推荐）：登记册条目派生 —— 新增第 7 采集器，从 infrastructure_registry 派生 `INF:`/`BAK:` 资产

- **做什么**：新建 collector，读 `infrastructure_registry.yaml` 的 `INFRA-STORE-*`（及未来 `infra_id`），每条目产出一条资产：
  `kind` 按条目语义映射（存储/备份类→`backup`，其余基建→`infra`）、`home = "infrastructure_registry.yaml#INFRA-STORE-003"`（**照抄 `logs_collector` 的登记册条目锚定姿势**）、`title` = 条目 name/description 摘要、`tags=["外溢资产","cold-storage","backup"]`、`ai_contract` 写"物理位在 F:/G: 盘，仓外，明细大盘自查（族级，不逐件）"。
- **改哪些文件**：① 新建 `src/zephyr/library/collectors/store_collector.py`（或 `infra_collector.py`）；② `src/zephyr/library/collectors/__init__.py` 的 `registry` dict 加一行 `"store": store_collect`（+ docstring "六采集器"→"七"）。**就这两处。**
- **走哪个生成器/登记链**：`collect_all()` 自动带出 → `ingest_all`（或 post-commit `library_regen_reconciler` 现成链，**不改它**）→ `python scripts/governance/generators/generate_library_index.py` 重生成 `backup.md`/`INDEX.md` 计数 → `generate_front_door.py` 重刷 FRONT_DOOR 七馆计数 → `generate_project_depgraph.py --force` + `apply_depgraph.py --add-design-node`（RULE-DEPGRAPH）→ `creation_token`（`scripts/governance/d3_metadata/batch_creation_tokens.py`）→ 新建 .py 大白话简介经 **`scripts/governance/d3_metadata/add_module_translation.py` 生成器通道**（注意：AGENTS.md 只写 `add_module_translation.py`，真路径在 `d3_metadata/` 子目录，`scripts/governance/` 根下不存在此文件 [亲验]）。
- **净零合规（根宪法 §4）**：不新增馆、不新增 gate、不新增册子、不新增 kind —— 复用**已存在但空置**的 2 个 kind 枚举 + 1 个空馆 + 1 本既有真源册 ⇒ 属"接入"而非"扩张"。
- **红利（顺带修宪悬空引用）**：`lookup INFRA-STORE` 从 0 命中变命中（`asset_id ILIKE` 直接吃 `INF:…#INFRA-STORE-003`）；`lookup 备份` 从 0 变命中（若 title 带中文，或补 `library_tag_vocabulary.yaml` 的 `match_tokens`）；基建与备份馆从 0 变在编。
- **领地冲突核查**：**零冲突**。不触碰被禁清单 `library_regen_reconciler.py` / `reconciliation_registry.py` / `library_new_module_reconciler.py` / `project_handbook` 族 / `capability_canonical_file_registry.yaml` / `module_translation_registry.yaml`。`module_translation_registry.yaml` 只经生成器 CLI 追加，非手改；`docs/library/backup.md`、`INDEX.md`、`FRONT_DOOR.md` 是生成视图，由生成器重写、不手改。**跨队摩擦面仅剩"共享 lib_assets 表 + 共享 post-commit reconciler 行为"这一既有事实**，且新采集器每轮复现 ⇒ 不会与他的 ghost 对账互相打架（与手登记的根本区别）。
- 补充：`.runtime/locks/` 只有 heartbeat .pid 文件、无 per-file claim 可查 [亲验]，故领地约束按 Owner 交办清单为准，未做第二方验证。

### 路线二（不推荐）：盘根直采 —— 扩 `fs_collector` 支持绝对盘根

- **改哪些文件**：`src/zephyr/library/collectors/fs_collector.py`（`_SCAN_ROOTS`/`collect(root=".",…)` 签名 / `_SKIP_DIRS` / `_FAMILY_DIRS` / `limit=60000`）；馆页同上由生成器重刷。
- **代价（逐条可证）**：
  1. `fs_collector` 是 `check_library_coverage.run_coverage()` 的**盘侧基准**（`disk_ids/disk_homes` 直接来自它）[读档]，改它=改对账语义，blind/ghost 计数跳变，行为与 LIBRARY-REGEN 链（reconciler 在他队领地）耦合面扩大；
  2. `G:/backup/{working_vault,db_dumps}` 是 14 天滚动目录，逐件入册会**复刻** `_FAMILY_DIRS` 注释记录的真实事故（"2026-09-23 实测两目录占 226/259 ghost、馆内 1988 行"）[读档]；
  3. `F:/ch_backup_disk.vhdx` 实测 716.32 GiB、`G:/backup/ch_vm_backup/data.vhdx` 591.57 G [读档 infrastructure_registry L229] ⇒ `>1MB` 虽跳哈希但仍产条目，且会吃掉 `limit=60000` 配额，反把仓内真文件挤成 blind；
  4. 违反 §4 全资产净零（逐件枚举冷档案 vs 族级一行）。
- **唯一可救的变体**：只做"每盘一条族级资产"（`BAK:F:/zephyr_cold`、`BAK:G:/backup` + `files_on_disk` aux），但那本质是路线一的子集（少了几条 INFRA-STORE 粒度、且仍要新采集器才不被自裁）。

### 推荐：**路线一**

理由三条：① 它是**唯一**能让资产在图书馆里"活下去"的姿势——采集器每轮复现 ⇒ 免疫 ghost 自裁（F 盘那条死账就是反例实证）；② 复用现成空置设施（BAK/INF kind、基建与备份馆谓词、`REG:` 册文件资产、logs_collector 的条目锚定先例），零新增馆/gate/册，合 §4 净零；③ 顺带把根宪法 §7 的 `INFRA-STORE-003` 从"查不到的悬空引用"变成可借条目，命中 A0 的真实痛点。
落地次序建议：等被禁文件所在在途会话落地后再动 `collectors/__init__.py`（一行改动，冲突面极小），新建 collector 本身可先行。

---

# 【B】Qoder "模型上下文协议服务器" 现状

## B1. 实际生效的配置文件在哪

| 层 | 路径 | 内容 | 证据 |
|---|---|---|---|
| Qoder CLI 用户设置 | `C:\Users\fanzi\.qoder-cn\settings.json`（152 B） | **仅** `enabledPlugins` 三键：`qoder-context@qoderapp-bundler`、`polarmem0@qoder-marketplace`、`duckdb@qoder-marketplace`（均 true）。**无 `mcpServers` 键 ⇒ 用户自定义 MCP server 数 = 0** | [亲验] cat |
| 插件自带 MCP 定义 | `C:\Users\fanzi\.qoder-cn\plugins\cache\qoderapp-bundler\qoder-context\1.0.61.d5594762\mcp.json` | 全仓唯一一份 `mcpServers` 声明：server `qoder-context`，stdio 起 `${QODER_NODE_RUNTIME} runtime/qoder-search.bundle.mjs mcp-bridge`，`startup=application`、`timeout=600000`、`alwaysAllow=["SearchKnowledge"]`、`toolOverrides.SearchKnowledge.exposedName="SearchKnowledge"/alwaysLoad=true` | [亲验] cat + `grep -rl mcpServers`（排除 logs/host-actions/file-history 后**只命中 qoder-context 的 4 个缓存版本**） |
| 运行时路由句柄 | `C:\Users\fanzi\.qoder-cn\mcp-router.json` | `{schemaVersion:2, pid:19284, baseUrl:"http://127.0.0.1:34685", apiKey:<明文，本案卷刻意不转录>, startedAt:1790272367565}`。**活性实测**：pid 19284 = `"Qoder CN.exe"` 存活（837,312 K）；TCP 127.0.0.1:34685 **open**；startedAt = **2026-09-24T17:52:47Z**（本地 09-25 01:52）⇒ **不是陈旧句柄** | [亲验] cat + tasklist + socket connect_ex + 时间换算 |
| 项目级 Qoder MCP | `D:\ZephyrAlpha\.mcp.json`、`.qoder\mcp.json`、`.qoder\settings.json`、`.trae\mcp.json` | **全部不存在 ⇒ 项目自定义 MCP server 数 = 0**。（`.qoder\` 下只有 `worktrees\`，13 个 `agent-general-purpose-*`） | [亲验] 逐个 `-f` 探测 + ls |
| 项目自研 MCP Gateway 册 | `D:\ZephyrAlpha\config\mcp.json`（11,619 B，`version 1.0.0`，自述"mod_inf_013 §12 SSoT"） | **12 个 servers**：task_manager / gate_engine / session_handoff / intent_router / blueprint_search / sandbox / governance / telemetry / vector_memory / red_blue_validator / rule_discovery / clone_guard + gateway/rate_limit/circuit_breaker/audit/auth(RBAC 三角色×acl_by_server)。**这不是 Qoder 读的配置文件**——它的消费方是仓库自己的 `src/zephyr/library/collectors/mcp_collector.py`（`_MCP_JSON = "config/mcp.json"`，产 `TOOL:mcp:*` 资产 29 条 active）。12 个 server 中**无一个出现在已连的 83 个工具里** | [亲验] cat + mcp_collector.py L32 + mcp_list 比对 + 总账 kind=mcp_tool 计数 |

## B2. 现在连了哪些 MCP 服务器（`mcp_list`，total=83 工具）[亲验]

| 命名空间 | 工具数（按列表点算） | 内容 | 来源 |
|---|---|---|---|
| `mcp__plugin_qoder-qmind__*` | 6 | retrieve / list_notebooks / list_sources / get_source / read_source / add_source | 插件（QMind 知识库） |
| `mcp__plugin_sites_qoder_sites__*` | 48 | Sites 全生命周期：prepare_site/publish_site/show_publish_confirmation、storage、database+migration、functions、secrets、analytics、audit、access policy…（含写资源型） | 插件（Qoder Sites） |
| `mcp__builtin__*` | 7 | create/read/list/wait/send/fork chat session + `qoder_cron` | 内置 |
| `mcp__browser-use__*` | 17 | navigate/click/fill/snapshot/screenshot/evaluate_script/network/console 等 | 内置（应用内浏览器） |
| `mcp__node-repl__*` | 5 | node_repl / wait / cancel / reset / add_node_module_dir | 内置扩展 |
| `mcp__extension-market__*` | 2 | search_extensions / install_extension | 内置（市场） |
| （不在 mcp_list 内）`SearchKnowledge` | 1 | qoder-context 插件经 `toolOverrides.exposedName` 暴露 | [亲验] 出现在本会话工具面、但 mcp_list 83 条无此名 ⇒ [推断] 走插件工具覆盖注册而非 router 枚举 |

**`enabledPlugins` 里的另两个不贡献 MCP**：`duckdb@1.0.0` 目录实含 `LICENSE/README.md/skills/{attach-db,convert-file,duckdb-docs,install-duckdb,query,read-file,read-memories,s3-explore,spatial}`——**纯 skills 包，无 mcp.json** [亲验]；`polarmem0` 同属技能型插件 [推断]。

## B3. 异常登记（事实 + 建议修法，**未动任何配置**）

| # | 事实 | 判定 | 建议修法（供 Owner 决策，本会话不执行） |
|---|---|---|---|
| E1 | `mcp-router.json` 内 **apiKey 明文**驻留用户目录 | **安全卫生问题，非损坏** | 值未转录进本案卷。Owner 决定是否轮换；权限收紧由 OS 侧做。**禁手改**（运行时句柄，进程重启自覆） |
| E2 | qoder-context 插件缓存 **4 份**：`1.0.42.c363cdb`、`1.0.51.fa026ec3`、`1.0.61.7f8d7bb7`、`1.0.61.d5594762`；`installed_plugins_v2.json` 指向 `1.0.61.d5594762`，该目录 mcp.json 内 `QODER_SEARCH_BUILD_ID="1.0.61.d5594762-win32-x64"` **自洽** | **无配置损坏、无空条目、无重复键**；仅缓存堆积（3 条陈旧，含同版本双 build hash 兄弟 `7f8d7bb7`） | 若要回收磁盘，走 Qoder 插件卸载/清理通道；**不要**手删 cache 子目录（`1.0.61.7f8d7bb7` 版本串与活动版同前缀，按版本前缀解析的选择器有踩错风险 [推断]） |
| E3 | **清单与在线能力不一致**：`installed_plugins_v2.json` 只登记 3 个插件，而 mcp_list 显示 `qoder-qmind`、`sites` 两个 plugin 前缀服务器在连（`C:\Users\fanzi\.qoder-cn\app\` 顶层只见 `bundled-resources`） | 疑为**内置 bundler 不经用户 v2 清单登记**，非损坏 | 以 Qoder UI 插件页核对二者来源；**勿手改 installed_plugins_v2.json**（改坏会让真插件失效） |
| E4 | 项目 `config/mcp.json` 内部字段漂移（与 Qoder 无关，但同属"MCP 配置"）：`task_manager/gate_engine/session_handoff/intent_router/blueprint_search` **缺 `status` 字段**（其余 7 个标 `implemented`）；`rule_discovery` **缺 `version`**；两处 `module != server_id` 已用 note 留痕（`doc_guard_server`→`session_handoff`、`sentinel_server`→`intent_router`） | 轻微 schema 不齐；无重名 server、无空 `servers` 项 | 走仓库侧通道补登记（该文件是他队注册册消费方 `mcp_collector.py` 的真源之一），用 `lookup mcp --kind mcp_tool --limit 40` 复核 `未注册_mcp.json`/`无契约` tags 后再改 |
| E5 | 已连服务器中**不存在仓库内 12 个自研 MCP server 任何一个**；亦无 duckdb/polarmem0 MCP 工具 | 现状即"零用户/项目自定义 MCP 接入" | 如需在 Qoder 里接入 `rule_discovery`/`clone_guard`/`governance` 等（根宪法 §0.4、§1 补充铁律点名的逃生/门位通道），须新增用户或项目级 `mcpServers` 条目；**本会话按纪律未做**。可用 `/mcp-config` 技能（已挂载）交互式落地 |

**B 一句话结论**：当前 Qoder 侧**没有任何用户或项目自定义 MCP server 条目**（`settings.json` 无 `mcpServers`、项目内 `.mcp.json`/`.qoder/mcp.json` 均不存在），已连 83 工具全部来自内置（builtin/browser-use/node-repl/extension-market）+ 插件（qmind/sites + qoder-context 的 SearchKnowledge）；生效配置是 `C:\Users\fanzi\.qoder-cn\settings.json`（启用面）+ `…\plugins\cache\qoderapp-bundler\qoder-context\1.0.61.d5594762\mcp.json`（唯一 mcpServers 声明）+ `…\.qoder-cn\mcp-router.json`（运行时句柄，pid 19284 与 127.0.0.1:34685 实测存活）；**配置未损坏、无空条目、无重复键**，异常仅两项：apiKey 明文驻留、qoder-context 3 份陈旧缓存（外加 installed_plugins_v2 与在线 plugin 服务器不一致的来源待核）。

---

## 附录：复现命令（全部只读）

```bash
python --version
PYTHONPATH=src python -m zephyr.library.lookup 冷储 --limit 8
PYTHONPATH=src python -m zephyr.library.lookup backup --limit 8
PYTHONPATH=src python -m zephyr.library.lookup INFRA-STORE        # 0 命中
PYTHONPATH=src python -m zephyr.library.lookup asset_inventory --kind module
# 总账口径（经 sanctioned PG 连接，非裸 duckdb）
PYTHONPATH=src python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g; c=g(); cur=c.cursor(); cur.execute(\"SELECT kind,status,count(*) FROM lib_assets GROUP BY 1,2 ORDER BY 1,2\"); [print(r) for r in cur.fetchall()]; c.close()"
sed -n '40,70p' scripts/governance/generators/generate_library_index.py   # L58 馆谓词
sed -n '20,60p' src/zephyr/library/collectors/fs_collector.py             # _SCAN_ROOTS
```

## 未做 / 边界声明

- 未跑 `git`（含 `git status`）、未跑 `lock_files.py`、未申请任何 claim、未写除本案卷外的任何文件。
- 领地：`library_regen_reconciler.py`、`reconciliation_registry.py`、`library_new_module_reconciler.py`、`project_handbook` 族、`capability_canonical_file_registry.yaml`、`module_translation_registry.yaml` —— **只读**，且 A5 推荐路线**不需要修改它们**。
- `docs/library/regulations.md` 的生成归属、`storage_map.md` 与 `backup_inventory.md` 的内文口径差、以及 `F:/G:` 盘面实况（未挂载探测）**均未展开**，属本次范围外。
