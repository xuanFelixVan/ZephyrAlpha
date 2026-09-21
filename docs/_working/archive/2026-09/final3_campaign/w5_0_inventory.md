---
ttl: task_bound
completes_when: W5-1 逐域内收审计消费本基线后归档（最迟 2026-10-19）
title: W5-0 全项目资产总盘点十类台账（W5-1/W5-3 基线）
---

# W5-0 全项目资产总盘点（十类台账）— final3_campaign

> session=st-final3-20260919 | date=2026-09-19 | 用途=W5-1 逐域内收审计（22 域分包）与 W5-3 总量仪表的基线
> 口径声明：**全部计数为 2026-09-19 当日本会话实测**（Python 只读扫描 / 直连 DB 查询），非文档转抄。
> 扫描范围为仓库正本（`D:\ZephyrAlpha`），未计入 `.aidrafts/`、`.worktrees/`、`.runtime/`、`.openclaw/` 等会话副本区。

## 0. 十类台账总表

| # | 类别 | 实测总数 | 口径 / 命令 | 证据等级 |
|---|------|---------|------------|---------|
| ① | 模块（src/zephyr） | **3259** 文件带 `[A_module]` 锚（锚行 3264；唯一 module_id **1063**；py 全树 3626） | 正则 `#\s*\[A_module\]\s*module_id=(\S+)` 逐文件扫描 `src/zephyr/**/*.py` | A（机读实测） |
| ② | 脚本（scripts/） | **1033** 个 .py（磁盘实测；script-manifest 登记 994，`total_scripts` 字段 993） | `rglob("*.py")` under `scripts/` + manifest 对账 | A（机读实测） |
| ③ | 注册表（ROOR 索引） | **75** 个（tier0=12 / tier1=29 / tier2=34；registry_id 零重复） | `yaml.safe_load(docs/registry_of_registries.yaml)` 数 `tiers[].registries[]` | A（机读实测） |
| ④ | 门禁 | **169**（gate_registry 册，字段=条数一致）+ **113**（in_process 册，全部 ⊆ 前者，并集 169） | 双册 `total_gates` 字段与 `gates[]` 列表双端核对 | A（机读实测） |
| ⑤ | 全景图 | **10** 张（§3 权威=10，表行实测=10，一致；4 份 YAML 真源文件在盘核实） | 解析 alignment_checklist.md §3 表行 `^\| \*\*…\*\*` + 磁盘存在性 | A（机读实测+权威对齐） |
| ⑥ | SOP | **37** 份 .md（9 族；族分布见 §6） | `docs/01_policies_and_standards/sop/**/*.md` 计数 | A（机读实测） |
| ⑦ | 文档树（docs/ 除 _working） | **1957** 份 .md | `docs/**/*.md` 排除 `_working` 路径段 | A（机读实测） |
| ⑧ | 配置 yaml | **79** 份（config/ 73 yaml+5 yml；src/**/config/ 6 yaml） | `config/**` + `src/**/*.yaml`（路径含 config 段） | A（机读实测） |
| ⑨ | 数据库表 | **ClickHouse 246** + **PG 图库 89** = 335 | CH：`DatabaseService.get_clickhouse_conn()` 查 `system.tables`（排 system 库）；PG：`get_depgraph_conn(read_only=True)` 查 `information_schema.tables`（RealDictCursor，错误 rollback 复测） | A（活库实测） |
| ⑩ | 常驻服务 | **35**（SERVICE_CATALOG，AST 解析权威）+ **43** 个 Zephyr 计划任务（Ready 33 / Disabled 6 / Running 4） | AST 解析 `services_registry.py` 的 `SERVICE_CATALOG` 列表元素数；PowerShell `Get-ScheduledTask -TaskName like *Zephyr*` | A（机读实测） |

---

## 1. ①模块 — src/zephyr（锚计数口径）

- py 全树 **3626**；带 `[A_module]` 锚文件 **3259**；锚行 3264（5 个文件有 ≥2 锚）；**无锚 .py 367**（W5-1 线索：含 512 个 `__init__.py` 中一部分与 11 个"[A_module] 存在但 module_id 解析失败"的疑似坏锚文件——3270 含锚串文件 vs 3259 正则命中）。
- 唯一 module_id **1063**；**109 个 module_id 被多文件共享**（蓝图粗粒度锚）。

**module_id 重复簇 TOP10（同 id 城 hacK，按文件数）**：

| module_id | 文件数 |
|---|---|
| MOD-FEEDBACK_LOOP | 287 |
| MOD-GATE_ENGINE | 202 |
| MOD-INF-016 | 195 |
| MOD-INF-022 | 107 |
| MOD-INF-025 | 86 |
| MOD-INF-018 | 79 |
| MOD-INF-019 | 74 |
| MOD-INF-020 | 66 |
| MOD-INF-039 | 66 |
| MOD-INF-017 | 66 |

