---
ttl: task_bound
completes_when: 判定台账四表在 TableRegistry 有品类条目、plan_engine 六件表名全部经 get_registry() 派生、四格六向台账各有实测证据或转方
---

# FF-12 判定链 · 六向台账（车道 st-ff-judgment-20260918）

> 环节：判定→结算→反馈闭环的**载体层**（`judgment_*` 四表）。上游=plan_engine 发射件
> （MOD-PLAN-026/027/029/030/031/032）+ `strategy_pipeline.pipeline_events` 唤醒链；
> 下游=`daily_decision_orchestrator`（晨判消费）+ meta-回测逐层归因（标准 §四 聚合报告，未接电）。
> 铁律真源=`docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md` v0.1 §一（判定/结算分离）。
> 表述纪律（裁定#325）：本表只写实测，**不含任何"链路已打通"断言**。
> 三态账（两代车道合并口径）：前手车道 st-ff-judgment-20260918 = 绿 3 / 黄 2 / **红 1**（⑤ 无哨兵）；
> 本车道 st-ff-judgment2-20260918 救活死信后 = **绿 4 / 黄 2 / 红 0**（⑤ 转绿=4/4 表有腿并实跑）——
> ⚠️ "环节级无红"不等于"链无红"：④ 一格内含 **3 处红项**（只写不读 + 晨判两条 SQL 抛 Code 47），
> ⑥ 仍为 PROVISIONAL 静态推演，且 ⑤ 自身今日实报 1 条 breach（judgment_plan_verification 空表，真阳）。

## 0. 本车道治的结构性断点（不是治理洁癖）

四表 DDL-as-Code 真源 **2026-09-16 就已存在**（`schemas/categories/judgment/` 四件 + `apply_market_tables_ddl.py`
部署 + 线上表已建），但 `business_data_categories.yaml` **一条品类都没有**（实测：注册前 `grep judgment` 命中 0 行）。
后果是双层的：

1. **无 SSoT**——`get_registry().table()` 是唯一表名真源入口，查不到 → 消费方（plan_engine 六件）**只能**
   硬编码字面量；改表名 = 断链。
2. **门禁对本族结构性失明**——`TABLE-NAME-REGISTRY` 判据是"added 行的字符串常量是否命中**已注册**表名"
   （`table_name_registry_gate.py:169-180`）。未注册 ⇒ 永远不命中 ⇒ 该族的硬编码**不可能被任何自动机制发现**。
   换句话说：**没注册这件事本身，就是这条门禁在判定链上失效的原因**。

总包裁定 R-H3 定为治本（禁豁免/禁绕过）。本批 = 品类 YAML 注册（纯元数据新增）+ 六个消费件表名改派生，
**零线上表变更**（禁 ALTER/DELETE 红线遵守）。

## 1. 实测基线（T1，全部亲跑）

| 项 | 交接令说法 | 实测真值 |
|---|---|---|
| 判定表张数 | "judgment_* 五表" | **4 张**（`system.tables WHERE name LIKE 'judgment%'` = judgment_daily_plan / judgment_intraday_market_state / judgment_next_day_forecast / judgment_plan_verification，全在 c1_market） |
| `e19bc24c` | "被 TABLE-NAME-REGISTRY 硬拦，至今合不进去" | **已在 dev**：`git merge-base --is-ancestor e19bc24c HEAD`=真，经 merge `259b15c612`（E0-M2，st-tdchain-20260917）并入，距 HEAD 347 个 commit |
| 线上行数 | — | intraday=4 / next_day=3 / daily_plan=2 / plan_verification=**0**（`synthetic` 全 0，即 9 行为真生产行） |
| 表引擎 | — | 四张全 `MergeTree`（符合标准 §一.3 只增不改） |
| 品类注册表 | — | 注册前 206 个全限定表名 / 207 条 category_id（唯一、无重号） |

**子串连坐实测**（注册前穷举比对，注册后再复核）：四个新全限定名与既有 206 名做双向 `in` 比对，
**命中 0 条**（判定族表名自带 `judgment_` 前缀且无同名主干，结构性规避了 `consensus_daily` 那类连坐）。
注册后全限定名总数 206→210。

