---
ttl: task_bound
completes_when: 本车道六项断点与六个待合并片段全部要么落地、要么登记交总包（无静默丢失）
---

# 编排与排班车道（st-ff-dag-20260918）· 接力与登记

> 单一写者制：本车道独占 `src/zephyr/data/config/tasks.yaml` + `schedule.yaml`。
> 本文件逐片段记"已合 / 未合 / 为何"，未合项均已回写 `COORDINATION_LEDGER.md` §6 待裁表。

## 1. BRK-050 依赖推导器（主件）

- 推导器：`scripts/derive_task_dependencies.py`（幂等、可重跑；`--dry-run` 出清单，`--apply` 落高置信边）。
- 建议清单产物：`docs/_working/fullflow_campaign/lanes/dag_dependency_proposals.md`（逐条 file:line 证据 + 置信度）。
- 实测前后对比（硬判据命令 = `python -c "import yaml;t=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks'];print(len(t),sum(1 for x in t if not x.get('dependencies')))"`）：
  - 普查基线：`262 235`
  - 片段合并后（+4 任务，其中 2 件自带 deps）：`266 237`
  - 推导器 --apply 后（本车道交付态）：**`266 226`**
  - 净效果：无依赖任务 235 → 226（同分母 262→266 下，声明依赖的任务 27 → 40）。
- **诚实覆盖面说明**（这是本件最重要的判读，勿把 226 当"已通")：
  表级读取血缘在本仓**没有登记处**——`dataflow_graph_registry.yaml`/`data_asset_registry.yaml` 的
  dataset 是契约级（`market_data.tick`），`consumed_by_jobs` 仅 12/264 有条、job.inputs 仅 66/122；
  depgraph `dataflow_edges` 实测 90 边全是 `design` 态 job→dataset（与普查 BRK-058/059/061 一致）。
  故可机检的表级血缘只能从**实现码**（`_fetch_<capability>` 函数体 + 同文件被调方法 + 模块级常量 +
  跨文件一跳）与**任务自述文字**里抠，而 provider 层普遍以 `payload.table`/`{table}` 参数化读表，
  文字面量少——推导器实跑证据 189 条、成建议 33 件、高置信落地 16 件。
  → 剩余 226 件中相当部分是**真·无上游的独立采集任务**（akshare/外部 API 直供），对其
  补 `dependencies: []` 是假闭环，本车道不做（R-013 教训：接错比不接更糟）。
  → 治本后续（交总包/FF-01 簇）：把表级血缘登进 `dataflow_graph_registry.yaml`（dataset 用
  `c1_market.<table>` 作 entity_name，156 件已是该形态），补齐 `consumed_by_jobs` 后**重跑本推导器即自动扩面**
  （推导器把品类册 + 注册表当输入，不需改码）。
- 环保护：逐边试加，成环即弃并打印 `CYCLE-REJECT`（实跑拦下 3 条共享 pattern 模块造成的假边）。
- 扇入预算 `MAX_NEW_DEPS_PER_TASK=4`：TaskQueue 语义是"任一前置 FAILED → 当前 BLOCKED"，
  无节制扇入会把 20 张 K 线表全挂成 `technical_indicator` 的前置=新增故障耦合。超预算同族边在
  建议清单 §2.1 登记，不落地。

## 2. BRK-067 双任务争非线程安全 SDK 单例

- 家族先例（同文件既有表达）：`kline_sector_incremental` 已用 `dependencies: ["industry_class_refresh", "kline_sector_880_incremental"]`
  把并发 tqcenter 任务**排成同批先后**（`_run_schedule_dag` 用局部 TaskQueue，同档期依赖才真门控）。
  → 即"显式串行依赖"是本仓既有机制，无互斥资源声明机制，**不发明新机制**。
- 本车道补的是残留豁口：`kline_sector_880_resample`（同 tqcenter、同 `daily_kline` 档期）此前只等
  `kline_sector_880_incremental`，于是它与 `kline_sector_incremental` **仍可并发**（二者在同一批里同为 READY）。
- 改法：`kline_sector_880_resample.dependencies += kline_sector_incremental`，并注释指明
  缺口真源 `known_data_gaps.yaml id=kline_sector_concept_shrinking`（gap_type=universe_shrinking）。
  最终链：`kline_sector_880_incremental → kline_sector_incremental → kline_sector_880_resample`（同批严格串行）。
- 另：推导器 D1 检测器 `_source_contention()` 已把 tqcenter/miniqmt/tdx/tickflow 四单一实例源
  在同档期的共批任务对全部列出（见建议清单 §3），供后续逐族核对串行化，不再靠人眼。

## 3. BRK-051 四盏死任务显式化（禁删，只标注）

