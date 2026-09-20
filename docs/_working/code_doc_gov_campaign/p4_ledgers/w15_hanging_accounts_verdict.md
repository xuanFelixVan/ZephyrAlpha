---
ttl: task_bound
session: st-code-doc-20260921
---

# WO-15 历史悬账验活台账（D1-D4 判活判死，只读分包）

> 执行：丙·分包4 st-code-doc-20260921（验活只读——判活判死+写台账，处置动作一律未执行，交总包统一处置）。
> 执行日：2026-09-21。原则："报告是死的库是活的"——全部结论以执行日实测为准。
> 证据标签：[亲验]=本会话实跑命令/查询；[推断]=据域与行为推断；[转报]=引用他人报告。
> 环境基线：Python 3.12.8 [亲验]；活跃会话实测仅 st-disk-ch-20260921（他会话，乙线）+本会话 [亲验]（任务书提示的 st-tilib-clear 已不活跃）。

## 总览

| 分件 | 任务书前提 | 执行日实测 | 判定 |
|---|---|---|---|
| D1 | staged 约 175 件 | 实测 **178** 件（167 A + 11 M；会话中段他会话新增 1 件） | 避让 3 / B 7 / C 168 / A 0 |
| D2 | "42 行 pending（PG 查询）" | 台账真源=CH `c1_backtest.node_verdict`（非 PG），实测 **41** 行 pending | 已被取代 19 / 仍存活待复验 22 / 作废 0 |
| D3 | backlog 140 条 | `docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml` 实测 **142** 条（REG-BTB-001，generator 产） | 抽验 22 条全活（22/22）；全量 142 对账：活≈138、字段漂移 4、死 0 |
| D4 | allow_empty 白名单约 12 表 | 两哨兵均无 12 表在册：`quality_sentinel_tables.yaml` 无该机制；`data_supply_sentinel.yaml` 实测仅 **1** 表在册 | 前提已死（BRK-046 收口已落地 8a8a3f9290）；余 1 表判"仍应允许空" |

---

## D1 staged 178 件三态终态表

方法（逐条跑，无抽样）：

1. `git diff --cached --name-status` 快照 178 件 [亲验]（执行中他会话入暂存 1 件，第二次快照收编；本表=终态快照）。
2. A 类判定（暂存==HEAD）：对每件跑 `git diff --cached --quiet -- <path>` 退出码 + `git ls-files -s` vs `git ls-tree -r HEAD` blob 对比 → **0 件**命中 [亲验]。
3. B 类判定：每件 staged blob 对全部 62 个 ref tip 树（`for-each-ref`+`ls-tree -r`）求交 + `git log --all --find-object` 全史检索 [亲验]。
4. C 类=其余全史零命中件，按目录族定性（族代表件实读内容）[亲验]。