**SSoT 方向判定**：**规则数据（改 YAML）**。依据不是记忆而是 `table_registry.py` 模块头
（裁定 #ARCH-CH-024 原文："表名属于声明态规则数据（trae_062 铁律：表名是 schema 声明而非 DB 实例），真源是 YAML"）
+ 既有 210 条目全部以 YAML 为源、`apply_*_ddl.py` 只负责把 `schemas/categories/*.py` 的 DDL 打到 DB。
∴ 本批未走 apply_*.py 直写 DB 路径，也未新建第二真源。

## 2. 六向台账

| 向 | 判据 | 状态 | 实测证据 |
|---|---|---|---|
| ① 上游能取 | 发射器有生产数据落库 | **绿** | 三张判定表有真实生产行（4/3/2，`synthetic=0`，max(asof_ts)=2026-09-18）；发射通道=`judgment_ledger.emit_judgment`→`ch_writer.write_tsv_outcome` |
| ② 自身能算 | 判定/结算分离不被破坏 | **绿** | `test_insert_columns_match_schema_ssot` 机械钉死"INSERT 契约无结算列组"；本批改造只动表名派生，154 项判定链测试零回归 |
| ③ 落库有结构 | DDL-as-Code 真源与 DB 一致 | **绿**（本批不重复验） | 四表 DDL 真源早在 `schemas/categories/judgment/`；漂移守卫=`scripts/ch/verify_schema_truth.py`（他车道件，本批未跑）；本批新增的是**品类条目**（含 `schema_file` 指向存在性证明，受 SCHEMA-FILE-EXISTS 门硬校验） |
| ④ 下游能取 | 谁在读判定结果 | **黄（含 3 处红，本批实测加重）** | 亲验读者仅 2 个：`daily_plan._SQL_FORECAST` 读 next_day_forecast 台账（P2a→P2b）、`strategy_pipeline/daily_decision_orchestrator.py:170-173` 读 daily_plan+plan_verification（晨判）。**红 1**：`judgment_intraday_market_state`（4 行）**除结算器外零读者**、`judgment_settler.aggregate_report()`（标准 §四"逐层归因报告"唯一产物）**全仓零调用方**（`grep -rn aggregate_report src/` 只命中风控同名异体件）⇒ 作战室任务 1 的判定 = **只写不读的 R-021 同型假通道**，如实判红不判绿。**红 2/3（本批新证，前手未测）**：那唯一读者自己就是坏的——`_SQL_SCENARIO_PLAN` 查 `plan_date`、`_SQL_SCENARIO_VERIFY` 查 `data_date`/`ingest_ts`，而 system.columns 实测 `judgment_daily_plan` **无 plan_date 列**（plan_date 只在 inputs_ref 里）、`judgment_plan_verification` **无 data_date/ingest_ts 列**（列集=verification_id/plan_judgment_id/scenario_hits/actual_scenario_id/plan_followed/deviations/plan_quality_score/verified_at/verified_by/synthetic）⇒ 两条 SQL 在 HEAD 上直跑均抛 ClickHouse `ServerException Code 47 (UNKNOWN_IDENTIFIER)`（亲跑，见 §6.4）。判读：**"有读者"≠"读者能跑"**，晨判读判定台账这条路今天是断的，且因该文件属他车道在途（MM）本批未代修，处方见 §5.1 |
| ⑤ 哨兵在岗 | 表有阈值行盯停更 | **绿（本批改判；红牌搬家不搬家如实记）** | 前手判红时两册 0 命中；本批在 `src/zephyr/data/config/data_supply_sentinel.yaml` 落 **4 条腿**（实跑 `check_tables()`：改前 checked=51/breached=8 → 改后 **checked=55/breached=9**）。唯一新增 breach=`judgment_plan_verification` "empty table or dimension slice"，**真阳**（该表实测 0 行，见 ④/§3）——即"哨兵在岗"的表现恰是它立刻报红。三张有行表 lag=0、confidence 填充率 1.0 全绿。能红证据见 §6.3（runner 注入点，零生产写）。落地口径与前手提案的 5 处差异（含 `past_only: false`、`row_filter: synthetic = 0`、不配 FINAL、不配 min_rows_in_window、未进 quality 册）逐条记于 `lanes/judgment_sentinel_yaml_fragment.yaml` 头注 |
| ⑥ 失败会响 | 判定失败/表空时下游行为 | **黄（PROVISIONAL，纯静态推演）** | 见 §3，未做动态断供注入，不敢称实测。⚠️ 本批把 ⑤ 补上后，"表空静默"从**不可见**变为**可见**（verification 空表由哨兵红牌出声），但 ⑥ 本身的推演口径未变，故仍判黄不升绿 |

