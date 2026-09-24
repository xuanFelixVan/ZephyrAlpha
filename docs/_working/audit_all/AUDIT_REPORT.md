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

---

# 终局更正 V（2026-09-24 06:36 CST · 收官第 2 轮复跑触发）

## V0 口径更正（追加进 U0 表，本条更正的是**本报告自身**的归因，非被审对象）
| 项 | U 节原写（06:13） | 更正后（06:36 实测） | 证法 |
|---|---|---|---|
| `align_all` 第 6 步崩 | "第 6 步崩（st-ailayer BLIND-01）"，并据此计入判据②"仅剩已登记他包项" | **HEAD 侧不崩**：崩因＝主区工作树+主 index 里一段 +15 行**未提交**钩子（`align_all.py:695-709`）在 `main()` 内 `from … import run_subprocess_hidden`，使该名字在整个 `main` 内变局部 ⇒ 第 536 行（钩子 `try` 之外）先用后绑 ⇒ `UnboundLocalError` ⇒ **第 6/7/8/9 步永不执行、`align_all` 恒 rc=1、总览报告永不落盘** | 三证：①`git show HEAD:…\|grep -n` 只 100/536/556；②`symtable`：HEAD 版该符号 `is_global()=True`，工作树版 `is_local()=True`（不靠运行）；③第 6 步载荷 `check_doc_node_id_hardcode.py --ci` 直跑 **rc=1（FOUND 2/1791，存量 WARN）而非 traceback** ⇒ 第 6 步可用 |
| 该钩子的"非阻断"自述 | 未质疑（照注释引用） | **被证伪**：`try/except` 只覆盖 695-709 自身，遮蔽在 536 发作 ⇒ 兜不住 ⇒ 阻断级。属"加钩子的人不会在自己那一段看到症状"的远程致盲 | 代码结构 + traceback 行号 |
| 三态归属 | 记为他包已落地缺陷 | `HEAD` 无 ｜ serializer worktree 无 ｜ **全部 7 个 `.aidrafts/*` 会话快照均无** ｜ 只有主区工作树+主 index 有 ⇒ "只活在第二真源里"；任何吸收该路径的提交都会把崩写进 HEAD（与 IDX-05 同根第六面） | `grep -c gen_search_veins` 逐树点验（主区=1，其余=0） |

## V1 新立案 F-AUDIT-WIP-01（P1 候选，路由 st-ailayer-final-20260924 + 同时交总指挥路由收棚方）
- **症状面**：全场以 `align_all` 为收官判据的包（含本包、st-align-dirty、st-commitsys）今晚测得的"第 6 步崩"**同因**——不是各自代码问题，也不是 HEAD 缺陷。
- **处方（一句）**：删 697 那行冗余函数内 import（模块级第 100 行已提供同名符号，删后行为不变）；或把钩子挪进独立 helper 使绑定不进 `main()`。§3.4 不代修（属主在途件；其 `.aidrafts` mtime=00:39、进程表无该 sid ⇒ 疑已散会，故须收棚方）。
- **附带第二面（同批半截态）**：钩子产物 `config/ai_search_veins.yaml` 盘上有 / index 无 / HEAD 无，而 `capability_canonical_file_registry.yaml` 已挂指针 ⇒ 尺A 早已列为悬空样本 ⇒ "钩子进 index、产物没进 index"的跨文件原子性半截（与同窗 st-commitsys-0018 死于 `IMPORT-INTEGRITY 悬空 import` 同族，差别在这条**在 index 侧不可见**）。

## V2 尺D＝全仓"函数内 import 遮蔽"AST 扫（新增，8,537 个 .py）：**全仓仅此 1 例**
- 判据：某名字在同一函数**自身作用域**内被 import 绑定，且绑定行之前已有 Load ⇒ 运行到即 UnboundLocalError。
- **反证第 18 例（分母虚高 26 倍）**：v1 得 27，逐条点开实为**函数签名的返回/参数注解**（`def f(x) -> datetime.date:` 配体内 `import datetime`、`exam_orchestrator.py` 两处 `-> HallucinationBreakdown`）——注解在 enclosing scope 求值，永不崩。⇒ 修＝只走 `fn.body`、不下钻嵌套作用域。
- **反证第 19 例（控制组逮到自己写错分支）**：v2 跑四条控制，"嵌套作用域"阴性 **FAIL(got=1 want=0)**——`isinstance(node, skip)` 被我写在 `iter_child_nodes` 下钻分支，而 `fn.body` 顶层元素直接 yield 未经过滤 ⇒ 嵌套 `def` 仍被下钻。修＝在 `pop()` 处过滤 ⇒ 四控制全 PASS 后重跑得 1。
- **失明增量第 17 条**：**pre-commit 只有 ruff，ruff 无 `used-before-assignment` 等价规则**（本窗两条 dead 队列项 `dead_reason` 实测 `hook=['ruff','ruff-format']`）⇒ "改作用域的钩子"零门可拦。建议（§4.1 净零、不新开册）：尺D 作 own-scope 结构门挂进既有 AST 结构校验族，**全仓现值=1 ⇒ 上线噪声近零**。

## V3 收官第 2 轮复跑（06:22–06:34）＝三把尺零新问题
尺A 业务面 **D1=165/D2=110**（整册 786/277 继续被他包台账行扰动＝不切片稳不住）｜尺B 三分 **45/71/31**｜尺C **正向 55/4680 + 反向硬悬空 10 条逐条同名**｜尺自检器 **14 真判 PASS + 1 有意负例自红，exit 0**｜`align_all`[1/9]-[5/9] **硬=3** 同批（裁定册 #383/#387×3）。

## V4 判据终表（V0 更正后，诚实版）
- ①全部应修落地＝本包授权内可自修项全落 ✅｜②"align_all exit0 或仅剩已登记他包/门位项"＝**原据"第6步崩属他包已登记项"的读法失效**；现余 3 硬确为已登记他包项（st-cmd 裁定册），但 **HEAD 面第 7/8/9 步从未在主区跑通过＝从未被测** ⇒ 本轮不以"未测"充"已满足"，判 🟡 待 WIP-01 清钩后补测｜③自审清单二次＝0 ⇒ 本轮虽三把尺零新问题，**但新立 WIP-01 + 一处本报告归因自我更正 ⇒ 仍未闭合**。
- ⇒ **不自删自动化**。下一轮三件事：(a) 看 WIP-01 是否已被撤钩/修正；(b) 若已清→主区复跑 `align_all` 取 HEAD 面全 9 步真值补判据②；若仍崩→以"HEAD 面 7-9 步不可测＋归因已交＋尺D 全仓 1 例已路由"记为已登记他包项据此收口；(c) 判据齐即写"自动化已自删·本包收官"+`qoder_cron remove 39cc5bd5-6b49-4b42-a65f-db987dccc076`。
- **U4 七项待裁不变**（V1 使第 3 项 depgraph 快照源越界之外再增一枚"在途件只活在 index"的姊妹项，二者可并一条修闸需求：落地完成后须把触及路径的 index 对齐新 HEAD，或禁主区 index 承载非当轮字节）。

---

# 终局更正 W（2026-09-24 07:05 CST · 收官第 3 轮触发 · 4 新案 + 1 撤回 + 判据②闭合）

## W0 本报告自身的两处更正
| 项 | 原写 | 更正后（07:05 实测） | 证法 |
|---|---|---|---|
| align 余 3 硬之处方（U1/U4 写"裁定册 related_arch×3 置空，处方交 st-cmd"） | 置空 | **撤回置空**。HEAD 面该字段 100 个非空值**全部**解析为 `#ARCH-*` 议题 id（悬空=0）⇒ 尺子语义无错；3 硬来自主 index **未提交的 staged 编辑**（`- related_arch: []` → `+ ['MOD-L00-004']` / `+ ['PS-CTR-003','MOD-INF-043']`，同批加 裁定 409（去 # 免自触门；编号未登记））。三值是**真存在但属别的命名空间**的对象（depgraph `blueprint_id` 命中 225/16 节点、`rule_catalog_registry` 在册），置空＝毁有效关联。正确处方二选一：(i) 改挂议题 id（`MOD-INF-043→#ARCH-BACKUP-SLO-001`、`MOD-L00-004→#ARCH-PROVIDER-BASENAME-001`，此二为**推断级**文本反查；`PS-CTR-003` 反查零命中⇒须先立议题），(ii) 扩字段语义+checker 按前缀分流（`#ARCH-`→议题册／`MOD-`→depgraph／`PS-`→规则册）＝改判定逻辑，高域门位只登记 | `registry_alignment.py:449-457` 读源码 + `git diff --cached` + depgraph `select count(*) … where blueprint_id=%s` |
| 判据②"HEAD 面第 7/8/9 步从未测过" | 记 🟡 待属主撤钩后补测 | **已闭合，不必等撤钩**：取 `git show HEAD:` 字节 `compile+exec`、`__file__` 指真身、`--no-report` ⇒ 零写入跑完九步。**rc=1、硬=3（全为上条那三项）、软=993**；[6/9] `FOUND 2/1791`、[7/9] 图8 硬 12(S4×2/S11×9/S12×1)+advisory 95、[8/9] 图9 硬0/软3、[9/9] GOMAP 机生层 424/硬0/软3 ⇒ **与 04:4x 独立探针逐位同值**（探针未偏，本包第 6-9 步旧结论全部沿用） | `.runtime/tmp/audit_all_20260924/run_headside_align.py` |