| # | 状态 | 路径 | 终态 | 依据/建议 |
|---|---|---|---|---|
| 1 | M | `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` | 避让 | 活跃会话 st-disk-ch-20260921 在途件（裁定#383 暂存稿自署乙线开工件）[亲验] |
| 2 | M | `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` | B | 暂存内容==master 分支 tip 同名件 [亲验]；dev 已有批9-4(7fbec92e89)更新版 → 过时副本，还原暂存不丢工作 |
| 3 | M | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md` | B | 暂存内容==master 分支 tip 同名件 [亲验]；dev 已有批9-4(7fbec92e89)更新版 → 过时副本，还原暂存不丢工作 |
| 4 | A | `docs/_working/ai_layer_vision/L1_perceive/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 5 | A | `docs/_working/ai_layer_vision/L2_intake_library/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 6 | A | `docs/_working/ai_layer_vision/L3_cleaning/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 7 | A | `docs/_working/ai_layer_vision/L4_compare/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 8 | A | `docs/_working/ai_layer_vision/L5_schedule_gate/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 9 | A | `docs/_working/ai_layer_vision/L6_ab_switch/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 10 | A | `docs/_working/ai_layer_vision/L7_heredity/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 11 | A | `docs/_working/ai_layer_vision/OBJ_M_models/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 12 | A | `docs/_working/ai_layer_vision/OBJ_R_rules_standards/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 13 | A | `docs/_working/ai_layer_vision/OBJ_S_perimeter/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 14 | A | `docs/_working/ai_layer_vision/OBJ_T_tools/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 15 | A | `docs/_working/ai_layer_vision/V0_layer_definition/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 16 | A | `docs/_working/ai_layer_vision/V1_three_layer_split/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 17 | A | `docs/_working/ai_layer_vision/V2_evolution_loop/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 18 | A | `docs/_working/ai_layer_vision/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 19 | A | `docs/_working/altdata_line/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜altdata 线索引 |
| 20 | A | `docs/_working/archive/2026-09/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜archive/2026-09 索引 |
| 21 | A | `docs/_working/automation/campaign/blueprints/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 22 | A | `docs/_working/automation/campaign/health/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 23 | A | `docs/_working/automation/campaign/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 24 | A | `docs/_working/automation/campaign/mining/01_数据源发现/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 25 | A | `docs/_working/automation/campaign/mining/02_原料入库/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 26 | A | `docs/_working/automation/campaign/mining/03_自动上架/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 27 | A | `docs/_working/automation/campaign/mining/04_洗数据/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 28 | A | `docs/_working/automation/campaign/mining/05_因子合成/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 29 | A | `docs/_working/automation/campaign/mining/06_策略合成/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 30 | A | `docs/_working/automation/campaign/mining/07_两级回测/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 31 | A | `docs/_working/automation/campaign/mining/08_模拟盘转正门/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 32 | A | `docs/_working/automation/campaign/mining/09_骨架体检/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 33 | A | `docs/_working/automation/campaign/mining/10_横向系统/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 34 | A | `docs/_working/automation/campaign/mining/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md（doc_type:index 生成器产物）+工段作业簿 |
| 35 | A | `docs/_working/automation/inbox/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交 |
| 36 | A | `docs/_working/automation/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交 |
| 37 | A | `docs/_working/bizmine_chain_mining/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜链式挖矿索引+骨架索引 |
| 38 | A | `docs/_working/bizmine_chain_mining/skeleton/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜链式挖矿索引+骨架索引 |
| 39 | A | `docs/_working/bizmine_night/algo_mining/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 40 | A | `docs/_working/bizmine_night/altdata_probes_b/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 41 | A | `docs/_working/bizmine_night/crypto_probe/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 42 | A | `docs/_working/bizmine_night/etf_family/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 43 | A | `docs/_working/bizmine_night/etf_t0_retest/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 44 | A | `docs/_working/bizmine_night/factor_sop_screen/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 45 | A | `docs/_working/bizmine_night/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 46 | A | `docs/_working/bizmine_night/indicators_sweep_a/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 47 | A | `docs/_working/bizmine_night/indicators_sweep_b/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 48 | A | `docs/_working/bizmine_night/indicators_sweep_c/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 49 | A | `docs/_working/bizmine_night/mid_valley/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 50 | A | `docs/_working/bizmine_night/pattern_backfill/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 51 | A | `docs/_working/bizmine_night/pattern_definition_audit/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 52 | A | `docs/_working/bizmine_night/pattern_events/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 53 | A | `docs/_working/bizmine_night/pattern_narrow_exam/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 54 | A | `docs/_working/bizmine_night/regime_axis/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 55 | A | `docs/_working/bizmine_night/sector_family/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 56 | A | `docs/_working/bizmine_night/sensors_b1/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 57 | A | `docs/_working/bizmine_night/t0_regime/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 58 | A | `docs/_working/bizmine_night/tick_matrix/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 59 | A | `docs/_working/bizmine_night/tick_t0/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 60 | A | `docs/_working/bizmine_night/volume_family_l1/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜目录索引 index.md 生成器产物 |
| 61 | A | `docs/_working/cold_backup_automation/00_master_plan.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜00 总体方案/01 挖掘发现（Owner 直属方案件） |
| 62 | A | `docs/_working/cold_backup_automation/01_mining_findings.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜00 总体方案/01 挖掘发现（Owner 直属方案件） |
| 63 | A | `docs/_working/cold_backup_automation/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜00 总体方案/01 挖掘发现（Owner 直属方案件） |
| 64 | A | `docs/_working/deep_review_full/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜深度评审分区索引（生成器产物） |
| 65 | A | `docs/_working/deep_review_full/p0_money_path/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜深度评审分区索引（生成器产物） |
| 66 | A | `docs/_working/deep_review_full/p1_decision_chain/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜深度评审分区索引（生成器产物） |
| 67 | A | `docs/_working/deep_review_full/p1_decision_chain/tdm_supplement/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜深度评审分区索引（生成器产物） |
| 68 | A | `docs/_working/deep_review_full/p2_infra/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜深度评审分区索引（生成器产物） |
| 69 | A | `docs/_working/disk_reorg_campaign/a0_master_order.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a0 收口总令/a2 集成简报（战役令件） |
| 70 | A | `docs/_working/disk_reorg_campaign/a2_max_integration_brief.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a0 收口总令/a2 集成简报（战役令件） |
| 71 | A | `docs/_working/disk_reorg_campaign/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a0 收口总令/a2 集成简报（战役令件） |
| 72 | A | `docs/_working/factory/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜工厂/strategy_cards/t_v2 索引 |
| 73 | A | `docs/_working/factory/strategy_cards/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜工厂/strategy_cards/t_v2 索引 |
| 74 | A | `docs/_working/factory/t_v2/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜工厂/strategy_cards/t_v2 索引 |
| 75 | A | `docs/_working/final3_campaign/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜p10 T0 机械波报告（裁定#371 实测报告）+索引 |
| 76 | A | `docs/_working/final3_campaign/p10_t0_mechanical_wave_report.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜p10 T0 机械波报告（裁定#371 实测报告）+索引 |
| 77 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0829.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 78 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0829.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 79 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0836.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 80 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0836.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 81 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0840.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 82 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0840.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 83 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0841.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 84 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0841.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 85 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0850.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 86 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0850.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 87 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0852.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 88 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0852.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 89 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0855.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 90 | A | `docs/_working/final3_campaign/p6_shed_salvage/ledgerp2a_pipeline_research_reports/intake-20260917-0855.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同上生成器 09-17 批的 p6 捡回件（14 件 md+yaml 成对） |
| 91 | A | `docs/_working/flash_speedup/F1_derived_commit_merge/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 92 | A | `docs/_working/flash_speedup/F2_prereq/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 93 | A | `docs/_working/flash_speedup/F3_head_gate_diff/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 94 | A | `docs/_working/flash_speedup/F4_generator_concurrency/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 95 | A | `docs/_working/flash_speedup/F5_dc_preflight/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 96 | A | `docs/_working/flash_speedup/F6_bottleneck/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 97 | A | `docs/_working/flash_speedup/F9_queue_newfile_deadletter/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 98 | A | `docs/_working/flash_speedup/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜F 系目录索引（生成器产物） |
| 99 | A | `docs/_working/full-auto-chain/S01_data_pipeline/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 100 | A | `docs/_working/full-auto-chain/S02_factor_discovery/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 101 | A | `docs/_working/full-auto-chain/S03_validation_certification/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 102 | A | `docs/_working/full-auto-chain/S04_hypothesis_intake/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 103 | A | `docs/_working/full-auto-chain/S05_strategy_construction/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 104 | A | `docs/_working/full-auto-chain/S06_backtest_exam/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 105 | A | `docs/_working/full-auto-chain/S07_registry_promotion/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 106 | A | `docs/_working/full-auto-chain/S08_sim_onboarding/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 107 | A | `docs/_working/full-auto-chain/S09_sim_operation/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 108 | A | `docs/_working/full-auto-chain/S10_sim_evaluation/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 109 | A | `docs/_working/full-auto-chain/S11_assembled_backtest/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 110 | A | `docs/_working/full-auto-chain/S11_assembled_backtest/nodes/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 111 | A | `docs/_working/full-auto-chain/S12_promotion_advisory/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 112 | A | `docs/_working/full-auto-chain/S13_frontend_approval/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 113 | A | `docs/_working/full-auto-chain/S14_live_qmt_bridge/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 114 | A | `docs/_working/full-auto-chain/S15_post_live_monitoring/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 115 | A | `docs/_working/full-auto-chain/evidence/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 116 | A | `docs/_working/full-auto-chain/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜S01-S15 目录索引+evidence（骨架导航，生成器产物） |
| 117 | A | `docs/_working/fullflow_campaign/adjudications/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 118 | A | `docs/_working/fullflow_campaign/delivery/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 119 | A | `docs/_working/fullflow_campaign/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 120 | A | `docs/_working/fullflow_campaign/lanes/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 121 | A | `docs/_working/fullflow_campaign/lanes/pit2_prescriptions.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 122 | A | `docs/_working/fullflow_campaign/recovered/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 123 | A | `docs/_working/fullflow_campaign/skeleton/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 124 | A | `docs/_working/fullflow_campaign/stages/FF-12_recon_feedback/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 125 | A | `docs/_working/fullflow_campaign/stages/FF-16_delivery_channel/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 126 | A | `docs/_working/fullflow_campaign/stages/_verifier/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 127 | A | `docs/_working/fullflow_campaign/stages/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 128 | A | `docs/_working/fullflow_campaign/verification/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜车道/阶段索引+pit2 处方移交案卷（战役交付件） |
| 129 | A | `docs/_working/guides/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜guides 索引 |
| 130 | A | `docs/_working/kimi_audit/adjudications/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 131 | A | `docs/_working/kimi_audit/exp_evidence/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 132 | A | `docs/_working/kimi_audit/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 133 | A | `docs/_working/kimi_audit/lane_reports/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 134 | A | `docs/_working/kimi_audit/lane_reports/p3_prereg/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 135 | A | `docs/_working/kimi_audit/nightbuild/e2e/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 136 | A | `docs/_working/kimi_audit/nightbuild/e4/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 137 | A | `docs/_working/kimi_audit/nightbuild/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 138 | A | `docs/_working/kimi_audit/redblue_git/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜审计车道索引+夜构建索引（战役交付件） |
| 139 | A | `docs/_working/pattern_line/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜模式线索引 |
| 140 | A | `docs/_working/pipeline-research/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 141 | A | `docs/_working/pipeline-research/reports/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 142 | A | `docs/_working/pipeline-research/reports/intake-20260918-2139.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 143 | A | `docs/_working/pipeline-research/reports/intake-20260918-2139.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 144 | A | `docs/_working/pipeline-research/reports/intake-20260918-2207.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 145 | A | `docs/_working/pipeline-research/reports/intake-20260918-2207.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 146 | A | `docs/_working/pipeline-research/reports/intake-20260918-2233.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 147 | A | `docs/_working/pipeline-research/reports/intake-20260918-2233.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 148 | A | `docs/_working/pipeline-research/reports/intake-20260919-0011.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 149 | A | `docs/_working/pipeline-research/reports/intake-20260919-0011.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 150 | A | `docs/_working/pipeline-research/reports/intake-20260919-0036.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 151 | A | `docs/_working/pipeline-research/reports/intake-20260919-0036.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 152 | A | `docs/_working/pipeline-research/reports/intake-20260919-0110.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 153 | A | `docs/_working/pipeline-research/reports/intake-20260919-0110.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 154 | A | `docs/_working/pipeline-research/reports/intake-20260919-0124.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 155 | A | `docs/_working/pipeline-research/reports/intake-20260919-0124.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 156 | A | `docs/_working/pipeline-research/reports/intake-20260920-0408.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 157 | A | `docs/_working/pipeline-research/reports/intake-20260920-0408.yaml` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 158 | A | `docs/_working/pipeline-research/sim-memos/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 159 | A | `docs/_working/pipeline-research/sim-memos/sim-memo-202609.json` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜C6 auto_intake 批报告（09-18~09-20 MOD-BT-189）生成器产物，新鲜 |
| 160 | A | `docs/_working/resource_schedule/e2e_evidence/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜资源调度索引+晨报/e2e 证据索引 |
| 161 | A | `docs/_working/resource_schedule/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜资源调度索引+晨报/e2e 证据索引 |
| 162 | A | `docs/_working/resource_schedule/morning_report/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜资源调度索引+晨报/e2e 证据索引 |
| 163 | A | `docs/_working/reviews/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜reviews 索引 |
| 164 | A | `docs/_working/rule_audit_campaign/a2_handoff/A2_M5_prescriptions.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a2_handoff repoint 补丁/行清单+索引（交接件） |
| 165 | A | `docs/_working/rule_audit_campaign/a2_handoff/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a2_handoff repoint 补丁/行清单+索引（交接件） |
| 166 | A | `docs/_working/rule_audit_campaign/a2_handoff/rules_m1_repoint.patch` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a2_handoff repoint 补丁/行清单+索引（交接件） |
| 167 | A | `docs/_working/rule_audit_campaign/a2_handoff/rules_repoint_rows.json` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a2_handoff repoint 补丁/行清单+索引（交接件） |
| 168 | A | `docs/_working/rule_audit_campaign/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜a2_handoff repoint 补丁/行清单+索引（交接件） |
| 169 | A | `docs/_working/trading_vision/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜trading_vision 索引（判定台账标准所在目录） |
| 170 | M | `docs/_working/unified_campaign/p2_backlog_master_ledger_v1_0.md` | C | 全史无同内容 [亲验]；总包工单台账编辑（D1 行改 175 件），留暂存随总包正门批提交 |
| 171 | A | `docs/_working/同花顺资料/index.md` | C | A 类逐条核验：git diff --cached --quiet 非零（≠HEAD）+ blob 全 ref tip/全史零命中 [亲验] → 真未落地，评估入册：留暂存待提交｜同花顺资料索引 |
| 172 | M | `schemas/categories/market/market_technical_indicator.py` | B | 暂存内容==master 分支 tip 同名件 [亲验]；dev 已有批9-4(7fbec92e89)更新版 → 过时副本，还原暂存不丢工作 |
| 173 | M | `scripts/governance/meta/rules_integrity_db.json` | B | 暂存=历史中间版，已被后继 reconciler 提交 0bbcc6b1ca 覆盖 [亲验] → 过时副本，还原暂存不丢工作 |
| 174 | M | `src/zephyr/data/storage_tiering.py` | 避让 | 活跃会话 st-disk-ch-20260921 在途件（裁定#383 暂存稿自署乙线开工件）[亲验] |
| 175 | M | `src/zephyr/factor/technical_indicators/cycle.py` | B | 暂存内容==master 分支 tip 同名件 [亲验]；dev 已有批9-4(7fbec92e89)更新版 → 过时副本，还原暂存不丢工作 |
| 176 | M | `tests/zephyr/data/test_prevention_bells_20260914.py` | 避让 | 会话中段新入暂存+数据线域，推断属乙线在途 [推断] |
| 177 | M | `tests/zephyr/factor/technical_indicators/test_cycle.py` | B | 暂存内容==master 分支 tip 同名件 [亲验]；dev 已有批9-4(7fbec92e89)更新版 → 过时副本，还原暂存不丢工作 |
| 178 | M | `tests/zephyr/factor/technical_indicators/test_indicator_base.py` | B | 暂存内容==master 分支 tip 同名件 [亲验]；dev 已有批9-4(7fbec92e89)更新版 → 过时副本，还原暂存不丢工作 |