## 3. ⑥ 的细节（静态推演，标 PROVISIONAL）

- **结算失败 = 有声**：`pipeline_events.maybe_settle_judgment_ledger` 的 `except` 分支
  同时做 `log.error(exc_info=True)` + `alert(msg, level="ERROR")` + 返回 `{"action":"error"}`
  （`pipeline_events.py:780-785`）——"永不反噬调度器"与"出声"同时成立，这条是设计对的。
- **判定表空 = 静默**：`judgment_settler.settle_table` 对 `rows=[]` 直接 `return SettleReport(table,0,0,0,0,())`，
  上层拼进 INFO 级 brief（`pipeline_events.py:778`）→ 空表/断供与"今日无事可做"**不可区分**；
  叠加 ⑤ 无阈值行 ⇒ **判定链停更不会以任何红牌出现**。这是 ⑥ 的真缺口，且它只能由 ⑤ 补（故本批不越界改哨兵）。
- **`judgment_plan_verification` 0 行意味着 T2/T3 段在产线尚无证据**：盘中归类器与收盘定格器
  的代码/测试都在（`test_scenario_classifier` 20 + `test_close_verifier` 14 = 34 项绿），但线上验证行从未落过一条 ⇒
  作战室任务 3"验证昨日计划"**只有判定没有验证**。
- ⚠️ **推演未覆盖的两种情形（禁当已验）**：① `alert()` 的落点是否真能到人——2026-09-15 Owner 裁定已删除
  飞书/SMTP 通道、通知改前端 promotion 页，ERROR 级 alert 是否仍会到达人眼**未验**（若不会，⑥ 的"有声"只剩日志）；
  ② 唤醒链未触发的场景（daily_kline 任务失败/进程未起）下判定表停更是静默的——需动态断供注入才能定档。
  **注入验证需一次性写生产路径表，与"禁 ALTER/DELETE、测试禁写 data/ 业务目录"两条红线冲突** ⇒
  本车道不自行动态注入，转总包定验证方案（建议：reader 注入点 monkeypatch + 只读断言，勿写真表）。

## 4. 本批改动（提交面）

