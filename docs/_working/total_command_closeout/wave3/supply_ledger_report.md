---
ttl: task_bound
completes_when: "3.2 假绿灯交叉尺与 3.3 供数守恒断言各自跑成红证+反事实控制组红，W-102 三把尺有 CI 可调用入口且逐把登记在册消费者"
---

# 波 3 · 3.2 / 3.3 数据链治本 + W-102 三把尺常设化（供数台账案卷）

## 0. 案卷头部（四字段）

- **turn_budget**：外部未给轮次上限；自设软预算＝每个调研块 ≤6 次工具调用、后期只落盘不再新调研。实际节奏＝调研块 1（判据/真源定位）→ 第 8 次调用内出本文件骨架 → 调研块 2（读数通道与宿主）→ 调研块 3（CI/登记约定与台账形态）→ 其余全部用于落盘与实测。
- **verified（实测，本会话内命令跑过或文件读过）**：
  - `10_wave_plan.md` L82/L83 判据原文：3.2＝`task_runs` 记账 ↔ 目标表真行数/最新业务日互证，不符报红并**降级下游**，自带反事实控制组（喂一行假 SUCCESS 而目标表不动 ⇒ 尺必须红）；3.3＝EV-03 搬到数据链、**内收不造第二套**、新鲜度用业务表 `max(date)` 不用 `system.` 面。
  - `00_master_skeleton.md` L79 `W-31`、L80 `W-32`、L162 `W-102`（三把尺＝禁缓存背书／供数守恒／反事实控制组入判据模板）、L236 `W-176`（业界四家对表"并入 W-102 注记行"）。
  - `92_acceptance_rulers.md` L34 `G-22 供数守恒`：判据"写后独立读最终真值与任务自称对账，不符降级下游｜落库后回读｜相等｜改回执不改数据 → 红"，指向波 3.3。
  - `01_adjudication_master.md` L59 `Z-16`：交叉尺＝回执与真值互证；"同一病同一药，禁造第二套（EV-03 家族扩展，内收原则）"；"新增尺需自带反事实控制组"。
  - `02_field_corrections_and_new_cases.md` L43 `X-24`：假绿灯名单**现跑现出、禁引旧名单**（旧"不可分辨集合 4 件"本窗仅 1 件成立）⇒ 本包尺内不携带任何历史名单常量。
  - `93_owner_menu.md` L144/L285：EV-03 已有归宿＝W-32/W-102，**不重复立项**（本包据此只做数据链，不碰提交链 EV 件）。
  - 记账表真源＝`src/zephyr/data/progress_store.py`：`task_runs(run_id, task_id, started_at, finished_at, status, rows_fetched, rows_written, error_msg)`；默认库 `REPO_ROOT/data/integrator_progress.db`（主区实测 37MB 活库，WAL 侧车在册；车道内 `data/` 无此库，`data/databases/integrator_progress.db` 为 0 字节死库，与 1A.5 描述一致）。
  - 既有台账消费者＝`src/zephyr/data/integrity_checker.py` L225/L246/L268 `_reconcile_task_runs`：只核对"今日应跑任务在 task_runs 是否有 SUCCESS"，**从不回读目标表真值**，且 `_query_task_runs_today` 注释自陈"失败返回 {}"（fail-silent）⇒ 这正是假绿宿主，本包 3.2 补的就是它缺的真值腿。
  - 供数对账既有宿主＝`src/zephyr/data/supply_sentinel.py`（`module_id: MOD-L00-004-SS`）+ 阈值唯一真源 `src/zephyr/data/config/data_supply_sentinel.yaml`（字段实测含 `date_col/max_lag_days/past_only/cadence/min_rows_in_window/column_fill_ratio/heartbeat_leg/gap_id/allow_empty`）；在册消费者＝`src/zephyr/data/scheduler.py` L238 `data_supply_sentinel` 槽位。
  - 缺口台账既有宿主＝`src/zephyr/data/config/known_data_gaps.yaml` 顶层 `gaps:` 列表，条目字段实测＝`id/table/gap_type/start_date/end_date(null=开放至今)/date_column/status/...`；消费者＝`src/zephyr/data/backfill_checker.py::run_known_gap_backfill`（L919 `_KNOWN_GAPS_PATH`）。
  - W-180.1 严格读通道**已在册可用**：`src/zephyr/data/ch_reader.py` 提供 `query_rows / count_strict / inject_final_strict / query_rows_table`，`[ERROR_CONTRACT]` 明文"query 失败返回空串、count 失败返回 0 → **判据类读数禁用**"⇒ 本包判据只走严格通道。
  - CI 挂载约定：`.github/workflows/governance.yml` 逐步调用 `python scripts/governance/... --check`；rc 命名常量真源＝`scripts/governance/_shared/constants.py` `EXIT_PASS=0 / EXIT_FINDINGS=1 / EXIT_ERROR=2`（`validate_exit_codes.py` 禁裸数字）。
  - 复杂度门自家尺＝`zephyr.gov_enforcement.commit_gates.high_complexity_gate._cyclomatic_complexity`（`d7_code/scan_complexity.py` 同源）；本包 12 个新 .py 复算结果 **零违规**（CCN ≤15、参数 ≤7）。
  - `src/zephyr/intelligence/observability/` 实测**不存在**（`find` 无该目录）⇒ 见 §6 越界规避决定。
