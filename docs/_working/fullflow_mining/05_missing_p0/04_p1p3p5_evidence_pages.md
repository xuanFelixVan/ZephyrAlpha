---
ttl: task_bound
volume: 04_p1p3p5_evidence_pages
session: st-ailayer-final-20260924
creation_token: fullflow-p0-p1p3p5-evidence-20260926
---

# 05_missing_p0/04 · P-1／P-3／P-5 件级比对取证三页（波3 取证工单回执册）

> 派单真源＝`../94_chief_rulings_wave2.md` §一（三案均判"c＝证据不足"，明写须补件级比对才能定环节终数）。
> 被测行＝`00_verification_table.md` 主表 B-9 残余（P-1）、D-12（P-3）、D-5（P-5）。
> 车道＝挖矿 W4-C；工作面 worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`。
> **只读取证**：零施工、零生产代码/配置改动、零热册改动、零 depgraph/PG 写、零提交、零入队、零 claim。
> 取证口径＝每格证据给 `file:line` 或**可复跑命令**（§五）；两源交叉＝E1 代码实扫 ＋ E2 注册表/地图册（F 册＝`00_skeleton/00_全环节总册.md`；域册＝`functional_domain_registry.yaml`）。
> 本册**不自赋裁定号**、不作任何 Owner 背书署名；退役项**只出判据与清单不删**（注册表净删＝Owner 门位，宪法 §5.2）。

## 一、P-1 · schema 版本化迁移是否独立环节（三向证据）

### 1.1 向一：谁触发迁移（E1 实测）

| 平面 | 迁移执行件 | 触发面实测 | 证据 |
|---|---|---|---|
| PG 架构库 | `apply_pg_schema()` | **有版本化入口、零调用方**＝人工/无自动触发器 | `src/zephyr/governance/depgraph_schema.py:1739`；全仓 `grep -rn "apply_pg_schema"` 仅命中定义 :1739 ＋ `__all__` :1853（§五 C-1） |
| PG 架构库 DDL 真源 | `02_create_pg_schema.sql`（幂等 CREATE IF NOT EXISTS） | 被上函数字面读取 | `depgraph_schema.py:1736 _PG_SCHEMA_SQL_PATH` |
| 一次性加列迁移 | `scripts/governance/migrations/add_acquisition_fields.py`（`nodes_metadata` 加两列＋枚举 CHECK） | `[STARTUP] manual`，但**提交后自动备份**（事件触发，合规） | 头注 :6／:120；调用 `backup_pg_architecture()` @:176 |
| CH 热库 | `scripts/ch/apply_*_ddl.py` ＝**24 枚**（实测计数） | **全部 manual、`[CONSUMERS]` 空**：实测 `grep -l "[STARTUP] manual" scripts/ch/apply_*.py`＝27/27（含 3 枚非 _ddl） | `apply_market_tables_ddl.py:5-6`、`apply_pf_alloc_ddl.py:6-7`、`apply_timezone_migration.py:5-6` |
| CH 时区专项迁移 | `apply_timezone_migration.py` 五阶段（system/version-col/business/recreate/tickdata） | `--dry-run`/`--verify`/`--phase` 人工三态；自称"全库 DateTime 时区统一化的**唯一执行链路**" | 头注 :8 INVARIANTS；`capability_canonical_file_registry.yaml:29899`、`module_translation_registry.yaml:2968` |
| **校验面（真在拦）** | `verify_schema_health.py`（INVARIANT："depgraph_schema.py 是 DDL 真源；DB 物理状态必须与 DDL 声明一致"） | **挂在合并门禁 GATE-C2 的 entry 里带 `--ci`**，且该 gate 的 `files_trigger` 含 `src/zephyr/governance/depgraph_schema\.py`＝**改 DDL 真源即自动跑 schema 健康校验** | `gate_registry.yaml:469-477`（GATE-C2，entry 第三行 :473）；文件头 :6/:9；`script-manifest.yaml:3441` |
| 同上 | `check_schema_version_writes.py`（`[CONSUMERS] G_TRAE_059 gate`） | 被规则执法册当**验证方法**消费（非 gate_registry） | `src/zephyr/gov_enforcement/rule_enforcement/g_trae_059.yaml:45`＋`:69`（`verification_method: python scripts/governance/d3_metadata/check_schema_version_writes.py`）；规则真源 `docs/01_policies_and_standards/rules/trae_059_schema_version_write_protection.yaml`；被引侧 `depgraph_schema.py:874/:1326/:1369` |

### 1.2 向二：迁移台账真源在哪（三处并存，含一处自相矛盾）

| 台账 | 实态 | 证据 |
|---|---|---|
| PG `_schema_version` 表 | **存在且被写入**（version/applied_at/description，ON CONFLICT DO NOTHING） | DDL 常量 `depgraph_schema.py:564 _DDL_SCHEMA_VERSION`；写入 :1761-1766；表清单 `:38` |
| PG `_MIGRATIONS` 版本列表 | 存在，注释自证用途＝"本列表保留以支持 `check_schema_version_writes.py` / `verify_schema_health.py` 引用版本号元数据"，且"不再执行"；另 `:1326-1327` 明写两把尺各引哪个接口 | `depgraph_schema.py:872-877`（含 `:67` v5/v11 历史 SQL 记录注） |
| `migrate_sqlite_to_pg/00..12_*.sql`（实测 15 个编号 SQL） | **无表登记**，且原文自称"本项目无 schema_migrations 表，迁移元数据通过 git commit log 追踪" | `05_fix_guc_trigger_bug.sql:93-99` → **与上一行同库两套口径＝病灶 V-P1-1** |
| CH 侧 applied 台账 | **不存在**（各 `apply_*_ddl.py` 只 IF NOT EXISTS 幂等，无版本/无 applied 记录）＝病灶 V-P1-2 | §五 C-4 实测；`apply_decision_daily_ddl.py:35` |
| `migration_registry.yaml` | 二次确认＝**代码目录重命名台账**（ARCH-031），条目字段 old/new_module，`deprecated`/`frozen`/禁新增／`ai_read_only`；`[CONSUMERS] scripts/migration/governance_root_split.py, dm311_autonomy_core_split.py…` | 册头 `:1-14` → **与 DB schema 无关**（对账表 V-2 定性成立，B-9 依据证伪维持） |
| 域册侧登记 | `D_INFRA_RUNTIME/persistence`（`SH-DB-001`，`ssot_path: src/zephyr/data/persistence/`）covers 明写 **"SQLite DDL Schema(v1-v8 迁移)"** → 迁移语义在**域面有位** | `functional_domain_registry.yaml:604-614` |
| F 册侧登记 | F 册全文 `grep 迁移`＝**0 命中**；DDL 只出现在 **F06**（`:31`），建表在 **F02**（`:27`），版本列 `_MIGRATIONS` 无任何 F 位 | §五 C-5 |

### 1.3 向三：回滚路径（E1）

| 通道 | 实态 | 证据 |
|---|---|---|
| 迁移前/后自动备份（PG） | **已自动化且事件触发**（trae_054 v1.6.0 STEP0），`backup_pg_architecture()` 被 6 处写路径调用：`apply_depgraph.py:6150`、`apply_battle_map.py:656`、`apply_dataflowgraph.py:146`、`apply_decisiongraph.py:727`、`generate_project_depgraph.py:4563`、`migrations/add_acquisition_fields.py:176` | `scripts/governance/meta/backup_runtime_state.py:294`；`:129` 节流病根注 |
| 显式 downgrade SQL | `scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema_down.sql` 在盘（实测 ls，唯一一枚 down 脚本） | §五 C-3 |
| CH 侧 | **明写不回滚**："已建不回滚（IF NOT EXISTS）" | `apply_decision_daily_ddl.py:35`、`apply_pf_alloc_ddl.py:37` |
| F107 回滚恢复环 | 对象＝**业务态/任务态**四级回滚＋checkpoint，不持 schema DDL 回滚（其 verifier 读 `sqlite_schema._DDL_TASKS` 状态词） | F 册 `:182`；`src/zephyr/infrastructure/rollback/rollback_verifier.py:45-94` |

### 1.4 P-1 判定

**并 F06／F07 子目补锚（不立独立环）**，另开两条**登记面欠账工单**（V-P1-1 双口径矛盾、V-P1-2 CH 无 applied 台账）。
理由（第一性＋w5_1）：全流通四要素逐条核——入口触发器（校验面 gate 自动／应用面 manual，与 F02/F06 现环节同档，不构成新要素）、出口真源（`_schema_version`＋`02_create_pg_schema.sql`＋`schemas/categories/**` 实测 223 py 三者皆已有主）、真源唯一（PG 面唯一，CH 面缺的是"登记"不是"环节"）、自动化程度（gate 侧已接、备份侧已事件触发）→ 迁移是 F06（CH DDL 应用）与 F07（PG 架构库 DDL 真源）同一真源的**派生动作**，按"同真源可派生→必并"不得独立成环。
**置信度＝中高**：三向各两源齐；未做的一件事＝连生产 PG 实读 `_schema_version` 行数（禁触生产 DB，属本车道边界），故"台账实际是否有人在写"未证。

### 1.5 若判错，代价是什么

| 误判方向 | 代价（可量化） |
|---|---|
| 误立独立环（同物判异物） | 122→N 的集合多一员且**永久**：此后每次改列/建表须在 F02、F06、F07、新环四处登记环节归属；depgraph 设计节点＋ROOR＋翻译册三绑同步成本 ×4；并与本案卷 B-9 已定的"P0① 依据证伪"自相矛盾→治理账面可信度受损（对账表 V-2 的教训反噬） |
| 误只补锚、掩掉 CH 缺陷（异物判同物／轻判） | CH 下一次时区级重建（`apply_timezone_migration.py` 五阶段：125 列类型标注＋17 表版本列重建＋20 表键列重建＋181GiB 分区批量重建）**仍无版本闸门、无回滚点**，失败面＝数据不可逆。→ 所以"并子目"必须与 V-P1-1/V-P1-2 两单**同批下达**，不可只补锚 |

## 二、P-3 · `src/zephyr/infra_runtime`（8 实体件/2,203 行）与 F71 AutoRuntime Core 是否同物（逐件比对）

### 2.1 两件对照（本体）

| 面 | F71 AutoRuntime Core | infra_runtime 包 |
|---|---|---|
| 真源 | `src/zephyr/trading/auto_runtime_core.py`（63,058 B；`class AutoRuntimeCore:102`），F 册 `:126` | `src/zephyr/infra_runtime/*.py` 8 件 2,203 行（实测 `wc -l` 2,259 含 `__init__.py` 56 行） |
| 职责 | **装配根/组合器**：`boot()`@:308、组件属性（fle_scheduler/local_scheduler/vms/registry/night_shift_queue/dream_cycle/health_monitor/task_learner/ollama_chat/embedding_router）@:184-302、"监控/调度/自愈"三层运营接口位 @:679-700 | **可复用底座构件库**：纯内存裁决，时钟/executor/告警全注入（8 件 `[DEPENDENCIES] 无` 一致） |
| blueprint | MOD-INF-035（@:1） | MOD-INF-074/075/076/077/078/079/080（逐件头注 :1） |
| 生产消费者 | 全链（`python -m zephyr.trading`；`feedback_loop/core.py:5`、`scheduler.py:5` 声明消费） | **零**（跨包 `grep "zephyr\.infra_runtime"` 在 src/scripts 中只命中 `check_pure_shim.py` 的注释文本；其余命中全在本包＋`tests/infra_runtime/` 8 件测试）＝§五 C-7 |
| 互引 | 未 import infra_runtime 任何件（`resource_optimization` 是其 DEPENDENCIES 之一，非本包） | 全部头注 `[CONSUMERS] 运行时装配批`＝**指向尚未落地的装配批** |

### 2.2 逐件表（每件：职责／入口／谁 import／与 F71 及 F13 是否重叠）

| 件（行数） | 职责一句话 | 入口 file:line | 谁 import 它（实测） | 与 F71 重叠 | 与 F13（MOD-BT-151）重叠 | 最近既有环 |
|---|---|---|---|---|---|---|
| `resource_scheduler.py`(301) | Hot/Warm/Cold 三平面 CPU 核亲和＋内存预算＋QPS 令牌桶的**资源维准入裁决** | `:63 ResourcePlane`、`:72 PlaneQuota`、`:82 ResourceRequest` | 仅 `tests/infra_runtime/test_resource_scheduler.py:26`＋同包 `runtime_admission` | 无（F71 无平面/配额码） | **不重叠（重点核项，见 §2.3）** | F80/F13 族（资源维） |
| `runtime_admission.py`(385) | 三件配额合成准入：并发/WIP←`orchestrator.governance.capacity_budget`、令牌桶←`shared.capacity_governance.api_cost_governor`、内存/空间←`resource_scheduler`；池词表真源＝`config/resource_profile_registry.yaml` | `:143 build_runtime_quotas`、`:93 PoolQuota`、`:120 AdmissionResult` | 仅 `tests/…/test_runtime_admission.py:28` | 无 | 部分（同"问闸放行"语义，维度不同） | **F80 资源画像与排班**（同册 `:145`；头注自称"排班表运行时下半身"） |
| `ha_sla_framework.py`(316) | 单机进程 SLA 登记＋健康探针编排＋连续失败触发注入式 restart（冷却期抑制）；明写"严格单机不做集群" | `:61 SlaTarget`、`:70 ProbeResult`、`:81 RestartEvent` | 仅测试 :26 | 部分接口位同名词（`health_monitor`），代码零重叠（auto_runtime_core `grep ha_sla\|probe`＝0 命中） | 无 | F81 监控告警（`:146`）子目 |
| `latency_budget_allocator.py`(237) | Hot=10ms/WARM=1000ms 端到端预算分解登记＋实际耗时上报＋消耗率报表 | `:64 Plane`、`:79 StageBudget`、`:87 BudgetTable` | 仅测试 :28 | 无 | 无 | **无位**（F 册 `grep SLA\|准入\|零拷贝` 只命中 F24/F98，不同对象） |
| `cold_plane_isolation.py`(287) | Cold 平面配额闭合校验（核⊆16-19／≤20GB／BelowNormal IO／iFind≤5QPS）＋通道白名单（Cold→Warm 仅 `config:*` 30s）＋盘中产出盘后激活 | `:84 Plane`、`:92 PendingStatus`、`:100 ResourceQuota` | 仅测试 :28 | 无 | **1/4 重叠**：两者都读交易时段；F13 管"何时能干"，此件管"在哪个平面干" | F80/F13 族 |
| `database_layer.py`(233) | sqlite/duckdb/pg/clickhouse 后端注册＋统一查询路由门面＋借还计数＋重试（注入 sleeper） | `:57 DbBackend(Protocol)`、`:81 DatabaseLayer` | 仅测试 :29 | 无 | 无 | **与宪法"DatabaseService 唯一真源"（AGENTS §7）门面重复**＝登记为病灶 V-P3-2 |
| `shared_memory_zero_copy.py`(259) | 42 万条因子值跨进程 `multiprocessing.shared_memory` 零拷贝通道＋生命周期单向＋越界拒＋超阈降级 fallback | `:60 ChannelState`、`:70 ChannelInfo` | 仅测试 :30 | 无 | 无 | 无位 |
| `ml_pipeline_process.py`(185) | P5 ML 管线进程四职责（inference/training/vram_mgmt/model_version）任务队列＋交易时段 training 退让＋GPU 夜间互斥 | `:72 TaskKind`、`:92 MlPipelineProcess` | 仅测试 :28 | 无 | 无 | **F68 GPU 矩阵/工厂格子**（`:123`，`gpu_consensus_scheduler.py`）子目 |

### 2.3 重点核项：F13 拉式闸门 vs `resource_scheduler.py` 疑同功能 —— **判为不同维，不重叠**

| 比对项 | F13 `scripts/backtest/compute_window_gate.py`（MOD-BT-151） | `resource_scheduler.py` |
|---|---|---|
| 判定输入 | 交易日日历 `is_open`＋收盘缓冲 15:30＋`--compute-class heavy/light`（`:22-28`） | 平面核集／内存 GB／QPS 令牌桶（`:8-13` INVARIANTS） |
| 是否含资源量纲 | **实测零**：`grep "mem\|core\|affinity\|qps\|plane\|GB"` 该文件＝**0 命中**（§五 C-8） | 全部三量纲皆有 |
| 触发形态 | 纯拉式（`:10` INVARIANTS："事件=任务到点开工前来问，本模块无常驻循环"），`[STARTUP] manual`，MATURITY=**experimental** | 库件（`[STARTUP] imported`），MATURITY=**production**，同输入必同输出 |
| 输出契约 | `SystemExit(0/3/1)`（CLI） | `ResourceSchedulerError(ZA-INF-0010)`＋拒绝留痕不抛（`:13`） |
| 域 | `D_BACKTEST` | `D_INFRA_RUNTIME` |
⇒ "疑同功能"仅在**词面**（都叫"闸门/准入"）成立，量纲正交：**F13＝时间维能不能开跑；resource_scheduler＝资源维放不放得下**。合并二者会让日历闸背上核亲和不变量（其 INVARIANTS 有"亲和核须为平面核子集且平面内独占"），属跨域不同对象→按 w5_1 判据④**不并**。

### 2.4 "同物嫌疑"的真病灶（E2 决定性证据）

`functional_domain_registry.yaml:343-351`：`domain: D_INFRA_RUNTIME / subdomain: runtime_core`，**`ssot_module: MOD-INF-035`（＝auto_runtime_core 的 blueprint）却配 `ssot_path: src/zephyr/infra_runtime/`**，covers＝"三层运行时编排(L1 Trae/L2 Local/L3 API)／节律调度(circadian_scheduler)／健康监控／工作编排(work_dag)"＝**逐条都是 F71 的职责**。同域另有第二条 `:759-772`（`MOD-INF-002`，同 `ssot_path`）与第三条 `:604`（persistence）。
⇒ 结论：上一棒"infra_runtime 与 F71 疑同物"的**唯一来源是域册登记错配（module↔path 绑错＋同 path 三条目）**，不是代码重叠。＝病灶 **V-P3-1**（域册是热册，本车道只登记不改，修法归总筹：把 `:346` 的 ssot_module 与 `:347` 的 ssot_path 二选一重绑，并合并 `:343/:759` 同域重复条目）。

### 2.5 P-3 判定

**F71 与 infra_runtime 不是同物**（装配根 vs 底座库，双向零 import 可复跑）。
**但也不建议新开"运行时底座/准入与 SLA"环**：8 件里 4 件（resource_scheduler／runtime_admission／cold_plane_isolation／latency_budget_allocator）与 F80 同真源族（`config/resource_profile_registry.yaml`，实测 1,785 行/64KB，生成器 `generate_resource_profile_registry.py`；F 册 `:260` 已把该册定为触发器登记真源）→ **并 F80 子目补锚**；`ha_sla_framework`→F81 子目、`ml_pipeline_process`→F68 子目、`shared_memory_zero_copy`→F71 待接线底座（补锚不占环）、`database_layer`→**门面重复待收敛**（不补锚，先裁 V-P3-2）。
共同前置事实：全 8 件 `[CONSUMERS] 运行时装配批` **未落地**、跨包生产 import＝0 → 立环＝**给未接线代码发环节身份证**，环的"入口触发器"要素实测为空。
**置信度＝高**（逐件三向证据＋零 import 硬尺＋域册错配双证）。

### 2.6 若判错，代价是什么

| 误判方向 | 代价 |
|---|---|
| 误并 F71（异物判同物） | F71 变"装配根＋8 件底座"混合环；`auto_runtime_core.py:9` 头注 `[MODIFY-GUARD] no structural changes without owner approval` 会**沿环传染**到底座件（现 8 件皆 `ai_modifiable`／`human_gated`，非 Owner-only）→ AI 施工权被错误连坐；`god_class_gate.py:26` 已盯 auto_runtime_core 方法数，合并后环级复杂度账面失真 |
| 误立新环（同物判异物／或拿"代码存在即环节"当判据） | N 直接 ＋1，且**每条新资源腿要在 F13/F80/新环三处登记**（环节集合永久污染，正是本案卷 V-10 假漏项的成因复现）；后续退役成本远高于现在补锚 |
| 误按"零消费"整体退役 | `runtime_admission` 已实依赖 `capacity_budget`/`api_cost_governor` 两真源＋带 8 件测试（实测 `find tests/infra_runtime -name "*.py"`＝8，一模块一对），退役＝毁掉已完成的排班"下半身"施工面；故退役建议只对 **database_layer 门面**单件提，且不删 |

## 三、P-5 · `src/zephyr/market_data` 与 F03 Provider 源路由／F10 行情订阅是否双真源（件级重叠表）

包实测：20 py（9 实体件）／**3,323 行**（`wc -l` 合计；子包 `connectors/ normalized_market_data_producer/ raw_data_cache/ failover/ api/ core/ models/ services/ infrastructure/_extensions/`，其中 6 个子包实测各只有 26 行 `__init__.py`＝**空壳占位**）。

### 3.1 件级重叠表

| 件（行数） | 职责一句话 | 入口 file:line | 生产消费者（实测） | 与 F03（`data/implementations/`＋`provider_base`）/F10（`data/scheduler.py`）关系 | 分类 |
|---|---|---|---|---|---|
| `normalized_market_data_producer/producer.py`(363) | 从 CH `c1_market.kline_daily` 读日 K→构造 CTR-001 `NormalizedMarketData`（frozen/Decimal）供下游；PIT 铁律：ch_reader 注 FINAL、只用 trade_date 截面对齐 | `:271 load_kline`、`:309 produce` | **真 import 两件**：`src/zephyr/ex_sor/core/market_context_provider.py:64`；头注 CONSUMERS 另列 `factor/core/ctr001_consumer/converter` | DEPENDENCIES 全在 `zephyr.data.*`（`ch_reader`/`table_registry`/`symbol_normalizer`）→ **F03/F06 之上的读侧供给门面，非第二套真源** | **(a) 补 F 册锚点** |
| `connectors/base.py`(432) | `MarketDataConnector(MarketDataVendor)` ABC＋连接状态机＋订阅注册表（Lock）＋callback 异常隔离 | `:54 ConnectionState`、`:126 MarketDataConnector` | **零**：头注 :5 自证"2026-09-05 AI-04 审计实证：**D_EX_SOR 声明删除——ex_sor 全域无 import**"，仅 `tests/market_data/connectors/test_connector_base.py:29` | **与 F10 同域重复簇**（tick 订阅/分发语义两处抽象：F10 真源 `data/scheduler.py`＋`sch_tick_subscriber`；本件是未接线骨架） | **(b) 向 F10 收敛（子目补锚＋标未接线）** |
| `connectors/manager.py`(219) | 连接器注册表单表＋`_connectors: dict[str,MarketDataConnector]` 读写加锁、connector_id 唯一 | `:45/:51` 错误类 | 头注 CONSUMERS＝`D_EX_SOR`（已被上一条自证删除） | 同上 | (b) |
| `failover/manager.py`(421) | 厂商故障切换策略（Enum Policy/Reason）＋切换原子（先确认目标可用）＋同 vendor 不自切 | `:54 FailoverPolicy`、`:61 FailoverReason` | **零**：头注 :5 自证"AI-04 实证：D_EX_SOR 接线**未落地**——ex_sor 全域无 import，`integration/failover_coordinator` 仅注释提及" | F03 的"源路由"含**降级/换源语义**（`data/policy_registry.py:8` "策略 yaml 是真源，DEFAULT_POLICIES 是 fallback"）→ 语义交叠，但 F03 侧真源是 yaml 策略册，本件是空跑骨架 | (b)＋与 F03 策略面**先比对再收敛** |
| `vendor_base.py`(185) | `MarketDataVendor` ABC＋VendorStatus 枚举（厂商抽象基类） | `:78 MarketDataVendor` | 仅同包（`vendor_registry`/`connectors`） | 与 `data/provider_base.py:IngestProviderBase`（CONSUMERS＝`data.scheduler`＋`data/implementations/*_provider`，**26 枚 provider 在册**）＝**同一抽象的第二套**，且第二套零注册 | **(c) 历史拆分残留→退役评估建议** |
| `vendor_registry.py`(201) | 厂商注册表（VendorAlreadyRegistered/NotFound 错误族） | `:43/:49` | **全仓零 vendor 注册**：`grep "register_vendor\|VendorDefinition\|vendor_id"` 排除本包＝**0 命中**（§五 C-11） | 同上 | (c) |
| `autoload.py`(208) | 厂商/连接器自动装载 | `:48 AutoloadError` | 头注 :5 自证"**zephyr.market_data 包入口实际未 import 本模块，生产装配待排期**"，仅测试消费 | 同上 | (c) |
| `raw_data_cache/cache.py`(422) | 原始报文 LRU＋TTL 双淘汰＋content_hash | `:52 EvictionPolicy` | 头注 :5 自证"normalized_market_data_producer **未 import** 本模块，生产装配待排期" | 与 `data/tick_redis_cache.py:132 TickRedisCache`＋`infrastructure/h1_redis_hot/*`（F10 供数缓存）**同域重复**（w5_1③） | (c) 或并入 F10 缓存子目，二选一待总筹 |
| `auction_data_manager.py`(497) | A 股集合竞价数据管理（D-DATA-32→MOD-MKT-007；B10/B13 两案归并） | `:93 AuctionSession`、`:76/:82` 错误类 | 头注 CONSUMERS 列两下游（MOD-SIG-089 auction_microstructure_analyzer／MOD-PLAN-015 auction_hit_recorder）＋`[STARTUP] manual`；**F 册 `grep 集合竞价\|auction`＝0 命中**（§五 C-12） | 与 F03 侧 `data/implementations/ch_auction_derive.py` 同族；F 册**整条数据线无位** | **(a) 补锚＋候选环节内缺口**（本波未做 auction 件级归属，见 §六） |
| 6 个子包 `api/ core/ models/ services/ infrastructure/ _extensions/`（各 26 行） | 仅 `__init__.py` 占位 | — | 零 | 与 F03/F10 无对象可叠 | (c) 空壳，登记即可 |

### 3.2 专项：`normalized_market_data_producer` 与 `src/zephyr/data/normalizers` 是否双真源 —— **不是，方向相反**

| 比对 | `market_data/normalized_market_data_producer/producer.py` | `src/zephyr/data/normalizers/`（4 件：`normalizer_base`/`ohlcv_normalizer`/`format_transformer`/`__init__`） |
|---|---|---|
| 数据流方向 | **读侧**：CH→内存 DTO（`load_kline`/`produce`） | **写侧**：provider 落库前字段/格式归一收口 |
| 抽象面 | 无 ABC，函数式＋`NormalizedMarketData`（frozen dataclass，真源 `shared/contracts/market_data.py`） | `DataNormalizer(abc.ABC)`@`normalizer_base.py:54`＋`SchemaSpec/FieldSpec`＋隔离记录 `QuarantinedRecord`@`format_transformer.py:163` |
| 自述 CONSUMERS | `factor.core.ctr001_consumer.converter`＋实测 ex_sor | `format_transformer.py:5` 原文："（P1 接线：scheduler/provider 落库前格式收口）"＝**尚未接线** |
⇒ 二者是"读侧 DTO 构造"与"写侧 schema 收口"，**跨环节不同对象**；真正的"未接线"缺陷在 normalizers 侧（属 F03/F04 环节内缺口，非 P-5 双真源）。同时注意：对账表 D-5 行称 market_data "含 normalized_market_data_producer"，但**域册 `:1472-1480` 已把 `src/zephyr/market_data/` 整包登记为 D_MKT_DATA 的 ssot_path（ssot_module=MOD-L00-002）**，而 F 册 `grep -w market_data`＝0（`:35` F10 用 `data/scheduler.py`）＝**域册有主、F 册无锚**，与 V-P3-1 同类登记断裂。

### 3.3 P-5 判定（三分类，均不推高 N）

- **(a) 实现细节→补 F 册锚点**：`normalized_market_data_producer`（有生产消费者，读侧供给）与 `auction_data_manager`（竞价数据线）→ 挂 F03/F06 读侧子目 ＋ F 册新增"集合竞价数据线"环节内缺口（是否成环另案，本波未取证）。
- **(b) 与 F10 同域重复簇→收敛唯一**：`connectors/*`＋`failover/*` 作为 F10 的"订阅抽象骨架（未接线）"子目补锚，真源仍 `data/scheduler.py`＋`sch_tick_subscriber`；`failover` 与 F03 的 `policy_registry` yaml 降级语义**必须先做条目级比对再谈合并**（本波未做）。
- **(c) 历史拆分残留→按内收判据提退役评估**：`vendor_base`/`vendor_registry`/`autoload`/`raw_data_cache`＋6 个空壳子包，命中 w5_1 判据②"零触发零消费→退役"（判据证据＝三条 AI-04 审计自证 CONSUMERS＋全仓零 vendor 注册＋包入口 `__init__.py:31` 只导出 `NormalizedMarketData` 与模块名）。
  **本车道只出判据与清单，不删**：退役属注册表/模块净删＝Owner 门位（宪法 §5.2），且 `market_data` 在域册有 ssot 条目（`:1472`），删件须与该条目同批处置。
- **双真源结论**：**不成立为"两个平行真源"**——F03/F10 是真在跑的通道（46 py implementations、26 provider、`data/scheduler.py:680 _providers` 注册表），market_data 侧**除 1 件读门面外全是未接线抽象骨架**；真正的缺陷是"骨架并存＋F 册无锚＋域册有主"三面断裂。
**置信度＝高**（三条作者自证 CONSUMERS 带日期与审计案号＋跨包 import/注册双零，均可复跑）。

### 3.4 若判错，代价是什么

| 误判方向 | 代价 |
|---|---|
| 误立"行情规范化与容灾"环（同物判异物） | **三案里代价最高**：与 F03/F06/F10 四分行情面，此后每个新 provider/新订阅腿要两处登记；且把一个 3,323 行中仅 **363 行有生产消费者**的包升格为环节＝确立"代码存在即环节"的坏判据，直接腐蚀 122→N 的尺 |
| 误整包退役（异物判同物／一把切） | 断实盘执行链供数：`load_kline` 被 `ex_sor/core/market_context_provider.py:64` 真实 import，其 INVARIANTS 持 PIT 铁律与 CP-03 门禁（头注 :8）；`auction_data_manager` 有 MOD-SIG-089/MOD-PLAN-015 两下游。→ 退役清单**必须逐件切分**，禁按包名打包 |
| 误判"已收口"（把 (b) 当已接线） | connectors/failover 零注册零 import，若当作 F10 的实现细节关闭，ex_sor 侧未来接 tick 订阅时会**再长第三套骨架**（本案卷 V-6 双同名包同构病灶） |

## 四、三案合并 · N 值影响表（供总筹定 122→N）

基线＝对账表 §三 第 3 项：N＝122＋10＝**132**（宽 137／窄 129）。

| 案 | 对账表现状 | 本波取证后判向 | 对 N 的增减 | 若总筹改判则 |
|---|---|---|---|---|
| P-1（B-9 残余） | 证据不足，未预计入 | 并 **F06＋F07 子目补锚**＋2 条登记面工单（V-P1-1 台账双口径／V-P1-2 CH 无 applied 台账） | **0** | 若立"schema 版本化迁移"独立环 → ＋1（132→133），代价见 §1.5 |
| P-3（D-12） | 证据不足（疑覆盖） | **与 F71 非同物**；4 件并 **F80 子目**、1 件挂 F81、1 件挂 F68、1 件补 F71 待接线锚、1 件（database_layer）门面重复待裁；不立环 | **0** | 若立"运行时底座/准入与 SLA"环 → ＋1（132→133），代价见 §2.6 |
| P-5（D-5） | 不成立（转收敛） | 维持 0；三分类落锚＝(a) 补锚 2 件、(b) 收敛 F10 4 件、(c) 退役评估建议 4 件＋6 空壳（**不删**） | **0** | 若立"行情规范化与容灾"环 → ＋1（132→133），代价见 §3.4（三案最高） |
| **合计** | — | 三案共同结论＝**均不推高终数** | **ΔN＝0 → N 维持 132** | 三案全改判立环的最坏上界＝135 |

附带（本波顺带实测出的**登记面**账，不占 N）：V-P1-1、V-P1-2、V-P3-1（域册 `functional_domain_registry.yaml:343/:346/:347` 与 `:759` 同 path 多模块错配）、V-P3-2（`infra_runtime/database_layer.py` vs `infrastructure/database_service` 门面双真源）、V-P5-1（域册有 `src/zephyr/market_data/` ssot 而 F 册零锚）、V-P5-2（F 册"集合竞价"0 命中）。

## 五、复核命令（全部只读，可在本 worktree 复跑）

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version    # 预期 3.12.x
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
ROOR=docs/registry_of_registries.yaml
DR=docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml
GR=docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml

# --- P-1 ---
# C-1 PG 迁移入口有、调用方零（预期：只命中 :1739 与 :1853）
grep -rn "apply_pg_schema" --include="*.py" src scripts | grep -v __pycache__
# C-2 版本台账三处（预期 _DDL_SCHEMA_VERSION:564 / _MIGRATIONS:877；两条 SQL 注释自相矛盾）
grep -n "_DDL_SCHEMA_VERSION\|^_MIGRATIONS" src/zephyr/governance/depgraph_schema.py
sed -n '93,99p' scripts/governance/migrate_sqlite_to_pg/05_fix_guc_trigger_bug.sql
# 校验面自动化两处（预期 GATE-C2 在 :469-477 且 files_trigger 含 depgraph_schema.py；G_TRAE_059 在执法册）
grep -n "GATE-C2" -A9 $GR | grep -n "verify_schema_health\|files_trigger" | cut -c1-160
grep -rn "check_schema_version_writes" src/zephyr/gov_enforcement/rule_enforcement/g_trae_059.yaml | cut -c1-150
# C-3 down 脚本与备份链（预期 backup@backup_runtime_state.py:294＋6 处调用点）
ls scripts/governance/migrate_sqlite_to_pg/ | grep -i down
grep -rn "backup_pg_architecture(" --include="*.py" src scripts | grep -v __pycache__ | grep -c ""
# C-4 CH 侧 DDL 与 manual 触发（预期 24 枚 apply_*ddl）
ls scripts/ch/apply_*ddl*.py | wc -l; grep -l "\[STARTUP\] manual" scripts/ch/apply_*.py | wc -l
# C-5 迁移册头＝重命名台账（预期 deprecated/frozen/禁新增）；F 册"迁移"0 命中
sed -n '1,14p' docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml
grep -c "迁移" $S; grep -n "^| F06 \|^| F07 \|^| F02 " $S | cut -c1-80

# --- P-3 ---
# C-6 件数与行数（预期 8 实体件/2,203 行）
find src/zephyr/infra_runtime -name "*.py" ! -name "__init__.py" | grep -v __pycache__ | xargs wc -l | tail -1
# C-7 跨包生产 import＝0（预期：仅 check_pure_shim.py 注释文本命中）
grep -rn "zephyr\.infra_runtime" --include="*.py" src scripts | grep -v "^src/zephyr/infra_runtime/" | grep -v __pycache__
# C-8 F13 与 resource_scheduler 量纲正交（预期第一条 grep 输出为空＝无 mem/core/qps/plane）
grep -n "mem\|core\|affinity\|qps\|plane\|GB" scripts/backtest/compute_window_gate.py
grep -n "\[INVARIANTS\]" -A5 src/zephyr/infra_runtime/resource_scheduler.py | head
# C-9 域册错配（预期 :343/:346/:347 三行；:759 第二条同 path）
sed -n '343,352p;759,765p' $DR
# C-10 资源画像册与 F80（预期 1785 行册＋F 册 :145 与 :260）
wc -l < config/resource_profile_registry.yaml; grep -n "^| F80 \|resource_profile_registry" $S | cut -c1-140

# --- P-5 ---
# C-11 全仓零 vendor 注册（预期 0 输出）
grep -rn "register_vendor\|VendorDefinition\|vendor_id" --include="*.py" src scripts | grep -v "^src/zephyr/market_data/" | grep -v __pycache__
# C-12 三条 AI-04 自证 CONSUMERS（未接线）＋ auction 在 F 册 0 命中
grep -n "\[CONSUMERS\]" src/zephyr/market_data/{autoload,connectors/base,failover/manager,raw_data_cache/cache}.py | cut -c1-200
grep -c "集合竞价\|auction" $S
# C-13 唯一生产消费者（预期 ex_sor/market_context_provider.py:64 真 import）
grep -rn "normalized_market_data_producer" --include="*.py" src scripts | grep -v "^src/zephyr/market_data/"
# C-14 读写两侧不同对象（预期 normalizer_base.py:54 ABC vs producer.py:271）
grep -n "^class DataNormalizer" src/zephyr/data/normalizers/normalizer_base.py; grep -n "^def load_kline\|^def produce" src/zephyr/market_data/normalized_market_data_producer/producer.py
# C-15 F03 侧真在跑（预期 implementations 46 py / 26 个 *_provider）
ls src/zephyr/data/implementations/*.py | wc -l; ls src/zephyr/data/implementations/*provider*.py | wc -l
# C-16 域册有主、F 册无锚（预期 domreg :1472-1476 命中；F 册 grep -w market_data＝0）
sed -n '1472,1480p' $DR; grep -c -w market_data $S
```

## 六、残余缺口（三案各还缺什么才能"六向齐全"）

| 案 | 仍缺 | 为什么本波没做 | 建议补法（下一波） |
|---|---|---|---|
| P-1 | ①生产 PG 实读 `_schema_version` 行数与最近 applied；②`schemas/categories/**`（223 py）与 CH 实际表列的漂移普查结果 | 禁触生产 DB／取证限量 | 由数据操作车道跑 `verify_schema_health.py --ci` 的等价只读模式并回填输出 |
| P-1 | ③`apply_timezone_migration.py --verify` 的最近一次运行台账（是否真跑过、0 残留） | 属破坏性面取证，只读车道不跑 | 只跑 `--verify`（文档称 0 写入需先读代码确认，勿跑 `--phase`） |
| P-3 | ④"运行时装配批"是否已在别处以别的名落地（当前判零依赖 `grep zephyr.infra_runtime` 一把尺） | 已做符号级；未做 PG/depgraph 面（禁写也禁查库） | 从 depgraph edges 反查 `zephyr.infra_runtime.*` 的入边数（只读 SQL） |
| P-3 | ⑤`resource_scheduler` 与 F80 的排班闸是否同口径 mem_ceiling（`runtime_admission` 自称"与排班闸同口径"） | 需读 `orchestrator/governance/capacity_budget.py` 全文比对 | 件级比对第二页（capacity_budget ↔ resource_profile_registry ↔ F80 三向） |
| P-5 | ⑥`failover/manager` 与 F03 `policy_registry` yaml 降级链的条目级重叠 | 本波按包/件面收口 | 读 `_registry/*policy*.yaml` 策略条目与 FailoverPolicy 枚举逐项对表 |
| P-5 | ⑦`auction_data_manager` 与 `data/implementations/ch_auction_derive.py` 的归属（F 册"集合竞价"0 命中＝整条数据线无位，是否成环） | 属新案，非 P-5 三问 | 立案为 auction 数据线二验（候选 B 段新行） |
| P-5 | ⑧退役评估的净删面账（域册 `:1472` ssot 条目＋翻译册＋`tests/market_data` 13 py（顶层 5 枚＋connectors/failover/raw_data_cache 三子目录）） | 净删＝Owner 门位，本车道无授权 | 出"退役 dry-run 清单＋diff 化披露"三段式提案，随波4 施工袋 |

三态结论：**本工单三案取证已挖干（件级表全部 file:line 化＋可复跑）**；结论均为"不推高 N"，故总筹 122→N 的 N **维持 132**；残余 8 项（§六）为**加深证据非改判项**，其中 P-1①③与 P-5⑦若出现反向证据可能改判（各 ±1）。