D1 族定性小结（C 类 168 件去向建议）：

- **167 件新文件**全部位于 `docs/_working/**`（战役交付文档/目录索引生成器产物，日期 2026-09-16~09-20，无陈旧作废对象），建议=**留暂存待提交**（由总包经 git_commit.py 正门批量落地，禁散落直提）。
- **1 件 M**（p2_backlog_master_ledger_v1_0.md）=总包工单台账本尊编辑，随总包本批提交。
- **B 类 7 件均为"过时副本"**：还原暂存不丢失任何未落地工作；但工作区当前内容≠暂存内容（tilib 6 件工作区已持 dev 批9-4 版），**处置只能动暂存区、禁触碰工作区**（交总包）。
- **避让 3 件**属活跃乙线 st-disk-ch-20260921（裁定#383 退役判决 + storage_tiering 退役注记 + 数据线测试件），不判不动。

---

## D2 判定台账 41 行 pending 逐行判定表

真源更正：任务书"PG 查询/forecast_ledger 体系"系前提误标——全仓无 forecast_ledger 命名实体 [亲验]；唯一 PG（depgraph，pg_database 仅 depgraph/postgres）无 forecast/judgment/node_backtest 台账表 [亲验]；判定台账真源=**CH `c1_backtest.node_verdict`**（DDL 真源 schemas/categories/backtest/backtest_node_verdict.py，写入方 src/zephyr/trading/validation/runner.py）[亲验]。