| 任务 | 标注结果 |
|---|---|
| `dividend_incremental` | 原**无** `disabled_reason` → 新增：源退役+schema 不匹配、缺口 `id=dividend_plan_miniqmt_retired`、处方（切 akshare 预案接口挂 daily_event）、替代链 `ex_dividend_event_incremental` 在册 |
| `futures_warehouse_receipt_backfill_shfe` | 原 reason 无缺口锚 → 改为 `[BRK-051 显式登记·断源非忘排]` + `id=futures_warehouse_receipt_shfe_archive_cap`（BRK-039，provider 硬界 2025-11-30） |
| `futures_warehouse_receipt_backfill_czce` | 改为 `[BRK-051 显式登记·一次性回填已了结]` + 同族 SHFE 缺口交叉指针 |
| `road_freight_index_full_refresh` | 改为 `[BRK-051 显式登记·一次性爬取已了结]` + 同型半死管线警示 `id=reservoir_level_source_stale`（BRK-040：按 max(date) 而非 ingest_ts 判活） |

## 4. BRK-022 核实结论（普查说的对不对）

- **先自验后动手**（R-013 纪律）：`grep -rn compute_nightly_sentiment` → 生产侧命中
  `scripts/data/run_nightly_sentiment.py:41-42`；`schedule.yaml` 在册槽位 `nightly_sentiment`
  （cron `20 8 * * *`，executor default，当日窗口+近 7 日缺口自愈）。
- 结论：**普查记载成立**（台账确实陈旧），该 gap 已按实测改 `status: completed` +
  `last_updated: '2026-09-18'`，并在 `resolution_plan` 内写闭合证据（两处 文件:行号），
  未新增字段（保 schema 面）。文件为 LF 真源，改后 `git diff --numstat` = `3 3`（零换行污染）。
- 同类顺手扫：其余 monitoring/reopened/open 共 9 件，逐件核处方引用的脚本/配置是否已在盘，
  **未发现第二件"已修但挂 monitoring"**（唯一在盘引用 `scripts/ch/repair_etf_minute_tz_split.py`
  属 instL 车道在飞 + Owner 门位，挂 monitoring 正确）。

## 5. R-015 对账档期 + 哨兵

- `schedule.yaml` 新增 `eod_reconciliation`：`cron "40 15 * * 0-4"`、`executor default`、`max_instances: 1`
  （15:40 = 收盘 15:00 + 柜台日终批之后，且早于 L4 `daily_kline` 16:30）。
  描述点名唯一入口 `src/zephyr/trading/recon_runner.py:392 run_daily_reconciliation`（R-015 定的"日终=recon_runner"）。
  **四要素辨析已写进槽位注释**：宪法 §9.3"reconciler 必须事件触发"约束的是**自愈环**；
  本槽位是**定时事实核对批**（与 L11 `integrity_check` 同性质），不据此声称自愈闭环达成。
  事件扇出侧（`PositionReconciler.handle_execution_report`）属 `src/zephyr/ex_core/**`=z-land，本车道未碰。
- `data_supply_sentinel.yaml` 新增 `c1_market.execution_report` 阈值行：`date_col: trade_date`、
  `max_lag_days: 10`、`past_only: true`。定档依据写在同行注释：本表按**成交事件**产行，
  无成交日不落行，3 天档必常态误报；10 天=一个自然交易旬。
- **未做**：哨兵实跑 breach 数未取（六向⑤要求实跑 0 breach）。原因=轮数预算，
  登记在此供复核：`python -m zephyr.data sentinel`（或 L13 槽位自动跑）需下一轮执行。

## 6. 六个待合并片段逐条结果

