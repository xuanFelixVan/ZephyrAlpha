---
ttl: task_bound
title: "全项目全景图族挂齐审查 — 缺口总账与终局报告"
---

# 全项目全景图族挂齐审查（图↔物双向对账）— 缺口总账 + 终局报告

> sid=st-audit-all-20260924 · 2026-09-24 · 方法论=audit_prompts_20_ai.md v5（T0 机械波 + 全图全库对齐 §11 + 能红自证 §0.14 + 门位笼子 §0.8）
> Owner 定调：不挂图不知全貌，挂图才见缺失与断点。八图逐张做「图有物无=悬空 / 物有图无=漏挂 / 挂错=断链」双向对账。

## 摘要（大白话）
把 8 张"全景图/册"与仓库实物逐条对表。**结论**：①②③号图基本挂齐，对账当场揪出并修好断链（工厂图车道 G 断点、工厂图 2 处数据表指错库、治理运行地图机生层 25 处陈旧快照）；把全仓结构对齐从 **28 硬打到 3 硬**（25 项 GOMAP 派生陈旧当场重跑清零并落地 dev；余 3 项是裁定册 related_arch 填错字段，处方已验证但热文件由总指挥活跃持有，随其下笔原子落）。④⑤⑥⑦⑧号图**发现的缺口绝大多数不能由审查包自行修**——它们是其他在飞施工包的写域、需要大量建码/接线的骨架件、或动生产数据/门禁/备份的高危门位项，已逐条带证据登记交总指挥/Owner。

## 全局修复统计
| 图 | 对账结论 | 当场修复（已入队） | 登记（不可自修） |
|---|---|---|---|
| ① TDM 182节点/254边 | 悬空0/漏挂(11 STR pending)/断链(provenance) | — | fw-tdm sha 陈旧（依赖他会话 staged 的 map，勿连坐）|
| ② 工厂 16节点/16边 | 悬空1/断链2 | ✅ E1G 补边 + account_nav_daily→c1_market（2 处）| news_data 语义待定 |
| ③ 企架八册+GOMAP | 派生文档陈旧为主 | ✅ GOMAP 重跑（硬 25→0 已落地 dev）| 裁定 related_arch×3（处方交总指挥，热文件）；各生成册重跑/04 断链/3 目录漏挂/产业链避让 |
| ④ 数据源 23 | 四态对账 | — | 3 空表静默失效/4 漏挂/3 断链（架构受保护+prod）|
| ⑤ 因子 175 | 三层依赖 | — | 骨架化：0/24 策略因子齐备（Owner 点名·高）|
| ⑥ 图书馆 4.3万 | blind3/ghost232/覆盖99.43% | — | fs_collector "models" skip-word 盲区（他包）|
| ⑦ 存储 INFRA-STORE-003 | 悬空0（3 路径欠精）| — | dedup-by-size 不安全（曾 hash 证伪·high 域）；G/E 盘漏挂（他包）|
| ⑧ 翻译册 7290 | 漏挂375(9.4%)/悬空155 | — | 43 文件双盲（改门禁=high）+968 重复待 dedupe（册被他会话 staged）|

**入队 commit（实况见附录 B）**：q-…-0002 GOMAP ✅durable 在 HEAD(5f4136315e) / q-…-0001 工厂图⚠落 HEAD 后**热册蒸发**→q-…-0008 重投 / q-…-0003-0004 裁定册 ☠️死信（合并器结构无能，处方交总指挥+st-commitsys）。**align_all 在 HEAD 上：28 硬 → 3 硬（25 GOMAP 硬实清零 durable；余 3 皆 ruling related_arch 待 st-commitsys 修合并器）**。注：因工厂保护链全盲，q-0001 工厂修对 HEAD 的 align 数字无影响（factory axis 恒 0），蒸发不显红——即本包最重要的失明实证。

## ① TDM 交易决策图（第七图）
- 实测：182 节点 / 254 边 / 0 悬空边 / 0 重复 id / 121 module_ref 节点（111 distinct path）/ 96 module_id / PP-001 sleeves=16。
- **悬空=0** [亲验]：所有 module_ref 路径盘上存在 ∧ 在 depgraph；module_id↔depgraph blueprint_id 0 失配。
- **元发现（重要）[亲验]**：`check_decision_map._module_exists_in_depgraph` 查不存在的列 `nodes.module_id`→异常被吞→**fail-open 对垃圾 ID 也返 True**（R9 实为死检查）；真覆盖靠 R21 缓存，本审直连 PG 复核=干净。→ 该 gate 失明已入红蓝复核。
- **漏挂**：8/8 现役 StrategyMeta 全上图；[推断] strategy_registry 11 条 status=active 的 STR-* 未挂（地图标 pending-owner-adoption=刻意留空，登记）。
- **断链**：fw-tdm-current provenance sha12 陈旧（framework_plans.yaml:240/294=d8d65f0e8b53，map 现=b0f196b28e45；sleeves 内容 100% 一致仅指纹漂移）。修法=重跑 generate_framework_plan_from_tdm.py，**但 trading_decision_map 现被他会话 staged**→避连坐，登记不即时重跑。

## ② 工厂图（第九图 策略生产全景图）
- 实测：16 节点 / 原 15 边 / 10 层 / 6 车道 / 16 data_refs。E4 实况 c1_backtest.strategy_screen=1340 行（screened_in 381/deferred_c4 321/rejected 216/translated_c4 206/oos_tested 160/sim_deviation 52/failed_obsolete 4）。
- **断链①（已修）**：FAC-E1G「车道G-全网搜索进货」原为**全图唯一 0-in&0-out 孤立节点**——edges 只列 FAC-E1→{E1A..E1E} 漏挂 E1G（模块 MOD-AUTO-E1G-001 在 depgraph 真实存在，纯漏边）。已补 `[FAC-E1, FAC-E1G]`。**盲区**：validate_structure 不查连通性故 align 长期放行。
- **断链②③（已修）**：FAC-E8/FAC-E9 data_refs `c1_backtest.account_nav_daily`→`c1_market.account_nav_daily`（[亲验] CH：该表 EXISTS 仅 c1_market）。
- **悬空（登记·语义）**：FAC-E1 data_ref `c1_market.news_data` 全 CH 不存在（仅 news_sentiment_window）；改指向需确认进货语义，登记。**盲区**：check_stores 只校 store_refs 从不校 data_refs。
- **断链（登记·Owner 编号）**：FAC-E8 module_ref `MOD-PA-002..024` 闭区间超卖——depgraph 缺 PA-008/009/010/011/012/016/017/018/019（present 13/23），build_status=partial；需 Owner 核 PA 编号意图。
- built 锚点核实：E1A/E4/E5/E6 module_ref 全 depgraph FOUND，无假锚。