pending 语义（runner.py 判定链）：pending=「验过但证据不足不下结论」的如实披露（触发<30 样本土规 PB-13 / 对照未建 / 参考价缺失），**不是欠账队列**；台账只追加不删改（铁律）。

实测：58 行 = 41 pending + 17 valid [亲验]（工单记 42，库是活的）。全部 41 行 window_end∈{09-10(38), 09-11(3)}，37 个节点全部 TDM 族且仍存在于现行 config/trading_decision_map.yaml（138 个 TDM id 全查）[亲验]。

| # | node_id | run | ingest_ts | verdict_reason | 判定 | 依据 |
|---|---|---|---|---|---|---|
| 1 | TDM-E-L1-AGG | VAL-P0-20260912-163755-002 | 2026-09-12 08:37:56 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 2 | TDM-E-L1-AGG | VAL-P0-20260912-164116-002 | 2026-09-12 08:41:18 | discrimination_below_threshold | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 3 | TDM-E-L1-AGG | VAL-P0-20260914-001859-002 | 2026-09-13 16:19:00 | discrimination_below_threshold | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 4 | TDM-E-L4 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 5 | TDM-E-L4-01 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 6 | TDM-E-L4-02 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 7 | TDM-E-L4-03 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 8 | TDM-E-L4-04 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 9 | TDM-E-L4-05 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 10 | TDM-E-L4-06 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 11 | TDM-E-L4-07 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 12 | TDM-E-L4-08 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 13 | TDM-E-L4-09 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 14 | TDM-E-L4-09 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 15 | TDM-E-L4-10 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 16 | TDM-E-L4-11 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 17 | TDM-E-L4-12 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 18 | TDM-E-L4-13 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 19 | TDM-E-L4-14 | VAL-20260912-070605 | 2026-09-11 23:06:10 | insufficient_samples | 已被取代-作废 | 同节点后继 valid 行（verdict_at 晚于本行 ingest）[亲验]；台账只追加，无需任何处置 |
| 20 | TDM-P-P2-01 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 21 | TDM-P-P2-03 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 22 | TDM-X-FLOW | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 23 | TDM-X-R1 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 24 | TDM-X-R1-01 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 25 | TDM-X-R1-02 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 26 | TDM-X-R1-03 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 27 | TDM-X-S1 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 28 | TDM-X-S1-01 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 29 | TDM-X-S1-02 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 30 | TDM-X-S1-03 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 31 | TDM-X-S1-04 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 32 | TDM-X-S1-05 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 33 | TDM-X-S1-06 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 34 | TDM-X-S2 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 35 | TDM-X-S2-01 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 36 | TDM-X-S2-01 | VAL-P0-20260912-170843-003 | 2026-09-12 09:08:48 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 37 | TDM-X-S2-02 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 38 | TDM-X-S2-03 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 39 | TDM-X-S2-04 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 40 | TDM-X-S2-05 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |
| 41 | TDM-X-S2-06 | VAL-20260912-070622 | 2026-09-11 23:06:27 | insufficient_samples | 仍存活待复验 | insufficient_samples（触发<30 土规）如实披露；节点在现行地图；待下个验证批次复验，非欠账 [亲验] |

