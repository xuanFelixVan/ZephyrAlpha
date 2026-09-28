---
ttl: task_bound
volume: wiring_E_anchor_register
session: st-ailayer-final-20260924
creation_token: fullflow-w4-e-anchor-register-20260926
---

# 05_missing_p0 · W4-E 登记面补锚记录册（三案裁后落册 + V-P3-1 交册 + V-P1-1 定性 + P-8 立案）

> 车道＝挖矿/登记面 W4-E；工作面＝worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`。
> 判据真源＝`../94_chief_rulings_wave2.md` §七（环节分母定档 132、四条处置，本册照裁执行、**不重开案子**）；件级证据真源＝`04_p1p3p5_evidence_pages.md`（本册锚点逐条回抄并**实测复核**，未自创行号）。
> 边界遵守：`catalogs/**` 热册零改动（含 `functional_domain_registry.yaml`）；`src/**`、`config/**`、`scripts/**`（含 SQL）零改动；`pending_rulings.md` 仅追加、未改任何已有行；零提交、零入队、零 claim。
> 计数式取证纪律：本轮所有"零命中/零调用"结论一律 `grep -c` 或 `grep -rn | grep -c ""` 取数，**未使用带截断的输出**当"零命中"（94 册 §七.6 教训）。

## 一、F 册补锚（`00_skeleton/00_全环节总册.md`，8 行）

| 行 | 案 | 补锚前"核心模块路径"列 | 本次补入（句末均带 file:line 或 04 册锚点） | 状态列 |
|---|---|---|---|---|
| F06 `:31` | P-1＋P-5(a) | `src/zephyr/data/ch_config.py；scripts/ch/apply_*_ddl.py` | CH DDL 应用面计数（24 枚，全 `[STARTUP] manual`）＋"CH 侧无版本化入口"的复跑尺＋PG 侧对应件（`apply_pg_schema()`/`_MIGRATIONS`/`backup_pg_architecture()`/`02_create_pg_schema_down.sql`）＋读侧供给门面 `producer.py:271 load_kline` 挂本环出口 | 仍 `built`，追加**如实标注**："CH 无 applied 迁移台账"＋"已建不回滚"（V-P1-2） |
| F07 `:32` | P-1 | `postgresql://localhost:5432/depgraph；generate_project_depgraph.py` | schema 应用面（`depgraph_schema.py:1739`→`_PG_SCHEMA_SQL_PATH:1736`→`02_create_pg_schema.sql`，写 `_schema_version`，DDL 常量 `:564`）＋版本列表 `_MIGRATIONS:877`（自证"不再执行"）＋回滚面（`backup_pg_architecture()`@`backup_runtime_state.py:294` 及 6 处调用点＋唯一 down 脚本）＋校验面（GATE-C2 挂 `verify_schema_health.py`、G_TRAE_059 挂 `check_schema_version_writes.py`） | 仍 `built`，追加**如实标注**："`apply_pg_schema()` 全仓零调用方＝建成未接"＋"PG 有版本表而 CH 无 applied 台账"＋V-P1-1 定性指针 |
| F03 `:28` | P-5(a) | `src/zephyr/data/implementations/（miniqmt_provider.py 等）` | F03 侧实到规模（implementations/*_provider 计数）＋降级策略真源 `data/policy_registry.py:8`＋**读侧门面 2 件**：`market_data/normalized_market_data_producer/producer.py:271/:309`（唯一生产消费者 `ex_sor/core/market_context_provider.py:64`）、`market_data/auction_data_manager.py:93 AuctionSession`（指向 P-8 案） | 仍 `built`，追加环节内缺口注记（`data/normalizers/format_transformer.py:5` 写侧收口未接线）＋"与 market_data 包非双真源" |
| F06/F07 之上另记 | — | — | `producer.py` 读的是本环出口 CH `c1_market.kline_daily`，故同一件在 F03（源路由）与 F06（落库出口）两侧各留一句指针锚，不重复占环 | — |
| F10 `:35` | P-5(b) | `src/zephyr/data/scheduler.py；sch_tick_subscriber` | 未接线订阅/容灾骨架并本环子目：`connectors/base.py:126 MarketDataConnector`/`:54 ConnectionState`、`connectors/manager.py:45/:51`、`failover/manager.py:54 FailoverPolicy`/`:61 FailoverReason`（含各子包装载面共 4 件） | 仍 `built`，加注**"接线未落地"**（三条 AI-04 审计自证 CONSUMERS＋跨包 import/注册双零） |
| F80 `:145` | P-3 | `MOD-RESCHED-PROFILE/SAMPLER/GATE/ALERT/VIEW` | **4 件并本环子目**：`resource_scheduler.py:63/:72/:82`、`runtime_admission.py:143/:93/:120`、`cold_plane_isolation.py:84/:92/:100`、`latency_budget_allocator.py:64/:79/:87`；并记与 F13 的量纲正交判据（04 册 §2.3） | 仍 `built`，加注"底座件 `[CONSUMERS] 运行时装配批` 未落地" |
| F81 `:146` | P-3 | `src/zephyr/trading/health_monitor.py；REG-ATH-001` | `ha_sla_framework.py:61 SlaTarget`/`:70 ProbeResult`/`:81 RestartEvent` → 本环子目，并记"与 health_monitor 仅同名词、代码零重叠" | 仍 `built`，加注零生产 import |
| F68 `:123` | P-3 | `gpu_consensus_scheduler.py；factory_grid_executor.py` | `ml_pipeline_process.py:72 TaskKind`/`:92 MlPipelineProcess` → 本环子目（P5 ML 管线进程四职责＋时段退让＋GPU 夜间互斥） | 仍 `built`，加注零生产 import |
| F71 `:126` | P-3 | `python -m zephyr.trading`→`auto_runtime_core.py` | `shared_memory_zero_copy.py:60 ChannelState`/`:70 ChannelInfo` **标"待接线锚"（不占环）**；并记"infra_runtime 与 F71 非同物"（装配根 vs 底座库、双向零 import）＋"疑同物"根因＝域册错配 V-P3-1（本册 §三）＋V-P3-2 门面重复指针 | 仍 `built`，未动状态 |

**补锚不翻状态声明**：8 行状态列的 `built`/`partial` 值**一字未改**，只在括号内追加如实标注（缺什么、哪一面未接线）。P-1/P-3/P-5 三案按 94 册 §七.1 **ΔN=0**，环节分母维持 132，本册未新增/未删除任何环节行。

## 二、对账尺前后（uncovered）

见 §六复核命令 R-0；本轮补锚全部落在既有 8 行的锚点列，**未新增/未删除任何 F 号行**，故尺的分母不变。改前改后实测（`generate_fullflow_crosscheck.py --stdout`，只打印不写盘）：**uncovered 前＝0 ／ 后＝0**（`status: covered` 122 行、`status: uncovered` 0 行；与 HEAD 在册产物 `00_skeleton/91_machine_crosscheck.yaml:510 coverage_uncovered_links: 0` 同值，即"before"读数取自在册产物与本次实测的一致结果）。被本次改动触及的 8 行（F03/F06/F07/F10/F68/F71/F80/F81）改前后均 `covered`。
⇒ 如实补一句尺的语义：本役 W4-A 报的"22 未覆盖"经分诊＋W4-B 开真簿＋W4-A 补锚后**已在 HEAD 收口为 0**，故本次登记面改动不再产生 uncovered 变化；尺本身仍持 94 册 §六记录的"提到即算已挖"已知局限（本册与 F 册新增文本提到 8 个 F 号，全为本来就有簿的号，无洗白面）。
方法学提醒（承 94 册 §六"尺的认领面提到即算已挖"已知局限）：本册与 F 册新增文本会**提到**若干 F 号（F03/F06/F07/F10/F68/F71/F80/F81），按该局限这些号只可能被计为"已挖"，不构成洗白风险（8 号本就有簿）；反向的 `F107` 类误伤已在 94 册 §六记录。

## 三、V-P3-1 域册错配——**待落 YAML 块（热册零改动，交总筹单点落地）**

`docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` 是热册（92 册 §一.4 禁止触碰清单），本车道**一个字未改**。以下为建议修正块＋逐条理由。

### 3.1 实测复核（本车道独立取数，非回抄）

| 锚点 | 实测原文（关键三行） | 判读 |
|---|---|---|
| `:343-353` | `domain: D_INFRA_RUNTIME` / `subdomain: runtime_core` / `ssot_module: MOD-INF-035`(`:346`) / `ssot_path: src/zephyr/infra_runtime/`(`:347`) / covers＝三层运行时编排·节律调度·健康监控·工作编排·自动接入(`:349-353`) | **module↔path 绑错**：`MOD-INF-035` 是 `auto_runtime_core.py`（＝F71 装配根）的 blueprint，`ssot_path` 却指向底座包；covers 逐条亦全为 F71 职责 |
| `:759-767` | `subdomain: runtime_integration` / `ssot_module: MOD-INF-002`(`:762`) / `ssot_path: src/zephyr/infra_runtime/`(`:763`) / covers＝运行时集成层·基础设施配置·模块间集成桥接 | 与 `:343` **同 `ssot_path` 的第二条目**（`MOD-INF-002` 未随包拆分重绑） |
| `:604-616` | `subdomain: persistence` / `ssot_module: SH-DB-001`(`:607`) / `ssot_path: src/zephyr/data/persistence/`(`:608`) / covers 首条＝`SQLite DDL Schema(v1-v8迁移)`(`:610`) | **同域**第三条，但 `ssot_path` 是 `data/persistence/`，**不与上两条同 path** |

⇒ **对本车道上游表述的一处实测更正（先验量纲，承"两个数字矛盾先验量纲"教训）**：`D_INFRA_RUNTIME` 域下确有 **3 条目**（`:343`/`:604`/`:759`），但 **同 `ssot_path: src/zephyr/infra_runtime/` 的只有 2 条目**（`:343`/`:759`）。94 册 §七.2 与 04 册 §2.4 写作"同 path 另有 :759/:604 共 3 条目"，把"同域第三条"计入了"同 path"。收敛动作因此**只涉及 2 条**（`:604` 属另一议题＝§3.4 附列），不改结论、不改 N。

### 3.2 块 A：`:343-353` 修后文本（保留 path、重绑 module、covers 换义）

```yaml
- domain: D_INFRA_RUNTIME
  subdomain: runtime_core
  domain_name_zh: 运行时底座与准入
  ssot_module: MOD-INF-074/075/076/077/078/079/080   # 原 MOD-INF-035 属 auto_runtime_core，已解绑
  ssot_path: src/zephyr/infra_runtime/
  covers:
  - 资源平面准入裁决（Hot/Warm/Cold 核亲和/内存预算/QPS 令牌桶）
  - 运行时配额合成准入（并发/令牌/内存三件配额）
  - Cold 平面隔离与盘后激活
  - 端到端延迟预算分解登记
  - 单机进程 SLA 登记与健康探针编排
  - 跨进程零拷贝通道
  - ML 管线进程任务队列
  - 多后端数据库访问门面（待收敛，见 V-P3-2）
  aliases:
  - 运行时底座
  - runtime foundation
  stability: evolving
  ai_autonomy: ai_modifiable
```

### 3.3 块 B：`:759-767` 处置（同 path 重复条目→收敛唯一，**合并而非新增**）

```yaml
# 方案 b-1（推荐·零净删）：把 :759 条目的 ssot_path 重绑到"运行时集成"的真家，避免与 :343 抢同一路径
- domain: D_INFRA_RUNTIME
  subdomain: runtime_integration
  domain_name_zh: 运行时集成
  ssot_module: MOD-INF-002
  ssot_path: src/zephyr/trading/          # 运行时集成/装配根面（F71 AutoRuntime Core）
  covers:
  - 三层运行时运营中心（装配根/组合器 boot()）
  - 三层路由（L1 Trae/L2 Local/L3 API）
  - 节律调度（circadian_scheduler）
  - 工作编排（work_orchestrator/work_dag）
  - 自动接入（auto_integrator）
# 方案 b-2（备选）：整条 :759 并入 :343（合并同域重复簇）——但该条 ssot_module 条目消失＝注册表净删＝Owner 门（宪法 §5.2），今夜不可执行
```

⇒ 块 A＋块 B 合起来的净效果：**`MOD-INF-035`/F71 装配根语义回到 `src/zephyr/trading/`，`src/zephyr/infra_runtime/` 只被一条目持有**，P-3"疑同物"的唯一来源被消除；环节集合与条目总数不变（走 b-1），不触 Owner 门。
⇒ 落地归属：域册是热册，**由总筹单点写**（用 `safe_write_text` CAS，写后进程外核实）；本车道只交块。

### 3.4 附列（同源不同病，交总筹一并判，本车道不动）

1. `:604-616` `persistence` 条目 covers 首条 `SQLite DDL Schema(v1-v8迁移)` ＝迁移语义在域面有位，但 `ssot_path: src/zephyr/data/persistence/` 与 SQLite DDL 现真源是否同处**未核**（本车道未读 `data/persistence/`，且 `src/zephyr/data/**` 在他道在途清单）。与 V-P1-1/V-P1-2 同族，建议并读。
2. `:1472-1480` `D_MKT_DATA/market_data` 条目：`ssot_module: MOD-L00-002`、`ssot_path: src/zephyr/market_data/`、covers＝"采集、分发和订阅管理"三条——**与包实态不符**（该包实测 20 py/3,323 行中仅 `producer.py` 363 行有生产消费者，其余为读侧 DTO/竞价管理/未接线骨架，见 04 册 §3.1）。＝V-P5-1 的另一半：域册有主而 covers 语义过宽，易再次诱发"包存在即环节"的误判（04 册 §3.4 已标为三案最高代价）。建议 covers 改列"读侧规范化 DTO／集合竞价数据管理／订阅与容灾抽象骨架（未接线）"。

## 四、V-P1-1 台账双口径矛盾——**定性＝注释/口径滞后，非真双源**（只登记，SQL 零改动）

**病灶表述**：`scripts/governance/migrate_sqlite_to_pg/05_fix_guc_trigger_bug.sql:94` 原文 `-- 注意：本项目无 schema_migrations 表，迁移元数据通过 git commit log 追踪。`，与 `depgraph_schema.py:564 _DDL_SCHEMA_VERSION`（`_schema_version` 表 DDL）＋`:877 _MIGRATIONS` 版本表面矛盾。

**取证（本车道实测，判"哪一侧被代码消费"）**：

| 侧 | 是否被代码消费 | 实测证据 |
|---|---|---|
| `_schema_version` 表 ＋ `_MIGRATIONS` 列表 | **是，两把尺都在读** | `scripts/governance/d11_compliance/verify_schema_health.py:201-206`（`expected = len(depgraph_schema._MIGRATIONS)`；`SELECT COALESCE(MAX(version),0) FROM _schema_version`；不等即报 `[VERSION-DRIFT]`），该件挂 GATE-C2（`gate_registry.yaml:469-477`）；`scripts/governance/d3_metadata/check_schema_version_writes.py:145-167`（同一比较，另 AST 扫描"白名单外写 `_schema_version`"即违规） |
| `schema_migrations` 表（SQL 注释所指） | **否** | 全仓 `grep -rn "schema_migrations" --include="*.py" src scripts` 计数＝**1**，且该命中不在任何迁移执行/登记链路上（见 §六 R-3 复跑）；对照 `_schema_version` 在 py 侧被 **31 个文件**引用 |
| 编号 SQL 文件本身（`00..12_*.sql`） | **无自动登记/无自动执行** | `grep -rn "migrate_sqlite_to_pg" --include="*.py" src scripts` 计数＝**36**，逐条判读全为：docstring/真源指针注释（`depgraph_schema.py:61/:873/:1408`）、报错提示里让人手工 `psql -f`（`:1412/:1427`、`battlemap_schema.py:306`、`dataflowgraph_schema.py:313`、`decisiongraph_schema.py:355`）、audit 白名单路径文本（`workspace_hygiene_reconciler.py:259-260`）、件自身 `[CONSUMERS] manual` 头注——**零"遍历编号 SQL 并登记 applied"的代码路径** |

**定性结论**：**口径滞后（注释错），不是双真源**。理由：该 SQL 的表述对"`schema_migrations` 这张表不存在"为真，但由此推得"本项目无迁移台账、靠 git log 追踪"为假——同库同项目存在**唯一被消费的版本台账** `_schema_version`（写入点 `apply_pg_schema()` `depgraph_schema.py:1761-1766`，一致性由上两把尺校验）。故＝**一处过时注释**，非"两套台账并行写入"，无需架构收敛。

**处置（守车道边界）**：SQL 一字未改。建议修法随波3-D 登记面批：把 `:93-99` 注释块更正为——
> 本项目 PG 架构库迁移台账真源＝`_schema_version` 表（DDL 常量 `depgraph_schema.py:564`；写入者 `apply_pg_schema()` `:1739/:1761-1766`；一致性尺 `verify_schema_health.py:201-206`〔GATE-C2〕与 `check_schema_version_writes.py:145-167`〔G_TRAE_059〕，判据 `MAX(_schema_version) == len(_MIGRATIONS)`）。本 SQL 是一次性手工修复件，**不登记入 `_MIGRATIONS`**（该列表 `:872-877` 注释自证"不再执行"，仅供两把尺读版本号元数据）。

**与 V-P1-2 的关系（94 册 §七.4 已定，本册不重开）**：CH 侧确实**无** applied 台账（`apply_*_ddl.py` 只 `IF NOT EXISTS` 幂等、明写"已建不回滚"），该缺陷是"登记缺位"非"环节缺位"（ΔN=0）；PG 侧缺陷是"入口建成未接"（`apply_pg_schema()` 零调用方）。两者与 V-P1-1 同批下达，不可只补锚（04 册 §1.5 反向代价：CH 时区级五阶段重建仍无版本闸门＝数据不可逆面）。

**未证残项**（车道边界，已在 04 册 §六 P-1①）：未连生产 PG 实读 `_schema_version` 行数/最近 applied_at ⇒ "台账是否真有人在写"仍未证；本轮结论只到"代码读它、代码写它的入口零调用方"。

## 五、P-8 新案（竞价数据线整条无环节位）——已追加立案

案文见 `pending_rulings.md` 表末新增行（P-8，一行一案，已有 7 行未改）。要点：94 册 §七.5 判"待挖"（六向未取），**不预计入 132**；本车道只立案＋给最小观测量。

**最小观测量（跑这 4 组命令即可定"真缺 or F 册无锚"，全只读；已跑者附本车道实测读数）**：

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md

# M-1 F 册整册 auction 命中数（计数式，禁截断）  → 实测读数＝0（＝整条线在 F 册无环节位）
grep -o -i -e 集合竞价 -e auction -e call_auction $S | wc -l

# M-2 实体件全集（判"一条线有几件、跨几包"）    → 实测读数＝5 件跨 5 包：
#   scripts/backfill_auction_snapshot_history.py（补史腿）
#   src/zephyr/data/implementations/ch_auction_derive.py（派生落库腿）
#   src/zephyr/market_data/auction_data_manager.py（管理腿 MOD-MKT-007）
#   src/zephyr/signal_ashare/auction_microstructure_analyzer.py（下游信号腿 MOD-SIG-089）
#   src/zephyr/plan_engine/auction_hit_recorder.py（下游记录腿 MOD-PLAN-015）
find src scripts -iname "*auction*" ! -path "*__pycache__*" | sort

# M-3 跨包生产消费者计数（判"有真实下游腿 or 零消费骨架"） → 实测读数＝14 命中（下游真实存在）
#   ⇒ w5_1 判据②"零触发零消费→退役"不适用；本案只能走"立环 or 既有环子目补锚"二选一
grep -rn "auction_data_manager\|AuctionSession\|auction_microstructure_analyzer\|auction_hit_recorder" \
  --include="*.py" src scripts | grep -v "^src/zephyr/market_data/" | grep -c ""

# M-4（本车道未跑，交下波）触发面与登记面读数：调度代码＋注册表各有无 auction
grep -rin "auction" src/zephyr/data/scheduler.py src/zephyr/trading/*.py | grep -c ""
grep -rin "auction" docs/01_policies_and_standards/_registry/catalogs/*.yaml | grep -c ""

# M-5（本车道未跑，交下波）出口真源读数：auction 表名与落库面（禁触生产 DB，只读代码侧登记表）
grep -rin "auction" src/zephyr/data/table_registry.py | grep -c ""
```

**读数小结**：M-1＝0／M-2＝5 件／M-3＝14 → "真缺嫌疑"已由"包名未见"抬升为"5 件 5 包＋14 处跨包消费而 F 册零位"；但环节四要素中的**入口触发器**（M-4）与**出口真源**（M-5）未取，**六向不齐 → 维持 94 册 §七.5 的"待挖、不预计入 132"**，本车道未据读数改判。

## 六、文件清单与复核命令

**本车道改动（2 件，均文档面）**：
1. `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`——8 行补锚（`:28/:31/:32/:35/:123/:126/:145/:146`），未增删行、未改状态列取值；
2. `docs/_working/fullflow_mining/05_missing_p0/pending_rulings.md`——表末追加 1 行（P-8），已有行零改动；
3. `docs/_working/fullflow_mining/05_missing_p0/wiring_E_anchor_register.md`——本册（新建，creation_token 见头注）。

**复核命令（全只读，可在本 worktree 复跑）**：

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
DR=docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml

# R-0 对账尺（uncovered 前后；--stdout＝只打印不写盘，本车道未生成/未改 91_machine_crosscheck.yaml）
python scripts/governance/fullflow/generate_fullflow_crosscheck.py --stdout | grep -c "status: covered"
python scripts/governance/fullflow/generate_fullflow_crosscheck.py --stdout | grep -c "status: uncovered"
grep -n "coverage_uncovered_links" docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml

# R-1 F 册补锚落位（8 行均应含 market_data / infra_runtime / apply_pg_schema 字样，计数式）
grep -c "apply_pg_schema\|_MIGRATIONS" $S; grep -c "zephyr/market_data\|zephyr/infra_runtime" $S
grep -n "^| F06 \|^| F07 \|^| F03 \|^| F10 \|^| F68 \|^| F71 \|^| F80 \|^| F81 " $S | cut -c1-90

# R-1b 状态列未翻（应仍为原值，且补的标注在括号内）
grep -n "^| F06 .*| built（" $S | grep -c "" ; grep -n "^| F07 .*| built（" $S | grep -c ""

# R-2 apply_pg_schema 零调用方（预期：code 侧仅 depgraph_schema.py 的 :1739 定义＋:1853 __all__＋:1765 内部串）
grep -rn "apply_pg_schema" --include="*.py" src scripts | grep -v __pycache__
grep -rl "apply_pg_schema" . --exclude-dir=.git --exclude-dir=__pycache__ | grep -c ""

# R-3 V-P1-1 双侧消费（预期 1 vs 31）
grep -rn "schema_migrations" --include="*.py" src scripts | grep -v __pycache__
grep -rln "_schema_version" --include="*.py" src scripts | grep -v __pycache__ | grep -c ""
grep -rn "migrate_sqlite_to_pg" --include="*.py" src scripts | grep -v __pycache__ | grep -c ""
sed -n '93,99p' scripts/governance/migrate_sqlite_to_pg/05_fix_guc_trigger_bug.sql
grep -n "_MIGRATIONS\|_schema_version" scripts/governance/d11_compliance/verify_schema_health.py

# R-4 V-P3-1 域册原文未改（预期 git diff 对本文件为空）
git diff --stat -- $DR; sed -n '343,353p;759,767p;604,616p;1472,1480p' $DR

# R-5 P-8 最小观测量
grep -o -i "集合竞价\|auction\|call_auction" $S | wc -l
find src scripts -iname "*auction*" ! -path "*__pycache__*" | sort
grep -rn "auction_data_manager\|AuctionSession\|auction_microstructure_analyzer\|auction_hit_recorder" --include="*.py" src scripts | grep -v "^src/zephyr/market_data/" | grep -c ""

# R-6 净零与边界自证（预期：只列本车道 3 件，热册/SQL/src/config 零命中）
git status --porcelain
```

## 七、本车道实测对上游两册的**四处口径修正**（不改判据、不改结论，只把数抽验一条）

承"两个数字矛盾先验量纲"与"交接书配方也要抽验一条"两条教训，本车道对回抄源（04 册／94 册）逐锚重跑，四处读数与其不一致，均已按**实测**写入 F 册并在下表留痕：

| # | 上游表述 | 本车道计数式实测 | 影响 |
|---|---|---|---|
| 1 | 94 册 §七.2／04 册 §2.4：域册"`ssot_path` 同 path 另有 `:759`/`:604` 共 3 条目" | `D_INFRA_RUNTIME` 域下确为 3 条目（`:343`/`:604`/`:759`），但**同 `ssot_path: src/zephyr/infra_runtime/` 只有 2 条**（`:343`/`:759`）；`:604` 的 path 是 `src/zephyr/data/persistence/` | 收敛动作面由"3 条"改"2 条"，块 A/B 已按 2 条给（§三.3.1）；不改"域册错配"定性与 ΔN=0 |
| 2 | 04 册 §1.3：`backup_pg_architecture()` "被 6 处写路径调用" | **代码调用点 7 处／6 文件**：04 册所列 6 处 + 漏计 `apply_decisiongraph.py:928`（同文件第二调用点） | F07 行按"7 处／6 文件"记，并点名漏计处；不影响"已事件触发"结论 |
| 3 | 04 册 §1.2／V-P1-2 表述为"CH 侧无 applied 台账"（易被读成"CH 侧无任何 `_MIGRATIONS` 名"） | `scripts/ch/apply_*.py` 中确只有 **1 枚**含 `_MIGRATIONS`：`apply_market_tables_ddl.py:612`，是**脚本内**建表清单（`:1243` 自身循环消费），**无版本号、无 applied 落库记录** | F06 行按"有脚本内清单、无 applied 台账"精确表述，防下波把 `:612` 当台账而判"V-P1-2 已证伪" |
| 4 | 04 册 §四：P-5 分类 (b)"收敛 F10 **4 件**" | 实体件 **3 枚**（`connectors/base.py`、`connectors/manager.py`、`failover/manager.py`）＋两枚**非空**子包装载面（`connectors/__init__.py` 51 行、`failover/__init__.py` 48 行，非 26 行空壳）＝按"件"计可读作 3 或 5 | F10 行把 5 个文件全列出并标明口径，采"实体 3 枚为准"，防后续按包名清点时件数漂移 |

**另记两处账面卫生（本车道无权限动，只报）**：
① `pending_rulings.md` 标题行仍写"一行一案，7 案"，本车道按"追加式禁改已有行"追加 P-8＝实到 8 案，**标题计数未更新**＝该计数属手工静态清单，违宪法 §9.5（凡"条目列表＋计数"应生成器产出）→ 建议总筹改由生成器出数或改字段化。
② 本 worktree 的 index 是多会话混合池（`git status --porcelain` 实测含 `catalogs/**`、`config/**`、`src/**` 等他道 staged 条目），**本车道三件产物之外的任何改动都不是本车道所为**；落地时须按件切袋，勿随袋吸收（归属篡改风险）。


**三态结论**：
- **完工**＝F 册 8 行补锚（P-1/P-3/P-5 三案裁后结论全部落册，ΔN=0 维持 132）＋V-P1-1 定性（注释/口径滞后，非双源）＋P-8 立案并附最小观测量＋V-P3-1 交册（YAML 块 A/B＋逐条理由＋"同 path 只有 2 条"的实测更正）。
- **待挖**＝P-8 的六向证据（本车道只出 M-1…M-4 尺，未取证改判）；V-P1-1 残项"生产 PG `_schema_version` 实读"；04 册 §六其余 5 项加深证据。
- **待裁/待落（他方）**＝①V-P3-1 块 A＋块 B 由**总筹**写热册（本车道禁触）；②V-P3-2 `database_layer` 门面收敛＝94 册 §七.3 已改判 P0 施工项、随波3-D；③V-P5-1/V-P1-2 的净删与 DDL 面＝Owner 门（注册表净删/DDL），今夜只登记。