| 文件 | 改法 |
|---|---|
| `docs/03_modules/_cross_layer/database/business_data_categories.yaml` | +4 品类条目（纯 insert，71 行；房规照 `market_index_kline`/`market_cross_validation_log` 十五字段式；`schema_file` 指向既有 DDL 真源） |
| `src/zephyr/plan_engine/judgment_ledger.py` | 表名派生**单点**：`_DB`+`schemas.TABLE_NAME` 拼接 → `get_registry().table(...)`（四表，新增导出 `VERIFICATION_TABLE`）；`INSERT_COLUMNS` 仍从 schemas 取（列清单真源=DDL 文件，不动） |
| `judgment_settler.py` / `scenario_classifier.py` / `close_verifier.py` | 验证表字面量 → 从 `judgment_ledger` 导入派生名（禁另拼第二份） |
| `daily_plan.py` / `intraday_l1_tracker.py` / `next_day_forecaster.py` | SQL 常量表名字面量 → `{table}` 占位 + `JUDGMENT_TABLES[...]` 注入；常量按房规改名 `_SQL_*` 并去 `Final`（`_extract_sql_constant_lines` 只认 `ast.Assign` + `^_?SQL_\w+$`，见 §5 坑位 2） |
| `tests/plan_engine/test_judgment_ledger.py` | +6 项 SSoT 闭环守卫（品类可见 / 三向一致 / 缺席必 KeyError）；**本车道另 +17 项钩子 merge 守卫**（16 例金样本逐字段比对 + 1 例反回退结构钉，见 §6.2） |
| `src/zephyr/data/config/data_supply_sentinel.yaml` | **本车道新增**：判定链四表 4 条腿（新鲜度 trading_days + synthetic=0 维度腿 + 三表 confidence 填充率腿），71 行注释+条目纯 insert，插在 `hl_liquidation_raw` 与 edb_data 留痕注释之间（§6.3） |
| `src/zephyr/plan_engine/judgment_ledger.py` | **本车道新增**：`JudgmentEmitHook`（表侧参数）+ `run_judgment_emit_hook`（钩子骨架唯一真源）+ `make_judgment_emit_hook`（公开入口工厂），+`Callable` 导入与 `__all__` 三条 |
| `src/zephyr/plan_engine/daily_plan.py`、`next_day_forecaster.py` | **本车道新增**：两份 25 行重复骨架删除，改为"登记 `_EMIT_HOOK` + `maybe_emit_* = make_judgment_emit_hook(...)`"（reader/emit 以 lambda 惰性取模块全局，保既有 monkeypatch 注入点）。CloneGuard CAPABILITY-OVERLAP 死信的治本面（§6.1-6.2） |

派生 SQL 已按字节比对：七处查询的输出串与改造前逐字符相同（`FROM c1_market.judgment_daily_plan WHERE ...`）。

## 5. 留给后手（本车道不代修，§3.4）

1. **`strategy_pipeline/daily_decision_orchestrator.py:170-173`** 仍硬编码 `c1_market.judgment_daily_plan` /
   `judgment_plan_verification`（且带 `# noqa: bare-sql`）。**注册后这条硬编码已从"看不见"变成"改它即被 TABLE-NAME-REGISTRY 拦"**
   ——门现在有力了。该文件本批为 `MM`（他会话 staged+unstaged 在飞），按 §3.4 不代修；处方：
   改 `from zephyr.plan_engine.judgment_ledger import JUDGMENT_TABLES, VERIFICATION_TABLE` + `{table}` 占位。
   - **本车道复测（2026-09-18）**：`git status` 该文件仍 `MM`，但**工作区字节 == HEAD**
     （`git diff HEAD --numstat` 空），差异只在**索引面**：index 把 P4 收口的
     `_alert` 从 `log.error(...)` 回退成 `log.debug("告警通道不可达")`（staged `+2/-10`，
     `:472-482`）——**这是一次未提交的"加严回退"**，若被任何一笔按现暂存面落地的提交吸收，
     拍板链告警未送达会重新静默。判读：不知归属、不代修、不改暂存，仅登记（R-038 同型风险）。
   - **加重处方（本车道新证）**：不只是"表名硬编码"，那两条 SQL 引用的列**在 HEAD 上根本不存在**
     （`judgment_daily_plan` 无 `plan_date`；`judgment_plan_verification` 无 `data_date`/`ingest_ts`），
     直跑均抛 ClickHouse `Code 47 UNKNOWN_IDENTIFIER` ⇒ 收口时必须**一并改列口径**而非只换表名：
     预案日在 `inputs_ref` 内（判定族幂等锚 `%plan_date:<D>|%`，见 `daily_plan._SQL_ALREADY`），
     验证侧时间列是 `verified_at`、场景列是 `actual_scenario_id`/`scenario_hits`。
     改法属**语义决策**（读哪一列=晨判怎么理解台账），且文件属他车道 ⇒ 交总包定档派工，本车道不擅改。