## ③ 企架图八册 + 治理运行地图（图10 GOMAP）
- align_all 真 exit=1 / 28 硬（基线红证）。分诊：
  - **GOMAP 25 硬 = 8 新增 + 17 漂移，0 幽灵** [亲验]：BLANKING-signal 空（重跑不会误清任何 domain/maturity）；scan() 从 `[DOMAIN]/[MATURITY]` 头注读，各漂移 scan 侧已填 → **头注是对的，yaml 才是陈旧快照**，「改头注迁就 scan」是循环论证。→ **重跑 generate_governance_map.py 一击清 25（已修，派生重建非手改）**。
  - **裁定 related_arch ×3（已验证处方·交总指挥落）**：#383 `['MOD-L00-004']`、#387 `['PS-CTR-003','MOD-INF-043']` 填了模块/契约号，违字段契约（line 53 明载 `关联 #ARCH-XXX 议题编号`），无对应 ARCH 条目、真身已在 affected_files → 置空 []（本地 align 3→0 已验）。**但队列合并器报死信**——ruling_registry 是总指挥 st-cmd 正活跃写入的热文件且命中已知合并限制 [[registry-collision-blocks-own-queue-fix]] → 回退本会话编辑、处方交总指挥随下笔裁定原子落。
  - **产业链 图8 数据层 12 硬违规**（S4×2 废弃链落位 / S11×9 死映射 .BJ 码 / S12×1）：全在 `ig_*`=产业链/长城写域，且 **st-chainpile-20260922 为活跃会话** → 避让登记，不代修。
- 各册悬空/断链（books 01/02/05/07/08/09）多为 **signal_ashare flat→nested 重构 + shared/migration/gov 脚本退役 + ruling#384 文档归档** 所致派生文档陈旧 → 处置=重跑各册生成器（机械），但 04/09/10 有他会话并发 M/D、且需先核哪些是生成物禁手改 → 登记为「派生文档批量重建」共享收口项。
- **漏挂（全册）**：顶层 `scripts/hooks`、`scripts/patrol`、`scripts/reports` 无任何册提及。
- **手编断链**：04/battle_map_positioning.md:60,492 → `file:///d:/临时工作区/…` 外部临时路径，登记重指 repo-relative。

## ④ 数据源注册表（四态：有注册/有表/有任务/有数据）
- 实读：DS 注册 23 / tasks.yaml 272 / CH live 表 237 [亲验 DatabaseService reader]。16 active 全四态齐。
- **CRITICAL 静默失效（高·prod·登记）**：有任务+有表但 **0 行** = `c1_market.suspend`（3 akshare 任务·universe 关键！）/`c1_market.etf_benchmark`/`c1_market.l2_tick`——调度在跑但采空表。属生产数据任务处置=high 门位。
- **漏挂 4（有表有数无注册·登记）**：crypto_binance(18431)/qmt_bridge(3899074)/alt_fx_ecb(96)/crypto_sentiment_panel(29)。qmt_bridge=执行域、crypto 疑他包；补登需架构受保护路径 [ARCH-APPROVAL]。
- **断链 3（登记）**：DS-EASTMONEY_DATACENTER 注册但 tasks.yaml:593 标 source=akshare（对不上）；placeholder 任务 margin/dragon_tiger/block_trade_qmt 指向不存在表。
- **伪悬空（已澄清·非洞）**：DS-BAIDUYUN（手工 bdpan 导入无任务=合规）、DS-IO_TABLE（`ig_io_edge` 在 PostgreSQL 非 CH，不是洞）。
- 反向：`generate_data_asset_coverage.py --check` total_missing=2 → c1_backtest.cohort_daily_ledger(170)/sim_daily_report(193) 未入 data_asset_registry。

## ⑤ 因子注册表（策略→因子→数据源三层依赖·Owner 点名重点）
- 机读：**175 因子**（本文件无 total 字段，实测）。
- **L1（册↔码）**：5 有 code_path 的文件均存在；但 **157/175 code_path 为空、171/175 inputs 为空** [亲验 yaml 复核吻合]。
- **L2（因子↔数据源）**：4 有-inputs 者中 3 个 crypto 因子依赖未注册的 crypto_binance；cross_market/ps_liquidity/institutional 目录 gate 在**已退役 iFind**（factor_design_state_complete.py:178）。
- **L3（策略→因子·头条）**：TDM 182 节点中 158 未声明因子，24 声明因子（32 distinct，全在册）但**仅 4/32 已计算** → **N=24 策略，0 个因子集齐备且有数据，24 个各有 ≥1 未算因子**。
- 诚实校准：157 空 ≠ 157 bug（含 planned backlog 规划件）；真缺口=L3 策略侧无一条因子链闭合。**不可自修**（逐因子建码+接数据源=大规模跨文件施工），登记。

## ⑥ 图书馆（lib_assets vs 全项目文件）
- 实测 lib_assets=43,945 / active 目录=33,534 / fs 盘=32,880。
- blind=3（2 新备份脚本+1）；**ghost=232**（229 盘验真已删，仅 3 假红 present-but-outside-scan；214 为轮转快照债 data/architecture_health 112+runtime_violation_snapshot 102；真代码/文档 ghost=8）。
- **生产代码文件覆盖率（新口径）**：tracked src+scripts .py=4,706，live 4,600 → **99.43% 覆盖，26 未覆盖=全部 `src/zephyr/<dom>/models/__init__.py`（非空）**。
- **根因·工具盲区**：fs_collector skip-word `"models"`（本为跳过 vendored ML 产物）静默丢弃真 `models/` 包 → 内置 blind 指标**结构上看不见这 26**（git 侧口径更强）。fs_collector.py 属 st-library 写域（本会话刚 salvage 其死锁）→ 登记。
- 红证：非零 + 注入探针触发 [亲验]。