## W1 新立 4 案（并入党册三清单）
- **F-AUDIT-EVAP-03【悬空/断链·断链面·P1 候选】热册"整文件字节覆盖"落地吃掉他会话条目（活体复现）**：06:26 `1de609aeb1` 给翻译册加 9 行（`1f1b9145c2`→`dd2fdc9aae`）；06:51 `20885a28f2`（他包 19 件代投，**parent 即 `1de609aeb1`＝线性提交、非分支合并**）把该路径写回旧 blob `1f1b9145c2`，`git diff --numstat` = **`0 9`（纯删除）**，被删正是那 9 行。现**盘=主 index=`dd2fdc9aae`（含条目）、HEAD=`1f1b9145c2`（不含）**＝"HEAD 落后于盘"的镜像现场，后续任何吸收该路径的提交会再加回来（同一文件在 HEAD 上来回抖）。机制钉在 `commit_queue.py:1447-1449`（读袋内 `blob_ref` 的**整个文件字节**，热册无条目级三方合并）。路由 **st-commitsys**；处方＝热册路径落地做条目级三方合并（base=入袋时记录的上一 HEAD blob，ours=当前 HEAD，theirs=袋内字节，只增不回退），并把"0 增 N 删且删的是 ≤60min 内他包落地条目"设为落地前置硬检。
- **F-AUDIT-MTR-04【漏挂的反面·假挂】翻译册条目内容与所挂文件无关**：条目 `name_zh: 词表加载器`／`plain_zh: "meta_question 包的词表读取小帮手…"`，而文件是「图书馆 PG 账本双链备份+月度恢复演练」（头署 `module_id=MOD-INF-043`、`[DOMAIN] D_INFRASTRUCTURE`）；该文本**全仓仅 1 处**（非复制，系生成错配）；册侧域 `D_GOV_ENFORCEMENT` 与文件头 `D_INFRASTRUCTURE` 不一致；且条目(06:26)早于文件本体(06:58)＝"先挂册后落物"半截（本次自愈）。**失明增量第 18 条**＝`TRANSLATION-COVERAGE` 门只查条目在不在、不查条目与文件相干性 ⇒ 为过门而填的条目可无限假挂。路由 **st-library-final**。处方＝`add_module_translation.py` 写入前做"条目↔文件头 `[MODULE]`/`[DOMAIN]`/docstring 首行"三项机械一致性检（零 LLM 成本）。
- **F-AUDIT-MTR-05【新尺·尺E】翻译册 `domain_id` ↔ 文件头 `# [DOMAIN]` 全量扫**：条目 7,677／可比对 5,055（一致 5,021）；不一致 34 = **真跨域 21 + 域未填(`null`/空，多 tests/) 13**；另"文件无 `[DOMAIN]` 头 2,382""不在盘 240"两态不判。按真源并集仲裁（depgraph `domains.domain_id` 74 ∪ 域册 `domain` 79 ∪ 契约 3）＝**18 条两侧都在册（真归属冲突，需按域定义裁）+ 3 条有一侧是未注册野值**（册侧 `D_PLAN_ENGINE`、册侧 `D_INFRA`、头侧 `D_EXECUTION_CORE` ⇒ 这 3 侧机械可判必错，是零争议可直修子集，仍属翻译册写域故登记不代修）。建议挂法（§4.1 净零）：并入既有 `add_module_translation.py` 校验面，噪声 21/5055=0.4%。**非缺陷测量（防重复劳动）**：YAML 79 域 vs DB 74 差的 5 域（`D_EXECUTION/D_ORDER/D_PORTFOLIO/D_SIGNAL/D_TEST`）在 `nodes.domain_id` 零引用；`nodes` 用的 73 域全在 `domains` 表内。
- **F-AUDIT-RULING-02**：即 W0 第一行那案（staged 在途编辑跨命名空间挂 `related_arch`）。风险陈述＝该 staged 件一旦被吸收，3 真红进 HEAD ⇒ **全场 align 变红、施工前判据失效**；与 IDX-05/WIP-01/EVAP-03 同根（主 index 承载非当轮字节）。路由＝**st-cmd（裁定册属主）+ 总指挥排归属**。

## W2 反证与尺自检增量（累计 22 例，其中本轮第 20-22 例）
- **例 20（我的尺差点自造假红）**：第一版域真源抽取用错键（`domain_id|id`，而域册的键叫 `domain`）⇒ 得 **0 元素集合**，于是把 21 条全判"两侧都不在册"。修正为三源并集后翻成 **18/2/1/0**。⇒ 立法：**凡"某物不在真源"的结论，先自证抽取器抽得到东西**（本轮起尺E 带四控制组：阳性只判出真那 1 条、三条阴性各不判红，全 PASS 才取数）。
- **例 21（基线自毁）**：复跑尺A 前未 `cp` 上一轮明细，`dangling_v2_lists.txt` 被覆盖 ⇒ 110→111 的增量只能靠 HEAD 变更集反查定位，不能直接 diff。⇒ 复跑型尺子**必须先快照基线**。
- **例 22（最重要的读数纪律）**：EVAP-03 那枚蒸发让尺A 业务面 **165/110 → 164/108**，看着像"欠账减少"。⇒ **计数下降不得直读为改善**，须先查该路径有无 net-negative diff；本包各轮"同值"结论不受影响（同值≠下降）。

## W3 待裁与移交（W 节口径，覆盖 U4 第 3 项与 V4 判据表）
- **要 Owner 点头的只有 1 项**：RULING-02 走 (i) 改挂议题 id 还是 (ii) 扩字段语义+分流校验（(ii) 是改判定逻辑=高域）。其余 3 案均有机械判据、可直接派属主包（st-commitsys／st-library-final×2）。
- **移交三件不变**：25 真幽灵"补建 or 销册"、R1 连坐解堵后的 3 袋归属、stash 定向提取。
- **终态判据自查（W 版）**：①应修落地＝授权内可自修项全落 ✅｜②align 真值＝HEAD 面九步全跑通且余 3 硬已定性为已登记在途项 ✅（本轮闭合）｜③**连续两轮零新立＝未满足**（本轮新立 4 案）🔴 ⇒ **不收口、不自删自动化**。下一轮补尺C 第 3 轮 + 盯 EVAP-03/RULING-02 走向。

---

# 终局更正 X（2026-09-24 07:22 CST · 同轮第二把新尺触发 · EVAP-03 由"单例"升级为"量化+级联+残损"）

## X1 F-AUDIT-EVAP-03 终态定性（三件一体，全部 blob 级亲验）
1. **量化**：今晚窗口（00:00–07:20，64 笔提交）热册出现 **11 起"0 增 N 删"事件 / 7 个文件**；叠"落地 blob ∈ 该路径祖先历史"的字节级回史判据后 **8 起证实为旧快照回写**、**3 起判为当轮主动改写/退役（不算缺陷）**。8 起**全部命中"往回第 1 笔"**。
2. **级联**：`c5b70a8ff8`(03:05, **本包 st-audit-all**「蒸发复发·重投」) 回写 `capability_canonical_file_registry.yaml -214`、`a1_ledger.md -92`；25 分钟后 `53cdc66e06`(03:12, st-align-dirty) 落地的 cap 册字节 **== 我 03:05 那笔 blob** ⇒ 陈旧字节被下一笔原样继承。**结论：受害者与加害者之间只隔一次"重投"；凡整文件字节落地路径，重投动作本身就是二次传播。**
3. **残损（逐本实测，不靠推断）**：cap 册**无残留**（HEAD 47,162 行 > 蒸发前 46,749 行，214 行已由后续批带回）；翻译册那条**待吸收自动回加**（盘/主 index=`dd2fdc9aae`、HEAD=`1f1b9145c2`）；🔴 **`generator_registry.yaml` 为功能级残损且仍未回**——06:20 `6199c0752a` 登记的两枚挂载 `module_algorithm_overview`/`governance_map` **HEAD 出现次数=0、盘=2** ⇒ 编排器对 08 册与 GOMAP 的**自动再生在 HEAD 上等于关闭**，而这正是本窗 st-align-dirty 为"GOMAP 被陈旧快照蒸发两次"开的处方，被 06:51 的回写原地注销。