| # | 片段 | 结果 |
|---|---|---|
| 1 | `lanes/altdataF_tasks_yaml_fragment.yaml` | **已合并** 2 件任务（`cftc_positioning_refresh`/`gold_etf_holdings_refresh`），但置 `schedule: disabled` + `extra.disabled: true` + `disabled_reason` 标翻转前置。原因=前驱未入 HEAD：`akshare_alt_provider` 的 `cftc_positioning`/`gold_etf_holdings` 能力实测 **HEAD 里 0 命中**（staged +117 / worktree +57），部署件 `scripts/ch/apply_cross_asset_ddl.py` 与两 schema 仍 untracked。直接排跑=fetch 必败 + 哨兵假红（R-014/G1 同款地雷）。翻转=一行改 `weekend_calibration`/`daily_capital`。 |
| 2 | `lanes/altdataF_categories_yaml_fragment.yaml` | **未合并·交总包**。载体 `docs/03_modules/_cross_layer/database/business_data_categories.yaml` 在战役"全员禁写"清单（COORDINATION_LEDGER §2），本车道任务书亦列禁写。已回写 ledger 待裁表（req_dag_01）。注：`TableRegistry.table()` 对未登记品类 KeyError fail-closed，altdataF 已内置同值回退表，故不阻塞其代码。 |
| 3 | `lanes/instL_tasks_yaml_fragment.yaml`（adj_factor 复权因子日更） | **文件不存在**（`ls`/`find` 实测无此片段）。替代事实：`tasks.yaml` 既有 `adj_factor_incremental`（`schedule: daily_kline`，source miniqmt，fallback akshare）且已是 3 件 hfq 任务的前置。分包12 T1 复权链的供水腿**在册**；若 instL 要新增/改档期，需其重出片段（登记 req_dag_02）。 |
| 4 | `lanes/minelineI_tasks_yaml_fragment.yaml`（quality_sentinel L11 槽位） | **文件不存在**（同上实测）。既有真源：`schedule.yaml` L11 `integrity_check`（`00 23 * * 0-4`）与 L13 `data_supply_sentinel`（`50 6 * * *`）均在册；`src/zephyr/data/quality_sentinel.py` 存在但**无任务条目**。已登记 req_dag_02 待其重出片段。 |
| 5 | residual T1 接线批（`cohort_ledger_daily` + pipeline_events 月频演练挂载） | ①`cohort_ledger_daily` **已合并**：`table: c1_backtest.cohort_daily_ledger`（真源 `schemas/categories/cohort_daily_ledger.py`，非本车道臆造）、`dependencies` 四腿按交接令原文、`extra.module: zephyr.alt_data.cohort_daily_ledger`；`schedule: disabled` + `extra.disabled: true` + 原因=该模块 `git cat-file -e HEAD:` 实测**不在 HEAD**（z-land 在飞、且其为纯计算件自身禁写库）。四腿任务 id 逐个实测在册。**未因此阻塞其余任务**（其余全部照常落地）。②`pipeline_events` 月频 `--due` 挂载**未做**：载体 `src/zephyr/strategy_pipeline/pipeline_events.py` 按任务书不在独占范围（z-land/pf_alloc 在改）→ 只登记需求（req_dag_03），未动文件。 |
| 6 | req_tdchainJ_03 `kline_index_intraday` 采集任务 | **已合并采集条目** `kline_index_intraday_incremental`（`schedule: disabled` + 原因=DDL 未落、表实测不在 system.tables；规格指针 `lanes/tdchainJ_kline_index_intraday_spec.md`）。建表需求已回写 ledger 待裁表交总包（`scripts/ch/apply_market_tables_ddl.py` 归总包，本车道未改）。新表落地批须同批加 `data_supply_sentinel.yaml` 阈值行 + 品类 YAML（已写进该任务 disabled_reason）。 |

## 7. 未达成 / 遗留（如实）

1. BRK-050 **未闭合到 0**：226 件仍无 `dependencies`。已论证其中多数是"真无上游"，但也承认
   实现码参数化读表导致可机检血缘面受限——**扩面依赖表级血缘登记（§1 治本后续）**，非本车道可自闭。
2. 哨兵实跑 breach 未测（§5）。
3. 推导器无独立 pytest 钉（家族同类件 `scripts/data/run_nightly_sentiment.py` 亦为"手动触发 + --help 自测"，
   本件自测=双次 `--apply` 幂等实测 + 环保护实跑拦截 3 条）。
4. 片段 4 的两件（instL adj_factor 日更、minelineI quality_sentinel L11）因**片段文件不存在**而未合，
   不是"选择不合"。

## 8. 落地状态与本车道遗留（收尾回写）

- 提交：入队 `q-20260918-st-ff-dag-20260918-0002`（11 件，含 tasks.yaml/schedule.yaml/推导器/两份登记册 token 与翻译）。
  前一笔 `...-0001` 已 dead：死因=prestage 拒收被 `.gitignore` 忽略的 force-add 路径，**非本批内容问题**；
  按门禁处方把推导器从 `scripts/data/` 移到 `scripts/` 根后重投（`scripts/data/*` 是再生产物区，
  豁免行属 PROTECTED-PATHS 须 ARCH-MODEL-LIFECYCLE-001 审批 → 已登记 req_dag_01 A5，请总包补豁免/或确认落点）。
- 遗留脏件（本车道制造，请后续批顺手清）：`capability_canonical_file_registry.yaml` 内
  `scripts/data/derive_task_dependencies.py` 那条 creation_token 已成孤儿（文件已移走），
  depgraph 亦留有该旧路径设计态节点 node_id=14830699（新路径节点 node_id=14830701）。
- 六向⑤未闭环项：`c1_market.execution_report` 哨兵阈值行已加，但**实跑 breach 数未取**（轮数预算），
  复核命令：`python -m zephyr.data sentinel`（或等 L13 `data_supply_sentinel` 06:50 自动跑）。
- 幂等实证：`python scripts/derive_task_dependencies.py --apply` 二次跑 = `tasks_touched: 0`，
  计数稳定 `266 226`（基线 `262 235`）。

<!-- gov2-hook-smoke 2026-09-18 st-ff-gov2-20260918：本行是 post-commit/reference-transaction 两个 guard 的真实端到端冒烟占位行（无内容语义，可在下次文档整理时删除） -->