2. **plan_engine 内 kline 族硬编码存量**（`intraday_l1_tracker._ETF_TABLE/_BREADTH_TABLE/_INDEX_TABLE/_A50_TABLE`、
   `next_day_forecaster._INDEX_TABLE`、`close_verifier._KLINE_SQL/_HAS_BARS_SQL`、`daily_plan._KLINE_SQL/_BREADTH_SQL/_NEXT_SESSION_SQL`、
   `scenario_classifier.py:383` 内联 SQL）——这些表名**大多已在注册表**，属 #ARCH-CH-024 Phase 5 存量欠账（diff-based 门不追）。
   本批**刻意未动**（越界且非判定链）。风险如实报：任何人改到这些行都会被 NO-BARE-SQL/TABLE-NAME-REGISTRY 拦，
   正解与 §4 同款。
3. **`judgment_plan_verification` 不合判定表通用骨架**（无 `judgment_id/asof_ts/module_id`，键是
   `verification_id + plan_judgment_id`）——标准 §二 的"所有判定台账表公共骨架"对它不成立。是设计取舍还是欠账，
   **属标准文档裁定面**，已在本批 YAML `hard_constraint` 里如实写明，交总包决定是否补进标准 §二。
4. **meta-回测逐层归因（标准 §五.3）零消费者**（④ 红项）——需要一条车道把 `aggregate_report()` 接进
   前端 promotion 页或归因报表，否则四表只是"能回测的账"，还不是"有人看的账"。
5. **quality 册（`config/quality_sentinel_tables.yaml`）对判定四表仍 0 命中**——本车道**故意未补**，
   三条实测理由（详见 `lanes/judgment_sentinel_yaml_fragment.yaml` 头注）：①tz 轴 `suspect_hours=[0..7]`
   是 Asia/Shanghai 口径，而本族时间列是 `DateTime64(3,'UTC')`（实测 asof_ts=01:47/08:07/08:34/11:11），
   配 `ts_col` 等于造一台天天误报的机器；②`empty_segment` 与本车道新鲜度腿重复，且
   `_SQL_RANGE_COUNT` 的 `<= toDate(end)` 上界对 DateTime64 会漏掉窗口末日盘中行（本族恰是盘中/收盘发射）；
   ③值维（N-1 型）已由 supply 侧 `column_fill_ratio` 单点守。**唯一有价值的缺口=epoch 纪元残留轴**：
   `asof_ts < toDate('1990-01-01')` 的判定行会让 PIT 锚与结算窗口静默错位，两册都不兜。
   → 处方：为该轴新增一维"仅 epoch"注册（需 owner 车道先给 `empty_gap_trading_days` 一个
   显式关闭语义或给日期列配 `toDate(toTimestamp(asof_ts))` 口径），禁为过检塞永真阈值。
6. **reDUP 无"委托块"下限**（本车道实测，登记为门禁质量断点候选，不走豁免旗）：
   merge 之后若两腿各留一个 `def maybe_emit_*(): return run_judgment_emit_hook(...)`，reDUP 仍判
   structural 100%（其 CLI 默认 `--min-lines 3`，委托块兜不住；见 `redup/cli_app/main.py:245`），
   于是"把 25 行重复压到 3 行重复"仍被 extract 级硬拦。现存的先例 `30dc814645`（R-002 vocabM 批）
   之所以过闸，实测原因是它两个薄封装的调用**写法不同**（一处 `field="plain_zh"` 关键字、一处位置参数）
   ——即今天的实际出口是"奖励参数写法不一致"，而 reDUP 对关键字/位置参数确判为不同结构
   （本车道对照实测：kw vs kw → 1.0；kw vs pos → 无组）。
   → 本车道未走该巧解，改走"入口工厂单点"（委托体也只有一份）。提请 Max 裁：
   是否给 CloneGuard/reDUP 增设"纯委托块（body 仅一条 return Call）不计 extract"的**结构性豁免判据**
   ——注意这是**放宽方向**，按 #321 只能由裁定批准，车道不得自便。

## 6. 死信接手记录（本车道 st-ff-judgment2-20260918，2026-09-18 21:0x-22:0x）

### 6.1 现场与判据复测（先读门，后定策）

