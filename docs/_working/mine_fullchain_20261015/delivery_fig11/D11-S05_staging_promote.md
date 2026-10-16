---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S05
name_zh: 在途编辑与暂存晋升
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S05
---

# D11-S05 在途编辑与暂存晋升

## 1. 定义
会话车道第五环节（全图 4 个 structure/未接线节点之一，骨架 🔨）：staging 产物生命周期。决策问题=「staging 产物在 24h TTL 内被晋升了吗？没晋升谁来兜底清理？」实况=只有清理面（24h TTL reconciler+abort 即时清理），晋升面（staging→docs/_working）全仓无实现。

## 2. 六向台账

### 2.1 输入面
- staging 目录：`.runtime/sessions/<sid>/staging/`（宪法 §9.4：暂存唯一合法位置，24h TTL）
- 触发事件：commit/abort/轮询扫描（reconciler 事件触发）

### 2.2 输出面
- 清理动作+告警文案（reconciler 台账）；本车道 2026-10-15 复核：全仓 grep promot* ∩ staging/_working 排除异域（allow_promote=永久区新文件准入/ml_model_factory 反向语义/reconciler 告警文案）后仍=空集——晋升实现缺失与 2026-09-25 作业簿 02 判定一致

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S05`（build_status=partial、verified_scope=structure、wiring_status=unwired_no_caller、red_reason=unwired）——图如实登记缺口，未说谎
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/02_claim协议与暂存晋升.md`（状态列 🔨 未转）

### 2.4 代码模块
- `src/zephyr/governance/audit/reconciliation_registry.py:11518` `def make_session_staging_lifecycle_reconciler(`（图记 :10988，行锚漂移 +530）
- 同文件 `:11550` `_STAGING_TTL_SECONDS = 24 * 3600`（图记 :11020；对齐 make_stash_lifecycle_reconciler 口径）
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:1835` `_cleanup_session_staging`（abort 即时清理另腿，:7843 消费）
- 注册面：reconciliation_registry.py:188（priority=802 在案）

### 2.5 门禁约束
- 反向约束：FILE-PLACEMENT-TTL gate（C05 链，exit 3 PROMOTION_BLOCKED 处方=--allow-promote+creation_token 前置）管永久区准入——晋升缺位时它是唯一闸门
- 宪法 §9.4：成果须 promote 到 docs/_working/ 才算交付（政策要求与实现缺失的落差在本环节显影）

### 2.6 自动化触发
- 兜底清理自动化在岗：priority=802 事件触发 reconciler（禁 cron，合永久系统四要素）
- 晋升自动化缺失：无任何代码路径实现 staging→docs/_working 晋升

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | staging 目录契约在案 |
| 输出面 | fail | 晋升出口全仓空集（两次实测一致）；交付语义断头 |
| SSOT真源 | pass | 图/骨架如实记缺口（unwired_no_caller+🔨） |
| 代码模块 | pass | 清理面三锚点实存（行锚漂移 +530） |
| 门禁约束 | pass | FILE-PLACEMENT-TTL 反向闸在册 |
| 自动化触发 | warn | 兜底自动化在岗；晋升自动化零实现=环节半身 |

## 4. 缺口与建议
- 【核心缺口=收口对象】"promote 缺失"是本环节红因：建议要么补最小晋升通道（一条 scripts/promote_staging.py+审计行，等长替代无），要么把宪法 §9.4 "promote 才算交付"的语义正式改签到 merge 回主区（S07）——二选一需 Owner 门位（宪法属保留面）。
- 【行锚滞后】reconciliation_registry.py 巨体文件行锚漂移 +530，同前建议。
