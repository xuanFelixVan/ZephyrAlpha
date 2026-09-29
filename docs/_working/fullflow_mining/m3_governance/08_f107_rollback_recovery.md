---
ttl: task_bound
---
# F107 回滚恢复（rollback_recovery_infra）

本册覆盖 F107
> 机生对账尺认领锚（文件名 08_f107 挂锚；续挖 07_rollback_recovery_infra.md 勿重开——该册 :10 自注刻意回避三认领位、自判"六向缺两向（下游消费/门禁尺）"，本册补齐之）。

## 0. 环节档案

- **职责（大白话）**：出事时把系统退回已知好状态——双轨 checkpoint + 四级回滚 + G0 自愈基建。
- **码面**：`src/zephyr/infrastructure/rollback/` 55 件（rollback_executor/agent_cooldown/auditor/auto_rollback_trigger/budget_tracker/cascade_failure_simulator/checkpoint_gc/commit_quality_gate 等）+ `src/zephyr/infrastructure/runtime/concurrency_guard.py`（并发守卫真身）。
- **上游**：F84 备份链；**下游**：全链（总册 :182）。

## 1. 六向台账

| 向 | 状态 | 证据 |
|---|---|---|
| 上游 | ✅ | F84 备份链在产（storage-audit 台账：冷库夜镜像链） |
| 下游 | ⚠️半 | git_guard.py:276/post_checkout_guard.py 实调 check_rollback_conflict（运行面活）；ex_core 三处 rollback（order_execution_saga 等）为订单级异对象不并（93 册 §二同判） |
| 消费 | ✅ | 双 guard 脚本消费 concurrency_guard.check_rollback_conflict/scan_active_locks（imports 实证 :66-70） |
| 供给 | ✅ | runtime/concurrency_guard.py:150 check_rollback_conflict 真身在册 |
| 接线 | ✅（本册修正后） | 头注 [DEPENDENCIES] 锚漂移已修：git_guard.py:5 / post_checkout_guard.py:7 原指 `rollback.concurrency_guard`（不存在），实 import=`runtime.concurrency_guard`（真身）。属文档锚漂移非死码（imports 恒真，IMPORT-INTEGRITY 门未拦因实际导入面合法） |
| 测试 | ⚠️ | rollback 包测试面未逐件清点（07 册遗留项），本册未补新测（无码变更） |

## 2. 本册产出（补两缺向）

1. **下游消费向补齐**：真消费=双 guard 脚本的冲突检查面（上表）；07 册"谁真调 rollback 包"之问部分回答——调的是 runtime/concurrency_guard 单件，rollback 主包（executor 族）的包外调用方仍待逐件反查（限量取证未做，07 册 §三 口径维持）。
2. **门禁/质量尺向补齐**：死锚修复 2 处（上表接线向）；rollback 主包无 pre-commit 门覆盖（与 F100 同构问题：基建包不走 gate_registry 机读面）——是否立门=留裁（同 F100 §表1 二案形态，不并案）。

## 3. 三态裁定

**GAP**（收窄）：六向中上游/消费/供给/接线四向已证，下游半证（rollback 主包包外调用方未穷尽）、测试向未清点；07 册 + 本册合并后 F107 仍非 SEALED——回滚演练实弹（全链路一次真实回滚演习）为最后缺项，属施工面非挖矿面。

## 4. 自审闸

- [x] 码面实测（ls/imports/函数真身）
- [x] 死引用修复落地（2 锚，随袋提交）
- [ ] rollback 主包包外调用方穷尽（07 册遗留，限量取证）
- [ ] 测试面清点 + 回滚实弹演练（施工波）