- **assumed（假设，未在本窗验证，落地方须复验）**：
  - `tasks.yaml` 的 `dependencies` 反向即为数据链下游闭包——实测 12+ 条非空依赖（如 `adj_factor -> kline_daily_hfq`），但未穷举全部 270 任务的血缘完整性；派生自 `derive_task_dependencies.py`（[DAG-DERIVED] 标记在册），本包未复算该生成器。
  - 生产环境 CH 可达时两把尺的 live 输出面（本窗 CH 不可达，见 §4-C：尺选择以 rc=2 显影而非判绿，这条**已被实测**，但完整 live 名单未出）。
  - `known_data_gaps.yaml` 的 `status` 取值全集（本包按 `accepted/open/in_progress/monitoring/deferred` 视为生效申报、`completed/resolved/fixed/closed` 视为不再背书；未在盘上穷举实际枚举）。
  - CI 步与消费者接线须 Owner/GW 侧登记（本包禁改热册与工作流，见 `registration_needs.yaml`）。
- **input_set_disjoint_with**：
  - 本包**只新建 14 件**：`scripts/governance/data_supply/{__init__,supply_sources,strict_truth_reader,false_green_crosscheck,supply_conservation,no_cache_endorsement,check_wave3_rulers,gen_registration_needs}.py`（8 件）、`tests/governance/data_supply/{__init__,test_false_green_crosscheck,test_supply_conservation,test_no_cache_and_cli_rc}.py`（4 件）、本文件 + 同目录 `registration_needs.yaml`（2 件，后者由生成器现读现出）。
  - 与兄弟包的不交面：`src/zephyr/intelligence/observability/**` 本包**一件未建**（该目录不存在，建包＝与"别人可能建包"的正面撞车面，主动放弃，见 §6）；`src/zephyr/data/**`、`config/**`、`docs/01_policies_and_standards/**`、`.github/**` 全程只读。
  - 只读输入集：`tasks.yaml` / `data_supply_sentinel.yaml` / `known_data_gaps.yaml` / `progress_store.py` / `ch_reader.py` / `integrity_checker.py` / `supply_sentinel.py` / 五本主册。
- **evidence_ref.cmd**：§4 三条命令原文 + 实测输出（A 控制组、B 离线常设尺、C live 失败必抛）。

## 1. 3.2 假绿灯交叉尺（W-31 / Z-16）

**判据实现**＝`scripts/governance/data_supply/false_green_crosscheck.py`（入口 `evaluate()`）。

| 腿 | 断言（Z-16 口径） | 红码 | 态 |
|---|---|---|---|
| 回执↔真值 | SUCCESS 且 `rows_written>0`，业务日独立回读为 0 | `FAKE_GREEN` | RED |
| 量值蒸发 | 实到 < 回执 | `RECEIPT_OVERSTATES` | RED |
| 未申报旁路写入 | 实到 > 回执 | `ARRIVAL_EXCEEDS_RECEIPT` | WARN |
| 空表自证 | SUCCESS 且回执 0 行、表确证空（严格通道已排除"读失败=0"） | `SUCCESS_EMPTY_TABLE` | RED |
| 新鲜度 | SUCCESS 但业务表 `max(date)` 落后 > 声明阈值 | `STALE_BEHIND_RECEIPT` / `FRESHNESS_UNKNOWN_EMPTY` | RED |
| 台账外任务 | SUCCESS 但 tasks.yaml 无声明 | `UNKNOWN_TASK` | RED |
| 静默空表无凭据 | `allow_empty` 且无 `gap_id`（BRK-046 纪律） | `SILENT_EMPTY_NO_GAP` | RED |
| 零回执 | 窗口内无任何 SUCCESS | `EMPTY_LEDGER` | RED（禁"无记录即无违规"） |