- 死信 `q-20260918-st-ff-judgment-20260918-0001` state=dead，`dead_reason`=CAPABILITY-OVERLAP
  （`daily_plan.maybe_emit_daily_plan` ↔ `next_day_forecaster.py:383 maybe_emit_next_day_forecast`
  相似度 100%，extract 级 / structural）。
- **磁盘 vs 死件 blob**：11 件全部 sha256 逐字节相等（`blobs/<sha>` 与工作树双测）——
  **本车道基线=磁盘=死件**，不存在 z-verifier3 那次"磁盘比 blob 新 5 分钟"的分叉。
- 门的判据链（file:line 亲读）：`capability_overlap_gate.py:312-378`（阶段2 CloneGuard，
  `:341-364` 有"纯文档串编辑豁免" `_is_cosmetic_only_change`，本批两文件均有真实语义改动 ⇒ 不豁免）
  → `orchestrator.py:316 check()` → `redup_adapter.py:88-185`（CLI `redup scan --changed-only
  --base-ref HEAD --min-sim 0.85`，`:287-295 _severity_for` 采信 `metadata.actionability`）
  → `aggregator.py:68` `{"extract":3,"review":2,"acknowledged":1}`。
  `resolve_finding`/acknowledged 通道吃的键（`orchestrator.py:168-207 _load_acknowledged_pairs`）
  = `echo-guard.yml` `acknowledged[].stable_key`，格式 `"<path>:<func>||<path>:<func>"`
  （无序 frozenset，分隔符归一正斜杠，兼容剥离纯 hex hash8 尾段）；手册所记"手工登记必须补
  `stable_key` 否则白名单不生效"经源码复核成立（`_load_acknowledged_pairs` 只认含 `||` 的 stable_key）。
- **亲跑复现**（原样调 orchestrator.check）：`extract 1.00 structural | daily_plan:maybe_emit_daily_plan
  <-> next_day_forecaster:383:maybe_emit_next_day_forecast`，与 dead_reason 一致。
- **是不是既有克隆被本批触出？是。** 两份函数都在 HEAD（HEAD 行号 771 / 381，dead_reason 的 383
  是本批改动后的工作树行号）；把 HEAD 版两份函数原文喂给同一把尺子（`redup scan --min-sim 0.5`）
  → `structural 1.0`；再取 reDUP 全仓 changed-only 原始 JSON：组 `06c56c3a9d5495e5`，
  `similarity_score=1.0`、`type=structural`、`metadata={"provenance":"local_duplicate",
  "actionability":"refactor","reason":"duplicate stays within one component"}`
  → `actionability=refactor` 才映射成 extract（硬阻断）。**结论：真问题，非尺子口径冤案 ⇒ merge。**

### 6.2 T1 处置=merge（不走 ack，R-002/R-O1 同原则）

- 改法：骨架单点 `judgment_ledger.run_judgment_emit_hook`；两腿只登记 `JudgmentEmitHook`
  （查重 SQL/表名/模块号/对外键名/文档），公开入口由 `make_judgment_emit_hook` 生成
  （`__name__`/`__doc__` 还原，文档与可发现性不降级）。
- **为什么留两个 `def` 不行**：委托体两处仍是 reDUP 100% 克隆（§5.6 实测），
  继续留在两处=重复未消除；本方案骨架与委托各只有一份，且**未动阈值、未加白名单、未加旗**。
- 行为保真：`reader`/`emit` 以 `lambda` 惰性取调用模块全局 ⇒ 既有 monkeypatch 注入点不破。
- **金样本比对（改造前 vs 改造后）**：`.runtime/tmp/st-ff-judgment2-20260918/golden_{pre,post}_merge.json`，
  16 例（2 腿 × 8 分支：唤醒点不符/任务失败/已发射/已发射未落库/落库成功/ValueError 漏判/
  发射抛异常/业务日解析抛异常），每例记录①返回 dict 的**有序** JSON ②发给 reader 的 SQL 原文
  ③发给 emit 的业务日 ⇒ **sha256 全等 `aaa021588c973568…`**。
