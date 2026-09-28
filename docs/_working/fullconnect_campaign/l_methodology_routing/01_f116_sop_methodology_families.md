---
ttl: task_bound
title: L12 案卷 F116 — SOP 方法论族（11 族 48 md 真源地图接线四态）
session: zc-l12-20260927
---

# F116 SOP 方法论族（M 段横切 X1，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 无上游环节（方法论真源=条目自足）；M0 76 环节册 X1 行"总筹引用，禁重挖"（`00_skeleton_fullflow.md:114`）；SOP README 头注"新 AI 入职第二读（第一读=AGENTS.md 冷启动）" |
| 下游消费 | 全链 122 环节的施工判据输入：宪法 §6.2 检索序"capability_cards → rules/*.yaml → … → sop/README.md（九族索引）"；capability_lookup 与 rule_catalog_registry 双通道冗余可达（README 使用纪律 3） |
| 自动化触发 | 非运行件，零调度——触发形态=会话冷启动/任务开工前人（AI）读（README"何时必读"列逐族列明）；`.trae PRE-OP` 行强制 mining 族开工前必读 |
| 真源与注册表 | `docs/01_policies_and_standards/sop/README.md`（module_id=SOP-INDEX-001，v1.6.0，status=active）；ROOR 内 rule_catalog_registry（PS-REG-018，机生）为发现通道 |
| 门禁与质量尺 | 新 SOP 入驻=N-11 命名闸（`*_policy.md`）+creation_token；族内唯一真源纪律（README 纪律 1）；"条目计数勿写死（只述族与功能）"（README 纪律 3） |
| 当前运行状态 | **绿（built）**：48 md 全部在盘、11 族目录齐、README v1.6.0 与 2026-09-14 七族重分类/2026-09-24 library 补登注记在文 |

## 二、子模块三级枚举（11 族 ×48 md 全清单，find 实测）

族级（11 目录）→ 文件级（45 md）→ 根层（3 md）：

1. `governance_sop/`（7）：agent_constitution_l0 / agent_constitution_legacy_v1 / alignment_checklist / commit_navigation_playbook / construction_ledger_method_policy / deep_adjudication_method_policy / index
2. `backtest_system_sop/`（7）：exam_policy / index / README / sop_a_full_map_orchestration / sop_b_node_loop / sop_c_strategy_library_intake / sop_d_run_archive_naming
3. `construction_sop/`（5）：construction_workflow_policy / document_review_and_optimization_policy / frontend_component_split_policy / index / lane_construction_discipline_policy
4. `mining_sop/`（6）：factor_mining_sop_policy / index / indicator_mining_sop_policy / mining_sop_policy / skeleton_mining_policy / trading_decision_map_pathfinding_policy
5. `review_sop/`（4）：deep_review_policy / defect_pattern_checklist / index / rule_disposition_policy
6. `ops_sop/`（4）：emergency_runbook / index / merge_conflict_resolution_policy / worktree_cleanup_policy
7. `trading_decision_map_sop/`（3）：index / tdm_consumption_policy / trading_decision_map_layering_policy
8. `data_ops_sop/`（3）：data_ops_policy / data_source_onboarding_sop / index
9. `automation_sop/`（2）：automation_crew_policy / index
10. `data_audit_sop/`（2）：index / industry_chain_data_audit_policy
11. `library_sop/`（2）：blood_flesh_cataloging_sop / index
根层（3）：`README.md`（SOP-INDEX-001 人写导航）+ `audit_prompts_20_ai.md`（AI-00 总控+AI-01~22 域差异表，禁改名/禁挪路径）+ `index.md`（generate_missing_index_md.py 机生 2026-09-19）

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| 11 族目录+45 族内 md | **已接线（built）** | 本日 find 全数在盘；README"两班导航"给出治理班 6 族/业务班 4 族入口映射 |
| README（SOP-INDEX-001） | **已接线** | v1.6.0 active；library_sop"2026-09-24 补登，此前未入索引"注记在文——补登闭环 |
| 根 audit_prompts_20_ai.md | **已接线（只读保护态）** | README 载明"修改走 attrib -r → claim → Gateway 提交 → 复位；旧 skip-worktree 声明实测已失效" |
| 根 index.md（机生） | **半接线（滞后嫌疑）** | 机生日期 2026-09-19，早于 library_sop 补登（09-24）与 v1.6.0——机生索引面可能落后于人写 README（未逐行 diff，见缺口 2） |

## 骨架勘误

1. **族数口径三值漂移**：总册 F116 行写"12 目录实测"但同格括注只列 **11** 个目录名；M0 X1 行写"SOP 方法论 12 族"；AGENTS.md §6 写"九族索引"；README 实际声明 **11 个族文件夹**。本日实测=11 族，"12 目录/12 族"为骨架侧笔误（可能把根层 README+index 计入）。建议总册 F116 行改"11 族（README SOP-INDEX-001 为准，计数勿写死）"。
2. 总册 F116 行把 trading_decision_map 族与"九族"并称（"九族…+TDM 族"=10），与 README 11 族分法（data_audit/review/library 各自成族）不一致——以 README 为准。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 族数口径漂移（12 vs 11 vs 九族）散布总册/M0/AGENTS 三处 | 按勘误 1 统一为"11 族，以 README 为准"；AGENTS.md 引用锚不动（其"九族"指 README 段落名） | P2 |
| 2 | 根 index.md 机生滞后（09-19）vs README v1.6.0（09-24 后） | 重跑 generate_missing_index_md.py 刷新机生索引 | P2 |
| 3 | 各族 index.md 是否与族内容同步未逐一核 | 并入机生索引重跑一并闭合 | P2 |

## 五、自审闸三态

**挖干（本环节方法论面）**：48 md 清单逐文件枚举 ✅ README 锚点实证 ✅；**待裁**：无（本环节无 Owner 门位事项；勘误 1 属文档对齐，走对齐清单通道）。

## 六、复跑命令

```bash
find docs/01_policies_and_standards/sop -name "*.md" | wc -l            # =48
find docs/01_policies_and_standards/sop -mindepth 1 -maxdepth 1 -type d | wc -l  # =11
head -12 docs/01_policies_and_standards/sop/README.md                    # SOP-INDEX-001 v1.6.0
grep -c "policy.md" docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml  # 发现通道在
```