## ⑦ 存储地图 INFRA-STORE-003 vs 四盘
- **硬悬空=0**（声明路径均在盘），但 3 处欠精：ch_backup_disk.vhdx 在 F:根（552.2GB 非 zephyr_cold 下）、disk2 在 G:根（503.2GB）、archive_manifest.jsonl 埋 50_archive/by_project/zephyralpha/。
- **漏挂（盘上有、图未名）**：G:\zephyr_cold=1297.5GB F:冷仓全镜像（自带 ch_vm_backup+60_mirror）；F:\zephyr_c4_pdf_cache；E:\ 各数据目录（cold_archive/c1_market/c3_fundamental/migration/ai_cache/OllamaModels）及 **E:\ZephyrAlpha 二仓副本**；worktree 脏 st-ff-*/wp12_lane/wp13_* 污染 F: 与 G: zephyr_cold。
- **⚠ 去重不安全（high·登记）**：阶段5「G 三份 ch_vm_backup 各 591.6GB 等值 1774.7G」的等值性**曾被三方 hash 证伪**[转报]；本审未重 hash（超只读 RO）→ **禁据 size 判重**，去重=删 2×591GB 属破坏性+high 门位。storage_map.md 属 st-backup 写域 → 登记。

## ⑧ 模块翻译册 vs 全部 .py
- 册 raw module_path=8,258，loader 去重可见=7,290 → **968 重复路径行塌陷**（`--dedupe` 可治）；无机读计数字段。
- in-scope tracked 生产 .py=4,000：**漏挂=375 缺翻译+2 泛化（9.4% 未覆盖）**，top：scripts/backtest/translated 29、src/zephyr/data 25、regime 23、ex_core 22。
- **悬空**：155 file-like 死翻译键（ex_core/* 重构批 + scripts/data/* 与⑥ghost 重叠）+74 dir-slash+4 锚点；29 depgraph 节点死 file_path。
- **门禁失明（关键·high·登记）**：runtime gate 仅 bootstrap-only（静默提交会报 0）；全仓 reconciler Layer-4 live=370 缺（不会假报 0，能红）；更深——**50 tracked in-scope .py 非 depgraph 节点 → reconciler 宇宙看不见，其中 43 又缺翻译 → 43 文件逃过 gate 与 reconciler 双重**。负控通过（探针→missing 触发；干净基线 3,625>0）。module_translation_registry.yaml 现被他会话 staged → 修 reconciler 宇宙覆盖=改门禁(high 域)+跨包补登，登记。

## 红蓝反证（§0.14 能红自证 / 审查器失明清单）
对 10 个「已挂齐/绿」结论做阴性对照：注入违规→看审查器能否报红。**关键副产品**：多个挂齐-checker 本身是盲的——**这直接威胁我两笔已落修的保护**（工厂连通性、data_refs 根本无人校验）。

| # | 被测结论 | checker | 判决 | 失明点 |
|---|---|---|---|---|
| 1 | GOMAP 424 模块对齐 | `_check_gomap_alignment` | **RED**（10 注入 8 触发）| 次要：counts 可撒谎/重复行不报 |
| 2 | related_arch 已清 | `check_governance_bidirectional` | **RED**（4 类触发）| 无——但**结论现=假：live 又 3 硬**（我回退的工作树未落，处方仍在死信件）|
| 3 | FAC-E1G 0 孤立 | validate_strategy_production_map | **GREEN-on-broken** | **是**：无连通性检查；FACTORY-MAP gate 复用同函数 |
| 4 | account_nav_daily 指对库 | 同上 check_stores | **GREEN-on-broken** | **是**：check_stores 只读 store_refs；全仓无 data_refs 校验 |
| 5 | 121 module_ref 全解析 | decision_map R9 | **R9 死检 fail-open**（垃圾也返 True）| 但结论非假绿：R19/R21 兜住垃圾路径/ID；根因 PG `UndefinedColumn: module_id` 被吞 |
| 6 | 覆盖 99.43% | fs_collector+set diff | **mixed**：集合差 RED；26 `models/__init__.py` 结构隐形(0/26) | **是**：`_SKIP_DIRS` 裸词 `models` |
| 7 | 370 缺翻译 | translation_coverage_reconciler | **RED**（注入触发）| 次要：`__init__.py` 豁免 |
| 8 | 16 active 健康 | generate_data_asset_coverage + R11 | **partial**：CH→册 RED(exit1)；**册→CH GREEN**（幽灵表+0行 suspend 不报）；**data_sources_registry 不在被校 19 册内** | **是**：反向存在性+空表静默失效无闸；R11 warn-only |
| 9 | 命名/frontmatter | C-02/C-04 per-file | **RED** | 是（模式）：目录名规则仅 `--scan` 触发，per-file 漏 |
| 10 | 因子 code_path 在 | `check_registry_code_anchor.py`（真checker；`factor_design_state_complete.py` 实为 depgraph **写器**名不符）| **mixed**：锚点 RED×4；全空 PASS=设计正常；junk `inputs`→**GREEN** | **是**：inputs 全仓无校验 |

### (A) 证为可信（能红）
GOMAP漂移 · related_arch双向 · TDM R19/R21 · 库 blind/ghost 集合差 · 翻译全仓 reconciler · frontmatter/命名(文件名) · 因子代码锚 checker。

### (B) 证为失明 → 审查器缺陷（各带一行修法；均属「改判定逻辑/门禁行为」或他包写域 → §0.15 上交登记，不擅改）
1. **#3** validate_structure 加连通性 pass（in∧out==0 且 built/partial→_err）；gate 自动继承。**← 保护我 FAC-E1G 修的前提**。
2. **#4** check_stores 兼校 data_refs（`c1_*.`→EXISTS TABLE，否则路径存在），或把工厂并入 `_check_data_existence`。**← 保护我 account_nav_daily 修**。
3. **#5** 修 `_SQL_CHECK_MODULE_EXISTS` 用真列（blueprint_id/node_id）且 SQL 语法错要抛不吞；否则删 R9 并入 fail_open_register。
4. **#6** fs_collector._SKIP_DIRS 裸 `models` 换成 vendored 显式白名单（属 st-library 写域，避让登记）。
5. **#8** 加 `--check-reverse`（entity_name→EXISTS TABLE，0 active parts→warn/red）+ 把 data_sources_registry 纳入 REGISTRY_SPECS。
6. **#8/R11** 「声明 active 但 0 行/无表」升 error，止住 suspend/etf_benchmark/l2_tick 静默采空滑入 warn。
7. **#9** check_naming_convention per-file 也校验每段路径名。
8. **#10** 加 inputs 引用闭包校（对 data_asset/data_sources 册）；把 factor_design_state_complete 从因子校验引用中摘除（它是写器非校验器）。
9. **#1 次要** GOMAP counts 对账 families + 报重复 path 行。

> **红蓝净结论**：我 2 笔落修本身正确且 align 亲验，但其**保护网（工厂连通性/data_refs 校验）不存在**——已作为高优先处方登记（B1/B2），否则同类断链将再次静默滑过。审查器失明清单是本次「挂齐」在元层（挂齐-checker 自身的挂齐）的实质交付。

本项目 100% AI 多会话并发（审查时活跃 5+ 会话、主区 index 583 件 staged、1295 脏件）。本包按 §3.4「他会话在途违规不代修」+§0.8 门位笼子执行：凡命中「其他在飞包写域 / 大规模建码接线 / 生产数据 / 门禁旗 / 备份去重破坏性操作 / 架构受保护路径补登」者一律带证据登记，交总指挥调查或转 Owner。这是**专业 diligence 而非偷懒**——盲改他包/高危面才是事故源。可自修的机械可证项（工厂断链、GOMAP 派生重建、裁定悬空引用、自产件 frontmatter）已全部当场修并入队。

---

# 附录 A · 自动化轮次追加发现（depgraph 轴，2026-09-24 01:38–01:52，30min cron 自主执行）
本包自挂监控自动化在监听总指挥批注（R2/R3）期间，沿 depgraph 数据轴再挖出 4 条**图↔物**级发现（超出八图原册，属"挂齐"的更深实物面），均登记上交（非本包写域/高影响面）：

- **F-AUDIT-DEP-01【门禁判据与文案错位 → 提交级联阻断·交 st-commitsys，并入失明清单第 11 条】**：`check_frontend_map.py:111` R4 把**过滤后的子集**当"模块全集"判在册性 → 任何"有前端引用但 depgraph 未标 frontend 覆盖"的在册模块必被判幽灵（红）。实证 `MOD-INF-037` 在 depgraph 有 **183 节点（含 12 blueprint）但 `has_frontend<>'no' OR frontend_ref<>''` 计数=0** → 门禁判"不存在"。**放大面**=FRONTEND-MAP `own_scope:false`（全仓扫描）+ 非 worktree 落地读主区脏工作树 → **全仓提交级联阻断**（st-gpu-final 自证"代修解 MAP-ALIGNMENT 全树阻断"）。处方：①文案区分"未在册"vs"在册未声明前端覆盖"+给可执行出口；②存在性判据与覆盖判据拆两条。**探针纪律留痕**：首计数误用不完整谓词得 0、后用原样谓词复核仍 0（数字可靠），但过程证明"抄近路改 WHERE"是这类对账第一号假红源。[亲验]
- **F-AUDIT-DEP-02【字段级系统悬空 119/119·交 st-cmd/st-commitsys】**：depgraph `nodes` 表 `node_type='blueprint'` 119 行 `blueprint_path` **100% 盘上不存在**（值为合成 `docs/03_modules/<ID>/` 目录形态，真身约定 `docs/03_modules/_domain_x/<name>/blueprint.md`，盘上真 blueprint.md 共 544）；`blueprint_links` 表 1707 行悬空 **102**，且 **102/102 皆同一合成形态**（其余 1605 真实存在）→ 病灶单一、形态可机判。≥4 消费方读该字段（depgraph_schema / audit.reconciliation_registry / autonomy_core.skills / blueprint_code_sync），读空即**静默降级**（同 [[ch-query-fails-soft-trap]] 族）。**自审更正**：机制是**解析**得来非硬编码伪造，只陈述可观测面、不断言生成器撒谎。修复=解析真身或双写规范形态。[亲验]
- **F-AUDIT-DEP-03【滥挂/错挂·6 ID 吃 73 目录】**：46 distinct blueprint_id 承载 119 blueprint 目录 → 6 个 ID 各挂多目录（`MOD-L02-001`×43=整个 factor 族 / `MOD-DATA_ENG`×13 / `MOD-INF-037`×12 / 余×2/×7）。后果=任何按 module:/blueprint_id 寻址的对齐轴（R4/⑤因子三层/前端归属）对 73 目录不可分辨=图↔物多对一退化。**双证坐实错挂非设计意图**：`MOD-INF-037` 注册表唯一身份=Registry Governance（module_translation:8991 + issue_registry:9 owner + 真身蓝图 registry_governance/blueprint.md），depgraph 却又挂它 12 个别的目录→互斥。`MOD-L02-001`×43 同形待同判。须先定"一族一蓝图"口径 → 上交。[亲验 部分（MOD-INF-037 坐实）+待判（L02）]
- **F-AUDIT-DEP-01b【解债无登记·上交】**：某会话降级 `module:MOD-INF-037`→`none:…归位后改回` 的**回挂义务只存于一条 free-text 注释**，未落 ARCH 议题/无裁定号/无 tracker → 按"临时降级+口头回挂必腐烂"（先例 [[hot-file-wipe-forensics]]），处方=登记一条 ARCH 议题（触发=MOD-INF-037 前端覆盖归位，动作=改回 module:）。本包不代写他包议题（§3.4）。

# 附录 B · 收官阻塞态（诚实·跨包依赖，非本包缺陷）
自动化监听 R2/R3 批注后的**实况**（更新 02:30 CST）：
- **q-0001 工厂 / q-0002 GOMAP**：q-0002 ✅ durable 在 HEAD（423 自洽，st-align-dirty 复投 ef85cda27b）。**q-0001 工厂 ⚠ 热册蒸发复发**——QA 亲验：00:04 落 HEAD(90889679b2) → 00:19 被 st-library(stale-snapshot)、00:43 被 st-k4 回退 → HEAD 退回 15 边/E1G 孤立/2 坏 ref 的破块。**因工厂保护链全盲（红蓝实证：validate_structure 无连通性检查、check_stores 不校 data_refs、FACTORY-MAP gate 仅包 validate_structure、lane-G 测试只断节点不断边），蒸发无人拦**。本包 02:30 重投 = q-…-0008。**durability 真闭环依赖 B1/B2 失明处方（st-commitsys）**——否则配置面热册蒸发将继续静默。
- **ruling related_arch ×3（q-0003/0004）**：☠️ dead **同因**——队列三向合并器对 `ruling_registry.yaml`（`ours`=dev 基线）有**结构性身份判据无能**（[[registry-collision-blocks-own-queue-fix]]），与本包编辑内容无关；R3#1 已由 **st-commitsys 领修合并器**（"单元素标量族 passthrough"）。合并器修好→requeue 0004→align 3→0。**非本包可自解**（换任何编辑重投必死同处，已停手不刷屏）。
- **battle_map file:/// 断链（q-0005）**：☠️ dead——被**外来 staged `frontend_map.yaml` 的 R4 假红连坐**打死（F-AUDIT-DEP-01 同源）。待 st-gpu-final 该批落 HEAD → requeue。袋字节完好，教科书级 blob 三重验证（R3#3）。
- **R3#2 外部真源指针标注**：让窗——`construction_workflow_policy.md` 工作树含**他会话 13 行在途未提交**，加注释即吸收外来内容（§2.5 连坐），反向回写即冲掉他包活（§3.4）→ acquire 后 release，请总指挥排窗。**净证据支持"保留"裁决**：外部指针族实为闭合设计（backup_config.yaml:104 + asset_inventory OFFREPO-TRAE-MEMORY:179 + scan_offrepo_assets.py:42 三处一致在册），非孤儿针。
- **align 现算硬=3**（全为 ruling #383/#387，等合并器修复）；soft warn≈987 存量。

**本包结论**：八图 + depgraph 数据轴的图↔物对账已**穷尽本包授权**；所有可自修机械项已尽（工厂/GOMAP/自产 frontmatter），其余全部带证据路由到**领域属主包 + 总指挥批注闭环**（ruling→st-commitsys 合并器，library→st-library，storage→st-backup，失明清单→st-commitsys，数据源→st-gpu，产业链→st-metaq）。**Owner 晨起案头无待裁**——残余项皆为跨包属主工，经自动化+总指挥编排推进，符合"无需人工参与"。**30min cron 持续监听，合并器修复后自动完成 ruling 落地复核+收官自删。**

---

# 终局更新 U（2026-09-24 04:18–06:13 CST · 自动化轮次 R4–R9）

> 本节**取代**上文 ⑧（翻译册）与"全局修复统计"表中与图↔物计数相关的早期数字，并把对账面从 8 本 YAML 册**扩到第二张图 depgraph（PostgreSQL，架构轴真图）**。上文原文保留作审计轨迹，不删（防"报告自己制造悬空"）。

## U0 口径更正表（先立此，防文档自相矛盾＝§4.3 事故源）
| 项 | 早期口径（02:30 前） | 终局口径（切片后） | 更正原因 / 证据等级 |
|---|---|---|---|
| 八图 D1 悬空总量 | 785 | **164**（165 减 1 条我尺假阳性） | 原尺对整册文本跑路径正则，把 `creation_tokens` 台账收据正文当图边；[亲验] 尺=`probe_dangling_v2_fieldslice.py` |
| 八图 D2（仅工作树） | 278 | **110** | 同上 |
| ⑧ 翻译册"悬空 155 file-like 死键" | 155（loader 可见口径） | **152**（HEAD 文本口径）→ 三分 45/71/31 | 两把尺口径不同不矛盾：loader 去重前 8,258→7,290 可见；本处用 HEAD 原文 [亲验] |
| ⑧ 翻译册"漏挂 375/9.4%" | 缺**翻译**的 tracked .py | 不变（不同命题）；另加 depgraph 侧漏挂 **55/4,680=1.2%** | "缺翻译"≠"图上无节点"，两者是两回事，此前混称"漏挂"是本包自己的措辞缺陷 [亲验] |
| `docs/_working` 被永久册引用 542 条 | 判为 SSOT 方向错 | **作废**（599/603 行在台账正文，业务面 canonical_override 命中=0） | 判据前提被证伪 [亲验] `probe_d1_working_ttl_verdict.py` |
| BAG-01 落地诚实率 | 35.5%（11/31） | **24.6%**（268 对，剔合成会话） | 窄窗+含压力测试袋；比率须带 窗口/是否剔合成/分母 三要素 [亲验] |
| 审查器"能红"证据 | 各门阴性对照 10 项 | 加 **尺自检器**（14 真判+1 有意负例） | 判通过的尺须自证能红 [[autoclaw-btfix-campaign]] 立法 [亲验] |

## U1 三清单终稿（图↔物两张账）
### A. 悬空（册/图挂了、物不在 HEAD）
**A-1 YAML 册侧 164 条**（HEAD 侧字节，`dangling_v2_lists.txt` 全量）
| 归属 | 条数 | 定性 | 处置状态 |
|---|---|---|---|
| module_translation_registry | 152 | 三分见下 | 高域（册净删）＋他包在途写域 → **登记上交** |
| ├ R_改名未同步 | 45 | 物在新址、旧路径未销（vms 族 8、ex_core/adapters→governance/adapters 2、ex_sor/core→api 1…） | 处方=改名后自动跟随（同 RULE-DEPGRAPH --force 思想）；[亲验] |
| ├ H_退役未销册 | 71 | 物曾在可及历史、后被删（含 3 个退役 gate、`_archive/vms_ri` 族） | 3 条已点名到 commit+行号＝MTR-02；[亲验] |
| └ N_从未落地 | 31 | =5 他包死信件（st-t0-matrix 0007/0008，等其落地自愈）+25 真幽灵+1 我尺假阳性 | 25 真幽灵待 Owner/属主裁"补建 or 销册"；[亲验] |
| capability_canonical_file_registry | 8 | 业务面切片后仅剩 8（早期报 628） | 量级已从"缺陷"降为"待逐条判"；[亲验] |
| GOMAP / gate_registry / TDM | 1 / 1 / 3 | 各 1–3 条，TDM 含 1 条指向 `docs/_working` 的散文 | 逐条轻修或标注；[亲验] |

**A-2 depgraph DB 侧**（`granularity='file'` 节点 ↔ `git ls-tree -r HEAD` ∧ 盘上 ∧ `git log --all --reflog --diff-filter=A`）
- 反向（图挂物、HEAD 无件）= **183**；分层后自明 173（`on_disk` 128 本机/生成件 + `planned` 26 + `deprecated` 19，**后两类是生命周期位的正确用法，不计缺陷**）⇒ **真需处置 = 10 条**，逐案三分（`depgraph_hard_subset.txt`）：
  - 移动未跟 **4**：`commit_gates/{library_blood_flesh,tag_vocab,state_vocab_registry}_gate.py`（旧节点仍标 production，新址 `commit_gates/library/` 亦有节点＝**新旧双节点并存**）、`registry_family/registry_mass_deletion_gate.py`（已移回）。
  - 退役未更 **3**：`{data_task_completeness,issue_resolved_integrity,library_coverage}_gate.py` 仍标 `production`，实由 `4b8fb00a555`(批A) 删、`9b0c31ab125`(批B) 只除名 YAML 三册**未回写 DB**。
  - 从未在 HEAD **3**：`scripts/backtest/sector_prereg_exam_runner.py`（标 **production**，其唯一添加件 `f44c1bfd742` **非 HEAD 祖先**＝只在未合并会话分支）、`scripts/data/backfill_option_daily_stats.py`、`src/zephyr/alt_data/emotion_index_replay.py`（标 testing，全 ref `--diff-filter=A` 零命中）。
- **10 条里 7 条是门禁文件自身** ⇒ 治理资产自己的图↔物一致性最差，这是本次"挂齐"在元层最锋利的一条。[亲验]

### B. 漏挂（物在、图上无）
- depgraph 正向：**55 / 4,680 tracked 生产 .py = 1.2%**（`src/zephyr` 40 / `scripts/industry_graph` 10 / `scripts/ch` 4 / 散件 1）⇒ 量级健康，非系统性洞。[亲验]
- 翻译册"缺翻译"口径：375（9.4%）不变，top：`scripts/backtest/translated` 29、`src/zephyr/data` 25、`regime` 23、`ex_core` 22。其中 **43 文件逃过 gate 与 reconciler 双重**（50 tracked .py 非 depgraph 节点 → reconciler 宇宙看不见）。[亲验]
- 存储/数据源/图书馆族漏挂：见上文 ④⑥⑦，未变（他包写域/需 [ARCH-APPROVAL]）。

### C. 断链（挂错、指错、跨面不同步）
- 工厂图 3 处（E1G 孤立边、`account_nav_daily` 两处指错库）＝**已修已落 HEAD**（`90889679b2`）。
- battle_map 手编 `file:///d:/临时工作区/…` 2 处＝**已修已落 HEAD**（`8639ed73c7`，HEAD 复测 `file:///` 命中=0）。
- GOMAP 机生层 25 硬＝**已修已落**（`5f4136315e` 重跑）；align 全图 28 硬→**HEAD 口径 0**（工作树余 3＝热册在途，非本包欠账）。
- **跨面同步断链（本轮新增，最重要）**：退役动作在 gate 两册已同步、在**翻译册与 depgraph 均未同步**（MTR-02/DEPG-01 同一笔账，可点名到 commit+行号）；以及"图读面"自身：`related_arch` ×3 处方已由 `9b0c31ab125`/st-cmd 面处置（HEAD 口径 0）。[亲验]

## U2 本轮新立案（6 项，均带判据）
1. **F-AUDIT-DANG-02**：`capability_canonical_file_registry.yaml` 47,163 行中 **42,018 行（89%）是 `creation_tokens` 台账**；整册正则扫描假边率 96%（9,790 refs → 业务面 363）。结构因＝**审计收据与查询真源同册**，双害：①扫描污染 ②每个新建文件批必写此册＝热册拉锯放大器（HEAD `a94d18ef1b` 自述"热册拉锯第二次实证"即此路径）。
2. **F-AUDIT-MTR-01**：翻译册 152 条真悬空三分定性（45/71/31）＋其根因＝单批 `ab168e55c8`(08-01 14:03)「双语真源扩容」**一次灌入 2,978 条 `module_path`，而该批 11 个文件全 `M` 零 `A`**（一条 .py 都没新建）⇒ 登记来源=文档/蓝图应然清单，非磁盘派生。152 条中 56 条（37%）出自该批。
3. **F-AUDIT-MTR-02**：批B `9b0c31ab125` 名曰"注册表除名"，实改 13 件中 `_registry/catalogs` 仅 3 册，**翻译册命中 0** ⇒ `module_translation_registry.yaml:55798` 至今挂着已删的 `library_coverage_gate.py`。
4. **F-AUDIT-MTR-03**：**全仓无"册→物"方向校验**——`translation_coverage_reconciler.py:251` 是 `for node in nodes:`（depgraph 驱动，方向严格 物→册）；`gate_registry.yaml` grep `module_translation` = **0** ⇒ 入口无存在性闸、存量无销旧 ⇒ **悬空单调递增**。
5. **F-AUDIT-DEPG-01**：depgraph 双向账（U1·A-2）＋**机制＝两套图共缺"销旧"这一半**（YAML 无册→物校验；DB 重建不删消失路径＝4 条双节点并存为直接实证）＋**DB 快照源越界**（非祖先会话分支的件可写成共享架构真源并标 production，与 [[merge-relay-via-queue-pattern]] "`--worktree-root` 才是快照源"同证）。定级 **P1 候选**。
6. **F-AUDIT-STASH-01 / F-AUDIT-IDX-05**（提交面第四、第五形）：死会话 stash 标称 14 行实为 **663 文件/+236,564/−5,305** 全树回退弹（两向皆毁，只登记）；主区 index 里 **12 件已跟踪件字节恰=会话起点 `f017ce3bf7` blob**（含 **AGENTS.md 宪法**、GOMAP 落后 48 行、`yaml_utils.py` 落后 70 行、`library/lookup.py` 落后 50 行，合计约 **278 行已落地工作**停在 index 之后），本包名下 2 件（LEDGER index=22 行 vs HEAD=747 行）**已现场拆除**（盘==HEAD 亲验后 `git add -- <自家两件>`）。机制假设"enqueue 写主 index"**已被否证**（`commit_queue.py:694` 入袋走 `blobs/<sha256>`；`git_commit.py` 无 `git add`），余"首次 staging 后无人回写"为未证候选 ⇒ 交 st-commitsys。
   - 6b：**编号险撞**自记——本块初稿命名 IDX-04，被追加脚本的幂等 MARK 检查挡下（04:28 已立 F-AUDIT-IDX-04）⇒ 新立 F-AUDIT-* 前须 `grep -oE "F-AUDIT-[A-Z0-9]+-[0-9]+" | sort -u` 取 max+1。**门能红的正例**。

## U3 修复统计（本包今日落地 14 笔 commit，全走 `git_commit.py --enqueue` 正门）
| 面 | 笔 | 内容 | 复测 |
|---|---|---|---|
| 工厂图 | `90889679b2` | E1G 补边 + `account_nav_daily`→c1_market ×2 | align 亲验 |
| GOMAP | `5f4136315e` | 机生层重跑 25→0 | align 硬 28→3 |
| 裁定册 | `a74e9a6c48`/0011 | `related_arch` ×3 置空 | HEAD grep=0（工作树余 3 为热册在途） |
| battle_map | `8639ed73c7` | 2 处 `file:///` → repo-relative | HEAD 命中 0，单件零连带 |
| 案卷 | 9 笔 | LEDGER 心跳块 6 个（04:56/05:09/05:29/05:41/05:48/05:53/06:02/06:09）+ 更正块 | 每笔 `--name-only` 核归属，纯增零删 |
| 排雷 | 2 件（非 commit） | 自家 index 回退弹拆除 | `git ls-files -s` 指回 HEAD blob |
**本包写域纪律实测**：对 `注册表/配置册` 类路径写入=**0**；对 depgraph DB 只 SELECT；对他人 staged/claim/在途批零触碰（`governance_operations_map.yaml`/`trading_decision_map.yaml` 未碰）。

## U4 剩余 / 待裁清单（要 Owner 或属主点头的，逐条给"这是什么/为何要点头/不点会怎样"）
1. **25 条真幽灵（ex_core 16 等）**：翻译册里挂着**从未存在**的模块，有中文名/大白话/责任层。要裁的是"这批是要建的（补 `build_status: planned` 标注）还是幻觉（销条目）"。不点＝全景图与前端反查继续展示不存在的执行器（`execution_mcp_server`/`rl_optimal_executor` 这类最像"我们已经有"的）。
2. **退役三闸的跨册补销（MTR-02/DEPG-01）**：文件已删、gate 两册已除名，但翻译册 1 处 + depgraph 3 节点仍称其在役。补销＝注册表净删＋DB 改，双 high ⇒ 须 Owner 批准由谁同批做。不点＝退役面永远查不干净，且下轮审查还会把这些当"在册"。
3. **depgraph 快照源越界（P1 候选）**：未合并会话分支的文件被写成共享真源并标 production。要定"DB 只能由 HEAD/落地后权威树生成"这条写入边界。不点＝A 会话的实验态可污染全场架构真源。
4. **台账/索引分层（DANG-02）**：42k 行 CREATE-GUARD 收据是否从 `capability_canonical_file_registry.yaml` 迁出独立册（迁出＝该册净删，high）。不点＝任何整册扫描继续 96% 假边、热册继续当写磁贴。
5. **死会话 stash 定向处置（STASH-01）**：663 件回退弹，pop 毁已落地面、drop 毁唯一在途副本 ⇒ 须属主/Owner 定向按件提取。
6. **裁定 409 全文只活在未提交面**（06:02 块 ④ 已交裁，等路由）；其配套 3 件同批原子须指定会话走正门（`RULE-RULING` 要求同 commit）。
7. 上文既有他包项未变：⑤因子 L3 0/24 链闭合、④三空表静默采空、⑥models skip-word 盲区、⑦dedup-by-size、43 文件双盲。

## U5 红蓝反证（终局 17 例 + 尺自检器 + 失明清单增量）
**能红自证（正门件）**：`redblue_ruler_selfcheck.py` = 14 真判（三把尺各含阳性/阴性对照）+ 1 有意负例（`want=999` 必红，实测 `[SELF-RED] +1`），exit 码可直接进门禁。
**自我否证 17 例**（全部为审查器自身缺陷，非被审对象）：①时钟外推 ②探针 v1/v2 自否 ③v3 负例三选错 ④"门读 index"逮到自己案卷未落 ⑤GEN-02 收录假阴性 ⑥DANG-01 主动否证"三闸静默失效"（P0→P2）⑦BAG-01 比率 35.5%→24.6% ⑧`files[].sha` 假字段造出"袋面丢失" ⑨DANG-01 台账正文当图边（785→164）⑩PATHRE 抓模板省略号 `src/zephyr/.../xxx.py` ⑪改名判据 basename 太松造 11 条假改名 ⑫漏挂尺只取 `node_type='module'` 造 22.9% 假漏挂（真 1.2%）⑬`--diff-filter=D` 误判"从未存在" ⑭断言数写死 16 实为 14 ⑮手工补正计数致文案不符 ⑯"enqueue 写主 index"假设被代码否证 ⑰编号险撞 IDX-04 被幂等闸拦下。
**失明清单增量（接上文 (B) 9 条之后）**：
10. **无"册→物"反向校验**（MTR-03）：给 `translation_coverage_reconciler` 加第四类漂移 `registry_only`，不新建 gate（§4.1 净零）。
11. **depgraph 重建不销旧节点**（DEPG-01）：重建须删除"路径不存在 ∧ 状态非 planned/deprecated"的节点；RENAME-DEPGRAPH-SYNC 现只查"改名批有没有跑重建"，不查"重建后旧节点是否消失"。
12. **退役跨面同步无闸**（MTR-02）：退役批的"注册表除名"清单应机生（含翻译册/depgraph/03_modules 卡片），现靠批注人肉列。
13. **主区 index 当第二真源**（IDX-05）：落地后触及路径 index 未回写 ⇒ 12 件停在会话起点 blob。处方二选：落地后对齐 index 到新 HEAD，或禁主区 index 承载非当轮字节。
14. **台账与索引同册**（DANG-02）：`creation_tokens` 迁出反查册（涉净删，high 门位）。
15. **stash 无规模自证/无归属**（STASH-01）：消息须带 `files=<n>` 或由 `session_worktree_*` push 后回写；watchdog 应把死会话名下 stash 纳入可见面。
16. **GATE-01 无草稿区豁免致"记录某裁定尚未落地"都要改拼写**（第三例红证，`#NNN` 自触）——已在本包 0012 死信实证。

## U6 复查清单（Owner/属主逐条可自验；含"我可能错在哪"）
| 结论 | 复核命令 | 可能错在哪 | 证据等级 |
|---|---|---|---|
| D1 真悬空=164（非 785） | `python .runtime/tmp/audit_all_20260924/probe_dangling_v2_fieldslice.py`；`grep 合计 .../dangling_v2_fieldslice.txt` | 切片按"顶层键 `creation_tokens:`"一刀切，若某业务字段恰在该段之后会被漏算；已用 note 行反向断言"宁多报不漏报" | 亲验（两跑同值） |
| 152 条三分 45/71/31 | `python .runtime/tmp/audit_all_20260924/probe_translation_d1_verdict.py` | 改名判据依赖"唯一非泛名同名"，真改名若同时重命名则退化为 H | 亲验 |
| 幽灵出自 `ab168e55c8`（2978 条/零 A） | `git show --format= --name-status ab168e55c8 \| sort \| uniq -c`；`git show --format= ab168e55c8 -- <翻译册> \| grep -c "^+ *- module_path:"` | "应然清单灌入"是从"零新建 .py + 2978 条"推的动机，未找到当时生成器命令行 | 亲验事实 + 推断动机 |
| 批B 未销翻译册 | `git show --format= --name-only 9b0c31ab125 \| grep -c module_translation_registry`（=0） | 无 | 亲验 |
| 无册→物门禁 | `grep -c module_translation docs/.../gate_registry.yaml`（=0）；`sed -n '249,262p' src/zephyr/governance/audit/translation_coverage_reconciler.py` | 可能有非 gate 的 reconciler 做此事而我未穷举全仓 | 亲验（限定于翻译册族） |
| depgraph 硬悬空 10 条 | 见 06:02 块 ② 的内嵌脚本 | DB 是**当前态**，其它会话可能在跑重建；复跑若变小说明部分自愈 | 亲验（时间戳 06:01） |
| 漏挂 1.2% | 同上（正向那三行） | 依赖"全 node_type 路径并集"口径，与 ⑧ 的"缺翻译"不可混用 | 亲验 |
| index 12 件停起点 blob、落后 278 行 | `git ls-files -s` × `git ls-tree -r f017ce3bf7` 集合交集（06:09 块 ③ 已给法） | 起点号取自本会话台账首行，若会话起点判断错则交集口径随之错 | 亲验 |
| STASH-01 663 件 | `git stash show --stat 'stash@{0}' \| tail -1` | 只点验 3 件内容，其余 660 件未逐件看 | 亲验（规模）+ 抽查（内容） |
| Owner 裁定 409 只活未提交面 | `git show HEAD:docs/.../ruling_registry.yaml \| grep -cE "MOD-L00-004"`=0 且盘上 `git hash-object` != HEAD | 见 05:29 块；文件正被多会话热写，读数须带时点 | 亲验（05:29 时点） |

## U7 终态判据自查（诚实版）
- ✅ 八图 + **depgraph 第二张图** 双向对账已做（超出指令原范围，属本轮最大增量）。
- ✅ 红蓝反证正门件跑通（尺自检器能红、揪出 8 项失明增量、17 例自我否证）。
- ✅ 本包可自修项全落（14 笔 commit，HEAD 侧零欠账；0019–0022 全 done）。
- 🟡 **收官判据逐条对表（严格读法）**：①"全部应修落地"＝本包授权内可自修项全落 ✅；②"align_all exit0 或仅剩已登记他包/门位项"＝现余 3 硬＋第 6 步崩，**两者均为已登记他包项（st-cmd 裁定册 / st-ailayer BLIND-01）**，按括号内口径判 ✅；③"**自审清单二次＝0**"＝图↔物三把尺 05:5x 与 06:05 两轮同值 ✅，**但 06:0x 那一轮本身又立了 MTR-01/02/03、DEPG-01、IDX-05 五案 ⇒ 该条未满足**，须以"本节落地之后再跑一轮、且该轮零新立案"为准。
- ⇒ **自动化处置（不提前自删的理由）**：终报本节已写完并交付，但 ③ 未闭合。下一轮只做三件事：**复跑三把尺 + 复跑尺自检器**（命令在 U6/U5），若该轮零新立案 ⇒ 立即在台账写"自动化已自删·本包收官"并 `qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076`；若仍有新立案 ⇒ 继续（守"全部任务完成前不停止"，不空转）。U4 七项待裁**不阻塞收官**——它们按 §5/§3.4 本就不属本包可自修面。