## X2 处方（交 st-commitsys，与 W1 那条合并为**一条**修闸需求，§4.1 净零）
> 高写入热册（注册表/配置册/台账/宪法）落地须**条目级三方合并**（base=入袋时记录的上一 HEAD blob、ours=当前 HEAD、theirs=袋内字节、只允许增不允许整段回退）；并加两道落地前置硬检：**(a)** 纯删除 diff（0 增 N 删）⇒ 若落地 blob 命中该路径历史（回史判据）即阻断并改道 rebase；**(b)** 落地后即时核"`git rev-parse HEAD:<path>` 是否等于入袋时盘字节"，不等则记堵点而非静默通过。**残损回收（一句话可解）**：`generator_registry.yaml` 按盘字节 re-land，复验 `git show HEAD:<G> | grep -c governance_map` 期望 2。

## X3 审查包自身纪律（新增两条，来自本轮反例 23/24）
- **自审必含自家提交**：做"回写/蒸发/净删"类审查时，检测域 MUST 包含本包自身的 commit——本包 03:05 那笔是今晚第 2 起被证实的回写，而我在其后写了 6 个心跳块、立过 EVAP-01/02，**从未把自家 numstat 纳入尺子**。这是本战役审查器最严重的一次自身失明。
- **两尺同框才可定性**：单用"0 增 N 删"假阳率 27%（3/11 为合法删除），必须叠"落地 blob ∈ 路径历史"的字节级回史判据。凡"某物不在真源/某笔是事故"类结论，须给出**能区分合法与事故的第二把尺**及其结果。

## X4 终态判据自查（X 版，覆盖 W3）
①授权内可自修项全落 ✅｜②HEAD 面 align 九步真值已取得、余 3 硬定性为已登记在途项 ✅（W0 闭合）｜③**连续两轮零新立＝未满足**（07:05 立 4 案，07:22 续立 1 案 + 2 把新尺 + 1 项高优移交）🔴 ｜④红蓝反证：尺自检器 14 真判+1 有意负例自红（06:0x），尺E 四控制组全 PASS，尺F/F2 三控制组全 PASS（阳性必检出/分母非零/判据不自扩）✅｜⑤终报：U+V+W+X 四节已交。⇒ **不收口、不自删自动化**；下一轮补尺C 第 3 轮 + 盯 `generator_registry` re-land 与本包 0025 落地是否再被回写。

---

# 终局更正 Y（2026-09-24 07:36 CST · 尺G 触发 · EVAP-03 覆盖面由"册内条目"扩到"整本文件"）

## Y1 尺G＝整件消失判据（补尺F2 的结构性盲区）
- **为什么必须有**：尺F2 用"落地 blob ∈ 该路径历史"证回写，对**整本文件被吞**必然失效（被删侧无新 blob 可比 ⇒ 只能落"非回写"）。`0f08f7a06c` 正是这样被 F2 放过的——而它是今晚最大一起。⇒ **反例第 25 例：尺子的"非回写"分支被我当成"不算缺陷"。**
- **判据（三条件同框）**：commit 删除 P ＋ **P 此刻仍在盘上**（真退役会连文件消失）＋ P 的添加笔是本 commit 的**祖先**、相隔 ≤90min、且**跨包**。
- **判据修正一次（反例第 26 例，由控制组当场拦下）**：初版取"最新添加"用 `git log --all --diff-filter=A -1` ⇒ 会取到晚于本 commit 的 `cf1c963092a "index on dev"`（stash/index 提交），gap 变负致该家族全漏；改为限定 `C^` 祖先链后四控制组全 PASS。
- **结果：今晚窗口 18 起整件消失 / 5 组加害→受害包对**（明细 `g_whole_file_swallow.tsv`）。

## Y2 三起定量事实（逐件亲验）
| 加害笔 | 时刻 | 受害包及其刚落地时间 | 被吞件 | 07:33 残损 |
|---|---|---|---|---|
| `0f08f7a06c`（st-k4 池化终批 v3，message 自述 10 件） | 00:43 | st-gpu-final 00:38（**相隔 5.5min**） | **成本考尺整功能 6 件**：`config/exam_scale_cost_gate.yaml`、`src/zephyr/backtest/regime_validation/exam_cost_gate.py`、`scripts/backtest/exam_cost_reexam.py`、`docs/03_modules/_domain_backtest/algo_flow/exam_cost_gate.yaml`、`tests/backtest/test_cost_gate_tier_wiring.py`、`tests/backtest/test_exam_cost_gate.py` | 3 件仍 `HEAD=0 盘=y` |
| `1cba19a9de`（st-flush） | 00:23 | st-library-final 00:19（4.1min） | 图书馆采集器族 7 件（含 `logs_collector.py` 与其测试、`regulations.md`、两门禁测试） | 已由后续批带回 |
| `0fe090715f`（st-align-dirty） | 07:06 | st-library-final 06:58（**7.5min，发生在本轮取证期间**） | 备份馆 3 件（`scripts/backup/library_ledger_backup.py`+注册 ps1+测试） | 仍 `HEAD=0 盘=y` |
- **同族第二特征**：`0f08f7a06c` 除删除外还把 `docs/library/regulations.md`、`logs_collector` 等**他会话在途件**一并提交（A 侧同样越界）⇒ 代投吸收的是**主 index 的 17,000 件快照**，与 AGENTS §2.5"commit 后必核 `git log -1 --name-only`"及本包 IDX-05/WIP-01/EVAP-03 同根。
- **X1 残损项回收实证**：`generator_registry.yaml` 两枚挂载已由 `86bf9217dd`(07:13) 自行带回（`git show HEAD:<G>|grep -c governance_map`=**2** ✓）⇒ "按盘字节 re-land"确为可行正解，上述两族待属主同样处置。

## Y3 本包自身交付件的落地面真相（X3 立法"自审必含自家"的第一次执行）
`docs/_working/audit_all/AUDIT_REPORT.md` 今日全部三笔逐字节核：`0c7e42b3ba`@04:30=137 行 → `da4de88435`@06:23=**246 行（U 节落地 ✓）** → `20885a28f2`@06:51=**137 行（U 节被回写吃掉）**，此后无人触及。⇒ **本包终报正文在 HEAD 上自 06:51 起只剩 04:30 版**，U/V/W/X/Y 全部只在盘与袋（LEDGER 同：盘 902 / HEAD 774 行）。**审查包自己的产物也没躲过同一把刀**——这既是本案最有力的说服力，也说明"再立一个 gate"不是解药，落地语义才是。

## Y4 判据终表（Y 版）
①授权内可自修项全落 ✅｜②HEAD 面 align 九步真值已取得、余 3 硬定性为已登记在途项 ✅｜③连续两轮零新立＝**未满足**（本轮加 1 案面扩、4 把新尺 E/F/F2/G、反例 20–26 例）🔴｜④红蓝反证：尺E 四控制、尺F 三控制、尺G 四控制全 PASS，尺自检器 14 真判+1 有意负例自红 ✅｜⑤终报 U/V/W/X/Y 五节已交。⇒ **不收口、不自删**；下一轮先核 0026/0027 是否落地（`git rev-parse HEAD:<报告>` 应≠`da4f3f24aa`），再复跑尺F/F2/G 看是否继续产生新事件。

---

# 终局更正 Z（2026-09-24 07:52 CST · 根因收口 · **撤回 X2 处方**）