D2 判定分布：**已被取代 19**（TDM-E-L1-AGG + TDM-E-L4 族 16 行，被 09-14/09-18 valid 重验覆盖）**/ 仍存活待复验 22**（TDM-P-P2×2、TDM-X-FLOW×1、TDM-X-R1 族×4、TDM-X-S1 族×7、TDM-X-S2 族×8 含 TDM-E-L4-09 旧行）**/ 已过期作废 0**。

建议（不在本包执行）：①19 行被取代件无需动作（只追加台账语义下自然失效）；②22 行=下游消融器/样本量前置未就绪的方法学状态，不应硬"结算"，应在下次验证批次（SOP-A 车道）按土规重跑覆盖；③工单前提更正：D2 真源指针应改指 CH c1_backtest.node_verdict。

---

## D3 backlog 142 条抽验表（抽 22 条，覆盖 P0 全量+P1/P2/P3 分层首中尾）

真源：`docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml`（REG-BTB-001，generator=scripts/backtest/generate_backtest_backlog.py，generated_at 2026-09-12）[亲验]；实测 **142** 条（工单记 140，库是活的）：P0×3/P1×32/P2×56/P3×51；confidence 分布 untested×123/valid×16/pending×2/verified×1；testable=False×22（阈值未预注册禁跑=护栏③状态，非死条目）[亲验]。