**降级下游**＝`tasks.yaml` 声明血缘（上游→下游反向邻接 + 传递闭包），红项任务的下游子任务与其目标表逐条点名：
`Verdict.offending_tasks`（肇事）/ `downgraded_tasks`（下游任务）/ `downgraded_tables`（下游表，窗内回执不得背书）。
X-24 合规：名单全为现跑现出，模块内**无历史名单常量**。

**宿主关系（内收）**：既有 `integrity_checker._reconcile_task_runs` 只做台账自证；本尺是它的**真值腿**，不另立记账面，不新建台账。

## 2. 3.3 供数守恒断言（W-32 / EV-03 家族 / G-22）

**判据实现**＝`scripts/governance/data_supply/supply_conservation.py`（入口 `evaluate()`）。

EV-03 的病＝"货单有记录、仓库里那件东西不见了"；药＝回执与真值互证。搬到数据链的守恒式：

```
声明供货日集合  △  实到供货日集合   ⊆  known_data_gaps 中仍生效的申报覆盖集
交集上： 实到行数(D)  ≥  声明行数(D)      （负差＝蒸发，红）
```

| 腿 | 断言 | 红码 | 态 |
|---|---|---|---|
| 集合腿（蒸发） | 回执声明供数、表侧该日 0 行且**无生效申报** | `UNDECLARED_EVAPORATION` | RED |
| 集合腿（已申报） | 同上但有生效缺口申报 | `GAP_DECLARED_MISSING_DAY` | WARN |
| 量值腿 | 声明 77 / 实到 40 | `PARTIAL_DELIVERY` | RED |
| 旁路写入 | 表侧有数、台账无回执 | `UNDECLARED_ARRIVAL` | WARN |
| 无日期轴 | 既无 `tasks.yaml date_col` 也无哨兵腿 | `NO_BUSINESS_DATE_COL` | RED |

**申报背书的时效性**（防"申报变永久放行"）：只有 `status ∈ {accepted, open, in_progress, monitoring, deferred}` 且 `day ∈ [start_date, end_date]`（`end_date: null`＝开放至今）的条目才覆盖；`completed/resolved` 的旧缺口**不再背书**（测试 `test_completed_gap_does_not_excuse_current_window` 钉住）。

**内收落点（未造第二套）**：声明侧三个输入全部派生自既有真源——`tasks.yaml`（谁供哪张表）+ `task_runs` 回执（自称供了多少，经 `ProgressStore` 宿主 API 读）+ `known_data_gaps.yaml`（已申报缺口）；新鲜度阈值直接复用 `data_supply_sentinel.yaml` 的 `max_lag_days` 腿。**未新增任何阈值册、未新增台账表**。
与 3.2 的分工＝同真源、不同断言面：3.2 逐回执行交叉核对并点名降级下游；3.3 在"表×窗口"上做集合/量值守恒与申报台账对账。

## 3. W-102 三把尺常设化 + 既有消费者挂载表

**CI 入口**＝`scripts/governance/data_supply/check_wave3_rulers.py`

```
--check [--ruler all|false-green|conservation|no-cache] [--offline]
        [--as-of YYYY-MM-DD] [--window-days N] [--limit N] [--ledger <path>]
--counterfactual [--ruler ...]
```

rc 契约（唯一对外语义）：

| 模式 | 0 | 1 | 2 |
|---|---|---|---|
| `--check` | 三把尺全绿 | 有红项（违规名单点名） | 声明侧真源不可用 / 读数失败必抛（禁洗成 0） |
| `--counterfactual` | 三把尺控制组全部如期显影（负控制转红 **且** 正控制保持绿） | 有尺退化（该红没红 / 该绿不绿） | 控制组自身异常 |

`--offline` 只跑不触库的"禁缓存背书"尺，供无 CH 的 CI 槽位。

**三把尺各自挂在哪个既有消费者上**（零消费者的尺＝装饰件；本包把"现在真在消费的"与"待登记才生效的"分列，不混称）：