## Z1 一句话根因（取代 X2/W1"须新建条目级三方合并"的说法）
条目级三向合并**早已存在**（`scripts/governance/commit_queue_landing.py:175-201` W2 治本，起因即 2026-09-22 注册表事故 `fb5a7821d` 抹掉 103 条身份），今晚 8 起热册回写**全部发生在队列通道**（六涉事提交的 message 尾注均带 `[GW:<sid>:q-<qid>]`）。它之所以仍然吃掉别人，是因为**入袋根本不记 base**：
- `scripts/commit_queue.py:696/712`：`"base_blob": None,  # A 段预留（B 段：git rev-parse HEAD:{path} 填充）`——**B 段从未实现**；`:45` 注明"由调用方显式传入"，而 `git_commit.py --enqueue` 通道从不传。实物证据＝07:50 直读本包 `pending/q-20260924-st-audit-all-20260924-0027.json`：`base_head=None`、两文件 `base_blob=[None, None]`。
- `_merge_registry_file:1071-1075` 缺 base 时兜底 `base_sha = old_dev^` ⇒ 当"他人条目"落在 `old_dev^..old_dev` 之间（今晚三起相隔 4–8 分钟），base 已含该条目、theirs（陈旧快照）不含 ⇒ **合并器把它读成"theirs 侧主动删除"并忠实执行**。⇒ `capability_canonical_file_registry -214`／`generator_registry -18`／`module_translation_registry -9` 都是**合并器亲手落的合法删除**，不是它没生效。

## Z2 修正后的处方（净零：不新建件，只把已有的字段填上）
1. `scripts/git_commit.py` enqueue 通道传 `base_head=当前 dev HEAD`；`commit_queue.py:696/712` 把预留字段 `base_blob` 填为 `git rev-parse HEAD:<path>`（字段、注释、测试位都在）。
2. `_merge_registry_file` 改以 **per-file `base_blob`** 为 base，**取消 `old_dev^` 兜底**——缺 base 时死信回人工，而不是猜一个 base 去"合并"。
3. 非注册表族（`docs/_working/**` 台账、交付物报告）**不在合并作用域内**⇒ 按"高写入热文件族"扩面，或至少给落地加两道本包已写好的前置硬检：**尺F**（热文件 0 增 N 删）、**尺G**（整件消失：删了、盘上还在、添加笔是本 commit 祖先、≤90min、跨包）。两把尺的控制组均已跑通（尺G 四控制 PASS）。
4. 路由＝**st-commitsys**（`commit_queue.py`/`commit_queue_landing.py`/`git_commit.py` 三处均为其写域）。本包对这三处**零写入**。

## Z3 撤回与降级清单（本报告对自身的不实之处，逐条给证）
| 原结论 | 处置 | 依据 |
|---|---|---|
| X2/W1"热册落地无条目级三方合并，须新建" | **撤回**，改为 Z2 | `commit_queue_landing.py:175-201/1089-1131` 实读 + 六涉事提交 GW 标记 |
| Y2"`0f08f7a06c` 代投吸收了主 index 的 17,000 件快照" | **降级改写**：该项走队列，成因是**入袋 files 清单含他会话在途件**（清单外 staged 被 gateway 吸收），与 IDX-05"主 index 第二真源"是两个机制，**不得并成一条** | GW 标记=亲验；"清单外吸收"的具体入口=推断级，下一轮读 `git_commit.py` staged 收集段定级 |
| W0 表第 2 行"判据②需等属主撤钩才能补测" | 已完成不需等（HEAD 字节 exec 零写入跑通九步） | `run_headside_align.py` 输出 |
| 本包旧处方"裁定册 related_arch×3 置空" | **撤回**（见 W1 F-AUDIT-RULING-02） | HEAD 面 100 值悬空=0；三值是真存在的跨命名空间对象 |

## Z4 交付物自身状态（诚实记账）
本包 `LEDGER.md`/`AUDIT_REPORT.md` 自 06:36 起的 V/W/X/Y/Z 五块**至今未进 HEAD**（报告 HEAD 仍 137 行=06:51 回写态、盘 346+ 行；`git log --all -S "V4 判据终表"` 零命中），0025/0026 已从 pending/processing/done/dead 四处消失（疑被 `supersedes`/compaction 折叠，同路径后袋覆盖前袋），0027 pending 中。⇒ **审查包自己的产物也没躲过同一把刀**；下一轮第一件＝核 0027 落地，仍不落则改 `--no-auto-enqueue` 直连单文件落并记为本包排雷项。判据③"连续两轮零新立"仍未满足 ⇒ **继续跑、不自删自动化**。

---

# 终局更新 AA（2026-09-24 09:04 CST · 收官"连续两轮零"第 1 轮 · 案卷落地通道复证 · 自家基线两处更正）

> 本节把 08:09/08:29 心跳与本轮 09:04 的实测并入终报（承 Z 节之后），使报告口径追至 09:04。全部断言附只读重放命令，遵 X3「引用即重放」。

## AA0 口径更正（覆盖 U4/V4 的"待裁/他包"标注）
- **"align_all 余 3＝裁定册 related_arch×3（383/387）→ 处方交 st-cmd"**：本包已于 **04:36 commit `a74e9a6c48`（done 袋 0011）自修落地**——383/387 `related_arch` 违字段契约（该域只收 `#ARCH-*` 议题号却填了模块/契约号 MOD-L00-004/PS-CTR-003/MOD-INF-043，且无对应 ARCH 条目）→ 置空 `[]`，真身在 `affected_files` 已存；align 全图硬 3→0。⇒ 该项 **closed（本包自毕，非他包待办）**，从 U4 剩余/待裁表移除，防总指挥重复派单。重放：`git show a74e9a6c48 --stat | head -6`。

## AA1 尺I 证伪 → 尺J 成立（审查器"能红自证"再进一格）
- **尺I（markdown 半句收尾/奇数反引号/奇数粗体 判文本局部吃掉）＝判据不成立**：两册合报 133 处可疑（绝大多数 `：`/`---` 正常收尾＝假红风暴），而真残口一处没抓到 ⇒ 废弃，留 `.runtime/tmp/audit_all_20260924/probe_text_integrity.py` 作反面教材。
- **尺J（同块跨袋长度比对）成立**：24 个 LEDGER 袋 × 71 块，跨袋长度不一致 19 块，Δ≥50 者 2 块，最大 **Δ=12,591 字**（`## 心跳 … 04:28` 块 19,749→7,158＝确曾被后手逐次砍尾，跨袋见 4 个长度）。控制组：合成阳性（截袋为被回退态）missing=71、合成阴性（同版本对自身）=0。恢复配方＝逐块取最长袋版本，四道前置（块头唯一 ∧ Δ≥50 ∧ 现存版是最长版严格前缀 ∧ CAS 写＋进程外回读）；已执行，**复扫待补块=0**。07:22/07:35 块跨袋同长＝无截断证据。重放：`python .runtime/tmp/audit_all_20260924/ruler_J_restore.py | tail -1`。

## AA2 F-AUDIT-MERGE-01【P1 候选·合并侧热册条目蒸发·39 秒最小复现】
- 尺＝逐笔核 key 存在性（`git log --since=07:25 --format=%h|%ci -- <翻译册>` 四笔，每笔 `git show <c>:<册>|grep -c <key>`）：`81647d88db`(07:36:16 翻译册终缺批)⇒两 key Y/Y → `4fc2cf6d04`(07:36:55 **merge gpu-final into dev**)⇒**同两 key n/n＝39 秒后被一次 merge 静默吃掉**（merge 对该册取分支侧，未做条目级三方合并）→ `5fe4d26426`(07:57:42 属主重投自捕)⇒回 Y/Y，HEAD 现 Y/Y。
- 定性：与 **EVAP-05/06 根因（队列入袋不记 `base_head`/`base_blob` ⇒ 合并器缺 base 兜底 `old_dev^`）同一病灶的第三个面**——前两面是"袋侧陈旧快照读成主动删除"，本面是"merge 侧对热册整文件取单侧"。处方并入 st-commitsys **一条**修闸需求（§4.1 净零）：注册表族文件的 merge/落地必须走条目级三方合并，缺 base 即死信而非兜底。本包对该册零写入（全程 `git show`/`git log`）。

## AA3 审查包纪律第 5 条（＝最重要一条）：引用即重放
- 案卷中任何"我读到了 X / 实测为 X"的句子，MUST 同批附一条可重放命令＋命中位置（行号/blob 名），写前先跑一次并把输出贴进块内；无命令可贴者一律降级为"推断"或不写。源自本轮公开更正的三处不实断言：**（甲）幻觉读数**（"HEAD 出现 08:16/08:24 两块心跳"＝三处穷举皆 0，那两块从未存在）、**（丙）漏时点**（"翻译册只剩 1"同一命题 07:57:11 与 07:57:42 两读数都"对"，缺时点即缺真值）、**引错块号**。（甲）比估钟危险：估钟只错时间，这个错的是事实。