| object_id | node_ids | confidence | 判活 | 证据 |
|---|---|---|---|---|
| BT-P0-001 | TDM-E-L1 | untested | 活 | TDM-E-L1 在地图+台账有 valid 行 [亲验]；backlog conf=untested 滞后（valid 判定 09-12 16:38 晚于台账生成 06:56） |
| BT-P0-002 | TDM-E-L1-AGG | untested | 活 | TDM-E-L1-AGG 在地图+台账 pending/valid 行 [亲验]；conf 字段滞后同上 |
| BT-P0-003 | TDM-E-L4-09,TDM-P-P2-01,TDM-P-P2-03,TDM-X-S2-01 | pending | 活 | 4 节点全在地图，台账 pending+valid 行混杂，conf=pending 相符 [亲验] |
| BT-P1-004 | TDM-E-L1-S4 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P1-008 | TDM-E-L2-01 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P1-012 | TDM-E-L2-01-4 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P1-016 | TDM-E-L3-03-1 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P1-020 | TDM-E-L3-05 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P1-024 | TDM-E-L3-07-2 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P1-028 | TDM-E-L4-02 | valid | 活 | TDM-E-L4-02 在地图，conf=valid 与台账相符 [亲验] |
| BT-P1-029 | TDM-E-FLOW | untested | 活 | TDM-E-FLOW 在现行地图 [亲验]；无台账行，confidence=untested 相符 |
| BT-P2-009 | TDM-E-L2-02-1 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P2-018 | TDM-E-L2-05-2 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P2-027 | TDM-E-L2-09-1 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P2-036 | TDM-E-L3-11-2 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P2-045 | TDM-E-L4-05 | valid | 活 | TDM-E-L4-05 在地图，conf=valid 与台账相符 [亲验] |
| BT-P2-054 | TDM-E-FLOW | untested | 活 | TDM-E-FLOW 在现行地图 [亲验]（台账尾件） |
| BT-P3-001 | TDM-P-FLOW | untested | 活 | TDM-P-FLOW 在现行地图 [亲验] |
| BT-P3-011 | TDM-P-P1-05 | untested | 活 | 1/1 节点在现行地图 [亲验]，verdicts=无 |
| BT-P3-021 | TDM-X-R1 | untested | 活 | TDM-X-R1 在地图，台账 pending（insufficient_samples）相符 [亲验] |
| BT-P3-031 | TDM-X-S2-02 | untested | 活 | TDM-X-S2-02 在地图，台账 pending 相符 [亲验] |
| BT-P3-041 | TDM-F-C2-03 | untested | 活 | TDM-F-C2-03 在现行地图 [亲验] |

