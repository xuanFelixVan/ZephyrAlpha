---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C11
name_zh: post-commit 对账与守卫
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C11
---

# D11-C11 post-commit 对账与守卫

## 1. 定义
提交车道第十一环节：提交后对账编排。决策问题=「这次 commit 之后要跑哪些 reconciler？异步编排与 shell 守卫怎么接力？」机制=网关 _register_default_reconcilers 事件触发编排（台数以实扫 register( 调用为准，实测 58 台）；run_post_commit_reconcile_async 异步化（launch 失败 fallback sync）；git_hooks 双守卫（post_commit_guard/reference_transaction_guard）红蓝触发；reconciler 必须事件触发禁定时器（永久系统四要素）。

## 2. 六向台账

### 2.1 输入面
- commit sha+session_id+commit_message（finally 段输入）
- reconciler 注册面：git_commit_gateway.py 内 register( 调用（2026-10-15 实查 grep -c = 58，与图 machine_facts.reconciler_register_calls=58 一致）

### 2.2 输出面
- 对账报告：`.runtime/reconcile_reports/`（实查 885 件）
- merge 后 reconcile_verify 默认 True 联动（S07）；reconciler 产 commit→C12 机器车道（已声明反馈环）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C11`（wired/production，machine_facts.reconciler_register_calls=58）
- 骨架：07_对账观测与紧急车道.md；主挂病历 RV1#全卷+RV2#全卷

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1839` `def _register_default_reconcilers(`（图记 :1547，行锚漂移 +292）
- 同文件 `:1326` `def run_post_commit_reconcile_async(`（launch_reconcile_async，失败 fallback sync+审计）
- 守卫：`scripts/governance/git_hooks/post_commit_guard.sh`（POST-COMMIT-GUARD：non-GW 检测+自动 revert+24h warn 累计阈值）+`reference_transaction_guard.sh`（实存在盘）；`.git/hooks/post-commit` 装配在盘

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=事件触发铁律（§9.3 禁 cron/Timer/sleep-loop）+reconciler 台数禁硬编码（裁定 D：以 registry 实际注册为准）

### 2.6 自动化触发
- commit finally→异步编排（进程分离 launch）；异步失败自动降级同步；红蓝触发双守卫

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | finally 输入+58 注册面实查一致 |
| 输出面 | pass | reconcile_reports 885 件在产 |
| SSOT真源 | pass | 图/骨架一致，机生计数同源 |
| 代码模块 | pass | 四锚点实存（行锚漂移 +292） |
| 门禁约束 | pass | 事件触发铁律+禁硬编码在案 |
| 自动化触发 | pass | 异步编排+fallback+双守卫全自动 |

## 4. 缺口与建议
- 【观测建议】58 台 reconciler 无逐台耗时/失败率聚合出口（reconcile_reports 是散件），建议 health 面加 reconciler 维度 TopN 慢台。
- 【行锚滞后】同 gateway 批量重扫建议。