## AA4 案卷落地通道复证 + 0009 noop 再确认
- **0032 已落地**＝`65225f4534`(08:38:26, files=2 纯增)：GATE-01 自触（未登记号 409 的 `裁定`+井号形态）经"去井号"处方修后一次通过；HEAD 现 LEDGER **1044**/REPORT **372**，盘==HEAD。⇒ 本包案卷"纯增不触他包"通道可用（对照 0030/0031 因该门 dead）。
- **0009 `battle_map_domain_policy.yaml:286` 指针修仍不在 HEAD**（`landed_id=noop@…`）：web 版为唯一真源，两文件 HEAD 皆存在＝**SSOT 误指非硬断链、低危**；属注册表册"单字段"边修被 noop 家族（F-AUDIT-LAND-01/MERGE-01/EVAP 同病灶），队列通道未修前本包第 N 次不硬闯、维持登记上交。
- 两处"已落 dev"复证非假绿：`90889679b2`/`5f4136315e`（工厂图补边/GOMAP 机生层 25→0）皆 HEAD 祖先，align 图 8/9/10 轴硬=0 亲验。

## AA5 收官"连续两轮零新问题"第 1 轮（三尺 + 红蓝反证齐绿）
- **尺H2**：命中袋-件对=30，合法改写侧 151 行、条目被吃侧 3 行＝**全属 0009**（`(no-key)×3`）；上一块报的"REPORT 90 行不在 HEAD"已随 0032 转 alive。除已登记 0009 外**零新死件**。
- **尺J**：待补块=0。
- **align_all（HEAD 面只读）**：`rc=0`、硬问题清零（六类全 0），软 984（图 8 chainmap 12 条硬按长城专项暂计软＝st-gpu-final 清欠中；翻译册 6 组重复 module_path＝已知，清源 `--dedupe`）。
- **红蓝反证 re-confirm**：`redblue_ruler_selfcheck.py` 真判 14 断言全 PASS + 1 有意负例触发红（＝自检器能红且不瞎报，非恒绿）；`probe_redblue.py` 图 9/图 10 校验器对"漂移/幽灵/元数据篡改/mount 不存在/disconnected 缺 note/整族删除"**每注入皆 RED✔**，并**揪出 2 处设计盲检器**（`counts` 谎报、`generated_at` 陈旧指纹均不比对＝恒绿盲区，交属主裁定是否纳入判据）。

## AA6 终态判据自查（AA 版，覆盖 U7/V4/Y4）
- ✅ 八图图↔物对账穷尽（dossier 各带三清单）｜✅ 已修落地经 HEAD 祖先亲验｜✅ 自家过时基线两处更正（383/387 closed / 0009 再定性）｜✅ 红蓝反证能红自证 + 盲检器猎取｜✅ 收官零复跑第 1 轮。
- ⬜ **收官零复跑第 2 轮**（下一轮复跑尺H2/J/align，须仍仅 0009 已知项、rc=0）｜⬜ 满足"连续两轮零"后**自删本自动化**（jobId `39cc5bd5`）+ 台账记"自动化已自删·本包收官"。
- ⬜ 高域/他包项维持上交（不属本包收官阻塞）：F-AUDIT-LAND-01/MERGE-01/EVAP（交 st-commitsys 修队列入袋记 base＋注册表族 merge/落地条目级三方合并）、图 8 chainmap 12 硬（st-gpu-final 清欠）、counts/generated_at 盲检（图 10 属主裁）、翻译册 6 组重复（`--dedupe` 清源）。
---

# 附录 AB · 红蓝反证并档（AB2 轮：2026-09-24 10:10 CST · 自我否证 38 例总表 + 失明清单 18 条指针 + 盲检器 4 处）

> **为什么要并这一档（＝本档第 34 例自触）**：台账自 09:04 起三块反复引用"累计 31 例"，但两册合看**显式编号只到 28**，29–31 从未逐条落地 ⇒ 该计数当时**不可重放**。本节把 1–35 全部枚举，并按 §4.3"计数不写死在散文"把例数降为**由表行派生的字段**。
> **计数重放命令**：`python -c "import re,pathlib;print(len(re.findall(r'^\| R[0-9]{2} ', pathlib.Path('docs/_working/audit_all/AUDIT_REPORT.md').read_text(encoding='utf-8'), flags=re.M)))"` ⇒ 期望 **38**（本表行数即真值，散文里的数字皆须与之同框）。

## AB0 本轮（10:10）能红自证复跑读数（内存注入，零生产写入）
- `redblue_ruler_selfcheck.py`＝**真判 14 条断言全 PASS ＋ 1 条有意负例触发红**（`[SELF-RED] +1`，exit 0）⇒ 自检器既能红也不瞎报，本轮再复证。
- `probe_redblue.py`＝注入场景 **17 例：13 例 RED✔ ＋ 4 例 GREEN✔（＝设计盲检器，见 AB3）**，覆盖图 9 连通性/元数据篡改/mount 不存在/整族删除 与图 10 机生层漂移/幽灵。

