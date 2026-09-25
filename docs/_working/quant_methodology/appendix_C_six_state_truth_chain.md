---
ttl: task_bound
title: 附录C 六段温度真源链——法定真源确认/实现层分叉定位/修复清单（只列不施工）
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 附录C：六段温度真源链与 601 vs 1,051 日分叉

> **结论先行**：HEAD 法定真源确认无误=`zephyr.signal_ashare.core.environment_switch` 的 `SIX_STATES`（六段封闭集）+ `framework_composer.py` 的 `REGIME_STATE_TO_ACTIVATION_PHASE`（唯一映射位点，与挂图侧 `auto_mount.R2SIX` 全等、有漂移守卫钉住）。**实现层分叉在两个文件**：法定侧 `scripts/backtest/auto_mount.py`（R2SIX）vs 产线占位 `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py`（REGIME_TO_SEGMENT）——产线表自注释承认是占位、无任何守卫，两套口径让同一道情绪门的宽度差 **75%（601 日 vs 1,051 日）**。

## 1. 法定真源链（HEAD 实测）

| 环节 | 位点 | 证据 |
|------|------|------|
| 六段封闭集（词表） | `src/zephyr/signal_ashare/core/environment_switch.py` 第 41 行 `SIX_STATES`（capitulation/accumulation/ignition/expansion/euphoria/distribution；"真源=地图 state_matrix 列轴"） | 模块头 INARIANTS：查表静态可审计、未知状态 fail-closed |
| r 态→六段唯一映射位点 | `src/zephyr/pf_core/strategy_engine/framework_composer.py` 第 153 行 `REGIME_STATE_TO_ACTIVATION_PHASE` = {r10→capitulation, r4→accumulation, r11→accumulation, r3→expansion, r12→ignition}（r1/r2 不路由） | 注释自述"唯一映射位点"；"同一张表在 auto_mount.py 的 R2SIX……两处必须同步，已登记主会话收编为共享真源（候选落点 zephyr.shared.contracts 或 config 规则 YAML）" |
| 挂图侧同表 | `scripts/backtest/auto_mount.py` 第 129 行 `R2SIX`（与 composer 逐键全等） | 第 154 行缓存键含 `sorted(R2SIX)`（表变即缓存失效） |
| 漂移守卫 | `tests/backtest/test_auto_mount_sle3.py` 的 `test_r2six_drift_guard_vs_framework_composer`（两表全等断言） | t0 终报 D-14 表："有漂移守卫钉住 ≡ 下行（实测两表全等）" |
| 状态词表加载通道 | framework_composer `_states_from_source`（惰性 import+缓存+fail-closed；activation 腿=SIX_STATES，regime 腿=`zephyr.regime.core.regime_detector.REGIME_STATES` 7 态） | CloneGuard 治本注释 |

## 2. 分叉的两个文件（追凶定位）

| 文件 | 常量 | 行号 | 内容 | 守卫 |
|------|------|------|------|------|
| `scripts/backtest/auto_mount.py` | `R2SIX` | 129 | {r10→capitulation, r4→accumulation, r11→accumulation, r3→expansion, r12→ignition}；r4→**accumulation**、r2→不路由 | ✅ 漂移守卫钉住 ≡ framework_composer |
| `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py` | `REGIME_TO_SEGMENT` | 110 | {r10→capitulation, **r4→distribution**, r1→accumulation, r11→accumulation, **r2→ignition**, r12→ignition, r3→expansion} | ❌ 无任何守卫 |

分叉点逐键对照：**r4**（法定=accumulation 修复 vs 产线=distribution 退潮——语义相反）；**r2**（法定=不路由 vs 产线=ignition 点火——凭空多出一态）；**r1**（法定表无此键=不路由 vs 产线=accumulation）。产线表自身注释承认："六段 v0 映射查表（草案值，裁定#305 第 1 点标注可调）……**情绪六段判定器接电后切换真源**"——即占位件待切换，切换从未发生。