- 测试账：`tests/plan_engine` 整目录 **732 passed**；`tests/strategy_pipeline` 整目录 **155 passed**；
  三件相关套件单独跑 95 passed（含本批新增 17 项）。**因加严而转红的既有测试=0 条**。

### 6.3 T2 哨兵账（实测）

| 项 | 改前 | 改后 |
|---|---|---|
| `check_tables()` checked | 51 | **55** |
| breached | 8 | **9** |
| blind_spots | 0 | 0 |
| 新增 breach | — | `c1_market.judgment_plan_verification` "empty table or dimension slice"（**真阳**：实测 0 行、max(verified_at)=1970-01-01） |
| 判定链其余三腿 | 无 | lag=0（max_date=2026-09-18）、confidence 填充率 1.0 ⇒ 绿 |

- 基线说明：前手报"改前 36/1"是 z-sentinel 落地**之前**的旧账；z-sentinel 落地后为 51/8；
  本车道改前实测=**51/8**（与其一致），改后=55/9。
- **能红证据**（全部走 `check_tables(runner=…)` 注入点，零生产写、零 ALTER/DELETE）：
  ①max(date) 返 2026-08-01 → 四条腿全红 `lag=35d(trading_days) > 2d`；
  ②countIf 返 `9\t0`（行在而 confidence 全 0、日期新鲜）→ 三张判定表红 `低填充列 {'confidence': 0.0}`；
  ③`row_filter` 改 `synthetic = 7`（空切片）→ 四条腿全红 empty dimension；
  ④把 `max_lag_days` 误拼为 `max_lag_day` → `SupplySentinelError`（未知字段 fail-closed，不静默空转）。
- 未做（如实）：**⑥向的动态断供注入仍为 PROVISIONAL**。理由与前两代车道一致——本族四表是
  线上生产表（`judgment_*` 现存 9 行真生产数据），注入停更要写/删真表行，撞"禁 ALTER/DELETE +
  测试禁写 `data/` 业务目录"两条红线；本批用 runner 注入代替，能证明**判据能红**，
  不能证明**排班真跑时红**（06:50 槽位实跑归 z-sentinel 的 schedule 面，本车道未越界触发）。

### 6.4 ④ 向新证（本批实测，非推断）

`git show HEAD:` 版两条晨判 SQL 原文直连 ClickHouse 只读通道执行：
`SELECT plan_date, payload FROM c1_market.judgment_daily_plan WHERE plan_date='2026-09-18' …`
与 `SELECT data_date, actual_scenario_id FROM c1_market.judgment_plan_verification …`
→ 均 `ServerException Code: 47`（UNKNOWN_IDENTIFIER），rc≠0。
判读：晨判读判定台账的**唯一**程序读者今天是断的；这不是表名漂移问题，是列口径与 DDL 真源不一致
（列集实测见 §5.1）。**处置**：文件属他车道 ⇒ 只登记 + 出处方，不代修。

### 6.5 未越界声明

- 未写 `ruling_registry.yaml`（总包独占）；未自取裁定号；本文件内战役裁定一律 `R-0NN` 前缀。
- 未把 `capability_canonical_file_registry.yaml` 带进提交面：前手两件新文件的 creation_token
  实测**已在 HEAD**（由 `7d2571903d` 红队批吸收，`git show HEAD:<册> | grep judgment_chain`
  命中 line 32278/32282）⇒ 按手册 §3.1 剔除 carrier（该册工作树另有他人 8 行在途 insert，带入即连坐）。
- 未 `git commit` 裸提、未加 `--no-verify`/`--skip-preflight`/plumbing/手写 `[GW:]`；
  未动 `docs/03_modules/**` 除 `business_data_categories.yaml`（TableRegistry 唯一真源，
  延续前手"纯 insert 4 条目"口径，注册前后双向子串连坐穷举**复测命中 0**）。
- `COORDINATION_LEDGER.md` 本批**未**带入提交面（现 `MM`，含他家 staged 内容），交工账由总包回写。