## AB1 自我否证总表（R=审查器自身缺陷，非被审对象）
| # | 病（一句话） | 出处 | 治法 | 固化态 |
|---|---|---|---|---|
| R01 | 时钟外推：心跳用估算钟当实测 | 附录A/U5① | 块头由 shell `date` 注入 | 做法已固化 |
| R02 | 探针 v1/v2 判据不成立仍拟上交 | U5② | 废弃件留作反面教材（尺I 同法） | 留件 |
| R03 | v3 负例三条选错 | U5③ | 负例须"选不出即无效" | 控制组 |
| R04 | "门读 index"假设逮到自己案卷未落 | U5④ | 结论前先核自家落地态 | 纪律 |
| R05 | GEN-02 收录假阴性 | U5⑤ | 生成器收录须反查 | 控制组 |
| R06 | DANG-01 主动否证自己 P0（三闸静默失效→P2） | U5⑥ | 降级须给证伪命令 | 纪律 |
| R07 | BAG-01 比率 35.5%→24.6%（分母口径漂移） | U5⑦ | 分母随判据同批声明 | 纪律 |
| R08 | 凭不存在的 `files[].sha` 字段造出"袋面丢失" | U5⑧ | 读实物字段前先 `keys()` | 纪律 |
| R09 | DANG-01 把台账正文当图边（785→164） | U5⑨ | 切片按结构而非正则面 | 已修尺 |
| R10 | PATHRE 抓模板省略号 `src/zephyr/.../xxx.py` | U5⑩ | 判据加省略号豁免 | 已修尺 |
| R11 | 改名判据 basename 太松造 11 条假改名 | U5⑪ | 唯一非泛名同名才算 | 已修尺 |
| R12 | 漏挂尺只取 `node_type='module'` 造 22.9% 假漏挂（真 1.2%） | U5⑫ | 全 node_type 路径并集 | 已修尺 |
| R13 | `--diff-filter=D` 误判"从未存在" | U5⑬ | 加祖先链存在性判据 | 已修尺 |
| R14 | 断言数写死 16 实为 14 | U5⑭ | 计数由行派生 | 自检器 |
| R15 | 手工补正计数致文案与实数不符 | U5⑮ | 同上 | 纪律 |
| R16 | "enqueue 写主 index"假设被代码否证 | U5⑯ | 读码不读直觉 | 纪律 |
| R17 | 编号险撞 IDX-04（幂等闸拦下） | U5⑰ | 立案前 `grep -oE 'F-AUDIT-*' \| max+1` | 追加脚本已带 |
| R18 | 尺D 分母虚高 26 倍（函数注解误判为体内遮蔽） | V2 | 只走 `fn.body` | 控制组 |
| R19 | 控制组逮到自己把过滤写错分支 | V2 | 在 `pop()` 处过滤 | 控制组生效正例 |
| R20 | 域真源抽取用错键得 0 元素⇒ 21 条全判野值 | W2例20 | 凡"不在真源"先自证抽得到 | 尺E 四控制 |
| R21 | 复跑前未快照基线⇒ 增量只能反查 | W2例21 | 复跑型尺必先 cp 基线 | 纪律 |
| R22 | 计数下降直读为"改善"（实为蒸发 165/110→164/108） | W2例22 | 先查 net-negative diff | 立法 |
| R23 | 自审域未含自家提交（本包 03:05 那笔即第 2 起回写） | X3 | 自审 MUST 含本包 commit | 立法（Y3 首次执行） |
| R24 | 单尺"0 增 N 删"假阳率 27% | X3 | 两尺同框（＋回史判据） | 尺F/F2 |
| R25 | 把尺F2 的"非回写"分支当成"不算缺陷"⇒ 放过整件消失 | Y1 | 立尺G 三条件同框 | 尺G 四控制 |
| R26 | "最新添加"用 `--all` 会取到 stash/index 提交致 gap 变负 | Y1 | 限定 `C^` 祖先链 | 控制组当场拦下 |
| R27 | "缺 X 所致事故"类结论未先证 X 不存在（六涉事提交全带 GW 队列标记⇒ 我默认了一整轮"直连无合并"） | 台账 07:22 块 | 先 grep 真源＋读实物字段 | 立法（并免重复造轮 §4.1） |
| R28 | 给别人"某时刻亲验"背书、自己块头时间戳是估的 | 台账 07:35 块 | 同一动作留可核对时锚 | 纪律 |
| R29 | **幻觉读数**："HEAD 出现 08:16/08:24 两块心跳"＝三处穷举皆 0，那两块从未存在 | AA3(甲)/08:01 块 | **引用即重放**：无可贴命令即降"推断" | 立法（纪律第 5 条） |
| R30 | 漏时点：同一命题 07:57:11 与 07:57:42 两读数都"对" | AA3(丙) | 读数必带时点 | 立法 |
| R31 | 引错块号（把他块结论记在本块名下） | AA3 | 引用附块头指纹 | 立法 |
| R32 | **阳性控制组钉死真件 ⇒ 必随落地 rot、整尺作废**（尺H2 第 1 轮后自我作废） | 09:34 块 | 控制组改合成样本：absent-key 阳性必 3、自比对阴性必 0 | 尺H2 合成控制（10:10 复验 3/0 稳定） |
| R33 | 滚动基线含已自毕项未回收⇒ 有重复派单风险（"383/387 交 st-cmd"实为本包 04:36 已落 `a74e9a6c48`） | 09:04 块 | closed 即从待办移已办 | 纪律 |
| R34 | **计数断言无枚举支撑**（"累计 31 例"三块引用而 29–31 未落地） | 本轮并档自触 | 例数改为表行派生＋重放命令 | 本档 |
| R35 | **结论缺"适用时窗"**："HEAD 面 GOMAP 漂移=0" 于 09:34 为真、他包 `96870e1fd3`@09:43 落地后失效（非误判，是过期） | 收官第 3 轮 10:0x | 凡"X=0/为真"须带测量时刻＋失效条件 | 纪律（R28 的结论级扩展） |
| R36 | 控制组阳性样本自身造错：把 flow-style 「another: [a, b]」当纯 dict 喂「零族」判据，期望 0 族实得 2 族 ⇒ 若尺不拦即成假绿 | 收官第 4 轮 10:5x 尺M 首版 | 控制样本先证判据成立再写期望值（R20/R26 同族病） | 尺M 当场 fail-closed 拦下 |
| R37 | 归因错并：0009 的静默丢失被记进「陈旧快照被读成删除」（MERGE-01/EVAP）家族，实为零竞态下「零族册不被承载」的另一条机制 | 收官第 4 轮 10:5x 尺L/尺M | 机制不同＋复现不同＋处方不同 ⇒ 判「跨域不同对象→不并」，分立 MERGE-02 | 已更正（见附录 AC1/AC3） |
| R38 | 立案前只做**编号级**反查（R17 原式）未做**机制级**反查 ⇒ 差点把 st-align-dirty 已立 D25 的同根另一枝另立新案 | 收官第 4 轮 AC5 | 反查对象＝机制描述里的函数名/代码位（`is_registry_mergeable`/`_split_registry_entries`），不是自家编号前缀 | 已并案（AC5） |
| R39 | **口径失真**：尺M 的"可承载 77"按"文件含 ≥1 顶层 list 族"判定，但合并器实际只 splice **族内条目**——族外的顶层标量/嵌套键编辑仍被静默吞。`rule_catalog_registry.yaml`（有 `files:` 族、被 M 计入 77）实证被吞 2 行（`generated_at`/`total_files`），跨 4 包 6 袋复现 ⇒ "可承载"应改述"部分可承载"，处方(iii)入队普查须核对**被改的键是否落在可 splice 的族内**，而非只看文件有没有族 | 收官第 5 轮 11:1x 尺N HARD 1→2 | 承载能力是**按键区域**非**按文件**度量；阳性控制不能只造"整册无族"，须造"有族但改族外键" | 已并入 MERGE-02 第二枝（AC7） |

## AB2 失明清单指针（18 条，勿在本档复述正文）
- 第 1–9 条＝本报告"红蓝反证（§0.14）"章 (B) 组；第 10–16 条＝U5"失明清单增量"；第 17 条＝V2（pre-commit 仅 ruff、无 `used-before-assignment` 等价规则）；第 18 条＝W1（`TRANSLATION-COVERAGE` 门只查条目在不在、不查条目↔文件相干性）。
- **本轮不新增条目**（§4.1 净零）：GOMAP 的新观察"派生册生成器以工作树为输入、缺 HEAD 基线闸门"（`generate_governance_map.py:143` `rglob`）按同类归并入既有"派生册 freshness"族，登记号＝`F-AUDIT-GOMAP-INFLIGHT`（定性升级版，见台账 10:0x 块 ③）。

## AB3 盲检器猎取（4 处设计盲区，全部 expect_red=False 实测坐实）
1. 图 9 `validate_structure` 对**完全无边连接的孤儿节点**不响（base=0→injected=0）。
2. 图 9 `validate_structure` 对**清空全部 edges** 不响（同上）。
3. 图 10 `gomap_alignment` 对 **`counts` 谎报**不比对（全改 999999 仍绿）。
4. 图 10 `gomap_alignment` 对 **`generated_at` 陈旧指纹**不比对（改成 1970 仍绿）。
⇒ 前两条＝工厂图连通性保护链缺失的同族现形（已作 B1/B2 处方交 st-commitsys/st-align-dirty）；后两条＝**校验器只信被检物自报元数据**，属设计选择而非笔误 ⇒ 是否纳入判据交图 10 属主裁定（本包不擅改判定逻辑＝high 域自律）。

## AB4 对终态判据的作用
红蓝反证一项（判据④）**由"逐轮增量叙述"变为"单档可重放"**：自检器/注入器读数在 AB0、病例总表在 AB1、失明与盲检指针在 AB2/AB3，Owner 或属主包复核只需跑 AB1 顶端一条计数命令 ＋ AB0 两条脚本。

---

# 附录 AC · 收官第 4 轮（收敛确认）＋ 新案 F-AUDIT-MERGE-02（2026-09-24 10:54 CST）

