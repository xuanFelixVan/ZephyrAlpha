---
campaign: matrix-20261006
lane: R-road-repair
status: draft（供地图值班队/Owner 晋升执行）
created: 2026-10-06
ttl: task_bound
---

# fac9_05 — 工厂地图↔代码漂移修复计划（本册只开方，不动刀）

> **边界声明**：`config/strategy_production_map.yaml` 及地图族今夜由 st-fig13-bone 等队在册演化
> （`docs/03_modules/path_ownership_map.yaml` 实测持锁中）。按并行协调纪律（宪法§3.4 他队在途不代修），
> 本册只登记**证据齐备的修复处方**，执行留给地图值班队或 Owner 晋升批。每条处方含验证步骤。

## 一、fac9_01 遗留两处名实错位（证据已考古）

### R1. FAC-E1A 挂点 `MOD-BT-035` 名实错位
- **现状**：节点「车道A-社区货源」module_ref=MOD-BT-035，翻译册名=「C2 粗筛成绩灌表」——灌表是 A 车道**下游工序**，与节点名对不上（fac9_01 §二.2）。
- **处方**：二选一（需 Owner/地图队定谳其一）：
  - ①节点语义收窄为「社区货源粗筛灌表」→ 保留 MOD-BT-035，改节点名（一处 YAML 改动）；
  - ②节点保持「车道A-社区货源」→ module_ref 改指爬取器真实模块（考古 `scripts/` 社区货源爬取件后回填；若无独立模块，build_status 改 `pending` 并登记 candidate_module 立项）。
- **验证**：改后跑 FACTORY-MAP 结构 validator + 翻译册反查 module_ref 名与节点名一致性。

### R2. MOD-BT-201 双源冲突（path_ownership vs battle_map）
- **现状**：path_ownership_map 唯一路径=`tests/backtest/test_forward_post.py`（E7 前哨对账器）；battle_map_alignment_report 表行=Closed Book Gate（`src/zephyr/backtest/core/closed_book_gate.py`）。两真源打架（fac9_01 §二.3）。
- **处方**：考古定谳三步——
  ①读 `src/zephyr/backtest/core/closed_book_gate.py` 头部 [BLUEPRINT]/[MODULE] 行，确认其自报 module_id；
  ②读 `tests/backtest/test_forward_post.py` 头部同字段；
  ③谁自报 MOD-BT-201 谁入册；两者都自报=重号事故，走 module_registry 改号（注册表净删=Owner 门位）。
- **验证**：path_ownership_map 单一路径约束复核 + depgraph 重建（RENAME-DEPGRAPH-SYNC 同款纪律）。

## 二、骨架车道（本战役 S 车道）新发现四项矛盾（登记不判）

来源：`docs/_working/matrix_campaign/mining/00_stage_skeleton.md` §5 + `99_skeleton_selfcheck.md` §4（2026-10-06）。

| # | 矛盾 | 证据 | 建议处置 |
|---|------|------|---------|
| S1 | 任务书「16 骨架+325 机制」vs 字段实查 10 stage+7 lane=17 骨架+324 机制；E1 名「六车道」实挂 7 lane | 00_stage_skeleton §5.1 | 改任务书表述（E1F 后加入未改名——改名为文档级修复） |
| S2 | census 称 TDM L4「13 子环节」vs 实查 14（图 effective 2026-10-05 晚于 census） | 00 §5.2 | census 属快照老化，下轮普查自愈；无需动刀 |
| S3 | chief B1 的 ENV-14 记 6 vs 同口径 7；四个 FLOW 终端聚合点在 21 环节分表无显式落位（分组账 180 vs 182） | 00 §5.3 | chief 全集无损，分组口径差；建议 chief 侧补一行对账注记 |
| S4 | FAC-E0-M-003 GPU Core 标 pending vs #ARCH-366 gpu_core 冒烟实证已在案；另 E4-M-001 编号空洞、E4 层混装 24 枚数据供给件（层语义漂移）、E3-M-002「挂起」字样与 built 不一致 | 00 §5.4 | GPU Core build_status 翻 built（证据=registry #ARCH-366/W-173 基准报告）；其余登记待地图队 |

## 三、本战役已实证的地图增量事实（供下轮挂图）

1. **考试域四册存量画像**（bt_p0_roster_v1 实测）：因子册 175 中可计算列直连=0、code_symbol 锚=31；
   策略册 161 中 alpha_sources 非空=2、code_path=23；指标册 143 全列直连 ✓。
   → 工厂 E3（构造代码）层的「登记→量化」工序存在大面积半成品，E4（考试咽喉）的注册表驱动考试器本战役已补齐（scripts/backtest/fexam/）。
2. **批1/批2 全 rework 的机器原因清单**已落 `docs/_working/fexam/*_scores_v1.yaml`（每对象 reason 字段）——
   即 E3→E4 的缺料清单，可直接作 candidate_module_registry 的输入。
3. M1/M2 挖矿 72 个缺口节点规格卡已齐（mining/m1_alt_sources/ + mining/m2_exit_sector/），S 级 10 张可即接。

## 四、盲点自查（≥6 条，禁留白）

1. 本册未复核 battle_map_alignment_report 的生成器与时点——R2 定谳须以代码自报为准，报告仅旁证。
2. S4 的 GPU Core 翻 built 建议未跑 depgraph --force（无重命名不触发，但 build_status 变更是否需 depgraph 重建未验证）。
3. 未清点 fac9_02 之后新增的 map 变更（fig13 系今夜在改），本册处方可能与在飞改动撞车——执行前必须重读 HEAD。
4. 指标册 143 全直连的判定基于 outputs 列名命中候选表，未验证列语义一致性（如同名列跨表异义）。
5. 因子 code_symbol 31 锚点未逐一 import 验证可调用性（本战役按 M/L 级只登记）。
6. R1 处方②的爬取器考古未执行（超本车道边界，留施工队）。