全量对账补充（142 条全体非抽样检查）[亲验]：

- 全部 142 条的 node_ids 引用 100% 可在现行 trading_decision_map.yaml 解析（抽验 22 条 22/22 节点级命中）；**死条目（节点已删/被裁定取代）0 条**。
- 19 条非 untested confidence 中 **15 条与台账相符**，**4 条字段漂移**：BT-P1-001(valid)/BT-P1-005(pending)/BT-P1-006(valid) 声称的节点 TDM-E-L1-S1/S0/S0-1 在图但 node_verdict 零行；BT-P1-032(verified) node_ids 为空（L5 执行件=t_v2 战役特殊条目）。→ 判"活但字段存疑"，建议总包转 backlog 再生成批次核对 confidence 溯源（防挪门柱语义）。
- **整体活死比估计：活 ≈138/142（97%）**，死 0，字段漂移 4（≈3%）。台账体系本身健康，无"对象已删仍挂账"悬账。

---

## D4 allow_empty 白名单收口建议表（只读，不动哨兵真源）

前提更正 [亲验]：`config/quality_sentinel_tables.yaml`（四变异哨兵）**无 allow_empty 机制**（epoch/tz_shift/empty_segment/non_trading_day 四轴，无空表白名单键）；"12 表 allow_empty 白名单"真源=`src/zephyr/data/config/data_supply_sentinel.yaml`（供数哨兵）。且 BRK-046 的 12 表收口**已经落地**——commit 8a8a3f9290（[FLOWTHROUGH][FF-16] 假通道收口车道 BRK-049/047/048/046…哨兵白名单收口）[亲验 git log]。