> **测点声明**：`date`=2026-09-24 10:54:26，HEAD=`e41a06c295`(10:50:30，他包 st-metaq 批）。本节全部读数为只读重放，多包并发窗内 HEAD 持续移动，**引用必带时点**（纪律 R35）。

## AC0 第 4 轮＝收敛确认：三尺与第 3 轮逐位一致，唯一硬项未变
| 尺 | 第 3 轮（10:04） | 第 4 轮（10:26–10:54） | 判 |
|---|---|---|---|
| 尺H2（done 袋 own-key 存活） | 袋-件对 31／alive 152／dead 3（全属 0009）；合成控制 3/0 | **同值 31／152／3；控制 3/0** | 零新件 ✅ |
| 尺J（LEDGER 块最长版） | 待补块=0 | 待补块=0 | ✅ |
| align（HEAD 面只读） | rc=1，唯一硬=图 10 GOMAP，软 1005 | **rc=1，唯一硬仍＝同一条 `scripts/audit/t0_gpu_condition_pack.py`**，余八类硬=0，软 1005 | 收敛 ✅ |
| 四元组三态 `<HEAD,index,盘,yaml盘,yamlHEAD>` | `(1,0,1,0,0)` | `(1,0,1,0,0)` 未归一（他包 `t0_*` 族 `git rm --cached` 搬迁仍在途） | 稳定他包在途项 ✅ |

⇒ `F-AUDIT-GOMAP-INFLIGHT` 不升为真缺陷（判据②命中"仅剩已登记他包/门位项"分支）；**不代修**理由两条：§3.4 owner 责任制＋RULE-SSOT（此刻任何旁观包重跑 `generate_governance_map.py` 都会把他包瞬态烙进派生册——已由 `sector_line` 一支实证：盘版 yaml 含它 2 处、HEAD 版 0 处）。

## AC1 新立 F-AUDIT-MERGE-02【注册表合并"作用域 vs 承载能力"错配＝静默假成功】
- **发现路径（诚实记账）**：不是设计出来的，是**收官判据①"全部应修落地"逼出来的**——此前该判据由 尺H2（done 袋）＋尺J（LEDGER 块）支撑，**"9 个 dead 袋里那份字节到底进没进 HEAD"从未量过**。新立 5 把尺补面：尺K（blob↔HEAD 行比对）→ 尺K2（缺行三分）→ 尺L（把合并器当纯函数直喂三侧字节复现 0009）→ 尺M（全册人口普查）→ 尺N（全窗 `noop@` 回执判决）。
- **死信袋载荷面结论**：尺K 报 4 件各缺 1 行，尺K2 三分**全部 REWRITE**（GATE-01 去井号净化，HEAD 版自带"去 # 免自触门"注）⇒ **零真残损**，判据①的这条支撑成立（尺K/K2 控制组：阳性人造前缀行必判 PREFIX、阴性 HEAD 自取行必判 PRESENT，皆 PASS）。
- **机制（两条代码位亲验，`scripts/governance/commit_queue_landing.py`）**：`is_registry_mergeable()` 按 **目录前缀+`.yaml`** 判定作用域（:197-201），而 `_split_registry_entries()` **只认顶层 list 族**（:223-259，作者自陈"ScalarNode/空文档→无族…走 noop 短路"）。命中作用域却切不出族的册：三侧族集皆空 → 无 splice → `merged==ours` → `_merge_registry_file` 返回 None（:1081-1085）→ `_apply_snapshot` 跳过该件（:1130-1132）→ 若袋内只有它则 `commit_files` 空 → **记 `landed_id=noop@<sha>` 且 `ok=True`（:1497）＝回执成功、HEAD 零变化、不留任何失败痕迹**。
- **无竞态复现（比 MERGE-01 的 39 秒复现更硬）**：`battle_map_domain_policy.yaml` 自 **09-22 13:20 无人改动**（`git log -1 -- <该文件>` ＋ `ours==base@0009落地父==48c26cd5a862` 亲验），故 base 与 ours 同字节、**排除竞态**；此前提下三种形态的 theirs 编辑——**P1 文件尾新增顶层键／P2 改已存在条目叶子值（0009 同形态）／P3 族内新增条目**——**全部判"合并结果==ours"**。⇒ 结论：**对该册任何形态的入队编辑都不承载**，不是"运气不好撞上竞态"。
- **人口（分母随判据同批声明＝纪律 R07）**：前缀下 tracked 83 件，命中 mergeable 判据 **82 册** ⇒ 可条目合并 **77**｜**零族（任何边修静默丢）3**＝`battle_map_domain_policy.yaml`、`depgraph_scan_exclusions.yaml`、`industry_graph_field_dictionary.yaml`｜**切分报错（任何改动必死信、永不可经队列合）2**＝`_index.yaml`（本身非合法 YAML）与 **`risk_tier_registry.yaml`**。
  - ⚠️ 后者根因值得单列：`domain_tiers` 条目引用别名 `*high_human_gate`（第 58 至 92 行间共 9 处），而锚点 `&high_human_gate` 定义在**另一个族** `tiers:` 的第 42 行——条目块被**独立**解析时锚点不在块内 ⇒ `found undefined alias` ⇒ 整册合并失败。**而 `risk_tier_registry.yaml` 正是宪法 §5 的人机门位册**（域→tier→human_gate 真源）＝**门禁强度配置无法经唯一合法提交通道落地**（本包未尝试改它，仅登记）。
- **全窗受害面（尺N，`done/` 现存记录，`dead/` 不计）**：`noop@` 回执 **89 袋** ⇒ 合法幂等 **A=46**｜袋≠HEAD **B=43**（歧义：可能"落了又被改"）｜**确证静默丢失 HARD=1**＝本包 0009（判据＝件在 HEAD、与袋不等、且该件末次提交时间 ≤ 袋落地时间 ⇒ 那次落地从未写过它）｜不可判 UNK=6（件已不在 HEAD，git 侧无法区分"从未写入"与"写入后被删"）。**读数随 HEAD 移动**：同脚本三次跑出 HARD=5→3→1（他包持续落地把歧义行改判出 HARD），以 10:54 时点 **HARD=1** 为准。
- **处方（三条全部路由 st-commitsys；本包不改提交系统＝§3.4/§0.8 高域自律）**：
  1. **可观测性（最小、且能立刻止血）**＝`merged==ours` 而 `theirs!=ours` 时**禁止**记 `ok=True/noop`，改死信并写原因"该册无顶层 list 族，条目级合并器不承载"——现回执与真幂等在证据上不可区分，是全场最坏的一种假绿（判据"回执不可信须复核"的唯一自动例外就该长在这里）。
  2. **承载**＝零族册回退行级三方（`base==ours` 已证无竞态时等价于整件写入），或显式声明"该册只走直连"。
  3. **前移**＝按尺M 的 `82/77/3/2` 生成"注册表结构普查册"（机生、勿手维＝§9.5），在 `enqueue` 当场拒绝不可承载件，而不是落地侧静默吞。
- **净零合规（§4.2）**：本案与 MERGE-01/EVAP 族**不并**——MERGE-01 的因是"入袋 `base_head/base_blob=None` ⇒ 兜底 `old_dev^` ⇒ 陈旧快照被读成主动删除"（条目级蒸发、需要竞态窗），本案的因是"作用域按前缀、承载按顶层 list 族 ⇒ 错配册根本不进合并"（**零竞态也丢**）。二者判据、复现、处方均不同 ⇒ 按"跨域不同对象→不并"分立两案。

## AC2 本包未连坐的反证（对 D27 的边界刻画，交 st-commitsys 参照）
本包最近四笔落地（`00a3bda7ac`/`21709f8f49`/`e964aeadbe`/`1fa27fb090`）`--name-status` **各只含 1 件 `M`、零 `D`**——而落地时主区 index 常驻他包 5 件 `t0_*` staged 删除。⇒ 他包登记的 **D27（落地块常驻 index 残留 delete 态被每个袋重复提交）对本包 markdown 通道未现形**，其病灶应限定在"注册表族/直连落地面"而非"所有落地路径"。复核：`git show --name-status <hash> | grep -c "^D"` 皆 0。

## AC3 对终态判据的作用（覆盖 AA6）
- ✅ 判据①"全部应修落地"现给**精确边界**：授权内可自修项全落（含 9 死信袋载荷面亲验零残损）；**唯一未落地面＝0009 那 3 行**，其因已升格为独立案 MERGE-02（有零竞态复现 ⇒ 重投 N 次仍会被吞，非"再试一次"可解）⇒ **维持登记上交、不再重投**。
- 🔄 判据③"连续两轮零新立"**计数重置**：第 3、4 轮本已达成，第 4 轮末新立 MERGE-02 ⇒ 据实重来，第 5、6 轮为新的两轮基线。**不抢跑宣布收官。**
- ✅ 判据④（红蓝反证）新增可套用产物：尺K2/L/M/N 四把尺都带**合成正负控制组**（阳性必红、阴性必零），且尺M 首版因我控制样本造错被尺自己 fail-closed 拦下（记 R36）＝"自写盘点脚本也要红证"这条纪律在本轮 again 生效。

## AC5 并案更正（对 AC1 的归因收敛，§4.1/§4.2 净零：同域重复簇→收敛唯一）
写完 AC1 后按 R17 纪律补做了"机制级"反查（此前我只反查**编号**撞车，未反查**机制**撞车），结果：
- **st-align-dirty 已立 D25**（`align_dirty_ledger.md:446/463`，09-24 晨间批）：`is_registry_mergeable()` 对 `_registry/catalogs/*.yaml` 一律走条目级三向合并，而 `fail_open_register.yaml` 顶层是**纯标量列表** ⇒ 合并器判"身份判不了" ⇒ **该册自 09-22 起任何改动都无法经队列落地**（q-0042 实测死信）。
- 与本案关系：**同一根（作用域按目录前缀、承载按条目族）不同枝**——D25 那枝**显式死信**（会报错、会被看见），本案这枝**静默 noop 且回执 ok=True**（不报错、不可见）。后果严重度不同：静默枝才是"全场最坏假绿"。
- ⇒ **处置＝并案不另立**：正式命名 **`F-AUDIT-MERGE-02 ≡ D25 的静默分支`**，本案对 D25 的**增量**共四项，缺一不立：
  1. 静默分支的**存在与判据**（`merged==ours ∧ theirs!=ours` 仍记 `ok=True/noop@`，`commit_queue_landing.py:1081-1085 → :1130-1132 → :1497`）；
  2. **人口分母** `82/77/3/2`（尺M），并给出**第三种成因**＝跨族 YAML 锚点（`risk_tier_registry.yaml` 别名在第 58-92 行、锚点在 `tiers:` 族第 42 行，条目块独立解析必 `undefined alias`）——D25 只覆盖"纯标量列表"一种；
  3. **零竞态复现**（尺L：base==ours 亲验，三种形态编辑 P1/P2/P3 全丢）——把"并发窗运气不好"这一解释排除掉；
  4. **全窗受害面量化**（尺N：89 张 `noop@` 回执 ⇒ 幂等 46／袋≠HEAD 43／确证静默丢失 1／不可判 6）。
- 处方同步并入 D25 那条（D25 已给"放过标量族 / 派生册声明 `merge_strategy: whole-file`"两条），本案补第三条：**回执语义修补**（静默丢弃必须显式化）——三条合起来是完整处方，单条都不够。

## AC6 尺O＝图 10 GOMAP 纯 HEAD 面双向普查（把第 3 轮的单点升级为穷尽）
第 3/4 轮的 GOMAP 结论都依赖生产校验器**恰好报出来的那一条**。校验器比对面是 `scan()`(工作树 rglob) ↔ `yaml`(盘版)，**HEAD 面从未整体量过**。尺O 把生成器入选判据（`SCAN_ROOTS=src/zephyr,scripts` + `SCAN_EXCLUDE_PARTS` + `_BUSINESS_EXCLUDE_PREFIXES` + `classify_family(rel)` 只看路径）原样重放到 **HEAD 提交树**，与 **HEAD 版 yaml** 条目集做双向差集：

| 量 | 读数（10:5x 时点，HEAD=`5471d43a52` 前态） |
|---|---|
| 应然（HEAD 树按生成器判据应进图） | **424** |
| 实册（HEAD 版 yaml 条目） | **423** |
| **HEAD 面漏挂（物有图无）** | **1** ＝ `scripts/audit/t0_gpu_condition_pack.py`（族 L2_resource） |
| **HEAD 面悬空（图有物无）** | **0** |
| 与生产校验器一致性锚点 | 该校验器 10:29 报的同一条**在本尺漏挂集内** ⇒ 尺与真源判据不矛盾 |
| 控制组 | 阳性＝抹掉真条目 `check_kill_switch_latency.py` 必被判漏挂 ✔；阴性＝自减必 0 ✔ |

⇒ **图 10 的收官结论由"1 条被报出来的漏挂"升格为"HEAD 面 423/424 挂齐、悬空 0、唯一漏挂属他包落地批未自跑刷新器"**；同时给出一条**结构性结论**：漏挂/悬空的唯一成因是"派生册以工作树为输入、无 HEAD 基线闸"（尺O 与尺L/M 同框），而非条目本身写错——这与 `F-AUDIT-GOMAP-INFLIGHT` 的定性一致，且**不新增案**（§4.1）。

# 附录 AC · 收官第 5 轮（新基线第 1 轮，2026-09-24 11:19 CST 实测，HEAD=`74ebcb0a50`）

## AC7 MERGE-02 第二枝＝"有族册的族外顶层键"同样被静默吞（R39 的实弹面）
AC1/AC5 把 MERGE-02 定性为"零族册（顶层无 list 族）任何编辑被 noop 吞"。**第 5 轮尺N 读数由 HARD=1 → 2**，新受害者**不是**零族册，而是一份**有族、被尺M 判为"可承载"的册**——证伪了"可承载＝全键可承载"的隐含假设：
- **新受害者**＝`st-backup-cold-20260924` q-…-0012 袋 `rule_catalog_registry.yaml`（末改 `bdc21d2240`@09:46:48 ≤ 落地 11:02:00 ⇒ 确证该次落地从未写入）。
- **被吞的恰是族外顶层标量键**：该册有 `files:`（顶层 list 族）+ 一堆顶层标量（`generated_at`/`total_files`/`total_rules`）+ 嵌套 dict `tier_distribution:`。差异行逐袋实测恒为 **2 行 = `generated_at: '<ts>'` + `total_files: <N>`**——`_split_registry_entries` 只 splice `files:` 族内条目，族外标量键的改动落在其视野之外 ⇒ 合并结果==ours ⇒ noop。
- **系统性复现（非竞态、非孤例）**：同一"改 rule_catalog 元数据"动作，跨 **4 个包 6 张 `noop@` 袋**（`st-ibt-remedy-cf` 0017/0021、`st-oddjobs` 0003/0010、`st-regfix-lane0b` 0011、`st-backup-cold` 0012）**每次都被吞同样 2 行** ⇒ 这是**结构性不承载**，重投 N 次仍吞（与 AC1 尺L 的零竞态结论同框）。
- **severity 分级（本枝 vs 我 0009）**：本枝受害者目标值**已 staged 于工作树**（`rule_catalog` 现 `MM`，盘版=`2026-09-24T00:56:02Z`/292，HEAD=`2026-09-20T09:41:29Z`/274）⇒ **非永久丢失，可经其他批次自愈**；但 `noop@` 回执仍误导（claim ok=True 实为未落 HEAD）。我 0009（`battle_map_domain_policy.yaml` 零族册）则是结构上任何编辑都进不去、盘亦无待落值 ⇒ **更硬**。同案不同 severity，处方不变。
- **尺互补性（防单尺假绿）**：尺H2（own-key 消失模型）对本枝 **dead=0**（顶层标量无 own-key，H2 看不见），**只有尺N**（noop 回执↔HEAD 差分）逮到 ⇒ 两尺不可互替，H2 干净不代表 N 干净。
- **处方增量（并入 D25/MERGE-02 交 st-commitsys）**：在 AC5 三条之上补 **(iii′) 入队普查粒度纠正**＝enqueue 侧对注册表件，须逐"被改的顶层键"判定其是否落在可 splice 的族内；落在族外（顶层标量/嵌套 dict）者**当场拒绝或整件走 passthrough**，不得凭"文件有族"放行后再在落地侧静默吞。
- **处置＝并案不另立**：同一根（作用域按目录前缀、承载按条目族、族外键无人接管）的第二枝；§4.2"同域重复簇→收敛唯一"。**且属他包（st-backup-cold）写域 + 注册表净删属 high 门位四类之一** ⇒ 本包**不代修**（§3.4/§0.8），只入本包案卷、路由 st-commitsys。

## AC8 align "硬项数"口径澄清（对第 4 轮"唯一硬项=GOMAP"的诚实校正）
第 5 轮 align HEAD 面 `--no-report` 头标"❌ 硬阻断: 4 个硬问题"，与第 4 轮台账"唯一硬项仍=GOMAP"表面矛盾。逐条拆解：`域不一致=0, 幽灵锚点=0, frontend=0, decision=0, factory=0, gomap=1` 之外，第 [3/9] 步"治理双向"报 `硬=3`＝裁定册 `#383`→`#MOD-L00-004`、`#387`→`#PS-CTR-003`/`#MOD-INF-043` 的 `related_arch` 悬空。**结论＝4 硬全部为已登记项、本包零新硬项**：1×GOMAP（`F-AUDIT-GOMAP-INFLIGHT`，他包在途）+ 3×裁定册 related_arch（基线"余 3=裁定册 related_arch×3、处方交 st-cmd、队列合并器对该热文件有已知撞车限制、勿硬闯"）。**差异非状态变化，而是第 4 轮复核命令 `grep -E "硬阻断|gomap"` 过滤掉了"治理双向=3"那行的呈现盲区**（该 grep 只匹配含"硬阻断"或"gomap"的行，治理双向 FAIL 行两词都不含）⇒ 自记：读 align 汇总须看各步 `硬=N` 明细，勿只信头标 grep。不改判据、不新增案。

## AC9 第 5 轮收敛判定
- 尺H2 dead=3（全属已登记 0009）｜尺J 待补块=0｜尺O 424/423/漏1/悬0（漏挂=GOMAP 他包在途）｜align 4 硬全登记｜尺N HARD=2（0009 + rule_catalog 第二枝）——**本轮零新立案**（新枝并入 MERGE-02＝AC7），为新基线**第 1 轮通过**。待第 6 轮再零新立，且尺N 的 HARD 不再增长（盯他包是否持续出现 rule_catalog/族外键类新受害者）→ 满足"连续两轮零新立"方可收官自删。