| 尺 | 现在真实存在的消费者（本窗实测） | 待登记的生产挂载点（本包无权改，见 registration_needs） |
|---|---|---|
| 禁缓存背书 | `check_wave3_rulers --check --offline` 直接调 `no_cache_endorsement.evaluate()`（末次实测 RC=0、`scanned=7 files`）；`tests/.../test_no_cache_and_cli_rc.py` 12 条断言 | `scripts/governance/observability/gate_cache.py` 的在册消费面 `run_all.py` / `phase_manager.py`（该文件 `[CONSUMERS]` 行实测原文）；`.github/workflows/governance.yml` 新增一步 |
| 供数守恒（3.3） | `--check --ruler conservation` + 7 条 pytest | `zephyr.data.scheduler` L238 `data_supply_sentinel` 槽位（宿主 `supply_sentinel.py`，schedule.yaml 06:50 日批在册）——守恒腿作为该哨兵的新维度 |
| 反事实控制组 | `--counterfactual`（rc 契约即"尺是否还活着"）；3 把尺各带负/正两半控制组，28 条 pytest 全绿 | 判据模板挂载：新尺准入须声明其控制组（建议并入 `gate_registry.yaml` 准入面，属热册，本包未动） |
| （3.2 假绿灯交叉尺） | `--check --ruler false-green` + 9 条 pytest | `zephyr.data.integrity_checker._reconcile_task_runs` 补真值腿（该函数现状"失败返回 {}"是在册 fail-silent，本包无权改宿主） |

注：三把尺的**判据逻辑与被测宿主之间的接线**需要改 `src/zephyr/data/**` 与 `.github/**`，两者都在本包写权之外 ⇒ 未接。本包能自证的消费面＝CLI rc + 28 条测试；生产挂载以 `registration_needs.yaml` 申报，不虚报"已挂上"。

## 4. 红证台账（命令原文 + 实测输出）

### A. 三把尺的反事实控制组（负控制转红 + 正控制保持绿）

```
$ python scripts/governance/data_supply/check_wave3_rulers.py --counterfactual
[counterfactual] 3.2_false_green -> OK（负控制转红、正控制保持绿） red_codes=['FAKE_GREEN', 'FRESHNESS_UNKNOWN_EMPTY'] probe_reads=3
    负控制=假 SUCCESS(rows_written=120) 表侧不动 → 红项 2 条；正控制=表随回执动 → 红项 0 条
    点名降级下游（其窗内回执不得背书）=['downstream_consumer']
[counterfactual] 3.3_supply_conservation -> OK（负控制转红、正控制保持绿） red_codes=['UNDECLARED_EVAPORATION'] probe_reads=2
    负控制=声明 77 行 / 表侧不动 → 红项 1 条；正控制=声明与实到相等 → 红项 0 条
[counterfactual] W-102_no_cache_endorsement -> OK（负控制转红、正控制保持绿） red_codes=['FAIL_SILENT_READ', 'MEMOIZED_JUDGMENT_FUNC'] probe_reads=4
    植入 ch_reader.count() 与 @lru_cache 两个反例须双双点名（实得 ['FAIL_SILENT_READ', 'MEMOIZED_JUDGMENT_FUNC']）；干净源码误报 0 条；行为腿双读 live=True
RC=0
```

判据点：3.2 的负控制正是 Z-16 原句"喂一行假 SUCCESS 到台账但目标表不动 ⇒ 尺必须红"；
降级面同时点名下游 `downstream_consumer`（肇事任务另列于 `offending_tasks`）。

### B. 常设尺离线绿面

```
$ python scripts/governance/data_supply/check_wave3_rulers.py --check --offline
[no-cache] scanned=6 files probe_reads=4
RC=0
```

### C. live 面：读数失败必抛、以 rc=2 显影（W-180 红线，绝不因读不到判绿）

台账经**既有宿主** `ProgressStore` 写入 tmp 夹具（一条 `adj_factor_incremental` SUCCESS/rows_written=5000，实测 `rows: 1`），真值侧走严格通道读 CH：本车道无 `config/.env.clickhouse`（属车道外配置，本包无权创建），CH 不可达。

```
$ python - <<'PY'   # 见 §附录命令：cli.main(["--check","--ruler","false-green","--ledger",<tmp>,"--as-of","2026-09-26"])
...
CH query_strict 失败(TCP+HTTP 均失败): SELECT trade_date AS d, count() AS n FROM c1_market.adj_factor WHERE trade_date BETWEEN toDate('2026-09-26') AND toDate('2026-09-26') GROUP BY d ORDER BY d | attempts=[('tcp', 'client 不可用（配置缺失或处于冷却期）'), ('http', 'host 不可用（配置缺失或处于冷却期）')]
scripts.governance.data_supply.strict_truth_reader.TruthReadError: 严格读数失败: SELECT ... :: ClickHouseQueryError: ...
[error] TruthReadError: 严格读数失败: ...
RC= 2
```