执行日实测在册 allow_empty：**1 张**（12→1，11 张已由 FF-16 车道撤豁免）。

| 表 | 实测状态（CH reader） | 建议 | 依据 |
|---|---|---|---|
| c1_market.market_convertible_bond_clause | 315 行 / distinct(snapshot_date)=1 / max=2026-09-18 [亲验] | **仍应允许空**（维持豁免） | 事件驱动低频供数=设计意图豁免（rationale_zh+reviewed_at 2026-09-18+reviewed_by 凭据齐全 [亲验]）；若后续接逐日全量刷新任务应撤销（文件内已自书该退出条件） |
| （其余 11 张原白名单表） | 已不在册（FF-16 收口撤豁免） | 无需再收口 | commit 8a8a3f9290 [转报 commit message]；哨兵真源属数据线 WO-3 域，本包未改任何哨兵文件 |

补充：判定链四表（judgment_plan_verification 等）**未加 allow_empty 是正确现状**——0 行报红=真信号（T2/T3 段产线从未落验证行），撤红路径=补产出而非豁免（与 FF-12 车道 09-18 判读一致 [转报 judgment_sentinel_yaml_fragment.yaml 实测账]）。

---

## 停手项与原因

1. D1 避让 3 件：活跃他会话乙线 st-disk-ch-20260921 在途件，判归属会与其提交流产生竞态——不判不动。
2. D2 的"结算"未执行：22 行待复验的前置（样本量/消融器）属验证车道域，本包只读。
3. D4 哨兵文件零改动：真源属数据线 WO-3 域；且收口已由 FF-16 落地，无剩余动作可做。
4. 台账计数漂移（178/41/142/1 vs 工单 175/42/140/12）均为"库是活的"正常演化，已在总览表逐项标明，无死磕项。

## 本包 stage 清单

- docs/_working/code_doc_gov_campaign/p4_ledgers/w15_hanging_accounts_verdict.md（本件，git add 未 commit，提交由总包统一走正门）