## 3. 敏感度实测（仓内机算证据，非本班复算）

- 闭卷窗 [2019-01-04, 2025-09-09] 的 `regime_state_anchored` 共 1,622 日：r3 601 / r2 450 / r4 302 / r1 269。
- 情绪门允许集 {ignition, expansion, euphoria} 覆盖日数：**按 R2SIX=601 日**（只有 r3→expansion 命中）vs **按产线占位=1,051 日**（r2→ignition 追加 450 日）⇒ **差 75%**。
- 证据：`docs/_working/t0_matrix/LEDGER.md` D-14 节（第 232 行）+ `docs/_working/t0_matrix/FINAL_REPORT_t0_matrix_reexam.md` §五-4（第 211 行）。
- 附带量化：包体宏观腿标签域 {r1,r2,r3,r4} vs 六段真源宏观腿标签域 {r1,r2,r3,r4,r10,r11,r12}，两源逐日一致率 **383/1,816=21.09%**（reconcile_pack_v1_summary.csv cross_source_* 三行，机算）——同名 rN 标签在两张表语义并不同，换源不是改表名。
- 同报告 §五-6 相邻坑：`regime_state_anchored.dominant` 实为波动率风险四档（r3=最低波、r4=最高波，模块自述"无趋势项"）——卡面"趋势支"实际开的是低波日（`src/zephyr/regime/core/anchored_state_machine.py` 自述）。

## 4. 修复清单（只列不施工；按序）

1. **Owner 裁定选型**（前置，production 行为变更=宪法 §5 门位）：裁定"产线 REGIME_TO_SEGMENT 切换消费法定六段真源"（其 TODO 自指的"接电"动作）；裁定须登记 ruling_registry（RULE-RULING，同 commit 原子）。
2. **共享真源收编**：按 framework_composer.py 第 149-151 行预留的收编方案落位——候选=zephyr.shared.contracts 常量或 config 规则 YAML（src 不能 import scripts，故收编到双方都能消费的层）；收编后 auto_mount.R2SIX 与 framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE 改为同源消费，守卫测试改为"三方同源断言"。
3. **改产线表**：daily_decision_orchestrator.REGIME_TO_SEGMENT 切换为消费共享真源（或直接删表改引用）；同步给产线补漂移守卫（镜像 test_r2six_drift_guard 的全等断言，防回归）。
4. **重算历史结论**：凡按占位口径出过的情绪门结论（做T 考试门宽、按六段分档的历史报告）标注口径版本并按新真源重算；考试结论引用纪律（exam_policy：跨批引用连口径一起引）在此同样适用。
5. **锚定表语义裁定**（关联坑）：r 态双词表（7 态 HMM vs 锚定表 4 档波动语义）须一并裁定换源/换态集——任一都是判据语义变更，须作废重开相关考试卡（t0 终报 §五-6 原口径），禁执行面悄悄改。
6. **dev 缺符号随车修**：`src/zephyr/pf_alloc/allocation_inputs.py` 引 `SQL_LATEST_ANCHORED_STATE` 而 dev 提交的 `schemas/categories/backtest/backtest_regime_state_anchored.py` 无此符号（主区靠工作副本脏文件掩盖，t0 终报 §五-5/D-15）——该 lane 收尾提交时一并愈，修复批勿漏验 `git show dev` 视角可导入。

## 5. 一段话结论

**法定真源链完好（SIX_STATES→REGIME_STATE_TO_ACTIVATION_PHASE→守卫→R2SIX 同表）；分叉=auto_mount.py:129（法定）vs daily_decision_orchestrator.py:110（产线占位，自认待切换、无守卫）；产线口径让情绪门宽 75%（1,051 vs 601 日）；修复六步=Owner 裁定→收编共享真源→切产线+补守卫→重算历史→裁定锚定表语义→随车修 dev 缺符号。**