**同名文件簇 TOP10（跨目录同名城，排除 `__init__.py`）**：models.py×9、__main__.py×8、contracts.py×7、cli.py×5、engine.py×5、config.py×4、metrics.py×4、task_queue.py×4、execution_report.py×4、risk_limits.py×4（同名城共 171 簇）。`__init__.py` 单列：512 个。
**同前缀簇**（归一化去版本尾）：init×512、safety_gate_l×18、models×9、main×8、contracts×7、cli×5。
**零消费嫌疑线索**：`shared/contracts/*` 与 `trading/trading_contracts/*` 存在同名同构对（execution_report.py / fill.py / order.py / instrument.py / risk_limits.py 等 ~11 组），疑为契约双真源——W5-1 建议优先内收。

## 2. ②脚本 — scripts/

- 磁盘 **1033** 个 .py；`scripts/script-manifest.yaml` 登记 994 条、头部 `total_scripts: 993`（**字段与列表差 1**，机生器内伤线索）。
- **对账**：磁盘不在册 40（多为新批 ai_layer/automation/backtest/ch/apply_*_ddl）；在册幽灵 1（manifest 有、磁盘无）。
- 同名文件簇 TOP10（≥2 全列）：check_naming_convention.py、run_all.py、generate_asset_index.py、registry_batch_edit.py、status_all.py、check_pit_compliance.py、check_frontmatter_metadata.py、generate_rule_catalog.py、fix_n12_ke_naming.py、frontmatter.py 各×2。
- 前缀/动词簇：validate_*×110、check_*×94、c4_*×88、generate_*×57、detect_*×41、apply_*×35、run_*×23、fix_*×21、verify_*×19（check_naming 与 fix_n 命名修复簇 fix_n×7 为一次性脚本嫌疑——W5-3 退役审计素材）。

## 3. ③注册表 — ROOR（docs/registry_of_registries.yaml）

- 索引注册表总数 **75**（机读 `tiers[].registries[]`）：tier0 核心源码级 12、tier1 治理与政策级 29、tier2 数据与运行时级 34；registry_id 无重复；无顶层游离 `registries` 键。
- 线索：ROOR 内 REG-SCRIPT-001 `entry_count: 991` 与本日实测 1033 漂移 +42（ROOR 条目数为快照字段，属预期可解释，但 W5-3 仪表应以机读为准，勿引 ROOR 快照数）。

## 4. ④门禁 — 双册口径

| 册 | 路径 | total_gates 字段 | gates[] 实长 | 判定 |
|---|---|---|---|---|
| gate_registry | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | 169 | 169 | 一致 |
| in_process_gate_registry | docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml | 113 | 113 | 一致 |

- 并集 169 / 交集 113：in_process 册是 gate_registry 的真子集（in-process 全部已并入总册）；in_process 册 enabled=true 113（无 false 残留）。
- 双册重复度即"两册口径"结论：**对外报数用 169，in-process 子集 113**。

## 5. ⑤全景图 — §3 权威核对

- alignment_checklist.md §3 声明"现 10 张"；实测 §3 表行 **10**（depgraph / dataflowgraph / decisiongraph / blueprint.md / battle_map / frontend_map / trading_decision_map / industry_chain_map / strategy_production_map / governance_operations_map）——**权威与实测一致**。
- YAML 真源在盘核实：config/trading_decision_map.yaml、config/strategy_production_map.yaml、config/governance_operations_map.yaml、src/zephyr/frontend/dashboard/web/frontend_map.yaml、config/chainmap_cluster_names.yaml 均存在。
- **命名漂移线索**：§3 depgraph 行真源写"PostgreSQL `dep_` 表组"，实测 PG 无任何 `dep_*` 表——图 1 实际挂 `nodes`/`edges`/`nodes_metadata`/`edges_metadata`/`nodes_archive_module_lifecycle` 表组（W5-1 文档改漏项）。

## 6. ⑥SOP — docs/01_policies_and_standards/sop/

- **37** 份 .md。族分布：backtest_system_sop 6、construction_sop 4、governance_sop 4、mining_sop 4、ops_sop 4、review_sop 4、data_ops_sop 3、trading_decision_map_sop 3、data_audit_sop 2、根散页 3。
- 同名簇：index.md×10（每族一册，生成器口径，正常）、README.md×2。

## 7. ⑦文档树 — docs/（除 _working）

- **1957** 份 .md。顶层分布：03_modules 1420、02_enterprise_architecture 344、_archive 131、01_policies_and_standards 62。
- **同名城**（本盘点的最大重复簇）：index.md×894、blueprint.md×546——均为 03_modules 模块目录的机生锚文件（每模块一 blueprint + 若干 index）；非冗余但构成"同名城"基数，W5-1 按 22 域分包时按目录聚合处理。
- README.md×6。

