---
ttl: task_bound
title: W4-3 三门禁缺口立项登记（净零并族）+排班一致性销项
owner: st-final3-20260919
created: 2026-09-19
---

# W4-3 三门禁缺口立项登记（净零并族）

- 日期：2026-09-19｜会话：st-final3-20260919｜性质：**立项登记件——只登记不施工 gate 代码**
- 净零纪律（宪法 §4.1）：新增参数面必须声明并入的既有 gate 族/被替代的旧条目，本件三缺口零新 gate_id

## 0. 三缺口总览

| # | 缺口 | 状态 | 净零方案一句话 |
|---|---|---|---|
| ① | 链活性卡（IG-CHAIN-LIVENESS 判据） | 立项 | 并 graph_quality_check 合格线 S 族（新增 S27 参数面）+ gate141 备选臂 + 入库口共享谓词，零新 gate |
| ② | 新全景图准入挂 ROOR | 立项 | 扩 NEW-FILE-DEPGRAPH-ENFORCEMENT 第二臂 + check_registry_consistency 共享谓词，零新 gate、零解析重复 |
| ③ | 排班一致性 reconciler | **销项（已建成）** | W4-4 批 1aa88be859 已注册 GATE-SCHEDULE-CONSISTENCY，见 §3 |

## 1. 缺口①：链活性卡（判据已备，本文只立项）

**缺口陈述**：新链入库无"≥1 条链内传导边才算活链"强制卡。实证=w4_1 三分法：A2 空壳链 2 条（登记后零节点）+C 类上游断供 148 条批量微链（导入器无活性约束）；活链判据 canonical SQL 已复现 583/873 覆盖口径。

**判据真源（已备，零重推导）**：`docs/_working/final3_campaign/w4_1_conduction_triage.md` §6（判据建议）+ §1（canonical SQL：`ig_chain.status='active'` ⇔ 存在 ≥1 条 ig_edge 两端节点同属本链的传导边）。

**净零并族方案**：

1. **存量巡检面（主）**：并 `scripts/industry_graph/graph_quality_check.py` 合格线 S 族（数据层唯一判定权引擎，S1~S26 在案，豁免/降级契约齐备）——新增参数面 **S27「链活性」**（SQL=canonical 判据取 NOT EXISTS 反面：`active 链 ∧ 零链内传导边`→违规清单；首期全集=w4_1 §3.2/§3.4/§5 共 162 条）。触发通道复用 align_all 第七节恒跑，零新调度。
2. **commit 卡点面（备选，Owner 裁是否需要）**：并 INDUSTRY-CHAIN-MAP gate（priority=141）族扩数据面第二臂（own-diff：仅当提交触及 ig_chain/ig_node/ig_edge 写入路径时校验其引入链满足活性判据）——**替代** w4_1 §6.4"新建 IG-CHAIN-LIVENESS 独立 gate"提议（省 gate_registry/能力卡/宪法引用三处净增）。全仓扫面需按 perf 方案 §2.6 分级登记（w4_1 §6.4 原文要求不豁免）。
3. **入库口准入面**：写入方（w4_1 §6.2 清单：concept_ingest/websearch_ingest/p3a_struct_extract/ths_import/r1_merge_plan）事务提交前调用与 S27 同源的共享谓词——零链内边→拒绝落 `status='active'`；`stub` 枚举值新增=**Owner 裁定项**（w4_1 §6.2）。

**落点文件路径**：

| 面 | 路径 |
|---|---|
| S27 参数面 | `scripts/industry_graph/graph_quality_check.py` |
| align_all 第七节收报告 | `scripts/governance/d5_architecture/generators/align_all.py` |
| 备选 commit 臂 | `src/zephyr/gov_enforcement/commit_gates/industry_chain_map_gate.py` |
| 入库口谓词接线 | `scripts/industry_graph/concept_ingest.py`、`scripts/industry_graph/ths_equity_import.py`、`scripts/industry_graph/p3a_struct_extract.py`、`scripts/industry_graph/execute_r1_chain_plans.py`（websearch 入库口施工时按 w4_1 §6.2 清单复核定位） |

