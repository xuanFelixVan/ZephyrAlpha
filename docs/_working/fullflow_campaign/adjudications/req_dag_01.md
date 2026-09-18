---
ttl: task_bound
completes_when: 总包对四件跨车道受阻项出裁定并由归属车道落地
---

# req_dag_01 · 排班车道（st-ff-dag-20260918）四件跨权登记

> 单一写者制下本车道只落地自己有权的部分；以下四件**载体不在本车道独占范围**，按 R-010②/§4 协议登记交总包，未停等。

## A1 altdataF 品类条目未并入（阻塞其 registry 正门）

- 片段：`docs/_working/fullflow_campaign/lanes/altdataF_categories_yaml_fragment.yaml`（2 条：
  `market_cftc_positioning` / `market_gold_etf_holdings`）。
- 载体：`docs/03_modules/_cross_layer/database/business_data_categories.yaml` —— 战役"全员禁写"
  （COORDINATION_LEDGER §2）+ 本车道任务书禁越界同列。
- 影响：`TableRegistry.table(category_id)` 对未登记品类 KeyError fail-closed
  （`src/zephyr/data/table_registry.py:145`）。altdataF 已内置同值回退表 `_PENDING_CATEGORY_TABLES`
  保运行，**但真源仍是 YAML**——不并即长期双口径（违 RULE-SSOT）。
- 建议：总包并入（纯 append 两条），随后 altdataF 批次删除回退表或保留为 fail-safe（其片段已注明同值无害）。

## A2 两件片段文件不存在（非"选择不合"）

- `docs/_working/fullflow_campaign/lanes/instL_tasks_yaml_fragment.yaml`（adj_factor 复权因子日更任务）
- `docs/_working/fullflow_campaign/lanes/minelineI_tasks_yaml_fragment.yaml`（quality_sentinel L11 槽位）
- 实测：`ls`/`find docs/_working -name "*fragment*"` 只命中 altdataF 两件；上述两件文件不存在。
- 现状核对：`tasks.yaml` 已有 `adj_factor_incremental`（daily_kline / miniqmt / fallback akshare），
  且已是 3 件 hfq 任务的前置（本次推导器又补 1 件）；`schedule.yaml` L11 `integrity_check`、
  L13 `data_supply_sentinel` 均在册；`src/zephyr/data/quality_sentinel.py` 存在但 tasks.yaml 无任务条目。
- 建议：请总包催 instL/minelineI 重出片段（含 table/capability/档期/module 四要素），本车道随时可合。

## A3 pipeline_events 月频演练 `--due` 挂载（载体属 z-land/pf_alloc 在改）

- 需求：residual T1 批要求 `pipeline_events` 月频演练挂 `--due`（`MONTHLY_DAYS=30` marker 先例，
  或 monthly 触发读 `tmp/crisis_drill_last.json`）。
- 载体：`src/zephyr/strategy_pipeline/pipeline_events.py` —— 本车道任务书明列"不在独占范围，需改时只登记"。
- 建议：转 z-land/pf_alloc 侧落地；若需新增月频档期，本车道可在 `schedule.yaml` 补槽位
  （现有 `monthly_static` 16 9 1 * 可复用，或新授 `monthly_drill`），等裁定。

## A4 kline_index_intraday 建表（req_tdchainJ_03 已批，DDL 归总包）

- 采集条目本车道已落：`tasks.yaml` 新增 `kline_index_intraday_incremental`
  （`schedule: disabled` + `disabled_reason` 标注翻转前置，避免"在册即跑→写不存在的表"）。
- 缺件：`scripts/ch/apply_market_tables_ddl.py`（总包独占）加 `c1_market.kline_index_intraday` DDL；
  品类 YAML 须同批（TABLE-NAME-REGISTRY 导入期 fail-closed）；新表须同批加哨兵阈值行（六向⑤）。
- 规格真源：`docs/_working/fullflow_campaign/lanes/tdchainJ_kline_index_intraday_spec.md`（§2 DDL 全文）。

## A5 附带发现的机制性地雷（登记不代修）

1. `.gitignore:603` 的 `scripts/data/*` 会把**新建在该目录的永久工具静默排除入库**
   （`git ls-files --others` 不报、`git status` 不报、token 工具因此判"无待登记文件"）。
   本车道按在册先例补 `!scripts/derive_task_dependencies.py` 豁免收编。
   → 本车道处置：PROTECTED-PATHS 门禁判 .gitignore 修改须走 ARCH-MODEL-LIFECYCLE-001 审批（无 CLI 逃生旗），
     故**未提交豁免行**，改以 git add -f 收编推导器（tracked 文件不受 ignore 规则影响）。
     请总包按审批流程补 !scripts/derive_task_dependencies.py 豁免行，使收编 durable；
     并建议加门禁"新 .py 落被 ignore 目录须显式豁免或改落点"（否则同类文件长期脱管）。
2. `dataflow_edges`（90）/`dataflow_datasets`（76）实测全 `design` 态且 dataset 为契约级命名，
   **无法用作任务级表血缘真源**（与普查 BRK-058/059/061 同源）。BRK-050 的彻底闭合依赖表级血缘登记，
   已写进 `lanes/dag_relay.md` §1 治本后续。