## 8. ⑧配置 yaml — config/ + src/**/config/

- config/ 下 **73** .yaml + **5** .yml；src 下 config 目录 **6** 份（src/zephyr/data/config/：data_supply_sentinel、known_data_gaps、manual_calendar_events_schema、policies、schedule、tasks）。合计 **79**。
- 同名簇仅 prometheus.yml×2；前缀簇无 ≥3 簇——配置层重复度健康。
- 线索：yml/yaml 后缀混用 5 份（prometheus 惯例除外，余 4 份可统一）。

## 9. ⑨数据库表 — ClickHouse + PG

**ClickHouse（get_clickhouse_conn → system.tables，排 system 库）= 246 表 / 约 125.7 亿行**：

| database | 表数 | 总行数 |
|---|---|---|
| c0_meta | 1 | 103 |
| c1_backtest | 14 | 9,686 |
| c1_market | 192 | 12,565,871,113 |
| c3_fundamental | 39 | 54,067,608 |

- 跨库同名表：**0**（同名声为零——CH 层重复度健康）。

**PG 图库（get_depgraph_conn → information_schema.tables，BASE TABLE）= 89 表**：

| schema | 表数 |
|---|---|
| public | 62 |
| ai_intake | 9 |
| ai_intake_test_smoke | 9 |
| ai_intake_test_smoke2 | 9 |

- **重复簇**：ai_intake 系 4 份 schema 变体（正本 9 表 + 两个 test_smoke 各 9 表）= 36 表同构，`ai_intake_test_smoke*` 是**生产 PG 内的测试残留**（测试隔离红线线索，W5-1 数据域分包处置）。
- public 前缀簇 TOP：ig_*（产业链图 13 表）、battle_map×3、dataflow×5、decision×4、domain×6、nodes/edges 系（depgraph 轴）。
- 佐证：battle_map_steps/anchors/edges 三表与 §3 battle_map 行吻合。

## 10. ⑩常驻服务 — 服务总闸 + 计划任务

- `src/zephyr/frontend/dashboard/services_registry.py` 的 `SERVICE_CATALOG` 实测 **35** 项（AST 解析列表元素，免副作用；id 无重复）——为"启动项唯一真源"（Owner 2026-09-02 裁定）。**文件 docstring 仍写"16 个启动项"= 过时注释线索**。
- 计划任务：`Get-ScheduledTask *Zephyr*` = **43** 个（Ready 33 / Running 4 / Disabled 6）。含 ZephyrAlpha_ProcessReaper（冷启动依赖）、ZephyrAlpha_DataScheduler、ZephyrAlpha_TickSubscriber、ZephyrAlpha_CHHealthProbe、ZephyrAlpha_WorktreeDriftWatchdog 等。
- 线索：`_OneShot0915/_Full0916/_NightlySentiment/_TradingWatchdog` 等 6 个 Disabled 任务为一次性/停用残留，退役审计候选。

---

## 11. 扫描脚本清单（.runtime/tmp/，不入库）

| 脚本 | 覆盖 | 复跑命令 |
|---|---|---|
| w5_0_scan_fs.py | ①②⑥⑦⑧ + 文件名/前缀重复簇 + manifest 对账 | `python .runtime/tmp/w5_0_scan_fs.py` |
| w5_0_scan_reg.py | ③④⑤⑩（ROOR/双册/§3/服务目录/schtasks） | `python .runtime/tmp/w5_0_scan_reg.py` |
| w5_0_scan_db.py | ⑨（CH system.tables + PG information_schema） | `python .runtime/tmp/w5_0_scan_db.py` |

原始机读结果：`.runtime/tmp/w5_0_fs_result.json`、`w5_0_reg_result.json`、`w5_0_db_result.json`（同目录，24h TTL，未 promote）。
环境前置：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:.../Scripts:$PATH"`（Python 3.12.x）。

## 12. 回执（六要素）

1. **十类计数**：全表见 §0，十类全实测，无缺类。
2. **证据等级**：十类均 A 级（本会话机读/活库直查）；⑤ 另做了权威 vs 实测双向核对。
3. **未完成项**：无硬未完成。两点口径说明：⑦ docs 计数含 `_archive` 131 份（口径未排除）；①的"模块数"给的是锚文件口径 3259，若 W5-1 需唯一 module_id 口径则为 1063。
4. **移交给 W5-1 的四条漂移线索**：§3"dep_ 表组"命名过时；PG 内 ai_intake_test_smoke×2 测试残留 schema；script-manifest total_scripts 993 vs 列表 994；services_registry docstring 16 vs 实际 35。
5. **红线遵守**：全程只读扫描（写操作仅产物+reaper keep 登记）；未触碰禁碰清单文件；未动他会话 staged 在途件。
6. **防误杀**：扫描批已在 `data/runtime/process_reaper_keep.txt` 登记 `w5_0_scan`。