**净零声明**：不新增 gate_id/规则条目；S27 并 S 族、commit 臂并 gate141、谓词函数级复用。**边界**：门禁只拦增量；存量 290 条按 w4_1 三分法消化，墓碑处置=Owner 门位禁删。

## 2. 缺口②：新全景图准入挂 ROOR

**缺口陈述**：新图准入现仅君子协定面——alignment_checklist §4.6 原则 6"新图必挂总线…并在本清单 §3 登记"（D38 同源）+ ROOR 头注"新增注册表 MUST 第一时间登记"。机器校验缺失实证：`docs/registry_of_registries.yaml`（883 行）无 trading_decision_map/strategy_production_map/governance_operations_map/frontend_map 任一 config 图条目——十图体系对 ROOR 登记要求事实性豁免，新图入册无 gate 拦。

**RULE-REGISTRY 扩面结论（任务问"查现有 RULE-REGISTRY gate 能否扩面"）**：RULE-REGISTRY 已外部化于 `docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml` `ai_registry_discovery` 节，性质=AI 冷启动行为铁律（读 registry_master_index.yaml / `discover_all_registries()`），**无 commit 级机器 gate 可直接扩面**；但其机器面脚本 `check_registry_consistency.py` 已读 ROOR——可作共享谓词宿主。可扩面的既有 gate=NEW-FILE-DEPGRAPH-ENFORCEMENT（`new_file_depgraph_gate.py`：own-diff staged 新增文件检测骨架、fail-open 错误契约、tests/ 豁免先例俱全）。

**净零方案**：

1. `new_file_depgraph_gate.py` 加**第二臂**（新参数面）：staged 新增文件匹配 `config/*_map.yaml`（全景图类）→ 查 ROOR 是否登记该路径，未登记→阻断；ROOR 同 commit 登记即过（豁免通道=登记动作本身）。
2. ROOR 登记谓词**共享化**落 `check_registry_consistency.py`（该脚本已实现 ROOR 读取），gate 只调用不复制——**禁重复建**。
3. 数据面：存量十图是否补登 ROOR 或声明豁免=**Owner 裁定项**（补登须走生成器/登记通道，禁手搓清单——运维红线 §9.5）。

**落点文件路径**：

| 面 | 路径 |
|---|---|
| 第二臂 | `src/zephyr/gov_enforcement/commit_gates/new_file_depgraph_gate.py` |
| 共享 ROOR 谓词 | `scripts/governance/d3_metadata/check_registry_consistency.py` |
| 臂测试扩展 | `tests/governance/commit_gates/test_new_file_depgraph_gate.py` |
| 数据面（裁定项） | `docs/registry_of_registries.yaml` |

**净零声明**：零新 gate_id、零 ROOR 解析重复实现；本参数面把 alignment_checklist §3/§4.6 的登记义务从君子协定升级为机器校验，属既有义务的执行机制化而非新规范。

## 3. 缺口③：排班一致性 reconciler——销项记录

- **状态：已建成已注册，W4-3 范围内剩余施工=0。**
- 实证：commit `1aa88be859`（W4-4 排班总排班视图：三表一入口，物理表不合并=Owner 裁定）。
  - `src/zephyr/governance/audit/schedule_consistency_reconciler.py`：`GATE_ID = "GATE-SCHEDULE-CONSISTENCY"`（L90，priority=826）；三表真源=`config/resource_profile_registry.yaml` + `src/zephyr/data/config/tasks.yaml` + `src/zephyr/data/config/schedule.yaml`；触发路径自携带（三表真源+本模块+统一 CLI，改动即对账——事件触发合规，无 cron/Timer/sleep-loop）。
  - `src/zephyr/governance/audit/reconciliation_registry.py` L649：已注册（处置面=只 warn/skip/fix-in-place）。
- 备注：该 gate 走 reconciliation_registry 通道（reconciler 派生 gate），不出现在 commit_gate 面的 gate_registry.yaml 机生清单属正常形态，非遗漏。
- 对 W4-3 总表唯一动作=本销项登记。

— 生成：2026-09-19 by st-final3-20260919（W4-3 立项登记批）