同一命令里可读到三件事实：① 判据 SQL 是业务表逐日 `count()` 与 `max(trade_date)`（新鲜度未碰 `system.` 面）；② 引擎探测/FINAL 注入由宿主 `inject_final_strict` 承担（失败必抛）；③ 尺在 CH 不可达时给 rc=2，不给绿。
**本窗未获得完整 live 违规名单**（CH 不可达），该项列为 §5 待复验项，不伪造。

### D. 测试面（28 条，含两把尺全部红/绿控制组）

```
$ python -m pytest tests/governance/data_supply -q
tests\governance\data_supply\test_false_green_crosscheck.py .........    [ 32%]
tests\governance\data_supply\test_no_cache_and_cli_rc.py ............    [ 75%]
tests\governance\data_supply\test_supply_conservation.py .......         [100%]
============================= 28 passed in 2.91s ==============================
```

### E. 复杂度/参数门自家尺复算（禁调阈值）

```
$ python - <<'PY'  # 用 high_complexity_gate._cyclomatic_complexity 复算 12 个新 .py
VIOLATIONS: none
```

首轮复算曾命中 1 条 `supply_conservation.check_table` 参数 8 > 7，已按门禁口径把 `lo/hi` 收进 `Window` 值对象后复算归零（未改阈值）。

## 5. 现势名单与待复验项

- X-24 要求的"现跑现出名单"＝命令 C/D 的入口，**必须**在 CH 可达面（Owner 机/带 `config/.env.clickhouse` 的槽位）复跑 `--check --ruler false-green` 与 `--check --ruler conservation` 才出真名单；本窗只出判据行为，不出名单。
- `270 任务`全量普查（H-110 提及）未在本窗执行：live 面不可达，跑它只会得到 rc=2。
- 台账装载路径：生产槽位应显式传 `--ledger <REPO_ROOT>/data/integrator_progress.db`；本包刻意**拒绝**由判据侧建库（`open_progress_store` 路径不存在即抛），以免复制 1A.5 点名的"0 字节死库"病因。

## 6. 越界规避与自我约束记录

- `src/zephyr/intelligence/observability/**`：实测该目录不存在。任务许可是"仅在不与别人撞的前提下新建**子件**"，建包本身即撞车面 ⇒ **本包一件未建于此**，全部落 `scripts/governance/data_supply/**`。若 Owner 要求 observability 面，需先定包归属（registration_needs 已列）。
- 主区工作树：零写入。全程未 `git add` / `git commit` / enqueue；CH、PG 零写入；未创建 `config/.env.clickhouse`；未改 `docs/01_policies_and_standards/**`、`config/flags.yaml`、任何阈值/断言/skip/xfail；无删除动作；无 kill 进程；未跑 `test_ops_guard_red_team.py`。
- 测试写盘：全部走 `tmp_path` / `tempfile`，`data/` 生产路径零写入。
- 指令/数据边界：本包未自赋任何裁定号；文内 ⬜/待办均为**申报**而非批准。§3 的挂载表把"实测已在消费"与"待登记"分列，避免把待办写成既成。
- 落盘换行：新文件写后统一 LF 校验（实测 0 个文件含 CRLF）。

## 7. 待登记件

见同目录 `registration_needs.yaml`（**由 `scripts/governance/data_supply/gen_registration_needs.py` 现读现出**，AGENTS §9.5 静态清单禁手工维护；实测输出 `files=14 mounts=8 anchor_incomplete=[]`）。内含：14 个新建件的 `module / module_id / startup / ttl / consumers`，8 条待登记挂载（CI 两步、`integrity_checker` 真值腿、`supply_sentinel` 守恒维度、新尺准入控制组条件、observability 包归属、模块大白话简介、CREATE-GUARD token），以及"本包明确未登记/未改"的负清单。

> 注：§4-A/B 的 `scanned=6` 是加生成器**之前**的实测；加 `gen_registration_needs.py` 后同一命令为 `scanned=7`、`--counterfactual` 仍 RC=0（§4-A 末次复跑输出为准）。
