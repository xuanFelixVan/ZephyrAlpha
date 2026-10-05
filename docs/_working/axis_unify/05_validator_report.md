---
ttl: task_bound
completes_when: 总筹签字验收后本件随批归档
title: 轴归一手术·F4 一致性防线报告（05）：R12 腿红绿实证+三项复测对照
executor: st-axisunify-flash-20261005
---

# F4 报告：validator R12 腿 + 三项复测（AFTER 于 worktree=落地面预演实测）

## 1. validator R12 腿（check_decision_map 扩展，复用申报）

- **复用形**：run_checks 加 R12（对标 R9 depgraph 存在性/R11 CH 实存性既有腿模式）；读取两图 battle_map_refs → PG battle_map_steps 全量比对（BattleMapReader 只读）。**零新 gate、零新册、零新脚本**（净零申报：validator 复用=join_checker 设计稿键归一+存在性判定之最小实现）。
- **死引用=error**：红攻实证——伪造 BM-FAKE-9999 注入→`R12 [FACTORY:...] 死引用: BM-FAKE-9999` 捕获（fails≥1）；真面 199 条引用 fails=0。
- **交易段无回链=warn 君子协定**：聚合计数单行（当前 217 条，含 R4 自有属预期；触发率实证后再议 gate 化——verdict §六/裁定#487）。
- **留空白名单生效**：TDM-E-L9*/TDM-C-* 无 refs 不告警（白名单来源=裁定#487 §四，代码常量注记引用）。
- **fail-open 语义**：两图无字段=回滚态 skip；PG 异常整腿跳过单 warn（对标 R11）；禁吞 ProgrammingError 同训（AUDIT 清单#5）。

## 2. 三项复测对照（BEFORE=主区 22:00-22:08；AFTER=worktree f5fe2238add+本批改动 22:40-22:45）

| 复测件 | BEFORE | AFTER | 判定 |
|---|---|---|---|
| check_decision_map | exit=0 | exit=0（R12 腿在岗：fails=0+君子协定 warn 1 行） | ✅ 不劣化 |
| align_all | exit=1；decision_map=0 factory_map=0 gomap=452 panorama=1 | exit=1；decision_map=0 factory_map=3* gomap=452 panorama=0 | ✅ 不劣化（*见下对照实验） |
| align_battle_map | 违规 539（孤儿环节0/幽灵0/缺叙事0/悬空0/域漂移1/孤儿模块538/ghost_tdm=0） | 违规 539 逐项相等 | ✅ 不劣化 |

### 2.1 factory_map=3 对照实验（隔离变量）

对同一 validator 对跑 HEAD 版（无本批 refs）vs worktree 版（有 refs）：**两侧同为 3 且错误同文**（`.runtime/logs/`、`data/strategy_intake/normalized/` 路径不存在）——系 worktree 新 checkout 缺运行时/数据目录的环境固有差异，与本批 refs 零相关（HEAD 对照=同 3 实证）。主区盘面基线该两目录实存故为 0。

## 3. alignment_checklist §3 注记（挂接申报）

battle_map 行轴标注维持裁定#483 后口径（横·覆盖切片）；本手术新增互挂字段后，对齐轴不变（step_id），叙事权面=TDM/工厂 refs 字段+PG tdm_node_id 双向互挂，防漂由 R12 腿+ghost_tdm 腿双向守。

## 4. 缺口与移交

- 217 条君子协定 warn 中含 R4 自有存量，属设计内；若 Owner 欲收敛，后续可按 02 提案 R4 名单做 acknowledged 登记降采样（本批不做，留实证期）。
- gomap error=452 系他会话在途 WIP 存量（基线已在案），本手术零触碰。
